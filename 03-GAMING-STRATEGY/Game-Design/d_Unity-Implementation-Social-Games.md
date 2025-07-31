# d_Unity-Implementation-Social-Games

## 🎯 Learning Objectives
- Master Unity-specific implementation patterns for social deduction games
- Design networked multiplayer systems for social gameplay
- Create responsive UI systems for discussion and voting
- Implement real-time communication and information management
- Build scalable social game architecture in Unity

## 🏗️ Unity Architecture for Social Games

### Core System Architecture
```csharp
// Main Social Deduction Game Manager
public class SocialDeductionGameManager : NetworkBehaviour
{
    [Header("Game Configuration")]
    [SerializeField] private GameConfig gameConfig;
    [SerializeField] private RoleManager roleManager;
    [SerializeField] private PhaseManager phaseManager;
    [SerializeField] private PlayerManager playerManager;
    
    [Header("Communication Systems")]
    [SerializeField] private ChatSystem chatSystem;
    [SerializeField] private VotingSystem votingSystem;
    [SerializeField] private InformationManager infoManager;
    
    [Header("UI Controllers")]
    [SerializeField] private GameUI gameUI;
    [SerializeField] private DiscussionUI discussionUI;
    [SerializeField] private VotingUI votingUI;
    
    private GameState currentState;
    private List<NetworkedPlayer> connectedPlayers;
    
    public override void OnNetworkSpawn()
    {
        if (IsServer)
        {
            InitializeGame();
        }
        SetupClientSystems();
    }
}
```

### Network Architecture Patterns
```csharp
// Authoritative Server Pattern
public class AuthoritativeGameServer : NetworkBehaviour
{
    [Header("Server Authority")]
    private Dictionary<ulong, PlayerRole> authorativeRoles;
    private Dictionary<ulong, HashSet<GameInformation>> playerKnowledge;
    private Queue<GameAction> actionQueue;
    
    [ServerRpc(RequireOwnership = false)]
    public void SubmitActionServerRpc(GameAction action, ulong playerId)
    {
        // Validate action against player's role and game state
        if (ValidateAction(action, playerId))
        {
            ProcessAction(action);
            BroadcastActionResult(action, playerId);
        }
        else
        {
            SendActionRejectionClientRpc(action.actionId, playerId);
        }
    }
    
    [ClientRpc]
    private void UpdateGameStateClientRpc(GameStateSnapshot snapshot)
    {
        // Send only information each client should know
        var filteredSnapshot = FilterInformationForClient(snapshot, GetClientId());
        localGameState.ApplyUpdate(filteredSnapshot);
    }
}
```

## 🎮 Player and Role Management

### Dynamic Role Assignment
```csharp
[CreateAssetMenu(fileName = "New Role Setup", menuName = "Social Deduction/Role Setup")]
public class RoleSetup : ScriptableObject
{
    [Header("Role Distribution")]
    public List<RoleAllocation> roleAllocations;
    public int minPlayers = 4;
    public int maxPlayers = 12;
    
    [System.Serializable]
    public class RoleAllocation
    {
        public Role role;
        public int count;
        public bool scaleWithPlayerCount;
        public AnimationCurve scalingCurve;
    }
    
    public Dictionary<Role, int> CalculateRoleDistribution(int playerCount)
    {
        var distribution = new Dictionary<Role, int>();
        
        foreach (var allocation in roleAllocations)
        {
            int count = allocation.count;
            if (allocation.scaleWithPlayerCount)
            {
                float scaleFactor = allocation.scalingCurve.Evaluate(playerCount / (float)maxPlayers);
                count = Mathf.RoundToInt(allocation.count * scaleFactor);
            }
            distribution[allocation.role] = count;
        }
        
        return distribution;
    }
}

// Role Manager Implementation
public class RoleManager : NetworkBehaviour
{
    [Header("Role Configuration")]
    [SerializeField] private RoleSetup currentSetup;
    [SerializeField] private List<Role> availableRoles;
    
    private Dictionary<ulong, Role> playerRoles;
    private Dictionary<Role, List<ulong>> roleGroups;
    
    [ServerRpc]
    public void AssignRolesServerRpc()
    {
        var playerIds = NetworkManager.Singleton.ConnectedClientsIds.ToList();
        var roleDistribution = currentSetup.CalculateRoleDistribution(playerIds.Count);
        
        var assignedRoles = ShuffleAndAssignRoles(playerIds, roleDistribution);
        
        foreach (var assignment in assignedRoles)
        {
            SendRoleAssignmentClientRpc(assignment.Key, assignment.Value);
        }
    }
    
    [ClientRpc]
    private void SendRoleAssignmentClientRpc(ulong playerId, Role assignedRole)
    {
        if (playerId == NetworkManager.Singleton.LocalClientId)
        {
            LocalPlayer.Instance.SetRole(assignedRole);
            GameUI.Instance.DisplayRoleInformation(assignedRole);
        }
    }
}
```

### Player Information Management
```csharp
// Information Filtering System
public class InformationManager : NetworkBehaviour
{
    [Header("Information Categories")]
    private Dictionary<InformationType, HashSet<ulong>> informationAccess;
    private Dictionary<ulong, PlayerInformationState> playerStates;
    
    public enum InformationType
    {
        PublicActions,
        RoleSpecificInfo,
        TeamMemberIdentities,
        InvestigationResults,
        ChatMessages,
        VotingResults
    }
    
    public bool CanPlayerAccessInformation(ulong playerId, InformationType infoType, object infoData)
    {
        var playerRole = RoleManager.Instance.GetPlayerRole(playerId);
        var playerState = playerStates[playerId];
        
        return infoType switch
        {
            InformationType.PublicActions => true,
            InformationType.RoleSpecificInfo => playerRole.HasAccess(infoData),
            InformationType.TeamMemberIdentities => playerRole.KnowsTeamMembers,
            InformationType.InvestigationResults => IsInvestigationTarget(playerId, infoData) || IsInvestigator(playerId, infoData),
            InformationType.ChatMessages => CanAccessChatChannel(playerId, infoData),
            InformationType.VotingResults => true,
            _ => false
        };
    }
    
    [ServerRpc(RequireOwnership = false)]
    public void RequestInformationServerRpc(ulong requestingPlayer, InformationType infoType, string infoId)
    {
        if (CanPlayerAccessInformation(requestingPlayer, infoType, infoId))
        {
            var information = GetInformation(infoType, infoId);
            SendInformationClientRpc(requestingPlayer, information);
        }
    }
}
```

## 💬 Communication Systems

### Multi-Channel Chat Implementation
```csharp
public class ChatSystem : NetworkBehaviour
{
    [Header("Chat Configuration")]
    [SerializeField] private float messageDisplayTime = 30f;
    [SerializeField] private int maxMessagesPerChannel = 100;
    [SerializeField] private ChatUI chatUI;
    
    private Dictionary<ChatChannel, List<ChatMessage>> channelMessages;
    private Dictionary<ulong, HashSet<ChatChannel>> playerChannelAccess;
    
    public enum ChatChannel
    {
        Public,
        Mafia,
        Dead,
        Private,
        System
    }
    
    [System.Serializable]
    public class ChatMessage
    {
        public ulong senderId;
        public string senderName;
        public string content;
        public ChatChannel channel;
        public float timestamp;
        public Color messageColor;
    }
    
    [ServerRpc(RequireOwnership = false)]
    public void SendMessageServerRpc(string message, ChatChannel channel, ulong senderId)
    {
        // Validate sender can access channel
        if (!CanAccessChannel(senderId, channel))
        {
            SendErrorMessageClientRpc(senderId, "You don't have access to that channel");
            return;
        }
        
        // Create and broadcast message
        var chatMessage = new ChatMessage
        {
            senderId = senderId,
            senderName = GetPlayerName(senderId),
            content = SanitizeMessage(message),
            channel = channel,
            timestamp = Time.time,
            messageColor = GetChannelColor(channel)
        };
        
        BroadcastMessageToChannel(chatMessage);
    }
    
    private void BroadcastMessageToChannel(ChatMessage message)
    {
        var eligiblePlayers = GetPlayersWithChannelAccess(message.channel);
        
        foreach (var playerId in eligiblePlayers)
        {
            ReceiveMessageClientRpc(message, playerId);
        }
    }
    
    [ClientRpc]
    private void ReceiveMessageClientRpc(ChatMessage message, ulong targetPlayerId)
    {
        if (targetPlayerId == NetworkManager.Singleton.LocalClientId)
        {
            chatUI.DisplayMessage(message);
            AudioManager.Instance.PlayChatSound(message.channel);
        }
    }
}
```

### Real-Time Discussion Tools
```csharp
// Discussion Phase Manager
public class DiscussionManager : NetworkBehaviour
{
    [Header("Discussion Settings")]
    [SerializeField] private float discussionTimeLimit = 300f; // 5 minutes
    [SerializeField] private bool allowSpeakingTimers = true;
    [SerializeField] private float maxSpeakingTime = 60f;
    
    [Header("UI References")]
    [SerializeField] private DiscussionUI discussionUI;
    [SerializeField] private SpeakingOrderUI speakingOrderUI;
    
    private Dictionary<ulong, float> playerSpeakingTime;
    private Queue<ulong> speakingQueue;
    private ulong currentSpeaker;
    private float discussionStartTime;
    
    [ServerRpc(RequireOwnership = false)]
    public void RequestSpeakingTimeServerRpc(ulong playerId)
    {
        if (!speakingQueue.Contains(playerId) && playerId != currentSpeaker)
        {
            speakingQueue.Enqueue(playerId);
            UpdateSpeakingQueueClientRpc();
        }
    }
    
    [ClientRpc]
    private void UpdateSpeakingQueueClientRpc()
    {
        speakingOrderUI.UpdateQueue(speakingQueue.ToArray(), currentSpeaker);
    }
    
    private void Update()
    {
        if (!IsServer) return;
        
        UpdateDiscussionTimer();
        ManageSpeakingRotation();
    }
    
    private void ManageSpeakingRotation()
    {
        if (currentSpeaker == 0 && speakingQueue.Count > 0)
        {
            currentSpeaker = speakingQueue.Dequeue();
            StartSpeakingTurnClientRpc(currentSpeaker);
        }
        
        if (allowSpeakingTimers && currentSpeaker != 0)
        {
            playerSpeakingTime[currentSpeaker] += Time.deltaTime;
            if (playerSpeakingTime[currentSpeaker] >= maxSpeakingTime)
            {
                EndSpeakingTurnServerRpc();
            }
        }
    }
}
```

## 🗳️ Voting System Implementation

### Flexible Voting Mechanics
```csharp
public class VotingSystem : NetworkBehaviour
{
    [Header("Voting Configuration")]
    [SerializeField] private float votingTimeLimit = 120f;
    [SerializeField] private bool allowVoteChanges = true;
    [SerializeField] private bool requireMajority = true;
    [SerializeField] private VotingUI votingUI;
    
    [System.Serializable]
    public class VotingSession
    {
        public string sessionId;
        public VotingType type;
        public List<VotingOption> options;
        public Dictionary<ulong, ulong> playerVotes; // voter -> target
        public float startTime;
        public bool isActive;
        public HashSet<ulong> eligibleVoters;
    }
    
    public enum VotingType
    {
        Elimination,
        Mission,
        Policy,
        Emergency
    }
    
    private VotingSession currentVotingSession;
    private Dictionary<ulong, ulong> submittedVotes;
    
    [ServerRpc(RequireOwnership = false)]
    public void StartVotingSessionServerRpc(VotingType type, List<ulong> eligibleTargets)
    {
        currentVotingSession = new VotingSession
        {
            sessionId = System.Guid.NewGuid().ToString(),
            type = type,
            options = CreateVotingOptions(eligibleTargets),
            playerVotes = new Dictionary<ulong, ulong>(),
            startTime = Time.time,
            isActive = true,
            eligibleVoters = GetEligibleVoters()
        };
        
        StartVotingClientRpc(currentVotingSession);
    }
    
    [ClientRpc]
    private void StartVotingClientRpc(VotingSession session)
    {
        votingUI.InitializeVoting(session);
        AudioManager.Instance.PlayVotingStartSound();
        
        if (session.eligibleVoters.Contains(NetworkManager.Singleton.LocalClientId))
        {
            votingUI.EnableVoting(true);
        }
    }
    
    [ServerRpc(RequireOwnership = false)]
    public void SubmitVoteServerRpc(ulong voterId, ulong targetId, string sessionId)
    {
        if (currentVotingSession?.sessionId != sessionId || !currentVotingSession.isActive)
        {
            SendVoteRejectionClientRpc(voterId, "Voting session not active");
            return;
        }
        
        if (!currentVotingSession.eligibleVoters.Contains(voterId))
        {
            SendVoteRejectionClientRpc(voterId, "You are not eligible to vote");
            return;
        }
        
        // Record or update vote
        currentVotingSession.playerVotes[voterId] = targetId;
        
        // Broadcast vote update (without revealing who voted for whom)
        UpdateVoteCountsClientRpc(CalculateVoteCounts());
        
        // Check if voting should end
        if (ShouldEndVoting())
        {
            EndVotingSession();
        }
    }
    
    private void EndVotingSession()
    {
        currentVotingSession.isActive = false;
        var results = CalculateVotingResults();
        
        ProcessVotingResultsClientRpc(results);
        
        // Apply voting results to game state
        ApplyVotingResults(results);
    }
}
```

### Anonymous and Transparent Voting Options
```csharp
// Voting Privacy Manager
public class VotingPrivacyManager : MonoBehaviour
{
    [Header("Privacy Settings")]
    [SerializeField] private bool showVoteProgress = true;
    [SerializeField] private bool showVoterIdentities = false;
    [SerializeField] private bool allowVoteTracking = true;
    
    public class VoteDisplayInfo
    {
        public Dictionary<ulong, int> voteCounts; // target -> count
        public Dictionary<ulong, List<ulong>> votersByTarget; // target -> list of voters (if transparent)
        public HashSet<ulong> playersWhoVoted;
        public int totalVotesNeeded;
    }
    
    public VoteDisplayInfo GetDisplayInfo(VotingSession session, bool isTransparentVoting)
    {
        var displayInfo = new VoteDisplayInfo
        {
            voteCounts = new Dictionary<ulong, int>(),
            playersWhoVoted = new HashSet<ulong>(session.playerVotes.Keys),
            totalVotesNeeded = CalculateVotesNeeded(session)
        };
        
        // Count votes by target
        foreach (var vote in session.playerVotes)
        {
            ulong target = vote.Value;
            displayInfo.voteCounts[target] = displayInfo.voteCounts.GetValueOrDefault(target, 0) + 1;
        }
        
        // Include voter identities if transparent voting
        if (isTransparentVoting && showVoterIdentities)
        {
            displayInfo.votersByTarget = new Dictionary<ulong, List<ulong>>();
            foreach (var vote in session.playerVotes)
            {
                ulong voter = vote.Key;
                ulong target = vote.Value;
                
                if (!displayInfo.votersByTarget.ContainsKey(target))
                {
                    displayInfo.votersByTarget[target] = new List<ulong>();
                }
                displayInfo.votersByTarget[target].Add(voter);
            }
        }
        
        return displayInfo;
    }
}
```

## 🎨 UI/UX Design for Social Games

### Responsive Social UI
```csharp
// Adaptive UI Controller
public class SocialGameUI : MonoBehaviour
{
    [Header("UI Panels")]
    [SerializeField] private PlayerListPanel playerListPanel;
    [SerializeField] private ChatPanel chatPanel;
    [SerializeField] private VotingPanel votingPanel;
    [SerializeField] private InformationPanel informationPanel;
    [SerializeField] private GamePhasePanel phasePanel;
    
    [Header("Layout Configuration")]
    [SerializeField] private bool adaptToPlayerCount = true;
    [SerializeField] private List<UILayoutConfig> layoutConfigs;
    [SerializeField] private float animationDuration = 0.3f;
    
    [System.Serializable]
    public class UILayoutConfig
    {
        public int minPlayers;
        public int maxPlayers;
        public Vector2 playerListSize;
        public Vector2 chatPanelSize;
        public bool showExtendedInfo;
    }
    
    private void Start()
    {
        SetupUILayout();
        RegisterForGameEvents();
    }
    
    public void AdaptUIToPlayerCount(int playerCount)
    {
        var config = GetLayoutConfig(playerCount);
        
        // Animate UI transitions
        LeanTween.size(playerListPanel.rectTransform, config.playerListSize, animationDuration);
        LeanTween.size(chatPanel.rectTransform, config.chatPanelSize, animationDuration);
        
        // Toggle extended information display
        informationPanel.SetExtendedMode(config.showExtendedInfo);
    }
    
    private void RegisterForGameEvents()
    {
        GameEvents.OnPhaseChanged += HandlePhaseChange;
        GameEvents.OnPlayerEliminated += HandlePlayerElimination;
        GameEvents.OnVotingStarted += ShowVotingUI;
        GameEvents.OnDiscussionStarted += ShowDiscussionUI;
    }
    
    private void HandlePhaseChange(GamePhase newPhase)
    {
        phasePanel.TransitionToPhase(newPhase);
        
        // Show/hide relevant UI panels
        switch (newPhase)
        {
            case GamePhase.Discussion:
                chatPanel.SetActive(true);
                votingPanel.SetActive(false);
                break;
            case GamePhase.Voting:
                chatPanel.SetActive(false);
                votingPanel.SetActive(true);
                break;
            case GamePhase.Night:
                DisableInteractionUI();
                break;
        }
    }
}
```

### Information Visualization
```csharp
// Player Information Display
public class PlayerInfoDisplay : MonoBehaviour
{
    [Header("Display Components")]
    [SerializeField] private Image playerAvatar;
    [SerializeField] private TextMeshProUGUI playerName;
    [SerializeField] private Image statusIndicator;
    [SerializeField] private Slider suspicionMeter;
    [SerializeField] private Transform roleIndicator;
    
    [Header("Visual States")]
    [SerializeField] private Color aliveColor = Color.white;
    [SerializeField] private Color deadColor = Color.gray;
    [SerializeField] private Color suspiciousColor = Color.red;
    [SerializeField] private Color trustedColor = Color.green;
    
    private PlayerData playerData;
    private float currentSuspicion;
    
    public void UpdatePlayerInfo(PlayerData data)
    {
        playerData = data;
        
        // Update basic info
        playerName.text = data.displayName;
        playerAvatar.sprite = data.avatarSprite;
        
        // Update status
        UpdateAliveStatus(data.isAlive);
        UpdateSuspicionLevel(data.suspicionLevel);
        UpdateRoleDisplay(data.knownRole);
    }
    
    private void UpdateSuspicionLevel(float suspicion)
    {
        currentSuspicion = suspicion;
        
        // Animate suspicion meter
        LeanTween.value(suspicionMeter.value, suspicion, 0.5f)
            .setOnUpdate(value => suspicionMeter.value = value);
        
        // Update color based on suspicion
        Color targetColor = Color.Lerp(trustedColor, suspiciousColor, suspicion);
        LeanTween.color(statusIndicator.rectTransform, targetColor, 0.3f);
    }
    
    private void UpdateRoleDisplay(Role knownRole)
    {
        if (knownRole != null)
        {
            roleIndicator.gameObject.SetActive(true);
            var roleDisplay = roleIndicator.GetComponent<RoleDisplay>();
            roleDisplay.SetRole(knownRole);
        }
        else
        {
            roleIndicator.gameObject.SetActive(false);
        }
    }
}
```

## 🚀 AI/LLM Integration in Unity

### AI-Powered Game Analysis
```csharp
// Game Analysis System
public class GameAnalysisSystem : MonoBehaviour
{
    [Header("Analysis Configuration")]
    [SerializeField] private bool enableRealTimeAnalysis = true;
    [SerializeField] private float analysisInterval = 10f;
    [SerializeField] private AnalysisUI analysisUI;
    
    private List<GameEvent> gameEventLog;
    private Dictionary<ulong, PlayerBehaviorProfile> playerProfiles;
    
    [System.Serializable]
    public class GameAnalysis
    {
        public Dictionary<ulong, float> suspicionLevels;
        public List<DeductionSuggestion> suggestions;
        public PredictedOutcome mostLikelyOutcome;
        public float confidenceLevel;
    }
    
    private async void PerformGameAnalysis()
    {
        var gameState = CollectCurrentGameState();
        var analysis = await RequestAIAnalysis(gameState);
        
        if (enableRealTimeAnalysis)
        {
            DisplayAnalysisResults(analysis);
        }
        
        UpdatePlayerProfiles(analysis);
    }
    
    private async Task<GameAnalysis> RequestAIAnalysis(GameStateSnapshot gameState)
    {
        // Prepare analysis request for AI service
        var analysisRequest = new AnalysisRequest
        {
            gameState = gameState,
            playerActions = gameEventLog.TakeLast(50).ToList(),
            playerProfiles = playerProfiles
        };
        
        // Call AI service (implement based on your AI provider)
        var response = await AIService.AnalyzeGameState(analysisRequest);
        return ParseAnalysisResponse(response);
    }
}
```

### Prompt Engineering Integration
```csharp
// AI Prompt Manager
public class AIPromptManager : MonoBehaviour
{
    [Header("Prompt Templates")]
    [TextArea(5, 10)]
    public string gameAnalysisPrompt = @"
        Analyze this social deduction game state:
        Players: {playerList}
        Current Phase: {gamePhase}
        Recent Actions: {recentActions}
        
        Provide:
        1. Suspicion levels for each player (0-1 scale)
        2. Most likely player roles based on behavior
        3. Suggested investigation targets
        4. Predicted winner based on current state
    ";
    
    [TextArea(5, 10)]
    public string playerCoachingPrompt = @"
        Help this player improve their social deduction skills:
        Player Role: {playerRole}
        Recent Actions: {playerActions}
        Game Outcome: {gameResult}
        
        Provide constructive feedback on:
        1. Decision-making effectiveness
        2. Social interaction quality
        3. Deduction accuracy
        4. Specific improvement suggestions
    ";
    
    public string FormatPrompt(string template, Dictionary<string, object> parameters)
    {
        string formattedPrompt = template;
        
        foreach (var param in parameters)
        {
            string placeholder = $"{{{param.Key}}}";
            formattedPrompt = formattedPrompt.Replace(placeholder, param.Value.ToString());
        }
        
        return formattedPrompt;
    }
}
```

## 💡 Key Unity Implementation Insights

### Performance Optimization
- **Network Message Batching**: Combine multiple small updates into single network calls
- **UI Pooling**: Reuse chat message and player info UI elements
- **LOD for Social Features**: Reduce update frequency for non-critical social information
- **Async Operations**: Handle AI analysis and database operations asynchronously

### Scalability Considerations
- **Room-Based Architecture**: Separate game instances for different player groups
- **Modular Role System**: Easy addition of new roles without core system changes
- **Configurable Game Rules**: Data-driven game configuration for different variants
- **Cross-Platform Compatibility**: Ensure social features work across PC, mobile, and console

### Security and Anti-Cheat
- **Server Authority**: All critical game state managed server-side
- **Information Validation**: Verify players can only access information they should know
- **Action Validation**: Confirm all player actions are legal for their role and game state
- **Communication Monitoring**: Detect and prevent cheating through external communication

This comprehensive Unity implementation guide provides the technical foundation needed to create robust, scalable social deduction games that can handle the complex requirements of multiplayer social gameplay while maintaining security and performance.