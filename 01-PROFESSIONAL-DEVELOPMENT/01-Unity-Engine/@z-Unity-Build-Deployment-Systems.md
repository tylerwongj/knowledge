# @z-Unity-Build-Deployment-Systems - Complete Build Pipeline Guide

## 🎯 Learning Objectives
- Master Unity's build system and deployment workflows
- Understand platform-specific build configurations and optimizations
- Learn CI/CD integration for automated builds
- Apply AI/LLM tools to streamline build automation and deployment

---

## 🔧 Unity Build System Fundamentals

### Build Settings Overview
Unity's build system transforms your project into platform-specific applications:

```csharp
// Build configuration script
using UnityEditor;
using UnityEngine;

public class BuildConfigurationManager : EditorWindow
{
    [MenuItem("Build/Configuration Manager")]
    static void Init()
    {
        BuildConfigurationManager window = GetWindow<BuildConfigurationManager>();
        window.Show();
    }
    
    private BuildTarget selectedPlatform = BuildTarget.StandaloneWindows64;
    private string buildPath = "Builds/";
    private bool developmentBuild = false;
    private bool allowDebugging = false;
    
    void OnGUI()
    {
        GUILayout.Label("Build Configuration", EditorStyles.boldLabel);
        
        selectedPlatform = (BuildTarget)EditorGUILayout.EnumPopup("Platform", selectedPlatform);
        buildPath = EditorGUILayout.TextField("Build Path", buildPath);
        developmentBuild = EditorGUILayout.Toggle("Development Build", developmentBuild);
        allowDebugging = EditorGUILayout.Toggle("Allow Debugging", allowDebugging);
        
        if (GUILayout.Button("Build"))
        {
            BuildProject();
        }
    }
    
    void BuildProject()
    {
        BuildPlayerOptions buildOptions = new BuildPlayerOptions
        {
            scenes = EditorBuildSettings.scenes
                .Where(scene => scene.enabled)
                .Select(scene => scene.path)
                .ToArray(),
            locationPathName = buildPath + GetBuildName(),
            target = selectedPlatform,
            options = GetBuildOptions()
        };
        
        BuildPipeline.BuildPlayer(buildOptions);
    }
    
    string GetBuildName()
    {
        string platformName = selectedPlatform.ToString();
        string timestamp = System.DateTime.Now.ToString("yyyyMMdd_HHmmss");
        return $"{Application.productName}_{platformName}_{timestamp}";
    }
    
    BuildOptions GetBuildOptions()
    {
        BuildOptions options = BuildOptions.None;
        
        if (developmentBuild)
            options |= BuildOptions.Development;
        
        if (allowDebugging)
            options |= BuildOptions.AllowDebugging;
        
        return options;
    }
}
```

---

## 🏗️ Platform-Specific Build Configurations

### Windows/Mac/Linux Standalone
Desktop platform builds with full feature support:

```csharp
public class StandaloneBuildConfig : MonoBehaviour
{
    [Header("Standalone Settings")]
    public bool createInstaller = true;
    public string companyName = "Your Company";
    public string productName = "Your Game";
    
    [RuntimeInitializeOnLoadMethod]
    static void ConfigureStandaloneSettings()
    {
        #if UNITY_EDITOR
        // Configure standalone-specific settings
        PlayerSettings.companyName = "Your Company";
        PlayerSettings.productName = "Your Game";
        PlayerSettings.runInBackground = true;
        PlayerSettings.displayResolutionDialog = ResolutionDialogSetting.Enabled;
        PlayerSettings.defaultIsNativeResolution = true;
        
        // Graphics settings
        PlayerSettings.colorSpace = ColorSpace.Linear;
        PlayerSettings.gpuSkinning = true;
        
        // Optimization
        PlayerSettings.stripEngineCode = true;
        PlayerSettings.managedStrippingLevel = ManagedStrippingLevel.Medium;
        #endif
    }
    
    #if UNITY_EDITOR
    [MenuItem("Build/Configure Standalone Build")]
    static void ConfigureStandaloneBuild()
    {
        EditorUserBuildSettings.SwitchActiveBuildTarget(
            BuildTargetGroup.Standalone, 
            BuildTarget.StandaloneWindows64
        );
        
        BuildPlayerOptions buildOptions = new BuildPlayerOptions
        {
            scenes = EditorBuildSettings.scenes
                .Where(scene => scene.enabled)
                .Select(scene => scene.path)
                .ToArray(),
            locationPathName = "Builds/Standalone/" + Application.productName + ".exe",
            target = BuildTarget.StandaloneWindows64,
            options = BuildOptions.None
        };
        
        BuildPipeline.BuildPlayer(buildOptions);
    }
    #endif
}
```

### Mobile (iOS/Android) Build Pipeline
Mobile-optimized build configurations:

```csharp
public class MobileBuildConfig : MonoBehaviour
{
    [Header("Mobile Settings")]
    public bool enableGPUInstancing = true;
    public bool useMultithreadedRendering = true;
    public int targetFrameRate = 60;
    
    #if UNITY_EDITOR
    [MenuItem("Build/Configure Mobile Build")]
    static void ConfigureMobileBuild()
    {
        // Android-specific settings
        if (EditorUserBuildSettings.activeBuildTarget == BuildTarget.Android)
        {
            ConfigureAndroidBuild();
        }
        // iOS-specific settings
        else if (EditorUserBuildSettings.activeBuildTarget == BuildTarget.iOS)
        {
            ConfigureiOSBuild();
        }
    }
    
    static void ConfigureAndroidBuild()
    {
        PlayerSettings.Android.bundleVersionCode = 1;
        PlayerSettings.Android.minSdkVersion = AndroidSdkVersions.AndroidApiLevel21;
        PlayerSettings.Android.targetSdkVersion = AndroidSdkVersions.AndroidApiLevelAuto;
        
        // Graphics API
        PlayerSettings.SetGraphicsAPIs(BuildTarget.Android, new GraphicsDeviceType[] { 
            GraphicsDeviceType.OpenGLES3, 
            GraphicsDeviceType.Vulkan 
        });
        
        // Optimization
        PlayerSettings.stripEngineCode = true;
        PlayerSettings.Android.useAPKExpansionFiles = false;
        
        EditorUserBuildSettings.buildAppBundle = true; // AAB format
        
        BuildProject(BuildTarget.Android, "Builds/Android/" + Application.productName + ".aab");
    }
    
    static void ConfigureiOSBuild()
    {
        PlayerSettings.iOS.buildNumber = "1";
        PlayerSettings.iOS.targetOSVersionString = "11.0";
        PlayerSettings.iOS.targetDevice = iOSTargetDevice.iPhoneAndiPad;
        
        // Graphics
        PlayerSettings.SetGraphicsAPIs(BuildTarget.iOS, new GraphicsDeviceType[] { 
            GraphicsDeviceType.Metal 
        });
        
        // Optimization
        PlayerSettings.iOS.scriptCallOptimization = ScriptCallOptimizationLevel.SlowAndSafe;
        PlayerSettings.strippingLevel = StrippingLevel.StripAssemblies;
        
        BuildProject(BuildTarget.iOS, "Builds/iOS/");
    }
    
    static void BuildProject(BuildTarget target, string path)
    {
        BuildPlayerOptions buildOptions = new BuildPlayerOptions
        {
            scenes = EditorBuildSettings.scenes
                .Where(scene => scene.enabled)
                .Select(scene => scene.path)
                .ToArray(),
            locationPathName = path,
            target = target,
            options = BuildOptions.None
        };
        
        BuildPipeline.BuildPlayer(buildOptions);
    }
    #endif
}
```

### WebGL Build Optimization
Web deployment with performance considerations:

```csharp
public class WebGLBuildConfig : MonoBehaviour
{
    #if UNITY_EDITOR
    [MenuItem("Build/Configure WebGL Build")]
    static void ConfigureWebGLBuild()
    {
        // WebGL-specific settings
        PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Gzip;
        PlayerSettings.WebGL.memorySize = 512; // MB
        PlayerSettings.WebGL.exceptionSupport = WebGLExceptionSupport.None;
        PlayerSettings.WebGL.nameFilesAsHashes = true;
        
        // Graphics optimization
        PlayerSettings.colorSpace = ColorSpace.Gamma; // Better performance on web
        PlayerSettings.SetGraphicsAPIs(BuildTarget.WebGL, new GraphicsDeviceType[] { 
            GraphicsDeviceType.OpenGLES3 
        });
        
        // Code stripping for size
        PlayerSettings.stripEngineCode = true;
        PlayerSettings.managedStrippingLevel = ManagedStrippingLevel.High;
        
        // Build
        BuildPlayerOptions buildOptions = new BuildPlayerOptions
        {
            scenes = EditorBuildSettings.scenes
                .Where(scene => scene.enabled)
                .Select(scene => scene.path)
                .ToArray(),
            locationPathName = "Builds/WebGL/",
            target = BuildTarget.WebGL,
            options = BuildOptions.None
        };
        
        BuildPipeline.BuildPlayer(buildOptions);
    }
    #endif
    
    void Start()
    {
        #if UNITY_WEBGL && !UNITY_EDITOR
        // WebGL runtime optimizations
        Application.targetFrameRate = 60;
        QualitySettings.vSyncCount = 1;
        
        // Prevent context loss
        Screen.sleepTimeout = SleepTimeout.NeverSleep;
        #endif
    }
}
```

---

## 🤖 Automated Build Pipeline

### Command Line Building
Create scripts for CI/CD integration:

```csharp
using UnityEditor;
using UnityEngine;
using System.Linq;
using System;

public class CommandLineBuild
{
    static void BuildAll()
    {
        BuildWindows();
        BuildMac();
        BuildLinux();
        BuildAndroid();
        BuildiOS();
        BuildWebGL();
    }
    
    static void BuildWindows()
    {
        BuildTarget target = BuildTarget.StandaloneWindows64;
        string path = "Builds/Windows/" + GetBuildName(target) + ".exe";
        
        GenericBuild(target, path);
    }
    
    static void BuildMac()
    {
        BuildTarget target = BuildTarget.StandaloneOSX;
        string path = "Builds/Mac/" + GetBuildName(target) + ".app";
        
        GenericBuild(target, path);
    }
    
    static void BuildLinux()
    {
        BuildTarget target = BuildTarget.StandaloneLinux64;
        string path = "Builds/Linux/" + GetBuildName(target);
        
        GenericBuild(target, path);
    }
    
    static void BuildAndroid()
    {
        BuildTarget target = BuildTarget.Android;
        string path = "Builds/Android/" + GetBuildName(target) + ".apk";
        
        // Configure Android-specific settings
        EditorUserBuildSettings.buildAppBundle = false; // APK for testing
        
        GenericBuild(target, path);
    }
    
    static void BuildiOS()
    {
        BuildTarget target = BuildTarget.iOS;
        string path = "Builds/iOS/";
        
        GenericBuild(target, path);
    }
    
    static void BuildWebGL()
    {
        BuildTarget target = BuildTarget.WebGL;
        string path = "Builds/WebGL/";
        
        GenericBuild(target, path);
    }
    
    static void GenericBuild(BuildTarget target, string path)
    {
        EditorUserBuildSettings.SwitchActiveBuildTarget(
            BuildPipeline.GetBuildTargetGroup(target), 
            target
        );
        
        // Get command line arguments
        string[] args = Environment.GetCommandLineArgs();
        bool developmentBuild = args.Contains("-development");
        bool allowDebugging = args.Contains("-debug");
        
        BuildOptions options = BuildOptions.None;
        if (developmentBuild) options |= BuildOptions.Development;
        if (allowDebugging) options |= BuildOptions.AllowDebugging;
        
        BuildPlayerOptions buildOptions = new BuildPlayerOptions
        {
            scenes = EditorBuildSettings.scenes
                .Where(scene => scene.enabled)
                .Select(scene => scene.path)
                .ToArray(),
            locationPathName = path,
            target = target,
            options = options
        };
        
        var result = BuildPipeline.BuildPlayer(buildOptions);
        
        if (result.summary.result == UnityEditor.Build.Reporting.BuildResult.Succeeded)
        {
            Debug.Log($"Build succeeded: {path}");
            Environment.Exit(0);
        }
        else
        {
            Debug.LogError($"Build failed: {result.summary.result}");
            Environment.Exit(1);
        }
    }
    
    static string GetBuildName(BuildTarget target)
    {
        string version = Application.version;
        string timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
        return $"{Application.productName}_v{version}_{target}_{timestamp}";
    }
}
```

### GitHub Actions CI/CD
Automate builds with GitHub Actions:

```yaml
# .github/workflows/build.yml
name: Unity Build Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    name: Build for ${{ matrix.targetPlatform }}
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        targetPlatform:
          - StandaloneWindows64
          - StandaloneOSX
          - StandaloneLinux64
          - Android
          - WebGL
    
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: 0
          lfs: true
      
      - uses: actions/cache@v2
        with:
          path: Library
          key: Library-${{ matrix.targetPlatform }}
          restore-keys: Library-
      
      - uses: game-ci/unity-builder@v2
        env:
          UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}
        with:
          targetPlatform: ${{ matrix.targetPlatform }}
          buildMethod: CommandLineBuild.GenericBuild
      
      - uses: actions/upload-artifact@v2
        with:
          name: Build-${{ matrix.targetPlatform }}
          path: build/${{ matrix.targetPlatform }}
```

---

## 📦 Build Optimization and Asset Management

### Asset Bundle System
Optimize loading and updates with asset bundles:

```csharp
using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class AssetBundleManager : MonoBehaviour
{
    private static AssetBundleManager instance;
    public static AssetBundleManager Instance => instance;
    
    private Dictionary<string, AssetBundle> loadedBundles = new Dictionary<string, AssetBundle>();
    
    [Header("Asset Bundle Settings")]
    public string bundleURL = "https://yourserver.com/bundles/";
    public string platformFolder;
    
    void Awake()
    {
        if (instance == null)
        {
            instance = this;
            DontDestroyOnLoad(gameObject);
            
            #if UNITY_ANDROID && !UNITY_EDITOR
            platformFolder = "android/";
            #elif UNITY_IOS && !UNITY_EDITOR
            platformFolder = "ios/";
            #elif UNITY_WEBGL && !UNITY_EDITOR
            platformFolder = "webgl/";
            #else
            platformFolder = "standalone/";
            #endif
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    public IEnumerator LoadAssetBundle(string bundleName)
    {
        if (loadedBundles.ContainsKey(bundleName))
        {
            yield break;
        }
        
        string url = bundleURL + platformFolder + bundleName;
        
        using (UnityWebRequest www = UnityWebRequestAssetBundle.GetAssetBundle(url))
        {
            yield return www.SendWebRequest();
            
            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError($"Failed to load asset bundle: {bundleName}");
                yield break;
            }
            
            AssetBundle bundle = DownloadHandlerAssetBundle.GetContent(www);
            loadedBundles[bundleName] = bundle;
            
            Debug.Log($"Asset bundle loaded: {bundleName}");
        }
    }
    
    public T LoadAsset<T>(string bundleName, string assetName) where T : Object
    {
        if (!loadedBundles.ContainsKey(bundleName))
        {
            Debug.LogError($"Asset bundle not loaded: {bundleName}");
            return null;
        }
        
        return loadedBundles[bundleName].LoadAsset<T>(assetName);
    }
    
    public void UnloadAssetBundle(string bundleName, bool unloadAllLoadedObjects = false)
    {
        if (loadedBundles.ContainsKey(bundleName))
        {
            loadedBundles[bundleName].Unload(unloadAllLoadedObjects);
            loadedBundles.Remove(bundleName);
        }
    }
}

#if UNITY_EDITOR
[UnityEditor.MenuItem("Assets/Build Asset Bundles")]
static void BuildAllAssetBundles()
{
    string assetBundleDirectory = "Assets/AssetBundles";
    if (!System.IO.Directory.Exists(assetBundleDirectory))
    {
        System.IO.Directory.CreateDirectory(assetBundleDirectory);
    }
    
    UnityEditor.BuildPipeline.BuildAssetBundles(
        assetBundleDirectory,
        UnityEditor.BuildAssetBundleOptions.None,
        UnityEditor.EditorUserBuildSettings.activeBuildTarget
    );
}
#endif
```

---

## 🚀 AI/LLM Integration Opportunities

### Build Automation Scripts
Use AI to generate build pipeline automation:

**Example prompts:**
> "Generate a Unity build script that creates platform-specific builds with version numbering"
> "Create a CI/CD pipeline configuration for Unity WebGL deployment to AWS S3"
> "Write a Unity script that validates build settings before deployment"

### Deployment Optimization
- Ask AI for platform-specific optimization strategies
- Generate automated testing scripts for builds
- Create build performance analysis tools

### Asset Pipeline Management
- Use AI to generate asset bundle management systems
- Create automated asset optimization scripts
- Generate build size analysis reports

### Documentation Generation
- Generate deployment guides for different platforms
- Create build troubleshooting documentation
- Generate platform-specific setup instructions

---

## 🎮 Practical Exercises

### Exercise 1: Multi-Platform Build System
Create an automated build system:
1. Configure build settings for Windows, Mac, and Linux
2. Implement command-line building support
3. Add version numbering and timestamping
4. Create build validation scripts

### Exercise 2: Mobile Deployment Pipeline
Set up mobile-specific builds:
1. Configure Android APK and AAB builds
2. Set up iOS Xcode project generation
3. Implement platform-specific optimizations
4. Create automated testing workflows

### Exercise 3: WebGL Optimization Pipeline
Build a web-optimized deployment system:
1. Configure WebGL build settings for performance
2. Implement progressive loading system
3. Create web-specific asset optimization
4. Set up automated deployment to hosting

---

## 🎯 Portfolio Project Ideas

### Beginner: "Cross-Platform Build Manager"
Create a comprehensive build management tool:
- GUI for build configuration
- Multi-platform support
- Version control integration
- Basic deployment automation

### Intermediate: "CI/CD Build Pipeline"
Implement professional deployment workflows:
- Automated testing integration
- Multiple environment deployments
- Asset bundle management
- Performance monitoring

### Advanced: "Enterprise Deployment System"
Build a complete deployment framework:
- Multi-tenant build system
- A/B testing deployment
- Rollback capabilities
- Analytics integration

---

## 📚 Essential Resources

### Official Unity Resources
- Unity Cloud Build documentation
- Platform-specific build guides
- Unity Package Manager documentation

### CI/CD Platforms
- **Unity Cloud Build**: Official Unity service
- **GitHub Actions**: Popular CI/CD platform
- **Jenkins**: Self-hosted automation server

### Deployment Platforms
- **Steam**: PC game distribution
- **Google Play Console**: Android deployment
- **App Store Connect**: iOS deployment
- **Itch.io**: Indie game hosting

---

## 🔍 Interview Preparation

### Common Build/Deployment Questions

1. **"How would you set up a CI/CD pipeline for a Unity project?"**
   - Version control integration
   - Automated testing
   - Multi-platform builds
   - Deployment automation

2. **"Explain the difference between development and release builds"**
   - Development: Debugging enabled, larger file size
   - Release: Optimized, stripped code, smaller size

3. **"How would you optimize build times for a large Unity project?"**
   - Incremental builds
   - Build caching
   - Asset bundle optimization
   - Parallel build processes

### Technical Challenges
Practice implementing:
- Command-line build scripts
- Platform-specific configurations
- Asset bundle systems
- Deployment automation

---

## ⚡ AI Productivity Hacks

### Automation Generation
- Generate build pipeline scripts for specific platforms
- Create deployment automation for various hosting services
- Generate testing frameworks for build validation

### Optimization Analysis
- Use AI to analyze build sizes and suggest optimizations
- Generate performance profiling scripts for builds
- Create automated quality assurance checklists

### Documentation Creation
- Generate deployment guides for different platforms
- Create troubleshooting documentation for common build issues
- Generate setup instructions for development environments

---

## 🎯 Next Steps
1. Master basic build configuration for target platforms
2. Implement automated build pipelines for your projects
3. Learn platform-specific optimization techniques
4. Build a comprehensive deployment system for portfolio demonstration

> **AI Integration Reminder**: Use LLMs to accelerate build pipeline development, generate platform-specific configurations, and create comprehensive deployment automation. Build systems benefit greatly from AI-assisted scripting and optimization analysis!