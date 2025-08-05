# @c-NoSQL-Gaming-Databases

## 🎯 Learning Objectives
- Master NoSQL database selection for Unity game development
- Implement MongoDB for flexible game data storage
- Design Redis caching strategies for real-time gaming
- Understand document-based player profile management

## 🔧 MongoDB for Unity Games

### Connection and Configuration
```csharp
// MongoDB Driver for Unity
using MongoDB.Driver;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;
using UnityEngine;

public class MongoDBManager : MonoBehaviour
{
    private IMongoClient mongoClient;
    private IMongoDatabase database;
    private IMongoCollection<Player> playersCollection;
    
    [SerializeField] private string connectionString = "mongodb://localhost:27017";
    [SerializeField] private string databaseName = "UnityGameDB";
    
    void Start()
    {
        InitializeDatabase();
    }
    
    private async void InitializeDatabase()
    {
        try
        {
            mongoClient = new MongoClient(connectionString);
            database = mongoClient.GetDatabase(databaseName);
            playersCollection = database.GetCollection<Player>("players");
            
            Debug.Log("MongoDB connection established successfully");
            
            // Create indexes for performance
            await CreateIndexesAsync();
        }
        catch (Exception ex)
        {
            Debug.LogError($"MongoDB connection failed: {ex.Message}");
        }
    }
    
    private async Task CreateIndexesAsync()
    {
        // Username index for fast lookups
        await playersCollection.Indexes.CreateOneAsync(
            new CreateIndexModel<Player>(
                Builders<Player>.IndexKeys.Ascending(p => p.Username),
                new CreateIndexOptions { Unique = true }
            )
        );
        
        // Composite index for leaderboards
        await playersCollection.Indexes.CreateOneAsync(
            new CreateIndexModel<Player>(
                Builders<Player>.IndexKeys
                    .Descending(p => p.HighScore)
                    .Ascending(p => p.CompletionTime)
            )
        );
    }
}
```

### Document-Based Player Model
```csharp
// Flexible Player Document Structure
[BsonIgnoreExtraElements]
public class Player
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string Id { get; set; }
    
    [BsonElement("username")]
    public string Username { get; set; }
    
    [BsonElement("email")]
    public string Email { get; set; }
    
    [BsonElement("profile")]
    public PlayerProfile Profile { get; set; }
    
    [BsonElement("stats")]
    public PlayerStats Stats { get; set; }
    
    [BsonElement("inventory")]
    public List<InventoryItem> Inventory { get; set; }
    
    [BsonElement("achievements")]
    public List<Achievement> Achievements { get; set; }
    
    [BsonElement("settings")]
    public Dictionary<string, object> GameSettings { get; set; }
    
    [BsonElement("createdAt")]
    public DateTime CreatedAt { get; set; }
    
    [BsonElement("lastLoginAt")]
    public DateTime LastLoginAt { get; set; }
}

public class PlayerProfile
{
    [BsonElement("level")]
    public int Level { get; set; }
    
    [BsonElement("experience")]
    public long Experience { get; set; }
    
    [BsonElement("avatarUrl")]
    public string AvatarUrl { get; set; }
    
    [BsonElement("displayName")]
    public string DisplayName { get; set; }
    
    [BsonElement("guild")]
    public GuildInfo Guild { get; set; }
}

public class PlayerStats
{
    [BsonElement("gamesPlayed")]
    public int GamesPlayed { get; set; }
    
    [BsonElement("highScore")]
    public long HighScore { get; set; }
    
    [BsonElement("totalPlayTime")]
    public TimeSpan TotalPlayTime { get; set; }
    
    [BsonElement("winRate")]
    public double WinRate { get; set; }
    
    [BsonElement("achievements")]
    public Dictionary<string, int> AchievementCounts { get; set; }
    
    [BsonElement("skillRatings")]
    public Dictionary<string, double> SkillRatings { get; set; }
}
```

### Advanced MongoDB Operations
```csharp
// Complex Query Operations
public class PlayerRepository
{
    private readonly IMongoCollection<Player> _players;
    
    public PlayerRepository(IMongoDatabase database)
    {
        _players = database.GetCollection<Player>("players");
    }
    
    // Find players by complex criteria
    public async Task<List<Player>> FindPlayersAsync(PlayerSearchCriteria criteria)
    {
        var filterBuilder = Builders<Player>.Filter;
        var filters = new List<FilterDefinition<Player>>();
        
        if (!string.IsNullOrEmpty(criteria.Username))
        {
            filters.Add(filterBuilder.Regex(p => p.Username, 
                new BsonRegularExpression(criteria.Username, "i")));
        }
        
        if (criteria.MinLevel.HasValue)
        {
            filters.Add(filterBuilder.Gte(p => p.Profile.Level, criteria.MinLevel.Value));
        }
        
        if (criteria.Guild != null)
        {
            filters.Add(filterBuilder.Eq(p => p.Profile.Guild.Name, criteria.Guild));
        }
        
        var combinedFilter = filterBuilder.And(filters);
        
        return await _players.Find(combinedFilter)
            .Sort(Builders<Player>.Sort.Descending(p => p.Stats.HighScore))
            .Limit(criteria.Limit ?? 50)
            .ToListAsync();
    }
    
    // Aggregation Pipeline for Leaderboards
    public async Task<List<LeaderboardEntry>> GetLeaderboardAsync(
        string leaderboardType, int limit = 100)
    {
        var pipeline = new BsonDocument[]
        {
            new BsonDocument("$match", new BsonDocument
            {
                { "stats.gamesPlayed", new BsonDocument("$gte", 5) }
            }),
            new BsonDocument("$project", new BsonDocument
            {
                { "username", 1 },
                { "displayName", "$profile.displayName" },
                { "level", "$profile.level" },
                { "score", leaderboardType == "highScore" ? "$stats.highScore" : "$stats.winRate" },
                { "avatarUrl", "$profile.avatarUrl" }
            }),
            new BsonDocument("$sort", new BsonDocument("score", -1)),
            new BsonDocument("$limit", limit),
            new BsonDocument("$addFields", new BsonDocument
            {
                { "rank", new BsonDocument("$add", new BsonArray { "$rank", 1 }) }
            })
        };
        
        var result = await _players.Aggregate<LeaderboardEntry>(pipeline).ToListAsync();
        return result;
    }
    
    // Atomic Updates for Game Session End
    public async Task UpdatePlayerStatsAsync(string playerId, GameSessionResult result)
    {
        var filter = Builders<Player>.Filter.Eq(p => p.Id, playerId);
        var update = Builders<Player>.Update
            .Inc(p => p.Stats.GamesPlayed, 1)
            .Inc(p => p.Profile.Experience, result.ExperienceGained)
            .Max(p => p.Stats.HighScore, result.Score)
            .Set(p => p.LastLoginAt, DateTime.UtcNow);
        
        // Conditional level update
        if (result.LevelUp)
        {
            update = update.Inc(p => p.Profile.Level, 1);
        }
        
        await _players.UpdateOneAsync(filter, update);
    }
}
```

## 🔧 Redis for Real-time Gaming

### Unity Redis Integration
```csharp
// Redis Cache Manager for Unity
using StackExchange.Redis;
using Newtonsoft.Json;

public class RedisCacheManager : MonoBehaviour
{
    private ConnectionMultiplexer redis;
    private IDatabase database;
    
    [SerializeField] private string connectionString = "localhost:6379";
    
    void Start()
    {
        InitializeRedis();
    }
    
    private async void InitializeRedis()
    {
        try
        {
            redis = await ConnectionMultiplexer.ConnectAsync(connectionString);
            database = redis.GetDatabase();
            Debug.Log("Redis connection established successfully");
        }
        catch (Exception ex)
        {
            Debug.LogError($"Redis connection failed: {ex.Message}");
        }
    }
    
    // Generic cache operations
    public async Task SetAsync<T>(string key, T value, TimeSpan? expiry = null)
    {
        var serializedValue = JsonConvert.SerializeObject(value);
        await database.StringSetAsync(key, serializedValue, expiry);
    }
    
    public async Task<T> GetAsync<T>(string key)
    {
        var value = await database.StringGetAsync(key);
        if (value.HasValue)
        {
            return JsonConvert.DeserializeObject<T>(value);
        }
        return default(T);
    }
    
    // Real-time leaderboard with Redis Sorted Sets
    public async Task UpdateLeaderboardAsync(string leaderboardKey, string playerId, double score)
    {
        await database.SortedSetAddAsync(leaderboardKey, playerId, score);
        
        // Keep only top 1000 entries
        await database.SortedSetRemoveRangeByRankAsync(leaderboardKey, 0, -1001);
    }
    
    public async Task<List<LeaderboardEntry>> GetTopPlayersAsync(string leaderboardKey, int count = 10)
    {
        var entries = await database.SortedSetRangeByRankWithScoresAsync(
            leaderboardKey, 0, count - 1, Order.Descending);
        
        var leaderboard = new List<LeaderboardEntry>();
        int rank = 1;
        
        foreach (var entry in entries)
        {
            // Get player details from cache or database
            var playerInfo = await GetPlayerInfoAsync(entry.Element);
            leaderboard.Add(new LeaderboardEntry
            {
                Rank = rank++,
                PlayerId = entry.Element,
                PlayerName = playerInfo.Username,
                Score = (long)entry.Score
            });
        }
        
        return leaderboard;
    }
}
```

### Session Management with Redis
```csharp
// Game Session Management
public class GameSessionManager : MonoBehaviour
{
    private RedisCacheManager cacheManager;
    private const int SESSION_TIMEOUT_MINUTES = 30;
    
    void Start()
    {
        cacheManager = GetComponent<RedisCacheManager>();
    }
    
    public async Task<string> CreateGameSessionAsync(string playerId, string gameMode)
    {
        var sessionId = Guid.NewGuid().ToString();
        var session = new GameSession
        {
            SessionId = sessionId,
            PlayerId = playerId,
            GameMode = gameMode,
            StartTime = DateTime.UtcNow,
            Status = "ACTIVE",
            PlayerPosition = Vector3.zero,
            GameState = new Dictionary<string, object>()
        };
        
        var sessionKey = $"session:{sessionId}";
        await cacheManager.SetAsync(sessionKey, session, 
            TimeSpan.FromMinutes(SESSION_TIMEOUT_MINUTES));
        
        // Add to active sessions list
        await cacheManager.database.SetAddAsync($"active_sessions:{playerId}", sessionId);
        
        return sessionId;
    }
    
    public async Task UpdateSessionStateAsync(string sessionId, Dictionary<string, object> gameState)
    {
        var sessionKey = $"session:{sessionId}";
        var session = await cacheManager.GetAsync<GameSession>(sessionKey);
        
        if (session != null)
        {
            session.GameState = gameState;
            session.LastUpdated = DateTime.UtcNow;
            
            await cacheManager.SetAsync(sessionKey, session, 
                TimeSpan.FromMinutes(SESSION_TIMEOUT_MINUTES));
        }
    }
    
    // Real-time player position updates
    public async Task UpdatePlayerPositionAsync(string sessionId, Vector3 position, Quaternion rotation)
    {
        var positionKey = $"position:{sessionId}";
        var positionData = new PlayerPositionData
        {
            Position = position,
            Rotation = rotation,
            Timestamp = DateTime.UtcNow
        };
        
        await cacheManager.SetAsync(positionKey, positionData, TimeSpan.FromSeconds(10));
        
        // Publish to subscribers (other players in same game)
        var channel = $"game_updates:{GetGameRoomId(sessionId)}";
        await cacheManager.redis.GetSubscriber().PublishAsync(channel, 
            JsonConvert.SerializeObject(positionData));
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### NoSQL Schema Design
```
Prompt: "Design a MongoDB schema for a Unity battle royale game that tracks player matches, weapon statistics, map preferences, team formations, and seasonal rankings. Include aggregation pipelines for analytics."
```

### Redis Caching Strategy
```
Prompt: "Create a comprehensive Redis caching strategy for a Unity MMO game including player sessions, guild data, auction house items, chat messages, and real-time event notifications with appropriate TTL values."
```

### Database Migration Scripts
```
Prompt: "Generate MongoDB migration scripts to convert existing SQL Server game data to document-based structure, including data transformation for nested player inventories and achievement systems."
```

## 💡 Key Highlights

### NoSQL Database Selection
- **MongoDB**: Flexible schemas, complex queries, horizontal scaling
- **Redis**: In-memory speed, pub/sub messaging, atomic operations
- **Cassandra**: Write-heavy workloads, time-series data, high availability
- **DynamoDB**: AWS integration, automatic scaling, global distribution

### Performance Optimization
- **Indexing strategy**: Compound indexes for complex queries
- **Data modeling**: Embed vs reference based on access patterns
- **Sharding**: Horizontal partitioning for scale
- **Connection pooling**: Efficient resource utilization
- **Caching layers**: Multi-level caching with Redis

### Real-time Gaming Features
- **Session management**: Player state persistence
- **Leaderboards**: Sorted sets for rankings
- **Pub/Sub messaging**: Real-time updates
- **Geolocation**: Spatial queries for location-based games
- **Time-series data**: Player analytics and telemetry