# @d-Unity-API-Integration-Patterns - Game API Development

## 🎯 Learning Objectives
- Master RESTful API integration patterns in Unity C#
- Implement secure authentication and authorization systems
- Build efficient API communication with proper error handling
- Create AI-enhanced API testing and optimization workflows

---

## 🔧 Unity API Integration System

### Comprehensive API Client Manager

```csharp
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using Newtonsoft.Json;
using System;
using System.Threading.Tasks;

/// <summary>
/// Advanced API integration system for Unity games
/// Supports REST, GraphQL, WebSocket connections with authentication
/// </summary>
public class GameAPIManager : MonoBehaviour
{
    [System.Serializable]
    public class APIConfiguration
    {
        public string baseURL = "https://api.yourgame.com";
        public string apiVersion = "v1";
        public int timeoutSeconds = 30;
        public int maxRetryAttempts = 3;
        public bool enableCaching = true;
        public bool enableRateLimiting = true;
        public int requestsPerMinute = 60;
    }
    
    [Header("API Configuration")]
    [SerializeField] private APIConfiguration config = new APIConfiguration();
    
    // Authentication
    private string authToken;
    private DateTime tokenExpiry;
    private bool isAuthenticated = false;
    
    // Request management
    private Queue<APIRequest> requestQueue = new Queue<APIRequest>();
    private Dictionary<string, object> responseCache = new Dictionary<string, object>();
    private Dictionary<string, DateTime> rateLimitTracker = new Dictionary<string, DateTime>();
    
    void Awake()
    {
        DontDestroyOnLoad(gameObject);
        StartCoroutine(ProcessRequestQueue());
    }
    
    // Authentication Methods
    public async Task<bool> AuthenticateAsync(string username, string password)
    {
        var loginData = new LoginRequest
        {
            username = username,
            password = password,
            deviceId = SystemInfo.deviceUniqueIdentifier
        };
        
        try
        {
            var response = await PostAsync<AuthResponse>("/auth/login", loginData, false);
            if (response != null && response.success)
            {
                authToken = response.token;
                tokenExpiry = DateTime.Now.AddSeconds(response.expiresIn);
                isAuthenticated = true;
                
                Debug.Log("Authentication successful");
                return true;
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"Authentication failed: {e.Message}");
        }
        
        return false;
    }
    
    public async Task<bool> RefreshTokenAsync()
    {
        if (string.IsNullOrEmpty(authToken))
            return false;
        
        try
        {
            var refreshData = new RefreshTokenRequest { token = authToken };
            var response = await PostAsync<AuthResponse>("/auth/refresh", refreshData, false);
            
            if (response != null && response.success)
            {
                authToken = response.token;
                tokenExpiry = DateTime.Now.AddSeconds(response.expiresIn);
                return true;
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"Token refresh failed: {e.Message}");
        }
        
        isAuthenticated = false;
        return false;
    }
    
    // HTTP Methods
    public async Task<T> GetAsync<T>(string endpoint, bool requireAuth = true) where T : class
    {
        return await SendRequestAsync<T>("GET", endpoint, null, requireAuth);
    }
    
    public async Task<T> PostAsync<T>(string endpoint, object data, bool requireAuth = true) where T : class
    {
        return await SendRequestAsync<T>("POST", endpoint, data, requireAuth);
    }
    
    public async Task<T> PutAsync<T>(string endpoint, object data, bool requireAuth = true) where T : class
    {
        return await SendRequestAsync<T>("PUT", endpoint, data, requireAuth);
    }
    
    public async Task<bool> DeleteAsync(string endpoint, bool requireAuth = true)
    {
        var response = await SendRequestAsync<APIResponse>("DELETE", endpoint, null, requireAuth);
        return response?.success ?? false;
    }
    
    private async Task<T> SendRequestAsync<T>(string method, string endpoint, object data, bool requireAuth) where T : class
    {
        // Check authentication
        if (requireAuth && !await EnsureAuthenticated())
        {
            Debug.LogError("Request failed: Not authenticated");
            return null;
        }
        
        // Check rate limiting
        if (!CheckRateLimit())
        {
            Debug.LogWarning("Request rate limited");
            return null;
        }
        
        // Check cache for GET requests
        if (method == "GET" && config.enableCaching)
        {
            var cacheKey = $"{endpoint}";
            if (responseCache.ContainsKey(cacheKey))
            {
                var cachedResponse = responseCache[cacheKey] as CachedResponse<T>;
                if (cachedResponse != null && !cachedResponse.IsExpired())
                {
                    return cachedResponse.data;
                }
            }
        }
        
        // Prepare request
        var url = $"{config.baseURL}/{config.apiVersion}{endpoint}";
        UnityWebRequest request = null;
        
        switch (method)
        {
            case "GET":
                request = UnityWebRequest.Get(url);
                break;
            case "POST":
                request = CreatePostRequest(url, data);
                break;
            case "PUT":
                request = CreatePutRequest(url, data);
                break;
            case "DELETE":
                request = UnityWebRequest.Delete(url);
                break;
        }
        
        // Set headers
        SetRequestHeaders(request, requireAuth);
        
        // Send request with retry logic
        var response = await SendRequestWithRetry<T>(request, method, endpoint);
        
        // Cache GET responses
        if (method == "GET" && config.enableCaching && response != null)
        {
            var cacheKey = $"{endpoint}";
            responseCache[cacheKey] = new CachedResponse<T>
            {
                data = response,
                timestamp = DateTime.Now,
                ttlMinutes = 5
            };
        }
        
        return response;
    }
    
    private async Task<T> SendRequestWithRetry<T>(UnityWebRequest request, string method, string endpoint) where T : class
    {
        Exception lastException = null;
        
        for (int attempt = 0; attempt <= config.maxRetryAttempts; attempt++)
        {
            try
            {
                // Send request
                var operation = request.SendWebRequest();
                
                // Wait with timeout
                var timeoutTime = Time.time + config.timeoutSeconds;
                while (!operation.isDone && Time.time < timeoutTime)
                {
                    await Task.Yield();
                }
                
                if (!operation.isDone)
                {
                    request.Abort();
                    throw new TimeoutException("Request timed out");
                }
                
                // Handle response
                if (request.result == UnityWebRequest.Result.Success)
                {
                    var responseText = request.downloadHandler.text;
                    
                    if (typeof(T) == typeof(string))
                    {
                        return responseText as T;
                    }
                    
                    if (!string.IsNullOrEmpty(responseText))
                    {
                        return JsonConvert.DeserializeObject<T>(responseText);
                    }
                    
                    return default(T);
                }
                else
                {
                    HandleHTTPError(request, method, endpoint);
                    
                    // Don't retry client errors (4xx)
                    if (request.responseCode >= 400 && request.responseCode < 500)
                    {
                        break;
                    }
                }
            }
            catch (Exception e)
            {
                lastException = e;
                Debug.LogWarning($"Request attempt {attempt + 1} failed: {e.Message}");
            }
            
            // Wait before retry (exponential backoff)
            if (attempt < config.maxRetryAttempts)
            {
                var delay = Mathf.Pow(2, attempt) * 1000; // 1s, 2s, 4s, etc.
                await Task.Delay((int)delay);
            }
        }
        
        Debug.LogError($"Request failed after {config.maxRetryAttempts + 1} attempts. Last error: {lastException?.Message}");
        return null;
    }
    
    // Game-Specific API Methods
    public async Task<PlayerProfile> GetPlayerProfileAsync(string playerId)
    {
        return await GetAsync<PlayerProfile>($"/players/{playerId}");
    }
    
    public async Task<LeaderboardResponse> GetLeaderboardAsync(string category, int page = 1, int limit = 50)
    {
        return await GetAsync<LeaderboardResponse>($"/leaderboard/{category}?page={page}&limit={limit}");
    }
    
    public async Task<bool> SubmitScoreAsync(string playerId, string category, int score)
    {
        var scoreData = new ScoreSubmission
        {
            playerId = playerId,
            category = category,
            score = score,
            timestamp = DateTime.Now
        };
        
        var response = await PostAsync<APIResponse>("/scores/submit", scoreData);
        return response?.success ?? false;
    }
    
    public async Task<ShopItemsResponse> GetShopItemsAsync(string category = null)
    {
        var endpoint = "/shop/items";
        if (!string.IsNullOrEmpty(category))
        {
            endpoint += $"?category={category}";
        }
        
        return await GetAsync<ShopItemsResponse>(endpoint);
    }
    
    public async Task<PurchaseResponse> PurchaseItemAsync(string itemId, string paymentMethod)
    {
        var purchaseData = new PurchaseRequest
        {
            itemId = itemId,
            paymentMethod = paymentMethod,
            playerId = GetCurrentPlayerId()
        };
        
        return await PostAsync<PurchaseResponse>("/shop/purchase", purchaseData);
    }
}

// Data Transfer Objects
[System.Serializable]
public class LoginRequest
{
    public string username;
    public string password;
    public string deviceId;
}

[System.Serializable]
public class AuthResponse : APIResponse
{
    public string token;
    public int expiresIn;
    public UserProfile user;
}

[System.Serializable]
public class APIResponse
{
    public bool success;
    public string message;
    public int statusCode;
}

[System.Serializable]
public class PlayerProfile
{
    public string playerId;
    public string username;
    public int level;
    public long experience;
    public int coins;
    public DateTime lastLogin;
    public string[] achievements;
}

[System.Serializable]
public class CachedResponse<T>
{
    public T data;
    public DateTime timestamp;
    public int ttlMinutes;
    
    public bool IsExpired()
    {
        return DateTime.Now > timestamp.AddMinutes(ttlMinutes);
    }
}
```

---

## 🚀 AI/LLM Integration Opportunities

### API Testing Automation
**Comprehensive API Test Generation Prompt:**
> "Generate comprehensive API tests for this Unity game API including authentication flows, player data operations, leaderboards, and shop functionality. Include edge cases, error scenarios, and performance tests."

### Intelligent Error Handling
```csharp
public class AIAPIErrorHandler : MonoBehaviour
{
    public async Task<string> AnalyzeAPIError(UnityWebRequest request, string context)
    {
        var errorAnalysisPrompt = $@"
        Analyze this Unity API error and provide solution:
        
        HTTP Status: {request.responseCode}
        Error: {request.error}
        Response: {request.downloadHandler?.text}
        Context: {context}
        
        Provide:
        1. Root cause analysis
        2. Specific fix recommendations
        3. Prevention strategies
        4. Retry logic suggestions
        ";
        
        return await CallAIService(errorAnalysisPrompt);
    }
}
```

---

## 💡 Key API Integration Patterns

### Authentication & Security
- **JWT Tokens**: Secure authentication with automatic refresh
- **Rate Limiting**: Prevent API abuse and ensure fair usage
- **Request Signing**: HMAC signatures for sensitive operations
- **SSL/TLS**: Encrypted communication for all API calls

### Performance Optimization
- **Caching**: Smart response caching with TTL
- **Connection Pooling**: Reuse HTTP connections
- **Compression**: GZIP compression for large responses
- **Async Operations**: Non-blocking API calls in Unity

This comprehensive API system provides enterprise-grade integration capabilities for Unity games with robust error handling and AI-enhanced optimization.