# @g-Unity-Custom-Editor-Scripting-Advanced - Professional Unity Tool Development

## 🎯 Learning Objectives
- Master advanced Unity Editor scripting for professional tool development
- Create custom inspectors, property drawers, and editor windows
- Implement data-driven editor tools that enhance team productivity
- Build automated workflow tools for Unity development pipelines

## 🔧 Advanced Custom Inspector Development

### Professional Custom Inspector Framework
```csharp
using UnityEngine;
using UnityEditor;
using System.Reflection;
using System.Collections.Generic;

/// <summary>
/// Advanced custom inspector base class with automatic UI generation
/// Provides professional-grade inspector UI with minimal code
/// </summary>
public abstract class AdvancedInspector : Editor
{
    protected SerializedObject targetObject;
    protected Dictionary<string, SerializedProperty> properties;
    protected GUIStyle headerStyle;
    protected GUIStyle boxStyle;
    
    private Vector2 scrollPosition;
    private bool showDebugInfo = false;
    
    protected virtual void OnEnable()
    {
        targetObject = serializedObject;
        CacheProperties();
        InitializeStyles();
    }
    
    public override void OnInspectorGUI()
    {
        targetObject.Update();
        
        DrawHeader();
        
        scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);
        
        DrawCustomInspector();
        DrawDebugSection();
        
        EditorGUILayout.EndScrollView();
        
        if (targetObject.hasModifiedProperties)
        {
            targetObject.ApplyModifiedProperties();
            OnPropertiesChanged();
        }
    }
    
    protected virtual void DrawHeader()
    {
        EditorGUILayout.BeginVertical(boxStyle);
        EditorGUILayout.LabelField(GetInspectorTitle(), headerStyle);
        EditorGUILayout.LabelField(GetInspectorDescription(), EditorStyles.wordWrappedMiniLabel);
        EditorGUILayout.EndVertical();
        
        EditorGUILayout.Space();
    }
    
    protected void DrawPropertyGroup(string groupName, params string[] propertyNames)
    {
        EditorGUILayout.BeginVertical(boxStyle);
        EditorGUILayout.LabelField(groupName, EditorStyles.boldLabel);
        
        foreach (string propertyName in propertyNames)
        {
            if (properties.ContainsKey(propertyName))
            {
                EditorGUILayout.PropertyField(properties[propertyName]);
            }
            else
            {
                EditorGUILayout.HelpBox($"Property '{propertyName}' not found", MessageType.Warning);
            }
        }
        
        EditorGUILayout.EndVertical();
        EditorGUILayout.Space();
    }
    
    protected void DrawConditionalProperty(string propertyName, string conditionProperty, object expectedValue)
    {
        if (!properties.ContainsKey(conditionProperty) || !properties.ContainsKey(propertyName))
            return;
        
        var condition = properties[conditionProperty];
        bool shouldShow = false;
        
        switch (condition.propertyType)
        {
            case SerializedPropertyType.Boolean:
                shouldShow = condition.boolValue == (bool)expectedValue;
                break;
            case SerializedPropertyType.Enum:
                shouldShow = condition.enumValueIndex == (int)expectedValue;
                break;
            case SerializedPropertyType.Integer:
                shouldShow = condition.intValue == (int)expectedValue;
                break;
        }
        
        if (shouldShow)
        {
            EditorGUILayout.PropertyField(properties[propertyName]);
        }
    }
    
    protected void DrawButtonRow(params System.Action[] buttonActions)
    {
        EditorGUILayout.BeginHorizontal();
        foreach (var action in buttonActions)
        {
            if (GUILayout.Button(action.Method.Name))
            {
                action.Invoke();
            }
        }
        EditorGUILayout.EndHorizontal();
    }
    
    protected abstract void DrawCustomInspector();
    protected abstract string GetInspectorTitle();
    protected virtual string GetInspectorDescription() => "";
    protected virtual void OnPropertiesChanged() { }
}

/// <summary>
/// Example implementation for a game manager component
/// </summary>
[CustomEditor(typeof(GameManager))]
public class GameManagerInspector : AdvancedInspector
{
    protected override string GetInspectorTitle() => "Game Manager Configuration";
    
    protected override string GetInspectorDescription() => 
        "Central game management system controlling core game mechanics and state.";
    
    protected override void DrawCustomInspector()
    {
        DrawPropertyGroup("Game Settings", 
            "gameMode", "difficulty", "playerCount", "timeLimit");
        
        DrawPropertyGroup("Performance Settings",
            "targetFrameRate", "enableVSync", "qualityLevel");
        
        DrawConditionalProperty("debugMode", "enableDebugging", true);
        DrawConditionalProperty("debugUIScale", "debugMode", true);
        
        DrawButtonRow(
            () => (target as GameManager).StartGame(),
            () => (target as GameManager).ResetGame(),
            () => (target as GameManager).SaveSettings()
        );
        
        if (Application.isPlaying)
        {
            DrawRuntimeStats();
        }
    }
    
    private void DrawRuntimeStats()
    {
        EditorGUILayout.BeginVertical(boxStyle);
        EditorGUILayout.LabelField("Runtime Statistics", EditorStyles.boldLabel);
        
        var gameManager = target as GameManager;
        EditorGUILayout.LabelField($"Current State: {gameManager.CurrentState}");
        EditorGUILayout.LabelField($"Frame Rate: {1f / Time.deltaTime:F1} FPS");
        EditorGUILayout.LabelField($"Memory Usage: {System.GC.GetTotalMemory(false) / 1024 / 1024} MB");
        
        EditorGUILayout.EndVertical();
    }
}
```

### Advanced Property Drawer System
```csharp
/// <summary>
/// Advanced property drawer with validation and custom UI
/// Supports ranges, validation, and complex data types
/// </summary>
[CustomPropertyDrawer(typeof(GameplayParameter))]
public class GameplayParameterDrawer : PropertyDrawer
{
    private const float LABEL_WIDTH = 120f;
    private const float BUTTON_WIDTH = 60f;
    private const float LINE_HEIGHT = 18f;
    private const float SPACING = 2f;
    
    public override float GetPropertyHeight(SerializedProperty property, GUIContent label)
    {
        var parameterType = property.FindPropertyRelative("parameterType");
        var showValidation = property.FindPropertyRelative("enableValidation").boolValue;
        
        float height = LINE_HEIGHT; // Base height
        
        // Add height for parameter-specific fields
        switch (parameterType.enumValueIndex)
        {
            case 0: // Float
            case 1: // Int
                height += showValidation ? LINE_HEIGHT * 2 : 0; // Min/Max fields
                break;
            case 2: // String
                height += showValidation ? LINE_HEIGHT : 0; // Length validation
                break;
            case 3: // Vector3
                height += LINE_HEIGHT; // XYZ components
                break;
        }
        
        return height + SPACING * 2;
    }
    
    public override void OnGUI(Rect position, SerializedProperty property, GUIContent label)
    {
        EditorGUI.BeginProperty(position, label, property);
        
        var rect = new Rect(position.x, position.y, position.width, LINE_HEIGHT);
        
        // Draw main parameter controls
        DrawParameterHeader(rect, property, label);
        rect.y += LINE_HEIGHT + SPACING;
        
        // Draw type-specific controls
        DrawParameterControls(rect, property);
        
        // Draw validation if enabled
        if (property.FindPropertyRelative("enableValidation").boolValue)
        {
            rect.y += LINE_HEIGHT + SPACING;
            DrawValidationControls(rect, property);
        }
        
        // Draw real-time validation feedback
        DrawValidationFeedback(position, property);
        
        EditorGUI.EndProperty();
    }
    
    private void DrawParameterHeader(Rect rect, SerializedProperty property, GUIContent label)
    {
        var labelRect = new Rect(rect.x, rect.y, LABEL_WIDTH, rect.height);
        var typeRect = new Rect(rect.x + LABEL_WIDTH, rect.y, 80, rect.height);
        var enabledRect = new Rect(rect.x + LABEL_WIDTH + 85, rect.y, 15, rect.height);
        var resetRect = new Rect(rect.xMax - BUTTON_WIDTH, rect.y, BUTTON_WIDTH, rect.height);
        
        EditorGUI.LabelField(labelRect, label);
        
        var parameterType = property.FindPropertyRelative("parameterType");
        EditorGUI.PropertyField(typeRect, parameterType, GUIContent.none);
        
        var enabled = property.FindPropertyRelative("enabled");
        EditorGUI.PropertyField(enabledRect, enabled, GUIContent.none);
        
        if (GUI.Button(resetRect, "Reset"))
        {
            ResetParameterToDefault(property);
        }
    }
    
    private void DrawParameterControls(Rect rect, SerializedProperty property)
    {
        var parameterType = property.FindPropertyRelative("parameterType").enumValueIndex;
        var valueRect = new Rect(rect.x + LABEL_WIDTH, rect.y, rect.width - LABEL_WIDTH - BUTTON_WIDTH - 5, rect.height);
        
        switch (parameterType)
        {
            case 0: // Float
                DrawFloatParameter(valueRect, property);
                break;
            case 1: // Int
                DrawIntParameter(valueRect, property);
                break;
            case 2: // String
                DrawStringParameter(valueRect, property);
                break;
            case 3: // Vector3
                DrawVector3Parameter(valueRect, property);
                break;
        }
    }
    
    private void DrawFloatParameter(Rect rect, SerializedProperty property)
    {
        var floatValue = property.FindPropertyRelative("floatValue");
        var minValue = property.FindPropertyRelative("minFloat");
        var maxValue = property.FindPropertyRelative("maxFloat");
        var enableValidation = property.FindPropertyRelative("enableValidation");
        
        if (enableValidation.boolValue)
        {
            floatValue.floatValue = EditorGUI.Slider(rect, floatValue.floatValue, 
                minValue.floatValue, maxValue.floatValue);
        }
        else
        {
            EditorGUI.PropertyField(rect, floatValue, GUIContent.none);
        }
        
        // Visual feedback for out-of-range values
        if (enableValidation.boolValue && 
           (floatValue.floatValue < minValue.floatValue || floatValue.floatValue > maxValue.floatValue))
        {
            EditorGUI.DrawRect(rect, new Color(1, 0, 0, 0.1f));
        }
    }
}

/// <summary>
/// Data structure for gameplay parameters with validation
/// </summary>
[System.Serializable]
public class GameplayParameter
{
    public enum ParameterType
    {
        Float,
        Int,
        String,
        Vector3,
        Bool
    }
    
    [SerializeField] private ParameterType parameterType = ParameterType.Float;
    [SerializeField] private bool enabled = true;
    [SerializeField] private bool enableValidation = false;
    
    [SerializeField] private float floatValue;
    [SerializeField] private int intValue;
    [SerializeField] private string stringValue;
    [SerializeField] private Vector3 vector3Value;
    [SerializeField] private bool boolValue;
    
    // Validation parameters
    [SerializeField] private float minFloat = 0f;
    [SerializeField] private float maxFloat = 100f;
    [SerializeField] private int minInt = 0;
    [SerializeField] private int maxInt = 100;
    [SerializeField] private int maxStringLength = 50;
    
    public T GetValue<T>()
    {
        if (!enabled) return default(T);
        
        switch (parameterType)
        {
            case ParameterType.Float when typeof(T) == typeof(float):
                return (T)(object)floatValue;
            case ParameterType.Int when typeof(T) == typeof(int):
                return (T)(object)intValue;
            case ParameterType.String when typeof(T) == typeof(string):
                return (T)(object)stringValue;
            case ParameterType.Vector3 when typeof(T) == typeof(Vector3):
                return (T)(object)vector3Value;
            case ParameterType.Bool when typeof(T) == typeof(bool):
                return (T)(object)boolValue;
            default:
                throw new System.InvalidOperationException($"Cannot convert {parameterType} to {typeof(T)}");
        }
    }
    
    public bool IsValid()
    {
        if (!enableValidation) return true;
        
        switch (parameterType)
        {
            case ParameterType.Float:
                return floatValue >= minFloat && floatValue <= maxFloat;
            case ParameterType.Int:
                return intValue >= minInt && intValue <= maxInt;
            case ParameterType.String:
                return string.IsNullOrEmpty(stringValue) || stringValue.Length <= maxStringLength;
            default:
                return true;
        }
    }
}
```

### Professional Editor Window Development
```csharp
/// <summary>
/// Advanced editor window for game configuration management
/// Features docking, layout persistence, and professional UI
/// </summary>
public class GameConfigurationWindow : EditorWindow, IHasCustomMenu
{
    [MenuItem("Tools/Game Configuration Manager")]
    public static void ShowWindow()
    {
        var window = GetWindow<GameConfigurationWindow>("Game Config");
        window.minSize = new Vector2(400, 300);
        window.Show();
    }
    
    private enum TabType
    {
        General,
        Performance,
        Audio,
        Graphics,
        Input,
        Analytics
    }
    
    private TabType currentTab = TabType.General;
    private Vector2 scrollPosition;
    private GUIStyle tabStyle;
    private GUIStyle activeTabStyle;
    private GUIStyle contentStyle;
    
    private SerializedObject gameConfig;
    private Dictionary<TabType, IConfigurationTab> configTabs;
    
    void OnEnable()
    {
        InitializeStyles();
        LoadGameConfiguration();
        InitializeConfigurationTabs();
        
        // Subscribe to undo/redo events
        Undo.undoRedoPerformed += OnUndoRedoPerformed;
    }
    
    void OnDisable()
    {
        Undo.undoRedoPerformed -= OnUndoRedoPerformed;
        SaveWindowState();
    }
    
    void OnGUI()
    {
        if (gameConfig == null)
        {
            EditorGUILayout.HelpBox("No game configuration found. Create one to continue.", MessageType.Warning);
            if (GUILayout.Button("Create Game Configuration"))
            {
                CreateGameConfiguration();
            }
            return;
        }
        
        gameConfig.Update();
        
        DrawToolbar();
        DrawTabNavigation();
        DrawTabContent();
        
        if (gameConfig.hasModifiedProperties)
        {
            gameConfig.ApplyModifiedProperties();
        }
    }
    
    private void DrawToolbar()
    {
        EditorGUILayout.BeginHorizontal(EditorStyles.toolbar);
        
        if (GUILayout.Button("Save", EditorStyles.toolbarButton))
        {
            SaveConfiguration();
        }
        
        if (GUILayout.Button("Load", EditorStyles.toolbarButton))
        {
            LoadConfiguration();
        }
        
        GUILayout.Space(10);
        
        if (GUILayout.Button("Export", EditorStyles.toolbarButton))
        {
            ExportConfiguration();
        }
        
        if (GUILayout.Button("Import", EditorStyles.toolbarButton))
        {
            ImportConfiguration();
        }
        
        GUILayout.FlexibleSpace();
        
        if (GUILayout.Button("Reset All", EditorStyles.toolbarButton))
        {
            if (EditorUtility.DisplayDialog("Reset Configuration", 
                "Are you sure you want to reset all settings to default?", "Yes", "Cancel"))
            {
                ResetToDefaults();
            }
        }
        
        EditorGUILayout.EndHorizontal();
    }
    
    private void DrawTabNavigation()
    {
        EditorGUILayout.BeginHorizontal();
        
        foreach (TabType tab in System.Enum.GetValues(typeof(TabType)))
        {
            var style = (currentTab == tab) ? activeTabStyle : tabStyle;
            
            if (GUILayout.Button(tab.ToString(), style))
            {
                currentTab = tab;
                GUI.FocusControl(null);
            }
        }
        
        EditorGUILayout.EndHorizontal();
    }
    
    private void DrawTabContent()
    {
        EditorGUILayout.BeginVertical(contentStyle);
        scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);
        
        if (configTabs.ContainsKey(currentTab))
        {
            configTabs[currentTab].DrawContent(gameConfig);
        }
        else
        {
            EditorGUILayout.LabelField($"Tab '{currentTab}' not implemented yet.");
        }
        
        EditorGUILayout.EndScrollView();
        EditorGUILayout.EndVertical();
    }
    
    public void AddItemsToMenu(GenericMenu menu)
    {
        menu.AddItem(new GUIContent("Reset Window Layout"), false, ResetWindowLayout);
        menu.AddItem(new GUIContent("Export Settings..."), false, ExportConfiguration);
        menu.AddItem(new GUIContent("Import Settings..."), false, ImportConfiguration);
        menu.AddSeparator("");
        menu.AddItem(new GUIContent("Documentation"), false, OpenDocumentation);
    }
    
    private void InitializeConfigurationTabs()
    {
        configTabs = new Dictionary<TabType, IConfigurationTab>
        {
            [TabType.General] = new GeneralConfigTab(),
            [TabType.Performance] = new PerformanceConfigTab(),
            [TabType.Audio] = new AudioConfigTab(),
            [TabType.Graphics] = new GraphicsConfigTab(),
            [TabType.Input] = new InputConfigTab(),
            [TabType.Analytics] = new AnalyticsConfigTab()
        };
    }
}

/// <summary>
/// Interface for configuration tab implementations
/// </summary>
public interface IConfigurationTab
{
    void DrawContent(SerializedObject configObject);
    void ResetToDefaults(SerializedObject configObject);
    bool ValidateSettings(SerializedObject configObject);
}

/// <summary>
/// Example implementation of a configuration tab
/// </summary>
public class PerformanceConfigTab : IConfigurationTab
{
    private bool showAdvanced = false;
    
    public void DrawContent(SerializedObject configObject)
    {
        EditorGUILayout.LabelField("Performance Settings", EditorStyles.boldLabel);
        
        // Basic performance settings
        var targetFrameRate = configObject.FindProperty("targetFrameRate");
        var vSyncCount = configObject.FindProperty("vSyncCount");
        var qualityLevel = configObject.FindProperty("qualityLevel");
        
        EditorGUILayout.PropertyField(targetFrameRate);
        EditorGUILayout.PropertyField(vSyncCount);
        EditorGUILayout.PropertyField(qualityLevel);
        
        EditorGUILayout.Space();
        
        // Advanced settings toggle
        showAdvanced = EditorGUILayout.Foldout(showAdvanced, "Advanced Settings");
        
        if (showAdvanced)
        {
            EditorGUI.indentLevel++;
            
            var renderPipelineAsset = configObject.FindProperty("renderPipelineAsset");
            var lodBias = configObject.FindProperty("lodBias");
            var maximumLODLevel = configObject.FindProperty("maximumLODLevel");
            
            EditorGUILayout.PropertyField(renderPipelineAsset);
            EditorGUILayout.PropertyField(lodBias);
            EditorGUILayout.PropertyField(maximumLODLevel);
            
            EditorGUI.indentLevel--;
        }
        
        EditorGUILayout.Space();
        
        // Performance monitoring
        if (Application.isPlaying)
        {
            DrawPerformanceMetrics();
        }
    }
    
    private void DrawPerformanceMetrics()
    {
        EditorGUILayout.LabelField("Runtime Metrics", EditorStyles.boldLabel);
        EditorGUI.BeginDisabledGroup(true);
        
        EditorGUILayout.FloatField("Current FPS", 1f / Time.unscaledDeltaTime);
        EditorGUILayout.LongField("Memory Usage (MB)", System.GC.GetTotalMemory(false) / 1024 / 1024);
        EditorGUILayout.IntField("Draw Calls", UnityStats.drawCalls);
        EditorGUILayout.IntField("Triangles", UnityStats.triangles);
        
        EditorGUI.EndDisabledGroup();
    }
    
    public void ResetToDefaults(SerializedObject configObject)
    {
        configObject.FindProperty("targetFrameRate").intValue = 60;
        configObject.FindProperty("vSyncCount").intValue = 1;
        configObject.FindProperty("qualityLevel").intValue = 3;
    }
    
    public bool ValidateSettings(SerializedObject configObject)
    {
        var targetFrameRate = configObject.FindProperty("targetFrameRate").intValue;
        return targetFrameRate > 0 && targetFrameRate <= 120;
    }
}
```

## 🚀 AI/LLM Integration Opportunities
- **Tool Generation**: "Generate Unity custom inspector for player controller component"
- **Editor Workflow**: "Create automated Unity build pipeline with custom editor tools"
- **Property Drawer Design**: "Design complex property drawer for AI behavior tree nodes"
- **Documentation Generation**: "Generate documentation for custom Unity editor tools"

## 💡 Key Unity Editor Scripting Highlights
- **Professional UI Design**: Create polished, user-friendly editor interfaces
- **Data Validation**: Implement real-time validation and feedback systems
- **Workflow Automation**: Build tools that eliminate repetitive manual tasks
- **Extensibility**: Design modular systems that can be easily extended
- **Performance Optimization**: Ensure editor tools don't impact Unity performance
- **Team Integration**: Create tools that enhance collaborative development workflows