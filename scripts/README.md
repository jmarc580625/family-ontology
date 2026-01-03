# Family Ontology Dependency Analyzer

This tool analyzes an OWL ontology file to determine the dependency order of property chain axioms, which is crucial for proper testing and materialization of inferred relationships.

## Features

- Extracts property chain dependencies from OWL ontologies
- Performs topological sort to determine processing order
- Detects circular dependencies
- Generates a human-readable report and machine-readable output
- Helps ensure tests run in the correct order

## Prerequisites

- Python 3.8+
- Required packages listed in `requirements.txt`

## Installation

1. Clone the repository (if not already done):
   ```bash
   git clone <repository-url>
   cd family-network
   ```

2. Install the required packages:
   ```bash
   pip install -r scripts/requirements.txt
   ```

## Usage

### Basic Usage

```bash
python scripts/dependency_analyzer.py path/to/your/ontology.ttl
```

### Output

The script generates two types of output:

1. **Console Output**:
   - Dependency graph showing relationships between properties
   - Topologically sorted list of relationships

2. **File Outputs** (saved to `scripts/output/`):
   - `relationship_order.txt`: Ordered list of relationships for testing
   - `dependency_graph.mmd`: Mermaid diagram of the dependency graph
   - `graph_data.json`: Machine-readable graph data
   - All files include generation metadata (timestamp, source file)

### Viewing the Diagram

You can view the generated Mermaid diagram by:

1. Opening the `.mmd` file in any text editor and copying its contents to:
   - [Mermaid Live Editor](https://mermaid.live)
   - VS Code with the Mermaid extension
   - Any other Mermaid-compatible viewer

2. The diagram will show the dependencies between relationships, with arrows indicating the direction of dependency.

### Example

```bash
$ python scripts/dependency_analyzer.py ontology/family-ontology.ttl

Dependency Graph:
:uncleAuntOf depends on: :parentOf, :siblingOf
:siblingInLawOf depends on: :spouseOf, :siblingOf
...

Topologically Sorted Relationships:
1. :spouseOf
2. :parentOf
3. :childOf
4. :siblingOf
5. :siblingInLawOf
6. :uncleAuntOf
...

Saved ordered relationships to relationship_order.txt
```

## Integration with Tests

You can use the generated `relationship_order.txt` to drive your test execution:

```python
# Example test_runner.py
import os

def run_tests_in_order(order_file='relationship_order.txt'):
    with open(order_file) as f:
        test_order = [line.strip() 
                     for line in f 
                     if line.strip() and not line.startswith('#')]
    
    for relationship in test_order:
        print(f"\n=== Testing: {relationship} ===")
        # Your test logic here
        # Example: run_test_for_relationship(relationship)

if __name__ == "__main__":
    run_tests_in_order()
```

## Error Handling

The script will raise an error if it detects:
- Circular dependencies in property chains
- Invalid OWL syntax
- Missing or inaccessible ontology files

## Troubleshooting

1. **Missing Dependencies**:
   ```
   ModuleNotFoundError: No module named 'rdflib'
   ```
   Solution: Run `pip install -r requirements.txt`

2. **File Not Found**:
   ```
   FileNotFoundError: [Errno 2] No such file or directory: 'nonexistent.owl'
   ```
   Solution: Verify the path to your ontology file

3. **Circular Dependency**:
   ```
   ValueError: Cycle detected in property chain dependencies
   ```
   Solution: Check your ontology for circular property chain definitions

## License

[Specify your license here]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
