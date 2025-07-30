# @48-Cloud-Save-System

## 🎯 Core Concept
Automated cloud save system for synchronizing player data across devices with conflict resolution and offline support.

## 🔧 Implementation

### Cloud Save Manager
```csharp
using UnityEngine;
using System.Collections.Generic;
using System.Collections;
using UnityEngine.Networking;
using System.IO;

public class CloudSaveManager : MonoBehaviour
{
    public static CloudSaveManager Instance;
    
    [Header("Cloud Settings")]
    public string cloudEndpoint = "https://your-cloud-service.com/api";
    public string apiKey = "";
    public bool enableCloudSave = true;
    public bool enableOfflineMode = true;
    public float autoSyncInterval = 300f; // 5 minutes
    
    [Header("Sync Settings")]
    public bool syncOnStart = true;
    public bool syncOnPause = true;
    public bool syncOnQuit = true;
    public ConflictResolution conflictResolution = ConflictResolution.LatestWins;
    
    [Header("Encryption")]
    public bool encryptSaveData = true;
    public string encryptionKey = "YourEncryptionKey123";
    
    private Dictionary<string, SaveDataEntry> localSaveData;
    private Dictionary<string, SaveDataEntry> cloudSaveData;
    private bool isOnline = true;
    private bool isSyncing = false;
    private string userId;
    
    public System.Action OnSyncStarted;
    public System.Action OnSyncCompleted;
    public System.Action<string> OnSyncFailed;
    public System.Action<SaveConflict> OnConflictDetected;
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeCloudSave();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void InitializeCloudSave()
    {
        localSaveData = new Dictionary<string, SaveDataEntry>();
        cloudSaveData = new Dictionary<string, SaveDataEntry>();
        
        userId = GetOrCreateUserId();
        
        // Load local save data
        LoadLocalSaveData();
        
        // Check internet connectivity
        StartCoroutine(CheckConnectivity());
        
        // Start auto-sync coroutine
        if (enableCloudSave)
        {
            StartCoroutine(AutoSyncCoroutine());
        }
        
        // Sync on start if enabled
        if (syncOnStart && enableCloudSave)
        {
            StartCoroutine(SyncWithCloud());
        }
        
        Debug.Log("Cloud Save Manager initialized");
    }
    
    string GetOrCreateUserId()
    {
        string id = PlayerPrefs.GetString("CloudUserId", "");
        
        if (string.IsNullOrEmpty(id))
        {
            id = System.Guid.NewGuid().ToString();
            PlayerPrefs.SetString("CloudUserId", id);
            PlayerPrefs.Save();
        }
        
        return id;
    }
    
    void LoadLocalSaveData()
    {
        string localPath = GetLocalSavePath();
        
        if (File.Exists(localPath))
        {
            try
            {
                string jsonData = File.ReadAllText(localPath);
                
                if (encryptSaveData)
                {
                    jsonData = DecryptString(jsonData, encryptionKey);
                }
                
                SaveDataCollection collection = JsonUtility.FromJson<SaveDataCollection>(jsonData);
                
                if (collection != null && collection.entries != null)
                {
                    foreach (var entry in collection.entries)
                    {
                        localSaveData[entry.key] = entry;
                    }
                }
                
                Debug.Log($"Loaded {localSaveData.Count} local save entries");
            }
            catch (System.Exception e)
            {
                Debug.LogError($"Failed to load local save data: {e.Message}");
            }
        }
    }
    
    void SaveLocalSaveData()
    {
        try
        {
            SaveDataCollection collection = new SaveDataCollection
            {
                userId = userId,
                lastSaved = System.DateTime.UtcNow.ToString("o"),
                entries = new List<SaveDataEntry>(localSaveData.Values)
            };
            
            string jsonData = JsonUtility.ToJson(collection, true);
            
            if (encryptSaveData)
            {
                jsonData = EncryptString(jsonData, encryptionKey);
            }
            
            string localPath = GetLocalSavePath();
            File.WriteAllText(localPath, jsonData);
            
            Debug.Log("Local save data saved successfully");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Failed to save local data: {e.Message}");
        }
    }
    
    string GetLocalSavePath()
    {
        return Path.Combine(Application.persistentDataPath, "cloudsave.dat");
    }
    
    public void SaveData(string key, object data)
    {
        string jsonData = JsonUtility.ToJson(data);
        
        SaveDataEntry entry = new SaveDataEntry
        {
            key = key,
            data = jsonData,
            timestamp = System.DateTime.UtcNow.ToString("o"),
            dataType = data.GetType().Name
        };
        
        localSaveData[key] = entry;
        
        // Save locally immediately
        SaveLocalSaveData();
        
        Debug.Log($"Data saved for key: {key}");
    }
    
    public T LoadData<T>(string key, T defaultValue = default(T))
    {
        if (localSaveData.ContainsKey(key))
        {
            try
            {
                SaveDataEntry entry = localSaveData[key];
                T data = JsonUtility.FromJson<T>(entry.data);
                return data;
            }
            catch (System.Exception e)
            {
                Debug.LogError($"Failed to load data for key {key}: {e.Message}");
            }
        }
        
        return defaultValue;
    }
    
    public bool HasData(string key)
    {
        return localSaveData.ContainsKey(key);
    }
    
    public void DeleteData(string key)
    {
        if (localSaveData.ContainsKey(key))
        {
            localSaveData.Remove(key);
            SaveLocalSaveData();
            Debug.Log($"Data deleted for key: {key}");
        }
    }
    
    public void ClearAllData()
    {
        localSaveData.Clear();
        SaveLocalSaveData();
        Debug.Log("All save data cleared");
    }
    
    IEnumerator CheckConnectivity()
    {
        while (true)
        {
            yield return new WaitForSeconds(10f);
            
            if (Application.internetReachability != NetworkReachability.NotReachable)
            {
                // Test actual connectivity to cloud service
                yield return StartCoroutine(TestCloudConnectivity());
            }
            else
            {
                isOnline = false;
            }
        }
    }
    
    IEnumerator TestCloudConnectivity()
    {
        using (UnityWebRequest request = UnityWebRequest.Get($"{cloudEndpoint}/ping"))
        {
            request.SetRequestHeader("Authorization", $"Bearer {apiKey}");
            request.timeout = 5;
            
            yield return request.SendWebRequest();
            
            isOnline = request.result == UnityWebRequest.Result.Success;
        }
    }
    
    IEnumerator AutoSyncCoroutine()
    {
        while (enableCloudSave)
        {
            yield return new WaitForSeconds(autoSyncInterval);
            
            if (isOnline && !isSyncing)
            {
                yield return StartCoroutine(SyncWithCloud());
            }
        }
    }
    
    public void ForceSyncNow()
    {
        if (!enableCloudSave)
        {
            Debug.LogWarning("Cloud save is disabled");
            return;
        }
        
        if (isSyncing)
        {
            Debug.LogWarning("Sync already in progress");
            return;
        }
        
        StartCoroutine(SyncWithCloud());
    }
    
    IEnumerator SyncWithCloud()
    {
        if (!isOnline)
        {
            Debug.LogWarning("Cannot sync: offline");
            yield break;
        }
        
        isSyncing = true;
        OnSyncStarted?.Invoke();
        
        Debug.Log("Starting cloud sync...");
        
        // Download cloud data
        yield return StartCoroutine(DownloadCloudData());
        
        // Resolve conflicts
        List<SaveConflict> conflicts = DetectConflicts();
        if (conflicts.Count > 0)
        {
            yield return StartCoroutine(ResolveConflicts(conflicts));
        }
        
        // Upload local changes
        yield return StartCoroutine(UploadLocalData());
        
        isSyncing = false;
        OnSyncCompleted?.Invoke();
        
        Debug.Log("Cloud sync completed");
    }
    
    IEnumerator DownloadCloudData()
    {
        string endpoint = $"{cloudEndpoint}/save/{userId}";
        
        using (UnityWebRequest request = UnityWebRequest.Get(endpoint))
        {
            request.SetRequestHeader("Authorization", $"Bearer {apiKey}");
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    string responseData = request.downloadHandler.text;
                    
                    if (encryptSaveData)
                    {
                        responseData = DecryptString(responseData, encryptionKey);
                    }
                    
                    SaveDataCollection collection = JsonUtility.FromJson<SaveDataCollection>(responseData);
                    
                    if (collection != null && collection.entries != null)
                    {
                        cloudSaveData.Clear();
                        foreach (var entry in collection.entries)
                        {
                            cloudSaveData[entry.key] = entry;
                        }
                        
                        Debug.Log($"Downloaded {cloudSaveData.Count} cloud save entries");
                    }
                }
                catch (System.Exception e)
                {
                    Debug.LogError($"Failed to parse cloud save data: {e.Message}");
                    OnSyncFailed?.Invoke($"Parse error: {e.Message}");
                }
            }
            else
            {
                Debug.LogError($"Failed to download cloud data: {request.error}");
                OnSyncFailed?.Invoke($"Download error: {request.error}");
            }
        }
    }
    
    IEnumerator UploadLocalData()
    {
        SaveDataCollection collection = new SaveDataCollection
        {
            userId = userId,
            lastSaved = System.DateTime.UtcNow.ToString("o"),
            entries = new List<SaveDataEntry>(localSaveData.Values)
        };
        
        string jsonData = JsonUtility.ToJson(collection);
        
        if (encryptSaveData)
        {
            jsonData = EncryptString(jsonData, encryptionKey);
        }
        
        string endpoint = $"{cloudEndpoint}/save/{userId}";
        
        using (UnityWebRequest request = new UnityWebRequest(endpoint, "PUT"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.SetRequestHeader("Authorization", $"Bearer {apiKey}");
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("Successfully uploaded save data to cloud");
            }
            else
            {
                Debug.LogError($"Failed to upload save data: {request.error}");
                OnSyncFailed?.Invoke($"Upload error: {request.error}");
            }
        }
    }
    
    List<SaveConflict> DetectConflicts()
    {
        List<SaveConflict> conflicts = new List<SaveConflict>();
        
        foreach (var localEntry in localSaveData)
        {
            string key = localEntry.Key;
            SaveDataEntry local = localEntry.Value;
            
            if (cloudSaveData.ContainsKey(key))
            {
                SaveDataEntry cloud = cloudSaveData[key];
                
                // Check if timestamps differ
                System.DateTime localTime = System.DateTime.Parse(local.timestamp);
                System.DateTime cloudTime = System.DateTime.Parse(cloud.timestamp);
                
                if (localTime != cloudTime && local.data != cloud.data)
                {
                    SaveConflict conflict = new SaveConflict
                    {
                        key = key,
                        localEntry = local,
                        cloudEntry = cloud
                    };
                    
                    conflicts.Add(conflict);
                }
            }
        }
        
        return conflicts;
    }
    
    IEnumerator ResolveConflicts(List<SaveConflict> conflicts)
    {
        foreach (SaveConflict conflict in conflicts)
        {
            OnConflictDetected?.Invoke(conflict);
            
            SaveDataEntry resolvedEntry = null;
            
            switch (conflictResolution)
            {
                case ConflictResolution.LatestWins:
                    resolvedEntry = ResolveByLatest(conflict);
                    break;
                    
                case ConflictResolution.LocalWins:
                    resolvedEntry = conflict.localEntry;
                    break;
                    
                case ConflictResolution.CloudWins:
                    resolvedEntry = conflict.cloudEntry;
                    break;
                    
                case ConflictResolution.UserChoice:
                    // This would typically show a UI for user selection
                    yield return StartCoroutine(ShowConflictResolutionUI(conflict));
                    resolvedEntry = conflict.resolvedEntry;
                    break;
            }
            
            if (resolvedEntry != null)
            {
                localSaveData[conflict.key] = resolvedEntry;
                Debug.Log($"Resolved conflict for key: {conflict.key}");
            }
        }
        
        // Save resolved data locally
        SaveLocalSaveData();
    }
    
    SaveDataEntry ResolveByLatest(SaveConflict conflict)
    {
        System.DateTime localTime = System.DateTime.Parse(conflict.localEntry.timestamp);
        System.DateTime cloudTime = System.DateTime.Parse(conflict.cloudEntry.timestamp);
        
        return localTime > cloudTime ? conflict.localEntry : conflict.cloudEntry;
    }
    
    IEnumerator ShowConflictResolutionUI(SaveConflict conflict)
    {
        // This would show a UI dialog for the user to choose
        // For now, default to latest wins
        conflict.resolvedEntry = ResolveByLatest(conflict);
        yield return null;
    }
    
    string EncryptString(string plainText, string key)
    {
        // Simple XOR encryption for demonstration
        // In production, use proper encryption
        byte[] data = System.Text.Encoding.UTF8.GetBytes(plainText);
        byte[] keyBytes = System.Text.Encoding.UTF8.GetBytes(key);
        
        for (int i = 0; i < data.Length; i++)
        {
            data[i] = (byte)(data[i] ^ keyBytes[i % keyBytes.Length]);
        }
        
        return System.Convert.ToBase64String(data);
    }
    
    string DecryptString(string cipherText, string key)
    {
        // Simple XOR decryption
        try
        {
            byte[] data = System.Convert.FromBase64String(cipherText);
            byte[] keyBytes = System.Text.Encoding.UTF8.GetBytes(key);
            
            for (int i = 0; i < data.Length; i++)
            {
                data[i] = (byte)(data[i] ^ keyBytes[i % keyBytes.Length]);
            }
            
            return System.Text.Encoding.UTF8.GetString(data);
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Decryption failed: {e.Message}");
            return cipherText;
        }
    }
    
    public CloudSaveStatus GetSaveStatus()
    {
        return new CloudSaveStatus
        {
            isOnline = isOnline,
            isSyncing = isSyncing,
            localEntryCount = localSaveData.Count,
            cloudEntryCount = cloudSaveData.Count,
            lastSyncTime = PlayerPrefs.GetString("LastSyncTime", "Never")
        };
    }
    
    public void SetConflictResolution(ConflictResolution resolution)
    {
        conflictResolution = resolution;
        PlayerPrefs.SetInt("ConflictResolution", (int)resolution);
        PlayerPrefs.Save();
    }
    
    void OnApplicationPause(bool pauseStatus)
    {
        if (pauseStatus && syncOnPause && enableCloudSave && !isSyncing)
        {
            StartCoroutine(SyncWithCloud());
        }
    }
    
    void OnApplicationQuit()
    {
        if (syncOnQuit && enableCloudSave && !isSyncing)
        {
            // Force immediate sync on quit
            StartCoroutine(SyncWithCloud());
        }
    }
    
    // Backup and restore functionality
    public void CreateBackup(string backupName)
    {
        try
        {
            SaveDataCollection backup = new SaveDataCollection
            {
                userId = userId,
                lastSaved = System.DateTime.UtcNow.ToString("o"),
                entries = new List<SaveDataEntry>(localSaveData.Values)
            };
            
            string jsonData = JsonUtility.ToJson(backup, true);
            string backupPath = Path.Combine(Application.persistentDataPath, $"backup_{backupName}.dat");
            
            File.WriteAllText(backupPath, jsonData);
            Debug.Log($"Backup created: {backupName}");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Failed to create backup: {e.Message}");
        }
    }
    
    public bool RestoreBackup(string backupName)
    {
        try
        {
            string backupPath = Path.Combine(Application.persistentDataPath, $"backup_{backupName}.dat");
            
            if (!File.Exists(backupPath))
            {
                Debug.LogError($"Backup file not found: {backupName}");
                return false;
            }
            
            string jsonData = File.ReadAllText(backupPath);
            SaveDataCollection backup = JsonUtility.FromJson<SaveDataCollection>(jsonData);
            
            if (backup != null && backup.entries != null)
            {
                localSaveData.Clear();
                foreach (var entry in backup.entries)
                {
                    localSaveData[entry.key] = entry;
                }
                
                SaveLocalSaveData();
                Debug.Log($"Backup restored: {backupName}");
                return true;
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Failed to restore backup: {e.Message}");
        }
        
        return false;
    }
    
    public List<string> GetAvailableBackups()
    {
        List<string> backups = new List<string>();
        
        try
        {
            string[] files = Directory.GetFiles(Application.persistentDataPath, "backup_*.dat");
            
            foreach (string file in files)
            {
                string fileName = Path.GetFileNameWithoutExtension(file);
                string backupName = fileName.Substring("backup_".Length);
                backups.Add(backupName);
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Failed to get backup list: {e.Message}");
        }
        
        return backups;
    }
}

// Data structures
public enum ConflictResolution
{
    LatestWins,
    LocalWins,
    CloudWins,
    UserChoice
}

[System.Serializable]
public class SaveDataEntry
{
    public string key;
    public string data;
    public string timestamp;
    public string dataType;
}

[System.Serializable]
public class SaveDataCollection
{
    public string userId;
    public string lastSaved;
    public List<SaveDataEntry> entries;
}

[System.Serializable]
public class SaveConflict
{
    public string key;
    public SaveDataEntry localEntry;
    public SaveDataEntry cloudEntry;
    public SaveDataEntry resolvedEntry;
}

[System.Serializable]
public class CloudSaveStatus
{
    public bool isOnline;
    public bool isSyncing;
    public int localEntryCount;
    public int cloudEntryCount;
    public string lastSyncTime;
}

// Helper component for easy save/load
public class CloudSaveHelper : MonoBehaviour
{
    public static void SavePlayerData(PlayerData data)
    {
        if (CloudSaveManager.Instance != null)
        {
            CloudSaveManager.Instance.SaveData("player_data", data);
        }
    }
    
    public static PlayerData LoadPlayerData()
    {
        if (CloudSaveManager.Instance != null)
        {
            return CloudSaveManager.Instance.LoadData<PlayerData>("player_data", new PlayerData());
        }
        
        return new PlayerData();
    }
    
    public static void SaveGameSettings(GameSettings settings)
    {
        if (CloudSaveManager.Instance != null)
        {
            CloudSaveManager.Instance.SaveData("game_settings", settings);
        }
    }
    
    public static GameSettings LoadGameSettings()
    {
        if (CloudSaveManager.Instance != null)
        {
            return CloudSaveManager.Instance.LoadData<GameSettings>("game_settings", new GameSettings());
        }
        
        return new GameSettings();
    }
}

// Example data structures
[System.Serializable]
public class PlayerData
{
    public string playerName = "Player";
    public int level = 1;
    public int experience = 0;
    public int currency = 0;
    public Vector3 position = Vector3.zero;
    public List<string> inventory = new List<string>();
    public List<string> achievements = new List<string>();
}

[System.Serializable]
public class GameSettings
{
    public float musicVolume = 1f;
    public float sfxVolume = 1f;
    public bool vibrationEnabled = true;
    public string language = "English";
    public int qualityLevel = 2;
}
```

## 🚀 AI/LLM Integration
- Automatically resolve save conflicts using intelligent analysis
- Generate backup strategies based on player behavior
- Create predictive sync scheduling for optimal performance

## 💡 Key Benefits
- Cross-device save synchronization
- Automatic conflict resolution
- Offline support with sync on reconnection