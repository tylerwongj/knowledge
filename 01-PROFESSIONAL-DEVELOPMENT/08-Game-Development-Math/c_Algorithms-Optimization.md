# Algorithms & Optimization

## Overview
Master essential algorithms, data structures, and optimization techniques for high-performance game development and technical interviews.

## Key Concepts

### Pathfinding Algorithms

**A* Pathfinding Implementation:**
```csharp
public class AStarPathfinder : MonoBehaviour
{
    [Header("Pathfinding Settings")]
    [SerializeField] private LayerMask obstacleLayer;
    [SerializeField] private float nodeSize = 1f;
    [SerializeField] private bool allowDiagonal = true;
    [SerializeField] private bool visualizeGrid = false;
    
    private Dictionary<Vector2Int, PathNode> nodes = new Dictionary<Vector2Int, PathNode>();
    private PriorityQueue<PathNode> openSet = new PriorityQueue<PathNode>();
    private HashSet<Vector2Int> closedSet = new HashSet<Vector2Int>();
    
    [System.Serializable]
    public class PathNode : IComparable<PathNode>
    {
        public Vector2Int position;
        public float gCost;      // Distance from start
        public float hCost;      // Heuristic distance to goal
        public float fCost => gCost + hCost;
        public PathNode parent;
        public bool walkable;
        
        public PathNode(Vector2Int pos, bool isWalkable = true)
        {
            position = pos;
            walkable = isWalkable;
            gCost = float.MaxValue;
            hCost = 0f;
        }
        
        public int CompareTo(PathNode other)
        {
            int compare = fCost.CompareTo(other.fCost);
            if (compare == 0)
                compare = hCost.CompareTo(other.hCost);
            return compare;
        }
    }
    
    public List<Vector3> FindPath(Vector3 startWorld, Vector3 targetWorld)
    {
        Vector2Int startGrid = WorldToGrid(startWorld);
        Vector2Int targetGrid = WorldToGrid(targetWorld);
        
        // Clear previous pathfinding data
        nodes.Clear();
        openSet.Clear();
        closedSet.Clear();
        
        // Initialize start node
        PathNode startNode = GetNode(startGrid);
        startNode.gCost = 0f;
        startNode.hCost = GetHeuristic(startGrid, targetGrid);
        openSet.Enqueue(startNode);
        
        while (openSet.Count > 0)
        {
            PathNode currentNode = openSet.Dequeue();
            closedSet.Add(currentNode.position);
            
            // Check if we reached the target
            if (currentNode.position == targetGrid)
            {
                return ReconstructPath(currentNode);
            }
            
            // Explore neighbors
            foreach (Vector2Int neighborPos in GetNeighbors(currentNode.position))
            {
                if (closedSet.Contains(neighborPos)) continue;
                
                PathNode neighborNode = GetNode(neighborPos);
                if (!neighborNode.walkable) continue;
                
                float tentativeGCost = currentNode.gCost + GetDistance(currentNode.position, neighborPos);
                
                if (tentativeGCost < neighborNode.gCost)
                {
                    neighborNode.parent = currentNode;
                    neighborNode.gCost = tentativeGCost;
                    neighborNode.hCost = GetHeuristic(neighborPos, targetGrid);
                    
                    if (!openSet.Contains(neighborNode))
                    {
                        openSet.Enqueue(neighborNode);
                    }
                }
            }
        }
        
        return new List<Vector3>(); // No path found
    }
    
    PathNode GetNode(Vector2Int position)
    {
        if (!nodes.ContainsKey(position))
        {
            bool walkable = IsWalkable(position);
            nodes[position] = new PathNode(position, walkable);
        }
        return nodes[position];
    }
    
    bool IsWalkable(Vector2Int gridPos)
    {
        Vector3 worldPos = GridToWorld(gridPos);
        return !Physics.CheckSphere(worldPos, nodeSize * 0.4f, obstacleLayer);
    }
    
    List<Vector2Int> GetNeighbors(Vector2Int position)
    {
        List<Vector2Int> neighbors = new List<Vector2Int>();
        
        // Cardinal directions
        neighbors.Add(position + Vector2Int.up);
        neighbors.Add(position + Vector2Int.down);
        neighbors.Add(position + Vector2Int.left);
        neighbors.Add(position + Vector2Int.right);
        
        // Diagonal directions
        if (allowDiagonal)
        {
            neighbors.Add(position + new Vector2Int(1, 1));
            neighbors.Add(position + new Vector2Int(1, -1));
            neighbors.Add(position + new Vector2Int(-1, 1));
            neighbors.Add(position + new Vector2Int(-1, -1));
        }
        
        return neighbors;
    }
    
    float GetHeuristic(Vector2Int a, Vector2Int b)
    {
        if (allowDiagonal)
        {
            // Octile distance (allows diagonal movement)
            int dx = Mathf.Abs(a.x - b.x);
            int dy = Mathf.Abs(a.y - b.y);
            return (dx + dy) + (Mathf.Sqrt(2) - 2) * Mathf.Min(dx, dy);
        }
        else
        {
            // Manhattan distance
            return Mathf.Abs(a.x - b.x) + Mathf.Abs(a.y - b.y);
        }
    }
    
    float GetDistance(Vector2Int a, Vector2Int b)
    {
        int dx = Mathf.Abs(a.x - b.x);
        int dy = Mathf.Abs(a.y - b.y);
        
        if (dx == 1 && dy == 1)
            return Mathf.Sqrt(2); // Diagonal movement
        else
            return 1f; // Straight movement
    }
    
    List<Vector3> ReconstructPath(PathNode endNode)
    {
        List<Vector3> path = new List<Vector3>();
        PathNode currentNode = endNode;
        
        while (currentNode != null)
        {
            path.Add(GridToWorld(currentNode.position));
            currentNode = currentNode.parent;
        }
        
        path.Reverse();
        return SmoothPath(path);
    }
    
    List<Vector3> SmoothPath(List<Vector3> originalPath)
    {
        if (originalPath.Count <= 2) return originalPath;
        
        List<Vector3> smoothedPath = new List<Vector3> { originalPath[0] };
        int currentIndex = 0;
        
        while (currentIndex < originalPath.Count - 1)
        {
            int furthestIndex = currentIndex + 1;
            
            // Find the furthest point we can reach with a straight line
            for (int i = currentIndex + 2; i < originalPath.Count; i++)
            {
                if (HasLineOfSight(originalPath[currentIndex], originalPath[i]))
                {
                    furthestIndex = i;
                }
                else
                {
                    break;
                }
            }
            
            smoothedPath.Add(originalPath[furthestIndex]);
            currentIndex = furthestIndex;
        }
        
        return smoothedPath;
    }
    
    bool HasLineOfSight(Vector3 start, Vector3 end)
    {
        Vector3 direction = (end - start).normalized;
        float distance = Vector3.Distance(start, end);
        
        return !Physics.Raycast(start + Vector3.up * 0.1f, direction, distance - 0.1f, obstacleLayer);
    }
    
    Vector2Int WorldToGrid(Vector3 worldPos)
    {
        return new Vector2Int(
            Mathf.RoundToInt(worldPos.x / nodeSize),
            Mathf.RoundToInt(worldPos.z / nodeSize)
        );
    }
    
    Vector3 GridToWorld(Vector2Int gridPos)
    {
        return new Vector3(gridPos.x * nodeSize, 0, gridPos.y * nodeSize);
    }
    
    void OnDrawGizmos()
    {
        if (!visualizeGrid) return;
        
        // Draw grid and obstacles
        Gizmos.color = Color.white;
        for (int x = -20; x <= 20; x++)
        {
            for (int z = -20; z <= 20; z++)
            {
                Vector2Int gridPos = new Vector2Int(x, z);
                Vector3 worldPos = GridToWorld(gridPos);
                
                if (IsWalkable(gridPos))
                {
                    Gizmos.color = Color.green;
                }
                else
                {
                    Gizmos.color = Color.red;
                }
                
                Gizmos.DrawWireCube(worldPos, Vector3.one * nodeSize * 0.9f);
            }
        }
    }
}

// Priority Queue implementation for A*
public class PriorityQueue<T> where T : IComparable<T>
{
    private List<T> heap = new List<T>();
    
    public int Count => heap.Count;
    
    public void Enqueue(T item)
    {
        heap.Add(item);
        HeapifyUp(heap.Count - 1);
    }
    
    public T Dequeue()
    {
        if (heap.Count == 0) throw new InvalidOperationException("Queue is empty");
        
        T result = heap[0];
        heap[0] = heap[heap.Count - 1];
        heap.RemoveAt(heap.Count - 1);
        
        if (heap.Count > 0)
            HeapifyDown(0);
        
        return result;
    }
    
    public bool Contains(T item)
    {
        return heap.Contains(item);
    }
    
    public void Clear()
    {
        heap.Clear();
    }
    
    private void HeapifyUp(int index)
    {
        while (index > 0)
        {
            int parentIndex = (index - 1) / 2;
            if (heap[index].CompareTo(heap[parentIndex]) >= 0) break;
            
            Swap(index, parentIndex);
            index = parentIndex;
        }
    }
    
    private void HeapifyDown(int index)
    {
        while (true)
        {
            int leftChild = 2 * index + 1;
            int rightChild = 2 * index + 2;
            int smallest = index;
            
            if (leftChild < heap.Count && heap[leftChild].CompareTo(heap[smallest]) < 0)
                smallest = leftChild;
            
            if (rightChild < heap.Count && heap[rightChild].CompareTo(heap[smallest]) < 0)
                smallest = rightChild;
            
            if (smallest == index) break;
            
            Swap(index, smallest);
            index = smallest;
        }
    }
    
    private void Swap(int i, int j)
    {
        T temp = heap[i];
        heap[i] = heap[j];
        heap[j] = temp;
    }
}
```

### Sorting and Search Algorithms

**Game-Specific Sorting Implementation:**
```csharp
public class GameSortingAlgorithms : MonoBehaviour
{
    [Header("Performance Testing")]
    [SerializeField] private int testArraySize = 10000;
    [SerializeField] private bool runPerformanceTests = false;
    
    void Start()
    {
        if (runPerformanceTests)
        {
            RunSortingPerformanceTests();
        }
    }
    
    // Quick Sort - Good for general purpose sorting
    public static void QuickSort<T>(T[] array, int low, int high) where T : IComparable<T>
    {
        if (low < high)
        {
            int partitionIndex = Partition(array, low, high);
            QuickSort(array, low, partitionIndex - 1);
            QuickSort(array, partitionIndex + 1, high);
        }
    }
    
    private static int Partition<T>(T[] array, int low, int high) where T : IComparable<T>
    {
        T pivot = array[high];
        int i = low - 1;
        
        for (int j = low; j < high; j++)
        {
            if (array[j].CompareTo(pivot) <= 0)
            {
                i++;
                Swap(array, i, j);
            }
        }
        
        Swap(array, i + 1, high);
        return i + 1;
    }
    
    // Heap Sort - Consistent O(n log n) performance
    public static void HeapSort<T>(T[] array) where T : IComparable<T>
    {
        int n = array.Length;
        
        // Build max heap
        for (int i = n / 2 - 1; i >= 0; i--)
        {
            Heapify(array, n, i);
        }
        
        // Extract elements from heap one by one
        for (int i = n - 1; i > 0; i--)
        {
            Swap(array, 0, i);
            Heapify(array, i, 0);
        }
    }
    
    private static void Heapify<T>(T[] array, int n, int i) where T : IComparable<T>
    {
        int largest = i;
        int left = 2 * i + 1;
        int right = 2 * i + 2;
        
        if (left < n && array[left].CompareTo(array[largest]) > 0)
            largest = left;
        
        if (right < n && array[right].CompareTo(array[largest]) > 0)
            largest = right;
        
        if (largest != i)
        {
            Swap(array, i, largest);
            Heapify(array, n, largest);
        }
    }
    
    // Radix Sort - Excellent for integers (enemy IDs, scores, etc.)
    public static void RadixSort(int[] array)
    {
        int max = GetMaxValue(array);
        
        for (int exp = 1; max / exp > 0; exp *= 10)
        {
            CountingSortByDigit(array, exp);
        }
    }
    
    private static void CountingSortByDigit(int[] array, int exp)
    {
        int n = array.Length;
        int[] output = new int[n];
        int[] count = new int[10];
        
        // Count occurrences of each digit
        for (int i = 0; i < n; i++)
        {
            count[(array[i] / exp) % 10]++;
        }
        
        // Change count[i] to actual position
        for (int i = 1; i < 10; i++)
        {
            count[i] += count[i - 1];
        }
        
        // Build output array
        for (int i = n - 1; i >= 0; i--)
        {
            output[count[(array[i] / exp) % 10] - 1] = array[i];
            count[(array[i] / exp) % 10]--;
        }
        
        // Copy output array back to original
        for (int i = 0; i < n; i++)
        {
            array[i] = output[i];
        }
    }
    
    private static int GetMaxValue(int[] array)
    {
        int max = array[0];
        for (int i = 1; i < array.Length; i++)
        {
            if (array[i] > max) max = array[i];
        }
        return max;
    }
    
    // Binary Search - Fast searching in sorted arrays
    public static int BinarySearch<T>(T[] array, T target) where T : IComparable<T>
    {
        int left = 0;
        int right = array.Length - 1;
        
        while (left <= right)
        {
            int mid = left + (right - left) / 2;
            int comparison = array[mid].CompareTo(target);
            
            if (comparison == 0)
                return mid;
            else if (comparison < 0)
                left = mid + 1;
            else
                right = mid - 1;
        }
        
        return -1; // Not found
    }
    
    // Interpolation Search - Better than binary search for uniformly distributed data
    public static int InterpolationSearch(int[] array, int target)
    {
        int left = 0;
        int right = array.Length - 1;
        
        while (left <= right && target >= array[left] && target <= array[right])
        {
            if (left == right)
            {
                return array[left] == target ? left : -1;
            }
            
            // Estimate position
            int pos = left + ((target - array[left]) * (right - left)) / (array[right] - array[left]);
            
            if (array[pos] == target)
                return pos;
            else if (array[pos] < target)
                left = pos + 1;
            else
                right = pos - 1;
        }
        
        return -1;
    }
    
    private static void Swap<T>(T[] array, int i, int j)
    {
        T temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
    
    void RunSortingPerformanceTests()
    {
        Debug.Log("Running sorting performance tests...");
        
        // Generate test data
        int[] testArray = GenerateRandomArray(testArraySize);
        
        // Test Quick Sort
        int[] quickSortArray = (int[])testArray.Clone();
        float startTime = Time.realtimeSinceStartup;
        QuickSort(quickSortArray, 0, quickSortArray.Length - 1);
        float quickSortTime = Time.realtimeSinceStartup - startTime;
        
        // Test Heap Sort
        int[] heapSortArray = (int[])testArray.Clone();
        startTime = Time.realtimeSinceStartup;
        HeapSort(heapSortArray);
        float heapSortTime = Time.realtimeSinceStartup - startTime;
        
        // Test Radix Sort
        int[] radixSortArray = (int[])testArray.Clone();
        startTime = Time.realtimeSinceStartup;
        RadixSort(radixSortArray);
        float radixSortTime = Time.realtimeSinceStartup - startTime;
        
        Debug.Log($"Quick Sort: {quickSortTime:F4}s");
        Debug.Log($"Heap Sort: {heapSortTime:F4}s");
        Debug.Log($"Radix Sort: {radixSortTime:F4}s");
    }
    
    int[] GenerateRandomArray(int size)
    {
        int[] array = new int[size];
        for (int i = 0; i < size; i++)
        {
            array[i] = Random.Range(0, size);
        }
        return array;
    }
}

// Example usage for game-specific data
[System.Serializable]
public class EnemyData : IComparable<EnemyData>
{
    public int id;
    public float health;
    public float distanceToPlayer;
    public int priority;
    
    // Sort by priority first, then by distance
    public int CompareTo(EnemyData other)
    {
        int priorityComparison = other.priority.CompareTo(priority); // Higher priority first
        if (priorityComparison != 0) return priorityComparison;
        
        return distanceToPlayer.CompareTo(other.distanceToPlayer); // Closer enemies first
    }
}

public class EnemyManager : MonoBehaviour
{
    [SerializeField] private EnemyData[] enemies;
    
    void Update()
    {
        // Sort enemies by priority and distance for AI processing
        if (enemies != null && enemies.Length > 0)
        {
            GameSortingAlgorithms.QuickSort(enemies, 0, enemies.Length - 1);
            ProcessEnemiesInOrder();
        }
    }
    
    void ProcessEnemiesInOrder()
    {
        // Process high-priority, close enemies first
        for (int i = 0; i < Mathf.Min(5, enemies.Length); i++)
        {
            ProcessEnemy(enemies[i]);
        }
    }
    
    void ProcessEnemy(EnemyData enemy)
    {
        // Process enemy AI, attacks, etc.
    }
}
```

### Performance Optimization Techniques

**Memory and CPU Optimization:**
```csharp
public class PerformanceOptimizer : MonoBehaviour
{
    [Header("Optimization Settings")]
    [SerializeField] private bool enableProfiling = true;
    [SerializeField] private int targetFrameRate = 60;
    [SerializeField] private float gcCollectionThreshold = 50f; // MB
    
    // Object pooling system
    public class ObjectPool<T> where T : Component
    {
        private readonly Stack<T> pool = new Stack<T>();
        private readonly T prefab;
        private readonly Transform parent;
        private readonly int initialSize;
        
        public ObjectPool(T prefab, Transform parent = null, int initialSize = 10)
        {
            this.prefab = prefab;
            this.parent = parent;
            this.initialSize = initialSize;
            
            InitializePool();
        }
        
        void InitializePool()
        {
            for (int i = 0; i < initialSize; i++)
            {
                T obj = Object.Instantiate(prefab, parent);
                obj.gameObject.SetActive(false);
                pool.Push(obj);
            }
        }
        
        public T Get()
        {
            if (pool.Count > 0)
            {
                T obj = pool.Pop();
                obj.gameObject.SetActive(true);
                return obj;
            }
            
            // Create new if pool is empty
            return Object.Instantiate(prefab, parent);
        }
        
        public void Return(T obj)
        {
            obj.gameObject.SetActive(false);
            pool.Push(obj);
        }
        
        public int AvailableCount => pool.Count;
    }
    
    // Spatial optimization using octree
    public class Octree<T> where T : class
    {
        private readonly Vector3 center;
        private readonly Vector3 size;
        private readonly int maxDepth;
        private readonly int maxObjects;
        
        private List<OctreeObject<T>> objects = new List<OctreeObject<T>>();
        private Octree<T>[] children;
        private int currentDepth;
        
        public Octree(Vector3 center, Vector3 size, int maxDepth = 5, int maxObjects = 10, int depth = 0)
        {
            this.center = center;
            this.size = size;
            this.maxDepth = maxDepth;
            this.maxObjects = maxObjects;
            this.currentDepth = depth;
        }
        
        public void Insert(T obj, Bounds bounds)
        {
            if (!ContainsBounds(bounds)) return;
            
            if (objects.Count < maxObjects || currentDepth >= maxDepth)
            {
                objects.Add(new OctreeObject<T>(obj, bounds));
                return;
            }
            
            if (children == null) Subdivide();
            
            foreach (var child in children)
            {
                child.Insert(obj, bounds);
            }
        }
        
        public List<T> QueryRange(Bounds range)
        {
            List<T> result = new List<T>();
            QueryRange(range, result);
            return result;
        }
        
        private void QueryRange(Bounds range, List<T> result)
        {
            if (!range.Intersects(GetBounds())) return;
            
            foreach (var obj in objects)
            {
                if (range.Intersects(obj.bounds))
                {
                    result.Add(obj.data);
                }
            }
            
            if (children != null)
            {
                foreach (var child in children)
                {
                    child.QueryRange(range, result);
                }
            }
        }
        
        private void Subdivide()
        {
            children = new Octree<T>[8];
            Vector3 halfSize = size * 0.5f;
            
            children[0] = new Octree<T>(center + new Vector3(-halfSize.x, halfSize.y, -halfSize.z), halfSize, maxDepth, maxObjects, currentDepth + 1);
            children[1] = new Octree<T>(center + new Vector3(halfSize.x, halfSize.y, -halfSize.z), halfSize, maxDepth, maxObjects, currentDepth + 1);
            children[2] = new Octree<T>(center + new Vector3(-halfSize.x, halfSize.y, halfSize.z), halfSize, maxDepth, maxObjects, currentDepth + 1);
            children[3] = new Octree<T>(center + new Vector3(halfSize.x, halfSize.y, halfSize.z), halfSize, maxDepth, maxObjects, currentDepth + 1);
            children[4] = new Octree<T>(center + new Vector3(-halfSize.x, -halfSize.y, -halfSize.z), halfSize, maxDepth, maxObjects, currentDepth + 1);
            children[5] = new Octree<T>(center + new Vector3(halfSize.x, -halfSize.y, -halfSize.z), halfSize, maxDepth, maxObjects, currentDepth + 1);
            children[6] = new Octree<T>(center + new Vector3(-halfSize.x, -halfSize.y, halfSize.z), halfSize, maxDepth, maxObjects, currentDepth + 1);
            children[7] = new Octree<T>(center + new Vector3(halfSize.x, -halfSize.y, halfSize.z), halfSize, maxDepth, maxObjects, currentDepth + 1);
        }
        
        private bool ContainsBounds(Bounds bounds)
        {
            return GetBounds().Contains(bounds.min) && GetBounds().Contains(bounds.max);
        }
        
        private Bounds GetBounds()
        {
            return new Bounds(center, size);
        }
    }
    
    private class OctreeObject<T>
    {
        public T data;
        public Bounds bounds;
        
        public OctreeObject(T data, Bounds bounds)
        {
            this.data = data;
            this.bounds = bounds;
        }
    }
    
    // Performance monitoring
    private class PerformanceMonitor
    {
        private readonly Queue<float> frameTimes = new Queue<float>();
        private readonly int maxSamples = 60;
        private float totalMemoryUsage;
        
        public float AverageFrameTime { get; private set; }
        public float AverageFPS { get; private set; }
        public float MemoryUsageMB { get; private set; }
        
        public void Update()
        {
            // Track frame time
            frameTimes.Enqueue(Time.unscaledDeltaTime);
            if (frameTimes.Count > maxSamples)
            {
                frameTimes.Dequeue();
            }
            
            // Calculate averages
            AverageFrameTime = frameTimes.Average();
            AverageFPS = 1f / AverageFrameTime;
            
            // Track memory usage
            MemoryUsageMB = (System.GC.GetTotalMemory(false) / 1024f / 1024f);
        }
        
        public bool ShouldForceGC(float threshold)
        {
            return MemoryUsageMB > threshold;
        }
    }
    
    private PerformanceMonitor monitor = new PerformanceMonitor();
    
    void Start()
    {
        Application.targetFrameRate = targetFrameRate;
        
        // Optimize Unity settings
        QualitySettings.vSyncCount = 0;
        QualitySettings.maxQueuedFrames = 2;
        
        // Optimize garbage collection
        System.GC.Collect();
        System.GC.WaitForPendingFinalizers();
    }
    
    void Update()
    {
        if (enableProfiling)
        {
            monitor.Update();
            
            // Force garbage collection if memory usage is high
            if (monitor.ShouldForceGC(gcCollectionThreshold))
            {
                ForceGarbageCollection();
            }
            
            // Log performance warnings
            if (monitor.AverageFPS < targetFrameRate * 0.8f)
            {
                Debug.LogWarning($"Performance warning: FPS dropped to {monitor.AverageFPS:F1}");
            }
        }
    }
    
    void ForceGarbageCollection()
    {
        System.GC.Collect();
        System.GC.WaitForPendingFinalizers();
        System.GC.Collect();
        
        Debug.Log($"Forced GC: Memory usage reduced to {monitor.MemoryUsageMB:F1} MB");
    }
    
    // Algorithm optimization examples
    
    // Cache-friendly data access patterns
    public void ProcessArrayCacheFriendly<T>(T[] array, System.Action<T> processor)
    {
        // Process array in chunks that fit in CPU cache
        const int cacheLineSize = 64; // bytes
        int elementsPerCacheLine = cacheLineSize / System.Runtime.InteropServices.Marshal.SizeOf<T>();
        
        for (int i = 0; i < array.Length; i += elementsPerCacheLine)
        {
            int end = Mathf.Min(i + elementsPerCacheLine, array.Length);
            for (int j = i; j < end; j++)
            {
                processor(array[j]);
            }
        }
    }
    
    // Bit manipulation for faster operations
    public static bool IsPowerOfTwo(int value)
    {
        return value > 0 && (value & (value - 1)) == 0;
    }
    
    public static int NextPowerOfTwo(int value)
    {
        value--;
        value |= value >> 1;
        value |= value >> 2;
        value |= value >> 4;
        value |= value >> 8;
        value |= value >> 16;
        return value + 1;
    }
    
    public static int FastModulo(int value, int powerOfTwoMod)
    {
        return value & (powerOfTwoMod - 1);
    }
    
    // SIMD-style operations using Unity's mathematics package
    public void OptimizedVectorOperations(Vector3[] positions, Vector3[] velocities, float deltaTime)
    {
        // Process multiple vectors simultaneously
        for (int i = 0; i < positions.Length - 3; i += 4)
        {
            // Update 4 positions at once
            positions[i] += velocities[i] * deltaTime;
            positions[i + 1] += velocities[i + 1] * deltaTime;
            positions[i + 2] += velocities[i + 2] * deltaTime;
            positions[i + 3] += velocities[i + 3] * deltaTime;
        }
        
        // Handle remaining elements
        for (int i = (positions.Length / 4) * 4; i < positions.Length; i++)
        {
            positions[i] += velocities[i] * deltaTime;
        }
    }
    
    void OnGUI()
    {
        if (!enableProfiling) return;
        
        GUILayout.BeginArea(new Rect(10, 10, 300, 200));
        GUILayout.Label($"FPS: {monitor.AverageFPS:F1}");
        GUILayout.Label($"Frame Time: {monitor.AverageFrameTime * 1000:F1}ms");
        GUILayout.Label($"Memory: {monitor.MemoryUsageMB:F1} MB");
        GUILayout.EndArea();
    }
}
```

## Practical Applications

### Game-Specific Algorithm Usage

**Real-time Strategy Game Optimization:**
```csharp
public class RTSOptimization : MonoBehaviour
{
    [Header("RTS Settings")]
    [SerializeField] private int maxUnitsToProcess = 100;
    [SerializeField] private float updateInterval = 0.1f;
    
    private List<Unit> allUnits = new List<Unit>();
    private PriorityQueue<Unit> unitUpdateQueue = new PriorityQueue<Unit>();
    private float lastUpdateTime;
    
    void Update()
    {
        if (Time.time - lastUpdateTime >= updateInterval)
        {
            ProcessUnitUpdates();
            lastUpdateTime = Time.time;
        }
    }
    
    void ProcessUnitUpdates()
    {
        // Sort units by priority (distance to camera, importance, etc.)
        SortUnitsByPriority();
        
        // Process only the most important units each frame
        int unitsProcessed = 0;
        while (unitUpdateQueue.Count > 0 && unitsProcessed < maxUnitsToProcess)
        {
            Unit unit = unitUpdateQueue.Dequeue();
            unit.UpdateAI();
            unitsProcessed++;
        }
    }
    
    void SortUnitsByPriority()
    {
        unitUpdateQueue.Clear();
        
        foreach (Unit unit in allUnits)
        {
            // Calculate priority based on various factors
            float priority = CalculateUnitPriority(unit);
            unit.Priority = priority;
            unitUpdateQueue.Enqueue(unit);
        }
    }
    
    float CalculateUnitPriority(Unit unit)
    {
        float distanceToCamera = Vector3.Distance(unit.transform.position, Camera.main.transform.position);
        float importance = unit.IsSelected ? 2f : 1f;
        float healthFactor = unit.Health < 0.3f ? 1.5f : 1f;
        
        return importance * healthFactor / (distanceToCamera + 1f);
    }
}

[System.Serializable]
public class Unit : IComparable<Unit>
{
    public Transform transform;
    public float Health { get; set; }
    public bool IsSelected { get; set; }
    public float Priority { get; set; }
    
    public void UpdateAI()
    {
        // AI update logic
    }
    
    public int CompareTo(Unit other)
    {
        return other.Priority.CompareTo(Priority); // Higher priority first
    }
}
```

## Interview Preparation

### Algorithm Questions

**Common Interview Problems:**
```csharp
// Problem: Find k closest enemies to player
public static EnemyData[] FindKClosestEnemies(EnemyData[] enemies, Vector3 playerPosition, int k)
{
    // Use min-heap to maintain k closest enemies
    var heap = new PriorityQueue<EnemyData>();
    
    foreach (var enemy in enemies)
    {
        enemy.distanceToPlayer = Vector3.Distance(enemy.transform.position, playerPosition);
        
        if (heap.Count < k)
        {
            heap.Enqueue(enemy);
        }
        else if (enemy.distanceToPlayer < heap.Peek().distanceToPlayer)
        {
            heap.Dequeue();
            heap.Enqueue(enemy);
        }
    }
    
    return heap.ToArray();
}

// Problem: Implement level-order traversal for skill tree
public static List<SkillNode> LevelOrderTraversal(SkillNode root)
{
    if (root == null) return new List<SkillNode>();
    
    List<SkillNode> result = new List<SkillNode>();
    Queue<SkillNode> queue = new Queue<SkillNode>();
    queue.Enqueue(root);
    
    while (queue.Count > 0)
    {
        SkillNode current = queue.Dequeue();
        result.Add(current);
        
        foreach (SkillNode child in current.children)
        {
            queue.Enqueue(child);
        }
    }
    
    return result;
}

// Problem: Detect cycle in quest dependency graph
public static bool HasCyclicDependency(Dictionary<string, List<string>> questDependencies)
{
    var visited = new HashSet<string>();
    var recStack = new HashSet<string>();
    
    foreach (string quest in questDependencies.Keys)
    {
        if (HasCycleUtil(quest, questDependencies, visited, recStack))
            return true;
    }
    
    return false;
}

private static bool HasCycleUtil(string quest, Dictionary<string, List<string>> dependencies, HashSet<string> visited, HashSet<string> recStack)
{
    if (recStack.Contains(quest)) return true;
    if (visited.Contains(quest)) return false;
    
    visited.Add(quest);
    recStack.Add(quest);
    
    if (dependencies.ContainsKey(quest))
    {
        foreach (string dependency in dependencies[quest])
        {
            if (HasCycleUtil(dependency, dependencies, visited, recStack))
                return true;
        }
    }
    
    recStack.Remove(quest);
    return false;
}
```

### Key Takeaways

**Algorithm Mastery:**
- Implement A* pathfinding with optimizations for game environments
- Use appropriate sorting algorithms based on data characteristics
- Apply spatial data structures (octrees, spatial hashing) for performance
- Understand time and space complexity for algorithm selection

**Optimization Expertise:**
- Profile and monitor performance continuously
- Use object pooling to reduce garbage collection
- Implement cache-friendly data access patterns
- Apply bit manipulation techniques for faster operations