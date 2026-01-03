import os
import json
import rdflib
import datetime
from rdflib.namespace import OWL, RDF, RDFS
from collections import defaultdict

class OntologyDependencyAnalyzer:
    def __init__(self, ontology_file):
        """Initialize the analyzer with an ontology file.
        
        Args:
            ontology_file (str): Path to the OWL ontology file in Turtle format
            
        Raises:
            FileNotFoundError: If the ontology file doesn't exist
            SyntaxError: If there's a syntax error in the ontology
            Exception: For any other parsing errors
        """
        if not os.path.exists(ontology_file):
            raise FileNotFoundError(f"Ontology file not found: {ontology_file}")
            
        self.graph = rdflib.Graph()
        try:
            self.graph.parse(ontology_file, format='turtle')
        except Exception as e:
            # Try to extract line number from the error message
            import re
            line_match = re.search(r'line (\d+)', str(e))
            if line_match:
                line_num = int(line_match.group(1))
                context = self._get_error_context(ontology_file, line_num)
                raise SyntaxError(
                    f"Error parsing ontology at line {line_num}:\n"
                    f"Context: {context}\n"
                    f"Error: {str(e)}"
                ) from e
            raise
            
        self.dependencies = defaultdict(set)
        self.reverse_deps = defaultdict(set)
        self.sorted_relations = []
        self.visited = set()
        self.temp_marked = set()
    
    def _get_error_context(self, file_path, line_num, context_lines=3):
        """Get context around a line number in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                start = max(0, line_num - context_lines - 1)
                end = min(len(lines), line_num + context_lines)
                context = []
                for i in range(start, end):
                    prefix = '>> ' if i + 1 == line_num else '   '
                    context.append(f"{prefix}{i+1}: {lines[i].rstrip()}")
                return '\n'.join(context)
        except Exception:
            return "(Could not retrieve context)"

    def extract_dependencies(self):
        """Extract property dependencies from the ontology.
        
        This method analyzes both:
        1. OWL property chain axioms (owl:propertyChainAxiom)
        2. Custom materialization dependency annotations (:materializationDependency)
        
        to build a dependency graph where an edge A -> B means that A depends on B.
        """
        # Clear any existing dependencies
        self.dependencies = defaultdict(set)
        self.reverse_deps = defaultdict(set)
        
        # Define the family ontology namespace for custom annotations
        FAMILY = rdflib.Namespace("http://example.org/family#")
        
        # 1. Get all properties with property chain axioms (OWL-based)
        for prop, _, chain_node in self.graph.triples((None, OWL.propertyChainAxiom, None)):
            if not isinstance(chain_node, rdflib.term.BNode):
                continue
                
            # Get the property that has this chain
            prop_uri = str(prop)
            
            # Get all components in the chain
            chain = list(self.graph.items(chain_node))
            
            # The property depends on all components in the chain
            for dep in chain:
                dep_uri = str(dep)
                # Skip blank nodes and literals
                if not isinstance(dep, (rdflib.URIRef, rdflib.Literal)):
                    continue
                    
                # Add the dependency
                self.dependencies[prop_uri].add(dep_uri)
                self.reverse_deps[dep_uri].add(prop_uri)
        
        # 2. Get all properties with materialization dependencies (custom annotation)
        for prop, _, dep in self.graph.triples((None, FAMILY.materializationDependency, None)):
            if not isinstance(prop, rdflib.URIRef) or not isinstance(dep, rdflib.URIRef):
                continue
            
            prop_uri = str(prop)
            dep_uri = str(dep)
            
            # Add the dependency
            self.dependencies[prop_uri].add(dep_uri)
            self.reverse_deps[dep_uri].add(prop_uri)

    def topological_sort(self):
        """Perform topological sort using depth-first search."""
        # Get all nodes (both dependents and dependencies)
        all_nodes = set(self.dependencies.keys())
        all_nodes.update(*self.dependencies.values())
        
        # Reset state
        self.visited = set()
        self.sorted_relations = []
        
        # Visit each unvisited node
        for node in all_nodes:
            if node not in self.visited:
                self._visit(node)
        
        return self.sorted_relations
    
    def _visit(self, node):
        """Helper function for topological sort."""
        if node in self.temp_marked:
            raise ValueError("Cycle detected in property chain dependencies")
        
        if node not in self.visited:
            self.temp_marked.add(node)
            
            # Visit all dependencies first
            for dep in sorted(self.dependencies.get(node, set())):
                self._visit(dep)
            
            self.visited.add(node)
            self.temp_marked.remove(node)
            self.sorted_relations.append(node)
    
    def get_dependency_graph(self):
        """Return the dependency graph as a dictionary."""
        return dict(self.dependencies)
    
    def _calculate_dependency_levels(self):
        """Calculate dependency levels for all properties using BFS.
        
        Returns:
            tuple: (nodes, relationships, dependency_levels, max_level)
                - nodes: set of all node names
                - relationships: list of (source, target) tuples
                - dependency_levels: dict mapping node names to their dependency level
                - max_level: maximum dependency level found
        """
        # Initialize data structures
        nodes = set()
        relationships = []
        dependency_levels = {}
        
        # First pass: collect all nodes and relationships
        for prop_uri, deps in self.dependencies.items():
            prop = self._get_short_name(prop_uri)
            nodes.add(prop)
            for dep_uri in deps:
                dep = self._get_short_name(dep_uri)
                nodes.add(dep)
                relationships.append((dep, prop))  # dep -> prop means prop depends on dep
        
        # Build the graph and reverse graph
        graph = {node: [] for node in nodes}  # Forward edges
        rev_graph = {node: [] for node in nodes}  # Reverse edges
        
        for source, target in relationships:
            graph[source].append(target)
            rev_graph[target].append(source)
        
        # Initialize levels - nodes with no dependencies start at level 0
        levels = {}
        # First, process all nodes with no dependencies (level 0)
        for node in nodes:
            if not rev_graph[node]:  # No dependencies
                levels[node] = 0
        
        # Then process nodes with dependencies
        changed = True
        while changed:
            changed = False
            for node in nodes:
                if node in levels:
                    continue  # Already processed
                
                # Get all dependencies
                deps = rev_graph[node]
                if not deps:  # Shouldn't happen due to first pass, but just in case
                    levels[node] = 0
                    changed = True
                    continue
                
                # Check if all dependencies have been processed
                if all(dep in levels for dep in deps):
                    # Node level is max dependency level + 1
                    max_dep_level = max(levels[dep] for dep in deps)
                    levels[node] = max_dep_level + 1
                    changed = True
        
        # Ensure all nodes have a level (should be the case, but just to be safe)
        for node in nodes:
            if node not in levels:
                levels[node] = 0  # Default to level 0 if somehow not processed
        
        # Find the maximum level
        max_level = max(levels.values()) if levels else 0
        
        return nodes, relationships, levels, max_level

    def generate_mermaid_diagram(self, output_file='dependency_graph.mmd', source_file=None):
        """Generate a Mermaid diagram of the dependency graph with level-based coloring.
        
        Args:
            output_file (str): Path to save the Mermaid diagram
            source_file (str, optional): Path to the source ontology file
            
        Returns:
            str: Path to the generated Mermaid diagram file
        """
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)) or '.', exist_ok=True)
        
        # Calculate dependency levels and get relationships
        nodes, relationships, dependency_levels, max_level = self._calculate_dependency_levels()
        
        # Define the Mermaid diagram with styles
        mermaid = [
            '%%{init: {"theme": "base", "themeVariables": { "background": "#ffffff" }}}%%',
            'graph LR',
            '    %% Define styles',
            '    classDef default fill:#ffffff,stroke:#333,stroke-width:1px,color:#000000',
            '    classDef Level0 fill:#90ee90,stroke:#333,stroke-width:1px,color:#000000',
            '    classDef Level1 fill:#ffffe0,stroke:#333,stroke-width:1px,color:#000000',
            '    classDef Level2 fill:#ffd580,stroke:#333,stroke-width:1px,color:#000000',
            '    classDef Level3Plus fill:#ffb6c1,stroke:#333,stroke-width:1px,color:#000000',
            '',
            '    %% Container styles',
            '    style Dependencies fill:#ffffff,stroke:#333,stroke-width:1px',
            '    style Context fill:#ffffff,stroke:#333,stroke-width:1px',
            '    linkStyle default fill:none,stroke:#333,stroke-width:1px',
            ''
        ]
        
        # Initialize a dictionary to store nodes by level
        nodes_by_level = defaultdict(list)
        for node in nodes:
            level = dependency_levels.get(node, 0)
            nodes_by_level[level].append(node)
        
        # Create a mapping of nodes to their level for quick lookup
        node_levels = {node: level for node, level in dependency_levels.items()}
        
        # Add level 0 nodes first
        if 0 in nodes_by_level:
            mermaid.append('    %% Level 0 nodes (no dependencies)')
            for node in sorted(nodes_by_level[0]):
                mermaid.append(f'    {node}:::Level0')
            mermaid.append('')
        
        # Process nodes level by level (starting from 1)
        for level in sorted(nodes_by_level.keys()):
            # Skip level 0 as we already processed it
            if level == 0:
                continue
                
            # For each node in this level, add its definition
            mermaid.append(f'    %% Level {level} nodes')
            for node in sorted(nodes_by_level[level]):
                # Add node with appropriate style
                style_level = min(level, 3)
                mermaid.append(f'    {node}:::Level{style_level if style_level < 3 else "3Plus"}')
            
            # Add a blank line after each level for readability
            mermaid.append('')
        
        # Add context information in its own subgraph at the end
        if source_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            context_subgraph = [
                '    %% Context information (appears at the bottom)',
                '    subgraph Context["Context"]',
                '        direction TB',
                '        style Context fill:#ffffff,stroke:#333,stroke-width:1px',
                '        style context fill:#ffffff,stroke:none,color:#000000',
                f'        context["Source: {os.path.basename(source_file)}\nGenerated: {timestamp}\n' +
                f'Total nodes: {len(nodes)}, Relationships: {len(relationships)}\n' +
                f'Max dependency depth: {max_level}"]',
                '    end'
            ]

        # Add dependencies in a subgraph, grouped by target level
        mermaid.extend([
            '',
            '    subgraph Dependencies["Dependencies"]',
            '        direction LR',
            ''
        ])
        
        # Buffer for storing dependencies
        dependency_buffer = []
        
        # Process dependencies level by level
        for level in sorted(nodes_by_level.keys()):
            # Skip level 0 as they have no dependencies
            if level == 0:
                continue
                
            # Add a comment for this level
            dependency_buffer.append(f'        %% Level {level} dependencies')
            
            # Process each node at this level
            for node in sorted(nodes_by_level[level]):
                # Find all dependencies of this node
                for source, target in relationships:
                    if target == node:  # This is a dependency of the current node
                        dependency_buffer.append(f'        {source} --> {target}')
            
            # Add a blank line after each level for readability
            dependency_buffer.append('')
        
        # Add all buffered dependencies to the diagram
        mermaid.extend(dependency_buffer)
        
        # Close the Dependencies subgraph
        mermaid.append('    end')
        
        # Add the context subgraph at the end if source file was provided
        if source_file:
            mermaid.extend([''] + context_subgraph)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(mermaid) + '\n')
        
        return output_file
    
    def _format_node_name(self, node_uri):
        """Convert a node URI to a valid Mermaid node name."""
        # Extract the last part of the URI after # or /
        name = node_uri.split('#')[-1].split('/')[-1]
        # Replace special characters with underscores
        return name.replace('-', '_').replace(':', '_')
    
    def _get_short_name(self, node_uri):
        """Get a short, readable name for a node."""
        # Extract the last part of the URI after # or /
        return node_uri.split('#')[-1].split('/')[-1]
    
    def dump_graph_data(self, output_file='graph_data.json'):
        """Dump graph data to a JSON file for debugging.
        
        Args:
            output_file (str): Path to save the JSON file
        """
        # Calculate dependency levels and get relationships
        nodes, relationships, dependency_levels, max_level = self._calculate_dependency_levels()
        
        # Group nodes by level
        nodes_by_level = defaultdict(list)
        for node, level in dependency_levels.items():
            nodes_by_level[level].append(node)
        
        # Sort nodes within each level to ensure consistent ordering
        for level in nodes_by_level:
            nodes_by_level[level].sort()
        
        # Build graph data structure
        graph_data = {
            'nodes': {},
            'relationships': [],
            'levels': {},
            'levels_ordered': {}
        }
        
        # Add nodes with their levels and dependencies
        for node in sorted(nodes):
            graph_data['nodes'][node] = {
                'level': dependency_levels.get(node, 0),
                'dependencies': [],
                'dependents': []
            }
        
        # Add relationships and build adjacency lists
        for source, target in relationships:
            graph_data['relationships'].append({
                'source': source,
                'target': target
            })
            
            if source in graph_data['nodes'] and target in graph_data['nodes']:
                graph_data['nodes'][source]['dependents'].append(target)
                graph_data['nodes'][target]['dependencies'].append(source)
        
        # Add levels and ordered levels
        graph_data['levels'] = dependency_levels
        
        # Create ordered levels structure
        for level in sorted(nodes_by_level.keys()):
            graph_data['levels_ordered'][f'level_{level}'] = nodes_by_level[level]
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_file)) or '.', exist_ok=True)
        
        # Write to file
        with open(output_file, 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        return output_file
    

def print_usage():
    """Print usage information."""
    print("""
Family Ontology Dependency Analyzer
---------------------------------

Usage: python dependency_analyzer.py <ontology_file.ttl>

This tool analyzes an OWL ontology file to determine the dependency order of property chain axioms.

Arguments:
  ontology_file.ttl  Path to the OWL ontology file in Turtle format

Output files will be saved in the 'output' directory:
  - relationship_order.txt  : Ordered list of relationships by dependency level
  - dependency_graph.mmd    : Mermaid diagram of the dependency graph
  - graph_data.json         : Complete graph data in JSON format

Example:
  python dependency_analyzer.py family-ontology.ttl
""")

def write_ordered_relationships(output_file, relationships, dependency_levels):
    """Write relationships to a file, grouped by dependency level.
    
    Args:
        output_file (str): Path to the output file
        relationships (list): List of relationship URIs in topological order
        dependency_levels (dict): Dictionary mapping short relationship names to their dependency levels
    """
    # Group relationships by level
    relationships_by_level = {}
    for rel in relationships:
        # Extract short name from URI to match with dependency_levels
        rel_name = rel.split('#')[-1].split('/')[-1]
        level = dependency_levels.get(rel_name, 0)
        if level not in relationships_by_level:
            relationships_by_level[level] = []
        relationships_by_level[level].append(rel)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Ordered Relationships by Dependency Level\n")
        f.write(f"# Generated at: {datetime.datetime.now().isoformat()}\n\n")
        
        # Write relationships grouped by level
        for level in sorted(relationships_by_level.keys()):
            # Level 0 has no dependencies, other levels show their depth
            if level == 0:
                f.write(f"## Level 0 (Base relationships - no dependencies)\n")
            else:
                f.write(f"## Level {level} (Dependency Depth: {level})\n")
            for rel in sorted(relationships_by_level[level]):
                # Extract just the relationship name from the URI
                rel_name = rel.split('#')[-1].split('/')[-1]
                f.write(f"- {rel_name} ({rel})\n")
            f.write("\n")

def main():
    import sys
    import os
    import datetime
    
    # Check command line arguments
    if len(sys.argv) != 2 or sys.argv[1] in ['-h', '--help']:
        print_usage()
        return 1 if len(sys.argv) > 1 and sys.argv[1] not in ['-h', '--help'] else 0
    
    ontology_file = sys.argv[1]
    
    try:
        # Print header
        print("=" * 80)
        print(f"Family Ontology Dependency Analyzer")
        print(f"{'=' * 80}")
        print(f"Ontology file: {os.path.abspath(ontology_file)}")
        print(f"Start time:    {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 80)
        
        # Initialize and analyze
        print("[1/4] Parsing ontology file...")
        analyzer = OntologyDependencyAnalyzer(ontology_file)
        
        print("[2/4] Extracting property chain dependencies...")
        analyzer.extract_dependencies()
        
        print("[3/4] Calculating dependency order...")
        sorted_rels = analyzer.topological_sort()
        
        # Get dependency levels for output
        nodes, relationships, dependency_levels, max_level = analyzer._calculate_dependency_levels()
        
        # Print summary
        print("\n" + "=" * 80)
        print("Dependency Analysis Results")
        print("=" * 80)
        
        print("\nDependency Graph:")
        for prop, deps in analyzer.get_dependency_graph().items():
            prop_short = prop.split('#')[-1].split('/')[-1]
            deps_short = [d.split('#')[-1].split('/')[-1] for d in sorted(deps)]
            print(f"- {prop_short} depends on: {', '.join(deps_short) or '(none)'}")
        
        print("\nTopologically Sorted Relationships:")
        for i, rel in enumerate(sorted_rels, 1):
            rel_short = rel.split('#')[-1].split('/')[-1]
            level = dependency_levels.get(rel_short, 0)
            print(f"{i:2d}. {rel_short} (Level {level})")
        
        # Save output files
        print("\n" + "-" * 80)
        print("Generating output files...")
        
        # Output directory is relative to the script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # Save ordered relationships with level grouping
        order_file = os.path.join(output_dir, 'relationship_order.txt')
        write_ordered_relationships(order_file, sorted_rels, dependency_levels)
        
        # Generate Mermaid diagram
        print("Generating Mermaid diagram...")
        mmd_file = os.path.join(output_dir, 'dependency_graph.mmd')
        analyzer.generate_mermaid_diagram(mmd_file, source_file=ontology_file)
        print(f"Mermaid diagram saved to: {os.path.abspath(mmd_file)}")
        
        # Dump graph data for debugging
        print("\nDumping graph data...")
        graph_data_file = os.path.join(output_dir, 'graph_data.json')
        analyzer.dump_graph_data(graph_data_file)
        print(f"Graph data saved to: {os.path.abspath(graph_data_file)}")
        
        # Print success message
        print("\n" + "=" * 80)
        print("Analysis Complete!")
        print("=" * 80)
        print(f"\nOutput files saved to:")
        print(f"- Ordered relationships: {os.path.abspath(order_file)}")
        print(f"- Mermaid diagram:       {os.path.abspath(mmd_file)}")
        print(f"- Graph data (JSON):     {os.path.abspath(graph_data_file)}")
        print("\nYou can view the diagram using any Mermaid-compatible viewer or paste the")
        print(f"contents of {os.path.basename(mmd_file)} into the Mermaid Live Editor:")
        print("https://mermaid.live")
        
    except FileNotFoundError as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        return 1
    except SyntaxError as e:
        print(f"\nSyntax Error in Ontology:\n{'=' * 80}\n{str(e)}\n{'=' * 80}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"\n{'*' * 80}", file=sys.stderr)
        print("An unexpected error occurred:", file=sys.stderr)
        print(f"{type(e).__name__}: {str(e)}\n", file=sys.stderr)
        print("Stack trace:", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        print("\n" + "*" * 80, file=sys.stderr)
        return 3
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
