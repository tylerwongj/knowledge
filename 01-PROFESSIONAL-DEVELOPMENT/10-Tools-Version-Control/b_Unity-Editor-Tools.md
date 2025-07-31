# @b-Unity-Editor-Tools - Essential Development Tools and Workflow Optimization

## 🎯 Learning Objectives
- Master Unity Editor customization and tool creation
- Implement efficient development workflows and automation
- Understand Unity's built-in tools and their applications
- Create custom editor scripts and inspector tools

## 🔧 Unity Editor Fundamentals

### Editor Layout Customization
```csharp
// Custom Editor Window
using UnityEditor;
using UnityEngine;

public class DeveloperToolsWindow : EditorWindow
{
    [MenuItem("Tools/Developer Tools")]
    public static void ShowWindow()
    {
        GetWindow<DeveloperToolsWindow>("Dev Tools");
    }
    
    private GameObject selectedObject;
    private string searchFilter = "";
    private Vector2 scrollPosition;
    
    void OnGUI()
    {
        GUILayout.Label("Developer Tools", EditorStyles.boldLabel);
        
        EditorGUILayout.Space();
        
        // Object selection
        selectedObject = EditorGUILayout.ObjectField("Selected Object", 
            selectedObject, typeof(GameObject), true) as GameObject;
        
        // Search filter
        searchFilter = EditorGUILayout.TextField("Search Filter", searchFilter);
        
        EditorGUILayout.Space();
        
        // Tool buttons
        EditorGUILayout.BeginHorizontal();
        if (GUILayout.Button("Quick Save Scene"))
        {
            EditorApplication.SaveScene();
            Debug.Log("Scene saved!");
        }
        
        if (GUILayout.Button("Clear Console"))
        {
            var logEntries = System.Type.GetType("UnityEditor.LogEntries,UnityEditor.dll");
            var clearMethod = logEntries.GetMethod("Clear", 
                System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.Public);
            clearMethod.Invoke(null, null);
        }
        EditorGUILayout.EndHorizontal();
        
        // Scrollable area
        scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);
        DrawHierarchyInfo();
        EditorGUILayout.EndScrollView();
    }
    
    void DrawHierarchyInfo()
    {
        if (selectedObject != null)
        {
            EditorGUILayout.LabelField($"Object: {selectedObject.name}");
            EditorGUILayout.LabelField($"Position: {selectedObject.transform.position}");
            EditorGUILayout.LabelField($"Children: {selectedObject.transform.childCount}");
            
            // Component list
            Component[] components = selectedObject.GetComponents<Component>();
            EditorGUILayout.LabelField($"Components ({components.Length}):");
            
            EditorGUI.indentLevel++;
            foreach (Component comp in components)
            {
                if (comp != null)
                    EditorGUILayout.LabelField($"• {comp.GetType().Name}");
            }
            EditorGUI.indentLevel--;
        }
    }
}
```

### Custom Inspector Scripts
```csharp
// Custom Property Drawer
using UnityEditor;
using UnityEngine;

[CustomPropertyDrawer(typeof(HealthComponent))]
public class HealthComponentDrawer : PropertyDrawer
{
    public override void OnGUI(Rect position, SerializedProperty property, GUIContent label)
    {
        EditorGUI.BeginProperty(position, label, property);
        
        // Calculate rects
        var labelRect = new Rect(position.x, position.y, position.width, EditorGUIUtility.singleLineHeight);
        var progressRect = new Rect(position.x, position.y + 20, position.width, 16);
        
        // Draw label
        EditorGUI.LabelField(labelRect, label);
        
        // Get health values
        var currentHealth = property.FindPropertyRelative("currentHealth");
        var maxHealth = property.FindPropertyRelative("maxHealth");
        
        if (currentHealth != null && maxHealth != null)
        {
            float healthPercent = maxHealth.floatValue > 0 ? 
                currentHealth.floatValue / maxHealth.floatValue : 0;
            
            // Draw progress bar
            EditorGUI.ProgressBar(progressRect, healthPercent, 
                $"{currentHealth.floatValue:F0}/{maxHealth.floatValue:F0}");
        }
        
        EditorGUI.EndProperty();
    }
    
    public override float GetPropertyHeight(SerializedProperty property, GUIContent label)
    {
        return EditorGUIUtility.singleLineHeight + 24;
    }
}

// Custom Editor for MonoBehaviour
[CustomEditor(typeof(PlayerController))]
public class PlayerControllerEditor : Editor
{
    private SerializedProperty moveSpeed;
    private SerializedProperty jumpForce;
    private SerializedProperty isGrounded;
    
    void OnEnable()
    {
        moveSpeed = serializedObject.FindProperty("moveSpeed");
        jumpForce = serializedObject.FindProperty("jumpForce");
        isGrounded = serializedObject.FindProperty("isGrounded");
    }
    
    public override void OnInspectorGUI()
    {
        serializedObject.Update();
        
        EditorGUILayout.LabelField("Player Controller Settings", EditorStyles.boldLabel);
        EditorGUILayout.Space();
        
        // Movement settings
        EditorGUILayout.LabelField("Movement", EditorStyles.miniBoldLabel);
        EditorGUILayout.PropertyField(moveSpeed);
        EditorGUILayout.PropertyField(jumpForce);
        
        EditorGUILayout.Space();
        
        // Runtime info
        if (Application.isPlaying)
        {
            EditorGUILayout.LabelField("Runtime Info", EditorStyles.miniBoldLabel);
            EditorGUI.BeginDisabledGroup(true);
            EditorGUILayout.PropertyField(isGrounded);
            EditorGUI.EndDisabledGroup();
            
            PlayerController player = (PlayerController)target;
            EditorGUILayout.LabelField($"Current Speed: {player.GetCurrentSpeed():F2}");
            
            // Debug buttons
            EditorGUILayout.Space();
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Test Jump"))
            {
                player.TestJump();
            }
            if (GUILayout.Button("Reset Position"))
            {
                player.ResetPosition();
            }
            EditorGUILayout.EndHorizontal();
        }
        
        serializedObject.ApplyModifiedProperties();
    }
}
```

## 🎮 Built-in Unity Tools

### Scene View Tools and Gizmos
```csharp
// Custom Gizmos and Handles
using UnityEditor;
using UnityEngine;

public class WaypointSystem : MonoBehaviour
{
    public Transform[] waypoints;
    public Color pathColor = Color.yellow;
    public bool showDirection = true;
    
    void OnDrawGizmos()
    {
        if (waypoints == null || waypoints.Length < 2) return;
        
        Gizmos.color = pathColor;
        
        for (int i = 0; i < waypoints.Length; i++)
        {
            if (waypoints[i] == null) continue;
            
            // Draw waypoint sphere
            Gizmos.DrawWireSphere(waypoints[i].position, 0.5f);
            
            // Draw path lines
            if (i < waypoints.Length - 1 && waypoints[i + 1] != null)
            {
                Gizmos.DrawLine(waypoints[i].position, waypoints[i + 1].position);
                
                // Draw direction arrows
                if (showDirection)
                {
                    Vector3 direction = (waypoints[i + 1].position - waypoints[i].position).normalized;
                    Vector3 midpoint = Vector3.Lerp(waypoints[i].position, waypoints[i + 1].position, 0.5f);
                    
                    Gizmos.DrawRay(midpoint, direction * 0.5f);
                    Gizmos.DrawRay(midpoint + direction * 0.5f, Quaternion.Euler(0, 140, 0) * direction * 0.2f);
                    Gizmos.DrawRay(midpoint + direction * 0.5f, Quaternion.Euler(0, -140, 0) * direction * 0.2f);
                }
            }
        }
    }
    
    void OnDrawGizmosSelected()
    {
        // Enhanced gizmos when selected
        Gizmos.color = Color.red;
        
        for (int i = 0; i < waypoints.Length; i++)
        {
            if (waypoints[i] == null) continue;
            
            Gizmos.DrawSphere(waypoints[i].position, 0.3f);
            
            // Draw labels
            #if UNITY_EDITOR
            Handles.Label(waypoints[i].position + Vector3.up, $"Waypoint {i}");
            #endif
        }
    }
}

// Custom Handles in Scene View
[CustomEditor(typeof(WaypointSystem))]
public class WaypointSystemEditor : Editor
{
    void OnSceneGUI()
    {
        WaypointSystem waypoints = (WaypointSystem)target;
        
        if (waypoints.waypoints == null) return;
        
        EditorGUI.BeginChangeCheck();
        
        for (int i = 0; i < waypoints.waypoints.Length; i++)
        {
            if (waypoints.waypoints[i] == null) continue;
            
            // Position handles
            Vector3 newPosition = Handles.PositionHandle(
                waypoints.waypoints[i].position, 
                waypoints.waypoints[i].rotation);
            
            if (EditorGUI.EndChangeCheck())
            {
                Undo.RecordObject(waypoints.waypoints[i], "Move Waypoint");
                waypoints.waypoints[i].position = newPosition;
            }
            
            // Add/Remove buttons
            Handles.BeginGUI();
            Vector3 screenPos = HandleUtility.WorldToGUIPoint(waypoints.waypoints[i].position);
            GUI.Label(new Rect(screenPos.x - 20, screenPos.y - 40, 40, 20), $"WP{i}");
            Handles.EndGUI();
        }
    }
}
```

### Asset Management Tools
```csharp
// Asset Database Utilities
using UnityEditor;
using UnityEngine;
using System.IO;

public class AssetManagementTools
{
    [MenuItem("Tools/Asset Management/Find Missing Scripts")]
    public static void FindMissingScripts()
    {
        GameObject[] allObjects = Resources.FindObjectsOfTypeAll<GameObject>();
        int missingCount = 0;
        
        foreach (GameObject obj in allObjects)
        {
            Component[] components = obj.GetComponents<Component>();
            for (int i = 0; i < components.Length; i++)
            {
                if (components[i] == null)
                {
                    Debug.LogError($"Missing script on: {GetGameObjectPath(obj)}", obj);
                    missingCount++;
                }
            }
        }
        
        Debug.Log($"Found {missingCount} missing scripts");
    }
    
    [MenuItem("Tools/Asset Management/Clean Empty Folders")]
    public static void CleanEmptyFolders()
    {
        string[] allFolders = AssetDatabase.GetAllAssetPaths()
            .Where(path => AssetDatabase.IsValidFolder(path))
            .ToArray();
        
        int deletedCount = 0;
        
        for (int i = allFolders.Length - 1; i >= 0; i--)
        {
            string folder = allFolders[i];
            if (IsEmptyFolder(folder))
            {
                AssetDatabase.DeleteAsset(folder);
                deletedCount++;
            }
        }
        
        AssetDatabase.Refresh();
        Debug.Log($"Deleted {deletedCount} empty folders");
    }
    
    [MenuItem("Tools/Asset Management/Rename with Prefix")]
    public static void RenameSelectedWithPrefix()
    {
        string prefix = EditorUtility.DisplayDialog("Add Prefix", "Enter prefix:", "Prefab_") ? "Prefab_" : "";
        
        if (string.IsNullOrEmpty(prefix)) return;
        
        foreach (Object obj in Selection.objects)
        {
            string assetPath = AssetDatabase.GetAssetPath(obj);
            string fileName = Path.GetFileNameWithoutExtension(assetPath);
            string fileExtension = Path.GetExtension(assetPath);
            string directory = Path.GetDirectoryName(assetPath);
            
            string newName = prefix + fileName + fileExtension;
            string newPath = Path.Combine(directory, newName);
            
            AssetDatabase.RenameAsset(assetPath, Path.GetFileNameWithoutExtension(newName));
        }
        
        AssetDatabase.Refresh();
    }
    
    private static string GetGameObjectPath(GameObject obj)
    {
        string path = obj.name;
        Transform parent = obj.transform.parent;
        
        while (parent != null)
        {
            path = parent.name + "/" + path;
            parent = parent.parent;
        }
        
        return path;
    }
    
    private static bool IsEmptyFolder(string folderPath)
    {
        return AssetDatabase.FindAssets("", new[] { folderPath }).Length == 0;
    }
}
```

## 🔧 Development Workflow Tools

### Build Automation Scripts
```csharp
// Build Pipeline Automation
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;
using System.IO;

public class BuildAutomation
{
    private static readonly string[] CommonScenes = {
        "Assets/Scenes/MainMenu.unity",
        "Assets/Scenes/GameLevel1.unity",
        "Assets/Scenes/GameLevel2.unity"
    };
    
    [MenuItem("Build/Build All Platforms")]
    public static void BuildAllPlatforms()
    {
        BuildWindows();
        BuildMac();
        BuildLinux();
        BuildAndroid();
        BuildWebGL();
    }
    
    [MenuItem("Build/Windows Build")]
    public static void BuildWindows()
    {
        string buildPath = "Builds/Windows/Game.exe";
        
        BuildPlayerOptions buildOptions = new BuildPlayerOptions
        {
            scenes = CommonScenes,
            locationPathName = buildPath,
            target = BuildTarget.StandaloneWindows64,
            options = BuildOptions.None
        };
        
        BuildWithReport(buildOptions, "Windows");
    }
    
    [MenuItem("Build/Development Build")]
    public static void BuildDevelopment()
    {
        string buildPath = "Builds/Development/Game.exe";
        
        BuildPlayerOptions buildOptions = new BuildPlayerOptions
        {
            scenes = CommonScenes,
            locationPathName = buildPath,
            target = BuildTarget.StandaloneWindows64,
            options = BuildOptions.Development | BuildOptions.AllowDebugging
        };
        
        BuildWithReport(buildOptions, "Development");
    }
    
    private static void BuildWithReport(BuildPlayerOptions options, string platform)
    {
        Debug.Log($"Starting {platform} build...");
        
        // Pre-build setup
        Directory.CreateDirectory(Path.GetDirectoryName(options.locationPathName));
        
        BuildReport report = BuildPipeline.BuildPlayer(options);
        BuildSummary summary = report.summary;
        
        if (summary.result == BuildResult.Succeeded)
        {
            Debug.Log($"{platform} build succeeded: {summary.outputPath} ({summary.totalSize} bytes)");
            
            // Open build folder
            EditorUtility.RevealInFinder(summary.outputPath);
        }
        else
        {
            Debug.LogError($"{platform} build failed");
            
            // Log build errors
            foreach (BuildStep step in report.steps)
            {
                foreach (BuildStepMessage message in step.messages)
                {
                    if (message.type == LogType.Error || message.type == LogType.Exception)
                    {
                        Debug.LogError($"Build Error: {message.content}");
                    }
                }
            }
        }
    }
    
    [MenuItem("Build/Clean Build Folder")]
    public static void CleanBuilds()
    {
        if (Directory.Exists("Builds"))
        {
            Directory.Delete("Builds", true);
            Debug.Log("Build folder cleaned");
        }
    }
}
```

### Project Analysis Tools
```csharp
// Project Statistics and Analysis
using UnityEditor;
using UnityEngine;
using System.Collections.Generic;
using System.Linq;

public class ProjectAnalyzer : EditorWindow
{
    [MenuItem("Tools/Project Analyzer")]
    public static void ShowWindow()
    {
        GetWindow<ProjectAnalyzer>("Project Analyzer");
    }
    
    private Vector2 scrollPosition;
    private Dictionary<string, int> scriptCounts = new Dictionary<string, int>();
    private Dictionary<string, long> assetSizes = new Dictionary<string, long>();
    
    void OnGUI()
    {
        GUILayout.Label("Project Analysis", EditorStyles.boldLabel);
        
        if (GUILayout.Button("Analyze Project"))
        {
            AnalyzeProject();
        }
        
        EditorGUILayout.Space();
        
        scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);
        
        // Script analysis
        if (scriptCounts.Count > 0)
        {
            EditorGUILayout.LabelField("Script Analysis", EditorStyles.boldLabel);
            foreach (var kvp in scriptCounts.OrderByDescending(x => x.Value))
            {
                EditorGUILayout.LabelField($"{kvp.Key}: {kvp.Value} files");
            }
            EditorGUILayout.Space();
        }
        
        // Asset size analysis
        if (assetSizes.Count > 0)
        {
            EditorGUILayout.LabelField("Asset Sizes", EditorStyles.boldLabel);
            foreach (var kvp in assetSizes.OrderByDescending(x => x.Value).Take(10))
            {
                string sizeStr = EditorUtility.FormatBytes(kvp.Value);
                EditorGUILayout.LabelField($"{kvp.Key}: {sizeStr}");
            }
        }
        
        EditorGUILayout.EndScrollView();
    }
    
    void AnalyzeProject()
    {
        scriptCounts.Clear();
        assetSizes.Clear();
        
        string[] allAssets = AssetDatabase.GetAllAssetPaths();
        
        foreach (string assetPath in allAssets)
        {
            if (assetPath.StartsWith("Assets/"))
            {
                // Count script types
                string extension = System.IO.Path.GetExtension(assetPath);
                if (scriptCounts.ContainsKey(extension))
                    scriptCounts[extension]++;
                else
                    scriptCounts[extension] = 1;
                
                // Calculate asset sizes
                System.IO.FileInfo fileInfo = new System.IO.FileInfo(assetPath);
                if (fileInfo.Exists)
                {
                    assetSizes[assetPath] = fileInfo.Length;
                }
            }
        }
        
        Debug.Log($"Analyzed {allAssets.Length} assets");
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Editor Tool Generation
```
Generate Unity editor tools for specific workflows:
- Input: [development needs, team size, project complexity]
- Output: Custom editor windows, inspector scripts, automation tools
- Include: Property drawers, scene view tools, build automation

Create Unity development workflow optimizer:
- Analyze: Current project structure, asset usage, build times
- Generate: Custom tools, editor scripts, automation pipelines
- Include: Performance profiling, asset optimization, team collaboration

Design Unity editor extensions for productivity:
- Features: [batch operations, asset management, debugging tools]
- Integration: [version control, CI/CD, team communication]
- Automation: [repetitive tasks, quality assurance, deployment]
```

### Development Process Automation
```
Build intelligent Unity project analyzer:
- Metrics: [code quality, asset usage, performance bottlenecks]
- Insights: [optimization opportunities, refactoring suggestions]
- Reports: [team productivity, project health, technical debt]

Generate Unity team workflow documentation:
- Content: [tool usage guides, best practices, troubleshooting]
- Format: [interactive tutorials, video scripts, quick reference]
- Focus: [editor customization, automation setup, collaboration tools]
```

## 💡 Key Highlights

### Essential Editor Tools
- **Scene View navigation: Alt+click to rotate, scroll to zoom**
- **Multi-object editing: Select multiple objects for batch operations**
- **Inspector lock: Lock inspector to keep object visible while selecting others**
- **Search filters: Use type filters in Hierarchy and Project windows**
- **Snap tools: Hold Ctrl while moving objects for grid snapping**

### Custom Editor Development
- **Use [CustomEditor] attribute for MonoBehaviour inspectors**
- **PropertyDrawer for custom property display**
- **EditorWindow for standalone tool windows**
- **Handles API for Scene View interaction**
- **Gizmos for visual debugging and scene annotations**

### Asset Management Best Practices
- **Regular asset database refresh after external changes**
- **Use AssetDatabase API for programmatic asset operations**
- **Implement asset post-processors for import automation**
- **Create asset bundles for modular content delivery**
- **Use Addressables for dynamic content loading**

### Build Pipeline Optimization
- **Automate build processes with BuildPlayerOptions**
- **Implement pre/post-build callbacks for custom operations**
- **Use build reports for performance analysis**
- **Create development vs. release build configurations**
- **Integrate with CI/CD systems for automated deployment**

### Workflow Efficiency Tips
- **Create custom shortcuts for frequently used operations**
- **Use Unity's Package Manager for tool distribution**
- **Implement editor preferences for team consistency**
- **Create project templates for rapid prototyping**
- **Use ScriptableObjects for editor tool configuration**