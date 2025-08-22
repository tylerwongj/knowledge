# @f-Advanced-Unity-XR-Development-Architecture

## 🎯 Learning Objectives

- Master Unity XR Toolkit for cross-platform VR/AR development
- Implement advanced interaction systems with hand tracking and eye tracking
- Create performance-optimized XR applications for mobile and standalone devices
- Design immersive user experiences with spatial computing principles

## 🔧 Core XR Architecture Framework

### Universal XR Foundation System

```csharp
using UnityEngine;
using UnityEngine.XR;
using UnityEngine.XR.Interaction.Toolkit;
using System;
using System.Collections.Generic;

// Universal XR manager supporting multiple platforms
public class UniversalXRManager : MonoBehaviour
{
    [Header("XR Configuration")]
    [SerializeField] private XRPlatform targetPlatform = XRPlatform.Auto;
    [SerializeField] private bool enableHandTracking = true;
    [SerializeField] private bool enableEyeTracking = false;
    [SerializeField] private bool enablePassthrough = false;
    
    [Header("Performance Settings")]
    [SerializeField] private int targetFrameRate = 90;
    [SerializeField] private float renderScale = 1.0f;
    [SerializeField] private bool enableFixedFoveatedRendering = true;
    
    // XR System References
    private XRRig xrRig;
    private Camera xrCamera;
    private XRHandTrackingManager handTrackingManager;
    private XREyeTrackingManager eyeTrackingManager;
    private XRPassthroughManager passthroughManager;
    
    // Events
    public event Action<XRPlatform> OnXRInitialized;
    public event Action<string> OnXRError;
    public event Action<bool> OnTrackingStatusChanged;
    
    public enum XRPlatform
    {
        Auto,
        OculusQuest,
        PICO,
        HTC_Vive,
        iOS_ARKit,
        Android_ARCore,
        HoloLens,
        MagicLeap
    }
    
    void Start()
    {
        InitializeXRSystem();
    }
    
    private async void InitializeXRSystem()
    {
        try
        {
            // Detect platform if set to auto
            if (targetPlatform == XRPlatform.Auto)
            {
                targetPlatform = DetectXRPlatform();
            }
            
            // Initialize XR subsystems
            await InitializeSubsystems();
            
            // Setup XR rig
            SetupXRRig();
            
            // Configure platform-specific settings
            ConfigurePlatformSettings();
            
            // Start tracking
            await StartXRTracking();
            
            OnXRInitialized?.Invoke(targetPlatform);
            Debug.Log($"XR System initialized for platform: {targetPlatform}");
        }
        catch (Exception ex)
        {
            OnXRError?.Invoke($"XR Initialization failed: {ex.Message}");
            Debug.LogError($"XR Initialization Error: {ex}");
        }
    }
    
    private XRPlatform DetectXRPlatform()
    {
        // Platform detection logic
        string deviceModel = SystemInfo.deviceModel.ToLower();
        
        if (deviceModel.Contains("quest"))
            return XRPlatform.OculusQuest;
        else if (deviceModel.Contains("pico"))
            return XRPlatform.PICO;
        else if (Application.platform == RuntimePlatform.IPhonePlayer)
            return XRPlatform.iOS_ARKit;
        else if (Application.platform == RuntimePlatform.Android)
            return XRPlatform.Android_ARCore;
        else if (deviceModel.Contains("hololens"))
            return XRPlatform.HoloLens;
        
        return XRPlatform.OculusQuest; // Default fallback
    }
    
    private async System.Threading.Tasks.Task InitializeSubsystems()
    {
        // Initialize XR display subsystem
        var displaySubsystems = new List<XRDisplaySubsystem>();
        SubsystemManager.GetInstances(displaySubsystems);
        
        if (displaySubsystems.Count > 0)
        {
            displaySubsystems[0].Start();
        }
        
        // Initialize input subsystem
        var inputSubsystems = new List<XRInputSubsystem>();
        SubsystemManager.GetInstances(inputSubsystems);
        
        if (inputSubsystems.Count > 0)
        {
            inputSubsystems[0].Start();
        }
        
        // Platform-specific subsystem initialization
        await InitializePlatformSubsystems();
    }
    
    private async System.Threading.Tasks.Task InitializePlatformSubsystems()
    {
        switch (targetPlatform)
        {
            case XRPlatform.OculusQuest:
                await InitializeOculusSubsystems();
                break;
            case XRPlatform.iOS_ARKit:
                await InitializeARKitSubsystems();
                break;
            case XRPlatform.Android_ARCore:
                await InitializeARCoreSubsystems();
                break;
            case XRPlatform.HoloLens:
                await InitializeHoloLensSubsystems();
                break;
        }
    }
    
    private async System.Threading.Tasks.Task InitializeOculusSubsystems()
    {
        // Oculus-specific initialization
        if (enableHandTracking)
        {
            handTrackingManager = gameObject.AddComponent<XRHandTrackingManager>();
            await handTrackingManager.Initialize();
        }
        
        if (enableEyeTracking)
        {
            eyeTrackingManager = gameObject.AddComponent<XREyeTrackingManager>();
            await eyeTrackingManager.Initialize();
        }
        
        if (enablePassthrough)
        {
            passthroughManager = gameObject.AddComponent<XRPassthroughManager>();
            await passthroughManager.Initialize();
        }
    }
    
    private async System.Threading.Tasks.Task InitializeARKitSubsystems()
    {
        // ARKit-specific initialization
        // Implementation would include ARKit subsystem setup
        await System.Threading.Tasks.Task.Delay(100); // Placeholder
    }
    
    private async System.Threading.Tasks.Task InitializeARCoreSubsystems()
    {
        // ARCore-specific initialization
        await System.Threading.Tasks.Task.Delay(100); // Placeholder
    }
    
    private async System.Threading.Tasks.Task InitializeHoloLensSubsystems()
    {
        // HoloLens-specific initialization
        await System.Threading.Tasks.Task.Delay(100); // Placeholder
    }
    
    private void SetupXRRig()
    {
        // Create or find XR Rig
        xrRig = FindObjectOfType<XRRig>();
        if (xrRig == null)
        {
            var xrRigGO = new GameObject("XR Rig");
            xrRig = xrRigGO.AddComponent<XRRig>();
        }
        
        // Setup camera
        xrCamera = xrRig.cameraGameObject.GetComponent<Camera>();
        if (xrCamera == null)
        {
            xrCamera = xrRig.cameraGameObject.AddComponent<Camera>();
        }
        
        // Configure camera for XR
        ConfigureXRCamera();
        
        // Setup interaction system
        SetupInteractionSystem();
    }
    
    private void ConfigureXRCamera()
    {
        xrCamera.nearClipPlane = 0.01f;
        xrCamera.farClipPlane = 1000f;
        
        // Platform-specific camera configuration
        switch (targetPlatform)
        {
            case XRPlatform.OculusQuest:
            case XRPlatform.PICO:
                xrCamera.fieldOfView = 90f;
                break;
            case XRPlatform.iOS_ARKit:
            case XRPlatform.Android_ARCore:
                xrCamera.fieldOfView = 60f;
                break;
            case XRPlatform.HoloLens:
                xrCamera.fieldOfView = 45f;
                break;
        }
    }
    
    private void SetupInteractionSystem()
    {
        // Add XR Interaction Manager
        var interactionManager = FindObjectOfType<XRInteractionManager>();
        if (interactionManager == null)
        {
            var managerGO = new GameObject("XR Interaction Manager");
            interactionManager = managerGO.AddComponent<XRInteractionManager>();
        }
        
        // Setup controllers based on platform
        SetupControllers();
    }
    
    private void SetupControllers()
    {
        switch (targetPlatform)
        {
            case XRPlatform.OculusQuest:
            case XRPlatform.PICO:
                SetupVRControllers();
                break;
            case XRPlatform.iOS_ARKit:
            case XRPlatform.Android_ARCore:
                SetupARTouchController();
                break;
            case XRPlatform.HoloLens:
                SetupHoloLensGestureController();
                break;
        }
    }
    
    private void SetupVRControllers()
    {
        // Left controller
        var leftController = CreateController("LeftHand Controller", XRNode.LeftHand);
        
        // Right controller
        var rightController = CreateController("RightHand Controller", XRNode.RightHand);
        
        // Add hand tracking if enabled
        if (enableHandTracking && handTrackingManager != null)
        {
            leftController.gameObject.AddComponent<HandTrackingController>();
            rightController.gameObject.AddComponent<HandTrackingController>();
        }
    }
    
    private XRController CreateController(string name, XRNode node)
    {
        var controllerGO = new GameObject(name);
        controllerGO.transform.SetParent(xrRig.transform);
        
        var controller = controllerGO.AddComponent<XRController>();
        controller.controllerNode = node;
        
        // Add ray interactor
        var rayInteractor = controllerGO.AddComponent<XRRayInteractor>();
        rayInteractor.raycastMask = -1;
        rayInteractor.raycastTriggerInteraction = QueryTriggerInteraction.Ignore;
        
        // Add direct interactor
        var directInteractor = controllerGO.AddComponent<XRDirectInteractor>();
        
        // Add line renderer for ray visualization
        var lineRenderer = controllerGO.AddComponent<LineRenderer>();
        rayInteractor.lineRenderer = lineRenderer;
        
        return controller;
    }
    
    private void SetupARTouchController()
    {
        var touchController = new GameObject("AR Touch Controller");
        touchController.transform.SetParent(xrRig.transform);
        touchController.AddComponent<ARTouchController>();
    }
    
    private void SetupHoloLensGestureController()
    {
        var gestureController = new GameObject("HoloLens Gesture Controller");
        gestureController.transform.SetParent(xrRig.transform);
        gestureController.AddComponent<HoloLensGestureController>();
    }
    
    private void ConfigurePlatformSettings()
    {
        // Set target frame rate
        Application.targetFrameRate = targetFrameRate;
        
        // Configure render scale
        UnityEngine.XR.XRSettings.renderViewportScale = renderScale;
        
        // Platform-specific optimizations
        switch (targetPlatform)
        {
            case XRPlatform.OculusQuest:
                ConfigureQuestSettings();
                break;
            case XRPlatform.iOS_ARKit:
                ConfigureARKitSettings();
                break;
            case XRPlatform.Android_ARCore:
                ConfigureARCoreSettings();
                break;
        }
    }
    
    private void ConfigureQuestSettings()
    {
        // Quest-specific optimizations
        QualitySettings.shadowDistance = 50f;
        QualitySettings.shadows = ShadowQuality.HardOnly;
        
        if (enableFixedFoveatedRendering)
        {
            // Enable foveated rendering for Quest
            // This would use Oculus SDK specific calls
        }
    }
    
    private void ConfigureARKitSettings()
    {
        // ARKit-specific settings
        Screen.sleepTimeout = SleepTimeout.NeverSleep;
    }
    
    private void ConfigureARCoreSettings()
    {
        // ARCore-specific settings
        Screen.sleepTimeout = SleepTimeout.NeverSleep;
    }
    
    private async System.Threading.Tasks.Task StartXRTracking()
    {
        // Start position tracking
        var trackingOrigin = xrRig.GetComponent<XRRig>();
        if (trackingOrigin != null)
        {
            trackingOrigin.requestedTrackingOriginMode = TrackingOriginModeFlags.Floor;
        }
        
        // Platform-specific tracking setup
        switch (targetPlatform)
        {
            case XRPlatform.iOS_ARKit:
            case XRPlatform.Android_ARCore:
                await StartARTracking();
                break;
        }
    }
    
    private async System.Threading.Tasks.Task StartARTracking()
    {
        // Start AR session
        // This would integrate with AR Foundation
        await System.Threading.Tasks.Task.Delay(500); // Simulate initialization
    }
    
    // Public API
    public bool IsXRActive => XRSettings.isDeviceActive;
    public XRPlatform CurrentPlatform => targetPlatform;
    public Camera XRCamera => xrCamera;
    public XRRig XRRig => xrRig;
    
    public void SetRenderScale(float scale)
    {
        renderScale = Mathf.Clamp(scale, 0.1f, 2.0f);
        UnityEngine.XR.XRSettings.renderViewportScale = renderScale;
    }
    
    public void TogglePassthrough(bool enable)
    {
        if (passthroughManager != null)
        {
            passthroughManager.SetPassthroughEnabled(enable);
        }
    }
}

// Hand tracking manager component
public class XRHandTrackingManager : MonoBehaviour
{
    [Header("Hand Tracking Settings")]
    [SerializeField] private bool trackFingers = true;
    [SerializeField] private float trackingConfidenceThreshold = 0.7f;
    
    private Dictionary<XRNode, HandTrackingData> handData = new Dictionary<XRNode, HandTrackingData>();
    
    public event Action<XRNode, HandTrackingData> OnHandDataUpdated;
    
    public async System.Threading.Tasks.Task Initialize()
    {
        // Initialize hand tracking subsystem
        handData[XRNode.LeftHand] = new HandTrackingData();
        handData[XRNode.RightHand] = new HandTrackingData();
        
        // Start tracking
        InvokeRepeating(nameof(UpdateHandTracking), 0f, 1f/60f); // 60 FPS tracking
        
        await System.Threading.Tasks.Task.CompletedTask;
    }
    
    private void UpdateHandTracking()
    {
        UpdateSingleHand(XRNode.LeftHand);
        UpdateSingleHand(XRNode.RightHand);
    }
    
    private void UpdateSingleHand(XRNode handNode)
    {
        var hand = handData[handNode];
        
        // Get hand position and rotation
        if (InputDevices.GetDeviceAtXRNode(handNode).TryGetFeatureValue(CommonUsages.devicePosition, out hand.position) &&
            InputDevices.GetDeviceAtXRNode(handNode).TryGetFeatureValue(CommonUsages.deviceRotation, out hand.rotation))
        {
            hand.isTracked = true;
            hand.confidence = UnityEngine.Random.Range(0.8f, 1.0f); // Placeholder
            
            // Update finger tracking if enabled
            if (trackFingers)
            {
                UpdateFingerTracking(handNode, hand);
            }
            
            OnHandDataUpdated?.Invoke(handNode, hand);
        }
        else
        {
            hand.isTracked = false;
            hand.confidence = 0f;
        }
        
        handData[handNode] = hand;
    }
    
    private void UpdateFingerTracking(XRNode handNode, HandTrackingData hand)
    {
        // Finger tracking implementation would go here
        // This is a simplified version
        hand.fingers = new FingerData[5];
        
        for (int i = 0; i < 5; i++)
        {
            hand.fingers[i] = new FingerData
            {
                isExtended = UnityEngine.Random.value > 0.5f,
                confidence = UnityEngine.Random.Range(0.7f, 1.0f)
            };
        }
    }
    
    public HandTrackingData GetHandData(XRNode handNode)
    {
        return handData.ContainsKey(handNode) ? handData[handNode] : default;
    }
    
    public bool IsHandTracked(XRNode handNode)
    {
        return handData.ContainsKey(handNode) && handData[handNode].isTracked;
    }
}

[System.Serializable]
public struct HandTrackingData
{
    public bool isTracked;
    public float confidence;
    public Vector3 position;
    public Quaternion rotation;
    public FingerData[] fingers;
}

[System.Serializable]
public struct FingerData
{
    public bool isExtended;
    public float confidence;
    public Vector3[] jointPositions;
}

// Eye tracking manager
public class XREyeTrackingManager : MonoBehaviour
{
    [Header("Eye Tracking Settings")]
    [SerializeField] private float gazeSmoothingFactor = 0.1f;
    [SerializeField] private float maxGazeDistance = 10f;
    
    private Vector3 gazeDirection;
    private Vector3 gazeOrigin;
    private bool isTrackingActive;
    private Vector3 smoothedGazeDirection;
    
    public event Action<Vector3, Vector3> OnGazeUpdated;
    public event Action<GameObject> OnGazeEnter;
    public event Action<GameObject> OnGazeExit;
    
    private GameObject currentGazeTarget;
    
    public async System.Threading.Tasks.Task Initialize()
    {
        // Initialize eye tracking
        isTrackingActive = true;
        InvokeRepeating(nameof(UpdateEyeTracking), 0f, 1f/120f); // High frequency for smooth gaze
        
        await System.Threading.Tasks.Task.CompletedTask;
    }
    
    private void UpdateEyeTracking()
    {
        if (!isTrackingActive) return;
        
        // Get eye tracking data (platform specific implementation)
        if (GetEyeTrackingData(out gazeOrigin, out gazeDirection))
        {
            // Smooth gaze direction
            smoothedGazeDirection = Vector3.Lerp(smoothedGazeDirection, gazeDirection, gazeSmoothingFactor);
            
            // Perform gaze raycast
            PerformGazeRaycast();
            
            OnGazeUpdated?.Invoke(gazeOrigin, smoothedGazeDirection);
        }
    }
    
    private bool GetEyeTrackingData(out Vector3 origin, out Vector3 direction)
    {
        // Platform-specific eye tracking data retrieval
        // This would integrate with the actual eye tracking SDK
        
        origin = Camera.main.transform.position;
        direction = Camera.main.transform.forward + new Vector3(
            UnityEngine.Random.Range(-0.1f, 0.1f),
            UnityEngine.Random.Range(-0.1f, 0.1f),
            0
        );
        
        return true; // Placeholder
    }
    
    private void PerformGazeRaycast()
    {
        if (Physics.Raycast(gazeOrigin, smoothedGazeDirection, out RaycastHit hit, maxGazeDistance))
        {
            if (currentGazeTarget != hit.collider.gameObject)
            {
                // Gaze exit previous target
                if (currentGazeTarget != null)
                {
                    OnGazeExit?.Invoke(currentGazeTarget);
                }
                
                // Gaze enter new target
                currentGazeTarget = hit.collider.gameObject;
                OnGazeEnter?.Invoke(currentGazeTarget);
            }
        }
        else
        {
            // No gaze target
            if (currentGazeTarget != null)
            {
                OnGazeExit?.Invoke(currentGazeTarget);
                currentGazeTarget = null;
            }
        }
    }
    
    public Vector3 GazeDirection => smoothedGazeDirection;
    public Vector3 GazeOrigin => gazeOrigin;
    public bool IsActive => isTrackingActive;
    public GameObject CurrentGazeTarget => currentGazeTarget;
}

// Passthrough manager for mixed reality
public class XRPassthroughManager : MonoBehaviour
{
    [Header("Passthrough Settings")]
    [SerializeField] private float passthroughOpacity = 0.8f;
    [SerializeField] private bool enableColorPassthrough = true;
    
    private bool isPassthroughActive;
    
    public event Action<bool> OnPassthroughStatusChanged;
    
    public async System.Threading.Tasks.Task Initialize()
    {
        // Initialize passthrough functionality
        await System.Threading.Tasks.Task.CompletedTask;
    }
    
    public void SetPassthroughEnabled(bool enabled)
    {
        if (isPassthroughActive != enabled)
        {
            isPassthroughActive = enabled;
            
            // Platform-specific passthrough implementation
            ApplyPassthroughSettings();
            
            OnPassthroughStatusChanged?.Invoke(isPassthroughActive);
        }
    }
    
    private void ApplyPassthroughSettings()
    {
        // This would integrate with platform-specific passthrough APIs
        // For example, Oculus Passthrough API, ARCore, ARKit, etc.
        
        if (isPassthroughActive)
        {
            // Enable passthrough
            Debug.Log("Passthrough enabled");
        }
        else
        {
            // Disable passthrough
            Debug.Log("Passthrough disabled");
        }
    }
    
    public void SetPassthroughOpacity(float opacity)
    {
        passthroughOpacity = Mathf.Clamp01(opacity);
        ApplyPassthroughSettings();
    }
    
    public bool IsPassthroughActive => isPassthroughActive;
    public float PassthroughOpacity => passthroughOpacity;
}
```

### Advanced XR Interaction System

```csharp
using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;
using System;
using System.Collections.Generic;

// Advanced grabbable object with physics-based interaction
public class AdvancedXRGrabbable : XRGrabInteractable
{
    [Header("Advanced Grab Settings")]
    [SerializeField] private bool usePhysicsGrab = true;
    [SerializeField] private float grabStrength = 1000f;
    [SerializeField] private float grabDamping = 50f;
    [SerializeField] private bool enableTwoHandedGrab = true;
    [SerializeField] private Transform twoHandedGrabPoint;
    
    [Header("Haptic Feedback")]
    [SerializeField] private float grabHapticIntensity = 0.5f;
    [SerializeField] private float grabHapticDuration = 0.1f;
    
    private Rigidbody objectRigidbody;
    private List<IXRSelectInteractor> currentGrabbers = new List<IXRSelectInteractor>();
    private Vector3 originalVelocity;
    private Vector3 originalAngularVelocity;
    
    // Physics grab variables
    private Joint physicsJoint;
    private bool wasKinematic;
    
    // Two-handed grab
    private bool isTwoHandedGrab;
    private Vector3 twoHandedInitialDistance;
    private Quaternion twoHandedInitialRotation;
    
    public event Action<IXRSelectInteractor> OnAdvancedGrabStart;
    public event Action<IXRSelectInteractor> OnAdvancedGrabEnd;
    public event Action OnTwoHandedGrabStart;
    public event Action OnTwoHandedGrabEnd;
    
    protected override void Awake()
    {
        base.Awake();
        objectRigidbody = GetComponent<Rigidbody>();
        
        if (objectRigidbody == null)
        {
            objectRigidbody = gameObject.AddComponent<Rigidbody>();
        }
    }
    
    protected override void OnSelectEntered(SelectEnterEventArgs args)
    {
        base.OnSelectEntered(args);
        
        currentGrabbers.Add(args.interactorObject);
        
        // Handle physics grab
        if (usePhysicsGrab)
        {
            SetupPhysicsGrab(args.interactorObject);
        }
        
        // Handle two-handed grab
        if (enableTwoHandedGrab && currentGrabbers.Count == 2)
        {
            SetupTwoHandedGrab();
        }
        
        // Haptic feedback
        TriggerHapticFeedback(args.interactorObject);
        
        OnAdvancedGrabStart?.Invoke(args.interactorObject);
    }
    
    protected override void OnSelectExited(SelectExitEventArgs args)
    {
        base.OnSelectExited(args);
        
        currentGrabbers.Remove(args.interactorObject);
        
        // Handle physics grab cleanup
        if (usePhysicsGrab)
        {
            CleanupPhysicsGrab();
        }
        
        // Handle two-handed grab cleanup
        if (isTwoHandedGrab && currentGrabbers.Count < 2)
        {
            CleanupTwoHandedGrab();
        }
        
        OnAdvancedGrabEnd?.Invoke(args.interactorObject);
    }
    
    private void SetupPhysicsGrab(IXRSelectInteractor interactor)
    {
        if (objectRigidbody == null) return;
        
        // Store original physics state
        wasKinematic = objectRigidbody.isKinematic;
        originalVelocity = objectRigidbody.velocity;
        originalAngularVelocity = objectRigidbody.angularVelocity;
        
        // Setup physics joint
        objectRigidbody.isKinematic = false;
        
        var interactorTransform = interactor.transform;
        if (interactorTransform != null)
        {
            var jointGO = new GameObject("PhysicsGrabJoint");
            jointGO.transform.position = interactorTransform.position;
            jointGO.transform.rotation = interactorTransform.rotation;
            
            var jointRB = jointGO.AddComponent<Rigidbody>();
            jointRB.isKinematic = true;
            
            physicsJoint = jointGO.AddComponent<ConfigurableJoint>();
            physicsJoint.connectedBody = objectRigidbody;
            
            // Configure joint for grabbing
            physicsJoint.xMotion = ConfigurableJointMotion.Limited;
            physicsJoint.yMotion = ConfigurableJointMotion.Limited;
            physicsJoint.zMotion = ConfigurableJointMotion.Limited;
            physicsJoint.angularXMotion = ConfigurableJointMotion.Limited;
            physicsJoint.angularYMotion = ConfigurableJointMotion.Limited;
            physicsJoint.angularZMotion = ConfigurableJointMotion.Limited;
            
            var drive = new JointDrive
            {
                positionSpring = grabStrength,
                positionDamper = grabDamping,
                maximumForce = float.MaxValue
            };
            
            physicsJoint.xDrive = drive;
            physicsJoint.yDrive = drive;
            physicsJoint.zDrive = drive;
            physicsJoint.angularXDrive = drive;
            physicsJoint.angularYZDrive = drive;
            
            // Update joint target in follow-up
            StartCoroutine(UpdatePhysicsGrab(interactorTransform, jointRB.transform));
        }
    }
    
    private System.Collections.IEnumerator UpdatePhysicsGrab(Transform interactorTransform, Transform jointTransform)
    {
        while (physicsJoint != null && interactorTransform != null)
        {
            jointTransform.position = interactorTransform.position;
            jointTransform.rotation = interactorTransform.rotation;
            
            yield return new WaitForFixedUpdate();
        }
    }
    
    private void CleanupPhysicsGrab()
    {
        if (physicsJoint != null)
        {
            DestroyImmediate(physicsJoint.gameObject);
            physicsJoint = null;
        }
        
        if (objectRigidbody != null)
        {
            objectRigidbody.isKinematic = wasKinematic;
        }
    }
    
    private void SetupTwoHandedGrab()
    {
        if (currentGrabbers.Count != 2) return;
        
        isTwoHandedGrab = true;
        
        var hand1 = currentGrabbers[0].transform;
        var hand2 = currentGrabbers[1].transform;
        
        twoHandedInitialDistance = hand1.position - hand2.position;
        twoHandedInitialRotation = transform.rotation;
        
        OnTwoHandedGrabStart?.Invoke();
        
        StartCoroutine(UpdateTwoHandedGrab());
    }
    
    private System.Collections.IEnumerator UpdateTwoHandedGrab()
    {
        while (isTwoHandedGrab && currentGrabbers.Count == 2)
        {
            var hand1 = currentGrabbers[0].transform;
            var hand2 = currentGrabbers[1].transform;
            
            // Calculate new scale based on hand distance
            Vector3 currentDistance = hand1.position - hand2.position;
            float scaleRatio = currentDistance.magnitude / twoHandedInitialDistance.magnitude;
            
            // Apply scaling (optional)
            // transform.localScale = Vector3.one * scaleRatio;
            
            // Calculate rotation based on hand orientation
            Vector3 handDirection = (hand2.position - hand1.position).normalized;
            Vector3 initialDirection = twoHandedInitialDistance.normalized;
            
            Quaternion rotationDelta = Quaternion.FromToRotation(initialDirection, handDirection);
            transform.rotation = rotationDelta * twoHandedInitialRotation;
            
            // Position at midpoint
            transform.position = Vector3.Lerp(hand1.position, hand2.position, 0.5f);
            
            yield return null;
        }
    }
    
    private void CleanupTwoHandedGrab()
    {
        isTwoHandedGrab = false;
        OnTwoHandedGrabEnd?.Invoke();
    }
    
    private void TriggerHapticFeedback(IXRSelectInteractor interactor)
    {
        if (interactor is XRBaseControllerInteractor controllerInteractor)
        {
            var controller = controllerInteractor.xrController;
            if (controller != null)
            {
                controller.SendHapticImpulse(grabHapticIntensity, grabHapticDuration);
            }
        }
    }
    
    // Public API
    public bool IsTwoHandedGrab => isTwoHandedGrab;
    public int GrabberCount => currentGrabbers.Count;
    public bool IsPhysicsGrab => usePhysicsGrab && physicsJoint != null;
}

// Advanced UI interaction for XR
public class XRAdvancedUI : MonoBehaviour
{
    [Header("UI Configuration")]
    [SerializeField] private Canvas uiCanvas;
    [SerializeField] private float interactionDistance = 2f;
    [SerializeField] private LayerMask uiLayerMask = -1;
    
    [Header("Visual Feedback")]
    [SerializeField] private GameObject pointerPrefab;
    [SerializeField] private Material hoverMaterial;
    [SerializeField] private Material selectMaterial;
    
    private Camera xrCamera;
    private LineRenderer laserPointer;
    private GameObject currentHoverTarget;
    private GameObject currentSelectTarget;
    
    // Gesture recognition
    private XRHandTrackingManager handTracker;
    private GestureRecognizer gestureRecognizer;
    
    public event Action<GameObject> OnUIElementHover;
    public event Action<GameObject> OnUIElementSelect;
    public event Action<string> OnGestureRecognized;
    
    void Start()
    {
        xrCamera = Camera.main;
        handTracker = FindObjectOfType<XRHandTrackingManager>();
        
        SetupLaserPointer();
        SetupGestureRecognition();
    }
    
    void Update()
    {
        UpdateUIInteraction();
        UpdateGestureRecognition();
    }
    
    private void SetupLaserPointer()
    {
        if (pointerPrefab != null)
        {
            var pointerGO = Instantiate(pointerPrefab);
            laserPointer = pointerGO.GetComponent<LineRenderer>();
            
            if (laserPointer == null)
            {
                laserPointer = pointerGO.AddComponent<LineRenderer>();
                laserPointer.material = new Material(Shader.Find("Unlit/Color"));
                laserPointer.color = Color.red;
                laserPointer.widthMultiplier = 0.01f;
                laserPointer.positionCount = 2;
            }
        }
    }
    
    private void SetupGestureRecognition()
    {
        gestureRecognizer = new GestureRecognizer();
        
        // Define gestures
        gestureRecognizer.AddGesture("Point", IsPointingGesture);
        gestureRecognizer.AddGesture("Pinch", IsPinchGesture);
        gestureRecognizer.AddGesture("Palm", IsPalmGesture);
    }
    
    private void UpdateUIInteraction()
    {
        Vector3 rayOrigin;
        Vector3 rayDirection;
        
        // Determine ray origin and direction based on input method
        if (handTracker != null && handTracker.IsHandTracked(XRNode.RightHand))
        {
            var handData = handTracker.GetHandData(XRNode.RightHand);
            rayOrigin = handData.position;
            rayDirection = handData.rotation * Vector3.forward;
        }
        else
        {
            // Fallback to gaze-based interaction
            rayOrigin = xrCamera.transform.position;
            rayDirection = xrCamera.transform.forward;
        }
        
        // Update laser pointer
        if (laserPointer != null)
        {
            laserPointer.SetPosition(0, rayOrigin);
            laserPointer.SetPosition(1, rayOrigin + rayDirection * interactionDistance);
        }
        
        // Perform UI raycast
        if (Physics.Raycast(rayOrigin, rayDirection, out RaycastHit hit, interactionDistance, uiLayerMask))
        {
            HandleUIHit(hit.collider.gameObject);
        }
        else
        {
            HandleUIHitEnd();
        }
    }
    
    private void HandleUIHit(GameObject hitObject)
    {
        // Handle hover
        if (currentHoverTarget != hitObject)
        {
            if (currentHoverTarget != null)
            {
                // End previous hover
                ApplyUIFeedback(currentHoverTarget, null);
            }
            
            currentHoverTarget = hitObject;
            ApplyUIFeedback(currentHoverTarget, hoverMaterial);
            OnUIElementHover?.Invoke(currentHoverTarget);
        }
        
        // Handle selection based on gesture or controller input
        bool shouldSelect = false;
        
        if (handTracker != null)
        {
            shouldSelect = gestureRecognizer.IsGestureActive("Pinch");
        }
        else
        {
            // Fallback to controller input
            shouldSelect = Input.GetButton("Fire1"); // Or XR controller specific input
        }
        
        if (shouldSelect && currentSelectTarget != hitObject)
        {
            if (currentSelectTarget != null)
            {
                ApplyUIFeedback(currentSelectTarget, hoverMaterial);
            }
            
            currentSelectTarget = hitObject;
            ApplyUIFeedback(currentSelectTarget, selectMaterial);
            OnUIElementSelect?.Invoke(currentSelectTarget);
            
            // Trigger UI element
            TriggerUIElement(currentSelectTarget);
        }
        else if (!shouldSelect && currentSelectTarget != null)
        {
            ApplyUIFeedback(currentSelectTarget, hoverMaterial);
            currentSelectTarget = null;
        }
    }
    
    private void HandleUIHitEnd()
    {
        if (currentHoverTarget != null)
        {
            ApplyUIFeedback(currentHoverTarget, null);
            currentHoverTarget = null;
        }
        
        if (currentSelectTarget != null)
        {
            ApplyUIFeedback(currentSelectTarget, null);
            currentSelectTarget = null;
        }
    }
    
    private void ApplyUIFeedback(GameObject target, Material feedbackMaterial)
    {
        var renderer = target.GetComponent<Renderer>();
        if (renderer != null)
        {
            if (feedbackMaterial != null)
            {
                renderer.material = feedbackMaterial;
            }
            else
            {
                // Restore original material
                // Implementation would restore cached original material
            }
        }
    }
    
    private void TriggerUIElement(GameObject element)
    {
        // Handle different UI element types
        var button = element.GetComponent<UnityEngine.UI.Button>();
        if (button != null)
        {
            button.onClick.Invoke();
        }
        
        var toggle = element.GetComponent<UnityEngine.UI.Toggle>();
        if (toggle != null)
        {
            toggle.isOn = !toggle.isOn;
        }
        
        // Add more UI element types as needed
    }
    
    private void UpdateGestureRecognition()
    {
        if (handTracker == null) return;
        
        // Update gestures for both hands
        gestureRecognizer.UpdateGestures(
            handTracker.GetHandData(XRNode.LeftHand),
            handTracker.GetHandData(XRNode.RightHand)
        );
        
        // Check for recognized gestures
        var recognizedGesture = gestureRecognizer.GetActiveGesture();
        if (!string.IsNullOrEmpty(recognizedGesture))
        {
            OnGestureRecognized?.Invoke(recognizedGesture);
        }
    }
    
    // Gesture recognition methods
    private bool IsPointingGesture(HandTrackingData hand)
    {
        if (!hand.isTracked || hand.fingers == null || hand.fingers.Length < 2) return false;
        
        // Index finger extended, others curled
        return hand.fingers[1].isExtended && 
               !hand.fingers[0].isExtended && 
               !hand.fingers[2].isExtended &&
               !hand.fingers[3].isExtended &&
               !hand.fingers[4].isExtended;
    }
    
    private bool IsPinchGesture(HandTrackingData hand)
    {
        if (!hand.isTracked || hand.fingers == null || hand.fingers.Length < 2) return false;
        
        // Thumb and index finger close together
        return !hand.fingers[0].isExtended && !hand.fingers[1].isExtended;
    }
    
    private bool IsPalmGesture(HandTrackingData hand)
    {
        if (!hand.isTracked || hand.fingers == null) return false;
        
        // All fingers extended
        bool allExtended = true;
        foreach (var finger in hand.fingers)
        {
            if (!finger.isExtended)
            {
                allExtended = false;
                break;
            }
        }
        
        return allExtended;
    }
}

// Gesture recognition system
public class GestureRecognizer
{
    private Dictionary<string, System.Func<HandTrackingData, bool>> gestures = 
        new Dictionary<string, System.Func<HandTrackingData, bool>>();
    
    private Dictionary<string, bool> gestureStates = new Dictionary<string, bool>();
    
    public void AddGesture(string name, System.Func<HandTrackingData, bool> recognitionFunction)
    {
        gestures[name] = recognitionFunction;
        gestureStates[name] = false;
    }
    
    public void UpdateGestures(HandTrackingData leftHand, HandTrackingData rightHand)
    {
        foreach (var gesture in gestures)
        {
            bool isActive = gesture.Value(rightHand) || gesture.Value(leftHand);
            gestureStates[gesture.Key] = isActive;
        }
    }
    
    public bool IsGestureActive(string gestureName)
    {
        return gestureStates.ContainsKey(gestureName) && gestureStates[gestureName];
    }
    
    public string GetActiveGesture()
    {
        foreach (var state in gestureStates)
        {
            if (state.Value)
            {
                return state.Key;
            }
        }
        return null;
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### AI-Powered XR Features

- **Intelligent Scene Understanding**: AI analysis of physical environment for better AR object placement
- **Adaptive UI**: Machine learning to optimize UI layouts based on user behavior and preferences
- **Natural Language Processing**: Voice commands and conversational AI in XR environments
- **Gesture Recognition**: Advanced AI models for more accurate and natural gesture interpretation

### Smart Content Generation

```csharp
// AI-powered content adaptation for XR
public class AIXRContentManager : MonoBehaviour
{
    [Header("AI Configuration")]
    [SerializeField] private string aiServiceEndpoint;
    [SerializeField] private float adaptationThreshold = 0.7f;
    
    // User behavior tracking
    private UserBehaviorData behaviorData = new UserBehaviorData();
    
    public async System.Threading.Tasks.Task<XRContentRecommendation> GetContentRecommendation(
        XREnvironmentData environmentData)
    {
        // Analyze environment and user behavior
        var analysisData = new
        {
            environment = environmentData,
            userBehavior = behaviorData,
            timestamp = System.DateTime.Now
        };
        
        // Call AI service for recommendations
        var recommendation = await CallAIService(analysisData);
        
        return recommendation;
    }
    
    private async System.Threading.Tasks.Task<XRContentRecommendation> CallAIService(object data)
    {
        // AI service integration placeholder
        await System.Threading.Tasks.Task.Delay(500);
        
        return new XRContentRecommendation
        {
            contentType = "InteractiveObject",
            position = Vector3.zero,
            scale = Vector3.one,
            confidence = 0.85f
        };
    }
}

public class UserBehaviorData
{
    public float averageSessionTime;
    public Vector3[] frequentPositions;
    public string[] preferredInteractions;
    public float eyeTrackingAccuracy;
}

public class XREnvironmentData
{
    public Vector3[] detectedSurfaces;
    public float lightingLevel;
    public float roomSize;
    public bool hasObstacles;
}

public class XRContentRecommendation
{
    public string contentType;
    public Vector3 position;
    public Vector3 scale;
    public float confidence;
}
```

## 💡 Key XR Development Principles

### Performance Optimization
- **Frame Rate Priority**: Maintain consistent 90+ FPS for VR comfort
- **Render Optimization**: Use foveated rendering and dynamic resolution scaling
- **Occlusion Culling**: Implement efficient culling for complex scenes
- **LOD Systems**: Dynamic level-of-detail based on user attention and distance

### User Experience Design
- **Comfort Considerations**: Minimize motion sickness with proper locomotion
- **Accessibility**: Support various interaction methods and user capabilities
- **Spatial Design**: Design for 3D space with proper depth and scale cues
- **Intuitive Interactions**: Use familiar real-world metaphors for interactions

### Cross-Platform Development
- **Universal Architecture**: Design systems that work across different XR platforms
- **Input Abstraction**: Create unified input handling for various controllers
- **Performance Scaling**: Adapt quality settings based on device capabilities
- **Testing Strategy**: Comprehensive testing across target platforms and devices

This comprehensive XR development guide provides the foundation for creating immersive, performant, and accessible XR experiences across multiple platforms and devices.