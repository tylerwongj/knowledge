# @a-CSharp-Unity-Interview-Patterns - Essential C# Patterns for Unity Interviews

## 🎯 Learning Objectives
- Master essential C# patterns frequently tested in Unity interviews
- Understand when and how to apply different design patterns
- Practice implementing patterns with Unity-specific considerations
- Build confidence in technical discussions about architecture

---

## 🔧 Essential Design Patterns for Unity

### 1. Singleton Pattern
**When to use**: Game managers, audio systems, data persistence
**Unity Implementation**:
```csharp
public class GameManager : MonoBehaviour 
{
    public static GameManager Instance { get; private set; }
    
    [SerializeField] private int playerLives = 3;
    [SerializeField] private int score = 0;
    
    void Awake() 
    {
        // Ensure only one instance exists
        if (Instance == null) 
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else 
        {
            Destroy(gameObject);
        }
    }
    
    public void AddScore(int points) 
    {
        score += points;
        OnScoreChanged?.Invoke(score);
    }
    
    public event System.Action<int> OnScoreChanged;
}
```

**Interview Question**: "What are the pros and cons of the Singleton pattern?"
- **Pros**: Global access, ensures single instance, lazy initialization
- **Cons**: Tight coupling, difficult to unit test, hidden dependencies

### 2. Observer Pattern (Events)
**When to use**: UI updates, game state changes, loosely coupled communication
```csharp
// Static event system for global communication
public static class GameEvents 
{
    // Player events
    public static event System.Action<int> OnPlayerHealthChanged;
    public static event System.Action OnPlayerDied;
    public static event System.Action<Vector3> OnPlayerMoved;
    
    // Game events
    public static event System.Action<int> OnScoreChanged;
    public static event System.Action<string> OnLevelCompleted;
    
    // Trigger methods
    public static void TriggerHealthChanged(int newHealth) 
    {
        OnPlayerHealthChanged?.Invoke(newHealth);
    }
    
    public static void TriggerPlayerDied() 
    {
        OnPlayerDied?.Invoke();
    }
}

// Usage in components
public class HealthUI : MonoBehaviour 
{
    [SerializeField] private Slider healthSlider;
    
    void OnEnable() 
    {
        GameEvents.OnPlayerHealthChanged += UpdateHealthDisplay;
    }
    
    void OnDisable() 
    {
        GameEvents.OnPlayerHealthChanged -= UpdateHealthDisplay;
    }
    
    void UpdateHealthDisplay(int health) 
    {
        healthSlider.value = health / 100f;
    }
}
```

**==Critical Interview Point==**: Always unsubscribe from events in OnDisable/OnDestroy to prevent memory leaks!

### 3. Object Pool Pattern
**When to use**: Bullets, enemies, particle effects, any frequently spawned objects
```csharp
public class ObjectPool<T> where T : MonoBehaviour 
{
    private T prefab;
    private Queue<T> pool = new Queue<T>();
    private Transform parent;
    
    public ObjectPool(T prefab, int initialSize, Transform parent = null) 
    {
        this.prefab = prefab;
        this.parent = parent;
        
        // Pre-populate pool
        for (int i = 0; i < initialSize; i++) 
        {
            T obj = Object.Instantiate(prefab, parent);
            obj.gameObject.SetActive(false);
            pool.Enqueue(obj);
        }
    }
    
    public T Get() 
    {
        if (pool.Count > 0) 
        {
            T obj = pool.Dequeue();
            obj.gameObject.SetActive(true);
            return obj;
        }
        
        // Pool exhausted, create new object
        return Object.Instantiate(prefab, parent);
    }
    
    public void Return(T obj) 
    {
        obj.gameObject.SetActive(false);
        pool.Enqueue(obj);
    }
}

// Specific implementation for bullets
public class BulletPool : MonoBehaviour 
{
    [SerializeField] private Bullet bulletPrefab;
    [SerializeField] private int poolSize = 50;
    
    private ObjectPool<Bullet> bulletPool;
    
    void Start() 
    {
        bulletPool = new ObjectPool<Bullet>(bulletPrefab, poolSize, transform);
    }
    
    public void FireBullet(Vector3 position, Vector3 direction) 
    {
        Bullet bullet = bulletPool.Get();
        bullet.transform.position = position;
        bullet.Fire(direction, () => bulletPool.Return(bullet));
    }
}
```

### 4. State Machine Pattern
**When to use**: AI behavior, player states, game flow management
```csharp
// Base state interface
public interface IState 
{
    void Enter();
    void Update();
    void Exit();
}

// State machine implementation
public class StateMachine 
{
    private IState currentState;
    
    public void ChangeState(IState newState) 
    {
        currentState?.Exit();
        currentState = newState;
        currentState?.Enter();
    }
    
    public void Update() 
    {
        currentState?.Update();
    }
}

// Player state implementation
public class PlayerIdleState : IState 
{
    private PlayerController player;
    
    public PlayerIdleState(PlayerController player) 
    {
        this.player = player;
    }
    
    public void Enter() 
    {
        player.SetAnimation("Idle");
    }
    
    public void Update() 
    {
        if (Input.GetAxis("Horizontal") != 0 || Input.GetAxis("Vertical") != 0) 
        {
            player.StateMachine.ChangeState(new PlayerMovingState(player));
        }
        
        if (Input.GetKeyDown(KeyCode.Space)) 
        {
            player.StateMachine.ChangeState(new PlayerJumpingState(player));
        }
    }
    
    public void Exit() 
    {
        // Cleanup if needed
    }
}
```

### 5. Command Pattern
**When to use**: Input handling, undo systems, macro recording
```csharp
// Command interface
public interface ICommand 
{
    void Execute();
    void Undo();
}

// Concrete command implementations
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

// Command invoker
public class InputHandler : MonoBehaviour 
{
    private Stack<ICommand> commandHistory = new Stack<ICommand>();
    
    void Update() 
    {
        if (Input.GetKeyDown(KeyCode.W)) 
        {
            ICommand move = new MoveCommand(transform, Vector3.forward);
            move.Execute();
            commandHistory.Push(move);
        }
        
        if (Input.GetKeyDown(KeyCode.Z) && commandHistory.Count > 0) 
        {
            ICommand lastCommand = commandHistory.Pop();
            lastCommand.Undo();
        }
    }
}
```

---

## 🚀 Advanced C# Patterns for Senior Interviews

### 6. Factory Pattern
**When to use**: Enemy spawning, item creation, UI element generation
```csharp
// Abstract factory
public abstract class EnemyFactory 
{
    public abstract Enemy CreateEnemy();
}

// Concrete factories
public class GoblinFactory : EnemyFactory 
{
    public override Enemy CreateEnemy() 
    {
        return new Goblin();
    }
}

public class OrcFactory : EnemyFactory 
{
    public override Enemy CreateEnemy() 
    {
        return new Orc();
    }
}

// Factory manager
public class EnemySpawner : MonoBehaviour 
{
    private Dictionary<EnemyType, EnemyFactory> factories;
    
    void Start() 
    {
        factories = new Dictionary<EnemyType, EnemyFactory>
        {
            { EnemyType.Goblin, new GoblinFactory() },
            { EnemyType.Orc, new OrcFactory() }
        };
    }
    
    public Enemy SpawnEnemy(EnemyType type) 
    {
        if (factories.TryGetValue(type, out EnemyFactory factory)) 
        {
            return factory.CreateEnemy();
        }
        return null;
    }
}
```

### 7. Strategy Pattern
**When to use**: AI behaviors, weapon systems, movement types
```csharp
// Strategy interface
public interface IMovementStrategy 
{
    void Move(Transform transform, float deltaTime);
}

// Concrete strategies
public class LinearMovement : IMovementStrategy 
{
    private Vector3 direction;
    private float speed;
    
    public LinearMovement(Vector3 direction, float speed) 
    {
        this.direction = direction.normalized;
        this.speed = speed;
    }
    
    public void Move(Transform transform, float deltaTime) 
    {
        transform.position += direction * speed * deltaTime;
    }
}

public class SinusoidalMovement : IMovementStrategy 
{
    private Vector3 baseDirection;
    private float amplitude;
    private float frequency;
    private float time;
    
    public void Move(Transform transform, float deltaTime) 
    {
        time += deltaTime;
        Vector3 perpendicular = Vector3.Cross(baseDirection, Vector3.up);
        Vector3 offset = perpendicular * Mathf.Sin(time * frequency) * amplitude;
        transform.position += (baseDirection + offset) * deltaTime;
    }
}

// Context using strategy
public class MovingEnemy : MonoBehaviour 
{
    private IMovementStrategy movementStrategy;
    
    public void SetMovementStrategy(IMovementStrategy strategy) 
    {
        movementStrategy = strategy;
    }
    
    void Update() 
    {
        movementStrategy?.Move(transform, Time.deltaTime);
    }
}
```

### 8. Dependency Injection Pattern
**When to use**: Service management, testing, loose coupling
```csharp
// Service interfaces
public interface IAudioService 
{
    void PlaySound(string soundName);
    void PlayMusic(string musicName);
}

public interface IDataService 
{
    void SaveGame(GameData data);
    GameData LoadGame();
}

// Service implementations
public class UnityAudioService : IAudioService 
{
    public void PlaySound(string soundName) 
    {
        // Unity AudioSource implementation
    }
    
    public void PlayMusic(string musicName) 
    {
        // Unity music implementation
    }
}

// Service locator
public class ServiceLocator 
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
        return default(T);
    }
}

// Usage in game objects
public class Player : MonoBehaviour 
{
    private IAudioService audioService;
    private IDataService dataService;
    
    void Start() 
    {
        // Dependency injection through service locator
        audioService = ServiceLocator.GetService<IAudioService>();
        dataService = ServiceLocator.GetService<IDataService>();
    }
    
    void OnTakeDamage() 
    {
        audioService?.PlaySound("PlayerHurt");
    }
}
```

---

## 💡 Unity-Specific Pattern Considerations

### MonoBehaviour Patterns
**Proper Component Communication**
```csharp
// Instead of FindObjectOfType (slow)
public class Player : MonoBehaviour 
{
    [SerializeField] private PlayerInput inputHandler;
    [SerializeField] private PlayerMovement movement;
    [SerializeField] private PlayerHealth health;
    
    // Inject dependencies in inspector or through initialization
    void Start() 
    {
        inputHandler.Initialize(movement);
        health.Initialize(this);
    }
}
```

**Component Caching Pattern**
```csharp
public class ComponentCache : MonoBehaviour 
{
    private Rigidbody cachedRigidbody;
    private Animator cachedAnimator;
    private Collider cachedCollider;
    
    public Rigidbody Rigidbody 
    {
        get 
        {
            if (cachedRigidbody == null)
                cachedRigidbody = GetComponent<Rigidbody>();
            return cachedRigidbody;
        }
    }
    
    public Animator Animator 
    {
        get 
        {
            if (cachedAnimator == null)
                cachedAnimator = GetComponent<Animator>();
            return cachedAnimator;
        }
    }
}
```

### Performance Patterns
**Update Manager Pattern**
```csharp
public class UpdateManager : MonoBehaviour 
{
    private static UpdateManager instance;
    private List<IUpdatable> updatables = new List<IUpdatable>();
    
    void Update() 
    {
        for (int i = updatables.Count - 1; i >= 0; i--) 
        {
            if (updatables[i] != null) 
            {
                updatables[i].OnUpdate();
            }
            else 
            {
                updatables.RemoveAt(i);
            }
        }
    }
    
    public static void RegisterUpdatable(IUpdatable updatable) 
    {
        instance.updatables.Add(updatable);
    }
    
    public static void UnregisterUpdatable(IUpdatable updatable) 
    {
        instance.updatables.Remove(updatable);
    }
}

public interface IUpdatable 
{
    void OnUpdate();
}

// Instead of individual Update() methods
public class Enemy : MonoBehaviour, IUpdatable 
{
    void Start() 
    {
        UpdateManager.RegisterUpdatable(this);
    }
    
    public void OnUpdate() 
    {
        // Update logic here
    }
    
    void OnDestroy() 
    {
        UpdateManager.UnregisterUpdatable(this);
    }
}
```

---

## 🎯 Common Interview Questions and Answers

### Q: "When would you use a Singleton vs Static Class?"
**Singleton**:
- Need to implement interfaces
- Require MonoBehaviour functionality
- Need lazy initialization
- Want inheritance capabilities

**Static Class**:
- Pure utility functions
- No state management needed
- Performance-critical operations
- Mathematical calculations

### Q: "How do you prevent memory leaks with events?"
```csharp
public class SafeEventHandler : MonoBehaviour 
{
    void OnEnable() 
    {
        // Subscribe to events
        GameEvents.OnPlayerDied += HandlePlayerDeath;
    }
    
    void OnDisable() 
    {
        // ALWAYS unsubscribe to prevent memory leaks
        GameEvents.OnPlayerDied -= HandlePlayerDeath;
    }
    
    void OnDestroy() 
    {
        // Backup cleanup
        GameEvents.OnPlayerDied -= HandlePlayerDeath;
    }
}
```

### Q: "Implement a simple finite state machine"
```csharp
public enum PlayerState { Idle, Walking, Jumping, Attacking }

public class PlayerStateMachine : MonoBehaviour 
{
    [SerializeField] private PlayerState currentState = PlayerState.Idle;
    private Dictionary<PlayerState, System.Action> stateActions;
    
    void Start() 
    {
        stateActions = new Dictionary<PlayerState, System.Action>
        {
            { PlayerState.Idle, HandleIdleState },
            { PlayerState.Walking, HandleWalkingState },
            { PlayerState.Jumping, HandleJumpingState },
            { PlayerState.Attacking, HandleAttackingState }
        };
    }
    
    void Update() 
    {
        if (stateActions.TryGetValue(currentState, out System.Action stateAction)) 
        {
            stateAction.Invoke();
        }
    }
    
    public void ChangeState(PlayerState newState) 
    {
        if (currentState != newState) 
        {
            ExitState(currentState);
            currentState = newState;
            EnterState(newState);
        }
    }
}
```

---

## 🚀 AI-Enhanced Pattern Learning

### Practice with AI
**Prompt for Pattern Implementation:**
> "Generate a Unity C# implementation of the [Pattern Name] pattern for [specific use case]. Include proper error handling, Unity-specific considerations, and performance optimizations."

**Code Review with AI:**
> "Review this Unity C# code for design pattern usage. Identify potential improvements, performance issues, and suggest better patterns if applicable."

### Pattern Selection Decision Tree
```markdown
Need global access to single instance?
├─ Yes → Singleton Pattern
└─ No → Continue

Need to notify multiple objects of changes?
├─ Yes → Observer Pattern (Events)
└─ No → Continue

Frequently creating/destroying objects?
├─ Yes → Object Pool Pattern
└─ No → Continue

Need to change behavior at runtime?
├─ Yes → Strategy Pattern
└─ No → Continue

Need to track and undo actions?
├─ Yes → Command Pattern
└─ No → Continue
```

---

## 📚 Advanced Topics for Senior Roles

### ECS (Entity Component System) Patterns
```csharp
// Data-oriented design with Unity ECS
public struct MovementComponent : IComponentData 
{
    public float3 velocity;
    public float speed;
}

public struct PositionComponent : IComponentData 
{
    public float3 position;
}

[UpdateInGroup(typeof(SimulationSystemGroup))]
public class MovementSystem : SystemBase 
{
    protected override void OnUpdate() 
    {
        float deltaTime = Time.DeltaTime;
        
        Entities.ForEach((ref PositionComponent pos, in MovementComponent movement) => 
        {
            pos.position += movement.velocity * movement.speed * deltaTime;
        }).ScheduleParallel();
    }
}
```

### Generic Patterns for Reusability
```csharp
// Generic component pattern
public abstract class BaseComponent<T> : MonoBehaviour where T : BaseComponent<T> 
{
    private static List<T> allInstances = new List<T>();
    
    protected virtual void Awake() 
    {
        allInstances.Add((T)this);
    }
    
    protected virtual void OnDestroy() 
    {
        allInstances.Remove((T)this);
    }
    
    public static List<T> GetAllInstances() 
    {
        return new List<T>(allInstances);
    }
}

// Usage
public class Enemy : BaseComponent<Enemy> 
{
    // Enemy-specific implementation
}

// Get all enemies in scene
List<Enemy> allEnemies = Enemy.GetAllInstances();
```

---

> **Interview Success Strategy**: Master these patterns not just as code implementations, but understand when and why to use each one. Practice explaining the trade-offs and benefits of different approaches. Use AI tools to generate practice scenarios and validate your pattern implementations!