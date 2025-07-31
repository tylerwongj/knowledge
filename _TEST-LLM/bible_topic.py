#!/usr/bin/env python3
"""Simple python script to ask ollama about bible topics"""

import ollama

def ask_bible_topic(topic):
    """Ask ollama about a specific bible topic"""
    try:
        stream = ollama.chat(
            model='llama3.2:3b',
            messages=[{
                'role': 'user', 
                'content': f'Tell me about {topic} from the Bible'
            }],
            stream=True
        )
        
        full_response = ""
        for chunk in stream:
            content = chunk['message']['content']
            print(content, end='', flush=True)
            full_response += content
        
        return full_response
        
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    topic = input("Enter a Bible topic: ")
    print(f"\n🔍 Asking about: {topic}\n")
    
    ask_bible_topic(topic)
    print("\n")  # Add newline at end