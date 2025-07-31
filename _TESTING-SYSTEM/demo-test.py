#!/usr/bin/env python3
"""
Demo script to show the AI Knowledge Testing System in action
"""

import sys
sys.path.append('.')

from question_generator import QuestionGenerator
from answer_evaluator import AnswerEvaluator

def main():
    print("🎯 AI-Powered Knowledge Testing System Demo")
    print("=" * 50)
    
    # Generate questions from 26-Bible folder
    print("\n1. Generating questions from 26-Bible folder...")
    generator = QuestionGenerator()
    questions = generator.generate_questions_from_folder("../26-Bible/", 3)
    
    print(f"✅ Generated {len(questions)} questions")
    
    # Show sample questions
    print("\n2. Sample Questions Generated:")
    for i, q in enumerate(questions, 1):
        print(f"\n   Question {i}: {q.question}")
        print(f"   Difficulty: {q.difficulty}")
        print(f"   Category: {q.category}")
        print(f"   Expected keywords: {', '.join(q.expected_keywords[:3])}")
    
    # Test evaluation system
    print("\n3. Testing Answer Evaluation System...")
    evaluator = AnswerEvaluator()
    
    # Use first question for demo
    if questions:
        question = questions[0]
        sample_answer = "The Holy Spirit helps believers understand Scripture through prayer and study."
        
        print(f"\n   Question: {question.question}")
        print(f"   Sample Answer: {sample_answer}")
        
        # Evaluate the answer
        result = evaluator.evaluate_answer(
            question.question,
            question.expected_answer,
            sample_answer,
            question.category,
            question.expected_keywords
        )
        
        print(f"\n   ✅ Evaluation Results:")
        print(f"   Score: {result.score:.1%}")
        print(f"   Method: {result.tier_used.value}")
        print(f"   Confidence: {result.confidence:.1%}")
        print(f"   Time: {result.evaluation_time:.2f}s")
        print(f"   Feedback: {result.feedback}")
        
        if result.improvement_suggestions:
            print(f"   Suggestions: {'; '.join(result.improvement_suggestions[:2])}")
    
    print(f"\n4. System Status:")
    stats = evaluator.get_evaluation_stats()
    print(f"   ✅ Local LLM Model: {stats['config']['evaluation']['local_llm_model']}")
    print(f"   ✅ API Available: {stats['api_available']}")
    print(f"   ✅ Question Types: {len(generator.questions)} total generated")
    
    print(f"\n🚀 System is ready! Use: python topic-tester.py ../26-Bible/ --questions 10")

if __name__ == "__main__":
    main()