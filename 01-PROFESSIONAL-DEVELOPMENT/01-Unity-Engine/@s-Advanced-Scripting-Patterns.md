# @s-Advanced-Scripting-Patterns - Unity Architecture & Design Patterns

## 🎯 Learning Objectives

- Master advanced Unity scripting patterns for scalable architecture
- Implement design patterns optimized for Unity development
- Create maintainable and extensible game systems
- Optimize code organization for team collaboration and performance

## 🔧 Core Design Patterns in Unity

### Singleton Pattern (Unity-Specific)
```csharp
public class GameManager : MonoBehaviour
{
    private static GameManager _instance;
    public static GameManager Instance
    {
        get
        {
            if (_instance == null)
            {
                _instance = FindObjectOfType<GameManager>();
                
                if (_instance == null)
                {
                    GameObject go = new GameObject("GameManager");
                    _instance = go.AddComponent<GameManager>();
                    DontDestroyOnLoad(go);
                }
            }
            return _instance;
        }
    }
    
    void Awake()
    {
        if (_instance == null)
        {
            _instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else if (_instance != this)
        {
            Destroy(gameObject);
        }
    }
}
```

### Observer Pattern with Unity Events
```csharp
using UnityEngine;
using UnityEngine.Events;

[System.Serializable]
public class PlayerHealthEvent : UnityEvent<float> { }

public class PlayerHealth : MonoBehaviour
{
    [SerializeField] private float maxHealth = 100f;
    [SerializeField] private float currentHealth;
    
    [Header("Events")]
    public PlayerHealthEvent OnHealthChanged = new PlayerHealthEvent();
    public UnityEvent OnPlayerDied = new UnityEvent();
    
    void Start()
    {
        currentHealth = maxHealth;
    }
    
    public void TakeDamage(float damage)
    {
        currentHealth = Mathf.Max(0, currentHealth - damage);
        OnHealthChanged.Invoke(currentHealth / maxHealth);
        
        if (currentHealth <= 0)
        {
            OnPlayerDied.Invoke();
        }
    }
}

// UI Component subscribing to health events
public class HealthUI : MonoBehaviour
{
    [SerializeField] private Slider healthSlider;
    [SerializeField] private PlayerHealth playerHealth;
    
    void Start()
    {
        playerHealth.OnHealthChanged.AddListener(UpdateHealthUI);
        playerHealth.OnPlayerDied.AddListener(ShowGameOverScreen);
    }
    
    void UpdateHealthUI(float healthPercentage)
    {
        healthSlider.value = healthPercentage;
    }
    
    void ShowGameOverScreen()
    {
        // Handle game over UI
    }
}
```

### Command Pattern for Input & Undo System
```csharp
public interface ICommand
{
    void Execute();
    void Undo();
}

public class MoveCommand : ICommand
{
    private Transform target;
    private Vector3 direction;
    private Vector3 previousPosition;
    
    public MoveCommand(Transform target, Vector3 direction)
    {
        this.target = target;
        this.direction = direction;
    }
    
    public void Execute()
    {
        previousPosition = target.position;
        target.position += direction;
    }
    
    public void Undo()
    {
        target.position = previousPosition;
    }
}

public class CommandManager : MonoBehaviour
{
    private Stack<ICommand> commandHistory = new Stack<ICommand>();
    private Stack<ICommand> undoHistory = new Stack<ICommand>();
    
    public void ExecuteCommand(ICommand command)
    {
        command.Execute();
        commandHistory.Push(command);
        undoHistory.Clear(); // Clear redo history when new command is executed
    }
    
    public void UndoLastCommand()
    {
        if (commandHistory.Count > 0)
        {
            var command = commandHistory.Pop();
            command.Undo();
            undoHistory.Push(command);
        }
    }
    
    public void RedoLastCommand()
    {
        if (undoHistory.Count > 0)
        {
            var command = undoHistory.Pop();
            command.Execute();
            commandHistory.Push(command);
        }
    }
}
```

## 🎮 State Machine Pattern

### Advanced State Machine Implementation
```csharp
public abstract class State
{
    public abstract void Enter();
    public abstract void Update();
    public abstract void Exit();
}

public class StateMachine
{
    private State currentState;
    private Dictionary<System.Type, State> states = new Dictionary<System.Type, State>();
    
    public void AddState<T>(T state) where T : State
    {
        states[typeof(T)] = state;
    }
    
    public void ChangeState<T>() where T : State
    {
        if (states.TryGetValue(typeof(T), out State newState))
        {
            currentState?.Exit();
            currentState = newState;
            currentState.Enter();
        }
    }
    
    public void Update()
    {
        currentState?.Update();
    }
}

// Example: Enemy AI States
public class IdleState : State
{
    private EnemyController enemy;
    
    public IdleState(EnemyController enemy)
    {
        this.enemy = enemy;
    }
    
    public override void Enter()
    {
        enemy.SetAnimation("Idle");
    }
    
    public override void Update()
    {
        if (enemy.PlayerInRange())
        {
            enemy.StateMachine.ChangeState<ChaseState>();
        }
    }
    
    public override void Exit()
    {
        // Cleanup idle state
    }
}

public class EnemyController : MonoBehaviour
{
    public StateMachine StateMachine { get; private set; }
    
    void Start()
    {
        StateMachine = new StateMachine();
        StateMachine.AddState(new IdleState(this));
        StateMachine.AddState(new ChaseState(this));
        StateMachine.AddState(new AttackState(this));
        
        StateMachine.ChangeState<IdleState>();
    }
    
    void Update()
    {
        StateMachine.Update();
    }
}
```

## 🏗️ Object Pooling Pattern

### Generic Object Pool
```csharp
using System.Collections.Generic;
using UnityEngine;

public class ObjectPool<T> where T : Component
{
    private Queue<T> objects = new Queue<T>();
    private T prefab;
    private Transform parent;
    
    public ObjectPool(T prefab, int initialSize = 10, Transform parent = null)
    {
        this.prefab = prefab;
        this.parent = parent;
        
        for (int i = 0; i < initialSize; i++)
        {
            T obj = Object.Instantiate(prefab, parent);
            obj.gameObject.SetActive(false);
            objects.Enqueue(obj);
        }
    }
    
    public T Get()
    {
        if (objects.Count > 0)
        {
            T obj = objects.Dequeue();
            obj.gameObject.SetActive(true);
            return obj;
        }
        else
        {
            return Object.Instantiate(prefab, parent);
        }
    }
    
    public void Return(T obj)
    {
        obj.gameObject.SetActive(false);
        objects.Enqueue(obj);
    }
}

// Pool Manager for multiple object types
public class PoolManager : MonoBehaviour
{
    private Dictionary<string, object> pools = new Dictionary<string, object>();
    
    public void CreatePool<T>(string poolName, T prefab, int initialSize) where T : Component
    {
        pools[poolName] = new ObjectPool<T>(prefab, initialSize, transform);
    }
    
    public T GetFromPool<T>(string poolName) where T : Component
    {
        if (pools.TryGetValue(poolName, out object pool))
        {
            return ((ObjectPool<T>)pool).Get();
        }
        return null;
    }
    
    public void ReturnToPool<T>(string poolName, T obj) where T : Component
    {
        if (pools.TryGetValue(poolName, out object pool))
        {
            ((ObjectPool<T>)pool).Return(obj);
        }
    }
}
```

## 🔄 Service Locator Pattern

### Service Management System
```csharp
using System;
using System.Collections.Generic;

public static class ServiceLocator
{
    private static Dictionary<Type, object> services = new Dictionary<Type, object>();
    
    public static void RegisterService<T>(T service)
    {
        services[typeof(T)] = service;
    }
    
    public static T GetService<T>()
    {
        if (services.TryGetValue(typeof(T), out object service))
        {
            return (T)service;
        }
        
        throw new Exception($"Service of type {typeof(T)} not registered");
    }
    
    public static bool TryGetService<T>(out T service)
    {
        if (services.TryGetValue(typeof(T), out object serviceObj))
        {
            service = (T)serviceObj;
            return true;
        }
        
        service = default(T);
        return false;
    }
    
    public static void UnregisterService<T>()
    {
        services.Remove(typeof(T));
    }
}

// Example Services
public interface IAudioService
{
    void PlaySound(string soundName);
    void PlayMusic(string musicName);
}

public class AudioService : MonoBehaviour, IAudioService
{
    void Start()
    {
        ServiceLocator.RegisterService<IAudioService>(this);
    }
    
    public void PlaySound(string soundName)
    {
        // Play sound implementation
    }
    
    public void PlayMusic(string musicName)
    {
        // Play music implementation
    }
}

// Using the service
public class PlayerController : MonoBehaviour
{
    void Start()
    {
        var audioService = ServiceLocator.GetService<IAudioService>();
        audioService.PlaySound("PlayerSpawn");
    }
}
```

## 🎯 Factory Pattern

### Game Object Factory
```csharp
public abstract class GameEntity : MonoBehaviour
{
    public abstract void Initialize();
}

public class Enemy : GameEntity
{
    [SerializeField] private float health;
    [SerializeField] private float speed;
    
    public override void Initialize()
    {
        // Initialize enemy-specific behavior
    }
    
    public void SetStats(float health, float speed)
    {
        this.health = health;
        this.speed = speed;
    }
}

public static class EntityFactory
{
    private static Dictionary<string, GameObject> prefabs = new Dictionary<string, GameObject>();
    
    public static void RegisterPrefab(string name, GameObject prefab)
    {
        prefabs[name] = prefab;
    }
    
    public static T CreateEntity<T>(string prefabName, Vector3 position = default) where T : GameEntity
    {
        if (prefabs.TryGetValue(prefabName, out GameObject prefab))
        {
            GameObject instance = Object.Instantiate(prefab, position, Quaternion.identity);
            T entity = instance.GetComponent<T>();
            entity.Initialize();
            return entity;
        }
        
        throw new ArgumentException($"Prefab {prefabName} not registered");
    }
    
    public static Enemy CreateEnemy(EnemyType type, Vector3 position)
    {
        Enemy enemy = CreateEntity<Enemy>(type.ToString(), position);
        
        switch (type)
        {
            case EnemyType.Goblin:
                enemy.SetStats(50f, 3f);
                break;
            case EnemyType.Orc:
                enemy.SetStats(100f, 2f);
                break;
            case EnemyType.Dragon:
                enemy.SetStats(500f, 1f);
                break;
        }
        
        return enemy;
    }
}

public enum EnemyType
{
    Goblin,
    Orc,
    Dragon
}
```

## 🚀 AI/LLM Integration Opportunities

### Pattern Generation Automation
```csharp
// Prompt: "Generate Unity design pattern implementation for [specific use case]"
public class PatternGenerator
{
    public void GenerateStatePattern()
    {
        // AI-generated state machine for specific game mechanics
        // Automated state transition logic
        // Context-aware state implementations
    }
    
    public void GenerateObserverPattern()
    {
        // AI-generated event system for game features
        // Automated event subscription management
        // Type-safe event implementations
    }
}
```

### Architecture Analysis Tools
```csharp
// Prompt: "Analyze Unity project architecture and suggest improvements"
public class ArchitectureAnalyzer
{
    public void AnalyzeCodeStructure()
    {
        // AI-powered code analysis
        // Pattern recognition and suggestions
        // Performance optimization recommendations
    }
}
```

## 💡 Key Highlights

- **Singleton**: Use carefully, prefer dependency injection for testability
- **Observer**: Unity Events provide built-in observer pattern implementation
- **Command**: Essential for undo/redo systems and input handling
- **State Machine**: Critical for AI, game states, and complex behaviors
- **Object Pooling**: Mandatory for performance in object-heavy games
- **Service Locator**: Provides global access to services without tight coupling
- **Factory**: Centralizes object creation and configuration logic

## 🎯 Best Practices

1. **Composition over Inheritance**: Favor component-based design
2. **Interface Segregation**: Keep interfaces focused and minimal
3. **Dependency Injection**: Avoid hard dependencies between systems
4. **Event-Driven Architecture**: Use events for loose coupling
5. **Performance Considerations**: Choose patterns based on performance needs
6. **Testing**: Design patterns should support unit testing
7. **Documentation**: Document pattern usage and architectural decisions

## 📚 Advanced Pattern Resources

- Unity Architecture Patterns Guide
- Game Programming Patterns (Nystrom)
- Clean Code Architecture
- Unity Design Patterns Implementation
- Performance-Oriented Design Patterns
- Testable Unity Code Patterns