#!/usr/bin/env python3
"""
Answer Evaluator for Knowledge Testing System

Provides hybrid evaluation using:
1. Keyword matching (fast, free)
2. Local LLM via Ollama (semantic understanding, free)
3. OpenAI API (complex theological/technical nuances, paid)
"""

import os
import re
import time
import yaml
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import ollama
import openai
from pathlib import Path


class EvaluationTier(Enum):
    """Evaluation tiers in order of complexity/cost."""
    KEYWORD = "keyword"
    LOCAL_LLM = "local_llm"
    API_LLM = "api_llm"


@dataclass
class EvaluationResult:
    """Result of answer evaluation."""
    score: float  # 0.0 to 1.0
    feedback: str
    tier_used: EvaluationTier
    confidence: float  # 0.0 to 1.0
    evaluation_time: float
    keyword_matches: List[str]
    improvement_suggestions: List[str]


class AnswerEvaluator:
    """Hybrid answer evaluation system."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.openai_client = None
        self._setup_openai()
        self._load_prompts()
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration with fallback defaults."""
        default_config = {
            'evaluation': {
                'keyword_threshold': 0.6,  # If keyword score >= this, skip LLM
                'local_llm_model': 'mixtral:8x7b',
                'openai_model': 'gpt-4o-mini',
                'max_local_llm_time': 30,  # seconds
                'use_api_fallback': True
            },
            'scoring': {
                'keyword_weight': 0.3,
                'semantic_weight': 0.7,
                'minimum_passing_score': 0.6
            },
            'prompts_dir': 'prompts'
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                # Deep merge
                for key, value in user_config.items():
                    if key in default_config and isinstance(value, dict):
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
        
        return default_config
    
    def _setup_openai(self):
        """Setup OpenAI client if API key is available."""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            openai.api_key = api_key
            self.openai_client = openai.OpenAI(api_key=api_key)
        else:
            print("Warning: No OpenAI API key found. API fallback disabled.")
            self.config['evaluation']['use_api_fallback'] = False
    
    def _load_prompts(self):
        """Load subject-specific evaluation prompts."""
        prompts_dir = Path(self.config['prompts_dir'])
        self.prompts = {
            'default': """
Evaluate this answer for accuracy and completeness.

Question: {question}
Expected Answer: {expected_answer}
Student Answer: {student_answer}

Score from 0.0 to 1.0 and provide constructive feedback.
Focus on accuracy, completeness, and understanding.
""",
            'theology': """
Evaluate this Reformed theology answer for doctrinal accuracy.

Question: {question}
Expected Answer: {expected_answer}
Student Answer: {student_answer}

Evaluate based on:
1. Biblical accuracy and proper Scripture usage
2. Alignment with Reformed confessions (Westminster, etc.)
3. Theological precision and clarity
4. Understanding of Reformed distinctives

Score from 0.0 to 1.0. Be generous with partial credit for biblical concepts even if terminology differs.
""",
            'technical': """
Evaluate this technical answer for accuracy and practical understanding.

Question: {question}
Expected Answer: {expected_answer}
Student Answer: {student_answer}

Evaluate based on:
1. Technical accuracy and correctness
2. Practical application understanding
3. Use of appropriate terminology
4. Completeness of explanation

Score from 0.0 to 1.0. Credit practical understanding even if exact wording differs.
"""
        }
        
        # Load custom prompts if they exist
        if prompts_dir.exists():
            for prompt_file in prompts_dir.glob('*.txt'):
                category = prompt_file.stem
                with open(prompt_file, 'r') as f:
                    self.prompts[category] = f.read().strip()
    
    def evaluate_answer(self, question: str, expected_answer: str, student_answer: str, 
                       category: str = "General Knowledge", expected_keywords: List[str] = None) -> EvaluationResult:
        """Main evaluation function using hybrid approach."""
        start_time = time.time()
        
        # Tier 1: Keyword matching
        keyword_score, keyword_matches = self._evaluate_keywords(student_answer, expected_keywords or [])
        
        # If keyword score is high enough, use it (but cap at reasonable level)
        if keyword_score >= self.config['evaluation']['keyword_threshold']:
            # Don't give perfect scores just for keywords
            adjusted_score = min(keyword_score * 0.85, 0.9)  # Cap keyword-only scores at 90%
            return EvaluationResult(
                score=adjusted_score,
                feedback=f"Good keyword coverage. Matched: {', '.join(keyword_matches)}",
                tier_used=EvaluationTier.KEYWORD,
                confidence=0.7,
                evaluation_time=time.time() - start_time,
                keyword_matches=keyword_matches,
                improvement_suggestions=self._suggest_improvements(student_answer, expected_answer)
            )
        
        # Tier 2: Local LLM evaluation (disabled - unreliable scoring)
        # try:
        #     local_result = self._evaluate_with_local_llm(question, expected_answer, student_answer, category)
        #     if local_result:
        #         return local_result
        # except Exception as e:
        #     print(f"Local LLM evaluation failed: {e}")
        
        # Tier 3: API LLM evaluation (fallback)
        if self.config['evaluation']['use_api_fallback'] and self.openai_client:
            try:
                api_result = self._evaluate_with_api(question, expected_answer, student_answer, category)
                if api_result:
                    return api_result
            except Exception as e:
                print(f"API evaluation failed: {e}")
        
        # Fallback to basic keyword evaluation
        return EvaluationResult(
            score=keyword_score,
            feedback=f"Basic evaluation - matched {len(keyword_matches)} keywords: {', '.join(keyword_matches)}",
            tier_used=EvaluationTier.KEYWORD,
            confidence=0.5,
            evaluation_time=time.time() - start_time,
            keyword_matches=keyword_matches,
            improvement_suggestions=["Consider expanding your answer with more detail."]
        )
    
    def _evaluate_keywords(self, student_answer: str, expected_keywords: List[str]) -> Tuple[float, List[str]]:
        """Evaluate answer based on keyword matching with intelligent scoring."""
        if not expected_keywords:
            return 0.5, []
        
        # Handle empty/very short answers
        if len(student_answer.strip()) < 5:
            return 0.1, []
        
        # Check for obviously wrong answers
        if student_answer.lower().strip() in ["i don't know", "don't know", "no idea", "not sure", "idk"]:
            return 0.1, []
        
        student_words = set(re.findall(r'\b\w+\b', student_answer.lower()))
        
        matches = []
        for keyword in expected_keywords:
            keyword_lower = keyword.lower()
            # Exact match or substring match
            if keyword_lower in student_words or any(keyword_lower in word for word in student_words):
                matches.append(keyword)
        
        # Calculate base score
        base_score = len(matches) / len(expected_keywords) if expected_keywords else 0.0
        
        # Apply intelligent scoring adjustments
        if base_score == 0:
            # Check for semantic similarity with simple heuristics
            if any(self._is_semantically_related(student_answer.lower(), kw.lower()) for kw in expected_keywords):
                return 0.3, []  # Some credit for related concepts
            else:
                return 0.1, []  # Very low score for no matches
        elif base_score < 0.3:
            return base_score * 0.6, matches  # Reduce score for poor keyword coverage
        elif base_score >= 0.8:
            return min(base_score * 0.85, 0.85), matches  # Cap keyword-only scores
        else:
            return base_score * 0.75, matches  # Moderate adjustment
    
    def _is_semantically_related(self, answer: str, keyword: str) -> bool:
        """Simple semantic relationship detection."""
        # Add simple synonym/related word detection
        related_terms = {
            'scripture': ['bible', 'word', 'biblical'],
            'god': ['lord', 'divine', 'holy'],
            'church': ['congregation', 'assembly', 'fellowship'],
            'prayer': ['worship', 'devotion', 'communion'],
            'salvation': ['redemption', 'saved', 'grace'],
            'faith': ['belief', 'trust', 'confidence']
        }
        
        if keyword in related_terms:
            return any(term in answer for term in related_terms[keyword])
        
        # Check if any related terms point back to this keyword
        for main_term, synonyms in related_terms.items():
            if keyword in synonyms and main_term in answer:
                return True
        
        return False
    
    def _evaluate_with_local_llm(self, question: str, expected_answer: str, 
                                student_answer: str, category: str) -> Optional[EvaluationResult]:
        """Evaluate using local Ollama LLM."""
        start_time = time.time()
        
        # Determine prompt based on category
        prompt_key = 'default'
        if 'theology' in category.lower() or 'bible' in category.lower():
            prompt_key = 'theology'
        elif any(tech in category.lower() for tech in ['unity', 'c#', 'programming', 'technical']):
            prompt_key = 'technical'
        
        prompt = self.prompts[prompt_key].format(
            question=question,
            expected_answer=expected_answer,
            student_answer=student_answer
        )
        
        try:
            response = ollama.chat(
                model=self.config['evaluation']['local_llm_model'],
                messages=[{
                    'role': 'user',
                    'content': prompt + "\n\nProvide your response in this format:\nSCORE: [0.0-1.0]\nFEEDBACK: [your feedback]"
                }]
            )
            
            evaluation_time = time.time() - start_time
            
            # Parse response
            content = response['message']['content']
            score, feedback = self._parse_llm_response(content)
            
            return EvaluationResult(
                score=score,
                feedback=feedback,
                tier_used=EvaluationTier.LOCAL_LLM,
                confidence=0.85,
                evaluation_time=evaluation_time,
                keyword_matches=[],  # Not applicable for LLM evaluation
                improvement_suggestions=self._extract_suggestions_from_feedback(feedback)
            )
            
        except Exception as e:
            print(f"Local LLM error: {e}")
            return None
    
    def _evaluate_with_api(self, question: str, expected_answer: str, 
                          student_answer: str, category: str) -> Optional[EvaluationResult]:
        """Evaluate using OpenAI API."""
        start_time = time.time()
        
        # Determine prompt based on category  
        prompt_key = 'default'
        if 'theology' in category.lower() or 'bible' in category.lower():
            prompt_key = 'theology'
        elif any(tech in category.lower() for tech in ['unity', 'c#', 'programming', 'technical']):
            prompt_key = 'technical'
        
        prompt = self.prompts[prompt_key].format(
            question=question,
            expected_answer=expected_answer,
            student_answer=student_answer
        )
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config['evaluation']['openai_model'],
                messages=[{
                    'role': 'user',
                    'content': prompt + "\n\nProvide your response in this format:\nSCORE: [0.0-1.0]\nFEEDBACK: [your feedback]"
                }],
                max_tokens=500,
                temperature=0.1  # Low temperature for consistent evaluation
            )
            
            evaluation_time = time.time() - start_time
            
            # Parse response
            content = response.choices[0].message.content
            score, feedback = self._parse_llm_response(content)
            
            return EvaluationResult(
                score=score,
                feedback=feedback,
                tier_used=EvaluationTier.API_LLM,
                confidence=0.95,
                evaluation_time=evaluation_time,
                keyword_matches=[],
                improvement_suggestions=self._extract_suggestions_from_feedback(feedback)
            )
            
        except Exception as e:
            print(f"API LLM error: {e}")
            return None
    
    def _parse_llm_response(self, content: str) -> Tuple[float, str]:
        """Parse LLM response to extract score and feedback."""
        # Look for score pattern
        score_match = re.search(r'SCORE:\s*(\d*\.?\d+)', content, re.IGNORECASE)
        feedback_match = re.search(r'FEEDBACK:\s*(.+)', content, re.IGNORECASE | re.DOTALL)
        
        if score_match:
            try:
                score = float(score_match.group(1))
                # Ensure score is in valid range
                score = max(0.0, min(1.0, score))
            except ValueError:
                score = 0.3  # Low score for invalid parsing
        else:
            # If no score found, try to infer from content
            content_lower = content.lower()
            if any(bad_word in content_lower for bad_word in ['incorrect', 'wrong', 'poor', "don't know", 'unclear']):
                score = 0.2
            elif any(ok_word in content_lower for ok_word in ['partially', 'somewhat', 'basic']):
                score = 0.5
            elif any(good_word in content_lower for good_word in ['good', 'correct', 'accurate', 'excellent']):
                score = 0.8
            else:
                score = 0.4  # Default middle-low score
        
        feedback = feedback_match.group(1).strip() if feedback_match else content.strip()
        
        # Cap LLM scores at reasonable levels for quality control
        if score > 0.95:
            score = 0.95  # Very rarely give perfect scores
        
        return score, feedback
    
    def _suggest_improvements(self, student_answer: str, expected_answer: str) -> List[str]:
        """Generate improvement suggestions based on answer comparison."""
        suggestions = []
        
        if len(student_answer.strip()) < 20:
            suggestions.append("Provide more detailed explanation")
        
        if len(expected_answer) > len(student_answer) * 2:
            suggestions.append("Consider expanding your answer to cover more key points")
        
        # Check for common theological terms if this seems like a theology question
        theology_terms = ['Scripture', 'biblical', 'Reformed', 'covenant', 'grace', 'salvation']
        if any(term in expected_answer for term in theology_terms):
            if not any(term.lower() in student_answer.lower() for term in theology_terms):
                suggestions.append("Include more biblical/theological terminology")
        
        return suggestions or ["Consider reviewing the source material for additional insights"]
    
    def _extract_suggestions_from_feedback(self, feedback: str) -> List[str]:
        """Extract actionable suggestions from LLM feedback."""
        # Simple extraction - look for sentences with suggestion keywords
        suggestion_keywords = ['should', 'could', 'consider', 'try', 'recommend', 'suggest']
        sentences = feedback.split('.')
        
        suggestions = []
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in suggestion_keywords):
                suggestions.append(sentence.strip())
        
        return suggestions[:3]  # Limit to top 3 suggestions
    
    def get_evaluation_stats(self) -> Dict:
        """Get statistics about evaluation performance (for debugging/optimization)."""
        return {
            'config': self.config,
            'api_available': self.openai_client is not None,
            'local_model': self.config['evaluation']['local_llm_model']
        }


def main():
    """Test the answer evaluator."""
    evaluator = AnswerEvaluator()
    
    # Test question
    question = "What is Sola Scriptura?"
    expected_answer = "Scripture Alone - The Bible is the only infallible rule of faith and practice"
    student_answer = "Sola Scriptura means that the Bible is our only authority for faith and practice, not church tradition"
    expected_keywords = ["Scripture", "Bible", "authority", "faith", "practice"]
    
    result = evaluator.evaluate_answer(question, expected_answer, student_answer, 
                                     "Reformed Theology", expected_keywords)
    
    print(f"Score: {result.score:.2f}")
    print(f"Tier: {result.tier_used.value}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Time: {result.evaluation_time:.2f}s")
    print(f"Feedback: {result.feedback}")
    print(f"Suggestions: {result.improvement_suggestions}")


if __name__ == "__main__":
    main()