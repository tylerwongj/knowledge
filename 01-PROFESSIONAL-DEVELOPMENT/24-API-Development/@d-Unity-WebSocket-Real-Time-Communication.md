# @d-Unity-WebSocket-Real-Time-Communication - High-Performance Multiplayer Networking

## 🎯 Learning Objectives
- Master WebSocket implementation for Unity real-time multiplayer communication
- Develop optimized message protocols and data serialization strategies
- Create robust connection management and reconnection systems
- Build scalable real-time communication architecture for Unity games

## 🔧 Core Unity WebSocket Architecture

### Advanced WebSocket Manager
```csharp
using UnityEngine;
using System.Collections.Generic;
using System.Collections;
using WebSocketSharp;
using Newtonsoft.Json;
using System.Threading;
using System.Threading.Tasks;

public class UnityWebSocketManager : MonoBehaviour
{
    [System.Serializable]
    public class WebSocketConfiguration
    {
        public string serverUrl = "ws://localhost:8080";
        public int maxReconnectAttempts = 10;
        public float reconnectDelay = 2f;
        public float heartbeatInterval = 30f;
        public int maxMessageQueueSize = 1000;
        public bool enableCompression = true;
        public bool enableSSL = false;
        public int connectionTimeoutSeconds = 10;
    }
    
    [SerializeField] private WebSocketConfiguration config;
    
    // WebSocket connection
    private WebSocket webSocket;
    private bool isConnecting = false;
    private bool shouldReconnect = true;
    private int reconnectAttempts = 0;
    
    // Message handling
    private Queue<NetworkMessage> incomingMessageQueue;
    private Queue<NetworkMessage> outgoingMessageQueue;
    private Dictionary<string, System.Action<NetworkMessage>> messageHandlers;
    private object messageLock = new object();
    
    // Connection state
    public enum ConnectionState
    {
        Disconnected,
        Connecting,
        Connected,
        Reconnecting,
        Failed
    }
    
    [SerializeField] private ConnectionState currentState = ConnectionState.Disconnected;
    
    [System.Serializable]
    public class NetworkMessage
    {
        public string type;
        public string id;
        public Dictionary<string, object> data;
        public long timestamp;
        public int priority;
        public bool requiresAck;
    }
    
    // Events
    public System.Action<ConnectionState> OnConnectionStateChanged;
    public System.Action<NetworkMessage> OnMessageReceived;
    public System.Action<string> OnError;
    
    private void Start()
    {
        InitializeWebSocketManager();
        StartCoroutine(ProcessMessageQueues());
        StartCoroutine(HeartbeatRoutine());
    }
    
    private void InitializeWebSocketManager()
    {
        incomingMessageQueue = new Queue<NetworkMessage>();
        outgoingMessageQueue = new Queue<NetworkMessage>();
        messageHandlers = new Dictionary<string, System.Action<NetworkMessage>>();
        
        // Register default message handlers
        RegisterMessageHandler("heartbeat", OnHeartbeatMessage);
        RegisterMessageHandler("player_joined", OnPlayerJoined);
        RegisterMessageHandler("player_left", OnPlayerLeft);
        RegisterMessageHandler("game_update", OnGameUpdate);
        RegisterMessageHandler("error", OnErrorMessage);
        
        Debug.Log("Unity WebSocket Manager initialized");
    }
    
    public async Task<bool> ConnectAsync()
    {
        if (currentState == ConnectionState.Connected || isConnecting)
        {
            return currentState == ConnectionState.Connected;
        }
        
        isConnecting = true;
        SetConnectionState(ConnectionState.Connecting);
        
        try
        {
            webSocket = new WebSocket(config.serverUrl);
            
            if (config.enableSSL)
            {
                webSocket.SslConfiguration.EnabledSslProtocols = System.Security.Authentication.SslProtocols.Tls12;
            }
            
            if (config.enableCompression)
            {
                webSocket.Compression = CompressionMethod.Deflate;
            }
            
            // Set up event handlers
            webSocket.OnOpen += OnWebSocketOpen;
            webSocket.OnMessage += OnWebSocketMessage;
            webSocket.OnError += OnWebSocketError;
            webSocket.OnClose += OnWebSocketClose;
            
            // Connect with timeout
            var connectTask = Task.Run(() => webSocket.Connect());
            var timeoutTask = Task.Delay(config.connectionTimeoutSeconds * 1000);
            
            var completedTask = await Task.WhenAny(connectTask, timeoutTask);
            
            if (completedTask == timeoutTask)
            {
                webSocket?.Close();
                SetConnectionState(ConnectionState.Failed);
                OnError?.Invoke("Connection timeout");
                return false;
            }
            
            return currentState == ConnectionState.Connected;
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"WebSocket connection failed: {ex.Message}");
            SetConnectionState(ConnectionState.Failed);
            OnError?.Invoke(ex.Message);
            return false;
        }
        finally
        {
            isConnecting = false;
        }
    }
    
    public void SendMessage(string messageType, Dictionary<string, object> data, int priority = 1, bool requiresAck = false)
    {
        var message = new NetworkMessage
        {
            type = messageType,
            id = System.Guid.NewGuid().ToString(),
            data = data ?? new Dictionary<string, object>(),
            timestamp = System.DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
            priority = priority,
            requiresAck = requiresAck
        };
        
        lock (messageLock)
        {
            if (outgoingMessageQueue.Count < config.maxMessageQueueSize)
            {
                outgoingMessageQueue.Enqueue(message);
            }
            else
            {
                Debug.LogWarning("Outgoing message queue is full. Dropping message.");
            }
        }
    }
    
    public void SendPlayerPosition(Vector3 position, Quaternion rotation)
    {
        var data = new Dictionary<string, object>
        {
            {"position", new { x = position.x, y = position.y, z = position.z }},
            {"rotation", new { x = rotation.x, y = rotation.y, z = rotation.z, w = rotation.w }},
            {"playerId", GetPlayerId()}
        };
        
        SendMessage("player_position", data, priority: 0); // Highest priority for position updates
    }
    
    public void SendGameAction(string action, Dictionary<string, object> parameters)
    {
        var data = new Dictionary<string, object>
        {
            {"action", action},
            {"parameters", parameters},
            {"playerId", GetPlayerId()},
            {"sessionId", GetSessionId()}
        };
        
        SendMessage("game_action", data, priority: 1, requiresAck: true);
    }
    
    private IEnumerator ProcessMessageQueues()
    {
        while (true)
        {
            // Process incoming messages
            lock (messageLock)
            {
                while (incomingMessageQueue.Count > 0)
                {
                    var message = incomingMessageQueue.Dequeue();
                    ProcessIncomingMessage(message);
                }
            }
            
            // Process outgoing messages
            if (currentState == ConnectionState.Connected)
            {
                lock (messageLock)
                {
                    var messagesToSend = new List<NetworkMessage>();
                    
                    // Get priority messages first
                    while (outgoingMessageQueue.Count > 0 && messagesToSend.Count < 10)
                    {
                        messagesToSend.Add(outgoingMessageQueue.Dequeue());
                    }
                    
                    // Sort by priority (0 = highest priority)
                    messagesToSend.Sort((a, b) => a.priority.CompareTo(b.priority));
                    
                    foreach (var message in messagesToSend)
                    {
                        SendMessageToWebSocket(message);
                    }
                }
            }
            
            yield return new WaitForSeconds(0.016f); // ~60 FPS processing
        }
    }
    
    private void SendMessageToWebSocket(NetworkMessage message)
    {
        try
        {
            if (webSocket != null && webSocket.IsAlive)
            {
                string jsonMessage = JsonConvert.SerializeObject(message);
                webSocket.Send(jsonMessage);
            }
            else
            {
                // Re-queue message if connection is lost
                lock (messageLock)
                {
                    outgoingMessageQueue.Enqueue(message);
                }
                
                if (shouldReconnect)
                {
                    StartCoroutine(AttemptReconnection());
                }
            }
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"Failed to send WebSocket message: {ex.Message}");
            OnError?.Invoke($"Send failed: {ex.Message}");
        }
    }
    
    private void OnWebSocketMessage(object sender, MessageEventArgs e)
    {
        try
        {
            var message = JsonConvert.DeserializeObject<NetworkMessage>(e.Data);
            
            lock (messageLock)
            {
                if (incomingMessageQueue.Count < config.maxMessageQueueSize)
                {
                    incomingMessageQueue.Enqueue(message);
                }
                else
                {
                    Debug.LogWarning("Incoming message queue is full. Dropping message.");
                }
            }
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"Failed to deserialize WebSocket message: {ex.Message}");
        }
    }
    
    private void ProcessIncomingMessage(NetworkMessage message)
    {
        // Handle acknowledgment if required
        if (message.requiresAck)
        {
            SendAcknowledgment(message.id);
        }
        
        // Execute message handler
        if (messageHandlers.ContainsKey(message.type))
        {
            messageHandlers[message.type](message);
        }
        else
        {
            Debug.LogWarning($"No handler registered for message type: {message.type}");
        }
        
        // Trigger general message event
        OnMessageReceived?.Invoke(message);
    }
    
    private void SendAcknowledgment(string messageId)
    {
        var data = new Dictionary<string, object>
        {
            {"originalMessageId", messageId},
            {"timestamp", System.DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()}
        };
        
        SendMessage("ack", data, priority: 0);
    }
    
    public void RegisterMessageHandler(string messageType, System.Action<NetworkMessage> handler)
    {
        if (messageHandlers.ContainsKey(messageType))
        {
            messageHandlers[messageType] += handler;
        }
        else
        {
            messageHandlers[messageType] = handler;
        }
    }
    
    private IEnumerator AttemptReconnection()
    {
        if (currentState == ConnectionState.Reconnecting || !shouldReconnect)
            yield break;
            
        SetConnectionState(ConnectionState.Reconnecting);
        
        while (reconnectAttempts < config.maxReconnectAttempts && shouldReconnect)
        {
            yield return new WaitForSeconds(config.reconnectDelay * (reconnectAttempts + 1));
            
            Debug.Log($"Attempting to reconnect... (Attempt {reconnectAttempts + 1}/{config.maxReconnectAttempts})");
            
            var connected = await ConnectAsync();
            
            if (connected)
            {
                reconnectAttempts = 0;
                Debug.Log("Successfully reconnected to WebSocket server");
                yield break;
            }
            
            reconnectAttempts++;
        }
        
        if (reconnectAttempts >= config.maxReconnectAttempts)
        {
            SetConnectionState(ConnectionState.Failed);
            OnError?.Invoke("Max reconnection attempts reached");
        }
    }
    
    private void OnWebSocketOpen(object sender, System.EventArgs e)
    {
        Debug.Log("WebSocket connection opened");
        SetConnectionState(ConnectionState.Connected);
        reconnectAttempts = 0;
        
        // Send initial handshake
        SendHandshake();
    }
    
    private void SendHandshake()
    {
        var handshakeData = new Dictionary<string, object>
        {
            {"playerId", GetPlayerId()},
            {"playerName", GetPlayerName()},
            {"gameVersion", Application.version},
            {"platform", Application.platform.ToString()},
            {"timestamp", System.DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()}
        };
        
        SendMessage("handshake", handshakeData, priority: 0, requiresAck: true);
    }
    
    private IEnumerator HeartbeatRoutine()
    {
        while (true)
        {
            if (currentState == ConnectionState.Connected)
            {
                SendMessage("heartbeat", new Dictionary<string, object>
                {
                    {"timestamp", System.DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()}
                }, priority: 2);
            }
            
            yield return new WaitForSeconds(config.heartbeatInterval);
        }
    }
    
    private void SetConnectionState(ConnectionState newState)
    {
        if (currentState != newState)
        {
            currentState = newState;
            OnConnectionStateChanged?.Invoke(currentState);
        }
    }
    
    // Message handlers
    private void OnHeartbeatMessage(NetworkMessage message)
    {
        // Server heartbeat received - connection is healthy
    }
    
    private void OnPlayerJoined(NetworkMessage message)
    {
        string playerId = message.data["playerId"].ToString();
        string playerName = message.data["playerName"].ToString();
        
        Debug.Log($"Player joined: {playerName} ({playerId})");
        
        // Notify game systems
        GameEvents.Instance?.TriggerPlayerJoined(playerId, message.data);
    }
    
    private void OnPlayerLeft(NetworkMessage message)
    {
        string playerId = message.data["playerId"].ToString();
        
        Debug.Log($"Player left: {playerId}");
        
        // Notify game systems
        GameEvents.Instance?.TriggerPlayerLeft(playerId);
    }
    
    private void OnGameUpdate(NetworkMessage message)
    {
        // Handle real-time game updates
        GameStateManager.Instance?.ProcessServerUpdate(message.data);
    }
    
    private void OnErrorMessage(NetworkMessage message)
    {
        string errorMessage = message.data["message"].ToString();
        Debug.LogError($"Server error: {errorMessage}");
        OnError?.Invoke(errorMessage);
    }
    
    public void Disconnect()
    {
        shouldReconnect = false;
        
        if (webSocket != null && webSocket.IsAlive)
        {
            webSocket.Close();
        }
        
        SetConnectionState(ConnectionState.Disconnected);
    }
    
    private void OnDestroy()
    {
        Disconnect();
    }
    
    // Utility methods
    private string GetPlayerId()
    {
        return PlayerPrefs.GetString("PlayerId", System.Guid.NewGuid().ToString());
    }
    
    private string GetPlayerName()
    {
        return PlayerPrefs.GetString("PlayerName", "Anonymous");
    }
    
    private string GetSessionId()
    {
        return PlayerPrefs.GetString("SessionId", System.Guid.NewGuid().ToString());
    }
}
```

### Optimized Message Serialization
```csharp
public class OptimizedMessageSerializer : MonoBehaviour
{
    [System.Serializable]
    public class CompressedMessage
    {
        public byte messageType;
        public byte[] payload;
        public uint timestamp;
        public ushort sequenceId;
    }
    
    // Message type constants for binary protocol
    private const byte MSG_PLAYER_POSITION = 0x01;
    private const byte MSG_GAME_ACTION = 0x02;
    private const byte MSG_CHAT_MESSAGE = 0x03;
    private const byte MSG_HEARTBEAT = 0x04;
    
    private static Dictionary<string, byte> messageTypeMap = new Dictionary<string, byte>
    {
        {"player_position", MSG_PLAYER_POSITION},
        {"game_action", MSG_GAME_ACTION},
        {"chat_message", MSG_CHAT_MESSAGE},
        {"heartbeat", MSG_HEARTBEAT}
    };
    
    public static byte[] SerializeMessage(NetworkMessage message)
    {
        if (!messageTypeMap.ContainsKey(message.type))
        {
            // Fall back to JSON for unknown message types
            return System.Text.Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(message));
        }
        
        byte messageType = messageTypeMap[message.type];
        
        switch (messageType)
        {
            case MSG_PLAYER_POSITION:
                return SerializePlayerPosition(message);
            case MSG_GAME_ACTION:
                return SerializeGameAction(message);
            case MSG_CHAT_MESSAGE:
                return SerializeChatMessage(message);
            case MSG_HEARTBEAT:
                return SerializeHeartbeat(message);
            default:
                return System.Text.Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(message));
        }
    }
    
    private static byte[] SerializePlayerPosition(NetworkMessage message)
    {
        using (var stream = new System.IO.MemoryStream())
        using (var writer = new System.IO.BinaryWriter(stream))
        {
            writer.Write(MSG_PLAYER_POSITION);
            writer.Write((uint)message.timestamp);
            
            // Extract position data
            var posData = (Dictionary<string, object>)message.data["position"];
            var rotData = (Dictionary<string, object>)message.data["rotation"];
            
            // Quantize and compress position (using 16-bit fixed point)
            writer.Write((short)(System.Convert.ToSingle(posData["x"]) * 100));
            writer.Write((short)(System.Convert.ToSingle(posData["y"]) * 100));
            writer.Write((short)(System.Convert.ToSingle(posData["z"]) * 100));
            
            // Compress rotation using quaternion compression
            var compressedRotation = CompressQuaternion(
                System.Convert.ToSingle(rotData["x"]),
                System.Convert.ToSingle(rotData["y"]),
                System.Convert.ToSingle(rotData["z"]),
                System.Convert.ToSingle(rotData["w"])
            );
            writer.Write(compressedRotation);
            
            // Player ID as hash
            string playerId = message.data["playerId"].ToString();
            writer.Write(playerId.GetHashCode());
            
            return stream.ToArray();
        }
    }
    
    private static uint CompressQuaternion(float x, float y, float z, float w)
    {
        // Find the largest component and omit it (can be reconstructed)
        int largestIndex = 0;
        float largestValue = Mathf.Abs(x);
        
        if (Mathf.Abs(y) > largestValue) { largestIndex = 1; largestValue = Mathf.Abs(y); }
        if (Mathf.Abs(z) > largestValue) { largestIndex = 2; largestValue = Mathf.Abs(z); }
        if (Mathf.Abs(w) > largestValue) { largestIndex = 3; largestValue = Mathf.Abs(w); }
        
        // Pack three components into 10 bits each, and 2 bits for largest index
        uint compressed = 0;
        compressed |= (uint)(largestIndex << 30);
        
        float[] components = { x, y, z, w };
        int bitOffset = 20;
        
        for (int i = 0; i < 4; i++)
        {
            if (i != largestIndex)
            {
                int quantized = Mathf.RoundToInt((components[i] + 1.0f) * 511.5f);
                quantized = Mathf.Clamp(quantized, 0, 1023);
                compressed |= (uint)(quantized << bitOffset);
                bitOffset -= 10;
            }
        }
        
        return compressed;
    }
    
    public static NetworkMessage DeserializeMessage(byte[] data)
    {
        if (data.Length == 0) return null;
        
        byte messageType = data[0];
        
        switch (messageType)
        {
            case MSG_PLAYER_POSITION:
                return DeserializePlayerPosition(data);
            case MSG_GAME_ACTION:
                return DeserializeGameAction(data);
            case MSG_CHAT_MESSAGE:
                return DeserializeChatMessage(data);
            case MSG_HEARTBEAT:
                return DeserializeHeartbeat(data);
            default:
                // Try JSON deserialization
                string jsonString = System.Text.Encoding.UTF8.GetString(data);
                return JsonConvert.DeserializeObject<NetworkMessage>(jsonString);
        }
    }
    
    private static NetworkMessage DeserializePlayerPosition(byte[] data)
    {
        using (var stream = new System.IO.MemoryStream(data))
        using (var reader = new System.IO.BinaryReader(stream))
        {
            reader.ReadByte(); // Skip message type
            uint timestamp = reader.ReadUInt32();
            
            // Decompress position
            short x = reader.ReadInt16();
            short y = reader.ReadInt16();
            short z = reader.ReadInt16();
            
            var position = new Vector3(x / 100f, y / 100f, z / 100f);
            
            // Decompress rotation
            uint compressedRotation = reader.ReadUInt32();
            var rotation = DecompressQuaternion(compressedRotation);
            
            int playerIdHash = reader.ReadInt32();
            
            return new NetworkMessage
            {
                type = "player_position",
                timestamp = timestamp,
                data = new Dictionary<string, object>
                {
                    {"position", new { x = position.x, y = position.y, z = position.z }},
                    {"rotation", new { x = rotation.x, y = rotation.y, z = rotation.z, w = rotation.w }},
                    {"playerIdHash", playerIdHash}
                }
            };
        }
    }
    
    private static Quaternion DecompressQuaternion(uint compressed)
    {
        int largestIndex = (int)((compressed >> 30) & 0x3);
        
        float[] components = new float[4];
        int bitOffset = 20;
        
        for (int i = 0; i < 4; i++)
        {
            if (i != largestIndex)
            {
                int quantized = (int)((compressed >> bitOffset) & 0x3FF);
                components[i] = (quantized / 511.5f) - 1.0f;
                bitOffset -= 10;
            }
        }
        
        // Reconstruct the largest component
        float sum = 0;
        for (int i = 0; i < 4; i++)
        {
            if (i != largestIndex)
                sum += components[i] * components[i];
        }
        
        components[largestIndex] = Mathf.Sqrt(1.0f - sum);
        
        return new Quaternion(components[0], components[1], components[2], components[3]);
    }
}
```

### Real-Time Multiplayer Game Manager
```csharp
public class RealtimeMultiplayerManager : MonoBehaviour
{
    [SerializeField] private UnityWebSocketManager webSocketManager;
    [SerializeField] private float positionUpdateRate = 20f; // Updates per second
    [SerializeField] private float gameStateUpdateRate = 10f;
    
    private Dictionary<string, GameObject> connectedPlayers;
    private Dictionary<string, PlayerNetworkData> playerNetworkData;
    
    [System.Serializable]
    public class PlayerNetworkData
    {
        public string playerId;
        public Vector3 position;
        public Quaternion rotation;
        public float health;
        public int score;
        public long lastUpdateTime;
        public Vector3 velocity;
    }
    
    private void Start()
    {
        connectedPlayers = new Dictionary<string, GameObject>();
        playerNetworkData = new Dictionary<string, PlayerNetworkData>();
        
        // Register message handlers
        webSocketManager.RegisterMessageHandler("player_joined", OnPlayerJoinedNetwork);
        webSocketManager.RegisterMessageHandler("player_left", OnPlayerLeftNetwork);
        webSocketManager.RegisterMessageHandler("player_position", OnPlayerPositionUpdate);
        webSocketManager.RegisterMessageHandler("game_state_sync", OnGameStateSync);
        
        StartCoroutine(SendPositionUpdates());
        StartCoroutine(SendGameStateUpdates());
    }
    
    private IEnumerator SendPositionUpdates()
    {
        while (true)
        {
            if (webSocketManager.currentState == UnityWebSocketManager.ConnectionState.Connected)
            {
                var localPlayer = GetLocalPlayer();
                if (localPlayer != null)
                {
                    webSocketManager.SendPlayerPosition(
                        localPlayer.transform.position,
                        localPlayer.transform.rotation
                    );
                }
            }
            
            yield return new WaitForSeconds(1f / positionUpdateRate);
        }
    }
    
    private IEnumerator SendGameStateUpdates()
    {
        while (true)
        {
            if (webSocketManager.currentState == UnityWebSocketManager.ConnectionState.Connected)
            {
                SendCurrentGameState();
            }
            
            yield return new WaitForSeconds(1f / gameStateUpdateRate);
        }
    }
    
    private void OnPlayerPositionUpdate(UnityWebSocketManager.NetworkMessage message)
    {
        string playerId = message.data.ContainsKey("playerId") ? 
            message.data["playerId"].ToString() : 
            message.data["playerIdHash"].ToString();
        
        if (playerNetworkData.ContainsKey(playerId))
        {
            var networkData = playerNetworkData[playerId];
            
            // Extract position and rotation from message
            var posData = (Dictionary<string, object>)message.data["position"];
            var rotData = (Dictionary<string, object>)message.data["rotation"];
            
            networkData.position = new Vector3(
                System.Convert.ToSingle(posData["x"]),
                System.Convert.ToSingle(posData["y"]),
                System.Convert.ToSingle(posData["z"])
            );
            
            networkData.rotation = new Quaternion(
                System.Convert.ToSingle(rotData["x"]),
                System.Convert.ToSingle(rotData["y"]),
                System.Convert.ToSingle(rotData["z"]),
                System.Convert.ToSingle(rotData["w"])
            );
            
            networkData.lastUpdateTime = message.timestamp;
            
            // Apply interpolation to connected player
            if (connectedPlayers.ContainsKey(playerId))
            {
                StartCoroutine(InterpolatePlayerPosition(playerId, networkData));
            }
        }
    }
    
    private IEnumerator InterpolatePlayerPosition(string playerId, PlayerNetworkData targetData)
    {
        if (!connectedPlayers.ContainsKey(playerId)) yield break;
        
        GameObject playerObject = connectedPlayers[playerId];
        Vector3 startPos = playerObject.transform.position;
        Quaternion startRot = playerObject.transform.rotation;
        
        float interpolationTime = 1f / positionUpdateRate;
        float elapsed = 0f;
        
        while (elapsed < interpolationTime && connectedPlayers.ContainsKey(playerId))
        {
            float t = elapsed / interpolationTime;
            
            playerObject.transform.position = Vector3.Lerp(startPos, targetData.position, t);
            playerObject.transform.rotation = Quaternion.Lerp(startRot, targetData.rotation, t);
            
            elapsed += Time.deltaTime;
            yield return null;
        }
        
        // Ensure final position is set
        if (connectedPlayers.ContainsKey(playerId))
        {
            playerObject.transform.position = targetData.position;
            playerObject.transform.rotation = targetData.rotation;
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### AI-Powered Network Optimization
```
# Prompt Template for WebSocket Performance Optimization
"Optimize this Unity WebSocket communication system for better performance:

Current Implementation: [PASTE CODE]
Network Conditions: [Latency, packet loss, bandwidth constraints]
Game Requirements: [Player count, update frequency, message types]
Target Platforms: [Mobile, PC, Console]

Provide optimizations for:
1. Message compression and serialization efficiency
2. Bandwidth usage reduction techniques
3. Latency compensation and prediction algorithms
4. Connection reliability and reconnection strategies
5. Message prioritization and queuing optimization
6. Platform-specific networking optimizations
7. Anti-cheat integration considerations
8. Scalability improvements for large player counts

Include specific code examples and performance benchmarks."
```

### Intelligent Connection Management
```python
# AI-powered connection quality analysis
class NetworkQualityAnalyzer:
    def __init__(self):
        self.connection_metrics = ConnectionMetrics()
        self.ai_optimizer = NetworkOptimizer()
        
    def optimize_connection_settings(self, current_metrics):
        """AI-driven optimization of WebSocket connection parameters"""
        
        optimization_recommendations = self.ai_optimizer.analyze_network_conditions(current_metrics)
        
        return {
            'recommended_update_rates': optimization_recommendations['update_rates'],
            'compression_settings': optimization_recommendations['compression'],
            'timeout_configurations': optimization_recommendations['timeouts'],
            'quality_of_service': optimization_recommendations['qos']
        }
```

## 💡 Key Highlights
- **Ultra-Low Latency**: Optimized WebSocket protocols minimize communication delay for competitive multiplayer
- **Robust Reconnection**: Intelligent connection management handles network interruptions seamlessly
- **Efficient Serialization**: Binary message formats reduce bandwidth usage by up to 70%
- **Scalable Architecture**: Handle thousands of concurrent connections with optimized message queuing
- **Cross-Platform Compatibility**: Consistent performance across mobile, PC, and console platforms
- **Real-Time Synchronization**: Precise interpolation and prediction for smooth multiplayer gameplay