# @08-Scriptable-Object-Factory

## 🎯 Core Concept
Automated ScriptableObject creation and data management systems for organized game data architecture.

## 🔧 Implementation

### ScriptableObject Generator
```csharp
using UnityEngine;
using UnityEditor;
using System.IO;

public class ScriptableObjectFactory
{
    [MenuItem("Game Tools/Create Item Database")]
    public static void CreateItemDatabase()
    {
        string[] itemNames = { "Sword", "Shield", "Potion", "Bow", "Armor", "Ring" };
        string[] itemTypes = { "Weapon", "Defense", "Consumable", "Weapon", "Defense", "Accessory" };
        
        for (int i = 0; i < itemNames.Length; i++)
        {
            GameItem item = ScriptableObject.CreateInstance<GameItem>();
            item.itemName = itemNames[i];
            item.itemType = itemTypes[i];
            item.value = Random.Range(10, 100);
            item.rarity = (ItemRarity)Random.Range(0, 4);
            
            string path = $"Assets/Data/Items/{itemNames[i]}.asset";
            AssetDatabase.CreateAsset(item, path);
        }
        
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
    }
    
    [MenuItem("Game Tools/Create Enemy Database")]
    public static void CreateEnemyDatabase()
    {
        string[] enemyNames = { "Goblin", "Orc", "Dragon", "Skeleton", "Troll" };
        
        foreach (string enemyName in enemyNames)
        {
            EnemyData enemy = ScriptableObject.CreateInstance<EnemyData>();
            enemy.enemyName = enemyName;
            enemy.health = Random.Range(50, 200);
            enemy.damage = Random.Range(10, 50);
            enemy.speed = Random.Range(1f, 5f);
            
            string path = $"Assets/Data/Enemies/{enemyName}.asset";
            AssetDatabase.CreateAsset(enemy, path);
        }
        
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
    }
}

// Example ScriptableObject classes
[CreateAssetMenu(fileName = "New Item", menuName = "Game/Item")]
public class GameItem : ScriptableObject
{
    public string itemName;
    public string itemType;
    public int value;
    public ItemRarity rarity;
    public Sprite icon;
    public string description;
}

[CreateAssetMenu(fileName = "New Enemy", menuName = "Game/Enemy")]
public class EnemyData : ScriptableObject
{
    public string enemyName;
    public int health;
    public int damage;
    public float speed;
    public GameObject prefab;
    public AudioClip attackSound;
}

public enum ItemRarity
{
    Common,
    Uncommon,
    Rare,
    Epic,
    Legendary
}
```

### Data Validator
```csharp
[MenuItem("Game Tools/Validate Game Data")]
public static void ValidateGameData()
{
    string[] itemGuids = AssetDatabase.FindAssets("t:GameItem");
    string[] enemyGuids = AssetDatabase.FindAssets("t:EnemyData");
    
    Debug.Log($"Found {itemGuids.Length} items and {enemyGuids.Length} enemies");
    
    foreach (string guid in itemGuids)
    {
        string path = AssetDatabase.GUIDToAssetPath(guid);
        GameItem item = AssetDatabase.LoadAssetAtPath<GameItem>(path);
        
        if (string.IsNullOrEmpty(item.itemName))
        {
            Debug.LogWarning($"Item at {path} has no name!");
        }
        
        if (item.value <= 0)
        {
            Debug.LogWarning($"Item {item.itemName} has invalid value: {item.value}");
        }
    }
}
```

## 🚀 AI/LLM Integration
- Generate balanced item stats automatically
- Create thematic item collections
- Validate data consistency across objects

## 💡 Key Benefits
- Organized game data architecture
- Batch creation of game assets
- Automated data validation