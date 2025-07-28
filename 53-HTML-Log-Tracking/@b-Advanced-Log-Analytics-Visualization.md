# @b-Advanced Log Analytics & Visualization

## 🎯 Learning Objectives
- Implement advanced log analytics using JavaScript and HTML5 Canvas
- Create interactive log visualization dashboards
- Build real-time log monitoring systems with WebSocket integration
- Develop AI-powered log analysis and pattern recognition tools

## 🔧 Advanced Log Analytics Implementation

### Real-Time Log Dashboard
```html
<!-- Advanced Log Dashboard HTML Structure -->
<div class="log-dashboard">
  <div class="dashboard-header">
    <h2>Real-Time Log Analytics</h2>
    <div class="dashboard-controls">
      <select id="time-range">
        <option value="1h">Last Hour</option>
        <option value="24h">Last 24 Hours</option>
        <option value="7d">Last 7 Days</option>
      </select>
      <button id="export-btn">Export Data</button>
      <button id="clear-logs">Clear Logs</button>
    </div>
  </div>
  
  <div class="analytics-grid">
    <div class="metric-card">
      <h3>Log Volume</h3>
      <canvas id="volume-chart" width="300" height="200"></canvas>
    </div>
    
    <div class="metric-card">
      <h3>Error Rate</h3>
      <canvas id="error-chart" width="300" height="200"></canvas>
    </div>
    
    <div class="metric-card">
      <h3>Performance Metrics</h3>
      <canvas id="performance-chart" width="300" height="200"></canvas>
    </div>
    
    <div class="metric-card">
      <h3>Top Errors</h3>
      <div id="error-list" class="error-summary"></div>
    </div>
  </div>
  
  <div class="log-stream">
    <h3>Live Log Stream</h3>
    <div id="live-logs" class="scrollable-logs"></div>
  </div>
</div>
```

### Advanced Log Analytics Engine
```javascript
class AdvancedLogAnalytics {
  constructor(options = {}) {
    this.logs = [];
    this.charts = {};
    this.websocket = null;
    this.analysisWorker = null;
    this.options = {
      updateInterval: options.updateInterval || 5000,
      maxLogRetention: options.maxLogRetention || 10000,
      enableRealTime: options.enableRealTime || true,
      ...options
    };
    
    this.init();
  }

  init() {
    this.setupCharts();
    this.setupWebSocket();
    this.setupAnalysisWorker();
    this.startPeriodicUpdates();
  }

  setupCharts() {
    // Volume Chart
    this.charts.volume = new LogChart('volume-chart', {
      type: 'line',
      title: 'Log Volume Over Time',
      yAxis: 'Count',
      xAxis: 'Time'
    });

    // Error Rate Chart
    this.charts.errorRate = new LogChart('error-chart', {
      type: 'bar',
      title: 'Error Distribution',
      yAxis: 'Count',
      xAxis: 'Error Type'
    });

    // Performance Chart
    this.charts.performance = new LogChart('performance-chart', {
      type: 'scatter',
      title: 'Response Time vs Load',
      yAxis: 'Response Time (ms)',
      xAxis: 'Requests/min'
    });
  }

  analyzeLogPatterns(timeRange = '1h') {
    const cutoffTime = this.getTimeRangeCutoff(timeRange);
    const recentLogs = this.logs.filter(log => 
      new Date(log.timestamp) > cutoffTime
    );

    return {
      volume: this.calculateLogVolume(recentLogs),
      errorRate: this.calculateErrorRate(recentLogs),
      topErrors: this.getTopErrors(recentLogs),
      performanceMetrics: this.calculatePerformanceMetrics(recentLogs),
      anomalies: this.detectAnomalies(recentLogs)
    };
  }

  calculateLogVolume(logs) {
    const hourlyBuckets = {};
    logs.forEach(log => {
      const hour = new Date(log.timestamp).toISOString().substr(0, 13);
      hourlyBuckets[hour] = (hourlyBuckets[hour] || 0) + 1;
    });
    return hourlyBuckets;
  }

  calculateErrorRate(logs) {
    const total = logs.length;
    const errors = logs.filter(log => 
      log.level === 'error' || log.level === 'warn'
    ).length;
    
    return {
      total,
      errors,
      rate: total > 0 ? (errors / total) * 100 : 0,
      trend: this.calculateErrorTrend(logs)
    };
  }

  getTopErrors(logs) {
    const errorCounts = {};
    logs.filter(log => log.level === 'error').forEach(log => {
      const errorKey = this.normalizeErrorMessage(log.message);
      errorCounts[errorKey] = (errorCounts[errorKey] || 0) + 1;
    });

    return Object.entries(errorCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10)
      .map(([error, count]) => ({ error, count }));
  }

  detectAnomalies(logs) {
    const anomalies = [];
    
    // Volume anomalies
    const volumeStats = this.calculateVolumeStatistics(logs);
    if (volumeStats.current > volumeStats.mean + (2 * volumeStats.stdDev)) {
      anomalies.push({
        type: 'volume_spike',
        severity: 'high',
        description: 'Unusual spike in log volume detected'
      });
    }

    // Error burst detection
    const errorBursts = this.detectErrorBursts(logs);
    anomalies.push(...errorBursts);

    return anomalies;
  }

  setupWebSocket() {
    if (!this.options.enableRealTime) return;

    this.websocket = new WebSocket('ws://localhost:8080/logs');
    this.websocket.onmessage = (event) => {
      const logEntry = JSON.parse(event.data);
      this.addLogEntry(logEntry);
      this.updateDashboard();
    };
  }

  exportAnalytics(format = 'json') {
    const analytics = this.analyzeLogPatterns('24h');
    
    switch (format) {
      case 'json':
        return JSON.stringify(analytics, null, 2);
      case 'csv':
        return this.convertAnalyticsToCSV(analytics);
      case 'html':
        return this.generateAnalyticsReport(analytics);
      default:
        return analytics;
    }
  }
}
```

### Interactive Chart Visualization
```javascript
class LogChart {
  constructor(canvasId, options) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.options = options;
    this.data = [];
    this.animationFrame = null;
  }

  updateData(newData) {
    this.data = newData;
    this.render();
  }

  render() {
    this.clearCanvas();
    
    switch (this.options.type) {
      case 'line':
        this.renderLineChart();
        break;
      case 'bar':
        this.renderBarChart();
        break;
      case 'scatter':
        this.renderScatterPlot();
        break;
      case 'heatmap':
        this.renderHeatmap();
        break;
    }
    
    this.renderAxes();
    this.renderLegend();
  }

  renderLineChart() {
    if (this.data.length < 2) return;

    this.ctx.strokeStyle = '#4a9eff';
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();

    const { width, height } = this.canvas;
    const padding = 40;

    this.data.forEach((point, index) => {
      const x = padding + (index / (this.data.length - 1)) * (width - 2 * padding);
      const y = height - padding - (point.value / this.getMaxValue()) * (height - 2 * padding);
      
      if (index === 0) {
        this.ctx.moveTo(x, y);
      } else {
        this.ctx.lineTo(x, y);
      }
    });

    this.ctx.stroke();
    
    // Add data points
    this.ctx.fillStyle = '#4a9eff';
    this.data.forEach((point, index) => {
      const x = padding + (index / (this.data.length - 1)) * (width - 2 * padding);
      const y = height - padding - (point.value / this.getMaxValue()) * (height - 2 * padding);
      
      this.ctx.beginPath();
      this.ctx.arc(x, y, 4, 0, 2 * Math.PI);
      this.ctx.fill();
    });
  }

  renderBarChart() {
    const { width, height } = this.canvas;
    const padding = 40;
    const barWidth = (width - 2 * padding) / this.data.length;
    const maxValue = this.getMaxValue();

    this.data.forEach((point, index) => {
      const barHeight = (point.value / maxValue) * (height - 2 * padding);
      const x = padding + index * barWidth;
      const y = height - padding - barHeight;

      // Color coding based on log level
      this.ctx.fillStyle = this.getBarColor(point.label);
      this.ctx.fillRect(x + 2, y, barWidth - 4, barHeight);
    });
  }

  getBarColor(label) {
    const colorMap = {
      'error': '#d9534f',
      'warn': '#f0ad4e',
      'info': '#4a9eff',
      'debug': '#909090'
    };
    return colorMap[label] || '#4a9eff';
  }
}
```

## 🚀 AI/LLM Integration Opportunities

### Intelligent Log Analysis
```javascript
class AILogAnalyzer {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.analysisHistory = [];
  }

  async analyzeLogTrends(logs, timeframe = '24h') {
    const prompt = `
      Analyze these application logs for the past ${timeframe} and provide insights:
      
      ${JSON.stringify(logs.slice(-500), null, 2)}
      
      Please identify:
      1. Critical error patterns and their root causes
      2. Performance degradation indicators
      3. User behavior anomalies
      4. Potential security concerns
      5. Recommendations for optimization
      
      Format as structured JSON with actionable insights.
    `;

    return await this.sendToAI(prompt);
  }

  async generateLogReport(analytics) {
    const prompt = `
      Create a comprehensive log analysis report based on this data:
      
      ${JSON.stringify(analytics, null, 2)}
      
      Include:
      - Executive summary
      - Key findings and trends
      - Risk assessment
      - Action items with priorities
      - Technical recommendations
    `;

    return await this.sendToAI(prompt);
  }

  async predictLogAnomalies(historicalData) {
    const prompt = `
      Based on this historical log data, predict potential issues:
      
      ${JSON.stringify(historicalData, null, 2)}
      
      Provide:
      1. Anomaly predictions for next 24 hours
      2. Confidence levels for each prediction
      3. Suggested preventive actions
      4. Monitoring recommendations
    `;

    return await this.sendToAI(prompt);
  }
}
```

### Automated Alert Generation
```javascript
class IntelligentAlerting {
  constructor(logAnalyzer) {
    this.analyzer = logAnalyzer;
    this.alertRules = [];
    this.alertHistory = [];
  }

  async createSmartAlert(logs, severity = 'medium') {
    const analysis = await this.analyzer.analyzeLogTrends(logs, '1h');
    
    const alertPrompt = `
      Based on this log analysis, create appropriate alerts:
      
      ${JSON.stringify(analysis, null, 2)}
      
      Generate alerts with:
      - Severity level (low/medium/high/critical)
      - Alert message
      - Recommended actions
      - Escalation path
    `;

    return await this.analyzer.sendToAI(alertPrompt);
  }

  setupProactiveMonitoring() {
    setInterval(async () => {
      const recentLogs = this.getRecentLogs(300); // Last 5 minutes
      const alerts = await this.createSmartAlert(recentLogs);
      
      alerts.forEach(alert => {
        if (alert.severity === 'critical') {
          this.sendImmediateNotification(alert);
        } else {
          this.queueAlert(alert);
        }
      });
    }, 300000); // Check every 5 minutes
  }
}
```

## 💡 Key Highlights

### Advanced Analytics Features
- **Real-time Dashboards**: Live updating charts and metrics
- **Pattern Recognition**: AI-powered anomaly detection
- **Predictive Analytics**: Forecast potential issues before they occur
- **Interactive Visualizations**: Drill-down capabilities and filtering
- **Automated Reporting**: Scheduled reports with AI-generated insights

### Performance Optimization
- **Web Workers**: Offload analysis to background threads
- **Canvas Rendering**: High-performance chart visualization
- **Data Streaming**: Efficient real-time data handling
- **Memory Management**: Automatic log rotation and cleanup
- **Caching Strategies**: Optimize repeated analysis operations

### Unity Integration Applications
- **WebGL Performance Monitoring**: Track Unity web builds performance
- **Cross-Platform Analytics**: Unified logging across Unity platforms
- **Player Behavior Analysis**: Understand user interactions in games
- **Build Pipeline Monitoring**: Track Unity build processes and failures
- **Asset Loading Analytics**: Monitor Unity asset loading performance

### Career Development Value
- **Full-Stack Analytics**: Demonstrate data visualization skills
- **AI Integration**: Show modern AI/ML tool usage
- **Performance Engineering**: Highlight optimization capabilities
- **Real-time Systems**: Display distributed systems knowledge
- **Data-Driven Decision Making**: Show analytical thinking skills