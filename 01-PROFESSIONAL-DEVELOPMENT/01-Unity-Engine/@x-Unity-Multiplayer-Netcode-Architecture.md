# @x-Unity-Multiplayer-Netcode-Architecture

## 🎯 Learning Objectives
- Master Unity Netcode for GameObjects architecture
- Implement client-server and peer-to-peer networking
- Design scalable multiplayer game systems
- Handle network optimization and security

## 🔧 Unity Netcode Architecture Fundamentals

### Network Manager Configuration
```csharp
// Advanced NetworkManager setup
public class GameNetworkManager : NetworkBehaviour
{
    [Header("Server Configuration")]
    [SerializeField] private int maxPlayers = 4;
    [SerializeField] private string gameVersion = "1.0.0";
    [SerializeField] private float tickRate = 30f;
    
    [Header("Connection Settings")]
    [SerializeField] private float connectionTimeout = 10f;
    [SerializeField] private int maxReconnectAttempts = 3;
    
    public static GameNetworkManager Instance { get; private set; }
    
    private Dictionary<ulong, PlayerData> connectedPlayers = new Dictionary<ulong, PlayerData>();
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeNetworking();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void InitializeNetworking()
    {
        NetworkManager.Singleton.ConnectionApprovalCallback = ConnectionApprovalCallback;
        NetworkManager.Singleton.OnClientConnectedCallback += OnClientConnected;
        NetworkManager.Singleton.OnClientDisconnectCallback += OnClientDisconnected;
        NetworkManager.Singleton.OnServerStarted += OnServerStarted;
        
        // Configure transport
        var transport = NetworkManager.Singleton.NetworkConfig.NetworkTransport;
        if (transport is UnityTransport unityTransport)
        {
            unityTransport.SetConnectionData("127.0.0.1", 7777);
            unityTransport.ConnectionTimeoutMS = (int)(connectionTimeout * 1000);
        }
    }
    
    private void ConnectionApprovalCallback(NetworkManager.ConnectionApprovalRequest request, NetworkManager.ConnectionApprovalResponse response)
    {
        // Validate connection
        if (connectedPlayers.Count >= maxPlayers)
        {
            response.Approved = false;
            response.Reason = "Server full";
            return;
        }
        
        // Version check
        var clientData = System.Text.Encoding.UTF8.GetString(request.Payload);
        if (clientData != gameVersion)
        {
            response.Approved = false;
            response.Reason = "Version mismatch";
            return;
        }
        
        response.Approved = true;
        response.CreatePlayerObject = true;
        response.PlayerPrefabHash = null; // Use default
    }
}
```

### Network Object Management
```csharp
// Advanced NetworkObject with ownership management
public class NetworkObjectManager : NetworkBehaviour
{
    [Header("Ownership Settings")]
    [SerializeField] private bool allowOwnershipTransfer = true;
    [SerializeField] private float ownershipTransferCooldown = 1f;
    
    private float lastOwnershipTransfer;
    private NetworkVariable<ulong> currentOwner = new NetworkVariable<ulong>();
    
    public override void OnNetworkSpawn()
    {
        currentOwner.Value = OwnerClientId;
        currentOwner.OnValueChanged += OnOwnerChanged;
    }
    
    [ServerRpc(RequireOwnership = false)]
    public void RequestOwnershipServerRpc(ulong newOwnerId, ServerRpcParams rpcParams = default)
    {
        if (!allowOwnershipTransfer || Time.time < lastOwnershipTransfer + ownershipTransferCooldown)
            return;
        
        if (CanTransferOwnership(rpcParams.Receive.SenderClientId, newOwnerId))
        {
            NetworkObject.ChangeOwnership(newOwnerId);
            currentOwner.Value = newOwnerId;
            lastOwnershipTransfer = Time.time;
            
            OnOwnershipTransferredClientRpc(newOwnerId);
        }
    }
    
    bool CanTransferOwnership(ulong requesterId, ulong newOwnerId)
    {
        // Implement custom ownership validation logic
        return NetworkManager.Singleton.ConnectedClients.ContainsKey(newOwnerId);
    }
    
    [ClientRpc]
    void OnOwnershipTransferredClientRpc(ulong newOwnerId)
    {
        OnOwnershipChanged(0, newOwnerId); // Trigger local events
    }
    
    void OnOwnerChanged(ulong previousOwner, ulong newOwner)
    {
        Debug.Log($"Ownership changed from {previousOwner} to {newOwner}");
        // Handle ownership change logic
    }
}
```

### Player Network Controller
```csharp
// Comprehensive player networking with prediction
public class NetworkPlayerController : NetworkBehaviour
{
    [Header("Movement Settings")]
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float jumpForce = 10f;
    
    [Header("Network Settings")]
    [SerializeField] private float reconciliationThreshold = 0.1f;
    [SerializeField] private int maxInputBuffer = 30;
    
    // Network variables
    private NetworkVariable<Vector3> networkPosition = new NetworkVariable<Vector3>();
    private NetworkVariable<Quaternion> networkRotation = new NetworkVariable<Quaternion>();
    private NetworkVariable<PlayerState> playerState = new NetworkVariable<PlayerState>();
    
    // Client prediction
    private Queue<InputCommand> inputBuffer = new Queue<InputCommand>();
    private List<StateSnapshot> stateHistory = new List<StateSnapshot>();
    
    private Rigidbody rb;
    private bool isGrounded;
    
    [System.Serializable]
    public struct InputCommand : INetworkSerializable
    {
        public Vector2 moveInput;
        public bool jumpPressed;
        public float timestamp;
        public uint sequenceNumber;
        
        public void NetworkSerialize<T>(BufferSerializer<T> serializer) where T : IReaderWriter
        {
            serializer.SerializeValue(ref moveInput);
            serializer.SerializeValue(ref jumpPressed);
            serializer.SerializeValue(ref timestamp);
            serializer.SerializeValue(ref sequenceNumber);
        }
    }
    
    [System.Serializable]
    public struct StateSnapshot
    {
        public Vector3 position;
        public Vector3 velocity;
        public float timestamp;
        public uint sequenceNumber;
    }
    
    public enum PlayerState
    {
        Idle,
        Moving,
        Jumping,
        Falling
    }
    
    void Awake()
    {
        rb = GetComponent<Rigidbody>();
    }
    
    public override void OnNetworkSpawn()
    {
        if (IsOwner)
        {
            networkPosition.Value = transform.position;
            networkRotation.Value = transform.rotation;
        }
        else
        {
            transform.position = networkPosition.Value;
            transform.rotation = networkRotation.Value;
        }
        
        networkPosition.OnValueChanged += OnPositionChanged;
        networkRotation.OnValueChanged += OnRotationChanged;
    }
    
    void Update()
    {
        if (IsOwner)
        {
            HandleInput();
            PredictMovement();
        }
        else
        {
            InterpolatePosition();
        }
    }
    
    void HandleInput()
    {
        var input = new InputCommand
        {
            moveInput = new Vector2(Input.GetAxis("Horizontal"), Input.GetAxis("Vertical")),
            jumpPressed = Input.GetKeyDown(KeyCode.Space),
            timestamp = Time.time,
            sequenceNumber = (uint)inputBuffer.Count
        };
        
        // Buffer input for prediction
        inputBuffer.Enqueue(input);
        if (inputBuffer.Count > maxInputBuffer)
            inputBuffer.Dequeue();
        
        // Send to server
        ProcessInputServerRpc(input);
    }
    
    [ServerRpc]
    void ProcessInputServerRpc(InputCommand input, ServerRpcParams rpcParams = default)
    {
        // Validate and process input on server
        if (ValidateInput(input, rpcParams.Receive.SenderClientId))
        {
            ApplyMovement(input);
            
            // Send authoritative state back
            var state = new StateSnapshot
            {
                position = transform.position,
                velocity = rb.velocity,
                timestamp = Time.time,
                sequenceNumber = input.sequenceNumber
            };
            
            UpdateClientStateClientRpc(state, ClientRpcParams.CreateSendToClient(rpcParams.Receive.SenderClientId));
        }
    }
    
    [ClientRpc]
    void UpdateClientStateClientRpc(StateSnapshot serverState, ClientRpcParams rpcParams = default)
    {
        if (!IsOwner) return;
        
        // Client-side prediction reconciliation
        var localState = GetCurrentState();
        float positionError = Vector3.Distance(localState.position, serverState.position);
        
        if (positionError > reconciliationThreshold)
        {
            // Reconcile position
            transform.position = serverState.position;
            rb.velocity = serverState.velocity;
            
            // Replay inputs after server state
            ReplayInputs(serverState.sequenceNumber);
        }
    }
    
    void PredictMovement()
    {
        if (inputBuffer.Count > 0)
        {
            var input = inputBuffer.Peek();
            ApplyMovement(input);
            
            // Store state for reconciliation
            stateHistory.Add(GetCurrentState());
            if (stateHistory.Count > maxInputBuffer)
                stateHistory.RemoveAt(0);
        }
    }
    
    void ApplyMovement(InputCommand input)
    {
        // Ground check
        isGrounded = Physics.Raycast(transform.position, Vector3.down, 1.1f);
        
        // Movement
        Vector3 movement = new Vector3(input.moveInput.x, 0, input.moveInput.y) * moveSpeed;
        rb.velocity = new Vector3(movement.x, rb.velocity.y, movement.z);
        
        // Jumping
        if (input.jumpPressed && isGrounded)
        {
            rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
        }
        
        // Update state
        UpdatePlayerState();
        
        // Update network variables (server only)
        if (IsServer)
        {
            networkPosition.Value = transform.position;
            networkRotation.Value = transform.rotation;
            playerState.Value = GetPlayerState();
        }
    }
    
    void ReplayInputs(uint fromSequence)
    {
        // Remove processed inputs
        while (inputBuffer.Count > 0 && inputBuffer.Peek().sequenceNumber <= fromSequence)
            inputBuffer.Dequeue();
        
        // Replay remaining inputs
        var tempInputs = inputBuffer.ToArray();
        foreach (var input in tempInputs)
        {
            ApplyMovement(input);
        }
    }
    
    bool ValidateInput(InputCommand input, ulong senderId)
    {
        // Anti-cheat validation
        if (input.moveInput.magnitude > 1.1f) // Allow small floating point errors
            return false;
        
        float timeDelta = Time.time - input.timestamp;
        if (timeDelta > 1f || timeDelta < -0.1f) // Reasonable time bounds
            return false;
        
        return true;
    }
    
    StateSnapshot GetCurrentState()
    {
        return new StateSnapshot
        {
            position = transform.position,
            velocity = rb.velocity,
            timestamp = Time.time,
            sequenceNumber = (uint)inputBuffer.Count
        };
    }
    
    void UpdatePlayerState()
    {
        if (rb.velocity.y > 0.1f)
            playerState.Value = PlayerState.Jumping;
        else if (rb.velocity.y < -0.1f)
            playerState.Value = PlayerState.Falling;
        else if (rb.velocity.magnitude > 0.1f)
            playerState.Value = PlayerState.Moving;
        else
            playerState.Value = PlayerState.Idle;
    }
    
    PlayerState GetPlayerState()
    {
        return playerState.Value;
    }
    
    void OnPositionChanged(Vector3 previousPos, Vector3 newPos)
    {
        if (!IsOwner)
        {
            // Smooth interpolation for non-owners
            StartCoroutine(InterpolateToPosition(newPos));
        }
    }
    
    void OnRotationChanged(Quaternion previousRot, Quaternion newRot)
    {
        if (!IsOwner)
        {
            transform.rotation = newRot;
        }
    }
    
    IEnumerator InterpolateToPosition(Vector3 targetPosition)
    {
        Vector3 startPosition = transform.position;
        float elapsedTime = 0f;
        float interpolationTime = 1f / 30f; // Match server tick rate
        
        while (elapsedTime < interpolationTime)
        {
            transform.position = Vector3.Lerp(startPosition, targetPosition, elapsedTime / interpolationTime);
            elapsedTime += Time.deltaTime;
            yield return null;
        }
        
        transform.position = targetPosition;
    }
    
    void InterpolatePosition()
    {
        // Simple position interpolation for non-owners
        transform.position = Vector3.Lerp(transform.position, networkPosition.Value, Time.deltaTime * 15f);
        transform.rotation = Quaternion.Lerp(transform.rotation, networkRotation.Value, Time.deltaTime * 15f);
    }
}
```

## 🌐 Advanced Networking Systems

### Lag Compensation System
```csharp
// Server-side lag compensation
public class LagCompensationManager : NetworkBehaviour
{
    [Header("Lag Compensation Settings")]
    [SerializeField] private float maxCompensationTime = 0.5f;
    [SerializeField] private int historyBufferSize = 60;
    
    private Dictionary<ulong, Queue<PlayerHistoryState>> playerHistory = new Dictionary<ulong, Queue<PlayerHistoryState>>();
    
    [System.Serializable]
    public struct PlayerHistoryState
    {
        public Vector3 position;
        public Quaternion rotation;
        public float timestamp;
        public bool isValid;
    }
    
    void FixedUpdate()
    {
        if (IsServer)
        {
            RecordPlayerStates();
        }
    }
    
    void RecordPlayerStates()
    {
        foreach (var client in NetworkManager.Singleton.ConnectedClients)
        {
            var playerId = client.Key;
            var playerObject = client.Value.PlayerObject;
            
            if (playerObject != null)
            {
                if (!playerHistory.ContainsKey(playerId))
                {
                    playerHistory[playerId] = new Queue<PlayerHistoryState>();
                }
                
                var history = playerHistory[playerId];
                var state = new PlayerHistoryState
                {
                    position = playerObject.transform.position,
                    rotation = playerObject.transform.rotation,
                    timestamp = Time.time,
                    isValid = true
                };
                
                history.Enqueue(state);
                
                // Maintain buffer size
                while (history.Count > historyBufferSize)
                {
                    history.Dequeue();
                }
            }
        }
    }
    
    public bool RewindPlayer(ulong playerId, float timestamp, out PlayerHistoryState rewindState)
    {
        rewindState = default;
        
        if (!playerHistory.ContainsKey(playerId))
            return false;
        
        var history = playerHistory[playerId];
        var targetTime = timestamp;
        
        // Find closest state to target time
        PlayerHistoryState closestState = default;
        float closestTimeDiff = float.MaxValue;
        bool foundState = false;
        
        foreach (var state in history)
        {
            if (!state.isValid) continue;
            
            float timeDiff = Mathf.Abs(state.timestamp - targetTime);
            if (timeDiff < closestTimeDiff && timeDiff <= maxCompensationTime)
            {
                closestState = state;
                closestTimeDiff = timeDiff;
                foundState = true;
            }
        }
        
        if (foundState)
        {
            rewindState = closestState;
            return true;
        }
        
        return false;
    }
    
    public void RestorePlayer(ulong playerId, Vector3 currentPosition, Quaternion currentRotation)
    {
        var clientObject = NetworkManager.Singleton.ConnectedClients[playerId].PlayerObject;
        if (clientObject != null)
        {
            clientObject.transform.position = currentPosition;
            clientObject.transform.rotation = currentRotation;
        }
    }
}
```

### Network Performance Monitor
```csharp
// Real-time network performance monitoring
public class NetworkPerformanceMonitor : NetworkBehaviour
{
    [Header("Monitoring Settings")]
    [SerializeField] private float updateInterval = 1f;
    [SerializeField] private int sampleSize = 30;
    
    [Header("Performance Thresholds")]
    [SerializeField] private float highLatencyThreshold = 100f; // ms
    [SerializeField] private float packetLossThreshold = 0.05f; // 5%
    [SerializeField] private float jitterThreshold = 20f; // ms
    
    public struct NetworkMetrics
    {
        public float averageLatency;
        public float packetLoss;
        public float jitter;
        public int bytesPerSecond;
        public float timestamp;
    }
    
    private Queue<NetworkMetrics> metricsHistory = new Queue<NetworkMetrics>();
    private NetworkVariable<NetworkMetrics> currentMetrics = new NetworkVariable<NetworkMetrics>();
    
    // Performance optimization flags
    public bool shouldReduceUpdateRate { get; private set; }
    public bool shouldCompressData { get; private set; }
    public bool shouldUseReliableDelivery { get; private set; }
    
    void Start()
    {
        if (IsServer)
        {
            InvokeRepeating(nameof(UpdateMetrics), 0f, updateInterval);
        }
        
        currentMetrics.OnValueChanged += OnMetricsChanged;
    }
    
    void UpdateMetrics()
    {
        var transport = NetworkManager.Singleton.NetworkConfig.NetworkTransport;
        var metrics = new NetworkMetrics
        {
            averageLatency = GetAverageRTT(),
            packetLoss = GetPacketLossRate(),
            jitter = GetJitter(),
            bytesPerSecond = GetBandwidthUsage(),
            timestamp = Time.time
        };
        
        metricsHistory.Enqueue(metrics);
        if (metricsHistory.Count > sampleSize)
            metricsHistory.Dequeue();
        
        currentMetrics.Value = metrics;
        AnalyzePerformance(metrics);
    }
    
    void AnalyzePerformance(NetworkMetrics metrics)
    {
        // Determine optimization strategies based on metrics
        shouldReduceUpdateRate = metrics.averageLatency > highLatencyThreshold || 
                                metrics.packetLoss > packetLossThreshold;
        
        shouldCompressData = metrics.bytesPerSecond > GetBandwidthLimit() * 0.8f;
        
        shouldUseReliableDelivery = metrics.packetLoss > packetLossThreshold * 0.5f;
        
        // Apply optimizations
        if (shouldReduceUpdateRate)
        {
            AdjustNetworkUpdateRate(0.5f); // Reduce by 50%
        }
        
        if (shouldCompressData)
        {
            EnableDataCompression(true);
        }
    }
    
    float GetAverageRTT()
    {
        // Implementation depends on transport layer
        // This is a placeholder - actual implementation would query transport
        return UnityEngine.Random.Range(20f, 200f); // Simulated for example
    }
    
    float GetPacketLossRate()
    {
        // Calculate packet loss based on sent vs received packets
        return UnityEngine.Random.Range(0f, 0.1f); // Simulated
    }
    
    float GetJitter()
    {
        // Calculate variance in packet arrival times
        return UnityEngine.Random.Range(5f, 50f); // Simulated
    }
    
    int GetBandwidthUsage()
    {
        // Calculate current bandwidth usage
        return UnityEngine.Random.Range(1000, 10000); // Simulated bytes/sec
    }
    
    int GetBandwidthLimit()
    {
        return 50000; // 50KB/s example limit
    }
    
    void AdjustNetworkUpdateRate(float multiplier)
    {
        NetworkManager.Singleton.NetworkConfig.SendTickRate = (ushort)(NetworkManager.Singleton.NetworkConfig.SendTickRate * multiplier);
    }
    
    void EnableDataCompression(bool enable)
    {
        // Implementation would enable/disable compression at transport level
        Debug.Log($"Data compression: {(enable ? "Enabled" : "Disabled")}");
    }
    
    void OnMetricsChanged(NetworkMetrics previous, NetworkMetrics current)
    {
        // React to metric changes on all clients
        if (current.averageLatency > highLatencyThreshold)
        {
            Debug.LogWarning($"High latency detected: {current.averageLatency}ms");
        }
    }
    
    public NetworkMetrics GetAverageMetrics()
    {
        if (metricsHistory.Count == 0)
            return default;
        
        var avgLatency = metricsHistory.Average(m => m.averageLatency);
        var avgPacketLoss = metricsHistory.Average(m => m.packetLoss);
        var avgJitter = metricsHistory.Average(m => m.jitter);
        var avgBandwidth = metricsHistory.Average(m => m.bytesPerSecond);
        
        return new NetworkMetrics
        {
            averageLatency = avgLatency,
            packetLoss = avgPacketLoss,
            jitter = avgJitter,
            bytesPerSecond = (int)avgBandwidth,
            timestamp = Time.time
        };
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Network Behavior Analysis
```csharp
public class NetworkBehaviorAnalyzer : MonoBehaviour
{
    public class ConnectionPattern
    {
        public float averageSessionLength;
        public int frequentDisconnects;
        public List<string> commonErrors;
        public float peakUsageHours;
    }
    
    public static string GenerateNetworkAnalysisPrompt(ConnectionPattern pattern)
    {
        return $@"
        Analyze multiplayer game network patterns:
        - Session Length: {pattern.averageSessionLength} minutes
        - Disconnects: {pattern.frequentDisconnects} per session
        - Common Errors: {string.Join(", ", pattern.commonErrors)}
        - Peak Usage: {pattern.peakUsageHours} hours
        
        Provide recommendations for:
        1. Connection stability improvements
        2. Error handling strategies
        3. Scalability optimizations
        4. Player retention techniques
        ";
    }
}
```

## 💡 Key Highlights

### Architecture Patterns
- **Client-Server**: Authoritative server with client prediction
- **Lag Compensation**: Server-side rewinding for fair gameplay
- **State Synchronization**: Reliable and unreliable data channels
- **Performance Monitoring**: Real-time network metrics and optimization

### Production Considerations
- **Anti-Cheat**: Server-side validation and sanity checks
- **Scalability**: Dynamic quality adjustment based on network conditions
- **Cross-Platform**: Platform-agnostic networking implementation
- **Testing**: Network simulation tools for latency and packet loss

This comprehensive networking architecture provides the foundation for professional multiplayer game development, essential for senior Unity positions requiring networking expertise.