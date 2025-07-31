# Modern C# Features for Unity & Enterprise Development

## Overview
Comprehensive coverage of modern C# language features from C# 7.0 through C# 12.0, with practical applications in Unity game development and enterprise software engineering.

## Key Concepts

### C# 7.0 - 7.3 Features

**Pattern Matching:**
```csharp
// Traditional approach
public void ProcessGameObject(GameObject obj)
{
    if (obj.GetComponent<Player>() != null)
    {
        var player = obj.GetComponent<Player>();
        player.Move();
    }
    else if (obj.GetComponent<Enemy>() != null)
    {
        var enemy = obj.GetComponent<Enemy>();
        enemy.Attack();
    }
}

// Modern pattern matching
public void ProcessGameObject(GameObject obj)
{
    switch (obj.GetComponent<MonoBehaviour>())
    {
        case Player player:
            player.Move();
            break;
        case Enemy enemy when enemy.IsAlive:
            enemy.Attack();
            break;
        case Enemy enemy when !enemy.IsAlive:
            enemy.Despawn();
            break;
        case null:
            Debug.LogWarning("No component found");
            break;
    }
}

// Property pattern matching (C# 8.0+)
public string GetPlayerStatus(Player player) => player switch
{
    { Health: <= 0 } => "Dead",
    { Health: < 30, IsDefending: true } => "Critically Injured but Defending",
    { Health: < 30 } => "Critically Injured",
    { Health: < 70, Mana: > 50 } => "Injured but has Mana",
    { IsDefending: true, Weapon: not null } => "Defending with Weapon",
    _ => "Healthy"
};
```

**Tuples and Deconstruction:**
```csharp
// Method returning multiple values
public (bool success, string message, int score) ProcessPlayerAction(PlayerAction action)
{
    switch (action.Type)
    {
        case ActionType.Attack:
            var damage = CalculateDamage(action);
            return (true, $"Dealt {damage} damage", damage);
        case ActionType.Heal:
            var healAmount = CalculateHeal(action);
            return (true, $"Healed {healAmount} HP", healAmount);
        default:
            return (false, "Invalid action", 0);
    }
}

// Usage with deconstruction
var (success, message, score) = ProcessPlayerAction(playerAction);
if (success)
{
    ShowMessage(message);
    AddToScore(score);
}

// Named tuples for clarity
public (Vector3 position, Quaternion rotation, Vector3 scale) GetTransformData(Transform transform)
{
    return (transform.position, transform.rotation, transform.localScale);
}

// Deconstruction in foreach
var enemies = new Dictionary<string, (int health, int damage)>
{
    ["Goblin"] = (50, 10),
    ["Orc"] = (100, 20),
    ["Dragon"] = (500, 50)
};

foreach (var (enemyType, (health, damage)) in enemies)
{
    Debug.Log($"{enemyType}: HP={health}, DMG={damage}");
}
```

**Local Functions:**
```csharp
public class PathfindingSystem
{
    public List<Vector3> FindPath(Vector3 start, Vector3 end, LayerMask obstacles)
    {
        // Local function with access to parent's parameters
        bool IsValidPosition(Vector3 pos)
        {
            return !Physics.CheckSphere(pos, 0.5f, obstacles);
        }
        
        // Another local function
        float CalculateHeuristic(Vector3 current, Vector3 target)
        {
            return Vector3.Distance(current, target);
        }
        
        // Local async function for expensive operations
        async Task<List<Vector3>> CalculatePathAsync()
        {
            var path = new List<Vector3>();
            // Complex pathfinding logic here
            await Task.Yield(); // Yield control to avoid blocking
            return path;
        }
        
        // Main logic uses local functions
        if (!IsValidPosition(start) || !IsValidPosition(end))
            return new List<Vector3>();
            
        return CalculatePathAsync().Result;
    }
}
```

### C# 8.0 Features

**Nullable Reference Types:**
```csharp
#nullable enable

public class PlayerManager
{
    private Player? currentPlayer; // Explicitly nullable
    private readonly List<Player> players = new(); // Non-nullable
    
    public Player? GetCurrentPlayer() => currentPlayer;
    
    // Null-forgiving operator when you know it's not null
    public void InitializePlayer(string playerName)
    {
        currentPlayer = FindPlayerByName(playerName);
        currentPlayer!.Initialize(); // Tell compiler it's not null
    }
    
    // Null-conditional and null-coalescing patterns
    public string GetPlayerDisplayName()
    {
        return currentPlayer?.Name ?? "No Player Selected";
    }
    
    // Pattern matching with null checks
    public bool TryGetPlayerLevel(out int level)
    {
        level = currentPlayer switch
        {
            null => 0,
            Player p when p.Experience < 100 => 1,
            Player p when p.Experience < 500 => 2,
            Player p => p.Experience / 100
        };
        
        return currentPlayer is not null;
    }
}
```

**Switch Expressions:**
```csharp
public class WeaponSystem
{
    // Traditional switch statement
    public int GetWeaponDamage_Old(WeaponType type)
    {
        switch (type)
        {
            case WeaponType.Sword:
                return 25;
            case WeaponType.Bow:
                return 15;
            case WeaponType.Staff:
                return 30;
            default:
                return 10;
        }
    }
    
    // Modern switch expression
    public int GetWeaponDamage(WeaponType type) => type switch
    {
        WeaponType.Sword => 25,
        WeaponType.Bow => 15,
        WeaponType.Staff => 30,
        _ => 10
    };
    
    // Complex switch expressions with patterns
    public float GetWeaponSpeed(Weapon weapon) => weapon switch
    {
        { Type: WeaponType.Sword, Enchantment: EnchantmentType.Speed } => 2.0f,
        { Type: WeaponType.Sword } => 1.5f,
        { Type: WeaponType.Bow, Durability: > 50 } => 1.8f,
        { Type: WeaponType.Bow } => 1.2f,
        { Type: WeaponType.Staff, MagicPower: var mp } when mp > 100 => 0.8f,
        { Type: WeaponType.Staff } => 1.0f,
        _ => 1.0f
    };
    
    // Tuple patterns in switch expressions
    public string GetCombatResult(int playerHealth, int enemyHealth) => (playerHealth, enemyHealth) switch
    {
        (> 0, <= 0) => "Victory!",
        (<= 0, > 0) => "Defeat!",
        (<= 0, <= 0) => "Draw!",
        var (p, e) when p > e => "Player advantage",
        var (p, e) when e > p => "Enemy advantage",
        _ => "Even match"
    };
}
```

### C# 9.0 Features

**Records for Data Transfer:**
```csharp
// Immutable data records
public record PlayerStats(int Health, int Mana, int Experience, string Name)
{
    // Additional computed properties
    public int Level => Experience / 100 + 1;
    public float HealthPercentage => (float)Health / 100;
    
    // Records support with-expressions for non-destructive mutation
    public PlayerStats TakeDamage(int damage) => this with { Health = Math.Max(0, Health - damage) };
    public PlayerStats GainExperience(int exp) => this with { Experience = Experience + exp };
}

// Usage
var player = new PlayerStats(100, 50, 250, "Hero");
var damagedPlayer = player.TakeDamage(30); // Creates new instance
var leveledPlayer = damagedPlayer.GainExperience(100);

// Record equality and comparison
Console.WriteLine(player == damagedPlayer); // False
Console.WriteLine(player with { Health = 70 } == damagedPlayer); // True
```

**Init-Only Properties:**
```csharp
public class GameConfiguration
{
    public string GameTitle { get; init; } = "Untitled Game";
    public int MaxPlayers { get; init; } = 4;
    public float Difficulty { get; init; } = 1.0f;
    public List<string> AvailableLevels { get; init; } = new();
    
    // Can only be set during initialization
    public DateTime CreatedAt { get; init; } = DateTime.UtcNow;
}

// Usage with object initializer
var config = new GameConfiguration
{
    GameTitle = "Space Adventure",
    MaxPlayers = 8,
    Difficulty = 1.5f,
    AvailableLevels = { "Tutorial", "Level1", "Level2", "Boss" }
};

// config.MaxPlayers = 6; // Compiler error - init-only property
```

### C# 10.0+ Features

**Global Using and File-Scoped Namespaces:**
```csharp
// GlobalUsings.cs
global using System;
global using System.Collections.Generic;
global using System.Linq;
global using UnityEngine;
global using static UnityEngine.Debug;

// PlayerController.cs with file-scoped namespace
namespace Game.Player;

public class PlayerController : MonoBehaviour
{
    // No need for using statements - they're global
    private List<PowerUp> powerUps = new();
    
    void Start()
    {
        Log("Player initialized"); // static using UnityEngine.Debug
    }
}
```

**String Interpolation Improvements:**
```csharp
public class GameUI
{
    // Raw string literals (C# 11)
    private const string JsonTemplate = """
        {
            "playerId": "{0}",
            "score": {1},
            "achievements": [
                {2}
            ]
        }
        """;
    
    // Interpolated string handlers for performance
    public void UpdateScoreDisplay(int score, string playerName)
    {
        // Compiler optimizes this to avoid string allocations
        var display = $"Player: {playerName} - Score: {score:N0}";
        scoreText.text = display;
    }
    
    // UTF-8 string literals (C# 11)
    public static ReadOnlySpan<byte> GetGameNameUtf8() => "Unity Game"u8;
}
```

**Required Members (C# 11):**
```csharp
public class Enemy
{
    public required string Name { get; init; }
    public required int Health { get; init; }
    public required Vector3 SpawnPosition { get; init; }
    
    public int Damage { get; init; } = 10;
    public float Speed { get; init; } = 5.0f;
    
    // All required members must be set during construction
}

// Usage
var enemy = new Enemy
{
    Name = "Goblin",
    Health = 50,
    SpawnPosition = Vector3.zero
    // Damage and Speed are optional - have default values
};
```

## Practical Applications

### Unity-Specific Modern C# Usage

**Component System with Modern Features:**
```csharp
// Using records for component data
public record struct MovementData(Vector3 Velocity, float Speed, bool IsGrounded);
public record struct HealthData(int Current, int Maximum);

public class ModernPlayerController : MonoBehaviour
{
    [SerializeField] private MovementData movement;
    [SerializeField] private HealthData health;
    
    // Pattern matching in Update
    void Update()
    {
        var input = GetInput();
        
        movement = input switch
        {
            InputData { IsJumping: true } when movement.IsGrounded => 
                movement with { Velocity = movement.Velocity + Vector3.up * 10f },
            InputData { MovementVector: var dir } when dir != Vector2.zero => 
                movement with { Velocity = new Vector3(dir.x, movement.Velocity.y, dir.y) * movement.Speed },
            _ => movement with { Velocity = new Vector3(0, movement.Velocity.y, 0) }
        };
        
        transform.position += movement.Velocity * Time.deltaTime;
    }
    
    // Local function for input processing
    private InputData GetInput()
    {
        bool IsKeyPressed(KeyCode key) => Input.GetKey(key);
        Vector2 GetMovementInput() => new(Input.GetAxis("Horizontal"), Input.GetAxis("Vertical"));
        
        return new InputData(
            MovementVector: GetMovementInput(),
            IsJumping: IsKeyPressed(KeyCode.Space),
            IsRunning: IsKeyPressed(KeyCode.LeftShift)
        );
    }
}

public record InputData(Vector2 MovementVector, bool IsJumping, bool IsRunning);
```

**Event System with Modern Patterns:**
```csharp
public static class GameEvents
{
    // Using tuples for event arguments
    public static event Action<(Player player, int damage, DamageType type)>? PlayerDamaged;
    public static event Action<(string itemName, int quantity)>? ItemCollected;
    public static event Action<(int level, float experience)>? PlayerLevelUp;
    
    // Extension methods for clean event raising
    public static void RaisePlayerDamaged(this Player player, int damage, DamageType type)
    {
        PlayerDamaged?.Invoke((player, damage, type));
    }
    
    public static void RaiseItemCollected(string itemName, int quantity = 1)
    {
        ItemCollected?.Invoke((itemName, quantity));
    }
}

// Usage with pattern matching
public class GameEventHandler : MonoBehaviour
{
    void Start()
    {
        GameEvents.PlayerDamaged += OnPlayerDamaged;
        GameEvents.ItemCollected += OnItemCollected;
    }
    
    private void OnPlayerDamaged((Player player, int damage, DamageType type) eventData)
    {
        var message = eventData switch
        {
            (_, var dmg, DamageType.Fire) when dmg > 50 => "Massive fire damage!",
            (_, var dmg, DamageType.Fire) => $"Fire damage: {dmg}",
            (_, var dmg, _) when dmg > 100 => "Critical damage!",
            (_, var dmg, var type) => $"{type} damage: {dmg}"
        };
        
        ShowDamageText(message);
    }
    
    private void OnItemCollected((string itemName, int quantity) eventData)
    {
        var (name, qty) = eventData; // Deconstruction
        ShowNotification($"Collected {qty}x {name}");
    }
}
```

### Async Patterns with Modern C#

**Improved Async/Await Patterns:**
```csharp
public class AssetLoader
{
    // Using ValueTask for better performance
    public async ValueTask<T> LoadAssetAsync<T>(string path) where T : UnityEngine.Object
    {
        // Check cache first - might return synchronously
        if (assetCache.TryGetValue(path, out var cached))
            return (T)cached;
        
        // Load asynchronously
        var request = Resources.LoadAsync<T>(path);
        
        while (!request.isDone)
        {
            await Task.Yield();
        }
        
        var asset = request.asset as T;
        assetCache[path] = asset;
        return asset;
    }
    
    // Async enumerable (C# 8.0)
    public async IAsyncEnumerable<T> LoadAssetsStreamAsync<T>(IEnumerable<string> paths) 
        where T : UnityEngine.Object
    {
        foreach (var path in paths)
        {
            var asset = await LoadAssetAsync<T>(path);
            if (asset != null)
                yield return asset;
        }
    }
    
    // Usage of async enumerable
    public async Task LoadAllUISprites()
    {
        var spritePaths = new[] { "UI/Button", "UI/Panel", "UI/Icon" };
        
        await foreach (var sprite in LoadAssetsStreamAsync<Sprite>(spritePaths))
        {
            RegisterSprite(sprite);
        }
    }
}
```

## Interview Preparation

### Modern C# Interview Questions

**"How do pattern matching improve code readability and performance?"**
- Reduces nested if-else chains and switch complexity
- Compiler optimizations for switch expressions
- Type safety with pattern matching guards
- Better code maintainability and expressiveness

**"Explain the benefits of records over traditional classes"**
- Immutability by default with with-expressions
- Built-in equality and hashing implementations
- Concise syntax for data-centric types
- Better for functional programming patterns

**"How do nullable reference types help prevent NullReferenceExceptions?"**
- Compile-time null safety warnings and errors
- Clear distinction between nullable and non-nullable references
- Better API design with explicit nullability contracts
- Integration with null-conditional and null-coalescing operators

### Key Takeaways

**Essential Modern C# Features:**
- Pattern matching for cleaner conditional logic
- Records and init-only properties for immutable data
- Nullable reference types for null safety
- Switch expressions for concise branching

**Unity-Specific Applications:**
- Record structs for performance-critical component data
- Pattern matching in Update loops and event handling
- Local functions for helper methods in MonoBehaviours
- Modern async patterns for asset loading and networking

**Professional Development:**
- Stay current with language evolution and best practices
- Migrate legacy code to use modern features where appropriate
- Understand performance implications of new language features
- Share knowledge about modern C# patterns with team members