# @k-Unity-Architecture-Interview-Patterns - System Design Questions for Unity Developers

## 🎯 Learning Objectives
- Master Unity-specific system design interview questions
- Understand scalable architecture patterns for game development
- Practice component-based design discussions
- Prepare for senior Unity developer architecture challenges

## 🔧 Common Unity Architecture Interview Questions

### Question 1: Design a Modular Inventory System
```csharp
// Interviewer: "Design an inventory system that supports different item types,
// equipment slots, and can be easily extended for new features."

public interface IInventoryItem
{
    string ItemId { get; }
    string Name { get; }
    string Description { get; }
    ItemType Type { get; }
    int MaxStackSize { get; }
    bool IsStackable { get; }
}

public abstract class BaseInventoryItem : ScriptableObject, IInventoryItem
{
    [SerializeField] protected string itemId;
    [SerializeField] protected string itemName;
    [SerializeField] protected string description;
    [SerializeField] protected ItemType itemType;
    [SerializeField] protected int maxStackSize = 1;
    
    public string ItemId => itemId;
    public string Name => itemName;
    public string Description => description;
    public ItemType Type => itemType;
    public int MaxStackSize => maxStackSize;
    public bool IsStackable => maxStackSize > 1;
}

// Component-based inventory system
[System.Serializable]
public class InventorySlot
{
    public IInventoryItem Item { get; set; }
    public int Quantity { get; set; }
    public SlotType SlotType { get; set; }
    
    public bool CanAcceptItem(IInventoryItem item)
    {
        if (Item == null) return true;
        return Item.ItemId == item.ItemId && Item.IsStackable && 
               Quantity + 1 <= Item.MaxStackSize;
    }
}

public class InventoryComponent : MonoBehaviour
{
    [SerializeField] private List<InventorySlot> slots = new List<InventorySlot>();
    
    public event System.Action<IInventoryItem, int> OnItemAdded;
    public event System.Action<IInventoryItem, int> OnItemRemoved;
    
    public bool TryAddItem(IInventoryItem item, int quantity = 1)
    {
        // Implementation with event notifications
        // Consider: stacking logic, overflow handling, slot restrictions
        var availableSlot = FindAvailableSlot(item);
        if (availableSlot != null)
        {
            AddToSlot(availableSlot, item, quantity);
            OnItemAdded?.Invoke(item, quantity);
            return true;
        }
        return false;
    }
}
```

### Question 2: Design a Scalable Save System
```csharp
// Interviewer: "Design a save system that can handle different data types,
// versioning, and can work across multiple platforms."

public interface ISaveable
{
    string SaveKey { get; }
    object GetSaveData();
    void LoadSaveData(object data);
    int SaveVersion { get; }
}

public class SaveDataContainer
{
    public Dictionary<string, object> Data { get; set; } = new Dictionary<string, object>();
    public int Version { get; set; }
    public DateTime SaveTime { get; set; }
    public string GameVersion { get; set; }
}

public class SaveManager : MonoBehaviour
{
    private static SaveManager _instance;
    public static SaveManager Instance => _instance;
    
    private List<ISaveable> saveables = new List<ISaveable>();
    private ISaveDataSerializer serializer;
    private ISaveDataStorage storage;
    
    void Awake()
    {
        if (_instance == null)
        {
            _instance = this;
            DontDestroyOnLoad(gameObject);
            
            // Strategy pattern for different platforms
            serializer = new JsonSaveSerializer();
            storage = GetPlatformStorage();
        }
    }
    
    public async Task<bool> SaveGameAsync(string saveSlot = "default")
    {
        var saveData = new SaveDataContainer
        {
            Version = GetCurrentSaveVersion(),
            SaveTime = DateTime.Now,
            GameVersion = Application.version
        };
        
        // Collect data from all saveables
        foreach (var saveable in saveables)
        {
            try
            {
                saveData.Data[saveable.SaveKey] = saveable.GetSaveData();
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"Failed to save data for {saveable.SaveKey}: {ex.Message}");
            }
        }
        
        var serializedData = serializer.Serialize(saveData);
        return await storage.SaveAsync(saveSlot, serializedData);
    }
    
    private ISaveDataStorage GetPlatformStorage()
    {
        #if UNITY_STANDALONE
            return new FileSystemStorage();
        #elif UNITY_ANDROID || UNITY_IOS
            return new PlayerPrefsStorage();
        #elif UNITY_WEBGL
            return new LocalStorageWrapper();
        #else
            return new FileSystemStorage();
        #endif
    }
}
```

### Question 3: Design a Multiplayer-Ready Event System
```csharp
// Interviewer: "Design an event system that can work in both single-player
// and multiplayer contexts, with proper synchronization."

public abstract class BaseGameEvent
{
    public string EventId { get; protected set; }
    public float Timestamp { get; protected set; }
    public int SenderId { get; protected set; }
    public EventPriority Priority { get; protected set; }
    
    protected BaseGameEvent()
    {
        EventId = System.Guid.NewGuid().ToString();
        Timestamp = Time.time;
    }
    
    public abstract void Execute();
    public abstract byte[] Serialize();
    public abstract void Deserialize(byte[] data);
}

public class NetworkedEventSystem : MonoBehaviour
{
    private Queue<BaseGameEvent> eventQueue = new Queue<BaseGameEvent>();
    private Dictionary<System.Type, List<IEventHandler>> handlers = 
        new Dictionary<System.Type, List<IEventHandler>>();
    
    // Client prediction and server reconciliation
    private Dictionary<string, BaseGameEvent> pendingEvents = 
        new Dictionary<string, BaseGameEvent>();
    
    public void PublishEvent<T>(T gameEvent) where T : BaseGameEvent
    {
        if (IsMultiplayer())
        {
            // Add to pending events for client prediction
            pendingEvents[gameEvent.EventId] = gameEvent;
            
            // Send to server for authoritative processing
            SendEventToServer(gameEvent);
            
            // Execute locally for immediate feedback (client prediction)
            if (ShouldPredictLocally(gameEvent))
            {
                ExecuteEventLocally(gameEvent);
            }
        }
        else
        {
            // Single-player: execute immediately
            ExecuteEventLocally(gameEvent);
        }
    }
    
    public void OnServerEventReceived(BaseGameEvent serverEvent)
    {
        // Server reconciliation: replace predicted event with authoritative one
        if (pendingEvents.ContainsKey(serverEvent.EventId))
        {
            var predictedEvent = pendingEvents[serverEvent.EventId];
            
            // Check if prediction was correct
            if (!EventsMatch(predictedEvent, serverEvent))
            {
                // Rollback and replay with correct event
                RollbackAndReplay(serverEvent);
            }
            
            pendingEvents.Remove(serverEvent.EventId);
        }
        else
        {
            // Event from another client
            ExecuteEventLocally(serverEvent);
        }
    }
}
```

## 🎮 Performance-Oriented Architecture Questions

### Question 4: Design a Memory-Efficient Object Pool System
```csharp
// Interviewer: "Design an object pooling system that minimizes garbage collection
// and can handle different object types efficiently."

public interface IPoolable
{
    void OnReturnedToPool();
    void OnTakenFromPool();
    bool IsAvailable { get; }
}

public class GenericObjectPool<T> where T : MonoBehaviour, IPoolable
{
    private readonly Stack<T> pool = new Stack<T>();
    private readonly HashSet<T> activeObjects = new HashSet<T>();
    private readonly Transform poolParent;
    private readonly T prefab;
    private readonly int maxSize;
    
    public GenericObjectPool(T prefab, int initialSize, int maxSize, Transform parent = null)
    {
        this.prefab = prefab;
        this.maxSize = maxSize;
        this.poolParent = parent;
        
        // Pre-instantiate objects
        for (int i = 0; i < initialSize; i++)
        {
            var obj = CreateNewObject();
            ReturnToPool(obj);
        }
    }
    
    public T GetFromPool()
    {
        T obj;
        
        if (pool.Count > 0)
        {
            obj = pool.Pop();
        }
        else
        {
            obj = CreateNewObject();
        }
        
        activeObjects.Add(obj);
        obj.gameObject.SetActive(true);
        obj.OnTakenFromPool();
        
        return obj;
    }
    
    public void ReturnToPool(T obj)
    {
        if (!activeObjects.Contains(obj)) return;
        
        activeObjects.Remove(obj);
        obj.OnReturnedToPool();
        obj.gameObject.SetActive(false);
        
        if (poolParent != null)
            obj.transform.SetParent(poolParent);
        
        if (pool.Count < maxSize)
        {
            pool.Push(obj);
        }
        else
        {
            // Pool is full, destroy the object
            Object.Destroy(obj.gameObject);
        }
    }
}

// Manager for multiple pool types
public class PoolManager : MonoBehaviour
{
    private Dictionary<System.Type, object> pools = new Dictionary<System.Type, object>();
    
    public void RegisterPool<T>(T prefab, int initialSize, int maxSize) 
        where T : MonoBehaviour, IPoolable
    {
        var pool = new GenericObjectPool<T>(prefab, initialSize, maxSize, transform);
        pools[typeof(T)] = pool;
    }
    
    public T GetPooledObject<T>() where T : MonoBehaviour, IPoolable
    {
        if (pools.TryGetValue(typeof(T), out var poolObj))
        {
            var pool = (GenericObjectPool<T>)poolObj;
            return pool.GetFromPool();
        }
        
        Debug.LogError($"No pool registered for type {typeof(T)}");
        return null;
    }
}
```

## 🚀 AI/LLM Integration for Interview Prep
- **Architecture Review**: "Analyze this Unity system design for scalability issues"
- **Trade-off Analysis**: "Compare ECS vs traditional Component pattern for this use case"
- **Best Practices**: "Suggest improvements for this multiplayer architecture"
- **Performance Optimization**: "Identify bottlenecks in this Unity system design"

## 💡 Key Architecture Interview Principles
- **Scalability**: Always consider how the system grows with content and users
- **Modularity**: Design for loose coupling and high cohesion
- **Performance**: Consider memory allocation, CPU usage, and frame rate impact
- **Maintainability**: Write code that's easy to understand and modify
- **Testability**: Design systems that can be unit tested and integration tested
- **Platform Considerations**: Account for different deployment targets and constraints