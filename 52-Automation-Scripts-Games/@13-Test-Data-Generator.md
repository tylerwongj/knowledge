# @13-Test-Data-Generator

## 🎯 Core Concept
Automated test data generation for game testing, debugging, and quality assurance workflows.

## 🔧 Implementation

### Test Data Factory
```csharp
using UnityEngine;
using System.Collections.Generic;

public class TestDataGenerator : MonoBehaviour
{
    [Header("Player Test Data")]
    public int playerCount = 10;
    public int minLevel = 1;
    public int maxLevel = 50;
    
    [Header("Item Test Data")]
    public int itemCount = 100;
    public string[] itemTypes = {"Weapon", "Armor", "Potion", "Accessory"};
    
    [ContextMenu("Generate Test Players")]
    public void GenerateTestPlayers()
    {
        List<TestPlayer> players = new List<TestPlayer>();
        
        for (int i = 0; i < playerCount; i++)
        {
            TestPlayer player = new TestPlayer
            {
                playerId = System.Guid.NewGuid().ToString(),
                playerName = GenerateRandomName(),
                level = Random.Range(minLevel, maxLevel + 1),
                experience = Random.Range(0, 10000),
                health = Random.Range(50, 200),
                mana = Random.Range(30, 150),
                gold = Random.Range(0, 5000)
            };
            
            players.Add(player);
        }
        
        SaveTestData("test_players.json", players);
        Debug.Log($"Generated {playerCount} test players");
    }
    
    [ContextMenu("Generate Test Items")]
    public void GenerateTestItems()
    {
        List<TestItem> items = new List<TestItem>();
        
        for (int i = 0; i < itemCount; i++)
        {
            TestItem item = new TestItem
            {
                itemId = System.Guid.NewGuid().ToString(),
                itemName = GenerateRandomItemName(),
                itemType = itemTypes[Random.Range(0, itemTypes.Length)],
                rarity = (ItemRarity)Random.Range(0, 5),
                value = Random.Range(10, 1000),
                level = Random.Range(1, 30)
            };
            
            items.Add(item);
        }
        
        SaveTestData("test_items.json", items);
        Debug.Log($"Generated {itemCount} test items");
    }
    
    string GenerateRandomName()
    {
        string[] firstNames = {"Alex", "Jordan", "Casey", "Morgan", "Riley", "Avery", "Quinn", "Sage"};
        string[] lastNames = {"Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"};
        
        return $"{firstNames[Random.Range(0, firstNames.Length)]} {lastNames[Random.Range(0, lastNames.Length)]}";
    }
    
    string GenerateRandomItemName()
    {
        string[] adjectives = {"Sharp", "Ancient", "Mystic", "Blessed", "Cursed", "Legendary", "Epic", "Rare"};
        string[] nouns = {"Sword", "Shield", "Bow", "Staff", "Ring", "Amulet", "Potion", "Scroll"};
        
        return $"{adjectives[Random.Range(0, adjectives.Length)]} {nouns[Random.Range(0, nouns.Length)]}";
    }
    
    void SaveTestData<T>(string filename, List<T> data)
    {
        string json = JsonUtility.ToJson(new SerializableList<T>(data), true);
        System.IO.File.WriteAllText(filename, json);
    }
}

[System.Serializable]
public class TestPlayer
{
    public string playerId;
    public string playerName;
    public int level;
    public int experience;
    public int health;
    public int mana;
    public int gold;
}

[System.Serializable]
public class TestItem
{
    public string itemId;
    public string itemName;
    public string itemType;
    public ItemRarity rarity;
    public int value;
    public int level;
}

[System.Serializable]
public class SerializableList<T>
{
    public List<T> items;
    public SerializableList(List<T> items) { this.items = items; }
}
```

## 🚀 AI/LLM Integration
- Generate realistic test scenarios automatically
- Create balanced game data for testing
- Generate edge case test data for stress testing

## 💡 Key Benefits
- Automated test data creation
- Consistent testing environments
- Reduced manual test setup time