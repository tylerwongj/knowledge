# @f-Unity-Data-Management-Serialization

## 🎯 Learning Objectives
- Master Unity's serialization system and data persistence
- Implement efficient save/load systems for game data
- Understand ScriptableObjects for data-driven development
- Create flexible data management architectures

## 🔧 Unity Serialization Fundamentals

### Unity Serialization Attributes
```csharp
[System.Serializable]
public class PlayerData
{
    [SerializeField] private string playerName;
    [SerializeField] private int level;
    [SerializeField] private float experience;
    
    [Header("Inventory")]
    [SerializeField] private List<ItemData> inventory = new List<ItemData>();
    
    [Header("Settings")]
    [Range(0f, 1f)]
    [SerializeField] private float masterVolume = 1f;
    
    [HideInInspector]
    [SerializeField] private string hiddenData;
    
    [Space(10)]
    [Tooltip("Player's current position in the world")]
    [SerializeField] private Vector3 worldPosition;
    
    // Properties for controlled access
    public string PlayerName => playerName;
    public int Level => level;
    public float Experience => experience;
    
    public void SetPlayerName(string name) => playerName = name;
    public void AddExperience(float exp) => experience += exp;
}

[System.Serializable]
public class ItemData
{
    public string itemId;
    public string itemName;
    public int quantity;
    public ItemType type;
    
    [TextArea(3, 5)]
    public string description;
}

public enum ItemType
{
    Weapon,
    Armor,
    Consumable,
    Quest
}
```

### ScriptableObject Data Architecture
```csharp
// Base data class
public abstract class GameData : ScriptableObject
{
    [SerializeField] protected string dataId;
    [SerializeField] protected string displayName;
    [TextArea(2, 4)]
    [SerializeField] protected string description;
    
    public string DataId => dataId;
    public string DisplayName => displayName;
    public string Description => description;
    
    protected virtual void OnValidate()
    {
        if (string.IsNullOrEmpty(dataId))
        {
            dataId = name.ToLower().Replace(" ", "_");
        }
    }
}

// Weapon data
[CreateAssetMenu(fileName = "New Weapon", menuName = "Game Data/Weapons/Weapon")]
public class WeaponData : GameData
{
    [Header("Combat Stats")]
    [SerializeField] private float damage = 10f;
    [SerializeField] private float attackSpeed = 1f;
    [SerializeField] private float range = 2f;
    
    [Header("Visual")]
    [SerializeField] private GameObject weaponPrefab;
    [SerializeField] private Sprite weaponIcon;
    [SerializeField] private AudioClip attackSound;
    
    [Header("Requirements")]
    [SerializeField] private int levelRequirement = 1;
    [SerializeField] private List<string> requiredSkills = new List<string>();
    
    public float Damage => damage;
    public float AttackSpeed => attackSpeed;
    public float Range => range;
    public GameObject WeaponPrefab => weaponPrefab;
    public Sprite WeaponIcon => weaponIcon;
}

// Character stats
[CreateAssetMenu(fileName = "New Character Stats", menuName = "Game Data/Characters/Stats")]
public class CharacterStats : GameData
{
    [Header("Base Attributes")]
    [SerializeField] private int strength = 10;
    [SerializeField] private int agility = 10;
    [SerializeField] private int intelligence = 10;
    [SerializeField] private int vitality = 10;
    
    [Header("Derived Stats")]
    [SerializeField] private float baseHealth = 100f;
    [SerializeField] private float baseMana = 50f;
    [SerializeField] private float baseSpeed = 5f;
    
    // Calculated properties
    public float CalculatedHealth => baseHealth + (vitality * 10f);
    public float CalculatedMana => baseMana + (intelligence * 5f);
    public float CalculatedSpeed => baseSpeed + (agility * 0.1f);
    public float CalculatedDamage => strength * 2f;
}
```

### Save/Load System Implementation
```csharp
public class SaveLoadManager : MonoBehaviour
{
    private const string SAVE_FILE_NAME = "gamedata.json";
    private string SavePath => Path.Combine(Application.persistentDataPath, SAVE_FILE_NAME);
    
    [Header("Save Settings")]
    [SerializeField] private bool enableAutoSave = true;
    [SerializeField] private float autoSaveInterval = 30f;
    [SerializeField] private bool enableBackups = true;
    [SerializeField] private int maxBackups = 3;
    
    public static SaveLoadManager Instance { get; private set; }
    
    public event System.Action<GameSaveData> OnDataLoaded;
    public event System.Action<GameSaveData> OnDataSaved;
    
    void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }
        
        Instance = this;
        DontDestroyOnLoad(gameObject);
        
        if (enableAutoSave)
        {
            InvokeRepeating(nameof(AutoSave), autoSaveInterval, autoSaveInterval);
        }
    }
    
    public async Task<GameSaveData> LoadGameDataAsync()
    {
        try
        {
            if (!File.Exists(SavePath))
            {
                Debug.Log("No save file found, creating new game data");
                return CreateNewGameData();
            }
            
            string jsonData = await File.ReadAllTextAsync(SavePath);
            GameSaveData saveData = JsonUtility.FromJson<GameSaveData>(jsonData);
            
            if (saveData != null)
            {
                OnDataLoaded?.Invoke(saveData);
                Debug.Log("Game data loaded successfully");
                return saveData;
            }
            else
            {
                Debug.LogError("Failed to deserialize save data");
                return CreateNewGameData();
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Error loading game data: {e.Message}");
            return CreateNewGameData();
        }
    }
    
    public async Task<bool> SaveGameDataAsync(GameSaveData saveData)
    {
        try
        {
            // Create backup if enabled
            if (enableBackups && File.Exists(SavePath))
            {
                CreateBackup();
            }
            
            saveData.lastSaveTime = System.DateTime.Now.ToBinary();
            saveData.version = Application.version;
            
            string jsonData = JsonUtility.ToJson(saveData, true);
            await File.WriteAllTextAsync(SavePath, jsonData);
            
            OnDataSaved?.Invoke(saveData);
            Debug.Log("Game data saved successfully");
            return true;
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Error saving game data: {e.Message}");
            return false;
        }
    }
    
    private void CreateBackup()
    {
        string backupDir = Path.Combine(Application.persistentDataPath, "backups");
        Directory.CreateDirectory(backupDir);
        
        string timestamp = System.DateTime.Now.ToString("yyyyMMdd_HHmmss");
        string backupPath = Path.Combine(backupDir, $"gamedata_backup_{timestamp}.json");
        
        File.Copy(SavePath, backupPath);
        
        // Clean up old backups
        CleanupOldBackups(backupDir);
    }
    
    private void CleanupOldBackups(string backupDir)
    {
        var backupFiles = Directory.GetFiles(backupDir, "gamedata_backup_*.json")
            .OrderByDescending(f => File.GetCreationTime(f))
            .Skip(maxBackups);
        
        foreach (string file in backupFiles)
        {
            File.Delete(file);
        }
    }
    
    private GameSaveData CreateNewGameData()
    {
        return new GameSaveData
        {
            playerData = new PlayerData(),
            gameSettings = new GameSettings(),
            lastSaveTime = System.DateTime.Now.ToBinary(),
            version = Application.version
        };
    }
    
    private async void AutoSave()
    {
        if (GameManager.Instance != null)
        {
            GameSaveData currentData = GameManager.Instance.GetCurrentSaveData();
            await SaveGameDataAsync(currentData);
        }
    }
}

// Main save data structure
[System.Serializable]
public class GameSaveData
{
    public PlayerData playerData;
    public GameSettings gameSettings;
    public long lastSaveTime;
    public string version;
    
    [Header("World State")]
    public List<QuestData> completedQuests = new List<QuestData>();
    public List<string> unlockedAreas = new List<string>();
    public Dictionary<string, bool> worldFlags = new Dictionary<string, bool>();
    
    // Convert DateTime for serialization compatibility
    public System.DateTime LastSaveDateTime
    {
        get => System.DateTime.FromBinary(lastSaveTime);
        set => lastSaveTime = value.ToBinary();
    }
}

[System.Serializable]
public class GameSettings
{
    [Range(0f, 1f)] public float masterVolume = 1f;
    [Range(0f, 1f)] public float musicVolume = 0.8f;
    [Range(0f, 1f)] public float sfxVolume = 1f;
    
    public bool fullscreen = true;
    public int resolutionIndex = 0;
    public int qualityLevel = 2;
    
    public KeyCode jumpKey = KeyCode.Space;
    public KeyCode interactKey = KeyCode.E;
    public KeyCode inventoryKey = KeyCode.Tab;
}
```

### Binary Serialization for Performance
```csharp
using System.Runtime.Serialization.Formatters.Binary;

public class BinarySaveSystem : MonoBehaviour
{
    private const string BINARY_SAVE_FILE = "gamedata.dat";
    private string BinarySavePath => Path.Combine(Application.persistentDataPath, BINARY_SAVE_FILE);
    
    public async Task<T> LoadBinaryDataAsync<T>() where T : class
    {
        try
        {
            if (!File.Exists(BinarySavePath))
            {
                return null;
            }
            
            byte[] data = await File.ReadAllBytesAsync(BinarySavePath);
            
            using (MemoryStream stream = new MemoryStream(data))
            {
                BinaryFormatter formatter = new BinaryFormatter();
                return formatter.Deserialize(stream) as T;
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Error loading binary data: {e.Message}");
            return null;
        }
    }
    
    public async Task<bool> SaveBinaryDataAsync<T>(T data) where T : class
    {
        try
        {
            using (MemoryStream stream = new MemoryStream())
            {
                BinaryFormatter formatter = new BinaryFormatter();
                formatter.Serialize(stream, data);
                
                byte[] bytes = stream.ToArray();
                await File.WriteAllBytesAsync(BinarySavePath, bytes);
                
                return true;
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Error saving binary data: {e.Message}");
            return false;
        }
    }
    
    // Compressed binary save
    public async Task<bool> SaveCompressedDataAsync<T>(T data) where T : class
    {
        try
        {
            using (MemoryStream stream = new MemoryStream())
            {
                BinaryFormatter formatter = new BinaryFormatter();
                formatter.Serialize(stream, data);
                
                byte[] uncompressed = stream.ToArray();
                byte[] compressed = CompressData(uncompressed);
                
                await File.WriteAllBytesAsync(BinarySavePath, compressed);
                return true;
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Error saving compressed data: {e.Message}");
            return false;
        }
    }
    
    private byte[] CompressData(byte[] data)
    {
        using (MemoryStream output = new MemoryStream())
        {
            using (System.IO.Compression.DeflateStream deflate = 
                new System.IO.Compression.DeflateStream(output, System.IO.Compression.CompressionMode.Compress))
            {
                deflate.Write(data, 0, data.Length);
            }
            return output.ToArray();
        }
    }
    
    private byte[] DecompressData(byte[] compressedData)
    {
        using (MemoryStream input = new MemoryStream(compressedData))
        using (MemoryStream output = new MemoryStream())
        {
            using (System.IO.Compression.DeflateStream deflate = 
                new System.IO.Compression.DeflateStream(input, System.IO.Compression.CompressionMode.Decompress))
            {
                deflate.CopyTo(output);
            }
            return output.ToArray();
        }
    }
}
```

### Data Validation and Migration
```csharp
public class DataVersionManager : MonoBehaviour
{
    [System.Serializable]
    public class VersionInfo
    {
        public string version;
        public int dataVersion;
        public System.DateTime releaseDate;
    }
    
    private readonly Dictionary<int, System.Func<GameSaveData, GameSaveData>> migrationMethods = 
        new Dictionary<int, System.Func<GameSaveData, GameSaveData>>();
    
    void Awake()
    {
        // Register migration methods
        migrationMethods[1] = MigrateFromVersion1;
        migrationMethods[2] = MigrateFromVersion2;
        // Add more as needed
    }
    
    public GameSaveData ValidateAndMigrateData(GameSaveData saveData)
    {
        if (saveData == null)
        {
            return CreateNewGameData();
        }
        
        // Validate data integrity
        if (!ValidateDataIntegrity(saveData))
        {
            Debug.LogWarning("Save data validation failed, creating new data");
            return CreateNewGameData();
        }
        
        // Perform version migration if needed
        int currentDataVersion = GetCurrentDataVersion();
        int saveDataVersion = GetSaveDataVersion(saveData);
        
        if (saveDataVersion < currentDataVersion)
        {
            Debug.Log($"Migrating save data from version {saveDataVersion} to {currentDataVersion}");
            saveData = PerformMigration(saveData, saveDataVersion, currentDataVersion);
        }
        
        return saveData;
    }
    
    private bool ValidateDataIntegrity(GameSaveData saveData)
    {
        // Check for null references
        if (saveData.playerData == null) return false;
        if (saveData.gameSettings == null) return false;
        
        // Validate ranges
        if (saveData.playerData.Level < 0) return false;
        if (saveData.gameSettings.masterVolume < 0 || saveData.gameSettings.masterVolume > 1) return false;
        
        // Additional validation logic
        return true;
    }
    
    private GameSaveData PerformMigration(GameSaveData saveData, int fromVersion, int toVersion)
    {
        GameSaveData migratedData = saveData;
        
        for (int version = fromVersion; version < toVersion; version++)
        {
            if (migrationMethods.TryGetValue(version + 1, out var migrationMethod))
            {
                migratedData = migrationMethod(migratedData);
                Debug.Log($"Applied migration to version {version + 1}");
            }
        }
        
        return migratedData;
    }
    
    private GameSaveData MigrateFromVersion1(GameSaveData oldData)
    {
        // Example: Add new fields, convert old data structures
        if (oldData.gameSettings == null)
        {
            oldData.gameSettings = new GameSettings();
        }
        
        return oldData;
    }
    
    private GameSaveData MigrateFromVersion2(GameSaveData oldData)
    {
        // Example: Convert inventory system
        // Migration logic here
        return oldData;
    }
    
    private int GetCurrentDataVersion() => 3; // Update when data structure changes
    private int GetSaveDataVersion(GameSaveData saveData) => 1; // Parse from save data
    private GameSaveData CreateNewGameData() => new GameSaveData();
}
```

## 🚀 AI/LLM Integration Opportunities

### Data Structure Design
```
"Design a serializable data structure for [game system] with proper Unity serialization"
"Create ScriptableObject architecture for [data type] with inheritance and polymorphism"
"Generate save/load system for [specific game data] with version migration"
```

### Performance Optimization
- AI-generated serialization performance comparisons
- Memory usage analysis for different serialization approaches
- Compression algorithm recommendations for save data

### Data Migration Strategies
- Automated migration method generation
- Data validation rule creation
- Backward compatibility analysis

## 💡 Key Highlights

### Serialization Best Practices
- **Use [SerializeField]** - Prefer private fields with SerializeField over public fields
- **Implement ISerializationCallbackReceiver** - For custom serialization logic
- **Cache ScriptableObject references** - Avoid repeated asset loading
- **Validate serialized data** - Check for null references and invalid values

### Save System Design Principles
- **Atomic saves** - Ensure save operations complete fully or not at all
- **Backup systems** - Maintain previous save versions for recovery
- **Async operations** - Use async/await for file I/O operations
- **Error handling** - Gracefully handle save/load failures

### ScriptableObject Advantages
- **Data-driven design** - Separate data from logic
- **Asset references** - Maintain proper Unity asset relationships
- **Inspector editing** - Designer-friendly data editing
- **Memory efficiency** - Shared data across multiple instances

### Performance Considerations
- **JSON vs Binary** - JSON for debugging, binary for performance
- **Compression** - Use for large save files
- **Incremental saves** - Save only changed data when possible
- **Threading** - Use background threads for heavy serialization

### Common Pitfalls
- Serializing Unity objects directly
- Not handling version compatibility
- Blocking main thread with large save operations
- Not validating loaded data
- Over-engineering simple data structures

This data management foundation enables robust, scalable save systems and data-driven game development in Unity.