# @k-Testing-Debugging - Unity Testing Frameworks & Debugging Techniques

## 🎯 Learning Objectives
- Master Unity Test Framework for automated testing workflows
- Learn advanced debugging techniques using Unity's debugging tools
- Understand performance profiling and optimization strategies
- Apply AI/LLM tools to generate test cases and debug complex issues

---

## 🔧 Unity Test Framework Fundamentals

### Test Categories in Unity
Unity provides comprehensive testing capabilities through multiple frameworks:

**Edit Mode Tests:**
- Run in the Unity Editor without entering Play mode
- Test utility functions, data structures, and editor scripts
- Fast execution for unit testing pure C# logic

**Play Mode Tests:**
- Execute in Unity's runtime environment
- Test GameObject behavior, component interactions, and scene logic
- Integration testing with Unity's systems

```csharp
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using System.Collections;

public class PlayerControllerTests
{
    private GameObject playerObject;
    private PlayerController playerController;
    
    [SetUp]
    public void Setup()
    {
        playerObject = new GameObject("TestPlayer");
        playerController = playerObject.AddComponent<PlayerController>();
        playerController.speed = 5f;
    }
    
    [TearDown]
    public void Teardown()
    {
        Object.DestroyImmediate(playerObject);
    }
    
    [Test]
    public void PlayerController_InitializesWithCorrectSpeed()
    {
        Assert.AreEqual(5f, playerController.speed);
    }
    
    [UnityTest]
    public IEnumerator PlayerController_MovesCorrectlyOverTime()
    {
        Vector3 startPosition = playerController.transform.position;
        Vector3 targetPosition = startPosition + Vector3.forward * 5f;
        
        playerController.MoveToPosition(targetPosition);
        
        yield return new WaitForSeconds(1f);
        
        Assert.AreEqual(targetPosition, playerController.transform.position, "Player should reach target position");
    }
}
```

### Advanced Testing Patterns

**Mock Objects for Dependencies:**
```csharp
public interface IHealthSystem
{
    int CurrentHealth { get; }
    void TakeDamage(int damage);
    bool IsAlive { get; }
}

public class MockHealthSystem : IHealthSystem
{
    public int CurrentHealth { get; private set; } = 100;
    public bool IsAlive => CurrentHealth > 0;
    
    public void TakeDamage(int damage)
    {
        CurrentHealth = Mathf.Max(0, CurrentHealth - damage);
    }
}

[Test]
public void EnemyAI_ReactsToPlayerDeath()
{
    var mockHealth = new MockHealthSystem();
    var enemy = CreateEnemyWithHealthSystem(mockHealth);
    
    mockHealth.TakeDamage(100); // Kill player
    
    Assert.IsFalse(mockHealth.IsAlive);
    Assert.AreEqual(EnemyState.Victory, enemy.CurrentState);
}
```

**Parameterized Tests for Data-Driven Testing:**
```csharp
public class WeaponDamageTests
{
    [TestCase(WeaponType.Sword, 25, 100, 75)]
    [TestCase(WeaponType.Bow, 15, 50, 35)]
    [TestCase(WeaponType.Staff, 30, 80, 50)]
    public void Weapon_DealsDamageCorrectly(WeaponType weaponType, int damage, int enemyHealth, int expectedHealth)
    {
        var weapon = WeaponFactory.Create(weaponType);
        var enemy = new Enemy { Health = enemyHealth };
        
        weapon.Attack(enemy);
        
        Assert.AreEqual(expectedHealth, enemy.Health);
    }
    
    [TestCaseSource(nameof(GetWeaponTestData))]
    public void Weapon_HandlesCriticalHits(WeaponTestData testData)
    {
        var weapon = WeaponFactory.Create(testData.WeaponType);
        weapon.CriticalHitChance = 1f; // Guarantee critical hit
        
        var enemy = new Enemy { Health = testData.EnemyHealth };
        weapon.Attack(enemy);
        
        Assert.LessOrEqual(enemy.Health, testData.EnemyHealth - (testData.Damage * 2));
    }
    
    private static IEnumerable<WeaponTestData> GetWeaponTestData()
    {
        yield return new WeaponTestData { WeaponType = WeaponType.Sword, Damage = 25, EnemyHealth = 100 };
        yield return new WeaponTestData { WeaponType = WeaponType.Bow, Damage = 15, EnemyHealth = 50 };
    }
}
```

---

## 🔍 Advanced Debugging Techniques

### Unity Console and Logging Best Practices

**Structured Logging System:**
```csharp
public static class GameLogger
{
    public enum LogCategory
    {
        Gameplay,
        UI,
        Audio,
        Network,
        Performance
    }
    
    [System.Diagnostics.Conditional("UNITY_EDITOR")]
    public static void Log(object message, LogCategory category = LogCategory.Gameplay, Object context = null)
    {
        string formattedMessage = $"[{category}] {System.DateTime.Now:HH:mm:ss} - {message}";
        Debug.Log(formattedMessage, context);
    }
    
    [System.Diagnostics.Conditional("UNITY_EDITOR")]
    public static void LogWarning(object message, LogCategory category = LogCategory.Gameplay, Object context = null)
    {
        string formattedMessage = $"[{category}] {System.DateTime.Now:HH:mm:ss} - {message}";
        Debug.LogWarning(formattedMessage, context);
    }
    
    [System.Diagnostics.Conditional("DEVELOPMENT_BUILD")]
    public static void LogError(object message, LogCategory category = LogCategory.Gameplay, Object context = null)
    {
        string formattedMessage = $"[{category}] {System.DateTime.Now:HH:mm:ss} - {message}";
        Debug.LogError(formattedMessage, context);
    }
}

// Usage examples
public class PlayerController : MonoBehaviour
{
    void Start()
    {
        GameLogger.Log("Player controller initialized", GameLogger.LogCategory.Gameplay, this);
    }
    
    void OnTriggerEnter(Collider other)
    {
        GameLogger.Log($"Player collided with {other.name}", GameLogger.LogCategory.Gameplay, other);
    }
}
```

### Visual Debugging with Gizmos and Handles

**Custom Debug Visualization:**
```csharp
public class AIController : MonoBehaviour
{
    [SerializeField] private float detectionRadius = 5f;
    [SerializeField] private float attackRange = 2f;
    [SerializeField] private LayerMask playerLayer;
    
    private void OnDrawGizmos()
    {
        // Detection radius
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(transform.position, detectionRadius);
        
        // Attack range
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(transform.position, attackRange);
        
        // Line of sight to player
        var player = FindPlayerInRange();
        if (player != null)
        {
            Gizmos.color = Color.green;
            Gizmos.DrawLine(transform.position, player.transform.position);
        }
    }
    
    private void OnDrawGizmosSelected()
    {
        // Show additional debug info when selected
        UnityEditor.Handles.Label(transform.position + Vector3.up * 2f, 
            $"State: {currentState}\nHealth: {health}/{maxHealth}");
    }
}
```

**Runtime Debug UI System:**
```csharp
public class DebugUI : MonoBehaviour
{
    [SerializeField] private bool showDebugInfo = true;
    [SerializeField] private KeyCode toggleKey = KeyCode.F1;
    
    private void Update()
    {
        if (Input.GetKeyDown(toggleKey))
        {
            showDebugInfo = !showDebugInfo;
        }
    }
    
    private void OnGUI()
    {
        if (!showDebugInfo) return;
        
        GUILayout.BeginArea(new Rect(10, 10, 300, 400));
        GUILayout.Label("=== DEBUG INFO ===");
        
        GUILayout.Label($"FPS: {(1f / Time.unscaledDeltaTime):F1}");
        GUILayout.Label($"Objects: {FindObjectsOfType<GameObject>().Length}");
        GUILayout.Label($"Memory: {(System.GC.GetTotalMemory(false) / 1024f / 1024f):F1} MB");
        
        if (GUILayout.Button("Collect Garbage"))
        {
            System.GC.Collect();
        }
        
        if (GUILayout.Button("Time Scale 0.1x"))
        {
            Time.timeScale = 0.1f;
        }
        
        if (GUILayout.Button("Time Scale 1x"))
        {
            Time.timeScale = 1f;
        }
        
        GUILayout.EndArea();
    }
}
```

---

## ⚡ Performance Profiling and Optimization

### Unity Profiler Deep Dive

**Custom Profiler Markers:**
```csharp
using Unity.Profiling;

public class AISystem : MonoBehaviour
{
    private static readonly ProfilerMarker s_AIUpdateMarker = new ProfilerMarker("AISystem.Update");
    private static readonly ProfilerMarker s_PathfindingMarker = new ProfilerMarker("AISystem.Pathfinding");
    private static readonly ProfilerMarker s_DecisionMakingMarker = new ProfilerMarker("AISystem.DecisionMaking");
    
    void Update()
    {
        using (s_AIUpdateMarker.Auto())
        {
            UpdateAllAI();
        }
    }
    
    private void UpdateAllAI()
    {
        foreach (var ai in activeAI)
        {
            using (s_PathfindingMarker.Auto())
            {
                ai.UpdatePathfinding();
            }
            
            using (s_DecisionMakingMarker.Auto())
            {
                ai.MakeDecisions();
            }
        }
    }
}
```

**Memory Allocation Profiling:**
```csharp
public class ObjectPool<T> where T : Component
{
    private readonly Queue<T> availableObjects = new Queue<T>();
    private readonly List<T> allObjects = new List<T>();
    private readonly T prefab;
    
    // Avoid allocations in hot paths
    private readonly Dictionary<T, bool> activeObjects = new Dictionary<T, bool>();
    
    public T Get()
    {
        if (availableObjects.Count > 0)
        {
            var obj = availableObjects.Dequeue();
            obj.gameObject.SetActive(true);
            activeObjects[obj] = true;
            return obj;
        }
        
        return CreateNewObject();
    }
    
    public void Return(T obj)
    {
        if (activeObjects.ContainsKey(obj))
        {
            obj.gameObject.SetActive(false);
            availableObjects.Enqueue(obj);
            activeObjects[obj] = false;
        }
    }
    
    // Profile object pool efficiency
    [System.Diagnostics.Conditional("UNITY_EDITOR")]
    private void LogPoolStatistics()
    {
        Debug.Log($"Pool Stats - Total: {allObjects.Count}, Available: {availableObjects.Count}, Active: {activeObjects.Count(kvp => kvp.Value)}");
    }
}
```

### Automated Performance Testing

**Performance Regression Detection:**
```csharp
[UnityTest]
public IEnumerator PerformanceTest_AISystemScaling()
{
    var testResults = new List<PerformanceTestResult>();
    
    for (int aiCount = 10; aiCount <= 1000; aiCount += 100)
    {
        yield return SetupAITest(aiCount);
        
        var stopwatch = System.Diagnostics.Stopwatch.StartNew();
        
        // Run for 100 frames
        for (int frame = 0; frame < 100; frame++)
        {
            aiSystem.UpdateAllAI();
            yield return null;
        }
        
        stopwatch.Stop();
        
        var result = new PerformanceTestResult
        {
            AICount = aiCount,
            AverageFrameTime = stopwatch.ElapsedMilliseconds / 100f,
            MemoryUsage = System.GC.GetTotalMemory(false)
        };
        
        testResults.Add(result);
        
        // Assert performance doesn't degrade beyond acceptable limits
        Assert.Less(result.AverageFrameTime, GetAcceptableFrameTime(aiCount), 
            $"Frame time exceeded limit with {aiCount} AI agents");
    }
    
    // Log results for analysis
    LogPerformanceResults(testResults);
}
```

---

## 🤖 AI/LLM Integration for Testing & Debugging

### AI-Generated Test Cases
Use LLMs to create comprehensive test scenarios:

**Prompt Example:**
> "Generate Unity test cases for a inventory system that handles item stacking, weight limits, and item durability. Include edge cases like full inventory, invalid items, and concurrent access."

### Automated Bug Report Analysis
AI-assisted bug triaging and categorization:

```csharp
public class BugReportAnalyzer
{
    public async Task<BugClassification> AnalyzeBugReport(string bugReport)
    {
        // Send to AI service for classification
        var prompt = $@"
        Analyze this Unity game bug report and classify it:
        
        Bug Report: {bugReport}
        
        Classify by:
        - Severity (Critical/High/Medium/Low)
        - Category (Gameplay/UI/Performance/Graphics/Audio)
        - Likely Root Cause
        - Suggested Investigation Steps
        
        Respond in JSON format.
        ";
        
        var response = await aiService.Analyze(prompt);
        return JsonUtility.FromJson<BugClassification>(response);
    }
}
```

### Smart Test Data Generation
AI-generated test data for comprehensive scenario coverage:

```csharp
[TestCaseSource(nameof(GenerateEnemyTestCases))]
public void Combat_HandlesVariousEnemyTypes(EnemyTestCase testCase)
{
    var player = CreateTestPlayer();
    var enemy = CreateTestEnemy(testCase);
    
    var combatResult = CombatSystem.ResolveCombat(player, enemy);
    
    Assert.IsTrue(combatResult.IsValid, $"Combat failed for enemy type: {testCase.EnemyType}");
}

private static IEnumerable<EnemyTestCase> GenerateEnemyTestCases()
{
    // AI-generated test cases covering edge cases
    return AITestGenerator.GenerateEnemyCombatScenarios();
}
```

---

## 💡 Professional Development Integration

### Continuous Integration Testing

**Automated Test Pipeline:**
```yaml
# Unity Cloud Build or GitHub Actions
name: Unity Test Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: game-ci/unity-test-runner@v2
        with:
          testMode: all
          coverageOptions: 'generateAdditionalMetrics;generateHtmlReport;generateBadgeReport'
      - uses: actions/upload-artifact@v3
        with:
          name: Coverage Report
          path: CodeCoverage/
```

### Test-Driven Development in Unity

**Red-Green-Refactor Workflow:**
```csharp
// 1. RED - Write failing test first
[Test]
public void InventorySystem_AddItem_ReturnsTrue_WhenSpaceAvailable()
{
    var inventory = new InventorySystem(capacity: 10);
    var item = new Item("Sword", weight: 5);
    
    bool result = inventory.AddItem(item);
    
    Assert.IsTrue(result);
    Assert.AreEqual(1, inventory.ItemCount);
}

// 2. GREEN - Write minimal code to pass
public class InventorySystem
{
    private List<Item> items = new List<Item>();
    private int capacity;
    
    public InventorySystem(int capacity) { this.capacity = capacity; }
    
    public bool AddItem(Item item)
    {
        if (items.Count < capacity)
        {
            items.Add(item);
            return true;
        }
        return false;
    }
    
    public int ItemCount => items.Count;
}

// 3. REFACTOR - Improve implementation while keeping tests green
```

### Code Coverage and Quality Metrics

**Coverage Analysis Setup:**
```csharp
[assembly: System.Runtime.CompilerServices.InternalsVisibleTo("Unity.TestRunner")]
[assembly: System.Runtime.CompilerServices.InternalsVisibleTo("Tests")]

// Custom coverage attributes for untestable code
[System.AttributeUsage(System.AttributeTargets.Method | System.AttributeTargets.Class)]
public class ExcludeFromCoverageAttribute : System.Attribute
{
    public string Reason { get; }
    
    public ExcludeFromCoverageAttribute(string reason)
    {
        Reason = reason;
    }
}

// Usage
[ExcludeFromCoverage("Unity lifecycle method")]
void Start()
{
    // Unity-specific initialization that doesn't need testing
}
```

---

## 🎯 Interview Preparation & Key Takeaways

### Common Testing/Debugging Interview Questions

**"How do you approach testing in Unity projects?"**
- Unit tests for game logic using Unity Test Framework
- Integration tests for component interactions and scene behavior
- Performance tests to catch regressions and ensure scalability
- Manual testing strategies for user experience validation

**"Describe your debugging process for complex issues"**
- Systematic reproduction of bugs in isolated environments
- Use of Unity's debugging tools (Console, Profiler, Frame Debugger)
- Implementation of custom logging and debug visualization
- Collaborative debugging techniques and documentation

**"How do you ensure code quality in a team environment?"**
- Test-driven development practices with comprehensive coverage
- Automated testing in CI/CD pipelines
- Code review processes with quality gates
- Performance monitoring and regression detection

### Essential Testing & Debugging Skills

**Technical Proficiency:**
- Unity Test Framework expertise for automated testing
- Proficiency with Unity's debugging and profiling tools
- Performance optimization techniques and memory management
- Custom tooling development for testing and debugging workflows

**Professional Workflow:**
- Test-driven development methodology
- Continuous integration and automated quality assurance
- Bug tracking and resolution documentation
- Team collaboration on testing strategies and standards

**Industry Best Practices:**
- Comprehensive test coverage for critical game systems
- Performance testing and optimization workflows
- Documentation of testing procedures and debugging techniques
- Knowledge sharing and mentoring on quality assurance practices