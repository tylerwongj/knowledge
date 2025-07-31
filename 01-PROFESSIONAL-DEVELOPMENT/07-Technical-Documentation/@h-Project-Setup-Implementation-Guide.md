# @h-Project Setup & Implementation Guide

## 🎯 Learning Objectives
- Master complete HTML log tracking system setup from scratch
- Implement production-ready logging infrastructure with best practices
- Create scalable deployment strategies for various environments
- Build comprehensive testing and maintenance workflows

## 🔧 Project Setup Implementation

### Initial Project Structure
```
html-log-tracking/
├── src/
│   ├── core/
│   │   ├── logger.js              # Core logging engine
│   │   ├── storage.js             # Storage management
│   │   ├── analytics.js           # Analytics engine
│   │   └── security.js            # Security features
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── dashboard.js       # Main dashboard
│   │   │   ├── charts.js          # Chart components
│   │   │   └── dashboard.css      # Dashboard styles
│   │   ├── debug/
│   │   │   ├── debugger.js        # Debug interface
│   │   │   ├── breakpoints.js     # Breakpoint system
│   │   │   └── debug.css          # Debug styles
│   │   └── export/
│   │       ├── exporter.js        # Export functionality
│   │       ├── formats.js         # Export formats
│   │       └── integrations.js    # Third-party integrations
│   ├── utils/
│   │   ├── helpers.js             # Utility functions
│   │   ├── validators.js          # Data validation
│   │   └── formatters.js          # Data formatting
│   └── assets/
│       ├── css/
│       │   ├── main.css           # Main styles
│       │   ├── themes.css         # Color themes
│       │   └── responsive.css     # Responsive design
│       ├── js/
│       │   └── vendor/            # Third-party libraries
│       └── icons/                 # Icon assets
├── config/
│   ├── development.js             # Development configuration
│   ├── production.js              # Production configuration
│   └── test.js                    # Test configuration
├── tests/
│   ├── unit/
│   │   ├── logger.test.js         # Logger unit tests
│   │   ├── analytics.test.js      # Analytics tests
│   │   └── security.test.js       # Security tests
│   ├── integration/
│   │   ├── dashboard.test.js      # Dashboard integration tests
│   │   └── export.test.js         # Export tests
│   └── e2e/
│       ├── logging-flow.test.js   # End-to-end tests
│       └── performance.test.js    # Performance tests
├── docs/
│   ├── api.md                     # API documentation
│   ├── setup.md                  # Setup instructions
│   └── examples/                  # Usage examples
├── examples/
│   ├── basic-usage/               # Basic implementation
│   ├── unity-integration/         # Unity examples
│   └── advanced-features/         # Advanced examples
├── package.json                   # Node.js dependencies
├── webpack.config.js              # Build configuration
├── .eslintrc.js                   # Code linting rules
├── .gitignore                     # Git ignore rules
└── README.md                      # Project documentation
```

### Package Configuration
```json
{
  "name": "html-log-tracking",
  "version": "1.0.0",
  "description": "Comprehensive HTML-based log tracking and analytics system",
  "main": "src/core/logger.js",
  "scripts": {
    "dev": "webpack serve --mode development",
    "build": "webpack --mode production",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "lint": "eslint src/",
    "lint:fix": "eslint src/ --fix",
    "docs": "jsdoc src/ -d docs/api",
    "analyze": "webpack-bundle-analyzer dist/stats.json"
  },
  "dependencies": {
    "chart.js": "^4.4.0",
    "date-fns": "^2.30.0",
    "compression": "^1.7.4",
    "crypto-js": "^4.2.0"
  },
  "devDependencies": {
    "webpack": "^5.89.0",
    "webpack-cli": "^5.1.4",
    "webpack-dev-server": "^4.15.1",
    "webpack-bundle-analyzer": "^4.10.1",
    "babel-loader": "^9.1.3",
    "css-loader": "^6.8.1",
    "style-loader": "^3.3.3",
    "mini-css-extract-plugin": "^2.7.6",
    "html-webpack-plugin": "^5.5.3",
    "jest": "^29.7.0",
    "eslint": "^8.54.0",
    "jsdoc": "^4.0.2",
    "puppeteer": "^21.5.2"
  },
  "keywords": [
    "logging",
    "analytics",
    "html",
    "javascript",
    "debugging",
    "monitoring",
    "unity",
    "performance"
  ],
  "author": "Your Name",
  "license": "MIT"
}
```

### Webpack Build Configuration
```javascript
// webpack.config.js
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  
  return {
    entry: {
      main: './src/index.js',
      dashboard: './src/components/dashboard/dashboard.js',
      debug: './src/components/debug/debugger.js'
    },
    
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: isProduction ? '[name].[contenthash].js' : '[name].js',
      clean: true,
      library: {
        name: 'HTMLLogTracker',
        type: 'umd'
      }
    },
    
    module: {
      rules: [
        {
          test: /\.js$/,
          exclude: /node_modules/,
          use: {
            loader: 'babel-loader',
            options: {
              presets: ['@babel/preset-env']
            }
          }
        },
        {
          test: /\.css$/,
          use: [
            isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
            'css-loader'
          ]
        },
        {
          test: /\.(png|svg|jpg|jpeg|gif)$/i,
          type: 'asset/resource'
        }
      ]
    },
    
    plugins: [
      new HtmlWebpackPlugin({
        template: './src/index.html',
        chunks: ['main']
      }),
      new HtmlWebpackPlugin({
        template: './src/dashboard.html',
        filename: 'dashboard.html',
        chunks: ['dashboard']
      }),
      ...(isProduction ? [
        new MiniCssExtractPlugin({
          filename: '[name].[contenthash].css'
        })
      ] : []),
      ...(process.env.ANALYZE ? [
        new BundleAnalyzerPlugin()
      ] : [])
    ],
    
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all'
          }
        }
      }
    },
    
    devServer: {
      static: {
        directory: path.join(__dirname, 'dist')
      },
      compress: true,
      port: 8080,
      hot: true,
      open: true
    },
    
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
        '@components': path.resolve(__dirname, 'src/components'),
        '@utils': path.resolve(__dirname, 'src/utils')
      }
    }
  };
};
```

### Core Logger Implementation
```javascript
// src/core/logger.js
import { StorageManager } from './storage.js';
import { SecurityManager } from './security.js';
import { AnalyticsEngine } from './analytics.js';

/**
 * Core HTML Log Tracking System
 * @class HTMLLogTracker
 */
export class HTMLLogTracker {
  /**
   * Create a new log tracker instance
   * @param {Object} options - Configuration options
   */
  constructor(options = {}) {
    this.config = this.mergeConfig(options);
    this.logs = [];
    this.listeners = new Map();
    this.plugins = new Map();
    
    // Initialize core components
    this.storage = new StorageManager(this.config.storage);
    this.security = new SecurityManager(this.config.security);
    this.analytics = new AnalyticsEngine(this.config.analytics);
    
    this.init();
  }

  /**
   * Merge user configuration with defaults
   * @param {Object} userConfig - User configuration
   * @returns {Object} Merged configuration
   */
  mergeConfig(userConfig) {
    const defaultConfig = {
      level: 'info',
      maxEntries: 1000,
      autoFlush: true,
      flushInterval: 30000,
      enableAnalytics: true,
      enableSecurity: true,
      storage: {
        type: 'localStorage',
        key: 'html-log-tracker',
        encrypt: false
      },
      security: {
        sanitizeData: true,
        encryptSensitive: false,
        maskPatterns: [/password/i, /token/i, /secret/i]
      },
      analytics: {
        enableRealTime: true,
        batchSize: 100,
        retentionDays: 30
      },
      export: {
        formats: ['json', 'csv'],
        compression: true
      }
    };

    return this.deepMerge(defaultConfig, userConfig);
  }

  /**
   * Initialize the logger
   */
  init() {
    this.sessionId = this.generateSessionId();
    this.startTime = new Date().toISOString();
    
    // Load existing logs from storage
    this.loadFromStorage();
    
    // Setup automatic cleanup
    this.setupCleanup();
    
    // Setup global error handlers
    this.setupErrorHandlers();
    
    // Start analytics if enabled
    if (this.config.enableAnalytics) {
      this.analytics.start();
    }
    
    // Setup auto-flush if enabled
    if (this.config.autoFlush) {
      this.setupAutoFlush();
    }

    this.log('info', 'HTML Log Tracker initialized', {
      sessionId: this.sessionId,
      config: this.sanitizeConfig(this.config)
    });
  }

  /**
   * Log a message
   * @param {string} level - Log level (debug, info, warn, error)
   * @param {string} message - Log message
   * @param {Object} context - Additional context data
   * @returns {Object} Log entry
   */
  log(level, message, context = {}) {
    if (!this.shouldLog(level)) {
      return null;
    }

    const logEntry = this.createLogEntry(level, message, context);
    
    // Apply security measures
    if (this.config.enableSecurity) {
      this.security.sanitizeLogEntry(logEntry);
    }
    
    // Add to logs array
    this.logs.push(logEntry);
    
    // Maintain max entries limit
    if (this.logs.length > this.config.maxEntries) {
      this.logs.shift();
    }
    
    // Save to storage
    this.saveToStorage();
    
    // Update analytics
    if (this.config.enableAnalytics) {
      this.analytics.processLogEntry(logEntry);
    }
    
    // Emit event for listeners
    this.emit('log', logEntry);
    
    return logEntry;
  }

  /**
   * Create a log entry object
   * @param {string} level - Log level
   * @param {string} message - Log message
   * @param {Object} context - Context data
   * @returns {Object} Log entry
   */
  createLogEntry(level, message, context) {
    return {
      id: this.generateId(),
      timestamp: new Date().toISOString(),
      level: level,
      message: message,
      context: context,
      sessionId: this.sessionId,
      url: window.location.href,
      userAgent: navigator.userAgent,
      stackTrace: this.captureStackTrace(),
      performance: this.capturePerformanceMetrics()
    };
  }

  /**
   * Add event listener
   * @param {string} event - Event name
   * @param {Function} callback - Callback function
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  /**
   * Remove event listener
   * @param {string} event - Event name
   * @param {Function} callback - Callback function
   */
  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  /**
   * Emit event to listeners
   * @param {string} event - Event name
   * @param {*} data - Event data
   */
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in event listener:', error);
        }
      });
    }
  }

  /**
   * Export logs in specified format
   * @param {string} format - Export format (json, csv, xml)
   * @param {Object} options - Export options
   * @returns {Promise<string>} Exported data
   */
  async export(format = 'json', options = {}) {
    const exporter = await import('@components/export/exporter.js');
    return exporter.exportLogs(this.logs, format, options);
  }

  /**
   * Clear all logs
   */
  clear() {
    this.logs = [];
    this.storage.clear();
    this.analytics.reset();
    this.emit('clear');
  }

  /**
   * Get analytics data
   * @returns {Object} Analytics data
   */
  getAnalytics() {
    return this.analytics.getAnalytics();
  }

  /**
   * Install plugin
   * @param {string} name - Plugin name
   * @param {Object} plugin - Plugin instance
   */
  use(name, plugin) {
    this.plugins.set(name, plugin);
    if (typeof plugin.install === 'function') {
      plugin.install(this);
    }
  }

  // Convenience methods
  debug(message, context) { return this.log('debug', message, context); }
  info(message, context) { return this.log('info', message, context); }
  warn(message, context) { return this.log('warn', message, context); }
  error(message, context) { return this.log('error', message, context); }

  // Private methods
  shouldLog(level) {
    const levels = { debug: 0, info: 1, warn: 2, error: 3 };
    return levels[level] >= levels[this.config.level];
  }

  generateSessionId() {
    return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  generateId() {
    return `log-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  captureStackTrace() {
    try {
      throw new Error();
    } catch (e) {
      return e.stack;
    }
  }

  capturePerformanceMetrics() {
    if (!window.performance) return null;
    
    return {
      timing: window.performance.timing,
      memory: window.performance.memory,
      navigation: window.performance.navigation
    };
  }

  loadFromStorage() {
    const stored = this.storage.load();
    if (stored && Array.isArray(stored.logs)) {
      this.logs = stored.logs;
    }
  }

  saveToStorage() {
    this.storage.save({
      logs: this.logs,
      metadata: {
        sessionId: this.sessionId,
        lastUpdated: new Date().toISOString()
      }
    });
  }

  setupCleanup() {
    // Clean up old logs periodically
    setInterval(() => {
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - this.config.analytics.retentionDays);
      
      this.logs = this.logs.filter(log => 
        new Date(log.timestamp) > cutoffDate
      );
      
      this.saveToStorage();
    }, 86400000); // Daily cleanup
  }

  setupErrorHandlers() {
    window.addEventListener('error', (event) => {
      this.error('JavaScript Error', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error
      });
    });

    window.addEventListener('unhandledrejection', (event) => {
      this.error('Unhandled Promise Rejection', {
        reason: event.reason,
        promise: event.promise
      });
    });
  }

  setupAutoFlush() {
    setInterval(() => {
      this.saveToStorage();
    }, this.config.flushInterval);
  }

  deepMerge(target, source) {
    for (const key in source) {
      if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
        target[key] = this.deepMerge(target[key] || {}, source[key]);
      } else {
        target[key] = source[key];
      }
    }
    return target;
  }

  sanitizeConfig(config) {
    const sanitized = { ...config };
    delete sanitized.security;
    return sanitized;
  }
}

// Export default instance
export default new HTMLLogTracker();
```

### Testing Setup
```javascript
// tests/unit/logger.test.js
import { HTMLLogTracker } from '../../src/core/logger.js';

describe('HTMLLogTracker', () => {
  let logger;

  beforeEach(() => {
    logger = new HTMLLogTracker({
      storage: { type: 'memory' },
      enableAnalytics: false,
      enableSecurity: false
    });
  });

  afterEach(() => {
    logger.clear();
  });

  describe('Basic Logging', () => {
    test('should create log entry with correct structure', () => {
      const entry = logger.info('Test message', { test: true });
      
      expect(entry).toHaveProperty('id');
      expect(entry).toHaveProperty('timestamp');
      expect(entry.level).toBe('info');
      expect(entry.message).toBe('Test message');
      expect(entry.context.test).toBe(true);
    });

    test('should respect log level filtering', () => {
      logger.config.level = 'warn';
      
      const debugEntry = logger.debug('Debug message');
      const infoEntry = logger.info('Info message');
      const warnEntry = logger.warn('Warning message');
      
      expect(debugEntry).toBeNull();
      expect(infoEntry).toBeNull();
      expect(warnEntry).toBeTruthy();
    });

    test('should maintain maximum entries limit', () => {
      logger.config.maxEntries = 3;
      
      logger.info('Message 1');
      logger.info('Message 2');
      logger.info('Message 3');
      logger.info('Message 4');
      
      expect(logger.logs).toHaveLength(3);
      expect(logger.logs[0].message).toBe('Message 2');
    });
  });

  describe('Event System', () => {
    test('should emit log events', (done) => {
      logger.on('log', (entry) => {
        expect(entry.message).toBe('Test event');
        done();
      });
      
      logger.info('Test event');
    });

    test('should support multiple listeners', () => {
      const listener1 = jest.fn();
      const listener2 = jest.fn();
      
      logger.on('log', listener1);
      logger.on('log', listener2);
      
      logger.info('Test message');
      
      expect(listener1).toHaveBeenCalled();
      expect(listener2).toHaveBeenCalled();
    });
  });

  describe('Export Functionality', () => {
    test('should export logs as JSON', async () => {
      logger.info('Test message 1');
      logger.warn('Test message 2');
      
      const exported = await logger.export('json');
      const parsed = JSON.parse(exported);
      
      expect(Array.isArray(parsed)).toBe(true);
      expect(parsed).toHaveLength(2);
    });
  });
});
```

### Development Workflow
```javascript
// scripts/dev-setup.js
const fs = require('fs');
const path = require('path');

class DevSetup {
  constructor() {
    this.projectRoot = path.resolve(__dirname, '..');
    this.setupTasks = [
      'createDirectories',
      'copyTemplates',
      'installDependencies',
      'setupGitHooks',
      'generateDocs'
    ];
  }

  async run() {
    console.log('🚀 Setting up HTML Log Tracking development environment...\n');
    
    for (const task of this.setupTasks) {
      try {
        await this[task]();
        console.log(`✅ ${task} completed`);
      } catch (error) {
        console.error(`❌ ${task} failed:`, error.message);
        process.exit(1);
      }
    }
    
    console.log('\n🎉 Development environment setup complete!');
    console.log('\nNext steps:');
    console.log('  npm run dev     # Start development server');
    console.log('  npm test        # Run tests');
    console.log('  npm run build   # Build for production');
  }

  async createDirectories() {
    const dirs = [
      'src/core',
      'src/components/dashboard',
      'src/components/debug',
      'src/components/export',
      'src/utils',
      'src/assets/css',
      'src/assets/js/vendor',
      'src/assets/icons',
      'config',
      'tests/unit',
      'tests/integration',
      'tests/e2e',
      'docs',
      'examples/basic-usage',
      'examples/unity-integration',
      'examples/advanced-features',
      'dist'
    ];

    for (const dir of dirs) {
      const fullPath = path.join(this.projectRoot, dir);
      if (!fs.existsSync(fullPath)) {
        fs.mkdirSync(fullPath, { recursive: true });
      }
    }
  }

  async copyTemplates() {
    const templates = {
      'templates/index.html': 'src/index.html',
      'templates/dashboard.html': 'src/dashboard.html',
      'templates/example.html': 'examples/basic-usage/index.html'
    };

    for (const [src, dest] of Object.entries(templates)) {
      const srcPath = path.join(this.projectRoot, src);
      const destPath = path.join(this.projectRoot, dest);
      
      if (fs.existsSync(srcPath)) {
        fs.copyFileSync(srcPath, destPath);
      }
    }
  }

  async installDependencies() {
    const { execSync } = require('child_process');
    console.log('Installing dependencies...');
    execSync('npm install', { stdio: 'inherit', cwd: this.projectRoot });
  }

  async setupGitHooks() {
    const hookScript = `#!/bin/sh
npm run lint
npm test
`;
    
    const hookPath = path.join(this.projectRoot, '.git/hooks/pre-commit');
    fs.writeFileSync(hookPath, hookScript);
    fs.chmodSync(hookPath, '755');
  }

  async generateDocs() {
    const { execSync } = require('child_process');
    try {
      execSync('npm run docs', { stdio: 'inherit', cwd: this.projectRoot });
    } catch (error) {
      console.warn('Documentation generation failed, skipping...');
    }
  }
}

// Run setup if called directly
if (require.main === module) {
  new DevSetup().run();
}

module.exports = DevSetup;
```

## 🚀 AI/LLM Integration Opportunities

### Automated Setup Assistant
```javascript
class AISetupAssistant {
  async generateProjectConfiguration(requirements) {
    const prompt = `
      Generate optimal configuration for HTML log tracking project:
      
      Requirements: ${JSON.stringify(requirements)}
      
      Provide:
      1. Webpack configuration optimization
      2. Performance settings recommendations
      3. Security configuration based on use case
      4. Storage strategy recommendations
      5. Testing strategy suggestions
      6. Deployment configuration
      
      Focus on production-ready, scalable solutions.
    `;

    return await this.sendToAI(prompt);
  }

  async optimizeBuildProcess(buildMetrics, projectSize) {
    const prompt = `
      Optimize build process based on metrics:
      
      Build Metrics: ${JSON.stringify(buildMetrics)}
      Project Size: ${projectSize}
      
      Suggest:
      1. Bundle optimization strategies
      2. Code splitting improvements
      3. Asset optimization techniques
      4. Build performance optimizations
      5. Development workflow improvements
      
      Provide specific webpack and tooling configurations.
    `;

    return await this.sendToAI(prompt);
  }
}
```

## 💡 Key Highlights

### Production-Ready Features
- **Modular Architecture**: Clean separation of concerns with plugin system
- **Build Optimization**: Webpack configuration with code splitting and optimization
- **Testing Suite**: Comprehensive unit, integration, and E2E testing
- **Development Tools**: Linting, formatting, and automated documentation
- **CI/CD Ready**: GitHub Actions, Docker, and deployment configurations

### Scalability Considerations
- **Performance Optimization**: Efficient memory usage and processing
- **Storage Strategies**: Multiple storage backends with encryption support
- **Plugin Architecture**: Extensible system for custom functionality
- **Configuration Management**: Environment-specific configurations
- **Error Handling**: Robust error recovery and reporting

### Unity Integration Setup
- **WebGL Bridge**: Seamless Unity to HTML logging communication
- **Cross-Platform Support**: Mobile, desktop, and web Unity builds
- **Performance Monitoring**: Unity-specific performance metrics
- **Game Analytics**: Player behavior and game event tracking
- **Debug Tools**: Unity-specific debugging interfaces

### Career Development Applications
- **Full-Stack Development**: Demonstrate end-to-end project capabilities
- **DevOps Integration**: Show CI/CD and deployment expertise
- **Code Quality**: Highlight testing, linting, and documentation practices
- **Performance Engineering**: Display optimization and scalability skills
- **Project Management**: Show ability to structure and organize complex projects

### Deployment Strategies
- **CDN Distribution**: Global content delivery optimization
- **Docker Containerization**: Scalable container deployment
- **Cloud Integration**: AWS, Azure, GCP deployment options
- **Monitoring Integration**: Production monitoring and alerting
- **A/B Testing**: Feature flag and testing infrastructure