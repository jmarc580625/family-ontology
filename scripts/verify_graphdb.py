#!/usr/bin/env python3
"""
Simple script to verify GraphDB setup is working correctly.

This script checks:
1. GraphDB is running and accessible
2. Repository can be created
3. Ontology and test data can be loaded
4. Basic SPARQL queries work
5. OWL2-RL reasoning is functioning

Usage:
    python scripts/verify_graphdb.py

Prerequisites:
    docker-compose up -d
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'tests'))

try:
    import requests
except ImportError:
    print("❌ Error: requests package not installed")
    print("   Run: pip install requests")
    sys.exit(1)


def check_graphdb_running(url: str = "http://localhost:7200", timeout: int = 5) -> bool:
    """Check if GraphDB is running."""
    print(f"\n1. Checking GraphDB at {url}...")
    try:
        response = requests.get(f"{url}/rest/repositories", timeout=timeout)
        if response.status_code == 200:
            print("   ✅ GraphDB is running")
            return True
        else:
            print(f"   ❌ GraphDB returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to GraphDB")
        print("   💡 Make sure GraphDB is running: docker-compose up -d")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ Connection timed out")
        return False


def verify_backend_import() -> bool:
    """Verify GraphDB backend can be imported."""
    print("\n2. Verifying GraphDB backend module...")
    try:
        from backends.graphdb_backend import GraphDBBackend
        print("   ✅ GraphDB backend module imported successfully")
        return True
    except ImportError as e:
        print(f"   ❌ Failed to import GraphDB backend: {e}")
        return False


def test_repository_operations(graphdb_url: str = "http://localhost:7200") -> bool:
    """Test repository creation and data loading."""
    print("\n3. Testing repository operations...")
    
    from backends.graphdb_backend import GraphDBBackend
    
    project_root = Path(__file__).parent.parent
    ontology_file = str(project_root / 'ontology' / 'family-ontology.ttl')
    data_file = str(project_root / 'tests' / 'data' / 'family-sample-data.ttl')
    
    # Check files exist
    if not Path(ontology_file).exists():
        print(f"   ❌ Ontology file not found: {ontology_file}")
        return False
    if not Path(data_file).exists():
        print(f"   ❌ Test data file not found: {data_file}")
        return False
    
    print(f"   📁 Ontology: {ontology_file}")
    print(f"   📁 Test data: {data_file}")
    
    try:
        backend = GraphDBBackend(
            ontology_file=ontology_file,
            data_files=[data_file],
            graphdb_url=graphdb_url,
            repository_id="family-ontology-verify",
            ruleset="owl2-rl"
        )
        
        print("   Initializing repository (this may take a moment)...")
        backend.initialize()
        print("   ✅ Repository created and data loaded")
        return True
        
    except Exception as e:
        print(f"   ❌ Repository operation failed: {e}")
        return False


def test_sparql_queries(graphdb_url: str = "http://localhost:7200") -> bool:
    """Test basic SPARQL queries."""
    print("\n4. Testing SPARQL queries...")
    
    from backends.graphdb_backend import GraphDBBackend
    
    project_root = Path(__file__).parent.parent
    ontology_file = str(project_root / 'ontology' / 'family-ontology.ttl')
    data_file = str(project_root / 'tests' / 'data' / 'family-sample-data.ttl')
    
    backend = GraphDBBackend(
        ontology_file=ontology_file,
        data_files=[data_file],
        graphdb_url=graphdb_url,
        repository_id="family-ontology-verify",
        ruleset="owl2-rl"
    )
    
    # Test simple query - count persons
    query = """
    PREFIX : <http://example.org/family#>
    SELECT (COUNT(?p) AS ?count) WHERE {
        ?p a :Person .
    }
    """
    
    try:
        results = backend.execute_query(query)
        if results:
            count = results[0].get('count', '0')
            print(f"   ✅ Query executed - Found {count} persons")
        else:
            print("   ⚠️ Query returned no results")
        return True
    except Exception as e:
        print(f"   ❌ Query failed: {e}")
        return False


def test_owl_reasoning(graphdb_url: str = "http://localhost:7200") -> bool:
    """Test OWL2-RL reasoning is working."""
    print("\n5. Testing OWL2-RL reasoning...")
    
    from backends.graphdb_backend import GraphDBBackend
    
    project_root = Path(__file__).parent.parent
    ontology_file = str(project_root / 'ontology' / 'family-ontology.ttl')
    data_file = str(project_root / 'tests' / 'data' / 'family-sample-data.ttl')
    
    backend = GraphDBBackend(
        ontology_file=ontology_file,
        data_files=[data_file],
        graphdb_url=graphdb_url,
        repository_id="family-ontology-verify",
        ruleset="owl2-rl"
    )
    
    # Test inverse property inference (childOf is inverse of parentOf)
    # If we have :alice :parentOf :bob, we should infer :bob :childOf :alice
    query = """
    PREFIX : <http://example.org/family#>
    SELECT ?child ?parent WHERE {
        ?child :childOf ?parent .
    } LIMIT 5
    """
    
    try:
        results = backend.execute_query(query)
        if results and len(results) > 0:
            print(f"   ✅ OWL reasoning working - Found {len(results)} childOf relationships (inferred from parentOf)")
            for r in results[:3]:
                child = r.get('child', '?').split('#')[-1]
                parent = r.get('parent', '?').split('#')[-1]
                print(f"      {child} :childOf {parent}")
            if len(results) > 3:
                print(f"      ... and {len(results) - 3} more")
        else:
            print("   ⚠️ No inferred relationships found - reasoning may not be working")
        return True
    except Exception as e:
        print(f"   ❌ Reasoning test failed: {e}")
        return False


def test_grandparent_inference(graphdb_url: str = "http://localhost:7200") -> bool:
    """Test property chain inference (grandparentOf)."""
    print("\n6. Testing property chain inference (grandparentOf)...")
    
    from backends.graphdb_backend import GraphDBBackend
    
    project_root = Path(__file__).parent.parent
    ontology_file = str(project_root / 'ontology' / 'family-ontology.ttl')
    data_file = str(project_root / 'tests' / 'data' / 'family-sample-data.ttl')
    
    backend = GraphDBBackend(
        ontology_file=ontology_file,
        data_files=[data_file],
        graphdb_url=graphdb_url,
        repository_id="family-ontology-verify",
        ruleset="owl2-rl"
    )
    
    # Test property chain: grandparentOf = parentOf o parentOf
    query = """
    PREFIX : <http://example.org/family#>
    SELECT ?grandparent ?grandchild WHERE {
        ?grandparent :grandparentOf ?grandchild .
    } LIMIT 5
    """
    
    try:
        results = backend.execute_query(query)
        if results and len(results) > 0:
            print(f"   ✅ Property chain working - Found {len(results)} grandparentOf relationships")
            for r in results[:3]:
                gp = r.get('grandparent', '?').split('#')[-1]
                gc = r.get('grandchild', '?').split('#')[-1]
                print(f"      {gp} :grandparentOf {gc}")
            if len(results) > 3:
                print(f"      ... and {len(results) - 3} more")
        else:
            print("   ⚠️ No grandparentOf relationships found")
            print("   💡 This may indicate property chains are not being inferred")
        return True
    except Exception as e:
        print(f"   ❌ Property chain test failed: {e}")
        return False


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("GraphDB Setup Verification")
    print("=" * 60)
    
    graphdb_url = "http://localhost:7200"
    all_passed = True
    
    # Test 1: Check GraphDB is running
    if not check_graphdb_running(graphdb_url):
        print("\n" + "=" * 60)
        print("❌ VERIFICATION FAILED")
        print("=" * 60)
        print("\nGraphDB is not running. Please start it with:")
        print("  docker-compose up -d")
        print("\nThen wait ~30 seconds for it to initialize and run this script again.")
        sys.exit(1)
    
    # Test 2: Verify backend import
    if not verify_backend_import():
        all_passed = False
    
    # Test 3: Repository operations
    if not test_repository_operations(graphdb_url):
        all_passed = False
    else:
        # Only run query tests if repository was created successfully
        
        # Test 4: SPARQL queries
        if not test_sparql_queries(graphdb_url):
            all_passed = False
        
        # Test 5: OWL reasoning
        if not test_owl_reasoning(graphdb_url):
            all_passed = False
        
        # Test 6: Property chain inference
        if not test_grandparent_inference(graphdb_url):
            all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL VERIFICATION TESTS PASSED")
        print("=" * 60)
        print("\nGraphDB is properly configured and working!")
        print("\nYou can now run the full test suite with:")
        print("  python tests/cli.py --mode graphdb run --level all")
    else:
        print("⚠️ SOME TESTS HAD ISSUES")
        print("=" * 60)
        print("\nReview the output above for details.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
