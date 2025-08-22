# @e-Unity-Database-Integration-Patterns - Game Data Architecture

## 🎯 Learning Objectives
- Design scalable database architectures for Unity multiplayer games
- Master SQL and NoSQL integration patterns with Unity C# code
- Implement efficient data synchronization and caching strategies
- Build AI-powered database optimization and query analysis systems

---

## 🔧 Unity Database Integration Architecture

### Comprehensive Database Manager

```csharp
using UnityEngine;
using System.Collections.Generic;
using System.Data;
using System.Threading.Tasks;
using Newtonsoft.Json;
using System;

/// <summary>
/// Universal database integration system for Unity games
/// Supports SQL Server, PostgreSQL, MySQL, MongoDB, and Firebase
/// </summary>
public class GameDatabaseManager : MonoBehaviour
{
    [System.Serializable]
    public class DatabaseConfiguration
    {
        public DatabaseType type = DatabaseType.PostgreSQL;
        public string connectionString;
        public int connectionPoolSize = 10;
        public int commandTimeout = 30;
        public bool enableCaching = true;
        public bool enableConnectionRetry = true;
        public int maxRetryAttempts = 3;
    }
    
    public enum DatabaseType
    {
        SQLServer,
        PostgreSQL,
        MySQL,
        MongoDB,
        Firebase,
        SQLite
    }
    
    [Header("Database Configuration")]
    [SerializeField] private DatabaseConfiguration primaryDb = new DatabaseConfiguration();
    [SerializeField] private DatabaseConfiguration readReplicaDb = new DatabaseConfiguration();
    [SerializeField] private bool useReadReplica = false;
    
    // Database providers
    private IDatabaseProvider primaryProvider;
    private IDatabaseProvider readProvider;
    private ICacheProvider cacheProvider;
    
    // Connection management
    private Dictionary<string, IDbConnection> connectionPool = new Dictionary<string, IDbConnection>();
    private Queue<string> availableConnections = new Queue<string>();
    
    void Awake()
    {
        InitializeDatabaseProviders();
        DontDestroyOnLoad(gameObject);
    }
    
    void InitializeDatabaseProviders()
    {
        // Initialize primary database
        primaryProvider = CreateDatabaseProvider(primaryDb);
        
        // Initialize read replica if configured
        if (useReadReplica)
        {
            readProvider = CreateDatabaseProvider(readReplicaDb);
        }
        else
        {
            readProvider = primaryProvider; // Use primary for reads too
        }
        
        // Initialize cache
        cacheProvider = new RedisCacheProvider("localhost:6379");
        
        Debug.Log($"Database manager initialized with {primaryDb.type}");
    }
    
    private IDatabaseProvider CreateDatabaseProvider(DatabaseConfiguration config)
    {
        switch (config.type)
        {
            case DatabaseType.PostgreSQL:
                return new PostgreSQLProvider(config);
            case DatabaseType.MySQL:
                return new MySQLProvider(config);
            case DatabaseType.SQLServer:
                return new SQLServerProvider(config);
            case DatabaseType.MongoDB:
                return new MongoDBProvider(config);
            case DatabaseType.Firebase:
                return new FirebaseProvider(config);
            case DatabaseType.SQLite:
                return new SQLiteProvider(config);
            default:
                throw new NotSupportedException($"Database type {config.type} not supported");
        }
    }
    
    // Player Data Operations
    public async Task<PlayerData> GetPlayerDataAsync(string playerId)
    {
        var cacheKey = $"player_data_{playerId}";
        
        // Try cache first
        if (primaryDb.enableCaching)
        {
            var cachedData = await cacheProvider.GetAsync<PlayerData>(cacheKey);
            if (cachedData != null)
            {
                return cachedData;
            }
        }
        
        // Query database
        var query = "SELECT * FROM players WHERE player_id = @playerId";
        var parameters = new Dictionary<string, object> { { "@playerId", playerId } };
        
        var playerData = await readProvider.QuerySingleAsync<PlayerData>(query, parameters);
        
        // Cache the result
        if (primaryDb.enableCaching && playerData != null)
        {
            await cacheProvider.SetAsync(cacheKey, playerData, TimeSpan.FromMinutes(15));
        }
        
        return playerData;
    }
    
    public async Task<bool> SavePlayerDataAsync(PlayerData playerData)
    {
        try
        {
            var query = @"
                INSERT INTO players (player_id, username, level, experience, coins, last_login)
                VALUES (@playerId, @username, @level, @experience, @coins, @lastLogin)
                ON CONFLICT (player_id) 
                DO UPDATE SET 
                    username = @username,
                    level = @level,
                    experience = @experience,
                    coins = @coins,
                    last_login = @lastLogin";
            
            var parameters = new Dictionary<string, object>
            {
                { "@playerId", playerData.playerId },
                { "@username", playerData.username },
                { "@level", playerData.level },
                { "@experience", playerData.experience },
                { "@coins", playerData.coins },
                { "@lastLogin", DateTime.Now }
            };
            
            await primaryProvider.ExecuteAsync(query, parameters);
            
            // Invalidate cache
            if (primaryDb.enableCaching)
            {
                var cacheKey = $"player_data_{playerData.playerId}";
                await cacheProvider.RemoveAsync(cacheKey);
            }
            
            return true;
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to save player data: {e.Message}");
            return false;
        }
    }
    
    // Leaderboard Operations
    public async Task<List<LeaderboardEntry>> GetLeaderboardAsync(string category, int limit = 100)
    {
        var cacheKey = $"leaderboard_{category}_{limit}";
        
        // Try cache first
        if (primaryDb.enableCaching)
        {
            var cachedData = await cacheProvider.GetAsync<List<LeaderboardEntry>>(cacheKey);
            if (cachedData != null)
            {
                return cachedData;
            }
        }
        
        var query = @"
            SELECT p.player_id, p.username, l.score, l.rank
            FROM leaderboards l
            JOIN players p ON l.player_id = p.player_id
            WHERE l.category = @category
            ORDER BY l.score DESC
            LIMIT @limit";
        
        var parameters = new Dictionary<string, object>
        {
            { "@category", category },
            { "@limit", limit }
        };
        
        var leaderboard = await readProvider.QueryAsync<LeaderboardEntry>(query, parameters);
        
        // Cache for 5 minutes
        if (primaryDb.enableCaching)
        {
            await cacheProvider.SetAsync(cacheKey, leaderboard, TimeSpan.FromMinutes(5));
        }
        
        return leaderboard;
    }
    
    public async Task UpdatePlayerScoreAsync(string playerId, string category, int score)
    {
        var query = @"
            INSERT INTO leaderboards (player_id, category, score, timestamp)
            VALUES (@playerId, @category, @score, @timestamp)
            ON CONFLICT (player_id, category)
            DO UPDATE SET 
                score = GREATEST(leaderboards.score, @score),
                timestamp = @timestamp";
        
        var parameters = new Dictionary<string, object>
        {
            { "@playerId", playerId },
            { "@category", category },
            { "@score", score },
            { "@timestamp", DateTime.Now }
        };
        
        await primaryProvider.ExecuteAsync(query, parameters);
        
        // Invalidate leaderboard cache
        var cachePattern = $"leaderboard_{category}_*";
        await cacheProvider.RemoveByPatternAsync(cachePattern);
    }
}

/// <summary>
/// PostgreSQL database provider implementation
/// Optimized for Unity game development with connection pooling and async operations
/// </summary>
public class PostgreSQLProvider : IDatabaseProvider
{
    private string connectionString;
    private DatabaseConfiguration config;
    
    public PostgreSQLProvider(DatabaseConfiguration configuration)
    {
        config = configuration;
        connectionString = configuration.connectionString;
    }
    
    public async Task<T> QuerySingleAsync<T>(string query, Dictionary<string, object> parameters = null) where T : class, new()
    {
        using (var connection = await CreateConnectionAsync())
        {
            using (var command = CreateCommand(query, parameters, connection))
            {
                using (var reader = await command.ExecuteReaderAsync())
                {
                    if (await reader.ReadAsync())
                    {
                        return MapToObject<T>(reader);
                    }
                }
            }
        }
        
        return null;
    }
    
    public async Task<List<T>> QueryAsync<T>(string query, Dictionary<string, object> parameters = null) where T : class, new()
    {
        var results = new List<T>();
        
        using (var connection = await CreateConnectionAsync())
        {
            using (var command = CreateCommand(query, parameters, connection))
            {
                using (var reader = await command.ExecuteReaderAsync())
                {
                    while (await reader.ReadAsync())
                    {
                        results.Add(MapToObject<T>(reader));
                    }
                }
            }
        }
        
        return results;
    }
    
    public async Task<int> ExecuteAsync(string query, Dictionary<string, object> parameters = null)
    {
        using (var connection = await CreateConnectionAsync())
        {
            using (var command = CreateCommand(query, parameters, connection))
            {
                return await command.ExecuteNonQueryAsync();
            }
        }
    }
    
    private async Task<IDbConnection> CreateConnectionAsync()
    {
        var connection = new Npgsql.NpgsqlConnection(connectionString);
        await connection.OpenAsync();
        return connection;
    }
    
    private IDbCommand CreateCommand(string query, Dictionary<string, object> parameters, IDbConnection connection)
    {
        var command = connection.CreateCommand();
        command.CommandText = query;
        command.CommandTimeout = config.commandTimeout;
        
        if (parameters != null)
        {
            foreach (var param in parameters)
            {
                var dbParam = command.CreateParameter();
                dbParam.ParameterName = param.Key;
                dbParam.Value = param.Value ?? DBNull.Value;
                command.Parameters.Add(dbParam);
            }
        }
        
        return command;
    }
    
    private T MapToObject<T>(IDataReader reader) where T : class, new()
    {
        var obj = new T();
        var properties = typeof(T).GetProperties();
        
        foreach (var property in properties)
        {
            var columnName = GetColumnName(property.Name);
            
            if (HasColumn(reader, columnName))
            {
                var value = reader[columnName];
                if (value != DBNull.Value)
                {
                    if (property.PropertyType == typeof(DateTime) && value is string dateStr)
                    {
                        if (DateTime.TryParse(dateStr, out var date))
                            property.SetValue(obj, date);
                    }
                    else
                    {
                        property.SetValue(obj, Convert.ChangeType(value, property.PropertyType));
                    }
                }
            }
        }
        
        return obj;
    }
    
    private string GetColumnName(string propertyName)
    {
        // Convert PascalCase to snake_case for PostgreSQL convention
        return string.Concat(propertyName.Select((x, i) => i > 0 && char.IsUpper(x) ? "_" + x.ToString() : x.ToString())).ToLower();
    }
    
    private bool HasColumn(IDataReader reader, string columnName)
    {
        try
        {
            return reader.GetOrdinal(columnName) >= 0;
        }
        catch
        {
            return false;
        }
    }
}

/// <summary>
/// MongoDB provider for flexible document storage
/// Ideal for player inventories, game configurations, and analytics data
/// </summary>
public class MongoDBProvider : IDatabaseProvider
{
    private MongoDB.Driver.MongoClient client;
    private MongoDB.Driver.IMongoDatabase database;
    
    public MongoDBProvider(DatabaseConfiguration config)
    {
        client = new MongoDB.Driver.MongoClient(config.connectionString);
        database = client.GetDatabase("game_database");
    }
    
    public async Task<T> QuerySingleAsync<T>(string collectionName, Dictionary<string, object> filter = null) where T : class
    {
        var collection = database.GetCollection<T>(collectionName);
        var filterDefinition = CreateFilterDefinition<T>(filter);
        
        using (var cursor = await collection.FindAsync(filterDefinition))
        {
            return await cursor.FirstOrDefaultAsync();
        }
    }
    
    public async Task<List<T>> QueryAsync<T>(string collectionName, Dictionary<string, object> filter = null, int limit = 1000) where T : class
    {
        var collection = database.GetCollection<T>(collectionName);
        var filterDefinition = CreateFilterDefinition<T>(filter);
        
        using (var cursor = await collection.FindAsync(filterDefinition, new MongoDB.Driver.FindOptions<T> { Limit = limit }))
        {
            return await cursor.ToListAsync();
        }
    }
    
    public async Task<bool> InsertAsync<T>(string collectionName, T document) where T : class
    {
        try
        {
            var collection = database.GetCollection<T>(collectionName);
            await collection.InsertOneAsync(document);
            return true;
        }
        catch (Exception e)
        {
            Debug.LogError($"MongoDB insert failed: {e.Message}");
            return false;
        }
    }
    
    public async Task<bool> UpdateAsync<T>(string collectionName, Dictionary<string, object> filter, T document) where T : class
    {
        try
        {
            var collection = database.GetCollection<T>(collectionName);
            var filterDefinition = CreateFilterDefinition<T>(filter);
            
            var result = await collection.ReplaceOneAsync(filterDefinition, document);
            return result.ModifiedCount > 0;
        }
        catch (Exception e)
        {
            Debug.LogError($"MongoDB update failed: {e.Message}");
            return false;
        }
    }
    
    private MongoDB.Driver.FilterDefinition<T> CreateFilterDefinition<T>(Dictionary<string, object> filter)
    {
        if (filter == null || filter.Count == 0)
            return MongoDB.Driver.Builders<T>.Filter.Empty;
        
        var filterBuilder = MongoDB.Driver.Builders<T>.Filter;
        var filters = new List<MongoDB.Driver.FilterDefinition<T>>();
        
        foreach (var kvp in filter)
        {
            filters.Add(filterBuilder.Eq(kvp.Key, kvp.Value));
        }
        
        return filterBuilder.And(filters);
    }
}

/// <summary>
/// Redis cache provider for high-performance data caching
/// Essential for multiplayer games and real-time features
/// </summary>
public class RedisCacheProvider : ICacheProvider
{
    private StackExchange.Redis.ConnectionMultiplexer redis;
    private StackExchange.Redis.IDatabase database;
    
    public RedisCacheProvider(string connectionString)
    {
        redis = StackExchange.Redis.ConnectionMultiplexer.Connect(connectionString);
        database = redis.GetDatabase();
    }
    
    public async Task<T> GetAsync<T>(string key) where T : class
    {
        try
        {
            var value = await database.StringGetAsync(key);
            if (value.HasValue)
            {
                return JsonConvert.DeserializeObject<T>(value);
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"Redis get failed for key {key}: {e.Message}");
        }
        
        return null;
    }
    
    public async Task<bool> SetAsync<T>(string key, T value, TimeSpan expiration) where T : class
    {
        try
        {
            var serializedValue = JsonConvert.SerializeObject(value);
            return await database.StringSetAsync(key, serializedValue, expiration);
        }
        catch (Exception e)
        {
            Debug.LogError($"Redis set failed for key {key}: {e.Message}");
            return false;
        }
    }
    
    public async Task<bool> RemoveAsync(string key)
    {
        try
        {
            return await database.KeyDeleteAsync(key);
        }
        catch (Exception e)
        {
            Debug.LogError($"Redis remove failed for key {key}: {e.Message}");
            return false;
        }
    }
    
    public async Task RemoveByPatternAsync(string pattern)
    {
        try
        {
            var server = redis.GetServer(redis.GetEndPoints().First());
            var keys = server.Keys(pattern: pattern);
            
            foreach (var key in keys)
            {
                await database.KeyDeleteAsync(key);
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"Redis pattern remove failed for pattern {pattern}: {e.Message}");
        }
    }
}
```

---

## 🚀 AI/LLM Integration Opportunities

### Intelligent Query Optimization

**Database Optimization Prompt:**
> "Analyze these Unity game database queries and suggest optimizations. Consider indexing strategies, query performance, data modeling improvements, and caching strategies. Focus on multiplayer game scenarios with high concurrent users."

### AI-Powered Data Analytics

```csharp
/// <summary>
/// AI-enhanced database analytics system for Unity games
/// Provides intelligent insights into player behavior and game performance
/// </summary>
public class DatabaseAnalyticsAI : MonoBehaviour
{
    private GameDatabaseManager dbManager;
    
    [System.Serializable]
    public class PlayerAnalytics
    {
        public string playerId;
        public float sessionDuration;
        public int actionsPerMinute;
        public float spendingPattern;
        public string[] preferredFeatures;
        public float churnRisk;
        public string playerSegment;
    }
    
    void Start()
    {
        dbManager = FindObjectOfType<GameDatabaseManager>();
    }
    
    public async Task<PlayerAnalytics> GeneratePlayerAnalytics(string playerId)
    {
        // Gather comprehensive player data
        var playerData = await dbManager.GetPlayerDataAsync(playerId);
        var sessionData = await GetPlayerSessionData(playerId);
        var purchaseData = await GetPlayerPurchaseData(playerId);
        var behaviorData = await GetPlayerBehaviorData(playerId);
        
        // AI analysis prompt
        var analysisPrompt = GenerateAnalyticsPrompt(playerData, sessionData, purchaseData, behaviorData);
        
        // Call AI service for analysis
        var aiInsights = await CallAnalyticsAI(analysisPrompt);
        
        return new PlayerAnalytics
        {
            playerId = playerId,
            sessionDuration = CalculateAverageSessionDuration(sessionData),
            actionsPerMinute = CalculateActionsPerMinute(behaviorData),
            spendingPattern = AnalyzeSpendingPattern(purchaseData),
            preferredFeatures = aiInsights.preferredFeatures,
            churnRisk = aiInsights.churnRisk,
            playerSegment = aiInsights.segment
        };
    }
    
    private string GenerateAnalyticsPrompt(object playerData, object sessionData, object purchaseData, object behaviorData)
    {
        return $@"
        Analyze this player's game data for behavioral insights:
        
        Player Profile: {JsonConvert.SerializeObject(playerData)}
        Session Data: {JsonConvert.SerializeObject(sessionData)}
        Purchase History: {JsonConvert.SerializeObject(purchaseData)}
        Behavior Patterns: {JsonConvert.SerializeObject(behaviorData)}
        
        Provide analysis for:
        1. Player segment classification (casual, core, hardcore)
        2. Churn risk assessment (0-1 scale)
        3. Preferred game features and content
        4. Monetization opportunities
        5. Engagement optimization recommendations
        
        Return structured JSON response.
        ";
    }
    
    public async Task OptimizeDatabasePerformance()
    {
        // Gather database performance metrics
        var performanceMetrics = await GatherDatabaseMetrics();
        
        // AI optimization analysis
        var optimizationPrompt = $@"
        Analyze database performance metrics for Unity multiplayer game:
        
        Metrics: {JsonConvert.SerializeObject(performanceMetrics)}
        
        Suggest:
        1. Index optimization strategies
        2. Query performance improvements
        3. Connection pool adjustments
        4. Caching strategy enhancements
        5. Database schema optimizations
        
        Focus on scalability for 10,000+ concurrent players.
        ";
        
        var optimizations = await CallOptimizationAI(optimizationPrompt);
        await ApplyDatabaseOptimizations(optimizations);
    }
}
```

---

## 💡 Key Database Integration Strategies

### Performance Optimization Patterns
- **Connection Pooling**: Efficient database connection management
- **Read Replicas**: Separate read and write operations for scalability
- **Caching Layer**: Redis for frequently accessed data
- **Query Optimization**: Indexed queries and batch operations

### Data Architecture Design
- **Player Data**: Relational database for structured player information
- **Game State**: NoSQL for flexible game state and inventory data
- **Analytics**: Time-series database for game events and metrics
- **Real-time**: In-memory cache for live game sessions

### Scalability Considerations
1. **Horizontal Sharding**: Distribute data across multiple database instances
2. **Vertical Partitioning**: Separate tables by access patterns
3. **Async Operations**: Non-blocking database calls in Unity
4. **Data Consistency**: ACID compliance for critical transactions

### AI-Enhanced Database Management
- **Query Optimization**: AI-suggested index and query improvements
- **Performance Monitoring**: Automated bottleneck detection and resolution
- **Predictive Scaling**: AI-predicted database resource requirements
- **Data Analytics**: Intelligent player behavior and game performance insights

This comprehensive database system provides enterprise-grade data management for Unity multiplayer games with AI-powered optimization and analytics capabilities.