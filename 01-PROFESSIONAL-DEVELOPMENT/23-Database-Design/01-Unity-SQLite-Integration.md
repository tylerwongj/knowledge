# 01-Unity-SQLite-Integration.md

## 🎯 Learning Objectives
- Master SQLite database integration for Unity local data storage
- Implement efficient ORM patterns for Unity game data management
- Design optimized database schemas for game progression and analytics
- Develop robust data migration and versioning strategies for Unity games

## 🔧 Unity SQLite Implementation

### SQLite Database Manager
```csharp
// Scripts/Database/SQLiteManager.cs
using System;
using System.Collections.Generic;
using System.Data;
using System.IO;
using UnityEngine;
using Mono.Data.Sqlite;

public class SQLiteManager : MonoBehaviour
{
    [Header("Database Configuration")]
    [SerializeField] private string databaseName = "GameDatabase.db";
    [SerializeField] private int databaseVersion = 1;
    [SerializeField] private bool enableLogging = true;
    [SerializeField] private bool enableBackups = true;
    [SerializeField] private int maxBackupCount = 5;
    
    public static SQLiteManager Instance { get; private set; }
    
    // Properties
    public string DatabasePath { get; private set; }
    public bool IsConnected { get; private set; }
    public int CurrentVersion { get; private set; }
    
    // Events
    public System.Action OnDatabaseReady;
    public System.Action<string> OnDatabaseError;
    public System.Action<int, int> OnDatabaseUpgrade;
    
    private IDbConnection connection;
    private readonly object lockObject = new object();
    
    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeDatabase();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    private void InitializeDatabase()
    {
        try
        {
            DatabasePath = Path.Combine(Application.persistentDataPath, databaseName);
            
            Log($"Initializing database at: {DatabasePath}");
            
            // Create connection
            string connectionString = $"URI=file:{DatabasePath}";
            connection = new SqliteConnection(connectionString);
            connection.Open();
            
            IsConnected = true;
            
            // Check/create version table
            CreateVersionTable();
            
            // Get current version
            CurrentVersion = GetDatabaseVersion();
            
            // Upgrade if necessary
            if (CurrentVersion < databaseVersion)
            {
                UpgradeDatabase(CurrentVersion, databaseVersion);
            }
            
            // Create core tables
            CreateCoreTables();
            
            Log($"Database initialized successfully (v{CurrentVersion})");
            OnDatabaseReady?.Invoke();
        }
        catch (Exception e)
        {
            LogError($"Database initialization failed: {e.Message}");
            OnDatabaseError?.Invoke(e.Message);
        }
    }
    
    private void CreateVersionTable()
    {
        string sql = @"
            CREATE TABLE IF NOT EXISTS database_version (
                id INTEGER PRIMARY KEY,
                version INTEGER NOT NULL,
                upgraded_at TEXT NOT NULL
            )";
        
        ExecuteNonQuery(sql);
        
        // Insert initial version if not exists
        if (GetDatabaseVersion() == 0)
        {
            string insertSql = @"
                INSERT INTO database_version (id, version, upgraded_at) 
                VALUES (1, @version, @timestamp)";
            
            var parameters = new Dictionary<string, object>
            {
                {"@version", databaseVersion},
                {"@timestamp", DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss")}
            };
            
            ExecuteNonQuery(insertSql, parameters);
        }
    }
    
    private int GetDatabaseVersion()
    {
        try
        {
            string sql = "SELECT version FROM database_version WHERE id = 1";
            var result = ExecuteScalar(sql);
            return result != null ? Convert.ToInt32(result) : 0;
        }
        catch
        {
            return 0;
        }
    }
    
    private void UpgradeDatabase(int fromVersion, int toVersion)
    {
        Log($"Upgrading database from v{fromVersion} to v{toVersion}");
        
        // Create backup before upgrade
        if (enableBackups)
        {
            CreateBackup($"pre_upgrade_v{fromVersion}_to_v{toVersion}");
        }
        
        try
        {
            BeginTransaction();
            
            // Apply migration scripts
            for (int version = fromVersion + 1; version <= toVersion; version++)
            {
                ApplyMigration(version);
            }
            
            // Update version
            string updateVersionSql = @"
                UPDATE database_version 
                SET version = @version, upgraded_at = @timestamp 
                WHERE id = 1";
            
            var parameters = new Dictionary<string, object>
            {
                {"@version", toVersion},
                {"@timestamp", DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss")}
            };
            
            ExecuteNonQuery(updateVersionSql, parameters);
            
            CommitTransaction();
            
            CurrentVersion = toVersion;
            OnDatabaseUpgrade?.Invoke(fromVersion, toVersion);
            
            Log($"Database upgraded successfully to v{toVersion}");
        }
        catch (Exception e)
        {
            RollbackTransaction();
            LogError($"Database upgrade failed: {e.Message}");
            throw;
        }
    }
    
    private void ApplyMigration(int version)
    {
        Log($"Applying migration for version {version}");
        
        switch (version)
        {
            case 1:
                // Initial schema - handled by CreateCoreTables
                break;
            case 2:
                ApplyMigrationV2();
                break;
            case 3:
                ApplyMigrationV3();
                break;
            // Add more migrations as needed
            default:
                LogError($"No migration script found for version {version}");
                break;
        }
    }
    
    private void ApplyMigrationV2()
    {
        // Example migration: Add analytics table
        string sql = @"
            CREATE TABLE IF NOT EXISTS analytics_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                event_data TEXT,
                player_id TEXT,
                timestamp TEXT NOT NULL,
                sent_to_server INTEGER DEFAULT 0
            )";
        
        ExecuteNonQuery(sql);
        
        // Add index for better performance
        ExecuteNonQuery("CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics_events(timestamp)");
        ExecuteNonQuery("CREATE INDEX IF NOT EXISTS idx_analytics_player ON analytics_events(player_id)");
    }
    
    private void ApplyMigrationV3()
    {
        // Example migration: Add achievements system
        string sql = @"
            CREATE TABLE IF NOT EXISTS achievements (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                progress INTEGER DEFAULT 0,
                target INTEGER NOT NULL,
                unlocked INTEGER DEFAULT 0,
                unlocked_at TEXT,
                created_at TEXT NOT NULL
            )";
        
        ExecuteNonQuery(sql);
    }
    
    private void CreateCoreTables()
    {
        // Player data table
        string playerTableSql = @"
            CREATE TABLE IF NOT EXISTS players (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT,
                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,
                coins INTEGER DEFAULT 0,
                gems INTEGER DEFAULT 0,
                last_login TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )";
        
        ExecuteNonQuery(playerTableSql);
        
        // Game sessions table
        string sessionsTableSql = @"
            CREATE TABLE IF NOT EXISTS game_sessions (
                id TEXT PRIMARY KEY,
                player_id TEXT NOT NULL,
                game_mode TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration INTEGER,
                score INTEGER DEFAULT 0,
                level_reached INTEGER DEFAULT 1,
                session_data TEXT,
                FOREIGN KEY (player_id) REFERENCES players (id)
            )";
        
        ExecuteNonQuery(sessionsTableSql);
        
        // Player inventory table
        string inventoryTableSql = @"
            CREATE TABLE IF NOT EXISTS player_inventory (
                id TEXT PRIMARY KEY,
                player_id TEXT NOT NULL,
                item_id TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                acquired_at TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (player_id) REFERENCES players (id)
            )";
        
        ExecuteNonQuery(inventoryTableSql);
        
        // Player progress table
        string progressTableSql = @"
            CREATE TABLE IF NOT EXISTS player_progress (
                id TEXT PRIMARY KEY,
                player_id TEXT NOT NULL,
                level_id TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                best_score INTEGER DEFAULT 0,
                stars INTEGER DEFAULT 0,
                completion_time INTEGER,
                first_completed_at TEXT,
                last_played_at TEXT,
                play_count INTEGER DEFAULT 0,
                FOREIGN KEY (player_id) REFERENCES players (id)
            )";
        
        ExecuteNonQuery(progressTableSql);
        
        // Settings table
        string settingsTableSql = @"
            CREATE TABLE IF NOT EXISTS player_settings (
                player_id TEXT PRIMARY KEY,
                settings_data TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (player_id) REFERENCES players (id)
            )";
        
        ExecuteNonQuery(settingsTableSql);
        
        // Create indexes for better performance
        CreateIndexes();
    }
    
    private void CreateIndexes()
    {
        string[] indexes = {
            "CREATE INDEX IF NOT EXISTS idx_sessions_player ON game_sessions(player_id)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON game_sessions(start_time)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_player ON player_inventory(player_id)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_item ON player_inventory(item_id)",
            "CREATE INDEX IF NOT EXISTS idx_progress_player ON player_progress(player_id)",
            "CREATE INDEX IF NOT EXISTS idx_progress_level ON player_progress(level_id)",
            "CREATE INDEX IF NOT EXISTS idx_players_username ON players(username)",
            "CREATE INDEX IF NOT EXISTS idx_players_email ON players(email)"
        };
        
        foreach (string index in indexes)
        {
            ExecuteNonQuery(index);
        }
    }
    
    // Core Database Operations
    public int ExecuteNonQuery(string sql, Dictionary<string, object> parameters = null)
    {
        lock (lockObject)
        {
            try
            {
                using (var command = connection.CreateCommand())
                {
                    command.CommandText = sql;
                    
                    if (parameters != null)
                    {
                        foreach (var param in parameters)
                        {
                            var parameter = command.CreateParameter();
                            parameter.ParameterName = param.Key;
                            parameter.Value = param.Value ?? DBNull.Value;
                            command.Parameters.Add(parameter);
                        }
                    }
                    
                    int result = command.ExecuteNonQuery();
                    Log($"Executed query: {sql} (affected rows: {result})");
                    return result;
                }
            }
            catch (Exception e)
            {
                LogError($"ExecuteNonQuery failed: {e.Message}\\nSQL: {sql}");
                throw;
            }
        }
    }
    
    public object ExecuteScalar(string sql, Dictionary<string, object> parameters = null)
    {
        lock (lockObject)
        {
            try
            {
                using (var command = connection.CreateCommand())
                {
                    command.CommandText = sql;
                    
                    if (parameters != null)
                    {
                        foreach (var param in parameters)
                        {
                            var parameter = command.CreateParameter();
                            parameter.ParameterName = param.Key;
                            parameter.Value = param.Value ?? DBNull.Value;
                            command.Parameters.Add(parameter);
                        }
                    }
                    
                    object result = command.ExecuteScalar();
                    Log($"Executed scalar query: {sql}");
                    return result;
                }
            }
            catch (Exception e)
            {
                LogError($"ExecuteScalar failed: {e.Message}\\nSQL: {sql}");
                throw;
            }
        }
    }
    
    public List<Dictionary<string, object>> ExecuteQuery(string sql, Dictionary<string, object> parameters = null)
    {
        lock (lockObject)
        {
            var results = new List<Dictionary<string, object>>();
            
            try
            {
                using (var command = connection.CreateCommand())
                {
                    command.CommandText = sql;
                    
                    if (parameters != null)
                    {
                        foreach (var param in parameters)
                        {
                            var parameter = command.CreateParameter();
                            parameter.ParameterName = param.Key;
                            parameter.Value = param.Value ?? DBNull.Value;
                            command.Parameters.Add(parameter);
                        }
                    }
                    
                    using (var reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            var row = new Dictionary<string, object>();
                            
                            for (int i = 0; i < reader.FieldCount; i++)
                            {
                                string columnName = reader.GetName(i);
                                object value = reader.IsDBNull(i) ? null : reader.GetValue(i);
                                row[columnName] = value;
                            }
                            
                            results.Add(row);
                        }
                    }
                }
                
                Log($"Executed query: {sql} (returned {results.Count} rows)");
                return results;
            }
            catch (Exception e)
            {
                LogError($"ExecuteQuery failed: {e.Message}\\nSQL: {sql}");
                throw;
            }
        }
    }
    
    // Transaction Management
    private IDbTransaction currentTransaction;
    
    public void BeginTransaction()
    {
        lock (lockObject)
        {
            if (currentTransaction != null)
            {
                throw new InvalidOperationException("Transaction already in progress");
            }
            
            currentTransaction = connection.BeginTransaction();
            Log("Transaction started");
        }
    }
    
    public void CommitTransaction()
    {
        lock (lockObject)
        {
            if (currentTransaction == null)
            {
                throw new InvalidOperationException("No transaction in progress");
            }
            
            currentTransaction.Commit();
            currentTransaction.Dispose();
            currentTransaction = null;
            Log("Transaction committed");
        }
    }
    
    public void RollbackTransaction()
    {
        lock (lockObject)
        {
            if (currentTransaction == null)
            {
                throw new InvalidOperationException("No transaction in progress");
            }
            
            currentTransaction.Rollback();
            currentTransaction.Dispose();
            currentTransaction = null;
            Log("Transaction rolled back");
        }
    }
    
    // Backup and Restore
    public void CreateBackup(string backupName = null)
    {
        if (!enableBackups) return;
        
        try
        {
            string timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
            string filename = backupName ?? $"backup_{timestamp}";
            string backupPath = Path.Combine(Application.persistentDataPath, $"{filename}.db");
            
            File.Copy(DatabasePath, backupPath, true);
            
            Log($"Database backup created: {backupPath}");
            
            // Clean up old backups
            CleanupOldBackups();
        }
        catch (Exception e)
        {
            LogError($"Backup creation failed: {e.Message}");
        }
    }
    
    private void CleanupOldBackups()
    {
        try
        {
            string backupPattern = "backup_*.db";
            string[] backupFiles = Directory.GetFiles(Application.persistentDataPath, backupPattern);
            
            if (backupFiles.Length > maxBackupCount)
            {
                Array.Sort(backupFiles);
                
                int filesToDelete = backupFiles.Length - maxBackupCount;
                for (int i = 0; i < filesToDelete; i++)
                {
                    File.Delete(backupFiles[i]);
                    Log($"Deleted old backup: {Path.GetFileName(backupFiles[i])}");
                }
            }
        }
        catch (Exception e)
        {
            LogError($"Backup cleanup failed: {e.Message}");
        }
    }
    
    // Utility Methods
    public void VacuumDatabase()
    {
        try
        {
            ExecuteNonQuery("VACUUM");
            Log("Database vacuumed successfully");
        }
        catch (Exception e)
        {
            LogError($"Database vacuum failed: {e.Message}");
        }
    }
    
    public long GetDatabaseSize()
    {
        try
        {
            var fileInfo = new FileInfo(DatabasePath);
            return fileInfo.Length;
        }
        catch
        {
            return 0;
        }
    }
    
    public Dictionary<string, object> GetDatabaseInfo()
    {
        var info = new Dictionary<string, object>
        {
            {"path", DatabasePath},
            {"version", CurrentVersion},
            {"size", GetDatabaseSize()},
            {"isConnected", IsConnected},
            {"created", File.GetCreationTime(DatabasePath)},
            {"lastModified", File.GetLastWriteTime(DatabasePath)}
        };
        
        return info;
    }
    
    // Logging
    private void Log(string message)
    {
        if (enableLogging)
        {
            Debug.Log($"[SQLiteManager] {message}");
        }
    }
    
    private void LogError(string message)
    {
        if (enableLogging)
        {
            Debug.LogError($"[SQLiteManager] {message}");
        }
    }
    
    // Cleanup
    private void OnDestroy()
    {
        if (connection != null)
        {
            if (currentTransaction != null)
            {
                currentTransaction.Rollback();
                currentTransaction.Dispose();
            }
            
            connection.Close();
            connection.Dispose();
            IsConnected = false;
            
            Log("Database connection closed");
        }
    }
    
    private void OnApplicationPause(bool pauseStatus)
    {
        if (pauseStatus && enableBackups)
        {
            CreateBackup("app_pause_backup");
        }
    }
    
    private void OnApplicationFocus(bool hasFocus)
    {
        if (!hasFocus && enableBackups)
        {
            CreateBackup("app_focus_backup");
        }
    }
}
```

### Unity ORM Implementation
```csharp
// Scripts/Database/GameORM.cs
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using UnityEngine;

public class GameORM
{
    private SQLiteManager database;
    
    public GameORM(SQLiteManager databaseManager)
    {
        database = databaseManager;
    }
    
    // Generic CRUD Operations
    public void Insert<T>(T entity) where T : class, new()
    {
        var tableName = GetTableName<T>();
        var properties = GetProperties<T>();
        
        var columns = string.Join(", ", properties.Select(p => p.Name.ToLower()));
        var parameters = string.Join(", ", properties.Select(p => $"@{p.Name.ToLower()}"));
        
        string sql = $"INSERT INTO {tableName} ({columns}) VALUES ({parameters})";
        
        var paramDict = new Dictionary<string, object>();
        foreach (var prop in properties)
        {
            var value = prop.GetValue(entity);
            paramDict[$"@{prop.Name.ToLower()}"] = value ?? DBNull.Value;
        }
        
        database.ExecuteNonQuery(sql, paramDict);
    }
    
    public void Update<T>(T entity) where T : class, new()
    {
        var tableName = GetTableName<T>();
        var properties = GetProperties<T>();
        var keyProperty = GetKeyProperty<T>();
        
        var setClause = string.Join(", ", 
            properties.Where(p => p.Name != keyProperty.Name)
                     .Select(p => $"{p.Name.ToLower()} = @{p.Name.ToLower()}"));
        
        string sql = $"UPDATE {tableName} SET {setClause} WHERE {keyProperty.Name.ToLower()} = @{keyProperty.Name.ToLower()}";
        
        var paramDict = new Dictionary<string, object>();
        foreach (var prop in properties)
        {
            var value = prop.GetValue(entity);
            paramDict[$"@{prop.Name.ToLower()}"] = value ?? DBNull.Value;
        }
        
        database.ExecuteNonQuery(sql, paramDict);
    }
    
    public void Delete<T>(object id) where T : class, new()
    {
        var tableName = GetTableName<T>();
        var keyProperty = GetKeyProperty<T>();
        
        string sql = $"DELETE FROM {tableName} WHERE {keyProperty.Name.ToLower()} = @id";
        
        var paramDict = new Dictionary<string, object>
        {
            {"@id", id}
        };
        
        database.ExecuteNonQuery(sql, paramDict);
    }
    
    public T GetById<T>(object id) where T : class, new()
    {
        var tableName = GetTableName<T>();
        var keyProperty = GetKeyProperty<T>();
        
        string sql = $"SELECT * FROM {tableName} WHERE {keyProperty.Name.ToLower()} = @id";
        
        var paramDict = new Dictionary<string, object>
        {
            {"@id", id}
        };
        
        var results = database.ExecuteQuery(sql, paramDict);
        return results.FirstOrDefault() != null ? MapToEntity<T>(results.First()) : null;
    }
    
    public List<T> GetAll<T>() where T : class, new()
    {
        var tableName = GetTableName<T>();
        string sql = $"SELECT * FROM {tableName}";
        
        var results = database.ExecuteQuery(sql);
        return results.Select(MapToEntity<T>).ToList();
    }
    
    public List<T> Where<T>(string condition, Dictionary<string, object> parameters = null) where T : class, new()
    {
        var tableName = GetTableName<T>();
        string sql = $"SELECT * FROM {tableName} WHERE {condition}";
        
        var results = database.ExecuteQuery(sql, parameters);
        return results.Select(MapToEntity<T>).ToList();
    }
    
    // Advanced Query Methods
    public List<T> GetPaged<T>(int page, int pageSize, string orderBy = null) where T : class, new()
    {
        var tableName = GetTableName<T>();
        var keyProperty = GetKeyProperty<T>();
        
        string orderClause = orderBy ?? keyProperty.Name.ToLower();
        int offset = (page - 1) * pageSize;
        
        string sql = $"SELECT * FROM {tableName} ORDER BY {orderClause} LIMIT @pageSize OFFSET @offset";
        
        var paramDict = new Dictionary<string, object>
        {
            {"@pageSize", pageSize},
            {"@offset", offset}
        };
        
        var results = database.ExecuteQuery(sql, paramDict);
        return results.Select(MapToEntity<T>).ToList();
    }
    
    public int Count<T>(string condition = null, Dictionary<string, object> parameters = null) where T : class, new()
    {
        var tableName = GetTableName<T>();
        string sql = $"SELECT COUNT(*) FROM {tableName}";
        
        if (!string.IsNullOrEmpty(condition))
        {
            sql += $" WHERE {condition}";
        }
        
        var result = database.ExecuteScalar(sql, parameters);
        return Convert.ToInt32(result);
    }
    
    public bool Exists<T>(object id) where T : class, new()
    {
        var tableName = GetTableName<T>();
        var keyProperty = GetKeyProperty<T>();
        
        string sql = $"SELECT COUNT(*) FROM {tableName} WHERE {keyProperty.Name.ToLower()} = @id";
        
        var paramDict = new Dictionary<string, object>
        {
            {"@id", id}
        };
        
        var result = database.ExecuteScalar(sql, paramDict);
        return Convert.ToInt32(result) > 0;
    }
    
    // Batch Operations
    public void InsertBatch<T>(IEnumerable<T> entities) where T : class, new()
    {
        database.BeginTransaction();
        try
        {
            foreach (var entity in entities)
            {
                Insert(entity);
            }
            database.CommitTransaction();
        }
        catch
        {
            database.RollbackTransaction();
            throw;
        }
    }
    
    public void UpdateBatch<T>(IEnumerable<T> entities) where T : class, new()
    {
        database.BeginTransaction();
        try
        {
            foreach (var entity in entities)
            {
                Update(entity);
            }
            database.CommitTransaction();
        }
        catch
        {
            database.RollbackTransaction();
            throw;
        }
    }
    
    // Utility Methods
    private string GetTableName<T>()
    {
        var type = typeof(T);
        var tableAttribute = type.GetCustomAttribute<TableAttribute>();
        return tableAttribute?.Name ?? type.Name.ToLower() + "s";
    }
    
    private PropertyInfo[] GetProperties<T>()
    {
        return typeof(T).GetProperties(BindingFlags.Public | BindingFlags.Instance)
                        .Where(p => p.CanRead && p.CanWrite)
                        .Where(p => p.GetCustomAttribute<IgnoreAttribute>() == null)
                        .ToArray();
    }
    
    private PropertyInfo GetKeyProperty<T>()
    {
        var properties = GetProperties<T>();
        var keyProperty = properties.FirstOrDefault(p => p.GetCustomAttribute<KeyAttribute>() != null);
        return keyProperty ?? properties.FirstOrDefault(p => p.Name.ToLower() == "id");
    }
    
    private T MapToEntity<T>(Dictionary<string, object> row) where T : class, new()
    {
        var entity = new T();
        var properties = GetProperties<T>();
        
        foreach (var property in properties)
        {
            string columnName = property.Name.ToLower();
            
            if (row.ContainsKey(columnName) && row[columnName] != null)
            {
                var value = row[columnName];
                
                // Handle type conversion
                if (property.PropertyType != value.GetType())
                {
                    value = ConvertValue(value, property.PropertyType);
                }
                
                property.SetValue(entity, value);
            }
        }
        
        return entity;
    }
    
    private object ConvertValue(object value, Type targetType)
    {
        if (value == null || value == DBNull.Value)
            return null;
        
        if (targetType.IsGenericType && targetType.GetGenericTypeDefinition() == typeof(Nullable<>))
        {
            targetType = Nullable.GetUnderlyingType(targetType);
        }
        
        if (targetType == typeof(DateTime) && value is string)
        {
            return DateTime.Parse(value.ToString());
        }
        
        if (targetType == typeof(bool) && value is long)
        {
            return Convert.ToInt64(value) != 0;
        }
        
        return Convert.ChangeType(value, targetType);
    }
}

// Attributes for ORM
[AttributeUsage(AttributeTargets.Class)]
public class TableAttribute : Attribute
{
    public string Name { get; }
    
    public TableAttribute(string name)
    {
        Name = name;
    }
}

[AttributeUsage(AttributeTargets.Property)]
public class KeyAttribute : Attribute
{
}

[AttributeUsage(AttributeTargets.Property)]
public class IgnoreAttribute : Attribute
{
}
```

### Game Data Models
```csharp
// Scripts/Database/Models/GameModels.cs
using System;
using System.Collections.Generic;

[Table("players")]
public class Player
{
    [Key]
    public string Id { get; set; }
    public string Username { get; set; }
    public string Email { get; set; }
    public int Level { get; set; } = 1;
    public int Experience { get; set; } = 0;
    public int Coins { get; set; } = 0;
    public int Gems { get; set; } = 0;
    public DateTime? LastLogin { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    
    public Player()
    {
        Id = Guid.NewGuid().ToString();
        CreatedAt = DateTime.UtcNow;
        UpdatedAt = DateTime.UtcNow;
    }
}

[Table("game_sessions")]
public class GameSession
{
    [Key]
    public string Id { get; set; }
    public string PlayerId { get; set; }
    public string GameMode { get; set; }
    public DateTime StartTime { get; set; }
    public DateTime? EndTime { get; set; }
    public int? Duration { get; set; }
    public int Score { get; set; } = 0;
    public int LevelReached { get; set; } = 1;
    public string SessionData { get; set; }
    
    public GameSession()
    {
        Id = Guid.NewGuid().ToString();
        StartTime = DateTime.UtcNow;
    }
    
    public void EndSession(int finalScore, int finalLevel, Dictionary<string, object> data = null)
    {
        EndTime = DateTime.UtcNow;
        Duration = (int)(EndTime.Value - StartTime).TotalSeconds;
        Score = finalScore;
        LevelReached = finalLevel;
        
        if (data != null)
        {
            SessionData = Newtonsoft.Json.JsonConvert.SerializeObject(data);
        }
    }
}

[Table("player_inventory")]
public class InventoryItem
{
    [Key]
    public string Id { get; set; }
    public string PlayerId { get; set; }
    public string ItemId { get; set; }
    public int Quantity { get; set; } = 1;
    public DateTime AcquiredAt { get; set; }
    public string Metadata { get; set; }
    
    public InventoryItem()
    {
        Id = Guid.NewGuid().ToString();
        AcquiredAt = DateTime.UtcNow;
    }
    
    public InventoryItem(string playerId, string itemId, int quantity = 1) : this()
    {
        PlayerId = playerId;
        ItemId = itemId;
        Quantity = quantity;
    }
}

[Table("player_progress")]
public class PlayerProgress
{
    [Key]
    public string Id { get; set; }
    public string PlayerId { get; set; }
    public string LevelId { get; set; }
    public bool Completed { get; set; } = false;
    public int BestScore { get; set; } = 0;
    public int Stars { get; set; } = 0;
    public int? CompletionTime { get; set; }
    public DateTime? FirstCompletedAt { get; set; }
    public DateTime? LastPlayedAt { get; set; }
    public int PlayCount { get; set; } = 0;
    
    public PlayerProgress()
    {
        Id = Guid.NewGuid().ToString();
    }
    
    public PlayerProgress(string playerId, string levelId) : this()
    {
        PlayerId = playerId;
        LevelId = levelId;
    }
    
    public void UpdateProgress(int score, int stars, int completionTime)
    {
        PlayCount++;
        LastPlayedAt = DateTime.UtcNow;
        
        if (score > BestScore)
        {
            BestScore = score;
        }
        
        if (stars > Stars)
        {
            Stars = stars;
        }
        
        if (!Completed && stars > 0)
        {
            Completed = true;
            FirstCompletedAt = DateTime.UtcNow;
        }
        
        if (CompletionTime == null || completionTime < CompletionTime)
        {
            CompletionTime = completionTime;
        }
    }
}

[Table("player_settings")]
public class PlayerSettings
{
    [Key]
    public string PlayerId { get; set; }
    public string SettingsData { get; set; }
    public DateTime UpdatedAt { get; set; }
    
    [Ignore]
    public Dictionary<string, object> Settings
    {
        get
        {
            if (string.IsNullOrEmpty(SettingsData))
                return new Dictionary<string, object>();
            
            return Newtonsoft.Json.JsonConvert.DeserializeObject<Dictionary<string, object>>(SettingsData);
        }
        set
        {
            SettingsData = Newtonsoft.Json.JsonConvert.SerializeObject(value);
            UpdatedAt = DateTime.UtcNow;
        }
    }
    
    public PlayerSettings()
    {
        UpdatedAt = DateTime.UtcNow;
    }
    
    public PlayerSettings(string playerId) : this()
    {
        PlayerId = playerId;
        Settings = new Dictionary<string, object>();
    }
}

[Table("analytics_events")]
public class AnalyticsEvent
{
    [Key]
    public int Id { get; set; }
    public string EventName { get; set; }
    public string EventData { get; set; }
    public string PlayerId { get; set; }
    public DateTime Timestamp { get; set; }
    public bool SentToServer { get; set; } = false;
    
    public AnalyticsEvent()
    {
        Timestamp = DateTime.UtcNow;
    }
    
    public AnalyticsEvent(string eventName, string playerId, Dictionary<string, object> data = null) : this()
    {
        EventName = eventName;
        PlayerId = playerId;
        
        if (data != null)
        {
            EventData = Newtonsoft.Json.JsonConvert.SerializeObject(data);
        }
    }
}

[Table("achievements")]
public class Achievement
{
    [Key]
    public string Id { get; set; }
    public string Name { get; set; }
    public string Description { get; set; }
    public int Progress { get; set; } = 0;
    public int Target { get; set; }
    public bool Unlocked { get; set; } = false;
    public DateTime? UnlockedAt { get; set; }
    public DateTime CreatedAt { get; set; }
    
    public Achievement()
    {
        CreatedAt = DateTime.UtcNow;
    }
    
    public Achievement(string id, string name, string description, int target) : this()
    {
        Id = id;
        Name = name;
        Description = description;
        Target = target;
    }
    
    public void UpdateProgress(int newProgress)
    {
        Progress = Math.Min(newProgress, Target);
        
        if (!Unlocked && Progress >= Target)
        {
            Unlocked = true;
            UnlockedAt = DateTime.UtcNow;
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Database Schema Design
```
PROMPT TEMPLATE - Unity SQLite Schema Design:

"Design an optimal SQLite database schema for this Unity game:

Game Details:
- Type: [RPG/Puzzle/Strategy/Action/etc.]
- Platform: [Mobile/PC/Console/Cross-platform]
- Features: [Progression/Inventory/Social/Analytics/etc.]
- Data Volume: [Estimated players and session data]

Create schema including:
1. Core player data tables with relationships
2. Game progression and achievement tracking
3. Inventory and item management system
4. Analytics and telemetry data capture
5. Settings and preferences storage
6. Optimized indexes for performance
7. Migration scripts for version updates
8. Data validation and constraints"
```

### ORM Performance Optimization
```
PROMPT TEMPLATE - Unity Database Performance:

"Optimize this Unity SQLite integration for performance:

```csharp
[PASTE YOUR DATABASE CODE]
```

Performance Requirements:
- Platform: [Mobile constraints/PC performance/etc.]
- Data Volume: [Expected records and growth]
- Usage Patterns: [Read-heavy/Write-heavy/Mixed]
- Performance Goals: [Response time targets]

Provide optimizations for:
1. Query optimization and indexing strategies
2. Connection pooling and transaction management
3. Batch operations and bulk data handling
4. Memory usage and garbage collection
5. Background processing and threading
6. Cache strategies and data lifecycle
7. Database maintenance and cleanup
8. Performance monitoring and profiling"
```

## 💡 Key SQLite Integration Principles

### Essential Unity Database Checklist
- **ACID compliance** - Ensure data consistency with proper transactions
- **Performance optimization** - Use indexes and efficient queries
- **Data migration** - Handle schema changes gracefully
- **Backup strategies** - Implement automatic backup and recovery
- **Memory management** - Optimize for mobile memory constraints
- **Threading safety** - Handle concurrent access properly
- **Error handling** - Robust error recovery and logging
- **Security measures** - Encrypt sensitive data appropriately

### Common Unity SQLite Challenges
1. **Platform differences** - SQLite behavior varies across platforms
2. **Threading issues** - Unity main thread limitations with database operations
3. **Memory constraints** - Large datasets on mobile devices
4. **Migration complexity** - Handling schema changes without data loss
5. **Performance bottlenecks** - Inefficient queries affecting frame rate
6. **Backup reliability** - Ensuring data safety across app updates
7. **Debugging difficulty** - Limited debugging tools for database issues
8. **Security concerns** - Protecting sensitive player data

This comprehensive SQLite integration provides Unity developers with robust local data storage capabilities, enabling efficient player progression tracking, analytics collection, and offline game functionality while maintaining excellent performance and data integrity.