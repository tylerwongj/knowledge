# @a-RESTful-API-Design-Unity

## 🎯 Learning Objectives
- Design and implement RESTful APIs for Unity game backends
- Master HTTP methods, status codes, and API versioning strategies
- Create scalable API architectures for multiplayer games
- Implement proper error handling and response formatting

## 🔧 RESTful API Fundamentals

### Unity HTTP Client Implementation
```csharp
// Unity REST API Client
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;
using Newtonsoft.Json;

public class GameAPIClient : MonoBehaviour
{
    [Header("API Configuration")]
    [SerializeField] private string baseUrl = "https://api.yourgame.com/v1";
    [SerializeField] private string apiKey = "your-api-key-here";
    [SerializeField] private int timeoutSeconds = 30;
    
    private Dictionary<string, string> defaultHeaders;
    
    void Start()
    {
        InitializeHeaders();
    }
    
    private void InitializeHeaders()
    {
        defaultHeaders = new Dictionary<string, string>
        {
            { "Content-Type", "application/json" },
            { "Accept", "application/json" },
            { "X-API-Key", apiKey },
            { "User-Agent", $"UnityGame/{Application.version}" }
        };
    }
    
    // Generic GET request
    public async Task<APIResponse<T>> GetAsync<T>(string endpoint, Dictionary<string, string> parameters = null)
    {
        var url = BuildUrl(endpoint, parameters);
        
        using (var request = UnityWebRequest.Get(url))
        {
            AddHeaders(request);
            request.timeout = timeoutSeconds;
            
            var operation = request.SendWebRequest();
            
            // Wait for completion with progress tracking
            while (!operation.isDone)
            {
                await Task.Yield();
            }
            
            return ProcessResponse<T>(request);
        }
    }
    
    // Generic POST request
    public async Task<APIResponse<T>> PostAsync<T>(string endpoint, object data)
    {
        var url = $"{baseUrl}/{endpoint.TrimStart('/')}";
        var jsonData = JsonConvert.SerializeObject(data);
        
        using (var request = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyData = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyData);
            request.downloadHandler = new DownloadHandlerBuffer();
            
            AddHeaders(request);
            request.timeout = timeoutSeconds;
            
            var operation = request.SendWebRequest();
            while (!operation.isDone)
            {
                await Task.Yield();
            }
            
            return ProcessResponse<T>(request);
        }
    }
    
    // Generic PUT request
    public async Task<APIResponse<T>> PutAsync<T>(string endpoint, object data)
    {
        var url = $"{baseUrl}/{endpoint.TrimStart('/')}";
        var jsonData = JsonConvert.SerializeObject(data);
        
        using (var request = new UnityWebRequest(url, "PUT"))
        {
            byte[] bodyData = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyData);
            request.downloadHandler = new DownloadHandlerBuffer();
            
            AddHeaders(request);
            request.timeout = timeoutSeconds;
            
            var operation = request.SendWebRequest();
            while (!operation.isDone)
            {
                await Task.Yield();
            }
            
            return ProcessResponse<T>(request);
        }
    }
    
    // Generic DELETE request
    public async Task<APIResponse<bool>> DeleteAsync(string endpoint)
    {
        var url = $"{baseUrl}/{endpoint.TrimStart('/')}";
        
        using (var request = UnityWebRequest.Delete(url))
        {
            AddHeaders(request);
            request.timeout = timeoutSeconds;
            
            var operation = request.SendWebRequest();
            while (!operation.isDone)
            {
                await Task.Yield();
            }
            
            var response = new APIResponse<bool>
            {
                StatusCode = (int)request.responseCode,
                Success = request.responseCode >= 200 && request.responseCode < 300,
                Data = request.responseCode >= 200 && request.responseCode < 300
            };
            
            if (!response.Success)
            {
                response.ErrorMessage = request.error ?? "Delete request failed";
            }
            
            return response;
        }
    }
    
    private void AddHeaders(UnityWebRequest request)
    {
        foreach (var header in defaultHeaders)
        {
            request.SetRequestHeader(header.Key, header.Value);
        }
        
        // Add authentication token if available
        var authToken = PlayerPrefs.GetString("auth_token", "");
        if (!string.IsNullOrEmpty(authToken))
        {
            request.SetRequestHeader("Authorization", $"Bearer {authToken}");
        }
    }
    
    private APIResponse<T> ProcessResponse<T>(UnityWebRequest request)
    {
        var response = new APIResponse<T>
        {
            StatusCode = (int)request.responseCode,
            Success = request.result == UnityWebRequest.Result.Success
        };
        
        if (response.Success)
        {
            try
            {
                var responseText = request.downloadHandler.text;
                response.Data = JsonConvert.DeserializeObject<T>(responseText);
            }
            catch (JsonException ex)
            {
                response.Success = false;
                response.ErrorMessage = $"JSON parsing error: {ex.Message}";
            }
        }
        else
        {
            response.ErrorMessage = request.error ?? "Request failed";
            
            // Try to parse error response
            if (!string.IsNullOrEmpty(request.downloadHandler.text))
            {
                try
                {
                    var errorResponse = JsonConvert.DeserializeObject<APIErrorResponse>(request.downloadHandler.text);
                    response.ErrorMessage = errorResponse.Message;
                    response.ErrorCode = errorResponse.Code;
                }
                catch
                {
                    // Use default error message if parsing fails
                }
            }
        }
        
        return response;
    }
    
    private string BuildUrl(string endpoint, Dictionary<string, string> parameters)
    {
        var url = $"{baseUrl}/{endpoint.TrimStart('/')}";
        
        if (parameters != null && parameters.Count > 0)
        {
            var queryParams = string.Join("&", 
                parameters.Select(kvp => $"{UnityWebRequest.EscapeURL(kvp.Key)}={UnityWebRequest.EscapeURL(kvp.Value)}"));
            url += $"?{queryParams}";
        }
        
        return url;
    }
}
```

### Game-Specific API Endpoints
```csharp
// Player Management API Service
public class PlayerAPIService : MonoBehaviour
{
    private GameAPIClient apiClient;
    
    void Start()
    {
        apiClient = GetComponent<GameAPIClient>();
    }
    
    // GET /players/{playerId}
    public async Task<APIResponse<Player>> GetPlayerAsync(string playerId)
    {
        return await apiClient.GetAsync<Player>($"players/{playerId}");
    }
    
    // GET /players/{playerId}/stats
    public async Task<APIResponse<PlayerStats>> GetPlayerStatsAsync(string playerId)
    {
        return await apiClient.GetAsync<PlayerStats>($"players/{playerId}/stats");
    }
    
    // PUT /players/{playerId}/stats
    public async Task<APIResponse<PlayerStats>> UpdatePlayerStatsAsync(string playerId, PlayerStatsUpdate update)
    {
        return await apiClient.PutAsync<PlayerStats>($"players/{playerId}/stats", update);
    }
    
    // GET /players/{playerId}/inventory
    public async Task<APIResponse<List<InventoryItem>>> GetPlayerInventoryAsync(string playerId)
    {
        return await apiClient.GetAsync<List<InventoryItem>>($"players/{playerId}/inventory");
    }
    
    // POST /players/{playerId}/inventory/items
    public async Task<APIResponse<InventoryItem>> AddInventoryItemAsync(string playerId, AddItemRequest request)
    {
        return await apiClient.PostAsync<InventoryItem>($"players/{playerId}/inventory/items", request);
    }
    
    // DELETE /players/{playerId}/inventory/items/{itemId}
    public async Task<APIResponse<bool>> RemoveInventoryItemAsync(string playerId, string itemId)
    {
        return await apiClient.DeleteAsync($"players/{playerId}/inventory/items/{itemId}");
    }
    
    // GET /leaderboards/{leaderboardId}
    public async Task<APIResponse<Leaderboard>> GetLeaderboardAsync(string leaderboardId, int limit = 100, int offset = 0)
    {
        var parameters = new Dictionary<string, string>
        {
            { "limit", limit.ToString() },
            { "offset", offset.ToString() }
        };
        
        return await apiClient.GetAsync<Leaderboard>($"leaderboards/{leaderboardId}", parameters);
    }
    
    // POST /players/{playerId}/scores
    public async Task<APIResponse<ScoreSubmissionResult>> SubmitScoreAsync(string playerId, ScoreSubmission score)
    {
        return await apiClient.PostAsync<ScoreSubmissionResult>($"players/{playerId}/scores", score);
    }
    
    // GET /achievements
    public async Task<APIResponse<List<Achievement>>> GetAchievementsAsync()
    {
        return await apiClient.GetAsync<List<Achievement>>("achievements");
    }
    
    // POST /players/{playerId}/achievements/{achievementId}/unlock
    public async Task<APIResponse<AchievementUnlockResult>> UnlockAchievementAsync(string playerId, string achievementId)
    {
        return await apiClient.PostAsync<AchievementUnlockResult>(
            $"players/{playerId}/achievements/{achievementId}/unlock", 
            new { timestamp = DateTime.UtcNow });
    }
}
```

## 🔧 API Response Handling and Error Management

### Comprehensive Error Handling
```csharp
// API Response Models
[System.Serializable]
public class APIResponse<T>
{
    public bool Success { get; set; }
    public int StatusCode { get; set; }
    public T Data { get; set; }
    public string ErrorMessage { get; set; }
    public string ErrorCode { get; set; }
    public Dictionary<string, object> Metadata { get; set; }
}

[System.Serializable]
public class APIErrorResponse
{
    public string Message { get; set; }
    public string Code { get; set; }
    public Dictionary<string, string> Details { get; set; }
    public string TraceId { get; set; }
    public DateTime Timestamp { get; set; }
}

// Error Handling Service
public class APIErrorHandler : MonoBehaviour
{
    [Header("Error Handling Settings")]
    [SerializeField] private bool showErrorMessages = true;
    [SerializeField] private bool logErrorsToAnalytics = true;
    [SerializeField] private int maxRetryAttempts = 3;
    
    public void HandleAPIError<T>(APIResponse<T> response, string operation)
    {
        if (response.Success)
            return;
            
        var errorInfo = new APIErrorInfo
        {
            Operation = operation,
            StatusCode = response.StatusCode,
            ErrorMessage = response.ErrorMessage,
            ErrorCode = response.ErrorCode,
            Timestamp = DateTime.UtcNow
        };
        
        // Log error
        Debug.LogError($"API Error [{response.StatusCode}]: {response.ErrorMessage} (Operation: {operation})");
        
        // Handle specific error types
        switch (response.StatusCode)
        {
            case 400: // Bad Request
                HandleBadRequestError(errorInfo);
                break;
            case 401: // Unauthorized
                HandleUnauthorizedError(errorInfo);
                break;
            case 403: // Forbidden
                HandleForbiddenError(errorInfo);
                break;
            case 404: // Not Found
                HandleNotFoundError(errorInfo);
                break;
            case 429: // Too Many Requests
                HandleRateLimitError(errorInfo);
                break;
            case 500: // Internal Server Error
            case 502: // Bad Gateway
            case 503: // Service Unavailable
                HandleServerError(errorInfo);
                break;
            default:
                HandleGenericError(errorInfo);
                break;
        }
        
        // Send to analytics if enabled
        if (logErrorsToAnalytics)
        {
            AnalyticsManager.Instance.TrackAPIError(errorInfo);
        }
    }
    
    private void HandleUnauthorizedError(APIErrorInfo errorInfo)
    {
        // Token expired or invalid
        if (showErrorMessages)
        {
            UIManager.Instance.ShowMessage("Session expired. Please log in again.", MessageType.Warning);
        }
        
        // Redirect to login
        GameManager.Instance.ReturnToLogin();
    }
    
    private void HandleRateLimitError(APIErrorInfo errorInfo)
    {
        if (showErrorMessages)
        {
            UIManager.Instance.ShowMessage("Too many requests. Please wait before trying again.", MessageType.Warning);
        }
        
        // Implement exponential backoff
        StartCoroutine(DelayedRetry(errorInfo.Operation, CalculateRetryDelay(errorInfo.StatusCode)));
    }
    
    private void HandleServerError(APIErrorInfo errorInfo)
    {
        if (showErrorMessages)
        {
            UIManager.Instance.ShowMessage("Server temporarily unavailable. Please try again later.", MessageType.Error);
        }
        
        // Implement retry logic for server errors
        if (CanRetry(errorInfo.Operation))
        {
            StartCoroutine(DelayedRetry(errorInfo.Operation, CalculateRetryDelay(errorInfo.StatusCode)));
        }
    }
    
    private IEnumerator DelayedRetry(string operation, float delay)
    {
        yield return new WaitForSeconds(delay);
        
        // Implement operation retry logic here
        switch (operation)
        {
            case "GetPlayerStats":
                // Retry getting player stats
                break;
            case "SubmitScore":
                // Retry score submission
                break;
            // Add more retry cases as needed
        }
    }
    
    private float CalculateRetryDelay(int statusCode)
    {
        return statusCode switch
        {
            429 => 60f, // Rate limit - wait 1 minute
            500 => 5f,  // Server error - wait 5 seconds
            502 => 10f, // Bad gateway - wait 10 seconds
            503 => 30f, // Service unavailable - wait 30 seconds
            _ => 2f     // Default - wait 2 seconds
        };
    }
}
```

### API Caching and Offline Support
```csharp
// API Response Cache Manager
public class APICacheManager : MonoBehaviour
{
    [Header("Cache Settings")]
    [SerializeField] private int maxCacheSize = 100;
    [SerializeField] private int defaultCacheDurationMinutes = 15;
    
    private Dictionary<string, CachedAPIResponse> responseCache;
    private Queue<string> cacheKeys; // For LRU eviction
    
    void Start()
    {
        responseCache = new Dictionary<string, CachedAPIResponse>();
        cacheKeys = new Queue<string>();
    }
    
    public bool TryGetCachedResponse<T>(string cacheKey, out T data)
    {
        data = default(T);
        
        if (!responseCache.ContainsKey(cacheKey))
            return false;
            
        var cachedResponse = responseCache[cacheKey];
        
        // Check if cache is expired
        if (DateTime.UtcNow > cachedResponse.ExpirationTime)
        {
            RemoveFromCache(cacheKey);
            return false;
        }
        
        try
        {
            data = JsonConvert.DeserializeObject<T>(cachedResponse.ResponseData);
            
            // Update access time for LRU
            cachedResponse.LastAccessTime = DateTime.UtcNow;
            
            return true;
        }
        catch (JsonException)
        {
            RemoveFromCache(cacheKey);
            return false;
        }
    }
    
    public void CacheResponse<T>(string cacheKey, T data, int cacheDurationMinutes = -1)
    {
        if (cacheDurationMinutes == -1)
            cacheDurationMinutes = defaultCacheDurationMinutes;
            
        var serializedData = JsonConvert.SerializeObject(data);
        var cachedResponse = new CachedAPIResponse
        {
            CacheKey = cacheKey,
            ResponseData = serializedData,
            CacheTime = DateTime.UtcNow,
            ExpirationTime = DateTime.UtcNow.AddMinutes(cacheDurationMinutes),
            LastAccessTime = DateTime.UtcNow
        };
        
        // Add to cache
        responseCache[cacheKey] = cachedResponse;
        cacheKeys.Enqueue(cacheKey);
        
        // Enforce cache size limit
        while (responseCache.Count > maxCacheSize)
        {
            var oldestKey = cacheKeys.Dequeue();
            RemoveFromCache(oldestKey);
        }
    }
    
    public async Task<APIResponse<T>> GetWithCacheAsync<T>(string endpoint, 
        Dictionary<string, string> parameters = null, int cacheDurationMinutes = -1)
    {
        var cacheKey = GenerateCacheKey(endpoint, parameters);
        
        // Try cache first
        if (TryGetCachedResponse<T>(cacheKey, out T cachedData))
        {
            return new APIResponse<T>
            {
                Success = true,
                Data = cachedData,
                StatusCode = 200
            };
        }
        
        // Make API call
        var apiClient = GetComponent<GameAPIClient>();
        var response = await apiClient.GetAsync<T>(endpoint, parameters);
        
        // Cache successful responses
        if (response.Success)
        {
            CacheResponse(cacheKey, response.Data, cacheDurationMinutes);
        }
        
        return response;
    }
    
    private string GenerateCacheKey(string endpoint, Dictionary<string, string> parameters)
    {
        var keyBuilder = new System.Text.StringBuilder(endpoint);
        
        if (parameters != null && parameters.Count > 0)
        {
            keyBuilder.Append("?");
            keyBuilder.Append(string.Join("&", 
                parameters.OrderBy(kvp => kvp.Key)
                .Select(kvp => $"{kvp.Key}={kvp.Value}")));
        }
        
        return keyBuilder.ToString();
    }
    
    private void RemoveFromCache(string cacheKey)
    {
        responseCache.Remove(cacheKey);
    }
    
    public void ClearCache()
    {
        responseCache.Clear();
        cacheKeys.Clear();
    }
    
    public void ClearExpiredCache()
    {
        var now = DateTime.UtcNow;
        var expiredKeys = responseCache
            .Where(kvp => now > kvp.Value.ExpirationTime)
            .Select(kvp => kvp.Key)
            .ToList();
            
        foreach (var key in expiredKeys)
        {
            RemoveFromCache(key);
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### API Documentation Generation
```
Prompt: "Generate comprehensive OpenAPI/Swagger documentation for a Unity game REST API including player management, inventory system, leaderboards, achievements, and matchmaking endpoints with request/response examples."
```

### API Testing Suite Creation
```
Prompt: "Create a complete Unity automated testing suite for REST API endpoints including unit tests, integration tests, and performance tests with mock data generation and error scenario coverage."
```

### API Client Code Generation
```
Prompt: "Generate a type-safe Unity C# API client library from this OpenAPI specification with automatic serialization, error handling, retries, and caching: [paste OpenAPI spec]"
```

## 💡 Key Highlights

### RESTful API Design Principles
- **Resource-based URLs**: Use nouns, not verbs (e.g., `/players/{id}` not `/getPlayer`)
- **HTTP methods mapping**: GET (read), POST (create), PUT (update), DELETE (remove)
- **Stateless operations**: Each request contains all necessary information
- **Consistent response format**: Standardized JSON structure across endpoints
- **Proper status codes**: Use appropriate HTTP status codes for different scenarios

### Unity-Specific Considerations
- **Async/await patterns**: Non-blocking API calls to prevent frame drops
- **Coroutine integration**: Alternative async pattern for older Unity versions
- **Error handling**: Graceful degradation when API is unavailable
- **Offline support**: Cache frequently accessed data for offline play
- **Performance optimization**: Request batching and response compression

### API Security and Performance
- **Authentication**: Bearer token or API key authentication
- **Rate limiting**: Prevent abuse with request throttling
- **Input validation**: Validate all incoming data server-side
- **Response caching**: Reduce server load and improve response times
- **Pagination**: Handle large datasets efficiently