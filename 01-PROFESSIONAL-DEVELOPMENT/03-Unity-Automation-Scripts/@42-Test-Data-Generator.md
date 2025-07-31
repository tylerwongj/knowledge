# @42-Test-Data-Generator

## 🎯 Core Concept
Automated test data generation system for creating realistic game content, player data, and testing scenarios.

## 🔧 Implementation

### Test Data Generator Framework
```csharp
using UnityEngine;
using System.Collections.Generic;
using System.Linq;
using System.IO;

public class TestDataGenerator : MonoBehaviour
{
    [Header("Generation Settings")]
    public int numberOfPlayers = 100;
    public int numberOfItems = 50;
    public int numberOfQuests = 25;
    public bool generateOnStart = false;
    public bool exportToJSON = true;
    
    [Header("Data Ranges")]
    public Vector2Int levelRange = new Vector2Int(1, 50);
    public Vector2Int currencyRange = new Vector2Int(0, 10000);
    public Vector2Int experienceRange = new Vector2Int(0, 100000);
    
    private TestDataConfig config;
    private System.Random random;
    
    void Start()
    {
        if (generateOnStart)
        {
            GenerateAllTestData();
        }
    }
    
    [ContextMenu("Generate All Test Data")]
    public void GenerateAllTestData()
    {
        InitializeGenerator();
        
        Debug.Log("Generating test data...");
        
        // Generate different types of test data
        List<PlayerData> players = GeneratePlayerData(numberOfPlayers);
        List<ItemData> items = GenerateItemData(numberOfItems);
        List<QuestData> quests = GenerateQuestData(numberOfQuests);
        List<GameSessionData> sessions = GenerateSessionData(50);
        
        // Export data if enabled
        if (exportToJSON)
        {
            ExportTestData(players, items, quests, sessions);
        }
        
        Debug.Log($"Generated {players.Count} players, {items.Count} items, {quests.Count} quests, {sessions.Count} sessions");
    }
    
    void InitializeGenerator()
    {
        random = new System.Random();
        config = Resources.Load<TestDataConfig>("TestDataConfig");
        
        if (config == null)
        {
            config = CreateDefaultConfig();
        }
    }
    
    TestDataConfig CreateDefaultConfig()
    {
        TestDataConfig defaultConfig = ScriptableObject.CreateInstance<TestDataConfig>();
        
        defaultConfig.playerNames = new string[]
        {
            "Alex", "Blake", "Casey", "Drew", "Emery", "Finley", "Gray", "Harper",
            "Indigo", "Jordan", "Kai", "Logan", "Morgan", "Noel", "Ocean", "Parker",
            "Quinn", "River", "Sage", "Taylor", "Unity", "Vale", "Wren", "Zion"
        };
        
        defaultConfig.itemNames = new string[]
        {
            "Sword", "Shield", "Potion", "Bow", "Staff", "Ring", "Amulet", "Boots",
            "Helmet", "Armor", "Dagger", "Axe", "Wand", "Scroll", "Gem", "Key"
        };
        
        defaultConfig.questTitles = new string[]
        {
            "Rescue the Village", "Find the Lost Artifact", "Defeat the Dragon",
            "Collect Ancient Runes", "Explore the Dungeon", "Deliver the Message",
            "Hunt the Beast", "Solve the Mystery", "Gather Resources", "Protect the Caravan"
        };
        
        defaultConfig.locationNames = new string[]
        {
            "Forest of Whispers", "Crystal Caves", "Ancient Ruins", "Mystic Lake",
            "Shadow Valley", "Golden Plains", "Ice Mountains", "Desert Oasis",
            "Haunted Manor", "Sky Temple", "Underground City", "Volcanic Peak"
        };
        
        return defaultConfig;
    }
    
    List<PlayerData> GeneratePlayerData(int count)
    {
        List<PlayerData> players = new List<PlayerData>();
        
        for (int i = 0; i < count; i++)
        {
            PlayerData player = new PlayerData
            {
                playerId = System.Guid.NewGuid().ToString(),
                playerName = GeneratePlayerName(),
                level = random.Next(levelRange.x, levelRange.y + 1),
                experience = random.Next(experienceRange.x, experienceRange.y + 1),
                currency = random.Next(currencyRange.x, currencyRange.y + 1),
                health = random.Next(50, 201),
                mana = random.Next(20, 101),
                strength = random.Next(10, 101),
                intelligence = random.Next(10, 101),
                agility = random.Next(10, 101),
                inventory = GenerateInventory(),
                achievements = GenerateAchievements(),
                playTime = random.Next(60, 50000), // 1 minute to ~14 hours
                lastLogin = GenerateRandomDate(),
                characterClass = GetRandomCharacterClass(),
                location = GetRandomLocation()
            };
            
            players.Add(player);
        }
        
        return players;
    }
    
    List<ItemData> GenerateItemData(int count)
    {
        List<ItemData> items = new List<ItemData>();
        
        for (int i = 0; i < count; i++)
        {
            ItemData item = new ItemData
            {
                itemId = System.Guid.NewGuid().ToString(),
                itemName = GenerateItemName(),
                itemType = GetRandomItemType(),
                rarity = GetRandomRarity(),
                level = random.Next(1, 51),
                value = random.Next(10, 1000),
                damage = GetRandomItemType() == ItemType.Weapon ? random.Next(5, 100) : 0,
                defense = GetRandomItemType() == ItemType.Armor ? random.Next(5, 50) : 0,
                description = GenerateItemDescription(),
                effects = GenerateItemEffects(),
                durability = random.Next(50, 101),
                weight = (float)random.NextDouble() * 10f + 0.1f
            };
            
            items.Add(item);
        }
        
        return items;
    }
    
    List<QuestData> GenerateQuestData(int count)
    {
        List<QuestData> quests = new List<QuestData>();
        
        for (int i = 0; i < count; i++)
        {
            QuestData quest = new QuestData
            {
                questId = System.Guid.NewGuid().ToString(),
                title = GenerateQuestTitle(),
                description = GenerateQuestDescription(),
                questType = GetRandomQuestType(),
                difficulty = GetRandomDifficulty(),
                requiredLevel = random.Next(1, 26),
                experienceReward = random.Next(100, 2000),
                currencyReward = random.Next(50, 500),
                itemRewards = GenerateQuestRewards(),
                objectives = GenerateQuestObjectives(),
                location = GetRandomLocation(),
                timeLimit = random.NextDouble() < 0.3 ? random.Next(300, 3600) : -1, // 30% have time limits
                isRepeatable = random.NextDouble() < 0.2 // 20% are repeatable
            };
            
            quests.Add(quest);
        }
        
        return quests;
    }
    
    List<GameSessionData> GenerateSessionData(int count)
    {
        List<GameSessionData> sessions = new List<GameSessionData>();
        
        for (int i = 0; i < count; i++)
        {
            GameSessionData session = new GameSessionData
            {
                sessionId = System.Guid.NewGuid().ToString(),
                playerId = System.Guid.NewGuid().ToString(),
                startTime = GenerateRandomDate(),
                duration = random.Next(300, 7200), // 5 minutes to 2 hours
                actionsPerformed = random.Next(10, 500),
                itemsCollected = random.Next(0, 20),
                enemiesDefeated = random.Next(0, 50),
                experienceGained = random.Next(50, 1000),
                currencyEarned = random.Next(20, 200),
                levelsGained = random.Next(0, 3),
                deathCount = random.Next(0, 5),
                questsCompleted = random.Next(0, 5),
                platformUsed = GetRandomPlatform(),
                deviceInfo = GenerateDeviceInfo()
            };
            
            sessions.Add(session);
        }
        
        return sessions;
    }
    
    string GeneratePlayerName()
    {
        if (config.playerNames.Length == 0) return "Player" + random.Next(1000, 9999);
        
        string baseName = config.playerNames[random.Next(config.playerNames.Length)];
        
        // Add random suffix sometimes
        if (random.NextDouble() < 0.3)
        {
            baseName += random.Next(10, 100).ToString();
        }
        
        return baseName;
    }
    
    string GenerateItemName()
    {
        if (config.itemNames.Length == 0) return "Item" + random.Next(1000, 9999);
        
        string baseName = config.itemNames[random.Next(config.itemNames.Length)];
        
        // Add quality prefix sometimes
        if (random.NextDouble() < 0.4)
        {
            string[] qualities = { "Ancient", "Mystical", "Enchanted", "Legendary", "Rare", "Fine", "Crude" };
            baseName = qualities[random.Next(qualities.Length)] + " " + baseName;
        }
        
        return baseName;
    }
    
    string GenerateQuestTitle()
    {
        if (config.questTitles.Length == 0) return "Quest " + random.Next(1000, 9999);
        
        return config.questTitles[random.Next(config.questTitles.Length)];
    }
    
    string GenerateItemDescription()
    {
        string[] adjectives = { "powerful", "ancient", "mystical", "enchanted", "cursed", "blessed", "rare", "common" };
        string[] materials = { "steel", "iron", "silver", "gold", "crystal", "obsidian", "wood", "leather" };
        
        string adjective = adjectives[random.Next(adjectives.Length)];
        string material = materials[random.Next(materials.Length)];
        
        return $"A {adjective} item crafted from {material}. Provides various benefits to the wielder.";
    }
    
    string GenerateQuestDescription()
    {
        string[] actions = { "Find", "Defeat", "Collect", "Deliver", "Rescue", "Explore", "Protect", "Investigate" };
        string[] targets = { "the ancient artifact", "the missing villager", "10 rare gems", "the secret message", 
                           "the lost treasure", "the hidden temple", "the merchant caravan", "the mysterious phenomenon" };
        
        string action = actions[random.Next(actions.Length)];
        string target = targets[random.Next(targets.Length)];
        
        return $"{action} {target} and return to the quest giver for your reward.";
    }
    
    List<string> GenerateInventory()
    {
        List<string> inventory = new List<string>();
        int itemCount = random.Next(5, 21);
        
        for (int i = 0; i < itemCount; i++)
        {
            inventory.Add(GenerateItemName());
        }
        
        return inventory;
    }
    
    List<string> GenerateAchievements()
    {
        string[] possibleAchievements = {
            "First Steps", "Level Up", "Item Collector", "Quest Master", "Explorer",
            "Dragon Slayer", "Treasure Hunter", "Social Butterfly", "Speedrunner", "Perfectionist"
        };
        
        List<string> achievements = new List<string>();
        int achievementCount = random.Next(0, 8);
        
        for (int i = 0; i < achievementCount; i++)
        {
            string achievement = possibleAchievements[random.Next(possibleAchievements.Length)];
            if (!achievements.Contains(achievement))
            {
                achievements.Add(achievement);
            }
        }
        
        return achievements;
    }
    
    List<string> GenerateItemEffects()
    {
        string[] effects = { "+10 Strength", "+5 Intelligence", "+15 Health", "+8 Mana", 
                           "Fire Resistance", "Ice Damage", "Lightning Speed", "Poison Immunity" };
        
        List<string> itemEffects = new List<string>();
        int effectCount = random.Next(0, 4);
        
        for (int i = 0; i < effectCount; i++)
        {
            string effect = effects[random.Next(effects.Length)];
            if (!itemEffects.Contains(effect))
            {
                itemEffects.Add(effect);
            }
        }
        
        return itemEffects;
    }
    
    List<string> GenerateQuestObjectives()
    {
        string[] objectives = {
            "Kill 5 wolves", "Collect 10 herbs", "Talk to the village elder", "Find the hidden chest",
            "Defeat the boss enemy", "Reach the mountain peak", "Solve the ancient puzzle", "Gather information"
        };
        
        List<string> questObjectives = new List<string>();
        int objectiveCount = random.Next(1, 4);
        
        for (int i = 0; i < objectiveCount; i++)
        {
            questObjectives.Add(objectives[random.Next(objectives.Length)]);
        }
        
        return questObjectives;
    }
    
    List<string> GenerateQuestRewards()
    {
        List<string> rewards = new List<string>();
        int rewardCount = random.Next(1, 4);
        
        for (int i = 0; i < rewardCount; i++)
        {
            rewards.Add(GenerateItemName());
        }
        
        return rewards;
    }
    
    string GenerateRandomDate()
    {
        System.DateTime start = System.DateTime.Now.AddDays(-365);
        int range = (System.DateTime.Now - start).Days;
        return start.AddDays(random.Next(range)).ToString("yyyy-MM-dd HH:mm:ss");
    }
    
    string GetRandomCharacterClass()
    {
        string[] classes = { "Warrior", "Mage", "Archer", "Rogue", "Paladin", "Necromancer", "Druid", "Bard" };
        return classes[random.Next(classes.Length)];
    }
    
    string GetRandomLocation()
    {
        if (config.locationNames.Length == 0)
        {
            string[] defaultLocations = { "Starting Village", "Dark Forest", "Ancient Temple", "Mountain Pass" };
            return defaultLocations[random.Next(defaultLocations.Length)];
        }
        
        return config.locationNames[random.Next(config.locationNames.Length)];
    }
    
    ItemType GetRandomItemType()
    {
        return (ItemType)random.Next(System.Enum.GetValues(typeof(ItemType)).Length);
    }
    
    Rarity GetRandomRarity()
    {
        // Weighted rarity distribution
        float roll = (float)random.NextDouble();
        if (roll < 0.5f) return Rarity.Common;
        if (roll < 0.8f) return Rarity.Uncommon;
        if (roll < 0.95f) return Rarity.Rare;
        if (roll < 0.99f) return Rarity.Epic;
        return Rarity.Legendary;
    }
    
    QuestType GetRandomQuestType()
    {
        return (QuestType)random.Next(System.Enum.GetValues(typeof(QuestType)).Length);
    }
    
    Difficulty GetRandomDifficulty()
    {
        return (Difficulty)random.Next(System.Enum.GetValues(typeof(Difficulty)).Length);
    }
    
    string GetRandomPlatform()
    {
        string[] platforms = { "PC", "PlayStation", "Xbox", "Nintendo Switch", "Mobile", "VR" };
        return platforms[random.Next(platforms.Length)];
    }
    
    string GenerateDeviceInfo()
    {
        string[] devices = {
            "Windows 10 - Intel i7", "PlayStation 5", "Xbox Series X", "iPhone 13", 
            "Samsung Galaxy S21", "Nintendo Switch", "Meta Quest 2", "Steam Deck"
        };
        return devices[random.Next(devices.Length)];
    }
    
    void ExportTestData(List<PlayerData> players, List<ItemData> items, 
                       List<QuestData> quests, List<GameSessionData> sessions)
    {
        TestDataExport export = new TestDataExport
        {
            generatedAt = System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"),
            playerCount = players.Count,
            itemCount = items.Count,
            questCount = quests.Count,
            sessionCount = sessions.Count,
            players = players,
            items = items,
            quests = quests,
            sessions = sessions
        };
        
        string json = JsonUtility.ToJson(export, true);
        string fileName = $"test_data_{System.DateTime.Now:yyyyMMdd_HHmmss}.json";
        
        File.WriteAllText(fileName, json);
        Debug.Log($"Test data exported to {fileName}");
        
        // Also export individual categories
        ExportPlayerDataCSV(players);
        ExportItemDataCSV(items);
        ExportQuestDataCSV(quests);
    }
    
    void ExportPlayerDataCSV(List<PlayerData> players)
    {
        System.Text.StringBuilder csv = new System.Text.StringBuilder();
        csv.AppendLine("PlayerId,PlayerName,Level,Experience,Currency,Health,Mana,Strength,Intelligence,Agility,CharacterClass,Location,PlayTime,LastLogin");
        
        foreach (var player in players)
        {
            csv.AppendLine($"{player.playerId},{player.playerName},{player.level},{player.experience}," +
                          $"{player.currency},{player.health},{player.mana},{player.strength}," +
                          $"{player.intelligence},{player.agility},{player.characterClass}," +
                          $"{player.location},{player.playTime},{player.lastLogin}");
        }
        
        File.WriteAllText("test_players.csv", csv.ToString());
    }
    
    void ExportItemDataCSV(List<ItemData> items)
    {
        System.Text.StringBuilder csv = new System.Text.StringBuilder();
        csv.AppendLine("ItemId,ItemName,ItemType,Rarity,Level,Value,Damage,Defense,Durability,Weight");
        
        foreach (var item in items)
        {
            csv.AppendLine($"{item.itemId},{item.itemName},{item.itemType},{item.rarity}," +
                          $"{item.level},{item.value},{item.damage},{item.defense}," +
                          $"{item.durability},{item.weight:F2}");
        }
        
        File.WriteAllText("test_items.csv", csv.ToString());
    }
    
    void ExportQuestDataCSV(List<QuestData> quests)
    {
        System.Text.StringBuilder csv = new System.Text.StringBuilder();
        csv.AppendLine("QuestId,Title,QuestType,Difficulty,RequiredLevel,ExperienceReward,CurrencyReward,Location,TimeLimit,IsRepeatable");
        
        foreach (var quest in quests)
        {
            csv.AppendLine($"{quest.questId},{quest.title},{quest.questType},{quest.difficulty}," +
                          $"{quest.requiredLevel},{quest.experienceReward},{quest.currencyReward}," +
                          $"{quest.location},{quest.timeLimit},{quest.isRepeatable}");
        }
        
        File.WriteAllText("test_quests.csv", csv.ToString());
    }
}

// Enums for data generation
public enum ItemType { Weapon, Armor, Consumable, Tool, Accessory, Material }
public enum Rarity { Common, Uncommon, Rare, Epic, Legendary }
public enum QuestType { Kill, Collect, Deliver, Escort, Explore, Talk }
public enum Difficulty { Easy, Normal, Hard, Expert, Legendary }

// Data structures
[System.Serializable]
public class PlayerData
{
    public string playerId;
    public string playerName;
    public int level;
    public int experience;
    public int currency;
    public int health;
    public int mana;
    public int strength;
    public int intelligence;
    public int agility;
    public List<string> inventory;
    public List<string> achievements;
    public int playTime;
    public string lastLogin;
    public string characterClass;
    public string location;
}

[System.Serializable]
public class ItemData
{
    public string itemId;
    public string itemName;
    public ItemType itemType;
    public Rarity rarity;
    public int level;
    public int value;
    public int damage;
    public int defense;
    public string description;
    public List<string> effects;
    public int durability;
    public float weight;
}

[System.Serializable]
public class QuestData
{
    public string questId;
    public string title;
    public string description;
    public QuestType questType;
    public Difficulty difficulty;
    public int requiredLevel;
    public int experienceReward;
    public int currencyReward;
    public List<string> itemRewards;
    public List<string> objectives;
    public string location;
    public int timeLimit;
    public bool isRepeatable;
}

[System.Serializable]
public class GameSessionData
{
    public string sessionId;
    public string playerId;
    public string startTime;
    public int duration;
    public int actionsPerformed;
    public int itemsCollected;
    public int enemiesDefeated;
    public int experienceGained;
    public int currencyEarned;
    public int levelsGained;
    public int deathCount;
    public int questsCompleted;
    public string platformUsed;
    public string deviceInfo;
}

[System.Serializable]
public class TestDataExport
{
    public string generatedAt;
    public int playerCount;
    public int itemCount;
    public int questCount;
    public int sessionCount;
    public List<PlayerData> players;
    public List<ItemData> items;
    public List<QuestData> quests;
    public List<GameSessionData> sessions;
}

[CreateAssetMenu(fileName = "TestDataConfig", menuName = "Test Data/Config")]
public class TestDataConfig : ScriptableObject
{
    public string[] playerNames;
    public string[] itemNames;
    public string[] questTitles;
    public string[] locationNames;
}
```

## 🚀 AI/LLM Integration
- Generate realistic player names and game content
- Create balanced item statistics and quest rewards
- Produce diverse test scenarios for comprehensive testing

## 💡 Key Benefits
- Automated test data generation
- Realistic game content creation
- Comprehensive testing scenarios