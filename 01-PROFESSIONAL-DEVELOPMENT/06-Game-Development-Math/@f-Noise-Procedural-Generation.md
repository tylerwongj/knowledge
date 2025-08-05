# @f-Noise-Procedural-Generation - Advanced Noise Functions and Procedural Mathematics

## 🎯 Learning Objectives
- Master noise functions and their applications in procedural generation
- Implement advanced mathematical techniques for creating realistic content
- Develop AI-enhanced understanding of randomness and controlled chaos in games
- Create systematic approach to procedural content generation and world building

## 🔧 Noise and Procedural Generation Architecture

### The NOISE Framework for Procedural Content
```
N - Natural: Create organic, natural-looking patterns and structures
O - Optimization: Implement efficient noise algorithms for real-time generation
I - Integration: Combine multiple noise functions for complex, layered results
S - Scaling: Apply noise at different scales and frequencies for detail variation
E - Evolution: Create dynamic, evolving content using time-based noise functions
```

### Unity Noise and Procedural Generation System
```csharp
using UnityEngine;
using System.Collections.Generic;
using System;

/// <summary>
/// Comprehensive noise and procedural generation system for Unity
/// Provides various noise functions, fractal algorithms, and procedural techniques
/// </summary>
public static class NoiseProceduralUtility
{
    public const float EPSILON = 0.0001f;
    
    #region Perlin Noise Variations
    
    /// <summary>
    /// Enhanced Perlin noise with octaves and persistence
    /// Essential for terrain generation and natural-looking patterns
    /// </summary>
    public static float FractalPerlinNoise(float x, float y, int octaves = 4, float persistence = 0.5f, float scale = 1f, float offsetX = 0f, float offsetY = 0f)
    {
        float total = 0f;
        float frequency = scale;
        float amplitude = 1f;
        float maxValue = 0f;
        
        for (int i = 0; i < octaves; i++)
        {
            total += Mathf.PerlinNoise((x + offsetX) * frequency, (y + offsetY) * frequency) * amplitude;
            
            maxValue += amplitude;
            amplitude *= persistence;
            frequency *= 2f;
        }
        
        return total / maxValue;
    }
    
    /// <summary>
    /// Ridged noise for mountain-like terrain features
    /// Perfect for creating sharp peaks and ridges
    /// </summary>
    public static float RidgedNoise(float x, float y, int octaves = 4, float persistence = 0.5f, float scale = 1f)
    {
        float total = 0f;
        float frequency = scale;
        float amplitude = 1f;
        float maxValue = 0f;
        
        for (int i = 0; i < octaves; i++)
        {
            float noise = Mathf.PerlinNoise(x * frequency, y * frequency);
            noise = 1f - Mathf.Abs(noise * 2f - 1f); // Create ridges
            noise = noise * noise; // Sharpen ridges
            
            total += noise * amplitude;
            maxValue += amplitude;
            amplitude *= persistence;
            frequency *= 2f;
        }
        
        return total / maxValue;
    }
    
    /// <summary>
    /// Billowy noise for cloud-like structures
    /// Creates soft, rounded features perfect for clouds and organic shapes
    /// </summary>
    public static float BillowyNoise(float x, float y, int octaves = 4, float persistence = 0.5f, float scale = 1f)
    {
        float total = 0f;
        float frequency = scale;
        float amplitude = 1f;
        float maxValue = 0f;
        
        for (int i = 0; i < octaves; i++)
        {
            float noise = Mathf.PerlinNoise(x * frequency, y * frequency);
            noise = Mathf.Abs(noise * 2f - 1f); // Create billowy effect
            
            total += noise * amplitude;
            maxValue += amplitude;
            amplitude *= persistence;
            frequency *= 2f;
        }
        
        return total / maxValue;
    }
    
    /// <summary>
    /// Turbulence noise for chaotic, swirling patterns
    /// Excellent for fire, smoke, and turbulent fluid effects
    /// </summary>
    public static float TurbulenceNoise(float x, float y, int octaves = 4, float persistence = 0.5f, float scale = 1f)
    {
        float total = 0f;
        float frequency = scale;
        float amplitude = 1f;
        
        for (int i = 0; i < octaves; i++)
        {
            total += Mathf.Abs(Mathf.PerlinNoise(x * frequency, y * frequency) - 0.5f) * amplitude;
            amplitude *= persistence;
            frequency *= 2f;
        }
        
        return total;
    }
    
    #endregion
    
    #region Simplex Noise Implementation
    
    // Simplex noise implementation for better quality and performance
    private static int[] permutation = {
        151,160,137,91,90,15,131,13,201,95,96,53,194,233,7,225,140,36,103,30,69,142,
        8,99,37,240,21,10,23,190,6,148,247,120,234,75,0,26,197,62,94,252,219,203,117,
        35,11,32,57,177,33,88,237,149,56,87,174,20,125,136,171,168,68,175,74,165,71,
        134,139,48,27,166,77,146,158,231,83,111,229,122,60,211,133,230,220,105,92,41,
        55,46,245,40,244,102,143,54,65,25,63,161,1,216,80,73,209,76,132,187,208,89,
        18,169,200,196,135,130,116,188,159,86,164,100,109,198,173,186,3,64,52,217,226,
        250,124,123,5,202,38,147,118,126,255,82,85,212,207,206,59,227,47,16,58,17,182,
        189,28,42,223,183,170,213,119,248,152,2,44,154,163,70,221,153,101,155,167,43,
        172,9,129,22,39,253,19,98,108,110,79,113,224,232,178,185,112,104,218,246,97,
        228,251,34,242,193,238,210,144,12,191,179,162,241,81,51,145,235,249,14,239,
        107,49,192,214,31,181,199,106,157,184,84,204,176,115,121,50,45,127,4,150,254,
        138,236,205,93,222,114,67,29,24,72,243,141,128,195,78,66,215,61,156,180
    };
    
    private static int[] p = new int[512];
    
    static NoiseProceduralUtility()
    {
        for (int i = 0; i < 512; i++)
        {
            p[i] = permutation[i % 256];
        }
    }
    
    /// <summary>
    /// Improved simplex noise implementation
    /// Higher quality than Perlin noise with better isotropy
    /// </summary>
    public static float SimplexNoise(float x, float y)
    {
        float n0, n1, n2; // Noise contributions from the three corners
        
        // Skew the input space to determine which simplex cell we're in
        float F2 = 0.5f * (Mathf.Sqrt(3.0f) - 1.0f);
        float s = (x + y) * F2; // Hairy factor for 2D
        int i = Mathf.FloorToInt(x + s);
        int j = Mathf.FloorToInt(y + s);
        
        float G2 = (3.0f - Mathf.Sqrt(3.0f)) / 6.0f;
        float t = (i + j) * G2;
        float X0 = i - t; // Unskew the cell origin back to (x,y) space
        float Y0 = j - t;
        float x0 = x - X0; // The x,y distances from the cell origin
        float y0 = y - Y0;
        
        // For the 2D case, the simplex shape is an equilateral triangle.
        // Determine which simplex we are in.
        int i1, j1; // Offsets for second (middle) corner of simplex in (i,j) coords
        if (x0 > y0) { i1 = 1; j1 = 0; } // lower triangle, XY order: (0,0)->(1,0)->(1,1)
        else { i1 = 0; j1 = 1; }      // upper triangle, YX order: (0,0)->(0,1)->(1,1)
        
        // A step of (1,0) in (i,j) means a step of (1-c,-c) in (x,y), and
        // a step of (0,1) in (i,j) means a step of (-c,1-c) in (x,y), where
        // c = (3-sqrt(3))/6
        float x1 = x0 - i1 + G2; // Offsets for middle corner in (x,y) unskewed coords
        float y1 = y0 - j1 + G2;
        float x2 = x0 - 1.0f + 2.0f * G2; // Offsets for last corner in (x,y) unskewed coords
        float y2 = y0 - 1.0f + 2.0f * G2;
        
        // Work out the hashed gradient indices of the three simplex corners
        int ii = i & 255;
        int jj = j & 255;
        int gi0 = p[ii + p[jj]] % 12;
        int gi1 = p[ii + i1 + p[jj + j1]] % 12;
        int gi2 = p[ii + 1 + p[jj + 1]] % 12;
        
        // Calculate the contribution from the three corners
        float t0 = 0.5f - x0 * x0 - y0 * y0;
        if (t0 < 0) n0 = 0.0f;
        else
        {
            t0 *= t0;
            n0 = t0 * t0 * Dot(grad3[gi0], x0, y0);  // (x,y) of grad3 used for 2D gradient
        }
        
        float t1 = 0.5f - x1 * x1 - y1 * y1;
        if (t1 < 0) n1 = 0.0f;
        else
        {
            t1 *= t1;
            n1 = t1 * t1 * Dot(grad3[gi1], x1, y1);
        }
        
        float t2 = 0.5f - x2 * x2 - y2 * y2;
        if (t2 < 0) n2 = 0.0f;
        else
        {
            t2 *= t2;
            n2 = t2 * t2 * Dot(grad3[gi2], x2, y2);
        }
        
        // Add contributions from each corner to get the final noise value.
        // The result is scaled to return values in the interval [-1,1].
        return 70.0f * (n0 + n1 + n2);
    }
    
    private static int[,] grad3 = new int[12, 3] {
        {1,1,0},{-1,1,0},{1,-1,0},{-1,-1,0},
        {1,0,1},{-1,0,1},{1,0,-1},{-1,0,-1},
        {0,1,1},{0,-1,1},{0,1,-1},{0,-1,-1}
    };
    
    private static float Dot(int[] g, float x, float y)
    {
        return g[0] * x + g[1] * y;
    }
    
    #endregion
    
    #region Voronoi Noise
    
    /// <summary>
    /// Voronoi noise for cellular patterns
    /// Perfect for stone textures, cell structures, and organic patterns
    /// </summary>
    public static float VoronoiNoise(float x, float y, float scale = 1f, bool useDistance = true)
    {
        x *= scale;
        y *= scale;
        
        int xInt = Mathf.FloorToInt(x);
        int yInt = Mathf.FloorToInt(y);
        
        float minDistance = float.MaxValue;
        Vector2 closestPoint = Vector2.zero;
        
        // Check surrounding cells
        for (int xi = -1; xi <= 1; xi++)
        {
            for (int yi = -1; yi <= 1; yi++)
            {
                Vector2 cellPoint = GetVoronoiPoint(xInt + xi, yInt + yi);
                cellPoint.x += xInt + xi;
                cellPoint.y += yInt + yi;
                
                float distance = Vector2.Distance(new Vector2(x, y), cellPoint);
                
                if (distance < minDistance)
                {
                    minDistance = distance;
                    closestPoint = cellPoint;
                }
            }
        }
        
        if (useDistance)
        {
            return Mathf.Clamp01(minDistance);
        }
        else
        {
            // Return feature point value
            return (closestPoint.x + closestPoint.y) * 0.5f % 1f;
        }
    }
    
    private static Vector2 GetVoronoiPoint(int x, int y)
    {
        // Generate deterministic random point in cell
        int hash = x * 374761393 + y * 668265263;
        hash = (hash ^ (hash >> 13)) * 1274126177;
        
        float fx = (hash & 0xFFFF) / 65535f;
        hash = (hash ^ (hash >> 16)) * 1274126177;
        float fy = (hash & 0xFFFF) / 65535f;
        
        return new Vector2(fx, fy);
    }
    
    /// <summary>
    /// Worley noise (cellular noise) with distance function variants
    /// Provides multiple distance metrics for different cellular patterns
    /// </summary>
    public static float WorleyNoise(float x, float y, float scale = 1f, DistanceFunction distanceFunc = DistanceFunction.Euclidean, int featurePoint = 0)
    {
        x *= scale;
        y *= scale;
        
        int xInt = Mathf.FloorToInt(x);
        int yInt = Mathf.FloorToInt(y);
        
        List<float> distances = new List<float>();
        
        // Check surrounding cells
        for (int xi = -1; xi <= 1; xi++)
        {
            for (int yi = -1; yi <= 1; yi++)
            {
                Vector2 cellPoint = GetVoronoiPoint(xInt + xi, yInt + yi);
                cellPoint.x += xInt + xi;
                cellPoint.y += yInt + yi;
                
                float distance = CalculateDistance(new Vector2(x, y), cellPoint, distanceFunc);
                distances.Add(distance);
            }
        }
        
        distances.Sort();
        
        if (featurePoint < distances.Count)
        {
            return Mathf.Clamp01(distances[featurePoint]);
        }
        
        return 1f;
    }
    
    public enum DistanceFunction
    {
        Euclidean,
        Manhattan,
        Chebyshev,
        Minkowski
    }
    
    private static float CalculateDistance(Vector2 a, Vector2 b, DistanceFunction func)
    {
        switch (func)
        {
            case DistanceFunction.Euclidean:
                return Vector2.Distance(a, b);
            
            case DistanceFunction.Manhattan:
                return Mathf.Abs(a.x - b.x) + Mathf.Abs(a.y - b.y);
            
            case DistanceFunction.Chebyshev:
                return Mathf.Max(Mathf.Abs(a.x - b.x), Mathf.Abs(a.y - b.y));
            
            case DistanceFunction.Minkowski:
                float p = 4f; // Minkowski parameter
                return Mathf.Pow(Mathf.Pow(Mathf.Abs(a.x - b.x), p) + Mathf.Pow(Mathf.Abs(a.y - b.y), p), 1f / p);
            
            default:
                return Vector2.Distance(a, b);
        }
    }
    
    #endregion
    
    #region Domain Warping
    
    /// <summary>
    /// Domain warping for complex, organic noise patterns
    /// Creates swirling, flowing patterns by distorting the input coordinates
    /// </summary>
    public static float DomainWarpedNoise(float x, float y, float warpStrength = 0.1f, float warpScale = 1f)
    {
        // Create warping offsets using noise
        float warpX = FractalPerlinNoise(x * warpScale, y * warpScale, 3, 0.5f, 0.02f) * warpStrength;
        float warpY = FractalPerlinNoise(x * warpScale + 1000f, y * warpScale + 1000f, 3, 0.5f, 0.02f) * warpStrength;
        
        // Apply warping to the original coordinates
        return FractalPerlinNoise(x + warpX, y + warpY, 4, 0.5f, 0.01f);
    }
    
    /// <summary>
    /// Multi-layer domain warping for extremely complex patterns
    /// Applies multiple layers of warping for ultra-realistic terrain and textures
    /// </summary>
    public static float MultilayerDomainWarp(float x, float y, int warpLayers = 3, float warpStrength = 0.1f)
    {
        float warpedX = x;
        float warpedY = y;
        
        // Apply multiple layers of warping
        for (int layer = 0; layer < warpLayers; layer++)
        {
            float layerScale = Mathf.Pow(2f, layer);
            float layerStrength = warpStrength / layerScale;
            
            float offsetX = layer * 1000f;
            float offsetY = layer * 2000f;
            
            float warpX = FractalPerlinNoise(warpedX * layerScale + offsetX, warpedY * layerScale + offsetY, 2, 0.5f, 0.02f) * layerStrength;
            float warpY = FractalPerlinNoise(warpedX * layerScale + offsetX + 500f, warpedY * layerScale + offsetY + 500f, 2, 0.5f, 0.02f) * layerStrength;
            
            warpedX += warpX;
            warpedY += warpY;
        }
        
        return FractalPerlinNoise(warpedX, warpedY, 5, 0.5f, 0.01f);
    }
    
    #endregion
    
    #region Noise Combination and Masking
    
    /// <summary>
    /// Combine multiple noise functions using various blending modes
    /// Essential for creating complex, layered procedural content
    /// </summary>
    public static float CombineNoise(float x, float y, NoiseLayer[] layers)
    {
        if (layers == null || layers.Length == 0) return 0f;
        
        float result = layers[0].GetValue(x, y) * layers[0].weight;
        
        for (int i = 1; i < layers.Length; i++)
        {
            float layerValue = layers[i].GetValue(x, y);
            
            switch (layers[i].blendMode)
            {
                case BlendMode.Add:
                    result += layerValue * layers[i].weight;
                    break;
                
                case BlendMode.Multiply:
                    result *= (layerValue * layers[i].weight);
                    break;
                
                case BlendMode.Subtract:
                    result -= layerValue * layers[i].weight;
                    break;
                
                case BlendMode.Divide:
                    if (Mathf.Abs(layerValue) > EPSILON)
                        result /= (layerValue * layers[i].weight);
                    break;
                
                case BlendMode.Max:
                    result = Mathf.Max(result, layerValue * layers[i].weight);
                    break;
                
                case BlendMode.Min:
                    result = Mathf.Min(result, layerValue * layers[i].weight);
                    break;
                
                case BlendMode.Screen:
                    result = 1f - (1f - result) * (1f - layerValue * layers[i].weight);
                    break;
                
                case BlendMode.Overlay:
                    if (result < 0.5f)
                        result = 2f * result * (layerValue * layers[i].weight);
                    else
                        result = 1f - 2f * (1f - result) * (1f - layerValue * layers[i].weight);
                    break;
            }
        }
        
        return Mathf.Clamp01(result);
    }
    
    public enum BlendMode
    {
        Add,
        Multiply,
        Subtract,
        Divide,
        Max,
        Min,
        Screen,
        Overlay
    }
    
    public enum NoiseType
    {
        Perlin,
        Simplex,
        Ridged,
        Billowy,
        Turbulence,
        Voronoi,
        Worley,
        DomainWarped
    }
    
    [Serializable]
    public class NoiseLayer
    {
        public NoiseType noiseType = NoiseType.Perlin;
        public BlendMode blendMode = BlendMode.Add;
        public float weight = 1f;
        public float scale = 1f;
        public int octaves = 4;
        public float persistence = 0.5f;
        public Vector2 offset = Vector2.zero;
        public float warpStrength = 0.1f;
        public DistanceFunction distanceFunction = DistanceFunction.Euclidean;
        public int featurePoint = 0;
        
        public float GetValue(float x, float y)
        {
            float adjustedX = (x + offset.x) * scale;
            float adjustedY = (y + offset.y) * scale;
            
            switch (noiseType)
            {
                case NoiseType.Perlin:
                    return FractalPerlinNoise(adjustedX, adjustedY, octaves, persistence, 1f);
                
                case NoiseType.Simplex:
                    return (SimplexNoise(adjustedX, adjustedY) + 1f) * 0.5f; // Normalize to 0-1
                
                case NoiseType.Ridged:
                    return RidgedNoise(adjustedX, adjustedY, octaves, persistence, 1f);
                
                case NoiseType.Billowy:
                    return BillowyNoise(adjustedX, adjustedY, octaves, persistence, 1f);
                
                case NoiseType.Turbulence:
                    return TurbulenceNoise(adjustedX, adjustedY, octaves, persistence, 1f);
                
                case NoiseType.Voronoi:
                    return VoronoiNoise(adjustedX, adjustedY, 1f, true);
                
                case NoiseType.Worley:
                    return WorleyNoise(adjustedX, adjustedY, 1f, distanceFunction, featurePoint);
                
                case NoiseType.DomainWarped:
                    return DomainWarpedNoise(adjustedX, adjustedY, warpStrength, 1f);
                
                default:
                    return 0f;
            }
        }
    }
    
    #endregion
    
    #region Erosion Simulation
    
    /// <summary>
    /// Simulate hydraulic erosion for realistic terrain modification
    /// Creates natural valley and river formations in height maps
    /// </summary>
    public static void HydraulicErosion(float[,] heightMap, int iterations = 100, float evaporationRate = 0.01f, float depositionRate = 0.3f, float minSlope = 0.01f)
    {
        int width = heightMap.GetLength(0);
        int height = heightMap.GetLength(1);
        
        for (int iteration = 0; iteration < iterations; iteration++)
        {
            // Pick random starting point
            int x = UnityEngine.Random.Range(1, width - 1);
            int y = UnityEngine.Random.Range(1, height - 1);
            
            float water = 1f;
            float sediment = 0f;
            float speed = 1f;
            Vector2 velocity = Vector2.zero;
            Vector2 position = new Vector2(x, y);
            
            // Simulate water droplet path
            for (int step = 0; step < 200; step++)
            {
                int posX = Mathf.FloorToInt(position.x);
                int posY = Mathf.FloorToInt(position.y);
                
                if (posX < 1 || posX >= width - 1 || posY < 1 || posY >= height - 1)
                    break;
                
                // Calculate gradient
                Vector2 gradient = CalculateGradient(heightMap, position);
                
                // Update velocity and position
                velocity = velocity * 0.9f + gradient * speed;
                position += velocity;
                
                // Calculate height at new position
                float newHeight = InterpolateHeight(heightMap, position);
                float heightDifference = InterpolateHeight(heightMap, position - velocity) - newHeight;
                
                // Calculate carrying capacity
                float carryingCapacity = Mathf.Max(-heightDifference * speed * water, minSlope);
                
                // Erosion or deposition
                if (sediment > carryingCapacity || heightDifference < 0)
                {
                    // Deposition
                    float depositionAmount = Mathf.Min(sediment - carryingCapacity, -heightDifference);
                    depositionAmount *= depositionRate;
                    
                    ApplyHeightChange(heightMap, position, depositionAmount);
                    sediment -= depositionAmount;
                }
                else
                {
                    // Erosion
                    float erosionAmount = Mathf.Min((carryingCapacity - sediment), heightDifference);
                    erosionAmount *= 0.1f; // Erosion rate
                    
                    ApplyHeightChange(heightMap, position, -erosionAmount);
                    sediment += erosionAmount;
                }
                
                // Evaporation
                water *= (1f - evaporationRate);
                if (water < 0.01f) break;
            }
        }
    }
    
    private static Vector2 CalculateGradient(float[,] heightMap, Vector2 position)
    {
        int x = Mathf.FloorToInt(position.x);
        int y = Mathf.FloorToInt(position.y);
        
        float gradX = heightMap[x + 1, y] - heightMap[x - 1, y];
        float gradY = heightMap[x, y + 1] - heightMap[x, y - 1];
        
        return new Vector2(gradX, gradY) * 0.5f;
    }
    
    private static float InterpolateHeight(float[,] heightMap, Vector2 position)
    {
        int x = Mathf.FloorToInt(position.x);
        int y = Mathf.FloorToInt(position.y);
        
        if (x < 0 || x >= heightMap.GetLength(0) - 1 || y < 0 || y >= heightMap.GetLength(1) - 1)
            return 0f;
        
        float fracX = position.x - x;
        float fracY = position.y - y;
        
        float h00 = heightMap[x, y];
        float h10 = heightMap[x + 1, y];
        float h01 = heightMap[x, y + 1];
        float h11 = heightMap[x + 1, y + 1];
        
        float h0 = Mathf.Lerp(h00, h10, fracX);
        float h1 = Mathf.Lerp(h01, h11, fracX);
        
        return Mathf.Lerp(h0, h1, fracY);
    }
    
    private static void ApplyHeightChange(float[,] heightMap, Vector2 position, float change)
    {
        int x = Mathf.FloorToInt(position.x);
        int y = Mathf.FloorToInt(position.y);
        
        if (x < 0 || x >= heightMap.GetLength(0) || y < 0 || y >= heightMap.GetLength(1))
            return;
        
        heightMap[x, y] += change;
    }
    
    #endregion
    
    #region Curve and Spline Generation
    
    /// <summary>
    /// Generate smooth curves using Catmull-Rom splines
    /// Perfect for creating natural paths, roads, and organic shapes
    /// </summary>
    public static List<Vector2> GenerateCatmullRomSpline(List<Vector2> controlPoints, int resolution = 10)
    {
        if (controlPoints.Count < 4) return controlPoints;
        
        List<Vector2> splinePoints = new List<Vector2>();
        
        for (int i = 0; i < controlPoints.Count - 3; i++)
        {
            for (int j = 0; j < resolution; j++)
            {
                float t = (float)j / resolution;
                Vector2 point = CatmullRomInterpolation(
                    controlPoints[i],
                    controlPoints[i + 1],
                    controlPoints[i + 2],
                    controlPoints[i + 3],
                    t
                );
                splinePoints.Add(point);
            }
        }
        
        return splinePoints;
    }
    
    private static Vector2 CatmullRomInterpolation(Vector2 p0, Vector2 p1, Vector2 p2, Vector2 p3, float t)
    {
        float t2 = t * t;
        float t3 = t2 * t;
        
        return 0.5f * (
            (2f * p1) +
            (-p0 + p2) * t +
            (2f * p0 - 5f * p1 + 4f * p2 - p3) * t2 +
            (-p0 + 3f * p1 - 3f * p2 + p3) * t3
        );
    }
    
    /// <summary>
    /// Generate procedural river networks using noise-guided paths
    /// Creates realistic branching river systems for terrain generation
    /// </summary>
    public static List<List<Vector2>> GenerateRiverNetwork(Vector2 source, Vector2 oceanDirection, int maxBranches = 5, float noiseScale = 0.1f)
    {
        var rivers = new List<List<Vector2>>();
        var queue = new Queue<(Vector2 start, Vector2 direction, int generation)>();
        
        queue.Enqueue((source, oceanDirection, 0));
        
        while (queue.Count > 0 && rivers.Count < maxBranches)
        {
            var (currentStart, currentDirection, generation) = queue.Dequeue();
            
            var riverPath = new List<Vector2>();
            Vector2 currentPos = currentStart;
            Vector2 direction = currentDirection.normalized;
            
            // Generate river path
            for (int step = 0; step < 100; step++)
            {
                riverPath.Add(currentPos);
                
                // Add noise to direction for natural meandering
                Vector2 noiseOffset = new Vector2(
                    FractalPerlinNoise(currentPos.x * noiseScale, currentPos.y * noiseScale + 1000f, 3, 0.5f, 1f) - 0.5f,
                    FractalPerlinNoise(currentPos.x * noiseScale + 1000f, currentPos.y * noiseScale, 3, 0.5f, 1f) - 0.5f
                ) * 0.3f;
                
                direction = (direction + noiseOffset).normalized;
                currentPos += direction * 2f;
                
                // Check for branching
                if (generation < 2 && step > 20 && step % 30 == 0 && UnityEngine.Random.value < 0.3f)
                {
                    Vector2 branchDirection = Quaternion.Euler(0, 0, UnityEngine.Random.Range(-45f, 45f)) * direction;
                    queue.Enqueue((currentPos, branchDirection, generation + 1));
                }
                
                // Stop if we've gone far enough
                if (Vector2.Distance(currentStart, currentPos) > 50f)
                    break;
            }
            
            rivers.Add(riverPath);
        }
        
        return rivers;
    }
    
    #endregion
}

/// <summary>
/// Practical noise and procedural generation examples for game development
/// Demonstrates real-world application of procedural techniques
/// </summary>
public class NoiseProceduralExamples : MonoBehaviour
{
    [Header("Terrain Generation")]
    public int terrainWidth = 256;
    public int terrainHeight = 256;
    public float terrainScale = 0.02f;
    public Material terrainMaterial;
    
    [Header("Noise Settings")]
    public NoiseProceduralUtility.NoiseLayer[] noiseLayers = new NoiseProceduralUtility.NoiseLayer[]
    {
        new NoiseProceduralUtility.NoiseLayer()
        {
            noiseType = NoiseProceduralUtility.NoiseType.Perlin,
            blendMode = NoiseProceduralUtility.BlendMode.Add,
            weight = 1f,
            scale = 0.02f,
            octaves = 4,
            persistence = 0.5f
        }
    };
    
    [Header("Texture Generation")]
    public int textureSize = 512;
    public Renderer targetRenderer;
    
    [Header("Animation Settings")]
    public bool animateNoise = false;
    public float animationSpeed = 1f;
    
    [Header("Erosion Settings")]
    public bool applyErosion = false;
    public int erosionIterations = 1000;
    
    private Texture2D generatedTexture;
    private Terrain generatedTerrain;
    private float animationTime = 0f;
    
    void Start()
    {
        GenerateProceduralContent();
    }
    
    void Update()
    {
        if (animateNoise)
        {
            animationTime += Time.deltaTime * animationSpeed;
            UpdateAnimatedNoise();
        }
    }
    
    #region Terrain Generation
    
    /// <summary>
    /// Example: Generate procedural terrain using multiple noise layers
    /// Demonstrates complex terrain creation with various noise functions
    /// </summary>
    void GenerateProceduralContent()
    {
        // Generate height map
        float[,] heightMap = GenerateHeightMap();
        
        // Apply erosion if enabled
        if (applyErosion)
        {
            NoiseProceduralUtility.HydraulicErosion(heightMap, erosionIterations);
        }
        
        // Create terrain mesh
        CreateTerrainFromHeightMap(heightMap);
        
        // Generate texture
        GenerateProceduralTexture();
    }
    
    float[,] GenerateHeightMap()
    {
        float[,] heightMap = new float[terrainWidth, terrainHeight];
        
        for (int x = 0; x < terrainWidth; x++)
        {
            for (int y = 0; y < terrainHeight; y++)
            {
                float worldX = x * terrainScale;
                float worldY = y * terrainScale;
                
                // Combine multiple noise layers
                float height = NoiseProceduralUtility.CombineNoise(worldX, worldY, noiseLayers);
                heightMap[x, y] = height;
            }
        }
        
        return heightMap;
    }
    
    void CreateTerrainFromHeightMap(float[,] heightMap)
    {
        // Create terrain data
        TerrainData terrainData = new TerrainData();
        terrainData.heightmapResolution = terrainWidth;
        terrainData.size = new Vector3(terrainWidth, 30f, terrainHeight);
        terrainData.SetHeights(0, 0, heightMap);
        
        // Create terrain GameObject
        GameObject terrainObject = Terrain.CreateTerrainGameObject(terrainData);
        terrainObject.transform.position = Vector3.zero;
        
        generatedTerrain = terrainObject.GetComponent<Terrain>();
        
        if (terrainMaterial != null)
        {
            generatedTerrain.materialTemplate = terrainMaterial;
        }
    }
    
    #endregion
    
    #region Texture Generation
    
    /// <summary>
    /// Example: Generate procedural textures using noise functions
    /// Demonstrates real-time texture creation for materials and surfaces
    /// </summary>
    void GenerateProceduralTexture()
    {
        if (generatedTexture == null)
        {
            generatedTexture = new Texture2D(textureSize, textureSize);
        }
        
        Color[] pixels = new Color[textureSize * textureSize];
        
        for (int x = 0; x < textureSize; x++)
        {
            for (int y = 0; y < textureSize; y++)
            {
                float worldX = (float)x / textureSize;
                float worldY = (float)y / textureSize;
                
                // Generate different texture channels using different noise types
                float r = NoiseProceduralUtility.FractalPerlinNoise(worldX * 8f, worldY * 8f, 4, 0.5f, 1f, animationTime * 0.1f);
                float g = NoiseProceduralUtility.RidgedNoise(worldX * 4f, worldY * 4f, 3, 0.6f, 1f);
                float b = NoiseProceduralUtility.VoronoiNoise(worldX, worldY, 16f);
                
                // Combine channels for complex texture
                float combinedValue = NoiseProceduralUtility.CombineNoise(worldX * 10f, worldY * 10f, noiseLayers);
                
                Color pixelColor = new Color(r, g, b, 1f);
                pixelColor = Color.Lerp(pixelColor, Color.white * combinedValue, 0.5f);
                
                pixels[y * textureSize + x] = pixelColor;
            }
        }
        
        generatedTexture.SetPixels(pixels);
        generatedTexture.Apply();
        
        // Apply to target renderer
        if (targetRenderer != null)
        {
            targetRenderer.material.mainTexture = generatedTexture;
        }
    }
    
    void UpdateAnimatedNoise()
    {
        if (targetRenderer != null)
        {
            GenerateProceduralTexture();
        }
    }
    
    #endregion
    
    #region Vegetation Placement
    
    /// <summary>
    /// Example: Procedural vegetation placement using noise-based distribution
    /// Demonstrates natural object placement for environment generation
    /// </summary>
    public void PlaceVegetation(GameObject[] vegetationPrefabs, int vegetationCount = 1000)
    {
        if (vegetationPrefabs == null || vegetationPrefabs.Length == 0) return;
        
        for (int i = 0; i < vegetationCount; i++)
        {
            // Generate random position
            Vector2 position = new Vector2(
                UnityEngine.Random.Range(0f, terrainWidth * terrainScale),
                UnityEngine.Random.Range(0f, terrainHeight * terrainScale)
            );
            
            // Use noise to determine placement probability
            float density = NoiseProceduralUtility.FractalPerlinNoise(position.x * 0.05f, position.y * 0.05f, 3, 0.5f, 1f);
            float clusterNoise = NoiseProceduralUtility.VoronoiNoise(position.x, position.y, 0.1f);
            
            // Combine noise functions for natural distribution
            float placementProbability = density * 0.7f + clusterNoise * 0.3f;
            
            if (placementProbability > 0.4f)
            {
                // Select vegetation type based on noise
                int vegetationType = Mathf.FloorToInt(NoiseProceduralUtility.SimplexNoise(position.x * 0.1f, position.y * 0.1f) * vegetationPrefabs.Length);
                vegetationType = Mathf.Clamp(vegetationType, 0, vegetationPrefabs.Length - 1);
                
                // Get terrain height at position
                float terrainHeight = GetTerrainHeightAtPosition(position);
                Vector3 worldPosition = new Vector3(position.x, terrainHeight, position.y);
                
                // Random rotation and scale
                Quaternion rotation = Quaternion.Euler(0, UnityEngine.Random.Range(0f, 360f), 0);
                float scale = UnityEngine.Random.Range(0.8f, 1.2f);
                
                GameObject vegetation = Instantiate(vegetationPrefabs[vegetationType], worldPosition, rotation);
                vegetation.transform.localScale = Vector3.one * scale;
                vegetation.transform.parent = transform;
            }
        }
    }
    
    float GetTerrainHeightAtPosition(Vector2 position)
    {
        if (generatedTerrain != null)
        {
            return generatedTerrain.SampleHeight(new Vector3(position.x, 0, position.y));
        }
        
        // Fallback to noise-based height
        return NoiseProceduralUtility.CombineNoise(position.x * terrainScale, position.y * terrainScale, noiseLayers) * 30f;
    }
    
    #endregion
    
    #region Cave Generation
    
    /// <summary>
    /// Example: Generate cave systems using 3D noise
    /// Demonstrates volumetric procedural generation for underground spaces
    /// </summary>
    public void GenerateCaveSystem(int caveWidth = 50, int caveHeight = 20, int caveDepth = 50, float caveThreshold = 0.4f)
    {
        bool[,,,] caveData = new bool[caveWidth, caveHeight, caveDepth, 1];
        
        for (int x = 0; x < caveWidth; x++)
        {
            for (int y = 0; y < caveHeight; y++)
            {
                for (int z = 0; z < caveDepth; z++)
                {
                    float worldX = x * 0.1f;
                    float worldY = y * 0.15f;
                    float worldZ = z * 0.1f;
                    
                    // Create main cave structure
                    float caveNoise = NoiseProceduralUtility.FractalPerlinNoise(worldX, worldZ, 4, 0.5f, 1f);
                    float verticalFactor = 1f - Mathf.Abs((float)y / caveHeight - 0.5f) * 2f; // Flatten at top/bottom
                    
                    // Add detailed cave features
                    float detailNoise = NoiseProceduralUtility.TurbulenceNoise(worldX * 2f, worldZ * 2f, 3, 0.6f, 1f);
                    float tunnelNoise = NoiseProceduralUtility.RidgedNoise(worldX * 0.5f, worldZ * 0.5f, 2, 0.7f, 1f);
                    
                    // Combine noise functions
                    float combinedNoise = (caveNoise * 0.6f + detailNoise * 0.3f + tunnelNoise * 0.1f) * verticalFactor;
                    
                    // Determine if this voxel is air (cave) or solid
                    caveData[x, y, z, 0] = combinedNoise > caveThreshold;
                }
            }
        }
        
        // Convert cave data to mesh (simplified example)
        CreateCaveMesh(caveData, caveWidth, caveHeight, caveDepth);
    }
    
    void CreateCaveMesh(bool[,,,] caveData, int width, int height, int depth)
    {
        GameObject caveObject = new GameObject("Generated Cave");
        MeshFilter meshFilter = caveObject.AddComponent<MeshFilter>();
        MeshRenderer meshRenderer = caveObject.AddComponent<MeshRenderer>();
        
        if (terrainMaterial != null)
        {
            meshRenderer.material = terrainMaterial;
        }
        
        // Simplified mesh generation (marching cubes would be better)
        List<Vector3> vertices = new List<Vector3>();
        List<int> triangles = new List<int>();
        
        for (int x = 0; x < width - 1; x++)
        {
            for (int y = 0; y < height - 1; y++)
            {
                for (int z = 0; z < depth - 1; z++)
                {
                    if (caveData[x, y, z, 0] && !caveData[x + 1, y, z, 0])
                    {
                        // Create face on positive X side
                        AddQuad(vertices, triangles, 
                            new Vector3(x + 1, y, z),
                            new Vector3(x + 1, y + 1, z),
                            new Vector3(x + 1, y + 1, z + 1),
                            new Vector3(x + 1, y, z + 1));
                    }
                    // Add similar checks for other faces...
                }
            }
        }
        
        Mesh caveMesh = new Mesh();
        caveMesh.vertices = vertices.ToArray();
        caveMesh.triangles = triangles.ToArray();
        caveMesh.RecalculateNormals();
        
        meshFilter.mesh = caveMesh;
        caveObject.transform.position = new Vector3(-width * 0.5f, -10f, -depth * 0.5f);
    }
    
    void AddQuad(List<Vector3> vertices, List<int> triangles, Vector3 v1, Vector3 v2, Vector3 v3, Vector3 v4)
    {
        int startIndex = vertices.Count;
        
        vertices.Add(v1);
        vertices.Add(v2);
        vertices.Add(v3);
        vertices.Add(v4);
        
        // First triangle
        triangles.Add(startIndex);
        triangles.Add(startIndex + 1);
        triangles.Add(startIndex + 2);
        
        // Second triangle
        triangles.Add(startIndex);
        triangles.Add(startIndex + 2);
        triangles.Add(startIndex + 3);
    }
    
    #endregion
    
    #region Debug Visualization
    
    /// <summary>
    /// Visualize noise patterns and procedural generation in Scene view
    /// Essential for debugging and understanding noise behavior
    /// </summary>
    void OnDrawGizmosSelected()
    {
        if (noiseLayers == null || noiseLayers.Length == 0) return;
        
        // Draw noise visualization grid
        Gizmos.color = Color.yellow;
        int gridSize = 20;
        float cellSize = 2f;
        
        for (int x = 0; x < gridSize; x++)
        {
            for (int z = 0; z < gridSize; z++)
            {
                Vector3 worldPos = transform.position + new Vector3(
                    (x - gridSize * 0.5f) * cellSize,
                    0,
                    (z - gridSize * 0.5f) * cellSize
                );
                
                float noiseValue = NoiseProceduralUtility.CombineNoise(
                    worldPos.x * terrainScale + animationTime * 0.1f,
                    worldPos.z * terrainScale + animationTime * 0.1f,
                    noiseLayers
                );
                
                Vector3 heightOffset = Vector3.up * noiseValue * 10f;
                Gizmos.color = Color.Lerp(Color.blue, Color.red, noiseValue);
                Gizmos.DrawSphere(worldPos + heightOffset, 0.2f);
                
                // Draw connection to ground
                Gizmos.color = Color.gray;
                Gizmos.DrawLine(worldPos, worldPos + heightOffset);
            }
        }
    }
    
    #endregion
}
```

## 🎯 Noise Functions and Procedural Mathematics

### Noise Function Characteristics
```markdown
## Essential Noise Functions for Procedural Generation

### Perlin Noise
**Characteristics**: Smooth, continuous gradients with controllable frequency
**Best For**: Terrain heightmaps, cloud patterns, natural textures
**Parameters**: Frequency, amplitude, octaves, persistence
**Performance**: Fast, widely supported

### Simplex Noise
**Characteristics**: Better visual quality than Perlin, isotropic
**Best For**: High-quality terrain, 3D textures, reduced artifacts
**Parameters**: Similar to Perlin but with improved gradient distribution
**Performance**: Slightly slower than Perlin but better quality

### Voronoi/Worley Noise
**Characteristics**: Cellular patterns with sharp boundaries
**Best For**: Stone textures, cell structures, cracked surfaces
**Parameters**: Distance function, feature points, scale
**Performance**: More expensive but unique patterns

### Ridged Noise
**Characteristics**: Sharp peaks and valleys, mountain-like features
**Best For**: Mountain ranges, rocky terrain, sharp geological features
**Parameters**: Ridge sharpness, octaves, persistence
**Performance**: Similar to Perlin with post-processing

### Domain Warping
**Characteristics**: Flowing, organic distortions of base noise
**Best For**: Realistic terrain, flowing patterns, organic textures
**Parameters**: Warp strength, warp scale, multiple layers
**Performance**: Expensive but highly realistic results
```

### Practical Implementation Patterns
```csharp
/// <summary>
/// Advanced procedural generation techniques for specific use cases
/// Demonstrates specialized applications of noise functions
/// </summary>
public static class ProceduralPatterns
{
    /// <summary>
    /// Generate realistic coastlines using multiple noise layers
    /// Creates natural-looking shorelines with bays and peninsulas
    /// </summary>
    public static bool[,] GenerateCoastline(int width, int height, float landPercentage = 0.4f)
    {
        bool[,] landMap = new bool[width, height];
        
        for (int x = 0; x < width; x++)
        {
            for (int y = 0; y < height; y++)
            {
                float fx = (float)x / width;
                float fy = (float)y / height;
                
                // Base continent shape
                float distanceFromCenter = Vector2.Distance(new Vector2(fx, fy), new Vector2(0.5f, 0.5f));
                float continentMask = 1f - Mathf.Clamp01(distanceFromCenter * 2f);
                
                // Add coastal variation
                float coastalNoise = NoiseProceduralUtility.FractalPerlinNoise(fx * 8f, fy * 8f, 4, 0.5f, 1f);
                float detailNoise = NoiseProceduralUtility.TurbulenceNoise(fx * 16f, fy * 16f, 3, 0.6f, 1f);
                
                // Combine for natural coastline
                float landValue = continentMask * 0.7f + coastalNoise * 0.2f + detailNoise * 0.1f;
                landMap[x, y] = landValue > (1f - landPercentage);
            }
        }
        
        return landMap;
    }
    
    /// <summary>
    /// Generate biome distribution using temperature and moisture maps
    /// Creates realistic biome placement based on climate simulation
    /// </summary>
    public static BiomeType[,] GenerateBiomes(int width, int height, float[,] heightMap)
    {
        BiomeType[,] biomeMap = new BiomeType[width, height];
        
        // Generate temperature and moisture maps
        float[,] temperatureMap = new float[width, height];
        float[,] moistureMap = new float[width, height];
        
        for (int x = 0; x < width; x++)
        {
            for (int y = 0; y < height; y++)
            {
                float fx = (float)x / width;
                float fy = (float)y / height;
                
                // Temperature decreases with latitude and altitude
                float latitudeEffect = 1f - Mathf.Abs(fy - 0.5f) * 2f; // Warmer at equator
                float altitudeEffect = 1f - heightMap[x, y]; // Cooler at higher altitude
                float temperatureNoise = NoiseProceduralUtility.FractalPerlinNoise(fx * 4f, fy * 4f, 3, 0.5f, 1f);
                
                temperatureMap[x, y] = (latitudeEffect * 0.5f + altitudeEffect * 0.3f + temperatureNoise * 0.2f);
                
                // Moisture based on distance from water and wind patterns
                float moistureNoise = NoiseProceduralUtility.FractalPerlinNoise(fx * 6f, fy * 6f, 4, 0.6f, 1f);
                float windPattern = NoiseProceduralUtility.SinDegrees(fy * 360f * 3f) * 0.1f; // Trade winds
                
                moistureMap[x, y] = moistureNoise * 0.8f + windPattern * 0.2f;
                
                // Determine biome based on temperature and moisture
                biomeMap[x, y] = ClassifyBiome(temperatureMap[x, y], moistureMap[x, y], heightMap[x, y]);
            }
        }
        
        return biomeMap;
    }
    
    private static BiomeType ClassifyBiome(float temperature, float moisture, float altitude)
    {
        // Water biomes
        if (altitude < 0.3f) return BiomeType.Ocean;
        
        // High altitude biomes
        if (altitude > 0.8f)
        {
            return temperature > 0.4f ? BiomeType.Alpine : BiomeType.Snow;
        }
        
        // Temperature-moisture based classification
        if (temperature > 0.7f)
        {
            if (moisture > 0.6f) return BiomeType.Jungle;
            if (moisture > 0.3f) return BiomeType.Savanna;
            return BiomeType.Desert;
        }
        else if (temperature > 0.4f)
        {
            if (moisture > 0.6f) return BiomeType.Forest;
            if (moisture > 0.3f) return BiomeType.Grassland;
            return BiomeType.Steppe;
        }
        else
        {
            if (moisture > 0.5f) return BiomeType.Taiga;
            return BiomeType.Tundra;
        }
    }
    
    public enum BiomeType
    {
        Ocean, Desert, Grassland, Forest, Jungle, Savanna, 
        Steppe, Taiga, Tundra, Alpine, Snow
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Procedural Content Enhancement
- **Intelligent Generation**: AI-powered procedural generation that learns from player preferences and behavior
- **Content Curation**: Machine learning systems that evaluate and select the best procedurally generated content
- **Adaptive Parameters**: AI optimization of noise parameters for specific artistic styles and gameplay requirements

### Advanced Pattern Recognition
- **Style Transfer**: AI systems that apply artistic styles to procedurally generated content
- **Quality Assessment**: Machine learning evaluation of procedural content quality and realism
- **Pattern Synthesis**: AI-assisted creation of new noise functions and procedural algorithms

### Real-time Optimization
- **Performance Prediction**: AI analysis of procedural generation costs and optimization recommendations
- **LOD Generation**: Machine learning-based level-of-detail systems for procedural content
- **Streaming Optimization**: AI-powered procedural content streaming and caching strategies

## 💡 Key Highlights

- **Master the NOISE Framework** for systematic approach to procedural content generation
- **Understand Noise Function Characteristics** and choose appropriate algorithms for specific visual effects
- **Implement Multi-layer Noise Systems** for complex, realistic patterns and textures
- **Apply Domain Warping Techniques** for organic, flowing distortions and natural-looking results
- **Create Realistic Terrain Features** using erosion simulation and geological modeling
- **Generate Complex Biome Systems** using climate simulation and environmental factors
- **Optimize Performance** through efficient noise algorithms and caching strategies
- **Focus on Practical Applications** solving real procedural generation challenges in game development