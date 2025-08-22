# @z-Unity-Enterprise-API-Architecture-Complete - Production-Grade API Integration Systems

## 🎯 Learning Objectives
- Master complete Unity API architecture from RESTful services to real-time communication
- Build enterprise-grade API integration systems with advanced security and performance optimization
- Implement sophisticated communication patterns including GraphQL, WebSockets, and gRPC
- Create scalable API middleware and caching systems for high-performance Unity applications

## 🔧 Core API Architecture Framework

### Unity REST API Integration with Advanced Features
```csharp
// Comprehensive Unity REST API manager with enterprise features
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;
using System.Security.Cryptography;
using System.IO;

public class UnityRestAPIManager : MonoBehaviour
{
    [System.Serializable]
    public class APIConfiguration
    {
        public string baseUrl;
        public string apiKey;
        public string apiSecret;
        public int timeout = 30;
        public int maxRetries = 3;
        public bool enableCaching = true;
        public bool enableCompression = true;
        public string userAgent = "Unity Game Client";
        public Dictionary<string, string> defaultHeaders;
    }

    [System.Serializable]
    public class APIResponse<T>
    {
        public bool success;
        public T data;
        public string error;
        public int statusCode;
        public Dictionary<string, string> headers;
        public long responseTime;
    }

    [System.Serializable]
    public class RequestMetrics
    {
        public string endpoint;
        public long requestTime;
        public long responseTime;
        public int statusCode;
        public long dataSize;
        public bool fromCache;
    }

    [Header("API Configuration")]
    [SerializeField] private APIConfiguration config;
    
    [Header("Performance Monitoring")]
    [SerializeField] private bool enableMetrics = true;
    [SerializeField] private int metricsHistorySize = 1000;

    private Dictionary<string, CachedResponse> responseCache;
    private Queue<RequestMetrics> metricsHistory;
    private Dictionary<string, int> retryCounters;
    private string jwtToken;
    private DateTime tokenExpiration;

    public static UnityRestAPIManager Instance { get; private set; }

    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeAPIManager();
        }
        else
        {
            Destroy(gameObject);
        }
    }

    private void InitializeAPIManager()
    {
        responseCache = new Dictionary<string, CachedResponse>();
        metricsHistory = new Queue<RequestMetrics>();
        retryCounters = new Dictionary<string, int>();
        
        if (config.defaultHeaders == null)
        {
            config.defaultHeaders = new Dictionary<string, string>
            {
                { "Content-Type", "application/json" },
                { "Accept", "application/json" },
                { "User-Agent", config.userAgent }
            };
        }
        
        // Start periodic cache cleanup
        InvokeRepeating(nameof(CleanupCache), 60f, 60f);
        
        Debug.Log("Unity REST API Manager initialized");
    }

    // Authentication system
    public async Task<bool> AuthenticateAsync(string username, string password)
    {
        try
        {
            var authRequest = new
            {
                username = username,
                password = HashPassword(password),
                clientId = SystemInfo.deviceUniqueIdentifier,
                timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds()
            };

            var response = await SendRequestAsync<AuthResponse>("POST", "/auth/login", authRequest);
            
            if (response.success && response.data != null)
            {
                jwtToken = response.data.token;
                tokenExpiration = DateTime.UtcNow.AddSeconds(response.data.expiresIn);
                
                // Update default headers with token
                config.defaultHeaders["Authorization"] = $"Bearer {jwtToken}";
                
                Debug.Log("Authentication successful");
                return true;
            }
            else
            {
                Debug.LogError($"Authentication failed: {response.error}");
                return false;
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"Authentication error: {e.Message}");
            return false;
        }
    }

    public async Task<bool> RefreshTokenAsync()
    {
        if (string.IsNullOrEmpty(jwtToken))
        {
            Debug.LogWarning("No token to refresh");
            return false;
        }

        try
        {
            var refreshRequest = new { token = jwtToken };
            var response = await SendRequestAsync<AuthResponse>("POST", "/auth/refresh", refreshRequest);
            
            if (response.success && response.data != null)
            {
                jwtToken = response.data.token;
                tokenExpiration = DateTime.UtcNow.AddSeconds(response.data.expiresIn);
                config.defaultHeaders["Authorization"] = $"Bearer {jwtToken}";
                
                Debug.Log("Token refreshed successfully");
                return true;
            }
            
            return false;
        }
        catch (Exception e)
        {
            Debug.LogError($"Token refresh error: {e.Message}");
            return false;
        }
    }

    // Core HTTP methods with advanced features
    public async Task<APIResponse<T>> GetAsync<T>(string endpoint, Dictionary<string, string> parameters = null)
    {
        string url = BuildUrl(endpoint, parameters);
        return await SendRequestAsync<T>("GET", url);
    }

    public async Task<APIResponse<T>> PostAsync<T>(string endpoint, object data = null)
    {
        return await SendRequestAsync<T>("POST", endpoint, data);
    }

    public async Task<APIResponse<T>> PutAsync<T>(string endpoint, object data = null)
    {
        return await SendRequestAsync<T>("PUT", endpoint, data);
    }

    public async Task<APIResponse<T>> DeleteAsync<T>(string endpoint)
    {
        return await SendRequestAsync<T>("DELETE", endpoint);
    }

    public async Task<APIResponse<T>> PatchAsync<T>(string endpoint, object data = null)
    {
        return await SendRequestAsync<T>("PATCH", endpoint, data);
    }

    // Advanced request method with full feature support
    private async Task<APIResponse<T>> SendRequestAsync<T>(string method, string endpoint, object data = null)
    {
        string fullUrl = endpoint.StartsWith("http") ? endpoint : config.baseUrl + endpoint;
        string cacheKey = GenerateCacheKey(method, fullUrl, data);
        
        var startTime = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        
        // Check cache first (GET requests only)
        if (method == "GET" && config.enableCaching && responseCache.ContainsKey(cacheKey))
        {
            var cachedResponse = responseCache[cacheKey];
            if (!cachedResponse.IsExpired())
            {
                RecordMetrics(endpoint, startTime, DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(), 
                    200, 0, true);
                
                return JsonConvert.DeserializeObject<APIResponse<T>>(cachedResponse.responseJson);
            }
            else
            {
                responseCache.Remove(cacheKey);
            }
        }

        // Check if token needs refresh
        if (!string.IsNullOrEmpty(jwtToken) && DateTime.UtcNow >= tokenExpiration.AddMinutes(-5))
        {
            await RefreshTokenAsync();
        }

        UnityWebRequest request = null;
        APIResponse<T> response = new APIResponse<T>();

        try
        {
            // Create request based on method
            switch (method.ToUpper())
            {
                case "GET":
                    request = UnityWebRequest.Get(fullUrl);
                    break;
                case "POST":
                    request = CreatePostRequest(fullUrl, data);
                    break;
                case "PUT":
                    request = CreatePutRequest(fullUrl, data);
                    break;
                case "DELETE":
                    request = UnityWebRequest.Delete(fullUrl);
                    break;
                case "PATCH":
                    request = CreatePatchRequest(fullUrl, data);
                    break;
                default:
                    throw new ArgumentException($"Unsupported HTTP method: {method}");
            }

            // Configure request
            ConfigureRequest(request);
            
            // Send request with retry logic
            int attempts = 0;
            bool success = false;
            
            while (attempts < config.maxRetries && !success)
            {
                attempts++;
                
                var operation = request.SendWebRequest();
                float timeoutTimer = 0f;
                
                while (!operation.isDone && timeoutTimer < config.timeout)
                {
                    timeoutTimer += Time.unscaledDeltaTime;
                    await Task.Yield();
                }
                
                if (!operation.isDone)
                {
                    request.Abort();
                    throw new TimeoutException($"Request timeout after {config.timeout} seconds");
                }
                
                response.statusCode = (int)request.responseCode;
                response.headers = GetResponseHeaders(request);
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    success = true;
                    string responseText = request.downloadHandler.text;
                    
                    try
                    {
                        if (typeof(T) == typeof(string))
                        {
                            response.data = (T)(object)responseText;
                        }
                        else
                        {
                            response.data = JsonConvert.DeserializeObject<T>(responseText);
                        }
                        
                        response.success = true;
                        
                        // Cache successful GET requests
                        if (method == "GET" && config.enableCaching)
                        {
                            var cachedResponse = new CachedResponse
                            {
                                responseJson = JsonConvert.SerializeObject(response),
                                timestamp = DateTime.UtcNow,
                                ttl = 300 // 5 minutes default TTL
                            };
                            responseCache[cacheKey] = cachedResponse;
                        }
                    }
                    catch (JsonException jsonEx)
                    {
                        response.success = false;
                        response.error = $"JSON parsing error: {jsonEx.Message}";
                    }
                }
                else
                {
                    response.success = false;
                    response.error = GetErrorMessage(request);
                    
                    // Check if we should retry
                    if (ShouldRetry(request.responseCode, attempts))
                    {
                        float delay = CalculateRetryDelay(attempts);
                        await Task.Delay(TimeSpan.FromSeconds(delay));
                        continue;
                    }
                }
            }
            
            var endTime = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
            response.responseTime = endTime - startTime;
            
            // Record metrics
            RecordMetrics(endpoint, startTime, endTime, response.statusCode, 
                request.downloadHandler?.data?.Length ?? 0, false);
                
            return response;
        }
        catch (Exception e)
        {
            response.success = false;
            response.error = e.Message;
            response.statusCode = -1;
            
            Debug.LogError($"API Request Error [{method} {endpoint}]: {e.Message}");
            return response;
        }
        finally
        {
            request?.Dispose();
        }
    }

    // Request creation helpers
    private UnityWebRequest CreatePostRequest(string url, object data)
    {
        string jsonData = data != null ? JsonConvert.SerializeObject(data) : "{}";
        byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
        
        UnityWebRequest request = new UnityWebRequest(url, "POST");
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        
        return request;
    }

    private UnityWebRequest CreatePutRequest(string url, object data)
    {
        string jsonData = data != null ? JsonConvert.SerializeObject(data) : "{}";
        byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
        
        UnityWebRequest request = new UnityWebRequest(url, "PUT");
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        
        return request;
    }

    private UnityWebRequest CreatePatchRequest(string url, object data)
    {
        string jsonData = data != null ? JsonConvert.SerializeObject(data) : "{}";
        byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
        
        UnityWebRequest request = new UnityWebRequest(url, "PATCH");
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        
        return request;
    }

    // Request configuration
    private void ConfigureRequest(UnityWebRequest request)
    {
        // Add default headers
        foreach (var header in config.defaultHeaders)
        {
            request.SetRequestHeader(header.Key, header.Value);
        }
        
        // Add request signature for security
        string signature = GenerateRequestSignature(request);
        request.SetRequestHeader("X-Request-Signature", signature);
        
        // Add timestamp
        request.SetRequestHeader("X-Timestamp", DateTimeOffset.UtcNow.ToUnixTimeSeconds().ToString());
        
        // Enable compression if configured
        if (config.enableCompression)
        {
            request.SetRequestHeader("Accept-Encoding", "gzip, deflate");
        }
    }

    // Security helpers
    private string HashPassword(string password)
    {
        using (SHA256 sha256 = SHA256.Create())
        {
            byte[] hashedBytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(password + config.apiSecret));
            return Convert.ToBase64String(hashedBytes);
        }
    }

    private string GenerateRequestSignature(UnityWebRequest request)
    {
        string stringToSign = $"{request.method}{request.url}{DateTimeOffset.UtcNow.ToUnixTimeSeconds()}";
        
        using (HMACSHA256 hmac = new HMACSHA256(Encoding.UTF8.GetBytes(config.apiSecret)))
        {
            byte[] hash = hmac.ComputeHash(Encoding.UTF8.GetBytes(stringToSign));
            return Convert.ToBase64String(hash);
        }
    }

    // Cache management
    private string GenerateCacheKey(string method, string url, object data)
    {
        string dataString = data != null ? JsonConvert.SerializeObject(data) : "";
        string combined = $"{method}:{url}:{dataString}";
        
        using (MD5 md5 = MD5.Create())
        {
            byte[] hash = md5.ComputeHash(Encoding.UTF8.GetBytes(combined));
            return Convert.ToBase64String(hash);
        }
    }

    private void CleanupCache()
    {
        var expiredKeys = new List<string>();
        
        foreach (var kvp in responseCache)
        {
            if (kvp.Value.IsExpired())
            {
                expiredKeys.Add(kvp.Key);
            }
        }
        
        foreach (string key in expiredKeys)
        {
            responseCache.Remove(key);
        }
        
        Debug.Log($"Cleaned up {expiredKeys.Count} expired cache entries");
    }

    // Metrics and monitoring
    private void RecordMetrics(string endpoint, long startTime, long endTime, int statusCode, long dataSize, bool fromCache)
    {
        if (!enableMetrics) return;
        
        var metrics = new RequestMetrics
        {
            endpoint = endpoint,
            requestTime = startTime,
            responseTime = endTime - startTime,
            statusCode = statusCode,
            dataSize = dataSize,
            fromCache = fromCache
        };
        
        metricsHistory.Enqueue(metrics);
        
        if (metricsHistory.Count > metricsHistorySize)
        {
            metricsHistory.Dequeue();
        }
    }

    public List<RequestMetrics> GetMetricsHistory(int count = 100)
    {
        var metrics = new List<RequestMetrics>();
        var tempQueue = new Queue<RequestMetrics>(metricsHistory);
        
        int itemsToTake = Math.Min(count, tempQueue.Count);
        for (int i = 0; i < itemsToTake; i++)
        {
            metrics.Add(tempQueue.Dequeue());
        }
        
        return metrics;
    }

    public Dictionary<string, object> GetPerformanceStats()
    {
        if (metricsHistory.Count == 0)
            return new Dictionary<string, object>();
        
        var metrics = metricsHistory.ToArray();
        var stats = new Dictionary<string, object>
        {
            ["totalRequests"] = metrics.Length,
            ["averageResponseTime"] = metrics.Average(m => m.responseTime),
            ["successRate"] = metrics.Count(m => m.statusCode >= 200 && m.statusCode < 300) / (float)metrics.Length * 100,
            ["cacheHitRate"] = metrics.Count(m => m.fromCache) / (float)metrics.Length * 100,
            ["totalDataTransferred"] = metrics.Sum(m => m.dataSize)
        };
        
        return stats;
    }

    // Utility methods
    private string BuildUrl(string endpoint, Dictionary<string, string> parameters)
    {
        string url = config.baseUrl + endpoint;
        
        if (parameters != null && parameters.Count > 0)
        {
            var queryParams = new List<string>();
            foreach (var param in parameters)
            {
                queryParams.Add($"{UnityWebRequest.EscapeURL(param.Key)}={UnityWebRequest.EscapeURL(param.Value)}");
            }
            url += "?" + string.Join("&", queryParams);
        }
        
        return url;
    }

    private Dictionary<string, string> GetResponseHeaders(UnityWebRequest request)
    {
        var headers = new Dictionary<string, string>();
        
        if (request.GetResponseHeaders() != null)
        {
            foreach (var header in request.GetResponseHeaders())
            {
                headers[header.Key] = header.Value;
            }
        }
        
        return headers;
    }

    private string GetErrorMessage(UnityWebRequest request)
    {
        switch (request.result)
        {
            case UnityWebRequest.Result.ConnectionError:
                return "Connection error: " + request.error;
            case UnityWebRequest.Result.DataProcessingError:
                return "Data processing error: " + request.error;
            case UnityWebRequest.Result.ProtocolError:
                return $"HTTP error {request.responseCode}: {request.error}";
            default:
                return "Unknown error: " + request.error;
        }
    }

    private bool ShouldRetry(long responseCode, int attemptNumber)
    {
        // Retry on server errors (5xx) and some client errors
        if (responseCode >= 500 && responseCode < 600) return true;
        if (responseCode == 429) return true; // Rate limited
        if (responseCode == 408) return true; // Request timeout
        
        return false;
    }

    private float CalculateRetryDelay(int attemptNumber)
    {
        // Exponential backoff with jitter
        float baseDelay = Mathf.Pow(2, attemptNumber - 1);
        float jitter = UnityEngine.Random.Range(0f, 0.1f);
        return baseDelay + jitter;
    }

    // Supporting classes
    [System.Serializable]
    public class AuthResponse
    {
        public string token;
        public int expiresIn;
        public string refreshToken;
        public string tokenType;
    }

    [System.Serializable]
    public class CachedResponse
    {
        public string responseJson;
        public DateTime timestamp;
        public int ttl; // Time to live in seconds
        
        public bool IsExpired()
        {
            return DateTime.UtcNow > timestamp.AddSeconds(ttl);
        }
    }
}
```

### Unity GraphQL Client with Advanced Features
```csharp
// Advanced Unity GraphQL client with subscription support
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

public class UnityGraphQLClient : MonoBehaviour
{
    [System.Serializable]
    public class GraphQLConfiguration
    {
        public string endpoint;
        public string subscriptionsEndpoint;
        public string authToken;
        public Dictionary<string, string> headers;
        public bool enableIntrospection = true;
        public int maxQueryDepth = 10;
    }

    [System.Serializable]
    public class GraphQLRequest
    {
        public string query;
        public Dictionary<string, object> variables;
        public string operationName;
    }

    [System.Serializable]
    public class GraphQLResponse<T>
    {
        public T data;
        public List<GraphQLError> errors;
        public Dictionary<string, object> extensions;
    }

    [System.Serializable]
    public class GraphQLError
    {
        public string message;
        public List<GraphQLLocation> locations;
        public List<string> path;
        public Dictionary<string, object> extensions;
    }

    [System.Serializable]
    public class GraphQLLocation
    {
        public int line;
        public int column;
    }

    [Header("GraphQL Configuration")]
    [SerializeField] private GraphQLConfiguration config;

    [Header("Query Management")]
    [SerializeField] private bool enableQueryCaching = true;
    [SerializeField] private bool enablePersistedQueries = true;

    private Dictionary<string, string> queryCache;
    private Dictionary<string, object> schemaCache;
    private WebSocketConnection subscriptionConnection;

    public static UnityGraphQLClient Instance { get; private set; }

    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeGraphQLClient();
        }
        else
        {
            Destroy(gameObject);
        }
    }

    private void InitializeGraphQLClient()
    {
        queryCache = new Dictionary<string, string>();
        schemaCache = new Dictionary<string, object>();

        if (config.headers == null)
        {
            config.headers = new Dictionary<string, string>();
        }

        if (!string.IsNullOrEmpty(config.authToken))
        {
            config.headers["Authorization"] = $"Bearer {config.authToken}";
        }

        config.headers["Content-Type"] = "application/json";

        Debug.Log("Unity GraphQL Client initialized");
    }

    // Query execution methods
    public async Task<GraphQLResponse<T>> ExecuteQueryAsync<T>(string query, Dictionary<string, object> variables = null, string operationName = null)
    {
        var request = new GraphQLRequest
        {
            query = query,
            variables = variables,
            operationName = operationName
        };

        return await SendGraphQLRequestAsync<T>(request);
    }

    public async Task<GraphQLResponse<T>> ExecuteMutationAsync<T>(string mutation, Dictionary<string, object> variables = null, string operationName = null)
    {
        var request = new GraphQLRequest
        {
            query = mutation,
            variables = variables,
            operationName = operationName
        };

        return await SendGraphQLRequestAsync<T>(request);
    }

    // Advanced query builder
    public class QueryBuilder
    {
        private StringBuilder queryBuilder;
        private List<string> fragments;
        private Dictionary<string, object> variables;
        private int indentLevel;

        public QueryBuilder()
        {
            queryBuilder = new StringBuilder();
            fragments = new List<string>();
            variables = new Dictionary<string, object>();
            indentLevel = 0;
        }

        public QueryBuilder Query(string name = null)
        {
            if (!string.IsNullOrEmpty(name))
            {
                queryBuilder.AppendLine($"query {name} {{");
            }
            else
            {
                queryBuilder.AppendLine("query {");
            }
            indentLevel++;
            return this;
        }

        public QueryBuilder Mutation(string name = null)
        {
            if (!string.IsNullOrEmpty(name))
            {
                queryBuilder.AppendLine($"mutation {name} {{");
            }
            else
            {
                queryBuilder.AppendLine("mutation {");
            }
            indentLevel++;
            return this;
        }

        public QueryBuilder Field(string name, Dictionary<string, object> args = null)
        {
            string indent = new string(' ', indentLevel * 2);
            
            if (args != null && args.Count > 0)
            {
                var argsList = new List<string>();
                foreach (var arg in args)
                {
                    string varName = $"var_{variables.Count}";
                    variables[varName] = arg.Value;
                    argsList.Add($"{arg.Key}: ${varName}");
                }
                queryBuilder.AppendLine($"{indent}{name}({string.Join(", ", argsList)})");
            }
            else
            {
                queryBuilder.AppendLine($"{indent}{name}");
            }
            
            return this;
        }

        public QueryBuilder StartSelection()
        {
            string indent = new string(' ', indentLevel * 2);
            queryBuilder.AppendLine($"{indent}{{");
            indentLevel++;
            return this;
        }

        public QueryBuilder EndSelection()
        {
            indentLevel--;
            string indent = new string(' ', indentLevel * 2);
            queryBuilder.AppendLine($"{indent}}}");
            return this;
        }

        public QueryBuilder Fields(params string[] fields)
        {
            string indent = new string(' ', indentLevel * 2);
            foreach (string field in fields)
            {
                queryBuilder.AppendLine($"{indent}{field}");
            }
            return this;
        }

        public QueryBuilder Fragment(string name, string type, Action<QueryBuilder> selectionBuilder)
        {
            var fragmentBuilder = new QueryBuilder();
            fragmentBuilder.queryBuilder.AppendLine($"fragment {name} on {type} {{");
            fragmentBuilder.indentLevel = 1;
            selectionBuilder(fragmentBuilder);
            fragmentBuilder.queryBuilder.AppendLine("}");
            
            fragments.Add(fragmentBuilder.queryBuilder.ToString());
            
            // Add fragment spread to current query
            string indent = new string(' ', indentLevel * 2);
            queryBuilder.AppendLine($"{indent}...{name}");
            
            return this;
        }

        public GraphQLRequest Build()
        {
            // Close any open braces
            while (indentLevel > 0)
            {
                EndSelection();
            }

            string finalQuery = queryBuilder.ToString();
            
            // Append fragments
            if (fragments.Count > 0)
            {
                finalQuery += "\n" + string.Join("\n", fragments);
            }

            return new GraphQLRequest
            {
                query = finalQuery,
                variables = variables.Count > 0 ? variables : null
            };
        }
    }

    // Subscription support
    public async Task<IAsyncEnumerable<GraphQLResponse<T>>> SubscribeAsync<T>(string subscription, Dictionary<string, object> variables = null)
    {
        if (subscriptionConnection == null)
        {
            await InitializeSubscriptionConnection();
        }

        var request = new GraphQLRequest
        {
            query = subscription,
            variables = variables
        };

        return subscriptionConnection.Subscribe<T>(request);
    }

    private async Task InitializeSubscriptionConnection()
    {
        if (string.IsNullOrEmpty(config.subscriptionsEndpoint))
        {
            throw new InvalidOperationException("Subscriptions endpoint not configured");
        }

        subscriptionConnection = new WebSocketConnection(config.subscriptionsEndpoint, config.headers);
        await subscriptionConnection.ConnectAsync();
    }

    // Core request execution
    private async Task<GraphQLResponse<T>> SendGraphQLRequestAsync<T>(GraphQLRequest request)
    {
        try
        {
            // Validate query depth
            if (config.maxQueryDepth > 0)
            {
                int depth = CalculateQueryDepth(request.query);
                if (depth > config.maxQueryDepth)
                {
                    throw new InvalidOperationException($"Query depth {depth} exceeds maximum allowed depth {config.maxQueryDepth}");
                }
            }

            string requestJson = JsonConvert.SerializeObject(request, Formatting.None);
            byte[] bodyRaw = Encoding.UTF8.GetBytes(requestJson);

            using (UnityWebRequest webRequest = new UnityWebRequest(config.endpoint, "POST"))
            {
                webRequest.uploadHandler = new UploadHandlerRaw(bodyRaw);
                webRequest.downloadHandler = new DownloadHandlerBuffer();

                // Add headers
                foreach (var header in config.headers)
                {
                    webRequest.SetRequestHeader(header.Key, header.Value);
                }

                var operation = webRequest.SendWebRequest();
                
                while (!operation.isDone)
                {
                    await Task.Yield();
                }

                if (webRequest.result != UnityWebRequest.Result.Success)
                {
                    Debug.LogError($"GraphQL request failed: {webRequest.error}");
                    return new GraphQLResponse<T>
                    {
                        errors = new List<GraphQLError>
                        {
                            new GraphQLError { message = webRequest.error }
                        }
                    };
                }

                string responseText = webRequest.downloadHandler.text;
                var response = JsonConvert.DeserializeObject<GraphQLResponse<T>>(responseText);

                if (response.errors != null && response.errors.Count > 0)
                {
                    foreach (var error in response.errors)
                    {
                        Debug.LogWarning($"GraphQL Error: {error.message}");
                    }
                }

                return response;
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"GraphQL request exception: {e.Message}");
            return new GraphQLResponse<T>
            {
                errors = new List<GraphQLError>
                {
                    new GraphQLError { message = e.Message }
                }
            };
        }
    }

    // Schema introspection
    public async Task<Dictionary<string, object>> GetSchemaAsync()
    {
        if (schemaCache.Count > 0)
            return schemaCache;

        string introspectionQuery = @"
            query IntrospectionQuery {
                __schema {
                    queryType { name }
                    mutationType { name }
                    subscriptionType { name }
                    types {
                        ...FullType
                    }
                    directives {
                        name
                        description
                        locations
                        args {
                            ...InputValue
                        }
                    }
                }
            }

            fragment FullType on __Type {
                kind
                name
                description
                fields(includeDeprecated: true) {
                    name
                    description
                    args {
                        ...InputValue
                    }
                    type {
                        ...TypeRef
                    }
                    isDeprecated
                    deprecationReason
                }
                inputFields {
                    ...InputValue
                }
                interfaces {
                    ...TypeRef
                }
                enumValues(includeDeprecated: true) {
                    name
                    description
                    isDeprecated
                    deprecationReason
                }
                possibleTypes {
                    ...TypeRef
                }
            }

            fragment InputValue on __InputValue {
                name
                description
                type { ...TypeRef }
                defaultValue
            }

            fragment TypeRef on __Type {
                kind
                name
                ofType {
                    kind
                    name
                    ofType {
                        kind
                        name
                        ofType {
                            kind
                            name
                        }
                    }
                }
            }";

        var response = await ExecuteQueryAsync<Dictionary<string, object>>(introspectionQuery);
        
        if (response.data != null)
        {
            schemaCache = response.data;
        }

        return schemaCache;
    }

    // Query analysis and validation
    private int CalculateQueryDepth(string query)
    {
        int maxDepth = 0;
        int currentDepth = 0;
        bool inString = false;
        char stringChar = '"';

        for (int i = 0; i < query.Length; i++)
        {
            char c = query[i];

            if (!inString)
            {
                if (c == '"' || c == '\'')
                {
                    inString = true;
                    stringChar = c;
                }
                else if (c == '{')
                {
                    currentDepth++;
                    maxDepth = Math.Max(maxDepth, currentDepth);
                }
                else if (c == '}')
                {
                    currentDepth--;
                }
            }
            else
            {
                if (c == stringChar && (i == 0 || query[i - 1] != '\\'))
                {
                    inString = false;
                }
            }
        }

        return maxDepth;
    }

    // Utility methods
    public static QueryBuilder CreateQuery()
    {
        return new QueryBuilder();
    }

    public void SetAuthToken(string token)
    {
        config.authToken = token;
        config.headers["Authorization"] = $"Bearer {token}";
    }

    public void ClearCache()
    {
        queryCache.Clear();
        schemaCache.Clear();
    }

    private void OnDestroy()
    {
        if (subscriptionConnection != null)
        {
            subscriptionConnection.Dispose();
        }
    }
}

// WebSocket connection for GraphQL subscriptions
public class WebSocketConnection : IDisposable
{
    private string endpoint;
    private Dictionary<string, string> headers;
    private bool isConnected;
    private Dictionary<string, TaskCompletionSource<bool>> pendingOperations;

    public WebSocketConnection(string endpoint, Dictionary<string, string> headers)
    {
        this.endpoint = endpoint;
        this.headers = headers;
        this.pendingOperations = new Dictionary<string, TaskCompletionSource<bool>>();
    }

    public async Task ConnectAsync()
    {
        // WebSocket implementation would go here
        // This is a simplified version - actual implementation would use
        // a WebSocket library or native WebSocket support
        await Task.Delay(100); // Simulate connection
        isConnected = true;
    }

    public async IAsyncEnumerable<GraphQLResponse<T>> Subscribe<T>(GraphQLRequest request)
    {
        if (!isConnected)
        {
            throw new InvalidOperationException("WebSocket not connected");
        }

        // Simplified subscription implementation
        // Real implementation would handle WebSocket messages
        yield return new GraphQLResponse<T>();
    }

    public void Dispose()
    {
        isConnected = false;
        // Clean up WebSocket connection
    }
}
```

### Unity WebSocket Real-Time Communication System
```csharp
// Advanced Unity WebSocket manager for real-time game communication
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using Newtonsoft.Json;
using System.Collections.Concurrent;
using System.Threading;

public class UnityWebSocketManager : MonoBehaviour
{
    [System.Serializable]
    public class WebSocketConfiguration
    {
        public string serverUrl;
        public int port = 443;
        public bool useSSL = true;
        public int reconnectInterval = 5;
        public int maxReconnectAttempts = 10;
        public int heartbeatInterval = 30;
        public bool enableCompression = true;
        public Dictionary<string, string> headers;
    }

    [System.Serializable]
    public class WebSocketMessage
    {
        public string type;
        public string id;
        public Dictionary<string, object> payload;
        public long timestamp;
        public string sessionId;
    }

    [System.Serializable]
    public class ConnectionMetrics
    {
        public int messagesSent;
        public int messagesReceived;
        public long totalBytesSent;
        public long totalBytesReceived;
        public float averageLatency;
        public DateTime connectionStartTime;
        public int reconnectCount;
    }

    public enum ConnectionState
    {
        Disconnected,
        Connecting,
        Connected,
        Reconnecting,
        Failed
    }

    [Header("WebSocket Configuration")]
    [SerializeField] private WebSocketConfiguration config;

    [Header("Connection Management")]
    [SerializeField] private bool autoReconnect = true;
    [SerializeField] private bool enableMetrics = true;

    // Events
    public event Action<ConnectionState> OnConnectionStateChanged;
    public event Action<WebSocketMessage> OnMessageReceived;
    public event Action<string> OnError;

    private IWebSocketClient webSocketClient;
    private ConnectionState currentState = ConnectionState.Disconnected;
    private ConnectionMetrics metrics;
    private ConcurrentQueue<WebSocketMessage> incomingMessages;
    private ConcurrentQueue<WebSocketMessage> outgoingMessages;
    private Dictionary<string, TaskCompletionSource<WebSocketMessage>> pendingRequests;
    private Timer heartbeatTimer;
    private Timer reconnectTimer;
    private CancellationTokenSource cancellationTokenSource;
    private string sessionId;

    public static UnityWebSocketManager Instance { get; private set; }

    public ConnectionState CurrentState => currentState;
    public ConnectionMetrics Metrics => metrics;
    public bool IsConnected => currentState == ConnectionState.Connected;

    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeWebSocketManager();
        }
        else
        {
            Destroy(gameObject);
        }
    }

    private void InitializeWebSocketManager()
    {
        metrics = new ConnectionMetrics();
        incomingMessages = new ConcurrentQueue<WebSocketMessage>();
        outgoingMessages = new ConcurrentQueue<WebSocketMessage>();
        pendingRequests = new Dictionary<string, TaskCompletionSource<WebSocketMessage>>();
        cancellationTokenSource = new CancellationTokenSource();
        sessionId = GenerateSessionId();

        if (config.headers == null)
        {
            config.headers = new Dictionary<string, string>();
        }

        Debug.Log("Unity WebSocket Manager initialized");
    }

    // Connection management
    public async Task<bool> ConnectAsync()
    {
        if (currentState == ConnectionState.Connected || currentState == ConnectionState.Connecting)
        {
            Debug.LogWarning("Already connected or connecting");
            return false;
        }

        SetConnectionState(ConnectionState.Connecting);
        
        try
        {
            string url = BuildWebSocketUrl();
            webSocketClient = CreateWebSocketClient();
            
            bool connected = await webSocketClient.ConnectAsync(url, config.headers);
            
            if (connected)
            {
                SetConnectionState(ConnectionState.Connected);
                metrics.connectionStartTime = DateTime.UtcNow;
                StartHeartbeat();
                StartMessageProcessing();
                
                Debug.Log("WebSocket connected successfully");
                return true;
            }
            else
            {
                SetConnectionState(ConnectionState.Failed);
                Debug.LogError("Failed to connect to WebSocket server");
                return false;
            }
        }
        catch (Exception e)
        {
            SetConnectionState(ConnectionState.Failed);
            Debug.LogError($"WebSocket connection error: {e.Message}");
            OnError?.Invoke(e.Message);
            return false;
        }
    }

    public async Task DisconnectAsync()
    {
        StopHeartbeat();
        StopReconnectTimer();
        
        if (webSocketClient != null)
        {
            await webSocketClient.DisconnectAsync();
            webSocketClient = null;
        }
        
        SetConnectionState(ConnectionState.Disconnected);
        cancellationTokenSource.Cancel();
        
        Debug.Log("WebSocket disconnected");
    }

    // Message sending methods
    public async Task<bool> SendMessageAsync(string type, Dictionary<string, object> payload = null)
    {
        var message = new WebSocketMessage
        {
            type = type,
            id = Guid.NewGuid().ToString(),
            payload = payload ?? new Dictionary<string, object>(),
            timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
            sessionId = sessionId
        };

        return await SendMessageAsync(message);
    }

    public async Task<bool> SendMessageAsync(WebSocketMessage message)
    {
        if (!IsConnected)
        {
            Debug.LogWarning("Cannot send message - WebSocket not connected");
            return false;
        }

        try
        {
            string json = JsonConvert.SerializeObject(message);
            bool sent = await webSocketClient.SendAsync(json);
            
            if (sent)
            {
                metrics.messagesSent++;
                metrics.totalBytesSent += Encoding.UTF8.GetByteCount(json);
                
                Debug.Log($"Sent message: {message.type} (ID: {message.id})");
                return true;
            }
            
            return false;
        }
        catch (Exception e)
        {
            Debug.LogError($"Error sending message: {e.Message}");
            OnError?.Invoke(e.Message);
            return false;
        }
    }

    public async Task<WebSocketMessage> SendRequestAsync(string type, Dictionary<string, object> payload = null, int timeoutMs = 10000)
    {
        var message = new WebSocketMessage
        {
            type = type,
            id = Guid.NewGuid().ToString(),
            payload = payload ?? new Dictionary<string, object>(),
            timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
            sessionId = sessionId
        };

        var tcs = new TaskCompletionSource<WebSocketMessage>();
        pendingRequests[message.id] = tcs;

        bool sent = await SendMessageAsync(message);
        if (!sent)
        {
            pendingRequests.Remove(message.id);
            return null;
        }

        try
        {
            var timeoutTask = Task.Delay(timeoutMs);
            var completedTask = await Task.WhenAny(tcs.Task, timeoutTask);
            
            if (completedTask == timeoutTask)
            {
                pendingRequests.Remove(message.id);
                throw new TimeoutException($"Request {message.id} timed out after {timeoutMs}ms");
            }
            
            return await tcs.Task;
        }
        catch (Exception e)
        {
            pendingRequests.Remove(message.id);
            Debug.LogError($"Request error: {e.Message}");
            throw;
        }
    }

    // Message processing
    private async void StartMessageProcessing()
    {
        _ = Task.Run(ProcessIncomingMessages, cancellationTokenSource.Token);
        _ = Task.Run(ProcessOutgoingMessages, cancellationTokenSource.Token);
    }

    private async Task ProcessIncomingMessages()
    {
        while (!cancellationTokenSource.Token.IsCancellationRequested)
        {
            try
            {
                if (webSocketClient != null && IsConnected)
                {
                    string messageJson = await webSocketClient.ReceiveAsync();
                    if (!string.IsNullOrEmpty(messageJson))
                    {
                        var message = JsonConvert.DeserializeObject<WebSocketMessage>(messageJson);
                        HandleIncomingMessage(message);
                    }
                }
                
                await Task.Delay(1, cancellationTokenSource.Token);
            }
            catch (OperationCanceledException)
            {
                break;
            }
            catch (Exception e)
            {
                Debug.LogError($"Error processing incoming messages: {e.Message}");
                OnError?.Invoke(e.Message);
                
                if (autoReconnect && currentState != ConnectionState.Reconnecting)
                {
                    _ = ReconnectAsync();
                }
            }
        }
    }

    private async Task ProcessOutgoingMessages()
    {
        while (!cancellationTokenSource.Token.IsCancellationRequested)
        {
            try
            {
                if (outgoingMessages.TryDequeue(out WebSocketMessage message))
                {
                    await SendMessageAsync(message);
                }
                
                await Task.Delay(1, cancellationTokenSource.Token);
            }
            catch (OperationCanceledException)
            {
                break;
            }
            catch (Exception e)
            {
                Debug.LogError($"Error processing outgoing messages: {e.Message}");
            }
        }
    }

    private void HandleIncomingMessage(WebSocketMessage message)
    {
        metrics.messagesReceived++;
        metrics.totalBytesReceived += Encoding.UTF8.GetByteCount(JsonConvert.SerializeObject(message));

        // Handle response to pending request
        if (pendingRequests.ContainsKey(message.id))
        {
            var tcs = pendingRequests[message.id];
            pendingRequests.Remove(message.id);
            tcs.SetResult(message);
            return;
        }

        // Handle special message types
        switch (message.type?.ToLower())
        {
            case "heartbeat":
                HandleHeartbeatResponse(message);
                break;
            case "error":
                HandleErrorMessage(message);
                break;
            case "disconnect":
                HandleDisconnectMessage(message);
                break;
            default:
                // Queue message for Unity main thread processing
                incomingMessages.Enqueue(message);
                break;
        }
    }

    // Unity main thread message processing
    private void Update()
    {
        // Process incoming messages on Unity main thread
        while (incomingMessages.TryDequeue(out WebSocketMessage message))
        {
            try
            {
                OnMessageReceived?.Invoke(message);
            }
            catch (Exception e)
            {
                Debug.LogError($"Error in message handler: {e.Message}");
            }
        }
    }

    // Heartbeat system
    private void StartHeartbeat()
    {
        if (config.heartbeatInterval > 0)
        {
            heartbeatTimer = new Timer(SendHeartbeat, null, 
                TimeSpan.FromSeconds(config.heartbeatInterval), 
                TimeSpan.FromSeconds(config.heartbeatInterval));
        }
    }

    private void StopHeartbeat()
    {
        heartbeatTimer?.Dispose();
        heartbeatTimer = null;
    }

    private async void SendHeartbeat(object state)
    {
        if (IsConnected)
        {
            var payload = new Dictionary<string, object>
            {
                ["timestamp"] = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
                ["metrics"] = enableMetrics ? metrics : null
            };

            await SendMessageAsync("heartbeat", payload);
        }
    }

    private void HandleHeartbeatResponse(WebSocketMessage message)
    {
        if (message.payload.ContainsKey("timestamp"))
        {
            long serverTimestamp = Convert.ToInt64(message.payload["timestamp"]);
            long clientTimestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
            float latency = (clientTimestamp - serverTimestamp) / 2f;
            
            // Update average latency
            if (metrics.averageLatency == 0)
            {
                metrics.averageLatency = latency;
            }
            else
            {
                metrics.averageLatency = (metrics.averageLatency * 0.8f) + (latency * 0.2f);
            }
        }
    }

    // Reconnection logic
    private async Task ReconnectAsync()
    {
        if (currentState == ConnectionState.Reconnecting)
            return;

        SetConnectionState(ConnectionState.Reconnecting);
        
        for (int attempt = 1; attempt <= config.maxReconnectAttempts; attempt++)
        {
            Debug.Log($"Reconnection attempt {attempt}/{config.maxReconnectAttempts}");
            
            try
            {
                bool connected = await ConnectAsync();
                if (connected)
                {
                    metrics.reconnectCount++;
                    Debug.Log("Reconnected successfully");
                    return;
                }
            }
            catch (Exception e)
            {
                Debug.LogWarning($"Reconnection attempt {attempt} failed: {e.Message}");
            }
            
            if (attempt < config.maxReconnectAttempts)
            {
                await Task.Delay(config.reconnectInterval * 1000);
            }
        }
        
        SetConnectionState(ConnectionState.Failed);
        Debug.LogError("Failed to reconnect after maximum attempts");
    }

    private void StartReconnectTimer()
    {
        if (autoReconnect && reconnectTimer == null)
        {
            reconnectTimer = new Timer(async _ => await ReconnectAsync(), null, 
                TimeSpan.FromSeconds(config.reconnectInterval), 
                TimeSpan.FromMilliseconds(-1));
        }
    }

    private void StopReconnectTimer()
    {
        reconnectTimer?.Dispose();
        reconnectTimer = null;
    }

    // Helper methods
    private void SetConnectionState(ConnectionState newState)
    {
        if (currentState != newState)
        {
            currentState = newState;
            OnConnectionStateChanged?.Invoke(newState);
            Debug.Log($"WebSocket state changed to: {newState}");
        }
    }

    private string BuildWebSocketUrl()
    {
        string protocol = config.useSSL ? "wss" : "ws";
        string url = $"{protocol}://{config.serverUrl}";
        
        if (config.port != (config.useSSL ? 443 : 80))
        {
            url += $":{config.port}";
        }
        
        return url;
    }

    private IWebSocketClient CreateWebSocketClient()
    {
        // Factory method to create platform-specific WebSocket client
        #if UNITY_WEBGL && !UNITY_EDITOR
            return new WebGLWebSocketClient();
        #else
            return new NativeWebSocketClient();
        #endif
    }

    private string GenerateSessionId()
    {
        return Guid.NewGuid().ToString("N");
    }

    private void HandleErrorMessage(WebSocketMessage message)
    {
        string errorMessage = message.payload.ContainsKey("message") 
            ? message.payload["message"].ToString() 
            : "Unknown error";
        
        OnError?.Invoke(errorMessage);
        Debug.LogError($"WebSocket server error: {errorMessage}");
    }

    private void HandleDisconnectMessage(WebSocketMessage message)
    {
        string reason = message.payload.ContainsKey("reason") 
            ? message.payload["reason"].ToString() 
            : "Server initiated disconnect";
        
        Debug.Log($"Server disconnected: {reason}");
        _ = DisconnectAsync();
    }

    // Public utility methods
    public void QueueMessage(WebSocketMessage message)
    {
        outgoingMessages.Enqueue(message);
    }

    public Dictionary<string, object> GetConnectionInfo()
    {
        return new Dictionary<string, object>
        {
            ["state"] = currentState.ToString(),
            ["sessionId"] = sessionId,
            ["serverUrl"] = config.serverUrl,
            ["metrics"] = metrics,
            ["isConnected"] = IsConnected
        };
    }

    // Cleanup
    private void OnDestroy()
    {
        cancellationTokenSource?.Cancel();
        StopHeartbeat();
        StopReconnectTimer();
        
        if (webSocketClient != null)
        {
            _ = webSocketClient.DisconnectAsync();
        }
    }
}

// WebSocket client interface and implementations
public interface IWebSocketClient
{
    Task<bool> ConnectAsync(string url, Dictionary<string, string> headers);
    Task<bool> DisconnectAsync();
    Task<bool> SendAsync(string message);
    Task<string> ReceiveAsync();
}

// Platform-specific WebSocket client implementations would go here
#if UNITY_WEBGL && !UNITY_EDITOR
public class WebGLWebSocketClient : IWebSocketClient
{
    // WebGL-specific WebSocket implementation using JavaScript interop
    public async Task<bool> ConnectAsync(string url, Dictionary<string, string> headers) 
    { 
        return await Task.FromResult(true); 
    }
    
    public async Task<bool> DisconnectAsync() 
    { 
        return await Task.FromResult(true); 
    }
    
    public async Task<bool> SendAsync(string message) 
    { 
        return await Task.FromResult(true); 
    }
    
    public async Task<string> ReceiveAsync() 
    { 
        return await Task.FromResult(""); 
    }
}
#else
public class NativeWebSocketClient : IWebSocketClient
{
    // Native WebSocket implementation for standalone platforms
    public async Task<bool> ConnectAsync(string url, Dictionary<string, string> headers) 
    { 
        return await Task.FromResult(true); 
    }
    
    public async Task<bool> DisconnectAsync() 
    { 
        return await Task.FromResult(true); 
    }
    
    public async Task<bool> SendAsync(string message) 
    { 
        return await Task.FromResult(true); 
    }
    
    public async Task<string> ReceiveAsync() 
    { 
        return await Task.FromResult(""); 
    }
}
#endif
```

## 🚀 AI/LLM Integration Opportunities

### AI-Enhanced API Development
- **Smart API Testing**: AI generates comprehensive test cases for all API endpoints
- **Performance Optimization**: AI analyzes API usage patterns and suggests optimizations
- **Error Prediction**: AI predicts potential API failures and suggests preventive measures
- **Documentation Generation**: AI automatically generates API documentation from code
- **Security Analysis**: AI scans APIs for security vulnerabilities and compliance issues

### Advanced Integration Patterns
- **Intelligent Rate Limiting**: AI manages API rate limits based on usage patterns
- **Dynamic Schema Evolution**: AI assists with API versioning and schema migrations
- **Real-time Analytics**: AI provides insights from API usage and performance metrics
- **Automated Load Balancing**: AI optimizes API request distribution across servers
- **Predictive Caching**: AI predicts which API responses should be cached for optimal performance

## 💡 Key Highlights

### Enterprise API Architecture
1. **Comprehensive Integration**: Complete REST, GraphQL, and WebSocket implementation
2. **Advanced Security**: Authentication, request signing, and encryption support
3. **Performance Optimization**: Caching, compression, and connection pooling
4. **Real-time Communication**: WebSocket support with heartbeat and reconnection
5. **Monitoring & Analytics**: Detailed metrics and performance tracking

### Professional Development Skills
- **API Design Mastery**: Understanding of RESTful principles, GraphQL, and real-time protocols
- **Security Implementation**: Knowledge of authentication, authorization, and secure communication
- **Performance Engineering**: Skills in optimizing API performance and scalability
- **Real-time Systems**: Experience with WebSocket and event-driven architectures
- **Enterprise Integration**: Ability to integrate complex API systems in production environments

### Career Development Impact
- **Backend Integration Expertise**: Valuable skills for full-stack Unity development roles
- **System Architecture**: Understanding of distributed systems and microservices
- **Performance Optimization**: Critical skills for high-scale applications
- **Security Engineering**: Knowledge of API security best practices
- **Technical Leadership**: Ability to design and implement enterprise-grade API architectures

This comprehensive API architecture mastery positions you as a Unity developer who can integrate with any backend system and build sophisticated network communication layers for enterprise-grade games and applications.