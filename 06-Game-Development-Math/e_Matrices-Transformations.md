# Matrices & Transformations

## Overview
Master matrix mathematics for 3D transformations, coordinate systems, and advanced rendering techniques in Unity game development.

## Key Concepts

### Matrix Fundamentals

**Matrix Representation:**
- **Identity Matrix:** No transformation applied (scaling = 1, rotation = 0, translation = 0)
- **Translation Matrix:** Moves objects in 3D space
- **Rotation Matrix:** Rotates objects around axes
- **Scale Matrix:** Changes object size uniformly or non-uniformly
- **Transformation Matrix:** Combines multiple transformations in single operation

**Unity Matrix Operations:**
```csharp
public class MatrixTransformations : MonoBehaviour
{
    [Header("Matrix Demonstration")]
    [SerializeField] private Transform targetObject;
    [SerializeField] private Vector3 customTranslation = Vector3.zero;
    [SerializeField] private Vector3 customRotation = Vector3.zero;
    [SerializeField] private Vector3 customScale = Vector3.one;
    
    [Header("Matrix Visualization")]
    [SerializeField] private bool showMatrixDebug = true;
    [SerializeField] private bool animateTransformations = false;
    
    void Start()
    {
        DemonstrateBasicMatrices();
        AnalyzeTransformMatrix();
    }
    
    void DemonstrateBasicMatrices()
    {
        // Identity Matrix
        Matrix4x4 identity = Matrix4x4.identity;
        Debug.Log($"Identity Matrix:\n{MatrixToString(identity)}");
        
        // Translation Matrix
        Matrix4x4 translation = Matrix4x4.Translate(customTranslation);
        Debug.Log($"Translation Matrix:\n{MatrixToString(translation)}");
        
        // Rotation Matrix
        Quaternion rotation = Quaternion.Euler(customRotation);
        Matrix4x4 rotationMatrix = Matrix4x4.Rotate(rotation);
        Debug.Log($"Rotation Matrix:\n{MatrixToString(rotationMatrix)}");
        
        // Scale Matrix
        Matrix4x4 scale = Matrix4x4.Scale(customScale);
        Debug.Log($"Scale Matrix:\n{MatrixToString(scale)}");
        
        // Combined Transformation Matrix (TRS)
        Matrix4x4 trs = Matrix4x4.TRS(customTranslation, rotation, customScale);
        Debug.Log($"Combined TRS Matrix:\n{MatrixToString(trs)}");
    }
    
    void AnalyzeTransformMatrix()
    {
        if (targetObject == null) return;
        
        // Get world-to-local and local-to-world matrices
        Matrix4x4 localToWorld = targetObject.localToWorldMatrix;
        Matrix4x4 worldToLocal = targetObject.worldToLocalMatrix;
        
        Debug.Log($"Local to World Matrix:\n{MatrixToString(localToWorld)}");
        Debug.Log($"World to Local Matrix:\n{MatrixToString(worldToLocal)}");
        
        // Extract transformation components from matrix
        Vector3 position = ExtractPosition(localToWorld);
        Quaternion rotation = ExtractRotation(localToWorld);
        Vector3 scale = ExtractScale(localToWorld);
        
        Debug.Log($"Extracted Position: {position}");
        Debug.Log($"Extracted Rotation: {rotation.eulerAngles}");
        Debug.Log($"Extracted Scale: {scale}");
    }
    
    string MatrixToString(Matrix4x4 matrix)
    {
        return $"[{matrix.m00:F2}, {matrix.m01:F2}, {matrix.m02:F2}, {matrix.m03:F2}]\n" +
               $"[{matrix.m10:F2}, {matrix.m11:F2}, {matrix.m12:F2}, {matrix.m13:F2}]\n" +
               $"[{matrix.m20:F2}, {matrix.m21:F2}, {matrix.m22:F2}, {matrix.m23:F2}]\n" +
               $"[{matrix.m30:F2}, {matrix.m31:F2}, {matrix.m32:F2}, {matrix.m33:F2}]";
    }
    
    Vector3 ExtractPosition(Matrix4x4 matrix)
    {
        return new Vector3(matrix.m03, matrix.m13, matrix.m23);
    }
    
    Quaternion ExtractRotation(Matrix4x4 matrix)
    {
        Vector3 forward = new Vector3(matrix.m02, matrix.m12, matrix.m22);
        Vector3 upwards = new Vector3(matrix.m01, matrix.m11, matrix.m21);
        return Quaternion.LookRotation(forward, upwards);
    }
    
    Vector3 ExtractScale(Matrix4x4 matrix)
    {
        Vector3 scale;
        scale.x = new Vector4(matrix.m00, matrix.m10, matrix.m20, matrix.m30).magnitude;
        scale.y = new Vector4(matrix.m01, matrix.m11, matrix.m21, matrix.m31).magnitude;
        scale.z = new Vector4(matrix.m02, matrix.m12, matrix.m22, matrix.m32).magnitude;
        return scale;
    }
    
    void Update()
    {
        if (animateTransformations)
        {
            AnimateMatrixTransformations();
        }
        
        if (showMatrixDebug)
        {
            DebugDrawMatrixAxes();
        }
    }
    
    void AnimateMatrixTransformations()
    {
        float time = Time.time;
        
        // Animated translation
        Vector3 animatedTranslation = new Vector3(
            Mathf.Sin(time) * 2f,
            Mathf.Cos(time * 0.5f) * 1f,
            Mathf.Sin(time * 0.3f) * 1.5f
        );
        
        // Animated rotation
        Vector3 animatedRotation = new Vector3(
            time * 30f,
            time * 45f,
            time * 60f
        );
        
        // Animated scale
        Vector3 animatedScale = Vector3.one * (1f + Mathf.Sin(time * 2f) * 0.3f);
        
        // Apply combined transformation
        Matrix4x4 animatedMatrix = Matrix4x4.TRS(
            animatedTranslation,
            Quaternion.Euler(animatedRotation),
            animatedScale
        );
        
        // Apply to transform
        ApplyMatrixToTransform(transform, animatedMatrix);
    }
    
    void ApplyMatrixToTransform(Transform target, Matrix4x4 matrix)
    {
        target.position = ExtractPosition(matrix);
        target.rotation = ExtractRotation(matrix);
        target.localScale = ExtractScale(matrix);
    }
    
    void DebugDrawMatrixAxes()
    {
        Matrix4x4 matrix = transform.localToWorldMatrix;
        
        Vector3 position = transform.position;
        Vector3 right = transform.right;
        Vector3 up = transform.up;
        Vector3 forward = transform.forward;
        
        // Draw coordinate axes
        Debug.DrawRay(position, right * 2f, Color.red);
        Debug.DrawRay(position, up * 2f, Color.green);
        Debug.DrawRay(position, forward * 2f, Color.blue);
    }
}
```

### Coordinate System Transformations

**Coordinate Space Conversions:**
```csharp
public class CoordinateSystemManager : MonoBehaviour
{
    [Header("Coordinate Conversion")]
    [SerializeField] private Transform referenceObject;
    [SerializeField] private Vector3 testPoint = Vector3.zero;
    [SerializeField] private bool showCoordinateSpaces = true;
    
    [Header("Camera Projections")]
    [SerializeField] private Camera targetCamera;
    [SerializeField] private Transform worldSpaceObject;
    
    void Update()
    {
        if (referenceObject != null)
        {
            DemonstrateCoordinateConversions();
        }
        
        if (targetCamera != null && worldSpaceObject != null)
        {
            DemonstrateCameraProjections();
        }
    }
    
    void DemonstrateCoordinateConversions()
    {
        // World to Local Space conversion
        Vector3 worldPoint = testPoint;
        Vector3 localPoint = referenceObject.InverseTransformPoint(worldPoint);
        
        // Local to World Space conversion
        Vector3 backToWorld = referenceObject.TransformPoint(localPoint);
        
        Debug.Log($"World Point: {worldPoint}");
        Debug.Log($"Local Point: {localPoint}");
        Debug.Log($"Back to World: {backToWorld}");
        
        // Direction transformations (no translation)
        Vector3 worldDirection = Vector3.forward;
        Vector3 localDirection = referenceObject.InverseTransformDirection(worldDirection);
        Vector3 backToWorldDirection = referenceObject.TransformDirection(localDirection);
        
        Debug.Log($"World Direction: {worldDirection}");
        Debug.Log($"Local Direction: {localDirection}");
        Debug.Log($"Back to World Direction: {backToWorldDirection}");
        
        // Manual matrix transformations
        Matrix4x4 worldToLocal = referenceObject.worldToLocalMatrix;
        Matrix4x4 localToWorld = referenceObject.localToWorldMatrix;
        
        Vector3 manualLocalPoint = worldToLocal.MultiplyPoint3x4(worldPoint);
        Vector3 manualWorldPoint = localToWorld.MultiplyPoint3x4(manualLocalPoint);
        
        Debug.Log($"Manual Local Point: {manualLocalPoint}");
        Debug.Log($"Manual World Point: {manualWorldPoint}");
        
        // Visualize coordinate spaces
        if (showCoordinateSpaces)
        {
            VisualizeCoordinateSpaces();
        }
    }
    
    void DemonstrateCameraProjections()
    {
        Vector3 worldPosition = worldSpaceObject.position;
        
        // World to Screen Space
        Vector3 screenPoint = targetCamera.WorldToScreenPoint(worldPosition);
        Debug.Log($"Screen Point: {screenPoint}");
        
        // World to Viewport Space (0-1 normalized)
        Vector3 viewportPoint = targetCamera.WorldToViewportPoint(worldPosition);
        Debug.Log($"Viewport Point: {viewportPoint}");
        
        // Screen to World Space (requires depth)
        Vector3 mousePosition = Input.mousePosition;
        mousePosition.z = Vector3.Distance(targetCamera.transform.position, worldPosition);
        Vector3 worldFromScreen = targetCamera.ScreenToWorldPoint(mousePosition);
        Debug.Log($"World from Screen: {worldFromScreen}");
        
        // Check if object is in front of camera
        bool isInFront = screenPoint.z > 0;
        bool isInViewport = viewportPoint.x >= 0 && viewportPoint.x <= 1 && 
                           viewportPoint.y >= 0 && viewportPoint.y <= 1;
        
        Debug.Log($"Object is in front: {isInFront}, In viewport: {isInViewport}");
        
        // Custom projection matrix calculations
        DemonstrateProjectionMatrix();
    }
    
    void DemonstrateProjectionMatrix()
    {
        Matrix4x4 projectionMatrix = targetCamera.projectionMatrix;
        Matrix4x4 worldToCameraMatrix = targetCamera.worldToCameraMatrix;
        
        // Combined view-projection matrix
        Matrix4x4 viewProjectionMatrix = projectionMatrix * worldToCameraMatrix;
        
        // Transform world point to clip space
        Vector4 worldPoint4 = new Vector4(worldSpaceObject.position.x, 
                                         worldSpaceObject.position.y, 
                                         worldSpaceObject.position.z, 1f);
        Vector4 clipSpacePoint = viewProjectionMatrix * worldPoint4;
        
        // Perspective divide to get NDC (Normalized Device Coordinates)
        Vector3 ndcPoint = new Vector3(clipSpacePoint.x / clipSpacePoint.w,
                                      clipSpacePoint.y / clipSpacePoint.w,
                                      clipSpacePoint.z / clipSpacePoint.w);
        
        Debug.Log($"Clip Space Point: {clipSpacePoint}");
        Debug.Log($"NDC Point: {ndcPoint}");
        
        // Convert NDC to screen coordinates
        Vector3 screenSize = new Vector3(Screen.width, Screen.height, 1f);
        Vector3 screenCoord = new Vector3(
            (ndcPoint.x + 1f) * 0.5f * screenSize.x,
            (ndcPoint.y + 1f) * 0.5f * screenSize.y,
            ndcPoint.z
        );
        
        Debug.Log($"Manual Screen Coordinate: {screenCoord}");
    }
    
    void VisualizeCoordinateSpaces()
    {
        // Draw world space axes at origin
        Debug.DrawRay(Vector3.zero, Vector3.right * 5f, Color.red);
        Debug.DrawRay(Vector3.zero, Vector3.up * 5f, Color.green);
        Debug.DrawRay(Vector3.zero, Vector3.forward * 5f, Color.blue);
        
        // Draw object's local space axes
        if (referenceObject != null)
        {
            Vector3 objPos = referenceObject.position;
            Debug.DrawRay(objPos, referenceObject.right * 3f, Color.cyan);
            Debug.DrawRay(objPos, referenceObject.up * 3f, Color.magenta);
            Debug.DrawRay(objPos, referenceObject.forward * 3f, Color.yellow);
        }
    }
    
    // Custom coordinate system transformation
    public Vector3 TransformBetweenObjects(Vector3 point, Transform fromSpace, Transform toSpace)
    {
        // Convert from source space to world space
        Vector3 worldPoint = fromSpace.TransformPoint(point);
        
        // Convert from world space to target space
        Vector3 targetSpacePoint = toSpace.InverseTransformPoint(worldPoint);
        
        return targetSpacePoint;
    }
    
    // Create custom transformation matrix
    public Matrix4x4 CreateCustomTransformation(Vector3 translation, Vector3 rotation, Vector3 scale)
    {
        Matrix4x4 translationMatrix = Matrix4x4.Translate(translation);
        Matrix4x4 rotationMatrix = Matrix4x4.Rotate(Quaternion.Euler(rotation));
        Matrix4x4 scaleMatrix = Matrix4x4.Scale(scale);
        
        // Order matters: Scale, then Rotate, then Translate
        return translationMatrix * rotationMatrix * scaleMatrix;
    }
}
```

### Advanced Matrix Operations

**Matrix Interpolation and Animation:**
```csharp
public class MatrixInterpolation : MonoBehaviour
{
    [Header("Matrix Interpolation")]
    [SerializeField] private Transform startTransform;
    [SerializeField] private Transform endTransform;
    [SerializeField] private float interpolationSpeed = 1f;
    [SerializeField] private AnimationCurve interpolationCurve = AnimationCurve.Linear(0, 0, 1, 1);
    
    [Header("Advanced Operations")]
    [SerializeField] private bool performMatrixDecomposition = true;
    [SerializeField] private bool showMatrixInverse = true;
    [SerializeField] private bool demonstrateOrthogonalization = true;
    
    private float interpolationTime = 0f;
    
    void Update()
    {
        if (startTransform != null && endTransform != null)
        {
            PerformMatrixInterpolation();
        }
        
        if (performMatrixDecomposition)
        {
            DemonstrateMatrixDecomposition();
        }
        
        if (showMatrixInverse)
        {
            DemonstrateMatrixInverse();
        }
        
        if (demonstrateOrthogonalization)
        {
            DemonstrateOrthogonalization();
        }
    }
    
    void PerformMatrixInterpolation()
    {
        interpolationTime += Time.deltaTime * interpolationSpeed;
        float t = interpolationCurve.Evaluate(interpolationTime % 1f);
        
        // Get transformation matrices
        Matrix4x4 startMatrix = startTransform.localToWorldMatrix;
        Matrix4x4 endMatrix = endTransform.localToWorldMatrix;
        
        // Decompose matrices
        Vector3 startPos = ExtractPosition(startMatrix);
        Quaternion startRot = ExtractRotation(startMatrix);
        Vector3 startScale = ExtractScale(startMatrix);
        
        Vector3 endPos = ExtractPosition(endMatrix);
        Quaternion endRot = ExtractRotation(endMatrix);
        Vector3 endScale = ExtractScale(endMatrix);
        
        // Interpolate components
        Vector3 lerpedPos = Vector3.Lerp(startPos, endPos, t);
        Quaternion lerpedRot = Quaternion.Lerp(startRot, endRot, t);
        Vector3 lerpedScale = Vector3.Lerp(startScale, endScale, t);
        
        // Reconstruct matrix
        Matrix4x4 interpolatedMatrix = Matrix4x4.TRS(lerpedPos, lerpedRot, lerpedScale);
        
        // Apply to transform
        transform.position = lerpedPos;
        transform.rotation = lerpedRot;
        transform.localScale = lerpedScale;
        
        // Alternative: Direct matrix interpolation (less stable for rotations)
        Matrix4x4 directLerp = LerpMatrix(startMatrix, endMatrix, t);
        Debug.Log($"Direct Matrix Lerp:\n{MatrixToString(directLerp)}");
    }
    
    Matrix4x4 LerpMatrix(Matrix4x4 a, Matrix4x4 b, float t)
    {
        Matrix4x4 result = new Matrix4x4();
        
        for (int i = 0; i < 16; i++)
        {
            result[i] = Mathf.Lerp(a[i], b[i], t);
        }
        
        return result;
    }
    
    void DemonstrateMatrixDecomposition()
    {
        Matrix4x4 transformMatrix = transform.localToWorldMatrix;
        
        // Decompose matrix into TRS components
        Vector3 position = ExtractPosition(transformMatrix);
        Quaternion rotation = ExtractRotation(transformMatrix);
        Vector3 scale = ExtractScale(transformMatrix);
        
        // Verify decomposition by reconstructing matrix
        Matrix4x4 reconstructed = Matrix4x4.TRS(position, rotation, scale);
        
        // Check if matrices are approximately equal
        bool isEqual = MatricesApproximatelyEqual(transformMatrix, reconstructed);
        
        Debug.Log($"Original Position: {transform.position}, Extracted: {position}");
        Debug.Log($"Original Rotation: {transform.rotation.eulerAngles}, Extracted: {rotation.eulerAngles}");
        Debug.Log($"Original Scale: {transform.localScale}, Extracted: {scale}");
        Debug.Log($"Matrix decomposition accurate: {isEqual}");
    }
    
    void DemonstrateMatrixInverse()
    {
        Matrix4x4 originalMatrix = transform.localToWorldMatrix;
        Matrix4x4 inverseMatrix = originalMatrix.inverse;
        
        // Multiply matrix by its inverse should give identity
        Matrix4x4 shouldBeIdentity = originalMatrix * inverseMatrix;
        
        Debug.Log($"Original Matrix:\n{MatrixToString(originalMatrix)}");
        Debug.Log($"Inverse Matrix:\n{MatrixToString(inverseMatrix)}");
        Debug.Log($"Product (should be identity):\n{MatrixToString(shouldBeIdentity)}");
        
        // Verify inverse properties
        Vector3 testPoint = new Vector3(1, 2, 3);
        Vector3 transformed = originalMatrix.MultiplyPoint3x4(testPoint);
        Vector3 backToOriginal = inverseMatrix.MultiplyPoint3x4(transformed);
        
        Debug.Log($"Test Point: {testPoint}");
        Debug.Log($"Transformed: {transformed}");
        Debug.Log($"Back to Original: {backToOriginal}");
        Debug.Log($"Inverse transformation accurate: {Vector3.Distance(testPoint, backToOriginal) < 0.001f}");
    }
    
    void DemonstrateOrthogonalization()
    {
        // Create a matrix with non-orthogonal axes (skewed)
        Matrix4x4 skewedMatrix = new Matrix4x4();
        skewedMatrix.SetColumn(0, new Vector4(1, 0.3f, 0, 0)); // Right vector (skewed)
        skewedMatrix.SetColumn(1, new Vector4(0.2f, 1, 0, 0)); // Up vector (skewed)
        skewedMatrix.SetColumn(2, new Vector4(0, 0, 1, 0));    // Forward vector
        skewedMatrix.SetColumn(3, new Vector4(0, 0, 0, 1));    // Position
        
        // Orthogonalize using Gram-Schmidt process
        Matrix4x4 orthogonalMatrix = OrthogonalizeMatrix(skewedMatrix);
        
        Debug.Log($"Skewed Matrix:\n{MatrixToString(skewedMatrix)}");
        Debug.Log($"Orthogonalized Matrix:\n{MatrixToString(orthogonalMatrix)}");
        
        // Verify orthogonality
        Vector3 right = orthogonalMatrix.GetColumn(0);
        Vector3 up = orthogonalMatrix.GetColumn(1);
        Vector3 forward = orthogonalMatrix.GetColumn(2);
        
        float dotRightUp = Vector3.Dot(right, up);
        float dotRightForward = Vector3.Dot(right, forward);
        float dotUpForward = Vector3.Dot(up, forward);
        
        Debug.Log($"Orthogonality check - Right·Up: {dotRightUp:F6}, Right·Forward: {dotRightForward:F6}, Up·Forward: {dotUpForward:F6}");
    }
    
    Matrix4x4 OrthogonalizeMatrix(Matrix4x4 matrix)
    {
        Vector3 v1 = matrix.GetColumn(0); // Right
        Vector3 v2 = matrix.GetColumn(1); // Up
        Vector3 v3 = matrix.GetColumn(2); // Forward
        
        // Gram-Schmidt orthogonalization
        Vector3 u1 = v1.normalized;
        Vector3 u2 = (v2 - Vector3.Dot(v2, u1) * u1).normalized;
        Vector3 u3 = (v3 - Vector3.Dot(v3, u1) * u1 - Vector3.Dot(v3, u2) * u2).normalized;
        
        Matrix4x4 result = matrix;
        result.SetColumn(0, new Vector4(u1.x, u1.y, u1.z, 0));
        result.SetColumn(1, new Vector4(u2.x, u2.y, u2.z, 0));
        result.SetColumn(2, new Vector4(u3.x, u3.y, u3.z, 0));
        
        return result;
    }
    
    bool MatricesApproximatelyEqual(Matrix4x4 a, Matrix4x4 b, float tolerance = 0.001f)
    {
        for (int i = 0; i < 16; i++)
        {
            if (Mathf.Abs(a[i] - b[i]) > tolerance)
                return false;
        }
        return true;
    }
    
    Vector3 ExtractPosition(Matrix4x4 matrix)
    {
        return new Vector3(matrix.m03, matrix.m13, matrix.m23);
    }
    
    Quaternion ExtractRotation(Matrix4x4 matrix)
    {
        Vector3 forward = new Vector3(matrix.m02, matrix.m12, matrix.m22);
        Vector3 upwards = new Vector3(matrix.m01, matrix.m11, matrix.m21);
        return Quaternion.LookRotation(forward, upwards);
    }
    
    Vector3 ExtractScale(Matrix4x4 matrix)
    {
        Vector3 scale;
        scale.x = new Vector4(matrix.m00, matrix.m10, matrix.m20, matrix.m30).magnitude;
        scale.y = new Vector4(matrix.m01, matrix.m11, matrix.m21, matrix.m31).magnitude;
        scale.z = new Vector4(matrix.m02, matrix.m12, matrix.m22, matrix.m32).magnitude;
        return scale;
    }
    
    string MatrixToString(Matrix4x4 matrix)
    {
        return $"[{matrix.m00:F3}, {matrix.m01:F3}, {matrix.m02:F3}, {matrix.m03:F3}]\n" +
               $"[{matrix.m10:F3}, {matrix.m11:F3}, {matrix.m12:F3}, {matrix.m13:F3}]\n" +
               $"[{matrix.m20:F3}, {matrix.m21:F3}, {matrix.m22:F3}, {matrix.m23:F3}]\n" +
               $"[{matrix.m30:F3}, {matrix.m31:F3}, {matrix.m32:F3}, {matrix.m33:F3}]";
    }
}
```

## Practical Applications

### Camera System with Matrix Control

**Advanced Camera Controller:**
```csharp
public class MatrixCameraController : MonoBehaviour
{
    [Header("Camera Settings")]
    [SerializeField] private Transform target;
    [SerializeField] private float distance = 10f;
    [SerializeField] private float heightOffset = 5f;
    [SerializeField] private float rotationSpeed = 2f;
    [SerializeField] private float smoothTime = 0.3f;
    
    [Header("Matrix Operations")]
    [SerializeField] private bool useMatrixCalculations = true;
    [SerializeField] private bool showDebugInfo = true;
    
    private Vector3 velocity = Vector3.zero;
    private Camera cam;
    
    void Start()
    {
        cam = GetComponent<Camera>();
    }
    
    void LateUpdate()
    {
        if (target == null) return;
        
        if (useMatrixCalculations)
        {
            UpdateCameraWithMatrices();
        }
        else
        {
            UpdateCameraTraditional();
        }
        
        if (showDebugInfo)
        {
            DebugCameraMatrices();
        }
    }
    
    void UpdateCameraWithMatrices()
    {
        // Calculate desired camera position using matrix operations
        Vector3 targetPosition = target.position;
        
        // Create rotation matrix for orbiting
        float mouseX = Input.GetAxis("Mouse X") * rotationSpeed;
        float mouseY = Input.GetAxis("Mouse Y") * rotationSpeed;
        
        // Build rotation matrices
        Matrix4x4 rotationY = CreateRotationMatrix(Vector3.up, mouseX * Time.deltaTime);
        Matrix4x4 rotationX = CreateRotationMatrix(Vector3.right, -mouseY * Time.deltaTime);
        
        // Combine rotations
        Matrix4x4 combinedRotation = rotationY * rotationX;
        
        // Apply rotation to current relative position
        Vector3 relativePosition = transform.position - targetPosition;
        Vector4 rotatedPosition = combinedRotation * new Vector4(relativePosition.x, relativePosition.y, relativePosition.z, 1f);
        
        // Calculate final camera position
        Vector3 desiredPosition = targetPosition + new Vector3(rotatedPosition.x, rotatedPosition.y, rotatedPosition.z);
        
        // Smooth movement
        transform.position = Vector3.SmoothDamp(transform.position, desiredPosition, ref velocity, smoothTime);
        
        // Look at target using matrix calculations
        Vector3 lookDirection = (targetPosition - transform.position).normalized;
        Matrix4x4 lookMatrix = CreateLookAtMatrix(transform.position, targetPosition, Vector3.up);
        
        // Apply look rotation
        transform.rotation = ExtractRotation(lookMatrix);
    }
    
    void UpdateCameraTraditional()
    {
        // Traditional approach for comparison
        Vector3 targetPosition = target.position + Vector3.up * heightOffset;
        Vector3 desiredPosition = targetPosition - transform.forward * distance;
        
        transform.position = Vector3.SmoothDamp(transform.position, desiredPosition, ref velocity, smoothTime);
        transform.LookAt(targetPosition);
    }
    
    Matrix4x4 CreateRotationMatrix(Vector3 axis, float angle)
    {
        Quaternion rotation = Quaternion.AngleAxis(angle * Mathf.Rad2Deg, axis);
        return Matrix4x4.Rotate(rotation);
    }
    
    Matrix4x4 CreateLookAtMatrix(Vector3 eye, Vector3 target, Vector3 up)
    {
        Vector3 forward = (target - eye).normalized;
        Vector3 right = Vector3.Cross(up, forward).normalized;
        Vector3 newUp = Vector3.Cross(forward, right);
        
        Matrix4x4 lookMatrix = new Matrix4x4();
        lookMatrix.SetRow(0, new Vector4(right.x, right.y, right.z, -Vector3.Dot(right, eye)));
        lookMatrix.SetRow(1, new Vector4(newUp.x, newUp.y, newUp.z, -Vector3.Dot(newUp, eye)));
        lookMatrix.SetRow(2, new Vector4(forward.x, forward.y, forward.z, -Vector3.Dot(forward, eye)));
        lookMatrix.SetRow(3, new Vector4(0, 0, 0, 1));
        
        return lookMatrix;
    }
    
    void DebugCameraMatrices()
    {
        Matrix4x4 viewMatrix = cam.worldToCameraMatrix;
        Matrix4x4 projectionMatrix = cam.projectionMatrix;
        Matrix4x4 viewProjectionMatrix = projectionMatrix * viewMatrix;
        
        Debug.Log($"View Matrix:\n{MatrixToString(viewMatrix)}");
        Debug.Log($"Projection Matrix:\n{MatrixToString(projectionMatrix)}");
        
        // Debug camera frustum
        DebugCameraFrustum();
    }
    
    void DebugCameraFrustum()
    {
        Matrix4x4 matrix = cam.projectionMatrix * cam.worldToCameraMatrix;
        
        // Extract frustum planes from view-projection matrix
        Plane[] frustumPlanes = GeometryUtility.CalculateFrustumPlanes(matrix);
        
        // Draw frustum bounds
        float nearDistance = cam.nearClipPlane;
        float farDistance = cam.farClipPlane;
        
        Vector3[] nearCorners = new Vector3[4];
        Vector3[] farCorners = new Vector3[4];
        
        cam.CalculateFrustumCorners(new Rect(0, 0, 1, 1), nearDistance, Camera.MonoOrStereoscopicEye.Mono, nearCorners);
        cam.CalculateFrustumCorners(new Rect(0, 0, 1, 1), farDistance, Camera.MonoOrStereoscopicEye.Mono, farCorners);
        
        // Transform corners to world space
        for (int i = 0; i < 4; i++)
        {
            nearCorners[i] = cam.transform.TransformPoint(nearCorners[i]);
            farCorners[i] = cam.transform.TransformPoint(farCorners[i]);
        }
        
        // Draw frustum lines
        for (int i = 0; i < 4; i++)
        {
            Debug.DrawLine(nearCorners[i], farCorners[i], Color.white);
            Debug.DrawLine(nearCorners[i], nearCorners[(i + 1) % 4], Color.cyan);
            Debug.DrawLine(farCorners[i], farCorners[(i + 1) % 4], Color.magenta);
        }
    }
    
    Quaternion ExtractRotation(Matrix4x4 matrix)
    {
        Vector3 forward = new Vector3(matrix.m02, matrix.m12, matrix.m22);
        Vector3 upwards = new Vector3(matrix.m01, matrix.m11, matrix.m21);
        return Quaternion.LookRotation(forward, upwards);
    }
    
    string MatrixToString(Matrix4x4 matrix)
    {
        return $"[{matrix.m00:F2}, {matrix.m01:F2}, {matrix.m02:F2}, {matrix.m03:F2}]\n" +
               $"[{matrix.m10:F2}, {matrix.m11:F2}, {matrix.m12:F2}, {matrix.m13:F2}]\n" +
               $"[{matrix.m20:F2}, {matrix.m21:F2}, {matrix.m22:F2}, {matrix.m23:F2}]\n" +
               $"[{matrix.m30:F2}, {matrix.m31:F2}, {matrix.m32:F2}, {matrix.m33:F2}]";
    }
}
```

## Interview Preparation

### Matrix Mathematics Questions

**Common Technical Questions:**
- "Explain the order of operations in transformation matrices (TRS vs RST)"
- "How do you decompose a transformation matrix back into position, rotation, and scale?"
- "What's the difference between multiplying a vector by a matrix vs multiplying matrices?"
- "How would you implement a custom coordinate system transformation?"

**Practical Implementation Questions:**
```csharp
// Interview question: "Implement matrix-based object following"
public class MatrixFollower : MonoBehaviour
{
    public Transform target;
    public float followSpeed = 2f;
    public Vector3 offset = Vector3.back * 5f;
    
    void Update()
    {
        if (target == null) return;
        
        // Create target's transformation matrix
        Matrix4x4 targetMatrix = target.localToWorldMatrix;
        
        // Apply offset in target's local space
        Vector4 localOffset = new Vector4(offset.x, offset.y, offset.z, 1f);
        Vector4 worldOffset = targetMatrix * localOffset;
        
        // Calculate desired position
        Vector3 desiredPosition = new Vector3(worldOffset.x, worldOffset.y, worldOffset.z);
        
        // Smooth follow
        transform.position = Vector3.Lerp(transform.position, desiredPosition, followSpeed * Time.deltaTime);
        
        // Match target rotation
        transform.rotation = Quaternion.Lerp(transform.rotation, target.rotation, followSpeed * Time.deltaTime);
    }
}

// "How would you create a custom projection matrix?"
public Matrix4x4 CreateCustomProjectionMatrix(float fov, float aspect, float near, float far)
{
    float f = 1.0f / Mathf.Tan(fov * 0.5f * Mathf.Deg2Rad);
    
    Matrix4x4 projection = new Matrix4x4();
    projection.m00 = f / aspect;
    projection.m11 = f;
    projection.m22 = (far + near) / (near - far);
    projection.m23 = (2.0f * far * near) / (near - far);
    projection.m32 = -1.0f;
    projection.m33 = 0.0f;
    
    return projection;
}
```

### Key Takeaways

**Essential Matrix Concepts:**
- Master transformation matrix composition and decomposition
- Understand coordinate system conversions and their applications
- Apply matrix interpolation for smooth animations and transitions
- Implement camera systems using matrix calculations

**Practical Unity Applications:**
- Build advanced camera controllers with matrix-based calculations
- Create custom coordinate systems for specialized gameplay mechanics
- Optimize transformations using matrix operations
- Debug rendering issues using matrix analysis and visualization