"""
GraphDB backend for testing with full OWL2-RL reasoning.
"""

import requests
import json
import time
from typing import List, Dict, Any
from pathlib import Path


class GraphDBBackend:
    """GraphDB backend with REST API integration."""
    
    def __init__(self, ontology_file: str, data_files: List[str] = None, 
                 graphdb_url: str = "http://localhost:7200",
                 repository_id: str = "family-ontology-test",
                 ruleset: str = "owl2-rl"):
        """
        Initialize GraphDB backend.
        
        Args:
            ontology_file: Path to ontology TTL file
            data_files: List of paths to test data TTL files
            graphdb_url: GraphDB server URL
            repository_id: Repository name
            ruleset: Inference ruleset (owl2-rl, rdfs, etc.)
        """
        self.ontology_file = ontology_file
        self.data_files = data_files or []
        self.graphdb_url = graphdb_url.rstrip('/')
        self.repository_id = repository_id
        self.ruleset = ruleset
        self.repo_url = f"{self.graphdb_url}/repositories/{self.repository_id}"
        
    def _wait_for_graphdb(self, timeout: int = 60):
        """Wait for GraphDB to be ready."""
        print(f"Waiting for GraphDB at {self.graphdb_url}...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.graphdb_url}/rest/repositories", timeout=5)
                if response.status_code == 200:
                    print("✓ GraphDB is ready")
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(2)
        
        raise TimeoutError(f"GraphDB not ready after {timeout} seconds")
    
    def _repository_exists(self) -> bool:
        """Check if repository exists."""
        try:
            response = requests.get(f"{self.graphdb_url}/rest/repositories/{self.repository_id}")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def _delete_repository(self):
        """Delete existing repository."""
        if self._repository_exists():
            print(f"Deleting repository: {self.repository_id}")
            response = requests.delete(f"{self.graphdb_url}/rest/repositories/{self.repository_id}")
            if response.status_code in [200, 204]:
                print("✓ Repository deleted")
                time.sleep(2)  # Wait for deletion to complete
            else:
                raise RuntimeError(f"Failed to delete repository: {response.status_code} {response.text}")
    
    def _create_repository(self):
        """Create new repository with specified ruleset."""
        print(f"Creating repository: {self.repository_id} with ruleset: {self.ruleset}")
        
        # Repository configuration in JSON format for GraphDB 10.x REST API
        config = {
            "id": self.repository_id,
            "title": "Family Ontology Test Repository",
            "type": "graphdb",
            "params": {
                "ruleset": {
                    "label": "Ruleset",
                    "name": "ruleset",
                    "value": self.ruleset
                },
                "baseURL": {
                    "label": "Base URL",
                    "name": "baseURL",
                    "value": "http://example.org/family#"
                },
                "defaultNS": {
                    "label": "Default namespaces for imports(';' delimited)",
                    "name": "defaultNS",
                    "value": ""
                },
                "imports": {
                    "label": "Imported RDF files(';' delimited)",
                    "name": "imports",
                    "value": ""
                }
            }
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            f"{self.graphdb_url}/rest/repositories",
            json=config,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            print("✓ Repository created")
            time.sleep(2)  # Wait for creation to complete
        else:
            raise RuntimeError(f"Failed to create repository: {response.status_code} {response.text}")
    
    def _load_file(self, file_path: str, context: str = None):
        """Load RDF file into repository."""
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        print(f"Loading: {file_path}")
        
        with open(file_path, 'rb') as f:
            data = f.read()
        
        headers = {'Content-Type': 'text/turtle'}
        params = {}
        if context:
            params['context'] = context
        
        response = requests.post(
            f"{self.repo_url}/statements",
            data=data,
            headers=headers,
            params=params
        )
        
        if response.status_code in [200, 204]:
            print(f"✓ Loaded: {Path(file_path).name}")
        else:
            raise RuntimeError(f"Failed to load file: {response.status_code} {response.text}")
    
    def initialize(self):
        """Initialize GraphDB repository and load data."""
        # Wait for GraphDB to be ready
        self._wait_for_graphdb()
        
        # Reset repository (delete and recreate)
        self._delete_repository()
        self._create_repository()
        
        # Load ontology
        self._load_file(self.ontology_file)
        
        # Load test data
        for data_file in self.data_files:
            self._load_file(data_file)
        
        # Wait for reasoning to complete
        time.sleep(2)
        
        stats = self.get_stats()
        print(f"✓ Repository initialized with {stats.get('total_statements', '?')} statements")
    
    def execute_query(self, sparql_query: str) -> List[Dict[str, Any]]:
        """
        Execute SPARQL query and return results.
        
        Args:
            sparql_query: SPARQL SELECT or ASK query
            
        Returns:
            List of result bindings as dictionaries
        """
        headers = {
            'Accept': 'application/sparql-results+json',
            'Content-Type': 'application/sparql-query'
        }
        
        response = requests.post(
            f"{self.repo_url}",
            data=sparql_query.encode('utf-8'),
            headers=headers
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Query failed: {response.status_code} {response.text}")
        
        result = response.json()
        
        # Handle ASK queries
        if 'boolean' in result:
            return [{'result': result['boolean']}]
        
        # Handle SELECT queries
        if 'results' in result and 'bindings' in result['results']:
            return [
                {var: binding[var]['value'] for var in binding}
                for binding in result['results']['bindings']
            ]
        
        return []
    
    def execute_update(self, sparql_update: str):
        """
        Execute SPARQL UPDATE query (for materialization).
        
        Args:
            sparql_update: SPARQL INSERT/DELETE query
        """
        headers = {'Content-Type': 'application/sparql-update'}
        
        response = requests.post(
            f"{self.repo_url}/statements",
            data=sparql_update.encode('utf-8'),
            headers=headers
        )
        
        if response.status_code not in [200, 204]:
            raise RuntimeError(f"Update failed: {response.status_code} {response.text}")
        
        print("✓ Update executed successfully")
    
    def reset(self):
        """Reset repository (delete and reload data)."""
        self.initialize()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get repository statistics."""
        try:
            response = requests.get(f"{self.repo_url}/size")
            if response.status_code == 200:
                return {
                    "backend": "graphdb",
                    "repository": self.repository_id,
                    "total_statements": int(response.text),
                    "url": self.graphdb_url
                }
        except:
            pass
        
        return {"backend": "graphdb", "status": "unknown"}
    
    def cleanup(self):
        """Cleanup resources (optionally delete repository)."""
        # Keep repository for inspection unless explicitly deleted
        pass