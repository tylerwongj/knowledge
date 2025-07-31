# @45-Networking-Multiplayer-Tools

## 🎯 Core Concept
Automated networking and multiplayer tools for connection management, synchronization, and network optimization.

## 🔧 Implementation

### Network Manager Framework
```csharp
using UnityEngine;
using UnityEngine.Networking;
using System.Collections.Generic;
using System.Collections;

public class NetworkManager : MonoBehaviour
{
    public static NetworkManager Instance;
    
    [Header("Network Settings")]
    public string serverAddress = "127.0.0.1";
    public int serverPort = 7777;
    public int maxConnections = 10;
    public bool autoStartServer = false;
    public bool autoConnectAsClient = false;
    
    [Header("Connection Management")]
    public float connectionTimeout = 10f;
    public float heartbeatInterval = 5f;
    public int maxReconnectAttempts = 3;
    public float reconnectDelay = 2f;
    
    [Header("Synchronization")]
    public float syncInterval = 0.1f;
    public bool compressData = true;
    public NetworkTransport transport = NetworkTransport.TCP;
    
    private Dictionary<int, NetworkConnection> connections;
    private Dictionary<int, NetworkPlayer> players;
    private bool isServer = false;
    private bool isClient = false;
    private bool isConnected = false;
    private int hostId = -1;
    private int reconnectAttempts = 0;
    
    public System.Action OnServerStarted;
    public System.Action OnServerStopped;
    public System.Action OnClientConnected;
    public System.Action OnClientDisconnected;
    public System.Action<NetworkPlayer> OnPlayerJoined;
    public System.Action<NetworkPlayer> OnPlayerLeft;
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeNetwork();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void Start()
    {
        if (autoStartServer)
        {
            StartServer();
        }
        else if (autoConnectAsClient)
        {
            ConnectToServer();
        }
    }
    
    void InitializeNetwork()
    {
        connections = new Dictionary<int, NetworkConnection>();
        players = new Dictionary<int, NetworkPlayer>();
        
        // Initialize network transport
        NetworkTransport.Init();
        
        // Start heartbeat coroutine
        StartCoroutine(HeartbeatCoroutine());
        
        Debug.Log("Network Manager initialized");
    }
    
    public void StartServer()
    {
        if (isServer || isClient)
        {
            Debug.LogWarning("Network already active");
            return;
        }
        
        ConnectionConfig config = new ConnectionConfig();
        config.AddChannel(QosType.ReliableSequenced);
        config.AddChannel(QosType.UnreliableSequenced);
        
        HostTopology topology = new HostTopology(config, maxConnections);
        
        hostId = NetworkTransport.AddHost(topology, serverPort);
        
        if (hostId >= 0)
        {
            isServer = true;
            Debug.Log($"Server started on port {serverPort}");
            OnServerStarted?.Invoke();
        }
        else
        {
            Debug.LogError("Failed to start server");
        }
    }
    
    public void StopServer()
    {
        if (!isServer)
        {
            Debug.LogWarning("Server is not running");
            return;
        }
        
        // Disconnect all clients
        foreach (var connection in connections.Values)
        {
            DisconnectClient(connection.connectionId);
        }
        
        NetworkTransport.RemoveHost(hostId);
        
        isServer = false;
        hostId = -1;
        connections.Clear();
        players.Clear();
        
        Debug.Log("Server stopped");
        OnServerStopped?.Invoke();
    }
    
    public void ConnectToServer()
    {
        if (isServer || isClient)
        {
            Debug.LogWarning("Network already active");
            return;
        }
        
        StartCoroutine(ConnectToServerCoroutine());
    }
    
    IEnumerator ConnectToServerCoroutine()
    {
        ConnectionConfig config = new ConnectionConfig();
        config.AddChannel(QosType.ReliableSequenced);
        config.AddChannel(QosType.UnreliableSequenced);
        
        HostTopology topology = new HostTopology(config, 1);
        hostId = NetworkTransport.AddHost(topology);
        
        byte error;
        int connectionId = NetworkTransport.Connect(hostId, serverAddress, serverPort, 0, out error);
        
        if (error != (byte)NetworkError.Ok)
        {
            Debug.LogError($"Failed to connect to server: {(NetworkError)error}");
            yield break;
        }
        
        isClient = true;
        float timeoutTimer = 0f;
        
        while (!isConnected && timeoutTimer < connectionTimeout)
        {
            timeoutTimer += Time.deltaTime;
            ProcessNetworkMessages();
            yield return null;
        }
        
        if (!isConnected)
        {
            Debug.LogError("Connection timeout");
            DisconnectFromServer();
            
            // Attempt reconnection
            if (reconnectAttempts < maxReconnectAttempts)
            {
                reconnectAttempts++;
                Debug.Log($"Reconnection attempt {reconnectAttempts}/{maxReconnectAttempts}");
                yield return new WaitForSeconds(reconnectDelay);
                ConnectToServer();
            }
        }
    }
    
    public void DisconnectFromServer()
    {
        if (!isClient)
        {
            Debug.LogWarning("Client is not connected");
            return;
        }
        
        if (isConnected)
        {
            NetworkTransport.Disconnect(hostId, connections.Keys.GetEnumerator().Current, out byte error);
        }
        
        NetworkTransport.RemoveHost(hostId);
        
        isClient = false;
        isConnected = false;
        hostId = -1;
        connections.Clear();
        players.Clear();
        
        Debug.Log("Disconnected from server");
        OnClientDisconnected?.Invoke();
    }
    
    void Update()
    {
        if (isServer || isClient)
        {
            ProcessNetworkMessages();
        }
    }
    
    void ProcessNetworkMessages()
    {
        int recHostId;
        int connectionId;
        int channelId;
        byte[] recBuffer = new byte[1024];
        int bufferSize = 1024;
        int dataSize;
        byte error;
        
        NetworkEventType recData = NetworkTransport.Receive(out recHostId, out connectionId, 
            out channelId, recBuffer, bufferSize, out dataSize, out error);
        
        switch (recData)
        {
            case NetworkEventType.Nothing:
                break;
                
            case NetworkEventType.ConnectEvent:
                HandleConnectionEvent(connectionId);
                break;
                
            case NetworkEventType.DataEvent:
                HandleDataEvent(connectionId, channelId, recBuffer, dataSize);
                break;
                
            case NetworkEventType.DisconnectEvent:
                HandleDisconnectionEvent(connectionId);
                break;
        }
    }
    
    void HandleConnectionEvent(int connectionId)
    {
        if (isServer)
        {
            NetworkConnection connection = new NetworkConnection(connectionId);
            connections[connectionId] = connection;
            
            NetworkPlayer player = new NetworkPlayer(connectionId, $"Player_{connectionId}");
            players[connectionId] = player;
            
            Debug.Log($"Client {connectionId} connected");
            OnPlayerJoined?.Invoke(player);
            
            // Send welcome message
            SendWelcomeMessage(connectionId);
        }
        else if (isClient)
        {
            isConnected = true;
            reconnectAttempts = 0;
            
            NetworkConnection connection = new NetworkConnection(connectionId);
            connections[connectionId] = connection;
            
            Debug.Log("Connected to server");
            OnClientConnected?.Invoke();
        }
    }
    
    void HandleDataEvent(int connectionId, int channelId, byte[] data, int dataSize)
    {
        NetworkMessage message = NetworkMessage.Deserialize(data, dataSize);
        
        if (message != null)
        {
            ProcessNetworkMessage(connectionId, message);
        }
    }
    
    void HandleDisconnectionEvent(int connectionId)
    {
        if (connections.ContainsKey(connectionId))
        {
            connections.Remove(connectionId);
        }
        
        if (players.ContainsKey(connectionId))
        {
            NetworkPlayer player = players[connectionId];
            players.Remove(connectionId);
            
            Debug.Log($"Player {player.playerName} disconnected");
            OnPlayerLeft?.Invoke(player);
        }
        
        if (isClient)
        {
            isConnected = false;
            Debug.Log("Disconnected from server");
            OnClientDisconnected?.Invoke();
        }
    }
    
    void ProcessNetworkMessage(int connectionId, NetworkMessage message)
    {
        switch (message.messageType)
        {
            case NetworkMessageType.PlayerData:
                HandlePlayerDataMessage(connectionId, message);
                break;
                
            case NetworkMessageType.GameState:
                HandleGameStateMessage(connectionId, message);
                break;
                
            case NetworkMessageType.ChatMessage:
                HandleChatMessage(connectionId, message);
                break;
                
            case NetworkMessageType.Heartbeat:
                HandleHeartbeatMessage(connectionId, message);
                break;
                
            case NetworkMessageType.Custom:
                HandleCustomMessage(connectionId, message);
                break;
        }
    }
    
    void SendWelcomeMessage(int connectionId)
    {
        NetworkMessage welcome = new NetworkMessage
        {
            messageType = NetworkMessageType.Welcome,
            data = $"Welcome to the server! Your ID is {connectionId}"
        };
        
        SendMessage(connectionId, welcome, 0); // Reliable channel
    }
    
    public void SendMessage(int connectionId, NetworkMessage message, int channelId = 0)
    {
        byte[] data = NetworkMessage.Serialize(message);
        
        if (data != null)
        {
            byte error;
            NetworkTransport.Send(hostId, connectionId, channelId, data, data.Length, out error);
            
            if (error != (byte)NetworkError.Ok)
            {
                Debug.LogError($"Failed to send message: {(NetworkError)error}");
            }
        }
    }
    
    public void BroadcastMessage(NetworkMessage message, int channelId = 0)
    {
        if (!isServer)
        {
            Debug.LogWarning("Only server can broadcast messages");
            return;
        }
        
        foreach (int connectionId in connections.Keys)
        {
            SendMessage(connectionId, message, channelId);
        }
    }
    
    void HandlePlayerDataMessage(int connectionId, NetworkMessage message)
    {
        if (players.ContainsKey(connectionId))
        {
            // Update player data
            PlayerData playerData = JsonUtility.FromJson<PlayerData>(message.data);
            players[connectionId].UpdateData(playerData);
            
            // Broadcast to other clients if server
            if (isServer)
            {
                BroadcastMessage(message, 1); // Unreliable channel for frequent updates
            }
        }
    }
    
    void HandleGameStateMessage(int connectionId, NetworkMessage message)
    {
        GameStateData gameState = JsonUtility.FromJson<GameStateData>(message.data);
        
        // Update local game state
        if (GameStateManager.Instance != null)
        {
            GameStateManager.Instance.SyncNetworkState(gameState);
        }
    }
    
    void HandleChatMessage(int connectionId, NetworkMessage message)
    {
        ChatMessageData chatData = JsonUtility.FromJson<ChatMessageData>(message.data);
        
        if (isServer)
        {
            // Add sender info and broadcast
            if (players.ContainsKey(connectionId))
            {
                chatData.senderName = players[connectionId].playerName;
                
                NetworkMessage broadcastMessage = new NetworkMessage
                {
                    messageType = NetworkMessageType.ChatMessage,
                    data = JsonUtility.ToJson(chatData)
                };
                
                BroadcastMessage(broadcastMessage, 0);
            }
        }
        else
        {
            // Display chat message
            if (ChatManager.Instance != null)
            {
                ChatManager.Instance.DisplayMessage(chatData);
            }
        }
    }
    
    void HandleHeartbeatMessage(int connectionId, NetworkMessage message)
    {
        if (connections.ContainsKey(connectionId))
        {
            connections[connectionId].lastHeartbeat = Time.time;
        }
    }
    
    void HandleCustomMessage(int connectionId, NetworkMessage message)
    {
        // Handle custom game-specific messages
        Debug.Log($"Received custom message from {connectionId}: {message.data}");
    }
    
    IEnumerator HeartbeatCoroutine()
    {
        while (true)
        {
            yield return new WaitForSeconds(heartbeatInterval);
            
            if (isConnected)
            {
                NetworkMessage heartbeat = new NetworkMessage
                {
                    messageType = NetworkMessageType.Heartbeat,
                    data = Time.time.ToString()
                };
                
                if (isServer)
                {
                    BroadcastMessage(heartbeat, 1);
                }
                else if (isClient && connections.Count > 0)
                {
                    int connectionId = connections.Keys.GetEnumerator().Current;
                    SendMessage(connectionId, heartbeat, 1);
                }
            }
            
            // Check for timed out connections
            if (isServer)
            {
                CheckConnectionTimeouts();
            }
        }
    }
    
    void CheckConnectionTimeouts()
    {
        List<int> timedOutConnections = new List<int>();
        
        foreach (var kvp in connections)
        {
            if (Time.time - kvp.Value.lastHeartbeat > connectionTimeout)
            {
                timedOutConnections.Add(kvp.Key);
            }
        }
        
        foreach (int connectionId in timedOutConnections)
        {
            Debug.Log($"Connection {connectionId} timed out");
            DisconnectClient(connectionId);
        }
    }
    
    void DisconnectClient(int connectionId)
    {
        byte error;
        NetworkTransport.Disconnect(hostId, connectionId, out error);
        
        if (connections.ContainsKey(connectionId))
        {
            connections.Remove(connectionId);
        }
        
        if (players.ContainsKey(connectionId))
        {
            NetworkPlayer player = players[connectionId];
            players.Remove(connectionId);
            OnPlayerLeft?.Invoke(player);
        }
    }
    
    public void SendChatMessage(string message)
    {
        ChatMessageData chatData = new ChatMessageData
        {
            message = message,
            timestamp = System.DateTime.Now.ToString("HH:mm:ss")
        };
        
        NetworkMessage networkMessage = new NetworkMessage
        {
            messageType = NetworkMessageType.ChatMessage,
            data = JsonUtility.ToJson(chatData)
        };
        
        if (isClient && connections.Count > 0)
        {
            int connectionId = connections.Keys.GetEnumerator().Current;
            SendMessage(connectionId, networkMessage, 0);
        }
    }
    
    public List<NetworkPlayer> GetConnectedPlayers()
    {
        return new List<NetworkPlayer>(players.Values);
    }
    
    public bool IsServer() => isServer;
    public bool IsClient() => isClient;
    public bool IsConnected() => isConnected;
    public int GetConnectionCount() => connections.Count;
    
    void OnApplicationQuit()
    {
        if (isServer)
        {
            StopServer();
        }
        else if (isClient)
        {
            DisconnectFromServer();
        }
        
        NetworkTransport.Shutdown();
    }
}

// Network data structures
public enum NetworkTransport { TCP, UDP }

public enum NetworkMessageType
{
    Welcome,
    PlayerData,
    GameState,
    ChatMessage,
    Heartbeat,
    Custom
}

[System.Serializable]
public class NetworkMessage
{
    public NetworkMessageType messageType;
    public string data;
    public float timestamp;
    
    public static byte[] Serialize(NetworkMessage message)
    {
        try
        {
            message.timestamp = Time.time;
            string json = JsonUtility.ToJson(message);
            return System.Text.Encoding.UTF8.GetBytes(json);
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Failed to serialize message: {e.Message}");
            return null;
        }
    }
    
    public static NetworkMessage Deserialize(byte[] data, int dataSize)
    {
        try
        {
            string json = System.Text.Encoding.UTF8.GetString(data, 0, dataSize);
            return JsonUtility.FromJson<NetworkMessage>(json);
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Failed to deserialize message: {e.Message}");
            return null;
        }
    }
}

[System.Serializable]
public class NetworkConnection
{
    public int connectionId;
    public float lastHeartbeat;
    public bool isAuthenticated;
    
    public NetworkConnection(int id)
    {
        connectionId = id;
        lastHeartbeat = Time.time;
        isAuthenticated = false;
    }
}

[System.Serializable]
public class NetworkPlayer
{
    public int connectionId;
    public string playerName;
    public Vector3 position;
    public Quaternion rotation;
    public PlayerState state;
    
    public NetworkPlayer(int id, string name)
    {
        connectionId = id;
        playerName = name;
        position = Vector3.zero;
        rotation = Quaternion.identity;
        state = PlayerState.Idle;
    }
    
    public void UpdateData(PlayerData data)
    {
        position = data.position;
        rotation = data.rotation;
        state = data.state;
    }
}

[System.Serializable]
public class PlayerData
{
    public Vector3 position;
    public Quaternion rotation;
    public PlayerState state;
    public float health;
    public int score;
}

[System.Serializable]
public class GameStateData
{
    public float gameTime;
    public int gameScore;
    public GamePhase currentPhase;
    public List<ObjectState> syncedObjects;
}

[System.Serializable]
public class ObjectState
{
    public string objectId;
    public Vector3 position;
    public Quaternion rotation;
    public bool isActive;
}

[System.Serializable]
public class ChatMessageData
{
    public string senderName;
    public string message;
    public string timestamp;
}

public enum PlayerState { Idle, Moving, Attacking, Dead }
public enum GamePhase { Lobby, Playing, Paused, Ended }

// Network synchronization component
public class NetworkSync : MonoBehaviour
{
    [Header("Sync Settings")]
    public bool syncPosition = true;
    public bool syncRotation = true;
    public bool syncScale = false;
    public float sendRate = 10f;
    
    private Vector3 networkPosition;
    private Quaternion networkRotation;
    private Vector3 networkScale;
    private float lastSendTime;
    
    void Start()
    {
        networkPosition = transform.position;
        networkRotation = transform.rotation;
        networkScale = transform.localScale;
    }
    
    void Update()
    {
        if (NetworkManager.Instance == null) return;
        
        if (NetworkManager.Instance.IsServer())
        {
            // Server sends authoritative data
            if (Time.time - lastSendTime > 1f / sendRate)
            {
                SendTransformData();
                lastSendTime = Time.time;
            }
        }
        else
        {
            // Client interpolates to network position
            InterpolateTransform();
        }
    }
    
    void SendTransformData()
    {
        ObjectState state = new ObjectState
        {
            objectId = gameObject.name,
            position = transform.position,
            rotation = transform.rotation,
            isActive = gameObject.activeInHierarchy
        };
        
        NetworkMessage message = new NetworkMessage
        {
            messageType = NetworkMessageType.Custom,
            data = JsonUtility.ToJson(state)
        };
        
        NetworkManager.Instance.BroadcastMessage(message, 1);
    }
    
    void InterpolateTransform()
    {
        if (syncPosition)
        {
            transform.position = Vector3.Lerp(transform.position, networkPosition, Time.deltaTime * 10f);
        }
        
        if (syncRotation)
        {
            transform.rotation = Quaternion.Lerp(transform.rotation, networkRotation, Time.deltaTime * 10f);
        }
        
        if (syncScale)
        {
            transform.localScale = Vector3.Lerp(transform.localScale, networkScale, Time.deltaTime * 10f);
        }
    }
    
    public void OnNetworkTransformUpdate(ObjectState state)
    {
        networkPosition = state.position;
        networkRotation = state.rotation;
        gameObject.SetActive(state.isActive);
    }
}
```

## 🚀 AI/LLM Integration
- Automatically optimize network message frequency based on importance
- Generate lag compensation algorithms
- Create intelligent matchmaking and server selection

## 💡 Key Benefits
- Automated network connection management
- Real-time synchronization system
- Robust error handling and reconnection