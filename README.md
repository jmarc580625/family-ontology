# Family Relationship Ontology

A comprehensive OWL2 DL ontology for modeling complex family relationships. Supports 66 relationship properties including biological, adoptive, in-law, and blended family relationships with automated inference via SPARQL materialization.

## Key Features

- **66 Relationship Properties**: Core, extended, in-law, blended family, and social relationships
- **Class-Based Gender Modeling**: `:MalePerson` and `:FemalePerson` classes for gender-specific properties
- **OWL2 DL Compliance**: Property chains, inverse properties, symmetric/irreflexive constraints
- **SPARQL Materialization**: Complex relationships inferred via SPARQL UPDATE scripts
- **Documented Dependencies**: Custom annotation properties track materialization dependencies
- **Comprehensive Test Suite**: 66 tests across 10 dependency levels

## Project Structure

```
family-ontology/
├── ontology/
│   └── family-ontology.ttl       # Main ontology (66 properties, 527 triples)
├── sparql/
│   └── materialisation/          # SPARQL UPDATE scripts for inference
├── tests/
│   ├── cli.py                    # Test runner CLI
│   ├── test-config.json          # Test configuration with levels
│   ├── data/                     # Test data (family-sample-data.ttl, family-anchors-data.ttl)
│   └── backends/                 # RDFLib and GraphDB backends
├── scripts/
│   ├── dependency_analyzer.py    # Generates dependency graphs
│   └── output/                   # Generated graphs (created on demand)
├── doc/
│   ├── TODO.md                   # Future enhancements
│   └── blended_family_enhancement.md
├── docker-compose.yml            # GraphDB setup
├── requirements.txt              # Python dependencies
└── LICENSE                       # MIT License
```

## Quick Start

### Prerequisites

- Python 3.7+
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/jmarc580625/family-ontology.git
cd family-ontology

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all tests
python tests/cli.py run --level all

# Run specific level (0-9)
python tests/cli.py run --level 0

# Run specific test by ID
python tests/cli.py run --test 0.1.1
```

### Test Levels

| Level | Description |
|-------|-------------|
| 0 | Base relationships (parentOf, childOf, spouseOf) |
| 1 | First-order inference (grandparent, parentInLaw, sibling, twin) |
| 2 | Second-order inference (greatGrandparent, uncleAunt, siblingInLaw) |
| 3 | Third-order inference (cousin) |
| 4-6 | Gender-specific variants |
| 7 | In-law relationships |
| 8 | Blended family (step, half-siblings) |
| 9 | Social relationships (godparents, friends) |

## Ontology Overview

### Classes

- `:Person` - Base class (equivalent to `foaf:Person`)
- `:Male`, `:Female` - Gender classes
- `:MalePerson`, `:FemalePerson` - Intersection classes for gender-specific properties

### Relationship Categories

**Core Family** (Level 0-1)
- `spouseOf`, `parentOf`, `childOf`, `siblingOf`, `twinOf`

**Extended Family** (Level 1-3)
- `grandparentOf`, `grandchildOf`, `greatGrandparentOf`, `greatGrandchildOf`
- `uncleAuntOf`, `niblingOf`, `cousinOf`

**In-Law Family** (Level 1-2)
- `parentInLawOf`, `childInLawOf`, `siblingInLawOf`

**Blended Family** (Level 1-2)
- `stepParentOf`, `stepChildOf`, `stepSiblingOf`, `halfSiblingOf`

**Gender-Specific** (Level 4-7)
- All of the above with male/female variants (e.g., `motherOf`, `fatherOf`, `sisterOf`, `brotherOf`)

**Social** (Level 9)
- `godParentOf`, `godChildOf`, `friendOf`, `closeFriendOf`, `witnessOf`

### Materialization Dependencies

The ontology uses custom annotation properties to document SPARQL materialization:

```turtle
:siblingOf
    :materializationDependency :parentOf ;
    :materializationScript "sparql/materialisation/materialize-siblingOf-GN.sparql" ;
    :materializationReason "OWL property chains cannot express irreflexive constraint" ;
    :materializationLevel 1 .
```

## Dependency Analysis

Generate relationship dependency graphs:

```bash
python scripts/dependency_analyzer.py ontology/family-ontology.ttl
```

Outputs:
- `scripts/output/dependency_graph.mmd` - Mermaid diagram
- `scripts/output/graph_data.json` - JSON graph data
- `scripts/output/relationship_order.txt` - Topological sort

## Using with GraphDB

> **Note**: GraphDB integration is implemented but not yet fully tested. The test suite currently runs against RDFLib by default. GraphDB support is available for users who want native OWL2-RL reasoning.

```bash
# Start GraphDB
docker-compose up -d

# Wait ~30 seconds for GraphDB to initialize, then verify setup
python scripts/verify_graphdb.py

# Access GraphDB Workbench at http://localhost:7200

# Run tests with GraphDB backend (experimental)
python tests/cli.py --mode graphdb run --level all
```

## Sample SPARQL Queries

### Find All Siblings

```sparql
PREFIX : <http://example.org/family#>

SELECT ?person ?sibling WHERE {
    ?person :siblingOf ?sibling .
    FILTER(STR(?person) < STR(?sibling))
}
```

### Find Grandparents

```sparql
PREFIX : <http://example.org/family#>

SELECT ?grandparent ?grandchild WHERE {
    ?grandparent :grandparentOf ?grandchild .
}
```

### Find All Relationships for a Person

```sparql
PREFIX : <http://example.org/family#>

SELECT ?relationship ?relative WHERE {
    :Alice ?relationship ?relative .
    FILTER(STRSTARTS(STR(?relationship), STR(:)))
}
```

## Extending the Ontology

1. Add new properties to `ontology/family-ontology.ttl`
2. If SPARQL materialization needed, add script to `sparql/materialisation/`
3. Add materialization annotations to the property
4. Add tests to `tests/test-config.json`
5. Run `python scripts/dependency_analyzer.py` to update graphs

## License

MIT License - see [LICENSE](LICENSE) file.
