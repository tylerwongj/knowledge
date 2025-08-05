# @e-Algorithms-Computational-Geometry - Advanced Algorithms for Game Development

## 🎯 Learning Objectives
- Master fundamental algorithms and data structures for game development
- Implement computational geometry solutions for collision detection and spatial queries
- Develop AI-enhanced understanding of algorithmic complexity and optimization
- Create systematic approach to performance-critical game programming challenges

## 🔧 Algorithms and Computational Geometry Architecture

### The ALGO Framework for Game Development
```
A - Analysis: Understand problem complexity and performance requirements
L - Logic: Design efficient algorithms and data structures for game scenarios
G - Geometry: Apply computational geometry for spatial calculations and collision detection
O - Optimization: Implement performance optimizations and memory-efficient solutions
```

### Unity Algorithms and Computational Geometry System
```csharp
using UnityEngine;
using System.Collections.Generic;
using System.Linq;
using System;

/// <summary>
/// Comprehensive algorithms and computational geometry system for Unity
/// Provides essential algorithms, data structures, and geometric calculations
/// </summary>
public static class AlgorithmsGeometryUtility
{
    public const float EPSILON = 0.0001f;
    
    #region Sorting and Searching Algorithms
    
    /// <summary>
    /// Quick sort implementation optimized for Vector3 arrays
    /// Essential for sorting spatial data and optimization algorithms
    /// </summary>
    public static void QuickSort<T>(T[] array, Comparison<T> comparison, int left = 0, int right = -1)
    {
        if (right == -1) right = array.Length - 1;
        
        if (left < right)
        {
            int pivotIndex = Partition(array, comparison, left, right);
            QuickSort(array, comparison, left, pivotIndex - 1);
            QuickSort(array, comparison, pivotIndex + 1, right);
        }
    }
    
    private static int Partition<T>(T[] array, Comparison<T> comparison, int left, int right)
    {
        T pivot = array[right];
        int i = left - 1;
        
        for (int j = left; j < right; j++)
        {
            if (comparison(array[j], pivot) <= 0)
            {
                i++;
                Swap(array, i, j);
            }
        }
        
        Swap(array, i + 1, right);
        return i + 1;
    }
    
    private static void Swap<T>(T[] array, int i, int j)
    {
        T temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
    
    /// <summary>
    /// Binary search for sorted arrays with custom comparison
    /// Critical for fast lookups in sorted spatial data
    /// </summary>
    public static int BinarySearch<T>(T[] sortedArray, T target, Comparison<T> comparison)
    {
        int left = 0;
        int right = sortedArray.Length - 1;
        
        while (left <= right)
        {
            int mid = left + (right - left) / 2;
            int compareResult = comparison(sortedArray[mid], target);
            
            if (compareResult == 0)
                return mid;
            else if (compareResult < 0)
                left = mid + 1;
            else
                right = mid - 1;
        }
        
        return -1; // Not found
    }
    
    /// <summary>
    /// Find K nearest neighbors using heap-based approach
    /// Essential for AI proximity queries and spatial analysis
    /// </summary>
    public static List<T> FindKNearestNeighbors<T>(List<T> points, T queryPoint, int k, Func<T, T, float> distanceFunction)
    {
        var distanceHeap = new SortedList<float, T>();
        
        foreach (var point in points)
        {
            float distance = distanceFunction(queryPoint, point);
            
            if (distanceHeap.Count < k)
            {
                distanceHeap.Add(distance, point);
            }
            else if (distance < distanceHeap.Keys[distanceHeap.Count - 1])
            {
                distanceHeap.RemoveAt(distanceHeap.Count - 1);
                distanceHeap.Add(distance, point);
            }
        }
        
        return distanceHeap.Values.ToList();
    }
    
    #endregion
    
    #region Computational Geometry
    
    /// <summary>
    /// Calculate cross product for 2D vectors (z-component only)
    /// Essential for determining point orientation and polygon operations
    /// </summary>
    public static float CrossProduct2D(Vector2 a, Vector2 b)
    {
        return a.x * b.y - a.y * b.x;
    }
    
    /// <summary>
    /// Determine orientation of three points (clockwise, counterclockwise, or collinear)
    /// Critical for polygon algorithms and convex hull calculations
    /// </summary>
    public static int Orientation(Vector2 p, Vector2 q, Vector2 r)
    {
        float val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y);
        
        if (Mathf.Abs(val) < EPSILON) return 0; // Collinear
        return (val > 0) ? 1 : 2; // Clockwise or Counterclockwise
    }
    
    /// <summary>
    /// Check if point lies on line segment
    /// Essential for collision detection and path validation
    /// </summary>
    public static bool PointOnSegment(Vector2 p, Vector2 q, Vector2 r)
    {
        return q.x <= Mathf.Max(p.x, r.x) && q.x >= Mathf.Min(p.x, r.x) &&
               q.y <= Mathf.Max(p.y, r.y) && q.y >= Mathf.Min(p.y, r.y);
    }
    
    /// <summary>
    /// Check if two line segments intersect
    /// Critical for collision detection and geometric queries
    /// </summary>
    public static bool DoIntersect(Vector2 p1, Vector2 q1, Vector2 p2, Vector2 q2)
    {
        int o1 = Orientation(p1, q1, p2);
        int o2 = Orientation(p1, q1, q2);
        int o3 = Orientation(p2, q2, p1);
        int o4 = Orientation(p2, q2, q1);
        
        // General case
        if (o1 != o2 && o3 != o4)
            return true;
        
        // Special cases
        if (o1 == 0 && PointOnSegment(p1, p2, q1)) return true;
        if (o2 == 0 && PointOnSegment(p1, q2, q1)) return true;
        if (o3 == 0 && PointOnSegment(p2, p1, q2)) return true;
        if (o4 == 0 && PointOnSegment(p2, q1, q2)) return true;
        
        return false;
    }
    
    /// <summary>
    /// Calculate convex hull using Graham's scan algorithm
    /// Essential for collision optimization and shape analysis
    /// </summary>
    public static List<Vector2> ConvexHull(List<Vector2> points)
    {
        if (points.Count < 3) return new List<Vector2>();
        
        // Find bottom-most point (or left most in case of tie)
        int minY = 0;
        for (int i = 1; i < points.Count; i++)
        {
            if (points[i].y < points[minY].y || 
                (points[i].y == points[minY].y && points[i].x < points[minY].x))
            {
                minY = i;
            }
        }
        
        // Swap bottom point to first position
        Vector2 temp = points[0];
        points[0] = points[minY];
        points[minY] = temp;
        
        Vector2 pivot = points[0];
        
        // Sort points by polar angle with respect to pivot
        points.Sort(1, points.Count - 1, Comparer<Vector2>.Create((a, b) =>
        {
            int orient = Orientation(pivot, a, b);
            if (orient == 0)
            {
                // If collinear, sort by distance
                float distA = Vector2.SqrMagnitude(pivot - a);
                float distB = Vector2.SqrMagnitude(pivot - b);
                return distA.CompareTo(distB);
            }
            return (orient == 2) ? -1 : 1;
        }));
        
        // Create convex hull
        Stack<Vector2> hull = new Stack<Vector2>();
        hull.Push(points[0]);
        hull.Push(points[1]);
        
        for (int i = 2; i < points.Count; i++)
        {
            while (hull.Count > 1)
            {
                Vector2 top = hull.Pop();
                Vector2 nextToTop = hull.Peek();
                hull.Push(top);
                
                if (Orientation(nextToTop, top, points[i]) != 2)
                    hull.Pop();
                else
                    break;
            }
            hull.Push(points[i]);
        }
        
        return hull.ToList();
    }
    
    /// <summary>
    /// Check if point is inside polygon using ray casting algorithm
    /// Essential for area detection and spatial queries
    /// </summary>
    public static bool PointInPolygon(Vector2 point, Vector2[] polygon)
    {
        int intersections = 0;
        int n = polygon.Length;
        
        for (int i = 0; i < n; i++)
        {
            Vector2 p1 = polygon[i];
            Vector2 p2 = polygon[(i + 1) % n];
            
            // Check if ray intersects with edge
            if (((p1.y > point.y) != (p2.y > point.y)) &&
                (point.x < (p2.x - p1.x) * (point.y - p1.y) / (p2.y - p1.y) + p1.x))
            {
                intersections++;
            }
        }
        
        return (intersections % 2) == 1;
    }
    
    /// <summary>
    /// Calculate minimum distance from point to line segment
    /// Critical for proximity calculations and collision detection
    /// </summary>
    public static float DistancePointToSegment(Vector2 point, Vector2 segmentStart, Vector2 segmentEnd)
    {
        Vector2 segment = segmentEnd - segmentStart;
        Vector2 pointToStart = point - segmentStart;
        
        float segmentLengthSquared = segment.sqrMagnitude;
        
        if (segmentLengthSquared < EPSILON)
        {
            // Segment is a point
            return Vector2.Distance(point, segmentStart);
        }
        
        // Project point onto line
        float t = Mathf.Clamp01(Vector2.Dot(pointToStart, segment) / segmentLengthSquared);
        Vector2 projection = segmentStart + t * segment;
        
        return Vector2.Distance(point, projection);
    }
    
    #endregion
    
    #region Spatial Data Structures
    
    /// <summary>
    /// Simple spatial hash grid for fast spatial queries
    /// Essential for collision detection optimization and neighborhood searches
    /// </summary>
    public class SpatialHashGrid<T>
    {
        private Dictionary<Vector2Int, List<SpatialItem<T>>> grid;
        private float cellSize;
        private Func<T, Vector2> positionExtractor;
        
        public struct SpatialItem<TItem>
        {
            public TItem Item;
            public Vector2 Position;
            
            public SpatialItem(TItem item, Vector2 position)
            {
                Item = item;
                Position = position;
            }
        }
        
        public SpatialHashGrid(float cellSize, Func<T, Vector2> positionExtractor)
        {
            this.cellSize = cellSize;
            this.positionExtractor = positionExtractor;
            this.grid = new Dictionary<Vector2Int, List<SpatialItem<T>>>();
        }
        
        public void Clear()
        {
            grid.Clear();
        }
        
        public void AddItem(T item)
        {
            Vector2 position = positionExtractor(item);
            Vector2Int cellKey = GetCellKey(position);
            
            if (!grid.ContainsKey(cellKey))
            {
                grid[cellKey] = new List<SpatialItem<T>>();
            }
            
            grid[cellKey].Add(new SpatialItem<T>(item, position));
        }
        
        public List<T> QueryRadius(Vector2 center, float radius)
        {
            List<T> results = new List<T>();
            float radiusSquared = radius * radius;
            
            // Calculate cell range to check
            int cellRadius = Mathf.CeilToInt(radius / cellSize);
            Vector2Int centerCell = GetCellKey(center);
            
            for (int x = -cellRadius; x <= cellRadius; x++)
            {
                for (int y = -cellRadius; y <= cellRadius; y++)
                {
                    Vector2Int cellKey = centerCell + new Vector2Int(x, y);
                    
                    if (grid.ContainsKey(cellKey))
                    {
                        foreach (var spatialItem in grid[cellKey])
                        {
                            float distanceSquared = Vector2.SqrMagnitude(spatialItem.Position - center);
                            if (distanceSquared <= radiusSquared)
                            {
                                results.Add(spatialItem.Item);
                            }
                        }
                    }
                }
            }
            
            return results;
        }
        
        private Vector2Int GetCellKey(Vector2 position)
        {
            return new Vector2Int(
                Mathf.FloorToInt(position.x / cellSize),
                Mathf.FloorToInt(position.y / cellSize)
            );
        }
    }
    
    #endregion
    
    #region Path Finding Algorithms
    
    /// <summary>
    /// A* pathfinding algorithm implementation
    /// Essential for AI navigation and optimal path calculation
    /// </summary>
    public static List<Vector2Int> AStarPathfinding(Vector2Int start, Vector2Int goal, Func<Vector2Int, bool> isWalkable, Func<Vector2Int, Vector2Int, float> heuristic)
    {
        var openSet = new SortedList<float, Vector2Int>();
        var cameFrom = new Dictionary<Vector2Int, Vector2Int>();
        var gScore = new Dictionary<Vector2Int, float>();
        var fScore = new Dictionary<Vector2Int, float>();
        
        gScore[start] = 0;
        fScore[start] = heuristic(start, goal);
        openSet.Add(fScore[start], start);
        
        while (openSet.Count > 0)
        {
            Vector2Int current = openSet.Values[0];
            openSet.RemoveAt(0);
            
            if (current == goal)
            {
                return ReconstructPath(cameFrom, current);
            }
            
            foreach (Vector2Int neighbor in GetNeighbors(current))
            {
                if (!isWalkable(neighbor))
                    continue;
                
                float tentativeGScore = gScore[current] + Vector2Int.Distance(current, neighbor);
                
                if (!gScore.ContainsKey(neighbor) || tentativeGScore < gScore[neighbor])
                {
                    cameFrom[neighbor] = current;
                    gScore[neighbor] = tentativeGScore;
                    fScore[neighbor] = gScore[neighbor] + heuristic(neighbor, goal);
                    
                    if (!openSet.ContainsValue(neighbor))
                    {
                        openSet.Add(fScore[neighbor], neighbor);
                    }
                }
            }
        }
        
        return new List<Vector2Int>(); // No path found
    }
    
    private static List<Vector2Int> ReconstructPath(Dictionary<Vector2Int, Vector2Int> cameFrom, Vector2Int current)
    {
        List<Vector2Int> path = new List<Vector2Int> { current };
        
        while (cameFrom.ContainsKey(current))
        {
            current = cameFrom[current];
            path.Insert(0, current);
        }
        
        return path;
    }
    
    private static IEnumerable<Vector2Int> GetNeighbors(Vector2Int position)
    {
        // 8-directional movement
        for (int dx = -1; dx <= 1; dx++)
        {
            for (int dy = -1; dy <= 1; dy++)
            {
                if (dx == 0 && dy == 0) continue;
                yield return position + new Vector2Int(dx, dy);
            }
        }
    }
    
    #endregion
    
    #region Graph Algorithms
    
    /// <summary>
    /// Generic graph structure for various algorithms
    /// Essential for navigation graphs and relationship modeling
    /// </summary>
    public class Graph<T>
    {
        private Dictionary<T, List<Edge<T>>> adjacencyList;
        
        public struct Edge<TNode>
        {
            public TNode To;
            public float Weight;
            
            public Edge(TNode to, float weight = 1f)
            {
                To = to;
                Weight = weight;
            }
        }
        
        public Graph()
        {
            adjacencyList = new Dictionary<T, List<Edge<T>>>();
        }
        
        public void AddNode(T node)
        {
            if (!adjacencyList.ContainsKey(node))
            {
                adjacencyList[node] = new List<Edge<T>>();
            }
        }
        
        public void AddEdge(T from, T to, float weight = 1f)
        {
            AddNode(from);
            AddNode(to);
            adjacencyList[from].Add(new Edge<T>(to, weight));
        }
        
        public List<T> GetNeighbors(T node)
        {
            if (adjacencyList.ContainsKey(node))
            {
                return adjacencyList[node].ConvertAll(edge => edge.To);
            }
            return new List<T>();
        }
        
        /// <summary>
        /// Dijkstra's shortest path algorithm
        /// Essential for finding optimal routes in weighted graphs
        /// </summary>
        public Dictionary<T, float> DijkstraShortestPath(T start)
        {
            var distances = new Dictionary<T, float>();
            var priorityQueue = new SortedList<float, T>();
            var visited = new HashSet<T>();
            
            // Initialize distances
            foreach (var node in adjacencyList.Keys)
            {
                distances[node] = float.MaxValue;
            }
            distances[start] = 0;
            priorityQueue.Add(0, start);
            
            while (priorityQueue.Count > 0)
            {
                T current = priorityQueue.Values[0];
                priorityQueue.RemoveAt(0);
                
                if (visited.Contains(current))
                    continue;
                
                visited.Add(current);
                
                if (adjacencyList.ContainsKey(current))
                {
                    foreach (var edge in adjacencyList[current])
                    {
                        if (!visited.Contains(edge.To))
                        {
                            float newDistance = distances[current] + edge.Weight;
                            if (newDistance < distances[edge.To])
                            {
                                distances[edge.To] = newDistance;
                                priorityQueue.Add(newDistance, edge.To);
                            }
                        }
                    }
                }
            }
            
            return distances;
        }
        
        /// <summary>
        /// Breadth-First Search for unweighted shortest path
        /// Essential for level-based searches and minimum step solutions
        /// </summary>
        public List<T> BreadthFirstSearch(T start, T goal)
        {
            var queue = new Queue<T>();
            var visited = new HashSet<T>();
            var parent = new Dictionary<T, T>();
            
            queue.Enqueue(start);
            visited.Add(start);
            
            while (queue.Count > 0)
            {
                T current = queue.Dequeue();
                
                if (current.Equals(goal))
                {
                    return ReconstructBFSPath(parent, start, goal);
                }
                
                foreach (T neighbor in GetNeighbors(current))
                {
                    if (!visited.Contains(neighbor))
                    {
                        visited.Add(neighbor);
                        parent[neighbor] = current;
                        queue.Enqueue(neighbor);
                    }
                }
            }
            
            return new List<T>(); // No path found
        }
        
        private List<T> ReconstructBFSPath(Dictionary<T, T> parent, T start, T goal)
        {
            List<T> path = new List<T>();
            T current = goal;
            
            while (!current.Equals(start))
            {
                path.Insert(0, current);
                current = parent[current];
            }
            path.Insert(0, start);
            
            return path;
        }
    }
    
    #endregion
}

/// <summary>
/// Practical algorithm implementations for common game development scenarios
/// Demonstrates real-world application of computational techniques
/// </summary>
public class AlgorithmExamples : MonoBehaviour
{
    [Header("Spatial Hash Grid Settings")]
    public float gridCellSize = 2f;
    public int numberOfObjects = 100;
    public float queryRadius = 3f;
    
    [Header("Pathfinding Settings")]
    public Vector2Int gridSize = new Vector2Int(20, 20);
    public Vector2Int startPos = new Vector2Int(0, 0);
    public Vector2Int goalPos = new Vector2Int(19, 19);
    public float obstaclePercentage = 0.3f;
    
    [Header("Collision Detection")]
    public Transform[] movingObjects;
    public LayerMask collisionLayers;
    
    private AlgorithmsGeometryUtility.SpatialHashGrid<Transform> spatialGrid;
    private bool[,] walkableGrid;
    private List<Vector2Int> currentPath;
    private List<Transform> nearbyObjects;
    
    void Start()
    {
        InitializeSpatialGrid();
        InitializePathfindingGrid();
        nearbyObjects = new List<Transform>();
    }
    
    void Update()
    {
        // Example 1: Spatial hash grid for efficient collision detection
        UpdateSpatialQueries();
        
        // Example 2: Dynamic pathfinding
        if (Input.GetKeyDown(KeyCode.P))
        {
            RecalculatePath();
        }
        
        // Example 3: Collision detection optimization
        UpdateCollisionDetection();
    }
    
    #region Spatial Hash Grid Example
    
    /// <summary>
    /// Example: Spatial hash grid for efficient proximity queries
    /// Demonstrates O(1) spatial lookups instead of O(n) brute force
    /// </summary>
    void InitializeSpatialGrid()
    {
        spatialGrid = new AlgorithmsGeometryUtility.SpatialHashGrid<Transform>(
            gridCellSize,
            transform => new Vector2(transform.position.x, transform.position.z)
        );
        
        // Populate with existing objects
        UpdateSpatialGrid();
    }
    
    void UpdateSpatialGrid()
    {
        spatialGrid.Clear();
        
        // Add all moving objects to spatial grid
        if (movingObjects != null)
        {
            foreach (Transform obj in movingObjects)
            {
                if (obj != null)
                {
                    spatialGrid.AddItem(obj);
                }
            }
        }
    }
    
    void UpdateSpatialQueries()
    {
        UpdateSpatialGrid();
        
        // Query nearby objects efficiently
        Vector2 queryPosition = new Vector2(transform.position.x, transform.position.z);
        nearbyObjects = spatialGrid.QueryRadius(queryPosition, queryRadius);
        
        // Process nearby objects (e.g., apply forces, check collisions)
        foreach (Transform nearbyObj in nearbyObjects)
        {
            if (nearbyObj != transform)
            {
                ProcessNearbyObject(nearbyObj);
            }
        }
    }
    
    void ProcessNearbyObject(Transform obj)
    {
        // Example: Apply repulsion force
        Vector3 direction = transform.position - obj.position;
        float distance = direction.magnitude;
        
        if (distance < queryRadius && distance > 0.1f)
        {
            float force = 1f / (distance * distance); // Inverse square law
            Vector3 repulsionForce = direction.normalized * force;
            
            Rigidbody rb = GetComponent<Rigidbody>();
            if (rb != null)
            {
                rb.AddForce(repulsionForce, ForceMode.Force);
            }
        }
    }
    
    #endregion
    
    #region Pathfinding Example
    
    /// <summary>
    /// Example: A* pathfinding with dynamic obstacle avoidance
    /// Demonstrates efficient navigation in dynamic environments
    /// </summary>
    void InitializePathfindingGrid()
    {
        walkableGrid = new bool[gridSize.x, gridSize.y];
        
        // Generate random obstacles
        for (int x = 0; x < gridSize.x; x++)
        {
            for (int y = 0; y < gridSize.y; y++)
            {
                walkableGrid[x, y] = UnityEngine.Random.value > obstaclePercentage;
            }
        }
        
        // Ensure start and goal are walkable
        walkableGrid[startPos.x, startPos.y] = true;
        walkableGrid[goalPos.x, goalPos.y] = true;
        
        RecalculatePath();
    }
    
    void RecalculatePath()
    {
        currentPath = AlgorithmsGeometryUtility.AStarPathfinding(
            startPos,
            goalPos,
            IsWalkable,
            ManhattanDistance
        );
        
        Debug.Log($"Path found with {currentPath.Count} nodes");
    }
    
    bool IsWalkable(Vector2Int position)
    {
        if (position.x < 0 || position.x >= gridSize.x || position.y < 0 || position.y >= gridSize.y)
            return false;
        
        return walkableGrid[position.x, position.y];
    }
    
    float ManhattanDistance(Vector2Int a, Vector2Int b)
    {
        return Mathf.Abs(a.x - b.x) + Mathf.Abs(a.y - b.y);
    }
    
    #endregion
    
    #region Collision Detection Example
    
    /// <summary>
    /// Example: Optimized collision detection using spatial partitioning
    /// Demonstrates broad-phase collision culling for performance
    /// </summary>
    void UpdateCollisionDetection()
    {
        if (movingObjects == null || movingObjects.Length < 2) return;
        
        // Broad phase: Use spatial grid to find potential collision pairs
        var potentialCollisions = new List<(Transform, Transform)>();
        
        for (int i = 0; i < movingObjects.Length; i++)
        {
            if (movingObjects[i] == null) continue;
            
            Vector2 position = new Vector2(movingObjects[i].position.x, movingObjects[i].position.z);
            var nearby = spatialGrid.QueryRadius(position, 2f); // Collision radius
            
            foreach (Transform other in nearby)
            {
                if (other != movingObjects[i] && Array.IndexOf(movingObjects, other) > i)
                {
                    potentialCollisions.Add((movingObjects[i], other));
                }
            }
        }
        
        // Narrow phase: Detailed collision detection for potential pairs
        foreach (var (objA, objB) in potentialCollisions)
        {
            if (IsColliding(objA, objB))
            {
                HandleCollision(objA, objB);
            }
        }
    }
    
    bool IsColliding(Transform objA, Transform objB)
    {
        // Simple sphere collision detection
        float collisionDistance = 1f; // Adjust based on object size
        return Vector3.Distance(objA.position, objB.position) < collisionDistance;
    }
    
    void HandleCollision(Transform objA, Transform objB)
    {
        // Example collision response
        Vector3 collisionDirection = (objA.position - objB.position).normalized;
        
        Rigidbody rbA = objA.GetComponent<Rigidbody>();
        Rigidbody rbB = objB.GetComponent<Rigidbody>();
        
        if (rbA != null)
        {
            rbA.AddForce(collisionDirection * 5f, ForceMode.Impulse);
        }
        
        if (rbB != null)
        {
            rbB.AddForce(-collisionDirection * 5f, ForceMode.Impulse);
        }
    }
    
    #endregion
    
    #region Debug Visualization
    
    /// <summary>
    /// Visualize algorithms and spatial structures in Scene view
    /// Essential for debugging and understanding algorithmic behavior
    /// </summary>
    void OnDrawGizmos()
    {
        // Draw spatial grid cells
        Gizmos.color = Color.gray;
        if (spatialGrid != null)
        {
            Vector2 center = new Vector2(transform.position.x, transform.position.z);
            int gridRadius = 5;
            
            for (int x = -gridRadius; x <= gridRadius; x++)
            {
                for (int y = -gridRadius; y <= gridRadius; y++)
                {
                    Vector3 cellCenter = new Vector3(
                        (center.x + x * gridCellSize),
                        transform.position.y,
                        (center.y + y * gridCellSize)
                    );
                    
                    Gizmos.DrawWireCube(cellCenter, new Vector3(gridCellSize, 0.1f, gridCellSize));
                }
            }
        }
        
        // Draw query radius
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(transform.position, queryRadius);
        
        // Draw nearby objects
        if (nearbyObjects != null)
        {
            Gizmos.color = Color.red;
            foreach (Transform obj in nearbyObjects)
            {
                if (obj != null && obj != transform)
                {
                    Gizmos.DrawLine(transform.position, obj.position);
                    Gizmos.DrawSphere(obj.position, 0.2f);
                }
            }
        }
        
        // Draw pathfinding grid
        if (walkableGrid != null)
        {
            Vector3 gridOffset = new Vector3(-gridSize.x * 0.5f, 0, -gridSize.y * 0.5f);
            
            for (int x = 0; x < gridSize.x; x++)
            {
                for (int y = 0; y < gridSize.y; y++)
                {
                    Vector3 cellPos = transform.position + gridOffset + new Vector3(x, 0, y);
                    
                    if (walkableGrid[x, y])
                    {
                        Gizmos.color = Color.white;
                        Gizmos.DrawCube(cellPos, Vector3.one * 0.8f);
                    }
                    else
                    {
                        Gizmos.color = Color.black;
                        Gizmos.DrawCube(cellPos, Vector3.one * 0.9f);
                    }
                }
            }
            
            // Draw path
            if (currentPath != null && currentPath.Count > 0)
            {
                Gizmos.color = Color.green;
                for (int i = 0; i < currentPath.Count - 1; i++)
                {
                    Vector3 fromPos = transform.position + gridOffset + new Vector3(currentPath[i].x, 0.5f, currentPath[i].y);
                    Vector3 toPos = transform.position + gridOffset + new Vector3(currentPath[i + 1].x, 0.5f, currentPath[i + 1].y);
                    Gizmos.DrawLine(fromPos, toPos);
                    Gizmos.DrawSphere(fromPos, 0.3f);
                }
                
                // Draw goal
                Vector3 goalPos = transform.position + gridOffset + new Vector3(currentPath[currentPath.Count - 1].x, 0.5f, currentPath[currentPath.Count - 1].y);
                Gizmos.DrawSphere(goalPos, 0.3f);
            }
        }
    }
    
    #endregion
}

/// <summary>
/// Advanced computational geometry algorithms for specialized applications
/// Includes polygon operations, Voronoi diagrams, and mesh processing
/// </summary>
public static class AdvancedComputationalGeometry
{
    #region Polygon Operations
    
    /// <summary>
    /// Sutherland-Hodgman polygon clipping algorithm
    /// Essential for viewport culling and area intersection
    /// </summary>
    public static List<Vector2> ClipPolygon(List<Vector2> polygon, List<Vector2> clipWindow)
    {
        List<Vector2> result = new List<Vector2>(polygon);
        
        for (int i = 0; i < clipWindow.Count; i++)
        {
            if (result.Count == 0) break;
            
            Vector2 clipStart = clipWindow[i];
            Vector2 clipEnd = clipWindow[(i + 1) % clipWindow.Count];
            
            result = ClipPolygonByEdge(result, clipStart, clipEnd);
        }
        
        return result;
    }
    
    private static List<Vector2> ClipPolygonByEdge(List<Vector2> polygon, Vector2 clipStart, Vector2 clipEnd)
    {
        List<Vector2> result = new List<Vector2>();
        
        if (polygon.Count == 0) return result;
        
        Vector2 previousVertex = polygon[polygon.Count - 1];
        
        foreach (Vector2 currentVertex in polygon)
        {
            bool currentInside = IsPointInsideEdge(currentVertex, clipStart, clipEnd);
            bool previousInside = IsPointInsideEdge(previousVertex, clipStart, clipEnd);
            
            if (currentInside)
            {
                if (!previousInside)
                {
                    // Entering: Add intersection point
                    Vector2 intersection = LineIntersection(previousVertex, currentVertex, clipStart, clipEnd);
                    result.Add(intersection);
                }
                result.Add(currentVertex);
            }
            else if (previousInside)
            {
                // Leaving: Add intersection point
                Vector2 intersection = LineIntersection(previousVertex, currentVertex, clipStart, clipEnd);
                result.Add(intersection);
            }
            
            previousVertex = currentVertex;
        }
        
        return result;
    }
    
    private static bool IsPointInsideEdge(Vector2 point, Vector2 edgeStart, Vector2 edgeEnd)
    {
        return AlgorithmsGeometryUtility.CrossProduct2D(edgeEnd - edgeStart, point - edgeStart) >= 0;
    }
    
    private static Vector2 LineIntersection(Vector2 p1, Vector2 p2, Vector2 p3, Vector2 p4)
    {
        float denominator = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x);
        
        if (Mathf.Abs(denominator) < AlgorithmsGeometryUtility.EPSILON)
            return Vector2.zero; // Lines are parallel
        
        float t = ((p1.x - p3.x) * (p3.y - p4.y) - (p1.y - p3.y) * (p3.x - p4.x)) / denominator;
        
        return new Vector2(
            p1.x + t * (p2.x - p1.x),
            p1.y + t * (p2.y - p1.y)
        );
    }
    
    /// <summary>
    /// Calculate polygon area using shoelace formula
    /// Essential for area-based calculations and polygon analysis
    /// </summary>
    public static float PolygonArea(Vector2[] vertices)
    {
        float area = 0f;
        int n = vertices.Length;
        
        for (int i = 0; i < n; i++)
        {
            int j = (i + 1) % n;
            area += vertices[i].x * vertices[j].y;
            area -= vertices[j].x * vertices[i].y;
        }
        
        return Mathf.Abs(area) * 0.5f;
    }
    
    /// <summary>
    /// Calculate polygon centroid
    /// Critical for center-of-mass calculations and pivot point determination
    /// </summary>
    public static Vector2 PolygonCentroid(Vector2[] vertices)
    {
        float area = PolygonArea(vertices);
        if (area < AlgorithmsGeometryUtility.EPSILON) return Vector2.zero;
        
        Vector2 centroid = Vector2.zero;
        int n = vertices.Length;
        
        for (int i = 0; i < n; i++)
        {
            int j = (i + 1) % n;
            float cross = vertices[i].x * vertices[j].y - vertices[j].x * vertices[i].y;
            centroid.x += (vertices[i].x + vertices[j].x) * cross;
            centroid.y += (vertices[i].y + vertices[j].y) * cross;
        }
        
        return centroid / (6f * area);
    }
    
    #endregion
    
    #region Voronoi Diagrams
    
    /// <summary>
    /// Simple Fortune's algorithm implementation for Voronoi diagrams
    /// Essential for procedural generation and spatial partitioning
    /// </summary>
    public static List<List<Vector2>> GenerateVoronoiDiagram(List<Vector2> sites, Rect bounds)
    {
        // Simplified Voronoi using Lloyd's relaxation
        var cells = new List<List<Vector2>>();
        
        foreach (Vector2 site in sites)
        {
            var cell = new List<Vector2>();
            
            // Create initial cell as bounding rectangle
            cell.Add(new Vector2(bounds.xMin, bounds.yMin));
            cell.Add(new Vector2(bounds.xMax, bounds.yMin));
            cell.Add(new Vector2(bounds.xMax, bounds.yMax));
            cell.Add(new Vector2(bounds.xMin, bounds.yMax));
            
            // Clip against all other sites
            foreach (Vector2 otherSite in sites)
            {
                if (otherSite == site) continue;
                
                // Create perpendicular bisector
                Vector2 midpoint = (site + otherSite) * 0.5f;
                Vector2 direction = (otherSite - site).normalized;
                Vector2 normal = new Vector2(-direction.y, direction.x);
                
                // Clip cell by this bisector
                cell = ClipPolygonByLine(cell, midpoint, normal);
            }
            
            cells.Add(cell);
        }
        
        return cells;
    }
    
    private static List<Vector2> ClipPolygonByLine(List<Vector2> polygon, Vector2 linePoint, Vector2 lineNormal)
    {
        List<Vector2> result = new List<Vector2>();
        
        if (polygon.Count == 0) return result;
        
        Vector2 previousVertex = polygon[polygon.Count - 1];
        
        foreach (Vector2 currentVertex in polygon)
        {
            bool currentInside = Vector2.Dot(currentVertex - linePoint, lineNormal) >= 0;
            bool previousInside = Vector2.Dot(previousVertex - linePoint, lineNormal) >= 0;
            
            if (currentInside)
            {
                if (!previousInside)
                {
                    // Find intersection
                    Vector2 intersection = LineLineIntersection(previousVertex, currentVertex - previousVertex, linePoint, lineNormal);
                    result.Add(intersection);
                }
                result.Add(currentVertex);
            }
            else if (previousInside)
            {
                Vector2 intersection = LineLineIntersection(previousVertex, currentVertex - previousVertex, linePoint, lineNormal);
                result.Add(intersection);
            }
            
            previousVertex = currentVertex;
        }
        
        return result;
    }
    
    private static Vector2 LineLineIntersection(Vector2 point, Vector2 direction, Vector2 linePoint, Vector2 lineNormal)
    {
        float denominator = Vector2.Dot(direction, lineNormal);
        if (Mathf.Abs(denominator) < AlgorithmsGeometryUtility.EPSILON)
            return point; // Lines are parallel
        
        float t = Vector2.Dot(linePoint - point, lineNormal) / denominator;
        return point + t * direction;
    }
    
    #endregion
}
```

## 🎯 Algorithm Complexity and Performance

### Time Complexity Analysis
```markdown
## Algorithm Complexity Reference

### Sorting Algorithms
**Quick Sort**: O(n log n) average, O(n²) worst case
**Merge Sort**: O(n log n) guaranteed, stable but uses more memory
**Heap Sort**: O(n log n) guaranteed, in-place but not stable

### Search Algorithms
**Binary Search**: O(log n) for sorted data
**Linear Search**: O(n) for unsorted data
**Hash Table Lookup**: O(1) average, O(n) worst case

### Spatial Algorithms
**Spatial Hash Grid**: O(1) insertion, O(k) query where k is result size
**KD-Tree**: O(log n) insertion, O(log n + k) query
**Brute Force Distance**: O(n²) for all pairs, O(n) for single query

### Graph Algorithms
**Dijkstra**: O((V + E) log V) with priority queue
**A***: O(b^d) where b is branching factor, d is depth
**BFS/DFS**: O(V + E) for traversal
```

### Performance Optimization Techniques
```csharp
/// <summary>
/// Performance optimization strategies for game algorithms
/// Demonstrates memory management and computational efficiency
/// </summary>
public static class AlgorithmOptimization
{
    /// <summary>
    /// Object pooling for frequent algorithm operations
    /// Reduces garbage collection overhead in performance-critical code
    /// </summary>
    public class ObjectPool<T> where T : new()
    {
        private Stack<T> pool = new Stack<T>();
        private Func<T> createFunction;
        private Action<T> resetFunction;
        
        public ObjectPool(Func<T> createFunction = null, Action<T> resetFunction = null)
        {
            this.createFunction = createFunction ?? (() => new T());
            this.resetFunction = resetFunction;
        }
        
        public T Get()
        {
            if (pool.Count > 0)
            {
                return pool.Pop();
            }
            return createFunction();
        }
        
        public void Return(T item)
        {
            resetFunction?.Invoke(item);
            pool.Push(item);
        }
    }
    
    /// <summary>
    /// Cached distance calculations for spatial algorithms
    /// Avoids expensive square root operations when possible
    /// </summary>
    private static Dictionary<(Vector2, Vector2), float> distanceCache = new Dictionary<(Vector2, Vector2), float>();
    
    public static float CachedDistance(Vector2 a, Vector2 b, bool useCache = true)
    {
        if (!useCache)
            return Vector2.Distance(a, b);
        
        var key = (a, b);
        if (distanceCache.ContainsKey(key))
            return distanceCache[key];
        
        float distance = Vector2.Distance(a, b);
        distanceCache[key] = distance;
        
        // Prevent cache from growing too large
        if (distanceCache.Count > 10000)
        {
            distanceCache.Clear();
        }
        
        return distance;
    }
    
    /// <summary>
    /// Batch processing for multiple similar operations
    /// Improves cache locality and reduces function call overhead
    /// </summary>
    public static void BatchNearestNeighborQueries(Vector2[] queryPoints, Vector2[] dataPoints, float radius, Action<int, List<int>> resultCallback)
    {
        var spatialGrid = new AlgorithmsGeometryUtility.SpatialHashGrid<int>(radius, index => dataPoints[index]);
        
        // Populate grid with all data points
        for (int i = 0; i < dataPoints.Length; i++)
        {
            spatialGrid.AddItem(i);
        }
        
        // Process all queries in batch
        for (int queryIndex = 0; queryIndex < queryPoints.Length; queryIndex++)
        {
            var nearbyIndices = spatialGrid.QueryRadius(queryPoints[queryIndex], radius);
            resultCallback(queryIndex, nearbyIndices);
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Algorithm Enhancement
- **Intelligent Pathfinding**: AI-powered navigation that learns optimal routes and adapts to player behavior
- **Dynamic Optimization**: Machine learning-based algorithm parameter tuning for performance optimization
- **Predictive Spatial Partitioning**: AI analysis of object movement patterns for optimized spatial data structures

### Computational Geometry Applications
- **Procedural Generation**: AI-assisted polygon generation and mesh optimization for level design
- **Collision Prediction**: Machine learning-based collision prediction and avoidance systems
- **Adaptive Algorithms**: AI systems that choose optimal algorithms based on data characteristics

### Performance Intelligence
- **Bottleneck Detection**: AI analysis of algorithm performance patterns and optimization recommendations
- **Memory Management**: Machine learning-based garbage collection timing and memory allocation strategies
- **Load Balancing**: AI-powered distribution of computational work across multiple frames

## 💡 Key Highlights

- **Master the ALGO Framework** for systematic approach to algorithmic problem solving in games
- **Understand Computational Complexity** and choose appropriate algorithms for performance requirements
- **Implement Spatial Data Structures** for efficient collision detection and proximity queries
- **Apply Pathfinding Algorithms** for intelligent AI navigation and optimal route calculation
- **Optimize Performance** through caching, object pooling, and batch processing techniques
- **Use Computational Geometry** for polygon operations, intersection tests, and spatial analysis
- **Focus on Practical Applications** solving real game development challenges with efficient algorithms
- **Debug and Profile** algorithmic performance using visualization and measurement tools