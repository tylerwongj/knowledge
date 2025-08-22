# @o-Advanced-CSharp-Unity-Performance-Patterns

## 🎯 Learning Objectives
- Master C# performance optimization techniques specific to Unity
- Implement advanced memory management patterns
- Design high-performance data structures for game development
- Apply CPU and garbage collection optimization strategies

## 🔧 Memory-Efficient Data Structures

### Object Pooling with Generic Constraints
```csharp
// Advanced object pooling system with type safety
public interface IPoolable
{
    void OnReturnToPool();
    void OnTakeFromPool();
}

public class AdvancedObjectPool<T> where T : class, IPoolable, new()
{
    private readonly Stack<T> pool = new Stack<T>();
    private readonly HashSet<T> activeObjects = new HashSet<T>();
    private readonly int maxSize;
    private readonly Func<T> createFunc;
    private readonly Action<T> resetAction;
    
    public int PooledCount => pool.Count;
    public int ActiveCount => activeObjects.Count;
    public int TotalCreated { get; private set; }
    
    public AdvancedObjectPool(int maxSize = 100, Func<T> createFunc = null, Action<T> resetAction = null)
    {
        this.maxSize = maxSize;
        this.createFunc = createFunc ?? (() => new T());
        this.resetAction = resetAction;
    }
    
    public T Get()
    {
        T item;
        
        if (pool.Count > 0)
        {
            item = pool.Pop();
        }
        else
        {
            item = createFunc();
            TotalCreated++;
        }
        
        activeObjects.Add(item);
        item.OnTakeFromPool();
        return item;
    }
    
    public void Return(T item)
    {
        if (item == null || !activeObjects.Contains(item))
            return;
        
        activeObjects.Remove(item);
        item.OnReturnToPool();
        resetAction?.Invoke(item);
        
        if (pool.Count < maxSize)
        {
            pool.Push(item);
        }
    }
    
    public void ReturnAll()
    {
        var activeList = new List<T>(activeObjects);
        foreach (var item in activeList)
        {
            Return(item);
        }
    }
    
    public void Warmup(int count)
    {
        for (int i = 0; i < count && pool.Count < maxSize; i++)
        {
            var item = createFunc();
            TotalCreated++;
            item.OnReturnToPool();
            resetAction?.Invoke(item);
            pool.Push(item);
        }
    }
    
    public void Clear()
    {
        pool.Clear();
        activeObjects.Clear();
        TotalCreated = 0;
    }
}

// Example poolable game object
public class PooledProjectile : MonoBehaviour, IPoolable
{
    [Header("Projectile Settings")]
    [SerializeField] private float speed = 10f;
    [SerializeField] private float lifetime = 5f;
    
    private Rigidbody rb;
    private float timeAlive;
    private AdvancedObjectPool<PooledProjectile> parentPool;
    
    void Awake()
    {
        rb = GetComponent<Rigidbody>();
    }
    
    public void Initialize(AdvancedObjectPool<PooledProjectile> pool)
    {
        parentPool = pool;
    }
    
    public void OnTakeFromPool()
    {
        gameObject.SetActive(true);
        timeAlive = 0f;
        rb.velocity = Vector3.zero;
        rb.angularVelocity = Vector3.zero;
    }
    
    public void OnReturnToPool()
    {
        gameObject.SetActive(false);
    }
    
    public void Launch(Vector3 direction, Vector3 position)
    {
        transform.position = position;
        transform.rotation = Quaternion.LookRotation(direction);
        rb.velocity = direction.normalized * speed;
    }
    
    void Update()
    {
        timeAlive += Time.deltaTime;
        if (timeAlive >= lifetime)
        {
            parentPool?.Return(this);
        }
    }
    
    void OnTriggerEnter(Collider other)
    {
        // Handle collision and return to pool
        parentPool?.Return(this);
    }
}
```

### High-Performance Collections
```csharp
// Memory-efficient ring buffer for streaming data
public class RingBuffer<T> : IEnumerable<T>
{
    private readonly T[] buffer;
    private int head;
    private int tail;
    private int count;
    private readonly int capacity;
    
    public int Count => count;
    public int Capacity => capacity;
    public bool IsFull => count == capacity;
    public bool IsEmpty => count == 0;
    
    public RingBuffer(int capacity)
    {
        if (capacity <= 0)
            throw new ArgumentException("Capacity must be greater than 0");
        
        this.capacity = capacity;
        buffer = new T[capacity];
        head = 0;
        tail = 0;
        count = 0;
    }
    
    public void Enqueue(T item)
    {
        buffer[tail] = item;
        tail = (tail + 1) % capacity;
        
        if (count < capacity)
        {
            count++;
        }
        else
        {
            // Buffer is full, overwrite oldest element
            head = (head + 1) % capacity;
        }
    }
    
    public T Dequeue()
    {
        if (IsEmpty)
            throw new InvalidOperationException("Buffer is empty");
        
        T item = buffer[head];
        buffer[head] = default(T); // Clear reference
        head = (head + 1) % capacity;
        count--;
        
        return item;
    }
    
    public bool TryDequeue(out T item)
    {
        if (IsEmpty)
        {
            item = default(T);
            return false;
        }
        
        item = Dequeue();
        return true;
    }
    
    public T Peek()
    {
        if (IsEmpty)
            throw new InvalidOperationException("Buffer is empty");
        
        return buffer[head];
    }
    
    public T this[int index]
    {
        get
        {
            if (index < 0 || index >= count)
                throw new IndexOutOfRangeException();
            
            return buffer[(head + index) % capacity];
        }
    }
    
    public void Clear()
    {
        Array.Clear(buffer, 0, capacity);
        head = 0;
        tail = 0;
        count = 0;
    }
    
    public IEnumerator<T> GetEnumerator()
    {
        for (int i = 0; i < count; i++)
        {
            yield return buffer[(head + i) % capacity];
        }
    }
    
    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();
    
    // Batch operations for better performance
    public int EnqueueBatch(ReadOnlySpan<T> items)
    {
        int enqueued = 0;
        foreach (var item in items)
        {
            if (count < capacity || IsFull)
            {
                Enqueue(item);
                enqueued++;
            }
            else
            {
                break;
            }
        }
        return enqueued;
    }
    
    public int DequeueBatch(Span<T> destination)
    {
        int dequeued = 0;
        for (int i = 0; i < destination.Length && !IsEmpty; i++)
        {
            destination[i] = Dequeue();
            dequeued++;
        }
        return dequeued;
    }
}
```

### Native Array Integration
```csharp
// High-performance Unity Job System integration
using Unity.Collections;
using Unity.Jobs;
using Unity.Mathematics;

public struct ParticleUpdateJob : IJobParallelFor
{
    public NativeArray<float3> positions;
    public NativeArray<float3> velocities;
    [ReadOnly] public float deltaTime;
    [ReadOnly] public float3 gravity;
    [ReadOnly] public float damping;
    
    public void Execute(int index)
    {
        var pos = positions[index];
        var vel = velocities[index];
        
        // Apply gravity
        vel += gravity * deltaTime;
        
        // Apply damping
        vel *= damping;
        
        // Update position
        pos += vel * deltaTime;
        
        // Simple ground collision
        if (pos.y < 0f)
        {
            pos.y = 0f;
            vel.y = -vel.y * 0.8f; // Bounce with energy loss
        }
        
        positions[index] = pos;
        velocities[index] = vel;
    }
}

// Particle system using Job System and Native Arrays
public class HighPerformanceParticleSystem : MonoBehaviour
{
    [Header("Particle Settings")]
    [SerializeField] private int maxParticles = 10000;
    [SerializeField] private float3 gravity = new float3(0, -9.81f, 0);
    [SerializeField] private float damping = 0.99f;
    [SerializeField] private Mesh particleMesh;
    [SerializeField] private Material particleMaterial;
    
    private NativeArray<float3> positions;
    private NativeArray<float3> velocities;
    private NativeArray<Matrix4x4> matrices;
    
    private int activeParticles;
    private JobHandle jobHandle;
    
    void Start()
    {
        InitializeNativeArrays();
    }
    
    void InitializeNativeArrays()
    {
        positions = new NativeArray<float3>(maxParticles, Allocator.Persistent);
        velocities = new NativeArray<float3>(maxParticles, Allocator.Persistent);
        matrices = new NativeArray<Matrix4x4>(maxParticles, Allocator.Persistent);
        
        // Initialize with default values
        for (int i = 0; i < maxParticles; i++)
        {
            positions[i] = float3.zero;
            velocities[i] = float3.zero;
            matrices[i] = Matrix4x4.identity;
        }
    }
    
    void Update()
    {
        // Complete previous frame's job
        jobHandle.Complete();
        
        // Schedule particle update job
        var updateJob = new ParticleUpdateJob
        {
            positions = positions,
            velocities = velocities,
            deltaTime = Time.deltaTime,
            gravity = gravity,
            damping = damping
        };
        
        jobHandle = updateJob.Schedule(activeParticles, 32);
        
        // Update matrices for rendering (on main thread for now)
        UpdateMatrices();
        
        // Render particles using Graphics.DrawMeshInstanced
        RenderParticles();
    }
    
    void UpdateMatrices()
    {
        for (int i = 0; i < activeParticles; i++)
        {
            matrices[i] = Matrix4x4.TRS(positions[i], quaternion.identity, Vector3.one);
        }
    }
    
    void RenderParticles()
    {
        if (activeParticles == 0) return;
        
        // Use Graphics.DrawMeshInstanced for efficient batch rendering
        const int maxInstancesPerBatch = 1023; // Unity limitation
        int batches = Mathf.CeilToInt((float)activeParticles / maxInstancesPerBatch);
        
        for (int batch = 0; batch < batches; batch++)
        {
            int startIndex = batch * maxInstancesPerBatch;
            int count = Mathf.Min(maxInstancesPerBatch, activeParticles - startIndex);
            
            var batchMatrices = new Matrix4x4[count];
            for (int i = 0; i < count; i++)
            {
                batchMatrices[i] = matrices[startIndex + i];
            }
            
            Graphics.DrawMeshInstanced(particleMesh, 0, particleMaterial, batchMatrices);
        }
    }
    
    public void EmitParticle(float3 position, float3 velocity)
    {
        if (activeParticles < maxParticles)
        {
            positions[activeParticles] = position;
            velocities[activeParticles] = velocity;
            activeParticles++;
        }
    }
    
    void OnDestroy()
    {
        jobHandle.Complete();
        
        if (positions.IsCreated)
            positions.Dispose();
        if (velocities.IsCreated)
            velocities.Dispose();
        if (matrices.IsCreated)
            matrices.Dispose();
    }
}
```

## ⚡ CPU Performance Optimization

### Burst-Compatible Code Patterns
```csharp
using Unity.Burst;
using Unity.Collections;
using Unity.Jobs;
using Unity.Mathematics;

// Burst-compiled math operations
[BurstCompile]
public struct FastMathOperations
{
    // Fast inverse square root (Quake algorithm)
    public static float FastInvSqrt(float x)
    {
        float xhalf = 0.5f * x;
        int i = *(int*)&x;
        i = 0x5f3759df - (i >> 1);
        x = *(float*)&i;
        x = x * (1.5f - xhalf * x * x);
        return x;
    }
    
    // Optimized distance calculation without sqrt
    public static float DistanceSquared(float3 a, float3 b)
    {
        float3 diff = a - b;
        return math.dot(diff, diff);
    }
    
    // Fast approximation of sine using polynomial
    public static float FastSin(float x)
    {
        // Normalize to [-π, π]
        const float PI = 3.14159265359f;
        while (x > PI) x -= 2 * PI;
        while (x < -PI) x += 2 * PI;
        
        // Use polynomial approximation: sin(x) ≈ x - x³/6 + x⁵/120
        float x2 = x * x;
        float x3 = x2 * x;
        float x5 = x3 * x2;
        return x - (x3 / 6.0f) + (x5 / 120.0f);
    }
    
    // Efficient 2D rotation
    public static float2 Rotate2D(float2 point, float angle)
    {
        float cos = math.cos(angle);
        float sin = math.sin(angle);
        return new float2(
            point.x * cos - point.y * sin,
            point.x * sin + point.y * cos
        );
    }
}

// Burst-compiled spatial partitioning
[BurstCompile]
public struct SpatialHashJob : IJobParallelFor
{
    [ReadOnly] public NativeArray<float3> positions;
    [WriteOnly] public NativeArray<int> spatialHashes;
    [ReadOnly] public float cellSize;
    [ReadOnly] public int3 gridDimensions;
    
    public void Execute(int index)
    {
        var pos = positions[index];
        var gridPos = new int3(
            (int)(pos.x / cellSize),
            (int)(pos.y / cellSize),
            (int)(pos.z / cellSize)
        );
        
        // Clamp to grid bounds
        gridPos = math.clamp(gridPos, int3.zero, gridDimensions - 1);
        
        // Convert 3D grid position to 1D hash
        spatialHashes[index] = gridPos.x + 
                              gridPos.y * gridDimensions.x + 
                              gridPos.z * gridDimensions.x * gridDimensions.y;
    }
}
```

### Memory Layout Optimization
```csharp
// Structure of Arrays (SoA) for better cache performance
public class OptimizedEntityManager
{
    // Instead of Array of Structures (AoS)
    // struct Entity { Vector3 position; Vector3 velocity; float health; int id; }
    
    // Use Structure of Arrays (SoA) for better cache locality
    private Vector3[] positions;
    private Vector3[] velocities;
    private float[] healths;
    private int[] ids;
    
    private int entityCount;
    private int capacity;
    
    public OptimizedEntityManager(int initialCapacity = 1000)
    {
        capacity = initialCapacity;
        positions = new Vector3[capacity];
        velocities = new Vector3[capacity];
        healths = new float[capacity];
        ids = new int[capacity];
        entityCount = 0;
    }
    
    public int CreateEntity(Vector3 position, Vector3 velocity, float health)
    {
        if (entityCount >= capacity)
        {
            ResizeArrays();
        }
        
        int entityId = entityCount;
        positions[entityId] = position;
        velocities[entityId] = velocity;
        healths[entityId] = health;
        ids[entityId] = entityId;
        entityCount++;
        
        return entityId;
    }
    
    public void RemoveEntity(int entityId)
    {
        if (entityId < 0 || entityId >= entityCount) return;
        
        // Swap with last entity to avoid gaps
        int lastIndex = entityCount - 1;
        if (entityId != lastIndex)
        {
            positions[entityId] = positions[lastIndex];
            velocities[entityId] = velocities[lastIndex];
            healths[entityId] = healths[lastIndex];
            ids[entityId] = ids[lastIndex];
        }
        
        entityCount--;
    }
    
    // Batch operations for better performance
    public void UpdatePositions(float deltaTime)
    {
        // Process positions and velocities in sequence for better cache usage
        for (int i = 0; i < entityCount; i++)
        {
            positions[i] += velocities[i] * deltaTime;
        }
    }
    
    // SIMD-friendly processing
    public void ProcessEntitiesInBatches(System.Action<int, int> processor, int batchSize = 64)
    {
        for (int start = 0; start < entityCount; start += batchSize)
        {
            int end = Mathf.Min(start + batchSize, entityCount);
            processor(start, end);
        }
    }
    
    private void ResizeArrays()
    {
        int newCapacity = capacity * 2;
        
        System.Array.Resize(ref positions, newCapacity);
        System.Array.Resize(ref velocities, newCapacity);
        System.Array.Resize(ref healths, newCapacity);
        System.Array.Resize(ref ids, newCapacity);
        
        capacity = newCapacity;
    }
    
    // Property accessors with bounds checking in debug builds only
    public Vector3 GetPosition(int entityId)
    {
        #if DEBUG
        if (entityId < 0 || entityId >= entityCount)
            throw new IndexOutOfRangeException($"Entity ID {entityId} out of range");
        #endif
        return positions[entityId];
    }
    
    public void SetPosition(int entityId, Vector3 position)
    {
        #if DEBUG
        if (entityId < 0 || entityId >= entityCount)
            throw new IndexOutOfRangeException($"Entity ID {entityId} out of range");
        #endif
        positions[entityId] = position;
    }
    
    // Span-based operations for zero-allocation processing
    public ReadOnlySpan<Vector3> GetPositionsSpan() => positions.AsSpan(0, entityCount);
    public ReadOnlySpan<Vector3> GetVelocitiesSpan() => velocities.AsSpan(0, entityCount);
    public ReadOnlySpan<float> GetHealthsSpan() => healths.AsSpan(0, entityCount);
}
```

## 🚀 AI/LLM Integration Opportunities

### Performance Analysis Automation
```csharp
public class PerformanceProfiler : MonoBehaviour
{
    public class PerformanceMetrics
    {
        public float averageFrameTime;
        public long allocatedMemory;
        public int gcCollections;
        public Dictionary<string, float> methodTimings;
    }
    
    public static string GenerateOptimizationPrompt(PerformanceMetrics metrics)
    {
        return $@"
        Analyze Unity C# performance metrics:
        - Frame Time: {metrics.averageFrameTime:F2}ms
        - Memory: {metrics.allocatedMemory / (1024 * 1024)}MB
        - GC Collections: {metrics.gcCollections}
        - Hot Methods: {string.Join(", ", metrics.methodTimings.Take(5).Select(kvp => $"{kvp.Key}: {kvp.Value:F2}ms"))}
        
        Provide specific optimization recommendations:
        1. Memory allocation reduction strategies
        2. CPU hotspot optimization approaches
        3. Garbage collection minimization techniques
        4. Unity-specific performance patterns
        ";
    }
}
```

### Code Pattern Analysis
```csharp
public class CodeAnalyzer
{
    public static string GeneratePatternAnalysisPrompt(string codeSnippet)
    {
        return $@"
        Analyze this Unity C# code for performance issues:
        
        ```csharp
        {codeSnippet}
        ```
        
        Identify and suggest improvements for:
        1. Memory allocation patterns
        2. Loop optimizations
        3. LINQ usage efficiency
        4. Object pooling opportunities
        5. Burst compilation compatibility
        6. Job System integration potential
        ";
    }
}
```

## 💡 Key Highlights

### Performance Patterns
- **Object Pooling**: Advanced generic pooling with lifecycle management
- **Native Collections**: Unity Job System integration with Burst compilation
- **Memory Layout**: Structure of Arrays for cache-friendly data access
- **SIMD Operations**: Burst-compatible math operations and algorithms

### Production Considerations
- **Profiling Integration**: Built-in performance monitoring and analysis
- **Scalability**: Dynamic capacity management and batch processing
- **Cross-Platform**: Platform-agnostic optimization strategies
- **Maintainability**: Clean separation of data and logic for testability

### Interview-Ready Knowledge
- Deep understanding of C# memory management in Unity context
- Advanced data structure implementations optimized for games
- Job System and Burst compilation integration patterns
- Performance analysis and optimization methodologies

This advanced C# performance guide provides the technical depth required for senior Unity developer positions, focusing on production-ready optimization patterns and modern Unity development practices.