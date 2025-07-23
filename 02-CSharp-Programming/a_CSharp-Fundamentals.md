# C# Fundamentals for Unity Development

## Overview
Master essential C# programming concepts specifically applied to Unity game development and professional software engineering.

## Key Concepts

### Core Language Syntax
**Variable Declaration and Types:**
- Value types (int, float, bool, char, struct)
- Reference types (class, string, array, object)
- Nullable types (int?, float?) for optional values
- Implicit typing with var keyword

**Control Flow Structures:**
- Conditional statements (if/else, switch/case)
- Loops (for, foreach, while, do-while)
- Exception handling (try/catch/finally)
- Pattern matching with switch expressions

### Object-Oriented Programming

**Classes and Objects:**
```csharp
public class Player
{
    public string Name { get; set; }
    private int health = 100;
    
    public void TakeDamage(int damage)
    {
        health -= damage;
        if (health <= 0) Die();
    }
}
```

**Inheritance and Polymorphism:**
- Base classes and derived classes
- Virtual and override methods
- Abstract classes and interfaces
- Method overloading and overriding

### Unity-Specific C# Patterns

**MonoBehaviour Lifecycle:**
- Awake() vs Start() initialization
- Update() vs FixedUpdate() vs LateUpdate()
- OnEnable/OnDisable for component activation
- OnDestroy() for cleanup operations

**Property Patterns:**
```csharp
[SerializeField] private float speed = 5f;
public float Speed 
{ 
    get => speed; 
    set => speed = Mathf.Max(0, value); 
}
```

## Practical Applications

### Memory Management
**Reference vs Value Types:**
- Structs are value types (copied by value)
- Classes are reference types (copied by reference)
- Understanding stack vs heap allocation
- Garbage collection impact on performance

**Unity-Specific Memory Considerations:**
- Avoid frequent allocations in Update()
- Use object pooling for frequently created objects
- Minimize string concatenation in loops
- Prefer StringBuilder for multiple string operations

### Common Unity Patterns

**Singleton Pattern:**
```csharp
public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else Destroy(gameObject);
    }
}
```

**Observer Pattern with Events:**
```csharp
public static event System.Action<int> OnScoreChanged;
public static event System.Action OnPlayerDied;

// Trigger events
OnScoreChanged?.Invoke(newScore);
OnPlayerDied?.Invoke();
```

## Interview Preparation

### Common Questions

**"Explain the difference between value types and reference types"**
- Value types store data directly, copied by value
- Reference types store memory addresses, copied by reference
- Impact on performance and memory allocation

**"What's the difference between Awake() and Start()?"**
- Awake() called when object instantiated (before Start)
- Start() called before first frame update
- Awake() used for internal initialization, Start() for setup requiring other objects

**"How do you handle null references safely?"**
- Null-conditional operators (?. and ?[])
- Null-coalescing operators (?? and ??=)
- Null checking before operations

### Key Takeaways

**Essential C# Features for Unity:**
- Strong typing with implicit var when appropriate
- LINQ for collections manipulation
- Async/await for asynchronous operations
- Properties with getters/setters for encapsulation

**Performance Considerations:**
- Minimize allocations in frequently called methods
- Use appropriate collection types (List vs Array)
- Understand boxing/unboxing overhead
- Implement proper disposal patterns with IDisposable