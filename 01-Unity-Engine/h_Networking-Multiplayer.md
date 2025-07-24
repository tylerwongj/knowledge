# @h-Networking-Multiplayer - Unity Multiplayer Development

## 🎯 Learning Objectives
- Master Unity Netcode for GameObjects and multiplayer architecture
- Understand client-server vs peer-to-peer networking models
- Implement synchronization, state management, and network optimization
- Build scalable multiplayer games with proper security and anti-cheat measures

## 🔧 Core Networking Concepts

### Unity Netcode for GameObjects Setup
```csharp
using Unity.Netcode;

public class PlayerController : NetworkBehaviour
{
    [SerializeField] private float moveSpeed = 5f;
    private NetworkVariable<Vector3> networkPosition = new NetworkVariable<Vector3>();
    
    public override void OnNetworkSpawn()
    {
        if (IsOwner)
        {
            // Only the owner can move this player
            enabled = true;
        }
        else
        {
            // Other clients just observe
            enabled = false;
        }
    }
    
    void Update()
    {
        if (!IsOwner) return;
        
        Vector3 movement = new Vector3(Input.GetAxis("Horizontal"), 0, Input.GetAxis("Vertical"));
        transform.position += movement * moveSpeed * Time.deltaTime;
        
        // Update network position
        UpdatePositionServerRpc(transform.position);
    }
    
    [ServerRpc]
    void UpdatePositionServerRpc(Vector3 newPos)
    {
        networkPosition.Value = newPos;
    }
}
```

### Network Variable Synchronization
```csharp
public class NetworkedHealth : NetworkBehaviour
{
    [SerializeField] private NetworkVariable<int> health = new NetworkVariable<int>(100);
    
    public override void OnNetworkSpawn()
    {
        health.OnValueChanged += OnHealthChanged;
    }
    
    private void OnHealthChanged(int previousValue, int newValue)
    {
        // Update UI or trigger effects when health changes
        UpdateHealthDisplay(newValue);
        
        if (newValue <= 0)
        {
            HandlePlayerDeath();
        }
    }
    
    [ServerRpc(RequireOwnership = false)]
    public void TakeDamageServerRpc(int damage, ulong attackerId)
    {
        if (!IsServer) return;
        
        health.Value = Mathf.Max(0, health.Value - damage);
        
        // Notify attacker of successful hit
        NotifyHitClientRpc(attackerId, damage);
    }
    
    [ClientRpc]
    void NotifyHitClientRpc(ulong attackerId, int damage)
    {
        // Visual feedback for successful hit
    }
}
```

### Custom Network Managers
```csharp
public class GameNetworkManager : NetworkManager
{
    [SerializeField] private GameObject playerPrefab;
    private Dictionary<ulong, PlayerData> connectedPlayers = new Dictionary<ulong, PlayerData>();
    
    public override void OnClientConnectedCallback(ulong clientId)
    {
        base.OnClientConnectedCallback(clientId);
        
        if (IsServer)
        {
            SpawnPlayerForClient(clientId);
            SendWelcomeMessageClientRpc(clientId);
        }
    }
    
    private void SpawnPlayerForClient(ulong clientId)
    {
        GameObject playerInstance = Instantiate(playerPrefab);
        playerInstance.GetComponent<NetworkObject>().SpawnAsPlayerObject(clientId);
        
        // Store player data
        connectedPlayers[clientId] = new PlayerData
        {
            playerId = clientId,
            spawnTime = Time.time
        };
    }
    
    [ClientRpc]
    void SendWelcomeMessageClientRpc(ulong newPlayerId)
    {
        Debug.Log($"Player {newPlayerId} joined the game!");
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Automated Networking Code Generation
```
"Generate a Unity Netcode system for a real-time strategy game with the following requirements:
- Unit selection and movement synchronization
- Resource collection across multiple players
- Building construction with conflict resolution
- Performance optimization for 100+ units
- Lag compensation for smooth gameplay"
```

### Network Architecture Planning
```
"Design a scalable multiplayer architecture for a battle royale game:
- 100 player capacity
- Server authoritative movement
- Anti-cheat integration
- Regional server deployment
- Spectator mode support
- Matchmaking system integration"
```

## 💡 Advanced Networking Patterns

### State Management and Reconciliation
```csharp
public class NetworkedTransform : NetworkBehaviour
{
    private Vector3 serverPosition;
    private Vector3 clientPosition;
    private float reconciliationThreshold = 0.1f;
    
    [ServerRpc]
    void SubmitMovementServerRpc(Vector3 clientPos, float timestamp)
    {
        // Server validates movement
        Vector3 validatedPos = ValidateMovement(clientPos, timestamp);
        
        if (Vector3.Distance(clientPos, validatedPos) > reconciliationThreshold)
        {
            // Send correction back to client
            CorrectPositionClientRpc(validatedPos, timestamp);
        }
        
        serverPosition = validatedPos;
        transform.position = serverPosition;
    }
    
    [ClientRpc]
    void CorrectPositionClientRpc(Vector3 correctedPos, float timestamp)
    {
        if (IsOwner)
        {
            // Reconcile client prediction with server state
            ReconcilePosition(correctedPos, timestamp);
        }
        else
        {
            // Just update position for other clients
            transform.position = correctedPos;
        }
    }
}
```

### Custom Network Serialization
```csharp
public struct PlayerInput : INetworkSerializable
{
    public Vector2 movement;
    public bool isJumping;
    public bool isShooting;
    public float lookAngle;
    
    public void NetworkSerialize<T>(BufferSerializer<T> serializer) where T : IReaderWriter
    {
        serializer.SerializeValue(ref movement);
        serializer.SerializeValue(ref isJumping);
        serializer.SerializeValue(ref isShooting);
        serializer.SerializeValue(ref lookAngle);
    }
}
```

### Anti-Cheat and Security
```csharp
public class AntiCheatValidator : NetworkBehaviour
{
    private Vector3 lastValidPosition;
    private float maxMoveSpeed = 10f;
    private float suspicionLevel = 0f;
    
    [ServerRpc]
    void ValidateMovementServerRpc(Vector3 newPos, float deltaTime)
    {
        float distanceMoved = Vector3.Distance(lastValidPosition, newPos);
        float maxAllowedDistance = maxMoveSpeed * deltaTime * 1.1f; // 10% tolerance
        
        if (distanceMoved > maxAllowedDistance)
        {
            suspicionLevel += 1f;
            
            if (suspicionLevel > 5f)
            {
                // Potential cheater detected
                HandleSuspiciousActivity();
            }
            
            // Reject movement and reset to last valid position
            ForcePositionClientRpc(lastValidPosition);
            return;
        }
        
        lastValidPosition = newPos;
        suspicionLevel = Mathf.Max(0, suspicionLevel - 0.1f); // Slowly decrease suspicion
    }
}
```

## 🔬 Performance Optimization for Multiplayer

### Network Culling and Interest Management
```csharp
public class NetworkCullingSystem : NetworkBehaviour
{
    [SerializeField] private float cullingDistance = 50f;
    private HashSet<ulong> playersInRange = new HashSet<ulong>();
    
    void Update()
    {
        if (!IsServer) return;
        
        // Update which players can see this object
        UpdatePlayerVisibility();
    }
    
    private void UpdatePlayerVisibility()
    {
        var currentlyVisible = new HashSet<ulong>();
        
        foreach (var client in NetworkManager.Singleton.ConnectedClients)
        {
            float distance = Vector3.Distance(transform.position, client.Value.PlayerObject.transform.position);
            
            if (distance <= cullingDistance)
            {
                currentlyVisible.Add(client.Key);
                
                if (!playersInRange.Contains(client.Key))
                {
                    // Player entered range - make object visible
                    NetworkObject.CheckObjectVisibility(client.Key, true);
                }
            }
        }
        
        // Handle players who left range
        foreach (var playerId in playersInRange)
        {
            if (!currentlyVisible.Contains(playerId))
            {
                NetworkObject.CheckObjectVisibility(playerId, false);
            }
        }
        
        playersInRange = currentlyVisible;
    }
}
```

### Bandwidth Optimization
```csharp
public class OptimizedNetworkUpdater : NetworkBehaviour
{
    private Vector3 lastSentPosition;
    private float sendThreshold = 0.1f;
    private float sendRate = 20f; // 20 updates per second
    private float lastSendTime;
    
    void Update()
    {
        if (!IsOwner) return;
        
        if (Time.time - lastSendTime >= 1f / sendRate)
        {
            if (Vector3.Distance(transform.position, lastSentPosition) > sendThreshold)
            {
                SendPositionUpdateServerRpc(transform.position);
                lastSentPosition = transform.position;
                lastSendTime = Time.time;
            }
        }
    }
}
```

## 📊 AI-Enhanced Multiplayer Development

### Automated Testing and Load Testing
- AI-generated bot players for stress testing
- Automated network condition simulation
- Performance regression detection
- Latency compensation algorithm optimization

### Smart Matchmaking Integration
```csharp
public class AIMatchmakingIntegration : MonoBehaviour
{
    public async Task<MatchmakingResult> FindMatch(PlayerSkillData skillData)
    {
        // AI analyzes player patterns and finds optimal matches
        var matchRequest = new MatchRequest
        {
            skillLevel = skillData.overallSkill,
            preferredGameModes = skillData.favoriteGameModes,
            latencyRequirements = GetOptimalLatency(),
            playerBehaviorProfile = await AnalyzePlayerBehavior(skillData)
        };
        
        return await SubmitToMatchmakingService(matchRequest);
    }
}
```

This networking knowledge enables creation of robust, scalable multiplayer games with AI-enhanced anti-cheat systems, automated testing, and performance optimization that scales to hundreds of concurrent players.