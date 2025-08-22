# @u-Unity-Scripting-Best-Practices-Professional

## 🎯 Learning Objectives

- Master professional Unity scripting patterns and conventions
- Implement scalable architecture for large game projects
- Optimize script performance for production environments
- Establish maintainable code practices for team development

## 🔧 Core Scripting Principles

### Script Organization and Naming

```csharp
// File: PlayerController.cs
// Namespace convention: CompanyName.ProjectName.SubSystem
namespace AcmeGames.SpaceAdventure.Player
{
    /// <summary>
    /// Handles player input and character movement
    /// </summary>
    [RequireComponent(typeof(CharacterController))]
    [RequireComponent(typeof(PlayerInput))]
    public class PlayerController : MonoBehaviour
    {
        #region Serialized Fields
        [Header("Movement Settings")]
        [SerializeField] private float moveSpeed = 5f;
        [SerializeField] private float jumpHeight = 2f;
        [SerializeField] private float gravity = -9.81f;
        
        [Header("Ground Check")]
        [SerializeField] private Transform groundCheck;
        [SerializeField] private float groundDistance = 0.4f;
        [SerializeField] private LayerMask groundMask;
        #endregion
        
        #region Private Fields
        private CharacterController controller;
        private PlayerInput playerInput;
        private Vector3 velocity;
        private bool isGrounded;
        
        // Cache frequently accessed components
        private Camera playerCamera;
        private Animator playerAnimator;
        #endregion
        
        #region Public Properties
        public bool IsMoving => velocity.magnitude > 0.1f;
        public float CurrentSpeed => velocity.magnitude;
        public Vector3 MoveDirection { get; private set; }
        #endregion
        
        #region Unity Lifecycle
        private void Awake()
        {
            // Initialize required components
            controller = GetComponent<CharacterController>();
            playerInput = GetComponent<PlayerInput>();
            
            // Cache components for performance
            playerCamera = Camera.main;
            playerAnimator = GetComponent<Animator>();
        }
        
        private void Start()
        {
            // Subscribe to input events
            playerInput.MoveAction.performed += OnMove;
            playerInput.JumpAction.performed += OnJump;
        }
        
        private void Update()
        {
            HandleGroundCheck();
            HandleMovement();
            HandleGravity();
            UpdateAnimations();
        }
        
        private void OnDestroy()
        {
            // Unsubscribe from events to prevent memory leaks
            if (playerInput != null)
            {
                playerInput.MoveAction.performed -= OnMove;
                playerInput.JumpAction.performed -= OnJump;
            }
        }
        #endregion
        
        #region Movement Logic
        private void HandleGroundCheck()
        {
            isGrounded = Physics.CheckSphere(groundCheck.position, groundDistance, groundMask);
            
            if (isGrounded && velocity.y < 0)
            {
                velocity.y = -2f; // Small negative value to keep grounded
            }
        }
        
        private void HandleMovement()
        {
            Vector2 input = playerInput.MoveAction.ReadValue<Vector2>();
            
            // Calculate movement direction relative to camera
            Vector3 forward = playerCamera.transform.forward;
            Vector3 right = playerCamera.transform.right;
            
            forward.y = 0f;
            right.y = 0f;
            
            forward.Normalize();
            right.Normalize();
            
            MoveDirection = forward * input.y + right * input.x;
            
            // Apply movement
            controller.Move(MoveDirection * moveSpeed * Time.deltaTime);
        }
        
        private void HandleGravity()
        {
            velocity.y += gravity * Time.deltaTime;
            controller.Move(velocity * Time.deltaTime);
        }
        
        private void OnMove(InputAction.CallbackContext context)
        {
            // Handle move input events if needed
        }
        
        private void OnJump(InputAction.CallbackContext context)
        {
            if (isGrounded)
            {
                velocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
            }
        }
        #endregion
        
        #region Animation Updates
        private void UpdateAnimations()
        {
            if (playerAnimator == null) return;
            
            playerAnimator.SetFloat("Speed", CurrentSpeed);
            playerAnimator.SetBool("IsGrounded", isGrounded);
            playerAnimator.SetFloat("VerticalVelocity", velocity.y);
        }
        #endregion
        
        #region Debug and Gizmos
        private void OnDrawGizmosSelected()
        {
            if (groundCheck != null)
            {
                Gizmos.color = isGrounded ? Color.green : Color.red;
                Gizmos.DrawWireSphere(groundCheck.position, groundDistance);
            }
        }
        #endregion
    }
}
```

### Dependency Injection Pattern

```csharp
// Service interfaces
public interface IHealthService
{
    void TakeDamage(float amount);
    void Heal(float amount);
    float CurrentHealth { get; }
    float MaxHealth { get; }
}

public interface IAudioService
{
    void PlaySound(AudioClip clip, Vector3 position);
    void PlayMusic(AudioClip music, bool loop = true);
    void StopMusic();
}

public interface IInventoryService
{
    bool AddItem(Item item);
    bool RemoveItem(Item item);
    bool HasItem(string itemId);
    T GetItem<T>(string itemId) where T : Item;
}

// Service locator for dependency injection
public class ServiceLocator : MonoBehaviour
{
    private static ServiceLocator instance;
    private readonly Dictionary<Type, object> services = new Dictionary<Type, object>();
    
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
        Type serviceType = typeof(T);
        
        if (services.ContainsKey(serviceType))
        {
            Debug.LogWarning($"Service {serviceType.Name} is already registered");
            return;
        }
        
        services[serviceType] = service;
        Debug.Log($"Registered service: {serviceType.Name}");
    }
    
    public T GetService<T>()
    {
        Type serviceType = typeof(T);
        
        if (services.TryGetValue(serviceType, out object service))
        {
            return (T)service;
        }
        
        Debug.LogError($"Service {serviceType.Name} not found");
        return default(T);
    }
    
    public bool HasService<T>()
    {
        return services.ContainsKey(typeof(T));
    }
}

// Usage in dependent classes
public class PlayerCombat : MonoBehaviour
{
    private IHealthService healthService;
    private IAudioService audioService;
    private IInventoryService inventoryService;
    
    private void Start()
    {
        // Inject dependencies
        healthService = ServiceLocator.Instance.GetService<IHealthService>();
        audioService = ServiceLocator.Instance.GetService<IAudioService>();
        inventoryService = ServiceLocator.Instance.GetService<IInventoryService>();
        
        // Validate dependencies
        if (healthService == null || audioService == null || inventoryService == null)
        {
            Debug.LogError("Required services not found!");
            enabled = false;
        }
    }
    
    public void TakeDamage(float damage, Vector3 damagePosition)
    {
        healthService.TakeDamage(damage);
        audioService.PlaySound(damageSound, damagePosition);
        
        // Check for special items that reduce damage
        if (inventoryService.HasItem("armor"))
        {
            var armor = inventoryService.GetItem<Armor>("armor");
            // Apply armor reduction
        }
    }
}
```

## 🎮 Performance-Optimized Patterns

### Object Pooling with Generic Support

```csharp
public interface IPoolable
{
    void OnSpawn();
    void OnDespawn();
    bool IsActive { get; }
}

public class ObjectPool<T> : MonoBehaviour where T : MonoBehaviour, IPoolable
{
    [SerializeField] private T prefab;
    [SerializeField] private int initialSize = 20;
    [SerializeField] private int maxSize = 100;
    [SerializeField] private bool allowGrowth = true;
    
    private readonly Queue<T> availableObjects = new Queue<T>();
    private readonly HashSet<T> allObjects = new HashSet<T>();
    private Transform poolParent;
    
    private void Awake()
    {
        CreatePoolParent();
        InitializePool();
    }
    
    private void CreatePoolParent()
    {
        poolParent = new GameObject($"{typeof(T).Name}_Pool").transform;
        poolParent.SetParent(transform);
    }
    
    private void InitializePool()
    {
        for (int i = 0; i < initialSize; i++)
        {
            CreateNewObject();
        }
    }
    
    private T CreateNewObject()
    {
        T obj = Instantiate(prefab, poolParent);
        obj.gameObject.SetActive(false);
        allObjects.Add(obj);
        availableObjects.Enqueue(obj);
        return obj;
    }
    
    public T Get()
    {
        T obj = null;
        
        // Try to get from available objects
        while (availableObjects.Count > 0)
        {
            obj = availableObjects.Dequeue();
            if (obj != null) break;
        }
        
        // Create new object if needed and allowed
        if (obj == null)
        {
            if (allowGrowth && allObjects.Count < maxSize)
            {
                obj = CreateNewObject();
                availableObjects.Dequeue(); // Remove the one we just added
            }
            else
            {
                Debug.LogWarning($"Pool for {typeof(T).Name} is exhausted!");
                return null;
            }
        }
        
        obj.gameObject.SetActive(true);
        obj.OnSpawn();
        return obj;
    }
    
    public void Return(T obj)
    {
        if (obj == null || !allObjects.Contains(obj)) return;
        
        obj.OnDespawn();
        obj.gameObject.SetActive(false);
        obj.transform.SetParent(poolParent);
        availableObjects.Enqueue(obj);
    }
    
    public void ReturnAll()
    {
        foreach (T obj in allObjects)
        {
            if (obj != null && obj.IsActive)
            {
                Return(obj);
            }
        }
    }
    
    public void PreWarm(int count)
    {
        count = Mathf.Min(count, maxSize - allObjects.Count);
        
        for (int i = 0; i < count; i++)
        {
            CreateNewObject();
        }
    }
    
    #region Debug Info
    [System.Diagnostics.Conditional("UNITY_EDITOR")]
    private void Update()
    {
        // Only in editor for debugging
        name = $"{typeof(T).Name}_Pool (Active: {allObjects.Count - availableObjects.Count}/{allObjects.Count})";
    }
    #endregion
}

// Example poolable object
public class Bullet : MonoBehaviour, IPoolable
{
    [SerializeField] private float speed = 10f;
    [SerializeField] private float lifetime = 5f;
    [SerializeField] private LayerMask hitLayers;
    
    private Rigidbody rb;
    private Collider col;
    private TrailRenderer trail;
    private float spawnTime;
    
    public bool IsActive => gameObject.activeInHierarchy;
    
    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
        col = GetComponent<Collider>();
        trail = GetComponent<TrailRenderer>();
    }
    
    public void OnSpawn()
    {
        spawnTime = Time.time;
        if (trail != null) trail.Clear();
        col.enabled = true;
    }
    
    public void OnDespawn()
    {
        rb.velocity = Vector3.zero;
        rb.angularVelocity = Vector3.zero;
        col.enabled = false;
    }
    
    public void Fire(Vector3 direction)
    {
        rb.velocity = direction * speed;
        transform.forward = direction;
    }
    
    private void Update()
    {
        if (Time.time - spawnTime >= lifetime)
        {
            ReturnToPool();
        }
    }
    
    private void OnTriggerEnter(Collider other)
    {
        if (((1 << other.gameObject.layer) & hitLayers) != 0)
        {
            // Handle hit logic here
            ReturnToPool();
        }
    }
    
    private void ReturnToPool()
    {
        FindObjectOfType<ObjectPool<Bullet>>()?.Return(this);
    }
}
```

### Event System with Type Safety

```csharp
// Generic event system
public static class EventSystem
{
    private static readonly Dictionary<Type, List<Delegate>> eventDictionary = 
        new Dictionary<Type, List<Delegate>>();
    
    public static void Subscribe<T>(System.Action<T> listener) where T : struct
    {
        Type eventType = typeof(T);
        
        if (!eventDictionary.ContainsKey(eventType))
        {
            eventDictionary[eventType] = new List<Delegate>();
        }
        
        eventDictionary[eventType].Add(listener);
    }
    
    public static void Unsubscribe<T>(System.Action<T> listener) where T : struct
    {
        Type eventType = typeof(T);
        
        if (eventDictionary.TryGetValue(eventType, out List<Delegate> delegates))
        {
            delegates.Remove(listener);
            
            if (delegates.Count == 0)
            {
                eventDictionary.Remove(eventType);
            }
        }
    }
    
    public static void Publish<T>(T eventData) where T : struct
    {
        Type eventType = typeof(T);
        
        if (eventDictionary.TryGetValue(eventType, out List<Delegate> delegates))
        {
            foreach (Delegate del in delegates.ToList()) // ToList to avoid modification during iteration
            {
                try
                {
                    ((System.Action<T>)del).Invoke(eventData);
                }
                catch (System.Exception ex)
                {
                    Debug.LogError($"Error in event handler for {eventType.Name}: {ex.Message}");
                }
            }
        }
    }
    
    public static void Clear()
    {
        eventDictionary.Clear();
    }
    
    public static void Clear<T>() where T : struct
    {
        Type eventType = typeof(T);
        eventDictionary.Remove(eventType);
    }
}

// Event data structures
public struct PlayerHealthChangedEvent
{
    public float OldHealth;
    public float NewHealth;
    public float MaxHealth;
    public GameObject Player;
}

public struct EnemyDefeatedEvent
{
    public GameObject Enemy;
    public Vector3 Position;
    public int Experience;
    public int Gold;
}

public struct LevelCompletedEvent
{
    public int LevelIndex;
    public float CompletionTime;
    public int Score;
    public bool NewRecord;
}

// Usage example
public class PlayerHealth : MonoBehaviour
{
    [SerializeField] private float maxHealth = 100f;
    private float currentHealth;
    
    public float CurrentHealth => currentHealth;
    public float MaxHealth => maxHealth;
    
    private void Start()
    {
        currentHealth = maxHealth;
    }
    
    public void TakeDamage(float damage)
    {
        float oldHealth = currentHealth;
        currentHealth = Mathf.Max(0f, currentHealth - damage);
        
        // Publish health changed event
        EventSystem.Publish(new PlayerHealthChangedEvent
        {
            OldHealth = oldHealth,
            NewHealth = currentHealth,
            MaxHealth = maxHealth,
            Player = gameObject
        });
        
        if (currentHealth <= 0f)
        {
            Die();
        }
    }
    
    public void Heal(float amount)
    {
        float oldHealth = currentHealth;
        currentHealth = Mathf.Min(maxHealth, currentHealth + amount);
        
        EventSystem.Publish(new PlayerHealthChangedEvent
        {
            OldHealth = oldHealth,
            NewHealth = currentHealth,
            MaxHealth = maxHealth,
            Player = gameObject
        });
    }
    
    private void Die()
    {
        // Handle death logic
        Debug.Log("Player died!");
    }
}

// Event listener example
public class UIHealthBar : MonoBehaviour
{
    [SerializeField] private Slider healthSlider;
    [SerializeField] private Text healthText;
    
    private void OnEnable()
    {
        EventSystem.Subscribe<PlayerHealthChangedEvent>(OnPlayerHealthChanged);
    }
    
    private void OnDisable()
    {
        EventSystem.Unsubscribe<PlayerHealthChangedEvent>(OnPlayerHealthChanged);
    }
    
    private void OnPlayerHealthChanged(PlayerHealthChangedEvent eventData)
    {
        float healthPercentage = eventData.NewHealth / eventData.MaxHealth;
        healthSlider.value = healthPercentage;
        healthText.text = $"{eventData.NewHealth:F0} / {eventData.MaxHealth:F0}";
        
        // Visual feedback for damage
        if (eventData.NewHealth < eventData.OldHealth)
        {
            StartCoroutine(FlashRed());
        }
    }
    
    private IEnumerator FlashRed()
    {
        Image fill = healthSlider.fillRect.GetComponent<Image>();
        Color originalColor = fill.color;
        fill.color = Color.red;
        
        yield return new WaitForSeconds(0.1f);
        
        fill.color = originalColor;
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Automated Code Analysis Prompts

```
Analyze this Unity C# script for:
1. Performance bottlenecks and optimization opportunities
2. Memory allocation patterns and GC pressure points
3. Threading safety and potential race conditions
4. Code maintainability and SOLID principle adherence

Context: Production Unity game targeting 60fps on mobile devices
Requirements: Specific actionable recommendations with code examples
```

### Architecture Pattern Generation

```
Generate Unity C# code for:
1. Observer pattern implementation for game events with type safety
2. Command pattern for undo/redo system in level editor
3. Strategy pattern for different AI behaviors with scriptable objects
4. Factory pattern for weapon/item generation system

Focus: Clean architecture, unit testability, performance optimization
Environment: Unity 2022.3 LTS, C# 9.0 features
```

## 💡 Advanced Scripting Patterns

### Scriptable Object Architecture

```csharp
// Base scriptable object for game data
public abstract class GameData : ScriptableObject
{
    [SerializeField] protected string id;
    [SerializeField] protected string displayName;
    [SerializeField, TextArea(3, 5)] protected string description;
    
    public string ID => id;
    public string DisplayName => displayName;
    public string Description => description;
    
    protected virtual void OnValidate()
    {
        if (string.IsNullOrEmpty(id))
        {
            id = name.ToLower().Replace(" ", "_");
        }
    }
}

// Weapon data scriptable object
[CreateAssetMenu(fileName = "New Weapon", menuName = "Game Data/Weapon")]
public class WeaponData : GameData
{
    [Header("Combat Stats")]
    [SerializeField] private float damage = 10f;
    [SerializeField] private float attackSpeed = 1f;
    [SerializeField] private float range = 1f;
    [SerializeField] private WeaponType weaponType;
    
    [Header("Audio")]
    [SerializeField] private AudioClip attackSound;
    [SerializeField] private AudioClip hitSound;
    
    [Header("Visual Effects")]
    [SerializeField] private GameObject muzzleFlashPrefab;
    [SerializeField] private GameObject hitEffectPrefab;
    
    public float Damage => damage;
    public float AttackSpeed => attackSpeed;
    public float Range => range;
    public WeaponType Type => weaponType;
    public AudioClip AttackSound => attackSound;
    public AudioClip HitSound => hitSound;
    public GameObject MuzzleFlashPrefab => muzzleFlashPrefab;
    public GameObject HitEffectPrefab => hitEffectPrefab;
}

public enum WeaponType
{
    Melee,
    Ranged,
    Magic
}

// Data collection manager
[CreateAssetMenu(fileName = "Weapon Database", menuName = "Game Data/Weapon Database")]
public class WeaponDatabase : ScriptableObject
{
    [SerializeField] private WeaponData[] weapons;
    
    private Dictionary<string, WeaponData> weaponDict;
    
    public IReadOnlyList<WeaponData> Weapons => weapons;
    
    private void OnEnable()
    {
        BuildDictionary();
    }
    
    private void BuildDictionary()
    {
        weaponDict = new Dictionary<string, WeaponData>();
        
        foreach (WeaponData weapon in weapons)
        {
            if (weapon != null && !string.IsNullOrEmpty(weapon.ID))
            {
                weaponDict[weapon.ID] = weapon;
            }
        }
    }
    
    public WeaponData GetWeapon(string id)
    {
        if (weaponDict == null) BuildDictionary();
        
        return weaponDict.TryGetValue(id, out WeaponData weapon) ? weapon : null;
    }
    
    public WeaponData[] GetWeaponsByType(WeaponType type)
    {
        return weapons.Where(w => w != null && w.Type == type).ToArray();
    }
    
    public WeaponData GetRandomWeapon()
    {
        return weapons[Random.Range(0, weapons.Length)];
    }
    
    #region Editor Utilities
    #if UNITY_EDITOR
    [ContextMenu("Refresh Database")]
    private void RefreshDatabase()
    {
        weapons = UnityEditor.AssetDatabase.FindAssets("t:WeaponData")
            .Select(guid => UnityEditor.AssetDatabase.LoadAssetAtPath<WeaponData>(
                UnityEditor.AssetDatabase.GUIDToAssetPath(guid)))
            .Where(asset => asset != null)
            .ToArray();
        
        BuildDictionary();
        UnityEditor.EditorUtility.SetDirty(this);
    }
    #endif
    #endregion
}
```

### Async/Await Patterns in Unity

```csharp
using System.Threading.Tasks;
using UnityEngine;

public class AsyncGameManager : MonoBehaviour
{
    [SerializeField] private float loadingDelay = 2f;
    
    private async void Start()
    {
        await InitializeGameAsync();
    }
    
    private async Task InitializeGameAsync()
    {
        try
        {
            Debug.Log("Starting game initialization...");
            
            // Load game data asynchronously
            Task dataTask = LoadGameDataAsync();
            Task audioTask = LoadAudioAsync();
            Task graphicsTask = InitializeGraphicsAsync();
            
            // Wait for all tasks to complete
            await Task.WhenAll(dataTask, audioTask, graphicsTask);
            
            Debug.Log("Game initialization completed!");
            
            // Start the game
            await StartGameplayAsync();
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"Failed to initialize game: {ex.Message}");
        }
    }
    
    private async Task LoadGameDataAsync()
    {
        Debug.Log("Loading game data...");
        
        // Simulate async data loading
        await Task.Delay(Mathf.RoundToInt(loadingDelay * 1000));
        
        Debug.Log("Game data loaded!");
    }
    
    private async Task LoadAudioAsync()
    {
        Debug.Log("Loading audio...");
        
        // Simulate async audio loading
        await Task.Delay(Mathf.RoundToInt(loadingDelay * 500));
        
        Debug.Log("Audio loaded!");
    }
    
    private async Task InitializeGraphicsAsync()
    {
        Debug.Log("Initializing graphics...");
        
        // Simulate async graphics initialization
        await Task.Delay(Mathf.RoundToInt(loadingDelay * 750));
        
        Debug.Log("Graphics initialized!");
    }
    
    private async Task StartGameplayAsync()
    {
        Debug.Log("Starting gameplay...");
        
        // Fade in or other startup effects
        await FadeInAsync();
        
        // Enable player controls
        EnablePlayerInput();
        
        Debug.Log("Gameplay started!");
    }
    
    private async Task FadeInAsync()
    {
        // Example fade in effect
        CanvasGroup fadePanel = FindObjectOfType<CanvasGroup>();
        
        if (fadePanel != null)
        {
            float fadeTime = 1f;
            float elapsedTime = 0f;
            
            while (elapsedTime < fadeTime)
            {
                elapsedTime += Time.deltaTime;
                fadePanel.alpha = Mathf.Lerp(1f, 0f, elapsedTime / fadeTime);
                
                // Wait for next frame
                await Task.Yield();
            }
            
            fadePanel.alpha = 0f;
        }
    }
    
    private void EnablePlayerInput()
    {
        // Enable player input systems
        PlayerController player = FindObjectOfType<PlayerController>();
        if (player != null)
        {
            player.enabled = true;
        }
    }
}

// Async resource loader
public static class AsyncResourceLoader
{
    public static async Task<T> LoadAssetAsync<T>(string path) where T : Object
    {
        ResourceRequest request = Resources.LoadAsync<T>(path);
        
        while (!request.isDone)
        {
            await Task.Yield();
        }
        
        return request.asset as T;
    }
    
    public static async Task<T[]> LoadAllAssetsAsync<T>(string path) where T : Object
    {
        ResourceRequest request = Resources.LoadAsync<T[]>(path);
        
        while (!request.isDone)
        {
            await Task.Yield();
        }
        
        return request.allAssets.Cast<T>().ToArray();
    }
    
    public static async Task<Texture2D> LoadTextureAsync(string url)
    {
        using (UnityEngine.Networking.UnityWebRequest request = 
               UnityEngine.Networking.UnityWebRequestTexture.GetTexture(url))
        {
            request.SendWebRequest();
            
            while (!request.isDone)
            {
                await Task.Yield();
            }
            
            if (request.result == UnityEngine.Networking.UnityWebRequest.Result.Success)
            {
                return UnityEngine.Networking.DownloadHandlerTexture.GetContent(request);
            }
            else
            {
                Debug.LogError($"Failed to load texture: {request.error}");
                return null;
            }
        }
    }
}
```

This comprehensive guide provides professional Unity scripting practices that are essential for large-scale game development, focusing on maintainability, performance, and team collaboration.