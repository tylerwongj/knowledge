# c-AI-Tool-Integrations-APIs - Technical Implementation Guide

## 🎯 Learning Objectives
- Master API integrations for major AI/LLM services
- Build custom AI tool chains and automation scripts
- Understand rate limiting, cost optimization, and error handling
- Create seamless integrations between AI tools and existing workflows

---

## 🔧 Core API Integration Architecture

### Major AI Service APIs

#### OpenAI API Integration
```python
import openai
from typing import Dict, List, Optional

class OpenAIService:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        
    def chat_completion(self, messages: List[Dict], model: str = "gpt-4"):
        """Generate chat completion with error handling"""
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except openai.error.RateLimitError:
            # Implement exponential backoff
            time.sleep(60)
            return self.chat_completion(messages, model)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def function_calling(self, messages: List[Dict], functions: List[Dict]):
        """Use GPT function calling for structured outputs"""
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            functions=functions,
            function_call="auto"
        )
        return response
```

#### Anthropic Claude API
```python
import anthropic
from typing import List, Dict

class ClaudeService:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate_content(self, prompt: str, system: str = None):
        """Generate content with Claude"""
        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4000,
                system=system,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"Claude API Error: {str(e)}"
    
    def analyze_document(self, document: str, analysis_type: str):
        """Specialized document analysis"""
        system_prompt = f"You are an expert analyst focusing on {analysis_type}."
        prompt = f"Analyze this document:\n\n{document}\n\nProvide detailed insights."
        return self.generate_content(prompt, system_prompt)
```

### Integration Patterns

#### Multi-Model Workflow
```python
class AIWorkflowOrchestrator:
    def __init__(self, openai_key: str, claude_key: str):
        self.openai = OpenAIService(openai_key)
        self.claude = ClaudeService(claude_key)
    
    def comprehensive_analysis(self, content: str):
        """Use multiple models for comprehensive analysis"""
        # Step 1: Initial analysis with Claude
        claude_analysis = self.claude.analyze_document(
            content, "comprehensive review"
        )
        
        # Step 2: Follow-up questions with GPT-4
        followup_prompt = f"""
        Based on this analysis: {claude_analysis}
        
        Generate 5 follow-up questions that would provide deeper insights.
        """
        questions = self.openai.chat_completion([
            {"role": "user", "content": followup_prompt}
        ])
        
        # Step 3: Answer questions with Claude
        final_analysis = self.claude.generate_content(
            f"Answer these questions about the content:\n{questions}\n\nOriginal content:\n{content}"
        )
        
        return {
            "initial_analysis": claude_analysis,
            "questions": questions,
            "final_analysis": final_analysis
        }
```

---

## 🚀 AI/LLM Integration Opportunities

### Productivity Tool Integrations

#### Slack Bot Integration
```python
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse

class AISlackBot:
    def __init__(self, slack_token: str, ai_service):
        self.client = WebClient(token=slack_token)
        self.ai = ai_service
    
    def handle_message(self, event):
        """Process Slack messages with AI assistance"""
        if event.get("subtype") is None:
            text = event.get("text", "")
            
            if text.startswith("@ai"):
                # Extract the question
                question = text.replace("@ai", "").strip()
                
                # Get AI response
                response = self.ai.chat_completion([
                    {"role": "user", "content": question}
                ])
                
                # Send response back to Slack
                self.client.chat_postMessage(
                    channel=event["channel"],
                    text=response,
                    thread_ts=event.get("ts")
                )
```

#### Gmail API Integration
```python
import base64
import json
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

class GmailAIAssistant:
    def __init__(self, credentials, ai_service):
        self.service = build('gmail', 'v1', credentials=credentials)
        self.ai = ai_service
    
    def auto_classify_emails(self):
        """Automatically classify and respond to emails"""
        # Get unread emails
        results = self.service.users().messages().list(
            userId='me', q='is:unread'
        ).execute()
        
        messages = results.get('messages', [])
        
        for message in messages:
            # Get email content
            msg = self.service.users().messages().get(
                userId='me', id=message['id']
            ).execute()
            
            # Extract email text
            email_text = self.extract_email_content(msg)
            
            # Classify with AI
            classification = self.ai.chat_completion([
                {
                    "role": "system", 
                    "content": "Classify this email as: urgent, normal, spam, or promotional"
                },
                {"role": "user", "content": email_text}
            ])
            
            # Apply label based on classification
            self.apply_label(message['id'], classification)
    
    def generate_response_draft(self, email_content: str):
        """Generate appropriate email response"""
        prompt = f"""
        Generate a professional email response to:
        {email_content}
        
        Make it:
        - Polite and professional
        - Concise but complete
        - Actionable where appropriate
        """
        
        return self.ai.chat_completion([
            {"role": "user", "content": prompt}
        ])
```

### Development Tool Integrations

#### GitHub Integration
```python
import requests
from typing import List, Dict

class GitHubAIAssistant:
    def __init__(self, github_token: str, ai_service):
        self.token = github_token
        self.ai = ai_service
        self.headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def analyze_pull_request(self, repo: str, pr_number: int):
        """AI-powered pull request analysis"""
        # Get PR diff
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
        pr_data = requests.get(url, headers=self.headers).json()
        
        # Get diff content
        diff_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
        files = requests.get(diff_url, headers=self.headers).json()
        
        # Analyze with AI
        analysis_prompt = f"""
        Analyze this pull request for:
        - Code quality issues
        - Potential bugs
        - Security concerns
        - Performance implications
        
        PR Title: {pr_data['title']}
        Description: {pr_data['body']}
        
        Files changed: {len(files)}
        """
        
        for file in files[:5]:  # Limit to first 5 files
            analysis_prompt += f"\n\nFile: {file['filename']}\n"
            analysis_prompt += f"Changes: {file.get('patch', 'No patch available')}\n"
        
        return self.ai.chat_completion([
            {"role": "user", "content": analysis_prompt}
        ])
    
    def auto_generate_commit_messages(self, diff: str):
        """Generate conventional commit messages"""
        prompt = f"""
        Generate a conventional commit message for this diff:
        {diff}
        
        Format: type(scope): description
        Types: feat, fix, docs, style, refactor, test, chore
        """
        
        return self.ai.chat_completion([
            {"role": "user", "content": prompt}
        ])
```

---

## 💡 Key Highlights

### **Essential Integration Patterns**

#### 1. **Rate Limiting and Cost Management**
```python
import time
from functools import wraps

def rate_limit(calls_per_minute: int):
    """Decorator for API rate limiting"""
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

@rate_limit(calls_per_minute=10)
def expensive_ai_call(prompt):
    # Your AI API call here
    pass
```

#### 2. **Retry Logic with Exponential Backoff**
```python
import time
import random
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(delay)
            
        return wrapper
    return decorator
```

#### 3. **Token Usage Optimization**
```python
class TokenOptimizer:
    def __init__(self, max_tokens=4000):
        self.max_tokens = max_tokens
    
    def truncate_content(self, content: str, reserve_tokens=500):
        """Truncate content to fit within token limits"""
        # Rough estimation: 1 token ≈ 4 characters
        max_chars = (self.max_tokens - reserve_tokens) * 4
        
        if len(content) > max_chars:
            return content[:max_chars] + "... [truncated]"
        return content
    
    def chunk_content(self, content: str, chunk_size=3000):
        """Split large content into processable chunks"""
        chunks = []
        words = content.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) > chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
```

### **Production-Ready Integration Framework**

#### Configuration Management
```python
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class AIServiceConfig:
    openai_api_key: str
    claude_api_key: str
    max_retries: int = 3
    timeout: int = 30
    rate_limit: int = 60  # requests per minute
    
    @classmethod
    def from_env(cls):
        return cls(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            claude_api_key=os.getenv('CLAUDE_API_KEY'),
            max_retries=int(os.getenv('AI_MAX_RETRIES', 3)),
            timeout=int(os.getenv('AI_TIMEOUT', 30))
        )
```

#### Logging and Monitoring
```python
import logging
import time
from functools import wraps

def log_ai_calls(logger):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger.info(f"AI call started: {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"AI call completed: {func.__name__} ({duration:.2f}s)")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"AI call failed: {func.__name__} ({duration:.2f}s): {str(e)}")
                raise
                
        return wrapper
    return decorator
```

---

## 🔥 Quick Wins Implementation

### Immediate Integration Projects

#### 1. **Email Auto-Responder**
- Set up Gmail API integration
- Create AI-powered response generation
- Implement classification and routing

#### 2. **Slack Productivity Bot**  
- Deploy AI assistant for team questions
- Add meeting summary generation
- Implement task management helpers

#### 3. **Code Review Assistant**
- GitHub webhook integration
- Automated code analysis and feedback
- Pull request optimization suggestions

#### 4. **Document Processing Pipeline**
- PDF/Word document analysis
- Automated summarization and extraction
- Multi-format output generation

### Advanced Integration Examples

#### Business Intelligence Dashboard
```python
class AIBusinessIntelligence:
    def __init__(self, ai_service, data_sources):
        self.ai = ai_service
        self.data_sources = data_sources
    
    def generate_insights(self, timeframe="last_30_days"):
        # Collect data from various sources
        sales_data = self.data_sources['sales'].get_data(timeframe)
        user_data = self.data_sources['analytics'].get_data(timeframe)
        
        # AI analysis
        insights = self.ai.chat_completion([{
            "role": "user",
            "content": f"Analyze this business data and provide key insights:\nSales: {sales_data}\nUsers: {user_data}"
        }])
        
        return insights
```

---

## 🎯 Implementation Roadmap

### Week 1-2: Foundation
1. **Set up API accounts** for major AI services
2. **Create basic integration framework** with error handling
3. **Build simple proof-of-concept** integrations
4. **Test authentication and rate limiting**

### Week 3-4: Core Integrations
1. **Implement email automation** system
2. **Create Slack bot** for team productivity
3. **Set up GitHub integration** for code assistance
4. **Build document processing** pipeline

### Month 2: Advanced Features
1. **Multi-model orchestration** workflows
2. **Custom fine-tuning** for specific tasks
3. **Performance optimization** and monitoring
4. **Scaling infrastructure** for production use

### Security and Best Practices
- **Never hardcode API keys** - use environment variables
- **Implement proper authentication** and token refresh
- **Monitor API usage and costs** regularly
- **Add comprehensive error handling** and logging
- **Test integrations thoroughly** before production deployment