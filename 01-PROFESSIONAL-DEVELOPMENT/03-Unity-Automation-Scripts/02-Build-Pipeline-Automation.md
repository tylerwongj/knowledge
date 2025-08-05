# 02-Build-Pipeline-Automation.md

## 🎯 Learning Objectives
- Master Unity build pipeline automation for multiple platforms
- Implement continuous integration workflows with automated testing
- Create custom build processors and post-build automation
- Develop AI-enhanced build optimization and deployment strategies

## 🔧 Unity Build Pipeline Implementation

### Comprehensive Build Manager
```csharp
// Scripts/Editor/BuildManager.cs
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.Build.Reporting;

public class BuildManager : EditorWindow
{
    [Header("Build Configuration")]
    [SerializeField] private string buildVersion = "1.0.0";
    [SerializeField] private string buildOutputPath = "Builds";
    [SerializeField] private bool developmentBuild = false;
    [SerializeField] private bool autoConnectProfiler = false;
    [SerializeField] private bool deepProfiling = false;
    [SerializeField] private bool scriptDebugging = false;
    
    // Platform Build Settings
    [Serializable]
    public class PlatformBuildSettings
    {
        public BuildTarget buildTarget;
        public string platformName;
        public bool enabled = true;
        public string customOutputPath = "";
        public BuildOptions buildOptions = BuildOptions.None;
        public Dictionary<string, string> customDefines = new Dictionary<string, string>();
        public ScriptingImplementation scriptingBackend = ScriptingImplementation.Mono2x;
        public ApiCompatibilityLevel apiCompatibilityLevel = ApiCompatibilityLevel.NET_Standard_2_0;
        public bool il2CppOptimizations = true;
        public string bundleIdentifier = "";
        public int bundleVersionCode = 1;
        
        public PlatformBuildSettings(BuildTarget target, string name)
        {
            buildTarget = target;
            platformName = name;
        }
    }
    
    private List<PlatformBuildSettings> platformSettings = new List<PlatformBuildSettings>();
    private List<string> buildLog = new List<string>();
    private Dictionary<BuildTarget, BuildSummary> buildResults = new Dictionary<BuildTarget, BuildSummary>();
    
    // Build Statistics
    private DateTime buildStartTime;
    private TimeSpan totalBuildTime;
    private int successfulBuilds = 0;
    private int failedBuilds = 0;
    
    // UI State
    private Vector2 scrollPosition;
    private int selectedTab = 0;
    private string[] tabNames = { "Platform Settings", "Build Queue", "CI/CD Integration", "Build Results", "Logs" };
    
    // Advanced Build Features
    [Serializable]
    public class BuildPreset
    {
        public string presetName;
        public List<BuildTarget> targets;
        public bool runTests;
        public bool createPackage;
        public bool uploadToCloud;
        public string cloudProvider;
        public Dictionary<string, object> customSettings;
        
        public BuildPreset()
        {
            targets = new List<BuildTarget>();
            customSettings = new Dictionary<string, object>();
        }
    }
    
    private List<BuildPreset> buildPresets = new List<BuildPreset>();
    private int selectedPreset = 0;
    
    [MenuItem("Tools/Build Manager")]
    public static void ShowWindow()
    {
        var window = GetWindow<BuildManager>("Build Manager");
        window.minSize = new Vector2(900, 700);
        window.Show();
    }
    
    private void OnEnable()
    {
        InitializePlatformSettings();
        LoadBuildPresets();
        LoadConfiguration();
    }
    
    private void OnGUI()
    {
        EditorGUILayout.BeginVertical();
        
        // Header
        DrawHeader();
        
        // Tab Selection
        selectedTab = GUILayout.Toolbar(selectedTab, tabNames);
        EditorGUILayout.Space();
        
        scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);
        
        switch (selectedTab)
        {
            case 0:
                DrawPlatformSettingsTab();
                break;
            case 1:
                DrawBuildQueueTab();
                break;
            case 2:
                DrawCIIntegrationTab();
                break;
            case 3:
                DrawBuildResultsTab();
                break;
            case 4:
                DrawLogsTab();
                break;
        }
        
        EditorGUILayout.EndScrollView();
        EditorGUILayout.EndVertical();
    }
    
    private void DrawHeader()
    {
        EditorGUILayout.Space();
        EditorGUILayout.LabelField("Unity Build Pipeline Manager", EditorStyles.boldLabel);
        
        EditorGUILayout.BeginHorizontal();
        EditorGUILayout.LabelField($"Version: {buildVersion} | Successful: {successfulBuilds} | Failed: {failedBuilds}", EditorStyles.miniLabel);
        GUILayout.FlexibleSpace();
        
        if (totalBuildTime.TotalSeconds > 0)
        {
            EditorGUILayout.LabelField($"Last Build Time: {totalBuildTime:hh\\:mm\\:ss}", EditorStyles.miniLabel);
        }
        EditorGUILayout.EndHorizontal();
        
        EditorGUILayout.Space();
    }
    
    private void DrawPlatformSettingsTab()
    {
        EditorGUILayout.LabelField("Platform Build Settings", EditorStyles.boldLabel);
        EditorGUILayout.Space();
        
        // Global Settings
        EditorGUILayout.BeginVertical("box");
        EditorGUILayout.LabelField("Global Build Settings", EditorStyles.boldLabel);
        
        buildVersion = EditorGUILayout.TextField("Build Version", buildVersion);
        buildOutputPath = EditorGUILayout.TextField("Output Path", buildOutputPath);
        
        EditorGUILayout.BeginHorizontal();
        if (GUILayout.Button("Browse"))
        {
            string path = EditorUtility.OpenFolderPanel("Select Build Output Folder", buildOutputPath, "");
            if (!string.IsNullOrEmpty(path))
            {
                buildOutputPath = path;
            }
        }
        EditorGUILayout.EndHorizontal();
        
        developmentBuild = EditorGUILayout.Toggle("Development Build", developmentBuild);
        autoConnectProfiler = EditorGUILayout.Toggle("Auto Connect Profiler", autoConnectProfiler);
        deepProfiling = EditorGUILayout.Toggle("Deep Profiling", deepProfiling);
        scriptDebugging = EditorGUILayout.Toggle("Script Debugging", scriptDebugging);
        
        EditorGUILayout.EndVertical();
        EditorGUILayout.Space();
        
        // Platform-Specific Settings
        EditorGUILayout.LabelField("Platform Configurations", EditorStyles.boldLabel);
        
        foreach (var platform in platformSettings)
        {
            EditorGUILayout.BeginVertical("box");
            
            EditorGUILayout.BeginHorizontal();
            platform.enabled = EditorGUILayout.Toggle(platform.enabled, GUILayout.Width(20));
            EditorGUILayout.LabelField(platform.platformName, EditorStyles.boldLabel);
            GUILayout.FlexibleSpace();
            
            if (GUILayout.Button("Configure", GUILayout.Width(80)))
            {
                ShowPlatformConfiguration(platform);
            }
            EditorGUILayout.EndHorizontal();
            
            if (platform.enabled)
            {
                EditorGUI.indentLevel++;
                
                platform.customOutputPath = EditorGUILayout.TextField("Custom Output Path", platform.customOutputPath);
                platform.scriptingBackend = (ScriptingImplementation)EditorGUILayout.EnumPopup("Scripting Backend", platform.scriptingBackend);
                platform.apiCompatibilityLevel = (ApiCompatibilityLevel)EditorGUILayout.EnumPopup("API Compatibility", platform.apiCompatibilityLevel);
                
                if (platform.scriptingBackend == ScriptingImplementation.IL2CPP)
                {
                    platform.il2CppOptimizations = EditorGUILayout.Toggle("IL2CPP Optimizations", platform.il2CppOptimizations);
                }
                
                if (IsMobilePlatform(platform.buildTarget))
                {
                    platform.bundleIdentifier = EditorGUILayout.TextField("Bundle Identifier", platform.bundleIdentifier);
                    platform.bundleVersionCode = EditorGUILayout.IntField("Bundle Version Code", platform.bundleVersionCode);
                }
                
                EditorGUI.indentLevel--;
            }
            
            EditorGUILayout.EndVertical();
            EditorGUILayout.Space();
        }
        
        // Action Buttons
        EditorGUILayout.BeginHorizontal();
        
        GUI.backgroundColor = Color.green;
        if (GUILayout.Button("Build Selected Platforms", GUILayout.Height(30)))
        {
            BuildSelectedPlatforms();
        }
        GUI.backgroundColor = Color.white;
        
        if (GUILayout.Button("Build All Platforms", GUILayout.Height(30)))
        {
            BuildAllPlatforms();
        }
        
        GUI.backgroundColor = Color.yellow;
        if (GUILayout.Button("Clean Build Folders", GUILayout.Height(30)))
        {
            CleanBuildFolders();
        }
        GUI.backgroundColor = Color.white;
        
        EditorGUILayout.EndHorizontal();
    }
    
    private void DrawBuildQueueTab()
    {
        EditorGUILayout.LabelField("Build Queue Management", EditorStyles.boldLabel);
        EditorGUILayout.Space();
        
        // Build Presets
        EditorGUILayout.LabelField("Build Presets", EditorStyles.boldLabel);
        EditorGUILayout.BeginVertical("box");
        
        if (buildPresets.Count > 0)
        {
            string[] presetNames = buildPresets.Select(p => p.presetName).ToArray();
            selectedPreset = EditorGUILayout.Popup("Select Preset", selectedPreset, presetNames);
            
            if (selectedPreset < buildPresets.Count)
            {
                var preset = buildPresets[selectedPreset];
                EditorGUILayout.LabelField($"Targets: {string.Join(", ", preset.targets)}");
                EditorGUILayout.LabelField($"Run Tests: {preset.runTests}");
                EditorGUILayout.LabelField($"Create Package: {preset.createPackage}");
                EditorGUILayout.LabelField($"Upload to Cloud: {preset.uploadToCloud}");
            }
        }
        else
        {
            EditorGUILayout.LabelField("No build presets configured", EditorStyles.centeredGreyMiniLabel);
        }
        
        EditorGUILayout.BeginHorizontal();
        if (GUILayout.Button("Create New Preset"))
        {
            CreateNewBuildPreset();
        }
        if (GUILayout.Button("Edit Preset") && buildPresets.Count > 0)
        {
            EditBuildPreset(buildPresets[selectedPreset]);
        }
        if (GUILayout.Button("Delete Preset") && buildPresets.Count > 0)
        {
            DeleteBuildPreset(selectedPreset);
        }
        EditorGUILayout.EndHorizontal();
        
        EditorGUILayout.EndVertical();
        EditorGUILayout.Space();
        
        // Scheduled Builds
        EditorGUILayout.LabelField("Scheduled Builds", EditorStyles.boldLabel);
        EditorGUILayout.BeginVertical("box");
        
        EditorGUILayout.Toggle("Enable Nightly Builds", false);
        EditorGUILayout.TextField("Build Schedule (Cron)", "0 2 * * *");
        EditorGUILayout.Toggle("Build on Git Push", false);
        EditorGUILayout.TextField("Webhook URL", "");
        
        EditorGUILayout.EndVertical();
        EditorGUILayout.Space();
        
        // Queue Actions
        EditorGUILayout.BeginHorizontal();
        if (GUILayout.Button("Execute Preset") && buildPresets.Count > 0)
        {
            ExecuteBuildPreset(buildPresets[selectedPreset]);
        }
        if (GUILayout.Button("Queue All Presets"))
        {
            QueueAllPresets();
        }
        if (GUILayout.Button("Clear Queue"))
        {
            ClearBuildQueue();
        }
        EditorGUILayout.EndHorizontal();
    }
    
    private void DrawCIIntegrationTab()
    {
        EditorGUILayout.LabelField("CI/CD Integration", EditorStyles.boldLabel);
        EditorGUILayout.Space();
        
        // GitHub Actions
        EditorGUILayout.LabelField("GitHub Actions", EditorStyles.boldLabel);
        EditorGUILayout.BeginVertical("box");
        
        if (GUILayout.Button("Generate GitHub Actions Workflow"))
        {
            GenerateGitHubActionsWorkflow();
        }
        
        EditorGUILayout.TextField("Repository URL", "https://github.com/username/repository");
        EditorGUILayout.Toggle("Enable Auto Build on PR", true);
        EditorGUILayout.Toggle("Run Tests Before Build", true);
        EditorGUILayout.Toggle("Upload Artifacts", true);
        
        EditorGUILayout.EndVertical();
        EditorGUILayout.Space();
        
        // Unity Cloud Build
        EditorGUILayout.LabelField("Unity Cloud Build", EditorStyles.boldLabel);
        EditorGUILayout.BeginVertical("box");
        
        EditorGUILayout.TextField("Organization ID", "");
        EditorGUILayout.TextField("Project ID", "");
        EditorGUILayout.PasswordField("API Key", "");
        
        EditorGUILayout.BeginHorizontal();
        if (GUILayout.Button("Test Connection"))
        {
            TestCloudBuildConnection();
        }
        if (GUILayout.Button("Sync Settings"))
        {
            SyncCloudBuildSettings();
        }
        EditorGUILayout.EndHorizontal();
        
        EditorGUILayout.EndVertical();
        EditorGUILayout.Space();
        
        // Custom CI/CD
        EditorGUILayout.LabelField("Custom CI/CD", EditorStyles.boldLabel);
        EditorGUILayout.BeginVertical("box");
        
        EditorGUILayout.Popup("CI Provider", 0, new string[] { "Jenkins", "GitLab CI", "TeamCity", "Bamboo", "Custom" });
        EditorGUILayout.TextField("Build Server URL", "");
        EditorGUILayout.TextField("API Token", "");
        
        if (GUILayout.Button("Generate Build Script"))
        {
            GenerateBuildScript();
        }
        
        EditorGUILayout.EndVertical();
        EditorGUILayout.Space();
        
        // Deployment Settings
        EditorGUILayout.LabelField("Deployment Configuration", EditorStyles.boldLabel);
        EditorGUILayout.BeginVertical("box");
        
        EditorGUILayout.Toggle("Auto Deploy to Steam", false);
        EditorGUILayout.Toggle("Auto Deploy to Google Play", false);
        EditorGUILayout.Toggle("Auto Deploy to App Store", false);
        EditorGUILayout.Toggle("Auto Deploy to Itch.io", false);
        
        EditorGUILayout.TextField("Steam App ID", "");
        EditorGUILayout.TextField("Google Play Package", "");
        EditorGUILayout.TextField("App Store Bundle ID", "");
        
        EditorGUILayout.EndVertical();
    }
    
    private void DrawBuildResultsTab()
    {
        EditorGUILayout.LabelField("Build Results & Analytics", EditorStyles.boldLabel);
        EditorGUILayout.Space();
        
        // Build Statistics
        EditorGUILayout.BeginVertical("box");
        EditorGUILayout.LabelField("Build Statistics", EditorStyles.boldLabel);
        
        EditorGUILayout.LabelField($"Total Builds: {successfulBuilds + failedBuilds}");
        EditorGUILayout.LabelField($"Success Rate: {GetSuccessRate():F1}%");
        EditorGUILayout.LabelField($"Average Build Time: {GetAverageBuildTime()}");
        EditorGUILayout.LabelField($"Last Build: {(buildResults.Count > 0 ? buildResults.Values.Last().endedAt.ToString() : "Never")}");
        
        EditorGUILayout.EndVertical();
        EditorGUILayout.Space();
        
        // Platform Results
        if (buildResults.Count > 0)
        {
            EditorGUILayout.LabelField("Recent Build Results", EditorStyles.boldLabel);
            
            foreach (var result in buildResults)
            {
                EditorGUILayout.BeginVertical("box");
                
                EditorGUILayout.BeginHorizontal();
                EditorGUILayout.LabelField(result.Key.ToString(), EditorStyles.boldLabel);
                GUILayout.FlexibleSpace();
                
                Color originalColor = GUI.color;
                GUI.color = result.Value.result == BuildResult.Succeeded ? Color.green : Color.red;
                EditorGUILayout.LabelField(result.Value.result.ToString(), EditorStyles.boldLabel, GUILayout.Width(80));
                GUI.color = originalColor;
                
                EditorGUILayout.EndHorizontal();
                
                EditorGUILayout.LabelField($"Build Time: {result.Value.buildEndedAt - result.Value.buildStartedAt:hh\\:mm\\:ss}");
                EditorGUILayout.LabelField($"Output Size: {EditorUtility.FormatBytes(result.Value.totalSize)}");
                EditorGUILayout.LabelField($"Warnings: {result.Value.totalWarnings}");
                EditorGUILayout.LabelField($"Errors: {result.Value.totalErrors}");
                
                if (result.Value.result == BuildResult.Failed)
                {
                    EditorGUILayout.LabelField("Build Failed", EditorStyles.centeredGreyMiniLabel);
                }
                
                EditorGUILayout.EndVertical();
                EditorGUILayout.Space();
            }
        }
        else
        {
            EditorGUILayout.LabelField("No build results available", EditorStyles.centeredGreyMiniLabel);
        }
        
        // Actions
        EditorGUILayout.BeginHorizontal();
        if (GUILayout.Button("Export Build Report"))
        {
            ExportBuildReport();
        }
        if (GUILayout.Button("Clear Results"))
        {
            ClearBuildResults();
        }
        if (GUILayout.Button("Open Build Folder"))
        {
            OpenBuildFolder();
        }
        EditorGUILayout.EndHorizontal();
    }
    
    private void DrawLogsTab()
    {
        EditorGUILayout.LabelField("Build Logs", EditorStyles.boldLabel);
        EditorGUILayout.Space();
        
        // Log Controls
        EditorGUILayout.BeginHorizontal();
        if (GUILayout.Button("Clear Logs"))
        {
            buildLog.Clear();
        }
        if (GUILayout.Button("Export Logs"))
        {
            ExportBuildLogs();
        }
        if (GUILayout.Button("Refresh"))
        {
            // Refresh display
        }
        EditorGUILayout.EndHorizontal();
        
        EditorGUILayout.Space();
        
        // Log Display
        if (buildLog.Count > 0)
        {
            foreach (string logEntry in buildLog.TakeLast(100))
            {
                EditorGUILayout.SelectableLabel(logEntry, EditorStyles.miniLabel);
            }
        }
        else
        {
            EditorGUILayout.LabelField("No build logs available", EditorStyles.centeredGreyMiniLabel);
        }
    }
    
    // Core Build Methods
    private void BuildSelectedPlatforms()
    {
        var selectedPlatforms = platformSettings.Where(p => p.enabled).ToList();
        
        if (selectedPlatforms.Count == 0)
        {
            EditorUtility.DisplayDialog("No Platforms Selected", "Please select at least one platform to build.", "OK");
            return;
        }
        
        StartBuildProcess(selectedPlatforms);
    }
    
    private void BuildAllPlatforms()
    {
        StartBuildProcess(platformSettings);
    }
    
    private void StartBuildProcess(List<PlatformBuildSettings> platforms)
    {
        buildStartTime = DateTime.Now;
        AddLog("Starting build process...");
        
        try
        {
            // Pre-build setup
            PreBuildSetup();
            
            // Build each platform
            foreach (var platform in platforms.Where(p => p.enabled))
            {
                BuildPlatform(platform);
            }
            
            // Post-build cleanup
            PostBuildCleanup();
            
            totalBuildTime = DateTime.Now - buildStartTime;
            AddLog($"Build process completed in {totalBuildTime:hh\\:mm\\:ss}");
            
            // Show completion dialog
            EditorUtility.DisplayDialog("Build Complete", 
                $"Build process completed.\\nSuccessful: {successfulBuilds}\\nFailed: {failedBuilds}\\nTotal Time: {totalBuildTime:hh\\:mm\\:ss}", "OK");
        }
        catch (Exception e)
        {
            AddLog($"CRITICAL ERROR: {e.Message}");
            EditorUtility.DisplayDialog("Build Error", $"An error occurred during the build process: {e.Message}", "OK");
        }
    }
    
    private void BuildPlatform(PlatformBuildSettings platformSettings)
    {
        AddLog($"Building {platformSettings.platformName}...");
        
        try
        {
            // Switch to target platform
            if (EditorUserBuildSettings.activeBuildTarget != platformSettings.buildTarget)
            {
                AddLog($"Switching to {platformSettings.buildTarget}...");
                EditorUserBuildSettings.SwitchActiveBuildTarget(
                    BuildPipeline.GetBuildTargetGroup(platformSettings.buildTarget),
                    platformSettings.buildTarget);
            }
            
            // Configure platform-specific settings
            ConfigurePlatformSettings(platformSettings);
            
            // Prepare build parameters
            var buildPlayerOptions = new BuildPlayerOptions
            {
                scenes = GetScenesToBuild(),
                locationPathName = GetBuildPath(platformSettings),
                target = platformSettings.buildTarget,
                targetGroup = BuildPipeline.GetBuildTargetGroup(platformSettings.buildTarget),
                options = GetBuildOptions(platformSettings)
            };
            
            // Execute build
            AddLog($"Executing build for {platformSettings.platformName}...");
            var report = BuildPipeline.BuildPlayer(buildPlayerOptions);
            
            // Process build result
            ProcessBuildResult(platformSettings, report);
        }
        catch (Exception e)
        {
            AddLog($"ERROR building {platformSettings.platformName}: {e.Message}");
            failedBuilds++;
        }
    }
    
    private void ConfigurePlatformSettings(PlatformBuildSettings platformSettings)
    {
        // Configure scripting backend
        PlayerSettings.SetScriptingBackend(
            BuildPipeline.GetBuildTargetGroup(platformSettings.buildTarget),
            platformSettings.scriptingBackend);
        
        // Configure API compatibility level
        PlayerSettings.SetApiCompatibilityLevel(
            BuildPipeline.GetBuildTargetGroup(platformSettings.buildTarget),
            platformSettings.apiCompatibilityLevel);
        
        // Platform-specific configurations
        switch (platformSettings.buildTarget)
        {
            case BuildTarget.Android:
                ConfigureAndroidSettings(platformSettings);
                break;
            case BuildTarget.iOS:
                ConfigureiOSSettings(platformSettings);
                break;
            case BuildTarget.WebGL:
                ConfigureWebGLSettings(platformSettings);
                break;
            case BuildTarget.StandaloneWindows64:
            case BuildTarget.StandaloneOSX:
            case BuildTarget.StandaloneLinux64:
                ConfigureDesktopSettings(platformSettings);
                break;
        }
    }
    
    private void ConfigureAndroidSettings(PlatformBuildSettings platformSettings)
    {
        if (!string.IsNullOrEmpty(platformSettings.bundleIdentifier))
        {
            PlayerSettings.SetApplicationIdentifier(BuildTargetGroup.Android, platformSettings.bundleIdentifier);
        }
        
        PlayerSettings.Android.bundleVersionCode = platformSettings.bundleVersionCode;
        
        // IL2CPP optimizations for Android
        if (platformSettings.scriptingBackend == ScriptingImplementation.IL2CPP && platformSettings.il2CppOptimizations)
        {
            PlayerSettings.SetIl2CppCompilerConfiguration(BuildTargetGroup.Android, Il2CppCompilerConfiguration.Release);
        }
    }
    
    private void ConfigureiOSSettings(PlatformBuildSettings platformSettings)
    {
        if (!string.IsNullOrEmpty(platformSettings.bundleIdentifier))
        {
            PlayerSettings.SetApplicationIdentifier(BuildTargetGroup.iOS, platformSettings.bundleIdentifier);
        }
        
        PlayerSettings.iOS.buildNumber = platformSettings.bundleVersionCode.ToString();
        
        // IL2CPP is required for iOS
        PlayerSettings.SetScriptingBackend(BuildTargetGroup.iOS, ScriptingImplementation.IL2CPP);
    }
    
    private void ConfigureWebGLSettings(PlatformBuildSettings platformSettings)
    {
        // WebGL-specific optimizations
        PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Gzip;
        PlayerSettings.WebGL.memorySize = 256; // MB
    }
    
    private void ConfigureDesktopSettings(PlatformBuildSettings platformSettings)
    {
        // Desktop-specific settings
        PlayerSettings.fullScreenMode = FullScreenMode.Windowed;
        PlayerSettings.defaultIsNativeResolution = true;
    }
    
    private string[] GetScenesToBuild()
    {
        return EditorBuildSettings.scenes
            .Where(scene => scene.enabled)
            .Select(scene => scene.path)
            .ToArray();
    }
    
    private string GetBuildPath(PlatformBuildSettings platformSettings)
    {
        string basePath = string.IsNullOrEmpty(platformSettings.customOutputPath) 
            ? buildOutputPath 
            : platformSettings.customOutputPath;
        
        string platformPath = Path.Combine(basePath, platformSettings.platformName);
        string versionPath = Path.Combine(platformPath, buildVersion);
        
        // Ensure directory exists
        Directory.CreateDirectory(versionPath);
        
        // Add executable name for standalone platforms
        string fileName = GetExecutableFileName(platformSettings.buildTarget);
        return Path.Combine(versionPath, fileName);
    }
    
    private string GetExecutableFileName(BuildTarget buildTarget)
    {
        string productName = PlayerSettings.productName.Replace(" ", "");
        
        switch (buildTarget)
        {
            case BuildTarget.StandaloneWindows64:
                return $"{productName}.exe";
            case BuildTarget.StandaloneOSX:
                return $"{productName}.app";
            case BuildTarget.StandaloneLinux64:
                return productName;
            case BuildTarget.Android:
                return $"{productName}.apk";
            case BuildTarget.WebGL:
                return ""; // WebGL builds to folder
            default:
                return productName;
        }
    }
    
    private BuildOptions GetBuildOptions(PlatformBuildSettings platformSettings)
    {
        BuildOptions options = platformSettings.buildOptions;
        
        if (developmentBuild)
        {
            options |= BuildOptions.Development;
        }
        
        if (autoConnectProfiler)
        {
            options |= BuildOptions.ConnectWithProfiler;
        }
        
        if (deepProfiling)
        {
            options |= BuildOptions.EnableDeepProfilingSupport;
        }
        
        if (scriptDebugging)
        {
            options |= BuildOptions.AllowDebugging;
        }
        
        return options;
    }
    
    private void ProcessBuildResult(PlatformBuildSettings platformSettings, BuildReport report)
    {
        buildResults[platformSettings.buildTarget] = report.summary;
        
        if (report.summary.result == BuildResult.Succeeded)
        {
            successfulBuilds++;
            AddLog($"✓ {platformSettings.platformName} built successfully");
            AddLog($"  Output: {report.summary.outputPath}");
            AddLog($"  Size: {EditorUtility.FormatBytes(report.summary.totalSize)}");
            AddLog($"  Time: {report.summary.buildEndedAt - report.summary.buildStartedAt:hh\\:mm\\:ss}");
        }
        else
        {
            failedBuilds++;
            AddLog($"✗ {platformSettings.platformName} build failed");
            AddLog($"  Errors: {report.summary.totalErrors}");
            AddLog($"  Warnings: {report.summary.totalWarnings}");
        }
    }
    
    // Utility Methods
    private void InitializePlatformSettings()
    {
        if (platformSettings.Count == 0)
        {
            platformSettings.Add(new PlatformBuildSettings(BuildTarget.StandaloneWindows64, "Windows"));
            platformSettings.Add(new PlatformBuildSettings(BuildTarget.StandaloneOSX, "macOS"));
            platformSettings.Add(new PlatformBuildSettings(BuildTarget.StandaloneLinux64, "Linux"));
            platformSettings.Add(new PlatformBuildSettings(BuildTarget.Android, "Android"));
            platformSettings.Add(new PlatformBuildSettings(BuildTarget.iOS, "iOS"));
            platformSettings.Add(new PlatformBuildSettings(BuildTarget.WebGL, "WebGL"));
        }
    }
    
    private bool IsMobilePlatform(BuildTarget buildTarget)
    {
        return buildTarget == BuildTarget.Android || buildTarget == BuildTarget.iOS;
    }
    
    private void AddLog(string message)
    {
        string timestamp = DateTime.Now.ToString("HH:mm:ss");
        buildLog.Add($"[{timestamp}] {message}");
        Debug.Log($"[BuildManager] {message}");
    }
    
    private float GetSuccessRate()
    {
        int total = successfulBuilds + failedBuilds;
        return total > 0 ? (float)successfulBuilds / total * 100f : 0f;
    }
    
    private string GetAverageBuildTime()
    {
        if (buildResults.Count == 0) return "N/A";
        
        var totalSeconds = buildResults.Values
            .Select(r => (r.buildEndedAt - r.buildStartedAt).TotalSeconds)
            .Average();
        
        return TimeSpan.FromSeconds(totalSeconds).ToString(@"hh\:mm\:ss");
    }
    
    // Build Process Methods
    private void PreBuildSetup()
    {
        AddLog("Performing pre-build setup...");
        
        // Clear console
        var logEntries = System.Type.GetType("UnityEditor.LogEntries, UnityEditor.dll");
        var clearMethod = logEntries.GetMethod("Clear", System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.Public);
        clearMethod?.Invoke(null, null);
        
        // Save current scene
        if (UnityEngine.SceneManagement.SceneManager.GetActiveScene().isDirty)
        {
            UnityEditor.SceneManagement.EditorSceneManager.SaveOpenScenes();
        }
        
        // Refresh asset database
        AssetDatabase.Refresh();
        
        AddLog("Pre-build setup completed");
    }
    
    private void PostBuildCleanup()
    {
        AddLog("Performing post-build cleanup...");
        
        // Clean temporary files
        CleanTemporaryFiles();
        
        // Generate build reports
        GenerateBuildReports();
        
        // Save configuration
        SaveConfiguration();
        
        AddLog("Post-build cleanup completed");
    }
    
    private void CleanTemporaryFiles()
    {
        // Clean Unity temp files
        string tempPath = Path.Combine(Application.dataPath, "..", "Temp");
        if (Directory.Exists(tempPath))
        {
            try
            {
                Directory.Delete(tempPath, true);
                AddLog("Temporary files cleaned");
            }
            catch (Exception e)
            {
                AddLog($"Warning: Could not clean temp files: {e.Message}");
            }
        }
    }
    
    // Additional Methods (implementations would continue...)
    private void ShowPlatformConfiguration(PlatformBuildSettings platform) { }
    private void CreateNewBuildPreset() { }
    private void EditBuildPreset(BuildPreset preset) { }
    private void DeleteBuildPreset(int index) { }
    private void ExecuteBuildPreset(BuildPreset preset) { }
    private void QueueAllPresets() { }
    private void ClearBuildQueue() { }
    private void GenerateGitHubActionsWorkflow() { }
    private void TestCloudBuildConnection() { }
    private void SyncCloudBuildSettings() { }
    private void GenerateBuildScript() { }
    private void ExportBuildReport() { }
    private void ClearBuildResults() { }
    private void OpenBuildFolder() { }
    private void ExportBuildLogs() { }
    private void CleanBuildFolders() { }
    private void GenerateBuildReports() { }
    private void LoadBuildPresets() { }
    private void LoadConfiguration() { }
    private void SaveConfiguration() { }
}
```

## 🚀 AI/LLM Integration Opportunities

### Build Optimization Analysis
```
PROMPT TEMPLATE - Unity Build Optimization:

"Analyze this Unity project's build configuration and suggest optimizations:

Project Details:
- Target Platforms: [PC/Mobile/Console/WebGL/etc.]
- Project Size: [Asset count, total size]
- Performance Requirements: [60fps/30fps/Battery life/etc.]
- Team Size: [Solo/Small/Large team]

Current Build Issues:
[LIST YOUR BUILD CHALLENGES]

Build Configuration:
```
[PASTE YOUR BUILD SETTINGS/CONFIGURATION]
```

Analyze and provide:
1. Platform-specific optimization recommendations
2. Asset bundling and compression strategies  
3. Build time reduction techniques
4. Memory usage optimizations
5. Loading time improvements
6. Platform store requirements compliance
7. CI/CD pipeline enhancements
8. Automated testing integration"
```

### CI/CD Pipeline Generation
```
PROMPT TEMPLATE - Unity CI/CD Pipeline:

"Generate a complete CI/CD pipeline for Unity development:

Repository Information:
- Git Provider: [GitHub/GitLab/Bitbucket/etc.]
- Team Structure: [Solo/Small team/Enterprise]
- Release Frequency: [Daily/Weekly/Monthly/etc.]
- Deployment Targets: [Steam/Mobile stores/Web/etc.]

Requirements:
- Automated Testing: [Unit/Integration/Performance tests]
- Multi-Platform Builds: [List target platforms]
- Asset Validation: [Quality checks/Optimization]
- Deployment: [Staging/Production environments]

Generate:
1. Complete CI/CD workflow files (YAML/JSON)
2. Build script configurations
3. Automated testing setups
4. Asset processing pipelines
5. Deployment automation scripts
6. Environment-specific configurations
7. Monitoring and notification systems
8. Rollback and recovery procedures"
```

## 💡 Key Build Pipeline Principles

### Essential Build Automation Checklist
- **Multi-platform support** - Consistent builds across all target platforms
- **Automated testing** - Unit tests, integration tests, and performance validation
- **Asset optimization** - Automated texture, audio, and model processing
- **Version management** - Automatic versioning and build numbering
- **CI/CD integration** - Seamless integration with version control systems
- **Error handling** - Robust error detection and recovery mechanisms
- **Build artifacts** - Proper organization and archival of build outputs
- **Deployment automation** - Streamlined deployment to various platforms

### Common Unity Build Challenges
1. **Platform switching time** - Optimization strategies for faster platform changes
2. **Asset processing delays** - Parallel processing and incremental builds
3. **Build size optimization** - Asset compression and unused asset removal
4. **Platform-specific issues** - Handling platform differences and requirements
5. **CI/CD complexity** - Managing complex build workflows and dependencies
6. **Build reproducibility** - Ensuring consistent builds across environments
7. **Resource management** - Handling build server resources and scaling
8. **Quality assurance** - Automated validation and testing integration

This comprehensive build pipeline system enables Unity developers to create professional, automated build processes that support multiple platforms, integrate with modern CI/CD workflows, and significantly reduce manual overhead while improving build quality and consistency.