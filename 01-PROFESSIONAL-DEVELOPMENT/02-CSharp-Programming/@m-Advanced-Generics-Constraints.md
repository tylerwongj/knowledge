# @m-Advanced-Generics-Constraints

## 🎯 Learning Objectives

- Master advanced generic programming techniques in C#
- Implement complex constraint combinations for type safety
- Create reusable generic systems for Unity game development
- Optimize generic code for performance and memory efficiency

## 🔧 Core Generic Constraints

### Basic Constraint Types

```csharp
// Class constraint - T must be reference type
public class Repository<T> where T : class
{
    private readonly List<T> items = new List<T>();
    
    public void Add(T item)
    {
        if (item != null) // Safe null check for reference types
            items.Add(item);
    }
}

// Struct constraint - T must be value type
public struct Optional<T> where T : struct
{
    private readonly T value;
    private readonly bool hasValue;
    
    public Optional(T value)
    {
        this.value = value;
        this.hasValue = true;
    }
    
    public T GetValueOrDefault(T defaultValue = default)
    {
        return hasValue ? value : defaultValue;
    }
}

// New constraint - T must have parameterless constructor
public class Factory<T> where T : new()
{
    public T Create()
    {
        return new T();
    }
    
    public T[] CreateArray(int count)
    {
        T[] array = new T[count];
        for (int i = 0; i < count; i++)
        {
            array[i] = new T();
        }
        return array;
    }
}
```

### Multiple Constraints

```csharp
// Multiple constraints with inheritance
public interface IGameEntity
{
    string Name { get; set; }
    Vector3 Position { get; set; }
}

public class Component : MonoBehaviour { }

// T must inherit from Component, implement IGameEntity, and have parameterless constructor
public class EntityManager<T> : MonoBehaviour 
    where T : Component, IGameEntity, new()
{
    private readonly Dictionary<string, T> entities = new Dictionary<string, T>();
    
    public T CreateEntity(string name, Vector3 position)
    {
        T entity = new T();
        entity.Name = name;
        entity.Position = position;
        
        entities[name] = entity;
        return entity;
    }
    
    public T GetEntity(string name)
    {
        return entities.TryGetValue(name, out T entity) ? entity : null;
    }
}
```

## 🎮 Unity-Specific Generic Patterns

### Generic Object Pool System

```csharp
public interface IPoolable
{
    void OnPoolGet();
    void OnPoolReturn();
}

public class ObjectPool<T> : MonoBehaviour where T : MonoBehaviour, IPoolable
{
    [SerializeField] private T prefab;
    [SerializeField] private int initialCapacity = 10;
    [SerializeField] private int maxCapacity = 100;
    
    private readonly Queue<T> pool = new Queue<T>();
    private readonly HashSet<T> activeObjects = new HashSet<T>();
    
    void Start()
    {
        InitializePool();
    }
    
    private void InitializePool()
    {
        for (int i = 0; i < initialCapacity; i++)
        {
            CreatePooledObject();
        }
    }
    
    private T CreatePooledObject()
    {
        T obj = Instantiate(prefab, transform);
        obj.gameObject.SetActive(false);
        pool.Enqueue(obj);
        return obj;
    }
    
    public T Get()
    {
        T obj;
        
        if (pool.Count > 0)
        {
            obj = pool.Dequeue();
        }
        else if (activeObjects.Count < maxCapacity)
        {
            obj = CreatePooledObject();
        }
        else
        {
            return null; // Pool exhausted
        }
        
        obj.gameObject.SetActive(true);
        obj.OnPoolGet();
        activeObjects.Add(obj);
        
        return obj;
    }
    
    public void Return(T obj)
    {
        if (!activeObjects.Contains(obj)) return;
        
        obj.OnPoolReturn();
        obj.gameObject.SetActive(false);
        activeObjects.Remove(obj);
        pool.Enqueue(obj);
    }
    
    public void ReturnAll()
    {
        var objectsToReturn = new List<T>(activeObjects);
        foreach (T obj in objectsToReturn)
        {
            Return(obj);
        }
    }
}

// Example usage
public class Bullet : MonoBehaviour, IPoolable
{
    private Rigidbody rb;
    private float lifetime = 5f;
    
    void Awake()
    {
        rb = GetComponent<Rigidbody>();
    }
    
    public void OnPoolGet()
    {
        rb.velocity = Vector3.zero;
        StartCoroutine(ReturnToPoolAfterTime());
    }
    
    public void OnPoolReturn()
    {
        StopAllCoroutines();
    }
    
    private IEnumerator ReturnToPoolAfterTime()
    {
        yield return new WaitForSeconds(lifetime);
        FindObjectOfType<ObjectPool<Bullet>>().Return(this);
    }
    
    public void Fire(Vector3 direction, float speed)
    {
        rb.velocity = direction * speed;
    }
}
```

### Generic State Machine

```csharp
public interface IState<T>
{
    void Enter(T context);
    void Update(T context);
    void Exit(T context);
}

public class StateMachine<TContext, TState> 
    where TState : class, IState<TContext>
{
    private TContext context;
    private TState currentState;
    private readonly Dictionary<Type, TState> states = new Dictionary<Type, TState>();
    
    public StateMachine(TContext context)
    {
        this.context = context;
    }
    
    public void AddState<T>(T state) where T : class, TState
    {
        states[typeof(T)] = state;
    }
    
    public void ChangeState<T>() where T : class, TState
    {
        Type stateType = typeof(T);
        
        if (!states.TryGetValue(stateType, out TState newState))
        {
            Debug.LogError($"State {stateType.Name} not found in state machine");
            return;
        }
        
        currentState?.Exit(context);
        currentState = newState;
        currentState.Enter(context);
    }
    
    public void Update()
    {
        currentState?.Update(context);
    }
    
    public T GetCurrentState<T>() where T : class, TState
    {
        return currentState as T;
    }
    
    public bool IsInState<T>() where T : class, TState
    {
        return currentState is T;
    }
}

// Example AI States
public class AIController : MonoBehaviour
{
    private StateMachine<AIController, AIState> stateMachine;
    
    public Transform target;
    public float detectionRange = 10f;
    public float attackRange = 2f;
    
    void Start()
    {
        stateMachine = new StateMachine<AIController, AIState>(this);
        stateMachine.AddState(new IdleState());
        stateMachine.AddState(new ChaseState());
        stateMachine.AddState(new AttackState());
        stateMachine.ChangeState<IdleState>();
    }
    
    void Update()
    {
        stateMachine.Update();
    }
    
    public float DistanceToTarget => target != null ? 
        Vector3.Distance(transform.position, target.position) : float.MaxValue;
}

public abstract class AIState : IState<AIController>
{
    public abstract void Enter(AIController context);
    public abstract void Update(AIController context);
    public abstract void Exit(AIController context);
}

public class IdleState : AIState
{
    public override void Enter(AIController context)
    {
        Debug.Log("Entering Idle State");
    }
    
    public override void Update(AIController context)
    {
        if (context.DistanceToTarget <= context.detectionRange)
        {
            context.GetComponent<StateMachine<AIController, AIState>>()?.ChangeState<ChaseState>();
        }
    }
    
    public override void Exit(AIController context)
    {
        Debug.Log("Exiting Idle State");
    }
}

public class ChaseState : AIState
{
    public override void Enter(AIController context)
    {
        Debug.Log("Entering Chase State");
    }
    
    public override void Update(AIController context)
    {
        if (context.DistanceToTarget > context.detectionRange)
        {
            // Lost target
            return; // Transition to idle
        }
        
        if (context.DistanceToTarget <= context.attackRange)
        {
            // Close enough to attack
            return; // Transition to attack
        }
        
        // Move towards target
        Vector3 direction = (context.target.position - context.transform.position).normalized;
        context.transform.position += direction * 5f * Time.deltaTime;
    }
    
    public override void Exit(AIController context)
    {
        Debug.Log("Exiting Chase State");
    }
}

public class AttackState : AIState
{
    private float attackCooldown = 1f;
    private float lastAttackTime;
    
    public override void Enter(AIController context)
    {
        Debug.Log("Entering Attack State");
        lastAttackTime = Time.time;
    }
    
    public override void Update(AIController context)
    {
        if (context.DistanceToTarget > context.attackRange)
        {
            // Target moved away
            return; // Transition to chase
        }
        
        if (Time.time - lastAttackTime >= attackCooldown)
        {
            PerformAttack(context);
            lastAttackTime = Time.time;
        }
    }
    
    public override void Exit(AIController context)
    {
        Debug.Log("Exiting Attack State");
    }
    
    private void PerformAttack(AIController context)
    {
        Debug.Log("Attacking!");
        // Attack logic here
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Automated Generic Code Generation

```
Generate Unity C# generic systems for:
1. Event system with type-safe callbacks and constraints
2. Data serialization system with Unity-compatible constraints
3. Component dependency injection with interface constraints
4. Performance monitoring system with measurable type constraints

Requirements: Unity 2022.3 LTS compatibility, zero-allocation patterns
Context: High-performance game development with strict memory requirements
```

### Advanced Constraint Pattern Analysis

```
Analyze and optimize these generic constraint patterns:
1. Multiple inheritance with interface constraints for ECS systems
2. Covariance/contravariance with Unity component hierarchies
3. Generic method constraints for builder patterns in Unity
4. Performance implications of constraint combinations in hot paths

Focus: Memory allocation, runtime performance, compile-time optimization
```

## 💡 Advanced Constraint Patterns

### Covariance and Contravariance

```csharp
// Covariant interface - can return more derived types
public interface IProducer<out T>
{
    T Produce();
    IEnumerable<T> ProduceMany();
}

// Contravariant interface - can accept more base types
public interface IConsumer<in T>
{
    void Consume(T item);
    void ConsumeMany(IEnumerable<T> items);
}

// Invariant interface - must be exact type
public interface IStorage<T>
{
    T Get(int index);
    void Set(int index, T item);
}

// Example implementation
public class WeaponFactory : IProducer<Weapon>
{
    public Weapon Produce()
    {
        return Random.value > 0.5f ? new Sword() : new Bow();
    }
    
    public IEnumerable<Weapon> ProduceMany()
    {
        for (int i = 0; i < 10; i++)
        {
            yield return Produce();
        }
    }
}

public class Inventory : IConsumer<Item>
{
    private readonly List<Item> items = new List<Item>();
    
    public void Consume(Item item)
    {
        items.Add(item);
    }
    
    public void ConsumeMany(IEnumerable<Item> newItems)
    {
        items.AddRange(newItems);
    }
}

// Usage demonstrating variance
public class GameManager : MonoBehaviour
{
    void Start()
    {
        // Covariance: can assign IProducer<Weapon> to IProducer<Item>
        IProducer<Item> itemProducer = new WeaponFactory();
        
        // Contravariance: can assign IConsumer<Item> to IConsumer<Weapon>
        IConsumer<Weapon> weaponConsumer = new Inventory();
        
        // Use them together
        foreach (Item item in itemProducer.ProduceMany())
        {
            if (item is Weapon weapon)
                weaponConsumer.Consume(weapon);
        }
    }
}
```

### Recursive Generic Constraints

```csharp
// Self-referencing constraint for fluent interfaces
public interface IBuilder<TSelf> where TSelf : IBuilder<TSelf>
{
    TSelf SetProperty(string name, object value);
}

public class GameObjectBuilder : IBuilder<GameObjectBuilder>
{
    private GameObject gameObject;
    private readonly Dictionary<string, object> properties = new Dictionary<string, object>();
    
    public GameObjectBuilder(string name)
    {
        gameObject = new GameObject(name);
    }
    
    public GameObjectBuilder SetProperty(string name, object value)
    {
        properties[name] = value;
        return this;
    }
    
    public GameObjectBuilder AddComponent<T>() where T : Component
    {
        gameObject.AddComponent<T>();
        return this;
    }
    
    public GameObjectBuilder SetPosition(Vector3 position)
    {
        gameObject.transform.position = position;
        return this;
    }
    
    public GameObjectBuilder SetRotation(Quaternion rotation)
    {
        gameObject.transform.rotation = rotation;
        return this;
    }
    
    public GameObject Build()
    {
        // Apply properties to components
        foreach (var property in properties)
        {
            ApplyProperty(property.Key, property.Value);
        }
        return gameObject;
    }
    
    private void ApplyProperty(string name, object value)
    {
        // Property application logic
    }
}

// Usage
public class GameSetup : MonoBehaviour
{
    void Start()
    {
        GameObject player = new GameObjectBuilder("Player")
            .SetPosition(Vector3.zero)
            .SetRotation(Quaternion.identity)
            .AddComponent<CharacterController>()
            .AddComponent<PlayerController>()
            .SetProperty("health", 100)
            .SetProperty("speed", 5f)
            .Build();
    }
}
```

### Conditional Constraints with Interfaces

```csharp
// Marker interfaces for different capabilities
public interface IDamageable
{
    float Health { get; set; }
    void TakeDamage(float damage);
}

public interface IMovable
{
    Vector3 Position { get; set; }
    void MoveTo(Vector3 target);
}

public interface IInteractable
{
    void Interact(GameObject interactor);
}

// Generic system that works with combinations of interfaces
public class EntitySystem<T> where T : MonoBehaviour
{
    protected readonly List<T> entities = new List<T>();
    
    public void Register(T entity)
    {
        entities.Add(entity);
    }
    
    public void Unregister(T entity)
    {
        entities.Remove(entity);
    }
    
    // Method only available if T implements IDamageable
    public void DamageAll(float damage) where T : IDamageable
    {
        foreach (T entity in entities)
        {
            entity.TakeDamage(damage);
        }
    }
    
    // Method only available if T implements IMovable
    public void MoveAllTo(Vector3 target) where T : IMovable
    {
        foreach (T entity in entities)
        {
            entity.MoveTo(target);
        }
    }
    
    // Method available if T implements both IDamageable and IMovable
    public void FleeFromDamage(Vector3 damageSource, float damageAmount) 
        where T : IDamageable, IMovable
    {
        foreach (T entity in entities)
        {
            entity.TakeDamage(damageAmount);
            Vector3 fleeDirection = (entity.Position - damageSource).normalized;
            entity.MoveTo(entity.Position + fleeDirection * 5f);
        }
    }
}

// Specialized systems
public class EnemySystem : EntitySystem<Enemy>
{
    public void UpdateAI()
    {
        foreach (Enemy enemy in entities)
        {
            enemy.UpdateBehavior();
        }
    }
}

public class NPCSystem : EntitySystem<NPC>
{
    public void ProcessDialogue()
    {
        foreach (NPC npc in entities)
        {
            npc.ProcessConversation();
        }
    }
}

// Example entities
public class Enemy : MonoBehaviour, IDamageable, IMovable
{
    public float Health { get; set; } = 100f;
    public Vector3 Position { get; set; }
    
    public void TakeDamage(float damage)
    {
        Health -= damage;
        if (Health <= 0) Die();
    }
    
    public void MoveTo(Vector3 target)
    {
        Position = target;
        transform.position = target;
    }
    
    public void UpdateBehavior()
    {
        // AI logic
    }
    
    private void Die()
    {
        Destroy(gameObject);
    }
}
```

## 🔥 Performance-Optimized Generic Patterns

### Zero-Allocation Generic Collections

```csharp
public struct ReadOnlySpan<T> where T : struct
{
    private readonly T[] array;
    private readonly int start;
    private readonly int length;
    
    public ReadOnlySpan(T[] array, int start, int length)
    {
        this.array = array;
        this.start = start;
        this.length = length;
    }
    
    public int Length => length;
    
    public T this[int index]
    {
        get
        {
            if (index < 0 || index >= length)
                throw new IndexOutOfRangeException();
            return array[start + index];
        }
    }
    
    public ReadOnlySpan<T> Slice(int start, int length)
    {
        if (start < 0 || start + length > this.length)
            throw new ArgumentOutOfRangeException();
        
        return new ReadOnlySpan<T>(array, this.start + start, length);
    }
    
    public Enumerator GetEnumerator() => new Enumerator(this);
    
    public struct Enumerator
    {
        private readonly ReadOnlySpan<T> span;
        private int index;
        
        public Enumerator(ReadOnlySpan<T> span)
        {
            this.span = span;
            index = -1;
        }
        
        public T Current => span[index];
        
        public bool MoveNext()
        {
            return ++index < span.Length;
        }
    }
}

// Usage in performance-critical systems
public class ParticleSystem<TParticle> : MonoBehaviour 
    where TParticle : struct, IParticle
{
    private TParticle[] particles;
    private int activeCount;
    
    public ReadOnlySpan<TParticle> ActiveParticles => 
        new ReadOnlySpan<TParticle>(particles, 0, activeCount);
    
    public void UpdateParticles()
    {
        var activeParticles = ActiveParticles;
        
        // Zero-allocation iteration
        for (int i = 0; i < activeParticles.Length; i++)
        {
            var particle = activeParticles[i];
            particle.Update(Time.deltaTime);
            particles[i] = particle; // Copy back if modified
        }
    }
}

public interface IParticle
{
    void Update(float deltaTime);
    bool IsAlive { get; }
}

public struct FireParticle : IParticle
{
    public Vector3 position;
    public Vector3 velocity;
    public float life;
    public float maxLife;
    
    public bool IsAlive => life > 0f;
    
    public void Update(float deltaTime)
    {
        life -= deltaTime;
        position += velocity * deltaTime;
        velocity += Vector3.down * 9.81f * deltaTime; // Gravity
    }
}
```

### Generic Component Caching

```csharp
public static class ComponentCache<T> where T : Component
{
    private static readonly Dictionary<GameObject, T> cache = new Dictionary<GameObject, T>();
    
    public static T Get(GameObject gameObject)
    {
        if (cache.TryGetValue(gameObject, out T component))
        {
            // Verify component still exists (object might have been destroyed)
            if (component != null) return component;
            cache.Remove(gameObject);
        }
        
        component = gameObject.GetComponent<T>();
        if (component != null)
        {
            cache[gameObject] = component;
        }
        
        return component;
    }
    
    public static bool TryGet(GameObject gameObject, out T component)
    {
        component = Get(gameObject);
        return component != null;
    }
    
    public static void Clear()
    {
        cache.Clear();
    }
    
    public static void Remove(GameObject gameObject)
    {
        cache.Remove(gameObject);
    }
}

// Usage in performance-critical systems
public class CombatSystem : MonoBehaviour
{
    private readonly List<GameObject> combatants = new List<GameObject>();
    
    void Update()
    {
        // Fast component access without repeated GetComponent calls
        foreach (GameObject combatant in combatants)
        {
            if (ComponentCache<Health>.TryGet(combatant, out Health health))
            {
                if (health.CurrentHealth <= 0)
                {
                    HandleDeath(combatant);
                }
            }
            
            if (ComponentCache<Weapon>.TryGet(combatant, out Weapon weapon))
            {
                weapon.UpdateCooldown();
            }
        }
    }
    
    private void HandleDeath(GameObject combatant)
    {
        combatants.Remove(combatant);
        ComponentCache<Health>.Remove(combatant);
        ComponentCache<Weapon>.Remove(combatant);
    }
}
```

This comprehensive guide covers advanced generic programming techniques specifically tailored for Unity game development, focusing on type safety, performance optimization, and maintainable code architecture.