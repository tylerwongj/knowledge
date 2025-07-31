# @d-XR-Performance-Optimization - Extended Reality Performance Engineering

## 🎯 Learning Objectives
- Master XR-specific performance requirements and constraints
- Implement advanced optimization techniques for VR and AR applications
- Profile and debug XR applications using specialized tools
- Achieve consistent 90fps+ performance across different XR platforms

## ⚡ XR Performance Fundamentals

### Critical Performance Metrics
- **Frame Rate**: 90fps minimum for VR, 60fps for mobile AR
- **Motion-to-Photon Latency**: Under 20ms for presence
- **Frame Time Consistency**: Avoid dropped frames at all costs
- **Thermal Management**: Prevent device overheating and throttling

### XR Rendering Pipeline Challenges
```csharp
public class XRRenderingOptimizer : MonoBehaviour
{
    [Header("Rendering Settings")]
    [SerializeField] private bool enableSinglePassStereo = true;
    [SerializeField] private bool enableInstancing = true;
    [SerializeField] private int eyeTextureResolution = 2048;
    
    void Start()
    {
        ConfigureXRRendering();
        StartCoroutine(MonitorFrameRate());
    }
    
    private void ConfigureXRRendering()
    {
        // Enable single-pass stereo rendering for VR efficiency
        if (enableSinglePassStereo && XRSettings.enabled)
        {
            XRSettings.stereoRenderingMode = XRSettings.StereoRenderingMode.SinglePass;
        }
        
        // Set eye texture resolution based on platform capability
        XRSettings.eyeTextureResolutionScale = CalculateOptimalResolutionScale();
        
        // Configure render pipeline for XR
        RenderPipelineManager.currentPipeline = Resources.Load<RenderPipelineAsset>("XR_URP_Pipeline");
    }
    
    private float CalculateOptimalResolutionScale()
    {
        // Adjust resolution based on device capability
        if (SystemInfo.graphicsMemorySize < 4000) // Less than 4GB VRAM
            return 0.8f;
        else if (SystemInfo.graphicsMemorySize < 8000) // Less than 8GB VRAM
            return 1.0f;
        else
            return 1.2f;
    }
}
```

## 🔧 Advanced Optimization Techniques

### Level of Detail (LOD) for XR
```csharp
public class XRLODManager : MonoBehaviour
{
    [Header("XR LOD Settings")]
    [SerializeField] private float[] vrLodDistances = {2f, 8f, 20f, 50f};
    [SerializeField] private float[] arLodDistances = {1f, 5f, 15f, 30f};
    [SerializeField] private bool useEyeTracking = false;
    
    private Camera leftEye, rightEye;
    private Dictionary<LODGroup, float> originalLODDistances = new Dictionary<LODGroup, float>();
    
    void Start()
    {
        SetupXRLOD();
        ConfigureLODGroups();
    }
    
    private void SetupXRLOD()
    {
        bool isVR = XRSettings.enabled && XRDevice.isPresent;
        float[] targetDistances = isVR ? vrLodDistances : arLodDistances;
        
        LODGroup[] lodGroups = FindObjectsOfType<LODGroup>();
        
        foreach (LODGroup lodGroup in lodGroups)
        {
            LOD[] lods = lodGroup.GetLODs();
            
            for (int i = 0; i < lods.Length && i < targetDistances.Length; i++)
            {
                lods[i].screenRelativeTransitionHeight = 1f / targetDistances[i];
            }
            
            lodGroup.SetLODs(lods);
        }
    }
    
    void Update()
    {
        if (useEyeTracking)
        {
            UpdateFoveatedLOD();
        }
    }
    
    private void UpdateFoveatedLOD()
    {
        // Implement foveated rendering based on eye tracking
        Vector3 gazeDirection = GetEyeTrackingGaze();
        
        LODGroup[] lodGroups = FindObjectsOfType<LODGroup>();
        
        foreach (LODGroup lodGroup in lodGroups)
        {
            float gazeDistance = Vector3.Distance(lodGroup.transform.position, gazeDirection);
            AdjustLODBasedOnGaze(lodGroup, gazeDistance);
        }
    }
}
```

### Occlusion Culling Optimization
```csharp
public class XROcclusionManager : MonoBehaviour
{
    [Header("Occlusion Settings")]
    [SerializeField] private bool enableDynamicOcclusion = true;
    [SerializeField] private float cullDistance = 100f;
    [SerializeField] private LayerMask occlusionLayers = -1;
    
    private Camera[] xrCameras;
    private Dictionary<Renderer, bool> rendererVisibility = new Dictionary<Renderer, bool>();
    
    void Start()
    {
        SetupOcclusionCulling();
    }
    
    private void SetupOcclusionCulling()
    {
        xrCameras = Camera.allCameras;
        
        // Enable occlusion culling on XR cameras
        foreach (Camera cam in xrCameras)
        {
            if (cam.stereoEnabled || cam.name.Contains("AR"))
            {
                cam.useOcclusionCulling = true;
            }
        }
        
        if (enableDynamicOcclusion)
        {
            StartCoroutine(DynamicOcclusionCulling());
        }
    }
    
    private IEnumerator DynamicOcclusionCulling()
    {
        while (true)
        {
            foreach (Camera cam in xrCameras)
            {
                if (cam.enabled)
                {
                    PerformOcclusionCulling(cam);
                }
            }
            
            yield return new WaitForSeconds(0.1f); // Check 10 times per second
        }
    }
    
    private void PerformOcclusionCulling(Camera camera)
    {
        Renderer[] allRenderers = FindObjectsOfType<Renderer>();
        
        foreach (Renderer renderer in allRenderers)
        {
            if (Vector3.Distance(camera.transform.position, renderer.transform.position) > cullDistance)
            {
                renderer.enabled = false;
                continue;
            }
            
            // Perform frustum culling
            Plane[] frustumPlanes = GeometryUtility.CalculateFrustumPlanes(camera);
            bool isVisible = GeometryUtility.TestPlanesAABB(frustumPlanes, renderer.bounds);
            
            renderer.enabled = isVisible;
        }
    }
}
```

## 📊 XR Profiling and Debugging

### XR Performance Profiler
```csharp
public class XRPerformanceProfiler : MonoBehaviour
{
    [Header("Profiling Settings")]
    [SerializeField] private bool enableProfiling = true;
    [SerializeField] private float profilingInterval = 1f;
    [SerializeField] private bool logToFile = true;
    
    private float frameTime;
    private float renderTime;
    private int drawCalls;
    private long memoryUsage;
    
    private StringBuilder performanceLog = new StringBuilder();
    
    void Start()
    {
        if (enableProfiling)
        {
            StartCoroutine(ProfilePerformance());
        }
    }
    
    private IEnumerator ProfilePerformance()
    {
        while (true)
        {
            CollectPerformanceMetrics();
            LogPerformanceData();
            
            yield return new WaitForSeconds(profilingInterval);
        }
    }
    
    private void CollectPerformanceMetrics()
    {
        // Frame timing
        frameTime = Time.unscaledDeltaTime;
        
        // Rendering stats
        renderTime = UnityEngine.Profiling.Profiler.GetCounter("Render Thread", "Main Thread") / 1000000f;
        drawCalls = UnityEngine.Profiling.Profiler.GetCounter("Render", "Draw Calls");
        
        // Memory usage
        memoryUsage = GC.GetTotalMemory(false);
        
        // XR-specific metrics
        if (XRSettings.enabled)
        {
            CollectXRMetrics();
        }
    }
    
    private void CollectXRMetrics()
    {
        // Eye texture resolution
        float eyeTextureScale = XRSettings.eyeTextureResolutionScale;
        
        // Tracking state
        bool isTracking = XRDevice.isPresent && InputTracking.GetLocalPosition(XRNode.Head) != Vector3.zero;
        
        // Add XR-specific data to log
        performanceLog.AppendLine($"XR Scale: {eyeTextureScale:F2}, Tracking: {isTracking}");
    }
    
    private void LogPerformanceData()
    {
        float fps = 1f / frameTime;
        
        string logEntry = $"FPS: {fps:F1}, Frame: {frameTime * 1000:F2}ms, " +
                         $"Render: {renderTime:F2}ms, Draws: {drawCalls}, " +
                         $"Memory: {memoryUsage / 1024 / 1024}MB";
        
        performanceLog.AppendLine(logEntry);
        
        if (logToFile && performanceLog.Length > 10000) // Write every ~10KB
        {
            WriteLogToFile();
        }
        
        // Warning for performance issues
        if (fps < 85f) // Below VR minimum threshold
        {
            Debug.LogWarning($"Performance Warning: {fps:F1} FPS");
        }
    }
    
    private void WriteLogToFile()
    {
        string filePath = Path.Combine(Application.persistentDataPath, "xr_performance.log");
        File.WriteAllText(filePath, performanceLog.ToString());
        performanceLog.Clear();
    }
}
```

### Memory Management for XR
```csharp
public class XRMemoryManager : MonoBehaviour
{
    [Header("Memory Management")]
    [SerializeField] private int maxTextureMemoryMB = 2048;
    [SerializeField] private int maxMeshMemoryMB = 512;
    [SerializeField] private bool enableAssetStreaming = true;
    
    private Dictionary<Texture, float> textureLastUsed = new Dictionary<Texture, float>();
    private Dictionary<Mesh, float> meshLastUsed = new Dictionary<Mesh, float>();
    
    void Start()
    {
        ConfigureMemorySettings();
        StartCoroutine(ManageMemory());
    }
    
    private void ConfigureMemorySettings()
    {
        // Set texture memory budget
        QualitySettings.masterTextureLimit = CalculateTextureLimit();
        
        // Configure asset streaming
        if (enableAssetStreaming)
        {
            QualitySettings.streamingMipmapsActive = true;
            QualitySettings.streamingMipmapsMemoryBudget = maxTextureMemoryMB / 2;
        }
    }
    
    private int CalculateTextureLimit()
    {
        long totalMemory = SystemInfo.systemMemorySize;
        
        if (totalMemory < 4000) return 2; // Reduce texture quality on low-memory devices
        if (totalMemory < 8000) return 1;
        return 0; // Full quality on high-memory devices
    }
    
    private IEnumerator ManageMemory()
    {
        while (true)
        {
            CleanupUnusedAssets();
            MonitorMemoryUsage();
            
            yield return new WaitForSeconds(5f);
        }
    }
    
    private void CleanupUnusedAssets()
    {
        float currentTime = Time.time;
        
        // Cleanup unused textures
        var unusedTextures = textureLastUsed.Where(kvp => currentTime - kvp.Value > 30f).ToList();
        foreach (var kvp in unusedTextures)
        {
            if (kvp.Key != null)
            {
                Resources.UnloadAsset(kvp.Key);
            }
            textureLastUsed.Remove(kvp.Key);
        }
        
        // Cleanup unused meshes
        var unusedMeshes = meshLastUsed.Where(kvp => currentTime - kvp.Value > 60f).ToList();
        foreach (var kvp in unusedMeshes)
        {
            if (kvp.Key != null)
            {
                Resources.UnloadAsset(kvp.Key);
            }
            meshLastUsed.Remove(kvp.Key);
        }
    }
    
    private void MonitorMemoryUsage()
    {
        long memoryUsage = GC.GetTotalMemory(false);
        long memoryLimitBytes = (long)maxTextureMemoryMB * 1024 * 1024;
        
        if (memoryUsage > memoryLimitBytes * 0.9f) // Above 90% of limit
        {
            // Aggressive cleanup
            Resources.UnloadUnusedAssets();
            GC.Collect();
            
            // Reduce quality if still over limit
            if (GC.GetTotalMemory(false) > memoryLimitBytes * 0.8f)
            {
                ReduceGraphicsQuality();
            }
        }
    }
    
    private void ReduceGraphicsQuality()
    {
        // Reduce texture resolution
        XRSettings.eyeTextureResolutionScale = Mathf.Max(0.5f, XRSettings.eyeTextureResolutionScale * 0.9f);
        
        // Reduce shadow quality
        QualitySettings.shadowResolution = ShadowResolution.Low;
        QualitySettings.shadowDistance = Mathf.Max(10f, QualitySettings.shadowDistance * 0.8f);
    }
}
```

## 🚀 AI/LLM Integration for Performance

### AI-Powered Performance Analysis
- **Prompt**: "Analyze XR performance bottlenecks from profiling data"
- **Automated Optimization**: ML-based asset quality adjustment
- **Predictive Scaling**: AI-driven performance scaling based on device capability
- **Content Optimization**: Automated LOD generation and texture compression

### Intelligent Resource Management
```csharp
public class AIPerformanceOptimizer : MonoBehaviour
{
    [SerializeField] private MLModel performancePredictionModel;
    [SerializeField] private float optimizationInterval = 10f;
    
    private PerformanceMetrics currentMetrics;
    
    void Start()
    {
        StartCoroutine(AIOptimizationLoop());
    }
    
    private IEnumerator AIOptimizationLoop()
    {
        while (true)
        {
            CollectMetrics();
            
            // Use AI model to predict performance bottlenecks
            var predictions = performancePredictionModel.Predict(currentMetrics);
            
            // Apply AI-suggested optimizations
            ApplyOptimizations(predictions);
            
            yield return new WaitForSeconds(optimizationInterval);
        }
    }
    
    private void ApplyOptimizations(PerformancePredictions predictions)
    {
        if (predictions.ShouldReduceTextureQuality)
        {
            XRSettings.eyeTextureResolutionScale *= 0.9f;
        }
        
        if (predictions.ShouldAdjustLOD)
        {
            AdjustLODDistances(predictions.RecommendedLODScale);
        }
        
        if (predictions.ShouldCullObjects)
        {
            UpdateCullingDistance(predictions.RecommendedCullDistance);
        }
    }
}
```

## 💡 Key Highlights

- **90fps is non-negotiable**: VR comfort requires consistent high frame rates
- **Thermal management is critical**: Mobile XR devices overheat quickly under load
- **Memory constraints are severe**: XR applications use significantly more memory than traditional apps
- **Platform-specific optimization**: Each XR platform has unique performance characteristics
- **Profiling is essential**: Continuous performance monitoring prevents issues before they impact users

## 🎯 Platform-Specific Optimizations

### Quest/Mobile VR Optimization
```csharp
public class QuestOptimizer : MonoBehaviour
{
    void Start()
    {
        if (IsQuestDevice())
        {
            ConfigureQuestSettings();
        }
    }
    
    private void ConfigureQuestSettings()
    {
        // Quest-specific optimizations
        XRSettings.eyeTextureResolutionScale = 1.0f; // Quest 2 native resolution
        Application.targetFrameRate = 90; // Quest native refresh rate
        
        // Disable expensive features on mobile chipset
        QualitySettings.shadows = ShadowQuality.Disable;
        QualitySettings.antiAliasing = 0;
        
        // Enable fixed foveated rendering
        EnableFixedFoveatedRendering();
    }
}
```

### PC VR Optimization
```csharp
public class PCVROptimizer : MonoBehaviour
{
    void Start()
    {
        if (IsPCVRDevice())
        {
            ConfigurePCVRSettings();
        }
    }
    
    private void ConfigurePCVRSettings()
    {
        // PC VR can handle higher quality
        XRSettings.eyeTextureResolutionScale = 1.4f;
        Application.targetFrameRate = 90; // or 120 for Index
        
        // Enable advanced rendering features
        QualitySettings.shadows = ShadowQuality.All;
        QualitySettings.antiAliasing = 4;
        
        // Enable dynamic resolution scaling
        EnableDynamicResolution();
    }
}
```

## 📚 Essential Resources

### Profiling Tools
- Unity XR Profiler and Frame Debugger
- Oculus Developer Hub performance tools
- SteamVR Frame Timing display
- Platform-specific profiling utilities

### Documentation
- Unity XR performance recommendations
- Oculus Quest performance guidelines
- SteamVR performance best practices
- Mobile AR optimization guides