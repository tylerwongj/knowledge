# 03-WebSocket-Real-Time-Communication.md

## 🎯 Learning Objectives
- Master WebSocket integration for real-time Unity multiplayer communication
- Implement reliable message queuing and connection management systems
- Design efficient binary protocol handling for game data synchronization
- Develop robust reconnection strategies and offline support mechanisms

## 🔧 Unity WebSocket Implementation

### WebSocket Connection Manager
```csharp
// Scripts/Networking/WebSocketManager.cs
using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using WebSocketSharp;
using Newtonsoft.Json;

public class WebSocketManager : MonoBehaviour
{
    [Header("WebSocket Configuration")]
    [SerializeField] private string serverUrl = "wss://api.yourgame.com/ws";
    [SerializeField] private float connectionTimeout = 10f;
    [SerializeField] private float heartbeatInterval = 30f;
    [SerializeField] private int maxReconnectAttempts = 5;
    [SerializeField] private float reconnectDelay = 2f;
    [SerializeField] private bool enableAutoReconnect = true;
    [SerializeField] private bool enableMessageQueue = true;
    
    public static WebSocketManager Instance { get; private set; }
    
    // Events
    public System.Action OnConnected;
    public System.Action OnDisconnected;
    public System.Action<string> OnError;
    public System.Action<WebSocketMessage> OnMessageReceived;
    public System.Action<ConnectionState> OnConnectionStateChanged;
    
    // Properties
    public ConnectionState State { get; private set; } = ConnectionState.Disconnected;
    public bool IsConnected => State == ConnectionState.Connected;
    public string SessionId { get; private set; }
    public float Ping { get; private set; }
    
    public enum ConnectionState
    {
        Disconnected,
        Connecting,
        Connected,
        Reconnecting,
        Error
    }
    
    [System.Serializable]
    public class WebSocketMessage
    {
        public string type;
        public string id;
        public object data;
        public DateTime timestamp;
        
        public WebSocketMessage()
        {
            id = Guid.NewGuid().ToString();
            timestamp = DateTime.UtcNow;
        }
        
        public T GetData<T>()
        {
            if (data is Newtonsoft.Json.Linq.JObject jObject)
            {
                return jObject.ToObject<T>();
            }
            return JsonConvert.DeserializeObject<T>(data.ToString());
        }
    }
    
    private WebSocket webSocket;
    private Queue<WebSocketMessage> messageQueue;
    private Queue<WebSocketMessage> outgoingQueue;
    private Dictionary<string, System.Action<WebSocketMessage>> messageHandlers;
    private Dictionary<string, System.Action<WebSocketMessage>> oneTimeHandlers;
    private Coroutine heartbeatCoroutine;
    private Coroutine reconnectCoroutine;
    private int reconnectAttempts = 0;
    private DateTime lastPingTime;
    
    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            Initialize();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    private void Initialize()
    {
        messageQueue = new Queue<WebSocketMessage>();
        outgoingQueue = new Queue<WebSocketMessage>();
        messageHandlers = new Dictionary<string, System.Action<WebSocketMessage>>();
        oneTimeHandlers = new Dictionary<string, System.Action<WebSocketMessage>>();
        
        // Register built-in message handlers
        RegisterHandler("pong", HandlePongMessage);
        RegisterHandler("session", HandleSessionMessage);
        RegisterHandler("error", HandleErrorMessage);
    }
    
    // Connection Management
    public void Connect(string customUrl = null)
    {
        if (State == ConnectionState.Connected || State == ConnectionState.Connecting)
        {
            Debug.LogWarning("[WebSocket] Already connected or connecting");
            return;
        }
        
        string url = customUrl ?? serverUrl;
        
        // Add authentication token if available
        if (AuthenticationManager.Instance != null && AuthenticationManager.Instance.IsAuthenticated)
        {
            var authHeader = AuthenticationManager.Instance.GetAuthorizationHeader();
            if (!string.IsNullOrEmpty(authHeader))
            {
                url += $"?token={authHeader.Replace("Bearer ", "")}";
            }
        }
        
        SetConnectionState(ConnectionState.Connecting);
        
        try
        {
            webSocket = new WebSocket(url);
            
            webSocket.OnOpen += OnWebSocketOpen;
            webSocket.OnMessage += OnWebSocketMessage;
            webSocket.OnError += OnWebSocketError;
            webSocket.OnClose += OnWebSocketClose;
            
            Debug.Log($"[WebSocket] Connecting to {url}");
            webSocket.ConnectAsync();
            
            // Start connection timeout
            StartCoroutine(ConnectionTimeoutCoroutine());
        }
        catch (Exception e)
        {
            Debug.LogError($"[WebSocket] Connection failed: {e.Message}");
            SetConnectionState(ConnectionState.Error);
            OnError?.Invoke(e.Message);
        }
    }
    
    public void Disconnect()
    {
        enableAutoReconnect = false;
        reconnectAttempts = 0;
        
        if (reconnectCoroutine != null)
        {
            StopCoroutine(reconnectCoroutine);
            reconnectCoroutine = null;
        }
        
        if (webSocket != null && webSocket.IsAlive)
        {
            Debug.Log("[WebSocket] Disconnecting...");
            webSocket.Close();
        }
        else
        {
            SetConnectionState(ConnectionState.Disconnected);
        }
    }
    
    // Message Sending
    public void Send(string messageType, object data = null)
    {
        var message = new WebSocketMessage
        {
            type = messageType,
            data = data
        };
        
        Send(message);
    }
    
    public void Send(WebSocketMessage message)
    {
        if (IsConnected)
        {
            try
            {
                string jsonMessage = JsonConvert.SerializeObject(message);
                webSocket.Send(jsonMessage);
                
                Debug.Log($"[WebSocket] Sent: {message.type} (ID: {message.id})");
            }
            catch (Exception e)
            {
                Debug.LogError($"[WebSocket] Send failed: {e.Message}");
                
                if (enableMessageQueue)
                {
                    outgoingQueue.Enqueue(message);
                    Debug.Log($"[WebSocket] Message queued for retry: {message.type}");
                }
            }
        }
        else if (enableMessageQueue)
        {
            outgoingQueue.Enqueue(message);
            Debug.Log($"[WebSocket] Message queued (not connected): {message.type}");
        }
        else
        {
            Debug.LogWarning($"[WebSocket] Cannot send message '{message.type}' - not connected");
        }
    }
    
    public void SendBinary(byte[] data)
    {
        if (IsConnected)
        {
            try
            {
                webSocket.Send(data);
                Debug.Log($"[WebSocket] Sent binary data: {data.Length} bytes");
            }
            catch (Exception e)
            {
                Debug.LogError($"[WebSocket] Binary send failed: {e.Message}");
            }
        }
        else
        {
            Debug.LogWarning("[WebSocket] Cannot send binary data - not connected");
        }
    }
    
    // Message Handling
    public void RegisterHandler(string messageType, System.Action<WebSocketMessage> handler)
    {
        messageHandlers[messageType] = handler;
        Debug.Log($"[WebSocket] Registered handler for: {messageType}");
    }
    
    public void UnregisterHandler(string messageType)
    {
        messageHandlers.Remove(messageType);
        Debug.Log($"[WebSocket] Unregistered handler for: {messageType}");
    }
    
    public void RegisterOneTimeHandler(string messageId, System.Action<WebSocketMessage> handler)
    {
        oneTimeHandlers[messageId] = handler;
    }
    
    public void SendWithResponse<T>(string messageType, object data, System.Action<T> onResponse, 
        System.Action<string> onError = null, float timeout = 10f)
    {
        var message = new WebSocketMessage
        {
            type = messageType,
            data = data
        };
        
        // Register one-time handler for response
        RegisterOneTimeHandler(message.id, (response) =>
        {
            try
            {
                T responseData = response.GetData<T>();
                onResponse?.Invoke(responseData);
            }
            catch (Exception e)
            {
                Debug.LogError($"[WebSocket] Response parsing failed: {e.Message}");
                onError?.Invoke($"Response parsing failed: {e.Message}");
            }
        });
        
        // Set up timeout
        StartCoroutine(RequestTimeoutCoroutine(message.id, timeout, onError));
        
        Send(message);
    }
    
    // WebSocket Event Handlers
    private void OnWebSocketOpen(object sender, EventArgs e)
    {
        Debug.Log("[WebSocket] Connected successfully");
        SetConnectionState(ConnectionState.Connected);
        reconnectAttempts = 0;
        
        // Start heartbeat
        if (heartbeatCoroutine != null)
        {
            StopCoroutine(heartbeatCoroutine);
        }
        heartbeatCoroutine = StartCoroutine(HeartbeatCoroutine());
        
        // Process queued messages
        ProcessOutgoingQueue();
        
        OnConnected?.Invoke();
    }
    
    private void OnWebSocketMessage(object sender, MessageEventArgs e)
    {
        try
        {
            if (e.IsBinary)
            {
                HandleBinaryMessage(e.RawData);
            }
            else
            {
                var message = JsonConvert.DeserializeObject<WebSocketMessage>(e.Data);
                HandleMessage(message);
            }
        }
        catch (Exception ex)
        {
            Debug.LogError($"[WebSocket] Message handling failed: {ex.Message}");
        }
    }
    
    private void OnWebSocketError(object sender, WebSocketSharp.ErrorEventArgs e)
    {
        Debug.LogError($"[WebSocket] Error: {e.Message}");
        SetConnectionState(ConnectionState.Error);
        OnError?.Invoke(e.Message);
        
        // Attempt reconnection if enabled
        if (enableAutoReconnect && reconnectAttempts < maxReconnectAttempts)
        {
            AttemptReconnection();
        }
    }
    
    private void OnWebSocketClose(object sender, CloseEventArgs e)
    {
        Debug.Log($"[WebSocket] Connection closed: {e.Reason} (Code: {e.Code})");
        SetConnectionState(ConnectionState.Disconnected);
        
        if (heartbeatCoroutine != null)
        {
            StopCoroutine(heartbeatCoroutine);
            heartbeatCoroutine = null;
        }
        
        OnDisconnected?.Invoke();
        
        // Attempt reconnection if it wasn't a clean close and reconnection is enabled
        if (!e.WasClean && enableAutoReconnect && reconnectAttempts < maxReconnectAttempts)
        {
            AttemptReconnection();
        }
    }
    
    // Message Processing
    private void HandleMessage(WebSocketMessage message)
    {
        Debug.Log($"[WebSocket] Received: {message.type} (ID: {message.id})");
        
        // Check for one-time handlers first (for request-response patterns)
        if (oneTimeHandlers.ContainsKey(message.id))
        {
            var handler = oneTimeHandlers[message.id];
            oneTimeHandlers.Remove(message.id);
            handler?.Invoke(message);
            return;
        }
        
        // Process with registered handlers
        if (messageHandlers.ContainsKey(message.type))
        {
            messageHandlers[message.type]?.Invoke(message);
        }
        else
        {
            Debug.LogWarning($"[WebSocket] No handler registered for message type: {message.type}");
        }
        
        // Add to message queue for external processing
        if (enableMessageQueue)
        {
            messageQueue.Enqueue(message);
        }
        
        // Notify global message received event
        OnMessageReceived?.Invoke(message);
    }
    
    private void HandleBinaryMessage(byte[] data)
    {
        Debug.Log($"[WebSocket] Received binary data: {data.Length} bytes");
        
        // Process binary data (implement according to your protocol)
        // This could be compressed game state, audio data, etc.
        ProcessBinaryData(data);
    }
    
    private void ProcessBinaryData(byte[] data)
    {
        // Example binary protocol handler
        if (data.Length < 4) return;
        
        // First 4 bytes could be message type identifier
        int messageType = BitConverter.ToInt32(data, 0);
        byte[] payload = new byte[data.Length - 4];
        Array.Copy(data, 4, payload, 0, payload.Length);
        
        switch (messageType)
        {
            case 1: // Game state update
                HandleGameStateUpdate(payload);
                break;
            case 2: // Player movement
                HandlePlayerMovement(payload);
                break;
            case 3: // Audio data
                HandleAudioData(payload);
                break;
            default:
                Debug.LogWarning($"[WebSocket] Unknown binary message type: {messageType}");
                break;
        }
    }
    
    // Built-in Message Handlers
    private void HandlePongMessage(WebSocketMessage message)
    {
        Ping = (float)(DateTime.UtcNow - lastPingTime).TotalMilliseconds;
        Debug.Log($"[WebSocket] Ping: {Ping}ms");
    }
    
    private void HandleSessionMessage(WebSocketMessage message)
    {
        var sessionData = message.GetData<SessionData>();
        SessionId = sessionData.sessionId;
        Debug.Log($"[WebSocket] Session established: {SessionId}");
    }
    
    private void HandleErrorMessage(WebSocketMessage message)
    {
        var errorData = message.GetData<ErrorData>();
        Debug.LogError($"[WebSocket] Server error: {errorData.message}");
        OnError?.Invoke(errorData.message);
    }
    
    // Connection State Management
    private void SetConnectionState(ConnectionState newState)
    {
        if (State != newState)
        {
            State = newState;
            Debug.Log($"[WebSocket] State changed to: {newState}");
            OnConnectionStateChanged?.Invoke(newState);
        }
    }
    
    private void AttemptReconnection()
    {
        if (reconnectCoroutine != null)
        {
            StopCoroutine(reconnectCoroutine);
        }
        
        reconnectCoroutine = StartCoroutine(ReconnectionCoroutine());
    }
    
    private IEnumerator ReconnectionCoroutine()
    {
        SetConnectionState(ConnectionState.Reconnecting);
        
        while (reconnectAttempts < maxReconnectAttempts && enableAutoReconnect)
        {
            reconnectAttempts++;
            float delay = reconnectDelay * Mathf.Pow(2, reconnectAttempts - 1); // Exponential backoff
            
            Debug.Log($"[WebSocket] Reconnection attempt {reconnectAttempts}/{maxReconnectAttempts} in {delay}s");
            yield return new WaitForSeconds(delay);
            
            try
            {
                if (webSocket != null)
                {
                    webSocket.Close();
                }
                
                Connect();
                yield break; // Exit if connection attempt started successfully
            }
            catch (Exception e)
            {
                Debug.LogError($"[WebSocket] Reconnection attempt failed: {e.Message}");
            }
        }
        
        Debug.LogError("[WebSocket] Max reconnection attempts reached");
        SetConnectionState(ConnectionState.Error);
    }
    
    // Utility Coroutines
    private IEnumerator HeartbeatCoroutine()
    {
        while (IsConnected)
        {
            yield return new WaitForSeconds(heartbeatInterval);
            
            if (IsConnected)
            {
                lastPingTime = DateTime.UtcNow;
                Send("ping");
            }
        }
    }
    
    private IEnumerator ConnectionTimeoutCoroutine()
    {
        yield return new WaitForSeconds(connectionTimeout);
        
        if (State == ConnectionState.Connecting)
        {
            Debug.LogError("[WebSocket] Connection timeout");
            SetConnectionState(ConnectionState.Error);
            OnError?.Invoke("Connection timeout");
            
            if (webSocket != null)
            {
                webSocket.Close();
            }
        }
    }
    
    private IEnumerator RequestTimeoutCoroutine(string messageId, float timeout, System.Action<string> onError)
    {
        yield return new WaitForSeconds(timeout);
        
        if (oneTimeHandlers.ContainsKey(messageId))
        {
            oneTimeHandlers.Remove(messageId);
            onError?.Invoke("Request timeout");
        }
    }
    
    private void ProcessOutgoingQueue()
    {
        while (outgoingQueue.Count > 0 && IsConnected)
        {
            var message = outgoingQueue.Dequeue();
            Send(message);
        }
    }
    
    // Binary Protocol Handlers (Examples)
    private void HandleGameStateUpdate(byte[] data)
    {
        // Deserialize game state from binary data
        // This would be implemented based on your specific protocol
        Debug.Log($"[WebSocket] Processing game state update: {data.Length} bytes");
    }
    
    private void HandlePlayerMovement(byte[] data)
    {
        // Deserialize player movement data
        Debug.Log($"[WebSocket] Processing player movement: {data.Length} bytes");
    }
    
    private void HandleAudioData(byte[] data)
    {
        // Process audio data for voice chat
        Debug.Log($"[WebSocket] Processing audio data: {data.Length} bytes");
    }
    
    // Public Utility Methods
    public WebSocketMessage GetNextMessage()
    {
        return messageQueue.Count > 0 ? messageQueue.Dequeue() : null;
    }
    
    public int GetQueuedMessageCount()
    {
        return messageQueue.Count;
    }
    
    public void ClearMessageQueue()
    {
        messageQueue.Clear();
        Debug.Log("[WebSocket] Message queue cleared");
    }
    
    // Data Classes
    [System.Serializable]
    private class SessionData
    {
        public string sessionId;
        public DateTime serverTime;
    }
    
    [System.Serializable]
    private class ErrorData
    {
        public string message;
        public int code;
    }
    
    private void OnApplicationFocus(bool hasFocus)
    {
        if (!hasFocus && IsConnected)
        {
            // Pause heartbeat when app loses focus
            if (heartbeatCoroutine != null)
            {
                StopCoroutine(heartbeatCoroutine);
                heartbeatCoroutine = null;
            }
        }
        else if (hasFocus && IsConnected)
        {
            // Resume heartbeat when app gains focus
            if (heartbeatCoroutine == null)
            {
                heartbeatCoroutine = StartCoroutine(HeartbeatCoroutine());
            }
        }
    }
    
    private void OnApplicationPause(bool pauseStatus)
    {
        OnApplicationFocus(!pauseStatus);
    }
    
    private void OnDestroy()
    {
        Disconnect();
    }
}
```

### Real-Time Game Communication Service
```csharp
// Scripts/Services/RealtimeGameService.cs
using System;
using System.Collections.Generic;
using UnityEngine;

public class RealtimeGameService : MonoBehaviour
{
    [Header("Game Communication Settings")]
    [SerializeField] private float positionUpdateRate = 20f; // Updates per second
    [SerializeField] private float rotationUpdateRate = 10f;
    [SerializeField] private bool enableDeltaCompression = true;
    [SerializeField] private float compressionThreshold = 0.01f;
    
    public static RealtimeGameService Instance { get; private set; }
    
    // Events
    public System.Action<string, PlayerState> OnPlayerStateUpdated;
    public System.Action<string, GameEvent> OnGameEventReceived;
    public System.Action<string> OnPlayerJoined;
    public System.Action<string> OnPlayerLeft;
    public System.Action<MatchState> OnMatchStateUpdated;
    
    [System.Serializable]
    public class PlayerState
    {
        public string playerId;
        public Vector3 position;
        public Quaternion rotation;
        public Vector3 velocity;
        public int health;
        public int score;
        public string currentAction;
        public Dictionary<string, object> customData;
        public DateTime timestamp;
    }
    
    [System.Serializable]
    public class GameEvent
    {
        public string eventType;
        public string sourcePlayerId;
        public string targetPlayerId;
        public Vector3 position;
        public object eventData;
        public DateTime timestamp;
    }
    
    [System.Serializable]
    public class MatchState
    {
        public string matchId;
        public string gameMode;
        public int currentRound;
        public float timeRemaining;
        public List<PlayerScore> scores;
        public string matchStatus;
        public Dictionary<string, object> gameSettings;
    }
    
    [System.Serializable]
    public class PlayerScore
    {
        public string playerId;
        public int score;
        public int kills;
        public int deaths;
        public float playtime;
    }
    
    private Dictionary<string, PlayerState> playerStates;
    private PlayerState lastSentState;
    private float lastPositionUpdate;
    private float lastRotationUpdate;
    private string currentMatchId;
    
    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            Initialize();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    private void Initialize()
    {
        playerStates = new Dictionary<string, PlayerState>();
        
        // Register WebSocket message handlers
        if (WebSocketManager.Instance != null)
        {
            WebSocketManager.Instance.RegisterHandler("player_state", HandlePlayerStateMessage);
            WebSocketManager.Instance.RegisterHandler("game_event", HandleGameEventMessage);
            WebSocketManager.Instance.RegisterHandler("player_joined", HandlePlayerJoinedMessage);
            WebSocketManager.Instance.RegisterHandler("player_left", HandlePlayerLeftMessage);
            WebSocketManager.Instance.RegisterHandler("match_state", HandleMatchStateMessage);
        }
    }
    
    private void Update()
    {
        // Send periodic position updates
        if (ShouldSendPositionUpdate())
        {
            SendPlayerPosition();
        }
        
        // Send periodic rotation updates
        if (ShouldSendRotationUpdate())
        {
            SendPlayerRotation();
        }
    }
    
    // Player State Management
    public void JoinMatch(string matchId, System.Action<bool> onComplete = null)
    {
        currentMatchId = matchId;
        
        var joinData = new
        {
            matchId = matchId,
            playerId = GetCurrentPlayerId(),
            playerData = GetCurrentPlayerData()
        };
        
        WebSocketManager.Instance.SendWithResponse<JoinMatchResponse>(
            "join_match",
            joinData,
            (response) =>
            {
                Debug.Log($"[RealtimeGame] Joined match: {matchId}");
                onComplete?.Invoke(response.success);
                
                if (response.success)
                {
                    // Initialize with existing players
                    foreach (var player in response.existingPlayers)
                    {
                        playerStates[player.playerId] = player;
                        OnPlayerStateUpdated?.Invoke(player.playerId, player);
                    }
                }
            },
            (error) =>
            {
                Debug.LogError($"[RealtimeGame] Failed to join match: {error}");
                onComplete?.Invoke(false);
            }
        );
    }
    
    public void LeaveMatch()
    {
        if (string.IsNullOrEmpty(currentMatchId)) return;
        
        var leaveData = new
        {
            matchId = currentMatchId,
            playerId = GetCurrentPlayerId()
        };
        
        WebSocketManager.Instance.Send("leave_match", leaveData);
        
        currentMatchId = null;
        playerStates.Clear();
        
        Debug.Log("[RealtimeGame] Left match");
    }
    
    public void UpdatePlayerState(PlayerState newState)
    {
        if (string.IsNullOrEmpty(currentMatchId)) return;
        
        // Apply delta compression if enabled
        if (enableDeltaCompression && lastSentState != null)
        {
            var deltaState = CreateDeltaState(lastSentState, newState);
            if (deltaState != null)
            {
                WebSocketManager.Instance.Send("player_state_delta", deltaState);
                lastSentState = newState;
                return;
            }
        }
        
        // Send full state
        WebSocketManager.Instance.Send("player_state", newState);
        lastSentState = newState;
    }
    
    public void SendGameEvent(GameEvent gameEvent)
    {
        if (string.IsNullOrEmpty(currentMatchId)) return;
        
        gameEvent.sourcePlayerId = GetCurrentPlayerId();
        gameEvent.timestamp = DateTime.UtcNow;
        
        WebSocketManager.Instance.Send("game_event", gameEvent);
        
        Debug.Log($"[RealtimeGame] Sent game event: {gameEvent.eventType}");
    }
    
    // Specific Update Methods
    private void SendPlayerPosition()
    {
        var playerTransform = GetPlayerTransform();
        if (playerTransform == null) return;
        
        var positionUpdate = new
        {
            playerId = GetCurrentPlayerId(),
            position = playerTransform.position,
            velocity = GetPlayerVelocity(),
            timestamp = DateTime.UtcNow
        };
        
        WebSocketManager.Instance.Send("position_update", positionUpdate);
        lastPositionUpdate = Time.time;
    }
    
    private void SendPlayerRotation()
    {
        var playerTransform = GetPlayerTransform();
        if (playerTransform == null) return;
        
        var rotationUpdate = new
        {
            playerId = GetCurrentPlayerId(),
            rotation = playerTransform.rotation,
            timestamp = DateTime.UtcNow
        };
        
        WebSocketManager.Instance.Send("rotation_update", rotationUpdate);
        lastRotationUpdate = Time.time;
    }
    
    public void SendChatMessage(string message, string targetPlayerId = null)
    {
        var chatData = new
        {
            matchId = currentMatchId,
            senderId = GetCurrentPlayerId(),
            targetId = targetPlayerId, // null for broadcast
            message = message,
            timestamp = DateTime.UtcNow
        };
        
        WebSocketManager.Instance.Send("chat_message", chatData);
    }
    
    public void SendCustomAction(string actionType, object actionData)
    {
        var customAction = new
        {
            matchId = currentMatchId,
            playerId = GetCurrentPlayerId(),
            actionType = actionType,
            actionData = actionData,
            timestamp = DateTime.UtcNow
        };
        
        WebSocketManager.Instance.Send("custom_action", customAction);
    }
    
    // Message Handlers
    private void HandlePlayerStateMessage(WebSocketManager.WebSocketMessage message)
    {
        var playerState = message.GetData<PlayerState>();
        
        if (playerState.playerId != GetCurrentPlayerId())
        {
            playerStates[playerState.playerId] = playerState;
            OnPlayerStateUpdated?.Invoke(playerState.playerId, playerState);
        }
    }
    
    private void HandleGameEventMessage(WebSocketManager.WebSocketMessage message)
    {
        var gameEvent = message.GetData<GameEvent>();
        OnGameEventReceived?.Invoke(gameEvent.eventType, gameEvent);
        
        Debug.Log($"[RealtimeGame] Received game event: {gameEvent.eventType} from {gameEvent.sourcePlayerId}");
    }
    
    private void HandlePlayerJoinedMessage(WebSocketManager.WebSocketMessage message)
    {
        var joinData = message.GetData<PlayerJoinData>();
        
        playerStates[joinData.playerId] = joinData.playerState;
        OnPlayerJoined?.Invoke(joinData.playerId);
        
        Debug.Log($"[RealtimeGame] Player joined: {joinData.playerId}");
    }
    
    private void HandlePlayerLeftMessage(WebSocketManager.WebSocketMessage message)
    {
        var leaveData = message.GetData<PlayerLeaveData>();
        
        playerStates.Remove(leaveData.playerId);
        OnPlayerLeft?.Invoke(leaveData.playerId);
        
        Debug.Log($"[RealtimeGame] Player left: {leaveData.playerId}");
    }
    
    private void HandleMatchStateMessage(WebSocketManager.WebSocketMessage message)
    {
        var matchState = message.GetData<MatchState>();
        OnMatchStateUpdated?.Invoke(matchState);
        
        Debug.Log($"[RealtimeGame] Match state updated: {matchState.matchStatus}");
    }
    
    // Utility Methods
    private bool ShouldSendPositionUpdate()
    {
        return Time.time - lastPositionUpdate >= (1f / positionUpdateRate) && 
               HasPlayerMovedSignificantly();
    }
    
    private bool ShouldSendRotationUpdate()
    {
        return Time.time - lastRotationUpdate >= (1f / rotationUpdateRate) && 
               HasPlayerRotatedSignificantly();
    }
    
    private bool HasPlayerMovedSignificantly()
    {
        var playerTransform = GetPlayerTransform();
        if (playerTransform == null || lastSentState == null) return true;
        
        float distance = Vector3.Distance(playerTransform.position, lastSentState.position);
        return distance > compressionThreshold;
    }
    
    private bool HasPlayerRotatedSignificantly()
    {
        var playerTransform = GetPlayerTransform();
        if (playerTransform == null || lastSentState == null) return true;
        
        float angle = Quaternion.Angle(playerTransform.rotation, lastSentState.rotation);
        return angle > compressionThreshold * 57.2958f; // Convert to degrees
    }
    
    private object CreateDeltaState(PlayerState oldState, PlayerState newState)
    {
        var delta = new Dictionary<string, object>();
        bool hasChanges = false;
        
        // Check position
        if (Vector3.Distance(oldState.position, newState.position) > compressionThreshold)
        {
            delta["position"] = newState.position;
            hasChanges = true;
        }
        
        // Check rotation
        if (Quaternion.Angle(oldState.rotation, newState.rotation) > compressionThreshold * 57.2958f)
        {
            delta["rotation"] = newState.rotation;
            hasChanges = true;
        }
        
        // Check other properties
        if (oldState.health != newState.health)
        {
            delta["health"] = newState.health;
            hasChanges = true;
        }
        
        if (oldState.score != newState.score)
        {
            delta["score"] = newState.score;
            hasChanges = true;
        }
        
        if (oldState.currentAction != newState.currentAction)
        {
            delta["currentAction"] = newState.currentAction;
            hasChanges = true;
        }
        
        if (hasChanges)
        {
            delta["playerId"] = newState.playerId;
            delta["timestamp"] = newState.timestamp;
            return delta;
        }
        
        return null;
    }
    
    private string GetCurrentPlayerId()
    {
        return AuthenticationManager.Instance?.CurrentUserId ?? "unknown";
    }
    
    private Transform GetPlayerTransform()
    {
        // This would be implemented to return the current player's transform
        var player = GameObject.FindWithTag("Player");
        return player?.transform;
    }
    
    private Vector3 GetPlayerVelocity()
    {
        var player = GameObject.FindWithTag("Player");
        var rigidbody = player?.GetComponent<Rigidbody>();
        return rigidbody?.velocity ?? Vector3.zero;
    }
    
    private object GetCurrentPlayerData()
    {
        return new
        {
            username = AuthenticationManager.Instance?.CurrentUser?.username ?? "Unknown",
            level = 1, // Get from player data
            skin = "default" // Get from player customization
        };
    }
    
    // Public Getters
    public PlayerState GetPlayerState(string playerId)
    {
        return playerStates.ContainsKey(playerId) ? playerStates[playerId] : null;
    }
    
    public Dictionary<string, PlayerState> GetAllPlayerStates()
    {
        return new Dictionary<string, PlayerState>(playerStates);
    }
    
    public bool IsInMatch()
    {
        return !string.IsNullOrEmpty(currentMatchId);
    }
    
    public string GetCurrentMatchId()
    {
        return currentMatchId;
    }
    
    // Data Classes
    [System.Serializable]
    private class JoinMatchResponse
    {
        public bool success;
        public string message;
        public List<PlayerState> existingPlayers;
    }
    
    [System.Serializable]
    private class PlayerJoinData
    {
        public string playerId;
        public PlayerState playerState;
    }
    
    [System.Serializable]
    private class PlayerLeaveData
    {
        public string playerId;
        public string reason;
    }
    
    private void OnDestroy()
    {
        LeaveMatch();
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### WebSocket Protocol Design
```
PROMPT TEMPLATE - Real-time Protocol Design:

"Design a comprehensive WebSocket protocol for this Unity multiplayer game:

Game Details:
- Type: [FPS/Racing/MOBA/Battle Royale/etc.]
- Max Players: [4/16/64/100+]
- Update Frequency: [High/Medium/Low latency requirements]
- Platform: [Mobile/PC/Cross-platform]

Create protocol including:
1. Message format and serialization strategy
2. State synchronization and delta compression
3. Event-driven communication patterns
4. Binary vs JSON message optimization
5. Reconnection and state recovery mechanisms
6. Anti-cheat and validation considerations
7. Bandwidth optimization techniques
8. Scalability and performance characteristics
9. Error handling and fallback strategies"
```

### Connection Reliability Analysis
```
PROMPT TEMPLATE - Connection Management Optimization:

"Optimize this Unity WebSocket connection management:

```csharp
[PASTE YOUR WEBSOCKET CODE]
```

Network Conditions:
- Target Platforms: [Mobile/PC/Console]
- Network Quality: [Variable/Stable/Poor mobile networks]
- Latency Requirements: [< 50ms/< 100ms/< 500ms]
- Reliability Needs: [Mission critical/Important/Best effort]

Provide optimizations for:
1. Connection establishment and handshake
2. Heartbeat and keep-alive strategies
3. Reconnection logic and exponential backoff
4. Message queuing and persistence
5. Bandwidth usage optimization
6. Mobile network handling (WiFi/cellular switches)
7. Background/foreground state management
8. Error detection and recovery mechanisms"
```

## 💡 Key WebSocket Integration Principles

### Essential Real-time Communication Checklist
- **Connection reliability** - Robust reconnection and error handling
- **Message ordering** - Ensure proper sequencing of critical messages
- **Bandwidth optimization** - Use binary protocols and compression when needed
- **State synchronization** - Efficient delta updates and conflict resolution
- **Latency management** - Minimize round-trip times for critical actions
- **Security considerations** - Validate all incoming data and authenticate connections
- **Mobile optimization** - Handle network switches and background states
- **Scalability planning** - Design for concurrent connections and load balancing

### Common Unity WebSocket Challenges
1. **Connection management** - Handling disconnections and reconnections gracefully
2. **Message ordering** - Ensuring proper sequence of game state updates
3. **Bandwidth constraints** - Optimizing data transmission for mobile networks
4. **State synchronization** - Resolving conflicts between client and server state
5. **Mobile platform issues** - Background app behavior and network switching
6. **Security vulnerabilities** - Preventing message tampering and replay attacks
7. **Performance impact** - Managing CPU usage for high-frequency updates
8. **Cross-platform compatibility** - Consistent behavior across different platforms

This comprehensive WebSocket implementation provides Unity developers with production-ready real-time communication capabilities, enabling smooth multiplayer experiences with robust connection management, efficient data transmission, and excellent mobile performance characteristics.