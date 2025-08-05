# @b-Matrix-Transformations-3D - Advanced Matrix Mathematics for 3D Graphics

## 🎯 Learning Objectives
- Master 3D transformation matrices for position, rotation, and scaling operations
- Implement practical matrix mathematics for camera systems and object manipulation
- Develop AI-enhanced understanding of coordinate spaces and transformation hierarchies
- Create systematic approach to complex 3D transformations and rendering pipelines

## 🔧 Matrix Transformation Architecture

### The MATRIX Framework for 3D Transformations
```
M - Mathematics: Understand fundamental matrix operations and linear algebra
A - Applications: Apply transformations to real-world 3D graphics problems
T - Transformations: Master translation, rotation, scaling, and projection matrices
R - Relationships: Comprehend coordinate spaces and transformation hierarchies
I - Implementation: Code efficient matrix operations in Unity and C#
X - eXpert: Solve complex transformation problems and optimization challenges
```

### Unity Matrix Mathematics System
```csharp
using UnityEngine;
using System.Collections.Generic;

/// <summary>
/// Comprehensive matrix mathematics system for Unity 3D transformations
/// Provides essential matrix operations, coordinate space conversions, and transformation utilities
/// </summary>
public static class MatrixMathUtility
{
    // Constants for matrix operations
    public const float EPSILON = 0.0001f;
    public const float DEG_TO_RAD = Mathf.PI / 180f;
    public const float RAD_TO_DEG = 180f / Mathf.PI;
    
    #region Basic Matrix Operations
    
    /// <summary>
    /// Create translation matrix from Vector3 position
    /// Essential for moving objects in 3D space
    /// </summary>
    public static Matrix4x4 CreateTranslationMatrix(Vector3 translation)
    {
        Matrix4x4 matrix = Matrix4x4.identity;
        matrix.m03 = translation.x;
        matrix.m13 = translation.y;
        matrix.m23 = translation.z;
        return matrix;
    }
    
    /// <summary>
    /// Create rotation matrix from Euler angles (in degrees)
    /// Critical for object orientation and camera control
    /// </summary>
    public static Matrix4x4 CreateRotationMatrix(Vector3 eulerAngles)
    {
        return Matrix4x4.Rotate(Quaternion.Euler(eulerAngles));
    }
    
    /// <summary>
    /// Create rotation matrix from quaternion
    /// More efficient and stable than Euler angles for complex rotations
    /// </summary>
    public static Matrix4x4 CreateRotationMatrix(Quaternion rotation)
    {
        return Matrix4x4.Rotate(rotation);
    }
    
    /// <summary>
    /// Create scaling matrix from Vector3 scale factors
    /// Essential for resizing objects along different axes
    /// </summary>
    public static Matrix4x4 CreateScaleMatrix(Vector3 scale)
    {
        Matrix4x4 matrix = Matrix4x4.identity;
        matrix.m00 = scale.x;
        matrix.m11 = scale.y;
        matrix.m22 = scale.z;
        return matrix;
    }
    
    /// <summary>
    /// Create uniform scaling matrix
    /// Convenient for proportional scaling operations
    /// </summary>
    public static Matrix4x4 CreateUniformScaleMatrix(float scale)
    {
        return CreateScaleMatrix(Vector3.one * scale);
    }
    
    #endregion
    
    #region Composite Transformations
    
    /// <summary>
    /// Create transformation matrix combining translation, rotation, and scale
    /// Order: Scale -> Rotate -> Translate (TRS order)
    /// </summary>
    public static Matrix4x4 CreateTRSMatrix(Vector3 translation, Quaternion rotation, Vector3 scale)
    {
        return Matrix4x4.TRS(translation, rotation, scale);
    }
    
    /// <summary>
    /// Create transformation matrix from Transform component
    /// Convenient wrapper for Unity Transform to Matrix conversion
    /// </summary>
    public static Matrix4x4 CreateTransformMatrix(Transform transform)
    {
        return transform.localToWorldMatrix;
    }
    
    /// <summary>
    /// Decompose transformation matrix into translation, rotation, and scale
    /// Essential for extracting transformation components from matrices
    /// </summary>
    public static void DecomposeMatrix(Matrix4x4 matrix, out Vector3 translation, out Quaternion rotation, out Vector3 scale)
    {
        // Extract translation
        translation = new Vector3(matrix.m03, matrix.m13, matrix.m23);
        
        // Extract scale
        scale = new Vector3(
            new Vector4(matrix.m00, matrix.m10, matrix.m20, matrix.m30).magnitude,
            new Vector4(matrix.m01, matrix.m11, matrix.m21, matrix.m31).magnitude,
            new Vector4(matrix.m02, matrix.m12, matrix.m22, matrix.m32).magnitude
        );
        
        // Remove scale from matrix to extract pure rotation
        Matrix4x4 rotationMatrix = matrix;
        rotationMatrix.m00 /= scale.x; rotationMatrix.m10 /= scale.x; rotationMatrix.m20 /= scale.x;
        rotationMatrix.m01 /= scale.y; rotationMatrix.m11 /= scale.y; rotationMatrix.m21 /= scale.y;
        rotationMatrix.m02 /= scale.z; rotationMatrix.m12 /= scale.z; rotationMatrix.m22 /= scale.z;
        
        rotation = rotationMatrix.rotation;
    }
    
    #endregion
    
    #region Coordinate Space Conversions
    
    /// <summary>
    /// Transform point from local space to world space
    /// Essential for converting object-relative positions to world positions
    /// </summary>
    public static Vector3 TransformPoint(Matrix4x4 transformMatrix, Vector3 localPoint)
    {
        return transformMatrix.MultiplyPoint3x4(localPoint);
    }
    
    /// <summary>
    /// Transform direction from local space to world space
    /// Critical for converting object-relative directions (ignores translation)
    /// </summary>
    public static Vector3 TransformDirection(Matrix4x4 transformMatrix, Vector3 localDirection)
    {
        return transformMatrix.MultiplyVector(localDirection);
    }
    
    /// <summary>
    /// Transform normal vector from local space to world space
    /// Essential for lighting calculations and surface orientation
    /// </summary>
    public static Vector3 TransformNormal(Matrix4x4 transformMatrix, Vector3 localNormal)
    {
        // Use inverse transpose for correct normal transformation
        Matrix4x4 inverseTranspose = transformMatrix.inverse.transpose;
        return inverseTranspose.MultiplyVector(localNormal).normalized;
    }
    
    /// <summary>
    /// Convert world space position to screen space coordinates
    /// Critical for UI positioning and screen-relative calculations
    /// </summary>
    public static Vector3 WorldToScreenPoint(Vector3 worldPosition, Camera camera)
    {
        return camera.WorldToScreenPoint(worldPosition);
    }
    
    /// <summary>
    /// Convert screen space coordinates to world space position
    /// Essential for mouse picking and screen-to-world interactions
    /// </summary>
    public static Vector3 ScreenToWorldPoint(Vector3 screenPosition, Camera camera)
    {
        return camera.ScreenToWorldPoint(screenPosition);
    }
    
    #endregion
    
    #region View and Projection Matrices
    
    /// <summary>
    /// Create look-at view matrix
    /// Essential for camera positioning and orientation
    /// </summary>
    public static Matrix4x4 CreateLookAtMatrix(Vector3 eye, Vector3 target, Vector3 up)
    {
        Vector3 forward = (target - eye).normalized;
        Vector3 right = Vector3.Cross(forward, up).normalized;
        Vector3 realUp = Vector3.Cross(right, forward);
        
        Matrix4x4 matrix = Matrix4x4.identity;
        
        // Set rotation part
        matrix.m00 = right.x;    matrix.m01 = realUp.x;   matrix.m02 = -forward.x;
        matrix.m10 = right.y;    matrix.m11 = realUp.y;   matrix.m12 = -forward.y;
        matrix.m20 = right.z;    matrix.m21 = realUp.z;   matrix.m22 = -forward.z;
        
        // Set translation part
        matrix.m03 = -Vector3.Dot(right, eye);
        matrix.m13 = -Vector3.Dot(realUp, eye);
        matrix.m23 = Vector3.Dot(forward, eye);
        
        return matrix;
    }
    
    /// <summary>
    /// Create perspective projection matrix
    /// Critical for 3D rendering and camera perspective
    /// </summary>
    public static Matrix4x4 CreatePerspectiveMatrix(float fovY, float aspectRatio, float nearPlane, float farPlane)
    {
        float f = 1.0f / Mathf.Tan(fovY * 0.5f * DEG_TO_RAD);
        
        Matrix4x4 matrix = Matrix4x4.zero;
        matrix.m00 = f / aspectRatio;
        matrix.m11 = f;
        matrix.m22 = (farPlane + nearPlane) / (nearPlane - farPlane);
        matrix.m23 = (2.0f * farPlane * nearPlane) / (nearPlane - farPlane);
        matrix.m32 = -1.0f;
        
        return matrix;
    }
    
    /// <summary>
    /// Create orthographic projection matrix
    /// Essential for 2D rendering and UI elements
    /// </summary>
    public static Matrix4x4 CreateOrthographicMatrix(float left, float right, float bottom, float top, float nearPlane, float farPlane)
    {
        Matrix4x4 matrix = Matrix4x4.identity;
        
        matrix.m00 = 2.0f / (right - left);
        matrix.m11 = 2.0f / (top - bottom);
        matrix.m22 = -2.0f / (farPlane - nearPlane);
        
        matrix.m03 = -(right + left) / (right - left);
        matrix.m13 = -(top + bottom) / (top - bottom);
        matrix.m23 = -(farPlane + nearPlane) / (farPlane - nearPlane);
        
        return matrix;
    }
    
    #endregion
    
    #region Advanced Matrix Operations
    
    /// <summary>
    /// Interpolate between two transformation matrices
    /// Essential for smooth transitions and animation blending
    /// </summary>
    public static Matrix4x4 InterpolateMatrix(Matrix4x4 from, Matrix4x4 to, float t)
    {
        // Decompose matrices
        DecomposeMatrix(from, out Vector3 fromPos, out Quaternion fromRot, out Vector3 fromScale);
        DecomposeMatrix(to, out Vector3 toPos, out Quaternion toRot, out Vector3 toScale);
        
        // Interpolate components
        Vector3 lerpPos = Vector3.Lerp(fromPos, toPos, t);
        Quaternion slerpRot = Quaternion.Slerp(fromRot, toRot, t);
        Vector3 lerpScale = Vector3.Lerp(fromScale, toScale, t);
        
        return CreateTRSMatrix(lerpPos, slerpRot, lerpScale);
    }
    
    /// <summary>
    /// Calculate matrix determinant (3x3 portion)
    /// Useful for detecting matrix validity and handedness
    /// </summary>
    public static float CalculateDeterminant3x3(Matrix4x4 matrix)
    {
        return matrix.m00 * (matrix.m11 * matrix.m22 - matrix.m12 * matrix.m21) -
               matrix.m01 * (matrix.m10 * matrix.m22 - matrix.m12 * matrix.m20) +
               matrix.m02 * (matrix.m10 * matrix.m21 - matrix.m11 * matrix.m20);
    }
    
    /// <summary>
    /// Check if matrix is valid (non-degenerate)
    /// Essential for validation in transformation chains
    /// </summary>
    public static bool IsValidMatrix(Matrix4x4 matrix)
    {
        float det = CalculateDeterminant3x3(matrix);
        return Mathf.Abs(det) > EPSILON;
    }
    
    #endregion
}

/// <summary>
/// Practical matrix transformation examples for common game development scenarios
/// Demonstrates real-world application of matrix mathematics
/// </summary>
public class MatrixTransformationExamples : MonoBehaviour
{
    [Header("Transformation Settings")]
    public Transform targetObject;
    public float rotationSpeed = 45f;
    public float scaleSpeed = 1f;
    public AnimationCurve scaleCurve = AnimationCurve.EaseInOut(0, 1, 1, 2);
    
    [Header("Camera Settings")]
    public Camera targetCamera;
    public Transform lookAtTarget;
    public float cameraDistance = 10f;
    public float cameraHeight = 5f;
    
    [Header("Animation Settings")]
    public Transform[] animationKeyframes;
    public float animationDuration = 5f;
    
    private float animationTime = 0f;
    private Matrix4x4[] keyframeMatrices;
    
    void Start()
    {
        // Pre-calculate keyframe matrices for efficient animation
        if (animationKeyframes != null && animationKeyframes.Length > 0)
        {
            keyframeMatrices = new Matrix4x4[animationKeyframes.Length];
            for (int i = 0; i < animationKeyframes.Length; i++)
            {
                if (animationKeyframes[i] != null)
                {
                    keyframeMatrices[i] = MatrixMathUtility.CreateTransformMatrix(animationKeyframes[i]);
                }
            }
        }
    }
    
    void Update()
    {
        // Example 1: Manual transformation matrix creation
        DemonstrateMatrixTransformation();
        
        // Example 2: Camera matrix manipulation
        UpdateCameraWithMatrices();
        
        // Example 3: Matrix-based animation
        AnimateWithMatrices();
    }
    
    #region Matrix Transformation Examples
    
    /// <summary>
    /// Example: Creating and applying transformation matrices manually
    /// Demonstrates building complex transformations from basic operations
    /// </summary>
    void DemonstrateMatrixTransformation()
    {
        if (targetObject == null) return;
        
        // Create individual transformation matrices
        Vector3 translation = new Vector3(Mathf.Sin(Time.time) * 3f, 0, 0);
        Vector3 rotation = new Vector3(0, Time.time * rotationSpeed, 0);
        float scaleValue = scaleCurve.Evaluate(Mathf.PingPong(Time.time * scaleSpeed, 1f));
        Vector3 scale = Vector3.one * scaleValue;
        
        // Method 1: Using Unity's built-in TRS
        Matrix4x4 transformMatrix = MatrixMathUtility.CreateTRSMatrix(
            translation,
            Quaternion.Euler(rotation),
            scale
        );
        
        // Method 2: Combining matrices manually (for educational purposes)
        Matrix4x4 translationMatrix = MatrixMathUtility.CreateTranslationMatrix(translation);
        Matrix4x4 rotationMatrix = MatrixMathUtility.CreateRotationMatrix(rotation);
        Matrix4x4 scaleMatrix = MatrixMathUtility.CreateScaleMatrix(scale);
        
        // Matrix multiplication order: Translation * Rotation * Scale
        Matrix4x4 combinedMatrix = translationMatrix * rotationMatrix * scaleMatrix;
        
        // Extract and apply transformation
        MatrixMathUtility.DecomposeMatrix(transformMatrix, out Vector3 pos, out Quaternion rot, out Vector3 scl);
        
        targetObject.position = pos;
        targetObject.rotation = rot;
        targetObject.localScale = scl;
    }
    
    /// <summary>
    /// Example: Creating a custom camera controller using matrices
    /// Demonstrates view matrix creation and camera positioning
    /// </summary>
    void UpdateCameraWithMatrices()
    {
        if (targetCamera == null || lookAtTarget == null) return;
        
        // Calculate camera position using circular motion
        float angle = Time.time * 30f * Mathf.Deg2Rad;
        Vector3 cameraPosition = lookAtTarget.position + new Vector3(
            Mathf.Cos(angle) * cameraDistance,
            cameraHeight,
            Mathf.Sin(angle) * cameraDistance
        );
        
        // Create look-at matrix
        Matrix4x4 viewMatrix = MatrixMathUtility.CreateLookAtMatrix(
            cameraPosition,
            lookAtTarget.position,
            Vector3.up
        );
        
        // Extract camera transform from view matrix
        Matrix4x4 cameraMatrix = viewMatrix.inverse;
        MatrixMathUtility.DecomposeMatrix(cameraMatrix, out Vector3 pos, out Quaternion rot, out Vector3 scale);
        
        targetCamera.transform.position = pos;
        targetCamera.transform.rotation = rot;
    }
    
    /// <summary>
    /// Example: Matrix-based keyframe animation system
    /// Demonstrates smooth interpolation between transformation matrices
    /// </summary>
    void AnimateWithMatrices()
    {
        if (keyframeMatrices == null || keyframeMatrices.Length < 2) return;
        
        animationTime += Time.deltaTime;
        float normalizedTime = (animationTime % animationDuration) / animationDuration;
        
        // Calculate which keyframes to interpolate between
        float frameFloat = normalizedTime * (keyframeMatrices.Length - 1);
        int frameIndex = Mathf.FloorToInt(frameFloat);
        float frameLerp = frameFloat - frameIndex;
        
        // Ensure we don't go out of bounds
        int nextFrameIndex = (frameIndex + 1) % keyframeMatrices.Length;
        
        // Interpolate between keyframe matrices
        Matrix4x4 currentMatrix = MatrixMathUtility.InterpolateMatrix(
            keyframeMatrices[frameIndex],
            keyframeMatrices[nextFrameIndex],
            frameLerp
        );
        
        // Apply interpolated transformation
        MatrixMathUtility.DecomposeMatrix(currentMatrix, out Vector3 pos, out Quaternion rot, out Vector3 scale);
        
        if (targetObject != null)
        {
            targetObject.position = pos;
            targetObject.rotation = rot;
            targetObject.localScale = scale;
        }
    }
    
    #endregion
    
    #region Debug Visualization
    
    /// <summary>
    /// Visualize transformation matrices and coordinate systems
    /// Essential for debugging matrix operations and understanding transformations
    /// </summary>
    void OnDrawGizmos()
    {
        if (targetObject != null)
        {
            // Draw local coordinate system
            DrawCoordinateSystem(targetObject.position, targetObject.rotation, 2f);
            
            // Draw transformation path for animation
            if (keyframeMatrices != null && keyframeMatrices.Length > 1)
            {
                Gizmos.color = Color.yellow;
                for (int i = 0; i < keyframeMatrices.Length - 1; i++)
                {
                    Vector3 currentPos = new Vector3(keyframeMatrices[i].m03, keyframeMatrices[i].m13, keyframeMatrices[i].m23);
                    Vector3 nextPos = new Vector3(keyframeMatrices[i + 1].m03, keyframeMatrices[i + 1].m13, keyframeMatrices[i + 1].m23);
                    Gizmos.DrawLine(currentPos, nextPos);
                }
            }
        }
        
        // Draw camera frustum if camera is assigned
        if (targetCamera != null)
        {
            Gizmos.color = Color.blue;
            Gizmos.matrix = targetCamera.transform.localToWorldMatrix;
            Gizmos.DrawFrustum(Vector3.zero, targetCamera.fieldOfView, targetCamera.farClipPlane, targetCamera.nearClipPlane, targetCamera.aspect);
            Gizmos.matrix = Matrix4x4.identity;
        }
    }
    
    /// <summary>
    /// Helper method to draw coordinate system axes
    /// Useful for visualizing object orientation and transformation results
    /// </summary>
    void DrawCoordinateSystem(Vector3 position, Quaternion rotation, float scale)
    {
        // Draw X axis (red)
        Gizmos.color = Color.red;
        Gizmos.DrawLine(position, position + rotation * Vector3.right * scale);
        
        // Draw Y axis (green)
        Gizmos.color = Color.green;
        Gizmos.DrawLine(position, position + rotation * Vector3.up * scale);
        
        // Draw Z axis (blue)
        Gizmos.color = Color.blue;
        Gizmos.DrawLine(position, position + rotation * Vector3.forward * scale);
    }
    
    #endregion
}

/// <summary>
/// Advanced matrix operations for complex graphics and animation systems
/// Includes custom projection matrices, bone transformations, and optimization techniques
/// </summary>
public static class AdvancedMatrixOperations
{
    #region Custom Projections
    
    /// <summary>
    /// Create oblique projection matrix for mirror/portal effects
    /// Essential for realistic reflections and portal rendering
    /// </summary>
    public static Matrix4x4 CreateObliqueMatrix(Matrix4x4 projection, Vector4 clipPlane)
    {
        Vector4 q = projection.inverse * new Vector4(
            Mathf.Sign(clipPlane.x),
            Mathf.Sign(clipPlane.y),
            1.0f,
            1.0f
        );
        
        Vector4 c = clipPlane * (2.0f / Vector4.Dot(clipPlane, q));
        
        // Replace the third row of the projection matrix
        projection[2] = c.x - projection[3];
        projection[6] = c.y - projection[7];
        projection[10] = c.z - projection[11];
        projection[14] = c.w - projection[15];
        
        return projection;
    }
    
    /// <summary>
    /// Create shadow projection matrix for planar shadows
    /// Useful for efficient real-time shadow rendering
    /// </summary>
    public static Matrix4x4 CreateShadowMatrix(Vector4 plane, Vector3 lightPosition)
    {
        float dot = Vector3.Dot(new Vector3(plane.x, plane.y, plane.z), lightPosition) + plane.w;
        
        Matrix4x4 shadowMatrix = new Matrix4x4();
        
        shadowMatrix.m00 = dot - lightPosition.x * plane.x;
        shadowMatrix.m10 = -lightPosition.y * plane.x;
        shadowMatrix.m20 = -lightPosition.z * plane.x;
        shadowMatrix.m30 = -plane.x;
        
        shadowMatrix.m01 = -lightPosition.x * plane.y;
        shadowMatrix.m11 = dot - lightPosition.y * plane.y;
        shadowMatrix.m21 = -lightPosition.z * plane.y;
        shadowMatrix.m31 = -plane.y;
        
        shadowMatrix.m02 = -lightPosition.x * plane.z;
        shadowMatrix.m12 = -lightPosition.y * plane.z;
        shadowMatrix.m22 = dot - lightPosition.z * plane.z;
        shadowMatrix.m32 = -plane.z;
        
        shadowMatrix.m03 = -lightPosition.x * plane.w;
        shadowMatrix.m13 = -lightPosition.y * plane.w;
        shadowMatrix.m23 = -lightPosition.z * plane.w;
        shadowMatrix.m33 = dot - plane.w;
        
        return shadowMatrix;
    }
    
    #endregion
    
    #region Skeletal Animation
    
    /// <summary>
    /// Calculate bone transformation matrix for skeletal animation
    /// Essential for character animation and rigging systems
    /// </summary>
    public static Matrix4x4 CalculateBoneMatrix(Transform bone, Matrix4x4 bindPose)
    {
        return bone.localToWorldMatrix * bindPose;
    }
    
    /// <summary>
    /// Blend multiple transformation matrices with weights
    /// Critical for animation blending and state transitions
    /// </summary>
    public static Matrix4x4 BlendMatrices(Matrix4x4[] matrices, float[] weights)
    {
        if (matrices.Length != weights.Length || matrices.Length == 0)
            return Matrix4x4.identity;
        
        // Decompose all matrices
        Vector3[] positions = new Vector3[matrices.Length];
        Quaternion[] rotations = new Quaternion[matrices.Length];
        Vector3[] scales = new Vector3[matrices.Length];
        
        for (int i = 0; i < matrices.Length; i++)
        {
            MatrixMathUtility.DecomposeMatrix(matrices[i], out positions[i], out rotations[i], out scales[i]);
        }
        
        // Blend components
        Vector3 blendedPosition = Vector3.zero;
        Vector3 blendedScale = Vector3.zero;
        Quaternion blendedRotation = new Quaternion(0, 0, 0, 0);
        
        float totalWeight = 0f;
        for (int i = 0; i < weights.Length; i++)
        {
            totalWeight += weights[i];
            blendedPosition += positions[i] * weights[i];
            blendedScale += scales[i] * weights[i];
            
            // Quaternion blending requires special handling
            if (i == 0)
            {
                blendedRotation = rotations[i];
            }
            else
            {
                blendedRotation = Quaternion.Slerp(blendedRotation, rotations[i], weights[i] / totalWeight);
            }
        }
        
        // Normalize by total weight
        if (totalWeight > 0)
        {
            blendedPosition /= totalWeight;
            blendedScale /= totalWeight;
        }
        
        return MatrixMathUtility.CreateTRSMatrix(blendedPosition, blendedRotation, blendedScale);
    }
    
    #endregion
    
    #region Performance Optimizations
    
    /// <summary>
    /// Cache for frequently used matrices to avoid recalculation
    /// Essential for performance in systems with many transformations
    /// </summary>
    public class MatrixCache
    {
        private Dictionary<int, Matrix4x4> cache = new Dictionary<int, Matrix4x4>();
        private Dictionary<int, float> timestamps = new Dictionary<int, float>();
        private float cacheTimeout = 0.1f; // Cache for 100ms
        
        public Matrix4x4 GetOrCalculate(int key, System.Func<Matrix4x4> calculator)
        {
            if (cache.ContainsKey(key) && Time.time - timestamps[key] < cacheTimeout)
            {
                return cache[key];
            }
            
            Matrix4x4 result = calculator();
            cache[key] = result;
            timestamps[key] = Time.time;
            
            return result;
        }
        
        public void ClearExpired()
        {
            var keysToRemove = new List<int>();
            foreach (var kvp in timestamps)
            {
                if (Time.time - kvp.Value > cacheTimeout)
                {
                    keysToRemove.Add(kvp.Key);
                }
            }
            
            foreach (int key in keysToRemove)
            {
                cache.Remove(key);
                timestamps.Remove(key);
            }
        }
    }
    
    /// <summary>
    /// Efficient batch transformation of multiple points
    /// Optimized for processing large numbers of vertices or positions
    /// </summary>
    public static void TransformPointsBatch(Matrix4x4 matrix, Vector3[] inputPoints, Vector3[] outputPoints)
    {
        if (inputPoints.Length != outputPoints.Length)
            throw new System.ArgumentException("Input and output arrays must have same length");
        
        for (int i = 0; i < inputPoints.Length; i++)
        {
            outputPoints[i] = matrix.MultiplyPoint3x4(inputPoints[i]);
        }
    }
    
    #endregion
}

/// <summary>
/// Matrix-based camera system for advanced rendering techniques
/// Demonstrates custom camera controls and rendering pipeline integration
/// </summary>
public class MatrixCameraController : MonoBehaviour
{
    [Header("Camera Settings")]
    public Camera controlledCamera;
    public Transform target;
    public float distance = 10f;
    public float height = 5f;
    public float rotationSpeed = 2f;
    
    [Header("Projection Settings")]
    public bool useCustomProjection = false;
    public float customFOV = 60f;
    public float customNear = 0.1f;
    public float customFar = 1000f;
    
    private Vector2 rotation;
    private Matrix4x4 originalProjection;
    
    void Start()
    {
        if (controlledCamera == null)
            controlledCamera = Camera.main;
            
        originalProjection = controlledCamera.projectionMatrix;
    }
    
    void LateUpdate()
    {
        HandleCameraInput();
        UpdateCameraPosition();
        UpdateProjectionMatrix();
    }
    
    /// <summary>
    /// Handle input for camera rotation
    /// Demonstrates matrix-based camera control system
    /// </summary>
    void HandleCameraInput()
    {
        if (Input.GetMouseButton(1)) // Right mouse button
        {
            rotation.x += Input.GetAxis("Mouse X") * rotationSpeed;
            rotation.y -= Input.GetAxis("Mouse Y") * rotationSpeed;
            rotation.y = Mathf.Clamp(rotation.y, -80f, 80f);
        }
    }
    
    /// <summary>
    /// Update camera position using matrix transformations
    /// Shows practical application of look-at matrix creation
    /// </summary>
    void UpdateCameraPosition()
    {
        if (target == null) return;
        
        // Calculate camera position using spherical coordinates
        Quaternion cameraRotation = Quaternion.Euler(rotation.y, rotation.x, 0);
        Vector3 offset = cameraRotation * new Vector3(0, height, -distance);
        Vector3 cameraPosition = target.position + offset;
        
        // Create view matrix manually
        Matrix4x4 viewMatrix = MatrixMathUtility.CreateLookAtMatrix(
            cameraPosition,
            target.position,
            Vector3.up
        );
        
        // Apply transformation to camera
        controlledCamera.worldToCameraMatrix = viewMatrix;
    }
    
    /// <summary>
    /// Update projection matrix for custom rendering effects
    /// Demonstrates custom projection matrix manipulation
    /// </summary>
    void UpdateProjectionMatrix()
    {
        if (useCustomProjection)
        {
            Matrix4x4 customProjection = MatrixMathUtility.CreatePerspectiveMatrix(
                customFOV,
                controlledCamera.aspect,
                customNear,
                customFar
            );
            
            controlledCamera.projectionMatrix = customProjection;
        }
        else
        {
            controlledCamera.ResetProjectionMatrix();
        }
    }
    
    void OnDisable()
    {
        // Restore original projection matrix
        if (controlledCamera != null)
        {
            controlledCamera.projectionMatrix = originalProjection;
        }
    }
}
```

## 🎯 Matrix Mathematics Fundamentals

### Core Matrix Concepts
```markdown
## Essential Matrix Mathematics for 3D Graphics

### Matrix Basics
**Definition**: A matrix is a rectangular array of numbers used to represent transformations
**4x4 Matrices**: Standard for 3D graphics, combining rotation, translation, and scaling
**Identity Matrix**: No transformation applied (like multiplying by 1)
**Matrix Multiplication**: Combines multiple transformations (order matters!)

### Transformation Types
**Translation**: Moving objects in 3D space (position change)
**Rotation**: Rotating objects around axes (orientation change)
**Scaling**: Resizing objects (size change)
**Projection**: Converting 3D coordinates to 2D screen coordinates

### Matrix Multiplication Order
**Unity Convention**: TRS (Translation × Rotation × Scale)
**Application Order**: Scale first, then rotate, then translate
**Composition**: Multiple transformations combine through multiplication
**Inverse**: Undoes transformations (essential for coordinate space conversions)

### Coordinate Spaces
**Local Space**: Object's own coordinate system
**World Space**: Global coordinate system for the scene
**View Space**: Camera's coordinate system
**Screen Space**: 2D coordinates on the screen
```

### Practical Applications
```csharp
/// <summary>
/// Real-world matrix applications in game development
/// Demonstrates practical usage patterns and common scenarios
/// </summary>
public class MatrixApplications : MonoBehaviour
{
    /// <summary>
    /// Example: Weapon positioning system using matrices
    /// Shows how to maintain weapon position relative to character
    /// </summary>
    public void PositionWeaponWithMatrix(Transform weapon, Transform hand, Vector3 localOffset, Vector3 localRotation)
    {
        // Create offset transformation matrix
        Matrix4x4 offsetMatrix = MatrixMathUtility.CreateTRSMatrix(
            localOffset,
            Quaternion.Euler(localRotation),
            Vector3.one
        );
        
        // Combine with hand transformation
        Matrix4x4 finalMatrix = hand.localToWorldMatrix * offsetMatrix;
        
        // Apply to weapon
        MatrixMathUtility.DecomposeMatrix(finalMatrix, out Vector3 pos, out Quaternion rot, out Vector3 scale);
        weapon.position = pos;
        weapon.rotation = rot;
    }
    
    /// <summary>
    /// Example: Portal rendering system using custom view matrices
    /// Demonstrates advanced matrix manipulation for special effects
    /// </summary>
    public Matrix4x4 CalculatePortalViewMatrix(Transform portal, Transform camera, Transform linkedPortal)
    {
        // Calculate relative transformation from camera to portal
        Matrix4x4 cameraToPortal = portal.worldToLocalMatrix * camera.localToWorldMatrix;
        
        // Apply transformation through linked portal
        Matrix4x4 portalToLinked = linkedPortal.localToWorldMatrix;
        
        // Combine transformations
        return (portalToLinked * cameraToPortal).inverse;
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Advanced Mathematics Learning
- **Matrix Visualization**: AI-generated interactive visualizations of matrix transformations and operations
- **Problem Solving**: AI-assisted analysis of complex transformation problems and step-by-step solutions
- **Code Generation**: AI-powered generation of optimized matrix operations for specific use cases

### Graphics Programming Enhancement
- **Shader Integration**: AI-enhanced matrix calculations for custom shaders and rendering effects
- **Animation Systems**: AI-powered skeletal animation and transformation blending algorithms
- **Performance Optimization**: AI analysis of matrix operations for performance bottlenecks and improvements

### Educational Applications
- **Interactive Learning**: AI-powered tutorials for understanding coordinate spaces and transformations
- **Visual Debugging**: AI-generated debugging tools for transformation hierarchy visualization
- **Practice Exercises**: AI-created matrix mathematics problems with increasing complexity levels

## 💡 Key Highlights

- **Master the MATRIX Framework** for systematic approach to 3D transformation mathematics
- **Understand Coordinate Space Conversions** between local, world, view, and screen spaces
- **Implement Efficient Matrix Operations** for position, rotation, scaling, and projection calculations
- **Build Advanced Camera Systems** using custom view and projection matrix manipulation
- **Optimize Performance** through matrix caching and batch transformation operations
- **Apply to Real-World Problems** including skeletal animation, portal rendering, and special effects
- **Debug and Visualize** transformations using coordinate system drawing and matrix decomposition
- **Focus on Practical Implementation** solving actual 3D graphics and animation challenges