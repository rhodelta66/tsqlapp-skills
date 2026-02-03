#!/usr/bin/env python3
"""
TSQL.APP URL Parser

Parses TSQL.APP URLs and outputs structured components for database queries.

Usage:
    python parse_url.py "https://domain/card?ord=123d&red=Filter&id=456"
    python parse_url.py "https://domain/parent/789/child?ord=123,456"
"""

import sys
import re
from urllib.parse import urlparse, parse_qs, unquote


def parse_tsqlapp_url(url: str) -> dict:
    """Parse a TSQL.APP URL into its components."""
    
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split('/') if p]
    query = parse_qs(parsed.query)
    
    result = {
        'domain': parsed.netloc,
        'card': None,
        'parent_id': None,
        'child_card': None,
        'sort_fields': [],
        'filter': None,
        'selected_id': None,
    }
    
    # Parse path: /card or /parent_card/parent_id/child_card
    if len(path_parts) >= 1:
        result['card'] = path_parts[0]
    
    if len(path_parts) == 3:
        # Child card context: /parent/id/child
        result['card'] = path_parts[0]  # parent card
        result['parent_id'] = int(path_parts[1])
        result['child_card'] = path_parts[2]
    
    # Parse ord parameter (sorting)
    if 'ord' in query:
        ord_value = query['ord'][0]
        for field in ord_value.split(','):
            field = field.strip()
            if field.endswith('d'):
                result['sort_fields'].append({
                    'field_id': int(field[:-1]),
                    'direction': 'DESC'
                })
            else:
                result['sort_fields'].append({
                    'field_id': int(field),
                    'direction': 'ASC'
                })
    
    # Parse red parameter (filter/reducer)
    if 'red' in query:
        result['filter'] = unquote(query['red'][0])
    
    # Parse id parameter (selected record)
    if 'id' in query:
        result['selected_id'] = int(query['id'][0])
    
    return result


def generate_queries(parsed: dict) -> list:
    """Generate SQL queries to look up the URL components."""
    
    queries = []
    
    # Card lookup
    card_name = parsed['child_card'] or parsed['card']
    if card_name:
        queries.append({
            'description': f"Get card '{card_name}'",
            'sql': f"SELECT id, name, tablename, basetable, reducer FROM api_card WHERE name = N'{card_name}'"
        })
    
    # Sort field lookups
    for sf in parsed['sort_fields']:
        queries.append({
            'description': f"Get sort field {sf['field_id']} ({sf['direction']})",
            'sql': f"SELECT id, name, card_id FROM api_card_fields WHERE id = {sf['field_id']}"
        })
    
    # Filter lookup (requires card_id)
    if parsed['filter']:
        queries.append({
            'description': f"Get filter '{parsed['filter']}'",
            'sql': f"SELECT id, name, sql FROM api_card_actions WHERE card_id = @card_id AND name = N'{parsed['filter']}' AND action = 'reducer'"
        })
    
    # Selected record (requires tablename)
    if parsed['selected_id']:
        queries.append({
            'description': f"Get selected record {parsed['selected_id']}",
            'sql': f"SELECT * FROM {{tablename}} WHERE id = {parsed['selected_id']}"
        })
    
    # Parent record (for child context)
    if parsed['parent_id']:
        queries.append({
            'description': f"Get parent record {parsed['parent_id']}",
            'sql': f"SELECT * FROM {{parent_tablename}} WHERE id = {parsed['parent_id']}"
        })
    
    return queries


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_url.py <url>")
        print("Example: python parse_url.py 'https://domain/incoming_invoice?ord=18377d&red=Draft+%2F+Empty&id=142338'")
        sys.exit(1)
    
    url = sys.argv[1]
    
    try:
        parsed = parse_tsqlapp_url(url)
        
        print("=" * 60)
        print("TSQL.APP URL PARSER")
        print("=" * 60)
        print(f"\nURL: {url}\n")
        
        print("PARSED COMPONENTS:")
        print("-" * 40)
        print(f"  Card:        {parsed['card']}")
        
        if parsed['child_card']:
            print(f"  Parent ID:   {parsed['parent_id']}")
            print(f"  Child Card:  {parsed['child_card']}")
        
        if parsed['sort_fields']:
            sort_str = ', '.join([f"{s['field_id']} {s['direction']}" for s in parsed['sort_fields']])
            print(f"  Sort:        {sort_str}")
        
        if parsed['filter']:
            print(f"  Filter:      {parsed['filter']}")
        
        if parsed['selected_id']:
            print(f"  Selected ID: {parsed['selected_id']}")
        
        print("\nSUGGESTED QUERIES:")
        print("-" * 40)
        
        queries = generate_queries(parsed)
        for i, q in enumerate(queries, 1):
            print(f"\n{i}. {q['description']}")
            print(f"   {q['sql']}")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"Error parsing URL: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
