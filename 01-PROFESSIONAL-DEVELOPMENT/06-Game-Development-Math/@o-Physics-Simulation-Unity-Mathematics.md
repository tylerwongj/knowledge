# @o-Physics-Simulation-Unity-Mathematics

## 🎯 Learning Objectives

- Master advanced physics simulation techniques in Unity using Unity Mathematics
- Implement custom physics solvers for specialized game mechanics  
- Create realistic particle systems and fluid dynamics
- Build high-performance physics simulations with job system integration

## 🔧 Custom Physics Foundation

### Verlet Integration System

```csharp
using Unity.Mathematics;
using Unity.Collections;
using Unity.Jobs;
using UnityEngine;
using Unity.Burst;

[System.Serializable]
public struct VerletParticle
{
    public float3 position;
    public float3 previousPosition;
    public float3 acceleration;
    public float inverseMass;
    public bool isFixed;
    
    public VerletParticle(float3 pos, float mass = 1f, bool fixedParticle = false)
    {
        position = pos;
        previousPosition = pos;
        acceleration = float3.zero;
        inverseMass = fixedParticle ? 0f : 1f / math.max(mass, 0.001f);
        isFixed = fixedParticle;
    }
    
    public void ApplyForce(float3 force)
    {
        if (!isFixed)
        {
            acceleration += force * inverseMass;
        }
    }
    
    public void UpdateVerlet(float deltaTime)
    {
        if (isFixed) return;
        
        float3 velocity = position - previousPosition;
        previousPosition = position;
        position += velocity + acceleration * deltaTime * deltaTime;
        acceleration = float3.zero;
    }
}

[System.Serializable]
public struct DistanceConstraint
{
    public int particleA;
    public int particleB;
    public float restDistance;
    public float strength;
    
    public DistanceConstraint(int a, int b, float distance, float constraintStrength = 1f)
    {
        particleA = a;
        particleB = b;
        restDistance = distance;
        strength = math.clamp(constraintStrength, 0f, 1f);
    }
}

public class VerletPhysicsSystem : MonoBehaviour
{
    [Header("Physics Settings")]
    [SerializeField] private float3 gravity = new float3(0, -9.81f, 0);
    [SerializeField] private float damping = 0.99f;
    [SerializeField] private int constraintIterations = 3;
    [SerializeField] private float timeStep = 0.016f; // 60 FPS
    
    [Header("Debug")]
    [SerializeField] private bool drawConstraints = true;
    [SerializeField] private Color constraintColor = Color.green;
    
    // Native arrays for job system
    private NativeArray<VerletParticle> particles;
    private NativeArray<DistanceConstraint> constraints;
    private JobHandle jobHandle;
    
    // Particle management
    private List<VerletParticle> particleList = new List<VerletParticle>();
    private List<DistanceConstraint> constraintList = new List<DistanceConstraint>();
    private bool isDirty = true;
    
    void Start()
    {
        InitializeClothDemo();
    }
    
    void InitializeClothDemo()
    {
        // Create a cloth grid
        int width = 10;
        int height = 10;
        float spacing = 1f;
        
        // Create particles
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                float3 position = new float3(x * spacing, 5f, y * spacing);
                bool isFixed = (y == height - 1) && (x == 0 || x == width - 1); // Fix top corners
                
                particleList.Add(new VerletParticle(position, 1f, isFixed));
            }
        }
        
        // Create constraints
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                int index = y * width + x;
                
                // Structural constraints (horizontal and vertical)
                if (x < width - 1)
                {
                    constraintList.Add(new DistanceConstraint(index, index + 1, spacing, 1f));
                }
                if (y < height - 1)
                {
                    constraintList.Add(new DistanceConstraint(index, index + width, spacing, 1f));
                }
                
                // Shear constraints (diagonal)
                if (x < width - 1 && y < height - 1)
                {
                    float diagonalDistance = math.sqrt(2f) * spacing;
                    constraintList.Add(new DistanceConstraint(index, index + width + 1, diagonalDistance, 0.5f));
                }
                if (x > 0 && y < height - 1)
                {
                    float diagonalDistance = math.sqrt(2f) * spacing;
                    constraintList.Add(new DistanceConstraint(index, index + width - 1, diagonalDistance, 0.5f));
                }
                
                // Bend constraints (skip one)
                if (x < width - 2)
                {
                    constraintList.Add(new DistanceConstraint(index, index + 2, spacing * 2f, 0.3f));
                }
                if (y < height - 2)
                {
                    constraintList.Add(new DistanceConstraint(index, index + width * 2, spacing * 2f, 0.3f));
                }
            }
        }
        
        isDirty = true;
    }
    
    void Update()
    {
        if (isDirty)
        {
            UpdateNativeArrays();
            isDirty = false;
        }
        
        // Complete previous frame's job
        jobHandle.Complete();
        
        // Schedule physics jobs
        var applyForcesJob = new ApplyForcesJob
        {
            particles = particles,
            gravity = gravity,
            deltaTime = timeStep
        };
        
        var integrateJob = new IntegrateVerletJob
        {
            particles = particles,
            damping = damping,
            deltaTime = timeStep
        };
        
        var constraintJob = new SolveConstraintsJob
        {
            particles = particles,
            constraints = constraints
        };
        
        // Chain jobs
        var forcesJobHandle = applyForcesJob.Schedule(particles.Length, 32);
        var integrateJobHandle = integrateJob.Schedule(particles.Length, 32, forcesJobHandle);
        
        JobHandle constraintJobHandle = integrateJobHandle;
        for (int i = 0; i < constraintIterations; i++)
        {
            constraintJobHandle = constraintJob.Schedule(constraints.Length, 32, constraintJobHandle);
        }
        
        jobHandle = constraintJobHandle;
        JobHandle.ScheduleBatchedJobs();
    }
    
    void UpdateNativeArrays()
    {
        // Dispose existing arrays
        if (particles.IsCreated) particles.Dispose();
        if (constraints.IsCreated) constraints.Dispose();
        
        // Create new arrays
        particles = new NativeArray<VerletParticle>(particleList.ToArray(), Allocator.Persistent);
        constraints = new NativeArray<DistanceConstraint>(constraintList.ToArray(), Allocator.Persistent);
    }
    
    void OnDestroy()
    {
        jobHandle.Complete();
        if (particles.IsCreated) particles.Dispose();
        if (constraints.IsCreated) constraints.Dispose();
    }
    
    void OnDrawGizmos()
    {
        if (!drawConstraints || !particles.IsCreated) return;
        
        Gizmos.color = constraintColor;
        
        for (int i = 0; i < constraints.Length; i++)
        {
            var constraint = constraints[i];
            var particleA = particles[constraint.particleA];
            var particleB = particles[constraint.particleB];
            
            Gizmos.DrawLine(particleA.position, particleB.position);
        }
        
        // Draw particles
        Gizmos.color = Color.red;
        for (int i = 0; i < particles.Length; i++)
        {
            var particle = particles[i];
            Gizmos.color = particle.isFixed ? Color.red : Color.blue;
            Gizmos.DrawSphere(particle.position, 0.05f);
        }
    }
    
    public void AddExternalForce(float3 force, float3 position, float radius)
    {
        jobHandle.Complete();
        
        for (int i = 0; i < particles.Length; i++)
        {
            var particle = particles[i];
            float distance = math.distance(particle.position, position);
            
            if (distance < radius)
            {
                float influence = 1f - (distance / radius);
                particle.ApplyForce(force * influence);
                particles[i] = particle;
            }
        }
    }
}

[BurstCompile]
public struct ApplyForcesJob : IJobParallelFor
{
    public NativeArray<VerletParticle> particles;
    [ReadOnly] public float3 gravity;
    [ReadOnly] public float deltaTime;
    
    public void Execute(int index)
    {
        var particle = particles[index];
        if (!particle.isFixed)
        {
            particle.ApplyForce(gravity);
        }
        particles[index] = particle;
    }
}

[BurstCompile]
public struct IntegrateVerletJob : IJobParallelFor
{
    public NativeArray<VerletParticle> particles;
    [ReadOnly] public float damping;
    [ReadOnly] public float deltaTime;
    
    public void Execute(int index)
    {
        var particle = particles[index];
        if (!particle.isFixed)
        {
            // Apply damping
            float3 velocity = particle.position - particle.previousPosition;
            velocity *= damping;
            particle.previousPosition = particle.position - velocity;
            
            // Verlet integration
            particle.UpdateVerlet(deltaTime);
        }
        particles[index] = particle;
    }
}

[BurstCompile]
public struct SolveConstraintsJob : IJobParallelFor
{
    public NativeArray<VerletParticle> particles;
    [ReadOnly] public NativeArray<DistanceConstraint> constraints;
    
    public void Execute(int index)
    {
        var constraint = constraints[index];
        var particleA = particles[constraint.particleA];
        var particleB = particles[constraint.particleB];
        
        float3 delta = particleB.position - particleA.position;
        float distance = math.length(delta);
        
        if (distance > 0.001f) // Avoid division by zero
        {
            float difference = (constraint.restDistance - distance) / distance;
            float3 correction = delta * difference * 0.5f * constraint.strength;
            
            if (!particleA.isFixed)
            {
                particleA.position -= correction * particleA.inverseMass / 
                    (particleA.inverseMass + particleB.inverseMass);
            }
            
            if (!particleB.isFixed)
            {
                particleB.position += correction * particleB.inverseMass / 
                    (particleA.inverseMass + particleB.inverseMass);
            }
            
            particles[constraint.particleA] = particleA;
            particles[constraint.particleB] = particleB;
        }
    }
}
```

### Fluid Dynamics Simulation

```csharp
using Unity.Mathematics;
using Unity.Collections;
using Unity.Jobs;
using UnityEngine;
using Unity.Burst;

[System.Serializable]
public struct FluidParticle
{
    public float3 position;
    public float3 velocity;
    public float3 force;
    public float density;
    public float pressure;
    public int gridIndex;
    
    public FluidParticle(float3 pos)
    {
        position = pos;
        velocity = float3.zero;
        force = float3.zero;
        density = 0f;
        pressure = 0f;
        gridIndex = -1;
    }
}

public class SPHFluidSimulation : MonoBehaviour
{
    [Header("Simulation Parameters")]
    [SerializeField] private float particleRadius = 0.1f;
    [SerializeField] private float smoothingRadius = 0.2f;
    [SerializeField] private float restDensity = 1000f;
    [SerializeField] private float gasConstant = 2000f;
    [SerializeField] private float viscosity = 250f;
    [SerializeField] private float3 gravity = new float3(0, -9.81f, 0);
    [SerializeField] private float damping = 0.95f;
    
    [Header("Rendering")]
    [SerializeField] private Mesh particleMesh;
    [SerializeField] private Material particleMaterial;
    [SerializeField] private int particleCount = 1000;
    
    // Native arrays
    private NativeArray<FluidParticle> particles;
    private NativeArray<float3> positions;
    private NativeArray<int> gridIndices;
    private NativeMultiHashMap<int, int> spatialGrid;
    
    // Rendering
    private Matrix4x4[] renderMatrices;
    private ComputeBuffer positionBuffer;
    private MaterialPropertyBlock propertyBlock;
    
    // Grid parameters
    private float cellSize;
    private int3 gridDimensions;
    private float3 gridMin;
    private float3 gridMax;
    
    void Start()
    {
        cellSize = smoothingRadius;
        InitializeFluidParticles();
        SetupRendering();
    }
    
    void InitializeFluidParticles()
    {
        particles = new NativeArray<FluidParticle>(particleCount, Allocator.Persistent);
        positions = new NativeArray<float3>(particleCount, Allocator.Persistent);
        gridIndices = new NativeArray<int>(particleCount, Allocator.Persistent);
        
        // Initialize grid
        gridMin = new float3(-5, 0, -5);
        gridMax = new float3(5, 10, 5);
        gridDimensions = (int3)math.ceil((gridMax - gridMin) / cellSize);
        
        spatialGrid = new NativeMultiHashMap<int, int>(particleCount * 8, Allocator.Persistent);
        
        // Create fluid particles in a box formation
        int particlesPerAxis = (int)math.ceil(math.pow(particleCount, 1f/3f));
        float spacing = particleRadius * 1.5f;
        
        int index = 0;
        for (int x = 0; x < particlesPerAxis && index < particleCount; x++)
        {
            for (int y = 0; y < particlesPerAxis && index < particleCount; y++)
            {
                for (int z = 0; z < particlesPerAxis && index < particleCount; z++)
                {
                    float3 pos = new float3(
                        x * spacing - particlesPerAxis * spacing * 0.5f,
                        y * spacing + 2f,
                        z * spacing - particlesPerAxis * spacing * 0.5f
                    );
                    
                    particles[index] = new FluidParticle(pos);
                    positions[index] = pos;
                    index++;
                }
            }
        }
        
        renderMatrices = new Matrix4x4[particleCount];
    }
    
    void SetupRendering()
    {
        positionBuffer = new ComputeBuffer(particleCount, sizeof(float) * 3);
        propertyBlock = new MaterialPropertyBlock();
    }
    
    void Update()
    {
        // Complete previous frame
        JobHandle.CompleteAll();
        
        float deltaTime = Time.deltaTime;
        
        // Update spatial grid
        var updateGridJob = new UpdateSpatialGridJob
        {
            particles = particles,
            gridIndices = gridIndices,
            spatialGrid = spatialGrid.AsParallelWriter(),
            cellSize = cellSize,
            gridMin = gridMin,
            gridDimensions = gridDimensions
        };
        
        spatialGrid.Clear();
        var gridJobHandle = updateGridJob.Schedule(particleCount, 32);
        
        // Calculate density and pressure
        var densityJob = new CalculateDensityJob
        {
            particles = particles,
            spatialGrid = spatialGrid,
            smoothingRadius = smoothingRadius,
            restDensity = restDensity,
            gasConstant = gasConstant,
            gridDimensions = gridDimensions,
            gridMin = gridMin,
            cellSize = cellSize
        };
        
        var densityJobHandle = densityJob.Schedule(particleCount, 32, gridJobHandle);
        
        // Calculate forces
        var forceJob = new CalculateForceJob
        {
            particles = particles,
            spatialGrid = spatialGrid,
            smoothingRadius = smoothingRadius,
            viscosity = viscosity,
            gravity = gravity,
            gridDimensions = gridDimensions,
            gridMin = gridMin,
            cellSize = cellSize
        };
        
        var forceJobHandle = forceJob.Schedule(particleCount, 32, densityJobHandle);
        
        // Integrate
        var integrateJob = new IntegrateFluidJob
        {
            particles = particles,
            positions = positions,
            deltaTime = deltaTime,
            damping = damping,
            bounds = new AABB { Min = gridMin, Max = gridMax }
        };
        
        var integrateJobHandle = integrateJob.Schedule(particleCount, 32, forceJobHandle);
        
        integrateJobHandle.Complete();
        
        // Update rendering
        UpdateRendering();
    }
    
    void UpdateRendering()
    {
        // Update position buffer for GPU instancing
        positionBuffer.SetData(positions);
        propertyBlock.SetBuffer("_Positions", positionBuffer);
        
        // Create matrices for instancing
        for (int i = 0; i < particleCount; i++)
        {
            renderMatrices[i] = Matrix4x4.TRS(
                positions[i], 
                Quaternion.identity, 
                Vector3.one * particleRadius
            );
        }
        
        // Render particles
        if (particleMesh != null && particleMaterial != null)
        {
            Graphics.DrawMeshInstanced(
                particleMesh, 
                0, 
                particleMaterial, 
                renderMatrices,
                particleCount,
                propertyBlock
            );
        }
    }
    
    void OnDestroy()
    {
        if (particles.IsCreated) particles.Dispose();
        if (positions.IsCreated) positions.Dispose();
        if (gridIndices.IsCreated) gridIndices.Dispose();
        if (spatialGrid.IsCreated) spatialGrid.Dispose();
        
        positionBuffer?.Dispose();
    }
    
    // Smoothing kernel functions
    public static float Poly6Kernel(float distanceSquared, float smoothingRadius)
    {
        float h2 = smoothingRadius * smoothingRadius;
        if (distanceSquared >= h2) return 0f;
        
        float diff = h2 - distanceSquared;
        return (315f / (64f * math.PI * math.pow(smoothingRadius, 9))) * diff * diff * diff;
    }
    
    public static float3 SpikyGradient(float3 direction, float distance, float smoothingRadius)
    {
        if (distance >= smoothingRadius || distance <= 0f) return float3.zero;
        
        float diff = smoothingRadius - distance;
        float coeff = -45f / (math.PI * math.pow(smoothingRadius, 6));
        return coeff * diff * diff * (direction / distance);
    }
    
    public static float ViscosityLaplacian(float distance, float smoothingRadius)
    {
        if (distance >= smoothingRadius) return 0f;
        
        float coeff = 45f / (math.PI * math.pow(smoothingRadius, 6));
        return coeff * (smoothingRadius - distance);
    }
}

[BurstCompile]
public struct UpdateSpatialGridJob : IJobParallelFor
{
    public NativeArray<FluidParticle> particles;
    public NativeArray<int> gridIndices;
    public NativeMultiHashMap<int, int>.ParallelWriter spatialGrid;
    [ReadOnly] public float cellSize;
    [ReadOnly] public float3 gridMin;
    [ReadOnly] public int3 gridDimensions;
    
    public void Execute(int index)
    {
        var particle = particles[index];
        int3 gridPos = (int3)math.floor((particle.position - gridMin) / cellSize);
        gridPos = math.clamp(gridPos, int3.zero, gridDimensions - 1);
        
        int gridIndex = gridPos.x + gridPos.y * gridDimensions.x + 
                       gridPos.z * gridDimensions.x * gridDimensions.y;
        
        particle.gridIndex = gridIndex;
        particles[index] = particle;
        gridIndices[index] = gridIndex;
        
        spatialGrid.Add(gridIndex, index);
    }
}

[BurstCompile]
public struct CalculateDensityJob : IJobParallelFor
{
    public NativeArray<FluidParticle> particles;
    [ReadOnly] public NativeMultiHashMap<int, int> spatialGrid;
    [ReadOnly] public float smoothingRadius;
    [ReadOnly] public float restDensity;
    [ReadOnly] public float gasConstant;
    [ReadOnly] public int3 gridDimensions;
    [ReadOnly] public float3 gridMin;
    [ReadOnly] public float cellSize;
    
    public void Execute(int index)
    {
        var particle = particles[index];
        float density = 0f;
        
        int3 gridPos = (int3)math.floor((particle.position - gridMin) / cellSize);
        
        // Check neighboring cells
        for (int x = -1; x <= 1; x++)
        {
            for (int y = -1; y <= 1; y++)
            {
                for (int z = -1; z <= 1; z++)
                {
                    int3 neighborGrid = gridPos + new int3(x, y, z);
                    if (math.any(neighborGrid < 0) || math.any(neighborGrid >= gridDimensions))
                        continue;
                    
                    int neighborIndex = neighborGrid.x + neighborGrid.y * gridDimensions.x + 
                                      neighborGrid.z * gridDimensions.x * gridDimensions.y;
                    
                    if (spatialGrid.TryGetFirstValue(neighborIndex, out int neighborParticle, out var iterator))
                    {
                        do
                        {
                            var neighbor = particles[neighborParticle];
                            float3 diff = particle.position - neighbor.position;
                            float distanceSquared = math.lengthsq(diff);
                            
                            density += SPHFluidSimulation.Poly6Kernel(distanceSquared, smoothingRadius);
                            
                        } while (spatialGrid.TryGetNextValue(out neighborParticle, ref iterator));
                    }
                }
            }
        }
        
        particle.density = density;
        particle.pressure = gasConstant * (density - restDensity);
        particles[index] = particle;
    }
}

[BurstCompile]
public struct CalculateForceJob : IJobParallelFor
{
    public NativeArray<FluidParticle> particles;
    [ReadOnly] public NativeMultiHashMap<int, int> spatialGrid;
    [ReadOnly] public float smoothingRadius;
    [ReadOnly] public float viscosity;
    [ReadOnly] public float3 gravity;
    [ReadOnly] public int3 gridDimensions;
    [ReadOnly] public float3 gridMin;
    [ReadOnly] public float cellSize;
    
    public void Execute(int index)
    {
        var particle = particles[index];
        float3 pressureForce = float3.zero;
        float3 viscosityForce = float3.zero;
        
        int3 gridPos = (int3)math.floor((particle.position - gridMin) / cellSize);
        
        // Check neighboring cells
        for (int x = -1; x <= 1; x++)
        {
            for (int y = -1; y <= 1; y++)
            {
                for (int z = -1; z <= 1; z++)
                {
                    int3 neighborGrid = gridPos + new int3(x, y, z);
                    if (math.any(neighborGrid < 0) || math.any(neighborGrid >= gridDimensions))
                        continue;
                    
                    int neighborIndex = neighborGrid.x + neighborGrid.y * gridDimensions.x + 
                                      neighborGrid.z * gridDimensions.x * gridDimensions.y;
                    
                    if (spatialGrid.TryGetFirstValue(neighborIndex, out int neighborParticle, out var iterator))
                    {
                        do
                        {
                            if (neighborParticle == index) continue;
                            
                            var neighbor = particles[neighborParticle];
                            float3 diff = particle.position - neighbor.position;
                            float distance = math.length(diff);
                            
                            if (distance < smoothingRadius && distance > 0f)
                            {
                                // Pressure force
                                float3 gradient = SPHFluidSimulation.SpikyGradient(diff, distance, smoothingRadius);
                                pressureForce -= gradient * (particle.pressure + neighbor.pressure) / (2f * neighbor.density);
                                
                                // Viscosity force
                                float laplacian = SPHFluidSimulation.ViscosityLaplacian(distance, smoothingRadius);
                                viscosityForce += (neighbor.velocity - particle.velocity) * laplacian / neighbor.density;
                            }
                            
                        } while (spatialGrid.TryGetNextValue(out neighborParticle, ref iterator));
                    }
                }
            }
        }
        
        particle.force = pressureForce + viscosityForce * viscosity + gravity;
        particles[index] = particle;
    }
}

[BurstCompile]
public struct IntegrateFluidJob : IJobParallelFor
{
    public NativeArray<FluidParticle> particles;
    public NativeArray<float3> positions;
    [ReadOnly] public float deltaTime;
    [ReadOnly] public float damping;
    [ReadOnly] public AABB bounds;
    
    public void Execute(int index)
    {
        var particle = particles[index];
        
        // Integrate velocity
        particle.velocity += particle.force * deltaTime;
        particle.velocity *= damping;
        
        // Integrate position
        particle.position += particle.velocity * deltaTime;
        
        // Boundary conditions
        if (particle.position.x < bounds.Min.x)
        {
            particle.position.x = bounds.Min.x;
            particle.velocity.x *= -0.5f;
        }
        if (particle.position.x > bounds.Max.x)
        {
            particle.position.x = bounds.Max.x;
            particle.velocity.x *= -0.5f;
        }
        
        if (particle.position.y < bounds.Min.y)
        {
            particle.position.y = bounds.Min.y;
            particle.velocity.y *= -0.5f;
        }
        if (particle.position.y > bounds.Max.y)
        {
            particle.position.y = bounds.Max.y;
            particle.velocity.y *= -0.5f;
        }
        
        if (particle.position.z < bounds.Min.z)
        {
            particle.position.z = bounds.Min.z;
            particle.velocity.z *= -0.5f;
        }
        if (particle.position.z > bounds.Max.z)
        {
            particle.position.z = bounds.Max.z;
            particle.velocity.z *= -0.5f;
        }
        
        particles[index] = particle;
        positions[index] = particle.position;
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Advanced Physics Simulation Generation

```
Create sophisticated Unity physics simulations using Mathematics package:
1. Custom constraint solvers for complex mechanical systems
2. Soft body deformation systems with realistic material properties
3. Advanced collision detection algorithms for non-convex shapes
4. Multi-threaded particle systems with complex interactions

Context: High-performance Unity game requiring realistic physics simulation
Focus: Job system optimization, burst compilation, mathematical accuracy
Requirements: 60fps performance, scalable to thousands of objects
```

### Procedural Animation Systems

```
Generate physics-based procedural animation systems:
1. Inverse kinematics solvers for character animation
2. Procedural cloth and hair simulation systems
3. Realistic water and fluid interaction with game objects
4. Dynamic rope and cable simulation with tension physics

Environment: Unity 2022.3 LTS with Mathematics and Job System
Goals: Realistic movement, performance optimization, artistic control
```

This comprehensive physics simulation framework provides the foundation for creating advanced, realistic physics systems in Unity games with optimal performance through job system integration and burst compilation.