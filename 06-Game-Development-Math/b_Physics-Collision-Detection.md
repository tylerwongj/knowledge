# Physics & Collision Detection

## Overview
Master physics simulations, collision detection algorithms, and Unity's physics system for realistic game interactions and performance optimization.

## Key Concepts

### Unity Physics Fundamentals

**Rigidbody Components:**
- **Mass:** Affects inertia and collision response
- **Drag:** Air resistance for linear movement
- **Angular Drag:** Resistance to rotational movement
- **Use Gravity:** Whether object is affected by global gravity
- **Is Kinematic:** Physics-driven vs script-controlled movement

**Physics Materials:**
```csharp
public class PhysicsMaterialController : MonoBehaviour
{
    [Header("Physics Material Settings")]
    [SerializeField] private PhysicMaterial bouncyMaterial;
    [SerializeField] private PhysicMaterial slipperyMaterial;
    [SerializeField] private PhysicMaterial roughMaterial;
    
    private Collider objectCollider;
    private Rigidbody rb;
    
    void Start()
    {
        objectCollider = GetComponent<Collider>();
        rb = GetComponent<Rigidbody>();
        
        CreatePhysicsMaterials();
    }
    
    void CreatePhysicsMaterials()
    {
        // Bouncy material (ball, trampoline)
        bouncyMaterial = new PhysicMaterial("Bouncy");
        bouncyMaterial.bounciness = 0.9f;
        bouncyMaterial.dynamicFriction = 0.1f;
        bouncyMaterial.staticFriction = 0.1f;
        bouncyMaterial.frictionCombine = PhysicMaterialCombine.Minimum;
        bouncyMaterial.bounceCombine = PhysicMaterialCombine.Maximum;
        
        // Slippery material (ice, oil)
        slipperyMaterial = new PhysicMaterial("Slippery");
        slipperyMaterial.bounciness = 0.1f;
        slipperyMaterial.dynamicFriction = 0.05f;
        slipperyMaterial.staticFriction = 0.05f;
        slipperyMaterial.frictionCombine = PhysicMaterialCombine.Minimum;
        
        // Rough material (concrete, sandpaper)
        roughMaterial = new PhysicMaterial("Rough");
        roughMaterial.bounciness = 0.0f;
        roughMaterial.dynamicFriction = 0.8f;
        roughMaterial.staticFriction = 1.0f;
        roughMaterial.frictionCombine = PhysicMaterialCombine.Maximum;
    }
    
    public void SetMaterial(string materialType)
    {
        switch (materialType.ToLower())
        {
            case "bouncy":
                objectCollider.material = bouncyMaterial;
                break;
            case "slippery":
                objectCollider.material = slipperyMaterial;
                break;
            case "rough":
                objectCollider.material = roughMaterial;
                break;
        }
    }
    
    // Dynamic physics property adjustment
    public void AdjustPhysicsProperties(float mass, float drag, float angularDrag)
    {
        if (rb != null)
        {
            rb.mass = mass;
            rb.drag = drag;
            rb.angularDrag = angularDrag;
        }
    }
}
```

### Collision Detection Systems

**Collision Event Handling:**
```csharp
public class CollisionDetectionSystem : MonoBehaviour
{
    [Header("Collision Settings")]
    [SerializeField] private LayerMask detectableLayers = -1;
    [SerializeField] private float collisionForceThreshold = 5f;
    [SerializeField] private bool enableCollisionEffects = true;
    
    [Header("Audio and Effects")]
    [SerializeField] private AudioClip[] collisionSounds;
    [SerializeField] private ParticleSystem collisionParticles;
    [SerializeField] private float effectCooldown = 0.1f;
    
    private AudioSource audioSource;
    private float lastEffectTime;
    private Rigidbody rb;
    
    void Start()
    {
        audioSource = GetComponent<AudioSource>();
        rb = GetComponent<Rigidbody>();
    }
    
    void OnCollisionEnter(Collision collision)
    {
        // Check if collision should be processed
        if (!ShouldProcessCollision(collision)) return;
        
        // Calculate collision data
        CollisionData data = AnalyzeCollision(collision);
        
        // Handle collision response
        HandleCollisionResponse(data);
        
        // Trigger effects
        if (enableCollisionEffects && Time.time - lastEffectTime > effectCooldown)
        {
            TriggerCollisionEffects(data);
            lastEffectTime = Time.time;
        }
        
        Debug.Log($"Collision with {collision.gameObject.name}: Force = {data.force}, Angle = {data.angle}");
    }
    
    void OnCollisionStay(Collision collision)
    {
        // Handle continuous collision (friction, sliding sounds)
        if (rb.velocity.magnitude > 0.5f)
        {
            ApplySlidingEffects(collision);
        }
    }
    
    void OnCollisionExit(Collision collision)
    {
        // Cleanup when objects separate
        StopSlidingEffects();
    }
    
    bool ShouldProcessCollision(Collision collision)
    {
        // Layer mask check
        int objectLayer = 1 << collision.gameObject.layer;
        if ((detectableLayers & objectLayer) == 0) return false;
        
        // Force threshold check
        float collisionForce = collision.relativeVelocity.magnitude;
        return collisionForce >= collisionForceThreshold;
    }
    
    CollisionData AnalyzeCollision(Collision collision)
    {
        ContactPoint contact = collision.contacts[0];
        
        return new CollisionData
        {
            point = contact.point,
            normal = contact.normal,
            force = collision.relativeVelocity.magnitude,
            angle = Vector3.Angle(collision.relativeVelocity, contact.normal),
            otherObject = collision.gameObject,
            material = contact.otherCollider.material
        };
    }
    
    void HandleCollisionResponse(CollisionData data)
    {
        // Damage system
        IDamageable damageable = data.otherObject.GetComponent<IDamageable>();
        if (damageable != null)
        {
            float damage = CalculateDamage(data.force, data.angle);
            damageable.TakeDamage(damage);
        }
        
        // Breakable objects
        IBreakable breakable = GetComponent<IBreakable>();
        if (breakable != null && data.force > breakable.BreakThreshold)
        {
            breakable.Break(data.point, data.force);
        }
    }
    
    void TriggerCollisionEffects(CollisionData data)
    {
        // Particle effects
        if (collisionParticles != null)
        {
            collisionParticles.transform.position = data.point;
            collisionParticles.transform.rotation = Quaternion.LookRotation(data.normal);
            collisionParticles.Play();
        }
        
        // Audio effects
        if (collisionSounds.Length > 0 && audioSource != null)
        {
            AudioClip soundToPlay = SelectCollisionSound(data);
            audioSource.pitch = Random.Range(0.8f, 1.2f);
            audioSource.volume = Mathf.Clamp01(data.force / 10f);
            audioSource.PlayOneShot(soundToPlay);
        }
    }
    
    AudioClip SelectCollisionSound(CollisionData data)
    {
        // Select sound based on material or force
        if (data.material != null)
        {
            // Different sounds for different materials
            string materialName = data.material.name.ToLower();
            if (materialName.Contains("metal")) return collisionSounds[0];
            if (materialName.Contains("wood")) return collisionSounds[1];
            if (materialName.Contains("stone")) return collisionSounds[2];
        }
        
        // Default random sound
        return collisionSounds[Random.Range(0, collisionSounds.Length)];
    }
    
    float CalculateDamage(float force, float angle)
    {
        // More damage for direct hits (low angle)
        float angleFactor = 1f - (angle / 180f);
        return force * angleFactor * 0.1f;
    }
    
    void ApplySlidingEffects(Collision collision)
    {
        // Continuous sliding particle effects and sounds
    }
    
    void StopSlidingEffects()
    {
        // Stop continuous effects
    }
}

[System.Serializable]
public struct CollisionData
{
    public Vector3 point;
    public Vector3 normal;
    public float force;
    public float angle;
    public GameObject otherObject;
    public PhysicMaterial material;
}

public interface IDamageable
{
    void TakeDamage(float damage);
}

public interface IBreakable
{
    float BreakThreshold { get; }
    void Break(Vector3 impactPoint, float force);
}
```

### Advanced Collision Detection

**Custom Collision Algorithms:**
```csharp
public class CustomCollisionDetection : MonoBehaviour
{
    [Header("Custom Collision Settings")]
    [SerializeField] private bool useCustomDetection = false;
    [SerializeField] private float detectionRadius = 1f;
    [SerializeField] private LayerMask collisionLayers = -1;
    
    // Sphere vs Sphere collision detection
    public static bool SphereSphereCollision(Vector3 center1, float radius1, Vector3 center2, float radius2)
    {
        float distance = Vector3.Distance(center1, center2);
        return distance <= (radius1 + radius2);
    }
    
    // Sphere vs Sphere collision with detailed info
    public static CollisionInfo SphereSphereCollisionInfo(Transform sphere1, float radius1, Transform sphere2, float radius2)
    {
        Vector3 center1 = sphere1.position;
        Vector3 center2 = sphere2.position;
        
        Vector3 direction = center2 - center1;
        float distance = direction.magnitude;
        float combinedRadius = radius1 + radius2;
        
        CollisionInfo info = new CollisionInfo();
        info.isColliding = distance <= combinedRadius;
        
        if (info.isColliding)
        {
            info.penetrationDepth = combinedRadius - distance;
            info.normal = direction.normalized;
            info.contactPoint = center1 + info.normal * radius1;
        }
        
        return info;
    }
    
    // Axis-Aligned Bounding Box (AABB) collision
    public static bool AABBCollision(Bounds bounds1, Bounds bounds2)
    {
        return bounds1.min.x <= bounds2.max.x && bounds1.max.x >= bounds2.min.x &&
               bounds1.min.y <= bounds2.max.y && bounds1.max.y >= bounds2.min.y &&
               bounds1.min.z <= bounds2.max.z && bounds1.max.z >= bounds2.min.z;
    }
    
    // Point in triangle test (2D)
    public static bool PointInTriangle(Vector2 point, Vector2 a, Vector2 b, Vector2 c)
    {
        float sign1 = Sign(point, a, b);
        float sign2 = Sign(point, b, c);
        float sign3 = Sign(point, c, a);
        
        bool hasNeg = (sign1 < 0f) || (sign2 < 0f) || (sign3 < 0f);
        bool hasPos = (sign1 > 0f) || (sign2 > 0f) || (sign3 > 0f);
        
        return !(hasNeg && hasPos);
    }
    
    private static float Sign(Vector2 p1, Vector2 p2, Vector2 p3)
    {
        return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y);
    }
    
    // Ray vs Sphere intersection
    public static bool RaySphereIntersection(Ray ray, Vector3 sphereCenter, float sphereRadius, out float distance)
    {
        Vector3 oc = ray.origin - sphereCenter;
        float a = Vector3.Dot(ray.direction, ray.direction);
        float b = 2.0f * Vector3.Dot(oc, ray.direction);
        float c = Vector3.Dot(oc, oc) - sphereRadius * sphereRadius;
        
        float discriminant = b * b - 4 * a * c;
        
        if (discriminant < 0)
        {
            distance = 0f;
            return false;
        }
        
        distance = (-b - Mathf.Sqrt(discriminant)) / (2.0f * a);
        return distance >= 0;
    }
    
    // Sweep and prune broad phase collision detection
    public class SweepAndPrune
    {
        private List<CollisionObject> objects = new List<CollisionObject>();
        private List<CollisionPair> potentialPairs = new List<CollisionPair>();
        
        public void AddObject(CollisionObject obj)
        {
            objects.Add(obj);
        }
        
        public List<CollisionPair> GetPotentialCollisions()
        {
            potentialPairs.Clear();
            
            // Sort by x-axis
            objects.Sort((a, b) => a.bounds.min.x.CompareTo(b.bounds.min.x));
            
            // Sweep and prune
            for (int i = 0; i < objects.Count; i++)
            {
                for (int j = i + 1; j < objects.Count; j++)
                {
                    if (objects[j].bounds.min.x > objects[i].bounds.max.x)
                        break; // No more overlaps possible
                    
                    // Check Y and Z overlap
                    if (objects[i].bounds.max.y >= objects[j].bounds.min.y &&
                        objects[i].bounds.min.y <= objects[j].bounds.max.y &&
                        objects[i].bounds.max.z >= objects[j].bounds.min.z &&
                        objects[i].bounds.min.z <= objects[j].bounds.max.z)
                    {
                        potentialPairs.Add(new CollisionPair(objects[i], objects[j]));
                    }
                }
            }
            
            return potentialPairs;
        }
    }
    
    void Update()
    {
        if (useCustomDetection)
        {
            PerformCustomCollisionDetection();
        }
    }
    
    void PerformCustomCollisionDetection()
    {
        Collider[] nearbyColliders = Physics.OverlapSphere(transform.position, detectionRadius, collisionLayers);
        
        foreach (Collider other in nearbyColliders)
        {
            if (other.gameObject == gameObject) continue;
            
            // Use custom collision detection based on collider types
            if (GetComponent<SphereCollider>() && other.GetComponent<SphereCollider>())
            {
                CheckSphereSphereCollision(other);
            }
            else if (GetComponent<BoxCollider>() && other.GetComponent<BoxCollider>())
            {
                CheckAABBCollision(other);
            }
        }
    }
    
    void CheckSphereSphereCollision(Collider other)
    {
        SphereCollider mySphere = GetComponent<SphereCollider>();
        SphereCollider otherSphere = other.GetComponent<SphereCollider>();
        
        CollisionInfo info = SphereSphereCollisionInfo(transform, mySphere.radius, other.transform, otherSphere.radius);
        
        if (info.isColliding)
        {
            OnCustomCollisionDetected(other.gameObject, info);
        }
    }
    
    void CheckAABBCollision(Collider other)
    {
        Bounds myBounds = GetComponent<Collider>().bounds;
        Bounds otherBounds = other.bounds;
        
        if (AABBCollision(myBounds, otherBounds))
        {
            CollisionInfo info = new CollisionInfo
            {
                isColliding = true,
                contactPoint = myBounds.center,
                normal = (otherBounds.center - myBounds.center).normalized
            };
            
            OnCustomCollisionDetected(other.gameObject, info);
        }
    }
    
    void OnCustomCollisionDetected(GameObject other, CollisionInfo info)
    {
        Debug.Log($"Custom collision detected with {other.name}");
        Debug.DrawRay(info.contactPoint, info.normal, Color.red, 1f);
    }
    
    void OnDrawGizmosSelected()
    {
        // Visualize detection radius
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(transform.position, detectionRadius);
    }
}

[System.Serializable]
public struct CollisionInfo
{
    public bool isColliding;
    public Vector3 contactPoint;
    public Vector3 normal;
    public float penetrationDepth;
}

[System.Serializable]
public class CollisionObject
{
    public GameObject gameObject;
    public Bounds bounds;
    public int id;
}

[System.Serializable]
public struct CollisionPair
{
    public CollisionObject objectA;
    public CollisionObject objectB;
    
    public CollisionPair(CollisionObject a, CollisionObject b)
    {
        objectA = a;
        objectB = b;
    }
}
```

### Physics Optimization

**Performance Optimization Techniques:**
```csharp
public class PhysicsOptimizer : MonoBehaviour
{
    [Header("Optimization Settings")]
    [SerializeField] private bool enableDistanceCulling = true;
    [SerializeField] private float cullingDistance = 50f;
    [SerializeField] private bool enableLevelOfDetail = true;
    [SerializeField] private float lodDistance = 20f;
    
    [Header("Sleep Settings")]
    [SerializeField] private float sleepVelocityThreshold = 0.1f;
    [SerializeField] private float sleepAngularVelocityThreshold = 0.1f;
    
    private Rigidbody rb;
    private Collider objectCollider;
    private Camera mainCamera;
    private bool isOptimized = false;
    
    void Start()
    {
        rb = GetComponent<Rigidbody>();
        objectCollider = GetComponent<Collider>();
        mainCamera = Camera.main;
        
        OptimizePhysicsSettings();
    }
    
    void OptimizePhysicsSettings()
    {
        if (rb != null)
        {
            // Optimize rigidbody settings
            rb.sleepThreshold = sleepVelocityThreshold;
            
            // Reduce collision detection for fast-moving objects
            if (rb.velocity.magnitude > 10f)
            {
                rb.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
            }
            else
            {
                rb.collisionDetectionMode = CollisionDetectionMode.Discrete;
            }
        }
        
        // Set up fixed timestep for consistent physics
        Time.fixedDeltaTime = 1f / 60f; // 60 FPS physics
    }
    
    void Update()
    {
        if (enableDistanceCulling)
        {
            PerformDistanceCulling();
        }
        
        if (enableLevelOfDetail)
        {
            PerformLODOptimization();
        }
        
        OptimizeBasedOnVelocity();
    }
    
    void PerformDistanceCulling()
    {
        if (mainCamera == null) return;
        
        float distanceToCamera = Vector3.Distance(transform.position, mainCamera.transform.position);
        
        if (distanceToCamera > cullingDistance)
        {
            if (!isOptimized)
            {
                // Disable physics for distant objects
                if (rb != null) rb.isKinematic = true;
                if (objectCollider != null) objectCollider.enabled = false;
                isOptimized = true;
            }
        }
        else
        {
            if (isOptimized)
            {
                // Re-enable physics for close objects
                if (rb != null) rb.isKinematic = false;
                if (objectCollider != null) objectCollider.enabled = true;
                isOptimized = false;
            }
        }
    }
    
    void PerformLODOptimization()
    {
        if (mainCamera == null) return;
        
        float distanceToCamera = Vector3.Distance(transform.position, mainCamera.transform.position);
        
        if (distanceToCamera > lodDistance)
        {
            // Reduce physics complexity
            if (rb != null)
            {
                rb.collisionDetectionMode = CollisionDetectionMode.Discrete;
                rb.interpolation = RigidbodyInterpolation.None;
            }
        }
        else
        {
            // Full physics quality
            if (rb != null)
            {
                rb.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
                rb.interpolation = RigidbodyInterpolation.Interpolate;
            }
        }
    }
    
    void OptimizeBasedOnVelocity()
    {
        if (rb == null) return;
        
        // Put nearly stationary objects to sleep
        if (rb.velocity.magnitude < sleepVelocityThreshold && 
            rb.angularVelocity.magnitude < sleepAngularVelocityThreshold)
        {
            rb.Sleep();
        }
        
        // Adjust collision detection based on speed
        if (rb.velocity.magnitude > 15f)
        {
            rb.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
        }
        else if (rb.velocity.magnitude > 5f)
        {
            rb.collisionDetectionMode = CollisionDetectionMode.Continuous;
        }
        else
        {
            rb.collisionDetectionMode = CollisionDetectionMode.Discrete;
        }
    }
    
    // Object pooling for physics objects
    public class PhysicsObjectPool : MonoBehaviour
    {
        [SerializeField] private GameObject physicsObjectPrefab;
        [SerializeField] private int poolSize = 100;
        
        private Queue<GameObject> pool = new Queue<GameObject>();
        
        void Start()
        {
            // Pre-instantiate physics objects
            for (int i = 0; i < poolSize; i++)
            {
                GameObject obj = Instantiate(physicsObjectPrefab);
                obj.SetActive(false);
                pool.Enqueue(obj);
            }
        }
        
        public GameObject GetPhysicsObject()
        {
            if (pool.Count > 0)
            {
                GameObject obj = pool.Dequeue();
                obj.SetActive(true);
                
                // Reset physics state
                Rigidbody rb = obj.GetComponent<Rigidbody>();
                if (rb != null)
                {
                    rb.velocity = Vector3.zero;
                    rb.angularVelocity = Vector3.zero;
                    rb.WakeUp();
                }
                
                return obj;
            }
            
            // Create new if pool is empty
            return Instantiate(physicsObjectPrefab);
        }
        
        public void ReturnPhysicsObject(GameObject obj)
        {
            obj.SetActive(false);
            pool.Enqueue(obj);
        }
    }
}
```

## Practical Applications

### Projectile Physics System

**Advanced Projectile Mechanics:**
```csharp
public class ProjectileSystem : MonoBehaviour
{
    [Header("Projectile Settings")]
    [SerializeField] private float initialVelocity = 20f;
    [SerializeField] private float gravity = 9.81f;
    [SerializeField] private float drag = 0.1f;
    [SerializeField] private float mass = 1f;
    
    [Header("Trajectory Prediction")]
    [SerializeField] private bool showTrajectory = true;
    [SerializeField] private int trajectoryPoints = 30;
    [SerializeField] private float trajectoryTimeStep = 0.1f;
    [SerializeField] private LineRenderer trajectoryLine;
    
    private Vector3 initialPosition;
    private Vector3 initialVelocityVector;
    private float timeInFlight;
    
    void Start()
    {
        if (trajectoryLine == null)
        {
            trajectoryLine = gameObject.AddComponent<LineRenderer>();
            trajectoryLine.material = new Material(Shader.Find("Sprites/Default"));
            trajectoryLine.color = Color.red;
            trajectoryLine.width = 0.1f;
        }
    }
    
    public void LaunchProjectile(Vector3 direction, float power = 1f)
    {
        initialPosition = transform.position;
        initialVelocityVector = direction.normalized * initialVelocity * power;
        timeInFlight = 0f;
        
        // If using Unity physics
        Rigidbody rb = GetComponent<Rigidbody>();
        if (rb != null)
        {
            rb.velocity = initialVelocityVector;
            rb.mass = mass;
            rb.drag = drag;
        }
    }
    
    // Manual physics calculation (for precise control)
    void UpdateManualPhysics()
    {
        timeInFlight += Time.deltaTime;
        
        // Calculate position using kinematic equations
        Vector3 position = CalculateProjectilePosition(timeInFlight);
        transform.position = position;
        
        // Calculate velocity for rotation
        Vector3 velocity = CalculateProjectileVelocity(timeInFlight);
        if (velocity.magnitude > 0.1f)
        {
            transform.rotation = Quaternion.LookRotation(velocity.normalized);
        }
    }
    
    Vector3 CalculateProjectilePosition(float time)
    {
        // x = x0 + v0x * t - 0.5 * drag * vx * t^2
        // y = y0 + v0y * t - 0.5 * g * t^2 - 0.5 * drag * vy * t^2
        
        Vector3 dragForce = -initialVelocityVector * drag;
        Vector3 gravityForce = new Vector3(0, -gravity, 0);
        
        Vector3 position = initialPosition + 
                          initialVelocityVector * time + 
                          0.5f * (gravityForce + dragForce) * time * time;
        
        return position;
    }
    
    Vector3 CalculateProjectileVelocity(float time)
    {
        Vector3 dragAcceleration = -initialVelocityVector.normalized * drag;
        Vector3 gravityAcceleration = new Vector3(0, -gravity, 0);
        
        Vector3 velocity = initialVelocityVector + 
                          (gravityAcceleration + dragAcceleration) * time;
        
        return velocity;
    }
    
    // Predict trajectory for aiming assistance
    public Vector3[] PredictTrajectory(Vector3 startPos, Vector3 velocity, int points, float timeStep)
    {
        Vector3[] trajectoryPoints = new Vector3[points];
        Vector3 currentPos = startPos;
        Vector3 currentVel = velocity;
        
        for (int i = 0; i < points; i++)
        {
            trajectoryPoints[i] = currentPos;
            
            // Update position and velocity for next point
            Vector3 acceleration = new Vector3(0, -gravity, 0) - currentVel * drag;
            currentVel += acceleration * timeStep;
            currentPos += currentVel * timeStep;
            
            // Stop if hits ground
            if (currentPos.y <= 0)
            {
                trajectoryPoints[i] = new Vector3(currentPos.x, 0, currentPos.z);
                break;
            }
        }
        
        return trajectoryPoints;
    }
    
    void Update()
    {
        if (showTrajectory)
        {
            UpdateTrajectoryVisualization();
        }
    }
    
    void UpdateTrajectoryVisualization()
    {
        if (trajectoryLine == null) return;
        
        Vector3[] points = PredictTrajectory(transform.position, initialVelocityVector, trajectoryPoints, trajectoryTimeStep);
        
        trajectoryLine.positionCount = points.Length;
        trajectoryLine.SetPositions(points);
    }
    
    // Calculate optimal angle for hitting target at distance
    public float CalculateOptimalAngle(float distance, float height = 0)
    {
        float v = initialVelocity;
        float g = gravity;
        
        // Solve: distance = (v^2 * sin(2θ)) / g
        float discriminant = Mathf.Pow(v, 4) - g * (g * distance * distance + 2 * height * v * v);
        
        if (discriminant < 0) return -1; // Target unreachable
        
        float angle1 = Mathf.Atan((v * v + Mathf.Sqrt(discriminant)) / (g * distance));
        float angle2 = Mathf.Atan((v * v - Mathf.Sqrt(discriminant)) / (g * distance));
        
        // Return the lower angle (more direct shot)
        return Mathf.Min(angle1, angle2) * Mathf.Rad2Deg;
    }
}
```

## Interview Preparation

### Physics Questions

**Common Technical Questions:**
- "How would you implement realistic car physics?"
- "Explain the difference between discrete and continuous collision detection"
- "How do you optimize physics performance for mobile devices?"
- "Implement a custom spring-damper system"

**Problem-Solving Examples:**
```csharp
// Interview question: "Create a bouncing ball that loses energy over time"
public class BouncingBall : MonoBehaviour
{
    [SerializeField] private float bounceMultiplier = 0.8f;
    [SerializeField] private float minVelocity = 0.1f;
    [SerializeField] private PhysicMaterial bouncyMaterial;
    
    private Rigidbody rb;
    private bool isRolling = false;
    
    void Start()
    {
        rb = GetComponent<Rigidbody>();
        
        // Create bouncy material
        bouncyMaterial = new PhysicMaterial();
        bouncyMaterial.bounciness = bounceMultiplier;
        GetComponent<Collider>().material = bouncyMaterial;
    }
    
    void OnCollisionEnter(Collision collision)
    {
        // Reduce velocity after each bounce
        if (collision.contacts[0].normal.y > 0.5f) // Hit ground
        {
            rb.velocity *= bounceMultiplier;
            
            if (rb.velocity.magnitude < minVelocity)
            {
                rb.velocity = Vector3.zero;
                isRolling = true;
            }
        }
    }
}
```

### Key Takeaways

**Physics System Mastery:**
- Understand Unity's physics components and their interactions
- Implement custom collision detection for specific game needs
- Optimize physics performance through culling and LOD systems
- Create realistic physics behaviors using proper material settings

**Practical Implementation Skills:**
- Build projectile systems with trajectory prediction
- Handle collision events with appropriate responses
- Implement physics-based character controllers
- Create breakable objects and destruction systems