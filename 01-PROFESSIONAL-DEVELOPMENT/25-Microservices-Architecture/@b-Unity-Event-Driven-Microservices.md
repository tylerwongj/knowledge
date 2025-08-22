# @b-Unity-Event-Driven-Microservices - Scalable Game Backend Architecture

## 🎯 Learning Objectives
- Master event-driven microservices architecture for Unity game backends
- Implement asynchronous messaging patterns for game systems communication
- Create resilient, scalable service architectures for multiplayer games
- Design event sourcing and CQRS patterns for game state management

## 🔧 Core Event-Driven Microservices Framework

### Unity Event-Driven Service Architecture
```csharp
using UnityEngine;
using System.Collections.Generic;
using System.Threading.Tasks;
using Newtonsoft.Json;
using System;

namespace UnityMicroservices
{
    [System.Serializable]
    public class GameEvent
    {
        public string eventId;
        public string eventType;
        public string aggregateId;
        public long timestamp;
        public int version;
        public Dictionary<string, object> payload;
        public Dictionary<string, string> metadata;
        public string correlationId;
        public string causationId;
    }
    
    public interface IEventBus
    {
        Task PublishAsync<T>(T gameEvent) where T : GameEvent;
        void Subscribe<T>(Func<T, Task> handler) where T : GameEvent;
        void Subscribe(string eventType, Func<GameEvent, Task> handler);
        Task<List<GameEvent>> GetEventsAsync(string aggregateId, int fromVersion = 0);
    }
    
    public class UnityEventBus : MonoBehaviour, IEventBus
    {
        [System.Serializable]
        public class EventBusConfiguration
        {
            public string messageQueueUrl = "amqp://localhost:5672";
            public string eventStoreUrl = "mongodb://localhost:27017/gameevents";
            public bool enableEventSourcing = true;
            public bool enableEventReplay = true;
            public int maxRetryAttempts = 3;
            public float retryDelaySeconds = 1f;
        }
        
        [SerializeField] private EventBusConfiguration config;
        private Dictionary<string, List<Func<GameEvent, Task>>> eventHandlers;
        private Dictionary<Type, List<Func<GameEvent, Task>>> typedHandlers;
        private IEventStore eventStore;
        private IMessageQueue messageQueue;
        
        private void Start()
        {
            InitializeEventBus();
        }
        
        private void InitializeEventBus()
        {
            eventHandlers = new Dictionary<string, List<Func<GameEvent, Task>>>();
            typedHandlers = new Dictionary<Type, List<Func<GameEvent, Task>>>();
            
            eventStore = new MongoEventStore(config.eventStoreUrl);
            messageQueue = new RabbitMQMessageQueue(config.messageQueueUrl);
            
            Debug.Log("Unity Event Bus initialized with event sourcing enabled");
        }
        
        public async Task PublishAsync<T>(T gameEvent) where T : GameEvent
        {
            try
            {
                // Enrich event with metadata
                gameEvent.eventId = Guid.NewGuid().ToString();
                gameEvent.timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
                
                if (string.IsNullOrEmpty(gameEvent.correlationId))
                {
                    gameEvent.correlationId = gameEvent.eventId;
                }
                
                // Store event if event sourcing is enabled
                if (config.enableEventSourcing)
                {
                    await eventStore.SaveEventAsync(gameEvent);
                }
                
                // Publish to message queue
                await messageQueue.PublishAsync(gameEvent.eventType, gameEvent);
                
                // Handle locally subscribed handlers
                await HandleEventLocally(gameEvent);
                
                Debug.Log($"Published event: {gameEvent.eventType} for aggregate {gameEvent.aggregateId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to publish event {gameEvent.eventType}: {ex.Message}");
                throw;
            }
        }
        
        public void Subscribe<T>(Func<T, Task> handler) where T : GameEvent
        {
            Type eventType = typeof(T);
            
            if (!typedHandlers.ContainsKey(eventType))
            {
                typedHandlers[eventType] = new List<Func<GameEvent, Task>>();
            }
            
            typedHandlers[eventType].Add(async (gameEvent) =>
            {
                if (gameEvent is T typedEvent)
                {
                    await handler(typedEvent);
                }
            });
        }
        
        public void Subscribe(string eventType, Func<GameEvent, Task> handler)
        {
            if (!eventHandlers.ContainsKey(eventType))
            {
                eventHandlers[eventType] = new List<Func<GameEvent, Task>>();
            }
            
            eventHandlers[eventType].Add(handler);
        }
        
        private async Task HandleEventLocally(GameEvent gameEvent)
        {
            // Handle typed subscriptions
            Type eventType = gameEvent.GetType();
            if (typedHandlers.ContainsKey(eventType))
            {
                var tasks = typedHandlers[eventType].Select(handler => handler(gameEvent));
                await Task.WhenAll(tasks);
            }
            
            // Handle string-based subscriptions
            if (eventHandlers.ContainsKey(gameEvent.eventType))
            {
                var tasks = eventHandlers[gameEvent.eventType].Select(handler => handler(gameEvent));
                await Task.WhenAll(tasks);
            }
        }
        
        public async Task<List<GameEvent>> GetEventsAsync(string aggregateId, int fromVersion = 0)
        {
            if (config.enableEventSourcing)
            {
                return await eventStore.GetEventsAsync(aggregateId, fromVersion);
            }
            
            return new List<GameEvent>();
        }
    }
}
```

### Player Service Microservice
```csharp
namespace UnityMicroservices.Services
{
    public class PlayerService : MonoBehaviour
    {
        [System.Serializable]
        public class PlayerCreatedEvent : GameEvent
        {
            public string playerId;
            public string playerName;
            public string email;
            public DateTime createdAt;
            public Dictionary<string, object> initialStats;
        }
        
        [System.Serializable]
        public class PlayerStatsUpdatedEvent : GameEvent
        {
            public string playerId;
            public Dictionary<string, object> statChanges;
            public Dictionary<string, object> newStats;
            public string reason;
        }
        
        [System.Serializable]
        public class PlayerLevelUpEvent : GameEvent
        {
            public string playerId;
            public int oldLevel;
            public int newLevel;
            public Dictionary<string, object> rewards;
        }
        
        private IEventBus eventBus;
        private Dictionary<string, PlayerAggregate> players;
        
        private void Start()
        {
            eventBus = FindObjectOfType<UnityEventBus>();
            players = new Dictionary<string, PlayerAggregate>();
            
            SubscribeToEvents();
        }
        
        private void SubscribeToEvents()
        {
            eventBus.Subscribe<PlayerCreatedEvent>(HandlePlayerCreated);
            eventBus.Subscribe<PlayerStatsUpdatedEvent>(HandlePlayerStatsUpdated);
            eventBus.Subscribe("game_completed", HandleGameCompleted);
            eventBus.Subscribe("achievement_unlocked", HandleAchievementUnlocked);
        }
        
        public async Task CreatePlayerAsync(string playerId, string playerName, string email)
        {
            var playerCreatedEvent = new PlayerCreatedEvent\n            {\n                eventType = \"player_created\",\n                aggregateId = playerId,\n                playerId = playerId,\n                playerName = playerName,\n                email = email,\n                createdAt = DateTime.UtcNow,\n                initialStats = GetDefaultPlayerStats(),\n                version = 1\n            };\n            \n            await eventBus.PublishAsync(playerCreatedEvent);\n        }\n        \n        public async Task UpdatePlayerStatsAsync(string playerId, Dictionary<string, object> statChanges, string reason = \"manual_update\")\n        {\n            if (!players.ContainsKey(playerId))\n            {\n                await LoadPlayerAsync(playerId);\n            }\n            \n            var player = players[playerId];\n            var oldStats = new Dictionary<string, object>(player.Stats);\n            \n            // Apply stat changes\n            foreach (var change in statChanges)\n            {\n                if (player.Stats.ContainsKey(change.Key))\n                {\n                    // Handle different stat types (addition, setting, etc.)\n                    player.Stats[change.Key] = ApplyStatChange(player.Stats[change.Key], change.Value);\n                }\n                else\n                {\n                    player.Stats[change.Key] = change.Value;\n                }\n            }\n            \n            var statsUpdatedEvent = new PlayerStatsUpdatedEvent\n            {\n                eventType = \"player_stats_updated\",\n                aggregateId = playerId,\n                playerId = playerId,\n                statChanges = statChanges,\n                newStats = new Dictionary<string, object>(player.Stats),\n                reason = reason,\n                version = player.Version + 1\n            };\n            \n            await eventBus.PublishAsync(statsUpdatedEvent);\n            \n            // Check for level up\n            await CheckForLevelUp(playerId, oldStats, player.Stats);\n        }\n        \n        private async Task CheckForLevelUp(string playerId, Dictionary<string, object> oldStats, Dictionary<string, object> newStats)\n        {\n            int oldLevel = Convert.ToInt32(oldStats.GetValueOrDefault(\"level\", 1));\n            int newLevel = CalculateLevel(newStats);\n            \n            if (newLevel > oldLevel)\n            {\n                var rewards = CalculateLevelUpRewards(oldLevel, newLevel);\n                \n                var levelUpEvent = new PlayerLevelUpEvent\n                {\n                    eventType = \"player_level_up\",\n                    aggregateId = playerId,\n                    playerId = playerId,\n                    oldLevel = oldLevel,\n                    newLevel = newLevel,\n                    rewards = rewards,\n                    version = players[playerId].Version + 1\n                };\n                \n                await eventBus.PublishAsync(levelUpEvent);\n            }\n        }\n        \n        private async Task HandlePlayerCreated(PlayerCreatedEvent playerCreatedEvent)\n        {\n            var player = new PlayerAggregate\n            {\n                PlayerId = playerCreatedEvent.playerId,\n                PlayerName = playerCreatedEvent.playerName,\n                Email = playerCreatedEvent.email,\n                CreatedAt = playerCreatedEvent.createdAt,\n                Stats = playerCreatedEvent.initialStats,\n                Version = playerCreatedEvent.version\n            };\n            \n            players[playerCreatedEvent.playerId] = player;\n            \n            Debug.Log($\"Player created: {playerCreatedEvent.playerName} ({playerCreatedEvent.playerId})\");\n            \n            // Trigger welcome sequence\n            await TriggerWelcomeSequence(playerCreatedEvent.playerId);\n        }\n        \n        private async Task HandlePlayerStatsUpdated(PlayerStatsUpdatedEvent statsUpdatedEvent)\n        {\n            if (players.ContainsKey(statsUpdatedEvent.playerId))\n            {\n                var player = players[statsUpdatedEvent.playerId];\n                player.Stats = statsUpdatedEvent.newStats;\n                player.Version = statsUpdatedEvent.version;\n                \n                Debug.Log($\"Player stats updated: {statsUpdatedEvent.playerId}\");\n            }\n        }\n        \n        private async Task HandleGameCompleted(GameEvent gameCompletedEvent)\n        {\n            string playerId = gameCompletedEvent.payload[\"playerId\"].ToString();\n            float score = Convert.ToSingle(gameCompletedEvent.payload[\"score\"]);\n            string gameMode = gameCompletedEvent.payload[\"gameMode\"].ToString();\n            \n            // Calculate experience and rewards based on performance\n            var statChanges = CalculateGameCompletionRewards(score, gameMode);\n            \n            await UpdatePlayerStatsAsync(playerId, statChanges, \"game_completed\");\n        }\n        \n        private async Task HandleAchievementUnlocked(GameEvent achievementEvent)\n        {\n            string playerId = achievementEvent.payload[\"playerId\"].ToString();\n            string achievementId = achievementEvent.payload[\"achievementId\"].ToString();\n            \n            // Grant achievement rewards\n            var rewards = GetAchievementRewards(achievementId);\n            \n            if (rewards.Count > 0)\n            {\n                await UpdatePlayerStatsAsync(playerId, rewards, $\"achievement_{achievementId}\");\n            }\n        }\n    }\n    \n    public class PlayerAggregate\n    {\n        public string PlayerId { get; set; }\n        public string PlayerName { get; set; }\n        public string Email { get; set; }\n        public DateTime CreatedAt { get; set; }\n        public Dictionary<string, object> Stats { get; set; }\n        public int Version { get; set; }\n        \n        public PlayerAggregate()\n        {\n            Stats = new Dictionary<string, object>();\n        }\n    }\n}
```

### Game Session Microservice
```csharp
namespace UnityMicroservices.Services
{
    public class GameSessionService : MonoBehaviour
    {
        [System.Serializable]
        public class GameSessionStartedEvent : GameEvent
        {
            public string sessionId;
            public List<string> playerIds;
            public string gameMode;
            public Dictionary<string, object> gameSettings;
            public DateTime startTime;
        }
        
        [System.Serializable]
        public class GameSessionEndedEvent : GameEvent
        {
            public string sessionId;
            public DateTime endTime;
            public TimeSpan duration;
            public Dictionary<string, object> finalScores;
            public string endReason;
        }
        
        [System.Serializable]
        public class PlayerJoinedSessionEvent : GameEvent
        {
            public string sessionId;
            public string playerId;
            public DateTime joinTime;\n        }\n        \n        [System.Serializable]\n        public class PlayerLeftSessionEvent : GameEvent\n        {\n            public string sessionId;\n            public string playerId;\n            public DateTime leaveTime;\n            public string leaveReason;\n        }\n        \n        private IEventBus eventBus;\n        private Dictionary<string, GameSessionAggregate> activeSessions;\n        \n        private void Start()\n        {\n            eventBus = FindObjectOfType<UnityEventBus>();\n            activeSessions = new Dictionary<string, GameSessionAggregate>();\n            \n            SubscribeToEvents();\n        }\n        \n        private void SubscribeToEvents()\n        {\n            eventBus.Subscribe<GameSessionStartedEvent>(HandleGameSessionStarted);\n            eventBus.Subscribe<GameSessionEndedEvent>(HandleGameSessionEnded);\n            eventBus.Subscribe<PlayerJoinedSessionEvent>(HandlePlayerJoinedSession);\n            eventBus.Subscribe<PlayerLeftSessionEvent>(HandlePlayerLeftSession);\n            \n            // Cross-service event subscriptions\n            eventBus.Subscribe(\"matchmaking_completed\", HandleMatchmakingCompleted);\n            eventBus.Subscribe(\"player_disconnected\", HandlePlayerDisconnected);\n        }\n        \n        public async Task StartGameSessionAsync(List<string> playerIds, string gameMode, Dictionary<string, object> settings)\n        {\n            string sessionId = Guid.NewGuid().ToString();\n            \n            var sessionStartedEvent = new GameSessionStartedEvent\n            {\n                eventType = \"game_session_started\",\n                aggregateId = sessionId,\n                sessionId = sessionId,\n                playerIds = playerIds,\n                gameMode = gameMode,\n                gameSettings = settings,\n                startTime = DateTime.UtcNow,\n                version = 1\n            };\n            \n            await eventBus.PublishAsync(sessionStartedEvent);\n        }\n        \n        public async Task EndGameSessionAsync(string sessionId, Dictionary<string, object> finalScores, string endReason = \"completed\")\n        {\n            if (!activeSessions.ContainsKey(sessionId))\n            {\n                Debug.LogWarning($\"Attempted to end non-existent session: {sessionId}\");\n                return;\n            }\n            \n            var session = activeSessions[sessionId];\n            var duration = DateTime.UtcNow - session.StartTime;\n            \n            var sessionEndedEvent = new GameSessionEndedEvent\n            {\n                eventType = \"game_session_ended\",\n                aggregateId = sessionId,\n                sessionId = sessionId,\n                endTime = DateTime.UtcNow,\n                duration = duration,\n                finalScores = finalScores,\n                endReason = endReason,\n                version = session.Version + 1\n            };\n            \n            await eventBus.PublishAsync(sessionEndedEvent);\n        }\n        \n        private async Task HandleMatchmakingCompleted(GameEvent matchmakingEvent)\n        {\n            var playerIds = ((List<object>)matchmakingEvent.payload[\"playerIds\"]).Select(p => p.ToString()).ToList();\n            string gameMode = matchmakingEvent.payload[\"gameMode\"].ToString();\n            var settings = (Dictionary<string, object>)matchmakingEvent.payload[\"gameSettings\"];\n            \n            await StartGameSessionAsync(playerIds, gameMode, settings);\n        }\n        \n        private async Task HandleGameSessionStarted(GameSessionStartedEvent sessionStartedEvent)\n        {\n            var session = new GameSessionAggregate\n            {\n                SessionId = sessionStartedEvent.sessionId,\n                PlayerIds = sessionStartedEvent.playerIds,\n                GameMode = sessionStartedEvent.gameMode,\n                Settings = sessionStartedEvent.gameSettings,\n                StartTime = sessionStartedEvent.startTime,\n                Version = sessionStartedEvent.version,\n                Status = \"active\"\n            };\n            \n            activeSessions[sessionStartedEvent.sessionId] = session;\n            \n            Debug.Log($\"Game session started: {sessionStartedEvent.sessionId} with {sessionStartedEvent.playerIds.Count} players\");\n            \n            // Initialize game world for session\n            await InitializeGameWorld(session);\n        }\n        \n        private async Task InitializeGameWorld(GameSessionAggregate session)\n        {\n            var gameWorldInitEvent = new GameEvent\n            {\n                eventType = \"game_world_initialize\",\n                aggregateId = session.SessionId,\n                payload = new Dictionary<string, object>\n                {\n                    {\"sessionId\", session.SessionId},\n                    {\"gameMode\", session.GameMode},\n                    {\"playerCount\", session.PlayerIds.Count},\n                    {\"settings\", session.Settings}\n                }\n            };\n            \n            await eventBus.PublishAsync(gameWorldInitEvent);\n        }\n    }\n    \n    public class GameSessionAggregate\n    {\n        public string SessionId { get; set; }\n        public List<string> PlayerIds { get; set; }\n        public string GameMode { get; set; }\n        public Dictionary<string, object> Settings { get; set; }\n        public DateTime StartTime { get; set; }\n        public DateTime? EndTime { get; set; }\n        public string Status { get; set; }\n        public int Version { get; set; }\n        \n        public GameSessionAggregate()\n        {\n            PlayerIds = new List<string>();\n            Settings = new Dictionary<string, object>();\n        }\n    }\n}
```

### Event Store Implementation
```csharp
namespace UnityMicroservices.Infrastructure
{
    public interface IEventStore\n    {\n        Task SaveEventAsync(GameEvent gameEvent);\n        Task<List<GameEvent>> GetEventsAsync(string aggregateId, int fromVersion = 0);\n        Task<List<GameEvent>> GetAllEventsAsync(DateTime from, DateTime to);\n        Task SaveSnapshotAsync(string aggregateId, int version, object snapshot);\n        Task<T> GetSnapshotAsync<T>(string aggregateId) where T : class;\n    }\n    \n    public class MongoEventStore : IEventStore\n    {\n        private readonly string connectionString;\n        private readonly string databaseName;\n        private readonly string eventsCollectionName;\n        private readonly string snapshotsCollectionName;\n        \n        public MongoEventStore(string connectionString, string databaseName = \"gameevents\")\n        {\n            this.connectionString = connectionString;\n            this.databaseName = databaseName;\n            this.eventsCollectionName = \"events\";\n            this.snapshotsCollectionName = \"snapshots\";\n        }\n        \n        public async Task SaveEventAsync(GameEvent gameEvent)\n        {\n            try\n            {\n                var eventDocument = new\n                {\n                    _id = gameEvent.eventId,\n                    eventType = gameEvent.eventType,\n                    aggregateId = gameEvent.aggregateId,\n                    version = gameEvent.version,\n                    timestamp = gameEvent.timestamp,\n                    payload = JsonConvert.SerializeObject(gameEvent.payload),\n                    metadata = JsonConvert.SerializeObject(gameEvent.metadata),\n                    correlationId = gameEvent.correlationId,\n                    causationId = gameEvent.causationId\n                };\n                \n                // In a real implementation, use MongoDB driver to save\n                Debug.Log($\"Event saved to store: {gameEvent.eventType} - {gameEvent.eventId}\");\n            }\n            catch (Exception ex)\n            {\n                Debug.LogError($\"Failed to save event {gameEvent.eventId}: {ex.Message}\");\n                throw;\n            }\n        }\n        \n        public async Task<List<GameEvent>> GetEventsAsync(string aggregateId, int fromVersion = 0)\n        {\n            try\n            {\n                // In a real implementation, query MongoDB for events\n                var events = new List<GameEvent>();\n                \n                Debug.Log($\"Retrieved {events.Count} events for aggregate {aggregateId} from version {fromVersion}\");\n                \n                return events;\n            }\n            catch (Exception ex)\n            {\n                Debug.LogError($\"Failed to retrieve events for aggregate {aggregateId}: {ex.Message}\");\n                throw;\n            }\n        }\n        \n        public async Task<List<GameEvent>> GetAllEventsAsync(DateTime from, DateTime to)\n        {\n            try\n            {\n                // Query events within time range\n                var events = new List<GameEvent>();\n                \n                return events;\n            }\n            catch (Exception ex)\n            {\n                Debug.LogError($\"Failed to retrieve events for time range {from} - {to}: {ex.Message}\");\n                throw;\n            }\n        }\n        \n        public async Task SaveSnapshotAsync(string aggregateId, int version, object snapshot)\n        {\n            try\n            {\n                var snapshotDocument = new\n                {\n                    _id = $\"{aggregateId}_{version}\",\n                    aggregateId = aggregateId,\n                    version = version,\n                    timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),\n                    data = JsonConvert.SerializeObject(snapshot)\n                };\n                \n                Debug.Log($\"Snapshot saved for aggregate {aggregateId} at version {version}\");\n            }\n            catch (Exception ex)\n            {\n                Debug.LogError($\"Failed to save snapshot for aggregate {aggregateId}: {ex.Message}\");\n                throw;\n            }\n        }\n        \n        public async Task<T> GetSnapshotAsync<T>(string aggregateId) where T : class\n        {\n            try\n            {\n                // In a real implementation, find the latest snapshot\n                return null;\n            }\n            catch (Exception ex)\n            {\n                Debug.LogError($\"Failed to retrieve snapshot for aggregate {aggregateId}: {ex.Message}\");\n                return null;\n            }\n        }\n    }\n}
```

## 🚀 AI/LLM Integration Opportunities

### AI-Powered Event Analysis
```
# Prompt Template for Event-Driven Architecture Optimization
"Analyze this Unity event-driven microservices system for optimization opportunities:

Current Architecture: [PASTE EVENT DEFINITIONS AND SERVICE CODE]
Event Patterns: [List of common event types and frequencies]
Performance Issues: [Current bottlenecks and scaling challenges]
Business Requirements: [Game requirements and SLA targets]

Provide optimization recommendations for:
1. Event schema design and versioning strategies
2. Service boundary optimization and coupling reduction
3. Event sourcing and CQRS implementation improvements
4. Message queue configuration and routing optimization
5. Error handling and retry mechanism enhancements
6. Monitoring and observability implementation
7. Performance bottleneck elimination
8. Scalability and resilience improvements

Include specific Unity C# code examples and architectural patterns."
```

### Automated Service Generation
```python
# AI-powered microservice generator
class UnityMicroserviceGenerator:
    def __init__(self):
        self.template_engine = TemplateEngine()
        self.code_generator = CodeGenerator()
        
    def generate_microservice(self, service_specification):
        \"\"\"Generate complete Unity microservice from specification\"\"\"
        
        service_code = self.code_generator.generate_service_class(service_specification)
        event_definitions = self.generate_event_definitions(service_specification)
        test_code = self.generate_test_suite(service_specification)
        
        return {
            'service_implementation': service_code,
            'event_definitions': event_definitions,
            'test_suite': test_code,
            'deployment_config': self.generate_deployment_config(service_specification)
        }
```

## 💡 Key Highlights
- **Scalable Architecture**: Event-driven design enables independent service scaling and deployment
- **Resilient Communication**: Asynchronous messaging provides fault tolerance and system resilience
- **Event Sourcing**: Complete audit trail of all game events enables replay and debugging capabilities
- **Loose Coupling**: Services communicate through events, reducing dependencies and increasing maintainability
- **Real-Time Processing**: Event streams enable real-time game state updates and player notifications
- **Unity Integration**: Seamless integration with Unity game clients through optimized event protocols