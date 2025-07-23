# @b-Scripting - Unity MonoBehaviour & C# Integration

## 🎯 Learning Objectives
- Master MonoBehaviour lifecycle and event functions
- Understand Unity's scripting API and component communication
- Learn input handling, coroutines, and Unity-specific C# features
- Use AI tools to generate and optimize Unity scripts

---

## 🔧 MonoBehaviour Lifecycle

### Core Event Functions (Execution Order)

```csharp
public class PlayerController : MonoBehaviour
{
    void Awake()    { /* Called when object is instantiated */ }
    void OnEnable() { /* Called when GameObject becomes active */ }
    void Start()    { /* Called before first frame, after all Awakes */ }
    
    void Update()      { /* Called every frame (frame-dependent) */ }
    void FixedUpdate() { /* Called at fixed intervals (physics) */ }
    void LateUpdate()  { /* Called after all Updates (camera follow) */ }
    
    void OnDisable() { /* Called when GameObject becomes inactive */ }
    void OnDestroy() { /* Called when object is destroyed */ }
}
```

### When to Use Each Function
- **Awake**: Initialize variables, get component references
- **Start**: Initialize objects that depend on other objects being ready
- **Update**: Input handling, UI updates, non-physics movement
- **FixedUpdate**: Physics calculations, Rigidbody manipulation
- **LateUpdate**: Camera following, UI elements that track world objects

---

## 🎮 Input Handling

### Legacy Input System

```csharp
void Update()
{
    // Keyboard input
    if (Input.GetKeyDown(KeyCode.Space))
        Jump();
    
    // Mouse input
    if (Input.GetMouseButtonDown(0))
        Shoot();
    
    // Axis input (smooth)
    float horizontal = Input.GetAxis("Horizontal");
    float vertical = Input.GetAxis("Vertical");
    
    Vector3 movement = new Vector3(horizontal, 0, vertical);
    transform.Translate(movement * speed * Time.deltaTime);
}
```

### New Input System (Recommended)

```csharp
using UnityEngine.InputSystem;

public class PlayerController : MonoBehaviour
{
    [SerializeField] private InputActionReference moveAction;
    [SerializeField] private InputActionReference jumpAction;
    
    void OnEnable()
    {
        jumpAction.action.performed += OnJump;
    }
    
    void OnDisable()
    {
        jumpAction.action.performed -= OnJump;
    }
    
    void Update()
    {
        Vector2 moveInput = moveAction.action.ReadValue<Vector2>();
        // Process movement
    }
    
    private void OnJump(InputAction.CallbackContext context)
    {
        if (context.performed)
            Jump();
    }
}
```

---

## 🔗 Component Communication

### Getting Components

```csharp
// Same GameObject
Rigidbody rb = GetComponent<Rigidbody>();
PlayerHealth health = GetComponent<PlayerHealth>();

// Child GameObjects
Transform childTransform = GetComponentInChildren<Transform>();
Renderer[] renderers = GetComponentsInChildren<Renderer>();

// Parent GameObjects
Canvas parentCanvas = GetComponentInParent<Canvas>();

// Find by name/tag (avoid in Update - expensive)
GameObject player = GameObject.FindWithTag("Player");
GameObject enemy = GameObject.Find("EnemyManager");
```

### Component References (Performance Best Practice)

```csharp
public class PlayerController : MonoBehaviour
{
    [SerializeField] private Rigidbody playerRb;
    [SerializeField] private Animator playerAnimator;
    [SerializeField] private AudioSource audioSource;
    
    void Awake()
    {
        // Cache components in Awake, not every frame
        if (playerRb == null)
            playerRb = GetComponent<Rigidbody>();
    }
}
```

---

## ⏰ Coroutines & Async Operations

### Basic Coroutine Pattern

```csharp
// Start coroutine
StartCoroutine(DelayedAction(2.0f));
```
// Coroutine method
IEnumerator DelayedAction(float delay)
{
    Debug.Log("Starting action...");
    yield return new WaitForSeconds(delay);
    Debug.Log("Action completed!");
}

// Complex coroutine with conditions
IEnumerator SpawnEnemiesOverTime()
{
    while (gameActive)
    {
        SpawnEnemy();
        yield return new WaitForSeconds(spawnInterval);
        
        if (enemyCount >= maxEnemies)
            yield break; // Exit coroutine
    }
}
```

```csharp
hello
```

### Common Yield Instructions

```csharp
yield return null;                          // Wait one frame
yield return new WaitForSeconds(1.0f);      // Wait for time
yield return new WaitForFixedUpdate();      // Wait for next physics update
yield return new WaitUntil(() => isReady);  // Wait for condition
yield return StartCoroutine(OtherCoroutine()); // Wait for another coroutine
```

---

## 🚀 AI/LLM Integration for Scripting

### Code Generation Prompts
**Basic Script Generation:**
> "Create a Unity script for a platform character controller with ground detection, jumping, and horizontal movement using Rigidbody"

**Advanced Patterns:**
> "Generate a Unity object pooling system for bullets with automatic return-to-pool after 3 seconds"

**Optimization Reviews:**
> "Review this Unity script for performance issues and suggest improvements: [paste your code]"

### AI-Assisted Debugging

```csharp
// Use AI to explain error messages and suggest fixes
// Example: "NullReferenceException in Unity GetComponent - what are common causes?"
```

### Script Templates with AI
- Generate singleton patterns for managers
- Create state machines for AI behavior
- Build event system architectures
- Generate UI controller boilerplate

---

## 🎯 Common Unity Scripting Patterns

### Singleton Pattern (Game Manager)

```csharp
public class GameManager : MonoBehaviour
{
    public static GameManager Instance;
    
    void Awake()
    {
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
}
```

### Object Pooling

```csharp
public class ObjectPool : MonoBehaviour
{
    [SerializeField] private GameObject prefab;
    [SerializeField] private int poolSize = 10;
    
    private Queue<GameObject> pool = new Queue<GameObject>();
    
    void Start()
    {
        for (int i = 0; i < poolSize; i++)
        {
            GameObject obj = Instantiate(prefab);
            obj.SetActive(false);
            pool.Enqueue(obj);
        }
    }
    
    public GameObject GetFromPool()
    {
        if (pool.Count > 0)
        {
            GameObject obj = pool.Dequeue();
            obj.SetActive(true);
            return obj;
        }
        return Instantiate(prefab); // Fallback if pool empty
    }
    
    public void ReturnToPool(GameObject obj)
    {
        obj.SetActive(false);
        pool.Enqueue(obj);
    }
}
```

### Events and Actions

```csharp
public class PlayerHealth : MonoBehaviour
{
    public static event System.Action<int> OnHealthChanged;
    public static event System.Action OnPlayerDeath;
    
    [SerializeField] private int health = 100;
    
    public void TakeDamage(int damage)
    {
        health -= damage;
        OnHealthChanged?.Invoke(health); // Notify UI
        
        if (health <= 0)
        {
            OnPlayerDeath?.Invoke(); // Notify Game Manager
        }
    }
}
```

Subscriber class:

```csharp
public class UIManager : MonoBehaviour
{
    void OnEnable()
    {
        PlayerHealth.OnHealthChanged += UpdateHealthBar;
        PlayerHealth.OnPlayerDeath += ShowGameOverScreen;
    }
    
    void OnDisable()
    {
        PlayerHealth.OnHealthChanged -= UpdateHealthBar;
        PlayerHealth.OnPlayerDeath -= ShowGameOverScreen;
    }
}
```

---

## 🎮 Practical Exercises

### Exercise 1: Movement Controller
Create a character controller with:
- WASD movement using Rigidbody
- Jump with ground detection
- Smooth camera follow using LateUpdate()

### Exercise 2: Interactive Objects
Build an interaction system:
- Raycast from camera for object detection
- Highlight objects on hover
- Trigger actions on click/key press

### Exercise 3: Game Manager with Events
Implement:
- Score tracking with UI updates
- Game state management (Playing, Paused, GameOver)
- Event-driven architecture for loose coupling

---

## 🎯 Portfolio Project Ideas

### Beginner: "Input Demo Showcase"
- Demonstrate different input methods
- Show smooth vs. immediate response
- Include mobile touch controls

### Intermediate: "System Architecture Demo"
- Object pooling system
- Event-driven UI updates
- Modular component communication

### Advanced: "Performance Optimization Case Study"
- Before/after optimization comparison
- Profiler screenshots showing improvements
- Detailed explanation of techniques used

---

## 🔍 Interview Preparation

### Common Questions
1. **"Explain the difference between Update and FixedUpdate"**
   - Update: Frame-dependent, varies with FPS, use for input/UI
   - FixedUpdate: Fixed timestep, consistent for physics

2. **"How do you optimize script performance?"**
   - Cache component references
   - Avoid expensive operations in Update
   - Use object pooling instead of Instantiate/Destroy

3. **"What's the difference between Awake and Start?"**
   - Awake: Called immediately when object created
   - Start: Called before first frame, after all Awakes complete

### Code Challenges
Practice implementing:
- Character controllers from scratch
- Component communication systems
- Performance-optimized update loops
- Coroutine-based state machines

---

## ⚡ AI Productivity Hacks

### Script Generation Workflow
1. **Describe requirements** to AI in detail
2. **Generate base script** with proper Unity patterns
3. **Optimize and customize** with AI assistance
4. **Add documentation** automatically

### Learning Acceleration
- Generate practice exercises with increasing difficulty
- Create code review checklists
- Build personal script template library
- Generate unit tests for Unity components

### Portfolio Enhancement
- AI-generated script documentation
- Automatic README generation for projects
- Performance analysis reports
- Code architecture explanations

---

## 🎯 Next Steps
1. Practice these scripting patterns in simple test projects
2. Build a modular character controller using these concepts
3. Move to **@c-Physics-Animation.md** for physics integration
4. Create a "Unity Scripting Cheatsheet" for interview prep

> **AI Integration Reminder**: Use LLMs to generate boilerplate code, explain complex patterns, and create practice exercises. Focus on understanding the patterns rather than memorizing syntax!