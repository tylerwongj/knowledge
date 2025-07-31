# @g-Design-Patterns-Unity - C# Design Patterns for Game Development

## 🎯 Learning Objectives
- Master essential design patterns for Unity game development
- Implement scalable and maintainable code architectures
- Apply SOLID principles to game programming challenges
- Create reusable systems that improve development efficiency

## 🔧 Creational Patterns in Unity

### Singleton Pattern (Use Sparingly)
```csharp
public class GameManager : MonoBehaviour
{
    private static GameManager instance;
    public static GameManager Instance
    {
        get
        {
            if (instance == null)
            {
                instance = FindObjectOfType<GameManager>();
                if (instance == null)
                {
                    GameObject go = new GameObject("GameManager");
                    instance = go.AddComponent<GameManager>();
                    DontDestroyOnLoad(go);
                }
            }
            return instance;
        }
    }
    
    private void Awake()
    {
        if (instance != null && instance != this)
        {
            Destroy(gameObject);
            return;
        }
        instance = this;
        DontDestroyOnLoad(gameObject);
    }
}

// Better alternative: ScriptableObject Singleton
[CreateAssetMenu(fileName = "GameSettings", menuName = "Game/Settings")]
public class GameSettings : ScriptableObject
{
    private static GameSettings instance;
    public static GameSettings Instance
    {
        get
        {
            if (instance == null)
                instance = Resources.Load<GameSettings>("GameSettings");
            return instance;
        }
    }
    
    [SerializeField] private float gameSpeed = 1.0f;
    [SerializeField] private int maxPlayers = 4;
    
    public float GameSpeed => gameSpeed;
    public int MaxPlayers => maxPlayers;
}
```

### Object Pool Pattern
```csharp
public class ObjectPool<T> : MonoBehaviour where T : MonoBehaviour
{
    [SerializeField] private T prefab;
    [SerializeField] private int initialPoolSize = 10;
    [SerializeField] private bool expandPool = true;
    
    private Queue<T> pool = new Queue<T>();
    private List<T> activeObjects = new List<T>();
    
    void Start()
    {
        InitializePool();
    }
    
    private void InitializePool()
    {
        for (int i = 0; i < initialPoolSize; i++)
        {
            T obj = Instantiate(prefab);
            obj.gameObject.SetActive(false);
            pool.Enqueue(obj);
        }
    }
    
    public T GetObject()
    {
        T obj;
        
        if (pool.Count > 0)
        {
            obj = pool.Dequeue();
        }
        else if (expandPool)
        {
            obj = Instantiate(prefab);
        }
        else
        {
            return null;
        }
        
        obj.gameObject.SetActive(true);
        activeObjects.Add(obj);
        return obj;
    }
    
    public void ReturnObject(T obj)
    {
        if (activeObjects.Remove(obj))
        {
            obj.gameObject.SetActive(false);
            pool.Enqueue(obj);
        }
    }
    
    public void ReturnAllObjects()
    {
        while (activeObjects.Count > 0)
        {
            ReturnObject(activeObjects[0]);
        }
    }
}

// Usage example
public class BulletPool : ObjectPool<Bullet>
{
    public static BulletPool Instance { get; private set; }
    
    void Awake()
    {
        Instance = this;
    }
}
```

### Factory Pattern
```csharp
public abstract class Enemy : MonoBehaviour
{
    public abstract void Initialize(Vector3 position, float health);
    public abstract void Attack();
}

public class Goblin : Enemy
{
    public override void Initialize(Vector3 position, float health)
    {
        transform.position = position;
        GetComponent<Health>().SetHealth(health);
    }
    
    public override void Attack()
    {
        // Goblin-specific attack behavior
    }
}

public class Dragon : Enemy
{
    public override void Initialize(Vector3 position, float health)
    {
        transform.position = position;
        GetComponent<Health>().SetHealth(health);
    }
    
    public override void Attack()
    {
        // Dragon-specific attack behavior
    }
}

public class EnemyFactory : MonoBehaviour
{
    [SerializeField] private GameObject goblinPrefab;
    [SerializeField] private GameObject dragonPrefab;
    
    public enum EnemyType
    {
        Goblin,
        Dragon
    }
    
    public Enemy CreateEnemy(EnemyType type, Vector3 position, float health)
    {
        GameObject prefab = type switch
        {
            EnemyType.Goblin => goblinPrefab,
            EnemyType.Dragon => dragonPrefab,
            _ => throw new ArgumentException($"Unknown enemy type: {type}")
        };
        
        GameObject enemyObject = Instantiate(prefab, position, Quaternion.identity);
        Enemy enemy = enemyObject.GetComponent<Enemy>();
        enemy.Initialize(position, health);
        
        return enemy;
    }
}
```

## 🔧 Behavioral Patterns

### State Machine Pattern
```csharp
public interface IState
{
    void Enter();
    void Update();
    void Exit();
}

public class StateMachine<T>
{
    private IState currentState;
    private Dictionary<T, IState> states = new Dictionary<T, IState>();
    
    public void AddState(T key, IState state)
    {
        states[key] = state;
    }
    
    public void ChangeState(T newState)
    {
        if (states.TryGetValue(newState, out IState state))
        {
            currentState?.Exit();
            currentState = state;
            currentState.Enter();
        }
    }
    
    public void Update()
    {
        currentState?.Update();
    }
}

// Player state implementation
public enum PlayerState
{
    Idle,
    Running,
    Jumping,
    Attacking
}

public class PlayerIdleState : IState
{
    private PlayerController player;
    
    public PlayerIdleState(PlayerController player)
    {
        this.player = player;
    }
    
    public void Enter()
    {
        player.Animator.SetBool("IsIdle", true);
    }
    
    public void Update()
    {
        if (Input.GetAxis("Horizontal") != 0)
        {
            player.StateMachine.ChangeState(PlayerState.Running);
        }
        else if (Input.GetButtonDown("Jump"))
        {
            player.StateMachine.ChangeState(PlayerState.Jumping);
        }
    }
    
    public void Exit()
    {
        player.Animator.SetBool("IsIdle", false);
    }
}

public class PlayerController : MonoBehaviour
{
    public StateMachine<PlayerState> StateMachine { get; private set; }
    public Animator Animator { get; private set; }
    
    void Start()
    {
        Animator = GetComponent<Animator>();
        StateMachine = new StateMachine<PlayerState>();
        
        StateMachine.AddState(PlayerState.Idle, new PlayerIdleState(this));
        StateMachine.AddState(PlayerState.Running, new PlayerRunningState(this));
        StateMachine.AddState(PlayerState.Jumping, new PlayerJumpingState(this));
        StateMachine.AddState(PlayerState.Attacking, new PlayerAttackingState(this));
        
        StateMachine.ChangeState(PlayerState.Idle);
    }
    
    void Update()
    {
        StateMachine.Update();
    }
}
```

### Observer Pattern (Event System)
```csharp
public static class EventManager
{
    private static Dictionary<Type, Delegate> eventDictionary = new Dictionary<Type, Delegate>();
    
    public static void Subscribe<T>(System.Action<T> listener) where T : struct
    {
        if (eventDictionary.TryGetValue(typeof(T), out Delegate existingDelegate))
        {
            eventDictionary[typeof(T)] = Delegate.Combine(existingDelegate, listener);
        }
        else
        {
            eventDictionary[typeof(T)] = listener;
        }
    }
    
    public static void Unsubscribe<T>(System.Action<T> listener) where T : struct
    {
        if (eventDictionary.TryGetValue(typeof(T), out Delegate existingDelegate))
        {
            eventDictionary[typeof(T)] = Delegate.Remove(existingDelegate, listener);
        }
    }
    
    public static void Publish<T>(T eventData) where T : struct
    {
        if (eventDictionary.TryGetValue(typeof(T), out Delegate existingDelegate))
        {
            ((System.Action<T>)existingDelegate)?.Invoke(eventData);
        }
    }
}

// Event structures
public struct PlayerDiedEvent
{
    public GameObject Player;
    public Vector3 DeathPosition;
}

public struct ItemCollectedEvent
{
    public GameObject Item;
    public GameObject Collector;
    public int Value;
}

// Usage examples
public class HealthSystem : MonoBehaviour
{
    void OnEnable()
    {
        EventManager.Subscribe<PlayerDiedEvent>(OnPlayerDied);
    }
    
    void OnDisable()
    {
        EventManager.Unsubscribe<PlayerDiedEvent>(OnPlayerDied);
    }
    
    private void OnPlayerDied(PlayerDiedEvent eventData)
    {
        // Handle player death (respawn, game over, etc.)
    }
    
    public void TakeDamage(float damage)
    {
        health -= damage;
        if (health <= 0)
        {
            EventManager.Publish(new PlayerDiedEvent
            {
                Player = gameObject,
                DeathPosition = transform.position
            });
        }
    }
}
```

### Command Pattern
```csharp
public interface ICommand
{
    void Execute();
    void Undo();
}

public class MoveCommand : ICommand
{
    private Transform target;
    private Vector3 displacement;
    
    public MoveCommand(Transform target, Vector3 displacement)
    {
        this.target = target;
        this.displacement = displacement;
    }
    
    public void Execute()
    {
        target.position += displacement;
    }
    
    public void Undo()
    {
        target.position -= displacement;
    }
}

public class InputHandler : MonoBehaviour
{
    private Stack<ICommand> commandHistory = new Stack<ICommand>();
    [SerializeField] private Transform player;
    [SerializeField] private float moveDistance = 1.0f;
    
    void Update()
    {
        ICommand command = null;
        
        if (Input.GetKeyDown(KeyCode.W))
            command = new MoveCommand(player, Vector3.forward * moveDistance);
        else if (Input.GetKeyDown(KeyCode.S))
            command = new MoveCommand(player, Vector3.back * moveDistance);
        else if (Input.GetKeyDown(KeyCode.A))
            command = new MoveCommand(player, Vector3.left * moveDistance);
        else if (Input.GetKeyDown(KeyCode.D))
            command = new MoveCommand(player, Vector3.right * moveDistance);
        
        if (command != null)
        {
            command.Execute();
            commandHistory.Push(command);
        }
        
        // Undo functionality
        if (Input.GetKeyDown(KeyCode.Z) && commandHistory.Count > 0)
        {
            ICommand lastCommand = commandHistory.Pop();
            lastCommand.Undo();
        }
    }
}
```

## 🔧 Structural Patterns

### Component Pattern (Unity's Core)
```csharp
// Composition over inheritance
public class Health : MonoBehaviour, IDamageable
{
    [SerializeField] private float maxHealth = 100f;
    [SerializeField] private float currentHealth;
    
    public event System.Action<float> OnHealthChanged;
    public event System.Action OnDeath;
    
    void Start()
    {
        currentHealth = maxHealth;
    }
    
    public void TakeDamage(float damage)
    {
        currentHealth = Mathf.Max(0, currentHealth - damage);
        OnHealthChanged?.Invoke(currentHealth / maxHealth);
        
        if (currentHealth <= 0)
        {
            OnDeath?.Invoke();
        }
    }
    
    public void Heal(float amount)
    {
        currentHealth = Mathf.Min(maxHealth, currentHealth + amount);
        OnHealthChanged?.Invoke(currentHealth / maxHealth);
    }
}

public interface IDamageable
{
    void TakeDamage(float damage);
}

public interface IMovable
{
    void Move(Vector3 direction);
}

public interface IAttacker
{
    void Attack(IDamageable target);
}

// Entity composition
public class Enemy : MonoBehaviour, IMovable, IAttacker
{
    private Health health;
    private NavMeshAgent agent;
    
    void Awake()
    {
        health = GetComponent<Health>();
        agent = GetComponent<NavMeshAgent>();
        
        health.OnDeath += OnDeath;
    }
    
    public void Move(Vector3 direction)
    {
        agent.SetDestination(transform.position + direction);
    }
    
    public void Attack(IDamageable target)
    {
        target.TakeDamage(10f);
    }
    
    private void OnDeath()
    {
        // Handle death logic
        Destroy(gameObject);
    }
}
```

### Adapter Pattern
```csharp
// Legacy system interface
public class LegacyAudioSystem
{
    public void PlaySoundEffect(string filename, float volume, bool loop)
    {
        // Legacy implementation
    }
}

// Modern interface we want to use
public interface IAudioManager
{
    void PlaySound(AudioClip clip, float volume = 1.0f);
    void PlayMusic(AudioClip clip, bool loop = true);
}

// Adapter to bridge the gap
public class AudioAdapter : IAudioManager
{
    private LegacyAudioSystem legacySystem;
    
    public AudioAdapter()
    {
        legacySystem = new LegacyAudioSystem();
    }
    
    public void PlaySound(AudioClip clip, float volume = 1.0f)
    {
        legacySystem.PlaySoundEffect(clip.name, volume, false);
    }
    
    public void PlayMusic(AudioClip clip, bool loop = true)
    {
        legacySystem.PlaySoundEffect(clip.name, 0.7f, loop);
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Pattern Implementation Generation
```
"Generate Unity C# implementation of [design pattern] for [specific game system]. Include proper error handling, Unity lifecycle integration, and performance considerations."

"Create modular [game system] using composition pattern with [specific components]. Include interfaces, event communication, and scalable architecture."

"Design event-driven architecture for [game feature] using Observer pattern. Include type-safe events, proper subscription management, and performance optimization."
```

### Architecture Review and Optimization
```
"Analyze Unity C# code architecture for [game system]. Identify design pattern opportunities, coupling issues, and suggest improvements for maintainability and scalability."

"Generate refactoring plan to implement [specific design pattern] in existing [game system] code. Include step-by-step migration strategy and risk mitigation."
```

## 💡 Key Highlights

**Design Pattern Benefits:**
- **Code Reusability**: Write once, use many times across different systems
- **Maintainability**: Clear structure makes debugging and updates easier
- **Scalability**: Patterns provide framework for adding new features
- **Team Communication**: Common vocabulary for discussing architecture

**Unity-Specific Considerations:**
- **MonoBehaviour Lifecycle**: Patterns must work with Unity's component system
- **Performance Impact**: Consider garbage collection and update loop efficiency
- **Serialization**: Ensure patterns work with Unity's serialization system
- **Inspector Integration**: Maintain designer-friendly workflow

**Common Pitfalls to Avoid:**
- **Singleton Overuse**: Creates tight coupling and testing difficulties
- **Pattern Overengineering**: Don't use patterns where simple solutions suffice
- **Performance Negligence**: Some patterns can impact frame rate if not optimized
- **Inflexibility**: Choose patterns that allow for future requirements changes

**Best Practices:**
- **Composition over Inheritance**: Use Unity's component system effectively
- **Interface Segregation**: Keep interfaces focused and minimal
- **Dependency Injection**: Reduce coupling between systems
- **Event-Driven Architecture**: Use events for loose coupling between systems

**Production Workflow:**
- **Pattern Documentation**: Document why specific patterns were chosen
- **Code Reviews**: Ensure patterns are implemented correctly
- **Performance Testing**: Profile pattern implementations regularly
- **Refactoring Guidelines**: Establish when and how to refactor to patterns