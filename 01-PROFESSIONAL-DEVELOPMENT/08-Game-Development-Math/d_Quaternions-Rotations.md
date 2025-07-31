# @d-Quaternions-Rotations - 3D Rotation Mathematics for Unity

## 🎯 Learning Objectives
- Master quaternion mathematics for 3D rotations
- Understand Euler angles vs quaternions in Unity
- Implement smooth rotation systems and camera controls
- Apply rotation mathematics to gameplay mechanics

## 🔧 Core Quaternion Concepts

### Mathematical Foundation
```csharp
// Quaternion representation: q = w + xi + yj + zk
public struct QuaternionExample
{
    public float w, x, y, z; // w = scalar, xyz = vector
    
    // Unity's Quaternion methods
    public static void QuaternionBasics()
    {
        // Identity quaternion (no rotation)
        Quaternion identity = Quaternion.identity;
        
        // Create from Euler angles
        Quaternion rotation = Quaternion.Euler(45f, 90f, 0f);
        
        // Create from axis-angle
        Quaternion axisRotation = Quaternion.AngleAxis(90f, Vector3.up);
        
        // Look rotation
        Vector3 direction = target.position - transform.position;
        Quaternion lookRotation = Quaternion.LookRotation(direction);
    }
}
```

### Quaternion Operations
```csharp
public class QuaternionOperations : MonoBehaviour
{
    [Header("Rotation Controls")]
    public float rotationSpeed = 90f;
    public Transform target;
    
    void Update()
    {
        // Continuous rotation
        ContinuousRotation();
        
        // Smooth look-at
        SmoothLookAt();
        
        // Relative rotations
        RelativeRotations();
    }
    
    void ContinuousRotation()
    {
        // Rotate around Y-axis
        float rotationAmount = rotationSpeed * Time.deltaTime;
        Quaternion deltaRotation = Quaternion.Euler(0, rotationAmount, 0);
        transform.rotation *= deltaRotation;
    }
    
    void SmoothLookAt()
    {
        if (target != null)
        {
            Vector3 direction = target.position - transform.position;
            Quaternion targetRotation = Quaternion.LookRotation(direction);
            
            // Smooth rotation using Slerp
            transform.rotation = Quaternion.Slerp(
                transform.rotation, 
                targetRotation, 
                Time.deltaTime * 2f
            );
        }
    }
    
    void RelativeRotations()
    {
        // Local space rotation
        if (Input.GetKey(KeyCode.Q))
            transform.Rotate(0, -rotationSpeed * Time.deltaTime, 0, Space.Self);
        
        if (Input.GetKey(KeyCode.E))
            transform.Rotate(0, rotationSpeed * Time.deltaTime, 0, Space.Self);
    }
}
```

## 🎮 Unity Rotation Systems

### Camera Controller with Quaternions
```csharp
public class QuaternionCameraController : MonoBehaviour
{
    [Header("Camera Settings")]
    public Transform target;
    public float distance = 5f;
    public float rotationSpeed = 100f;
    public float verticalLimit = 80f;
    
    private float horizontalAngle = 0f;
    private float verticalAngle = 0f;
    
    void LateUpdate()
    {
        if (target == null) return;
        
        // Get input
        float mouseX = Input.GetAxis("Mouse X") * rotationSpeed * Time.deltaTime;
        float mouseY = Input.GetAxis("Mouse Y") * rotationSpeed * Time.deltaTime;
        
        // Update angles
        horizontalAngle += mouseX;
        verticalAngle -= mouseY;
        verticalAngle = Mathf.Clamp(verticalAngle, -verticalLimit, verticalLimit);
        
        // Create rotation using quaternions
        Quaternion horizontalRotation = Quaternion.AngleAxis(horizontalAngle, Vector3.up);
        Quaternion verticalRotation = Quaternion.AngleAxis(verticalAngle, Vector3.right);
        Quaternion finalRotation = horizontalRotation * verticalRotation;
        
        // Position camera
        Vector3 offset = finalRotation * Vector3.back * distance;
        transform.position = target.position + offset;
        transform.rotation = finalRotation;
    }
}
```

### Character Rotation System
```csharp
public class CharacterRotationController : MonoBehaviour
{
    [Header("Rotation Settings")]
    public float turnSpeed = 180f;
    public bool smoothRotation = true;
    public float smoothTime = 0.1f;
    
    private CharacterController controller;
    private Vector3 moveDirection;
    
    void Start()
    {
        controller = GetComponent<CharacterController>();
    }
    
    void Update()
    {
        HandleMovementInput();
        UpdateRotation();
    }
    
    void HandleMovementInput()
    {
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");
        
        moveDirection = new Vector3(horizontal, 0, vertical).normalized;
    }
    
    void UpdateRotation()
    {
        if (moveDirection.magnitude > 0.1f)
        {
            // Calculate target rotation
            Quaternion targetRotation = Quaternion.LookRotation(moveDirection);
            
            if (smoothRotation)
            {
                // Smooth rotation
                transform.rotation = Quaternion.Slerp(
                    transform.rotation,
                    targetRotation,
                    turnSpeed * Time.deltaTime
                );
            }
            else
            {
                // Instant rotation
                transform.rotation = targetRotation;
            }
        }
    }
}
```

## 🔄 Advanced Rotation Techniques

### Gimbal Lock Prevention
```csharp
public class GimbalLockDemo : MonoBehaviour
{
    [Header("Rotation Comparison")]
    public Transform eulerObject;
    public Transform quaternionObject;
    
    [Header("Controls")]
    public Vector3 eulerAngles;
    
    void Update()
    {
        // Euler angles - prone to gimbal lock
        eulerObject.rotation = Quaternion.Euler(eulerAngles);
        
        // Quaternion approach - no gimbal lock
        Quaternion xRot = Quaternion.AngleAxis(eulerAngles.x, Vector3.right);
        Quaternion yRot = Quaternion.AngleAxis(eulerAngles.y, Vector3.up);
        Quaternion zRot = Quaternion.AngleAxis(eulerAngles.z, Vector3.forward);
        
        quaternionObject.rotation = yRot * xRot * zRot;
        
        // Visualize the difference
        Debug.DrawRay(eulerObject.position, eulerObject.forward * 2f, Color.red);
        Debug.DrawRay(quaternionObject.position, quaternionObject.forward * 2f, Color.green);
    }
}
```

### Interpolation and Animation
```csharp
public class RotationInterpolation : MonoBehaviour
{
    [Header("Interpolation Types")]
    public Transform target;
    public float duration = 2f;
    
    [Header("Animation Curves")]
    public AnimationCurve rotationCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);
    
    private Quaternion startRotation;
    private Quaternion endRotation;
    private float elapsedTime;
    
    void Start()
    {
        startRotation = transform.rotation;
        endRotation = Quaternion.LookRotation(target.position - transform.position);
    }
    
    void Update()
    {
        if (elapsedTime < duration)
        {
            elapsedTime += Time.deltaTime;
            float t = elapsedTime / duration;
            
            // Apply animation curve
            float curveValue = rotationCurve.Evaluate(t);
            
            // Different interpolation methods
            switch (GetInterpolationType())
            {
                case InterpolationType.Lerp:
                    transform.rotation = Quaternion.Lerp(startRotation, endRotation, curveValue);
                    break;
                    
                case InterpolationType.Slerp:
                    transform.rotation = Quaternion.Slerp(startRotation, endRotation, curveValue);
                    break;
                    
                case InterpolationType.SlerpUnclamped:
                    transform.rotation = Quaternion.SlerpUnclamped(startRotation, endRotation, curveValue);
                    break;
            }
        }
    }
    
    enum InterpolationType { Lerp, Slerp, SlerpUnclamped }
    
    InterpolationType GetInterpolationType()
    {
        if (Input.GetKey(KeyCode.Alpha1)) return InterpolationType.Lerp;
        if (Input.GetKey(KeyCode.Alpha2)) return InterpolationType.Slerp;
        return InterpolationType.SlerpUnclamped;
    }
}
```

## 🎯 Practical Applications

### Turret Tracking System
```csharp
public class TurretController : MonoBehaviour
{
    [Header("Turret Components")]
    public Transform turretBase;
    public Transform turretBarrel;
    public Transform target;
    
    [Header("Rotation Limits")]
    public float horizontalSpeed = 90f;
    public float verticalSpeed = 45f;
    public float maxVerticalAngle = 30f;
    public float minVerticalAngle = -10f;
    
    void Update()
    {
        if (target == null) return;
        
        TrackTarget();
    }
    
    void TrackTarget()
    {
        Vector3 targetDirection = target.position - turretBase.position;
        
        // Horizontal rotation (base)
        Vector3 horizontalDirection = Vector3.ProjectOnPlane(targetDirection, Vector3.up);
        Quaternion horizontalTarget = Quaternion.LookRotation(horizontalDirection);
        
        turretBase.rotation = Quaternion.RotateTowards(
            turretBase.rotation,
            horizontalTarget,
            horizontalSpeed * Time.deltaTime
        );
        
        // Vertical rotation (barrel)
        float verticalAngle = Mathf.Atan2(targetDirection.y, horizontalDirection.magnitude) * Mathf.Rad2Deg;
        verticalAngle = Mathf.Clamp(verticalAngle, minVerticalAngle, maxVerticalAngle);
        
        Quaternion verticalTarget = Quaternion.Euler(verticalAngle, 0, 0);
        turretBarrel.localRotation = Quaternion.RotateTowards(
            turretBarrel.localRotation,
            verticalTarget,
            verticalSpeed * Time.deltaTime
        );
    }
}
```

### Spacecraft Controller
```csharp
public class SpacecraftController : MonoBehaviour
{
    [Header("Flight Controls")]
    public float pitchSpeed = 90f;
    public float yawSpeed = 90f;
    public float rollSpeed = 90f;
    public float thrustPower = 10f;
    
    [Header("Stabilization")]
    public bool autoStabilize = true;
    public float stabilizationForce = 2f;
    
    private Rigidbody rb;
    private Vector3 torqueInput;
    
    void Start()
    {
        rb = GetComponent<Rigidbody>();
    }
    
    void Update()
    {
        GetFlightInput();
        ApplyStabilization();
    }
    
    void FixedUpdate()
    {
        ApplyRotationalForces();
        ApplyThrust();
    }
    
    void GetFlightInput()
    {
        float pitch = Input.GetAxis("Vertical") * pitchSpeed;
        float yaw = Input.GetAxis("Horizontal") * yawSpeed;
        float roll = 0f;
        
        if (Input.GetKey(KeyCode.Q)) roll = -rollSpeed;
        if (Input.GetKey(KeyCode.E)) roll = rollSpeed;
        
        torqueInput = new Vector3(pitch, yaw, roll);
    }
    
    void ApplyRotationalForces()
    {
        rb.AddRelativeTorque(torqueInput * Time.fixedDeltaTime);
    }
    
    void ApplyThrust()
    {
        if (Input.GetKey(KeyCode.Space))
        {
            rb.AddRelativeForce(Vector3.forward * thrustPower * Time.fixedDeltaTime);
        }
    }
    
    void ApplyStabilization()
    {
        if (autoStabilize && torqueInput.magnitude < 0.1f)
        {
            // Gradually reduce angular velocity
            rb.angularVelocity = Vector3.Lerp(
                rb.angularVelocity,
                Vector3.zero,
                stabilizationForce * Time.deltaTime
            );
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Rotation System Prompts
```
Generate a Unity quaternion-based rotation system for [specific use case]:
- Input: [movement type, constraints, smoothness requirements]
- Output: Complete C# script with proper quaternion mathematics
- Include: Gimbal lock prevention, smooth interpolation, input handling

Create advanced camera controller using quaternions:
- Features: [orbit, first-person, third-person, cinematic]
- Constraints: [collision detection, smooth follow, look limits]
- Polish: [easing curves, shake effects, zoom controls]

Design spacecraft/vehicle rotation physics:
- Type: [airplane, spaceship, submarine, drone]
- Physics: [realistic torque, drag simulation, autopilot]
- Controls: [6DOF movement, stability systems, momentum]
```

### Mathematical Understanding
```
Explain quaternion mathematics for Unity developers:
- Focus: Practical application over pure theory
- Include: Code examples, common pitfalls, debugging tips
- Compare: Euler angles vs quaternions in game scenarios

Generate rotation debugging utilities:
- Visualize: Quaternion values, rotation paths, gimbal lock
- Tools: Gizmos, inspector tools, runtime displays
- Help: Common rotation problems and solutions
```

## 💡 Key Highlights

### Essential Quaternion Knowledge
- **Always use Quaternion.Slerp() for smooth rotations**
- **Quaternion multiplication order matters: A * B ≠ B * A**
- **Identity quaternion (0,0,0,1) represents no rotation**
- **Quaternions prevent gimbal lock inherent in Euler angles**
- **Use Quaternion.LookRotation() for object-to-target orientation**

### Unity Best Practices
- **Prefer quaternions over Euler angles for runtime calculations**
- **Use transform.Rotate() for simple local rotations**
- **RotateTowards() for clamped rotation speeds**
- **Always normalize quaternions after mathematical operations**
- **Cache rotation calculations to avoid per-frame overhead**

### Performance Optimization
- **Quaternion operations are more expensive than Vector3**
- **Cache frequently used rotations (identity, 90-degree turns)**
- **Use Quaternion.Angle() to check rotation differences**
- **Avoid converting between Euler and quaternions repeatedly**
- **Consider using rotation matrices for complex transformations**

### Common Rotation Patterns
- **Camera orbit: Spherical coordinates + quaternion conversion**
- **Character turning: LookRotation + Slerp interpolation**
- **Turret tracking: Separate horizontal/vertical rotation constraints**
- **Vehicle physics: AddRelativeTorque() for realistic rotation**
- **Animation blending: Multiple quaternion interpolations**