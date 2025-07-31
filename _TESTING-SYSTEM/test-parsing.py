#!/usr/bin/env python3
"""Simple test to verify parsing is working correctly"""

from question_generator import QuestionGenerator

# Generate questions
generator = QuestionGenerator()
questions = generator.generate_questions_from_folder("../26-Bible/", 10)

print(f"Generated {len(questions)} questions:\n")

for i, q in enumerate(questions, 1):
    print(f"{i}. Question: {q.question}")
    print(f"   Expected Answer: {q.expected_answer}")
    print(f"   Keywords: {', '.join(q.expected_keywords)}")
    print(f"   Category: {q.category}")
    print()