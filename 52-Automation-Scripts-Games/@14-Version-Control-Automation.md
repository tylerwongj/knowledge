# @14-Version-Control-Automation

## 🎯 Core Concept
Automated Git workflows and version control management for Unity game development projects.

## 🔧 Implementation

### Git Automation Manager
```csharp
using UnityEngine;
using UnityEditor;
using System.Diagnostics;

public class GitAutomationManager
{
    [MenuItem("Git/Quick Commit")]
    public static void QuickCommit()
    {
        string commitMessage = EditorInputDialog.Show("Commit Message", "Enter commit message:", "Update game assets");
        
        if (!string.IsNullOrEmpty(commitMessage))
        {
            ExecuteGitCommand("add .");
            ExecuteGitCommand($"commit -m \"[CC] {GetCurrentBranch()} - {commitMessage}\"");
            
            Debug.Log($"Committed changes: {commitMessage}");
        }
    }
    
    [MenuItem("Git/Push Changes")]
    public static void PushChanges()
    {
        string result = ExecuteGitCommand("push origin HEAD");
        
        if (result.Contains("error") || result.Contains("failed"))
        {
            Debug.LogError($"Push failed: {result}");
        }
        else
        {
            Debug.Log("Changes pushed successfully");
        }
    }
    
    [MenuItem("Git/Pull Latest")]
    public static void PullLatest()
    {
        string result = ExecuteGitCommand("pull origin HEAD");
        
        if (result.Contains("error") || result.Contains("failed"))
        {
            Debug.LogError($"Pull failed: {result}");
        }
        else
        {
            Debug.Log("Pulled latest changes");
            AssetDatabase.Refresh();
        }
    }
    
    [MenuItem("Git/Create Feature Branch")]
    public static void CreateFeatureBranch()
    {
        string branchName = EditorInputDialog.Show("New Branch", "Enter branch name:", "feature/new-feature");
        
        if (!string.IsNullOrEmpty(branchName))
        {
            ExecuteGitCommand($"checkout -b {branchName}");
            Debug.Log($"Created and switched to branch: {branchName}");
        }
    }
    
    [MenuItem("Git/Show Status")]
    public static void ShowStatus()
    {
        string status = ExecuteGitCommand("status --porcelain");
        
        if (string.IsNullOrEmpty(status))
        {
            Debug.Log("Working directory clean");
        }
        else
        {
            Debug.Log($"Git Status:\\n{status}");
        }
    }
    
    [MenuItem("Git/View Recent Commits")]
    public static void ViewRecentCommits()
    {
        string commits = ExecuteGitCommand("log --oneline -10");
        Debug.Log($"Recent Commits:\\n{commits}");
    }
    
    [MenuItem("Git/Backup Current Work")]
    public static void BackupCurrentWork()
    {
        string timestamp = System.DateTime.Now.ToString("yyyyMMdd_HHmmss");
        string branchName = $"backup/{timestamp}";
        
        ExecuteGitCommand("add .");
        ExecuteGitCommand($"commit -m \"[CC] backup - Work in progress backup {timestamp}\"");
        ExecuteGitCommand($"branch {branchName}");
        
        Debug.Log($"Work backed up to branch: {branchName}");
    }
    
    static string ExecuteGitCommand(string command)
    {
        try
        {
            ProcessStartInfo startInfo = new ProcessStartInfo
            {
                FileName = "git",
                Arguments = command,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                WorkingDirectory = Application.dataPath + "/.."
            };
            
            using (Process process = Process.Start(startInfo))
            {
                string output = process.StandardOutput.ReadToEnd();
                string error = process.StandardError.ReadToEnd();
                process.WaitForExit();
                
                return string.IsNullOrEmpty(error) ? output : error;
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Git command failed: {e.Message}");
            return "";
        }
    }
    
    static string GetCurrentBranch()
    {
        string result = ExecuteGitCommand("branch --show-current");
        return result.Trim();
    }
}

// Simple input dialog utility
public class EditorInputDialog
{
    public static string Show(string title, string message, string defaultValue = "")
    {
        // This is a simplified version - in practice you'd want a proper EditorWindow
        return EditorUtility.DisplayDialog(title, message, "OK", "Cancel") ? defaultValue : "";
    }
}
```

### Automated Backup System
```csharp
[InitializeOnLoad]
public class AutoBackupSystem
{
    private static double lastBackupTime;
    private const double BACKUP_INTERVAL = 3600; // 1 hour in seconds
    
    static AutoBackupSystem()
    {
        EditorApplication.update += CheckAutoBackup;
    }
    
    static void CheckAutoBackup()
    {
        double currentTime = EditorApplication.timeSinceStartup;
        
        if (currentTime - lastBackupTime > BACKUP_INTERVAL)
        {
            PerformAutoBackup();
            lastBackupTime = currentTime;
        }
    }
    
    static void PerformAutoBackup()
    {
        if (HasUncommittedChanges())
        {
            string timestamp = System.DateTime.Now.ToString("yyyy-MM-dd_HH-mm");
            GitAutomationManager.ExecuteGitCommand("add .");
            GitAutomationManager.ExecuteGitCommand($"commit -m \"[CC] auto-backup - Automatic backup {timestamp}\"");
            
            Debug.Log($"Auto-backup created: {timestamp}");
        }
    }
    
    static bool HasUncommittedChanges()
    {
        string status = GitAutomationManager.ExecuteGitCommand("status --porcelain");
        return !string.IsNullOrEmpty(status.Trim());
    }
}
```

## 🚀 AI/LLM Integration
- Generate intelligent commit messages based on changes
- Automate branch naming conventions
- Create merge conflict resolution suggestions

## 💡 Key Benefits
- Streamlined version control workflows
- Automated backup systems
- Consistent commit message formatting