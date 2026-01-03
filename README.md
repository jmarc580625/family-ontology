# 🧬 Family Relationship Ontology

A comprehensive and expressive ontology for modeling complex family relationships using RDF and OWL. This implementation provides a robust framework for representing and reasoning about family structures with support for both immediate and extended family relationships.

## 🌟 Key Features

- **Comprehensive Relationship Modeling**: Covers a wide range of family relationships including:
  - Core: parent/child, sibling, spouse
  - Extended: grandparent/grandchild, uncle/aunt, cousin
  - Blended: step-relationships, half-siblings, in-laws
  - Gender-specific: mother, father, son, daughter, etc.

- **OWL 2 DL Compliance**: Built with OWL 2 DL expressivity for maximum compatibility with reasoners

- **Modular Design**: Organized into logical sections for maintainability and extensibility

- **Standard Alignment**: Extends established vocabularies:
  - FOAF (Friend of a Friend)
  - Relationship Vocabulary
  - Schema.org

- **Automated Testing**: Comprehensive test suite with:
  - Unit tests for individual relationships
  - Integration tests for complex family structures
  - Automated test runner with detailed reporting

---

## 📦 Project Structure

```
family-network/
├── family-ontology.ttl        # Main ontology file with all class and property definitions
├── materialize-inferences.rq  # SPARQL rules for materializing inferred relationships
├── tests/
│   ├── data/                  # Test data files in Turtle format
│   ├── family-relationships.json  # Test cases with SPARQL queries
│   └── test-runner.py         # Python script to execute test cases
└── README.md                  # This documentation
```

---

## 🧪 Testing Approach

The test suite ensures the correctness of family relationships defined in the ontology. It uses a combination of test data and SPARQL queries to validate both explicit and inferred relationships.

### Test Components

1. **Test Data** (`tests/data/family-sample-data.ttl`)
   - Contains sample individuals and their relationships
   - Used as the foundation for running test queries
   - Includes various family relationships for comprehensive testing

2. **Test Cases** (`tests/family-relationships.json`)
   - Defines test cases as SPARQL queries with expected results
   - Organized by relationship types (spouse, parent/child, sibling, etc.)
   - Each test case includes:
     - Unique ID (e.g., "0.1.1")
     - Name and description
     - SPARQL query to execute
     - Expected results in JSON format

3. **Test Runner** (`tests/test-runner.py`)
   - Python script that executes test cases against the ontology
   - Compares actual query results with expected results
   - Provides detailed pass/fail reporting
   - Supports running individual tests or the entire test suite

### Running Tests

```bash
# Run all tests
python tests/test-runner.py family-ontology.ttl tests/family-relationships.json

# Run specific test by ID
python tests/test-runner.py family-ontology.ttl tests/family-relationships.json --test 0.1.1
```

### Test Case Example

```json
"0.1.1": {
  "name": "Spouse relationships",
  "description": "Test spouse relationships (explicit in data, reflexive)",
  "query": """
    SELECT ?spouse1 ?spouse2 WHERE {
      ?spouse1 :spouseOf ?spouse2 .
    }
    ORDER BY ?spouse1 ?spouse2
  """,
  "expected": [
    { "spouse1": ":Alice", "spouse2": ":Antoine" },
    { "spouse1": ":Antoine", "spouse2": ":Alice" }
  ]
}
```

### Test Categories

1. **Basic Relationships**
   - Spouse relationships
   - Parent/child relationships
   - Sibling relationships

2. **Extended Family**
   - Grandparent/grandchild
   - Uncle/aunt relationships
   - Cousin relationships

3. **Advanced Relationships**
   - Step relationships
   - Half-siblings
   - In-law relationships

## 📘 Ontology Summary

The ontology defines:

- **Classes**: `Person`, `Male`, `Female`
- **Object Properties**:
  - Core: `hasParent`, `hasChild`, `hasSibling`, `hasSpouse`
  - Inferred: `hasGrandparent`, `hasUncleOrAunt`, `hasCousin`
- **Individuals**: `alice`, `bob`, `carol`, `eva`, `david`

These allow you to describe family trees and derive indirect relationships using logic.

---

## 🚀 Testing the Family Ontology

### Prerequisites: GraphDB Setup

1. **Install and Configure GraphDB**
   - Download and install [GraphDB Free/Standard/Enterprise](https://www.ontotext.com/products/graphdb/)
   - Start the GraphDB server

2. **Create a New Repository**
   - Open GraphDB Workbench (typically at http://localhost:7200)
   - Navigate to "Setup" → "Repositories" → "Create new repository"
   - Configure with these settings:
     - Repository ID: `family-ontology`
     - Ruleset: `OWL2-RL`
     - Enable "Enable context index"
     - Enable "Enable predicate list index"
     - Enable "Enable sameAs"
   - Click "Create"

3. **Import the Ontology and Sample Data**
   - Go to "Import" → "RDF"
   - Upload both files:
     - `family-ontology.ttl` (the main ontology)
     - `tests/data/family-sample-data.ttl` (sample test data)
   - Select the "family-ontology" repository
   - Click "Import"

### Option 1: Manual Testing in GraphDB

1. **Run Test Queries**
   - Open the "SPARQL" tab in GraphDB Workbench
   - Select the "family-ontology" repository
   - Copy a test query from `tests/family-relationships.json`
   - Execute and verify results against expected output

2. **Example Test Query**
   ```sparql
   # Test 0.1.1 - Spouse relationships
   PREFIX : <http://example.org/family#>
   
   SELECT ?spouse1 ?spouse2 WHERE {
     ?spouse1 :spouseOf ?spouse2 .
   }
   ORDER BY ?spouse1 ?spouse2
   ```

3. **Test Results Verification**
   - **PASS**: Actual results match expected results in the test case
   - **FAIL**: Results differ from expected
   - **ERROR**: Query execution failed

### Option 2: Automated Testing with Python

1. **Prerequisites**
   - Python 3.7+
   - Install required package:
     ```bash
     pip install rdflib
     ```

2. **Run All Tests**
   ```bash
   python tests/test-runner.py family-ontology.ttl tests/family-relationships.json
   ```

3. **Run Specific Test**
   ```bash
   python tests/test-runner.py family-ontology.ttl tests/family-relationships.json --test 1.1.1
   ```

---

## 🔎 Sample SPARQL Queries

### 1. List All Family Members

```sparql
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX : <http://example.org/family#>

SELECT ?person ?gender WHERE {
  ?person a foaf:Person ;
          foaf:gender ?gender .
} ORDER BY ?person
```

### 2. Find All Spouse Relationships

```sparql
PREFIX : <http://example.org/family#>

SELECT ?spouse1 ?spouse2 WHERE {
  ?spouse1 :spouseOf ?spouse2 .
  FILTER(STR(?spouse1) < STR(?spouse2))  # Avoid duplicate pairs
} ORDER BY ?spouse1
```

### 3. Find Parents and Their Children

```sparql
PREFIX : <http://example.org/family#>

SELECT ?parent ?child WHERE {
  ?parent :parentOf ?child .
} ORDER BY ?parent ?child
```

### 4. Find All Sibling Pairs (Including Twins)

```sparql
PREFIX : <http://example.org/family#>

SELECT ?sibling1 ?sibling2 WHERE {
  {
    ?sibling1 :siblingOf ?sibling2 .
  } UNION {
    ?sibling1 :twinOf ?sibling2 .
  }

} ORDER BY ?sibling1
```

### 5. Find Grandparent-Grandchild Relationships

```sparql
PREFIX : <http://example.org/family#>

SELECT ?grandparent ?grandchild WHERE {
  ?grandparent :parentOf/:parentOf ?grandchild .
} ORDER BY ?grandparent, ?grandchild
```

### 6. Find All Family Members with Their Relationships

```sparql
PREFIX : <http://example.org/family#>

SELECT ?person1 ?relationship ?person2 WHERE {
  {
    ?person1 :spouseOf ?person2 .
    BIND("spouse" AS ?relationship)
  } UNION {
    ?person1 :parentOf ?person2 .
    BIND("parent" AS ?relationship)
  } UNION {
    ?person1 :siblingOf ?person2 .
    BIND("sibling" AS ?relationship)
  } UNION {
    ?person1 :twinOf ?person2 .
    BIND("twin" AS ?relationship)
  }
} ORDER BY ?person1 ?relationship ?person2
```

### 7. Who is David's grandparent?

PREFIX : <http://example.org/family#>
SELECT ?grandparent WHERE {
  :david :hasGrandparent ?grandparent .
}

📄 License
This ontology is released under the MIT License. Feel free to modify and reuse.
