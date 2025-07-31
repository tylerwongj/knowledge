# C# Performance Optimization for Unity & Enterprise Development

## Overview
Advanced performance optimization techniques in C# with specific focus on Unity game development, memory management, and high-performance computing scenarios.

## Key Concepts

### Memory Management and Garbage Collection

**Understanding GC Pressure:**
```csharp
// Bad - creates unnecessary garbage
public class BadInventory
{
    private List<Item> items = new List<Item>();
    
    public List<Item> GetItemsByType(ItemType type)
    {
        var result = new List<Item>(); // New allocation every call
        foreach (var item in items)
        {
            if (item.Type == type)
                result.Add(item);
        }
        return result;
    }
    
    public string GetItemList()
    {
        string result = "";
        foreach (var item in items)
        {
            result += item.Name + ", "; // String concatenation creates garbage
        }
        return result;
    }
}

// Good - minimizes allocations
public class OptimizedInventory
{
    private List<Item> items = new List<Item>();
    private List<Item> cachedResults = new List<Item>(); // Reused buffer
    private StringBuilder stringBuilder = new StringBuilder(); // Reused builder
    
    public IReadOnlyList<Item> GetItemsByType(ItemType type)
    {
        cachedResults.Clear(); // Reuse existing list
        foreach (var item in items)
        {
            if (item.Type == type)
                cachedResults.Add(item);
        }
        return cachedResults;
    }
    
    public string GetItemList()
    {
        stringBuilder.Clear();
        foreach (var item in items)
        {
            stringBuilder.Append(item.Name);
            stringBuilder.Append(", ");
        }
        return stringBuilder.ToString();
    }
}
```

**Object Pooling Patterns:**
```csharp
public class GenericObjectPool<T> where T : class, new()
{
    private readonly ConcurrentQueue<T> objects = new ConcurrentQueue<T>();
    private readonly Func<T> objectFactory;
    private readonly Action<T> resetAction;
    private readonly int maxSize;
    
    public GenericObjectPool(Func<T> factory = null, Action<T> reset = null, int maxSize = 100)
    {
        objectFactory = factory ?? (() => new T());
        resetAction = reset ?? (obj => { });
        this.maxSize = maxSize;
    }
    
    public T Get()
    {
        if (objects.TryDequeue(out T item))
        {
            return item;
        }
        return objectFactory();
    }
    
    public void Return(T item)
    {
        if (objects.Count < maxSize)
        {
            resetAction(item);
            objects.Enqueue(item);
        }
    }
}

// Usage example for Unity
public class BulletPool
{
    private readonly GenericObjectPool<Bullet> pool;
    
    public BulletPool()
    {
        pool = new GenericObjectPool<Bullet>(
            factory: () => Object.Instantiate(bulletPrefab).GetComponent<Bullet>(),
            reset: bullet => bullet.Reset(),
            maxSize: 200
        );
    }
    
    public Bullet GetBullet()
    {
        var bullet = pool.Get();
        bullet.gameObject.SetActive(true);
        return bullet;
    }
    
    public void ReturnBullet(Bullet bullet)
    {
        bullet.gameObject.SetActive(false);
        pool.Return(bullet);
    }
}
```

### Data Structure Optimization

**Cache-Friendly Data Layouts:**
```csharp
// Bad - poor cache locality
public class BadEnemySystem
{
    private List<Enemy> enemies = new List<Enemy>();
    
    public void UpdateEnemies()
    {
        foreach (var enemy in enemies)
        {
            enemy.UpdateAI();        // Random memory access
            enemy.UpdatePhysics();   // Random memory access
            enemy.UpdateAnimation(); // Random memory access
        }
    }
}

// Good - Structure of Arrays (SoA) pattern
public class OptimizedEnemySystem
{
    private Vector3[] positions;
    private Vector3[] velocities;
    private float[] healths;
    private AIState[] aiStates;
    private int enemyCount;
    
    public void UpdateEnemies()
    {
        // Update positions (sequential memory access)
        for (int i = 0; i < enemyCount; i++)
        {
            positions[i] += velocities[i] * Time.deltaTime;
        }
        
        // Update AI (sequential memory access)
        for (int i = 0; i < enemyCount; i++)
        {
            aiStates[i] = UpdateAIState(aiStates[i], positions[i]);
        }
        
        // Update health (sequential memory access)
        for (int i = 0; i < enemyCount; i++)
        {
            if (healths[i] <= 0)
                RemoveEnemy(i);
        }
    }
}
```

**High-Performance Collections:**
```csharp
// Unsafe collections for maximum performance
public unsafe struct UnsafeDynamicArray<T> where T : unmanaged
{
    private T* data;
    private int capacity;
    private int count;
    
    public int Count => count;
    public int Capacity => capacity;
    
    public UnsafeDynamicArray(int initialCapacity)
    {
        capacity = initialCapacity;
        count = 0;
        data = (T*)Marshal.AllocHGlobal(sizeof(T) * capacity);
    }
    
    public void Add(T item)
    {
        if (count >= capacity)
            Resize(capacity * 2);
        
        data[count++] = item;
    }
    
    public ref T this[int index]
    {
        get
        {
            #if UNITY_EDITOR
            if (index >= count) throw new IndexOutOfRangeException();
            #endif
            return ref data[index];
        }
    }
    
    private void Resize(int newCapacity)
    {
        T* newData = (T*)Marshal.AllocHGlobal(sizeof(T) * newCapacity);
        Buffer.MemoryCopy(data, newData, sizeof(T) * capacity, sizeof(T) * count);
        
        Marshal.FreeHGlobal((IntPtr)data);
        data = newData;
        capacity = newCapacity;
    }
    
    public void Dispose()
    {
        if (data != null)
        {
            Marshal.FreeHGlobal((IntPtr)data);
            data = null;
        }
    }
}
```

### SIMD and Vectorization

**Unity Mathematics Integration:**
```csharp
using Unity.Mathematics;
using static Unity.Mathematics.math;

public class SIMDOptimizedCalculations
{
    // Process 4 positions simultaneously using SIMD
    public static void UpdatePositions(float4[] positions, float4[] velocities, float deltaTime)
    {
        for (int i = 0; i < positions.Length; i++)
        {
            positions[i] += velocities[i] * deltaTime;
        }
    }
    
    // Matrix transformations using SIMD
    public static void TransformPoints(float3[] points, float4x4 matrix)
    {
        for (int i = 0; i < points.Length; i++)
        {
            points[i] = transform(matrix, points[i]);
        }
    }
    
    // Distance calculations with SIMD
    public static void CalculateDistances(float3[] positions, float3 targetPos, float[] distances)
    {
        for (int i = 0; i < positions.Length; i++)
        {
            distances[i] = distance(positions[i], targetPos);
        }
    }
    
    // Batch collision detection
    public static bool[] CheckSphereCollisions(float3[] centers, float[] radii, float3 testPoint)
    {
        bool[] results = new bool[centers.Length];
        
        for (int i = 0; i < centers.Length; i++)
        {
            float dist = distance(centers[i], testPoint);
            results[i] = dist <= radii[i];
        }
        
        return results;
    }
}
```

**Custom SIMD Operations:**
```csharp
using System.Numerics;

public static class CustomSIMD
{
    // Process arrays of floats using Vector<T>
    public static void MultiplyArrays(float[] a, float[] b, float[] result)
    {
        int vectorSize = Vector<float>.Count;
        int i = 0;
        
        // Process vectors
        for (; i <= a.Length - vectorSize; i += vectorSize)
        {
            var va = new Vector<float>(a, i);
            var vb = new Vector<float>(b, i);
            var vr = va * vb;
            vr.CopyTo(result, i);
        }
        
        // Process remaining elements
        for (; i < a.Length; i++)
        {
            result[i] = a[i] * b[i];
        }
    }
    
    // Fast dot product using SIMD
    public static float DotProduct(float[] a, float[] b)
    {
        if (a.Length != b.Length)
            throw new ArgumentException("Arrays must have same length");
        
        int vectorSize = Vector<float>.Count;
        Vector<float> sum = Vector<float>.Zero;
        int i = 0;
        
        // Process vectors
        for (; i <= a.Length - vectorSize; i += vectorSize)
        {
            var va = new Vector<float>(a, i);
            var vb = new Vector<float>(b, i);
            sum += va * vb;
        }
        
        float result = Vector.Dot(sum, Vector<float>.One);
        
        // Add remaining elements
        for (; i < a.Length; i++)
        {
            result += a[i] * b[i];
        }
        
        return result;
    }
}
```

## Practical Applications

### Unity-Specific Optimizations

**Optimized Update Loops:**
```csharp
public class PerformanceManager : MonoBehaviour
{
    private readonly List<IUpdatable> updatables = new List<IUpdatable>();
    private readonly List<IFixedUpdatable> fixedUpdatables = new List<IFixedUpdatable>();
    private readonly List<ILateUpdatable> lateUpdatables = new List<ILateUpdatable>();
    
    // Cached arrays to avoid allocations
    private IUpdatable[] updateArray;
    private IFixedUpdatable[] fixedUpdateArray;
    private ILateUpdatable[] lateUpdateArray;
    
    private bool needsArrayUpdate = true;
    
    void Update()
    {
        if (needsArrayUpdate)
            UpdateArrays();
        
        // Process updates in batches to improve cache locality
        for (int i = 0; i < updateArray.Length; i++)
        {
            updateArray[i].OnUpdate();
        }
    }
    
    void FixedUpdate()
    {
        for (int i = 0; i < fixedUpdateArray.Length; i++)
        {
            fixedUpdateArray[i].OnFixedUpdate();
        }
    }
    
    void LateUpdate()
    {
        for (int i = 0; i < lateUpdateArray.Length; i++)
        {
            lateUpdateArray[i].OnLateUpdate();
        }
    }
    
    public void RegisterUpdatable(IUpdatable updatable)
    {
        updatables.Add(updatable);
        needsArrayUpdate = true;
    }
    
    private void UpdateArrays()
    {
        updateArray = updatables.ToArray();
        fixedUpdateArray = fixedUpdatables.ToArray();
        lateUpdateArray = lateUpdatables.ToArray();
        needsArrayUpdate = false;
    }
}

public interface IUpdatable { void OnUpdate(); }
public interface IFixedUpdatable { void OnFixedUpdate(); }
public interface ILateUpdatable { void OnLateUpdate(); }
```

**String Optimization for UI:**
```csharp
public class OptimizedUITextManager
{
    private readonly Dictionary<string, string> stringCache = new Dictionary<string, string>();
    private readonly StringBuilder stringBuilder = new StringBuilder();
    
    // String interning for frequently used strings
    public string GetCachedString(string format, params object[] args)
    {
        stringBuilder.Clear();
        stringBuilder.AppendFormat(format, args);
        string key = stringBuilder.ToString();
        
        if (!stringCache.TryGetValue(key, out string cached))
        {
            cached = string.Intern(key);
            stringCache[key] = cached;
        }
        
        return cached;
    }
    
    // Optimized number to string conversion
    private readonly string[] numberStrings = new string[1000];
    
    public string NumberToString(int number)
    {
        if (number >= 0 && number < numberStrings.Length)
        {
            return numberStrings[number] ??= number.ToString();
        }
        
        return number.ToString();
    }
    
    // Fast string formatting for common patterns
    public string FormatScore(int score)
    {
        return GetCachedString("Score: {0}", score);
    }
    
    public string FormatHealth(int current, int max)
    {
        return GetCachedString("HP: {0}/{1}", current, max);
    }
}
```

### Async/Await Performance

**High-Performance Async Patterns:**
```csharp
public class AsyncOptimizations
{
    // Use ValueTask for potentially synchronous operations
    public ValueTask<int> GetCachedValueAsync(string key)
    {
        if (cache.TryGetValue(key, out int value))
        {
            return new ValueTask<int>(value); // No allocation
        }
        
        return LoadValueAsync(key); // Returns Task<int>, auto-converted
    }
    
    // Pool async operations to reduce allocations
    private readonly ObjectPool<AsyncOperation> operationPool = 
        new ObjectPool<AsyncOperation>(() => new AsyncOperation());
    
    public async ValueTask<T> PerformOperationAsync<T>(Func<AsyncOperation, ValueTask<T>> operation)
    {
        var asyncOp = operationPool.Get();
        try
        {
            return await operation(asyncOp);
        }
        finally
        {
            operationPool.Return(asyncOp);
        }
    }
    
    // Batch async operations for better throughput
    public async Task<T[]> ProcessBatchAsync<T>(IEnumerable<Func<Task<T>>> operations, int maxConcurrency = 10)
    {
        using var semaphore = new SemaphoreSlim(maxConcurrency);
        var tasks = operations.Select(async operation =>
        {
            await semaphore.WaitAsync();
            try
            {
                return await operation();
            }
            finally
            {
                semaphore.Release();
            }
        });
        
        return await Task.WhenAll(tasks);
    }
}
```

**ConfigureAwait Optimization:**
```csharp
public class NetworkManager
{
    // Always use ConfigureAwait(false) in library code
    public async Task<string> DownloadDataAsync(string url)
    {
        using var client = new HttpClient();
        var response = await client.GetAsync(url).ConfigureAwait(false);
        return await response.Content.ReadAsStringAsync().ConfigureAwait(false);
    }
    
    // Use ConfigureAwait(true) only when you need to return to the original context
    public async Task UpdateUIAsync(string data)
    {
        var processedData = await ProcessDataAsync(data).ConfigureAwait(false);
        
        // Need to return to UI thread for Unity
        await Task.Yield(); // Force continuation on Unity main thread
        UpdateUI(processedData);
    }
}
```

## Interview Preparation

### Performance-Related Interview Questions

**"How do you identify and fix performance bottlenecks in C#?"**
- Use profiling tools (Unity Profiler, dotTrace, PerfView)
- Identify hot paths through code analysis
- Measure before and after optimizations
- Focus on algorithmic improvements before micro-optimizations

**"Explain garbage collection impact and mitigation strategies"**
- Understand generational GC and allocation patterns
- Minimize allocations in frequently called code
- Use object pooling for temporary objects
- Implement proper disposal patterns for resources

**"How do you optimize memory usage in large applications?"**
- Structure of Arrays (SoA) for better cache locality
- Use appropriate collection types and sizes
- Implement lazy loading and caching strategies
- Monitor memory usage and detect leaks

### Key Takeaways

**Essential Performance Concepts:**
- Memory allocation patterns and GC pressure reduction
- Cache-friendly data structure design
- SIMD utilization for mathematical operations
- Async/await best practices for scalable applications

**Unity-Specific Optimizations:**
- Update loop management and batching
- String handling optimization for UI systems
- Component caching and reference management
- Physics and rendering performance considerations

**Professional Development:**
- Performance profiling and measurement techniques
- Code review focusing on performance implications
- Documentation of optimization decisions and trade-offs
- Knowledge sharing on performance best practices