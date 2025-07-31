# @d-Natural-Language-Data-Queries

## 🎯 Learning Objectives
- Master natural language processing for data query interfaces
- Develop AI systems that convert human language to database queries
- Build conversational analytics platforms with LLM integration
- Create intelligent query suggestion and auto-completion systems
- Implement voice-activated data exploration capabilities

## 🔧 Core Natural Language Query Concepts

### Query Intent Classification System

#### Multi-Intent Query Processor
```python
import spacy
import re
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class QueryIntent:
    primary_intent: str
    confidence: float
    entities: Dict[str, List[str]]
    temporal_context: Dict[str, str]
    aggregation_type: str
    comparison_operators: List[str]

class NaturalLanguageQueryProcessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.intent_patterns = {
            'aggregation': [
                r'\b(sum|total|count|average|mean|median|max|maximum|min|minimum)\b',
                r'\bhow (many|much)\b',
                r'\btop \d+\b',
                r'\bbottom \d+\b'
            ],
            'comparison': [
                r'\bcompare .+ (to|with|versus|vs)\b',
                r'\bdifference between\b',
                r'\bgreater than\b',
                r'\bless than\b',
                r'\bhigher than\b',
                r'\blower than\b'
            ],
            'trend_analysis': [
                r'\btrend\b',
                r'\bover time\b',
                r'\bchanges?\b',
                r'\bgrowth\b',
                r'\bdecline\b',
                r'\bincrease\b',
                r'\bdecrease\b'
            ],
            'filtering': [
                r'\bwhere\b',
                r'\bfilter by\b',
                r'\bonly\b',
                r'\bexclude\b',
                r'\bthat (are|is|have|has)\b'
            ],
            'distribution': [
                r'\bdistribution\b',
                r'\bbreakdown\b',
                r'\bby category\b',
                r'\bgroup by\b',
                r'\bsegment\b'
            ]
        }
        
        self.temporal_patterns = {
            'relative': [
                r'\blast (\d+) (day|week|month|year)s?\b',
                r'\bpast (\d+) (day|week|month|year)s?\b',
                r'\bprevious (\d+) (day|week|month|year)s?\b'
            ],
            'absolute': [
                r'\bin (\d{4})\b',
                r'\b(january|february|march|april|may|june|july|august|september|october|november|december) \d{4}\b',
                r'\b\d{1,2}/\d{1,2}/\d{4}\b'
            ],
            'contextual': [
                r'\btoday\b',
                r'\byesterday\b',
                r'\bthis (week|month|year)\b',
                r'\blast (week|month|year)\b'
            ]
        }
    
    def process_query(self, query_text: str, data_schema: Dict) -> QueryIntent:
        # Preprocess the query
        query_lower = query_text.lower().strip()
        doc = self.nlp(query_text)
        
        # Extract primary intent
        primary_intent = self._classify_primary_intent(query_lower)
        
        # Extract entities (columns, values, etc.)
        entities = self._extract_entities(doc, data_schema)
        
        # Extract temporal context
        temporal_context = self._extract_temporal_context(query_lower)
        
        # Extract aggregation type
        aggregation_type = self._extract_aggregation_type(query_lower)
        
        # Extract comparison operators
        comparison_ops = self._extract_comparison_operators(query_lower)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(query_lower, primary_intent, entities)
        
        return QueryIntent(
            primary_intent=primary_intent,
            confidence=confidence,
            entities=entities,
            temporal_context=temporal_context,
            aggregation_type=aggregation_type,
            comparison_operators=comparison_ops
        )
    
    def _classify_primary_intent(self, query: str) -> str:
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query))
                score += matches
            intent_scores[intent] = score
        
        # Return intent with highest score, or 'general' if no strong match
        if max(intent_scores.values()) > 0:
            return max(intent_scores, key=intent_scores.get)
        return 'general'
    
    def _extract_entities(self, doc, data_schema: Dict) -> Dict[str, List[str]]:
        entities = {
            'columns': [],
            'values': [],
            'operators': [],
            'functions': []
        }
        
        # Map tokens to schema elements
        available_columns = data_schema.get('columns', [])
        column_synonyms = data_schema.get('column_synonyms', {})
        
        for token in doc:
            token_text = token.text.lower()
            
            # Check for direct column matches
            if token_text in [col.lower() for col in available_columns]:
                entities['columns'].append(token_text)
            
            # Check for column synonyms
            for synonym, actual_column in column_synonyms.items():
                if synonym.lower() in token_text:
                    entities['columns'].append(actual_column)
            
            # Extract numeric values
            if token.like_num:
                entities['values'].append(token.text)
            
            # Extract quoted strings (likely values)
            if token.text.startswith('"') and token.text.endswith('"'):
                entities['values'].append(token.text.strip('"'))
        
        return entities
    
    def _extract_temporal_context(self, query: str) -> Dict[str, str]:
        temporal_info = {}
        
        # Check for relative time expressions
        for pattern in self.temporal_patterns['relative']:
            match = re.search(pattern, query)
            if match:
                amount = match.group(1)
                unit = match.group(2)
                temporal_info['type'] = 'relative'
                temporal_info['amount'] = amount
                temporal_info['unit'] = unit
                temporal_info['direction'] = 'past'
                break
        
        # Check for absolute dates
        if not temporal_info:
            for pattern in self.temporal_patterns['absolute']:
                match = re.search(pattern, query)
                if match:
                    temporal_info['type'] = 'absolute'
                    temporal_info['date_string'] = match.group(0)
                    break
        
        # Check for contextual time references
        if not temporal_info:
            for pattern in self.temporal_patterns['contextual']:
                if re.search(pattern, query):
                    temporal_info['type'] = 'contextual'
                    temporal_info['reference'] = re.search(pattern, query).group(0)
                    break
        
        return temporal_info
    
    def generate_sql_query(self, intent: QueryIntent, table_name: str) -> str:
        """Convert natural language intent to SQL query"""
        
        # Start building SQL components
        select_clause = "*"
        where_clauses = []
        group_by_clause = ""
        order_by_clause = ""
        having_clause = ""
        
        # Handle aggregation
        if intent.aggregation_type and intent.entities['columns']:
            primary_column = intent.entities['columns'][0]
            if intent.aggregation_type in ['sum', 'total']:
                select_clause = f"SUM({primary_column})"
            elif intent.aggregation_type in ['count']:
                select_clause = f"COUNT({primary_column})"
            elif intent.aggregation_type in ['average', 'mean']:
                select_clause = f"AVG({primary_column})"
            elif intent.aggregation_type in ['max', 'maximum']:
                select_clause = f"MAX({primary_column})"
            elif intent.aggregation_type in ['min', 'minimum']:
                select_clause = f"MIN({primary_column})"
        
        # Handle temporal filtering
        if intent.temporal_context:
            date_filter = self._build_date_filter(intent.temporal_context)
            if date_filter:
                where_clauses.append(date_filter)
        
        # Handle value filtering
        if intent.entities['values'] and intent.entities['columns']:
            for i, value in enumerate(intent.entities['values']):
                if i < len(intent.entities['columns']):
                    column = intent.entities['columns'][i]
                    where_clauses.append(f"{column} = '{value}'")
        
        # Handle comparison operators
        for op in intent.comparison_operators:
            if op in ['>', '<', '>=', '<=', '=', '!=']:
                # This would need more sophisticated parsing
                pass
        
        # Build final query
        query_parts = [f"SELECT {select_clause}", f"FROM {table_name}"]
        
        if where_clauses:
            query_parts.append(f"WHERE {' AND '.join(where_clauses)}")
        
        if group_by_clause:
            query_parts.append(f"GROUP BY {group_by_clause}")
        
        if having_clause:
            query_parts.append(f"HAVING {having_clause}")
        
        if order_by_clause:
            query_parts.append(f"ORDER BY {order_by_clause}")
        
        return " ".join(query_parts)
```

### Advanced Query Understanding with LLM Integration

#### LLM-Enhanced Query Processor
```python
import openai
import json
from typing import Optional

class LLMQueryProcessor:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.query_templates = {
            'aggregation': """
            Convert this natural language query to a structured format:
            Query: "{query}"
            Available columns: {columns}
            Data types: {data_types}
            
            Return JSON with:
            - intent: primary purpose of query
            - aggregation: type of aggregation needed
            - grouping: columns to group by
            - filters: conditions to apply
            - time_range: temporal constraints
            - sort: ordering requirements
            """,
            'comparison': """
            Analyze this comparison query:
            Query: "{query}"
            Available data: {schema}
            
            Identify:
            - What is being compared
            - Comparison criteria
            - Metrics to calculate
            - Grouping dimensions
            - Time periods involved
            
            Return as structured JSON.
            """,
            'exploration': """
            This appears to be an exploratory data query:
            Query: "{query}"
            Dataset info: {dataset_info}
            
            Suggest:
            - Best visualization type
            - Key dimensions to explore
            - Relevant metrics
            - Potential insights to look for
            - Follow-up questions to ask
            
            Format as JSON response.
            """
        }
    
    def process_with_llm(self, query: str, data_context: Dict) -> Dict:
        # Determine query type
        query_type = self._classify_query_type(query)
        
        # Select appropriate template
        template = self.query_templates.get(query_type, self.query_templates['exploration'])
        
        # Format prompt
        prompt = template.format(
            query=query,
            columns=data_context.get('columns', []),
            data_types=data_context.get('data_types', {}),
            schema=data_context.get('schema', {}),
            dataset_info=data_context.get('info', {})
        )
        
        # Get LLM response
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data analysis expert. Convert natural language queries to structured database operations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        # Parse response
        try:
            result = json.loads(response.choices[0].message.content)
            return self._validate_and_enhance_result(result, data_context)
        except json.JSONDecodeError:
            # Fallback to basic processing
            return self._fallback_processing(query, data_context)
    
    def _validate_and_enhance_result(self, result: Dict, context: Dict) -> Dict:
        # Validate column names exist
        available_columns = context.get('columns', [])
        
        if 'grouping' in result:
            valid_grouping = [col for col in result['grouping'] 
                            if col in available_columns]
            result['grouping'] = valid_grouping
        
        if 'filters' in result:
            valid_filters = []
            for filter_item in result['filters']:
                if filter_item.get('column') in available_columns:
                    valid_filters.append(filter_item)
            result['filters'] = valid_filters
        
        # Add execution metadata
        result['confidence'] = self._calculate_llm_confidence(result)
        result['suggested_viz'] = self._suggest_visualization(result)
        
        return result
    
    def generate_query_suggestions(self, partial_query: str, data_context: Dict) -> List[str]:
        """Generate query completion suggestions"""
        
        prompt = f"""
        The user is typing this partial query: "{partial_query}"
        Available data columns: {data_context.get('columns', [])}
        
        Suggest 5 possible completions that would create meaningful data queries.
        Focus on common analytical tasks like:
        - Aggregations and summaries
        - Trends over time
        - Comparisons between groups
        - Filtering and exploration
        
        Return as a JSON list of suggested completions.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        try:
            suggestions = json.loads(response.choices[0].message.content)
            return suggestions if isinstance(suggestions, list) else []
        except:
            return []
```

### Voice-Activated Query System

#### Speech-to-Query Pipeline
```python
import speech_recognition as sr
import pyttsx3
import queue
import threading
from typing import Callable

class VoiceQuerySystem:
    def __init__(self, query_processor: LLMQueryProcessor):
        self.query_processor = query_processor
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.is_listening = False
        self.query_queue = queue.Queue()
        
        # Configure speech recognition
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        
        # Configure text-to-speech
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.9)
    
    def start_voice_interface(self, result_callback: Callable):
        """Start continuous voice recognition for data queries"""
        self.is_listening = True
        
        # Start listening thread
        listen_thread = threading.Thread(target=self._listen_continuously)
        listen_thread.daemon = True
        listen_thread.start()
        
        # Start processing thread
        process_thread = threading.Thread(
            target=self._process_voice_queries, 
            args=(result_callback,)
        )
        process_thread.daemon = True
        process_thread.start()
        
        self._speak("Voice query system activated. Say 'data query' followed by your question.")
    
    def _listen_continuously(self):
        """Continuously listen for voice input"""
        while self.is_listening:
            try:
                with self.microphone as source:
                    # Listen for wake phrase
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                # Recognize speech
                text = self.recognizer.recognize_google(audio).lower()
                
                # Check for wake phrase
                if 'data query' in text or 'query data' in text:
                    self._speak("I'm listening for your data query")
                    
                    # Listen for actual query
                    with self.microphone as source:
                        query_audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                    
                    query_text = self.recognizer.recognize_google(query_audio)
                    self.query_queue.put(query_text)
                    
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except Exception as e:
                print(f"Voice recognition error: {e}")
    
    def _process_voice_queries(self, result_callback: Callable):
        """Process voice queries using NLP"""
        while self.is_listening:
            try:
                query = self.query_queue.get(timeout=1)
                
                self._speak("Processing your query...")
                
                # Process query
                result = self.query_processor.process_with_llm(query, {})
                
                # Execute query and get results
                # This would connect to your actual data source
                
                # Provide voice feedback
                summary = self._generate_voice_summary(result)
                self._speak(summary)
                
                # Call result callback for UI updates
                result_callback(query, result)
                
            except queue.Empty:
                continue
            except Exception as e:
                self._speak(f"Sorry, I encountered an error processing your query: {str(e)}")
    
    def _generate_voice_summary(self, query_result: Dict) -> str:
        """Generate spoken summary of query results"""
        intent = query_result.get('intent', 'unknown')
        
        if intent == 'aggregation':
            agg_type = query_result.get('aggregation', 'summary')
            return f"I found the {agg_type} you requested. The results are displayed on your screen."
        
        elif intent == 'comparison':
            return "I've compared the data as requested. Check the visualization for details."
        
        elif intent == 'trend':
            return "The trend analysis is complete. You can see the pattern in the chart."
        
        else:
            return "Your query has been processed. Results are now visible."
    
    def _speak(self, text: str):
        """Convert text to speech"""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def stop_listening(self):
        """Stop voice recognition system"""
        self.is_listening = False
        self._speak("Voice query system deactivated.")
```

## 🚀 AI/LLM Integration for Natural Language Queries

### Intelligent Query Suggestion Engine
```python
class QuerySuggestionEngine:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.query_history = []
        self.user_patterns = {}
    
    def suggest_queries(self, data_context: Dict, user_id: str = None) -> List[Dict]:
        """Generate intelligent query suggestions based on data and user patterns"""
        
        # Analyze data characteristics
        data_summary = self._analyze_data_characteristics(data_context)
        
        # Get user patterns if available
        user_context = self.user_patterns.get(user_id, {})
        
        # Generate suggestions using LLM
        prompt = f"""
        Based on this dataset, suggest 8 interesting and valuable data queries:
        
        Data characteristics:
        - Columns: {data_summary['columns']}
        - Data types: {data_summary['data_types']}
        - Row count: {data_summary['row_count']}
        - Has time series: {data_summary['has_temporal']}
        - Categorical columns: {data_summary['categorical_columns']}
        - Numeric columns: {data_summary['numeric_columns']}
        
        User preferences (if known): {user_context}
        
        Generate queries that would provide business insights, including:
        1. Trend analysis queries
        2. Comparison queries
        3. Distribution analysis
        4. Outlier detection
        5. Correlation analysis
        6. Segmentation analysis
        
        Return as JSON array with format:
        [{{
            "query": "natural language query",
            "intent": "primary purpose",
            "difficulty": "beginner|intermediate|advanced",
            "insight_potential": "high|medium|low",
            "visualization": "recommended chart type"
        }}]
        """
        
        response = self.llm_client.generate(prompt)
        
        try:
            suggestions = json.loads(response)
            return self._rank_and_filter_suggestions(suggestions, user_context)
        except:
            return self._fallback_suggestions(data_context)
    
    def learn_from_query(self, user_id: str, query: str, success: bool, execution_time: float):
        """Learn from user query patterns to improve suggestions"""
        
        if user_id not in self.user_patterns:
            self.user_patterns[user_id] = {
                'successful_queries': [],
                'preferred_intents': {},
                'complexity_preference': 'intermediate',
                'response_time_preference': 'fast'
            }
        
        user_profile = self.user_patterns[user_id]
        
        if success:
            user_profile['successful_queries'].append(query)
            
            # Analyze query intent
            intent = self._classify_query_intent(query)
            user_profile['preferred_intents'][intent] = user_profile['preferred_intents'].get(intent, 0) + 1
        
        # Update complexity preference based on usage
        complexity = self._assess_query_complexity(query)
        if success and execution_time < 5.0:  # Fast successful queries
            user_profile['complexity_preference'] = complexity
    
    def generate_follow_up_questions(self, original_query: str, results: Dict) -> List[str]:
        """Generate intelligent follow-up questions based on query results"""
        
        prompt = f"""
        A user asked: "{original_query}"
        
        The query results showed:
        - Number of results: {results.get('row_count', 'unknown')}
        - Key findings: {results.get('summary', 'various data points')}
        - Interesting patterns: {results.get('patterns', 'standard distribution')}
        
        Suggest 5 natural follow-up questions that would provide deeper insights.
        Focus on:
        - Drilling down into specific segments
        - Understanding causation
        - Exploring related dimensions
        - Time-based analysis
        - Comparative analysis
        
        Return as a simple JSON array of question strings.
        """
        
        response = self.llm_client.generate(prompt)
        
        try:
            follow_ups = json.loads(response)
            return follow_ups if isinstance(follow_ups, list) else []
        except:
            return [
                "What caused this pattern?",
                "How does this compare to previous periods?",
                "Which segment shows the strongest performance?",
                "What are the key drivers of this trend?",
                "How might this change in the future?"
            ]
```

### Query Optimization and Explanation

#### Query Performance Optimizer
```python
class QueryOptimizer:
    def __init__(self):
        self.optimization_rules = {
            'avoid_select_star': self._optimize_select_columns,
            'add_indexes': self._suggest_indexes,
            'limit_large_results': self._add_limits,
            'optimize_joins': self._optimize_joins,
            'cache_common_queries': self._identify_cacheable_queries
        }
        self.query_cache = {}
        self.performance_history = {}
    
    def optimize_query(self, query: str, data_context: Dict) -> Dict:
        """Optimize a query for better performance"""
        
        optimization_results = {
            'original_query': query,
            'optimized_query': query,
            'optimizations_applied': [],
            'estimated_improvement': 0,
            'explanation': []
        }
        
        # Apply optimization rules
        optimized_query = query
        for rule_name, rule_func in self.optimization_rules.items():
            result = rule_func(optimized_query, data_context)
            if result['improved']:
                optimized_query = result['query']
                optimization_results['optimizations_applied'].append(rule_name)
                optimization_results['explanation'].extend(result['explanation'])
                optimization_results['estimated_improvement'] += result.get('improvement_percent', 0)
        
        optimization_results['optimized_query'] = optimized_query
        
        return optimization_results
    
    def explain_query_performance(self, query: str, execution_stats: Dict) -> str:
        """Generate human-readable explanation of query performance"""
        
        execution_time = execution_stats.get('execution_time', 0)
        rows_scanned = execution_stats.get('rows_scanned', 0)
        rows_returned = execution_stats.get('rows_returned', 0)
        
        explanation_parts = []
        
        # Execution time analysis
        if execution_time < 1:
            explanation_parts.append("✅ Query executed quickly")
        elif execution_time < 5:
            explanation_parts.append("⚠️ Query took moderate time to execute")
        else:
            explanation_parts.append("🐌 Query execution was slow")
        
        # Data scanning efficiency
        if rows_scanned > 0:
            scan_efficiency = rows_returned / rows_scanned
            if scan_efficiency > 0.1:
                explanation_parts.append("✅ Query efficiently filtered data")
            else:
                explanation_parts.append("⚠️ Query scanned many rows but returned few results")
        
        # Optimization suggestions
        optimization_suggestions = self._generate_optimization_suggestions(execution_stats)
        if optimization_suggestions:
            explanation_parts.append("💡 Suggestions for improvement:")
            explanation_parts.extend(optimization_suggestions)
        
        return "\n".join(explanation_parts)
    
    def _generate_optimization_suggestions(self, stats: Dict) -> List[str]:
        suggestions = []
        
        if stats.get('full_table_scan', False):
            suggestions.append("• Consider adding an index on frequently filtered columns")
        
        if stats.get('rows_scanned', 0) > 100000:
            suggestions.append("• Add more specific filters to reduce data scanning")
        
        if stats.get('execution_time', 0) > 10:
            suggestions.append("• Consider breaking complex query into smaller parts")
        
        return suggestions
```

## 💡 Advanced Query Understanding Techniques

### Contextual Query Enhancement
```python
class ContextualQueryEnhancer:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.conversation_history = []
        self.domain_knowledge = {}
    
    def enhance_query_with_context(self, query: str, conversation_context: List[str], domain: str = None) -> Dict:
        """Enhance query understanding using conversation context and domain knowledge"""
        
        # Build context prompt
        context_info = "\n".join([
            "Previous queries in this conversation:",
            *conversation_context[-5:],  # Last 5 queries for context
            f"\nCurrent query: {query}"
        ])
        
        domain_info = ""
        if domain and domain in self.domain_knowledge:
            domain_info = f"\nDomain context ({domain}): {self.domain_knowledge[domain]}"
        
        prompt = f"""
        Analyze this query in context:
        
        {context_info}
        {domain_info}
        
        Enhance the query understanding by:
        1. Resolving ambiguous references (e.g., "it", "that", "the previous result")
        2. Inferring missing context from conversation history
        3. Identifying implicit comparisons or relationships
        4. Suggesting more specific or complete queries
        5. Detecting if this is a follow-up question
        
        Return JSON with:
        - enhanced_query: clarified version of the query
        - inferred_context: what context was used
        - confidence: how confident you are in the enhancement
        - suggestions: alternative interpretations
        """
        
        response = self.llm_client.generate(prompt)
        
        try:
            result = json.loads(response)
            self.conversation_history.append({
                'original_query': query,
                'enhanced_query': result.get('enhanced_query', query),
                'timestamp': datetime.now().isoformat()
            })
            return result
        except:
            return {
                'enhanced_query': query,
                'inferred_context': [],
                'confidence': 0.5,
                'suggestions': []
            }
    
    def add_domain_knowledge(self, domain: str, knowledge: Dict):
        """Add domain-specific knowledge to improve query understanding"""
        self.domain_knowledge[domain] = knowledge
    
    def detect_query_ambiguity(self, query: str, data_schema: Dict) -> List[Dict]:
        """Detect potentially ambiguous elements in queries"""
        
        ambiguities = []
        
        # Check for ambiguous column references
        query_words = query.lower().split()
        schema_columns = [col.lower() for col in data_schema.get('columns', [])]
        
        for word in query_words:
            # Check if word could refer to multiple columns
            potential_matches = [col for col in schema_columns if word in col or col in word]
            if len(potential_matches) > 1:
                ambiguities.append({
                    'type': 'column_ambiguity',
                    'term': word,
                    'potential_matches': potential_matches,
                    'suggestion': f"Did you mean one of: {', '.join(potential_matches)}?"
                })
        
        # Check for vague time references
        vague_time_patterns = ['recently', 'lately', 'soon', 'a while ago']
        for pattern in vague_time_patterns:
            if pattern in query.lower():
                ambiguities.append({
                    'type': 'temporal_ambiguity',
                    'term': pattern,
                    'suggestion': f"Please specify exact time period instead of '{pattern}'"
                })
        
        return ambiguities
```

## 📊 Unity Game Development Integration

### Game Analytics Natural Language Interface
```csharp
using UnityEngine;
using System.Collections.Generic;
using UnityEngine.Networking;
using System.Collections;
using System.Text;

public class GameAnalyticsNLInterface : MonoBehaviour
{
    [System.Serializable]
    public class NLQueryRequest
    {
        public string query;
        public string gameSession;
        public List<string> availableMetrics;
    }
    
    [System.Serializable]
    public class NLQueryResponse
    {
        public string interpretedQuery;
        public string queryType;
        public List<string> dataFields;
        public string visualizationType;
        public float confidence;
    }
    
    private string nlpApiUrl = "http://localhost:5000/api/nlp-query";
    private Dictionary<string, object> gameMetrics;
    
    private void Start()
    {
        InitializeMetricsCollection();
    }
    
    private void InitializeMetricsCollection()
    {
        gameMetrics = new Dictionary<string, object>
        {
            ["player_position"] = Vector3.zero,
            ["fps"] = 60f,
            ["memory_usage"] = 0f,
            ["level_completion_time"] = 0f,
            ["score"] = 0f,
            ["enemies_defeated"] = 0f,
            ["power_ups_collected"] = 0f
        };
    }
    
    public void ProcessNaturalLanguageQuery(string userQuery)
    {
        StartCoroutine(SendNLQueryToAPI(userQuery));
    }
    
    private IEnumerator SendNLQueryToAPI(string query)
    {
        var request = new NLQueryRequest
        {
            query = query,
            gameSession = System.Guid.NewGuid().ToString(),
            availableMetrics = new List<string>(gameMetrics.Keys)
        };
        
        string jsonData = JsonUtility.ToJson(request);
        
        using (UnityWebRequest webRequest = UnityWebRequest.Put(nlpApiUrl, jsonData))
        {
            webRequest.SetRequestHeader("Content-Type", "application/json");
            yield return webRequest.SendWebRequest();
            
            if (webRequest.result == UnityWebRequest.Result.Success)
            {
                var response = JsonUtility.FromJson<NLQueryResponse>(webRequest.downloadHandler.text);
                ProcessQueryResponse(response);
            }
            else
            {
                Debug.LogError($"NL Query failed: {webRequest.error}");
            }
        }
    }
    
    private void ProcessQueryResponse(NLQueryResponse response)
    {
        Debug.Log($"Interpreted Query: {response.interpretedQuery}");
        Debug.Log($"Query Type: {response.queryType}");
        Debug.Log($"Confidence: {response.confidence}");
        
        // Execute the query based on interpretation
        switch (response.queryType.ToLower())
        {
            case "performance":
                ShowPerformanceAnalytics(response.dataFields);
                break;
            case "player_behavior":
                ShowPlayerBehaviorAnalytics(response.dataFields);
                break;
            case "game_progression":
                ShowProgressionAnalytics(response.dataFields);
                break;
            default:
                ShowGeneralAnalytics(response.dataFields);
                break;
        }
    }
    
    private void ShowPerformanceAnalytics(List<string> fields)
    {
        // Create performance dashboard
        var performanceData = new Dictionary<string, float>();
        
        foreach (string field in fields)
        {
            if (gameMetrics.ContainsKey(field))
            {
                performanceData[field] = (float)gameMetrics[field];
            }
        }
        
        // Generate visualization (this would integrate with your UI system)
        CreatePerformanceVisualization(performanceData);
    }
    
    private void CreatePerformanceVisualization(Dictionary<string, float> data)
    {
        // Implementation would depend on your UI framework
        Debug.Log("Creating performance visualization with data:");
        foreach (var kvp in data)
        {
            Debug.Log($"{kvp.Key}: {kvp.Value}");
        }
    }
    
    // Voice input integration
    public void StartVoiceQuery()
    {
        // This would integrate with platform-specific voice recognition
        // For example, on mobile devices or desktop with microphone access
        
#if UNITY_ANDROID || UNITY_IOS
        StartMobileVoiceRecognition();
#elif UNITY_STANDALONE_WIN || UNITY_STANDALONE_OSX
        StartDesktopVoiceRecognition();
#endif
    }
    
    private void StartMobileVoiceRecognition()
    {
        // Mobile-specific voice recognition implementation
        Debug.Log("Starting mobile voice recognition for analytics queries");
    }
    
    private void StartDesktopVoiceRecognition()
    {
        // Desktop-specific voice recognition implementation
        Debug.Log("Starting desktop voice recognition for analytics queries");
    }
}
```

## 🎓 Advanced Learning and Professional Applications

### Next Steps for NL Query Mastery
1. **Study computational linguistics**: Deep NLP understanding
2. **Master query optimization**: Database performance tuning
3. **Learn voice processing**: Speech recognition and synthesis
4. **Practice with real datasets**: Build NL interfaces for various domains
5. **Explore multilingual support**: International query processing

### Professional Applications
1. **Business intelligence**: Executive-friendly analytics interfaces
2. **Scientific research**: Accessible data exploration for researchers
3. **Customer support**: Natural language data retrieval systems
4. **Gaming analytics**: Player-friendly analytics dashboards
5. **Healthcare**: Clinical data query interfaces

---

*Natural Language Data Queries v1.0 | Making data accessible through conversation*