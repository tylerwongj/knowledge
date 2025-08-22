# @m-Spline-Curve-Mathematics-Unity

## 🎯 Learning Objectives

- Master Bézier curves and spline mathematics for Unity development
- Implement smooth camera movements and object trajectories
- Create procedural paths and animations using mathematical curve functions
- Optimize spline calculations for real-time performance in games

## 🔧 Core Spline Mathematics

### Bézier Curve Fundamentals

```csharp
public static class BezierUtils
{
    // Linear interpolation (2 points)
    public static Vector3 LinearBezier(Vector3 p0, Vector3 p1, float t)
    {
        return Vector3.Lerp(p0, p1, t);
    }
    
    // Quadratic Bézier (3 points)
    public static Vector3 QuadraticBezier(Vector3 p0, Vector3 p1, Vector3 p2, float t)
    {
        float oneMinusT = 1f - t;
        return oneMinusT * oneMinusT * p0 + 
               2f * oneMinusT * t * p1 + 
               t * t * p2;
    }
    
    // Cubic Bézier (4 points)
    public static Vector3 CubicBezier(Vector3 p0, Vector3 p1, Vector3 p2, Vector3 p3, float t)
    {
        float oneMinusT = 1f - t;
        float oneMinusTSquared = oneMinusT * oneMinusT;
        float tSquared = t * t;
        
        return oneMinusTSquared * oneMinusT * p0 +
               3f * oneMinusTSquared * t * p1 +
               3f * oneMinusT * tSquared * p2 +
               tSquared * t * p3;
    }
}
```

### Catmull-Rom Splines

```csharp
public static class CatmullRomSpline
{
    public static Vector3 GetPoint(Vector3 p0, Vector3 p1, Vector3 p2, Vector3 p3, float t)
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
    
    public static Vector3 GetTangent(Vector3 p0, Vector3 p1, Vector3 p2, Vector3 p3, float t)
    {
        float t2 = t * t;
        
        return 0.5f * (
            (-p0 + p2) +
            2f * (2f * p0 - 5f * p1 + 4f * p2 - p3) * t +
            3f * (-p0 + 3f * p1 - 3f * p2 + p3) * t2
        );
    }
}
```

## 🎮 Unity Implementation Examples

### Smooth Camera Movement System

```csharp
public class SplineCameraController : MonoBehaviour
{
    [SerializeField] private Transform[] waypoints;
    [SerializeField] private float moveSpeed = 2f;
    [SerializeField] private AnimationCurve easingCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);
    
    private float currentTime = 0f;
    private bool isMoving = false;

    public void StartCameraMovement()
    {
        isMoving = true;
        currentTime = 0f;
    }

    void Update()
    {
        if (!isMoving || waypoints.Length < 4) return;

        currentTime += Time.deltaTime * moveSpeed;
        float normalizedTime = currentTime / (waypoints.Length - 3);
        
        if (normalizedTime >= 1f)
        {
            isMoving = false;
            return;
        }

        int currentSegment = Mathf.FloorToInt(normalizedTime * (waypoints.Length - 3));
        float segmentT = (normalizedTime * (waypoints.Length - 3)) - currentSegment;
        
        // Apply easing curve
        segmentT = easingCurve.Evaluate(segmentT);
        
        Vector3 position = CatmullRomSpline.GetPoint(
            waypoints[currentSegment].position,
            waypoints[currentSegment + 1].position,
            waypoints[currentSegment + 2].position,
            waypoints[currentSegment + 3].position,
            segmentT
        );
        
        transform.position = position;
        
        // Orient camera along path
        Vector3 tangent = CatmullRomSpline.GetTangent(
            waypoints[currentSegment].position,
            waypoints[currentSegment + 1].position,
            waypoints[currentSegment + 2].position,
            waypoints[currentSegment + 3].position,
            segmentT
        );
        
        if (tangent != Vector3.zero)
            transform.rotation = Quaternion.LookRotation(tangent.normalized);
    }
}
```

### Procedural Track Generator

```csharp
public class ProceduralTrackGenerator : MonoBehaviour
{
    [SerializeField] private int trackSegments = 50;
    [SerializeField] private float trackWidth = 4f;
    [SerializeField] private Material trackMaterial;
    
    private Vector3[] controlPoints;
    private Mesh trackMesh;

    public void GenerateTrack(Vector3[] points)
    {
        controlPoints = points;
        CreateTrackMesh();
    }

    private void CreateTrackMesh()
    {
        if (controlPoints.Length < 4) return;

        List<Vector3> vertices = new List<Vector3>();
        List<int> triangles = new List<int>();
        List<Vector2> uvs = new List<Vector2>();

        for (int i = 0; i < trackSegments; i++)
        {
            float t = (float)i / (trackSegments - 1);
            int segmentIndex = Mathf.FloorToInt(t * (controlPoints.Length - 3));
            float segmentT = (t * (controlPoints.Length - 3)) - segmentIndex;

            Vector3 centerPoint = CatmullRomSpline.GetPoint(
                controlPoints[segmentIndex],
                controlPoints[segmentIndex + 1],
                controlPoints[segmentIndex + 2],
                controlPoints[segmentIndex + 3],
                segmentT
            );

            Vector3 tangent = CatmullRomSpline.GetTangent(
                controlPoints[segmentIndex],
                controlPoints[segmentIndex + 1],
                controlPoints[segmentIndex + 2],
                controlPoints[segmentIndex + 3],
                segmentT
            ).normalized;

            Vector3 right = Vector3.Cross(tangent, Vector3.up).normalized;

            // Create track vertices
            vertices.Add(centerPoint - right * trackWidth * 0.5f);
            vertices.Add(centerPoint + right * trackWidth * 0.5f);

            // Create UVs
            uvs.Add(new Vector2(0f, t));
            uvs.Add(new Vector2(1f, t));

            // Create triangles (skip first segment)
            if (i > 0)
            {
                int baseIndex = (i - 1) * 2;
                
                // First triangle
                triangles.Add(baseIndex);
                triangles.Add(baseIndex + 2);
                triangles.Add(baseIndex + 1);
                
                // Second triangle
                triangles.Add(baseIndex + 1);
                triangles.Add(baseIndex + 2);
                triangles.Add(baseIndex + 3);
            }
        }

        // Create and assign mesh
        trackMesh = new Mesh();
        trackMesh.vertices = vertices.ToArray();
        trackMesh.triangles = triangles.ToArray();
        trackMesh.uv = uvs.ToArray();
        trackMesh.RecalculateNormals();

        GetComponent<MeshFilter>().mesh = trackMesh;
        GetComponent<MeshRenderer>().material = trackMaterial;
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Automated Spline Optimization Prompts

```
Generate optimized Unity C# code for:
1. Adaptive spline resolution based on curvature
2. Memory-efficient spline caching system
3. Multi-threaded spline calculations for large datasets
4. GPU-accelerated spline evaluation using compute shaders

Context: Unity game development requiring smooth 60fps performance
Requirements: Maintainable code with clear documentation
```

### Procedural Content Generation

```
Create Unity spline-based systems for:
1. Procedural road networks using Voronoi diagrams
2. River generation with terrain-aware spline placement
3. Dynamic rope/cable physics using spline mathematics
4. Organic growth patterns for vegetation systems

Focus: Performance optimization and visual quality balance
```

## 💡 Key Performance Optimizations

### Spline Caching System

```csharp
public class SplineCache
{
    private readonly Dictionary<int, Vector3[]> cachedPoints = new Dictionary<int, Vector3[]>();
    private readonly Dictionary<int, Vector3[]> cachedTangents = new Dictionary<int, Vector3[]>();
    
    public Vector3[] GetCachedPoints(int splineID, int resolution)
    {
        int key = splineID * 1000 + resolution;
        return cachedPoints.TryGetValue(key, out Vector3[] points) ? points : null;
    }
    
    public void CacheSpline(int splineID, int resolution, Vector3[] points, Vector3[] tangents)
    {
        int key = splineID * 1000 + resolution;
        cachedPoints[key] = points;
        cachedTangents[key] = tangents;
    }
    
    public void ClearCache()
    {
        cachedPoints.Clear();
        cachedTangents.Clear();
    }
}
```

### Adaptive Resolution System

```csharp
public static class AdaptiveSplineResolution
{
    public static int CalculateOptimalResolution(Vector3[] controlPoints, float maxError = 0.1f)
    {
        int minResolution = 10;
        int maxResolution = 100;
        
        for (int resolution = minResolution; resolution <= maxResolution; resolution += 10)
        {
            if (CalculateSplineError(controlPoints, resolution) <= maxError)
                return resolution;
        }
        
        return maxResolution;
    }
    
    private static float CalculateSplineError(Vector3[] controlPoints, int resolution)
    {
        float maxError = 0f;
        
        for (int i = 0; i < resolution - 1; i++)
        {
            float t1 = (float)i / (resolution - 1);
            float t2 = (float)(i + 1) / (resolution - 1);
            float tMid = (t1 + t2) * 0.5f;
            
            Vector3 linearMid = Vector3.Lerp(
                EvaluateSpline(controlPoints, t1),
                EvaluateSpline(controlPoints, t2),
                0.5f
            );
            
            Vector3 actualMid = EvaluateSpline(controlPoints, tMid);
            float error = Vector3.Distance(linearMid, actualMid);
            
            maxError = Mathf.Max(maxError, error);
        }
        
        return maxError;
    }
    
    private static Vector3 EvaluateSpline(Vector3[] points, float t)
    {
        // Implementation depends on spline type
        return Vector3.zero; // Placeholder
    }
}
```

## 🔥 Advanced Spline Applications

### Dynamic Rope Physics

```csharp
public class SplineRope : MonoBehaviour
{
    [SerializeField] private int segments = 20;
    [SerializeField] private float segmentLength = 1f;
    [SerializeField] private float gravity = -9.81f;
    [SerializeField] private float damping = 0.99f;
    
    private Vector3[] positions;
    private Vector3[] oldPositions;
    private bool[] isFixed;
    private LineRenderer lineRenderer;

    void Start()
    {
        InitializeRope();
        lineRenderer = GetComponent<LineRenderer>();
        lineRenderer.positionCount = segments + 1;
    }

    void FixedUpdate()
    {
        SimulateRope();
        RenderRope();
    }

    private void SimulateRope()
    {
        // Verlet integration
        for (int i = 0; i < positions.Length; i++)
        {
            if (isFixed[i]) continue;

            Vector3 velocity = (positions[i] - oldPositions[i]) * damping;
            oldPositions[i] = positions[i];
            positions[i] += velocity + Vector3.up * gravity * Time.fixedDeltaTime * Time.fixedDeltaTime;
        }

        // Constraint satisfaction
        for (int iteration = 0; iteration < 3; iteration++)
        {
            for (int i = 0; i < positions.Length - 1; i++)
            {
                Vector3 direction = positions[i + 1] - positions[i];
                float distance = direction.magnitude;
                Vector3 correction = direction.normalized * (distance - segmentLength) * 0.5f;

                if (!isFixed[i]) positions[i] += correction;
                if (!isFixed[i + 1]) positions[i + 1] -= correction;
            }
        }
    }

    private void RenderRope()
    {
        // Create smooth spline through rope segments
        Vector3[] smoothPoints = new Vector3[segments * 3];
        
        for (int i = 0; i < segments - 1; i++)
        {
            int baseIndex = i * 3;
            Vector3 p0 = i > 0 ? positions[i - 1] : positions[i];
            Vector3 p1 = positions[i];
            Vector3 p2 = positions[i + 1];
            Vector3 p3 = i < segments - 2 ? positions[i + 2] : positions[i + 1];

            for (int j = 0; j < 3; j++)
            {
                float t = j / 3f;
                smoothPoints[baseIndex + j] = CatmullRomSpline.GetPoint(p0, p1, p2, p3, t);
            }
        }

        lineRenderer.positionCount = smoothPoints.Length;
        lineRenderer.SetPositions(smoothPoints);
    }

    private void InitializeRope()
    {
        positions = new Vector3[segments + 1];
        oldPositions = new Vector3[segments + 1];
        isFixed = new bool[segments + 1];

        for (int i = 0; i <= segments; i++)
        {
            positions[i] = transform.position + Vector3.down * i * segmentLength;
            oldPositions[i] = positions[i];
            isFixed[i] = i == 0; // Fix first segment
        }
    }
}
```

### Organic Growth System

```csharp
public class OrganicGrowthSpline : MonoBehaviour
{
    [SerializeField] private float growthSpeed = 1f;
    [SerializeField] private float branchProbability = 0.1f;
    [SerializeField] private GameObject leafPrefab;
    
    private List<SplineSegment> activeSegments = new List<SplineSegment>();
    private List<Vector3> growthDirections = new List<Vector3>();

    [System.Serializable]
    public class SplineSegment
    {
        public Vector3[] controlPoints = new Vector3[4];
        public float growthProgress = 0f;
        public bool isActive = true;
        public LineRenderer renderer;
    }

    void Start()
    {
        CreateInitialSegment();
    }

    void Update()
    {
        UpdateGrowth();
        CheckForBranching();
    }

    private void UpdateGrowth()
    {
        for (int i = 0; i < activeSegments.Count; i++)
        {
            var segment = activeSegments[i];
            if (!segment.isActive) continue;

            segment.growthProgress += growthSpeed * Time.deltaTime;
            
            if (segment.growthProgress >= 1f)
            {
                segment.growthProgress = 1f;
                segment.isActive = false;
                CreateNextSegment(segment);
            }

            RenderSegment(segment);
        }
    }

    private void RenderSegment(SplineSegment segment)
    {
        int resolution = 20;
        Vector3[] points = new Vector3[resolution];
        
        for (int i = 0; i < resolution; i++)
        {
            float t = (float)i / (resolution - 1) * segment.growthProgress;
            points[i] = BezierUtils.CubicBezier(
                segment.controlPoints[0],
                segment.controlPoints[1],
                segment.controlPoints[2],
                segment.controlPoints[3],
                t
            );
        }

        segment.renderer.positionCount = Mathf.FloorToInt(resolution * segment.growthProgress);
        segment.renderer.SetPositions(points);
    }

    private void CreateNextSegment(SplineSegment parentSegment)
    {
        Vector3 startPoint = parentSegment.controlPoints[3];
        Vector3 direction = (parentSegment.controlPoints[3] - parentSegment.controlPoints[2]).normalized;
        
        // Add some organic variation
        direction += new Vector3(
            Random.Range(-0.3f, 0.3f),
            Random.Range(-0.1f, 0.3f),
            Random.Range(-0.3f, 0.3f)
        );
        direction.Normalize();

        SplineSegment newSegment = new SplineSegment();
        newSegment.controlPoints[0] = startPoint;
        newSegment.controlPoints[1] = startPoint + direction * 0.5f;
        newSegment.controlPoints[2] = startPoint + direction * 1.5f;
        newSegment.controlPoints[3] = startPoint + direction * 2f;
        newSegment.renderer = CreateLineRenderer();

        activeSegments.Add(newSegment);
    }

    private void CheckForBranching()
    {
        for (int i = 0; i < activeSegments.Count; i++)
        {
            var segment = activeSegments[i];
            if (segment.growthProgress > 0.5f && Random.value < branchProbability * Time.deltaTime)
            {
                CreateBranch(segment);
            }
        }
    }

    private void CreateBranch(SplineSegment parentSegment)
    {
        Vector3 branchPoint = BezierUtils.CubicBezier(
            parentSegment.controlPoints[0],
            parentSegment.controlPoints[1],
            parentSegment.controlPoints[2],
            parentSegment.controlPoints[3],
            0.7f
        );

        Vector3 branchDirection = Vector3.Cross(
            (parentSegment.controlPoints[3] - parentSegment.controlPoints[0]).normalized,
            Vector3.up
        ).normalized;

        SplineSegment branch = new SplineSegment();
        branch.controlPoints[0] = branchPoint;
        branch.controlPoints[1] = branchPoint + branchDirection * 0.3f;
        branch.controlPoints[2] = branchPoint + branchDirection * 0.8f;
        branch.controlPoints[3] = branchPoint + branchDirection * 1.2f;
        branch.renderer = CreateLineRenderer();

        activeSegments.Add(branch);
    }

    private LineRenderer CreateLineRenderer()
    {
        GameObject obj = new GameObject("SplineSegment");
        obj.transform.SetParent(transform);
        LineRenderer lr = obj.AddComponent<LineRenderer>();
        lr.material = GetComponent<LineRenderer>().material;
        lr.startWidth = 0.1f;
        lr.endWidth = 0.05f;
        return lr;
    }

    private void CreateInitialSegment()
    {
        SplineSegment initial = new SplineSegment();
        initial.controlPoints[0] = transform.position;
        initial.controlPoints[1] = transform.position + Vector3.up * 0.5f;
        initial.controlPoints[2] = transform.position + Vector3.up * 1.5f;
        initial.controlPoints[3] = transform.position + Vector3.up * 2f;
        initial.renderer = CreateLineRenderer();
        
        activeSegments.Add(initial);
    }
}
```

## 📈 Advanced Mathematical Applications

### Curvature Analysis for Path Planning

```csharp
public static class SplineCurvatureAnalysis
{
    public static float CalculateCurvature(Vector3 p0, Vector3 p1, Vector3 p2, Vector3 p3, float t)
    {
        Vector3 firstDerivative = GetFirstDerivative(p0, p1, p2, p3, t);
        Vector3 secondDerivative = GetSecondDerivative(p0, p1, p2, p3, t);
        
        Vector3 cross = Vector3.Cross(firstDerivative, secondDerivative);
        float numerator = cross.magnitude;
        float denominator = Mathf.Pow(firstDerivative.magnitude, 3f);
        
        return denominator > 0f ? numerator / denominator : 0f;
    }
    
    private static Vector3 GetFirstDerivative(Vector3 p0, Vector3 p1, Vector3 p2, Vector3 p3, float t)
    {
        float oneMinusT = 1f - t;
        return 3f * oneMinusT * oneMinusT * (p1 - p0) +
               6f * oneMinusT * t * (p2 - p1) +
               3f * t * t * (p3 - p2);
    }
    
    private static Vector3 GetSecondDerivative(Vector3 p0, Vector3 p1, Vector3 p2, Vector3 p3, float t)
    {
        float oneMinusT = 1f - t;
        return 6f * oneMinusT * (p2 - 2f * p1 + p0) +
               6f * t * (p3 - 2f * p2 + p1);
    }
    
    public static float[] AnalyzePathDifficulty(Vector3[] controlPoints, int resolution = 50)
    {
        float[] curvatures = new float[resolution];
        
        for (int i = 0; i < resolution; i++)
        {
            float t = (float)i / (resolution - 1);
            int segmentIndex = Mathf.FloorToInt(t * (controlPoints.Length - 3));
            float segmentT = (t * (controlPoints.Length - 3)) - segmentIndex;
            
            curvatures[i] = CalculateCurvature(
                controlPoints[segmentIndex],
                controlPoints[segmentIndex + 1],
                controlPoints[segmentIndex + 2],
                controlPoints[segmentIndex + 3],
                segmentT
            );
        }
        
        return curvatures;
    }
}
```

This comprehensive guide provides the mathematical foundation and practical implementation techniques for using splines in Unity game development, with focus on performance optimization and real-world applications.
