#!/usr/bin/env python3
"""Debug the scoring system"""

from question_generator import QuestionGenerator
from answer_evaluator import AnswerEvaluator

# Generate a sample question
generator = QuestionGenerator()
questions = generator.generate_questions_from_folder("../26-Bible/", 1)

if questions:
    q = questions[0]
    print(f"Question: {q.question}")
    print(f"Expected Answer: {q.expected_answer}")
    print(f"Keywords: {q.expected_keywords}")
    print()
    
    # Test different student answers
    test_answers = [
        "Scripture alone is the authority",  # Should score high
        "The Bible is our guide",           # Should score medium  
        "I don't know",                     # Should score low
        q.expected_answer[:50] + "..."      # Partial correct answer
    ]
    
    evaluator = AnswerEvaluator("config.yaml")
    
    for answer in test_answers:
        print(f"Testing answer: '{answer}'")
        
        # Test keyword scoring directly
        score, matches = evaluator._evaluate_keywords(answer, q.expected_keywords)
        print(f"  Keyword score: {score:.2%} (matches: {matches})")
        
        # Test full evaluation
        result = evaluator.evaluate_answer(q.question, q.expected_answer, answer, q.category, q.expected_keywords)
        print(f"  Final score: {result.score:.2%} via {result.tier_used.value}")
        print(f"  Feedback: {result.feedback}")
        print()