# @e-AI-Opponent-Design-Patterns - Intelligent AI Systems for Turn-Based Games

## 🎯 Learning Objectives
- Design AI opponents that provide engaging, balanced challenges
- Implement multiple AI personality types with distinct behavioral patterns
- Create adaptive difficulty systems that respond to player skill progression
- Understand AI decision-making frameworks for turn-based strategic depth

## 🤖 Core AI Architecture Patterns

### Modular AI Decision System
```csharp
public abstract class AIOpponent : MonoBehaviour
{
    [System.Serializable]
    public class AIPersonality
    {
        public string personalityName;
        public AIArchetype archetype;
        public float aggression;      // 0-1: Passive to highly aggressive
        public float riskTolerance;   // 0-1: Risk-averse to risk-seeking
        public float planning;        // 0-1: Reactive to long-term planner
        public float adaptability;    // 0-1: Rigid to highly adaptive
        public float efficiency;      // 0-1: Wasteful to hyper-efficient
    }
    
    public enum AIArchetype
    {
        Aggressive,    // High-pressure, fast expansion
        Defensive,     // Turtle, late-game focused
        Economic,      // Resource optimization focus
        Adaptive,      // Responds to player strategy
        Chaotic,       // Unpredictable, creative plays
        Analytical,    // Calculated, optimal moves
        Opportunistic, // Exploits player mistakes
        Balanced       // Well-rounded approach
    }
    
    [SerializeField] protected AIPersonality personality;
    [SerializeField] protected AIDecisionEngine decisionEngine;
    [SerializeField] protected float difficultyMultiplier = 1.0f;
    
    public abstract AIAction SelectBestAction(GameState currentState, List<AIAction> availableActions);
    
    protected virtual float EvaluateAction(AIAction action, GameState state)
    {
        float baseValue = action.GetBaseUtility();
        float personalityModifier = ApplyPersonalityModifiers(action, state);
        float situationalModifier = ApplySituationalModifiers(action, state);
        
        return baseValue * personalityModifier * situationalModifier * difficultyMultiplier;
    }
    
    protected virtual float ApplyPersonalityModifiers(AIAction action, GameState state)
    {
        float modifier = 1.0f;
        
        switch (action.actionType)
        {
            case ActionType.Attack:
                modifier *= (1.0f + personality.aggression);
                break;
            case ActionType.Defend:
                modifier *= (2.0f - personality.aggression); // Inverse of aggression
                break;
            case ActionType.Economy:
                modifier *= (action.isRisky ? personality.riskTolerance : (2.0f - personality.riskTolerance));
                break;
            case ActionType.LongTerm:
                modifier *= (1.0f + personality.planning);
                break;
        }
        
        return modifier;
    }
}
```

### Hierarchical AI Decision Tree
```csharp
public class HierarchicalAI : AIOpponent
{
    [System.Serializable]
    public class DecisionNode
    {
        public string nodeName;
        public NodeType type;
        public List<DecisionCondition> conditions;
        public List<DecisionNode> children;
        public AIAction associatedAction;
        public float weight;
    }
    
    public enum NodeType
    {
        Strategic,    // High-level strategic decisions
        Tactical,     // Mid-level tactical choices
        Operational,  // Low-level execution decisions
        Emergency     // Crisis response decisions
    }
    
    [System.Serializable]
    public class DecisionCondition
    {
        public string conditionName;
        public ConditionType type;
        public float threshold;
        public bool isTrue;
    }
    
    public enum ConditionType
    {
        ResourceLevel,
        HealthPercentage,
        EnemyStrength,
        TurnNumber,
        PlayerBehaviorPattern,
        MapControl,
        TimeRemaining
    }
    
    [SerializeField] private DecisionNode rootNode;
    [SerializeField] private Dictionary<string, float> gameStateValues;
    
    public override AIAction SelectBestAction(GameState currentState, List<AIAction> availableActions)
    {
        UpdateGameStateValues(currentState);
        var selectedNode = TraverseDecisionTree(rootNode, currentState);
        
        if (selectedNode?.associatedAction != null)
        {
            return OptimizeActionParameters(selectedNode.associatedAction, currentState);
        }
        
        // Fallback to utility-based selection
        return SelectHighestUtilityAction(availableActions, currentState);
    }
    
    private DecisionNode TraverseDecisionTree(DecisionNode currentNode, GameState state)
    {
        // Evaluate conditions for current node
        bool allConditionsMet = true;
        foreach (var condition in currentNode.conditions)
        {
            if (!EvaluateCondition(condition, state))
            {
                allConditionsMet = false;
                break;
            }
        }
        
        if (!allConditionsMet)
        {
            return null;
        }
        
        // If this is a leaf node, return it
        if (currentNode.children.Count == 0)
        {
            return currentNode;
        }
        
        // Recursively evaluate children
        DecisionNode bestChild = null;
        float bestWeight = -1f;
        
        foreach (var child in currentNode.children)
        {
            var result = TraverseDecisionTree(child, state);
            if (result != null && result.weight > bestWeight)
            {
                bestChild = result;
                bestWeight = result.weight;
            }
        }
        
        return bestChild;
    }
    
    private bool EvaluateCondition(DecisionCondition condition, GameState state)
    {
        float currentValue = GetStateValue(condition.conditionName, state);
        
        switch (condition.type)
        {
            case ConditionType.ResourceLevel:
                return currentValue >= condition.threshold;
            case ConditionType.HealthPercentage:
                return currentValue >= condition.threshold;
            case ConditionType.EnemyStrength:
                return currentValue <= condition.threshold; // Lower enemy strength is better
            default:
                return currentValue >= condition.threshold;
        }
    }
}
```

### Behavior Tree AI Implementation
```csharp
public abstract class BTNode
{
    public enum NodeState
    {
        Running,
        Success,
        Failure
    }
    
    protected NodeState state = NodeState.Running;
    public NodeState State { get { return state; } }
    
    public abstract NodeState Evaluate(AIContext context);
}

public class BTSelector : BTNode
{
    private List<BTNode> children = new List<BTNode>();
    
    public BTSelector(List<BTNode> children)
    {
        this.children = children;
    }
    
    public override NodeState Evaluate(AIContext context)
    {
        foreach (var child in children)
        {
            switch (child.Evaluate(context))
            {
                case NodeState.Success:
                    state = NodeState.Success;
                    return state;
                case NodeState.Running:
                    state = NodeState.Running;
                    return state;
                case NodeState.Failure:
                    continue; // Try next child
            }
        }
        
        state = NodeState.Failure;
        return state;
    }
}

public class BTSequence : BTNode
{
    private List<BTNode> children = new List<BTNode>();
    
    public BTSequence(List<BTNode> children)
    {
        this.children = children;
    }
    
    public override NodeState Evaluate(AIContext context)
    {
        foreach (var child in children)
        {
            switch (child.Evaluate(context))
            {
                case NodeState.Failure:
                    state = NodeState.Failure;
                    return state;
                case NodeState.Running:
                    state = NodeState.Running;
                    return state;
                case NodeState.Success:
                    continue; // Continue to next child
            }
        }
        
        state = NodeState.Success;
        return state;
    }
}

public class BehaviorTreeAI : AIOpponent
{
    [SerializeField] private BTNode rootNode;
    
    private void Start()
    {
        BuildBehaviorTree();
    }
    
    private void BuildBehaviorTree()
    {
        // Example behavior tree for aggressive AI
        var attackSequence = new BTSequence(new List<BTNode>
        {
            new CheckEnemyInRange(),
            new CheckHealthAboveThreshold(0.3f),
            new ExecuteAttack()
        });
        
        var defendSequence = new BTSequence(new List<BTNode>
        {
            new CheckHealthBelowThreshold(0.5f),
            new CheckCanDefend(),
            new ExecuteDefense()
        });
        
        var economySequence = new BTSequence(new List<BTNode>
        {
            new CheckResourcesLow(),
            new CheckCanGatherResources(),
            new ExecuteResourceGathering()
        });
        
        rootNode = new BTSelector(new List<BTNode>
        {
            attackSequence,
            defendSequence,
            economySequence
        });
    }
    
    public override AIAction SelectBestAction(GameState currentState, List<AIAction> availableActions)
    {
        var context = new AIContext(currentState, availableActions, personality);
        
        var result = rootNode.Evaluate(context);
        
        if (result == BTNode.NodeState.Success && context.selectedAction != null)
        {
            return context.selectedAction;
        }
        
        // Fallback to random action
        return availableActions[Random.Range(0, availableActions.Count)];
    }
}
```

## 🧠 AI Personality Systems

### Dynamic Personality Adaptation
```csharp
public class AdaptivePersonalityAI : AIOpponent
{
    [System.Serializable]
    public class PersonalityTrait
    {
        public string traitName;
        public float currentValue;
        public float baseValue;
        public float adaptationRate;
        public float min = 0f;
        public float max = 1f;
    }
    
    [SerializeField] private List<PersonalityTrait> traits;
    [SerializeField] private PlayerBehaviorAnalyzer playerAnalyzer;
    
    private void Update()
    {
        if (ShouldAdaptPersonality())
        {
            AdaptToPlayerBehavior();
        }
    }
    
    private void AdaptToPlayerBehavior()
    {
        var playerProfile = playerAnalyzer.GetCurrentPlayerProfile();
        
        // Counter-adapt to player strategies
        if (playerProfile.isAggressive)
        {
            AdjustTrait("defensiveness", 0.2f);
            AdjustTrait("riskTolerance", -0.1f);
        }
        
        if (playerProfile.isEconomyFocused)
        {
            AdjustTrait("aggression", 0.15f);
            AdjustTrait("earlyPressure", 0.25f);
        }
        
        if (playerProfile.makesMistakes)
        {
            AdjustTrait("opportunism", 0.3f);
            AdjustTrait("patience", 0.1f);
        }
        
        // Normalize traits to prevent extreme values
        NormalizeTraits();
    }
    
    private void AdjustTrait(string traitName, float adjustment)
    {
        var trait = traits.Find(t => t.traitName == traitName);
        if (trait != null)
        {
            float targetValue = trait.currentValue + adjustment;
            trait.currentValue = Mathf.Lerp(trait.currentValue, targetValue, trait.adaptationRate * Time.deltaTime);
            trait.currentValue = Mathf.Clamp(trait.currentValue, trait.min, trait.max);
        }
    }
    
    private void NormalizeTraits()
    {
        // Ensure traits maintain realistic relationships
        var aggression = GetTraitValue("aggression");
        var defensiveness = GetTraitValue("defensiveness");
        
        // Aggression and defensiveness should be somewhat inverse
        if (aggression + defensiveness > 1.5f)
        {
            float total = aggression + defensiveness;
            SetTraitValue("aggression", aggression / total * 1.5f);
            SetTraitValue("defensiveness", defensiveness / total * 1.5f);
        }
    }
}
```

### Multi-Layered AI Personality
```csharp
public class LayeredPersonalityAI : AIOpponent
{
    [System.Serializable]
    public class PersonalityLayer
    {
        public string layerName;
        public LayerType type;
        public float influence; // How much this layer affects decisions
        public List<TraitModifier> modifiers;
        public bool isActive;
    }
    
    public enum LayerType
    {
        Core,          // Fundamental personality traits
        Situational,   // Context-dependent behaviors
        Emotional,     // Current emotional state
        Strategic,     // Long-term strategic preferences
        Reactive       // Response to recent events
    }
    
    [System.Serializable]
    public class TraitModifier
    {
        public string targetTrait;
        public float modifier;
        public ModifierType type;
    }
    
    public enum ModifierType
    {
        Additive,
        Multiplicative,
        Override
    }
    
    [SerializeField] private List<PersonalityLayer> personalityLayers;
    [SerializeField] private Dictionary<string, float> compiledTraits;
    
    private void Start()
    {
        CompilePersonalityTraits();
    }
    
    private void CompilePersonalityTraits()
    {
        compiledTraits = new Dictionary<string, float>();
        
        // Start with base trait values
        InitializeBaseTraits();
        
        // Apply each personality layer in order of influence
        var sortedLayers = personalityLayers
            .Where(layer => layer.isActive)
            .OrderBy(layer => layer.influence)
            .ToList();
        
        foreach (var layer in sortedLayers)
        {
            ApplyPersonalityLayer(layer);
        }
    }
    
    private void ApplyPersonalityLayer(PersonalityLayer layer)
    {
        foreach (var modifier in layer.modifiers)
        {
            if (!compiledTraits.ContainsKey(modifier.targetTrait))
            {
                compiledTraits[modifier.targetTrait] = 0.5f; // Default value
            }
            
            float currentValue = compiledTraits[modifier.targetTrait];
            
            switch (modifier.type)
            {
                case ModifierType.Additive:
                    compiledTraits[modifier.targetTrait] = currentValue + (modifier.modifier * layer.influence);
                    break;
                case ModifierType.Multiplicative:
                    compiledTraits[modifier.targetTrait] = currentValue * (1.0f + modifier.modifier * layer.influence);
                    break;
                case ModifierType.Override:
                    if (layer.influence > 0.8f) // Only strong influences can override
                    {
                        compiledTraits[modifier.targetTrait] = modifier.modifier;
                    }
                    break;
            }
            
            // Clamp values to valid range
            compiledTraits[modifier.targetTrait] = Mathf.Clamp01(compiledTraits[modifier.targetTrait]);
        }
    }
    
    public void TriggerEmotionalResponse(EmotionalTrigger trigger)
    {
        var emotionalLayer = personalityLayers.Find(layer => layer.type == LayerType.Emotional);
        if (emotionalLayer != null)
        {
            ApplyEmotionalTrigger(emotionalLayer, trigger);
            CompilePersonalityTraits(); // Recompile with new emotional state
        }
    }
}
```

## 🎯 Difficulty Scaling and Adaptation

### Adaptive Difficulty System
```csharp
public class AdaptiveDifficultyManager : MonoBehaviour
{
    [System.Serializable]
    public class DifficultyMetrics
    {
        public float playerWinRate;
        public float averageGameLength;
        public float playerEngagement;
        public float frustractionLevel;
        public float skillProgression;
    }
    
    [System.Serializable]
    public class DifficultyAdjustment
    {
        public string adjustmentName;
        public AdjustmentType type;
        public float magnitude;
        public float applicationRate; // How quickly to apply
    }
    
    public enum AdjustmentType
    {
        AIIntelligence,     // Smarter decision making
        AIResources,        // Economic advantages
        AISpeed,            // Faster actions/responses
        PlayerHandicaps,    // Temporary player boosts
        GameRules,          // Modify game mechanics
        AIPersonality       // Change AI behavior patterns
    }
    
    [SerializeField] private DifficultyMetrics currentMetrics;
    [SerializeField] private List<DifficultyAdjustment> availableAdjustments;
    [SerializeField] private float targetWinRate = 0.45f; // Slightly favor player
    [SerializeField] private float adjustmentThreshold = 0.1f;
    
    public void UpdateDifficulty()
    {
        AnalyzePlayerPerformance();
        
        if (NeedsDifficultyAdjustment())
        {
            var adjustments = SelectAppropriateAdjustments();
            ApplyDifficultyAdjustments(adjustments);
        }
    }
    
    private void AnalyzePlayerPerformance()
    {
        // Collect metrics from recent games
        var recentGames = GameHistoryManager.Instance.GetRecentGames(10);
        
        currentMetrics.playerWinRate = CalculateWinRate(recentGames);
        currentMetrics.averageGameLength = CalculateAverageLength(recentGames);
        currentMetrics.playerEngagement = AnalyzeEngagementPatterns(recentGames);
        currentMetrics.frustractionLevel = DetectFrustrationIndicators(recentGames);
        currentMetrics.skillProgression = MeasureSkillProgression(recentGames);
    }
    
    private bool NeedsDifficultyAdjustment()
    {
        // Check if player performance deviates significantly from target
        float winRateDeviation = Mathf.Abs(currentMetrics.playerWinRate - targetWinRate);
        
        if (winRateDeviation > adjustmentThreshold)
        {
            return true;
        }
        
        // Check for other indicators
        if (currentMetrics.frustractionLevel > 0.7f)
        {
            return true; // Player is getting frustrated
        }
        
        if (currentMetrics.playerEngagement < 0.3f)
        {
            return true; // Player is losing interest
        }
        
        return false;
    }
    
    private List<DifficultyAdjustment> SelectAppropriateAdjustments()
    {
        var adjustments = new List<DifficultyAdjustment>();
        
        if (currentMetrics.playerWinRate > targetWinRate + adjustmentThreshold)
        {
            // Player winning too much - increase difficulty
            adjustments.Add(new DifficultyAdjustment
            {
                adjustmentName = "Increase AI Intelligence",
                type = AdjustmentType.AIIntelligence,
                magnitude = 0.1f,
                applicationRate = 0.05f
            });
        }
        else if (currentMetrics.playerWinRate < targetWinRate - adjustmentThreshold)
        {
            // Player losing too much - decrease difficulty
            adjustments.Add(new DifficultyAdjustment
            {
                adjustmentName = "Provide Player Handicap",
                type = AdjustmentType.PlayerHandicaps,
                magnitude = 0.15f,
                applicationRate = 0.1f
            });
        }
        
        if (currentMetrics.frustractionLevel > 0.6f)
        {
            // Reduce frustration by making AI more predictable
            adjustments.Add(new DifficultyAdjustment
            {
                adjustmentName = "Reduce AI Unpredictability",
                type = AdjustmentType.AIPersonality,
                magnitude = -0.2f,
                applicationRate = 0.15f
            });
        }
        
        return adjustments;
    }
    
    private void ApplyDifficultyAdjustments(List<DifficultyAdjustment> adjustments)
    {
        foreach (var adjustment in adjustments)
        {
            switch (adjustment.type)
            {
                case AdjustmentType.AIIntelligence:
                    AdjustAIIntelligence(adjustment.magnitude);
                    break;
                case AdjustmentType.AIResources:
                    AdjustAIResources(adjustment.magnitude);
                    break;
                case AdjustmentType.PlayerHandicaps:
                    ApplyPlayerHandicap(adjustment.magnitude);
                    break;
                case AdjustmentType.AIPersonality:
                    AdjustAIPersonality(adjustment.magnitude);
                    break;
            }
        }
    }
}
```

### Rubber Band AI System
```csharp
public class RubberBandAI : AIOpponent
{
    [System.Serializable]
    public class GameStateAnalysis
    {
        public float playerAdvantage; // -1 to 1 (AI advantage to player advantage)
        public float gameProgressPercent; // 0 to 1
        public bool isCloseGame;
        public float tensionLevel;
    }
    
    [SerializeField] private GameStateAnalysis currentAnalysis;
    [SerializeField] private float rubberBandStrength = 0.3f;
    [SerializeField] private AnimationCurve rubberBandCurve;
    
    public override AIAction SelectBestAction(GameState currentState, List<AIAction> availableActions)
    {
        AnalyzeGameState(currentState);
        
        var baseActions = EvaluateAllActions(availableActions, currentState);
        var adjustedActions = ApplyRubberBandLogic(baseActions);
        
        return SelectFromAdjustedActions(adjustedActions);
    }
    
    private void AnalyzeGameState(GameState state)
    {
        currentAnalysis.playerAdvantage = CalculatePlayerAdvantage(state);
        currentAnalysis.gameProgressPercent = CalculateGameProgress(state);
        currentAnalysis.isCloseGame = IsGameClose(state);
        currentAnalysis.tensionLevel = CalculateTension(state);
    }
    
    private List<ScoredAction> ApplyRubberBandLogic(List<ScoredAction> baseActions)
    {
        float rubberBandFactor = CalculateRubberBandFactor();
        
        foreach (var action in baseActions)
        {
            // If player is ahead, boost AI actions that help catch up
            if (currentAnalysis.playerAdvantage > 0.2f)
            {
                if (action.action.helpsAICatchUp)
                {
                    action.score *= (1.0f + rubberBandFactor);
                }
            }
            // If AI is ahead, slightly reduce AI efficiency to keep game close
            else if (currentAnalysis.playerAdvantage < -0.2f)
            {
                if (action.action.maintainsAIAdvantage)
                {
                    action.score *= (1.0f - rubberBandFactor * 0.5f);
                }
            }
            
            // Boost dramatic/exciting actions when game is close
            if (currentAnalysis.isCloseGame && action.action.isDramatic)
            {
                action.score *= (1.0f + rubberBandFactor * 0.5f);
            }
        }
        
        return baseActions;
    }
    
    private float CalculateRubberBandFactor()
    {
        float advantageMagnitude = Mathf.Abs(currentAnalysis.playerAdvantage);
        float progressFactor = rubberBandCurve.Evaluate(currentAnalysis.gameProgressPercent);
        
        return rubberBandStrength * advantageMagnitude * progressFactor;
    }
    
    private bool IsGameClose(GameState state)
    {
        // Determine if the game is in a close/exciting state
        float scoreDifference = Mathf.Abs(state.playerScore - state.aiScore);
        float maxPossibleScore = state.maxScore;
        
        return scoreDifference / maxPossibleScore < 0.15f; // Within 15% is "close"
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### LLM-Enhanced AI Decision Making
```csharp
public class LLMEnhancedAI : AIOpponent
{
    [System.Serializable]
    public class DecisionContext
    {
        public GameState currentState;
        public List<AIAction> availableActions;
        public string gameHistory;
        public PlayerBehaviorPattern playerPattern;
    }
    
    public override AIAction SelectBestAction(GameState currentState, List<AIAction> availableActions)
    {
        // Use traditional AI for basic filtering
        var viableActions = FilterViableActions(availableActions, currentState);
        
        // If decision is complex or novel, consult LLM
        if (IsComplexDecision(viableActions, currentState) || IsNovelSituation(currentState))
        {
            return ConsultLLMForDecision(viableActions, currentState);
        }
        
        // Use traditional AI for routine decisions
        return base.SelectBestAction(currentState, viableActions);
    }
    
    private AIAction ConsultLLMForDecision(List<AIAction> actions, GameState state)
    {
        string prompt = BuildDecisionPrompt(actions, state);
        string llmResponse = LLMInterface.GetDecision(prompt);
        
        return ParseLLMDecision(llmResponse, actions);
    }
    
    private string BuildDecisionPrompt(List<AIAction> actions, GameState state)
    {
        return $@"
        You are an AI opponent in a turn-based strategy game with the following personality:
        - Archetype: {personality.archetype}
        - Aggression: {personality.aggression:F2}
        - Risk Tolerance: {personality.riskTolerance:F2}
        
        Current game state:
        - Turn: {state.turnNumber}
        - AI Resources: {state.aiResources}
        - Player Resources: {state.playerResources}
        - Game Phase: {state.currentPhase}
        
        Available actions:
        {string.Join("\n", actions.Select(a => $"- {a.actionName}: {a.description}"))}
        
        Choose the best action considering:
        1. Your personality traits
        2. Current strategic position
        3. Player's likely responses
        4. Long-term game plan
        
        Explain your reasoning and select one action.
        ";
    }
}
```

### Dynamic AI Personality Generation
```
Generate an AI opponent personality for a turn-based strategy game:

Game Context:
- Genre: [GAME_TYPE]
- Target Difficulty: [DIFFICULTY_LEVEL]
- Player Skill Level: [PLAYER_LEVEL]
- Game Length: [EXPECTED_DURATION]

Requirements:
- Create distinct behavioral patterns
- Balance challenge with fun
- Provide clear personality traits (0-1 scale)
- Include strategic preferences and weaknesses
- Suggest unique dialogue/flavor text

Format as Unity-compatible C# data structure.
```

### AI Behavior Analysis and Improvement
```csharp
public class AIBehaviorAnalyzer : MonoBehaviour
{
    public void AnalyzeAIPerformance()
    {
        string analysisPrompt = $@"
        Analyze this AI opponent's performance data:
        
        Games Played: {gameData.totalGames}
        Win Rate: {gameData.winRate:P2}
        Average Game Length: {gameData.averageLength} turns
        Player Satisfaction: {gameData.playerSatisfaction:F2}/5
        
        Decision Patterns:
        {GenerateDecisionPatternSummary()}
        
        Player Feedback:
        {GetPlayerFeedbackSummary()}
        
        Identify:
        1. Strengths in AI behavior
        2. Weaknesses and exploitable patterns
        3. Specific improvements for better gameplay
        4. Personality adjustments needed
        
        Provide concrete recommendations for AI improvements.
        ";
        
        string analysis = LLMInterface.AnalyzeData(analysisPrompt);
        ImplementAIImprovements(analysis);
    }
}
```

## 💡 Advanced AI Patterns

### Emergent Strategy AI
```csharp
public class EmergentStrategyAI : AIOpponent
{
    [System.Serializable]
    public class StrategyPattern
    {
        public string patternName;
        public List<ActionSequence> sequences;
        public float successRate;
        public int timesUsed;
        public float effectiveness;
    }
    
    [System.Serializable]
    public class ActionSequence
    {
        public List<AIAction> actions;
        public List<GameStateCondition> preconditions;
        public float confidence;
    }
    
    [SerializeField] private List<StrategyPattern> discoveredStrategies;
    [SerializeField] private StrategyLearningSystem learningSystem;
    
    public override AIAction SelectBestAction(GameState currentState, List<AIAction> availableActions)
    {
        // First, try to continue an existing strategy
        var continuationAction = TryContinueStrategy(currentState, availableActions);
        if (continuationAction != null)
        {
            return continuationAction;
        }
        
        // Look for opportunities to start new strategies
        var newStrategyAction = TryStartNewStrategy(currentState, availableActions);
        if (newStrategyAction != null)
        {
            return newStrategyAction;
        }
        
        // Fall back to basic action selection
        return base.SelectBestAction(currentState, availableActions);
    }
    
    private void DiscoverNewStrategies(GameResult gameResult)
    {
        if (gameResult.wasSuccessful)
        {
            var actionHistory = gameResult.aiActionHistory;
            var newPatterns = learningSystem.AnalyzeForPatterns(actionHistory);
            
            foreach (var pattern in newPatterns)
            {
                if (!PatternAlreadyKnown(pattern))
                {
                    discoveredStrategies.Add(pattern);
                    OnNewStrategyDiscovered?.Invoke(pattern);
                }
            }
        }
    }
    
    public UnityEvent<StrategyPattern> OnNewStrategyDiscovered;
}
```

### Meta-Learning AI System
```csharp
public class MetaLearningAI : AIOpponent
{
    [System.Serializable]
    public class OpponentModel
    {
        public string opponentId;
        public Dictionary<string, float> behaviorPatterns;
        public Dictionary<string, float> weaknesses;
        public List<string> exploitableStrategies;
        public float adaptationRate;
    }
    
    [SerializeField] private Dictionary<string, OpponentModel> opponentModels;
    [SerializeField] private string currentOpponentId;
    
    public override AIAction SelectBestAction(GameState currentState, List<AIAction> availableActions)
    {
        var opponentModel = GetOrCreateOpponentModel(currentOpponentId);
        var adaptedActions = AdaptActionsToOpponent(availableActions, opponentModel);
        
        return SelectOptimalAction(adaptedActions, currentState, opponentModel);
    }
    
    private List<AIAction> AdaptActionsToOpponent(List<AIAction> actions, OpponentModel model)
    {
        var adaptedActions = new List<AIAction>();
        
        foreach (var action in actions)
        {
            var adaptedAction = action.Clone();
            
            // Boost actions that exploit known weaknesses
            foreach (var weakness in model.weaknesses)
            {
                if (action.countersWeakness(weakness.Key))
                {
                    adaptedAction.utilityScore *= (1.0f + weakness.Value * 0.5f);
                }
            }
            
            // Adapt to opponent's behavioral patterns
            foreach (var pattern in model.behaviorPatterns)
            {
                if (action.respondsToPattern(pattern.Key))
                {
                    adaptedAction.utilityScore *= (1.0f + pattern.Value * 0.3f);
                }
            }
            
            adaptedActions.Add(adaptedAction);
        }
        
        return adaptedActions;
    }
    
    public void UpdateOpponentModel(string opponentId, GameResult result)
    {
        var model = GetOrCreateOpponentModel(opponentId);
        
        // Update behavior patterns based on observed actions
        foreach (var playerAction in result.playerActionHistory)
        {
            UpdateBehaviorPattern(model, playerAction);
        }
        
        // Update weaknesses based on what worked against this opponent
        foreach (var aiAction in result.aiActionHistory)
        {
            if (aiAction.wasEffective)
            {
                UpdateWeaknessModel(model, aiAction);
            }
        }
        
        opponentModels[opponentId] = model;
    }
}
```

---

*AI opponent design v1.0 | Intelligent challenge | Adaptive gameplay experience*