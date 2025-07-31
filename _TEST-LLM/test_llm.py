#!/usr/bin/env python3
"""Super simple LLM test to see if ollama is working properly"""

import ollama

def test_basic_chat():
    """Test basic ollama chat functionality"""
    print("🧪 Testing Basic Ollama Chat...")
    
    try:
        response = ollama.chat(
            model='llama3.2:1b',
            messages=[{
                'role': 'user', 
                'content': 'Say hello in exactly 3 words.'
            }]
        )
        
        print(f"✅ Response: {response['message']['content']}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_scoring():
    """Test if LLM can follow scoring format"""
    print("\n🎯 Testing Scoring Format...")
    
    try:
        response = ollama.chat(
            model='llama3.2:1b',
            messages=[{
                'role': 'user',
                'content': '''Rate this answer from 0.0 to 1.0:

Question: What is 2+2?
Expected: 4
Student Answer: 4

Respond in this format:
SCORE: [0.0-1.0]
FEEDBACK: [brief feedback]'''
            }]
        )
        
        content = response['message']['content']
        print(f"✅ LLM Response:\n{content}")
        
        # Try to parse score
        import re
        score_match = re.search(r'SCORE:\s*(\d*\.?\d+)', content, re.IGNORECASE)
        if score_match:
            score = float(score_match.group(1))
            print(f"✅ Parsed Score: {score}")
        else:
            print("❌ Could not parse score from response")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_bad_answer():
    """Test scoring for obviously wrong answer"""
    print("\n🚫 Testing Bad Answer Scoring...")
    
    try:
        response = ollama.chat(
            model='llama3.2:1b',
            messages=[{
                'role': 'user',
                'content': '''Rate this answer from 0.0 to 1.0:

Question: What is the capital of France?
Expected: Paris
Student Answer: I don't know

Respond in this format:
SCORE: [0.0-1.0]
FEEDBACK: [brief feedback]'''
            }]
        )
        
        content = response['message']['content']
        print(f"Response:\n{content}")
        
        import re
        score_match = re.search(r'SCORE:\s*(\d*\.?\d+)', content, re.IGNORECASE)
        if score_match:
            score = float(score_match.group(1))
            print(f"Score for 'I don't know': {score}")
            if score > 0.3:
                print("⚠️  WARNING: Score too high for wrong answer!")
            else:
                print("✅ Score appropriately low")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Local LLM (llama3.2:1b)\n")
    
    # Run tests
    test_basic_chat()
    test_scoring() 
    test_bad_answer()
    
    print("\n🏁 Test Complete!")