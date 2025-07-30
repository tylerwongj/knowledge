# @47-Analytics-Data-Collection

## 🎯 Core Concept
Automated analytics and data collection system for tracking player behavior, game metrics, and performance analytics.

## 🔧 Implementation

### Analytics Manager
```csharp
using UnityEngine;
using System.Collections.Generic;
using System.Collections;
using System.IO;
using UnityEngine.Networking;

public class AnalyticsManager : MonoBehaviour
{
    public static AnalyticsManager Instance;
    
    [Header("Analytics Settings")]
    public bool enableAnalytics = true;
    public bool enableLocalStorage = true;
    public bool enableRemoteTracking = false;
    public string analyticsEndpoint = "https://your-analytics-server.com/events";
    public string apiKey = "";
    
    [Header("Collection Settings")]
    public float sessionSampleRate = 1f;
    public int maxEventsPerBatch = 100;
    public float batchSendInterval = 30f;
    public bool trackUserInteractions = true;
    public bool trackPerformanceMetrics = true;
    public bool trackErrors = true;
    
    [Header("Privacy")]
    public bool anonymizeData = true;
    public bool requireUserConsent = true;
    
    private List<AnalyticsEvent> eventQueue;
    private Dictionary<string, object> sessionData;
    private string sessionId;
    private string userId;
    private bool userConsent = false;
    private float sessionStartTime;
    private int totalEvents = 0;
    
    public System.Action<AnalyticsEvent> OnEventTracked;
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeAnalytics();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void InitializeAnalytics()
    {
        eventQueue = new List<AnalyticsEvent>();
        sessionData = new Dictionary<string, object>();
        
        // Generate session and user IDs
        sessionId = System.Guid.NewGuid().ToString();
        userId = GetOrCreateUserId();
        sessionStartTime = Time.time;
        
        // Check user consent
        if (requireUserConsent)
        {
            userConsent = PlayerPrefs.GetInt("AnalyticsConsent", 0) == 1;
        }
        else
        {
            userConsent = true;
        }
        
        // Initialize session data
        InitializeSessionData();
        
        // Start batch sending coroutine
        if (enableAnalytics && userConsent)
        {
            StartCoroutine(BatchSendCoroutine());
            TrackSessionStart();
        }
        
        Debug.Log($"Analytics initialized. Session ID: {sessionId}");
    }
    
    void InitializeSessionData()
    {
        sessionData["session_id"] = sessionId;
        sessionData["user_id"] = anonymizeData ? HashString(userId) : userId;
        sessionData["platform"] = Application.platform.ToString();
        sessionData["app_version"] = Application.version;
        sessionData["unity_version"] = Application.unityVersion;
        sessionData["device_model"] = SystemInfo.deviceModel;
        sessionData["operating_system"] = SystemInfo.operatingSystem;
        sessionData["memory_size"] = SystemInfo.systemMemorySize;
        sessionData["graphics_device"] = SystemInfo.graphicsDeviceName;
        sessionData["screen_resolution"] = $"{Screen.width}x{Screen.height}";
        sessionData["start_time"] = System.DateTime.UtcNow.ToString("o");
    }
    
    string GetOrCreateUserId()
    {
        string id = PlayerPrefs.GetString("UserId", "");
        
        if (string.IsNullOrEmpty(id))
        {
            id = System.Guid.NewGuid().ToString();
            PlayerPrefs.SetString("UserId", id);
            PlayerPrefs.Save();
        }
        
        return id;
    }
    
    string HashString(string input)
    {
        // Simple hash for anonymization
        return input.GetHashCode().ToString();
    }
    
    public void SetUserConsent(bool consent)
    {
        userConsent = consent;
        PlayerPrefs.SetInt("AnalyticsConsent", consent ? 1 : 0);
        PlayerPrefs.Save();
        
        if (consent && enableAnalytics)
        {
            StartCoroutine(BatchSendCoroutine());
            TrackSessionStart();
        }
        else if (!consent)
        {
            // Clear stored data if consent is revoked
            ClearStoredData();
        }
        
        Debug.Log($"User consent for analytics: {consent}");
    }
    
    public void TrackEvent(string eventName, Dictionary<string, object> parameters = null)
    {
        if (!enableAnalytics || !userConsent)
            return;
        
        AnalyticsEvent analyticsEvent = new AnalyticsEvent
        {
            eventName = eventName,
            timestamp = System.DateTime.UtcNow.ToString("o"),
            sessionId = sessionId,
            parameters = parameters ?? new Dictionary<string, object>()
        };
        
        // Add session data to parameters
        foreach (var kvp in sessionData)
        {
            if (!analyticsEvent.parameters.ContainsKey(kvp.Key))
            {
                analyticsEvent.parameters[kvp.Key] = kvp.Value;
            }
        }
        
        eventQueue.Add(analyticsEvent);
        totalEvents++;
        
        OnEventTracked?.Invoke(analyticsEvent);
        
        // Save locally if enabled
        if (enableLocalStorage)
        {
            SaveEventLocally(analyticsEvent);
        }
        
        Debug.Log($"Tracked event: {eventName}");
    }
    
    void TrackSessionStart()
    {
        Dictionary<string, object> parameters = new Dictionary<string, object>
        {
            ["session_duration"] = 0f,
            ["first_session"] = !PlayerPrefs.HasKey("FirstSession")
        };
        
        if (!PlayerPrefs.HasKey("FirstSession"))
        {
            PlayerPrefs.SetInt("FirstSession", 1);
            PlayerPrefs.Save();
        }
        
        TrackEvent("session_start", parameters);
    }
    
    void TrackSessionEnd()
    {
        Dictionary<string, object> parameters = new Dictionary<string, object>
        {
            ["session_duration"] = Time.time - sessionStartTime,
            ["total_events"] = totalEvents
        };
        
        TrackEvent("session_end", parameters);
    }
    
    public void TrackLevelStart(string levelName, int levelNumber)
    {
        Dictionary<string, object> parameters = new Dictionary<string, object>
        {
            ["level_name"] = levelName,
            ["level_number"] = levelNumber,
            ["attempt_number"] = PlayerPrefs.GetInt($"Level_{levelNumber}_Attempts", 0) + 1
        };
        
        PlayerPrefs.SetInt($"Level_{levelNumber}_Attempts", (int)parameters["attempt_number"]);
        
        TrackEvent("level_start", parameters);
    }
    
    public void TrackLevelComplete(string levelName, int levelNumber, float completionTime, int score)
    {
        Dictionary<string, object> parameters = new Dictionary<string, object>
        {
            ["level_name"] = levelName,
            ["level_number"] = levelNumber,
            ["completion_time"] = completionTime,
            ["score"] = score,
            ["attempts"] = PlayerPrefs.GetInt($"Level_{levelNumber}_Attempts", 1)
        };
        
        TrackEvent("level_complete", parameters);
    }
    
    public void TrackLevelFail(string levelName, int levelNumber, string failReason, float timeSpent)
    {
        Dictionary<string, object> parameters = new Dictionary<string, object>
        {
            ["level_name"] = levelName,
            ["level_number"] = levelNumber,
            ["fail_reason"] = failReason,
            ["time_spent"] = timeSpent
        };
        
        TrackEvent("level_fail", parameters);
    }
    
    public void TrackPurchase(string itemId, string itemType, float price, string currency)
    {
        Dictionary<string, object> parameters = new Dictionary<string, object>
        {
            ["item_id"] = itemId,
            ["item_type"] = itemType,
            ["price"] = price,
            ["currency"] = currency,
            ["transaction_id"] = System.Guid.NewGuid().ToString()
        };
        
        TrackEvent("purchase", parameters);
    }
    
    public void TrackUserInteraction(string interactionType, string targetObject, Vector3 position)
    {
        if (!trackUserInteractions)
            return;
        
        Dictionary<string, object> parameters = new Dictionary<string, object>
        {
            ["interaction_type"] = interactionType,
            ["target_object"] = targetObject,
            ["position_x"] = position.x,
            ["position_y"] = position.y,
            ["position_z"] = position.z
        };
        
        TrackEvent("user_interaction", parameters);
    }
    
    public void TrackPerformanceMetric(string metricName, float value)
    {
        if (!trackPerformanceMetrics)
            return;
        
        Dictionary<string, object> parameters = new Dictionary<string, object>
        {
            ["metric_name"] = metricName,
            ["value"] = value,
            ["fps"] = 1f / Time.smoothDeltaTime,
            ["memory_usage"] = UnityEngine.Profiling.Profiler.GetTotalAllocatedMemory(false) / (1024f * 1024f)
        };
        
        TrackEvent("performance_metric", parameters);
    }
    
    public void TrackError(string errorType, string errorMessage, string stackTrace)
    {
        if (!trackErrors)
            return;
        
        Dictionary<string, object> parameters = new Dictionary<string, object>
        {
            ["error_type"] = errorType,
            ["error_message"] = errorMessage,
            ["stack_trace"] = stackTrace,
            ["scene"] = UnityEngine.SceneManagement.SceneManager.GetActiveScene().name
        };
        
        TrackEvent("error", parameters);
    }
    
    public void TrackCustomEvent(string eventName, Dictionary<string, object> customParameters)
    {
        TrackEvent($"custom_{eventName}", customParameters);
    }
    
    void SaveEventLocally(AnalyticsEvent analyticsEvent)
    {
        string eventJson = JsonUtility.ToJson(analyticsEvent);
        string fileName = $"analytics_{System.DateTime.Now:yyyyMMdd}.log";
        string filePath = Path.Combine(Application.persistentDataPath, fileName);
        
        try
        {
            File.AppendAllText(filePath, eventJson + "\n");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Failed to save analytics event locally: {e.Message}");
        }
    }
    
    IEnumerator BatchSendCoroutine()
    {
        while (enableAnalytics && userConsent)
        {
            yield return new WaitForSeconds(batchSendInterval);
            
            if (eventQueue.Count > 0 && enableRemoteTracking)
            {
                yield return StartCoroutine(SendEventBatch());
            }
        }
    }
    
    IEnumerator SendEventBatch()
    {
        if (eventQueue.Count == 0 || string.IsNullOrEmpty(analyticsEndpoint))
            yield break;
        
        List<AnalyticsEvent> batchEvents = new List<AnalyticsEvent>();
        int eventsToSend = Mathf.Min(eventQueue.Count, maxEventsPerBatch);
        
        for (int i = 0; i < eventsToSend; i++)
        {
            batchEvents.Add(eventQueue[i]);
        }
        
        AnalyticsBatch batch = new AnalyticsBatch
        {
            events = batchEvents,
            batchId = System.Guid.NewGuid().ToString(),
            timestamp = System.DateTime.UtcNow.ToString("o")
        };
        
        string jsonData = JsonUtility.ToJson(batch);
        
        using (UnityWebRequest request = new UnityWebRequest(analyticsEndpoint, "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            if (!string.IsNullOrEmpty(apiKey))
            {
                request.SetRequestHeader("Authorization", $"Bearer {apiKey}");
            }
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                // Remove sent events from queue
                eventQueue.RemoveRange(0, eventsToSend);
                Debug.Log($"Successfully sent {eventsToSend} analytics events");
            }
            else
            {
                Debug.LogError($"Failed to send analytics batch: {request.error}");
            }
        }
    }
    
    public AnalyticsReport GenerateReport()
    {
        AnalyticsReport report = new AnalyticsReport
        {
            sessionId = sessionId,
            userId = anonymizeData ? HashString(userId) : userId,
            sessionDuration = Time.time - sessionStartTime,
            totalEvents = totalEvents,
            generatedAt = System.DateTime.UtcNow.ToString("o")
        };
        
        // Calculate event type distribution
        Dictionary<string, int> eventCounts = new Dictionary<string, int>();
        foreach (var analyticsEvent in eventQueue)
        {
            if (eventCounts.ContainsKey(analyticsEvent.eventName))
            {
                eventCounts[analyticsEvent.eventName]++;
            }
            else
            {
                eventCounts[analyticsEvent.eventName] = 1;
            }
        }
        
        report.eventDistribution = eventCounts;
        
        return report;
    }
    
    public void ExportAnalyticsData(string fileName = "")
    {
        if (string.IsNullOrEmpty(fileName))
        {
            fileName = $"analytics_export_{System.DateTime.Now:yyyyMMdd_HHmmss}.json";
        }
        
        AnalyticsExport export = new AnalyticsExport
        {
            sessionData = sessionData,
            events = eventQueue,
            report = GenerateReport()
        };
        
        string json = JsonUtility.ToJson(export, true);
        File.WriteAllText(fileName, json);
        
        Debug.Log($"Analytics data exported to {fileName}");
    }
    
    void ClearStoredData()
    {
        eventQueue.Clear();
        
        // Clear local files
        string[] files = Directory.GetFiles(Application.persistentDataPath, "analytics_*.log");
        foreach (string file in files)
        {
            try
            {
                File.Delete(file);
            }
            catch (System.Exception e)
            {
                Debug.LogError($"Failed to delete analytics file {file}: {e.Message}");
            }
        }
        
        Debug.Log("Analytics data cleared");
    }
    
    void OnApplicationPause(bool pauseStatus)
    {
        if (pauseStatus)
        {
            TrackEvent("app_pause");
        }
        else
        {
            TrackEvent("app_resume");
        }
    }
    
    void OnApplicationFocus(bool hasFocus)
    {
        if (hasFocus)
        {
            TrackEvent("app_focus");
        }
        else
        {
            TrackEvent("app_unfocus");
        }
    }
    
    void OnApplicationQuit()
    {
        TrackSessionEnd();
        
        // Send any remaining events immediately
        if (eventQueue.Count > 0 && enableRemoteTracking)
        {
            StartCoroutine(SendEventBatch());
        }
    }
    
    // Unity Analytics integration if available
    void Start()
    {
        #if UNITY_ANALYTICS
        if (UnityEngine.Analytics.Analytics.enabled)
        {
            Debug.Log("Unity Analytics is enabled");
        }
        #endif
    }
}

// Data structures
[System.Serializable]
public class AnalyticsEvent
{
    public string eventName;
    public string timestamp;
    public string sessionId;
    public Dictionary<string, object> parameters;
}

[System.Serializable]
public class AnalyticsBatch
{
    public List<AnalyticsEvent> events;
    public string batchId;
    public string timestamp;
}

[System.Serializable]
public class AnalyticsReport
{
    public string sessionId;
    public string userId;
    public float sessionDuration;
    public int totalEvents;
    public Dictionary<string, int> eventDistribution;
    public string generatedAt;
}

[System.Serializable]
public class AnalyticsExport
{
    public Dictionary<string, object> sessionData;
    public List<AnalyticsEvent> events;
    public AnalyticsReport report;
}

// Analytics tracking components
public class AnalyticsTracker : MonoBehaviour
{
    [Header("Tracking Settings")]
    public bool trackClicks = true;
    public bool trackHovers = true;
    public bool trackVisibility = true;
    public string customEventPrefix = "";
    
    void Start()
    {
        if (trackVisibility)
        {
            TrackVisibility();
        }
    }
    
    void OnMouseDown()
    {
        if (trackClicks && AnalyticsManager.Instance != null)
        {
            string eventName = string.IsNullOrEmpty(customEventPrefix) ? 
                "object_click" : $"{customEventPrefix}_click";
            
            Dictionary<string, object> parameters = new Dictionary<string, object>
            {
                ["object_name"] = gameObject.name,
                ["position"] = transform.position.ToString()
            };
            
            AnalyticsManager.Instance.TrackEvent(eventName, parameters);
        }
    }
    
    void OnMouseEnter()
    {
        if (trackHovers && AnalyticsManager.Instance != null)
        {
            string eventName = string.IsNullOrEmpty(customEventPrefix) ? 
                "object_hover" : $"{customEventPrefix}_hover";
            
            Dictionary<string, object> parameters = new Dictionary<string, object>
            {
                ["object_name"] = gameObject.name
            };
            
            AnalyticsManager.Instance.TrackEvent(eventName, parameters);
        }
    }
    
    void TrackVisibility()
    {
        if (AnalyticsManager.Instance != null)
        {
            string eventName = string.IsNullOrEmpty(customEventPrefix) ? 
                "object_visible" : $"{customEventPrefix}_visible";
            
            Dictionary<string, object> parameters = new Dictionary<string, object>
            {
                ["object_name"] = gameObject.name,
                ["scene"] = UnityEngine.SceneManagement.SceneManager.GetActiveScene().name
            };
            
            AnalyticsManager.Instance.TrackEvent(eventName, parameters);
        }
    }
}

// Performance analytics component
public class PerformanceAnalytics : MonoBehaviour
{
    [Header("Performance Tracking")]
    public float reportInterval = 5f;
    public bool trackFPS = true;
    public bool trackMemory = true;
    public bool trackBatches = true;
    
    private float nextReportTime;
    
    void Update()
    {
        if (Time.time >= nextReportTime)
        {
            ReportPerformanceMetrics();
            nextReportTime = Time.time + reportInterval;
        }
    }
    
    void ReportPerformanceMetrics()
    {
        if (AnalyticsManager.Instance == null)
            return;
        
        if (trackFPS)
        {
            float fps = 1f / Time.smoothDeltaTime;
            AnalyticsManager.Instance.TrackPerformanceMetric("fps", fps);
        }
        
        if (trackMemory)
        {
            float memoryMB = UnityEngine.Profiling.Profiler.GetTotalAllocatedMemory(false) / (1024f * 1024f);
            AnalyticsManager.Instance.TrackPerformanceMetric("memory_mb", memoryMB);
        }
        
        if (trackBatches)
        {
            // This would require additional implementation to track draw calls
            AnalyticsManager.Instance.TrackPerformanceMetric("draw_calls", 0);
        }
    }
}
```

## 🚀 AI/LLM Integration
- Automatically analyze player behavior patterns
- Generate insights from collected metrics
- Create personalized game recommendations based on analytics

## 💡 Key Benefits
- Comprehensive player behavior tracking
- Performance monitoring and optimization
- Data-driven game improvement insights