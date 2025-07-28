# @21-Achievement-System-Builder

## 🎯 Core Concept
Automated achievement system with progress tracking and notification management.

## 🔧 Implementation

### Achievement Framework
```csharp
using UnityEngine;
using System.Collections.Generic;

[CreateAssetMenu(fileName = "New Achievement", menuName = "Game/Achievement")]
public class Achievement : ScriptableObject
{
    public string achievementName;
    public string description;
    public Sprite icon;
    public int pointValue;
    public AchievementType type;
    public int targetValue;
    public bool isSecret;
    public string[] prerequisites;
}

public enum AchievementType
{
    Progress,
    Count,
    Unlock,
    Time,
    Collection
}

public class AchievementManager : MonoBehaviour
{
    public static AchievementManager Instance;
    
    [Header("Achievement Settings")]
    public Achievement[] allAchievements;
    public GameObject achievementNotificationPrefab;
    public Transform notificationParent;
    
    private Dictionary<string, int> achievementProgress;
    private HashSet<string> unlockedAchievements;
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeAchievements();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void InitializeAchievements()
    {
        achievementProgress = new Dictionary<string, int>();
        unlockedAchievements = new HashSet<string>();
        
        foreach (var achievement in allAchievements)
        {
            achievementProgress[achievement.name] = 0;
        }
        
        LoadAchievementData();
    }
    
    public void UpdateProgress(string achievementId, int progress)
    {
        if (achievementProgress.ContainsKey(achievementId) && !IsUnlocked(achievementId))
        {
            achievementProgress[achievementId] = progress;
            CheckAchievementCompletion(achievementId);
        }
    }
    
    public void IncrementProgress(string achievementId, int amount = 1)
    {
        if (achievementProgress.ContainsKey(achievementId) && !IsUnlocked(achievementId))
        {
            achievementProgress[achievementId] += amount;
            CheckAchievementCompletion(achievementId);
        }
    }
    
    void CheckAchievementCompletion(string achievementId)
    {
        Achievement achievement = GetAchievement(achievementId);
        if (achievement != null && achievementProgress[achievementId] >= achievement.targetValue)
        {
            UnlockAchievement(achievementId);
        }
    }
    
    void UnlockAchievement(string achievementId)
    {
        if (!unlockedAchievements.Contains(achievementId))
        {
            unlockedAchievements.Add(achievementId);
            Achievement achievement = GetAchievement(achievementId);
            
            if (achievement != null)
            {
                ShowAchievementNotification(achievement);
                SaveAchievementData();
                
                Debug.Log($"Achievement Unlocked: {achievement.achievementName}");
            }
        }
    }
    
    void ShowAchievementNotification(Achievement achievement)
    {
        if (achievementNotificationPrefab != null && notificationParent != null)
        {
            GameObject notification = Instantiate(achievementNotificationPrefab, notificationParent);
            AchievementNotification notificationScript = notification.GetComponent<AchievementNotification>();
            
            if (notificationScript != null)
            {
                notificationScript.ShowAchievement(achievement);
            }
        }
    }
    
    public bool IsUnlocked(string achievementId)
    {
        return unlockedAchievements.Contains(achievementId);
    }
    
    public int GetProgress(string achievementId)
    {
        return achievementProgress.ContainsKey(achievementId) ? achievementProgress[achievementId] : 0;
    }
    
    Achievement GetAchievement(string achievementId)
    {
        foreach (var achievement in allAchievements)
        {
            if (achievement.name == achievementId)
                return achievement;
        }
        return null;
    }
    
    void SaveAchievementData()
    {
        // Save to PlayerPrefs or custom save system
        foreach (var kvp in achievementProgress)
        {
            PlayerPrefs.SetInt($"Achievement_Progress_{kvp.Key}", kvp.Value);
        }
        
        foreach (var achievement in unlockedAchievements)
        {
            PlayerPrefs.SetInt($"Achievement_Unlocked_{achievement}", 1);
        }
        
        PlayerPrefs.Save();
    }
    
    void LoadAchievementData()
    {
        foreach (var achievement in allAchievements)
        {
            achievementProgress[achievement.name] = PlayerPrefs.GetInt($"Achievement_Progress_{achievement.name}", 0);
            
            if (PlayerPrefs.GetInt($"Achievement_Unlocked_{achievement.name}", 0) == 1)
            {
                unlockedAchievements.Add(achievement.name);
            }
        }
    }
}

public class AchievementNotification : MonoBehaviour
{
    public UnityEngine.UI.Text achievementNameText;
    public UnityEngine.UI.Text descriptionText;
    public UnityEngine.UI.Image iconImage;
    public float displayDuration = 3f;
    
    public void ShowAchievement(Achievement achievement)
    {
        achievementNameText.text = achievement.achievementName;
        descriptionText.text = achievement.description;
        iconImage.sprite = achievement.icon;
        
        Invoke(nameof(HideNotification), displayDuration);
    }
    
    void HideNotification()
    {
        Destroy(gameObject);
    }
}
```

## 🚀 AI/LLM Integration
- Generate achievement ideas based on gameplay
- Create balanced point values automatically
- Generate achievement descriptions and names

## 💡 Key Benefits
- Player engagement and retention
- Automated progress tracking
- Customizable notification system