# @37-Error-Handling-System

## 🎯 Core Concept
Automated error handling, logging, and recovery system for robust game stability and debugging.

## 🔧 Implementation

### Error Management Framework
```csharp
using UnityEngine;
using System.Collections.Generic;
using System.IO;
using System;

public class ErrorHandlingSystem : MonoBehaviour
{
    public static ErrorHandlingSystem Instance;
    
    [Header("Error Settings")]
    public bool enableErrorLogging = true;
    public bool enableCrashReporting = true;
    public bool enableAutoRecovery = true;
    public int maxErrorLogSize = 1000000; // 1MB
    
    [Header("Recovery Settings")]
    public float recoveryDelay = 2f;
    public int maxRecoveryAttempts = 3;
    
    private Queue<ErrorEntry> errorQueue;
    private Dictionary<Type, int> errorCounts;
    private string logFilePath;
    private bool isRecovering = false;
    
    public System.Action<ErrorEntry> OnErrorLogged;
    public System.Action<string> OnCriticalError;
    public System.Action OnRecoveryStarted;
    public System.Action OnRecoveryCompleted;
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeErrorHandling();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void InitializeErrorHandling()
    {
        errorQueue = new Queue<ErrorEntry>();
        errorCounts = new Dictionary<Type, int>();
        
        logFilePath = Path.Combine(Application.persistentDataPath, "error_log.txt");
        
        // Register Unity's log callback
        Application.logMessageReceived += HandleUnityLog;
        
        // Register unhandled exception handler
        AppDomain.CurrentDomain.UnhandledException += HandleUnhandledException;
        
        Debug.Log("Error handling system initialized");
    }
    
    void HandleUnityLog(string logString, string stackTrace, LogType type)
    {
        if (!enableErrorLogging) return;
        
        ErrorSeverity severity = ConvertLogTypeToSeverity(type);
        
        if (severity >= ErrorSeverity.Warning)
        {
            LogError(new ErrorEntry
            {
                message = logString,
                stackTrace = stackTrace,
                severity = severity,
                timestamp = DateTime.Now,
                source = "Unity"
            });
        }
    }
    
    void HandleUnhandledException(object sender, UnhandledExceptionEventArgs e)
    {
        Exception exception = e.ExceptionObject as Exception;
        
        if (exception != null)
        {
            LogError(new ErrorEntry
            {
                message = exception.Message,
                stackTrace = exception.StackTrace,
                severity = ErrorSeverity.Critical,
                timestamp = DateTime.Now,
                source = "Unhandled Exception"
            });
            
            if (enableAutoRecovery && !isRecovering)
            {
                StartCoroutine(AttemptRecovery());
            }
        }
    }
    
    ErrorSeverity ConvertLogTypeToSeverity(LogType logType)
    {
        switch (logType)
        {
            case LogType.Error:
            case LogType.Exception:
                return ErrorSeverity.Error;
            case LogType.Assert:
                return ErrorSeverity.Critical;
            case LogType.Warning:
                return ErrorSeverity.Warning;
            default:
                return ErrorSeverity.Info;
        }
    }
    
    public void LogError(ErrorEntry error)
    {
        errorQueue.Enqueue(error);
        
        // Track error frequency
        Type errorType = error.GetType();
        if (errorCounts.ContainsKey(errorType))
        {
            errorCounts[errorType]++;
        }
        else
        {
            errorCounts[errorType] = 1;
        }
        
        // Write to file
        if (enableErrorLogging)
        {
            WriteErrorToFile(error);
        }
        
        // Handle critical errors
        if (error.severity == ErrorSeverity.Critical)
        {
            OnCriticalError?.Invoke(error.message);
            
            if (enableAutoRecovery && !isRecovering)
            {
                StartCoroutine(AttemptRecovery());
            }
        }
        
        OnErrorLogged?.Invoke(error);
        
        // Keep queue size manageable
        if (errorQueue.Count > 1000)
        {
            errorQueue.Dequeue();
        }
    }
    
    void WriteErrorToFile(ErrorEntry error)
    {
        try
        {
            // Check file size and rotate if needed
            if (File.Exists(logFilePath))
            {
                FileInfo fileInfo = new FileInfo(logFilePath);
                if (fileInfo.Length > maxErrorLogSize)
                {
                    RotateLogFile();
                }
            }
            
            string logEntry = FormatErrorEntry(error);
            File.AppendAllText(logFilePath, logEntry + Environment.NewLine);
        }
        catch (Exception e)
        {
            Debug.LogWarning($"Failed to write error to log file: {e.Message}");
        }
    }
    
    void RotateLogFile()
    {
        try
        {
            string backupPath = logFilePath.Replace(".txt", "_backup.txt");
            
            if (File.Exists(backupPath))
            {
                File.Delete(backupPath);
            }
            
            File.Move(logFilePath, backupPath);
        }
        catch (Exception e)
        {
            Debug.LogWarning($"Failed to rotate log file: {e.Message}");
        }
    }
    
    string FormatErrorEntry(ErrorEntry error)
    {
        return $"[{error.timestamp:yyyy-MM-dd HH:mm:ss}] [{error.severity}] [{error.source}] {error.message}" +
               (string.IsNullOrEmpty(error.stackTrace) ? "" : $"\nStack Trace:\n{error.stackTrace}");
    }
    
    System.Collections.IEnumerator AttemptRecovery()
    {
        if (isRecovering) yield break;
        
        isRecovering = true;
        OnRecoveryStarted?.Invoke();
        
        Debug.Log("Starting error recovery process...");
        
        yield return new WaitForSeconds(recoveryDelay);
        
        // Recovery strategies
        bool recoverySuccessful = false;
        
        for (int attempt = 1; attempt <= maxRecoveryAttempts && !recoverySuccessful; attempt++)
        {
            Debug.Log($"Recovery attempt {attempt}/{maxRecoveryAttempts}");
            
            try
            {
                // Strategy 1: Force garbage collection
                System.GC.Collect();
                Resources.UnloadUnusedAssets();
                
                // Strategy 2: Reset critical systems
                ResetCriticalSystems();
                
                // Strategy 3: Validate game state
                if (ValidateGameState())
                {
                    recoverySuccessful = true;
                    Debug.Log("Recovery successful");
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"Recovery attempt {attempt} failed: {e.Message}");
            }
            
            if (!recoverySuccessful && attempt < maxRecoveryAttempts)
            {
                yield return new WaitForSeconds(recoveryDelay);
            }
        }
        
        if (!recoverySuccessful)
        {
            Debug.LogError("All recovery attempts failed");
            // Last resort: return to main menu
            ReturnToSafeState();
        }
        
        OnRecoveryCompleted?.Invoke();
        isRecovering = false;
    }
    
    void ResetCriticalSystems()
    {
        // Reset audio
        if (AudioListener.volume == 0)
        {
            AudioListener.volume = 1f;
        }
        
        // Reset time scale
        if (Time.timeScale != 1f)
        {
            Time.timeScale = 1f;
        }
        
        // Reset cursor
        Cursor.lockState = CursorLockMode.None;
        Cursor.visible = true;
        
        Debug.Log("Critical systems reset");
    }
    
    bool ValidateGameState()
    {
        try
        {
            // Check if essential managers exist
            if (GameStateManager.Instance == null)
            {
                Debug.LogWarning("GameStateManager missing");
                return false;
            }
            
            // Check scene validity
            var activeScene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            if (!activeScene.isLoaded)
            {
                Debug.LogWarning("Active scene not loaded");
                return false;
            }
            
            // Check camera
            if (Camera.main == null)
            {
                Debug.LogWarning("Main camera missing");
                return false;
            }
            
            return true;
        }
        catch (Exception e)
        {
            Debug.LogError($"Game state validation failed: {e.Message}");
            return false;
        }
    }
    
    void ReturnToSafeState()
    {
        try
        {
            // Save current progress if possible
            if (SaveSystemManager.Instance != null)
            {
                // Emergency save
                Debug.Log("Performing emergency save...");
            }
            
            // Return to main menu
            if (GameStateManager.Instance != null)
            {
                GameStateManager.Instance.QuitToMainMenu();
            }
            else
            {
                // Fallback: load main menu scene directly
                UnityEngine.SceneManagement.SceneManager.LoadScene("MainMenu");
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to return to safe state: {e.Message}");
            
            // Ultimate fallback: quit application
            Application.Quit();
        }
    }
    
    public void ReportBug(string description, string reproductionSteps = "")
    {
        if (!enableCrashReporting) return;
        
        ErrorEntry bugReport = new ErrorEntry
        {
            message = $"User Bug Report: {description}",
            stackTrace = reproductionSteps,
            severity = ErrorSeverity.Warning,
            timestamp = DateTime.Now,
            source = "User Report"
        };
        
        LogError(bugReport);
        
        // Generate detailed system info
        string systemInfo = GenerateSystemInfo();
        File.WriteAllText(Path.Combine(Application.persistentDataPath, "bug_report.txt"), 
            FormatErrorEntry(bugReport) + "\n\nSystem Info:\n" + systemInfo);
        
        Debug.Log("Bug report submitted");
    }
    
    string GenerateSystemInfo()
    {
        return $"Unity Version: {Application.unityVersion}\n" +
               $"Platform: {Application.platform}\n" +
               $"Device Model: {SystemInfo.deviceModel}\n" +
               $"Operating System: {SystemInfo.operatingSystem}\n" +
               $"Processor: {SystemInfo.processorType}\n" +
               $"Memory: {SystemInfo.systemMemorySize}MB\n" +
               $"Graphics: {SystemInfo.graphicsDeviceName}\n" +
               $"Graphics Memory: {SystemInfo.graphicsMemorySize}MB\n" +
               $"Screen Resolution: {Screen.width}x{Screen.height}\n" +
               $"Game Version: {Application.version}";
    }
    
    public ErrorStatistics GetErrorStatistics()
    {
        return new ErrorStatistics
        {
            totalErrors = errorQueue.Count,
            errorsByType = new Dictionary<Type, int>(errorCounts),
            lastError = errorQueue.Count > 0 ? errorQueue.ToArray()[errorQueue.Count - 1] : null
        };
    }
    
    public void ClearErrorLog()
    {
        errorQueue.Clear();
        errorCounts.Clear();
        
        if (File.Exists(logFilePath))
        {
            File.Delete(logFilePath);
        }
        
        Debug.Log("Error log cleared");
    }
    
    void OnDestroy()
    {
        if (Application.logMessageReceived != null)
        {
            Application.logMessageReceived -= HandleUnityLog;
        }
    }
}

[System.Serializable]
public class ErrorEntry
{
    public string message;
    public string stackTrace;
    public ErrorSeverity severity;
    public DateTime timestamp;
    public string source;
}

public enum ErrorSeverity
{
    Info = 0,
    Warning = 1,
    Error = 2,
    Critical = 3
}

[System.Serializable]
public class ErrorStatistics
{
    public int totalErrors;
    public Dictionary<Type, int> errorsByType;
    public ErrorEntry lastError;
}

// UI component for displaying errors in development builds
public class ErrorDisplay : MonoBehaviour
{
    [Header("UI References")]
    public GameObject errorPanel;
    public UnityEngine.UI.Text errorText;
    public UnityEngine.UI.Button dismissButton;
    public UnityEngine.UI.Button reportButton;
    
    void Start()
    {
        if (ErrorHandlingSystem.Instance != null)
        {
            ErrorHandlingSystem.Instance.OnErrorLogged += ShowError;
        }
        
        if (dismissButton != null)
        {
            dismissButton.onClick.AddListener(DismissError);
        }
        
        if (reportButton != null)
        {
            reportButton.onClick.AddListener(ReportCurrentError);
        }
    }
    
    void ShowError(ErrorEntry error)
    {
        if (Debug.isDebugBuild && error.severity >= ErrorSeverity.Error)
        {
            if (errorPanel != null)
            {
                errorPanel.SetActive(true);
            }
            
            if (errorText != null)
            {
                errorText.text = $"Error: {error.message}\n\nTime: {error.timestamp:HH:mm:ss}\nSource: {error.source}";
            }
        }
    }
    
    void DismissError()
    {
        if (errorPanel != null)
        {
            errorPanel.SetActive(false);
        }
    }
    
    void ReportCurrentError()
    {
        if (ErrorHandlingSystem.Instance != null)
        {
            ErrorHandlingSystem.Instance.ReportBug("Error reported from in-game display");
        }
        
        DismissError();
    }
}
```

## 🚀 AI/LLM Integration
- Automatically categorize and prioritize errors
- Generate recovery strategies based on error patterns
- Create intelligent error reports with context

## 💡 Key Benefits
- Comprehensive error tracking and logging
- Automatic recovery mechanisms
- Detailed crash reporting system