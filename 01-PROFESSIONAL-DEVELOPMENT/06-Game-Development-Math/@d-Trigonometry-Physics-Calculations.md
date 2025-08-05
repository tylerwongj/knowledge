# @d-Trigonometry-Physics-Calculations - Advanced Trigonometry for Game Physics

## 🎯 Learning Objectives
- Master trigonometric functions and their applications in game development
- Implement practical physics calculations for realistic game mechanics
- Develop AI-enhanced understanding of wave functions and periodic behavior
- Create systematic approach to circular motion and oscillation systems

## 🔧 Trigonometry and Physics Architecture

### The TRIG Framework for Physics Mathematics
```
T - Triangles: Master right triangle relationships and trigonometric ratios
R - Rotation: Apply trigonometry to circular motion and rotation calculations
I - Integration: Combine trigonometric functions with physics simulations
G - Gameplay: Implement trigonometry in practical game mechanics and systems
```

### Unity Trigonometry Physics System
```csharp
using UnityEngine;
using System.Collections.Generic;
using System;

/// <summary>
/// Comprehensive trigonometry and physics calculation system for Unity
/// Provides essential trigonometric operations and physics simulations
/// </summary>
public static class TrigonometryPhysicsUtility
{
    // Mathematical constants
    public const float PI = Mathf.PI;
    public const float TWO_PI = 2f * Mathf.PI;
    public const float HALF_PI = Mathf.PI * 0.5f;
    public const float DEG_TO_RAD = Mathf.PI / 180f;
    public const float RAD_TO_DEG = 180f / Mathf.PI;
    public const float EPSILON = 0.0001f;
    
    #region Basic Trigonometric Functions
    
    /// <summary>
    /// Calculate sine value with angle in degrees
    /// Essential for wave motion and oscillating systems
    /// </summary>
    public static float SinDegrees(float angleDegrees)
    {
        return Mathf.Sin(angleDegrees * DEG_TO_RAD);
    }
    
    /// <summary>
    /// Calculate cosine value with angle in degrees
    /// Critical for circular motion and position calculations
    /// </summary>
    public static float CosDegrees(float angleDegrees)
    {
        return Mathf.Cos(angleDegrees * DEG_TO_RAD);
    }
    
    /// <summary>
    /// Calculate tangent value with angle in degrees
    /// Useful for slope calculations and trajectory analysis
    /// </summary>
    public static float TanDegrees(float angleDegrees)
    {
        return Mathf.Tan(angleDegrees * DEG_TO_RAD);
    }
    
    /// <summary>
    /// Calculate angle from opposite and adjacent sides
    /// Essential for determining rotation angles from positions
    /// </summary>
    public static float Atan2Degrees(float opposite, float adjacent)
    {
        return Mathf.Atan2(opposite, adjacent) * RAD_TO_DEG;
    }
    
    /// <summary>
    /// Calculate hypotenuse length from two sides
    /// Basic Pythagorean theorem implementation
    /// </summary>
    public static float Hypotenuse(float sideA, float sideB)
    {
        return Mathf.Sqrt(sideA * sideA + sideB * sideB);
    }
    
    #endregion
    
    #region Circular Motion and Rotation
    
    /// <summary>
    /// Calculate position on circle given center, radius, and angle
    /// Essential for orbital motion and circular patterns
    /// </summary>
    public static Vector2 PointOnCircle(Vector2 center, float radius, float angleDegrees)
    {
        float angleRad = angleDegrees * DEG_TO_RAD;
        return new Vector2(
            center.x + radius * Mathf.Cos(angleRad),
            center.y + radius * Mathf.Sin(angleRad)
        );
    }
    
    /// <summary>
    /// Calculate 3D position on sphere given center, radius, and spherical coordinates
    /// Critical for 3D orbital motion and procedural positioning
    /// </summary>
    public static Vector3 PointOnSphere(Vector3 center, float radius, float azimuthDegrees, float elevationDegrees)
    {
        float azimuthRad = azimuthDegrees * DEG_TO_RAD;
        float elevationRad = elevationDegrees * DEG_TO_RAD;
        
        float cosElevation = Mathf.Cos(elevationRad);
        
        return new Vector3(
            center.x + radius * cosElevation * Mathf.Cos(azimuthRad),
            center.y + radius * Mathf.Sin(elevationRad),
            center.z + radius * cosElevation * Mathf.Sin(azimuthRad)
        );
    }
    
    /// <summary>
    /// Calculate angular velocity for circular motion
    /// Essential for consistent rotational movement
    /// </summary>
    public static float AngularVelocity(float radius, float linearSpeed)
    {
        if (radius < EPSILON) return 0f;
        return linearSpeed / radius * RAD_TO_DEG;
    }
    
    /// <summary>
    /// Calculate centripetal acceleration for circular motion
    /// Critical for realistic circular motion physics
    /// </summary>
    public static float CentripetalAcceleration(float velocity, float radius)
    {
        if (radius < EPSILON) return 0f;
        return (velocity * velocity) / radius;
    }
    
    #endregion
    
    #region Wave Functions and Oscillation
    
    /// <summary>
    /// Generate sine wave value with customizable parameters
    /// Essential for smooth oscillating motion and animation
    /// </summary>
    public static float SineWave(float time, float amplitude = 1f, float frequency = 1f, float phase = 0f, float offset = 0f)
    {
        return amplitude * Mathf.Sin(TWO_PI * frequency * time + phase) + offset;
    }
    
    /// <summary>
    /// Generate cosine wave value with customizable parameters
    /// Useful for phase-shifted oscillations and circular motion
    /// </summary>
    public static float CosineWave(float time, float amplitude = 1f, float frequency = 1f, float phase = 0f, float offset = 0f)
    {
        return amplitude * Mathf.Cos(TWO_PI * frequency * time + phase) + offset;
    }
    
    /// <summary>
    /// Generate damped oscillation (exponentially decaying sine wave)
    /// Critical for realistic spring physics and bouncing effects
    /// </summary>
    public static float DampedOscillation(float time, float amplitude = 1f, float frequency = 1f, float dampingFactor = 0.1f, float phase = 0f)
    {
        return amplitude * Mathf.Exp(-dampingFactor * time) * Mathf.Sin(TWO_PI * frequency * time + phase);
    }
    
    /// <summary>
    /// Generate square wave for digital/binary animations
    /// Useful for blinking effects and discrete state changes
    /// </summary>
    public static float SquareWave(float time, float frequency = 1f, float dutyCycle = 0.5f)
    {
        float phase = (time * frequency) % 1f;
        return phase < dutyCycle ? 1f : -1f;
    }
    
    /// <summary>
    /// Generate triangle wave for linear oscillation
    /// Perfect for back-and-forth motion with constant speed
    /// </summary>
    public static float TriangleWave(float time, float frequency = 1f, float amplitude = 1f)
    {
        float phase = (time * frequency) % 1f;
        return amplitude * (2f * Mathf.Abs(2f * phase - 1f) - 1f);
    }
    
    #endregion
    
    #region Physics Calculations
    
    /// <summary>
    /// Calculate projectile trajectory position at given time
    /// Essential for ballistic calculations and projectile weapons
    /// </summary>
    public static Vector3 ProjectilePosition(Vector3 initialPosition, Vector3 initialVelocity, float time, float gravity = -9.81f)
    {
        Vector3 gravityVector = new Vector3(0, gravity, 0);
        return initialPosition + initialVelocity * time + 0.5f * gravityVector * time * time;
    }
    
    /// <summary>
    /// Calculate projectile velocity at given time
    /// Critical for impact calculations and physics simulation
    /// </summary>
    public static Vector3 ProjectileVelocity(Vector3 initialVelocity, float time, float gravity = -9.81f)
    {
        Vector3 gravityVector = new Vector3(0, gravity, 0);
        return initialVelocity + gravityVector * time;
    }
    
    /// <summary>
    /// Calculate launch angle for projectile to hit target
    /// Essential for AI targeting and artillery systems
    /// </summary>
    public static float CalculateLaunchAngle(Vector3 startPosition, Vector3 targetPosition, float launchSpeed, float gravity = 9.81f)
    {
        Vector3 displacement = targetPosition - startPosition;
        float horizontalDistance = new Vector2(displacement.x, displacement.z).magnitude;
        float verticalDistance = displacement.y;
        
        float speedSquared = launchSpeed * launchSpeed;
        float gravityDistance = gravity * horizontalDistance;
        
        float discriminant = speedSquared * speedSquared - gravity * (gravity * horizontalDistance * horizontalDistance + 2f * verticalDistance * speedSquared);
        
        if (discriminant < 0) return -1f; // No solution possible
        
        float angle1 = Mathf.Atan((speedSquared + Mathf.Sqrt(discriminant)) / gravityDistance);
        float angle2 = Mathf.Atan((speedSquared - Mathf.Sqrt(discriminant)) / gravityDistance);
        
        // Return the lower angle (more direct trajectory)
        return Mathf.Min(angle1, angle2) * RAD_TO_DEG;
    }
    
    /// <summary>
    /// Calculate pendulum motion angle at given time
    /// Perfect for swinging objects and pendulum mechanics
    /// </summary>
    public static float PendulumAngle(float time, float amplitude, float length, float gravity = 9.81f)
    {
        float angularFrequency = Mathf.Sqrt(gravity / length);
        return amplitude * Mathf.Cos(angularFrequency * time);
    }
    
    /// <summary>
    /// Calculate spring force using Hooke's law
    /// Essential for elastic physics and spring systems
    /// </summary>
    public static float SpringForce(float displacement, float springConstant)
    {
        return -springConstant * displacement;
    }
    
    /// <summary>
    /// Calculate harmonic oscillator position
    /// Critical for spring-mass systems and oscillating objects
    /// </summary>
    public static float HarmonicOscillatorPosition(float time, float amplitude, float frequency, float phase = 0f, float dampingFactor = 0f)
    {
        if (dampingFactor > 0f)
        {
            return amplitude * Mathf.Exp(-dampingFactor * time) * Mathf.Cos(TWO_PI * frequency * time + phase);
        }
        else
        {
            return amplitude * Mathf.Cos(TWO_PI * frequency * time + phase);
        }
    }
    
    #endregion
    
    #region Angle Utilities
    
    /// <summary>
    /// Normalize angle to range [0, 360) degrees
    /// Essential for consistent angle calculations and comparisons
    /// </summary>
    public static float NormalizeAngle360(float angle)
    {
        angle = angle % 360f;
        if (angle < 0f) angle += 360f;
        return angle;
    }
    
    /// <summary>
    /// Normalize angle to range [-180, 180] degrees
    /// Useful for calculating shortest angular distance
    /// </summary>
    public static float NormalizeAngle180(float angle)
    {
        angle = NormalizeAngle360(angle);
        if (angle > 180f) angle -= 360f;
        return angle;
    }
    
    /// <summary>
    /// Calculate shortest angular distance between two angles
    /// Critical for smooth rotation and angular interpolation
    /// </summary>
    public static float AngleDifference(float angleA, float angleB)
    {
        float diff = NormalizeAngle180(angleB - angleA);
        return diff;
    }
    
    /// <summary>
    /// Interpolate between two angles taking shortest path
    /// Essential for smooth angular animations and rotations
    /// </summary>
    public static float LerpAngle(float fromAngle, float toAngle, float t)
    {
        float diff = AngleDifference(fromAngle, toAngle);
        return fromAngle + diff * Mathf.Clamp01(t);
    }
    
    #endregion
    
    #region Advanced Physics
    
    /// <summary>
    /// Calculate orbital velocity for circular orbit
    /// Essential for space games and orbital mechanics
    /// </summary>
    public static float OrbitalVelocity(float centralMass, float orbitRadius, float gravitationalConstant = 6.67430e-11f)
    {
        return Mathf.Sqrt(gravitationalConstant * centralMass / orbitRadius);
    }
    
    /// <summary>
    /// Calculate escape velocity from gravitational body
    /// Critical for space travel and rocket physics
    /// </summary>
    public static float EscapeVelocity(float mass, float radius, float gravitationalConstant = 6.67430e-11f)
    {
        return Mathf.Sqrt(2f * gravitationalConstant * mass / radius);
    }
    
    /// <summary>
    /// Calculate Doppler effect frequency shift
    /// Useful for sound effects and radar systems
    /// </summary>
    public static float DopplerShift(float sourceFrequency, float sourceVelocity, float observerVelocity, float waveSpeed = 343f)
    {
        return sourceFrequency * (waveSpeed + observerVelocity) / (waveSpeed + sourceVelocity);
    }
    
    #endregion
}

/// <summary>
/// Practical trigonometry and physics examples for game development
/// Demonstrates real-world application of mathematical concepts
/// </summary>
public class TrigonometryPhysicsExamples : MonoBehaviour
{
    [Header("Orbital Motion Settings")]
    public Transform orbitCenter;
    public float orbitRadius = 5f;
    public float orbitSpeed = 30f; // degrees per second
    public bool useEllipticalOrbit = false;
    public float ellipseRatioB = 0.7f;
    
    [Header("Oscillation Settings")]
    public float oscillationAmplitude = 2f;
    public float oscillationFrequency = 1f;
    public float dampingFactor = 0.1f;
    public AnimationCurve oscillationCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);
    
    [Header("Projectile Settings")]
    public Transform projectilePrefab;
    public Transform targetMarker;
    public float launchSpeed = 20f;
    public float gravity = 9.81f;
    
    [Header("Wave Motion Settings")]
    public Transform[] waveObjects;
    public float waveAmplitude = 1f;
    public float waveFrequency = 0.5f;
    public float waveSpeed = 2f;
    
    private float currentOrbitAngle = 0f;
    private float startTime;
    private Vector3[] waveObjectBasePositions;
    
    void Start()
    {
        startTime = Time.time;
        
        // Store base positions for wave objects
        if (waveObjects != null && waveObjects.Length > 0)
        {
            waveObjectBasePositions = new Vector3[waveObjects.Length];
            for (int i = 0; i < waveObjects.Length; i++)
            {
                if (waveObjects[i] != null)
                {
                    waveObjectBasePositions[i] = waveObjects[i].position;
                }
            }
        }
    }
    
    void Update()
    {
        float currentTime = Time.time - startTime;
        
        // Example 1: Orbital motion
        DemonstrateOrbitalMotion(currentTime);
        
        // Example 2: Oscillation and wave motion
        DemonstrateOscillation(currentTime);
        
        // Example 3: Wave propagation
        DemonstrateWaveMotion(currentTime);
        
        // Handle input for projectile launch
        if (Input.GetKeyDown(KeyCode.Space) && projectilePrefab != null && targetMarker != null)
        {
            LaunchProjectileAtTarget();
        }
    }
    
    #region Orbital Motion Examples
    
    /// <summary>
    /// Example: Orbital motion using trigonometry
    /// Demonstrates circular and elliptical orbit calculations
    /// </summary>
    void DemonstrateOrbitalMotion(float time)
    {
        if (orbitCenter == null) return;
        
        // Update orbit angle
        currentOrbitAngle += orbitSpeed * Time.deltaTime;
        currentOrbitAngle = TrigonometryPhysicsUtility.NormalizeAngle360(currentOrbitAngle);
        
        Vector3 orbitPosition;
        
        if (useEllipticalOrbit)
        {
            // Elliptical orbit
            float radiusX = orbitRadius;
            float radiusZ = orbitRadius * ellipseRatioB;
            
            orbitPosition = new Vector3(
                orbitCenter.position.x + radiusX * TrigonometryPhysicsUtility.CosDegrees(currentOrbitAngle),
                orbitCenter.position.y,
                orbitCenter.position.z + radiusZ * TrigonometryPhysicsUtility.SinDegrees(currentOrbitAngle)
            );
        }
        else
        {
            // Circular orbit
            Vector2 circlePoint = TrigonometryPhysicsUtility.PointOnCircle(
                new Vector2(orbitCenter.position.x, orbitCenter.position.z),
                orbitRadius,
                currentOrbitAngle
            );
            
            orbitPosition = new Vector3(circlePoint.x, orbitCenter.position.y, circlePoint.y);
        }
        
        transform.position = orbitPosition;
        
        // Make object face forward along orbit
        Vector3 tangent = new Vector3(
            -TrigonometryPhysicsUtility.SinDegrees(currentOrbitAngle),
            0,
            TrigonometryPhysicsUtility.CosDegrees(currentOrbitAngle)
        );
        
        if (tangent != Vector3.zero)
        {
            transform.rotation = Quaternion.LookRotation(tangent);
        }
    }
    
    #endregion
    
    #region Oscillation Examples
    
    /// <summary>
    /// Example: Various oscillation patterns using trigonometry
    /// Demonstrates sine waves, damped oscillation, and harmonic motion
    /// </summary>
    void DemonstrateOscillation(float time)
    {
        if (orbitCenter == null) return;
        
        // Simple harmonic oscillation on Y axis
        float oscillationY = TrigonometryPhysicsUtility.DampedOscillation(
            time,
            oscillationAmplitude,
            oscillationFrequency,
            dampingFactor
        );
        
        // Add curve-based variation
        float curveMultiplier = oscillationCurve.Evaluate(Mathf.PingPong(time * 0.5f, 1f));
        
        Vector3 oscillationOffset = new Vector3(0, oscillationY * curveMultiplier, 0);
        
        // Apply to position if not doing orbital motion
        if (!enabled || orbitCenter == null)
        {
            transform.position = transform.position + oscillationOffset;
        }
    }
    
    #endregion
    
    #region Wave Motion Examples
    
    /// <summary>
    /// Example: Wave propagation across multiple objects
    /// Demonstrates wave physics and synchronized motion
    /// </summary>
    void DemonstrateWaveMotion(float time)
    {
        if (waveObjects == null || waveObjectBasePositions == null) return;
        
        for (int i = 0; i < waveObjects.Length; i++)
        {
            if (waveObjects[i] == null) continue;
            
            // Calculate phase offset based on position in array
            float phaseOffset = (float)i / waveObjects.Length * TrigonometryPhysicsUtility.TWO_PI;
            
            // Calculate wave height using sine wave
            float waveHeight = TrigonometryPhysicsUtility.SineWave(
                time,
                waveAmplitude,
                waveFrequency,
                phaseOffset + time * waveSpeed
            );
            
            // Apply wave motion to Y position
            Vector3 newPosition = waveObjectBasePositions[i];
            newPosition.y += waveHeight;
            waveObjects[i].position = newPosition;
            
            // Optional: Add rotation based on wave slope
            float waveSlope = TrigonometryPhysicsUtility.CosineWave(
                time,
                waveAmplitude * waveFrequency * TrigonometryPhysicsUtility.TWO_PI,
                waveFrequency,
                phaseOffset + time * waveSpeed
            );
            
            float rotationAngle = Mathf.Atan(waveSlope) * TrigonometryPhysicsUtility.RAD_TO_DEG;
            waveObjects[i].rotation = Quaternion.Euler(0, 0, rotationAngle);
        }
    }
    
    #endregion
    
    #region Projectile Examples
    
    /// <summary>
    /// Example: Projectile physics with trigonometric calculations
    /// Demonstrates ballistic trajectory and targeting
    /// </summary>
    void LaunchProjectileAtTarget()
    {
        if (projectilePrefab == null || targetMarker == null) return;
        
        Vector3 startPosition = transform.position;
        Vector3 targetPosition = targetMarker.position;
        
        // Calculate optimal launch angle
        float launchAngle = TrigonometryPhysicsUtility.CalculateLaunchAngle(
            startPosition,
            targetPosition,
            launchSpeed,
            gravity
        );
        
        if (launchAngle < 0)
        {
            Debug.LogWarning("Target is out of range!");
            return;
        }
        
        // Calculate launch direction
        Vector3 horizontalDirection = (targetPosition - startPosition);
        horizontalDirection.y = 0;
        horizontalDirection.Normalize();
        
        // Calculate initial velocity
        Vector3 initialVelocity = horizontalDirection * launchSpeed * TrigonometryPhysicsUtility.CosDegrees(launchAngle);
        initialVelocity.y = launchSpeed * TrigonometryPhysicsUtility.SinDegrees(launchAngle);
        
        // Instantiate and launch projectile
        GameObject projectile = Instantiate(projectilePrefab.gameObject, startPosition, Quaternion.identity);
        Rigidbody rb = projectile.GetComponent<Rigidbody>();
        
        if (rb != null)
        {
            rb.velocity = initialVelocity;
            
            // Add projectile trajectory component
            ProjectileTrajectory trajectory = projectile.AddComponent<ProjectileTrajectory>();
            trajectory.Initialize(initialVelocity, gravity);
        }
    }
    
    #endregion
    
    #region Debug Visualization
    
    /// <summary>
    /// Visualize trigonometric calculations and physics in Scene view
    /// Essential for debugging and understanding mathematical relationships
    /// </summary>
    void OnDrawGizmos()
    {
        if (orbitCenter != null)
        {
            // Draw orbit path
            Gizmos.color = Color.yellow;
            
            if (useEllipticalOrbit)
            {
                // Draw ellipse approximation
                Vector3 previousPoint = Vector3.zero;
                int segments = 64;
                
                for (int i = 0; i <= segments; i++)
                {
                    float angle = (float)i / segments * 360f;
                    float radiusX = orbitRadius;
                    float radiusZ = orbitRadius * ellipseRatioB;
                    
                    Vector3 point = new Vector3(
                        orbitCenter.position.x + radiusX * TrigonometryPhysicsUtility.CosDegrees(angle),
                        orbitCenter.position.y,
                        orbitCenter.position.z + radiusZ * TrigonometryPhysicsUtility.SinDegrees(angle)
                    );
                    
                    if (i > 0)
                    {
                        Gizmos.DrawLine(previousPoint, point);
                    }
                    previousPoint = point;
                }
            }
            else
            {
                // Draw circular orbit
                float radius = orbitRadius;
                Vector3 center = orbitCenter.position;
                
                Vector3 previousPoint = center + new Vector3(radius, 0, 0);
                int segments = 64;
                
                for (int i = 1; i <= segments; i++)
                {
                    float angle = (float)i / segments * 360f;
                    Vector3 point = center + new Vector3(
                        radius * TrigonometryPhysicsUtility.CosDegrees(angle),
                        0,
                        radius * TrigonometryPhysicsUtility.SinDegrees(angle)
                    );
                    
                    Gizmos.DrawLine(previousPoint, point);
                    previousPoint = point;
                }
            }
            
            // Draw current position indicator
            Gizmos.color = Color.red;
            Gizmos.DrawSphere(transform.position, 0.2f);
            
            // Draw velocity vector
            if (Application.isPlaying)
            {
                Gizmos.color = Color.blue;
                Vector3 tangent = new Vector3(
                    -TrigonometryPhysicsUtility.SinDegrees(currentOrbitAngle),
                    0,
                    TrigonometryPhysicsUtility.CosDegrees(currentOrbitAngle)
                );
                Gizmos.DrawLine(transform.position, transform.position + tangent * 2f);
            }
        }
        
        // Draw wave objects connections
        if (waveObjects != null && waveObjects.Length > 1)
        {
            Gizmos.color = Color.green;
            for (int i = 0; i < waveObjects.Length - 1; i++)
            {
                if (waveObjects[i] != null && waveObjects[i + 1] != null)
                {
                    Gizmos.DrawLine(waveObjects[i].position, waveObjects[i + 1].position);
                }
            }
        }
        
        // Draw projectile trajectory prediction
        if (targetMarker != null && Application.isPlaying)
        {
            Gizmos.color = Color.cyan;
            Vector3 startPos = transform.position;
            Vector3 targetPos = targetMarker.position;
            
            float angle = TrigonometryPhysicsUtility.CalculateLaunchAngle(startPos, targetPos, launchSpeed, gravity);
            
            if (angle >= 0)
            {
                Vector3 horizontalDir = (targetPos - startPos);
                horizontalDir.y = 0;
                horizontalDir.Normalize();
                
                Vector3 initialVel = horizontalDir * launchSpeed * TrigonometryPhysicsUtility.CosDegrees(angle);
                initialVel.y = launchSpeed * TrigonometryPhysicsUtility.SinDegrees(angle);
                
                // Draw trajectory arc
                Vector3 previousPoint = startPos;
                float timeStep = 0.1f;
                float maxTime = 5f;
                
                for (float t = timeStep; t <= maxTime; t += timeStep)
                {
                    Vector3 trajectoryPoint = TrigonometryPhysicsUtility.ProjectilePosition(startPos, initialVel, t, -gravity);
                    
                    if (trajectoryPoint.y < startPos.y - 10f) break; // Stop if too low
                    
                    Gizmos.DrawLine(previousPoint, trajectoryPoint);
                    previousPoint = trajectoryPoint;
                }
            }
        }
    }
    
    #endregion
}

/// <summary>
/// Projectile trajectory component for realistic ballistic motion
/// Demonstrates physics integration with trigonometric calculations
/// </summary>
public class ProjectileTrajectory : MonoBehaviour
{
    private Vector3 initialVelocity;
    private float gravity;
    private float startTime;
    private Vector3 startPosition;
    private TrailRenderer trail;
    
    public void Initialize(Vector3 velocity, float gravityValue)
    {
        initialVelocity = velocity;
        gravity = gravityValue;
        startTime = Time.time;
        startPosition = transform.position;
        
        // Add trail renderer for visual effect
        trail = GetComponent<TrailRenderer>();
        if (trail == null)
        {
            trail = gameObject.AddComponent<TrailRenderer>();
            trail.time = 3f;
            trail.startWidth = 0.1f;
            trail.endWidth = 0.05f;
            trail.material = new Material(Shader.Find("Sprites/Default"));
            trail.color = Color.red;
        }
        
        // Destroy after reasonable time
        Destroy(gameObject, 10f);
    }
    
    void Update()
    {
        float currentTime = Time.time - startTime;
        
        // Calculate position using physics equations
        Vector3 currentPosition = TrigonometryPhysicsUtility.ProjectilePosition(
            startPosition,
            initialVelocity,
            currentTime,
            -gravity
        );
        
        transform.position = currentPosition;
        
        // Calculate current velocity for rotation
        Vector3 currentVelocity = TrigonometryPhysicsUtility.ProjectileVelocity(
            initialVelocity,
            currentTime,
            -gravity
        );
        
        // Orient projectile along velocity vector
        if (currentVelocity.magnitude > 0.1f)
        {
            transform.rotation = Quaternion.LookRotation(currentVelocity.normalized);
        }
        
        // Check for ground collision
        if (currentPosition.y < 0f)
        {
            OnGroundHit();
        }
    }
    
    void OnGroundHit()
    {
        // Create impact effect or handle collision
        Debug.Log($"Projectile hit ground at: {transform.position}");
        
        // Optional: Create explosion or impact effect
        // Instantiate(explosionEffect, transform.position, Quaternion.identity);
        
        Destroy(gameObject);
    }
}

/// <summary>
/// Advanced trigonometric calculations for specialized game mechanics
/// Includes Fourier analysis, complex wave patterns, and mathematical modeling
/// </summary>
public static class AdvancedTrigonometry
{
    #region Fourier Analysis
    
    /// <summary>
    /// Generate complex wave by combining multiple sine waves (additive synthesis)
    /// Essential for realistic sound synthesis and complex motion patterns
    /// </summary>
    public static float FourierSynthesis(float time, float[] amplitudes, float[] frequencies, float[] phases)
    {
        float result = 0f;
        
        for (int i = 0; i < amplitudes.Length && i < frequencies.Length && i < phases.Length; i++)
        {
            result += TrigonometryPhysicsUtility.SineWave(time, amplitudes[i], frequencies[i], phases[i]);
        }
        
        return result;
    }
    
    /// <summary>
    /// Generate sawtooth wave using Fourier series approximation
    /// Useful for sharp, angular motion patterns
    /// </summary>
    public static float SawtoothWave(float time, float frequency = 1f, float amplitude = 1f, int harmonics = 10)
    {
        float result = 0f;
        
        for (int n = 1; n <= harmonics; n++)
        {
            float harmonicAmplitude = amplitude / n;
            result += harmonicAmplitude * TrigonometryPhysicsUtility.SineWave(time, 1f, frequency * n);
        }
        
        return result * (2f / Mathf.PI);
    }
    
    #endregion
    
    #region Complex Motion Patterns
    
    /// <summary>
    /// Generate Lissajous curve for complex orbital patterns
    /// Perfect for decorative motion and mathematical art
    /// </summary>
    public static Vector2 LissajousCurve(float time, float amplitudeX, float amplitudeY, float frequencyX, float frequencyY, float phaseShift = 0f)
    {
        return new Vector2(
            amplitudeX * TrigonometryPhysicsUtility.SinDegrees(frequencyX * time * 360f),
            amplitudeY * TrigonometryPhysicsUtility.SinDegrees(frequencyY * time * 360f + phaseShift)
        );
    }
    
    /// <summary>
    /// Generate cycloid curve (wheel rolling motion)
    /// Essential for realistic wheel physics and rolling objects
    /// </summary>
    public static Vector2 CycloidCurve(float time, float radius, float speed)
    {
        float angle = speed * time;
        return new Vector2(
            radius * (angle - TrigonometryPhysicsUtility.SinDegrees(angle * TrigonometryPhysicsUtility.RAD_TO_DEG)),
            radius * (1f - TrigonometryPhysicsUtility.CosDegrees(angle * TrigonometryPhysicsUtility.RAD_TO_DEG))
        );
    }
    
    /// <summary>
    /// Generate epicycloid curve (circle rolling around circle)
    /// Perfect for gear mechanisms and planetary motion
    /// </summary>
    public static Vector2 EpicycloidCurve(float time, float majorRadius, float minorRadius, float speed)
    {
        float angle = speed * time;
        float ratio = (majorRadius + minorRadius) / minorRadius;
        
        return new Vector2(
            (majorRadius + minorRadius) * TrigonometryPhysicsUtility.CosDegrees(angle * TrigonometryPhysicsUtility.RAD_TO_DEG) - 
            minorRadius * TrigonometryPhysicsUtility.CosDegrees(ratio * angle * TrigonometryPhysicsUtility.RAD_TO_DEG),
            (majorRadius + minorRadius) * TrigonometryPhysicsUtility.SinDegrees(angle * TrigonometryPhysicsUtility.RAD_TO_DEG) - 
            minorRadius * TrigonometryPhysicsUtility.SinDegrees(ratio * angle * TrigonometryPhysicsUtility.RAD_TO_DEG)
        );
    }
    
    #endregion
    
    #region Physics Modeling
    
    /// <summary>
    /// Calculate coupled oscillator system (two connected springs)
    /// Essential for realistic physics simulations with multiple objects
    /// </summary>
    public static Vector2 CoupledOscillators(float time, float mass1, float mass2, float springConstant, float couplingConstant, Vector2 initialConditions)
    {
        float totalMass = mass1 + mass2;
        float reducedMass = (mass1 * mass2) / totalMass;
        
        float omega1 = Mathf.Sqrt(springConstant / mass1);
        float omega2 = Mathf.Sqrt((springConstant + 2f * couplingConstant) / reducedMass);
        
        float amplitude1 = initialConditions.x;
        float amplitude2 = initialConditions.y;
        
        return new Vector2(
            amplitude1 * TrigonometryPhysicsUtility.CosineWave(time, 1f, omega1 / TrigonometryPhysicsUtility.TWO_PI),
            amplitude2 * TrigonometryPhysicsUtility.CosineWave(time, 1f, omega2 / TrigonometryPhysicsUtility.TWO_PI)
        );
    }
    
    /// <summary>
    /// Calculate wave interference pattern
    /// Critical for realistic wave physics and sound simulation
    /// </summary>
    public static float WaveInterference(float position, float time, float frequency1, float amplitude1, float frequency2, float amplitude2, float phase1 = 0f, float phase2 = 0f)
    {
        float wave1 = amplitude1 * TrigonometryPhysicsUtility.SineWave(time - position / frequency1, 1f, frequency1, phase1);
        float wave2 = amplitude2 * TrigonometryPhysicsUtility.SineWave(time - position / frequency2, 1f, frequency2, phase2);
        
        return wave1 + wave2;
    }
    
    #endregion
}
```

## 🎯 Trigonometry Physics Fundamentals

### Core Trigonometric Concepts
```markdown
## Essential Trigonometry for Game Physics

### Basic Trigonometric Functions
**Sine (sin)**: Opposite side / Hypotenuse - Essential for vertical motion and wave patterns
**Cosine (cos)**: Adjacent side / Hypotenuse - Critical for horizontal motion and circular paths
**Tangent (tan)**: Opposite side / Adjacent side - Useful for slopes and angular relationships

### Unit Circle Relationships
**Angle Measurement**: Degrees (0-360°) and Radians (0-2π) conversion
**Quadrant Analysis**: Understanding sign patterns across four quadrants
**Reference Angles**: Simplifying calculations using acute angle relationships

### Physics Applications
**Circular Motion**: Position calculation using cos and sin for x and y coordinates
**Wave Motion**: Sine and cosine functions for oscillating systems
**Projectile Motion**: Trigonometry for launch angles and trajectory calculations
**Force Decomposition**: Breaking forces into horizontal and vertical components
```

### Practical Physics Implementations
```csharp
/// <summary>
/// Real-world physics applications using trigonometry
/// Demonstrates practical implementation patterns for game development
/// </summary>
public class PhysicsApplications : MonoBehaviour
{
    /// <summary>
    /// Example: Character movement on slopes using trigonometry
    /// Shows how to maintain constant speed regardless of slope angle
    /// </summary>
    public void MoveOnSlope(float moveSpeed, float slopeAngle)
    {
        // Calculate movement components for slope
        Vector3 slopeDirection = new Vector3(
            TrigonometryPhysicsUtility.CosDegrees(slopeAngle),
            TrigonometryPhysicsUtility.SinDegrees(slopeAngle),
            0
        );
        
        // Apply movement maintaining constant speed
        Vector3 movement = slopeDirection * moveSpeed * Time.deltaTime;
        transform.position += movement;
    }
    
    /// <summary>
    /// Example: Camera shake using trigonometric noise
    /// Demonstrates realistic camera shake effects using wave functions
    /// </summary>
    public Vector3 CalculateCameraShake(float intensity, float frequency, float time)
    {
        float shakeX = TrigonometryPhysicsUtility.SineWave(time, intensity, frequency, 0f);
        float shakeY = TrigonometryPhysicsUtility.CosineWave(time, intensity, frequency * 1.3f, Mathf.PI * 0.25f);
        float shakeZ = TrigonometryPhysicsUtility.SineWave(time, intensity * 0.5f, frequency * 0.8f, Mathf.PI * 0.5f);
        
        return new Vector3(shakeX, shakeY, shakeZ);
    }
    
    /// <summary>
    /// Example: Wind effect on objects using trigonometry
    /// Shows how to create realistic wind effects with varying force
    /// </summary>
    public Vector3 CalculateWindForce(Vector3 windDirection, float windStrength, float gustiness, float time)
    {
        // Base wind force
        Vector3 baseWind = windDirection.normalized * windStrength;
        
        // Add gustiness using multiple sine waves
        float gustFactor = 1f + gustiness * (
            TrigonometryPhysicsUtility.SineWave(time, 0.3f, 0.5f) +
            TrigonometryPhysicsUtility.SineWave(time, 0.2f, 1.2f, Mathf.PI * 0.3f) +
            TrigonometryPhysicsUtility.SineWave(time, 0.1f, 2.1f, Mathf.PI * 0.7f)
        );
        
        return baseWind * gustFactor;
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Physics Simulation Enhancement
- **Realistic Motion**: AI-generated physics parameters for natural-looking movement patterns
- **Wave Synthesis**: Machine learning-based wave pattern generation for complex oscillations
- **Trajectory Optimization**: AI-powered ballistic calculations for intelligent targeting systems

### Game Mechanics Development
- **Procedural Animation**: AI-assisted trigonometric animation systems for character movement
- **Environmental Effects**: Machine learning-based weather and atmospheric simulation
- **Audio Synthesis**: AI-powered sound generation using trigonometric wave functions

### Educational Applications
- **Interactive Visualization**: AI-generated visual explanations of trigonometric concepts
- **Problem Generation**: Automated physics problem creation with varying difficulty levels
- **Performance Analysis**: AI analysis of physics simulation performance and optimization

## 💡 Key Highlights

- **Master the TRIG Framework** for systematic approach to trigonometry in game physics
- **Understand Circular Motion** using sine and cosine functions for orbital and rotational systems
- **Implement Wave Physics** with oscillation, damping, and complex wave pattern generation
- **Apply Projectile Calculations** for realistic ballistic trajectories and targeting systems
- **Create Advanced Motion Patterns** using Lissajous curves, cycloids, and complex mathematical functions
- **Optimize Physics Performance** through efficient trigonometric calculations and caching strategies
- **Visualize Mathematical Concepts** using debug gizmos and real-time animation systems
- **Focus on Practical Implementation** solving real game development challenges using trigonometry