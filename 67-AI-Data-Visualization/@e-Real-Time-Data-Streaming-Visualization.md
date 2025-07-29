# @e-Real-Time-Data-Streaming-Visualization

## 🎯 Learning Objectives
- Master real-time data streaming architectures for live visualization
- Develop high-performance streaming data pipelines with AI integration
- Build responsive visualization systems that handle continuous data flow
- Implement intelligent buffering and optimization for streaming analytics
- Create adaptive visualization systems that adjust to data velocity changes

## 🔧 Core Real-Time Streaming Concepts

### Streaming Data Architecture

#### High-Performance Data Pipeline
```python
import asyncio
import websockets
import json
from typing import Dict, List, Callable, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np
from collections import deque
import threading
import time

@dataclass
class StreamingDataPoint:
    timestamp: float
    value: Any
    source: str
    metadata: Dict[str, Any] = None

class StreamingDataBuffer:
    def __init__(self, max_size: int = 10000, window_size: timedelta = timedelta(minutes=5)):
        self.max_size = max_size
        self.window_size = window_size
        self.buffer = deque(maxlen=max_size)
        self.indices = {}  # For fast lookups
        self.lock = threading.RLock()
    
    def add_data_point(self, data_point: StreamingDataPoint):
        with self.lock:
            self.buffer.append(data_point)
            
            # Maintain time-based window
            current_time = time.time()
            cutoff_time = current_time - self.window_size.total_seconds()
            
            # Remove old data points
            while self.buffer and self.buffer[0].timestamp < cutoff_time:
                old_point = self.buffer.popleft()
                # Clean up indices if they exist
                if old_point.source in self.indices:
                    self.indices[old_point.source].discard(len(self.buffer))
    
    def get_recent_data(self, source: str = None, duration: timedelta = None) -> List[StreamingDataPoint]:
        with self.lock:
            if not duration:
                duration = self.window_size
            
            cutoff_time = time.time() - duration.total_seconds()
            
            if source:
                return [point for point in self.buffer 
                       if point.source == source and point.timestamp >= cutoff_time]
            else:
                return [point for point in self.buffer 
                       if point.timestamp >= cutoff_time]
    
    def get_aggregated_data(self, aggregation: str, interval: timedelta, source: str = None) -> List[Dict]:
        """Aggregate streaming data into time buckets"""
        with self.lock:
            data_points = self.get_recent_data(source)
            
            if not data_points:
                return []
            
            # Group by time intervals
            interval_seconds = interval.total_seconds()
            buckets = {}
            
            for point in data_points:
                bucket_key = int(point.timestamp // interval_seconds) * interval_seconds
                if bucket_key not in buckets:
                    buckets[bucket_key] = []
                buckets[bucket_key].append(point.value)
            
            # Apply aggregation
            result = []
            for bucket_time, values in sorted(buckets.items()):
                if aggregation == 'mean':
                    agg_value = np.mean(values)
                elif aggregation == 'sum':
                    agg_value = np.sum(values)
                elif aggregation == 'count':
                    agg_value = len(values)
                elif aggregation == 'max':
                    agg_value = np.max(values)
                elif aggregation == 'min':
                    agg_value = np.min(values)
                else:
                    agg_value = values[-1]  # Latest value
                
                result.append({
                    'timestamp': bucket_time,
                    'value': float(agg_value),
                    'count': len(values)
                })
            
            return result

class RealTimeDataProcessor:
    def __init__(self):
        self.buffers = {}
        self.processors = {}
        self.subscribers = {}
        self.is_running = False
        
    def register_data_source(self, source_id: str, buffer_config: Dict = None):
        """Register a new streaming data source"""
        config = buffer_config or {}
        self.buffers[source_id] = StreamingDataBuffer(
            max_size=config.get('max_size', 10000),
            window_size=timedelta(minutes=config.get('window_minutes', 5))
        )
        self.subscribers[source_id] = []
    
    def subscribe_to_updates(self, source_id: str, callback: Callable):
        """Subscribe to real-time updates from a data source"""
        if source_id not in self.subscribers:
            self.subscribers[source_id] = []
        self.subscribers[source_id].append(callback)
    
    async def process_streaming_data(self, source_id: str, data_stream):
        """Process continuous data stream"""
        buffer = self.buffers.get(source_id)
        if not buffer:
            raise ValueError(f"Data source {source_id} not registered")
        
        async for raw_data in data_stream:
            # Parse and validate data
            data_point = self._parse_data_point(raw_data, source_id)
            
            # Add to buffer
            buffer.add_data_point(data_point)
            
            # Notify subscribers
            await self._notify_subscribers(source_id, data_point)
    
    def _parse_data_point(self, raw_data: Any, source_id: str) -> StreamingDataPoint:
        """Parse raw data into structured format"""
        if isinstance(raw_data, dict):
            return StreamingDataPoint(
                timestamp=raw_data.get('timestamp', time.time()),
                value=raw_data.get('value'),
                source=source_id,
                metadata=raw_data.get('metadata', {})
            )
        else:
            return StreamingDataPoint(
                timestamp=time.time(),
                value=raw_data,
                source=source_id
            )
    
    async def _notify_subscribers(self, source_id: str, data_point: StreamingDataPoint):
        """Notify all subscribers of new data"""
        subscribers = self.subscribers.get(source_id, [])
        
        for callback in subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data_point)
                else:
                    callback(data_point)
            except Exception as e:
                print(f"Error notifying subscriber: {e}")
```

#### WebSocket-Based Real-Time Communication
```python
import websockets
import json
import asyncio
from typing import Set

class RealTimeVisualizationServer:
    def __init__(self, port: int = 8765):
        self.port = port
        self.connected_clients: Set[websockets.WebSocketServerProtocol] = set()
        self.data_processor = RealTimeDataProcessor()
        self.chart_configurations = {}
        
    async def start_server(self):
        """Start WebSocket server for real-time visualization"""
        print(f"Starting real-time visualization server on port {self.port}")
        
        async with websockets.serve(self.handle_client_connection, "localhost", self.port):
            await asyncio.Future()  # Run forever
    
    async def handle_client_connection(self, websocket, path):
        """Handle new client connections"""
        self.connected_clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.connected_clients)}")
        
        try:
            await self.send_initial_data(websocket)
            
            async for message in websocket:
                await self.handle_client_message(websocket, json.loads(message))
                
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            self.connected_clients.remove(websocket)
            print(f"Client disconnected. Total clients: {len(self.connected_clients)}")
    
    async def send_initial_data(self, websocket):
        """Send initial data and configuration to new client"""
        initial_data = {
            'type': 'initial_configuration',
            'charts': list(self.chart_configurations.keys()),
            'data_sources': list(self.data_processor.buffers.keys())
        }
        
        await websocket.send(json.dumps(initial_data))
    
    async def handle_client_message(self, websocket, message):
        """Handle messages from clients"""
        message_type = message.get('type')
        
        if message_type == 'subscribe_to_chart':
            chart_id = message.get('chart_id')
            await self.subscribe_client_to_chart(websocket, chart_id)
            
        elif message_type == 'request_historical_data':
            await self.send_historical_data(websocket, message)
            
        elif message_type == 'update_chart_config':
            await self.update_chart_configuration(message)
    
    async def subscribe_client_to_chart(self, websocket, chart_id: str):
        """Subscribe client to real-time updates for specific chart"""
        if chart_id in self.chart_configurations:
            config = self.chart_configurations[chart_id]
            data_source = config['data_source']
            
            # Add client-specific callback
            async def client_update_callback(data_point: StreamingDataPoint):
                update_message = {
                    'type': 'chart_data_update',
                    'chart_id': chart_id,
                    'data_point': {
                        'timestamp': data_point.timestamp,
                        'value': data_point.value,
                        'source': data_point.source
                    }
                }
                
                try:
                    await websocket.send(json.dumps(update_message))
                except:
                    # Client disconnected
                    pass
            
            self.data_processor.subscribe_to_updates(data_source, client_update_callback)
    
    async def broadcast_to_all_clients(self, message: Dict):
        """Broadcast message to all connected clients"""
        if self.connected_clients:
            await asyncio.gather(
                *[client.send(json.dumps(message)) for client in self.connected_clients],
                return_exceptions=True
            )
    
    def register_chart(self, chart_id: str, config: Dict):
        """Register a new real-time chart"""
        self.chart_configurations[chart_id] = config
        
        # Register data source if not exists
        data_source = config['data_source']
        if data_source not in self.data_processor.buffers:
            self.data_processor.register_data_source(data_source, config.get('buffer_config', {}))
    
    async def simulate_data_stream(self, source_id: str, data_generator: Callable):
        """Simulate streaming data for testing"""
        while True:
            try:
                data = data_generator()
                data_point = StreamingDataPoint(
                    timestamp=time.time(),
                    value=data,
                    source=source_id
                )
                
                buffer = self.data_processor.buffers.get(source_id)
                if buffer:
                    buffer.add_data_point(data_point)
                    await self.data_processor._notify_subscribers(source_id, data_point)
                
                await asyncio.sleep(0.1)  # 10 updates per second
                
            except Exception as e:
                print(f"Error in data simulation: {e}")
                await asyncio.sleep(1)
```

### Intelligent Data Sampling and Optimization

#### Adaptive Sampling Strategy
```python
import numpy as np
from typing import Tuple, Optional
from enum import Enum

class SamplingStrategy(Enum):
    UNIFORM = "uniform"
    ADAPTIVE = "adaptive"
    IMPORTANCE_BASED = "importance_based"
    OUTLIER_PRESERVING = "outlier_preserving"

class StreamingDataSampler:
    def __init__(self, target_points: int = 1000, strategy: SamplingStrategy = SamplingStrategy.ADAPTIVE):
        self.target_points = target_points
        self.strategy = strategy
        self.importance_threshold = 0.1
        self.outlier_zscore_threshold = 2.0
        
    def sample_data_stream(self, data_points: List[StreamingDataPoint]) -> List[StreamingDataPoint]:
        """Apply intelligent sampling to reduce data density while preserving important information"""
        
        if len(data_points) <= self.target_points:
            return data_points
        
        if self.strategy == SamplingStrategy.UNIFORM:
            return self._uniform_sampling(data_points)
        elif self.strategy == SamplingStrategy.ADAPTIVE:
            return self._adaptive_sampling(data_points)
        elif self.strategy == SamplingStrategy.IMPORTANCE_BASED:
            return self._importance_based_sampling(data_points)
        elif self.strategy == SamplingStrategy.OUTLIER_PRESERVING:
            return self._outlier_preserving_sampling(data_points)
        
        return data_points
    
    def _uniform_sampling(self, data_points: List[StreamingDataPoint]) -> List[StreamingDataPoint]:
        """Simple uniform sampling - take every nth point"""
        step = len(data_points) // self.target_points
        return data_points[::step]
    
    def _adaptive_sampling(self, data_points: List[StreamingDataPoint]) -> List[StreamingDataPoint]:
        """Adaptive sampling based on data variability"""
        if len(data_points) < 3:
            return data_points
        
        # Calculate local variability
        values = [float(point.value) if isinstance(point.value, (int, float)) else 0 
                 for point in data_points]
        
        # Calculate moving variance
        window_size = min(10, len(values) // 10)
        variances = []
        
        for i in range(len(values)):
            start_idx = max(0, i - window_size // 2)
            end_idx = min(len(values), i + window_size // 2 + 1)
            local_values = values[start_idx:end_idx]
            
            if len(local_values) > 1:
                variance = np.var(local_values)
            else:
                variance = 0
            variances.append(variance)
        
        # Sample more densely in high-variance regions
        variance_threshold = np.percentile(variances, 70)
        sampled_indices = []
        
        i = 0
        while i < len(data_points) and len(sampled_indices) < self.target_points:
            sampled_indices.append(i)
            
            # Determine next sampling interval based on variance
            if variances[i] > variance_threshold:
                # High variance - sample more densely
                step = max(1, (len(data_points) - i) // (self.target_points - len(sampled_indices)) // 2)
            else:
                # Low variance - can skip more points
                step = max(1, (len(data_points) - i) // (self.target_points - len(sampled_indices)))
            
            i += step
        
        return [data_points[i] for i in sampled_indices]
    
    def _importance_based_sampling(self, data_points: List[StreamingDataPoint]) -> List[StreamingDataPoint]:
        """Sample based on data importance (peaks, valleys, inflection points)"""
        if len(data_points) < 3:
            return data_points
        
        values = [float(point.value) if isinstance(point.value, (int, float)) else 0 
                 for point in data_points]
        
        # Calculate importance scores
        importance_scores = self._calculate_importance_scores(values)
        
        # Select top important points
        important_indices = np.argsort(importance_scores)[-self.target_points:]
        important_indices = sorted(important_indices)
        
        return [data_points[i] for i in important_indices]
    
    def _calculate_importance_scores(self, values: List[float]) -> List[float]:
        """Calculate importance scores for data points"""
        if len(values) < 3:
            return [1.0] * len(values)
        
        scores = []
        
        for i in range(len(values)):
            score = 0
            
            # Local extrema detection
            if i > 0 and i < len(values) - 1:
                if (values[i] > values[i-1] and values[i] > values[i+1]) or \
                   (values[i] < values[i-1] and values[i] < values[i+1]):
                    score += 2.0  # Peak or valley
            
            # Rate of change
            if i > 0 and i < len(values) - 1:
                rate_of_change = abs((values[i+1] - values[i-1]) / 2)
                score += rate_of_change
            
            # Distance from mean
            local_mean = np.mean(values[max(0, i-5):min(len(values), i+6)])
            score += abs(values[i] - local_mean)
            
            scores.append(score)
        
        return scores
    
    def _outlier_preserving_sampling(self, data_points: List[StreamingDataPoint]) -> List[StreamingDataPoint]:
        """Preserve outliers while sampling regular data"""
        values = [float(point.value) if isinstance(point.value, (int, float)) else 0 
                 for point in data_points]
        
        if len(values) < 3:
            return data_points
        
        # Identify outliers using z-score
        z_scores = np.abs((values - np.mean(values)) / np.std(values))
        outlier_indices = np.where(z_scores > self.outlier_zscore_threshold)[0]
        
        # Always include outliers
        selected_indices = set(outlier_indices)
        
        # Sample remaining points uniformly
        non_outlier_indices = [i for i in range(len(data_points)) if i not in outlier_indices]
        remaining_slots = self.target_points - len(outlier_indices)
        
        if remaining_slots > 0 and non_outlier_indices:
            step = len(non_outlier_indices) // remaining_slots
            sampled_regular = non_outlier_indices[::max(1, step)][:remaining_slots]
            selected_indices.update(sampled_regular)
        
        # Return sorted by timestamp
        selected_indices = sorted(selected_indices)
        return [data_points[i] for i in selected_indices]
```

## 🚀 AI/LLM Integration for Real-Time Visualization

### Intelligent Stream Analysis
```python
class AIStreamAnalyzer:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.pattern_memory = {}
        self.anomaly_threshold = 2.0
        
    async def analyze_stream_in_realtime(self, data_stream: List[StreamingDataPoint], 
                                       analysis_window: int = 100) -> Dict:
        """Perform real-time AI analysis of streaming data"""
        
        if len(data_stream) < analysis_window:
            return {'status': 'insufficient_data'}
        
        # Get recent data window
        recent_data = data_stream[-analysis_window:]
        values = [point.value for point in recent_data if isinstance(point.value, (int, float))]
        
        if not values:
            return {'status': 'no_numeric_data'}
        
        # Statistical analysis
        stats = self._calculate_stream_statistics(values)
        
        # Anomaly detection
        anomalies = self._detect_anomalies(values)
        
        # Pattern recognition
        patterns = self._recognize_patterns(values)
        
        # LLM-based interpretation
        interpretation = await self._generate_ai_interpretation(stats, anomalies, patterns)
        
        return {
            'status': 'analysis_complete',
            'statistics': stats,
            'anomalies': anomalies,
            'patterns': patterns,
            'ai_interpretation': interpretation,
            'recommendations': await self._generate_recommendations(stats, patterns)
        }
    
    def _calculate_stream_statistics(self, values: List[float]) -> Dict:
        """Calculate streaming statistics"""
        return {
            'mean': np.mean(values),
            'std': np.std(values),
            'min': np.min(values),
            'max': np.max(values),
            'trend': self._calculate_trend(values),
            'volatility': np.std(np.diff(values)) if len(values) > 1 else 0,
            'recent_change': (values[-1] - values[-10]) / values[-10] if len(values) >= 10 else 0
        }
    
    def _detect_anomalies(self, values: List[float]) -> List[Dict]:
        """Detect anomalies in streaming data"""
        if len(values) < 10:
            return []
        
        # Z-score based anomaly detection
        z_scores = np.abs((values - np.mean(values)) / np.std(values))
        anomaly_indices = np.where(z_scores > self.anomaly_threshold)[0]
        
        anomalies = []
        for idx in anomaly_indices:
            anomalies.append({
                'index': int(idx),
                'value': values[idx],
                'z_score': float(z_scores[idx]),
                'type': 'statistical_outlier'
            })
        
        return anomalies
    
    async def _generate_ai_interpretation(self, stats: Dict, anomalies: List, patterns: Dict) -> str:
        """Generate AI interpretation of streaming data"""
        
        prompt = f"""
        Analyze this real-time data stream:
        
        Statistics:
        - Mean: {stats['mean']:.2f}
        - Standard Deviation: {stats['std']:.2f}
        - Trend: {stats['trend']}
        - Volatility: {stats['volatility']:.2f}
        - Recent Change: {stats['recent_change']:.2%}
        
        Anomalies Detected: {len(anomalies)}
        Patterns: {patterns}
        
        Provide a concise interpretation of:
        1. Overall data health and stability
        2. Significance of any anomalies
        3. Key trends and patterns
        4. Potential concerns or opportunities
        
        Keep response under 150 words.
        """
        
        try:
            response = await self.llm_client.generate_async(prompt)
            return response
        except:
            return "Analysis complete - check statistics and anomalies for details."
    
    async def _generate_recommendations(self, stats: Dict, patterns: Dict) -> List[str]:
        """Generate actionable recommendations based on stream analysis"""
        
        recommendations = []
        
        # High volatility recommendation
        if stats['volatility'] > np.mean([stats['std']]) * 1.5:
            recommendations.append("High volatility detected - consider implementing additional smoothing or investigating root causes")
        
        # Trend-based recommendations
        if stats['trend'] == 'increasing' and stats['recent_change'] > 0.1:
            recommendations.append("Strong upward trend - monitor for potential peaks or capacity limits")
        elif stats['trend'] == 'decreasing' and stats['recent_change'] < -0.1:
            recommendations.append("Declining trend detected - investigate potential issues or performance degradation")
        
        # Pattern-based recommendations
        if patterns.get('seasonality'):
            recommendations.append("Seasonal patterns detected - consider predictive scaling or resource planning")
        
        return recommendations

class PredictiveStreamingVisualizer:
    def __init__(self, ai_analyzer: AIStreamAnalyzer):
        self.ai_analyzer = ai_analyzer
        self.prediction_models = {}
        self.forecast_horizon = 60  # seconds
        
    async def create_predictive_chart(self, data_stream: List[StreamingDataPoint], 
                                    chart_config: Dict) -> Dict:
        """Create chart with predictive forecasting"""
        
        # Analyze current stream
        analysis = await self.ai_analyzer.analyze_stream_in_realtime(data_stream)
        
        # Generate predictions
        predictions = self._generate_predictions(data_stream)
        
        # Enhanced chart configuration
        enhanced_config = chart_config.copy()
        enhanced_config.update({
            'type': 'predictive_timeseries',
            'show_predictions': True,
            'show_confidence_bands': True,
            'analysis_insights': analysis.get('ai_interpretation', ''),
            'predictions': predictions,
            'forecast_horizon': self.forecast_horizon
        })
        
        return enhanced_config
    
    def _generate_predictions(self, data_stream: List[StreamingDataPoint]) -> List[Dict]:
        """Generate simple predictions for streaming data"""
        if len(data_stream) < 10:
            return []
        
        # Extract recent values and timestamps
        recent_points = data_stream[-20:]  # Use last 20 points
        values = [point.value for point in recent_points if isinstance(point.value, (int, float))]
        timestamps = [point.timestamp for point in recent_points]
        
        if len(values) < 5:
            return []
        
        # Simple linear trend prediction
        x = np.arange(len(values))
        coeffs = np.polyfit(x, values, 1)  # Linear fit
        
        # Generate future predictions
        predictions = []
        last_timestamp = timestamps[-1]
        
        for i in range(1, 11):  # Predict next 10 points
            future_timestamp = last_timestamp + i
            predicted_value = coeffs[0] * (len(values) + i) + coeffs[1]
            
            # Add some uncertainty
            uncertainty = np.std(values) * (i / 10)  # Uncertainty increases with time
            
            predictions.append({
                'timestamp': future_timestamp,
                'predicted_value': float(predicted_value),
                'confidence_upper': float(predicted_value + uncertainty),
                'confidence_lower': float(predicted_value - uncertainty)
            })
        
        return predictions
```

### Adaptive Visualization Engine
```python
class AdaptiveVisualizationEngine:
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.adaptation_rules = {
            'high_frequency': self._adapt_for_high_frequency,
            'high_volume': self._adapt_for_high_volume, 
            'low_performance': self._adapt_for_low_performance,
            'pattern_change': self._adapt_for_pattern_change
        }
        
    def adapt_visualization(self, chart_config: Dict, stream_characteristics: Dict, 
                          performance_metrics: Dict) -> Dict:
        """Adapt visualization based on streaming characteristics and performance"""
        
        adapted_config = chart_config.copy()
        
        # Determine adaptation strategy
        adaptations_needed = self._analyze_adaptation_needs(
            stream_characteristics, performance_metrics
        )
        
        # Apply adaptations
        for adaptation_type in adaptations_needed:
            if adaptation_type in self.adaptation_rules:
                adapted_config = self.adaptation_rules[adaptation_type](
                    adapted_config, stream_characteristics, performance_metrics
                )
        
        return adapted_config
    
    def _analyze_adaptation_needs(self, stream_chars: Dict, perf_metrics: Dict) -> List[str]:
        """Analyze what adaptations are needed"""
        adaptations = []
        
        # High frequency data
        if stream_chars.get('update_frequency', 0) > 50:  # >50 updates/sec
            adaptations.append('high_frequency')
        
        # High volume
        if stream_chars.get('data_points_per_second', 0) > 1000:
            adaptations.append('high_volume')
        
        # Performance issues
        if perf_metrics.get('render_time', 0) > 100:  # >100ms render time
            adaptations.append('low_performance')
        
        # Pattern changes
        if stream_chars.get('pattern_stability', 1.0) < 0.7:
            adaptations.append('pattern_change')
        
        return adaptations
    
    def _adapt_for_high_frequency(self, config: Dict, stream_chars: Dict, perf_metrics: Dict) -> Dict:
        """Adapt for high-frequency data streams"""
        config['sampling_strategy'] = 'adaptive'
        config['update_throttle'] = 100  # milliseconds
        config['max_visible_points'] = 500
        config['enable_data_aggregation'] = True
        config['aggregation_window'] = '1s'
        
        return config
    
    def _adapt_for_high_volume(self, config: Dict, stream_chars: Dict, perf_metrics: Dict) -> Dict:
        """Adapt for high-volume data streams"""
        config['enable_virtualization'] = True
        config['chunk_size'] = 1000
        config['lazy_rendering'] = True
        config['compress_historical_data'] = True
        
        return config
    
    def _adapt_for_low_performance(self, config: Dict, stream_chars: Dict, perf_metrics: Dict) -> Dict:
        """Adapt for low-performance scenarios"""
        config['reduce_animation'] = True
        config['simplify_rendering'] = True
        config['decrease_update_frequency'] = True
        config['disable_antialiasing'] = True
        config['use_canvas_instead_of_svg'] = True
        
        return config
```

## 💡 Advanced Real-Time Features

### Multi-Stream Synchronization
```python
class MultiStreamSynchronizer:
    def __init__(self):
        self.streams = {}
        self.sync_buffer = {}
        self.sync_tolerance = 0.1  # seconds
        
    def register_stream(self, stream_id: str, stream_source):
        """Register a data stream for synchronization"""
        self.streams[stream_id] = {
            'source': stream_source,
            'buffer': deque(maxlen=1000),
            'last_sync_time': 0
        }
        self.sync_buffer[stream_id] = deque(maxlen=100)
    
    async def synchronize_streams(self) -> Dict[str, List[StreamingDataPoint]]:
        """Synchronize multiple data streams by timestamp"""
        
        # Collect data from all streams
        for stream_id, stream_info in self.streams.items():
            # This would read from actual stream source
            new_data = await self._read_from_stream(stream_info['source'])
            
            for data_point in new_data:
                self.sync_buffer[stream_id].append(data_point)
        
        # Find common time window
        synchronized_data = {}
        
        if not self.sync_buffer:
            return synchronized_data
        
        # Find the latest minimum timestamp across all streams
        min_timestamps = []
        for stream_id, buffer in self.sync_buffer.items():
            if buffer:
                min_timestamps.append(min(point.timestamp for point in buffer))
        
        if not min_timestamps:
            return synchronized_data
        
        sync_start_time = max(min_timestamps)
        
        # Extract synchronized data
        for stream_id, buffer in self.sync_buffer.items():
            synchronized_data[stream_id] = [
                point for point in buffer 
                if point.timestamp >= sync_start_time
            ]
        
        return synchronized_data
    
    def create_synchronized_visualization(self, sync_data: Dict[str, List[StreamingDataPoint]]) -> Dict:
        """Create visualization configuration for synchronized streams"""
        
        chart_config = {
            'type': 'multi_stream_timeline',
            'streams': [],
            'synchronization': {
                'enabled': True,
                'tolerance': self.sync_tolerance,
                'sync_time': time.time()
            }
        }
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        for i, (stream_id, data_points) in enumerate(sync_data.items()):
            stream_config = {
                'id': stream_id,
                'name': stream_id.replace('_', ' ').title(),
                'data': [
                    {
                        'timestamp': point.timestamp,
                        'value': point.value
                    }
                    for point in data_points
                ],
                'color': colors[i % len(colors)],
                'line_style': 'solid'
            }
            
            chart_config['streams'].append(stream_config)
        
        return chart_config
```

## 📊 Unity Game Development Integration

### Real-Time Game Analytics Streaming
```csharp
using UnityEngine;
using System.Collections.Generic;
using System.Collections;
using WebSocketSharp;
using System.Text;
using Newtonsoft.Json;

public class RealTimeGameAnalytics : MonoBehaviour
{
    [System.Serializable]
    public class GameMetricStream
    {
        public string metricName;
        public float currentValue;
        public Queue<float> recentValues;
        public bool isStreaming;
        
        public GameMetricStream(string name)
        {
            metricName = name;
            recentValues = new Queue<float>();
            isStreaming = false;
        }
    }
    
    [System.Serializable]
    public class StreamingDataPacket
    {
        public string streamId;
        public float timestamp;
        public float value;
        public Dictionary<string, object> metadata;
    }
    
    public string websocketUrl = "ws://localhost:8765";
    public float streamingInterval = 0.1f; // 10 fps
    public int maxBufferSize = 1000;
    
    private WebSocket webSocket;
    private Dictionary<string, GameMetricStream> activeStreams;
    private bool isConnected = false;
    
    // Performance metrics
    private int frameCount = 0;
    private float deltaTime = 0.0f;
    private float fps = 0.0f;
    
    private void Start()
    {
        InitializeStreaming();
        StartCoroutine(StreamGameMetrics());
    }
    
    private void InitializeStreaming()
    {
        activeStreams = new Dictionary<string, GameMetricStream>();
        
        // Register core game metrics
        RegisterMetricStream("fps");
        RegisterMetricStream("memory_usage_mb");
        RegisterMetricStream("player_position_x");
        RegisterMetricStream("player_position_z");
        RegisterMetricStream("active_enemies");
        RegisterMetricStream("player_health");
        RegisterMetricStream("score");
        
        // Initialize WebSocket connection
        ConnectToVisualizationServer();
    }
    
    private void ConnectToVisualizationServer()
    {
        try
        {
            webSocket = new WebSocket(websocketUrl);
            
            webSocket.OnOpen += (sender, e) =>
            {
                isConnected = true;
                Debug.Log("Connected to real-time visualization server");
            };
            
            webSocket.OnMessage += (sender, e) =>
            {
                HandleServerMessage(e.Data);
            };
            
            webSocket.OnError += (sender, e) =>
            {
                Debug.LogError($"WebSocket error: {e.Message}");
                isConnected = false;
            };
            
            webSocket.OnClose += (sender, e) =>
            {
                isConnected = false;
                Debug.Log("Disconnected from visualization server");
                
                // Attempt reconnection after delay
                StartCoroutine(ReconnectAfterDelay(5.0f));
            };
            
            webSocket.Connect();
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"Failed to connect to visualization server: {ex.Message}");
        }
    }
    
    private IEnumerator ReconnectAfterDelay(float delay)
    {
        yield return new WaitForSeconds(delay);
        if (!isConnected)
        {
            ConnectToVisualizationServer();
        }
    }
    
    public void RegisterMetricStream(string metricName)
    {
        if (!activeStreams.ContainsKey(metricName))
        {
            activeStreams[metricName] = new GameMetricStream(metricName);
        }
    }
    
    public void StartStreaming(string metricName)
    {
        if (activeStreams.ContainsKey(metricName))
        {
            activeStreams[metricName].isStreaming = true;
        }
    }
    
    public void StopStreaming(string metricName)
    {
        if (activeStreams.ContainsKey(metricName))
        {
            activeStreams[metricName].isStreaming = false;
        }
    }
    
    private IEnumerator StreamGameMetrics()
    {
        while (true)
        {
            if (isConnected)
            {
                // Collect current metric values
                CollectMetricValues();
                
                // Stream active metrics
                foreach (var kvp in activeStreams)
                {
                    if (kvp.Value.isStreaming)
                    {
                        StreamMetric(kvp.Key, kvp.Value.currentValue);
                    }
                }
            }
            
            yield return new WaitForSeconds(streamingInterval);
        }
    }
    
    private void CollectMetricValues()
    {
        // FPS calculation
        frameCount++;
        deltaTime += (Time.unscaledDeltaTime - deltaTime) * 0.1f;
        fps = 1.0f / deltaTime;
        UpdateMetricValue("fps", fps);
        
        // Memory usage
        long memoryUsage = System.GC.GetTotalMemory(false);
        float memoryMB = memoryUsage / (1024f * 1024f);
        UpdateMetricValue("memory_usage_mb", memoryMB);
        
        // Player position (if player exists)
        GameObject player = GameObject.FindWithTag("Player");
        if (player != null)
        {
            Vector3 pos = player.transform.position;
            UpdateMetricValue("player_position_x", pos.x);
            UpdateMetricValue("player_position_z", pos.z);
        }
        
        // Active enemies count
        GameObject[] enemies = GameObject.FindGameObjectsWithTag("Enemy");
        UpdateMetricValue("active_enemies", enemies.Length);
        
        // Additional custom metrics would be collected here
    }
    
    private void UpdateMetricValue(string metricName, float value)
    {
        if (activeStreams.ContainsKey(metricName))
        {
            var stream = activeStreams[metricName];
            stream.currentValue = value;
            
            // Maintain recent values buffer
            stream.recentValues.Enqueue(value);
            if (stream.recentValues.Count > maxBufferSize)
            {
                stream.recentValues.Dequeue();
            }
        }
    }
    
    private void StreamMetric(string metricName, float value)
    {
        var packet = new StreamingDataPacket
        {
            streamId = metricName,
            timestamp = Time.time,
            value = value,
            metadata = new Dictionary<string, object>
            {
                ["gameTime"] = Time.time,
                ["level"] = Application.loadedLevelName,
                ["frameCount"] = frameCount
            }
        };
        
        string jsonData = JsonConvert.SerializeObject(packet);
        
        try
        {
            webSocket.Send(jsonData);
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"Failed to send metric data: {ex.Message}");
        }
    }
    
    private void HandleServerMessage(string message)
    {
        try
        {
            var serverCommand = JsonConvert.DeserializeObject<Dictionary<string, object>>(message);
            string commandType = serverCommand["type"].ToString();
            
            switch (commandType)
            {
                case "start_streaming":
                    string metricToStart = serverCommand["metric"].ToString();
                    StartStreaming(metricToStart);
                    break;
                    
                case "stop_streaming":
                    string metricToStop = serverCommand["metric"].ToString();
                    StopStreaming(metricToStop);
                    break;
                    
                case "request_historical_data":
                    string requestedMetric = serverCommand["metric"].ToString();
                    SendHistoricalData(requestedMetric);
                    break;
            }
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"Error handling server message: {ex.Message}");
        }
    }
    
    private void SendHistoricalData(string metricName)
    {
        if (activeStreams.ContainsKey(metricName))
        {
            var stream = activeStreams[metricName];
            var historicalData = new
            {
                type = "historical_data_response",
                metric = metricName,
                data = stream.recentValues.ToArray()
            };
            
            string jsonData = JsonConvert.SerializeObject(historicalData);
            webSocket.Send(jsonData);
        }
    }
    
    private void OnDestroy()
    {
        if (webSocket != null && isConnected)
        {
            webSocket.Close();
        }
    }
    
    // Public methods for external metric registration
    public void RegisterCustomMetric(string metricName, System.Func<float> valueProvider)
    {
        RegisterMetricStream(metricName);
        StartCoroutine(UpdateCustomMetric(metricName, valueProvider));
    }
    
    private IEnumerator UpdateCustomMetric(string metricName, System.Func<float> valueProvider)
    {
        while (activeStreams.ContainsKey(metricName))
        {
            try
            {
                float value = valueProvider();
                UpdateMetricValue(metricName, value);
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"Error updating custom metric {metricName}: {ex.Message}");
            }
            
            yield return new WaitForSeconds(streamingInterval);
        }
    }
}
```

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"id": "1", "content": "Check current state of 67-AI-Data-Visualization folder", "status": "completed", "priority": "high"}, {"id": "2", "content": "Create comprehensive markdown files for AI Data Visualization topics", "status": "in_progress", "priority": "high"}, {"id": "3", "content": "Follow naming conventions with @ prefix and alphabetical organization", "status": "completed", "priority": "medium"}, {"id": "4", "content": "Complete remaining files for comprehensive coverage", "status": "pending", "priority": "high"}]