"""
RDFLib in-memory backend for testing.
"""

from rdflib import Graph, Namespace
from typing import List, Dict, Any
import os
import sys

try:
    import owlrl
    OWLRL_AVAILABLE = True
except ImportError:
    OWLRL_AVAILABLE = False


class RDFLibBackend:
    """In-memory RDFLib backend for fast local testing."""
    
    def __init__(self, ontology_file: str, data_files: List[str] = None):
        """
        Initialize RDFLib backend.
        
        Args:
            ontology_file: Path to ontology TTL file
            data_files: List of paths to test data TTL files
        """
        self.ontology_file = ontology_file
        self.data_files = data_files or []
        self.graph = None
        
    def initialize(self):
        """Load ontology and data into memory."""
        self.graph = Graph()
        
        # Load ontology
        if not os.path.exists(self.ontology_file):
            print(f"\n❌ Error: Ontology file not found: {self.ontology_file}", file=sys.stderr)
            sys.exit(1)
        
        print(f"Loading ontology: {self.ontology_file}")
        self._parse_file_with_error_handling(self.ontology_file)
        
        # Load test data
        for data_file in self.data_files:
            if not os.path.exists(data_file):
                print(f"\n❌ Error: Test data file not found: {data_file}", file=sys.stderr)
                sys.exit(1)
            print(f"Loading test data: {data_file}")
            self._parse_file_with_error_handling(data_file)
        
        # Bind namespaces for pretty printing
        for prefix, ns in self.graph.namespaces():
            if prefix:
                self.graph.bind(prefix, ns)
        
        # Apply OWL-RL reasoning if available
        if OWLRL_AVAILABLE:
            triples_before = len(self.graph)
            owlrl.DeductiveClosure(owlrl.RDFS_OWLRL_Semantics).expand(self.graph)
            triples_after = len(self.graph)
            inferred = triples_after - triples_before
            print(f"✓ Loaded {triples_before} triples, inferred {inferred} additional triples")
        else:
            print(f"✓ Loaded {len(self.graph)} triples (OWL-RL reasoning not available)")
            print("  Tip: Install owlrl for better inference: pip install owlrl")
    
    def _parse_file_with_error_handling(self, file_path: str):
        """Parse RDF file with enhanced error reporting."""
        try:
            self.graph.parse(file_path, format="turtle")
        except Exception as e:
            # Enhanced error message
            error_msg = f"\n{'='*80}\n"
            error_msg += f"❌ TURTLE SYNTAX ERROR\n"
            error_msg += f"{'='*80}\n"
            error_msg += f"File: {file_path}\n\n"
            
            # Try to extract line number from error
            error_str = str(e)
            if hasattr(e, 'lines'):
                error_msg += f"Line: {e.lines}\n"
            
            # Common Turtle syntax issues
            error_msg += "\nCommon issues to check:\n"
            error_msg += "  • Missing period (.) at end of statement\n"
            error_msg += "  • Missing semicolon (;) between properties\n"
            error_msg += "  • Unclosed brackets [ ] or ( )\n"
            error_msg += "  • Invalid prefix or namespace\n"
            error_msg += "  • Extra or missing whitespace\n"
            error_msg += "  • Special characters in URIs not escaped\n"
            
            # Try to show problematic lines
            if hasattr(e, 'lines') and e.lines:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        line_num = e.lines
                        
                        error_msg += f"\nContext around line {line_num}:\n"
                        error_msg += "-" * 80 + "\n"
                        
                        # Show 3 lines before and after
                        start = max(0, line_num - 4)
                        end = min(len(lines), line_num + 3)
                        
                        for i in range(start, end):
                            line_marker = ">>> " if i == line_num - 1 else "    "
                            error_msg += f"{line_marker}{i+1:4d} | {lines[i]}"
                        
                        error_msg += "-" * 80 + "\n"
                except:
                    pass
            
            error_msg += f"\nOriginal error: {error_str}\n"
            error_msg += "=" * 80 + "\n"
            
            raise RuntimeError(error_msg) from e
        
    def execute_query(self, sparql_query: str) -> List[Dict[str, Any]]:
        """
        Execute SPARQL query and return results.
        
        Args:
            sparql_query: SPARQL SELECT or ASK query
            
        Returns:
            List of result bindings as dictionaries
        """
        if not self.graph:
            raise RuntimeError("Backend not initialized. Call initialize() first.")
        
        results = self.graph.query(sparql_query)
        
        # Handle ASK queries
        if isinstance(results, bool):
            return [{'result': results}]
        
        # Handle SELECT queries
        result_list = []
        for row in results:
            row_dict = {}
            # Get the variable names from the results object
            for var in results.vars:
                var_name = str(var)
                value = row[var]
                if value is not None:
                    row_dict[var_name] = str(value)
            result_list.append(row_dict)
        
        return result_list
    
    def execute_update(self, sparql_update: str) -> int:
        """
        Execute SPARQL UPDATE query (for materialization).
        
        Args:
            sparql_update: SPARQL INSERT/DELETE query
            
        Returns:
            Number of triples added
        """
        if not self.graph:
            raise RuntimeError("Backend not initialized. Call initialize() first.")
        
        # Count triples before update
        count_before = len(self.graph)
        
        # Execute update
        self.graph.update(sparql_update)
        
        # Count triples after update
        count_after = len(self.graph)
        
        return count_after - count_before
    
    def reset(self):
        """Reset the graph (reload from scratch)."""
        self.graph = None
        self.initialize()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the loaded data."""
        if not self.graph:
            return {"status": "not initialized"}
        
        return {
            "backend": "rdflib",
            "triples": len(self.graph),
            "namespaces": list(dict(self.graph.namespaces()).keys())
        }
    
    def cleanup(self):
        """Cleanup resources."""
        self.graph = None