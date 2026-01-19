#!/usr/bin/env python3
"""
Generate materialize-all.json from test-config.json.

This script:
1. Reads materialization_requirements from test-config.json
2. Concatenates files following dependency level order (0, 1, 2, ...)
3. Removes duplicates while preserving order
4. Extracts only filenames (removes path)
5. Only regenerates if test-config.json is newer than materialize-all.json
"""

import json
import os
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory (parent of scripts folder)."""
    return Path(__file__).parent.parent


def should_regenerate(source_path: Path, target_path: Path) -> bool:
    """Check if target needs regeneration based on modification times."""
    if not target_path.exists():
        return True
    
    source_mtime = source_path.stat().st_mtime
    target_mtime = target_path.stat().st_mtime
    
    return source_mtime > target_mtime


def extract_filename(filepath: str) -> str:
    """Extract filename from a path string."""
    return Path(filepath).name


def generate_materialization_order(config: dict) -> list[str]:
    """
    Generate ordered list of materialization files.
    
    Processes levels in numeric order (0, 1, 2, ...) and concatenates
    files while removing duplicates (preserving first occurrence).
    """
    requirements = config.get("materialization_requirements", {})
    
    # Sort levels numerically
    sorted_levels = sorted(requirements.keys(), key=int)
    
    seen = set()
    ordered_files = []
    
    for level in sorted_levels:
        files = requirements[level]
        for filepath in files:
            filename = extract_filename(filepath)
            if filename not in seen:
                seen.add(filename)
                ordered_files.append(filename)
    
    return ordered_files


def main():
    project_root = get_project_root()
    
    source_path = project_root / "tests" / "test-config.json"
    target_path = project_root / "sparql" / "materialisation" / "materialize-all.json"
    
    # Check if regeneration is needed
    if not should_regenerate(source_path, target_path):
        print(f"No regeneration needed: {target_path.name} is up to date.")
        return 0
    
    # Read source config
    if not source_path.exists():
        print(f"Error: Source file not found: {source_path}", file=sys.stderr)
        return 1
    
    with open(source_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # Generate materialization order
    materialization_order = generate_materialization_order(config)
    
    # Create output structure
    output = {
        "materialization_order": materialization_order
    }
    
    # Write target file
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
        f.write("\n")
    
    print(f"Generated {target_path.name} with {len(materialization_order)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
