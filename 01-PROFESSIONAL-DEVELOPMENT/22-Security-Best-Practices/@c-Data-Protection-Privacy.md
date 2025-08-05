# @c-Data-Protection-Privacy

## 🎯 Learning Objectives
- Implement GDPR and privacy compliance in Unity games
- Master data encryption and secure storage techniques
- Design privacy-by-design architecture for game development
- Understand data retention and deletion requirements

## 🔧 GDPR Compliance Framework

### Data Processing and Consent Management
```csharp
// GDPR-Compliant Data Manager
using System.Collections.Generic;
using UnityEngine;

public class GDPRDataManager : MonoBehaviour
{
    [Header("Privacy Settings")]
    [SerializeField] private bool requireExplicitConsent = true;
    [SerializeField] private string privacyPolicyUrl = "https://yourgame.com/privacy";
    [SerializeField] private string dataProcessingBasis = "legitimate_interest";
    
    private Dictionary<string, ConsentRecord> playerConsents;
    private List<DataProcessor> dataProcessors;
    
    void Start()
    {
        playerConsents = new Dictionary<string, ConsentRecord>();
        InitializeDataProcessors();
    }
    
    private void InitializeDataProcessors()
    {
        dataProcessors = new List<DataProcessor>
        {
            new DataProcessor
            {
                ProcessorId = "analytics",
                ProcessorName = "Game Analytics",
                Purpose = "Improve game experience and performance",
                DataTypes = new[] { "gameplay_events", "device_info", "performance_metrics" },
                LegalBasis = "legitimate_interest",
                RetentionPeriod = TimeSpan.FromDays(365),
                IsEssential = false
            },
            new DataProcessor
            {
                ProcessorId = "crashlytics",
                ProcessorName = "Crash Reporting",
                Purpose = "Monitor and fix game crashes",
                DataTypes = new[] { "crash_logs", "device_info", "app_version" },
                LegalBasis = "legitimate_interest",
                RetentionPeriod = TimeSpan.FromDays(90),
                IsEssential = true
            },
            new DataProcessor
            {
                ProcessorId = "advertising",
                ProcessorName = "Targeted Advertising",
                Purpose = "Show relevant advertisements",
                DataTypes = new[] { "advertising_id", "demographics", "behavioral_data" },
                LegalBasis = "consent",
                RetentionPeriod = TimeSpan.FromDays(730),
                IsEssential = false
            }
        };
    }
    
    public async Task<bool> RequestConsentAsync(string playerId)
    {
        var consentUI = FindObjectOfType<ConsentUI>();
        if (consentUI == null)
        {
            Debug.LogError("ConsentUI not found");
            return false;
        }
        
        // Show consent dialog with detailed information
        var consentRequest = new ConsentRequest
        {
            PlayerId = playerId,
            DataProcessors = dataProcessors,
            PrivacyPolicyUrl = privacyPolicyUrl,
            RequestTimestamp = DateTime.UtcNow
        };
        
        var consentResponse = await consentUI.ShowConsentDialogAsync(consentRequest);
        
        if (consentResponse != null)
        {
            await RecordConsentAsync(playerId, consentResponse);
            return consentResponse.HasValidConsent();
        }
        
        return false;
    }
    
    public async Task RecordConsentAsync(string playerId, ConsentResponse response)
    {
        var consentRecord = new ConsentRecord
        {
            PlayerId = playerId,
            ConsentTimestamp = DateTime.UtcNow,
            ConsentVersion = "1.0",
            IPAddress = GetClientIP(),
            UserAgent = SystemInfo.operatingSystem,
            ProcessorConsents = response.ProcessorConsents,
            ConsentMethod = "in_game_dialog"
        };
        
        playerConsents[playerId] = consentRecord;
        
        // Store in database
        await DatabaseManager.Instance.SaveConsentRecordAsync(consentRecord);
        
        // Log consent event
        PrivacyLogger.Instance.LogConsentGranted(playerId, response.ProcessorConsents);
        
        // Configure analytics based on consent
        ConfigureAnalyticsConsent(response);
    }
    
    public bool HasValidConsent(string playerId, string processorId)
    {
        if (!playerConsents.ContainsKey(playerId))
            return false;
            
        var consent = playerConsents[playerId];
        
        // Check if consent has expired (GDPR recommends re-consent after 2 years)
        if (DateTime.UtcNow - consent.ConsentTimestamp > TimeSpan.FromDays(730))
            return false;
            
        return consent.ProcessorConsents.ContainsKey(processorId) && 
               consent.ProcessorConsents[processorId];
    }
    
    public async Task WithdrawConsentAsync(string playerId, string processorId)
    {
        if (playerConsents.ContainsKey(playerId))
        {
            var consent = playerConsents[playerId];
            consent.ProcessorConsents[processorId] = false;
            consent.ConsentWithdrawalTimestamp = DateTime.UtcNow;
            
            // Update database
            await DatabaseManager.Instance.UpdateConsentRecordAsync(consent);
            
            // Stop data processing for this processor
            await StopDataProcessingAsync(playerId, processorId);
            
            PrivacyLogger.Instance.LogConsentWithdrawn(playerId, processorId);
        }
    }
    
    private async Task StopDataProcessingAsync(string playerId, string processorId)
    {
        switch (processorId)
        {
            case "analytics":
                AnalyticsManager.Instance.DisableAnalytics(playerId);
                break;
            case "advertising":
                AdManager.Instance.DisableTargetedAds(playerId);
                break;
            case "crashlytics":
                // Cannot disable crash reporting as it's essential
                break;
        }
        
        // Queue data for deletion if required
        await QueueDataDeletionAsync(playerId, processorId);
    }
}
```

### Data Subject Rights Implementation
```csharp
// Data Subject Rights Handler
public class DataSubjectRightsManager : MonoBehaviour
{
    private DatabaseManager databaseManager;
    private FileStorageManager fileStorageManager;
    
    void Start()
    {
        databaseManager = DatabaseManager.Instance;
        fileStorageManager = FileStorageManager.Instance;
    }
    
    // Right to Access (Article 15)
    public async Task<PlayerDataExport> ExportPlayerDataAsync(string playerId)
    {
        var dataExport = new PlayerDataExport
        {
            PlayerId = playerId,
            ExportTimestamp = DateTime.UtcNow,
            ExportId = Guid.NewGuid().ToString()
        };
        
        try
        {
            // Collect all player data from various sources
            dataExport.ProfileData = await databaseManager.GetPlayerProfileAsync(playerId);
            dataExport.GameplayData = await databaseManager.GetPlayerGameplayDataAsync(playerId);
            dataExport.InventoryData = await databaseManager.GetPlayerInventoryAsync(playerId);
            dataExport.AchievementData = await databaseManager.GetPlayerAchievementsAsync(playerId);
            dataExport.TransactionData = await databaseManager.GetPlayerTransactionsAsync(playerId);
            dataExport.ConsentRecords = await databaseManager.GetPlayerConsentHistoryAsync(playerId);
            dataExport.AnalyticsData = await AnalyticsManager.Instance.GetPlayerAnalyticsDataAsync(playerId);
            dataExport.CommunicationData = await databaseManager.GetPlayerCommunicationsAsync(playerId);
            
            // Include metadata about data processing
            dataExport.DataProcessingInfo = GetDataProcessingInfo(playerId);
            
            // Generate human-readable format
            var exportJson = JsonConvert.SerializeObject(dataExport, Formatting.Indented);
            
            // Store export file securely
            var exportPath = await fileStorageManager.StorePlayerExportAsync(playerId, exportJson);
            dataExport.ExportFilePath = exportPath;
            
            // Log data access request
            PrivacyLogger.Instance.LogDataAccessRequest(playerId, dataExport.ExportId);
            
            return dataExport;
        }
        catch (Exception ex)
        {
            Debug.LogError($"Failed to export player data: {ex.Message}");
            throw;
        }
    }
    
    // Right to Rectification (Article 16)
    public async Task<bool> UpdatePlayerDataAsync(string playerId, PlayerDataUpdate updateRequest)
    {
        try
        {
            // Validate update request
            if (!ValidateDataUpdateRequest(updateRequest))
            {
                return false;
            }
            
            // Log original data for audit trail
            var originalData = await databaseManager.GetPlayerProfileAsync(playerId);
            await PrivacyLogger.Instance.LogDataRectificationRequestAsync(playerId, originalData, updateRequest);
            
            // Apply updates
            if (updateRequest.ProfileUpdates != null)
            {
                await databaseManager.UpdatePlayerProfileAsync(playerId, updateRequest.ProfileUpdates);
            }
            
            if (updateRequest.PreferenceUpdates != null)
            {
                await databaseManager.UpdatePlayerPreferencesAsync(playerId, updateRequest.PreferenceUpdates);
            }
            
            // Update timestamp
            await databaseManager.UpdatePlayerLastModifiedAsync(playerId, DateTime.UtcNow);
            
            return true;
        }
        catch (Exception ex)
        {
            Debug.LogError($"Failed to update player data: {ex.Message}");
            return false;
        }
    }
    
    // Right to Erasure (Article 17) - "Right to be Forgotten"
    public async Task<DataDeletionResult> DeletePlayerDataAsync(string playerId, DataDeletionRequest request)
    {
        var result = new DataDeletionResult
        {
            PlayerId = playerId,
            RequestId = Guid.NewGuid().ToString(),
            RequestTimestamp = DateTime.UtcNow
        };
        
        try
        {
            // Check if deletion is legally required or allowed
            var deletionValidation = await ValidateDataDeletionRequestAsync(playerId, request);
            if (!deletionValidation.IsValid)
            {
                result.Success = false;
                result.Reason = deletionValidation.Reason;
                return result;
            }
            
            // Create backup before deletion (for audit purposes)
            var backupExport = await ExportPlayerDataAsync(playerId);
            result.BackupExportId = backupExport.ExportId;
            
            // Begin deletion process
            var deletionTasks = new List<Task<bool>>();
            
            if (request.DeleteProfile)
            {
                deletionTasks.Add(databaseManager.DeletePlayerProfileAsync(playerId));
            }
            
            if (request.DeleteGameplayData)
            {
                deletionTasks.Add(databaseManager.DeletePlayerGameplayDataAsync(playerId));
            }
            
            if (request.DeleteAnalyticsData)
            {
                deletionTasks.Add(AnalyticsManager.Instance.DeletePlayerAnalyticsAsync(playerId));
            }
            
            if (request.DeleteCommunications)
            {
                deletionTasks.Add(databaseManager.DeletePlayerCommunicationsAsync(playerId));
            }
            
            // Execute deletions
            var deletionResults = await Task.WhenAll(deletionTasks);
            result.Success = deletionResults.All(r => r);
            
            if (result.Success)
            {
                // Mark account as deleted but keep audit trail
                await databaseManager.MarkPlayerAccountDeletedAsync(playerId, DateTime.UtcNow);
                
                // Log deletion completion
                await PrivacyLogger.Instance.LogDataDeletionCompletedAsync(playerId, request, result);
            }
            
            result.CompletionTimestamp = DateTime.UtcNow;
            return result;
        }
        catch (Exception ex)
        {
            Debug.LogError($"Failed to delete player data: {ex.Message}");
            result.Success = false;
            result.Reason = ex.Message;
            return result;
        }
    }
    
    // Right to Data Portability (Article 20)
    public async Task<DataPortabilityExport> CreatePortableDataExportAsync(string playerId)
    {
        var export = new DataPortabilityExport
        {
            PlayerId = playerId,
            ExportTimestamp = DateTime.UtcNow,
            Format = "JSON",
            Schema = "GameDataPortability_v1.0"
        };
        
        // Export data in standardized, machine-readable format
        export.StructuredData = new Dictionary<string, object>
        {
            ["player_profile"] = await databaseManager.GetPortablePlayerProfileAsync(playerId),
            ["achievements"] = await databaseManager.GetPortableAchievementsAsync(playerId),
            ["statistics"] = await databaseManager.GetPortableStatisticsAsync(playerId),
            ["preferences"] = await databaseManager.GetPortablePreferencesAsync(playerId),
            ["game_progress"] = await databaseManager.GetPortableGameProgressAsync(playerId)
        };
        
        // Include schema information for data interpretation
        export.SchemaInformation = GetDataPortabilitySchema();
        
        return export;
    }
}
```

## 🔧 Encryption and Secure Storage

### Data Encryption Implementation
```csharp
// Advanced Encryption Service for Game Data
using System.Security.Cryptography;

public class GameDataEncryption : MonoBehaviour
{
    [Header("Encryption Settings")]
    [SerializeField] private EncryptionLevel defaultEncryptionLevel = EncryptionLevel.High;
    
    private readonly Dictionary<EncryptionLevel, EncryptionConfig> encryptionConfigs;
    
    public GameDataEncryption()
    {
        encryptionConfigs = new Dictionary<EncryptionLevel, EncryptionConfig>
        {
            [EncryptionLevel.Low] = new EncryptionConfig
            {
                Algorithm = "AES-128-GCM",
                KeySize = 128,
                Iterations = 1000
            },
            [EncryptionLevel.Medium] = new EncryptionConfig
            {
                Algorithm = "AES-256-GCM",
                KeySize = 256,
                Iterations = 10000
            },
            [EncryptionLevel.High] = new EncryptionConfig
            {
                Algorithm = "AES-256-GCM",
                KeySize = 256,
                Iterations = 100000
            }
        };
    }
    
    public EncryptedData EncryptSensitiveData(string plaintext, string playerId, 
        DataSensitivityLevel sensitivity = DataSensitivityLevel.Personal)
    {
        var encryptionLevel = GetEncryptionLevelForSensitivity(sensitivity);
        var config = encryptionConfigs[encryptionLevel];
        
        // Generate unique encryption key for this data
        var masterKey = GetOrCreatePlayerMasterKey(playerId);
        var dataKey = DeriveDataKey(masterKey, plaintext.GetHashCode().ToString(), config.Iterations);
        
        using (var aesGcm = new AesGcm(dataKey))
        {
            var plaintextBytes = Encoding.UTF8.GetBytes(plaintext);
            var nonce = new byte[12]; // GCM standard nonce size
            var ciphertext = new byte[plaintextBytes.Length];
            var tag = new byte[16]; // GCM authentication tag
            
            // Generate random nonce
            using (var rng = RandomNumberGenerator.Create())
            {
                rng.GetBytes(nonce);
            }
            
            // Encrypt and authenticate
            aesGcm.Encrypt(nonce, plaintextBytes, ciphertext, tag);
            
            return new EncryptedData
            {
                EncryptionMethod = config.Algorithm,
                EncryptionLevel = encryptionLevel,
                Nonce = Convert.ToBase64String(nonce),
                Ciphertext = Convert.ToBase64String(ciphertext),
                AuthenticationTag = Convert.ToBase64String(tag),
                KeyDerivationInfo = new KeyDerivationInfo
                {
                    Iterations = config.Iterations,
                    Salt = GenerateRandomSalt(),
                    Algorithm = "PBKDF2-SHA256"
                },
                EncryptionTimestamp = DateTime.UtcNow
            };
        }
    }
    
    public string DecryptSensitiveData(EncryptedData encryptedData, string playerId)
    {
        try
        {
            var masterKey = GetOrCreatePlayerMasterKey(playerId);
            var dataKey = DeriveDataKey(masterKey, encryptedData.GetHashCode().ToString(), 
                encryptedData.KeyDerivationInfo.Iterations);
            
            using (var aesGcm = new AesGcm(dataKey))
            {
                var nonce = Convert.FromBase64String(encryptedData.Nonce);
                var ciphertext = Convert.FromBase64String(encryptedData.Ciphertext);
                var tag = Convert.FromBase64String(encryptedData.AuthenticationTag);
                var plaintext = new byte[ciphertext.Length];
                
                // Decrypt and verify authentication
                aesGcm.Decrypt(nonce, ciphertext, tag, plaintext);
                
                return Encoding.UTF8.GetString(plaintext);
            }
        }
        catch (CryptographicException ex)
        {
            Debug.LogError($"Decryption failed: {ex.Message}");
            SecurityLogger.Instance.LogDecryptionFailure(playerId, encryptedData.EncryptionMethod);
            throw new SecurityException("Data decryption failed - possible tampering detected");
        }
    }
    
    private byte[] GetOrCreatePlayerMasterKey(string playerId)
    {
        // In production, this should be retrieved from secure key management service
        var keyIdentifier = $"player_master_key_{playerId}";
        
        // Check if key exists in secure storage
        var existingKey = SecureKeyStore.Instance.GetKey(keyIdentifier);
        if (existingKey != null)
        {
            return existingKey;
        }
        
        // Generate new master key
        var masterKey = new byte[32]; // 256-bit key
        using (var rng = RandomNumberGenerator.Create())
        {
            rng.GetBytes(masterKey);
        }
        
        // Store securely
        SecureKeyStore.Instance.StoreKey(keyIdentifier, masterKey);
        
        return masterKey;
    }
    
    private byte[] DeriveDataKey(byte[] masterKey, string context, int iterations)
    {
        var salt = Encoding.UTF8.GetBytes($"GameDataKey_{context}");
        
        using (var pbkdf2 = new Rfc2898DeriveBytes(masterKey, salt, iterations, HashAlgorithmName.SHA256))
        {
            return pbkdf2.GetBytes(32); // 256-bit derived key
        }
    }
    
    private EncryptionLevel GetEncryptionLevelForSensitivity(DataSensitivityLevel sensitivity)
    {
        return sensitivity switch
        {
            DataSensitivityLevel.Public => EncryptionLevel.Low,
            DataSensitivityLevel.Internal => EncryptionLevel.Medium,
            DataSensitivityLevel.Personal => EncryptionLevel.High,
            DataSensitivityLevel.Sensitive => EncryptionLevel.High,
            _ => defaultEncryptionLevel
        };
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Privacy Policy Generation
```
Prompt: "Generate a comprehensive GDPR-compliant privacy policy for a Unity multiplayer RPG game that includes data collection practices, consent management, player rights, data retention policies, and third-party integrations."
```

### Data Protection Impact Assessment
```
Prompt: "Create a Data Protection Impact Assessment (DPIA) template for Unity game development projects, including privacy risk evaluation, mitigation strategies, and compliance monitoring procedures."
```

### Consent Management UI
```
Prompt: "Design a user-friendly consent management interface for Unity mobile games that clearly explains data processing purposes, allows granular consent control, and meets GDPR transparency requirements."
```

## 💡 Key Highlights

### GDPR Compliance Essentials
- **Lawful basis**: Establish valid legal grounds for data processing
- **Explicit consent**: Clear, specific, and freely given consent
- **Data minimization**: Collect only necessary data for stated purposes
- **Purpose limitation**: Use data only for declared purposes
- **Transparency**: Clear information about data processing activities

### Data Subject Rights Implementation
- **Right to access**: Provide complete data exports within 30 days
- **Right to rectification**: Allow data correction and updates
- **Right to erasure**: Implement "right to be forgotten" functionality
- **Right to portability**: Export data in machine-readable format
- **Right to object**: Allow opt-out from data processing

### Security and Privacy by Design
- **Data encryption**: Protect sensitive data at rest and in transit
- **Access controls**: Limit data access to authorized personnel only
- **Audit logging**: Track all data access and modification activities
- **Data retention**: Automatically delete data after retention periods
- **Privacy impact assessments**: Evaluate privacy risks for new features