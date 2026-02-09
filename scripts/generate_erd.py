#!/usr/bin/env python3
"""
Generate ERD diagram for Salesforce schema.
Outputs Mermaid diagram format and CSV for Lucidchart import.
"""

import csv
from collections import defaultdict
from pathlib import Path

# Core Salesforce standard objects
CORE_OBJECTS = {
    'account', 'contact', 'opportunity', 'campaign', 'lead', 'user', 
    'case', 'task', 'event', 'contract', 'quote', 'order', 'product2',
    'pricebook2', 'pricebookentry', 'opportunitylineitem', 'contractlineitem',
    'campaignmember', 'opportunitycontactrole', 'accountcontactrole',
    'accountcontactrelation', 'accountteammember', 'opportunitystage',
    'product_2'
}

# Custom objects that are important (based on staging models)
CUSTOM_OBJECTS_OF_INTEREST = {
    'pse_proj_c', 'pse_assignment_c', 'pse_timecard_c', 'pse_practice_c',
    'pse_est_vs_actuals_c', 'pse_timecard_header_c', 'pse_time_period_c',
    'pse_schedule_c', 'pse_resource_request_c', 'pse_region_c', 'pse_milestone_c',
    'zuora_subscription_c', 'zuora_customer_account_c', 'zuora_zinvoice_c'
}

def analyze_schema(csv_path):
    """Analyze the schema CSV and extract relationships."""
    tables = set()
    columns_by_table = defaultdict(list)
    foreign_keys = defaultdict(list)
    table_has_id = defaultdict(bool)
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            table = row['table_name']
            column = row['column_name']
            tables.add(table)
            columns_by_table[table].append(column)
            
            if column == 'id':
                table_has_id[table] = True
            
            # Identify foreign keys
            if column.endswith('_id') and column != 'id':
                fk_name = column.replace('_id', '')
                ref_table = None
                
                # Direct match
                if fk_name in tables:
                    ref_table = fk_name
                # Standard Salesforce objects
                elif fk_name in CORE_OBJECTS:
                    ref_table = fk_name
                # Owner/User references
                elif fk_name in ['owner', 'created_by', 'last_modified_by']:
                    ref_table = 'user'
                # Custom object pattern (ends with _c)
                elif fk_name.endswith('_c') and fk_name in tables:
                    ref_table = fk_name
                # Custom field pattern (remove _c and check)
                elif fk_name.endswith('_c') and fk_name[:-2] in tables:
                    ref_table = fk_name[:-2]
                # PSE custom objects (pse_*_c)
                elif fk_name.startswith('pse_') and fk_name in tables:
                    ref_table = fk_name
                # Zuora custom objects (zuora_*_c)
                elif fk_name.startswith('zuora_') and fk_name in tables:
                    ref_table = fk_name
                # Plural to singular
                elif fk_name + 's' in tables:
                    ref_table = fk_name + 's'
                elif len(fk_name) > 1 and fk_name[:-1] in tables:
                    ref_table = fk_name[:-1]
                
                if ref_table and ref_table in tables:
                    foreign_keys[table].append((column, ref_table))
    
    return tables, columns_by_table, foreign_keys, table_has_id

def identify_important_tables(tables, foreign_keys, relationship_threshold=2):
    """Identify tables to include in ERD."""
    important = set()
    
    # Add core objects
    important.update(CORE_OBJECTS & tables)
    
    # Add custom objects of interest
    important.update(CUSTOM_OBJECTS_OF_INTEREST & tables)
    
    # Add tables with many relationships
    for table, fks in foreign_keys.items():
        if len(fks) >= relationship_threshold:
            important.add(table)
    
    # Add tables that are referenced by important tables (transitive closure)
    changed = True
    while changed:
        changed = False
        referenced_tables = set()
        for table in important:
            for fk_col, ref_table in foreign_keys.get(table, []):
                if ref_table not in important:
                    referenced_tables.add(ref_table)
                    changed = True
        important.update(referenced_tables)
    
    return important

def generate_mermaid_erd(tables, foreign_keys, important_tables):
    """Generate Mermaid ERD diagram."""
    lines = ["erDiagram"]
    
    # Sort tables for consistent output
    sorted_tables = sorted(important_tables)
    
    # Add table definitions (simplified - just show table name)
    for table in sorted_tables:
        # Use proper case for display
        display_name = table.replace('__c', '').replace('_', ' ').title()
        lines.append(f"    {table} {{")
        lines.append(f"        string id PK")
        lines.append(f"    }}")
    
    lines.append("")
    
    # Add relationships (with labels)
    relationship_set = set()
    for table in sorted_tables:
        for fk_col, ref_table in foreign_keys.get(table, []):
            if ref_table in important_tables and table != ref_table:
                # Use FK column name as relationship label
                rel_key = (table, ref_table, fk_col)
                if rel_key not in relationship_set:
                    relationship_set.add(rel_key)
                    # Clean up FK name for label
                    label = fk_col.replace('_id', '').replace('_c', '').replace('_', ' ').title()
                    # Determine cardinality (simplified - assume many-to-one)
                    lines.append(f"    {ref_table} ||--o{{ {table} : \"{label}\"")
    
    return "\n".join(lines)

def generate_lucidchart_csv(tables, foreign_keys, important_tables):
    """Generate CSV for Lucidchart import.
    
    Format: Entity1,Attribute1,Entity2,Attribute2,Cardinality,Label
    """
    lines = ["Entity1,Attribute1,Entity2,Attribute2,Cardinality,Label"]
    
    relationship_set = set()
    for table in sorted(important_tables):
        for fk_col, ref_table in foreign_keys.get(table, []):
            if ref_table in important_tables and table != ref_table:
                rel_key = (table, ref_table, fk_col)
                if rel_key not in relationship_set:
                    relationship_set.add(rel_key)
                    # Clean label
                    label = fk_col.replace('_id', '').replace('_c', '').replace('_', ' ').title()
                    lines.append(f"{ref_table},id,{table},{fk_col},One-to-Many,\"{label}\"")
    
    return "\n".join(lines)

def generate_detailed_markdown(tables, foreign_keys, important_tables):
    """Generate detailed markdown documentation."""
    lines = ["# Salesforce Schema ERD Documentation\n"]
    lines.append(f"**Total Tables Analyzed:** {len(tables)}")
    lines.append(f"**Tables in ERD:** {len(important_tables)}\n")
    
    lines.append("## Core Salesforce Objects\n")
    core_in_erd = sorted(CORE_OBJECTS & important_tables)
    for table in core_in_erd:
        lines.append(f"- `{table}`")
    
    lines.append("\n## Table Relationships\n")
    
    # Group by source table
    for table in sorted(important_tables):
        fks = foreign_keys.get(table, [])
        if fks:
            lines.append(f"### {table}")
            for fk_col, ref_table in sorted(fks):
                if ref_table in important_tables:
                    lines.append(f"- `{fk_col}` → `{ref_table}`")
            lines.append("")
    
    return "\n".join(lines)

def main():
    csv_path = Path(__file__).parent.parent / '_knowledge_base' / '66degrees_salesforce_schema.csv'
    
    print("Analyzing schema...")
    tables, columns_by_table, foreign_keys, table_has_id = analyze_schema(csv_path)
    
    print(f"Found {len(tables)} tables")
    print(f"Found {sum(len(fks) for fks in foreign_keys.values())} relationships")
    
    print("Identifying important tables...")
    important_tables = identify_important_tables(tables, foreign_keys)
    print(f"Selected {len(important_tables)} tables for ERD")
    
    # Generate outputs
    output_dir = Path(__file__).parent.parent / '_knowledge_base' / 'diagrams'
    output_dir.mkdir(exist_ok=True)
    
    # Mermaid ERD
    mermaid_content = generate_mermaid_erd(tables, foreign_keys, important_tables)
    mermaid_path = output_dir / 'salesforce_erd_mermaid.md'
    with open(mermaid_path, 'w') as f:
        f.write("```mermaid\n")
        f.write(mermaid_content)
        f.write("\n```\n")
    print(f"Generated Mermaid ERD: {mermaid_path}")
    
    # Lucidchart CSV
    csv_content = generate_lucidchart_csv(tables, foreign_keys, important_tables)
    csv_path_out = output_dir / 'salesforce_erd_lucidchart.csv'
    with open(csv_path_out, 'w') as f:
        f.write(csv_content)
    print(f"Generated Lucidchart CSV: {csv_path_out}")
    
    # Detailed markdown
    md_content = generate_detailed_markdown(tables, foreign_keys, important_tables)
    md_path = output_dir / 'salesforce_erd_detailed.md'
    with open(md_path, 'w') as f:
        f.write(md_content)
    print(f"Generated detailed documentation: {md_path}")
    
    print("\nDone!")

if __name__ == '__main__':
    main()