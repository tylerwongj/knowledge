# i_Input-Systems - Unity Input Management & Controls

## 🎯 Learning Objectives
- Master Unity's Input System (new) and legacy Input Manager
- Implement cross-platform input handling (keyboard, mouse, gamepad, touch)
- Create flexible control schemes and input remapping
- Handle input events and player actions efficiently

## 🔧 Core Input System Components

### New Input System Setup
```csharp
// Input Actions asset-based approach
using UnityEngine;
using UnityEngine.InputSystem;

[CreateAssetMenu(fileName = "PlayerInputActions", menuName = "Input/Player Input Actions")]
public class PlayerInputActions : ScriptableObject, IInputActionCollection
{
    // Auto-generated from Input Actions asset
    public InputActionAsset inputActions;
    
    public InputActionMap playerMap => inputActions.FindActionMap("Player");
    public InputAction moveAction => playerMap.FindAction("Move");
    public InputAction jumpAction => playerMap.FindAction("Jump");
    public InputAction lookAction => playerMap.FindAction("Look");
    public InputAction fireAction => playerMap.FindAction("Fire");
    
    public IEnumerator<InputAction> GetEnumerator()
    {
        return inputActions.GetEnumerator();
    }
    
    IEnumerator IEnumerable.GetEnumerator()
    {
        return GetEnumerator();
    }
}

// Player input controller
public class PlayerInputController : MonoBehaviour
{
    [Header("Input Actions")]
    public PlayerInputActions inputActions;
    
    [Header("Movement Settings")]
    public float moveSpeed = 5f;
    public float lookSensitivity = 2f;
    
    private Vector2 moveInput;
    private Vector2 lookInput;
    private bool jumpPressed;
    private bool firePressed;
    
    private CharacterController characterController;
    private Camera playerCamera;
    
    void Awake()
    {
        characterController = GetComponent<CharacterController>();
        playerCamera = Camera.main;
        
        // Enable input actions
        inputActions.Enable();
        
        // Subscribe to input events
        inputActions.moveAction.performed += OnMove;
        inputActions.moveAction.canceled += OnMove;
        
        inputActions.lookAction.performed += OnLook;
        inputActions.lookAction.canceled += OnLook;
        
        inputActions.jumpAction.performed += OnJump;
        inputActions.fireAction.performed += OnFire;
    }
    
    void OnDestroy()
    {
        // Unsubscribe from events
        inputActions.moveAction.performed -= OnMove;
        inputActions.moveAction.canceled -= OnMove;
        inputActions.lookAction.performed -= OnLook;
        inputActions.lookAction.canceled -= OnLook;
        inputActions.jumpAction.performed -= OnJump;
        inputActions.fireAction.performed -= OnFire;
        
        inputActions.Disable();
    }
    
    void OnMove(InputAction.CallbackContext context)
    {
        moveInput = context.ReadValue<Vector2>();
    }
    
    void OnLook(InputAction.CallbackContext context)
    {
        lookInput = context.ReadValue<Vector2>();
    }
    
    void OnJump(InputAction.CallbackContext context)
    {
        jumpPressed = true;
    }
    
    void OnFire(InputAction.CallbackContext context)
    {
        firePressed = true;
    }
    
    void Update()
    {
        HandleMovement();
        HandleLook();
        HandleActions();
    }
    
    void HandleMovement()
    {
        Vector3 movement = transform.right * moveInput.x + transform.forward * moveInput.y;
        characterController.Move(movement * moveSpeed * Time.deltaTime);
    }
    
    void HandleLook()
    {
        if (lookInput != Vector2.zero)
        {
            float mouseX = lookInput.x * lookSensitivity;
            float mouseY = lookInput.y * lookSensitivity;
            
            transform.Rotate(Vector3.up * mouseX);
            playerCamera.transform.Rotate(Vector3.left * mouseY);
        }
    }
    
    void HandleActions()
    {
        if (jumpPressed)
        {
            // Handle jump logic
            Debug.Log("Jump!");
            jumpPressed = false;
        }
        
        if (firePressed)
        {
            // Handle fire logic
            Debug.Log("Fire!");
            firePressed = false;
        }
    }
}
```

### Legacy Input System
```csharp
// Legacy Input Manager approach
public class LegacyInputController : MonoBehaviour
{
    [Header("Input Settings")]
    public KeyCode jumpKey = KeyCode.Space;
    public KeyCode fireKey = KeyCode.Mouse0;
    
    [Header("Sensitivity")]
    public float mouseSensitivity = 2f;
    public float moveSpeed = 5f;
    
    private CharacterController characterController;
    private Camera playerCamera;
    private float verticalLookRotation = 0f;
    
    void Start()
    {
        characterController = GetComponent<CharacterController>();
        playerCamera = Camera.main;
        
        // Lock cursor for FPS controls
        Cursor.lockState = CursorLockMode.Locked;
    }
    
    void Update()
    {
        HandleMovementInput();
        HandleMouseLook();
        HandleActionInput();
    }
    
    void HandleMovementInput()
    {
        // WASD movement
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");
        
        Vector3 movement = transform.right * horizontal + transform.forward * vertical;
        characterController.Move(movement * moveSpeed * Time.deltaTime);
    }
    
    void HandleMouseLook()
    {
        // Mouse look
        float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity;
        float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity;
        
        // Horizontal rotation (Y-axis)
        transform.Rotate(Vector3.up * mouseX);
        
        // Vertical rotation (X-axis) with clamping
        verticalLookRotation -= mouseY;
        verticalLookRotation = Mathf.Clamp(verticalLookRotation, -90f, 90f);
        playerCamera.transform.localRotation = Quaternion.Euler(verticalLookRotation, 0f, 0f);
    }
    
    void HandleActionInput()
    {
        // Jump input
        if (Input.GetKeyDown(jumpKey))
        {
            // Handle jump
            Debug.Log("Jump!");
        }
        
        // Fire input
        if (Input.GetKeyDown(fireKey))
        {
            // Handle fire
            Debug.Log("Fire!");
        }
        
        // Alternative input checking
        if (Input.GetButtonDown("Fire1"))
        {
            Debug.Log("Fire1 button pressed!");
        }
    }
}
```

### Mobile Touch Input
```csharp
// Touch input handling
public class TouchInputController : MonoBehaviour
{
    [Header("Touch Settings")]
    public float touchSensitivity = 2f;
    public float deadZone = 50f;
    
    [Header("Virtual Controls")]
    public RectTransform leftJoystick;
    public RectTransform rightJoystick;
    public Button jumpButton;
    public Button fireButton;
    
    private Vector2 leftJoystickInput;
    private Vector2 rightJoystickInput;
    
    void Start()
    {
        // Setup button events
        jumpButton.onClick.AddListener(OnJumpPressed);
        fireButton.onClick.AddListener(OnFirePressed);
    }
    
    void Update()
    {
        HandleTouchInput();
        HandleVirtualJoysticks();
    }
    
    void HandleTouchInput()
    {
        // Multi-touch support
        for (int i = 0; i < Input.touchCount; i++)
        {
            Touch touch = Input.GetTouch(i);
            
            switch (touch.phase)
            {
                case TouchPhase.Began:
                    OnTouchBegan(touch);
                    break;
                    
                case TouchPhase.Moved:
                    OnTouchMoved(touch);
                    break;
                    
                case TouchPhase.Ended:
                case TouchPhase.Canceled:
                    OnTouchEnded(touch);
                    break;
            }
        }
    }
    
    void OnTouchBegan(Touch touch)
    {
        // Handle touch start
        Debug.Log($"Touch began at: {touch.position}");
    }
    
    void OnTouchMoved(Touch touch)
    {
        // Handle touch movement (camera look, etc.)
        Vector2 deltaPosition = touch.deltaPosition;
        
        // Apply camera rotation based on touch delta
        if (deltaPosition.magnitude > deadZone)
        {
            float rotationX = deltaPosition.x * touchSensitivity * Time.deltaTime;
            float rotationY = deltaPosition.y * touchSensitivity * Time.deltaTime;
            
            transform.Rotate(Vector3.up * rotationX);
            Camera.main.transform.Rotate(Vector3.left * rotationY);
        }
    }
    
    void OnTouchEnded(Touch touch)
    {
        // Handle touch end
        Debug.Log($"Touch ended at: {touch.position}");
    }
    
    void HandleVirtualJoysticks()
    {
        // Process virtual joystick input
        HandleMovement(leftJoystickInput);
        HandleLook(rightJoystickInput);
    }
    
    void HandleMovement(Vector2 input)
    {
        if (input.magnitude > 0.1f)
        {
            Vector3 movement = transform.right * input.x + transform.forward * input.y;
            GetComponent<CharacterController>().Move(movement * 5f * Time.deltaTime);
        }
    }
    
    void HandleLook(Vector2 input)
    {
        if (input.magnitude > 0.1f)
        {
            transform.Rotate(Vector3.up * input.x * touchSensitivity * Time.deltaTime);
            Camera.main.transform.Rotate(Vector3.left * input.y * touchSensitivity * Time.deltaTime);
        }
    }
    
    void OnJumpPressed()
    {
        Debug.Log("Jump button pressed!");
    }
    
    void OnFirePressed()
    {
        Debug.Log("Fire button pressed!");
    }
}
```

### Input Remapping System
```csharp
// Key remapping system
[System.Serializable]
public class InputBinding
{
    public string actionName;
    public KeyCode primaryKey;
    public KeyCode secondaryKey;
    public string gamepadButton;
}

public class InputRemappingSystem : MonoBehaviour
{
    [Header("Input Bindings")]
    public InputBinding[] inputBindings;
    
    private Dictionary<string, InputBinding> bindingMap = new Dictionary<string, InputBinding>();
    
    void Start()
    {
        LoadInputBindings();
        InitializeBindingMap();
    }
    
    void InitializeBindingMap()
    {
        foreach (var binding in inputBindings)
        {
            bindingMap[binding.actionName] = binding;
        }
    }
    
    public bool GetActionPressed(string actionName)
    {
        if (bindingMap.ContainsKey(actionName))
        {
            var binding = bindingMap[actionName];
            return Input.GetKeyDown(binding.primaryKey) || 
                   Input.GetKeyDown(binding.secondaryKey);
        }
        return false;
    }
    
    public bool GetActionHeld(string actionName)
    {
        if (bindingMap.ContainsKey(actionName))
        {
            var binding = bindingMap[actionName];
            return Input.GetKey(binding.primaryKey) || 
                   Input.GetKey(binding.secondaryKey);
        }
        return false;
    }
    
    public void RemapKey(string actionName, KeyCode newKey, bool isPrimary = true)
    {
        if (bindingMap.ContainsKey(actionName))
        {
            if (isPrimary)
                bindingMap[actionName].primaryKey = newKey;
            else
                bindingMap[actionName].secondaryKey = newKey;
                
            SaveInputBindings();
        }
    }
    
    void SaveInputBindings()
    {
        foreach (var binding in inputBindings)
        {
            PlayerPrefs.SetInt($"{binding.actionName}_Primary", (int)binding.primaryKey);
            PlayerPrefs.SetInt($"{binding.actionName}_Secondary", (int)binding.secondaryKey);
        }
        PlayerPrefs.Save();
    }
    
    void LoadInputBindings()
    {
        foreach (var binding in inputBindings)
        {
            if (PlayerPrefs.HasKey($"{binding.actionName}_Primary"))
            {
                binding.primaryKey = (KeyCode)PlayerPrefs.GetInt($"{binding.actionName}_Primary");
                binding.secondaryKey = (KeyCode)PlayerPrefs.GetInt($"{binding.actionName}_Secondary");
            }
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Input System Architecture
```
Prompt: "Create a Unity input system for [game type] supporting [platforms]. Include keyboard/mouse, gamepad, and touch controls with input remapping and cross-platform compatibility."

Example: "Create a Unity input system for a 3D platformer supporting PC, console, and mobile. Include character movement, camera controls, jumping, and special abilities."
```

### Control Scheme Design
```
Prompt: "Design intuitive control schemes for [specific game mechanics] in Unity. Consider accessibility, different input devices, and user preferences with code implementation."
```

### Input Event Architecture
```
Prompt: "Create an event-driven input system in Unity that decouples input detection from game logic. Include action mapping, input buffering, and combo detection."
```

## 🔧 Advanced Input Features

### Input Buffering System
```csharp
// Input buffer for precise timing
public class InputBuffer : MonoBehaviour
{
    [System.Serializable]
    public class BufferedInput
    {
        public string actionName;
        public float timestamp;
        public bool consumed;
        
        public BufferedInput(string action, float time)
        {
            actionName = action;
            timestamp = time;
            consumed = false;
        }
    }
    
    [Header("Buffer Settings")]
    public float bufferWindow = 0.2f; // Buffer window in seconds
    public int maxBufferSize = 10;
    
    private List<BufferedInput> inputBuffer = new List<BufferedInput>();
    
    public void BufferInput(string actionName)
    {
        // Add input to buffer
        inputBuffer.Add(new BufferedInput(actionName, Time.time));
        
        // Clean old inputs
        CleanBuffer();
        
        // Limit buffer size
        if (inputBuffer.Count > maxBufferSize)
        {
            inputBuffer.RemoveAt(0);
        }
    }
    
    public bool ConsumeBufferedInput(string actionName, float maxAge = -1f)
    {
        if (maxAge < 0) maxAge = bufferWindow;
        
        for (int i = inputBuffer.Count - 1; i >= 0; i--)
        {
            var bufferedInput = inputBuffer[i];
            
            if (!bufferedInput.consumed && 
                bufferedInput.actionName == actionName &&
                Time.time - bufferedInput.timestamp <= maxAge)
            {
                bufferedInput.consumed = true;
                return true;
            }
        }
        
        return false;
    }
    
    void CleanBuffer()
    {
        float currentTime = Time.time;
        inputBuffer.RemoveAll(input => 
            input.consumed || 
            currentTime - input.timestamp > bufferWindow);
    }
    
    void Update()
    {
        // Example usage - buffer jump input
        if (Input.GetKeyDown(KeyCode.Space))
        {
            BufferInput("Jump");
        }
    }
}
```

### Gesture Recognition
```csharp
// Simple gesture recognition system
public class GestureRecognizer : MonoBehaviour
{
    [System.Serializable]
    public class Gesture
    {
        public string name;
        public Vector2[] points;
        public float tolerance = 0.3f;
    }
    
    [Header("Gestures")]
    public Gesture[] gestures;
    
    private List<Vector2> currentGesture = new List<Vector2>();
    private bool isRecording = false;
    
    void Update()
    {
        HandleGestureInput();
    }
    
    void HandleGestureInput()
    {
        if (Input.GetMouseButtonDown(0))
        {
            StartGesture();
        }
        else if (Input.GetMouseButton(0) && isRecording)
        {
            ContinueGesture();
        }
        else if (Input.GetMouseButtonUp(0) && isRecording)
        {
            EndGesture();
        }
    }
    
    void StartGesture()
    {
        isRecording = true;
        currentGesture.Clear();
        currentGesture.Add(Input.mousePosition);
    }
    
    void ContinueGesture()
    {
        Vector2 currentPos = Input.mousePosition;
        Vector2 lastPos = currentGesture[currentGesture.Count - 1];
        
        // Only add if moved significantly
        if (Vector2.Distance(currentPos, lastPos) > 10f)
        {
            currentGesture.Add(currentPos);
        }
    }
    
    void EndGesture()
    {
        isRecording = false;
        
        if (currentGesture.Count > 2)
        {
            string recognizedGesture = RecognizeGesture();
            if (!string.IsNullOrEmpty(recognizedGesture))
            {
                OnGestureRecognized(recognizedGesture);
            }
        }
    }
    
    string RecognizeGesture()
    {
        foreach (var gesture in gestures)
        {
            if (CompareGestures(currentGesture, gesture))
            {
                return gesture.name;
            }
        }
        return null;
    }
    
    bool CompareGestures(List<Vector2> input, Gesture template)
    {
        if (input.Count < 2 || template.points.Length < 2)
            return false;
            
        // Normalize both gestures
        var normalizedInput = NormalizeGesture(input);
        var normalizedTemplate = NormalizeGesture(template.points.ToList());
        
        // Compare using simple distance matching
        float totalDistance = 0f;
        int minCount = Mathf.Min(normalizedInput.Count, normalizedTemplate.Count);
        
        for (int i = 0; i < minCount; i++)
        {
            totalDistance += Vector2.Distance(normalizedInput[i], normalizedTemplate[i]);
        }
        
        float averageDistance = totalDistance / minCount;
        return averageDistance < template.tolerance;
    }
    
    List<Vector2> NormalizeGesture(List<Vector2> points)
    {
        // Simple normalization - scale to unit square
        if (points.Count == 0) return points;
        
        Vector2 min = points[0];
        Vector2 max = points[0];
        
        foreach (var point in points)
        {
            min = Vector2.Min(min, point);
            max = Vector2.Max(max, point);
        }
        
        Vector2 size = max - min;
        if (size.x == 0 || size.y == 0) return points;
        
        List<Vector2> normalized = new List<Vector2>();
        foreach (var point in points)
        {
            normalized.Add(new Vector2(
                (point.x - min.x) / size.x,
                (point.y - min.y) / size.y
            ));
        }
        
        return normalized;
    }
    
    void OnGestureRecognized(string gestureName)
    {
        Debug.Log($"Gesture recognized: {gestureName}");
        // Trigger gesture-specific actions
    }
}
```

## 💡 Key Highlights

### Input System Comparison
- **New Input System**: Event-based, asset-driven, cross-platform, more complex setup
- **Legacy Input Manager**: Simple, polling-based, editor-configured, being deprecated
- **Performance**: New system is more efficient for complex input scenarios
- **Migration**: Use Input System package for new projects

### Cross-Platform Considerations
- **Input Devices**: Keyboard/mouse (PC), gamepad (console), touch (mobile)
- **Control Schemes**: Design for each platform's strengths
- **UI Scaling**: Adjust touch targets for different screen sizes
- **Testing**: Test on target devices early and often

### Best Practices
- **Event-Driven**: Use callbacks instead of polling when possible
- **Input Validation**: Sanitize and validate all input
- **Buffering**: Implement input buffering for responsive controls
- **Accessibility**: Support alternative input methods and customization

### Performance Tips
- **Avoid GetKey in Update**: Cache input states or use events
- **Touch Optimization**: Limit touch processing to visible UI
- **Input Polling**: Only poll inputs when needed
- **Memory Management**: Minimize allocations in input processing