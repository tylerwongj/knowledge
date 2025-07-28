# @b-Data-Structures-Mastery - Essential Data Structures for Coding Interviews

## 🎯 Learning Objectives
- Master implementation and application of core data structures
- Understand time/space complexity for each data structure operation
- Recognize when to use specific data structures for optimal solutions
- Practice common interview patterns using each data structure

## 🔧 Core Data Structures

### Arrays and Dynamic Arrays

#### Implementation Essentials
```csharp
// Array manipulation fundamentals
public class ArrayOperations 
{
    // Two pointers technique
    public int[] TwoSum(int[] nums, int target) 
    {
        var map = new Dictionary<int, int>();
        for (int i = 0; i < nums.Length; i++) 
        {
            int complement = target - nums[i];
            if (map.ContainsKey(complement)) 
                return new int[] { map[complement], i };
            map[nums[i]] = i;
        }
        return new int[0];
    }
    
    // Sliding window technique
    public int MaxSubarraySum(int[] nums, int k) 
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
}
```

#### Key Patterns
- **Two Pointers**: Left/right pointers for sorted arrays
- **Sliding Window**: Fixed/variable size windows
- **Prefix Sums**: Cumulative sums for range queries
- **Binary Search**: Search in sorted arrays

### Linked Lists

#### Implementation Essentials
```csharp
public class ListNode 
{
    public int val;
    public ListNode next;
    public ListNode(int val = 0, ListNode next = null) 
    {
        this.val = val;
        this.next = next;
    }
}

public class LinkedListOperations 
{
    // Reverse linked list
    public ListNode ReverseList(ListNode head) 
    {
        ListNode prev = null, current = head;
        
        while (current != null) 
        {
            ListNode nextTemp = current.next;
            current.next = prev;
            prev = current;
            current = nextTemp;
        }
        return prev;
    }
    
    // Detect cycle using Floyd's algorithm
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
    
    // Find middle of linked list
    public ListNode FindMiddle(ListNode head) 
    {
        ListNode slow = head, fast = head;
        while (fast != null && fast.next != null) 
        {
            slow = slow.next;
            fast = fast.next.next;
        }
        return slow;
    }
}
```

#### Key Patterns
- **Two Pointers**: Fast/slow pointers for cycle detection
- **Reversal**: Iterative and recursive reversal
- **Merging**: Merge sorted lists
- **Dummy Nodes**: Simplify edge case handling

### Stacks and Queues

#### Stack Implementation
```csharp
public class StackProblems 
{
    // Valid parentheses
    public bool IsValid(string s) 
    {
        var stack = new Stack<char>();
        var mapping = new Dictionary<char, char> { {')', '('}, {'}', '{'}, {']', '['} };
        
        foreach (char c in s) 
        {
            if (mapping.ContainsKey(c)) 
            {
                if (stack.Count == 0 || stack.Pop() != mapping[c]) 
                    return false;
            } 
            else 
            {
                stack.Push(c);
            }
        }
        return stack.Count == 0;
    }
    
    // Monotonic stack for next greater element
    public int[] NextGreaterElement(int[] nums) 
    {
        var result = new int[nums.Length];
        var stack = new Stack<int>();
        
        for (int i = nums.Length - 1; i >= 0; i--) 
        {
            while (stack.Count > 0 && stack.Peek() <= nums[i]) 
                stack.Pop();
            
            result[i] = stack.Count == 0 ? -1 : stack.Peek();
            stack.Push(nums[i]);
        }
        return result;
    }
}
```

#### Queue Implementation
```csharp
public class QueueProblems 
{
    // BFS template
    public int BFS(TreeNode root) 
    {
        if (root == null) return 0;
        
        var queue = new Queue<TreeNode>();
        queue.Enqueue(root);
        int level = 0;
        
        while (queue.Count > 0) 
        {
            int size = queue.Count;
            level++;
            
            for (int i = 0; i < size; i++) 
            {
                TreeNode node = queue.Dequeue();
                
                if (node.left != null) queue.Enqueue(node.left);
                if (node.right != null) queue.Enqueue(node.right);
            }
        }
        return level;
    }
}
```

### Hash Tables (Dictionaries)

#### Implementation Patterns
```csharp
public class HashTableProblems 
{
    // Frequency counting
    public char FirstUniqueChar(string s) 
    {
        var freq = new Dictionary<char, int>();
        
        // Count frequencies
        foreach (char c in s) 
            freq[c] = freq.GetValueOrDefault(c, 0) + 1;
        
        // Find first unique
        foreach (char c in s) 
            if (freq[c] == 1) return c;
        
        return ' ';
    }
    
    // Group anagrams
    public IList<IList<string>> GroupAnagrams(string[] strs) 
    {
        var groups = new Dictionary<string, IList<string>>();
        
        foreach (string str in strs) 
        {
            char[] chars = str.ToCharArray();
            Array.Sort(chars);
            string key = new string(chars);
            
            if (!groups.ContainsKey(key)) 
                groups[key] = new List<string>();
            groups[key].Add(str);
        }
        
        return new List<IList<string>>(groups.Values);
    }
}
```

### Binary Trees

#### Tree Traversal Implementation
```csharp
public class TreeNode 
{
    public int val;
    public TreeNode left;
    public TreeNode right;
    public TreeNode(int val = 0, TreeNode left = null, TreeNode right = null) 
    {
        this.val = val;
        this.left = left;
        this.right = right;
    }
}

public class BinaryTreeOperations 
{
    // Inorder traversal (recursive)
    public IList<int> InorderTraversal(TreeNode root) 
    {
        var result = new List<int>();
        InorderHelper(root, result);
        return result;
    }
    
    private void InorderHelper(TreeNode node, IList<int> result) 
    {
        if (node != null) 
        {
            InorderHelper(node.left, result);
            result.Add(node.val);
            InorderHelper(node.right, result);
        }
    }
    
    // Level order traversal (BFS)
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
    
    // Validate BST
    public bool IsValidBST(TreeNode root) 
    {
        return ValidateBST(root, null, null);
    }
    
    private bool ValidateBST(TreeNode node, int? lower, int? upper) 
    {
        if (node == null) return true;
        
        if (lower != null && node.val <= lower) return false;
        if (upper != null && node.val >= upper) return false;
        
        return ValidateBST(node.left, lower, node.val) && 
               ValidateBST(node.right, node.val, upper);
    }
}
```

### Heaps (Priority Queues)

#### Heap Implementation
```csharp
public class HeapProblems 
{
    // Kth largest element
    public int FindKthLargest(int[] nums, int k) 
    {
        var minHeap = new PriorityQueue<int, int>();
        
        foreach (int num in nums) 
        {
            minHeap.Enqueue(num, num);
            if (minHeap.Count > k) 
                minHeap.Dequeue();
        }
        
        return minHeap.Peek();
    }
    
    // Merge k sorted lists
    public ListNode MergeKLists(ListNode[] lists) 
    {
        var pq = new PriorityQueue<ListNode, int>();
        
        // Add first node of each list
        foreach (var list in lists) 
        {
            if (list != null) 
                pq.Enqueue(list, list.val);
        }
        
        var dummy = new ListNode(0);
        var current = dummy;
        
        while (pq.Count > 0) 
        {
            var node = pq.Dequeue();
            current.next = node;
            current = current.next;
            
            if (node.next != null) 
                pq.Enqueue(node.next, node.next.val);
        }
        
        return dummy.next;
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Data Structure Selection
```
PROMPT: "Given this problem description: [PROBLEM], which data structure would be most efficient and why? Analyze time/space complexity."
```

### Implementation Review
```
PROMPT: "Review my [DATA_STRUCTURE] implementation for correctness, efficiency, and edge cases: [CODE]"
```

### Pattern Recognition
```
PROMPT: "Identify common patterns in these data structure problems: [LIST_OF_PROBLEMS]. Suggest similar practice problems."
```

## 💡 Key Highlights

### Complexity Analysis Summary
- **Array**: Access O(1), Search O(n), Insert/Delete O(n)
- **Linked List**: Access O(n), Search O(n), Insert/Delete O(1)
- **Stack/Queue**: Push/Pop/Enqueue/Dequeue O(1)
- **Hash Table**: Average O(1) for all operations
- **Binary Tree**: Average O(log n) for balanced trees
- **Heap**: Insert/Delete O(log n), Peek O(1)

### Common Interview Patterns
- Use **two pointers** for array problems
- Use **fast/slow pointers** for linked list cycles
- Use **monotonic stack** for next/previous greater elements
- Use **BFS** for shortest path in unweighted graphs
- Use **DFS** for path finding and backtracking
- Use **heap** for top-k problems

### Edge Cases to Always Consider
- Empty input (null, empty array/string)
- Single element
- Duplicate elements
- Negative numbers
- Integer overflow
- Circular references

This comprehensive guide provides the foundation for mastering data structures essential for coding interview success.