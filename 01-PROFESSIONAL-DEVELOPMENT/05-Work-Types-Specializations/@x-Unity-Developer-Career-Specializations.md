# @x-Unity-Developer-Career-Specializations

## 🎯 Learning Objectives

- Master specialized Unity development career paths and technical expertise areas
- Develop deep domain knowledge for specific Unity development roles
- Create compelling portfolios and expertise demonstrations for specialized positions
- Build strategic career progression plans within Unity development specializations

## 🔧 Core Unity Developer Specializations

### Gameplay Programmer Specialization

```csharp
using UnityEngine;
using System.Collections.Generic;
using Unity.Mathematics;

/// <summary>
/// Advanced gameplay programming patterns for specialized gameplay programmers.
/// Demonstrates complex game mechanics implementation and design patterns.
/// </summary>
public class AdvancedGameplaySystem : MonoBehaviour
{
    [System.Serializable]
    public class PlayerAbilitySystem
    {
        public enum AbilityType
        {
            Active,      // Player-triggered abilities
            Passive,     // Always-active abilities
            Reactive,    // Trigger-based abilities
            Conditional  // State-dependent abilities
        }

        [System.Serializable]
        public class Ability
        {
            public string name;
            public AbilityType type;
            public float cooldown;
            public float duration;
            public float manaCost;
            public List<Effect> effects;
            public List<string> requirements;
            public AnimationClip animation;
            public AudioClip sound;
            
            [System.NonSerialized]
            public float lastUsedTime;
            [System.NonSerialized]
            public bool isActive;
        }

        [System.Serializable]
        public class Effect
        {
            public string effectType;
            public float magnitude;
            public float duration;
            public AnimationCurve falloffCurve;
            public bool stackable;
            public int maxStacks;
        }

        private Dictionary<string, Ability> abilities = new Dictionary<string, Ability>();
        private List<Effect> activeEffects = new List<Effect>();

        public bool TryUseAbility(string abilityName, GameObject target = null)
        {
            if (!abilities.TryGetValue(abilityName, out Ability ability))
            {
                Debug.LogWarning($"Ability {abilityName} not found");
                return false;
            }

            // Check cooldown
            if (Time.time - ability.lastUsedTime < ability.cooldown)
            {
                Debug.Log($"Ability {abilityName} is on cooldown");
                return false;
            }

            // Check mana/resources
            if (!HasSufficientResources(ability.manaCost))
            {
                Debug.Log($"Insufficient resources for {abilityName}");
                return false;
            }

            // Execute ability
            ExecuteAbility(ability, target);
            ability.lastUsedTime = Time.time;
            
            return true;
        }

        private void ExecuteAbility(Ability ability, GameObject target)
        {
            // Play animation
            if (ability.animation != null)
            {
                // Trigger animation system
                var animator = GetComponent<Animator>();
                animator?.Play(ability.animation.name);
            }

            // Play sound
            if (ability.sound != null)
            {
                AudioSource.PlayClipAtPoint(ability.sound, transform.position);
            }

            // Apply effects
            foreach (var effect in ability.effects)
            {
                ApplyEffect(effect, target);
            }
        }

        private void ApplyEffect(Effect effect, GameObject target)
        {
            // Complex effect system implementation
            switch (effect.effectType.ToLower())
            {
                case "damage":
                    ApplyDamageEffect(effect, target);
                    break;
                case "heal":
                    ApplyHealingEffect(effect, target);
                    break;
                case "buff":
                    ApplyBuffEffect(effect, target);
                    break;
                case "debuff":
                    ApplyDebuffEffect(effect, target);
                    break;
                default:
                    Debug.LogWarning($"Unknown effect type: {effect.effectType}");
                    break;
            }
        }

        private void ApplyDamageEffect(Effect effect, GameObject target)
        {
            if (target?.GetComponent<Health>() is Health health)
            {
                float damage = effect.magnitude;
                
                // Apply falloff curve if specified
                if (effect.falloffCurve != null && effect.falloffCurve.keys.Length > 0)
                {
                    float distance = Vector3.Distance(transform.position, target.transform.position);
                    float falloffMultiplier = effect.falloffCurve.Evaluate(distance);
                    damage *= falloffMultiplier;
                }

                health.TakeDamage(damage);
            }
        }

        private void ApplyHealingEffect(Effect effect, GameObject target)
        {
            if (target?.GetComponent<Health>() is Health health)
            {
                health.Heal(effect.magnitude);
            }
        }

        private void ApplyBuffEffect(Effect effect, GameObject target)
        {
            // Add to active effects for duration-based management
            var buffEffect = new Effect
            {
                effectType = effect.effectType,
                magnitude = effect.magnitude,
                duration = effect.duration,
                falloffCurve = effect.falloffCurve
            };

            activeEffects.Add(buffEffect);
            StartCoroutine(RemoveEffectAfterDuration(buffEffect, effect.duration));
        }

        private void ApplyDebuffEffect(Effect effect, GameObject target)
        {
            // Similar to buff but with negative effects
            ApplyBuffEffect(effect, target); // Reuse buff logic with different effect type
        }

        private System.Collections.IEnumerator RemoveEffectAfterDuration(Effect effect, float duration)
        {
            yield return new WaitForSeconds(duration);
            activeEffects.Remove(effect);
        }

        private bool HasSufficientResources(float cost)
        {
            // Check player resources (mana, stamina, etc.)
            var resourceManager = GetComponent<ResourceManager>();
            return resourceManager?.HasResource("mana", cost) ?? true;
        }
    }

    [System.Serializable]
    public class AdvancedStateMachine
    {
        public interface IState
        {
            void Enter();
            void Update();
            void Exit();
            bool CanTransitionTo(System.Type stateType);
        }

        public abstract class BaseState : IState
        {
            protected AdvancedStateMachine stateMachine;
            protected float stateTime;

            public BaseState(AdvancedStateMachine machine)
            {
                stateMachine = machine;
            }

            public virtual void Enter()
            {
                stateTime = 0f;
            }

            public virtual void Update()
            {
                stateTime += Time.deltaTime;
            }

            public virtual void Exit() { }

            public virtual bool CanTransitionTo(System.Type stateType)
            {
                return true; // Override in specific states for restrictions
            }
        }

        private IState currentState;
        private Dictionary<System.Type, IState> states = new Dictionary<System.Type, IState>();
        private MonoBehaviour owner;

        public AdvancedStateMachine(MonoBehaviour owner)
        {
            this.owner = owner;
        }

        public void RegisterState<T>(T state) where T : IState
        {
            states[typeof(T)] = state;
        }

        public void ChangeState<T>() where T : IState
        {
            if (states.TryGetValue(typeof(T), out IState newState))
            {
                if (currentState?.CanTransitionTo(typeof(T)) ?? true)
                {
                    currentState?.Exit();
                    currentState = newState;
                    currentState.Enter();
                }
            }
        }

        public void Update()
        {
            currentState?.Update();
        }

        public T GetCurrentState<T>() where T : class, IState
        {
            return currentState as T;
        }
    }

    // Combat system specialized for gameplay programmers
    [System.Serializable]
    public class AdvancedCombatSystem
    {
        public enum DamageType
        {
            Physical,
            Magical,
            Fire,
            Ice,
            Lightning,
            Poison,
            True // Ignores resistance
        }

        [System.Serializable]
        public class DamageInfo
        {
            public float amount;
            public DamageType type;
            public GameObject source;
            public Vector3 hitPoint;
            public Vector3 hitDirection;
            public bool isCritical;
            public float criticalMultiplier;
        }

        [System.Serializable]
        public class CombatStats
        {
            public float attackPower;
            public float defense;
            public float criticalChance;
            public float criticalMultiplier;
            public Dictionary<DamageType, float> resistances;
            public Dictionary<DamageType, float> weaknesses;

            public CombatStats()
            {
                resistances = new Dictionary<DamageType, float>();
                weaknesses = new Dictionary<DamageType, float>();
            }
        }

        public static float CalculateDamage(DamageInfo damage, CombatStats targetStats)
        {
            float finalDamage = damage.amount;

            // Apply critical hit
            if (damage.isCritical)
            {
                finalDamage *= damage.criticalMultiplier;
            }

            // Apply resistance/weakness
            if (targetStats.resistances.ContainsKey(damage.type))
            {
                finalDamage *= (1f - targetStats.resistances[damage.type]);
            }

            if (targetStats.weaknesses.ContainsKey(damage.type))
            {
                finalDamage *= (1f + targetStats.weaknesses[damage.type]);
            }

            // Apply defense (except for true damage)
            if (damage.type != DamageType.True)
            {
                finalDamage = Mathf.Max(0, finalDamage - targetStats.defense);
            }

            return finalDamage;
        }

        public static bool RollCriticalHit(float criticalChance)
        {
            return UnityEngine.Random.Range(0f, 1f) < criticalChance;
        }
    }
}

// Specialized component for gameplay programmers
public class Health : MonoBehaviour
{
    [SerializeField] private float maxHealth = 100f;
    [SerializeField] private float currentHealth;
    [SerializeField] private bool canRegenerate = true;
    [SerializeField] private float regenerationRate = 1f;

    public System.Action<float, float> OnHealthChanged; // current, max
    public System.Action OnDeath;

    void Start()
    {
        currentHealth = maxHealth;
    }

    public void TakeDamage(float amount)
    {
        currentHealth = Mathf.Max(0, currentHealth - amount);
        OnHealthChanged?.Invoke(currentHealth, maxHealth);

        if (currentHealth <= 0)
        {
            OnDeath?.Invoke();
        }
    }

    public void Heal(float amount)
    {
        currentHealth = Mathf.Min(maxHealth, currentHealth + amount);
        OnHealthChanged?.Invoke(currentHealth, maxHealth);
    }
}

public class ResourceManager : MonoBehaviour
{
    [System.Serializable]
    public class Resource
    {
        public string name;
        public float current;
        public float maximum;
        public float regenerationRate;
    }

    [SerializeField] private List<Resource> resources = new List<Resource>();

    public bool HasResource(string resourceName, float amount)
    {
        var resource = resources.Find(r => r.name == resourceName);
        return resource != null && resource.current >= amount;
    }

    public bool ConsumeResource(string resourceName, float amount)
    {
        var resource = resources.Find(r => r.name == resourceName);
        if (resource != null && resource.current >= amount)
        {
            resource.current -= amount;
            return true;
        }
        return false;
    }
}
```

### Graphics Programmer Specialization

```csharp
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Unity.Mathematics;

/// <summary>
/// Advanced graphics programming techniques for specialized graphics programmers.
/// Includes custom render pipelines, shaders, and visual effects systems.
/// </summary>
public class AdvancedGraphicsSystem : MonoBehaviour
{
    [System.Serializable]
    public class CustomRenderFeature : ScriptableRendererFeature
    {
        [System.Serializable]
        public class Settings
        {
            public RenderPassEvent renderPassEvent = RenderPassEvent.AfterRenderingOpaques;
            public Material material;
            public string profilerTag = "Custom Render Feature";
        }

        public Settings settings = new Settings();
        private CustomRenderPass renderPass;

        public override void Create()
        {
            renderPass = new CustomRenderPass(settings);
        }

        public override void AddRenderPasses(ScriptableRenderer renderer, ref RenderingData renderingData)
        {
            if (settings.material != null)
            {
                renderer.EnqueuePass(renderPass);
            }
        }

        private class CustomRenderPass : ScriptableRenderPass
        {
            private Settings settings;
            private RenderTargetIdentifier source;
            private RenderTargetHandle temporaryColorTexture;

            public CustomRenderPass(Settings settings)
            {
                this.settings = settings;
                renderPassEvent = settings.renderPassEvent;
                temporaryColorTexture.Init("_TemporaryColorTexture");
            }

            public override void Configure(CommandBuffer cmd, RenderTextureDescriptor cameraTextureDescriptor)
            {
                cmd.GetTemporaryRT(temporaryColorTexture.id, cameraTextureDescriptor);
            }

            public override void Execute(ScriptableRenderContext context, ref RenderingData renderingData)
            {
                CommandBuffer cmd = CommandBufferPool.Get(settings.profilerTag);

                RenderTextureDescriptor opaqueDescriptor = renderingData.cameraData.cameraTargetDescriptor;
                opaqueDescriptor.depthBufferBits = 0;

                if (renderingData.cameraData.camera.cameraType == CameraType.Game)
                {
                    source = renderingData.cameraData.renderer.cameraColorTarget;
                    
                    // Custom rendering logic here
                    Blit(cmd, source, temporaryColorTexture.Identifier(), settings.material);
                    Blit(cmd, temporaryColorTexture.Identifier(), source);
                }

                context.ExecuteCommandBuffer(cmd);
                CommandBufferPool.Release(cmd);
            }

            public override void FrameCleanup(CommandBuffer cmd)
            {
                cmd.ReleaseTemporaryRT(temporaryColorTexture.id);
            }
        }
    }

    [System.Serializable]
    public class AdvancedShaderController
    {
        [System.Serializable]
        public class ShaderProperty
        {
            public string name;
            public enum PropertyType { Float, Vector, Color, Texture }
            public PropertyType type;
            public Vector4 vectorValue;
            public Color colorValue;
            public float floatValue;
            public Texture textureValue;
        }

        public Material targetMaterial;
        public List<ShaderProperty> properties = new List<ShaderProperty>();
        
        private Dictionary<string, int> propertyIDs = new Dictionary<string, int>();

        public void Initialize()
        {
            // Cache property IDs for performance
            foreach (var property in properties)
            {
                propertyIDs[property.name] = Shader.PropertyToID(property.name);
            }
        }

        public void UpdateShaderProperties()
        {
            if (targetMaterial == null) return;

            foreach (var property in properties)
            {
                int propertyID = propertyIDs[property.name];
                
                switch (property.type)
                {
                    case ShaderProperty.PropertyType.Float:
                        targetMaterial.SetFloat(propertyID, property.floatValue);
                        break;
                    case ShaderProperty.PropertyType.Vector:
                        targetMaterial.SetVector(propertyID, property.vectorValue);
                        break;
                    case ShaderProperty.PropertyType.Color:
                        targetMaterial.SetColor(propertyID, property.colorValue);
                        break;
                    case ShaderProperty.PropertyType.Texture:
                        if (property.textureValue != null)
                            targetMaterial.SetTexture(propertyID, property.textureValue);
                        break;
                }
            }
        }

        // Advanced material property animation
        public void AnimateProperty(string propertyName, float targetValue, float duration, AnimationCurve curve = null)
        {
            var property = properties.Find(p => p.name == propertyName);
            if (property != null && property.type == ShaderProperty.PropertyType.Float)
            {
                var behaviour = targetMaterial.GetComponent<MonoBehaviour>();
                behaviour?.StartCoroutine(AnimateFloatProperty(property, targetValue, duration, curve));
            }
        }

        private System.Collections.IEnumerator AnimateFloatProperty(ShaderProperty property, float targetValue, float duration, AnimationCurve curve)
        {
            float startValue = property.floatValue;
            float elapsedTime = 0f;

            while (elapsedTime < duration)
            {
                elapsedTime += Time.deltaTime;
                float t = elapsedTime / duration;
                
                if (curve != null)
                    t = curve.Evaluate(t);

                property.floatValue = Mathf.Lerp(startValue, targetValue, t);
                UpdateShaderProperties();
                
                yield return null;
            }

            property.floatValue = targetValue;
            UpdateShaderProperties();
        }
    }

    // Advanced lighting system for graphics programmers
    [System.Serializable]
    public class DynamicLightingSystem
    {
        [System.Serializable]
        public class LightData
        {
            public Vector3 position;
            public Color color;
            public float intensity;
            public float range;
            public LightType type;
            public Vector3 direction; // For spotlights and directional lights
            public float spotAngle;   // For spotlights
            public AnimationCurve falloffCurve;
        }

        public List<LightData> dynamicLights = new List<LightData>();
        public ComputeShader lightingComputeShader;
        public RenderTexture lightingTexture;

        private ComputeBuffer lightBuffer;
        private int lightingKernel;

        public void Initialize()
        {
            if (lightingComputeShader != null)
            {
                lightingKernel = lightingComputeShader.FindKernel("CSMain");
                
                // Create render texture for lighting calculations
                lightingTexture = new RenderTexture(Screen.width, Screen.height, 0, RenderTextureFormat.ARGBFloat);
                lightingTexture.enableRandomWrite = true;
                lightingTexture.Create();
                
                // Initialize compute buffer for lights
                UpdateLightBuffer();
            }
        }

        public void UpdateLightBuffer()
        {
            if (lightBuffer != null)
            {
                lightBuffer.Release();
            }

            if (dynamicLights.Count > 0)
            {
                lightBuffer = new ComputeBuffer(dynamicLights.Count, sizeof(float) * 12); // Adjust size based on LightData
                lightBuffer.SetData(dynamicLights.ToArray());
            }
        }

        public void CalculateLighting()
        {
            if (lightingComputeShader == null || lightBuffer == null) return;

            lightingComputeShader.SetTexture(lightingKernel, "Result", lightingTexture);
            lightingComputeShader.SetBuffer(lightingKernel, "LightBuffer", lightBuffer);
            lightingComputeShader.SetInt("LightCount", dynamicLights.Count);
            
            int threadGroupsX = Mathf.CeilToInt(lightingTexture.width / 8.0f);
            int threadGroupsY = Mathf.CeilToInt(lightingTexture.height / 8.0f);
            
            lightingComputeShader.Dispatch(lightingKernel, threadGroupsX, threadGroupsY, 1);
        }

        public void Cleanup()
        {
            lightBuffer?.Release();
            if (lightingTexture != null)
            {
                lightingTexture.Release();
            }
        }
    }

    // Advanced post-processing system
    [System.Serializable]
    public class CustomPostProcessing
    {
        [System.Serializable]
        public class PostProcessEffect
        {
            public string name;
            public Material material;
            public bool enabled = true;
            public int renderOrder = 0;
            
            [System.Serializable]
            public class EffectParameter
            {
                public string parameterName;
                public float value;
                public float minValue;
                public float maxValue;
            }
            
            public List<EffectParameter> parameters = new List<EffectParameter>();
        }

        public List<PostProcessEffect> effects = new List<PostProcessEffect>();
        private RenderTexture[] temporaryTextures;

        public void ProcessEffects(RenderTexture source, RenderTexture destination)
        {
            var enabledEffects = effects.Where(e => e.enabled && e.material != null)
                                       .OrderBy(e => e.renderOrder)
                                       .ToArray();

            if (enabledEffects.Length == 0)
            {
                Graphics.Blit(source, destination);
                return;
            }

            // Create temporary textures for ping-pong rendering
            if (temporaryTextures == null || temporaryTextures.Length < 2)
            {
                temporaryTextures = new RenderTexture[2];
                for (int i = 0; i < 2; i++)
                {
                    temporaryTextures[i] = new RenderTexture(source.width, source.height, 0, source.format);
                    temporaryTextures[i].Create();
                }
            }

            RenderTexture currentSource = source;
            RenderTexture currentDestination = temporaryTextures[0];

            for (int i = 0; i < enabledEffects.Length; i++)
            {
                var effect = enabledEffects[i];
                
                // Update effect parameters
                foreach (var param in effect.parameters)
                {
                    effect.material.SetFloat(param.parameterName, param.value);
                }

                // Determine destination for this effect
                if (i == enabledEffects.Length - 1)
                {
                    // Last effect goes to final destination
                    currentDestination = destination;
                }
                else
                {
                    // Ping-pong between temporary textures
                    currentDestination = temporaryTextures[(i + 1) % 2];
                }

                Graphics.Blit(currentSource, currentDestination, effect.material);
                currentSource = currentDestination;
            }
        }

        public void Cleanup()
        {
            if (temporaryTextures != null)
            {
                foreach (var texture in temporaryTextures)
                {
                    if (texture != null)
                    {
                        texture.Release();
                    }
                }
            }
        }
    }
}
```

### Engine Programmer Specialization

```csharp
using UnityEngine;
using Unity.Collections;
using Unity.Jobs;
using Unity.Mathematics;
using System.Runtime.InteropServices;

/// <summary>
/// Advanced engine programming techniques for specialized engine programmers.
/// Includes low-level optimizations, custom systems, and performance-critical code.
/// </summary>
public class AdvancedEngineSystem : MonoBehaviour
{
    // Custom memory management system
    [System.Serializable]
    public unsafe class AdvancedMemoryManager
    {
        private struct MemoryBlock
        {
            public void* pointer;
            public int size;
            public bool isAllocated;
            public int alignmentOffset;
        }

        private byte* memoryPool;
        private int poolSize;
        private int currentOffset;
        private NativeList<MemoryBlock> blocks;

        public AdvancedMemoryManager(int poolSizeBytes, Allocator allocator = Allocator.Persistent)
        {
            poolSize = poolSizeBytes;
            memoryPool = (byte*)UnsafeUtility.Malloc(poolSize, 16, allocator);
            currentOffset = 0;
            blocks = new NativeList<MemoryBlock>(1024, allocator);
        }

        public void* Allocate(int size, int alignment = 16)
        {
            // Calculate aligned offset
            int alignedOffset = (currentOffset + alignment - 1) & ~(alignment - 1);
            
            if (alignedOffset + size > poolSize)
            {
                Debug.LogError("Memory pool exhausted");
                return null;
            }

            void* pointer = memoryPool + alignedOffset;
            
            blocks.Add(new MemoryBlock
            {
                pointer = pointer,
                size = size,
                isAllocated = true,
                alignmentOffset = alignedOffset - currentOffset
            });

            currentOffset = alignedOffset + size;
            return pointer;
        }

        public T* Allocate<T>(int count = 1) where T : unmanaged
        {
            int size = UnsafeUtility.SizeOf<T>() * count;
            int alignment = UnsafeUtility.AlignOf<T>();
            return (T*)Allocate(size, alignment);
        }

        public void Deallocate(void* pointer)
        {
            for (int i = 0; i < blocks.Length; i++)
            {
                if (blocks[i].pointer == pointer)
                {
                    var block = blocks[i];
                    block.isAllocated = false;
                    blocks[i] = block;
                    break;
                }
            }
        }

        public void Reset()
        {
            currentOffset = 0;
            blocks.Clear();
        }

        public void Dispose()
        {
            if (memoryPool != null)
            {
                UnsafeUtility.Free(memoryPool, Allocator.Persistent);
                memoryPool = null;
            }
            
            if (blocks.IsCreated)
            {
                blocks.Dispose();
            }
        }

        public int GetUsedMemory() => currentOffset;
        public int GetTotalMemory() => poolSize;
        public float GetMemoryUtilization() => (float)currentOffset / poolSize;
    }

    // High-performance job system for engine programmers
    [Unity.Burst.BurstCompile]
    public struct AdvancedTransformJob : IJobParallelForTransform
    {
        [ReadOnly] public NativeArray<float3> velocities;
        [ReadOnly] public NativeArray<float3> forces;
        [ReadOnly] public float deltaTime;
        [ReadOnly] public float drag;

        public void Execute(int index, TransformAccess transform)
        {
            if (index >= velocities.Length) return;

            float3 velocity = velocities[index];
            float3 force = forces[index];
            
            // Apply physics
            velocity += force * deltaTime;
            velocity *= (1.0f - drag * deltaTime);
            
            // Update position
            float3 position = transform.position;
            position += velocity * deltaTime;
            transform.position = position;
        }
    }

    [Unity.Burst.BurstCompile]
    public struct SpatialHashJob : IJob
    {
        public struct SpatialEntry
        {
            public float3 position;
            public int entityIndex;
        }

        [ReadOnly] public NativeArray<float3> positions;
        [ReadOnly] public float cellSize;
        public NativeMultiHashMap<int, SpatialEntry> spatialHash;

        public void Execute()
        {
            spatialHash.Clear();
            
            for (int i = 0; i < positions.Length; i++)
            {
                int hash = GetSpatialHash(positions[i]);
                spatialHash.Add(hash, new SpatialEntry
                {
                    position = positions[i],
                    entityIndex = i
                });
            }
        }

        private int GetSpatialHash(float3 position)
        {
            int x = (int)math.floor(position.x / cellSize);
            int y = (int)math.floor(position.y / cellSize);
            int z = (int)math.floor(position.z / cellSize);
            
            // Hash function
            return x * 73856093 ^ y * 19349663 ^ z * 83492791;
        }
    }

    // Advanced profiling and performance monitoring
    [System.Serializable]
    public class AdvancedProfiler
    {
        private struct ProfileSample
        {
            public string name;
            public long startTicks;
            public long endTicks;
            public int threadId;
        }

        private NativeArray<ProfileSample> samples;
        private int sampleIndex;
        private readonly int maxSamples;
        private System.Collections.Generic.Dictionary<string, System.Diagnostics.Stopwatch> activeTimers;

        public AdvancedProfiler(int maxSamples = 10000)
        {
            this.maxSamples = maxSamples;
            samples = new NativeArray<ProfileSample>(maxSamples, Allocator.Persistent);
            sampleIndex = 0;
            activeTimers = new System.Collections.Generic.Dictionary<string, System.Diagnostics.Stopwatch>();
        }

        public void BeginSample(string name)
        {
            if (!activeTimers.ContainsKey(name))
            {
                activeTimers[name] = new System.Diagnostics.Stopwatch();
            }
            
            activeTimers[name].Restart();
        }

        public void EndSample(string name)
        {
            if (activeTimers.TryGetValue(name, out var timer))
            {
                timer.Stop();
                
                if (sampleIndex < maxSamples)
                {
                    samples[sampleIndex] = new ProfileSample
                    {
                        name = name,
                        startTicks = 0, // Would store actual start time
                        endTicks = timer.ElapsedTicks,
                        threadId = System.Threading.Thread.CurrentThread.ManagedThreadId
                    };
                    sampleIndex++;
                }
            }
        }

        public void GenerateReport()
        {
            var report = new System.Text.StringBuilder();
            report.AppendLine("Performance Report");
            report.AppendLine("==================");

            var groupedSamples = new System.Collections.Generic.Dictionary<string, System.Collections.Generic.List<long>>();
            
            for (int i = 0; i < sampleIndex; i++)
            {
                var sample = samples[i];
                if (!groupedSamples.ContainsKey(sample.name))
                {
                    groupedSamples[sample.name] = new System.Collections.Generic.List<long>();
                }
                groupedSamples[sample.name].Add(sample.endTicks);
            }

            foreach (var kvp in groupedSamples)
            {
                var times = kvp.Value;
                var avgTicks = times.Sum() / (double)times.Count;
                var avgMs = (avgTicks / System.Diagnostics.Stopwatch.Frequency) * 1000.0;
                
                report.AppendLine($"{kvp.Key}: {avgMs:F3}ms avg ({times.Count} samples)");
            }

            Debug.Log(report.ToString());
        }

        public void Dispose()
        {
            if (samples.IsCreated)
            {
                samples.Dispose();
            }
        }
    }

    // Custom asset loading and streaming system
    [System.Serializable]
    public class AdvancedAssetStreamer
    {
        public enum LoadPriority
        {
            Critical,
            High,
            Normal,
            Low,
            Background
        }

        [System.Serializable]
        public class AssetRequest
        {
            public string assetPath;
            public System.Type assetType;
            public LoadPriority priority;
            public System.Action<UnityEngine.Object> onLoaded;
            public System.Action<string> onError;
            public float timeRequested;
            public bool isComplete;
        }

        private System.Collections.Generic.Queue<AssetRequest>[] priorityQueues;
        private System.Collections.Generic.Dictionary<string, UnityEngine.Object> assetCache;
        private System.Collections.Generic.Dictionary<string, AssetRequest> activeRequests;
        private int maxConcurrentLoads = 4;
        private int currentLoads = 0;

        public AdvancedAssetStreamer()
        {
            int priorityCount = System.Enum.GetValues(typeof(LoadPriority)).Length;
            priorityQueues = new System.Collections.Generic.Queue<AssetRequest>[priorityCount];
            
            for (int i = 0; i < priorityCount; i++)
            {
                priorityQueues[i] = new System.Collections.Generic.Queue<AssetRequest>();
            }

            assetCache = new System.Collections.Generic.Dictionary<string, UnityEngine.Object>();
            activeRequests = new System.Collections.Generic.Dictionary<string, AssetRequest>();
        }

        public void LoadAssetAsync<T>(string assetPath, LoadPriority priority, System.Action<T> onLoaded, System.Action<string> onError = null) where T : UnityEngine.Object
        {
            // Check cache first
            if (assetCache.TryGetValue(assetPath, out UnityEngine.Object cachedAsset))
            {
                onLoaded?.Invoke(cachedAsset as T);
                return;
            }

            // Check if already loading
            if (activeRequests.ContainsKey(assetPath))
            {
                var existingRequest = activeRequests[assetPath];
                existingRequest.onLoaded += (asset) => onLoaded?.Invoke(asset as T);
                return;
            }

            var request = new AssetRequest
            {
                assetPath = assetPath,
                assetType = typeof(T),
                priority = priority,
                onLoaded = (asset) => onLoaded?.Invoke(asset as T),
                onError = onError,
                timeRequested = Time.time,
                isComplete = false
            };

            priorityQueues[(int)priority].Enqueue(request);
            activeRequests[assetPath] = request;
        }

        public void Update()
        {
            if (currentLoads >= maxConcurrentLoads)
                return;

            // Process queues by priority
            for (int priority = 0; priority < priorityQueues.Length; priority++)
            {
                var queue = priorityQueues[priority];
                
                while (queue.Count > 0 && currentLoads < maxConcurrentLoads)
                {
                    var request = queue.Dequeue();
                    StartAsyncLoad(request);
                }
            }
        }

        private void StartAsyncLoad(AssetRequest request)
        {
            currentLoads++;
            
            var resourceRequest = Resources.LoadAsync(request.assetPath, request.assetType);
            resourceRequest.completed += (operation) =>
            {
                currentLoads--;
                
                if (resourceRequest.asset != null)
                {
                    assetCache[request.assetPath] = resourceRequest.asset;
                    request.onLoaded?.Invoke(resourceRequest.asset);
                }
                else
                {
                    request.onError?.Invoke($"Failed to load asset: {request.assetPath}");
                }

                request.isComplete = true;
                activeRequests.Remove(request.assetPath);
            };
        }

        public void ClearCache()
        {
            assetCache.Clear();
        }

        public int GetCacheSize()
        {
            return assetCache.Count;
        }

        public void UnloadAsset(string assetPath)
        {
            if (assetCache.TryGetValue(assetPath, out UnityEngine.Object asset))
            {
                if (asset != null)
                {
                    Resources.UnloadAsset(asset);
                }
                assetCache.Remove(assetPath);
            }
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Career Specialization Optimization

```
Create intelligent Unity career development tools:
1. Skill gap analysis and personalized learning path generation
2. Portfolio project suggestions based on target specializations
3. Interview preparation with role-specific technical challenges
4. Salary negotiation data and market analysis for Unity specializations

Context: Unity developer career advancement, specialization focus
Focus: Targeted skill development, competitive positioning, career growth
Requirements: Current job market data, personalized recommendations
```

### Technical Expertise Assessment

```
Build sophisticated Unity specialization evaluation systems:
1. Technical competency assessment tools for different Unity roles
2. Project complexity evaluation and skill demonstration frameworks
3. Mentorship matching based on specialization goals
4. Industry trend analysis and emerging specialization identification

Environment: Professional Unity development career planning
Goals: Accurate skill assessment, strategic career positioning, expert development
```

This comprehensive Unity specialization guide provides developers with deep technical knowledge and career development strategies for advancing in specialized Unity development roles with domain expertise and professional growth opportunities.