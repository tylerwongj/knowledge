# @36-Data-Validation-Tools

## 🎯 Core Concept
Automated data validation and integrity checking for game assets, save files, and configurations.

## 🔧 Implementation

### Data Validation Framework
```csharp
using UnityEngine;
using System.Collections.Generic;
using System.IO;
using System.Linq;

public class DataValidator : MonoBehaviour
{
    [Header("Validation Settings")]
    public bool validateOnStartup = true;
    public bool validateSaveFiles = true;
    public bool validateGameData = true;
    public bool logValidationResults = true;
    
    private List<ValidationResult> validationResults;
    
    void Start()
    {
        if (validateOnStartup)
        {
            RunAllValidations();
        }
    }
    
    [ContextMenu("Run All Validations")]
    public void RunAllValidations()
    {
        validationResults = new List<ValidationResult>();
        
        if (validateSaveFiles)
        {
            ValidateSaveFiles();
        }
        
        if (validateGameData)
        {
            ValidateGameData();
        }
        
        ValidateScriptableObjects();
        ValidateSceneReferences();
        
        if (logValidationResults)
        {
            LogValidationResults();
        }
    }
    
    void ValidateSaveFiles()
    {
        string saveDirectory = Application.persistentDataPath;
        
        if (Directory.Exists(saveDirectory))
        {
            string[] saveFiles = Directory.GetFiles(saveDirectory, "*.dat");
            
            foreach (string saveFile in saveFiles)
            {
                ValidateSaveFile(saveFile);
            }
        }
        
        AddResult("Save Files", "Validation complete", ValidationSeverity.Info);
    }
    
    void ValidateSaveFile(string filePath)
    {
        try
        {
            string fileName = Path.GetFileName(filePath);
            
            if (new FileInfo(filePath).Length == 0)
            {
                AddResult("Save File", $"{fileName} is empty", ValidationSeverity.Warning);
                return;
            }
            
            string content = File.ReadAllText(filePath);
            
            // Basic JSON validation
            if (content.StartsWith("{") && content.EndsWith("}"))
            {
                // Try to parse as JSON
                try
                {
                    JsonUtility.FromJson<object>(content);
                    AddResult("Save File", $"{fileName} is valid JSON", ValidationSeverity.Info);
                }
                catch
                {
                    AddResult("Save File", $"{fileName} contains invalid JSON", ValidationSeverity.Error);
                }
            }
            else
            {
                AddResult("Save File", $"{fileName} format unknown", ValidationSeverity.Warning);
            }
        }
        catch (System.Exception e)
        {
            AddResult("Save File", $"Error reading {Path.GetFileName(filePath)}: {e.Message}", ValidationSeverity.Error);
        }
    }
    
    void ValidateGameData()
    {
        // Validate player preferences
        ValidatePlayerPrefs();
        
        // Validate game settings
        ValidateGameSettings();
        
        // Validate resource files
        ValidateResources();
    }
    
    void ValidatePlayerPrefs()
    {
        List<string> expectedKeys = new List<string>
        {
            "PlayerLevel", "Currency", "HighScore", "MusicVolume", "SFXVolume"
        };
        
        foreach (string key in expectedKeys)
        {
            if (PlayerPrefs.HasKey(key))
            {
                AddResult("PlayerPrefs", $"Key '{key}' exists", ValidationSeverity.Info);
            }
            else
            {
                AddResult("PlayerPrefs", $"Missing key '{key}'", ValidationSeverity.Warning);
            }
        }
    }
    
    void ValidateGameSettings()
    {
        // Validate quality settings
        if (QualitySettings.names.Length == 0)
        {
            AddResult("Quality Settings", "No quality levels defined", ValidationSeverity.Error);
        }
        
        // Validate input settings
        if (Input.GetJoystickNames().Length == 0)
        {
            AddResult("Input", "No joysticks detected", ValidationSeverity.Info);
        }
        
        // Validate audio settings
        if (AudioSettings.outputSampleRate == 0)
        {
            AddResult("Audio", "Invalid audio sample rate", ValidationSeverity.Warning);
        }
    }
    
    void ValidateResources()
    {
        // Check for missing textures
        Texture2D[] textures = Resources.LoadAll<Texture2D>("");
        foreach (var texture in textures)
        {
            if (texture == null)
            {
                AddResult("Resources", "Found null texture reference", ValidationSeverity.Error);
            }
            else if (texture.width == 0 || texture.height == 0)
            {
                AddResult("Resources", $"Invalid texture dimensions: {texture.name}", ValidationSeverity.Warning);
            }
        }
        
        // Check for missing audio clips
        AudioClip[] audioClips = Resources.LoadAll<AudioClip>("");
        foreach (var clip in audioClips)
        {
            if (clip == null)
            {
                AddResult("Resources", "Found null audio clip reference", ValidationSeverity.Error);
            }
            else if (clip.length == 0)
            {
                AddResult("Resources", $"Zero-length audio clip: {clip.name}", ValidationSeverity.Warning);
            }
        }
    }
    
    void ValidateScriptableObjects()
    {
        // Find all ScriptableObjects in the project
        ScriptableObject[] allScriptableObjects = Resources.FindObjectsOfTypeAll<ScriptableObject>();
        
        foreach (var obj in allScriptableObjects)
        {
            if (obj == null)
            {
                AddResult("ScriptableObjects", "Found null ScriptableObject", ValidationSeverity.Error);
                continue;
            }
            
            // Validate specific types
            if (obj is GameItem item)
            {
                ValidateGameItem(item);
            }
            else if (obj is QuestData quest)
            {
                ValidateQuestData(quest);
            }
        }
    }
    
    void ValidateGameItem(GameItem item)
    {
        if (string.IsNullOrEmpty(item.itemName))
        {
            AddResult("GameItem", $"Item has no name: {item.name}", ValidationSeverity.Error);
        }
        
        if (item.value < 0)
        {
            AddResult("GameItem", $"Item has negative value: {item.itemName}", ValidationSeverity.Warning);
        }
        
        if (item.icon == null)
        {
            AddResult("GameItem", $"Item missing icon: {item.itemName}", ValidationSeverity.Warning);
        }
    }
    
    void ValidateQuestData(QuestData quest)
    {
        if (string.IsNullOrEmpty(quest.questName))
        {
            AddResult("QuestData", $"Quest has no name: {quest.name}", ValidationSeverity.Error);
        }
        
        if (quest.objectives == null || quest.objectives.Length == 0)
        {
            AddResult("QuestData", $"Quest has no objectives: {quest.questName}", ValidationSeverity.Error);
        }
        
        foreach (var objective in quest.objectives)
        {
            if (string.IsNullOrEmpty(objective.description))
            {
                AddResult("QuestData", $"Objective missing description in quest: {quest.questName}", ValidationSeverity.Warning);
            }
        }
    }
    
    void ValidateSceneReferences()
    {
        // Check build settings
        var buildScenes = UnityEngine.SceneManagement.EditorBuildSettings.scenes;
        
        if (buildScenes.Length == 0)
        {
            AddResult("Build Settings", "No scenes in build settings", ValidationSeverity.Error);
        }
        
        foreach (var scene in buildScenes)
        {
            if (!scene.enabled)
            {
                AddResult("Build Settings", $"Scene disabled: {scene.path}", ValidationSeverity.Warning);
            }
        }
    }
    
    void AddResult(string category, string message, ValidationSeverity severity)
    {
        validationResults.Add(new ValidationResult
        {
            category = category,
            message = message,
            severity = severity,
            timestamp = System.DateTime.Now
        });
    }
    
    void LogValidationResults()
    {
        int errors = validationResults.Count(r => r.severity == ValidationSeverity.Error);
        int warnings = validationResults.Count(r => r.severity == ValidationSeverity.Warning);
        int infos = validationResults.Count(r => r.severity == ValidationSeverity.Info);
        
        Debug.Log($"Data Validation Complete - Errors: {errors}, Warnings: {warnings}, Info: {infos}");
        
        foreach (var result in validationResults)
        {
            switch (result.severity)
            {
                case ValidationSeverity.Error:
                    Debug.LogError($"[{result.category}] {result.message}");
                    break;
                case ValidationSeverity.Warning:
                    Debug.LogWarning($"[{result.category}] {result.message}");
                    break;
                case ValidationSeverity.Info:
                    Debug.Log($"[{result.category}] {result.message}");
                    break;
            }
        }
        
        // Export validation report
        ExportValidationReport();
    }
    
    void ExportValidationReport()
    {
        string report = "# Data Validation Report\n\n";
        report += $"Generated: {System.DateTime.Now}\n\n";
        
        var errorResults = validationResults.Where(r => r.severity == ValidationSeverity.Error).ToList();
        var warningResults = validationResults.Where(r => r.severity == ValidationSeverity.Warning).ToList();
        var infoResults = validationResults.Where(r => r.severity == ValidationSeverity.Info).ToList();
        
        if (errorResults.Count > 0)
        {
            report += "## Errors\n";
            foreach (var result in errorResults)
            {
                report += $"- [{result.category}] {result.message}\n";
            }
            report += "\n";
        }
        
        if (warningResults.Count > 0)
        {
            report += "## Warnings\n";
            foreach (var result in warningResults)
            {
                report += $"- [{result.category}] {result.message}\n";
            }
            report += "\n";
        }
        
        if (infoResults.Count > 0)
        {
            report += "## Information\n";
            foreach (var result in infoResults)
            {
                report += $"- [{result.category}] {result.message}\n";
            }
        }
        
        File.WriteAllText("validation_report.md", report);
        Debug.Log("Validation report exported to validation_report.md");
    }
    
    public List<ValidationResult> GetValidationResults()
    {
        return validationResults ?? new List<ValidationResult>();
    }
    
    public bool HasErrors()
    {
        return validationResults != null && validationResults.Any(r => r.severity == ValidationSeverity.Error);
    }
    
    public bool HasWarnings()
    {
        return validationResults != null && validationResults.Any(r => r.severity == ValidationSeverity.Warning);
    }
}

[System.Serializable]
public class ValidationResult
{
    public string category;
    public string message;
    public ValidationSeverity severity;
    public System.DateTime timestamp;
}

public enum ValidationSeverity
{
    Info,
    Warning,
    Error
}

// Data integrity checker for specific game systems
public class SaveDataIntegrityChecker
{
    public static bool ValidateSaveData(string saveData)
    {
        try
        {
            if (string.IsNullOrEmpty(saveData))
                return false;
            
            // Basic JSON structure validation
            if (!saveData.StartsWith("{") || !saveData.EndsWith("}"))
                return false;
            
            // Try to parse as GameSaveData
            GameSaveData data = JsonUtility.FromJson<GameSaveData>(saveData);
            
            // Validate data ranges
            if (data.playerLevel < 1 || data.playerLevel > 999)
                return false;
            
            if (data.playerExperience < 0)
                return false;
            
            if (data.currency < 0)
                return false;
            
            // Validate timestamp
            if (string.IsNullOrEmpty(data.lastSaved))
                return false;
            
            return true;
        }
        catch
        {
            return false;
        }
    }
    
    public static string RepairSaveData(string corruptedSaveData)
    {
        try
        {
            GameSaveData data = JsonUtility.FromJson<GameSaveData>(corruptedSaveData);
            
            // Repair invalid values
            data.playerLevel = Mathf.Clamp(data.playerLevel, 1, 999);
            data.playerExperience = Mathf.Max(0, data.playerExperience);
            data.currency = Mathf.Max(0, data.currency);
            
            if (string.IsNullOrEmpty(data.lastSaved))
            {
                data.lastSaved = System.DateTime.Now.ToString();
            }
            
            return JsonUtility.ToJson(data, true);
        }
        catch
        {
            // Return default save data if repair fails
            return JsonUtility.ToJson(new GameSaveData(), true);
        }
    }
}
```

## 🚀 AI/LLM Integration
- Automatically detect data corruption patterns
- Generate validation rules from data schemas
- Create repair strategies for common issues

## 💡 Key Benefits
- Comprehensive data validation
- Automatic corruption detection
- Detailed validation reporting