# @30-Quest-System-Generator

## 🎯 Core Concept
Automated quest system with objectives, progress tracking, and reward management.

## 🔧 Implementation

### Quest Framework
```csharp
using UnityEngine;
using System.Collections.Generic;

[CreateAssetMenu(fileName = "New Quest", menuName = "Quest/Quest Data")]
public class QuestData : ScriptableObject
{
    public string questId;
    public string questName;
    public string description;
    public QuestType questType;
    public QuestObjective[] objectives;
    public QuestReward[] rewards;
    public string[] prerequisites;
    public bool isRepeatable;
    public int experienceReward;
}

public enum QuestType
{
    Main,
    Side,
    Daily,
    Collection,
    Kill,
    Delivery
}

[System.Serializable]
public class QuestObjective
{
    public string objectiveId;
    public string description;
    public ObjectiveType type;
    public string targetId;
    public int requiredAmount;
    public int currentAmount;
    public bool isCompleted;
}

public enum ObjectiveType
{
    Kill,
    Collect,
    Interact,
    Reach,
    Survive,
    Escort
}

[System.Serializable]
public class QuestReward
{
    public RewardType type;
    public string itemId;
    public int amount;
}

public enum RewardType
{
    Experience,
    Currency,
    Item,
    Unlock
}

public class QuestManager : MonoBehaviour
{
    public static QuestManager Instance;
    
    [Header("Quest Settings")]
    public QuestData[] allQuests;
    
    private List<Quest> activeQuests;
    private List<Quest> completedQuests;
    private Dictionary<string, QuestData> questDatabase;
    
    public System.Action<Quest> OnQuestStarted;
    public System.Action<Quest> OnQuestCompleted;
    public System.Action<Quest, QuestObjective> OnObjectiveCompleted;
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeQuests();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void InitializeQuests()
    {
        activeQuests = new List<Quest>();
        completedQuests = new List<Quest>();
        questDatabase = new Dictionary<string, QuestData>();
        
        foreach (var questData in allQuests)
        {
            questDatabase[questData.questId] = questData;
        }
        
        LoadQuestProgress();
    }
    
    public bool StartQuest(string questId)
    {
        if (!questDatabase.ContainsKey(questId)) return false;
        
        QuestData questData = questDatabase[questId];
        
        // Check prerequisites
        if (!CheckPrerequisites(questData.prerequisites)) return false;
        
        // Check if already active or completed
        if (IsQuestActive(questId) || (!questData.isRepeatable && IsQuestCompleted(questId)))
        {
            return false;
        }
        
        Quest newQuest = new Quest(questData);
        activeQuests.Add(newQuest);
        
        OnQuestStarted?.Invoke(newQuest);
        SaveQuestProgress();
        
        Debug.Log($"Quest started: {questData.questName}");
        return true;
    }
    
    public void UpdateObjective(string questId, string objectiveId, int amount = 1)
    {
        Quest quest = GetActiveQuest(questId);
        if (quest == null) return;
        
        QuestObjective objective = quest.GetObjective(objectiveId);
        if (objective == null || objective.isCompleted) return;
        
        objective.currentAmount = Mathf.Min(objective.currentAmount + amount, objective.requiredAmount);
        
        if (objective.currentAmount >= objective.requiredAmount)
        {
            objective.isCompleted = true;
            OnObjectiveCompleted?.Invoke(quest, objective);
            
            Debug.Log($"Objective completed: {objective.description}");
            
            // Check if quest is complete
            if (quest.IsCompleted())
            {
                CompleteQuest(quest);
            }
        }
        
        SaveQuestProgress();
    }
    
    public void UpdateObjectiveByType(ObjectiveType type, string targetId, int amount = 1)
    {
        foreach (var quest in activeQuests)
        {
            foreach (var objective in quest.objectives)
            {
                if (objective.type == type && objective.targetId == targetId && !objective.isCompleted)
                {
                    UpdateObjective(quest.questData.questId, objective.objectiveId, amount);
                }
            }
        }
    }
    
    void CompleteQuest(Quest quest)
    {
        activeQuests.Remove(quest);
        completedQuests.Add(quest);
        
        // Give rewards
        GiveRewards(quest.questData.rewards);
        
        // Give experience
        if (quest.questData.experienceReward > 0)
        {
            // Add experience to player
            Debug.Log($"Gained {quest.questData.experienceReward} experience");
        }
        
        OnQuestCompleted?.Invoke(quest);
        SaveQuestProgress();
        
        Debug.Log($"Quest completed: {quest.questData.questName}");
    }
    
    void GiveRewards(QuestReward[] rewards)
    {
        foreach (var reward in rewards)
        {
            switch (reward.type)
            {
                case RewardType.Currency:
                    AddCurrency(reward.amount);
                    break;
                case RewardType.Item:
                    GiveItem(reward.itemId, reward.amount);
                    break;
                case RewardType.Experience:
                    AddExperience(reward.amount);
                    break;
                case RewardType.Unlock:
                    UnlockContent(reward.itemId);
                    break;
            }
        }
    }
    
    void AddCurrency(int amount)
    {
        int currentCurrency = PlayerPrefs.GetInt("Currency", 0);
        PlayerPrefs.SetInt("Currency", currentCurrency + amount);
        Debug.Log($"Gained {amount} currency");
    }
    
    void GiveItem(string itemId, int amount)
    {
        // Integrate with inventory system
        Debug.Log($"Received {amount}x {itemId}");
    }
    
    void AddExperience(int amount)
    {
        // Integrate with player level system
        Debug.Log($"Gained {amount} experience");
    }
    
    void UnlockContent(string contentId)
    {
        PlayerPrefs.SetInt($"Unlocked_{contentId}", 1);
        Debug.Log($"Unlocked: {contentId}");
    }
    
    bool CheckPrerequisites(string[] prerequisites)
    {
        if (prerequisites == null || prerequisites.Length == 0) return true;
        
        foreach (string prerequisiteId in prerequisites)
        {
            if (!IsQuestCompleted(prerequisiteId))
                return false;
        }
        
        return true;
    }
    
    public Quest GetActiveQuest(string questId)
    {
        return activeQuests.Find(q => q.questData.questId == questId);
    }
    
    public bool IsQuestActive(string questId)
    {
        return GetActiveQuest(questId) != null;
    }
    
    public bool IsQuestCompleted(string questId)
    {
        return completedQuests.Exists(q => q.questData.questId == questId);
    }
    
    public List<Quest> GetActiveQuests() => new List<Quest>(activeQuests);
    public List<Quest> GetCompletedQuests() => new List<Quest>(completedQuests);
    
    void SaveQuestProgress()
    {
        QuestSaveData saveData = new QuestSaveData
        {
            activeQuests = new List<QuestProgress>(),
            completedQuests = new List<string>()
        };
        
        foreach (var quest in activeQuests)
        {
            saveData.activeQuests.Add(quest.GetSaveData());
        }
        
        foreach (var quest in completedQuests)
        {
            saveData.completedQuests.Add(quest.questData.questId);
        }
        
        string json = JsonUtility.ToJson(saveData);
        PlayerPrefs.SetString("QuestData", json);
        PlayerPrefs.Save();
    }
    
    void LoadQuestProgress()
    {
        string json = PlayerPrefs.GetString("QuestData", "");
        if (string.IsNullOrEmpty(json)) return;
        
        QuestSaveData saveData = JsonUtility.FromJson<QuestSaveData>(json);
        
        // Load active quests
        foreach (var questProgress in saveData.activeQuests)
        {
            if (questDatabase.ContainsKey(questProgress.questId))
            {
                Quest quest = new Quest(questDatabase[questProgress.questId]);
                quest.LoadProgress(questProgress);
                activeQuests.Add(quest);
            }
        }
        
        // Load completed quests
        foreach (string questId in saveData.completedQuests)
        {
            if (questDatabase.ContainsKey(questId))
            {
                Quest quest = new Quest(questDatabase[questId]);
                quest.MarkAsCompleted();
                completedQuests.Add(quest);
            }
        }
    }
}

public class Quest
{
    public QuestData questData;
    public QuestObjective[] objectives;
    public System.DateTime startTime;
    
    public Quest(QuestData data)
    {
        questData = data;
        objectives = new QuestObjective[data.objectives.Length];
        for (int i = 0; i < data.objectives.Length; i++)
        {
            objectives[i] = new QuestObjective
            {
                objectiveId = data.objectives[i].objectiveId,
                description = data.objectives[i].description,
                type = data.objectives[i].type,
                targetId = data.objectives[i].targetId,
                requiredAmount = data.objectives[i].requiredAmount,
                currentAmount = 0,
                isCompleted = false
            };
        }
        startTime = System.DateTime.Now;
    }
    
    public bool IsCompleted()
    {
        foreach (var objective in objectives)
        {
            if (!objective.isCompleted)
                return false;
        }
        return true;
    }
    
    public QuestObjective GetObjective(string objectiveId)
    {
        return System.Array.Find(objectives, obj => obj.objectiveId == objectiveId);
    }
    
    public void MarkAsCompleted()
    {
        foreach (var objective in objectives)
        {
            objective.isCompleted = true;
            objective.currentAmount = objective.requiredAmount;
        }
    }
    
    public QuestProgress GetSaveData()
    {
        return new QuestProgress
        {
            questId = questData.questId,
            objectives = objectives,
            startTime = startTime.ToBinary()
        };
    }
    
    public void LoadProgress(QuestProgress progress)
    {
        objectives = progress.objectives;
        startTime = System.DateTime.FromBinary(progress.startTime);
    }
}

[System.Serializable]
public class QuestSaveData
{
    public List<QuestProgress> activeQuests;
    public List<string> completedQuests;
}

[System.Serializable]
public class QuestProgress
{
    public string questId;
    public QuestObjective[] objectives;
    public long startTime;
}
```

## 🚀 AI/LLM Integration
- Generate quest content from game themes
- Create balanced reward structures
- Automatically link quest dependencies

## 💡 Key Benefits
- Complete quest management system
- Automatic progress tracking
- Flexible objective types