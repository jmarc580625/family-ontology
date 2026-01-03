#!/usr/bin/env python3
"""
Legacy test runner for backward compatibility.
Redirects to new CLI with RDFLib backend.
"""

import sys
import os

# Add tests directory to path
sys.path.insert(0, os.path.dirname(__file__))

from backends.rdflib_backend import RDFLibBackend
from runners.base_runner import BaseTestRunner


def main():
    """Main entry point for legacy test runner."""
    if len(sys.argv) != 3:
        print("Usage: python test-runner.py <ontology_file> <test_file>")
        print("\nNote: This is the legacy interface. For more options, use:")
        print("  python cli.py run --help")
        sys.exit(1)
    
    ontology_file = sys.argv[1]
    test_file = sys.argv[2]
    
    # Use RDFLib backend (fast, in-memory)
    print("Using RDFLib backend (legacy mode)")
    print("For GraphDB support, use: python cli.py run --mode graphdb\n")
    
    # Determine data files
    test_dir = os.path.dirname(__file__)
    data_files = []
    for data_filename in ['family-sample-data.ttl', 'family-anchors-data.ttl']:
        data_file = os.path.join(test_dir, 'data', data_filename)
        if os.path.exists(data_file):
            data_files.append(data_file)
    
    # Create backend and runner
    backend = RDFLibBackend(ontology_file, data_files)
    backend.initialize()
    
    runner = BaseTestRunner(backend, test_file)
    results = runner.run_tests()
    
    # Save results
    runner.save_results('test_results.json')
    
    # Cleanup
    backend.cleanup()
    
    # Exit with appropriate code
    sys.exit(0 if results['failed'] == 0 else 1)


if __name__ == "__main__":
    main()