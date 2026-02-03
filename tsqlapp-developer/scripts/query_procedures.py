#!/usr/bin/env python3
"""
TSQL.APP Procedure Query Tool

Query the CSV procedure catalog to verify procedures and extract parameter signatures.
This script helps ensure code generation uses only documented procedures.
"""

import csv
import sys
from pathlib import Path
from typing import List, Dict, Optional


def load_procedures_csv(csv_path: str) -> List[Dict[str, str]]:
    """Load the procedures CSV file into memory."""
    procedures = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            procedures.append(row)
    return procedures


def find_procedure(procedures: List[Dict[str, str]], proc_name: str) -> List[Dict[str, str]]:
    """Find all parameters for a specific procedure."""
    return [p for p in procedures if p['ProcedureName'].lower() == proc_name.lower()]


def search_procedures(procedures: List[Dict[str, str]], pattern: str) -> List[str]:
    """Search for procedures matching a pattern."""
    matches = set()
    pattern_lower = pattern.lower()
    for p in procedures:
        if pattern_lower in p['ProcedureName'].lower():
            matches.add(p['ProcedureName'])
    return sorted(matches)


def format_parameter_info(param: Dict[str, str]) -> str:
    """Format parameter information for display."""
    parts = [f"  @{param['ParameterName'].lstrip('@')}"]
    
    # Type and size
    param_type = param['ParameterType']
    size = param['ParameterSize']
    if size and size != 'None' and size != '':
        if size == 'MAX' or size == '-1':
            parts.append(f"{param_type}(MAX)")
        else:
            parts.append(f"{param_type}({size})")
    else:
        parts.append(param_type)
    
    # Required/Optional
    is_required = param['IsRequired'] == 'Yes'
    parts.append("REQUIRED" if is_required else "optional")
    
    # Output
    is_output = param['IsOutput'] == 'Yes'
    if is_output:
        parts.append("OUTPUT")
    
    # Default value
    default = param.get('DefaultValue', 'None')
    if default and default != 'None' and not is_required:
        parts.append(f"default={default}")
    
    return " | ".join(parts)


def display_procedure_info(proc_name: str, params: List[Dict[str, str]]):
    """Display complete procedure information."""
    if not params:
        print(f"\n❌ Procedure '{proc_name}' NOT FOUND in catalog")
        return
    
    print(f"\n✅ Procedure: {proc_name}")
    print("=" * 80)
    
    # Separate required and optional parameters
    required = [p for p in params if p['IsRequired'] == 'Yes']
    optional = [p for p in params if p['IsRequired'] != 'Yes']
    
    if required:
        print("\nREQUIRED Parameters:")
        for param in required:
            print(format_parameter_info(param))
    
    if optional:
        print("\nOPTIONAL Parameters:")
        for param in optional:
            print(format_parameter_info(param))
    
    # Generate example usage
    print("\nExample Usage:")
    print("-" * 80)
    
    # Declare variables for OUTPUT parameters
    output_params = [p for p in params if p['IsOutput'] == 'Yes']
    for param in output_params:
        param_name = param['ParameterName'].lstrip('@')
        print(f"DECLARE @{param_name} NVARCHAR(MAX);")
    
    if output_params:
        print()
    
    # EXEC statement
    print(f"EXEC {proc_name}")
    for i, param in enumerate(required):
        param_name = param['ParameterName']
        is_output = param['IsOutput'] == 'Yes'
        value = f"@{param_name.lstrip('@')}" if is_output else f"N'value'"
        suffix = " OUT" if is_output else ""
        comma = "," if i < len(required) - 1 or optional else ";"
        print(f"    {param_name} = {value}{suffix}{comma}")
    
    print()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python query_procedures.py <procedure_name>     # Find specific procedure")
        print("  python query_procedures.py --search <pattern>   # Search for procedures")
        print()
        print("Examples:")
        print("  python query_procedures.py sp_api_modal_text")
        print("  python query_procedures.py --search modal")
        sys.exit(1)
    
    # Find CSV file
    script_dir = Path(__file__).parent
    csv_path = script_dir.parent / "references" / "tsql.app_procs-all.csv"
    
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        sys.exit(1)
    
    # Load procedures
    procedures = load_procedures_csv(str(csv_path))
    print(f"Loaded {len(procedures)} procedure parameter records")
    
    # Handle search mode
    if sys.argv[1] == "--search":
        if len(sys.argv) < 3:
            print("❌ Please provide a search pattern")
            sys.exit(1)
        
        pattern = sys.argv[2]
        matches = search_procedures(procedures, pattern)
        
        if not matches:
            print(f"\n❌ No procedures found matching '{pattern}'")
        else:
            print(f"\n✅ Found {len(matches)} procedures matching '{pattern}':")
            for proc in matches:
                print(f"  - {proc}")
        return
    
    # Find specific procedure
    proc_name = sys.argv[1]
    params = find_procedure(procedures, proc_name)
    display_procedure_info(proc_name, params)


if __name__ == "__main__":
    main()
