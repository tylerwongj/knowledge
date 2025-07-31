# f_Trigonometry-Game-Applications

## 🎯 Learning Objectives
- Master trigonometric functions for game development scenarios
- Apply sine, cosine, and tangent to movement, rotation, and animation
- Implement circular motion, wave patterns, and oscillations
- Create smooth interpolation and easing functions using trigonometry

## 🔧 Core Trigonometric Concepts

### Basic Trigonometric Functions
```csharp
// Unity coordinate system considerations
public class TrigonometryHelper : MonoBehaviour
{
    public static float Sin(float angle) => Mathf.Sin(angle * Mathf.Deg2Rad);
    public static float Cos(float angle) => Mathf.Cos(angle * Mathf.Deg2Rad);
    public static float Tan(float angle) => Mathf.Tan(angle * Mathf.Deg2Rad);
    
    // Inverse functions
    public static float Asin(float value) => Mathf.Asin(value) * Mathf.Rad2Deg;
    public static float Acos(float value) => Mathf.Acos(value) * Mathf.Rad2Deg;
    public static float Atan2(float y, float x) => Mathf.Atan2(y, x) * Mathf.Rad2Deg;
}
```

### Circular Motion and Orbital Mechanics
```csharp
public class CircularMotion : MonoBehaviour
{
    [Header("Orbit Parameters")]
    public float radius = 5f;
    public float angularSpeed = 90f; // degrees per second
    public Transform centerPoint;
    
    private float currentAngle = 0f;
    
    void Update()
    {
        // Update angle based on time
        currentAngle += angularSpeed * Time.deltaTime;
        
        // Calculate position using trigonometry
        float x = centerPoint.position.x + radius * Mathf.Cos(currentAngle * Mathf.Deg2Rad);
        float z = centerPoint.position.z + radius * Mathf.Sin(currentAngle * Mathf.Deg2Rad);
        
        transform.position = new Vector3(x, transform.position.y, z);
        
        // Optional: Look at center while orbiting
        transform.LookAt(centerPoint);
    }
}
```

### Wave Functions and Oscillations
```csharp
public class WaveMotion : MonoBehaviour
{
    [Header("Wave Parameters")]
    public float amplitude = 2f;
    public float frequency = 1f;
    public float phase = 0f;
    public Vector3 direction = Vector3.up;
    
    private Vector3 startPosition;
    
    void Start()
    {
        startPosition = transform.position;
    }
    
    void Update()
    {
        float time = Time.time;
        float waveValue = amplitude * Mathf.Sin(2 * Mathf.PI * frequency * time + phase);
        
        transform.position = startPosition + direction.normalized * waveValue;
    }
}

// Advanced wave combinations
public class ComplexWave : MonoBehaviour
{
    [System.Serializable]
    public class WaveComponent
    {
        public float amplitude = 1f;
        public float frequency = 1f;
        public float phase = 0f;
        public Vector3 direction = Vector3.up;
    }
    
    public WaveComponent[] waves;
    private Vector3 startPosition;
    
    void Start()
    {
        startPosition = transform.position;
    }
    
    void Update()
    {
        Vector3 displacement = Vector3.zero;
        float time = Time.time;
        
        foreach (var wave in waves)
        {
            float waveValue = wave.amplitude * Mathf.Sin(2 * Mathf.PI * wave.frequency * time + wave.phase);
            displacement += wave.direction.normalized * waveValue;
        }
        
        transform.position = startPosition + displacement;
    }
}
```

## 🔧 Practical Game Applications

### Enemy AI Patrol Patterns
```csharp
public class PatrolAI : MonoBehaviour
{
    [Header("Patrol Settings")]
    public Transform[] waypoints;
    public float patrolSpeed = 3f;
    public float waitTime = 2f;
    public AnimationCurve speedCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);
    
    private int currentWaypoint = 0;
    private float journeyProgress = 0f;
    private bool isWaiting = false;
    
    void Update()
    {
        if (waypoints.Length < 2) return;
        
        if (!isWaiting)
        {
            MoveToWaypoint();
        }
    }
    
    void MoveToWaypoint()
    {
        Transform target = waypoints[currentWaypoint];
        float distance = Vector3.Distance(transform.position, target.position);
        
        // Smooth acceleration/deceleration using trigonometry
        float smoothSpeed = patrolSpeed * speedCurve.Evaluate(1f - (distance / 10f));
        
        transform.position = Vector3.MoveTowards(transform.position, target.position, smoothSpeed * Time.deltaTime);
        
        if (Vector3.Distance(transform.position, target.position) < 0.1f)
        {
            StartCoroutine(WaitAtWaypoint());
        }
    }
    
    IEnumerator WaitAtWaypoint()
    {
        isWaiting = true;
        yield return new WaitForSeconds(waitTime);
        currentWaypoint = (currentWaypoint + 1) % waypoints.Length;
        isWaiting = false;
    }
}
```

### Smooth Look-At and Rotation
```csharp
public class SmoothLookAt : MonoBehaviour
{
    [Header("Look At Settings")]
    public Transform target;
    public float rotationSpeed = 90f;
    public bool useSmoothing = true;
    public AnimationCurve smoothingCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);
    
    void Update()
    {
        if (target == null) return;
        
        Vector3 direction = (target.position - transform.position).normalized;
        float targetAngle = Mathf.Atan2(direction.x, direction.z) * Mathf.Rad2Deg;
        
        if (useSmoothing)
        {
            float currentAngle = transform.eulerAngles.y;
            float angleDifference = Mathf.DeltaAngle(currentAngle, targetAngle);
            
            // Smooth rotation using trigonometry
            float rotationAmount = rotationSpeed * Time.deltaTime;
            float smoothedRotation = rotationAmount * smoothingCurve.Evaluate(Mathf.Abs(angleDifference) / 180f);
            
            float newAngle = Mathf.MoveTowardsAngle(currentAngle, targetAngle, smoothedRotation);
            transform.rotation = Quaternion.Euler(0, newAngle, 0);
        }
        else
        {
            transform.rotation = Quaternion.Euler(0, targetAngle, 0);
        }
    }
}
```

### Procedural Animation and Easing
```csharp
public class ProceduralAnimation : MonoBehaviour
{
    [Header("Animation Parameters")]
    public float duration = 2f;
    public Vector3 targetPosition;
    public Vector3 targetRotation;
    public AnimationCurve easingCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);
    
    private Vector3 startPosition;
    private Vector3 startRotation;
    private float animationTime = 0f;
    private bool isAnimating = false;
    
    public void StartAnimation()
    {
        startPosition = transform.position;
        startRotation = transform.eulerAngles;
        animationTime = 0f;
        isAnimating = true;
    }
    
    void Update()
    {
        if (!isAnimating) return;
        
        animationTime += Time.deltaTime;
        float progress = animationTime / duration;
        
        if (progress >= 1f)
        {
            progress = 1f;
            isAnimating = false;
        }
        
        // Apply easing using trigonometric functions
        float easedProgress = easingCurve.Evaluate(progress);
        
        // Smooth position interpolation
        transform.position = Vector3.Lerp(startPosition, targetPosition, easedProgress);
        
        // Smooth rotation interpolation
        Vector3 currentRotation = Vector3.Lerp(startRotation, targetRotation, easedProgress);
        transform.rotation = Quaternion.Euler(currentRotation);
    }
    
    // Custom easing functions using trigonometry
    public static class EasingFunctions
    {
        public static float EaseInSine(float t) => 1f - Mathf.Cos(t * Mathf.PI / 2f);
        public static float EaseOutSine(float t) => Mathf.Sin(t * Mathf.PI / 2f);
        public static float EaseInOutSine(float t) => -(Mathf.Cos(Mathf.PI * t) - 1f) / 2f;
        
        public static float EaseInCirc(float t) => 1f - Mathf.Sqrt(1f - t * t);
        public static float EaseOutCirc(float t) => Mathf.Sqrt(1f - (t - 1f) * (t - 1f));
    }
}
```

## 🔧 Advanced Applications

### Noise-Based Procedural Generation
```csharp
public class ProceduralTerrain : MonoBehaviour
{
    [Header("Terrain Parameters")]
    public int width = 100;
    public int height = 100;
    public float scale = 20f;
    public float heightMultiplier = 5f;
    public AnimationCurve heightCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);
    
    void Start()
    {
        GenerateTerrain();
    }
    
    void GenerateTerrain()
    {
        Terrain terrain = GetComponent<Terrain>();
        TerrainData terrainData = terrain.terrainData;
        
        terrainData.heightmapResolution = width + 1;
        terrainData.size = new Vector3(width, heightMultiplier, height);
        
        float[,] heights = new float[width + 1, height + 1];
        
        for (int x = 0; x <= width; x++)
        {
            for (int y = 0; y <= height; y++)
            {
                float xCoord = (float)x / width * scale;
                float yCoord = (float)y / height * scale;
                
                // Combine multiple octaves of noise using trigonometry
                float noise = 0f;
                float amplitude = 1f;
                float frequency = 1f;
                
                for (int octave = 0; octave < 4; octave++)
                {
                    noise += Mathf.PerlinNoise(xCoord * frequency, yCoord * frequency) * amplitude;
                    amplitude *= 0.5f;
                    frequency *= 2f;
                }
                
                // Apply height curve for more natural terrain
                heights[x, y] = heightCurve.Evaluate(noise);
            }
        }
        
        terrainData.SetHeights(0, 0, heights);
    }
}
```

### Field of View and Line of Sight
```csharp
public class FieldOfView : MonoBehaviour
{
    [Header("FOV Settings")]
    public float viewRadius = 10f;
    public float viewAngle = 90f;
    public LayerMask targetMask;
    public LayerMask obstacleMask;
    
    public List<Transform> visibleTargets = new List<Transform>();
    
    void Start()
    {
        StartCoroutine(FindTargetsWithDelay(0.2f));
    }
    
    IEnumerator FindTargetsWithDelay(float delay)
    {
        while (true)
        {
            yield return new WaitForSeconds(delay);
            FindVisibleTargets();
        }
    }
    
    void FindVisibleTargets()
    {
        visibleTargets.Clear();
        Collider[] targetsInViewRadius = Physics.OverlapSphere(transform.position, viewRadius, targetMask);
        
        foreach (Collider target in targetsInViewRadius)
        {
            Vector3 dirToTarget = (target.transform.position - transform.position).normalized;
            
            // Use dot product to check if target is within view angle
            if (Vector3.Angle(transform.forward, dirToTarget) < viewAngle / 2)
            {
                float distToTarget = Vector3.Distance(transform.position, target.transform.position);
                
                // Raycast to check for obstacles
                if (!Physics.Raycast(transform.position, dirToTarget, distToTarget, obstacleMask))
                {
                    visibleTargets.Add(target.transform);
                }
            }
        }
    }
    
    public Vector3 DirFromAngle(float angleInDegrees, bool angleIsGlobal)
    {
        if (!angleIsGlobal)
        {
            angleInDegrees += transform.eulerAngles.y;
        }
        
        return new Vector3(Mathf.Sin(angleInDegrees * Mathf.Deg2Rad), 0, Mathf.Cos(angleInDegrees * Mathf.Deg2Rad));
    }
    
    void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.white;
        Gizmos.DrawWireSphere(transform.position, viewRadius);
        
        Vector3 viewAngleA = DirFromAngle(-viewAngle / 2, false);
        Vector3 viewAngleB = DirFromAngle(viewAngle / 2, false);
        
        Gizmos.color = Color.yellow;
        Gizmos.DrawLine(transform.position, transform.position + viewAngleA * viewRadius);
        Gizmos.DrawLine(transform.position, transform.position + viewAngleB * viewRadius);
        
        Gizmos.color = Color.red;
        foreach (Transform visibleTarget in visibleTargets)
        {
            Gizmos.DrawLine(transform.position, visibleTarget.position);
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Content Generation Prompts
```
"Generate Unity C# code for [specific trigonometric application] with the following requirements: [requirements]. Include comments explaining the mathematical concepts and provide parameter customization options."

"Create a trigonometry-based shader effect for [visual effect description] that uses sine and cosine functions for [specific behavior]. Explain the mathematical principles behind the effect."

"Design a procedural animation system using trigonometric functions for [animation type]. Include easing functions and parameter controls for fine-tuning."
```

### Learning Acceleration
- **Concept Explanation**: "Explain how [trigonometric concept] applies to [game development scenario] with visual examples"
- **Code Optimization**: "Optimize this trigonometry-heavy code for better performance while maintaining accuracy"
- **Problem Solving**: "I need to create [specific game mechanic] using trigonometry. What's the best mathematical approach?"

### Advanced Applications
- **Shader Programming**: Combining trigonometry with GPU programming for visual effects
- **Physics Simulation**: Using trigonometric functions for realistic physics behaviors
- **Procedural Content**: Mathematical functions for generating game worlds and content

## 💡 Key Highlights

### Essential Formulas for Game Development
- **Circular Motion**: `x = centerX + radius * cos(angle)`, `y = centerY + radius * sin(angle)`
- **Wave Functions**: `y = amplitude * sin(2π * frequency * time + phase)`
- **Distance Calculation**: `distance = sqrt((x2-x1)² + (y2-y1)²)`
- **Angle Between Vectors**: `angle = acos(dot(v1, v2) / (|v1| * |v2|))`

### Performance Considerations
- **Use `Mathf.Sin/Cos` tables** for frequently called trigonometric functions
- **Cache calculations** when possible, especially in Update() loops
- **Consider approximation functions** for less critical calculations
- **Use `Vector3.Angle()` instead of manual calculations** when appropriate

### Common Unity-Specific Applications
- **Camera orbiting** around objects or characters
- **Procedural animation** for UI elements and environmental objects
- **Enemy AI patterns** with smooth, predictable movement
- **Visual effects** with wave-based animations and oscillations
- **Terrain generation** using noise functions and height curves

### Integration with Other Systems
- **Physics**: Combining trigonometry with Rigidbody for realistic motion
- **Animation**: Blending procedural and keyframe animation systems
- **Audio**: Synchronizing visual effects with audio waveforms
- **Networking**: Predicting movement patterns for multiplayer games

This comprehensive understanding of trigonometry in game development provides the mathematical foundation for creating smooth, natural, and visually appealing game mechanics and effects.