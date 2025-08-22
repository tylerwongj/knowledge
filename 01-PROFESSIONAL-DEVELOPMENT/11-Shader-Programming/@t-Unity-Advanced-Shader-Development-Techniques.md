# @t-Unity-Advanced-Shader-Development-Techniques

## 🎯 Learning Objectives

- Master advanced Unity shader programming with HLSL and Shader Graph
- Implement complex visual effects using compute shaders and GPU optimization
- Create production-ready shader systems with performance monitoring
- Build custom render pipeline features and advanced lighting models

## 🔧 Advanced Shader Architecture

### Universal Render Pipeline Custom Lit Shader

```hlsl
Shader "Custom/AdvancedLit"
{
    Properties
    {
        [MainTexture] _BaseMap ("Base Map", 2D) = "white" {}
        [MainColor] _BaseColor ("Base Color", Color) = (1, 1, 1, 1)
        
        [Space(10)]
        [Header(Surface Properties)]
        _Metallic ("Metallic", Range(0.0, 1.0)) = 0.0
        _Smoothness ("Smoothness", Range(0.0, 1.0)) = 0.5
        _MetallicGlossMap ("Metallic Map", 2D) = "white" {}
        
        [Space(10)]
        [Header(Normal Mapping)]
        [Toggle(_NORMALMAP)] _EnableNormalMap ("Enable Normal Map", Float) = 0
        _BumpMap ("Normal Map", 2D) = "bump" {}
        _BumpScale ("Normal Scale", Range(0.0, 2.0)) = 1.0
        
        [Space(10)]
        [Header(Emission)]
        [Toggle(_EMISSION)] _EnableEmission ("Enable Emission", Float) = 0
        [HDR] _EmissionColor ("Emission Color", Color) = (0, 0, 0, 1)
        _EmissionMap ("Emission Map", 2D) = "white" {}
        
        [Space(10)]
        [Header(Advanced Features)]
        [Toggle(_PARALLAXMAP)] _EnableParallax ("Enable Parallax", Float) = 0
        _ParallaxMap ("Parallax Map", 2D) = "grey" {}
        _Parallax ("Parallax Scale", Range(0.005, 0.08)) = 0.02
        
        [Toggle(_DETAIL_MULX2)] _EnableDetailMap ("Enable Detail", Float) = 0
        _DetailMap ("Detail Map", 2D) = "grey" {}
        _DetailNormalMap ("Detail Normal", 2D) = "bump" {}
        _DetailScale ("Detail Scale", Range(0.0, 2.0)) = 1.0
        
        [Space(10)]
        [Header(Advanced Lighting)]
        [Toggle(_SUBSURFACE)] _EnableSSS ("Enable Subsurface Scattering", Float) = 0
        _SSSColor ("SSS Color", Color) = (1, 0.4, 0.25, 1)
        _SSSPower ("SSS Power", Range(1.0, 16.0)) = 4.0
        _SSSDistortion ("SSS Distortion", Range(0.0, 1.0)) = 0.0
        _SSSScale ("SSS Scale", Range(0.0, 2.0)) = 1.0
        
        [Toggle(_CLEARCOAT)] _EnableClearCoat ("Enable Clear Coat", Float) = 0
        _ClearCoat ("Clear Coat Strength", Range(0.0, 1.0)) = 0.0
        _ClearCoatSmoothness ("Clear Coat Smoothness", Range(0.0, 1.0)) = 1.0
        
        [Space(10)]
        [Header(Performance)]
        [KeywordEnum(Off, Low, Medium, High)] _Quality ("Quality Level", Float) = 2
        
        [Space(10)]
        [Header(Rendering)]
        [Enum(UnityEngine.Rendering.CullMode)] _Cull ("Cull Mode", Float) = 2
        [Enum(UnityEngine.Rendering.BlendMode)] _SrcBlend ("Src Blend", Float) = 1
        [Enum(UnityEngine.Rendering.BlendMode)] _DstBlend ("Dst Blend", Float) = 0
        _ZWrite ("Z Write", Float) = 1.0
    }
    
    SubShader
    {
        Tags 
        { 
            "RenderType" = "Opaque" 
            "RenderPipeline" = "UniversalPipeline"
            "IgnoreProjector" = "True"
        }
        
        LOD 300
        
        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }
            
            Blend [_SrcBlend] [_DstBlend]
            ZWrite [_ZWrite]
            Cull [_Cull]
            
            HLSLPROGRAM
            #pragma target 4.5
            #pragma exclude_renderers gles gles3 glcore
            
            // Unity keywords
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
            #pragma multi_compile _ _ADDITIONAL_LIGHTS_VERTEX _ADDITIONAL_LIGHTS
            #pragma multi_compile_fragment _ _ADDITIONAL_LIGHT_SHADOWS
            #pragma multi_compile_fragment _ _SHADOWS_SOFT
            #pragma multi_compile_fragment _ _SCREEN_SPACE_OCCLUSION
            #pragma multi_compile _ LIGHTMAP_SHADOW_MIXING
            #pragma multi_compile _ SHADOWS_SHADOWMASK
            #pragma multi_compile _ DIRLIGHTMAP_COMBINED
            #pragma multi_compile _ LIGHTMAP_ON
            #pragma multi_compile_fog
            
            // Custom feature keywords
            #pragma shader_feature_local _NORMALMAP
            #pragma shader_feature_local _EMISSION
            #pragma shader_feature_local _PARALLAXMAP
            #pragma shader_feature_local _DETAIL_MULX2
            #pragma shader_feature_local _SUBSURFACE
            #pragma shader_feature_local _CLEARCOAT
            #pragma shader_feature_local _QUALITY_LOW _QUALITY_MEDIUM _QUALITY_HIGH
            
            // GPU Instancing
            #pragma multi_compile_instancing
            #pragma multi_compile _ DOTS_INSTANCING_ON
            
            #pragma vertex LitPassVertex
            #pragma fragment LitPassFragment
            
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Shadows.hlsl"
            #include "AdvancedLitInput.hlsl"
            #include "AdvancedLitForwardPass.hlsl"
            
            ENDHLSL
        }
        
        Pass
        {
            Name "ShadowCaster"
            Tags { "LightMode" = "ShadowCaster" }
            
            ZWrite On
            ZTest LEqual
            ColorMask 0
            Cull [_Cull]
            
            HLSLPROGRAM
            #pragma target 2.0
            #pragma exclude_renderers gles gles3 glcore
            
            #pragma vertex ShadowPassVertex
            #pragma fragment ShadowPassFragment
            
            #pragma multi_compile_instancing
            #pragma multi_compile _ DOTS_INSTANCING_ON
            
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "AdvancedLitInput.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/Shaders/ShadowCasterPass.hlsl"
            
            ENDHLSL
        }
        
        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode" = "DepthOnly" }
            
            ZWrite On
            ColorMask 0
            Cull [_Cull]
            
            HLSLPROGRAM
            #pragma target 2.0
            #pragma exclude_renderers gles gles3 glcore
            
            #pragma vertex DepthOnlyVertex
            #pragma fragment DepthOnlyFragment
            
            #pragma multi_compile_instancing
            #pragma multi_compile _ DOTS_INSTANCING_ON
            
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "AdvancedLitInput.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/Shaders/DepthOnlyPass.hlsl"
            
            ENDHLSL
        }
    }
    
    SubShader
    {
        Tags 
        { 
            "RenderType" = "Opaque" 
            "RenderPipeline" = "UniversalPipeline"
            "IgnoreProjector" = "True"
        }
        
        LOD 150
        
        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }
            
            Blend [_SrcBlend] [_DstBlend]
            ZWrite [_ZWrite]
            Cull [_Cull]
            
            HLSLPROGRAM
            #pragma target 2.0
            #pragma only_renderers gles gles3 glcore d3d11
            
            // Simplified keywords for mobile
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS
            #pragma multi_compile _ _ADDITIONAL_LIGHTS_VERTEX _ADDITIONAL_LIGHTS
            #pragma multi_compile_fragment _ _ADDITIONAL_LIGHT_SHADOWS
            #pragma multi_compile_fog
            
            #pragma shader_feature_local _NORMALMAP
            #pragma shader_feature_local _EMISSION
            
            #pragma multi_compile_instancing
            
            #pragma vertex SimpleLitPassVertex
            #pragma fragment SimpleLitPassFragment
            
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "AdvancedLitInput.hlsl"
            #include "AdvancedLitSimplePass.hlsl"
            
            ENDHLSL
        }
    }
    
    Fallback "Hidden/Universal Render Pipeline/FallbackError"
    CustomEditor "AdvancedLitShaderGUI"
}
```

### Advanced Lighting Input and Functions

```hlsl
// AdvancedLitInput.hlsl
#ifndef ADVANCED_LIT_INPUT_INCLUDED
#define ADVANCED_LIT_INPUT_INCLUDED

#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
#include "Packages/com.unity.render-pipelines.core/ShaderLibrary/CommonMaterial.hlsl"
#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/SurfaceInput.hlsl"

CBUFFER_START(UnityPerMaterial)
    float4 _BaseMap_ST;
    float4 _BaseColor;
    float4 _EmissionColor;
    float4 _SSSColor;
    
    half _Metallic;
    half _Smoothness;
    half _BumpScale;
    half _Parallax;
    half _DetailScale;
    
    half _SSSPower;
    half _SSSDistortion;
    half _SSSScale;
    half _ClearCoat;
    half _ClearCoatSmoothness;
    
    half _Cutoff;
    half _ZWrite;
    half _Cull;
    half _SrcBlend;
    half _DstBlend;
CBUFFER_END

TEXTURE2D(_BaseMap);               SAMPLER(sampler_BaseMap);
TEXTURE2D(_MetallicGlossMap);      SAMPLER(sampler_MetallicGlossMap);
TEXTURE2D(_BumpMap);               SAMPLER(sampler_BumpMap);
TEXTURE2D(_ParallaxMap);           SAMPLER(sampler_ParallaxMap);
TEXTURE2D(_EmissionMap);           SAMPLER(sampler_EmissionMap);
TEXTURE2D(_DetailMap);             SAMPLER(sampler_DetailMap);
TEXTURE2D(_DetailNormalMap);       SAMPLER(sampler_DetailNormalMap);

#ifdef _SPECULAR_SETUP
    #define SAMPLE_METALLICSPECULAR(uv) SAMPLE_TEXTURE2D(_SpecGlossMap, sampler_SpecGlossMap, uv)
#else
    #define SAMPLE_METALLICSPECULAR(uv) SAMPLE_TEXTURE2D(_MetallicGlossMap, sampler_MetallicGlossMap, uv)
#endif

// Advanced surface data structure
struct AdvancedSurfaceData
{
    half3 albedo;
    half3 specular;
    half  metallic;
    half  smoothness;
    half3 normalTS;
    half3 emission;
    half  occlusion;
    half  alpha;
    half  clearCoatMask;
    half  clearCoatSmoothness;
    half3 subsurfaceColor;
    half  subsurfacePower;
};

// Parallax mapping function
float2 ParallaxMapping(float2 texCoords, float3 viewDir, float heightScale, TEXTURE2D_PARAM(heightMap, sampler_heightMap))
{
    #if defined(_PARALLAXMAP)
        // Traditional parallax mapping
        float height = SAMPLE_TEXTURE2D(heightMap, sampler_heightMap, texCoords).r;
        float2 p = viewDir.xy / viewDir.z * (height * heightScale);
        return texCoords - p;
    #else
        return texCoords;
    #endif
}

// Advanced parallax occlusion mapping
float2 ParallaxOcclusionMapping(float2 texCoords, float3 viewDir, float heightScale, TEXTURE2D_PARAM(heightMap, sampler_heightMap))
{
    #if defined(_PARALLAXMAP) && defined(_QUALITY_HIGH)
        const float minLayers = 8.0;
        const float maxLayers = 32.0;
        float numLayers = lerp(maxLayers, minLayers, abs(dot(float3(0, 0, 1), viewDir)));
        
        float layerDepth = 1.0 / numLayers;
        float currentLayerDepth = 0.0;
        float2 P = viewDir.xy * heightScale;
        float2 deltaTexCoords = P / numLayers;
        
        float2 currentTexCoords = texCoords;
        float currentDepthMapValue = SAMPLE_TEXTURE2D(heightMap, sampler_heightMap, currentTexCoords).r;
        
        while(currentLayerDepth < currentDepthMapValue)
        {
            currentTexCoords -= deltaTexCoords;
            currentDepthMapValue = SAMPLE_TEXTURE2D(heightMap, sampler_heightMap, currentTexCoords).r;
            currentLayerDepth += layerDepth;
        }
        
        // Interpolation for smoother results
        float2 prevTexCoords = currentTexCoords + deltaTexCoords;
        float afterDepth = currentDepthMapValue - currentLayerDepth;
        float beforeDepth = SAMPLE_TEXTURE2D(heightMap, sampler_heightMap, prevTexCoords).r - currentLayerDepth + layerDepth;
        float weight = afterDepth / (afterDepth - beforeDepth);
        
        return prevTexCoords * weight + currentTexCoords * (1.0 - weight);
    #else
        return ParallaxMapping(texCoords, viewDir, heightScale, TEXTURE2D_ARGS(heightMap, sampler_heightMap));
    #endif
}

// Sample base color with detail mapping
half4 SampleAlbedoAlpha(float2 uv, float2 detailUV, TEXTURE2D_PARAM(albedoAlphaMap, sampler))
{
    half4 color = SAMPLE_TEXTURE2D(albedoAlphaMap, sampler, uv) * _BaseColor;
    
    #if defined(_DETAIL_MULX2)
        half4 detail = SAMPLE_TEXTURE2D(_DetailMap, sampler_DetailMap, detailUV);
        color.rgb *= detail.rgb * unity_ColorSpaceDouble.rgb * _DetailScale;
    #endif
    
    return color;
}

// Sample metallic with specular workflow support
half4 SampleMetallicSpecGloss(float2 uv, half albedoAlpha)
{
    half4 specGloss;
    
    #ifdef _METALLICSPECGLOSSMAP
        specGloss = SAMPLE_TEXTURE2D(_MetallicGlossMap, sampler_MetallicGlossMap, uv);
        #ifdef _SMOOTHNESS_TEXTURE_ALBEDO_CHANNEL_A
            specGloss.a = albedoAlpha * _Smoothness;
        #else
            specGloss.a *= _Smoothness;
        #endif
    #else
        #if _SPECULAR_SETUP
            specGloss.rgb = _SpecColor.rgb;
        #else
            specGloss.rgb = _Metallic.rrr;
        #endif
        
        #ifdef _SMOOTHNESS_TEXTURE_ALBEDO_CHANNEL_A
            specGloss.a = albedoAlpha * _Smoothness;
        #else
            specGloss.a = _Smoothness;
        #endif
    #endif
    
    return specGloss;
}

// Sample normal with detail normal blending
half3 SampleNormal(float2 uv, float2 detailUV, TEXTURE2D_PARAM(bumpMap, sampler), half scale = 1.0h)
{
    half3 normalTS = UnpackNormalScale(SAMPLE_TEXTURE2D(bumpMap, sampler, uv), scale);
    
    #if defined(_DETAIL_MULX2)
        half3 detailNormalTS = UnpackNormalScale(SAMPLE_TEXTURE2D(_DetailNormalMap, sampler_DetailNormalMap, detailUV), _DetailScale);
        normalTS = BlendNormalRNM(normalTS, detailNormalTS);
    #endif
    
    return normalTS;
}

// Sample emission
half3 SampleEmission(float2 uv, half3 emissionColor, TEXTURE2D_PARAM(emissionMap, sampler))
{
    #ifndef _EMISSION
        return 0;
    #else
        return SAMPLE_TEXTURE2D(emissionMap, sampler, uv).rgb * emissionColor.rgb;
    #endif
}

// Initialize advanced surface data
inline void InitializeAdvancedSurfaceData(float2 uv, float2 detailUV, out AdvancedSurfaceData outSurfaceData)
{
    half4 albedoAlpha = SampleAlbedoAlpha(uv, detailUV, TEXTURE2D_ARGS(_BaseMap, sampler_BaseMap));
    outSurfaceData.albedo = albedoAlpha.rgb;
    outSurfaceData.alpha = Alpha(albedoAlpha.a, _BaseColor, _Cutoff);
    
    half4 specGloss = SampleMetallicSpecGloss(uv, albedoAlpha.a);
    outSurfaceData.metallic = specGloss.r;
    outSurfaceData.specular = half3(0.0h, 0.0h, 0.0h);
    outSurfaceData.smoothness = specGloss.a;
    
    outSurfaceData.normalTS = SampleNormal(uv, detailUV, TEXTURE2D_ARGS(_BumpMap, sampler_BumpMap), _BumpScale);
    outSurfaceData.occlusion = SampleOcclusion(uv);
    outSurfaceData.emission = SampleEmission(uv, _EmissionColor.rgb, TEXTURE2D_ARGS(_EmissionMap, sampler_EmissionMap));
    
    // Advanced features
    #if defined(_CLEARCOAT)
        outSurfaceData.clearCoatMask = _ClearCoat;
        outSurfaceData.clearCoatSmoothness = _ClearCoatSmoothness;
    #else
        outSurfaceData.clearCoatMask = 0.0h;
        outSurfaceData.clearCoatSmoothness = 0.0h;
    #endif
    
    #if defined(_SUBSURFACE)
        outSurfaceData.subsurfaceColor = _SSSColor.rgb;
        outSurfaceData.subsurfacePower = _SSSPower;
    #else
        outSurfaceData.subsurfaceColor = half3(0.0h, 0.0h, 0.0h);
        outSurfaceData.subsurfacePower = 0.0h;
    #endif
}

#endif
```

### Compute Shader for Advanced Effects

```hlsl
// AdvancedEffectsCompute.compute
#pragma kernel CSParticleUpdate
#pragma kernel CSFluidSimulation
#pragma kernel CSCelluarAutomata
#pragma kernel CSPerlinNoise3D

#include "UnityCG.cginc"

// Shared constants
static const uint THREAD_GROUP_SIZE = 64;
static const float PI = 3.14159265f;
static const float TWO_PI = 6.28318531f;

// Particle system compute shader
struct Particle
{
    float3 position;
    float3 velocity;
    float3 acceleration;
    float life;
    float size;
    float4 color;
    uint isActive;
};

// Fluid simulation data
struct FluidParticle
{
    float3 position;
    float3 velocity;
    float density;
    float pressure;
    float mass;
};

// Noise generation data
struct NoiseData
{
    float3 position;
    float value;
    float3 gradient;
};

// Buffers
RWStructuredBuffer<Particle> _ParticleBuffer;
RWStructuredBuffer<FluidParticle> _FluidBuffer;
RWStructuredBuffer<uint> _CellularBuffer;
RWStructuredBuffer<NoiseData> _NoiseBuffer;

// Particle system parameters
float _DeltaTime;
float3 _Gravity;
float3 _WindForce;
float _Damping;
uint _ParticleCount;
float _EmissionRate;
float3 _EmitterPosition;
float3 _EmitterVelocity;
float _ParticleLifetime;

// Fluid simulation parameters
float _SmoothingRadius;
float _RestDensity;
float _Stiffness;
float _Viscosity;
uint _FluidParticleCount;

// Cellular automata parameters
uint _GridWidth;
uint _GridHeight;
uint _GridDepth;
uint _Rule;

// Noise parameters
uint _NoiseWidth;
uint _NoiseHeight;
uint _NoiseDepth;
float _NoiseScale;
float _TimeOffset;
int _Octaves;
float _Persistence;

// Utility functions
float random(float2 st)
{
    return frac(sin(dot(st.xy, float2(12.9898, 78.233))) * 43758.5453123);
}

float3 random3(float3 st)
{
    st = float3(dot(st, float3(127.1, 311.7, 74.7)),
                dot(st, float3(269.5, 183.3, 246.1)),
                dot(st, float3(113.5, 271.9, 124.6)));
    return -1.0 + 2.0 * frac(sin(st) * 43758.5453123);
}

// 3D Perlin noise function
float perlin3D(float3 p)
{
    float3 pi = floor(p);
    float3 pf = p - pi;
    
    // Fade curves
    float3 w = pf * pf * (3.0 - 2.0 * pf);
    
    // Interpolate gradients
    return lerp(
        lerp(
            lerp(dot(random3(pi + float3(0, 0, 0)), pf - float3(0, 0, 0)),
                 dot(random3(pi + float3(1, 0, 0)), pf - float3(1, 0, 0)), w.x),
            lerp(dot(random3(pi + float3(0, 1, 0)), pf - float3(0, 1, 0)),
                 dot(random3(pi + float3(1, 1, 0)), pf - float3(1, 1, 0)), w.x), w.y),
        lerp(
            lerp(dot(random3(pi + float3(0, 0, 1)), pf - float3(0, 0, 1)),
                 dot(random3(pi + float3(1, 0, 1)), pf - float3(1, 0, 1)), w.x),
            lerp(dot(random3(pi + float3(0, 1, 1)), pf - float3(0, 1, 1)),
                 dot(random3(pi + float3(1, 1, 1)), pf - float3(1, 1, 1)), w.x), w.y), w.z);
}

// Fractal Brownian Motion
float fbm(float3 p, int octaves, float persistence)
{
    float value = 0.0;
    float amplitude = 0.5;
    float frequency = 1.0;
    
    for (int i = 0; i < octaves; i++)
    {
        value += amplitude * perlin3D(p * frequency);
        amplitude *= persistence;
        frequency *= 2.0;
    }
    
    return value;
}

// SPH kernel functions
float SpikyKernel(float distance, float radius)
{
    if (distance >= radius) return 0.0f;
    
    float x = 1.0f - distance / radius;
    return 15.0f / (PI * pow(radius, 6)) * x * x * x;
}

float SpikyKernelDerivative(float distance, float radius)
{
    if (distance >= radius) return 0.0f;
    
    float x = 1.0f - distance / radius;
    return -45.0f / (PI * pow(radius, 6)) * x * x;
}

float ViscosityKernel(float distance, float radius)
{
    if (distance >= radius) return 0.0f;
    
    return 45.0f / (PI * pow(radius, 6)) * (radius - distance);
}

// Particle system update kernel
[numthreads(THREAD_GROUP_SIZE, 1, 1)]
void CSParticleUpdate(uint3 id : SV_DispatchThreadID)
{
    uint index = id.x;
    if (index >= _ParticleCount) return;
    
    Particle particle = _ParticleBuffer[index];
    
    if (particle.isActive == 0) return;
    
    // Update particle physics
    particle.acceleration = _Gravity + _WindForce;
    particle.velocity += particle.acceleration * _DeltaTime;
    particle.velocity *= _Damping;
    particle.position += particle.velocity * _DeltaTime;
    
    // Update particle life
    particle.life -= _DeltaTime;
    
    // Fade out color based on life
    float lifeRatio = particle.life / _ParticleLifetime;
    particle.color.a = lifeRatio;
    
    // Deactivate if life expired
    if (particle.life <= 0.0f)
    {
        particle.isActive = 0;
    }
    
    // Ground collision (simple)
    if (particle.position.y < 0.0f)
    {
        particle.position.y = 0.0f;
        particle.velocity.y = -particle.velocity.y * 0.5f; // Bounce with energy loss
    }
    
    _ParticleBuffer[index] = particle;
}

// Fluid simulation kernel using SPH
[numthreads(THREAD_GROUP_SIZE, 1, 1)]
void CSFluidSimulation(uint3 id : SV_DispatchThreadID)
{
    uint index = id.x;
    if (index >= _FluidParticleCount) return;
    
    FluidParticle particle = _FluidBuffer[index];
    
    // Calculate density and pressure
    float density = 0.0f;
    float3 pressureForce = float3(0, 0, 0);
    float3 viscosityForce = float3(0, 0, 0);
    
    // Iterate through all other particles for SPH calculation
    for (uint i = 0; i < _FluidParticleCount; i++)
    {
        if (i == index) continue;
        
        FluidParticle neighbor = _FluidBuffer[i];
        float3 diff = particle.position - neighbor.position;
        float distance = length(diff);
        
        if (distance < _SmoothingRadius)
        {
            // Density calculation
            density += neighbor.mass * SpikyKernel(distance, _SmoothingRadius);
            
            // Pressure force calculation
            if (distance > 0)
            {
                float3 direction = diff / distance;
                float pressureValue = (particle.pressure + neighbor.pressure) / (2.0f * neighbor.density);
                pressureForce += -neighbor.mass * pressureValue * SpikyKernelDerivative(distance, _SmoothingRadius) * direction;
                
                // Viscosity force calculation
                float3 velocityDiff = neighbor.velocity - particle.velocity;
                viscosityForce += _Viscosity * neighbor.mass * velocityDiff / neighbor.density * ViscosityKernel(distance, _SmoothingRadius);
            }
        }
    }
    
    // Update particle properties
    particle.density = max(density, _RestDensity);
    particle.pressure = _Stiffness * (particle.density - _RestDensity);
    
    // Apply forces
    float3 totalForce = pressureForce + viscosityForce + _Gravity;
    float3 acceleration = totalForce / particle.density;
    
    // Update velocity and position
    particle.velocity += acceleration * _DeltaTime;
    particle.position += particle.velocity * _DeltaTime;
    
    // Simple boundary conditions
    float3 minBounds = float3(-10, 0, -10);
    float3 maxBounds = float3(10, 20, 10);
    
    if (particle.position.x < minBounds.x || particle.position.x > maxBounds.x)
        particle.velocity.x *= -0.5f;
    if (particle.position.y < minBounds.y || particle.position.y > maxBounds.y)
        particle.velocity.y *= -0.5f;
    if (particle.position.z < minBounds.z || particle.position.z > maxBounds.z)
        particle.velocity.z *= -0.5f;
    
    particle.position = clamp(particle.position, minBounds, maxBounds);
    
    _FluidBuffer[index] = particle;
}

// 3D Cellular automata kernel
[numthreads(4, 4, 4)]
void CSCelluarAutomata(uint3 id : SV_DispatchThreadID)
{
    if (id.x >= _GridWidth || id.y >= _GridHeight || id.z >= _GridDepth)
        return;
    
    uint index = id.x + id.y * _GridWidth + id.z * _GridWidth * _GridHeight;
    uint currentState = _CellularBuffer[index];
    
    // Count neighbors in 3x3x3 neighborhood
    uint neighborCount = 0;
    
    for (int dx = -1; dx <= 1; dx++)
    {
        for (int dy = -1; dy <= 1; dy++)
        {
            for (int dz = -1; dz <= 1; dz++)
            {
                if (dx == 0 && dy == 0 && dz == 0) continue;
                
                int nx = (int)id.x + dx;
                int ny = (int)id.y + dy;
                int nz = (int)id.z + dz;
                
                if (nx >= 0 && nx < (int)_GridWidth &&
                    ny >= 0 && ny < (int)_GridHeight &&
                    nz >= 0 && nz < (int)_GridDepth)
                {
                    uint neighborIndex = nx + ny * _GridWidth + nz * _GridWidth * _GridHeight;
                    neighborCount += _CellularBuffer[neighborIndex];
                }
            }
        }
    }
    
    // Apply Conway's Game of Life rules in 3D
    uint newState = 0;
    if (currentState == 1)
    {
        // Cell is alive
        if (neighborCount >= 4 && neighborCount <= 5)
            newState = 1; // Survive
    }
    else
    {
        // Cell is dead
        if (neighborCount == 4)
            newState = 1; // Birth
    }
    
    _CellularBuffer[index] = newState;
}

// 3D Perlin noise generation kernel
[numthreads(4, 4, 4)]
void CSPerlinNoise3D(uint3 id : SV_DispatchThreadID)
{
    if (id.x >= _NoiseWidth || id.y >= _NoiseHeight || id.z >= _NoiseDepth)
        return;
    
    uint index = id.x + id.y * _NoiseWidth + id.z * _NoiseWidth * _NoiseHeight;
    
    // Calculate 3D position in noise space
    float3 position = float3(id.x, id.y, id.z) / float3(_NoiseWidth, _NoiseHeight, _NoiseDepth) * _NoiseScale;
    position += _TimeOffset; // Animate the noise
    
    // Generate fractal Brownian motion
    float noiseValue = fbm(position, _Octaves, _Persistence);
    
    // Calculate gradient for normal mapping
    float epsilon = 0.01f;
    float3 gradient;
    gradient.x = fbm(position + float3(epsilon, 0, 0), _Octaves, _Persistence) - noiseValue;
    gradient.y = fbm(position + float3(0, epsilon, 0), _Octaves, _Persistence) - noiseValue;
    gradient.z = fbm(position + float3(0, 0, epsilon), _Octaves, _Persistence) - noiseValue;
    gradient = normalize(gradient / epsilon);
    
    NoiseData data;
    data.position = position;
    data.value = noiseValue;
    data.gradient = gradient;
    
    _NoiseBuffer[index] = data;
}
```

### Shader Performance Manager

```csharp
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using System.Collections.Generic;
using System.Linq;

public class ShaderPerformanceManager : MonoBehaviour
{
    [Header("Performance Monitoring")]
    [SerializeField] private bool enablePerformanceMonitoring = true;
    [SerializeField] private float monitoringInterval = 1f;
    [SerializeField] private int maxShaderVariants = 256;
    
    [Header("Quality Settings")]
    [SerializeField] private ShaderQualityLevel targetQuality = ShaderQualityLevel.High;
    [SerializeField] private bool adaptiveQuality = true;
    [SerializeField] private float targetFrameTime = 16.67f; // 60 FPS
    
    [Header("Shader Variants")]
    [SerializeField] private ShaderVariantCollection shaderVariantCollection;
    [SerializeField] private bool preloadShaders = true;
    
    // Performance tracking
    private Dictionary<Shader, ShaderPerformanceData> shaderPerformance;
    private List<Material> trackedMaterials;
    private FramePerformanceData currentFrame;
    
    // Quality management
    private int currentQualityLevel;
    private float averageFrameTime;
    private Queue<float> frameTimes;
    private const int frameHistorySize = 60;
    
    [System.Serializable]
    public struct ShaderPerformanceData
    {
        public string shaderName;
        public int variantCount;
        public float averageRenderTime;
        public long memoryUsage;
        public int drawCalls;
        public bool isOptimized;
        public List<string> optimizationSuggestions;
    }
    
    [System.Serializable]
    public struct FramePerformanceData
    {
        public float frameTime;
        public int totalDrawCalls;
        public int shaderSwitches;
        public float gpuTime;
        public Dictionary<Shader, float> shaderTimes;
    }
    
    public enum ShaderQualityLevel
    {
        Low = 0,
        Medium = 1,
        High = 2,
        Ultra = 3
    }
    
    void Start()
    {
        InitializeShaderPerformanceManager();
    }
    
    void InitializeShaderPerformanceManager()
    {
        shaderPerformance = new Dictionary<Shader, ShaderPerformanceData>();
        trackedMaterials = new List<Material>();
        frameTimes = new Queue<float>();
        currentQualityLevel = (int)targetQuality;
        
        // Find all materials in the scene
        DiscoverMaterials();
        
        // Preload shaders if requested
        if (preloadShaders && shaderVariantCollection != null)
        {
            PreloadShaderVariants();
        }
        
        // Start performance monitoring
        if (enablePerformanceMonitoring)
        {
            InvokeRepeating(nameof(MonitorShaderPerformance), 0f, monitoringInterval);
        }
        
        // Setup render pipeline callbacks
        RenderPipelineManager.beginCameraRendering += OnBeginCameraRendering;
        RenderPipelineManager.endCameraRendering += OnEndCameraRendering;
    }
    
    void DiscoverMaterials()
    {
        // Find all renderers in the scene
        var renderers = FindObjectsOfType<Renderer>();
        
        foreach (var renderer in renderers)
        {
            foreach (var material in renderer.materials)
            {
                if (material != null && !trackedMaterials.Contains(material))
                {
                    trackedMaterials.Add(material);
                    TrackShaderPerformance(material.shader);
                }
            }
        }
        
        Debug.Log($"ShaderPerformanceManager: Tracking {trackedMaterials.Count} materials with {shaderPerformance.Count} unique shaders");
    }
    
    void TrackShaderPerformance(Shader shader)
    {
        if (shader == null || shaderPerformance.ContainsKey(shader)) return;
        
        var performanceData = new ShaderPerformanceData
        {
            shaderName = shader.name,
            variantCount = GetShaderVariantCount(shader),
            averageRenderTime = 0f,
            memoryUsage = GetShaderMemoryUsage(shader),
            drawCalls = 0,
            isOptimized = IsShaderOptimized(shader),
            optimizationSuggestions = GenerateOptimizationSuggestions(shader)
        };
        
        shaderPerformance[shader] = performanceData;
    }
    
    void PreloadShaderVariants()
    {
        if (shaderVariantCollection == null) return;
        
        Debug.Log("Preloading shader variants...");
        shaderVariantCollection.WarmUp();
        
        // Additional warmup for tracked materials
        foreach (var material in trackedMaterials)
        {
            if (material != null)
            {
                // Force shader compilation by creating a temporary mesh renderer
                var go = new GameObject("TempShaderWarmup");
                go.hideFlags = HideFlags.HideAndDontSave;
                
                var meshRenderer = go.AddComponent<MeshRenderer>();
                var meshFilter = go.AddComponent<MeshFilter>();
                
                meshFilter.mesh = Resources.GetBuiltinResource<Mesh>("Quad.fbx");
                meshRenderer.material = material;
                
                // Render one frame to compile shader
                meshRenderer.enabled = true;
                meshRenderer.enabled = false;
                
                DestroyImmediate(go);
            }
        }
        
        Debug.Log("Shader variant preloading complete");
    }
    
    void MonitorShaderPerformance()
    {
        // Update frame time tracking
        frameTimes.Enqueue(Time.unscaledDeltaTime * 1000f); // Convert to milliseconds
        if (frameTimes.Count > frameHistorySize)
        {
            frameTimes.Dequeue();
        }
        
        averageFrameTime = frameTimes.Average();
        
        // Adaptive quality adjustment
        if (adaptiveQuality)
        {
            AdjustQualityBasedOnPerformance();
        }
        
        // Update shader performance metrics
        UpdateShaderMetrics();
        
        // Log performance warnings
        CheckPerformanceWarnings();
    }
    
    void AdjustQualityBasedOnPerformance()
    {
        const float performanceThreshold = 1.1f; // 10% tolerance
        
        if (averageFrameTime > targetFrameTime * performanceThreshold)
        {
            // Performance is below target, reduce quality
            if (currentQualityLevel > 0)
            {
                currentQualityLevel--;
                ApplyQualitySettings(currentQualityLevel);
                Debug.LogWarning($"Shader quality reduced to level {currentQualityLevel} due to performance: {averageFrameTime:F2}ms");
            }
        }
        else if (averageFrameTime < targetFrameTime * 0.8f) // 20% better than target
        {
            // Performance is good, can increase quality
            if (currentQualityLevel < 3)
            {
                currentQualityLevel++;
                ApplyQualitySettings(currentQualityLevel);
                Debug.Log($"Shader quality increased to level {currentQualityLevel}");
            }
        }
    }
    
    void ApplyQualitySettings(int qualityLevel)
    {
        foreach (var material in trackedMaterials)
        {
            if (material == null) continue;
            
            // Apply quality-specific shader keywords
            switch (qualityLevel)
            {
                case 0: // Low quality
                    material.DisableKeyword("_QUALITY_MEDIUM");
                    material.DisableKeyword("_QUALITY_HIGH");
                    material.EnableKeyword("_QUALITY_LOW");
                    break;
                case 1: // Medium quality
                    material.DisableKeyword("_QUALITY_LOW");
                    material.DisableKeyword("_QUALITY_HIGH");
                    material.EnableKeyword("_QUALITY_MEDIUM");
                    break;
                case 2: // High quality
                    material.DisableKeyword("_QUALITY_LOW");
                    material.DisableKeyword("_QUALITY_MEDIUM");
                    material.EnableKeyword("_QUALITY_HIGH");
                    break;
                case 3: // Ultra quality
                    material.DisableKeyword("_QUALITY_LOW");
                    material.DisableKeyword("_QUALITY_MEDIUM");
                    material.DisableKeyword("_QUALITY_HIGH");
                    // Ultra uses all features enabled
                    break;
            }
        }
    }
    
    void UpdateShaderMetrics()
    {
        // Update performance metrics for each tracked shader
        foreach (var kvp in shaderPerformance.ToArray())
        {
            var shader = kvp.Key;
            var data = kvp.Value;
            
            // Count materials using this shader
            int materialCount = trackedMaterials.Count(m => m != null && m.shader == shader);
            
            // Estimate render time based on complexity
            data.averageRenderTime = EstimateShaderRenderTime(shader, materialCount);
            
            // Update optimization status
            data.isOptimized = IsShaderOptimized(shader);
            
            shaderPerformance[shader] = data;
        }
    }
    
    void CheckPerformanceWarnings()
    {
        // Check for performance issues
        foreach (var kvp in shaderPerformance)
        {
            var shader = kvp.Key;
            var data = kvp.Value;
            
            if (data.variantCount > maxShaderVariants)
            {
                Debug.LogWarning($"Shader '{data.shaderName}' has {data.variantCount} variants (limit: {maxShaderVariants})");
            }
            
            if (!data.isOptimized)
            {
                Debug.LogWarning($"Shader '{data.shaderName}' is not optimized. Suggestions: {string.Join(", ", data.optimizationSuggestions)}");
            }
        }
    }
    
    int GetShaderVariantCount(Shader shader)
    {
        // Estimate based on shader keywords and passes
        var serializedShader = new SerializedObject(shader);
        var passCount = 1; // Default estimate
        
        // This is a simplified estimation - actual variant count depends on keyword combinations
        var keywords = shader.keywordSpace.keywordNames;
        int estimatedVariants = Mathf.Max(1, 1 << Mathf.Min(keywords.Length, 10)); // Limit estimation
        
        return estimatedVariants * passCount;
    }
    
    long GetShaderMemoryUsage(Shader shader)
    {
        // Estimate memory usage based on shader complexity
        return Profiler.GetRuntimeMemorySizeLong(shader);
    }
    
    bool IsShaderOptimized(Shader shader)
    {
        if (shader == null) return false;
        
        // Check for common optimization indicators
        bool hasLOD = shader.maximumLOD < 600; // Standard shaders have LOD 300-600
        bool hasBurstedVariants = shader.name.Contains("Burst") || shader.name.Contains("GPU");
        bool hasMinimalKeywords = shader.keywordSpace.keywordNames.Length < 20;
        
        return hasLOD && hasMinimalKeywords;
    }
    
    List<string> GenerateOptimizationSuggestions(Shader shader)
    {
        var suggestions = new List<string>();
        
        if (shader == null) return suggestions;
        
        // Analyze shader for optimization opportunities
        int keywordCount = shader.keywordSpace.keywordNames.Length;
        if (keywordCount > 15)
        {
            suggestions.Add("Reduce shader keyword count to minimize variants");
        }
        
        if (shader.maximumLOD > 400)
        {
            suggestions.Add("Consider implementing LOD system for complex shaders");
        }
        
        if (shader.name.Contains("Standard") || shader.name.Contains("URP/Lit"))
        {
            suggestions.Add("Consider custom optimized shader for specific use cases");
        }
        
        return suggestions;
    }
    
    float EstimateShaderRenderTime(Shader shader, int materialCount)
    {
        // Simplified estimation based on shader complexity and usage
        float baseTime = 0.1f; // Base render time in ms
        float complexityMultiplier = shader.maximumLOD / 300f; // Normalize to standard shader LOD
        float usageMultiplier = Mathf.Sqrt(materialCount); // More materials = more render time
        
        return baseTime * complexityMultiplier * usageMultiplier;
    }
    
    void OnBeginCameraRendering(ScriptableRenderContext context, Camera camera)
    {
        if (!enablePerformanceMonitoring) return;
        
        currentFrame = new FramePerformanceData
        {
            frameTime = Time.unscaledDeltaTime * 1000f,
            shaderTimes = new Dictionary<Shader, float>()
        };
    }
    
    void OnEndCameraRendering(ScriptableRenderContext context, Camera camera)
    {
        if (!enablePerformanceMonitoring) return;
        
        // Finalize frame data
        currentFrame.gpuTime = GetGPUTime();
    }
    
    float GetGPUTime()
    {
        // Get GPU time from Unity's profiler
        return Profiler.GetCounterValue(ProfilerCounter.GPUTime) / 1000000f; // Convert to milliseconds
    }
    
    public ShaderPerformanceData GetShaderPerformance(Shader shader)
    {
        return shaderPerformance.TryGetValue(shader, out var data) ? data : new ShaderPerformanceData();
    }
    
    public Dictionary<Shader, ShaderPerformanceData> GetAllShaderPerformance()
    {
        return new Dictionary<Shader, ShaderPerformanceData>(shaderPerformance);
    }
    
    public void SetQualityLevel(ShaderQualityLevel quality)
    {
        targetQuality = quality;
        currentQualityLevel = (int)quality;
        ApplyQualitySettings(currentQualityLevel);
    }
    
    void OnDestroy()
    {
        RenderPipelineManager.beginCameraRendering -= OnBeginCameraRendering;
        RenderPipelineManager.endCameraRendering -= OnEndCameraRendering;
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Automated Shader Generation

```
Generate optimized Unity shaders for specific use cases:
1. Performance-optimized mobile shaders with automatic LOD systems
2. Advanced material shaders with PBR and custom lighting models
3. Compute shader systems for particle effects and fluid simulation
4. Custom post-processing effects with temporal filtering

Context: Unity URP/HDRP development with performance requirements
Focus: Production-ready shaders, cross-platform optimization, artistic control
Requirements: Shader Graph compatibility, maintainable HLSL code
```

### Shader Performance Analysis

```
Create intelligent shader optimization tools:
1. Automated shader variant analysis and optimization recommendations
2. Performance bottleneck identification with specific fixes
3. Dynamic quality scaling systems based on hardware capabilities
4. Shader compilation time optimization and caching strategies

Environment: Unity 2022.3 LTS with Universal Render Pipeline
Goals: Optimal performance, reduced compilation times, automated optimization
```

This comprehensive shader development system provides advanced tools for creating high-performance, visually impressive shaders with automated optimization and performance monitoring capabilities.