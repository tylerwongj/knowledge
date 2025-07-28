# @e-Real-Time Debugging & Troubleshooting

## 🎯 Learning Objectives
- Master real-time debugging techniques using HTML log tracking systems
- Implement interactive debugging interfaces and diagnostic tools
- Create automated troubleshooting workflows with AI-powered assistance
- Build comprehensive error tracking and resolution systems

## 🔧 Real-Time Debugging Implementation

### Interactive Debug Console
```html
<!-- Real-Time Debug Interface -->
<div class="debug-console" id="debug-console">
  <div class="console-header">
    <h3>Real-Time Debug Console</h3>
    <div class="console-controls">
      <button id="clear-console">Clear</button>
      <button id="export-debug">Export</button>
      <button id="toggle-auto-scroll">Auto-scroll</button>
      <select id="log-level-filter">
        <option value="all">All Levels</option>
        <option value="debug">Debug</option>
        <option value="info">Info</option>
        <option value="warn">Warning</option>
        <option value="error">Error</option>
      </select>
    </div>
  </div>
  
  <div class="debug-tabs">
    <button class="tab-button active" data-tab="logs">Logs</button>
    <button class="tab-button" data-tab="network">Network</button>
    <button class="tab-button" data-tab="performance">Performance</button>
    <button class="tab-button" data-tab="errors">Errors</button>
    <button class="tab-button" data-tab="console">Console</button>
  </div>
  
  <div class="debug-content">
    <div id="logs-tab" class="tab-content active">
      <div id="log-stream" class="log-stream"></div>
    </div>
    
    <div id="network-tab" class="tab-content">
      <div id="network-requests" class="network-monitor"></div>
    </div>
    
    <div id="performance-tab" class="tab-content">
      <div id="performance-metrics" class="performance-monitor"></div>
    </div>
    
    <div id="errors-tab" class="tab-content">
      <div id="error-tracking" class="error-monitor"></div>
    </div>
    
    <div id="console-tab" class="tab-content">
      <div id="console-input-container">
        <input type="text" id="console-input" placeholder="Enter JavaScript command..." />
        <button id="execute-command">Execute</button>
      </div>
      <div id="console-output" class="console-output"></div>
    </div>
  </div>
</div>
```

### Advanced Debug Logger
```javascript
class RealTimeDebugger {
  constructor(options = {}) {
    this.debugLevel = options.debugLevel || 'info';
    this.maxEntries = options.maxEntries || 1000;
    this.autoScroll = options.autoScroll !== false;
    this.enableStackTrace = options.enableStackTrace !== false;
    this.enableSourceMap = options.enableSourceMap !== false;
    
    this.logs = [];
    this.errors = new Map();
    this.networkRequests = [];
    this.performanceMarks = new Map();
    this.breakpoints = new Map();
    
    this.initializeDebugger();
    this.setupErrorHandling();
    this.setupNetworkMonitoring();
    this.setupPerformanceTracking();
  }

  initializeDebugger() {
    this.originalConsole = {
      log: console.log,
      warn: console.warn,
      error: console.error,
      debug: console.debug,
      info: console.info
    };

    // Override console methods
    console.log = (...args) => {
      this.originalConsole.log(...args);
      this.addDebugEntry('info', args, this.getStackTrace());
    };

    console.warn = (...args) => {
      this.originalConsole.warn(...args);
      this.addDebugEntry('warn', args, this.getStackTrace());
    };

    console.error = (...args) => {
      this.originalConsole.error(...args);
      this.addDebugEntry('error', args, this.getStackTrace());
    };

    console.debug = (...args) => {
      this.originalConsole.debug(...args);
      this.addDebugEntry('debug', args, this.getStackTrace());
    };
  }

  addDebugEntry(level, args, stackTrace) {
    const entry = {
      id: this.generateId(),
      timestamp: new Date().toISOString(),
      level: level,
      message: args.map(arg => this.formatArgument(arg)).join(' '),
      args: args,
      stackTrace: stackTrace,
      source: this.getSourceLocation(stackTrace),
      context: this.captureContext(),
      sessionId: this.getSessionId()
    };

    this.logs.push(entry);
    this.renderDebugEntry(entry);
    
    if (this.logs.length > this.maxEntries) {
      this.logs.shift();
    }

    // Trigger analysis for critical errors
    if (level === 'error') {
      this.analyzeError(entry);
    }
  }

  formatArgument(arg) {
    if (typeof arg === 'object') {
      try {
        return JSON.stringify(arg, this.getCircularReplacer(), 2);
      } catch (e) {
        return '[Object: circular reference or unserializable]';
      }
    }
    return String(arg);
  }

  getStackTrace() {
    if (!this.enableStackTrace) return null;
    
    try {
      throw new Error();
    } catch (e) {
      return e.stack;
    }
  }

  getSourceLocation(stackTrace) {
    if (!stackTrace) return null;
    
    const lines = stackTrace.split('\n');
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line.includes('RealTimeDebugger') && !line.includes('console.')) {
        const match = line.match(/at\s+(.+?)\s+\((.+):(\d+):(\d+)\)/);
        if (match) {
          return {
            function: match[1],
            file: match[2],
            line: parseInt(match[3]),
            column: parseInt(match[4])
          };
        }
      }
    }
    return null;
  }

  captureContext() {
    return {
      url: window.location.href,
      userAgent: navigator.userAgent,
      timestamp: Date.now(),
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      },
      memory: performance.memory ? {
        used: performance.memory.usedJSHeapSize,
        total: performance.memory.totalJSHeapSize,
        limit: performance.memory.jsHeapSizeLimit
      } : null
    };
  }

  setupErrorHandling() {
    window.addEventListener('error', (event) => {
      this.handleError({
        type: 'javascript',
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error,
        stack: event.error?.stack
      });
    });

    window.addEventListener('unhandledrejection', (event) => {
      this.handleError({
        type: 'promise',
        message: event.reason?.message || 'Unhandled Promise Rejection',
        reason: event.reason,
        stack: event.reason?.stack
      });
    });
  }

  handleError(errorInfo) {
    const errorEntry = {
      id: this.generateId(),
      timestamp: new Date().toISOString(),
      type: errorInfo.type,
      message: errorInfo.message,
      filename: errorInfo.filename,
      line: errorInfo.lineno,
      column: errorInfo.colno,
      stack: errorInfo.stack,
      context: this.captureContext(),
      frequency: this.updateErrorFrequency(errorInfo.message),
      severity: this.calculateErrorSeverity(errorInfo)
    };

    this.errors.set(errorEntry.id, errorEntry);
    this.renderErrorEntry(errorEntry);
    
    // Auto-suggest fixes for common errors
    this.suggestErrorFix(errorEntry);
  }

  calculateErrorSeverity(errorInfo) {
    let severity = 1; // Base severity
    
    // Check error patterns
    if (errorInfo.message.includes('TypeError')) severity += 2;
    if (errorInfo.message.includes('ReferenceError')) severity += 3;
    if (errorInfo.message.includes('SyntaxError')) severity += 1;
    if (errorInfo.message.includes('Network')) severity += 2;
    
    // Check if error blocks user interaction
    if (this.blocksUserInteraction(errorInfo)) severity += 2;
    
    // Check frequency
    const frequency = this.getErrorFrequency(errorInfo.message);
    if (frequency > 5) severity += 1;
    if (frequency > 10) severity += 2;
    
    return Math.min(severity, 5); // Cap at 5
  }

  async suggestErrorFix(errorEntry) {
    const commonFixes = {
      'TypeError': [
        'Check if the object exists before accessing properties',
        'Verify method exists on the object',
        'Ensure correct data type is being used'
      ],
      'ReferenceError': [
        'Check variable spelling and scope',
        'Ensure variable is declared before use',
        'Verify import/export statements'
      ],
      'Network Error': [
        'Check internet connection',
        'Verify API endpoint URL',
        'Check for CORS issues',
        'Validate request format'
      ]
    };

    const errorType = this.categorizeError(errorEntry.message);
    const suggestions = commonFixes[errorType] || ['Review code logic and syntax'];
    
    errorEntry.suggestions = suggestions;
    this.renderErrorSuggestions(errorEntry);
  }
}
```

### Interactive Breakpoint System
```javascript
class InteractiveBreakpoints {
  constructor(debugger) {
    this.debugger = debugger;
    this.breakpoints = new Map();
    this.watchedVariables = new Map();
    this.conditionalBreakpoints = new Map();
    
    this.setupBreakpointInterface();
  }

  addBreakpoint(file, line, condition = null) {
    const id = `${file}:${line}`;
    const breakpoint = {
      id: id,
      file: file,
      line: line,
      condition: condition,
      enabled: true,
      hitCount: 0,
      created: new Date().toISOString()
    };

    this.breakpoints.set(id, breakpoint);
    this.instrumentCode(file, line, breakpoint);
    this.renderBreakpoint(breakpoint);
    
    return breakpoint;
  }

  addWatchVariable(variableName, scope = 'global') {
    const watchId = `${scope}.${variableName}`;
    const watch = {
      id: watchId,
      variable: variableName,
      scope: scope,
      previousValue: this.getVariableValue(variableName, scope),
      enabled: true,
      changeCount: 0
    };

    this.watchedVariables.set(watchId, watch);
    this.setupVariableWatcher(watch);
    
    return watch;
  }

  instrumentCode(file, line, breakpoint) {
    // This would typically require source map support
    // For demonstration, we'll use a simpler approach
    const originalFunction = this.findFunctionAtLine(file, line);
    if (originalFunction) {
      this.wrapFunctionWithBreakpoint(originalFunction, breakpoint);
    }
  }

  triggerBreakpoint(breakpoint, context) {
    if (!breakpoint.enabled) return;
    
    // Check condition if exists
    if (breakpoint.condition && !this.evaluateCondition(breakpoint.condition, context)) {
      return;
    }

    breakpoint.hitCount++;
    
    const debugContext = {
      breakpoint: breakpoint,
      localVariables: this.captureLocalVariables(context),
      stackTrace: this.getStackTrace(),
      timestamp: new Date().toISOString()
    };

    this.pauseExecution(debugContext);
    this.showDebugInterface(debugContext);
  }

  pauseExecution(context) {
    // Simulate paused execution
    this.isPaused = true;
    this.pausedContext = context;
    
    // Show interactive debug interface
    this.showInteractiveDebugger(context);
  }

  showInteractiveDebugger(context) {
    const debuggerInterface = document.createElement('div');
    debuggerInterface.className = 'interactive-debugger-overlay';
    debuggerInterface.innerHTML = `
      <div class="debugger-panel">
        <h3>Execution Paused</h3>
        <div class="breakpoint-info">
          <strong>File:</strong> ${context.breakpoint.file}<br>
          <strong>Line:</strong> ${context.breakpoint.line}<br>
          <strong>Hit Count:</strong> ${context.breakpoint.hitCount}
        </div>
        
        <div class="variable-inspector">
          <h4>Local Variables</h4>
          <div id="local-variables"></div>
        </div>
        
        <div class="stack-trace">
          <h4>Call Stack</h4>
          <div id="call-stack"></div>
        </div>
        
        <div class="debugger-controls">
          <button onclick="this.continueExecution()">Continue (F8)</button>
          <button onclick="this.stepOver()">Step Over (F10)</button>
          <button onclick="this.stepInto()">Step Into (F11)</button>
          <button onclick="this.stepOut()">Step Out (Shift+F11)</button>
        </div>
        
        <div class="console-eval">
          <input type="text" id="eval-input" placeholder="Evaluate expression...">
          <button onclick="this.evaluateExpression()">Evaluate</button>
          <div id="eval-output"></div>
        </div>
      </div>
    `;
    
    document.body.appendChild(debuggerInterface);
    this.populateVariableInspector(context.localVariables);
    this.populateCallStack(context.stackTrace);
  }

  evaluateExpression(expression) {
    try {
      const result = eval(expression);
      return {
        success: true,
        result: result,
        type: typeof result
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
}
```

### Automated Troubleshooting Assistant
```javascript
class TroubleshootingAssistant {
  constructor(debugger) {
    this.debugger = debugger;
    this.knowledgeBase = new Map();
    this.solutionCache = new Map();
    this.userFeedback = [];
    
    this.initializeKnowledgeBase();
  }

  initializeKnowledgeBase() {
    // Common error patterns and solutions
    this.knowledgeBase.set('TypeError: Cannot read property', {
      category: 'null-reference',
      commonCauses: [
        'Object is null or undefined',
        'Asynchronous operation not completed',
        'Property name misspelled',
        'Object structure changed'
      ],
      solutions: [
        'Add null/undefined checks before property access',
        'Use optional chaining operator (?.)',
        'Ensure async operations complete before access',
        'Verify object structure matches expectations'
      ],
      codeExamples: [
        'if (obj && obj.property) { /* safe access */ }',
        'const value = obj?.property?.nestedProperty;',
        'await asyncFunction().then(result => result.property);'
      ]
    });

    this.knowledgeBase.set('ReferenceError: variable is not defined', {
      category: 'scope-issue',
      commonCauses: [
        'Variable declared in different scope',
        'Typo in variable name',
        'Variable not imported',
        'Hoisting issue'
      ],
      solutions: [
        'Check variable spelling and case',
        'Verify variable is in correct scope',
        'Add proper import/export statements',
        'Move variable declaration before use'
      ]
    });
  }

  async analyzeProblem(errorContext) {
    const analysis = {
      errorType: this.categorizeError(errorContext),
      severity: this.assessSeverity(errorContext),
      scope: this.determineScope(errorContext),
      frequency: this.getErrorFrequency(errorContext),
      relatedErrors: this.findRelatedErrors(errorContext),
      suggestedSolutions: await this.generateSolutions(errorContext)
    };

    return analysis;
  }

  async generateSolutions(errorContext) {
    const solutions = [];
    
    // Check knowledge base for known patterns
    const knownSolution = this.findKnownSolution(errorContext);
    if (knownSolution) {
      solutions.push({
        type: 'known-pattern',
        confidence: 0.9,
        solution: knownSolution,
        automated: this.canAutomate(knownSolution)
      });
    }

    // AI-powered analysis for unknown issues
    if (solutions.length === 0) {
      const aiSolution = await this.getAISolution(errorContext);
      if (aiSolution) {
        solutions.push({
          type: 'ai-generated',
          confidence: aiSolution.confidence,
          solution: aiSolution,
          automated: false
        });
      }
    }

    // Context-specific solutions
    const contextSolutions = this.generateContextualSolutions(errorContext);
    solutions.push(...contextSolutions);

    return solutions.sort((a, b) => b.confidence - a.confidence);
  }

  async getAISolution(errorContext) {
    const prompt = `
      Analyze this JavaScript error and provide troubleshooting guidance:
      
      Error: ${errorContext.message}
      File: ${errorContext.filename}:${errorContext.line}:${errorContext.column}
      Stack: ${errorContext.stack}
      
      Context:
      - Browser: ${navigator.userAgent}
      - URL: ${window.location.href}
      - Time: ${errorContext.timestamp}
      
      Please provide:
      1. Root cause analysis
      2. Step-by-step debugging approach
      3. Specific code fixes
      4. Prevention strategies
      5. Related best practices
      
      Format as actionable troubleshooting steps.
    `;

    try {
      const response = await this.callAIService(prompt);
      return {
        analysis: response.analysis,
        steps: response.steps,
        codeExamples: response.codeExamples,
        confidence: response.confidence || 0.7
      };
    } catch (error) {
      console.warn('AI analysis failed:', error);
      return null;
    }
  }

  createInteractiveFix(solution) {
    if (!solution.automated) return null;

    return {
      title: solution.solution.title,
      description: solution.solution.description,
      steps: solution.solution.steps.map(step => ({
        description: step,
        action: this.createAutomatedAction(step),
        completed: false
      })),
      apply: () => this.applySolution(solution)
    };
  }

  async applySolution(solution) {
    const results = [];
    
    for (const step of solution.solution.steps) {
      try {
        const result = await this.executeStep(step);
        results.push({
          step: step,
          success: true,
          result: result
        });
      } catch (error) {
        results.push({
          step: step,
          success: false,
          error: error.message
        });
        break; // Stop on first failure
      }
    }

    return results;
  }

  generateTroubleshootingReport(analysis, solutions, actions) {
    return {
      timestamp: new Date().toISOString(),
      problem: analysis,
      solutions: solutions,
      actionsApplied: actions,
      resolution: this.assessResolution(actions),
      recommendations: this.generateRecommendations(analysis, solutions)
    };
  }
}
```

## 🚀 AI/LLM Integration Opportunities

### Intelligent Debug Assistant
```javascript
class AIDebugAssistant {
  async analyzeDebugSession(debugLogs, errorContext) {
    const prompt = `
      Analyze this debugging session and provide insights:
      
      Error Context: ${JSON.stringify(errorContext)}
      Debug Logs: ${JSON.stringify(debugLogs.slice(-50))}
      
      Provide:
      1. Root cause analysis with confidence level
      2. Step-by-step debugging strategy
      3. Code fixes with explanations
      4. Test cases to prevent regression
      5. Performance impact assessment
      6. Best practices to prevent similar issues
      
      Format as an interactive debugging guide.
    `;

    return await this.sendToAI(prompt);
  }

  async generateTestCases(errorAnalysis) {
    const prompt = `
      Generate comprehensive test cases for this error scenario:
      
      ${JSON.stringify(errorAnalysis)}
      
      Create:
      1. Unit tests to reproduce the bug
      2. Integration tests for related functionality
      3. Edge case tests
      4. Performance regression tests
      5. User acceptance test scenarios
      
      Include both positive and negative test cases.
    `;

    return await this.sendToAI(prompt);
  }

  async optimizeDebuggingWorkflow(debugHistory) {
    const prompt = `
      Analyze debugging patterns and suggest optimizations:
      
      Debug History: ${JSON.stringify(debugHistory)}
      
      Recommend:
      1. Debugging workflow improvements
      2. Preventive coding practices
      3. Better logging strategies
      4. Tool configuration optimizations
      5. Team debugging best practices
      
      Focus on reducing time-to-resolution.
    `;

    return await this.sendToAI(prompt);
  }
}
```

## 💡 Key Highlights

### Real-Time Debugging Features
- **Interactive Console**: Live JavaScript execution and evaluation
- **Breakpoint Management**: Conditional breakpoints with hit counts
- **Variable Watching**: Real-time variable state monitoring
- **Stack Trace Analysis**: Complete call stack inspection
- **Source Map Support**: Original source location mapping

### Unity Debugging Applications
- **WebGL Debugging**: Debug Unity web builds in browser environment
- **Remote Debugging**: Debug Unity mobile builds remotely
- **Performance Profiling**: Real-time Unity performance monitoring
- **Asset Pipeline Debugging**: Track Unity asset processing issues
- **Build Process Monitoring**: Debug Unity build and deployment processes

### Automated Troubleshooting
- **Pattern Recognition**: Identify common error patterns automatically
- **Solution Suggestions**: AI-powered fix recommendations
- **Automated Fixes**: One-click solutions for common issues
- **Knowledge Base**: Continuously learning from resolved issues
- **Interactive Guides**: Step-by-step troubleshooting workflows

### Advanced Debugging Techniques
- **Memory Leak Detection**: Identify and track memory leaks
- **Performance Bottlenecks**: Real-time performance issue identification
- **Network Request Debugging**: Monitor and analyze API calls
- **Error Correlation**: Link related errors and issues
- **Predictive Analysis**: Anticipate potential issues before they occur

### Career Development Value
- **Advanced Debugging Skills**: Demonstrate sophisticated debugging capabilities
- **Problem-Solving Methodology**: Show systematic approach to troubleshooting
- **Tool Development**: Display ability to build debugging tools
- **AI Integration**: Highlight modern AI-assisted development practices
- **Performance Engineering**: Show expertise in performance debugging and optimization