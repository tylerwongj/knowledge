# @n-Memory-Profiling-GC-Optimization

## 🎯 Learning Objectives

- Master C# memory management and garbage collection optimization
- Implement zero-allocation patterns for performance-critical Unity code
- Use profiling tools to identify and eliminate memory leaks
- Create memory-efficient data structures and algorithms

## 🔧 Garbage Collection Fundamentals

### Understanding GC Behavior in Unity

```csharp
using System;
using System.Collections.Generic;
using UnityEngine;
using Unity.Profiling;

public class GCOptimizationDemo : MonoBehaviour
{
    // ProfilerMarkers for measuring allocations
    private static readonly ProfilerMarker s_UpdateMarker = new ProfilerMarker("GCDemo.Update");
    private static readonly ProfilerMarker s_StringOperationsMarker = new ProfilerMarker("StringOperations");
    private static readonly ProfilerMarker s_CollectionOperationsMarker = new ProfilerMarker("CollectionOperations");
    
    [Header("Performance Settings")]
    [SerializeField] private bool enableOptimizations = true;
    [SerializeField] private int iterations = 1000;
    
    // Cached components to avoid GetComponent allocations
    private Transform cachedTransform;
    private Rigidbody cachedRigidbody;
    
    // Pre-allocated collections
    private List<GameObject> gameObjectPool = new List<GameObject>(100);
    private StringBuilder stringBuilder = new System.Text.StringBuilder(256);
    
    // Value types to avoid boxing
    private struct OptimizedData
    {
        public Vector3 position;
        public Quaternion rotation;
        public float health;
        public int level;
        
        public OptimizedData(Vector3 pos, Quaternion rot, float hp, int lvl)
        {
            position = pos;
            rotation = rot;
            health = hp;
            level = lvl;
        }
    }
    
    private void Awake()
    {
        // Cache components once to avoid repeated GetComponent calls
        cachedTransform = transform;
        cachedRigidbody = GetComponent<Rigidbody>();
        
        // Pre-populate collections to avoid dynamic resizing
        InitializeCollections();
    }
    
    private void InitializeCollections()
    {
        gameObjectPool.Capacity = 100;
        for (int i = 0; i < 50; i++)
        {
            gameObjectPool.Add(null); // Reserve space
        }
    }
    
    private void Update()
    {
        using (s_UpdateMarker.Auto())
        {
            if (enableOptimizations)
            {
                OptimizedOperations();
            }
            else
            {
                UnoptimizedOperations();
            }
        }
    }
    
    #region Optimized vs Unoptimized Patterns
    
    private void OptimizedOperations()
    {
        // Zero-allocation string operations
        using (s_StringOperationsMarker.Auto())
        {
            OptimizedStringOperations();
        }
        
        // Efficient collection operations
        using (s_CollectionOperationsMarker.Auto())
        {
            OptimizedCollectionOperations();
        }
        
        // Value type operations
        OptimizedValueTypeOperations();
    }
    
    private void UnoptimizedOperations()
    {
        // Allocation-heavy string operations
        using (s_StringOperationsMarker.Auto())
        {
            UnoptimizedStringOperations();
        }
        
        // Inefficient collection operations
        using (s_CollectionOperationsMarker.Auto())
        {
            UnoptimizedCollectionOperations();
        }
        
        // Boxing operations
        UnoptimizedBoxingOperations();
    }
    
    private void OptimizedStringOperations()
    {
        // Use StringBuilder for multiple concatenations
        stringBuilder.Clear();
        stringBuilder.Append("Player Level: ");
        stringBuilder.Append(GetPlayerLevel());
        stringBuilder.Append(", Health: ");
        stringBuilder.Append(GetPlayerHealth());
        
        string result = stringBuilder.ToString();
        
        // Use string.Format with cached format string
        const string FORMAT = "Position: {0:F2}, {1:F2}, {2:F2}";
        string positionText = string.Format(FORMAT, 
            cachedTransform.position.x, 
            cachedTransform.position.y, 
            cachedTransform.position.z);
    }
    
    private void UnoptimizedStringOperations()
    {
        // Multiple string concatenations create many temporary strings
        string result = "Player Level: " + GetPlayerLevel() + ", Health: " + GetPlayerHealth();
        
        // String interpolation in loops
        for (int i = 0; i < 10; i++)
        {
            string temp = $"Item {i}: {GetItemName(i)}";
            // Each iteration allocates new strings
        }
    }
    
    private void OptimizedCollectionOperations()
    {
        // Reuse existing list capacity
        var tempList = gameObjectPool;
        tempList.Clear(); // Doesn't deallocate underlying array
        
        // Use for loops instead of foreach to avoid enumerator allocation
        for (int i = 0; i < iterations && i < tempList.Capacity; i++)
        {
            // Reuse existing slots
            if (i < tempList.Count)
            {
                tempList[i] = FindNearbyGameObject();
            }
            else
            {
                tempList.Add(FindNearbyGameObject());
            }
        }
        
        // Use array-based operations when possible
        ProcessGameObjectsArray(tempList.ToArray());
    }
    
    private void UnoptimizedCollectionOperations()
    {
        // Creates new list every frame
        var tempList = new List<GameObject>();
        
        // Dynamic resizing causes allocations
        for (int i = 0; i < iterations; i++)
        {
            tempList.Add(FindNearbyGameObject());
        }
        
        // LINQ operations allocate enumerators and delegates
        var filtered = tempList.Where(go => go != null).ToList();
        var names = filtered.Select(go => go.name).ToArray();
    }
    
    private void OptimizedValueTypeOperations()
    {
        // Use structs to avoid heap allocations
        var data = new OptimizedData(
            cachedTransform.position,
            cachedTransform.rotation,
            GetPlayerHealth(),
            GetPlayerLevel()
        );
        
        // Pass by reference to avoid copies
        ProcessOptimizedData(ref data);
        
        // Use stackalloc for small temporary arrays
        Span<int> tempArray = stackalloc int[10];
        for (int i = 0; i < tempArray.Length; i++)
        {
            tempArray[i] = i * i;
        }
        
        ProcessTempData(tempArray);
    }
    
    private void UnoptimizedBoxingOperations()
    {
        // Boxing value types to objects
        object boxedInt = GetPlayerLevel(); // Boxes int to object
        object boxedFloat = GetPlayerHealth(); // Boxes float to object
        
        // Using non-generic collections
        System.Collections.ArrayList list = new System.Collections.ArrayList();
        list.Add(1); // Boxing
        list.Add(2.5f); // Boxing
        list.Add(true); // Boxing
        
        // Unboxing operations
        int level = (int)boxedInt; // Unboxing
        float health = (float)boxedFloat; // Unboxing
    }
    #endregion
    
    #region Helper Methods
    
    private int GetPlayerLevel() => UnityEngine.Random.Range(1, 100);
    private float GetPlayerHealth() => UnityEngine.Random.Range(0f, 100f);
    private string GetItemName(int index) => $"Item_{index}";
    
    private GameObject FindNearbyGameObject()
    {
        // Placeholder for finding nearby objects
        return gameObject;
    }
    
    private void ProcessGameObjectsArray(GameObject[] objects)
    {
        // Process array without allocations
    }
    
    private void ProcessOptimizedData(ref OptimizedData data)
    {
        // Process data by reference to avoid copying
        data.health = Mathf.Clamp(data.health, 0f, 100f);
    }
    
    private void ProcessTempData(Span<int> data)
    {
        // Process span without allocations
        for (int i = 0; i < data.Length; i++)
        {
            data[i] *= 2;
        }
    }
    #endregion
}
```

### Memory Pool Pattern Implementation

```csharp
using System;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Generic object pool that minimizes GC allocations
/// </summary>
public class MemoryPool<T> where T : class, new()
{
    private readonly Stack<T> pool;
    private readonly Func<T> createFunc;
    private readonly Action<T> resetAction;
    private readonly int maxCapacity;
    
    public int CountAll { get; private set; }
    public int CountActive => CountAll - CountInactive;
    public int CountInactive => pool.Count;
    
    public MemoryPool(int initialCapacity = 10, int maxCapacity = 1000, 
                      Func<T> createFunc = null, Action<T> resetAction = null)
    {
        this.maxCapacity = maxCapacity;
        this.createFunc = createFunc ?? (() => new T());
        this.resetAction = resetAction;
        this.pool = new Stack<T>(initialCapacity);
        
        // Pre-populate pool
        for (int i = 0; i < initialCapacity; i++)
        {
            pool.Push(this.createFunc());
            CountAll++;
        }
    }
    
    public T Get()
    {
        T item;
        
        if (pool.Count == 0)
        {
            item = createFunc();
            CountAll++;
        }
        else
        {
            item = pool.Pop();
        }
        
        return item;
    }
    
    public void Return(T item)
    {
        if (item == null) return;
        
        if (pool.Count < maxCapacity)
        {
            resetAction?.Invoke(item);
            pool.Push(item);
        }
        else
        {
            // Pool is full, let GC handle it
            CountAll--;
        }
    }
    
    public void Clear()
    {
        pool.Clear();
        CountAll = 0;
    }
    
    public void PreWarm(int count)
    {
        for (int i = pool.Count; i < count && CountAll < maxCapacity; i++)
        {
            pool.Push(createFunc());
            CountAll++;
        }
    }
}

// Specialized pools for common Unity objects
public static class UnityObjectPools
{
    private static MemoryPool<List<Vector3>> vectorListPool;
    private static MemoryPool<List<Transform>> transformListPool;
    private static MemoryPool<Dictionary<string, object>> dictionaryPool;
    private static MemoryPool<System.Text.StringBuilder> stringBuilderPool;
    
    static UnityObjectPools()
    {
        // Vector3 list pool
        vectorListPool = new MemoryPool<List<Vector3>>(
            initialCapacity: 5,
            maxCapacity: 50,
            createFunc: () => new List<Vector3>(32),
            resetAction: list => list.Clear()
        );
        
        // Transform list pool
        transformListPool = new MemoryPool<List<Transform>>(
            initialCapacity: 5,
            maxCapacity: 50,
            createFunc: () => new List<Transform>(16),
            resetAction: list => list.Clear()
        );
        
        // Dictionary pool
        dictionaryPool = new MemoryPool<Dictionary<string, object>>(
            initialCapacity: 3,
            maxCapacity: 20,
            createFunc: () => new Dictionary<string, object>(16),
            resetAction: dict => dict.Clear()
        );
        
        // StringBuilder pool
        stringBuilderPool = new MemoryPool<System.Text.StringBuilder>(
            initialCapacity: 3,
            maxCapacity: 10,
            createFunc: () => new System.Text.StringBuilder(256),
            resetAction: sb => sb.Clear()
        );
    }
    
    public static List<Vector3> GetVectorList() => vectorListPool.Get();
    public static void ReturnVectorList(List<Vector3> list) => vectorListPool.Return(list);
    
    public static List<Transform> GetTransformList() => transformListPool.Get();
    public static void ReturnTransformList(List<Transform> list) => transformListPool.Return(list);
    
    public static Dictionary<string, object> GetDictionary() => dictionaryPool.Get();
    public static void ReturnDictionary(Dictionary<string, object> dict) => dictionaryPool.Return(dict);
    
    public static System.Text.StringBuilder GetStringBuilder() => stringBuilderPool.Get();
    public static void ReturnStringBuilder(System.Text.StringBuilder sb) => stringBuilderPool.Return(sb);
}

// Usage example
public class PooledOperationsExample : MonoBehaviour
{
    void Start()
    {
        PerformPooledOperations();
    }
    
    private void PerformPooledOperations()
    {
        // Get pooled objects
        var vectorList = UnityObjectPools.GetVectorList();
        var transformList = UnityObjectPools.GetTransformList();
        var dictionary = UnityObjectPools.GetDictionary();
        var stringBuilder = UnityObjectPools.GetStringBuilder();
        
        try
        {
            // Use the objects
            vectorList.Add(Vector3.zero);
            vectorList.Add(Vector3.one);
            
            transformList.Add(transform);
            
            dictionary["position"] = transform.position;
            dictionary["rotation"] = transform.rotation;
            
            stringBuilder.Append("Result: ");
            stringBuilder.Append(vectorList.Count);
            stringBuilder.Append(" vectors processed");
            
            string result = stringBuilder.ToString();
            Debug.Log(result);
        }
        finally
        {
            // Always return to pool
            UnityObjectPools.ReturnVectorList(vectorList);
            UnityObjectPools.ReturnTransformList(transformList);
            UnityObjectPools.ReturnDictionary(dictionary);
            UnityObjectPools.ReturnStringBuilder(stringBuilder);
        }
    }
}
```

## 🎮 Unity-Specific Memory Optimization

### Component and GameObject Pooling

```csharp
using System.Collections.Generic;
using UnityEngine;

public interface IPoolable
{
    void OnSpawnFromPool();
    void OnReturnToPool();
    bool IsActiveInPool { get; }
}

[System.Serializable]
public class ComponentPool<T> where T : Component, IPoolable
{
    [SerializeField] private T prefab;
    [SerializeField] private int initialSize = 10;
    [SerializeField] private int maxSize = 100;
    [SerializeField] private bool allowGrowth = true;
    
    private Queue<T> availableComponents = new Queue<T>();
    private HashSet<T> allComponents = new HashSet<T>();
    private Transform poolParent;
    
    public int TotalCount => allComponents.Count;
    public int AvailableCount => availableComponents.Count;
    public int ActiveCount => TotalCount - AvailableCount;
    
    public void Initialize(Transform parent = null)
    {
        poolParent = parent;
        
        if (poolParent == null)
        {
            var poolObject = new GameObject($"{typeof(T).Name}_Pool");
            poolParent = poolObject.transform;
            Object.DontDestroyOnLoad(poolObject);
        }
        
        // Pre-instantiate initial pool
        for (int i = 0; i < initialSize; i++)
        {
            CreateNewComponent();
        }
    }
    
    private T CreateNewComponent()
    {
        if (prefab == null)
        {
            Debug.LogError($"Prefab is null for pool of type {typeof(T).Name}");
            return null;
        }
        
        T component = Object.Instantiate(prefab, poolParent);
        component.gameObject.SetActive(false);
        
        allComponents.Add(component);
        availableComponents.Enqueue(component);
        
        return component;
    }
    
    public T Get()
    {
        T component = null;
        
        // Try to get from available components
        while (availableComponents.Count > 0)
        {
            component = availableComponents.Dequeue();
            if (component != null && allComponents.Contains(component))
            {
                break;
            }
            component = null;
        }
        
        // Create new if needed
        if (component == null)
        {
            if (allowGrowth && allComponents.Count < maxSize)
            {
                component = CreateNewComponent();
                if (availableComponents.Count > 0)
                {
                    availableComponents.Dequeue(); // Remove the one we just added
                }
            }
            else
            {
                Debug.LogWarning($"Pool for {typeof(T).Name} is exhausted!");
                return null;
            }
        }
        
        // Activate and initialize
        if (component != null)
        {
            component.gameObject.SetActive(true);
            component.OnSpawnFromPool();
        }
        
        return component;
    }
    
    public void Return(T component)
    {
        if (component == null || !allComponents.Contains(component)) return;
        
        component.OnReturnToPool();
        component.gameObject.SetActive(false);
        component.transform.SetParent(poolParent);
        
        availableComponents.Enqueue(component);
    }
    
    public void ReturnAll()
    {
        foreach (T component in allComponents)
        {
            if (component != null && component.IsActiveInPool)
            {
                Return(component);
            }
        }
    }
    
    public void Clear()
    {
        foreach (T component in allComponents)
        {
            if (component != null)
            {
                Object.Destroy(component.gameObject);
            }
        }
        
        allComponents.Clear();
        availableComponents.Clear();
    }
}

// Example poolable bullet component
public class PoolableBullet : MonoBehaviour, IPoolable
{
    [SerializeField] private float speed = 10f;
    [SerializeField] private float lifetime = 5f;
    [SerializeField] private LayerMask collisionMask;
    
    private Rigidbody rb;
    private Collider col;
    private TrailRenderer trail;
    private float spawnTime;
    private Vector3 direction;
    
    public bool IsActiveInPool => gameObject.activeInHierarchy;
    
    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
        col = GetComponent<Collider>();
        trail = GetComponent<TrailRenderer>();
    }
    
    public void OnSpawnFromPool()
    {
        spawnTime = Time.time;
        col.enabled = true;
        
        if (trail != null)
        {
            trail.Clear();
            trail.enabled = true;
        }
    }
    
    public void OnReturnToPool()
    {
        rb.velocity = Vector3.zero;
        rb.angularVelocity = Vector3.zero;
        col.enabled = false;
        
        if (trail != null)
        {
            trail.enabled = false;
        }
        
        // Reset any bullet-specific state
        direction = Vector3.zero;
    }
    
    public void Initialize(Vector3 startPosition, Vector3 shootDirection)
    {
        transform.position = startPosition;
        direction = shootDirection.normalized;
        rb.velocity = direction * speed;
        transform.forward = direction;
    }
    
    private void Update()
    {
        // Check lifetime
        if (Time.time - spawnTime >= lifetime)
        {
            ReturnToPool();
        }
    }
    
    private void OnTriggerEnter(Collider other)
    {
        if (((1 << other.gameObject.layer) & collisionMask) != 0)
        {
            // Handle collision
            ProcessHit(other);
            ReturnToPool();
        }
    }
    
    private void ProcessHit(Collider target)
    {
        // Handle damage, effects, etc.
        var health = target.GetComponent<Health>();
        if (health != null)
        {
            health.TakeDamage(10f);
        }
    }
    
    private void ReturnToPool()
    {
        BulletPoolManager.Instance.ReturnBullet(this);
    }
}

// Pool manager for bullets
public class BulletPoolManager : MonoBehaviour
{
    public static BulletPoolManager Instance { get; private set; }
    
    [SerializeField] private PoolableBullet bulletPrefab;
    [SerializeField] private int initialPoolSize = 50;
    [SerializeField] private int maxPoolSize = 200;
    
    private ComponentPool<PoolableBullet> bulletPool;
    
    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializePool();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    private void InitializePool()
    {
        bulletPool = new ComponentPool<PoolableBullet>
        {
            prefab = bulletPrefab,
            initialSize = initialPoolSize,
            maxSize = maxPoolSize,
            allowGrowth = true
        };
        
        bulletPool.Initialize(transform);
    }
    
    public PoolableBullet SpawnBullet(Vector3 position, Vector3 direction)
    {
        var bullet = bulletPool.Get();
        if (bullet != null)
        {
            bullet.Initialize(position, direction);
        }
        return bullet;
    }
    
    public void ReturnBullet(PoolableBullet bullet)
    {
        bulletPool.Return(bullet);
    }
    
    private void OnDestroy()
    {
        bulletPool?.Clear();
    }
    
    #region Debug Info
    private void OnGUI()
    {
        if (bulletPool != null)
        {
            GUILayout.Label($"Bullet Pool - Total: {bulletPool.TotalCount}, Active: {bulletPool.ActiveCount}, Available: {bulletPool.AvailableCount}");
        }
    }
    #endregion
}
```

## 🚀 AI/LLM Integration Opportunities

### Automated Memory Analysis

```
Analyze Unity C# code for memory optimization opportunities:
1. Identify allocation hotspots and suggest zero-allocation alternatives
2. Recommend object pooling candidates and implementation strategies
3. Detect boxing/unboxing patterns and provide value type solutions
4. Suggest string operation optimizations and StringBuilder usage

Context: Unity mobile game targeting 60fps with strict memory constraints
Requirements: Specific code examples, performance impact analysis, implementation priority
```

### GC Optimization Pattern Generation

```
Generate C# memory optimization patterns for Unity:
1. Custom allocator implementations for specific use cases
2. Memory-efficient data structures for large datasets
3. Stackalloc and Span<T> usage patterns for performance-critical code
4. Profile-guided optimization strategies for production games

Focus: Unity 2022.3 LTS compatibility, mobile performance, zero-allocation patterns
Environment: High-performance game development, real-time constraints
```

## 💡 Advanced Memory Profiling Techniques

### Custom Memory Profiler

```csharp
using System;
using System.Collections.Generic;
using UnityEngine;
using Unity.Profiling;

public class CustomMemoryProfiler : MonoBehaviour
{
    [System.Serializable]
    public class MemorySnapshot
    {
        public float timestamp;
        public long totalAllocatedMemory;
        public long totalReservedMemory;
        public long totalUnusedReservedMemory;
        public long gcMemory;
        public int gcCollectionCount;
        public Dictionary<string, long> categoryMemory;
        
        public MemorySnapshot()
        {
            categoryMemory = new Dictionary<string, long>();
        }
    }
    
    [SerializeField] private bool enableProfiling = true;
    [SerializeField] private float snapshotInterval = 1f;
    [SerializeField] private int maxSnapshots = 300; // 5 minutes at 1 second intervals
    
    private List<MemorySnapshot> snapshots = new List<MemorySnapshot>();
    private ProfilerRecorder totalReservedMemoryRecorder;
    private ProfilerRecorder totalUsedMemoryRecorder;
    private ProfilerRecorder gcReservedMemoryRecorder;
    private ProfilerRecorder gcUsedMemoryRecorder;
    
    // Custom allocation tracking
    private Dictionary<string, long> customAllocations = new Dictionary<string, long>();
    private static CustomMemoryProfiler instance;
    
    public static CustomMemoryProfiler Instance => instance;
    
    private void Awake()
    {
        if (instance == null)
        {
            instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeProfilers();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    private void InitializeProfilers()
    {
        totalReservedMemoryRecorder = ProfilerRecorder.StartNew("System Memory", "Reserved");
        totalUsedMemoryRecorder = ProfilerRecorder.StartNew("System Memory", "Used");
        gcReservedMemoryRecorder = ProfilerRecorder.StartNew("GC Memory", "Reserved");
        gcUsedMemoryRecorder = ProfilerRecorder.StartNew("GC Memory", "Used");
        
        InvokeRepeating(nameof(TakeMemorySnapshot), 0f, snapshotInterval);
    }
    
    private void TakeMemorySnapshot()
    {
        if (!enableProfiling) return;
        
        var snapshot = new MemorySnapshot
        {
            timestamp = Time.time,
            totalReservedMemory = totalReservedMemoryRecorder.Valid ? totalReservedMemoryRecorder.LastValue : 0,
            totalAllocatedMemory = totalUsedMemoryRecorder.Valid ? totalUsedMemoryRecorder.LastValue : 0,
            gcMemory = gcUsedMemoryRecorder.Valid ? gcUsedMemoryRecorder.LastValue : 0,
            gcCollectionCount = GC.CollectionCount(0) + GC.CollectionCount(1) + GC.CollectionCount(2)
        };
        
        // Copy custom allocations
        foreach (var kvp in customAllocations)
        {
            snapshot.categoryMemory[kvp.Key] = kvp.Value;
        }
        
        snapshots.Add(snapshot);
        
        // Trim old snapshots
        if (snapshots.Count > maxSnapshots)
        {
            snapshots.RemoveAt(0);
        }
        
        // Check for memory spikes
        CheckForMemorySpikes(snapshot);
    }
    
    private void CheckForMemorySpikes(MemorySnapshot current)
    {
        if (snapshots.Count < 2) return;
        
        var previous = snapshots[snapshots.Count - 2];
        long memoryDelta = current.totalAllocatedMemory - previous.totalAllocatedMemory;
        
        // Threshold for memory spike detection (e.g., 10MB)
        const long SPIKE_THRESHOLD = 10 * 1024 * 1024;
        
        if (memoryDelta > SPIKE_THRESHOLD)
        {
            Debug.LogWarning($"Memory spike detected: +{memoryDelta / (1024 * 1024)}MB in {current.timestamp - previous.timestamp:F2}s");
            LogMemoryState();
        }
    }
    
    public void TrackCustomAllocation(string category, long bytes)
    {
        if (customAllocations.ContainsKey(category))
        {
            customAllocations[category] += bytes;
        }
        else
        {
            customAllocations[category] = bytes;
        }
    }
    
    public void LogMemoryState()
    {
        if (snapshots.Count == 0) return;
        
        var latest = snapshots[snapshots.Count - 1];
        
        Debug.Log($"Memory Profile at {latest.timestamp:F2}s:");
        Debug.Log($"  Total Reserved: {latest.totalReservedMemory / (1024 * 1024)}MB");
        Debug.Log($"  Total Used: {latest.totalAllocatedMemory / (1024 * 1024)}MB");
        Debug.Log($"  GC Memory: {latest.gcMemory / (1024 * 1024)}MB");
        Debug.Log($"  GC Collections: {latest.gcCollectionCount}");
        
        foreach (var kvp in latest.categoryMemory)
        {
            Debug.Log($"  {kvp.Key}: {kvp.Value / (1024 * 1024)}MB");
        }
    }
    
    public MemorySnapshot[] GetRecentSnapshots(int count = 10)
    {
        int startIndex = Mathf.Max(0, snapshots.Count - count);
        int actualCount = snapshots.Count - startIndex;
        
        MemorySnapshot[] result = new MemorySnapshot[actualCount];
        for (int i = 0; i < actualCount; i++)
        {
            result[i] = snapshots[startIndex + i];
        }
        
        return result;
    }
    
    public void ExportSnapshotsToCSV(string filename = null)
    {
        if (filename == null)
        {
            filename = $"memory_profile_{DateTime.Now:yyyyMMdd_HHmmss}.csv";
        }
        
        string path = Application.persistentDataPath + "/" + filename;
        
        using (var writer = new System.IO.StreamWriter(path))
        {
            // Write header
            writer.WriteLine("Timestamp,TotalReserved,TotalUsed,GCMemory,GCCollections");
            
            // Write data
            foreach (var snapshot in snapshots)
            {
                writer.WriteLine($"{snapshot.timestamp:F2},{snapshot.totalReservedMemory},{snapshot.totalAllocatedMemory},{snapshot.gcMemory},{snapshot.gcCollectionCount}");
            }
        }
        
        Debug.Log($"Memory profile exported to: {path}");
    }
    
    private void OnDestroy()
    {
        totalReservedMemoryRecorder.Dispose();
        totalUsedMemoryRecorder.Dispose();
        gcReservedMemoryRecorder.Dispose();
        gcUsedMemoryRecorder.Dispose();
    }
    
    #region Unity Editor GUI
    #if UNITY_EDITOR
    private void OnGUI()
    {
        if (!enableProfiling) return;
        
        GUILayout.BeginArea(new Rect(10, 10, 300, 200));
        GUILayout.Label("Memory Profiler", EditorStyles.boldLabel);
        
        if (snapshots.Count > 0)
        {
            var latest = snapshots[snapshots.Count - 1];
            GUILayout.Label($"Reserved: {latest.totalReservedMemory / (1024 * 1024)}MB");
            GUILayout.Label($"Used: {latest.totalAllocatedMemory / (1024 * 1024)}MB");
            GUILayout.Label($"GC: {latest.gcMemory / (1024 * 1024)}MB");
            GUILayout.Label($"GC Collections: {latest.gcCollectionCount}");
        }
        
        if (GUILayout.Button("Log Memory State"))
        {
            LogMemoryState();
        }
        
        if (GUILayout.Button("Export CSV"))
        {
            ExportSnapshotsToCSV();
        }
        
        GUILayout.EndArea();
    }
    #endif
    #endregion
}

// Usage tracking wrapper
public static class TrackedOperations
{
    public static T[] TrackedArrayResize<T>(T[] array, int newSize, string category = "ArrayResize")
    {
        long oldSize = array != null ? array.Length * System.Runtime.InteropServices.Marshal.SizeOf<T>() : 0;
        
        T[] newArray = new T[newSize];
        if (array != null)
        {
            System.Array.Copy(array, newArray, Mathf.Min(array.Length, newSize));
        }
        
        long newSizeBytes = newSize * System.Runtime.InteropServices.Marshal.SizeOf<T>();
        long delta = newSizeBytes - oldSize;
        
        CustomMemoryProfiler.Instance?.TrackCustomAllocation(category, delta);
        
        return newArray;
    }
    
    public static List<T> TrackedListCreation<T>(int capacity, string category = "ListCreation")
    {
        long sizeBytes = capacity * System.Runtime.InteropServices.Marshal.SizeOf<T>();
        CustomMemoryProfiler.Instance?.TrackCustomAllocation(category, sizeBytes);
        
        return new List<T>(capacity);
    }
    
    public static Dictionary<TKey, TValue> TrackedDictionaryCreation<TKey, TValue>(int capacity, string category = "DictionaryCreation")
    {
        // Estimate dictionary overhead
        long keySize = System.Runtime.InteropServices.Marshal.SizeOf<TKey>();
        long valueSize = System.Runtime.InteropServices.Marshal.SizeOf<TValue>();
        long estimatedSize = capacity * (keySize + valueSize + 32); // 32 bytes overhead per entry
        
        CustomMemoryProfiler.Instance?.TrackCustomAllocation(category, estimatedSize);
        
        return new Dictionary<TKey, TValue>(capacity);
    }
}
```

This comprehensive guide provides practical tools and techniques for memory optimization in Unity C# development, with focus on production-ready patterns and profiling strategies.