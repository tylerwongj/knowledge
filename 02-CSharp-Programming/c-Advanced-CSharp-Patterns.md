# Advanced C# Patterns for Game Development

## Overview
Professional-level C# design patterns, SOLID principles, and architectural patterns essential for scalable game development and software engineering roles.

## Key Concepts

### SOLID Principles in Unity

**Single Responsibility Principle:**
```csharp
// Bad - multiple responsibilities
public class Player : MonoBehaviour
{
    void Update()
    {
        HandleInput();
        MovePlayer();
        CheckCollisions();
        UpdateUI();
        PlaySounds();
    }
}

// Good - separated responsibilities
public class PlayerController : MonoBehaviour
{
    private PlayerInput input;
    private PlayerMovement movement;
    private PlayerCollision collision;
}
```

**Dependency Inversion:**
```csharp
public interface IWeapon
{
    void Fire();
    void Reload();
}

public class Player : MonoBehaviour
{
    private IWeapon currentWeapon; // Depends on abstraction
    
    public void SetWeapon(IWeapon weapon)
    {
        currentWeapon = weapon;
    }
}
```

### Design Patterns for Unity

**Command Pattern for Input:**
```csharp
public interface ICommand
{
    void Execute();
    void Undo();
}

public class MoveCommand : ICommand
{
    private PlayerController player;
    private Vector3 direction;
    private Vector3 previousPosition;
    
    public MoveCommand(PlayerController player, Vector3 direction)
    {
        this.player = player;
        this.direction = direction;
    }
    
    public void Execute()
    {
        previousPosition = player.transform.position;
        player.Move(direction);
    }
    
    public void Undo()
    {
        player.transform.position = previousPosition;
    }
}
```

**Observer Pattern with Generic Events:**
```csharp
public class EventManager<T> where T : class
{
    private static Dictionary<Type, List<System.Action<T>>> events = 
        new Dictionary<Type, List<System.Action<T>>>();
    
    public static void Subscribe<U>(System.Action<U> listener) where U : class, T
    {
        Type eventType = typeof(U);
        if (!events.ContainsKey(eventType))
            events[eventType] = new List<System.Action<T>>();
        
        events[eventType].Add(listener as System.Action<T>);
    }
    
    public static void Publish<U>(U eventData) where U : class, T
    {
        Type eventType = typeof(U);
        if (events.ContainsKey(eventType))
        {
            foreach (var listener in events[eventType])
                listener?.Invoke(eventData);
        }
    }
}
```

### Generic Programming and Constraints

**Generic Singleton Pattern:**
```csharp
public abstract class Singleton<T> : MonoBehaviour where T : MonoBehaviour
{
    private static T instance;
    public static T Instance
    {
        get
        {
            if (instance == null)
            {
                instance = FindObjectOfType<T>();
                if (instance == null)
                {
                    GameObject obj = new GameObject(typeof(T).Name);
                    instance = obj.AddComponent<T>();
                }
            }
            return instance;
        }
    }
    
    protected virtual void Awake()
    {
        if (instance == null)
        {
            instance = this as T;
            DontDestroyOnLoad(gameObject);
        }
        else if (instance != this)
        {
            Destroy(gameObject);
        }
    }
}
```

**Generic Object Pool:**
```csharp
public class ObjectPool<T> where T : Component
{
    private readonly Queue<T> objects = new Queue<T>();
    private readonly T prefab;
    private readonly Transform parent;
    
    public ObjectPool(T prefab, Transform parent = null, int initialSize = 10)
    {
        this.prefab = prefab;
        this.parent = parent;
        
        for (int i = 0; i < initialSize; i++)
        {
            CreateObject();
        }
    }
    
    public T Get()
    {
        if (objects.Count == 0)
            CreateObject();
        
        T obj = objects.Dequeue();
        obj.gameObject.SetActive(true);
        return obj;
    }
    
    public void Return(T obj)
    {
        obj.gameObject.SetActive(false);
        objects.Enqueue(obj);
    }
    
    private void CreateObject()
    {
        T obj = Object.Instantiate(prefab, parent);
        obj.gameObject.SetActive(false);
        objects.Enqueue(obj);
    }
}
```

### Asynchronous Programming Patterns

**Async State Management:**
```csharp
public class GameStateManager : MonoBehaviour
{
    private GameState currentState;
    private readonly Dictionary<Type, GameState> states = new Dictionary<Type, GameState>();
    
    public async Task<T> ChangeStateAsync<T>() where T : GameState, new()
    {
        if (currentState != null)
            await currentState.ExitAsync();
        
        if (!states.ContainsKey(typeof(T)))
            states[typeof(T)] = new T();
        
        currentState = states[typeof(T)];
        await currentState.EnterAsync();
        
        return currentState as T;
    }
}

public abstract class GameState
{
    public abstract Task EnterAsync();
    public abstract Task ExitAsync();
    public abstract void Update();
}
```

**Task-Based Asset Loading:**
```csharp
public class AssetLoader
{
    public async Task<T> LoadAssetAsync<T>(string path) where T : UnityEngine.Object
    {
        var request = Resources.LoadAsync<T>(path);
        
        while (!request.isDone)
        {
            await Task.Yield();
        }
        
        return request.asset as T;
    }
    
    public async Task<T[]> LoadAssetsAsync<T>(params string[] paths) where T : UnityEngine.Object
    {
        var tasks = paths.Select(LoadAssetAsync<T>).ToArray();
        return await Task.WhenAll(tasks);
    }
}
```

## Practical Applications

### Modular Architecture

**Plugin System Architecture:**
```csharp
public interface IGameModule
{
    string ModuleName { get; }
    void Initialize();
    void Update();
    void Shutdown();
}

public class ModuleManager : Singleton<ModuleManager>
{
    private readonly List<IGameModule> modules = new List<IGameModule>();
    
    public void RegisterModule<T>() where T : IGameModule, new()
    {
        var module = new T();
        modules.Add(module);
        module.Initialize();
    }
    
    void Update()
    {
        foreach (var module in modules)
            module.Update();
    }
    
    void OnDestroy()
    {
        foreach (var module in modules)
            module.Shutdown();
    }
}
```

**Dependency Injection Container:**
```csharp
public class ServiceContainer
{
    private readonly Dictionary<Type, object> services = new Dictionary<Type, object>();
    private readonly Dictionary<Type, Func<object>> factories = new Dictionary<Type, Func<object>>();
    
    public void Register<T>(T instance)
    {
        services[typeof(T)] = instance;
    }
    
    public void Register<T>(Func<T> factory)
    {
        factories[typeof(T)] = () => factory();
    }
    
    public T Resolve<T>()
    {
        Type type = typeof(T);
        
        if (services.ContainsKey(type))
            return (T)services[type];
        
        if (factories.ContainsKey(type))
        {
            var instance = (T)factories[type]();
            services[type] = instance; // Cache for singleton behavior
            return instance;
        }
        
        throw new InvalidOperationException($"Service {type.Name} not registered");
    }
}
```

### Performance Optimization Patterns

**Flyweight Pattern for Game Objects:**
```csharp
public class EnemyType
{
    public string Name { get; set; }
    public Sprite Sprite { get; set; }
    public float Speed { get; set; }
    public int Health { get; set; }
    
    // Intrinsic data shared among all enemies of this type
}

public class Enemy : MonoBehaviour
{
    private EnemyType enemyType; // Reference to shared data
    private Vector3 position;    // Extrinsic data unique to this instance
    private float currentHealth; // Extrinsic data unique to this instance
    
    public void Initialize(EnemyType type, Vector3 startPosition)
    {
        enemyType = type;
        position = startPosition;
        currentHealth = type.Health;
    }
}
```

## Interview Preparation

### Advanced Technical Questions

**"How would you implement a save system using design patterns?"**
- Command pattern for undoable actions
- Memento pattern for state snapshots
- Strategy pattern for different save formats
- Observer pattern for save state notifications

**"Explain how you'd architect a multiplayer game system"**
- Command pattern for networked actions
- State pattern for connection states
- Observer pattern for network events
- Factory pattern for message creation

**"How do you handle memory management in complex game systems?"**
- Object pooling for frequently allocated objects
- Weak references for observer patterns
- Dispose pattern for unmanaged resources
- Lazy initialization for expensive objects

### Key Takeaways

**Professional Architecture Patterns:**
- Apply SOLID principles to Unity development
- Use dependency injection for testable, modular code
- Implement proper separation of concerns
- Design for extensibility and maintainability

**Performance and Scalability:**
- Use appropriate design patterns for performance
- Implement efficient async patterns for I/O operations
- Design systems that scale with game complexity
- Balance flexibility with performance requirements