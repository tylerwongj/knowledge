# @40-Performance-Profiling-Tools

## 🎯 Core Concept
Automated performance profiling and optimization tools for monitoring FPS, memory usage, and system bottlenecks.

## 🔧 Implementation

### Performance Profiler System
```csharp
using UnityEngine;
using UnityEngine.Profiling;
using System.Collections.Generic;
using System.IO;
using System.Text;

public class PerformanceProfiler : MonoBehaviour
{
    public static PerformanceProfiler Instance;
    
    [Header("Profiling Settings")]
    public bool enableProfiling = true;
    public bool profileOnStart = true;
    public float samplingInterval = 0.1f;
    public int maxSamples = 1000;
    public bool exportDataOnQuit = true;
    
    [Header("Monitoring")]
    public bool monitorFPS = true;
    public bool monitorMemory = true;
    public bool monitorGPU = true;
    public bool monitorDrawCalls = true;
    
    [Header("Display")]
    public bool showRealTimeStats = true;
    public KeyCode toggleDisplayKey = KeyCode.F12;
    
    private List<PerformanceSample> samples;
    private float lastSampleTime;
    private bool displayVisible = false;
    private PerformanceStats currentStats;
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeProfiler();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void InitializeProfiler()
    {
        samples = new List<PerformanceSample>();
        currentStats = new PerformanceStats();
        
        if (profileOnStart)
        {
            StartProfiling();
        }
    }
    
    void Update()
    {
        if (!enableProfiling) return;
        
        // Toggle display
        if (Input.GetKeyDown(toggleDisplayKey))
        {
            displayVisible = !displayVisible;
        }
        
        // Sample performance data
        if (Time.time - lastSampleTime >= samplingInterval)
        {
            SamplePerformance();
            lastSampleTime = Time.time;
        }
    }
    
    void SamplePerformance()
    {
        PerformanceSample sample = new PerformanceSample
        {
            timestamp = Time.time,
            frameCount = Time.frameCount
        };
        
        if (monitorFPS)
        {
            sample.fps = 1f / Time.unscaledDeltaTime;
            sample.frameTime = Time.unscaledDeltaTime * 1000f; // Convert to milliseconds
        }
        
        if (monitorMemory)
        {
            sample.totalMemory = Profiler.GetTotalAllocatedMemory(false);
            sample.reservedMemory = Profiler.GetTotalReservedMemory(false);
            sample.unusedMemory = Profiler.GetTotalUnusedReservedMemory(false);
            sample.monoMemory = Profiler.GetMonoUsedSize();
        }
        
        if (monitorGPU)
        {
            sample.gpuMemory = Profiler.GetAllocatedMemoryForGraphicsDriver();
        }
        
        if (monitorDrawCalls)
        {
            sample.drawCalls = UnityEngine.Rendering.FrameDebugger.enabled ? 
                UnityEngine.Rendering.FrameDebugger.count : -1;
            sample.triangles = 0; // Would need custom implementation
            sample.vertices = 0; // Would need custom implementation
        }
        
        samples.Add(sample);
        
        // Update current stats
        UpdateCurrentStats(sample);
        
        // Limit sample count
        if (samples.Count > maxSamples)
        {
            samples.RemoveAt(0);
        }
    }
    
    void UpdateCurrentStats(PerformanceSample sample)
    {
        currentStats.currentFPS = sample.fps;
        currentStats.currentFrameTime = sample.frameTime;
        currentStats.currentMemoryMB = sample.totalMemory / (1024f * 1024f);
        
        // Calculate averages
        if (samples.Count > 0)
        {
            float fpsSum = 0f;
            float frameTimeSum = 0f;
            long memorySum = 0;
            
            foreach (var s in samples)
            {
                fpsSum += s.fps;
                frameTimeSum += s.frameTime;
                memorySum += s.totalMemory;
            }
            
            currentStats.averageFPS = fpsSum / samples.Count;
            currentStats.averageFrameTime = frameTimeSum / samples.Count;
            currentStats.averageMemoryMB = (memorySum / samples.Count) / (1024f * 1024f);
            
            // Find min/max FPS
            currentStats.minFPS = float.MaxValue;
            currentStats.maxFPS = float.MinValue;
            
            foreach (var s in samples)
            {
                if (s.fps < currentStats.minFPS) currentStats.minFPS = s.fps;
                if (s.fps > currentStats.maxFPS) currentStats.maxFPS = s.fps;
            }
        }
    }
    
    public void StartProfiling()
    {
        enableProfiling = true;
        samples.Clear();
        Debug.Log("Performance profiling started");
    }
    
    public void StopProfiling()
    {
        enableProfiling = false;
        Debug.Log("Performance profiling stopped");
    }
    
    public void ClearData()
    {
        samples.Clear();
        Debug.Log("Performance data cleared");
    }
    
    public PerformanceReport GenerateReport()
    {
        if (samples.Count == 0)
        {
            Debug.LogWarning("No performance data to generate report");
            return null;
        }
        
        PerformanceReport report = new PerformanceReport();
        
        // Calculate statistics
        float fpsSum = 0f;
        float frameTimeSum = 0f;
        long memorySum = 0;
        float minFPS = float.MaxValue;
        float maxFPS = float.MinValue;
        long maxMemory = 0;
        
        foreach (var sample in samples)
        {
            fpsSum += sample.fps;
            frameTimeSum += sample.frameTime;
            memorySum += sample.totalMemory;
            
            if (sample.fps < minFPS) minFPS = sample.fps;
            if (sample.fps > maxFPS) maxFPS = sample.fps;
            if (sample.totalMemory > maxMemory) maxMemory = sample.totalMemory;
        }
        
        report.totalSamples = samples.Count;
        report.averageFPS = fpsSum / samples.Count;
        report.averageFrameTime = frameTimeSum / samples.Count;
        report.minFPS = minFPS;
        report.maxFPS = maxFPS;
        report.averageMemoryMB = (memorySum / samples.Count) / (1024f * 1024f);
        report.maxMemoryMB = maxMemory / (1024f * 1024f);
        report.profilingDuration = samples[samples.Count - 1].timestamp - samples[0].timestamp;
        
        // Performance classification
        if (report.averageFPS >= 60f)
            report.performanceGrade = "Excellent";
        else if (report.averageFPS >= 45f)
            report.performanceGrade = "Good";
        else if (report.averageFPS >= 30f)
            report.performanceGrade = "Fair";
        else
            report.performanceGrade = "Poor";
        
        return report;
    }
    
    public void ExportDataToCSV(string fileName = "")
    {
        if (samples.Count == 0)
        {
            Debug.LogWarning("No data to export");
            return;
        }
        
        if (string.IsNullOrEmpty(fileName))
        {
            fileName = $"performance_data_{System.DateTime.Now:yyyyMMdd_HHmmss}.csv";
        }
        
        StringBuilder csv = new StringBuilder();
        
        // Header
        csv.AppendLine("Timestamp,Frame,FPS,FrameTime(ms),TotalMemory(MB),ReservedMemory(MB),MonoMemory(MB),GPUMemory(MB)");
        
        // Data
        foreach (var sample in samples)
        {
            csv.AppendLine($"{sample.timestamp:F2},{sample.frameCount},{sample.fps:F1}," +
                          $"{sample.frameTime:F2},{sample.totalMemory / (1024f * 1024f):F2}," +
                          $"{sample.reservedMemory / (1024f * 1024f):F2}," +
                          $"{sample.monoMemory / (1024f * 1024f):F2}," +
                          $"{sample.gpuMemory / (1024f * 1024f):F2}");
        }
        
        File.WriteAllText(fileName, csv.ToString());
        Debug.Log($"Performance data exported to {fileName}");
    }
    
    public void ExportReportToJSON(string fileName = "")
    {
        PerformanceReport report = GenerateReport();
        if (report == null) return;
        
        if (string.IsNullOrEmpty(fileName))
        {
            fileName = $"performance_report_{System.DateTime.Now:yyyyMMdd_HHmmss}.json";
        }
        
        string json = JsonUtility.ToJson(report, true);
        File.WriteAllText(fileName, json);
        Debug.Log($"Performance report exported to {fileName}");
    }
    
    void OnGUI()
    {
        if (!showRealTimeStats || !displayVisible) return;
        
        GUI.skin.box.fontSize = 12;
        GUI.skin.label.fontSize = 12;
        
        float boxWidth = 300f;
        float boxHeight = 200f;
        Rect boxRect = new Rect(10, 10, boxWidth, boxHeight);
        
        GUI.Box(boxRect, "Performance Monitor");
        
        GUILayout.BeginArea(new Rect(15, 35, boxWidth - 10, boxHeight - 30));
        
        GUILayout.Label($"FPS: {currentStats.currentFPS:F1} (Avg: {currentStats.averageFPS:F1})");
        GUILayout.Label($"Frame Time: {currentStats.currentFrameTime:F2}ms");
        GUILayout.Label($"Memory: {currentStats.currentMemoryMB:F1}MB (Avg: {currentStats.averageMemoryMB:F1}MB)");
        
        if (samples.Count > 0)
        {
            GUILayout.Label($"Min FPS: {currentStats.minFPS:F1}");
            GUILayout.Label($"Max FPS: {currentStats.maxFPS:F1}");
            GUILayout.Label($"Samples: {samples.Count}");
        }
        
        GUILayout.Space(10);
        
        if (GUILayout.Button("Clear Data"))
        {
            ClearData();
        }
        
        if (GUILayout.Button("Export CSV"))
        {
            ExportDataToCSV();
        }
        
        if (GUILayout.Button("Export Report"))
        {
            ExportReportToJSON();
        }
        
        GUILayout.EndArea();
    }
    
    void OnApplicationQuit()
    {
        if (exportDataOnQuit && samples.Count > 0)
        {
            ExportDataToCSV();
            ExportReportToJSON();
        }
    }
    
    // Memory leak detection
    public void DetectMemoryLeaks()
    {
        if (samples.Count < 100) return;
        
        // Check for consistently increasing memory usage
        int recentSamples = Mathf.Min(50, samples.Count);
        long startMemory = samples[samples.Count - recentSamples].totalMemory;
        long endMemory = samples[samples.Count - 1].totalMemory;
        
        float memoryGrowth = (endMemory - startMemory) / (1024f * 1024f);
        
        if (memoryGrowth > 10f) // 10MB growth
        {
            Debug.LogWarning($"Potential memory leak detected! Memory increased by {memoryGrowth:F1}MB");
        }
    }
    
    // Performance bottleneck detection
    public void DetectBottlenecks()
    {
        if (currentStats.averageFPS < 30f)
        {
            Debug.LogWarning("Low FPS detected - potential CPU bottleneck");
        }
        
        if (currentStats.averageFrameTime > 16.67f) // 60 FPS threshold
        {
            Debug.LogWarning($"High frame time detected: {currentStats.averageFrameTime:F2}ms");
        }
        
        if (currentStats.currentMemoryMB > 1000f) // 1GB threshold
        {
            Debug.LogWarning($"High memory usage detected: {currentStats.currentMemoryMB:F1}MB");
        }
    }
}

[System.Serializable]
public class PerformanceSample
{
    public float timestamp;
    public int frameCount;
    public float fps;
    public float frameTime;
    public long totalMemory;
    public long reservedMemory;
    public long unusedMemory;
    public long monoMemory;
    public long gpuMemory;
    public int drawCalls;
    public int triangles;
    public int vertices;
}

[System.Serializable]
public class PerformanceStats
{
    public float currentFPS;
    public float averageFPS;
    public float minFPS;
    public float maxFPS;
    public float currentFrameTime;
    public float averageFrameTime;
    public float currentMemoryMB;
    public float averageMemoryMB;
}

[System.Serializable]
public class PerformanceReport
{
    public int totalSamples;
    public float averageFPS;
    public float minFPS;
    public float maxFPS;
    public float averageFrameTime;
    public float averageMemoryMB;
    public float maxMemoryMB;
    public float profilingDuration;
    public string performanceGrade;
    public string generatedAt = System.DateTime.Now.ToString();
}

// Component for profiling specific objects
public class ObjectProfiler : MonoBehaviour
{
    [Header("Profiling")]
    public bool profileRendering = true;
    public bool profileAnimation = true;
    public bool profilePhysics = true;
    
    private Renderer objectRenderer;
    private Animator objectAnimator;
    private Rigidbody objectRigidbody;
    
    void Start()
    {
        objectRenderer = GetComponent<Renderer>();
        objectAnimator = GetComponent<Animator>();
        objectRigidbody = GetComponent<Rigidbody>();
    }
    
    void Update()
    {
        if (profileRendering && objectRenderer != null)
        {
            ProfileRendering();
        }
        
        if (profileAnimation && objectAnimator != null)
        {
            ProfileAnimation();
        }
        
        if (profilePhysics && objectRigidbody != null)
        {
            ProfilePhysics();
        }
    }
    
    void ProfileRendering()
    {
        // Profile rendering performance
        if (!objectRenderer.isVisible)
        {
            // Object is not visible, rendering cost is minimal
            return;
        }
        
        // Check if object is using expensive materials/shaders
        Material[] materials = objectRenderer.materials;
        foreach (Material mat in materials)
        {
            if (mat.shader.name.Contains("Standard"))
            {
                // Standard shader can be expensive
                Debug.Log($"Object {name} using Standard shader");
            }
        }
    }
    
    void ProfileAnimation()
    {
        // Profile animation performance
        if (objectAnimator.enabled && objectAnimator.runtimeAnimatorController != null)
        {
            // Check for complex animation states
            AnimatorStateInfo stateInfo = objectAnimator.GetCurrentAnimatorStateInfo(0);
            if (stateInfo.length > 10f)
            {
                Debug.Log($"Object {name} has long animation: {stateInfo.length}s");
            }
        }
    }
    
    void ProfilePhysics()
    {
        // Profile physics performance
        if (!objectRigidbody.IsSleeping())
        {
            // Active rigidbody consumes physics processing
            if (objectRigidbody.velocity.magnitude > 10f)
            {
                Debug.Log($"Object {name} has high velocity: {objectRigidbody.velocity.magnitude}");
            }
        }
    }
}
```

## 🚀 AI/LLM Integration
- Automatically identify performance bottlenecks
- Generate optimization recommendations
- Create performance benchmarks and comparisons

## 💡 Key Benefits
- Real-time performance monitoring
- Automated bottleneck detection
- Comprehensive profiling reports