# @a-Unity-Game-Security-Fundamentals

## 🎯 Learning Objectives
- Implement comprehensive security measures for Unity games
- Protect against common game exploits and cheating methods
- Secure client-server communication and data transmission
- Design anti-cheat systems and server-side validation

## 🔧 Client-Side Security Foundations

### Code Obfuscation and Protection
```csharp
// Secure PlayerPrefs Alternative
using System.Security.Cryptography;
using System.Text;
using UnityEngine;

public static class SecurePlayerPrefs
{
    private static readonly string encryptionKey = SystemInfo.deviceUniqueIdentifier + "UnityGame";
    
    public static void SetSecureString(string key, string value)
    {
        string encryptedValue = EncryptString(value, encryptionKey);
        PlayerPrefs.SetString(GetHashedKey(key), encryptedValue);
    }
    
    public static string GetSecureString(string key, string defaultValue = "")
    {
        string hashedKey = GetHashedKey(key);
        if (!PlayerPrefs.HasKey(hashedKey))
            return defaultValue;
            
        string encryptedValue = PlayerPrefs.GetString(hashedKey);
        return DecryptString(encryptedValue, encryptionKey);
    }
    
    public static void SetSecureInt(string key, int value)
    {
        SetSecureString(key, value.ToString());
    }
    
    public static int GetSecureInt(string key, int defaultValue = 0)
    {
        string value = GetSecureString(key, defaultValue.ToString());
        return int.TryParse(value, out int result) ? result : defaultValue;
    }
    
    private static string EncryptString(string plaintext, string password)
    {
        byte[] plaintextBytes = Encoding.UTF8.GetBytes(plaintext);
        using (Aes aes = Aes.Create())
        {
            byte[] key = new Rfc2898DeriveBytes(password, new byte[] { 
                0x49, 0x76, 0x61, 0x6e, 0x20, 0x4d, 0x65, 0x64, 
                0x76, 0x65, 0x64, 0x65, 0x76 }, 1000).GetBytes(32);
            aes.Key = key;
            aes.GenerateIV();
            
            using (var encryptor = aes.CreateEncryptor(aes.Key, aes.IV))
            {
                byte[] encryptedBytes = encryptor.TransformFinalBlock(plaintextBytes, 0, plaintextBytes.Length);
                byte[] result = new byte[aes.IV.Length + encryptedBytes.Length];
                Buffer.BlockCopy(aes.IV, 0, result, 0, aes.IV.Length);
                Buffer.BlockCopy(encryptedBytes, 0, result, aes.IV.Length, encryptedBytes.Length);
                return System.Convert.ToBase64String(result);
            }
        }
    }
    
    private static string DecryptString(string ciphertext, string password)
    {
        byte[] ciphertextBytes = System.Convert.FromBase64String(ciphertext);
        using (Aes aes = Aes.Create())
        {
            byte[] key = new Rfc2898DeriveBytes(password, new byte[] { 
                0x49, 0x76, 0x61, 0x6e, 0x20, 0x4d, 0x65, 0x64, 
                0x76, 0x65, 0x64, 0x65, 0x76 }, 1000).GetBytes(32);
            aes.Key = key;
            
            byte[] iv = new byte[aes.IV.Length];
            byte[] encrypted = new byte[ciphertextBytes.Length - iv.Length];
            Buffer.BlockCopy(ciphertextBytes, 0, iv, 0, iv.Length);
            Buffer.BlockCopy(ciphertextBytes, iv.Length, encrypted, 0, encrypted.Length);
            aes.IV = iv;
            
            using (var decryptor = aes.CreateDecryptor(aes.Key, aes.IV))
            {
                byte[] decryptedBytes = decryptor.TransformFinalBlock(encrypted, 0, encrypted.Length);
                return Encoding.UTF8.GetString(decryptedBytes);
            }
        }
    }
    
    private static string GetHashedKey(string key)
    {
        using (SHA256 sha256 = SHA256.Create())
        {
            byte[] hashedBytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(key + encryptionKey));
            return System.Convert.ToBase64String(hashedBytes);
        }
    }
}
```

### Anti-Tampering Measures
```csharp
// Runtime Integrity Checking
public class SecurityManager : MonoBehaviour
{
    [SerializeField] private bool enableRuntimeChecks = true;
    [SerializeField] private float checkInterval = 30f;
    
    private Dictionary<string, string> criticalFileHashes;
    private float lastCheckTime;
    
    void Start()
    {
        if (enableRuntimeChecks)
        {
            InitializeSecurityChecks();
            InvokeRepeating(nameof(PerformSecurityChecks), checkInterval, checkInterval);
        }
    }
    
    private void InitializeSecurityChecks()
    {
        criticalFileHashes = new Dictionary<string, string>();
        
        // Hash critical game files
        string[] criticalFiles = {
            "GameData/player_stats.json",
            "GameData/item_definitions.json",
            "GameData/economy_settings.json"
        };
        
        foreach (var file in criticalFiles)
        {
            if (File.Exists(Path.Combine(Application.streamingAssetsPath, file)))
            {
                criticalFileHashes[file] = CalculateFileHash(file);
            }
        }
    }
    
    private void PerformSecurityChecks()
    {
        // Check for debugger attachment
        if (System.Diagnostics.Debugger.IsAttached)
        {
            HandleSecurityViolation("Debugger detected");
            return;
        }
        
        // Check system time manipulation
        if (IsSystemTimeManipulated())
        {
            HandleSecurityViolation("System time manipulation detected");
            return;
        }
        
        // Check file integrity
        foreach (var kvp in criticalFileHashes)
        {
            string currentHash = CalculateFileHash(kvp.Key);
            if (currentHash != kvp.Value)
            {
                HandleSecurityViolation($"File tampering detected: {kvp.Key}");
                return;
            }
        }
        
        // Check memory modification (basic)
        if (IsMemoryModified())
        {
            HandleSecurityViolation("Memory modification detected");
            return;
        }
        
        lastCheckTime = Time.time;
    }
    
    private bool IsSystemTimeManipulated()
    {
        // Compare system time with server time
        var serverTime = GetServerTime();
        var systemTime = DateTime.UtcNow;
        
        if (serverTime.HasValue)
        {
            var timeDifference = Math.Abs((serverTime.Value - systemTime).TotalMinutes);
            return timeDifference > 5; // Allow 5 minutes tolerance
        }
        
        return false;
    }
    
    private bool IsMemoryModified()
    {
        // Basic check for common memory editing tools
        Process[] processes = Process.GetProcesses();
        string[] suspiciousProcesses = {
            "cheatengine", "artmoney", "gamecih", "gameguardian",
            "memoryeditor", "gamemaker", "speedhack"
        };
        
        foreach (var process in processes)
        {
            foreach (var suspicious in suspiciousProcesses)
            {
                if (process.ProcessName.ToLower().Contains(suspicious))
                {
                    return true;
                }
            }
        }
        
        return false;
    }
    
    private void HandleSecurityViolation(string violation)
    {
        Debug.LogWarning($"Security violation detected: {violation}");
        
        // Log to analytics
        AnalyticsManager.Instance.TrackSecurityViolation(violation);
        
        // Graceful degradation instead of immediate shutdown
        GameManager.Instance.EnableSecureMode();
        
        // Optionally disconnect from server
        if (NetworkManager.Instance.IsConnected)
        {
            NetworkManager.Instance.DisconnectWithReason("Security check failed");
        }
    }
}
```

## 🔧 Server-Side Validation Systems

### Input Validation and Sanitization
```csharp
// Server-Side Player Action Validator
public class PlayerActionValidator
{
    private readonly Dictionary<string, DateTime> lastActionTimes;
    private readonly Dictionary<string, ActionLimits> actionLimits;
    
    public PlayerActionValidator()
    {
        lastActionTimes = new Dictionary<string, DateTime>();
        actionLimits = new Dictionary<string, ActionLimits>
        {
            { "MOVE", new ActionLimits { MaxPerSecond = 60, CooldownMs = 0 } },
            { "ATTACK", new ActionLimits { MaxPerSecond = 5, CooldownMs = 200 } },
            { "CAST_SPELL", new ActionLimits { MaxPerSecond = 2, CooldownMs = 500 } },
            { "USE_ITEM", new ActionLimits { MaxPerSecond = 10, CooldownMs = 100 } },
            { "CHAT", new ActionLimits { MaxPerSecond = 1, CooldownMs = 1000 } }
        };
    }
    
    public ValidationResult ValidatePlayerAction(string playerId, PlayerAction action)
    {
        var result = new ValidationResult { IsValid = true };
        
        // Check action type validity
        if (!actionLimits.ContainsKey(action.ActionType))
        {
            result.IsValid = false;
            result.Reason = "Invalid action type";
            return result;
        }
        
        // Rate limiting check
        if (!IsActionAllowed(playerId, action.ActionType))
        {
            result.IsValid = false;
            result.Reason = "Action rate limit exceeded";
            return result;
        }
        
        // Validate action parameters
        switch (action.ActionType)
        {
            case "MOVE":
                result = ValidateMovement(playerId, action);
                break;
            case "ATTACK":
                result = ValidateAttack(playerId, action);
                break;
            case "CAST_SPELL":
                result = ValidateSpellCast(playerId, action);
                break;
            case "USE_ITEM":
                result = ValidateItemUsage(playerId, action);
                break;
        }
        
        if (result.IsValid)
        {
            UpdateActionHistory(playerId, action.ActionType);
        }
        
        return result;
    }
    
    private ValidationResult ValidateMovement(string playerId, PlayerAction action)
    {
        var result = new ValidationResult { IsValid = true };
        
        // Get player's current position from server state
        var currentPosition = GetPlayerPosition(playerId);
        var targetPosition = action.GetVector3Parameter("position");
        
        // Check movement distance
        float distance = Vector3.Distance(currentPosition, targetPosition);
        float maxMovementPerTick = GetPlayerMaxSpeed(playerId) * Time.fixedDeltaTime;
        
        if (distance > maxMovementPerTick * 1.5f) // Allow some tolerance
        {
            result.IsValid = false;
            result.Reason = "Movement distance exceeds maximum allowed";
            LogSuspiciousActivity(playerId, "Excessive movement distance", distance);
        }
        
        // Check if position is within valid game bounds
        if (!IsPositionValid(targetPosition))
        {
            result.IsValid = false;
            result.Reason = "Invalid target position";
        }
        
        // Check for wall clipping
        if (IsWallClipping(currentPosition, targetPosition))
        {
            result.IsValid = false;
            result.Reason = "Wall clipping detected";
        }
        
        return result;
    }
    
    private ValidationResult ValidateAttack(string playerId, PlayerAction action)
    {
        var result = new ValidationResult { IsValid = true };
        
        var attackerId = playerId;
        var targetId = action.GetStringParameter("targetId");
        var damage = action.GetIntParameter("damage");
        
        // Validate target exists and is in range
        if (!IsValidAttackTarget(attackerId, targetId))
        {
            result.IsValid = false;
            result.Reason = "Invalid attack target";
            return result;
        }
        
        // Server-side damage calculation
        var serverCalculatedDamage = CalculateDamage(attackerId, targetId);
        var damageTolerance = serverCalculatedDamage * 0.1f; // 10% tolerance
        
        if (Math.Abs(damage - serverCalculatedDamage) > damageTolerance)
        {
            result.IsValid = false;
            result.Reason = "Damage calculation mismatch";
            LogSuspiciousActivity(playerId, "Damage manipulation", 
                $"Client: {damage}, Server: {serverCalculatedDamage}");
        }
        
        return result;
    }
}
```

### Anti-Cheat System Implementation
```csharp
// Comprehensive Anti-Cheat System
public class AntiCheatSystem : MonoBehaviour
{
    [Header("Detection Settings")]
    [SerializeField] private bool enableSpeedHackDetection = true;
    [SerializeField] private bool enableTeleportDetection = true;
    [SerializeField] private bool enableStatisticalAnalysis = true;
    
    private Dictionary<string, PlayerBehaviorProfile> playerProfiles;
    private Queue<GameEvent> recentEvents;
    
    void Start()
    {
        playerProfiles = new Dictionary<string, PlayerBehaviorProfile>();
        recentEvents = new Queue<GameEvent>();
        
        InvokeRepeating(nameof(PerformStatisticalAnalysis), 60f, 60f);
    }
    
    public void AnalyzePlayerAction(string playerId, PlayerAction action)
    {
        if (!playerProfiles.ContainsKey(playerId))
        {
            playerProfiles[playerId] = new PlayerBehaviorProfile(playerId);
        }
        
        var profile = playerProfiles[playerId];
        profile.RecordAction(action);
        
        // Speed hack detection
        if (enableSpeedHackDetection && action.ActionType == "MOVE")
        {
            CheckForSpeedHack(playerId, action, profile);
        }
        
        // Teleport detection
        if (enableTeleportDetection && action.ActionType == "MOVE")
        {
            CheckForTeleport(playerId, action, profile);
        }
        
        // Aim bot detection
        if (action.ActionType == "ATTACK")
        {
            CheckForAimBot(playerId, action, profile);
        }
        
        // Pattern analysis
        AnalyzeActionPatterns(playerId, profile);
    }
    
    private void CheckForSpeedHack(string playerId, PlayerAction action, PlayerBehaviorProfile profile)
    {
        var movements = profile.GetRecentActions("MOVE", 10);
        if (movements.Count < 5) return;
        
        float totalDistance = 0f;
        float totalTime = 0f;
        
        for (int i = 1; i < movements.Count; i++)
        {
            var prev = movements[i - 1];
            var curr = movements[i];
            
            var prevPos = prev.GetVector3Parameter("position");
            var currPos = curr.GetVector3Parameter("position");
            
            totalDistance += Vector3.Distance(prevPos, currPos);
            totalTime += (float)(curr.Timestamp - prev.Timestamp).TotalSeconds;
        }
        
        float averageSpeed = totalDistance / totalTime;
        float maxAllowedSpeed = GetPlayerMaxSpeed(playerId) * 1.2f; // 20% tolerance
        
        if (averageSpeed > maxAllowedSpeed)
        {
            var confidence = Mathf.Clamp01((averageSpeed - maxAllowedSpeed) / maxAllowedSpeed);
            ReportCheatSuspicion(playerId, CheatType.SpeedHack, confidence, 
                $"Speed: {averageSpeed:F2} (max: {maxAllowedSpeed:F2})");
        }
    }
    
    private void CheckForAimBot(string playerId, PlayerAction action, PlayerBehaviorProfile profile)
    {
        var attacks = profile.GetRecentActions("ATTACK", 20);
        if (attacks.Count < 10) return;
        
        int hits = 0;
        float totalAccuracy = 0f;
        List<float> accuracyValues = new List<float>();
        
        foreach (var attack in attacks)
        {
            bool isHit = attack.GetBoolParameter("hit");
            if (isHit)
            {
                hits++;
                float accuracy = attack.GetFloatParameter("accuracy");
                totalAccuracy += accuracy;
                accuracyValues.Add(accuracy);
            }
        }
        
        float hitRate = (float)hits / attacks.Count;
        float averageAccuracy = hits > 0 ? totalAccuracy / hits : 0f;
        
        // Calculate accuracy consistency (low variance suggests aimbot)
        float variance = 0f;
        if (accuracyValues.Count > 1)
        {
            float mean = accuracyValues.Average();
            variance = accuracyValues.Sum(x => Mathf.Pow(x - mean, 2)) / accuracyValues.Count;
        }
        
        // Suspicious if: high hit rate + high accuracy + low variance
        if (hitRate > 0.85f && averageAccuracy > 0.9f && variance < 0.01f)
        {
            var confidence = (hitRate + averageAccuracy + (1f - variance)) / 3f;
            ReportCheatSuspicion(playerId, CheatType.AimBot, confidence,
                $"Hit rate: {hitRate:P}, Accuracy: {averageAccuracy:P}, Variance: {variance:F4}");
        }
    }
    
    private void ReportCheatSuspicion(string playerId, CheatType cheatType, float confidence, string details)
    {
        var report = new CheatReport
        {
            PlayerId = playerId,
            CheatType = cheatType,
            Confidence = confidence,
            Details = details,
            Timestamp = DateTime.UtcNow,
            ServerInstance = Environment.MachineName
        };
        
        // Log locally
        Debug.LogWarning($"Cheat suspicion: {playerId} - {cheatType} (confidence: {confidence:P})");
        
        // Send to analytics/monitoring system
        SendCheatReportAsync(report);
        
        // Take automated action based on confidence
        if (confidence > 0.8f)
        {
            // High confidence - immediate action
            TakeAntiCheatAction(playerId, AntiCheatAction.TemporaryBan, cheatType);
        }
        else if (confidence > 0.6f)
        {
            // Medium confidence - increase monitoring
            IncreasePlayerMonitoring(playerId);
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Security Code Review
```
Prompt: "Review this Unity game security implementation for potential vulnerabilities, focusing on client-server communication, data validation, and anti-cheat measures: [paste code]"
```

### Threat Modeling Automation
```
Prompt: "Generate a comprehensive threat model for a Unity multiplayer RPG game, including attack vectors, risk assessments, and mitigation strategies for cheating, data breaches, and system compromise."
```

### Security Testing Scenarios
```
Prompt: "Create automated security test cases for Unity game anti-cheat systems, including speed hacking, memory modification, packet manipulation, and statistical anomaly detection."
```

## 💡 Key Highlights

### Defense in Depth Strategy
- **Client-side protection**: Code obfuscation, runtime checks, anti-tampering
- **Network security**: Encrypted communication, authentication, rate limiting
- **Server-side validation**: Authoritative game state, input validation
- **Behavioral analysis**: Statistical anomaly detection, pattern recognition
- **Monitoring & response**: Real-time threat detection, automated countermeasures

### Common Unity Game Vulnerabilities
- **Client-side trust**: Never trust client calculations for critical game state
- **Weak authentication**: Implement proper session management and token validation
- **Insecure storage**: Encrypt sensitive data, avoid plaintext credentials
- **Network packet manipulation**: Validate all incoming data server-side
- **Memory editing**: Implement runtime integrity checks and obfuscation

### Security Best Practices
- **Principle of least privilege**: Limit access to essential functions only
- **Fail securely**: Default to secure state when errors occur
- **Regular security audits**: Automated scanning and manual code review
- **Security by design**: Integrate security considerations from project start
- **Incident response**: Plan for breach detection and recovery procedures