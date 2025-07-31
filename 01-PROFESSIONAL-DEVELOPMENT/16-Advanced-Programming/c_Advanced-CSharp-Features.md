# @c-Advanced-CSharp-Features - Modern C# Features & Advanced Language Constructs

## 🎯 Learning Objectives
- Master modern C# features for Unity development
- Implement advanced language constructs and patterns
- Leverage async/await, LINQ, and generics effectively
- Use AI tools to optimize C# code with latest language features

## 🔧 Modern C# Features in Unity

### C# 8.0+ Features

#### Nullable Reference Types
```csharp
#nullable enable

using UnityEngine;

public class PlayerController : MonoBehaviour
{
    [SerializeField] private Transform? targetTransform;
    [SerializeField] private AudioClip? jumpSound;
    
    private Rigidbody playerRigidbody = null!; // Non-null field
    
    private void Awake()
    {
        playerRigidbody = GetComponent<Rigidbody>();
        
        // Null-conditional operator
        targetTransform?.SetParent(transform);
    }
    
    public void PlayJumpSound()
    {
        // Null-coalescing assignment
        jumpSound ??= Resources.Load<AudioClip>("DefaultJump");
        
        if (jumpSound is not null)
        {
            AudioSource.PlayClipAtPoint(jumpSound, transform.position);
        }
    }
    
    // Null-coalescing operator with method
    public Vector3 GetTargetPosition() => targetTransform?.position ?? Vector3.zero;
}
```

#### Pattern Matching and Switch Expressions
```csharp
public class WeaponSystem : MonoBehaviour
{
    public enum WeaponType { Pistol, Rifle, Shotgun, Sniper }
    
    // Switch expressions (C# 8.0)
    public float GetDamage(WeaponType weapon) => weapon switch
    {
        WeaponType.Pistol => 25f,
        WeaponType.Rifle => 35f,
        WeaponType.Shotgun => 60f,
        WeaponType.Sniper => 100f,
        _ => 0f
    };
    
    public string GetWeaponDescription(WeaponType weapon) => weapon switch
    {
        WeaponType.Pistol => "Fast, low damage",
        WeaponType.Rifle => "Balanced weapon",
        WeaponType.Shotgun => "Close range, high damage",
        WeaponType.Sniper => "Long range, very high damage",
        _ => "Unknown weapon"
    };
    
    // Property patterns
    public bool IsHighDamageWeapon(WeaponType weapon) => weapon switch
    {
        WeaponType.Shotgun or WeaponType.Sniper => true,
        _ => false
    };
    
    // Tuple patterns
    public float GetDamageMultiplier(WeaponType weapon, bool isHeadshot) => (weapon, isHeadshot) switch
    {
        (WeaponType.Sniper, true) => 3.0f,
        (WeaponType.Rifle, true) => 2.0f,
        (WeaponType.Pistol, true) => 1.5f,
        (WeaponType.Shotgun, true) => 1.2f,
        (_, false) => 1.0f,
        _ => 1.0f
    };
}
```

#### Records and Value Types
```csharp
// Record types for immutable game data
public record PlayerStats(int Health, int Mana, float Speed, float Damage)
{
    public PlayerStats WithHealth(int newHealth) => this with { Health = newHealth };
    public PlayerStats WithMana(int newMana) => this with { Mana = newMana };
}

public record struct Vector2Int(int X, int Y)
{
    public static Vector2Int Zero => new(0, 0);
    public static Vector2Int One => new(1, 1);
    
    public Vector2Int(Vector2 vector) : this((int)vector.x, (int)vector.y) { }
    
    public float Magnitude => Mathf.Sqrt(X * X + Y * Y);
    
    public static Vector2Int operator +(Vector2Int a, Vector2Int b) => new(a.X + b.X, a.Y + b.Y);
    public static Vector2Int operator -(Vector2Int a, Vector2Int b) => new(a.X - b.X, a.Y - b.Y);
}

// Using records in game systems
public class GameState : MonoBehaviour
{
    private PlayerStats currentStats = new(100, 50, 5.0f, 25.0f);
    
    public void TakeDamage(int damage)
    {
        int newHealth = Mathf.Max(0, currentStats.Health - damage);
        currentStats = currentStats.WithHealth(newHealth);
        
        if (currentStats.Health <= 0)
            HandlePlayerDeath();
    }
    
    private void HandlePlayerDeath() { /* Death logic */ }
}
```

### Advanced Generics and Constraints

#### Generic Interfaces and Constraints
```csharp
public interface IGameEntity
{
    int Id { get; }
    Vector3 Position { get; set; }
    bool IsActive { get; set; }
}

public interface IDamageable
{
    int Health { get; }
    void TakeDamage(int damage);
}

// Generic manager with multiple constraints
public class EntityManager<T> : MonoBehaviour where T : MonoBehaviour, IGameEntity
{
    private Dictionary<int, T> entities = new();
    private ObjectPool<T> entityPool;
    
    public void RegisterEntity(T entity)
    {
        entities[entity.Id] = entity;
    }
    
    public T? GetEntity(int id)
    {
        entities.TryGetValue(id, out T? entity);
        return entity;
    }
    
    public void UpdateActiveEntities()
    {
        foreach (var entity in entities.Values)
        {
            if (entity.IsActive)
            {
                // Update entity
            }
        }
    }
}

// Specialized damage system with generic constraints
public class DamageSystem<T> : MonoBehaviour where T : MonoBehaviour, IGameEntity, IDamageable
{
    public void DealDamageInRadius(Vector3 center, float radius, int damage)
    {
        var entities = FindObjectsOfType<T>();
        
        foreach (var entity in entities)
        {
            if (Vector3.Distance(center, entity.Position) <= radius)
            {
                entity.TakeDamage(damage);
            }
        }
    }
}
```

#### Generic Method Overloading and Variance
```csharp
public class EventSystem : MonoBehaviour
{
    private Dictionary<Type, List<object>> eventHandlers = new();
    
    // Generic event subscription
    public void Subscribe<T>(System.Action<T> handler) where T : class
    {
        var eventType = typeof(T);
        
        if (!eventHandlers.ContainsKey(eventType))
            eventHandlers[eventType] = new List<object>();
            
        eventHandlers[eventType].Add(handler);
    }
    
    // Generic event publishing
    public void Publish<T>(T eventData) where T : class
    {
        var eventType = typeof(T);
        
        if (eventHandlers.TryGetValue(eventType, out var handlers))
        {
            foreach (System.Action<T> handler in handlers.Cast<System.Action<T>>())
            {
                handler?.Invoke(eventData);
            }
        }
    }
    
    // Contravariance example
    public void Subscribe<T>(System.Action<object> genericHandler) where T : class
    {
        Subscribe<T>(obj => genericHandler(obj));
    }
}

// Usage example
public class GameEvents
{
    public class PlayerDied { public int PlayerId; public Vector3 Position; }
    public class EnemySpawned { public int EnemyId; public EnemyType Type; }
}

public class GameEventHandler : MonoBehaviour
{
    private EventSystem eventSystem;
    
    private void Start()
    {
        eventSystem = FindObjectOfType<EventSystem>();
        
        // Subscribe to specific events
        eventSystem.Subscribe<GameEvents.PlayerDied>(OnPlayerDied);
        eventSystem.Subscribe<GameEvents.EnemySpawned>(OnEnemySpawned);
    }
    
    private void OnPlayerDied(GameEvents.PlayerDied eventData)
    {
        Debug.Log($"Player {eventData.PlayerId} died at {eventData.Position}");
    }
    
    private void OnEnemySpawned(GameEvents.EnemySpawned eventData)
    {
        Debug.Log($"Enemy {eventData.EnemyId} of type {eventData.Type} spawned");
    }
}
```

### Async/Await Patterns in Unity

#### Async Loading Systems
```csharp
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.AddressableAssets;

public class AssetLoader : MonoBehaviour
{
    // Async asset loading with progress reporting
    public async Task<T> LoadAssetAsync<T>(string key, System.IProgress<float>? progress = null) where T : Object
    {
        var handle = Addressables.LoadAssetAsync<T>(key);
        
        while (!handle.IsDone)
        {
            progress?.Report(handle.PercentComplete);
            await Task.Yield(); // Yield control back to Unity
        }
        
        if (handle.Status == UnityEngine.ResourceManagement.AsyncOperations.AsyncOperationStatus.Succeeded)
        {
            return handle.Result;
        }
        
        throw new System.Exception($"Failed to load asset: {key}");
    }
    
    // Async scene loading
    public async Task LoadSceneAsync(string sceneName, System.IProgress<float>? progress = null)
    {
        var operation = UnityEngine.SceneManagement.SceneManager.LoadSceneAsync(sceneName);
        
        while (!operation.isDone)
        {
            progress?.Report(operation.progress);
            await Task.Yield();
        }
    }
    
    // Batch asset loading
    public async Task<Dictionary<string, T>> LoadMultipleAssetsAsync<T>(
        string[] keys, 
        System.IProgress<float>? progress = null) where T : Object
    {
        var results = new Dictionary<string, T>();
        var tasks = new List<Task<T>>();
        
        foreach (var key in keys)
        {
            tasks.Add(LoadAssetAsync<T>(key));
        }
        
        for (int i = 0; i < tasks.Count; i++)
        {
            results[keys[i]] = await tasks[i];
            progress?.Report((float)(i + 1) / tasks.Count);
        }
        
        return results;
    }
}
```

#### Async Animation and Tweening
```csharp
public static class AsyncAnimations
{
    public static async Task MoveToAsync(this Transform transform, Vector3 target, float duration)
    {
        Vector3 start = transform.position;
        float elapsedTime = 0f;
        
        while (elapsedTime < duration)
        {
            elapsedTime += Time.deltaTime;
            float t = elapsedTime / duration;
            
            transform.position = Vector3.Lerp(start, target, t);
            await Task.Yield();
        }
        
        transform.position = target;
    }
    
    public static async Task ScaleToAsync(this Transform transform, Vector3 targetScale, float duration)
    {
        Vector3 startScale = transform.localScale;
        float elapsedTime = 0f;
        
        while (elapsedTime < duration)
        {
            elapsedTime += Time.deltaTime;
            float t = Mathf.SmoothStep(0f, 1f, elapsedTime / duration);
            
            transform.localScale = Vector3.Lerp(startScale, targetScale, t);
            await Task.Yield();
        }
        
        transform.localScale = targetScale;
    }
    
    public static async Task FadeAsync(this CanvasGroup canvasGroup, float targetAlpha, float duration)
    {
        float startAlpha = canvasGroup.alpha;
        float elapsedTime = 0f;
        
        while (elapsedTime < duration)
        {
            elapsedTime += Time.deltaTime;
            float t = elapsedTime / duration;
            
            canvasGroup.alpha = Mathf.Lerp(startAlpha, targetAlpha, t);
            await Task.Yield();
        }
        
        canvasGroup.alpha = targetAlpha;
    }
}

// Usage example
public class UIController : MonoBehaviour
{
    [SerializeField] private Transform panel;
    [SerializeField] private CanvasGroup canvasGroup;
    
    public async Task ShowPanelAsync()
    {
        // Animate multiple properties concurrently
        var moveTask = panel.MoveToAsync(Vector3.zero, 0.5f);
        var scaleTask = panel.ScaleToAsync(Vector3.one, 0.3f);
        var fadeTask = canvasGroup.FadeAsync(1f, 0.4f);
        
        await Task.WhenAll(moveTask, scaleTask, fadeTask);
    }
    
    public async Task HidePanelAsync()
    {
        // Sequential animations
        await canvasGroup.FadeAsync(0f, 0.2f);
        await panel.ScaleToAsync(Vector3.zero, 0.3f);
    }
}
```

### LINQ and Functional Programming

#### Advanced LINQ Queries
```csharp
using System.Linq;
using UnityEngine;

public class GameAnalytics : MonoBehaviour
{
    [System.Serializable]
    public class Player
    {
        public int Id;
        public string Name;
        public int Level;
        public float Score;
        public Vector3 Position;
        public bool IsActive;
    }
    
    [SerializeField] private List<Player> players = new();
    
    // Complex LINQ queries for game analysis
    public void AnalyzePlayerData()
    {
        // Top players by score
        var topPlayers = players
            .Where(p => p.IsActive)
            .OrderByDescending(p => p.Score)
            .Take(5)
            .Select(p => new { p.Name, p.Score, p.Level })
            .ToArray();
        
        // Average score by level
        var averageScoreByLevel = players
            .Where(p => p.IsActive)
            .GroupBy(p => p.Level)
            .Select(g => new { 
                Level = g.Key, 
                AverageScore = g.Average(p => p.Score),
                PlayerCount = g.Count()
            })
            .OrderBy(x => x.Level)
            .ToArray();
        
        // Players in specific area
        Vector3 center = Vector3.zero;
        float radius = 10f;
        
        var playersInArea = players
            .Where(p => p.IsActive)
            .Where(p => Vector3.Distance(p.Position, center) <= radius)
            .OrderBy(p => Vector3.Distance(p.Position, center))
            .ToList();
        
        // Performance aggregations
        var stats = players
            .Where(p => p.IsActive)
            .Aggregate(
                new { TotalScore = 0f, MaxLevel = 0, MinLevel = int.MaxValue, Count = 0 },
                (acc, p) => new { 
                    TotalScore = acc.TotalScore + p.Score,
                    MaxLevel = Mathf.Max(acc.MaxLevel, p.Level),
                    MinLevel = Mathf.Min(acc.MinLevel, p.Level),
                    Count = acc.Count + 1
                }
            );
    }
    
    // Functional programming patterns
    public System.Func<Player, bool> CreateLevelFilter(int minLevel, int maxLevel) =>
        player => player.Level >= minLevel && player.Level <= maxLevel;
    
    public System.Func<Player, float> CreateDistanceCalculator(Vector3 referencePoint) =>
        player => Vector3.Distance(player.Position, referencePoint);
    
    public void ProcessPlayersWithFilters()
    {
        var levelFilter = CreateLevelFilter(5, 15);
        var distanceCalculator = CreateDistanceCalculator(Vector3.zero);
        
        var filteredPlayers = players
            .Where(levelFilter)
            .Select(p => new { 
                Player = p, 
                Distance = distanceCalculator(p) 
            })
            .Where(x => x.Distance <= 20f)
            .OrderBy(x => x.Distance)
            .ToList();
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Modern C# Feature Adoption
```
PROMPT: "Refactor this Unity C# code to use modern C# features:
[paste code]

Apply these improvements where beneficial:
- Nullable reference types for better null safety
- Pattern matching and switch expressions
- Records for immutable data structures
- Async/await for loading operations
- LINQ for data processing
- Latest C# syntax improvements

Maintain Unity compatibility and performance considerations."
```

### Performance-Optimized Generic Systems
```
PROMPT: "Design a generic system for Unity that handles [specific requirement]:
Requirements:
- Type-safe operations
- High performance (minimal allocations)
- Extensible design
- Unity-specific optimizations

Include:
- Generic constraints where appropriate
- Memory-efficient implementations
- Async operations if beneficial
- LINQ integration where suitable
- Error handling and validation"
```

### Async Pattern Implementation
```
PROMPT: "Convert this synchronous Unity system to use async/await patterns:
[describe current system]

Consider:
- Loading operations that can be async
- Animation sequences
- Network operations
- File I/O operations
- Progress reporting requirements
- Cancellation token support
- Error handling strategies

Provide complete implementation with proper async patterns."
```

## 💡 Key Highlights

### Modern C# Features for Unity
- **Nullable Reference Types**: Improve null safety and reduce NullReferenceExceptions
- **Pattern Matching**: Cleaner conditional logic and type checking
- **Records**: Immutable data structures for game state and configurations
- **Switch Expressions**: More concise and readable conditional logic
- **Async/Await**: Non-blocking operations for loading and animations

### Advanced Generic Programming
- **Generic Constraints**: Type-safe operations with interface and class constraints
- **Variance**: Covariance and contravariance for flexible type relationships
- **Generic Methods**: Reusable algorithms that work with multiple types
- **Performance**: Avoid boxing and reduce memory allocations

### Async Programming Best Practices
- **Unity Main Thread**: Always return to main thread for Unity operations
- **Task.Yield()**: Use instead of Task.Delay(0) for Unity compatibility
- **Progress Reporting**: Implement IProgress<T> for loading feedback
- **Cancellation**: Support CancellationToken for interruptible operations
- **Exception Handling**: Proper async exception handling patterns

### LINQ Performance Considerations
- **Lazy Evaluation**: Understanding deferred execution
- **Memory Allocations**: Use ToArray() or ToList() judiciously
- **Performance**: Profile LINQ queries in performance-critical paths
- **Alternatives**: Consider foreach loops for simple operations
- **Composition**: Chain operations efficiently

### AI-Enhanced C# Development
- **Code Modernization**: Regular AI-assisted updates to latest C# features
- **Pattern Recognition**: Identify opportunities for advanced language features
- **Performance Analysis**: AI evaluation of generic and async code performance
- **Best Practice Enforcement**: Automated code review for modern C# patterns
- **Learning Acceleration**: AI-generated examples and explanations of complex features

This comprehensive understanding of modern C# features will enable you to write more efficient, maintainable, and type-safe Unity code while leveraging AI tools to accelerate adoption of advanced language constructs and ensure best practices are consistently applied.