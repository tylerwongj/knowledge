# @c-Unity-Production-Pipeline-Enterprise-Architecture

## 🎯 Learning Objectives

- Design and implement enterprise-grade Unity build pipelines
- Master Unity Cloud Build and custom CI/CD solutions
- Establish automated testing and quality assurance workflows
- Create scalable deployment strategies for multiple platforms

## 🔧 Enterprise Build Pipeline Architecture

### Multi-Platform Build Configuration

```yaml
# unity-pipeline.yml - GitHub Actions Configuration
name: Unity CI/CD Pipeline

on:
  push:
    branches: [ main, develop, release/* ]
  pull_request:
    branches: [ main, develop ]

env:
  UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}
  UNITY_EMAIL: ${{ secrets.UNITY_EMAIL }}
  UNITY_PASSWORD: ${{ secrets.UNITY_PASSWORD }}

jobs:
  # Code Quality Checks
  quality-check:
    name: Code Quality Analysis
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
          lfs: true
      
      - name: Cache Library
        uses: actions/cache@v3
        with:
          path: Library
          key: Library-${{ runner.os }}-${{ hashFiles('Assets/**', 'Packages/**', 'ProjectSettings/**') }}
      
      - name: Setup Unity
        uses: game-ci/unity-builder@v2
        with:
          unity-version: 2022.3.10f1
          target-platform: StandaloneWindows64
      
      - name: Run Code Analysis
        run: |
          # Custom code analysis scripts
          ./Scripts/CodeAnalysis/run-static-analysis.sh
          ./Scripts/CodeAnalysis/check-naming-conventions.sh
          ./Scripts/CodeAnalysis/validate-assets.sh
      
      - name: Upload Analysis Results
        uses: actions/upload-artifact@v3
        with:
          name: code-analysis
          path: Analysis/

  # Automated Testing
  test-suite:
    name: Test Suite
    runs-on: ubuntu-latest
    needs: quality-check
    strategy:
      matrix:
        test-mode: [EditMode, PlayMode]
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
          lfs: true
      
      - name: Cache Library
        uses: actions/cache@v3
        with:
          path: Library
          key: Library-${{ runner.os }}-${{ matrix.test-mode }}-${{ hashFiles('Assets/**', 'Packages/**', 'ProjectSettings/**') }}
      
      - name: Run Tests
        uses: game-ci/unity-test-runner@v2
        env:
          UNITY_LICENSE: ${{ env.UNITY_LICENSE }}
        with:
          unity-version: 2022.3.10f1
          test-mode: ${{ matrix.test-mode }}
          coverage-options: 'generateAdditionalMetrics;generateHtmlReport;generateBadgeReport'
      
      - name: Upload Test Results
        uses: actions/upload-artifact@v3
        with:
          name: test-results-${{ matrix.test-mode }}
          path: artifacts/
      
      - name: Publish Test Results
        uses: dorny/test-reporter@v1
        if: success() || failure()
        with:
          name: Unity Tests (${{ matrix.test-mode }})
          path: artifacts/**/*.xml
          reporter: java-junit

  # Multi-Platform Builds
  build:
    name: Build ${{ matrix.targetPlatform }}
    runs-on: ${{ matrix.os }}
    needs: test-suite
    strategy:
      fail-fast: false
      matrix:
        include:
          - targetPlatform: StandaloneWindows64
            os: windows-latest
          - targetPlatform: StandaloneOSX
            os: macos-latest
          - targetPlatform: StandaloneLinux64
            os: ubuntu-latest
          - targetPlatform: iOS
            os: macos-latest
          - targetPlatform: Android
            os: ubuntu-latest
          - targetPlatform: WebGL
            os: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
          lfs: true
      
      - name: Cache Library
        uses: actions/cache@v3
        with:
          path: Library
          key: Library-${{ runner.os }}-${{ matrix.targetPlatform }}-${{ hashFiles('Assets/**', 'Packages/**', 'ProjectSettings/**') }}
      
      - name: Setup Build Environment
        run: |
          echo "Setting up environment for ${{ matrix.targetPlatform }}"
          ./Scripts/BuildPipeline/setup-environment.sh ${{ matrix.targetPlatform }}
      
      - name: Build Unity Project
        uses: game-ci/unity-builder@v2
        env:
          UNITY_LICENSE: ${{ env.UNITY_LICENSE }}
        with:
          unity-version: 2022.3.10f1
          target-platform: ${{ matrix.targetPlatform }}
          build-name: GameBuild-${{ matrix.targetPlatform }}
          builds-path: Builds
          custom-parameters: -quit -batchmode -executeMethod BuildPipeline.BuildGame
      
      - name: Post-Build Processing
        run: |
          ./Scripts/BuildPipeline/post-build-processing.sh ${{ matrix.targetPlatform }}
      
      - name: Upload Build Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-${{ matrix.targetPlatform }}
          path: Builds/

  # Deployment Pipeline
  deploy:
    name: Deploy to ${{ matrix.environment }}
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    strategy:
      matrix:
        environment: [staging, production]
    environment: ${{ matrix.environment }}
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Download Build Artifacts
        uses: actions/download-artifact@v3
        with:
          path: Builds/
      
      - name: Deploy to Environment
        run: |
          ./Scripts/Deployment/deploy.sh ${{ matrix.environment }}
          
      - name: Health Check
        run: |
          ./Scripts/Deployment/health-check.sh ${{ matrix.environment }}
      
      - name: Notify Deployment
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#game-deployments'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Custom Unity Build Pipeline

```csharp
using UnityEngine;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using System;
using System.IO;
using System.Collections.Generic;

namespace BuildPipeline
{
    /// <summary>
    /// Enterprise build pipeline for Unity projects
    /// </summary>
    public static class BuildManager
    {
        private const string BUILD_CONFIG_PATH = "Assets/BuildConfiguration";
        
        [MenuItem("Build/Build All Platforms")]
        public static void BuildAllPlatforms()
        {
            var config = LoadBuildConfiguration();
            
            foreach (var platformConfig in config.platforms)
            {
                if (platformConfig.enabled)
                {
                    BuildPlatform(platformConfig);
                }
            }
        }
        
        [MenuItem("Build/Build Current Platform")]
        public static void BuildCurrentPlatform()
        {
            var currentTarget = EditorUserBuildSettings.activeBuildTarget;
            var config = LoadBuildConfiguration();
            
            var platformConfig = config.GetPlatformConfig(currentTarget);
            if (platformConfig != null)
            {
                BuildPlatform(platformConfig);
            }
            else
            {
                Debug.LogError($"No configuration found for platform: {currentTarget}");
            }
        }
        
        public static void BuildGame()
        {
            // Method called from CI/CD pipeline
            var platform = GetCommandLineArg("-platform");
            var configuration = GetCommandLineArg("-configuration");
            var outputPath = GetCommandLineArg("-outputPath");
            
            if (string.IsNullOrEmpty(platform))
            {
                platform = EditorUserBuildSettings.activeBuildTarget.ToString();
            }
            
            var config = LoadBuildConfiguration();
            var platformConfig = config.GetPlatformConfig(platform);
            
            if (platformConfig == null)
            {
                throw new BuildFailedException($"Platform configuration not found: {platform}");
            }
            
            // Override configuration if specified
            if (!string.IsNullOrEmpty(configuration))
            {
                platformConfig.buildConfiguration = (BuildConfiguration)Enum.Parse(typeof(BuildConfiguration), configuration);
            }
            
            if (!string.IsNullOrEmpty(outputPath))
            {
                platformConfig.outputPath = outputPath;
            }
            
            BuildPlatform(platformConfig);
        }
        
        private static void BuildPlatform(PlatformBuildConfig config)
        {
            Debug.Log($"Starting build for platform: {config.platform}");
            
            var stopwatch = System.Diagnostics.Stopwatch.StartNew();
            
            try
            {
                // Pre-build setup
                SetupBuildEnvironment(config);
                
                // Configure build options
                var buildOptions = CreateBuildPlayerOptions(config);
                
                // Execute build
                var report = BuildPipeline.BuildPlayer(buildOptions);
                
                stopwatch.Stop();
                
                // Handle build result
                HandleBuildResult(report, config, stopwatch.Elapsed);
            }
            catch (Exception ex)
            {
                stopwatch.Stop();
                HandleBuildError(ex, config, stopwatch.Elapsed);
                throw;
            }
        }
        
        private static void SetupBuildEnvironment(PlatformBuildConfig config)
        {
            // Set build target
            if (EditorUserBuildSettings.activeBuildTarget != config.buildTarget)
            {
                EditorUserBuildSettings.SwitchActiveBuildTarget(
                    BuildPipeline.GetBuildTargetGroup(config.buildTarget),
                    config.buildTarget
                );
            }
            
            // Configure platform-specific settings
            ConfigurePlatformSettings(config);
            
            // Setup scripting defines
            SetupScriptingDefines(config);
            
            // Configure quality settings
            ConfigureQualitySettings(config);
            
            // Run pre-build processors
            RunPreBuildProcessors(config);
        }
        
        private static BuildPlayerOptions CreateBuildPlayerOptions(PlatformBuildConfig config)
        {
            var options = new BuildPlayerOptions
            {
                scenes = GetScenesForBuild(config),
                locationPathName = GetOutputPath(config),
                target = config.buildTarget,
                options = GetBuildOptions(config)
            };
            
            return options;
        }
        
        private static string[] GetScenesForBuild(PlatformBuildConfig config)
        {
            if (config.useCustomScenes && config.customScenes.Length > 0)
            {
                return config.customScenes;
            }
            
            // Use scenes from build settings
            var scenes = new List<string>();
            for (int i = 0; i < EditorBuildSettings.scenes.Length; i++)
            {
                var scene = EditorBuildSettings.scenes[i];
                if (scene.enabled)
                {
                    scenes.Add(scene.path);
                }
            }
            
            return scenes.ToArray();
        }
        
        private static string GetOutputPath(PlatformBuildConfig config)
        {
            var basePath = string.IsNullOrEmpty(config.outputPath) ? "Builds" : config.outputPath;
            var platformPath = Path.Combine(basePath, config.platform);
            var configPath = Path.Combine(platformPath, config.buildConfiguration.ToString());
            
            // Add timestamp for unique builds
            var timestamp = DateTime.Now.ToString("yyyyMMdd-HHmmss");
            var finalPath = Path.Combine(configPath, $"Build-{timestamp}");
            
            // Platform-specific executable naming
            var executableName = GetExecutableName(config);
            return Path.Combine(finalPath, executableName);
        }
        
        private static string GetExecutableName(PlatformBuildConfig config)
        {
            var productName = PlayerSettings.productName;
            
            switch (config.buildTarget)
            {
                case BuildTarget.StandaloneWindows:
                case BuildTarget.StandaloneWindows64:
                    return $"{productName}.exe";
                    
                case BuildTarget.StandaloneOSX:
                    return $"{productName}.app";
                    
                case BuildTarget.StandaloneLinux64:
                    return productName;
                    
                case BuildTarget.Android:
                    return $"{productName}.apk";
                    
                case BuildTarget.iOS:
                    return "iOS-Build";
                    
                case BuildTarget.WebGL:
                    return "WebGL-Build";
                    
                default:
                    return productName;
            }
        }
        
        private static BuildOptions GetBuildOptions(PlatformBuildConfig config)
        {
            var options = BuildOptions.None;
            
            switch (config.buildConfiguration)
            {
                case BuildConfiguration.Development:
                    options |= BuildOptions.Development;
                    options |= BuildOptions.AllowDebugging;
                    options |= BuildOptions.ConnectWithProfiler;
                    break;
                    
                case BuildConfiguration.Debug:
                    options |= BuildOptions.Development;
                    options |= BuildOptions.AllowDebugging;
                    options |= BuildOptions.ConnectWithProfiler;
                    options |= BuildOptions.ShowBuiltPlayer;
                    break;
                    
                case BuildConfiguration.Release:
                    // Release builds use default options
                    break;
            }
            
            if (config.cleanBuild)
            {
                options |= BuildOptions.CleanBuildCache;
            }
            
            if (config.strictMode)
            {
                options |= BuildOptions.StrictMode;
            }
            
            return options;
        }
        
        private static void ConfigurePlatformSettings(PlatformBuildConfig config)
        {
            switch (config.buildTarget)
            {
                case BuildTarget.Android:
                    ConfigureAndroidSettings(config);
                    break;
                    
                case BuildTarget.iOS:
                    ConfigureIOSSettings(config);
                    break;
                    
                case BuildTarget.WebGL:
                    ConfigureWebGLSettings(config);
                    break;
            }
        }
        
        private static void ConfigureAndroidSettings(PlatformBuildConfig config)
        {
            // Configure Android-specific settings
            if (config.androidSettings != null)
            {
                PlayerSettings.Android.bundleVersionCode = config.androidSettings.versionCode;
                PlayerSettings.Android.minSdkVersion = config.androidSettings.minSdkVersion;
                PlayerSettings.Android.targetSdkVersion = config.androidSettings.targetSdkVersion;
                
                if (!string.IsNullOrEmpty(config.androidSettings.keystorePath))
                {
                    PlayerSettings.Android.useCustomKeystore = true;
                    PlayerSettings.Android.keystoreName = config.androidSettings.keystorePath;
                    PlayerSettings.Android.keyaliasName = config.androidSettings.keyAlias;
                }
            }
        }
        
        private static void ConfigureIOSSettings(PlatformBuildConfig config)
        {
            // Configure iOS-specific settings
            if (config.iosSettings != null)
            {
                PlayerSettings.iOS.buildNumber = config.iosSettings.buildNumber;
                PlayerSettings.iOS.targetDevice = config.iosSettings.targetDevice;
                PlayerSettings.iOS.targetOSVersionString = config.iosSettings.targetOSVersion;
                
                if (!string.IsNullOrEmpty(config.iosSettings.teamId))
                {
                    PlayerSettings.iOS.appleDeveloperTeamID = config.iosSettings.teamId;
                }
            }
        }
        
        private static void ConfigureWebGLSettings(PlatformBuildConfig config)
        {
            // Configure WebGL-specific settings
            if (config.webGLSettings != null)
            {
                PlayerSettings.WebGL.compressionFormat = config.webGLSettings.compressionFormat;
                PlayerSettings.WebGL.memorySize = config.webGLSettings.memorySize;
                PlayerSettings.WebGL.dataCaching = config.webGLSettings.dataCaching;
            }
        }
        
        private static void SetupScriptingDefines(PlatformBuildConfig config)
        {
            var targetGroup = BuildPipeline.GetBuildTargetGroup(config.buildTarget);
            var currentDefines = PlayerSettings.GetScriptingDefineSymbolsForGroup(targetGroup);
            var definesList = new List<string>(currentDefines.Split(';'));
            
            // Add configuration-specific defines
            var configDefine = $"BUILD_{config.buildConfiguration.ToString().ToUpper()}";
            if (!definesList.Contains(configDefine))
            {
                definesList.Add(configDefine);
            }
            
            // Add platform-specific defines
            var platformDefine = $"PLATFORM_{config.platform.ToUpper()}";
            if (!definesList.Contains(platformDefine))
            {
                definesList.Add(platformDefine);
            }
            
            // Add custom defines from config
            if (config.customDefines != null)
            {
                foreach (var define in config.customDefines)
                {
                    if (!definesList.Contains(define))
                    {
                        definesList.Add(define);
                    }
                }
            }
            
            var newDefines = string.Join(";", definesList);
            PlayerSettings.SetScriptingDefineSymbolsForGroup(targetGroup, newDefines);
        }
        
        private static void ConfigureQualitySettings(PlatformBuildConfig config)
        {
            if (config.qualitySettings != null)
            {
                var targetGroup = BuildPipeline.GetBuildTargetGroup(config.buildTarget);
                QualitySettings.SetQualityLevel(config.qualitySettings.qualityLevel);
            }
        }
        
        private static void RunPreBuildProcessors(PlatformBuildConfig config)
        {
            // Version increment
            IncrementVersion(config);
            
            // Asset validation
            ValidateAssets(config);
            
            // Custom processors
            if (config.preBuildProcessors != null)
            {
                foreach (var processor in config.preBuildProcessors)
                {
                    processor.Process(config);
                }
            }
        }
        
        private static void IncrementVersion(PlatformBuildConfig config)
        {
            if (config.autoIncrementVersion)
            {
                var version = PlayerSettings.bundleVersion;
                var parts = version.Split('.');
                
                if (parts.Length >= 3)
                {
                    if (int.TryParse(parts[2], out int build))
                    {
                        parts[2] = (build + 1).ToString();
                        PlayerSettings.bundleVersion = string.Join(".", parts);
                        
                        Debug.Log($"Version incremented to: {PlayerSettings.bundleVersion}");
                    }
                }
            }
        }
        
        private static void ValidateAssets(PlatformBuildConfig config)
        {
            if (config.validateAssets)
            {
                // Run asset validation
                var validator = new AssetValidator();
                var validationResult = validator.ValidateProject();
                
                if (!validationResult.IsValid)
                {
                    throw new BuildFailedException($"Asset validation failed: {validationResult.ErrorMessage}");
                }
            }
        }
        
        private static void HandleBuildResult(BuildReport report, PlatformBuildConfig config, TimeSpan buildTime)
        {
            var result = report.summary.result;
            var outputPath = report.summary.outputPath;
            var totalSize = report.summary.totalSize;
            
            Debug.Log($"Build completed in {buildTime.TotalMinutes:F2} minutes");
            Debug.Log($"Build result: {result}");
            Debug.Log($"Output path: {outputPath}");
            Debug.Log($"Build size: {FormatBytes(totalSize)}");
            
            if (result == BuildResult.Succeeded)
            {
                Debug.Log($"✅ Build successful for {config.platform}");
                
                // Run post-build processors
                RunPostBuildProcessors(config, report);
                
                // Generate build report
                GenerateBuildReport(config, report, buildTime);
            }
            else
            {
                throw new BuildFailedException($"Build failed for {config.platform}: {result}");
            }
        }
        
        private static void HandleBuildError(Exception ex, PlatformBuildConfig config, TimeSpan buildTime)
        {
            Debug.LogError($"❌ Build failed for {config.platform} after {buildTime.TotalMinutes:F2} minutes");
            Debug.LogError($"Error: {ex.Message}");
            
            // Generate error report
            GenerateErrorReport(config, ex, buildTime);
        }
        
        private static void RunPostBuildProcessors(PlatformBuildConfig config, BuildReport report)
        {
            if (config.postBuildProcessors != null)
            {
                foreach (var processor in config.postBuildProcessors)
                {
                    processor.Process(config, report);
                }
            }
        }
        
        private static void GenerateBuildReport(PlatformBuildConfig config, BuildReport report, TimeSpan buildTime)
        {
            var reportData = new BuildReportData
            {
                Platform = config.platform,
                Configuration = config.buildConfiguration.ToString(),
                BuildTime = buildTime,
                OutputPath = report.summary.outputPath,
                TotalSize = report.summary.totalSize,
                Result = report.summary.result.ToString(),
                Timestamp = DateTime.UtcNow
            };
            
            var reportPath = Path.Combine("BuildReports", $"BuildReport-{config.platform}-{DateTime.Now:yyyyMMdd-HHmmss}.json");
            Directory.CreateDirectory(Path.GetDirectoryName(reportPath));
            
            var json = JsonUtility.ToJson(reportData, true);
            File.WriteAllText(reportPath, json);
            
            Debug.Log($"Build report generated: {reportPath}");
        }
        
        private static void GenerateErrorReport(PlatformBuildConfig config, Exception ex, TimeSpan buildTime)
        {
            var errorData = new BuildErrorReport
            {
                Platform = config.platform,
                Configuration = config.buildConfiguration.ToString(),
                BuildTime = buildTime,
                ErrorMessage = ex.Message,
                StackTrace = ex.StackTrace,
                Timestamp = DateTime.UtcNow
            };
            
            var reportPath = Path.Combine("BuildReports", $"ErrorReport-{config.platform}-{DateTime.Now:yyyyMMdd-HHmmss}.json");
            Directory.CreateDirectory(Path.GetDirectoryName(reportPath));
            
            var json = JsonUtility.ToJson(errorData, true);
            File.WriteAllText(reportPath, json);
            
            Debug.LogError($"Error report generated: {reportPath}");
        }
        
        private static BuildConfiguration LoadBuildConfiguration()
        {
            var configPath = Path.Combine(BUILD_CONFIG_PATH, "BuildConfiguration.asset");
            var config = AssetDatabase.LoadAssetAtPath<BuildConfiguration>(configPath);
            
            if (config == null)
            {
                throw new FileNotFoundException($"Build configuration not found at: {configPath}");
            }
            
            return config;
        }
        
        private static string GetCommandLineArg(string name)
        {
            var args = Environment.GetCommandLineArgs();
            for (int i = 0; i < args.Length; i++)
            {
                if (args[i] == name && i + 1 < args.Length)
                {
                    return args[i + 1];
                }
            }
            return string.Empty;
        }
        
        private static string FormatBytes(ulong bytes)
        {
            string[] sizes = { "B", "KB", "MB", "GB", "TB" };
            double len = bytes;
            int order = 0;
            while (len >= 1024 && order < sizes.Length - 1)
            {
                order++;
                len = len / 1024;
            }
            return $"{len:0.##} {sizes[order]}";
        }
    }
    
    // Supporting data structures
    [System.Serializable]
    public class BuildReportData
    {
        public string Platform;
        public string Configuration;
        public TimeSpan BuildTime;
        public string OutputPath;
        public ulong TotalSize;
        public string Result;
        public DateTime Timestamp;
    }
    
    [System.Serializable]
    public class BuildErrorReport
    {
        public string Platform;
        public string Configuration;
        public TimeSpan BuildTime;
        public string ErrorMessage;
        public string StackTrace;
        public DateTime Timestamp;
    }
    
    public class BuildFailedException : Exception
    {
        public BuildFailedException(string message) : base(message) { }
        public BuildFailedException(string message, Exception innerException) : base(message, innerException) { }
    }
}

// Build configuration ScriptableObject
[CreateAssetMenu(fileName = "BuildConfiguration", menuName = "Build Pipeline/Build Configuration")]
public class BuildConfiguration : ScriptableObject
{
    [Header("General Settings")]
    public string projectName = "GameProject";
    public string version = "1.0.0";
    public bool autoIncrementVersion = true;
    
    [Header("Platform Configurations")]
    public PlatformBuildConfig[] platforms = new PlatformBuildConfig[0];
    
    public PlatformBuildConfig GetPlatformConfig(BuildTarget target)
    {
        return Array.Find(platforms, config => config.buildTarget == target);
    }
    
    public PlatformBuildConfig GetPlatformConfig(string platformName)
    {
        return Array.Find(platforms, config => config.platform.Equals(platformName, StringComparison.OrdinalIgnoreCase));
    }
}

[System.Serializable]
public class PlatformBuildConfig
{
    [Header("Platform Settings")]
    public string platform = "Windows";
    public BuildTarget buildTarget = BuildTarget.StandaloneWindows64;
    public bool enabled = true;
    
    [Header("Build Settings")]
    public BuildConfiguration buildConfiguration = BuildConfiguration.Release;
    public string outputPath = "";
    public bool cleanBuild = false;
    public bool strictMode = true;
    public bool validateAssets = true;
    
    [Header("Scenes")]
    public bool useCustomScenes = false;
    public string[] customScenes = new string[0];
    
    [Header("Scripting")]
    public string[] customDefines = new string[0];
    
    [Header("Quality")]
    public QualitySettingsConfig qualitySettings;
    
    [Header("Platform Specific")]
    public AndroidBuildSettings androidSettings;
    public IOSBuildSettings iosSettings;
    public WebGLBuildSettings webGLSettings;
    
    [Header("Processors")]
    public IPreBuildProcessor[] preBuildProcessors;
    public IPostBuildProcessor[] postBuildProcessors;
}

public enum BuildConfiguration
{
    Debug,
    Development,
    Release
}

[System.Serializable]
public class QualitySettingsConfig
{
    public int qualityLevel = 3; // High quality by default
}

[System.Serializable]
public class AndroidBuildSettings
{
    public int versionCode = 1;
    public AndroidSdkVersions minSdkVersion = AndroidSdkVersions.AndroidApiLevel21;
    public AndroidSdkVersions targetSdkVersion = AndroidSdkVersions.AndroidApiLevel30;
    public string keystorePath = "";
    public string keyAlias = "";
}

[System.Serializable]
public class IOSBuildSettings
{
    public string buildNumber = "1";
    public iOSTargetDevice targetDevice = iOSTargetDevice.iPhoneAndiPad;
    public string targetOSVersion = "11.0";
    public string teamId = "";
}

[System.Serializable]
public class WebGLBuildSettings
{
    public WebGLCompressionFormat compressionFormat = WebGLCompressionFormat.Gzip;
    public int memorySize = 256;
    public bool dataCaching = true;
}

// Processor interfaces
public interface IPreBuildProcessor
{
    void Process(PlatformBuildConfig config);
}

public interface IPostBuildProcessor
{
    void Process(PlatformBuildConfig config, BuildReport report);
}

// Asset validator
public class AssetValidator
{
    public ValidationResult ValidateProject()
    {
        var result = new ValidationResult { IsValid = true };
        
        // Check for missing references
        CheckMissingReferences(result);
        
        // Validate texture settings
        ValidateTextureSettings(result);
        
        // Check audio settings
        ValidateAudioSettings(result);
        
        // Validate prefabs
        ValidatePrefabs(result);
        
        return result;
    }
    
    private void CheckMissingReferences(ValidationResult result)
    {
        // Implementation for checking missing references
    }
    
    private void ValidateTextureSettings(ValidationResult result)
    {
        // Implementation for validating texture compression settings
    }
    
    private void ValidateAudioSettings(ValidationResult result)
    {
        // Implementation for validating audio compression settings
    }
    
    private void ValidatePrefabs(ValidationResult result)
    {
        // Implementation for validating prefab configurations
    }
}

public class ValidationResult
{
    public bool IsValid { get; set; }
    public string ErrorMessage { get; set; }
    public List<string> Warnings { get; set; } = new List<string>();
}
```

## 🚀 AI/LLM Integration for CI/CD

### Build Pipeline Optimization Prompts

```
Analyze and optimize this Unity CI/CD pipeline configuration:

Pipeline: [Insert pipeline YAML/configuration]
Project Type: [Mobile/Desktop/WebGL/Multi-platform]
Team Size: [Number of developers]
Build Frequency: [Daily/Per-commit/Release cycles]

Provide optimization recommendations for:
1. Build time reduction strategies
2. Parallel execution opportunities
3. Caching and artifact management
4. Resource utilization optimization
5. Cost reduction for cloud builds
6. Security and compliance improvements
7. Monitoring and alerting setup

Focus on enterprise-scale best practices and Unity-specific optimizations.
```

### Automated Pipeline Generation

```
Generate a comprehensive Unity CI/CD pipeline for:

Project Requirements:
- Platform targets: [iOS, Android, Windows, WebGL]
- Team structure: [Remote team, multiple time zones]
- Quality requirements: [High, with automated testing]
- Deployment strategy: [Staging + Production environments]
- Security requirements: [Enterprise compliance]

Include:
1. Multi-stage pipeline configuration (YAML)
2. Automated testing integration
3. Security scanning and compliance checks
4. Deployment automation with rollback
5. Monitoring and notification setup
6. Documentation and runbook creation

Output production-ready pipeline configurations.
```

## 💡 Advanced Enterprise Patterns

### Microservices Build Architecture

```bash
#!/bin/bash
# enterprise-build-orchestrator.sh

set -e

# Configuration
PROJECT_ROOT=$(pwd)
BUILD_CONFIG_FILE="BuildConfiguration/enterprise-config.json"
ARTIFACTS_DIR="BuildArtifacts"
REPORTS_DIR="BuildReports"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Environment validation
validate_environment() {
    log_info "Validating build environment..."
    
    # Check Unity installation
    if ! command -v unity &> /dev/null; then
        log_error "Unity command line tools not found"
        exit 1
    fi
    
    # Check required tools
    local required_tools=("git" "jq" "curl")
    for tool in "${required_tools[@]}"; do
        if ! command -v $tool &> /dev/null; then
            log_error "$tool is required but not installed"
            exit 1
        fi
    done
    
    # Validate Unity license
    if [ -z "$UNITY_LICENSE" ] && [ -z "$UNITY_USERNAME" ]; then
        log_error "Unity license or credentials not configured"
        exit 1
    fi
    
    log_info "Environment validation completed"
}

# Load build configuration
load_build_config() {
    if [ ! -f "$BUILD_CONFIG_FILE" ]; then
        log_error "Build configuration file not found: $BUILD_CONFIG_FILE"
        exit 1
    fi
    
    log_info "Loading build configuration from $BUILD_CONFIG_FILE"
    BUILD_CONFIG=$(cat "$BUILD_CONFIG_FILE")
}

# Pre-build validation
pre_build_validation() {
    log_info "Running pre-build validation..."
    
    # Git repository validation
    if [ ! -d ".git" ]; then
        log_error "Not a Git repository"
        exit 1
    fi
    
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        log_warn "Uncommitted changes detected"
    fi
    
    # Unity project validation
    if [ ! -f "ProjectSettings/ProjectVersion.txt" ]; then
        log_error "Not a Unity project"
        exit 1
    fi
    
    # Asset validation
    unity -batchmode -quit -projectPath "$PROJECT_ROOT" \
          -executeMethod BuildPipeline.AssetValidator.ValidateAssets \
          -logFile "$REPORTS_DIR/asset-validation.log"
    
    if [ $? -ne 0 ]; then
        log_error "Asset validation failed"
        exit 1
    fi
    
    log_info "Pre-build validation completed"
}

# Run automated tests
run_tests() {
    log_info "Running automated test suite..."
    
    local test_modes=("EditMode" "PlayMode")
    
    for mode in "${test_modes[@]}"; do
        log_info "Running $mode tests..."
        
        unity -batchmode -quit -projectPath "$PROJECT_ROOT" \
              -runTests -testPlatform $mode \
              -testResults "$REPORTS_DIR/test-results-$mode.xml" \
              -logFile "$REPORTS_DIR/test-$mode.log"
        
        if [ $? -ne 0 ]; then
            log_error "$mode tests failed"
            exit 1
        fi
    done
    
    # Generate test coverage report
    unity -batchmode -quit -projectPath "$PROJECT_ROOT" \
          -executeMethod BuildPipeline.TestCoverage.GenerateReport \
          -coverageResultsPath "$REPORTS_DIR/coverage.xml" \
          -logFile "$REPORTS_DIR/coverage.log"
    
    log_info "Test suite completed successfully"
}

# Build specific platform
build_platform() {
    local platform=$1
    local config=$2
    
    log_info "Building platform: $platform ($config)"
    
    local build_path="$ARTIFACTS_DIR/$platform/$config"
    mkdir -p "$build_path"
    
    # Platform-specific build command
    unity -batchmode -quit -projectPath "$PROJECT_ROOT" \
          -executeMethod BuildPipeline.BuildManager.BuildGame \
          -platform "$platform" \
          -configuration "$config" \
          -outputPath "$build_path" \
          -logFile "$REPORTS_DIR/build-$platform-$config.log"
    
    if [ $? -eq 0 ]; then
        log_info "✅ Build successful: $platform ($config)"
        
        # Generate build metadata
        generate_build_metadata "$platform" "$config" "$build_path"
        
        # Package build artifacts
        package_build_artifacts "$platform" "$config" "$build_path"
    else
        log_error "❌ Build failed: $platform ($config)"
        exit 1
    fi
}

# Generate build metadata
generate_build_metadata() {
    local platform=$1
    local config=$2
    local build_path=$3
    
    local metadata_file="$build_path/build-metadata.json"
    
    cat > "$metadata_file" << EOF
{
    "platform": "$platform",
    "configuration": "$config",
    "buildTime": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "gitCommit": "$(git rev-parse HEAD)",
    "gitBranch": "$(git rev-parse --abbrev-ref HEAD)",
    "unityVersion": "$(unity -version | head -n1)",
    "buildNumber": "$BUILD_NUMBER",
    "version": "$(cat ProjectSettings/ProjectVersion.txt | grep m_EditorVersion | cut -d' ' -f2)"
}
EOF
    
    log_info "Build metadata generated: $metadata_file"
}

# Package build artifacts
package_build_artifacts() {
    local platform=$1
    local config=$2
    local build_path=$3
    
    local archive_name="build-$platform-$config-$(date +%Y%m%d-%H%M%S).tar.gz"
    local archive_path="$ARTIFACTS_DIR/$archive_name"
    
    tar -czf "$archive_path" -C "$build_path" .
    
    log_info "Build artifacts packaged: $archive_path"
    
    # Upload to artifact repository
    if [ -n "$ARTIFACT_REPOSITORY_URL" ]; then
        upload_artifact "$archive_path"
    fi
}

# Upload artifact to repository
upload_artifact() {
    local artifact_path=$1
    
    log_info "Uploading artifact to repository..."
    
    curl -H "Authorization: Bearer $ARTIFACT_REPOSITORY_TOKEN" \
         -F "file=@$artifact_path" \
         "$ARTIFACT_REPOSITORY_URL/upload"
    
    if [ $? -eq 0 ]; then
        log_info "✅ Artifact uploaded successfully"
    else
        log_error "❌ Artifact upload failed"
    fi
}

# Generate comprehensive build report
generate_build_report() {
    log_info "Generating comprehensive build report..."
    
    local report_file="$REPORTS_DIR/build-report-$(date +%Y%m%d-%H%M%S).html"
    
    # Create HTML report (simplified version)
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Unity Build Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 10px; border-radius: 5px; }
        .section { margin: 20px 0; }
        .success { color: green; }
        .error { color: red; }
        .warning { color: orange; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Unity Build Report</h1>
        <p>Generated: $(date)</p>
        <p>Commit: $(git rev-parse HEAD)</p>
        <p>Branch: $(git rev-parse --abbrev-ref HEAD)</p>
    </div>
    
    <div class="section">
        <h2>Build Summary</h2>
        <!-- Build summary content would be dynamically generated -->
    </div>
    
    <div class="section">
        <h2>Test Results</h2>
        <!-- Test results would be embedded here -->
    </div>
    
    <div class="section">
        <h2>Build Artifacts</h2>
        <!-- Artifact information would be listed here -->
    </div>
</body>
</html>
EOF
    
    log_info "Build report generated: $report_file"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up temporary files..."
    
    # Remove temporary build files
    find "$PROJECT_ROOT" -name "*.tmp" -delete
    find "$PROJECT_ROOT" -name "Temp" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Compress old logs
    find "$REPORTS_DIR" -name "*.log" -mtime +7 -exec gzip {} \;
    
    log_info "Cleanup completed"
}

# Main execution
main() {
    log_info "Starting Unity Enterprise Build Pipeline..."
    
    # Create necessary directories
    mkdir -p "$ARTIFACTS_DIR" "$REPORTS_DIR"
    
    # Load configuration
    load_build_config
    
    # Execute build pipeline
    validate_environment
    pre_build_validation
    run_tests
    
    # Build all configured platforms
    echo "$BUILD_CONFIG" | jq -r '.platforms[] | select(.enabled == true) | "\(.name) \(.configuration)"' | while read -r platform config; do
        build_platform "$platform" "$config"
    done
    
    # Generate reports
    generate_build_report
    
    # Cleanup
    cleanup
    
    log_info "🎉 Unity Enterprise Build Pipeline completed successfully!"
}

# Error handling
trap 'log_error "Build pipeline failed at line $LINENO"' ERR

# Execute main function
main "$@"
```

This enterprise-grade Unity production pipeline provides comprehensive build automation, testing integration, and deployment capabilities suitable for large-scale game development teams.