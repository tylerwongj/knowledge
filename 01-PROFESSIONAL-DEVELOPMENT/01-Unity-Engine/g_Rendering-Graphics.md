# g_Rendering-Graphics - Unity Rendering Pipeline & Graphics

## 🎯 Learning Objectives
- Master Unity's rendering pipelines (Built-in, URP, HDRP)
- Understand shaders, materials, and lighting systems
- Optimize graphics performance for different platforms
- Implement advanced visual effects and post-processing

## 🔧 Core Rendering Concepts

### Rendering Pipelines
```csharp
// Built-in Render Pipeline (Legacy)
// - Forward rendering
// - Deferred rendering
// - Legacy lighting model

// Universal Render Pipeline (URP)
// - Scriptable render pipeline
// - Mobile-optimized
// - Cross-platform compatibility

// High Definition Render Pipeline (HDRP)
// - High-end graphics
// - Advanced lighting
// - Ray tracing support
```

### Materials and Shaders
```csharp
// Material property access
public class MaterialController : MonoBehaviour
{
    private Material material;
    
    void Start()
    {
        material = GetComponent<Renderer>().material;
        
        // Modify material properties
        material.SetFloat("_Metallic", 0.5f);
        material.SetColor("_Color", Color.red);
        material.SetTexture("_MainTex", newTexture);
    }
    
    // Animate material properties
    void Update()
    {
        float emission = Mathf.Sin(Time.time) * 0.5f + 0.5f;
        material.SetFloat("_EmissionIntensity", emission);
    }
}
```

### Lighting Systems
```csharp
// Dynamic lighting control
public class LightingManager : MonoBehaviour
{
    public Light directionalLight;
    public AnimationCurve lightIntensityCurve;
    
    [Range(0f, 24f)]
    public float timeOfDay = 12f;
    
    void Update()
    {
        // Day/night cycle
        float normalizedTime = timeOfDay / 24f;
        
        // Rotate sun
        float sunAngle = normalizedTime * 360f - 90f;
        directionalLight.transform.rotation = Quaternion.Euler(sunAngle, 0, 0);
        
        // Adjust intensity
        directionalLight.intensity = lightIntensityCurve.Evaluate(normalizedTime);
        
        // Color temperature
        directionalLight.color = Color.Lerp(Color.red, Color.white, 
            Mathf.Clamp01((normalizedTime - 0.25f) * 2f));
    }
}
```

### Performance Optimization
```csharp
// LOD (Level of Detail) System
public class LODController : MonoBehaviour
{
    public GameObject[] lodLevels;
    public float[] lodDistances = {50f, 100f, 200f};
    
    private Camera playerCamera;
    
    void Start()
    {
        playerCamera = Camera.main;
    }
    
    void Update()
    {
        float distance = Vector3.Distance(transform.position, playerCamera.transform.position);
        
        // Activate appropriate LOD level
        for (int i = 0; i < lodLevels.Length; i++)
        {
            bool shouldActivate = (i == 0 && distance < lodDistances[0]) ||
                                (i > 0 && distance >= lodDistances[i-1] && distance < lodDistances[i]);
            
            lodLevels[i].SetActive(shouldActivate);
        }
    }
}

// Occlusion Culling Helper
public class OcclusionCullingManager : MonoBehaviour
{
    void Start()
    {
        // Enable occlusion culling
        Camera.main.useOcclusionCulling = true;
        
        // Bake occlusion culling data in editor
        #if UNITY_EDITOR
        UnityEditor.StaticOcclusionCulling.Compute();
        #endif
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Shader Development Assistance
```
Prompt: "Create a Unity shader for [effect description]. Include vertex and fragment shader code with explanations of each pass and property."

Example: "Create a Unity shader for a holographic effect with animated scanlines, color shifting, and transparency based on viewing angle."
```

### Performance Optimization Analysis
```
Prompt: "Analyze this Unity rendering setup and suggest performance optimizations: [paste code/setup]. Focus on draw calls, batching, and LOD systems."
```

### Visual Effect Creation
```
Prompt: "Generate Unity C# scripts for creating [visual effect] using particle systems, shaders, and post-processing. Include performance considerations."
```

## 🔧 Advanced Graphics Techniques

### Post-Processing Stack
```csharp
// Custom post-processing effect
using UnityEngine;
using UnityEngine.Rendering.PostProcessing;

[System.Serializable]
[PostProcess(typeof(CustomEffectRenderer), PostProcessEvent.AfterStack, "Custom/MyEffect")]
public sealed class CustomEffect : PostProcessEffectSettings
{
    [Range(0f, 1f), Tooltip("Effect intensity")]
    public FloatParameter intensity = new FloatParameter { value = 0.5f };
    
    [ColorUsage(false, true, 0f, 8f, 0.125f, 3f)]
    public ColorParameter color = new ColorParameter { value = Color.white };
}

public sealed class CustomEffectRenderer : PostProcessEffectRenderer<CustomEffect>
{
    public override void Render(PostProcessRenderContext context)
    {
        var sheet = context.propertySheets.Get(Shader.Find("Custom/PostProcessEffect"));
        sheet.properties.SetFloat("_Intensity", settings.intensity);
        sheet.properties.SetColor("_Color", settings.color);
        
        context.command.BlitFullscreenTriangle(context.source, context.destination, sheet, 0);
    }
}
```

### Texture Streaming
```csharp
// Texture streaming optimization
public class TextureStreamingManager : MonoBehaviour
{
    void Start()
    {
        // Configure texture streaming
        QualitySettings.streamingMipmapsActive = true;
        QualitySettings.streamingMipmapsMemoryBudget = 512; // MB
        QualitySettings.streamingMipmapsMaxLevelReduction = 2;
        
        // Set texture streaming for specific textures
        var renderer = GetComponent<Renderer>();
        if (renderer.material.mainTexture is Texture2D tex)
        {
            tex.requestedMipmapLevel = 0; // Highest quality
        }
    }
}
```

### Reflection Probes
```csharp
// Dynamic reflection probe management
public class ReflectionProbeManager : MonoBehaviour
{
    public ReflectionProbe[] probes;
    public float updateInterval = 1f;
    
    private float lastUpdate;
    
    void Update()
    {
        if (Time.time - lastUpdate > updateInterval)
        {
            UpdateNearestProbe();
            lastUpdate = Time.time;
        }
    }
    
    void UpdateNearestProbe()
    {
        Vector3 playerPos = Camera.main.transform.position;
        ReflectionProbe nearest = null;
        float nearestDistance = float.MaxValue;
        
        foreach (var probe in probes)
        {
            float distance = Vector3.Distance(probe.transform.position, playerPos);
            if (distance < nearestDistance)
            {
                nearest = probe;
                nearestDistance = distance;
            }
        }
        
        if (nearest != null)
        {
            nearest.RenderProbe();
        }
    }
}
```

## 💡 Key Highlights

### Essential Graphics Concepts
- **Rendering Pipeline**: Choose URP for most projects, HDRP for high-end graphics
- **Draw Calls**: Minimize by using batching, atlasing, and LOD systems
- **Lighting**: Use baked lighting for static objects, dynamic for moving elements
- **Shaders**: Learn ShaderGraph for visual shader creation, HLSL for advanced effects

### Performance Best Practices
- **Texture Compression**: Use appropriate formats (DXT, ETC, ASTC)
- **Mesh Optimization**: Reduce polygon count, use LOD groups
- **Occlusion Culling**: Bake occlusion data for complex scenes
- **Batching**: Static batching for non-moving objects, dynamic for moving ones

### Mobile Optimization
- **Overdraw**: Minimize transparent objects and overlapping geometry
- **Texture Memory**: Use texture streaming and compression
- **Shader Complexity**: Avoid complex fragment shaders on mobile
- **Frame Rate**: Target 30 FPS for mobile, 60 FPS for desktop/console

### Debugging Tools
- **Frame Debugger**: Analyze draw calls and rendering steps
- **Profiler**: Monitor GPU usage and render thread performance
- **Graphics Settings**: Test different quality levels and platforms
- **Scene View**: Use rendering mode overlays to visualize issues