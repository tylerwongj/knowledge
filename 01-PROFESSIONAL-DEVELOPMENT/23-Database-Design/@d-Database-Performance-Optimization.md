# @d-Database-Performance-Optimization

## 🎯 Learning Objectives
- Master database indexing strategies for Unity game databases
- Implement query optimization techniques for real-time gaming
- Design efficient caching layers for multiplayer game performance
- Monitor and tune database performance for scaling Unity games

## 🔧 Query Optimization Fundamentals

### Index Design for Gaming Workloads
```sql
-- Player Lookup Optimization
CREATE INDEX IX_Players_Username_Active 
ON Players (Username) 
WHERE IsActive = 1
INCLUDE (PlayerId, Email, LastLoginDate);

-- Composite Index for Leaderboards
CREATE INDEX IX_PlayerStats_Leaderboard 
ON PlayerStats (GameMode, Score DESC, CompletionTime ASC)
INCLUDE (PlayerId, PlayerName, AchievedDate);

-- Covering Index for Inventory Queries
CREATE INDEX IX_PlayerInventory_Lookup
ON PlayerInventory (PlayerId, ItemType)
INCLUDE (ItemId, Quantity, LastUpdated, IsEquipped);

-- Partial Index for Active Sessions
CREATE INDEX IX_GameSessions_Active
ON GameSessions (PlayerId, StartTime DESC)
WHERE EndTime IS NULL
INCLUDE (SessionId, GameMode, CurrentLevel);
```

### Query Performance Analysis
```sql
-- Unity Game Analytics Query Optimization
WITH PlayerActivity AS (
    SELECT 
        p.PlayerId,
        p.Username,
        COUNT(gs.SessionId) as SessionCount,
        AVG(DATEDIFF(MINUTE, gs.StartTime, gs.EndTime)) as AvgSessionMinutes,
        MAX(ps.HighScore) as BestScore,
        ROW_NUMBER() OVER (ORDER BY MAX(ps.HighScore) DESC) as ScoreRank
    FROM Players p
    LEFT JOIN GameSessions gs ON p.PlayerId = gs.PlayerId
    LEFT JOIN PlayerStats ps ON p.PlayerId = ps.PlayerId
    WHERE p.LastLoginDate >= DATEADD(DAY, -30, GETUTCDATE())
    GROUP BY p.PlayerId, p.Username
),
RetentionMetrics AS (
    SELECT 
        PlayerId,
        COUNT(DISTINCT CAST(StartTime AS DATE)) as ActiveDays,
        DATEDIFF(DAY, MIN(StartTime), MAX(StartTime)) + 1 as SpanDays
    FROM GameSessions
    WHERE StartTime >= DATEADD(DAY, -30, GETUTCDATE())
    GROUP BY PlayerId
)
SELECT 
    pa.Username,
    pa.SessionCount,
    pa.AvgSessionMinutes,
    pa.BestScore,
    pa.ScoreRank,
    rm.ActiveDays,
    CAST(rm.ActiveDays AS FLOAT) / rm.SpanDays as RetentionRate
FROM PlayerActivity pa
JOIN RetentionMetrics rm ON pa.PlayerId = rm.PlayerId
WHERE pa.SessionCount >= 5
ORDER BY pa.ScoreRank;
```

### Execution Plan Optimization
```csharp
// Unity Database Query Profiler
using System.Data.SqlClient;
using System.Diagnostics;

public class QueryProfiler : MonoBehaviour
{
    private SqlConnection connection;
    
    public async Task<QueryResult<T>> ExecuteOptimizedQuery<T>(
        string query, 
        object parameters, 
        bool enableProfiling = false)
    {
        var stopwatch = Stopwatch.StartNew();
        var result = new QueryResult<T>();
        
        try
        {
            if (enableProfiling)
            {
                // Enable execution plan capture
                await ExecuteAsync("SET STATISTICS IO ON");
                await ExecuteAsync("SET STATISTICS TIME ON");
            }
            
            using var command = new SqlCommand(query, connection);
            AddParameters(command, parameters);
            
            // Execute with timeout monitoring
            var timeout = Task.Delay(TimeSpan.FromSeconds(30));
            var execution = ExecuteQueryAsync<T>(command);
            
            var completedTask = await Task.WhenAny(execution, timeout);
            
            if (completedTask == timeout)
            {
                throw new TimeoutException($"Query exceeded 30 second timeout: {query}");
            }
            
            result.Data = await execution;
            result.ExecutionTime = stopwatch.Elapsed;
            result.Success = true;
            
            if (enableProfiling)
            {
                result.ExecutionPlan = await GetExecutionPlanAsync(query);
                LogPerformanceMetrics(query, result);
            }
        }
        catch (Exception ex)
        {
            result.Success = false;
            result.ErrorMessage = ex.Message;
            Debug.LogError($"Query failed: {query} - {ex.Message}");
        }
        finally
        {
            stopwatch.Stop();
        }
        
        return result;
    }
    
    private void LogPerformanceMetrics(string query, QueryResult result)
    {
        if (result.ExecutionTime.TotalMilliseconds > 1000)
        {
            Debug.LogWarning($"Slow query detected ({result.ExecutionTime.TotalMilliseconds}ms): {query}");
            
            // Send to analytics for monitoring
            AnalyticsManager.Instance.TrackSlowQuery(query, result.ExecutionTime);
        }
    }
}
```

## 🔧 Caching Strategies for Unity Games

### Multi-Level Caching Architecture
```csharp
// Hierarchical Caching System
public class GameDataCache : MonoBehaviour
{
    private MemoryCache localCache;           // L1: In-memory cache
    private RedisCacheManager distributedCache; // L2: Redis distributed cache
    private DatabaseManager database;          // L3: Database
    
    void Start()
    {
        localCache = new MemoryCache(new MemoryCacheOptions
        {
            SizeLimit = 1000,
            ExpirationScanFrequency = TimeSpan.FromMinutes(5)
        });
        
        distributedCache = GetComponent<RedisCacheManager>();
        database = GetComponent<DatabaseManager>();
    }
    
    public async Task<Player> GetPlayerAsync(string playerId)
    {
        // L1 Cache Check
        var cacheKey = $"player:{playerId}";
        if (localCache.TryGetValue(cacheKey, out Player cachedPlayer))
        {
            AnalyticsManager.Instance.TrackCacheHit("L1", "player");
            return cachedPlayer;
        }
        
        // L2 Cache Check (Redis)
        var redisPlayer = await distributedCache.GetAsync<Player>(cacheKey);
        if (redisPlayer != null)
        {
            // Store in L1 cache for faster subsequent access
            localCache.Set(cacheKey, redisPlayer, TimeSpan.FromMinutes(5));
            AnalyticsManager.Instance.TrackCacheHit("L2", "player");
            return redisPlayer;
        }
        
        // L3 Database Query
        var dbPlayer = await database.GetPlayerAsync(playerId);
        if (dbPlayer != null)
        {
            // Cache in both levels
            await distributedCache.SetAsync(cacheKey, dbPlayer, TimeSpan.FromMinutes(30));
            localCache.Set(cacheKey, dbPlayer, TimeSpan.FromMinutes(5));
            AnalyticsManager.Instance.TrackCacheMiss("player");
        }
        
        return dbPlayer;
    }
    
    // Smart cache invalidation
    public async Task InvalidatePlayerCacheAsync(string playerId)
    {
        var cacheKey = $"player:{playerId}";
        
        // Remove from all cache levels
        localCache.Remove(cacheKey);
        await distributedCache.RemoveAsync(cacheKey);
        
        // Invalidate related caches
        await InvalidateLeaderboardCacheAsync();
        await InvalidateGuildCacheAsync(playerId);
    }
}
```

### Cache-Aside Pattern Implementation
```csharp
// Leaderboard Caching with Write-Through
public class LeaderboardService : MonoBehaviour
{
    private GameDataCache cache;
    private DatabaseManager database;
    
    public async Task<List<LeaderboardEntry>> GetLeaderboardAsync(
        string gameMode, int limit = 100)
    {
        var cacheKey = $"leaderboard:{gameMode}:{limit}";
        
        // Try cache first
        var cachedLeaderboard = await cache.GetAsync<List<LeaderboardEntry>>(cacheKey);
        if (cachedLeaderboard != null && cachedLeaderboard.Any())
        {
            return cachedLeaderboard;
        }
        
        // Generate from database
        var leaderboard = await GenerateLeaderboardFromDatabase(gameMode, limit);
        
        // Cache with shorter TTL for frequently changing data
        await cache.SetAsync(cacheKey, leaderboard, TimeSpan.FromMinutes(2));
        
        return leaderboard;
    }
    
    public async Task UpdatePlayerScoreAsync(string playerId, string gameMode, long score)
    {
        // Update database first (write-through)
        await database.UpdatePlayerScoreAsync(playerId, gameMode, score);
        
        // Invalidate affected caches
        await InvalidateLeaderboardCaches(gameMode);
        await cache.InvalidatePlayerCacheAsync(playerId);
        
        // Optionally, precompute and cache new leaderboard
        _ = Task.Run(async () =>
        {
            await GetLeaderboardAsync(gameMode); // Warm the cache
        });
    }
    
    private async Task InvalidateLeaderboardCaches(string gameMode)
    {
        var patterns = new[]
        {
            $"leaderboard:{gameMode}:*",
            "leaderboard:global:*",
            $"player_rank:{gameMode}:*"
        };
        
        foreach (var pattern in patterns)
        {
            await cache.RemoveByPatternAsync(pattern);
        }
    }
}
```

## 🔧 Database Connection Optimization

### Connection Pool Management
```csharp
// Optimized Connection Pool Configuration
public class OptimizedDatabaseManager : MonoBehaviour
{
    private readonly string connectionString;
    
    public OptimizedDatabaseManager()
    {
        var builder = new SqlConnectionStringBuilder
        {
            DataSource = "your-server.database.windows.net",
            InitialCatalog = "UnityGameDB",
            UserID = "gameuser",
            Password = "SecurePassword123!",
            
            // Connection Pool Optimization
            MinPoolSize = 5,           // Minimum connections
            MaxPoolSize = 100,         // Maximum connections  
            Pooling = true,
            ConnectionTimeout = 30,    // Connection timeout
            CommandTimeout = 120,      // Command timeout
            
            // Performance Settings
            MultipleActiveResultSets = true,  // Enable MARS
            Encrypt = true,
            TrustServerCertificate = false,
            ApplicationName = "UnityGame",
            
            // Advanced Settings
            LoadBalanceTimeout = 0,    // Disable load balancing timeout
            PacketSize = 8192,         // Network packet size
            ConnectRetryCount = 3,     // Auto-retry on connection failure
            ConnectRetryInterval = 10   // Retry interval in seconds
        };
        
        connectionString = builder.ConnectionString;
    }
    
    // Connection health monitoring
    public async Task<bool> TestConnectionHealthAsync()
    {
        try
        {
            using var connection = new SqlConnection(connectionString);
            await connection.OpenAsync();
            
            using var command = new SqlCommand("SELECT 1", connection);
            var result = await command.ExecuteScalarAsync();
            
            return result?.ToString() == "1";
        }
        catch (Exception ex)
        {
            Debug.LogError($"Connection health check failed: {ex.Message}");
            return false;
        }
    }
    
    // Async batch operations for better performance
    public async Task<int> BatchUpdatePlayerStatsAsync(List<PlayerStatUpdate> updates)
    {
        using var connection = new SqlConnection(connectionString);
        await connection.OpenAsync();
        
        using var transaction = connection.BeginTransaction();
        try
        {
            var command = new SqlCommand(@"
                UPDATE PlayerStats 
                SET Experience = @Experience,
                    Level = @Level,
                    LastPlayDate = @LastPlayDate
                WHERE PlayerId = @PlayerId", connection, transaction);
            
            int totalUpdated = 0;
            
            foreach (var update in updates)
            {
                command.Parameters.Clear();
                command.Parameters.AddWithValue("@PlayerId", update.PlayerId);
                command.Parameters.AddWithValue("@Experience", update.Experience);
                command.Parameters.AddWithValue("@Level", update.Level);
                command.Parameters.AddWithValue("@LastPlayDate", update.LastPlayDate);
                
                totalUpdated += await command.ExecuteNonQueryAsync();
            }
            
            await transaction.CommitAsync();
            return totalUpdated;
        }
        catch
        {
            await transaction.RollbackAsync();
            throw;
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Performance Analysis Automation
```
Prompt: "Analyze this Unity game database execution plan and suggest specific index optimizations for player lookup queries, leaderboard generation, and inventory management operations: [paste execution plan]"
```

### Cache Strategy Optimization
```
Prompt: "Design an optimal caching strategy for a Unity MMO with 50k concurrent players, including cache hierarchies, TTL values, invalidation patterns, and memory usage optimization for player data, guild information, and auction house items."
```

### Database Monitoring Queries
```
Prompt: "Generate comprehensive SQL Server monitoring queries for Unity game database that track connection pool usage, query performance, deadlocks, index usage statistics, and automatic alerting for performance degradation."
```

## 💡 Key Highlights

### Index Strategy Best Practices
- **Covering indexes**: Include frequently accessed columns
- **Partial indexes**: Filter conditions for active records only  
- **Composite indexes**: Match query WHERE and ORDER BY clauses
- **Index maintenance**: Regular rebuilding and statistics updates
- **Monitor usage**: Remove unused indexes that slow down writes

### Query Optimization Techniques
- **Parameterized queries**: Prevent SQL injection and enable plan reuse
- **Avoid SELECT ***: Only retrieve needed columns
- **Limit result sets**: Use TOP/LIMIT for large datasets
- **Batch operations**: Group multiple updates into single transactions
- **Async operations**: Non-blocking database calls in Unity

### Performance Monitoring
- **Execution plans**: Identify table scans and missing indexes
- **Wait statistics**: Find bottlenecks in I/O, locks, memory
- **Connection metrics**: Pool usage, timeout rates, retry counts
- **Query store**: Historical performance tracking and regression detection
- **Real-time alerts**: Automated notification of performance issues