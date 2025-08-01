# @o-Custom-Editor-Tools-Scripting - Unity Editor Automation & Tools

## 🎯 Learning Objectives
- Master Unity Editor scripting for custom tools and workflows
- Create automated asset processing and generation systems
- Build custom inspector interfaces and property drawers
- Implement editor windows and scene view tools for enhanced productivity

## 🔧 Editor Scripting Fundamentals

### Custom Editor Windows
```csharp
using UnityEngine;
using UnityEditor;

public class CustomToolWindow : EditorWindow
{
    private string searchString = "";
    private Vector2 scrollPosition;
    private bool showAdvancedOptions = false;
    
    [MenuItem("Tools/Custom Tool Window")]
    public static void ShowWindow()
    {
        GetWindow<CustomToolWindow>("Custom Tools");
    }
    
    private void OnGUI()
    {
        GUILayout.Label("Custom Tool Window", EditorStyles.boldLabel);
        
        EditorGUILayout.Space();
        
        // Search functionality
        searchString = EditorGUILayout.TextField("Search:", searchString);
        
        // Scroll view for content
        scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);
        
        // Foldout for advanced options
        showAdvancedOptions = EditorGUILayout.Foldout(showAdvancedOptions, "Advanced Options");
        if (showAdvancedOptions)
        {
            EditorGUI.indentLevel++;
            
            if (GUILayout.Button("Process All Assets"))
            {
                ProcessAllAssets();
            }
            
            if (GUILayout.Button("Generate Documentation"))
            {
                GenerateDocumentation();
            }
            
            EditorGUI.indentLevel--;
        }
        
        EditorGUILayout.EndScrollView();
        
        // Status bar
        EditorGUILayout.Space();
        EditorGUILayout.LabelField("Status: Ready", EditorStyles.miniLabel);
    }
    
    private void ProcessAllAssets()
    {
        string[] assetPaths = AssetDatabase.FindAssets("t:ScriptableObject");
        
        EditorUtility.DisplayProgressBar("Processing Assets", "Starting...", 0f);
        
        for (int i = 0; i < assetPaths.Length; i++)
        {
            string path = AssetDatabase.GUIDToAssetPath(assetPaths[i]);
            EditorUtility.DisplayProgressBar("Processing Assets", $"Processing {path}", 
                (float)i / assetPaths.Length);
            
            // Process asset logic here
            System.Threading.Thread.Sleep(10); // Simulate processing time
        }
        
        EditorUtility.ClearProgressBar();
        Debug.Log($"Processed {assetPaths.Length} assets");
    }
    
    private void GenerateDocumentation()
    {
        // Documentation generation logic
        Debug.Log("Documentation generated successfully");
    }
}
```

### Custom Property Drawers
```csharp
using UnityEngine;
using UnityEditor;

[System.Serializable]
public class MinMaxRange
{
    public float minValue;
    public float maxValue;
    
    public MinMaxRange(float min, float max)
    {
        minValue = min;
        maxValue = max;
    }
}

[CustomPropertyDrawer(typeof(MinMaxRange))]
public class MinMaxRangeDrawer : PropertyDrawer
{
    public override void OnGUI(Rect position, SerializedProperty property, GUIContent label)
    {
        EditorGUI.BeginProperty(position, label, property);
        
        // Draw label
        position = EditorGUI.PrefixLabel(position, GUIUtility.GetControlID(FocusType.Passive), label);
        
        // Calculate rects
        var minRect = new Rect(position.x, position.y, 50, position.height);
        var sliderRect = new Rect(position.x + 55, position.y, position.width - 110, position.height);
        var maxRect = new Rect(position.x + position.width - 50, position.y, 50, position.height);
        
        // Get properties
        var minProp = property.FindPropertyRelative("minValue");
        var maxProp = property.FindPropertyRelative("maxValue");
        
        // Draw fields and slider
        float minValue = EditorGUI.FloatField(minRect, minProp.floatValue);
        float maxValue = EditorGUI.FloatField(maxRect, maxProp.floatValue);
        
        EditorGUI.MinMaxSlider(sliderRect, ref minValue, ref maxValue, 0f, 100f);
        
        // Ensure min is not greater than max
        if (minValue > maxValue) minValue = maxValue;
        
        minProp.floatValue = minValue;
        maxProp.floatValue = maxValue;
        
        EditorGUI.EndProperty();
    }
    
    public override float GetPropertyHeight(SerializedProperty property, GUIContent label)
    {
        return EditorGUIUtility.singleLineHeight;
    }
}
```

### Custom Inspector Scripts
```csharp
using UnityEngine;
using UnityEditor;

[System.Serializable]
public class GameObjectSettings : MonoBehaviour
{
    [Header("Transform Settings")]
    public bool lockPosition = false;
    public bool lockRotation = false;
    public bool lockScale = false;
    
    [Header("Rendering")]
    public bool enableShadows = true;
    public bool enableOcclusion = true;
    
    [Header("Audio")]
    [Range(0f, 1f)] public float volume = 1f;
    public AudioClip[] audioClips;
    
    [Header("Advanced")]
    public MinMaxRange healthRange = new MinMaxRange(0, 100);
}

[CustomEditor(typeof(GameObjectSettings))]
public class GameObjectSettingsEditor : Editor
{
    private bool showTransformSettings = true;
    private bool showRenderingSettings = true;
    private bool showAudioSettings = true;
    private bool showAdvancedSettings = false;
    
    public override void OnInspectorGUI()
    {
        serializedObject.Update();
        
        GameObjectSettings settings = (GameObjectSettings)target;
        
        // Custom header
        EditorGUILayout.Space();
        EditorGUILayout.LabelField("Game Object Settings", EditorStyles.boldLabel);
        EditorGUILayout.Space();
        
        // Transform Settings
        showTransformSettings = EditorGUILayout.BeginFoldoutHeaderGroup(showTransformSettings, "Transform Settings");
        if (showTransformSettings)
        {
            EditorGUI.indentLevel++;
            
            EditorGUILayout.PropertyField(serializedObject.FindProperty("lockPosition"));
            EditorGUILayout.PropertyField(serializedObject.FindProperty("lockRotation"));
            EditorGUILayout.PropertyField(serializedObject.FindProperty("lockScale"));
            
            // Quick buttons
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Lock All"))
            {
                settings.lockPosition = settings.lockRotation = settings.lockScale = true;
            }
            if (GUILayout.Button("Unlock All"))
            {
                settings.lockPosition = settings.lockRotation = settings.lockScale = false;
            }
            EditorGUILayout.EndHorizontal();
            
            EditorGUI.indentLevel--;
        }
        EditorGUILayout.EndFoldoutHeaderGroup();
        
        // Rendering Settings
        showRenderingSettings = EditorGUILayout.BeginFoldoutHeaderGroup(showRenderingSettings, "Rendering");
        if (showRenderingSettings)
        {
            EditorGUI.indentLevel++;
            EditorGUILayout.PropertyField(serializedObject.FindProperty("enableShadows"));
            EditorGUILayout.PropertyField(serializedObject.FindProperty("enableOcclusion"));
            EditorGUI.indentLevel--;
        }
        EditorGUILayout.EndFoldoutHeaderGroup();
        
        // Audio Settings
        showAudioSettings = EditorGUILayout.BeginFoldoutHeaderGroup(showAudioSettings, "Audio");
        if (showAudioSettings)
        {
            EditorGUI.indentLevel++;
            EditorGUILayout.PropertyField(serializedObject.FindProperty("volume"));
            EditorGUILayout.PropertyField(serializedObject.FindProperty("audioClips"), true);
            
            // Audio preview
            if (settings.audioClips != null && settings.audioClips.Length > 0)
            {
                EditorGUILayout.BeginHorizontal();
                EditorGUILayout.LabelField("Preview Audio:", GUILayout.Width(100));
                for (int i = 0; i < settings.audioClips.Length; i++)
                {
                    if (settings.audioClips[i] != null)
                    {
                        if (GUILayout.Button($"Play {i}", GUILayout.Width(60)))
                        {
                            AudioSource.PlayClipAtPoint(settings.audioClips[i], Vector3.zero, settings.volume);
                        }
                    }
                }
                EditorGUILayout.EndHorizontal();
            }
            
            EditorGUI.indentLevel--;
        }
        EditorGUILayout.EndFoldoutHeaderGroup();
        
        // Advanced Settings
        showAdvancedSettings = EditorGUILayout.BeginFoldoutHeaderGroup(showAdvancedSettings, "Advanced");
        if (showAdvancedSettings)
        {
            EditorGUI.indentLevel++;
            EditorGUILayout.PropertyField(serializedObject.FindProperty("healthRange"));
            EditorGUI.indentLevel--;
        }
        EditorGUILayout.EndFoldoutHeaderGroup();
        
        // Warning box
        if (settings.lockPosition && settings.lockRotation && settings.lockScale)
        {
            EditorGUILayout.HelpBox("All transform components are locked!", MessageType.Warning);
        }
        
        serializedObject.ApplyModifiedProperties();
    }
}
```

## 🛠️ Asset Processing and Automation

### Asset Post Processor
```csharp
using UnityEngine;
using UnityEditor;

public class CustomAssetPostprocessor : AssetPostprocessor
{
    // Texture import settings
    private void OnPreprocessTexture()
    {
        TextureImporter textureImporter = (TextureImporter)assetImporter;
        
        // Auto-configure texture settings based on folder
        if (assetPath.Contains("/UI/"))
        {
            ConfigureUITexture(textureImporter);
        }
        else if (assetPath.Contains("/Environment/"))
        {
            ConfigureEnvironmentTexture(textureImporter);
        }
        else if (assetPath.Contains("/Characters/"))
        {
            ConfigureCharacterTexture(textureImporter);
        }
    }
    
    private void ConfigureUITexture(TextureImporter importer)
    {
        importer.textureType = TextureImporterType.Sprite;
        importer.spriteImportMode = SpriteImportMode.Single;
        importer.filterMode = FilterMode.Bilinear;
        importer.mipmapEnabled = false;
        
        // Platform-specific settings
        var androidSettings = importer.GetPlatformTextureSettings("Android");
        androidSettings.overridden = true;
        androidSettings.format = TextureImporterFormat.ETC2_RGBA8;
        androidSettings.compressionQuality = 50;
        importer.SetPlatformTextureSettings(androidSettings);
        
        var iosSettings = importer.GetPlatformTextureSettings("iPhone");
        iosSettings.overridden = true;
        iosSettings.format = TextureImporterFormat.ASTC_6x6;
        iosSettings.compressionQuality = 50;
        importer.SetPlatformTextureSettings(iosSettings);
    }
    
    private void ConfigureEnvironmentTexture(TextureImporter importer)
    {
        importer.textureType = TextureImporterType.Default;
        importer.mipmapEnabled = true;
        importer.filterMode = FilterMode.Trilinear;
        importer.anisoLevel = 4;
    }
    
    private void ConfigureCharacterTexture(TextureImporter importer)
    {
        importer.textureType = TextureImporterType.Default;
        importer.mipmapEnabled = true;
        importer.filterMode = FilterMode.Trilinear;
        importer.anisoLevel = 8;
        
        // Enable normal map if contains "_Normal" in name
        if (assetPath.Contains("_Normal") || assetPath.Contains("_NRM"))
        {
            importer.textureType = TextureImporterType.NormalMap;
        }
    }
    
    // Audio import settings
    private void OnPreprocessAudio()
    {
        AudioImporter audioImporter = (AudioImporter)assetImporter;
        
        if (assetPath.Contains("/Music/"))
        {
            ConfigureMusicAudio(audioImporter);
        }
        else if (assetPath.Contains("/SFX/"))
        {
            ConfigureSFXAudio(audioImporter);
        }
        else if (assetPath.Contains("/Voice/"))
        {
            ConfigureVoiceAudio(audioImporter);
        }
    }
    
    private void ConfigureMusicAudio(AudioImporter importer)
    {
        var sampleSettings = importer.defaultSampleSettings;
        sampleSettings.loadType = AudioClipLoadType.Streaming;
        sampleSettings.compressionFormat = AudioCompressionFormat.Vorbis;
        sampleSettings.quality = 0.7f;
        importer.defaultSampleSettings = sampleSettings;
    }
    
    private void ConfigureSFXAudio(AudioImporter importer)
    {
        var sampleSettings = importer.defaultSampleSettings;
        sampleSettings.loadType = AudioClipLoadType.DecompressOnLoad;
        sampleSettings.compressionFormat = AudioCompressionFormat.Vorbis;
        sampleSettings.quality = 0.5f;
        importer.defaultSampleSettings = sampleSettings;
    }
    
    private void ConfigureVoiceAudio(AudioImporter importer)
    {
        var sampleSettings = importer.defaultSampleSettings;
        sampleSettings.loadType = AudioClipLoadType.CompressedInMemory;
        sampleSettings.compressionFormat = AudioCompressionFormat.Vorbis;
        sampleSettings.quality = 0.8f;
        importer.defaultSampleSettings = sampleSettings;
    }
}
```

### Batch Asset Operations
```csharp
using UnityEngine;
using UnityEditor;
using System.Collections.Generic;
using System.IO;

public class BatchAssetOperations : EditorWindow
{
    private enum OperationType
    {
        RenameAssets,
        MoveAssets,
        ConvertTextures,
        OptimizeAudio,
        GeneratePrefabs
    }
    
    private OperationType operationType = OperationType.RenameAssets;
    private string searchPattern = "";
    private string replacementText = "";
    private string targetFolder = "Assets/";
    
    [MenuItem("Tools/Batch Asset Operations")]
    public static void ShowWindow()
    {
        GetWindow<BatchAssetOperations>("Batch Operations");
    }
    
    private void OnGUI()
    {
        GUILayout.Label("Batch Asset Operations", EditorStyles.boldLabel);
        EditorGUILayout.Space();
        
        operationType = (OperationType)EditorGUILayout.EnumPopup("Operation Type:", operationType);
        EditorGUILayout.Space();
        
        switch (operationType)
        {
            case OperationType.RenameAssets:
                DrawRenameGUI();
                break;
            case OperationType.MoveAssets:
                DrawMoveGUI();
                break;
            case OperationType.ConvertTextures:
                DrawTextureConversionGUI();
                break;
            case OperationType.OptimizeAudio:
                DrawAudioOptimizationGUI();
                break;
            case OperationType.GeneratePrefabs:
                DrawPrefabGenerationGUI();
                break;
        }
        
        EditorGUILayout.Space();
        
        if (GUILayout.Button("Execute Operation", GUILayout.Height(30)))
        {
            ExecuteOperation();
        }
    }
    
    private void DrawRenameGUI()
    {
        searchPattern = EditorGUILayout.TextField("Search Pattern:", searchPattern);
        replacementText = EditorGUILayout.TextField("Replace With:", replacementText);
        
        EditorGUILayout.HelpBox("This will rename all assets matching the search pattern.", MessageType.Info);
    }
    
    private void DrawMoveGUI()
    {
        searchPattern = EditorGUILayout.TextField("Asset Filter:", searchPattern);
        targetFolder = EditorGUILayout.TextField("Target Folder:", targetFolder);
        
        if (GUILayout.Button("Select Folder"))
        {
            string selectedPath = EditorUtility.OpenFolderPanel("Select Target Folder", "Assets", "");
            if (!string.IsNullOrEmpty(selectedPath))
            {
                targetFolder = "Assets" + selectedPath.Substring(Application.dataPath.Length);
            }
        }
    }
    
    private void DrawTextureConversionGUI()
    {
        EditorGUILayout.LabelField("Convert all textures to optimized formats");
        EditorGUILayout.HelpBox("This will apply platform-specific compression to all textures.", MessageType.Info);
    }
    
    private void DrawAudioOptimizationGUI()
    {
        EditorGUILayout.LabelField("Optimize audio files for different platforms");
        EditorGUILayout.HelpBox("This will apply compression settings based on audio type.", MessageType.Info);
    }
    
    private void DrawPrefabGenerationGUI()
    {
        targetFolder = EditorGUILayout.TextField("Prefab Output Folder:", targetFolder);
        EditorGUILayout.HelpBox("Generate prefabs from selected GameObjects in scene.", MessageType.Info);
    }
    
    private void ExecuteOperation()
    {
        switch (operationType)
        {
            case OperationType.RenameAssets:
                RenameAssets();
                break;
            case OperationType.MoveAssets:
                MoveAssets();
                break;
            case OperationType.ConvertTextures:
                ConvertTextures();
                break;
            case OperationType.OptimizeAudio:
                OptimizeAudio();
                break;
            case OperationType.GeneratePrefabs:
                GeneratePrefabs();
                break;
        }
        
        AssetDatabase.Refresh();
    }
    
    private void RenameAssets()
    {
        string[] guids = AssetDatabase.FindAssets(searchPattern);
        int renamed = 0;
        
        foreach (string guid in guids)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            string fileName = Path.GetFileNameWithoutExtension(path);
            
            if (fileName.Contains(searchPattern))
            {
                string newFileName = fileName.Replace(searchPattern, replacementText);
                string newPath = Path.GetDirectoryName(path) + "/" + newFileName + Path.GetExtension(path);
                
                AssetDatabase.RenameAsset(path, newFileName);
                renamed++;
            }
        }
        
        Debug.Log($"Renamed {renamed} assets");
    }
    
    private void MoveAssets()
    {
        string[] guids = AssetDatabase.FindAssets(searchPattern);
        int moved = 0;
        
        // Ensure target folder exists
        if (!AssetDatabase.IsValidFolder(targetFolder))
        {
            Directory.CreateDirectory(targetFolder);
            AssetDatabase.Refresh();
        }
        
        foreach (string guid in guids)
        {
            string oldPath = AssetDatabase.GUIDToAssetPath(guid);
            string fileName = Path.GetFileName(oldPath);
            string newPath = targetFolder + "/" + fileName;
            
            AssetDatabase.MoveAsset(oldPath, newPath);
            moved++;
        }
        
        Debug.Log($"Moved {moved} assets to {targetFolder}");
    }
    
    private void ConvertTextures()
    {
        string[] textureGuids = AssetDatabase.FindAssets("t:Texture2D");
        int converted = 0;
        
        foreach (string guid in textureGuids)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
            
            if (importer != null)
            {
                // Apply platform-specific settings
                ApplyTextureOptimization(importer);
                AssetDatabase.ImportAsset(path);
                converted++;
            }
        }
        
        Debug.Log($"Optimized {converted} textures");
    }
    
    private void ApplyTextureOptimization(TextureImporter importer)
    {
        // Android settings
        var androidSettings = importer.GetPlatformTextureSettings("Android");
        androidSettings.overridden = true;
        androidSettings.format = TextureImporterFormat.ETC2_RGBA8;
        androidSettings.compressionQuality = 50;
        importer.SetPlatformTextureSettings(androidSettings);
        
        // iOS settings
        var iosSettings = importer.GetPlatformTextureSettings("iPhone");
        iosSettings.overridden = true;
        iosSettings.format = TextureImporterFormat.ASTC_6x6;
        iosSettings.compressionQuality = 50;
        importer.SetPlatformTextureSettings(iosSettings);
    }
    
    private void OptimizeAudio()
    {
        string[] audioGuids = AssetDatabase.FindAssets("t:AudioClip");
        int optimized = 0;
        
        foreach (string guid in audioGuids)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            AudioImporter importer = AssetImporter.GetAtPath(path) as AudioImporter;
            
            if (importer != null)
            {
                ApplyAudioOptimization(importer);
                AssetDatabase.ImportAsset(path);
                optimized++;
            }
        }
        
        Debug.Log($"Optimized {optimized} audio files");
    }
    
    private void ApplyAudioOptimization(AudioImporter importer)
    {
        var settings = importer.defaultSampleSettings;
        
        if (importer.assetPath.Contains("Music"))
        {
            settings.loadType = AudioClipLoadType.Streaming;
            settings.compressionFormat = AudioCompressionFormat.Vorbis;
            settings.quality = 0.7f;
        }
        else
        {
            settings.loadType = AudioClipLoadType.DecompressOnLoad;
            settings.compressionFormat = AudioCompressionFormat.Vorbis;
            settings.quality = 0.5f;
        }
        
        importer.defaultSampleSettings = settings;
    }
    
    private void GeneratePrefabs()
    {
        GameObject[] selectedObjects = Selection.gameObjects;
        int generated = 0;
        
        foreach (GameObject obj in selectedObjects)
        {
            string prefabPath = targetFolder + "/" + obj.name + ".prefab";
            PrefabUtility.SaveAsPrefabAsset(obj, prefabPath);
            generated++;
        }
        
        Debug.Log($"Generated {generated} prefabs in {targetFolder}");
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Editor Tool Generation
- **Custom Tool Creation**: Generate editor tools based on workflow descriptions
- **Inspector Automation**: AI-generated custom inspectors for complex components
- **Asset Processing**: Automated asset pipeline configuration and optimization

### Code Analysis and Generation
- **Script Templates**: Generate editor script templates for common patterns
- **Performance Analysis**: AI-assisted analysis of editor tool performance
- **Documentation Generation**: Automatically document custom editor tools and workflows

### Workflow Optimization
- **Process Automation**: Identify and automate repetitive editor tasks
- **Tool Integration**: Connect multiple editor tools for seamless workflows
- **Performance Monitoring**: Track and optimize editor tool usage patterns

## 💡 Key Highlights

- **Master Editor Scripting** with custom windows, inspectors, and property drawers
- **Automate Asset Processing** with post-processors and batch operations
- **Create Reusable Tools** for enhanced productivity and team efficiency
- **Implement Custom Workflows** tailored to specific project requirements
- **Leverage AI Integration** for tool generation and optimization
- **Build Comprehensive Toolsets** for professional Unity development
- **Focus on Team Productivity** with shared editor tools and standardized workflows