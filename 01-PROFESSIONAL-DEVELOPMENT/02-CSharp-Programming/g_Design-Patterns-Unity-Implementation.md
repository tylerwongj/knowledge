# g_Design Patterns Unity Implementation - Enterprise C# Patterns for Game Development

## 🎯 Learning Objectives
- Master Gang of Four design patterns in Unity C# development
- Implement enterprise-level software architecture patterns in game projects
- Create reusable, maintainable code solutions using proven design patterns
- Apply pattern-based thinking to solve complex Unity development challenges

## 🔧 Creational Patterns

### Singleton Pattern (Unity-Safe Implementation)
```csharp
public class GameManager : MonoBehaviour
{
    private static GameManager _instance;
    private static readonly object _lock = new object();
    
    public static GameManager Instance
    {
        get
        {
            if (_instance == null)
            {
                lock (_lock)
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
                }
            }
            return _instance;
        }
    }
    
    private void Awake()
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

### Factory Pattern for GameObject Creation
```csharp
public interface IEnemy
{
    void Initialize();
    void Attack();
    void TakeDamage(int damage);
}

public class EnemyFactory : MonoBehaviour
{
    [SerializeField] private GameObject zombiePrefab;
    [SerializeField] private GameObject skeletonPrefab;
    [SerializeField] private GameObject bossPrefab;
    
    public enum EnemyType
    {
        Zombie,
        Skeleton,
        Boss
    }
    
    public IEnemy CreateEnemy(EnemyType type, Vector3 position)
    {
        GameObject prefab = GetPrefabForType(type);
        GameObject enemyObject = Instantiate(prefab, position, Quaternion.identity);
        
        IEnemy enemy = enemyObject.GetComponent<IEnemy>();
        enemy?.Initialize();
        
        return enemy;
    }
    
    private GameObject GetPrefabForType(EnemyType type)
    {
        return type switch
        {
            EnemyType.Zombie => zombiePrefab,
            EnemyType.Skeleton => skeletonPrefab,
            EnemyType.Boss => bossPrefab,
            _ => zombiePrefab
        };
    }
}
```

### Object Pool Pattern (Advanced Implementation)
```csharp
public class AdvancedObjectPool<T> : MonoBehaviour where T : MonoBehaviour, IPoolable
{
    [SerializeField] private T prefab;
    [SerializeField] private int initialPoolSize = 10;
    [SerializeField] private int maxPoolSize = 100;
    [SerializeField] private bool expandPool = true;
    
    private Queue<T> availableObjects = new Queue<T>();
    private HashSet<T> activeObjects = new HashSet<T>();
    
    private void Start()
    {
        InitializePool();
    }
    
    private void InitializePool()
    {
        for (int i = 0; i < initialPoolSize; i++)
        {
            CreateNewObject();
        }
    }
    
    private T CreateNewObject()
    {
        T newObject = Instantiate(prefab, transform);
        newObject.gameObject.SetActive(false);
        newObject.SetPool(this);
        availableObjects.Enqueue(newObject);
        return newObject;
    }
    
    public T GetObject()
    {
        T objectToReturn;
        
        if (availableObjects.Count > 0)
        {
            objectToReturn = availableObjects.Dequeue();
        }
        else if (expandPool && activeObjects.Count < maxPoolSize)
        {
            objectToReturn = CreateNewObject();
            availableObjects.Dequeue(); // Remove from available since we're returning it
        }
        else
        {
            return null; // Pool exhausted
        }
        
        activeObjects.Add(objectToReturn);
        objectToReturn.gameObject.SetActive(true);
        objectToReturn.OnSpawn();
        
        return objectToReturn;
    }
    
    public void ReturnObject(T objectToReturn)
    {
        if (activeObjects.Contains(objectToReturn))
        {
            activeObjects.Remove(objectToReturn);
            objectToReturn.OnDespawn();
            objectToReturn.gameObject.SetActive(false);
            availableObjects.Enqueue(objectToReturn);
        }
    }
}

public interface IPoolable
{
    void SetPool(MonoBehaviour pool);
    void OnSpawn();
    void OnDespawn();
}
```

## 🚀 Behavioral Patterns

### Strategy Pattern for AI Behaviors
```csharp
public interface IMovementStrategy
{
    void Move(Transform transform, Transform target);
}

public class DirectMovement : IMovementStrategy
{
    private float speed;
    
    public DirectMovement(float speed)
    {
        this.speed = speed;
    }
    
    public void Move(Transform transform, Transform target)
    {
        Vector3 direction = (target.position - transform.position).normalized;
        transform.position += direction * speed * Time.deltaTime;
    }
}

public class PatrolMovement : IMovementStrategy
{
    private float speed;
    private Vector3[] patrolPoints;
    private int currentPatrolIndex;
    
    public PatrolMovement(float speed, Vector3[] patrolPoints)
    {
        this.speed = speed;
        this.patrolPoints = patrolPoints;
    }
    
    public void Move(Transform transform, Transform target)
    {
        if (patrolPoints.Length == 0) return;
        
        Vector3 targetPoint = patrolPoints[currentPatrolIndex];
        Vector3 direction = (targetPoint - transform.position).normalized;
        
        transform.position += direction * speed * Time.deltaTime;
        
        if (Vector3.Distance(transform.position, targetPoint) < 0.5f)
        {
            currentPatrolIndex = (currentPatrolIndex + 1) % patrolPoints.Length;
        }
    }
}

public class EnemyController : MonoBehaviour
{
    private IMovementStrategy movementStrategy;
    private Transform player;
    
    public void SetMovementStrategy(IMovementStrategy strategy)
    {
        movementStrategy = strategy;
    }
    
    private void Update()
    {
        if (movementStrategy != null && player != null)
        {
            movementStrategy.Move(transform, player);
        }
    }
}
```

### Command Pattern for Input System
```csharp
public interface ICommand
{
    void Execute();
    void Undo();
    bool IsUndoable { get; }
}

public class MoveCommand : ICommand
{
    private Transform target;
    private Vector3 direction;
    private float distance;
    private Vector3 previousPosition;
    
    public bool IsUndoable => true;
    
    public MoveCommand(Transform target, Vector3 direction, float distance)
    {
        this.target = target;
        this.direction = direction.normalized;
        this.distance = distance;
    }
    
    public void Execute()
    {
        previousPosition = target.position;
        target.position += direction * distance;
    }
    
    public void Undo()
    {
        target.position = previousPosition;
    }
}

public class InputHandler : MonoBehaviour
{
    private Stack<ICommand> commandHistory = new Stack<ICommand>();
    private PlayerController player;
    
    private void Start()
    {
        player = GetComponent<PlayerController>();
    }
    
    private void Update()
    {
        HandleInput();
    }
    
    private void HandleInput()
    {
        Vector3 input = Vector3.zero;
        
        if (Input.GetKeyDown(KeyCode.W))
            input = Vector3.forward;
        else if (Input.GetKeyDown(KeyCode.S))
            input = Vector3.back;
        else if (Input.GetKeyDown(KeyCode.A))
            input = Vector3.left;
        else if (Input.GetKeyDown(KeyCode.D))
            input = Vector3.right;
        
        if (input != Vector3.zero)
        {
            ICommand moveCommand = new MoveCommand(transform, input, 1f);
            ExecuteCommand(moveCommand);
        }
        
        if (Input.GetKeyDown(KeyCode.Z))
        {
            UndoLastCommand();
        }
    }
    
    private void ExecuteCommand(ICommand command)
    {
        command.Execute();
        
        if (command.IsUndoable)
        {
            commandHistory.Push(command);
        }
    }
    
    private void UndoLastCommand()
    {
        if (commandHistory.Count > 0)
        {
            ICommand lastCommand = commandHistory.Pop();
            lastCommand.Undo();
        }
    }
}
```

## 💡 Structural Patterns

### Adapter Pattern for Third-Party Integration
```csharp
// Third-party audio system interface
public interface IThirdPartyAudio
{
    void PlaySound(string soundName, float volume, bool loop);
    void StopSound(string soundName);
}

// Unity AudioSource wrapper
public interface IAudioService
{
    void Play(string clipName, float volume = 1f, bool looping = false);
    void Stop(string clipName);
    void SetVolume(string clipName, float volume);
}

public class AudioAdapter : MonoBehaviour, IAudioService
{
    private IThirdPartyAudio thirdPartyAudio;
    private Dictionary<string, AudioClip> audioClips;
    
    public AudioAdapter(IThirdPartyAudio thirdPartyAudio)
    {
        this.thirdPartyAudio = thirdPartyAudio;
        LoadAudioClips();
    }
    
    public void Play(string clipName, float volume = 1f, bool looping = false)
    {
        if (audioClips.ContainsKey(clipName))
        {
            thirdPartyAudio.PlaySound(clipName, volume, looping);
        }
    }
    
    public void Stop(string clipName)
    {
        thirdPartyAudio.StopSound(clipName);
    }
    
    public void SetVolume(string clipName, float volume)
    {
        // Implementation would depend on third-party system capabilities
        Stop(clipName);
        Play(clipName, volume);
    }
    
    private void LoadAudioClips()
    {
        audioClips = new Dictionary<string, AudioClip>();
        // Load clips from Resources or addressable system
    }
}
```

### Decorator Pattern for Power-ups
```csharp
public interface IWeapon
{
    float Damage { get; }
    float FireRate { get; }
    void Fire();
}

public class BasicWeapon : MonoBehaviour, IWeapon
{
    [SerializeField] private float baseDamage = 10f;
    [SerializeField] private float baseFireRate = 1f;
    
    public virtual float Damage => baseDamage;
    public virtual float FireRate => baseFireRate;
    
    public virtual void Fire()
    {
        Debug.Log($"Firing basic weapon - Damage: {Damage}, Rate: {FireRate}");
        // Basic firing logic
    }
}

public abstract class WeaponDecorator : IWeapon
{
    protected IWeapon weapon;
    
    public WeaponDecorator(IWeapon weapon)
    {
        this.weapon = weapon;
    }
    
    public virtual float Damage => weapon.Damage;
    public virtual float FireRate => weapon.FireRate;
    
    public virtual void Fire()
    {
        weapon.Fire();
    }
}

public class DamageBoostDecorator : WeaponDecorator
{
    private float damageMultiplier;
    
    public DamageBoostDecorator(IWeapon weapon, float multiplier) : base(weapon)
    {
        damageMultiplier = multiplier;
    }
    
    public override float Damage => weapon.Damage * damageMultiplier;
    
    public override void Fire()
    {
        Debug.Log("Damage boost active!");
        base.Fire();
    }
}

public class RapidFireDecorator : WeaponDecorator
{
    private float fireRateMultiplier;
    
    public RapidFireDecorator(IWeapon weapon, float multiplier) : base(weapon)
    {
        fireRateMultiplier = multiplier;
    }
    
    public override float FireRate => weapon.FireRate * fireRateMultiplier;
    
    public override void Fire()
    {
        Debug.Log("Rapid fire active!");
        base.Fire();
    }
}
```

## 🚀 AI/LLM Integration for Pattern Implementation

### Pattern Selection and Implementation
```
Prompt: "I need to implement [specific functionality] in Unity. Which design pattern would be most appropriate, and can you provide a complete C# implementation with Unity-specific considerations?"

Prompt: "Review this Unity code and identify opportunities to apply design patterns for better maintainability and extensibility: [code snippet]"

Prompt: "Create a comprehensive architecture using multiple design patterns for a [game type] that handles [specific systems like inventory, combat, AI, etc.]"
```

### Code Generation and Optimization
```
Prompt: "Generate a complete implementation of the [pattern name] pattern for Unity that includes proper error handling, Unity lifecycle management, and performance considerations."

Prompt: "Help me refactor this Unity script to use the [pattern name] pattern while maintaining the same functionality but improving testability and maintainability."
```

## 🔄 Advanced Pattern Combinations

### MVC + Observer + Command Pattern Integration
```csharp
public class GameController : MonoBehaviour
{
    private GameModel model;
    private GameView view;
    private CommandInvoker commandInvoker;
    
    private void Start()
    {
        model = new GameModel();
        view = FindObjectOfType<GameView>();
        commandInvoker = new CommandInvoker();
        
        // Wire up observer relationships
        model.OnScoreChanged += view.UpdateScore;
        model.OnHealthChanged += view.UpdateHealth;
        model.OnGameStateChanged += view.UpdateGameState;
    }
    
    public void ExecutePlayerAction(ICommand command)
    {
        commandInvoker.ExecuteCommand(command);
    }
    
    public void UndoLastAction()
    {
        commandInvoker.UndoLastCommand();
    }
}
```

This comprehensive guide provides enterprise-level design pattern implementations specifically tailored for Unity development, enabling scalable and maintainable game architecture.