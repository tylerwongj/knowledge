# Unity-Specific C# Programming

## Overview
Advanced C# techniques and patterns specifically optimized for Unity game development and performance.

## Key Concepts

### Unity Component System
**MonoBehaviour Architecture:**
- Component-based entity system design
- GameObject-Component relationship patterns
- Communication between components via GetComponent<>()
- Component lifecycle and execution order

**Script Execution Order:**
- Awake() for internal setup before any Start()
- Start() for initialization requiring other objects
- Update() for per-frame logic (framerate dependent)
- FixedUpdate() for physics and fixed timestep operations
- LateUpdate() for camera and follow logic after all Updates

### Performance-Critical Programming

**Avoiding Garbage Collection:**
```csharp
// Bad - creates garbage every frame
void Update()
{
    string text = "Score: " + score.ToString();
}

// Good - reuse objects and minimize allocations
private StringBuilder scoreText = new StringBuilder();
void UpdateScoreDisplay()
{
    scoreText.Clear();
    scoreText.Append("Score: ");
    scoreText.Append(score);
}
```

**Object Pooling Pattern:**
```csharp
public class BulletPool : MonoBehaviour
{
    private Queue<GameObject> bulletPool = new Queue<GameObject>();
    [SerializeField] private GameObject bulletPrefab;
    [SerializeField] private int poolSize = 50;
    
    void Start()
    {
        for (int i = 0; i < poolSize; i++)
        {
            GameObject bullet = Instantiate(bulletPrefab);
            bullet.SetActive(false);
            bulletPool.Enqueue(bullet);
        }
    }
    
    public GameObject GetBullet()
    {
        if (bulletPool.Count > 0)
        {
            GameObject bullet = bulletPool.Dequeue();
            bullet.SetActive(true);
            return bullet;
        }
        return Instantiate(bulletPrefab);
    }
    
    public void ReturnBullet(GameObject bullet)
    {
        bullet.SetActive(false);
        bulletPool.Enqueue(bullet);
    }
}
```

### Unity-Specific Data Structures

**ScriptableObjects for Data:**
```csharp
[CreateAssetMenu(fileName = "New Weapon", menuName = "Game/Weapon")]
public class WeaponData : ScriptableObject
{
    public string weaponName;
    public int damage;
    public float fireRate;
    public GameObject projectilePrefab;
}
```

**Serialization Attributes:**
- [SerializeField] for private field exposure
- [HideInInspector] to hide public fields
- [Header("Section")] for organization
- [Range(min, max)] for slider controls

### Event System Implementation

**Unity Events vs C# Events:**
```csharp
// C# Events (better performance)
public static event System.Action<float> OnHealthChanged;
public static event System.Action OnPlayerDeath;

// UnityEvents (Inspector assignable)
[System.Serializable]
public class HealthEvent : UnityEvent<float> { }
public HealthEvent onHealthChanged;
```

**Event Manager Pattern:**
```csharp
public class EventManager : MonoBehaviour
{
    public static EventManager Instance;
    
    public event System.Action<int> OnScoreChanged;
    public event System.Action<string> OnLevelComplete;
    
    void Awake()
    {
        if (Instance == null) Instance = this;
        else Destroy(gameObject);
    }
    
    public void TriggerScoreChange(int newScore)
    {
        OnScoreChanged?.Invoke(newScore);
    }
}
```

## Practical Applications

### Coroutines and Async Programming

**Coroutine Usage Patterns:**
```csharp
// Timed operations
IEnumerator DelayedAction(float delay, System.Action action)
{
    yield return new WaitForSeconds(delay);
    action?.Invoke();
}

// Frame-based operations
IEnumerator MoveOverTime(Transform target, Vector3 destination, float duration)
{
    Vector3 startPos = target.position;
    float elapsed = 0;
    
    while (elapsed < duration)
    {
        elapsed += Time.deltaTime;
        float t = elapsed / duration;
        target.position = Vector3.Lerp(startPos, destination, t);
        yield return null;
    }
}
```

**Async/Await in Unity:**
```csharp
using System.Threading.Tasks;

public async Task LoadSceneAsync(string sceneName)
{
    var operation = SceneManager.LoadSceneAsync(sceneName);
    operation.allowSceneActivation = false;
    
    while (operation.progress < 0.9f)
    {
        await Task.Yield();
    }
    
    operation.allowSceneActivation = true;
    await Task.Delay(100); // Small delay before completion
}
```

### Memory Management Strategies

**Cache Component References:**
```csharp
public class Player : MonoBehaviour
{
    private Rigidbody rb;
    private Animator animator;
    private AudioSource audioSource;
    
    void Awake()
    {
        rb = GetComponent<Rigidbody>();
        animator = GetComponent<Animator>();
        audioSource = GetComponent<AudioSource>();
    }
}
```

**Proper Disposal Patterns:**
```csharp
public class NetworkManager : MonoBehaviour, System.IDisposable
{
    private NetworkClient client;
    
    void OnDestroy()
    {
        Dispose();
    }
    
    public void Dispose()
    {
        client?.Disconnect();
        client?.Dispose();
    }
}
```

## Interview Preparation

### Technical Questions

**"How do you optimize C# code for Unity?"**
- Minimize garbage collection through object pooling
- Cache component references instead of frequent GetComponent calls
- Use appropriate Update methods (Update vs FixedUpdate)
- Implement proper disposal patterns for resources

**"Explain the difference between Coroutines and async/await"**
- Coroutines run on main thread, good for frame-based operations
- Async/await can run on background threads, better for I/O operations
- Coroutines integrated with Unity lifecycle, async requires careful thread handling

**"How do you handle communication between GameObjects?"**
- Events for loose coupling between systems
- Direct references for tightly coupled components
- Singleton managers for global state
- Message passing through event managers

### Key Takeaways

**Unity C# Best Practices:**
- Use appropriate Unity-specific patterns (MonoBehaviour, ScriptableObjects)
- Optimize for performance with object pooling and caching
- Implement proper event systems for decoupled architecture
- Handle memory management and garbage collection carefully

**Professional Development Patterns:**
- Separate data from behavior using ScriptableObjects
- Use dependency injection for testable code
- Implement proper error handling and logging
- Follow SOLID principles adapted for Unity's component system