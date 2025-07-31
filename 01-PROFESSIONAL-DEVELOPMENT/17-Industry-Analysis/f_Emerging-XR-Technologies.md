# @f-Emerging-XR-Technologies - Extended Reality Development Mastery

## 🎯 Learning Objectives
- Master VR/AR/MR development in Unity
- Implement hand tracking and gesture recognition
- Optimize performance for XR platforms
- Understand spatial computing principles

## 🔧 Core XR Development Concepts

### Unity XR Toolkit Setup
```csharp
using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;
using UnityEngine.XR;

public class XRManager : MonoBehaviour
{
    [Header("XR Configuration")]
    public XRRig xrRig;
    public XRInteractionManager interactionManager;
    public LayerMask interactionLayerMask;
    
    [Header("Hand Tracking")]
    public bool enableHandTracking = true;
    public HandTrackingProvider handTrackingProvider;
    
    private bool isXRActive = false;
    
    private void Start()
    {
        InitializeXR();
    }
    
    private void InitializeXR()
    {
        // Check if XR device is available
        if (XRSettings.isDeviceActive)
        {
            isXRActive = true;
            ConfigureXRInteractions();
            
            if (enableHandTracking)
            {
                SetupHandTracking();
            }
            
            Debug.Log($"XR initialized for device: {XRSettings.loadedDeviceName}");
        }
        else
        {
            Debug.LogWarning("No XR device detected");
            EnableDesktopFallback();
        }
    }
    
    private void ConfigureXRInteractions()
    {
        // Setup interaction system
        interactionManager.enabled = true;
        
        // Configure ray interactors
        var leftRayInteractor = xrRig.transform.Find("LeftHand Controller/Ray Interactor").GetComponent<XRRayInteractor>();
        var rightRayInteractor = xrRig.transform.Find("RightHand Controller/Ray Interactor").GetComponent<XRRayInteractor>();
        
        leftRayInteractor.interactionLayerMask = interactionLayerMask;
        rightRayInteractor.interactionLayerMask = interactionLayerMask;
        
        // Configure direct interactors
        var leftDirectInteractor = xrRig.transform.Find("LeftHand Controller/Direct Interactor").GetComponent<XRDirectInteractor>();
        var rightDirectInteractor = xrRig.transform.Find("RightHand Controller/Direct Interactor").GetComponent<XRDirectInteractor>();
        
        leftDirectInteractor.interactionLayerMask = interactionLayerMask;
        rightDirectInteractor.interactionLayerMask = interactionLayerMask;
    }
}
```

### Hand Tracking Implementation
```csharp
using UnityEngine;
using UnityEngine.XR.Hands;

public class HandTrackingController : MonoBehaviour
{
    [Header("Hand Tracking Configuration")]
    public XRHandSubsystem handSubsystem;
    public Transform leftHandRoot;
    public Transform rightHandRoot;
    
    [Header("Gesture Recognition")]
    public GestureRecognizer gestureRecognizer;
    public HandPose[] recognizedPoses;
    
    private XRHand leftHand;
    private XRHand rightHand;
    
    private void Start()
    {
        InitializeHandTracking();
    }
    
    private void InitializeHandTracking()
    {
        // Get hand subsystem
        handSubsystem = XRGeneralSettings.Instance.Manager.activeLoader.GetLoadedSubsystem<XRHandSubsystem>();
        
        if (handSubsystem != null)
        {
            handSubsystem.trackingAcquired += OnHandTrackingAcquired;
            handSubsystem.trackingLost += OnHandTrackingLost;
            handSubsystem.updatedHands += OnHandsUpdated;
            
            Debug.Log("Hand tracking initialized");
        }
    }
    
    private void OnHandsUpdated(XRHandSubsystem subsystem, XRHandSubsystem.UpdateSuccessFlags updateSuccessFlags, XRHandSubsystem.UpdateType updateType)
    {
        // Update hand positions and rotations
        if (updateSuccessFlags.HasFlag(XRHandSubsystem.UpdateSuccessFlags.LeftHandRootPose))
        {
            UpdateHandTransform(subsystem.leftHand, leftHandRoot);
        }
        
        if (updateSuccessFlags.HasFlag(XRHandSubsystem.UpdateSuccessFlags.RightHandRootPose))
        {
            UpdateHandTransform(subsystem.rightHand, rightHandRoot);
        }
        
        // Perform gesture recognition
        RecognizeGestures();
    }
    
    private void UpdateHandTransform(XRHand hand, Transform handRoot)
    {
        if (hand.rootPose.TryGetPosition(out Vector3 position))
        {
            handRoot.position = position;
        }
        
        if (hand.rootPose.TryGetRotation(out Quaternion rotation))
        {
            handRoot.rotation = rotation;
        }
        
        // Update individual finger joints
        UpdateFingerJoints(hand, handRoot);
    }
    
    private void RecognizeGestures()
    {
        // Check for predefined gestures
        foreach (var pose in recognizedPoses)
        {
            if (IsGestureMatch(leftHand, pose))
            {
                OnGestureRecognized(pose, HandType.Left);
            }
            
            if (IsGestureMatch(rightHand, pose))
            {
                OnGestureRecognized(pose, HandType.Right);
            }
        }
    }
    
    private void OnGestureRecognized(HandPose pose, HandType handType)
    {
        Debug.Log($"Gesture recognized: {pose.name} on {handType} hand");
        
        // Execute gesture-specific actions
        ExecuteGestureAction(pose, handType);
    }
}
```

### AR Foundation Integration
```csharp
using UnityEngine;
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.ARSubsystems;

public class ARManager : MonoBehaviour
{
    [Header("AR Configuration")]
    public ARCamera arCamera;
    public ARPlaneManager planeManager;
    public AROcclusionManager occlusionManager;
    public ARRaycastManager raycastManager;
    
    [Header("Placement")]
    public GameObject placementPrefab;
    private List<ARRaycastHit> raycastHits = new List<ARRaycastHit>();
    
    private void Start()
    {
        InitializeAR();
    }
    
    private void InitializeAR()
    {
        // Enable plane detection
        planeManager.enabled = true;
        planeManager.requestedDetectionMode = PlaneDetectionMode.Horizontal | PlaneDetectionMode.Vertical;
        
        // Configure occlusion
        if (occlusionManager != null)
        {
            occlusionManager.requestedHumanDepthMode = HumanDepthMode.Best;
            occlusionManager.requestedHumanStencilMode = HumanStencilMode.Best;
        }
        
        // Setup plane events
        planeManager.planesChanged += OnPlanesChanged;
        
        Debug.Log("AR Foundation initialized");
    }
    
    private void Update()
    {
        HandleTouchInput();
    }
    
    private void HandleTouchInput()
    {
        if (Input.touchCount > 0)
        {
            Touch touch = Input.GetTouch(0);
            
            if (touch.phase == TouchPhase.Began)
            {
                // Perform raycast to detect planes
                if (raycastManager.Raycast(touch.position, raycastHits, TrackableType.PlaneWithinPolygon))
                {
                    Pose hitPose = raycastHits[0].pose;
                    PlaceObject(hitPose.position, hitPose.rotation);
                }
            }
        }
    }
    
    private void PlaceObject(Vector3 position, Quaternion rotation)
    {
        if (placementPrefab != null)
        {
            GameObject placedObject = Instantiate(placementPrefab, position, rotation);
            
            // Add AR interaction components
            var arObject = placedObject.AddComponent<ARPlacedObject>();
            arObject.Initialize(position, rotation);
            
            Debug.Log($"Object placed at: {position}");
        }
    }
    
    private void OnPlanesChanged(ARPlanesChangedEventArgs eventArgs)
    {
        // Handle new planes
        foreach (var plane in eventArgs.added)
        {
            Debug.Log($"New plane detected: {plane.trackableId}");
            ConfigurePlaneVisualization(plane);
        }
        
        // Handle updated planes
        foreach (var plane in eventArgs.updated)
        {
            UpdatePlaneVisualization(plane);
        }
        
        // Handle removed planes
        foreach (var plane in eventArgs.removed)
        {
            Debug.Log($"Plane removed: {plane.trackableId}");
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities
- Generate XR interaction patterns and UI designs
- Create automated spatial mapping optimization
- AI-assisted gesture recognition training
- Machine learning for object occlusion and tracking

## 💡 Key Highlights
- **Use Unity XR Toolkit for cross-platform XR development**
- **Implement proper hand tracking and gesture recognition**
- **Optimize rendering for XR performance requirements**
- **Test extensively on target XR devices**