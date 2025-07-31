# @03-Team Dynamics Analysis

## 🎯 Learning Objectives
- Master systematic approaches to analyzing competitive team performance
- Develop frameworks for evaluating team synergy, communication, and coordination
- Leverage AI tools for automated team analysis and strategic recommendations
- Build Unity-based systems for team performance visualization and coaching

## 🤝 Team Performance Framework

### Core Team Metrics System
**Comprehensive Team Analytics**:
```csharp
// TeamDynamicsAnalyzer.cs - Advanced team performance analysis system
using UnityEngine;
using System.Collections.Generic;
using System.Linq;

[System.Serializable]
public class TeamMember
{
    public string playerName;
    public string role;
    public string playStyle; // Aggressive, Passive, Supportive, Carry
    public float individualSkill;
    public float teamworkRating;
    public float communicationScore;
    public float adaptabilityScore;
    public List<string> championPool;
    public Dictionary<string, float> synergyRatings; // With other team members
}

[System.Serializable]
public class TeamComposition
{
    public List<TeamMember> members;
    public string teamName;
    public float overallSynergy;
    public float communicationEfficiency;
    public float strategicCoherence;
    public float adaptabilityFactor;
    public Dictionary<string, float> phaseStrengths; // Early, Mid, Late game
    public List<string> preferredStrategies;
    public List<TeamWeakness> identifiedWeaknesses;
}

[System.Serializable]
public class TeamPerformanceMetrics
{
    [Header("Win Conditions")]
    public float winRateOverall;
    public Dictionary<string, float> winRateByGameLength;
    public Dictionary<string, float> winRateByStrategy;
    public Dictionary<string, float> winRateVsTeamStyles;
    
    [Header("Team Coordination")]
    public float teamfightWinRate;
    public float objectiveControlRate;
    public float rotationEfficiency;
    public float visionControlScore;
    
    [Header("Communication Metrics")]
    public float callAccuracy;
    public float informationSharingRate;
    public float conflictResolutionTime;
    public float shotcallingClarity;
    
    [Header("Strategic Metrics")]
    public float draftSuccessRate;
    public float adaptationSpeed;
    public float counterStrategyEffectiveness;
    public float gameplanExecutionRate;
}

[System.Serializable]
public class TeamWeakness
{
    public string weaknessType;
    public string description;
    public float severity; // 0-10
    public List<string> affectedSituations;
    public string recommendedImprovement;
    public float improvementPriority;
}

public class TeamDynamicsAnalyzer : MonoBehaviour
{
    [Header("Analysis Configuration")]
    public string targetTeam = "Team Alpha";
    public int analysisWindowGames = 50;
    public float updateInterval = 1800f; // 30 minutes
    public bool enableRealTimeTracking = true;
    
    [Header("Data Sources")]
    public List<string> dataSourceAPIs;
    public bool includeVoiceCommsAnalysis = false;
    public bool trackIndividualContributions = true;
    
    private TeamComposition currentTeam;
    private TeamPerformanceMetrics performanceMetrics;
    private List<MatchAnalysis> recentMatches = new List<MatchAnalysis>();
    
    void Start()
    {
        InitializeTeamAnalysis();
        
        if (enableRealTimeTracking)
        {
            InvokeRepeating(nameof(UpdateTeamAnalysis), 0f, updateInterval);
        }
    }
    
    void InitializeTeamAnalysis()
    {
        Debug.Log($"🔍 Initializing team dynamics analysis for {targetTeam}");
        
        // Initialize team composition
        currentTeam = new TeamComposition
        {
            teamName = targetTeam,
            members = CreateSampleTeam(),
            preferredStrategies = new List<string>(),
            identifiedWeaknesses = new List<TeamWeakness>()
        };
        
        // Initialize performance metrics
        performanceMetrics = new TeamPerformanceMetrics
        {
            winRateByGameLength = new Dictionary<string, float>(),
            winRateByStrategy = new Dictionary<string, float>(),
            winRateVsTeamStyles = new Dictionary<string, float>()
        };
        
        currentTeam.phaseStrengths = new Dictionary<string, float>
        {
            ["Early Game"] = 0f,
            ["Mid Game"] = 0f,
            ["Late Game"] = 0f
        };
        
        CalculateInitialMetrics();
    }
    
    List<TeamMember> CreateSampleTeam()
    {
        return new List<TeamMember>
        {
            new TeamMember
            {
                playerName = "TopLaner",
                role = "Top",
                playStyle = "Aggressive",
                individualSkill = UnityEngine.Random.Range(7f, 9f),
                teamworkRating = UnityEngine.Random.Range(6f, 8f),
                communicationScore = UnityEngine.Random.Range(5f, 9f),
                adaptabilityScore = UnityEngine.Random.Range(6f, 8f),
                championPool = new List<string> { "Champion1", "Champion2", "Champion3" },
                synergyRatings = new Dictionary<string, float>()
            },
            new TeamMember
            {
                playerName = "Jungler",
                role = "Jungle",
                playStyle = "Supportive",
                individualSkill = UnityEngine.Random.Range(7f, 9f),
                teamworkRating = UnityEngine.Random.Range(7f, 9f),
                communicationScore = UnityEngine.Random.Range(7f, 9f),
                adaptabilityScore = UnityEngine.Random.Range(7f, 9f),
                championPool = new List<string> { "JungleChamp1", "JungleChamp2", "JungleChamp3" },
                synergyRatings = new Dictionary<string, float>()
            },
            new TeamMember
            {
                playerName = "MidLaner",
                role = "Mid",
                playStyle = "Carry",
                individualSkill = UnityEngine.Random.Range(8f, 10f),
                teamworkRating = UnityEngine.Random.Range(6f, 8f),
                communicationScore = UnityEngine.Random.Range(6f, 8f),
                adaptabilityScore = UnityEngine.Random.Range(7f, 9f),
                championPool = new List<string> { "MidChamp1", "MidChamp2", "MidChamp3" },
                synergyRatings = new Dictionary<string, float>()
            },
            new TeamMember
            {
                playerName = "ADCarry",
                role = "ADC",
                playStyle = "Passive",
                individualSkill = UnityEngine.Random.Range(7f, 9f),
                teamworkRating = UnityEngine.Random.Range(7f, 8f),
                communicationScore = UnityEngine.Random.Range(5f, 7f),
                adaptabilityScore = UnityEngine.Random.Range(6f, 8f),
                championPool = new List<string> { "ADCChamp1", "ADCChamp2", "ADCChamp3" },
                synergyRatings = new Dictionary<string, float>()
            },
            new TeamMember
            {
                playerName = "Support",
                role = "Support",
                playStyle = "Supportive",
                individualSkill = UnityEngine.Random.Range(6f, 8f),
                teamworkRating = UnityEngine.Random.Range(8f, 10f),
                communicationScore = UnityEngine.Random.Range(8f, 10f),
                adaptabilityScore = UnityEngine.Random.Range(7f, 9f),
                championPool = new List<string> { "SupportChamp1", "SupportChamp2", "SupportChamp3" },
                synergyRatings = new Dictionary<string, float>()
            }
        };
    }
    
    void CalculateInitialMetrics()
    {
        CalculateTeamSynergy();
        CalculateCommunicationEfficiency();
        CalculateStrategicCoherence();
        CalculatePhaseStrengths();
        
        Debug.Log($"✅ Initial team analysis complete for {targetTeam}");
    }
    
    [ContextMenu("Update Team Analysis")]
    void UpdateTeamAnalysis()
    {
        Debug.Log($"🔄 Updating team dynamics analysis...");
        
        // Collect recent match data
        CollectRecentMatchData();
        
        // Analyze team performance trends
        AnalyzePerformanceTrends();
        
        // Update synergy calculations
        UpdateSynergyMetrics();
        
        // Identify team weaknesses
        IdentifyTeamWeaknesses();
        
        // Generate strategic recommendations
        GenerateTeamRecommendations();
        
        Debug.Log($"✅ Team analysis updated - {recentMatches.Count} matches analyzed");
    }
    
    void CollectRecentMatchData()
    {
        // Simulate match data collection
        for (int i = 0; i < 5; i++) // Simulate 5 recent matches
        {
            var match = new MatchAnalysis
            {
                matchId = $"Match_{System.DateTime.Now.AddDays(-i):yyyyMMdd}_{i}",
                matchDate = System.DateTime.Now.AddDays(-i),
                victory = UnityEngine.Random.Range(0f, 1f) > 0.4f, // 60% win rate
                gameDuration = UnityEngine.Random.Range(20f, 45f),
                teamComposition = "Standard",
                strategy = GetRandomStrategy(),
                performanceScore = UnityEngine.Random.Range(6f, 9f),
                teamworkRating = UnityEngine.Random.Range(5f, 9f),
                communicationRating = UnityEngine.Random.Range(6f, 8f),
                keyMoments = GenerateKeyMoments(),
                weaknessesExposed = GenerateExposedWeaknesses()
            };
            
            recentMatches.Add(match);
        }
        
        // Keep only recent matches
        if (recentMatches.Count > analysisWindowGames)
        {
            recentMatches = recentMatches.OrderByDescending(m => m.matchDate)
                                       .Take(analysisWindowGames)
                                       .ToList();
        }
    }
    
    string GetRandomStrategy()
    {
        var strategies = new string[] { "Early Game Aggression", "Scale to Late", "Split Push", "Team Fight Focus", "Objective Control" };
        return strategies[UnityEngine.Random.Range(0, strategies.Length)];
    }
    
    List<string> GenerateKeyMoments()
    {
        var moments = new List<string>
        {
            "Strong early game coordination",
            "Mid game teamfight victory",
            "Successful baron control",
            "Late game positioning error",
            "Excellent communication in clutch moment"
        };
        
        return moments.Take(UnityEngine.Random.Range(2, 4)).ToList();
    }
    
    List<string> GenerateExposedWeaknesses()
    {
        var weaknesses = new List<string>
        {
            "Poor vision control",
            "Miscommunication in teamfights",
            "Slow adaptation to enemy strategy",
            "Individual positioning errors",
            "Draft phase indecision"
        };
        
        return weaknesses.Take(UnityEngine.Random.Range(0, 3)).ToList();
    }
    
    void AnalyzePerformanceTrends()
    {
        if (recentMatches.Count < 5) return;
        
        // Calculate win rates by different factors
        performanceMetrics.winRateOverall = recentMatches.Count(m => m.victory) / (float)recentMatches.Count;
        
        // Win rate by game length
        var shortGames = recentMatches.Where(m => m.gameDuration < 25f);
        var midGames = recentMatches.Where(m => m.gameDuration >= 25f && m.gameDuration < 35f);
        var longGames = recentMatches.Where(m => m.gameDuration >= 35f);
        
        performanceMetrics.winRateByGameLength["Short"] = shortGames.Any() ? shortGames.Count(m => m.victory) / (float)shortGames.Count() : 0f;
        performanceMetrics.winRateByGameLength["Mid"] = midGames.Any() ? midGames.Count(m => m.victory) / (float)midGames.Count() : 0f;
        performanceMetrics.winRateByGameLength["Long"] = longGames.Any() ? longGames.Count(m => m.victory) / (float)longGames.Count() : 0f;
        
        // Win rate by strategy
        var strategiesByType = recentMatches.GroupBy(m => m.strategy);
        foreach (var strategyGroup in strategiesByType)
        {
            var winRate = strategyGroup.Count(m => m.victory) / (float)strategyGroup.Count();
            performanceMetrics.winRateByStrategy[strategyGroup.Key] = winRate;
        }
        
        Debug.Log($"📊 Performance Analysis:");
        Debug.Log($"Overall Win Rate: {performanceMetrics.winRateOverall:P1}");
        Debug.Log($"Short Game Win Rate: {performanceMetrics.winRateByGameLength.GetValueOrDefault("Short", 0f):P1}");
        Debug.Log($"Long Game Win Rate: {performanceMetrics.winRateByGameLength.GetValueOrDefault("Long", 0f):P1}");
    }
    
    void CalculateTeamSynergy()
    {
        float totalSynergy = 0f;
        int synergyPairs = 0;
        
        // Calculate pairwise synergy between team members
        for (int i = 0; i < currentTeam.members.Count; i++)
        {
            for (int j = i + 1; j < currentTeam.members.Count; j++)
            {
                var member1 = currentTeam.members[i];
                var member2 = currentTeam.members[j];
                
                float synergy = CalculatePairSynergy(member1, member2);
                totalSynergy += synergy;
                synergyPairs++;
                
                // Store bilateral synergy ratings
                member1.synergyRatings[member2.playerName] = synergy;
                member2.synergyRatings[member1.playerName] = synergy;
            }
        }
        
        currentTeam.overallSynergy = totalSynergy / synergyPairs;
        
        Debug.Log($"🤝 Team Synergy: {currentTeam.overallSynergy:F2}/10");
    }
    
    float CalculatePairSynergy(TeamMember member1, TeamMember member2)
    {
        // Calculate synergy based on multiple factors
        float playStyleSynergy = CalculatePlayStyleSynergy(member1.playStyle, member2.playStyle);
        float communicationSynergy = (member1.communicationScore + member2.communicationScore) / 2f / 10f;
        float roleCompatibility = CalculateRoleCompatibility(member1.role, member2.role);
        
        // Weighted average
        float synergy = (playStyleSynergy * 0.4f + communicationSynergy * 0.3f + roleCompatibility * 0.3f) * 10f;
        
        return Mathf.Clamp(synergy, 0f, 10f);
    }
    
    float CalculatePlayStyleSynergy(string style1, string style2)
    {
        // Define synergy matrix for different play styles
        var synergyMatrix = new Dictionary<(string, string), float>
        {
            [("Aggressive", "Aggressive")] = 0.6f, // Can conflict
            [("Aggressive", "Supportive")] = 0.9f, // Great synergy
            [("Aggressive", "Carry")] = 0.7f, // Good synergy
            [("Aggressive", "Passive")] = 0.5f, // Potential conflict
            [("Supportive", "Supportive")] = 0.8f, // Good teamwork
            [("Supportive", "Carry")] = 0.95f, // Excellent synergy
            [("Supportive", "Passive")] = 0.7f, // Decent synergy
            [("Carry", "Carry")] = 0.4f, // Resource conflicts
            [("Carry", "Passive")] = 0.6f, // Moderate synergy
            [("Passive", "Passive")] = 0.5f // Lack of initiative
        };
        
        var key = (style1, style2);
        var reverseKey = (style2, style1);
        
        if (synergyMatrix.ContainsKey(key))
            return synergyMatrix[key];
        if (synergyMatrix.ContainsKey(reverseKey))
            return synergyMatrix[reverseKey];
        
        return 0.7f; // Default synergy
    }
    
    float CalculateRoleCompatibility(string role1, string role2)
    {
        // Define role compatibility matrix
        var compatibilityMatrix = new Dictionary<(string, string), float>
        {
            [("Top", "Jungle")] = 0.9f, // High synergy for ganks
            [("Top", "Mid")] = 0.7f, // Moderate synergy
            [("Top", "ADC")] = 0.6f, // Lower direct synergy
            [("Top", "Support")] = 0.5f, // Minimal direct synergy
            [("Jungle", "Mid")] = 0.85f, // High synergy for ganks
            [("Jungle", "ADC")] = 0.8f, // Good synergy for bot ganks
            [("Jungle", "Support")] = 0.8f, // Good synergy for vision/ganks
            [("Mid", "ADC")] = 0.7f, // Moderate synergy
            [("Mid", "Support")] = 0.6f, // Lower direct synergy
            [("ADC", "Support")] = 0.95f // Highest synergy (lane partners)
        };
        
        var key = (role1, role2);
        var reverseKey = (role2, role1);
        
        if (compatibilityMatrix.ContainsKey(key))
            return compatibilityMatrix[key];
        if (compatibilityMatrix.ContainsKey(reverseKey))
            return compatibilityMatrix[reverseKey];
        
        return 0.7f; // Default compatibility
    }
    
    void CalculateCommunicationEfficiency()
    {
        float avgCommunicationScore = currentTeam.members.Average(m => m.communicationScore);
        float communicationVariance = CalculateVariance(currentTeam.members.Select(m => m.communicationScore).ToList());
        
        // Lower variance means more consistent communication
        float consistencyFactor = Mathf.Clamp01(1f - (communicationVariance / 4f)); // Normalize variance
        
        currentTeam.communicationEfficiency = (avgCommunicationScore / 10f) * consistencyFactor;
        
        Debug.Log($"💬 Communication Efficiency: {currentTeam.communicationEfficiency:P1}");
    }
    
    void CalculateStrategicCoherence()
    {
        // Calculate how well the team's individual play styles align with team strategy
        float coherenceScore = 0f;
        
        // Analyze recent match strategies
        if (recentMatches.Any())
        {
            var recentTeamworkRatings = recentMatches.Select(m => m.teamworkRating).ToList();
            coherenceScore = recentTeamworkRatings.Average() / 10f;
        }
        else
        {
            // Use individual adaptability scores as proxy
            coherenceScore = currentTeam.members.Average(m => m.adaptabilityScore) / 10f;
        }
        
        currentTeam.strategicCoherence = coherenceScore;
        
        Debug.Log($"🎯 Strategic Coherence: {currentTeam.strategicCoherence:P1}");
    }
    
    void CalculatePhaseStrengths()
    {
        // Analyze team composition strengths by game phase
        float earlyGameStrength = 0f;
        float midGameStrength = 0f;
        float lateGameStrength = 0f;
        
        foreach (var member in currentTeam.members)
        {
            // Assign phase strengths based on role and play style
            switch (member.role)
            {
                case "Top":
                    earlyGameStrength += member.playStyle == "Aggressive" ? 0.3f : 0.1f;
                    midGameStrength += 0.2f;
                    lateGameStrength += member.playStyle == "Carry" ? 0.3f : 0.15f;
                    break;
                    
                case "Jungle":
                    earlyGameStrength += 0.4f; // Junglers typically strong early
                    midGameStrength += 0.3f;
                    lateGameStrength += 0.2f;
                    break;
                    
                case "Mid":
                    earlyGameStrength += 0.2f;
                    midGameStrength += 0.4f; // Mid laners peak mid game
                    lateGameStrength += member.playStyle == "Carry" ? 0.4f : 0.2f;
                    break;
                    
                case "ADC":
                    earlyGameStrength += 0.1f;
                    midGameStrength += 0.2f;
                    lateGameStrength += 0.5f; // ADCs scale to late game
                    break;
                    
                case "Support":
                    earlyGameStrength += 0.3f; // Supports strong early for lane
                    midGameStrength += 0.25f;
                    lateGameStrength += 0.2f;
                    break;
            }
        }
        
        currentTeam.phaseStrengths["Early Game"] = Mathf.Clamp01(earlyGameStrength);
        currentTeam.phaseStrengths["Mid Game"] = Mathf.Clamp01(midGameStrength);
        currentTeam.phaseStrengths["Late Game"] = Mathf.Clamp01(lateGameStrength);
        
        Debug.Log($"⏰ Phase Strengths - Early: {currentTeam.phaseStrengths["Early Game"]:P0}, " +
                 $"Mid: {currentTeam.phaseStrengths["Mid Game"]:P0}, " +
                 $"Late: {currentTeam.phaseStrengths["Late Game"]:P0}");
    }
    
    void UpdateSynergyMetrics()
    {
        // Recalculate synergy based on recent performance
        CalculateTeamSynergy();
        CalculateCommunicationEfficiency();
        CalculateStrategicCoherence();
        
        // Update adaptability factor based on recent matches
        if (recentMatches.Any())
        {
            var recentAdaptability = recentMatches
                .SelectMany(m => m.keyMoments)
                .Count(moment => moment.Contains("adaptation") || moment.Contains("adjust")) / (float)recentMatches.Count;
            
            currentTeam.adaptabilityFactor = recentAdaptability;
        }
    }
    
    void IdentifyTeamWeaknesses()
    {
        currentTeam.identifiedWeaknesses.Clear();
        
        // Analyze communication weaknesses
        if (currentTeam.communicationEfficiency < 0.7f)
        {
            currentTeam.identifiedWeaknesses.Add(new TeamWeakness
            {
                weaknessType = "Communication",
                description = "Team communication efficiency below optimal level",
                severity = (0.7f - currentTeam.communicationEfficiency) * 10f,
                affectedSituations = new List<string> { "Teamfights", "Objective control", "Rotations" },
                recommendedImprovement = "Practice structured communication protocols and callouts",
                improvementPriority = 8f
            });
        }
        
        // Analyze synergy weaknesses
        if (currentTeam.overallSynergy < 7f)
        {
            currentTeam.identifiedWeaknesses.Add(new TeamWeakness
            {
                weaknessType = "Team Synergy",
                description = "Low synergy between team members affecting coordination",
                severity = (7f - currentTeam.overallSynergy),
                affectedSituations = new List<string> { "Team coordination", "Strategic execution" },
                recommendedImprovement = "Team building exercises and coordinated practice sessions",
                improvementPriority = 7f
            });
        }
        
        // Analyze phase-specific weaknesses
        var weakestPhase = currentTeam.phaseStrengths.OrderBy(p => p.Value).First();
        if (weakestPhase.Value < 0.6f)
        {
            currentTeam.identifiedWeaknesses.Add(new TeamWeakness
            {
                weaknessType = "Phase Weakness",
                description = $"Team struggles during {weakestPhase.Key} phase",
                severity = (0.6f - weakestPhase.Value) * 10f,
                affectedSituations = new List<string> { $"{weakestPhase.Key} strategy execution" },
                recommendedImprovement = $"Focus practice on {weakestPhase.Key} scenarios and strategies",
                improvementPriority = 6f
            });
        }
        
        // Analyze match-specific weaknesses
        if (recentMatches.Any())
        {
            var commonWeaknesses = recentMatches
                .SelectMany(m => m.weaknessesExposed)
                .GroupBy(w => w)
                .Where(g => g.Count() >= recentMatches.Count * 0.4f) // Appears in 40%+ of matches
                .Select(g => g.Key);
            
            foreach (var weakness in commonWeaknesses)
            {
                currentTeam.identifiedWeaknesses.Add(new TeamWeakness
                {
                    weaknessType = "Recurring Issue",
                    description = weakness,
                    severity = 6f,
                    affectedSituations = new List<string> { "Match performance" },
                    recommendedImprovement = GenerateImprovementSuggestion(weakness),
                    improvementPriority = 7f
                });
            }
        }
        
        Debug.Log($"⚠️ Identified {currentTeam.identifiedWeaknesses.Count} team weaknesses");
    }
    
    string GenerateImprovementSuggestion(string weakness)
    {
        var suggestions = new Dictionary<string, string>
        {
            ["Poor vision control"] = "Implement structured ward placement drills and vision timing practice",
            ["Miscommunication in teamfights"] = "Practice teamfight scenarios with clear communication protocols",
            ["Slow adaptation to enemy strategy"] = "Study opponent analysis and practice counter-strategy execution",
            ["Individual positioning errors"] = "Individual coaching sessions and positioning review",
            ["Draft phase indecision"] = "Develop draft preparation strategies and backup plans"
        };
        
        return suggestions.ContainsKey(weakness) ? suggestions[weakness] : "Targeted practice and coaching focus needed";
    }
    
    void GenerateTeamRecommendations()
    {
        Debug.Log("💡 Team Improvement Recommendations:");
        
        // Prioritize weaknesses by severity and improvement priority
        var prioritizedWeaknesses = currentTeam.identifiedWeaknesses
            .OrderByDescending(w => w.severity * w.improvementPriority)
            .Take(3);
        
        int priority = 1;
        foreach (var weakness in prioritizedWeaknesses)
        {
            Debug.Log($"{priority}. {weakness.weaknessType} (Severity: {weakness.severity:F1}/10)");
            Debug.Log($"   Issue: {weakness.description}");
            Debug.Log($"   Solution: {weakness.recommendedImprovement}");
            Debug.Log();
            priority++;
        }
        
        // Generate strategic recommendations
        GenerateStrategicRecommendations();
    }
    
    void GenerateStrategicRecommendations()
    {
        Debug.Log("🎯 Strategic Recommendations:");
        
        // Recommend strategies based on team strengths
        var strongestPhase = currentTeam.phaseStrengths.OrderByDescending(p => p.Value).First();
        
        Debug.Log($"• Focus on {strongestPhase.Key} strategies (Team strength: {strongestPhase.Value:P0})");
        
        if (currentTeam.overallSynergy > 8f)
        {
            Debug.Log("• Leverage high team synergy with coordinated team-fight strategies");
        }
        
        if (currentTeam.communicationEfficiency > 0.8f)
        {
            Debug.Log("• Utilize strong communication for complex rotational plays");
        }
        
        // Recommend based on recent performance
        if (recentMatches.Any())
        {
            var bestStrategy = performanceMetrics.winRateByStrategy
                .OrderByDescending(s => s.Value)
                .FirstOrDefault();
            
            if (!string.IsNullOrEmpty(bestStrategy.Key))
            {
                Debug.Log($"• Continue focusing on '{bestStrategy.Key}' strategy (Win rate: {bestStrategy.Value:P1})");
            }
        }
    }
    
    float CalculateVariance(List<float> values)
    {
        if (values.Count <= 1) return 0f;
        
        float mean = values.Average();
        float variance = values.Sum(x => Mathf.Pow(x - mean, 2)) / values.Count;
        return variance;
    }
    
    [ContextMenu("Generate Team Report")]
    void GenerateTeamReport()
    {
        var report = new System.Text.StringBuilder();
        report.AppendLine($"🏆 Team Dynamics Analysis Report: {targetTeam}");
        report.AppendLine($"Generated: {System.DateTime.Now}");
        report.AppendLine($"Analysis Window: {analysisWindowGames} games");
        report.AppendLine();
        
        // Team Overview
        report.AppendLine("## Team Overview");
        report.AppendLine($"Overall Synergy: {currentTeam.overallSynergy:F1}/10");
        report.AppendLine($"Communication Efficiency: {currentTeam.communicationEfficiency:P1}");
        report.AppendLine($"Strategic Coherence: {currentTeam.strategicCoherence:P1}");
        report.AppendLine();
        
        // Performance Metrics
        report.AppendLine("## Performance Metrics");
        report.AppendLine($"Overall Win Rate: {performanceMetrics.winRateOverall:P1}");
        
        foreach (var gameLength in performanceMetrics.winRateByGameLength)
        {
            report.AppendLine($"{gameLength.Key} Game Win Rate: {gameLength.Value:P1}");
        }
        report.AppendLine();
        
        // Phase Strengths
        report.AppendLine("## Phase Strengths");
        foreach (var phase in currentTeam.phaseStrengths.OrderByDescending(p => p.Value))
        {
            report.AppendLine($"{phase.Key}: {phase.Value:P0}");
        }
        report.AppendLine();
        
        // Team Members
        report.AppendLine("## Team Member Analysis");
        foreach (var member in currentTeam.members)
        {
            report.AppendLine($"### {member.playerName} ({member.role})");
            report.AppendLine($"- Play Style: {member.playStyle}");
            report.AppendLine($"- Individual Skill: {member.individualSkill:F1}/10");
            report.AppendLine($"- Teamwork Rating: {member.teamworkRating:F1}/10");
            report.AppendLine($"- Communication: {member.communicationScore:F1}/10");
            report.AppendLine();
        }
        
        // Identified Weaknesses
        if (currentTeam.identifiedWeaknesses.Any())
        {
            report.AppendLine("## Identified Weaknesses");
            foreach (var weakness in currentTeam.identifiedWeaknesses.OrderByDescending(w => w.severity))
            {
                report.AppendLine($"### {weakness.weaknessType} (Severity: {weakness.severity:F1}/10)");
                report.AppendLine($"**Issue:** {weakness.description}");
                report.AppendLine($"**Recommendation:** {weakness.recommendedImprovement}");
                report.AppendLine($"**Priority:** {weakness.improvementPriority:F1}/10");
                report.AppendLine();
            }
        }
        
        // Save report
        var fileName = $"team_analysis_{targetTeam}_{System.DateTime.Now:yyyyMMdd}.md";
        var filePath = System.IO.Path.Combine(Application.persistentDataPath, fileName);
        System.IO.File.WriteAllText(filePath, report.ToString());
        
        Debug.Log($"📄 Team analysis report saved to: {filePath}");
    }
}

[System.Serializable]
public class MatchAnalysis
{
    public string matchId;
    public System.DateTime matchDate;
    public bool victory;
    public float gameDuration;
    public string teamComposition;
    public string strategy;
    public float performanceScore;
    public float teamworkRating;
    public float communicationRating;
    public List<string> keyMoments;
    public List<string> weaknessesExposed;
}
```

Team dynamics analysis provides comprehensive frameworks for evaluating competitive team performance, identifying coordination strengths and weaknesses, and generating data-driven recommendations for strategic improvement and optimal team synergy development.