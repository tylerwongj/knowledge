# @b-SQL-Server-Unity-Integration

## 🎯 Learning Objectives
- Integrate SQL Server with Unity games for persistent data storage
- Implement secure database connections and authentication
- Master Entity Framework Core for Unity backend services
- Design scalable data access patterns for multiplayer games

## 🔧 Unity-SQL Server Connection Setup

### Connection String Configuration
```csharp
// Unity GameData Manager
using System.Data.SqlClient;
using UnityEngine;

public class DatabaseManager : MonoBehaviour
{
    [SerializeField] private string connectionString;
    private SqlConnection connection;
    
    void Start()
    {
        // Production: Store in secure configuration
        connectionString = "Server=your-server.database.windows.net;" +
                          "Database=UnityGameDB;" +
                          "User Id=gameuser;" +
                          "Password=SecurePassword123!;" +
                          "Encrypt=True;" +
                          "TrustServerCertificate=False;" +
                          "Connection Timeout=30;";
        
        InitializeConnection();
    }
    
    private async void InitializeConnection()
    {
        try
        {
            connection = new SqlConnection(connectionString);
            await connection.OpenAsync();
            Debug.Log("Database connection established successfully");
        }
        catch (SqlException ex)
        {
            Debug.LogError($"Database connection failed: {ex.Message}");
        }
    }
}
```

### Entity Framework Core Integration
```csharp
// DbContext for Unity Game
using Microsoft.EntityFrameworkCore;

public class UnityGameContext : DbContext
{
    public DbSet<Player> Players { get; set; }
    public DbSet<GameSession> GameSessions { get; set; }
    public DbSet<PlayerInventory> PlayerInventory { get; set; }
    public DbSet<Achievement> Achievements { get; set; }
    
    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        optionsBuilder.UseSqlServer(GetConnectionString());
        optionsBuilder.EnableSensitiveDataLogging(false); // Production: false
    }
    
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // Player Entity Configuration
        modelBuilder.Entity<Player>(entity =>
        {
            entity.HasKey(p => p.PlayerId);
            entity.Property(p => p.Username).HasMaxLength(50).IsRequired();
            entity.Property(p => p.Email).HasMaxLength(100).IsRequired();
            entity.HasIndex(p => p.Username).IsUnique();
            entity.HasIndex(p => p.Email).IsUnique();
        });
        
        // Player Inventory Configuration
        modelBuilder.Entity<PlayerInventory>(entity =>
        {
            entity.HasKey(pi => new { pi.PlayerId, pi.ItemId });
            entity.HasOne(pi => pi.Player)
                  .WithMany(p => p.Inventory)
                  .HasForeignKey(pi => pi.PlayerId);
        });
    }
}

// Entity Models
public class Player
{
    public Guid PlayerId { get; set; }
    public string Username { get; set; }
    public string Email { get; set; }
    public DateTime CreatedDate { get; set; }
    public DateTime? LastLoginDate { get; set; }
    public int PlayerLevel { get; set; }
    public decimal Currency { get; set; }
    
    // Navigation Properties
    public ICollection<PlayerInventory> Inventory { get; set; }
    public ICollection<GameSession> GameSessions { get; set; }
}
```

## 🔧 Unity Data Access Patterns

### Repository Pattern Implementation
```csharp
// Generic Repository Interface
public interface IRepository<T> where T : class
{
    Task<T> GetByIdAsync(object id);
    Task<IEnumerable<T>> GetAllAsync();
    Task<T> AddAsync(T entity);
    Task UpdateAsync(T entity);
    Task DeleteAsync(object id);
}

// Player Repository Implementation
public class PlayerRepository : IRepository<Player>
{
    private readonly UnityGameContext _context;
    
    public PlayerRepository(UnityGameContext context)
    {
        _context = context;
    }
    
    public async Task<Player> GetByIdAsync(object id)
    {
        return await _context.Players
            .Include(p => p.Inventory)
            .FirstOrDefaultAsync(p => p.PlayerId == (Guid)id);
    }
    
    public async Task<Player> GetByUsernameAsync(string username)
    {
        return await _context.Players
            .Include(p => p.Inventory)
            .FirstOrDefaultAsync(p => p.Username == username);
    }
    
    public async Task<Player> AddAsync(Player player)
    {
        _context.Players.Add(player);
        await _context.SaveChangesAsync();
        return player;
    }
    
    public async Task UpdatePlayerStatsAsync(Guid playerId, int experience, int level)
    {
        var player = await _context.Players.FindAsync(playerId);
        if (player != null)
        {
            player.Experience += experience;
            player.PlayerLevel = level;
            player.LastLoginDate = DateTime.UtcNow;
            await _context.SaveChangesAsync();
        }
    }
}
```

### Unity Service Layer
```csharp
// Player Service for Unity Integration
public class PlayerService : MonoBehaviour
{
    private PlayerRepository playerRepository;
    private UnityGameContext dbContext;
    
    void Start()
    {
        dbContext = new UnityGameContext();
        playerRepository = new PlayerRepository(dbContext);
    }
    
    public async Task<bool> AuthenticatePlayerAsync(string username)
    {
        try
        {
            var player = await playerRepository.GetByUsernameAsync(username);
            if (player != null)
            {
                // Update last login
                await playerRepository.UpdateAsync(player);
                LoadPlayerData(player);
                return true;
            }
            return false;
        }
        catch (Exception ex)
        {
            Debug.LogError($"Authentication failed: {ex.Message}");
            return false;
        }
    }
    
    private void LoadPlayerData(Player player)
    {
        // Update Unity GameManager with player data
        GameManager.Instance.SetCurrentPlayer(player);
        UIManager.Instance.UpdatePlayerInfo(player.Username, player.PlayerLevel);
    }
    
    public async Task SavePlayerProgressAsync(int experience, int level, Vector3 position)
    {
        var playerId = GameManager.Instance.CurrentPlayer.PlayerId;
        await playerRepository.UpdatePlayerStatsAsync(playerId, experience, level);
        
        // Save position data
        await SavePlayerPositionAsync(playerId, position);
    }
}
```

## 🚀 Advanced Unity-Database Integration

### Real-time Multiplayer Data Sync
```csharp
// Real-time Player Position Sync
public class MultiplayerSyncService : MonoBehaviour
{
    private readonly Timer syncTimer;
    private const int SYNC_INTERVAL_MS = 100; // 10 FPS sync rate
    
    void Start()
    {
        syncTimer = new Timer(SyncPlayerPositions, null, 0, SYNC_INTERVAL_MS);
    }
    
    private async void SyncPlayerPositions(object state)
    {
        var activePlayers = FindObjectsOfType<PlayerController>();
        var positionUpdates = new List<PlayerPositionUpdate>();
        
        foreach (var player in activePlayers)
        {
            positionUpdates.Add(new PlayerPositionUpdate
            {
                PlayerId = player.PlayerId,
                Position = player.transform.position,
                Rotation = player.transform.rotation,
                Timestamp = DateTime.UtcNow
            });
        }
        
        await BatchUpdatePlayerPositionsAsync(positionUpdates);
    }
    
    private async Task BatchUpdatePlayerPositionsAsync(List<PlayerPositionUpdate> updates)
    {
        using var context = new UnityGameContext();
        
        var sql = @"
            MERGE PlayerPositions AS target
            USING (VALUES ";
        
        var parameters = new List<SqlParameter>();
        for (int i = 0; i < updates.Count; i++)
        {
            sql += $"(@PlayerId{i}, @PosX{i}, @PosY{i}, @PosZ{i}, @RotX{i}, @RotY{i}, @RotZ{i}, @RotW{i}, @Timestamp{i})";
            if (i < updates.Count - 1) sql += ", ";
            
            parameters.AddRange(new[]
            {
                new SqlParameter($"@PlayerId{i}", updates[i].PlayerId),
                new SqlParameter($"@PosX{i}", updates[i].Position.x),
                new SqlParameter($"@PosY{i}", updates[i].Position.y),
                new SqlParameter($"@PosZ{i}", updates[i].Position.z),
                new SqlParameter($"@RotX{i}", updates[i].Rotation.x),
                new SqlParameter($"@RotY{i}", updates[i].Rotation.y),
                new SqlParameter($"@RotZ{i}", updates[i].Rotation.z),
                new SqlParameter($"@RotW{i}", updates[i].Rotation.w),
                new SqlParameter($"@Timestamp{i}", updates[i].Timestamp)
            });
        }
        
        sql += @") AS source (PlayerId, PosX, PosY, PosZ, RotX, RotY, RotZ, RotW, Timestamp)
               ON target.PlayerId = source.PlayerId
               WHEN MATCHED THEN UPDATE SET
                   PosX = source.PosX, PosY = source.PosY, PosZ = source.PosZ,
                   RotX = source.RotX, RotY = source.RotY, RotZ = source.RotZ, RotW = source.RotW,
                   LastUpdated = source.Timestamp
               WHEN NOT MATCHED THEN INSERT
                   (PlayerId, PosX, PosY, PosZ, RotX, RotY, RotZ, RotW, LastUpdated)
                   VALUES (source.PlayerId, source.PosX, source.PosY, source.PosZ,
                          source.RotX, source.RotY, source.RotZ, source.RotW, source.Timestamp);";
        
        await context.Database.ExecuteSqlRawAsync(sql, parameters.ToArray());
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Database Query Generation
```
Prompt: "Generate optimized SQL queries for Unity game analytics: daily active users, player retention by cohort, revenue per user, session duration analysis, and level progression funnel."
```

### Entity Framework Migration Scripts
```
Prompt: "Create Entity Framework Core migrations for adding a guild system to my Unity game database, including guild creation, membership, roles, and guild wars functionality."
```

### Performance Monitoring Queries
```
Prompt: "Write SQL Server performance monitoring queries for Unity game database that track query execution times, deadlocks, connection pool usage, and identify slow-running operations."
```

## 💡 Key Highlights

### Connection Management
- **Connection pooling**: Reuse database connections efficiently
- **Async operations**: Non-blocking database calls in Unity
- **Error handling**: Graceful degradation when database is unavailable
- **Timeout configuration**: Prevent Unity freezing on slow queries
- **Secure credentials**: Environment variables or Azure Key Vault

### Performance Optimization
- **Batch operations**: Group multiple database updates
- **Lazy loading**: Load related data only when needed
- **Caching strategy**: Redis for frequently accessed data
- **Index optimization**: Query performance tuning
- **Connection string tuning**: Pool size, timeout settings

### Security Best Practices
- **SQL injection prevention**: Parameterized queries only
- **Authentication**: Azure AD or SQL Server authentication
- **Encryption**: TLS for data in transit, TDE for data at rest
- **Least privilege**: Database user with minimal required permissions
- **Audit logging**: Track data access and modifications