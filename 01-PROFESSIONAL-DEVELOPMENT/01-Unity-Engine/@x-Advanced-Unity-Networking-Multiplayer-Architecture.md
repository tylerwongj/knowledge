# @x-Advanced-Unity-Networking-Multiplayer-Architecture

## 🎯 Learning Objectives

- Master Unity Netcode for GameObjects (NGO) for scalable multiplayer architecture
- Implement client-server networking with authoritative server design
- Create robust synchronization systems for game state and player actions
- Design lag compensation, prediction, and rollback systems for smooth gameplay

## 🔧 Core Networking Architecture

### Netcode for GameObjects Foundation

```csharp
using Unity.Netcode;
using Unity.Collections;
using UnityEngine;
using System;
using System.Collections.Generic;

// Base networked game object with essential networking features
public abstract class NetworkedGameObject : NetworkBehaviour
{
    [Header("Network Configuration")]
    [SerializeField] protected float networkUpdateRate = 20f;
    [SerializeField] protected bool enablePrediction = true;
    [SerializeField] protected float reconciliationThreshold = 0.1f;
    
    // Network variables for state synchronization
    protected NetworkVariable<Vector3> networkPosition = new NetworkVariable<Vector3>();
    protected NetworkVariable<Quaternion> networkRotation = new NetworkVariable<Quaternion>();
    protected NetworkVariable<int> networkHealth = new NetworkVariable<int>();
    
    // Client-side prediction data
    protected struct PredictionData
    {
        public uint tick;
        public Vector3 position;
        public Quaternion rotation;
        public Vector3 velocity;
        public float timestamp;
    }
    
    protected Queue<PredictionData> predictionHistory = new Queue<PredictionData>();
    protected uint currentTick = 0;
    
    public override void OnNetworkSpawn()
    {
        base.OnNetworkSpawn();
        
        if (IsOwner)
        {
            // Initialize prediction system for owned objects
            InvokeRepeating(nameof(SendPositionUpdate), 0f, 1f / networkUpdateRate);
        }
        else
        {
            // Subscribe to network variable changes for remote objects
            networkPosition.OnValueChanged += OnNetworkPositionChanged;
            networkRotation.OnValueChanged += OnNetworkRotationChanged;
            networkHealth.OnValueChanged += OnNetworkHealthChanged;
        }
    }
    
    protected virtual void OnNetworkPositionChanged(Vector3 previousValue, Vector3 newValue)
    {
        if (!IsOwner)
        {
            // Interpolate to smooth remote object movement
            StartCoroutine(InterpolatePosition(transform.position, newValue));
        }
    }
    
    protected virtual void OnNetworkRotationChanged(Quaternion previousValue, Quaternion newValue)
    {
        if (!IsOwner)
        {
            StartCoroutine(InterpolateRotation(transform.rotation, newValue));
        }
    }
    
    protected virtual void OnNetworkHealthChanged(int previousValue, int newValue)
    {
        OnHealthChanged?.Invoke(previousValue, newValue);
    }
    
    // Events for game logic
    public event Action<int, int> OnHealthChanged;
    
    protected virtual void SendPositionUpdate()
    {
        if (IsOwner && IsSpawned)
        {
            currentTick++;
            
            // Store prediction data
            var predictionData = new PredictionData
            {
                tick = currentTick,
                position = transform.position,
                rotation = transform.rotation,
                velocity = GetComponent<Rigidbody>()?.velocity ?? Vector3.zero,
                timestamp = Time.time
            };
            
            predictionHistory.Enqueue(predictionData);
            
            // Limit history size
            while (predictionHistory.Count > 100)
            {
                predictionHistory.Dequeue();
            }
            
            // Send update to server
            UpdatePositionServerRpc(transform.position, transform.rotation, currentTick);
        }
    }
    
    [ServerRpc(RequireOwnership = true)]
    protected virtual void UpdatePositionServerRpc(Vector3 position, Quaternion rotation, uint tick)
    {
        // Server authority - validate movement
        if (IsValidMovement(position, rotation))
        {
            networkPosition.Value = position;
            networkRotation.Value = rotation;
            
            // Send reconciliation data back to client
            if (enablePrediction)
            {
                ReconcilePositionClientRpc(position, rotation, tick);
            }
        }
    }
    
    [ClientRpc]
    protected virtual void ReconcilePositionClientRpc(Vector3 serverPosition, Quaternion serverRotation, uint tick)
    {
        if (!IsOwner) return;
        
        // Find the prediction that corresponds to this server update
        var predictionArray = predictionHistory.ToArray();
        
        for (int i = 0; i < predictionArray.Length; i++)
        {
            if (predictionArray[i].tick == tick)
            {
                float positionDifference = Vector3.Distance(predictionArray[i].position, serverPosition);
                
                if (positionDifference > reconciliationThreshold)
                {
                    // Reconciliation needed - snap to server position and replay predictions
                    transform.position = serverPosition;
                    transform.rotation = serverRotation;
                    
                    // Replay predictions after this tick
                    ReplayPredictions(tick);
                }
                break;
            }
        }
    }
    
    protected virtual void ReplayPredictions(uint fromTick)
    {
        var predictionArray = predictionHistory.ToArray();
        
        for (int i = 0; i < predictionArray.Length; i++)
        {
            if (predictionArray[i].tick > fromTick)
            {
                // Re-apply this prediction
                ApplyPredictionMovement(predictionArray[i]);
            }
        }
    }
    
    protected virtual void ApplyPredictionMovement(PredictionData prediction)
    {
        // Override in derived classes to implement specific movement logic
    }
    
    protected virtual bool IsValidMovement(Vector3 newPosition, Quaternion newRotation)
    {
        // Server-side movement validation
        float distance = Vector3.Distance(transform.position, newPosition);
        float maxDistance = GetMaxMovementDistance();
        
        return distance <= maxDistance;
    }
    
    protected virtual float GetMaxMovementDistance()
    {
        return 10f; // Override in derived classes
    }
    
    private System.Collections.IEnumerator InterpolatePosition(Vector3 from, Vector3 to)
    {
        float duration = 1f / networkUpdateRate;
        float elapsed = 0f;
        
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float t = elapsed / duration;
            transform.position = Vector3.Lerp(from, to, t);
            yield return null;
        }
    }
    
    private System.Collections.IEnumerator InterpolateRotation(Quaternion from, Quaternion to)
    {
        float duration = 1f / networkUpdateRate;
        float elapsed = 0f;
        
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float t = elapsed / duration;
            transform.rotation = Quaternion.Lerp(from, to, t);
            yield return null;
        }
    }
}

// Advanced player controller with networking
public class NetworkedPlayerController : NetworkedGameObject
{
    [Header("Player Movement")]
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float jumpForce = 10f;
    [SerializeField] private float groundCheckRadius = 0.3f;
    [SerializeField] private LayerMask groundLayerMask = 1;
    
    private Rigidbody playerRigidbody;
    private bool isGrounded;
    private Vector2 inputVector;
    
    // Input handling with client-side prediction
    private struct InputData
    {
        public uint tick;
        public Vector2 movement;
        public bool jump;
        public float timestamp;
    }
    
    private Queue<InputData> inputHistory = new Queue<InputData>();
    private InputData currentInput;
    
    protected override void Awake()
    {
        base.Awake();
        playerRigidbody = GetComponent<Rigidbody>();
    }
    
    void Update()
    {
        if (!IsOwner) return;
        
        HandleInput();
        
        if (enablePrediction)
        {
            ApplyMovementPrediction();
        }
    }
    
    void FixedUpdate()
    {
        if (!IsOwner) return;
        
        // Ground check
        isGrounded = Physics.CheckSphere(
            transform.position + Vector3.down * 0.1f,
            groundCheckRadius,
            groundLayerMask
        );
    }
    
    private void HandleInput()
    {
        currentInput.movement = new Vector2(
            Input.GetAxis("Horizontal"),
            Input.GetAxis("Vertical")
        );
        
        currentInput.jump = Input.GetButtonDown("Jump") && isGrounded;
        currentInput.tick = currentTick;
        currentInput.timestamp = Time.time;
        
        inputHistory.Enqueue(currentInput);
        
        // Send input to server
        ProcessInputServerRpc(currentInput.movement, currentInput.jump, currentInput.tick);
        
        // Limit input history
        while (inputHistory.Count > 60) // 1 second at 60 FPS
        {
            inputHistory.Dequeue();
        }
    }
    
    private void ApplyMovementPrediction()
    {
        // Apply movement immediately for responsive controls
        Vector3 movement = new Vector3(currentInput.movement.x, 0f, currentInput.movement.y);
        movement = transform.TransformDirection(movement) * moveSpeed;
        
        playerRigidbody.velocity = new Vector3(movement.x, playerRigidbody.velocity.y, movement.z);
        
        if (currentInput.jump)
        {
            playerRigidbody.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
        }
    }
    
    [ServerRpc(RequireOwnership = true)]
    private void ProcessInputServerRpc(Vector2 movement, bool jump, uint tick)
    {
        // Server processes input with authority
        Vector3 moveDirection = new Vector3(movement.x, 0f, movement.y);
        moveDirection = transform.TransformDirection(moveDirection) * moveSpeed;
        
        var rb = GetComponent<Rigidbody>();
        rb.velocity = new Vector3(moveDirection.x, rb.velocity.y, moveDirection.z);
        
        if (jump && IsGroundedServer())
        {
            rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
        }
        
        // Update network variables
        networkPosition.Value = transform.position;
        networkRotation.Value = transform.rotation;
        
        // Send reconciliation data
        ReconcileMovementClientRpc(transform.position, rb.velocity, tick);
    }
    
    [ClientRpc]
    private void ReconcileMovementClientRpc(Vector3 serverPosition, Vector3 serverVelocity, uint tick)
    {
        if (!IsOwner) return;
        
        float positionError = Vector3.Distance(transform.position, serverPosition);
        
        if (positionError > reconciliationThreshold)
        {
            // Reconcile position
            transform.position = serverPosition;
            playerRigidbody.velocity = serverVelocity;
            
            // Replay inputs after this tick
            ReplayInputs(tick);
        }
    }
    
    private void ReplayInputs(uint fromTick)
    {
        var inputArray = inputHistory.ToArray();
        
        foreach (var input in inputArray)
        {
            if (input.tick > fromTick)
            {
                // Re-apply this input
                Vector3 movement = new Vector3(input.movement.x, 0f, input.movement.y);
                movement = transform.TransformDirection(movement) * moveSpeed;
                playerRigidbody.velocity = new Vector3(movement.x, playerRigidbody.velocity.y, movement.z);
                
                if (input.jump)
                {
                    playerRigidbody.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
                }
            }
        }
    }
    
    private bool IsGroundedServer()
    {
        return Physics.CheckSphere(
            transform.position + Vector3.down * 0.1f,
            groundCheckRadius,
            groundLayerMask
        );
    }
    
    protected override float GetMaxMovementDistance()
    {
        return moveSpeed * (1f / networkUpdateRate) * 1.5f; // Allow some tolerance
    }
    
    protected override void ApplyPredictionMovement(PredictionData prediction)
    {
        // Find corresponding input for this prediction
        var inputArray = inputHistory.ToArray();
        
        foreach (var input in inputArray)
        {
            if (input.tick == prediction.tick)
            {
                Vector3 movement = new Vector3(input.movement.x, 0f, input.movement.y);
                movement = transform.TransformDirection(movement) * moveSpeed;
                playerRigidbody.velocity = new Vector3(movement.x, prediction.velocity.y, movement.z);
                break;
            }
        }
    }
}
```

### Advanced Game State Management

```csharp
using Unity.Netcode;
using Unity.Collections;
using UnityEngine;
using System;
using System.Collections.Generic;
using System.Linq;

// Network game manager with comprehensive state synchronization
public class NetworkGameManager : NetworkBehaviour
{
    [Header("Game Configuration")]
    [SerializeField] private int maxPlayers = 8;
    [SerializeField] private float matchDuration = 300f; // 5 minutes
    [SerializeField] private int scoreToWin = 10;
    
    // Network variables for game state
    private NetworkVariable<GameState> currentGameState = new NetworkVariable<GameState>(GameState.Lobby);
    private NetworkVariable<float> matchTimeRemaining = new NetworkVariable<float>();
    private NetworkVariable<int> playersReady = new NetworkVariable<int>();
    
    // Player management
    private NetworkList<PlayerData> connectedPlayers;
    private NetworkVariable<ulong> matchWinnerId = new NetworkVariable<ulong>();
    
    // Events
    public event Action<GameState, GameState> OnGameStateChanged;
    public event Action<float> OnMatchTimeChanged;
    public event Action<PlayerData> OnPlayerJoined;
    public event Action<PlayerData> OnPlayerLeft;
    public event Action<ulong> OnMatchEnded;
    
    public enum GameState
    {
        Lobby,
        WaitingForPlayers,
        CountDown,
        InGame,
        GameEnded,
        Disconnected
    }
    
    private void Awake()
    {
        connectedPlayers = new NetworkList<PlayerData>();
    }
    
    public override void OnNetworkSpawn()
    {
        if (IsServer)
        {
            // Server initialization
            currentGameState.Value = GameState.Lobby;
            matchTimeRemaining.Value = matchDuration;
            
            NetworkManager.OnClientConnectedCallback += OnClientConnected;
            NetworkManager.OnClientDisconnectCallback += OnClientDisconnected;
        }
        
        // Client subscriptions
        currentGameState.OnValueChanged += OnGameStateValueChanged;
        matchTimeRemaining.OnValueChanged += OnMatchTimeValueChanged;
        connectedPlayers.OnListChanged += OnPlayersListChanged;
    }
    
    public override void OnNetworkDespawn()
    {
        if (IsServer)
        {
            NetworkManager.OnClientConnectedCallback -= OnClientConnected;
            NetworkManager.OnClientDisconnectCallback -= OnClientDisconnected;
        }
    }
    
    void Update()
    {
        if (IsServer && currentGameState.Value == GameState.InGame)
        {
            UpdateMatchTime();
            CheckWinConditions();
        }
    }
    
    private void OnClientConnected(ulong clientId)
    {
        Debug.Log($"Client {clientId} connected");
        
        // Add player to the list
        var newPlayer = new PlayerData
        {
            clientId = clientId,
            playerName = $"Player_{clientId}",
            score = 0,
            isReady = false,
            isAlive = true
        };
        
        connectedPlayers.Add(newPlayer);
        
        // Check if we can start the match
        if (connectedPlayers.Count >= 2 && currentGameState.Value == GameState.Lobby)
        {
            TransitionToState(GameState.WaitingForPlayers);
        }
    }
    
    private void OnClientDisconnected(ulong clientId)
    {
        Debug.Log($"Client {clientId} disconnected");
        
        // Remove player from list
        for (int i = connectedPlayers.Count - 1; i >= 0; i--)
        {
            if (connectedPlayers[i].clientId == clientId)
            {
                connectedPlayers.RemoveAt(i);
                break;
            }
        }
        
        // Handle game state if needed
        if (currentGameState.Value == GameState.InGame && connectedPlayers.Count < 2)
        {
            EndMatch();
        }
    }
    
    private void UpdateMatchTime()
    {
        matchTimeRemaining.Value = Mathf.Max(0f, matchTimeRemaining.Value - Time.deltaTime);
        
        if (matchTimeRemaining.Value <= 0f)
        {
            EndMatch();
        }
    }
    
    private void CheckWinConditions()
    {
        foreach (var player in connectedPlayers)
        {
            if (player.score >= scoreToWin)
            {
                matchWinnerId.Value = player.clientId;
                EndMatch();
                return;
            }
        }
    }
    
    public void TransitionToState(GameState newState)
    {
        if (!IsServer) return;
        
        var oldState = currentGameState.Value;
        currentGameState.Value = newState;
        
        // Handle state-specific logic
        switch (newState)
        {
            case GameState.CountDown:
                StartCoroutine(CountdownCoroutine());
                break;
            case GameState.InGame:
                StartMatch();
                break;
            case GameState.GameEnded:
                HandleGameEnd();
                break;
        }
    }
    
    private System.Collections.IEnumerator CountdownCoroutine()
    {
        for (int i = 3; i > 0; i--)
        {
            ShowCountdownClientRpc(i);
            yield return new WaitForSeconds(1f);
        }
        
        ShowCountdownClientRpc(0); // "GO!"
        yield return new WaitForSeconds(1f);
        
        TransitionToState(GameState.InGame);
    }
    
    [ClientRpc]
    private void ShowCountdownClientRpc(int count)
    {
        // UI will handle displaying the countdown
        Debug.Log(count > 0 ? count.ToString() : "GO!");
    }
    
    private void StartMatch()
    {
        matchTimeRemaining.Value = matchDuration;
        
        // Reset all player scores and states
        for (int i = 0; i < connectedPlayers.Count; i++)
        {
            var player = connectedPlayers[i];
            player.score = 0;
            player.isAlive = true;
            connectedPlayers[i] = player;
        }
    }
    
    private void EndMatch()
    {
        TransitionToState(GameState.GameEnded);
    }
    
    private void HandleGameEnd()
    {
        // Find winner (highest score or last alive)
        if (matchWinnerId.Value == 0)
        {
            var winner = connectedPlayers.OrderByDescending(p => p.score).FirstOrDefault();
            if (winner.clientId != 0)
            {
                matchWinnerId.Value = winner.clientId;
            }
        }
        
        // Schedule return to lobby
        StartCoroutine(ReturnToLobbyCoroutine());
    }
    
    private System.Collections.IEnumerator ReturnToLobbyCoroutine()
    {
        yield return new WaitForSeconds(10f); // Show results for 10 seconds
        
        // Reset game state
        matchWinnerId.Value = 0;
        playersReady.Value = 0;
        TransitionToState(GameState.Lobby);
    }
    
    // Client-callable methods
    [ServerRpc(RequireOwnership = false)]
    public void SetPlayerReadyServerRpc(bool ready, ServerRpcParams serverRpcParams = default)
    {
        ulong clientId = serverRpcParams.Receive.SenderClientId;
        
        // Update player ready state
        for (int i = 0; i < connectedPlayers.Count; i++)
        {
            var player = connectedPlayers[i];
            if (player.clientId == clientId)
            {
                bool wasReady = player.isReady;
                player.isReady = ready;
                connectedPlayers[i] = player;
                
                // Update ready count
                if (ready && !wasReady)
                    playersReady.Value++;
                else if (!ready && wasReady)
                    playersReady.Value--;
                
                break;
            }
        }
        
        // Check if all players are ready
        if (playersReady.Value == connectedPlayers.Count && 
            connectedPlayers.Count >= 2 && 
            currentGameState.Value == GameState.WaitingForPlayers)
        {
            TransitionToState(GameState.CountDown);
        }
    }
    
    [ServerRpc(RequireOwnership = false)]
    public void UpdatePlayerScoreServerRpc(int scoreChange, ServerRpcParams serverRpcParams = default)
    {
        ulong clientId = serverRpcParams.Receive.SenderClientId;
        
        for (int i = 0; i < connectedPlayers.Count; i++)
        {
            var player = connectedPlayers[i];
            if (player.clientId == clientId)
            {
                player.score += scoreChange;
                connectedPlayers[i] = player;
                break;
            }
        }
    }
    
    [ServerRpc(RequireOwnership = false)]
    public void SetPlayerAliveServerRpc(bool alive, ServerRpcParams serverRpcParams = default)
    {
        ulong clientId = serverRpcParams.Receive.SenderClientId;
        
        for (int i = 0; i < connectedPlayers.Count; i++)
        {
            var player = connectedPlayers[i];
            if (player.clientId == clientId)
            {
                player.isAlive = alive;
                connectedPlayers[i] = player;
                break;
            }
        }
        
        // Check if only one player remains
        if (currentGameState.Value == GameState.InGame)
        {
            var alivePlayers = connectedPlayers.Where(p => p.isAlive).ToList();
            if (alivePlayers.Count <= 1)
            {
                if (alivePlayers.Count == 1)
                {
                    matchWinnerId.Value = alivePlayers[0].clientId;
                }
                EndMatch();
            }
        }
    }
    
    // Event handlers
    private void OnGameStateValueChanged(GameState oldState, GameState newState)
    {
        OnGameStateChanged?.Invoke(oldState, newState);
    }
    
    private void OnMatchTimeValueChanged(float oldTime, float newTime)
    {
        OnMatchTimeChanged?.Invoke(newTime);
    }
    
    private void OnPlayersListChanged(NetworkListEvent<PlayerData> changeEvent)
    {
        switch (changeEvent.Type)
        {
            case NetworkListEvent<PlayerData>.EventType.Add:
                OnPlayerJoined?.Invoke(changeEvent.Value);
                break;
            case NetworkListEvent<PlayerData>.EventType.Remove:
                OnPlayerLeft?.Invoke(changeEvent.Value);
                break;
        }
    }
    
    // Public accessors
    public GameState CurrentGameState => currentGameState.Value;
    public float MatchTimeRemaining => matchTimeRemaining.Value;
    public IReadOnlyList<PlayerData> ConnectedPlayers => connectedPlayers;
    public ulong MatchWinnerId => matchWinnerId.Value;
}

// Player data structure
[System.Serializable]
public struct PlayerData : INetworkSerializable, IEquatable<PlayerData>
{
    public ulong clientId;
    public FixedString64Bytes playerName;
    public int score;
    public bool isReady;
    public bool isAlive;
    
    public void NetworkSerialize<T>(BufferSerializer<T> serializer) where T : IReaderWriter
    {
        serializer.SerializeValue(ref clientId);
        serializer.SerializeValue(ref playerName);
        serializer.SerializeValue(ref score);
        serializer.SerializeValue(ref isReady);
        serializer.SerializeValue(ref isAlive);
    }
    
    public bool Equals(PlayerData other)
    {
        return clientId == other.clientId;
    }
    
    public override int GetHashCode()
    {
        return clientId.GetHashCode();
    }
}
```

### Lag Compensation and Rollback System

```csharp
using Unity.Netcode;
using UnityEngine;
using System.Collections.Generic;
using System.Linq;

// Advanced lag compensation system
public class LagCompensationManager : NetworkBehaviour
{
    [Header("Compensation Settings")]
    [SerializeField] private float maxCompensationTime = 0.5f;
    [SerializeField] private int maxHistoryFrames = 128;
    [SerializeField] private bool enableRollback = true;
    
    // Snapshot data for rollback
    private struct EntitySnapshot
    {
        public uint tick;
        public float timestamp;
        public Vector3 position;
        public Quaternion rotation;
        public bool isAlive;
        public float health;
    }
    
    private Dictionary<ulong, Queue<EntitySnapshot>> entityHistories = 
        new Dictionary<ulong, Queue<EntitySnapshot>>();
    
    private uint currentServerTick = 0;
    
    public override void OnNetworkSpawn()
    {
        if (IsServer)
        {
            // Start server tick updates
            InvokeRepeating(nameof(UpdateServerTick), 0f, Time.fixedDeltaTime);
        }
    }
    
    private void UpdateServerTick()
    {
        currentServerTick++;
        
        // Store snapshots of all networked entities
        var networkedObjects = FindObjectsOfType<NetworkedGameObject>();
        
        foreach (var obj in networkedObjects)
        {
            if (obj.IsSpawned)
            {
                StoreEntitySnapshot(obj);
            }
        }
    }
    
    private void StoreEntitySnapshot(NetworkedGameObject entity)
    {
        ulong networkId = entity.NetworkObjectId;
        
        if (!entityHistories.ContainsKey(networkId))
        {
            entityHistories[networkId] = new Queue<EntitySnapshot>();
        }
        
        var snapshot = new EntitySnapshot
        {
            tick = currentServerTick,
            timestamp = Time.time,
            position = entity.transform.position,
            rotation = entity.transform.rotation,
            isAlive = entity.gameObject.activeInHierarchy,
            health = entity.GetComponent<Health>()?.CurrentHealth ?? 100f
        };
        
        entityHistories[networkId].Enqueue(snapshot);
        
        // Limit history size
        while (entityHistories[networkId].Count > maxHistoryFrames)
        {
            entityHistories[networkId].Dequeue();
        }
    }
    
    // Rollback entities to a specific timestamp for hit validation
    public RollbackState RollbackToTimestamp(float targetTimestamp)
    {
        if (!IsServer || !enableRollback) return null;
        
        var rollbackState = new RollbackState();
        
        foreach (var kvp in entityHistories)
        {
            ulong networkId = kvp.Key;
            var history = kvp.Value;
            
            // Find the snapshot closest to the target timestamp
            var snapshots = history.ToArray();
            EntitySnapshot? targetSnapshot = null;
            
            for (int i = snapshots.Length - 1; i >= 0; i--)
            {
                if (snapshots[i].timestamp <= targetTimestamp)
                {
                    targetSnapshot = snapshots[i];
                    break;
                }
            }
            
            if (targetSnapshot.HasValue)
            {
                var networkObject = NetworkManager.SpawnManager.SpawnedObjects[networkId];
                if (networkObject != null)
                {
                    // Store current state for restoration
                    rollbackState.StoreCurrentState(networkId, networkObject.transform);
                    
                    // Apply historical state
                    networkObject.transform.position = targetSnapshot.Value.position;
                    networkObject.transform.rotation = targetSnapshot.Value.rotation;
                    
                    // Update physics
                    var rb = networkObject.GetComponent<Rigidbody>();
                    if (rb != null)
                    {
                        rb.position = targetSnapshot.Value.position;
                        rb.rotation = targetSnapshot.Value.rotation;
                    }
                }
            }
        }
        
        return rollbackState;
    }
    
    // Restore entities to their current state after rollback
    public void RestoreFromRollback(RollbackState rollbackState)
    {
        if (rollbackState != null)
        {
            rollbackState.RestoreStates();
        }
    }
    
    // Hit validation with lag compensation
    [ServerRpc(RequireOwnership = false)]
    public void ValidateHitServerRpc(ulong targetId, Vector3 hitPosition, float clientTimestamp, 
                                   ServerRpcParams serverRpcParams = default)
    {
        float ping = GetClientPing(serverRpcParams.Receive.SenderClientId);
        float compensatedTimestamp = clientTimestamp - ping;
        
        // Don't compensate beyond reasonable limits
        float maxCompensation = Time.time - maxCompensationTime;
        compensatedTimestamp = Mathf.Max(compensatedTimestamp, maxCompensation);
        
        // Rollback world state
        var rollbackState = RollbackToTimestamp(compensatedTimestamp);
        
        try
        {
            // Validate hit at the compensated timestamp
            bool isValidHit = PerformHitValidation(targetId, hitPosition);
            
            if (isValidHit)
            {
                // Apply damage to the target
                ApplyDamageToTarget(targetId, 25f); // Example damage
                
                // Notify clients of successful hit
                NotifyHitClientRpc(targetId, hitPosition);
            }
        }
        finally
        {
            // Always restore world state
            RestoreFromRollback(rollbackState);
        }
    }
    
    private bool PerformHitValidation(ulong targetId, Vector3 hitPosition)
    {
        if (NetworkManager.SpawnManager.SpawnedObjects.TryGetValue(targetId, out var target))
        {
            // Perform raycast or collision check at the hit position
            float hitDistance = Vector3.Distance(hitPosition, target.transform.position);
            
            // Simple validation - in a real game, this would be more sophisticated
            return hitDistance <= 2f; // Within reasonable hit range
        }
        
        return false;
    }
    
    private void ApplyDamageToTarget(ulong targetId, float damage)
    {
        if (NetworkManager.SpawnManager.SpawnedObjects.TryGetValue(targetId, out var target))
        {
            var health = target.GetComponent<Health>();
            if (health != null)
            {
                health.TakeDamage(damage);
            }
        }
    }
    
    [ClientRpc]
    private void NotifyHitClientRpc(ulong targetId, Vector3 hitPosition)
    {
        // Show hit effect, play sound, etc.
        Debug.Log($"Hit confirmed on target {targetId} at position {hitPosition}");
    }
    
    private float GetClientPing(ulong clientId)
    {
        // In a real implementation, you would track actual ping times
        // This is a simplified version
        return UnityEngine.Random.Range(0.02f, 0.1f); // 20-100ms ping
    }
}

// Helper class for managing rollback state
public class RollbackState
{
    private Dictionary<ulong, TransformState> storedStates = 
        new Dictionary<ulong, TransformState>();
    
    private struct TransformState
    {
        public Vector3 position;
        public Quaternion rotation;
        public Vector3 velocity;
        public Vector3 angularVelocity;
    }
    
    public void StoreCurrentState(ulong networkId, Transform transform)
    {
        var rb = transform.GetComponent<Rigidbody>();
        
        storedStates[networkId] = new TransformState
        {
            position = transform.position,
            rotation = transform.rotation,
            velocity = rb?.velocity ?? Vector3.zero,
            angularVelocity = rb?.angularVelocity ?? Vector3.zero
        };
    }
    
    public void RestoreStates()
    {
        foreach (var kvp in storedStates)
        {
            ulong networkId = kvp.Key;
            var state = kvp.Value;
            
            if (NetworkManager.Singleton.SpawnManager.SpawnedObjects.TryGetValue(networkId, out var networkObject))
            {
                networkObject.transform.position = state.position;
                networkObject.transform.rotation = state.rotation;
                
                var rb = networkObject.GetComponent<Rigidbody>();
                if (rb != null)
                {
                    rb.position = state.position;
                    rb.rotation = state.rotation;
                    rb.velocity = state.velocity;
                    rb.angularVelocity = state.angularVelocity;
                }
            }
        }
    }
}

// Health component with networking
public class Health : NetworkBehaviour
{
    [Header("Health Settings")]
    [SerializeField] private int maxHealth = 100;
    
    private NetworkVariable<int> currentHealth = new NetworkVariable<int>();
    
    public int CurrentHealth => currentHealth.Value;
    public int MaxHealth => maxHealth;
    public bool IsAlive => currentHealth.Value > 0;
    
    public event System.Action<int, int> OnHealthChanged;
    public event System.Action OnDeath;
    
    public override void OnNetworkSpawn()
    {
        if (IsServer)
        {
            currentHealth.Value = maxHealth;
        }
        
        currentHealth.OnValueChanged += OnHealthValueChanged;
    }
    
    private void OnHealthValueChanged(int oldHealth, int newHealth)
    {
        OnHealthChanged?.Invoke(oldHealth, newHealth);
        
        if (newHealth <= 0 && oldHealth > 0)
        {
            OnDeath?.Invoke();
        }
    }
    
    [ServerRpc(RequireOwnership = false)]
    public void TakeDamageServerRpc(int damage)
    {
        TakeDamage(damage);
    }
    
    public void TakeDamage(int damage)
    {
        if (!IsServer) return;
        
        currentHealth.Value = Mathf.Max(0, currentHealth.Value - damage);
    }
    
    [ServerRpc(RequireOwnership = false)]
    public void HealServerRpc(int healAmount)
    {
        if (!IsServer) return;
        
        currentHealth.Value = Mathf.Min(maxHealth, currentHealth.Value + healAmount);
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### AI-Powered Network Optimization

- **Dynamic Load Balancing**: AI algorithms to distribute players across servers based on latency and load
- **Predictive Scaling**: Machine learning models to anticipate server capacity needs
- **Cheat Detection**: AI systems to identify suspicious player behavior patterns
- **Network Optimization**: Dynamic adjustment of update rates and compression based on network conditions

### Advanced Multiplayer Features

```csharp
// AI-enhanced matchmaking system
public class AIMatchmakingSystem : NetworkBehaviour
{
    [Header("Matchmaking Configuration")]
    [SerializeField] private float skillRatingWeight = 0.4f;
    [SerializeField] private float latencyWeight = 0.3f;
    [SerializeField] private float connectionQualityWeight = 0.3f;
    
    public async System.Threading.Tasks.Task<MatchmakingResult> FindMatch(PlayerProfile playerProfile)
    {
        // Use AI algorithms to find optimal matches
        var potentialMatches = await AnalyzePotentialMatches(playerProfile);
        
        // Score matches using weighted criteria
        var bestMatch = potentialMatches
            .OrderByDescending(m => CalculateMatchScore(playerProfile, m))
            .FirstOrDefault();
        
        return new MatchmakingResult
        {
            success = bestMatch != null,
            matchedPlayers = bestMatch?.players ?? new List<PlayerProfile>(),
            estimatedWaitTime = CalculateEstimatedWaitTime(playerProfile)
        };
    }
    
    private float CalculateMatchScore(PlayerProfile player, PotentialMatch match)
    {
        float skillScore = CalculateSkillCompatibility(player, match);
        float latencyScore = CalculateLatencyScore(player, match);
        float connectionScore = CalculateConnectionScore(player, match);
        
        return (skillScore * skillRatingWeight) + 
               (latencyScore * latencyWeight) + 
               (connectionScore * connectionQualityWeight);
    }
    
    private float CalculateSkillCompatibility(PlayerProfile player, PotentialMatch match)
    {
        // AI algorithm to determine skill compatibility
        return 0.8f; // Placeholder
    }
    
    private float CalculateLatencyScore(PlayerProfile player, PotentialMatch match)
    {
        // Calculate based on geographical distance and network quality
        return 0.9f; // Placeholder
    }
    
    private float CalculateConnectionScore(PlayerProfile player, PotentialMatch match)
    {
        // Analyze connection stability and quality
        return 0.85f; // Placeholder
    }
    
    private async System.Threading.Tasks.Task<List<PotentialMatch>> AnalyzePotentialMatches(PlayerProfile player)
    {
        // AI-powered analysis of potential matches
        await System.Threading.Tasks.Task.Delay(1000); // Simulate AI processing
        return new List<PotentialMatch>(); // Placeholder
    }
    
    private float CalculateEstimatedWaitTime(PlayerProfile player)
    {
        // AI prediction of wait time based on current queue and historical data
        return 30f; // Placeholder: 30 seconds
    }
}

public class PlayerProfile
{
    public ulong playerId;
    public string playerName;
    public float skillRating;
    public Vector2 geographicLocation;
    public float averageLatency;
    public float connectionStability;
    public List<string> preferredGameModes;
}

public class PotentialMatch
{
    public List<PlayerProfile> players;
    public float averageSkillLevel;
    public float estimatedLatency;
    public string gameMode;
}

public class MatchmakingResult
{
    public bool success;
    public List<PlayerProfile> matchedPlayers;
    public float estimatedWaitTime;
}
```

## 💡 Key Networking Principles

### Architecture Design
- **Client-Server Authority**: Server makes all authoritative decisions for game state
- **Client-Side Prediction**: Local prediction for responsive controls with server reconciliation
- **Delta Compression**: Only send changed data to minimize bandwidth usage
- **State Synchronization**: Robust systems for keeping all clients in sync

### Performance Optimization
- **Network LOD**: Reduce update frequency for distant or less important objects
- **Interest Management**: Only send relevant updates to each client
- **Batching**: Group multiple updates into single network messages
- **Compression**: Use efficient serialization and compression techniques

### Security Considerations
- **Input Validation**: Validate all client inputs on the server
- **Anti-Cheat**: Implement server-side validation for all game actions
- **Rate Limiting**: Prevent clients from sending too many messages
- **Encryption**: Secure sensitive data transmission

This comprehensive networking guide provides the foundation for creating scalable, secure, and performant multiplayer games in Unity using modern networking techniques.