# @b-GraphQL-Unity-Integration

## 🎯 Learning Objectives
- Implement GraphQL clients in Unity for efficient data fetching
- Master GraphQL queries, mutations, and subscriptions for game development
- Design flexible data schemas for multiplayer game backends
- Optimize GraphQL performance for real-time gaming scenarios

## 🔧 GraphQL Client Implementation

### Unity GraphQL Client Setup
```csharp
// Unity GraphQL Client
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;
using Newtonsoft.Json;
using System.Text;

public class GraphQLClient : MonoBehaviour
{
    [Header("GraphQL Configuration")]
    [SerializeField] private string graphqlEndpoint = "https://api.yourgame.com/graphql";
    [SerializeField] private string authToken;
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
            { "User-Agent", $"UnityGame/{Application.version}" }
        };
        
        if (!string.IsNullOrEmpty(authToken))
        {
            defaultHeaders["Authorization"] = $"Bearer {authToken}";
        }
    }
    
    public async Task<GraphQLResponse<T>> QueryAsync<T>(string query, object variables = null)
    {
        var request = new GraphQLRequest
        {
            Query = query,
            Variables = variables
        };
        
        return await SendRequestAsync<T>(request);
    }
    
    public async Task<GraphQLResponse<T>> MutateAsync<T>(string mutation, object variables = null)
    {
        var request = new GraphQLRequest
        {
            Query = mutation,
            Variables = variables
        };
        
        return await SendRequestAsync<T>(request);
    }
    
    private async Task<GraphQLResponse<T>> SendRequestAsync<T>(GraphQLRequest request)
    {
        var jsonRequest = JsonConvert.SerializeObject(request);
        var bodyData = Encoding.UTF8.GetBytes(jsonRequest);
        
        using (var webRequest = new UnityWebRequest(graphqlEndpoint, "POST"))
        {
            webRequest.uploadHandler = new UploadHandlerRaw(bodyData);
            webRequest.downloadHandler = new DownloadHandlerBuffer();
            webRequest.timeout = timeoutSeconds;
            
            // Add headers
            foreach (var header in defaultHeaders)
            {
                webRequest.SetRequestHeader(header.Key, header.Value);
            }
            
            var operation = webRequest.SendWebRequest();
            
            // Wait for completion
            while (!operation.isDone)
            {
                await Task.Yield();
            }
            
            return ProcessGraphQLResponse<T>(webRequest);
        }
    }
    
    private GraphQLResponse<T> ProcessGraphQLResponse<T>(UnityWebRequest webRequest)
    {
        var response = new GraphQLResponse<T>();
        
        if (webRequest.result == UnityWebRequest.Result.Success)
        {
            try
            {
                var responseText = webRequest.downloadHandler.text;
                var graphqlResponse = JsonConvert.DeserializeObject<GraphQLRawResponse>(responseText);
                
                if (graphqlResponse.Errors != null && graphqlResponse.Errors.Count > 0)
                {
                    response.Errors = graphqlResponse.Errors;
                    response.Success = false;
                }
                else
                {
                    response.Data = JsonConvert.DeserializeObject<T>(graphqlResponse.Data.ToString());
                    response.Success = true;
                }
            }
            catch (JsonException ex)
            {
                response.Success = false;
                response.Errors = new List<GraphQLError>
                {
                    new GraphQLError { Message = $"JSON parsing error: {ex.Message}" }
                };
            }
        }
        else
        {
            response.Success = false;
            response.Errors = new List<GraphQLError>
            {
                new GraphQLError { Message = webRequest.error ?? "Request failed" }
            };
        }
        
        return response;
    }
    
    public void SetAuthToken(string token)
    {
        authToken = token;
        if (!string.IsNullOrEmpty(token))
        {
            defaultHeaders["Authorization"] = $"Bearer {token}";
        }
        else
        {
            defaultHeaders.Remove("Authorization");
        }
    }
}
```

### Game-Specific GraphQL Queries
```csharp
// GraphQL Query Builder for Game Operations
public class GameGraphQLQueries
{
    // Get player with nested data
    public static string GetPlayerQuery = @"
        query GetPlayer($playerId: ID!) {
            player(id: $playerId) {
                id
                username
                email
                level
                experience
                createdAt
                lastLoginAt
                profile {
                    displayName
                    avatarUrl
                    bio
                    settings {
                        soundEnabled
                        musicVolume
                        language
                    }
                }
                stats {
                    gamesPlayed
                    gamesWon
                    totalPlayTime
                    highScore
                    achievements {
                        id
                        name
                        description
                        unlockedAt
                        rarity
                    }
                }
                inventory {
                    items {
                        id
                        itemId
                        quantity
                        acquiredAt
                        item {
                            name
                            description
                            rarity
                            category
                            iconUrl
                        }
                    }
                    currency {
                        type
                        amount
                    }
                }
            }
        }";
    
    // Get leaderboard with flexible filtering
    public static string GetLeaderboardQuery = @"
        query GetLeaderboard($gameMode: String!, $timeframe: TimeFrame!, $limit: Int = 100, $offset: Int = 0) {
            leaderboard(gameMode: $gameMode, timeframe: $timeframe, limit: $limit, offset: $offset) {
                entries {
                    rank
                    score
                    player {
                        id
                        username
                        profile {
                            displayName
                            avatarUrl
                        }
                        level
                    }
                    achievedAt
                }
                totalEntries
                hasMore
                timeframe
                lastUpdated
            }
        }";
    
    // Get multiple players with batch loading
    public static string GetPlayersQuery = @"
        query GetPlayers($playerIds: [ID!]!) {
            players(ids: $playerIds) {
                id
                username
                level
                profile {
                    displayName
                    avatarUrl
                }
                stats {
                    gamesPlayed
                    highScore
                }
                isOnline
                lastSeen
            }
        }";
    
    // Complex matchmaking query
    public static string FindMatchQuery = @"
        query FindMatch($gameMode: String!, $skillLevel: Int!, $region: String, $maxPlayers: Int = 4) {
            findMatch(
                gameMode: $gameMode
                skillLevel: $skillLevel
                region: $region
                maxPlayers: $maxPlayers
            ) {
                matchId
                gameMode
                players {
                    id
                    username
                    skillLevel
                    profile {
                        displayName
                        avatarUrl
                    }
                }
                gameSettings {
                    mapId
                    gameDuration
                    rules
                }
                estimatedStartTime
                serverRegion
            }
        }";
    
    // Guild/clan information with members
    public static string GetGuildQuery = @"
        query GetGuild($guildId: ID!) {
            guild(id: $guildId) {
                id
                name
                description
                tag
                level
                memberCount
                maxMembers
                createdAt
                leader {
                    id
                    username
                    profile {
                        displayName
                        avatarUrl
                    }
                }
                members(limit: 50) {
                    id
                    username
                    role
                    joinedAt
                    contribution
                    lastActive
                    profile {
                        displayName
                        avatarUrl
                        level
                    }
                }
                stats {
                    totalExperience
                    guildRank
                    weeklyActivity
                }
            }
        }";
}
```

### GraphQL Mutations for Game Actions
```csharp
// GraphQL Mutations for Game Operations
public class GameGraphQLMutations
{
    // Submit game score
    public static string SubmitScoreMutation = @"
        mutation SubmitScore($input: ScoreSubmissionInput!) {
            submitScore(input: $input) {
                success
                newPersonalBest
                newRank
                experienceGained
                achievementsUnlocked {
                    id
                    name
                    description
                    rarity
                }
                errors {
                    field
                    message
                }
            }
        }";
    
    // Update player profile
    public static string UpdatePlayerProfileMutation = @"
        mutation UpdatePlayerProfile($input: PlayerProfileUpdateInput!) {
            updatePlayerProfile(input: $input) {
                player {
                    id
                    profile {
                        displayName
                        bio
                        avatarUrl
                        settings {
                            soundEnabled
                            musicVolume
                            language
                        }
                    }
                }
                success
                errors {
                    field
                    message
                }
            }
        }";
    
    // Use inventory item
    public static string UseItemMutation = @"
        mutation UseItem($input: UseItemInput!) {
            useItem(input: $input) {
                success
                itemUsed {
                    id
                    quantity
                    item {
                        name
                        effects {
                            type
                            value
                            duration
                        }
                    }
                }
                playerEffects {
                    type
                    value
                    duration
                    appliedAt
                }
                updatedInventory {
                    items {
                        id
                        itemId
                        quantity
                    }
                }
                errors {
                    field
                    message
                }
            }
        }";
    
    // Join guild
    public static string JoinGuildMutation = @"
        mutation JoinGuild($guildId: ID!, $message: String) {
            joinGuild(guildId: $guildId, message: $message) {
                success
                membership {
                    guild {
                        id
                        name
                        tag
                    }
                    role
                    joinedAt
                }
                errors {
                    field
                    message
                }
            }
        }";
    
    // Start matchmaking
    public static string StartMatchmakingMutation = @"
        mutation StartMatchmaking($input: MatchmakingInput!) {
            startMatchmaking(input: $input) {
                success
                queueId
                estimatedWaitTime
                queuePosition
                gameMode
                skillRating
                errors {
                    field
                    message
                }
            }
        }";
}
```

## 🔧 GraphQL Service Integration

### Game API Service with GraphQL
```csharp
// Comprehensive Game API Service using GraphQL
public class GameGraphQLService : MonoBehaviour
{
    private GraphQLClient graphqlClient;
    private Dictionary<string, object> cachedQueries;
    
    [Header("Caching Settings")]
    [SerializeField] private bool enableQueryCaching = true;
    [SerializeField] private int cacheExpirationMinutes = 5;
    
    void Start()
    {
        graphqlClient = GetComponent<GraphQLClient>();
        cachedQueries = new Dictionary<string, object>();
    }
    
    // Player operations
    public async Task<PlayerData> GetPlayerAsync(string playerId, bool useCache = true)
    {
        var variables = new { playerId };
        var cacheKey = $"player_{playerId}";
        
        if (useCache && TryGetCachedResult<PlayerResponse>(cacheKey, out var cachedResult))
        {
            return cachedResult.Player;
        }
        
        var response = await graphqlClient.QueryAsync<PlayerResponse>(GameGraphQLQueries.GetPlayerQuery, variables);
        
        if (response.Success)
        {
            if (useCache)
            {
                CacheResult(cacheKey, response.Data);
            }
            return response.Data.Player;
        }
        else
        {
            HandleGraphQLErrors(response.Errors, "GetPlayer");
            return null;
        }
    }
    
    public async Task<List<PlayerData>> GetPlayersAsync(List<string> playerIds)
    {
        var variables = new { playerIds };
        
        var response = await graphqlClient.QueryAsync<PlayersResponse>(GameGraphQLQueries.GetPlayersQuery, variables);
        
        if (response.Success)
        {
            return response.Data.Players;
        }
        else
        {
            HandleGraphQLErrors(response.Errors, "GetPlayers");
            return new List<PlayerData>();
        }
    }
    
    // Leaderboard operations
    public async Task<LeaderboardData> GetLeaderboardAsync(string gameMode, string timeframe, int limit = 100, int offset = 0)
    {
        var variables = new { gameMode, timeframe, limit, offset };
        var cacheKey = $"leaderboard_{gameMode}_{timeframe}_{limit}_{offset}";
        
        if (TryGetCachedResult<LeaderboardResponse>(cacheKey, out var cachedResult))
        {
            return cachedResult.Leaderboard;
        }
        
        var response = await graphqlClient.QueryAsync<LeaderboardResponse>(GameGraphQLQueries.GetLeaderboardQuery, variables);
        
        if (response.Success)
        {
            CacheResult(cacheKey, response.Data);
            return response.Data.Leaderboard;
        }
        else
        {
            HandleGraphQLErrors(response.Errors, "GetLeaderboard");
            return null;
        }
    }
    
    // Score submission
    public async Task<ScoreSubmissionResult> SubmitScoreAsync(ScoreSubmissionInput input)
    {
        var variables = new { input };
        
        var response = await graphqlClient.MutateAsync<ScoreSubmissionResponse>(
            GameGraphQLMutations.SubmitScoreMutation, variables);
        
        if (response.Success)
        {
            var result = response.Data.SubmitScore;
            
            // Invalidate related caches
            InvalidatePlayerCache(input.PlayerId);
            InvalidateLeaderboardCache(input.GameMode);
            
            // Handle achievements unlocked
            if (result.AchievementsUnlocked?.Count > 0)
            {
                HandleAchievementsUnlocked(result.AchievementsUnlocked);
            }
            
            return result;
        }
        else
        {
            HandleGraphQLErrors(response.Errors, "SubmitScore");
            return null;
        }
    }
    
    // Profile update
    public async Task<PlayerData> UpdatePlayerProfileAsync(PlayerProfileUpdateInput input)
    {
        var variables = new { input };
        
        var response = await graphqlClient.MutateAsync<UpdatePlayerProfileResponse>(
            GameGraphQLMutations.UpdatePlayerProfileMutation, variables);
        
        if (response.Success)
        {
            // Invalidate player cache
            InvalidatePlayerCache(input.PlayerId);
            
            return response.Data.UpdatePlayerProfile.Player;
        }
        else
        {
            HandleGraphQLErrors(response.Errors, "UpdatePlayerProfile");
            return null;
        }
    }
    
    // Guild operations
    public async Task<GuildData> GetGuildAsync(string guildId)
    {
        var variables = new { guildId };
        var cacheKey = $"guild_{guildId}";
        
        if (TryGetCachedResult<GuildResponse>(cacheKey, out var cachedResult))
        {
            return cachedResult.Guild;
        }
        
        var response = await graphqlClient.QueryAsync<GuildResponse>(GameGraphQLQueries.GetGuildQuery, variables);
        
        if (response.Success)
        {
            CacheResult(cacheKey, response.Data);
            return response.Data.Guild;
        }
        else
        {
            HandleGraphQLErrors(response.Errors, "GetGuild");
            return null;
        }
    }
    
    // Matchmaking
    public async Task<MatchmakingResult> StartMatchmakingAsync(MatchmakingInput input)
    {
        var variables = new { input };
        
        var response = await graphqlClient.MutateAsync<StartMatchmakingResponse>(
            GameGraphQLMutations.StartMatchmakingMutation, variables);
        
        if (response.Success)
        {
            return response.Data.StartMatchmaking;
        }
        else
        {
            HandleGraphQLErrors(response.Errors, "StartMatchmaking");
            return null;
        }
    }
    
    // Cache management
    private bool TryGetCachedResult<T>(string cacheKey, out T result)
    {
        result = default(T);
        
        if (!enableQueryCaching || !cachedQueries.ContainsKey(cacheKey))
            return false;
            
        var cacheEntry = cachedQueries[cacheKey] as CacheEntry<T>;
        if (cacheEntry == null || cacheEntry.IsExpired)
        {
            cachedQueries.Remove(cacheKey);
            return false;
        }
        
        result = cacheEntry.Data;
        return true;
    }
    
    private void CacheResult<T>(string cacheKey, T data)
    {
        if (!enableQueryCaching) return;
        
        cachedQueries[cacheKey] = new CacheEntry<T>
        {
            Data = data,
            ExpirationTime = DateTime.UtcNow.AddMinutes(cacheExpirationMinutes)
        };
    }
    
    private void InvalidatePlayerCache(string playerId)
    {
        var keysToRemove = cachedQueries.Keys
            .Where(key => key.StartsWith($"player_{playerId}"))
            .ToList();
            
        foreach (var key in keysToRemove)
        {
            cachedQueries.Remove(key);
        }
    }
    
    private void InvalidateLeaderboardCache(string gameMode)
    {
        var keysToRemove = cachedQueries.Keys
            .Where(key => key.StartsWith($"leaderboard_{gameMode}"))
            .ToList();
            
        foreach (var key in keysToRemove)
        {
            cachedQueries.Remove(key);
        }
    }
    
    private void HandleGraphQLErrors(List<GraphQLError> errors, string operation)
    {
        foreach (var error in errors)
        {
            Debug.LogError($"GraphQL Error in {operation}: {error.Message}");
            
            // Handle specific error types
            if (error.Extensions?.ContainsKey("code") == true)
            {
                var errorCode = error.Extensions["code"].ToString();
                HandleSpecificError(errorCode, error.Message, operation);
            }
        }
        
        // Send to analytics
        AnalyticsManager.Instance.TrackGraphQLError(operation, errors);
    }
    
    private void HandleSpecificError(string errorCode, string message, string operation)
    {
        switch (errorCode)
        {
            case "UNAUTHENTICATED":
                GameManager.Instance.ReturnToLogin();
                break;
            case "FORBIDDEN":
                UIManager.Instance.ShowMessage("You don't have permission to perform this action.", MessageType.Error);
                break;
            case "RATE_LIMITED":
                UIManager.Instance.ShowMessage("Too many requests. Please wait before trying again.", MessageType.Warning);
                break;
            case "VALIDATION_ERROR":
                UIManager.Instance.ShowMessage($"Invalid input: {message}", MessageType.Error);
                break;
        }
    }
    
    private void HandleAchievementsUnlocked(List<AchievementData> achievements)
    {
        foreach (var achievement in achievements)
        {
            UIManager.Instance.ShowAchievementUnlocked(achievement);
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### GraphQL Schema Generation
```
Prompt: "Generate a comprehensive GraphQL schema for a Unity MMO game including player management, guild systems, inventory, achievements, leaderboards, matchmaking, and real-time chat with appropriate types, queries, mutations, and subscriptions."
```

### Query Optimization Analysis
```
Prompt: "Analyze these GraphQL queries for a Unity game and suggest optimizations for reducing over-fetching, implementing proper batching, and improving performance for mobile clients: [paste queries]"
```

### GraphQL Client Generation
```
Prompt: "Generate a strongly-typed Unity C# GraphQL client from this schema with automatic query building, response caching, error handling, and subscription support: [paste GraphQL schema]"
```

## 💡 Key Highlights

### GraphQL Advantages for Games
- **Flexible data fetching**: Request exactly the data needed, reducing bandwidth
- **Single endpoint**: Simplifies API management and versioning
- **Strong typing**: Schema-driven development with compile-time validation
- **Real-time subscriptions**: Live updates for multiplayer features
- **Efficient batching**: Combine multiple requests into single network call

### Unity-Specific Considerations
- **Async/await patterns**: Non-blocking GraphQL operations
- **Error handling**: Graceful handling of partial failures and network issues
- **Caching strategies**: Reduce redundant queries and improve performance
- **Authentication integration**: Token-based auth with GraphQL requests
- **Offline support**: Cache GraphQL responses for offline gameplay

### Performance Optimization
- **Query complexity analysis**: Prevent expensive queries from impacting server performance
- **Dataloader pattern**: Batch and cache database queries on server
- **Response compression**: Reduce network payload size
- **Field-level caching**: Cache individual fields based on their volatility
- **Subscription management**: Efficient real-time update delivery