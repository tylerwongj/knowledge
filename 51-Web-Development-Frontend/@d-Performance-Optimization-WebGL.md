# @d-Performance Optimization WebGL - Unity Web Build Performance Mastery

## 🎯 Learning Objectives
- Master Unity WebGL build optimization techniques for web deployment
- Implement advanced web performance monitoring and Core Web Vitals optimization
- Create efficient loading strategies for Unity games in web browsers
- Develop AI-automated performance testing and optimization workflows
- Build high-performance web interfaces that complement Unity WebGL builds

## ⚡ Unity WebGL Optimization Fundamentals

### Build Configuration Optimization
```csharp
// Unity Build Settings Optimization (C# Editor Script)
using UnityEngine;
using UnityEditor;
using UnityEditor.Build.Reporting;

public class WebGLBuildOptimizer : EditorWindow
{
    [MenuItem("Tools/WebGL Build Optimizer")]
    public static void ShowWindow()
    {
        GetWindow<WebGLBuildOptimizer>("WebGL Optimizer");
    }

    void OnGUI()
    {
        GUILayout.Label("Unity WebGL Build Optimization", EditorStyles.boldLabel);
        
        if (GUILayout.Button("Apply Optimal WebGL Settings"))
        {
            ApplyOptimalSettings();
        }
        
        if (GUILayout.Button("Build Optimized WebGL"))
        {
            BuildOptimizedWebGL();
        }
    }

    static void ApplyOptimalSettings()
    {
        // Player Settings Optimization
        PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Brotli;
        PlayerSettings.WebGL.decompressionFallback = true;
        PlayerSettings.WebGL.dataCaching = true;
        PlayerSettings.WebGL.debugSymbols = false;
        
        // Memory Settings
        PlayerSettings.WebGL.memorySize = 512; // MB - adjust based on game needs
        PlayerSettings.WebGL.exceptionSupport = WebGLExceptionSupport.None;
        PlayerSettings.WebGL.nameFilesAsHashes = true;
        
        // Optimization Settings
        PlayerSettings.stripEngineCode = true;
        PlayerSettings.managedStrippingLevel = ManagedStrippingLevel.High;
        PlayerSettings.WebGL.template = "PROJECT:Better2020"; // Custom template
        
        // Graphics Settings
        var graphicsSettings = AssetDatabase.LoadAssetAtPath<GraphicsSettings>("ProjectSettings/GraphicsSettings.asset");
        
        Debug.Log("Optimal WebGL settings applied!");
    }

    static void BuildOptimizedWebGL()
    {
        string buildPath = "Builds/WebGL-Optimized";
        
        BuildPlayerOptions buildOptions = new BuildPlayerOptions
        {
            scenes = EditorBuildSettings.scenes.Select(s => s.path).ToArray(),
            locationPathName = buildPath,
            target = BuildTarget.WebGL,
            options = BuildOptions.None
        };
        
        // Apply additional optimizations
        EditorUserBuildSettings.webGLOptimizationLevel = 2;
        EditorUserBuildSettings.webGLUseEmbeddedResources = false;
        
        BuildReport report = BuildPipeline.BuildPlayer(buildOptions);
        
        if (report.summary.result == BuildResult.Succeeded)
        {
            Debug.Log($"WebGL build succeeded! Size: {report.summary.totalSize} bytes");
            PostBuildOptimization(buildPath);
        }
        else
        {
            Debug.LogError("WebGL build failed!");
        }
    }
    
    static void PostBuildOptimization(string buildPath)
    {
        // Additional post-build optimizations
        string buildFilesPath = Path.Combine(buildPath, "Build");
        
        // Compress additional assets
        CompressAssets(buildFilesPath);
        
        // Generate performance hints
        GeneratePerformanceReport(buildPath);
    }
}
```

### Advanced Asset Optimization
```csharp
// Asset Processing Pipeline for WebGL
public class WebGLAssetProcessor : AssetPostprocessor
{
    void OnPreprocessTexture()
    {
        if (assetImporter.assetPath.Contains("WebGL"))
        {
            TextureImporter textureImporter = (TextureImporter)assetImporter;
            
            // WebGL-specific texture settings
            var platformSettings = new TextureImporterPlatformSettings
            {
                name = "WebGL",
                overridden = true,
                maxTextureSize = 1024, // Reduce for web
                format = TextureImporterFormat.DXT5, // Good compression
                compressionQuality = 50, // Balance quality/size
                allowsAlphaSplitting = true
            };
            
            textureImporter.SetPlatformTextureSettings(platformSettings);
        }
    }

    void OnPreprocessAudio()
    {
        if (assetImporter.assetPath.Contains("WebGL"))
        {
            AudioImporter audioImporter = (AudioImporter)assetImporter;
            
            // WebGL audio optimization
            var sampleSettings = new AudioImporterSampleSettings
            {
                loadType = AudioClipLoadType.CompressedInMemory,
                compressionFormat = AudioCompressionFormat.Vorbis,
                quality = 0.7f, // Good balance for web
                sampleRateSetting = AudioSampleRateSetting.OptimizeForPlatform
            };
            
            audioImporter.SetOverrideSampleSettings("WebGL", sampleSettings);
        }
    }
}
```

## 🌐 Web Performance Optimization

### Advanced Loading Strategies
```javascript
// Progressive Unity WebGL Loader with Performance Monitoring
class AdvancedUnityLoader {
    constructor(config) {
        this.config = {
            buildUrl: config.buildUrl,
            dataUrl: config.dataUrl,
            frameworkUrl: config.frameworkUrl,
            codeUrl: config.codeUrl,
            streamingAssetsUrl: config.streamingAssetsUrl || "StreamingAssets",
            ...config
        };
        
        this.metrics = {
            loadStartTime: 0,
            loadEndTime: 0,
            downloadSize: 0,
            compressionRatio: 0,
            memoryUsage: 0,
            fps: 0
        };
        
        this.instance = null;
        this.loadingCallbacks = [];
        this.performanceObserver = null;
    }

    async loadWithProgression() {
        this.metrics.loadStartTime = performance.now();
        
        try {
            // Preload critical resources
            await this.preloadCriticalResources();
            
            // Load Unity with detailed progress tracking
            this.instance = await this.createUnityInstanceWithMetrics();
            
            // Start performance monitoring
            this.startPerformanceMonitoring();
            
            this.metrics.loadEndTime = performance.now();
            return this.instance;
            
        } catch (error) {
            this.handleLoadingError(error);
            throw error;
        }
    }

    async preloadCriticalResources() {
        const resources = [
            { url: this.config.frameworkUrl, type: 'script' },
            { url: this.config.dataUrl, type: 'arraybuffer' },
            { url: this.config.codeUrl, type: 'arraybuffer' }
        ];

        const preloadPromises = resources.map(resource => 
            this.preloadResource(resource.url, resource.type)
        );

        await Promise.all(preloadPromises);
    }

    async preloadResource(url, type) {
        return new Promise((resolve, reject) => {
            if (type === 'script') {
                const link = document.createElement('link');
                link.rel = 'preload';
                link.as = 'script';
                link.href = url;
                link.onload = resolve;
                link.onerror = reject;
                document.head.appendChild(link);
            } else if (type === 'arraybuffer') {
                fetch(url, { method: 'HEAD' })
                    .then(response => {
                        this.metrics.downloadSize += parseInt(response.headers.get('content-length') || '0');
                        resolve();
                    })
                    .catch(reject);
            }
        });
    }

    async createUnityInstanceWithMetrics() {
        const canvas = document.querySelector('#unity-canvas');
        if (!canvas) throw new Error('Unity canvas not found');

        // Enhanced progress tracking
        const progressCallback = (progress) => {
            const progressPercent = Math.round(progress * 100);
            this.notifyProgress(progressPercent, 'downloading');
            
            // Update UI elements
            this.updateProgressUI(progressPercent);
        };

        // Load Unity loader script
        await this.loadUnityScript();

        // Create Unity instance with comprehensive config
        const unityInstance = await createUnityInstance(canvas, {
            dataUrl: this.config.dataUrl,
            frameworkUrl: this.config.frameworkUrl,
            codeUrl: this.config.codeUrl,
            streamingAssetsUrl: this.config.streamingAssetsUrl,
            companyName: this.config.companyName || "DefaultCompany",
            productName: this.config.productName || "Game",
            productVersion: this.config.productVersion || "1.0",
            
            // Performance optimizations
            matchWebGLToCanvasSize: true,
            devicePixelRatio: Math.min(window.devicePixelRatio, 2), // Limit for performance
            
            // Memory management
            totalMemory: this.config.memorySize * 1024 * 1024 || 268435456, // Default 256MB
            
            // Callbacks
            onProgress: progressCallback,
            onRuntimeInitialized: () => this.onRuntimeInitialized(),
        });

        return unityInstance;
    }

    loadUnityScript() {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = this.config.buildUrl + '/UnityLoader.js';
            script.onload = resolve;
            script.onerror = () => reject(new Error('Failed to load Unity script'));
            document.head.appendChild(script);
        });
    }

    onRuntimeInitialized() {
        this.notifyProgress(100, 'ready');
        
        // Initialize performance monitoring
        this.startCoreWebVitalsTracking();
        
        // Send analytics
        this.sendLoadingAnalytics();
    }

    startPerformanceMonitoring() {
        // Monitor FPS
        let frameCount = 0;
        let lastTime = performance.now();
        
        const fpsCounter = () => {
            frameCount++;
            const currentTime = performance.now();
            
            if (currentTime >= lastTime + 1000) {
                this.metrics.fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
                frameCount = 0;
                lastTime = currentTime;
                
                this.updatePerformanceUI();
            }
            
            requestAnimationFrame(fpsCounter);
        };
        
        requestAnimationFrame(fpsCounter);

        // Monitor memory usage
        if (performance.memory) {
            setInterval(() => {
                this.metrics.memoryUsage = performance.memory.usedJSHeapSize / 1048576; // MB
            }, 1000);
        }
    }

    startCoreWebVitalsTracking() {
        // Largest Contentful Paint
        new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const lastEntry = entries[entries.length - 1];
            this.metrics.lcp = lastEntry.startTime;
        }).observe({ entryTypes: ['largest-contentful-paint'] });

        // First Input Delay
        new PerformanceObserver((list) => {
            const entries = list.getEntries();
            entries.forEach(entry => {
                this.metrics.fid = entry.processingStart - entry.startTime;
            });
        }).observe({ entryTypes: ['first-input'] });

        // Cumulative Layout Shift
        let cumulativeLayoutShift = 0;
        new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (!entry.hadRecentInput) {
                    cumulativeLayoutShift += entry.value;
                }
            }
            this.metrics.cls = cumulativeLayoutShift;
        }).observe({ entryTypes: ['layout-shift'] });
    }

    updateProgressUI(progress) {
        const progressBar = document.querySelector('.unity-progress-bar');
        const progressText = document.querySelector('.unity-progress-text');
        
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
        
        if (progressText) {
            progressText.textContent = `Loading... ${progress}%`;
        }
    }

    updatePerformanceUI() {
        const performancePanel = document.querySelector('.unity-performance');
        if (performancePanel) {
            performancePanel.innerHTML = `
                <div class="metric">FPS: ${this.metrics.fps}</div>
                <div class="metric">Memory: ${this.metrics.memoryUsage.toFixed(1)}MB</div>
                <div class="metric">Load Time: ${((this.metrics.loadEndTime - this.metrics.loadStartTime) / 1000).toFixed(2)}s</div>
            `;
        }
    }

    notifyProgress(progress, stage) {
        this.loadingCallbacks.forEach(callback => {
            callback({ progress, stage, metrics: this.metrics });
        });
    }

    onProgress(callback) {
        this.loadingCallbacks.push(callback);
    }

    sendLoadingAnalytics() {
        const analyticsData = {
            loadTime: this.metrics.loadEndTime - this.metrics.loadStartTime,
            downloadSize: this.metrics.downloadSize,
            deviceInfo: {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                cores: navigator.hardwareConcurrency,
                memory: navigator.deviceMemory
            },
            performanceMetrics: this.metrics
        };

        // Send to analytics service
        this.sendAnalytics('unity_webgl_load', analyticsData);
    }

    async sendAnalytics(event, data) {
        try {
            await fetch('/api/analytics', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ event, data, timestamp: Date.now() })
            });
        } catch (error) {
            console.warn('Analytics sending failed:', error);
        }
    }

    handleLoadingError(error) {
        console.error('Unity loading failed:', error);
        
        const errorContainer = document.querySelector('.unity-error');
        if (errorContainer) {
            errorContainer.innerHTML = `
                <div class="error-message">
                    <h3>Failed to load game</h3>
                    <p>${error.message}</p>
                    <button onclick="location.reload()">Retry</button>
                </div>
            `;
            errorContainer.style.display = 'block';
        }

        // Send error analytics
        this.sendAnalytics('unity_webgl_error', {
            error: error.message,
            stack: error.stack,
            userAgent: navigator.userAgent,
            timestamp: Date.now()
        });
    }
}
```

### Compression and Caching Strategies
```javascript
// Service Worker for Unity WebGL Caching
const CACHE_NAME = 'unity-webgl-v1';
const UNITY_ASSETS = [
    '/Build/UnityLoader.js',
    '/Build/game.data',
    '/Build/game.framework.js',
    '/Build/game.wasm'
];

// Advanced caching strategy for Unity assets
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                return cache.addAll(UNITY_ASSETS);
            })
    );
});

self.addEventListener('fetch', event => {
    // Unity asset caching strategy
    if (event.request.url.includes('/Build/')) {
        event.respondWith(
            caches.match(event.request)
                .then(response => {
                    if (response) {
                        // Serve from cache
                        return response;
                    }
                    
                    // Fetch and cache with compression handling
                    return fetch(event.request)
                        .then(response => {
                            // Don't cache if not a successful response
                            if (!response || response.status !== 200 || response.type !== 'basic') {
                                return response;
                            }

                            const responseToCache = response.clone();
                            caches.open(CACHE_NAME)
                                .then(cache => {
                                    cache.put(event.request, responseToCache);
                                });

                            return response;
                        });
                })
        );
    }
    
    // Regular network-first strategy for other assets
    event.respondWith(
        fetch(event.request)
            .catch(() => caches.match(event.request))
    );
});

// Compression detection and fallback
class CompressionHandler {
    static detectSupport() {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        
        return {
            brotli: 'br' in Request.prototype,
            gzip: true, // Always supported
            webgl: !!gl,
            wasm: typeof WebAssembly === 'object',
            threads: typeof SharedArrayBuffer !== 'undefined'
        };
    }
    
    static async loadOptimalBuild(buildPath) {
        const support = this.detectSupport();
        
        let buildFiles = {
            data: `${buildPath}/game.data`,
            framework: `${buildPath}/game.framework.js`,
            code: `${buildPath}/game.wasm`
        };
        
        // Use compressed versions if supported
        if (support.brotli) {
            buildFiles.data += '.br';
            buildFiles.framework += '.br';
            buildFiles.code += '.br';
        } else if (support.gzip) {
            buildFiles.data += '.gz';
            buildFiles.framework += '.gz';
            buildFiles.code += '.gz';
        }
        
        return buildFiles;
    }
}
```

## 🚀 AI/LLM Integration for Performance

### Automated Performance Analysis
```javascript
// AI-powered Unity WebGL performance analyzer
const performancePrompts = {
    analyzeLoadingMetrics: (metrics) => `
Analyze Unity WebGL loading performance metrics and provide optimization recommendations:

Loading Metrics:
${JSON.stringify(metrics, null, 2)}

Device Information:
- User Agent: ${navigator.userAgent}
- Platform: ${navigator.platform}
- CPU Cores: ${navigator.hardwareConcurrency}
- Memory: ${navigator.deviceMemory}GB
- Connection: ${navigator.connection?.effectiveType}

Analyze:
1. Loading time bottlenecks
2. Memory usage patterns
3. Compression effectiveness
4. Core Web Vitals impact
5. Device-specific optimizations

Provide specific, actionable optimization recommendations with code examples.
`,

    optimizeBuildSettings: (buildReport) => `
Review Unity WebGL build report and suggest optimization strategies:

Build Report:
${JSON.stringify(buildReport, null, 2)}

Focus on:
1. Asset optimization opportunities
2. Code stripping improvements
3. Compression setting adjustments
4. Memory allocation optimization
5. Loading strategy improvements

Provide Unity C# code and build settings recommendations.
`,

    generatePerformanceTests: (gameSpecs) => `
Generate comprehensive performance test suite for Unity WebGL game:

Game Specifications:
${JSON.stringify(gameSpecs, null, 2)}

Create automated tests for:
1. Loading performance across devices
2. Runtime FPS stability
3. Memory leak detection
4. Core Web Vitals compliance
5. Cross-browser compatibility
6. Network condition variations

Include JavaScript test code and Unity C# performance monitoring scripts.
`
};

class AIPerformanceAnalyzer {
    constructor(aiService) {
        this.aiService = aiService;
        this.metrics = new Map();
        this.recommendations = [];
    }

    async analyzePerformance(unityLoader) {
        // Collect comprehensive metrics
        const metrics = await this.collectMetrics(unityLoader);
        
        // Get AI analysis
        const analysis = await this.aiService.analyze(
            performancePrompts.analyzeLoadingMetrics(metrics)
        );
        
        // Generate actionable recommendations
        this.recommendations = await this.generateRecommendations(analysis);
        
        return {
            metrics,
            analysis,
            recommendations: this.recommendations,
            score: this.calculatePerformanceScore(metrics)
        };
    }

    async collectMetrics(unityLoader) {
        return {
            loading: {
                totalTime: unityLoader.metrics.loadEndTime - unityLoader.metrics.loadStartTime,
                downloadSize: unityLoader.metrics.downloadSize,
                compressionRatio: unityLoader.metrics.compressionRatio
            },
            runtime: {
                averageFPS: this.calculateAverageFPS(),
                memoryUsage: unityLoader.metrics.memoryUsage,
                peakMemory: this.getPeakMemoryUsage()
            },
            webVitals: {
                lcp: unityLoader.metrics.lcp,
                fid: unityLoader.metrics.fid,
                cls: unityLoader.metrics.cls
            },
            device: {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                cores: navigator.hardwareConcurrency,
                memory: navigator.deviceMemory,
                connection: navigator.connection?.effectiveType
            },
            errors: this.getErrorLog()
        };
    }

    async generateRecommendations(analysis) {
        const recommendations = [];
        
        // Parse AI analysis for actionable items
        const lines = analysis.split('\n');
        let currentCategory = '';
        
        lines.forEach(line => {
            if (line.includes(':') && !line.startsWith(' ')) {
                currentCategory = line.split(':')[0].trim();
            } else if (line.trim().startsWith('-') || line.trim().startsWith('•')) {
                recommendations.push({
                    category: currentCategory,
                    recommendation: line.trim().substring(1).trim(),
                    priority: this.assessPriority(line),
                    implementation: this.generateImplementation(line)
                });
            }
        });
        
        return recommendations;
    }

    calculatePerformanceScore(metrics) {
        let score = 100;
        
        // Loading performance (30%)
        if (metrics.loading.totalTime > 5000) score -= 20;
        else if (metrics.loading.totalTime > 3000) score -= 10;
        
        // Runtime performance (40%)
        if (metrics.runtime.averageFPS < 30) score -= 30;
        else if (metrics.runtime.averageFPS < 50) score -= 15;
        
        // Core Web Vitals (20%)
        if (metrics.webVitals.lcp > 2500) score -= 10;
        if (metrics.webVitals.fid > 100) score -= 5;
        if (metrics.webVitals.cls > 0.1) score -= 5;
        
        // Memory usage (10%)
        if (metrics.runtime.memoryUsage > 500) score -= 10;
        else if (metrics.runtime.memoryUsage > 300) score -= 5;
        
        return Math.max(score, 0);
    }

    async optimizeBasedOnRecommendations() {
        const optimizations = [];
        
        for (const rec of this.recommendations) {
            if (rec.priority === 'high') {
                try {
                    await this.implementOptimization(rec);
                    optimizations.push({
                        ...rec,
                        status: 'implemented',
                        timestamp: Date.now()
                    });
                } catch (error) {
                    optimizations.push({
                        ...rec,
                        status: 'failed',
                        error: error.message,
                        timestamp: Date.now()
                    });
                }
            }
        }
        
        return optimizations;
    }

    async implementOptimization(recommendation) {
        switch (recommendation.category.toLowerCase()) {
            case 'compression':
                return this.optimizeCompression();
            case 'caching':
                return this.optimizeCaching();
            case 'loading':
                return this.optimizeLoading();
            case 'memory':
                return this.optimizeMemory();
            default:
                console.log(`Manual implementation required: ${recommendation.recommendation}`);
        }
    }

    // Performance optimization implementations
    async optimizeCompression() {
        // Implement compression optimization
        const compressionWorker = new Worker('/workers/compression-optimizer.js');
        return new Promise((resolve) => {
            compressionWorker.postMessage({ action: 'optimize' });
            compressionWorker.onmessage = (e) => resolve(e.data);
        });
    }

    async optimizeCaching() {
        // Update service worker with better caching strategies
        if ('serviceWorker' in navigator) {
            const registration = await navigator.serviceWorker.ready;
            registration.active?.postMessage({ action: 'updateCache' });
        }
    }

    // Additional helper methods
    calculateAverageFPS() {
        const fpsHistory = this.metrics.get('fpsHistory') || [];
        return fpsHistory.length > 0 
            ? fpsHistory.reduce((a, b) => a + b, 0) / fpsHistory.length 
            : 0;
    }

    getPeakMemoryUsage() {
        const memoryHistory = this.metrics.get('memoryHistory') || [];
        return memoryHistory.length > 0 ? Math.max(...memoryHistory) : 0;
    }

    getErrorLog() {
        return this.metrics.get('errors') || [];
    }

    assessPriority(recommendation) {
        const highPriorityKeywords = ['critical', 'major', 'significant', 'urgent'];
        const mediumPriorityKeywords = ['moderate', 'important', 'noticeable'];
        
        const text = recommendation.toLowerCase();
        
        if (highPriorityKeywords.some(keyword => text.includes(keyword))) {
            return 'high';
        } else if (mediumPriorityKeywords.some(keyword => text.includes(keyword))) {
            return 'medium';
        }
        
        return 'low';
    }

    generateImplementation(recommendation) {
        // Generate implementation steps based on recommendation content
        return {
            steps: ['Analyze current implementation', 'Apply optimization', 'Test performance'],
            estimatedTime: '30 minutes',
            difficulty: 'medium'
        };
    }
}
```

## 💡 Key Highlights

### Unity WebGL Performance Essentials
- **Build Optimization**: Proper compression, stripping, and asset optimization
- **Loading Strategies**: Progressive loading with detailed progress tracking
- **Memory Management**: Efficient memory allocation and cleanup
- **Core Web Vitals**: Optimize for LCP, FID, and CLS metrics

### Advanced Web Performance Techniques
- **Service Workers**: Intelligent caching strategies for Unity assets
- **Compression**: Brotli/Gzip support with automatic fallbacks
- **Progressive Enhancement**: Graceful degradation for different device capabilities
- **Performance Monitoring**: Real-time FPS, memory, and Core Web Vitals tracking

### AI-Powered Optimization
- **Automated Analysis**: AI-driven performance bottleneck identification
- **Dynamic Optimization**: Real-time optimization based on device capabilities
- **Predictive Loading**: AI-powered asset preloading strategies
- **Continuous Improvement**: Automated performance testing and optimization

### Unity-Specific Benefits
- **Professional Deployment**: Production-ready Unity WebGL builds
- **Cross-Platform Performance**: Consistent experience across devices
- **Analytics Integration**: Comprehensive performance and user behavior tracking
- **Error Handling**: Robust error recovery and user experience preservation

## 🎯 Next Steps for Unity WebGL Mastery
1. **Implement Build Pipeline**: Automated Unity WebGL optimization pipeline
2. **Deploy Performance Monitoring**: Real-time performance tracking system
3. **Create AI Analyzer**: Automated performance analysis and optimization
4. **Build Testing Suite**: Comprehensive cross-device performance testing
5. **Optimize for Mobile**: Mobile-specific Unity WebGL performance optimizations