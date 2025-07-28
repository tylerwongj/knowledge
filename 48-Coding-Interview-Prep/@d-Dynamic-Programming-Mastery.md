# @d-Dynamic-Programming-Mastery - Dynamic Programming for Coding Interviews

## 🎯 Learning Objectives
- Master the fundamental concepts and patterns of dynamic programming
- Learn to identify when DP is the optimal approach for a problem
- Understand the transition from recursive solutions to optimized DP solutions
- Practice implementing both top-down (memoization) and bottom-up (tabulation) approaches

## 🔧 Dynamic Programming Fundamentals

### Core Concepts

#### When to Use Dynamic Programming
- **Optimal Substructure**: Problem can be broken down into smaller subproblems
- **Overlapping Subproblems**: Same subproblems are solved multiple times
- **Optimization**: Finding minimum, maximum, or counting solutions

#### DP Problem Categories
1. **0/1 Knapsack**: Include/exclude decisions
2. **Unbounded Knapsack**: Unlimited use of items
3. **Longest Common Subsequence**: String/array matching
4. **Longest Increasing Subsequence**: Sequence optimization
5. **Matrix Chain Multiplication**: Optimal partitioning
6. **Edit Distance**: String transformation
7. **Coin Change**: Making change with minimum coins
8. **House Robber**: Non-adjacent selection

### Basic DP Template

#### Top-Down Approach (Memoization)
```csharp
public class TopDownDP 
{
    // Fibonacci with memoization
    public int Fibonacci(int n) 
    {
        var memo = new Dictionary<int, int>();
        return FibHelper(n, memo);
    }
    
    private int FibHelper(int n, Dictionary<int, int> memo) 
    {
        if (n <= 1) return n;
        if (memo.ContainsKey(n)) return memo[n];
        
        memo[n] = FibHelper(n - 1, memo) + FibHelper(n - 2, memo);
        return memo[n];
    }
    
    // Climbing stairs
    public int ClimbStairs(int n) 
    {
        var memo = new Dictionary<int, int>();
        return ClimbHelper(n, memo);
    }
    
    private int ClimbHelper(int n, Dictionary<int, int> memo) 
    {
        if (n <= 2) return n;
        if (memo.ContainsKey(n)) return memo[n];
        
        memo[n] = ClimbHelper(n - 1, memo) + ClimbHelper(n - 2, memo);
        return memo[n];
    }
}
```

#### Bottom-Up Approach (Tabulation)
```csharp
public class BottomUpDP 
{
    // Fibonacci with tabulation
    public int Fibonacci(int n) 
    {
        if (n <= 1) return n;
        
        var dp = new int[n + 1];
        dp[0] = 0;
        dp[1] = 1;
        
        for (int i = 2; i <= n; i++) 
            dp[i] = dp[i - 1] + dp[i - 2];
        
        return dp[n];
    }
    
    // Space-optimized Fibonacci
    public int FibonacciOptimized(int n) 
    {
        if (n <= 1) return n;
        
        int prev2 = 0, prev1 = 1;
        for (int i = 2; i <= n; i++) 
        {
            int current = prev1 + prev2;
            prev2 = prev1;
            prev1 = current;
        }
        return prev1;
    }
}
```

## 🔧 Classic DP Problems

### 1. Knapsack Problems

#### 0/1 Knapsack
```csharp
public class KnapsackProblems 
{
    // 0/1 Knapsack - each item can be used at most once
    public int Knapsack01(int[] weights, int[] values, int capacity) 
    {
        int n = weights.Length;
        var dp = new int[n + 1, capacity + 1];
        
        for (int i = 1; i <= n; i++) 
        {
            for (int w = 1; w <= capacity; w++) 
            {
                // Don't take item i-1
                dp[i, w] = dp[i - 1, w];
                
                // Take item i-1 if it fits
                if (weights[i - 1] <= w) 
                {
                    int valueWithItem = dp[i - 1, w - weights[i - 1]] + values[i - 1];
                    dp[i, w] = Math.Max(dp[i, w], valueWithItem);
                }
            }
        }
        return dp[n, capacity];
    }
    
    // Space-optimized 0/1 Knapsack
    public int Knapsack01Optimized(int[] weights, int[] values, int capacity) 
    {
        var dp = new int[capacity + 1];
        
        for (int i = 0; i < weights.Length; i++) 
        {
            // Traverse backwards to avoid using updated values
            for (int w = capacity; w >= weights[i]; w--) 
            {
                dp[w] = Math.Max(dp[w], dp[w - weights[i]] + values[i]);
            }
        }
        return dp[capacity];
    }
    
    // Unbounded Knapsack - unlimited use of each item
    public int UnboundedKnapsack(int[] weights, int[] values, int capacity) 
    {
        var dp = new int[capacity + 1];
        
        for (int w = 1; w <= capacity; w++) 
        {
            for (int i = 0; i < weights.Length; i++) 
            {
                if (weights[i] <= w) 
                {
                    dp[w] = Math.Max(dp[w], dp[w - weights[i]] + values[i]);
                }
            }
        }
        return dp[capacity];
    }
}
```

### 2. Longest Common Subsequence (LCS)

```csharp
public class LCSProblems 
{
    // Longest Common Subsequence
    public int LongestCommonSubsequence(string text1, string text2) 
    {
        int m = text1.Length, n = text2.Length;
        var dp = new int[m + 1, n + 1];
        
        for (int i = 1; i <= m; i++) 
        {
            for (int j = 1; j <= n; j++) 
            {
                if (text1[i - 1] == text2[j - 1]) 
                    dp[i, j] = dp[i - 1, j - 1] + 1;
                else 
                    dp[i, j] = Math.Max(dp[i - 1, j], dp[i, j - 1]);
            }
        }
        return dp[m, n];
    }
    
    // Print LCS
    public string PrintLCS(string text1, string text2) 
    {
        int m = text1.Length, n = text2.Length;
        var dp = new int[m + 1, n + 1];
        
        // Fill dp table
        for (int i = 1; i <= m; i++) 
        {
            for (int j = 1; j <= n; j++) 
            {
                if (text1[i - 1] == text2[j - 1]) 
                    dp[i, j] = dp[i - 1, j - 1] + 1;
                else 
                    dp[i, j] = Math.Max(dp[i - 1, j], dp[i, j - 1]);
            }
        }
        
        // Reconstruct LCS
        var result = new StringBuilder();
        int x = m, y = n;
        
        while (x > 0 && y > 0) 
        {
            if (text1[x - 1] == text2[y - 1]) 
            {
                result.Insert(0, text1[x - 1]);
                x--;
                y--;
            } 
            else if (dp[x - 1, y] > dp[x, y - 1]) 
                x--;
            else 
                y--;
        }
        
        return result.ToString();
    }
}
```

### 3. Edit Distance Problems

```csharp
public class EditDistanceProblems 
{
    // Edit Distance (Levenshtein Distance)
    public int MinDistance(string word1, string word2) 
    {
        int m = word1.Length, n = word2.Length;
        var dp = new int[m + 1, n + 1];
        
        // Initialize base cases
        for (int i = 0; i <= m; i++) dp[i, 0] = i;
        for (int j = 0; j <= n; j++) dp[0, j] = j;
        
        for (int i = 1; i <= m; i++) 
        {
            for (int j = 1; j <= n; j++) 
            {
                if (word1[i - 1] == word2[j - 1]) 
                {
                    dp[i, j] = dp[i - 1, j - 1];
                } 
                else 
                {
                    dp[i, j] = 1 + Math.Min(
                        Math.Min(dp[i - 1, j],     // Delete
                                dp[i, j - 1]),     // Insert
                        dp[i - 1, j - 1]           // Replace
                    );
                }
            }
        }
        return dp[m, n];
    }
    
    // Minimum ASCII Delete Sum
    public int MinimumDeleteSum(string s1, string s2) 
    {
        int m = s1.Length, n = s2.Length;
        var dp = new int[m + 1, n + 1];
        
        // Initialize base cases
        for (int i = 1; i <= m; i++) 
            dp[i, 0] = dp[i - 1, 0] + s1[i - 1];
        for (int j = 1; j <= n; j++) 
            dp[0, j] = dp[0, j - 1] + s2[j - 1];
        
        for (int i = 1; i <= m; i++) 
        {
            for (int j = 1; j <= n; j++) 
            {
                if (s1[i - 1] == s2[j - 1]) 
                {
                    dp[i, j] = dp[i - 1, j - 1];
                } 
                else 
                {
                    dp[i, j] = Math.Min(
                        dp[i - 1, j] + s1[i - 1],
                        dp[i, j - 1] + s2[j - 1]
                    );
                }
            }
        }
        return dp[m, n];
    }
}
```

### 4. Longest Increasing Subsequence

```csharp
public class LISProblems 
{
    // Longest Increasing Subsequence O(n²)
    public int LengthOfLIS(int[] nums) 
    {
        if (nums.Length == 0) return 0;
        
        var dp = new int[nums.Length];
        Array.Fill(dp, 1);
        
        for (int i = 1; i < nums.Length; i++) 
        {
            for (int j = 0; j < i; j++) 
            {
                if (nums[i] > nums[j]) 
                    dp[i] = Math.Max(dp[i], dp[j] + 1);
            }
        }
        
        return dp.Max();
    }
    
    // Longest Increasing Subsequence O(n log n)
    public int LengthOfLISOptimal(int[] nums) 
    {
        var tails = new List<int>();
        
        foreach (int num in nums) 
        {
            int left = 0, right = tails.Count;
            
            while (left < right) 
            {
                int mid = left + (right - left) / 2;
                if (tails[mid] < num) 
                    left = mid + 1;
                else 
                    right = mid;
            }
            
            if (left == tails.Count) 
                tails.Add(num);
            else 
                tails[left] = num;
        }
        
        return tails.Count;
    }
    
    // Print LIS
    public IList<int> PrintLIS(int[] nums) 
    {
        if (nums.Length == 0) return new List<int>();
        
        var dp = new int[nums.Length];
        var parent = new int[nums.Length];
        Array.Fill(dp, 1);
        Array.Fill(parent, -1);
        
        int maxLength = 1, maxIndex = 0;
        
        for (int i = 1; i < nums.Length; i++) 
        {
            for (int j = 0; j < i; j++) 
            {
                if (nums[i] > nums[j] && dp[j] + 1 > dp[i]) 
                {
                    dp[i] = dp[j] + 1;
                    parent[i] = j;
                }
            }
            
            if (dp[i] > maxLength) 
            {
                maxLength = dp[i];
                maxIndex = i;
            }
        }
        
        // Reconstruct LIS
        var result = new List<int>();
        int current = maxIndex;
        
        while (current != -1) 
        {
            result.Add(nums[current]);
            current = parent[current];
        }
        
        result.Reverse();
        return result;
    }
}
```

### 5. Coin Change Problems

```csharp
public class CoinChangeProblems 
{
    // Coin Change - minimum coins
    public int CoinChange(int[] coins, int amount) 
    {
        var dp = new int[amount + 1];
        Array.Fill(dp, amount + 1);
        dp[0] = 0;
        
        for (int i = 1; i <= amount; i++) 
        {
            foreach (int coin in coins) 
            {
                if (coin <= i) 
                    dp[i] = Math.Min(dp[i], dp[i - coin] + 1);
            }
        }
        
        return dp[amount] > amount ? -1 : dp[amount];
    }
    
    // Coin Change - number of ways
    public int Change(int amount, int[] coins) 
    {
        var dp = new int[amount + 1];
        dp[0] = 1;
        
        foreach (int coin in coins) 
        {
            for (int i = coin; i <= amount; i++) 
            {
                dp[i] += dp[i - coin];
            }
        }
        
        return dp[amount];
    }
    
    // Coin Change with actual coins used
    public IList<int> CoinChangeCoins(int[] coins, int amount) 
    {
        var dp = new int[amount + 1];
        var parent = new int[amount + 1];
        Array.Fill(dp, amount + 1);
        Array.Fill(parent, -1);
        dp[0] = 0;
        
        for (int i = 1; i <= amount; i++) 
        {
            for (int j = 0; j < coins.Length; j++) 
            {
                if (coins[j] <= i && dp[i - coins[j]] + 1 < dp[i]) 
                {
                    dp[i] = dp[i - coins[j]] + 1;
                    parent[i] = j;
                }
            }
        }
        
        if (dp[amount] > amount) return new List<int>();
        
        // Reconstruct solution
        var result = new List<int>();
        int current = amount;
        
        while (current > 0) 
        {
            int coinIndex = parent[current];
            result.Add(coins[coinIndex]);
            current -= coins[coinIndex];
        }
        
        return result;
    }
}
```

### 6. House Robber Problems

```csharp
public class HouseRobberProblems 
{
    // House Robber - linear arrangement
    public int Rob(int[] nums) 
    {
        if (nums.Length == 0) return 0;
        if (nums.Length == 1) return nums[0];
        
        int prev2 = 0, prev1 = 0;
        
        foreach (int num in nums) 
        {
            int current = Math.Max(prev1, prev2 + num);
            prev2 = prev1;
            prev1 = current;
        }
        
        return prev1;
    }
    
    // House Robber II - circular arrangement
    public int RobCircular(int[] nums) 
    {
        if (nums.Length == 0) return 0;
        if (nums.Length == 1) return nums[0];
        if (nums.Length == 2) return Math.Max(nums[0], nums[1]);
        
        // Rob houses 0 to n-2 OR houses 1 to n-1
        return Math.Max(
            RobLinear(nums, 0, nums.Length - 2),
            RobLinear(nums, 1, nums.Length - 1)
        );
    }
    
    private int RobLinear(int[] nums, int start, int end) 
    {
        int prev2 = 0, prev1 = 0;
        
        for (int i = start; i <= end; i++) 
        {
            int current = Math.Max(prev1, prev2 + nums[i]);
            prev2 = prev1;
            prev1 = current;
        }
        
        return prev1;
    }
    
    // House Robber III - binary tree
    public int RobTree(TreeNode root) 
    {
        var result = RobHelper(root);
        return Math.Max(result[0], result[1]);
    }
    
    // Returns [rob_root, not_rob_root]
    private int[] RobHelper(TreeNode node) 
    {
        if (node == null) return new int[] { 0, 0 };
        
        var left = RobHelper(node.left);
        var right = RobHelper(node.right);
        
        // Rob current node
        int robCurrent = node.val + left[1] + right[1];
        
        // Don't rob current node
        int notRobCurrent = Math.Max(left[0], left[1]) + Math.Max(right[0], right[1]);
        
        return new int[] { robCurrent, notRobCurrent };
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Problem Identification
```
PROMPT: "Analyze this problem and determine if DP is suitable. Identify the subproblems and recurrence relation: [PROBLEM]"
```

### State Space Design
```
PROMPT: "Help me design the DP state space for this problem. What should dp[i] or dp[i][j] represent? [PROBLEM_DESCRIPTION]"
```

### Optimization Suggestions
```
PROMPT: "Review my DP solution and suggest space optimizations or alternative approaches: [CODE]"
```

### Test Case Generation
```
PROMPT: "Generate comprehensive test cases for this DP problem, including edge cases: [PROBLEM]"
```

## 💡 Key Highlights

### DP Problem Recognition Checklist
- ✅ **Optimization**: Find min/max value
- ✅ **Counting**: Number of ways to do something
- ✅ **Decision**: Yes/No based on optimal choice
- ✅ **Optimal Substructure**: Solution contains optimal solutions to subproblems
- ✅ **Overlapping Subproblems**: Same subproblems solved multiple times

### Common DP Patterns
- **Linear DP**: `dp[i] = f(dp[i-1], dp[i-2], ...)`
- **Grid DP**: `dp[i][j] = f(dp[i-1][j], dp[i][j-1], ...)`
- **Interval DP**: `dp[i][j] = f(dp[i][k], dp[k+1][j])`
- **Tree DP**: Bottom-up computation on trees
- **Bitmask DP**: Use bits to represent states

### Optimization Techniques
- **Space Optimization**: Use O(1) or O(n) instead of O(n²)
- **Rolling Arrays**: Only keep necessary previous states
- **State Compression**: Use bitmasks for compact representation
- **Memoization vs Tabulation**: Choose based on problem constraints

### Common Mistakes to Avoid
- Forgetting to handle base cases properly
- Not considering all possible transitions
- Using wrong loop order in tabulation
- Incorrect space optimization implementation
- Not validating the recurrence relation

This comprehensive guide provides the foundation for mastering dynamic programming in coding interviews.