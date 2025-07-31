# @d-Debugging-Profiling-Tools - Unity Performance Analysis and Optimization

## 🎯 Learning Objectives
- Master Unity's built-in debugging and profiling tools
- Implement performance monitoring and optimization strategies
- Understand memory management and garbage collection analysis
- Develop efficient debugging workflows for complex Unity projects

## 🔧 Unity Profiler Deep Dive

### CPU Profiler Analysis
```csharp
// Performance-Aware Code Patterns
using UnityEngine;
using Unity.Profiling;

public class ProfiledGameManager : MonoBehaviour
{
    // Custom profiler markers for detailed analysis
    private static readonly ProfilerMarker s_UpdateMarker = new ProfilerMarker("GameManager.Update");
    private static readonly ProfilerMarker s_AIUpdateMarker = new ProfilerMarker("AI.Update");
    private static readonly ProfilerMarker s_PhysicsUpdateMarker = new ProfilerMarker("Physics.Update");
    
    [Header("Performance Settings")]
    [SerializeField] private int maxAIUpdatesPerFrame = 5;
    [SerializeField] private float aiUpdateInterval = 0.1f;
    
    private float lastAIUpdate;
    private int currentAIIndex;
    private AIController[] aiControllers;
    
    void Start()
    {
        aiControllers = FindObjectsOfType<AIController>();
        Debug.Log($"Found {aiControllers.Length} AI controllers");
    }
    
    void Update()
    {
        using (s_UpdateMarker.Auto())
        {
            UpdateAIControllers();
            UpdatePhysicsCalculations();
            UpdateUI();
        }
    }
    
    private void UpdateAIControllers()
    {
        using (s_AIUpdateMarker.Auto())
        {
            // Spread AI updates across multiple frames
            if (Time.time - lastAIUpdate >= aiUpdateInterval)
            {
                int updatesThisFrame = 0;
                int startIndex = currentAIIndex;
                
                do
                {
                    if (aiControllers[currentAIIndex] != null)
                    {
                        aiControllers[currentAIIndex].UpdateAI();
                        updatesThisFrame++;
                    }
                    
                    currentAIIndex = (currentAIIndex + 1) % aiControllers.Length;
                    
                } while (updatesThisFrame < maxAIUpdatesPerFrame && currentAIIndex != startIndex);
                
                lastAIUpdate = Time.time;
            }
        }
    }
    
    private void UpdatePhysicsCalculations()
    {
        using (s_PhysicsUpdateMarker.Auto())
        {
            // Custom physics calculations that can be profiled
            PerformCustomPhysicsCalculations();
        }
    }
    
    private void PerformCustomPhysicsCalculations()
    {
        // Placeholder for custom physics
    }
    
    private void UpdateUI()
    {
        // UI update logic (can add profiler marker if needed)
    }
}

// Memory-Efficient Object Pooling
public class ObjectPool : MonoBehaviour
{
    [Header("Pool Settings")]
    [SerializeField] private GameObject prefab;
    [SerializeField] private int initialPoolSize = 20;
    [SerializeField] private bool canGrow = true;
    
    private Queue<GameObject> pool = new Queue<GameObject>();
    private static readonly ProfilerMarker s_GetObjectMarker = new ProfilerMarker("ObjectPool.GetObject");
    private static readonly ProfilerMarker s_ReturnObjectMarker = new ProfilerMarker("ObjectPool.ReturnObject");
    
    void Start()
    {
        // Pre-populate pool to avoid allocations during gameplay
        for (int i = 0; i < initialPoolSize; i++)
        {
            GameObject obj = Instantiate(prefab);
            obj.SetActive(false);
            pool.Enqueue(obj);
        }
    }
    
    public GameObject GetObject()
    {
        using (s_GetObjectMarker.Auto())
        {
            if (pool.Count > 0)
            {
                GameObject obj = pool.Dequeue();
                obj.SetActive(true);
                return obj;
            }
            else if (canGrow)
            {
                // Pool can grow if needed (monitor in profiler)
                return Instantiate(prefab);
            }
            
            return null;
        }
    }
    
    public void ReturnObject(GameObject obj)
    {
        using (s_ReturnObjectMarker.Auto())
        {
            obj.SetActive(false);
            pool.Enqueue(obj);
        }
    }
}
```

### Memory Profiler Usage
```csharp
// Memory-Conscious Development Patterns
using UnityEngine;
using System.Collections.Generic;

public class MemoryOptimizedManager : MonoBehaviour
{
    [Header("Memory Management")]
    [SerializeField] private bool enableMemoryLogging = true;
    [SerializeField] private float memoryCheckInterval = 5f;
    
    // Cache frequently accessed components
    private Dictionary<int, Transform> transformCache = new Dictionary<int, Transform>();
    private Dictionary<int, Rigidbody> rigidbodyCache = new Dictionary<int, Rigidbody>();
    
    // String builder for string concatenation (avoid GC)
    private System.Text.StringBuilder stringBuilder = new System.Text.StringBuilder(256);
    
    // Object pools for frequently created/destroyed objects
    private Queue<ParticleSystem> particlePool = new Queue<ParticleSystem>();
    private Queue<AudioSource> audioSourcePool = new Queue<AudioSource>();
    
    void Start()
    {
        if (enableMemoryLogging)
        {
            InvokeRepeating(nameof(LogMemoryUsage), memoryCheckInterval, memoryCheckInterval);
        }
        
        InitializePools();
    }
    
    private void InitializePools()
    {
        // Pre-allocate particle systems
        for (int i = 0; i < 10; i++)
        {
            GameObject particleObj = new GameObject("PooledParticle");
            ParticleSystem ps = particleObj.AddComponent<ParticleSystem>();
            particleObj.SetActive(false);
            particlePool.Enqueue(ps);
        }
        
        // Pre-allocate audio sources
        for (int i = 0; i < 5; i++)
        {
            GameObject audioObj = new GameObject("PooledAudio");
            AudioSource audioSource = audioObj.AddComponent<AudioSource>();
            audioObj.SetActive(false);
            audioSourcePool.Enqueue(audioSource);
        }
    }
    
    private void LogMemoryUsage()
    {
        long memoryUsage = System.GC.GetTotalMemory(false);
        stringBuilder.Clear();
        stringBuilder.Append("Memory Usage: ");
        stringBuilder.Append((memoryUsage / 1024f / 1024f).ToString("F2"));
        stringBuilder.Append(" MB");
        
        Debug.Log(stringBuilder.ToString());
        
        // Log additional memory stats
        Debug.Log($"Managed Heap: {Unity.Profiling.Profiler.GetMonoUsedSize() / 1024f / 1024f:F2} MB");
        Debug.Log($"GFX Memory: {Unity.Profiling.Profiler.GetAllocatedMemoryForGraphicsDriver() / 1024f / 1024f:F2} MB");
    }
    
    // Efficient component caching
    public T GetCachedComponent<T>(GameObject obj) where T : Component
    {
        int instanceID = obj.GetInstanceID();
        
        if (typeof(T) == typeof(Transform))
        {
            if (!transformCache.ContainsKey(instanceID))
            {
                transformCache[instanceID] = obj.transform;
            }
            return transformCache[instanceID] as T;
        }
        else if (typeof(T) == typeof(Rigidbody))
        {
            if (!rigidbodyCache.ContainsKey(instanceID))
            {
                rigidbodyCache[instanceID] = obj.GetComponent<Rigidbody>();
            }
            return rigidbodyCache[instanceID] as T;
        }
        
        // Fallback to standard GetComponent
        return obj.GetComponent<T>();
    }
    
    // Memory-efficient string operations
    public string BuildStatusString(float health, float mana, int level)
    {
        stringBuilder.Clear();
        stringBuilder.Append("Health: ");
        stringBuilder.Append(health.ToString("F1"));
        stringBuilder.Append(" | Mana: ");
        stringBuilder.Append(mana.ToString("F1"));
        stringBuilder.Append(" | Level: ");
        stringBuilder.Append(level);
        
        return stringBuilder.ToString();
    }
    
    void OnDestroy()
    {
        // Clear caches to prevent memory leaks
        transformCache.Clear();
        rigidbodyCache.Clear();
    }
}
```

## 🔍 Advanced Debugging Techniques

### Visual Debugging Tools
```csharp
// Advanced Debug Visualization System
using UnityEngine;
using System.Collections.Generic;

public class DebugVisualization : MonoBehaviour
{
    [Header("Debug Settings")]
    [SerializeField] private bool enableDebugDraw = true;
    [SerializeField] private Color rayColor = Color.red;
    [SerializeField] private Color sphereColor = Color.blue;
    [SerializeField] private float debugDuration = 0.1f;
    
    private List<DebugRay> debugRays = new List<DebugRay>();
    private List<DebugSphere> debugSpheres = new List<DebugSphere>();
    
    private struct DebugRay
    {
        public Vector3 origin;
        public Vector3 direction;
        public Color color;
        public float duration;
        public float startTime;
    }
    
    private struct DebugSphere
    {
        public Vector3 center;
        public float radius;
        public Color color;
        public float duration;
        public float startTime;
    }
    
    public static DebugVisualization Instance { get; private set; }
    
    void Awake()
    {
        Instance = this;
    }
    
    void Update()
    {
        if (!enableDebugDraw) return;
        
        UpdateDebugRays();
        UpdateDebugSpheres();
    }
    
    public void DrawRay(Vector3 origin, Vector3 direction, Color color, float duration = 0.1f)
    {
        if (!enableDebugDraw) return;
        
        debugRays.Add(new DebugRay
        {
            origin = origin,
            direction = direction,
            color = color,
            duration = duration,
            startTime = Time.time
        });
    }
    
    public void DrawSphere(Vector3 center, float radius, Color color, float duration = 0.1f)
    {
        if (!enableDebugDraw) return;
        
        debugSpheres.Add(new DebugSphere
        {
            center = center,
            radius = radius,
            color = color,
            duration = duration,
            startTime = Time.time
        });
    }
    
    private void UpdateDebugRays()
    {
        for (int i = debugRays.Count - 1; i >= 0; i--)
        {
            DebugRay ray = debugRays[i];
            
            if (Time.time - ray.startTime > ray.duration)
            {
                debugRays.RemoveAt(i);
                continue;
            }
            
            Debug.DrawRay(ray.origin, ray.direction, ray.color, debugDuration);
        }
    }
    
    private void UpdateDebugSpheres()
    {
        for (int i = debugSpheres.Count - 1; i >= 0; i--)
        {
            DebugSphere sphere = debugSpheres[i];
            
            if (Time.time - sphere.startTime > sphere.duration)
            {
                debugSpheres.RemoveAt(i);
                continue;
            }
            
            DrawWireSphere(sphere.center, sphere.radius, sphere.color);
        }
    }
    
    private void DrawWireSphere(Vector3 center, float radius, Color color)
    {
        int segments = 16;
        float angleStep = 360f / segments;
        
        // Draw horizontal circle
        for (int i = 0; i < segments; i++)
        {
            float angle1 = i * angleStep * Mathf.Deg2Rad;
            float angle2 = (i + 1) % segments * angleStep * Mathf.Deg2Rad;
            
            Vector3 point1 = center + new Vector3(Mathf.Cos(angle1), 0, Mathf.Sin(angle1)) * radius;
            Vector3 point2 = center + new Vector3(Mathf.Cos(angle2), 0, Mathf.Sin(angle2)) * radius;
            
            Debug.DrawLine(point1, point2, color, debugDuration);
        }
        
        // Draw vertical circle
        for (int i = 0; i < segments; i++)
        {
            float angle1 = i * angleStep * Mathf.Deg2Rad;
            float angle2 = (i + 1) % segments * angleStep * Mathf.Deg2Rad;
            
            Vector3 point1 = center + new Vector3(0, Mathf.Cos(angle1), Mathf.Sin(angle1)) * radius;
            Vector3 point2 = center + new Vector3(0, Mathf.Cos(angle2), Mathf.Sin(angle2)) * radius;
            
            Debug.DrawLine(point1, point2, color, debugDuration);
        }
    }
}

// Usage example in gameplay code
public class PlayerController : MonoBehaviour
{
    [Header("Ground Check")]
    [SerializeField] private float groundCheckDistance = 0.1f;
    [SerializeField] private LayerMask groundMask = 1;
    
    private bool isGrounded;
    
    void Update()
    {
        CheckGroundStatus();
        
        // Visualize ground check ray
        if (DebugVisualization.Instance != null)
        {
            Color rayColor = isGrounded ? Color.green : Color.red;
            DebugVisualization.Instance.DrawRay(transform.position, Vector3.down * groundCheckDistance, rayColor, 0.1f);
        }
    }
    
    private void CheckGroundStatus()
    {
        isGrounded = Physics.Raycast(transform.position, Vector3.down, groundCheckDistance, groundMask);
    }
}
```

### Frame Rate Analysis Tools
```csharp
// Comprehensive Frame Rate Monitor
using UnityEngine;
using System.Collections.Generic;

public class FrameRateMonitor : MonoBehaviour
{
    [Header("Display Settings")]
    [SerializeField] private bool showOnScreen = true;
    [SerializeField] private KeyCode toggleKey = KeyCode.F1;
    [SerializeField] private int fontSize = 20;
    
    [Header("Monitoring Settings")]
    [SerializeField] private float updateInterval = 0.5f;
    [SerializeField] private int historyLength = 60;
    
    private float fps;
    private float minFps = float.MaxValue;
    private float maxFps = 0f;
    private float avgFps;
    
    private Queue<float> fpsHistory = new Queue<float>();
    private float nextUpdateTime;
    
    private GUIStyle guiStyle;
    private Rect displayRect;
    
    void Start()
    {
        // Initialize GUI style
        guiStyle = new GUIStyle();
        guiStyle.fontSize = fontSize;
        guiStyle.normal.textColor = Color.white;
        
        displayRect = new Rect(10, 10, 300, 150);
    }
    
    void Update()
    {
        // Toggle display
        if (Input.GetKeyDown(toggleKey))
        {
            showOnScreen = !showOnScreen;
        }
        
        // Calculate current FPS
        fps = 1f / Time.unscaledDeltaTime;
        
        // Update statistics
        if (Time.time >= nextUpdateTime)
        {
            UpdateStatistics();
            nextUpdateTime = Time.time + updateInterval;
        }
    }
    
    private void UpdateStatistics()
    {
        // Add to history
        fpsHistory.Enqueue(fps);
        
        // Maintain history length
        while (fpsHistory.Count > historyLength)
        {
            fpsHistory.Dequeue();
        }
        
        // Update min/max
        minFps = Mathf.Min(minFps, fps);
        maxFps = Mathf.Max(maxFps, fps);
        
        // Calculate average
        if (fpsHistory.Count > 0)
        {
            float sum = 0f;
            foreach (float f in fpsHistory)
            {
                sum += f;
            }
            avgFps = sum / fpsHistory.Count;
        }
    }
    
    void OnGUI()
    {
        if (!showOnScreen) return;
        
        // Background
        GUI.Box(displayRect, "");
        
        // FPS Information
        string displayText = $"FPS: {fps:F1}\n" +
                           $"Min: {minFps:F1}\n" +
                           $"Max: {maxFps:F1}\n" +
                           $"Avg: {avgFps:F1}\n" +
                           $"Frame Time: {(1000f / fps):F2}ms\n" +
                           $"Toggle: {toggleKey}";
        
        GUI.Label(new Rect(displayRect.x + 5, displayRect.y + 5, displayRect.width - 10, displayRect.height - 10), 
                  displayText, guiStyle);
    }
    
    // Reset statistics (useful for testing)
    [ContextMenu("Reset Statistics")]
    public void ResetStatistics()
    {
        minFps = float.MaxValue;
        maxFps = 0f;
        fpsHistory.Clear();
    }
    
    // Log detailed frame time analysis
    public void LogFrameAnalysis()
    {
        Debug.Log($"=== Frame Rate Analysis ===");
        Debug.Log($"Current FPS: {fps:F2}");
        Debug.Log($"Min FPS: {minFps:F2}");
        Debug.Log($"Max FPS: {maxFps:F2}");
        Debug.Log($"Average FPS: {avgFps:F2}");
        Debug.Log($"Frame Time: {(1000f / fps):F2}ms");
        Debug.Log($"History Count: {fpsHistory.Count}");
        
        // Log performance warnings
        if (fps < 30f)
        {
            Debug.LogWarning("Low FPS detected! Consider performance optimization.");
        }
        
        if (maxFps - minFps > 30f)
        {
            Debug.LogWarning("High FPS variance detected! Frame rate is unstable.");
        }
    }
}
```

## 🔍 Unity Console and Logging

### Advanced Logging System
```csharp
// Comprehensive Logging System
using UnityEngine;
using System.IO;
using System;

public static class GameLogger
{
    public enum LogLevel
    {
        Debug = 0,
        Info = 1,
        Warning = 2,
        Error = 3,
        Fatal = 4
    }
    
    private static LogLevel currentLogLevel = LogLevel.Debug;
    private static bool writeToFile = true;
    private static string logFilePath;
    private static StreamWriter logWriter;
    
    static GameLogger()
    {
        InitializeLogger();
    }
    
    private static void InitializeLogger()
    {
        if (writeToFile)
        {
            string logDirectory = Path.Combine(Application.persistentDataPath, "Logs");
            Directory.CreateDirectory(logDirectory);
            
            string timestamp = DateTime.Now.ToString("yyyy-MM-dd_HH-mm-ss");
            logFilePath = Path.Combine(logDirectory, $"game_log_{timestamp}.txt");
            
            try
            {
                logWriter = new StreamWriter(logFilePath, true);
                logWriter.AutoFlush = true;
                
                WriteToFile($"=== Game Log Started at {DateTime.Now} ===");
                WriteToFile($"Unity Version: {Application.unityVersion}");
                WriteToFile($"Platform: {Application.platform}");
                WriteToFile($"Device: {SystemInfo.deviceName} ({SystemInfo.deviceModel})");
                WriteToFile("==========================================");
            }
            catch (Exception e)
            {
                Debug.LogError($"Failed to initialize log file: {e.Message}");
                writeToFile = false;
            }
        }
    }
    
    public static void SetLogLevel(LogLevel level)
    {
        currentLogLevel = level;
        LogInfo($"Log level set to: {level}");
    }
    
    public static void LogDebug(string message, UnityEngine.Object context = null)
    {
        Log(LogLevel.Debug, message, context);
    }
    
    public static void LogInfo(string message, UnityEngine.Object context = null)
    {
        Log(LogLevel.Info, message, context);
    }
    
    public static void LogWarning(string message, UnityEngine.Object context = null)
    {
        Log(LogLevel.Warning, message, context);
    }
    
    public static void LogError(string message, UnityEngine.Object context = null)
    {
        Log(LogLevel.Error, message, context);
    }
    
    public static void LogFatal(string message, UnityEngine.Object context = null)
    {
        Log(LogLevel.Fatal, message, context);
    }
    
    private static void Log(LogLevel level, string message, UnityEngine.Object context)
    {
        if (level < currentLogLevel) return;
        
        string timestamp = DateTime.Now.ToString("HH:mm:ss.fff");
        string formattedMessage = $"[{timestamp}] [{level}] {message}";
        
        // Log to Unity Console
        switch (level)
        {
            case LogLevel.Debug:
            case LogLevel.Info:
                Debug.Log(formattedMessage, context);
                break;
            case LogLevel.Warning:
                Debug.LogWarning(formattedMessage, context);
                break;
            case LogLevel.Error:
            case LogLevel.Fatal:
                Debug.LogError(formattedMessage, context);
                break;
        }
        
        // Log to file
        WriteToFile(formattedMessage);
        
        // Handle fatal errors
        if (level == LogLevel.Fatal)
        {
            HandleFatalError(message);
        }
    }
    
    private static void WriteToFile(string message)
    {
        if (writeToFile && logWriter != null)
        {
            try
            {
                logWriter.WriteLine(message);
            }
            catch (Exception e)
            {
                Debug.LogError($"Failed to write to log file: {e.Message}");
                writeToFile = false;
            }
        }
    }
    
    private static void HandleFatalError(string message)
    {
        // Perform emergency save operations
        WriteToFile("FATAL ERROR - Attempting emergency save...");
        
        // Try to save critical game state
        try
        {
            // SaveGame.EmergencySave(); // Your save system
            WriteToFile("Emergency save completed");
        }
        catch (Exception e)
        {
            WriteToFile($"Emergency save failed: {e.Message}");
        }
    }
    
    public static void LogException(Exception exception, UnityEngine.Object context = null)
    {
        string message = $"Exception: {exception.GetType().Name} - {exception.Message}\nStack Trace:\n{exception.StackTrace}";
        LogError(message, context);
    }
    
    public static void FlushLogs()
    {
        logWriter?.Flush();
    }
    
    public static void Shutdown()
    {
        WriteToFile($"=== Game Log Ended at {DateTime.Now} ===");
        logWriter?.Close();
        logWriter = null;
    }
}

// Usage example in game systems
public class GameManager : MonoBehaviour
{
    void Start()
    {
        GameLogger.LogInfo("GameManager started");
        GameLogger.SetLogLevel(GameLogger.LogLevel.Info); // Filter out debug logs in builds
    }
    
    void Update()
    {
        try
        {
            // Game logic that might throw exceptions
            ProcessGameLogic();
        }
        catch (Exception e)
        {
            GameLogger.LogException(e, this);
        }
    }
    
    private void ProcessGameLogic()
    {
        // Placeholder for game logic
    }
    
    void OnApplicationPause(bool pauseStatus)
    {
        GameLogger.LogInfo($"Application pause status: {pauseStatus}");
        GameLogger.FlushLogs(); // Ensure logs are written
    }
    
    void OnApplicationQuit()
    {
        GameLogger.LogInfo("Application quitting");
        GameLogger.Shutdown();
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Performance Analysis Automation
```
Generate Unity performance analysis tools:
- Input: [profiler data, frame rate logs, memory usage patterns]
- Output: Optimization recommendations, bottleneck identification, code suggestions
- Include: Automated profiling, regression detection, performance comparisons

Create intelligent debugging assistant:
- Features: [exception analysis, log pattern recognition, debug strategy suggestions]
- Integration: [Unity Editor, Visual Studio, team communication tools]
- Learning: [project-specific issues, team debugging patterns, solution effectiveness]

Design Unity performance monitoring system:
- Metrics: [FPS, memory usage, draw calls, physics performance]
- Alerts: [performance degradation, memory leaks, optimization opportunities]
- Reports: [trend analysis, performance comparisons, team dashboards]
```

### Debugging Workflow Enhancement
```
Build automated Unity debugging workflow:
- Analysis: [console errors, performance spikes, memory allocation patterns]
- Suggestions: [debugging strategies, profiler settings, optimization priorities]
- Documentation: [issue reproduction steps, solution tracking, knowledge base]

Generate Unity profiling training materials:
- Content: [profiler usage guides, optimization techniques, best practices]
- Format: [interactive tutorials, video scripts, hands-on exercises]
- Focus: [common performance issues, platform-specific optimization, team workflows]
```

## 💡 Key Highlights

### Essential Unity Profiler Features
- **CPU Profiler: Identify expensive scripts and functions**
- **Memory Profiler: Track allocations and garbage collection**
- **Rendering Profiler: Analyze draw calls and GPU usage**
- **Audio Profiler: Monitor audio processing performance**
- **Physics Profiler: Debug physics calculations and collisions**

### Critical Performance Metrics
- **Frame Rate: Target 60 FPS for smooth gameplay**
- **Frame Time: Consistent frame times prevent stuttering**
- **Memory Usage: Monitor heap size and GC frequency**
- **Draw Calls: Minimize for better rendering performance**
- **Batching: Use static/dynamic batching for optimization**

### Debugging Best Practices
- **Use profiler markers for custom code sections**
- **Enable Development Build for detailed profiling**
- **Profile on target devices, not just editor**
- **Use conditional compilation for debug code**
- **Implement comprehensive logging system**

### Memory Optimization Strategies
- **Object pooling for frequently created/destroyed objects**
- **Texture compression and asset optimization**
- **Audio compression and streaming**
- **Garbage collection minimization techniques**
- **Resource loading and unloading management**

### Advanced Debugging Techniques
- **Visual debugging with gizmos and debug draw**
- **Custom profiler markers for specific systems**
- **Frame-by-frame analysis for complex issues**
- **Memory snapshot comparison for leak detection**
- **Performance regression testing in CI/CD pipelines**