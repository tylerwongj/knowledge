# @c-WebSocket-Real-time-Communication

## 🎯 Learning Objectives
- Implement WebSocket connections for real-time Unity multiplayer games
- Master bidirectional communication patterns and message handling
- Design scalable real-time architecture for multiplayer gaming
- Handle connection management, reconnection, and error scenarios

## 🔧 WebSocket Client Implementation

### Unity WebSocket Manager
```csharp
// Unity WebSocket Client Manager
using UnityEngine;
using System;
using System.Collections.Generic;
using System.Text;
using WebSocketSharp;
using Newtonsoft.Json;

public class WebSocketManager : MonoBehaviour
{
    [Header("WebSocket Configuration")]
    [SerializeField] private string serverUrl = "ws://localhost:8080";
    [SerializeField] private bool autoReconnect = true;
    [SerializeField] private int reconnectInterval = 5;
    [SerializeField] private int maxReconnectAttempts = 10;
    
    private WebSocket webSocket;
    private bool isConnecting = false;
    private int reconnectAttempts = 0;
    private Queue<string> messageQueue;
    private Dictionary<string, Action<WebSocketMessage>> messageHandlers;
    
    // Events
    public event Action OnConnected;
    public event Action OnDisconnected;
    public event Action<string> OnError;
    public event Action<WebSocketMessage> OnMessageReceived;
    
    void Start()
    {
        messageQueue = new Queue<string>();
        messageHandlers = new Dictionary<string, Action<WebSocketMessage>>();
        InitializeMessageHandlers();
    }
    
    void Update()
    {
        // Process queued messages on main thread
        while (messageQueue.Count > 0)
        {
            var message = messageQueue.Dequeue();
            ProcessMessage(message);
        }
    }
    
    public void Connect()
    {
        if (webSocket != null && (webSocket.ReadyState == WebSocketState.Open || webSocket.ReadyState == WebSocketState.Connecting))
        {
            Debug.LogWarning("WebSocket is already connected or connecting");
            return;
        }
        
        isConnecting = true;
        
        try
        {
            webSocket = new WebSocket(serverUrl);
            
            // Configure WebSocket
            webSocket.OnOpen += OnWebSocketOpen;
            webSocket.OnMessage += OnWebSocketMessage;
            webSocket.OnClose += OnWebSocketClose;
            webSocket.OnError += OnWebSocketError;
            
            // Set custom headers if needed
            webSocket.CustomHeaders = GetCustomHeaders();
            
            // Connect
            webSocket.ConnectAsync();
            Debug.Log($"Connecting to WebSocket server: {serverUrl}");
        }
        catch (Exception ex)
        {
            Debug.LogError($"Failed to initialize WebSocket connection: {ex.Message}");
            isConnecting = false;
            OnError?.Invoke(ex.Message);
        }
    }
    
    public void Disconnect()
    {
        autoReconnect = false;
        
        if (webSocket != null)
        {
            webSocket.Close();
            webSocket = null;
        }
    }
    
    public void SendMessage(string messageType, object data)
    {
        if (webSocket?.ReadyState != WebSocketState.Open)
        {
            Debug.LogWarning("WebSocket is not connected. Message queued for later.");
            return;
        }
        
        var message = new WebSocketMessage
        {
            Type = messageType,
            Data = data,
            Timestamp = DateTime.UtcNow,
            MessageId = Guid.NewGuid().ToString()
        };
        
        try
        {
            var json = JsonConvert.SerializeObject(message);
            webSocket.Send(json);
            
            Debug.Log($"Sent WebSocket message: {messageType}");
        }
        catch (Exception ex)
        {
            Debug.LogError($"Failed to send WebSocket message: {ex.Message}");
            OnError?.Invoke($"Send failed: {ex.Message}");
        }
    }
    
    public void RegisterMessageHandler(string messageType, Action<WebSocketMessage> handler)
    {
        messageHandlers[messageType] = handler;
    }
    
    public void UnregisterMessageHandler(string messageType)
    {
        messageHandlers.Remove(messageType);
    }
    
    private Dictionary<string, string> GetCustomHeaders()
    {
        var headers = new Dictionary<string, string>();
        
        // Add authentication if available
        var authToken = PlayerPrefs.GetString("auth_token", "");
        if (!string.IsNullOrEmpty(authToken))
        {
            headers["Authorization"] = $"Bearer {authToken}";
        }
        
        // Add player ID
        var playerId = PlayerPrefs.GetString("player_id", "");
        if (!string.IsNullOrEmpty(playerId))
        {
            headers["X-Player-ID"] = playerId;
        }
        
        // Add client version
        headers["X-Client-Version"] = Application.version;
        
        return headers;
    }
    
    private void OnWebSocketOpen(object sender, EventArgs e)
    {
        Debug.Log("WebSocket connection opened");
        isConnecting = false;
        reconnectAttempts = 0;
        
        // Send authentication message
        SendAuthenticationMessage();
        
        // Trigger connected event on main thread
        UnityMainThreadDispatcher.Instance.Enqueue(() => OnConnected?.Invoke());
    }
    
    private void OnWebSocketMessage(object sender, MessageEventArgs e)
    {
        // Queue message for processing on main thread
        messageQueue.Enqueue(e.Data);
    }
    
    private void OnWebSocketClose(object sender, CloseEventArgs e)
    {
        Debug.Log($"WebSocket connection closed: {e.Reason}");
        isConnecting = false;
        
        // Trigger disconnected event on main thread
        UnityMainThreadDispatcher.Instance.Enqueue(() => OnDisconnected?.Invoke());
        
        // Attempt reconnection if enabled
        if (autoReconnect && reconnectAttempts < maxReconnectAttempts)
        {
            reconnectAttempts++;
            Debug.Log($"Attempting reconnection ({reconnectAttempts}/{maxReconnectAttempts}) in {reconnectInterval} seconds");
            
            UnityMainThreadDispatcher.Instance.Enqueue(() => 
            {
                Invoke(nameof(AttemptReconnection), reconnectInterval);
            });
        }
    }
    
    private void OnWebSocketError(object sender, ErrorEventArgs e)
    {
        Debug.LogError($"WebSocket error: {e.Message}");
        isConnecting = false;
        
        // Trigger error event on main thread
        UnityMainThreadDispatcher.Instance.Enqueue(() => OnError?.Invoke(e.Message));
    }
    
    private void AttemptReconnection()
    {
        if (!autoReconnect) return;
        
        Debug.Log("Attempting to reconnect WebSocket");
        Connect();
    }
    
    private void ProcessMessage(string messageData)
    {
        try
        {
            var message = JsonConvert.DeserializeObject<WebSocketMessage>(messageData);
            
            Debug.Log($"Received WebSocket message: {message.Type}");
            
            // Trigger general message event
            OnMessageReceived?.Invoke(message);
            
            // Handle specific message types
            if (messageHandlers.ContainsKey(message.Type))
            {
                messageHandlers[message.Type].Invoke(message);
            }
            else
            {
                Debug.LogWarning($"No handler registered for message type: {message.Type}");
            }
        }
        catch (JsonException ex)
        {
            Debug.LogError($"Failed to parse WebSocket message: {ex.Message}");
        }
    }
    
    private void SendAuthenticationMessage()
    {
        var authToken = PlayerPrefs.GetString("auth_token", "");
        var playerId = PlayerPrefs.GetString("player_id", "");
        
        if (!string.IsNullOrEmpty(authToken) && !string.IsNullOrEmpty(playerId))
        {
            SendMessage("authenticate", new
            {
                token = authToken,
                playerId = playerId,
                clientVersion = Application.version
            });
        }
    }
    
    void OnDestroy()
    {
        Disconnect();
    }
    
    private void InitializeMessageHandlers()
    {
        // Register default message handlers
        RegisterMessageHandler("ping", HandlePingMessage);
        RegisterMessageHandler("authentication_result", HandleAuthenticationResult);
        RegisterMessageHandler("player_joined", HandlePlayerJoined);
        RegisterMessageHandler("player_left", HandlePlayerLeft);
        RegisterMessageHandler("game_state_update", HandleGameStateUpdate);
        RegisterMessageHandler("chat_message", HandleChatMessage);
    }
    
    private void HandlePingMessage(WebSocketMessage message)
    {
        // Respond to server ping with pong
        SendMessage("pong", new { timestamp = DateTime.UtcNow });
    }
    
    private void HandleAuthenticationResult(WebSocketMessage message)
    {
        var result = JsonConvert.DeserializeObject<AuthenticationResult>(message.Data.ToString());
        
        if (result.Success)
        {
            Debug.Log("WebSocket authentication successful");
            GameManager.Instance.OnWebSocketAuthenticated();
        }
        else
        {
            Debug.LogError($"WebSocket authentication failed: {result.ErrorMessage}");
            OnError?.Invoke($"Authentication failed: {result.ErrorMessage}");
        }
    }
    
    private void HandlePlayerJoined(WebSocketMessage message)
    {
        var playerData = JsonConvert.DeserializeObject<PlayerJoinedData>(message.Data.ToString());
        GameManager.Instance.OnPlayerJoined(playerData);
    }
    
    private void HandlePlayerLeft(WebSocketMessage message)
    {
        var playerData = JsonConvert.DeserializeObject<PlayerLeftData>(message.Data.ToString());
        GameManager.Instance.OnPlayerLeft(playerData);
    }
    
    private void HandleGameStateUpdate(WebSocketMessage message)
    {
        var gameState = JsonConvert.DeserializeObject<GameStateUpdate>(message.Data.ToString());
        GameManager.Instance.UpdateGameState(gameState);
    }
    
    private void HandleChatMessage(WebSocketMessage message)
    {
        var chatMessage = JsonConvert.DeserializeObject<ChatMessage>(message.Data.ToString());
        ChatManager.Instance.OnMessageReceived(chatMessage);
    }
}
```

### Real-time Game State Synchronization
```csharp
// Real-time Game State Synchronization
public class RealtimeGameSync : MonoBehaviour
{
    [Header("Sync Settings")]
    [SerializeField] private float syncInterval = 0.1f; // 10 FPS
    [SerializeField] private float maxSyncDistance = 1.0f;
    [SerializeField] private bool enablePrediction = true;
    
    private WebSocketManager webSocketManager;
    private Dictionary<string, PlayerState> remotePlayerStates;
    private Dictionary<string, PlayerController> localPlayers;
    private float lastSyncTime;
    
    void Start()
    {
        webSocketManager = FindObjectOfType<WebSocketManager>();
        remotePlayerStates = new Dictionary<string, PlayerState>();
        localPlayers = new Dictionary<string, PlayerController>();
        
        // Register for WebSocket events
        webSocketManager.RegisterMessageHandler("player_state_update", HandlePlayerStateUpdate);
        webSocketManager.RegisterMessageHandler("game_object_update", HandleGameObjectUpdate);
        webSocketManager.RegisterMessageHandler("player_action", HandlePlayerAction);
        
        // Start sync coroutine
        StartCoroutine(SyncGameStateRoutine());
    }
    
    private IEnumerator SyncGameStateRoutine()
    {
        while (true)
        {
            yield return new WaitForSeconds(syncInterval);
            
            if (webSocketManager != null && Time.time - lastSyncTime >= syncInterval)
            {
                SendLocalPlayerStates();
                lastSyncTime = Time.time;
            }
        }
    }
    
    private void SendLocalPlayerStates()
    {
        foreach (var kvp in localPlayers)
        {
            var playerId = kvp.Key;
            var playerController = kvp.Value;
            
            var playerState = new PlayerState
            {
                PlayerId = playerId,
                Position = playerController.transform.position,
                Rotation = playerController.transform.rotation,
                Velocity = playerController.GetComponent<Rigidbody>()?.velocity ?? Vector3.zero,
                Animation = playerController.GetCurrentAnimation(),
                Health = playerController.Health,
                Timestamp = DateTime.UtcNow
            };
            
            webSocketManager.SendMessage("player_state_update", playerState);
        }
    }
    
    private void HandlePlayerStateUpdate(WebSocketMessage message)
    {
        var playerState = JsonConvert.DeserializeObject<PlayerState>(message.Data.ToString());
        
        // Don't process our own state updates
        if (IsLocalPlayer(playerState.PlayerId))
            return;
            
        // Store remote player state
        remotePlayerStates[playerState.PlayerId] = playerState;
        
        // Apply state to game object
        ApplyRemotePlayerState(playerState);
    }
    
    private void ApplyRemotePlayerState(PlayerState playerState)
    {
        var remotePlayer = GetRemotePlayer(playerState.PlayerId);
        if (remotePlayer == null)
        {
            // Create remote player if it doesn't exist
            remotePlayer = CreateRemotePlayer(playerState.PlayerId);
        }
        
        // Calculate interpolation
        var targetPosition = playerState.Position;
        var targetRotation = playerState.Rotation;
        
        // Apply prediction if enabled
        if (enablePrediction)
        {
            var timeDelta = (float)(DateTime.UtcNow - playerState.Timestamp).TotalSeconds;
            targetPosition += playerState.Velocity * timeDelta;
        }
        
        // Smoothly interpolate to target state
        var currentPosition = remotePlayer.transform.position;
        var distance = Vector3.Distance(currentPosition, targetPosition);
        
        if (distance > maxSyncDistance)
        {
            // Teleport if too far away (likely a missed update)
            remotePlayer.transform.position = targetPosition;
            remotePlayer.transform.rotation = targetRotation;
        }
        else
        {
            // Smooth interpolation
            remotePlayer.transform.position = Vector3.Lerp(currentPosition, targetPosition, Time.deltaTime * 10f);
            remotePlayer.transform.rotation = Quaternion.Lerp(remotePlayer.transform.rotation, targetRotation, Time.deltaTime * 10f);
        }
        
        // Update animation and other properties
        var animator = remotePlayer.GetComponent<Animator>();
        if (animator != null && !string.IsNullOrEmpty(playerState.Animation))
        {
            animator.SetTrigger(playerState.Animation);
        }
        
        // Update health display
        var healthBar = remotePlayer.GetComponentInChildren<HealthBar>();
        if (healthBar != null)
        {
            healthBar.UpdateHealth(playerState.Health);
        }
    }
    
    private void HandleGameObjectUpdate(WebSocketMessage message)
    {
        var objectUpdate = JsonConvert.DeserializeObject<GameObjectUpdate>(message.Data.ToString());
        
        var gameObj = GameObject.Find(objectUpdate.ObjectId);
        if (gameObj != null)
        {
            // Apply transform updates
            if (objectUpdate.Position.HasValue)
                gameObj.transform.position = objectUpdate.Position.Value;
                
            if (objectUpdate.Rotation.HasValue)
                gameObj.transform.rotation = objectUpdate.Rotation.Value;
                
            if (objectUpdate.Scale.HasValue)
                gameObj.transform.localScale = objectUpdate.Scale.Value;
                
            // Apply property updates
            if (objectUpdate.Properties != null)
            {
                ApplyObjectProperties(gameObj, objectUpdate.Properties);
            }
        }
    }
    
    private void HandlePlayerAction(WebSocketMessage message)
    {
        var playerAction = JsonConvert.DeserializeObject<PlayerAction>(message.Data.ToString());
        
        // Don't process our own actions
        if (IsLocalPlayer(playerAction.PlayerId))
            return;
            
        var remotePlayer = GetRemotePlayer(playerAction.PlayerId);
        if (remotePlayer != null)
        {
            ExecutePlayerAction(remotePlayer, playerAction);
        }
    }
    
    private void ExecutePlayerAction(GameObject player, PlayerAction action)
    {
        switch (action.ActionType)
        {
            case "attack":
                var combatSystem = player.GetComponent<CombatSystem>();
                combatSystem?.PerformAttack(action.TargetId, action.GetVector3Parameter("direction"));
                break;
                
            case "cast_spell":
                var magicSystem = player.GetComponent<MagicSystem>();
                magicSystem?.CastSpell(action.GetStringParameter("spellId"), action.GetVector3Parameter("targetPosition"));
                break;
                
            case "use_item":
                var inventory = player.GetComponent<PlayerInventory>();
                inventory?.UseItem(action.GetStringParameter("itemId"));
                break;
                
            case "emote":
                var emoteSystem = player.GetComponent<EmoteSystem>();
                emoteSystem?.PlayEmote(action.GetStringParameter("emoteId"));
                break;
        }
    }
    
    public void RegisterLocalPlayer(string playerId, PlayerController playerController)
    {
        localPlayers[playerId] = playerController;
    }
    
    public void UnregisterLocalPlayer(string playerId)
    {
        localPlayers.Remove(playerId);
    }
    
    public void SendPlayerAction(string actionType, Dictionary<string, object> parameters = null)
    {
        var action = new PlayerAction
        {
            PlayerId = GameManager.Instance.CurrentPlayerId,
            ActionType = actionType,
            Parameters = parameters ?? new Dictionary<string, object>(),
            Timestamp = DateTime.UtcNow
        };
        
        webSocketManager.SendMessage("player_action", action);
    }
    
    private bool IsLocalPlayer(string playerId)
    {
        return localPlayers.ContainsKey(playerId);
    }
    
    private GameObject GetRemotePlayer(string playerId)
    {
        return GameObject.Find($"RemotePlayer_{playerId}");
    }
    
    private GameObject CreateRemotePlayer(string playerId)
    {
        var remotePlayerPrefab = Resources.Load<GameObject>("RemotePlayerPrefab");
        var remotePlayer = Instantiate(remotePlayerPrefab);
        remotePlayer.name = $"RemotePlayer_{playerId}";
        
        // Initialize remote player components
        var networkPlayer = remotePlayer.GetComponent<NetworkPlayer>();
        if (networkPlayer != null)
        {
            networkPlayer.Initialize(playerId);
        }
        
        return remotePlayer;
    }
    
    private void ApplyObjectProperties(GameObject gameObj, Dictionary<string, object> properties)
    {
        foreach (var property in properties)
        {
            switch (property.Key)
            {
                case "color":
                    var renderer = gameObj.GetComponent<Renderer>();
                    if (renderer != null && ColorUtility.TryParseHtmlString(property.Value.ToString(), out Color color))
                    {
                        renderer.material.color = color;
                    }
                    break;
                    
                case "active":
                    if (bool.TryParse(property.Value.ToString(), out bool active))
                    {
                        gameObj.SetActive(active);
                    }
                    break;
                    
                case "text":
                    var textMesh = gameObj.GetComponent<TextMesh>();
                    if (textMesh != null)
                    {
                        textMesh.text = property.Value.ToString();
                    }
                    break;
            }
        }
    }
}
```

### Chat System with WebSocket
```csharp
// Real-time Chat System
public class RealtimeChatManager : MonoBehaviour
{
    [Header("Chat Settings")]
    [SerializeField] private int maxChatHistory = 100;
    [SerializeField] private float chatMessageLifetime = 30f;
    [SerializeField] private bool enableProfanityFilter = true;
    
    private WebSocketManager webSocketManager;
    private List<ChatMessage> chatHistory;
    private Dictionary<string, DateTime> lastMessageTimes;
    private HashSet<string> mutedPlayers;
    
    // Events
    public event Action<ChatMessage> OnChatMessageReceived;
    public event Action<string> OnPlayerMuted;
    public event Action<string> OnPlayerUnmuted;
    
    void Start()
    {
        webSocketManager = FindObjectOfType<WebSocketManager>();
        chatHistory = new List<ChatMessage>();
        lastMessageTimes = new Dictionary<string, DateTime>();
        mutedPlayers = new HashSet<string>();
        
        // Register WebSocket message handlers
        webSocketManager.RegisterMessageHandler("chat_message", HandleChatMessage);
        webSocketManager.RegisterMessageHandler("player_muted", HandlePlayerMuted);
        webSocketManager.RegisterMessageHandler("player_unmuted", HandlePlayerUnmuted);
        webSocketManager.RegisterMessageHandler("chat_history", HandleChatHistory);
        
        // Request chat history when connected
        webSocketManager.OnConnected += RequestChatHistory;
    }
    
    public void SendChatMessage(string message, ChatChannel channel = ChatChannel.General)
    {
        // Validate message
        if (string.IsNullOrWhiteSpace(message))
            return;
            
        if (message.Length > 500) // Max message length
        {
            UIManager.Instance.ShowMessage("Message too long. Maximum 500 characters.", MessageType.Warning);
            return;
        }
        
        // Check rate limiting
        var playerId = GameManager.Instance.CurrentPlayerId;
        if (IsRateLimited(playerId))
        {
            UIManager.Instance.ShowMessage("You are sending messages too quickly. Please wait.", MessageType.Warning);
            return;
        }
        
        // Apply profanity filter
        if (enableProfanityFilter)
        {
            message = ApplyProfanityFilter(message);
        }
        
        var chatMessage = new ChatMessageRequest
        {
            Message = message,
            Channel = channel,
            PlayerId = playerId,
            PlayerName = GameManager.Instance.CurrentPlayer.Username,
            Timestamp = DateTime.UtcNow
        };
        
        webSocketManager.SendMessage("send_chat_message", chatMessage);
        
        // Update rate limiting
        lastMessageTimes[playerId] = DateTime.UtcNow;
    }
    
    public void SendPrivateMessage(string targetPlayerId, string message)
    {
        if (string.IsNullOrWhiteSpace(message) || string.IsNullOrWhiteSpace(targetPlayerId))
            return;
            
        var playerId = GameManager.Instance.CurrentPlayerId;
        if (IsRateLimited(playerId))
        {
            UIManager.Instance.ShowMessage("You are sending messages too quickly. Please wait.", MessageType.Warning);
            return;
        }
        
        if (enableProfanityFilter)
        {
            message = ApplyProfanityFilter(message);
        }
        
        var privateMessage = new PrivateMessageRequest
        {
            TargetPlayerId = targetPlayerId,
            Message = message,
            PlayerId = playerId,
            PlayerName = GameManager.Instance.CurrentPlayer.Username,
            Timestamp = DateTime.UtcNow
        };
        
        webSocketManager.SendMessage("send_private_message", privateMessage);
        lastMessageTimes[playerId] = DateTime.UtcNow;
    }
    
    private void HandleChatMessage(WebSocketMessage message)
    {
        var chatMessage = JsonConvert.DeserializeObject<ChatMessage>(message.Data.ToString());
        
        // Check if player is muted
        if (mutedPlayers.Contains(chatMessage.PlayerId))
            return;
            
        // Add to history
        chatHistory.Add(chatMessage);
        
        // Maintain history size limit
        while (chatHistory.Count > maxChatHistory)
        {
            chatHistory.RemoveAt(0);
        }
        
        // Trigger event
        OnChatMessageReceived?.Invoke(chatMessage);
        
        // Display in UI
        DisplayChatMessage(chatMessage);
    }
    
    private void HandlePlayerMuted(WebSocketMessage message)
    {
        var muteData = JsonConvert.DeserializeObject<PlayerMuteData>(message.Data.ToString());
        mutedPlayers.Add(muteData.PlayerId);
        OnPlayerMuted?.Invoke(muteData.PlayerId);
        
        UIManager.Instance.ShowMessage($"Player {muteData.PlayerName} has been muted.", MessageType.Info);
    }
    
    private void HandlePlayerUnmuted(WebSocketMessage message)
    {
        var unmuteData = JsonConvert.DeserializeObject<PlayerUnmuteData>(message.Data.ToString());
        mutedPlayers.Remove(unmuteData.PlayerId);
        OnPlayerUnmuted?.Invoke(unmuteData.PlayerId);
        
        UIManager.Instance.ShowMessage($"Player {unmuteData.PlayerName} has been unmuted.", MessageType.Info);
    }
    
    private void HandleChatHistory(WebSocketMessage message)
    {
        var history = JsonConvert.DeserializeObject<List<ChatMessage>>(message.Data.ToString());
        
        chatHistory.Clear();
        chatHistory.AddRange(history);
        
        // Display historical messages
        foreach (var chatMessage in history)
        {
            DisplayChatMessage(chatMessage, isHistorical: true);
        }
    }
    
    private void RequestChatHistory()
    {
        webSocketManager.SendMessage("request_chat_history", new
        {
            maxMessages = maxChatHistory,
            channels = new[] { ChatChannel.General, ChatChannel.Guild, ChatChannel.System }
        });
    }
    
    private bool IsRateLimited(string playerId)
    {
        if (!lastMessageTimes.ContainsKey(playerId))
            return false;
            
        var timeSinceLastMessage = DateTime.UtcNow - lastMessageTimes[playerId];
        return timeSinceLastMessage.TotalSeconds < 1.0; // 1 second rate limit
    }
    
    private string ApplyProfanityFilter(string message)
    {
        // Simple profanity filter implementation
        var profanityWords = new[] { "badword1", "badword2", "badword3" };
        
        foreach (var word in profanityWords)
        {
            message = message.Replace(word, new string('*', word.Length), StringComparison.OrdinalIgnoreCase);
        }
        
        return message;
    }
    
    private void DisplayChatMessage(ChatMessage chatMessage, bool isHistorical = false)
    {
        var chatUI = FindObjectOfType<ChatUI>();
        if (chatUI != null)
        {
            chatUI.AddMessage(chatMessage, isHistorical);
        }
        
        // Show floating text for nearby players
        if (chatMessage.Channel == ChatChannel.Local)
        {
            ShowFloatingChatText(chatMessage);
        }
    }
    
    private void ShowFloatingChatText(ChatMessage chatMessage)
    {
        var player = GameObject.Find($"RemotePlayer_{chatMessage.PlayerId}");
        if (player != null)
        {
            var floatingText = FindObjectOfType<FloatingTextManager>();
            floatingText?.ShowText(player.transform.position + Vector3.up * 2f, chatMessage.Message, Color.white, 3f);
        }
    }
    
    public void MutePlayer(string playerId)
    {
        mutedPlayers.Add(playerId);
        webSocketManager.SendMessage("mute_player", new { playerId });
    }
    
    public void UnmutePlayer(string playerId)
    {
        mutedPlayers.Remove(playerId);
        webSocketManager.SendMessage("unmute_player", new { playerId });
    }
    
    public List<ChatMessage> GetChatHistory(ChatChannel? channel = null)
    {
        if (channel.HasValue)
        {
            return chatHistory.Where(msg => msg.Channel == channel.Value).ToList();
        }
        
        return new List<ChatMessage>(chatHistory);
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Real-time Architecture Design
```
Prompt: "Design a scalable WebSocket architecture for a Unity battle royale game with 100 players per match, including message routing, state synchronization, anti-cheat integration, and server clustering strategies."
```

### Message Protocol Optimization
```
Prompt: "Create an efficient binary message protocol for Unity WebSocket communication that minimizes bandwidth usage for player position updates, chat messages, and game events while maintaining type safety and extensibility."
```

### Connection Management System
```
Prompt: "Generate a robust WebSocket connection management system for Unity that handles network failures, implements exponential backoff reconnection, manages message queuing during disconnects, and provides seamless failover between servers."
```

## 💡 Key Highlights

### WebSocket Advantages for Gaming
- **Bidirectional communication**: Real-time two-way data flow
- **Low latency**: Minimal protocol overhead compared to HTTP
- **Persistent connection**: Avoid connection establishment overhead
- **Event-driven**: Perfect for real-time game events and updates
- **Firewall friendly**: Uses standard HTTP ports (80/443)

### Unity-Specific Considerations
- **Main thread execution**: Process WebSocket messages on Unity main thread
- **Coroutine integration**: Use coroutines for periodic sync operations
- **Scene transitions**: Handle WebSocket connections across scene changes
- **Mobile optimization**: Manage battery usage and data consumption
- **Error recovery**: Graceful handling of network interruptions

### Real-time Game Features
- **Player synchronization**: Position, rotation, animation states
- **Chat systems**: Text, voice, and emote communication
- **Game events**: Pickups, kills, objective updates
- **Spectator modes**: Live game viewing and replay systems
- **Admin tools**: Real-time moderation and game management