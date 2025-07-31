# e_Package-Management-Dependencies

## 🎯 Learning Objectives
- Master Unity Package Manager and external dependency management
- Implement efficient asset pipeline workflows for team collaboration
- Configure build systems and continuous integration for Unity projects
- Optimize development workflows using package management best practices

## 🔧 Unity Package Manager Fundamentals

### Package Manager Interface and Operations
```csharp
// Example package manifest configuration
// Packages/manifest.json
{
  "dependencies": {
    "com.unity.addressables": "1.21.17",
    "com.unity.cinemachine": "2.9.7",
    "com.unity.inputsystem": "1.7.0",
    "com.unity.render-pipelines.universal": "14.0.8",
    "com.unity.textmeshpro": "3.0.6",
    "com.unity.timeline": "1.7.5",
    "com.unity.visualscripting": "1.8.0"
  },
  "scopedRegistries": [
    {
      "name": "Custom Package Registry",
      "url": "https://npm.pkg.github.com/@yourcompany",
      "scopes": ["com.yourcompany"]
    }
  ]
}
```

### Custom Package Development
```csharp
// Example custom package structure
// Packages/com.yourcompany.utilities/package.json
{
  "name": "com.yourcompany.utilities",
  "version": "1.0.0",
  "displayName": "Company Utilities",
  "description": "Common utilities and tools for company projects",
  "unity": "2022.3",
  "unityRelease": "0f1",
  "dependencies": {
    "com.unity.textmeshpro": "3.0.6"
  },
  "keywords": ["utilities", "tools", "common"],
  "author": {
    "name": "Your Company",
    "email": "dev@yourcompany.com",
    "url": "https://yourcompany.com"
  }
}

// Runtime utility example
// Packages/com.yourcompany.utilities/Runtime/GameObjectExtensions.cs
using UnityEngine;

namespace YourCompany.Utilities
{
    public static class GameObjectExtensions
    {
        public static T GetOrAddComponent<T>(this GameObject gameObject) where T : Component
        {
            T component = gameObject.GetComponent<T>();
            if (component == null)
            {
                component = gameObject.AddComponent<T>();
            }
            return component;
        }
        
        public static void DestroyAllChildren(this Transform transform)
        {
            for (int i = transform.childCount - 1; i >= 0; i--)
            {
                if (Application.isPlaying)
                {
                    Object.Destroy(transform.GetChild(i).gameObject);
                }
                else
                {
                    Object.DestroyImmediate(transform.GetChild(i).gameObject);
                }
            }
        }
    }
}
```

### Assembly Definition Management
```csharp
// Example Assembly Definition file
// Scripts/Runtime/CompanyUtilities.asmdef
{
    "name": "CompanyUtilities",
    "rootNamespace": "YourCompany.Utilities",
    "references": [
        "Unity.TextMeshPro",
        "Unity.InputSystem",
        "Unity.Addressables"
    ],
    "includePlatforms": [],
    "excludePlatforms": [],
    "allowUnsafeCode": false,
    "overrideReferences": false,
    "precompiledReferences": [],
    "autoReferenced": true,
    "defineConstraints": [],
    "versionDefines": [
        {
            "name": "com.unity.inputsystem",
            "expression": "1.0.0",
            "define": "INPUT_SYSTEM_ENABLED"
        }
    ],
    "noEngineReferences": false
}

// Conditional compilation example
#if INPUT_SYSTEM_ENABLED
using UnityEngine.InputSystem;
#endif

public class InputManager : MonoBehaviour
{
#if INPUT_SYSTEM_ENABLED
    private PlayerInput playerInput;
    
    void Start()
    {
        playerInput = GetComponent<PlayerInput>();
        if (playerInput != null)
        {
            playerInput.onActionTriggered += OnActionTriggered;
        }
    }
    
    private void OnActionTriggered(InputAction.CallbackContext context)
    {
        // Handle input using new Input System
    }
#else
    void Update()
    {
        // Fallback to legacy Input Manager
        if (Input.GetKeyDown(KeyCode.Space))
        {
            // Handle input using legacy system
        }
    }
#endif
}
```

## 🔧 External Package Management

### NuGet Integration for Unity
```csharp
// Example NuGet package integration
// Using NuGetForUnity or other NuGet solutions

// Packages/packages.config (for NuGetForUnity)
<?xml version="1.0" encoding="utf-8"?>
<packages>
  <package id="Newtonsoft.Json" version="13.0.3" targetFramework="net471" />
  <package id="System.Threading.Tasks.Extensions" version="4.5.4" targetFramework="net471" />
</packages>

// Using external libraries in Unity
using Newtonsoft.Json;
using System.Threading.Tasks;

[System.Serializable]
public class GameData
{
    public string playerName;
    public int level;
    public float[] position;
    public Dictionary<string, object> customData;
}

public class DataManager : MonoBehaviour
{
    private const string SAVE_FILE = "gamedata.json";
    
    public async Task SaveGameDataAsync(GameData data)
    {
        try
        {
            string json = JsonConvert.SerializeObject(data, Formatting.Indented);
            string filePath = Path.Combine(Application.persistentDataPath, SAVE_FILE);
            
            await File.WriteAllTextAsync(filePath, json);
            Debug.Log("Game data saved successfully");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Failed to save game data: {e.Message}");
        }
    }
    
    public async Task<GameData> LoadGameDataAsync()
    {
        try
        {
            string filePath = Path.Combine(Application.persistentDataPath, SAVE_FILE);
            
            if (!File.Exists(filePath))
            {
                return new GameData();
            }
            
            string json = await File.ReadAllTextAsync(filePath);
            return JsonConvert.DeserializeObject<GameData>(json);
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Failed to load game data: {e.Message}");
            return new GameData();
        }
    }
}
```

### Git Submodules for Shared Libraries
```bash
# Adding submodules for shared code libraries
git submodule add https://github.com/yourcompany/unity-common-utilities.git Assets/Plugins/CommonUtilities
git submodule add https://github.com/yourcompany/unity-networking-framework.git Assets/Plugins/NetworkingFramework

# Initialize and update submodules
git submodule init
git submodule update

# Update all submodules to latest
git submodule update --remote

# .gitmodules configuration
[submodule "Assets/Plugins/CommonUtilities"]
	path = Assets/Plugins/CommonUtilities
	url = https://github.com/yourcompany/unity-common-utilities.git
	branch = main
[submodule "Assets/Plugins/NetworkingFramework"]
	path = Assets/Plugins/NetworkingFramework
	url = https://github.com/yourcompany/unity-networking-framework.git
	branch = develop
```

## 🔧 Asset Pipeline and Build Management

### Addressable Asset System
```csharp
// Addressable asset management
using UnityEngine;
using UnityEngine.AddressableAssets;
using UnityEngine.ResourceManagement.AsyncOperations;
using System.Collections.Generic;

public class AssetManager : MonoBehaviour
{
    [Header("Asset Configuration")]
    public List<AssetReferenceGameObject> prefabReferences;
    public List<AssetReferenceTexture2D> textureReferences;
    public List<AssetReferenceAudioClip> audioReferences;
    
    private Dictionary<string, GameObject> loadedPrefabs = new Dictionary<string, GameObject>();
    private Dictionary<string, AsyncOperationHandle> loadOperations = new Dictionary<string, AsyncOperationHandle>();
    
    public async void LoadAssetAsync<T>(AssetReference assetRef, System.Action<T> onComplete) where T : Object
    {
        if (assetRef == null || !assetRef.RuntimeKeyIsValid())
        {
            Debug.LogError("Invalid asset reference");
            onComplete?.Invoke(null);
            return;
        }
        
        try
        {
            var handle = Addressables.LoadAssetAsync<T>(assetRef);
            loadOperations[assetRef.AssetGUID] = handle;
            
            T result = await handle.Task;
            onComplete?.Invoke(result);
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Failed to load asset: {e.Message}");
            onComplete?.Invoke(null);
        }
    }
    
    public void LoadPrefabAndInstantiate(AssetReferenceGameObject prefabRef, Vector3 position, System.Action<GameObject> onComplete)
    {
        LoadAssetAsync<GameObject>(prefabRef, (prefab) =>
        {
            if (prefab != null)
            {
                GameObject instance = Instantiate(prefab, position, Quaternion.identity);
                onComplete?.Invoke(instance);
            }
            else
            {
                onComplete?.Invoke(null);
            }
        });
    }
    
    public void UnloadAsset(AssetReference assetRef)
    {
        if (loadOperations.TryGetValue(assetRef.AssetGUID, out AsyncOperationHandle handle))
        {
            Addressables.Release(handle);
            loadOperations.Remove(assetRef.AssetGUID);
        }
    }
    
    void OnDestroy()
    {
        // Clean up all loaded assets
        foreach (var handle in loadOperations.Values)
        {
            if (handle.IsValid())
            {
                Addressables.Release(handle);
            }
        }
        loadOperations.Clear();
    }
}

// Build script for automated addressable builds
#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.AddressableAssets.Settings;
using UnityEditor.AddressableAssets.Build;

public static class AddressableBuildScript
{
    [MenuItem("Build/Build Addressables")]
    public static void BuildAddressables()
    {
        AddressableAssetSettings.CleanPlayerContent();
        AddressableAssetSettings.BuildPlayerContent();
        Debug.Log("Addressable build completed");
    }
    
    public static void BuildAddressablesForPlatform(BuildTarget target)
    {
        var settings = AddressableAssetSettingsDefaultObject.Settings;
        var buildScript = settings.DataBuilders[0] as IDataBuilder;
        
        var buildContext = new AddressablesDataBuilderInput(settings)
        {
            RuntimeCatalogFilename = "catalog.json",
            RuntimeSettingsFilename = "settings.json"
        };
        
        buildScript.BuildData<AddressableAssetBuildResult>(buildContext);
    }
}
#endif
```

### Continuous Integration Setup
```yaml
# GitHub Actions workflow for Unity builds
# .github/workflows/unity-build.yml
name: Unity Build and Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    name: Build Unity Project
    runs-on: ubuntu-latest
    
    strategy:
      fail-fast: false
      matrix:
        projectPath:
          - .
        unityVersion:
          - 2022.3.21f1
        targetPlatform:
          - StandaloneWindows64
          - StandaloneOSX
          - StandaloneLinux64
          - WebGL
          - Android
          - iOS
    
    steps:
      # Checkout repository
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          lfs: true
      
      # Git LFS checkout
      - name: Checkout LFS objects
        run: git lfs checkout
      
      # Cache Unity Library folder
      - uses: actions/cache@v3
        with:
          path: ${{ matrix.projectPath }}/Library
          key: Library-${{ matrix.projectPath }}-${{ matrix.targetPlatform }}-${{ hashFiles(matrix.projectPath + '/Packages/packages-lock.json') }}
          restore-keys: |
            Library-${{ matrix.projectPath }}-${{ matrix.targetPlatform }}-
            Library-${{ matrix.projectPath }}-
      
      # Run Unity tests
      - name: Run Unity Tests
        uses: game-ci/unity-test-runner@v4
        env:
          UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}
          UNITY_EMAIL: ${{ secrets.UNITY_EMAIL }}
          UNITY_PASSWORD: ${{ secrets.UNITY_PASSWORD }}
        with:
          projectPath: ${{ matrix.projectPath }}
          unityVersion: ${{ matrix.unityVersion }}
          githubToken: ${{ secrets.GITHUB_TOKEN }}
      
      # Build Unity project
      - name: Build Unity Project
        uses: game-ci/unity-builder@v4
        env:
          UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}
          UNITY_EMAIL: ${{ secrets.UNITY_EMAIL }}
          UNITY_PASSWORD: ${{ secrets.UNITY_PASSWORD }}
        with:
          projectPath: ${{ matrix.projectPath }}
          unityVersion: ${{ matrix.unityVersion }}
          targetPlatform: ${{ matrix.targetPlatform }}
          customImage: 'unityci/editor:ubuntu-2022.3.21f1-base-3.0.0'
      
      # Upload build artifacts
      - name: Upload Build Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: Build-${{ matrix.targetPlatform }}
          path: build/${{ matrix.targetPlatform }}
          retention-days: 7
```

## 🔧 Development Workflow Optimization

### Editor Scripts for Package Management
```csharp
#if UNITY_EDITOR
using UnityEngine;
using UnityEditor;
using UnityEditor.PackageManager;
using UnityEditor.PackageManager.Requests;
using System.Collections.Generic;

public class PackageManagerUtility : EditorWindow
{
    private static readonly Dictionary<string, string> CommonPackages = new Dictionary<string, string>
    {
        { "Addressables", "com.unity.addressables" },
        { "Cinemachine", "com.unity.cinemachine" },
        { "Input System", "com.unity.inputsystem" },
        { "Timeline", "com.unity.timeline" },
        { "Visual Scripting", "com.unity.visualscripting" },
        { "Universal Render Pipeline", "com.unity.render-pipelines.universal" },
        { "ProBuilder", "com.unity.probuilder" },
        { "ProGrid", "com.unity.progrids" }
    };
    
    private Vector2 scrollPosition;
    private static AddRequest addRequest;
    private static RemoveRequest removeRequest;
    private static ListRequest listRequest;
    
    [MenuItem("Tools/Package Manager Utility")]
    public static void ShowWindow()
    {
        GetWindow<PackageManagerUtility>("Package Manager Utility");
    }
    
    void OnGUI()
    {
        GUILayout.Label("Unity Package Manager Utility", EditorStyles.boldLabel);
        EditorGUILayout.Space();
        
        if (GUILayout.Button("Refresh Package List"))
        {
            RefreshPackageList();
        }
        
        EditorGUILayout.Space();
        GUILayout.Label("Quick Install Common Packages:", EditorStyles.boldLabel);
        
        scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);
        
        foreach (var package in CommonPackages)
        {
            EditorGUILayout.BeginHorizontal();
            GUILayout.Label(package.Key, GUILayout.Width(200));
            
            if (GUILayout.Button("Install", GUILayout.Width(100)))
            {
                InstallPackage(package.Value);
            }
            
            if (GUILayout.Button("Remove", GUILayout.Width(100)))
            {
                RemovePackage(package.Value);
            }
            
            EditorGUILayout.EndHorizontal();
        }
        
        EditorGUILayout.EndScrollView();
        
        EditorGUILayout.Space();
        
        if (GUILayout.Button("Setup Complete Development Environment"))
        {
            SetupDevelopmentEnvironment();
        }
    }
    
    void Update()
    {
        if (addRequest != null && addRequest.IsCompleted)
        {
            if (addRequest.Status == StatusCode.Success)
            {
                Debug.Log($"Successfully installed package: {addRequest.Result.displayName}");
            }
            else
            {
                Debug.LogError($"Failed to install package: {addRequest.Error.message}");
            }
            addRequest = null;
        }
        
        if (removeRequest != null && removeRequest.IsCompleted)
        {
            if (removeRequest.Status == StatusCode.Success)
            {
                Debug.Log("Successfully removed package");
            }
            else
            {
                Debug.LogError($"Failed to remove package: {removeRequest.Error.message}");
            }
            removeRequest = null;
        }
    }
    
    void InstallPackage(string packageName)
    {
        if (addRequest == null)
        {
            addRequest = Client.Add(packageName);
            EditorApplication.update += CheckInstallProgress;
        }
    }
    
    void RemovePackage(string packageName)
    {
        if (removeRequest == null)
        {
            removeRequest = Client.Remove(packageName);
            EditorApplication.update += CheckRemoveProgress;
        }
    }
    
    void CheckInstallProgress()
    {
        if (addRequest.IsCompleted)
        {
            EditorApplication.update -= CheckInstallProgress;
            Repaint();
        }
    }
    
    void CheckRemoveProgress()
    {
        if (removeRequest.IsCompleted)
        {
            EditorApplication.update -= CheckRemoveProgress;
            Repaint();
        }
    }
    
    void RefreshPackageList()
    {
        listRequest = Client.List();
    }
    
    void SetupDevelopmentEnvironment()
    {
        // Install essential packages for development
        string[] essentialPackages = {
            "com.unity.addressables",
            "com.unity.inputsystem",
            "com.unity.cinemachine",
            "com.unity.timeline"
        };
        
        foreach (string package in essentialPackages)
        {
            Client.Add(package);
        }
        
        // Create standard folder structure
        CreateFolderStructure();
        
        Debug.Log("Development environment setup initiated");
    }
    
    void CreateFolderStructure()
    {
        string[] folders = {
            "Assets/_Project",
            "Assets/_Project/Scripts",
            "Assets/_Project/Scripts/Runtime",
            "Assets/_Project/Scripts/Editor",
            "Assets/_Project/Prefabs",
            "Assets/_Project/Materials",
            "Assets/_Project/Textures",
            "Assets/_Project/Audio",
            "Assets/_Project/Scenes",
            "Assets/_Project/Animation",
            "Assets/_Project/UI"
        };
        
        foreach (string folder in folders)
        {
            if (!AssetDatabase.IsValidFolder(folder))
            {
                string parentFolder = System.IO.Path.GetDirectoryName(folder).Replace('\\', '/');
                string folderName = System.IO.Path.GetFileName(folder);
                AssetDatabase.CreateFolder(parentFolder, folderName);
            }
        }
        
        AssetDatabase.Refresh();
    }
}
#endif
```

## 🚀 AI/LLM Integration Opportunities

### Content Generation Prompts
```
"Generate a Unity package.json configuration for [package type] with proper dependencies and versioning. Include assembly definitions and documentation structure."

"Create a build script for [platform] that handles [specific requirements] using Unity Cloud Build or GitHub Actions. Include error handling and notification systems."

"Design a package management workflow for [team size] working on [project type]. Include version control integration and dependency conflict resolution."
```

### Learning Acceleration
- **Package Discovery**: "Find Unity packages for [specific functionality] and compare their features, performance, and licensing"
- **Integration Guidance**: "How do I integrate [external library] with Unity while maintaining cross-platform compatibility?"
- **Workflow Optimization**: "Optimize our asset pipeline for [team size] developers working on [project scale]"

### Advanced Applications
- **Custom Package Development**: Creating reusable components and tools as Unity packages
- **Build Pipeline Automation**: Automated testing, building, and deployment workflows
- **Asset Optimization**: Automated asset processing and optimization pipelines

## 💡 Key Highlights

### Package Management Best Practices
- **Semantic Versioning**: Follow semver (major.minor.patch) for package versions
- **Dependency Management**: Keep dependencies minimal and well-documented
- **Assembly Definitions**: Use proper assembly separation for faster compilation
- **Package Documentation**: Include comprehensive README and API documentation

### Version Control Integration
- **Git LFS**: Use for large assets (textures, audio, models)
- **.gitignore Configuration**: Proper exclusion of generated files and caches
- **Branching Strategy**: Feature branches for package development and testing
- **Submodule Management**: Careful handling of shared library dependencies

### Build System Optimization
- **Incremental Builds**: Minimize rebuild times through proper dependency management
- **Platform-Specific Configurations**: Conditional compilation and asset variants
- **Automated Testing**: Unit tests and integration tests in CI/CD pipeline
- **Artifact Management**: Proper storage and versioning of build outputs

### Team Collaboration Features
- **Shared Package Registries**: Custom registries for internal packages
- **Version Locking**: Consistent package versions across team members
- **Documentation Standards**: Clear package documentation and usage examples
- **Review Processes**: Code review workflows for package modifications

### Performance Considerations
- **Compilation Time**: Assembly definitions reduce compilation scope
- **Runtime Performance**: Package overhead and initialization costs
- **Memory Usage**: Asset loading strategies and memory management
- **Build Size**: Package inclusion impact on final build size

### Integration Patterns
- **Addressable Integration**: Seamless asset loading and management
- **Input System**: Modern input handling across platforms
- **Render Pipelines**: Compatibility with URP/HDRP rendering systems
- **Platform Services**: Integration with platform-specific features and SDKs

This comprehensive package management and dependency system knowledge provides the foundation for efficient Unity development workflows and effective team collaboration.