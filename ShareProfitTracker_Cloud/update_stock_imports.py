#!/usr/bin/env python3
"""Update stock imports in GUI files to use massive database"""

import os
import re

def update_file_imports(file_path):
    """Update imports in a Python file to use massive stock database"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Replace enhanced_stock_symbols imports with massive_stock_symbols
        patterns = [
            (r'from data\.enhanced_stock_symbols import ([^\n]+)',
             r'try:\n    from data.massive_stock_symbols import \1\n    print("Using massive stock database (1200+ stocks)")\nexcept ImportError:\n    from data.enhanced_stock_symbols import \1\n    print("Fallback to enhanced stock database")'),

            (r'from data\.stock_symbols import ([^\n]+)',
             r'try:\n    from data.massive_stock_symbols import \1\n    print("Using massive stock database (1200+ stocks)")\nexcept ImportError:\n    from data.stock_symbols import \1\n    print("Fallback to basic stock database")'),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        # Only write if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file_path}")
            return True
        else:
            print(f"No changes needed: {file_path}")
            return False

    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Update all GUI files to use massive stock database"""
    print("UPDATING GUI IMPORTS TO USE MASSIVE STOCK DATABASE")
    print("=" * 60)

    gui_files = [
        'gui/add_stock_dialog.py',
        'gui/autocomplete_entry.py',
        'gui/dividend_dialog.py',
        'gui/stock_adjustment_dialog.py'
    ]

    updated_count = 0

    for file_path in gui_files:
        if os.path.exists(file_path):
            if update_file_imports(file_path):
                updated_count += 1
        else:
            print(f"File not found: {file_path}")

    print(f"\nUpdated {updated_count} files to use massive stock database")
    print("The application will now have access to 1200+ stocks!")

if __name__ == "__main__":
    main()