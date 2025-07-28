# @c-Unity Component Documentation Standards

## 🎯 Learning Objectives
- Master comprehensive component documentation standards for Unity development
- Implement consistent code documentation patterns that enhance team collaboration
- Create self-documenting code that reduces onboarding time and maintenance overhead
- Build documentation systems that integrate with Unity's workflow and tooling

## 🔧 Component Documentation Framework

### MonoBehaviour Documentation Template
```csharp
/// <summary>
/// PlayerController - Handles player movement, input processing, and state management
/// 
/// Design Document Reference: Section 3.2 - Player Mechanics
/// Architecture Pattern: Component-based with event-driven communication
/// Performance Requirements: < 0.5ms per frame, 60 FPS target
/// 
/// Dependencies:
/// - Rigidbody2D: Physics-based movement
/// - Collider2D: Collision detection
/// - PlayerInputActions: New Input System integration
/// - PlayerModel: Data persistence and state
/// 
/// Usage:
/// 1. Attach to Player GameObject
/// 2. Configure movement parameters in inspector
/// 3. Assign input action asset
/// 4. Connect to PlayerModel ScriptableObject
/// 
/// Testing:
/// - Unit tests: TestPlayerMovement.cs
/// - Integration tests: PlayerControllerIntegrationTests.cs
/// - Performance tests: MovementPerformanceTests.cs
/// 
/// Known Issues:
/// - Issue #123: Edge case with wall jumping on steep angles
/// - TODO: Implement coyote time for better jump feel
/// 
/// Version History:
/// v1.0 - Initial implementation (2024-01-15)
/// v1.1 - Added double jump mechanic (2024-02-01)
/// v1.2 - Improved input responsiveness (2024-02-15)
/// </summary>
[RequireComponent(typeof(Rigidbody2D))]
[RequireComponent(typeof(Collider2D))]
[DisallowMultipleComponent]
public class PlayerController : MonoBehaviour, IMovementController, IInputHandler
{
    #region Inspector Configuration
    
    [Header("Movement Settings")]
    [Tooltip("Maximum horizontal movement speed in units per second")]
    [SerializeField, Range(1f, 20f)] private float maxMoveSpeed = 8f;
    
    [Tooltip("Time to reach maximum speed from standstill")]
    [SerializeField, Range(0.1f, 2f)] private float accelerationTime = 0.2f;
    
    [Tooltip("Jump force applied when jump input is detected")]
    [SerializeField, Range(5f, 30f)] private float jumpForce = 15f;
    
    [Header("Input Configuration")]
    [Tooltip("Input Action Asset containing player controls")]
    [SerializeField] private InputActionAsset inputActions;
    
    [Header("Dependencies")]
    [Tooltip("Player data model - contains persistent player state")]
    [SerializeField] private PlayerModel playerModel;
    
    [Tooltip("Audio source for movement sound effects")]
    [SerializeField] private AudioSource movementAudioSource;
    
    [Header("Debug and Validation")]
    [Tooltip("Enable debug visualization for movement states")]
    [SerializeField] private bool showDebugInfo = false;
    
    [Tooltip("Log performance metrics to console")]
    [SerializeField] private bool logPerformanceMetrics = false;
    
    [Tooltip("Validate component setup on Start()")]
    [SerializeField] private bool validateSetup = true;
    
    #endregion
    
    #region Private Fields
    
    /// <summary>Cached Rigidbody2D component for physics operations</summary>
    private Rigidbody2D playerRigidbody;
    
    /// <summary>Current horizontal movement input (-1 to 1)</summary>
    private float currentMovementInput;
    
    /// <summary>Is the player currently grounded?</summary>
    private bool isGrounded;
    
    /// <summary>Performance tracking for frame time</summary>
    private float lastFrameTime;
    
    #endregion
    
    #region Unity Lifecycle
    
    /// <summary>
    /// Initialize component references and validate setup
    /// Called once when component is first loaded
    /// </summary>
    private void Awake()
    {
        CacheComponentReferences();
        InitializeInputSystem();
        
        if (validateSetup)
        {
            ValidateComponentSetup();
        }
    }
    
    /// <summary>
    /// Subscribe to events and initialize systems
    /// Called after all Awake() calls are complete
    /// </summary>
    private void Start()
    {
        SubscribeToEvents();
        InitializePlayerState();
        LogComponentInitialization();
    }
    
    /// <summary>
    /// Handle physics-based movement updates
    /// Called at fixed timestep for consistent physics
    /// </summary>
    private void FixedUpdate()
    {
        if (logPerformanceMetrics)
        {
            lastFrameTime = Time.realtimeSinceStartup;
        }
        
        ProcessMovementInput();
        UpdateGroundedState();
        
        if (logPerformanceMetrics)
        {
            LogPerformanceMetrics();
        }
    }
    
    /// <summary>
    /// Handle debug visualization and UI updates
    /// Called once per frame at variable timestep
    /// </summary>
    private void Update()
    {
        if (showDebugInfo)
        {
            DrawDebugInformation();
        }
    }
    
    /// <summary>
    /// Clean up event subscriptions and resources
    /// Called when component is destroyed
    /// </summary>
    private void OnDestroy()
    {
        UnsubscribeFromEvents();
        CleanupInputSystem();
    }
    
    #endregion
    
    #region Initialization Methods
    
    /// <summary>
    /// Cache frequently used component references for performance
    /// Reduces GetComponent() calls during gameplay
    /// </summary>
    private void CacheComponentReferences()
    {
        playerRigidbody = GetComponent<Rigidbody2D>();
        
        // Validate critical components exist
        if (playerRigidbody == null)
        {
            Debug.LogError($"[{GetType().Name}] Rigidbody2D component is required", this);
        }
    }
    
    /// <summary>
    /// Initialize the new Input System with action callbacks
    /// Configures input handling for movement and jump actions
    /// </summary>
    private void InitializeInputSystem()
    {
        if (inputActions == null)
        {
            Debug.LogError($"[{GetType().Name}] Input Actions asset is not assigned", this);
            return;
        }
        
        // Enable input actions and bind callbacks
        inputActions.Enable();
        
        var moveAction = inputActions.FindAction("Move");
        var jumpAction = inputActions.FindAction("Jump");
        
        if (moveAction != null)
        {
            moveAction.performed += OnMoveInput;
            moveAction.canceled += OnMoveInput;
        }
        
        if (jumpAction != null)
        {
            jumpAction.performed += OnJumpInput;
        }
    }
    
    /// <summary>
    /// Validate that all required components and references are properly configured
    /// Helps catch setup issues early in development
    /// </summary>
    private void ValidateComponentSetup()
    {
        var validationResults = new List<string>();
        
        // Check required components
        if (GetComponent<Rigidbody2D>() == null)
            validationResults.Add("Missing required Rigidbody2D component");
        
        if (GetComponent<Collider2D>() == null)
            validationResults.Add("Missing required Collider2D component");
        
        // Check configuration
        if (inputActions == null)
            validationResults.Add("Input Actions asset not assigned");
        
        if (playerModel == null)
            validationResults.Add("Player Model not assigned - some features may not work");
        
        // Check value ranges
        if (maxMoveSpeed <= 0)
            validationResults.Add("Max Move Speed must be greater than 0");
        
        if (jumpForce <= 0)
            validationResults.Add("Jump Force must be greater than 0");
        
        // Report validation results
        if (validationResults.Count > 0)
        {
            string errorMessage = $"[{GetType().Name}] Setup validation failed:\n";
            errorMessage += string.Join("\n", validationResults);
            Debug.LogError(errorMessage, this);
        }
        else
        {
            Debug.Log($"[{GetType().Name}] Component setup validation passed", this);
        }
    }
    
    #endregion
    
    #region Input Handling
    
    /// <summary>
    /// Handle movement input from the Input System
    /// Updates movement state based on player input
    /// </summary>
    /// <param name="context">Input action context containing input data</param>
    private void OnMoveInput(InputAction.CallbackContext context)
    {
        currentMovementInput = context.ReadValue<Vector2>().x;
        
        if (showDebugInfo)
        {
            Debug.Log($"[Input] Movement input: {currentMovementInput}", this);
        }
    }
    
    /// <summary>
    /// Handle jump input from the Input System
    /// Processes jump action when input is detected
    /// </summary>
    /// <param name="context">Input action context containing input data</param>
    private void OnJumpInput(InputAction.CallbackContext context)
    {
        if (context.performed && isGrounded)
        {
            PerformJump();
        }
    }
    
    #endregion
    
    #region Movement Implementation
    
    /// <summary>
    /// Process horizontal movement based on current input
    /// Applies physics-based movement with acceleration/deceleration
    /// </summary>
    private void ProcessMovementInput()
    {
        // Calculate target velocity based on input
        float targetVelocity = currentMovementInput * maxMoveSpeed;
        
        // Apply acceleration/deceleration
        float velocityDifference = targetVelocity - playerRigidbody.velocity.x;
        float accelerationRate = 1f / accelerationTime;
        float movement = velocityDifference * accelerationRate * Time.fixedDeltaTime;
        
        // Apply movement to rigidbody
        playerRigidbody.velocity = new Vector2(
            playerRigidbody.velocity.x + movement,
            playerRigidbody.velocity.y
        );
        
        // Update player model if available
        if (playerModel != null)
        {
            playerModel.SetMovementState(currentMovementInput != 0);
        }
    }
    
    /// <summary>
    /// Execute jump action with physics force
    /// Applies upward force and updates player state
    /// </summary>
    private void PerformJump()
    {
        // Apply jump force
        playerRigidbody.velocity = new Vector2(playerRigidbody.velocity.x, jumpForce);
        
        // Update state
        isGrounded = false;
        
        // Play jump sound effect
        if (movementAudioSource != null)
        {
            movementAudioSource.Play();
        }
        
        // Update player model
        if (playerModel != null)
        {
            playerModel.TriggerJump();
        }
        
        if (showDebugInfo)
        {
            Debug.Log($"[Movement] Jump performed with force: {jumpForce}", this);
        }
    }
    
    #endregion
    
    #region Debug and Performance
    
    /// <summary>
    /// Draw debug information in Scene view
    /// Visualizes component state for development
    /// </summary>
    private void DrawDebugInformation()
    {
        // Draw movement vector
        Vector3 position = transform.position;
        Vector3 velocityVector = new Vector3(playerRigidbody.velocity.x, 0, 0);
        
        Debug.DrawRay(position, velocityVector, Color.green);
        
        // Draw grounded state
        Color groundedColor = isGrounded ? Color.green : Color.red;
        Debug.DrawRay(position + Vector3.down * 0.5f, Vector3.down * 0.5f, groundedColor);
    }
    
    /// <summary>
    /// Log performance metrics for optimization analysis
    /// Tracks frame time and component performance
    /// </summary>
    private void LogPerformanceMetrics()
    {
        float frameTime = (Time.realtimeSinceStartup - lastFrameTime) * 1000f;
        
        if (frameTime > 0.5f) // Log if frame time exceeds 0.5ms
        {
            Debug.LogWarning($"[Performance] {GetType().Name} frame time: {frameTime:F3}ms", this);
        }
    }
    
    /// <summary>
    /// Log component initialization for debugging
    /// Provides visibility into component lifecycle
    /// </summary>
    private void LogComponentInitialization()
    {
        Debug.Log($"[{GetType().Name}] Component initialized successfully. " +
                 $"Max Speed: {maxMoveSpeed}, Jump Force: {jumpForce}", this);
    }
    
    #endregion
    
    #region Public Interface
    
    /// <summary>
    /// Get current movement speed for external systems
    /// </summary>
    /// <returns>Current horizontal movement speed</returns>
    public float GetCurrentSpeed()
    {
        return Mathf.Abs(playerRigidbody.velocity.x);
    }
    
    /// <summary>
    /// Check if player is currently grounded
    /// </summary>
    /// <returns>True if player is on ground, false otherwise</returns>
    public bool IsGrounded()
    {
        return isGrounded;
    }
    
    /// <summary>
    /// Temporarily disable player input (for cutscenes, menus, etc.)
    /// </summary>
    /// <param name="disabled">True to disable input, false to enable</param>
    public void SetInputDisabled(bool disabled)
    {
        if (disabled)
        {
            inputActions?.Disable();
        }
        else
        {
            inputActions?.Enable();
        }
    }
    
    #endregion
}
```

## 🚀 AI/LLM Integration Opportunities

### AI-Enhanced Documentation Generation
```yaml
AI_Documentation_Enhancement:
  automated_documentation:
    - Component summary generation from code analysis
    - Parameter description generation from usage patterns
    - Cross-reference generation between related components
    - Performance impact documentation from profiling data
  
  code_analysis:
    - Dependency analysis and documentation
    - Usage pattern identification and documentation
    - Performance bottleneck identification
    - Best practice compliance checking
  
  maintenance_support:
    - Automated documentation updates from code changes
    - Inconsistency detection between code and documentation
    - Missing documentation identification
    - Documentation quality scoring and improvement suggestions
```

### Intelligent Code Documentation Tools
```python
class UnityComponentDocumentationGenerator:
    def __init__(self, unity_project_path):
        self.project_path = unity_project_path
        self.component_analyzer = ComponentAnalyzer()
        
    def generate_component_documentation(self, component_script_path):
        """AI-powered component documentation generation"""
        component_analysis = {
            'class_analysis': self._analyze_component_class(component_script_path),
            'method_documentation': self._generate_method_docs(component_script_path),
            'field_documentation': self._generate_field_docs(component_script_path),
            'usage_examples': self._generate_usage_examples(component_script_path),
            'performance_notes': self._analyze_performance_implications(component_script_path)
        }
        
        return self._format_documentation(component_analysis)
    
    def validate_documentation_quality(self, component_script_path):
        """Assess documentation quality and provide improvement suggestions"""
        quality_metrics = {
            'completeness_score': self._assess_documentation_completeness(component_script_path),
            'clarity_score': self._assess_documentation_clarity(component_script_path),
            'accuracy_score': self._validate_documentation_accuracy(component_script_path),
            'maintenance_score': self._assess_maintenance_quality(component_script_path),
            'improvement_suggestions': self._generate_improvement_suggestions(component_script_path)
        }
        
        return quality_metrics
    
    def generate_component_relationships(self, component_list):
        """Map relationships and dependencies between components"""
        relationship_map = {}
        
        for component in component_list:
            relationships = {
                'dependencies': self._find_component_dependencies(component),
                'dependents': self._find_component_dependents(component),
                'communication_patterns': self._analyze_communication(component),
                'data_flow': self._map_data_flow(component)
            }
            
            relationship_map[component.name] = relationships
        
        return relationship_map
```

## 💡 ScriptableObject Documentation Standards

### Data Asset Documentation Template
```csharp
/// <summary>
/// WeaponData - Configuration data for weapon systems
/// 
/// Design Document Reference: Section 4.1 - Combat System
/// Data Architecture: ScriptableObject-based configuration system
/// Usage Pattern: Factory pattern for weapon instantiation
/// 
/// Configuration Guidelines:
/// - Damage values should follow damage curve in design document
/// - Fire rate affects game balance - coordinate with design team
/// - Audio clips should follow naming convention: "weapon_[type]_[action]"
/// 
/// Validation Rules:
/// - Damage must be positive and within balance ranges
/// - Fire rate cannot exceed engine limitations (60 shots/sec)
/// - Range values must be realistic for game scale
/// 
/// Testing:
/// - Balance tests: WeaponBalanceTests.cs
/// - Integration tests: WeaponSystemTests.cs
/// - Performance tests: WeaponPerformanceTests.cs
/// </summary>
[CreateAssetMenu(fileName = "NewWeaponData", menuName = "Game/Weapons/Weapon Data")]
public class WeaponData : ScriptableObject, IValidatable
{
    #region Basic Properties
    
    [Header("Weapon Identity")]
    [Tooltip("Display name shown to players")]
    public string weaponName = "New Weapon";
    
    [Tooltip("Unique identifier for save system and networking")]
    public string weaponID = "";
    
    [Tooltip("Weapon category for inventory organization")]
    public WeaponCategory category = WeaponCategory.Primary;
    
    [Header("Combat Statistics")]
    [Tooltip("Base damage per shot (before modifiers)")]
    [Range(1, 1000)]
    public int baseDamage = 10;
    
    [Tooltip("Shots per second firing rate")]
    [Range(0.1f, 60f)]
    public float fireRate = 1f;
    
    [Tooltip("Maximum effective range in world units")]
    [Range(1f, 100f)]
    public float range = 10f;
    
    [Tooltip("Accuracy percentage (0-100)")]
    [Range(0f, 100f)]
    public float accuracy = 80f;
    
    #endregion
    
    #region Audio Configuration
    
    [Header("Audio Settings")]
    [Tooltip("Sound played when weapon fires")]
    public AudioClip fireSound;
    
    [Tooltip("Sound played when reloading")]
    public AudioClip reloadSound;
    
    [Tooltip("Sound played when weapon is empty")]
    public AudioClip emptySound;
    
    [Tooltip("Volume modifier for weapon sounds (0-1)")]
    [Range(0f, 1f)]
    public float audioVolume = 1f;
    
    #endregion
    
    #region Visual Configuration
    
    [Header("Visual Settings")]
    [Tooltip("Prefab instantiated when weapon fires")]
    public GameObject muzzleFlashPrefab;
    
    [Tooltip("Projectile prefab for ballistic weapons")]
    public GameObject projectilePrefab;
    
    [Tooltip("Impact effect when projectile hits target")]
    public GameObject impactEffectPrefab;
    
    #endregion
    
    #region Balance Configuration
    
    [Header("Balance Settings")]
    [Tooltip("Weapon tier for progression system (1-5)")]
    [Range(1, 5)]
    public int weaponTier = 1;
    
    [Tooltip("Resource cost to use weapon")]
    public ResourceCost ammunitionCost;
    
    [Tooltip("Experience points awarded for kills with this weapon")]
    [Range(1, 100)]
    public int experienceReward = 10;
    
    [Header("Upgrade Configuration")]
    [Tooltip("Available upgrade paths for this weapon")]
    public WeaponUpgrade[] availableUpgrades;
    
    #endregion
    
    #region Documentation and Validation
    
    [Header("Documentation")]
    [TextArea(3, 5)]
    [Tooltip("Design notes and balance considerations")]
    public string designNotes = "";
    
    [TextArea(2, 3)]
    [Tooltip("Known issues or limitations")]
    public string knownIssues = "";
    
    [Header("Validation")]
    [Tooltip("Enable runtime validation of weapon parameters")]
    public bool enableValidation = true;
    
    [Tooltip("Reference to design document balance sheet")]
    public TextAsset balanceReference;
    
    #endregion
    
    #region Validation Implementation
    
    /// <summary>
    /// Validate weapon configuration against design requirements
    /// Called automatically when asset is modified in editor
    /// </summary>
    public ValidationResult Validate()
    {
        var result = new ValidationResult();
        
        // Validate basic properties
        if (string.IsNullOrEmpty(weaponName))
        {
            result.AddError("Weapon name cannot be empty");
        }
        
        if (string.IsNullOrEmpty(weaponID))
        {
            result.AddError("Weapon ID must be set for save system compatibility");
        }
        
        // Validate balance parameters
        if (baseDamage <= 0)
        {
            result.AddError("Base damage must be positive");
        }
        
        if (fireRate <= 0)
        {
            result.AddError("Fire rate must be positive");
        }
        
        // Validate against design document ranges
        if (enableValidation && balanceReference != null)
        {
            ValidateAgainstDesignDocument(result);
        }
        
        // Validate audio configuration
        if (fireSound == null)
        {
            result.AddWarning("Fire sound not assigned - weapon will be silent");
        }
        
        return result;
    }
    
    /// <summary>
    /// Validate weapon parameters against design document specifications
    /// Ensures consistency with documented balance requirements
    /// </summary>
    private void ValidateAgainstDesignDocument(ValidationResult result)
    {
        // Parse balance reference document
        var balanceData = ParseBalanceDocument(balanceReference);
        
        if (balanceData.TryGetValue($"{category}_damage_range", out var damageRange))
        {
            var range = (Vector2)damageRange;
            if (baseDamage < range.x || baseDamage > range.y)
            {
                result.AddWarning($"Base damage {baseDamage} outside design range [{range.x}-{range.y}]");
            }
        }
        
        if (balanceData.TryGetValue($"{category}_fire_rate_range", out var fireRateRange))
        {
            var range = (Vector2)fireRateRange;
            if (fireRate < range.x || fireRate > range.y)
            {
                result.AddWarning($"Fire rate {fireRate} outside design range [{range.x}-{range.y}]");
            }
        }
    }
    
    #endregion
    
    #region Editor Utilities
    
    [ContextMenu("Generate Weapon ID")]
    private void GenerateWeaponID()
    {
        weaponID = $"{category}_{weaponName.Replace(" ", "").ToLower()}_{GetInstanceID()}";
        #if UNITY_EDITOR
        UnityEditor.EditorUtility.SetDirty(this);
        #endif
    }
    
    [ContextMenu("Validate Configuration")]
    private void ValidateInEditor()
    {
        var result = Validate();
        
        if (result.HasErrors)
        {
            Debug.LogError($"Weapon validation failed for {weaponName}:\n{result.GetErrorSummary()}", this);
        }
        else if (result.HasWarnings)
        {
            Debug.LogWarning($"Weapon validation warnings for {weaponName}:\n{result.GetWarningSummary()}", this);
        }
        else
        {
            Debug.Log($"Weapon validation passed for {weaponName}", this);
        }
    }
    
    [ContextMenu("Export Documentation")]
    private void ExportDocumentation()
    {
        var documentation = GenerateDocumentation();
        
        #if UNITY_EDITOR
        var path = UnityEditor.EditorUtility.SaveFilePanel("Export Weapon Documentation", 
            Application.dataPath, $"{weaponName}_Documentation", "md");
            
        if (!string.IsNullOrEmpty(path))
        {
            System.IO.File.WriteAllText(path, documentation);
            Debug.Log($"Documentation exported to: {path}", this);
        }
        #endif
    }
    
    /// <summary>
    /// Generate comprehensive documentation for this weapon
    /// Creates markdown documentation with all configuration details
    /// </summary>
    private string GenerateDocumentation()
    {
        var doc = new StringBuilder();
        
        doc.AppendLine($"# {weaponName} Documentation");
        doc.AppendLine();
        doc.AppendLine($"**Weapon ID:** {weaponID}");
        doc.AppendLine($"**Category:** {category}");
        doc.AppendLine($"**Tier:** {weaponTier}");
        doc.AppendLine();
        
        doc.AppendLine("## Combat Statistics");
        doc.AppendLine($"- **Base Damage:** {baseDamage}");
        doc.AppendLine($"- **Fire Rate:** {fireRate} shots/sec");
        doc.AppendLine($"- **Range:** {range} units");
        doc.AppendLine($"- **Accuracy:** {accuracy}%");
        doc.AppendLine();
        
        if (!string.IsNullOrEmpty(designNotes))
        {
            doc.AppendLine("## Design Notes");
            doc.AppendLine(designNotes);
            doc.AppendLine();
        }
        
        if (!string.IsNullOrEmpty(knownIssues))
        {
            doc.AppendLine("## Known Issues");
            doc.AppendLine(knownIssues);
            doc.AppendLine();
        }
        
        // Add validation results
        var validation = Validate();
        if (validation.HasIssues)
        {
            doc.AppendLine("## Validation Results");
            doc.AppendLine(validation.ToString());
        }
        
        return doc.ToString();
    }
    
    #endregion
}
```

## 🔧 Interface and System Documentation

### Interface Documentation Standards
```csharp
/// <summary>
/// IMovementController - Standard interface for all movement systems
/// 
/// Design Pattern: Interface Segregation Principle
/// Usage: Implement for any object that needs standardized movement control
/// Testing: All implementations must pass IMovementControllerTests
/// 
/// Implementation Guidelines:
/// - All movement should be physics-based for consistency
/// - Speed values should be in world units per second
/// - Movement state should be queryable for animation systems
/// - Input handling should be separated from movement logic
/// 
/// Performance Requirements:
/// - Movement updates must complete within 0.1ms
/// - No memory allocations during movement updates
/// - Use object pooling for temporary movement calculations
/// </summary>
public interface IMovementController
{
    /// <summary>
    /// Current movement speed in world units per second
    /// Used by animation systems and UI displays
    /// </summary>
    float CurrentSpeed { get; }
    
    /// <summary>
    /// Maximum possible movement speed for this controller
    /// Used for balance calculations and effect scaling
    /// </summary>
    float MaxSpeed { get; }
    
    /// <summary>
    /// Is the movement controller currently able to move?
    /// False during stunned, frozen, or disabled states
    /// </summary>
    bool CanMove { get; }
    
    /// <summary>
    /// Move in specified direction with given intensity
    /// </summary>
    /// <param name="direction">Normalized direction vector</param>
    /// <param name="intensity">Movement intensity (0-1)</param>
    void Move(Vector2 direction, float intensity = 1f);
    
    /// <summary>
    /// Stop all movement immediately
    /// Used for emergency stops, cutscenes, and state transitions
    /// </summary>
    void Stop();
    
    /// <summary>
    /// Temporarily disable movement (for cutscenes, menus, etc.)
    /// </summary>
    /// <param name="disabled">True to disable, false to enable</param>
    void SetMovementDisabled(bool disabled);
    
    /// <summary>
    /// Event fired when movement state changes
    /// Subscribe for animation triggers and sound effects
    /// </summary>
    event System.Action<bool> OnMovementStateChanged;
}
```

This comprehensive Unity component documentation framework establishes clear standards for code documentation, validation, and maintenance across game development teams, with particular emphasis on Unity-specific patterns and AI-enhanced documentation workflows.