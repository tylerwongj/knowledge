# @n-Advanced-Animation-Systems - Unity Animation Mastery

## 🎯 Learning Objectives
- Master Unity's Timeline, Cinemachine, and advanced animation workflows
- Implement procedural animation and runtime animation blending
- Create complex character rigs and facial animation systems
- Optimize animation performance for production environments

## 🔧 Advanced Animator Controller Patterns

### State Machine Layers and Masking
```csharp
using UnityEngine;

public class AdvancedAnimatorController : MonoBehaviour
{
    [SerializeField] private Animator animator;
    [SerializeField] private AvatarMask upperBodyMask;
    [SerializeField] private AvatarMask lowerBodyMask;
    
    void Start()
    {
        SetupAnimatorLayers();
    }
    
    private void SetupAnimatorLayers()
    {
        // Configure layer weights and masks
        animator.SetLayerWeight(1, 1.0f); // Upper body layer
        animator.SetLayerWeight(2, 1.0f); // Additive layer
        
        // Apply masks to layers
        var controller = animator.runtimeAnimatorController as AnimatorController;
        controller.layers[1].avatarMask = upperBodyMask;
    }
    
    public void BlendToState(string stateName, float transitionTime = 0.2f)
    {
        animator.CrossFadeInFixedTime(stateName, transitionTime);
    }
}
```

### Runtime Animation Blending
```csharp
public class RuntimeAnimationBlender : MonoBehaviour
{
    [SerializeField] private AnimationClip[] animationClips;
    [SerializeField] private float[] blendWeights;
    private AnimationMixerPlayable mixerPlayable;
    private PlayableGraph playableGraph;
    
    void Start()
    {
        CreateBlendTree();
    }
    
    private void CreateBlendTree()
    {
        playableGraph = PlayableGraph.Create();
        mixerPlayable = AnimationMixerPlayable.Create(playableGraph, animationClips.Length);
        
        for (int i = 0; i < animationClips.Length; i++)
        {
            var clipPlayable = AnimationClipPlayable.Create(playableGraph, animationClips[i]);
            playableGraph.Connect(clipPlayable, 0, mixerPlayable, i);
            mixerPlayable.SetInputWeight(i, blendWeights[i]);
        }
        
        var output = AnimationPlayableOutput.Create(playableGraph, "Animation", GetComponent<Animator>());
        output.SetSourcePlayable(mixerPlayable);
        playableGraph.Play();
    }
    
    public void UpdateBlendWeights(float[] newWeights)
    {
        for (int i = 0; i < newWeights.Length && i < mixerPlayable.GetInputCount(); i++)
        {
            mixerPlayable.SetInputWeight(i, newWeights[i]);
        }
    }
}
```

## 🔧 Procedural Animation Systems

### IK System Implementation
```csharp
using UnityEngine;

public class ProceduralIKSystem : MonoBehaviour
{
    [SerializeField] private Animator animator;
    [SerializeField] private Transform leftHandTarget;
    [SerializeField] private Transform rightHandTarget;
    [SerializeField] private Transform lookAtTarget;
    
    [Range(0, 1)] public float leftHandWeight = 1.0f;
    [Range(0, 1)] public float rightHandWeight = 1.0f;
    [Range(0, 1)] public float lookAtWeight = 1.0f;
    
    void OnAnimatorIK(int layerIndex)
    {
        if (animator == null) return;
        
        // Set hand IK targets
        if (leftHandTarget != null)
        {
            animator.SetIKPositionWeight(AvatarIKGoal.LeftHand, leftHandWeight);
            animator.SetIKRotationWeight(AvatarIKGoal.LeftHand, leftHandWeight);
            animator.SetIKPosition(AvatarIKGoal.LeftHand, leftHandTarget.position);
            animator.SetIKRotation(AvatarIKGoal.LeftHand, leftHandTarget.rotation);
        }
        
        if (rightHandTarget != null)
        {
            animator.SetIKPositionWeight(AvatarIKGoal.RightHand, rightHandWeight);
            animator.SetIKRotationWeight(AvatarIKGoal.RightHand, rightHandWeight);
            animator.SetIKPosition(AvatarIKGoal.RightHand, rightHandTarget.position);
            animator.SetIKRotation(AvatarIKGoal.RightHand, rightHandTarget.rotation);
        }
        
        // Set look at target
        if (lookAtTarget != null)
        {
            animator.SetLookAtWeight(lookAtWeight);
            animator.SetLookAtPosition(lookAtTarget.position);
        }
    }
}
```

### Bone Chain IK Solver
```csharp
public class BoneChainIK : MonoBehaviour
{
    [SerializeField] private Transform[] bones;
    [SerializeField] private Transform target;
    [SerializeField] private Transform pole;
    [SerializeField] private int iterations = 10;
    [SerializeField] private float threshold = 0.01f;
    
    private float[] boneLengths;
    private float totalLength;
    
    void Start()
    {
        CalculateBoneLengths();
    }
    
    private void CalculateBoneLengths()
    {
        boneLengths = new float[bones.Length - 1];
        totalLength = 0;
        
        for (int i = 0; i < boneLengths.Length; i++)
        {
            boneLengths[i] = Vector3.Distance(bones[i].position, bones[i + 1].position);
            totalLength += boneLengths[i];
        }
    }
    
    void LateUpdate()
    {
        SolveIK();
    }
    
    private void SolveIK()
    {
        if (target == null || bones.Length < 2) return;
        
        Vector3 targetPosition = target.position;
        float distanceToTarget = Vector3.Distance(bones[0].position, targetPosition);
        
        // Check if target is reachable
        if (distanceToTarget > totalLength)
        {
            // Stretch towards target
            Vector3 direction = (targetPosition - bones[0].position).normalized;
            for (int i = 1; i < bones.Length; i++)
            {
                bones[i].position = bones[i - 1].position + direction * boneLengths[i - 1];
            }
        }
        else
        {
            // FABRIK algorithm
            for (int iteration = 0; iteration < iterations; iteration++)
            {
                // Forward reaching
                bones[bones.Length - 1].position = targetPosition;
                for (int i = bones.Length - 2; i >= 0; i--)
                {
                    Vector3 direction = (bones[i].position - bones[i + 1].position).normalized;
                    bones[i].position = bones[i + 1].position + direction * boneLengths[i];
                }
                
                // Backward reaching
                Vector3 rootPos = bones[0].position;
                for (int i = 1; i < bones.Length; i++)
                {
                    Vector3 direction = (bones[i].position - bones[i - 1].position).normalized;
                    bones[i].position = bones[i - 1].position + direction * boneLengths[i - 1];
                }
                
                // Check if close enough to target
                if (Vector3.Distance(bones[bones.Length - 1].position, targetPosition) < threshold)
                    break;
            }
        }
        
        // Apply pole constraint if available
        if (pole != null && bones.Length >= 3)
        {
            ApplyPoleConstraint();
        }
    }
}
```

## 🔧 Timeline and Sequencing

### Custom Timeline Tracks
```csharp
using UnityEngine;
using UnityEngine.Timeline;
using UnityEngine.Playables;

[TrackColor(0.855f, 0.8623f, 0.87f)]
[TrackClipType(typeof(CustomAnimationClip))]
public class CustomAnimationTrack : TrackAsset
{
    public override Playable CreateTrackMixer(PlayableGraph graph, GameObject go, int inputCount)
    {
        return ScriptPlayable<CustomAnimationMixerBehaviour>.Create(graph, inputCount);
    }
}

[System.Serializable]
public class CustomAnimationClip : PlayableAsset, ITimelineClipAsset
{
    public CustomAnimationBehaviour template = new CustomAnimationBehaviour();
    
    public ClipCaps clipCaps => ClipCaps.Blending;
    
    public override Playable CreatePlayable(PlayableGraph graph, GameObject owner)
    {
        var playable = ScriptPlayable<CustomAnimationBehaviour>.Create(graph, template);
        return playable;
    }
}
```

### Animation Event System
```csharp
public class AnimationEventManager : MonoBehaviour
{
    [SerializeField] private Animator animator;
    private Dictionary<string, System.Action> animationEvents;
    
    void Start()
    {
        SetupAnimationEvents();
    }
    
    private void SetupAnimationEvents()
    {
        animationEvents = new Dictionary<string, System.Action>
        {
            { "FootstepLeft", () => PlayFootstepSound(0) },
            { "FootstepRight", () => PlayFootstepSound(1) },
            { "WeaponSwing", () => TriggerWeaponEffect() },
            { "SpellCast", () => CreateMagicEffect() }
        };
    }
    
    // Called by Animation Events
    public void OnAnimationEvent(string eventName)
    {
        if (animationEvents.TryGetValue(eventName, out System.Action action))
        {
            action.Invoke();
        }
    }
    
    private void PlayFootstepSound(int foot)
    {
        // Play footstep audio based on surface material
        AudioSource.PlayClipAtPoint(GetFootstepClip(), transform.position);
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Animation System Generation
```
"Generate Unity Animator Controller with [number] states for [character type]. Include transition conditions, blend trees for movement, and combat animations. Optimize for mobile performance."

"Create procedural animation system for [specific movement type] using Unity's Playables API. Include runtime blending and IK integration."

"Design Timeline sequence for [cutscene/gameplay moment] with camera movements, character animations, and audio synchronization."
```

### Performance Optimization Prompts
```
"Analyze Unity animation system for performance bottlenecks. Focus on bone count, animation compression, and culling systems. Provide optimization recommendations."

"Generate efficient animation streaming system for open-world game with [number] characters. Include LOD systems and memory management."
```

## 💡 Key Highlights

**Advanced Animation Concepts:**
- **Playables API**: Runtime animation graph construction and manipulation
- **Animation Jobs**: Multi-threaded animation processing for performance
- **Custom Playable Behaviors**: Timeline integration and custom animation logic
- **Bone Mapping**: Runtime retargeting between different character rigs

**Performance Optimization:**
- **Animation Compression**: Optimize keyframe data and interpolation
- **Culling Systems**: Disable animations for off-screen characters
- **LOD Animation**: Reduce animation quality based on distance
- **Streaming**: Load/unload animation data dynamically

**Character Animation Pipeline:**
- **Rigging Standards**: Consistent bone naming and hierarchy
- **Blend Shape Integration**: Facial animation and morph targets
- **Root Motion**: Proper movement integration with physics
- **Animation Layers**: Additive animations and body part masking

**Production Workflows:**
- **Version Control**: Animation file organization and team collaboration
- **Asset Validation**: Automated checks for animation quality
- **Performance Profiling**: Identify and resolve animation bottlenecks
- **Platform Optimization**: Adapt animations for different target platforms

**Essential Tools Integration:**
- **Timeline**: Complex sequence creation and preview
- **Cinemachine**: Automated camera work with animation
- **Animation Rigging**: Runtime IK and constraint systems
- **Recorder**: Capture and analyze animation performance