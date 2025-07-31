# @03-WebGL Performance Optimization

## 🎯 Learning Objectives
- Master Unity WebGL performance optimization techniques and best practices
- Implement advanced memory management and loading strategies for web games
- Leverage AI tools for automated performance analysis and optimization workflows
- Build high-performance web games that run smoothly across all browsers and devices

## ⚡ Unity WebGL Performance Framework

### Core Performance Manager
**WebGL Performance Optimization System**:
```csharp
// WebGLPerformanceManager.cs - Comprehensive WebGL performance optimization
using UnityEngine;
using UnityEngine.Profiling;
using System.Collections.Generic;
using System.Collections;
using System.Runtime.InteropServices;

public class WebGLPerformanceManager : MonoBehaviour
{
    [DllImport("__Internal")]
    private static extern void OptimizeWebGLMemory();
    
    [DllImport("__Internal")]
    private static extern int GetWebGLMemoryUsage();
    
    [DllImport("__Internal")]
    private static extern void SetWebGLQualityLevel(int level);
    
    [DllImport("__Internal")]
    private static extern float GetBrowserPerformanceScore();
    
    [System.Serializable]
    public class WebGLSettings
    {
        [Header("Memory Management")]
        public int targetMemoryMB = 512;
        public bool enableMemoryOptimization = true;
        public float memoryCleanupInterval = 60f;
        
        [Header("Quality Scaling")]
        public bool enableAdaptiveQuality = true;
        public float[] qualityThresholds = { 30f, 45f, 60f };
        public int[] qualityLevels = { 0, 1, 2, 3 };
        
        [Header("Loading Optimization")]
        public bool enableProgressiveLoading = true;
        public bool compressTextures = true;
        public bool enableAssetStreaming = true;
        
        [Header("Rendering Optimization")]
        public bool enableBatching = true;
        public bool enableCulling = true;
        public int maxDrawCalls = 100;
        public int maxVertices = 50000;
    }
    
    [System.Serializable]
    public class PerformanceMetrics
    {
        public float currentFPS;
        public float averageFPS;
        public int memoryUsageMB;
        public int drawCalls;
        public int vertices;
        public float frameTime;
        public float browserScore;
        public bool isPerformant;
    }
    
    [Header("WebGL Configuration")]
    public WebGLSettings webglSettings;
    
    [Header("Performance Monitoring")]
    public bool enableRealTimeMonitoring = true;
    public float monitoringInterval = 1f;
    public int performanceHistorySize = 300;
    
    private PerformanceMetrics currentMetrics;
    private Queue<float> fpsHistory = new Queue<float>();
    private Queue<int> memoryHistory = new Queue<int>();
    private float lastCleanupTime;
    private int currentQualityLevel = 2;
    private bool isInitialized = false;
    
    // Performance optimization components
    private LODGroup[] lodGroups;
    private Camera mainCamera;
    private List<Renderer> managedRenderers = new List<Renderer>();
    
    // Events
    public System.Action<PerformanceMetrics> OnPerformanceUpdate;
    public System.Action<int> OnQualityLevelChanged;
    
    void Start()
    {
        if (Application.platform == RuntimePlatform.WebGLPlayer)
        {
            InitializeWebGLOptimization();
        }
    }
    
    void InitializeWebGLOptimization()
    {
        Debug.Log("🚀 Initializing WebGL Performance Manager...");
        
        currentMetrics = new PerformanceMetrics();
        
        // Find and cache performance-critical components
        mainCamera = Camera.main;
        lodGroups = FindObjectsOfType<LODGroup>();
        CacheRenderersForOptimization();
        
        // Set initial quality based on browser performance
        if (webglSettings.enableAdaptiveQuality)
        {
            StartCoroutine(InitializeAdaptiveQuality());
        }
        
        // Start performance monitoring
        if (enableRealTimeMonitoring)
        {
            StartCoroutine(MonitorPerformance());
        }
        
        // Start memory cleanup routine
        if (webglSettings.enableMemoryOptimization)
        {
            StartCoroutine(MemoryCleanupRoutine());
        }
        
        isInitialized = true;
        Debug.Log("✅ WebGL Performance Manager initialized");
    }
    
    void CacheRenderersForOptimization()
    {
        Renderer[] allRenderers = FindObjectsOfType<Renderer>();
        
        foreach (var renderer in allRenderers)
        {
            // Only manage renderers that can benefit from optimization
            if (renderer.gameObject.activeInHierarchy && 
                renderer.isVisible && 
                renderer.GetComponent<LODGroup>() == null)
            {
                managedRenderers.Add(renderer);
            }
        }
        
        Debug.Log($"📊 Managing {managedRenderers.Count} renderers for optimization");
    }
    
    IEnumerator InitializeAdaptiveQuality()
    {
        yield return new WaitForSeconds(2f); // Wait for initial frame settling
        
        float browserScore = GetBrowserPerformanceScore();
        int recommendedQuality = DetermineOptimalQuality(browserScore);
        
        SetQualityLevel(recommendedQuality);
        Debug.Log($"🎮 Set initial quality level to {recommendedQuality} (browser score: {browserScore})");
    }
    
    int DetermineOptimalQuality(float browserScore)
    {
        for (int i = 0; i < webglSettings.qualityThresholds.Length; i++)
        {
            if (browserScore < webglSettings.qualityThresholds[i])
            {
                return webglSettings.qualityLevels[i];
            }
        }
        
        return webglSettings.qualityLevels[webglSettings.qualityLevels.Length - 1];
    }
    
    IEnumerator MonitorPerformance()
    {
        while (true)
        {
            yield return new WaitForSeconds(monitoringInterval);
            
            UpdatePerformanceMetrics();
            
            if (webglSettings.enableAdaptiveQuality)
            {
                CheckAndAdjustQuality();
            }
            
            CheckMemoryUsage();
            OnPerformanceUpdate?.Invoke(currentMetrics);
        }
    }
    
    void UpdatePerformanceMetrics()
    {
        // Calculate FPS
        currentMetrics.currentFPS = 1f / Time.unscaledDeltaTime;
        currentMetrics.frameTime = Time.unscaledDeltaTime * 1000f; // Convert to milliseconds
        
        // Update FPS history
        fpsHistory.Enqueue(currentMetrics.currentFPS);
        if (fpsHistory.Count > performanceHistorySize)
        {
            fpsHistory.Dequeue();
        }
        
        // Calculate average FPS
        float fpsSum = 0f;
        foreach (float fps in fpsHistory)
        {
            fpsSum += fps;
        }
        currentMetrics.averageFPS = fpsSum / fpsHistory.Count;
        
        // Memory usage
        currentMetrics.memoryUsageMB = GetWebGLMemoryUsage();
        memoryHistory.Enqueue(currentMetrics.memoryUsageMB);
        if (memoryHistory.Count > performanceHistorySize)
        {
            memoryHistory.Dequeue();
        }
        
        // Rendering stats
        currentMetrics.drawCalls = UnityEngine.Rendering.FrameDebugger.enabled ? 0 : EstimateDrawCalls();
        currentMetrics.vertices = EstimateVertexCount();
        
        // Browser performance score
        currentMetrics.browserScore = GetBrowserPerformanceScore();
        
        // Overall performance assessment
        currentMetrics.isPerformant = currentMetrics.averageFPS >= 30f && 
                                    currentMetrics.memoryUsageMB <= webglSettings.targetMemoryMB;
    }
    
    int EstimateDrawCalls()
    {
        int drawCalls = 0;
        
        foreach (var renderer in managedRenderers)
        {
            if (renderer != null && renderer.isVisible)
            {
                drawCalls += renderer.materials.Length;
            }
        }
        
        return drawCalls;
    }
    
    int EstimateVertexCount()
    {
        int vertices = 0;
        
        foreach (var renderer in managedRenderers)
        {
            if (renderer != null && renderer.isVisible)
            {
                var meshFilter = renderer.GetComponent<MeshFilter>();
                if (meshFilter != null && meshFilter.mesh != null)
                {
                    vertices += meshFilter.mesh.vertexCount;
                }
            }
        }
        
        return vertices;
    }
    
    void CheckAndAdjustQuality()
    {
        float averageFPS = currentMetrics.averageFPS;
        
        // Quality adjustment logic
        if (averageFPS < 25f && currentQualityLevel > 0)
        {
            // Decrease quality if FPS is too low
            SetQualityLevel(currentQualityLevel - 1);
            Debug.Log($"📉 Reduced quality to level {currentQualityLevel} (FPS: {averageFPS:F1})");
        }
        else if (averageFPS > 50f && currentQualityLevel < webglSettings.qualityLevels.Length - 1)
        {
            // Increase quality if FPS is stable and high
            SetQualityLevel(currentQualityLevel + 1);
            Debug.Log($"📈 Increased quality to level {currentQualityLevel} (FPS: {averageFPS:F1})");
        }
    }
    
    void SetQualityLevel(int level)
    {
        currentQualityLevel = Mathf.Clamp(level, 0, webglSettings.qualityLevels.Length - 1);
        QualitySettings.SetQualityLevel(currentQualityLevel);
        SetWebGLQualityLevel(currentQualityLevel);
        
        // Apply quality-specific optimizations
        ApplyQualityOptimizations(currentQualityLevel);
        
        OnQualityLevelChanged?.Invoke(currentQualityLevel);
    }
    
    void ApplyQualityOptimizations(int qualityLevel)
    {
        switch (qualityLevel)
        {
            case 0: // Low Quality
                ApplyLowQualitySettings();
                break;
            case 1: // Medium Quality
                ApplyMediumQualitySettings();
                break;
            case 2: // High Quality
                ApplyHighQualitySettings();
                break;
            case 3: // Ultra Quality
                ApplyUltraQualitySettings();
                break;
        }
    }
    
    void ApplyLowQualitySettings()
    {
        // Reduce texture quality
        QualitySettings.globalTextureMipmapLimit = 2;
        
        // Disable expensive effects
        QualitySettings.shadows = ShadowQuality.Disable;
        QualitySettings.shadowResolution = ShadowResolution.Low;
        
        // Reduce particle density
        QualitySettings.particleRaycastBudget = 16;
        
        // Optimize LOD settings
        QualitySettings.lodBias = 0.5f;
        
        // Reduce animation quality
        QualitySettings.skinWeights = SkinWeights.TwoBones;
        
        Debug.Log("🔧 Applied low quality settings");
    }
    
    void ApplyMediumQualitySettings()
    {
        QualitySettings.globalTextureMipmapLimit = 1;
        QualitySettings.shadows = ShadowQuality.HardOnly;
        QualitySettings.shadowResolution = ShadowResolution.Medium;
        QualitySettings.particleRaycastBudget = 64;
        QualitySettings.lodBias = 0.75f;
        QualitySettings.skinWeights = SkinWeights.TwoBones;
        
        Debug.Log("🔧 Applied medium quality settings");
    }
    
    void ApplyHighQualitySettings()
    {
        QualitySettings.globalTextureMipmapLimit = 0;
        QualitySettings.shadows = ShadowQuality.All;
        QualitySettings.shadowResolution = ShadowResolution.High;
        QualitySettings.particleRaycastBudget = 256;
        QualitySettings.lodBias = 1f;
        QualitySettings.skinWeights = SkinWeights.FourBones;
        
        Debug.Log("🔧 Applied high quality settings");
    }
    
    void ApplyUltraQualitySettings()
    {
        QualitySettings.globalTextureMipmapLimit = 0;
        QualitySettings.shadows = ShadowQuality.All;
        QualitySettings.shadowResolution = ShadowResolution.VeryHigh;
        QualitySettings.particleRaycastBudget = 1024;
        QualitySettings.lodBias = 1.5f;
        QualitySettings.skinWeights = SkinWeights.UnlimitedBones;
        
        Debug.Log("🔧 Applied ultra quality settings");
    }
    
    void CheckMemoryUsage()
    {
        if (currentMetrics.memoryUsageMB > webglSettings.targetMemoryMB * 0.9f)
        {
            Debug.LogWarning($"⚠️ High memory usage: {currentMetrics.memoryUsageMB}MB");
            
            if (webglSettings.enableMemoryOptimization)
            {
                StartCoroutine(ForceMemoryCleanup());
            }
        }
    }
    
    IEnumerator MemoryCleanupRoutine()
    {
        while (true)
        {
            yield return new WaitForSeconds(webglSettings.memoryCleanupInterval);
            
            if (Time.time - lastCleanupTime >= webglSettings.memoryCleanupInterval)
            {
                PerformMemoryCleanup();
                lastCleanupTime = Time.time;
            }
        }
    }
    
    IEnumerator ForceMemoryCleanup()
    {
        Debug.Log("🧹 Performing force memory cleanup...");
        
        // Unload unused assets
        yield return Resources.UnloadUnusedAssets();
        
        // Force garbage collection
        System.GC.Collect();
        
        // WebGL-specific memory optimization
        OptimizeWebGLMemory();
        
        Debug.Log("✅ Force memory cleanup completed");
    }
    
    void PerformMemoryCleanup()
    {
        // Regular memory cleanup
        Resources.UnloadUnusedAssets();
        System.GC.Collect();
        OptimizeWebGLMemory();
        
        Debug.Log("🧹 Regular memory cleanup performed");
    }
    
    // Public API methods
    public void SetTargetFrameRate(int fps)
    {
        Application.targetFrameRate = fps;
        Debug.Log($"🎯 Target frame rate set to {fps} FPS");
    }
    
    public void EnableVSync(bool enable)
    {
        QualitySettings.vSyncCount = enable ? 1 : 0;
        Debug.Log($"🔄 VSync {(enable ? "enabled" : "disabled")}");
    }
    
    public void OptimizeForBattery()
    {
        // Battery optimization settings
        SetQualityLevel(0);
        SetTargetFrameRate(30);
        EnableVSync(true);
        
        Debug.Log("🔋 Optimized for battery life");
    }
    
    public void OptimizeForPerformance()
    {
        // Performance optimization settings
        SetQualityLevel(3);
        SetTargetFrameRate(60);
        EnableVSync(false);
        
        Debug.Log("⚡ Optimized for performance");
    }
    
    public PerformanceMetrics GetCurrentMetrics()
    {
        return currentMetrics;
    }
    
    public float GetAverageFPS()
    {
        return currentMetrics.averageFPS;
    }
    
    public int GetMemoryUsage()
    {
        return currentMetrics.memoryUsageMB;
    }
    
    // Culling optimization
    public void EnableOcclusionCulling(bool enable)
    {
        if (mainCamera != null)
        {
            mainCamera.useOcclusionCulling = enable;
            Debug.Log($"👁️ Occlusion culling {(enable ? "enabled" : "disabled")}");
        }
    }
    
    public void SetCullingDistance(float distance)
    {
        if (mainCamera != null)
        {
            mainCamera.farClipPlane = distance;
            Debug.Log($"📏 Culling distance set to {distance}");
        }
    }
    
    // LOD optimization
    public void SetLODBias(float bias)
    {
        QualitySettings.lodBias = bias;
        
        foreach (var lodGroup in lodGroups)
        {
            if (lodGroup != null)
            {
                lodGroup.size *= bias;
            }
        }
        
        Debug.Log($"🔍 LOD bias set to {bias}");
    }
    
    // Debug and monitoring
    [ContextMenu("Force Performance Analysis")]
    public void ForcePerformanceAnalysis()
    {
        UpdatePerformanceMetrics();
        LogPerformanceReport();
    }
    
    void LogPerformanceReport()
    {
        Debug.Log("📊 WebGL Performance Report:");
        Debug.Log($"  Current FPS: {currentMetrics.currentFPS:F1}");
        Debug.Log($"  Average FPS: {currentMetrics.averageFPS:F1}");
        Debug.Log($"  Memory Usage: {currentMetrics.memoryUsageMB} MB");
        Debug.Log($"  Draw Calls: {currentMetrics.drawCalls}");
        Debug.Log($"  Vertices: {currentMetrics.vertices:N0}");
        Debug.Log($"  Frame Time: {currentMetrics.frameTime:F2} ms");
        Debug.Log($"  Quality Level: {currentQualityLevel}");
        Debug.Log($"  Browser Score: {currentMetrics.browserScore}");
        Debug.Log($"  Is Performant: {currentMetrics.isPerformant}");
    }
    
    void OnGUI()
    {
        if (!isInitialized || !enableRealTimeMonitoring) return;
        
        GUI.Box(new Rect(10, 10, 250, 160), "WebGL Performance Monitor");
        GUI.Label(new Rect(15, 30, 240, 20), $"FPS: {currentMetrics.currentFPS:F1} (Avg: {currentMetrics.averageFPS:F1})");
        GUI.Label(new Rect(15, 50, 240, 20), $"Memory: {currentMetrics.memoryUsageMB} MB");
        GUI.Label(new Rect(15, 70, 240, 20), $"Draw Calls: {currentMetrics.drawCalls}");
        GUI.Label(new Rect(15, 90, 240, 20), $"Vertices: {currentMetrics.vertices:N0}");
        GUI.Label(new Rect(15, 110, 240, 20), $"Quality Level: {currentQualityLevel}");
        GUI.Label(new Rect(15, 130, 240, 20), $"Frame Time: {currentMetrics.frameTime:F1}ms");
        GUI.Label(new Rect(15, 150, 240, 20), $"Status: {(currentMetrics.isPerformant ? "✅ Good" : "⚠️ Poor")}");
    }
}
```

### WebGL Asset Streaming System
**Progressive Asset Loading**:
```csharp
// WebGLAssetStreamer.cs - Optimized asset streaming for WebGL
using UnityEngine;
using UnityEngine.AddressableAssets;
using UnityEngine.ResourceManagement.AsyncOperations;
using System.Collections.Generic;
using System.Collections;

public class WebGLAssetStreamer : MonoBehaviour
{
    [System.Serializable]
    public class StreamingConfig
    {
        [Header("Loading Strategy")]
        public bool enableProgressiveLoading = true;
        public bool prioritizeEssentialAssets = true;
        public int maxConcurrentLoads = 3;
        public float loadingTimeSliceMS = 16f; // ~60 FPS budget
        
        [Header("Memory Management")]
        public int maxCachedAssets = 50;
        public float assetUnloadDelay = 30f;
        public bool enableSmartUnloading = true;
        
        [Header("Compression")]
        public bool compressTextures = true;
        public bool compressAudio = true;
        public TextureCompressionQuality textureQuality = TextureCompressionQuality.Normal;
    }
    
    [System.Serializable]
    public class AssetRequest
    {
        public string assetKey;
        public AssetPriority priority;
        public System.Action<UnityEngine.Object> onLoaded;
        public System.Action<string> onFailed;
        public float requestTime;
        public bool isEssential;
    }
    
    public enum AssetPriority
    {
        Critical = 0,   // Game-breaking if not loaded
        High = 1,       // Important for gameplay
        Medium = 2,     // Quality of life
        Low = 3,        // Nice to have
        Background = 4  // Load when idle
    }
    
    [Header("Streaming Configuration")]
    public StreamingConfig config;
    
    [Header("Preload Lists")]
    public List<string> essentialAssets = new List<string>();
    public List<string> preloadAssets = new List<string>();
    
    private Queue<AssetRequest> loadingQueue = new Queue<AssetRequest>();
    private Dictionary<string, UnityEngine.Object> assetCache = new Dictionary<string, UnityEngine.Object>();
    private Dictionary<string, float> assetLastUsed = new Dictionary<string, float>();
    private List<AsyncOperationHandle> activeOperations = new List<AsyncOperationHandle>();
    
    private bool isStreamingActive = false;
    private int currentConcurrentLoads = 0;
    private float totalLoadingTime = 0f;
    private int totalAssetsLoaded = 0;
    
    // Events
    public System.Action<string, float> OnAssetLoadProgress;
    public System.Action<string> OnAssetLoaded;
    public System.Action<float> OnOverallProgress;
    
    void Start()
    {
        if (Application.platform == RuntimePlatform.WebGLPlayer)
        {
            InitializeStreaming();
        }
    }
    
    void InitializeStreaming()
    {
        Debug.Log("📦 Initializing WebGL Asset Streamer...");
        
        StartCoroutine(StreamingLoop());
        StartCoroutine(MemoryManagementLoop());
        
        // Preload essential assets
        if (config.prioritizeEssentialAssets)
        {
            PreloadEssentialAssets();
        }
        
        isStreamingActive = true;
    }
    
    void PreloadEssentialAssets()
    {
        Debug.Log($"⚡ Preloading {essentialAssets.Count} essential assets...");
        
        foreach (string assetKey in essentialAssets)
        {
            RequestAsset(assetKey, AssetPriority.Critical, null, null, true);
        }
        
        foreach (string assetKey in preloadAssets)
        {
            RequestAsset(assetKey, AssetPriority.High, null, null, false);
        }
    }
    
    public void RequestAsset(string assetKey, AssetPriority priority = AssetPriority.Medium, 
                           System.Action<UnityEngine.Object> onLoaded = null, 
                           System.Action<string> onFailed = null, 
                           bool isEssential = false)
    {
        // Check if asset is already cached
        if (assetCache.ContainsKey(assetKey))
        {
            assetLastUsed[assetKey] = Time.time;
            onLoaded?.Invoke(assetCache[assetKey]);
            return;
        }
        
        // Check if asset is already in queue
        foreach (var request in loadingQueue)
        {
            if (request.assetKey == assetKey)
            {
                // Update priority if higher
                if (priority < request.priority)
                {
                    request.priority = priority;
                }
                return;
            }
        }
        
        // Add to loading queue
        var assetRequest = new AssetRequest
        {
            assetKey = assetKey,
            priority = priority,
            onLoaded = onLoaded,
            onFailed = onFailed,
            requestTime = Time.time,
            isEssential = isEssential
        };
        
        loadingQueue.Enqueue(assetRequest);
        
        Debug.Log($"📋 Asset requested: {assetKey} (Priority: {priority})");
    }
    
    IEnumerator StreamingLoop()
    {
        while (isStreamingActive)
        {
            if (loadingQueue.Count > 0 && currentConcurrentLoads < config.maxConcurrentLoads)
            {
                var request = GetNextHighestPriorityRequest();
                if (request != null)
                {
                    StartCoroutine(LoadAssetAsync(request));
                }
            }
            
            yield return null; // Wait one frame
        }
    }
    
    AssetRequest GetNextHighestPriorityRequest()
    {
        AssetRequest highestPriorityRequest = null;
        var tempQueue = new Queue<AssetRequest>();
        
        // Find highest priority request
        while (loadingQueue.Count > 0)
        {
            var request = loadingQueue.Dequeue();
            
            if (highestPriorityRequest == null || request.priority < highestPriorityRequest.priority)
            {
                if (highestPriorityRequest != null)
                {
                    tempQueue.Enqueue(highestPriorityRequest);
                }
                highestPriorityRequest = request;
            }
            else
            {
                tempQueue.Enqueue(request);
            }
        }
        
        // Restore queue
        while (tempQueue.Count > 0)
        {
            loadingQueue.Enqueue(tempQueue.Dequeue());
        }
        
        return highestPriorityRequest;
    }
    
    IEnumerator LoadAssetAsync(AssetRequest request)
    {
        currentConcurrentLoads++;
        float startTime = Time.realtimeSinceStartup;
        
        Debug.Log($"📥 Loading asset: {request.assetKey}");
        
        var handle = Addressables.LoadAssetAsync<UnityEngine.Object>(request.assetKey);
        activeOperations.Add(handle);
        
        // Monitor loading progress
        while (!handle.IsDone)
        {
            OnAssetLoadProgress?.Invoke(request.assetKey, handle.PercentComplete);
            yield return null;
            
            // Respect frame time budget
            if (Time.realtimeSinceStartup - startTime > config.loadingTimeSliceMS / 1000f)
            {
                yield return null;
                startTime = Time.realtimeSinceStartup;
            }
        }
        
        // Handle completion
        if (handle.Status == AsyncOperationStatus.Succeeded)
        {
            var asset = handle.Result;
            
            // Apply WebGL-specific optimizations
            OptimizeAssetForWebGL(asset);
            
            // Cache the asset
            CacheAsset(request.assetKey, asset);
            
            // Notify completion
            request.onLoaded?.Invoke(asset);
            OnAssetLoaded?.Invoke(request.assetKey);
            
            totalAssetsLoaded++;
            totalLoadingTime += Time.realtimeSinceStartup - startTime;
            
            Debug.Log($"✅ Asset loaded: {request.assetKey} ({totalAssetsLoaded} total)");
        }
        else
        {
            string error = $"Failed to load asset: {request.assetKey} - {handle.OperationException?.Message}";
            Debug.LogError($"❌ {error}");
            request.onFailed?.Invoke(error);
        }
        
        activeOperations.Remove(handle);
        currentConcurrentLoads--;
        
        // Update overall progress
        float progress = (float)totalAssetsLoaded / (essentialAssets.Count + preloadAssets.Count);
        OnOverallProgress?.Invoke(progress);
    }
    
    void OptimizeAssetForWebGL(UnityEngine.Object asset)
    {
        if (asset is Texture2D texture)
        {
            OptimizeTexture(texture);
        }
        else if (asset is AudioClip audioClip)
        {
            OptimizeAudio(audioClip);
        }
        else if (asset is Mesh mesh)
        {
            OptimizeMesh(mesh);
        }
    }
    
    void OptimizeTexture(Texture2D texture)
    {
        if (!config.compressTextures) return;
        
        // Apply texture compression settings for WebGL
        // This would be done at build time, but we can verify settings here
        if (texture.format != TextureFormat.DXT1 && texture.format != TextureFormat.DXT5)
        {
            Debug.LogWarning($"⚠️ Texture {texture.name} not optimally compressed for WebGL");
        }
    }
    
    void OptimizeAudio(AudioClip audioClip)
    {
        if (!config.compressAudio) return;
        
        // Audio optimization for WebGL
        // Verify compression settings
        Debug.Log($"🔊 Audio clip loaded: {audioClip.name} ({audioClip.length:F1}s)");
    }
    
    void OptimizeMesh(Mesh mesh)
    {
        // Mesh optimization for WebGL
        if (mesh.vertexCount > 10000)
        {
            Debug.LogWarning($"⚠️ High vertex count mesh: {mesh.name} ({mesh.vertexCount} vertices)");
        }
    }
    
    void CacheAsset(string assetKey, UnityEngine.Object asset)
    {
        // Check cache size limit
        if (assetCache.Count >= config.maxCachedAssets)
        {
            UnloadOldestAsset();
        }
        
        assetCache[assetKey] = asset;
        assetLastUsed[assetKey] = Time.time;
        
        Debug.Log($"💾 Asset cached: {assetKey} (Cache size: {assetCache.Count})");
    }
    
    void UnloadOldestAsset()
    {
        string oldestAsset = null;
        float oldestTime = float.MaxValue;
        
        foreach (var kvp in assetLastUsed)
        {
            if (kvp.Value < oldestTime && !essentialAssets.Contains(kvp.Key))
            {
                oldestTime = kvp.Value;
                oldestAsset = kvp.Key;
            }
        }
        
        if (oldestAsset != null)
        {
            UnloadAsset(oldestAsset);
        }
    }
    
    void UnloadAsset(string assetKey)
    {
        if (assetCache.ContainsKey(assetKey))
        {
            var asset = assetCache[assetKey];
            
            // Don't unload essential assets
            if (!essentialAssets.Contains(assetKey))
            {
                assetCache.Remove(assetKey);
                assetLastUsed.Remove(assetKey);
                
                // Release addressable asset
                Addressables.Release(asset);
                
                Debug.Log($"🗑️ Asset unloaded: {assetKey}");
            }
        }
    }
    
    IEnumerator MemoryManagementLoop()
    {
        while (isStreamingActive)
        {
            yield return new WaitForSeconds(config.assetUnloadDelay);
            
            if (config.enableSmartUnloading)
            {
                PerformSmartUnloading();
            }
        }
    }
    
    void PerformSmartUnloading()
    {
        float currentTime = Time.time;
        var assetsToUnload = new List<string>();
        
        foreach (var kvp in assetLastUsed)
        {
            if (currentTime - kvp.Value > config.assetUnloadDelay && 
                !essentialAssets.Contains(kvp.Key))
            {
                assetsToUnload.Add(kvp.Key);
            }
        }
        
        foreach (string assetKey in assetsToUnload)
        {
            UnloadAsset(assetKey);
        }
        
        if (assetsToUnload.Count > 0)
        {
            Debug.Log($"🧹 Smart unloading: {assetsToUnload.Count} assets removed");
        }
    }
    
    // Public API
    public bool IsAssetLoaded(string assetKey)
    {
        return assetCache.ContainsKey(assetKey);
    }
    
    public T GetCachedAsset<T>(string assetKey) where T : UnityEngine.Object
    {
        if (assetCache.ContainsKey(assetKey))
        {
            assetLastUsed[assetKey] = Time.time;
            return assetCache[assetKey] as T;
        }
        return null;
    }
    
    public void ClearCache()
    {
        foreach (var kvp in assetCache)
        {
            if (!essentialAssets.Contains(kvp.Key))
            {
                Addressables.Release(kvp.Value);
            }
        }
        
        assetCache.Clear();
        assetLastUsed.Clear();
        
        Debug.Log("🧹 Asset cache cleared");
    }
    
    public int GetQueueSize()
    {
        return loadingQueue.Count;
    }
    
    public int GetCacheSize()
    {
        return assetCache.Count;
    }
    
    public float GetAverageLoadTime()
    {
        return totalAssetsLoaded > 0 ? totalLoadingTime / totalAssetsLoaded : 0f;
    }
    
    void OnDestroy()
    {
        isStreamingActive = false;
        
        // Cancel active operations
        foreach (var handle in activeOperations)
        {
            if (handle.IsValid())
            {
                Addressables.Release(handle);
            }
        }
        
        ClearCache();
    }
}
```

## 🚀 AI Integration Opportunities

### Smart WebGL Optimization
**AI-Enhanced Performance Optimization**:
- Generate adaptive quality scaling algorithms based on device capabilities
- Automate asset compression and optimization pipelines for WebGL deployment
- Create intelligent loading strategies that predict asset usage patterns
- Build automated performance testing and regression detection systems
- Generate custom shader optimizations for WebGL rendering pipeline

### Prompt Templates for WebGL Optimization
```
"Create a Unity WebGL memory management system that automatically adjusts quality settings based on browser performance and available memory"

"Generate an asset streaming pipeline for Unity WebGL that prioritizes critical game assets and implements smart caching with progressive loading"

"Build a comprehensive WebGL performance monitoring dashboard that tracks FPS, memory usage, and provides optimization recommendations"
```

WebGL performance optimization ensures Unity games run smoothly across all web browsers and devices, providing consistent player experiences through adaptive quality scaling, intelligent asset streaming, and comprehensive memory management.