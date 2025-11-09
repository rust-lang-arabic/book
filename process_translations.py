#!/usr/bin/env python3
"""
Process markdown files to remove duplicate English translations within paragraphs.
For each Arabic term with English translation in parentheses, keep only the first
occurrence within each paragraph.
"""

import re
import os
from pathlib import Path

def process_paragraph(paragraph):
    """
    Process a single paragraph to remove duplicate English translations.
    Keep only the first occurrence of each English translation.
    """
    if not paragraph.strip():
        return paragraph

    # Dictionary to track which English translations have been used in this paragraph
    seen_translations = {}

    # Pattern to match Arabic term followed by English in parentheses
    # This matches: word(s) followed by space and (English text)
    pattern = r'(\S+(?:\s+\S+)*?)\s*\(([^)]+)\)'

    def replace_match(match):
        arabic_term = match.group(1).strip()
        english_translation = match.group(2).strip()
        full_match = match.group(0)

        # Create a key for tracking (using the English translation)
        key = english_translation.lower()

        # If we've already seen this English translation in this paragraph
        if key in seen_translations:
            # Remove the English translation, keep only the Arabic term
            return arabic_term
        else:
            # First occurrence - keep it and record it
            seen_translations[key] = True
            return full_match

    # Process the paragraph
    result = re.sub(pattern, replace_match, paragraph)
    return result

def process_file(file_path):
    """
    Process a single markdown file.
    Split into paragraphs, process each, and write back.
    """
    print(f"Processing: {file_path}")

    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into paragraphs (separated by one or more blank lines)
    # We need to preserve the structure, so we'll split carefully
    paragraphs = re.split(r'(\n\s*\n)', content)

    # Process each paragraph
    processed = []
    for i, para in enumerate(paragraphs):
        if para.strip():  # If it's not just whitespace
            if re.match(r'^\s*\n+\s*$', para):
                # This is separator whitespace, keep as-is
                processed.append(para)
            else:
                # This is actual content, process it
                processed.append(process_paragraph(para))
        else:
            processed.append(para)

    # Join back together
    result = ''.join(processed)

    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"  ✓ Completed: {file_path}")

def main():
    """Process all markdown files in the src directory."""
    src_dir = Path('/home/user/book/src')

    if not src_dir.exists():
        print(f"Error: {src_dir} does not exist")
        return

    # Find all .md files
    md_files = sorted(src_dir.glob('**/*.md'))

    if not md_files:
        print("No markdown files found")
        return

    print(f"Found {len(md_files)} markdown files to process\n")

    # Process each file
    for md_file in md_files:
        process_file(md_file)

    print(f"\n✓ Successfully processed {len(md_files)} files")

if __name__ == '__main__':
    main()
