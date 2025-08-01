# 01-Unity-Security-Implementation.md

## 🎯 Learning Objectives
- Master Unity-specific security vulnerabilities and mitigation strategies
- Implement secure data handling and network communication in Unity games
- Apply security best practices for Unity deployment and distribution
- Develop secure authentication and anti-cheat systems for Unity multiplayer games

## 🔧 Unity Security Fundamentals

### Code Obfuscation and Protection
```csharp
// Unity Security Manager - Centralized security handling
public class GameSecurityManager : MonoBehaviour
{
    [Header("Security Configuration")]
    [SerializeField] private bool enableDebugProtection = true;
    [SerializeField] private bool enableCheatDetection = true;
    [SerializeField] private float integrityCheckInterval = 30f;
    
    private Dictionary<string, string> secureHashes;
    private bool isSecurityCompromised = false;
    
    private void Awake()
    {
        // Prevent running in debug mode in production
        if (enableDebugProtection && Debug.isDebugBuild)
        {
            HandleSecurityViolation("Debug build detected in production");
            return;
        }
        
        InitializeSecurityHashes();
        StartCoroutine(PeriodicIntegrityCheck());
    }
    
    private void InitializeSecurityHashes()
    {
        secureHashes = new Dictionary<string, string>
        {
            {"PlayerStats", ComputeHash(PlayerStats.Instance.ToString())},
            {"GameConfig", ComputeHash(GameConfig.Instance.ToString())},
            {"Currency", ComputeHash(CurrencyManager.Instance.GetBalance().ToString())}
        };
    }
    
    private string ComputeHash(string input)
    {
        using (var sha256 = System.Security.Cryptography.SHA256.Create())
        {
            byte[] hashedBytes = sha256.ComputeHash(System.Text.Encoding.UTF8.GetBytes(input));
            return System.Convert.ToBase64String(hashedBytes);
        }
    }
    
    private IEnumerator PeriodicIntegrityCheck()
    {
        while (!isSecurityCompromised)
        {
            yield return new WaitForSeconds(integrityCheckInterval);
            
            if (enableCheatDetection)
            {
                ValidateDataIntegrity();
                DetectSpeedHacking();
                ValidatePlayerPosition();
            }
        }
    }
    
    private void ValidateDataIntegrity()
    {
        string currentStatsHash = ComputeHash(PlayerStats.Instance.ToString());
        if (secureHashes["PlayerStats"] != currentStatsHash)
        {
            // Check if change was legitimate (through proper game systems)
            if (!PlayerStats.Instance.WasLastChangeValid())
            {
                HandleSecurityViolation("Player stats tampering detected");
            }
            else
            {
                secureHashes["PlayerStats"] = currentStatsHash;
            }
        }
    }
    
    private void DetectSpeedHacking()
    {
        float currentSpeed = PlayerMovement.Instance.GetCurrentSpeed();
        float maxAllowedSpeed = PlayerMovement.Instance.GetMaxSpeed() * 1.1f; // 10% tolerance
        
        if (currentSpeed > maxAllowedSpeed)
        {
            HandleSecurityViolation($"Speed hacking detected: {currentSpeed} > {maxAllowedSpeed}");
        }
    }
    
    private void HandleSecurityViolation(string violation)
    {
        Debug.LogError($"Security Violation: {violation}");
        isSecurityCompromised = true;
        
        // Implement your security response (disconnect, ban, reset, etc.)
        NetworkManager.Instance?.DisconnectPlayer("Security violation");
        
        // Log to analytics for monitoring
        AnalyticsManager.Instance?.LogSecurityEvent(violation);
    }
}
```

### Secure Data Storage and Encryption
```csharp
// Secure PlayerPrefs implementation with encryption
public static class SecurePlayerPrefs
{
    private static readonly string encryptionKey = GenerateDeviceSpecificKey();
    
    private static string GenerateDeviceSpecificKey()
    {
        // Generate key based on device-specific information
        string deviceInfo = $"{SystemInfo.deviceUniqueIdentifier}_{Application.version}";
        return ComputeHash(deviceInfo).Substring(0, 32); // AES-256 requires 32-byte key
    }
    
    public static void SetSecureString(string key, string value)
    {
        string encryptedValue = EncryptString(value, encryptionKey);
        PlayerPrefs.SetString($"secure_{key}", encryptedValue);
        PlayerPrefs.Save();
    }
    
    public static string GetSecureString(string key, string defaultValue = "")
    {
        string encryptedValue = PlayerPrefs.GetString($"secure_{key}", "");
        if (string.IsNullOrEmpty(encryptedValue))
            return defaultValue;
            
        try
        {
            return DecryptString(encryptedValue, encryptionKey);
        }
        catch
        {
            // If decryption fails, return default and clear corrupted data
            PlayerPrefs.DeleteKey($"secure_{key}");
            return defaultValue;
        }
    }
    
    public static void SetSecureInt(string key, int value)
    {
        SetSecureString(key, value.ToString());
    }
    
    public static int GetSecureInt(string key, int defaultValue = 0)
    {
        string stringValue = GetSecureString(key, defaultValue.ToString());
        return int.TryParse(stringValue, out int result) ? result : defaultValue;
    }
    
    private static string EncryptString(string plainText, string key)
    {
        using (Aes aes = Aes.Create())
        {
            aes.Key = System.Text.Encoding.UTF8.GetBytes(key);
            aes.GenerateIV();
            
            ICryptoTransform encryptor = aes.CreateEncryptor();
            byte[] plainBytes = System.Text.Encoding.UTF8.GetBytes(plainText);
            byte[] encryptedBytes = encryptor.TransformFinalBlock(plainBytes, 0, plainBytes.Length);
            
            // Combine IV and encrypted data
            byte[] result = new byte[aes.IV.Length + encryptedBytes.Length];
            System.Array.Copy(aes.IV, 0, result, 0, aes.IV.Length);
            System.Array.Copy(encryptedBytes, 0, result, aes.IV.Length, encryptedBytes.Length);
            
            return System.Convert.ToBase64String(result);
        }
    }
    
    private static string DecryptString(string cipherText, string key)
    {
        byte[] cipherBytes = System.Convert.FromBase64String(cipherText);
        
        using (Aes aes = Aes.Create())
        {
            aes.Key = System.Text.Encoding.UTF8.GetBytes(key);
            
            // Extract IV from the beginning of cipher text
            byte[] iv = new byte[aes.IV.Length];
            byte[] encrypted = new byte[cipherBytes.Length - iv.Length];
            
            System.Array.Copy(cipherBytes, 0, iv, 0, iv.Length);
            System.Array.Copy(cipherBytes, iv.Length, encrypted, 0, encrypted.Length);
            
            aes.IV = iv;
            
            ICryptoTransform decryptor = aes.CreateDecryptor();
            byte[] decryptedBytes = decryptor.TransformFinalBlock(encrypted, 0, encrypted.Length);
            
            return System.Text.Encoding.UTF8.GetString(decryptedBytes);
        }
    }
    
    private static string ComputeHash(string input)
    {
        using (var sha256 = System.Security.Cryptography.SHA256.Create())
        {
            byte[] hashedBytes = sha256.ComputeHash(System.Text.Encoding.UTF8.GetBytes(input));
            return System.Convert.ToBase64String(hashedBytes);
        }
    }
}
```

### Network Security and Anti-Cheat
```csharp
// Secure network communication with validation
public class SecureNetworkManager : NetworkBehaviour
{
    [Header("Security Settings")]
    [SerializeField] private float maxCommandsPerSecond = 10f;
    [SerializeField] private bool enableServerValidation = true;
    [SerializeField] private float positionValidationTolerance = 2f;
    
    private Dictionary<uint, CommandRateTracker> clientCommandRates;
    private Dictionary<uint, Vector3> lastValidatedPositions;
    
    private struct CommandRateTracker
    {
        public float lastResetTime;
        public int commandCount;
    }
    
    [Server]
    public override void OnStartServer()
    {
        clientCommandRates = new Dictionary<uint, CommandRateTracker>();
        lastValidatedPositions = new Dictionary<uint, Vector3>();
    }
    
    [Command]
    public void CmdMovePlayer(Vector3 newPosition, float timestamp)
    {
        uint clientId = connectionToClient.connectionId;
        
        // Rate limiting
        if (!ValidateCommandRate(clientId))
        {
            KickPlayer(clientId, "Command rate limit exceeded");
            return;
        }
        
        // Timestamp validation to prevent replay attacks
        if (!ValidateTimestamp(timestamp))
        {
            KickPlayer(clientId, "Invalid timestamp");
            return;
        }
        
        // Position validation
        if (enableServerValidation && !ValidatePosition(clientId, newPosition))
        {
            KickPlayer(clientId, "Invalid position");
            return;
        }
        
        // Apply movement
        transform.position = newPosition;
        lastValidatedPositions[clientId] = newPosition;
        
        // Broadcast to other clients
        RpcUpdatePlayerPosition(newPosition);
    }
    
    private bool ValidateCommandRate(uint clientId)
    {
        float currentTime = Time.time;
        
        if (!clientCommandRates.ContainsKey(clientId))
        {
            clientCommandRates[clientId] = new CommandRateTracker
            {
                lastResetTime = currentTime,
                commandCount = 1
            };
            return true;
        }
        
        var tracker = clientCommandRates[clientId];
        
        // Reset counter every second
        if (currentTime - tracker.lastResetTime >= 1f)
        {
            tracker.lastResetTime = currentTime;
            tracker.commandCount = 1;
            clientCommandRates[clientId] = tracker;
            return true;
        }
        
        tracker.commandCount++;
        clientCommandRates[clientId] = tracker;
        
        return tracker.commandCount <= maxCommandsPerSecond;
    }
    
    private bool ValidateTimestamp(float timestamp)
    {
        float serverTime = Time.time;
        float timeDifference = Mathf.Abs(serverTime - timestamp);
        
        // Allow reasonable network latency tolerance (500ms)
        return timeDifference <= 0.5f;
    }
    
    private bool ValidatePosition(uint clientId, Vector3 newPosition)
    {
        if (!lastValidatedPositions.ContainsKey(clientId))
        {
            return true; // First position is always valid
        }
        
        Vector3 lastPosition = lastValidatedPositions[clientId];
        float distance = Vector3.Distance(lastPosition, newPosition);
        float maxDistance = GetMaxMovementDistance(clientId);
        
        return distance <= maxDistance + positionValidationTolerance;
    }
    
    private float GetMaxMovementDistance(uint clientId)
    {
        // Calculate based on player's movement speed and time elapsed
        PlayerController player = GetPlayerController(clientId);
        if (player == null) return 0f;
        
        float maxSpeed = player.GetMaxSpeed();
        float timeSinceLastUpdate = Time.fixedDeltaTime;
        
        return maxSpeed * timeSinceLastUpdate;
    }
    
    private void KickPlayer(uint clientId, string reason)
    {
        Debug.LogWarning($"Kicking player {clientId}: {reason}");
        
        // Log security violation
        AnalyticsManager.Instance?.LogSecurityEvent($"Player kicked: {reason}");
        
        // Disconnect the client
        NetworkServer.connections[clientId]?.Disconnect();
    }
    
    [ClientRpc]
    private void RpcUpdatePlayerPosition(Vector3 position)
    {
        // Update position on all clients
        transform.position = position;
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Security Code Review Automation
```
PROMPT TEMPLATE - Security Code Review:

"Review this Unity C# code for security vulnerabilities:

```csharp
[PASTE YOUR CODE HERE]
```

Focus on:
1. Input validation and sanitization
2. Authentication and authorization flaws
3. Data encryption and storage security
4. Network communication vulnerabilities
5. Anti-cheat bypass possibilities
6. Memory management and buffer overflows
7. Information disclosure risks

Provide specific recommendations with Unity-focused solutions and code examples for fixes."
```

### Automated Security Testing Scenarios
```
PROMPT TEMPLATE - Security Test Generation:

"Generate comprehensive security test scenarios for this Unity game feature:

Feature: [DESCRIBE YOUR FEATURE]
Network Type: [Local/Online Multiplayer/Single Player]
Data Sensitivity: [High/Medium/Low]

Generate tests for:
1. Authentication bypass attempts
2. Data tampering scenarios
3. Network packet manipulation
4. Client-side validation bypass
5. Resource exhaustion attacks
6. Privilege escalation attempts

Include Unity-specific test implementations using NUnit framework."
```

## 💡 Key Security Principles for Unity Development

### Essential Security Checklist
- **Never trust client input** - Always validate on server
- **Encrypt sensitive data** - Use proper encryption for save files and network traffic
- **Implement rate limiting** - Prevent spam and DoS attacks
- **Use server-side validation** - Critical game logic should run on server
- **Secure API endpoints** - Authenticate and authorize all API calls
- **Monitor for anomalies** - Detect unusual player behavior patterns
- **Regular security audits** - Review code and infrastructure regularly
- **Principle of least privilege** - Give minimal necessary permissions

### Common Unity Security Vulnerabilities
1. **Client-side currency/score manipulation**
2. **Unencrypted save file tampering**
3. **Network packet injection/modification**
4. **Memory editing and value manipulation**
5. **Asset bundle injection attacks**
6. **Debug information exposure**
7. **Insecure random number generation**
8. **Authentication token mismanagement**

### Unity-Specific Security Tools
- **Unity Cloud Build** - Secure build pipeline management
- **Unity Analytics** - Monitor for suspicious player behavior
- **Unity Netcode** - Built-in network security features
- **Code obfuscation tools** - Protect against reverse engineering
- **Asset encryption** - Secure game assets and content

This comprehensive security implementation provides Unity developers with practical, production-ready security solutions that protect against common game development vulnerabilities while maintaining performance and user experience.