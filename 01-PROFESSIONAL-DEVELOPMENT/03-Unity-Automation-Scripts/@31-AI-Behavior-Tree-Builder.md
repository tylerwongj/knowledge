# @31-AI-Behavior-Tree-Builder

## 🎯 Core Concept
Automated AI behavior tree creation for NPC and enemy AI with visual node editor support.

## 🔧 Implementation

### Behavior Tree Framework
```csharp
using UnityEngine;
using System.Collections.Generic;

public abstract class BehaviorNode
{
    public enum NodeState { Running, Success, Failure }
    
    protected NodeState state;
    public NodeState State => state;
    
    public abstract NodeState Evaluate();
    
    public virtual void Reset()
    {
        state = NodeState.Running;
    }
}

public abstract class CompositeNode : BehaviorNode
{
    protected List<BehaviorNode> children = new List<BehaviorNode>();
    
    public void AddChild(BehaviorNode child)
    {
        children.Add(child);
    }
    
    public override void Reset()
    {
        base.Reset();
        foreach (var child in children)
        {
            child.Reset();
        }
    }
}

public class SequenceNode : CompositeNode
{
    private int currentChildIndex = 0;
    
    public override NodeState Evaluate()
    {
        if (currentChildIndex >= children.Count)
        {
            state = NodeState.Success;
            return state;
        }
        
        NodeState childState = children[currentChildIndex].Evaluate();
        
        switch (childState)
        {
            case NodeState.Success:
                currentChildIndex++;
                if (currentChildIndex >= children.Count)
                {
                    state = NodeState.Success;
                    currentChildIndex = 0;
                }
                else
                {
                    state = NodeState.Running;
                }
                break;
                
            case NodeState.Failure:
                state = NodeState.Failure;
                currentChildIndex = 0;
                break;
                
            case NodeState.Running:
                state = NodeState.Running;
                break;
        }
        
        return state;
    }
    
    public override void Reset()
    {
        base.Reset();
        currentChildIndex = 0;
    }
}

public class SelectorNode : CompositeNode
{
    private int currentChildIndex = 0;
    
    public override NodeState Evaluate()
    {
        if (currentChildIndex >= children.Count)
        {
            state = NodeState.Failure;
            return state;
        }
        
        NodeState childState = children[currentChildIndex].Evaluate();
        
        switch (childState)
        {
            case NodeState.Success:
                state = NodeState.Success;
                currentChildIndex = 0;
                break;
                
            case NodeState.Failure:
                currentChildIndex++;
                if (currentChildIndex >= children.Count)
                {
                    state = NodeState.Failure;
                    currentChildIndex = 0;
                }
                else
                {
                    state = NodeState.Running;
                }
                break;
                
            case NodeState.Running:
                state = NodeState.Running;
                break;
        }
        
        return state;
    }
    
    public override void Reset()
    {
        base.Reset();
        currentChildIndex = 0;
    }
}

public abstract class ActionNode : BehaviorNode
{
    protected AIAgent agent;
    
    public ActionNode(AIAgent agent)
    {
        this.agent = agent;
    }
}

public abstract class ConditionNode : BehaviorNode
{
    protected AIAgent agent;
    
    public ConditionNode(AIAgent agent)
    {
        this.agent = agent;
    }
}

// Specific AI Actions
public class MoveToTargetAction : ActionNode
{
    private Vector3 targetPosition;
    private float acceptableDistance = 1f;
    
    public MoveToTargetAction(AIAgent agent, Vector3 target, float distance = 1f) : base(agent)
    {
        targetPosition = target;
        acceptableDistance = distance;
    }
    
    public override NodeState Evaluate()
    {
        float distance = Vector3.Distance(agent.transform.position, targetPosition);
        
        if (distance <= acceptableDistance)
        {
            agent.StopMoving();
            state = NodeState.Success;
        }
        else
        {
            agent.MoveTo(targetPosition);
            state = NodeState.Running;
        }
        
        return state;
    }
}

public class AttackTargetAction : ActionNode
{
    private float attackRange = 2f;
    private float attackCooldown = 1f;
    private float lastAttackTime = 0f;
    
    public AttackTargetAction(AIAgent agent, float range = 2f, float cooldown = 1f) : base(agent)
    {
        attackRange = range;
        attackCooldown = cooldown;
    }
    
    public override NodeState Evaluate()
    {
        if (agent.Target == null)
        {
            state = NodeState.Failure;
            return state;
        }
        
        float distance = Vector3.Distance(agent.transform.position, agent.Target.position);
        
        if (distance > attackRange)
        {
            state = NodeState.Failure;
            return state;
        }
        
        if (Time.time - lastAttackTime >= attackCooldown)
        {
            agent.Attack();
            lastAttackTime = Time.time;
            state = NodeState.Success;
        }
        else
        {
            state = NodeState.Running;
        }
        
        return state;
    }
}

public class PatrolAction : ActionNode
{
    private Vector3[] patrolPoints;
    private int currentPatrolIndex = 0;
    private float waitTime = 2f;
    private float waitTimer = 0f;
    private bool isWaiting = false;
    
    public PatrolAction(AIAgent agent, Vector3[] points, float wait = 2f) : base(agent)
    {
        patrolPoints = points;
        waitTime = wait;
    }
    
    public override NodeState Evaluate()
    {
        if (patrolPoints == null || patrolPoints.Length == 0)
        {
            state = NodeState.Failure;
            return state;
        }
        
        Vector3 currentTarget = patrolPoints[currentPatrolIndex];
        float distance = Vector3.Distance(agent.transform.position, currentTarget);
        
        if (distance <= 1f)
        {
            if (!isWaiting)
            {
                isWaiting = true;
                waitTimer = 0f;
                agent.StopMoving();
            }
            
            waitTimer += Time.deltaTime;
            
            if (waitTimer >= waitTime)
            {
                currentPatrolIndex = (currentPatrolIndex + 1) % patrolPoints.Length;
                isWaiting = false;
            }
        }
        else
        {
            agent.MoveTo(currentTarget);
        }
        
        state = NodeState.Running;
        return state;
    }
}

// Condition Nodes
public class HasTargetCondition : ConditionNode
{
    public HasTargetCondition(AIAgent agent) : base(agent) { }
    
    public override NodeState Evaluate()
    {
        state = agent.Target != null ? NodeState.Success : NodeState.Failure;
        return state;
    }
}

public class IsTargetInRangeCondition : ConditionNode
{
    private float range;
    
    public IsTargetInRangeCondition(AIAgent agent, float detectionRange) : base(agent)
    {
        range = detectionRange;
    }
    
    public override NodeState Evaluate()
    {
        if (agent.Target == null)
        {
            state = NodeState.Failure;
            return state;
        }
        
        float distance = Vector3.Distance(agent.transform.position, agent.Target.position);
        state = distance <= range ? NodeState.Success : NodeState.Failure;
        return state;
    }
}

public class HealthBelowThresholdCondition : ConditionNode
{
    private float threshold;
    
    public HealthBelowThresholdCondition(AIAgent agent, float healthThreshold) : base(agent)
    {
        threshold = healthThreshold;
    }
    
    public override NodeState Evaluate()
    {
        state = agent.Health <= threshold ? NodeState.Success : NodeState.Failure;
        return state;
    }
}

// AI Agent Component
public class AIAgent : MonoBehaviour
{
    [Header("AI Settings")]
    public float detectionRange = 10f;
    public float attackRange = 2f;
    public float moveSpeed = 5f;
    public float health = 100f;
    public Transform[] patrolPoints;
    
    private BehaviorNode rootNode;
    private Transform target;
    private UnityEngine.AI.NavMeshAgent navAgent;
    
    public Transform Target => target;
    public float Health => health;
    
    void Start()
    {
        navAgent = GetComponent<UnityEngine.AI.NavMeshAgent>();
        navAgent.speed = moveSpeed;
        
        BuildBehaviorTree();
    }
    
    void BuildBehaviorTree()
    {
        // Create behavior tree structure
        SelectorNode rootSelector = new SelectorNode();
        
        // Combat behavior sequence
        SequenceNode combatSequence = new SequenceNode();
        combatSequence.AddChild(new HasTargetCondition(this));
        combatSequence.AddChild(new IsTargetInRangeCondition(this, attackRange));
        combatSequence.AddChild(new AttackTargetAction(this, attackRange));
        
        // Chase behavior sequence
        SequenceNode chaseSequence = new SequenceNode();
        chaseSequence.AddChild(new HasTargetCondition(this));
        chaseSequence.AddChild(new MoveToTargetAction(this, target != null ? target.position : transform.position, attackRange));
        
        // Patrol behavior
        Vector3[] patrolPositions = new Vector3[patrolPoints.Length];
        for (int i = 0; i < patrolPoints.Length; i++)
        {
            patrolPositions[i] = patrolPoints[i].position;
        }
        PatrolAction patrolAction = new PatrolAction(this, patrolPositions);
        
        // Build tree hierarchy
        rootSelector.AddChild(combatSequence);
        rootSelector.AddChild(chaseSequence);
        rootSelector.AddChild(patrolAction);
        
        rootNode = rootSelector;
    }
    
    void Update()
    {
        // Update target detection
        DetectTarget();
        
        // Execute behavior tree
        if (rootNode != null)
        {
            rootNode.Evaluate();
        }
    }
    
    void DetectTarget()
    {
        GameObject player = GameObject.FindGameObjectWithTag("Player");
        if (player != null)
        {
            float distance = Vector3.Distance(transform.position, player.transform.position);
            if (distance <= detectionRange)
            {
                target = player.transform;
            }
            else if (distance > detectionRange * 1.5f) // Lose target if too far
            {
                target = null;
            }
        }
    }
    
    public void MoveTo(Vector3 position)
    {
        if (navAgent != null)
        {
            navAgent.SetDestination(position);
        }
    }
    
    public void StopMoving()
    {
        if (navAgent != null)
        {
            navAgent.ResetPath();
        }
    }
    
    public void Attack()
    {
        Debug.Log($"{name} attacks!");
        // Implement attack logic
    }
    
    public void TakeDamage(float damage)
    {
        health -= damage;
        if (health <= 0)
        {
            Die();
        }
    }
    
    void Die()
    {
        Debug.Log($"{name} died!");
        // Implement death logic
        gameObject.SetActive(false);
    }
    
    void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(transform.position, detectionRange);
        
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(transform.position, attackRange);
    }
}

// Behavior Tree Builder Utility
public static class BehaviorTreeBuilder
{
    public static BehaviorNode CreateGuardAI(AIAgent agent, Vector3[] patrolPoints)
    {
        SelectorNode root = new SelectorNode();
        
        // Combat sequence
        SequenceNode combat = new SequenceNode();
        combat.AddChild(new HasTargetCondition(agent));
        combat.AddChild(new IsTargetInRangeCondition(agent, agent.attackRange));
        combat.AddChild(new AttackTargetAction(agent));
        
        // Chase sequence
        SequenceNode chase = new SequenceNode();
        chase.AddChild(new HasTargetCondition(agent));
        chase.AddChild(new MoveToTargetAction(agent, Vector3.zero, agent.attackRange));
        
        // Patrol
        PatrolAction patrol = new PatrolAction(agent, patrolPoints);
        
        root.AddChild(combat);
        root.AddChild(chase);
        root.AddChild(patrol);
        
        return root;
    }
    
    public static BehaviorNode CreateAggressiveAI(AIAgent agent)
    {
        SelectorNode root = new SelectorNode();
        
        // Always attack if target in range
        SequenceNode attack = new SequenceNode();
        attack.AddChild(new HasTargetCondition(agent));
        attack.AddChild(new IsTargetInRangeCondition(agent, agent.attackRange));
        attack.AddChild(new AttackTargetAction(agent));
        
        // Always chase if has target
        SequenceNode chase = new SequenceNode();
        chase.AddChild(new HasTargetCondition(agent));
        chase.AddChild(new MoveToTargetAction(agent, Vector3.zero, agent.attackRange));
        
        root.AddChild(attack);
        root.AddChild(chase);
        
        return root;
    }
}
```

## 🚀 AI/LLM Integration
- Generate behavior trees from AI descriptions
- Create balanced AI difficulty curves
- Automatically tune AI parameters

## 💡 Key Benefits
- Modular AI behavior system
- Easy behavior tree construction
- Reusable AI components