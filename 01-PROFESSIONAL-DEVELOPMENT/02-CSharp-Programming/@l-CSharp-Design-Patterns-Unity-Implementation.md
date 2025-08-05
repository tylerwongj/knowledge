# @l-CSharp-Design-Patterns-Unity-Implementation - Professional Architecture Patterns

## 🎯 Learning Objectives
- Master essential design patterns for Unity game development
- Implement scalable and maintainable game architecture patterns
- Create flexible systems using proven software design principles
- Optimize pattern implementations for Unity's component-based architecture
- Develop reusable code frameworks for rapid game development

## 🔧 Core Architectural Patterns

### Singleton Pattern (Unity-Optimized)
```csharp
// Thread-safe, lazy-initialized singleton with Unity lifecycle management
public abstract class Singleton<T> : MonoBehaviour where T : MonoBehaviour
{
    private static T _instance;
    private static readonly object _lock = new object();
    private static bool _applicationIsQuitting = false;
    
    public static T Instance
    {
        get
        {
            if (_applicationIsQuitting)
            {
                Debug.LogWarning($"[Singleton] Instance '{typeof(T)}' already destroyed. Returning null.");
                return null;
            }
            
            lock (_lock)
            {
                if (_instance == null)
                {
                    _instance = FindObjectOfType<T>();
                    
                    if (_instance == null)
                    {
                        GameObject singleton = new GameObject($"{typeof(T).Name} (Singleton)");
                        _instance = singleton.AddComponent<T>();
                        DontDestroyOnLoad(singleton);
                    }
                }
                
                return _instance;
            }
        }
    }
    
    protected virtual void Awake()
    {
        if (_instance == null)
        {
            _instance = this as T;
            DontDestroyOnLoad(gameObject);
            OnAwakeImplementation();
        }
        else if (_instance != this)
        {
            Debug.LogWarning($"[Singleton] Duplicate instance of {typeof(T).Name} found. Destroying duplicate.");
            Destroy(gameObject);
        }
    }
    
    protected virtual void OnAwakeImplementation() { }
    
    protected virtual void OnDestroy()
    {
        _applicationIsQuitting = true;
    }
    
    protected virtual void OnApplicationQuit()
    {
        _applicationIsQuitting = true;
    }
}

// Example implementation: Audio Manager
public class AudioManager : Singleton<AudioManager>
{
    [Header("Audio Sources")]
    [SerializeField] private AudioSource musicSource;
    [SerializeField] private AudioSource sfxSource;
    
    [Header("Audio Settings")]
    [SerializeField] private float masterVolume = 1f;
    [SerializeField] private float musicVolume = 0.8f;
    [SerializeField] private float sfxVolume = 1f;
    
    private Dictionary<string, AudioClip> _audioClips = new Dictionary<string, AudioClip>();
    private Dictionary<string, AudioSource> _loopingSources = new Dictionary<string, AudioSource>();
    
    protected override void OnAwakeImplementation()
    {
        LoadAudioClips();
        SetupAudioSources();
    }
    
    public void PlaySFX(string clipName, float volume = 1f)
    {
        if (_audioClips.TryGetValue(clipName, out AudioClip clip))
        {
            sfxSource.PlayOneShot(clip, volume * sfxVolume * masterVolume);
        }
    }
    
    public void PlayMusic(string clipName, bool loop = true)
    {
        if (_audioClips.TryGetValue(clipName, out AudioClip clip))
        {
            musicSource.clip = clip;
            musicSource.loop = loop;
            musicSource.volume = musicVolume * masterVolume;
            musicSource.Play();
        }
    }
    
    public void PlayLoopingSFX(string clipName, string sourceId)
    {
        if (!_audioClips.TryGetValue(clipName, out AudioClip clip)) return;
        
        if (!_loopingSources.TryGetValue(sourceId, out AudioSource source))
        {
            GameObject loopObject = new GameObject($"Looping_{sourceId}");
            loopObject.transform.SetParent(transform);
            source = loopObject.AddComponent<AudioSource>();
            _loopingSources[sourceId] = source;
        }
        
        source.clip = clip;
        source.loop = true;
        source.volume = sfxVolume * masterVolume;
        source.Play();
    }
    
    public void StopLoopingSFX(string sourceId)
    {
        if (_loopingSources.TryGetValue(sourceId, out AudioSource source))
        {
            source.Stop();
        }
    }
}
```

### Observer Pattern (Event System)
```csharp
// Type-safe event system with automatic cleanup
public static class EventManager
{
    private static Dictionary<Type, List<object>> _eventListeners = new Dictionary<Type, List<object>>();
    private static Dictionary<object, List<Type>> _listenerToEvents = new Dictionary<object, List<Type>>();
    
    public static void Subscribe<T>(object listener, Action<T> callback) where T : IGameEvent
    {
        Type eventType = typeof(T);
        
        if (!_eventListeners.ContainsKey(eventType))
        {
            _eventListeners[eventType] = new List<object>();
        }
        
        if (!_listenerToEvents.ContainsKey(listener))
        {
            _listenerToEvents[listener] = new List<Type>();
        }
        
        var eventCallback = new EventCallback<T>(listener, callback);
        _eventListeners[eventType].Add(eventCallback);
        _listenerToEvents[listener].Add(eventType);
    }
    
    public static void Unsubscribe<T>(object listener) where T : IGameEvent
    {
        Type eventType = typeof(T);
        
        if (_eventListeners.TryGetValue(eventType, out List<object> callbacks))
        {
            callbacks.RemoveAll(callback => 
                callback is EventCallback<T> eventCallback && 
                eventCallback.Listener == listener);
        }
        
        if (_listenerToEvents.TryGetValue(listener, out List<Type> eventTypes))
        {
            eventTypes.Remove(eventType);
        }
    }
    
    public static void UnsubscribeAll(object listener)
    {
        if (_listenerToEvents.TryGetValue(listener, out List<Type> eventTypes))
        {
            foreach (Type eventType in eventTypes.ToList())
            {
                if (_eventListeners.TryGetValue(eventType, out List<object> callbacks))
                {
                    callbacks.RemoveAll(callback => 
                    {
                        var eventCallbackType = typeof(EventCallback<>).MakeGenericType(eventType);
                        if (eventCallbackType.IsInstanceOfType(callback))
                        {
                            var listenerProperty = eventCallbackType.GetProperty("Listener");
                            return listenerProperty?.GetValue(callback) == listener;
                        }
                        return false;
                    });
                }
            }
            
            _listenerToEvents.Remove(listener);
        }
    }
    
    public static void Publish<T>(T gameEvent) where T : IGameEvent
    {
        Type eventType = typeof(T);
        
        if (_eventListeners.TryGetValue(eventType, out List<object> callbacks))
        {
            // Create a copy to avoid modification during iteration
            var callbacksCopy = new List<object>(callbacks);
            
            foreach (object callback in callbacksCopy)
            {
                if (callback is EventCallback<T> eventCallback)
                {
                    try
                    {
                        eventCallback.Invoke(gameEvent);
                    }
                    catch (System.Exception ex)
                    {
                        Debug.LogError($"Error invoking event callback: {ex.Message}");
                    }
                }
            }
        }
    }
    
    public static void Clear()
    {
        _eventListeners.Clear();
        _listenerToEvents.Clear();
    }
    
    private class EventCallback<T> where T : IGameEvent
    {
        public object Listener { get; }
        private readonly Action<T> _callback;
        
        public EventCallback(object listener, Action<T> callback)
        {
            Listener = listener;
            _callback = callback;
        }
        
        public void Invoke(T gameEvent)
        {
            _callback?.Invoke(gameEvent);
        }
    }
}

// Event interfaces and implementations
public interface IGameEvent { }

public struct PlayerHealthChangedEvent : IGameEvent
{
    public int NewHealth { get; }
    public int MaxHealth { get; }
    public int PreviousHealth { get; }
    
    public PlayerHealthChangedEvent(int newHealth, int maxHealth, int previousHealth)
    {
        NewHealth = newHealth;
        MaxHealth = maxHealth;
        PreviousHealth = previousHealth;
    }
}

public struct EnemyDefeatedEvent : IGameEvent
{
    public string EnemyType { get; }
    public Vector3 Position { get; }
    public int ScoreValue { get; }
    
    public EnemyDefeatedEvent(string enemyType, Vector3 position, int scoreValue)
    {
        EnemyType = enemyType;
        Position = position;
        ScoreValue = scoreValue;
    }
}

// Example usage in a component
public class PlayerHealthUI : MonoBehaviour
{
    [SerializeField] private Slider healthSlider;
    [SerializeField] private Text healthText;
    
    private void OnEnable()
    {
        EventManager.Subscribe<PlayerHealthChangedEvent>(this, OnPlayerHealthChanged);
    }
    
    private void OnDisable()
    {
        EventManager.UnsubscribeAll(this);
    }
    
    private void OnPlayerHealthChanged(PlayerHealthChangedEvent healthEvent)
    {
        float healthPercent = (float)healthEvent.NewHealth / healthEvent.MaxHealth;
        healthSlider.value = healthPercent;
        healthText.text = $"{healthEvent.NewHealth}/{healthEvent.MaxHealth}";
    }
}
```

### Command Pattern (Action System)
```csharp
// Command pattern for undo/redo functionality and input handling
public interface ICommand
{
    void Execute();
    void Undo();
    bool CanExecute();
    string Description { get; }
}

public class CommandManager : MonoBehaviour
{
    private Stack<ICommand> _undoStack = new Stack<ICommand>();
    private Stack<ICommand> _redoStack = new Stack<ICommand>();
    private int _maxHistorySize = 50;
    
    public bool CanUndo => _undoStack.Count > 0;
    public bool CanRedo => _redoStack.Count > 0;
    
    public void ExecuteCommand(ICommand command)
    {
        if (command == null || !command.CanExecute()) return;
        
        command.Execute();
        _undoStack.Push(command);
        _redoStack.Clear(); // Clear redo stack when new command is executed
        
        // Limit history size
        while (_undoStack.Count > _maxHistorySize)
        {
            var commands = _undoStack.ToArray();
            _undoStack.Clear();
            for (int i = commands.Length - _maxHistorySize; i < commands.Length; i++)
            {
                _undoStack.Push(commands[i]);
            }
        }
    }
    
    public void Undo()
    {
        if (!CanUndo) return;
        
        ICommand command = _undoStack.Pop();
        command.Undo();
        _redoStack.Push(command);
    }
    
    public void Redo()
    {
        if (!CanRedo) return;
        
        ICommand command = _redoStack.Pop();
        command.Execute();
        _undoStack.Push(command);
    }
    
    public void ClearHistory()
    {
        _undoStack.Clear();
        _redoStack.Clear();
    }
}

// Example commands for a level editor
public class PlaceObjectCommand : ICommand
{
    private readonly GameObject _prefab;
    private readonly Vector3 _position;
    private readonly Quaternion _rotation;
    private GameObject _instantiatedObject;
    
    public string Description => $"Place {_prefab.name} at {_position}";
    
    public PlaceObjectCommand(GameObject prefab, Vector3 position, Quaternion rotation)
    {
        _prefab = prefab;
        _position = position;
        _rotation = rotation;
    }
    
    public bool CanExecute()
    {
        return _prefab != null;
    }
    
    public void Execute()
    {
        _instantiatedObject = Object.Instantiate(_prefab, _position, _rotation);
    }
    
    public void Undo()
    {
        if (_instantiatedObject != null)
        {
            Object.DestroyImmediate(_instantiatedObject);
        }
    }
}

public class MoveObjectCommand : ICommand
{
    private readonly Transform _target;
    private readonly Vector3 _oldPosition;
    private readonly Vector3 _newPosition;
    
    public string Description => $"Move {_target.name} to {_newPosition}";
    
    public MoveObjectCommand(Transform target, Vector3 newPosition)
    {
        _target = target;
        _oldPosition = target.position;
        _newPosition = newPosition;
    }
    
    public bool CanExecute()
    {
        return _target != null;
    }
    
    public void Execute()
    {
        _target.position = _newPosition;
    }
    
    public void Undo()
    {
        _target.position = _oldPosition;
    }
}

// Macro command for complex operations
public class MacroCommand : ICommand
{
    private readonly List<ICommand> _commands = new List<ICommand>();
    
    public string Description { get; private set; }
    
    public MacroCommand(string description)
    {
        Description = description;
    }
    
    public void AddCommand(ICommand command)
    {
        _commands.Add(command);
    }
    
    public bool CanExecute()
    {
        return _commands.All(cmd => cmd.CanExecute());
    }
    
    public void Execute()
    {
        foreach (var command in _commands)
        {
            command.Execute();
        }
    }
    
    public void Undo()
    {
        // Undo in reverse order
        for (int i = _commands.Count - 1; i >= 0; i--)
        {
            _commands[i].Undo();
        }
    }
}
```

### State Machine Pattern
```csharp
// Hierarchical State Machine for complex game object behavior
public abstract class State<T>
{
    protected T _context;
    
    public State(T context)
    {
        _context = context;
    }
    
    public virtual void Enter() { }
    public virtual void Update() { }
    public virtual void FixedUpdate() { }
    public virtual void Exit() { }
    public virtual void OnTriggerEnter(Collider other) { }
    public virtual void OnTriggerExit(Collider other) { }
}

public class StateMachine<T>
{
    private State<T> _currentState;
    private State<T> _previousState;
    private Dictionary<Type, State<T>> _states = new Dictionary<Type, State<T>>();
    
    public State<T> CurrentState => _currentState;
    public State<T> PreviousState => _previousState;
    
    public void AddState<TState>(TState state) where TState : State<T>
    {
        _states[typeof(TState)] = state;
    }
    
    public void ChangeState<TState>() where TState : State<T>
    {
        if (_states.TryGetValue(typeof(TState), out State<T> newState))
        {
            _previousState = _currentState;
            _currentState?.Exit();
            _currentState = newState;
            _currentState.Enter();
        }
    }
    
    public void Update()
    {
        _currentState?.Update();
    }
    
    public void FixedUpdate()
    {
        _currentState?.FixedUpdate();
    }
    
    public void OnTriggerEnter(Collider other)
    {
        _currentState?.OnTriggerEnter(other);
    }
    
    public void OnTriggerExit(Collider other)
    {
        _currentState?.OnTriggerExit(other);
    }
    
    public bool IsInState<TState>() where TState : State<T>
    {
        return _currentState?.GetType() == typeof(TState);
    }
}

// Example: Enemy AI State Machine
public class EnemyController : MonoBehaviour
{
    [Header("AI Settings")]
    [SerializeField] private float detectionRange = 10f;
    [SerializeField] private float attackRange = 2f;
    [SerializeField] private float patrolSpeed = 2f;
    [SerializeField] private float chaseSpeed = 5f;
    
    [Header("Patrol Points")]
    [SerializeField] private Transform[] patrolPoints;
    
    private StateMachine<EnemyController> _stateMachine;
    private NavMeshAgent _agent;
    private Animator _animator;
    private Transform _player;
    private int _currentPatrolIndex;
    
    public float DetectionRange => detectionRange;
    public float AttackRange => attackRange;
    public float PatrolSpeed => patrolSpeed;
    public float ChaseSpeed => chaseSpeed;
    public Transform[] PatrolPoints => patrolPoints;
    public Transform Player => _player;
    public NavMeshAgent Agent => _agent;
    public Animator Animator => _animator;
    public int CurrentPatrolIndex { get => _currentPatrolIndex; set => _currentPatrolIndex = value; }
    
    private void Awake()
    {
        _agent = GetComponent<NavMeshAgent>();
        _animator = GetComponent<Animator>();
        _player = GameObject.FindGameObjectWithTag("Player")?.transform;
        
        SetupStateMachine();
    }
    
    private void SetupStateMachine()
    {
        _stateMachine = new StateMachine<EnemyController>();
        _stateMachine.AddState(new PatrolState(this));
        _stateMachine.AddState(new ChaseState(this));
        _stateMachine.AddState(new AttackState(this));
        _stateMachine.AddState(new DeadState(this));
        
        _stateMachine.ChangeState<PatrolState>();
    }
    
    private void Update()
    {
        _stateMachine.Update();
    }
    
    private void FixedUpdate()
    {
        _stateMachine.FixedUpdate();
    }
    
    private void OnTriggerEnter(Collider other)
    {
        _stateMachine.OnTriggerEnter(other);
    }
    
    private void OnTriggerExit(Collider other)
    {
        _stateMachine.OnTriggerExit(other);
    }
    
    public float DistanceToPlayer()
    {
        return _player != null ? Vector3.Distance(transform.position, _player.position) : float.MaxValue;
    }
}

// State implementations
public class PatrolState : State<EnemyController>
{
    public PatrolState(EnemyController context) : base(context) { }
    
    public override void Enter()
    {
        _context.Agent.speed = _context.PatrolSpeed;
        _context.Animator.SetBool("IsPatrolling", true);
        MoveToNextPatrolPoint();
    }
    
    public override void Update()
    {
        // Check for player detection
        float distanceToPlayer = _context.DistanceToPlayer();
        if (distanceToPlayer <= _context.DetectionRange)
        {
            _context.GetComponent<StateMachine<EnemyController>>().ChangeState<ChaseState>();
            return;
        }
        
        // Continue patrolling
        if (!_context.Agent.pathPending && _context.Agent.remainingDistance < 0.5f)
        {
            MoveToNextPatrolPoint();
        }
    }
    
    public override void Exit()
    {
        _context.Animator.SetBool("IsPatrolling", false);
    }
    
    private void MoveToNextPatrolPoint()
    {
        if (_context.PatrolPoints.Length == 0) return;
        
        _context.Agent.destination = _context.PatrolPoints[_context.CurrentPatrolIndex].position;
        _context.CurrentPatrolIndex = (_context.CurrentPatrolIndex + 1) % _context.PatrolPoints.Length;
    }
}

public class ChaseState : State<EnemyController>
{
    public ChaseState(EnemyController context) : base(context) { }
    
    public override void Enter()
    {
        _context.Agent.speed = _context.ChaseSpeed;
        _context.Animator.SetBool("IsChasing", true);
    }
    
    public override void Update()
    {
        float distanceToPlayer = _context.DistanceToPlayer();
        
        // Check if player is in attack range
        if (distanceToPlayer <= _context.AttackRange)
        {
            _context.GetComponent<StateMachine<EnemyController>>().ChangeState<AttackState>();
            return;
        }
        
        // Check if player is out of detection range
        if (distanceToPlayer > _context.DetectionRange * 1.5f) // Hysteresis
        {
            _context.GetComponent<StateMachine<EnemyController>>().ChangeState<PatrolState>();
            return;
        }
        
        // Continue chasing
        if (_context.Player != null)
        {
            _context.Agent.destination = _context.Player.position;
        }
    }
    
    public override void Exit()
    {
        _context.Animator.SetBool("IsChasing", false);
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### AI-Powered Pattern Recognition and Suggestion
```csharp
// AI system to analyze code and suggest appropriate design patterns
public class AIPatternAnalyzer : MonoBehaviour
{
    [System.Serializable]
    public class CodeAnalysisResult
    {
        public string codeSection;
        public List<string> detectedIssues;
        public List<PatternSuggestion> patternSuggestions;
        public float confidenceScore;
    }
    
    [System.Serializable]
    public class PatternSuggestion
    {
        public string patternName;
        public string reasoning;
        public string implementationExample;
        public int priority;
        public float benefitScore;
    }
    
    public async Task<CodeAnalysisResult> AnalyzeCodeStructure(string codeText)
    {
        var result = new CodeAnalysisResult
        {
            codeSection = codeText,
            detectedIssues = new List<string>(),
            patternSuggestions = new List<PatternSuggestion>()
        };
        
        // AI analysis of code patterns and anti-patterns
        await AnalyzeForSingletonAbuse(result);
        await AnalyzeForObserverPattern(result);
        await AnalyzeForCommandPattern(result);
        await AnalyzeForStatePattern(result);
        await AnalyzeForFactoryPattern(result);
        
        return result;
    }
    
    private async Task AnalyzeForSingletonAbuse(CodeAnalysisResult result)
    {
        // AI detection of singleton anti-patterns
        if (ContainsPattern(result.codeSection, "static.*Instance") && 
            ContainsPattern(result.codeSection, "FindObjectOfType"))
        {
            result.detectedIssues.Add("Potential singleton abuse detected");
            result.patternSuggestions.Add(new PatternSuggestion
            {
                patternName = "Dependency Injection",
                reasoning = "Multiple singletons create tight coupling. Consider dependency injection.",
                implementationExample = GenerateDIExample(),
                priority = 8,
                benefitScore = 0.7f
            });
        }
    }
    
    private async Task AnalyzeForObserverPattern(CodeAnalysisResult result)
    {
        // AI detection of potential observer pattern usage
        if (ContainsPattern(result.codeSection, "OnTriggerEnter") && 
            ContainsPattern(result.codeSection, "SendMessage|BroadcastMessage"))
        {
            result.patternSuggestions.Add(new PatternSuggestion
            {
                patternName = "Observer Pattern (Event System)",
                reasoning = "SendMessage creates tight coupling. Use event system for loose coupling.",
                implementationExample = GenerateEventSystemExample(),
                priority = 9,
                benefitScore = 0.8f
            });
        }
    }
    
    private async Task AnalyzeForCommandPattern(CodeAnalysisResult result)
    {
        // AI detection of input handling that could benefit from command pattern
        if (ContainsPattern(result.codeSection, "Input\\.Get.*Down") && 
            ContainsPattern(result.codeSection, "if.*else.*if"))
        {
            result.patternSuggestions.Add(new PatternSuggestion
            {
                patternName = "Command Pattern",
                reasoning = "Complex input handling detected. Command pattern enables undo/redo and input remapping.",
                implementationExample = GenerateCommandPatternExample(),
                priority = 7,
                benefitScore = 0.6f
            });
        }
    }
    
    private async Task AnalyzeForStatePattern(CodeAnalysisResult result)
    {
        // AI detection of state management anti-patterns
        if (ContainsPattern(result.codeSection, "enum.*State") && 
            ContainsPattern(result.codeSection, "switch.*state"))
        {
            result.patternSuggestions.Add(new PatternSuggestion
            {
                patternName = "State Machine Pattern",
                reasoning = "Large switch statements for state management. State pattern provides better maintainability.",
                implementationExample = GenerateStateMachineExample(),
                priority = 8,
                benefitScore = 0.75f
            });
        }
    }
    
    private async Task AnalyzeForFactoryPattern(CodeAnalysisResult result)
    {
        // AI detection of object creation complexity
        if (ContainsPattern(result.codeSection, "Instantiate.*GameObject") && 
            ContainsPattern(result.codeSection, "GetComponent.*"))
        {
            result.patternSuggestions.Add(new PatternSuggestion
            {
                patternName = "Factory Pattern",
                reasoning = "Complex object instantiation detected. Factory pattern centralizes creation logic.",
                implementationExample = GenerateFactoryPatternExample(),
                priority = 6,
                benefitScore = 0.5f
            });
        }
    }
    
    private bool ContainsPattern(string text, string pattern)
    {
        return System.Text.RegularExpressions.Regex.IsMatch(text, pattern);
    }
    
    private string GenerateDIExample()
    {
        return @"
// Instead of multiple singletons:
public class GameManager : MonoBehaviour
{
    [SerializeField] private AudioManager audioManager;
    [SerializeField] private UIManager uiManager;
    [SerializeField] private SaveManager saveManager;
    
    // Inject dependencies instead of using singletons
    public void Initialize(AudioManager audio, UIManager ui, SaveManager save)
    {
        audioManager = audio;
        uiManager = ui;
        saveManager = save;
    }
}";
    }
    
    private string GenerateEventSystemExample()
    {
        return @"
// Replace SendMessage with event system:
public class PlayerController : MonoBehaviour
{
    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag('Collectible'))
        {
            EventManager.Publish(new ItemCollectedEvent(other.gameObject));
        }
    }
}";
    }
    
    private string GenerateCommandPatternExample()
    {
        return @"
// Replace direct input handling with commands:
public class InputHandler : MonoBehaviour
{
    private CommandManager commandManager;
    
    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space))
            commandManager.ExecuteCommand(new JumpCommand(player));
        if (Input.GetKeyDown(KeyCode.Z) && Input.GetKey(KeyCode.LeftControl))
            commandManager.Undo();
    }
}";
    }
    
    private string GenerateStateMachineExample()
    {
        return @"
// Replace switch statements with state machine:
public class PlayerController : MonoBehaviour
{
    private StateMachine<PlayerController> stateMachine;
    
    private void Start()
    {
        stateMachine = new StateMachine<PlayerController>();
        stateMachine.AddState(new IdleState(this));
        stateMachine.AddState(new MovingState(this));
        stateMachine.AddState(new JumpingState(this));
    }
}";
    }
    
    private string GenerateFactoryPatternExample()
    {
        return @"
// Replace direct instantiation with factory:
public class EnemyFactory : MonoBehaviour
{
    public Enemy CreateEnemy(EnemyType type, Vector3 position)
    {
        GameObject prefab = GetEnemyPrefab(type);
        GameObject instance = Instantiate(prefab, position, Quaternion.identity);
        Enemy enemy = instance.GetComponent<Enemy>();
        enemy.Initialize(GetEnemyData(type));
        return enemy;
    }
}";
    }
}
```

## 💡 Key Pattern Implementation Highlights

### Unity-Specific Considerations
- **Component-Based Architecture**: Adapt patterns to work with Unity's component system
- **Lifecycle Management**: Handle Unity's object creation/destruction lifecycle properly
- **Serialization**: Ensure patterns work with Unity's serialization system
- **Performance**: Optimize patterns for Unity's frame-based execution model

### Anti-Pattern Avoidance
- **Singleton Abuse**: Use dependency injection instead of multiple singletons
- **God Objects**: Break large classes into smaller, focused components
- **Tight Coupling**: Use events and interfaces to reduce dependencies
- **Premature Optimization**: Choose patterns based on actual needs, not speculation

### Modern C# Features Integration
- **Async/Await**: Integrate asynchronous patterns with traditional design patterns
- **Generics**: Use generic implementations for type-safe, reusable patterns
- **Events and Delegates**: Leverage C# events for observer pattern implementations
- **Interfaces and Abstract Classes**: Design flexible, testable pattern implementations

This comprehensive guide provides professional-grade design pattern implementations specifically optimized for Unity game development, enabling scalable and maintainable game architecture.