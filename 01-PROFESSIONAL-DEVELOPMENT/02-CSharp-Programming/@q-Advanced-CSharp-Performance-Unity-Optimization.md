# @q-Advanced C# Performance Unity Optimization

## 🎯 Learning Objectives
- Master advanced C# performance optimization techniques for Unity
- Understand memory management and garbage collection optimization
- Implement high-performance algorithms and data structures
- Profile and optimize critical performance bottlenecks

## ⚡ Memory Management and GC Optimization

### Understanding Unity's Memory Model
```csharp
// Memory allocation patterns to avoid
public class BadMemoryPractices : MonoBehaviour
{
    // ❌ Allocates new array every frame
    void Update()
    {
        var enemies = FindObjectsOfType<Enemy>(); // Allocates array
        string debugText = "Enemies: " + enemies.Length; // Boxing + string allocation
        
        // Allocates new Vector3 every frame
        transform.position = new Vector3(x, y, z);
    }
    
    // ❌ Frequent LINQ usage creates garbage
    public Enemy GetNearestEnemy(Vector3 position)
    {
        return FindObjectsOfType<Enemy>()
            .Where(e => e.IsActive)  // Allocates enumerator
            .OrderBy(e => Vector3.Distance(position, e.transform.position)) // Allocates
            .FirstOrDefault(); // More allocations
    }
}

// Optimized memory management
public class OptimizedMemoryPractices : MonoBehaviour
{
    // ✅ Reuse collections and cache references
    private readonly List<Enemy> _cachedEnemies = new List<Enemy>(32);
    private readonly List<Enemy> _activeEnemies = new List<Enemy>(32);
    private Enemy[] _enemyArray = new Enemy[32];
    
    // ✅ Object pooling for frequently created objects
    private readonly Queue<Projectile> _projectilePool = new Queue<Projectile>();
    private readonly StringBuilder _stringBuilder = new StringBuilder(256);
    
    void Update()
    {
        // ✅ Cache and reuse
        UpdateEnemyCache();
        
        // ✅ Use StringBuilder for string concatenation
        _stringBuilder.Clear();
        _stringBuilder.Append("Enemies: ");
        _stringBuilder.Append(_activeEnemies.Count);
        var debugText = _stringBuilder.ToString();
        
        // ✅ Modify existing Vector3 instead of creating new
        var pos = transform.position;
        pos.x = newX;
        pos.y = newY;
        pos.z = newZ;
        transform.position = pos;
    }
    
    // ✅ Manual iteration instead of LINQ
    public Enemy GetNearestEnemy(Vector3 position)
    {
        Enemy nearest = null;
        float nearestDistanceSqr = float.MaxValue;
        
        for (int i = 0; i < _activeEnemies.Count; i++)
        {
            var enemy = _activeEnemies[i];
            if (!enemy.IsActive) continue;
            
            // Use sqrMagnitude to avoid expensive sqrt calculation
            var distanceSqr = (enemy.transform.position - position).sqrMagnitude;
            if (distanceSqr < nearestDistanceSqr)
            {
                nearestDistanceSqr = distanceSqr;
                nearest = enemy;
            }
        }
        
        return nearest;
    }
    
    // ✅ Object pooling implementation
    public Projectile GetProjectile()
    {
        if (_projectilePool.Count > 0)
        {
            var projectile = _projectilePool.Dequeue();
            projectile.gameObject.SetActive(true);
            return projectile;
        }
        
        return Instantiate(projectilePrefab);
    }
    
    public void ReturnProjectile(Projectile projectile)
    {
        projectile.gameObject.SetActive(false);
        projectile.Reset(); // Clean up state
        _projectilePool.Enqueue(projectile);
    }
}
```

### Advanced Object Pooling System
```csharp
public interface IPoolable
{
    void OnPoolGet();
    void OnPoolReturn();
    bool IsInUse { get; set; }
}

public class ObjectPool<T> where T : Component, IPoolable
{
    private readonly Queue<T> _pool = new Queue<T>();
    private readonly HashSet<T> _active = new HashSet<T>();
    private readonly T _prefab;
    private readonly Transform _parent;
    private readonly int _maxPoolSize;
    
    public ObjectPool(T prefab, int initialSize = 10, int maxPoolSize = 100, Transform parent = null)
    {
        _prefab = prefab;
        _maxPoolSize = maxPoolSize;
        _parent = parent;
        
        // Pre-populate pool
        for (int i = 0; i < initialSize; i++)
        {
            var obj = CreateNewObject();
            obj.gameObject.SetActive(false);
            _pool.Enqueue(obj);
        }
    }
    
    public T Get()
    {
        T obj;
        
        if (_pool.Count > 0)
        {
            obj = _pool.Dequeue();
        }
        else
        {
            obj = CreateNewObject();
        }
        
        obj.gameObject.SetActive(true);
        obj.IsInUse = true;
        obj.OnPoolGet();
        _active.Add(obj);
        
        return obj;
    }
    
    public void Return(T obj)
    {
        if (!_active.Contains(obj)) return;
        
        _active.Remove(obj);
        obj.IsInUse = false;
        obj.OnPoolReturn();
        obj.gameObject.SetActive(false);
        
        // Don't exceed max pool size
        if (_pool.Count < _maxPoolSize)
        {
            _pool.Enqueue(obj);
        }
        else
        {
            Object.Destroy(obj.gameObject);
        }
    }
    
    private T CreateNewObject()
    {
        var obj = Object.Instantiate(_prefab, _parent);
        return obj;
    }
    
    public void Clear()
    {
        // Return all active objects
        var activeArray = new T[_active.Count];
        _active.CopyTo(activeArray);
        
        foreach (var obj in activeArray)
        {
            Return(obj);
        }
        
        // Destroy pooled objects
        while (_pool.Count > 0)
        {
            var obj = _pool.Dequeue();
            Object.Destroy(obj.gameObject);
        }
    }
}

// Generic pool manager
public class PoolManager : MonoBehaviour
{
    private readonly Dictionary<Type, object> _pools = new Dictionary<Type, object>();
    private static PoolManager _instance;
    
    public static PoolManager Instance
    {
        get
        {
            if (_instance == null)
            {
                _instance = FindObjectOfType<PoolManager>();
                if (_instance == null)
                {
                    var go = new GameObject("PoolManager");
                    _instance = go.AddComponent<PoolManager>();
                    DontDestroyOnLoad(go);
                }
            }
            return _instance;
        }
    }
    
    public void RegisterPool<T>(T prefab, int initialSize = 10, int maxSize = 100) 
        where T : Component, IPoolable
    {
        var pool = new ObjectPool<T>(prefab, initialSize, maxSize, transform);
        _pools[typeof(T)] = pool;
    }
    
    public T Get<T>() where T : Component, IPoolable
    {
        if (_pools.TryGetValue(typeof(T), out var poolObj))
        {
            var pool = (ObjectPool<T>)poolObj;
            return pool.Get();
        }
        
        throw new InvalidOperationException($"Pool for type {typeof(T).Name} not registered");
    }
    
    public void Return<T>(T obj) where T : Component, IPoolable
    {
        if (_pools.TryGetValue(typeof(T), out var poolObj))
        {
            var pool = (ObjectPool<T>)poolObj;
            pool.Return(obj);
        }
    }
}
```

### Struct-Based Value Types for Performance
```csharp
// ✅ Use structs for small, immutable data
[System.Serializable]
public readonly struct GameStats
{
    public readonly int Health;
    public readonly int Mana;
    public readonly float Speed;
    public readonly float Damage;
    
    public GameStats(int health, int mana, float speed, float damage)
    {
        Health = health;
        Mana = mana;
        Speed = speed;
        Damage = damage;
    }
    
    // Efficient operations without allocation
    public GameStats WithHealth(int newHealth) =>
        new GameStats(newHealth, Mana, Speed, Damage);
        
    public GameStats WithDamage(float newDamage) =>
        new GameStats(Health, Mana, Speed, newDamage);
        
    public static GameStats operator +(GameStats a, GameStats b) =>
        new GameStats(
            a.Health + b.Health,
            a.Mana + b.Mana,
            a.Speed + b.Speed,
            a.Damage + b.Damage);
}

// ✅ Efficient vector-like operations
[System.Serializable]
public readonly struct Vector2Int : IEquatable<Vector2Int>
{
    public readonly int X;
    public readonly int Y;
    
    public Vector2Int(int x, int y)
    {
        X = x;
        Y = y;
    }
    
    public static readonly Vector2Int Zero = new Vector2Int(0, 0);
    public static readonly Vector2Int One = new Vector2Int(1, 1);
    public static readonly Vector2Int Up = new Vector2Int(0, 1);
    public static readonly Vector2Int Down = new Vector2Int(0, -1);
    public static readonly Vector2Int Left = new Vector2Int(-1, 0);
    public static readonly Vector2Int Right = new Vector2Int(1, 0);
    
    public int SqrMagnitude => X * X + Y * Y;
    public float Magnitude => Mathf.Sqrt(SqrMagnitude);
    
    public static Vector2Int operator +(Vector2Int a, Vector2Int b) =>
        new Vector2Int(a.X + b.X, a.Y + b.Y);
        
    public static Vector2Int operator -(Vector2Int a, Vector2Int b) =>
        new Vector2Int(a.X - b.X, a.Y - b.Y);
        
    public static Vector2Int operator *(Vector2Int a, int scalar) =>
        new Vector2Int(a.X * scalar, a.Y * scalar);
        
    public bool Equals(Vector2Int other) =>
        X == other.X && Y == other.Y;
        
    public override bool Equals(object obj) =>
        obj is Vector2Int other && Equals(other);
        
    public override int GetHashCode() =>
        HashCode.Combine(X, Y);
        
    public static bool operator ==(Vector2Int left, Vector2Int right) =>
        left.Equals(right);
        
    public static bool operator !=(Vector2Int left, Vector2Int right) =>
        !left.Equals(right);
}
```

## 🔧 High-Performance Algorithms and Data Structures

### Spatial Partitioning for Collision Detection
```csharp
public class SpatialGrid<T> where T : class
{
    private readonly Dictionary<Vector2Int, List<T>> _grid;
    private readonly Dictionary<T, Vector2Int> _objectPositions;
    private readonly float _cellSize;
    private readonly int _maxObjectsPerCell;
    
    public SpatialGrid(float cellSize, int maxObjectsPerCell = 32)
    {
        _cellSize = cellSize;
        _maxObjectsPerCell = maxObjectsPerCell;
        _grid = new Dictionary<Vector2Int, List<T>>();
        _objectPositions = new Dictionary<T, Vector2Int>();
    }
    
    public void Add(T obj, Vector3 position)
    {
        var cellCoord = WorldToGrid(position);
        
        if (!_grid.TryGetValue(cellCoord, out var cell))
        {
            cell = new List<T>(_maxObjectsPerCell);
            _grid[cellCoord] = cell;
        }
        
        cell.Add(obj);
        _objectPositions[obj] = cellCoord;
    }
    
    public void Remove(T obj)
    {
        if (_objectPositions.TryGetValue(obj, out var cellCoord))
        {
            if (_grid.TryGetValue(cellCoord, out var cell))
            {
                cell.Remove(obj);
                if (cell.Count == 0)
                {
                    _grid.Remove(cellCoord);
                }
            }
            _objectPositions.Remove(obj);
        }
    }
    
    public void UpdatePosition(T obj, Vector3 newPosition)
    {
        var newCellCoord = WorldToGrid(newPosition);
        
        if (_objectPositions.TryGetValue(obj, out var oldCellCoord))
        {
            if (oldCellCoord != newCellCoord)
            {
                // Move to new cell
                Remove(obj);
                Add(obj, newPosition);
            }
        }
        else
        {
            Add(obj, newPosition);
        }
    }
    
    public List<T> Query(Vector3 center, float radius)
    {
        var results = new List<T>();
        var radiusSqr = radius * radius;
        
        // Calculate grid bounds for the query
        var minCell = WorldToGrid(center - Vector3.one * radius);
        var maxCell = WorldToGrid(center + Vector3.one * radius);
        
        for (int x = minCell.X; x <= maxCell.X; x++)
        {
            for (int y = minCell.Y; y <= maxCell.Y; y++)
            {
                var cellCoord = new Vector2Int(x, y);
                if (_grid.TryGetValue(cellCoord, out var cell))
                {
                    foreach (var obj in cell)
                    {
                        // Perform actual distance check
                        var objPosition = GetObjectPosition(obj);
                        var distanceSqr = (objPosition - center).sqrMagnitude;
                        
                        if (distanceSqr <= radiusSqr)
                        {
                            results.Add(obj);
                        }
                    }
                }
            }
        }
        
        return results;
    }
    
    private Vector2Int WorldToGrid(Vector3 worldPos)
    {
        return new Vector2Int(
            Mathf.FloorToInt(worldPos.x / _cellSize),
            Mathf.FloorToInt(worldPos.z / _cellSize)
        );
    }
    
    private Vector3 GetObjectPosition(T obj)
    {
        // This would need to be implemented based on your object type
        // Could use interfaces or delegates for position retrieval
        throw new NotImplementedException("Implement position retrieval for your object type");
    }
}
```

### High-Performance Event System
```csharp
// Zero-allocation event system using delegates
public static class FastEventSystem
{
    private static readonly Dictionary<Type, Delegate> _eventHandlers = new();
    private static readonly Queue<Action> _deferredEvents = new();
    
    public static void Subscribe<T>(Action<T> handler) where T : struct
    {
        var eventType = typeof(T);
        
        if (_eventHandlers.TryGetValue(eventType, out var existingHandler))
        {
            _eventHandlers[eventType] = Delegate.Combine(existingHandler, handler);
        }
        else
        {
            _eventHandlers[eventType] = handler;
        }
    }
    
    public static void Unsubscribe<T>(Action<T> handler) where T : struct
    {
        var eventType = typeof(T);
        
        if (_eventHandlers.TryGetValue(eventType, out var existingHandler))
        {
            var newHandler = Delegate.Remove(existingHandler, handler);
            if (newHandler == null)
            {
                _eventHandlers.Remove(eventType);
            }
            else
            {
                _eventHandlers[eventType] = newHandler;
            }
        }
    }
    
    public static void Publish<T>(T eventData) where T : struct
    {
        var eventType = typeof(T);
        
        if (_eventHandlers.TryGetValue(eventType, out var handler))
        {
            ((Action<T>)handler)(eventData);
        }
    }
    
    public static void PublishDeferred<T>(T eventData) where T : struct
    {
        _deferredEvents.Enqueue(() => Publish(eventData));
    }
    
    public static void ProcessDeferredEvents()
    {
        while (_deferredEvents.Count > 0)
        {
            var eventAction = _deferredEvents.Dequeue();
            eventAction();
        }
    }
}

// Example usage with struct events (no allocations)
public struct PlayerHealthChangedEvent
{
    public int PlayerId;
    public float OldHealth;
    public float NewHealth;
    public float Damage;
}

public class HealthSystem : MonoBehaviour
{
    private void Start()
    {
        FastEventSystem.Subscribe<PlayerHealthChangedEvent>(OnPlayerHealthChanged);
    }
    
    public void DamagePlayer(int playerId, float damage)
    {
        var player = GetPlayer(playerId);
        var oldHealth = player.Health;
        player.Health = Mathf.Max(0, player.Health - damage);
        
        // Zero allocation event
        FastEventSystem.Publish(new PlayerHealthChangedEvent
        {
            PlayerId = playerId,
            OldHealth = oldHealth,
            NewHealth = player.Health,
            Damage = damage
        });
    }
    
    private void OnPlayerHealthChanged(PlayerHealthChangedEvent eventData)
    {
        // Handle health change
        if (eventData.NewHealth <= 0)
        {
            // Player died
            HandlePlayerDeath(eventData.PlayerId);
        }
    }
}
```

### Efficient Collection Operations
```csharp
public static class CollectionExtensions
{
    // ✅ Fast removal from lists without preserving order
    public static bool RemoveAtSwapBack<T>(this List<T> list, int index)
    {
        if (index < 0 || index >= list.Count)
            return false;
            
        // Move last element to the removed position
        list[index] = list[list.Count - 1];
        list.RemoveAt(list.Count - 1);
        return true;
    }
    
    public static bool RemoveSwapBack<T>(this List<T> list, T item)
    {
        var index = list.IndexOf(item);
        if (index >= 0)
        {
            return list.RemoveAtSwapBack(index);
        }
        return false;
    }
    
    // ✅ Binary search for sorted lists
    public static int BinarySearch<T>(this List<T> list, T item, IComparer<T> comparer = null)
    {
        comparer ??= Comparer<T>.Default;
        
        int left = 0;
        int right = list.Count - 1;
        
        while (left <= right)
        {
            int mid = left + (right - left) / 2;
            int comparison = comparer.Compare(list[mid], item);
            
            if (comparison == 0)
                return mid;
            else if (comparison < 0)
                left = mid + 1;
            else
                right = mid - 1;
        }
        
        return ~left; // Return bitwise complement for insertion point
    }
    
    // ✅ Efficient batch operations
    public static void AddRange<T>(this List<T> list, ReadOnlySpan<T> span)
    {
        var requiredCapacity = list.Count + span.Length;
        if (list.Capacity < requiredCapacity)
        {
            list.Capacity = Math.Max(requiredCapacity, list.Capacity * 2);
        }
        
        foreach (var item in span)
        {
            list.Add(item);
        }
    }
    
    // ✅ Memory-efficient filtering
    public static void FilterInPlace<T>(this List<T> list, Predicate<T> predicate)
    {
        int writeIndex = 0;
        
        for (int readIndex = 0; readIndex < list.Count; readIndex++)
        {
            if (predicate(list[readIndex]))
            {
                if (writeIndex != readIndex)
                {
                    list[writeIndex] = list[readIndex];
                }
                writeIndex++;
            }
        }
        
        // Remove extra elements
        var removeCount = list.Count - writeIndex;
        if (removeCount > 0)
        {
            list.RemoveRange(writeIndex, removeCount);
        }
    }
}
```

## 📊 Performance Profiling and Optimization

### Custom Profiling Framework
```csharp
public static class PerformanceProfiler
{
    private static readonly Dictionary<string, ProfileData> _profiles = new();
    private static readonly Dictionary<string, float> _startTimes = new();
    
    public static void BeginSample(string sampleName)
    {
        _startTimes[sampleName] = Time.realtimeSinceStartup;
    }
    
    public static void EndSample(string sampleName)
    {
        if (_startTimes.TryGetValue(sampleName, out var startTime))
        {
            var duration = Time.realtimeSinceStartup - startTime;
            
            if (!_profiles.TryGetValue(sampleName, out var profile))
            {
                profile = new ProfileData(sampleName);
                _profiles[sampleName] = profile;
            }
            
            profile.AddSample(duration);
            _startTimes.Remove(sampleName);
        }
    }
    
    public static ProfileData GetProfile(string sampleName)
    {
        return _profiles.TryGetValue(sampleName, out var profile) ? profile : null;
    }
    
    public static void ClearProfiles()
    {
        _profiles.Clear();
        _startTimes.Clear();
    }
    
    // Usage with disposable pattern
    public static ProfileScope Sample(string sampleName)
    {
        return new ProfileScope(sampleName);
    }
}

public readonly struct ProfileScope : IDisposable
{
    private readonly string _sampleName;
    
    public ProfileScope(string sampleName)
    {
        _sampleName = sampleName;
        PerformanceProfiler.BeginSample(sampleName);
    }
    
    public void Dispose()
    {
        PerformanceProfiler.EndSample(_sampleName);
    }
}

public class ProfileData
{
    public string Name { get; }
    public int SampleCount { get; private set; }
    public float TotalTime { get; private set; }
    public float AverageTime => SampleCount > 0 ? TotalTime / SampleCount : 0f;
    public float MinTime { get; private set; } = float.MaxValue;
    public float MaxTime { get; private set; }
    public float LastTime { get; private set; }
    
    public ProfileData(string name)
    {
        Name = name;
    }
    
    public void AddSample(float time)
    {
        SampleCount++;
        TotalTime += time;
        LastTime = time;
        MinTime = Mathf.Min(MinTime, time);
        MaxTime = Mathf.Max(MaxTime, time);
    }
    
    public void Reset()
    {
        SampleCount = 0;
        TotalTime = 0f;
        MinTime = float.MaxValue;
        MaxTime = 0f;
        LastTime = 0f;
    }
}

// Example usage
public class GameSystem : MonoBehaviour
{
    void Update()
    {
        using (PerformanceProfiler.Sample("GameSystem.Update"))
        {
            UpdateEnemies();
            UpdateProjectiles();
            UpdateUI();
        }
    }
    
    void UpdateEnemies()
    {
        using (PerformanceProfiler.Sample("UpdateEnemies"))
        {
            // Enemy update logic
        }
    }
}
```

## 🚀 AI/LLM Integration for Performance Optimization

### Automated Performance Analysis
```yaml
AI_Performance_Assistance:
  code_analysis:
    - Memory allocation hotspot identification
    - GC pressure analysis and recommendations
    - Algorithm complexity evaluation
    - Data structure optimization suggestions
    - Caching opportunity identification
    
  optimization_suggestions:
    - Object pooling implementation guidance
    - SIMD optimization opportunities
    - Async/await pattern improvements
    - Collection operation optimizations
    - Memory layout improvements for cache efficiency
```

### Performance Optimization Prompts
```yaml
Optimization_Prompts:
  memory_analysis:
    - "Analyze this Unity C# code for memory allocation issues"
    - "Suggest object pooling strategies for this system"
    - "Identify garbage collection pressure points in this code"
    - "Recommend struct vs class usage for this data"
    - "Optimize this collection usage to reduce allocations"
    
  algorithm_optimization:
    - "Improve the performance of this algorithm"
    - "Suggest more efficient data structures for this use case"
    - "Optimize this loop for better cache performance"
    - "Implement SIMD optimizations for this computation"
    - "Reduce the complexity of this search algorithm"
```

## 💡 Key Highlights

- **Memory Awareness**: Understand and minimize garbage collection pressure
- **Data Structure Choice**: Select appropriate collections for performance
- **Algorithm Optimization**: Focus on algorithmic complexity and cache efficiency
- **Profiling Integration**: Use both Unity Profiler and custom profiling tools
- **Struct Usage**: Leverage value types for performance-critical code
- **Object Pooling**: Implement pooling for frequently created/destroyed objects

## 🔗 Next Steps

1. **Profile Existing Code**: Use Unity Profiler to identify performance bottlenecks
2. **Implement Object Pooling**: Create pooling systems for dynamic objects
3. **Optimize Memory Usage**: Reduce allocations in critical paths
4. **Practice Algorithm Optimization**: Improve computational complexity
5. **Build Performance Framework**: Create reusable optimization patterns

*Advanced C# performance optimization in Unity requires understanding both language-level optimizations and Unity-specific constraints. Success comes from measuring performance impacts and applying targeted optimizations where they matter most.*