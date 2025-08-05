# @a-Unity-Game-Analytics-Implementation

## 🎯 Learning Objectives
- Master comprehensive game analytics implementation in Unity
- Build custom analytics pipelines for player behavior tracking
- Implement real-time data visualization and monitoring systems
- Create automated reporting and business intelligence dashboards

## 🔧 Core Unity Analytics Framework

### Custom Analytics Manager
```csharp
using UnityEngine;
using System.Collections.Generic;
using System.Collections;
using Newtonsoft.Json;
using UnityEngine.Networking;
using System;

public class GameAnalyticsManager : MonoBehaviour
{
    [System.Serializable]
    public class AnalyticsConfig
    {
        public string apiKey;
        public string endpointUrl;
        public bool enableDebugLogging = true;
        public int batchSize = 50;
        public float flushInterval = 30f;
        public bool enableOfflineQueue = true;
    }

    [SerializeField] private AnalyticsConfig config;
    
    private Queue<AnalyticsEvent> eventQueue = new Queue<AnalyticsEvent>();
    private List<AnalyticsEvent> pendingEvents = new List<AnalyticsEvent>();
    private string sessionId;
    private string playerId;
    private float sessionStartTime;
    private Dictionary<string, object> sessionProperties;

    public static GameAnalyticsManager Instance { get; private set; }

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

    private void InitializeAnalytics()
    {
        sessionId = System.Guid.NewGuid().ToString();
        playerId = GetOrCreatePlayerId();
        sessionStartTime = Time.realtimeSinceStartup;
        
        sessionProperties = new Dictionary<string, object>
        {
            { "device_model", SystemInfo.deviceModel },
            { "device_type", SystemInfo.deviceType.ToString() },
            { "operating_system", SystemInfo.operatingSystem },
            { "processor_type", SystemInfo.processorType },
            { "graphics_device_name", SystemInfo.graphicsDeviceName },
            { "system_memory_size", SystemInfo.systemMemorySize },
            { "graphics_memory_size", SystemInfo.graphicsMemorySize },
            { "screen_resolution", $"{Screen.width}x{Screen.height}" },
            { "unity_version", Application.unityVersion },
            { "app_version", Application.version },
            { "platform", Application.platform.ToString() }
        };

        // Start session
        TrackEvent("session_start", sessionProperties);
        
        // Start periodic flush coroutine
        StartCoroutine(PeriodicFlush());
        
        Debug.Log($"Analytics initialized - Session: {sessionId}, Player: {playerId}");
    }

    public void TrackEvent(string eventName, Dictionary<string, object> properties = null)
    {
        var analyticsEvent = new AnalyticsEvent
        {
            eventName = eventName,
            sessionId = sessionId,
            playerId = playerId,
            timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
            sessionTime = Time.realtimeSinceStartup - sessionStartTime,
            properties = properties ?? new Dictionary<string, object>()
        };

        // Add standard properties
        analyticsEvent.properties["level"] = GetCurrentLevel();
        analyticsEvent.properties["game_mode"] = GetCurrentGameMode();
        analyticsEvent.properties["platform"] = Application.platform.ToString();

        eventQueue.Enqueue(analyticsEvent);

        if (config.enableDebugLogging)
        {
            Debug.Log($"Analytics Event: {eventName} - {JsonConvert.SerializeObject(analyticsEvent.properties)}");
        }

        // Auto-flush if queue is full
        if (eventQueue.Count >= config.batchSize)
        {
            FlushEvents();
        }
    }

    public void TrackLevelStart(int level, string gameMode = "")
    {
        var properties = new Dictionary<string, object>
        {
            { "level", level },
            { "game_mode", gameMode },
            { "attempts", GetLevelAttempts(level) }
        };
        
        TrackEvent("level_start", properties);
    }

    public void TrackLevelComplete(int level, float completionTime, int score, bool firstTime = false)
    {
        var properties = new Dictionary<string, object>
        {
            { "level", level },
            { "completion_time", completionTime },
            { "score", score },
            { "first_completion", firstTime },
            { "attempts", GetLevelAttempts(level) }
        };
        
        TrackEvent("level_complete", properties);
    }

    public void TrackLevelFail(int level, float timeSpent, string failReason = "")
    {
        var properties = new Dictionary<string, object>
        {
            { "level", level },
            { "time_spent", timeSpent },
            { "fail_reason", failReason },
            { "attempts", GetLevelAttempts(level) }
        };
        
        TrackEvent("level_fail", properties);
    }

    public void TrackPurchase(string itemId, string itemType, int quantity, float price, string currency = "USD")
    {
        var properties = new Dictionary<string, object>
        {
            { "item_id", itemId },
            { "item_type", itemType },
            { "quantity", quantity },
            { "price", price },
            { "currency", currency },
            { "player_level", GetCurrentLevel() },
            { "total_purchases", GetTotalPurchases() }
        };
        
        TrackEvent("item_purchase", properties);
    }

    public void TrackUserAction(string action, string context = "", Dictionary<string, object> additionalData = null)
    {
        var properties = new Dictionary<string, object>
        {
            { "action", action },
            { "context", context }
        };

        if (additionalData != null)
        {
            foreach (var kvp in additionalData)
            {
                properties[kvp.Key] = kvp.Value;
            }
        }
        
        TrackEvent("user_action", properties);
    }

    public void TrackPerformanceMetric(string metricName, float value, string unit = "")
    {
        var properties = new Dictionary<string, object>
        {
            { "metric_name", metricName },
            { "value", value },
            { "unit", unit },
            { "fps", (int)(1f / Time.deltaTime) },
            { "memory_usage", GC.GetTotalMemory(false) / 1024f / 1024f } // MB
        };
        
        TrackEvent("performance_metric", properties);
    }

    public void FlushEvents()
    {
        if (eventQueue.Count == 0) return;

        var eventsToSend = new List<AnalyticsEvent>();
        while (eventQueue.Count > 0 && eventsToSend.Count < config.batchSize)
        {
            eventsToSend.Add(eventQueue.Dequeue());
        }

        StartCoroutine(SendEventsToServer(eventsToSend));
    }

    private IEnumerator SendEventsToServer(List<AnalyticsEvent> events)
    {
        var payload = new AnalyticsPayload
        {
            events = events,
            sessionId = sessionId,
            playerId = playerId,
            timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()
        };

        string jsonPayload = JsonConvert.SerializeObject(payload);
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonPayload);

        using (UnityWebRequest request = new UnityWebRequest(config.endpointUrl, "POST"))
        {
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.SetRequestHeader("Authorization", $"Bearer {config.apiKey}");

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                if (config.enableDebugLogging)
                {
                    Debug.Log($"Analytics batch sent successfully: {events.Count} events");
                }
            }
            else
            {
                Debug.LogError($"Analytics send failed: {request.error}");
                
                // Re-queue events if enabled
                if (config.enableOfflineQueue)
                {
                    foreach (var analyticsEvent in events)
                    {
                        eventQueue.Enqueue(analyticsEvent);
                    }
                }
            }
        }
    }

    private IEnumerator PeriodicFlush()
    {
        while (true)
        {
            yield return new WaitForSeconds(config.flushInterval);
            FlushEvents();
        }
    }

    private string GetOrCreatePlayerId()
    {
        string playerId = PlayerPrefs.GetString("analytics_player_id", "");
        if (string.IsNullOrEmpty(playerId))
        {
            playerId = System.Guid.NewGuid().ToString();
            PlayerPrefs.SetString("analytics_player_id", playerId);
            PlayerPrefs.Save();
        }
        return playerId;
    }

    private int GetCurrentLevel()
    {
        // Implement based on your game's level system
        return PlayerPrefs.GetInt("current_level", 1);
    }

    private string GetCurrentGameMode()
    {
        // Implement based on your game's mode system
        return "default";
    }

    private int GetLevelAttempts(int level)
    {
        return PlayerPrefs.GetInt($"level_{level}_attempts", 0);
    }

    private int GetTotalPurchases()
    {
        return PlayerPrefs.GetInt("total_purchases", 0);
    }

    void OnApplicationPause(bool pauseStatus)
    {
        if (pauseStatus)
        {
            TrackEvent("app_pause");
            FlushEvents();
        }
        else
        {
            TrackEvent("app_resume");
        }
    }

    void OnApplicationFocus(bool hasFocus)
    {
        if (!hasFocus)
        {
            FlushEvents();
        }
    }

    void OnDestroy()
    {
        TrackEvent("session_end", new Dictionary<string, object>
        {
            { "session_duration", Time.realtimeSinceStartup - sessionStartTime }
        });
        FlushEvents();
    }
}

[System.Serializable]
public class AnalyticsEvent
{
    public string eventName;
    public string sessionId;
    public string playerId;
    public long timestamp;
    public float sessionTime;
    public Dictionary<string, object> properties;
}

[System.Serializable]
public class AnalyticsPayload
{
    public List<AnalyticsEvent> events;
    public string sessionId;
    public string playerId;
    public long timestamp;
}
```

## 🚀 Real-Time Analytics Dashboard

### Unity Analytics Visualizer
```csharp
using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;
using System.Linq;

public class AnalyticsVisualizerUI : MonoBehaviour
{
    [Header("UI References")]
    [SerializeField] private Text sessionInfoText;
    [SerializeField] private Text eventsCountText;
    [SerializeField] private Transform eventListParent;
    [SerializeField] private GameObject eventItemPrefab;
    [SerializeField] private ScrollRect eventScrollRect;
    [SerializeField] private Toggle enableAnalyticsToggle;
    [SerializeField] private Button clearEventsButton;
    [SerializeField] private Button exportDataButton;

    [Header("Performance Metrics")]
    [SerializeField] private Text fpsText;
    [SerializeField] private Text memoryText;
    [SerializeField] private Text batteryText;
    [SerializeField] private Image performanceIndicator;

    private List<AnalyticsEventDisplay> displayedEvents = new List<AnalyticsEventDisplay>();
    private Queue<string> recentEvents = new Queue<string>();
    private const int MAX_DISPLAYED_EVENTS = 100;

    private float fpsUpdateInterval = 0.5f;
    private float fpsTimer = 0f;
    private int fpsFrameCount = 0;
    private float fpsSum = 0f;

    void Start()
    {
        InitializeUI();
        InvokeRepeating(nameof(UpdatePerformanceMetrics), 1f, 1f);
    }

    void Update()
    {
        UpdateFPSCounter();
        UpdateEventDisplay();
    }

    private void InitializeUI()
    {
        enableAnalyticsToggle.isOn = GameAnalyticsManager.Instance != null;
        enableAnalyticsToggle.onValueChanged.AddListener(OnAnalyticsToggled);
        
        clearEventsButton.onClick.AddListener(ClearEventDisplay);
        exportDataButton.onClick.AddListener(ExportAnalyticsData);

        UpdateSessionInfo();
    }

    private void UpdateSessionInfo()
    {
        if (GameAnalyticsManager.Instance != null)
        {
            sessionInfoText.text = $"Session Active\nPlayer ID: {GameAnalyticsManager.Instance.playerId}\nSession: {GameAnalyticsManager.Instance.sessionId}";
        }
        else
        {
            sessionInfoText.text = "Analytics Disabled";
        }
    }

    private void UpdateEventDisplay()
    {
        // This would be called by the analytics manager when new events are tracked
        eventsCountText.text = $"Events: {recentEvents.Count}";
    }

    public void OnEventTracked(string eventName, Dictionary<string, object> properties)
    {
        string eventDisplay = $"[{System.DateTime.Now:HH:mm:ss}] {eventName}";
        if (properties != null && properties.Count > 0)
        {
            eventDisplay += $" - {string.Join(", ", properties.Select(kvp => $"{kvp.Key}:{kvp.Value}"))}";
        }

        recentEvents.Enqueue(eventDisplay);

        // Limit queue size
        while (recentEvents.Count > MAX_DISPLAYED_EVENTS)
        {
            recentEvents.Dequeue();
        }

        UpdateEventListUI();
    }

    private void UpdateEventListUI()
    {
        // Clear existing items
        foreach (Transform child in eventListParent)
        {
            Destroy(child.gameObject);
        }

        // Add recent events
        foreach (string eventText in recentEvents.Reverse())
        {
            GameObject eventItem = Instantiate(eventItemPrefab, eventListParent);
            Text eventLabel = eventItem.GetComponentInChildren<Text>();
            eventLabel.text = eventText;
        }

        // Scroll to bottom
        Canvas.ForceUpdateCanvases();
        eventScrollRect.verticalNormalizedPosition = 0f;
    }

    private void UpdateFPSCounter()
    {
        fpsTimer += Time.deltaTime;
        fpsFrameCount++;
        fpsSum += 1f / Time.deltaTime;

        if (fpsTimer >= fpsUpdateInterval)
        {
            float averageFPS = fpsSum / fpsFrameCount;
            fpsText.text = $"FPS: {averageFPS:F1}";

            // Update performance indicator color
            if (averageFPS >= 55f)
                performanceIndicator.color = Color.green;
            else if (averageFPS >= 30f)
                performanceIndicator.color = Color.yellow;
            else
                performanceIndicator.color = Color.red;

            fpsTimer = 0f;
            fpsFrameCount = 0;
            fpsSum = 0f;
        }
    }

    private void UpdatePerformanceMetrics()
    {
        // Memory usage
        long memoryUsage = System.GC.GetTotalMemory(false);
        float memoryMB = memoryUsage / (1024f * 1024f);
        memoryText.text = $"Memory: {memoryMB:F1} MB";

        // Battery level (mobile only)
        if (Application.isMobilePlatform)
        {
            float batteryLevel = SystemInfo.batteryLevel;
            if (batteryLevel >= 0)
            {
                batteryText.text = $"Battery: {batteryLevel * 100:F0}%";
            }
            else
            {
                batteryText.text = "Battery: Unknown";
            }
        }
        else
        {
            batteryText.text = "Battery: N/A";
        }

        // Track performance metrics
        if (GameAnalyticsManager.Instance != null)
        {
            GameAnalyticsManager.Instance.TrackPerformanceMetric("fps", 1f / Time.deltaTime);
            GameAnalyticsManager.Instance.TrackPerformanceMetric("memory_mb", memoryMB);
        }
    }

    private void OnAnalyticsToggled(bool enabled)
    {
        if (enabled && GameAnalyticsManager.Instance == null)
        {
            // Re-enable analytics (would need to recreate manager)
            Debug.Log("Analytics re-enabled");
        }
        else if (!enabled && GameAnalyticsManager.Instance != null)
        {
            // Disable analytics
            GameAnalyticsManager.Instance.gameObject.SetActive(false);
        }

        UpdateSessionInfo();
    }

    private void ClearEventDisplay()
    {
        recentEvents.Clear();
        UpdateEventListUI();
    }

    private void ExportAnalyticsData()
    {
        // Export recent events to JSON file
        var exportData = new
        {
            exportTime = System.DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ"),
            events = recentEvents.ToArray(),
            sessionInfo = new
            {
                playerId = GameAnalyticsManager.Instance?.playerId,
                sessionId = GameAnalyticsManager.Instance?.sessionId,
                platform = Application.platform.ToString(),
                version = Application.version
            }
        };

        string json = JsonUtility.ToJson(exportData, true);
        string filename = $"analytics_export_{System.DateTime.Now:yyyyMMdd_HHmmss}.json";
        
        System.IO.File.WriteAllText(System.IO.Path.Combine(Application.persistentDataPath, filename), json);
        Debug.Log($"Analytics data exported to: {filename}");
    }
}

[System.Serializable]
public class AnalyticsEventDisplay
{
    public string eventName;
    public string timestamp;
    public string properties;
}
```

## 🔧 Advanced Analytics Patterns

### Player Behavior Analysis
```csharp
using UnityEngine;
using System.Collections.Generic;
using System.Linq;

public class PlayerBehaviorAnalyzer : MonoBehaviour
{
    [System.Serializable]
    public class PlayerSegment
    {
        public string segmentName;
        public List<string> criteria;
        public int playerCount;
        public float retentionRate;
    }

    [System.Serializable]
    public class BehaviorPattern
    {
        public string patternName;
        public List<string> eventSequence;
        public float frequency;
        public float averageTimeBetweenEvents;
    }

    private Dictionary<string, List<AnalyticsEvent>> playerEventHistory = new Dictionary<string, List<AnalyticsEvent>>();
    private List<PlayerSegment> playerSegments = new List<PlayerSegment>();
    private List<BehaviorPattern> detectedPatterns = new List<BehaviorPattern>();

    public void AnalyzePlayerBehavior(string playerId, List<AnalyticsEvent> events)
    {
        if (!playerEventHistory.ContainsKey(playerId))
        {
            playerEventHistory[playerId] = new List<AnalyticsEvent>();
        }

        playerEventHistory[playerId].AddRange(events);

        // Analyze patterns
        DetectEngagementPatterns(playerId);
        DetectChurnRisk(playerId);
        DetectMonetizationOpportunities(playerId);
        UpdatePlayerSegmentation(playerId);
    }

    private void DetectEngagementPatterns(string playerId)
    {
        var playerEvents = playerEventHistory[playerId];
        var sessionEvents = playerEvents.Where(e => e.eventName == "session_start").ToList();

        if (sessionEvents.Count >= 7) // At least a week of data
        {
            var engagementMetrics = new Dictionary<string, object>
            {
                { "sessions_per_week", sessionEvents.Count },
                { "average_session_length", CalculateAverageSessionLength(playerId) },
                { "retention_day_1", CalculateRetention(playerId, 1) },
                { "retention_day_7", CalculateRetention(playerId, 7) },
                { "retention_day_30", CalculateRetention(playerId, 30) }
            };

            GameAnalyticsManager.Instance.TrackEvent("player_engagement_analysis", engagementMetrics);
        }
    }

    private void DetectChurnRisk(string playerId)
    {
        var playerEvents = playerEventHistory[playerId];
        var lastEventTime = playerEvents.OrderByDescending(e => e.timestamp).FirstOrDefault()?.timestamp ?? 0;
        var currentTime = System.DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        
        var daysSinceLastActivity = (currentTime - lastEventTime) / (1000 * 60 * 60 * 24);

        var churnRiskFactors = new Dictionary<string, object>
        {
            { "days_since_last_activity", daysSinceLastActivity },
            { "total_sessions", playerEvents.Count(e => e.eventName == "session_start") },
            { "completed_levels", playerEvents.Count(e => e.eventName == "level_complete") },
            { "failed_levels", playerEvents.Count(e => e.eventName == "level_fail") },
            { "purchases", playerEvents.Count(e => e.eventName == "item_purchase") }
        };

        // Calculate churn risk score (0-100)
        float churnRiskScore = CalculateChurnRiskScore(churnRiskFactors);
        churnRiskFactors["churn_risk_score"] = churnRiskScore;

        if (churnRiskScore > 70)
        {
            GameAnalyticsManager.Instance.TrackEvent("high_churn_risk_detected", churnRiskFactors);
        }
    }

    private void DetectMonetizationOpportunities(string playerId)
    {
        var playerEvents = playerEventHistory[playerId];
        var levelCompleteEvents = playerEvents.Where(e => e.eventName == "level_complete").ToList();
        var purchaseEvents = playerEvents.Where(e => e.eventName == "item_purchase").ToList();

        var monetizationMetrics = new Dictionary<string, object>
        {
            { "levels_completed", levelCompleteEvents.Count },
            { "purchases_made", purchaseEvents.Count },
            { "time_to_first_purchase", CalculateTimeToFirstPurchase(playerId) },
            { "average_session_length", CalculateAverageSessionLength(playerId) },
            { "engagement_score", CalculateEngagementScore(playerId) }
        };

        // Identify monetization opportunity
        if (purchaseEvents.Count == 0 && levelCompleteEvents.Count > 5)
        {
            monetizationMetrics["opportunity_type"] = "non_paying_engaged_user";
            GameAnalyticsManager.Instance.TrackEvent("monetization_opportunity", monetizationMetrics);
        }
    }

    private void UpdatePlayerSegmentation(string playerId)
    {
        var playerEvents = playerEventHistory[playerId];
        
        // Define segments based on behavior
        if (IsWhalePlayer(playerId))
        {
            AssignPlayerToSegment(playerId, "whale");
        }
        else if (IsRegularSpender(playerId))
        {
            AssignPlayerToSegment(playerId, "regular_spender");
        }
        else if (IsHighlyEngaged(playerId))
        {
            AssignPlayerToSegment(playerId, "highly_engaged_f2p");
        }
        else if (IsAtRiskPlayer(playerId))
        {
            AssignPlayerToSegment(playerId, "at_risk");
        }
        else
        {
            AssignPlayerToSegment(playerId, "casual");
        }
    }

    private float CalculateAverageSessionLength(string playerId)
    {
        var playerEvents = playerEventHistory[playerId];
        var sessionStarts = playerEvents.Where(e => e.eventName == "session_start").ToList();
        var sessionEnds = playerEvents.Where(e => e.eventName == "session_end").ToList();

        if (sessionStarts.Count == 0 || sessionEnds.Count == 0) return 0f;

        float totalSessionTime = 0f;
        int validSessions = 0;

        for (int i = 0; i < Mathf.Min(sessionStarts.Count, sessionEnds.Count); i++)
        {
            var sessionLength = sessionEnds[i].timestamp - sessionStarts[i].timestamp;
            if (sessionLength > 0 && sessionLength < 24 * 60 * 60 * 1000) // Valid session (less than 24 hours)
            {
                totalSessionTime += sessionLength / 1000f; // Convert to seconds
                validSessions++;
            }
        }

        return validSessions > 0 ? totalSessionTime / validSessions : 0f;
    }

    private bool CalculateRetention(string playerId, int days)
    {
        var playerEvents = playerEventHistory[playerId];
        var firstSession = playerEvents.Where(e => e.eventName == "session_start").OrderBy(e => e.timestamp).FirstOrDefault();
        
        if (firstSession == null) return false;

        var retentionDate = firstSession.timestamp + (days * 24 * 60 * 60 * 1000);
        var sessionsAfterRetentionDate = playerEvents.Where(e => e.eventName == "session_start" && e.timestamp >= retentionDate).ToList();

        return sessionsAfterRetentionDate.Count > 0;
    }

    private float CalculateChurnRiskScore(Dictionary<string, object> factors)
    {
        float score = 0f;

        // Days since last activity (40% weight)
        if (factors.ContainsKey("days_since_last_activity"))
        {
            float days = (float)factors["days_since_last_activity"];
            score += Mathf.Clamp01(days / 7f) * 40f; // 7+ days = max risk
        }

        // Session frequency (30% weight)
        if (factors.ContainsKey("total_sessions"))
        {
            int sessions = (int)factors["total_sessions"];
            score += Mathf.Clamp01(1f - (sessions / 50f)) * 30f; // Less than 50 sessions = risk
        }

        // Purchase behavior (20% weight)
        if (factors.ContainsKey("purchases"))
        {
            int purchases = (int)factors["purchases"];
            score += purchases == 0 ? 20f : 0f; // No purchases = risk
        }

        // Level progression (10% weight)
        if (factors.ContainsKey("completed_levels") && factors.ContainsKey("failed_levels"))
        {
            int completed = (int)factors["completed_levels"];
            int failed = (int)factors["failed_levels"];
            float successRate = completed + failed > 0 ? (float)completed / (completed + failed) : 0f;
            score += (1f - successRate) * 10f; // Low success rate = risk
        }

        return Mathf.Clamp(score, 0f, 100f);
    }

    private float CalculateTimeToFirstPurchase(string playerId)
    {
        var playerEvents = playerEventHistory[playerId];
        var firstSession = playerEvents.Where(e => e.eventName == "session_start").OrderBy(e => e.timestamp).FirstOrDefault();
        var firstPurchase = playerEvents.Where(e => e.eventName == "item_purchase").OrderBy(e => e.timestamp).FirstOrDefault();

        if (firstSession == null || firstPurchase == null) return -1f;

        return (firstPurchase.timestamp - firstSession.timestamp) / (1000f * 60f * 60f); // Hours
    }

    private float CalculateEngagementScore(string playerId)
    {
        var playerEvents = playerEventHistory[playerId];
        var totalSessions = playerEvents.Count(e => e.eventName == "session_start");
        var levelsCompleted = playerEvents.Count(e => e.eventName == "level_complete");
        var averageSessionLength = CalculateAverageSessionLength(playerId);

        // Normalize and combine metrics (0-100 scale)
        float sessionScore = Mathf.Clamp01(totalSessions / 100f) * 40f;
        float progressScore = Mathf.Clamp01(levelsCompleted / 50f) * 40f;
        float timeScore = Mathf.Clamp01(averageSessionLength / 300f) * 20f; // 5 minutes = max

        return sessionScore + progressScore + timeScore;
    }

    private bool IsWhalePlayer(string playerId)
    {
        var playerEvents = playerEventHistory[playerId];
        var purchases = playerEvents.Where(e => e.eventName == "item_purchase").ToList();
        
        // Calculate total spending (simplified - would need actual price data)
        return purchases.Count >= 10; // 10+ purchases qualifies as whale
    }

    private bool IsRegularSpender(string playerId)
    {
        var playerEvents = playerEventHistory[playerId];
        var purchases = playerEvents.Where(e => e.eventName == "item_purchase").ToList();
        
        return purchases.Count >= 3 && purchases.Count < 10;
    }

    private bool IsHighlyEngaged(string playerId)
    {
        return CalculateEngagementScore(playerId) > 70f;
    }

    private bool IsAtRiskPlayer(string playerId)
    {
        var riskFactors = new Dictionary<string, object>();
        return CalculateChurnRiskScore(riskFactors) > 60f;
    }

    private void AssignPlayerToSegment(string playerId, string segmentName)
    {
        var properties = new Dictionary<string, object>
        {
            { "player_id", playerId },
            { "segment", segmentName },
            { "assignment_time", System.DateTimeOffset.UtcNow.ToString() }
        };

        GameAnalyticsManager.Instance.TrackEvent("player_segment_assignment", properties);
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Automated Analytics Insights
```prompt
Generate automated analytics insights for Unity game data including:
- Player behavior pattern detection and analysis
- Churn prediction models with actionable recommendations
- Monetization optimization strategies based on player segments
- A/B testing frameworks for feature optimization
- Real-time anomaly detection for game metrics
- Personalized player experience recommendations
```

### Business Intelligence Dashboard
```prompt
Create comprehensive BI dashboard for Unity game analytics:
- KPI tracking with industry benchmarks
- Player lifecycle analysis and retention funnels
- Revenue analytics and monetization insights
- Performance monitoring and technical health metrics
- Competitive analysis integration
- Automated reporting and alert systems
```

## 💡 Key Analytics Implementation Best Practices

### 1. Data Quality & Validation
- Implement schema validation for all events
- Use consistent naming conventions across events
- Validate data types and ranges before sending
- Monitor for duplicate or malformed events

### 2. Performance Optimization
- Batch events to reduce network calls
- Implement local caching for offline scenarios
- Use efficient serialization formats
- Monitor analytics overhead on game performance

### 3. Privacy & Compliance
- Implement opt-out mechanisms for data collection
- Anonymize personally identifiable information
- Comply with GDPR, CCPA, and regional regulations
- Provide transparent data usage policies

### 4. Actionable Insights
- Focus on metrics that drive business decisions
- Implement real-time alerting for critical events
- Create automated analysis and reporting
- Build feedback loops for continuous optimization

This comprehensive analytics framework provides everything needed to implement professional-grade game analytics that drive data-informed decisions and optimize player experience.