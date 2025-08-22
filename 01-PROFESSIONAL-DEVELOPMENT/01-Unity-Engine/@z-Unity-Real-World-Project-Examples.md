# @z-Unity-Real-World-Project-Examples

## 🎯 Learning Objectives
- Build complete Unity projects from concept to deployment
- Master real-world Unity development patterns and architectures
- Implement industry-standard game systems and features
- Create portfolio-worthy projects demonstrating Unity expertise

## 🔧 Complete Project Examples

### Project 1: Mobile Endless Runner Game

**Project Overview:**
A complete mobile endless runner similar to Temple Run or Subway Surfers, showcasing mobile optimization, procedural generation, and monetization integration.

**Core Systems Implementation:**

```csharp
// Main Game Manager
using UnityEngine;
using UnityEngine.SceneManagement;

public class GameManager : MonoBehaviour
{
    [Header("Game State")]
    public bool isGameActive = false;
    public float gameSpeed = 10f;
    public float speedIncrement = 0.5f;
    public float speedIncreaseInterval = 30f;
    
    [Header("Score System")]
    public int currentScore = 0;
    public int highScore = 0;
    public int coinsCollected = 0;
    
    [Header("References")]
    public PlayerController player;
    public UIManager uiManager;
    public AudioManager audioManager;
    public PowerUpManager powerUpManager;
    
    public static GameManager Instance { get; private set; }
    
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
        
        LoadGameData();
    }
    
    void Start()
    {
        StartGame();
    }
    
    void Update()
    {
        if (isGameActive)
        {
            UpdateScore();
            IncreaseSpeed();
        }
    }
    
    public void StartGame()
    {
        isGameActive = true;
        Time.timeScale = 1f;
        uiManager.ShowGameUI();
        audioManager.PlayBackgroundMusic();
    }
    
    public void EndGame()
    {
        isGameActive = false;
        
        // Check for high score
        if (currentScore > highScore)
        {
            highScore = currentScore;
            uiManager.ShowNewHighScore();
        }
        
        SaveGameData();
        uiManager.ShowGameOverScreen();
        audioManager.PlayGameOverSound();
    }
    
    void UpdateScore()
    {
        currentScore += Mathf.RoundToInt(gameSpeed * Time.deltaTime);
        uiManager.UpdateScore(currentScore);
    }
    
    void IncreaseSpeed()
    {
        gameSpeed += speedIncrement * Time.deltaTime / speedIncreaseInterval;
    }
    
    public void CollectCoin()
    {
        coinsCollected++;
        currentScore += 10;
        uiManager.UpdateCoins(coinsCollected);
        audioManager.PlayCoinSound();
    }
    
    void LoadGameData()
    {
        highScore = PlayerPrefs.GetInt("HighScore", 0);
        coinsCollected = PlayerPrefs.GetInt("TotalCoins", 0);
    }
    
    void SaveGameData()
    {
        PlayerPrefs.SetInt("HighScore", highScore);
        PlayerPrefs.SetInt("TotalCoins", coinsCollected);
        PlayerPrefs.Save();
    }
    
    public void RestartGame()
    {
        SceneManager.LoadScene(SceneManager.GetActiveScene().name);
    }
}

// Player Controller with Swipe Controls
public class PlayerController : MonoBehaviour
{
    [Header("Movement Settings")]
    public float jumpForce = 10f;
    public float slideDistance = 2f;
    public float laneChangeSpeed = 15f;
    
    [Header("Lane Positions")]
    public Transform[] lanePositions;
    public int currentLane = 1; // Start in middle lane
    
    private Rigidbody rb;
    private Animator animator;
    private bool isGrounded = true;
    private bool isSliding = false;
    private Vector3 targetPosition;
    
    // Touch input variables
    private Vector2 startTouchPosition;
    private Vector2 endTouchPosition;
    private float minSwipeDistance = 50f;
    
    void Start()
    {
        rb = GetComponent<Rigidbody>();
        animator = GetComponent<Animator>();
        targetPosition = lanePositions[currentLane].position;
    }
    
    void Update()
    {
        if (!GameManager.Instance.isGameActive) return;
        
        HandleInput();
        MoveToTargetLane();
        UpdateAnimations();
    }
    
    void HandleInput()
    {
        // Touch input for mobile
        if (Input.touchCount > 0)
        {
            Touch touch = Input.GetTouch(0);
            
            if (touch.phase == TouchPhase.Began)
            {
                startTouchPosition = touch.position;
            }
            else if (touch.phase == TouchPhase.Ended)
            {
                endTouchPosition = touch.position;
                ProcessSwipe();
            }
        }
        
        // Keyboard input for testing
        if (Input.GetKeyDown(KeyCode.UpArrow) || Input.GetKeyDown(KeyCode.W))
            Jump();
        if (Input.GetKeyDown(KeyCode.DownArrow) || Input.GetKeyDown(KeyCode.S))
            Slide();
        if (Input.GetKeyDown(KeyCode.LeftArrow) || Input.GetKeyDown(KeyCode.A))
            ChangeLane(-1);
        if (Input.GetKeyDown(KeyCode.RightArrow) || Input.GetKeyDown(KeyCode.D))
            ChangeLane(1);
    }
    
    void ProcessSwipe()
    {
        Vector2 swipeDirection = endTouchPosition - startTouchPosition;
        
        if (swipeDirection.magnitude < minSwipeDistance) return;
        
        swipeDirection.Normalize();
        
        // Determine swipe direction
        if (Mathf.Abs(swipeDirection.x) > Mathf.Abs(swipeDirection.y))
        {
            // Horizontal swipe
            if (swipeDirection.x > 0)
                ChangeLane(1); // Right
            else
                ChangeLane(-1); // Left
        }
        else
        {
            // Vertical swipe
            if (swipeDirection.y > 0)
                Jump(); // Up
            else
                Slide(); // Down
        }
    }
    
    void Jump()
    {
        if (isGrounded && !isSliding)
        {
            rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
            isGrounded = false;
            animator.SetTrigger("Jump");
        }
    }
    
    void Slide()
    {
        if (isGrounded && !isSliding)
        {
            StartCoroutine(SlideCoroutine());
        }
    }
    
    System.Collections.IEnumerator SlideCoroutine()
    {
        isSliding = true;
        animator.SetBool("IsSliding", true);
        
        // Lower the collider
        GetComponent<CapsuleCollider>().height = 1f;
        GetComponent<CapsuleCollider>().center = new Vector3(0, 0.5f, 0);
        
        yield return new WaitForSeconds(1f);
        
        // Restore collider
        GetComponent<CapsuleCollider>().height = 2f;
        GetComponent<CapsuleCollider>().center = new Vector3(0, 1f, 0);
        
        isSliding = false;
        animator.SetBool("IsSliding", false);
    }
    
    void ChangeLane(int direction)
    {
        currentLane = Mathf.Clamp(currentLane + direction, 0, lanePositions.Length - 1);
        targetPosition = new Vector3(lanePositions[currentLane].position.x, transform.position.y, transform.position.z);
    }
    
    void MoveToTargetLane()
    {
        Vector3 currentPos = transform.position;
        Vector3 newPos = Vector3.Lerp(currentPos, targetPosition, laneChangeSpeed * Time.deltaTime);
        transform.position = newPos;
    }
    
    void UpdateAnimations()
    {
        animator.SetBool("IsGrounded", isGrounded);
        animator.SetFloat("Speed", GameManager.Instance.gameSpeed);
    }
    
    void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.CompareTag("Ground"))
        {
            isGrounded = true;
        }
        else if (collision.gameObject.CompareTag("Obstacle"))
        {
            GameManager.Instance.EndGame();
        }
    }
    
    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Coin"))
        {
            GameManager.Instance.CollectCoin();
            Destroy(other.gameObject);
        }
        else if (other.CompareTag("PowerUp"))
        {
            PowerUpManager.Instance.ActivatePowerUp(other.GetComponent<PowerUp>().powerUpType);
            Destroy(other.gameObject);
        }
    }
}

// Procedural Level Generator
public class LevelGenerator : MonoBehaviour
{
    [Header("Generation Settings")]
    public GameObject[] levelSegments;
    public int segmentsToGenerate = 5;
    public float segmentLength = 30f;
    
    [Header("Spawn Settings")]
    public GameObject[] obstacles;
    public GameObject[] collectibles;
    public GameObject[] powerUps;
    
    private Queue<GameObject> activeSegments;
    private float nextSegmentPosition = 0f;
    
    void Start()
    {
        activeSegments = new Queue<GameObject>();
        
        // Generate initial segments
        for (int i = 0; i < segmentsToGenerate; i++)
        {
            GenerateSegment();
        }
    }
    
    void Update()
    {
        // Check if we need to generate new segments
        if (Camera.main.transform.position.z + 100f > nextSegmentPosition - (segmentsToGenerate * segmentLength))
        {
            GenerateSegment();
            RemoveOldSegment();
        }
    }
    
    void GenerateSegment()
    {
        GameObject segmentPrefab = levelSegments[Random.Range(0, levelSegments.Length)];
        Vector3 spawnPosition = new Vector3(0, 0, nextSegmentPosition);
        
        GameObject newSegment = Instantiate(segmentPrefab, spawnPosition, Quaternion.identity);
        activeSegments.Enqueue(newSegment);
        
        // Populate segment with obstacles and collectibles
        PopulateSegment(newSegment);
        
        nextSegmentPosition += segmentLength;
    }
    
    void PopulateSegment(GameObject segment)
    {
        LevelSegment segmentScript = segment.GetComponent<LevelSegment>();
        
        if (segmentScript != null)
        {
            foreach (Transform spawnPoint in segmentScript.obstacleSpawnPoints)
            {
                if (Random.Range(0f, 1f) < 0.3f) // 30% chance to spawn obstacle
                {
                    GameObject obstacle = obstacles[Random.Range(0, obstacles.Length)];
                    Instantiate(obstacle, spawnPoint.position, spawnPoint.rotation, segment.transform);
                }
            }
            
            foreach (Transform spawnPoint in segmentScript.collectibleSpawnPoints)
            {
                if (Random.Range(0f, 1f) < 0.7f) // 70% chance to spawn collectible
                {
                    GameObject collectible = collectibles[Random.Range(0, collectibles.Length)];
                    Instantiate(collectible, spawnPoint.position, spawnPoint.rotation, segment.transform);
                }
            }
        }
    }
    
    void RemoveOldSegment()
    {
        if (activeSegments.Count > segmentsToGenerate)
        {
            GameObject oldSegment = activeSegments.Dequeue();
            Destroy(oldSegment);
        }
    }
}
```

**Project Architecture:**
```
EndlessRunner/
├── Scripts/
│   ├── Managers/
│   │   ├── GameManager.cs
│   │   ├── UIManager.cs
│   │   ├── AudioManager.cs
│   │   └── PowerUpManager.cs
│   ├── Player/
│   │   ├── PlayerController.cs
│   │   └── PlayerAnimationController.cs
│   ├── Level/
│   │   ├── LevelGenerator.cs
│   │   ├── LevelSegment.cs
│   │   └── EnvironmentMover.cs
│   ├── Collectibles/
│   │   ├── Coin.cs
│   │   └── PowerUp.cs
│   └── Utils/
│       ├── ObjectPool.cs
│       └── SaveSystem.cs
├── Prefabs/
│   ├── Player/
│   ├── LevelSegments/
│   ├── Obstacles/
│   └── UI/
├── Materials/
├── Textures/
└── Audio/
    ├── Music/
    └── SFX/
```

### Project 2: 2D Tower Defense Game

**Project Overview:**
A complete 2D tower defense game with multiple tower types, enemy waves, upgrade systems, and strategic gameplay elements.

**Core Systems:**

```csharp
// Wave Management System
[System.Serializable]
public class Wave
{
    public string waveName;
    public List<WaveSegment> segments;
    public float timeBetweenSegments = 2f;
}

[System.Serializable]
public class WaveSegment
{
    public GameObject enemyPrefab;
    public int enemyCount;
    public float spawnRate;
}

public class WaveManager : MonoBehaviour
{
    [Header("Wave Configuration")]
    public List<Wave> waves;
    public float timeBetweenWaves = 5f;
    
    [Header("Spawn Settings")]
    public Transform[] spawnPoints;
    public Transform[] waypoints;
    
    private int currentWaveIndex = 0;
    private bool isSpawning = false;
    
    public static WaveManager Instance { get; private set; }
    
    void Awake()
    {
        Instance = this;
    }
    
    void Start()
    {
        StartNextWave();
    }
    
    public void StartNextWave()
    {
        if (currentWaveIndex < waves.Count)
        {
            StartCoroutine(SpawnWave(waves[currentWaveIndex]));
            currentWaveIndex++;
        }
        else
        {
            // All waves complete - victory!
            GameManager.Instance.Victory();
        }
    }
    
    IEnumerator SpawnWave(Wave wave)
    {
        isSpawning = true;
        UIManager.Instance.ShowWaveStart(wave.waveName);
        
        foreach (WaveSegment segment in wave.segments)
        {
            yield return StartCoroutine(SpawnSegment(segment));
            yield return new WaitForSeconds(wave.timeBetweenSegments);
        }
        
        isSpawning = false;
        
        // Wait for all enemies to be defeated or reach end
        yield return new WaitUntil(() => EnemyManager.Instance.AllEnemiesDefeated());
        
        yield return new WaitForSeconds(timeBetweenWaves);
        StartNextWave();
    }
    
    IEnumerator SpawnSegment(WaveSegment segment)
    {
        for (int i = 0; i < segment.enemyCount; i++)
        {
            SpawnEnemy(segment.enemyPrefab);
            yield return new WaitForSeconds(1f / segment.spawnRate);
        }
    }
    
    void SpawnEnemy(GameObject enemyPrefab)
    {
        Transform spawnPoint = spawnPoints[Random.Range(0, spawnPoints.Length)];
        GameObject enemy = ObjectPool.Instance.SpawnFromPool("Enemy", spawnPoint.position, spawnPoint.rotation);
        
        Enemy enemyScript = enemy.GetComponent<Enemy>();
        enemyScript.SetWaypoints(waypoints);
        enemyScript.ResetEnemy();
    }
}

// Tower System
public abstract class Tower : MonoBehaviour
{
    [Header("Tower Stats")]
    public float damage = 50f;
    public float range = 5f;
    public float fireRate = 1f;
    public int cost = 100;
    
    [Header("Upgrade System")]
    public TowerUpgrade[] upgrades;
    public int currentUpgradeLevel = 0;
    
    protected Transform target;
    protected float nextFireTime;
    protected List<Enemy> enemiesInRange = new List<Enemy>();
    
    public virtual void Start()
    {
        InvokeRepeating(nameof(UpdateTarget), 0f, 0.1f);
    }
    
    public virtual void Update()
    {
        if (target != null && Time.time >= nextFireTime)
        {
            Fire();
            nextFireTime = Time.time + 1f / fireRate;
        }
    }
    
    protected virtual void UpdateTarget()
    {
        enemiesInRange.Clear();
        
        Collider2D[] enemies = Physics2D.OverlapCircleAll(transform.position, range, LayerMask.GetMask("Enemy"));
        
        foreach (Collider2D enemyCollider in enemies)
        {
            Enemy enemy = enemyCollider.GetComponent<Enemy>();
            if (enemy != null && enemy.IsAlive())
            {
                enemiesInRange.Add(enemy);
            }
        }
        
        // Choose target based on strategy (closest, strongest, etc.)
        target = GetBestTarget();
    }
    
    protected virtual Transform GetBestTarget()
    {
        if (enemiesInRange.Count == 0) return null;
        
        // Default: target closest enemy
        Enemy closestEnemy = enemiesInRange[0];
        float closestDistance = Vector3.Distance(transform.position, closestEnemy.transform.position);
        
        foreach (Enemy enemy in enemiesInRange)
        {
            float distance = Vector3.Distance(transform.position, enemy.transform.position);
            if (distance < closestDistance)
            {
                closestDistance = distance;
                closestEnemy = enemy;
            }
        }
        
        return closestEnemy.transform;
    }
    
    protected abstract void Fire();
    
    public virtual bool CanUpgrade()
    {
        return currentUpgradeLevel < upgrades.Length;
    }
    
    public virtual void Upgrade()
    {
        if (CanUpgrade())
        {
            TowerUpgrade upgrade = upgrades[currentUpgradeLevel];
            
            damage += upgrade.damageIncrease;
            range += upgrade.rangeIncrease;
            fireRate += upgrade.fireRateIncrease;
            
            currentUpgradeLevel++;
            
            // Visual upgrade effects
            ApplyUpgradeVisuals(upgrade);
        }
    }
    
    protected virtual void ApplyUpgradeVisuals(TowerUpgrade upgrade)
    {
        // Change tower appearance, add effects, etc.
    }
    
    void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(transform.position, range);
    }
}

// Specific Tower Implementation
public class LaserTower : Tower
{
    [Header("Laser Settings")]
    public LineRenderer laserLine;
    public ParticleSystem hitEffect;
    public float laserDuration = 0.1f;
    
    protected override void Fire()
    {
        if (target == null) return;
        
        // Deal damage
        Enemy enemy = target.GetComponent<Enemy>();
        if (enemy != null)
        {
            enemy.TakeDamage(damage);
        }
        
        // Visual effects
        StartCoroutine(FireLaser());
    }
    
    IEnumerator FireLaser()
    {
        laserLine.enabled = true;
        laserLine.SetPosition(0, transform.position);
        laserLine.SetPosition(1, target.position);
        
        // Particle effect at hit point
        hitEffect.transform.position = target.position;
        hitEffect.Play();
        
        yield return new WaitForSeconds(laserDuration);
        
        laserLine.enabled = false;
    }
}
```

### Project 3: 3D Platformer Adventure

**Project Overview:**
A 3D platformer with character progression, collectibles, environmental puzzles, and multiple levels.

**Key Systems:**

```csharp
// Advanced 3D Character Controller
public class PlatformerController : MonoBehaviour
{
    [Header("Movement Settings")]
    public float moveSpeed = 8f;
    public float jumpHeight = 2f;
    public float gravity = -25f;
    public float airControl = 0.3f;
    
    [Header("Ground Detection")]
    public Transform groundCheck;
    public float groundDistance = 0.4f;
    public LayerMask groundMask;
    
    [Header("Wall Jump")]
    public float wallJumpForce = 15f;
    public float wallSlideSpeed = 2f;
    public LayerMask wallMask;
    
    [Header("Abilities")]
    public float dashDistance = 5f;
    public float dashDuration = 0.2f;
    public int maxJumps = 2;
    
    private CharacterController controller;
    private Vector3 velocity;
    private bool isGrounded;
    private bool canDash = true;
    private int jumpsRemaining;
    private Vector3 moveDirection;
    
    // Wall detection
    private bool isTouchingWall;
    private Vector3 wallNormal;
    
    void Start()
    {
        controller = GetComponent<CharacterController>();
        jumpsRemaining = maxJumps;
    }
    
    void Update()
    {
        GroundCheck();
        WallCheck();
        HandleInput();
        ApplyMovement();
        ApplyGravity();
        
        controller.Move(velocity * Time.deltaTime);
    }
    
    void GroundCheck()
    {
        bool wasGrounded = isGrounded;
        isGrounded = Physics.CheckSphere(groundCheck.position, groundDistance, groundMask);
        
        if (isGrounded && !wasGrounded)
        {
            jumpsRemaining = maxJumps;
            canDash = true;
        }
    }
    
    void WallCheck()
    {
        // Cast rays to detect walls
        Vector3 rayOrigin = transform.position + Vector3.up;
        float rayDistance = 0.7f;
        
        RaycastHit hit;
        if (Physics.Raycast(rayOrigin, transform.forward, out hit, rayDistance, wallMask))
        {
            isTouchingWall = true;
            wallNormal = hit.normal;
        }
        else if (Physics.Raycast(rayOrigin, -transform.forward, out hit, rayDistance, wallMask))
        {
            isTouchingWall = true;
            wallNormal = hit.normal;
        }
        else
        {
            isTouchingWall = false;
        }
    }
    
    void HandleInput()
    {
        // Movement input
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");
        
        Vector3 direction = transform.right * horizontal + transform.forward * vertical;
        
        if (isGrounded)
        {
            moveDirection = direction;
        }
        else
        {
            // Air control
            moveDirection = Vector3.Lerp(moveDirection, direction, airControl * Time.deltaTime);
        }
        
        // Jump input
        if (Input.GetButtonDown("Jump"))
        {
            if (isGrounded || jumpsRemaining > 0)
            {
                Jump();
            }
            else if (isTouchingWall && !isGrounded)
            {
                WallJump();
            }
        }
        
        // Dash input
        if (Input.GetKeyDown(KeyCode.LeftShift) && canDash)
        {
            StartCoroutine(Dash());
        }
    }
    
    void ApplyMovement()
    {
        Vector3 move = moveDirection * moveSpeed;
        
        // Apply wall sliding
        if (isTouchingWall && !isGrounded && velocity.y < 0)
        {
            velocity.y = Mathf.Max(velocity.y, -wallSlideSpeed);
        }
        
        velocity.x = move.x;
        velocity.z = move.z;
    }
    
    void ApplyGravity()
    {
        if (isGrounded && velocity.y < 0)
        {
            velocity.y = -2f; // Small downward force to keep grounded
        }
        else
        {
            velocity.y += gravity * Time.deltaTime;
        }
    }
    
    void Jump()
    {
        velocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
        
        if (!isGrounded)
        {
            jumpsRemaining--;
        }
        
        // Visual/audio effects
        PlayJumpEffects();
    }
    
    void WallJump()
    {
        // Jump away from wall
        Vector3 jumpDirection = wallNormal + Vector3.up;
        velocity = jumpDirection.normalized * wallJumpForce;
        
        // Reset wall touch to prevent immediate re-attachment
        isTouchingWall = false;
        
        PlayWallJumpEffects();
    }
    
    IEnumerator Dash()
    {
        canDash = false;
        float dashSpeed = dashDistance / dashDuration;
        Vector3 dashDirection = moveDirection.normalized;
        
        if (dashDirection == Vector3.zero)
            dashDirection = transform.forward;
        
        float dashTime = 0f;
        while (dashTime < dashDuration)
        {
            controller.Move(dashDirection * dashSpeed * Time.deltaTime);
            dashTime += Time.deltaTime;
            yield return null;
        }
        
        // Dash cooldown
        yield return new WaitForSeconds(1f);
        canDash = true;
    }
    
    void PlayJumpEffects()
    {
        // Particle effects, sound, animation triggers
    }
    
    void PlayWallJumpEffects()
    {
        // Wall jump specific effects
    }
}

// Collectible and Progression System
public class CollectibleManager : MonoBehaviour
{
    [Header("Collectible Types")]
    public int coins = 0;
    public int gems = 0;
    public int powerOrbs = 0;
    
    [Header("Abilities")]
    public bool hasDoubleJump = false;
    public bool hasDash = false;
    public bool hasWallJump = false;
    
    public static CollectibleManager Instance { get; private set; }
    
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
    
    public void CollectItem(CollectibleType type, int value = 1)
    {
        switch (type)
        {
            case CollectibleType.Coin:
                coins += value;
                break;
            case CollectibleType.Gem:
                gems += value;
                break;
            case CollectibleType.PowerOrb:
                powerOrbs += value;
                CheckForAbilityUnlock();
                break;
        }
        
        UIManager.Instance.UpdateCollectibleUI();
        SaveProgress();
    }
    
    void CheckForAbilityUnlock()
    {
        if (powerOrbs >= 3 && !hasDoubleJump)
        {
            UnlockAbility(AbilityType.DoubleJump);
        }
        if (powerOrbs >= 6 && !hasDash)
        {
            UnlockAbility(AbilityType.Dash);
        }
        if (powerOrbs >= 9 && !hasWallJump)
        {
            UnlockAbility(AbilityType.WallJump);
        }
    }
    
    void UnlockAbility(AbilityType ability)
    {
        switch (ability)
        {
            case AbilityType.DoubleJump:
                hasDoubleJump = true;
                break;
            case AbilityType.Dash:
                hasDash = true;
                break;
            case AbilityType.WallJump:
                hasWallJump = true;
                break;
        }
        
        UIManager.Instance.ShowAbilityUnlocked(ability);
    }
    
    void SaveProgress()
    {
        PlayerPrefs.SetInt("Coins", coins);
        PlayerPrefs.SetInt("Gems", gems);
        PlayerPrefs.SetInt("PowerOrbs", powerOrbs);
        PlayerPrefs.SetInt("HasDoubleJump", hasDoubleJump ? 1 : 0);
        PlayerPrefs.SetInt("HasDash", hasDash ? 1 : 0);
        PlayerPrefs.SetInt("HasWallJump", hasWallJump ? 1 : 0);
    }
}
```

## 🚀 AI/LLM Integration for Project Development

### Automated Project Setup
```python
#!/usr/bin/env python3
"""
Unity Project Generator
Creates complete Unity project structure with AI-generated code
"""

def generate_unity_project(project_type, game_name):
    # AI-generated project setup
    project_structure = {
        'endless_runner': generate_endless_runner_structure(),
        'tower_defense': generate_tower_defense_structure(),
        'platformer': generate_platformer_structure()
    }
    
    return project_structure[project_type]

def generate_game_scripts(project_type, requirements):
    """Generate complete game scripts using AI"""
    prompt = f"""
    Generate a complete Unity {project_type} game with:
    - Requirements: {requirements}
    - Industry-standard architecture
    - Performance optimizations
    - Mobile-friendly design
    - Comprehensive commenting
    """
    
    # AI implementation for script generation
    pass
```

### Project Documentation Generator
```python
def generate_project_documentation(project_path):
    """Generate comprehensive project documentation"""
    docs = {
        'README.md': generate_readme(),
        'ARCHITECTURE.md': analyze_project_architecture(),
        'API_REFERENCE.md': generate_api_docs(),
        'SETUP_GUIDE.md': create_setup_instructions()
    }
    
    return docs
```

## 💡 Key Highlights

**Project Development Benefits:**
- **Real-World Experience**: Industry-standard project structure and patterns
- **Portfolio Quality**: Complete, polished games demonstrating Unity expertise
- **System Integration**: Complex systems working together seamlessly
- **Performance Optimization**: Mobile and desktop optimization techniques

**Architecture Principles:**
- **Modular Design**: Loosely coupled systems for maintainability
- **Manager Pattern**: Centralized control for game state and systems
- **Component Composition**: Flexible, reusable component-based architecture
- **Event-Driven Communication**: Decoupled system communication

**Best Practices Demonstrated:**
- Object pooling for performance
- Proper state management
- Mobile input handling
- Save system implementation
- UI/UX integration
- Audio system integration

**Technical Skills Showcased:**
- Advanced Unity features (Coroutines, Events, ScriptableObjects)
- Design patterns (Singleton, Observer, Factory)
- Performance optimization techniques
- Mobile development considerations
- Cross-platform input handling

These complete project examples provide comprehensive learning resources and portfolio pieces that demonstrate mastery of Unity development across different game genres and technical requirements.