# @b-Network-Security-Authentication

## 🎯 Learning Objectives
- Implement secure authentication systems for Unity multiplayer games
- Master JWT token management and session security
- Design secure network communication protocols
- Protect against common network-based attacks

## 🔧 Authentication System Architecture

### JWT-Based Authentication
```csharp
// Unity JWT Authentication Manager
using System.IdentityModel.Tokens.Jwt;
using Microsoft.IdentityModel.Tokens;
using System.Security.Claims;
using System.Text;
using UnityEngine;

public class JWTAuthenticationManager : MonoBehaviour
{
    [Header("JWT Configuration")]
    [SerializeField] private string secretKey = "your-super-secret-key-here-make-it-long-and-complex";
    [SerializeField] private string issuer = "UnityGameServer";
    [SerializeField] private string audience = "UnityGameClient";
    [SerializeField] private int tokenExpirationMinutes = 60;
    
    private SecurityKey signingKey;
    private SigningCredentials signingCredentials;
    
    void Start()
    {
        InitializeJWT();
    }
    
    private void InitializeJWT()
    {
        signingKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secretKey));
        signingCredentials = new SigningCredentials(signingKey, SecurityAlgorithms.HmacSha256);
    }
    
    public string GenerateToken(string playerId, string username, string[] roles = null)
    {
        var claims = new List<Claim>
        {
            new Claim(ClaimTypes.NameIdentifier, playerId),
            new Claim(ClaimTypes.Name, username),
            new Claim("jti", Guid.NewGuid().ToString()),
            new Claim("iat", DateTimeOffset.UtcNow.ToUnixTimeSeconds().ToString(), ClaimValueTypes.Integer64)
        };
        
        // Add roles if provided
        if (roles != null)
        {
            foreach (var role in roles)
            {
                claims.Add(new Claim(ClaimTypes.Role, role));
            }
        }
        
        var tokenDescriptor = new SecurityTokenDescriptor
        {
            Subject = new ClaimsIdentity(claims),
            Expires = DateTime.UtcNow.AddMinutes(tokenExpirationMinutes),
            Issuer = issuer,
            Audience = audience,
            SigningCredentials = signingCredentials
        };
        
        var tokenHandler = new JwtSecurityTokenHandler();
        var token = tokenHandler.CreateToken(tokenDescriptor);
        return tokenHandler.WriteToken(token);
    }
    
    public ClaimsPrincipal ValidateToken(string token)
    {
        try
        {
            var tokenHandler = new JwtSecurityTokenHandler();
            var validationParameters = new TokenValidationParameters
            {
                ValidateIssuerSigningKey = true,
                IssuerSigningKey = signingKey,
                ValidateIssuer = true,
                ValidIssuer = issuer,
                ValidateAudience = true,
                ValidAudience = audience,
                ValidateLifetime = true,
                ClockSkew = TimeSpan.FromMinutes(1) // Allow 1 minute clock skew
            };
            
            var principal = tokenHandler.ValidateToken(token, validationParameters, out SecurityToken validatedToken);
            return principal;
        }
        catch (SecurityTokenException ex)
        {
            Debug.LogError($"Token validation failed: {ex.Message}");
            return null;
        }
    }
    
    public bool IsTokenExpired(string token)
    {
        try
        {
            var tokenHandler = new JwtSecurityTokenHandler();
            var jwt = tokenHandler.ReadJwtToken(token);
            return jwt.ValidTo < DateTime.UtcNow;
        }
        catch
        {
            return true; // Consider invalid tokens as expired
        }
    }
    
    public string RefreshToken(string expiredToken)
    {
        var principal = ValidateToken(expiredToken);
        if (principal == null)
            return null;
            
        var playerId = principal.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        var username = principal.FindFirst(ClaimTypes.Name)?.Value;
        var roles = principal.FindAll(ClaimTypes.Role).Select(c => c.Value).ToArray();
        
        return GenerateToken(playerId, username, roles);
    }
}
```

### Secure Login Flow
```csharp
// Secure Authentication Service
public class SecureAuthenticationService : MonoBehaviour
{
    [Header("Security Settings")]
    [SerializeField] private int maxLoginAttempts = 5;
    [SerializeField] private int lockoutDurationMinutes = 15;
    [SerializeField] private bool enableTwoFactorAuth = false;
    
    private Dictionary<string, LoginAttemptTracker> loginAttempts;
    private JWTAuthenticationManager jwtManager;
    
    void Start()
    {
        loginAttempts = new Dictionary<string, LoginAttemptTracker>();
        jwtManager = GetComponent<JWTAuthenticationManager>();
    }
    
    public async Task<AuthenticationResult> AuthenticateAsync(LoginRequest request)
    {
        var result = new AuthenticationResult();
        
        // Check for account lockout
        if (IsAccountLocked(request.Username))
        {
            result.Success = false;
            result.ErrorMessage = "Account temporarily locked due to too many failed attempts";
            result.ErrorCode = AuthErrorCode.AccountLocked;
            return result;
        }
        
        // Validate input
        if (!ValidateLoginInput(request))
        {
            result.Success = false;
            result.ErrorMessage = "Invalid input format";
            result.ErrorCode = AuthErrorCode.InvalidInput;
            RecordFailedAttempt(request.Username);
            return result;
        }
        
        // Verify credentials with database
        var user = await VerifyCredentialsAsync(request.Username, request.Password);
        if (user == null)
        {
            result.Success = false;
            result.ErrorMessage = "Invalid username or password";
            result.ErrorCode = AuthErrorCode.InvalidCredentials;
            RecordFailedAttempt(request.Username);
            return result;
        }
        
        // Check if account is active
        if (!user.IsActive)
        {
            result.Success = false;
            result.ErrorMessage = "Account is deactivated";
            result.ErrorCode = AuthErrorCode.AccountDeactivated;
            return result;
        }
        
        // Two-factor authentication check
        if (enableTwoFactorAuth && user.TwoFactorEnabled)
        {
            if (string.IsNullOrEmpty(request.TwoFactorCode))
            {
                result.Success = false;
                result.RequiresTwoFactor = true;
                result.ErrorMessage = "Two-factor authentication required";
                result.ErrorCode = AuthErrorCode.TwoFactorRequired;
                return result;
            }
            
            if (!await VerifyTwoFactorCodeAsync(user.UserId, request.TwoFactorCode))
            {
                result.Success = false;
                result.ErrorMessage = "Invalid two-factor authentication code";
                result.ErrorCode = AuthErrorCode.InvalidTwoFactor;
                RecordFailedAttempt(request.Username);
                return result;
            }
        }
        
        // Generate JWT token
        var roles = await GetUserRolesAsync(user.UserId);
        var token = jwtManager.GenerateToken(user.UserId, user.Username, roles);
        
        // Clear failed attempts
        ClearFailedAttempts(request.Username);
        
        // Update last login
        await UpdateLastLoginAsync(user.UserId);
        
        result.Success = true;
        result.Token = token;
        result.User = user;
        result.ExpiresAt = DateTime.UtcNow.AddMinutes(60);
        
        return result;
    }
    
    private async Task<User> VerifyCredentialsAsync(string username, string password)
    {
        // Hash the provided password with the stored salt
        var user = await DatabaseManager.Instance.GetUserByUsernameAsync(username);
        if (user == null)
            return null;
            
        var hashedPassword = HashPassword(password, user.PasswordSalt);
        if (hashedPassword != user.PasswordHash)
            return null;
            
        return user;
    }
    
    private string HashPassword(string password, string salt)
    {
        using (var pbkdf2 = new Rfc2898DeriveBytes(password, Convert.FromBase64String(salt), 10000))
        {
            byte[] hash = pbkdf2.GetBytes(20);
            return Convert.ToBase64String(hash);
        }
    }
    
    private bool IsAccountLocked(string username)
    {
        if (!loginAttempts.ContainsKey(username))
            return false;
            
        var tracker = loginAttempts[username];
        if (tracker.FailedAttempts >= maxLoginAttempts)
        {
            var lockoutExpiry = tracker.LastAttempt.AddMinutes(lockoutDurationMinutes);
            return DateTime.UtcNow < lockoutExpiry;
        }
        
        return false;
    }
    
    private void RecordFailedAttempt(string username)
    {
        if (!loginAttempts.ContainsKey(username))
        {
            loginAttempts[username] = new LoginAttemptTracker();
        }
        
        var tracker = loginAttempts[username];
        tracker.FailedAttempts++;
        tracker.LastAttempt = DateTime.UtcNow;
        
        // Log security event
        SecurityLogger.Instance.LogFailedLogin(username, GetClientIP());
    }
    
    private void ClearFailedAttempts(string username)
    {
        if (loginAttempts.ContainsKey(username))
        {
            loginAttempts.Remove(username);
        }
    }
}
```

## 🔧 Secure Network Communication

### TLS/SSL Implementation
```csharp
// Secure Network Manager with TLS
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;
using System.Net.Sockets;

public class SecureNetworkManager : MonoBehaviour
{
    [Header("TLS Configuration")]
    [SerializeField] private string serverAddress = "secure-game-server.com";
    [SerializeField] private int serverPort = 443;
    [SerializeField] private bool validateServerCertificate = true;
    
    private TcpClient tcpClient;
    private SslStream sslStream;
    private NetworkStream networkStream;
    
    public async Task<bool> ConnectSecureAsync()
    {
        try
        {
            tcpClient = new TcpClient();
            await tcpClient.ConnectAsync(serverAddress, serverPort);
            
            networkStream = tcpClient.GetStream();
            sslStream = new SslStream(networkStream, false, ValidateServerCertificate);
            
            // Authenticate as client
            await sslStream.AuthenticateAsClientAsync(serverAddress);
            
            if (sslStream.IsAuthenticated && sslStream.IsEncrypted)
            {
                Debug.Log($"Secure connection established. Cipher: {sslStream.CipherAlgorithm}, Key strength: {sslStream.KeyExchangeStrength}");
                StartReceiving();
                return true;
            }
            else
            {
                Debug.LogError("Failed to establish secure connection");
                return false;
            }
        }
        catch (Exception ex)
        {
            Debug.LogError($"Secure connection failed: {ex.Message}");
            return false;
        }
    }
    
    private bool ValidateServerCertificate(object sender, X509Certificate certificate, 
        X509Chain chain, SslPolicyErrors sslPolicyErrors)
    {
        if (!validateServerCertificate)
            return true; // Skip validation for development
            
        if (sslPolicyErrors == SslPolicyErrors.None)
            return true;
            
        // Log certificate validation errors
        Debug.LogWarning($"Certificate validation errors: {sslPolicyErrors}");
        
        // Allow self-signed certificates in development
        if (Application.isEditor && sslPolicyErrors == SslPolicyErrors.RemoteCertificateChainErrors)
        {
            Debug.LogWarning("Allowing self-signed certificate in development mode");
            return true;
        }
        
        return false;
    }
    
    public async Task SendSecureMessageAsync(GameMessage message)
    {
        if (sslStream == null || !sslStream.IsAuthenticated)
        {
            Debug.LogError("No secure connection available");
            return;
        }
        
        try
        {
            // Serialize and encrypt message
            var messageData = SerializeMessage(message);
            var encryptedData = EncryptMessage(messageData);
            
            // Send message length first
            var lengthBytes = BitConverter.GetBytes(encryptedData.Length);
            await sslStream.WriteAsync(lengthBytes, 0, lengthBytes.Length);
            
            // Send encrypted message
            await sslStream.WriteAsync(encryptedData, 0, encryptedData.Length);
            await sslStream.FlushAsync();
        }
        catch (Exception ex)
        {
            Debug.LogError($"Failed to send secure message: {ex.Message}");
            HandleConnectionError();
        }
    }
    
    private async void StartReceiving()
    {
        byte[] lengthBuffer = new byte[4];
        
        while (sslStream != null && sslStream.IsAuthenticated)
        {
            try
            {
                // Read message length
                await sslStream.ReadAsync(lengthBuffer, 0, 4);
                int messageLength = BitConverter.ToInt32(lengthBuffer, 0);
                
                if (messageLength > 1024 * 1024) // 1MB limit
                {
                    Debug.LogError("Message too large, possible attack");
                    break;
                }
                
                // Read encrypted message
                byte[] messageBuffer = new byte[messageLength];
                int totalRead = 0;
                
                while (totalRead < messageLength)
                {
                    int bytesRead = await sslStream.ReadAsync(messageBuffer, totalRead, 
                        messageLength - totalRead);
                    if (bytesRead == 0)
                        break;
                    totalRead += bytesRead;
                }
                
                // Decrypt and process message
                var decryptedData = DecryptMessage(messageBuffer);
                var message = DeserializeMessage(decryptedData);
                ProcessReceivedMessage(message);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error receiving secure message: {ex.Message}");
                HandleConnectionError();
                break;
            }
        }
    }
}
```

### Message Authentication and Integrity
```csharp
// Message Authentication Code (MAC) for integrity verification
using System.Security.Cryptography;

public class MessageIntegrityManager
{
    private readonly byte[] hmacKey;
    
    public MessageIntegrityManager(string secretKey)
    {
        hmacKey = Encoding.UTF8.GetBytes(secretKey);
    }
    
    public SecureMessage CreateSecureMessage(GameMessage message)
    {
        var messageData = JsonConvert.SerializeObject(message);
        var messageBytes = Encoding.UTF8.GetBytes(messageData);
        
        var secureMessage = new SecureMessage
        {
            MessageId = Guid.NewGuid().ToString(),
            Timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
            Payload = Convert.ToBase64String(messageBytes),
            Nonce = GenerateNonce()
        };
        
        // Calculate HMAC for integrity verification
        secureMessage.MAC = CalculateHMAC(secureMessage);
        
        return secureMessage;
    }
    
    public bool VerifyMessageIntegrity(SecureMessage secureMessage)
    {
        var receivedMAC = secureMessage.MAC;
        secureMessage.MAC = null; // Remove MAC before calculation
        
        var calculatedMAC = CalculateHMAC(secureMessage);
        secureMessage.MAC = receivedMAC; // Restore MAC
        
        return calculatedMAC == receivedMAC;
    }
    
    private string CalculateHMAC(SecureMessage message)
    {
        var messageString = $"{message.MessageId}|{message.Timestamp}|{message.Payload}|{message.Nonce}";
        var messageBytes = Encoding.UTF8.GetBytes(messageString);
        
        using (var hmac = new HMACSHA256(hmacKey))
        {
            var hashBytes = hmac.ComputeHash(messageBytes);
            return Convert.ToBase64String(hashBytes);
        }
    }
    
    private string GenerateNonce()
    {
        var nonceBytes = new byte[16];
        using (var rng = RandomNumberGenerator.Create())
        {
            rng.GetBytes(nonceBytes);
        }
        return Convert.ToBase64String(nonceBytes);
    }
    
    public bool IsMessageTooOld(SecureMessage message, int maxAgeSeconds = 300)
    {
        var messageTime = DateTimeOffset.FromUnixTimeMilliseconds(message.Timestamp);
        var age = DateTimeOffset.UtcNow - messageTime;
        return age.TotalSeconds > maxAgeSeconds;
    }
}
```

## 🚀 Session Management and Authorization

### Secure Session Handling
```csharp
// Game Session Security Manager
public class GameSessionManager : MonoBehaviour
{
    private Dictionary<string, GameSession> activeSessions;
    private Dictionary<string, DateTime> sessionLastActivity;
    private readonly int sessionTimeoutMinutes = 30;
    
    void Start()
    {
        activeSessions = new Dictionary<string, GameSession>();
        sessionLastActivity = new Dictionary<string, DateTime>();
        
        // Clean up expired sessions every minute
        InvokeRepeating(nameof(CleanupExpiredSessions), 60f, 60f);
    }
    
    public GameSession CreateSession(string playerId, string token)
    {
        var sessionId = Guid.NewGuid().ToString();
        var session = new GameSession
        {
            SessionId = sessionId,
            PlayerId = playerId,
            Token = token,
            CreatedAt = DateTime.UtcNow,
            LastActivity = DateTime.UtcNow,
            IsActive = true,
            IPAddress = GetClientIP(),
            UserAgent = GetClientUserAgent()
        };
        
        activeSessions[sessionId] = session;
        sessionLastActivity[sessionId] = DateTime.UtcNow;
        
        // Log session creation
        SecurityLogger.Instance.LogSessionCreated(sessionId, playerId);
        
        return session;
    }
    
    public bool ValidateSession(string sessionId, string token)
    {
        if (!activeSessions.ContainsKey(sessionId))
            return false;
            
        var session = activeSessions[sessionId];
        
        // Check if session is active
        if (!session.IsActive)
            return false;
            
        // Verify token matches
        if (session.Token != token)
        {
            SecurityLogger.Instance.LogSessionTokenMismatch(sessionId, session.PlayerId);
            return false;
        }
        
        // Check for session timeout
        if (IsSessionExpired(sessionId))
        {
            InvalidateSession(sessionId, "Session expired");
            return false;
        }
        
        // Update last activity
        sessionLastActivity[sessionId] = DateTime.UtcNow;
        session.LastActivity = DateTime.UtcNow;
        
        return true;
    }
    
    public void InvalidateSession(string sessionId, string reason = "Manual invalidation")
    {
        if (activeSessions.ContainsKey(sessionId))
        {
            var session = activeSessions[sessionId];
            session.IsActive = false;
            session.InvalidatedAt = DateTime.UtcNow;
            session.InvalidationReason = reason;
            
            SecurityLogger.Instance.LogSessionInvalidated(sessionId, session.PlayerId, reason);
            
            // Remove from tracking
            activeSessions.Remove(sessionId);
            sessionLastActivity.Remove(sessionId);
        }
    }
    
    private bool IsSessionExpired(string sessionId)
    {
        if (!sessionLastActivity.ContainsKey(sessionId))
            return true;
            
        var lastActivity = sessionLastActivity[sessionId];
        var timeSinceActivity = DateTime.UtcNow - lastActivity;
        
        return timeSinceActivity.TotalMinutes > sessionTimeoutMinutes;
    }
    
    private void CleanupExpiredSessions()
    {
        var expiredSessions = sessionLastActivity
            .Where(kvp => IsSessionExpired(kvp.Key))
            .Select(kvp => kvp.Key)
            .ToList();
            
        foreach (var sessionId in expiredSessions)
        {
            InvalidateSession(sessionId, "Session timeout");
        }
        
        Debug.Log($"Cleaned up {expiredSessions.Count} expired sessions");
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Security Architecture Design
```
Prompt: "Design a comprehensive authentication and authorization system for a Unity MMO game with 100k+ concurrent players, including JWT implementation, session management, role-based access control, and multi-factor authentication."
```

### Network Security Analysis
```
Prompt: "Analyze this Unity network communication code for security vulnerabilities and suggest improvements for TLS implementation, message authentication, and protection against common network attacks: [paste code]"
```

### Authentication Flow Optimization
```
Prompt: "Create an optimized authentication flow for Unity mobile games that balances security with user experience, including social login integration, biometric authentication, and secure token refresh mechanisms."
```

## 💡 Key Highlights

### Authentication Best Practices
- **Strong password policies**: Minimum length, complexity requirements
- **Multi-factor authentication**: SMS, email, or authenticator app verification  
- **Account lockout protection**: Prevent brute force attacks with rate limiting
- **Secure token storage**: Use secure storage mechanisms, never plain text
- **Session timeout**: Automatic invalidation of inactive sessions

### Network Security Measures
- **TLS/SSL encryption**: All client-server communication encrypted
- **Certificate validation**: Verify server identity to prevent MITM attacks
- **Message authentication**: HMAC verification for message integrity
- **Replay attack prevention**: Nonce and timestamp validation
- **Rate limiting**: Prevent DoS attacks and excessive API usage

### Authorization and Access Control
- **Principle of least privilege**: Grant minimum necessary permissions
- **Role-based access control**: Organize permissions by user roles
- **Token-based authorization**: Stateless authentication with JWT
- **Session validation**: Verify active sessions for each request
- **Audit logging**: Track authentication and authorization events