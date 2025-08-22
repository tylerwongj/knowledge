# @a-Shader-Programming-Fundamentals - Unity Shader Development Foundation

## 🎯 Learning Objectives
- Understand shader basics and rendering pipeline in Unity
- Master HLSL/ShaderLab syntax and structure
- Learn vertex and fragment shader fundamentals
- Apply AI/LLM tools to accelerate shader learning and debugging

---

## 🔧 Shader Fundamentals

### What Are Shaders?
Shaders are **GPU programs** that determine how 3D objects appear on screen:

- **Vertex Shader**: Processes each vertex (position, UV coordinates, normals)
- **Fragment Shader**: Determines final pixel color
- **Geometry Shader**: Optional - can create/modify geometry
- **Compute Shader**: General-purpose GPU computing

### Unity's Shader Pipeline
```
Mesh Data → Vertex Shader → Rasterization → Fragment Shader → Final Pixel
```

### ShaderLab Structure
Unity shaders use **ShaderLab** wrapper around HLSL:

```hlsl
Shader "Custom/MyShader" {
    Properties {
        _MainTex ("Texture", 2D) = "white" {}
        _Color ("Color", Color) = (1,1,1,1)
    }
    
    SubShader {
        Tags { "RenderType"="Opaque" }
        
        Pass {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            
            // HLSL code here
            ENDCG
        }
    }
}
```

---

## 🚀 Essential Shader Types

### 1. Unlit Shader (Simplest)
No lighting calculations - perfect for UI, effects, or stylized visuals:

```hlsl
Shader "Custom/Unlit" {
    Properties {
        _MainTex ("Texture", 2D) = "white" {}
        _Color ("Color", Color) = (1,1,1,1)
    }
    
    SubShader {
        Tags { "RenderType"="Opaque" }
        
        Pass {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            
            struct appdata {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
            };
            
            struct v2f {
                float2 uv : TEXCOORD0;
                float4 vertex : SV_POSITION;
            };
            
            sampler2D _MainTex;
            float4 _Color;
            
            v2f vert (appdata v) {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = v.uv;
                return o;
            }
            
            fixed4 frag (v2f i) : SV_Target {
                fixed4 col = tex2D(_MainTex, i.uv) * _Color;
                return col;
            }
            ENDCG
        }
    }
}
```

### 2. Surface Shader (Unity's High-Level)
Unity's simplified lighting system:

```hlsl
Shader "Custom/Surface" {
    Properties {
        _Color ("Color", Color) = (1,1,1,1)
        _MainTex ("Albedo", 2D) = "white" {}
        _Glossiness ("Smoothness", Range(0,1)) = 0.5
        _Metallic ("Metallic", Range(0,1)) = 0.0
    }
    
    SubShader {
        Tags { "RenderType"="Opaque" }
        
        CGPROGRAM
        #pragma surface surf Standard fullforwardshadows
        
        sampler2D _MainTex;
        half _Glossiness;
        half _Metallic;
        fixed4 _Color;
        
        struct Input {
            float2 uv_MainTex;
        };
        
        void surf (Input IN, inout SurfaceOutputStandard o) {
            fixed4 c = tex2D (_MainTex, IN.uv_MainTex) * _Color;
            o.Albedo = c.rgb;
            o.Metallic = _Metallic;
            o.Smoothness = _Glossiness;
            o.Alpha = c.a;
        }
        ENDCG
    }
}
```

---

## 🎨 Common Shader Techniques

### 1. UV Animation
Moving textures for water, conveyor belts, scrolling backgrounds:

```hlsl
// In fragment shader
float2 scrolledUV = i.uv + _Time.y * _ScrollSpeed;
fixed4 col = tex2D(_MainTex, scrolledUV);
```

### 2. Color Lerping
Smooth color transitions:

```hlsl
fixed4 finalColor = lerp(_ColorA, _ColorB, _BlendFactor);
```

### 3. Vertex Displacement
Moving vertices for waves, wind effects:

```hlsl
// In vertex shader
float wave = sin(_Time.y * _Frequency + v.vertex.x * _WaveLength) * _Amplitude;
v.vertex.y += wave;
```

### 4. Transparency/Alpha
Making objects see-through:

```hlsl
// In Properties
_Alpha ("Alpha", Range(0,1)) = 1.0

// In SubShader Tags
Tags { "RenderType"="Transparent" "Queue"="Transparent" }

// Enable alpha blending
Blend SrcAlpha OneMinusSrcAlpha

// In fragment shader
col.a = _Alpha;
```

---

## 🚀 AI/LLM Integration Opportunities

### Shader Code Generation
Use AI to generate shader boilerplate and effects:

**Example prompts:**
> "Generate a Unity HLSL shader that creates a dissolve effect using a noise texture"
> "Create a toon/cell shader for stylized rendering in Unity"
> "Write a vertex shader that creates flag-waving animation"

### Debugging and Optimization
- Ask AI to explain shader compilation errors
- Get suggestions for performance optimization
- Generate test cases for different shader variations

### Learning Acceleration
- Request analogies to understand complex shader concepts
- Generate practice exercises for different shader techniques
- Create study guides for shader programming interviews

### Documentation Generation
- Use AI to comment complex shader code
- Generate README files for shader collections
- Create technical explanations for portfolio projects

---

## 💡 Key Shader Concepts

### 1. Coordinate Spaces
- **Object Space**: Local to the mesh
- **World Space**: Global 3D coordinates
- **View Space**: Relative to camera
- **Clip Space**: Final transformed coordinates

### 2. Common HLSL Functions
```hlsl
// Mathematical
lerp(a, b, t)          // Linear interpolation
saturate(x)            // Clamp to 0-1
dot(a, b)              // Dot product
normalize(v)           // Unit vector
length(v)              // Vector magnitude

// Texture Sampling
tex2D(sampler, uv)     // Sample 2D texture
tex2Dlod(sampler, uv)  // Sample with specific mip level

// Utility
UnityObjectToClipPos(pos)  // Transform vertex to clip space
WorldSpaceViewDir(pos)     // Direction from vertex to camera
```

### 3. Performance Considerations
- **Vertex vs Fragment**: Do calculations in vertex shader when possible
- **Texture Lookups**: Minimize texture samples in fragment shader
- **Branching**: Avoid if/else statements on mobile
- **Precision**: Use `fixed` for colors, `half` for most calculations

---

## 🎮 Practical Exercises

### Exercise 1: Color Gradient Shader
Create a shader that displays a gradient from one color to another:
1. Set up two color properties
2. Use UV coordinates to lerp between colors
3. Add time-based animation to cycle colors

### Exercise 2: Texture Scrolling
Build a conveyor belt or flowing water effect:
1. Create UV offset based on time
2. Add speed control property
3. Make it tile seamlessly

### Exercise 3: Simple Dissolve Effect
Create an object that dissolves away:
1. Use a noise texture as dissolve mask
2. Add dissolve threshold property
3. Create edge glow effect

---

## 🎯 Portfolio Project Ideas

### Beginner: "Shader Showcase Scene"
Create a scene demonstrating various shader effects:
- Unlit textured objects
- Animated UV scrolling
- Color transitions
- Simple vertex displacement

### Intermediate: "Stylized Environment Shaders"
Build a cohesive set of stylized shaders:
- Toon/cell shading for characters
- Stylized water shader
- Wind-animated foliage
- Particle effects with custom shaders

### Advanced: "Interactive Shader System"
Create shaders that respond to gameplay:
- Health-based character shaders
- Environmental hazard effects
- UI shaders with dynamic elements
- Post-processing effect stack

---

## 📚 Essential Resources

### Official Unity Resources
- Unity Shader Graph (visual shader editor)
- Unity Manual: Shaders and Materials
- Unity Shader Reference documentation

### Learning Platforms
- **Catlike Coding**: Advanced Unity tutorials
- **Alan Zucconi**: Comprehensive shader tutorials
- **Harry Alisavakis**: Creative shader techniques

### AI-Enhanced Learning
- Use Claude/ChatGPT for shader concept explanations
- Generate practice shaders based on visual descriptions
- Debug shader compilation errors with AI assistance

---

## 🔍 Interview Preparation

### Common Shader Questions

1. **"Explain the difference between vertex and fragment shaders"**
   - Vertex: Processes each vertex, runs fewer times
   - Fragment: Determines pixel color, runs once per pixel

2. **"How would you optimize a shader for mobile?"**
   - Use lower precision (fixed/half vs float)
   - Minimize texture lookups
   - Avoid branching and complex calculations

3. **"What's the difference between Surface shaders and vertex/fragment shaders?"**
   - Surface: Unity's high-level, automatic lighting
   - Vert/Frag: Low-level, full control, better performance

### Code Challenge Preparation
Practice writing shaders that demonstrate:
- Basic UV manipulation
- Color blending techniques
- Simple vertex animation
- Texture sampling and filtering

---

## ⚡ AI Productivity Hacks

### Rapid Prototyping
- Generate shader templates for common effects
- Use AI to convert Shader Graph to HLSL code
- Create variations of existing shaders quickly

### Learning Optimization
- Generate shader challenges based on your skill level
- Create visual reference guides for HLSL functions
- Ask AI to explain complex graphics programming concepts

### Portfolio Enhancement
- Use AI to write technical descriptions of shader effects
- Generate documentation for shader collections
- Create demo scene descriptions highlighting technical achievements

---

## 🎯 Next Steps
1. Master basic unlit and surface shader creation
2. Move to **@b-Advanced-Shader-Techniques.md** for complex effects
3. Practice with Unity's Shader Graph for visual learning
4. Build a portfolio shader collection demonstrating various techniques

> **AI Integration Reminder**: Use LLMs to accelerate shader learning, debug compilation errors, and generate creative effect ideas. Shader programming benefits greatly from AI-assisted experimentation and explanation!