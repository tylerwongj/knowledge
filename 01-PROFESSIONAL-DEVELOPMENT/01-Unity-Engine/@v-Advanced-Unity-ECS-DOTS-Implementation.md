# @v-Advanced-Unity-ECS-DOTS-Implementation

## 🎯 Learning Objectives

- Master Unity's Entity Component System (ECS) and Data-Oriented Technology Stack (DOTS)
- Implement high-performance systems using job-based parallelism
- Create scalable architectures for massive multiplayer and simulation games
- Optimize memory usage and CPU performance with data-oriented design

## 🔧 Core ECS Architecture Fundamentals

### Entity Management System

```csharp
using Unity.Entities;
using Unity.Collections;
using Unity.Mathematics;
using Unity.Transforms;
using Unity.Rendering;

// Component data structures (IComponentData for single values)
public struct Health : IComponentData
{
    public float Value;
    public float MaxValue;
    public bool IsDead => Value <= 0f;
}

public struct MovementSpeed : IComponentData
{
    public float Value;
}

public struct Target : IComponentData
{
    public Entity Value;
    public float3 Position;
    public float EngagementRange;
}

// Buffer components for collections
[InternalBufferCapacity(16)]
public struct DamageBufferElement : IBufferElementData
{
    public float Damage;
    public Entity Source;
    public float3 Position;
    public float Timestamp;
}

// Tag components for filtering
public struct EnemyTag : IComponentData { }
public struct PlayerTag : IComponentData { }
public struct DeadTag : IComponentData { }

// Cleanup components (automatically removed when entity is destroyed)
public struct DestroyAfterTime : IComponentData, ICleanupComponent
{
    public float TimeRemaining;
}

// Advanced entity factory with proper initialization
public static class EntityFactory
{
    public static Entity CreateUnit(EntityManager entityManager, 
                                   float3 position, 
                                   quaternion rotation,
                                   float health,
                                   float movementSpeed,
                                   bool isEnemy = false)
    {
        // Create entity with archetype for better performance
        var archetype = entityManager.CreateArchetype(
            typeof(LocalToWorld),
            typeof(Translation),
            typeof(Rotation),
            typeof(NonUniformScale),
            typeof(Health),
            typeof(MovementSpeed),
            typeof(DamageBufferElement)
        );
        
        Entity entity = entityManager.CreateEntity(archetype);
        
        // Set component data
        entityManager.SetComponentData(entity, new Translation { Value = position });
        entityManager.SetComponentData(entity, new Rotation { Value = rotation });
        entityManager.SetComponentData(entity, new NonUniformScale { Value = new float3(1f) });
        
        entityManager.SetComponentData(entity, new Health 
        { 
            Value = health, 
            MaxValue = health 
        });
        
        entityManager.SetComponentData(entity, new MovementSpeed 
        { 
            Value = movementSpeed 
        });
        
        // Add tag components conditionally
        if (isEnemy)
        {
            entityManager.AddComponent<EnemyTag>(entity);
        }
        else
        {
            entityManager.AddComponent<PlayerTag>(entity);
        }
        
        return entity;
    }
    
    public static Entity CreateProjectile(EntityManager entityManager,
                                         float3 position,
                                         float3 direction,
                                         float speed,
                                         float damage,
                                         Entity owner)
    {
        var archetype = entityManager.CreateArchetype(
            typeof(LocalToWorld),
            typeof(Translation),
            typeof(Rotation),
            typeof(ProjectileComponent)
        );
        
        Entity projectile = entityManager.CreateEntity(archetype);
        
        entityManager.SetComponentData(projectile, new Translation { Value = position });
        entityManager.SetComponentData(projectile, new Rotation 
        { 
            Value = quaternion.LookRotation(direction, math.up()) 
        });
        
        entityManager.SetComponentData(projectile, new ProjectileComponent
        {
            Velocity = direction * speed,
            Damage = damage,
            Owner = owner,
            Lifetime = 10f // 10 seconds
        });
        
        return projectile;
    }
}

public struct ProjectileComponent : IComponentData
{
    public float3 Velocity;
    public float Damage;
    public Entity Owner;
    public float Lifetime;
}
```

### High-Performance Systems Implementation

```csharp
using Unity.Entities;
using Unity.Jobs;
using Unity.Collections;
using Unity.Mathematics;
using Unity.Transforms;

// Movement system using job parallelization
[UpdateInGroup(typeof(SimulationSystemGroup))]
public partial class MovementSystem : SystemBase
{
    protected override void OnUpdate()
    {
        float deltaTime = Time.DeltaTime;
        
        // Parallel job for movement calculation
        Entities
            .WithName("MovementJob")
            .ForEach((ref Translation translation, 
                     in MovementSpeed speed, 
                     in Target target) =>
            {
                float3 direction = math.normalize(target.Position - translation.Value);
                float3 movement = direction * speed.Value * deltaTime;
                
                // Only move if not at target
                if (math.distance(translation.Value, target.Position) > 0.1f)
                {
                    translation.Value += movement;
                }
            })
            .ScheduleParallel();
    }
}

// Combat system with damage processing
[UpdateInGroup(typeof(SimulationSystemGroup))]
[UpdateAfter(typeof(MovementSystem))]
public partial class CombatSystem : SystemBase
{
    private EndSimulationEntityCommandBufferSystem m_EndSimulationEcbSystem;
    
    protected override void OnCreate()
    {
        m_EndSimulationEcbSystem = World
            .GetOrCreateSystem<EndSimulationEntityCommandBufferSystem>();
    }
    
    protected override void OnUpdate()
    {
        var ecb = m_EndSimulationEcbSystem.CreateCommandBuffer().AsParallelWriter();
        var deltaTime = Time.DeltaTime;
        
        // Process damage buffers
        Entities
            .WithName("ProcessDamageJob")
            .ForEach((Entity entity,
                     int entityInQueryIndex,
                     ref Health health,
                     in DynamicBuffer<DamageBufferElement> damageBuffer) =>
            {
                // Apply all damage from buffer
                for (int i = 0; i < damageBuffer.Length; i++)
                {
                    health.Value -= damageBuffer[i].Damage;
                }
                
                // Clear damage buffer after processing
                if (damageBuffer.Length > 0)
                {
                    ecb.SetBuffer<DamageBufferElement>(entityInQueryIndex, entity);
                }
                
                // Mark as dead if health <= 0
                if (health.IsDead)
                {
                    ecb.AddComponent<DeadTag>(entityInQueryIndex, entity);
                    ecb.AddComponent<DestroyAfterTime>(entityInQueryIndex, entity, 
                        new DestroyAfterTime { TimeRemaining = 2f });
                }
            })
            .ScheduleParallel();
        
        // Handle dead entities cleanup
        Entities
            .WithName("DeadEntitiesCleanupJob")
            .WithAll<DeadTag>()
            .ForEach((Entity entity,
                     int entityInQueryIndex,
                     ref DestroyAfterTime destroyTimer) =>
            {
                destroyTimer.TimeRemaining -= deltaTime;
                
                if (destroyTimer.TimeRemaining <= 0f)
                {
                    ecb.DestroyEntity(entityInQueryIndex, entity);
                }
            })
            .ScheduleParallel();
        
        m_EndSimulationEcbSystem.AddJobHandleForProducer(Dependency);
    }
}

// Projectile system with collision detection
[UpdateInGroup(typeof(SimulationSystemGroup))]
public partial class ProjectileSystem : SystemBase
{
    private EndSimulationEntityCommandBufferSystem m_EndSimulationEcbSystem;
    
    protected override void OnCreate()
    {
        m_EndSimulationEcbSystem = World
            .GetOrCreateSystem<EndSimulationEntityCommandBufferSystem>();
    }
    
    protected override void OnUpdate()
    {
        var ecb = m_EndSimulationEcbSystem.CreateCommandBuffer().AsParallelWriter();
        var deltaTime = Time.DeltaTime;
        
        // Move projectiles
        Entities
            .WithName("ProjectileMovementJob")
            .ForEach((Entity entity,
                     int entityInQueryIndex,
                     ref Translation translation,
                     ref ProjectileComponent projectile) =>
            {
                // Update position
                translation.Value += projectile.Velocity * deltaTime;
                
                // Update lifetime
                projectile.Lifetime -= deltaTime;
                
                // Destroy if lifetime expired
                if (projectile.Lifetime <= 0f)
                {
                    ecb.DestroyEntity(entityInQueryIndex, entity);
                }
            })
            .ScheduleParallel();
        
        // Collision detection job
        var projectilePositions = GetComponentDataFromEntity<Translation>(true);
        var healthComponents = GetComponentDataFromEntity<Health>(false);
        var damageBuffers = GetBufferFromEntity<DamageBufferElement>(false);
        
        Entities
            .WithName("ProjectileCollisionJob")
            .WithReadOnly(projectilePositions)
            .WithNativeDisableContainerSafetyRestriction(healthComponents)
            .WithNativeDisableContainerSafetyRestriction(damageBuffers)
            .WithAll<EnemyTag>() // Only check collision with enemies
            .ForEach((Entity targetEntity,
                     int entityInQueryIndex,
                     in Translation targetPosition) =>
            {
                // Check collision with all projectiles
                Entities
                    .WithName("ProjectileCollisionInnerJob")
                    .WithReadOnly(projectilePositions)
                    .ForEach((Entity projectileEntity,
                             in ProjectileComponent projectile) =>
                    {
                        if (!projectilePositions.HasComponent(projectileEntity)) return;
                        
                        float3 projectilePos = projectilePositions[projectileEntity].Value;
                        float distance = math.distance(projectilePos, targetPosition.Value);
                        
                        // Collision threshold
                        if (distance < 0.5f)
                        {
                            // Add damage to target
                            if (damageBuffers.HasComponent(targetEntity))
                            {
                                var damageBuffer = damageBuffers[targetEntity];
                                damageBuffer.Add(new DamageBufferElement
                                {
                                    Damage = projectile.Damage,
                                    Source = projectile.Owner,
                                    Position = projectilePos,
                                    Timestamp = Time.ElapsedTime
                                });
                            }
                            
                            // Destroy projectile
                            ecb.DestroyEntity(entityInQueryIndex, projectileEntity);
                        }
                    })
                    .Run(); // Run on main thread due to nested ForEach
            })
            .Run(); // Must run on main thread due to complexity
        
        m_EndSimulationEcbSystem.AddJobHandleForProducer(Dependency);
    }
}
```

## 🎮 Advanced Performance Optimization

### Chunk-Based Processing System

```csharp
using Unity.Entities;
using Unity.Collections;
using Unity.Mathematics;
using Unity.Transforms;

// High-performance chunk iteration system
[UpdateInGroup(typeof(SimulationSystemGroup))]
public partial class OptimizedMovementSystem : SystemBase
{
    private EntityQuery m_MovementQuery;
    
    protected override void OnCreate()
    {
        // Create optimized query
        m_MovementQuery = GetEntityQuery(new EntityQueryDesc
        {
            All = new ComponentType[]
            {
                ComponentType.ReadWrite<Translation>(),
                ComponentType.ReadOnly<MovementSpeed>(),
                ComponentType.ReadOnly<Target>()
            },
            None = new ComponentType[]
            {
                typeof(DeadTag) // Exclude dead entities
            }
        });
    }
    
    protected override void OnUpdate()
    {
        var deltaTime = Time.DeltaTime;
        
        // Process chunks directly for maximum performance
        var job = new ChunkMovementJob
        {
            DeltaTime = deltaTime,
            TranslationType = GetComponentTypeHandle<Translation>(false),
            SpeedType = GetComponentTypeHandle<MovementSpeed>(true),
            TargetType = GetComponentTypeHandle<Target>(true)
        };
        
        Dependency = job.ScheduleParallel(m_MovementQuery, Dependency);
    }
}

// Chunk-based job for optimal performance
[Unity.Burst.BurstCompile]
public struct ChunkMovementJob : IJobEntityBatch
{
    public float DeltaTime;
    
    public ComponentTypeHandle<Translation> TranslationType;
    [ReadOnly] public ComponentTypeHandle<MovementSpeed> SpeedType;
    [ReadOnly] public ComponentTypeHandle<Target> TargetType;
    
    public void Execute(ArchetypeChunk chunk, int chunkIndex, int firstEntityIndex)
    {
        var translations = chunk.GetNativeArray(TranslationType);
        var speeds = chunk.GetNativeArray(SpeedType);
        var targets = chunk.GetNativeArray(TargetType);
        
        // Process all entities in chunk
        for (int i = 0; i < chunk.Count; i++)
        {
            var translation = translations[i];
            var speed = speeds[i];
            var target = targets[i];
            
            float3 direction = math.normalize(target.Position - translation.Value);
            float distance = math.distance(translation.Value, target.Position);
            
            // Only move if not at target
            if (distance > 0.1f)
            {
                float3 movement = direction * speed.Value * DeltaTime;
                translation.Value += movement;
                translations[i] = translation;
            }
        }
    }
}
```

### Memory-Optimized Spatial Partitioning

```csharp
using Unity.Entities;
using Unity.Collections;
using Unity.Mathematics;
using Unity.Jobs;

// Spatial hash for efficient neighbor queries
public struct SpatialHashMap : IDisposable
{
    private NativeMultiHashMap<int, SpatialEntry> hashMap;
    private float cellSize;
    
    public struct SpatialEntry
    {
        public Entity Entity;
        public float3 Position;
    }
    
    public SpatialHashMap(int capacity, float cellSize, Allocator allocator)
    {
        this.hashMap = new NativeMultiHashMap<int, SpatialEntry>(capacity, allocator);
        this.cellSize = cellSize;
    }
    
    public void Clear()
    {
        hashMap.Clear();
    }
    
    public void Add(Entity entity, float3 position)
    {
        int hash = GetSpatialHash(position);
        hashMap.Add(hash, new SpatialEntry { Entity = entity, Position = position });
    }
    
    public NativeArray<SpatialEntry> GetNearbyEntities(float3 position, 
                                                       float radius, 
                                                       Allocator allocator)
    {
        var results = new NativeList<SpatialEntry>(16, allocator);
        
        // Check surrounding cells
        int cellRadius = (int)math.ceil(radius / cellSize);
        for (int x = -cellRadius; x <= cellRadius; x++)
        {
            for (int z = -cellRadius; z <= cellRadius; z++)
            {
                float3 cellPos = position + new float3(x * cellSize, 0, z * cellSize);
                int hash = GetSpatialHash(cellPos);
                
                if (hashMap.TryGetFirstValue(hash, out SpatialEntry entry, out NativeMultiHashMapIterator<int> iterator))
                {
                    do
                    {
                        if (math.distance(position, entry.Position) <= radius)
                        {
                            results.Add(entry);
                        }
                    } while (hashMap.TryGetNextValue(out entry, ref iterator));
                }
            }
        }
        
        return results.ToArray(allocator);
    }
    
    private int GetSpatialHash(float3 position)
    {
        int x = (int)math.floor(position.x / cellSize);
        int z = (int)math.floor(position.z / cellSize);
        
        // Simple hash combining x and z
        return x * 73856093 ^ z * 19349663;
    }
    
    public void Dispose()
    {
        if (hashMap.IsCreated)
        {
            hashMap.Dispose();
        }
    }
}

// System using spatial partitioning for neighbor detection
[UpdateInGroup(typeof(SimulationSystemGroup))]
public partial class FlockingSystem : SystemBase
{
    private SpatialHashMap spatialMap;
    
    protected override void OnCreate()
    {
        spatialMap = new SpatialHashMap(10000, 5f, Allocator.Persistent);
    }
    
    protected override void OnDestroy()
    {
        spatialMap.Dispose();
    }
    
    protected override void OnUpdate()
    {
        spatialMap.Clear();
        
        // Build spatial map
        Entities
            .WithName("BuildSpatialMap")
            .ForEach((Entity entity, in Translation translation) =>
            {
                spatialMap.Add(entity, translation.Value);
            })
            .Run();
        
        // Apply flocking behavior
        var deltaTime = Time.DeltaTime;
        
        Entities
            .WithName("FlockingBehavior")
            .ForEach((Entity entity,
                     ref Translation translation,
                     ref FlockingComponent flocking,
                     in MovementSpeed speed) =>
            {
                var neighbors = spatialMap.GetNearbyEntities(
                    translation.Value, 
                    flocking.NeighborRadius, 
                    Allocator.Temp);
                
                if (neighbors.Length > 1) // Exclude self
                {
                    float3 separation = CalculateSeparation(translation.Value, neighbors);
                    float3 alignment = CalculateAlignment(neighbors);
                    float3 cohesion = CalculateCohesion(translation.Value, neighbors);
                    
                    float3 steeringForce = separation * flocking.SeparationWeight +
                                          alignment * flocking.AlignmentWeight +
                                          cohesion * flocking.CohesionWeight;
                    
                    flocking.Velocity += steeringForce * deltaTime;
                    flocking.Velocity = math.normalize(flocking.Velocity) * speed.Value;
                    
                    translation.Value += flocking.Velocity * deltaTime;
                }
                
                neighbors.Dispose();
            })
            .Run();
    }
    
    private float3 CalculateSeparation(float3 position, NativeArray<SpatialHashMap.SpatialEntry> neighbors)
    {
        float3 separation = float3.zero;
        int count = 0;
        
        foreach (var neighbor in neighbors)
        {
            float distance = math.distance(position, neighbor.Position);
            if (distance > 0.01f && distance < 2f) // Avoid self and too distant
            {
                float3 diff = position - neighbor.Position;
                separation += math.normalize(diff) / distance; // Weight by inverse distance
                count++;
            }
        }
        
        return count > 0 ? separation / count : float3.zero;
    }
    
    private float3 CalculateAlignment(NativeArray<SpatialHashMap.SpatialEntry> neighbors)
    {
        // Simplified - in real implementation, would need velocity data
        return float3.zero;
    }
    
    private float3 CalculateCohesion(float3 position, NativeArray<SpatialHashMap.SpatialEntry> neighbors)
    {
        if (neighbors.Length <= 1) return float3.zero;
        
        float3 center = float3.zero;
        int count = 0;
        
        foreach (var neighbor in neighbors)
        {
            if (math.distance(position, neighbor.Position) > 0.01f)
            {
                center += neighbor.Position;
                count++;
            }
        }
        
        if (count > 0)
        {
            center /= count;
            return math.normalize(center - position);
        }
        
        return float3.zero;
    }
}

public struct FlockingComponent : IComponentData
{
    public float3 Velocity;
    public float NeighborRadius;
    public float SeparationWeight;
    public float AlignmentWeight;
    public float CohesionWeight;
}
```

## 🚀 AI/LLM Integration Opportunities

### Automated ECS System Generation

```
Generate Unity ECS systems for:
1. Complex AI behavior trees using job-based parallelism
2. Large-scale physics simulation with spatial partitioning
3. Procedural content generation using burst-compiled jobs
4. Network synchronization systems for multiplayer ECS games

Context: High-performance Unity game requiring 60fps with thousands of entities
Focus: Burst compilation compatibility, memory optimization, scalable architecture
Requirements: Production-ready code with comprehensive documentation
```

### Performance Analysis and Optimization

```
Analyze and optimize Unity ECS implementations:
1. Memory layout optimization for cache efficiency
2. Job dependency chain optimization for parallel execution
3. Entity archetype design for minimal structural changes
4. Burst compilation opportunities and SIMD optimization

Environment: Unity DOTS 1.0, large-scale simulation requirements
Goals: Maximum performance, minimal garbage collection, scalable systems
```

## 💡 Advanced ECS Patterns

### State Machine System

```csharp
// State machine implementation using ECS
public struct StateMachineComponent : IComponentData
{
    public Entity CurrentState;
    public float StateTime;
}

public struct StateTransition : IBufferElementData
{
    public Entity FromState;
    public Entity ToState;
    public StateTransitionCondition Condition;
}

public enum StateTransitionCondition
{
    OnHealthLow,
    OnEnemyNear,
    OnTimeExpired,
    OnTargetReached
}

[UpdateInGroup(typeof(SimulationSystemGroup))]
public partial class StateMachineSystem : SystemBase
{
    private EndSimulationEntityCommandBufferSystem m_EndSimulationEcbSystem;
    
    protected override void OnCreate()
    {
        m_EndSimulationEcbSystem = World
            .GetOrCreateSystem<EndSimulationEntityCommandBufferSystem>();
    }
    
    protected override void OnUpdate()
    {
        var ecb = m_EndSimulationEcbSystem.CreateCommandBuffer().AsParallelWriter();
        var deltaTime = Time.DeltaTime;
        
        // Update state timers
        Entities
            .WithName("UpdateStateTime")
            .ForEach((ref StateMachineComponent stateMachine) =>
            {
                stateMachine.StateTime += deltaTime;
            })
            .ScheduleParallel();
        
        // Check state transitions
        Entities
            .WithName("CheckStateTransitions")
            .ForEach((Entity entity,
                     int entityInQueryIndex,
                     ref StateMachineComponent stateMachine,
                     in DynamicBuffer<StateTransition> transitions,
                     in Health health) =>
            {
                foreach (var transition in transitions)
                {
                    if (transition.FromState == stateMachine.CurrentState)
                    {
                        bool shouldTransition = false;
                        
                        switch (transition.Condition)
                        {
                            case StateTransitionCondition.OnHealthLow:
                                shouldTransition = health.Value < health.MaxValue * 0.3f;
                                break;
                            case StateTransitionCondition.OnTimeExpired:
                                shouldTransition = stateMachine.StateTime > 5f;
                                break;
                            // Add more conditions as needed
                        }
                        
                        if (shouldTransition)
                        {
                            stateMachine.CurrentState = transition.ToState;
                            stateMachine.StateTime = 0f;
                            break; // Only one transition per frame
                        }
                    }
                }
            })
            .ScheduleParallel();
        
        m_EndSimulationEcbSystem.AddJobHandleForProducer(Dependency);
    }
}
```

### Advanced Entity Streaming

```csharp
using Unity.Entities;
using Unity.Collections;
using Unity.Mathematics;
using Unity.Transforms;

// Level-of-detail and streaming system
public struct LODComponent : IComponentData
{
    public int CurrentLOD;
    public float LODDistance0; // High detail
    public float LODDistance1; // Medium detail  
    public float LODDistance2; // Low detail
    public float CullingDistance; // Completely disable
}

public struct StreamingCell : IComponentData
{
    public int2 CellCoordinates;
    public bool IsLoaded;
    public float LoadRadius;
    public float UnloadRadius;
}

[UpdateInGroup(typeof(PresentationSystemGroup))]
public partial class LODSystem : SystemBase
{
    private EntityQuery m_PlayerQuery;
    
    protected override void OnCreate()
    {
        m_PlayerQuery = GetEntityQuery(typeof(PlayerTag), typeof(Translation));
    }
    
    protected override void OnUpdate()
    {
        // Get player position
        if (m_PlayerQuery.CalculateEntityCount() == 0) return;
        
        var playerPositions = m_PlayerQuery.ToComponentDataArray<Translation>(Allocator.TempJob);
        if (playerPositions.Length == 0)
        {
            playerPositions.Dispose();
            return;
        }
        
        float3 playerPos = playerPositions[0].Value;
        playerPositions.Dispose();
        
        // Update LODs based on distance to player
        Entities
            .WithName("UpdateLOD")
            .ForEach((ref LODComponent lod,
                     in Translation translation) =>
            {
                float distance = math.distance(playerPos, translation.Value);
                
                int newLOD = 0;
                if (distance > lod.CullingDistance)
                {
                    newLOD = -1; // Culled
                }
                else if (distance > lod.LODDistance2)
                {
                    newLOD = 3; // Lowest LOD
                }
                else if (distance > lod.LODDistance1)
                {
                    newLOD = 2;
                }
                else if (distance > lod.LODDistance0)
                {
                    newLOD = 1;
                }
                else
                {
                    newLOD = 0; // Highest LOD
                }
                
                lod.CurrentLOD = newLOD;
            })
            .ScheduleParallel();
    }
}
```

This comprehensive guide provides advanced ECS/DOTS implementation patterns for building high-performance, scalable Unity applications with data-oriented design principles.