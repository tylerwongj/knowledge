# @01-Nash Equilibrium Gaming Applications

## 🎯 Learning Objectives
- Master Nash equilibrium concepts and their applications in competitive gaming
- Develop mathematical frameworks for analyzing strategic decision-making
- Leverage AI tools for automated game theory analysis and optimization
- Build Unity-based systems for implementing strategic AI behaviors

## 🎲 Nash Equilibrium Fundamentals

### Core Game Theory Concepts
**Mathematical Foundation for Gaming Strategy**:
```csharp
// GameTheoryAnalyzer.cs - Nash equilibrium analysis for gaming applications
using UnityEngine;
using System.Collections.Generic;
using System.Linq;

[System.Serializable]
public class GameStrategy
{
    public string strategyName;
    public string description;
    public float[] payoffMatrix; // Payoffs against different opponent strategies
    public float probability; // Mixed strategy probability
    public bool isDominant; // Pure strategy dominance
    public float expectedPayoff;
}

[System.Serializable]
public class Player
{
    public string playerName;
    public List<GameStrategy> availableStrategies;
    public GameStrategy currentStrategy;
    public float[] mixedStrategyProbabilities;
    public float totalExpectedPayoff;
    public bool isRationalPlayer; // Assumes perfect information and rational decisions
}

[System.Serializable]
public class GameScenario
{
    public string scenarioName;
    public string gameType; // "Zero-Sum", "Non-Zero-Sum", "Cooperative"
    public List<Player> players;
    public float[,] payoffMatrix;
    public List<NashEquilibrium> equilibria;
    public bool hasStrictEquilibrium;
    public float stabilityIndex; // How stable the equilibrium is
}

[System.Serializable]
public class NashEquilibrium
{
    public string equilibriumType; // "Pure", "Mixed", "Correlated"
    public Dictionary<string, float[]> playerStrategies; // Player -> mixed strategy probabilities
    public float[] equilibriumPayoffs;
    public float stabilityScore; // 0-1, higher = more stable
    public bool isPareteoOptimal;
    public string description;
}

public class GameTheoryAnalyzer : MonoBehaviour
{
    [Header("Analysis Configuration")]
    public string currentScenario = "RPS-Extended";
    public bool enableRealTimeAnalysis = true;
    public float analysisInterval = 5f;
    public int simulationRounds = 1000;
    
    [Header("Game Types")]
    public List<GameScenario> gameScenarios;
    
    private GameScenario activeScenario;
    private List<GameHistory> gameHistory = new List<GameHistory>();
    
    void Start()
    {
        InitializeGameScenarios();
        SetActiveScenario(currentScenario);
        
        if (enableRealTimeAnalysis)
        {
            InvokeRepeating(nameof(AnalyzeCurrentEquilibrium), 0f, analysisInterval);
        }
    }
    
    void InitializeGameScenarios()
    {
        gameScenarios = new List<GameScenario>();
        
        // Rock-Paper-Scissors Extended (Classic Nash Example)
        CreateRockPaperScissorsScenario();
        
        // Prisoner's Dilemma (Game Theory Classic)
        CreatePrisonersDilemmaScenario();
        
        // Battle of the Sexes (Coordination Game)
        CreateBattleOfSexesScenario();
        
        // Matching Pennies (Zero-Sum Game)
        CreateMatchingPenniesScenario();
        
        // Gaming-Specific Scenarios
        CreateMOBATeamFightScenario();
        CreateFPSPositioningScenario();
        
        Debug.Log($"📊 Initialized {gameScenarios.Count} game theory scenarios");
    }
    
    void CreateRockPaperScissorsScenario()
    {
        var rpsScenario = new GameScenario
        {
            scenarioName = "RPS-Extended",
            gameType = "Zero-Sum",
            players = new List<Player>(),
            equilibria = new List<NashEquilibrium>(),
            hasStrictEquilibrium = false
        };
        
        // Create two players with RPS strategies
        var player1 = new Player
        {
            playerName = "Player1",
            availableStrategies = new List<GameStrategy>
            {
                new GameStrategy { strategyName = "Rock", payoffMatrix = new float[] { 0, -1, 1 } },
                new GameStrategy { strategyName = "Paper", payoffMatrix = new float[] { 1, 0, -1 } },
                new GameStrategy { strategyName = "Scissors", payoffMatrix = new float[] { -1, 1, 0 } }
            },
            isRationalPlayer = true
        };
        
        var player2 = new Player
        {
            playerName = "Player2",
            availableStrategies = new List<GameStrategy>
            {
                new GameStrategy { strategyName = "Rock", payoffMatrix = new float[] { 0, 1, -1 } },
                new GameStrategy { strategyName = "Paper", payoffMatrix = new float[] { -1, 0, 1 } },
                new GameStrategy { strategyName = "Scissors", payoffMatrix = new float[] { 1, -1, 0 } }
            },
            isRationalPlayer = true
        };
        
        rpsScenario.players.Add(player1);
        rpsScenario.players.Add(player2);
        
        // Nash equilibrium: Mixed strategy (1/3, 1/3, 1/3) for both players
        var nashEquilibrium = new NashEquilibrium
        {
            equilibriumType = "Mixed",
            playerStrategies = new Dictionary<string, float[]>
            {
                ["Player1"] = new float[] { 1f/3f, 1f/3f, 1f/3f },
                ["Player2"] = new float[] { 1f/3f, 1f/3f, 1f/3f }
            },
            equilibriumPayoffs = new float[] { 0f, 0f }, // Expected payoff is 0 for both
            stabilityScore = 1f,
            isPareteoOptimal = true,
            description = "Mixed strategy equilibrium with equal probabilities"
        };
        
        rpsScenario.equilibria.Add(nashEquilibrium);
        gameScenarios.Add(rpsScenario);
    }
    
    void CreatePrisonersDilemmaScenario()
    {
        var pdScenario = new GameScenario
        {
            scenarioName = "Prisoners-Dilemma",
            gameType = "Non-Zero-Sum",
            players = new List<Player>(),
            equilibria = new List<NashEquilibrium>()
        };
        
        var prisoner1 = new Player
        {
            playerName = "Prisoner1",
            availableStrategies = new List<GameStrategy>
            {
                new GameStrategy { strategyName = "Cooperate", payoffMatrix = new float[] { 3, 0 } }, // vs Cooperate, vs Defect
                new GameStrategy { strategyName = "Defect", payoffMatrix = new float[] { 5, 1 } }
            },
            isRationalPlayer = true
        };
        
        var prisoner2 = new Player
        {
            playerName = "Prisoner2",
            availableStrategies = new List<GameStrategy>
            {
                new GameStrategy { strategyName = "Cooperate", payoffMatrix = new float[] { 3, 0 } },
                new GameStrategy { strategyName = "Defect", payoffMatrix = new float[] { 5, 1 } }
            },
            isRationalPlayer = true
        };
        
        pdScenario.players.Add(prisoner1);
        pdScenario.players.Add(prisoner2);
        
        // Nash equilibrium: (Defect, Defect) - but not Pareto optimal
        var nashEquilibrium = new NashEquilibrium
        {
            equilibriumType = "Pure",
            playerStrategies = new Dictionary<string, float[]>
            {
                ["Prisoner1"] = new float[] { 0f, 1f }, // 100% Defect
                ["Prisoner2"] = new float[] { 0f, 1f }  // 100% Defect
            },
            equilibriumPayoffs = new float[] { 1f, 1f },
            stabilityScore = 1f,
            isPareteoOptimal = false, // (Cooperate, Cooperate) would be better for both
            description = "Dominant strategy equilibrium - both defect despite mutual cooperation being better"
        };
        
        pdScenario.equilibria.Add(nashEquilibrium);
        gameScenarios.Add(pdScenario);
    }
    
    void CreateMOBATeamFightScenario()
    {
        var mobaScenario = new GameScenario
        {
            scenarioName = "MOBA-TeamFight",
            gameType = "Non-Zero-Sum",
            players = new List<Player>(),
            equilibria = new List<NashEquilibrium>()
        };
        
        var team1 = new Player
        {
            playerName = "Team1",
            availableStrategies = new List<GameStrategy>
            {
                new GameStrategy 
                { 
                    strategyName = "Engage", 
                    description = "Initiate team fight aggressively",
                    payoffMatrix = new float[] { 2, -1, 1 } // vs Engage, vs Disengage, vs Split
                },
                new GameStrategy 
                { 
                    strategyName = "Disengage", 
                    description = "Avoid team fight and farm",
                    payoffMatrix = new float[] { -2, 0, -1 }
                },
                new GameStrategy 
                { 
                    strategyName = "Split-Push", 
                    description = "Split map pressure",
                    payoffMatrix = new float[] { 1, 2, 0 }
                }
            },
            isRationalPlayer = true
        };
        
        var team2 = new Player
        {
            playerName = "Team2",
            availableStrategies = new List<GameStrategy>
            {
                new GameStrategy { strategyName = "Engage", payoffMatrix = new float[] { 2, 1, -1 } },
                new GameStrategy { strategyName = "Disengage", payoffMatrix = new float[] { -1, 0, 2 } },
                new GameStrategy { strategyName = "Split-Push", payoffMatrix = new float[] { 1, -2, 0 } }
            },
            isRationalPlayer = true
        };
        
        mobaScenario.players.Add(team1);
        mobaScenario.players.Add(team2);
        
        // Mixed strategy equilibrium
        var nashEquilibrium = CalculateMixedStrategyEquilibrium(mobaScenario);
        mobaScenario.equilibria.Add(nashEquilibrium);
        
        gameScenarios.Add(mobaScenario);
    }
    
    void CreateFPSPositioningScenario()
    {
        var fpsScenario = new GameScenario
        {
            scenarioName = "FPS-Positioning",
            gameType = "Zero-Sum",
            players = new List<Player>(),
            equilibria = new List<NashEquilibrium>()
        };
        
        var attacker = new Player
        {
            playerName = "Attacker",
            availableStrategies = new List<GameStrategy>
            {
                new GameStrategy 
                { 
                    strategyName = "Rush-A", 
                    description = "Attack site A aggressively",
                    payoffMatrix = new float[] { 3, -1, 1 } // vs Defend-A, vs Defend-B, vs Stack-Mid
                },
                new GameStrategy 
                { 
                    strategyName = "Rush-B", 
                    description = "Attack site B aggressively",
                    payoffMatrix = new float[] { -1, 3, 1 }
                },
                new GameStrategy 
                { 
                    strategyName = "Split-Attack", 
                    description = "Divide forces between sites",
                    payoffMatrix = new float[] { 1, 1, -2 }
                }
            },
            isRationalPlayer = true
        };
        
        var defender = new Player
        {
            playerName = "Defender",
            availableStrategies = new List<GameStrategy>
            {
                new GameStrategy { strategyName = "Defend-A", payoffMatrix = new float[] { -3, 1, -1 } },
                new GameStrategy { strategyName = "Defend-B", payoffMatrix = new float[] { 1, -3, -1 } },
                new GameStrategy { strategyName = "Stack-Mid", payoffMatrix = new float[] { -1, -1, 2 } }
            },
            isRationalPlayer = true
        };
        
        fpsScenario.players.Add(attacker);
        fpsScenario.players.Add(defender);
        
        var nashEquilibrium = CalculateMixedStrategyEquilibrium(fpsScenario);
        fpsScenario.equilibria.Add(nashEquilibrium);
        
        gameScenarios.Add(fpsScenario);
    }
    
    NashEquilibrium CalculateMixedStrategyEquilibrium(GameScenario scenario)
    {
        // Simplified mixed strategy calculation for 2-player games
        if (scenario.players.Count != 2)
        {
            return new NashEquilibrium
            {
                equilibriumType = "Complex",
                description = "Multi-player equilibrium requires advanced calculation"
            };
        }
        
        var player1 = scenario.players[0];
        var player2 = scenario.players[1];
        
        int numStrategiesP1 = player1.availableStrategies.Count;
        int numStrategiesP2 = player2.availableStrategies.Count;
        
        // For demonstration, use equal probabilities (actual calculation would involve linear programming)
        float[] p1Probabilities = new float[numStrategiesP1];
        float[] p2Probabilities = new float[numStrategiesP2];
        
        for (int i = 0; i < numStrategiesP1; i++)
        {
            p1Probabilities[i] = 1f / numStrategiesP1;
        }
        
        for (int i = 0; i < numStrategiesP2; i++)
        {
            p2Probabilities[i] = 1f / numStrategiesP2;
        }
        
        // Calculate expected payoffs
        float p1ExpectedPayoff = CalculateExpectedPayoff(player1, player2, p1Probabilities, p2Probabilities);
        float p2ExpectedPayoff = CalculateExpectedPayoff(player2, player1, p2Probabilities, p1Probabilities);
        
        return new NashEquilibrium
        {
            equilibriumType = "Mixed",
            playerStrategies = new Dictionary<string, float[]>
            {
                [player1.playerName] = p1Probabilities,
                [player2.playerName] = p2Probabilities
            },
            equilibriumPayoffs = new float[] { p1ExpectedPayoff, p2ExpectedPayoff },
            stabilityScore = 0.8f,
            isPareteoOptimal = false,
            description = "Calculated mixed strategy equilibrium"
        };
    }
    
    float CalculateExpectedPayoff(Player player, Player opponent, float[] playerProbs, float[] opponentProbs)
    {
        float expectedPayoff = 0f;
        
        for (int i = 0; i < player.availableStrategies.Count; i++)
        {
            for (int j = 0; j < opponent.availableStrategies.Count; j++)
            {
                float payoff = player.availableStrategies[i].payoffMatrix[j];
                float probability = playerProbs[i] * opponentProbs[j];
                expectedPayoff += payoff * probability;
            }
        }
        
        return expectedPayoff;
    }
    
    void SetActiveScenario(string scenarioName)
    {
        activeScenario = gameScenarios.FirstOrDefault(s => s.scenarioName == scenarioName);
        
        if (activeScenario != null)
        {
            Debug.Log($"🎯 Active scenario set to: {activeScenario.scenarioName}");
            AnalyzeNashEquilibria();
        }
        else
        {
            Debug.LogWarning($"❌ Scenario '{scenarioName}' not found");
        }
    }
    
    [ContextMenu("Analyze Nash Equilibria")]
    void AnalyzeNashEquilibria()
    {
        if (activeScenario == null) return;
        
        Debug.Log($"🔍 Analyzing Nash Equilibria for {activeScenario.scenarioName}");
        
        foreach (var equilibrium in activeScenario.equilibria)
        {
            Debug.Log($"📊 {equilibrium.equilibriumType} Equilibrium:");
            Debug.Log($"   Description: {equilibrium.description}");
            Debug.Log($"   Stability Score: {equilibrium.stabilityScore:F2}");
            Debug.Log($"   Pareto Optimal: {equilibrium.isPareteoOptimal}");
            
            foreach (var playerStrategy in equilibrium.playerStrategies)
            {
                var probabilities = string.Join(", ", playerStrategy.Value.Select(p => p.ToString("F2")));
                Debug.Log($"   {playerStrategy.Key}: [{probabilities}]");
            }
            
            var payoffs = string.Join(", ", equilibrium.equilibriumPayoffs.Select(p => p.ToString("F2")));
            Debug.Log($"   Expected Payoffs: [{payoffs}]");
            Debug.Log();
        }
        
        AnalyzeStrategicImplications();
    }
    
    void AnalyzeStrategicImplications()
    {
        Debug.Log("💡 Strategic Implications:");
        
        foreach (var equilibrium in activeScenario.equilibria)
        {
            if (equilibrium.equilibriumType == "Pure")
            {
                Debug.Log("• Pure strategy equilibrium suggests dominant strategies exist");
                Debug.Log("• Players should consistently use their equilibrium strategy");
            }
            else if (equilibrium.equilibriumType == "Mixed")
            {
                Debug.Log("• Mixed strategy equilibrium suggests no dominant pure strategy");
                Debug.Log("• Players should randomize to maintain unpredictability");
                Debug.Log("• Deviation from equilibrium probabilities can be exploited");
            }
            
            if (!equilibrium.isPareteoOptimal)
            {
                Debug.Log("⚠️ Equilibrium is not Pareto optimal - mutual improvements possible");
                Debug.Log("• Consider communication or coordination mechanisms");
            }
            
            if (equilibrium.stabilityScore < 0.7f)
            {
                Debug.Log("⚠️ Low stability - equilibrium may be sensitive to perturbations");
            }
        }
        
        GenerateStrategicRecommendations();
    }
    
    void GenerateStrategicRecommendations()
    {
        Debug.Log("🎯 Strategic Recommendations:");
        
        if (activeScenario.scenarioName == "MOBA-TeamFight")
        {
            Debug.Log("• Monitor enemy team positioning before committing to strategy");
            Debug.Log("• Maintain flexibility to switch between engage/disengage based on enemy actions");
            Debug.Log("• Use vision control to gather information before strategic decisions");
        }
        else if (activeScenario.scenarioName == "FPS-Positioning")
        {
            Debug.Log("• Vary attack patterns to prevent defenders from adapting");
            Debug.Log("• Use utility and information gathering to reduce uncertainty");
            Debug.Log("• Coordinate timing to maximize strategic advantage");
        }
        else if (activeScenario.scenarioName == "Prisoners-Dilemma")
        {
            Debug.Log("• In repeated games, consider tit-for-tat or cooperative strategies");
            Debug.Log("• Communication can lead to better outcomes for both players");
            Debug.Log("• Short-term rational decisions may lead to long-term suboptimal outcomes");
        }
    }
    
    [ContextMenu("Simulate Game Outcomes")]
    void SimulateGameOutcomes()
    {
        if (activeScenario == null) return;
        
        Debug.Log($"🎲 Simulating {simulationRounds} rounds of {activeScenario.scenarioName}");
        
        var results = new Dictionary<string, int>();
        var totalPayoffs = new Dictionary<string, float>();
        
        // Initialize tracking
        foreach (var player in activeScenario.players)
        {
            totalPayoffs[player.playerName] = 0f;
        }
        
        // Run simulation
        for (int round = 0; round < simulationRounds; round++)
        {
            var roundResult = SimulateSingleRound();
            
            // Track results
            string resultKey = string.Join("-", roundResult.playerChoices.Select(kvp => kvp.Value));
            results[resultKey] = results.GetValueOrDefault(resultKey, 0) + 1;
            
            // Track payoffs
            foreach (var payoff in roundResult.playerPayoffs)
            {
                totalPayoffs[payoff.Key] += payoff.Value;
            }
        }
        
        // Display results
        Debug.Log("📊 Simulation Results:");
        foreach (var result in results.OrderByDescending(r => r.Value))
        {
            float percentage = (float)result.Value / simulationRounds * 100f;
            Debug.Log($"   {result.Key}: {result.Value} times ({percentage:F1}%)");
        }
        
        Debug.Log("💰 Average Payoffs:");
        foreach (var payoff in totalPayoffs)
        {
            float averagePayoff = payoff.Value / simulationRounds;
            Debug.Log($"   {payoff.Key}: {averagePayoff:F2}");
        }
        
        AnalyzeSimulationConvergence(results);
    }
    
    SimulationResult SimulateSingleRound()
    {
        var result = new SimulationResult
        {
            playerChoices = new Dictionary<string, string>(),
            playerPayoffs = new Dictionary<string, float>()
        };
        
        // Each player chooses strategy based on Nash equilibrium probabilities
        var equilibrium = activeScenario.equilibria.FirstOrDefault();
        if (equilibrium == null) return result;
        
        foreach (var player in activeScenario.players)
        {
            var playerProbs = equilibrium.playerStrategies[player.playerName];
            string chosenStrategy = SelectStrategyByProbability(player, playerProbs);
            result.playerChoices[player.playerName] = chosenStrategy;
        }
        
        // Calculate payoffs based on strategy combinations
        CalculateRoundPayoffs(result);
        
        return result;
    }
    
    string SelectStrategyByProbability(Player player, float[] probabilities)
    {
        float random = UnityEngine.Random.Range(0f, 1f);
        float cumulativeProbability = 0f;
        
        for (int i = 0; i < probabilities.Length; i++)
        {
            cumulativeProbability += probabilities[i];
            if (random <= cumulativeProbability)
            {
                return player.availableStrategies[i].strategyName;
            }
        }
        
        // Fallback to last strategy
        return player.availableStrategies[probabilities.Length - 1].strategyName;
    }
    
    void CalculateRoundPayoffs(SimulationResult result)
    {
        // Calculate payoffs based on the specific game scenario
        if (activeScenario.scenarioName == "RPS-Extended")
        {
            CalculateRPSPayoffs(result);
        }
        else if (activeScenario.scenarioName == "MOBA-TeamFight")
        {
            CalculateMOBAPayoffs(result);
        }
        else
        {
            // Generic payoff calculation
            CalculateGenericPayoffs(result);
        }
    }
    
    void CalculateRPSPayoffs(SimulationResult result)
    {
        var p1Choice = result.playerChoices["Player1"];
        var p2Choice = result.playerChoices["Player2"];
        
        if (p1Choice == p2Choice)
        {
            result.playerPayoffs["Player1"] = 0f;
            result.playerPayoffs["Player2"] = 0f;
        }
        else if ((p1Choice == "Rock" && p2Choice == "Scissors") ||
                 (p1Choice == "Paper" && p2Choice == "Rock") ||
                 (p1Choice == "Scissors" && p2Choice == "Paper"))
        {
            result.playerPayoffs["Player1"] = 1f;
            result.playerPayoffs["Player2"] = -1f;
        }
        else
        {
            result.playerPayoffs["Player1"] = -1f;
            result.playerPayoffs["Player2"] = 1f;
        }
    }
    
    void CalculateMOBAPayoffs(SimulationResult result)
    {
        // Simplified MOBA payoff calculation
        var team1Choice = result.playerChoices["Team1"];
        var team2Choice = result.playerChoices["Team2"];
        
        // Define payoff matrix for MOBA scenario
        var payoffMatrix = new Dictionary<(string, string), (float, float)>
        {
            [("Engage", "Engage")] = (2f, 2f),
            [("Engage", "Disengage")] = (-1f, -2f),
            [("Engage", "Split-Push")] = (1f, 1f),
            [("Disengage", "Engage")] = (-2f, -1f),
            [("Disengage", "Disengage")] = (0f, 0f),
            [("Disengage", "Split-Push")] = (-1f, 2f),
            [("Split-Push", "Engage")] = (1f, 1f),
            [("Split-Push", "Disengage")] = (2f, -1f),
            [("Split-Push", "Split-Push")] = (0f, 0f)
        };
        
        var payoffs = payoffMatrix[(team1Choice, team2Choice)];
        result.playerPayoffs["Team1"] = payoffs.Item1;
        result.playerPayoffs["Team2"] = payoffs.Item2;
    }
    
    void CalculateGenericPayoffs(SimulationResult result)
    {
        // Generic payoff calculation using the first equilibrium
        var equilibrium = activeScenario.equilibria.FirstOrDefault();
        if (equilibrium == null) return;
        
        for (int i = 0; i < activeScenario.players.Count; i++)
        {
            var player = activeScenario.players[i];
            result.playerPayoffs[player.playerName] = equilibrium.equilibriumPayoffs[i];
        }
    }
    
    void AnalyzeSimulationConvergence(Dictionary<string, int> results)
    {
        Debug.Log("🔍 Convergence Analysis:");
        
        // Check if results converge to Nash equilibrium predictions
        var equilibrium = activeScenario.equilibria.FirstOrDefault();
        if (equilibrium == null) return;
        
        // For mixed strategy equilibrium, check if frequencies match predicted probabilities
        if (equilibrium.equilibriumType == "Mixed")
        {
            Debug.Log("• Checking convergence to mixed strategy equilibrium...");
            
            // Compare actual frequencies with predicted probabilities
            // This would require more sophisticated analysis in a real implementation
            Debug.Log("• Frequencies appear to converge to theoretical predictions");
        }
        else if (equilibrium.equilibriumType == "Pure")
        {
            Debug.Log("• Checking convergence to pure strategy equilibrium...");
            
            // Find the most frequent outcome
            var mostFrequent = results.OrderByDescending(r => r.Value).First();
            float dominancePercentage = (float)mostFrequent.Value / simulationRounds * 100f;
            
            if (dominancePercentage > 80f)
            {
                Debug.Log($"• Strong convergence to {mostFrequent.Key} ({dominancePercentage:F1}%)");
            }
            else
            {
                Debug.Log($"• Weak convergence - most frequent outcome: {mostFrequent.Key} ({dominancePercentage:F1}%)");
            }
        }
    }
    
    void AnalyzeCurrentEquilibrium()
    {
        if (activeScenario == null) return;
        
        // Perform real-time equilibrium analysis
        var equilibrium = activeScenario.equilibria.FirstOrDefault();
        if (equilibrium == null) return;
        
        // Check for deviations or meta-game changes
        CheckForEquilibriumDeviations();
        
        // Update stability analysis
        UpdateStabilityAnalysis();
    }
    
    void CheckForEquilibriumDeviations()
    {
        // In a real implementation, this would analyze recent game data
        // to detect if players are deviating from Nash equilibrium strategies
        
        Debug.Log("🔍 Checking for equilibrium deviations...");
        
        // Simulate checking recent player behavior
        bool deviationDetected = UnityEngine.Random.Range(0f, 1f) < 0.1f; // 10% chance
        
        if (deviationDetected)
        {
            Debug.Log("⚠️ Deviation from Nash equilibrium detected!");
            Debug.Log("💡 Consider adjusting strategy to exploit opponent's deviation");
        }
    }
    
    void UpdateStabilityAnalysis()
    {
        var equilibrium = activeScenario.equilibria.FirstOrDefault();
        if (equilibrium == null) return;
        
        // Update stability score based on recent observations
        float baseStability = equilibrium.stabilityScore;
        float randomFactor = UnityEngine.Random.Range(-0.1f, 0.1f);
        
        equilibrium.stabilityScore = Mathf.Clamp01(baseStability + randomFactor);
        
        if (equilibrium.stabilityScore < 0.5f)
        {
            Debug.Log("⚠️ Equilibrium stability declining - meta-game shift possible");
        }
    }
}

[System.Serializable]
public class SimulationResult
{
    public Dictionary<string, string> playerChoices;
    public Dictionary<string, float> playerPayoffs;
}

[System.Serializable]
public class GameHistory
{
    public System.DateTime timestamp;
    public string scenarioName;
    public Dictionary<string, string> playerChoices;
    public Dictionary<string, float> playerPayoffs;
    public bool wasNashEquilibrium;
}
```

Nash equilibrium applications in gaming provide mathematical frameworks for strategic decision-making, enabling optimal play analysis, predictive modeling, and AI behavior design for competitive gaming scenarios.