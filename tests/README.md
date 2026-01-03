# Family Ontology Test Suite

Test infrastructure for validating the family ontology with support for both in-memory (RDFLib) and triple store (GraphDB) backends.

## Directory Structure

```
tests/
├── backends/               # Database adapters
│   ├── __init__.py
│   ├── rdflib_backend.py  # In-memory testing (fast)
│   └── graphdb_backend.py # GraphDB with OWL2-RL reasoning
├── runners/                # Test execution engines
│   ├── __init__.py
│   ├── base_runner.py     # Core test runner
│   └── test_executor.py   # Level-based execution
├── data/                   # Test datasets
│   ├── family-sample-data.ttl
│   └── social-sample-data.ttl
├── cli.py                  # Main entry point ⭐
├── test-runner.py          # Legacy interface (backward compatible)
├── family-relationships.json  # Test definitions
├── test-config.json        # Level mappings
├── test-strategy.md        # Testing strategy documentation
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Quick Start

### 1. Set Up Virtual Environment (First Time Only)

```bash
# From project root
cd d:\family-network

# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Your prompt should now show (venv)
```

### 2. Install Dependencies

```bash
# Make sure venv is activated first!
cd tests
pip install -r requirements.txt
```

### 3. Run Tests with RDFLib (Fast, Local)

```bash
# Make sure venv is activated and you're in tests/ directory
cd tests

# Run all tests
python cli.py --mode rdflib run

# Run specific test
python cli.py --mode rdflib run --test 0.1.4
```

### 4. Run Tests with GraphDB (Complete Reasoning)

```bash
# Start GraphDB container (from project root)
cd ..
docker-compose up -d

# Wait for GraphDB to be ready (check http://localhost:7200)
# Then run tests (make sure venv is activated)
cd tests
python cli.py --mode graphdb run

# Run specific dependency level
python cli.py --mode graphdb run --level 1
```

---

## Usage

### Running Tests

**All tests (RDFLib)**:
```bash
python cli.py --mode rdflib run
```

**All tests (GraphDB)**:
```bash
python cli.py --mode graphdb run
```

**Specific dependency level**:
```bash
python cli.py --mode graphdb run --level 0  # Base relationships
python cli.py --mode graphdb run --level 1  # One-level inferences
python cli.py --mode graphdb run --level 2  # Two-level inferences
python cli.py --mode graphdb run --level 3  # Extended family
```

**Specific test**:
```bash
python cli.py --mode graphdb run --test 0.1.4
```

**With materialization scripts**:
```bash
python cli.py --mode graphdb run --level 2 \
  --materialize ../queries/materialize-level0.sparql ../queries/materialize-level1.sparql
```

**Save results to file**:
```bash
python cli.py --mode graphdb run --output my_results.json
```

### Verifying Materialization Scripts

```bash
python cli.py --mode graphdb verify --script ../queries/materialize-siblingOf.sparql
```

This command:
1. Resets the repository
2. Loads ontology and data
3. Applies the materialization script
4. Reports the number of triples added

### Resetting GraphDB Repository

```bash
python cli.py --mode graphdb reset
```

Useful when you need a clean state without restarting the container.

---

## Workflow: Materialization Discovery

This is the core workflow for discovering which relationships need materialization.

### Step 1: Run Level Tests

```bash
python cli.py --mode graphdb run --level 1
```

### Step 2: On Failure, Analyze

The test runner will provide:
- Expected vs actual results
- Failure analysis
- Suggested actions

Example output:
```
 FAIL

Expected:
[
  { "sibling1": ":Bob", "sibling2": ":Carol" },
  { "sibling1": ":Carol", "sibling2": ":Bob" }
]

Actual:
[]

────────────────────────────────────────────────────────────────────────────────
FAILURE ANALYSIS:
 No results returned (expected results)
 → Possible causes:
  • Property chain axiom not supported by reasoner
  • Inference not triggered
  • Missing data

→ Suggested action:
  • Create materialization query for this relationship
  • Check ontology axioms for test 0.1.4
────────────────────────────────────────────────────────────────────────────────
```

### Step 3: Create Materialization Script

Create `../queries/materialize-siblingOf.sparql`:

```sparql
PREFIX : <http://example.org/family#>

INSERT {
  ?sibling1 :siblingOf ?sibling2 .
}
WHERE {
  ?parent :parentOf ?sibling1 .
  ?parent :parentOf ?sibling2 .
  FILTER(?sibling1 != ?sibling2)
}
```

### Step 4: Verify Materialization

```bash
python cli.py --mode graphdb verify --script ../queries/materialize-siblingOf.sparql
```

Expected output:
```
================================================================================
VERIFYING MATERIALIZATION: materialize-siblingOf.sparql
================================================================================
Statements before: 125
  • Applying: materialize-siblingOf.sparql
    Applied successfully
Statements after:  127

 Materialization successful
   Added 2 new statement(s)
```

### Step 5: Re-run Tests with Materialization

```bash
python cli.py --mode graphdb run --level 1 --materialize ../queries/materialize-siblingOf.sparql
```

Expected output:
```
================================================================================
Test 0.1.4: Sibling relationships
Description: Test sibling relationships (inferred)
 PASS
```

### Step 6: Update Configuration

Add to `test-config.json`:

```json
"materialization_requirements": {
  "1": ["../queries/materialize-siblingOf.sparql"]
}
```

---

## Test Levels

Tests are organized by dependency depth (see `test-config.json`):

| Level | Name | Tests | Relationships |
|-------|------|-------|---------------|
| **0** | Base relationships | 0.1.1, 0.1.2, 2.1.1 | spouseOf, parentOf, twinOf |
| **1** | One-level inferences | 0.1.3, 0.1.4, 1.1.1, 1.1.2 | childOf, siblingOf, grandparentOf |
| **2** | Two-level inferences | 0.2.1, 1.1.3-1.1.5 | niblingOf, uncleAuntOf, in-laws |
| **3** | Extended family | 1.1.6 | cousinOf, great-grandparents |

---

## Backend Comparison

| Feature | RDFLib | GraphDB |
|---------|--------|----------|
| **Speed** | Fast (in-memory) | Slower (container + reasoning) |
| **Reasoning** | Basic RDFS | Complete OWL2-RL |
| **Use Case** | Quick iteration | Complete validation |
| **Setup** | None | Docker required |
| **Startup** | Instant | 30-60 seconds |
| **Inspection** | Limited | Workbench UI |
| **Property Chains** | Limited support | Full support |
| **Materialization** | Supported | Supported |

### When to Use Which?

- **RDFLib**: Fast local tests during development
- **GraphDB**: Discover materialization needs, validate complete ontology

---

## GraphDB Configuration

Configured in `../docker-compose.yml`:
- **Edition**: GraphDB Free
- **Version**: 10.7.0
- **Ruleset**: OWL2-RL
- **Port**: 7200
- **Workbench**: http://localhost:7200
- **Heap Size**: 2GB

---

## Backward Compatibility

The legacy `test-runner.py` still works for RDFLib mode:

```bash
python test-runner.py ../family-ontology.ttl family-relationships.json
```

This is equivalent to:
```bash
python cli.py --mode rdflib --ontology ../family-ontology.ttl --test-file family-relationships.json run
```

---

## Tips & Best Practices

### Development Workflow

1. **Fast iteration**: Use RDFLib for quick tests during development
   ```bash
   python cli.py --mode rdflib run
   ```

2. **Complete validation**: Use GraphDB to discover materialization needs
   ```bash
   python cli.py --mode graphdb run --level 1
   ```

3. **Interactive debugging**: Keep GraphDB workbench open during testing
   - Navigate to http://localhost:7200
   - Inspect inferred triples
   - Test SPARQL queries manually

4. **Clean state**: Reset repository between test runs for consistency
   ```bash
   python cli.py --mode graphdb reset
   ```

### Materialization Script Guidelines

1. **One relationship per script**: Keep scripts focused
2. **Test before committing**: Use `verify` command
3. **Document purpose**: Add comments explaining the relationship
4. **Handle edge cases**: Include FILTERs for self-relationships, duplicates

### Test Organization

- **Level 0**: Only base data, no inferences needed
- **Level 1**: May need materialization if reasoner doesn't support chains
- **Level 2+**: Likely needs materialization for complex chains

---

## Troubleshooting

### GraphDB not responding

```bash
# Check container status
cd ..
docker-compose ps

# View logs
docker-compose logs graphdb

# Restart container
docker-compose restart graphdb
```

### Connection refused

- Wait 30-60 seconds after `docker-compose up`
- Check http://localhost:7200 in browser
- Verify no other service is using port 7200

### Repository not found

```bash
python cli.py --mode graphdb reset
```

### Import errors

```bash
# Make sure virtual environment is activated!
venv\Scripts\activate

# Then install dependencies
cd tests
pip install -r requirements.txt
```

### Path issues (data files not found)

Ensure venv is activated and you're in the `tests/` directory:
```bash
# Activate venv
cd d:\family-network
venv\Scripts\activate

# Run tests
cd tests
python cli.py --mode rdflib run
```

### Test data in wrong location

The new structure expects test data in `tests/data/`:
- `tests/data/family-sample-data.ttl`
- `tests/family-sample-data.ttl` (old location)

---

## Examples

### Example 1: Quick Sanity Check

```bash
# Activate venv first
cd d:\family-network
venv\Scripts\activate
cd tests

# Fast check with RDFLib
python cli.py --mode rdflib run
```

### Example 2: Level-by-Level Validation

```bash
# Activate venv first
cd d:\family-network
venv\Scripts\activate
cd tests

# Test each level sequentially
python cli.py --mode graphdb run --level 0
python cli.py --mode graphdb run --level 1
python cli.py --mode graphdb run --level 2
python cli.py --mode graphdb run --level 3
```

### Example 3: Debug Specific Test

```bash
# Run one test with GraphDB for detailed analysis
python cli.py --mode graphdb run --test 0.1.4

# If it fails, inspect in workbench:
# http://localhost:7200/sparql
```

### Example 4: Complete Materialization Workflow

```bash
# 1. Run level and find failure
python cli.py --mode graphdb run --level 1

# 2. Create materialization script
# (Edit ../queries/materialize-siblingOf.sparql)

# 3. Verify it works
python cli.py --mode graphdb verify --script ../queries/materialize-siblingOf.sparql

# 4. Re-run with materialization
python cli.py --mode graphdb run --level 1 --materialize ../queries/materialize-siblingOf.sparql

# 5. Success! Update test-config.json
```

---

## Advanced Usage

### Custom Ontology File

```bash
python cli.py --mode rdflib --ontology /path/to/custom-ontology.ttl run
```

### Custom Test Data

```bash
python cli.py --mode graphdb run --data data/custom-data1.ttl data/custom-data2.ttl
```

### Custom GraphDB URL

```bash
python cli.py --mode graphdb --graphdb-url http://remote-server:7200 run
```

### Custom Repository

```bash
python cli.py --mode graphdb --repository my-custom-repo run
```

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Test Ontology

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        cd tests
        pip install -r requirements.txt
    
    - name: Run RDFLib tests
      run: |
        cd tests
        python cli.py --mode rdflib run
    
    - name: Start GraphDB
      run: docker-compose up -d
    
    - name: Wait for GraphDB
      run: sleep 60
    
    - name: Run GraphDB tests
      run: |
        cd tests
        python cli.py --mode graphdb run
```

---

## Contributing

### Adding New Tests

1. Add test definition to `family-relationships.json`
2. Assign appropriate test ID (e.g., `1.2.3`)
3. Add to relevant level in `test-config.json`
4. Run test to verify

### Adding New Backends

1. Create new backend in `backends/`
2. Implement required interface:
   - `initialize()`
   - `execute_query(sparql_query)`
   - `execute_update(sparql_update)`
   - `get_stats()`
   - `cleanup()`
3. Register in `backends/__init__.py`
4. Add to `cli.py` backend selection

---

## Reference

### CLI Commands Summary

```bash
# Run tests
python cli.py run [--mode MODE] [--level LEVEL] [--test TEST_ID]

# Verify materialization
python cli.py verify --script SCRIPT_PATH [--mode MODE]

# Reset repository
python cli.py reset --mode graphdb

# Get help
python cli.py --help
python cli.py run --help
```

### File Purposes

- `cli.py`: Main entry point with argparse
- `test-runner.py`: Legacy backward-compatible interface
- `family-relationships.json`: Test definitions with SPARQL queries
- `test-config.json`: Level mappings and materialization requirements
- `test-strategy.md`: Detailed testing strategy and methodology
- `requirements.txt`: Python dependencies
- `backends/`: Database adapter implementations
- `runners/`: Test execution logic
- `data/`: Test datasets

---

## See Also

- **Test Strategy**: See `test-strategy.md` for detailed methodology
- **Ontology**: See `../family-ontology.ttl` for relationship definitions
- **Dependency Analysis**: See `../scripts/dependency_analyzer.py`
- **GraphDB Docs**: https://graphdb.ontotext.com/documentation/
- **RDFLib Docs**: https://rdflib.readthedocs.io/

---

---

## Virtual Environment Quick Reference

### Windows

```bash
# Create venv (first time only)
python -m venv venv

# Activate venv (every session)
venv\Scripts\activate

# Deactivate when done
deactivate

# Check if venv is active
# Your prompt should show: (venv) C:\path\to\directory>
```

### Linux/Mac

```bash
# Create venv (first time only)
python3 -m venv venv

# Activate venv (every session)
source venv/bin/activate

# Deactivate when done
deactivate
```

### Troubleshooting venv

**PowerShell execution policy error**:
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**venv not activating**:
- Make sure you're in the project root (`d:\family-network`)
- Check that `venv\Scripts\activate.bat` exists
- Try: `venv\Scripts\activate.bat` directly

**Packages not found after installation**:
- Verify venv is activated (check for `(venv)` in prompt)
- Reinstall: `pip install -r tests/requirements.txt`

---

**Happy Testing!** 🧪✨