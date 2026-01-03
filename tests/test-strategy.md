# Family Ontology Test Strategy

## Overview
This document outlines the testing strategy for validating inference rules and materialized relationships in the family ontology. The strategy is organized into rounds, with each round building upon the previous one to ensure proper dependency handling.

## Core Principles

### Axiom Chain Strategy
1. **Minimize Reasoning Steps**: Build upon existing relationships rather than recreating longer chains
   - Prefer `[ :parentOf :grandparentOf ]` over `[ :parentOf :parentOf :parentOf ]`
   - Example: `:greatGrandParentOf` should use `[ :parentOf :grandparentOf ]`

2. **Consistent Directionality**:
   - For symmetric relationships, only one direction needs to be asserted
   - For inverse relationships, only one direction needs to be asserted
   - Maintain consistent directionality across all test cases

3. **Test Data Principles**:
   - **Minimal Base Data**: Only include facts that cannot be inferred
   - **Symmetric Relationships**: Only assert one direction (e.g., only `A spouseOf B`, not both)
   - **Inverse Relationships**: Only assert one direction (e.g., only `A parentOf B`, not `B childOf A`)
   - **Consistency**: Maintain a single, consistent direction for all relationships

## Test Numbering Scheme

### Structure
Test IDs in `family-relationships.json` follow a hierarchical numbering pattern: `X.Y.Z`

- **X**: Test round/category
  - `0`: Base relationships and core inferences
  - `1`: Extended family relationships
  - `2`: Special relationships (twins, etc.)
- **Y**: Relationship type group
  - `.1.`: Primary family relationships
  - `.2.`: Gender-specific relationships
  - `.3.`: Special cases
- **Z**: Specific test case within the group

### Mapping to Test File
Each test in `family-relationships.json` is identified by its ID (e.g., `0.1.1`). The test file contains:
- `name`: Human-readable test name
- `description`: Purpose and scope
- `query`: SPARQL query to execute
- `expected`: Expected results

Example:
```json
"0.1.1": {
  "name": "Spouse relationships",
  "description": "Test spouse relationships (explicit in data, reflexive)",
  "query": "...",
  "expected": [...]
}
```

## Testing Rounds

### Round 0: Representative relationships sample 

#### Step 1: Direct Base Relationships and basic inferences
- **Objective**: Verify core relationships and basic inferences
- **Test Cases**:
  - `0.1.1` - Spouse relationships (symmetric)
  - `0.1.2` - Parent-child relationships (inverse of child)
  - `2.1.1` - Twin relationships (symmetric)

#### Step 2: One-Level Inferences
- **Objective**: Test relationships derived directly from base relationships
- **Test Cases**:
  - `0.1.4` - Sibling relationships (symetric, from shared parents)

#### Step 3: Two-Level Inferences
- **Objective**: Test relationships that depend on one-level inference
- **Test Cases**:
  - `1.1.1` - Grandparent relationships (parentOf ∘ parentOf)

#### Step 3: Inverse of two-Level Inferences
- **Objective**: Test inverse relationships of one-level inference
- **Test Cases**:
  - `1.1.2` - Grandchild relationships (inverse of grandparentOf)

#### Step 3: Gender-specific Inferences
- **Objective**: Test relationships that depend on gender
- **Test Cases**:
  - `0.2.1` - Mother relationships


### Round 1: Gender-Neutral Relationships

#### Step 1: Direct Base Relationships
- **Objective**: Verify core relationships that can't be inferred
- **Test Cases**:
  - `0.1.1` - Spouse relationships (symmetric)
  - `0.1.2` - Parent-child relationships
  - `2.1.1` - Twin relationships (symmetric)

#### Step 2: First-Level Inferences
- **Objective**: Test relationships derived directly from base relationships
- **Test Cases**:
  - `0.1.4` - Sibling relationships (from shared parents)

#### Step 3: Second-Level Inferences
- **Objective**: Test relationships that depend on first-level inferences
- **Test Cases**:
  - `1.1.1` - Grandparent relationships (parentOf ∘ parentOf)
  - `1.1.2` - Grandchild relationships (inverse of grandparentOf)

#### Step 4: In-Law Relationships
- **Objective**: Test relationships through marriage
- **Test Cases**:
  - `1.1.3` - Parent-in-law relationships
  - `1.1.4` - Child-in-law relationships
  - `1.1.5` - Sibling-in-law relationships

#### Step 5: Extended Family
- **Objective**: Test more distant family relationships
- **Test Cases**:
  - `1.1.6` - Uncle/Aunt relationships (siblingOf ∘ parentOf)

### Round 2: Gender-Specific Relationships

#### Step 1: Core Gender-Specific
- **Objective**: Test basic gendered relationships
- **Test Cases**:
  - `0.2.1` - Mother relationships
  - `0.2.2` - Father relationships
  - `0.2.3` - Daughter relationships
  - `0.2.4` - Son relationships
  - `0.2.5` - Sister relationships
  - `0.2.6` - Brother relationships

#### Step 2: Extended Gender-Specific
- **Objective**: Test gendered extended family relationships
- **Test Cases**:
  - (Future) Grandmother/Grandfather
  - (Future) Aunt/Uncle

#### Step 3: Blended Family
- **Objective**: Test step-relationships and other blended family terms
- **Test Cases**:
  - (Future) Step-mother/Step-father
  - (Future) Step-siblings

## Test Data Principles

1. **Minimal Base Data**:
   - Only include facts that cannot be inferred
   - For symmetric relationships, only assert one direction
   - For inverse relationships, only assert one direction

2. **Property Chain Strategy**:
   - Prefer building on existing relationships (e.g., `[ :parentOf :grandparentOf ]` over `[ :parentOf :parentOf ]`)
   - Document all property chains for maintainability

3. **Test Data Structure**:
   ```
   tests/
   ├── data/
   │   ├── round1-step1-base.ttl
   │   ├── round1-step2-inverses.ttl
   │   └── round2-step1-gender-specific.ttl
   ├── queries/
   │   ├── round1/
   │   └── round2/
   └── expected/
       ├── round1/
       └── round2/
   ```

## Implementation Status

### Completed
- [x] Base relationship tests (0.1.1, 0.1.2, 2.1.1)
- [x] First-level inference tests (0.1.3, 0.1.4)

### In Progress
- [ ] Second-level inference tests (1.1.1, 1.1.2)
- [ ] In-law relationship tests (1.1.3-1.1.5)
- [ ] Extended family tests (1.1.6)

### Pending
- [ ] Gender-specific relationship tests (0.2.1-0.2.6)
- [ ] Blended family tests

## Next Steps
1. Complete test cases for Round 1, Step 3
2. Implement property chains for extended family relationships
3. Add test data for gender-specific relationships
4. Document any required materialization rules

## Known Limitations
1. Reasoner support for complex property chains may vary
2. Performance considerations for deep inference chains
3. Need to handle edge cases in blended families

---

## GraphDB Container Testing Approaches

### Overview
This section outlines different approaches for integrating GraphDB containers into the test execution workflow. Each approach has trade-offs in terms of complexity, isolation, performance, and CI/CD integration.

### Approach 1: Single Shared Container with Repository Management

**Description**: Run a single GraphDB container that stays up across all tests. Create/delete repositories for test isolation.

**Architecture**:
```
┌─────────────────────────────────────┐
│     Test Runner (Python)            │
│  - Load ontology via HTTP API       │
│  - Execute SPARQL queries           │
│  - Manage repository lifecycle      │
└──────────────┬──────────────────────┘
               │ HTTP REST API
               ▼
┌─────────────────────────────────────┐
│   GraphDB Container (Persistent)    │
│  - OWL2-RL Reasoner                 │
│  - Multiple repositories            │
│  - Port 7200 exposed                │
└─────────────────────────────────────┘
```

**Pros**:
- Fast test execution (no container startup overhead)
- Easy to inspect state between tests (via GraphDB workbench)
- Mimics production GraphDB setup
- Good for local development and debugging

**Cons**:
- Requires manual container lifecycle management
- Repository creation/deletion adds complexity
- State leakage risk if cleanup fails
- Not ideal for parallel test execution
- Requires GraphDB to be running before tests

**Implementation Requirements**:
- Docker Compose file for GraphDB
- Python library for GraphDB REST API (`requests` or `SPARQLWrapper`)
- Repository creation/deletion logic in test setup/teardown
- Health check to ensure GraphDB is ready

**Use Cases**:
- Local development and debugging
- Interactive testing with GraphDB workbench
- Manual test execution

---

### Approach 2: Container Per Test Suite

**Description**: Spin up a fresh GraphDB container for each test suite execution, then tear it down.

**Architecture**:
```
┌─────────────────────────────────────┐
│     Test Runner (Python)            │
│  - Start GraphDB container          │
│  - Wait for ready                   │
│  - Create repository                │
│  - Load ontology                    │
│  - Execute all tests                │
│  - Stop container                   │
└──────────────┬──────────────────────┘
               │ Docker API
               ▼
┌─────────────────────────────────────┐
│   GraphDB Container (Ephemeral)     │
│  - Fresh state per run              │
│  - Single repository                │
│  - Deleted after tests              │
└─────────────────────────────────────┘
```

**Pros**:
- Complete isolation between test runs
- No state leakage
- Automated lifecycle (no manual start/stop)
- Works well in CI/CD pipelines
- Clean and predictable

**Cons**:
- Slower (30-60s container startup time)
- Not suitable for rapid iterative testing
- Higher resource usage during startup
- Network configuration complexity

**Implementation Requirements**:
- Python Docker SDK (`docker` package)
- Container startup with health checks
- Repository auto-creation script
- Wait logic for GraphDB readiness (poll `/rest/repositories` endpoint)
- Proper cleanup in teardown/exception handlers

**Use Cases**:
- CI/CD pipeline testing
- Regression test suites
- Automated nightly builds
- Ensuring clean state for each run

---

### Approach 3: Container Per Test Case (Maximum Isolation)

**Description**: Create a new container for each individual test case.

**Architecture**:
```
For each test case:
  ┌─────────────────────────────┐
  │  Start Container            │
  │  Load Minimal Data          │
  │  Execute Single Test        │
  │  Capture Results            │
  │  Stop Container             │
  └─────────────────────────────┘
```

**Pros**:
- Ultimate test isolation
- Parallel execution potential
- No cross-test contamination
- Easy to debug individual tests

**Cons**:
- Very slow (minutes for full test suite)
- High resource consumption
- Overhead not justified for most use cases
- Complexity in managing multiple containers

**Implementation Requirements**:
- Same as Approach 2, but per test
- Parallel container orchestration
- Resource pooling and limits

**Use Cases**:
- Debugging specific failing tests
- Parallel test execution on powerful CI systems
- Validating specific inference scenarios

**Not Recommended** for this project due to overhead vs. benefit ratio.

---

### Approach 4: Hybrid - Docker Compose + Pytest Fixtures

**Description**: Use Docker Compose for container management, pytest fixtures for test lifecycle.

**Architecture**:
```
┌─────────────────────────────────────┐
│        docker-compose.yml           │
│  - GraphDB service definition       │
│  - Named volumes for persistence    │
│  - Network configuration            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     Pytest + Fixtures               │
│  - session: Start/stop compose      │
│  - module: Repository setup         │
│  - function: Data loading           │
└─────────────────────────────────────┘
```

**Pros**:
- Declarative container configuration
- Excellent for local development
- pytest fixtures provide clean test structure
- Can mix container and in-memory tests
- Easy to add additional services (e.g., monitoring)

**Cons**:
- Requires pytest framework adoption
- Docker Compose must be installed
- Slightly more complex setup

**Implementation Requirements**:
- Docker Compose file with GraphDB service
- Pytest with fixtures for different scopes
- `pytest-docker-compose` or similar plugin
- Repository management via fixtures

**Use Cases**:
- Professional test automation
- Teams familiar with pytest
- Mixed testing strategies (unit + integration)

---

### Approach 5: Testcontainers Pattern

**Description**: Use Testcontainers library for programmatic container management.

**Architecture**:
```
┌─────────────────────────────────────┐
│     Test Runner (Python)            │
│  - Testcontainers library           │
│  - Automatic lifecycle              │
│  - Dynamic port allocation          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Testcontainers Framework          │
│  - Container lifecycle mgmt         │
│  - Health checks                    │
│  - Log capture                      │
│  - Automatic cleanup                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   GraphDB Container                 │
└─────────────────────────────────────┘
```

**Pros**:
- Industry-standard pattern
- Automatic container lifecycle
- Built-in health checks and wait strategies
- Dynamic port allocation (no conflicts)
- Excellent for CI/CD
- Log capture for debugging
- Works with pytest, unittest, or standalone

**Cons**:
- Adds dependency on Testcontainers library
- Requires Docker daemon access
- Startup time still present

**Implementation Requirements**:
- Install `testcontainers` Python package
- Create GraphDB container wrapper class
- Implement wait strategies for GraphDB readiness
- Repository initialization logic

**Use Cases**:
- Modern testing best practices
- CI/CD pipelines
- Integration testing
- Teams using containers in testing

---

### Approach 6: In-Memory RDFLib (Current) vs. GraphDB Dual Mode

**Description**: Keep current RDFLib tests, add optional GraphDB integration tests.

**Architecture**:
```
┌─────────────────────────────────────┐
│     Test Runner (Configurable)      │
│  ┌──────────────┐  ┌──────────────┐ │
│  │  RDFLib Mode │  │ GraphDB Mode │ │
│  │  - Fast      │  │  - Complete  │ │
│  │  - Limited   │  │  - Slow      │ │
│  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────┘
```

**Pros**:
- Fast local testing with RDFLib
- Comprehensive testing with GraphDB
- Gradual migration path
- Best of both worlds
- Flexible for different scenarios

**Cons**:
- Maintaining two test paths
- Potential inconsistencies between reasoners
- More complex test configuration

**Implementation Requirements**:
- Abstract test runner interface
- Backend selection (env var or CLI flag)
- Separate test suites or markers

**Use Cases**:
- Transitioning from RDFLib to GraphDB
- Quick local tests + thorough CI tests
- Comparing reasoner behavior

---

### Comparison Matrix

| Approach | Startup Time | Isolation | CI/CD Ready | Complexity | Debug Ease | Cost |
|----------|-------------|-----------|-------------|------------|------------|------|
| 1. Shared Container | 0s (running) | Low | Moderate | Low | Excellent | Low |
| 2. Per Suite | 30-60s | High | Excellent | Medium | Good | Medium |
| 3. Per Test | High (minutes) | Maximum | Poor | High | Good | High |
| 4. Docker Compose + Pytest | 30-60s | High | Excellent | Medium | Excellent | Medium |
| 5. Testcontainers | 30-60s | High | Excellent | Medium | Good | Medium |
| 6. Dual Mode | 0s / 30-60s | Medium | Excellent | High | Good | Medium |

---

### Recommended Approach for This Project

**Primary Recommendation: Approach 5 (Testcontainers) + Approach 6 (Dual Mode)**

**Rationale**:
1. **Testcontainers** provides professional-grade container management
2. **Dual Mode** allows fast local iteration with RDFLib
3. CI/CD runs full GraphDB tests for comprehensive validation
4. Easy to understand and maintain
5. Industry-standard pattern

**Implementation Plan**:
1. Keep existing RDFLib test runner for local quick tests
2. Add Testcontainers-based GraphDB test runner
3. Use environment variable to select mode: `TEST_MODE=rdflib|graphdb`
4. CI/CD runs both modes:
   - Quick smoke tests with RDFLib
   - Full integration tests with GraphDB

**Fallback Option: Approach 4 (Docker Compose + Pytest)**
- If team prefers explicit Docker Compose control
- If already using pytest extensively
- Simpler if Testcontainers seems over-engineered

---

### Key Questions for Discussion

1. **Test Execution Frequency**:
   - How often will tests run? (After each commit? Daily? On-demand?)
   - Are we optimizing for developer speed or CI thoroughness?

2. **Resource Constraints**:
   - CI/CD resource limits (memory, CPU, time)?
   - Local development machine capabilities?

3. **Team Preferences**:
   - Pytest adoption vs. current test framework?
   - Comfort level with Docker/containers?
   - Preference for explicit control vs. magic abstractions?

4. **Testing Strategy**:
   - Will we phase out RDFLib entirely or keep both?
   - Need for parallel test execution?
   - Importance of testing against exact production reasoner?

5. **GraphDB Configuration**:
   - Which GraphDB edition? (Free, Standard, Enterprise)
   - Required ruleset? (OWL2-RL, RDFS-Plus, custom)
   - Licensing considerations for CI/CD?

6. **Data Loading Strategy**:
   - Load ontology + data once or per test?
   - Incremental data loading for different test rounds?
   - Materialization vs. on-demand inference?

---

### Next Steps After Discussion

1. **Select primary approach** based on answers to key questions
2. **Create PoC** with 2-3 tests using chosen approach
3. **Measure performance** (startup time, execution time, resource usage)
4. **Document setup** for team members
5. **Create CI/CD pipeline** configuration
6. **Migrate existing tests** incrementally
7. **Add GraphDB-specific tests** that leverage advanced reasoning

---

### Additional Considerations

#### GraphDB Container Image
- Official: `ontotext/graphdb:10.x-free` (or standard/enterprise)
- Pre-configured with repositories?
- Custom image with our ontology baked in?

#### Authentication & Security
- GraphDB free doesn't require auth by default
- Standard/Enterprise may need credentials
- How to manage secrets in CI/CD?

#### Performance Optimization
- Container image caching in CI/CD
- Volume mounting vs. HTTP upload for ontology
- Keep container warm between test rounds?

#### Monitoring & Debugging
- Capture GraphDB logs on test failure
- GraphDB workbench access during local testing
- Query performance metrics collection

---

## Workflow-Specific Approach Recommendation

### Your Specific Requirements

Based on your incremental testing and materialization discovery workflow:

**Key Characteristics**:
1. **Static Test Data**: No data modification during testing
2. **Pre-defined Tests**: All tests and expected results in `family-relationships.json`
3. **Dependency-Driven**: Testing follows relationship dependency levels (0-3)
4. **Iterative Refinement**: Discover materialization needs through failures
5. **Database Reset Required**: Frequent resets with accumulated materialization scripts

**Your Process Flow**:
```
For each dependency level (0 → 3):
  ├─ Load ontology + test data
  ├─ Run step tests
  ├─ IF PASS → Continue to next level
  └─ IF FAIL (axiom chain unsupported)
     ├─ Identify missing materialization
     ├─ Create/update SPARQL materialization script
     ├─ Reset database
     ├─ Reload ontology + data
     ├─ Apply ALL materialization scripts
     ├─ Verify materialization worked
     └─ Retry step
```

---

### Optimal Approach for Your Workflow

**Recommended: Approach 1 (Shared Container) + Reset Script**

This differs from the general recommendation because your workflow benefits from:

#### Why Shared Container Works Best Here

1. **Manual Inspection During Failures**
   - When a test fails, you need to inspect GraphDB workbench
   - Understand why inference didn't happen
   - Craft the correct materialization query
   - Container stays running for interactive debugging

2. **Rapid Iteration Cycle**
   - Write materialization script
   - Reset repository (seconds, not 30-60s container restart)
   - Re-run test
   - Iterate until it works

3. **State Inspection Between Steps**
   - Verify what was inferred at each dependency level
   - Query intermediate relationships
   - Check materialization results

4. **Materialization Script Development**
   - Test SPARQL INSERT queries interactively
   - See results immediately in workbench
   - Debug complex property chains

#### Implementation Design

**Architecture**:
```
┌─────────────────────────────────────────────────────┐
│  Test Orchestrator (Python)                        │
│  ────────────────────────────────────────────────  │
│  For each dependency level:                         │
│    1. Reset repository (DELETE + CREATE)            │
│    2. Load ontology (family-ontology.ttl)           │
│    3. Load test data (family-sample-data.ttl)       │
│    4. Apply materialization scripts (level 0..N-1)  │
│    5. Run level N tests                             │
│    6. Report: PASS | FAIL | need materialization   │
└────────────────────┬────────────────────────────────┘
                     │ GraphDB REST API
                     ▼
┌─────────────────────────────────────────────────────┐
│  GraphDB Container (Long-Running)                   │
│  ────────────────────────────────────────────────  │
│  Repository: family-ontology-test                   │
│  Ruleset: OWL2-RL                                   │
│  Workbench: http://localhost:7200                   │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Materialization Scripts (Accumulated)              │
│  ────────────────────────────────────────────────  │
│  queries/materialize-level0.sparql  (if needed)     │
│  queries/materialize-level1.sparql  (if needed)     │
│  queries/materialize-level2.sparql  (if needed)     │
└─────────────────────────────────────────────────────┘
```

**Key Components**:

1. **Repository Reset Function**
   ```python
   def reset_repository(graphdb_url, repo_name):
       """Delete and recreate repository for clean state"""
       # DELETE /rest/repositories/{repo}
       # POST /rest/repositories with config
   ```

2. **Data Loading Function**
   ```python
   def load_data(graphdb_url, repo_name, files):
       """Load RDF files into repository"""
       for file in files:
           # POST /repositories/{repo}/statements
   ```

3. **Materialization Executor**
   ```python
   def apply_materializations(graphdb_url, repo_name, scripts):
       """Execute SPARQL UPDATE queries for materialization"""
       for script in scripts:
           # POST /repositories/{repo}/statements (SPARQL UPDATE)
   ```

4. **Test Runner with Level Support**
   ```python
   def run_level_tests(level, tests, materialization_scripts):
       reset_repository()
       load_data([ontology, sample_data])
       apply_materializations(materialization_scripts[0:level])
       results = execute_tests(tests[level])
       return results
   ```

---

### Workflow Support Features

#### Feature 1: Dependency Level Testing

**Command**:
```bash
python test_runner.py --mode graphdb --level 0
python test_runner.py --mode graphdb --level 1 --materialize queries/materialize-level0.sparql
python test_runner.py --mode graphdb --level 2 --materialize queries/materialize-level*.sparql
```

**Test Configuration** (extends `family-relationships.json`):
```json
{
  "test_levels": {
    "0": ["0.1.1", "0.1.2", "2.1.1"],
    "1": ["0.1.3", "0.1.4", "1.1.1"],
    "2": ["1.1.3", "1.1.4", "1.1.5"],
    "3": ["1.1.6"]
  },
  "materialization_requirements": {
    "1": [],  # Level 1 may need materializations discovered from level 0 failures
    "2": [],  # Level 2 may need materializations discovered from level 1 failures
    "3": []   # Level 3 may need materializations discovered from level 2 failures
  }
}
```

#### Feature 2: Failure Analysis

**When Test Fails**:
```python
def analyze_failure(test_id, expected, actual):
    """Analyze why inference failed and suggest materialization"""
    if len(actual) == 0:
        return {
            "reason": "no_inference",
            "suggestion": "Property chain may not be supported",
            "action": "Create materialization query",
            "template": generate_materialization_template(test_id)
        }
    elif len(actual) < len(expected):
        return {
            "reason": "partial_inference",
            "missing": set(expected) - set(actual),
            "action": "Check specific patterns"
        }
```

#### Feature 3: Interactive Debug Mode

**Command**:
```bash
python test_runner.py --mode graphdb --level 1 --test 0.1.4 --debug
```

**Behavior**:
- Run test
- On failure, pause and print:
  - Expected vs Actual results
  - GraphDB workbench URL with query pre-filled
  - Suggestion for materialization
  - Wait for user to press Enter after manual inspection
  - Option to re-run test or skip

#### Feature 4: Materialization Verification

**Command**:
```bash
python test_runner.py --verify-materialization queries/materialize-siblingOf.sparql
```

**Process**:
1. Reset repository
2. Load ontology + data
3. Execute materialization script
4. Query to verify expected triples were added
5. Report success/failure with triple counts

---

### Materialization Discovery Workflow

**Example: Level 1 - siblingOf Relationship**

**Step 1: Run Test**
```bash
$ python test_runner.py --mode graphdb --level 1 --test 0.1.4

================================================================================
Test 0.1.4: Sibling relationships
Description: Test sibling relationships (inferred)
❌ FAIL

Expected:
[
  { "sibling1": ":Bob", "sibling2": ":Carol" },
  { "sibling1": ":Carol", "sibling2": ":Bob" }
]

Actual:
[]

Analysis:
- Reason: No inference occurred
- Property chain: siblingOf not inferred from shared parentOf
- Action: Create materialization query

Suggested materialization template saved to:
  queries/materialize-siblingOf-template.sparql

Inspect in GraphDB Workbench:
  http://localhost:7200/sparql?query=...
```

**Step 2: Craft Materialization**

Create `queries/materialize-siblingOf.sparql`:
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

**Step 3: Verify Materialization**
```bash
$ python test_runner.py --verify-materialization queries/materialize-siblingOf.sparql

✅ Materialization successful
- Triples added: 2
- Verification query passed
- Added relationships:
  :Bob :siblingOf :Carol
  :Carol :siblingOf :Bob
```

**Step 4: Retry Test with Materialization**
```bash
$ python test_runner.py --mode graphdb --level 1 --test 0.1.4 \
    --materialize queries/materialize-siblingOf.sparql

✅ PASS
```

**Step 5: Update Documentation**

Add to `materialization_requirements` in test config:
```json
"materialization_requirements": {
  "1": ["queries/materialize-siblingOf.sparql"]
}
```

---

### Answers to Key Questions (Context-Aware)

#### 1. Test Execution Frequency
**Answer**: High frequency during materialization discovery phase
- **Developer iteration**: Every few minutes while crafting materialization queries
- **Optimization**: Developer speed (fast reset) over CI thoroughness
- **Pattern**: Fail → Inspect → Craft → Verify → Retry

#### 2. Resource Constraints
**Answer**: Minimal - optimizing for single developer workflow
- **Local machine**: Primary environment
- **CI/CD**: Secondary (validation after materialization scripts complete)
- **Memory**: GraphDB container + workbench (~2GB)

#### 3. Team Preferences
**Answer**: Simple, interactive, inspection-friendly
- **Framework**: Keep current Python test runner, add GraphDB backend
- **Docker**: Docker Compose for simple start/stop
- **Control**: Explicit control preferred (manual container management)
- **Debugging**: Visual workbench access critical

#### 4. Testing Strategy
**Answer**: Dual mode with phase transition
- **Phase 1 (Current)**: Discover materialization needs with GraphDB
- **Phase 2 (Future)**: Validate complete ontology with both RDFLib + GraphDB
- **Keep both**: RDFLib for quick sanity checks, GraphDB for full validation
- **Parallel execution**: Not needed (sequential dependency levels)
- **Production match**: Essential during discovery phase

#### 5. GraphDB Configuration
**Answer**: 
- **Edition**: GraphDB Free (sufficient for testing, no license issues)
- **Ruleset**: OWL2-RL (matches ontology design)
- **Licensing**: No concerns with Free edition

#### 6. Data Loading Strategy
**Answer**: Complete reload per level
- **Pattern**: Reset → Load ontology → Load data → Apply level N-1 materializations → Test level N
- **Loading**: HTTP POST (simple, no volume mounting complexity)
- **Materialization**: Incremental (only apply scripts for previous levels)
- **Inference**: Automatic via OWL2-RL, supplemented by materialization

---

### Implementation Artifacts

**Files to Create**:

1. **`docker-compose.yml`** - GraphDB container setup
2. **`tests/graphdb_backend.py`** - GraphDB REST API wrapper
3. **`tests/test_runner_graphdb.py`** - Enhanced test runner with GraphDB support
4. **`queries/README.md`** - Materialization scripts documentation
5. **`tests/test_config.json`** - Level-to-test mapping with materialization requirements

**Enhanced Test Runner Features**:
- `--mode rdflib|graphdb` - Select backend
- `--level N` - Run specific dependency level
- `--test X.Y.Z` - Run specific test
- `--materialize file1.sparql file2.sparql` - Apply materializations
- `--verify-materialization file.sparql` - Test materialization script
- `--debug` - Interactive debugging mode
- `--reset-only` - Just reset repository

---

### Revised Recommendation

**For Your Specific Workflow**:

✅ **Use: Approach 1 (Shared Container)**
- Start once: `docker-compose up -d`
- Keep running during entire discovery phase
- Repository reset is fast (~2s)
- Workbench always available for inspection

✅ **Add: Enhanced Test Runner**
- Level-based test execution
- Materialization script management
- Failure analysis and suggestions
- Interactive debug mode

✅ **Transition Path**:
1. **Week 1-2**: Discovery phase with shared container
2. **Week 3**: Document all materialization requirements
3. **Week 4**: Implement CI/CD with Testcontainers for automated validation

**This approach prioritizes**:
- Fast iteration during materialization discovery
- Easy inspection and debugging
- Simple setup (no complex orchestration)
- Clear path to automated CI/CD later

---

### Quick Start

**Setup (5 minutes)**:
```bash
# 1. Start GraphDB
docker-compose up -d

# 2. Wait for ready
curl http://localhost:7200/rest/repositories

# 3. Run dependency level 0 tests
python tests/test_runner.py --mode graphdb --level 0

# 4. On failure, inspect in workbench
open http://localhost:7200

# 5. Create materialization, verify, retry
python tests/test_runner.py --verify-materialization queries/materialize-X.sparql
python tests/test_runner.py --mode graphdb --level 0 --materialize queries/materialize-X.sparql
```

This workflow-specific approach aligns with your incremental testing strategy and materialization discovery process.
