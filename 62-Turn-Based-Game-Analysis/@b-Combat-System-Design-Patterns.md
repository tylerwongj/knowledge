# @b-Combat-System-Design-Patterns - Turn-Based Combat Mechanics and Implementation

## 🎯 Learning Objectives
- Master various turn-based combat system architectures and patterns
- Understand initiative systems, action resolution, and damage calculation
- Implement flexible combat frameworks in Unity for different game types
- Analyze combat depth, balance, and player engagement strategies

## ⚔️ Core Combat System Patterns

### Initiative and Turn Order Systems
```csharp
public class InitiativeSystem : MonoBehaviour
{
    [System.Serializable]
    public class CombatEntity
    {
        public string entityName;
        public int baseInitiative;
        public int currentInitiative;
        public bool hasActedThisRound;
        public GameObject entityObject;
        
        public void RollInitiative(int diceSize = 20)
        {
            currentInitiative = baseInitiative + Random.Range(1, diceSize + 1);
        }
    }
    
    [SerializeField] private List<CombatEntity> combatants = new List<CombatEntity>();
    [SerializeField] private Queue<CombatEntity> turnQueue = new Queue<CombatEntity>();
    
    public void StartCombat()
    {
        // Roll initiative for all combatants
        foreach (var entity in combatants)
        {
            entity.RollInitiative();
            entity.hasActedThisRound = false;
        }
        
        // Sort by initiative (highest first)
        combatants.Sort((a, b) => b.currentInitiative.CompareTo(a.currentInitiative));
        
        // Build turn queue
        turnQueue.Clear();
        foreach (var entity in combatants)
        {
            turnQueue.Enqueue(entity);
        }
    }
    
    public CombatEntity GetNextCombatant()
    {
        if (turnQueue.Count == 0)
        {
            StartNewRound();
        }
        
        return turnQueue.Dequeue();
    }
    
    private void StartNewRound()
    {
        foreach (var entity in combatants)
        {
            entity.hasActedThisRound = false;
            turnQueue.Enqueue(entity);
        }
    }
}
```

### Action Point Systems
```csharp
public class ActionPointCombat : MonoBehaviour
{
    [System.Serializable]
    public class CombatAction
    {
        public string actionName;
        public int actionPointCost;
        public ActionType type;
        public int damage;
        public int accuracy;
        public List<StatusEffect> appliedEffects;
    }
    
    public enum ActionType
    {
        Attack,
        Defend,
        Move,
        Skill,
        Item
    }
    
    [SerializeField] private int maxActionPoints = 4;
    [SerializeField] private int currentActionPoints;
    
    public bool CanPerformAction(CombatAction action)
    {
        return currentActionPoints >= action.actionPointCost;
    }
    
    public void ExecuteAction(CombatAction action, CombatEntity target)
    {
        if (!CanPerformAction(action)) return;
        
        currentActionPoints -= action.actionPointCost;
        
        switch (action.type)
        {
            case ActionType.Attack:
                ProcessAttack(action, target);
                break;
            case ActionType.Defend:
                ProcessDefense(action);
                break;
            case ActionType.Move:
                ProcessMovement(action);
                break;
        }
    }
    
    private void ProcessAttack(CombatAction action, CombatEntity target)
    {
        int hitChance = Random.Range(1, 101);
        if (hitChance <= action.accuracy)
        {
            int finalDamage = CalculateDamage(action.damage, target);
            target.TakeDamage(finalDamage);
            ApplyStatusEffects(action.appliedEffects, target);
        }
    }
}
```

## 🎲 Damage and Resolution Systems

### Damage Calculation Patterns
```csharp
public class DamageCalculator : MonoBehaviour
{
    [System.Serializable]
    public class DamageFormula
    {
        public DamageType type;
        public float baseMultiplier = 1.0f;
        public float varianceRange = 0.1f; // ±10% variance
        public bool useRandomVariance = true;
    }
    
    public enum DamageType
    {
        Physical,
        Magical,
        True, // Ignores all defenses
        Percentage // Based on target's max health
    }
    
    public int CalculateDamage(int baseDamage, CombatEntity attacker, CombatEntity defender, DamageType damageType)
    {
        float damage = baseDamage;
        
        // Apply attacker stats
        switch (damageType)
        {
            case DamageType.Physical:
                damage *= (1.0f + attacker.physicalPower / 100.0f);
                damage *= (1.0f - defender.physicalDefense / 100.0f);
                break;
            case DamageType.Magical:
                damage *= (1.0f + attacker.magicalPower / 100.0f);
                damage *= (1.0f - defender.magicalDefense / 100.0f);
                break;
            case DamageType.Percentage:
                damage = defender.maxHealth * (baseDamage / 100.0f);
                break;
        }
        
        // Apply variance for less predictable combat
        if (useRandomVariance && damageType != DamageType.True)
        {
            float variance = Random.Range(-varianceRange, varianceRange);
            damage *= (1.0f + variance);
        }
        
        return Mathf.Max(1, Mathf.RoundToInt(damage)); // Minimum 1 damage
    }
}
```

### Status Effect System
```csharp
public abstract class StatusEffect : ScriptableObject
{
    public string effectName;
    public string description;
    public Sprite icon;
    public int duration;
    public bool stackable;
    public int maxStacks = 1;
    
    public abstract void OnApply(CombatEntity target);
    public abstract void OnTick(CombatEntity target);
    public abstract void OnRemove(CombatEntity target);
}

[CreateAssetMenu(fileName = "New Poison Effect", menuName = "Combat/Status Effects/Poison")]
public class PoisonEffect : StatusEffect
{
    [SerializeField] private int damagePerTurn;
    
    public override void OnApply(CombatEntity target)
    {
        Debug.Log($"{target.name} is poisoned!");
    }
    
    public override void OnTick(CombatEntity target)
    {
        target.TakeDamage(damagePerTurn);
        duration--;
    }
    
    public override void OnRemove(CombatEntity target)
    {
        Debug.Log($"{target.name} recovers from poison.");
    }
}

public class StatusEffectManager : MonoBehaviour
{
    [SerializeField] private List<StatusEffect> activeEffects = new List<StatusEffect>();
    
    public void ApplyStatusEffect(StatusEffect effect)
    {
        if (effect.stackable)
        {
            var existingEffect = activeEffects.Find(e => e.effectName == effect.effectName);
            if (existingEffect != null && existingEffect.maxStacks > 1)
            {
                // Handle stacking logic
                return;
            }
        }
        
        var newEffect = Instantiate(effect);
        newEffect.OnApply(GetComponent<CombatEntity>());
        activeEffects.Add(newEffect);
    }
    
    public void ProcessStatusEffects()
    {
        for (int i = activeEffects.Count - 1; i >= 0; i--)
        {
            var effect = activeEffects[i];
            effect.OnTick(GetComponent<CombatEntity>());
            
            if (effect.duration <= 0)
            {
                effect.OnRemove(GetComponent<CombatEntity>());
                activeEffects.RemoveAt(i);
            }
        }
    }
}
```

## 🛡️ Defense and Mitigation Systems

### Armor and Resistance Types
```csharp
public class DefenseSystem : MonoBehaviour
{
    [System.Serializable]
    public class DefenseStats
    {
        [Header("Physical Defense")]
        public int armor; // Flat damage reduction
        public float physicalResistance; // Percentage reduction
        
        [Header("Magical Defense")]
        public int magicResistance; // Flat magic damage reduction
        public float spellResistance; // Percentage reduction
        
        [Header("Special Defenses")]
        public float criticalResistance; // Reduce critical hit chance
        public float statusResistance; // Resist debuffs
        public List<DamageType> immunities; // Complete immunity to damage types
    }
    
    [SerializeField] private DefenseStats baseDefense;
    [SerializeField] private DefenseStats currentDefense;
    
    public int ApplyDefenses(int incomingDamage, DamageType damageType, bool isCritical = false)
    {
        // Check for immunity
        if (currentDefense.immunities.Contains(damageType))
        {
            return 0;
        }
        
        float damage = incomingDamage;
        
        // Apply flat reduction first
        switch (damageType)
        {
            case DamageType.Physical:
                damage = Mathf.Max(0, damage - currentDefense.armor);
                damage *= (1.0f - currentDefense.physicalResistance);
                break;
            case DamageType.Magical:
                damage = Mathf.Max(0, damage - currentDefense.magicResistance);
                damage *= (1.0f - currentDefense.spellResistance);
                break;
        }
        
        // Critical hit resistance
        if (isCritical)
        {
            damage *= (1.0f - currentDefense.criticalResistance);
        }
        
        return Mathf.RoundToInt(damage);
    }
}
```

### Cover and Positioning Systems
```csharp
public class CoverSystem : MonoBehaviour
{
    public enum CoverType
    {
        None,
        Light,  // 25% damage reduction
        Heavy,  // 50% damage reduction
        Total   // Line of sight blocked
    }
    
    [SerializeField] private LayerMask coverMask;
    
    public CoverType GetCoverBetween(Vector3 attacker, Vector3 target)
    {
        Vector3 direction = target - attacker;
        float distance = direction.magnitude;
        
        RaycastHit[] hits = Physics.RaycastAll(attacker, direction.normalized, distance, coverMask);
        
        CoverType bestCover = CoverType.None;
        
        foreach (var hit in hits)
        {
            var coverObject = hit.collider.GetComponent<CoverObject>();
            if (coverObject != null)
            {
                if (coverObject.coverType > bestCover)
                {
                    bestCover = coverObject.coverType;
                }
            }
        }
        
        return bestCover;
    }
    
    public float GetCoverModifier(CoverType coverType)
    {
        switch (coverType)
        {
            case CoverType.Light: return 0.75f;
            case CoverType.Heavy: return 0.5f;
            case CoverType.Total: return 0.0f;
            default: return 1.0f;
        }
    }
}
```

## 🎯 Targeting and Range Systems

### Grid-Based Combat
```csharp
public class GridCombatSystem : MonoBehaviour
{
    [System.Serializable]
    public class GridPosition
    {
        public int x, y;
        public bool isOccupied;
        public CombatEntity occupant;
        public TerrainType terrain;
        
        public float GetDistanceTo(GridPosition other)
        {
            return Mathf.Abs(x - other.x) + Mathf.Abs(y - other.y); // Manhattan distance
        }
    }
    
    [SerializeField] private GridPosition[,] combatGrid;
    [SerializeField] private int gridWidth = 10;
    [SerializeField] private int gridHeight = 10;
    
    public List<GridPosition> GetValidTargets(GridPosition origin, int range, TargetType targetType)
    {
        List<GridPosition> validTargets = new List<GridPosition>();
        
        for (int x = 0; x < gridWidth; x++)
        {
            for (int y = 0; y < gridHeight; y++)
            {
                GridPosition current = combatGrid[x, y];
                
                if (current.GetDistanceTo(origin) <= range)
                {
                    if (IsValidTarget(current, targetType))
                    {
                        validTargets.Add(current);
                    }
                }
            }
        }
        
        return validTargets;
    }
    
    private bool IsValidTarget(GridPosition position, TargetType targetType)
    {
        switch (targetType)
        {
            case TargetType.Enemy:
                return position.isOccupied && position.occupant.IsEnemy();
            case TargetType.Ally:
                return position.isOccupied && position.occupant.IsAlly();
            case TargetType.Empty:
                return !position.isOccupied;
            case TargetType.Any:
                return true;
            default:
                return false;
        }
    }
}
```

### Area of Effect Systems
```csharp
public class AOESystem : MonoBehaviour
{
    public enum AOEShape
    {
        Circle,
        Square,
        Line,
        Cone,
        Cross
    }
    
    [System.Serializable]
    public class AOEPattern
    {
        public AOEShape shape;
        public int size;
        public bool affectsAllies;
        public bool affectsEnemies;
        public bool requiresLineOfSight;
    }
    
    public List<CombatEntity> GetAOETargets(Vector3 center, AOEPattern pattern)
    {
        List<CombatEntity> targets = new List<CombatEntity>();
        Collider[] colliders = Physics.OverlapSphere(center, pattern.size);
        
        foreach (var collider in colliders)
        {
            var entity = collider.GetComponent<CombatEntity>();
            if (entity != null)
            {
                if (IsInAOEShape(center, entity.transform.position, pattern) &&
                    IsValidAOETarget(entity, pattern))
                {
                    if (!pattern.requiresLineOfSight || 
                        HasLineOfSight(center, entity.transform.position))
                    {
                        targets.Add(entity);
                    }
                }
            }
        }
        
        return targets;
    }
    
    private bool IsInAOEShape(Vector3 center, Vector3 target, AOEPattern pattern)
    {
        Vector3 direction = target - center;
        float distance = direction.magnitude;
        
        switch (pattern.shape)
        {
            case AOEShape.Circle:
                return distance <= pattern.size;
            case AOEShape.Square:
                return Mathf.Abs(direction.x) <= pattern.size && 
                       Mathf.Abs(direction.z) <= pattern.size;
            case AOEShape.Line:
                return Mathf.Abs(Vector3.Cross(direction.normalized, Vector3.forward).magnitude) <= 1.0f &&
                       distance <= pattern.size;
            default:
                return false;
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Combat Balance Analysis
```
Analyze this turn-based combat system for balance issues:

Combat Entity Stats:
- Health: [VALUE]
- Attack: [VALUE] 
- Defense: [VALUE]
- Speed: [VALUE]

Available Actions:
- [ACTION_LIST]

Status Effects:
- [EFFECT_LIST]

Identify potential dominant strategies, underpowered options, and recommend specific numerical adjustments for better balance.
```

### AI Opponent Development
```csharp
public class AIDecisionSystem : MonoBehaviour
{
    [System.Serializable]
    public class DecisionWeight
    {
        public ActionType actionType;
        public float baseWeight;
        public AnimationCurve situationalModifier;
    }
    
    public CombatAction SelectBestAction(List<CombatAction> availableActions, GameState currentState)
    {
        // Use LLM integration to analyze current game state
        // and suggest optimal action based on game context
        string gameStateAnalysis = AnalyzeGameState(currentState);
        string recommendedAction = LLMInterface.GetActionRecommendation(gameStateAnalysis);
        
        return ParseActionFromRecommendation(recommendedAction, availableActions);
    }
}
```

### Content Generation Prompts
```
Generate 5 unique status effects for a fantasy turn-based combat system:

Requirements:
- Each effect should have clear mechanical impact
- Provide duration, stack behavior, and removal conditions
- Include both beneficial and detrimental effects
- Consider counterplay and strategic depth
- Format as C# ScriptableObject data

Focus on effects that create interesting tactical decisions.
```

## 💡 Advanced Combat Patterns

### Combo and Chain Systems
```csharp
public class ComboSystem : MonoBehaviour
{
    [System.Serializable]
    public class ComboChain
    {
        public List<ActionType> requiredSequence;
        public CombatAction finisherAction;
        public float timeWindow = 3.0f;
    }
    
    [SerializeField] private List<ComboChain> availableCombos;
    [SerializeField] private List<ActionType> currentSequence = new List<ActionType>();
    [SerializeField] private float lastActionTime;
    
    public bool TryExecuteCombo(ActionType newAction)
    {
        // Check if action continues a valid combo
        if (Time.time - lastActionTime > GetMaxComboWindow())
        {
            currentSequence.Clear();
        }
        
        currentSequence.Add(newAction);
        lastActionTime = Time.time;
        
        // Check for completed combos
        foreach (var combo in availableCombos)
        {
            if (SequenceMatches(currentSequence, combo.requiredSequence))
            {
                ExecuteComboFinisher(combo);
                currentSequence.Clear();
                return true;
            }
        }
        
        return false;
    }
}
```

### Resource Management Combat
```csharp
public class ResourceCombatSystem : MonoBehaviour
{
    [System.Serializable]
    public class ResourcePool
    {
        public string resourceName;
        public int currentAmount;
        public int maxAmount;
        public int regenPerTurn;
        public Color resourceColor;
        
        public bool CanSpend(int amount) => currentAmount >= amount;
        
        public void Spend(int amount)
        {
            currentAmount = Mathf.Max(0, currentAmount - amount);
        }
        
        public void Regenerate()
        {
            currentAmount = Mathf.Min(maxAmount, currentAmount + regenPerTurn);
        }
    }
    
    [SerializeField] private ResourcePool mana;
    [SerializeField] private ResourcePool stamina;
    [SerializeField] private ResourcePool focus;
    
    public bool CanAffordAction(CombatAction action)
    {
        return mana.CanSpend(action.manaCost) &&
               stamina.CanSpend(action.staminaCost) &&
               focus.CanSpend(action.focusCost);
    }
}
```

## 🎮 Unity Implementation Patterns

### Event-Driven Combat
```csharp
public static class CombatEvents
{
    public static UnityEvent<CombatEntity, int> OnDamageDealt = new UnityEvent<CombatEntity, int>();
    public static UnityEvent<CombatEntity> OnEntityDefeated = new UnityEvent<CombatEntity>();
    public static UnityEvent<CombatAction> OnActionExecuted = new UnityEvent<CombatAction>();
    public static UnityEvent OnCombatEnded = new UnityEvent();
}

public class CombatEventHandler : MonoBehaviour
{
    private void OnEnable()
    {
        CombatEvents.OnDamageDealt.AddListener(HandleDamageDealt);
        CombatEvents.OnEntityDefeated.AddListener(HandleEntityDefeated);
    }
    
    private void OnDisable()
    {
        CombatEvents.OnDamageDealt.RemoveListener(HandleDamageDealt);
        CombatEvents.OnEntityDefeated.RemoveListener(HandleEntityDefeated);
    }
    
    private void HandleDamageDealt(CombatEntity target, int damage)
    {
        // Trigger damage animations, sound effects, UI updates
        FloatingTextManager.Instance.ShowDamage(target.transform.position, damage);
    }
}
```

### Combat Animation Integration
```csharp
public class CombatAnimationController : MonoBehaviour
{
    [SerializeField] private Animator combatAnimator;
    [SerializeField] private float animationTimeoutDuration = 3.0f;
    
    public IEnumerator PlayCombatAnimation(string animationName, CombatEntity target = null)
    {
        combatAnimator.SetTrigger(animationName);
        
        float timer = 0f;
        while (timer < animationTimeoutDuration)
        {
            AnimatorStateInfo stateInfo = combatAnimator.GetCurrentAnimatorStateInfo(0);
            
            if (stateInfo.IsName(animationName) && stateInfo.normalizedTime >= 1.0f)
            {
                break;
            }
            
            timer += Time.deltaTime;
            yield return null;
        }
        
        // Animation complete, trigger any follow-up effects
        OnAnimationComplete?.Invoke();
    }
    
    public UnityEvent OnAnimationComplete;
}
```

---

*Combat system patterns v1.0 | Turn-based tactical depth | Unity-optimized implementation*