# @d-Unity-Component-System-Architecture

## 🎯 Learning Objectives
- Master Unity's component-based architecture and composition patterns
- Design flexible and reusable component systems
- Implement proper component communication and dependency management
- Create modular systems that scale with project complexity

## 🔧 Component Architecture Fundamentals

### Component Composition Pattern
```csharp
// Base component interface
public interface IComponent
{
    GameObject GameObject { get; }
    bool Enabled { get; set; }
    void Initialize();
    void Cleanup();
}

// Modular health system
public class Health : MonoBehaviour, IComponent
{
    [SerializeField] private float maxHealth = 100f;
    [SerializeField] private float currentHealth;
    
    public float MaxHealth => maxHealth;
    public float CurrentHealth => currentHealth;
    public float HealthPercentage => currentHealth / maxHealth;
    
    public event System.Action<float> OnHealthChanged;
    public event System.Action OnDeath;
    
    public void Initialize()
    {
        currentHealth = maxHealth;
    }
    
    public void TakeDamage(float damage)
    {
        currentHealth = Mathf.Max(0, currentHealth - damage);
        OnHealthChanged?.Invoke(currentHealth);
        
        if (currentHealth <= 0)
        {
            OnDeath?.Invoke();
        }
    }
    
    public void Heal(float amount)
    {
        currentHealth = Mathf.Min(maxHealth, currentHealth + amount);
        OnHealthChanged?.Invoke(currentHealth);
    }
    
    public void Cleanup()
    {
        OnHealthChanged = null;
        OnDeath = null;
    }
}

// Movement component
public class Movement : MonoBehaviour, IComponent
{
    [SerializeField] private float speed = 5f;
    [SerializeField] private float rotationSpeed = 180f;
    
    private Rigidbody rb;
    private Vector3 movementInput;
    
    public void Initialize()
    {
        rb = GetComponent<Rigidbody>();
        if (rb == null)
        {
            rb = gameObject.AddComponent<Rigidbody>();
        }
    }
    
    public void SetMovementInput(Vector3 input)
    {
        movementInput = input.normalized;
    }
    
    void FixedUpdate()
    {
        if (movementInput != Vector3.zero)
        {
            // Move
            rb.MovePosition(transform.position + movementInput * speed * Time.fixedDeltaTime);
            
            // Rotate towards movement direction
            Quaternion targetRotation = Quaternion.LookRotation(movementInput);
            transform.rotation = Quaternion.RotateTowards(
                transform.rotation, 
                targetRotation, 
                rotationSpeed * Time.fixedDeltaTime
            );
        }
    }
    
    public void Cleanup() { }
}
```

### Component Manager System
```csharp
public class ComponentManager : MonoBehaviour
{
    private readonly Dictionary<System.Type, IComponent> components = new Dictionary<System.Type, IComponent>();
    private readonly List<IComponent> allComponents = new List<IComponent>();
    
    void Awake()
    {
        // Auto-register all components on this GameObject
        RegisterAllComponents();
        InitializeComponents();
    }
    
    private void RegisterAllComponents()
    {
        IComponent[] foundComponents = GetComponents<IComponent>();
        
        foreach (IComponent component in foundComponents)
        {
            System.Type componentType = component.GetType();
            components[componentType] = component;
            allComponents.Add(component);
        }
    }
    
    private void InitializeComponents()
    {
        foreach (IComponent component in allComponents)
        {
            component.Initialize();
        }
    }
    
    public T GetComponent<T>() where T : class, IComponent
    {
        components.TryGetValue(typeof(T), out IComponent component);
        return component as T;
    }
    
    public bool HasComponent<T>() where T : class, IComponent
    {
        return components.ContainsKey(typeof(T));
    }
    
    void OnDestroy()
    {
        foreach (IComponent component in allComponents)
        {
            component.Cleanup();
        }
    }
}
```

### Component Communication System
```csharp
// Message system for loose coupling
public interface IMessage { }

public struct DamageMessage : IMessage
{
    public float damage;
    public Vector3 source;
    public string damageType;
}

public struct HealMessage : IMessage
{
    public float healAmount;
    public string healType;
}

public class MessageBus : MonoBehaviour
{
    private readonly Dictionary<System.Type, List<System.Action<IMessage>>> subscribers = 
        new Dictionary<System.Type, List<System.Action<IMessage>>>();
    
    public void Subscribe<T>(System.Action<T> handler) where T : IMessage
    {
        System.Type messageType = typeof(T);
        
        if (!subscribers.ContainsKey(messageType))
        {
            subscribers[messageType] = new List<System.Action<IMessage>>();
        }
        
        subscribers[messageType].Add(message => handler((T)message));
    }
    
    public void Unsubscribe<T>(System.Action<T> handler) where T : IMessage
    {
        System.Type messageType = typeof(T);
        
        if (subscribers.ContainsKey(messageType))
        {
            subscribers[messageType].RemoveAll(h => h.Method == handler.Method);
        }
    }
    
    public void Publish<T>(T message) where T : IMessage
    {
        System.Type messageType = typeof(T);
        
        if (subscribers.ContainsKey(messageType))
        {
            foreach (var handler in subscribers[messageType])
            {
                handler(message);
            }
        }
    }
}

// Component using message system
public class CombatComponent : MonoBehaviour, IComponent
{
    private Health healthComponent;
    private MessageBus messageBus;
    
    public void Initialize()
    {
        healthComponent = GetComponent<Health>();
        messageBus = FindObjectOfType<MessageBus>();
        
        // Subscribe to messages
        messageBus.Subscribe<DamageMessage>(HandleDamage);
        messageBus.Subscribe<HealMessage>(HandleHeal);
    }
    
    private void HandleDamage(DamageMessage message)
    {
        if (healthComponent != null)
        {
            healthComponent.TakeDamage(message.damage);
        }
    }
    
    private void HandleHeal(HealMessage message)
    {
        if (healthComponent != null)
        {
            healthComponent.Heal(message.healAmount);
        }
    }
    
    public void Cleanup()
    {
        messageBus?.Unsubscribe<DamageMessage>(HandleDamage);
        messageBus?.Unsubscribe<HealMessage>(HandleHeal);
    }
}
```

### Dependency Injection for Components
```csharp
// Service locator pattern for Unity
public class ServiceLocator : MonoBehaviour
{
    private static ServiceLocator instance;
    private readonly Dictionary<System.Type, object> services = new Dictionary<System.Type, object>();
    
    public static ServiceLocator Instance
    {
        get
        {
            if (instance == null)
            {
                instance = FindObjectOfType<ServiceLocator>();
                if (instance == null)
                {
                    GameObject go = new GameObject("ServiceLocator");
                    instance = go.AddComponent<ServiceLocator>();
                    DontDestroyOnLoad(go);
                }
            }
            return instance;
        }
    }
    
    public void RegisterService<T>(T service)
    {
        services[typeof(T)] = service;
    }
    
    public T GetService<T>()
    {
        services.TryGetValue(typeof(T), out object service);
        return (T)service;
    }
    
    public bool HasService<T>()
    {
        return services.ContainsKey(typeof(T));
    }
}

// Component with dependencies
public class AIController : MonoBehaviour, IComponent
{
    private IPathfinding pathfinding;
    private ITargetingSystem targeting;
    private Movement movement;
    
    public void Initialize()
    {
        // Inject dependencies
        pathfinding = ServiceLocator.Instance.GetService<IPathfinding>();
        targeting = ServiceLocator.Instance.GetService<ITargetingSystem>();
        movement = GetComponent<Movement>();
    }
    
    void Update()
    {
        if (pathfinding != null && targeting != null)
        {
            Transform target = targeting.GetNearestTarget(transform.position);
            if (target != null)
            {
                Vector3[] path = pathfinding.FindPath(transform.position, target.position);
                if (path.Length > 1)
                {
                    Vector3 direction = (path[1] - transform.position).normalized;
                    movement.SetMovementInput(direction);
                }
            }
        }
    }
    
    public void Cleanup() { }
}
```

### ScriptableObject-Based Component Data
```csharp
[CreateAssetMenu(fileName = "New Character Stats", menuName = "Game/Character Stats")]
public class CharacterStats : ScriptableObject
{
    [Header("Base Stats")]
    public float maxHealth = 100f;
    public float speed = 5f;
    public float attackDamage = 25f;
    public float defense = 10f;
    
    [Header("Combat Settings")]
    public float attackRange = 2f;
    public float attackCooldown = 1f;
    
    [Header("AI Behavior")]
    public float detectionRadius = 10f;
    public float chaseSpeed = 7f;
}

// Component using ScriptableObject data
public class CharacterController : MonoBehaviour, IComponent
{
    [SerializeField] private CharacterStats stats;
    
    private Health health;
    private Movement movement;
    private Combat combat;
    
    public void Initialize()
    {
        // Initialize components with ScriptableObject data
        health = GetComponent<Health>();
        movement = GetComponent<Movement>();
        combat = GetComponent<Combat>();
        
        if (health != null)
        {
            health.Initialize(stats.maxHealth);
        }
        
        if (movement != null)
        {
            movement.SetSpeed(stats.speed);
        }
        
        if (combat != null)
        {
            combat.Initialize(stats.attackDamage, stats.attackRange, stats.attackCooldown);
        }
    }
    
    public void Cleanup() { }
}
```

## 🚀 AI/LLM Integration Opportunities

### Component Architecture Design
```
"Design a component system for [game feature] with proper separation of concerns"
"Generate component interfaces for [specific game mechanic]"
"Create a modular system for [gameplay element] using Unity components"
```

### Code Generation
- AI-generated component templates
- Automated dependency injection setup
- Component communication pattern implementation

### Architecture Analysis
- Component coupling analysis
- Performance impact assessment of component designs
- Best practice recommendations for component organization

## 💡 Key Highlights

### Component Design Principles
- **Single Responsibility**: Each component handles one concern
- **Loose Coupling**: Components communicate through interfaces/messages
- **High Cohesion**: Related functionality grouped together
- **Composition over Inheritance**: Favor component composition

### Communication Patterns
- **Direct Reference**: For tightly coupled, performance-critical systems
- **Event System**: For loose coupling and one-to-many relationships
- **Message Bus**: For complex, decoupled communication
- **Service Locator**: For shared services and dependencies

### Performance Considerations
- Component caching for frequently accessed components
- Minimize Update() methods across components
- Use object pooling for dynamic component creation
- Batch component operations where possible

### Common Architecture Patterns
- **Entity-Component-System (ECS)**: For performance-critical applications
- **Component Manager**: Central component coordination
- **Service Locator**: Dependency management
- **Observer Pattern**: Event-driven component communication

### Best Practices
- Initialize components in proper order
- Handle component dependencies gracefully
- Provide clear component interfaces
- Document component interactions
- Test components in isolation

This component architecture foundation enables creation of maintainable, scalable Unity systems that can grow with project complexity.