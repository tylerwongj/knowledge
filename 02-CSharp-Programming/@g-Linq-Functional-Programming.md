# @g-LINQ & Functional Programming

## 🎯 Learning Objectives
- Master LINQ queries for data manipulation and filtering
- Understand functional programming concepts in C#
- Apply method chaining and lambda expressions effectively
- Optimize query performance and understand deferred execution

## 🔍 LINQ Fundamentals

### Query Syntax vs Method Syntax
```csharp
// Query syntax (SQL-like)
var queryResult = from player in players
                 where player.Score > 100
                 orderby player.Name
                 select player;

// Method syntax (functional style)
var methodResult = players
    .Where(p => p.Score > 100)
    .OrderBy(p => p.Name)
    .Select(p => p);

// Both produce identical results, method syntax is generally preferred
```

### Core LINQ Operations
```csharp
public class GameStatistics
{
    public List<Player> players;
    public List<Match> matches;
    
    // Filtering
    public IEnumerable<Player> GetTopPlayers(int minScore)
    {
        return players.Where(p => p.Score >= minScore);
    }
    
    // Projection
    public IEnumerable<string> GetPlayerNames()
    {
        return players.Select(p => p.Name);
    }
    
    // Anonymous types for data shaping
    public var GetPlayerSummary()
    {
        return players.Select(p => new 
        {
            Name = p.Name,
            Score = p.Score,
            Rank = GetPlayerRank(p)
        });
    }
    
    // Aggregation
    public double GetAverageScore()
    {
        return players.Average(p => p.Score);
    }
    
    public Player GetBestPlayer()
    {
        return players.OrderByDescending(p => p.Score).First();
    }
}
```

## 🎯 Advanced LINQ Operations

### Grouping and Joining
```csharp
public class AdvancedQueries
{
    // Grouping
    public IEnumerable<IGrouping<string, Player>> GroupPlayersByTeam(List<Player> players)
    {
        return players.GroupBy(p => p.Team);
    }
    
    // Complex grouping with custom keys
    public var GroupByScoreRange(List<Player> players)
    {
        return players.GroupBy(p => new
        {
            ScoreRange = p.Score switch
            {
                >= 1000 => "Elite",
                >= 500 => "Advanced",
                >= 100 => "Intermediate",
                _ => "Beginner"
            }
        });
    }
    
    // Inner join
    public var GetPlayerMatchData(List<Player> players, List<Match> matches)
    {
        return from player in players
               join match in matches on player.Id equals match.PlayerId
               select new
               {
                   PlayerName = player.Name,
                   MatchDate = match.Date,
                   MatchScore = match.Score
               };
    }
    
    // Left join using GroupJoin
    public var GetPlayersWithMatches(List<Player> players, List<Match> matches)
    {
        return from player in players
               join match in matches on player.Id equals match.PlayerId into playerMatches
               from pm in playerMatches.DefaultIfEmpty()
               select new
               {
                   Player = player,
                   Match = pm // Will be null if no matches
               };
    }
}
```

### Set Operations and Complex Queries
```csharp
public class SetOperations
{
    // Union, Intersect, Except
    public IEnumerable<Player> GetAllActivePlayers(List<Player> team1, List<Player> team2)
    {
        return team1.Union(team2, new PlayerComparer());
    }
    
    public IEnumerable<Player> GetCommonPlayers(List<Player> team1, List<Player> team2)
    {
        return team1.Intersect(team2, new PlayerComparer());
    }
    
    // Distinct with custom comparer
    public IEnumerable<Player> RemoveDuplicatePlayers(List<Player> players)
    {
        return players.Distinct(new PlayerComparer());
    }
    
    // Pagination
    public IEnumerable<Player> GetPlayersPage(List<Player> players, int pageNumber, int pageSize)
    {
        return players
            .Skip((pageNumber - 1) * pageSize)
            .Take(pageSize);
    }
    
    // Partitioning
    public (IEnumerable<Player> PassedPlayers, IEnumerable<Player> FailedPlayers) 
        PartitionPlayersByScore(List<Player> players, int passingScore)
    {
        return (
            players.Where(p => p.Score >= passingScore),
            players.Where(p => p.Score < passingScore)
        );
    }
}

public class PlayerComparer : IEqualityComparer<Player>
{
    public bool Equals(Player x, Player y) => x?.Id == y?.Id;
    public int GetHashCode(Player obj) => obj?.Id.GetHashCode() ?? 0;
}
```

## 🏗️ Functional Programming Concepts

### Higher-Order Functions
```csharp
public class FunctionalConcepts
{
    // Functions as parameters
    public IEnumerable<T> ApplyFilter<T>(IEnumerable<T> source, Func<T, bool> predicate)
    {
        return source.Where(predicate);
    }
    
    // Function composition
    public Func<T, TResult> Compose<T, TIntermediate, TResult>(
        Func<T, TIntermediate> first,
        Func<TIntermediate, TResult> second)
    {
        return x => second(first(x));
    }
    
    // Example usage
    public void Example()
    {
        var players = GetPlayers();
        
        // Define filters as functions
        Func<Player, bool> isHighScorer = p => p.Score > 500;
        Func<Player, bool> isActive = p => p.IsActive;
        Func<Player, bool> isExperienced = p => p.GamesPlayed > 100;
        
        // Combine filters
        var topPlayers = players
            .Where(isHighScorer)
            .Where(isActive)
            .Where(isExperienced);
        
        // Function composition
        Func<Player, string> getName = p => p.Name;
        Func<string, string> toUpper = s => s.ToUpper();
        var getUpperName = Compose(getName, toUpper);
        
        var upperNames = players.Select(getUpperName);
    }
}
```

### Immutability and Pure Functions
```csharp
public readonly struct PlayerStats
{
    public int Score { get; init; }
    public int GamesPlayed { get; init; }
    public string Name { get; init; }
    
    // Pure function - no side effects, same input always produces same output
    public PlayerStats AddScore(int points)
    {
        return this with { Score = Score + points };
    }
    
    public double GetAverageScore()
    {
        return GamesPlayed > 0 ? (double)Score / GamesPlayed : 0;
    }
}

public static class PlayerStatsExtensions
{
    // Extension methods as pure functions
    public static PlayerStats WithBonusPoints(this PlayerStats stats, int bonus)
    {
        return stats with { Score = stats.Score + bonus };
    }
    
    public static PlayerStats IncrementGames(this PlayerStats stats)
    {
        return stats with { GamesPlayed = stats.GamesPlayed + 1 };
    }
}
```

## ⚡ Performance Optimization

### Deferred Execution Understanding
```csharp
public class DeferredExecutionDemo
{
    public void DemonstrateDeferred()
    {
        var players = GetPlayers();
        
        // Query is defined but not executed
        var highScorers = players.Where(p => 
        {
            Console.WriteLine($"Checking {p.Name}"); // This won't run yet
            return p.Score > 100;
        });
        
        Console.WriteLine("Query defined");
        
        // Execution happens here
        var firstHighScorer = highScorers.First(); // Only evaluates until first match
        
        // Each enumeration re-executes the query
        var count = highScorers.Count(); // Full enumeration
        var list = highScorers.ToList(); // Another full enumeration
    }
    
    // Force immediate execution when needed
    public List<Player> GetCachedResults()
    {
        return GetPlayers()
            .Where(p => p.Score > 100)
            .ToList(); // Immediate execution and caching
    }
}
```

### Optimization Techniques
```csharp
public class QueryOptimization
{
    // Avoid repeated enumeration
    public void OptimizedProcessing(IEnumerable<Player> players)
    {
        // Bad - multiple enumerations
        if (players.Any())
        {
            var count = players.Count();
            var first = players.First();
            // Each call re-enumerates
        }
        
        // Good - single enumeration
        var playerList = players.ToList();
        if (playerList.Any())
        {
            var count = playerList.Count;
            var first = playerList.First();
        }
    }
    
    // Use appropriate methods for performance
    public bool HasActivePlayer(List<Player> players)
    {
        // Good - stops at first match
        return players.Any(p => p.IsActive);
        
        // Bad - processes entire collection
        // return players.Where(p => p.IsActive).Count() > 0;
    }
    
    // Optimize complex queries
    public IEnumerable<Player> GetTopPlayersByTeam(List<Player> players)
    {
        return players
            .Where(p => p.IsActive) // Filter early
            .GroupBy(p => p.Team)
            .SelectMany(g => g.OrderByDescending(p => p.Score).Take(3)) // Top 3 per team
            .OrderByDescending(p => p.Score);
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Query Generation
```
Prompt: "Generate LINQ queries to analyze player performance data, including filtering by date ranges, calculating moving averages, and identifying performance trends."

Prompt: "Create complex LINQ expressions for game analytics that combine multiple data sources (players, matches, achievements) to produce comprehensive reports."

Prompt: "Design functional programming patterns in C# for managing game state immutably, including player progression and inventory management."
```

### Code Optimization
```
Prompt: "Analyze this LINQ query for performance issues and suggest optimizations: [paste query]"

Prompt: "Convert this imperative loop-based code to functional LINQ expressions while maintaining or improving performance."
```

## 🧮 Mathematical Operations with LINQ

### Statistical Calculations
```csharp
public class GameAnalytics
{
    public PlayerAnalysis AnalyzePlayer(List<Match> matches, int playerId)
    {
        var playerMatches = matches.Where(m => m.PlayerId == playerId);
        
        return new PlayerAnalysis
        {
            TotalMatches = playerMatches.Count(),
            AverageScore = playerMatches.Average(m => m.Score),
            MedianScore = CalculateMedian(playerMatches.Select(m => m.Score)),
            StandardDeviation = CalculateStandardDeviation(playerMatches.Select(m => m.Score)),
            WinRate = playerMatches.Count(m => m.Won) / (double)playerMatches.Count(),
            BestStreak = CalculateBestStreak(playerMatches.OrderBy(m => m.Date))
        };
    }
    
    private double CalculateMedian(IEnumerable<int> values)
    {
        var sorted = values.OrderBy(x => x).ToList();
        var mid = sorted.Count / 2;
        return sorted.Count % 2 == 0 
            ? (sorted[mid - 1] + sorted[mid]) / 2.0 
            : sorted[mid];
    }
    
    private double CalculateStandardDeviation(IEnumerable<int> values)
    {
        var list = values.ToList();
        var average = list.Average();
        var sumOfSquares = list.Sum(x => Math.Pow(x - average, 2));
        return Math.Sqrt(sumOfSquares / list.Count);
    }
}
```

## 💡 Advanced Patterns and Best Practices

### Custom LINQ Extensions
```csharp
public static class CustomLinqExtensions
{
    // Batch processing
    public static IEnumerable<IEnumerable<T>> Batch<T>(this IEnumerable<T> source, int batchSize)
    {
        var batch = new List<T>(batchSize);
        foreach (var item in source)
        {
            batch.Add(item);
            if (batch.Count == batchSize)
            {
                yield return batch;
                batch = new List<T>(batchSize);
            }
        }
        if (batch.Count > 0)
            yield return batch;
    }
    
    // Conditional Where
    public static IEnumerable<T> WhereIf<T>(this IEnumerable<T> source, bool condition, Func<T, bool> predicate)
    {
        return condition ? source.Where(predicate) : source;
    }
    
    // Median calculation
    public static double Median<T>(this IEnumerable<T> source, Func<T, double> selector)
    {
        var values = source.Select(selector).OrderBy(x => x).ToList();
        var mid = values.Count / 2;
        return values.Count % 2 == 0 
            ? (values[mid - 1] + values[mid]) / 2 
            : values[mid];
    }
}
```

### Functional Error Handling
```csharp
public class Result<T>
{
    public bool IsSuccess { get; }
    public T Value { get; }
    public string Error { get; }
    
    private Result(T value) => (IsSuccess, Value) = (true, value);
    private Result(string error) => (IsSuccess, Error) = (false, error);
    
    public static Result<T> Success(T value) => new(value);
    public static Result<T> Failure(string error) => new(error);
    
    public Result<TResult> Map<TResult>(Func<T, TResult> func)
    {
        return IsSuccess 
            ? Result<TResult>.Success(func(Value))
            : Result<TResult>.Failure(Error);
    }
    
    public Result<TResult> FlatMap<TResult>(Func<T, Result<TResult>> func)
    {
        return IsSuccess ? func(Value) : Result<TResult>.Failure(Error);
    }
}
```

## 🎯 Real-World Application Patterns
- **Data Pipeline Processing**: ETL operations using LINQ
- **Report Generation**: Complex aggregations and transformations  
- **Game State Queries**: Real-time game analysis and statistics
- **Configuration Processing**: Settings validation and transformation
- **API Response Mapping**: Converting between data models functionally