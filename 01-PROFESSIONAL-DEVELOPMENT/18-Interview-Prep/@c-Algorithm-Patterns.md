# @c-Algorithm-Patterns - Common Algorithm Patterns for Coding Interviews

## 🎯 Learning Objectives
- Master the most frequently asked algorithm patterns in coding interviews
- Develop pattern recognition skills to quickly identify optimal approaches
- Understand when and how to apply each algorithmic technique
- Practice implementing solutions using each pattern efficiently

## 🔧 Essential Algorithm Patterns

### Two Pointers Pattern

#### When to Use
- Problems involving sorted arrays or strings
- Finding pairs or triplets that meet certain criteria
- Palindrome verification
- Removing duplicates

#### Implementation Template
```csharp
public class TwoPointersPattern 
{
    // Two Sum in sorted array
    public int[] TwoSum(int[] nums, int target) 
    {
        int left = 0, right = nums.Length - 1;
        
        while (left < right) 
        {
            int sum = nums[left] + nums[right];
            if (sum == target) 
                return new int[] { left, right };
            else if (sum < target) 
                left++;
            else 
                right--;
        }
        return new int[0];
    }
    
    // Remove duplicates from sorted array
    public int RemoveDuplicates(int[] nums) 
    {
        if (nums.Length <= 1) return nums.Length;
        
        int writeIndex = 1;
        for (int i = 1; i < nums.Length; i++) 
        {
            if (nums[i] != nums[i - 1]) 
            {
                nums[writeIndex] = nums[i];
                writeIndex++;
            }
        }
        return writeIndex;
    }
    
    // Valid palindrome
    public bool IsPalindrome(string s) 
    {
        int left = 0, right = s.Length - 1;
        
        while (left < right) 
        {
            while (left < right && !char.IsLetterOrDigit(s[left])) 
                left++;
            while (left < right && !char.IsLetterOrDigit(s[right])) 
                right--;
            
            if (char.ToLower(s[left]) != char.ToLower(s[right])) 
                return false;
            
            left++;
            right--;
        }
        return true;
    }
}
```

### Sliding Window Pattern

#### When to Use
- Problems involving contiguous subarrays or substrings
- Finding maximum/minimum in fixed or variable size windows
- String pattern matching

#### Implementation Template
```csharp
public class SlidingWindowPattern 
{
    // Maximum sum subarray of size k
    public int MaxSumSubarray(int[] nums, int k) 
    {
        int maxSum = 0, windowSum = 0;
        
        // Calculate sum of first window
        for (int i = 0; i < k; i++) 
            windowSum += nums[i];
        maxSum = windowSum;
        
        // Slide the window
        for (int i = k; i < nums.Length; i++) 
        {
            windowSum = windowSum - nums[i - k] + nums[i];
            maxSum = Math.Max(maxSum, windowSum);
        }
        return maxSum;
    }
    
    // Longest substring without repeating characters
    public int LengthOfLongestSubstring(string s) 
    {
        var charSet = new HashSet<char>();
        int left = 0, maxLength = 0;
        
        for (int right = 0; right < s.Length; right++) 
        {
            while (charSet.Contains(s[right])) 
            {
                charSet.Remove(s[left]);
                left++;
            }
            charSet.Add(s[right]);
            maxLength = Math.Max(maxLength, right - left + 1);
        }
        return maxLength;
    }
    
    // Minimum window substring
    public string MinWindow(string s, string t) 
    {
        var need = new Dictionary<char, int>();
        var window = new Dictionary<char, int>();
        
        foreach (char c in t) 
            need[c] = need.GetValueOrDefault(c, 0) + 1;
        
        int left = 0, right = 0, valid = 0;
        int start = 0, len = int.MaxValue;
        
        while (right < s.Length) 
        {
            char c = s[right];
            right++;
            
            if (need.ContainsKey(c)) 
            {
                window[c] = window.GetValueOrDefault(c, 0) + 1;
                if (window[c] == need[c]) 
                    valid++;
            }
            
            while (valid == need.Count) 
            {
                if (right - left < len) 
                {
                    start = left;
                    len = right - left;
                }
                
                char d = s[left];
                left++;
                
                if (need.ContainsKey(d)) 
                {
                    if (window[d] == need[d]) 
                        valid--;
                    window[d]--;
                }
            }
        }
        
        return len == int.MaxValue ? "" : s.Substring(start, len);
    }
}
```

### Fast and Slow Pointers (Floyd's Cycle Detection)

#### When to Use
- Detecting cycles in linked lists
- Finding the middle of a linked list
- Happy number problems

#### Implementation Template
```csharp
public class FastSlowPointers 
{
    // Detect cycle in linked list
    public bool HasCycle(ListNode head) 
    {
        if (head == null || head.next == null) return false;
        
        ListNode slow = head, fast = head.next;
        while (slow != fast) 
        {
            if (fast == null || fast.next == null) return false;
            slow = slow.next;
            fast = fast.next.next;
        }
        return true;
    }
    
    // Find cycle start
    public ListNode DetectCycle(ListNode head) 
    {
        if (head == null || head.next == null) return null;
        
        ListNode slow = head, fast = head;
        
        // Phase 1: Detect if cycle exists
        while (fast != null && fast.next != null) 
        {
            slow = slow.next;
            fast = fast.next.next;
            if (slow == fast) break;
        }
        
        if (fast == null || fast.next == null) return null;
        
        // Phase 2: Find cycle start
        slow = head;
        while (slow != fast) 
        {
            slow = slow.next;
            fast = fast.next;
        }
        return slow;
    }
    
    // Happy number
    public bool IsHappy(int n) 
    {
        int slow = n, fast = n;
        
        do 
        {
            slow = GetNext(slow);
            fast = GetNext(GetNext(fast));
        } while (slow != fast);
        
        return slow == 1;
    }
    
    private int GetNext(int n) 
    {
        int sum = 0;
        while (n > 0) 
        {
            int digit = n % 10;
            sum += digit * digit;
            n /= 10;
        }
        return sum;
    }
}
```

### Binary Search Pattern

#### When to Use
- Searching in sorted arrays
- Finding insertion points
- Search space reduction problems

#### Implementation Template
```csharp
public class BinarySearchPattern 
{
    // Classic binary search
    public int BinarySearch(int[] nums, int target) 
    {
        int left = 0, right = nums.Length - 1;
        
        while (left <= right) 
        {
            int mid = left + (right - left) / 2;
            
            if (nums[mid] == target) 
                return mid;
            else if (nums[mid] < target) 
                left = mid + 1;
            else 
                right = mid - 1;
        }
        return -1;
    }
    
    // Find first bad version
    public int FirstBadVersion(int n) 
    {
        int left = 1, right = n;
        
        while (left < right) 
        {
            int mid = left + (right - left) / 2;
            if (IsBadVersion(mid)) 
                right = mid;
            else 
                left = mid + 1;
        }
        return left;
    }
    
    // Search in rotated sorted array
    public int SearchRotated(int[] nums, int target) 
    {
        int left = 0, right = nums.Length - 1;
        
        while (left <= right) 
        {
            int mid = left + (right - left) / 2;
            
            if (nums[mid] == target) return mid;
            
            if (nums[left] <= nums[mid]) 
            {
                // Left side is sorted
                if (target >= nums[left] && target < nums[mid]) 
                    right = mid - 1;
                else 
                    left = mid + 1;
            } 
            else 
            {
                // Right side is sorted
                if (target > nums[mid] && target <= nums[right]) 
                    left = mid + 1;
                else 
                    right = mid - 1;
            }
        }
        return -1;
    }
}
```

### Depth-First Search (DFS) Pattern

#### When to Use
- Tree and graph traversal
- Pathfinding problems
- Backtracking algorithms

#### Implementation Template
```csharp
public class DFSPattern 
{
    // Maximum depth of binary tree
    public int MaxDepth(TreeNode root) 
    {
        if (root == null) return 0;
        return 1 + Math.Max(MaxDepth(root.left), MaxDepth(root.right));
    }
    
    // Path sum
    public bool HasPathSum(TreeNode root, int targetSum) 
    {
        if (root == null) return false;
        
        if (root.left == null && root.right == null) 
            return targetSum == root.val;
        
        return HasPathSum(root.left, targetSum - root.val) || 
               HasPathSum(root.right, targetSum - root.val);
    }
    
    // Number of islands (2D grid DFS)
    public int NumIslands(char[][] grid) 
    {
        if (grid == null || grid.Length == 0) return 0;
        
        int count = 0;
        for (int i = 0; i < grid.Length; i++) 
        {
            for (int j = 0; j < grid[0].Length; j++) 
            {
                if (grid[i][j] == '1') 
                {
                    DFS(grid, i, j);
                    count++;
                }
            }
        }
        return count;
    }
    
    private void DFS(char[][] grid, int i, int j) 
    {
        if (i < 0 || i >= grid.Length || j < 0 || j >= grid[0].Length || grid[i][j] == '0') 
            return;
        
        grid[i][j] = '0'; // Mark as visited
        
        // Explore all 4 directions
        DFS(grid, i + 1, j);
        DFS(grid, i - 1, j);
        DFS(grid, i, j + 1);
        DFS(grid, i, j - 1);
    }
}
```

### Breadth-First Search (BFS) Pattern

#### When to Use
- Level-order tree traversal
- Shortest path in unweighted graphs
- Minimum steps problems

#### Implementation Template
```csharp
public class BFSPattern 
{
    // Binary tree level order traversal
    public IList<IList<int>> LevelOrder(TreeNode root) 
    {
        var result = new List<IList<int>>();
        if (root == null) return result;
        
        var queue = new Queue<TreeNode>();
        queue.Enqueue(root);
        
        while (queue.Count > 0) 
        {
            int levelSize = queue.Count;
            var currentLevel = new List<int>();
            
            for (int i = 0; i < levelSize; i++) 
            {
                TreeNode node = queue.Dequeue();
                currentLevel.Add(node.val);
                
                if (node.left != null) queue.Enqueue(node.left);
                if (node.right != null) queue.Enqueue(node.right);
            }
            result.Add(currentLevel);
        }
        return result;
    }
    
    // Minimum steps to reach target
    public int MinSteps(int start, int target) 
    {
        if (start == target) return 0;
        
        var queue = new Queue<int>();
        var visited = new HashSet<int>();
        
        queue.Enqueue(start);
        visited.Add(start);
        
        int steps = 0;
        
        while (queue.Count > 0) 
        {
            int size = queue.Count;
            steps++;
            
            for (int i = 0; i < size; i++) 
            {
                int current = queue.Dequeue();
                
                // Generate next possible states
                var nextStates = GetNextStates(current);
                
                foreach (int next in nextStates) 
                {
                    if (next == target) return steps;
                    
                    if (!visited.Contains(next)) 
                    {
                        visited.Add(next);
                        queue.Enqueue(next);
                    }
                }
            }
        }
        return -1;
    }
    
    private List<int> GetNextStates(int current) 
    {
        // Implementation depends on specific problem
        return new List<int>();
    }
}
```

### Dynamic Programming Pattern

#### When to Use
- Optimization problems (min/max)
- Counting problems
- Decision problems (yes/no)

#### Implementation Template
```csharp
public class DynamicProgramming 
{
    // Fibonacci with memoization
    public int Fibonacci(int n) 
    {
        return FibHelper(n, new Dictionary<int, int>());
    }
    
    private int FibHelper(int n, Dictionary<int, int> memo) 
    {
        if (n <= 1) return n;
        if (memo.ContainsKey(n)) return memo[n];
        
        memo[n] = FibHelper(n - 1, memo) + FibHelper(n - 2, memo);
        return memo[n];
    }
    
    // Coin change
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
    
    // Longest increasing subsequence
    public int LengthOfLIS(int[] nums) 
    {
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
}
```

## 🚀 AI/LLM Integration Opportunities

### Pattern Recognition
```
PROMPT: "Analyze this problem and identify which algorithmic pattern(s) would be most suitable: [PROBLEM_DESCRIPTION]"
```

### Code Optimization
```
PROMPT: "Review my solution using [PATTERN_NAME] pattern. Suggest optimizations for time/space complexity: [CODE]"
```

### Similar Problems Generation
```
PROMPT: "Generate 3 similar problems that use the same [PATTERN_NAME] pattern but with different contexts."
```

## 💡 Key Highlights

### Pattern Selection Guide
- **Sorted Array + Target**: Binary Search or Two Pointers
- **Substring/Subarray**: Sliding Window
- **Tree/Graph Traversal**: DFS or BFS
- **Cycle Detection**: Fast/Slow Pointers
- **Optimization**: Dynamic Programming
- **Backtracking**: DFS with state restoration

### Time Complexity Summary
- **Two Pointers**: O(n)
- **Sliding Window**: O(n)
- **Binary Search**: O(log n)
- **DFS/BFS**: O(V + E) for graphs, O(n) for trees
- **Dynamic Programming**: Often O(n²) or O(n*m)

### Common Optimizations
- Use HashSet for O(1) lookups
- Precompute prefix sums for range queries
- Use monotonic stack/queue for optimization
- Apply memoization to avoid redundant calculations

This comprehensive guide provides the essential algorithmic patterns needed to solve most coding interview problems efficiently.