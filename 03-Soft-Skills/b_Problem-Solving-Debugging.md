# Problem-Solving & Debugging

## Overview
Develop systematic approaches to identifying, analyzing, and resolving technical problems in software development and game development scenarios.

## Key Concepts

### Systematic Debugging Approach

**The Scientific Method for Debugging:**
1. **Observe:** Identify and document the problem symptoms
2. **Hypothesize:** Form theories about potential causes
3. **Test:** Create experiments to validate or disprove hypotheses
4. **Analyze:** Evaluate results and refine understanding
5. **Implement:** Apply the solution and verify it works
6. **Document:** Record the problem and solution for future reference

**Root Cause Analysis:**
- **5 Whys Technique:** Keep asking "why" to drill down to root causes
- **Fishbone Diagram:** Categorize potential causes (code, environment, data, process)
- **Timeline Analysis:** Map when the problem started and what changed
- **Dependency Mapping:** Identify all systems and components involved

### Unity-Specific Debugging

**Common Unity Issues and Solutions:**
```csharp
// Null Reference Exceptions
public class PlayerController : MonoBehaviour
{
    private Rigidbody rb;
    
    void Start()
    {
        // Always verify component exists
        rb = GetComponent<Rigidbody>();
        if (rb == null)
        {
            Debug.LogError("PlayerController requires a Rigidbody component!");
            enabled = false;
            return;
        }
    }
    
    void Update()
    {
        // Defensive programming
        if (rb != null && Input.GetKey(KeyCode.W))
        {
            rb.AddForce(Vector3.forward * 10f);
        }
    }
}
```

**Performance Debugging:**
- Use Unity Profiler to identify bottlenecks
- Monitor garbage collection spikes and frame drops
- Analyze draw calls and batching efficiency
- Check for memory leaks and excessive allocations

### Logical Problem-Solving

**Breaking Down Complex Problems:**
1. **Decomposition:** Split large problems into smaller, manageable pieces
2. **Pattern Recognition:** Identify similarities to previously solved problems
3. **Abstraction:** Focus on essential elements, ignore irrelevant details
4. **Algorithm Design:** Create step-by-step solutions

**Problem-Solving Frameworks:**
```markdown
## STAR Method for Problem Documentation
**Situation:** What was the context and background?
**Task:** What needed to be accomplished?
**Action:** What specific steps were taken?
**Result:** What was the outcome and lessons learned?

## Example: Unity Performance Issue
**Situation:** Game framerate dropping to 15 FPS during combat scenes
**Task:** Identify and fix performance bottlenecks
**Action:** 
- Used Unity Profiler to identify excessive draw calls
- Implemented object pooling for projectiles
- Optimized shader complexity and texture sizes
**Result:** Achieved stable 60 FPS with 200+ objects on screen
```

### Code Investigation Techniques

**Reading Unfamiliar Code:**
```csharp
// Step 1: Understand the purpose and context
public class EnemyAI : MonoBehaviour
{
    // Step 2: Identify key data structures and their relationships
    private NavMeshAgent agent;
    private Transform player;
    private StateMachine stateMachine;
    
    // Step 3: Trace execution flow through key methods
    void Update()
    {
        stateMachine.Update(); // Main update loop
        UpdateTargeting();     // Secondary systems
        HandleCombat();        // Specific behaviors
    }
    
    // Step 4: Map inputs, outputs, and side effects
    private void HandleCombat()
    {
        // Input: player position, enemy state
        // Output: attack commands, animation triggers
        // Side effects: modify health, trigger events
    }
}
```

**Stack Trace Analysis:**
- Read from bottom to top to understand call chain
- Identify your code vs framework/library code
- Focus on the first occurrence in your code
- Look for patterns in recurring errors

## Practical Applications

### Debugging Tools and Techniques

**Unity Debugging Tools:**
```csharp
public class DebugHelper : MonoBehaviour
{
    [Header("Debug Visualization")]
    public bool showDebugInfo = true;
    public bool drawGizmos = true;
    
    void Update()
    {
        if (showDebugInfo)
        {
            // Display runtime information
            Debug.Log($"Player Position: {transform.position}");
            Debug.Log($"Current State: {GetComponent<StateMachine>().CurrentState}");
        }
    }
    
    void OnDrawGizmos()
    {
        if (drawGizmos)
        {
            // Visualize collision bounds, AI paths, etc.
            Gizmos.color = Color.red;
            Gizmos.DrawWireSphere(transform.position, 5f);
        }
    }
    
    // Conditional compilation for debug code
    [System.Diagnostics.Conditional("DEBUG")]
    private void DebugOnlyMethod()
    {
        // This code only runs in debug builds
        Debug.Log("Debug build detected");
    }
}
```

**Systematic Testing Approach:**
- **Unit Testing:** Test individual components in isolation
- **Integration Testing:** Test component interactions
- **User Acceptance Testing:** Verify features meet requirements
- **Regression Testing:** Ensure fixes don't break existing functionality

### Critical Thinking

**Evaluating Solutions:**
- **Feasibility:** Can this solution be implemented with available resources?
- **Scalability:** Will this work as the system grows?
- **Maintainability:** How easy will this be to modify and debug later?
- **Performance:** What are the computational and memory costs?

**Decision-Making Framework:**
1. **Define the Problem:** Clear problem statement and success criteria
2. **Generate Options:** Brainstorm multiple potential solutions
3. **Evaluate Trade-offs:** Consider pros, cons, and risks for each option
4. **Make Decision:** Choose based on data, not just intuition
5. **Plan Implementation:** Break down solution into actionable steps
6. **Monitor Results:** Track effectiveness and adjust as needed

### Learning from Failures

**Post-Mortem Analysis:**
```markdown
## Bug Post-Mortem Template
**Issue:** Player save data corruption in 0.3% of saves
**Root Cause:** Race condition between auto-save and manual save
**Timeline:**
- Day 1: Users report lost progress
- Day 2: Reproduced issue in testing environment
- Day 3: Identified race condition in SaveManager
- Day 4: Implemented save queue with mutex locks
**Lessons Learned:**
- Need better concurrency testing for save systems
- Implement save validation and backup mechanisms
- Add more detailed logging for save operations
**Prevention:**
- Code review checklist item for concurrency issues
- Automated testing with concurrent save operations
```

## Interview Preparation

### Problem-Solving Questions

**"Walk me through how you debug a complex issue"**
- Start with reproducing the problem consistently
- Use systematic elimination to narrow down causes
- Leverage debugging tools and logging effectively
- Document findings and verify solutions

**"Describe a challenging technical problem you solved"**
- Use STAR method to structure the response
- Emphasize systematic approach and critical thinking
- Highlight collaboration and communication aspects
- Discuss lessons learned and how you applied them

**"How do you approach learning new technologies or codebases?"**
- Start with high-level architecture and documentation
- Build small test projects to understand key concepts
- Read and trace through existing code examples
- Ask targeted questions to experienced team members

### Key Takeaways

**Systematic Problem-Solving:**
- Use structured approaches like the scientific method
- Break complex problems into manageable components
- Document problems and solutions for future reference
- Practice root cause analysis, not just symptom fixing

**Debugging Expertise:**
- Master debugging tools specific to your technology stack
- Develop hypothesis-driven testing strategies
- Build defensive programming habits to prevent issues
- Learn from failures through systematic post-mortem analysis