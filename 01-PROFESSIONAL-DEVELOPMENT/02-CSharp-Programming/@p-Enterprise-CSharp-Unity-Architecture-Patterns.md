# @p-Enterprise C# Unity Architecture Patterns

## 🎯 Learning Objectives
- Master enterprise-level C# architecture patterns for Unity
- Implement scalable, maintainable code architectures
- Understand dependency injection and inversion of control
- Design robust systems for large-scale Unity projects

## 🏗️ Architectural Foundations

### SOLID Principles in Unity Context
```csharp
// Single Responsibility Principle
public class PlayerHealthSystem
{
    private readonly IHealthCalculator _calculator;
    private readonly IHealthPersistence _persistence;
    private readonly IHealthEvents _events;
    
    public PlayerHealthSystem(
        IHealthCalculator calculator,
        IHealthPersistence persistence,
        IHealthEvents events)
    {
        _calculator = calculator;
        _persistence = persistence;
        _events = events;
    }
    
    public void TakeDamage(float damage)
    {
        var actualDamage = _calculator.CalculateDamage(damage);
        var newHealth = CurrentHealth - actualDamage;
        
        SetHealth(newHealth);
        _events.OnHealthChanged(CurrentHealth, actualDamage);
    }
}

// Open/Closed Principle - Extensible without modification
public abstract class WeaponBehavior
{
    public abstract void Fire(Vector3 direction, float force);
    public virtual void OnEquip() { }
    public virtual void OnUnequip() { }
}

public class RifleWeapon : WeaponBehavior
{
    public override void Fire(Vector3 direction, float force)
    {
        // Rifle-specific firing logic
        CreateBullet(direction, force * 1.2f);
        PlayRifleSound();
        ApplyRecoil(direction * -0.1f);
    }
}

public class ShotgunWeapon : WeaponBehavior
{
    public override void Fire(Vector3 direction, float force)
    {
        // Shotgun-specific firing logic
        for (int i = 0; i < 5; i++)
        {
            var spread = Random.insideUnitCircle * 0.2f;
            var shotDirection = direction + new Vector3(spread.x, spread.y, 0);
            CreatePellet(shotDirection, force * 0.8f);
        }
        PlayShotgunSound();
    }
}

// Liskov Substitution Principle
public interface IMovementController
{
    void Move(Vector3 direction);
    bool CanMove { get; }
    float MovementSpeed { get; }
}

public class PlayerMovementController : IMovementController
{
    public bool CanMove => !_isStunned && !_isDead;
    public float MovementSpeed => _baseSpeed * _speedMultiplier;
    
    public void Move(Vector3 direction)
    {
        if (!CanMove) return;
        
        transform.Translate(direction * MovementSpeed * Time.deltaTime);
    }
}

// Interface Segregation Principle
public interface IRenderable
{
    void Render();
}

public interface IUpdatable
{
    void Update(float deltaTime);
}

public interface IInitializable
{
    Task InitializeAsync();
}

// Dependency Inversion Principle
public class GameSaveSystem
{
    private readonly ISaveDataProvider _dataProvider;
    private readonly IEncryptionService _encryption;
    private readonly ICompressionService _compression;
    
    public GameSaveSystem(
        ISaveDataProvider dataProvider,
        IEncryptionService encryption,
        ICompressionService compression)
    {
        _dataProvider = dataProvider;
        _encryption = encryption;
        _compression = compression;
    }
    
    public async Task<bool> SaveGameAsync(GameData data)
    {
        var serialized = JsonUtility.ToJson(data);
        var compressed = await _compression.CompressAsync(serialized);
        var encrypted = await _encryption.EncryptAsync(compressed);
        
        return await _dataProvider.SaveAsync("game_save", encrypted);
    }
}
```

### Dependency Injection Container
```csharp
public interface IServiceContainer
{
    void RegisterSingleton<TInterface, TImplementation>()
        where TImplementation : class, TInterface, new()
        where TInterface : class;
    
    void RegisterTransient<TInterface, TImplementation>()
        where TImplementation : class, TInterface, new()
        where TInterface : class;
    
    void RegisterInstance<T>(T instance) where T : class;
    
    T Resolve<T>() where T : class;
    object Resolve(Type type);
    bool IsRegistered<T>() where T : class;
}

public class UnityServiceContainer : IServiceContainer
{
    private readonly Dictionary<Type, ServiceDescriptor> _services = new();
    private readonly Dictionary<Type, object> _singletonInstances = new();
    
    public void RegisterSingleton<TInterface, TImplementation>()
        where TImplementation : class, TInterface, new()
        where TInterface : class
    {
        _services[typeof(TInterface)] = new ServiceDescriptor
        {
            ServiceType = typeof(TInterface),
            ImplementationType = typeof(TImplementation),
            Lifetime = ServiceLifetime.Singleton,
            Factory = () => new TImplementation()
        };
    }
    
    public void RegisterTransient<TInterface, TImplementation>()
        where TImplementation : class, TInterface, new()
        where TInterface : class
    {
        _services[typeof(TInterface)] = new ServiceDescriptor
        {
            ServiceType = typeof(TInterface),
            ImplementationType = typeof(TImplementation),
            Lifetime = ServiceLifetime.Transient,
            Factory = () => new TImplementation()
        };
    }
    
    public T Resolve<T>() where T : class
    {
        return (T)Resolve(typeof(T));
    }
    
    public object Resolve(Type type)
    {
        if (!_services.TryGetValue(type, out var descriptor))
        {
            throw new InvalidOperationException($"Service {type.Name} is not registered");
        }
        
        if (descriptor.Lifetime == ServiceLifetime.Singleton)
        {
            if (_singletonInstances.TryGetValue(type, out var instance))
                return instance;
                
            instance = CreateInstance(descriptor);
            _singletonInstances[type] = instance;
            return instance;
        }
        
        return CreateInstance(descriptor);
    }
    
    private object CreateInstance(ServiceDescriptor descriptor)
    {
        var instance = descriptor.Factory();
        
        // Inject dependencies into the created instance
        InjectDependencies(instance);
        
        return instance;
    }
    
    private void InjectDependencies(object instance)
    {
        var type = instance.GetType();
        var properties = type.GetProperties(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance)
            .Where(p => p.GetCustomAttribute<InjectAttribute>() != null);
            
        foreach (var property in properties)
        {
            if (IsRegistered(property.PropertyType))
            {
                var dependency = Resolve(property.PropertyType);
                property.SetValue(instance, dependency);
            }
        }
    }
}

[AttributeUsage(AttributeTargets.Property | AttributeTargets.Field)]
public class InjectAttribute : Attribute { }

public class ServiceDescriptor
{
    public Type ServiceType { get; set; }
    public Type ImplementationType { get; set; }
    public ServiceLifetime Lifetime { get; set; }
    public Func<object> Factory { get; set; }
}

public enum ServiceLifetime
{
    Transient,
    Singleton
}
```

### Command Pattern for Actions
```csharp
public interface ICommand
{
    Task ExecuteAsync();
    Task UndoAsync();
    bool CanExecute { get; }
    string Description { get; }
}

public abstract class GameCommand : ICommand
{
    public abstract string Description { get; }
    public virtual bool CanExecute => true;
    
    public abstract Task ExecuteAsync();
    public virtual Task UndoAsync() => Task.CompletedTask;
}

public class MovePlayerCommand : GameCommand
{
    private readonly IPlayerController _player;
    private readonly Vector3 _targetPosition;
    private Vector3 _previousPosition;
    
    public override string Description => $"Move player to {_targetPosition}";
    
    public MovePlayerCommand(IPlayerController player, Vector3 targetPosition)
    {
        _player = player;
        _targetPosition = targetPosition;
    }
    
    public override async Task ExecuteAsync()
    {
        _previousPosition = _player.Position;
        await _player.MoveToAsync(_targetPosition);
    }
    
    public override async Task UndoAsync()
    {
        await _player.MoveToAsync(_previousPosition);
    }
}

public class CommandInvoker
{
    private readonly Stack<ICommand> _executedCommands = new();
    private readonly Queue<ICommand> _commandQueue = new();
    
    public async Task ExecuteCommandAsync(ICommand command)
    {
        if (!command.CanExecute)
            return;
            
        await command.ExecuteAsync();
        _executedCommands.Push(command);
    }
    
    public async Task UndoLastCommandAsync()
    {
        if (_executedCommands.Count == 0)
            return;
            
        var command = _executedCommands.Pop();
        await command.UndoAsync();
    }
    
    public void QueueCommand(ICommand command)
    {
        _commandQueue.Enqueue(command);
    }
    
    public async Task ProcessQueuedCommandsAsync()
    {
        while (_commandQueue.Count > 0)
        {
            var command = _commandQueue.Dequeue();
            await ExecuteCommandAsync(command);
        }
    }
}
```

### Observer Pattern with Events
```csharp
public interface IEventBus
{
    void Subscribe<T>(Action<T> handler) where T : IGameEvent;
    void Unsubscribe<T>(Action<T> handler) where T : IGameEvent;
    void Publish<T>(T gameEvent) where T : IGameEvent;
    Task PublishAsync<T>(T gameEvent) where T : IGameEvent;
}

public interface IGameEvent
{
    DateTime Timestamp { get; }
    string EventId { get; }
    Dictionary<string, object> Metadata { get; }
}

public abstract class GameEvent : IGameEvent
{
    public DateTime Timestamp { get; } = DateTime.UtcNow;
    public string EventId { get; } = Guid.NewGuid().ToString();
    public Dictionary<string, object> Metadata { get; } = new();
}

public class PlayerLevelUpEvent : GameEvent
{
    public int PlayerId { get; set; }
    public int OldLevel { get; set; }
    public int NewLevel { get; set; }
    public int ExperienceGained { get; set; }
    public List<string> UnlockedFeatures { get; set; } = new();
}

public class TypedEventBus : IEventBus
{
    private readonly Dictionary<Type, List<Delegate>> _subscribers = new();
    private readonly Queue<IGameEvent> _eventQueue = new();
    private readonly object _lock = new object();
    
    public void Subscribe<T>(Action<T> handler) where T : IGameEvent
    {
        lock (_lock)
        {
            var eventType = typeof(T);
            if (!_subscribers.ContainsKey(eventType))
                _subscribers[eventType] = new List<Delegate>();
                
            _subscribers[eventType].Add(handler);
        }
    }
    
    public void Unsubscribe<T>(Action<T> handler) where T : IGameEvent
    {
        lock (_lock)
        {
            var eventType = typeof(T);
            if (_subscribers.TryGetValue(eventType, out var handlers))
            {
                handlers.Remove(handler);
                if (handlers.Count == 0)
                    _subscribers.Remove(eventType);
            }
        }
    }
    
    public void Publish<T>(T gameEvent) where T : IGameEvent
    {
        lock (_lock)
        {
            _eventQueue.Enqueue(gameEvent);
        }
    }
    
    public async Task PublishAsync<T>(T gameEvent) where T : IGameEvent
    {
        var eventType = typeof(T);
        
        if (_subscribers.TryGetValue(eventType, out var handlers))
        {
            var tasks = handlers.Select(async handler =>
            {
                try
                {
                    if (handler is Action<T> action)
                        action(gameEvent);
                    else if (handler is Func<T, Task> asyncAction)
                        await asyncAction(gameEvent);
                }
                catch (Exception ex)
                {
                    Debug.LogError($"Event handler error: {ex.Message}");
                }
            });
            
            await Task.WhenAll(tasks);
        }
    }
}

// Example usage of the event system
public class PlayerProgressionSystem
{
    private readonly IEventBus _eventBus;
    
    [Inject] public IPlayerRepository PlayerRepository { get; set; }
    [Inject] public IAchievementSystem AchievementSystem { get; set; }
    
    public PlayerProgressionSystem(IEventBus eventBus)
    {
        _eventBus = eventBus;
        _eventBus.Subscribe<PlayerLevelUpEvent>(OnPlayerLevelUp);
    }
    
    private async void OnPlayerLevelUp(PlayerLevelUpEvent levelUpEvent)
    {
        // Update player data
        var player = await PlayerRepository.GetByIdAsync(levelUpEvent.PlayerId);
        player.Level = levelUpEvent.NewLevel;
        await PlayerRepository.SaveAsync(player);
        
        // Check for achievements
        await AchievementSystem.CheckLevelAchievementsAsync(player);
        
        // Show level up UI
        var uiEvent = new ShowLevelUpUIEvent
        {
            PlayerId = levelUpEvent.PlayerId,
            NewLevel = levelUpEvent.NewLevel,
            UnlockedFeatures = levelUpEvent.UnlockedFeatures
        };
        
        _eventBus.Publish(uiEvent);
    }
}
```

## 🔧 Advanced Unity Architecture Patterns

### Repository Pattern for Data Access
```csharp
public interface IRepository<T> where T : class
{
    Task<T> GetByIdAsync(string id);
    Task<IEnumerable<T>> GetAllAsync();
    Task<T> AddAsync(T entity);
    Task<T> UpdateAsync(T entity);
    Task<bool> DeleteAsync(string id);
    IQueryable<T> Query();
}

public interface IPlayerRepository : IRepository<Player>
{
    Task<Player> GetByUsernameAsync(string username);
    Task<IEnumerable<Player>> GetPlayersByLevelRangeAsync(int minLevel, int maxLevel);
    Task<bool> UpdatePlayerStatsAsync(string playerId, PlayerStats stats);
}

public class PlayerRepository : IPlayerRepository
{
    private readonly IDataContext _dataContext;
    private readonly IMemoryCache _cache;
    private readonly ILogger _logger;
    
    public PlayerRepository(
        IDataContext dataContext,
        IMemoryCache cache,
        ILogger logger)
    {
        _dataContext = dataContext;
        _cache = cache;
        _logger = logger;
    }
    
    public async Task<Player> GetByIdAsync(string id)
    {
        var cacheKey = $"player_{id}";
        
        if (_cache.TryGetValue(cacheKey, out Player cachedPlayer))
            return cachedPlayer;
            
        var player = await _dataContext.Players
            .Include(p => p.Stats)
            .Include(p => p.Inventory)
            .FirstOrDefaultAsync(p => p.Id == id);
            
        if (player != null)
        {
            _cache.Set(cacheKey, player, TimeSpan.FromMinutes(10));
        }
        
        return player;
    }
    
    public async Task<Player> GetByUsernameAsync(string username)
    {
        return await _dataContext.Players
            .FirstOrDefaultAsync(p => p.Username == username);
    }
    
    public async Task<T> UpdateAsync(T entity)
    {
        try
        {
            _dataContext.Update(entity);
            await _dataContext.SaveChangesAsync();
            
            // Invalidate cache
            if (entity is Player player)
                _cache.Remove($"player_{player.Id}");
                
            return entity;
        }
        catch (Exception ex)
        {
            _logger.LogError($"Failed to update entity: {ex.Message}");
            throw;
        }
    }
}
```

### Factory Pattern for Object Creation
```csharp
public interface IGameObjectFactory
{
    T Create<T>(string prefabName) where T : Component;
    GameObject CreateGameObject(string prefabName);
    Task<T> CreateAsync<T>(string prefabName) where T : Component;
}

public class UnityGameObjectFactory : IGameObjectFactory
{
    private readonly IResourceLoader _resourceLoader;
    private readonly IServiceContainer _serviceContainer;
    private readonly Dictionary<string, GameObject> _prefabCache = new();
    
    public UnityGameObjectFactory(
        IResourceLoader resourceLoader,
        IServiceContainer serviceContainer)
    {
        _resourceLoader = resourceLoader;
        _serviceContainer = serviceContainer;
    }
    
    public T Create<T>(string prefabName) where T : Component
    {
        var gameObject = CreateGameObject(prefabName);
        var component = gameObject.GetComponent<T>();
        
        if (component == null)
        {
            throw new InvalidOperationException($"Prefab {prefabName} does not contain component {typeof(T).Name}");
        }
        
        // Inject dependencies if the component supports it
        InjectDependencies(component);
        
        return component;
    }
    
    public GameObject CreateGameObject(string prefabName)
    {
        var prefab = GetPrefab(prefabName);
        var instance = Object.Instantiate(prefab);
        
        // Inject dependencies into all injectable components
        var injectableComponents = instance.GetComponentsInChildren<IInjectableBehaviour>();
        foreach (var component in injectableComponents)
        {
            InjectDependencies(component);
        }
        
        return instance;
    }
    
    private GameObject GetPrefab(string prefabName)
    {
        if (_prefabCache.TryGetValue(prefabName, out var cachedPrefab))
            return cachedPrefab;
            
        var prefab = _resourceLoader.Load<GameObject>(prefabName);
        if (prefab == null)
        {
            throw new InvalidOperationException($"Prefab {prefabName} not found");
        }
        
        _prefabCache[prefabName] = prefab;
        return prefab;
    }
    
    private void InjectDependencies(object target)
    {
        var type = target.GetType();
        var properties = type.GetProperties(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance)
            .Where(p => p.GetCustomAttribute<InjectAttribute>() != null);
            
        foreach (var property in properties)
        {
            if (_serviceContainer.IsRegistered(property.PropertyType))
            {
                var dependency = _serviceContainer.Resolve(property.PropertyType);
                property.SetValue(target, dependency);
            }
        }
    }
}

public interface IInjectableBehaviour
{
    void OnDependenciesInjected();
}

// Example injectable MonoBehaviour
public class PlayerController : MonoBehaviour, IInjectableBehaviour
{
    [Inject] public IInputService InputService { get; set; }
    [Inject] public IPlayerRepository PlayerRepository { get; set; }
    [Inject] public IEventBus EventBus { get; set; }
    
    private Player _playerData;
    
    public void OnDependenciesInjected()
    {
        // Dependencies are now available
        InitializePlayer();
    }
    
    private async void InitializePlayer()
    {
        _playerData = await PlayerRepository.GetByIdAsync(PlayerId);
        InputService.OnMoveInput += HandleMoveInput;
    }
}
```

### State Machine Pattern
```csharp
public interface IState<TContext>
{
    void Enter(TContext context);
    void Update(TContext context, float deltaTime);
    void Exit(TContext context);
    bool CanTransitionTo<TState>() where TState : IState<TContext>;
}

public abstract class State<TContext> : IState<TContext>
{
    public virtual void Enter(TContext context) { }
    public virtual void Update(TContext context, float deltaTime) { }
    public virtual void Exit(TContext context) { }
    public virtual bool CanTransitionTo<TState>() where TState : IState<TContext> => true;
}

public class StateMachine<TContext>
{
    private IState<TContext> _currentState;
    private readonly Dictionary<Type, IState<TContext>> _states = new();
    private readonly TContext _context;
    
    public StateMachine(TContext context)
    {
        _context = context;
    }
    
    public void RegisterState<TState>(TState state) where TState : IState<TContext>
    {
        _states[typeof(TState)] = state;
    }
    
    public void TransitionTo<TState>() where TState : IState<TContext>
    {
        var newStateType = typeof(TState);
        
        if (!_states.TryGetValue(newStateType, out var newState))
        {
            throw new InvalidOperationException($"State {newStateType.Name} is not registered");
        }
        
        if (_currentState != null && !_currentState.CanTransitionTo<TState>())
        {
            throw new InvalidOperationException($"Cannot transition from {_currentState.GetType().Name} to {newStateType.Name}");
        }
        
        _currentState?.Exit(_context);
        _currentState = newState;
        _currentState.Enter(_context);
    }
    
    public void Update(float deltaTime)
    {
        _currentState?.Update(_context, deltaTime);
    }
}

// Example: Player state machine
public class PlayerStateMachine : MonoBehaviour
{
    private StateMachine<PlayerController> _stateMachine;
    private PlayerController _playerController;
    
    private void Awake()
    {
        _playerController = GetComponent<PlayerController>();
        _stateMachine = new StateMachine<PlayerController>(_playerController);
        
        // Register states
        _stateMachine.RegisterState(new IdleState());
        _stateMachine.RegisterState(new MovingState());
        _stateMachine.RegisterState(new JumpingState());
        _stateMachine.RegisterState(new AttackingState());
        
        // Start in idle state
        _stateMachine.TransitionTo<IdleState>();
    }
    
    private void Update()
    {
        _stateMachine.Update(Time.deltaTime);
    }
}

public class IdleState : State<PlayerController>
{
    public override void Enter(PlayerController context)
    {
        context.SetAnimation("Idle");
    }
    
    public override void Update(PlayerController context, float deltaTime)
    {
        if (context.InputService.HasMoveInput)
        {
            context.StateMachine.TransitionTo<MovingState>();
        }
        else if (context.InputService.HasJumpInput)
        {
            context.StateMachine.TransitionTo<JumpingState>();
        }
    }
}

public class MovingState : State<PlayerController>
{
    public override void Enter(PlayerController context)
    {
        context.SetAnimation("Running");
    }
    
    public override void Update(PlayerController context, float deltaTime)
    {
        context.Move(context.InputService.MoveDirection);
        
        if (!context.InputService.HasMoveInput)
        {
            context.StateMachine.TransitionTo<IdleState>();
        }
        else if (context.InputService.HasJumpInput)
        {
            context.StateMachine.TransitionTo<JumpingState>();
        }
    }
}
```

## 🚀 AI/LLM Integration for Architecture

### Automated Architecture Analysis
```yaml
AI_Architecture_Assistance:
  code_review:
    - SOLID principle compliance checking
    - Design pattern identification and suggestions
    - Dependency analysis and optimization
    - Performance bottleneck identification
    - Code smell detection and refactoring suggestions
    
  documentation_generation:
    - Architecture diagram generation from code
    - API documentation with examples
    - Design decision documentation
    - Code comment generation and improvement
    - README and setup guide creation
```

### Architecture Decision Prompts
```yaml
Decision_Making_Prompts:
  pattern_selection:
    - "Analyze this Unity system and suggest appropriate design patterns"
    - "Review this architecture for scalability and maintainability"
    - "Identify potential performance issues in this code structure"
    - "Suggest dependency injection improvements for this system"
    - "Evaluate this state machine implementation for best practices"
    
  refactoring_guidance:
    - "Help refactor this monolithic class using SOLID principles"
    - "Suggest how to implement the Repository pattern for this data access"
    - "Design an event system for loose coupling between these components"
    - "Create a factory pattern for this object creation scenario"
    - "Implement proper error handling throughout this architecture"
```

## 💡 Key Highlights

- **SOLID Foundation**: Master SOLID principles for maintainable Unity code
- **Dependency Injection**: Use DI containers for loose coupling and testability
- **Pattern Library**: Build a repertoire of proven design patterns for Unity
- **Event-Driven Design**: Implement robust event systems for component communication
- **Architecture Documentation**: Maintain clear documentation of architectural decisions
- **AI-Assisted Development**: Leverage AI tools for architecture analysis and improvement

## 🔗 Next Steps

1. **Practice SOLID Principles**: Refactor existing code to follow SOLID principles
2. **Implement DI Container**: Build and use dependency injection in Unity projects
3. **Master Design Patterns**: Practice implementing common patterns in Unity context
4. **Build Event Systems**: Create type-safe event systems for project communication
5. **Document Architecture**: Practice writing clear architectural documentation

*Enterprise C# Unity architecture requires balancing theoretical principles with practical Unity constraints. Success comes from applying proven patterns while considering Unity's component-based architecture and performance requirements.*