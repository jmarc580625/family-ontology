#!/usr/bin/env python3
"""
Command-line interface for family ontology testing.
"""

import argparse
import sys
import json
from pathlib import Path

# Import backends
from backends.rdflib_backend import RDFLibBackend
from backends.graphdb_backend import GraphDBBackend

# Import runners
from runners.base_runner import BaseTestRunner
from runners.test_executor import TestExecutor


def get_default_paths():
    """Get default file paths relative to project root."""
    tests_dir = Path(__file__).parent
    project_root = tests_dir.parent
    
    return {
        'ontology': str(project_root / 'ontology' / 'family-ontology.ttl'),
        'test_data': str(tests_dir / 'data' / 'family-sample-data.ttl'),
        'test_file': str(tests_dir / 'family-relationships.json'),
        'config_file': str(tests_dir / 'test-config.json')
    }


def create_backend(mode, ontology_file, data_files, graphdb_url, repository_id):
    """Create backend instance based on mode."""
    if mode == 'rdflib':
        return RDFLibBackend(ontology_file, data_files)
    elif mode == 'graphdb':
        return GraphDBBackend(ontology_file, data_files, graphdb_url, repository_id)
    else:
        raise ValueError(f"Invalid mode: {mode}. Must be 'rdflib' or 'graphdb'")


def cmd_run_tests(args):
    """Run tests command."""
    paths = get_default_paths()
    
    # Load config to check for level-specific data files
    config_file = args.config or paths['config_file']
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Determine data files
    # Priority: 1) CLI args, 2) level-specific config
    # No implicit defaults - configuration must be explicit
    data_files = None
    
    if args.data:
        # Explicit CLI argument takes precedence
        data_files = args.data
    elif args.level == 'all':
        # Collect all unique data files from all levels
        test_levels = config.get('test_levels', {})
        all_data_files = []
        seen = set()
        for level in range(10):
            level_config = test_levels.get(str(level), {})
            for data_file in level_config.get('data_files', []):
                if data_file not in seen:
                    all_data_files.append(data_file)
                    seen.add(data_file)
        data_files = all_data_files if all_data_files else None
    elif args.level:
        # Check if this level has specific data files
        test_levels = config.get('test_levels', {})
        level_config = test_levels.get(str(args.level), {})
        if 'data_files' in level_config:
            data_files = level_config['data_files']
    
    # Validate that data files are specified
    if data_files is None or len(data_files) == 0:
        print("\n❌ Error: No data files specified", file=sys.stderr)
        print("\nPlease specify data files either:", file=sys.stderr)
        print("  1. Via CLI: --data <file1> <file2> ...", file=sys.stderr)
        print("  2. Via config: Add 'data_files' to level configuration in test-config.json", file=sys.stderr)
        sys.exit(1)
    
    # Resolve data file paths relative to project root
    project_root = Path(__file__).parent.parent
    data_files = [str(project_root / f) for f in data_files]
    
    # Create backend
    print(f"Using backend: {args.mode}")
    backend = create_backend(
        args.mode,
        args.ontology or paths['ontology'],
        data_files,
        args.graphdb_url,
        args.repository
    )
    
    # Initialize backend
    print("\nInitializing backend...")
    backend.initialize()
    
    # Create executor
    executor = TestExecutor(
        backend,
        args.test_file or paths['test_file'],
        args.config or paths['config_file'],
        verbose=args.verbose
    )
    
    # Run based on arguments
    try:
        if args.level is not None:
            if args.level == 'all':
                # Run all levels together - single initialization with all materialization
                print("\n" + "="*80)
                print("RUNNING ALL LEVELS TOGETHER (0-9)")
                print("Testing everything working together with all materialization applied")
                print("="*80)
                
                # Check if explicit "all" config exists, otherwise auto-collect
                mat_config = executor.config.get('materialization_requirements', {})
                if 'all' in mat_config:
                    # Use explicit configuration
                    all_materialize = mat_config['all']
                    print("\nUsing explicit 'all' configuration from test-config.json")
                else:
                    # Fallback: collect from all levels with deduplication
                    all_materialize = []
                    seen = set()
                    for level in range(10):
                        for script in mat_config.get(str(level), []):
                            if script not in seen:
                                all_materialize.append(script)
                                seen.add(script)
                    print("\nAuto-collecting from all levels (0-9) with deduplication")
                
                if all_materialize:
                    print(f"Loaded {len(all_materialize)} materialization requirement(s)\n")
                    print(f"Applying {len(all_materialize)} materialization script(s)...")
                    # Resolve relative paths from project root
                    resolved_scripts = [executor._resolve_script_path(p) for p in all_materialize]
                    for script_path in resolved_scripts:
                        executor.apply_materialization(script_path)
                else:
                    print("\nNo materialization requirements found\n")
                
                # Run all tests from all levels
                all_test_ids = []
                test_levels = executor.config.get('test_levels', {})
                for level in range(10):
                    test_ids = test_levels.get(str(level), {}).get('tests', [])
                    all_test_ids.extend(test_ids)
                
                print(f"\nRunning {len(all_test_ids)} tests from all levels...\n")
                results = executor.runner.run_tests(all_test_ids)
                
                # Show summary by level
                print("\n" + "="*80)
                print("RESULTS BY LEVEL")
                print("="*80)
                
                for level in range(10):
                    level_name = test_levels.get(str(level), {}).get('name', f'Level {level}')
                    test_ids = test_levels.get(str(level), {}).get('tests', [])
                    
                    if not test_ids:
                        continue
                    
                    # Count results for this level
                    level_passed = 0
                    level_failed = 0
                    for test_id in test_ids:
                        if test_id in results['details']:
                            if results['details'][test_id]['status'] == 'PASS':
                                level_passed += 1
                            else:
                                level_failed += 1
                    
                    level_total = level_passed + level_failed
                    if level_total == 0:
                        continue
                    
                    status = "✅" if level_failed == 0 else "❌"
                    print(f"{status} Level {level}: {level_name} - {level_passed}/{level_total} passed")
                
                # Final summary
                print("\n" + "="*80)
                if results['failed'] == 0:
                    print("✅ ALL TESTS PASSED")
                else:
                    print(f"❌ {results['failed']}/{results['total']} TESTS FAILED")
                print("="*80)
            else:
                # Run specific level (handles its own materialization from config if not specified)
                try:
                    level = int(args.level)
                    if level < 0 or level > 9:
                        raise ValueError(f"Level must be between 0-9, got {level}")
                    materialize = args.materialize  # Pass None if not specified, so config is used
                    results = executor.run_level(level, materialize)
                except ValueError as e:
                    print(f"\n❌ Invalid level: {args.level}. Use 0-9 or 'all'", file=sys.stderr)
                    backend.cleanup()
                    sys.exit(1)
        else:
            # Apply materialization scripts if provided (for individual tests or all tests)
            if args.materialize:
                print(f"\nApplying {len(args.materialize)} materialization script(s)...")
                for script_path in args.materialize:
                    executor.apply_materialization(script_path)
            
            if args.test:
                # Run specific test
                results = executor.runner.run_tests([args.test])
            else:
                # Run all tests
                results = executor.runner.run_tests()
    except ValueError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        backend.cleanup()
        sys.exit(1)
    
    # Save results
    if args.output:
        executor.runner.save_results(args.output)
    
    # Cleanup
    backend.cleanup()
    
    # Exit with appropriate code
    sys.exit(0 if results['failed'] == 0 else 1)


def cmd_verify_materialization(args):
    """Verify materialization script command."""
    paths = get_default_paths()
    
    # Create backend
    print(f"Using backend: {args.mode}")
    backend = create_backend(
        args.mode,
        args.ontology or paths['ontology'],
        [paths['test_data']],
        args.graphdb_url,
        args.repository
    )
    
    # Initialize backend
    backend.initialize()
    
    # Create executor
    executor = TestExecutor(
        backend,
        paths['test_file'],
        paths['config_file']
    )
    
    # Verify materialization
    success = executor.verify_materialization(args.script)
    
    # Cleanup
    backend.cleanup()
    
    sys.exit(0 if success else 1)


def cmd_reset_repository(args):
    """Reset GraphDB repository command."""
    if args.mode != 'graphdb':
        print("Reset is only applicable to GraphDB backend")
        sys.exit(1)
    
    paths = get_default_paths()
    
    backend = GraphDBBackend(
        paths['ontology'],
        [paths['test_data']],
        args.graphdb_url,
        args.repository
    )
    
    print("Resetting GraphDB repository...")
    backend.initialize()
    print("✓ Repository reset complete")
    
    sys.exit(0)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Family Ontology Test Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests with RDFLib (fast)
  python cli.py run --mode rdflib

  # Run specific dependency level with GraphDB
  python cli.py run --mode graphdb --level 1

  # Run specific test
  python cli.py run --mode graphdb --test 0.1.4

  # Run level with materialization
  python cli.py run --mode graphdb --level 2 \\
    --materialize queries/materialize-level0.sparql queries/materialize-level1.sparql

  # Verify materialization script
  python cli.py verify --script queries/materialize-siblingOf.sparql

  # Reset GraphDB repository
  python cli.py reset --mode graphdb
        """
    )
    
    # Global arguments
    parser.add_argument('--mode', choices=['rdflib', 'graphdb'], default='rdflib',
                       help='Backend mode (default: rdflib)')
    parser.add_argument('--ontology', help='Path to ontology file')
    parser.add_argument('--graphdb-url', default='http://localhost:7200',
                       help='GraphDB URL (default: http://localhost:7200)')
    parser.add_argument('--repository', default='family-ontology-test',
                       help='GraphDB repository ID (default: family-ontology-test)')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Run tests command
    run_parser = subparsers.add_parser('run', help='Run tests')
    run_parser.add_argument('--level', 
                           help='Run specific dependency level (0-9 or "all")')
    run_parser.add_argument('--test', help='Run specific test ID (e.g., 0.1.4)')
    run_parser.add_argument('--data', nargs='+', help='Test data files')
    run_parser.add_argument('--test-file', help='Test definitions JSON file')
    run_parser.add_argument('--config', help='Test configuration JSON file')
    run_parser.add_argument('--materialize', nargs='+',
                           help='Materialization scripts to apply')
    run_parser.add_argument('--output', help='Output file for results (JSON)')
    run_parser.add_argument('--verbose', '-v', action='store_true',
                           help='Show expected and actual results for all tests')
    run_parser.set_defaults(func=cmd_run_tests)
    
    # Verify materialization command
    verify_parser = subparsers.add_parser('verify', help='Verify materialization script')
    verify_parser.add_argument('--script', required=True,
                              help='Path to materialization SPARQL script')
    verify_parser.set_defaults(func=cmd_verify_materialization)
    
    # Reset repository command
    reset_parser = subparsers.add_parser('reset', help='Reset GraphDB repository')
    reset_parser.set_defaults(func=cmd_reset_repository)
    
    # Parse and execute
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()