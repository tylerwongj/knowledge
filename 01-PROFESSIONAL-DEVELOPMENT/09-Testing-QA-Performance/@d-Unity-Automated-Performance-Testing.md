# @d-Unity-Automated-Performance-Testing - Comprehensive Performance Validation Systems

## 🎯 Learning Objectives
- Implement automated performance testing pipelines for Unity projects
- Create comprehensive performance regression detection systems
- Master Unity's performance testing tools and custom metrics collection
- Design scalable performance monitoring for continuous integration

## 🔧 Core Performance Testing Framework

### Automated Performance Test Suite
```csharp
using UnityEngine;
using UnityEngine.TestTools;
using Unity.PerformanceTesting;
using System.Collections;
using System.Collections.Generic;
using NUnit.Framework;

/// <summary>
/// Comprehensive automated performance test suite for Unity projects
/// Provides standardized performance benchmarking and regression detection
/// </summary>
public class UnityPerformanceTestSuite
{
    [UnityTest, Performance]
    [Category("Performance")]
    [Timeout(60000)] // 60 second timeout
    public IEnumerator TestFrameRatePerformance()
    {
        // Setup test scene
        yield return SetupPerformanceTestScene();
        
        // Allow scene to stabilize
        yield return new WaitForSeconds(2f);
        
        // Measure frame rate over sustained period
        using (Measure.Frames().DontRecordFramerate())
        {
            yield return Measure.Frames()
                .MeasurementCount(300) // 5 seconds at 60 FPS
                .Run();
        }
        
        // Cleanup
        yield return CleanupTestScene();
    }
    
    [UnityTest, Performance]
    public IEnumerator TestMemoryAllocationUnderLoad()
    {
        yield return SetupMemoryTestScene();
        
        // Baseline memory measurement
        var initialMemory = System.GC.GetTotalMemory(true);
        
        // Simulate gameplay load for memory testing
        using (Measure.ProfilerMarkers("Memory.Allocation"))
        {
            for (int i = 0; i < 100; i++)
            {
                // Simulate typical gameplay operations
                SpawnGameObjects(10);
                yield return null;
                
                if (i % 20 == 0)
                {
                    // Periodic cleanup to simulate realistic usage
                    CleanupSomeObjects();
                    yield return new WaitForEndOfFrame();
                }
            }
        }
        
        // Measure memory after operations
        var finalMemory = System.GC.GetTotalMemory(false);
        var memoryDelta = finalMemory - initialMemory;
        
        // Record custom metric
        using (Measure.Custom("Memory.AllocationDelta", "MB"))
        {
            Measure.Custom("Memory.AllocationDelta", "MB")
                .SampleGroup("MemoryTest")
                .MeasurementCount(1)
                .Run(() => memoryDelta / 1024f / 1024f);
        }
        
        yield return CleanupTestScene();
    }
    
    [UnityTest, Performance]
    public IEnumerator TestLoadingTimePerformance()
    {
        var scenes = new string[] 
        { 
            "MainMenu", "GameLevel1", "GameLevel2", "GameLevel3" 
        };
        
        foreach (var sceneName in scenes)
        {
            using (Measure.Method($"Scene.LoadTime.{sceneName}"))
            {
                var stopwatch = System.Diagnostics.Stopwatch.StartNew();
                
                var asyncLoad = UnityEngine.SceneManagement.SceneManager.LoadSceneAsync(sceneName);
                asyncLoad.allowSceneActivation = false;
                
                // Wait for scene to load (but not activate)
                while (asyncLoad.progress < 0.9f)
                {
                    yield return null;
                }
                
                stopwatch.Stop();
                
                // Record loading time
                Measure.Custom($"Scene.LoadTime.{sceneName}", "ms")
                    .SampleGroup("LoadingTimes")
                    .MeasurementCount(1)
                    .Run(() => stopwatch.ElapsedMilliseconds);
                
                // Activate and then immediately unload
                asyncLoad.allowSceneActivation = true;
                yield return asyncLoad;
                
                // Unload the scene
                yield return UnityEngine.SceneManagement.SceneManager.UnloadSceneAsync(sceneName);
            }
        }
    }
    
    [UnityTest, Performance]
    public IEnumerator TestRenderingPerformance()
    {
        yield return SetupRenderingTestScene();
        
        // Test various rendering scenarios
        var renderingScenarios = new[]
        {
            new { Name = "LowComplexity", ObjectCount = 50, LightCount = 2 },
            new { Name = "MediumComplexity", ObjectCount = 200, LightCount = 4 },
            new { Name = "HighComplexity", ObjectCount = 500, LightCount = 8 }
        };
        
        foreach (var scenario in renderingScenarios)
        {
            // Setup scenario
            SetupRenderingScenario(scenario.ObjectCount, scenario.LightCount);
            yield return new WaitForSeconds(1f); // Stabilize
            
            // Measure GPU performance
            using (Measure.ProfilerMarkers($"GPU.{scenario.Name}"))
            {
                using (Measure.Custom($"DrawCalls.{scenario.Name}", "calls"))
                {
                    for (int frame = 0; frame < 60; frame++) // 1 second of measurement
                    {
                        var drawCalls = UnityStats.drawCalls;
                        Measure.Custom($"DrawCalls.{scenario.Name}", "calls")
                            .SampleGroup($"Rendering.{scenario.Name}")
                            .MeasurementCount(1)
                            .Run(() => drawCalls);
                        
                        yield return null;
                    }
                }
            }
            
            // Cleanup scenario
            CleanupRenderingScenario();
        }
        
        yield return CleanupTestScene();
    }
    
    private IEnumerator SetupPerformanceTestScene()
    {
        // Create standardized performance test environment
        var testScene = new GameObject("PerformanceTestRoot");
        
        // Add consistent lighting
        var light = new GameObject("TestLight");
        light.transform.SetParent(testScene.transform);
        var lightComponent = light.AddComponent<Light>();
        lightComponent.type = LightType.Directional;
        lightComponent.intensity = 1.0f;
        
        // Add test camera
        var cameraGO = new GameObject("TestCamera");
        cameraGO.transform.SetParent(testScene.transform);
        var camera = cameraGO.AddComponent<Camera>();
        camera.transform.position = new Vector3(0, 5, -10);
        camera.transform.LookAt(Vector3.zero);
        
        yield return null; // Wait one frame for setup
    }
}
```

### Custom Performance Metrics Collection
```csharp
/// <summary>
/// Advanced performance metrics collection system
/// Provides detailed insights beyond basic Unity profiler data
/// </summary>
public class AdvancedPerformanceMetrics : MonoBehaviour
{
    [Header("Measurement Settings")]
    public float measurementInterval = 0.1f;
    public int maxSampleHistory = 1000;
    public bool enableGPUMetrics = true;
    public bool enableMemoryTracking = true;
    
    [Header("Thresholds")]
    public float frameTimeWarningMs = 20f;
    public float frameTimeCriticalMs = 33f;
    public long memoryWarningMB = 500;
    public long memoryCriticalMB = 800;
    
    private Queue<PerformanceSample> sampleHistory;
    private PerformanceProfiler profiler;
    private MemoryProfiler memoryProfiler;
    private GPUProfiler gpuProfiler;
    
    void Start()
    {
        sampleHistory = new Queue<PerformanceSample>();
        profiler = new PerformanceProfiler();
        memoryProfiler = new MemoryProfiler();
        
        if (enableGPUMetrics)
        {
            gpuProfiler = new GPUProfiler();
        }
        
        InvokeRepeating(nameof(CollectPerformanceMetrics), 0f, measurementInterval);
    }
    
    private void CollectPerformanceMetrics()
    {
        var sample = new PerformanceSample
        {
            timestamp = Time.realtimeSinceStartup,
            frameTime = Time.unscaledDeltaTime * 1000f, // Convert to milliseconds
            frameRate = 1f / Time.unscaledDeltaTime,
            
            // CPU metrics
            cpuUsage = profiler.GetCPUUsage(),
            mainThreadTime = profiler.GetMainThreadTime(),
            renderThreadTime = profiler.GetRenderThreadTime(),
            
            // Memory metrics
            totalMemoryMB = enableMemoryTracking ? memoryProfiler.GetTotalMemoryMB() : 0,
            gcMemoryMB = enableMemoryTracking ? memoryProfiler.GetGCMemoryMB() : 0,
            nativeMemoryMB = enableMemoryTracking ? memoryProfiler.GetNativeMemoryMB() : 0,
            
            // GPU metrics (if available)
            gpuFrameTime = enableGPUMetrics ? gpuProfiler?.GetGPUFrameTime() ?? 0 : 0,
            drawCalls = UnityStats.drawCalls,
            triangles = UnityStats.triangles,
            vertices = UnityStats.vertices,
            
            // Unity-specific metrics
            batchedDrawCalls = UnityStats.batchedDrawCalls,
            dynamicBatchedDrawCalls = UnityStats.dynamicBatchedDrawCalls,
            staticBatchedDrawCalls = UnityStats.staticBatchedDrawCalls,
            instancedBatchedDrawCalls = UnityStats.instancedBatchedDrawCalls
        };
        
        // Store sample
        sampleHistory.Enqueue(sample);
        
        // Maintain sample history size
        while (sampleHistory.Count > maxSampleHistory)
        {
            sampleHistory.Dequeue();
        }
        
        // Check for performance issues
        CheckPerformanceThresholds(sample);
        
        // Send to performance testing framework if running tests
        if (IsRunningPerformanceTests())
        {
            RecordTestMetrics(sample);
        }
    }
    
    private void CheckPerformanceThresholds(PerformanceSample sample)
    {
        // Frame time warnings
        if (sample.frameTime > frameTimeCriticalMs)
        {
            Debug.LogWarning($"CRITICAL: Frame time {sample.frameTime:F2}ms exceeds threshold {frameTimeCriticalMs}ms");
        }
        else if (sample.frameTime > frameTimeWarningMs)
        {
            Debug.LogWarning($"WARNING: Frame time {sample.frameTime:F2}ms exceeds threshold {frameTimeWarningMs}ms");
        }
        
        // Memory warnings
        if (sample.totalMemoryMB > memoryCriticalMB)
        {
            Debug.LogWarning($"CRITICAL: Memory usage {sample.totalMemoryMB}MB exceeds threshold {memoryCriticalMB}MB");
        }
        else if (sample.totalMemoryMB > memoryWarningMB)
        {
            Debug.LogWarning($"WARNING: Memory usage {sample.totalMemoryMB}MB exceeds threshold {memoryWarningMB}MB");
        }
    }
    
    public PerformanceReport GenerateReport(float timeWindowSeconds = 60f)
    {
        var cutoffTime = Time.realtimeSinceStartup - timeWindowSeconds;
        var recentSamples = sampleHistory.Where(s => s.timestamp >= cutoffTime).ToList();
        
        if (recentSamples.Count == 0)
        {
            return new PerformanceReport { IsValid = false };
        }
        
        return new PerformanceReport
        {
            IsValid = true,
            TimeWindow = timeWindowSeconds,
            SampleCount = recentSamples.Count,
            
            // Frame rate statistics
            AverageFrameRate = recentSamples.Average(s => s.frameRate),
            MinFrameRate = recentSamples.Min(s => s.frameRate),
            MaxFrameRate = recentSamples.Max(s => s.frameRate),
            FrameRateStdDev = CalculateStandardDeviation(recentSamples.Select(s => s.frameRate)),
            
            // Frame time statistics  
            AverageFrameTime = recentSamples.Average(s => s.frameTime),
            MaxFrameTime = recentSamples.Max(s => s.frameTime),
            FrameTimeP95 = CalculatePercentile(recentSamples.Select(s => s.frameTime), 0.95f),
            FrameTimeP99 = CalculatePercentile(recentSamples.Select(s => s.frameTime), 0.99f),
            
            // Memory statistics
            AverageMemoryMB = recentSamples.Average(s => s.totalMemoryMB),
            MaxMemoryMB = recentSamples.Max(s => s.totalMemoryMB),
            MinMemoryMB = recentSamples.Min(s => s.totalMemoryMB),
            
            // Rendering statistics
            AverageDrawCalls = recentSamples.Average(s => s.drawCalls),
            MaxDrawCalls = recentSamples.Max(s => s.drawCalls),
            AverageTriangles = recentSamples.Average(s => s.triangles)
        };
    }
}

[System.Serializable]
public class PerformanceSample
{
    public float timestamp;
    public float frameTime;
    public float frameRate;
    
    // CPU metrics
    public float cpuUsage;
    public float mainThreadTime;
    public float renderThreadTime;
    
    // Memory metrics
    public long totalMemoryMB;
    public long gcMemoryMB;
    public long nativeMemoryMB;
    
    // GPU metrics
    public float gpuFrameTime;
    public int drawCalls;
    public int triangles;
    public int vertices;
    
    // Batching metrics
    public int batchedDrawCalls;
    public int dynamicBatchedDrawCalls;
    public int staticBatchedDrawCalls;
    public int instancedBatchedDrawCalls;
}
```

### CI/CD Performance Integration
```csharp
/// <summary>
/// Continuous Integration performance testing integration
/// Automatically runs performance tests and tracks regressions
/// </summary>
public class CIPerformanceIntegration
{
    [MenuItem("Tools/Performance/Run CI Performance Tests")]
    public static void RunCIPerformanceTests()
    {
        var testRunner = new PerformanceTestRunner();
        testRunner.RunAllTests();
    }
    
    public class PerformanceTestRunner
    {
        private List<PerformanceTestResult> testResults;
        private PerformanceBaseline baseline;
        
        public void RunAllTests()
        {
            testResults = new List<PerformanceTestResult>();
            LoadPerformanceBaseline();
            
            Debug.Log("Starting CI Performance Test Suite...");
            
            // Run standardized performance tests
            RunFrameRateTests();
            RunMemoryTests();
            RunLoadingTimeTests();
            RunRenderingTests();
            
            // Analyze results against baseline
            AnalyzeResultsAgainstBaseline();
            
            // Generate reports
            GenerateJUnitReport();
            GenerateHTMLReport();
            GenerateJSONReport();
            
            // Check for regressions
            CheckForRegressions();
        }
        
        private void RunFrameRateTests()
        {
            var scenes = GetTestScenes();
            
            foreach (var sceneName in scenes)
            {
                var result = new PerformanceTestResult
                {
                    TestName = $"FrameRate_{sceneName}",
                    Category = "Performance",
                    StartTime = System.DateTime.UtcNow
                };
                
                try
                {
                    // Load scene and measure performance
                    var sceneLoadOp = UnityEngine.SceneManagement.SceneManager.LoadSceneAsync(sceneName);
                    while (!sceneLoadOp.isDone)
                    {
                        System.Threading.Thread.Sleep(16); // ~60fps equivalent
                    }
                    
                    // Stabilization period
                    System.Threading.Thread.Sleep(2000);
                    
                    // Measurement period
                    var samples = new List<float>();
                    var startTime = Time.realtimeSinceStartup;
                    
                    while (Time.realtimeSinceStartup - startTime < 10f) // 10 second test
                    {
                        samples.Add(1f / Time.unscaledDeltaTime);
                        System.Threading.Thread.Sleep(16);
                    }
                    
                    result.Metrics = new Dictionary<string, float>
                    {
                        ["AverageFrameRate"] = samples.Average(),
                        ["MinFrameRate"] = samples.Min(),
                        ["MaxFrameRate"] = samples.Max(),
                        ["FrameRateStdDev"] = CalculateStandardDeviation(samples)
                    };
                    
                    result.Success = true;
                    result.Message = $"Frame rate test completed successfully";
                }
                catch (System.Exception ex)
                {
                    result.Success = false;
                    result.Message = $"Frame rate test failed: {ex.Message}";
                }
                finally
                {
                    result.EndTime = System.DateTime.UtcNow;
                    result.Duration = result.EndTime - result.StartTime;
                    testResults.Add(result);
                }
            }
        }
        
        private void CheckForRegressions()
        {
            var regressions = new List<string>();
            
            foreach (var result in testResults)
            {
                if (!result.Success) continue;
                
                var baselineResult = baseline.GetResult(result.TestName);
                if (baselineResult == null) continue;
                
                foreach (var metric in result.Metrics)
                {
                    var baselineValue = baselineResult.GetMetric(metric.Key);
                    if (baselineValue == 0) continue;
                    
                    var changePercent = (metric.Value - baselineValue) / baselineValue * 100f;
                    
                    // Check for significant regressions (>5% degradation)
                    if (changePercent < -5f)
                    {
                        regressions.Add($"{result.TestName}.{metric.Key}: {changePercent:F1}% regression");
                    }
                }
            }
            
            if (regressions.Count > 0)
            {
                var regressionMessage = "Performance Regressions Detected:\n" + 
                                      string.Join("\n", regressions);
                
                Debug.LogError(regressionMessage);
                
                // Fail CI build if regressions detected
                EditorApplication.Exit(1);
            }
            else
            {
                Debug.Log("No performance regressions detected.");
            }
        }
        
        private void GenerateJUnitReport()
        {
            var xml = new System.Xml.XmlDocument();
            var testSuite = xml.CreateElement("testsuite");
            testSuite.SetAttribute("name", "Unity Performance Tests");
            testSuite.SetAttribute("tests", testResults.Count.ToString());
            testSuite.SetAttribute("failures", testResults.Count(r => !r.Success).ToString());
            testSuite.SetAttribute("time", testResults.Sum(r => r.Duration.TotalSeconds).ToString("F2"));
            
            foreach (var result in testResults)
            {
                var testCase = xml.CreateElement("testcase");
                testCase.SetAttribute("classname", "UnityPerformance");
                testCase.SetAttribute("name", result.TestName);
                testCase.SetAttribute("time", result.Duration.TotalSeconds.ToString("F2"));
                
                if (!result.Success)
                {
                    var failure = xml.CreateElement("failure");
                    failure.SetAttribute("message", result.Message);
                    testCase.AppendChild(failure);
                }
                
                testSuite.AppendChild(testCase);
            }
            
            xml.AppendChild(testSuite);
            xml.Save("Assets/TestResults/performance-results.xml");
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities
- **Test Generation**: "Generate Unity performance tests for mobile game with 100+ enemies"
- **Threshold Optimization**: "Analyze performance data to recommend optimal warning thresholds"
- **Report Analysis**: "Summarize performance regression trends from CI test results"
- **Test Strategy**: "Design comprehensive performance testing strategy for Unity VR application"

## 💡 Key Automated Performance Testing Highlights
- **Standardized Benchmarks**: Create consistent, repeatable performance measurements
- **Regression Detection**: Automatically identify performance degradations in CI pipeline
- **Multi-Metric Analysis**: Track frame rate, memory, GPU, and loading time metrics
- **Historical Trending**: Monitor performance evolution over time and releases
- **Threshold-Based Alerts**: Automatic warnings for performance issues
- **Cross-Platform Testing**: Validate performance across target platforms and devices