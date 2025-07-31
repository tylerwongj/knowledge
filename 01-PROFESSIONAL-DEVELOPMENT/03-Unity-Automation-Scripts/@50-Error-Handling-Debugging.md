# @50-Error-Handling-Debugging

## 🎯 Core Concept
Automated error handling and debugging system for comprehensive error tracking, crash reporting, and development debugging tools.

## 🔧 Implementation

### Debug Manager Framework
```csharp
using UnityEngine;
using System.Collections.Generic;
using System.Collections;
using System.IO;
using System.Text;

public class DebugManager : MonoBehaviour
{
    public static DebugManager Instance;
    
    [Header("Debug Settings")]
    public bool enableDebugMode = true;
    public bool enableConsoleLogging = true;
    public bool enableFileLogging = true;
    public bool enableCrashReporting = true;
    public LogLevel minimumLogLevel = LogLevel.Info;
    
    [Header("Performance Monitoring")]
    public bool enablePerformanceTracking = true;
    public bool enableMemoryTracking = true;
    public float performanceLogInterval = 5f;
    
    [Header("Error Handling")]
    public bool autoReportCrashes = true;
    public bool showErrorPopups = true;
    public int maxErrorsPerSession = 100;
    public string crashReportEndpoint = "";
    
    [Header("Debug UI")]
    public bool enableDebugOverlay = true;
    public KeyCode debugToggleKey = KeyCode.F12;
    public bool showFPSCounter = true;
    public bool showMemoryInfo = true;
    
    private List<LogEntry> logHistory;
    private Dictionary<string, int> errorCounts;
    private StringBuilder logBuffer;
    private string logFilePath;
    private bool isDebugOverlayVisible = false;
    private float lastPerformanceLog;
    private int totalErrors = 0;
    
    public System.Action<LogEntry> OnLogReceived;
    public System.Action<CrashReport> OnCrashDetected;
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeDebugManager();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void InitializeDebugManager()
    {
        logHistory = new List<LogEntry>();
        errorCounts = new Dictionary<string, int>();
        logBuffer = new StringBuilder();
        
        // Set up log file
        if (enableFileLogging)
        {
            string timestamp = System.DateTime.Now.ToString("yyyyMMdd_HHmmss");
            logFilePath = Path.Combine(Application.persistentDataPath, $"debug_log_{timestamp}.txt");
            
            // Write session header
            WriteToLogFile($"=== DEBUG SESSION STARTED ===");
            WriteToLogFile($"Time: {System.DateTime.Now}");
            WriteToLogFile($"Application: {Application.productName} v{Application.version}");
            WriteToLogFile($"Unity Version: {Application.unityVersion}");
            WriteToLogFile($"Platform: {Application.platform}");
            WriteToLogFile($"Device: {SystemInfo.deviceModel}");
            WriteToLogFile($"OS: {SystemInfo.operatingSystem}");
            WriteToLogFile($"Memory: {SystemInfo.systemMemorySize}MB");
            WriteToLogFile($"Graphics: {SystemInfo.graphicsDeviceName}");
            WriteToLogFile("================================");
        }
        
        // Hook into Unity's log system
        Application.logMessageReceived += HandleUnityLog;
        
        // Set up crash reporting
        if (enableCrashReporting)
        {
            Application.logMessageReceived += HandleCrashDetection;
        }
        
        Debug.Log("Debug Manager initialized successfully");
    }
    
    void Update()
    {
        // Toggle debug overlay
        if (Input.GetKeyDown(debugToggleKey))
        {
            ToggleDebugOverlay();
        }
        
        // Performance logging
        if (enablePerformanceTracking && Time.time - lastPerformanceLog > performanceLogInterval)
        {
            LogPerformanceMetrics();
            lastPerformanceLog = Time.time;
        }
    }
    
    void HandleUnityLog(string logString, string stackTrace, LogType type)
    {
        LogLevel level = ConvertLogType(type);
        
        if (level < minimumLogLevel)
            return;
        
        LogEntry entry = new LogEntry
        {
            message = logString,
            stackTrace = stackTrace,
            level = level,
            timestamp = System.DateTime.Now,
            frameCount = Time.frameCount
        };
        
        // Add to history
        logHistory.Add(entry);
        
        // Limit history size
        if (logHistory.Count > 1000)
        {
            logHistory.RemoveAt(0);
        }
        
        // Track error counts
        if (level == LogLevel.Error || level == LogLevel.Exception)
        {
            totalErrors++;
            string errorKey = GetErrorKey(logString);
            
            if (errorCounts.ContainsKey(errorKey))
            {
                errorCounts[errorKey]++;
            }
            else
            {
                errorCounts[errorKey] = 1;
            }
        }
        
        // Write to file
        if (enableFileLogging)
        {
            WriteToLogFile($"[{entry.timestamp:HH:mm:ss.fff}] [{level}] {logString}");
            if (!string.IsNullOrEmpty(stackTrace))
            {
                WriteToLogFile($"Stack Trace: {stackTrace}");
            }
        }
        
        // Notify listeners
        OnLogReceived?.Invoke(entry);
        
        // Handle errors
        if (level == LogLevel.Error || level == LogLevel.Exception)
        {
            HandleError(entry);
        }
    }
    
    void HandleCrashDetection(string logString, string stackTrace, LogType type)
    {
        if (type == LogType.Exception || type == LogType.Error)
        {
            // Check for critical errors that might indicate a crash
            if (IsCriticalError(logString, stackTrace))
            {
                CrashReport crashReport = new CrashReport
                {
                    errorMessage = logString,
                    stackTrace = stackTrace,
                    timestamp = System.DateTime.Now,
                    deviceInfo = GetDeviceInfo(),
                    gameState = GetGameState()
                };
                
                HandleCrash(crashReport);
            }
        }
    }
    
    bool IsCriticalError(string message, string stackTrace)
    {
        string[] criticalKeywords = {
            "OutOfMemoryException",
            "StackOverflowException",
            "AccessViolationException",
            "NullReferenceException",
            "UnityException",
            "Fatal",
            "Crash"
        };
        
        foreach (string keyword in criticalKeywords)
        {
            if (message.Contains(keyword) || stackTrace.Contains(keyword))
            {
                return true;
            }
        }
        
        return false;
    }
    
    void HandleError(LogEntry entry)
    {
        if (totalErrors > maxErrorsPerSession)
        {
            Debug.LogWarning("Maximum errors per session reached. Disabling error handling.");
            return;
        }
        
        // Show error popup if enabled
        if (showErrorPopups && (entry.level == LogLevel.Error || entry.level == LogLevel.Exception))
        {
            StartCoroutine(ShowErrorPopup(entry));
        }
        
        // Auto-save on critical errors
        if (entry.level == LogLevel.Exception)
        {
            AutoSaveOnError();
        }
    }
    
    void HandleCrash(CrashReport crashReport)
    {
        OnCrashDetected?.Invoke(crashReport);
        
        // Save crash report to file
        SaveCrashReport(crashReport);
        
        // Send to server if enabled
        if (autoReportCrashes && !string.IsNullOrEmpty(crashReportEndpoint))
        {
            StartCoroutine(SendCrashReport(crashReport));
        }
        
        Debug.LogError($"Crash detected: {crashReport.errorMessage}");
    }
    
    void SaveCrashReport(CrashReport report)
    {
        try
        {
            string crashFileName = $"crash_report_{report.timestamp:yyyyMMdd_HHmmss}.json";
            string crashFilePath = Path.Combine(Application.persistentDataPath, crashFileName);
            
            string json = JsonUtility.ToJson(report, true);
            File.WriteAllText(crashFilePath, json);
            
            Debug.Log($"Crash report saved to: {crashFilePath}");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Failed to save crash report: {e.Message}");
        }
    }
    
    IEnumerator SendCrashReport(CrashReport report)
    {
        string json = JsonUtility.ToJson(report);
        byte[] data = System.Text.Encoding.UTF8.GetBytes(json);
        
        using (UnityEngine.Networking.UnityWebRequest request = 
               new UnityEngine.Networking.UnityWebRequest(crashReportEndpoint, "POST"))
        {
            request.uploadHandler = new UnityEngine.Networking.UploadHandlerRaw(data);
            request.downloadHandler = new UnityEngine.Networking.DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityEngine.Networking.UnityWebRequest.Result.Success)
            {
                Debug.Log("Crash report sent successfully");
            }
            else
            {
                Debug.LogError($"Failed to send crash report: {request.error}");
            }
        }
    }
    
    IEnumerator ShowErrorPopup(LogEntry entry)
    {
        yield return new WaitForSeconds(0.1f);
        
        // This would show a UI popup with error details
        // Implementation depends on your UI system
        Debug.LogWarning($"Error popup would show: {entry.message}");
    }
    
    void AutoSaveOnError()
    {
        // Auto-save game state when critical errors occur
        try
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.SaveGame();
                Debug.Log("Auto-saved game due to error");
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Auto-save failed: {e.Message}");
        }
    }
    
    void LogPerformanceMetrics()
    {
        PerformanceMetrics metrics = GatherPerformanceMetrics();
        
        string performanceLog = $"Performance - FPS: {metrics.fps:F1}, " +
                               $"Memory: {metrics.memoryUsage:F1}MB, " +
                               $"GC: {metrics.gcCollections}, " +
                               $"Draw Calls: {metrics.drawCalls}";
        
        LogInfo(performanceLog);
        
        // Check for performance warnings
        if (metrics.fps < 30)
        {
            LogWarning("Low FPS detected: " + metrics.fps.ToString("F1"));
        }
        
        if (metrics.memoryUsage > 512)
        {
            LogWarning("High memory usage: " + metrics.memoryUsage.ToString("F1") + "MB");
        }
    }
    
    PerformanceMetrics GatherPerformanceMetrics()
    {
        return new PerformanceMetrics
        {
            fps = 1f / Time.smoothDeltaTime,
            memoryUsage = (float)(System.GC.GetTotalMemory(false) / (1024.0 * 1024.0)),
            gcCollections = System.GC.CollectionCount(0),
            drawCalls = UnityEngine.Rendering.FrameDebugger.enabled ? 
                       UnityEngine.Rendering.FrameDebugger.GetFrameEventCount() : 0
        };
    }
    
    void WriteToLogFile(string message)
    {
        if (!enableFileLogging || string.IsNullOrEmpty(logFilePath))
            return;
        
        try
        {
            File.AppendAllText(logFilePath, message + "\n");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Failed to write to log file: {e.Message}");
        }
    }
    
    void ToggleDebugOverlay()
    {
        isDebugOverlayVisible = !isDebugOverlayVisible;
        Debug.Log($"Debug overlay: {(isDebugOverlayVisible ? "Enabled" : "Disabled")}");
    }
    
    void OnGUI()
    {
        if (!enableDebugOverlay || !isDebugOverlayVisible)
            return;
        
        // Debug overlay UI
        GUILayout.BeginArea(new Rect(10, 10, 300, Screen.height - 20));
        GUILayout.BeginVertical("box");
        
        GUILayout.Label("DEBUG OVERLAY", GUI.skin.label);
        
        if (showFPSCounter)
        {
            float fps = 1f / Time.smoothDeltaTime;
            GUILayout.Label($"FPS: {fps:F1}");
        }
        
        if (showMemoryInfo)
        {
            float memory = (float)(System.GC.GetTotalMemory(false) / (1024.0 * 1024.0));
            GUILayout.Label($"Memory: {memory:F1} MB");
        }
        
        GUILayout.Label($"Errors: {totalErrors}");
        GUILayout.Label($"Frame: {Time.frameCount}");
        
        if (GUILayout.Button("Clear Logs"))
        {
            ClearLogs();
        }
        
        if (GUILayout.Button("Save Debug Report"))
        {
            SaveDebugReport();
        }
        
        // Recent logs
        GUILayout.Label("Recent Logs:");
        for (int i = Mathf.Max(0, logHistory.Count - 5); i < logHistory.Count; i++)
        {
            LogEntry entry = logHistory[i];
            GUI.color = GetLogColor(entry.level);
            GUILayout.Label($"[{entry.level}] {entry.message}", GUI.skin.label);
        }
        GUI.color = Color.white;
        
        GUILayout.EndVertical();
        GUILayout.EndArea();
    }
    
    Color GetLogColor(LogLevel level)
    {
        switch (level)
        {
            case LogLevel.Error:
            case LogLevel.Exception:
                return Color.red;
            case LogLevel.Warning:
                return Color.yellow;
            case LogLevel.Info:
                return Color.white;
            case LogLevel.Debug:
                return Color.gray;
            default:
                return Color.white;
        }
    }
    
    LogLevel ConvertLogType(LogType type)
    {
        switch (type)
        {
            case LogType.Error:
                return LogLevel.Error;
            case LogType.Exception:
                return LogLevel.Exception;
            case LogType.Warning:
                return LogLevel.Warning;
            case LogType.Log:
                return LogLevel.Info;
            default:
                return LogLevel.Debug;
        }
    }
    
    string GetErrorKey(string message)
    {
        // Create a key for grouping similar errors
        if (string.IsNullOrEmpty(message))
            return "Unknown";
        
        // Take first 50 characters for grouping
        return message.Length > 50 ? message.Substring(0, 50) : message;
    }
    
    DeviceInfo GetDeviceInfo()
    {
        return new DeviceInfo
        {
            deviceModel = SystemInfo.deviceModel,
            operatingSystem = SystemInfo.operatingSystem,
            systemMemorySize = SystemInfo.systemMemorySize,
            graphicsDeviceName = SystemInfo.graphicsDeviceName,
            processorType = SystemInfo.processorType,
            processorCount = SystemInfo.processorCount
        };
    }
    
    GameStateInfo GetGameState()
    {
        return new GameStateInfo
        {
            currentScene = UnityEngine.SceneManagement.SceneManager.GetActiveScene().name,
            gameTime = Time.time,
            frameCount = Time.frameCount,
            playerPosition = Vector3.zero // Get from player if available
        };
    }
    
    public void LogInfo(string message)
    {
        Debug.Log(message);
    }
    
    public void LogWarning(string message)
    {
        Debug.LogWarning(message);
    }
    
    public void LogError(string message)
    {
        Debug.LogError(message);
    }
    
    public void LogException(System.Exception exception)
    {
        Debug.LogException(exception);
    }
    
    public void ClearLogs()
    {
        logHistory.Clear();
        errorCounts.Clear();
        totalErrors = 0;
        Debug.Log("Debug logs cleared");
    }
    
    public void SaveDebugReport()
    {
        try
        {
            DebugReport report = new DebugReport
            {
                timestamp = System.DateTime.Now,
                deviceInfo = GetDeviceInfo(),
                gameState = GetGameState(),
                performanceMetrics = GatherPerformanceMetrics(),
                recentLogs = logHistory.GetRange(Mathf.Max(0, logHistory.Count - 100), 
                                               Mathf.Min(100, logHistory.Count)),
                errorCounts = new Dictionary<string, int>(errorCounts)
            };
            
            string reportPath = Path.Combine(Application.persistentDataPath, 
                                           $"debug_report_{System.DateTime.Now:yyyyMMdd_HHmmss}.json");
            string json = JsonUtility.ToJson(report, true);
            File.WriteAllText(reportPath, json);
            
            Debug.Log($"Debug report saved to: {reportPath}");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Failed to save debug report: {e.Message}");
        }
    }
    
    public List<LogEntry> GetLogHistory()
    {
        return new List<LogEntry>(logHistory);
    }
    
    public Dictionary<string, int> GetErrorCounts()
    {
        return new Dictionary<string, int>(errorCounts);
    }
    
    void OnApplicationQuit()
    {
        if (enableFileLogging)
        {
            WriteToLogFile("=== DEBUG SESSION ENDED ===");
            WriteToLogFile($"Total Errors: {totalErrors}");
            WriteToLogFile($"Session Duration: {Time.time:F1} seconds");
        }
        
        Application.logMessageReceived -= HandleUnityLog;
        Application.logMessageReceived -= HandleCrashDetection;
    }
}

// Data structures
public enum LogLevel
{
    Debug = 0,
    Info = 1,
    Warning = 2,
    Error = 3,
    Exception = 4
}

[System.Serializable]
public class LogEntry
{
    public string message;
    public string stackTrace;
    public LogLevel level;
    public System.DateTime timestamp;
    public int frameCount;
}

[System.Serializable]
public class CrashReport
{
    public string errorMessage;
    public string stackTrace;
    public System.DateTime timestamp;
    public DeviceInfo deviceInfo;
    public GameStateInfo gameState;
}

[System.Serializable]
public class DeviceInfo
{
    public string deviceModel;
    public string operatingSystem;
    public int systemMemorySize;
    public string graphicsDeviceName;
    public string processorType;
    public int processorCount;
}

[System.Serializable]
public class GameStateInfo
{
    public string currentScene;
    public float gameTime;
    public int frameCount;
    public Vector3 playerPosition;
}

[System.Serializable]
public class PerformanceMetrics
{
    public float fps;
    public float memoryUsage;
    public int gcCollections;
    public int drawCalls;
}

[System.Serializable]
public class DebugReport
{
    public System.DateTime timestamp;
    public DeviceInfo deviceInfo;
    public GameStateInfo gameState;
    public PerformanceMetrics performanceMetrics;
    public List<LogEntry> recentLogs;
    public Dictionary<string, int> errorCounts;
}

// Debug utilities
public static class DebugUtils
{
    public static void LogMethodEntry(string methodName)
    {
        if (DebugManager.Instance != null)
        {
            DebugManager.Instance.LogInfo($"[METHOD] Entering: {methodName}");
        }
    }
    
    public static void LogMethodExit(string methodName)
    {
        if (DebugManager.Instance != null)
        {
            DebugManager.Instance.LogInfo($"[METHOD] Exiting: {methodName}");
        }
    }
    
    public static void LogVariableValue(string variableName, object value)
    {
        if (DebugManager.Instance != null)
        {
            DebugManager.Instance.LogInfo($"[VAR] {variableName} = {value}");
        }
    }
    
    public static void LogCondition(string condition, bool result)
    {
        if (DebugManager.Instance != null)
        {
            DebugManager.Instance.LogInfo($"[CONDITION] {condition} = {result}");
        }
    }
}
```

## 🚀 AI/LLM Integration
- Automatically categorize and analyze error patterns
- Generate intelligent crash reports with context
- Create predictive error detection algorithms

## 💡 Key Benefits
- Comprehensive error tracking and logging
- Automated crash reporting and recovery
- Real-time performance monitoring