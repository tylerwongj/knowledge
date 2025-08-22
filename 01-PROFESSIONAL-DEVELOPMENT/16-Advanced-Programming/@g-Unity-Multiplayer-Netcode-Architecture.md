# @g-Unity-Multiplayer-Netcode-Architecture

## 🎯 Learning Objectives

- Master Unity Netcode for GameObjects multiplayer architecture
- Implement client-server synchronization with optimal performance
- Create scalable multiplayer systems for real-time games
- Build secure and robust networked game mechanics

## 🔧 Core Netcode Architecture

### Network Manager and Connection Setup

```csharp
using Unity.Netcode;
using Unity.Collections;
using UnityEngine;
using System.Collections.Generic;

public class GameNetworkManager : NetworkBehaviour
{
    [Header("Network Configuration")]
    [SerializeField] private NetworkConfig networkConfig;
    [SerializeField] private int maxPlayers = 4;
    [SerializeField] private float connectionTimeout = 30f;
    [SerializeField] private bool enableRelay = true;
    
    [Header("Game State")]
    [SerializeField] private NetworkVariable<GameState> currentGameState = 
        new NetworkVariable<GameState>(GameState.Lobby, NetworkVariableReadPermission.Everyone);
    
    // Network events
    public static System.Action<ulong> OnPlayerConnected;
    public static System.Action<ulong> OnPlayerDisconnected;
    public static System.Action<GameState> OnGameStateChanged;
    
    // Player management
    private Dictionary<ulong, PlayerData> connectedPlayers = new Dictionary<ulong, PlayerData>();
    private NetworkList<PlayerData> playerList;
    
    public enum GameState
    {
        Lobby,
        Starting,
        InGame,
        GameOver,
        Disconnected
    }
    
    [System.Serializable]
    public struct PlayerData : INetworkSerializable
    {
        public ulong clientId;
        public FixedString64Bytes playerName;
        public int playerIndex;
        public bool isReady;
        public Vector3 spawnPosition;
        public float score;
        
        public void NetworkSerialize<T>(BufferSerializer<T> serializer) where T : IReaderWriter
        {
            serializer.SerializeValue(ref clientId);
            serializer.SerializeValue(ref playerName);
            serializer.SerializeValue(ref playerIndex);
            serializer.SerializeValue(ref isReady);
            serializer.SerializeValue(ref spawnPosition);
            serializer.SerializeValue(ref score);
        }
    }
    
    private void Awake()
    {
        // Initialize network list
        playerList = new NetworkList<PlayerData>();
        
        // Don't destroy on load
        if (FindObjectsOfType<GameNetworkManager>().Length == 1)
        {
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
            return;
        }
    }
    
    public override void OnNetworkSpawn()
    {
        // Subscribe to network events
        NetworkManager.Singleton.OnClientConnectedCallback += OnClientConnected;
        NetworkManager.Singleton.OnClientDisconnectCallback += OnClientDisconnected;
        
        // Subscribe to game state changes
        currentGameState.OnValueChanged += OnGameStateValueChanged;
        
        // Subscribe to player list changes
        playerList.OnListChanged += OnPlayerListChanged;
        
        if (IsServer)
        {
            NetworkManager.Singleton.ConnectionApprovalCallback = ApprovalCheck;
        }
    }
    
    public override void OnNetworkDespawn()
    {
        // Unsubscribe from events
        if (NetworkManager.Singleton != null)
        {
            NetworkManager.Singleton.OnClientConnectedCallback -= OnClientConnected;
            NetworkManager.Singleton.OnClientDisconnectCallback -= OnClientDisconnected;
        }
        
        currentGameState.OnValueChanged -= OnGameStateValueChanged;
        playerList.OnListChanged -= OnPlayerListChanged;
    }
    
    private void ApprovalCheck(NetworkManager.ConnectionApprovalRequest request, 
                              NetworkManager.ConnectionApprovalResponse response)
    {
        // Check if game is full
        if (connectedPlayers.Count >= maxPlayers)
        {
            response.Approved = false;
            response.Reason = "Game is full";
            return;
        }
        
        // Check game state
        if (currentGameState.Value != GameState.Lobby)
        {
            response.Approved = false;
            response.Reason = "Game already in progress";
            return;
        }
        
        // Approve connection
        response.Approved = true;
        response.CreatePlayerObject = true;
        response.PlayerPrefabHash = null; // Use default player prefab
    }
    
    private void OnClientConnected(ulong clientId)
    {
        if (IsServer)
        {
            // Create player data
            var playerData = new PlayerData
            {
                clientId = clientId,
                playerName = $"Player_{clientId}",
                playerIndex = connectedPlayers.Count,
                isReady = false,
                spawnPosition = GetSpawnPosition(connectedPlayers.Count),
                score = 0f
            };
            
            connectedPlayers[clientId] = playerData;
            playerList.Add(playerData);
            
            Debug.Log($"Player {clientId} connected. Total players: {connectedPlayers.Count}");
        }
        
        OnPlayerConnected?.Invoke(clientId);
    }
    
    private void OnClientDisconnected(ulong clientId)
    {
        if (IsServer)
        {
            if (connectedPlayers.ContainsKey(clientId))
            {
                // Remove from player list
                var playerData = connectedPlayers[clientId];
                for (int i = 0; i < playerList.Count; i++)
                {
                    if (playerList[i].clientId == clientId)
                    {
                        playerList.RemoveAt(i);
                        break;
                    }
                }
                
                connectedPlayers.Remove(clientId);
                Debug.Log($"Player {clientId} disconnected. Remaining players: {connectedPlayers.Count}");
                
                // Check if we need to end the game
                if (connectedPlayers.Count == 0)
                {
                    ChangeGameState(GameState.Lobby);
                }
            }
        }
        
        OnPlayerDisconnected?.Invoke(clientId);
    }
    
    private void OnGameStateValueChanged(GameState previousState, GameState newState)
    {
        Debug.Log($"Game state changed from {previousState} to {newState}");
        OnGameStateChanged?.Invoke(newState);
        
        // Handle state-specific logic
        switch (newState)
        {
            case GameState.Starting:
                if (IsServer)
                {
                    StartCoroutine(StartGameCountdown());
                }
                break;
                
            case GameState.InGame:
                if (IsServer)
                {
                    SpawnAllPlayers();
                }
                break;
                
            case GameState.GameOver:
                if (IsServer)
                {
                    StartCoroutine(ReturnToLobby());
                }
                break;
        }
    }
    
    private void OnPlayerListChanged(NetworkListEvent<PlayerData> changeEvent)
    {
        // Handle player list changes for UI updates
        Debug.Log($"Player list changed: {changeEvent.Type}");
    }
    
    [ServerRpc(RequireOwnership = false)]
    public void SetPlayerReadyServerRpc(ulong clientId, bool ready)
    {
        if (connectedPlayers.ContainsKey(clientId))
        {
            var playerData = connectedPlayers[clientId];
            playerData.isReady = ready;
            connectedPlayers[clientId] = playerData;
            
            // Update network list
            for (int i = 0; i < playerList.Count; i++)
            {
                if (playerList[i].clientId == clientId)
                {
                    playerList[i] = playerData;
                    break;
                }
            }
            
            // Check if all players are ready
            CheckAllPlayersReady();
        }
    }
    
    private void CheckAllPlayersReady()
    {
        if (currentGameState.Value != GameState.Lobby) return;
        
        bool allReady = connectedPlayers.Count > 0;
        foreach (var player in connectedPlayers.Values)
        {
            if (!player.isReady)
            {
                allReady = false;
                break;
            }
        }
        
        if (allReady && connectedPlayers.Count >= 2) // Minimum 2 players
        {
            ChangeGameState(GameState.Starting);
        }
    }
    
    private void ChangeGameState(GameState newState)
    {
        if (IsServer)
        {
            currentGameState.Value = newState;
        }
    }
    
    private Vector3 GetSpawnPosition(int playerIndex)
    {
        // Define spawn positions in a circle
        float angle = (playerIndex * 360f / maxPlayers) * Mathf.Deg2Rad;
        float radius = 5f;
        return new Vector3(Mathf.Sin(angle) * radius, 0f, Mathf.Cos(angle) * radius);
    }
    
    private System.Collections.IEnumerator StartGameCountdown()
    {
        yield return new WaitForSeconds(3f); // 3 second countdown
        ChangeGameState(GameState.InGame);
    }
    
    private void SpawnAllPlayers()
    {
        foreach (var playerData in connectedPlayers.Values)
        {
            // Spawn player at designated position
            SpawnPlayerAtPositionClientRpc(playerData.clientId, playerData.spawnPosition);
        }
    }
    
    [ClientRpc]
    private void SpawnPlayerAtPositionClientRpc(ulong clientId, Vector3 position)
    {
        // Find player network object and set position
        var playerObject = NetworkManager.Singleton.ConnectedClients[clientId].PlayerObject;
        if (playerObject != null)
        {
            playerObject.transform.position = position;
        }
    }
    
    private System.Collections.IEnumerator ReturnToLobby()
    {
        yield return new WaitForSeconds(5f); // Show game over for 5 seconds
        
        // Reset all player ready states
        foreach (var clientId in connectedPlayers.Keys.ToArray())
        {
            var playerData = connectedPlayers[clientId];
            playerData.isReady = false;
            playerData.score = 0f;
            connectedPlayers[clientId] = playerData;
        }
        
        ChangeGameState(GameState.Lobby);
    }
    
    // Public methods for UI and game logic
    public PlayerData[] GetAllPlayers()
    {
        return playerList.ToArray();
    }
    
    public PlayerData? GetPlayer(ulong clientId)
    {
        return connectedPlayers.ContainsKey(clientId) ? connectedPlayers[clientId] : null;
    }
    
    public GameState GetCurrentGameState()
    {
        return currentGameState.Value;
    }
    
    public bool IsGameInProgress()
    {
        return currentGameState.Value == GameState.InGame;
    }
}
```

### Networked Player Controller

```csharp
using Unity.Netcode;
using UnityEngine;

public class NetworkedPlayerController : NetworkBehaviour
{
    [Header("Movement Settings")]
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float jumpForce = 8f;
    [SerializeField] private float rotationSpeed = 10f;
    
    [Header("Network Settings")]
    [SerializeField] private float networkUpdateRate = 30f;
    [SerializeField] private float positionThreshold = 0.1f;
    [SerializeField] private float rotationThreshold = 1f;
    
    // Network variables with client authority for responsive movement
    private NetworkVariable<Vector3> networkPosition = new NetworkVariable<Vector3>(
        default, NetworkVariableReadPermission.Everyone, NetworkVariableWritePermission.Owner);
    
    private NetworkVariable<Quaternion> networkRotation = new NetworkVariable<Quaternion>(
        default, NetworkVariableReadPermission.Everyone, NetworkVariableWritePermission.Owner);
    
    private NetworkVariable<PlayerState> networkPlayerState = new NetworkVariable<PlayerState>(
        default, NetworkVariableReadPermission.Everyone, NetworkVariableWritePermission.Owner);
    
    // Components
    private Rigidbody playerRigidbody;
    private Animator playerAnimator;
    private CharacterController characterController;
    
    // Input and movement
    private Vector2 movementInput;
    private bool jumpInput;
    private bool isGrounded;
    
    // Network interpolation
    private Vector3 serverPosition;
    private Quaternion serverRotation;
    private float lastUpdateTime;
    
    public struct PlayerState : INetworkSerializable
    {
        public bool isGrounded;
        public bool isMoving;
        public bool isJumping;
        public float health;
        public int ammo;
        
        public void NetworkSerialize<T>(BufferSerializer<T> serializer) where T : IReaderWriter
        {
            serializer.SerializeValue(ref isGrounded);
            serializer.SerializeValue(ref isMoving);
            serializer.SerializeValue(ref isJumping);
            serializer.SerializeValue(ref health);
            serializer.SerializeValue(ref ammo);
        }
    }
    
    private void Awake()
    {
        characterController = GetComponent<CharacterController>();
        playerRigidbody = GetComponent<Rigidbody>();
        playerAnimator = GetComponent<Animator>();
    }
    
    public override void OnNetworkSpawn()
    {
        // Subscribe to network variable changes
        networkPosition.OnValueChanged += OnNetworkPositionChanged;
        networkRotation.OnValueChanged += OnNetworkRotationChanged;
        networkPlayerState.OnValueChanged += OnNetworkPlayerStateChanged;
        
        // Initialize position
        if (IsOwner)
        {
            networkPosition.Value = transform.position;
            networkRotation.Value = transform.rotation;
        }
        else
        {
            // Set initial interpolation targets
            serverPosition = networkPosition.Value;
            serverRotation = networkRotation.Value;
            lastUpdateTime = Time.time;
        }
        
        // Start network update coroutine for owner
        if (IsOwner)
        {
            InvokeRepeating(nameof(SendNetworkUpdate), 0f, 1f / networkUpdateRate);
        }
    }
    
    public override void OnNetworkDespawn()
    {
        networkPosition.OnValueChanged -= OnNetworkPositionChanged;
        networkRotation.OnValueChanged -= OnNetworkRotationChanged;
        networkPlayerState.OnValueChanged -= OnNetworkPlayerStateChanged;
        
        if (IsOwner)
        {
            CancelInvoke(nameof(SendNetworkUpdate));
        }
    }
    
    private void Update()
    {
        if (IsOwner)
        {
            // Handle input and movement for owner
            HandleInput();
            HandleMovement();
            UpdatePlayerState();
        }
        else
        {
            // Interpolate to network position for non-owners
            InterpolateNetworkTransform();
        }
        
        // Update animations for all clients
        UpdateAnimations();
    }
    
    private void HandleInput()
    {
        // Get movement input
        movementInput.x = Input.GetAxisRaw("Horizontal");
        movementInput.y = Input.GetAxisRaw("Vertical");
        
        // Get jump input
        jumpInput = Input.GetButtonDown("Jump");
        
        // Check if grounded
        isGrounded = characterController.isGrounded;
    }
    
    private void HandleMovement()
    {
        // Calculate movement direction
        Vector3 moveDirection = new Vector3(movementInput.x, 0f, movementInput.y);
        moveDirection = transform.TransformDirection(moveDirection);
        moveDirection.Normalize();
        
        // Apply movement
        if (characterController != null)
        {
            // Character controller movement
            Vector3 velocity = moveDirection * moveSpeed;
            
            // Apply gravity
            if (!isGrounded)
            {
                velocity.y = playerRigidbody.velocity.y;
            }
            
            // Apply jump
            if (jumpInput && isGrounded)
            {
                velocity.y = jumpForce;
            }
            
            characterController.Move(velocity * Time.deltaTime);
        }
        
        // Handle rotation
        if (moveDirection != Vector3.zero)
        {
            Quaternion targetRotation = Quaternion.LookRotation(moveDirection);
            transform.rotation = Quaternion.Slerp(transform.rotation, targetRotation, 
                rotationSpeed * Time.deltaTime);
        }
    }
    
    private void UpdatePlayerState()
    {
        var state = networkPlayerState.Value;
        state.isGrounded = isGrounded;
        state.isMoving = movementInput.magnitude > 0.1f;
        state.isJumping = jumpInput && isGrounded;
        // Update other state values as needed
        
        networkPlayerState.Value = state;
    }
    
    private void SendNetworkUpdate()
    {
        if (!IsOwner) return;
        
        // Only send updates if significant change
        bool positionChanged = Vector3.Distance(transform.position, networkPosition.Value) > positionThreshold;
        bool rotationChanged = Quaternion.Angle(transform.rotation, networkRotation.Value) > rotationThreshold;
        
        if (positionChanged || rotationChanged)
        {
            networkPosition.Value = transform.position;
            networkRotation.Value = transform.rotation;
        }
    }
    
    private void OnNetworkPositionChanged(Vector3 oldPos, Vector3 newPos)
    {
        if (!IsOwner)
        {
            serverPosition = newPos;
            lastUpdateTime = Time.time;
        }
    }
    
    private void OnNetworkRotationChanged(Quaternion oldRot, Quaternion newRot)
    {
        if (!IsOwner)
        {
            serverRotation = newRot;
        }
    }
    
    private void OnNetworkPlayerStateChanged(PlayerState oldState, PlayerState newState)
    {
        // Handle state changes for visual effects, animations, etc.
        if (newState.isJumping && !oldState.isJumping)
        {
            // Trigger jump effect
            TriggerJumpEffect();
        }
    }
    
    private void InterpolateNetworkTransform()
    {
        // Smooth interpolation to server position
        float timeSinceUpdate = Time.time - lastUpdateTime;
        float lerpRate = Mathf.Clamp01(timeSinceUpdate * networkUpdateRate);
        
        transform.position = Vector3.Lerp(transform.position, serverPosition, lerpRate);
        transform.rotation = Quaternion.Lerp(transform.rotation, serverRotation, lerpRate);
    }
    
    private void UpdateAnimations()
    {
        if (playerAnimator == null) return;
        
        var state = networkPlayerState.Value;
        playerAnimator.SetBool("IsGrounded", state.isGrounded);
        playerAnimator.SetBool("IsMoving", state.isMoving);
        playerAnimator.SetBool("IsJumping", state.isJumping);
    }
    
    private void TriggerJumpEffect()
    {
        // Play jump sound, particle effect, etc.
        Debug.Log($"Player {NetworkObjectId} jumped!");
    }
    
    // Network RPC methods for actions
    [ServerRpc]
    public void FireWeaponServerRpc(Vector3 origin, Vector3 direction)
    {
        // Server authoritative weapon firing
        if (CanFireWeapon())
        {
            ProcessWeaponFire(origin, direction);
            FireWeaponClientRpc(origin, direction);
        }
    }
    
    [ClientRpc]
    private void FireWeaponClientRpc(Vector3 origin, Vector3 direction)
    {
        // Visual effects for weapon firing
        CreateMuzzleFlash(origin, direction);
        PlayFireSound();
    }
    
    private bool CanFireWeapon()
    {
        var state = networkPlayerState.Value;
        return state.ammo > 0; // Add more validation as needed
    }
    
    private void ProcessWeaponFire(Vector3 origin, Vector3 direction)
    {
        // Server-side weapon logic
        var state = networkPlayerState.Value;
        state.ammo = Mathf.Max(0, state.ammo - 1);
        networkPlayerState.Value = state;
        
        // Raycast for hit detection
        if (Physics.Raycast(origin, direction, out RaycastHit hit, 100f))
        {
            // Process hit
            var targetPlayer = hit.collider.GetComponent<NetworkedPlayerController>();
            if (targetPlayer != null)
            {
                targetPlayer.TakeDamageServerRpc(10f, NetworkObjectId);
            }
        }
    }
    
    [ServerRpc]
    public void TakeDamageServerRpc(float damage, ulong attackerId)
    {
        var state = networkPlayerState.Value;
        state.health = Mathf.Max(0f, state.health - damage);
        networkPlayerState.Value = state;
        
        // Notify clients of damage taken
        TakeDamageClientRpc(damage, attackerId);
        
        if (state.health <= 0f)
        {
            HandlePlayerDeathServerRpc();
        }
    }
    
    [ClientRpc]
    private void TakeDamageClientRpc(float damage, ulong attackerId)
    {
        // Visual feedback for taking damage
        ShowDamageEffect(damage);
        
        if (IsOwner)
        {
            // Update UI for owner
            UpdateHealthUI();
        }
    }
    
    [ServerRpc]
    private void HandlePlayerDeathServerRpc()
    {
        // Server-side death logic
        HandlePlayerDeathClientRpc();
    }
    
    [ClientRpc]
    private void HandlePlayerDeathClientRpc()
    {
        // Death effects and respawn logic
        ShowDeathEffect();
        
        if (IsServer)
        {
            // Respawn after delay
            Invoke(nameof(RespawnPlayer), 3f);
        }
    }
    
    private void RespawnPlayer()
    {
        // Reset player state
        var state = networkPlayerState.Value;
        state.health = 100f;
        state.ammo = 30;
        networkPlayerState.Value = state;
        
        // Reset position
        transform.position = Vector3.zero; // Or get spawn position from GameManager
        networkPosition.Value = transform.position;
    }
    
    // Visual effect methods (implement based on your game's needs)
    private void CreateMuzzleFlash(Vector3 origin, Vector3 direction) { }
    private void PlayFireSound() { }
    private void ShowDamageEffect(float damage) { }
    private void UpdateHealthUI() { }
    private void ShowDeathEffect() { }
}
```

## 🚀 AI/LLM Integration Opportunities

### Intelligent Netcode Optimization

```
Generate Unity Netcode systems for:
1. Adaptive network prediction and lag compensation algorithms
2. Intelligent bandwidth management for mobile multiplayer games
3. Server-side anti-cheat validation systems
4. Dynamic load balancing for multiplayer game sessions

Context: Real-time multiplayer game with 4-16 players
Focus: Low latency, cheat prevention, scalable architecture
Requirements: Production-ready code with comprehensive error handling
```

### Automated Network Testing

```
Create automated testing frameworks for Unity Netcode:
1. Network simulation with artificial latency and packet loss
2. Automated stress testing for concurrent player connections
3. Desynchronization detection and recovery systems
4. Performance profiling tools for network-intensive operations

Environment: Unity Netcode for GameObjects, automated CI/CD pipeline
Goals: Reliable multiplayer experience, early issue detection, performance optimization
```

## 💡 Advanced Networking Patterns

### Object Pooling for Networked Objects

```csharp
using Unity.Netcode;
using Unity.Collections;
using UnityEngine;
using System.Collections.Generic;

public class NetworkedObjectPool : NetworkBehaviour
{
    [Header("Pool Configuration")]
    [SerializeField] private NetworkObject prefab;
    [SerializeField] private int initialPoolSize = 20;
    [SerializeField] private int maxPoolSize = 100;
    [SerializeField] private bool allowGrowth = true;
    
    // Pool management
    private Queue<NetworkObject> availableObjects = new Queue<NetworkObject>();
    private HashSet<NetworkObject> activeObjects = new HashSet<NetworkObject>();
    private Dictionary<ulong, NetworkObject> networkIdToObject = new Dictionary<ulong, NetworkObject>();
    
    // Network list for syncing pool state
    private NetworkList<PooledObjectData> pooledObjects;
    
    public struct PooledObjectData : INetworkSerializable
    {
        public ulong networkId;
        public bool isActive;
        public Vector3 position;
        public Quaternion rotation;
        public float spawnTime;
        
        public void NetworkSerialize<T>(BufferSerializer<T> serializer) where T : IReaderWriter
        {
            serializer.SerializeValue(ref networkId);
            serializer.SerializeValue(ref isActive);
            serializer.SerializeValue(ref position);
            serializer.SerializeValue(ref rotation);
            serializer.SerializeValue(ref spawnTime);
        }
    }
    
    private void Awake()
    {
        pooledObjects = new NetworkList<PooledObjectData>();
    }
    
    public override void OnNetworkSpawn()
    {
        if (IsServer)
        {
            InitializePool();
        }
        
        // Subscribe to pool changes
        pooledObjects.OnListChanged += OnPooledObjectsChanged;
    }
    
    public override void OnNetworkDespawn()
    {
        pooledObjects.OnListChanged -= OnPooledObjectsChanged;
        
        // Clean up pool
        ClearPool();
    }
    
    private void InitializePool()
    {
        if (!IsServer) return;
        
        for (int i = 0; i < initialPoolSize; i++)
        {
            CreatePooledObject();
        }
        
        Debug.Log($"Initialized network object pool with {initialPoolSize} objects");
    }
    
    private NetworkObject CreatePooledObject()
    {
        if (!IsServer) return null;
        
        NetworkObject obj = Instantiate(prefab);
        obj.gameObject.SetActive(false);
        
        // Spawn network object but keep it inactive
        obj.Spawn(false);
        obj.gameObject.SetActive(false);
        
        availableObjects.Enqueue(obj);
        networkIdToObject[obj.NetworkObjectId] = obj;
        
        return obj;
    }
    
    [ServerRpc(RequireOwnership = false)]
    public void RequestObjectServerRpc(Vector3 position, Quaternion rotation, ulong requesterId)
    {
        NetworkObject obj = GetPooledObject();
        
        if (obj != null)
        {
            // Configure object
            obj.transform.position = position;
            obj.transform.rotation = rotation;
            obj.gameObject.SetActive(true);
            
            // Add to active set
            activeObjects.Add(obj);
            
            // Update network list
            var poolData = new PooledObjectData
            {
                networkId = obj.NetworkObjectId,
                isActive = true,
                position = position,
                rotation = rotation,
                spawnTime = (float)NetworkManager.Singleton.ServerTime.Time
            };
            
            pooledObjects.Add(poolData);
            
            // Notify clients
            ObjectSpawnedClientRpc(obj.NetworkObjectId, position, rotation);
        }
        else
        {
            Debug.LogWarning("No available objects in pool!");
        }
    }
    
    private NetworkObject GetPooledObject()
    {
        if (availableObjects.Count > 0)
        {
            return availableObjects.Dequeue();
        }
        else if (allowGrowth && activeObjects.Count < maxPoolSize)
        {
            return CreatePooledObject();
        }
        
        return null; // Pool exhausted
    }
    
    [ServerRpc(RequireOwnership = false)]
    public void ReturnObjectServerRpc(ulong networkId)
    {
        if (networkIdToObject.TryGetValue(networkId, out NetworkObject obj))
        {
            ReturnObjectToPool(obj);
        }
    }
    
    private void ReturnObjectToPool(NetworkObject obj)
    {
        if (!IsServer) return;
        
        // Deactivate object
        obj.gameObject.SetActive(false);
        
        // Remove from active set
        activeObjects.Remove(obj);
        availableObjects.Enqueue(obj);
        
        // Update network list
        for (int i = 0; i < pooledObjects.Count; i++)
        {
            if (pooledObjects[i].networkId == obj.NetworkObjectId)
            {
                var poolData = pooledObjects[i];
                poolData.isActive = false;
                pooledObjects[i] = poolData;
                break;
            }
        }
        
        // Notify clients
        ObjectReturnedClientRpc(obj.NetworkObjectId);
    }
    
    [ClientRpc]
    private void ObjectSpawnedClientRpc(ulong networkId, Vector3 position, Quaternion rotation)
    {
        if (networkIdToObject.TryGetValue(networkId, out NetworkObject obj))
        {
            obj.transform.position = position;
            obj.transform.rotation = rotation;
            obj.gameObject.SetActive(true);
        }
    }
    
    [ClientRpc]
    private void ObjectReturnedClientRpc(ulong networkId)
    {
        if (networkIdToObject.TryGetValue(networkId, out NetworkObject obj))
        {
            obj.gameObject.SetActive(false);
        }
    }
    
    private void OnPooledObjectsChanged(NetworkListEvent<PooledObjectData> changeEvent)
    {
        // Handle pool synchronization for late-joining clients
        switch (changeEvent.Type)
        {
            case NetworkListEvent<PooledObjectData>.EventType.Add:
                OnObjectAddedToPool(changeEvent.Value);
                break;
                
            case NetworkListEvent<PooledObjectData>.EventType.RemoveAt:
                OnObjectRemovedFromPool(changeEvent.PreviousValue);
                break;
                
            case NetworkListEvent<PooledObjectData>.EventType.Value:
                OnObjectDataChanged(changeEvent.Value);
                break;
        }
    }
    
    private void OnObjectAddedToPool(PooledObjectData data)
    {
        // Ensure client has the object reference
        if (!networkIdToObject.ContainsKey(data.networkId))
        {
            // Find the network object
            if (NetworkManager.Singleton.SpawnManager.SpawnedObjects.TryGetValue(data.networkId, out NetworkObject obj))
            {
                networkIdToObject[data.networkId] = obj;
            }
        }
    }
    
    private void OnObjectRemovedFromPool(PooledObjectData data)
    {
        // Clean up references
        networkIdToObject.Remove(data.networkId);
    }
    
    private void OnObjectDataChanged(PooledObjectData data)
    {
        if (networkIdToObject.TryGetValue(data.networkId, out NetworkObject obj))
        {
            obj.gameObject.SetActive(data.isActive);
            
            if (data.isActive)
            {
                obj.transform.position = data.position;
                obj.transform.rotation = data.rotation;
            }
        }
    }
    
    private void ClearPool()
    {
        // Clean up all pooled objects
        foreach (var obj in activeObjects)
        {
            if (obj != null)
            {
                if (obj.IsSpawned)
                {
                    obj.Despawn();
                }
                Destroy(obj.gameObject);
            }
        }
        
        while (availableObjects.Count > 0)
        {
            var obj = availableObjects.Dequeue();
            if (obj != null)
            {
                if (obj.IsSpawned)
                {
                    obj.Despawn();
                }
                Destroy(obj.gameObject);
            }
        }
        
        activeObjects.Clear();
        networkIdToObject.Clear();
        pooledObjects.Clear();
    }
    
    // Debug information
    public void LogPoolStatus()
    {
        Debug.Log($"Pool Status - Active: {activeObjects.Count}, Available: {availableObjects.Count}, Total: {activeObjects.Count + availableObjects.Count}");
    }
}
```

### Lag Compensation System

```csharp
using Unity.Netcode;
using Unity.Collections;
using UnityEngine;
using System.Collections.Generic;

public class LagCompensationManager : NetworkBehaviour
{
    [Header("Lag Compensation Settings")]
    [SerializeField] private float historyDuration = 1f; // Keep 1 second of history
    [SerializeField] private float snapshotRate = 20f; // 20 snapshots per second
    [SerializeField] private bool enableClientPrediction = true;
    [SerializeField] private bool enableServerReconciliation = true;
    
    // Player state history for lag compensation
    private Dictionary<ulong, List<PlayerSnapshot>> playerHistories = new Dictionary<ulong, List<PlayerSnapshot>>();
    private Dictionary<ulong, List<InputSnapshot>> inputHistories = new Dictionary<ulong, List<InputSnapshot>>();
    
    public struct PlayerSnapshot
    {
        public double timestamp;
        public Vector3 position;
        public Quaternion rotation;
        public Vector3 velocity;
        public bool isGrounded;
        public float health;
    }
    
    public struct InputSnapshot
    {
        public double timestamp;
        public Vector2 movement;
        public bool jump;
        public bool fire;
        public Vector3 aimDirection;
        public uint inputSequence;
    }
    
    private void Awake()
    {
        // Initialize snapshot timer
        InvokeRepeating(nameof(TakeSnapshot), 0f, 1f / snapshotRate);
    }
    
    public override void OnNetworkSpawn()
    {
        if (IsServer)
        {
            // Server handles authoritative state
            NetworkManager.Singleton.OnClientConnectedCallback += OnClientConnected;
            NetworkManager.Singleton.OnClientDisconnectCallback += OnClientDisconnected;
        }
    }
    
    public override void OnNetworkDespawn()
    {
        if (NetworkManager.Singleton != null)
        {
            NetworkManager.Singleton.OnClientConnectedCallback -= OnClientConnected;
            NetworkManager.Singleton.OnClientDisconnectCallback -= OnClientDisconnected;
        }
        
        CancelInvoke(nameof(TakeSnapshot));
    }
    
    private void OnClientConnected(ulong clientId)
    {
        if (IsServer)
        {
            playerHistories[clientId] = new List<PlayerSnapshot>();
            inputHistories[clientId] = new List<InputSnapshot>();
        }
    }
    
    private void OnClientDisconnected(ulong clientId)
    {
        if (IsServer)
        {
            playerHistories.Remove(clientId);
            inputHistories.Remove(clientId);
        }
    }
    
    private void TakeSnapshot()
    {
        if (!IsServer) return;
        
        double currentTime = NetworkManager.Singleton.ServerTime.Time;
        
        // Take snapshot of all players
        foreach (var client in NetworkManager.Singleton.ConnectedClients)
        {
            ulong clientId = client.Key;
            var playerObject = client.Value.PlayerObject;
            
            if (playerObject != null)
            {
                var playerController = playerObject.GetComponent<NetworkedPlayerController>();
                if (playerController != null)
                {
                    TakePlayerSnapshot(clientId, playerController, currentTime);
                }
            }
        }
        
        // Clean up old snapshots
        CleanupOldSnapshots(currentTime);
    }
    
    private void TakePlayerSnapshot(ulong clientId, NetworkedPlayerController player, double timestamp)
    {
        if (!playerHistories.ContainsKey(clientId)) return;
        
        var snapshot = new PlayerSnapshot
        {
            timestamp = timestamp,
            position = player.transform.position,
            rotation = player.transform.rotation,
            velocity = player.GetComponent<Rigidbody>()?.velocity ?? Vector3.zero,
            isGrounded = player.GetComponent<CharacterController>()?.isGrounded ?? false,
            // health = player.GetHealth() // Implement as needed
        };
        
        playerHistories[clientId].Add(snapshot);
    }
    
    private void CleanupOldSnapshots(double currentTime)
    {
        double cutoffTime = currentTime - historyDuration;
        
        foreach (var history in playerHistories.Values)
        {
            history.RemoveAll(snapshot => snapshot.timestamp < cutoffTime);
        }
        
        foreach (var history in inputHistories.Values)
        {
            history.RemoveAll(input => input.timestamp < cutoffTime);
        }
    }
    
    // Client prediction methods
    [ServerRpc]
    public void SubmitInputServerRpc(InputSnapshot input, ulong clientId)
    {
        if (!inputHistories.ContainsKey(clientId))
        {
            inputHistories[clientId] = new List<InputSnapshot>();
        }
        
        inputHistories[clientId].Add(input);
        
        // Process input with lag compensation
        ProcessInputWithLagCompensation(input, clientId);
        
        // Send authoritative state back to client
        if (enableServerReconciliation)
        {
            SendServerReconciliationClientRpc(input.inputSequence, GetPlayerSnapshot(clientId));
        }
    }
    
    private void ProcessInputWithLagCompensation(InputSnapshot input, ulong clientId)
    {
        // Calculate client's latency
        double clientTime = input.timestamp;
        double serverTime = NetworkManager.Singleton.ServerTime.Time;
        double latency = serverTime - clientTime;
        
        // Rewind world state to client's time
        double compensatedTime = serverTime - latency;
        RewindWorldState(compensatedTime, clientId);
        
        // Process the input
        ApplyPlayerInput(input, clientId);
        
        // Restore world state
        RestoreWorldState();
    }
    
    private void RewindWorldState(double targetTime, ulong excludeClientId)
    {
        // Rewind all players except the one we're processing
        foreach (var kvp in playerHistories)
        {
            ulong clientId = kvp.Key;
            if (clientId == excludeClientId) continue;
            
            var history = kvp.Value;
            var snapshot = GetSnapshotAtTime(history, targetTime);
            
            if (snapshot.HasValue)
            {
                ApplySnapshotToPlayer(clientId, snapshot.Value);
            }
        }
    }
    
    private PlayerSnapshot? GetSnapshotAtTime(List<PlayerSnapshot> history, double targetTime)
    {
        if (history.Count == 0) return null;
        
        // Find the two snapshots to interpolate between
        PlayerSnapshot? before = null;
        PlayerSnapshot? after = null;
        
        for (int i = 0; i < history.Count; i++)
        {
            if (history[i].timestamp <= targetTime)
            {
                before = history[i];
            }
            else
            {
                after = history[i];
                break;
            }
        }
        
        if (!before.HasValue) return history.Count > 0 ? history[0] : null;
        if (!after.HasValue) return before;
        
        // Interpolate between snapshots
        double t = (targetTime - before.Value.timestamp) / (after.Value.timestamp - before.Value.timestamp);
        t = Mathf.Clamp01((float)t);
        
        return new PlayerSnapshot
        {
            timestamp = targetTime,
            position = Vector3.Lerp(before.Value.position, after.Value.position, (float)t),
            rotation = Quaternion.Lerp(before.Value.rotation, after.Value.rotation, (float)t),
            velocity = Vector3.Lerp(before.Value.velocity, after.Value.velocity, (float)t),
            isGrounded = after.Value.isGrounded, // Use latest boolean state
            health = after.Value.health
        };
    }
    
    private void ApplySnapshotToPlayer(ulong clientId, PlayerSnapshot snapshot)
    {
        if (NetworkManager.Singleton.ConnectedClients.TryGetValue(clientId, out var client))
        {
            if (client.PlayerObject != null)
            {
                client.PlayerObject.transform.position = snapshot.position;
                client.PlayerObject.transform.rotation = snapshot.rotation;
                
                var rb = client.PlayerObject.GetComponent<Rigidbody>();
                if (rb != null)
                {
                    rb.velocity = snapshot.velocity;
                }
            }
        }
    }
    
    private void RestoreWorldState()
    {
        // Restore all players to their current authoritative state
        foreach (var client in NetworkManager.Singleton.ConnectedClients)
        {
            ulong clientId = client.Key;
            if (playerHistories.ContainsKey(clientId) && playerHistories[clientId].Count > 0)
            {
                var latestSnapshot = playerHistories[clientId][playerHistories[clientId].Count - 1];
                ApplySnapshotToPlayer(clientId, latestSnapshot);
            }
        }
    }
    
    private void ApplyPlayerInput(InputSnapshot input, ulong clientId)
    {
        if (NetworkManager.Singleton.ConnectedClients.TryGetValue(clientId, out var client))
        {
            var playerController = client.PlayerObject?.GetComponent<NetworkedPlayerController>();
            if (playerController != null)
            {
                // Apply movement input
                Vector3 movement = new Vector3(input.movement.x, 0f, input.movement.y);
                // Apply movement logic here
                
                // Handle jump
                if (input.jump)
                {
                    // Apply jump logic here
                }
                
                // Handle weapon fire
                if (input.fire)
                {
                    ProcessWeaponFire(input.aimDirection, clientId, input.timestamp);
                }
            }
        }
    }
    
    private void ProcessWeaponFire(Vector3 aimDirection, ulong clientId, double fireTime)
    {
        // Process weapon fire with hit detection using rewound world state
        // This ensures hits are calculated based on where enemies were when the client fired
        
        Vector3 origin = GetPlayerPosition(clientId);
        if (Physics.Raycast(origin, aimDirection, out RaycastHit hit, 100f))
        {
            // Process hit on rewound target
            var targetController = hit.collider.GetComponent<NetworkedPlayerController>();
            if (targetController != null)
            {
                // Apply damage
                targetController.TakeDamageServerRpc(25f, clientId);
            }
        }
    }
    
    private Vector3 GetPlayerPosition(ulong clientId)
    {
        if (NetworkManager.Singleton.ConnectedClients.TryGetValue(clientId, out var client))
        {
            return client.PlayerObject?.transform.position ?? Vector3.zero;
        }
        return Vector3.zero;
    }
    
    private PlayerSnapshot GetPlayerSnapshot(ulong clientId)
    {
        if (playerHistories.ContainsKey(clientId) && playerHistories[clientId].Count > 0)
        {
            return playerHistories[clientId][playerHistories[clientId].Count - 1];
        }
        
        return new PlayerSnapshot
        {
            timestamp = NetworkManager.Singleton.ServerTime.Time,
            position = GetPlayerPosition(clientId)
        };
    }
    
    [ClientRpc]
    private void SendServerReconciliationClientRpc(uint inputSequence, PlayerSnapshot serverState)
    {
        // Client receives authoritative state for reconciliation
        OnServerReconciliation(inputSequence, serverState);
    }
    
    private void OnServerReconciliation(uint inputSequence, PlayerSnapshot serverState)
    {
        if (!IsOwner || !enableServerReconciliation) return;
        
        // Compare client prediction with server state
        // If there's a significant difference, correct the client state
        
        float positionError = Vector3.Distance(transform.position, serverState.position);
        float rotationError = Quaternion.Angle(transform.rotation, serverState.rotation);
        
        const float POSITION_THRESHOLD = 0.5f;
        const float ROTATION_THRESHOLD = 5f;
        
        if (positionError > POSITION_THRESHOLD || rotationError > ROTATION_THRESHOLD)
        {
            // Snap to server state
            transform.position = serverState.position;
            transform.rotation = serverState.rotation;
            
            // Re-apply inputs that happened after the reconciled input
            ReapplyInputsAfterSequence(inputSequence);
            
            Debug.Log($"Client reconciliation: Position error {positionError:F2}m, Rotation error {rotationError:F2}°");
        }
    }
    
    private void ReapplyInputsAfterSequence(uint sequenceNumber)
    {
        // Re-apply any inputs that were sent after the reconciled input
        // This maintains client prediction while correcting for server discrepancies
        
        ulong clientId = NetworkManager.Singleton.LocalClientId;
        if (inputHistories.ContainsKey(clientId))
        {
            var inputs = inputHistories[clientId];
            foreach (var input in inputs)
            {
                if (input.inputSequence > sequenceNumber)
                {
                    // Re-apply this input locally
                    ApplyInputLocally(input);
                }
            }
        }
    }
    
    private void ApplyInputLocally(InputSnapshot input)
    {
        // Apply input to local player for prediction
        // This should match the server-side input processing logic
        
        Vector3 movement = new Vector3(input.movement.x, 0f, input.movement.y);
        // Apply movement logic locally
        
        if (input.jump)
        {
            // Apply jump logic locally
        }
    }
}
```

This comprehensive guide provides advanced multiplayer networking implementation using Unity Netcode, including client-server synchronization, lag compensation, and object pooling for scalable multiplayer games.