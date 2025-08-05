# @k-Advanced-CSharp-Optimization-Techniques - Performance Mastery

## 🎯 Learning Objectives
- Master advanced C# optimization techniques for Unity and .NET applications
- Implement memory-efficient data structures and algorithms
- Optimize garbage collection performance and reduce allocations
- Create high-performance code patterns for game development
- Understand compiler optimizations and low-level performance considerations

## 🔧 Core Optimization Fundamentals

### Memory Allocation Optimization
```csharp
// Zero-allocation string manipulation for performance-critical code
public static class StringOptimization
{
    private static readonly StringBuilder _stringBuilder = new StringBuilder(256);
    private static readonly char[] _charBuffer = new char[64];
    
    // Zero-allocation string formatting for common scenarios
    public static string FormatScore(int score)
    {
        _stringBuilder.Clear();
        _stringBuilder.Append("Score: ");
        _stringBuilder.Append(score);
        return _stringBuilder.ToString();
    }
    
    // Zero-allocation number to string conversion
    public static string IntToString(int value)
    {
        if (value == 0) return "0";
        
        int length = 0;
        int temp = value;
        bool negative = value < 0;
        
        if (negative)
        {
            value = -value;
            temp = value;
        }
        
        // Calculate length
        while (temp > 0)
        {
            temp /= 10;
            length++;
        }
        
        if (negative) length++;
        
        // Fill buffer from right to left
        int index = length - 1;
        while (value > 0)
        {
            _charBuffer[index--] = (char)('0' + (value % 10));
            value /= 10;
        }
        
        if (negative) _charBuffer[0] = '-';
        
        return new string(_charBuffer, 0, length);
    }
    
    // String pooling for frequently used strings
    private static readonly Dictionary<string, string> _stringPool = new Dictionary<string, string>();
    
    public static string Intern(string str)
    {
        if (_stringPool.TryGetValue(str, out string pooled))
            return pooled;
        
        _stringPool[str] = str;
        return str;
    }
}

// Struct-based alternatives to reduce allocations
public readonly struct Vector2Int : IEquatable<Vector2Int>
{
    public readonly int x;
    public readonly int y;
    
    public Vector2Int(int x, int y)
    {
        this.x = x;
        this.y = y;
    }
    
    public static Vector2Int operator +(Vector2Int a, Vector2Int b)
        => new Vector2Int(a.x + b.x, a.y + b.y);
    
    public static Vector2Int operator -(Vector2Int a, Vector2Int b)
        => new Vector2Int(a.x - b.x, a.y - b.y);
    
    public bool Equals(Vector2Int other)
        => x == other.x && y == other.y;
    
    public override bool Equals(object obj)
        => obj is Vector2Int other && Equals(other);
    
    public override int GetHashCode()
        => (x << 16) | (ushort)y;
    
    public static bool operator ==(Vector2Int a, Vector2Int b) => a.Equals(b);
    public static bool operator !=(Vector2Int a, Vector2Int b) => !a.Equals(b);
}
```

### High-Performance Collections
```csharp
// Cache-friendly array-based collections for performance
public class FastList<T> : IEnumerable<T>
{
    private T[] _items;
    private int _count;
    
    public int Count => _count;
    public int Capacity => _items.Length;
    
    public ref T this[int index]
    {
        get
        {
            if (index >= _count)
                throw new IndexOutOfRangeException();
            return ref _items[index];
        }
    }
    
    public FastList(int capacity = 4)
    {
        _items = new T[capacity];
        _count = 0;
    }
    
    public void Add(T item)
    {
        if (_count == _items.Length)
            Resize();
        
        _items[_count++] = item;
    }
    
    public bool Remove(T item)
    {
        int index = IndexOf(item);
        if (index >= 0)
        {
            RemoveAt(index);
            return true;
        }
        return false;
    }
    
    public void RemoveAt(int index)
    {
        if (index >= _count)
            throw new IndexOutOfRangeException();
        
        _count--;
        if (index < _count)
        {
            Array.Copy(_items, index + 1, _items, index, _count - index);
        }
        
        _items[_count] = default(T);
    }
    
    public int IndexOf(T item)
    {
        return Array.IndexOf(_items, item, 0, _count);
    }
    
    public void Clear()
    {
        if (_count > 0)
        {
            Array.Clear(_items, 0, _count);
            _count = 0;
        }
    }
    
    private void Resize()
    {
        int newCapacity = _items.Length * 2;
        T[] newItems = new T[newCapacity];
        Array.Copy(_items, newItems, _count);
        _items = newItems;
    }
    
    // Span-based enumeration for zero-allocation iteration
    public ReadOnlySpan<T> AsSpan() => new ReadOnlySpan<T>(_items, 0, _count);
    
    public IEnumerator<T> GetEnumerator()
    {
        for (int i = 0; i < _count; i++)
            yield return _items[i];
    }
    
    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();
}

// Object pooling for frequently allocated objects
public class ObjectPool<T> where T : class, new()
{
    private readonly ConcurrentQueue<T> _pool = new ConcurrentQueue<T>();
    private readonly Func<T> _factory;
    private readonly Action<T> _resetAction;
    private readonly int _maxPoolSize;
    
    public ObjectPool(Func<T> factory = null, Action<T> resetAction = null, int maxPoolSize = 100)
    {
        _factory = factory ?? (() => new T());
        _resetAction = resetAction;
        _maxPoolSize = maxPoolSize;
    }
    
    public T Get()
    {
        if (_pool.TryDequeue(out T item))
            return item;
        
        return _factory();
    }
    
    public void Return(T item)
    {
        if (item == null) return;
        
        _resetAction?.Invoke(item);
        
        if (_pool.Count < _maxPoolSize)
            _pool.Enqueue(item);
    }
    
    public PooledObject<T> GetPooled() => new PooledObject<T>(this);
    
    public void Clear()
    {
        while (_pool.TryDequeue(out _)) { }
    }
}

// RAII-style pooled object management
public readonly struct PooledObject<T> : IDisposable where T : class, new()
{
    private readonly ObjectPool<T> _pool;
    public readonly T Value;
    
    internal PooledObject(ObjectPool<T> pool)
    {
        _pool = pool;
        Value = pool.Get();
    }
    
    public void Dispose()
    {
        _pool.Return(Value);
    }
}
```

### CPU Cache-Optimized Data Structures
```csharp
// Structure of Arrays (SoA) pattern for better cache performance
public class ParticleSystemSoA
{
    private const int INITIAL_CAPACITY = 1000;
    
    // Separate arrays for each component (better cache locality)
    private Vector3[] _positions;
    private Vector3[] _velocities;
    private float[] _lifetimes;
    private Color32[] _colors;
    private float[] _sizes;
    
    private int _count;
    private int _capacity;
    
    public int Count => _count;
    
    public ParticleSystemSoA(int capacity = INITIAL_CAPACITY)
    {
        _capacity = capacity;
        _positions = new Vector3[capacity];
        _velocities = new Vector3[capacity];
        _lifetimes = new float[capacity];
        _colors = new Color32[capacity];
        _sizes = new float[capacity];
        _count = 0;
    }
    
    public int AddParticle(Vector3 position, Vector3 velocity, float lifetime, Color32 color, float size)
    {
        if (_count >= _capacity)
            Resize();
        
        int index = _count++;
        _positions[index] = position;
        _velocities[index] = velocity;
        _lifetimes[index] = lifetime;
        _colors[index] = color;
        _sizes[index] = size;
        
        return index;
    }
    
    // Cache-friendly update loop processing one component at a time
    public void UpdatePositions(float deltaTime)
    {
        for (int i = 0; i < _count; i++)
        {
            _positions[i] += _velocities[i] * deltaTime;
        }
    }
    
    public void UpdateLifetimes(float deltaTime)
    {
        for (int i = 0; i < _count; i++)
        {
            _lifetimes[i] -= deltaTime;
        }
    }
    
    public void RemoveDeadParticles()
    {
        int writeIndex = 0;
        
        for (int readIndex = 0; readIndex < _count; readIndex++)
        {
            if (_lifetimes[readIndex] > 0)
            {
                if (writeIndex != readIndex)
                {
                    _positions[writeIndex] = _positions[readIndex];
                    _velocities[writeIndex] = _velocities[readIndex];
                    _lifetimes[writeIndex] = _lifetimes[readIndex];
                    _colors[writeIndex] = _colors[readIndex];
                    _sizes[writeIndex] = _sizes[readIndex];
                }
                writeIndex++;
            }
        }
        
        _count = writeIndex;
    }
    
    // Vectorized operations using SIMD when available
    public void ApplyGravity(Vector3 gravity, float deltaTime)
    {
        Vector3 gravityDelta = gravity * deltaTime;
        
        // Manual loop unrolling for better performance
        int i = 0;
        int remainder = _count % 4;
        int limit = _count - remainder;
        
        // Process 4 elements at a time
        for (; i < limit; i += 4)
        {
            _velocities[i] += gravityDelta;
            _velocities[i + 1] += gravityDelta;
            _velocities[i + 2] += gravityDelta;
            _velocities[i + 3] += gravityDelta;
        }
        
        // Handle remaining elements
        for (; i < _count; i++)
        {
            _velocities[i] += gravityDelta;
        }
    }
    
    private void Resize()
    {
        int newCapacity = _capacity * 2;
        Array.Resize(ref _positions, newCapacity);
        Array.Resize(ref _velocities, newCapacity);
        Array.Resize(ref _lifetimes, newCapacity);
        Array.Resize(ref _colors, newCapacity);
        Array.Resize(ref _sizes, newCapacity);
        _capacity = newCapacity;
    }
    
    // Span accessors for zero-allocation access
    public ReadOnlySpan<Vector3> Positions => new ReadOnlySpan<Vector3>(_positions, 0, _count);
    public ReadOnlySpan<Vector3> Velocities => new ReadOnlySpan<Vector3>(_velocities, 0, _count);
    public ReadOnlySpan<Color32> Colors => new ReadOnlySpan<Color32>(_colors, 0, _count);
}
```

### Advanced Algorithm Optimizations
```csharp
// Optimized spatial partitioning for collision detection
public class SpatialHashGrid<T> where T : class
{
    private struct Cell
    {
        public FastList<T> items;
        public int version;
    }
    
    private readonly Dictionary<long, Cell> _cells;
    private readonly float _cellSize;
    private readonly Func<T, Vector2> _getPosition;
    private int _currentVersion;
    
    public SpatialHashGrid(float cellSize, Func<T, Vector2> getPosition)
    {
        _cells = new Dictionary<long, Cell>();
        _cellSize = cellSize;
        _getPosition = getPosition;
        _currentVersion = 1;
    }
    
    public void Clear()
    {
        _currentVersion++;
        // Let old cells be garbage collected naturally
    }
    
    public void Insert(T item)
    {
        Vector2 pos = _getPosition(item);
        long cellKey = GetCellKey(pos);
        
        if (!_cells.TryGetValue(cellKey, out Cell cell) || cell.version != _currentVersion)
        {
            cell = new Cell
            {
                items = new FastList<T>(),
                version = _currentVersion
            };
            _cells[cellKey] = cell;
        }
        
        cell.items.Add(item);
    }
    
    public void Query(Vector2 position, float radius, FastList<T> results)
    {
        results.Clear();
        
        int minX = Mathf.FloorToInt((position.x - radius) / _cellSize);
        int maxX = Mathf.FloorToInt((position.x + radius) / _cellSize);
        int minY = Mathf.FloorToInt((position.y - radius) / _cellSize);
        int maxY = Mathf.FloorToInt((position.y + radius) / _cellSize);
        
        float radiusSquared = radius * radius;
        
        for (int x = minX; x <= maxX; x++)
        {
            for (int y = minY; y <= maxY; y++)
            {
                long cellKey = GetCellKey(x, y);
                
                if (_cells.TryGetValue(cellKey, out Cell cell) && cell.version == _currentVersion)
                {
                    var span = cell.items.AsSpan();
                    for (int i = 0; i < span.Length; i++)
                    {
                        T item = span[i];
                        Vector2 itemPos = _getPosition(item);
                        
                        float distSquared = (itemPos - position).sqrMagnitude;
                        if (distSquared <= radiusSquared)
                        {
                            results.Add(item);
                        }
                    }
                }
            }
        }
    }
    
    private long GetCellKey(Vector2 position)
    {
        int x = Mathf.FloorToInt(position.x / _cellSize);
        int y = Mathf.FloorToInt(position.y / _cellSize);
        return GetCellKey(x, y);
    }
    
    private long GetCellKey(int x, int y)
    {
        return ((long)x << 32) | (uint)y;
    }
}

// Optimized pathfinding with binary heap
public class OptimizedAStar
{
    private struct Node : IComparable<Node>
    {
        public Vector2Int position;
        public float gCost;
        public float hCost;
        public float fCost => gCost + hCost;
        public Vector2Int parent;
        
        public int CompareTo(Node other)
        {
            int compare = fCost.CompareTo(other.fCost);
            return compare == 0 ? hCost.CompareTo(other.hCost) : compare;
        }
    }
    
    private readonly BinaryHeap<Node> _openSet;
    private readonly Dictionary<Vector2Int, Node> _allNodes;
    private readonly HashSet<Vector2Int> _closedSet;
    private readonly Func<Vector2Int, bool> _isWalkable;
    
    public OptimizedAStar(Func<Vector2Int, bool> isWalkable)
    {
        _openSet = new BinaryHeap<Node>();
        _allNodes = new Dictionary<Vector2Int, Node>();
        _closedSet = new HashSet<Vector2Int>();
        _isWalkable = isWalkable;
    }
    
    public List<Vector2Int> FindPath(Vector2Int start, Vector2Int target)
    {
        _openSet.Clear();
        _allNodes.Clear();
        _closedSet.Clear();
        
        Node startNode = new Node
        {
            position = start,
            gCost = 0,
            hCost = ManhattanDistance(start, target),
            parent = start
        };
        
        _openSet.Push(startNode);
        _allNodes[start] = startNode;
        
        while (_openSet.Count > 0)
        {
            Node current = _openSet.Pop();
            
            if (current.position == target)
                return ReconstructPath(current);
            
            _closedSet.Add(current.position);
            
            foreach (Vector2Int neighbor in GetNeighbors(current.position))
            {
                if (!_isWalkable(neighbor) || _closedSet.Contains(neighbor))
                    continue;
                
                float tentativeGCost = current.gCost + 1f;
                
                if (!_allNodes.TryGetValue(neighbor, out Node neighborNode))
                {
                    neighborNode = new Node
                    {
                        position = neighbor,
                        gCost = tentativeGCost,
                        hCost = ManhattanDistance(neighbor, target),
                        parent = current.position
                    };
                    
                    _allNodes[neighbor] = neighborNode;
                    _openSet.Push(neighborNode);
                }
                else if (tentativeGCost < neighborNode.gCost)
                {
                    neighborNode.gCost = tentativeGCost;
                    neighborNode.parent = current.position;
                    _allNodes[neighbor] = neighborNode;
                    _openSet.UpdateItem(neighborNode);
                }
            }
        }
        
        return new List<Vector2Int>(); // No path found
    }
    
    private float ManhattanDistance(Vector2Int a, Vector2Int b)
    {
        return Mathf.Abs(a.x - b.x) + Mathf.Abs(a.y - b.y);
    }
    
    private IEnumerable<Vector2Int> GetNeighbors(Vector2Int position)
    {
        yield return new Vector2Int(position.x + 1, position.y);
        yield return new Vector2Int(position.x - 1, position.y);
        yield return new Vector2Int(position.x, position.y + 1);
        yield return new Vector2Int(position.x, position.y - 1);
    }
    
    private List<Vector2Int> ReconstructPath(Node target)
    {
        List<Vector2Int> path = new List<Vector2Int>();
        Vector2Int current = target.position;
        
        while (_allNodes.TryGetValue(current, out Node node) && node.position != node.parent)
        {
            path.Add(current);
            current = node.parent;
        }
        
        path.Add(current);
        path.Reverse();
        return path;
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### AI-Powered Code Optimization
```csharp
// AI-assisted performance profiling and optimization suggestions
public class AICodeOptimizer
{
    [System.Serializable]
    public class PerformanceMetrics
    {
        public string methodName;
        public long executionTimeNs;
        public int allocationsCount;
        public long memoryUsageBytes;
        public int callCount;
        public float averageExecutionTime;
    }
    
    [System.Serializable]
    public class OptimizationSuggestion
    {
        public string issue;
        public string suggestion;
        public string codeExample;
        public int priority; // 1-10 scale
        public float estimatedImprovement;
    }
    
    private readonly Dictionary<string, PerformanceMetrics> _metrics;
    private readonly List<OptimizationSuggestion> _suggestions;
    
    public AICodeOptimizer()
    {
        _metrics = new Dictionary<string, PerformanceMetrics>();
        _suggestions = new List<OptimizationSuggestion>();
    }
    
    public void ProfileMethod(string methodName, Action method)
    {
        long startMemory = GC.GetTotalMemory(false);
        Stopwatch stopwatch = Stopwatch.StartNew();
        
        method();
        
        stopwatch.Stop();
        long endMemory = GC.GetTotalMemory(false);
        
        UpdateMetrics(methodName, stopwatch.ElapsedTicks, endMemory - startMemory);
    }
    
    public async Task<List<OptimizationSuggestion>> AnalyzeAndSuggestOptimizations()
    {
        _suggestions.Clear();
        
        foreach (var metric in _metrics.Values)
        {
            await AnalyzeMethod(metric);
        }
        
        // Sort by priority and potential impact
        _suggestions.Sort((a, b) => 
        {
            int priorityCompare = b.priority.CompareTo(a.priority);
            return priorityCompare == 0 ? 
                b.estimatedImprovement.CompareTo(a.estimatedImprovement) : 
                priorityCompare;
        });
        
        return new List<OptimizationSuggestion>(_suggestions);
    }
    
    private async Task AnalyzeMethod(PerformanceMetrics metrics)
    {
        // AI analysis of performance bottlenecks
        if (metrics.allocationsCount > 100 && metrics.callCount > 10)
        {
            _suggestions.Add(new OptimizationSuggestion
            {
                issue = $"High allocation count in {metrics.methodName}",
                suggestion = "Consider object pooling or struct alternatives",
                codeExample = GenerateObjectPoolingExample(metrics.methodName),
                priority = 8,
                estimatedImprovement = 0.3f
            });
        }
        
        if (metrics.averageExecutionTime > 16.67f) // > 1 frame at 60 FPS
        {
            _suggestions.Add(new OptimizationSuggestion
            {
                issue = $"Long execution time in {metrics.methodName}",
                suggestion = "Consider breaking into smaller operations or async processing",
                codeExample = await GenerateAsyncExample(metrics.methodName),
                priority = 9,
                estimatedImprovement = 0.5f
            });
        }
        
        // AI-powered pattern recognition for optimization opportunities
        await AnalyzeAlgorithmicComplexity(metrics);
    }
    
    private void UpdateMetrics(string methodName, long elapsedTicks, long memoryDelta)
    {
        if (!_metrics.TryGetValue(methodName, out PerformanceMetrics metrics))
        {
            metrics = new PerformanceMetrics { methodName = methodName };
            _metrics[methodName] = metrics;
        }
        
        metrics.executionTimeNs += elapsedTicks * 100; // Convert to nanoseconds
        metrics.allocationsCount += memoryDelta > 0 ? 1 : 0;
        metrics.memoryUsageBytes += Math.Max(0, memoryDelta);
        metrics.callCount++;
        metrics.averageExecutionTime = metrics.executionTimeNs / (float)metrics.callCount / 1_000_000f; // Convert to ms
    }
    
    private string GenerateObjectPoolingExample(string methodName)
    {
        return $@"
// Original: {methodName} with high allocations
// Optimized version with object pooling:
private static readonly ObjectPool<SomeClass> _pool = new ObjectPool<SomeClass>();

public void Optimized{methodName}()
{{
    using var pooled = _pool.GetPooled();
    var obj = pooled.Value;
    // Use obj instead of creating new instances
}}";
    }
    
    private async Task<string> GenerateAsyncExample(string methodName)
    {
        // AI-generated async optimization example
        return $@"
// Original: {methodName} blocking main thread
// Optimized version with async processing:
public async Task Optimized{methodName}Async()
{{
    await Task.Run(() =>
    {{
        // Move heavy computation to background thread
        // Break large operations into smaller chunks
        // Use cancellation tokens for responsiveness
    }});
}}";
    }
    
    private async Task AnalyzeAlgorithmicComplexity(PerformanceMetrics metrics)
    {
        // AI analysis of algorithmic patterns and complexity
        // This would integrate with ML models trained on code patterns
        
        if (metrics.averageExecutionTime * metrics.callCount > 100f)
        {
            _suggestions.Add(new OptimizationSuggestion
            {
                issue = $"Potential O(n²) complexity detected in {metrics.methodName}",
                suggestion = "Consider using more efficient data structures or algorithms",
                codeExample = await GenerateAlgorithmOptimization(metrics.methodName),
                priority = 10,
                estimatedImprovement = 0.8f
            });
        }
    }
    
    private async Task<string> GenerateAlgorithmOptimization(string methodName)
    {
        // AI-suggested algorithmic improvements
        return $@"
// Consider these optimizations for {methodName}:
// 1. Use Dictionary<K,V> instead of List<T>.Find() for O(1) lookups
// 2. Implement spatial partitioning for collision detection
// 3. Use binary search for sorted data instead of linear search
// 4. Cache expensive calculations
// 5. Use SIMD operations for bulk data processing";
    }
}
```

## 💡 Key Optimization Highlights

### Compilation and JIT Optimizations
- **Method Inlining**: Use `[MethodImpl(MethodImplOptions.AggressiveInlining)]` for small, frequently called methods
- **Bounds Check Elimination**: Use `unsafe` code or Span<T> to eliminate array bounds checks
- **Dead Code Elimination**: Remove unused code branches and variables
- **Constant Folding**: Use `const` and `readonly` for compile-time optimizations

### Memory Access Patterns
- **Cache Locality**: Structure data for sequential access patterns
- **False Sharing**: Avoid cache line conflicts in multi-threaded scenarios
- **Memory Alignment**: Use proper struct layout for optimal memory access
- **Prefetching**: Implement data prefetching for predictable access patterns

### Garbage Collection Optimization
- **Generation Awareness**: Minimize Gen 2 collections through proper object lifetime management
- **Large Object Heap**: Avoid unnecessary large allocations (>85KB)
- **Weak References**: Use weak references for cached data that can be recreated
- **Finalizer Optimization**: Avoid finalizers or implement IDisposable properly

### SIMD and Vectorization
- **System.Numerics.Vector**: Use built-in vectorization for mathematical operations
- **Span<T> and Memory<T>**: Leverage modern .NET memory management primitives
- **Unsafe Code**: Use unsafe pointers for maximum performance in critical sections
- **Intrinsics**: Use hardware-specific intrinsics for specialized operations

This comprehensive guide provides advanced C# optimization techniques essential for high-performance Unity game development and .NET applications, covering memory management, algorithmic optimization, and modern language features.