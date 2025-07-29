# @h-Advanced-Mechanics-Innovation - Cutting-Edge Design Patterns for Turn-Based Games

## 🎯 Learning Objectives
- Explore innovative mechanics that push turn-based design boundaries
- Implement hybrid systems that blend turn-based with other genres
- Master temporal manipulation and non-linear turn structures
- Design emergent gameplay systems for maximum player creativity

## 🔄 Temporal Mechanics and Time Manipulation

### Time Dilation System
```csharp
public class TemporalMechanicsManager : MonoBehaviour
{
    [System.Serializable]
    public class TimeZone
    {
        public string zoneName;
        public Vector3 center;
        public float radius;
        public float timeScale; // 0.5 = half speed, 2.0 = double speed
        public TemporalEffect effect;
        public int duration; // In turns
        public bool affectsAllEntities;
        public List<string> affectedEntityTypes;
    }
    
    public enum TemporalEffect
    {
        Acceleration,    // Actions happen faster
        Deceleration,    // Actions happen slower  
        Stasis,         // Complete time stop
        Rewind,         // Reverse time effects
        Prediction,     // See future possibilities
        Echo           // Actions repeat from past
    }
    
    [System.Serializable]
    public class TemporalAction
    {
        public string actionName;
        public int originalTurn;
        public int scheduledTurn;
        public Player executor;
        public List<ActionParameter> parameters;
        public TemporalStatus status;
    }
    
    public enum TemporalStatus
    {
        Scheduled,      // Will execute in future
        Executing,      // Currently happening
        Completed,      // Has been executed
        Cancelled,      // Was cancelled before execution
        Rewound        // Was undone by time manipulation
    }
    
    [SerializeField] private List<TimeZone> activeTimeZones;
    [SerializeField] private List<TemporalAction> scheduledActions;
    [SerializeField] private int currentTurn;
    [SerializeField] private Dictionary<int, GameState> gameStateHistory;
    
    public void CreateTimeZone(TimeZone newZone)
    {
        activeTimeZones.Add(newZone);
        ApplyTemporalEffects(newZone);
        OnTimeZoneCreated?.Invoke(newZone);
    }
    
    private void ApplyTemporalEffects(TimeZone zone)
    {
        var entitiesInZone = GetEntitiesInZone(zone);
        
        foreach (var entity in entitiesInZone)
        {
            if (ShouldAffectEntity(entity, zone))
            {
                ApplyTemporalEffectToEntity(entity, zone.effect, zone.timeScale);
            }
        }
    }
    
    private void ApplyTemporalEffectToEntity(GameObject entity, TemporalEffect effect, float timeScale)
    {
        var temporalComponent = entity.GetComponent<TemporalEntity>();
        if (temporalComponent == null)
        {
            temporalComponent = entity.AddComponent<TemporalEntity>();
        }
        
        switch (effect)
        {
            case TemporalEffect.Acceleration:
                temporalComponent.SetTimeScale(timeScale);
                temporalComponent.GrantExtraTurns(Mathf.RoundToInt(timeScale - 1));
                break;
                
            case TemporalEffect.Deceleration:
                temporalComponent.SetTimeScale(timeScale);
                temporalComponent.ReduceActionsPerTurn(1.0f / timeScale);
                break;
                
            case TemporalEffect.Stasis:
                temporalComponent.EnterStasis();
                break;
                
            case TemporalEffect.Rewind:
                StartCoroutine(RewindEntity(entity, 3)); // Rewind 3 turns
                break;
                
            case TemporalEffect.Prediction:
                temporalComponent.EnableFutureSight();
                break;
                
            case TemporalEffect.Echo:
                ScheduleEchoActions(entity);
                break;
        }
    }
    
    public void ScheduleAction(TemporalAction action)
    {
        action.status = TemporalStatus.Scheduled;
        scheduledActions.Add(action);
        
        // Visual indicator for scheduled actions
        ShowScheduledActionIndicator(action);
    }
    
    public void ProcessTurn(int turnNumber)
    {
        currentTurn = turnNumber;
        
        // Save current game state for potential rewind
        gameStateHistory[turnNumber] = CaptureGameState();
        
        // Execute scheduled actions for this turn
        var actionsToExecute = scheduledActions
            .Where(a => a.scheduledTurn == turnNumber && a.status == TemporalStatus.Scheduled)
            .ToList();
        
        foreach (var action in actionsToExecute)
        {
            ExecuteScheduledAction(action);
        }
        
        // Update time zones
        UpdateTimeZones(turnNumber);
        
        // Clean up old history (keep last 10 turns)
        CleanupOldHistory(turnNumber);
    }
    
    private IEnumerator RewindEntity(GameObject entity, int turnsToRewind)
    {
        int targetTurn = Mathf.Max(0, currentTurn - turnsToRewind);
        
        if (gameStateHistory.ContainsKey(targetTurn))
        {
            var entityData = GetEntityDataFromHistory(entity, targetTurn);
            RestoreEntityState(entity, entityData);
            
            // Visual rewind effect
            yield return PlayRewindEffect(entity, turnsToRewind);
        }
    }
    
    public void CreateTimeLoop(Vector3 center, float radius, int loopLength)
    {
        var loopZone = new TimeZone
        {
            zoneName = "TimeLoop",
            center = center,
            radius = radius,
            timeScale = 1.0f,
            effect = TemporalEffect.Echo,
            duration = loopLength,
            affectsAllEntities = true
        };
        
        CreateTimeZone(loopZone);
        
        // Schedule the loop to repeat actions
        StartCoroutine(ManageTimeLoop(loopZone, loopLength));
    }
    
    private IEnumerator ManageTimeLoop(TimeZone loopZone, int loopLength)
    {
        var loopStartTurn = currentTurn;
        var recordedActions = new List<TemporalAction>();
        
        // Record actions for one loop cycle
        for (int i = 0; i < loopLength; i++)
        {
            yield return new WaitUntil(() => currentTurn > loopStartTurn + i);
            
            // Record all actions taken in the loop zone this turn
            var turnActions = GetActionsInZone(loopZone, currentTurn);
            recordedActions.AddRange(turnActions);
        }
        
        // Now replay these actions infinitely
        while (activeTimeZones.Contains(loopZone))
        {
            foreach (var action in recordedActions)
            {
                var echoAction = CreateEchoAction(action, currentTurn + (action.scheduledTurn - loopStartTurn));
                ScheduleAction(echoAction);
            }
            
            yield return new WaitForSeconds(loopLength * TurnManager.Instance.turnDuration);
        }
    }
    
    public UnityEvent<TimeZone> OnTimeZoneCreated;
    public UnityEvent<TemporalAction> OnActionScheduled;
    public UnityEvent<int> OnTimeRewind;
}
```

### Simultaneous Turn Resolution
```csharp
public class SimultaneousTurnSystem : MonoBehaviour
{
    [System.Serializable]
    public class SimultaneousPhase
    {
        public string phaseName;
        public float planningTime;
        public float executionTime;
        public bool allowActionChanges;
        public ResolutionOrder resolutionOrder;
        public List<ActionType> allowedActions;
    }
    
    public enum ResolutionOrder
    {
        Simultaneous,    // All actions happen at once
        Initiative,      // Based on initiative scores
        Priority,        // Based on action priority
        Random,          // Randomized order
        Declared        // In order actions were declared
    }
    
    [System.Serializable]
    public class PlayerAction
    {
        public Player player;
        public GameAction action;
        public int initiative;
        public int priority;
        public float declarationTime;
        public ActionStatus status;
        public List<ActionConsequence> consequences;
    }
    
    public enum ActionStatus
    {
        Planning,       // Player is still deciding
        Committed,      // Action is locked in
        Executing,      // Currently being resolved
        Completed,      // Finished execution
        Failed,         // Could not execute
        Interrupted     // Stopped by another action
    }
    
    [SerializeField] private SimultaneousPhase currentPhase;
    [SerializeField] private List<PlayerAction> committedActions;
    [SerializeField] private Dictionary<Player, bool> playerReady;
    [SerializeField] private float phaseTimer;
    
    public void StartSimultaneousPhase(SimultaneousPhase phase)
    {
        currentPhase = phase;
        phaseTimer = phase.planningTime;
        committedActions.Clear();
        playerReady.Clear();
        
        // Initialize all players as not ready
        foreach (var player in GameManager.Instance.GetActivePlayers())
        {
            playerReady[player] = false;
        }
        
        OnPhaseBegan?.Invoke(phase);
        StartCoroutine(ManagePhaseTimer());
    }
    
    private IEnumerator ManagePhaseTimer()
    {
        // Planning phase
        while (phaseTimer > 0 && !AllPlayersReady())
        {
            phaseTimer -= Time.deltaTime;
            OnTimerUpdated?.Invoke(phaseTimer);
            yield return null;
        }
        
        // Lock in all actions
        LockInAllActions();
        
        // Execution phase
        yield return StartCoroutine(ExecuteSimultaneousActions());
        
        OnPhaseCompleted?.Invoke(currentPhase);
    }
    
    public void CommitPlayerAction(Player player, GameAction action)
    {
        if (!currentPhase.allowActionChanges && GetPlayerAction(player) != null)
        {
            return; // Action already committed and changes not allowed
        }
        
        // Remove previous action if exists
        RemovePlayerAction(player);
        
        var playerAction = new PlayerAction
        {
            player = player,
            action = action,
            initiative = CalculateInitiative(player, action),
            priority = action.priority,
            declarationTime = Time.time,
            status = ActionStatus.Committed
        };
        
        committedActions.Add(playerAction);
        playerReady[player] = true;
        
        OnActionCommitted?.Invoke(playerAction);
    }
    
    private IEnumerator ExecuteSimultaneousActions()
    {
        var sortedActions = SortActionsByResolutionOrder(committedActions);
        
        switch (currentPhase.resolutionOrder)
        {
            case ResolutionOrder.Simultaneous:
                yield return ExecuteAllActionsTogether(sortedActions);
                break;
            case ResolutionOrder.Initiative:
            case ResolutionOrder.Priority:
            case ResolutionOrder.Declared:
                yield return ExecuteActionsInSequence(sortedActions);
                break;
            case ResolutionOrder.Random:
                yield return ExecuteActionsRandomly(sortedActions);
                break;
        }
    }
    
    private IEnumerator ExecuteAllActionsTogether(List<PlayerAction> actions)
    {
        // Start all actions simultaneously
        foreach (var playerAction in actions)
        {
            playerAction.status = ActionStatus.Executing;
            StartCoroutine(ExecuteSingleAction(playerAction));
        }
        
        // Wait for all actions to complete
        yield return new WaitUntil(() => actions.All(a => 
            a.status == ActionStatus.Completed || 
            a.status == ActionStatus.Failed || 
            a.status == ActionStatus.Interrupted));
        
        // Resolve conflicts and interactions
        ResolveActionInteractions(actions);
    }
    
    private void ResolveActionInteractions(List<PlayerAction> actions)
    {
        // Check for conflicts between actions
        var conflicts = DetectActionConflicts(actions);
        
        foreach (var conflict in conflicts)
        {
            ResolveConflict(conflict);
        }
        
        // Apply consequences
        foreach (var playerAction in actions)
        {
            ApplyActionConsequences(playerAction);
        }
    }
    
    private List<ActionConflict> DetectActionConflicts(List<PlayerAction> actions)
    {
        var conflicts = new List<ActionConflict>();
        
        for (int i = 0; i < actions.Count; i++)
        {
            for (int j = i + 1; j < actions.Count; j++)
            {
                var conflict = CheckForConflict(actions[i], actions[j]);
                if (conflict != null)
                {
                    conflicts.Add(conflict);
                }
            }
        }
        
        return conflicts;
    }
    
    private ActionConflict CheckForConflict(PlayerAction action1, PlayerAction action2)
    {
        // Check if actions target the same resource/location
        if (ActionsTargetSameResource(action1.action, action2.action))
        {
            return new ActionConflict
            {
                conflictType = ConflictType.ResourceContention,
                involvedActions = new List<PlayerAction> { action1, action2 },
                resolutionMethod = DetermineResolutionMethod(action1, action2)
            };
        }
        
        // Check if actions directly interfere with each other
        if (ActionsInterfere(action1.action, action2.action))
        {
            return new ActionConflict
            {
                conflictType = ConflictType.DirectInterference,
                involvedActions = new List<PlayerAction> { action1, action2 },
                resolutionMethod = ConflictResolutionMethod.Priority
            };
        }
        
        return null;
    }
    
    public UnityEvent<SimultaneousPhase> OnPhaseBegan;
    public UnityEvent<float> OnTimerUpdated;
    public UnityEvent<PlayerAction> OnActionCommitted;
    public UnityEvent<SimultaneousPhase> OnPhaseCompleted;
}
```

## 🧩 Emergent Gameplay Systems

### Dynamic Rule System
```csharp
public class DynamicRuleEngine : MonoBehaviour
{
    [System.Serializable]
    public class GameRule
    {
        public string ruleName;
        public string description;
        public RuleCondition condition;
        public RuleEffect effect;
        public RuleScope scope;
        public int priority;
        public bool isActive;
        public bool isTemporary;
        public int duration; // -1 for permanent
    }
    
    [System.Serializable]
    public class RuleCondition
    {
        public ConditionType type;
        public string parameter;
        public ComparisonOperator comparison;
        public float value;
        public List<RuleCondition> subConditions;
        public LogicalOperator logicalOperator;
    }
    
    public enum ConditionType
    {
        GameState,
        PlayerAction,
        ResourceLevel,
        TurnNumber,
        EntityCount,
        ScriptedEvent,
        PlayerBehavior,
        RandomChance
    }
    
    public enum RuleScope
    {
        Global,      // Affects entire game
        Player,      // Affects specific player
        Area,        // Affects specific game area
        Entity,      // Affects specific entities
        Temporary    // Limited duration effect
    }
    
    [System.Serializable]
    public class RuleEffect
    {
        public EffectType type;
        public string targetParameter;
        public float magnitude;
        public EffectApplication application;
        public List<string> additionalParameters;
    }
    
    public enum EffectType
    {
        ModifyValue,     // Change numerical values
        EnableAction,    // Allow new actions
        DisableAction,   // Prevent actions
        CreateEntity,    // Spawn new game elements
        TriggerEvent,    // Activate game events
        ChangeRule,      // Modify other rules
        PlayerConstraint // Limit player options
    }
    
    [SerializeField] private List<GameRule> activeRules;
    [SerializeField] private List<GameRule> potentialRules;
    [SerializeField] private RuleHistory ruleHistory;
    
    public void EvaluateRules(GameState currentState)
    {
        // Check conditions for potential new rules
        foreach (var rule in potentialRules)
        {
            if (EvaluateRuleCondition(rule.condition, currentState))
            {
                ActivateRule(rule);
            }
        }
        
        // Update existing rules
        for (int i = activeRules.Count - 1; i >= 0; i--)
        {
            var rule = activeRules[i];
            
            if (rule.isTemporary)
            {
                rule.duration--;
                if (rule.duration <= 0)
                {
                    DeactivateRule(rule);
                    continue;
                }
            }
            
            // Re-evaluate rule conditions
            if (!EvaluateRuleCondition(rule.condition, currentState))
            {
                DeactivateRule(rule);
            }
        }
    }
    
    private bool EvaluateRuleCondition(RuleCondition condition, GameState state)
    {
        bool result = EvaluateSingleCondition(condition, state);
        
        // Process sub-conditions if they exist
        if (condition.subConditions != null && condition.subConditions.Count > 0)
        {
            foreach (var subCondition in condition.subConditions)
            {
                bool subResult = EvaluateRuleCondition(subCondition, state);
                
                switch (condition.logicalOperator)
                {
                    case LogicalOperator.And:
                        result = result && subResult;
                        break;
                    case LogicalOperator.Or:
                        result = result || subResult;
                        break;
                    case LogicalOperator.Not:
                        result = result && !subResult;
                        break;
                }
            }
        }
        
        return result;
    }
    
    private bool EvaluateSingleCondition(RuleCondition condition, GameState state)
    {
        float actualValue = GetParameterValue(condition.parameter, state);
        
        switch (condition.comparison)
        {
            case ComparisonOperator.Equal:
                return Mathf.Approximately(actualValue, condition.value);
            case ComparisonOperator.GreaterThan:
                return actualValue > condition.value;
            case ComparisonOperator.LessThan:
                return actualValue < condition.value;
            case ComparisonOperator.GreaterThanOrEqual:
                return actualValue >= condition.value;
            case ComparisonOperator.LessThanOrEqual:
                return actualValue <= condition.value;
            default:
                return false;
        }
    }
    
    private void ActivateRule(GameRule rule)
    {
        if (activeRules.Contains(rule)) return;
        
        rule.isActive = true;
        activeRules.Add(rule);
        
        // Sort by priority
        activeRules.Sort((a, b) => b.priority.CompareTo(a.priority));
        
        // Apply rule effect
        ApplyRuleEffect(rule.effect);
        
        // Record in history
        ruleHistory.RecordRuleActivation(rule);
        
        OnRuleActivated?.Invoke(rule);
    }
    
    private void DeactivateRule(GameRule rule)
    {
        if (!activeRules.Contains(rule)) return;
        
        rule.isActive = false;
        activeRules.Remove(rule);
        
        // Reverse rule effect if applicable
        ReverseRuleEffect(rule.effect);
        
        // Record in history
        ruleHistory.RecordRuleDeactivation(rule);
        
        OnRuleDeactivated?.Invoke(rule);
    }
    
    private void ApplyRuleEffect(RuleEffect effect)
    {
        switch (effect.type)
        {
            case EffectType.ModifyValue:
                ModifyGameParameter(effect.targetParameter, effect.magnitude, effect.application);
                break;
            case EffectType.EnableAction:
                EnableAction(effect.targetParameter);
                break;
            case EffectType.DisableAction:
                DisableAction(effect.targetParameter);
                break;
            case EffectType.CreateEntity:
                CreateEntity(effect.targetParameter, effect.additionalParameters);
                break;
            case EffectType.TriggerEvent:
                TriggerGameEvent(effect.targetParameter);
                break;
        }
    }
    
    public void AddTemporaryRule(GameRule rule, int duration)
    {
        rule.isTemporary = true;
        rule.duration = duration;
        potentialRules.Add(rule);
        
        // Immediately evaluate if conditions are met
        EvaluateRules(GameManager.Instance.GetCurrentState());
    }
    
    public UnityEvent<GameRule> OnRuleActivated;
    public UnityEvent<GameRule> OnRuleDeactivated;
}
```

### Procedural Objective Generation
```csharp
public class ProceduralObjectiveSystem : MonoBehaviour
{
    [System.Serializable]
    public class ObjectiveTemplate
    {
        public string templateName;
        public ObjectiveType type;
        public DifficultyLevel difficulty;
        public List<ObjectiveRequirement> requirements;
        public ObjectiveReward reward;
        public ObjectiveConstraints constraints;
        public float weight; // Probability weight for selection
    }
    
    public enum ObjectiveType
    {
        Survival,        // Stay alive for X turns
        Elimination,     // Defeat X enemies
        Collection,      // Gather X resources
        Control,         // Hold territory for X turns
        Discovery,       // Explore X areas
        Protection,      // Keep allies alive
        Efficiency,      // Complete task within X turns
        Puzzle          // Solve specific challenges
    }
    
    [System.Serializable]
    public class ObjectiveRequirement
    {
        public RequirementType type;
        public string targetParameter;
        public int quantity;
        public float timeLimit;
        public List<string> conditions;
    }
    
    [System.Serializable]
    public class GeneratedObjective
    {
        public string objectiveName;
        public string description;
        public ObjectiveType type;
        public List<ObjectiveRequirement> requirements;
        public ObjectiveReward reward;
        public ObjectiveStatus status;
        public float progress;
        public int turnCreated;
    }
    
    public enum ObjectiveStatus
    {
        Generated,
        Active,
        Completed,
        Failed,
        Expired
    }
    
    [SerializeField] private List<ObjectiveTemplate> objectiveTemplates;
    [SerializeField] private List<GeneratedObjective> activeObjectives;
    [SerializeField] private int maxSimultaneousObjectives = 3;
    [SerializeField] private float objectiveGenerationRate = 0.3f; // Per turn
    
    public void UpdateObjectives(GameState currentState, int currentTurn)
    {
        // Update progress on active objectives
        UpdateObjectiveProgress(currentState);
        
        // Check for completed or failed objectives
        ProcessCompletedObjectives();
        
        // Generate new objectives if needed
        if (ShouldGenerateNewObjective(currentTurn))
        {
            GenerateNewObjective(currentState, currentTurn);
        }
    }
    
    private void UpdateObjectiveProgress(GameState state)
    {
        foreach (var objective in activeObjectives)
        {
            if (objective.status != ObjectiveStatus.Active) continue;
            
            float newProgress = CalculateObjectiveProgress(objective, state);
            
            if (newProgress != objective.progress)
            {
                objective.progress = newProgress;
                OnObjectiveProgressUpdated?.Invoke(objective);
                
                if (objective.progress >= 1.0f)
                {
                    CompleteObjective(objective);
                }
            }
        }
    }
    
    private float CalculateObjectiveProgress(GeneratedObjective objective, GameState state)
    {
        float totalProgress = 0f;
        
        foreach (var requirement in objective.requirements)
        {
            float requirementProgress = CalculateRequirementProgress(requirement, state);
            totalProgress += requirementProgress / objective.requirements.Count;
        }
        
        return Mathf.Clamp01(totalProgress);
    }
    
    private float CalculateRequirementProgress(ObjectiveRequirement requirement, GameState state)
    {
        switch (requirement.type)
        {
            case RequirementType.Count:
                int currentCount = GetParameterCount(requirement.targetParameter, state);
                return Mathf.Clamp01((float)currentCount / requirement.quantity);
                
            case RequirementType.Duration:
                float elapsedTime = GetElapsedTime(requirement.targetParameter, state);
                return Mathf.Clamp01(elapsedTime / requirement.timeLimit);
                
            case RequirementType.Condition:
                return EvaluateConditions(requirement.conditions, state) ? 1.0f : 0.0f;
                
            default:
                return 0f;
        }
    }
    
    private bool ShouldGenerateNewObjective(int currentTurn)
    {
        if (activeObjectives.Count >= maxSimultaneousObjectives)
            return false;
            
        return Random.value < objectiveGenerationRate;
    }
    
    private void GenerateNewObjective(GameState state, int currentTurn)
    {
        // Filter templates based on current game state
        var viableTemplates = FilterViableTemplates(objectiveTemplates, state);
        
        if (viableTemplates.Count == 0) return;
        
        // Select template based on weighted probability
        var selectedTemplate = SelectWeightedTemplate(viableTemplates);
        
        // Generate specific objective from template
        var newObjective = CreateObjectiveFromTemplate(selectedTemplate, state, currentTurn);
        
        // Add to active objectives
        activeObjectives.Add(newObjective);
        newObjective.status = ObjectiveStatus.Active;
        
        OnObjectiveGenerated?.Invoke(newObjective);
    }
    
    private List<ObjectiveTemplate> FilterViableTemplates(List<ObjectiveTemplate> templates, GameState state)
    {
        var viableTemplates = new List<ObjectiveTemplate>();
        
        foreach (var template in templates)
        {
            if (IsTemplateViable(template, state))
            {
                viableTemplates.Add(template);
            }
        }
        
        return viableTemplates;
    }
    
    private bool IsTemplateViable(ObjectiveTemplate template, GameState state)
    {
        // Check if template constraints are satisfied
        if (!template.constraints.CanBeUsed(state))
            return false;
            
        // Check if required elements exist in game state
        foreach (var requirement in template.requirements)
        {
            if (!RequirementCanBeFulfilled(requirement, state))
                return false;
        }
        
        return true;
    }
    
    private GeneratedObjective CreateObjectiveFromTemplate(ObjectiveTemplate template, GameState state, int turn)
    {
        var objective = new GeneratedObjective
        {
            objectiveName = GenerateObjectiveName(template, state),
            description = GenerateObjectiveDescription(template, state),
            type = template.type,
            requirements = AdaptRequirements(template.requirements, state),
            reward = CalculateReward(template, state),
            status = ObjectiveStatus.Generated,
            progress = 0f,
            turnCreated = turn
        };
        
        return objective;
    }
    
    private string GenerateObjectiveName(ObjectiveTemplate template, GameState state)
    {
        // Use contextual information to create unique names
        var contextualElements = GetContextualElements(state);
        
        switch (template.type)
        {
            case ObjectiveType.Elimination:
                return $"Eliminate {contextualElements.enemyType}s";
            case ObjectiveType.Collection:
                return $"Gather {contextualElements.resourceType}";
            case ObjectiveType.Control:
                return $"Control {contextualElements.locationName}";
            default:
                return template.templateName;
        }
    }
    
    public UnityEvent<GeneratedObjective> OnObjectiveGenerated;
    public UnityEvent<GeneratedObjective> OnObjectiveProgressUpdated;
    public UnityEvent<GeneratedObjective> OnObjectiveCompleted;
}
```

## 🌐 Hybrid Genre Integration

### Real-Time Strategy Elements
```csharp
public class HybridRTSTurnBased : MonoBehaviour
{
    [System.Serializable]
    public class RTSPhase
    {
        public string phaseName;
        public float duration;
        public bool allowsUnitMovement;
        public bool allowsResourceGathering;
        public bool allowsConstruction;
        public List<RTSAction> allowedActions;
        public int maxSimultaneousActions;
    }
    
    [System.Serializable]
    public class RTSAction
    {
        public string actionName;
        public ActionCategory category;
        public float executionTime;
        public bool canBeQueued;
        public bool canBeCancelled;
        public List<ResourceCost> costs;
    }
    
    public enum ActionCategory
    {
        Movement,
        Combat,
        Economy,
        Construction,
        Research,
        Special
    }
    
    [SerializeField] private RTSPhase currentPhase;
    [SerializeField] private List<RTSAction> queuedActions;
    [SerializeField] private Dictionary<Player, List<RTSAction>> playerActionQueues;
    [SerializeField] private float phaseTimer;
    
    public void StartRTSPhase(RTSPhase phase)
    {
        currentPhase = phase;
        phaseTimer = phase.duration;
        
        // Initialize action queues for all players
        foreach (var player in GameManager.Instance.GetActivePlayers())
        {
            if (!playerActionQueues.ContainsKey(player))
            {
                playerActionQueues[player] = new List<RTSAction>();
            }
        }
        
        OnRTSPhaseStarted?.Invoke(phase);
        StartCoroutine(ManageRTSPhase());
    }
    
    private IEnumerator ManageRTSPhase()
    {
        while (phaseTimer > 0)
        {
            phaseTimer -= Time.deltaTime;
            
            // Process queued actions
            ProcessQueuedActions();
            
            // Update UI
            OnRTSTimerUpdated?.Invoke(phaseTimer);
            
            yield return null;
        }
        
        // Phase ended - return to turn-based mode
        OnRTSPhaseEnded?.Invoke(currentPhase);
        ReturnToTurnBasedMode();
    }
    
    public bool QueueAction(Player player, RTSAction action)
    {
        if (!currentPhase.allowedActions.Contains(action))
            return false;
            
        var playerQueue = playerActionQueues[player];
        
        if (playerQueue.Count >= currentPhase.maxSimultaneousActions)
            return false;
            
        // Check if player can afford the action
        if (!CanAffordAction(player, action))
            return false;
            
        // Add to queue
        playerQueue.Add(action);
        
        // Start executing immediately if it's the first in queue
        if (playerQueue.Count == 1)
        {
            StartCoroutine(ExecuteRTSAction(player, action));
        }
        
        OnActionQueued?.Invoke(player, action);
        return true;
    }
    
    private IEnumerator ExecuteRTSAction(Player player, RTSAction action)
    {
        action.status = ActionStatus.Executing;
        OnActionStarted?.Invoke(player, action);
        
        // Consume resources
        ConsumeActionCosts(player, action);
        
        // Execute over time
        float elapsed = 0f;
        
        while (elapsed < action.executionTime)
        {
            elapsed += Time.deltaTime;
            
            // Update action progress
            float progress = elapsed / action.executionTime;
            OnActionProgress?.Invoke(player, action, progress);
            
            // Check if action was cancelled
            if (action.status == ActionStatus.Cancelled)
            {
                RefundActionCosts(player, action, progress);
                yield break;
            }
            
            yield return null;
        }
        
        // Action completed
        action.status = ActionStatus.Completed;
        ApplyActionEffects(player, action);
        
        // Remove from queue
        playerActionQueues[player].Remove(action);
        
        // Start next action in queue if available
        if (playerActionQueues[player].Count > 0)
        {
            var nextAction = playerActionQueues[player][0];
            StartCoroutine(ExecuteRTSAction(player, nextAction));
        }
        
        OnActionCompleted?.Invoke(player, action);
    }
    
    public void CancelAction(Player player, RTSAction action)
    {
        if (!action.canBeCancelled) return;
        
        action.status = ActionStatus.Cancelled;
        OnActionCancelled?.Invoke(player, action);
    }
    
    private void ProcessQueuedActions()
    {
        foreach (var playerQueue in playerActionQueues)
        {
            var player = playerQueue.Key;
            var actions = playerQueue.Value;
            
            // Update action priorities based on game state
            UpdateActionPriorities(player, actions);
            
            // Handle action conflicts
            ResolveActionConflicts(player, actions);
        }
    }
    
    private void ReturnToTurnBasedMode()
    {
        // Complete all ongoing actions instantly or convert them to turn-based actions
        foreach (var playerQueue in playerActionQueues)
        {
            foreach (var action in playerQueue.Value)
            {
                if (action.status == ActionStatus.Executing)
                {
                    ConvertToTurnBasedAction(playerQueue.Key, action);
                }
            }
        }
        
        // Clear queues
        foreach (var queue in playerActionQueues.Values)
        {
            queue.Clear();
        }
        
        // Resume turn-based gameplay
        TurnManager.Instance.ResumeTurnBasedMode();
    }
    
    public UnityEvent<RTSPhase> OnRTSPhaseStarted;
    public UnityEvent<float> OnRTSTimerUpdated;
    public UnityEvent<Player, RTSAction> OnActionQueued;
    public UnityEvent<Player, RTSAction> OnActionCompleted;
    public UnityEvent<RTSPhase> OnRTSPhaseEnded;
}
```

### Puzzle Integration System
```csharp
public class TurnBasedPuzzleIntegration : MonoBehaviour
{
    [System.Serializable]
    public class PuzzleChallenge
    {
        public string puzzleName;
        public PuzzleType type;
        public DifficultyLevel difficulty;
        public PuzzleState currentState;
        public List<PuzzleElement> elements;
        public PuzzleVictoryCondition victoryCondition;
        public int turnLimit;
        public bool isOptional;
    }
    
    public enum PuzzleType
    {
        Logic,          // Pattern recognition, deduction
        Spatial,        // Movement, positioning
        Resource,       // Optimization challenges
        Temporal,       // Time-based sequences
        Social,         // Multi-player cooperation
        Hybrid         // Combines multiple types
    }
    
    [System.Serializable]
    public class PuzzleElement
    {
        public string elementName;
        public Vector3 position;
        public ElementState state;
        public List<ElementInteraction> possibleInteractions;
        public bool isMovable;
        public bool isActivatable;
    }
    
    public enum ElementState
    {
        Inactive,
        Active,
        Locked,
        Broken,
        Solved
    }
    
    [SerializeField] private List<PuzzleChallenge> activePuzzles;
    [SerializeField] private PuzzleGenerator puzzleGenerator;
    [SerializeField] private GameStateIntegrator stateIntegrator;
    
    public void IntegratePuzzleIntoTurn(PuzzleChallenge puzzle, GameState currentState)
    {
        // Modify game rules to accommodate puzzle
        var puzzleRules = CreatePuzzleRules(puzzle);
        foreach (var rule in puzzleRules)
        {
            GameRuleManager.Instance.AddTemporaryRule(rule, puzzle.turnLimit);
        }
        
        // Add puzzle-specific actions to available actions
        var puzzleActions = GeneratePuzzleActions(puzzle);
        ActionManager.Instance.AddTemporaryActions(puzzleActions);
        
        // Integrate puzzle state with game state
        stateIntegrator.IntegratePuzzleState(puzzle, currentState);
        
        OnPuzzleIntegrated?.Invoke(puzzle);
    }
    
    private List<GameRule> CreatePuzzleRules(PuzzleChallenge puzzle)
    {
        var rules = new List<GameRule>();
        
        switch (puzzle.type)
        {
            case PuzzleType.Logic:
                rules.AddRange(CreateLogicPuzzleRules(puzzle));
                break;
            case PuzzleType.Spatial:
                rules.AddRange(CreateSpatialPuzzleRules(puzzle));
                break;
            case PuzzleType.Resource:
                rules.AddRange(CreateResourcePuzzleRules(puzzle));
                break;
            case PuzzleType.Temporal:
                rules.AddRange(CreateTemporalPuzzleRules(puzzle));
                break;
        }
        
        return rules;
    }
    
    private List<GameRule> CreateLogicPuzzleRules(PuzzleChallenge puzzle)
    {
        var rules = new List<GameRule>();
        
        // Example: Pattern matching puzzle
        rules.Add(new GameRule
        {
            ruleName = "Pattern Recognition",
            description = "Actions must follow discovered pattern",
            condition = new RuleCondition
            {
                type = ConditionType.PlayerAction,
                parameter = "ActionSequence"
            },
            effect = new RuleEffect
            {
                type = EffectType.PlayerConstraint,
                targetParameter = "ValidatePattern"
            },
            scope = RuleScope.Player,
            isTemporary = true,
            duration = puzzle.turnLimit
        });
        
        return rules;
    }
    
    public void ProcessPuzzleAction(Player player, PuzzleAction action, PuzzleChallenge puzzle)
    {
        // Validate action is legal for current puzzle state
        if (!IsValidPuzzleAction(action, puzzle))
        {
            OnInvalidPuzzleAction?.Invoke(player, action, puzzle);
            return;
        }
        
        // Apply action to puzzle state
        ApplyPuzzleAction(action, puzzle);
        
        // Check for puzzle completion
        if (IsPuzzleSolved(puzzle))
        {
            CompletePuzzle(puzzle, player);
        }
        else if (puzzle.turnLimit <= 0)
        {
            FailPuzzle(puzzle, player);
        }
        
        OnPuzzleActionProcessed?.Invoke(player, action, puzzle);
    }
    
    private bool IsValidPuzzleAction(PuzzleAction action, PuzzleChallenge puzzle)
    {
        var targetElement = puzzle.elements.Find(e => e.elementName == action.targetElement);
        if (targetElement == null) return false;
        
        return targetElement.possibleInteractions.Any(i => i.actionType == action.actionType);
    }
    
    private void CompletePuzzle(PuzzleChallenge puzzle, Player solver)
    {
        puzzle.currentState = PuzzleState.Solved;
        
        // Award puzzle rewards
        AwardPuzzleRewards(puzzle, solver);
        
        // Remove puzzle rules
        RemovePuzzleRules(puzzle);
        
        // Integrate solution effects into game state
        ApplyPuzzleSolutionEffects(puzzle, solver);
        
        OnPuzzleCompleted?.Invoke(puzzle, solver);
    }
    
    private void AwardPuzzleRewards(PuzzleChallenge puzzle, Player solver)
    {
        var rewards = CalculatePuzzleRewards(puzzle);
        
        foreach (var reward in rewards)
        {
            solver.inventory.AddReward(reward);
        }
        
        // Bonus rewards for efficiency
        if (puzzle.turnLimit > 0)
        {
            var efficiencyBonus = CalculateEfficiencyBonus(puzzle);
            solver.inventory.AddReward(efficiencyBonus);
        }
    }
    
    public UnityEvent<PuzzleChallenge> OnPuzzleIntegrated;
    public UnityEvent<Player, PuzzleAction, PuzzleChallenge> OnPuzzleActionProcessed;
    public UnityEvent<PuzzleChallenge, Player> OnPuzzleCompleted;
}
```

## 🚀 AI/LLM Integration Opportunities

### Dynamic Mechanic Generation
```
Generate innovative turn-based game mechanics based on these constraints:

Game Context:
- Genre: [GAME_TYPE]
- Theme: [SETTING/THEME]
- Target complexity: [COMPLEXITY_LEVEL]
- Player count: [PLAYER_COUNT]

Existing Mechanics:
- [CURRENT_MECHANICS_LIST]

Innovation Goals:
- Create unique decision points
- Increase strategic depth
- Maintain accessibility
- Encourage creative play

Requirements:
- Must integrate with existing systems
- Should create emergent gameplay
- Provide clear risk/reward tradeoffs
- Support multiple play styles

Generate 3 detailed mechanic proposals with:
1. Core mechanic description
2. Unity implementation outline
3. Balance considerations
4. Player psychology impact
5. Potential edge cases

Format as Unity-compatible design documents.
```

### Emergent Narrative Integration
```csharp
public class EmergentNarrativeSystem : MonoBehaviour
{
    public void GenerateContextualNarrative(GameState state)
    {
        string narrativePrompt = $@"
        Generate contextual narrative elements for current game state:
        
        Game Situation:
        - Turn: {state.turnNumber}
        - Player actions: {GetRecentActions()}
        - World state: {GetWorldDescription()}
        - Dramatic tension: {CalculateTension():F2}
        
        Narrative Requirements:
        - Reflect player choices and consequences
        - Maintain thematic consistency
        - Create meaningful character moments
        - Support strategic decision-making
        
        Generate:
        1. Atmospheric descriptions for current situation
        2. Character dialogue reflecting game state
        3. Environmental storytelling elements
        4. Potential future narrative hooks
        
        Keep narrative elements concise and game-relevant.
        ";
        
        string narrative = LLMInterface.GenerateNarrative(narrativePrompt);
        IntegrateNarrativeElements(narrative, state);
    }
}
```

### Adaptive Balance Suggestions
```
Analyze emergent gameplay patterns and suggest balance adjustments:

Emergent Patterns Observed:
- [PLAYER_STRATEGY_PATTERNS]
- [UNEXPECTED_COMBOS]
- [DOMINANT_TACTICS]

Game Metrics:
- Win rates: [WIN_RATE_DATA]
- Strategy diversity: [DIVERSITY_METRICS]
- Player engagement: [ENGAGEMENT_DATA]

Design Intent vs Reality:
- Intended strategies: [DESIGN_GOALS]
- Actual player behavior: [OBSERVED_BEHAVIOR]
- Unexpected interactions: [EMERGENT_BEHAVIORS]

Recommend:
1. Mechanical adjustments to encourage variety
2. New systems to support underused strategies
3. Balance changes to reduce dominant patterns
4. Innovations to increase strategic depth

Prioritize changes that preserve positive emergent behaviors while addressing balance issues.
```

## 💡 Next-Generation Mechanics

### Quantum Decision Systems
```csharp
public class QuantumDecisionSystem : MonoBehaviour
{
    [System.Serializable]
    public class QuantumState
    {
        public string stateName;
        public float probability;
        public GameState associatedState;
        public bool hasCollapsed;
        public List<QuantumEntanglement> entanglements;
    }
    
    [System.Serializable]
    public class QuantumAction
    {
        public string actionName;
        public List<QuantumOutcome> possibleOutcomes;
        public bool causesCollapse;
        public float coherenceTime;
        public QuantumMeasurement measurement;
    }
    
    [SerializeField] private List<QuantumState> superpositionStates;
    [SerializeField] private QuantumCoherence currentCoherence;
    
    public void CreateSuperposition(List<GameState> possibleStates)
    {
        superpositionStates.Clear();
        
        float totalProbability = 1.0f / possibleStates.Count;
        
        foreach (var state in possibleStates)
        {
            superpositionStates.Add(new QuantumState
            {
                stateName = state.stateName,
                probability = totalProbability,
                associatedState = state,
                hasCollapsed = false
            });
        }
        
        OnSuperpositionCreated?.Invoke(superpositionStates);
    }
    
    public void ExecuteQuantumAction(QuantumAction action)
    {
        if (action.causesCollapse)
        {
            CollapseWaveFunction(action.measurement);
        }
        else
        {
            ModifySuperposition(action);
        }
    }
    
    private void CollapseWaveFunction(QuantumMeasurement measurement)
    {
        // Select outcome based on probabilities
        float random = Random.value;
        float cumulativeProbability = 0f;
        
        foreach (var state in superpositionStates)
        {
            cumulativeProbability += state.probability;
            if (random <= cumulativeProbability)
            {
                // Collapse to this state
                CollapseToState(state);
                break;
            }
        }
    }
    
    public UnityEvent<List<QuantumState>> OnSuperpositionCreated;
    public UnityEvent<QuantumState> OnWaveFunctionCollapsed;
}
```

---

*Advanced mechanics innovation v1.0 | Genre-pushing design | Emergent complexity optimization*