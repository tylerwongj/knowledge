#!/usr/bin/env python3
"""Test specific theologian parsing"""

from question_generator import QuestionGenerator
import re

# Read the TERMS.md file and check parsing
with open("../26-Bible/TERMS.md", "r") as f:
    content = f.read()

generator = QuestionGenerator()

# Split content into sections like the parser does
sections = re.split(r'\n###\s+\*\*([^*]+)\*\*', content)

print("Found these theologian sections:")
for i in range(1, len(sections), 2):
    if i + 1 >= len(sections):
        break
        
    term = sections[i].strip()
    section_content = sections[i + 1].strip()
    
    # Check if this looks like a theologian
    if any(name in term.lower() for name in ['calvin', 'macarthur', 'piper', 'sproul']):
        print(f"\n=== {term} ===")
        print(f"Section content preview: {section_content[:200]}...")
        
        # Test the definition extraction
        definition = generator._extract_first_definition(section_content)
        print(f"Extracted definition: {definition}")