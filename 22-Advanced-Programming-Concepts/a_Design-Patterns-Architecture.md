# @a-Design-Patterns-Architecture - Software Design Patterns & Architectural Principles

## 🎯 Learning Objectives
- Master essential design patterns used in Unity and C# development
- Understand architectural principles for scalable game development
- Apply SOLID principles and clean architecture concepts
- Leverage AI tools to identify and implement optimal design patterns

## 🔧 Core Design Patterns for Unity Development

### Creational Patterns

#### Singleton Pattern
```csharp
public class GameManager : MonoBehaviour
{
    private static GameManager _instance;
    public static GameManager Instance
    {
        get
        {
            if (_instance == null)
                _instance = FindObjectOfType<GameManager>();
            return _instance;
        }
    }
    
    private void Awake()
    {
        if (_instance != null && _instance != this)
            Destroy(this.gameObject);
        else
            _instance = this;
    }
}
```

#### Object Pool Pattern
```csharp
public class ObjectPool<T> where T : MonoBehaviour
{
    private Queue<T> pool = new Queue<T>();
    private T prefab;
    
    public ObjectPool(T prefab, int initialSize = 10)
    {
        this.prefab = prefab;
        for (int i = 0; i < initialSize; i++)
        {
            T obj = Object.Instantiate(prefab);
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
        return Object.Instantiate(prefab);
    }
    
    public void Return(T obj)
    {
        obj.gameObject.SetActive(false);
        pool.Enqueue(obj);
    }
}
```

### Behavioral Patterns

#### Observer Pattern (Unity Events)
```csharp
using UnityEngine;
using UnityEngine.Events;

public class HealthSystem : MonoBehaviour
{
    [System.Serializable]
    public class HealthEvent : UnityEvent<int> { }
    
    public HealthEvent OnHealthChanged;
    public UnityEvent OnDeath;
    
    private int currentHealth = 100;
    
    public void TakeDamage(int damage)
    {
        currentHealth -= damage;
        OnHealthChanged?.Invoke(currentHealth);
        
        if (currentHealth <= 0)
            OnDeath?.Invoke();
    }
}
```

#### Command Pattern
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
```

#### State Machine Pattern
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
    
    public void Update()
    {
        currentState?.Update();
    }
}

// Player states
public class IdleState : State
{
    public override void Enter() { /* Setup idle animation */ }
    public override void Update() { /* Check for input transitions */ }
    public override void Exit() { /* Cleanup */ }
}
```

### Structural Patterns

#### Component Pattern (Unity's Core)
```csharp
// Unity's component system is built on this pattern
public class PlayerController : MonoBehaviour
{
    private Rigidbody rb;
    private Animator animator;
    
    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
        animator = GetComponent<Animator>();
    }
}
```

#### Facade Pattern
```csharp
public class AudioManager : MonoBehaviour
{
    private AudioSource musicSource;
    private AudioSource sfxSource;
    
    public void PlayMusic(AudioClip clip) => musicSource.PlayOneShot(clip);
    public void PlaySFX(AudioClip clip) => sfxSource.PlayOneShot(clip);
    public void SetMusicVolume(float volume) => musicSource.volume = volume;
    public void SetSFXVolume(float volume) => sfxSource.volume = volume;
}
```

## 🏗️ Architectural Principles

### SOLID Principles in Unity

#### Single Responsibility Principle
```csharp
// BAD: Multiple responsibilities
public class Player : MonoBehaviour
{
    public void Move() { /* Movement logic */ }
    public void Shoot() { /* Shooting logic */ }
    public void UpdateUI() { /* UI logic */ }
    public void SaveGame() { /* Save logic */ }
}

// GOOD: Separated responsibilities
public class PlayerMovement : MonoBehaviour { /* Only movement */ }
public class PlayerCombat : MonoBehaviour { /* Only combat */ }
public class UIController : MonoBehaviour { /* Only UI */ }
public class SaveSystem : MonoBehaviour { /* Only saving */ }
```

#### Open/Closed Principle
```csharp
public abstract class Weapon : MonoBehaviour
{
    public abstract void Fire();
}

public class Pistol : Weapon
{
    public override void Fire() { /* Pistol firing logic */ }
}

public class Rifle : Weapon
{
    public override void Fire() { /* Rifle firing logic */ }
}
```

#### Dependency Inversion Principle
```csharp
public interface IInputHandler
{
    Vector2 GetMovementInput();
    bool GetJumpInput();
}

public class KeyboardInput : IInputHandler
{
    public Vector2 GetMovementInput() => new Vector2(Input.GetAxis("Horizontal"), Input.GetAxis("Vertical"));
    public bool GetJumpInput() => Input.GetKeyDown(KeyCode.Space);
}

public class PlayerController : MonoBehaviour
{
    private IInputHandler inputHandler;
    
    private void Start()
    {
        inputHandler = GetComponent<IInputHandler>();
    }
}
```

### Clean Architecture for Games

#### Game Architecture Layers
```csharp
// Domain Layer (Core Game Logic)
public class GameRules
{
    public bool CanPlayerMove(Vector3 position) { /* Game rules logic */ }
    public int CalculateScore(int kills, int time) { /* Scoring logic */ }
}

// Application Layer (Use Cases)
public class PlayerMoveUseCase
{
    private GameRules gameRules;
    
    public bool Execute(Vector3 newPosition)
    {
        return gameRules.CanPlayerMove(newPosition);
    }
}

// Infrastructure Layer (Unity-specific)
public class UnityPlayerController : MonoBehaviour
{
    private PlayerMoveUseCase moveUseCase;
    
    private void Update()
    {
        Vector3 targetPosition = transform.position + GetInput();
        if (moveUseCase.Execute(targetPosition))
            transform.position = targetPosition;
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Design Pattern Recognition and Implementation
```
PROMPT: "Analyze this Unity C# code and suggest appropriate design patterns:
[paste code]

Consider:
- Current code structure and responsibilities
- Potential scalability issues
- Unity-specific constraints
- Performance implications
- Maintenance and testability improvements"
```

### Architecture Review and Optimization
```
PROMPT: "Review this game architecture for a [game type] and suggest improvements:
[describe current architecture]

Focus on:
- SOLID principle violations
- Coupling and cohesion issues
- Unity-specific performance patterns
- Scalability for team development
- Testing and debugging considerations"
```

### Pattern Implementation Assistance
```
PROMPT: "Implement a [specific pattern] for Unity that handles [specific requirement]:
- Show the interface/abstract class design
- Provide a concrete implementation example
- Include Unity-specific considerations
- Add comments explaining the pattern benefits
- Suggest testing approaches"
```

## 💡 Key Highlights

### Essential Patterns for Unity Development
- **Singleton**: Game managers, audio systems, UI controllers
- **Object Pool**: Bullets, enemies, particles, UI elements
- **Observer**: Health systems, achievements, UI updates
- **Command**: Input handling, undo systems, replay functionality
- **State Machine**: AI behavior, player states, game flow
- **Component**: Unity's core architecture pattern

### Architecture Best Practices
- **Separation of Concerns**: Keep game logic separate from Unity-specific code
- **Dependency Injection**: Use interfaces to reduce coupling
- **Event-Driven Architecture**: Leverage Unity's event system for loose coupling
- **Modular Design**: Create reusable, testable components
- **Performance Patterns**: Object pooling, efficient update patterns

### Common Anti-Patterns to Avoid
- **God Objects**: Massive scripts handling everything
- **Tight Coupling**: Direct references everywhere
- **Singleton Abuse**: Using singletons for everything
- **Update Overhead**: Too many Update() calls
- **Memory Leaks**: Forgotten event subscriptions

### AI-Enhanced Development Workflow
1. **Pattern Recognition**: Use AI to identify code smells and suggest patterns
2. **Implementation Generation**: Generate boilerplate pattern implementations
3. **Architecture Review**: Regular AI-assisted architecture assessments
4. **Refactoring Assistance**: AI-guided refactoring for better patterns
5. **Documentation**: Auto-generate pattern documentation and usage examples

This comprehensive understanding of design patterns and architecture principles will enable you to build scalable, maintainable Unity projects while leveraging AI tools to accelerate the development process and ensure best practices are consistently applied.