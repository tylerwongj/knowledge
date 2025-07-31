#!/usr/bin/env python3
"""Show the questions that will be generated for testing"""

from question_generator import QuestionGenerator

generator = QuestionGenerator()
questions = generator.generate_questions_from_folder("../26-Bible/", 5)

print("🎯 Sample Questions Generated:")
print("=" * 50)

for i, q in enumerate(questions, 1):
    print(f"\n{i}. Question: {q.question}")
    print(f"   Expected Answer: {q.expected_answer}")
    print(f"   Keywords: {', '.join(q.expected_keywords[:3])}")
    print(f"   Difficulty: {q.difficulty}")