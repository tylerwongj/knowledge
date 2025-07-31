# @02-Player Performance Analytics

## 🎯 Learning Objectives
- Master systematic approaches to analyzing individual player performance
- Develop data-driven frameworks for skill assessment and improvement tracking
- Leverage AI tools for automated performance analysis and coaching insights
- Build Unity-based analytics systems for competitive gaming applications

## 📊 Performance Metrics Framework

### Core Performance Indicators
**Player Analytics System**:
```csharp
// PlayerPerformanceAnalyzer.cs - Comprehensive player analytics framework
using UnityEngine;
using System.Collections.Generic;
using System.Linq;

[System.Serializable]
public class PlayerMetrics
{
    [Header("Basic Stats")]
    public string playerName;
    public string gameTitle;
    public string role;
    public int gamesPlayed;
    public float winRate;
    public float averageGameDuration;
    
    [Header("Mechanical Skills")]
    public float averageAPM; // Actions Per Minute
    public float accuracyPercentage;
    public float reactionTime;
    public float mechanicalConsistency;
    
    [Header("Strategic Performance")]
    public float decisionMakingScore;
    public float mapAwarenessRating;
    public float objectiveControl;
    public float teamfightPositioning;
    
    [Header("Mental Performance")]
    public float clutchPerformance;
    public float tiltResistance;
    public float adaptabilityScore;
    public float communicationRating;
    
    [Header("Game-Specific Stats")]
    public Dictionary<string, float> gameSpecificMetrics;
    public List<PerformanceTrend> trends;
    public List<MatchPerformance> recentMatches;
}

[System.Serializable]
public class PerformanceTrend
{
    public string metricName;
    public List<float> values;
    public List<System.DateTime> timestamps;
    public float trendDirection; // -1 to 1 (declining to improving)
    public float confidence; // 0 to 1
}

[System.Serializable]
public class MatchPerformance
{
    public System.DateTime matchDate;
    public string opponent;
    public bool victory;
    public float performanceScore;
    public Dictionary<string, float> matchMetrics;
    public List<string> notableEvents;
    public string performanceSummary;
}

public class PlayerPerformanceAnalyzer : MonoBehaviour
{
    [Header("Analysis Settings")]
    public string targetPlayer = "Player1";
    public int analysisWindowDays = 30;
    public float updateInterval = 300f; // 5 minutes
    public bool enableRealTimeTracking = true;
    
    [Header("Game Integration")]
    public string gameAPIEndpoint;
    public string apiKey;
    public List<string> trackedMetrics;
    
    private PlayerMetrics currentMetrics;
    private List<PlayerMetrics> historicalData = new List<PlayerMetrics>();
    
    void Start()
    {
        InitializeMetrics();
        
        if (enableRealTimeTracking)
        {
            InvokeRepeating(nameof(UpdatePerformanceMetrics), 0f, updateInterval);
        }
    }
    
    void InitializeMetrics()
    {
        currentMetrics = new PlayerMetrics
        {
            playerName = targetPlayer,
            gameSpecificMetrics = new Dictionary<string, float>(),
            trends = new List<PerformanceTrend>(),
            recentMatches = new List<MatchPerformance>()
        };
        
        // Initialize tracked metrics
        foreach (var metric in trackedMetrics)
        {
            currentMetrics.gameSpecificMetrics[metric] = 0f;
            
            currentMetrics.trends.Add(new PerformanceTrend
            {
                metricName = metric,
                values = new List<float>(),
                timestamps = new List<System.DateTime>(),
                trendDirection = 0f,
                confidence = 0f
            });
        }
        
        Debug.Log($"📊 Initialized performance tracking for {targetPlayer}");
    }
    
    [ContextMenu("Update Performance Metrics")]
    void UpdatePerformanceMetrics()
    {
        Debug.Log($"🔄 Updating performance metrics for {targetPlayer}...");
        
        // Collect current performance data
        CollectBasicStats();
        CollectMechanicalMetrics();
        CollectStrategicMetrics();
        CollectMentalPerformanceMetrics();
        CollectGameSpecificData();
        
        // Analyze trends
        AnalyzeTrends();
        
        // Generate insights
        GeneratePerformanceInsights();
        
        // Store historical data
        var snapshot = JsonUtility.FromJson<PlayerMetrics>(JsonUtility.ToJson(currentMetrics));
        historicalData.Add(snapshot);
        
        // Maintain data window
        MaintainDataWindow();
    }
    
    void CollectBasicStats()
    {
        // In real implementation, collect from game API
        currentMetrics.gamesPlayed = UnityEngine.Random.Range(100, 1000);
        currentMetrics.winRate = UnityEngine.Random.Range(0.4f, 0.7f);
        currentMetrics.averageGameDuration = UnityEngine.Random.Range(25f, 45f);
        
        Debug.Log($"Basic stats - Games: {currentMetrics.gamesPlayed}, Win Rate: {currentMetrics.winRate:P1}");
    }
    
    void CollectMechanicalMetrics()
    {
        // Simulate mechanical skill collection
        currentMetrics.averageAPM = UnityEngine.Random.Range(150f, 400f);
        currentMetrics.accuracyPercentage = UnityEngine.Random.Range(0.6f, 0.95f);
        currentMetrics.reactionTime = UnityEngine.Random.Range(150f, 250f); // milliseconds
        currentMetrics.mechanicalConsistency = UnityEngine.Random.Range(0.7f, 0.95f);
        
        Debug.Log($"Mechanical - APM: {currentMetrics.averageAPM:F0}, Accuracy: {currentMetrics.accuracyPercentage:P1}");
    }
    
    void CollectStrategicMetrics()
    {
        // Simulate strategic performance collection
        currentMetrics.decisionMakingScore = UnityEngine.Random.Range(6f, 10f);
        currentMetrics.mapAwarenessRating = UnityEngine.Random.Range(5f, 10f);
        currentMetrics.objectiveControl = UnityEngine.Random.Range(0.4f, 0.9f);
        currentMetrics.teamfightPositioning = UnityEngine.Random.Range(6f, 10f);
        
        Debug.Log($"Strategic - Decision Making: {currentMetrics.decisionMakingScore:F1}/10");
    }
    
    void CollectMentalPerformanceMetrics()
    {
        // Simulate mental performance collection
        currentMetrics.clutchPerformance = UnityEngine.Random.Range(0.5f, 1.0f);
        currentMetrics.tiltResistance = UnityEngine.Random.Range(0.6f, 0.95f);
        currentMetrics.adaptabilityScore = UnityEngine.Random.Range(6f, 10f);
        currentMetrics.communicationRating = UnityEngine.Random.Range(5f, 10f);
        
        Debug.Log($"Mental - Clutch: {currentMetrics.clutchPerformance:P1}, Tilt Resistance: {currentMetrics.tiltResistance:P1}");
    }
    
    void CollectGameSpecificData()
    {
        // Collect game-specific metrics
        foreach (var metric in trackedMetrics)
        {
            float value = UnityEngine.Random.Range(0f, 100f);
            currentMetrics.gameSpecificMetrics[metric] = value;
            
            // Update trend data
            var trend = currentMetrics.trends.FirstOrDefault(t => t.metricName == metric);
            if (trend != null)
            {
                trend.values.Add(value);
                trend.timestamps.Add(System.DateTime.Now);
                
                // Keep trend data manageable
                if (trend.values.Count > 100)
                {
                    trend.values.RemoveAt(0);
                    trend.timestamps.RemoveAt(0);
                }
            }
        }
    }
    
    void AnalyzeTrends()
    {
        foreach (var trend in currentMetrics.trends)
        {
            if (trend.values.Count < 5) continue;
            
            // Calculate trend direction using linear regression
            var recentValues = trend.values.TakeLast(10).ToList();
            trend.trendDirection = CalculateTrendDirection(recentValues);
            trend.confidence = CalculateTrendConfidence(recentValues);
            
            // Log significant trends
            if (Mathf.Abs(trend.trendDirection) > 0.3f && trend.confidence > 0.6f)
            {
                string direction = trend.trendDirection > 0 ? "improving" : "declining";
                Debug.Log($"📈 {trend.metricName} is {direction} (confidence: {trend.confidence:P0})");
            }
        }
    }
    
    float CalculateTrendDirection(List<float> values)
    {
        if (values.Count < 2) return 0f;
        
        // Simple linear regression slope calculation
        float n = values.Count;
        float sumX = 0f, sumY = 0f, sumXY = 0f, sumX2 = 0f;
        
        for (int i = 0; i < values.Count; i++)
        {
            float x = i;
            float y = values[i];
            
            sumX += x;
            sumY += y;
            sumXY += x * y;
            sumX2 += x * x;
        }
        
        float slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
        
        // Normalize slope to -1 to 1 range
        return Mathf.Clamp(slope / 10f, -1f, 1f);
    }
    
    float CalculateTrendConfidence(List<float> values)
    {
        if (values.Count < 3) return 0f;
        
        float variance = CalculateVariance(values);
        float maxVariance = 100f; // Adjust based on metric scale
        
        // Higher confidence for lower variance (more consistent trend)
        return Mathf.Clamp01(1f - (variance / maxVariance));
    }
    
    float CalculateVariance(List<float> values)
    {
        float mean = values.Average();
        float variance = values.Sum(x => Mathf.Pow(x - mean, 2)) / values.Count;
        return variance;
    }
    
    void GeneratePerformanceInsights()
    {
        Debug.Log($"💡 Performance Insights for {targetPlayer}:");
        
        // Identify strengths and weaknesses
        var strengths = new List<string>();
        var weaknesses = new List<string>();
        
        // Analyze mechanical performance
        if (currentMetrics.averageAPM > 300f)
            strengths.Add("High mechanical speed");
        else if (currentMetrics.averageAPM < 200f)
            weaknesses.Add("Low actions per minute");
        
        if (currentMetrics.accuracyPercentage > 0.85f)
            strengths.Add("Excellent accuracy");
        else if (currentMetrics.accuracyPercentage < 0.7f)
            weaknesses.Add("Accuracy needs improvement");
        
        // Analyze strategic performance
        if (currentMetrics.decisionMakingScore > 8.5f)
            strengths.Add("Strong decision making");
        else if (currentMetrics.decisionMakingScore < 7f)
            weaknesses.Add("Decision making inconsistency");
        
        // Analyze mental performance
        if (currentMetrics.clutchPerformance > 0.8f)
            strengths.Add("Excellent clutch performance");
        else if (currentMetrics.clutchPerformance < 0.6f)
            weaknesses.Add("Struggles in clutch situations");
        
        // Log insights
        if (strengths.Any())
        {
            Debug.Log($"💪 Strengths: {string.Join(", ", strengths)}");
        }
        
        if (weaknesses.Any())
        {
            Debug.Log($"⚠️ Areas for improvement: {string.Join(", ", weaknesses)}");
        }
        
        // Generate improvement recommendations
        GenerateImprovementRecommendations();
    }
    
    void GenerateImprovementRecommendations()
    {
        var recommendations = new List<string>();
        
        // Mechanical skill recommendations
        if (currentMetrics.averageAPM < 250f)
        {
            recommendations.Add("Practice APM training exercises to improve mechanical speed");
        }
        
        if (currentMetrics.accuracyPercentage < 0.8f)
        {
            recommendations.Add("Focus on precision over speed in aim training");
        }
        
        // Strategic recommendations
        if (currentMetrics.mapAwarenessRating < 7f)
        {
            recommendations.Add("Practice minimap awareness drills");
        }
        
        if (currentMetrics.objectiveControl < 0.6f)
        {
            recommendations.Add("Study objective timing and team coordination");
        }
        
        // Mental performance recommendations
        if (currentMetrics.tiltResistance < 0.7f)
        {
            recommendations.Add("Work on mental resilience and tilt management");
        }
        
        if (currentMetrics.communicationRating < 7f)
        {
            recommendations.Add("Practice clear and concise team communication");
        }
        
        Debug.Log($"📋 Improvement Recommendations:");
        foreach (var recommendation in recommendations.Take(3)) // Top 3 recommendations
        {
            Debug.Log($"  • {recommendation}");
        }
    }
    
    void MaintainDataWindow()
    {
        var cutoffDate = System.DateTime.Now.AddDays(-analysisWindowDays);
        historicalData = historicalData.Where(d => d.recentMatches.Any() && 
            d.recentMatches.Last().matchDate > cutoffDate).ToList();
        
        Debug.Log($"📚 Maintaining {historicalData.Count} historical data points");
    }
    
    [ContextMenu("Generate Performance Report")]
    void GeneratePerformanceReport()
    {
        var report = new System.Text.StringBuilder();
        report.AppendLine($"🏆 Performance Report: {targetPlayer}");
        report.AppendLine($"Generated: {System.DateTime.Now}");
        report.AppendLine($"Analysis Period: {analysisWindowDays} days");
        report.AppendLine();
        
        // Basic statistics
        report.AppendLine("## Basic Statistics");
        report.AppendLine($"Games Played: {currentMetrics.gamesPlayed}");
        report.AppendLine($"Win Rate: {currentMetrics.winRate:P1}");
        report.AppendLine($"Average Game Duration: {currentMetrics.averageGameDuration:F1} minutes");
        report.AppendLine();
        
        // Performance breakdown
        report.AppendLine("## Performance Breakdown");
        
        report.AppendLine("### Mechanical Skills");
        report.AppendLine($"- APM: {currentMetrics.averageAPM:F0}");
        report.AppendLine($"- Accuracy: {currentMetrics.accuracyPercentage:P1}");
        report.AppendLine($"- Reaction Time: {currentMetrics.reactionTime:F0}ms");
        report.AppendLine($"- Consistency: {currentMetrics.mechanicalConsistency:P1}");
        report.AppendLine();
        
        report.AppendLine("### Strategic Performance");
        report.AppendLine($"- Decision Making: {currentMetrics.decisionMakingScore:F1}/10");
        report.AppendLine($"- Map Awareness: {currentMetrics.mapAwarenessRating:F1}/10");
        report.AppendLine($"- Objective Control: {currentMetrics.objectiveControl:P1}");
        report.AppendLine($"- Teamfight Positioning: {currentMetrics.teamfightPositioning:F1}/10");
        report.AppendLine();
        
        report.AppendLine("### Mental Performance");
        report.AppendLine($"- Clutch Performance: {currentMetrics.clutchPerformance:P1}");
        report.AppendLine($"- Tilt Resistance: {currentMetrics.tiltResistance:P1}");
        report.AppendLine($"- Adaptability: {currentMetrics.adaptabilityScore:F1}/10");
        report.AppendLine($"- Communication: {currentMetrics.communicationRating:F1}/10");
        report.AppendLine();
        
        // Trends analysis
        report.AppendLine("## Performance Trends");
        foreach (var trend in currentMetrics.trends.Where(t => t.confidence > 0.5f))
        {
            string direction = trend.trendDirection > 0 ? "↗️ Improving" : "↘️ Declining";
            report.AppendLine($"- {trend.metricName}: {direction} (confidence: {trend.confidence:P0})");
        }
        report.AppendLine();
        
        // Save report
        var fileName = $"performance_report_{targetPlayer}_{System.DateTime.Now:yyyyMMdd}.md";
        var filePath = System.IO.Path.Combine(Application.persistentDataPath, fileName);
        System.IO.File.WriteAllText(filePath, report.ToString());
        
        Debug.Log($"📄 Performance report saved to: {filePath}");
    }
}
```

### Advanced Skill Assessment
**Multi-Dimensional Skill Evaluation**:
```csharp
// SkillAssessmentEngine.cs
using UnityEngine;
using System.Collections.Generic;
using System.Linq;

[System.Serializable]
public class SkillCategory
{
    public string categoryName;
    public float weight; // Importance weighting
    public List<SkillMetric> metrics;
    public float overallScore;
    public string proficiencyLevel; // Beginner, Intermediate, Advanced, Expert, Master
}

[System.Serializable]
public class SkillMetric
{
    public string metricName;
    public float currentValue;
    public float benchmarkValue; // Professional/top-tier benchmark
    public float weight;
    public float normalizedScore; // 0-100
    public string description;
}

public class SkillAssessmentEngine : MonoBehaviour
{
    [Header("Assessment Configuration")]
    public string gameTitle = "League of Legends";
    public string role = "ADC";
    public List<SkillCategory> skillCategories;
    
    [Header("Benchmarking")]
    public bool useProfessionalBenchmarks = true;
    public string benchmarkTier = "Challenger";
    
    private Dictionary<string, float> roleBenchmarks;
    
    void Start()
    {
        InitializeSkillCategories();
        LoadBenchmarkData();
    }
    
    void InitializeSkillCategories()
    {
        skillCategories = new List<SkillCategory>();
        
        // Mechanical Skills Category
        var mechanicalSkills = new SkillCategory
        {
            categoryName = "Mechanical Skills",
            weight = 0.3f,
            metrics = new List<SkillMetric>
            {
                new SkillMetric
                {
                    metricName = "Last Hitting Accuracy",
                    weight = 0.25f,
                    benchmarkValue = 90f,
                    description = "Ability to farm minions efficiently"
                },
                new SkillMetric
                {
                    metricName = "Skill Shot Accuracy",
                    weight = 0.25f,
                    benchmarkValue = 75f,
                    description = "Accuracy of aimed abilities"
                },
                new SkillMetric
                {
                    metricName = "Kiting Efficiency",
                    weight = 0.25f,
                    benchmarkValue = 85f,
                    description = "Attack-move efficiency in combat"
                },
                new SkillMetric
                {
                    metricName = "Reaction Time",
                    weight = 0.25f,
                    benchmarkValue = 180f, // Lower is better
                    description = "Response time to threats (ms)"
                }
            }
        };
        
        // Game Knowledge Category
        var gameKnowledge = new SkillCategory
        {
            categoryName = "Game Knowledge",
            weight = 0.25f,
            metrics = new List<SkillMetric>
            {
                new SkillMetric
                {
                    metricName = "Champion Matchup Knowledge",
                    weight = 0.3f,
                    benchmarkValue = 85f,
                    description = "Understanding of champion interactions"
                },
                new SkillMetric
                {
                    metricName = "Item Build Efficiency",
                    weight = 0.25f,
                    benchmarkValue = 90f,
                    description = "Optimal itemization choices"
                },
                new SkillMetric
                {
                    metricName = "Map Awareness",
                    weight = 0.25f,
                    benchmarkValue = 80f,
                    description = "Minimap usage and positioning"
                },
                new SkillMetric
                {
                    metricName = "Objective Priority",
                    weight = 0.2f,
                    benchmarkValue = 85f,
                    description = "Understanding objective importance"
                }
            }
        };
        
        // Strategic Thinking Category
        var strategicThinking = new SkillCategory
        {
            categoryName = "Strategic Thinking",
            weight = 0.25f,
            metrics = new List<SkillMetric>
            {
                new SkillMetric
                {
                    metricName = "Decision Making Speed",
                    weight = 0.3f,
                    benchmarkValue = 80f,
                    description = "Quick and effective decision making"
                },
                new SkillMetric
                {
                    metricName = "Risk Assessment",
                    weight = 0.25f,
                    benchmarkValue = 85f,
                    description = "Ability to evaluate risk vs reward"
                },
                new SkillMetric
                {
                    metricName = "Team Coordination",
                    weight = 0.25f,
                    benchmarkValue = 75f,
                    description = "Synergy with team members"
                },
                new SkillMetric
                {
                    metricName = "Adaptation Speed",
                    weight = 0.2f,
                    benchmarkValue = 80f,
                    description = "Adjusting to changing game states"
                }
            }
        };
        
        // Mental Performance Category
        var mentalPerformance = new SkillCategory
        {
            categoryName = "Mental Performance",
            weight = 0.2f,
            metrics = new List<SkillMetric>
            {
                new SkillMetric
                {
                    metricName = "Consistency",
                    weight = 0.3f,
                    benchmarkValue = 85f,
                    description = "Performance stability across games"
                },
                new SkillMetric
                {
                    metricName = "Pressure Handling",
                    weight = 0.25f,
                    benchmarkValue = 80f,
                    description = "Performance under pressure"
                },
                new SkillMetric
                {
                    metricName = "Tilt Resistance",
                    weight = 0.25f,
                    benchmarkValue = 75f,
                    description = "Emotional control during setbacks"
                },
                new SkillMetric
                {
                    metricName = "Focus Duration",
                    weight = 0.2f,
                    benchmarkValue = 90f,
                    description = "Maintaining concentration in long games"
                }
            }
        };
        
        skillCategories.AddRange(new[] { mechanicalSkills, gameKnowledge, strategicThinking, mentalPerformance });
        
        Debug.Log($"📊 Initialized {skillCategories.Count} skill categories for {role} assessment");
    }
    
    void LoadBenchmarkData()
    {
        roleBenchmarks = new Dictionary<string, float>();
        
        // Load benchmarks based on role and tier
        // In real implementation, this would load from database or API
        
        Debug.Log($"📈 Loaded benchmark data for {benchmarkTier} {role} players");
    }
    
    [ContextMenu("Perform Skill Assessment")]
    public void PerformSkillAssessment()
    {
        Debug.Log($"🎯 Performing comprehensive skill assessment...");
        
        // Collect current performance data
        CollectPerformanceData();
        
        // Calculate normalized scores
        CalculateNormalizedScores();
        
        // Determine proficiency levels
        DetermineProficiencyLevels();
        
        // Generate assessment report
        GenerateAssessmentReport();
    }
    
    void CollectPerformanceData()
    {
        // Simulate performance data collection
        foreach (var category in skillCategories)
        {
            foreach (var metric in category.metrics)
            {
                // Simulate current performance values
                metric.currentValue = GeneratePerformanceValue(metric);
            }
        }
    }
    
    float GeneratePerformanceValue(SkillMetric metric)
    {
        // Simulate realistic performance data based on metric type
        float baseValue = metric.benchmarkValue;
        float variance = baseValue * 0.3f; // 30% variance
        
        // Special handling for reaction time (lower is better)
        if (metric.metricName.Contains("Reaction Time"))
        {
            return UnityEngine.Random.Range(baseValue * 0.8f, baseValue * 1.4f);
        }
        
        return UnityEngine.Random.Range(baseValue * 0.6f, baseValue * 1.1f);
    }
    
    void CalculateNormalizedScores()
    {
        foreach (var category in skillCategories)
        {
            float categorySum = 0f;
            
            foreach (var metric in category.metrics)
            {
                // Calculate normalized score (0-100)
                float normalizedScore;
                
                if (metric.metricName.Contains("Reaction Time"))
                {
                    // Lower is better for reaction time
                    normalizedScore = Mathf.Clamp01(metric.benchmarkValue / metric.currentValue) * 100f;
                }
                else
                {
                    // Higher is better for most metrics
                    normalizedScore = Mathf.Clamp01(metric.currentValue / metric.benchmarkValue) * 100f;
                }
                
                metric.normalizedScore = normalizedScore;
                categorySum += normalizedScore * metric.weight;
            }
            
            category.overallScore = categorySum;
        }
    }
    
    void DetermineProficiencyLevels()
    {
        foreach (var category in skillCategories)
        {
            category.proficiencyLevel = GetProficiencyLevel(category.overallScore);
        }
    }
    
    string GetProficiencyLevel(float score)
    {
        if (score >= 90f) return "Master";
        if (score >= 80f) return "Expert";
        if (score >= 70f) return "Advanced";
        if (score >= 60f) return "Intermediate";
        return "Beginner";
    }
    
    void GenerateAssessmentReport()
    {
        Debug.Log("📋 Skill Assessment Results:");
        
        float overallScore = skillCategories.Sum(c => c.overallScore * c.weight);
        string overallLevel = GetProficiencyLevel(overallScore);
        
        Debug.Log($"🏆 Overall Skill Level: {overallLevel} ({overallScore:F1}/100)");
        Debug.Log();
        
        foreach (var category in skillCategories.OrderByDescending(c => c.overallScore))
        {
            Debug.Log($"📊 {category.categoryName}: {category.proficiencyLevel} ({category.overallScore:F1}/100)");
            
            // Show top metrics in category
            var topMetrics = category.metrics.OrderByDescending(m => m.normalizedScore).Take(2);
            foreach (var metric in topMetrics)
            {
                Debug.Log($"  ✅ {metric.metricName}: {metric.normalizedScore:F1}/100");
            }
            
            // Show areas for improvement
            var weakMetrics = category.metrics.OrderBy(m => m.normalizedScore).Take(1);
            foreach (var metric in weakMetrics)
            {
                Debug.Log($"  ⚠️ {metric.metricName}: {metric.normalizedScore:F1}/100 (improvement needed)");
            }
            
            Debug.Log();
        }
        
        // Generate specific recommendations
        GenerateImprovementPlan();
    }
    
    void GenerateImprovementPlan()
    {
        Debug.Log("💡 Personalized Improvement Plan:");
        
        var improvementAreas = new List<(string category, string metric, float score, string suggestion)>();
        
        foreach (var category in skillCategories)
        {
            var weakestMetric = category.metrics.OrderBy(m => m.normalizedScore).First();
            
            if (weakestMetric.normalizedScore < 70f)
            {
                string suggestion = GenerateImprovementSuggestion(category.categoryName, weakestMetric.metricName);
                improvementAreas.Add((category.categoryName, weakestMetric.metricName, weakestMetric.normalizedScore, suggestion));
            }
        }
        
        // Prioritize by impact and ease of improvement
        var prioritizedAreas = improvementAreas
            .OrderBy(area => area.score)
            .ThenByDescending(area => GetImprovementEase(area.metric))
            .Take(3);
        
        int priority = 1;
        foreach (var area in prioritizedAreas)
        {
            Debug.Log($"{priority}. {area.category} - {area.metric} ({area.score:F1}/100)");
            Debug.Log($"   💡 {area.suggestion}");
            Debug.Log();
            priority++;
        }
    }
    
    string GenerateImprovementSuggestion(string category, string metric)
    {
        // Generate contextual improvement suggestions
        var suggestions = new Dictionary<string, Dictionary<string, string>>
        {
            ["Mechanical Skills"] = new Dictionary<string, string>
            {
                ["Last Hitting Accuracy"] = "Practice last-hitting in custom games for 15 minutes daily",
                ["Skill Shot Accuracy"] = "Use aim training tools and practice combo execution",
                ["Kiting Efficiency"] = "Practice attack-move commands in training mode",
                ["Reaction Time"] = "Use reaction time training games and reduce input lag"
            },
            ["Game Knowledge"] = new Dictionary<string, string>
            {
                ["Champion Matchup Knowledge"] = "Study champion guides and watch educational content",
                ["Item Build Efficiency"] = "Review optimal builds for different game states",
                ["Map Awareness"] = "Practice minimap checking every 3-5 seconds",
                ["Objective Priority"] = "Learn objective timers and team coordination"
            },
            ["Strategic Thinking"] = new Dictionary<string, string>
            {
                ["Decision Making Speed"] = "Review replays to identify decision points",
                ["Risk Assessment"] = "Practice evaluating fight outcomes before engaging",
                ["Team Coordination"] = "Improve communication and shotcalling skills",
                ["Adaptation Speed"] = "Study different game states and appropriate responses"
            },
            ["Mental Performance"] = new Dictionary<string, string>
            {
                ["Consistency"] = "Develop pre-game routines and maintain physical health",
                ["Pressure Handling"] = "Practice meditation and stress management techniques",
                ["Tilt Resistance"] = "Learn tilt management strategies and take breaks",
                ["Focus Duration"] = "Improve sleep schedule and limit distractions"
            }
        };
        
        return suggestions.ContainsKey(category) && suggestions[category].ContainsKey(metric)
            ? suggestions[category][metric]
            : "Focus on deliberate practice and seek coaching feedback";
    }
    
    float GetImprovementEase(string metric)
    {
        // Return ease of improvement (0-1, higher = easier)
        var easeRatings = new Dictionary<string, float>
        {
            ["Last Hitting Accuracy"] = 0.8f,
            ["Map Awareness"] = 0.7f,
            ["Item Build Efficiency"] = 0.9f,
            ["Reaction Time"] = 0.3f,
            ["Consistency"] = 0.4f,
            ["Pressure Handling"] = 0.5f
        };
        
        return easeRatings.ContainsKey(metric) ? easeRatings[metric] : 0.5f;
    }
    
    [ContextMenu("Export Assessment Data")]
    void ExportAssessmentData()
    {
        var exportData = new
        {
            PlayerID = "Player1",
            AssessmentDate = System.DateTime.Now,
            GameTitle = gameTitle,
            Role = role,
            OverallScore = skillCategories.Sum(c => c.overallScore * c.weight),
            SkillCategories = skillCategories.Select(c => new
            {
                c.categoryName,
                c.overallScore,
                c.proficiencyLevel,
                Metrics = c.metrics.Select(m => new
                {
                    m.metricName,
                    m.currentValue,
                    m.benchmarkValue,
                    m.normalizedScore
                })
            })
        };
        
        string json = JsonUtility.ToJson(exportData, true);
        var fileName = $"skill_assessment_{System.DateTime.Now:yyyyMMdd_HHmm}.json";
        var filePath = System.IO.Path.Combine(Application.persistentDataPath, fileName);
        System.IO.File.WriteAllText(filePath, json);
        
        Debug.Log($"📄 Assessment data exported to: {filePath}");
    }
}
```

Player performance analytics provide comprehensive frameworks for skill assessment, improvement tracking, and personalized coaching recommendations, enabling data-driven player development and competitive optimization.