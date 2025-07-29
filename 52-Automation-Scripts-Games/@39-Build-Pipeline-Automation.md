# @39-Build-Pipeline-Automation

## 🎯 Core Concept
Automated build pipeline system for continuous integration, multi-platform builds, and deployment.

## 🔧 Implementation

### Build Pipeline Manager
```csharp
using UnityEngine;
using UnityEditor;
using UnityEditor.Build.Reporting;
using System.Collections.Generic;
using System.IO;

public class BuildPipelineManager
{
    [Header("Build Settings")]
    public static string buildOutputPath = "Builds/";
    public static bool enableAutoVersioning = true;
    public static bool cleanBeforeBuild = true;
    public static bool generateBuildReport = true;
    
    [MenuItem("Build Tools/Build All Platforms")]
    public static void BuildAllPlatforms()
    {
        if (cleanBeforeBuild)
        {
            CleanBuildDirectory();
        }
        
        List<BuildTarget> platforms = new List<BuildTarget>
        {
            BuildTarget.StandaloneWindows64,
            BuildTarget.StandaloneOSX,
            BuildTarget.StandaloneLinux64,
            BuildTarget.Android,
            BuildTarget.iOS
        };
        
        foreach (BuildTarget platform in platforms)
        {
            BuildForPlatform(platform);
        }
        
        if (generateBuildReport)
        {
            GenerateBuildSummary();
        }
    }
    
    public static void BuildForPlatform(BuildTarget target)
    {
        string platformName = GetPlatformName(target);
        string outputPath = Path.Combine(buildOutputPath, platformName, GetBuildFileName(target));
        
        Debug.Log($"Starting build for {platformName}...");
        
        // Update version if enabled
        if (enableAutoVersioning)
        {
            UpdateVersionNumber();
        }
        
        // Setup build options
        BuildPlayerOptions buildOptions = new BuildPlayerOptions
        {
            scenes = GetBuildScenes(),
            locationPathName = outputPath,
            target = target,
            options = GetBuildOptions(target)
        };
        
        // Perform pre-build steps
        PreBuildSteps(target);
        
        // Execute build
        BuildReport report = BuildPipeline.BuildPlayer(buildOptions);
        
        // Perform post-build steps
        PostBuildSteps(target, report);
        
        // Log results
        if (report.summary.result == BuildResult.Succeeded)
        {
            Debug.Log($"Build succeeded for {platformName}: {outputPath}");
            LogBuildInfo(report);
        }
        else
        {
            Debug.LogError($"Build failed for {platformName}: {report.summary.totalErrors} errors");
        }
    }
    
    static string[] GetBuildScenes()
    {
        List<string> scenes = new List<string>();
        
        foreach (EditorBuildSettingsScene scene in EditorBuildSettings.scenes)
        {
            if (scene.enabled)
            {
                scenes.Add(scene.path);
            }
        }
        
        return scenes.ToArray();
    }
    
    static BuildOptions GetBuildOptions(BuildTarget target)
    {
        BuildOptions options = BuildOptions.None;
        
        // Development build for testing
        if (EditorUserBuildSettings.development)
        {
            options |= BuildOptions.Development;
        }
        
        // Enable script debugging
        if (EditorUserBuildSettings.allowDebugging)
        {
            options |= BuildOptions.AllowDebugging;
        }
        
        // Platform-specific options
        switch (target)
        {
            case BuildTarget.Android:
                // Android-specific build options
                break;
            case BuildTarget.iOS:
                // iOS-specific build options
                break;
        }
        
        return options;
    }
    
    static void PreBuildSteps(BuildTarget target)
    {
        Debug.Log($"Executing pre-build steps for {GetPlatformName(target)}...");
        
        // Clean temporary files
        CleanTempFiles();
        
        // Update build timestamp
        UpdateBuildTimestamp();
        
        // Validate project settings
        ValidateProjectSettings(target);
        
        // Platform-specific pre-build steps
        switch (target)
        {
            case BuildTarget.Android:
                ConfigureAndroidSettings();
                break;
            case BuildTarget.iOS:
                ConfigureIOSSettings();
                break;
        }
    }
    
    static void PostBuildSteps(BuildTarget target, BuildReport report)
    {
        Debug.Log($"Executing post-build steps for {GetPlatformName(target)}...");
        
        // Generate build metadata
        GenerateBuildMetadata(target, report);
        
        // Copy additional files
        CopyAdditionalFiles(target);
        
        // Create installer/package if needed
        CreatePackage(target);
        
        // Upload to distribution platform if configured
        if (ShouldAutoUpload(target))
        {
            UploadBuild(target, report);
        }
    }
    
    static void ConfigureAndroidSettings()
    {
        // Set Android-specific settings
        PlayerSettings.Android.minSdkVersion = AndroidSdkVersions.AndroidApiLevel23;
        PlayerSettings.Android.targetSdkVersion = AndroidSdkVersions.AndroidApiLevelAuto;
        
        // Configure keystore for release builds
        if (!EditorUserBuildSettings.development)
        {
            PlayerSettings.Android.keystoreName = "release.keystore";
            PlayerSettings.Android.keystorePass = System.Environment.GetEnvironmentVariable("ANDROID_KEYSTORE_PASS");
            PlayerSettings.Android.keyaliasName = "release";
            PlayerSettings.Android.keyaliasPass = System.Environment.GetEnvironmentVariable("ANDROID_KEY_PASS");
        }
        
        Debug.Log("Android settings configured");
    }
    
    static void ConfigureIOSSettings()
    {
        // Set iOS-specific settings
        PlayerSettings.iOS.targetOSVersionString = "11.0";
        PlayerSettings.iOS.sdkVersion = iOSSdkVersion.DeviceSDK;
        
        // Configure signing for release builds
        if (!EditorUserBuildSettings.development)
        {
            PlayerSettings.iOS.appleDeveloperTeamID = System.Environment.GetEnvironmentVariable("IOS_TEAM_ID");
        }
        
        Debug.Log("iOS settings configured");
    }
    
    static void UpdateVersionNumber()
    {
        string currentVersion = PlayerSettings.bundleVersion;
        string[] versionParts = currentVersion.Split('.');
        
        if (versionParts.Length >= 3)
        {
            int buildNumber = int.Parse(versionParts[2]) + 1;
            string newVersion = $"{versionParts[0]}.{versionParts[1]}.{buildNumber}";
            
            PlayerSettings.bundleVersion = newVersion;
            PlayerSettings.Android.bundleVersionCode++;
            PlayerSettings.iOS.buildNumber = buildNumber.ToString();
            
            Debug.Log($"Version updated to {newVersion}");
        }
    }
    
    static void UpdateBuildTimestamp()
    {
        // Store build timestamp in PlayerPrefs or ScriptableObject
        string timestamp = System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
        EditorPrefs.SetString("LastBuildTime", timestamp);
        
        // Update build info asset
        BuildInfoAsset buildInfo = Resources.Load<BuildInfoAsset>("BuildInfo");
        if (buildInfo != null)
        {
            buildInfo.buildTime = timestamp;
            buildInfo.buildNumber++;
            EditorUtility.SetDirty(buildInfo);
        }
    }
    
    static void ValidateProjectSettings(BuildTarget target)
    {
        List<string> issues = new List<string>();
        
        // Check company name
        if (string.IsNullOrEmpty(PlayerSettings.companyName))
        {
            issues.Add("Company name not set");
        }
        
        // Check product name
        if (string.IsNullOrEmpty(PlayerSettings.productName))
        {
            issues.Add("Product name not set");
        }
        
        // Check version
        if (string.IsNullOrEmpty(PlayerSettings.bundleVersion))
        {
            issues.Add("Version not set");
        }
        
        // Platform-specific validation
        switch (target)
        {
            case BuildTarget.Android:
                if (string.IsNullOrEmpty(PlayerSettings.applicationIdentifier))
                {
                    issues.Add("Package name not set for Android");
                }
                break;
            case BuildTarget.iOS:
                if (string.IsNullOrEmpty(PlayerSettings.iOS.appleDeveloperTeamID))
                {
                    issues.Add("Apple Developer Team ID not set for iOS");
                }
                break;
        }
        
        if (issues.Count > 0)
        {
            string errorMessage = "Project validation failed:\n" + string.Join("\n", issues);
            throw new System.Exception(errorMessage);
        }
        
        Debug.Log("Project settings validation passed");
    }
    
    static void CleanBuildDirectory()
    {
        if (Directory.Exists(buildOutputPath))
        {
            Directory.Delete(buildOutputPath, true);
        }
        Directory.CreateDirectory(buildOutputPath);
        
        Debug.Log("Build directory cleaned");
    }
    
    static void CleanTempFiles()
    {
        // Clean Unity temp files
        string tempPath = "Temp/";
        if (Directory.Exists(tempPath))
        {
            try
            {
                Directory.Delete(tempPath, true);
                Debug.Log("Temporary files cleaned");
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"Could not clean temp files: {e.Message}");
            }
        }
    }
    
    static void GenerateBuildMetadata(BuildTarget target, BuildReport report)
    {
        string platformName = GetPlatformName(target);
        string metadataPath = Path.Combine(buildOutputPath, platformName, "build_metadata.json");
        
        BuildMetadata metadata = new BuildMetadata
        {
            platform = platformName,
            version = PlayerSettings.bundleVersion,
            buildTime = System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"),
            buildResult = report.summary.result.ToString(),
            totalSize = report.summary.totalSize,
            buildDuration = report.summary.totalTime.TotalSeconds,
            unityVersion = Application.unityVersion
        };
        
        string json = JsonUtility.ToJson(metadata, true);
        File.WriteAllText(metadataPath, json);
        
        Debug.Log($"Build metadata generated: {metadataPath}");
    }
    
    static void CopyAdditionalFiles(BuildTarget target)
    {
        string platformName = GetPlatformName(target);
        string platformBuildPath = Path.Combine(buildOutputPath, platformName);
        
        // Copy README
        if (File.Exists("README.md"))
        {
            File.Copy("README.md", Path.Combine(platformBuildPath, "README.md"), true);
        }
        
        // Copy changelog
        if (File.Exists("CHANGELOG.md"))
        {
            File.Copy("CHANGELOG.md", Path.Combine(platformBuildPath, "CHANGELOG.md"), true);
        }
        
        // Copy platform-specific files
        string platformAssetsPath = Path.Combine("BuildAssets", platformName);
        if (Directory.Exists(platformAssetsPath))
        {
            CopyDirectory(platformAssetsPath, platformBuildPath);
        }
    }
    
    static void CreatePackage(BuildTarget target)
    {
        string platformName = GetPlatformName(target);
        string buildPath = Path.Combine(buildOutputPath, platformName);
        
        switch (target)
        {
            case BuildTarget.StandaloneWindows64:
                CreateWindowsInstaller(buildPath);
                break;
            case BuildTarget.StandaloneOSX:
                CreateMacPackage(buildPath);
                break;
            case BuildTarget.Android:
                // APK already generated
                Debug.Log("Android APK generated");
                break;
        }
    }
    
    static void CreateWindowsInstaller(string buildPath)
    {
        // This would typically use a tool like NSIS or WiX
        Debug.Log("Windows installer creation not implemented");
    }
    
    static void CreateMacPackage(string buildPath)
    {
        // This would typically create a .app bundle and optionally a .dmg
        Debug.Log("Mac package creation not implemented");
    }
    
    static void UploadBuild(BuildTarget target, BuildReport report)
    {
        if (report.summary.result != BuildResult.Succeeded)
        {
            Debug.LogWarning("Skipping upload due to failed build");
            return;
        }
        
        Debug.Log($"Uploading build for {GetPlatformName(target)}...");
        
        // This would integrate with services like:
        // - Steam (Steamworks SDK)
        // - Google Play Console
        // - App Store Connect
        // - Itch.io
        // - Custom distribution servers
        
        Debug.Log("Build upload not implemented");
    }
    
    static bool ShouldAutoUpload(BuildTarget target)
    {
        // Check environment variables or build settings
        return System.Environment.GetEnvironmentVariable("AUTO_UPLOAD") == "true";
    }
    
    static void LogBuildInfo(BuildReport report)
    {
        Debug.Log($"Build completed in {report.summary.totalTime.TotalMinutes:F1} minutes");
        Debug.Log($"Total build size: {report.summary.totalSize / (1024 * 1024):F1} MB");
        Debug.Log($"Total warnings: {report.summary.totalWarnings}");
    }
    
    static void GenerateBuildSummary()
    {
        string summaryPath = Path.Combine(buildOutputPath, "build_summary.html");
        
        string html = @"
        <!DOCTYPE html>
        <html>
        <head>
            <title>Build Summary</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .platform { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
                .success { background-color: #d4edda; }
                .failure { background-color: #f8d7da; }
            </style>
        </head>
        <body>
            <h1>Build Summary</h1>
            <p>Generated: " + System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + @"</p>
            <!-- Build details would be populated here -->
        </body>
        </html>";
        
        File.WriteAllText(summaryPath, html);
        Debug.Log($"Build summary generated: {summaryPath}");
    }
    
    static string GetPlatformName(BuildTarget target)
    {
        switch (target)
        {
            case BuildTarget.StandaloneWindows64: return "Windows";
            case BuildTarget.StandaloneOSX: return "Mac";
            case BuildTarget.StandaloneLinux64: return "Linux";
            case BuildTarget.Android: return "Android";
            case BuildTarget.iOS: return "iOS";
            default: return target.ToString();
        }
    }
    
    static string GetBuildFileName(BuildTarget target)
    {
        string productName = PlayerSettings.productName.Replace(" ", "");
        string version = PlayerSettings.bundleVersion;
        
        switch (target)
        {
            case BuildTarget.StandaloneWindows64:
                return $"{productName}_v{version}.exe";
            case BuildTarget.StandaloneOSX:
                return $"{productName}_v{version}.app";
            case BuildTarget.StandaloneLinux64:
                return $"{productName}_v{version}";
            case BuildTarget.Android:
                return $"{productName}_v{version}.apk";
            case BuildTarget.iOS:
                return $"{productName}_iOS";
            default:
                return $"{productName}_v{version}";
        }
    }
    
    static void CopyDirectory(string sourceDir, string destDir)
    {
        Directory.CreateDirectory(destDir);
        
        foreach (string file in Directory.GetFiles(sourceDir, "*", SearchOption.AllDirectories))
        {
            string relativePath = Path.GetRelativePath(sourceDir, file);
            string destFile = Path.Combine(destDir, relativePath);
            
            Directory.CreateDirectory(Path.GetDirectoryName(destFile));
            File.Copy(file, destFile, true);
        }
    }
}

[System.Serializable]
public class BuildMetadata
{
    public string platform;
    public string version;
    public string buildTime;
    public string buildResult;
    public ulong totalSize;
    public double buildDuration;
    public string unityVersion;
}

[CreateAssetMenu(fileName = "BuildInfo", menuName = "Build/Build Info")]
public class BuildInfoAsset : ScriptableObject
{
    public string buildTime;
    public int buildNumber;
    public string version;
    public string gitCommit;
}
```

## 🚀 AI/LLM Integration
- Generate build configurations based on project requirements
- Automatically optimize build settings for different platforms
- Create intelligent deployment strategies

## 💡 Key Benefits
- Automated multi-platform builds
- Continuous integration support  
- Build validation and reporting