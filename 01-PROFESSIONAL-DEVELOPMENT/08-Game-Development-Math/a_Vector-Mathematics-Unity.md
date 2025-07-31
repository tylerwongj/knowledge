# Vector Mathematics in Unity

## Overview
Master essential vector mathematics concepts for game development, including 2D/3D vector operations, transformations, and practical Unity implementations.

## Key Concepts

### Vector Fundamentals

**Vector Representation:**
- **2D Vectors:** (x, y) coordinates representing position, direction, or magnitude
- **3D Vectors:** (x, y, z) coordinates for 3D space calculations
- **Unity Vector Types:** Vector2, Vector3, Vector4 for different dimensional needs
- **Magnitude:** Length of a vector calculated using Pythagorean theorem

**Basic Vector Operations:**
```csharp
public class VectorMathExamples : MonoBehaviour
{
    [Header("Vector Demonstration")]
    [SerializeField] private Transform pointA;
    [SerializeField] private Transform pointB;
    [SerializeField] private float moveSpeed = 5f;
    
    void Start()
    {
        DemonstrateVectorOperations();
    }
    
    void DemonstrateVectorOperations()
    {
        Vector3 positionA = pointA.position;
        Vector3 positionB = pointB.position;
        
        // Vector Addition: Combining movements or forces
        Vector3 combinedMovement = Vector3.right * 2f + Vector3.forward * 3f;
        Debug.Log($"Combined Movement: {combinedMovement}");
        
        // Vector Subtraction: Finding direction between points
        Vector3 directionAToB = positionB - positionA;
        Debug.Log($"Direction A to B: {directionAToB}");
        
        // Vector Magnitude: Distance calculation
        float distance = directionAToB.magnitude;
        Debug.Log($"Distance between A and B: {distance}");
        
        // Vector Normalization: Unit direction vector
        Vector3 normalizedDirection = directionAToB.normalized;
        Debug.Log($"Normalized Direction: {normalizedDirection}");
        
        // Scalar Multiplication: Scaling vectors
        Vector3 scaledVector = normalizedDirection * moveSpeed;
        Debug.Log($"Scaled Movement Vector: {scaledVector}");
    }
    
    // Practical example: Move towards target
    void Update()
    {
        if (pointB != null)
        {
            Vector3 direction = (pointB.position - transform.position).normalized;
            transform.position += direction * moveSpeed * Time.deltaTime;
        }
    }
}
```

### Dot Product Applications

**Dot Product Fundamentals:**
- **Mathematical Definition:** a·b = |a||b|cos(θ)
- **Unity Implementation:** Vector3.Dot(vectorA, vectorB)
- **Results:** Positive (acute angle), Zero (perpendicular), Negative (obtuse angle)
- **Common Uses:** Angle calculation, forward/backward detection, projection

**Practical Dot Product Usage:**
```csharp
public class DotProductApplications : MonoBehaviour
{
    [Header("Dot Product Examples")]
    [SerializeField] private Transform player;
    [SerializeField] private Transform enemy;
    [SerializeField] private float detectionAngle = 60f;
    [SerializeField] private float detectionRange = 10f;
    
    void Update()
    {
        if (player != null && enemy != null)
        {
            CheckPlayerVisibility();
            CalculateMovementAlignment();
            ProjectVectorOntoSurface();
        }
    }
    
    // Enemy AI: Check if player is within field of view
    void CheckPlayerVisibility()
    {
        Vector3 toPlayer = (player.position - transform.position).normalized;
        Vector3 forward = transform.forward;
        
        // Dot product to determine if player is in front
        float dot = Vector3.Dot(forward, toPlayer);
        
        // Convert detection angle to dot product threshold
        float threshold = Mathf.Cos(detectionAngle * 0.5f * Mathf.Deg2Rad);
        
        if (dot > threshold)
        {
            float distance = Vector3.Distance(transform.position, player.position);
            if (distance <= detectionRange)
            {
                Debug.Log("Player detected in field of view!");
                OnPlayerDetected();
            }
        }
    }
    
    // Movement Analysis: Check if moving towards or away from target
    void CalculateMovementAlignment()
    {
        Vector3 velocity = GetComponent<Rigidbody>().velocity;
        Vector3 toTarget = (enemy.position - transform.position).normalized;
        
        float alignment = Vector3.Dot(velocity.normalized, toTarget);
        
        if (alignment > 0.8f)
        {
            Debug.Log("Moving directly towards target");
        }
        else if (alignment < -0.8f)
        {
            Debug.Log("Moving away from target");
        }
        else
        {
            Debug.Log("Moving perpendicular to target");
        }
    }
    
    // Vector Projection: Project movement onto surface
    void ProjectVectorOntoSurface()
    {
        Vector3 movement = Vector3.forward * 5f;
        Vector3 surfaceNormal = Vector3.up; // Flat ground
        
        // Project movement vector onto surface (remove vertical component)
        Vector3 projectedMovement = movement - Vector3.Dot(movement, surfaceNormal) * surfaceNormal;
        
        Debug.DrawRay(transform.position, movement, Color.red);
        Debug.DrawRay(transform.position, projectedMovement, Color.green);
    }
    
    private void OnPlayerDetected()
    {
        // AI behavior when player is detected
        Debug.Log("Alert! Player spotted!");
    }
}
```

### Cross Product and Rotations

**Cross Product Applications:**
```csharp
public class CrossProductExamples : MonoBehaviour
{
    [Header("Cross Product Demonstrations")]
    [SerializeField] private Transform objectA;
    [SerializeField] private Transform objectB;
    [SerializeField] private float rotationSpeed = 90f;
    
    void Update()
    {
        DemonstrateCrossProduct();
        CalculatePerpendicularVector();
        DetermineRotationDirection();
    }
    
    // Find perpendicular vector for rotation axis
    void DemonstrateCrossProduct()
    {
        Vector3 vectorA = objectA.forward;
        Vector3 vectorB = objectB.forward;
        
        // Cross product gives perpendicular vector
        Vector3 perpendicular = Vector3.Cross(vectorA, vectorB);
        
        // Visualize the vectors
        Debug.DrawRay(transform.position, vectorA * 3f, Color.red);
        Debug.DrawRay(transform.position, vectorB * 3f, Color.blue);
        Debug.DrawRay(transform.position, perpendicular * 2f, Color.green);
        
        // Use perpendicular vector as rotation axis
        if (perpendicular.magnitude > 0.01f)
        {
            transform.Rotate(perpendicular.normalized, rotationSpeed * Time.deltaTime);
        }
    }
    
    // Calculate surface normal from three points
    Vector3 CalculateSurfaceNormal(Vector3 p1, Vector3 p2, Vector3 p3)
    {
        Vector3 edge1 = p2 - p1;
        Vector3 edge2 = p3 - p1;
        
        // Cross product gives surface normal
        Vector3 normal = Vector3.Cross(edge1, edge2).normalized;
        return normal;
    }
    
    // Determine which direction to rotate (clockwise vs counterclockwise)
    void DetermineRotationDirection()
    {
        Vector3 fromVector = transform.forward;
        Vector3 toVector = (objectA.position - transform.position).normalized;
        
        // Cross product to determine rotation direction
        Vector3 cross = Vector3.Cross(fromVector, toVector);
        
        // Use y-component to determine direction (in XZ plane)
        float rotationDirection = Mathf.Sign(cross.y);
        
        if (rotationDirection > 0)
        {
            Debug.Log("Rotate counterclockwise");
        }
        else if (rotationDirection < 0)
        {
            Debug.Log("Rotate clockwise");
        }
    }
    
    // 2D Cross Product for determining side
    float Cross2D(Vector2 a, Vector2 b)
    {
        return a.x * b.y - a.y * b.x;
    }
    
    // Check which side of a line a point is on
    bool IsPointOnLeftSide(Vector2 lineStart, Vector2 lineEnd, Vector2 point)
    {
        Vector2 lineVector = lineEnd - lineStart;
        Vector2 pointVector = point - lineStart;
        
        return Cross2D(lineVector, pointVector) > 0;
    }
}
```

### Distance and Interpolation

**Distance Calculations and Movement:**
```csharp
public class DistanceAndInterpolation : MonoBehaviour
{
    [Header("Distance and Movement")]
    [SerializeField] private Transform target;
    [SerializeField] private float followDistance = 5f;
    [SerializeField] private float smoothTime = 0.3f;
    [SerializeField] private float arrivalThreshold = 0.1f;
    
    private Vector3 velocity = Vector3.zero;
    
    void Update()
    {
        if (target != null)
        {
            PerformDistanceBasedMovement();
            DemonstrateInterpolationMethods();
        }
    }
    
    void PerformDistanceBasedMovement()
    {
        float distanceToTarget = Vector3.Distance(transform.position, target.position);
        
        // Different behaviors based on distance
        if (distanceToTarget > followDistance + 1f)
        {
            // Too far - move closer
            Vector3 direction = (target.position - transform.position).normalized;
            transform.position += direction * 3f * Time.deltaTime;
        }
        else if (distanceToTarget < followDistance - 1f)
        {
            // Too close - move away
            Vector3 direction = (transform.position - target.position).normalized;
            transform.position += direction * 2f * Time.deltaTime;
        }
        
        // Smooth rotation towards target
        Vector3 lookDirection = (target.position - transform.position).normalized;
        if (lookDirection != Vector3.zero)
        {
            Quaternion targetRotation = Quaternion.LookRotation(lookDirection);
            transform.rotation = Quaternion.Slerp(transform.rotation, targetRotation, 2f * Time.deltaTime);
        }
    }
    
    void DemonstrateInterpolationMethods()
    {
        Vector3 targetPosition = target.position;
        
        // Linear interpolation (Lerp) - constant rate
        Vector3 lerpPosition = Vector3.Lerp(transform.position, targetPosition, 2f * Time.deltaTime);
        
        // Smooth damp - slows down as it approaches target
        Vector3 smoothPosition = Vector3.SmoothDamp(transform.position, targetPosition, ref velocity, smoothTime);
        
        // Move towards - constant speed regardless of distance
        Vector3 moveTowardPosition = Vector3.MoveTowards(transform.position, targetPosition, 5f * Time.deltaTime);
        
        // Choose interpolation method based on desired behavior
        transform.position = smoothPosition; // Using smooth damp for natural movement
    }
    
    // Advanced: Bezier curve interpolation for smooth paths
    public Vector3 BezierCurve(Vector3 start, Vector3 control, Vector3 end, float t)
    {
        float oneMinusT = 1f - t;
        return oneMinusT * oneMinusT * start + 
               2f * oneMinusT * t * control + 
               t * t * end;
    }
    
    // Calculate closest point on line segment
    public Vector3 ClosestPointOnLine(Vector3 lineStart, Vector3 lineEnd, Vector3 point)
    {
        Vector3 lineDirection = lineEnd - lineStart;
        float lineLength = lineDirection.magnitude;
        lineDirection.Normalize();
        
        Vector3 toPoint = point - lineStart;
        float projectionLength = Vector3.Dot(toPoint, lineDirection);
        
        // Clamp to line segment
        projectionLength = Mathf.Clamp(projectionLength, 0f, lineLength);
        
        return lineStart + lineDirection * projectionLength;
    }
}
```

## Practical Applications

### Character Movement Systems

**Advanced Movement Controller:**
```csharp
public class VectorBasedMovement : MonoBehaviour
{
    [Header("Movement Settings")]
    [SerializeField] private float walkSpeed = 3f;
    [SerializeField] private float runSpeed = 6f;
    [SerializeField] private float acceleration = 10f;
    [SerializeField] private float friction = 15f;
    [SerializeField] private float airControl = 2f;
    
    [Header("Jump Settings")]
    [SerializeField] private float jumpForce = 8f;
    [SerializeField] private float gravity = 20f;
    [SerializeField] private LayerMask groundLayer;
    
    private Vector3 velocity;
    private bool isGrounded;
    private Rigidbody rb;
    
    void Start()
    {
        rb = GetComponent<Rigidbody>();
        rb.useGravity = false; // Handle gravity manually for more control
    }
    
    void Update()
    {
        HandleInput();
        ApplyMovement();
        CheckGrounded();
    }
    
    void HandleInput()
    {
        Vector2 input = new Vector2(Input.GetAxis("Horizontal"), Input.GetAxis("Vertical"));
        bool isRunning = Input.GetKey(KeyCode.LeftShift);
        
        // Convert input to world space movement
        Vector3 moveDirection = transform.right * input.x + transform.forward * input.y;
        moveDirection.Normalize();
        
        float targetSpeed = isRunning ? runSpeed : walkSpeed;
        Vector3 targetVelocity = moveDirection * targetSpeed;
        
        // Ground movement with acceleration and friction
        if (isGrounded)
        {
            if (moveDirection.magnitude > 0.1f)
            {
                // Accelerate towards target velocity
                velocity = Vector3.MoveTowards(velocity, targetVelocity, acceleration * Time.deltaTime);
            }
            else
            {
                // Apply friction when no input
                velocity = Vector3.MoveTowards(velocity, Vector3.zero, friction * Time.deltaTime);
            }
        }
        else
        {
            // Air control - limited movement in air
            Vector3 airVelocity = new Vector3(velocity.x, 0, velocity.z);
            airVelocity = Vector3.MoveTowards(airVelocity, targetVelocity, airControl * Time.deltaTime);
            velocity.x = airVelocity.x;
            velocity.z = airVelocity.z;
        }
        
        // Jump input
        if (Input.GetKeyDown(KeyCode.Space) && isGrounded)
        {
            velocity.y = jumpForce;
        }
    }
    
    void ApplyMovement()
    {
        // Apply gravity
        if (!isGrounded)
        {
            velocity.y -= gravity * Time.deltaTime;
        }
        
        // Apply velocity to rigidbody
        rb.velocity = velocity;
    }
    
    void CheckGrounded()
    {
        float checkDistance = 0.1f;
        Vector3 spherePosition = transform.position + Vector3.down * checkDistance;
        isGrounded = Physics.CheckSphere(spherePosition, 0.1f, groundLayer);
        
        // Reset vertical velocity if grounded
        if (isGrounded && velocity.y < 0)
        {
            velocity.y = 0;
        }
    }
}
```

### AI Navigation and Pathfinding

**Vector-Based AI Movement:**
```csharp
public class AIVectorMovement : MonoBehaviour
{
    [Header("AI Settings")]
    [SerializeField] private Transform target;
    [SerializeField] private float moveSpeed = 3f;
    [SerializeField] private float rotationSpeed = 180f;
    [SerializeField] private float stoppingDistance = 2f;
    [SerializeField] private float avoidanceRadius = 1.5f;
    
    [Header("Pathfinding")]
    [SerializeField] private LayerMask obstacleLayer;
    [SerializeField] private float raycastDistance = 3f;
    
    private Vector3 currentVelocity;
    
    void Update()
    {
        if (target != null)
        {
            Vector3 desiredVelocity = CalculateDesiredVelocity();
            Vector3 avoidanceForce = CalculateAvoidanceForce();
            
            // Combine forces
            Vector3 finalVelocity = desiredVelocity + avoidanceForce;
            
            // Apply movement
            ApplyMovement(finalVelocity);
        }
    }
    
    Vector3 CalculateDesiredVelocity()
    {
        Vector3 toTarget = target.position - transform.position;
        float distance = toTarget.magnitude;
        
        if (distance > stoppingDistance)
        {
            // Move towards target
            Vector3 desired = toTarget.normalized * moveSpeed;
            return desired;
        }
        else
        {
            // Slow down when close to target
            float slowFactor = distance / stoppingDistance;
            Vector3 desired = toTarget.normalized * moveSpeed * slowFactor;
            return desired;
        }
    }
    
    Vector3 CalculateAvoidanceForce()
    {
        Vector3 avoidanceForce = Vector3.zero;
        
        // Raycast in multiple directions to detect obstacles
        Vector3[] directions = {
            transform.forward,
            transform.forward + transform.right * 0.5f,
            transform.forward - transform.right * 0.5f
        };
        
        foreach (Vector3 direction in directions)
        {
            if (Physics.Raycast(transform.position, direction, out RaycastHit hit, raycastDistance, obstacleLayer))
            {
                // Calculate avoidance force
                Vector3 avoidDirection = (transform.position - hit.point).normalized;
                float avoidStrength = 1f - (hit.distance / raycastDistance);
                avoidanceForce += avoidDirection * avoidStrength * moveSpeed;
                
                Debug.DrawRay(transform.position, direction * hit.distance, Color.red);
            }
            else
            {
                Debug.DrawRay(transform.position, direction * raycastDistance, Color.green);
            }
        }
        
        return avoidanceForce;
    }
    
    void ApplyMovement(Vector3 velocity)
    {
        if (velocity.magnitude > 0.1f)
        {
            // Move
            transform.position += velocity * Time.deltaTime;
            
            // Rotate towards movement direction
            Quaternion targetRotation = Quaternion.LookRotation(velocity.normalized);
            transform.rotation = Quaternion.RotateTowards(transform.rotation, targetRotation, rotationSpeed * Time.deltaTime);
        }
    }
    
    // Flocking behavior for group AI
    public Vector3 CalculateFlockingForce(AIVectorMovement[] neighbors)
    {
        Vector3 separation = Vector3.zero;
        Vector3 alignment = Vector3.zero;
        Vector3 cohesion = Vector3.zero;
        int count = 0;
        
        foreach (AIVectorMovement neighbor in neighbors)
        {
            if (neighbor != this)
            {
                float distance = Vector3.Distance(transform.position, neighbor.transform.position);
                
                if (distance < avoidanceRadius)
                {
                    // Separation - avoid crowding
                    Vector3 diff = (transform.position - neighbor.transform.position).normalized;
                    separation += diff / distance; // Weight by distance
                    
                    // Alignment - steer towards average heading
                    alignment += neighbor.currentVelocity;
                    
                    // Cohesion - steer towards center of neighbors
                    cohesion += neighbor.transform.position;
                    
                    count++;
                }
            }
        }
        
        if (count > 0)
        {
            // Average the forces
            separation = separation.normalized * moveSpeed;
            alignment = (alignment / count).normalized * moveSpeed;
            cohesion = ((cohesion / count) - transform.position).normalized * moveSpeed;
            
            // Weight the different behaviors
            return separation * 2f + alignment * 1f + cohesion * 1f;
        }
        
        return Vector3.zero;
    }
}
```

## Interview Preparation

### Vector Mathematics Questions

**Common Technical Questions:**
- "Explain the difference between dot product and cross product"
- "How would you implement smooth camera following using vectors?"
- "Calculate the angle between two vectors without using Unity's built-in functions"
- "How do you determine if a point is inside a triangle using vector math?"

**Practical Implementation Questions:**
```csharp
// Example interview question: "Implement enemy field of view detection"
public bool IsTargetInFieldOfView(Transform enemy, Transform target, float fovAngle, float maxRange)
{
    Vector3 toTarget = target.position - enemy.position;
    float distance = toTarget.magnitude;
    
    // Check distance
    if (distance > maxRange) return false;
    
    // Check angle using dot product
    Vector3 forward = enemy.forward;
    Vector3 directionToTarget = toTarget.normalized;
    
    float dot = Vector3.Dot(forward, directionToTarget);
    float threshold = Mathf.Cos(fovAngle * 0.5f * Mathf.Deg2Rad);
    
    return dot > threshold;
}

// "How would you smooth movement between waypoints?"
public class WaypointMovement : MonoBehaviour
{
    public Transform[] waypoints;
    public float moveSpeed = 5f;
    
    private int currentWaypoint = 0;
    
    void Update()
    {
        if (waypoints.Length == 0) return;
        
        Vector3 targetPosition = waypoints[currentWaypoint].position;
        Vector3 direction = (targetPosition - transform.position).normalized;
        
        transform.position += direction * moveSpeed * Time.deltaTime;
        
        if (Vector3.Distance(transform.position, targetPosition) < 0.1f)
        {
            currentWaypoint = (currentWaypoint + 1) % waypoints.Length;
        }
    }
}
```

### Key Takeaways

**Essential Vector Concepts:**
- Master dot product for angle calculations and projections
- Use cross product for perpendicular vectors and rotations
- Understand vector normalization for direction calculations
- Apply interpolation methods for smooth movement and animations

**Practical Unity Applications:**
- Implement character movement with proper physics
- Create AI behaviors using vector-based calculations
- Build camera systems with smooth following and rotation
- Design gameplay mechanics using distance and angle calculations