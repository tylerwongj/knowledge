# @a-Unity Shader Programming Fundamentals

## 🎯 Learning Objectives
- Understand the Unity shader pipeline and rendering process
- Master HLSL syntax and shader development fundamentals
- Build practical shader effects for Unity games
- Develop debugging and optimization skills for shader performance

## 🔧 Core Shader Concepts

### Unity Rendering Pipeline Overview
```
Application -> CPU Processing -> GPU Processing -> Screen Output
               |                 |
               Mesh Data          Vertex Shader
               Textures          Geometry Shader (optional)
               Materials         Fragment/Pixel Shader
               Lighting          Output Merger
```

### Shader Types in Unity
```hlsl
// Unlit Shader - No lighting calculations
Shader "Custom/UnlitColor"
{
    Properties
    {
        _MainTex ("Texture", 2D) = "white" {}
        _Color ("Color", Color) = (1,1,1,1)
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        LOD 100

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
            };

            struct v2f
            {
                float2 uv : TEXCOORD0;
                float4 vertex : SV_POSITION;
            };

            sampler2D _MainTex;
            float4 _MainTex_ST;
            fixed4 _Color;
            
            v2f vert (appdata v)
            {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = TRANSFORM_TEX(v.uv, _MainTex);
                return o;
            }
            
            fixed4 frag (v2f i) : SV_Target
            {
                fixed4 col = tex2D(_MainTex, i.uv) * _Color;
                return col;
            }
            ENDCG
        }
    }
}
```

### HLSL Language Fundamentals

#### Data Types
```hlsl
// Scalar types
float   // 32-bit floating point
half    // 16-bit floating point (mobile optimization)
fixed   // 11-bit fixed point (legacy, now float)
int     // 32-bit integer
bool    // Boolean

// Vector types
float2  // 2D vector (x, y)
float3  // 3D vector (x, y, z)
float4  // 4D vector (x, y, z, w) - often used for RGBA colors

// Matrix types
float4x4  // 4x4 matrix (common for transformations)
float3x3  // 3x3 matrix
```

#### Swizzling and Vector Operations
```hlsl
float4 color = float4(1.0, 0.5, 0.2, 1.0);

// Swizzling - accessing components
float3 rgb = color.rgb;     // Gets (r, g, b)
float2 rg = color.rg;       // Gets (r, g)
float alpha = color.a;      // Gets alpha component

// Rearranging components
float4 bgra = color.bgra;   // Reorders to (b, g, r, a)
float3 grb = color.grb;     // Gets (g, r, b)
```

## 🚀 Essential Shader Techniques

### Texture Sampling and UV Manipulation
```hlsl
// Basic texture sampling
fixed4 col = tex2D(_MainTex, i.uv);

// UV scrolling for animations
float2 scrolledUV = i.uv + _Time.y * _ScrollSpeed;
fixed4 col = tex2D(_MainTex, scrolledUV);

// UV scaling and tiling
float2 tiledUV = i.uv * _TileScale + _TileOffset;
fixed4 col = tex2D(_MainTex, tiledUV);

// Polar coordinates for radial effects
float2 center = float2(0.5, 0.5);
float2 delta = i.uv - center;
float angle = atan2(delta.y, delta.x);
float radius = length(delta);
```

### Color Manipulation and Effects
```hlsl
// Hue shifting
float3 hsv = rgb2hsv(col.rgb);
hsv.x += _HueShift;
col.rgb = hsv2rgb(hsv);

// Brightness and contrast
col.rgb = (col.rgb - 0.5) * _Contrast + 0.5;
col.rgb *= _Brightness;

// Gradient mapping
float luminance = dot(col.rgb, float3(0.299, 0.587, 0.114));
col.rgb = tex2D(_GradientTex, float2(luminance, 0.5)).rgb;
```

### Lighting Calculations
```hlsl
// Lambert diffuse lighting
float3 lightDir = normalize(_WorldSpaceLightPos0.xyz);
float3 normal = normalize(i.worldNormal);
float NdotL = max(0, dot(normal, lightDir));
float3 diffuse = _LightColor0.rgb * NdotL;

// Phong specular lighting
float3 viewDir = normalize(_WorldSpaceCameraPos - i.worldPos);
float3 reflectDir = reflect(-lightDir, normal);
float spec = pow(max(0, dot(viewDir, reflectDir)), _Shininess);
float3 specular = _SpecColor.rgb * spec;
```

## 💡 Practical Shader Examples

### Dissolve Effect Shader
```hlsl
// Fragment shader for dissolve effect
fixed4 frag (v2f i) : SV_Target
{
    fixed4 col = tex2D(_MainTex, i.uv);
    fixed noise = tex2D(_NoiseTex, i.uv).r;
    
    // Create dissolve cutoff
    clip(noise - _DissolveAmount);
    
    // Edge burning effect
    float edge = noise - _DissolveAmount;
    if (edge < _EdgeWidth)
    {
        col.rgb = lerp(_BurnColor.rgb, col.rgb, edge / _EdgeWidth);
    }
    
    return col;
}
```

### Water Wave Shader
```hlsl
// Vertex shader for water waves
v2f vert (appdata v)
{
    v2f o;
    
    // Calculate wave displacement
    float wave1 = sin(v.vertex.x * _WaveFreq1 + _Time.y * _WaveSpeed1) * _WaveAmp1;
    float wave2 = sin(v.vertex.z * _WaveFreq2 + _Time.y * _WaveSpeed2) * _WaveAmp2;
    
    v.vertex.y += wave1 + wave2;
    
    o.vertex = UnityObjectToClipPos(v.vertex);
    o.uv = TRANSFORM_TEX(v.uv, _MainTex);
    return o;
}
```

## 🔧 Shader Optimization Techniques

### Performance Best Practices
```hlsl
// Use appropriate precision
half4 color;  // Instead of float4 on mobile
fixed4 color; // For simple color operations

// Minimize texture samples
// Bad: Multiple samples
fixed4 col1 = tex2D(_MainTex, i.uv);
fixed4 col2 = tex2D(_MainTex, i.uv + offset);

// Good: Single sample with preprocessing
fixed4 col = tex2D(_MainTex, i.uv);

// Use built-in functions
float luminance = dot(col.rgb, float3(0.299, 0.587, 0.114));
// Instead of manual calculation

// Avoid branches in fragment shaders
// Bad:
if (col.a > 0.5)
    col.rgb *= 2.0;
else
    col.rgb *= 0.5;

// Good:
float multiplier = lerp(0.5, 2.0, step(0.5, col.a));
col.rgb *= multiplier;
```

### LOD and Quality Scaling
```hlsl
SubShader
{
    Tags { "RenderType"="Opaque" }
    LOD 200  // Level of Detail
    
    Pass
    {
        // High quality version
    }
}

SubShader
{
    Tags { "RenderType"="Opaque" }
    LOD 100  // Lower quality fallback
    
    Pass
    {
        // Simplified version
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Shader Development Acceleration
```
# Shader Generation Prompt
"Create a Unity HLSL shader that:
- Implements [specific effect]
- Uses [texture inputs/properties]
- Optimized for [platform/performance target]
- Includes proper vertex and fragment shaders
- Uses Unity's built-in lighting functions"

# Optimization Analysis
"Analyze this shader code for performance issues:
[shader code]
Focus on: mobile optimization, texture sampling efficiency, mathematical operations"

# Effect Implementation
"Convert this visual effect description to Unity shader code:
[description of desired visual effect]"
```

### Shader Learning and Documentation
- Generate explanations for complex shader mathematics
- Create interactive tutorials for shader concepts
- Automate shader documentation and commenting
- Generate test cases for shader validation

## 🎯 Learning Progression Path

### Week 1-2: Fundamentals
- Understand the rendering pipeline
- Learn HLSL syntax and basic operations
- Create simple unlit and vertex-colored shaders
- Practice UV manipulation and texture sampling

### Week 3-4: Lighting and Materials
- Implement diffuse and specular lighting
- Understand surface shaders vs vertex/fragment shaders
- Create material property interfaces
- Learn normal mapping and bump mapping

### Week 5-6: Special Effects
- Implement dissolve, burning, and transition effects
- Create animated shaders with time-based functions
- Build environmental effects (water, fire, magic)
- Learn post-processing and screen-space effects

### Week 7-8: Optimization and Advanced Topics
- Master mobile optimization techniques
- Understand GPU profiling and debugging
- Learn compute shaders for complex calculations
- Explore advanced rendering techniques (PBR, subsurface scattering)

## 🔗 Unity Integration

### Shader Graph Integration
- Understand when to use Shader Graph vs hand-coded shaders
- Convert between visual and code representations
- Optimize Shader Graph outputs
- Create custom nodes for reusable functionality

### C# Script Integration
```csharp
public class ShaderController : MonoBehaviour
{
    [SerializeField] private Material material;
    [SerializeField] private float dissolveSpeed = 1f;
    
    private void Update()
    {
        // Animate shader properties from C#
        float dissolveAmount = Mathf.PingPong(Time.time * dissolveSpeed, 1f);
        material.SetFloat("_DissolveAmount", dissolveAmount);
        
        // Set color based on game state
        Color healthColor = Color.Lerp(Color.red, Color.green, playerHealth / maxHealth);
        material.SetColor("_HealthColor", healthColor);
    }
}
```

This foundation provides the essential knowledge for creating effective shaders in Unity while leveraging AI tools to accelerate learning and development.