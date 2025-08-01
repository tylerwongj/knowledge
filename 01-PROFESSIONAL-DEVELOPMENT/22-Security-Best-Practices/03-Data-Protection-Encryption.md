# 03-Data-Protection-Encryption.md

## 🎯 Learning Objectives
- Implement comprehensive data encryption strategies for Unity games
- Master secure data transmission and storage techniques
- Design privacy-compliant data collection and processing systems
- Develop secure backup and recovery mechanisms for game data

## 🔧 Unity Data Encryption Implementation

### Advanced Encryption Service
```csharp
// Comprehensive encryption service for Unity game data
using System;
using System.Security.Cryptography;
using System.Text;
using UnityEngine;
using System.Collections.Generic;
using Newtonsoft.Json;

public class GameDataEncryption : MonoBehaviour
{
    [Header("Encryption Configuration")]
    [SerializeField] private bool enableEncryption = true;
    [SerializeField] private EncryptionLevel defaultEncryptionLevel = EncryptionLevel.High;
    
    public static GameDataEncryption Instance { get; private set; }
    
    public enum EncryptionLevel
    {
        None = 0,
        Basic = 1,    // Simple XOR encryption
        Medium = 2,   // AES-128
        High = 3,     // AES-256
        Maximum = 4   // AES-256 + HMAC
    }
    
    private Dictionary<string, EncryptionLevel> dataTypeEncryption;
    private byte[] masterKey;
    private byte[] hmacKey;
    
    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeEncryption();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    private void InitializeEncryption()
    {
        // Generate or load encryption keys
        GenerateMasterKeys();
        
        // Configure encryption levels for different data types
        dataTypeEncryption = new Dictionary<string, EncryptionLevel>
        {
            {"PlayerStats", EncryptionLevel.High},
            {"Currency", EncryptionLevel.Maximum},
            {"Inventory", EncryptionLevel.High},
            {"Settings", EncryptionLevel.Medium},
            {"Achievements", EncryptionLevel.Medium},
            {"Leaderboard", EncryptionLevel.Basic},
            {"Analytics", EncryptionLevel.Basic}
        };
    }
    
    private void GenerateMasterKeys()
    {
        // In production, these keys should be derived from secure sources
        // such as device keystore, server-provided keys, or user passwords
        string deviceSeed = $"{SystemInfo.deviceUniqueIdentifier}_{Application.version}";
        
        using (var sha256 = SHA256.Create())
        {
            byte[] seedBytes = Encoding.UTF8.GetBytes(deviceSeed);
            masterKey = sha256.ComputeHash(seedBytes);
            
            // Generate HMAC key from different source
            string hmacSeed = $"{deviceSeed}_HMAC_{SystemInfo.deviceModel}";
            hmacKey = sha256.ComputeHash(Encoding.UTF8.GetBytes(hmacSeed));
        }
    }
    
    // Main encryption/decryption methods
    public string EncryptData(string data, string dataType = "default")
    {
        if (!enableEncryption || string.IsNullOrEmpty(data))
            return data;
        
        EncryptionLevel level = GetEncryptionLevel(dataType);
        
        switch (level)
        {
            case EncryptionLevel.None:
                return data;
            case EncryptionLevel.Basic:
                return EncryptXOR(data);
            case EncryptionLevel.Medium:
                return EncryptAES128(data);
            case EncryptionLevel.High:
                return EncryptAES256(data);
            case EncryptionLevel.Maximum:
                return EncryptAES256WithHMAC(data);
            default:
                return EncryptAES256(data);
        }
    }
    
    public string DecryptData(string encryptedData, string dataType = "default")
    {
        if (!enableEncryption || string.IsNullOrEmpty(encryptedData))
            return encryptedData;
        
        EncryptionLevel level = GetEncryptionLevel(dataType);
        
        try
        {
            switch (level)
            {
                case EncryptionLevel.None:
                    return encryptedData;
                case EncryptionLevel.Basic:
                    return DecryptXOR(encryptedData);
                case EncryptionLevel.Medium:
                    return DecryptAES128(encryptedData);
                case EncryptionLevel.High:
                    return DecryptAES256(encryptedData);
                case EncryptionLevel.Maximum:
                    return DecryptAES256WithHMAC(encryptedData);
                default:
                    return DecryptAES256(encryptedData);
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"Decryption failed for data type '{dataType}': {e.Message}");
            return null;
        }
    }
    
    private EncryptionLevel GetEncryptionLevel(string dataType)
    {
        return dataTypeEncryption.ContainsKey(dataType) 
            ? dataTypeEncryption[dataType] 
            : defaultEncryptionLevel;
    }
    
    // XOR Encryption (Basic)
    private string EncryptXOR(string data)
    {
        byte[] dataBytes = Encoding.UTF8.GetBytes(data);
        byte[] result = new byte[dataBytes.Length];
        
        for (int i = 0; i < dataBytes.Length; i++)
        {
            result[i] = (byte)(dataBytes[i] ^ masterKey[i % masterKey.Length]);
        }
        
        return Convert.ToBase64String(result);
    }
    
    private string DecryptXOR(string encryptedData)
    {
        byte[] encryptedBytes = Convert.FromBase64String(encryptedData);
        byte[] result = new byte[encryptedBytes.Length];
        
        for (int i = 0; i < encryptedBytes.Length; i++)
        {
            result[i] = (byte)(encryptedBytes[i] ^ masterKey[i % masterKey.Length]);
        }
        
        return Encoding.UTF8.GetString(result);
    }
    
    // AES-256 Encryption (High Security)
    private string EncryptAES256(string data)
    {
        using (Aes aes = Aes.Create())
        {
            aes.KeySize = 256;
            aes.Key = masterKey;
            aes.GenerateIV();
            
            ICryptoTransform encryptor = aes.CreateEncryptor();
            byte[] dataBytes = Encoding.UTF8.GetBytes(data);
            byte[] encryptedBytes = encryptor.TransformFinalBlock(dataBytes, 0, dataBytes.Length);
            
            // Combine IV and encrypted data
            byte[] result = new byte[aes.IV.Length + encryptedBytes.Length];
            Array.Copy(aes.IV, 0, result, 0, aes.IV.Length);
            Array.Copy(encryptedBytes, 0, result, aes.IV.Length, encryptedBytes.Length);
            
            return Convert.ToBase64String(result);
        }
    }
    
    private string DecryptAES256(string encryptedData)
    {
        byte[] encryptedBytes = Convert.FromBase64String(encryptedData);
        
        using (Aes aes = Aes.Create())
        {
            aes.KeySize = 256;
            aes.Key = masterKey;
            
            // Extract IV from the beginning
            byte[] iv = new byte[aes.IV.Length];
            byte[] cipherText = new byte[encryptedBytes.Length - iv.Length];
            
            Array.Copy(encryptedBytes, 0, iv, 0, iv.Length);
            Array.Copy(encryptedBytes, iv.Length, cipherText, 0, cipherText.Length);
            
            aes.IV = iv;
            
            ICryptoTransform decryptor = aes.CreateDecryptor();
            byte[] decryptedBytes = decryptor.TransformFinalBlock(cipherText, 0, cipherText.Length);
            
            return Encoding.UTF8.GetString(decryptedBytes);
        }
    }
    
    // AES-256 with HMAC (Maximum Security)
    private string EncryptAES256WithHMAC(string data)
    {
        // First encrypt with AES-256
        string encrypted = EncryptAES256(data);
        byte[] encryptedBytes = Convert.FromBase64String(encrypted);
        
        // Generate HMAC for integrity verification
        using (var hmac = new HMACSHA256(hmacKey))
        {
            byte[] hash = hmac.ComputeHash(encryptedBytes);
            
            // Combine encrypted data and HMAC
            byte[] result = new byte[encryptedBytes.Length + hash.Length];
            Array.Copy(encryptedBytes, 0, result, 0, encryptedBytes.Length);
            Array.Copy(hash, 0, result, encryptedBytes.Length, hash.Length);
            
            return Convert.ToBase64String(result);
        }
    }
    
    private string DecryptAES256WithHMAC(string encryptedData)
    {
        byte[] combinedBytes = Convert.FromBase64String(encryptedData);
        
        // Separate encrypted data and HMAC
        int hmacLength = 32; // SHA-256 produces 32-byte hash
        byte[] encryptedBytes = new byte[combinedBytes.Length - hmacLength];
        byte[] receivedHmac = new byte[hmacLength];
        
        Array.Copy(combinedBytes, 0, encryptedBytes, 0, encryptedBytes.Length);
        Array.Copy(combinedBytes, encryptedBytes.Length, receivedHmac, 0, hmacLength);
        
        // Verify HMAC integrity
        using (var hmac = new HMACSHA256(hmacKey))
        {
            byte[] computedHmac = hmac.ComputeHash(encryptedBytes);
            
            if (!CompareHashes(receivedHmac, computedHmac))
            {
                throw new CryptographicException("Data integrity verification failed");
            }
        }
        
        // Decrypt the data
        string encryptedString = Convert.ToBase64String(encryptedBytes);
        return DecryptAES256(encryptedString);
    }
    
    private bool CompareHashes(byte[] hash1, byte[] hash2)
    {
        if (hash1.Length != hash2.Length)
            return false;
        
        int result = 0;
        for (int i = 0; i < hash1.Length; i++)
        {
            result |= hash1[i] ^ hash2[i];
        }
        
        return result == 0;
    }
    
    // AES-128 Encryption (Medium Security)
    private string EncryptAES128(string data)
    {
        // Use first 16 bytes of master key for AES-128
        byte[] key128 = new byte[16];
        Array.Copy(masterKey, 0, key128, 0, 16);
        
        using (Aes aes = Aes.Create())
        {
            aes.KeySize = 128;
            aes.Key = key128;
            aes.GenerateIV();
            
            ICryptoTransform encryptor = aes.CreateEncryptor();
            byte[] dataBytes = Encoding.UTF8.GetBytes(data);
            byte[] encryptedBytes = encryptor.TransformFinalBlock(dataBytes, 0, dataBytes.Length);
            
            // Combine IV and encrypted data
            byte[] result = new byte[aes.IV.Length + encryptedBytes.Length];
            Array.Copy(aes.IV, 0, result, 0, aes.IV.Length);
            Array.Copy(encryptedBytes, 0, result, aes.IV.Length, encryptedBytes.Length);
            
            return Convert.ToBase64String(result);
        }
    }
    
    private string DecryptAES128(string encryptedData)
    {
        byte[] key128 = new byte[16];
        Array.Copy(masterKey, 0, key128, 0, 16);
        
        byte[] encryptedBytes = Convert.FromBase64String(encryptedData);
        
        using (Aes aes = Aes.Create())
        {
            aes.KeySize = 128;
            aes.Key = key128;
            
            // Extract IV from the beginning
            byte[] iv = new byte[aes.IV.Length];
            byte[] cipherText = new byte[encryptedBytes.Length - iv.Length];
            
            Array.Copy(encryptedBytes, 0, iv, 0, iv.Length);
            Array.Copy(encryptedBytes, iv.Length, cipherText, 0, cipherText.Length);
            
            aes.IV = iv;
            
            ICryptoTransform decryptor = aes.CreateDecryptor();
            byte[] decryptedBytes = decryptor.TransformFinalBlock(cipherText, 0, cipherText.Length);
            
            return Encoding.UTF8.GetString(decryptedBytes);
        }
    }
}
```

### Secure Save System Implementation
```csharp
// Secure save system with encryption and integrity checks
using System;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using Newtonsoft.Json;

public class SecureSaveSystem : MonoBehaviour
{
    [Header("Save Configuration")]
    [SerializeField] private string saveDirectory = "SecureSaves";
    [SerializeField] private bool enableBackups = true;
    [SerializeField] private int maxBackupCount = 5;
    [SerializeField] private bool enableCompression = true;
    
    public static SecureSaveSystem Instance { get; private set; }
    
    private string SavePath => Path.Combine(Application.persistentDataPath, saveDirectory);
    
    [System.Serializable]
    public class SecureSaveData
    {
        public string version = Application.version;
        public DateTime saveTime = DateTime.UtcNow;
        public string checksum;
        public Dictionary<string, object> gameData;
        public string deviceId = SystemInfo.deviceUniqueIdentifier;
        
        public SecureSaveData()
        {
            gameData = new Dictionary<string, object>();
        }
    }
    
    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            CreateSaveDirectory();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    private void CreateSaveDirectory()
    {
        if (!Directory.Exists(SavePath))
        {
            Directory.CreateDirectory(SavePath);
        }
    }
    
    // Save game data securely
    public bool SaveGameData<T>(string saveName, T data, string dataType = "GameData") where T : class
    {
        try
        {
            // Create secure save data wrapper
            SecureSaveData saveData = new SecureSaveData();
            
            // Serialize the actual game data
            string jsonData = JsonConvert.SerializeObject(data, Formatting.None);
            
            // Encrypt the serialized data
            string encryptedData = GameDataEncryption.Instance.EncryptData(jsonData, dataType);
            
            // Store in save data
            saveData.gameData["main"] = encryptedData;
            saveData.gameData["dataType"] = dataType;
            
            // Calculate checksum for integrity verification
            saveData.checksum = CalculateChecksum(encryptedData);
            
            // Serialize the complete save data
            string saveJson = JsonConvert.SerializeObject(saveData, Formatting.Indented);
            
            // Optionally compress the save data
            if (enableCompression)
            {
                saveJson = CompressString(saveJson);
            }
            
            // Create backup if enabled
            if (enableBackups)
            {
                CreateBackup(saveName);
            }
            
            // Write to file
            string filePath = Path.Combine(SavePath, $"{saveName}.save");
            File.WriteAllText(filePath, saveJson);
            
            Debug.Log($"Game data saved successfully: {saveName}");
            return true;
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to save game data '{saveName}': {e.Message}");
            return false;
        }
    }
    
    // Load game data securely
    public T LoadGameData<T>(string saveName, string dataType = "GameData") where T : class
    {
        try
        {
            string filePath = Path.Combine(SavePath, $"{saveName}.save");
            
            if (!File.Exists(filePath))
            {
                Debug.LogWarning($"Save file not found: {saveName}");
                return null;
            }
            
            // Read save file
            string saveJson = File.ReadAllText(filePath);
            
            // Decompress if needed
            if (enableCompression)
            {
                saveJson = DecompressString(saveJson);
            }
            
            // Deserialize save data wrapper
            SecureSaveData saveData = JsonConvert.DeserializeObject<SecureSaveData>(saveJson);
            
            if (saveData == null || saveData.gameData == null)
            {
                Debug.LogError($"Invalid save data format: {saveName}");
                return null;
            }
            
            // Verify device ID for tamper detection
            if (saveData.deviceId != SystemInfo.deviceUniqueIdentifier)
            {
                Debug.LogWarning($"Save file device mismatch: {saveName}");
                // Depending on your game's policy, you might want to reject or accept this
            }
            
            // Extract encrypted data
            if (!saveData.gameData.ContainsKey("main"))
            {
                Debug.LogError($"Save data missing main content: {saveName}");
                return null;
            }
            
            string encryptedData = saveData.gameData["main"].ToString();
            
            // Verify integrity
            string calculatedChecksum = CalculateChecksum(encryptedData);
            if (calculatedChecksum != saveData.checksum)
            {
                Debug.LogError($"Save data integrity check failed: {saveName}");
                
                // Try to restore from backup
                if (enableBackups)
                {
                    return RestoreFromBackup<T>(saveName, dataType);
                }
                
                return null;
            }
            
            // Decrypt the data
            string decryptedData = GameDataEncryption.Instance.DecryptData(encryptedData, dataType);
            
            if (string.IsNullOrEmpty(decryptedData))
            {
                Debug.LogError($"Failed to decrypt save data: {saveName}");
                return null;
            }
            
            // Deserialize the actual game data
            T gameData = JsonConvert.DeserializeObject<T>(decryptedData);
            
            Debug.Log($"Game data loaded successfully: {saveName}");
            return gameData;
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to load game data '{saveName}': {e.Message}");
            
            // Try to restore from backup
            if (enableBackups)
            {
                return RestoreFromBackup<T>(saveName, dataType);
            }
            
            return null;
        }
    }
    
    // Backup management
    private void CreateBackup(string saveName)
    {
        try
        {
            string originalPath = Path.Combine(SavePath, $"{saveName}.save");
            
            if (!File.Exists(originalPath))
                return;
            
            // Create backup with timestamp
            string timestamp = DateTime.UtcNow.ToString("yyyyMMdd_HHmmss");
            string backupPath = Path.Combine(SavePath, $"{saveName}_backup_{timestamp}.save");
            
            File.Copy(originalPath, backupPath);
            
            // Clean up old backups
            CleanupOldBackups(saveName);
        }
        catch (Exception e)
        {
            Debug.LogWarning($"Failed to create backup for '{saveName}': {e.Message}");
        }
    }
    
    private void CleanupOldBackups(string saveName)
    {
        try
        {
            string[] backupFiles = Directory.GetFiles(SavePath, $"{saveName}_backup_*.save");
            
            if (backupFiles.Length <= maxBackupCount)
                return;
            
            // Sort by creation time (oldest first)
            Array.Sort(backupFiles, (x, y) => File.GetCreationTime(x).CompareTo(File.GetCreationTime(y)));
            
            // Delete oldest backups
            int filesToDelete = backupFiles.Length - maxBackupCount;
            for (int i = 0; i < filesToDelete; i++)
            {
                File.Delete(backupFiles[i]);
            }
        }
        catch (Exception e)
        {
            Debug.LogWarning($"Failed to cleanup old backups for '{saveName}': {e.Message}");
        }
    }
    
    private T RestoreFromBackup<T>(string saveName, string dataType) where T : class
    {
        try
        {
            string[] backupFiles = Directory.GetFiles(SavePath, $"{saveName}_backup_*.save");
            
            if (backupFiles.Length == 0)
            {
                Debug.LogWarning($"No backup files found for '{saveName}'");
                return null;
            }
            
            // Sort by creation time (newest first)
            Array.Sort(backupFiles, (x, y) => File.GetCreationTime(y).CompareTo(File.GetCreationTime(x)));
            
            // Try to load from the most recent backup
            foreach (string backupFile in backupFiles)
            {
                try
                {
                    string backupName = Path.GetFileNameWithoutExtension(backupFile);
                    
                    // Temporarily rename backup to main save
                    string tempSavePath = Path.Combine(SavePath, $"{saveName}_temp.save");
                    File.Copy(backupFile, tempSavePath);
                    
                    // Try to load from backup
                    string saveJson = File.ReadAllText(tempSavePath);
                    
                    if (enableCompression)
                    {
                        saveJson = DecompressString(saveJson);
                    }
                    
                    SecureSaveData saveData = JsonConvert.DeserializeObject<SecureSaveData>(saveJson);
                    string encryptedData = saveData.gameData["main"].ToString();
                    string decryptedData = GameDataEncryption.Instance.DecryptData(encryptedData, dataType);
                    T gameData = JsonConvert.DeserializeObject<T>(decryptedData);
                    
                    // Clean up temp file
                    File.Delete(tempSavePath);
                    
                    Debug.Log($"Successfully restored '{saveName}' from backup: {backupName}");
                    return gameData;
                }
                catch (Exception backupException)
                {
                    Debug.LogWarning($"Failed to restore from backup '{backupFile}': {backupException.Message}");
                    continue;
                }
            }
            
            Debug.LogError($"All backup restoration attempts failed for '{saveName}'");
            return null;
        }
        catch (Exception e)
        {
            Debug.LogError($"Backup restoration failed for '{saveName}': {e.Message}");
            return null;
        }
    }
    
    // Utility methods
    private string CalculateChecksum(string data)
    {
        using (var sha256 = System.Security.Cryptography.SHA256.Create())
        {
            byte[] hashBytes = sha256.ComputeHash(System.Text.Encoding.UTF8.GetBytes(data));
            return Convert.ToBase64String(hashBytes);
        }
    }
    
    private string CompressString(string text)
    {
        byte[] data = System.Text.Encoding.UTF8.GetBytes(text);
        
        using (var memoryStream = new MemoryStream())
        {
            using (var gzipStream = new System.IO.Compression.GZipStream(memoryStream, System.IO.Compression.CompressionMode.Compress))
            {
                gzipStream.Write(data, 0, data.Length);
            }
            
            return Convert.ToBase64String(memoryStream.ToArray());
        }
    }
    
    private string DecompressString(string compressedText)
    {
        byte[] compressedData = Convert.FromBase64String(compressedText);
        
        using (var memoryStream = new MemoryStream(compressedData))
        {
            using (var gzipStream = new System.IO.Compression.GZipStream(memoryStream, System.IO.Compression.CompressionMode.Decompress))
            {
                using (var reader = new StreamReader(gzipStream))
                {
                    return reader.ReadToEnd();
                }
            }
        }
    }
    
    // Public utility methods
    public bool SaveExists(string saveName)
    {
        string filePath = Path.Combine(SavePath, $"{saveName}.save");
        return File.Exists(filePath);
    }
    
    public bool DeleteSave(string saveName)
    {
        try
        {
            string filePath = Path.Combine(SavePath, $"{saveName}.save");
            
            if (File.Exists(filePath))
            {
                File.Delete(filePath);
            }
            
            // Also delete backups
            string[] backupFiles = Directory.GetFiles(SavePath, $"{saveName}_backup_*.save");
            foreach (string backupFile in backupFiles)
            {
                File.Delete(backupFile);
            }
            
            return true;
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to delete save '{saveName}': {e.Message}");
            return false;
        }
    }
    
    public string[] GetAvailableSaves()
    {
        try
        {
            string[] saveFiles = Directory.GetFiles(SavePath, "*.save");
            List<string> saveNames = new List<string>();
            
            foreach (string filePath in saveFiles)
            {
                string fileName = Path.GetFileNameWithoutExtension(filePath);
                
                // Skip backup files
                if (!fileName.Contains("_backup_"))
                {
                    saveNames.Add(fileName);
                }
            }
            
            return saveNames.ToArray();
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to get available saves: {e.Message}");
            return new string[0];
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Data Encryption Security Audit
```
PROMPT TEMPLATE - Encryption Security Review:

"Review this Unity data encryption implementation for security vulnerabilities:

```csharp
[PASTE YOUR ENCRYPTION CODE]
```

Analyze for:
1. Encryption algorithm strength and implementation
2. Key generation and management security
3. Data integrity protection mechanisms
4. Potential timing attack vulnerabilities
5. Side-channel attack resistance
6. Key storage and derivation security
7. Forward secrecy considerations

Provide specific improvements with Unity-focused implementation examples."
```

### GDPR Compliance Generator
```
PROMPT TEMPLATE - Privacy Compliance Implementation:

"Generate a GDPR-compliant data handling system for Unity with these requirements:

Game Type: [Mobile/PC/Console/Web]
Data Collection: [Analytics/User profiles/Leaderboards/etc.]
User Regions: [EU/Global/Specific regions]
Platform Integration: [Google Play/App Store/Steam/etc.]

Include:
1. Data collection consent management
2. Data export functionality (right to portability)
3. Data deletion system (right to erasure)
4. Privacy policy integration
5. Age verification for minors
6. Cookie/tracking consent (for web games)
7. Data retention policies implementation"
```

## 💡 Key Data Protection Principles

### Essential Data Protection Checklist
- **Encrypt sensitive data at rest** - Use strong encryption for stored data
- **Secure data in transit** - Always use HTTPS/TLS for network communication
- **Implement data minimization** - Only collect necessary data
- **Provide user control** - Allow users to manage their data
- **Regular security audits** - Review data handling practices regularly
- **Backup and recovery** - Implement secure backup mechanisms
- **Access controls** - Limit who can access sensitive data
- **Data retention policies** - Delete data when no longer needed

### Common Data Protection Vulnerabilities
1. **Unencrypted sensitive data storage**
2. **Weak encryption key management**
3. **Plaintext data transmission**
4. **Excessive data collection**
5. **Missing data integrity checks**
6. **Inadequate backup security**
7. **Poor access control implementation**
8. **Missing data retention policies**

This comprehensive data protection system provides Unity developers with enterprise-grade encryption and privacy compliance capabilities, ensuring sensitive player data remains secure while meeting regulatory requirements like GDPR and CCPA.