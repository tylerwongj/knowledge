# @18-Particle-System-Manager

## 🎯 Core Concept
Automated particle system creation and effect management for visual consistency.

## 🔧 Implementation

### Particle Effect Factory
```csharp
using UnityEngine;
using UnityEditor;

public class ParticleEffectFactory
{
    [MenuItem("Tools/Effects/Create Fire Effect")]
    public static void CreateFireEffect()
    {
        GameObject fireEffect = new GameObject("Fire Effect");
        ParticleSystem ps = fireEffect.AddComponent<ParticleSystem>();
        
        var main = ps.main;
        main.startLifetime = 2f;
        main.startSpeed = 5f;
        main.startSize = 0.5f;
        main.startColor = Color.red;
        main.maxParticles = 100;
        
        var emission = ps.emission;
        emission.rateOverTime = 50;
        
        var shape = ps.shape;
        shape.shapeType = ParticleSystemShapeType.Circle;
        shape.radius = 0.5f;
        
        var velocityOverLifetime = ps.velocityOverLifetime;
        velocityOverLifetime.enabled = true;
        velocityOverLifetime.space = ParticleSystemSimulationSpace.Local;
        velocityOverLifetime.y = new ParticleSystem.MinMaxCurve(2f, 8f);
        
        var colorOverLifetime = ps.colorOverLifetime;
        colorOverLifetime.enabled = true;
        Gradient gradient = new Gradient();
        gradient.SetKeys(
            new GradientColorKey[] { new GradientColorKey(Color.red, 0f), new GradientColorKey(Color.yellow, 0.5f), new GradientColorKey(Color.black, 1f) },
            new GradientAlphaKey[] { new GradientAlphaKey(1f, 0f), new GradientAlphaKey(1f, 0.5f), new GradientAlphaKey(0f, 1f) }
        );
        colorOverLifetime.color = gradient;
        
        Debug.Log("Fire effect created");
    }
    
    [MenuItem("Tools/Effects/Optimize All Particle Systems")]
    public static void OptimizeParticleSystems()
    {
        ParticleSystem[] particleSystems = Object.FindObjectsOfType<ParticleSystem>();
        
        foreach (var ps in particleSystems)
        {
            var main = ps.main;
            if (main.maxParticles > 1000)
            {
                main.maxParticles = 1000;
                Debug.Log($"Optimized particle count for {ps.name}");
            }
            
            var emission = ps.emission;
            if (emission.rateOverTime.constant > 100)
            {
                emission.rateOverTime = 100;
                Debug.Log($"Optimized emission rate for {ps.name}");
            }
        }
    }
}
```

## 🚀 AI/LLM Integration
- Generate particle effects based on descriptions
- Automatically optimize performance settings
- Create themed effect collections

## 💡 Key Benefits
- Consistent visual effects across the game
- Automated performance optimization
- Rapid effect prototyping