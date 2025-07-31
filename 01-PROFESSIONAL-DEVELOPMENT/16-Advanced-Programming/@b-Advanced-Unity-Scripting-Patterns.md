# @b-Advanced-Unity-Scripting-Patterns

## 🎯 Learning Objectives
- Master advanced Unity scripting patterns and architectures
- Implement scalable code organization for larger projects
- Apply design patterns specifically for Unity game development
- Create reusable and maintainable game systems

## 🔧 Advanced Unity Patterns

### Singleton Pattern for Game Managers
```csharp
public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }
    
    [SerializeField] private int score;
    [SerializeField] private bool gamePaused;
    
    void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }
        
        Instance = this;
        DontDestroyOnLoad(gameObject);
    }
    
    public void AddScore(int points) => score += points;
    public void PauseGame() => gamePaused = true;
}
```

### Event System Architecture
```csharp
// Event definitions
public static class GameEvents
{
    public static event System.Action<int> OnScoreChanged;
    public static event System.Action<bool> OnGameStateChanged;
    
    public static void ScoreChanged(int newScore) => OnScoreChanged?.Invoke(newScore);
    public static void GameStateChanged(bool isPaused) => OnGameStateChanged?.Invoke(isPaused);
}

// Subscriber example
public class UIManager : MonoBehaviour
{
    void OnEnable()
    {
        GameEvents.OnScoreChanged += UpdateScoreDisplay;
        GameEvents.OnGameStateChanged += UpdatePauseMenu;
    }
    
    void OnDisable()
    {
        GameEvents.OnScoreChanged -= UpdateScoreDisplay;
        GameEvents.OnGameStateChanged -= UpdatePauseMenu;
    }
    
    private void UpdateScoreDisplay(int score) { /* Update UI */ }
    private void UpdatePauseMenu(bool isPaused) { /* Toggle pause menu */ }
}
```

### Object Pool Pattern
```csharp
public class ObjectPool<T> : MonoBehaviour where T : MonoBehaviour
{
    [SerializeField] private T prefab;
    [SerializeField] private int poolSize = 10;
    
    private Queue<T> pool = new Queue<T>();
    
    void Start()
    {
        for (int i = 0; i < poolSize; i++)
        {
            T obj = Instantiate(prefab);
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
        
        return Instantiate(prefab);
    }
    
    public void Return(T obj)
    {
        obj.gameObject.SetActive(false);
        pool.Enqueue(obj);
    }
}
```

### State Machine Pattern
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
    
    public void ChangeState(State newState)
    {
        currentState?.Exit();
        currentState = newState;
        currentState?.Enter();
    }
    
    public void Update() => currentState?.Update();
}

// Usage example
public class PlayerIdleState : State
{
    private PlayerController player;
    
    public PlayerIdleState(PlayerController player) => this.player = player;
    
    public override void Enter() => player.PlayIdleAnimation();
    public override void Update() { /* Check for input transitions */ }
    public override void Exit() { /* Cleanup */ }
}
```

### Command Pattern for Input System
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
    
    public void Undo() => target.position = previousPosition;
}

public class InputHandler : MonoBehaviour
{
    private Stack<ICommand> commandHistory = new Stack<ICommand>();
    
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.W))
        {
            ICommand moveUp = new MoveCommand(transform, Vector3.forward);
            moveUp.Execute();
            commandHistory.Push(moveUp);
        }
        
        if (Input.GetKeyDown(KeyCode.Z) && commandHistory.Count > 0)
        {
            commandHistory.Pop().Undo();
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Pattern Implementation Assistance
```
"Generate a Unity observer pattern implementation for [specific game event]"
"Create a state machine for [character/system] with [specific states]"
"Implement object pooling for [specific game objects] with performance optimization"
```

### Architecture Design
- AI-generated architecture diagrams for Unity systems
- Code review for pattern implementation correctness
- Performance analysis of different pattern approaches

### Advanced Code Generation
- Custom Unity editor tools using advanced patterns
- Automated pattern refactoring suggestions
- Integration patterns for third-party Unity assets

## 💡 Key Highlights

### Pattern Selection Guidelines
- **Singleton**: Game managers, audio managers, persistent data
- **Observer**: UI updates, game events, achievement systems
- **Object Pool**: Bullets, enemies, particle effects
- **State Machine**: AI behavior, game states, animation control
- **Command**: Input handling, undo systems, replay functionality

### Performance Considerations
- Event subscription/unsubscription in OnEnable/OnDisable
- Proper cleanup in singleton implementations
- Memory-efficient object pooling strategies
- State machine update optimization

### Unity-Specific Optimizations
- Use Unity events vs C# events appropriately
- Leverage Unity's component system with patterns
- Consider Unity's Job System for heavy computations
- Implement patterns with Unity's serialization in mind

### Common Anti-Patterns to Avoid
- Overuse of singletons (singleton hell)
- Complex inheritance hierarchies
- Tight coupling between systems
- Update-heavy implementations

These advanced patterns form the backbone of professional Unity development and enable creation of maintainable, scalable game systems.