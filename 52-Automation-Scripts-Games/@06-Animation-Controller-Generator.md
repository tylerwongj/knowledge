# @06-Animation-Controller-Generator

## 🎯 Core Concept
Automated animation controller creation and state machine generation for character and object animations.

## 🔧 Implementation

### Animation Controller Factory
```csharp
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;

public class AnimationControllerFactory
{
    [MenuItem("Game Tools/Generate Animation Controller")]
    public static void GenerateAnimationController()
    {
        AnimatorController controller = AnimatorController.CreateAnimatorControllerAtPath(
            "Assets/Animations/GeneratedController.controller");
        
        // Add parameters
        controller.AddParameter("Speed", AnimatorControllerParameterType.Float);
        controller.AddParameter("IsGrounded", AnimatorControllerParameterType.Bool);
        controller.AddParameter("Jump", AnimatorControllerParameterType.Trigger);
        
        // Create states
        var rootStateMachine = controller.layers[0].stateMachine;
        
        var idleState = rootStateMachine.AddState("Idle");
        var walkState = rootStateMachine.AddState("Walk");
        var jumpState = rootStateMachine.AddState("Jump");
        
        // Add transitions
        var idleToWalk = idleState.AddTransition(walkState);
        idleToWalk.AddCondition(AnimatorConditionMode.Greater, 0.1f, "Speed");
        
        var walkToIdle = walkState.AddTransition(idleState);
        walkToIdle.AddCondition(AnimatorConditionMode.Less, 0.1f, "Speed");
        
        var anyToJump = rootStateMachine.AddAnyStateTransition(jumpState);
        anyToJump.AddCondition(AnimatorConditionMode.If, 0, "Jump");
        
        AssetDatabase.SaveAssets();
    }
}
```

### Batch Animation Assignment
```csharp
[MenuItem("Game Tools/Assign Animations")]
public static void AssignAnimations()
{
    string[] animationGuids = AssetDatabase.FindAssets("t:AnimationClip");
    AnimatorController controller = AssetDatabase.LoadAssetAtPath<AnimatorController>(
        "Assets/Animations/GeneratedController.controller");
    
    foreach (string guid in animationGuids)
    {
        string path = AssetDatabase.GUIDToAssetPath(guid);
        AnimationClip clip = AssetDatabase.LoadAssetAtPath<AnimationClip>(path);
        
        if (clip.name.Contains("Idle"))
        {
            AssignClipToState(controller, "Idle", clip);
        }
        else if (clip.name.Contains("Walk"))
        {
            AssignClipToState(controller, "Walk", clip);
        }
    }
}

static void AssignClipToState(AnimatorController controller, string stateName, AnimationClip clip)
{
    var states = controller.layers[0].stateMachine.states;
    foreach (var state in states)
    {
        if (state.state.name == stateName)
        {
            state.state.motion = clip;
            break;
        }
    }
}
```

## 🚀 AI/LLM Integration
- Generate state machines based on character behavior descriptions
- Automatically create blend trees for complex animations
- Optimize transition conditions using AI analysis

## 💡 Key Benefits
- Rapid animation controller setup
- Consistent state machine architecture
- Automated animation clip assignment