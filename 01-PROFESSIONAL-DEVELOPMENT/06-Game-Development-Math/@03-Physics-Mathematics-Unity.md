# @03-Physics Mathematics Unity

## 🎯 Learning Objectives
- Master physics mathematics for realistic Unity game mechanics
- Apply Newtonian physics, forces, and momentum to gameplay systems
- Leverage AI tools for complex physics calculations and optimizations
- Build intuitive understanding of realistic movement and interactions

## ⚡ Newton's Laws in Unity

### First Law: Inertia and Constant Motion
**Unity Rigidbody Implementation**:
```csharp
public class InertiaDemo : MonoBehaviour 
{
    private Rigidbody rb;
    
    void Start() 
    {
        rb = GetComponent<Rigidbody>();
        
        // Object continues moving unless acted upon by force
        rb.velocity = new Vector3(5f, 0f, 0f); // Constant velocity
    }
    
    void Update() 
    {
        // Without external forces, object maintains constant velocity
        // Unity automatically handles this through Rigidbody physics
        
        if (Input.GetKeyDown(KeyCode.Space)) 
        {
            // Apply force to change motion (external force required)
            rb.AddForce(Vector3.up * 10f, ForceMode.Impulse);
        }
    }
}
```

### Second Law: F = ma (Force, Mass, Acceleration)
**Force Application Systems**:
```csharp
public class ForceCalculations : MonoBehaviour 
{
    public float mass = 1f;
    public float desiredAcceleration = 10f;
    
    private Rigidbody rb;
    
    void Start() 
    {
        rb = GetComponent<Rigidbody>();
        rb.mass = mass;
    }
    
    void FixedUpdate() 
    {
        // F = ma: Calculate required force for desired acceleration
        Vector3 inputDirection = GetInputDirection();
        Vector3 requiredForce = inputDirection * mass * desiredAcceleration;
        
        rb.AddForce(requiredForce, ForceMode.Force);
        
        // Alternative: Direct acceleration (Unity handles mass internally)
        // rb.AddForce(inputDirection * desiredAcceleration, ForceMode.Acceleration);
    }
    
    Vector3 GetInputDirection() 
    {
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");
        return new Vector3(horizontal, 0f, vertical).normalized;
    }
}
```

### Third Law: Action and Reaction
**Reaction Force Systems**:
```csharp
public class ActionReaction : MonoBehaviour 
{
    public float explosionForce = 1000f;
    public float explosionRadius = 10f;
    
    void OnTriggerEnter(Collider other) 
    {
        if (other.CompareTag("Player")) 
        {
            // Apply explosion force to all nearby objects
            Collider[] affectedObjects = Physics.OverlapSphere(transform.position, explosionRadius);
            
            foreach (Collider obj in affectedObjects) 
            {
                Rigidbody objRb = obj.GetComponent<Rigidbody>();
                if (objRb != null) 
                {
                    // Calculate force direction and magnitude
                    Vector3 forceDirection = (obj.transform.position - transform.position).normalized;
                    float distance = Vector3.Distance(transform.position, obj.transform.position);
                    
                    // Apply inverse square law for realistic force falloff
                    float forceMagnitude = explosionForce / (distance * distance + 1f);
                    
                    objRb.AddForce(forceDirection * forceMagnitude, ForceMode.Impulse);
                }
            }
        }
    }
}
```

## 🎱 Momentum and Collision Physics

### Linear Momentum Conservation
**Collision Response System**:
```csharp
public class MomentumCollision : MonoBehaviour 
{
    private Rigidbody rb;
    
    void Start() 
    {
        rb = GetComponent<Rigidbody>();
    }
    
    void OnCollisionEnter(Collision collision) 
    {
        Rigidbody otherRb = collision.rigidbody;
        if (otherRb != null) 
        {
            // Calculate momentum before collision
            Vector3 momentum1Before = rb.mass * rb.velocity;
            Vector3 momentum2Before = otherRb.mass * otherRb.velocity;
            Vector3 totalMomentumBefore = momentum1Before + momentum2Before;
            
            // Unity handles the collision response automatically
            // But we can add custom effects based on momentum transfer
            float impactMagnitude = totalMomentumBefore.magnitude;
            
            if (impactMagnitude > 10f) 
            {
                // Create impact effects for high-momentum collisions
                CreateImpactEffect(collision.contacts[0].point, impactMagnitude);
            }
        }
    }
    
    void CreateImpactEffect(Vector3 point, float intensity) 
    {
        // Spawn particles, play sounds, etc. based on collision intensity
        Debug.Log($"Impact at {point} with intensity {intensity}");
    }
}
```

### Custom Collision Resolution
**Manual Collision Response**:
```csharp
public class CustomCollisionResponse : MonoBehaviour 
{
    [Header("Collision Settings")]
    public float restitution = 0.8f; // Bounciness (0 = perfectly inelastic, 1 = perfectly elastic)
    
    void OnCollisionEnter(Collision collision) 
    {
        Rigidbody rb1 = GetComponent<Rigidbody>();
        Rigidbody rb2 = collision.rigidbody;
        
        if (rb2 != null) 
        {
            // Get collision normal
            Vector3 normal = collision.contacts[0].normal;
            
            // Calculate relative velocity
            Vector3 relativeVelocity = rb1.velocity - rb2.velocity;
            float velocityAlongNormal = Vector3.Dot(relativeVelocity, normal);
            
            // Don't resolve if velocities are separating
            if (velocityAlongNormal > 0) return;
            
            // Calculate impulse scalar
            float impulseScalar = -(1 + restitution) * velocityAlongNormal;
            impulseScalar /= 1/rb1.mass + 1/rb2.mass;
            
            // Apply impulse
            Vector3 impulse = impulseScalar * normal;
            rb1.velocity += impulse / rb1.mass;
            rb2.velocity -= impulse / rb2.mass;
        }
    }
}
```

## 🌊 Fluid Dynamics and Air Resistance

### Drag and Air Resistance
**Realistic Air Resistance**:
```csharp
public class AirResistance : MonoBehaviour 
{
    [Header("Drag Settings")]
    public float dragCoefficient = 0.47f; // Sphere drag coefficient
    public float airDensity = 1.225f; // kg/m³ at sea level
    public float crossSectionalArea = 1f; // m²
    
    private Rigidbody rb;
    
    void Start() 
    {
        rb = GetComponent<Rigidbody>();
    }
    
    void FixedUpdate() 
    {
        // Calculate drag force: F_drag = 0.5 * ρ * v² * C_d * A
        Vector3 velocity = rb.velocity;
        float speedSquared = velocity.sqrMagnitude;
        
        if (speedSquared > 0.01f) // Avoid division by zero
        {
            Vector3 dragDirection = -velocity.normalized;
            float dragMagnitude = 0.5f * airDensity * speedSquared * dragCoefficient * crossSectionalArea;
            
            Vector3 dragForce = dragDirection * dragMagnitude;
            rb.AddForce(dragForce, ForceMode.Force);
        }
    }
}
```

### Buoyancy Physics
**Water Buoyancy System**:
```csharp
public class BuoyancyPhysics : MonoBehaviour 
{
    [Header("Buoyancy Settings")]
    public float waterDensity = 1000f; // kg/m³
    public float objectVolume = 1f; // m³
    public float waterLevel = 0f;
    public float dragInWater = 0.99f;
    
    private Rigidbody rb;
    private bool isInWater = false;
    
    void Start() 
    {
        rb = GetComponent<Rigidbody>();
    }
    
    void FixedUpdate() 
    {
        float objectBottom = transform.position.y - transform.localScale.y * 0.5f;
        float objectTop = transform.position.y + transform.localScale.y * 0.5f;
        
        if (objectBottom < waterLevel) 
        {
            isInWater = true;
            
            // Calculate submerged volume
            float submergedHeight = Mathf.Min(waterLevel - objectBottom, transform.localScale.y);
            float submergedRatio = submergedHeight / transform.localScale.y;
            float submergedVolume = objectVolume * submergedRatio;
            
            // Apply buoyancy force: F_buoyancy = ρ_water * V_submerged * g
            float buoyancyForce = waterDensity * submergedVolume * Physics.gravity.magnitude;
            rb.AddForce(Vector3.up * buoyancyForce, ForceMode.Force);
            
            // Apply water drag
            rb.velocity *= dragInWater;
        }
        else 
        {
            isInWater = false;
        }
    }
}
```

## 🎯 Projectile Physics and Ballistics

### Parabolic Motion Calculations
**Advanced Projectile System**:
```csharp
public class BallisticsCalculator : MonoBehaviour 
{
    [Header("Ballistics Settings")]
    public float muzzleVelocity = 100f;
    public float projectileMass = 0.1f;
    public float gravity = 9.8f;
    
    public Vector3 CalculateTrajectoryVelocity(Vector3 target, float angle) 
    {
        Vector3 direction = target - transform.position;
        float horizontalDistance = new Vector3(direction.x, 0, direction.z).magnitude;
        float verticalDistance = direction.y;
        
        // Convert angle to radians
        float angleRad = angle * Mathf.Deg2Rad;
        
        // Calculate required velocity components
        float velocityMagnitude = Mathf.Sqrt(gravity * horizontalDistance * horizontalDistance / 
            (horizontalDistance * Mathf.Tan(angleRad) - verticalDistance) / Mathf.Cos(angleRad) / Mathf.Cos(angleRad));
        
        Vector3 horizontalDirection = new Vector3(direction.x, 0, direction.z).normalized;
        Vector3 velocity = horizontalDirection * velocityMagnitude * Mathf.Cos(angleRad) + 
                          Vector3.up * velocityMagnitude * Mathf.Sin(angleRad);
        
        return velocity;
    }
    
    public float CalculateFlightTime(Vector3 initialVelocity, float targetHeight) 
    {
        // Using kinematic equation: y = v₀t + 0.5at²
        // Rearranged to solve for time: t = (-v₀ ± √(v₀² + 2ah)) / a
        float a = -gravity;
        float v0 = initialVelocity.y;
        float deltaY = targetHeight - transform.position.y;
        
        float discriminant = v0 * v0 + 2 * a * deltaY;
        if (discriminant < 0) return -1f; // No solution
        
        float t1 = (-v0 + Mathf.Sqrt(discriminant)) / a;
        float t2 = (-v0 - Mathf.Sqrt(discriminant)) / a;
        
        // Return positive time
        return t1 > 0 ? t1 : t2;
    }
}
```

### Wind and Environmental Effects
**Environmental Physics**:
```csharp
public class EnvironmentalPhysics : MonoBehaviour 
{
    [Header("Wind Settings")]
    public Vector3 windVelocity = new Vector3(2f, 0f, 0f);
    public float windVariation = 0.5f;
    
    [Header("Temperature Effects")]
    public float temperature = 20f; // Celsius
    public float standardTemperature = 15f;
    
    private Rigidbody rb;
    
    void Start() 
    {
        rb = GetComponent<Rigidbody>();
    }
    
    void FixedUpdate() 
    {
        ApplyWindForce();
        ApplyTemperatureEffects();
    }
    
    void ApplyWindForce() 
    {
        // Add random variation to wind
        Vector3 currentWind = windVelocity + Random.insideUnitSphere * windVariation;
        
        // Wind force affects lighter objects more
        float windEffect = 1f / rb.mass;
        rb.AddForce(currentWind * windEffect, ForceMode.Force);
    }
    
    void ApplyTemperatureEffects() 
    {
        // Temperature affects air density and drag
        float temperatureFactor = (temperature + 273.15f) / (standardTemperature + 273.15f);
        float adjustedDrag = rb.drag / temperatureFactor;
        
        rb.drag = adjustedDrag;
    }
}
```

## 🚀 AI-Enhanced Physics Development

### Automated Physics Optimization
**AI-Powered Performance Tuning**:
```csharp
public class PhysicsOptimizer : MonoBehaviour 
{
    [Header("Performance Settings")]
    public int maxActiveRigidbodies = 100;
    public float sleepThreshold = 0.5f;
    
    private List<Rigidbody> managedRigidbodies = new List<Rigidbody>();
    
    void Start() 
    {
        // Find all rigidbodies in scene
        managedRigidbodies.AddRange(FindObjectsOfType<Rigidbody>());
        OptimizePhysicsSettings();
    }
    
    void OptimizePhysicsSettings() 
    {
        foreach (Rigidbody rb in managedRigidbodies) 
        {
            // AI-suggested optimizations
            rb.sleepThreshold = sleepThreshold;
            
            // Disable unnecessary physics for distant objects
            float distanceToPlayer = Vector3.Distance(rb.transform.position, Camera.main.transform.position);
            if (distanceToPlayer > 50f) 
            {
                rb.isKinematic = true; // Disable physics simulation
            }
        }
    }
    
    void Update() 
    {
        // Dynamic physics management
        int activeCount = managedRigidbodies.Count(rb => !rb.IsSleeping());
        
        if (activeCount > maxActiveRigidbodies) 
        {
            // Force sleep on least important objects
            var sortedByImportance = managedRigidbodies
                .OrderBy(rb => CalculateImportance(rb))
                .Take(activeCount - maxActiveRigidbodies);
            
            foreach (var rb in sortedByImportance) 
            {
                rb.Sleep();
            }
        }
    }
    
    float CalculateImportance(Rigidbody rb) 
    {
        float distanceToPlayer = Vector3.Distance(rb.transform.position, Camera.main.transform.position);
        float velocity = rb.velocity.magnitude;
        
        // Objects closer to player and moving faster are more important
        return 1f / (distanceToPlayer + 1f) + velocity;
    }
}
```

### Procedural Physics Interactions
**AI-Generated Physics Behaviors**:
```csharp
public class ProceduralPhysics : MonoBehaviour 
{
    public enum PhysicsBehavior { Bouncy, Heavy, Floaty, Sticky, Explosive }
    
    public PhysicsBehavior behaviorType;
    
    void Start() 
    {
        ApplyPhysicsBehavior();
    }
    
    void ApplyPhysicsBehavior() 
    {
        Rigidbody rb = GetComponent<Rigidbody>();
        PhysicMaterial physicsMaterial = new PhysicMaterial();
        
        switch (behaviorType) 
        {
            case PhysicsBehavior.Bouncy:
                physicsMaterial.bounciness = 0.9f;
                physicsMaterial.frictionCombine = PhysicMaterialCombine.Minimum;
                rb.mass = 0.5f;
                break;
                
            case PhysicsBehavior.Heavy:
                physicsMaterial.staticFriction = 0.8f;
                physicsMaterial.dynamicFriction = 0.6f;
                rb.mass = 10f;
                rb.drag = 2f;
                break;
                
            case PhysicsBehavior.Floaty:
                rb.mass = 0.1f;
                rb.drag = 5f;
                rb.useGravity = false;
                gameObject.AddComponent<BuoyancyPhysics>();
                break;
                
            case PhysicsBehavior.Sticky:
                physicsMaterial.staticFriction = 2f;
                physicsMaterial.frictionCombine = PhysicMaterialCombine.Maximum;
                break;
                
            case PhysicsBehavior.Explosive:
                gameObject.AddComponent<ActionReaction>();
                break;
        }
        
        GetComponent<Collider>().material = physicsMaterial;
    }
}
```

## 💡 Advanced Physics Concepts

### Gyroscopic Effects and Angular Momentum
**Gyroscope Simulation**:
```csharp
public class GyroscopeEffect : MonoBehaviour 
{
    [Header("Gyroscope Settings")]
    public float spinRate = 100f; // RPM
    public Vector3 spinAxis = Vector3.up;
    
    private Rigidbody rb;
    private Vector3 angularMomentum;
    
    void Start() 
    {
        rb = GetComponent<Rigidbody>();
        
        // Convert RPM to rad/s and set initial angular velocity
        float angularVelocity = spinRate * 2f * Mathf.PI / 60f;
        rb.angularVelocity = spinAxis.normalized * angularVelocity;
    }
    
    void FixedUpdate() 
    {
        // Calculate angular momentum: L = I * ω
        angularMomentum = rb.inertiaTensor.x * rb.angularVelocity.x * Vector3.right +
                         rb.inertiaTensor.y * rb.angularVelocity.y * Vector3.up +
                         rb.inertiaTensor.z * rb.angularVelocity.z * Vector3.forward;
        
        // Gyroscopic precession occurs when external torque is applied
        if (Input.GetKey(KeyCode.G)) 
        {
            Vector3 externalTorque = Vector3.forward * 10f;
            Vector3 precessionTorque = Vector3.Cross(angularMomentum.normalized, externalTorque);
            rb.AddTorque(precessionTorque, ForceMode.Force);
        }
    }
}
```

### Elastic and Plastic Deformation
**Material Response System**:
```csharp
public class DeformableObject : MonoBehaviour 
{
    [Header("Material Properties")]
    public float elasticLimit = 10f; // Force threshold for elastic deformation
    public float plasticLimit = 50f; // Force threshold for permanent deformation
    public float recoveryRate = 2f; // Rate of elastic recovery
    
    private Vector3 originalScale;
    private Vector3 currentDeformation = Vector3.zero;
    private Vector3 permanentDeformation = Vector3.zero;
    
    void Start() 
    {
        originalScale = transform.localScale;
    }
    
    void OnCollisionEnter(Collision collision) 
    {
        float impactForce = collision.impulse.magnitude / Time.fixedDeltaTime;
        
        if (impactForce > elasticLimit) 
        {
            Vector3 deformationDirection = collision.contacts[0].normal;
            float deformationAmount = (impactForce - elasticLimit) / 100f;
            
            if (impactForce > plasticLimit) 
            {
                // Permanent deformation
                permanentDeformation += deformationDirection * deformationAmount * 0.1f;
            }
            else 
            {
                // Temporary elastic deformation
                currentDeformation += deformationDirection * deformationAmount;
            }
            
            UpdateDeformation();
        }
    }
    
    void Update() 
    {
        // Elastic recovery
        currentDeformation = Vector3.Lerp(currentDeformation, Vector3.zero, recoveryRate * Time.deltaTime);
        UpdateDeformation();
    }
    
    void UpdateDeformation() 
    {
        Vector3 totalDeformation = currentDeformation + permanentDeformation;
        transform.localScale = originalScale + totalDeformation;
    }
}
```

Physics mathematics in Unity enables the creation of believable, interactive worlds where objects behave according to real-world principles, enhanced by AI tools for optimization and procedural behavior generation.