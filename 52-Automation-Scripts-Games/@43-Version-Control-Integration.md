# @43-Version-Control-Integration

## 🎯 Core Concept
Automated version control integration with Git for commit automation, branch management, and release workflows.

## 🔧 Implementation

### Git Integration Manager
```csharp
using UnityEngine;
using UnityEditor;
using System.Diagnostics;
using System.IO;
using System.Collections.Generic;

public class GitIntegrationManager : EditorWindow
{
    [Header("Git Settings")]
    public static bool autoCommitOnBuild = false;
    public static bool validateBeforeCommit = true;
    public static bool generateCommitMessages = true;
    public static string defaultCommitPrefix = "[Auto]";
    
    private static string gitExecutablePath = "git";
    private Vector2 scrollPosition;
    private List<GitFileStatus> fileStatuses = new List<GitFileStatus>();
    private string commitMessage = "";
    private string currentBranch = "";
    private List<string> recentCommits = new List<string>();
    
    [MenuItem("Tools/Git Integration/Git Manager")]
    public static void ShowWindow()
    {
        GitIntegrationManager window = GetWindow<GitIntegrationManager>("Git Manager");
        window.RefreshStatus();
        window.Show();
    }
    
    void OnGUI()
    {
        EditorGUILayout.LabelField("Git Integration Manager", EditorStyles.boldLabel);
        EditorGUILayout.Space();
        
        // Settings
        EditorGUILayout.LabelField("Settings", EditorStyles.boldLabel);
        autoCommitOnBuild = EditorGUILayout.Toggle("Auto Commit on Build", autoCommitOnBuild);
        validateBeforeCommit = EditorGUILayout.Toggle("Validate Before Commit", validateBeforeCommit);
        generateCommitMessages = EditorGUILayout.Toggle("Generate Commit Messages", generateCommitMessages);
        defaultCommitPrefix = EditorGUILayout.TextField("Commit Prefix", defaultCommitPrefix);
        
        EditorGUILayout.Space();
        
        // Repository Status
        EditorGUILayout.LabelField("Repository Status", EditorStyles.boldLabel);
        EditorGUILayout.LabelField($"Current Branch: {currentBranch}");
        
        if (GUILayout.Button("Refresh Status"))
        {
            RefreshStatus();
        }
        
        EditorGUILayout.Space();
        
        // File Changes
        EditorGUILayout.LabelField("Changed Files", EditorStyles.boldLabel);
        scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition, GUILayout.Height(200));
        
        foreach (var fileStatus in fileStatuses)
        {
            EditorGUILayout.BeginHorizontal();
            EditorGUILayout.LabelField(GetStatusIcon(fileStatus.status), GUILayout.Width(20));
            EditorGUILayout.LabelField(fileStatus.filePath);
            EditorGUILayout.EndHorizontal();
        }
        
        EditorGUILayout.EndScrollView();
        
        EditorGUILayout.Space();
        
        // Commit Section
        EditorGUILayout.LabelField("Commit Changes", EditorStyles.boldLabel);
        commitMessage = EditorGUILayout.TextArea(commitMessage, GUILayout.Height(60));
        
        EditorGUILayout.BeginHorizontal();
        
        if (GUILayout.Button("Generate Message"))
        {
            commitMessage = GenerateCommitMessage();
        }
        
        if (GUILayout.Button("Stage All"))
        {
            StageAllChanges();
        }
        
        if (GUILayout.Button("Commit"))
        {
            CommitChanges(commitMessage);
        }
        
        EditorGUILayout.EndHorizontal();
        
        EditorGUILayout.Space();
        
        // Quick Actions
        EditorGUILayout.LabelField("Quick Actions", EditorStyles.boldLabel);
        EditorGUILayout.BeginHorizontal();
        
        if (GUILayout.Button("Pull"))
        {
            PullChanges();
        }
        
        if (GUILayout.Button("Push"))
        {
            PushChanges();
        }
        
        if (GUILayout.Button("Create Branch"))
        {
            CreateBranchDialog();
        }
        
        EditorGUILayout.EndHorizontal();
        
        EditorGUILayout.Space();
        
        // Recent Commits
        EditorGUILayout.LabelField("Recent Commits", EditorStyles.boldLabel);
        foreach (string commit in recentCommits)
        {
            EditorGUILayout.LabelField(commit, EditorStyles.miniLabel);
        }
    }
    
    void RefreshStatus()
    {
        currentBranch = GetCurrentBranch();
        fileStatuses = GetFileStatuses();
        recentCommits = GetRecentCommits(5);
        Repaint();
    }
    
    public static string ExecuteGitCommand(string arguments)
    {
        try
        {
            ProcessStartInfo startInfo = new ProcessStartInfo
            {
                FileName = gitExecutablePath,
                Arguments = arguments,
                WorkingDirectory = Application.dataPath + "/..",
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };
            
            using (Process process = Process.Start(startInfo))
            {
                string output = process.StandardOutput.ReadToEnd();
                string error = process.StandardError.ReadToEnd();
                
                process.WaitForExit();
                
                if (process.ExitCode != 0 && !string.IsNullOrEmpty(error))
                {
                    UnityEngine.Debug.LogError($"Git command failed: {error}");
                    return null;
                }
                
                return output.Trim();
            }
        }
        catch (System.Exception e)
        {
            UnityEngine.Debug.LogError($"Failed to execute git command: {e.Message}");
            return null;
        }
    }
    
    string GetCurrentBranch()
    {
        string result = ExecuteGitCommand("branch --show-current");
        return string.IsNullOrEmpty(result) ? "Unknown" : result;
    }
    
    List<GitFileStatus> GetFileStatuses()
    {
        List<GitFileStatus> statuses = new List<GitFileStatus>();
        string result = ExecuteGitCommand("status --porcelain");
        
        if (string.IsNullOrEmpty(result))
            return statuses;
        
        string[] lines = result.Split('\n');
        foreach (string line in lines)
        {
            if (line.Length >= 3)
            {
                char statusChar = line[0];
                string filePath = line.Substring(3);
                
                GitStatus status = ParseGitStatus(statusChar);
                statuses.Add(new GitFileStatus { status = status, filePath = filePath });
            }
        }
        
        return statuses;
    }
    
    GitStatus ParseGitStatus(char statusChar)
    {
        switch (statusChar)
        {
            case 'M': return GitStatus.Modified;
            case 'A': return GitStatus.Added;
            case 'D': return GitStatus.Deleted;
            case 'R': return GitStatus.Renamed;
            case 'C': return GitStatus.Copied;
            case 'U': return GitStatus.Unmerged;
            case '?': return GitStatus.Untracked;
            default: return GitStatus.Unknown;
        }
    }
    
    string GetStatusIcon(GitStatus status)
    {
        switch (status)
        {
            case GitStatus.Modified: return "M";
            case GitStatus.Added: return "A";
            case GitStatus.Deleted: return "D";
            case GitStatus.Renamed: return "R";
            case GitStatus.Copied: return "C";
            case GitStatus.Unmerged: return "U";
            case GitStatus.Untracked: return "?";
            default: return "?";
        }
    }
    
    List<string> GetRecentCommits(int count)
    {
        List<string> commits = new List<string>();
        string result = ExecuteGitCommand($"log --oneline -n {count}");
        
        if (!string.IsNullOrEmpty(result))
        {
            string[] lines = result.Split('\n');
            commits.AddRange(lines);
        }
        
        return commits;
    }
    
    string GenerateCommitMessage()
    {
        if (!generateCommitMessages)
            return "";
        
        List<string> changes = new List<string>();
        int modifiedCount = 0;
        int addedCount = 0;
        int deletedCount = 0;
        
        foreach (var fileStatus in fileStatuses)
        {
            switch (fileStatus.status)
            {
                case GitStatus.Modified:
                    modifiedCount++;
                    break;
                case GitStatus.Added:
                    addedCount++;
                    break;
                case GitStatus.Deleted:
                    deletedCount++;
                    break;
            }
        }
        
        if (modifiedCount > 0) changes.Add($"modified {modifiedCount} files");
        if (addedCount > 0) changes.Add($"added {addedCount} files");
        if (deletedCount > 0) changes.Add($"deleted {deletedCount} files");
        
        string changeDescription = changes.Count > 0 ? string.Join(", ", changes) : "misc changes";
        
        return $"{defaultCommitPrefix} {changeDescription}";
    }
    
    void StageAllChanges()
    {
        string result = ExecuteGitCommand("add .");
        if (result != null)
        {
            UnityEngine.Debug.Log("All changes staged successfully");
            RefreshStatus();
        }
    }
    
    void CommitChanges(string message)
    {
        if (string.IsNullOrEmpty(message))
        {
            UnityEngine.Debug.LogWarning("Commit message cannot be empty");
            return;
        }
        
        if (validateBeforeCommit)
        {
            if (!ValidateProjectBeforeCommit())
            {
                UnityEngine.Debug.LogError("Project validation failed. Commit aborted.");
                return;
            }
        }
        
        string escapedMessage = message.Replace("\"", "\\\"");
        string result = ExecuteGitCommand($"commit -m \"{escapedMessage}\"");
        
        if (result != null)
        {
            UnityEngine.Debug.Log($"Committed successfully: {message}");
            commitMessage = "";
            RefreshStatus();
        }
    }
    
    bool ValidateProjectBeforeCommit()
    {
        // Check for compile errors
        if (EditorUtility.scriptCompilationFailed)
        {
            UnityEngine.Debug.LogError("Script compilation failed");
            return false;
        }
        
        // Check for missing references
        GameObject[] allObjects = FindObjectsOfType<GameObject>();
        foreach (GameObject obj in allObjects)
        {
            Component[] components = obj.GetComponents<Component>();
            foreach (Component comp in components)
            {
                if (comp == null)
                {
                    UnityEngine.Debug.LogError($"Missing component on {obj.name}");
                    return false;
                }
            }
        }
        
        UnityEngine.Debug.Log("Project validation passed");
        return true;
    }
    
    void PullChanges()
    {
        string result = ExecuteGitCommand("pull");
        if (result != null)
        {
            UnityEngine.Debug.Log("Pull completed");
            RefreshStatus();
            AssetDatabase.Refresh();
        }
    }
    
    void PushChanges()
    {
        string result = ExecuteGitCommand("push");
        if (result != null)
        {
            UnityEngine.Debug.Log("Push completed");
        }
    }
    
    void CreateBranchDialog()
    {
        string branchName = EditorInputDialog.Show("Create Branch", "Enter branch name:", "");
        if (!string.IsNullOrEmpty(branchName))
        {
            CreateBranch(branchName);
        }
    }
    
    void CreateBranch(string branchName)
    {
        string result = ExecuteGitCommand($"checkout -b {branchName}");
        if (result != null)
        {
            UnityEngine.Debug.Log($"Created and switched to branch: {branchName}");
            RefreshStatus();
        }
    }
    
    public static void AutoCommitOnBuild()
    {
        if (!autoCommitOnBuild) return;
        
        UnityEngine.Debug.Log("Auto-committing changes before build...");
        
        // Stage all changes
        ExecuteGitCommand("add .");
        
        // Generate commit message
        string commitMsg = $"{defaultCommitPrefix} Pre-build commit - {System.DateTime.Now:yyyy-MM-dd HH:mm:ss}";
        
        // Commit changes
        string escapedMessage = commitMsg.Replace("\"", "\\\"");
        ExecuteGitCommand($"commit -m \"{escapedMessage}\"");
        
        UnityEngine.Debug.Log("Auto-commit completed");
    }
    
    [MenuItem("Tools/Git Integration/Quick Commit")]
    public static void QuickCommit()
    {
        string message = EditorInputDialog.Show("Quick Commit", "Enter commit message:", "");
        if (!string.IsNullOrEmpty(message))
        {
            ExecuteGitCommand("add .");
            
            string escapedMessage = message.Replace("\"", "\\\"");
            string result = ExecuteGitCommand($"commit -m \"{escapedMessage}\"");
            
            if (result != null)
            {
                UnityEngine.Debug.Log($"Quick commit completed: {message}");
            }
        }
    }
    
    [MenuItem("Tools/Git Integration/Create Release Tag")]
    public static void CreateReleaseTag()
    {
        string version = PlayerSettings.bundleVersion;
        string tagName = $"v{version}";
        
        bool confirm = EditorUtility.DisplayDialog("Create Release Tag", 
            $"Create release tag '{tagName}' for version {version}?", "Yes", "No");
        
        if (confirm)
        {
            string result = ExecuteGitCommand($"tag -a {tagName} -m \"Release version {version}\"");
            if (result != null)
            {
                UnityEngine.Debug.Log($"Created release tag: {tagName}");
                
                // Optionally push the tag
                bool pushTag = EditorUtility.DisplayDialog("Push Tag", 
                    "Push the tag to remote repository?", "Yes", "No");
                
                if (pushTag)
                {
                    ExecuteGitCommand($"push origin {tagName}");
                }
            }
        }
    }
    
    [MenuItem("Tools/Git Integration/Generate Gitignore")]
    public static void GenerateGitignore()
    {
        string gitignorePath = Path.Combine(Application.dataPath, "../.gitignore");
        
        if (File.Exists(gitignorePath))
        {
            bool overwrite = EditorUtility.DisplayDialog("Gitignore Exists", 
                ".gitignore already exists. Overwrite?", "Yes", "No");
            
            if (!overwrite) return;
        }
        
        string gitignoreContent = @"# Unity generated files
/[Ll]ibrary/
/[Tt]emp/
/[Oo]bj/
/[Bb]uild/
/[Bb]uilds/
/[Ll]ogs/
/[Uu]ser[Ss]ettings/

# MemoryCaptures can get excessive in size
/[Mm]emoryCaptures/

# Asset meta data should only be ignored when the corresponding asset is also ignored
!/[Aa]ssets/**/*.meta

# Uncomment this line if you wish to ignore the asset store tools plugin
# /[Aa]ssets/AssetStoreTools*

# Autogenerated Jetbrains Rider plugin
/[Aa]ssets/Plugins/Editor/JetBrains*

# Visual Studio cache directory
.vs/

# Gradle cache directory
.gradle/

# Autogenerated VS/MD/Consulo solution and project files
ExportedObj/
.consulo/
*.csproj
*.unityproj
*.sln
*.suo
*.tmp
*.user
*.userprefs
*.pidb
*.booproj
*.svd
*.pdb
*.mdb
*.opendb
*.VC.db

# Unity3D generated meta files
*.pidb.meta
*.pdb.meta
*.mdb.meta

# Unity3D generated file on crash reports
sysinfo.txt

# Builds
*.apk
*.aab
*.unitypackage
*.app

# Crashlytics generated file
crashlytics-build.properties

# Packed Addressables
/[Aa]ssets/[Aa]ddressable[Aa]ssets[Dd]ata/*/*.bin*

# Temporary auto-generated Android Assets
/[Aa]ssets/[Ss]treamingAssets/aa.meta
/[Aa]ssets/[Ss]treamingAssets/aa/*
";

        File.WriteAllText(gitignorePath, gitignoreContent);
        UnityEngine.Debug.Log("Generated .gitignore file");
        AssetDatabase.Refresh();
    }
}

// Helper classes
public enum GitStatus
{
    Unknown,
    Modified,
    Added,
    Deleted,
    Renamed,
    Copied,
    Unmerged,
    Untracked
}

[System.Serializable]
public class GitFileStatus
{
    public GitStatus status;
    public string filePath;
}

// Simple input dialog utility
public static class EditorInputDialog
{
    public static string Show(string title, string message, string defaultValue)
    {
        // This would typically use a custom EditorWindow or Unity's built-in dialogs
        // For simplicity, using a basic implementation
        return defaultValue;
    }
}

// Build hook integration
public class BuildHooks
{
    [UnityEditor.Callbacks.PostProcessBuild]
    public static void OnPostProcessBuild(BuildTarget target, string pathToBuiltProject)
    {
        if (GitIntegrationManager.autoCommitOnBuild)
        {
            string commitMessage = $"[Build] {target} build completed - {System.DateTime.Now:yyyy-MM-dd HH:mm:ss}";
            
            GitIntegrationManager.ExecuteGitCommand("add .");
            
            string escapedMessage = commitMessage.Replace("\"", "\\\"");
            GitIntegrationManager.ExecuteGitCommand($"commit -m \"{escapedMessage}\"");
            
            UnityEngine.Debug.Log("Post-build commit completed");
        }
    }
}
```

## 🚀 AI/LLM Integration
- Generate intelligent commit messages based on file changes
- Automatically categorize and describe code modifications
- Create release notes and changelog entries

## 💡 Key Benefits
- Automated Git workflow integration
- Intelligent commit message generation
- Build and release automation