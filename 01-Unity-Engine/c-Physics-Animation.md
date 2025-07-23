# @c-Physics-Animation - Unity Physics & Animation Systems

## 🎯 Learning Objectives
- Master Unity's physics system (Rigidbody, Colliders, Joints)
- Understand animation workflows (Animator, Animation, Timeline)
- Learn physics-based character movement and interactions
- Leverage AI to optimize physics performance and create animation assets

---

## ⚡ Unity Physics System

### Rigidbody Fundamentals
```csharp
public class PhysicsPlayer : MonoBehaviour
{
    [SerializeField] private Rigidbody rb;
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float jumpForce = 10f;
    
    void Awake()
    {
        rb = GetComponent<Rigidbody>();
    }
    
    void FixedUpdate() // Always use FixedUpdate for physics!
    {
        // Movement with physics
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");
        
        Vector3 movement = new Vector3(horizontal, 0, vertical) * moveSpeed;
        rb.velocity = new Vector3(movement.x, rb.velocity.y, movement.z);
    }
    
    void Update()
    {
        // Jump input detection
        if (Input.GetKeyDown(KeyCode.Space) && IsGrounded())
        {
            rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
        }
    }
}
```

### Collision Detection
```csharp
public class CollisionHandler : MonoBehaviour
{
    // Trigger events (isTrigger = true)
    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            Debug.Log("Player entered trigger zone");
        }
    }
    
    void OnTriggerStay(Collider other) { /* While overlapping */ }
    void OnTriggerExit(Collider other) { /* When leaving */ }
    
    // Collision events (isTrigger = false)
    void OnCollisionEnter(Collision collision)
    {
        // Access collision data
        ContactPoint contact = collision.contacts[0];
        Vector3 hitPoint = contact.point;
        Vector3 hitNormal = contact.normal;
        
        if (collision.gameObject.CompareTag("Enemy"))
        {
            TakeDamage(10);
        }
    }
}
```

### Advanced Physics Techniques
```csharp
public class AdvancedPhysics : MonoBehaviour
{
    [SerializeField] private Rigidbody rb;
    
    void FixedUpdate()
    {
        // Different force application methods
        rb.AddForce(Vector3.forward * 10f);              // Continuous force
        rb.AddForce(Vector3.up * 500f, ForceMode.Impulse); // Instant impulse
        rb.AddTorque(Vector3.up * 10f);                  // Rotational force
        
        // Direct velocity manipulation
        rb.velocity = Vector3.ClampMagnitude(rb.velocity, maxSpeed);
        
        // Raycast for ground detection
        if (Physics.Raycast(transform.position, Vector3.down, 1.1f))
        {
            isGrounded = true;
        }
    }
    
    // Custom gravity
    void ApplyCustomGravity()
    {
        rb.useGravity = false; // Disable Unity's gravity
        rb.AddForce(Vector3.down * customGravityStrength);
    }
}
```

---

## 🎭 Animation System

### Animator Controller Setup
```csharp
public class AnimationController : MonoBehaviour
{
    [SerializeField] private Animator animator;
    [SerializeField] private float speed;
    
    void Update()
    {
        // Set animator parameters
        animator.SetFloat("Speed", speed);
        animator.SetBool("IsGrounded", IsGrounded());
        animator.SetTrigger("Jump"); // One-time trigger
        
        // Get current animation info
        AnimatorStateInfo stateInfo = animator.GetCurrentAnimatorStateInfo(0);
        if (stateInfo.IsName("JumpAnimation") && stateInfo.normalizedTime >= 1.0f)
        {
            // Jump animation finished
        }
    }
    
    // Animation Events (called from Animation clips)
    public void OnFootstep()
    {
        // Play footstep sound
        AudioSource.PlayClipAtPoint(footstepClip, transform.position);
    }
    
    public void OnAttackHit()
    {
        // Deal damage during attack animation
        DealDamageInRange();
    }
}
```

### Procedural Animation
```csharp
public class ProceduralAnimation : MonoBehaviour
{
    [SerializeField] private Transform target;
    [SerializeField] private float bobSpeed = 2f;
    [SerializeField] private float bobHeight = 0.5f;
    
    private Vector3 startPosition;
    
    void Start()
    {
        startPosition = transform.position;
    }
    
    void Update()
    {
        // Simple bobbing animation
        float newY = startPosition.y + Mathf.Sin(Time.time * bobSpeed) * bobHeight;
        transform.position = new Vector3(transform.position.x, newY, transform.position.z);
        
        // Smooth rotation towards target
        if (target != null)
        {
            Vector3 direction = (target.position - transform.position).normalized;
            Quaternion lookRotation = Quaternion.LookRotation(direction);
            transform.rotation = Quaternion.Slerp(transform.rotation, lookRotation, Time.deltaTime * 2f);
        }
    }
}
```

### Timeline and Cinemachine Integration
```csharp
using UnityEngine.Playables;
using UnityEngine.Timeline;

public class CutsceneManager : MonoBehaviour
{
    [SerializeField] private PlayableDirector timeline;
    
    public void PlayCutscene()
    {
        timeline.Play();
    }
    
    public void PauseCutscene()
    {
        timeline.Pause();
    }
    
    // Timeline Signal Receiver methods
    public void OnCutsceneStart()
    {
        // Disable player input
        GetComponent<PlayerInput>().enabled = false;
    }
    
    public void OnCutsceneEnd()
    {
        // Re-enable player input
        GetComponent<PlayerInput>().enabled = true;
    }
}
```

---

## 🚀 AI/LLM Integration for Physics & Animation

### Physics Optimization with AI
**Performance Analysis Prompt:**
> "Analyze this Unity physics script for performance bottlenecks and suggest optimizations: [paste code]"

**Physics Debugging:**
> "My Unity character is jittery when moving. The Rigidbody has these settings: [settings]. What could be causing this?"

### Animation Asset Generation
**Animation Planning:**
> "Create a state machine diagram for a 2D platformer character with idle, run, jump, fall, and attack states"

**Blend Tree Setup:**
> "Explain how to set up a blend tree in Unity for smooth 8-directional character movement"

### Code Generation Examples
```csharp
// AI-generated ground detection system
public class GroundDetection : MonoBehaviour
{
    [SerializeField] private Transform groundCheckPoint;
    [SerializeField] private float groundCheckRadius = 0.1f;
    [SerializeField] private LayerMask groundLayerMask;
    
    public bool IsGrounded()
    {
        return Physics.CheckSphere(groundCheckPoint.position, groundCheckRadius, groundLayerMask);
    }
    
    void OnDrawGizmosSelected()
    {
        if (groundCheckPoint != null)
        {
            Gizmos.color = IsGrounded() ? Color.green : Color.red;
            Gizmos.DrawWireSphere(groundCheckPoint.position, groundCheckRadius);
        }
    }
}
```

---

## 🎮 Common Physics & Animation Patterns

### Character Controller (Physics-Based)
```csharp
public class PhysicsCharacterController : MonoBehaviour
{
    [Header("Movement")]
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float airControl = 0.5f;
    
    [Header("Jumping")]
    [SerializeField] private float jumpForce = 10f;
    [SerializeField] private float fallMultiplier = 2.5f;
    [SerializeField] private float lowJumpMultiplier = 2f;
    
    private Rigidbody rb;
    private bool isGrounded;
    private float horizontal;
    
    void Awake()
    {
        rb = GetComponent<Rigidbody>();
    }
    
    void Update()
    {
        horizontal = Input.GetAxis("Horizontal");
        
        if (Input.GetKeyDown(KeyCode.Space) && isGrounded)
        {
            rb.velocity = new Vector3(rb.velocity.x, jumpForce, rb.velocity.z);
        }
    }
    
    void FixedUpdate()
    {
        // Ground movement vs air movement
        float currentMoveSpeed = isGrounded ? moveSpeed : moveSpeed * airControl;
        rb.velocity = new Vector3(horizontal * currentMoveSpeed, rb.velocity.y, rb.velocity.z);
        
        // Better jump feel
        if (rb.velocity.y < 0)
        {
            rb.velocity += Vector3.up * Physics.gravity.y * (fallMultiplier - 1) * Time.fixedDeltaTime;
        }
        else if (rb.velocity.y > 0 && !Input.GetKey(KeyCode.Space))
        {
            rb.velocity += Vector3.up * Physics.gravity.y * (lowJumpMultiplier - 1) * Time.fixedDeltaTime;
        }
    }
}
```

### Animation State Manager
```csharp
public class AnimationStateManager : MonoBehaviour
{
    private Animator animator;
    private Rigidbody rb;
    
    // Animation parameter hashes (more efficient than strings)
    private int speedHash = Animator.StringToHash("Speed");
    private int groundedHash = Animator.StringToHash("IsGrounded");
    private int jumpHash = Animator.StringToHash("Jump");
    
    void Awake()
    {
        animator = GetComponent<Animator>();
        rb = GetComponent<Rigidbody>();
    }
    
    void Update()
    {
        UpdateAnimationParameters();
    }
    
    void UpdateAnimationParameters()
    {
        // Speed based on velocity magnitude
        float speed = new Vector3(rb.velocity.x, 0, rb.velocity.z).magnitude;
        animator.SetFloat(speedHash, speed);
        
        // Grounded state
        animator.SetBool(groundedHash, IsGrounded());
        
        // Jump trigger
        if (Input.GetKeyDown(KeyCode.Space))
        {
            animator.SetTrigger(jumpHash);
        }
    }
}
```

---

## 🎯 Practical Exercises

### Exercise 1: Physics Playground
Create a scene with:
- Bouncy balls with different physics materials
- Ramps and obstacles
- Force zones that push objects
- Interactive physics puzzles

### Exercise 2: Character Animation Setup
Build a character with:
- Basic locomotion blend tree (idle, walk, run)
- Jump/fall animations with proper transitions
- Attack animations with animation events
- Facial expressions or secondary animations

### Exercise 3: Physics-Based Puzzle
Design a puzzle involving:
- Moving platforms with joints
- Pressure plates activated by physics objects
- Chain reactions using collision events
- Player physics manipulation (pushing/pulling)

---

## 🎯 Portfolio Project Ideas

### Beginner: "Physics Demo Reel"
- Showcase different physics interactions
- Demonstrate understanding of forces, joints, materials
- Include performance comparisons

### Intermediate: "Character Movement Showcase"
- Multiple movement types (platformer, FPS, top-down)
- Smooth animation integration
- Physics-based and kinematic comparisons

### Advanced: "Physics-Based Game Mechanic"
- Original gameplay mechanic using physics
- Complex multi-object interactions
- Performance optimization documentation

---

## 🔍 Interview Preparation

### Common Questions
1. **"When would you use Rigidbody vs Character Controller?"**
   - Rigidbody: Realistic physics, environmental interactions
   - Character Controller: Precise control, predictable movement

2. **"How do you optimize physics performance?"**
   - Reduce Fixed Timestep frequency
   - Use simpler collider shapes
   - Limit Rigidbody count
   - Use collision layers efficiently

3. **"Explain the difference between Trigger and Collision events"**
   - Trigger: Detection only, objects pass through
   - Collision: Physical response, objects bounce/stop

### Technical Challenges
- Implement smooth character movement with physics
- Create a physics-based vehicle controller
- Design an animation state machine for complex character
- Optimize a scene with many physics objects

---

## ⚡ AI Productivity Hacks

### Physics Development
- Generate physics calculation formulas
- Create collision detection optimizations
- Design physics-based game mechanics
- Generate performance testing scenarios

### Animation Workflow
- Plan animation state machines with AI
- Generate animation event timing
- Create procedural animation scripts
- Design blend tree structures

### Learning Acceleration
- Generate physics problem scenarios
- Create animation timing exercises
- Build physics debugging checklists
- Generate performance profiling guides

---

## 🎯 Next Steps
1. Implement physics-based character movement
2. Create basic animation controller with blend trees
3. Move to **@d-UI-UX.md** for user interface systems
4. Build a physics + animation demo for portfolio

> **AI Integration Reminder**: Use LLMs to optimize physics calculations, plan animation workflows, and generate performance testing scenarios. Physics and animation are compute-intensive - AI can help you write more efficient code!