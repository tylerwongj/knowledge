# @a-After-Effects-Unity-Integration

## 🎯 Learning Objectives
- Master After Effects to Unity workflow for game UI animations
- Understand motion graphics principles for interactive design
- Implement efficient animation pipelines for Unity projects
- Build reusable animation systems and templates

## 🔧 Core After Effects to Unity Workflow

### Project Setup for Unity Integration
```javascript
// After Effects Expression for Unity-Compatible Animations
// Save as preset for consistent Unity export

// Position animation with easing curves
function createUnityPosition() {
    var startPos = [0, 0];
    var endPos = [100, 0];
    var duration = 1; // seconds
    
    if (time < duration) {
        var t = time / duration;
        // Unity-compatible easing (matches Animation Curve)
        var easeT = ease(t, 0.33, 0.67); // Ease in-out
        
        return linear(easeT, startPos, endPos);
    } else {
        return endPos;
    }
}

// Scale animation with Unity timing
function createUnityScale() {
    var startScale = [0, 0];
    var endScale = [100, 100];
    var duration = 0.5;
    
    if (time < duration) {
        var t = time / duration;
        var easeT = easeOut(t, 0.2); // Quick ease out
        
        return linear(easeT, startScale, endScale);
    } else {
        return endScale;
    }
}

// Rotation with Unity conventions (Z-axis for 2D)
function createUnityRotation() {
    var startRot = 0;
    var endRot = 360;
    var duration = 2;
    
    if (time < duration) {
        var t = time / duration;
        return linear(t, startRot, endRot);
    } else {
        return endRot;
    }
}
```

### Export Settings for Unity
```javascript
// After Effects Script for Unity Export
// Place in Scripts folder

(function exportForUnity() {
    var comp = app.project.activeItem;
    if (!comp || !(comp instanceof CompItem)) {
        alert("Please select a composition");
        return;
    }
    
    // Unity export settings
    var exportSettings = {
        format: "PNG Sequence",
        resolution: "Full",
        frameRate: 30, // Match Unity's preferred frame rate
        colorDepth: "32-bit",
        alphaChannel: "Premultiplied",
        startFrame: 1,
        endFrame: comp.duration * comp.frameRate
    };
    
    // Set up render queue
    var renderQueueItem = app.project.renderQueue.items.add(comp);
    var outputModule = renderQueueItem.outputModule(1);
    
    // Configure output
    outputModule.applyTemplate("PNG Sequence");
    outputModule.file = new File(Folder.desktop + "/UnityExport/" + comp.name + "/[#####].png");
    
    // Color management for Unity
    outputModule.includeSourceXMP = false;
    outputModule.colorManagement = "Straight Color";
    
    // Start render
    app.project.renderQueue.render();
    
    // Generate Unity animation data
    generateUnityAnimationData(comp);
})();

function generateUnityAnimationData(comp) {
    var animData = {
        name: comp.name,
        duration: comp.duration,
        frameRate: comp.frameRate,
        layers: []
    };
    
    // Extract layer animation data
    for (var i = 1; i <= comp.numLayers; i++) {
        var layer = comp.layer(i);
        var layerData = {
            name: layer.name,
            position: extractKeyframes(layer.property("Position")),
            scale: extractKeyframes(layer.property("Scale")),
            rotation: extractKeyframes(layer.property("Rotation")),
            opacity: extractKeyframes(layer.property("Opacity"))
        };
        
        animData.layers.push(layerData);
    }
    
    // Save as JSON for Unity import
    var file = new File(Folder.desktop + "/UnityExport/" + comp.name + "/animation.json");
    file.open("w");
    file.write(JSON.stringify(animData, null, 2));
    file.close();
}

function extractKeyframes(property) {
    if (!property || property.numKeys === 0) return null;
    
    var keyframes = [];
    for (var i = 1; i <= property.numKeys; i++) {
        keyframes.push({
            time: property.keyTime(i),
            value: property.keyValue(i),
            inTangent: property.keyInTangent(i),
            outTangent: property.keyOutTangent(i)
        });
    }
    
    return keyframes;
}
```

## 🚀 Unity Animation System Integration

### After Effects Data Importer
```csharp
using UnityEngine;
using UnityEditor;
using System.Collections.Generic;
using Newtonsoft.Json;
using System.IO;

[System.Serializable]
public class AEAnimationData
{
    public string name;
    public float duration;
    public float frameRate;
    public List<AELayerData> layers;
}

[System.Serializable]
public class AELayerData
{
    public string name;
    public List<AEKeyframe> position;
    public List<AEKeyframe> scale;
    public List<AEKeyframe> rotation;
    public List<AEKeyframe> opacity;
}

[System.Serializable]
public class AEKeyframe
{
    public float time;
    public float[] value;
    public float[] inTangent;
    public float[] outTangent;
}

public class AEToUnityImporter : EditorWindow
{
    [MenuItem("Tools/After Effects/Import Animation")]
    static void ShowWindow()
    {
        GetWindow<AEToUnityImporter>("AE Importer");
    }

    private string jsonPath = "";
    private GameObject targetObject;
    private bool createAnimationClip = true;
    private bool applyImmediately = false;

    void OnGUI()
    {
        GUILayout.Label("After Effects to Unity Importer", EditorStyles.boldLabel);
        
        EditorGUILayout.BeginHorizontal();
        EditorGUILayout.LabelField("Animation JSON:", GUILayout.Width(100));
        jsonPath = EditorGUILayout.TextField(jsonPath);
        if (GUILayout.Button("Browse", GUILayout.Width(60)))
        {
            jsonPath = EditorUtility.OpenFilePanel("Select Animation JSON", "", "json");
        }
        EditorGUILayout.EndHorizontal();
        
        targetObject = EditorGUILayout.ObjectField("Target Object", targetObject, typeof(GameObject), true) as GameObject;
        
        createAnimationClip = EditorGUILayout.Toggle("Create Animation Clip", createAnimationClip);
        applyImmediately = EditorGUILayout.Toggle("Apply Immediately", applyImmediately);
        
        EditorGUILayout.Space();
        
        if (GUILayout.Button("Import Animation"))
        {
            ImportAnimation();
        }
    }

    void ImportAnimation()
    {
        if (string.IsNullOrEmpty(jsonPath) || !File.Exists(jsonPath))
        {
            EditorUtility.DisplayDialog("Error", "Please select a valid JSON file", "OK");
            return;
        }

        if (targetObject == null)
        {
            EditorUtility.DisplayDialog("Error", "Please assign a target object", "OK");
            return;
        }

        try
        {
            string jsonContent = File.ReadAllText(jsonPath);
            AEAnimationData animData = JsonConvert.DeserializeObject<AEAnimationData>(jsonContent);
            
            if (createAnimationClip)
            {
                CreateAnimationClip(animData);
            }
            
            if (applyImmediately)
            {
                ApplyAnimation(animData);
            }
            
            Debug.Log($"Successfully imported animation: {animData.name}");
        }
        catch (System.Exception e)
        {
            EditorUtility.DisplayDialog("Import Error", $"Failed to import animation: {e.Message}", "OK");
        }
    }

    void CreateAnimationClip(AEAnimationData animData)
    {
        AnimationClip clip = new AnimationClip();
        clip.name = animData.name;
        clip.frameRate = animData.frameRate;
        
        foreach (var layerData in animData.layers)
        {
            string objectPath = FindObjectPath(targetObject, layerData.name);
            
            if (layerData.position != null)
            {
                CreatePositionCurves(clip, objectPath, layerData.position);
            }
            
            if (layerData.scale != null)
            {
                CreateScaleCurves(clip, objectPath, layerData.scale);
            }
            
            if (layerData.rotation != null)
            {
                CreateRotationCurves(clip, objectPath, layerData.rotation);
            }
            
            if (layerData.opacity != null)
            {
                CreateOpacityCurves(clip, objectPath, layerData.opacity);
            }
        }
        
        // Save animation clip
        string savePath = $"Assets/Animations/{animData.name}.anim";
        AssetDatabase.CreateAsset(clip, savePath);
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
    }

    void CreatePositionCurves(AnimationClip clip, string path, List<AEKeyframe> keyframes)
    {
        AnimationCurve curveX = new AnimationCurve();
        AnimationCurve curveY = new AnimationCurve();
        AnimationCurve curveZ = new AnimationCurve();
        
        foreach (var keyframe in keyframes)
        {
            // Convert AE coordinates to Unity coordinates
            float x = keyframe.value[0] / 100f; // AE pixels to Unity units
            float y = -keyframe.value[1] / 100f; // Flip Y axis
            float z = 0f;
            
            curveX.AddKey(keyframe.time, x);
            curveY.AddKey(keyframe.time, y);
            curveZ.AddKey(keyframe.time, z);
        }
        
        clip.SetCurve(path, typeof(Transform), "localPosition.x", curveX);
        clip.SetCurve(path, typeof(Transform), "localPosition.y", curveY);
        clip.SetCurve(path, typeof(Transform), "localPosition.z", curveZ);
    }

    void CreateScaleCurves(AnimationClip clip, string path, List<AEKeyframe> keyframes)
    {
        AnimationCurve curveX = new AnimationCurve();
        AnimationCurve curveY = new AnimationCurve();
        AnimationCurve curveZ = new AnimationCurve();
        
        foreach (var keyframe in keyframes)
        {
            float x = keyframe.value[0] / 100f; // AE percentage to Unity scale
            float y = keyframe.value[1] / 100f;
            float z = 1f;
            
            curveX.AddKey(keyframe.time, x);
            curveY.AddKey(keyframe.time, y);
            curveZ.AddKey(keyframe.time, z);
        }
        
        clip.SetCurve(path, typeof(Transform), "localScale.x", curveX);
        clip.SetCurve(path, typeof(Transform), "localScale.y", curveY);
        clip.SetCurve(path, typeof(Transform), "localScale.z", curveZ);
    }

    void CreateRotationCurves(AnimationClip clip, string path, List<AEKeyframe> keyframes)
    {
        AnimationCurve curveZ = new AnimationCurve();
        
        foreach (var keyframe in keyframes)
        {
            float rotation = keyframe.value[0]; // AE rotation in degrees
            curveZ.AddKey(keyframe.time, rotation);
        }
        
        clip.SetCurve(path, typeof(Transform), "localEulerAngles.z", curveZ);
    }

    void CreateOpacityCurves(AnimationClip clip, string path, List<AEKeyframe> keyframes)
    {
        AnimationCurve curve = new AnimationCurve();
        
        foreach (var keyframe in keyframes)
        {
            float alpha = keyframe.value[0] / 100f; // AE percentage to Unity alpha
            curve.AddKey(keyframe.time, alpha);
        }
        
        // Try to apply to various UI components
        clip.SetCurve(path, typeof(CanvasGroup), "alpha", curve);
        clip.SetCurve(path, typeof(UnityEngine.UI.Image), "color.a", curve);
        clip.SetCurve(path, typeof(UnityEngine.UI.Text), "color.a", curve);
    }

    string FindObjectPath(GameObject root, string targetName)
    {
        // Simple implementation - should be enhanced for complex hierarchies
        Transform found = root.transform.Find(targetName);
        if (found != null)
        {
            return targetName;
        }
        
        // Search recursively
        return SearchRecursively(root.transform, targetName, "");
    }

    string SearchRecursively(Transform parent, string targetName, string currentPath)
    {
        for (int i = 0; i < parent.childCount; i++)
        {
            Transform child = parent.GetChild(i);
            string childPath = string.IsNullOrEmpty(currentPath) ? child.name : currentPath + "/" + child.name;
            
            if (child.name == targetName)
            {
                return childPath;
            }
            
            string result = SearchRecursively(child, targetName, childPath);
            if (!string.IsNullOrEmpty(result))
            {
                return result;
            }
        }
        
        return "";
    }

    void ApplyAnimation(AEAnimationData animData)
    {
        // Immediately apply animation to target object
        StartCoroutine(PlayAnimation(animData));
    }

    System.Collections.IEnumerator PlayAnimation(AEAnimationData animData)
    {
        float startTime = Time.time;
        
        while (Time.time - startTime < animData.duration)
        {
            float t = (Time.time - startTime) / animData.duration;
            
            foreach (var layerData in animData.layers)
            {
                GameObject layerObj = GameObject.Find(layerData.name);
                if (layerObj == null) continue;
                
                ApplyKeyframeAtTime(layerObj, layerData, t);
            }
            
            yield return null;
        }
    }

    void ApplyKeyframeAtTime(GameObject obj, AELayerData layerData, float t)
    {
        if (layerData.position != null)
        {
            Vector3 pos = InterpolateVector3(layerData.position, t);
            obj.transform.localPosition = pos;
        }
        
        if (layerData.scale != null)
        {
            Vector3 scale = InterpolateVector3(layerData.scale, t);
            obj.transform.localScale = scale;
        }
        
        if (layerData.rotation != null)
        {
            float rotation = InterpolateFloat(layerData.rotation, t);
            obj.transform.localEulerAngles = new Vector3(0, 0, rotation);
        }
        
        if (layerData.opacity != null)
        {
            float alpha = InterpolateFloat(layerData.opacity, t);
            ApplyAlpha(obj, alpha);
        }
    }

    Vector3 InterpolateVector3(List<AEKeyframe> keyframes, float t)
    {
        // Simple linear interpolation - should be enhanced with proper curve evaluation
        if (keyframes.Count == 0) return Vector3.zero;
        if (keyframes.Count == 1) return new Vector3(keyframes[0].value[0], keyframes[0].value[1], 0);
        
        for (int i = 0; i < keyframes.Count - 1; i++)
        {
            if (t >= keyframes[i].time && t <= keyframes[i + 1].time)
            {
                float localT = (t - keyframes[i].time) / (keyframes[i + 1].time - keyframes[i].time);
                
                Vector3 start = new Vector3(keyframes[i].value[0], -keyframes[i].value[1], 0) / 100f;
                Vector3 end = new Vector3(keyframes[i + 1].value[0], -keyframes[i + 1].value[1], 0) / 100f;
                
                return Vector3.Lerp(start, end, localT);
            }
        }
        
        return Vector3.zero;
    }

    float InterpolateFloat(List<AEKeyframe> keyframes, float t)
    {
        if (keyframes.Count == 0) return 0f;
        if (keyframes.Count == 1) return keyframes[0].value[0] / 100f;
        
        for (int i = 0; i < keyframes.Count - 1; i++)
        {
            if (t >= keyframes[i].time && t <= keyframes[i + 1].time)
            {
                float localT = (t - keyframes[i].time) / (keyframes[i + 1].time - keyframes[i].time);
                float start = keyframes[i].value[0] / 100f;
                float end = keyframes[i + 1].value[0] / 100f;
                
                return Mathf.Lerp(start, end, localT);
            }
        }
        
        return 0f;
    }

    void ApplyAlpha(GameObject obj, float alpha)
    {
        CanvasGroup canvasGroup = obj.GetComponent<CanvasGroup>();
        if (canvasGroup != null)
        {
            canvasGroup.alpha = alpha;
            return;
        }
        
        UnityEngine.UI.Image image = obj.GetComponent<UnityEngine.UI.Image>();
        if (image != null)
        {
            Color color = image.color;
            color.a = alpha;
            image.color = color;
            return;
        }
        
        UnityEngine.UI.Text text = obj.GetComponent<UnityEngine.UI.Text>();
        if (text != null)
        {
            Color color = text.color;
            color.a = alpha;
            text.color = color;
        }
    }
}
```

## 🔧 Motion Graphics Templates for Unity UI

### UI Animation Template System
```csharp
using UnityEngine;
using UnityEngine.UI;
using DG.Tweening;

[System.Serializable]
public class UIAnimationTemplate
{
    public string templateName;
    public float duration = 1f;
    public Ease easeType = Ease.OutBack;
    public AnimationType animationType;
    public Vector3 fromValue;
    public Vector3 toValue;
    public bool useFrom = true;
}

public enum AnimationType
{
    Position,
    Scale,
    Rotation,
    Fade,
    SlideIn,
    PopIn,
    Bounce
}

public class UIAnimationManager : MonoBehaviour
{
    [SerializeField] private UIAnimationTemplate[] enterAnimations;
    [SerializeField] private UIAnimationTemplate[] exitAnimations;
    [SerializeField] private bool playOnStart = true;
    [SerializeField] private float delayBetweenElements = 0.1f;

    private RectTransform rectTransform;
    private CanvasGroup canvasGroup;
    private Sequence currentSequence;

    void Awake()
    {
        rectTransform = GetComponent<RectTransform>();
        canvasGroup = GetComponent<CanvasGroup>();
        
        if (canvasGroup == null)
        {
            canvasGroup = gameObject.AddComponent<CanvasGroup>();
        }
    }

    void Start()
    {
        if (playOnStart)
        {
            PlayEnterAnimation();
        }
    }

    public void PlayEnterAnimation()
    {
        if (currentSequence != null)
        {
            currentSequence.Kill();
        }

        currentSequence = DOTween.Sequence();
        
        foreach (var anim in enterAnimations)
        {
            AddAnimationToSequence(currentSequence, anim, true);
        }
        
        currentSequence.Play();
    }

    public void PlayExitAnimation(System.Action onComplete = null)
    {
        if (currentSequence != null)
        {
            currentSequence.Kill();
        }

        currentSequence = DOTween.Sequence();
        
        foreach (var anim in exitAnimations)
        {
            AddAnimationToSequence(currentSequence, anim, false);
        }
        
        if (onComplete != null)
        {
            currentSequence.OnComplete(() => onComplete());
        }
        
        currentSequence.Play();
    }

    private void AddAnimationToSequence(Sequence sequence, UIAnimationTemplate template, bool isEnter)
    {
        Tween tween = null;
        
        switch (template.animationType)
        {
            case AnimationType.Position:
                if (template.useFrom)
                {
                    rectTransform.anchoredPosition = template.fromValue;
                    tween = rectTransform.DOAnchorPos(template.toValue, template.duration);
                }
                else
                {
                    tween = rectTransform.DOAnchorPos(template.toValue, template.duration);
                }
                break;
                
            case AnimationType.Scale:
                if (template.useFrom)
                {
                    transform.localScale = template.fromValue;
                    tween = transform.DOScale(template.toValue, template.duration);
                }
                else
                {
                    tween = transform.DOScale(template.toValue, template.duration);
                }
                break;
                
            case AnimationType.Rotation:
                if (template.useFrom)
                {
                    transform.eulerAngles = template.fromValue;
                    tween = transform.DORotate(template.toValue, template.duration);
                }
                else
                {
                    tween = transform.DORotate(template.toValue, template.duration);
                }
                break;
                
            case AnimationType.Fade:
                if (template.useFrom)
                {
                    canvasGroup.alpha = template.fromValue.x;
                    tween = canvasGroup.DOFade(template.toValue.x, template.duration);
                }
                else
                {
                    tween = canvasGroup.DOFade(template.toValue.x, template.duration);
                }
                break;
                
            case AnimationType.SlideIn:
                CreateSlideInAnimation(sequence, template, isEnter);
                return;
                
            case AnimationType.PopIn:
                CreatePopInAnimation(sequence, template, isEnter);
                return;
                
            case AnimationType.Bounce:
                CreateBounceAnimation(sequence, template, isEnter);
                return;
        }
        
        if (tween != null)
        {
            tween.SetEase(template.easeType);
            sequence.Join(tween);
        }
    }

    private void CreateSlideInAnimation(Sequence sequence, UIAnimationTemplate template, bool isEnter)
    {
        Vector2 screenSize = new Vector2(Screen.width, Screen.height);
        Vector2 offScreenPosition = Vector2.zero;
        
        // Determine slide direction
        if (template.fromValue.x < 0) offScreenPosition.x = -screenSize.x;
        else if (template.fromValue.x > 0) offScreenPosition.x = screenSize.x;
        
        if (template.fromValue.y < 0) offScreenPosition.y = -screenSize.y;
        else if (template.fromValue.y > 0) offScreenPosition.y = screenSize.y;
        
        if (isEnter)
        {
            rectTransform.anchoredPosition = offScreenPosition;
            var tween = rectTransform.DOAnchorPos(Vector2.zero, template.duration);
            tween.SetEase(template.easeType);
            sequence.Join(tween);
        }
        else
        {
            var tween = rectTransform.DOAnchorPos(offScreenPosition, template.duration);
            tween.SetEase(template.easeType);
            sequence.Join(tween);
        }
    }

    private void CreatePopInAnimation(Sequence sequence, UIAnimationTemplate template, bool isEnter)
    {
        if (isEnter)
        {
            transform.localScale = Vector3.zero;
            canvasGroup.alpha = 0f;
            
            sequence.Join(transform.DOScale(Vector3.one, template.duration).SetEase(Ease.OutBack));
            sequence.Join(canvasGroup.DOFade(1f, template.duration * 0.5f));
        }
        else
        {
            sequence.Join(transform.DOScale(Vector3.zero, template.duration).SetEase(Ease.InBack));
            sequence.Join(canvasGroup.DOFade(0f, template.duration * 0.5f));
        }
    }

    private void CreateBounceAnimation(Sequence sequence, UIAnimationTemplate template, bool isEnter)
    {
        if (isEnter)
        {
            transform.localScale = Vector3.zero;
            
            var tween = transform.DOScale(Vector3.one, template.duration);
            tween.SetEase(Ease.OutBounce);
            sequence.Join(tween);
        }
        else
        {
            var tween = transform.DOScale(Vector3.zero, template.duration);
            tween.SetEase(Ease.InBounce);
            sequence.Join(tween);
        }
    }

    public void StopAllAnimations()
    {
        if (currentSequence != null)
        {
            currentSequence.Kill();
        }
    }

    void OnDestroy()
    {
        StopAllAnimations();
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Animation Template Generation
```prompt
Create After Effects animation template for Unity [UI_ELEMENT_TYPE] including:
- Smooth entrance and exit animations
- Hover and click state transitions
- Loading and success state animations
- Export-ready settings for Unity import
- Expressions for procedural animation
- Performance-optimized keyframe timing
```

### Motion Graphics Style Guide
```prompt
Develop comprehensive motion graphics style guide for Unity game [GAME_GENRE]:
- Animation timing and easing principles
- Color palette and visual hierarchy
- Transition patterns and micro-interactions
- After Effects project templates
- Unity implementation guidelines
- Performance budgets and optimization tips
```

## 💡 Key Motion Graphics Best Practices

### 1. Performance Optimization
- Use transform animations over pixel-based effects
- Implement object pooling for repeating animations
- Cache animation sequences for reuse
- Profile animation performance on target devices

### 2. Consistent Timing
- Establish standard durations for different animation types
- Use consistent easing curves across the project
- Maintain 60fps performance on target platforms
- Consider accessibility needs for motion sensitivity

### 3. Modular Design
- Create reusable animation templates
- Build scalable animation systems
- Implement data-driven animation parameters
- Design for localization and different screen sizes

### 4. Unity Integration
- Match After Effects coordinate systems to Unity
- Use appropriate import formats for different asset types
- Optimize texture atlases for UI animations
- Implement efficient update loops for animated elements

This comprehensive guide provides everything needed to create professional motion graphics workflows between After Effects and Unity for high-quality game UI animations.