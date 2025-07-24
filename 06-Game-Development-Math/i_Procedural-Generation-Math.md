# @i-Procedural-Generation-Math - Mathematical Foundations for Content Creation

## 🎯 Learning Objectives
- Master mathematical algorithms for procedural content generation
- Implement noise functions for natural-looking procedural systems
- Apply probability distributions for balanced random generation
- Optimize procedural algorithms for real-time performance in Unity

## 🔧 Core Procedural Mathematics

### Noise Functions for Natural Generation
**Perlin and Simplex noise for organic procedural content:**

```csharp
public class ProceduralNoise : MonoBehaviour
{
    [Header("Noise Generation Settings")]
    [SerializeField] private int terrainWidth = 256;
    [SerializeField] private int terrainHeight = 256;
    [SerializeField] private float noiseScale = 0.05f;
    [SerializeField] private int octaves = 4;
    [SerializeField] private float persistence = 0.5f;
    [SerializeField] private float lacunarity = 2f;
    
    // Generate heightmap using multi-octave Perlin noise
    public float[,] GenerateHeightMap()
    {
        float[,] heightMap = new float[terrainWidth, terrainHeight];
        
        for (int x = 0; x < terrainWidth; x++)
        {
            for (int y = 0; y < terrainHeight; y++)
            {
                float amplitude = 1f;
                float frequency = noiseScale;
                float noiseHeight = 0f;
                float maxValue = 0f;
                
                // Apply multiple octaves for detail
                for (int i = 0; i < octaves; i++)
                {
                    float sampleX = x * frequency;
                    float sampleY = y * frequency;
                    
                    float perlinValue = Mathf.PerlinNoise(sampleX, sampleY) * 2f - 1f;
                    noiseHeight += perlinValue * amplitude;
                    maxValue += amplitude;
                    
                    amplitude *= persistence;
                    frequency *= lacunarity;
                }
                
                heightMap[x, y] = noiseHeight / maxValue;
            }
        }
        
        return heightMap;
    }
    
    // 3D noise for volumetric generation (caves, density maps)
    public float Sample3DNoise(Vector3 position, float scale)
    {
        float xy = Mathf.PerlinNoise(position.x * scale, position.y * scale);
        float xz = Mathf.PerlinNoise(position.x * scale, position.z * scale);
        float yz = Mathf.PerlinNoise(position.y * scale, position.z * scale);
        
        return (xy + xz + yz) / 3f;
    }
}
```

### Advanced Randomization Systems
**Controlled randomness for balanced procedural generation:**

```csharp
public static class ProceduralRandom
{
    // Weighted random selection
    public static T WeightedRandomChoice<T>(T[] items, float[] weights)
    {
        if (items.Length != weights.Length)
            throw new System.ArgumentException("Items and weights arrays must have same length");
        
        float totalWeight = 0f;
        foreach (float weight in weights)
            totalWeight += weight;
        
        float randomValue = UnityEngine.Random.Range(0f, totalWeight);
        float currentWeight = 0f;
        
        for (int i = 0; i < items.Length; i++)
        {
            currentWeight += weights[i];
            if (randomValue <= currentWeight)
                return items[i];
        }
        
        return items[items.Length - 1]; // Fallback
    }
    
    // Gaussian (normal) distribution random
    public static float GaussianRandom(float mean = 0f, float standardDeviation = 1f)
    {
        // Box-Muller transformation
        static bool hasSpare = false;
        static float spare;
        
        if (hasSpare)
        {
            hasSpare = false;
            return spare * standardDeviation + mean;
        }
        
        hasSpare = true;
        float u1 = UnityEngine.Random.Range(0f, 1f);
        float u2 = UnityEngine.Random.Range(0f, 1f);
        
        float magnitude = standardDeviation * Mathf.Sqrt(-2f * Mathf.Log(u1));
        spare = magnitude * Mathf.Cos(2f * Mathf.PI * u2);
        
        return magnitude * Mathf.Sin(2f * Mathf.PI * u2) + mean;
    }
    
    // Poisson disk sampling for even distribution
    public static List<Vector2> PoissonDiskSampling(float radius, Vector2 regionSize, int numSamplesBeforeRejection = 30)
    {
        float cellSize = radius / Mathf.Sqrt(2);
        int[,] grid = new int[Mathf.CeilToInt(regionSize.x / cellSize), Mathf.CeilToInt(regionSize.y / cellSize)];
        List<Vector2> points = new List<Vector2>();
        List<Vector2> spawnPoints = new List<Vector2>();
        
        spawnPoints.Add(regionSize / 2);
        
        while (spawnPoints.Count > 0)
        {
            int spawnIndex = UnityEngine.Random.Range(0, spawnPoints.Count);
            Vector2 spawnCentre = spawnPoints[spawnIndex];
            bool candidateAccepted = false;
            
            for (int i = 0; i < numSamplesBeforeRejection; i++)
            {
                float angle = UnityEngine.Random.value * Mathf.PI * 2;
                Vector2 dir = new Vector2(Mathf.Sin(angle), Mathf.Cos(angle));
                Vector2 candidate = spawnCentre + dir * UnityEngine.Random.Range(radius, 2 * radius);
                
                if (IsValid(candidate, regionSize, cellSize, radius, points, grid))
                {
                    points.Add(candidate);
                    spawnPoints.Add(candidate);
                    grid[(int)(candidate.x / cellSize), (int)(candidate.y / cellSize)] = points.Count;
                    candidateAccepted = true;
                    break;
                }
            }
            
            if (!candidateAccepted)
            {
                spawnPoints.RemoveAt(spawnIndex);
            }
        }
        
        return points;
    }
    
    private static bool IsValid(Vector2 candidate, Vector2 sampleRegionSize, float cellSize, float radius, List<Vector2> points, int[,] grid)
    {
        if (candidate.x >= 0 && candidate.x < sampleRegionSize.x && candidate.y >= 0 && candidate.y < sampleRegionSize.y)
        {
            int cellX = (int)(candidate.x / cellSize);
            int cellY = (int)(candidate.y / cellSize);
            int searchStartX = Mathf.Max(0, cellX - 2);
            int searchEndX = Mathf.Min(cellX + 2, grid.GetLength(0) - 1);
            int searchStartY = Mathf.Max(0, cellY - 2);
            int searchEndY = Mathf.Min(cellY + 2, grid.GetLength(1) - 1);
            
            for (int x = searchStartX; x <= searchEndX; x++)
            {
                for (int y = searchStartY; y <= searchEndY; y++)
                {
                    int pointIndex = grid[x, y] - 1;
                    if (pointIndex != -1)
                    {
                        float sqrDst = (candidate - points[pointIndex]).sqrMagnitude;
                        if (sqrDst < radius * radius)
                        {
                            return false;
                        }
                    }
                }
            }
            return true;
        }
        return false;
    }
}
```

## 🚀 Cellular Automata for Complex Systems

### Conway's Game of Life Variations
**Rule-based procedural generation for cave systems and organic structures:**

```csharp
public class CellularAutomata : MonoBehaviour
{
    [Header("Cellular Automata Settings")]
    [SerializeField] private int mapWidth = 100;
    [SerializeField] private int mapHeight = 100;
    [SerializeField] private float initialFillPercent = 45f;
    [SerializeField] private int smoothingIterations = 5;
    
    private int[,] map;
    
    public int[,] GenerateCaveSystem()
    {
        map = new int[mapWidth, mapHeight];
        RandomFillMap();
        
        for (int i = 0; i < smoothingIterations; i++)
        {
            SmoothMap();
        }
        
        return map;
    }
    
    void RandomFillMap()
    {
        for (int x = 0; x < mapWidth; x++)
        {
            for (int y = 0; y < mapHeight; y++)
            {
                if (x == 0 || x == mapWidth - 1 || y == 0 || y == mapHeight - 1)
                {
                    map[x, y] = 1; // Wall border
                }
                else
                {
                    map[x, y] = (UnityEngine.Random.Range(0f, 100f) < initialFillPercent) ? 1 : 0;
                }
            }
        }
    }
    
    void SmoothMap()
    {
        int[,] newMap = new int[mapWidth, mapHeight];
        
        for (int x = 0; x < mapWidth; x++)
        {
            for (int y = 0; y < mapHeight; y++)
            {
                int neighbourWallTiles = GetSurroundingWallCount(x, y);
                
                if (neighbourWallTiles > 4)
                    newMap[x, y] = 1;
                else if (neighbourWallTiles < 4)
                    newMap[x, y] = 0;
                else
                    newMap[x, y] = map[x, y];
            }
        }
        
        map = newMap;
    }
    
    int GetSurroundingWallCount(int gridX, int gridY)
    {
        int wallCount = 0;
        
        for (int neighbourX = gridX - 1; neighbourX <= gridX + 1; neighbourX++)
        {
            for (int neighbourY = gridY - 1; neighbourY <= gridY + 1; neighbourY++)
            {
                if (neighbourX >= 0 && neighbourX < mapWidth && neighbourY >= 0 && neighbourY < mapHeight)
                {
                    if (neighbourX != gridX || neighbourY != gridY)
                    {
                        wallCount += map[neighbourX, neighbourY];
                    }
                }
                else
                {
                    wallCount++;
                }
            }
        }
        
        return wallCount;
    }
}
```

### L-Systems for Organic Growth
**Mathematical grammar systems for procedural plant and structure generation:**

```csharp
public class LSystemGenerator : MonoBehaviour
{
    [System.Serializable]
    public class LSystemRule
    {
        public char input;
        public string output;
    }
    
    [Header("L-System Settings")]
    [SerializeField] private string axiom = "F";
    [SerializeField] private LSystemRule[] rules;
    [SerializeField] private int iterations = 4;
    [SerializeField] private float angle = 25f;
    [SerializeField] private float length = 1f;
    
    public string GenerateLSystem()
    {
        string current = axiom;
        
        for (int i = 0; i < iterations; i++)
        {
            current = ApplyRules(current);
        }
        
        return current;
    }
    
    string ApplyRules(string input)
    {
        System.Text.StringBuilder result = new System.Text.StringBuilder();
        
        foreach (char c in input)
        {
            bool ruleApplied = false;
            
            foreach (LSystemRule rule in rules)
            {
                if (rule.input == c)
                {
                    result.Append(rule.output);
                    ruleApplied = true;
                    break;
                }
            }
            
            if (!ruleApplied)
            {
                result.Append(c);
            }
        }
        
        return result.ToString();
    }
    
    // Turtle graphics interpretation for 3D generation
    public List<Vector3> InterpretLSystemAs3D(string lSystem)
    {
        List<Vector3> points = new List<Vector3>();
        Stack<TurtleState> stateStack = new Stack<TurtleState>();
        
        TurtleState current = new TurtleState
        {
            position = Vector3.zero,
            direction = Vector3.up,
            right = Vector3.right,
            up = Vector3.forward
        };
        
        points.Add(current.position);
        
        foreach (char c in lSystem)
        {
            switch (c)
            {
                case 'F': // Forward
                    current.position += current.direction * length;
                    points.Add(current.position);
                    break;
                    
                case '+': // Turn right
                    current.direction = Quaternion.AngleAxis(angle, current.up) * current.direction;
                    current.right = Quaternion.AngleAxis(angle, current.up) * current.right;
                    break;
                    
                case '-': // Turn left
                    current.direction = Quaternion.AngleAxis(-angle, current.up) * current.direction;
                    current.right = Quaternion.AngleAxis(-angle, current.up) * current.right;
                    break;
                    
                case '[': // Push state
                    stateStack.Push(current);
                    break;
                    
                case ']': // Pop state
                    current = stateStack.Pop();
                    points.Add(current.position);
                    break;
            }
        }
        
        return points;
    }
    
    [System.Serializable]
    public struct TurtleState
    {
        public Vector3 position;
        public Vector3 direction;
        public Vector3 right;
        public Vector3 up;
    }
}
```

## 💡 Performance Optimization for Procedural Systems

### Efficient Generation Techniques
**Optimizing procedural algorithms for real-time performance:**

```csharp
public class OptimizedProceduralGeneration : MonoBehaviour
{
    [Header("Performance Settings")]
    [SerializeField] private int chunkSize = 16;
    [SerializeField] private int maxGenerationPerFrame = 5;
    
    private Dictionary<Vector2Int, bool> generatedChunks = new Dictionary<Vector2Int, bool>();
    private Queue<Vector2Int> generationQueue = new Queue<Vector2Int>();
    
    void Update()
    {
        // Limit generation per frame to maintain framerate
        int generated = 0;
        while (generationQueue.Count > 0 && generated < maxGenerationPerFrame)
        {
            Vector2Int chunkCoord = generationQueue.Dequeue();
            GenerateChunk(chunkCoord);
            generated++;
        }
    }
    
    // Async chunk generation using coroutines
    public IEnumerator GenerateChunkAsync(Vector2Int chunkCoord)
    {
        if (generatedChunks.ContainsKey(chunkCoord))
            yield break;
        
        // Generate in smaller sub-chunks to spread load
        int subChunkSize = chunkSize / 4;
        
        for (int subX = 0; subX < 4; subX++)
        {
            for (int subY = 0; subY < 4; subY++)
            {
                Vector2Int subChunkStart = new Vector2Int(
                    chunkCoord.x * chunkSize + subX * subChunkSize,
                    chunkCoord.y * chunkSize + subY * subChunkSize
                );
                
                GenerateSubChunk(subChunkStart, subChunkSize);
                yield return null; // Yield control back to Unity
            }
        }
        
        generatedChunks[chunkCoord] = true;
    }
    
    void GenerateChunk(Vector2Int chunkCoord)
    {
        StartCoroutine(GenerateChunkAsync(chunkCoord));
    }
    
    void GenerateSubChunk(Vector2Int start, int size)
    {
        // Actual procedural generation logic here
        // This is where you'd apply noise functions, cellular automata, etc.
        for (int x = start.x; x < start.x + size; x++)
        {
            for (int y = start.y; y < start.y + size; y++)
            {
                // Generate tile/voxel at position (x, y)
                float noiseValue = Mathf.PerlinNoise(x * 0.1f, y * 0.1f);
                // Process noise value...
            }
        }
    }
    
    // Memory-efficient noise caching
    private Dictionary<Vector2Int, float> noiseCache = new Dictionary<Vector2Int, float>();
    
    public float GetCachedNoise(int x, int y, float scale)
    {
        Vector2Int key = new Vector2Int(x, y);
        
        if (noiseCache.ContainsKey(key))
        {
            return noiseCache[key];
        }
        
        float noise = Mathf.PerlinNoise(x * scale, y * scale);
        
        // Limit cache size to prevent memory leaks
        if (noiseCache.Count > 10000)
        {
            noiseCache.Clear();
        }
        
        noiseCache[key] = noise;
        return noise;
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Advanced Procedural Algorithms
- **Prompt**: "Generate procedural dungeon layout algorithm using [specific constraints] and mathematical rules"
- **Automation**: Create rule-based systems for procedural content with AI-designed parameters
- **Analysis**: Optimize procedural generation algorithms for specific performance targets

### Dynamic Content Creation
- **Prompt**: "Design adaptive procedural system that generates content based on player skill level using probability distributions"
- **Integration**: Use AI to analyze player behavior and adjust procedural generation parameters
- **Quality**: Generate diverse procedural content with AI-driven variation systems

## 💡 Key Highlights

**⭐ Essential Procedural Concepts:**
- Noise functions (Perlin, Simplex) are fundamental for natural-looking procedural content
- Controlled randomness with probability distributions creates balanced generation
- Cellular automata excel at creating organic, cave-like structures

**🔧 Performance Optimization:**
- Async generation with coroutines prevents frame rate drops during content creation
- Noise value caching reduces redundant calculations in procedural systems
- Chunk-based generation enables infinite worlds with controlled memory usage

**🎮 Game Development Applications:**
- Terrain generation relies heavily on multi-octave noise functions
- Dungeon and level generation benefit from cellular automata and L-systems
- Item and loot distribution systems use weighted random selection

**⚡ Unity-Specific Integration:**
- Coroutines enable frame-rate friendly procedural generation
- ScriptableObjects can store procedural generation rules and parameters
- Job System can parallelize expensive procedural calculations for better performance