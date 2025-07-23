# Data Structures & Algorithms for Game Development

## Overview
Essential data structures and algorithms optimized for game development scenarios, focusing on performance-critical operations and Unity-specific implementations.

## Key Concepts

### Game-Optimized Data Structures

**Spatial Data Structures:**
```csharp
// Quadtree for 2D spatial partitioning
public class QuadTree<T> where T : class
{
    private readonly Rectangle bounds;
    private readonly List<T> objects = new List<T>();
    private QuadTree<T>[] children;
    private const int MaxObjects = 10;
    private const int MaxLevels = 5;
    private int level;
    
    public void Insert(T obj, Vector2 position)
    {
        if (children != null)
        {
            int index = GetIndex(position);
            if (index != -1)
            {
                children[index].Insert(obj, position);
                return;
            }
        }
        
        objects.Add(obj);
        
        if (objects.Count > MaxObjects && level < MaxLevels)
        {
            if (children == null) Split();
            
            for (int i = objects.Count - 1; i >= 0; i--)
            {
                int index = GetIndex(GetPosition(objects[i]));
                if (index != -1)
                {
                    children[index].Insert(objects[i], GetPosition(objects[i]));
                    objects.RemoveAt(i);
                }
            }
        }
    }
    
    public List<T> Retrieve(Rectangle area)
    {
        List<T> result = new List<T>();
        Retrieve(result, area);
        return result;
    }
}
```

**Object Pool with Priority Queue:**
```csharp
public class PriorityObjectPool<T> where T : MonoBehaviour, IPrioritizable
{
    private readonly SortedDictionary<int, Queue<T>> pools = new SortedDictionary<int, Queue<T>>();
    private readonly T prefab;
    
    public T Get(int priority = 0)
    {
        // Try to get from exact priority pool first
        if (pools.ContainsKey(priority) && pools[priority].Count > 0)
            return pools[priority].Dequeue();
        
        // Try lower priority pools
        foreach (var kvp in pools)
        {
            if (kvp.Key <= priority && kvp.Value.Count > 0)
                return kvp.Value.Dequeue();
        }
        
        // Create new if none available
        return CreateObject(priority);
    }
    
    public void Return(T item)
    {
        int priority = item.Priority;
        if (!pools.ContainsKey(priority))
            pools[priority] = new Queue<T>();
        
        item.gameObject.SetActive(false);
        pools[priority].Enqueue(item);
    }
}
```

### Performance-Critical Algorithms

**A* Pathfinding Implementation:**
```csharp
public class AStarPathfinder
{
    private readonly Dictionary<Vector2Int, Node> nodes = new Dictionary<Vector2Int, Node>();
    private readonly PriorityQueue<Node> openSet = new PriorityQueue<Node>();
    private readonly HashSet<Vector2Int> closedSet = new HashSet<Vector2Int>();
    
    public List<Vector2Int> FindPath(Vector2Int start, Vector2Int goal, Func<Vector2Int, bool> isWalkable)
    {
        Clear();
        
        var startNode = GetNode(start);
        startNode.GCost = 0;
        startNode.HCost = GetHeuristic(start, goal);
        openSet.Enqueue(startNode);
        
        while (openSet.Count > 0)
        {
            var current = openSet.Dequeue();
            
            if (current.Position == goal)
                return ReconstructPath(current);
            
            closedSet.Add(current.Position);
            
            foreach (var neighbor in GetNeighbors(current.Position))
            {
                if (closedSet.Contains(neighbor) || !isWalkable(neighbor))
                    continue;
                
                var neighborNode = GetNode(neighbor);
                float tentativeGCost = current.GCost + GetDistance(current.Position, neighbor);
                
                if (tentativeGCost < neighborNode.GCost)
                {
                    neighborNode.Parent = current;
                    neighborNode.GCost = tentativeGCost;
                    neighborNode.HCost = GetHeuristic(neighbor, goal);
                    
                    if (!openSet.Contains(neighborNode))
                        openSet.Enqueue(neighborNode);
                }
            }
        }
        
        return new List<Vector2Int>(); // No path found
    }
    
    private float GetHeuristic(Vector2Int a, Vector2Int b)
    {
        return Mathf.Abs(a.x - b.x) + Mathf.Abs(a.y - b.y); // Manhattan distance
    }
}
```

**Binary Search for Game Events:**
```csharp
public class TimelineEventManager
{
    private readonly List<GameEvent> events = new List<GameEvent>();
    private bool isSorted = true;
    
    public void AddEvent(GameEvent gameEvent)
    {
        events.Add(gameEvent);
        isSorted = false;
    }
    
    public List<GameEvent> GetEventsInRange(float startTime, float endTime)
    {
        if (!isSorted)
        {
            events.Sort((a, b) => a.Time.CompareTo(b.Time));
            isSorted = true;
        }
        
        int startIndex = BinarySearchFloor(startTime);
        int endIndex = BinarySearchCeiling(endTime);
        
        var result = new List<GameEvent>();
        for (int i = startIndex; i <= endIndex && i < events.Count; i++)
        {
            if (events[i].Time >= startTime && events[i].Time <= endTime)
                result.Add(events[i]);
        }
        
        return result;
    }
    
    private int BinarySearchFloor(float time)
    {
        int left = 0, right = events.Count - 1;
        int result = -1;
        
        while (left <= right)
        {
            int mid = left + (right - left) / 2;
            
            if (events[mid].Time <= time)
            {
                result = mid;
                left = mid + 1;
            }
            else
            {
                right = mid - 1;
            }
        }
        
        return Math.Max(0, result);
    }
}
```

### Collision Detection Algorithms

**Broad Phase Collision Detection:**
```csharp
public class SpatialHashGrid
{
    private readonly Dictionary<int, List<ICollidable>> grid = new Dictionary<int, List<ICollidable>>();
    private readonly float cellSize;
    
    public SpatialHashGrid(float cellSize)
    {
        this.cellSize = cellSize;
    }
    
    public void Insert(ICollidable obj)
    {
        var bounds = obj.GetBounds();
        var cells = GetCells(bounds);
        
        foreach (int cell in cells)
        {
            if (!grid.ContainsKey(cell))
                grid[cell] = new List<ICollidable>();
            
            grid[cell].Add(obj);
        }
    }
    
    public HashSet<CollisionPair> GetPotentialCollisions()
    {
        var pairs = new HashSet<CollisionPair>();
        
        foreach (var cell in grid.Values)
        {
            for (int i = 0; i < cell.Count; i++)
            {
                for (int j = i + 1; j < cell.Count; j++)
                {
                    pairs.Add(new CollisionPair(cell[i], cell[j]));
                }
            }
        }
        
        return pairs;
    }
    
    private HashSet<int> GetCells(Bounds bounds)
    {
        var cells = new HashSet<int>();
        
        int minX = Mathf.FloorToInt(bounds.min.x / cellSize);
        int maxX = Mathf.FloorToInt(bounds.max.x / cellSize);
        int minY = Mathf.FloorToInt(bounds.min.y / cellSize);
        int maxY = Mathf.FloorToInt(bounds.max.y / cellSize);
        
        for (int x = minX; x <= maxX; x++)
        {
            for (int y = minY; y <= maxY; y++)
            {
                cells.Add(GetHashCode(x, y));
            }
        }
        
        return cells;
    }
    
    private int GetHashCode(int x, int y)
    {
        return x * 73856093 ^ y * 19349663; // Hash function for 2D coordinates
    }
}
```

## Practical Applications

### Inventory and Item Management

**Dynamic Inventory System:**
```csharp
public class Inventory
{
    private readonly Dictionary<ItemType, Stack<Item>> itemStacks = new Dictionary<ItemType, Stack<Item>>();
    private readonly Dictionary<int, Item> itemsBySlot = new Dictionary<int, Item>();
    private readonly int maxSlots;
    
    public bool AddItem(Item item)
    {
        // Try to stack with existing items first
        if (itemStacks.ContainsKey(item.Type) && item.IsStackable)
        {
            var stack = itemStacks[item.Type];
            if (stack.Count > 0 && stack.Peek().CanStackWith(item))
            {
                stack.Peek().StackCount += item.StackCount;
                return true;
            }
        }
        
        // Find empty slot
        int emptySlot = FindEmptySlot();
        if (emptySlot == -1) return false;
        
        itemsBySlot[emptySlot] = item;
        
        if (!itemStacks.ContainsKey(item.Type))
            itemStacks[item.Type] = new Stack<Item>();
        
        itemStacks[item.Type].Push(item);
        return true;
    }
    
    public Item RemoveItem(int slot)
    {
        if (!itemsBySlot.ContainsKey(slot)) return null;
        
        var item = itemsBySlot[slot];
        itemsBySlot.Remove(slot);
        
        if (itemStacks.ContainsKey(item.Type))
        {
            var stack = itemStacks[item.Type];
            stack.Pop();
            if (stack.Count == 0)
                itemStacks.Remove(item.Type);
        }
        
        return item;
    }
}
```

### AI Decision Trees

**Behavior Tree Implementation:**
```csharp
public abstract class BehaviorNode
{
    public enum NodeState { Running, Success, Failure }
    
    public abstract NodeState Evaluate();
}

public class Selector : BehaviorNode
{
    private readonly List<BehaviorNode> children = new List<BehaviorNode>();
    
    public override NodeState Evaluate()
    {
        foreach (var child in children)
        {
            switch (child.Evaluate())
            {
                case NodeState.Success:
                    return NodeState.Success;
                case NodeState.Running:
                    return NodeState.Running;
                case NodeState.Failure:
                    continue;
            }
        }
        
        return NodeState.Failure;
    }
}

public class Sequence : BehaviorNode
{
    private readonly List<BehaviorNode> children = new List<BehaviorNode>();
    
    public override NodeState Evaluate()
    {
        foreach (var child in children)
        {
            switch (child.Evaluate())
            {
                case NodeState.Failure:
                    return NodeState.Failure;
                case NodeState.Running:
                    return NodeState.Running;
                case NodeState.Success:
                    continue;
            }
        }
        
        return NodeState.Success;
    }
}
```

## Interview Preparation

### Algorithm Complexity Questions

**"What's the time complexity of finding nearby objects in a game?"**
- Naive approach: O(n²) checking all pairs
- Spatial hashing: O(n) average case with proper cell sizing
- Quadtree: O(log n) for sparse distributions
- Consider memory vs time tradeoffs

**"How would you optimize collision detection for 1000+ objects?"**
- Broad phase: spatial partitioning (O(n) vs O(n²))
- Narrow phase: efficient shape-specific algorithms
- Temporal coherence: track previously colliding pairs
- Early exit conditions for distant objects

**"Explain pathfinding optimization techniques"**
- Hierarchical pathfinding for large maps
- Jump point search for uniform grids
- Flow fields for many agents to same destination
- Pre-computed navigation meshes

### Key Takeaways

**Performance-Critical Considerations:**
- Choose appropriate data structures for access patterns
- Understand time/space complexity tradeoffs
- Implement spatial partitioning for position-based queries
- Use binary search for sorted data lookups

**Game-Specific Algorithm Applications:**
- A* pathfinding with heuristic optimization
- Spatial hashing for collision broad phase
- Priority queues for event scheduling
- Behavior trees for AI decision making