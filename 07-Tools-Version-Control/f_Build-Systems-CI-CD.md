# f_Build-Systems-CI-CD

## 🎯 Learning Objectives
- Master Unity Cloud Build and local build automation systems
- Implement comprehensive CI/CD pipelines for Unity projects
- Configure automated testing, deployment, and release management
- Optimize build performance and reliability for team development

## 🔧 Unity Cloud Build Configuration

### Project Setup and Configuration
```csharp
// Build configuration script for Unity Cloud Build
#if UNITY_EDITOR
using UnityEngine;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using System.IO;

public class CloudBuildProcessor : IPreprocessBuildWithReport, IPostprocessBuildWithReport
{
    public int callbackOrder => 0;
    
    public void OnPreprocessBuild(BuildReport report)
    {
        Debug.Log($"Starting build for {report.summary.platform}");
        
        // Set build-specific configurations
        ConfigureBuildSettings(report.summary.platform);
        
        // Update version number from environment variables
        UpdateVersionFromEnvironment();
        
        // Configure addressable settings for build
        ConfigureAddressables();
    }
    
    public void OnPostprocessBuild(BuildReport report)
    {
        Debug.Log($"Build completed: {report.summary.result}");
        
        if (report.summary.result == BuildResult.Succeeded)
        {
            // Generate build artifacts
            GenerateBuildArtifacts(report);
            
            // Upload build logs if needed
            UploadBuildLogs(report);
        }
    }
    
    private void ConfigureBuildSettings(BuildTarget platform)
    {
        // Platform-specific build configurations
        switch (platform)
        {
            case BuildTarget.StandaloneWindows64:
                PlayerSettings.SetScriptingBackend(BuildTargetGroup.Standalone, ScriptingImplementation.IL2CPP);
                PlayerSettings.SetApiCompatibilityLevel(BuildTargetGroup.Standalone, ApiCompatibilityLevel.NET_Standard_2_0);
                break;
                
            case BuildTarget.Android:
                PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
                PlayerSettings.SetScriptingBackend(BuildTargetGroup.Android, ScriptingImplementation.IL2CPP);
                PlayerSettings.Android.minSdkVersion = AndroidSdkVersions.AndroidApiLevel24;
                break;
                
            case BuildTarget.iOS:
                PlayerSettings.SetScriptingBackend(BuildTargetGroup.iOS, ScriptingImplementation.IL2CPP);
                PlayerSettings.iOS.targetOSVersionString = "12.0";
                break;
                
            case BuildTarget.WebGL:
                PlayerSettings.SetScriptingBackend(BuildTargetGroup.WebGL, ScriptingImplementation.IL2CPP);
                PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Gzip;
                PlayerSettings.WebGL.linkerTarget = WebGLLinkerTarget.Wasm;
                break;
        }
    }
    
    private void UpdateVersionFromEnvironment()
    {
        string buildNumber = System.Environment.GetEnvironmentVariable("BUILD_NUMBER");
        string gitCommit = System.Environment.GetEnvironmentVariable("GIT_COMMIT");
        
        if (!string.IsNullOrEmpty(buildNumber))
        {
            string currentVersion = PlayerSettings.bundleVersion;
            PlayerSettings.bundleVersion = $"{currentVersion}.{buildNumber}";
        }
        
        if (!string.IsNullOrEmpty(gitCommit))
        {
            // Store commit hash in a scriptable object or build info file
            CreateBuildInfoAsset(gitCommit, buildNumber);
        }
    }
    
    private void CreateBuildInfoAsset(string gitCommit, string buildNumber)
    {
        var buildInfo = ScriptableObject.CreateInstance<BuildInfo>();
        buildInfo.gitCommit = gitCommit;
        buildInfo.buildNumber = buildNumber;
        buildInfo.buildDate = System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
        
        AssetDatabase.CreateAsset(buildInfo, "Assets/Resources/BuildInfo.asset");
        AssetDatabase.SaveAssets();
    }
    
    private void ConfigureAddressables()
    {
        #if ADDRESSABLE_ASSETS
        var settings = UnityEditor.AddressableAssets.AddressableAssetSettingsDefaultObject.Settings;
        if (settings != null)
        {
            // Configure remote content delivery
            var profile = settings.profileSettings.GetProfile(settings.activeProfileId);
            if (profile != null)
            {
                string cdnUrl = System.Environment.GetEnvironmentVariable("CDN_URL");
                if (!string.IsNullOrEmpty(cdnUrl))
                {
                    settings.profileSettings.SetValue(settings.activeProfileId, "RemoteLoadPath", cdnUrl);
                }
            }
        }
        #endif
    }
    
    private void GenerateBuildArtifacts(BuildReport report)
    {
        // Create build manifest
        var manifest = new BuildManifest
        {
            platform = report.summary.platform.ToString(),
            result = report.summary.result.ToString(),
            buildTime = report.summary.buildEndedAt - report.summary.buildStartedAt,
            outputPath = report.summary.outputPath,
            totalSize = report.summary.totalSize,
            totalTime = report.summary.totalTime
        };
        
        string manifestJson = JsonUtility.ToJson(manifest, true);
        string manifestPath = Path.Combine(Path.GetDirectoryName(report.summary.outputPath), "build-manifest.json");
        File.WriteAllText(manifestPath, manifestJson);
    }
    
    private void UploadBuildLogs(BuildReport report)
    {
        // Implementation for uploading build logs to external service
        // This could be S3, Azure Blob Storage, or any other service
        string logContent = GenerateDetailedBuildLog(report);
        
        // Upload logic here
        Debug.Log("Build logs uploaded successfully");
    }
    
    private string GenerateDetailedBuildLog(BuildReport report)
    {
        var logBuilder = new System.Text.StringBuilder();
        logBuilder.AppendLine($"Build Report for {report.summary.platform}");
        logBuilder.AppendLine($"Result: {report.summary.result}");
        logBuilder.AppendLine($"Total Time: {report.summary.totalTime}");
        logBuilder.AppendLine($"Total Size: {report.summary.totalSize} bytes");
        logBuilder.AppendLine($"Output Path: {report.summary.outputPath}");
        
        // Add detailed step information
        foreach (var step in report.steps)
        {
            logBuilder.AppendLine($"Step: {step.name} - Duration: {step.duration}");
            foreach (var message in step.messages)
            {
                logBuilder.AppendLine($"  {message.type}: {message.content}");
            }
        }
        
        return logBuilder.ToString();
    }
}

[System.Serializable]
public class BuildManifest
{
    public string platform;
    public string result;
    public System.TimeSpan buildTime;
    public string outputPath;
    public ulong totalSize;
    public System.TimeSpan totalTime;
}

[CreateAssetMenu(fileName = "BuildInfo", menuName = "Build/Build Info")]
public class BuildInfo : ScriptableObject
{
    public string gitCommit;
    public string buildNumber;
    public string buildDate;
    public string platform;
}
#endif
```

### Advanced Build Scripting
```csharp
#if UNITY_EDITOR
using UnityEngine;
using UnityEditor;
using UnityEditor.Build.Reporting;
using System.Collections.Generic;
using System.IO;
using System.Linq;

public static class AdvancedBuildScript
{
    private static readonly Dictionary<BuildTarget, string> PlatformExtensions = new Dictionary<BuildTarget, string>
    {
        { BuildTarget.StandaloneWindows64, ".exe" },
        { BuildTarget.StandaloneOSX, ".app" },
        { BuildTarget.StandaloneLinux64, "" },
        { BuildTarget.Android, ".apk" },
        { BuildTarget.iOS, "" },
        { BuildTarget.WebGL, "" }
    };
    
    [MenuItem("Build/Build All Platforms")]
    public static void BuildAllPlatforms()
    {
        var platforms = new BuildTarget[]
        {
            BuildTarget.StandaloneWindows64,
            BuildTarget.StandaloneOSX,
            BuildTarget.Android,
            BuildTarget.WebGL
        };
        
        foreach (var platform in platforms)
        {
            BuildForPlatform(platform);
        }
    }
    
    [MenuItem("Build/Build Current Platform")]
    public static void BuildCurrentPlatform()
    {
        BuildForPlatform(EditorUserBuildSettings.activeBuildTarget);
    }
    
    public static void BuildForPlatform(BuildTarget platform)
    {
        // Get scenes to build
        string[] scenes = GetScenesForBuild();
        if (scenes.Length == 0)
        {
            Debug.LogError("No scenes found for build");
            return;
        }
        
        // Configure build options
        BuildPlayerOptions buildOptions = new BuildPlayerOptions
        {
            scenes = scenes,
            locationPathName = GetBuildPath(platform),
            target = platform,
            targetGroup = BuildPipeline.GetBuildTargetGroup(platform),
            options = GetBuildOptions(platform)
        };
        
        // Perform build
        Debug.Log($"Starting build for {platform}...");
        BuildReport report = BuildPipeline.BuildPlayer(buildOptions);
        
        // Process build result
        ProcessBuildResult(report, platform);
    }
    
    private static string[] GetScenesForBuild()
    {
        return EditorBuildSettings.scenes
            .Where(scene => scene.enabled)
            .Select(scene => scene.path)
            .ToArray();
    }
    
    private static string GetBuildPath(BuildTarget platform)
    {
        string projectName = PlayerSettings.productName;
        string basePath = Path.Combine("Builds", platform.ToString());
        
        // Ensure directory exists
        if (!Directory.Exists(basePath))
        {
            Directory.CreateDirectory(basePath);
        }
        
        string extension = PlatformExtensions.ContainsKey(platform) ? PlatformExtensions[platform] : "";
        return Path.Combine(basePath, projectName + extension);
    }
    
    private static BuildOptions GetBuildOptions(BuildTarget platform)
    {
        BuildOptions options = BuildOptions.None;
        
        // Add debug symbols in development builds
        if (EditorUserBuildSettings.development)
        {
            options |= BuildOptions.Development;
            options |= BuildOptions.AllowDebugging;
        }
        
        // Platform-specific options
        switch (platform)
        {
            case BuildTarget.WebGL:
                // WebGL specific options
                break;
            case BuildTarget.Android:
                // Android specific options
                break;
            case BuildTarget.iOS:
                // iOS specific options
                break;
        }
        
        return options;
    }
    
    private static void ProcessBuildResult(BuildReport report, BuildTarget platform)
    {
        switch (report.summary.result)
        {
            case BuildResult.Succeeded:
                Debug.Log($"Build for {platform} succeeded!");
                PostProcessSuccessfulBuild(report, platform);
                break;
                
            case BuildResult.Failed:
                Debug.LogError($"Build for {platform} failed!");
                LogBuildErrors(report);
                break;
                
            case BuildResult.Cancelled:
                Debug.LogWarning($"Build for {platform} was cancelled.");
                break;
        }
    }
    
    private static void PostProcessSuccessfulBuild(BuildReport report, BuildTarget platform)
    {
        // Copy additional files
        CopyAdditionalFiles(report.summary.outputPath, platform);
        
        // Generate checksums
        GenerateChecksums(report.summary.outputPath);
        
        // Create archive if needed
        if (ShouldCreateArchive(platform))
        {
            CreateBuildArchive(report.summary.outputPath, platform);
        }
        
        // Upload to distribution service
        if (ShouldAutoUpload(platform))
        {
            UploadBuild(report.summary.outputPath, platform);
        }
    }
    
    private static void CopyAdditionalFiles(string buildPath, BuildTarget platform)
    {
        string[] additionalFiles = { "README.txt", "CHANGELOG.md", "LICENSE" };
        string buildDirectory = Path.GetDirectoryName(buildPath);
        
        foreach (string file in additionalFiles)
        {
            string sourcePath = Path.Combine(Application.dataPath, "..", file);
            if (File.Exists(sourcePath))
            {
                string destPath = Path.Combine(buildDirectory, file);
                File.Copy(sourcePath, destPath, true);
            }
        }
    }
    
    private static void GenerateChecksums(string buildPath)
    {
        // Generate MD5 and SHA256 checksums for the build
        if (File.Exists(buildPath))
        {
            using (var md5 = System.Security.Cryptography.MD5.Create())
            using (var sha256 = System.Security.Cryptography.SHA256.Create())
            {
                byte[] fileBytes = File.ReadAllBytes(buildPath);
                
                string md5Hash = System.BitConverter.ToString(md5.ComputeHash(fileBytes)).Replace("-", "").ToLower();
                string sha256Hash = System.BitConverter.ToString(sha256.ComputeHash(fileBytes)).Replace("-", "").ToLower();
                
                string checksumFile = buildPath + ".checksums";
                string[] checksums = {
                    $"MD5: {md5Hash}",
                    $"SHA256: {sha256Hash}"
                };
                
                File.WriteAllLines(checksumFile, checksums);
                Debug.Log($"Checksums generated: {checksumFile}");
            }
        }
    }
    
    private static bool ShouldCreateArchive(BuildTarget platform)
    {
        // Logic to determine if archive should be created
        return platform != BuildTarget.iOS; // iOS builds are already in a specific format
    }
    
    private static void CreateBuildArchive(string buildPath, BuildTarget platform)
    {
        // Create zip archive of the build
        string archivePath = buildPath + ".zip";
        
        if (platform == BuildTarget.StandaloneOSX)
        {
            // For macOS, archive the entire .app bundle
            CreateArchiveFromDirectory(buildPath, archivePath);
        }
        else if (Directory.Exists(Path.GetDirectoryName(buildPath)))
        {
            CreateArchiveFromDirectory(Path.GetDirectoryName(buildPath), archivePath);
        }
        
        Debug.Log($"Build archive created: {archivePath}");
    }
    
    private static void CreateArchiveFromDirectory(string sourceDir, string archivePath)
    {
        // Implementation would use System.IO.Compression or similar
        // This is a placeholder for the actual archiving logic
        Debug.Log($"Creating archive from {sourceDir} to {archivePath}");
    }
    
    private static bool ShouldAutoUpload(BuildTarget platform)
    {
        // Logic to determine if build should be automatically uploaded
        return System.Environment.GetEnvironmentVariable("AUTO_UPLOAD") == "true";
    }
    
    private static void UploadBuild(string buildPath, BuildTarget platform)
    {
        // Implementation for uploading builds to distribution service
        Debug.Log($"Uploading build {buildPath} for {platform}");
    }
    
    private static void LogBuildErrors(BuildReport report)
    {
        foreach (var step in report.steps)
        {
            foreach (var message in step.messages)
            {
                if (message.type == LogType.Error || message.type == LogType.Exception)
                {
                    Debug.LogError($"Build Error in {step.name}: {message.content}");
                }
            }
        }
    }
}
#endif
```

## 🔧 GitHub Actions CI/CD Pipeline

### Complete Unity Build Workflow
```yaml
# .github/workflows/unity-ci-cd.yml
name: Unity CI/CD Pipeline

on:
  push:
    branches: [ main, develop, 'release/*' ]
  pull_request:
    branches: [ main ]
  release:
    types: [ published ]

env:
  UNITY_VERSION: 2022.3.21f1
  PROJECT_PATH: .

jobs:
  # Job 1: Code Quality and Testing
  quality-check:
    name: Code Quality & Tests
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          lfs: true
      
      - name: Setup .NET
        uses: actions/setup-dotnet@v3
        with:
          dotnet-version: '6.0.x'
      
      - name: Cache Unity Library
        uses: actions/cache@v3
        with:
          path: ${{ env.PROJECT_PATH }}/Library
          key: Library-${{ runner.os }}-${{ hashFiles('**/ProjectSettings/ProjectVersion.txt') }}-${{ hashFiles('**/Packages/packages-lock.json') }}
          restore-keys: |
            Library-${{ runner.os }}-${{ hashFiles('**/ProjectSettings/ProjectVersion.txt') }}-
            Library-${{ runner.os }}-
      
      - name: Run Unity Tests
        uses: game-ci/unity-test-runner@v4
        env:
          UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}
          UNITY_EMAIL: ${{ secrets.UNITY_EMAIL }}
          UNITY_PASSWORD: ${{ secrets.UNITY_PASSWORD }}
        with:
          projectPath: ${{ env.PROJECT_PATH }}
          unityVersion: ${{ env.UNITY_VERSION }}
          githubToken: ${{ secrets.GITHUB_TOKEN }}
          checkName: 'Unity Test Results'
          coverageOptions: 'generateAdditionalMetrics'
      
      - name: Upload Test Results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: Test Results
          path: artifacts/
          retention-days: 30
      
      - name: Code Coverage Report
        uses: codecov/codecov-action@v4
        if: always()
        with:
          files: artifacts/coverage-results.xml
          flags: unittests
          name: unity-tests
          fail_ci_if_error: false

  # Job 2: Multi-Platform Builds
  build:
    name: Build ${{ matrix.targetPlatform }}
    runs-on: ${{ matrix.os }}
    needs: quality-check
    
    strategy:
      fail-fast: false
      matrix:
        include:
          - targetPlatform: StandaloneWindows64
            os: windows-latest
            buildMethod: 'BuildScript.BuildWindows'
          - targetPlatform: StandaloneOSX
            os: macos-latest
            buildMethod: 'BuildScript.BuildMacOS'
          - targetPlatform: StandaloneLinux64
            os: ubuntu-latest
            buildMethod: 'BuildScript.BuildLinux'
          - targetPlatform: WebGL
            os: ubuntu-latest
            buildMethod: 'BuildScript.BuildWebGL'
          - targetPlatform: iOS
            os: macos-latest
            buildMethod: 'BuildScript.BuildiOS'
          - targetPlatform: Android
            os: ubuntu-latest
            buildMethod: 'BuildScript.BuildAndroid'
    
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          lfs: true
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Cache Unity Library
        uses: actions/cache@v3
        with:
          path: ${{ env.PROJECT_PATH }}/Library
          key: Library-${{ matrix.targetPlatform }}-${{ hashFiles('**/ProjectSettings/ProjectVersion.txt') }}-${{ hashFiles('**/Packages/packages-lock.json') }}
          restore-keys: |
            Library-${{ matrix.targetPlatform }}-
            Library-
      
      - name: Free Disk Space (Ubuntu)
        if: matrix.os == 'ubuntu-latest'
        uses: jlumbroso/free-disk-space@main
        with:
          tool-cache: false
          android: true
          dotnet: true
          haskell: true
          large-packages: true
          swap-storage: true
      
      - name: Setup Unity
        uses: game-ci/unity-builder@v4
        env:
          UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}
          UNITY_EMAIL: ${{ secrets.UNITY_EMAIL }}
          UNITY_PASSWORD: ${{ secrets.UNITY_PASSWORD }}
        with:
          projectPath: ${{ env.PROJECT_PATH }}
          unityVersion: ${{ env.UNITY_VERSION }}
          targetPlatform: ${{ matrix.targetPlatform }}
          customImage: 'unityci/editor:ubuntu-${{ env.UNITY_VERSION }}-base-3.0.0'
          buildMethod: ${{ matrix.buildMethod }}
          versioning: Semantic
          allowDirtyBuild: false
      
      - name: Upload Build Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: Build-${{ matrix.targetPlatform }}
          path: build/${{ matrix.targetPlatform }}
          retention-days: 14
      
      - name: Upload to Internal Distribution (Android)
        if: matrix.targetPlatform == 'Android' && github.ref == 'refs/heads/develop'
        uses: wzieba/Firebase-Distribution-Github-Action@v1
        with:
          appId: ${{ secrets.FIREBASE_APP_ID }}
          serviceCredentialsFileContent: ${{ secrets.CREDENTIAL_FILE_CONTENT }}
          groups: internal-testers
          file: build/Android/Android.apk
          releaseNotes: "Automated build from commit ${{ github.sha }}"
      
      - name: Deploy to TestFlight (iOS)
        if: matrix.targetPlatform == 'iOS' && github.ref == 'refs/heads/main'
        uses: apple-actions/upload-testflight-build@v1
        with:
          app-path: build/iOS
          issuer-id: ${{ secrets.APPSTORE_ISSUER_ID }}
          api-key-id: ${{ secrets.APPSTORE_API_KEY_ID }}
          api-private-key: ${{ secrets.APPSTORE_API_PRIVATE_KEY }}

  # Job 3: Deploy WebGL Build
  deploy-web:
    name: Deploy WebGL
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
    
    steps:
      - name: Download WebGL Build
        uses: actions/download-artifact@v3
        with:
          name: Build-WebGL
          path: build-webgl/
      
      - name: Deploy to GitHub Pages (Main)
        if: github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: build-webgl/WebGL/WebGL
          destination_dir: production
      
      - name: Deploy to GitHub Pages (Develop)
        if: github.ref == 'refs/heads/develop'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: build-webgl/WebGL/WebGL
          destination_dir: staging
      
      - name: Deploy to AWS S3
        if: github.ref == 'refs/heads/main'
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Sync to S3
        if: github.ref == 'refs/heads/main'
        run: |
          aws s3 sync build-webgl/WebGL/WebGL/ s3://${{ secrets.S3_BUCKET_NAME }}/game/ --delete
          aws cloudfront create-invalidation --distribution-id ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }} --paths "/*"

  # Job 4: Release Management
  release:
    name: Create Release
    runs-on: ubuntu-latest
    needs: [quality-check, build]
    if: github.event_name == 'release'
    
    steps:
      - name: Download All Artifacts
        uses: actions/download-artifact@v3
        with:
          path: artifacts/
      
      - name: Create Release Archives
        run: |
          cd artifacts/
          for dir in Build-*/; do
            if [ -d "$dir" ]; then
              platform=$(echo "$dir" | sed 's/Build-//g' | sed 's/\///g')
              tar -czf "${platform}.tar.gz" -C "$dir" .
            fi
          done
      
      - name: Upload Release Assets
        uses: softprops/action-gh-release@v1
        with:
          files: artifacts/*.tar.gz
          body: |
            ## Release Notes
            
            This release was automatically generated from commit ${{ github.sha }}.
            
            ### Changes
            ${{ github.event.release.body }}
            
            ### Build Information
            - Unity Version: ${{ env.UNITY_VERSION }}
            - Build Date: ${{ github.event.release.created_at }}
            - Commit: ${{ github.sha }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  # Job 5: Notifications
  notify:
    name: Send Notifications
    runs-on: ubuntu-latest
    needs: [quality-check, build, deploy-web]
    if: always()
    
    steps:
      - name: Notify Slack (Success)
        if: needs.build.result == 'success'
        uses: 8398a7/action-slack@v3
        with:
          status: success
          channel: '#dev-builds'
          text: |
            ✅ Unity build completed successfully!
            Branch: ${{ github.ref_name }}
            Commit: ${{ github.sha }}
            Platforms: Windows, macOS, Linux, WebGL, iOS, Android
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
      
      - name: Notify Slack (Failure)
        if: needs.build.result == 'failure' || needs.quality-check.result == 'failure'
        uses: 8398a7/action-slack@v3
        with:
          status: failure
          channel: '#dev-builds'
          text: |
            ❌ Unity build failed!
            Branch: ${{ github.ref_name }}
            Commit: ${{ github.sha }}
            Check the logs: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
      
      - name: Update Discord
        if: needs.build.result == 'success' && github.ref == 'refs/heads/main'
        uses: Ilshidur/action-discord@master
        with:
          args: |
            🎮 New Unity build available!
            **WebGL Demo**: https://yourgame.github.io/production/
            **Download**: ${{ github.server_url }}/${{ github.repository }}/releases/latest
        env:
          DISCORD_WEBHOOK: ${{ secrets.DISCORD_WEBHOOK }}
```

## 🔧 Local Build Automation

### PowerShell Build Script (Windows)
```powershell
# BuildScript.ps1 - Automated Unity Build Script
param(
    [string]$UnityPath = "C:\Program Files\Unity\Hub\Editor\2022.3.21f1\Editor\Unity.exe",
    [string]$ProjectPath = ".",
    [string[]]$Platforms = @("StandaloneWindows64", "Android", "WebGL"),
    [string]$BuildPath = "Builds",
    [switch]$Development = $false,
    [switch]$Clean = $false,
    [switch]$Package = $false
)

# Configuration
$LogFile = "build-log-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$BuildMethod = "AdvancedBuildScript.BuildFromCommandLine"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

function Test-UnityInstallation {
    if (-not (Test-Path $UnityPath)) {
        Write-Log "Unity not found at: $UnityPath" "ERROR"
        Write-Log "Please install Unity or specify correct path with -UnityPath parameter" "ERROR"
        exit 1
    }
    Write-Log "Unity found at: $UnityPath" "SUCCESS"
}

function Clean-BuildDirectory {
    if ($Clean -and (Test-Path $BuildPath)) {
        Write-Log "Cleaning build directory: $BuildPath" "INFO"
        Remove-Item -Path $BuildPath -Recurse -Force
    }
    
    if (-not (Test-Path $BuildPath)) {
        New-Item -ItemType Directory -Path $BuildPath -Force | Out-Null
    }
}

function Build-Platform {
    param([string]$Platform)
    
    Write-Log "Starting build for platform: $Platform" "INFO"
    
    $OutputPath = Join-Path $BuildPath $Platform
    $LogPath = Join-Path $BuildPath "$Platform-unity.log"
    
    $UnityArgs = @(
        "-batchmode",
        "-quit",
        "-projectPath", "`"$ProjectPath`"",
        "-buildTarget", $Platform,
        "-executeMethod", $BuildMethod,
        "-logFile", "`"$LogPath`"",
        "-customBuildPath", "`"$OutputPath`"",
        "-customBuildName", "$(Split-Path -Leaf $ProjectPath)"
    )
    
    if ($Development) {
        $UnityArgs += "-development"
    }
    
    $Process = Start-Process -FilePath $UnityPath -ArgumentList $UnityArgs -Wait -PassThru -NoNewWindow
    
    if ($Process.ExitCode -eq 0) {
        Write-Log "Build completed successfully for $Platform" "SUCCESS"
        
        # Verify build output
        if (Test-Path $OutputPath) {
            $BuildSize = (Get-ChildItem -Path $OutputPath -Recurse | Measure-Object -Property Length -Sum).Sum
            Write-Log "Build size for $Platform: $([math]::Round($BuildSize / 1MB, 2)) MB" "INFO"
        }
        
        return $true
    } else {
        Write-Log "Build failed for $Platform with exit code: $($Process.ExitCode)" "ERROR"
        
        # Display Unity log if available
        if (Test-Path $LogPath) {
            Write-Log "Unity build log:" "ERROR"
            Get-Content $LogPath | Select-Object -Last 20 | ForEach-Object { Write-Log $_ "ERROR" }
        }
        
        return $false
    }
}

function Package-Builds {
    if (-not $Package) { return }
    
    Write-Log "Creating build packages..." "INFO"
    
    foreach ($Platform in $Platforms) {
        $PlatformPath = Join-Path $BuildPath $Platform
        if (Test-Path $PlatformPath) {
            $ArchivePath = Join-Path $BuildPath "$Platform.zip"
            
            try {
                Compress-Archive -Path "$PlatformPath\*" -DestinationPath $ArchivePath -Force
                Write-Log "Package created: $ArchivePath" "SUCCESS"
            } catch {
                Write-Log "Failed to create package for $Platform`: $($_.Exception.Message)" "ERROR"
            }
        }
    }
}

function Generate-BuildReport {
    $ReportPath = Join-Path $BuildPath "build-report.json"
    
    $Report = @{
        BuildDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Platforms = @()
        TotalBuildTime = 0
        Success = $true
    }
    
    foreach ($Platform in $Platforms) {
        $PlatformPath = Join-Path $BuildPath $Platform
        $PlatformInfo = @{
            Name = $Platform
            Success = Test-Path $PlatformPath
            Size = 0
        }
        
        if ($PlatformInfo.Success) {
            $PlatformInfo.Size = (Get-ChildItem -Path $PlatformPath -Recurse | Measure-Object -Property Length -Sum).Sum
        } else {
            $Report.Success = $false
        }
        
        $Report.Platforms += $PlatformInfo
    }
    
    $Report | ConvertTo-Json -Depth 3 | Out-File -FilePath $ReportPath -Encoding UTF8
    Write-Log "Build report generated: $ReportPath" "INFO"
}

# Main execution
try {
    Write-Log "Starting Unity build process..." "INFO"
    Write-Log "Project: $ProjectPath" "INFO"
    Write-Log "Platforms: $($Platforms -join ', ')" "INFO"
    Write-Log "Development Build: $Development" "INFO"
    
    Test-UnityInstallation
    Clean-BuildDirectory
    
    $StartTime = Get-Date
    $SuccessfulBuilds = 0
    
    foreach ($Platform in $Platforms) {
        if (Build-Platform $Platform) {
            $SuccessfulBuilds++
        }
    }
    
    $EndTime = Get-Date
    $TotalTime = $EndTime - $StartTime
    
    Write-Log "Build process completed in $([math]::Round($TotalTime.TotalMinutes, 2)) minutes" "INFO"
    Write-Log "Successful builds: $SuccessfulBuilds / $($Platforms.Count)" "INFO"
    
    Package-Builds
    Generate-BuildReport
    
    if ($SuccessfulBuilds -eq $Platforms.Count) {
        Write-Log "All builds completed successfully!" "SUCCESS"
        exit 0
    } else {
        Write-Log "Some builds failed. Check the logs for details." "WARNING"
        exit 1
    }
    
} catch {
    Write-Log "Build script error: $($_.Exception.Message)" "ERROR"
    exit 1
}
```

## 🚀 AI/LLM Integration Opportunities

### Content Generation Prompts
```
"Generate a Unity build script for [platform] that handles [specific requirements] including error handling, logging, and artifact management."

"Create a CI/CD pipeline configuration for [service] that builds Unity projects for [platforms] with automated testing and deployment to [distribution platforms]."

"Design a build optimization strategy for [project type] that reduces build times and improves reliability for a team of [size] developers."
```

### Learning Acceleration
- **Pipeline Optimization**: "How can I optimize our Unity build pipeline for faster iteration times?"
- **Error Resolution**: "Debug this Unity build error: [error message] occurring during [build phase]"
- **Platform-Specific Issues**: "Resolve Unity build issues for [platform] related to [specific problem area]"

### Advanced Applications
- **Automated Testing Integration**: Unit test, integration test, and performance test automation
- **Multi-Environment Deployment**: Staging, production, and feature branch deployment strategies
- **Build Analytics**: Performance monitoring and build time optimization analysis

## 💡 Key Highlights

### Essential Build System Components
- **Version Control Integration**: Automated versioning based on git commits and tags
- **Multi-Platform Support**: Consistent builds across Windows, macOS, Linux, Mobile, and Web
- **Quality Gates**: Automated testing, code analysis, and approval workflows
- **Artifact Management**: Build storage, distribution, and retention policies

### Performance Optimization Strategies
- **Incremental Builds**: Only rebuild changed components to reduce build times
- **Parallel Execution**: Multiple platform builds running simultaneously
- **Caching Systems**: Library, package, and intermediate file caching
- **Build Agent Optimization**: Proper resource allocation and clean environments

### Security and Compliance
- **Code Signing**: Proper certificate management for production builds
- **Secret Management**: Secure handling of API keys, certificates, and credentials
- **Audit Trails**: Complete build history and change tracking
- **Access Control**: Role-based permissions for build triggers and deployments

### Monitoring and Analytics
- **Build Metrics**: Success rates, build times, and failure analysis
- **Performance Tracking**: Resource usage and optimization opportunities
- **Alerting Systems**: Immediate notification of build failures or issues
- **Reporting Dashboards**: Visual build status and trend analysis

### Integration Patterns
- **Git Workflow Integration**: Branch-based builds and merge request validation
- **Issue Tracking**: Automatic linking of builds to tickets and user stories
- **Documentation Systems**: Automated API documentation and release notes
- **Distribution Platforms**: Steam, App Store, Google Play, and web deployment automation

This comprehensive build system and CI/CD knowledge provides the foundation for reliable, scalable, and efficient Unity development workflows that support professional game development teams.