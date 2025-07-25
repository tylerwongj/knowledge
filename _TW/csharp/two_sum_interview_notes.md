# Interview Prep: ==Two Sum== Problem Breakdown

## Problem Statement

Given an array of integers and a target sum, return the indices of the two numbers that add up to the target.

### Example:

Input: `nums = [2, 7, 11, 15]`, `target = 9`\
Output: `[0, 1]` because `2 + 7 = 9`

---

## My Initial Thought Process (Brute Force)

### Parameters:

- ==Input: `int[] nums`, `int target`==
- ==Output: `int[]` of length 2==, containing indices of the numbers

### Return type:

- I considered using an `int[]` to return the pair of indices
- I considered returning `null` if no match is found

### Edge Cases I Thought Of:

- Array is too small (e.g. fewer than 2 elements)
- Input data is malformed (e.g. null array)
- No solution exists (return `null` or empty array)

### Brute Force Logic:

1. Loop through array with outer index `i`
2. For each `i`, loop again with index `j = i+1`
3. If `nums[i] + nums[j] == target`, return `[i, j]`
4. If no result found, return `null` or empty array

### Weaknesses in My Approach:

- Time complexity: O(n²)
- Not scalable for large arrays

---

## Optimized Solution: Using Dictionary

### Key Idea:

Use a hash map to track previously seen values while iterating. Check if the current number's complement (target - num) has already been seen.

### Code (C#):

```csharp
public int[] TwoSum(int[] nums, int target)
{
    Dictionary<int, int> seen = new Dictionary<int, int>();

    for (int i = 0; i < nums.Length; i++)
    {
        int num = nums[i];
        int complement = target - num;

        if (seen.ContainsKey(complement))
        {
            return new int[] { seen[complement], i };
        }

        if (!seen.ContainsKey(num)) // Avoid overwriting earlier index
        {
            seen[num] = i;
        }
    }

    return new int[0]; // ==Return empty array if no solution==
}
```

### Benefits of This Approach:

- **Time complexity:** O(n)
- **Space complexity:** O(n)
- Only one pass through the array

---

## Important Interview Tips:

### 1. Return Values:

- Prefer `new int[0]` over `null` for no result — safer for consumers
- Check for `result.Length == 0` instead of null checks

### 2. Dictionary Strategy:

- Store the **number** as the key, and **its index** as the value
- On each iteration:
  - Calculate `complement = target - num`
  - Check if `complement` is already in dictionary
  - If yes, return both indices
  - Otherwise, store `num -> index`

### 3. Optimization Path:

- Start with brute force if stuck
- Once it works, try improving time/space complexity
- Talk through both in interviews: ==brute-force first, then optimization==

---

## Summary

This problem is a common warm-up for interviews. Practicing both the brute-force and optimized versions helps demonstrate problem-solving skills and algorithm knowledge. Pay attention to return value conventions, and be ready to explain your choices.

