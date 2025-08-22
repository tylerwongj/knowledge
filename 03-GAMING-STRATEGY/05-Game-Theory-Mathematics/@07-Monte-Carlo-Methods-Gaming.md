# @07-Monte-Carlo-Methods-Gaming - Advanced Simulation and Strategy Optimization

## 🎯 Learning Objectives
- Master Monte Carlo simulation methods for strategic game analysis and optimization
- Implement Monte Carlo Tree Search (MCTS) for dynamic decision-making in complex games
- Build advanced probability estimation systems for uncertain gaming scenarios
- Create AI systems that use statistical simulation for strategic advantage

## 🔧 Monte Carlo Foundations

### Statistical Simulation Principles
```yaml
Monte Carlo Method Core Concepts:
  Random Sampling:
    - Law of Large Numbers: Sample means converge to expected values
    - Central Limit Theorem: Sample distributions approach normal distribution
    - Pseudo-random Numbers: Deterministic algorithms producing random-like sequences
    - Variance Reduction: Techniques to improve estimate accuracy with fewer samples
  
  Convergence Properties:
    - Error Reduction: Error proportional to 1/√n where n is sample size
    - Confidence Intervals: Statistical bounds on estimate accuracy
    - Sample Size Planning: Calculate required samples for desired precision
    - Stopping Criteria: Determine when simulation has sufficient accuracy
  
  Gaming Applications:
    - Strategy Evaluation: Test strategy effectiveness across many scenarios
    - Risk Assessment: Quantify probability distributions of outcomes
    - Decision Optimization: Find optimal strategies through exhaustive simulation
    - Uncertainty Quantification: Model unknown opponent behaviors and game states

Advanced Sampling Techniques:
  Importance Sampling:
    - Focus computation on high-impact scenarios
    - Reduce variance by sampling critical regions more frequently
    - Adjust probabilities to emphasize rare but important events
    - Application: Focus on game-changing moments rather than routine play
  
  Stratified Sampling:
    - Divide problem space into strata for consistent coverage
    - Ensure representation across all important game scenarios
    - Reduce variance compared to pure random sampling
    - Application: Sample across different game phases and opponent types
  
  Antithetic Variates:
    - Use negatively correlated samples to reduce variance
    - Generate paired samples that offset each other's errors
    - Improve estimate accuracy with same computational cost
    - Application: Test complementary strategies simultaneously
  
  Control Variates:
    - Use known analytical solutions to improve unknown estimates
    - Leverage partial analytical knowledge to guide simulation
    - Significantly reduce required sample sizes
    - Application: Use simplified game models to improve complex simulations
```

### Monte Carlo Tree Search Implementation
```python
# Advanced Monte Carlo Tree Search implementation for strategic gaming
import numpy as np
import math
import random
from collections import defaultdict
import copy

class MCTSNode:
    def __init__(self, game_state, parent=None, action=None):
        self.game_state = game_state
        self.parent = parent
        self.action = action  # Action that led to this node
        self.children = {}
        self.visits = 0
        self.total_reward = 0.0
        self.untried_actions = None
        self.is_terminal = False
        
        # Advanced MCTS features
        self.virtual_losses = 0  # For parallel MCTS
        self.policy_prior = None  # For neural network guided MCTS
        self.value_estimate = None
        self.uncertainty_estimate = 0.0
    
    def is_fully_expanded(self):
        """Check if all possible actions have been tried"""
        if self.untried_actions is None:
            self.untried_actions = self.game_state.get_legal_actions()
        return len(self.untried_actions) == 0 and len(self.children) > 0
    
    def get_ucb1_value(self, exploration_constant=1.4):
        """Calculate UCB1 value for action selection"""
        if self.visits == 0:
            return float('inf')
        
        exploitation = self.total_reward / self.visits
        exploration = math.sqrt(math.log(self.parent.visits) / self.visits)
        
        return exploitation + exploration_constant * exploration
    
    def get_puct_value(self, exploration_constant=1.0):
        """PUCT value for neural network guided MCTS"""
        if self.visits == 0:
            return float('inf')
        
        exploitation = self.total_reward / self.visits
        
        # Prior probability bonus (from neural network policy)
        prior_bonus = 0.0
        if self.policy_prior is not None:
            prior_bonus = exploration_constant * self.policy_prior * math.sqrt(self.parent.visits) / (1 + self.visits)
        
        return exploitation + prior_bonus

class AdvancedMCTS:
    def __init__(self, exploration_constant=1.4, max_iterations=10000, max_time=5.0):
        self.exploration_constant = exploration_constant
        self.max_iterations = max_iterations
        self.max_time = max_time
        self.root = None
        
        # Advanced features
        self.neural_network = None  # Optional neural network for guidance
        self.use_virtual_losses = True
        self.use_progressive_widening = True
        self.progressive_widening_constant = 0.5
        
    def search(self, initial_game_state):
        """Main MCTS search algorithm"""
        self.root = MCTSNode(initial_game_state)
        
        import time
        start_time = time.time()
        
        for iteration in range(self.max_iterations):
            if time.time() - start_time > self.max_time:
                break
            
            # MCTS four phases
            selected_node = self.selection(self.root)
            expanded_node = self.expansion(selected_node)
            reward = self.simulation(expanded_node)
            self.backpropagation(expanded_node, reward)
            
            # Optional: update neural network
            if self.neural_network and iteration % 100 == 0:
                self.update_neural_network()
        
        return self.get_best_action()
    
    def selection(self, node):
        """Select most promising node using UCB1 or PUCT"""
        while not node.is_terminal and node.is_fully_expanded():
            if self.neural_network:
                # Use PUCT for neural network guided search
                best_child = max(node.children.values(), 
                               key=lambda n: n.get_puct_value(self.exploration_constant))
            else:
                # Use UCB1 for traditional MCTS
                best_child = max(node.children.values(), 
                               key=lambda n: n.get_ucb1_value(self.exploration_constant))
            
            # Apply virtual losses for parallel search
            if self.use_virtual_losses:
                best_child.virtual_losses += 1
            
            node = best_child
        
        return node
    
    def expansion(self, node):
        """Expand node by adding new child"""
        if node.is_terminal:
            return node
        
        if node.untried_actions is None:
            node.untried_actions = node.game_state.get_legal_actions()
        
        # Progressive widening: limit number of children explored
        if self.use_progressive_widening:
            max_children = int(self.progressive_widening_constant * math.sqrt(node.visits))
            if len(node.children) >= max_children and node.untried_actions:
                return node
        
        if node.untried_actions:
            action = random.choice(node.untried_actions)
            node.untried_actions.remove(action)
            
            new_state = node.game_state.apply_action(action)
            child = MCTSNode(new_state, parent=node, action=action)
            
            # Neural network evaluation
            if self.neural_network:
                policy_probs, value_estimate = self.neural_network.evaluate(new_state)
                child.policy_prior = policy_probs.get(action, 0.1)
                child.value_estimate = value_estimate
            
            node.children[action] = child
            return child
        
        return node
    
    def simulation(self, node, max_depth=100):
        """Simulate random playouts or use neural network evaluation"""
        if self.neural_network and node.value_estimate is not None:
            # Use neural network value estimate instead of random simulation
            return node.value_estimate
        
        # Traditional random simulation
        current_state = copy.deepcopy(node.game_state)
        depth = 0
        
        while not current_state.is_terminal() and depth < max_depth:
            legal_actions = current_state.get_legal_actions()
            if not legal_actions:
                break
            
            # Use intelligent simulation policy instead of pure random
            action = self.select_simulation_action(current_state, legal_actions)
            current_state = current_state.apply_action(action)
            depth += 1
        
        return current_state.get_reward()
    
    def select_simulation_action(self, state, legal_actions):
        """Select action during simulation using heuristics"""
        # Implement domain-specific heuristics here
        # For now, use uniform random selection
        return random.choice(legal_actions)
    
    def backpropagation(self, node, reward):
        """Propagate reward back through the tree"""
        while node is not None:
            node.visits += 1
            node.total_reward += reward
            
            # Remove virtual losses
            if self.use_virtual_losses and node.virtual_losses > 0:
                node.virtual_losses -= 1
            
            # Discount factor for multi-step rewards
            reward *= 0.99  # Slight discount
            node = node.parent
    
    def get_best_action(self):
        """Get the best action based on visit count"""
        if not self.root.children:
            return None
        
        # Return action with highest visit count (most explored)
        best_action = max(self.root.children.keys(), 
                         key=lambda a: self.root.children[a].visits)
        
        # Also return statistics for analysis
        action_stats = {}
        for action, child in self.root.children.items():
            action_stats[action] = {
                'visits': child.visits,
                'average_reward': child.total_reward / child.visits if child.visits > 0 else 0,
                'confidence': self.calculate_confidence_interval(child),
                'exploration_bonus': self.calculate_exploration_bonus(child)
            }
        
        return best_action, action_stats
    
    def calculate_confidence_interval(self, node, confidence=0.95):
        """Calculate confidence interval for node's reward estimate"""
        if node.visits < 2:
            return (float('-inf'), float('inf'))
        
        mean = node.total_reward / node.visits
        # Simplified confidence interval calculation
        # In practice, would need to track reward variance
        std_error = 1.0 / math.sqrt(node.visits)  # Approximate
        z_score = 1.96  # 95% confidence interval
        
        margin_of_error = z_score * std_error
        return (mean - margin_of_error, mean + margin_of_error)

# Advanced Monte Carlo strategy evaluation
class StrategyEvaluator:
    def __init__(self):
        self.evaluation_cache = {}
        self.confidence_thresholds = {
            'low': 0.8,
            'medium': 0.9,
            'high': 0.95,
            'very_high': 0.99
        }
    
    def evaluate_strategy_portfolio(self, strategies, game_scenarios, num_simulations=10000):
        """Evaluate multiple strategies across various scenarios"""
        results = {
            'strategy_performance': {},
            'scenario_analysis': {},
            'optimal_strategy_mapping': {},
            'risk_analysis': {},
            'confidence_analysis': {}
        }
        
        for strategy in strategies:
            strategy_results = self.evaluate_single_strategy(
                strategy, game_scenarios, num_simulations
            )
            results['strategy_performance'][strategy.name] = strategy_results
        
        # Analyze optimal strategy for each scenario
        results['optimal_strategy_mapping'] = self.find_optimal_strategies_per_scenario(
            results['strategy_performance'], game_scenarios
        )
        
        # Risk analysis across strategies
        results['risk_analysis'] = self.analyze_strategy_risks(
            results['strategy_performance']
        )
        
        return results
    
    def evaluate_single_strategy(self, strategy, scenarios, num_simulations):
        """Evaluate single strategy across all scenarios"""
        scenario_results = {}
        
        for scenario in scenarios:
            cache_key = f"{strategy.name}_{hash(str(scenario))}"
            
            if cache_key in self.evaluation_cache:
                scenario_results[scenario.name] = self.evaluation_cache[cache_key]
                continue
            
            # Run Monte Carlo simulations
            simulation_results = []
            for _ in range(num_simulations):
                result = self.run_single_simulation(strategy, scenario)
                simulation_results.append(result)
            
            # Statistical analysis
            analysis = self.analyze_simulation_results(simulation_results)
            scenario_results[scenario.name] = analysis
            self.evaluation_cache[cache_key] = analysis
        
        return scenario_results
    
    def run_single_simulation(self, strategy, scenario):
        """Run single Monte Carlo simulation"""
        # Initialize game state from scenario
        game_state = scenario.create_initial_state()
        
        total_reward = 0
        step_count = 0
        max_steps = 1000  # Prevent infinite games
        
        while not game_state.is_terminal() and step_count < max_steps:
            # Get strategy decision
            action = strategy.select_action(game_state)
            
            # Apply action and get reward
            game_state = game_state.apply_action(action)
            reward = game_state.get_reward()
            
            total_reward += reward
            step_count += 1
        
        return {
            'total_reward': total_reward,
            'steps_taken': step_count,
            'final_state': game_state,
            'success': game_state.is_successful_termination()
        }
    
    def analyze_simulation_results(self, results):
        """Analyze results from multiple simulations"""
        rewards = [r['total_reward'] for r in results]
        steps = [r['steps_taken'] for r in results]
        success_rate = np.mean([r['success'] for r in results])
        
        analysis = {
            'mean_reward': np.mean(rewards),
            'reward_std': np.std(rewards),
            'median_reward': np.median(rewards),
            'reward_range': (np.min(rewards), np.max(rewards)),
            'mean_steps': np.mean(steps),
            'success_rate': success_rate,
            'confidence_intervals': self.calculate_confidence_intervals(rewards),
            'risk_metrics': self.calculate_risk_metrics(rewards),
            'sample_size': len(results)
        }
        
        return analysis
    
    def calculate_risk_metrics(self, rewards):
        """Calculate various risk metrics"""
        rewards = np.array(rewards)
        mean_reward = np.mean(rewards)
        
        # Value at Risk (VaR) - worst case in top 5% of scenarios
        var_95 = np.percentile(rewards, 5)
        var_99 = np.percentile(rewards, 1)
        
        # Conditional Value at Risk (CVaR) - expected loss beyond VaR
        cvar_95 = np.mean(rewards[rewards <= var_95])
        cvar_99 = np.mean(rewards[rewards <= var_99])
        
        # Sharpe ratio approximation
        sharpe_ratio = mean_reward / np.std(rewards) if np.std(rewards) > 0 else 0
        
        # Maximum drawdown (simplified)
        cumulative_rewards = np.cumsum(rewards)
        running_max = np.maximum.accumulate(cumulative_rewards)
        drawdown = running_max - cumulative_rewards
        max_drawdown = np.max(drawdown)
        
        return {
            'value_at_risk_95': var_95,
            'value_at_risk_99': var_99,
            'conditional_var_95': cvar_95,
            'conditional_var_99': cvar_99,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'downside_risk': np.std(rewards[rewards < mean_reward]),
            'upside_potential': np.mean(rewards[rewards > mean_reward]) - mean_reward
        }

# Parallel Monte Carlo implementation for performance
class ParallelMonteCarlo:
    def __init__(self, num_processes=4):
        self.num_processes = num_processes
    
    def parallel_strategy_evaluation(self, strategies, scenarios, total_simulations):
        """Run strategy evaluation in parallel"""
        import multiprocessing as mp
        from functools import partial
        
        # Divide simulations among processes
        sims_per_process = total_simulations // self.num_processes
        
        # Create evaluation function
        eval_func = partial(self.evaluate_strategy_chunk, 
                           strategies=strategies, scenarios=scenarios)
        
        # Run parallel evaluation
        with mp.Pool(processes=self.num_processes) as pool:
            chunk_results = pool.map(eval_func, 
                                   [sims_per_process] * self.num_processes)
        
        # Aggregate results
        return self.aggregate_parallel_results(chunk_results)

# Claude Code prompt for Monte Carlo gaming:
"""
Create advanced Monte Carlo simulation system for competitive gaming:
1. Implement MCTS with neural network guidance for real-time strategic decisions
2. Build comprehensive strategy evaluation using statistical simulation
3. Create parallel Monte Carlo system for rapid strategy optimization
4. Develop risk analysis tools that quantify strategy robustness
5. Integrate with Unity for live Monte Carlo decision support during matches
"""
```

## 🚀 Advanced Probability Estimation

### Bayesian Inference for Gaming
```yaml
Bayesian Methods in Gaming Strategy:
  Prior Knowledge Integration:
    - Historical Performance: Use past game results as prior distributions
    - Player Tendencies: Model opponent behavior patterns probabilistically
    - Strategy Effectiveness: Update beliefs about strategy success rates
    - Meta-game Evolution: Track changing strategy effectiveness over time
  
  Uncertainty Quantification:
    - Parameter Estimation: Estimate unknown game parameters with confidence intervals
    - Model Selection: Choose between competing strategic models using evidence
    - Prediction Intervals: Provide uncertainty bounds on future performance
    - Decision Theory: Make optimal decisions accounting for uncertainty
  
  Online Learning:
    - Sequential Updates: Continuously refine estimates as new data arrives
    - Adaptive Strategies: Modify tactics based on updated beliefs
    - Change Detection: Identify when opponent behavior patterns shift
    - Exploration vs Exploitation: Balance information gathering and optimization

Advanced Sampling Methods:
  Markov Chain Monte Carlo (MCMC):
    - Gibbs Sampling: Sample from complex multivariate distributions
    - Metropolis-Hastings: General purpose MCMC for arbitrary distributions
    - Hamiltonian Monte Carlo: Efficient sampling using gradient information
    - Application: Sample from complex strategy spaces and opponent models
  
  Particle Filtering:
    - Sequential Monte Carlo for tracking changing game states
    - Handle non-linear, non-Gaussian dynamics in gaming scenarios
    - Real-time belief updates about opponent strategies
    - Particle degeneracy prevention for long-term tracking
  
  Variational Methods:
    - Approximate complex posteriors with simpler distributions
    - Fast approximate inference for real-time gaming applications
    - Variational Bayes for automatic model complexity control
    - Mean-field approximations for high-dimensional strategy spaces
```

### Unity Integration for Real-Time Monte Carlo
```csharp
// Unity implementation of real-time Monte Carlo decision system
using UnityEngine;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Linq;

public class RealTimeMonteCarloEngine : MonoBehaviour
{
    [Header("Monte Carlo Configuration")]
    [SerializeField] private int simulationsPerDecision = 1000;
    [SerializeField] private float maxDecisionTime = 0.1f;
    [SerializeField] private int maxSimulationDepth = 50;
    [SerializeField] private bool useParallelSimulation = true;
    
    [Header("Strategy Evaluation")]
    [SerializeField] private List<StrategyTemplate> availableStrategies;
    [SerializeField] private float explorationConstant = 1.4f;
    [SerializeField] private bool useProgressiveWidening = true;
    
    private MonteCarloTreeSearch mctsEngine;
    private Dictionary<string, StrategyStatistics> strategyStats;
    private GameStateEvaluator gameStateEvaluator;
    
    [System.Serializable]
    public class StrategyTemplate
    {
        public string strategyName;
        public StrategyType type;
        public float baseEffectiveness = 0.5f;
        public List<GameCondition> optimalConditions;
        public float adaptationRate = 0.1f;
    }
    
    public enum StrategyType
    {
        Aggressive,
        Defensive,
        Economic,
        Adaptive,
        CounterStrategy,
        Hybrid
    }
    
    [System.Serializable]
    public class GameCondition
    {
        public string conditionName;
        public float threshold;
        public ComparisonType comparison;
    }
    
    public enum ComparisonType
    {
        Greater,
        Less,
        Equal,
        GreaterOrEqual,
        LessOrEqual
    }
    
    [System.Serializable]
    public class StrategyStatistics
    {
        public string strategyName;
        public int totalSimulations;
        public float averageReward;
        public float winRate;
        public float variance;
        public List<float> recentPerformance;
        public float confidenceLower;
        public float confidenceUpper;
        
        public void UpdateStatistics(float reward, bool won)
        {
            totalSimulations++;
            
            // Update running averages
            float alpha = 1.0f / Mathf.Min(totalSimulations, 100); // Adaptive learning rate
            averageReward = averageReward * (1 - alpha) + reward * alpha;
            winRate = winRate * (1 - alpha) + (won ? 1f : 0f) * alpha;
            
            // Track recent performance
            recentPerformance.Add(reward);
            if (recentPerformance.Count > 50)
                recentPerformance.RemoveAt(0);
            
            // Update confidence intervals
            UpdateConfidenceInterval();
        }
        
        private void UpdateConfidenceInterval()
        {
            if (recentPerformance.Count < 10) return;
            
            float mean = recentPerformance.Average();
            float variance = recentPerformance.Select(x => (x - mean) * (x - mean)).Average();
            float standardError = Mathf.Sqrt(variance / recentPerformance.Count);
            
            // 95% confidence interval
            float marginOfError = 1.96f * standardError;
            confidenceLower = mean - marginOfError;
            confidenceUpper = mean + marginOfError;
        }
    }
    
    void Start()
    {
        InitializeMonteCarloSystem();
    }
    
    void InitializeMonteCarloSystem()
    {
        mctsEngine = new MonteCarloTreeSearch(explorationConstant, simulationsPerDecision, maxDecisionTime);
        strategyStats = new Dictionary<string, StrategyStatistics>();
        gameStateEvaluator = GetComponent<GameStateEvaluator>();
        
        // Initialize strategy statistics
        foreach (var strategy in availableStrategies)
        {
            strategyStats[strategy.strategyName] = new StrategyStatistics
            {
                strategyName = strategy.strategyName,
                averageReward = strategy.baseEffectiveness,
                recentPerformance = new List<float>()
            };
        }
        
        Debug.Log("Monte Carlo Engine initialized with " + availableStrategies.Count + " strategies");
    }
    
    public async Task<MonteCarloDecision> MakeOptimalDecision(GameState currentState)
    {
        var startTime = Time.realtimeSinceStartup;
        
        // Evaluate available actions using Monte Carlo simulation
        var actionEvaluations = await EvaluateActionsAsync(currentState);
        
        // Select best action based on evaluation
        var bestAction = SelectBestAction(actionEvaluations);
        
        var decisionTime = Time.realtimeSinceStartup - startTime;
        
        return new MonteCarloDecision
        {
            selectedAction = bestAction.action,
            confidence = bestAction.confidence,
            expectedReward = bestAction.expectedReward,
            alternativeActions = actionEvaluations.Take(3).ToList(),
            decisionTime = decisionTime,
            simulationsRun = simulationsPerDecision,
            explorationInfo = GetExplorationInfo(actionEvaluations)
        };
    }
    
    async Task<List<ActionEvaluation>> EvaluateActionsAsync(GameState gameState)
    {
        var availableActions = gameState.GetLegalActions();
        var evaluations = new List<ActionEvaluation>();
        
        if (useParallelSimulation)
        {
            // Run simulations in parallel for better performance
            var tasks = availableActions.Select(action => 
                Task.Run(() => EvaluateAction(action, gameState))
            ).ToArray();
            
            var results = await Task.WhenAll(tasks);
            evaluations.AddRange(results);
        }
        else
        {
            // Sequential evaluation
            foreach (var action in availableActions)
            {
                var evaluation = EvaluateAction(action, gameState);
                evaluations.Add(evaluation);
            }
        }
        
        return evaluations.OrderByDescending(e => e.expectedReward).ToList();
    }
    
    ActionEvaluation EvaluateAction(GameAction action, GameState initialState)
    {
        var rewards = new List<float>();
        var wins = 0;
        var simulationsToRun = Mathf.Min(simulationsPerDecision, 
            Mathf.RoundToInt(maxDecisionTime * 1000)); // Adaptive simulation count
        
        for (int i = 0; i < simulationsToRun; i++)
        {
            var result = SimulateSingleGame(action, initialState);
            rewards.Add(result.totalReward);
            if (result.won) wins++;
        }
        
        // Calculate statistics
        float meanReward = rewards.Average();
        float variance = rewards.Select(r => (r - meanReward) * (r - meanReward)).Average();
        float standardError = Mathf.Sqrt(variance / simulationsToRun);
        
        return new ActionEvaluation
        {
            action = action,
            expectedReward = meanReward,
            winRate = (float)wins / simulationsToRun,
            confidence = 1.0f - (standardError / (Mathf.Abs(meanReward) + 0.01f)),
            variance = variance,
            simulationCount = simulationsToRun,
            confidenceInterval = new Vector2(
                meanReward - 1.96f * standardError,
                meanReward + 1.96f * standardError
            )
        };
    }
    
    SimulationResult SimulateSingleGame(GameAction firstAction, GameState initialState)
    {
        var currentState = initialState.ApplyAction(firstAction);
        var totalReward = currentState.GetReward();
        var stepCount = 1;
        
        // Continue simulation with selected strategy
        var activeStrategy = SelectStrategyForSimulation(currentState);
        
        while (!currentState.IsTerminal() && stepCount < maxSimulationDepth)
        {
            var actions = currentState.GetLegalActions();
            if (actions.Count == 0) break;
            
            var selectedAction = activeStrategy.SelectAction(currentState, actions);
            currentState = currentState.ApplyAction(selectedAction);
            totalReward += currentState.GetReward();
            stepCount++;
            
            // Potentially switch strategies during simulation
            if (stepCount % 10 == 0)
            {
                activeStrategy = SelectStrategyForSimulation(currentState);
            }
        }
        
        return new SimulationResult
        {
            totalReward = totalReward,
            finalState = currentState,
            won = currentState.IsVictorious(),
            stepsTaken = stepCount
        };
    }
    
    IStrategy SelectStrategyForSimulation(GameState state)
    {
        // Select strategy based on current game conditions and statistics
        var candidates = availableStrategies.Where(s => 
            IsStrategyApplicable(s, state)
        ).ToList();
        
        if (candidates.Count == 0)
            return new RandomStrategy();
        
        // Weighted selection based on performance statistics
        var weights = candidates.Select(s => 
            strategyStats[s.strategyName].averageReward + 
            strategyStats[s.strategyName].confidenceUpper * 0.1f
        ).ToArray();
        
        var selectedStrategy = WeightedRandomSelection(candidates, weights);
        return CreateStrategyInstance(selectedStrategy);
    }
    
    ActionEvaluation SelectBestAction(List<ActionEvaluation> evaluations)
    {
        if (evaluations.Count == 0) return null;
        
        // Multi-criteria selection: reward, confidence, and win rate
        var scored = evaluations.Select(e => new {
            evaluation = e,
            score = e.expectedReward * 0.6f + 
                   e.confidence * 0.2f + 
                   e.winRate * 0.2f
        }).OrderByDescending(x => x.score);
        
        return scored.First().evaluation;
    }
    
    public void UpdateStrategyPerformance(string strategyName, float reward, bool won)
    {
        if (strategyStats.ContainsKey(strategyName))
        {
            strategyStats[strategyName].UpdateStatistics(reward, won);
        }
    }
    
    public StrategyPerformanceReport GeneratePerformanceReport()
    {
        return new StrategyPerformanceReport
        {
            strategyStatistics = strategyStats.Values.ToList(),
            totalSimulations = strategyStats.Values.Sum(s => s.totalSimulations),
            bestPerformingStrategy = strategyStats.Values
                .OrderByDescending(s => s.averageReward)
                .FirstOrDefault()?.strategyName,
            mostReliableStrategy = strategyStats.Values
                .OrderByDescending(s => s.winRate)
                .FirstOrDefault()?.strategyName
        };
    }
    
    [System.Serializable]
    public class ActionEvaluation
    {
        public GameAction action;
        public float expectedReward;
        public float winRate;
        public float confidence;
        public float variance;
        public int simulationCount;
        public Vector2 confidenceInterval;
    }
    
    [System.Serializable]
    public class MonteCarloDecision
    {
        public GameAction selectedAction;
        public float confidence;
        public float expectedReward;
        public List<ActionEvaluation> alternativeActions;
        public float decisionTime;
        public int simulationsRun;
        public string explorationInfo;
    }
    
    [System.Serializable]
    public class SimulationResult
    {
        public float totalReward;
        public GameState finalState;
        public bool won;
        public int stepsTaken;
    }
    
    [System.Serializable]
    public class StrategyPerformanceReport
    {
        public List<StrategyStatistics> strategyStatistics;
        public int totalSimulations;
        public string bestPerformingStrategy;
        public string mostReliableStrategy;
    }
}
```

## 💡 Key Highlights

### Monte Carlo Method Advantages
- **Handles Complexity**: Effective for games with large state spaces and complex interactions
- **Uncertainty Quantification**: Provides statistical confidence measures for decisions
- **Anytime Algorithm**: Can provide results with varying quality based on available computation time
- **Domain Flexibility**: Applicable to diverse game types without requiring domain-specific knowledge

### MCTS Strategic Benefits
- **Selective Expansion**: Focuses computational resources on most promising game paths
- **Asymmetric Tree Growth**: Automatically identifies and explores critical decision points
- **Balance Exploration/Exploitation**: UCB1 formula optimally balances trying new strategies vs exploiting known good ones
- **Scalable Performance**: Performance improves gracefully with additional computation time

### Real-Time Integration Features
- **Adaptive Simulation**: Adjusts simulation count based on available decision time
- **Parallel Processing**: Leverages multiple CPU cores for faster strategy evaluation
- **Statistical Confidence**: Provides uncertainty estimates for strategic recommendations
- **Online Learning**: Continuously improves strategy evaluation based on actual game outcomes

### Unity Implementation Benefits
- **Real-Time Decision Support**: Provides strategic recommendations during live gameplay
- **Performance Monitoring**: Tracks and visualizes strategy effectiveness over time
- **Configurable Parameters**: Allows tuning of exploration vs exploitation balance
- **Integration Ready**: Designed for seamless integration with existing Unity game systems

This comprehensive Monte Carlo system provides sophisticated statistical simulation capabilities for strategic gaming, enabling data-driven decision making with quantified confidence levels and continuous learning from gameplay experience.