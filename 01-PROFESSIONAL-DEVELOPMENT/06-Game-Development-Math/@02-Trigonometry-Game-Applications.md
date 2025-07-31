# @02-Trigonometry Game Applications

## 🎯 Learning Objectives
- Master trigonometric functions for Unity game development
- Apply sine, cosine, and tangent to create smooth animations and movement
- Leverage AI tools for complex trigonometric calculations and optimizations
- Build intuitive understanding of circular and wave-based motion in games

## 📊 Trigonometry Fundamentals in Unity

### Core Trigonometric Functions
**Unity's Mathf Class**:
```csharp
// Unity uses radians for trigonometric functions
float angleInRadians = angleInDegrees * Mathf.Deg2Rad;
float angleInDegrees = angleInRadians * Mathf.Rad2Deg;

// Basic trigonometric functions
float sine = Mathf.Sin(angleInRadians);
float cosine = Mathf.Cos(angleInRadians);
float tangent = Mathf.Tan(angleInRadians);

// Inverse functions
float arcSine = Mathf.Asin(value);      // Returns radians
float arcCosine = Mathf.Acos(value);    // Returns radians
float arcTangent = Mathf.Atan2(y, x);   // Returns angle from origin to point (x,y)
```

**Unit Circle Applications**:
```csharp
// Create circular motion using sine and cosine
public class CircularMotion : MonoBehaviour 
{
    public float radius = 5f;
    public float speed = 2f;
    
    private float angle = 0f;
    private Vector3 centerPosition;
    
    void Start() 
    {
        centerPosition = transform.position;
    }
    
    void Update() 
    {
        angle += speed * Time.deltaTime;
        
        float x = centerPosition.x + radius * Mathf.Cos(angle);
        float z = centerPosition.z + radius * Mathf.Sin(angle);
        
        transform.position = new Vector3(x, centerPosition.y, z);
    }
}
```

### Wave Functions and Oscillation
**Sine Wave Applications**:
```csharp
public class WaveMotion : MonoBehaviour 
{
    [Header("Wave Parameters")]
    public float amplitude = 2f;      // Height of wave
    public float frequency = 1f;      // Speed of oscillation
    public float phase = 0f;          // Starting offset
    
    private Vector3 startPosition;
    
    void Start() 
    {
        startPosition = transform.position;
    }
    
    void Update() 
    {
        float wave = amplitude * Mathf.Sin(frequency * Time.time + phase);
        transform.position = startPosition + Vector3.up * wave;
    }
}
```

## 🎮 Movement and Animation Applications

### Smooth Character Movement
**Sine-Based Acceleration Curves**:
```csharp
public class SmoothMovement : MonoBehaviour 
{
    public Transform target;
    public float duration = 2f;
    
    private Vector3 startPosition;
    private float elapsedTime = 0f;
    
    void Start() 
    {
        startPosition = transform.position;
    }
    
    void Update() 
    {
        elapsedTime += Time.deltaTime;
        float progress = elapsedTime / duration;
        
        // Smooth acceleration using sine curve
        float smoothProgress = Mathf.Sin(progress * Mathf.PI * 0.5f);
        
        transform.position = Vector3.Lerp(startPosition, target.position, smoothProgress);
    }
}
```

**Bobbing and Floating Animations**:
```csharp
public class FloatingAnimation : MonoBehaviour 
{
    [Header("Float Settings")]
    public float floatAmplitude = 0.5f;
    public float floatFrequency = 1f;
    
    [Header("Rotation Settings")]
    public float rotationSpeed = 30f;
    
    private Vector3 startPosition;
    
    void Start() 
    {
        startPosition = transform.position;
    }
    
    void Update() 
    {
        // Vertical floating motion
        float newY = startPosition.y + Mathf.Sin(Time.time * floatFrequency) * floatAmplitude;
        transform.position = new Vector3(startPosition.x, newY, startPosition.z);
        
        // Gentle rotation
        transform.Rotate(Vector3.up, rotationSpeed * Time.deltaTime);
    }
}
```

### Camera Systems and Look-At Mechanics
**Smooth Camera Following with Trigonometry**:
```csharp
public class TrigonometricCamera : MonoBehaviour 
{
    public Transform target;
    public float distance = 10f;
    public float height = 5f;
    public float rotationSpeed = 2f;
    
    private float currentAngle = 0f;
    
    void LateUpdate() 
    {
        currentAngle += rotationSpeed * Time.deltaTime;
        
        float x = target.position.x + distance * Mathf.Cos(currentAngle);
        float z = target.position.z + distance * Mathf.Sin(currentAngle);
        float y = target.position.y + height;
        
        transform.position = new Vector3(x, y, z);
        transform.LookAt(target);
    }
}
```

## 🎯 Gameplay Mechanics Using Trigonometry

### Projectile Systems and Ballistics
**Parabolic Trajectory Calculation**:
```csharp
public class ProjectileLauncher : MonoBehaviour 
{
    public float launchForce = 10f;
    public float gravity = -9.8f;
    
    public Vector3 CalculateTrajectory(Vector3 target, float timeToTarget) 
    {
        Vector3 direction = target - transform.position;
        Vector3 directionXZ = new Vector3(direction.x, 0, direction.z);
        
        float horizontalDistance = directionXZ.magnitude;
        float verticalDistance = direction.y;
        
        // Calculate launch angle using trigonometry
        float velocityY = (verticalDistance / timeToTarget) + (0.5f * Mathf.Abs(gravity) * timeToTarget);
        float velocityXZ = horizontalDistance / timeToTarget;
        
        Vector3 velocity = directionXZ.normalized * velocityXZ;
        velocity.y = velocityY;
        
        return velocity;
    }
    
    public void LaunchProjectile(Vector3 target) 
    {
        GameObject projectile = Instantiate(projectilePrefab, transform.position, Quaternion.identity);
        Rigidbody rb = projectile.GetComponent<Rigidbody>();
        
        Vector3 launchVelocity = CalculateTrajectory(target, 2f);
        rb.velocity = launchVelocity;
    }
}
```

### Field of View and Detection Systems
**Cone-Based Detection Using Trigonometry**:
```csharp
public class FieldOfView : MonoBehaviour 
{
    [Header("FOV Settings")]
    public float viewRadius = 10f;
    public float viewAngle = 90f;
    
    [Header("Detection")]
    public LayerMask targetMask;
    public LayerMask obstacleMask;
    
    public List<Transform> visibleTargets = new List<Transform>();
    
    void Update() 
    {
        FindVisibleTargets();
    }
    
    void FindVisibleTargets() 
    {
        visibleTargets.Clear();
        Collider[] targetsInViewRadius = Physics.OverlapSphere(transform.position, viewRadius, targetMask);
        
        foreach (Collider target in targetsInViewRadius) 
        {
            Vector3 directionToTarget = (target.transform.position - transform.position).normalized;
            
            // Use dot product and trigonometry to check if target is within view angle
            float angleBetween = Vector3.Angle(transform.forward, directionToTarget);
            
            if (angleBetween < viewAngle / 2) 
            {
                float distanceToTarget = Vector3.Distance(transform.position, target.transform.position);
                
                // Raycast to check for obstacles
                if (!Physics.Raycast(transform.position, directionToTarget, distanceToTarget, obstacleMask)) 
                {
                    visibleTargets.Add(target.transform);
                }
            }
        }
    }
    
    public Vector3 DirectionFromAngle(float angleInDegrees, bool angleIsGlobal) 
    {
        if (!angleIsGlobal) 
        {
            angleInDegrees += transform.eulerAngles.y;
        }
        
        float radians = angleInDegrees * Mathf.Deg2Rad;
        return new Vector3(Mathf.Sin(radians), 0, Mathf.Cos(radians));
    }
}
```

## 🌊 Advanced Trigonometric Applications

### Procedural Animation Systems
**Complex Wave Combinations**:
```csharp
public class ProceduralWaves : MonoBehaviour 
{
    [System.Serializable]
    public class WaveFunction 
    {
        public float amplitude = 1f;
        public float frequency = 1f;
        public float phase = 0f;
        public Vector3 direction = Vector3.up;
    }
    
    public WaveFunction[] waves;
    private Vector3 originalPosition;
    
    void Start() 
    {
        originalPosition = transform.position;
    }
    
    void Update() 
    {
        Vector3 combinedWave = Vector3.zero;
        
        foreach (WaveFunction wave in waves) 
        {
            float waveValue = wave.amplitude * Mathf.Sin(wave.frequency * Time.time + wave.phase);
            combinedWave += wave.direction * waveValue;
        }
        
        transform.position = originalPosition + combinedWave;
    }
}
```

### Shader and Visual Effects Integration
**Trigonometry in Vertex Shaders**:
```csharp
// Script to pass wave parameters to shaders
public class WaveShaderController : MonoBehaviour 
{
    public Material waveMaterial;
    
    [Header("Wave Parameters")]
    public float waveSpeed = 1f;
    public float waveAmplitude = 0.1f;
    public float waveFrequency = 10f;
    
    void Update() 
    {
        if (waveMaterial != null) 
        {
            waveMaterial.SetFloat("_Time", Time.time * waveSpeed);
            waveMaterial.SetFloat("_Amplitude", waveAmplitude);
            waveMaterial.SetFloat("_Frequency", waveFrequency);
        }
    }
}
```

## 🚀 AI-Enhanced Trigonometric Development

### Automated Pattern Generation
**AI-Assisted Wave Function Creation**:
```csharp
public class AIWaveGenerator : MonoBehaviour 
{
    // AI can generate complex wave combinations for specific effects
    public static WaveFunction[] GenerateHarmonicSeries(int harmonics, float baseFrequency) 
    {
        WaveFunction[] waves = new WaveFunction[harmonics];
        
        for (int i = 0; i < harmonics; i++) 
        {
            waves[i] = new WaveFunction 
            {
                frequency = baseFrequency * (i + 1),
                amplitude = 1f / (i + 1), // Decreasing amplitude for higher harmonics
                phase = UnityEngine.Random.Range(0f, 2f * Mathf.PI)
            };
        }
        
        return waves;
    }
}
```

### Performance Optimization
**Lookup Tables and Caching**:
```csharp
public static class TrigonometryCache 
{
    private static readonly Dictionary<float, float> sineCache = new Dictionary<float, float>();
    private static readonly Dictionary<float, float> cosineCache = new Dictionary<float, float>();
    
    public static float FastSin(float angle) 
    {
        // Round to nearest degree for caching
        float rounded = Mathf.Round(angle * Mathf.Rad2Deg);
        
        if (!sineCache.ContainsKey(rounded)) 
        {
            sineCache[rounded] = Mathf.Sin(rounded * Mathf.Deg2Rad);
        }
        
        return sineCache[rounded];
    }
    
    public static float FastCos(float angle) 
    {
        float rounded = Mathf.Round(angle * Mathf.Rad2Deg);
        
        if (!cosineCache.ContainsKey(rounded)) 
        {
            cosineCache[rounded] = Mathf.Cos(rounded * Mathf.Deg2Rad);
        }
        
        return cosineCache[rounded];
    }
}
```

## 🎪 Creative Applications and Special Effects

### Particle Systems and Effects
**Trigonometric Particle Patterns**:
```csharp
public class TrigonometricParticles : MonoBehaviour 
{
    public ParticleSystem particles;
    
    void Start() 
    {
        CreateSpiralPattern();
    }
    
    void CreateSpiralPattern() 
    {
        ParticleSystem.EmissionModule emission = particles.emission;
        emission.enabled = false;
        
        for (int i = 0; i < 100; i++) 
        {
            float angle = i * 0.1f;
            float radius = angle * 0.5f;
            
            Vector3 position = new Vector3(
                radius * Mathf.Cos(angle),
                i * 0.1f,
                radius * Mathf.Sin(angle)
            );
            
            ParticleSystem.EmitParams emitParams = new ParticleSystem.EmitParams();
            emitParams.position = position;
            particles.Emit(emitParams, 1);
        }
    }
}
```

### Audio Visualization
**Music-Reactive Trigonometric Effects**:
```csharp
public class AudioVisualization : MonoBehaviour 
{
    public AudioSource audioSource;
    public Transform[] visualizerBars;
    
    private float[] spectrumData = new float[64];
    
    void Update() 
    {
        audioSource.GetSpectrumData(spectrumData, 0, FFTWindow.BlackmanHarris);
        
        for (int i = 0; i < visualizerBars.Length && i < spectrumData.Length; i++) 
        {
            float intensity = spectrumData[i] * 100f;
            
            // Create wave-like motion based on audio intensity
            float wave = intensity * Mathf.Sin(Time.time * 5f + i * 0.5f);
            Vector3 scale = new Vector3(1f, 1f + wave, 1f);
            
            visualizerBars[i].localScale = scale;
        }
    }
}
```

## 💡 Learning and Mastery Strategies

### Progressive Complexity
1. **Basic Functions**: Start with simple sine/cosine animations
2. **Combined Motions**: Combine multiple trigonometric functions
3. **Gameplay Integration**: Apply to game mechanics and systems
4. **Performance Optimization**: Implement caching and approximations
5. **Creative Applications**: Explore artistic and visual effects

### AI-Enhanced Learning
- Generate practice problems with increasing complexity
- Create interactive visualizations of trigonometric concepts
- Automate code optimization for trigonometric calculations
- Build debugging tools for wave-based animations

### Real-World Applications
- Study how AAA games use trigonometry for smooth animations
- Analyze particle effects and their mathematical foundations
- Experiment with procedural content generation using waves
- Create portfolio projects showcasing mathematical mastery

Trigonometry provides the mathematical foundation for creating smooth, natural-looking animations and movements that enhance the player experience in Unity games.