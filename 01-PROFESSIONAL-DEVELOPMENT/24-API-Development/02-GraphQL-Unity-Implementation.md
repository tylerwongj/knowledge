# 02-GraphQL-Unity-Implementation.md

## 🎯 Learning Objectives
- Master GraphQL integration in Unity applications with efficient query management
- Implement real-time subscriptions for live game data updates
- Design optimized data fetching strategies with caching and batching
- Develop type-safe GraphQL clients with code generation and validation

## 🔧 Unity GraphQL Implementation

### GraphQL Client Manager
```csharp
// Scripts/GraphQL/GraphQLClient.cs
using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

public class GraphQLClient : MonoBehaviour
{
    [Header("GraphQL Configuration")]
    [SerializeField] private string graphqlEndpoint = "https://api.yourgame.com/graphql";
    [SerializeField] private string subscriptionEndpoint = "wss://api.yourgame.com/graphql";
    [SerializeField] private float defaultTimeout = 30f;
    [SerializeField] private bool enableQueryCaching = true;
    [SerializeField] private bool enableBatching = true;
    [SerializeField] private float batchingDelay = 0.1f;
    
    public static GraphQLClient Instance { get; private set; }
    
    // Events
    public System.Action<GraphQLError> OnGraphQLError;
    public System.Action<bool> OnConnectionStatusChanged;
    
    // Properties
    public bool IsConnected { get; private set; }
    
    private Dictionary<string, string> defaultHeaders;
    private GraphQLCache cache;
    private GraphQLSubscriptionManager subscriptionManager;
    private List<GraphQLRequest> batchQueue;
    private bool isBatchProcessing;
    
    [System.Serializable]
    public class GraphQLRequest
    {
        public string id;
        public string query;
        public object variables;
        public string operationName;
        public System.Action<GraphQLResponse> onSuccess;
        public System.Action<GraphQLError> onError;
        public bool useCache;
        public float cacheExpiry;
        public DateTime timestamp;
        
        public GraphQLRequest()
        {
            id = Guid.NewGuid().ToString();
            variables = new object();
            useCache = false;
            cacheExpiry = 300f;
            timestamp = DateTime.UtcNow;
        }
    }
    
    [System.Serializable]
    public class GraphQLResponse
    {
        public JObject data;
        public List<GraphQLError> errors;
        public JObject extensions;
        public bool fromCache;
        
        public T GetData<T>(string path = null)
        {
            try
            {
                JToken token = string.IsNullOrEmpty(path) ? data : data.SelectToken(path);
                return token != null ? token.ToObject<T>() : default(T);
            }
            catch (Exception e)
            {
                Debug.LogError($"Failed to extract GraphQL data: {e.Message}");
                return default(T);
            }
        }
        
        public bool HasErrors => errors != null && errors.Count > 0;
    }
    
    [System.Serializable]
    public class GraphQLError
    {
        public string message;
        public List<GraphQLLocation> locations;
        public List<string> path;
        public JObject extensions;
    }
    
    [System.Serializable]
    public class GraphQLLocation
    {
        public int line;
        public int column;
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
        defaultHeaders = new Dictionary<string, string>
        {
            {"Content-Type", "application/json"},
            {"Accept", "application/json"}
        };
        
        cache = new GraphQLCache();
        subscriptionManager = new GraphQLSubscriptionManager(subscriptionEndpoint);
        batchQueue = new List<GraphQLRequest>();
        
        IsConnected = true; // Assume connected initially
        
        // Start batch processing coroutine
        StartCoroutine(ProcessBatchQueue());
    }
    
    // Query execution
    public void Query<T>(string query, object variables = null, System.Action<T> onSuccess = null,
        System.Action<GraphQLError> onError = null, bool useCache = true, float cacheExpiry = 300f)
    {
        var request = new GraphQLRequest
        {
            query = query,
            variables = variables ?? new object(),
            onSuccess = (response) =>
            {
                if (response.HasErrors)
                {
                    onError?.Invoke(response.errors[0]);
                }
                else
                {
                    onSuccess?.Invoke(response.GetData<T>());
                }
            },
            onError = onError,
            useCache = useCache,
            cacheExpiry = cacheExpiry
        };
        
        ExecuteRequest(request);
    }
    
    public void Mutation<T>(string mutation, object variables = null, System.Action<T> onSuccess = null,
        System.Action<GraphQLError> onError = null)
    {
        var request = new GraphQLRequest
        {
            query = mutation,
            variables = variables ?? new object(),
            onSuccess = (response) =>
            {
                if (response.HasErrors)
                {
                    onError?.Invoke(response.errors[0]);
                }
                else
                {
                    onSuccess?.Invoke(response.GetData<T>());
                    
                    // Clear related cache entries for mutations
                    cache.InvalidateRelatedQueries(mutation);
                }
            },
            onError = onError,
            useCache = false // Mutations are never cached
        };
        
        ExecuteRequest(request);
    }
    
    public GraphQLSubscription Subscribe<T>(string subscription, object variables = null,
        System.Action<T> onData = null, System.Action<GraphQLError> onError = null)
    {
        return subscriptionManager.Subscribe<T>(subscription, variables, onData, onError);
    }
    
    private void ExecuteRequest(GraphQLRequest request)
    {
        // Check cache for queries
        if (request.query.Trim().StartsWith("query") && request.useCache)
        {
            string cacheKey = GenerateCacheKey(request.query, request.variables);
            var cachedResponse = cache.Get(cacheKey);
            
            if (cachedResponse != null)
            {
                Debug.Log($"[GraphQL] Cache hit for query");
                request.onSuccess?.Invoke(cachedResponse);
                return;
            }
        }
        
        // Add to batch queue if batching is enabled
        if (enableBatching && !request.query.Trim().StartsWith("mutation"))
        {
            batchQueue.Add(request);
        }
        else
        {
            StartCoroutine(ExecuteSingleRequest(request));
        }
    }
    
    private IEnumerator ExecuteSingleRequest(GraphQLRequest request)
    {
        var requestBody = new
        {
            query = request.query,
            variables = request.variables,
            operationName = request.operationName
        };
        
        string jsonData = JsonConvert.SerializeObject(requestBody);
        
        using (UnityWebRequest webRequest = new UnityWebRequest(graphqlEndpoint, "POST"))
        {
            byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
            webRequest.uploadHandler = new UploadHandlerRaw(bodyRaw);
            webRequest.downloadHandler = new DownloadHandlerBuffer();
            
            // Set headers
            foreach (var header in defaultHeaders)
            {
                webRequest.SetRequestHeader(header.Key, header.Value);
            }
            
            // Add authentication
            if (AuthenticationManager.Instance != null && AuthenticationManager.Instance.IsAuthenticated)
            {
                AuthenticationManager.Instance.AddAuthorizationHeader(webRequest);
            }
            
            webRequest.timeout = (int)defaultTimeout;
            
            Debug.Log($"[GraphQL] Executing: {GetOperationType(request.query)}");
            
            yield return webRequest.SendWebRequest();
            
            if (webRequest.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    var response = JsonConvert.DeserializeObject<GraphQLResponse>(webRequest.downloadHandler.text);
                    
                    if (response.HasErrors)
                    {
                        Debug.LogError($"[GraphQL] Query errors: {string.Join(", ", response.errors.ConvertAll(e => e.message))}");
                        request.onError?.Invoke(response.errors[0]);
                        OnGraphQLError?.Invoke(response.errors[0]);
                    }
                    else
                    {
                        // Cache successful queries
                        if (request.query.Trim().StartsWith("query") && request.useCache)
                        {
                            string cacheKey = GenerateCacheKey(request.query, request.variables);
                            cache.Set(cacheKey, response, request.cacheExpiry);
                        }
                        
                        request.onSuccess?.Invoke(response);
                    }
                }
                catch (Exception e)
                {
                    Debug.LogError($"[GraphQL] Response parsing error: {e.Message}");
                    var error = new GraphQLError { message = $"Response parsing error: {e.Message}" };
                    request.onError?.Invoke(error);
                    OnGraphQLError?.Invoke(error);
                }
            }
            else
            {
                Debug.LogError($"[GraphQL] Request failed: {webRequest.error}");
                var error = new GraphQLError { message = webRequest.error };
                request.onError?.Invoke(error);
                OnGraphQLError?.Invoke(error);
            }
        }
    }
    
    private IEnumerator ProcessBatchQueue()
    {
        while (true)
        {
            yield return new WaitForSeconds(batchingDelay);
            
            if (batchQueue.Count > 0 && !isBatchProcessing)
            {
                isBatchProcessing = true;
                var batchRequests = new List<GraphQLRequest>(batchQueue);
                batchQueue.Clear();
                
                yield return StartCoroutine(ExecuteBatchRequest(batchRequests));
                
                isBatchProcessing = false;
            }
        }
    }
    
    private IEnumerator ExecuteBatchRequest(List<GraphQLRequest> requests)
    {
        if (requests.Count == 1)
        {
            // Execute single request normally
            yield return StartCoroutine(ExecuteSingleRequest(requests[0]));
            yield break;
        }
        
        Debug.Log($"[GraphQL] Executing batch of {requests.Count} requests");
        
        var batchArray = requests.ConvertAll(req => new
        {
            query = req.query,
            variables = req.variables,
            operationName = req.operationName
        });
        
        string jsonData = JsonConvert.SerializeObject(batchArray);
        
        using (UnityWebRequest webRequest = new UnityWebRequest(graphqlEndpoint, "POST"))
        {
            byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
            webRequest.uploadHandler = new UploadHandlerRaw(bodyRaw);
            webRequest.downloadHandler = new DownloadHandlerBuffer();
            
            foreach (var header in defaultHeaders)
            {
                webRequest.SetRequestHeader(header.Key, header.Value);
            }
            
            if (AuthenticationManager.Instance != null && AuthenticationManager.Instance.IsAuthenticated)
            {
                AuthenticationManager.Instance.AddAuthorizationHeader(webRequest);
            }
            
            webRequest.timeout = (int)defaultTimeout;
            
            yield return webRequest.SendWebRequest();
            
            if (webRequest.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    var responses = JsonConvert.DeserializeObject<List<GraphQLResponse>>(webRequest.downloadHandler.text);
                    
                    for (int i = 0; i < requests.Count && i < responses.Count; i++)
                    {
                        var request = requests[i];
                        var response = responses[i];
                        
                        if (response.HasErrors)
                        {
                            request.onError?.Invoke(response.errors[0]);
                            OnGraphQLError?.Invoke(response.errors[0]);
                        }
                        else
                        {
                            // Cache successful queries
                            if (request.query.Trim().StartsWith("query") && request.useCache)
                            {
                                string cacheKey = GenerateCacheKey(request.query, request.variables);
                                cache.Set(cacheKey, response, request.cacheExpiry);
                            }
                            
                            request.onSuccess?.Invoke(response);
                        }
                    }
                }
                catch (Exception e)
                {
                    Debug.LogError($"[GraphQL] Batch response parsing error: {e.Message}");
                    var error = new GraphQLError { message = $"Batch response parsing error: {e.Message}" };
                    
                    foreach (var request in requests)
                    {
                        request.onError?.Invoke(error);
                    }
                    OnGraphQLError?.Invoke(error);
                }
            }
            else
            {
                Debug.LogError($"[GraphQL] Batch request failed: {webRequest.error}");
                var error = new GraphQLError { message = webRequest.error };
                
                foreach (var request in requests)
                {
                    request.onError?.Invoke(error);
                }
                OnGraphQLError?.Invoke(error);
            }
        }
    }
    
    private string GenerateCacheKey(string query, object variables)
    {
        string variablesJson = JsonConvert.SerializeObject(variables);
        return $"{query.GetHashCode()}:{variablesJson.GetHashCode()}";
    }
    
    private string GetOperationType(string query)
    {
        string trimmed = query.Trim().ToLower();
        if (trimmed.StartsWith("query")) return "Query";
        if (trimmed.StartsWith("mutation")) return "Mutation";
        if (trimmed.StartsWith("subscription")) return "Subscription";
        return "Unknown";
    }
    
    // Utility methods
    public void SetDefaultHeader(string key, string value)
    {
        defaultHeaders[key] = value;
    }
    
    public void ClearCache()
    {
        cache.Clear();
        Debug.Log("[GraphQL] Cache cleared");
    }
    
    public void SetCacheEnabled(bool enabled)
    {
        enableQueryCaching = enabled;
    }
    
    public void SetBatchingEnabled(bool enabled)
    {
        enableBatching = enabled;
    }
    
    private void OnDestroy()
    {
        subscriptionManager?.Dispose();
    }
}
```

### GraphQL Query Builder
```csharp
// Scripts/GraphQL/GraphQLQueryBuilder.cs
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

public class GraphQLQueryBuilder
{
    private string operationType;
    private string operationName;
    private List<string> fields;
    private Dictionary<string, object> variables;
    private Dictionary<string, string> arguments;
    private List<GraphQLFragment> fragments;
    private int indentLevel;
    
    public GraphQLQueryBuilder(string type = "query")
    {
        operationType = type;
        fields = new List<string>();
        variables = new Dictionary<string, object>();
        arguments = new Dictionary<string, string>();
        fragments = new List<GraphQLFragment>();
        indentLevel = 0;
    }
    
    public GraphQLQueryBuilder Name(string name)
    {
        operationName = name;
        return this;
    }
    
    public GraphQLQueryBuilder Variable(string name, object value, string type = null)
    {
        variables[name] = value;
        return this;
    }
    
    public GraphQLQueryBuilder Field(string name, System.Action<GraphQLQueryBuilder> configure = null)
    {
        var fieldBuilder = new StringBuilder();
        fieldBuilder.Append(GetIndent() + name);
        
        if (configure != null)
        {
            fieldBuilder.AppendLine(" {");
            indentLevel++;
            
            var subBuilder = new GraphQLQueryBuilder();
            subBuilder.indentLevel = indentLevel;
            configure(subBuilder);
            
            fieldBuilder.Append(string.Join("\n", subBuilder.fields));
            
            indentLevel--;
            fieldBuilder.AppendLine();
            fieldBuilder.Append(GetIndent() + "}");
        }
        
        fields.Add(fieldBuilder.ToString());
        return this;
    }
    
    public GraphQLQueryBuilder Field(string name, Dictionary<string, object> args, 
        System.Action<GraphQLQueryBuilder> configure = null)
    {
        var fieldBuilder = new StringBuilder();
        fieldBuilder.Append(GetIndent() + name);
        
        if (args != null && args.Count > 0)
        {
            var argStrings = args.Select(kvp => $"{kvp.Key}: {FormatArgument(kvp.Value)}");
            fieldBuilder.Append($"({string.Join(", ", argStrings)})");
        }
        
        if (configure != null)
        {
            fieldBuilder.AppendLine(" {");
            indentLevel++;
            
            var subBuilder = new GraphQLQueryBuilder();
            subBuilder.indentLevel = indentLevel;
            configure(subBuilder);
            
            fieldBuilder.Append(string.Join("\n", subBuilder.fields));
            
            indentLevel--;
            fieldBuilder.AppendLine();
            fieldBuilder.Append(GetIndent() + "}");
        }
        
        fields.Add(fieldBuilder.ToString());
        return this;
    }
    
    public GraphQLQueryBuilder SimpleField(string name)
    {
        fields.Add(GetIndent() + name);
        return this;
    }
    
    public GraphQLQueryBuilder SimpleFields(params string[] names)
    {
        foreach (string name in names)
        {
            fields.Add(GetIndent() + name);
        }
        return this;
    }
    
    public GraphQLQueryBuilder Fragment(string name, string onType, System.Action<GraphQLQueryBuilder> configure)
    {
        var fragmentBuilder = new GraphQLQueryBuilder();
        configure(fragmentBuilder);
        
        var fragment = new GraphQLFragment
        {
            name = name,
            onType = onType,
            fields = fragmentBuilder.fields
        };
        
        fragments.Add(fragment);
        fields.Add(GetIndent() + $"...{name}");
        
        return this;
    }
    
    public GraphQLQueryBuilder InlineFragment(string onType, System.Action<GraphQLQueryBuilder> configure)
    {
        var fragmentBuilder = new StringBuilder();
        fragmentBuilder.AppendLine(GetIndent() + $"... on {onType} {{");
        
        indentLevel++;
        var subBuilder = new GraphQLQueryBuilder();
        subBuilder.indentLevel = indentLevel;
        configure(subBuilder);
        
        fragmentBuilder.Append(string.Join("\n", subBuilder.fields));
        indentLevel--;
        
        fragmentBuilder.AppendLine();
        fragmentBuilder.Append(GetIndent() + "}");
        
        fields.Add(fragmentBuilder.ToString());
        return this;
    }
    
    public string Build()
    {
        var query = new StringBuilder();
        
        // Operation definition
        query.Append(operationType);
        
        if (!string.IsNullOrEmpty(operationName))
        {
            query.Append($" {operationName}");
        }
        
        // Variables
        if (variables.Count > 0)
        {
            var variableStrings = variables.Select(kvp => $"${kvp.Key}: {GetVariableType(kvp.Value)}");
            query.Append($"({string.Join(", ", variableStrings)})");
        }
        
        query.AppendLine(" {");
        
        // Fields
        query.Append(string.Join("\n", fields));
        
        query.AppendLine();
        query.AppendLine("}");
        
        // Fragments
        foreach (var fragment in fragments)
        {
            query.AppendLine();
            query.AppendLine($"fragment {fragment.name} on {fragment.onType} {{");
            query.Append(string.Join("\n", fragment.fields));
            query.AppendLine();
            query.AppendLine("}");
        }
        
        return query.ToString();
    }
    
    public GraphQLClient.GraphQLRequest BuildRequest()
    {
        return new GraphQLClient.GraphQLRequest
        {
            query = Build(),
            variables = variables,
            operationName = operationName
        };
    }
    
    private string GetIndent()
    {
        return new string(' ', indentLevel * 2);
    }
    
    private string FormatArgument(object value)
    {
        switch (value)
        {
            case string s:
                return $"\"{s}\"";
            case bool b:
                return b.ToString().ToLower();
            case null:
                return "null";
            case System.Collections.IEnumerable enumerable when !(value is string):
                var items = enumerable.Cast<object>().Select(FormatArgument);
                return $"[{string.Join(", ", items)}]";
            default:
                return value.ToString();
        }
    }
    
    private string GetVariableType(object value)
    {
        switch (value)
        {
            case string _:
                return "String";
            case int _:
                return "Int";
            case float _:
            case double _:
                return "Float";
            case bool _:
                return "Boolean";
            case System.Collections.IEnumerable _ when !(value is string):
                return "[String]"; // Default array type
            default:
                return "String"; // Default type
        }
    }
    
    private class GraphQLFragment
    {
        public string name;
        public string onType;
        public List<string> fields;
    }
    
    // Static helper methods for common query patterns
    public static GraphQLQueryBuilder Query(string name = null)
    {
        return new GraphQLQueryBuilder("query").Name(name);
    }
    
    public static GraphQLQueryBuilder Mutation(string name = null)
    {
        return new GraphQLQueryBuilder("mutation").Name(name);
    }
    
    public static GraphQLQueryBuilder Subscription(string name = null)
    {
        return new GraphQLQueryBuilder("subscription").Name(name);
    }
}
```

### Game-Specific GraphQL Service
```csharp
// Scripts/Services/GameGraphQLService.cs
using System;
using System.Collections.Generic;
using UnityEngine;

public class GameGraphQLService : MonoBehaviour
{
    public static GameGraphQLService Instance { get; private set; }
    
    // Events
    public System.Action<PlayerData> OnPlayerDataUpdated;
    public System.Action<List<LeaderboardEntry>> OnLeaderboardUpdated;
    public System.Action<GameMatch> OnMatchUpdated;
    
    [Serializable]
    public class PlayerData
    {
        public string id;
        public string username;
        public string email;
        public int level;
        public long experience;
        public PlayerStats stats;
        public List<Achievement> achievements;
        public Inventory inventory;
    }
    
    [Serializable]
    public class PlayerStats
    {
        public int gamesPlayed;
        public int gamesWon;
        public int totalScore;
        public float averageScore;
        public int killCount;
        public int deathCount;
        public float playtimeMinutes;
    }
    
    [Serializable]
    public class Achievement
    {
        public string id;
        public string name;
        public string description;
        public bool unlocked;
        public DateTime unlockedAt;
        public int progress;
        public int target;
    }
    
    [Serializable]
    public class Inventory
    {
        public List<InventoryItem> items;
        public int coins;
        public int gems;
    }
    
    [Serializable]
    public class InventoryItem
    {
        public string id;
        public string itemId;
        public int quantity;
        public Dictionary<string, object> metadata;
    }
    
    [Serializable]
    public class LeaderboardEntry
    {
        public int rank;
        public PlayerData player;
        public long score;
        public DateTime achievedAt;
    }
    
    [Serializable]
    public class GameMatch
    {
        public string id;
        public string gameMode;
        public List<MatchPlayer> players;
        public string status;
        public DateTime startTime;
        public DateTime endTime;
        public MatchResult result;
    }
    
    [Serializable]
    public class MatchPlayer
    {
        public PlayerData player;
        public int score;
        public int kills;
        public int deaths;
        public bool isWinner;
    }
    
    [Serializable]
    public class MatchResult
    {
        public string winnerId;
        public int duration;
        public Dictionary<string, object> stats;
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
    
    // Player Data Operations
    public void GetPlayerData(string playerId, System.Action<PlayerData> onSuccess = null, 
        System.Action<GraphQLClient.GraphQLError> onError = null)
    {
        var query = GraphQLQueryBuilder
            .Query("GetPlayer")
            .Variable("playerId", playerId)
            .Field("player", new Dictionary<string, object> { {"id", "$playerId"} }, builder =>
                builder
                    .SimpleFields("id", "username", "email", "level", "experience")
                    .Field("stats", statsBuilder =>
                        statsBuilder.SimpleFields("gamesPlayed", "gamesWon", "totalScore", 
                            "averageScore", "killCount", "deathCount", "playtimeMinutes"))
                    .Field("achievements", achievementBuilder =>
                        achievementBuilder.SimpleFields("id", "name", "description", "unlocked", 
                            "unlockedAt", "progress", "target"))
                    .Field("inventory", invBuilder =>
                        invBuilder
                            .SimpleFields("coins", "gems")
                            .Field("items", itemBuilder =>
                                itemBuilder.SimpleFields("id", "itemId", "quantity", "metadata")))
            );
        
        GraphQLClient.Instance.Query<PlayerDataResponse>(
            query.Build(),
            query.variables,
            (response) =>
            {
                OnPlayerDataUpdated?.Invoke(response.player);
                onSuccess?.Invoke(response.player);
            },
            onError
        );
    }
    
    public void UpdatePlayerStats(string playerId, PlayerStats newStats, 
        System.Action<PlayerData> onSuccess = null, System.Action<GraphQLClient.GraphQLError> onError = null)
    {
        var mutation = GraphQLQueryBuilder
            .Mutation("UpdatePlayerStats")
            .Variable("playerId", playerId)
            .Variable("stats", newStats)
            .Field("updatePlayerStats", new Dictionary<string, object> 
                { 
                    {"playerId", "$playerId"}, 
                    {"stats", "$stats"} 
                }, builder =>
                builder
                    .SimpleFields("id", "username", "level", "experience")
                    .Field("stats", statsBuilder =>
                        statsBuilder.SimpleFields("gamesPlayed", "gamesWon", "totalScore"))
            );
        
        GraphQLClient.Instance.Mutation<UpdatePlayerResponse>(
            mutation.Build(),
            mutation.variables,
            (response) =>
            {
                OnPlayerDataUpdated?.Invoke(response.updatePlayerStats);
                onSuccess?.Invoke(response.updatePlayerStats);
            },
            onError
        );
    }
    
    // Leaderboard Operations
    public void GetLeaderboard(string leaderboardType, int limit = 20, 
        System.Action<List<LeaderboardEntry>> onSuccess = null, 
        System.Action<GraphQLClient.GraphQLError> onError = null)
    {
        var query = GraphQLQueryBuilder
            .Query("GetLeaderboard")
            .Variable("type", leaderboardType)
            .Variable("limit", limit)
            .Field("leaderboard", new Dictionary<string, object> 
                { 
                    {"type", "$type"}, 
                    {"first", "$limit"} 
                }, builder =>
                builder
                    .Field("entries", entryBuilder =>
                        entryBuilder
                            .SimpleFields("rank", "score", "achievedAt")
                            .Field("player", playerBuilder =>
                                playerBuilder.SimpleFields("id", "username", "level")))
            );
        
        GraphQLClient.Instance.Query<LeaderboardResponse>(
            query.Build(),
            query.variables,
            (response) =>
            {
                OnLeaderboardUpdated?.Invoke(response.leaderboard.entries);
                onSuccess?.Invoke(response.leaderboard.entries);
            },
            onError
        );
    }
    
    public void SubmitScore(string playerId, string leaderboardType, long score,
        System.Action<LeaderboardEntry> onSuccess = null, System.Action<GraphQLClient.GraphQLError> onError = null)
    {
        var mutation = GraphQLQueryBuilder
            .Mutation("SubmitScore")
            .Variable("playerId", playerId)
            .Variable("leaderboardType", leaderboardType)
            .Variable("score", score)
            .Field("submitScore", new Dictionary<string, object> 
                { 
                    {"playerId", "$playerId"}, 
                    {"leaderboardType", "$leaderboardType"},
                    {"score", "$score"}
                }, builder =>
                builder
                    .SimpleFields("rank", "score", "achievedAt")
                    .Field("player", playerBuilder =>
                        playerBuilder.SimpleFields("id", "username"))
            );
        
        GraphQLClient.Instance.Mutation<SubmitScoreResponse>(
            mutation.Build(),
            mutation.variables,
            (response) => onSuccess?.Invoke(response.submitScore),
            onError
        );
    }
    
    // Match Operations
    public void CreateMatch(string gameMode, List<string> playerIds,
        System.Action<GameMatch> onSuccess = null, System.Action<GraphQLClient.GraphQLError> onError = null)
    {
        var mutation = GraphQLQueryBuilder
            .Mutation("CreateMatch")
            .Variable("gameMode", gameMode)
            .Variable("playerIds", playerIds)
            .Field("createMatch", new Dictionary<string, object> 
                { 
                    {"gameMode", "$gameMode"}, 
                    {"playerIds", "$playerIds"}
                }, builder =>
                builder
                    .SimpleFields("id", "gameMode", "status", "startTime")
                    .Field("players", playerBuilder =>
                        playerBuilder
                            .SimpleFields("score", "kills", "deaths", "isWinner")
                            .Field("player", pBuilder =>
                                pBuilder.SimpleFields("id", "username")))
            );
        
        GraphQLClient.Instance.Mutation<CreateMatchResponse>(
            mutation.Build(),
            mutation.variables,
            (response) =>
            {
                OnMatchUpdated?.Invoke(response.createMatch);
                onSuccess?.Invoke(response.createMatch);
            },
            onError
        );
    }
    
    // Real-time Subscriptions
    public GraphQLSubscription SubscribeToPlayerUpdates(string playerId,
        System.Action<PlayerData> onUpdate = null, System.Action<GraphQLClient.GraphQLError> onError = null)
    {
        var subscription = GraphQLQueryBuilder
            .Subscription("PlayerUpdated")
            .Variable("playerId", playerId)
            .Field("playerUpdated", new Dictionary<string, object> { {"playerId", "$playerId"} }, builder =>
                builder
                    .SimpleFields("id", "username", "level", "experience")
                    .Field("stats", statsBuilder =>
                        statsBuilder.SimpleFields("gamesPlayed", "gamesWon", "totalScore"))
            );
        
        return GraphQLClient.Instance.Subscribe<PlayerUpdatedResponse>(
            subscription.Build(),
            subscription.variables,
            (response) =>
            {
                OnPlayerDataUpdated?.Invoke(response.playerUpdated);
                onUpdate?.Invoke(response.playerUpdated);
            },
            onError
        );
    }
    
    public GraphQLSubscription SubscribeToMatchUpdates(string matchId,
        System.Action<GameMatch> onUpdate = null, System.Action<GraphQLClient.GraphQLError> onError = null)
    {
        var subscription = GraphQLQueryBuilder
            .Subscription("MatchUpdated")
            .Variable("matchId", matchId)
            .Field("matchUpdated", new Dictionary<string, object> { {"matchId", "$matchId"} }, builder =>
                builder
                    .SimpleFields("id", "gameMode", "status", "startTime", "endTime")
                    .Field("players", playerBuilder =>
                        playerBuilder
                            .SimpleFields("score", "kills", "deaths", "isWinner")
                            .Field("player", pBuilder =>
                                pBuilder.SimpleFields("id", "username")))
                    .Field("result", resultBuilder =>
                        resultBuilder.SimpleFields("winnerId", "duration", "stats"))
            );
        
        return GraphQLClient.Instance.Subscribe<MatchUpdatedResponse>(
            subscription.Build(),
            subscription.variables,
            (response) =>
            {
                OnMatchUpdated?.Invoke(response.matchUpdated);
                onUpdate?.Invoke(response.matchUpdated);
            },
            onError
        );
    }
    
    // Response wrapper classes
    [Serializable]
    private class PlayerDataResponse
    {
        public PlayerData player;
    }
    
    [Serializable]
    private class UpdatePlayerResponse
    {
        public PlayerData updatePlayerStats;
    }
    
    [Serializable]
    private class LeaderboardResponse
    {
        public LeaderboardData leaderboard;
    }
    
    [Serializable]
    private class LeaderboardData
    {
        public List<LeaderboardEntry> entries;
    }
    
    [Serializable]
    private class SubmitScoreResponse
    {
        public LeaderboardEntry submitScore;
    }
    
    [Serializable]
    private class CreateMatchResponse
    {
        public GameMatch createMatch;
    }
    
    [Serializable]
    private class PlayerUpdatedResponse
    {
        public PlayerData playerUpdated;
    }
    
    [Serializable]
    private class MatchUpdatedResponse
    {
        public GameMatch matchUpdated;
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### GraphQL Schema Analysis
```
PROMPT TEMPLATE - GraphQL Client Generation:

"Generate a complete Unity GraphQL client from this schema:

```graphql
[PASTE YOUR GRAPHQL SCHEMA]
```

Requirements:
- Unity Version: [2022.3 LTS/2023.2/etc.]
- Real-time Support: [WebSocket subscriptions needed/not needed]
- Caching Strategy: [Aggressive/Conservative/None]
- Type Safety: [Full code generation/Runtime validation/Basic]

Generate:
1. Complete GraphQL client with caching
2. Type-safe data models for all schema types
3. Query builder with fluent API
4. Subscription management for real-time updates
5. Error handling and retry logic
6. Performance optimization strategies
7. Usage examples for common operations
8. Unit tests for generated code"
```

### Query Optimization Analysis
```
PROMPT TEMPLATE - GraphQL Performance Optimization:

"Analyze and optimize these GraphQL queries for Unity:

```graphql
[PASTE YOUR QUERIES]
```

Current Performance Issues:
- Query Complexity: [High/Medium/Low]
- Network Latency: [High/Medium/Low]
- Mobile Device Performance: [Concern/Not a concern]
- Caching Requirements: [Aggressive/Selective/None]

Provide optimizations for:
1. Query complexity reduction and field selection
2. Fragment usage for code reuse
3. Batch query strategies
4. Caching implementation with invalidation
5. Subscription management and performance
6. Mobile-specific optimizations
7. Error handling and fallback strategies
8. Monitoring and performance metrics"
```

## 💡 Key GraphQL Integration Principles

### Essential GraphQL Checklist
- **Efficient queries** - Request only needed fields to minimize payload
- **Smart caching** - Cache responses with appropriate invalidation strategies
- **Error handling** - Handle both network and GraphQL errors gracefully
- **Type safety** - Use code generation or strong typing for data models
- **Real-time updates** - Implement subscriptions for live data when needed
- **Query optimization** - Use fragments and avoid N+1 query problems
- **Batch operations** - Group multiple queries to reduce network round trips
- **Performance monitoring** - Track query performance and optimization opportunities

### Common Unity GraphQL Challenges
1. **Complexity management** - GraphQL queries can become very complex
2. **Caching strategy** - Determining what and when to cache
3. **Real-time synchronization** - Managing subscription lifecycle
4. **Type safety** - Ensuring data integrity without compile-time checking
5. **Error handling** - Distinguishing between different error types
6. **Performance impact** - Large queries affecting mobile performance
7. **Schema evolution** - Handling backend changes gracefully
8. **Authentication** - Managing auth tokens in GraphQL context

This comprehensive GraphQL implementation provides Unity developers with a powerful, type-safe, and performant GraphQL client that supports queries, mutations, subscriptions, and advanced features like caching and batching while maintaining excellent mobile performance characteristics.