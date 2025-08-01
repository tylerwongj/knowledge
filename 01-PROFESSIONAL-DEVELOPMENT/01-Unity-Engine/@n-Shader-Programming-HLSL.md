# @n-Shader-Programming-HLSL - Unity Shader Development Mastery

## 🎯 Learning Objectives
- Master HLSL shader programming for Unity applications
- Implement custom visual effects and rendering techniques
- Optimize shader performance for different platforms
- Create reusable shader libraries and tools

## 🔧 HLSL Fundamentals in Unity

### Shader Structure and Syntax
```hlsl
Shader "Custom/MyShader"
{
    Properties
    {
        _MainTex ("Texture", 2D) = "white" {}
        _Color ("Color", Color) = (1,1,1,1)
        _Metallic ("Metallic", Range(0,1)) = 0.0
        _Smoothness ("Smoothness", Range(0,1)) = 0.5
    }
    
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        LOD 200
        
        CGPROGRAM
        #pragma surface surf Standard fullforwardshadows
        #pragma target 3.0
        
        sampler2D _MainTex;
        fixed4 _Color;
        half _Metallic;
        half _Smoothness;
        
        struct Input
        {
            float2 uv_MainTex;
        };
        
        void surf (Input IN, inout SurfaceOutputStandard o)
        {
            fixed4 c = tex2D (_MainTex, IN.uv_MainTex) * _Color;
            o.Albedo = c.rgb;
            o.Metallic = _Metallic;
            o.Smoothness = _Smoothness;
            o.Alpha = c.a;
        }
        ENDCG
    }
}
```

### Advanced Vertex and Fragment Shaders
```hlsl
Shader "Custom/Advanced"
{
    Properties
    {
        _MainTex ("Texture", 2D) = "white" {}
        _DisplacementMap ("Displacement", 2D) = "black" {}
        _DisplacementStrength ("Displacement Strength", Float) = 1.0
    }
    
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            
            struct appdata
            {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
                float3 normal : NORMAL;
            };
            
            struct v2f
            {
                float2 uv : TEXCOORD0;
                float4 vertex : SV_POSITION;
                float3 worldNormal : TEXCOORD1;
                float3 worldPos : TEXCOORD2;
            };
            
            sampler2D _MainTex;
            sampler2D _DisplacementMap;
            float _DisplacementStrength;
            
            v2f vert (appdata v)
            {
                v2f o;
                
                // Sample displacement map
                float displacement = tex2Dlod(_DisplacementMap, float4(v.uv, 0, 0)).r;
                v.vertex.xyz += v.normal * displacement * _DisplacementStrength;
                
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = v.uv;
                o.worldNormal = UnityObjectToWorldNormal(v.normal);
                o.worldPos = mul(unity_ObjectToWorld, v.vertex).xyz;
                
                return o;
            }
            
            fixed4 frag (v2f i) : SV_Target
            {
                fixed4 col = tex2D(_MainTex, i.uv);
                
                // Simple lighting calculation
                float3 lightDir = normalize(_WorldSpaceLightPos0.xyz);
                float NdotL = max(0, dot(i.worldNormal, lightDir));
                col.rgb *= NdotL;
                
                return col;
            }
            ENDCG
        }
    }
}
```

## 🎨 Visual Effects and Techniques

### Procedural Textures and Noise
```hlsl
float hash(float2 p)
{
    return frac(sin(dot(p, float2(127.1, 311.7))) * 43758.5453);
}

float noise(float2 p)
{
    float2 i = floor(p);
    float2 f = frac(p);
    
    float a = hash(i);
    float b = hash(i + float2(1.0, 0.0));
    float c = hash(i + float2(0.0, 1.0));
    float d = hash(i + float2(1.0, 1.0));
    
    float2 u = f * f * (3.0 - 2.0 * f);
    
    return lerp(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}

// Fractal Brownian Motion
float fbm(float2 p, int octaves)
{
    float result = 0.0;
    float amplitude = 0.5;
    float frequency = 1.0;
    
    for(int i = 0; i < octaves; i++)
    {
        result += amplitude * noise(p * frequency);
        amplitude *= 0.5;
        frequency *= 2.0;
    }
    
    return result;
}
```

### Water and Fluid Simulation
```hlsl
Shader "Custom/Water"
{
    Properties
    {
        _WaterTex ("Water Texture", 2D) = "white" {}
        _NormalMap ("Normal Map", 2D) = "bump" {}
        _WaveSpeed ("Wave Speed", Float) = 1.0
        _WaveScale ("Wave Scale", Float) = 1.0
        _Transparency ("Transparency", Range(0,1)) = 0.5
    }
    
    SubShader
    {
        Tags { "Queue"="Transparent" "RenderType"="Transparent" }
        Blend SrcAlpha OneMinusSrcAlpha
        
        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            
            struct v2f
            {
                float4 pos : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 worldPos : TEXCOORD1;
            };
            
            sampler2D _WaterTex;
            sampler2D _NormalMap;
            float _WaveSpeed;
            float _WaveScale;
            float _Transparency;
            
            v2f vert(appdata_base v)
            {
                v2f o;
                
                // Wave animation
                float wave = sin(_Time.y * _WaveSpeed + v.vertex.x * _WaveScale) * 0.1;
                v.vertex.y += wave;
                
                o.pos = UnityObjectToClipPos(v.vertex);
                o.uv = v.texcoord;
                o.worldPos = mul(unity_ObjectToWorld, v.vertex).xyz;
                
                return o;
            }
            
            fixed4 frag(v2f i) : SV_Target
            {
                // Animated UV coordinates
                float2 uv1 = i.uv + _Time.x * 0.1;
                float2 uv2 = i.uv + _Time.x * 0.15;
                
                fixed4 water1 = tex2D(_WaterTex, uv1);
                fixed4 water2 = tex2D(_WaterTex, uv2);
                
                fixed4 finalColor = lerp(water1, water2, 0.5);
                finalColor.a = _Transparency;
                
                return finalColor;
            }
            ENDCG
        }
    }
}
```

## 🛠️ Shader Tools and Utilities

### C# Shader Property Management
```csharp
using UnityEngine;

[System.Serializable]
public class ShaderPropertyManager : MonoBehaviour
{
    [Header("Material References")]
    public Material targetMaterial;
    
    [Header("Float Properties")]
    public FloatProperty[] floatProperties;
    
    [Header("Color Properties")]
    public ColorProperty[] colorProperties;
    
    [Header("Texture Properties")]
    public TextureProperty[] textureProperties;
    
    [System.Serializable]
    public class FloatProperty
    {
        public string propertyName;
        public float value;
        [Range(0f, 5f)] public float animationSpeed = 1f;
        public bool animate;
        public AnimationCurve animationCurve = AnimationCurve.Linear(0, 0, 1, 1);
    }
    
    [System.Serializable]
    public class ColorProperty
    {
        public string propertyName;
        public Color color = Color.white;
        public bool useHDR;
    }
    
    [System.Serializable]
    public class TextureProperty
    {
        public string propertyName;
        public Texture2D texture;
        public Vector2 tiling = Vector2.one;
        public Vector2 offset = Vector2.zero;
    }
    
    private void Start()
    {
        if (targetMaterial == null)
            targetMaterial = GetComponent<Renderer>().material;
            
        ApplyProperties();
    }
    
    private void Update()
    {
        UpdateAnimatedProperties();
    }
    
    private void ApplyProperties()
    {
        foreach (var prop in floatProperties)
        {
            if (targetMaterial.HasProperty(prop.propertyName))
                targetMaterial.SetFloat(prop.propertyName, prop.value);
        }
        
        foreach (var prop in colorProperties)
        {
            if (targetMaterial.HasProperty(prop.propertyName))
                targetMaterial.SetColor(prop.propertyName, prop.color);
        }
        
        foreach (var prop in textureProperties)
        {
            if (targetMaterial.HasProperty(prop.propertyName))
            {
                targetMaterial.SetTexture(prop.propertyName, prop.texture);
                targetMaterial.SetTextureScale(prop.propertyName, prop.tiling);
                targetMaterial.SetTextureOffset(prop.propertyName, prop.offset);
            }
        }
    }
    
    private void UpdateAnimatedProperties()
    {
        foreach (var prop in floatProperties)
        {
            if (prop.animate && targetMaterial.HasProperty(prop.propertyName))
            {
                float animatedValue = prop.value * prop.animationCurve.Evaluate(
                    (Time.time * prop.animationSpeed) % 1f);
                targetMaterial.SetFloat(prop.propertyName, animatedValue);
            }
        }
    }
}
```

### Shader Performance Optimization
```csharp
using UnityEngine;
using UnityEngine.Rendering;

public class ShaderPerformanceOptimizer : MonoBehaviour
{
    [Header("LOD Settings")]
    public ShaderLODLevel[] lodLevels;
    
    [Header("Platform Optimization")]
    public bool optimizeForMobile = true;
    public bool useComputeShaders = false;
    
    [System.Serializable]
    public class ShaderLODLevel
    {
        public float distance;
        public Material material;
        public int shaderLOD;
    }
    
    private Camera mainCamera;
    private Renderer targetRenderer;
    private Material currentMaterial;
    
    private void Start()
    {
        mainCamera = Camera.main;
        targetRenderer = GetComponent<Renderer>();
        currentMaterial = targetRenderer.material;
        
        OptimizeForPlatform();
    }
    
    private void Update()
    {
        UpdateShaderLOD();
    }
    
    private void OptimizeForPlatform()
    {
        if (optimizeForMobile)
        {
            // Reduce shader complexity for mobile
            QualitySettings.globalTextureMipmapLimit = 1;
            
            // Use simpler shader variants
            Shader.EnableKeyword("MOBILE_OPTIMIZATION");
            Shader.DisableKeyword("HIGH_QUALITY_LIGHTING");
        }
        
        // Platform-specific optimizations
        switch (SystemInfo.graphicsDeviceType)
        {
            case GraphicsDeviceType.OpenGLES2:
            case GraphicsDeviceType.OpenGLES3:
                OptimizeForMobileGL();
                break;
                
            case GraphicsDeviceType.Vulkan:
                OptimizeForVulkan();
                break;
                
            case GraphicsDeviceType.Direct3D11:
            case GraphicsDeviceType.Direct3D12:
                OptimizeForDirectX();
                break;
        }
    }
    
    private void UpdateShaderLOD()
    {
        if (mainCamera == null || lodLevels.Length == 0) return;
        
        float distance = Vector3.Distance(transform.position, mainCamera.transform.position);
        
        for (int i = 0; i < lodLevels.Length; i++)
        {
            if (distance <= lodLevels[i].distance)
            {
                if (targetRenderer.material != lodLevels[i].material)
                {
                    targetRenderer.material = lodLevels[i].material;
                    targetRenderer.material.maximumLOD = lodLevels[i].shaderLOD;
                }
                break;
            }
        }
    }
    
    private void OptimizeForMobileGL()
    {
        // Reduce precision for mobile GPUs
        Shader.SetGlobalFloat("_HalfPrecision", 1.0f);
    }
    
    private void OptimizeForVulkan()
    {
        // Enable Vulkan-specific optimizations
        if (useComputeShaders)
            Shader.EnableKeyword("VULKAN_COMPUTE");
    }
    
    private void OptimizeForDirectX()
    {
        // Enable DirectX-specific features
        Shader.EnableKeyword("DIRECTX_OPTIMIZATION");
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Shader Code Generation
- **Automated Shader Creation**: Generate shaders based on visual descriptions
- **Parameter Optimization**: AI-assisted shader parameter tuning
- **Cross-Platform Conversion**: Automatically convert shaders between platforms

### Performance Analysis
- **Bottleneck Detection**: AI analysis of shader performance metrics
- **Optimization Suggestions**: Automated recommendations for shader improvements
- **LOD Generation**: AI-generated level-of-detail shader variants

### Visual Effect Automation
- **Effect Library Generation**: Create comprehensive shader effect libraries
- **Material Variant Creation**: Generate multiple material variations automatically
- **Documentation Generation**: Auto-generate shader documentation and tutorials

## 💡 Key Highlights

- **Master HLSL syntax** and Unity's shader architecture
- **Implement visual effects** using procedural techniques and noise functions
- **Optimize shader performance** for different platforms and hardware
- **Create reusable tools** for shader property management and automation
- **Leverage AI assistance** for shader generation and optimization
- **Build comprehensive libraries** of visual effects and materials
- **Focus on cross-platform compatibility** and performance optimization

## 🔄 Advanced Shader Techniques

### Compute Shaders for GPU Acceleration
```hlsl
#pragma kernel CSMain

RWTexture2D<float4> Result;
float Time;

[numthreads(8,8,1)]
void CSMain (uint3 id : SV_DispatchThreadID)
{
    float2 uv = float2(id.xy) / 512.0;
    
    // Generate procedural pattern
    float pattern = sin(uv.x * 10.0 + Time) * cos(uv.y * 10.0 + Time);
    
    Result[id.xy] = float4(pattern, pattern, pattern, 1.0);
}
```

### Multi-Pass Rendering Effects
```hlsl
Shader "Custom/MultiPass"
{
    SubShader
    {
        // First pass - depth
        Pass
        {
            Name "DepthPass"
            ColorMask 0
            ZWrite On
            // Vertex/Fragment shader for depth
        }
        
        // Second pass - color
        Pass
        {
            Name "ColorPass"
            ZWrite Off
            ZTest Equal
            // Main rendering pass
        }
        
        // Third pass - outline
        Pass
        {
            Name "OutlinePass"
            Cull Front
            ZWrite Off
            // Outline effect
        }
    }
}
```

This comprehensive guide provides the foundation for mastering shader programming in Unity, from basic HLSL syntax to advanced visual effects and performance optimization techniques.