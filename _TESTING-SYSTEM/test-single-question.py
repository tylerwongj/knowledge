#!/usr/bin/env python3
"""Test a single question to verify we get real definitions"""

from question_generator import QuestionGenerator
from answer_evaluator import AnswerEvaluator

# Generate questions
generator = QuestionGenerator()
questions = generator.generate_questions_from_folder("../26-Bible/", 3)

# Show the first question with its real expected answer
if questions:
    q = questions[0]
    print(f"Question: {q.question}")
    print(f"Expected Answer: {q.expected_answer}")
    print(f"Keywords: {q.expected_keywords}")
    print(f"Difficulty: {q.difficulty}")
    print(f"Type: {q.question_type}")
    
    # Test evaluation with a sample answer
    evaluator = AnswerEvaluator()
    sample_answer = "Scripture is without error in the original manuscripts"
    
    result = evaluator.evaluate_answer(
        q.question, q.expected_answer, sample_answer, 
        q.category, q.expected_keywords
    )
    
    print(f"\nSample Answer: {sample_answer}")
    print(f"Score: {result.score:.1%}")
    print(f"Feedback: {result.feedback}")
else:
    print("No questions generated")