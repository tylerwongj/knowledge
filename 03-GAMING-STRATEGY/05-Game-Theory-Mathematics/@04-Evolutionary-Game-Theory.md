# @04-Evolutionary-Game-Theory - Dynamic Strategy Evolution

## 🎯 Learning Objectives  
- Master evolutionary game theory for dynamic strategy systems
- Implement evolutionary stable strategies (ESS) in Unity games
- Design population dynamics and strategy adaptation mechanics
- Apply replicator dynamics to competitive multiplayer environments

## 🔧 Core Evolutionary Game Concepts

### Mathematical Foundation
```csharp
// Unity C# implementation of evolutionary game dynamics
public class EvolutionaryGameEngine : MonoBehaviour
{
    [System.Serializable]
    public class Strategy
    {
        public string strategyName;
        public float[] actionProbabilities;
        public float fitness;
        public float populationShare;
        
        public float CalculateFitness(List<Strategy> population, float[,] payoffMatrix)
        {
            float totalFitness = 0f;
            
            for (int i = 0; i < population.Count; i++)
            {
                Strategy opponent = population[i];
                float expectedPayoff = CalculateExpectedPayoff(this, opponent, payoffMatrix);
                totalFitness += expectedPayoff * opponent.populationShare;
            }
            
            return totalFitness;
        }
        
        public Strategy Mutate(float mutationRate, float mutationStrength)
        {
            var mutatedStrategy = new Strategy
            {
                strategyName = $"{strategyName}_mutant",
                actionProbabilities = new float[actionProbabilities.Length]
            };
            
            for (int i = 0; i < actionProbabilities.Length; i++)
            {
                if (Random.value < mutationRate)
                {
                    float mutation = Random.Range(-mutationStrength, mutationStrength);
                    mutatedStrategy.actionProbabilities[i] = 
                        Mathf.Clamp01(actionProbabilities[i] + mutation);
                }
                else
                {
                    mutatedStrategy.actionProbabilities[i] = actionProbabilities[i];
                }
            }
            
            // Normalize probabilities
            float sum = mutatedStrategy.actionProbabilities.Sum();
            for (int i = 0; i < mutatedStrategy.actionProbabilities.Length; i++)
            {
                mutatedStrategy.actionProbabilities[i] /= sum;
            }
            
            return mutatedStrategy;
        }
    }
    
    public class PopulationDynamics
    {
        public List<Strategy> population;
        public float[,] payoffMatrix;
        public float mutationRate = 0.01f;
        public float selectionPressure = 1.0f;
        
        public void UpdatePopulation(float deltaTime)
        {
            // Calculate fitness for all strategies
            foreach (var strategy in population)
            {
                strategy.fitness = strategy.CalculateFitness(population, payoffMatrix);
            }
            
            // Apply replicator dynamics
            ApplyReplicatorDynamics(deltaTime);
            
            // Apply mutations
            ApplyMutations();
            
            // Remove extinct strategies
            population.RemoveAll(s => s.populationShare < 0.001f);
        }
        
        private void ApplyReplicatorDynamics(float deltaTime)
        {
            float averageFitness = CalculateAverageFitness();
            
            foreach (var strategy in population)
            {
                float growthRate = (strategy.fitness - averageFitness) * selectionPressure;
                strategy.populationShare *= Mathf.Exp(growthRate * deltaTime);
            }
            
            // Normalize population shares
            float totalShare = population.Sum(s => s.populationShare);
            foreach (var strategy in population)
            {
                strategy.populationShare /= totalShare;
            }
        }
        
        private float CalculateAverageFitness()
        {
            return population.Sum(s => s.fitness * s.populationShare);
        }
    }
}
```

### Evolutionary Stable Strategies (ESS)
- **ESS Definition**: Strategies that cannot be invaded by mutants
- **Invasion Resistance**: Testing strategy stability against variants
- **Convergence Analysis**: Long-term population equilibrium
- **Multi-Strategy Equilibria**: Coexistence of different approaches

## 🎮 Gaming Applications

### Dynamic Meta Evolution
```csharp
public class MetaEvolutionSystem : MonoBehaviour
{
    [System.Serializable]
    public class MetaStrategy
    {
        public string strategyName;
        public float usage;
        public float winRate;
        public float adaptationSpeed;
        public List<string> counters;
        public List<string> vulnerabilities;
        
        public float CalculateMetaFitness(Dictionary<string, float> currentMeta)
        {
            float fitness = winRate;
            
            // Adjust fitness based on counter-strategies in meta
            foreach (var counter in counters)
            {
                if (currentMeta.ContainsKey(counter))
                {
                    fitness += currentMeta[counter] * 0.3f; // Benefit from countering popular strategies
                }
            }
            
            // Reduce fitness based on strategies that counter this one
            foreach (var vulnerability in vulnerabilities)
            {
                if (currentMeta.ContainsKey(vulnerability))
                {
                    fitness -= currentMeta[vulnerability] * 0.4f; // Penalty from being countered
                }
            }
            
            return Mathf.Max(0.1f, fitness);
        }
    }
    
    public List<MetaStrategy> availableStrategies;
    public Dictionary<string, float> currentMetaShares;
    public float metaUpdateRate = 0.1f;
    
    void Update()
    {
        UpdateMetaEvolution(Time.deltaTime);
    }
    
    void UpdateMetaEvolution(float deltaTime)
    {
        // Calculate fitness for each strategy in current meta
        var fitnessValues = new Dictionary<string, float>();
        foreach (var strategy in availableStrategies)
        {
            fitnessValues[strategy.strategyName] = 
                strategy.CalculateMetaFitness(currentMetaShares);
        }
        
        // Apply evolutionary pressure
        float averageFitness = fitnessValues.Values.Average();
        var newShares = new Dictionary<string, float>();
        
        foreach (var kvp in currentMetaShares)
        {
            float growthRate = (fitnessValues[kvp.Key] - averageFitness) * metaUpdateRate;
            newShares[kvp.Key] = kvp.Value * Mathf.Exp(growthRate * deltaTime);
        }
        
        // Normalize shares
        float totalShare = newShares.Values.Sum();
        foreach (var key in newShares.Keys.ToList())
        {
            newShares[key] /= totalShare;
        }
        
        currentMetaShares = newShares;
        
        // Trigger events for meta shifts
        DetectMetaShifts();
    }
}
```

### AI Learning and Adaptation
```csharp
public class EvolutionaryAI : MonoBehaviour
{
    [System.Serializable]
    public class AIGenotype
    {
        public float[] genes; // Neural network weights or behavior parameters
        public float fitness;
        public int generation;
        
        public AIGenotype Crossover(AIGenotype partner, float crossoverRate)
        {
            var offspring = new AIGenotype
            {
                genes = new float[genes.Length],
                generation = Mathf.Max(generation, partner.generation) + 1
            };
            
            for (int i = 0; i < genes.Length; i++)
            {
                if (Random.value < crossoverRate)
                {
                    offspring.genes[i] = partner.genes[i];
                }
                else
                {
                    offspring.genes[i] = genes[i];
                }
            }
            
            return offspring;
        }
        
        public void Mutate(float mutationRate, float mutationStrength)
        {
            for (int i = 0; i < genes.Length; i++)
            {
                if (Random.value < mutationRate)
                {
                    genes[i] += Random.Range(-mutationStrength, mutationStrength);
                }
            }
        }
    }
    
    public class GeneticAlgorithm
    {
        public List<AIGenotype> population;
        public int populationSize = 100;
        public float mutationRate = 0.02f;
        public float crossoverRate = 0.7f;
        public float elitismRate = 0.1f;
        
        public void EvolveGeneration()
        {
            // Sort by fitness
            population.Sort((a, b) => b.fitness.CompareTo(a.fitness));
            
            var newPopulation = new List<AIGenotype>();
            
            // Elitism: Keep best individuals
            int eliteCount = Mathf.RoundToInt(populationSize * elitismRate);
            for (int i = 0; i < eliteCount; i++)
            {
                newPopulation.Add(population[i]);
            }
            
            // Generate offspring
            while (newPopulation.Count < populationSize)
            {
                var parent1 = TournamentSelection();
                var parent2 = TournamentSelection();
                
                var offspring = parent1.Crossover(parent2, crossoverRate);
                offspring.Mutate(mutationRate, 0.1f);
                
                newPopulation.Add(offspring);
            }
            
            population = newPopulation;
        }
        
        private AIGenotype TournamentSelection(int tournamentSize = 3)
        {
            var tournament = new List<AIGenotype>();
            for (int i = 0; i < tournamentSize; i++)
            {
                tournament.Add(population[Random.Range(0, population.Count)]);
            }
            
            return tournament.OrderByDescending(individual => individual.fitness).First();
        }
    }
}
```

## 🧮 Advanced Evolutionary Mechanics

### Multi-Level Selection
```csharp
public class MultiLevelSelection : MonoBehaviour
{
    [System.Serializable]
    public class Group
    {
        public List<AIGenotype> members;
        public float groupFitness;
        public float cooperationLevel;
        
        public float CalculateGroupFitness()
        {
            float individualSum = members.Sum(m => m.fitness);
            float cooperationBonus = cooperationLevel * members.Count * 0.5f;
            return individualSum + cooperationBonus;
        }
        
        public void UpdateCooperationLevel()
        {
            // Calculate cooperation based on member behaviors
            cooperationLevel = members.Average(m => GetCooperationGene(m));
        }
        
        private float GetCooperationGene(AIGenotype individual)
        {
            // Assume cooperation is encoded in specific gene
            return individual.genes[0]; // Simplified example
        }
    }
    
    public List<Group> groups;
    public float groupSelectionStrength = 0.3f;
    public float individualSelectionStrength = 0.7f;
    
    public void ApplyMultiLevelSelection()
    {
        // Individual-level selection within groups
        foreach (var group in groups)
        {
            ApplyIndividualSelection(group);
        }
        
        // Group-level selection
        ApplyGroupSelection();
        
        // Migration between groups
        ApplyMigration();
    }
    
    private void ApplyGroupSelection()
    {
        groups.Sort((a, b) => b.groupFitness.CompareTo(a.groupFitness));
        
        // Successful groups get more resources/reproduction opportunities
        for (int i = 0; i < groups.Count; i++)
        {
            float selectionPressure = 1f - ((float)i / groups.Count) * groupSelectionStrength;
            groups[i].members.ForEach(m => m.fitness *= selectionPressure);
        }
    }
}
```

### Adaptive Dynamics
- **Fitness Landscapes**: Dynamic payoff surface navigation
- **Red Queen Effect**: Continuous adaptation arms race
- **Punctuated Equilibrium**: Rapid evolutionary bursts
- **Neutral Networks**: Evolution through neutral mutations

## 🚀 AI/LLM Integration Opportunities

### Evolutionary Game Design Prompts
```
"Design evolutionary game mechanics featuring:
- Replicator dynamics for strategy population evolution
- Mutation and selection pressure systems
- ESS analysis and stability testing
- Unity implementation with genetic algorithms"

"Create adaptive AI system using evolutionary principles:
- Population-based learning algorithms
- Multi-objective fitness optimization
- Dynamic strategy adaptation
- Performance monitoring and analysis"

"Generate evolutionary stable strategy analysis for:
- Competitive multiplayer balance
- AI opponent difficulty scaling
- Meta-game evolution prediction
- Player behavior adaptation systems"
```

### Advanced Evolution Simulation
- **Parameter Space Exploration**: Automated fitness landscape mapping
- **Strategy Discovery**: AI-generated novel approaches
- **Balance Prediction**: Evolutionary equilibrium forecasting
- **Player Modeling**: Behavioral evolution tracking

## 🎯 Practical Implementation

### Unity Evolutionary Framework
```csharp
[CreateAssetMenu(fileName = "EvolutionaryConfig", menuName = "Game Theory/Evolutionary Game")]
public class EvolutionaryGameConfig : ScriptableObject
{
    [Header("Population Settings")]
    public int initialPopulationSize = 100;
    public float mutationRate = 0.02f;
    public float selectionPressure = 1.0f;
    public int maxGenerations = 1000;
    
    [Header("Strategy Evolution")]
    public AnimationCurve fitnessSelection;
    public float crossoverRate = 0.7f;
    public float elitismRate = 0.1f;
    public bool enableNeutralEvolution = true;
    
    [Header("Convergence Criteria")]
    public float convergenceThreshold = 0.001f;
    public int convergenceGenerations = 50;
    public bool stopAtConvergence = true;
    
    public void InitializeEvolution(EvolutionaryGameEngine engine)
    {
        engine.population = GenerateInitialPopulation();
        engine.mutationRate = mutationRate;
        engine.selectionPressure = selectionPressure;
    }
    
    private List<Strategy> GenerateInitialPopulation()
    {
        var population = new List<Strategy>();
        
        for (int i = 0; i < initialPopulationSize; i++)
        {
            var strategy = new Strategy
            {
                strategyName = $"Strategy_{i}",
                populationShare = 1f / initialPopulationSize
            };
            
            // Random initial strategy
            strategy.actionProbabilities = GenerateRandomStrategy();
            population.Add(strategy);
        }
        
        return population;
    }
}
```

### Performance Monitoring
- **Convergence Tracking**: Monitor population stability over time
- **Diversity Metrics**: Measure strategy variation in population
- **Fitness Evolution**: Track average and maximum fitness progression
- **Strategy Genealogy**: Trace successful strategy lineages

## 💡 Key Highlights

### Essential Evolutionary Concepts
- **Replicator Dynamics**: Mathematical model for strategy frequency evolution
- **ESS Criteria**: Strategies stable against invasion by mutants
- **Fitness Landscapes**: Multidimensional strategy space navigation
- **Neutral Evolution**: Changes without fitness impact

### Unity Implementation Patterns
- Modular evolutionary algorithm components
- Configurable selection and mutation operators
- Real-time population monitoring and visualization
- Integration with existing game AI systems

### Game Design Applications
- Dynamic meta-game evolution and balance
- Adaptive AI opponents that learn and evolve
- Player strategy analysis and response systems
- Long-term competitive environment management

## 🔍 Advanced Research Topics

### Cultural Evolution
```csharp
public class CulturalEvolution : MonoBehaviour
{
    [System.Serializable]
    public class CulturalTrait
    {
        public string traitName;
        public float transmissionRate;
        public float innovationRate;
        public float culturalFitness;
        public List<string> prerequisites;
        
        public bool CanTransmit(AIGenotype learner, AIGenotype teacher)
        {
            // Check if learner can acquire trait from teacher
            return Vector3.Distance(GetTraitPosition(learner), GetTraitPosition(teacher)) 
                   < transmissionRate;
        }
        
        public CulturalTrait Innovate(float innovationStrength)
        {
            // Generate variant of cultural trait
            return new CulturalTrait
            {
                traitName = $"{traitName}_variant",
                transmissionRate = transmissionRate + Random.Range(-innovationStrength, innovationStrength),
                culturalFitness = culturalFitness + Random.Range(-0.1f, 0.1f)
            };
        }
    }
}
```

### Coevolutionary Dynamics
- **Predator-Prey Cycles**: Oscillating strategy dominance
- **Arms Race Dynamics**: Escalating competitive adaptation
- **Mutualistic Evolution**: Cooperative strategy coevolution
- **Frequency-Dependent Selection**: Success depends on strategy rarity

---

*Evolutionary game theory for dynamic, adaptive multiplayer gaming systems with emergent strategic complexity*