#!/usr/bin/env python3
"""
Question Generator for Knowledge Testing System

Parses TERMS.md files and generates questions for knowledge testing.
Supports multiple question types and difficulty levels.
"""

import os
import re
import yaml
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import random


@dataclass
class Question:
    """Represents a knowledge testing question."""
    question: str
    expected_keywords: List[str]
    expected_answer: str
    difficulty: str  # 'easy', 'medium', 'hard'
    category: str
    source_file: str
    question_type: str  # 'definition', 'comparison', 'application', 'biblical_support'


class QuestionGenerator:
    """Generates questions from TERMS.md files and other knowledge content."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.questions: List[Question] = []
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration or use defaults."""
        default_config = {
            'question_types': {
                'definition': 0.4,
                'comparison': 0.2,
                'application': 0.2,
                'biblical_support': 0.2
            },
            'difficulty_distribution': {
                'easy': 0.5,
                'medium': 0.3,
                'hard': 0.2
            },
            'keywords_per_question': 3
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config
    
    def generate_questions_from_folder(self, folder_path: str, num_questions: int = 10) -> List[Question]:
        """Generate questions from a knowledge folder."""
        folder_path = Path(folder_path)
        
        # Look for TERMS.md file first
        terms_file = folder_path / "TERMS.md"
        if terms_file.exists():
            self._parse_terms_file(str(terms_file))
        
        # Parse other .md files for additional context
        for md_file in folder_path.glob("*.md"):
            if md_file.name not in ["TERMS.md", "README.md", "TODOS.md"]:
                self._parse_content_file(str(md_file))
        
        # Select and return requested number of questions
        return self._select_questions(num_questions)
    
    def _parse_terms_file(self, file_path: str):
        """Parse TERMS.md file to extract definitions and generate questions."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract term definitions using regex patterns
            self._extract_definitions(content, file_path)
            self._extract_comparisons(content, file_path)
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
    
    def _extract_definitions(self, content: str, source_file: str):
        """Extract definition-based questions from TERMS.md content."""
        # Split content into sections by ### headers
        sections = re.split(r'\n###\s+\*\*([^*]+)\*\*', content)
        
        # Process each section (skip first empty section)
        for i in range(1, len(sections), 2):
            if i + 1 >= len(sections):
                break
                
            term = sections[i].strip()
            section_content = sections[i + 1].strip()
            
            # Extract the first meaningful definition from this section
            definition = self._extract_first_definition(section_content)
            
            if definition and len(definition) > 15:
                # Clean up definition
                definition = re.sub(r'\s+', ' ', definition).strip()
                
                # Generate definition question
                question = Question(
                    question=f"What is {term}?",
                    expected_keywords=self._extract_keywords(definition),
                    expected_answer=definition,
                    difficulty=self._assign_difficulty(term, definition),
                    category=self._determine_category(source_file),
                    source_file=source_file,
                    question_type="definition"
                )
                self.questions.append(question)
                
                # Generate explanation question for complex terms
                if len(definition) > 50:
                    explain_question = Question(
                        question=f"Explain {term} and its significance in Reformed theology.",
                        expected_keywords=self._extract_keywords(definition),
                        expected_answer=definition,
                        difficulty=self._escalate_difficulty(self._assign_difficulty(term, definition)),
                        category=self._determine_category(source_file),
                        source_file=source_file,
                        question_type="application"
                    )
                    self.questions.append(explain_question)
        
        # Handle comparison terms like "Exegesis vs. Eisegesis"
        self._extract_vs_comparisons(content, source_file)
    
    def _extract_first_definition(self, section_content: str) -> str:
        """Extract the first meaningful definition from a section."""
        # For theologians/people, combine multiple fields for complete definition
        if self._is_person_entry(section_content):
            return self._extract_person_definition(section_content)
        
        # Try different patterns for regular definitions
        patterns = [
            r'\*\*Definition\*\*:\s*([^\n]+(?:\n[^*\n]+)*)',  # **Definition**: content
            r'\*\*([^*]+)\*\*:\s*([^\n]+)',  # **Any Field**: content (take first one)
            r'^([^*\n]+)(?:\n|$)',  # First line if no bold formatting
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, section_content, re.MULTILINE)
            if matches:
                # For pattern with two groups, take the second (the definition)
                if isinstance(matches[0], tuple) and len(matches[0]) == 2:
                    return matches[0][1].strip()
                # For single group, take it
                elif isinstance(matches[0], str):
                    return matches[0].strip()
        
        return ""
    
    def _is_person_entry(self, section_content: str) -> bool:
        """Check if this is a person/theologian entry."""
        person_indicators = ['Ministry', 'Major Work', 'Contribution', 'Key Works', 'Emphasis', 'Born', 'Death']
        return any(indicator in section_content for indicator in person_indicators)
    
    def _extract_person_definition(self, section_content: str) -> str:
        """Extract a comprehensive definition for a person."""
        # Extract key fields for people
        fields = re.findall(r'\*\*([^*]+)\*\*:\s*([^\n]+)', section_content)
        
        # Build a comprehensive definition
        parts = []
        for field_name, field_value in fields[:3]:  # Take first 3 fields
            if field_name.lower() in ['ministry', 'major work', 'contribution', 'emphasis', 'key doctrine']:
                parts.append(f"{field_name}: {field_value}")
        
        if parts:
            return " | ".join(parts)
        else:
            # Fallback to first field
            return fields[0][1] if fields else ""
    
    def _extract_vs_comparisons(self, content: str, source_file: str):
        """Extract comparison terms like 'Exegesis vs. Eisegesis'."""
        # Find sections with "vs" in the title
        vs_pattern = r'###\s+\*\*([^*]+vs[^*]+)\*\*\s*\n((?:[^#]+(?:\n|$))*)'
        vs_matches = re.findall(vs_pattern, content, re.MULTILINE | re.IGNORECASE)
        
        for comparison_title, section_content in vs_matches:
            comparison_title = comparison_title.strip()
            
            # Extract the two terms and their definitions
            term_patterns = [
                r'\*\*([^*]+)\*\*:\s*([^\n]+)',  # **Term**: definition
            ]
            
            definitions = []
            for pattern in term_patterns:
                matches = re.findall(pattern, section_content)
                definitions.extend(matches)
            
            if len(definitions) >= 2:
                term1, def1 = definitions[0]
                term2, def2 = definitions[1]
                
                full_definition = f"{term1.strip()}: {def1.strip()} | {term2.strip()}: {def2.strip()}"
                
                question = Question(
                    question=f"Compare and contrast {term1.strip().lower()} and {term2.strip().lower()}.",
                    expected_keywords=[term1.strip().lower(), term2.strip().lower(), 'difference', 'contrast'],
                    expected_answer=full_definition,
                    difficulty="medium",
                    category=self._determine_category(source_file),
                    source_file=source_file,
                    question_type="comparison"
                )
                self.questions.append(question)
    
    def _extract_comparisons(self, content: str, source_file: str):
        """Extract comparison-based questions from content."""
        # Look for vs. patterns
        vs_pattern = r'###\s+\*\*([^*]+vs[^*]+)\*\*'
        vs_matches = re.findall(vs_pattern, content, re.IGNORECASE)
        
        for comparison in vs_matches:
            comparison = comparison.strip()
            terms = [term.strip() for term in comparison.lower().replace(' vs. ', ' vs ').split(' vs ')]
            
            if len(terms) == 2:
                question = Question(
                    question=f"Compare and contrast {terms[0]} and {terms[1]}.",
                    expected_keywords=terms + ['difference', 'contrast', 'compare'],
                    expected_answer=f"Comparison between {terms[0]} and {terms[1]}",
                    difficulty="medium",
                    category=self._determine_category(source_file),
                    source_file=source_file,
                    question_type="comparison"
                )
                self.questions.append(question)
    
    def _parse_content_file(self, file_path: str):
        """Parse general content files for additional question material."""
        # Skip content files if we have TERMS.md - focus on quality over quantity
        if file_path.endswith('TERMS.md'):
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Only extract from files with substantial content definitions
            # Look for definition patterns like "**Definition**:" or clear explanations
            definition_patterns = [
                r'(?:Definition|Meaning|Explanation):\s*([^\n]+(?:\n[^\n#]+)*)',
                r'\*\*([^*]+)\*\*[:\-]\s*([^\n]+(?:\n[^\n#]+)*)'
            ]
            
            for pattern in definition_patterns:
                matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
                for match in matches[:2]:  # Limit to 2 per file
                    if isinstance(match, tuple) and len(match) == 2:
                        term, definition = match
                        if len(definition.strip()) > 30:  # Only substantial definitions
                            question = Question(
                                question=f"What is {term.strip()}?",
                                expected_keywords=self._extract_keywords(definition),
                                expected_answer=definition.strip(),
                                difficulty="medium",
                                category=self._determine_category(file_path),
                                source_file=file_path,
                                question_type="definition"
                            )
                            self.questions.append(question)
                    
        except Exception as e:
            print(f"Error parsing content file {file_path}: {e}")
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        # Remove common words and extract meaningful terms
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'cannot', 'a', 'an'}
        
        # Extract words, filter stop words, and return top keywords
        words = re.findall(r'\b[A-Za-z]{3,}\b', text.lower())
        keywords = [word for word in words if word not in stop_words]
        
        # Return unique keywords, prioritizing longer ones
        unique_keywords = list(set(keywords))
        unique_keywords.sort(key=len, reverse=True)
        
        return unique_keywords[:self.config['keywords_per_question']]
    
    def _assign_difficulty(self, term: str, definition: str) -> str:
        """Assign difficulty based on term complexity."""
        # Simple heuristics for difficulty assignment
        if len(definition) < 50:
            return "easy"
        elif len(definition) < 150 or len(term.split()) > 2:
            return "medium"
        else:
            return "hard"
    
    def _escalate_difficulty(self, current_difficulty: str) -> str:
        """Escalate difficulty level."""
        escalation = {"easy": "medium", "medium": "hard", "hard": "hard"}
        return escalation.get(current_difficulty, "medium")
    
    def _determine_category(self, file_path: str) -> str:
        """Determine question category based on file path."""
        path_lower = file_path.lower()
        
        if 'bible' in path_lower or 'theology' in path_lower:
            return 'Reformed Theology'
        elif 'unity' in path_lower:
            return 'Unity Development'
        elif 'csharp' in path_lower or 'c#' in path_lower:
            return 'C# Programming'
        elif 'ai' in path_lower or 'llm' in path_lower:
            return 'AI/LLM Automation'
        elif 'soft-skill' in path_lower:
            return 'Professional Skills'
        else:
            return 'General Knowledge'
    
    def _select_questions(self, num_questions: int) -> List[Question]:
        """Select diverse questions based on configuration."""
        if not self.questions:
            return []
        
        # Shuffle questions and select diverse set
        random.shuffle(self.questions)
        
        selected = []
        question_types_seen = set()
        difficulties_seen = set()
        
        # First pass: prioritize diversity
        for question in self.questions:
            if len(selected) >= num_questions:
                break
            
            # Prefer questions that add diversity
            adds_type_diversity = question.question_type not in question_types_seen
            adds_difficulty_diversity = question.difficulty not in difficulties_seen
            
            if adds_type_diversity or adds_difficulty_diversity or len(selected) < num_questions // 2:
                selected.append(question)
                question_types_seen.add(question.question_type)
                difficulties_seen.add(question.difficulty)
        
        # Second pass: fill remaining slots
        remaining_questions = [q for q in self.questions if q not in selected]
        while len(selected) < num_questions and remaining_questions:
            selected.append(remaining_questions.pop(0))
        
        return selected[:num_questions]
    
    def export_questions(self, questions: List[Question], output_format: str = 'yaml') -> str:
        """Export questions to specified format."""
        if output_format == 'yaml':
            question_data = []
            for q in questions:
                question_data.append({
                    'question': q.question,
                    'expected_keywords': q.expected_keywords,
                    'expected_answer': q.expected_answer,
                    'difficulty': q.difficulty,
                    'category': q.category,
                    'source_file': q.source_file,
                    'question_type': q.question_type
                })
            return yaml.dump(question_data, default_flow_style=False)
        
        elif output_format == 'json':
            import json
            question_data = [q.__dict__ for q in questions]
            return json.dumps(question_data, indent=2)
        
        else:  # text format
            output = []
            for i, q in enumerate(questions, 1):
                output.append(f"Question {i}: {q.question}")
                output.append(f"Difficulty: {q.difficulty}")
                output.append(f"Category: {q.category}")
                output.append(f"Expected Keywords: {', '.join(q.expected_keywords)}")
                output.append("")
            return "\n".join(output)


def main():
    """Main function for testing the question generator."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python question-generator.py <folder_path> [num_questions]")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    num_questions = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    generator = QuestionGenerator()
    questions = generator.generate_questions_from_folder(folder_path, num_questions)
    
    print(f"Generated {len(questions)} questions from {folder_path}")
    print("\n" + generator.export_questions(questions, 'text'))


if __name__ == "__main__":
    main()