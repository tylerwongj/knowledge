# 01-Unity-REST-API-Integration.md

## 🎯 Learning Objectives
- Master RESTful API integration in Unity applications
- Implement secure HTTP client systems with authentication
- Design robust error handling and retry mechanisms for network operations
- Develop efficient data serialization and caching strategies for API responses

## 🔧 Unity REST API Implementation

### Comprehensive HTTP Client Manager
```csharp
// Scripts/Networking/APIManager.cs
using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;

public class APIManager : MonoBehaviour
{
    [Header("API Configuration")]
    [SerializeField] private string baseURL = "https://api.yourgame.com";
    [SerializeField] private float defaultTimeout = 30f;
    [SerializeField] private int maxRetryAttempts = 3;
    [SerializeField] private float retryDelay = 1f;
    [SerializeField] private bool enableLogging = true;
    
    public static APIManager Instance { get; private set; }
    
    // Events
    public System.Action<bool> OnConnectivityChanged;
    public System.Action<APIError> OnAPIError;
    
    // Properties
    public bool IsOnline { get; private set; } = true;
    public string BaseURL => baseURL;
    
    private Dictionary<string, string> defaultHeaders;
    private Queue<APIRequest> requestQueue;
    private bool isProcessingQueue = false;
    private APICache cache;
    
    // Request tracking
    private Dictionary<string, UnityWebRequest> activeRequests;
    private int requestCounter = 0;
    
    [System.Serializable]
    public class APIRequest
    {
        public string id;
        public string method;
        public string endpoint;
        public object data;
        public Dictionary<string, string> headers;
        public float timeout;
        public int retryCount;
        public System.Action<APIResponse> onSuccess;
        public System.Action<APIError> onError;
        public bool useCache;
        public float cacheExpiry;
        
        public APIRequest()
        {
            headers = new Dictionary<string, string>();
            retryCount = 0;
            useCache = false;
            cacheExpiry = 300f; // 5 minutes default
        }
    }
    
    [System.Serializable]
    public class APIResponse
    {
        public int statusCode;
        public string data;
        public Dictionary<string, string> headers;
        public bool fromCache;
        public DateTime timestamp;
        
        public T GetData<T>()
        {
            try
            {
                return JsonConvert.DeserializeObject<T>(data);
            }
            catch (Exception e)
            {
                Debug.LogError($"Failed to deserialize API response: {e.Message}");
                return default(T);
            }
        }
    }
    
    [System.Serializable]
    public class APIError
    {
        public int statusCode;
        public string message;
        public string endpoint;
        public string method;
        public DateTime timestamp;
        public Exception exception;
    }
    
    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            Initialize();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    private void Initialize()
    {
        // Initialize collections
        defaultHeaders = new Dictionary<string, string>
        {
            {"Content-Type", "application/json"},
            {"Accept", "application/json"},
            {"User-Agent", $"Unity/{Application.unityVersion} ({Application.productName}/{Application.version})"}
        };
        
        requestQueue = new Queue<APIRequest>();
        activeRequests = new Dictionary<string, UnityWebRequest>();
        cache = new APICache();
        
        // Start connectivity monitoring
        StartCoroutine(MonitorConnectivity());
        
        // Start request queue processor
        StartCoroutine(ProcessRequestQueue());
    }
    
    // Public API methods
    public void GET<T>(string endpoint, System.Action<T> onSuccess, System.Action<APIError> onError = null, 
        bool useCache = true, float cacheExpiry = 300f)
    {
        var request = new APIRequest
        {
            method = "GET",
            endpoint = endpoint,
            onSuccess = (response) => onSuccess?.Invoke(response.GetData<T>()),
            onError = onError,
            useCache = useCache,
            cacheExpiry = cacheExpiry
        };
        
        EnqueueRequest(request);
    }
    
    public void POST<T>(string endpoint, object data, System.Action<T> onSuccess, 
        System.Action<APIError> onError = null)
    {
        var request = new APIRequest
        {
            method = "POST",
            endpoint = endpoint,
            data = data,
            onSuccess = (response) => onSuccess?.Invoke(response.GetData<T>()),
            onError = onError
        };
        
        EnqueueRequest(request);
    }
    
    public void PUT<T>(string endpoint, object data, System.Action<T> onSuccess, 
        System.Action<APIError> onError = null)
    {
        var request = new APIRequest
        {
            method = "PUT",
            endpoint = endpoint,
            data = data,
            onSuccess = (response) => onSuccess?.Invoke(response.GetData<T>()),
            onError = onError
        };
        
        EnqueueRequest(request);
    }
    
    public void DELETE(string endpoint, System.Action<bool> onSuccess, System.Action<APIError> onError = null)
    {
        var request = new APIRequest
        {
            method = "DELETE",
            endpoint = endpoint,
            onSuccess = (response) => onSuccess?.Invoke(response.statusCode >= 200 && response.statusCode < 300),
            onError = onError
        };
        
        EnqueueRequest(request);
    }
    
    // Advanced request method with full control
    public void SendRequest(APIRequest request)
    {
        EnqueueRequest(request);
    }
    
    private void EnqueueRequest(APIRequest request)
    {
        // Generate unique request ID
        request.id = $"req_{++requestCounter}_{DateTime.UtcNow.Ticks}";
        request.timeout = request.timeout > 0 ? request.timeout : defaultTimeout;
        
        // Check cache for GET requests
        if (request.method == "GET" && request.useCache)
        {
            var cachedResponse = cache.Get(GetCacheKey(request));
            if (cachedResponse != null)
            {
                LogRequest($"Cache hit for {request.method} {request.endpoint}");
                request.onSuccess?.Invoke(cachedResponse);
                return;
            }
        }
        
        // Add to queue
        requestQueue.Enqueue(request);
        
        LogRequest($"Enqueued {request.method} {request.endpoint} (ID: {request.id})");
    }
    
    private IEnumerator ProcessRequestQueue()
    {
        while (true)
        {
            if (!isProcessingQueue && requestQueue.Count > 0)
            {
                isProcessingQueue = true;
                var request = requestQueue.Dequeue();
                
                yield return StartCoroutine(ExecuteRequest(request));
                
                isProcessingQueue = false;
                
                // Small delay between requests to prevent overwhelming the server
                yield return new WaitForSeconds(0.1f);
            }
            else
            {
                yield return new WaitForSeconds(0.1f);
            }
        }
    }
    
    private IEnumerator ExecuteRequest(APIRequest request)
    {
        // Check connectivity
        if (!IsOnline)
        {
            var error = new APIError
            {
                statusCode = 0,
                message = "No internet connection",
                endpoint = request.endpoint,
                method = request.method,
                timestamp = DateTime.UtcNow
            };
            
            request.onError?.Invoke(error);
            yield break;
        }
        
        string url = baseURL + request.endpoint;
        UnityWebRequest webRequest = null;
        
        try
        {
            // Create appropriate request based on method
            switch (request.method.ToUpper())
            {
                case "GET":
                    webRequest = UnityWebRequest.Get(url);
                    break;
                
                case "POST":
                    string postData = request.data != null ? JsonConvert.SerializeObject(request.data) : "";
                    webRequest = UnityWebRequest.PostWwwForm(url, "");
                    webRequest.uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(postData));
                    break;
                
                case "PUT":
                    string putData = request.data != null ? JsonConvert.SerializeObject(request.data) : "";
                    webRequest = UnityWebRequest.Put(url, putData);
                    break;
                
                case "DELETE":
                    webRequest = UnityWebRequest.Delete(url);
                    break;
                
                default:
                    throw new NotSupportedException($"HTTP method {request.method} is not supported");
            }
            
            // Set headers
            foreach (var header in defaultHeaders)
            {
                webRequest.SetRequestHeader(header.Key, header.Value);
            }
            
            foreach (var header in request.headers)
            {
                webRequest.SetRequestHeader(header.Key, header.Value);
            }
            
            // Add authentication if available
            if (AuthenticationManager.Instance != null && AuthenticationManager.Instance.IsAuthenticated)
            {
                AuthenticationManager.Instance.AddAuthorizationHeader(webRequest);
            }
            
            // Set timeout
            webRequest.timeout = (int)request.timeout;
            
            // Track active request
            activeRequests[request.id] = webRequest;
            
            LogRequest($"Sending {request.method} {url}");
            
            // Send request
            yield return webRequest.SendWebRequest();
            
            // Remove from active requests
            activeRequests.Remove(request.id);
            
            // Handle response
            if (webRequest.result == UnityWebRequest.Result.Success)
            {
                var response = new APIResponse
                {
                    statusCode = (int)webRequest.responseCode,
                    data = webRequest.downloadHandler.text,
                    headers = ParseResponseHeaders(webRequest),
                    fromCache = false,
                    timestamp = DateTime.UtcNow
                };
                
                LogRequest($"Success {request.method} {url} ({response.statusCode})");
                
                // Cache GET responses
                if (request.method == "GET" && request.useCache)
                {
                    cache.Set(GetCacheKey(request), response, request.cacheExpiry);
                }
                
                request.onSuccess?.Invoke(response);
            }
            else
            {
                // Handle error with retry logic
                yield return StartCoroutine(HandleRequestError(request, webRequest));
            }
        }
        catch (Exception e)
        {
            LogError($"Exception in request {request.method} {url}: {e.Message}");
            
            var error = new APIError
            {
                statusCode = 0,
                message = e.Message,
                endpoint = request.endpoint,
                method = request.method,
                timestamp = DateTime.UtcNow,
                exception = e
            };
            
            request.onError?.Invoke(error);
            OnAPIError?.Invoke(error);
        }
        finally
        {
            webRequest?.Dispose();
        }
    }
    
    private IEnumerator HandleRequestError(APIRequest request, UnityWebRequest webRequest)
    {
        var statusCode = (int)webRequest.responseCode;
        var errorMessage = webRequest.error;
        
        LogError($"Error {request.method} {request.endpoint} ({statusCode}): {errorMessage}");
        
        // Determine if retry is appropriate
        bool shouldRetry = ShouldRetryRequest(statusCode, request.retryCount);
        
        if (shouldRetry && request.retryCount < maxRetryAttempts)
        {
            request.retryCount++;
            float delay = retryDelay * Mathf.Pow(2, request.retryCount - 1); // Exponential backoff
            
            LogRequest($"Retrying {request.method} {request.endpoint} in {delay}s (attempt {request.retryCount}/{maxRetryAttempts})");
            
            yield return new WaitForSeconds(delay);
            
            // Re-enqueue the request
            requestQueue.Enqueue(request);
        }
        else
        {
            // Final failure
            var error = new APIError
            {
                statusCode = statusCode,
                message = errorMessage,
                endpoint = request.endpoint,
                method = request.method,
                timestamp = DateTime.UtcNow
            };
            
            request.onError?.Invoke(error);
            OnAPIError?.Invoke(error);
        }
    }
    
    private bool ShouldRetryRequest(int statusCode, int retryCount)
    {
        // Retry on network errors and server errors (500-599)
        // Don't retry on client errors (400-499) except for specific cases
        if (statusCode == 0) return true; // Network error
        if (statusCode >= 500) return true; // Server error
        if (statusCode == 408) return true; // Request timeout
        if (statusCode == 429) return true; // Too many requests
        
        return false;
    }
    
    private Dictionary<string, string> ParseResponseHeaders(UnityWebRequest request)
    {
        var headers = new Dictionary<string, string>();
        
        var responseHeaders = request.GetResponseHeaders();
        if (responseHeaders != null)
        {
            foreach (var header in responseHeaders)
            {
                headers[header.Key] = header.Value;
            }
        }
        
        return headers;
    }
    
    private string GetCacheKey(APIRequest request)
    {
        return $"{request.method}:{request.endpoint}";
    }
    
    private IEnumerator MonitorConnectivity()
    {
        bool wasOnline = IsOnline;
        
        while (true)
        {
            IsOnline = Application.internetReachability != NetworkReachability.NotReachable;
            
            if (IsOnline != wasOnline)
            {
                LogRequest($"Connectivity changed: {(IsOnline ? "ONLINE" : "OFFLINE")}");
                OnConnectivityChanged?.Invoke(IsOnline);
                wasOnline = IsOnline;
            }
            
            yield return new WaitForSeconds(5f); // Check every 5 seconds
        }
    }
    
    // Public utility methods
    public void SetDefaultHeader(string key, string value)
    {
        defaultHeaders[key] = value;
    }
    
    public void RemoveDefaultHeader(string key)
    {
        defaultHeaders.Remove(key);
    }
    
    public void CancelRequest(string requestId)
    {
        if (activeRequests.ContainsKey(requestId))
        {
            activeRequests[requestId].Abort();
            activeRequests.Remove(requestId);
            LogRequest($"Cancelled request {requestId}");
        }
    }
    
    public void CancelAllRequests()
    {
        foreach (var request in activeRequests.Values)
        {
            request.Abort();
        }
        activeRequests.Clear();
        requestQueue.Clear();
        LogRequest("Cancelled all requests");
    }
    
    public void ClearCache()
    {
        cache.Clear();
        LogRequest("Cache cleared");
    }
    
    private void LogRequest(string message)
    {
        if (enableLogging)
        {
            Debug.Log($"[APIManager] {message}");
        }
    }
    
    private void LogError(string message)
    {
        if (enableLogging)
        {
            Debug.LogError($"[APIManager] {message}");
        }
    }
    
    private void OnDestroy()
    {
        CancelAllRequests();
    }
}
```

### API Response Caching System
```csharp
// Scripts/Networking/APICache.cs
using System;
using System.Collections.Generic;
using UnityEngine;

public class APICache
{
    private Dictionary<string, CacheEntry> cache;
    private float maxCacheSize = 50f * 1024 * 1024; // 50MB
    private float currentCacheSize = 0f;
    
    private class CacheEntry
    {
        public APIManager.APIResponse response;
        public DateTime expiryTime;
        public float size;
        public DateTime lastAccessed;
        
        public bool IsExpired => DateTime.UtcNow > expiryTime;
    }
    
    public APICache()
    {
        cache = new Dictionary<string, CacheEntry>();
    }
    
    public APIManager.APIResponse Get(string key)
    {
        if (cache.ContainsKey(key))
        {
            var entry = cache[key];
            
            if (!entry.IsExpired)
            {
                entry.lastAccessed = DateTime.UtcNow;
                entry.response.fromCache = true;
                return entry.response;
            }
            else
            {
                // Remove expired entry
                Remove(key);
            }
        }
        
        return null;
    }
    
    public void Set(string key, APIManager.APIResponse response, float expirySeconds)
    {
        // Calculate response size
        float responseSize = CalculateResponseSize(response);
        
        // Remove existing entry if it exists
        if (cache.ContainsKey(key))
        {
            Remove(key);
        }
        
        // Ensure we have space
        while (currentCacheSize + responseSize > maxCacheSize && cache.Count > 0)
        {
            RemoveLeastRecentlyUsed();
        }
        
        // Add new entry
        var entry = new CacheEntry
        {
            response = response,
            expiryTime = DateTime.UtcNow.AddSeconds(expirySeconds),
            size = responseSize,
            lastAccessed = DateTime.UtcNow
        };
        
        cache[key] = entry;
        currentCacheSize += responseSize;
        
        Debug.Log($"[APICache] Cached response for {key} ({responseSize:F1} bytes, expires in {expirySeconds}s)");
    }
    
    public void Remove(string key)
    {
        if (cache.ContainsKey(key))
        {
            currentCacheSize -= cache[key].size;
            cache.Remove(key);
        }
    }
    
    public void Clear()
    {
        cache.Clear();
        currentCacheSize = 0f;
        Debug.Log("[APICache] Cache cleared");
    }
    
    public void CleanupExpired()
    {
        var expiredKeys = new List<string>();
        
        foreach (var kvp in cache)
        {
            if (kvp.Value.IsExpired)
            {
                expiredKeys.Add(kvp.Key);
            }
        }
        
        foreach (var key in expiredKeys)
        {
            Remove(key);
        }
        
        if (expiredKeys.Count > 0)
        {
            Debug.Log($"[APICache] Removed {expiredKeys.Count} expired entries");
        }
    }
    
    private void RemoveLeastRecentlyUsed()
    {
        string lruKey = null;
        DateTime oldestAccess = DateTime.MaxValue;
        
        foreach (var kvp in cache)
        {
            if (kvp.Value.lastAccessed < oldestAccess)
            {
                oldestAccess = kvp.Value.lastAccessed;
                lruKey = kvp.Key;
            }
        }
        
        if (lruKey != null)
        {
            Debug.Log($"[APICache] Removing LRU entry: {lruKey}");
            Remove(lruKey);
        }
    }
    
    private float CalculateResponseSize(APIManager.APIResponse response)
    {
        float size = 0f;
        
        if (!string.IsNullOrEmpty(response.data))
        {
            size += System.Text.Encoding.UTF8.GetByteCount(response.data);
        }
        
        if (response.headers != null)
        {
            foreach (var header in response.headers)
            {
                size += System.Text.Encoding.UTF8.GetByteCount(header.Key);
                size += System.Text.Encoding.UTF8.GetByteCount(header.Value);
            }
        }
        
        return size;
    }
    
    public CacheStats GetStats()
    {
        CleanupExpired(); // Clean up before calculating stats
        
        return new CacheStats
        {
            entryCount = cache.Count,
            totalSize = currentCacheSize,
            maxSize = maxCacheSize,
            utilizationPercentage = (currentCacheSize / maxCacheSize) * 100f
        };
    }
    
    public class CacheStats
    {
        public int entryCount;
        public float totalSize;
        public float maxSize;
        public float utilizationPercentage;
        
        public override string ToString()
        {
            return $"Cache: {entryCount} entries, {totalSize:F1}/{maxSize:F1} bytes ({utilizationPercentage:F1}%)";
        }
    }
}
```

### Game-Specific API Service
```csharp
// Scripts/Services/GameAPIService.cs
using System;
using System.Collections.Generic;
using UnityEngine;

public class GameAPIService : MonoBehaviour
{
    [Header("Game API Configuration")]
    [SerializeField] private bool enableAnalytics = true;
    [SerializeField] private float leaderboardCacheTime = 60f;
    [SerializeField] private float playerDataCacheTime = 300f;
    
    public static GameAPIService Instance { get; private set; }
    
    // Events
    public System.Action<PlayerProfile> OnPlayerProfileUpdated;
    public System.Action<List<LeaderboardEntry>> OnLeaderboardUpdated;
    public System.Action<List<Achievement>> OnAchievementsUpdated;
    
    [Serializable]
    public class PlayerProfile
    {
        public string playerId;
        public string username;
        public string email;
        public int level;
        public long experience;
        public int coins;
        public int gems;
        public List<string> unlockedItems;
        public Dictionary<string, object> customData;
        public DateTime lastLoginTime;
        public DateTime createdTime;
    }
    
    [Serializable]
    public class LeaderboardEntry
    {
        public int rank;
        public string playerId;
        public string username;
        public long score;
        public string additionalData;
        public DateTime timestamp;
    }
    
    [Serializable]
    public class Achievement
    {
        public string achievementId;
        public string name;
        public string description;
        public bool isUnlocked;
        public float progress;
        public int rewardCoins;
        public int rewardExperience;
        public DateTime unlockedTime;
    }
    
    [Serializable]
    public class GameSession
    {
        public string sessionId;
        public DateTime startTime;
        public DateTime endTime;
        public int score;
        public int duration;
        public string gameMode;
        public Dictionary<string, object> sessionData;
    }
    
    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    // Player Profile Management
    public void GetPlayerProfile(System.Action<PlayerProfile> onSuccess, System.Action<string> onError = null)
    {
        if (!AuthenticationManager.Instance.IsAuthenticated)
        {
            onError?.Invoke("Player not authenticated");
            return;
        }
        
        string endpoint = $"/players/{AuthenticationManager.Instance.CurrentUserId}";
        
        APIManager.Instance.GET<PlayerProfile>(
            endpoint,
            (profile) =>
            {
                OnPlayerProfileUpdated?.Invoke(profile);
                onSuccess?.Invoke(profile);
            },
            (error) => onError?.Invoke(error.message),
            useCache: true,
            cacheExpiry: playerDataCacheTime
        );
    }
    
    public void UpdatePlayerProfile(PlayerProfile profile, System.Action<PlayerProfile> onSuccess, 
        System.Action<string> onError = null)
    {
        string endpoint = $"/players/{profile.playerId}";
        
        APIManager.Instance.PUT<PlayerProfile>(
            endpoint,
            profile,
            (updatedProfile) =>
            {
                OnPlayerProfileUpdated?.Invoke(updatedProfile);
                onSuccess?.Invoke(updatedProfile);
                
                // Clear related cache entries
                ClearPlayerCache(profile.playerId);
            },
            (error) => onError?.Invoke(error.message)
        );
    }
    
    // Currency Management
    public void AddCurrency(string currencyType, int amount, string source, 
        System.Action<PlayerProfile> onSuccess, System.Action<string> onError = null)
    {
        var request = new
        {
            currencyType = currencyType,
            amount = amount,
            source = source,
            timestamp = DateTime.UtcNow
        };
        
        string endpoint = $"/players/{AuthenticationManager.Instance.CurrentUserId}/currency";
        
        APIManager.Instance.POST<PlayerProfile>(
            endpoint,
            request,
            (profile) =>
            {
                OnPlayerProfileUpdated?.Invoke(profile);
                onSuccess?.Invoke(profile);
                ClearPlayerCache(profile.playerId);
            },
            (error) => onError?.Invoke(error.message)
        );
    }
    
    public void SpendCurrency(string currencyType, int amount, string reason,
        System.Action<PlayerProfile> onSuccess, System.Action<string> onError = null)
    {
        var request = new
        {
            currencyType = currencyType,
            amount = -amount, // Negative for spending
            source = $"spend_{reason}",
            timestamp = DateTime.UtcNow
        };
        
        string endpoint = $"/players/{AuthenticationManager.Instance.CurrentUserId}/currency";
        
        APIManager.Instance.POST<PlayerProfile>(
            endpoint,
            request,
            (profile) =>
            {
                OnPlayerProfileUpdated?.Invoke(profile);
                onSuccess?.Invoke(profile);
                ClearPlayerCache(profile.playerId);
            },
            (error) => onError?.Invoke(error.message)
        );
    }
    
    // Leaderboard Management
    public void GetLeaderboard(string leaderboardId, int limit = 100, 
        System.Action<List<LeaderboardEntry>> onSuccess = null, System.Action<string> onError = null)
    {
        string endpoint = $"/leaderboards/{leaderboardId}?limit={limit}";
        
        APIManager.Instance.GET<LeaderboardResponse>(
            endpoint,
            (response) =>
            {
                OnLeaderboardUpdated?.Invoke(response.entries);
                onSuccess?.Invoke(response.entries);
            },
            (error) => onError?.Invoke(error.message),
            useCache: true,
            cacheExpiry: leaderboardCacheTime
        );
    }
    
    public void SubmitScore(string leaderboardId, long score, string additionalData = null,
        System.Action<LeaderboardEntry> onSuccess = null, System.Action<string> onError = null)
    {
        var request = new
        {
            playerId = AuthenticationManager.Instance.CurrentUserId,
            score = score,
            additionalData = additionalData,
            timestamp = DateTime.UtcNow
        };
        
        string endpoint = $"/leaderboards/{leaderboardId}/scores";
        
        APIManager.Instance.POST<LeaderboardEntry>(
            endpoint,
            request,
            (entry) =>
            {
                onSuccess?.Invoke(entry);
                
                // Clear leaderboard cache to show updated rankings
                ClearLeaderboardCache(leaderboardId);
            },
            (error) => onError?.Invoke(error.message)
        );
    }
    
    // Achievement Management
    public void GetAchievements(System.Action<List<Achievement>> onSuccess = null, 
        System.Action<string> onError = null)
    {
        string endpoint = $"/players/{AuthenticationManager.Instance.CurrentUserId}/achievements";
        
        APIManager.Instance.GET<AchievementResponse>(
            endpoint,
            (response) =>
            {
                OnAchievementsUpdated?.Invoke(response.achievements);
                onSuccess?.Invoke(response.achievements);
            },
            (error) => onError?.Invoke(error.message),
            useCache: true,
            cacheExpiry: playerDataCacheTime
        );
    }
    
    public void UnlockAchievement(string achievementId, System.Action<Achievement> onSuccess = null,
        System.Action<string> onError = null)
    {
        var request = new
        {
            achievementId = achievementId,
            timestamp = DateTime.UtcNow
        };
        
        string endpoint = $"/players/{AuthenticationManager.Instance.CurrentUserId}/achievements/unlock";
        
        APIManager.Instance.POST<Achievement>(
            endpoint,
            request,
            (achievement) =>
            {
                onSuccess?.Invoke(achievement);
                ClearPlayerCache(AuthenticationManager.Instance.CurrentUserId);
            },
            (error) => onError?.Invoke(error.message)
        );
    }
    
    // Game Session Management
    public void StartGameSession(string gameMode, System.Action<GameSession> onSuccess = null,
        System.Action<string> onError = null)
    {
        var request = new
        {
            playerId = AuthenticationManager.Instance.CurrentUserId,
            gameMode = gameMode,
            startTime = DateTime.UtcNow,
            platform = Application.platform.ToString(),
            version = Application.version
        };
        
        string endpoint = "/sessions/start";
        
        APIManager.Instance.POST<GameSession>(
            endpoint,
            request,
            onSuccess,
            (error) => onError?.Invoke(error.message)
        );
    }
    
    public void EndGameSession(string sessionId, int score, Dictionary<string, object> sessionData = null,
        System.Action<GameSession> onSuccess = null, System.Action<string> onError = null)
    {
        var request = new
        {
            sessionId = sessionId,
            endTime = DateTime.UtcNow,
            score = score,
            sessionData = sessionData ?? new Dictionary<string, object>()
        };
        
        string endpoint = "/sessions/end";
        
        APIManager.Instance.POST<GameSession>(
            endpoint,
            request,
            onSuccess,
            (error) => onError?.Invoke(error.message)
        );
    }
    
    // Analytics
    public void TrackEvent(string eventName, Dictionary<string, object> parameters = null)
    {
        if (!enableAnalytics) return;
        
        var eventData = new
        {
            eventName = eventName,
            playerId = AuthenticationManager.Instance.CurrentUserId,
            parameters = parameters ?? new Dictionary<string, object>(),
            timestamp = DateTime.UtcNow,
            platform = Application.platform.ToString(),
            version = Application.version
        };
        
        APIManager.Instance.POST<object>(
            "/analytics/events",
            eventData,
            (_) => { }, // Success callback (we don't need to handle response)
            (error) => Debug.LogWarning($"Analytics event failed: {error.message}")
        );
    }
    
    // Cache management
    private void ClearPlayerCache(string playerId)
    {
        // This would clear specific cache entries related to the player
        // Implementation depends on your cache key strategy
    }
    
    private void ClearLeaderboardCache(string leaderboardId)
    {
        // Clear leaderboard-specific cache entries
    }
    
    // Response wrapper classes
    [Serializable]
    private class LeaderboardResponse
    {
        public List<LeaderboardEntry> entries;
        public int totalCount;
        public DateTime lastUpdated;
    }
    
    [Serializable]
    private class AchievementResponse
    {
        public List<Achievement> achievements;
        public int totalUnlocked;
        public int totalAvailable;
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### API Integration Code Generator
```
PROMPT TEMPLATE - REST API Client Generation:

"Generate a complete Unity REST API client for this API specification:

API Documentation:
```
[PASTE YOUR API DOCUMENTATION OR OPENAPI SPEC]
```

Requirements:
- Unity Version: [2022.3 LTS/2023.2/etc.]
- Authentication: [JWT/API Key/OAuth/etc.]
- Platform Targets: [Mobile/PC/WebGL/etc.]
- Caching Strategy: [Simple/Advanced/None]

Generate:
1. Complete API client with all endpoints
2. Data models with proper serialization
3. Error handling and retry logic
4. Authentication integration
5. Caching implementation
6. Usage examples and documentation
7. Unit tests for API methods
8. Performance optimization suggestions"
```

### API Error Handling Strategy
```
PROMPT TEMPLATE - Error Handling Design:

"Design a comprehensive error handling strategy for Unity REST API integration:

API Characteristics:
- Type: [Game Backend/Third-party Service/Multiple APIs]
- Reliability: [High/Medium/Low]
- Expected Error Rates: [<1%/1-5%/5%+]
- User Experience Priority: [Seamless/Informative/Performance]

Create strategy including:
1. Error categorization and severity levels
2. Retry logic with exponential backoff
3. Circuit breaker pattern implementation
4. User-friendly error message mapping
5. Offline mode and graceful degradation
6. Logging and monitoring integration
7. Recovery mechanisms and fallbacks
8. Performance impact considerations"
```

## 💡 Key REST API Integration Principles

### Essential API Integration Checklist
- **Proper error handling** - Handle network errors, timeouts, and API errors gracefully
- **Authentication management** - Secure token storage and automatic refresh
- **Request optimization** - Use caching, compression, and request batching
- **Offline support** - Graceful degradation when network is unavailable
- **Security best practices** - Validate responses and protect sensitive data
- **Performance monitoring** - Track request times and success rates
- **User experience** - Provide loading states and meaningful error messages
- **Testing strategy** - Comprehensive testing including edge cases

### Common Unity API Integration Challenges
1. **Coroutine complexity** - Managing async operations and UI updates
2. **Error handling** - Distinguishing between network and application errors
3. **Authentication flow** - Token refresh and re-authentication
4. **Data serialization** - JSON parsing and type safety
5. **Platform differences** - Network behavior across platforms
6. **Performance impact** - API calls affecting frame rate
7. **Offline scenarios** - Handling network connectivity issues
8. **Security concerns** - Protecting API keys and user data

This comprehensive REST API integration system provides Unity developers with production-ready networking capabilities, ensuring reliable communication with backend services while maintaining excellent user experience and security standards.