# @c-Resource-Management-Systems - Economic and Resource Flow Design in Turn-Based Games

## 🎯 Learning Objectives
- Master resource management mechanics for strategic depth and player engagement
- Implement scalable resource systems in Unity with clean architecture patterns
- Understand resource scarcity, abundance, and conversion mechanics
- Design meaningful economic choices that drive player decision-making

## 💰 Core Resource System Types

### Basic Resource Categories
```csharp
public enum ResourceType
{
    // Primary Resources
    Currency,           // Gold, credits, coins
    Energy,            // Mana, stamina, action points
    Materials,         // Wood, stone, metal
    Food,              // Population support, health
    
    // Secondary Resources
    Influence,         // Political power, reputation
    Knowledge,         // Research points, experience
    Time,              // Turns, deadlines, aging
    Space,             // Territory, inventory slots
    
    // Special Resources
    Unique,            // Rare items, artifacts
    Renewable,         // Resources that regenerate
    Consumable,        // One-time use items
    Convertible        // Resources that transform
}

[System.Serializable]
public class Resource
{
    public ResourceType type;
    public string displayName;
    public string description;
    public Sprite icon;
    public Color resourceColor;
    
    [Header("Mechanics")]
    public int currentAmount;
    public int maxCapacity = -1; // -1 for unlimited
    public int regenerationRate;
    public bool canOverflow;
    public float conversionRate = 1.0f;
    
    [Header("UI")]
    public bool showInMainUI;
    public int displayPriority;
}
```

### Resource Pool Manager
```csharp
public class ResourceManager : MonoBehaviour
{
    [SerializeField] private List<Resource> resources = new List<Resource>();
    [SerializeField] private Dictionary<ResourceType, Resource> resourceLookup;
    
    public UnityEvent<ResourceType, int, int> OnResourceChanged; // type, old, new
    public UnityEvent<ResourceType> OnResourceDepleted;
    public UnityEvent<ResourceType> OnResourceMaxed;
    
    private void Awake()
    {
        InitializeResourceLookup();
    }
    
    private void InitializeResourceLookup()
    {
        resourceLookup = new Dictionary<ResourceType, Resource>();
        foreach (var resource in resources)
        {
            resourceLookup[resource.type] = resource;
        }
    }
    
    public bool CanAfford(ResourceType type, int amount)
    {
        return GetResourceAmount(type) >= amount;
    }
    
    public bool CanAfford(Dictionary<ResourceType, int> cost)
    {
        foreach (var kvp in cost)
        {
            if (!CanAfford(kvp.Key, kvp.Value))
                return false;
        }
        return true;
    }
    
    public void SpendResources(Dictionary<ResourceType, int> cost)
    {
        if (!CanAfford(cost)) return;
        
        foreach (var kvp in cost)
        {
            ModifyResource(kvp.Key, -kvp.Value);
        }
    }
    
    public void ModifyResource(ResourceType type, int amount)
    {
        if (!resourceLookup.ContainsKey(type)) return;
        
        var resource = resourceLookup[type];
        int oldAmount = resource.currentAmount;
        
        resource.currentAmount += amount;
        
        // Handle capacity limits
        if (resource.maxCapacity > 0)
        {
            if (resource.canOverflow)
            {
                // Allow temporary overflow but mark for special handling
                if (resource.currentAmount > resource.maxCapacity)
                {
                    StartCoroutine(HandleResourceOverflow(type));
                }
            }
            else
            {
                resource.currentAmount = Mathf.Clamp(resource.currentAmount, 0, resource.maxCapacity);
            }
        }
        else
        {
            resource.currentAmount = Mathf.Max(0, resource.currentAmount);
        }
        
        // Trigger events
        OnResourceChanged?.Invoke(type, oldAmount, resource.currentAmount);
        
        if (resource.currentAmount <= 0 && oldAmount > 0)
        {
            OnResourceDepleted?.Invoke(type);
        }
        
        if (resource.maxCapacity > 0 && resource.currentAmount >= resource.maxCapacity && oldAmount < resource.maxCapacity)
        {
            OnResourceMaxed?.Invoke(type);
        }
    }
    
    private IEnumerator HandleResourceOverflow(ResourceType type)
    {
        yield return new WaitForSeconds(1.0f);
        // Gradually reduce overflow or apply penalties
        var resource = resourceLookup[type];
        if (resource.currentAmount > resource.maxCapacity)
        {
            int overflow = resource.currentAmount - resource.maxCapacity;
            ModifyResource(type, -overflow);
        }
    }
}
```

## 🔄 Resource Flow and Conversion Systems

### Production and Consumption Chains
```csharp
[System.Serializable]
public class ProductionChain
{
    [Header("Input Requirements")]
    public List<ResourceCost> inputCosts;
    
    [Header("Output Production")]
    public List<ResourceReward> outputs;
    
    [Header("Production Settings")]
    public float productionTime = 1.0f;
    public int maxProductionQueue = 5;
    public bool requiresWorker = false;
    public BuildingType requiredBuilding;
    
    [Header("Efficiency Modifiers")]
    public float baseEfficiency = 1.0f;
    public List<EfficiencyModifier> modifiers;
}

[System.Serializable]
public class ResourceCost
{
    public ResourceType resourceType;
    public int amount;
    public bool isPerTurn;
}

[System.Serializable]
public class ResourceReward
{
    public ResourceType resourceType;
    public int baseAmount;
    public float variancePercentage = 0.1f;
    
    public int GetActualAmount()
    {
        float variance = Random.Range(-variancePercentage, variancePercentage);
        return Mathf.RoundToInt(baseAmount * (1.0f + variance));
    }
}

public class ProductionManager : MonoBehaviour
{
    [SerializeField] private List<ProductionChain> activeProduction;
    [SerializeField] private ResourceManager resourceManager;
    
    public void StartProduction(ProductionChain chain)
    {
        if (resourceManager.CanAfford(ConvertCostsToDict(chain.inputCosts)))
        {
            StartCoroutine(ProcessProduction(chain));
        }
    }
    
    private IEnumerator ProcessProduction(ProductionChain chain)
    {
        // Consume input resources
        resourceManager.SpendResources(ConvertCostsToDict(chain.inputCosts));
        
        // Wait for production time
        yield return new WaitForSeconds(chain.productionTime);
        
        // Generate outputs
        foreach (var output in chain.outputs)
        {
            int producedAmount = output.GetActualAmount();
            producedAmount = Mathf.RoundToInt(producedAmount * chain.baseEfficiency);
            resourceManager.ModifyResource(output.resourceType, producedAmount);
        }
    }
    
    private Dictionary<ResourceType, int> ConvertCostsToDict(List<ResourceCost> costs)
    {
        var dict = new Dictionary<ResourceType, int>();
        foreach (var cost in costs)
        {
            dict[cost.resourceType] = cost.amount;
        }
        return dict;
    }
}
```

### Trading and Exchange Systems
```csharp
public class TradingSystem : MonoBehaviour
{
    [System.Serializable]
    public class TradeOffer
    {
        public string offerName;
        public List<ResourceCost> requiredResources;
        public List<ResourceReward> offeredResources;
        public bool isLimitedTime;
        public float timeLimit;
        public int maxUses = -1; // -1 for unlimited
        public int currentUses = 0;
    }
    
    [System.Serializable]
    public class MarketFluctuation
    {
        public ResourceType resourceType;
        public float demandMultiplier = 1.0f;
        public float supplyMultiplier = 1.0f;
        public AnimationCurve priceFluctuationCurve;
    }
    
    [SerializeField] private List<TradeOffer> availableTrades;
    [SerializeField] private List<MarketFluctuation> marketConditions;
    [SerializeField] private ResourceManager resourceManager;
    
    public bool ExecuteTrade(TradeOffer offer)
    {
        if (!CanExecuteTrade(offer)) return false;
        
        // Apply market fluctuations to trade
        var adjustedOffer = ApplyMarketConditions(offer);
        
        // Execute the trade
        resourceManager.SpendResources(ConvertCostsToDict(adjustedOffer.requiredResources));
        
        foreach (var reward in adjustedOffer.offeredResources)
        {
            resourceManager.ModifyResource(reward.resourceType, reward.GetActualAmount());
        }
        
        offer.currentUses++;
        return true;
    }
    
    private bool CanExecuteTrade(TradeOffer offer)
    {
        if (offer.maxUses > 0 && offer.currentUses >= offer.maxUses)
            return false;
            
        return resourceManager.CanAfford(ConvertCostsToDict(offer.requiredResources));
    }
    
    private TradeOffer ApplyMarketConditions(TradeOffer baseOffer)
    {
        var adjustedOffer = JsonUtility.FromJson<TradeOffer>(JsonUtility.ToJson(baseOffer));
        
        foreach (var condition in marketConditions)
        {
            // Adjust costs and rewards based on market conditions
            foreach (var cost in adjustedOffer.requiredResources)
            {
                if (cost.resourceType == condition.resourceType)
                {
                    cost.amount = Mathf.RoundToInt(cost.amount * condition.demandMultiplier);
                }
            }
            
            foreach (var reward in adjustedOffer.offeredResources)
            {
                if (reward.resourceType == condition.resourceType)
                {
                    reward.baseAmount = Mathf.RoundToInt(reward.baseAmount * condition.supplyMultiplier);
                }
            }
        }
        
        return adjustedOffer;
    }
}
```

## ⚡ Energy and Action Point Systems

### Action Point Management
```csharp
public class ActionPointSystem : MonoBehaviour
{
    [System.Serializable]
    public class ActionPointPool
    {
        public string poolName;
        public int maxPoints;
        public int currentPoints;
        public int regenerationPerTurn;
        public bool carryOverUnused;
        public int carryOverLimit;
        public Color poolColor;
    }
    
    [SerializeField] private List<ActionPointPool> actionPools;
    [SerializeField] private Dictionary<string, ActionPointPool> poolLookup;
    
    public UnityEvent<string, int, int> OnActionPointsChanged;
    public UnityEvent<string> OnActionPoolDepleted;
    
    private void Awake()
    {
        InitializePoolLookup();
    }
    
    public bool CanAffordAction(string poolName, int cost)
    {
        if (!poolLookup.ContainsKey(poolName)) return false;
        return poolLookup[poolName].currentPoints >= cost;
    }
    
    public void SpendActionPoints(string poolName, int amount)
    {
        if (!poolLookup.ContainsKey(poolName)) return;
        
        var pool = poolLookup[poolName];
        int oldPoints = pool.currentPoints;
        pool.currentPoints = Mathf.Max(0, pool.currentPoints - amount);
        
        OnActionPointsChanged?.Invoke(poolName, oldPoints, pool.currentPoints);
        
        if (pool.currentPoints <= 0 && oldPoints > 0)
        {
            OnActionPoolDepleted?.Invoke(poolName);
        }
    }
    
    public void RegenerateActionPoints()
    {
        foreach (var pool in actionPools)
        {
            int oldPoints = pool.currentPoints;
            int newPoints = pool.currentPoints + pool.regenerationPerTurn;
            
            if (pool.carryOverUnused)
            {
                newPoints = Mathf.Min(newPoints, pool.maxPoints + pool.carryOverLimit);
            }
            else
            {
                newPoints = Mathf.Min(newPoints, pool.maxPoints);
            }
            
            pool.currentPoints = newPoints;
            
            if (newPoints != oldPoints)
            {
                OnActionPointsChanged?.Invoke(pool.poolName, oldPoints, newPoints);
            }
        }
    }
    
    private void InitializePoolLookup()
    {
        poolLookup = new Dictionary<string, ActionPointPool>();
        foreach (var pool in actionPools)
        {
            poolLookup[pool.poolName] = pool;
        }
    }
}
```

### Dynamic Resource Generation
```csharp
public class DynamicResourceGenerator : MonoBehaviour
{
    [System.Serializable]
    public class ResourceGenerator
    {
        public ResourceType generatedResource;
        public int baseGenerationRate;
        public List<GenerationModifier> modifiers;
        public bool isActive = true;
    }
    
    [System.Serializable]
    public class GenerationModifier
    {
        public string modifierName;
        public float multiplier = 1.0f;
        public int flatBonus = 0;
        public bool isTemporary;
        public float duration;
        public float remainingTime;
    }
    
    [SerializeField] private List<ResourceGenerator> generators;
    [SerializeField] private ResourceManager resourceManager;
    
    public void ProcessGeneration()
    {
        foreach (var generator in generators)
        {
            if (!generator.isActive) continue;
            
            int totalGeneration = CalculateGeneration(generator);
            resourceManager.ModifyResource(generator.generatedResource, totalGeneration);
            
            UpdateModifiers(generator);
        }
    }
    
    private int CalculateGeneration(ResourceGenerator generator)
    {
        float total = generator.baseGenerationRate;
        float multiplier = 1.0f;
        int flatBonus = 0;
        
        foreach (var modifier in generator.modifiers)
        {
            multiplier *= modifier.multiplier;
            flatBonus += modifier.flatBonus;
        }
        
        return Mathf.RoundToInt(total * multiplier) + flatBonus;
    }
    
    private void UpdateModifiers(ResourceGenerator generator)
    {
        for (int i = generator.modifiers.Count - 1; i >= 0; i--)
        {
            var modifier = generator.modifiers[i];
            if (modifier.isTemporary)
            {
                modifier.remainingTime -= Time.deltaTime;
                if (modifier.remainingTime <= 0)
                {
                    generator.modifiers.RemoveAt(i);
                }
            }
        }
    }
    
    public void AddTemporaryModifier(ResourceType resourceType, GenerationModifier modifier)
    {
        var generator = generators.Find(g => g.generatedResource == resourceType);
        if (generator != null)
        {
            modifier.remainingTime = modifier.duration;
            generator.modifiers.Add(modifier);
        }
    }
}
```

## 🏗️ Infrastructure and Building Systems

### Building Resource Management
```csharp
public class BuildingSystem : MonoBehaviour
{
    [System.Serializable]
    public class Building
    {
        public string buildingName;
        public BuildingType type;
        public List<ResourceCost> constructionCost;
        public List<ResourceCost> maintenanceCost;
        public List<ResourceReward> production;
        public int maxWorkers;
        public int currentWorkers;
        public float efficiencyRating = 1.0f;
        public bool isConstructed;
        public bool isActive;
    }
    
    public enum BuildingType
    {
        ResourceProduction,
        Processing,
        Storage,
        Military,
        Residential,
        Research,
        Special
    }
    
    [SerializeField] private List<Building> buildings;
    [SerializeField] private ResourceManager resourceManager;
    [SerializeField] private int maxBuildings = 10;
    
    public bool CanConstruct(Building buildingPrefab)
    {
        if (buildings.Count >= maxBuildings) return false;
        return resourceManager.CanAfford(ConvertCostsToDict(buildingPrefab.constructionCost));
    }
    
    public void ConstructBuilding(Building buildingPrefab)
    {
        if (!CanConstruct(buildingPrefab)) return;
        
        resourceManager.SpendResources(ConvertCostsToDict(buildingPrefab.constructionCost));
        
        var newBuilding = JsonUtility.FromJson<Building>(JsonUtility.ToJson(buildingPrefab));
        newBuilding.isConstructed = true;
        newBuilding.isActive = true;
        buildings.Add(newBuilding);
    }
    
    public void ProcessBuildingMaintenance()
    {
        foreach (var building in buildings)
        {
            if (!building.isActive) continue;
            
            // Check if can afford maintenance
            if (resourceManager.CanAfford(ConvertCostsToDict(building.maintenanceCost)))
            {
                resourceManager.SpendResources(ConvertCostsToDict(building.maintenanceCost));
                ProcessBuildingProduction(building);
            }
            else
            {
                // Building becomes inactive due to lack of maintenance
                building.isActive = false;
                building.efficiencyRating *= 0.9f; // Gradual degradation
            }
        }
    }
    
    private void ProcessBuildingProduction(Building building)
    {
        float workerEfficiency = (float)building.currentWorkers / building.maxWorkers;
        float totalEfficiency = building.efficiencyRating * workerEfficiency;
        
        foreach (var production in building.production)
        {
            int producedAmount = Mathf.RoundToInt(production.GetActualAmount() * totalEfficiency);
            resourceManager.ModifyResource(production.resourceType, producedAmount);
        }
    }
    
    private Dictionary<ResourceType, int> ConvertCostsToDict(List<ResourceCost> costs)
    {
        var dict = new Dictionary<ResourceType, int>();
        foreach (var cost in costs)
        {
            dict[cost.resourceType] = cost.amount;
        }
        return dict;
    }
}
```

## 📊 Resource Scarcity and Pressure Systems

### Scarcity Mechanics
```csharp
public class ScarcityManager : MonoBehaviour
{
    [System.Serializable]
    public class ScarcityCondition
    {
        public ResourceType resourceType;
        public int criticalThreshold;
        public int warningThreshold;
        public List<ScarcityEffect> effects;
        public bool isActive;
    }
    
    [System.Serializable]
    public class ScarcityEffect
    {
        public EffectType type;
        public float magnitude;
        public string description;
    }
    
    public enum EffectType
    {
        ProductionPenalty,
        MaintenanceIncrease,
        PopulationUnrest,
        BuildingShutdown,
        TradeDisruption
    }
    
    [SerializeField] private List<ScarcityCondition> scarcityConditions;
    [SerializeField] private ResourceManager resourceManager;
    
    public UnityEvent<ResourceType, ScarcityLevel> OnScarcityLevelChanged;
    
    public enum ScarcityLevel
    {
        Abundant,
        Normal,
        Warning,
        Critical,
        Depleted
    }
    
    public void CheckScarcityConditions()
    {
        foreach (var condition in scarcityConditions)
        {
            int currentAmount = resourceManager.GetResourceAmount(condition.resourceType);
            ScarcityLevel newLevel = GetScarcityLevel(currentAmount, condition);
            
            if (newLevel != GetCurrentScarcityLevel(condition.resourceType))
            {
                OnScarcityLevelChanged?.Invoke(condition.resourceType, newLevel);
                ApplyScarcityEffects(condition, newLevel);
            }
        }
    }
    
    private ScarcityLevel GetScarcityLevel(int amount, ScarcityCondition condition)
    {
        if (amount <= 0) return ScarcityLevel.Depleted;
        if (amount <= condition.criticalThreshold) return ScarcityLevel.Critical;
        if (amount <= condition.warningThreshold) return ScarcityLevel.Warning;
        return ScarcityLevel.Normal;
    }
    
    private void ApplyScarcityEffects(ScarcityCondition condition, ScarcityLevel level)
    {
        foreach (var effect in condition.effects)
        {
            switch (effect.type)
            {
                case EffectType.ProductionPenalty:
                    ApplyProductionPenalty(condition.resourceType, effect.magnitude, level);
                    break;
                case EffectType.PopulationUnrest:
                    TriggerPopulationUnrest(effect.magnitude, level);
                    break;
            }
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Economic Balance Analysis
```
Analyze this resource economy for balance issues:

Resources:
- [LIST_OF_RESOURCES]

Production Chains:
- [PRODUCTION_CHAINS]

Costs and Rewards:
- [COST_REWARD_RATIOS]

Identify potential economic exploits, resource bottlenecks, and recommend adjustments for balanced gameplay progression.
```

### Dynamic Economy Generation
```csharp
public class AIEconomyGenerator : MonoBehaviour
{
    public void GenerateBalancedEconomy(int playerCount, DifficultyLevel difficulty)
    {
        string economyPrompt = $@"
        Generate a balanced resource economy for a {playerCount}-player turn-based strategy game.
        
        Difficulty: {difficulty}
        
        Requirements:
        - 4-6 primary resources
        - 2-3 secondary resources
        - Production chains with meaningful choices
        - Scarcity pressure without frustration
        - Multiple viable strategies
        
        Format as JSON with resource definitions, production chains, and balance rationale.
        ";
        
        // Integration with LLM API to generate economy
        string economyJSON = LLMInterface.GenerateContent(economyPrompt);
        ImplementGeneratedEconomy(economyJSON);
    }
}
```

### Resource Optimization Advisor
```
Given current resource state:
- [CURRENT_RESOURCES]
- [AVAILABLE_ACTIONS]
- [GAME_OBJECTIVES]

Recommend optimal resource allocation strategy considering:
1. Short-term survival needs
2. Long-term growth potential  
3. Risk mitigation
4. Opportunity costs

Provide 3 alternative strategies with trade-offs explained.
```

## 💡 Advanced Resource Patterns

### Seasonal Resource Cycles
```csharp
public class SeasonalResourceSystem : MonoBehaviour
{
    [System.Serializable]
    public class Season
    {
        public string seasonName;
        public float duration;
        public List<ResourceModifier> resourceModifiers;
        public List<SpecialEvent> possibleEvents;
    }
    
    [SerializeField] private List<Season> seasons;
    [SerializeField] private int currentSeasonIndex;
    [SerializeField] private float seasonProgress;
    
    public void UpdateSeason()
    {
        seasonProgress += Time.deltaTime;
        
        if (seasonProgress >= seasons[currentSeasonIndex].duration)
        {
            AdvanceToNextSeason();
        }
        
        ApplySeasonalModifiers();
    }
    
    private void AdvanceToNextSeason()
    {
        currentSeasonIndex = (currentSeasonIndex + 1) % seasons.Count;
        seasonProgress = 0f;
        
        OnSeasonChanged?.Invoke(seasons[currentSeasonIndex]);
    }
    
    public UnityEvent<Season> OnSeasonChanged;
}
```

### Resource Decay and Spoilage
```csharp
public class ResourceDecaySystem : MonoBehaviour
{
    [System.Serializable]
    public class DecayableResource
    {
        public ResourceType resourceType;
        public float decayRate; // Percentage per turn
        public int minimumAmount; // Amount that never decays
        public bool canSpoilCompletely;
    }
    
    [SerializeField] private List<DecayableResource> decayableResources;
    [SerializeField] private ResourceManager resourceManager;
    
    public void ProcessResourceDecay()
    {
        foreach (var decayResource in decayableResources)
        {
            int currentAmount = resourceManager.GetResourceAmount(decayResource.resourceType);
            int decayableAmount = Mathf.Max(0, currentAmount - decayResource.minimumAmount);
            
            if (decayableAmount > 0)
            {
                int decayAmount = Mathf.RoundToInt(decayableAmount * decayResource.decayRate);
                resourceManager.ModifyResource(decayResource.resourceType, -decayAmount);
            }
        }
    }
}
```

---

*Resource management systems v1.0 | Economic depth | Strategic resource optimization*