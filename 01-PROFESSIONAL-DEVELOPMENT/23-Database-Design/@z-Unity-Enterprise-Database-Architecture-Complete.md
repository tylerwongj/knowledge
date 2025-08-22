# @z-Unity-Enterprise-Database-Architecture-Complete - Scalable Game Data Management

## 🎯 Learning Objectives
- Master enterprise-grade database architecture for Unity games at massive scale
- Implement sophisticated data management patterns for complex game systems
- Build high-performance, distributed database solutions for live games
- Create comprehensive data analytics and business intelligence systems

## 🔧 Core Database Architecture Framework

### Multi-Database Unity Integration System
```csharp
// Enterprise Unity Database Manager with multiple database support
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using System.Data;
using System.Data.SqlClient;
using MongoDB.Driver;
using StackExchange.Redis;
using Cassandra;
using InfluxDB.Client;

public class UnityDatabaseManager : MonoBehaviour
{
    [System.Serializable]
    public class DatabaseConfig
    {
        [Header("SQL Database Configuration")]
        public string sqlConnectionString;
        public int sqlCommandTimeout = 30;
        public bool enableSqlConnectionPooling = true;
        public int maxSqlConnections = 100;
        
        [Header("MongoDB Configuration")]
        public string mongoConnectionString;
        public string mongoDatabaseName;
        public bool enableMongoSSL = true;
        
        [Header("Redis Configuration")]
        public string redisConnectionString;
        public int redisDatabase = 0;
        public int redisCommandTimeout = 5000;
        
        [Header("Cassandra Configuration")]
        public string[] cassandraContactPoints;
        public string cassandraKeyspace;
        public int cassandraPort = 9042;
        
        [Header("InfluxDB Configuration (Analytics)")]
        public string influxDbUrl;
        public string influxDbToken;
        public string influxDbOrganization;
        public string influxDbBucket;
        
        [Header("Performance Settings")]
        public bool enableQueryCaching = true;
        public int cacheExpirationMinutes = 15;
        public bool enableBatchOperations = true;
        public int batchSize = 1000;
        public bool enableReadReplicas = true;
    }
    
    [SerializeField] private DatabaseConfig config;
    
    // Database connections
    private SqlConnection sqlConnection;
    private IMongoDatabase mongoDatabase;
    private IDatabase redisDatabase;
    private ISession cassandraSession;
    private InfluxDBClient influxDbClient;
    
    // Connection managers
    private DatabaseConnectionPool sqlConnectionPool;
    private QueryCache queryCache;
    private BatchOperationManager batchManager;
    private DatabaseMetricsCollector metricsCollector;
    
    public static UnityDatabaseManager Instance { get; private set; }
    
    // Events for database operations
    public event Action<string> OnDatabaseConnected;
    public event Action<string, Exception> OnDatabaseError;
    public event Action<DatabaseMetrics> OnMetricsUpdated;
    
    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeDatabaseSystems();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    private async void InitializeDatabaseSystems()
    {
        try
        {
            // Initialize core systems
            queryCache = new QueryCache(config.cacheExpirationMinutes);
            batchManager = new BatchOperationManager(config.batchSize);
            metricsCollector = new DatabaseMetricsCollector();
            
            // Initialize database connections
            await InitializeSqlDatabase();
            await InitializeMongoDatabase();
            await InitializeRedisDatabase();
            await InitializeCassandraDatabase();
            await InitializeInfluxDatabase();
            
            // Start background services
            StartMetricsCollection();
            StartHealthMonitoring();
            
            Debug.Log("Unity Database Manager initialized successfully");
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to initialize database systems: {e.Message}");
            OnDatabaseError?.Invoke("Initialization", e);
        }
    }
    
    #region SQL Database Operations
    
    private async Task InitializeSqlDatabase()
    {
        if (config.enableSqlConnectionPooling)
        {
            sqlConnectionPool = new DatabaseConnectionPool(
                config.sqlConnectionString, 
                config.maxSqlConnections
            );
        }
        else
        {
            sqlConnection = new SqlConnection(config.sqlConnectionString);
            await sqlConnection.OpenAsync();
        }
        
        OnDatabaseConnected?.Invoke("SQL Server");
        Debug.Log("SQL Database connection established");
    }
    
    public async Task<List<T>> ExecuteQuery<T>(string query, object parameters = null) where T : class, new()
    {
        // Check cache first
        string cacheKey = queryCache.GenerateCacheKey(query, parameters);
        if (config.enableQueryCaching && queryCache.TryGetValue(cacheKey, out List<T> cachedResult))
        {
            metricsCollector.RecordCacheHit();
            return cachedResult;
        }
        
        try
        {
            var connection = sqlConnectionPool?.GetConnection() ?? sqlConnection;
            
            using (var command = new SqlCommand(query, connection))
            {
                command.CommandTimeout = config.sqlCommandTimeout;
                
                // Add parameters
                if (parameters != null)
                {
                    AddSqlParameters(command, parameters);
                }
                
                var results = new List<T>();
                using (var reader = await command.ExecuteReaderAsync())
                {
                    while (await reader.ReadAsync())
                    {
                        var item = MapSqlRowToObject<T>(reader);
                        results.Add(item);
                    }
                }
                
                // Cache results
                if (config.enableQueryCaching)
                {
                    queryCache.Set(cacheKey, results);
                }
                
                metricsCollector.RecordQuery("SQL", query);
                return results;
            }
        }
        catch (Exception e)
        {
            metricsCollector.RecordError("SQL", e);
            OnDatabaseError?.Invoke("SQL Query", e);
            throw;
        }
        finally
        {
            sqlConnectionPool?.ReturnConnection(sqlConnection);
        }
    }
    
    public async Task<int> ExecuteNonQuery(string query, object parameters = null)
    {
        try
        {
            var connection = sqlConnectionPool?.GetConnection() ?? sqlConnection;
            
            using (var command = new SqlCommand(query, connection))
            {
                command.CommandTimeout = config.sqlCommandTimeout;
                
                if (parameters != null)
                {
                    AddSqlParameters(command, parameters);
                }
                
                var result = await command.ExecuteNonQueryAsync();
                metricsCollector.RecordCommand("SQL", query);
                return result;
            }
        }
        catch (Exception e)
        {
            metricsCollector.RecordError("SQL", e);
            OnDatabaseError?.Invoke("SQL Command", e);
            throw;
        }
        finally
        {
            sqlConnectionPool?.ReturnConnection(sqlConnection);
        }
    }
    
    public async Task<List<T>> ExecuteStoredProcedure<T>(string procedureName, object parameters = null) where T : class, new()
    {
        string cacheKey = queryCache.GenerateCacheKey($"SP:{procedureName}", parameters);
        if (config.enableQueryCaching && queryCache.TryGetValue(cacheKey, out List<T> cachedResult))
        {
            metricsCollector.RecordCacheHit();
            return cachedResult;
        }
        
        try
        {
            var connection = sqlConnectionPool?.GetConnection() ?? sqlConnection;
            
            using (var command = new SqlCommand(procedureName, connection))
            {
                command.CommandType = CommandType.StoredProcedure;
                command.CommandTimeout = config.sqlCommandTimeout;
                
                if (parameters != null)
                {
                    AddSqlParameters(command, parameters);
                }
                
                var results = new List<T>();
                using (var reader = await command.ExecuteReaderAsync())
                {
                    while (await reader.ReadAsync())
                    {
                        var item = MapSqlRowToObject<T>(reader);
                        results.Add(item);
                    }
                }
                
                if (config.enableQueryCaching)
                {
                    queryCache.Set(cacheKey, results);
                }
                
                metricsCollector.RecordStoredProcedure("SQL", procedureName);
                return results;
            }
        }
        catch (Exception e)
        {
            metricsCollector.RecordError("SQL", e);
            OnDatabaseError?.Invoke("SQL Stored Procedure", e);
            throw;
        }
        finally
        {
            sqlConnectionPool?.ReturnConnection(sqlConnection);
        }
    }
    
    #endregion
    
    #region MongoDB Operations
    
    private async Task InitializeMongoDatabase()
    {
        try
        {
            var client = new MongoClient(config.mongoConnectionString);
            mongoDatabase = client.GetDatabase(config.mongoDatabaseName);
            
            // Test connection
            await mongoDatabase.RunCommandAsync((Command<BsonDocument>)"{ping:1}");
            
            OnDatabaseConnected?.Invoke("MongoDB");
            Debug.Log("MongoDB connection established");
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to initialize MongoDB: {e.Message}");
            throw;
        }
    }
    
    public async Task<List<T>> FindDocuments<T>(string collectionName, FilterDefinition<T> filter, 
        FindOptions<T> options = null)
    {
        try
        {
            var collection = mongoDatabase.GetCollection<T>(collectionName);
            var cursor = await collection.FindAsync(filter, options);
            var results = await cursor.ToListAsync();
            
            metricsCollector.RecordQuery("MongoDB", $"Find in {collectionName}");
            return results;
        }
        catch (Exception e)
        {
            metricsCollector.RecordError("MongoDB", e);
            OnDatabaseError?.Invoke("MongoDB Find", e);
            throw;
        }
    }
    
    public async Task InsertDocument<T>(string collectionName, T document)
    {
        try
        {
            var collection = mongoDatabase.GetCollection<T>(collectionName);
            await collection.InsertOneAsync(document);
            
            metricsCollector.RecordCommand("MongoDB", $"Insert into {collectionName}");
        }
        catch (Exception e)
        {
            metricsCollector.RecordError("MongoDB", e);
            OnDatabaseError?.Invoke("MongoDB Insert", e);
            throw;
        }
    }
    
    public async Task<long> UpdateDocuments<T>(string collectionName, FilterDefinition<T> filter, 
        UpdateDefinition<T> update, UpdateOptions options = null)
    {
        try
        {
            var collection = mongoDatabase.GetCollection<T>(collectionName);
            var result = await collection.UpdateManyAsync(filter, update, options);
            
            metricsCollector.RecordCommand("MongoDB", $"Update in {collectionName}");
            return result.ModifiedCount;
        }
        catch (Exception e)
        {
            metricsCollector.RecordError("MongoDB", e);
            OnDatabaseError?.Invoke("MongoDB Update", e);
            throw;
        }
    }
    
    public async Task<long> DeleteDocuments<T>(string collectionName, FilterDefinition<T> filter)
    {
        try
        {
            var collection = mongoDatabase.GetCollection<T>(collectionName);
            var result = await collection.DeleteManyAsync(filter);
            
            metricsCollector.RecordCommand("MongoDB", $"Delete from {collectionName}");
            return result.DeletedCount;
        }
        catch (Exception e)
        {
            metricsCollector.RecordError("MongoDB", e);
            OnDatabaseError?.Invoke("MongoDB Delete", e);
            throw;
        }
    }
    
    // Advanced MongoDB aggregation operations
    public async Task<List<TResult>> AggregateDocuments<T, TResult>(string collectionName, 
        PipelineDefinition<T, TResult> pipeline, AggregateOptions options = null)
    {
        try
        {
            var collection = mongoDatabase.GetCollection<T>(collectionName);
            var cursor = await collection.AggregateAsync(pipeline, options);
            var results = await cursor.ToListAsync();
            
            metricsCollector.RecordQuery("MongoDB", $"Aggregate in {collectionName}");
            return results;
        }
        catch (Exception e)
        {
            metricsCollector.RecordError("MongoDB", e);
            OnDatabaseError?.Invoke("MongoDB Aggregate", e);
            throw;
        }
    }
    
    #endregion
    
    #region Redis Cache Operations
    
    private async Task InitializeRedisDatabase()
    {
        try
        {
            var redis = ConnectionMultiplexer.Connect(config.redisConnectionString);
            redisDatabase = redis.GetDatabase(config.redisDatabase);
            
            // Test connection
            await redisDatabase.PingAsync();
            
            OnDatabaseConnected?.Invoke("Redis");
            Debug.Log("Redis connection established");
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to initialize Redis: {e.Message}");
            throw;
        }
    }
    
    public async Task<bool> SetCache<T>(string key, T value, TimeSpan? expiry = null)
    {
        try
        {
            string serializedValue = JsonUtility.ToJson(value);
            bool result = await redisDatabase.StringSetAsync(key, serializedValue, expiry);
            
            metricsCollector.RecordCommand("Redis", "SET");
            return result;
        }
        catch (Exception e)
        {
            metricsCollector.RecordError("Redis", e);
            OnDatabaseError?.Invoke("Redis Set", e);
            return false;
        }
    }
    
    public async Task<T> GetCache<T>(string key) where T : class
    {
        try
        {
            var value = await redisDatabase.StringGetAsync(key);
            if (!value.HasValue)
            {
                metricsCollector.RecordCacheMiss();
                return null;
            }
            
            metricsCollector.RecordCacheHit();
            metricsCollector.RecordQuery("Redis", "GET");
            return JsonUtility.FromJson<T>(value);
        }
        catch (Exception e)
        {
            metricsCollector.RecordError("Redis", e);
            OnDatabaseError?.Invoke("Redis Get", e);
            return null;
        }
    }
    
    public async Task<bool> DeleteCache(string key)
    {
        try
        {
            bool result = await redisDatabase.KeyDeleteAsync(key);
            metricsCollector.RecordCommand("Redis", "DELETE");
            return result;
        }
        catch (Exception e)
        {
            metricsCollector.RecordError("Redis", e);
            OnDatabaseError?.Invoke("Redis Delete", e);
            return false;
        }
    }
    
    // Advanced Redis operations
    public async Task<long> IncrementCounter(string key, long value = 1)
    {
        try
        {
            long result = await redisDatabase.StringIncrementAsync(key, value);
            metricsCollector.RecordCommand("Redis", "INCR");
            return result;
        }
        catch (Exception e)
        {
            metricsCollector.RecordError("Redis", e);
            OnDatabaseError?.Invoke("Redis Increment", e);
            return 0;
        }
    }
    
    public async Task<bool> AddToSet(string key, string value)
    {
        try
        {
            bool result = await redisDatabase.SetAddAsync(key, value);
            metricsCollector.RecordCommand("Redis", "SADD");
            return result;
        }
        catch (Exception e)
        {
            metricsCollector.RecordError("Redis", e);
            OnDatabaseError?.Invoke("Redis Set Add", e);
            return false;
        }
    }
    
    public async Task<string[]> GetSetMembers(string key)
    {
        try
        {
            var values = await redisDatabase.SetMembersAsync(key);
            metricsCollector.RecordQuery("Redis", "SMEMBERS");
            return values.ToStringArray();
        }
        catch (Exception e)
        {
            metricsCollector.RecordError("Redis", e);
            OnDatabaseError?.Invoke("Redis Set Members", e);
            return new string[0];
        }
    }
    
    #endregion
    
    #region Cassandra Operations (Time-Series Data)
    
    private async Task InitializeCassandraDatabase()
    {
        try
        {
            var cluster = Cluster.Builder()
                .AddContactPoints(config.cassandraContactPoints)
                .WithPort(config.cassandraPort)
                .Build();
                
            cassandraSession = await cluster.ConnectAsync(config.cassandraKeyspace);
            
            OnDatabaseConnected?.Invoke("Cassandra");
            Debug.Log("Cassandra connection established");
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to initialize Cassandra: {e.Message}");
            throw;
        }
    }
    
    public async Task<List<T>> ExecuteCassandraQuery<T>(string cql, params object[] parameters) where T : new()
    {
        try
        {
            var statement = new SimpleStatement(cql, parameters);
            var rowSet = await cassandraSession.ExecuteAsync(statement);
            
            var results = new List<T>();
            foreach (var row in rowSet)
            {
                var item = MapCassandraRowToObject<T>(row);
                results.Add(item);
            }
            
            metricsCollector.RecordQuery("Cassandra", cql);
            return results;
        }
        catch (Exception e)
        {
            metricsCollector.RecordError("Cassandra", e);
            OnDatabaseError?.Invoke("Cassandra Query", e);
            throw;
        }
    }
    
    // Time-series data insertion for game analytics
    public async Task InsertTimeSeriesData(string table, Dictionary<string, object> data, DateTime timestamp)
    {
        try
        {
            var columns = string.Join(", ", data.Keys);
            var placeholders = string.Join(", ", data.Keys.Select(k => "?"));
            var values = data.Values.Concat(new object[] { timestamp }).ToArray();
            
            var cql = $"INSERT INTO {table} ({columns}, timestamp) VALUES ({placeholders}, ?)";
            var statement = new SimpleStatement(cql, values);
            
            await cassandraSession.ExecuteAsync(statement);
            metricsCollector.RecordCommand("Cassandra", $"Insert into {table}");
        }
        catch (Exception e)
        {
            metricsCollector.RecordError("Cassandra", e);
            OnDatabaseError?.Invoke("Cassandra Insert", e);
            throw;
        }
    }
    
    #endregion
    
    #region InfluxDB Operations (Analytics and Metrics)
    
    private async Task InitializeInfluxDatabase()
    {
        try
        {
            influxDbClient = InfluxDBClientFactory.Create(config.influxDbUrl, config.influxDbToken);
            
            // Test connection
            var health = await influxDbClient.HealthAsync();
            if (health.Status != HealthCheck.StatusEnum.Pass)
            {
                throw new Exception("InfluxDB health check failed");
            }
            
            OnDatabaseConnected?.Invoke("InfluxDB");
            Debug.Log("InfluxDB connection established");
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to initialize InfluxDB: {e.Message}");
            throw;
        }
    }
    
    public async Task WriteGameMetrics(string measurement, Dictionary<string, object> fields, 
        Dictionary<string, string> tags = null, DateTime? timestamp = null)
    {
        try
        {
            var writeApi = influxDbClient.GetWriteApiAsync();
            
            var point = PointData.Measurement(measurement);
            
            // Add tags
            if (tags != null)
            {
                foreach (var tag in tags)
                {
                    point = point.Tag(tag.Key, tag.Value);
                }
            }
            
            // Add fields
            foreach (var field in fields)
            {
                point = point.Field(field.Key, field.Value);
            }
            
            // Set timestamp
            if (timestamp.HasValue)
            {
                point = point.Timestamp(timestamp.Value, WritePrecision.Ns);
            }
            
            await writeApi.WritePointAsync(point, config.influxDbBucket, config.influxDbOrganization);
            metricsCollector.RecordCommand("InfluxDB", $"Write {measurement}");
        }
        catch (Exception e)
        {
            metricsCollector.RecordError("InfluxDB", e);
            OnDatabaseError?.Invoke("InfluxDB Write", e);
            throw;
        }
    }
    
    public async Task<List<FluxTable>> QueryGameAnalytics(string fluxQuery)
    {
        try
        {
            var queryApi = influxDbClient.GetQueryApi();
            var tables = await queryApi.QueryAsync(fluxQuery, config.influxDbOrganization);
            
            metricsCollector.RecordQuery("InfluxDB", fluxQuery);
            return tables;
        }
        catch (Exception e)
        {
            metricsCollector.RecordError("InfluxDB", e);
            OnDatabaseError?.Invoke("InfluxDB Query", e);
            throw;
        }
    }
    
    #endregion
    
    #region Batch Operations and Performance Optimization
    
    public class BatchOperationManager
    {
        private int batchSize;
        private Dictionary<string, List<object>> batches;
        private Timer flushTimer;
        
        public BatchOperationManager(int batchSize)
        {
            this.batchSize = batchSize;
            batches = new Dictionary<string, List<object>>();
            
            // Auto-flush every 5 seconds
            flushTimer = new Timer(async _ => await FlushAllBatches(), null, 
                TimeSpan.FromSeconds(5), TimeSpan.FromSeconds(5));
        }
        
        public void AddToBatch(string batchKey, object operation)
        {
            if (!batches.ContainsKey(batchKey))
            {
                batches[batchKey] = new List<object>();
            }
            
            batches[batchKey].Add(operation);
            
            // Auto-flush when batch size reached
            if (batches[batchKey].Count >= batchSize)
            {
                _ = FlushBatch(batchKey);
            }
        }
        
        public async Task FlushBatch(string batchKey)
        {
            if (!batches.ContainsKey(batchKey) || batches[batchKey].Count == 0)
                return;
                
            var operations = batches[batchKey].ToList();
            batches[batchKey].Clear();
            
            // Execute batch operations based on type
            await ExecuteBatchOperations(batchKey, operations);
        }
        
        private async Task FlushAllBatches()
        {
            var batchKeys = batches.Keys.ToList();
            foreach (var key in batchKeys)
            {
                await FlushBatch(key);
            }
        }
        
        private async Task ExecuteBatchOperations(string batchKey, List<object> operations)
        {
            try
            {
                if (batchKey.StartsWith("SQL_"))
                {
                    await ExecuteSqlBatch(operations);
                }
                else if (batchKey.StartsWith("MONGO_"))
                {
                    await ExecuteMongoBatch(batchKey, operations);
                }
                else if (batchKey.StartsWith("INFLUX_"))
                {
                    await ExecuteInfluxBatch(operations);
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"Batch operation failed for {batchKey}: {e.Message}");
            }
        }
        
        private async Task ExecuteSqlBatch(List<object> operations)
        {
            // Implementation for SQL batch operations
        }
        
        private async Task ExecuteMongoBatch(string collectionName, List<object> operations)
        {
            // Implementation for MongoDB batch operations
        }
        
        private async Task ExecuteInfluxBatch(List<object> operations)
        {
            // Implementation for InfluxDB batch operations
        }
    }
    
    public class QueryCache
    {
        private Dictionary<string, CacheItem> cache;
        private int expirationMinutes;
        
        public QueryCache(int expirationMinutes)
        {
            this.expirationMinutes = expirationMinutes;
            cache = new Dictionary<string, CacheItem>();
            
            // Clean expired items every minute
            InvokeRepeating(nameof(CleanExpiredItems), 60f, 60f);
        }
        
        public string GenerateCacheKey(string query, object parameters)
        {
            string paramString = parameters != null ? JsonUtility.ToJson(parameters) : "";
            return $"{query.GetHashCode()}_{paramString.GetHashCode()}";
        }
        
        public bool TryGetValue<T>(string key, out List<T> value)
        {
            value = null;
            
            if (cache.ContainsKey(key) && !cache[key].IsExpired())
            {
                value = (List<T>)cache[key].Value;
                return true;
            }
            
            return false;
        }
        
        public void Set<T>(string key, List<T> value)
        {
            cache[key] = new CacheItem
            {
                Value = value,
                ExpiryTime = DateTime.Now.AddMinutes(expirationMinutes)
            };
        }
        
        private void CleanExpiredItems()
        {
            var expiredKeys = cache.Where(kvp => kvp.Value.IsExpired()).Select(kvp => kvp.Key).ToList();
            foreach (var key in expiredKeys)
            {
                cache.Remove(key);
            }
        }
        
        private class CacheItem
        {
            public object Value { get; set; }
            public DateTime ExpiryTime { get; set; }
            
            public bool IsExpired() => DateTime.Now > ExpiryTime;
        }
    }
    
    #endregion
    
    #region Database Metrics and Monitoring
    
    public class DatabaseMetricsCollector
    {
        private Dictionary<string, DatabaseMetrics> metrics;
        
        public DatabaseMetricsCollector()
        {
            metrics = new Dictionary<string, DatabaseMetrics>();
        }
        
        public void RecordQuery(string database, string query)
        {
            GetMetrics(database).QueryCount++;
            GetMetrics(database).LastQueryTime = DateTime.Now;
        }
        
        public void RecordCommand(string database, string command)
        {
            GetMetrics(database).CommandCount++;
            GetMetrics(database).LastCommandTime = DateTime.Now;
        }
        
        public void RecordError(string database, Exception error)
        {
            GetMetrics(database).ErrorCount++;
            GetMetrics(database).LastError = error.Message;
            GetMetrics(database).LastErrorTime = DateTime.Now;
        }
        
        public void RecordCacheHit()
        {
            GetMetrics("Cache").CacheHits++;
        }
        
        public void RecordCacheMiss()
        {
            GetMetrics("Cache").CacheMisses++;
        }
        
        public void RecordStoredProcedure(string database, string procedureName)
        {
            GetMetrics(database).StoredProcedureCount++;
        }
        
        private DatabaseMetrics GetMetrics(string database)
        {
            if (!metrics.ContainsKey(database))
            {
                metrics[database] = new DatabaseMetrics { DatabaseName = database };
            }
            
            return metrics[database];
        }
        
        public Dictionary<string, DatabaseMetrics> GetAllMetrics()
        {
            return new Dictionary<string, DatabaseMetrics>(metrics);
        }
    }
    
    [System.Serializable]
    public class DatabaseMetrics
    {
        public string DatabaseName;
        public int QueryCount;
        public int CommandCount;
        public int ErrorCount;
        public int CacheHits;
        public int CacheMisses;
        public int StoredProcedureCount;
        public DateTime LastQueryTime;
        public DateTime LastCommandTime;
        public DateTime LastErrorTime;
        public string LastError;
        
        public float CacheHitRatio => CacheHits + CacheMisses > 0 ? (float)CacheHits / (CacheHits + CacheMisses) : 0f;
        public float ErrorRate => QueryCount + CommandCount > 0 ? (float)ErrorCount / (QueryCount + CommandCount) : 0f;
    }
    
    #endregion
    
    #region Helper Methods
    
    private void AddSqlParameters(SqlCommand command, object parameters)
    {
        var properties = parameters.GetType().GetProperties();
        foreach (var property in properties)
        {
            command.Parameters.AddWithValue($"@{property.Name}", property.GetValue(parameters) ?? DBNull.Value);
        }
    }
    
    private T MapSqlRowToObject<T>(SqlDataReader reader) where T : new()
    {
        var item = new T();
        var properties = typeof(T).GetProperties();
        
        foreach (var property in properties)
        {
            if (reader.HasColumn(property.Name) && !reader.IsDBNull(property.Name))
            {
                property.SetValue(item, reader[property.Name]);
            }
        }
        
        return item;
    }
    
    private T MapCassandraRowToObject<T>(Row row) where T : new()
    {
        var item = new T();
        var properties = typeof(T).GetProperties();
        
        foreach (var property in properties)
        {
            try
            {
                var value = row.GetValue<object>(property.Name.ToLower());
                if (value != null)
                {
                    property.SetValue(item, Convert.ChangeType(value, property.PropertyType));
                }
            }
            catch
            {
                // Skip properties that can't be mapped
            }
        }
        
        return item;
    }
    
    private void StartMetricsCollection()
    {
        InvokeRepeating(nameof(CollectAndReportMetrics), 60f, 60f);
    }
    
    private void StartHealthMonitoring()
    {
        InvokeRepeating(nameof(MonitorDatabaseHealth), 30f, 30f);
    }
    
    private void CollectAndReportMetrics()
    {
        var allMetrics = metricsCollector.GetAllMetrics();
        OnMetricsUpdated?.Invoke(allMetrics.Values.First()); // Simplified for example
    }
    
    private async void MonitorDatabaseHealth()
    {
        // Monitor database connections and performance
        // Implement health checks for all database systems
        try
        {
            // SQL Server health check
            if (sqlConnection?.State == ConnectionState.Open || sqlConnectionPool != null)
            {
                await ExecuteNonQuery("SELECT 1");
            }
            
            // Redis health check
            if (redisDatabase != null)
            {
                await redisDatabase.PingAsync();
            }
            
            // MongoDB health check
            if (mongoDatabase != null)
            {
                await mongoDatabase.RunCommandAsync((Command<BsonDocument>)"{ping:1}");
            }
        }
        catch (Exception e)
        {
            Debug.LogWarning($"Database health check failed: {e.Message}");
        }
    }
    
    private void OnDestroy()
    {
        // Cleanup database connections
        sqlConnection?.Close();
        sqlConnectionPool?.Dispose();
        cassandraSession?.Dispose();
        influxDbClient?.Dispose();
        
        // Flush any pending batch operations
        batchManager?.FlushAllBatches();
    }
    
    #endregion
}

// Extension method for SqlDataReader
public static class SqlDataReaderExtensions
{
    public static bool HasColumn(this SqlDataReader reader, string columnName)
    {
        for (int i = 0; i < reader.FieldCount; i++)
        {
            if (reader.GetName(i).Equals(columnName, StringComparison.InvariantCultureIgnoreCase))
                return true;
        }
        return false;
    }
}

// Database connection pool implementation
public class DatabaseConnectionPool : IDisposable
{
    private Queue<SqlConnection> availableConnections;
    private HashSet<SqlConnection> allConnections;
    private string connectionString;
    private int maxConnections;
    private object lockObject = new object();
    
    public DatabaseConnectionPool(string connectionString, int maxConnections)
    {
        this.connectionString = connectionString;
        this.maxConnections = maxConnections;
        availableConnections = new Queue<SqlConnection>();
        allConnections = new HashSet<SqlConnection>();
        
        // Initialize pool
        for (int i = 0; i < Math.Min(5, maxConnections); i++)
        {
            CreateConnection();
        }
    }
    
    public SqlConnection GetConnection()
    {
        lock (lockObject)
        {
            if (availableConnections.Count == 0 && allConnections.Count < maxConnections)
            {
                CreateConnection();
            }
            
            if (availableConnections.Count > 0)
            {
                return availableConnections.Dequeue();
            }
            
            // Wait for connection to become available or create new one
            // In production, implement proper waiting mechanism
            throw new InvalidOperationException("No available database connections");
        }
    }
    
    public void ReturnConnection(SqlConnection connection)
    {
        if (connection == null) return;
        
        lock (lockObject)
        {
            if (allConnections.Contains(connection) && connection.State == ConnectionState.Open)
            {
                availableConnections.Enqueue(connection);
            }
        }
    }
    
    private void CreateConnection()
    {
        var connection = new SqlConnection(connectionString);
        connection.Open();
        allConnections.Add(connection);
        availableConnections.Enqueue(connection);
    }
    
    public void Dispose()
    {
        lock (lockObject)
        {
            foreach (var connection in allConnections)
            {
                connection.Close();
                connection.Dispose();
            }
            
            availableConnections.Clear();
            allConnections.Clear();
        }
    }
}
```

### Advanced Database Schema Design for Games
```sql
-- Comprehensive game database schema with performance optimization
-- SQL Server implementation with cross-database compatibility

-- Core Player Management Schema
CREATE TABLE Players (
    PlayerID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    Username NVARCHAR(50) UNIQUE NOT NULL,
    Email NVARCHAR(255) UNIQUE NOT NULL,
    PasswordHash NVARCHAR(255) NOT NULL,
    Salt NVARCHAR(255) NOT NULL,
    CreatedAt DATETIME2 DEFAULT GETUTCDATE(),
    LastLoginAt DATETIME2,
    IsActive BIT DEFAULT 1,
    IsBanned BIT DEFAULT 0,
    BanReason NVARCHAR(MAX),
    Region NVARCHAR(10),
    TimeZone NVARCHAR(50),
    PreferredLanguage NVARCHAR(10),
    TotalPlayTime INT DEFAULT 0, -- in minutes
    
    -- Indexing for performance
    INDEX IX_Players_Username (Username),
    INDEX IX_Players_Email (Email),
    INDEX IX_Players_CreatedAt (CreatedAt),
    INDEX IX_Players_LastLoginAt (LastLoginAt),
    INDEX IX_Players_Region (Region)
);

-- Player Profile and Statistics
CREATE TABLE PlayerProfiles (
    ProfileID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    PlayerID UNIQUEIDENTIFIER NOT NULL,
    DisplayName NVARCHAR(100),
    AvatarURL NVARCHAR(500),
    Level INT DEFAULT 1,
    Experience BIGINT DEFAULT 0,
    Reputation INT DEFAULT 0,
    Biography NVARCHAR(MAX),
    DateOfBirth DATE,
    Country NVARCHAR(100),
    ProfileVisibility TINYINT DEFAULT 1, -- 0=Private, 1=Friends, 2=Public
    UpdatedAt DATETIME2 DEFAULT GETUTCDATE(),
    
    FOREIGN KEY (PlayerID) REFERENCES Players(PlayerID) ON DELETE CASCADE,
    INDEX IX_PlayerProfiles_PlayerID (PlayerID),
    INDEX IX_PlayerProfiles_Level (Level),
    INDEX IX_PlayerProfiles_Experience (Experience)
);

-- Game Sessions and Analytics
CREATE TABLE GameSessions (
    SessionID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    PlayerID UNIQUEIDENTIFIER NOT NULL,
    GameVersion NVARCHAR(20) NOT NULL,
    Platform NVARCHAR(20) NOT NULL, -- PC, Mobile, Console
    DeviceInfo NVARCHAR(500),
    StartTime DATETIME2 DEFAULT GETUTCDATE(),
    EndTime DATETIME2,
    DurationMinutes AS DATEDIFF(MINUTE, StartTime, EndTime) PERSISTED,
    IPAddress NVARCHAR(45),
    Country NVARCHAR(100),
    SessionData NVARCHAR(MAX), -- JSON data
    
    FOREIGN KEY (PlayerID) REFERENCES Players(PlayerID),
    INDEX IX_GameSessions_PlayerID (PlayerID),
    INDEX IX_GameSessions_StartTime (StartTime),
    INDEX IX_GameSessions_Platform (Platform),
    INDEX IX_GameSessions_GameVersion (GameVersion)
);

-- Player Progression and Achievements
CREATE TABLE PlayerAchievements (
    AchievementID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    PlayerID UNIQUEIDENTIFIER NOT NULL,
    AchievementType NVARCHAR(50) NOT NULL,
    AchievementName NVARCHAR(100) NOT NULL,
    Description NVARCHAR(500),
    UnlockedAt DATETIME2 DEFAULT GETUTCDATE(),
    Progress FLOAT DEFAULT 0.0, -- 0.0 to 1.0
    IsCompleted BIT DEFAULT 0,
    Metadata NVARCHAR(MAX), -- JSON for additional data
    
    FOREIGN KEY (PlayerID) REFERENCES Players(PlayerID) ON DELETE CASCADE,
    UNIQUE (PlayerID, AchievementType, AchievementName),
    INDEX IX_PlayerAchievements_PlayerID (PlayerID),
    INDEX IX_PlayerAchievements_Type (AchievementType),
    INDEX IX_PlayerAchievements_UnlockedAt (UnlockedAt)
);

-- Virtual Economy Management
CREATE TABLE Currencies (
    CurrencyID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    CurrencyCode NVARCHAR(10) UNIQUE NOT NULL, -- GOLD, GEMS, COINS
    DisplayName NVARCHAR(50) NOT NULL,
    Description NVARCHAR(200),
    IconURL NVARCHAR(500),
    IsPremium BIT DEFAULT 0,
    ExchangeRate DECIMAL(18,4), -- Rate to base currency
    IsActive BIT DEFAULT 1,
    CreatedAt DATETIME2 DEFAULT GETUTCDATE()
);

CREATE TABLE PlayerCurrencies (
    PlayerCurrencyID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    PlayerID UNIQUEIDENTIFIER NOT NULL,
    CurrencyID UNIQUEIDENTIFIER NOT NULL,
    Balance BIGINT DEFAULT 0,
    TotalEarned BIGINT DEFAULT 0,
    TotalSpent BIGINT DEFAULT 0,
    LastUpdated DATETIME2 DEFAULT GETUTCDATE(),
    
    FOREIGN KEY (PlayerID) REFERENCES Players(PlayerID) ON DELETE CASCADE,
    FOREIGN KEY (CurrencyID) REFERENCES Currencies(CurrencyID),
    UNIQUE (PlayerID, CurrencyID),
    INDEX IX_PlayerCurrencies_PlayerID (PlayerID),
    INDEX IX_PlayerCurrencies_Balance (Balance)
);

-- Transaction Log for Audit Trail
CREATE TABLE CurrencyTransactions (
    TransactionID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    PlayerID UNIQUEIDENTIFIER NOT NULL,
    CurrencyID UNIQUEIDENTIFIER NOT NULL,
    TransactionType NVARCHAR(20) NOT NULL, -- EARN, SPEND, TRANSFER, ADJUST
    Amount BIGINT NOT NULL,
    BalanceBefore BIGINT NOT NULL,
    BalanceAfter BIGINT NOT NULL,
    Source NVARCHAR(100), -- Quest, Purchase, Admin, etc.
    Reference NVARCHAR(200), -- External reference (order ID, quest ID)
    Metadata NVARCHAR(MAX), -- JSON for additional context
    CreatedAt DATETIME2 DEFAULT GETUTCDATE(),
    
    FOREIGN KEY (PlayerID) REFERENCES Players(PlayerID),
    FOREIGN KEY (CurrencyID) REFERENCES Currencies(CurrencyID),
    INDEX IX_CurrencyTransactions_PlayerID (PlayerID),
    INDEX IX_CurrencyTransactions_CreatedAt (CreatedAt),
    INDEX IX_CurrencyTransactions_Type (TransactionType),
    INDEX IX_CurrencyTransactions_Source (Source)
);

-- Inventory and Items System
CREATE TABLE Items (
    ItemID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    ItemCode NVARCHAR(50) UNIQUE NOT NULL,
    Name NVARCHAR(100) NOT NULL,
    Description NVARCHAR(MAX),
    Category NVARCHAR(50) NOT NULL,
    Rarity NVARCHAR(20) DEFAULT 'Common',
    MaxStackSize INT DEFAULT 1,
    IsStackable BIT DEFAULT 0,
    IsTradeable BIT DEFAULT 1,
    IconURL NVARCHAR(500),
    Properties NVARCHAR(MAX), -- JSON for item properties
    IsActive BIT DEFAULT 1,
    CreatedAt DATETIME2 DEFAULT GETUTCDATE(),
    
    INDEX IX_Items_Category (Category),
    INDEX IX_Items_Rarity (Rarity),
    INDEX IX_Items_ItemCode (ItemCode)
);

CREATE TABLE PlayerInventory (
    InventoryID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    PlayerID UNIQUEIDENTIFIER NOT NULL,
    ItemID UNIQUEIDENTIFIER NOT NULL,
    Quantity INT DEFAULT 1,
    AcquiredAt DATETIME2 DEFAULT GETUTCDATE(),
    Metadata NVARCHAR(MAX), -- JSON for item-specific data (level, enchantments)
    IsEquipped BIT DEFAULT 0,
    SlotPosition INT,
    
    FOREIGN KEY (PlayerID) REFERENCES Players(PlayerID) ON DELETE CASCADE,
    FOREIGN KEY (ItemID) REFERENCES Items(ItemID),
    INDEX IX_PlayerInventory_PlayerID (PlayerID),
    INDEX IX_PlayerInventory_ItemID (ItemID),
    INDEX IX_PlayerInventory_AcquiredAt (AcquiredAt)
);

-- Leaderboards and Rankings
CREATE TABLE Leaderboards (
    LeaderboardID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    Name NVARCHAR(100) NOT NULL,
    Description NVARCHAR(500),
    MetricType NVARCHAR(50) NOT NULL, -- SCORE, TIME, LEVEL, etc.
    SortOrder NVARCHAR(10) DEFAULT 'DESC', -- ASC or DESC
    ResetPeriod NVARCHAR(20), -- DAILY, WEEKLY, MONTHLY, NEVER
    LastResetAt DATETIME2,
    IsActive BIT DEFAULT 1,
    CreatedAt DATETIME2 DEFAULT GETUTCDATE()
);

CREATE TABLE LeaderboardEntries (
    EntryID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    LeaderboardID UNIQUEIDENTIFIER NOT NULL,
    PlayerID UNIQUEIDENTIFIER NOT NULL,
    Score BIGINT NOT NULL,
    Rank INT,
    AdditionalData NVARCHAR(MAX), -- JSON for extra metrics
    AchievedAt DATETIME2 DEFAULT GETUTCDATE(),
    Season NVARCHAR(20),
    
    FOREIGN KEY (LeaderboardID) REFERENCES Leaderboards(LeaderboardID) ON DELETE CASCADE,
    FOREIGN KEY (PlayerID) REFERENCES Players(PlayerID) ON DELETE CASCADE,
    UNIQUE (LeaderboardID, PlayerID, Season),
    INDEX IX_LeaderboardEntries_LeaderboardID (LeaderboardID),
    INDEX IX_LeaderboardEntries_Score (Score),
    INDEX IX_LeaderboardEntries_Rank (Rank),
    INDEX IX_LeaderboardEntries_AchievedAt (AchievedAt)
);

-- Social Features - Friends and Guilds
CREATE TABLE PlayerFriends (
    FriendshipID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    PlayerID UNIQUEIDENTIFIER NOT NULL,
    FriendPlayerID UNIQUEIDENTIFIER NOT NULL,
    Status NVARCHAR(20) DEFAULT 'PENDING', -- PENDING, ACCEPTED, BLOCKED
    InitiatedBy UNIQUEIDENTIFIER NOT NULL, -- Who sent the request
    CreatedAt DATETIME2 DEFAULT GETUTCDATE(),
    AcceptedAt DATETIME2,
    
    FOREIGN KEY (PlayerID) REFERENCES Players(PlayerID),
    FOREIGN KEY (FriendPlayerID) REFERENCES Players(PlayerID),
    FOREIGN KEY (InitiatedBy) REFERENCES Players(PlayerID),
    UNIQUE (PlayerID, FriendPlayerID),
    INDEX IX_PlayerFriends_PlayerID (PlayerID),
    INDEX IX_PlayerFriends_Status (Status),
    
    CONSTRAINT CK_PlayerFriends_NotSelf CHECK (PlayerID != FriendPlayerID)
);

-- Game Content and Configuration
CREATE TABLE GameContent (
    ContentID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    ContentType NVARCHAR(50) NOT NULL, -- LEVEL, QUEST, ITEM, etc.
    ContentKey NVARCHAR(100) UNIQUE NOT NULL,
    Version NVARCHAR(20) NOT NULL,
    Data NVARCHAR(MAX) NOT NULL, -- JSON content data
    IsActive BIT DEFAULT 1,
    CreatedAt DATETIME2 DEFAULT GETUTCDATE(),
    UpdatedAt DATETIME2 DEFAULT GETUTCDATE(),
    CreatedBy NVARCHAR(100),
    
    INDEX IX_GameContent_ContentType (ContentType),
    INDEX IX_GameContent_ContentKey (ContentKey),
    INDEX IX_GameContent_Version (Version)
);

-- Analytics and Event Tracking
CREATE TABLE PlayerEvents (
    EventID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    PlayerID UNIQUEIDENTIFIER,
    SessionID UNIQUEIDENTIFIER,
    EventType NVARCHAR(50) NOT NULL,
    EventName NVARCHAR(100) NOT NULL,
    EventData NVARCHAR(MAX), -- JSON event parameters
    CreatedAt DATETIME2 DEFAULT GETUTCDATE(),
    
    FOREIGN KEY (PlayerID) REFERENCES Players(PlayerID),
    FOREIGN KEY (SessionID) REFERENCES GameSessions(SessionID),
    INDEX IX_PlayerEvents_PlayerID (PlayerID),
    INDEX IX_PlayerEvents_EventType (EventType),
    INDEX IX_PlayerEvents_CreatedAt (CreatedAt),
    INDEX IX_PlayerEvents_SessionID (SessionID)
);

-- Performance Optimization Views
CREATE VIEW vw_PlayerStats AS
SELECT 
    p.PlayerID,
    p.Username,
    pp.Level,
    pp.Experience,
    COUNT(pa.AchievementID) as AchievementCount,
    SUM(pc.Balance) as TotalCurrencyValue,
    p.TotalPlayTime,
    p.LastLoginAt,
    DATEDIFF(DAY, p.LastLoginAt, GETUTCDATE()) as DaysSinceLastLogin
FROM Players p
LEFT JOIN PlayerProfiles pp ON p.PlayerID = pp.PlayerID
LEFT JOIN PlayerAchievements pa ON p.PlayerID = pa.PlayerID AND pa.IsCompleted = 1
LEFT JOIN PlayerCurrencies pc ON p.PlayerID = pc.PlayerID
WHERE p.IsActive = 1 AND p.IsBanned = 0
GROUP BY p.PlayerID, p.Username, pp.Level, pp.Experience, p.TotalPlayTime, p.LastLoginAt;

-- Stored Procedures for Common Operations
CREATE PROCEDURE sp_UpdatePlayerCurrency
    @PlayerID UNIQUEIDENTIFIER,
    @CurrencyCode NVARCHAR(10),
    @Amount BIGINT,
    @TransactionType NVARCHAR(20),
    @Source NVARCHAR(100),
    @Reference NVARCHAR(200) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRANSACTION;
    
    DECLARE @CurrencyID UNIQUEIDENTIFIER;
    DECLARE @CurrentBalance BIGINT;
    DECLARE @NewBalance BIGINT;
    
    -- Get currency ID
    SELECT @CurrencyID = CurrencyID FROM Currencies WHERE CurrencyCode = @CurrencyCode AND IsActive = 1;
    
    IF @CurrencyID IS NULL
    BEGIN
        ROLLBACK TRANSACTION;
        RAISERROR('Currency not found or inactive', 16, 1);
        RETURN;
    END
    
    -- Get current balance
    SELECT @CurrentBalance = ISNULL(Balance, 0) 
    FROM PlayerCurrencies 
    WHERE PlayerID = @PlayerID AND CurrencyID = @CurrencyID;
    
    -- Calculate new balance
    SET @NewBalance = @CurrentBalance + @Amount;
    
    -- Prevent negative balances for spending
    IF @NewBalance < 0 AND @TransactionType = 'SPEND'
    BEGIN
        ROLLBACK TRANSACTION;
        RAISERROR('Insufficient balance', 16, 1);
        RETURN;
    END
    
    -- Update or insert player currency
    IF EXISTS (SELECT 1 FROM PlayerCurrencies WHERE PlayerID = @PlayerID AND CurrencyID = @CurrencyID)
    BEGIN
        UPDATE PlayerCurrencies 
        SET Balance = @NewBalance,
            TotalEarned = TotalEarned + CASE WHEN @Amount > 0 THEN @Amount ELSE 0 END,
            TotalSpent = TotalSpent + CASE WHEN @Amount < 0 THEN ABS(@Amount) ELSE 0 END,
            LastUpdated = GETUTCDATE()
        WHERE PlayerID = @PlayerID AND CurrencyID = @CurrencyID;
    END
    ELSE
    BEGIN
        INSERT INTO PlayerCurrencies (PlayerID, CurrencyID, Balance, TotalEarned, TotalSpent)
        VALUES (@PlayerID, @CurrencyID, @NewBalance, 
                CASE WHEN @Amount > 0 THEN @Amount ELSE 0 END,
                CASE WHEN @Amount < 0 THEN ABS(@Amount) ELSE 0 END);
    END
    
    -- Log transaction
    INSERT INTO CurrencyTransactions 
    (PlayerID, CurrencyID, TransactionType, Amount, BalanceBefore, BalanceAfter, Source, Reference)
    VALUES 
    (@PlayerID, @CurrencyID, @TransactionType, @Amount, @CurrentBalance, @NewBalance, @Source, @Reference);
    
    COMMIT TRANSACTION;
    
    -- Return new balance
    SELECT @NewBalance as NewBalance;
END;

-- Database maintenance and optimization procedures
CREATE PROCEDURE sp_ArchiveOldSessions
    @DaysToKeep INT = 30
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Archive old sessions to separate table
    INSERT INTO GameSessionsArchive 
    SELECT * FROM GameSessions 
    WHERE StartTime < DATEADD(DAY, -@DaysToKeep, GETUTCDATE());
    
    -- Delete archived sessions
    DELETE FROM GameSessions 
    WHERE StartTime < DATEADD(DAY, -@DaysToKeep, GETUTCDATE());
    
    SELECT @@ROWCOUNT as ArchivedRows;
END;

-- Indexes for performance optimization
CREATE INDEX IX_PlayerEvents_Composite ON PlayerEvents (PlayerID, EventType, CreatedAt);
CREATE INDEX IX_CurrencyTransactions_Composite ON CurrencyTransactions (PlayerID, CurrencyID, CreatedAt);
CREATE INDEX IX_GameSessions_Duration ON GameSessions (DurationMinutes) WHERE DurationMinutes IS NOT NULL;

-- Partitioning strategy for large tables (SQL Server 2016+)
-- Partition PlayerEvents by date for better performance
CREATE PARTITION FUNCTION pf_PlayerEvents_Date (DATETIME2)
AS RANGE RIGHT FOR VALUES 
('2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01', 
 '2024-05-01', '2024-06-01', '2024-07-01', '2024-08-01',
 '2024-09-01', '2024-10-01', '2024-11-01', '2024-12-01');

CREATE PARTITION SCHEME ps_PlayerEvents_Date
AS PARTITION pf_PlayerEvents_Date ALL TO ([PRIMARY]);

-- Apply partitioning to PlayerEvents table (requires table recreation)
-- This would be done during initial schema creation
```

## 🚀 AI/LLM Integration Opportunities

### Intelligent Database Operations
- **Query Optimization**: AI analyzes query patterns and suggests performance improvements
- **Predictive Scaling**: AI forecasts database load and automatically adjusts resources
- **Anomaly Detection**: AI identifies unusual database patterns and potential issues
- **Data Insights**: AI generates business intelligence reports from game data
- **Schema Evolution**: AI suggests database schema changes based on usage patterns

### Advanced Database Automation
- **Smart Indexing**: AI creates optimal indexes based on query patterns
- **Automated Maintenance**: AI schedules and executes database maintenance tasks
- **Capacity Planning**: AI predicts storage and performance requirements
- **Cost Optimization**: AI suggests database configuration changes to reduce costs
- **Data Quality**: AI detects and suggests fixes for data quality issues

## 💡 Key Highlights

### Enterprise Database Architecture
1. **Multi-Database Strategy**: SQL for transactions, NoSQL for documents, Redis for cache, time-series for analytics
2. **High Performance**: Connection pooling, query caching, batch operations, optimized indexes
3. **Scalability**: Horizontal partitioning, read replicas, distributed caching
4. **Reliability**: ACID compliance, backup strategies, disaster recovery, health monitoring
5. **Security**: Encryption at rest and in transit, SQL injection prevention, access control

### Advanced Database Features
- **Real-time Analytics**: InfluxDB integration for time-series game metrics
- **Document Storage**: MongoDB for flexible game content and user-generated data
- **Caching Layer**: Redis for session management and frequently accessed data
- **Search Capabilities**: Full-text search integration for game content discovery
- **Audit Trails**: Comprehensive transaction logging for compliance and debugging

### Career Development Impact
- **Database Architecture**: Demonstrates ability to design complex, scalable database systems
- **Performance Engineering**: Skills in optimizing database performance for high-load applications
- **Data Management**: Understanding of data lifecycle, retention, and compliance requirements
- **Business Intelligence**: Ability to extract business insights from large datasets
- **Enterprise Integration**: Knowledge of integrating databases with enterprise systems

This comprehensive database mastery positions you as a Unity developer who understands enterprise-grade data management and can build games with sophisticated backend systems that scale to millions of players.