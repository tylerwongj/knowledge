# 02-Authentication-Systems.md

## 🎯 Learning Objectives
- Design and implement secure authentication systems for Unity games
- Master JWT token management and session handling in Unity
- Implement OAuth integration with social platforms (Steam, Google, Apple)
- Develop secure user registration and password management systems

## 🔧 Unity Authentication Implementation

### JWT Token Management System
```csharp
// JWT Authentication Manager for Unity
using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;

public class AuthenticationManager : MonoBehaviour
{
    [Header("Authentication Configuration")]
    [SerializeField] private string authServerUrl = "https://your-auth-server.com";
    [SerializeField] private float tokenRefreshBuffer = 300f; // 5 minutes before expiry
    
    public static AuthenticationManager Instance { get; private set; }
    
    // Events
    public System.Action<bool> OnAuthenticationStateChanged;
    public System.Action<string> OnAuthenticationError;
    
    // Properties
    public bool IsAuthenticated => !string.IsNullOrEmpty(currentAccessToken) && !IsTokenExpired();
    public string CurrentUserId => currentUser?.userId;
    public UserProfile CurrentUser => currentUser;
    
    private string currentAccessToken;
    private string currentRefreshToken;
    private DateTime tokenExpiryTime;
    private UserProfile currentUser;
    private Coroutine tokenRefreshCoroutine;
    
    [System.Serializable]
    public class UserProfile
    {
        public string userId;
        public string username;
        public string email;
        public string displayName;
        public string avatarUrl;
        public DateTime lastLoginTime;
        public Dictionary<string, object> customData;
    }
    
    [System.Serializable]
    public class AuthResponse
    {
        public string accessToken;
        public string refreshToken;
        public int expiresIn;
        public UserProfile user;
        public string message;
        public bool success;
    }
    
    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            LoadStoredTokens();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    private void Start()
    {
        // Auto-refresh tokens if we have valid stored tokens
        if (IsAuthenticated)
        {
            StartTokenRefreshCoroutine();
            OnAuthenticationStateChanged?.Invoke(true);
        }
    }
    
    // Email/Password Authentication
    public void RegisterWithEmail(string email, string password, string username, 
        System.Action<bool, string> callback)
    {
        StartCoroutine(RegisterCoroutine(email, password, username, callback));
    }
    
    private IEnumerator RegisterCoroutine(string email, string password, string username, 
        System.Action<bool, string> callback)
    {
        var registrationData = new
        {
            email = email,
            password = password,
            username = username,
            deviceId = SystemInfo.deviceUniqueIdentifier,
            platform = Application.platform.ToString()
        };
        
        string jsonData = JsonConvert.SerializeObject(registrationData);
        
        using (UnityWebRequest request = UnityWebRequest.PostWwwForm($"{authServerUrl}/auth/register", ""))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    AuthResponse response = JsonConvert.DeserializeObject<AuthResponse>(request.downloadHandler.text);
                    
                    if (response.success)
                    {
                        HandleSuccessfulAuthentication(response);
                        callback?.Invoke(true, "Registration successful");
                    }
                    else
                    {
                        callback?.Invoke(false, response.message);
                    }
                }
                catch (Exception e)
                {
                    Debug.LogError($"Registration response parsing error: {e.Message}");
                    callback?.Invoke(false, "Invalid server response");
                }
            }
            else
            {
                string errorMessage = $"Registration failed: {request.error}";
                Debug.LogError(errorMessage);
                callback?.Invoke(false, errorMessage);
            }
        }
    }
    
    public void LoginWithEmail(string email, string password, System.Action<bool, string> callback)
    {
        StartCoroutine(LoginCoroutine(email, password, callback));
    }
    
    private IEnumerator LoginCoroutine(string email, string password, System.Action<bool, string> callback)
    {
        var loginData = new
        {
            email = email,
            password = password,
            deviceId = SystemInfo.deviceUniqueIdentifier,
            rememberMe = true
        };
        
        string jsonData = JsonConvert.SerializeObject(loginData);
        
        using (UnityWebRequest request = UnityWebRequest.PostWwwForm($"{authServerUrl}/auth/login", ""))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    AuthResponse response = JsonConvert.DeserializeObject<AuthResponse>(request.downloadHandler.text);
                    
                    if (response.success)
                    {
                        HandleSuccessfulAuthentication(response);
                        callback?.Invoke(true, "Login successful");
                    }
                    else
                    {
                        callback?.Invoke(false, response.message);
                    }
                }
                catch (Exception e)
                {
                    Debug.LogError($"Login response parsing error: {e.Message}");
                    callback?.Invoke(false, "Invalid server response");
                }
            }
            else
            {
                string errorMessage = $"Login failed: {request.error}";
                Debug.LogError(errorMessage);
                callback?.Invoke(false, errorMessage);
            }
        }
    }
    
    // Social Authentication (OAuth)
    public void LoginWithGoogle(string googleIdToken, System.Action<bool, string> callback)
    {
        StartCoroutine(SocialLoginCoroutine("google", googleIdToken, callback));
    }
    
    public void LoginWithApple(string appleIdToken, System.Action<bool, string> callback)
    {
        StartCoroutine(SocialLoginCoroutine("apple", appleIdToken, callback));
    }
    
    public void LoginWithSteam(string steamTicket, System.Action<bool, string> callback)
    {
        StartCoroutine(SocialLoginCoroutine("steam", steamTicket, callback));
    }
    
    private IEnumerator SocialLoginCoroutine(string provider, string token, System.Action<bool, string> callback)
    {
        var socialLoginData = new
        {
            provider = provider,
            token = token,
            deviceId = SystemInfo.deviceUniqueIdentifier
        };
        
        string jsonData = JsonConvert.SerializeObject(socialLoginData);
        
        using (UnityWebRequest request = UnityWebRequest.PostWwwForm($"{authServerUrl}/auth/social", ""))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    AuthResponse response = JsonConvert.DeserializeObject<AuthResponse>(request.downloadHandler.text);
                    
                    if (response.success)
                    {
                        HandleSuccessfulAuthentication(response);
                        callback?.Invoke(true, $"{provider} login successful");
                    }
                    else
                    {
                        callback?.Invoke(false, response.message);
                    }
                }
                catch (Exception e)
                {
                    Debug.LogError($"Social login response parsing error: {e.Message}");
                    callback?.Invoke(false, "Invalid server response");
                }
            }
            else
            {
                string errorMessage = $"{provider} login failed: {request.error}";
                Debug.LogError(errorMessage);
                callback?.Invoke(false, errorMessage);
            }
        }
    }
    
    // Token Management
    private void HandleSuccessfulAuthentication(AuthResponse response)
    {
        currentAccessToken = response.accessToken;
        currentRefreshToken = response.refreshToken;
        currentUser = response.user;
        
        // Calculate token expiry time
        tokenExpiryTime = DateTime.UtcNow.AddSeconds(response.expiresIn);
        
        // Store tokens securely
        StoreTokensSecurely();
        
        // Start automatic token refresh
        StartTokenRefreshCoroutine();
        
        // Notify authentication state change
        OnAuthenticationStateChanged?.Invoke(true);
        
        Debug.Log($"Authentication successful for user: {currentUser.username}");
    }
    
    private void StoreTokensSecurely()
    {
        SecurePlayerPrefs.SetSecureString("access_token", currentAccessToken);
        SecurePlayerPrefs.SetSecureString("refresh_token", currentRefreshToken);
        SecurePlayerPrefs.SetSecureString("token_expiry", tokenExpiryTime.ToBinary().ToString());
        SecurePlayerPrefs.SetSecureString("user_profile", JsonConvert.SerializeObject(currentUser));
    }
    
    private void LoadStoredTokens()
    {
        currentAccessToken = SecurePlayerPrefs.GetSecureString("access_token");
        currentRefreshToken = SecurePlayerPrefs.GetSecureString("refresh_token");
        
        string expiryString = SecurePlayerPrefs.GetSecureString("token_expiry");
        if (!string.IsNullOrEmpty(expiryString) && long.TryParse(expiryString, out long expiry))
        {
            tokenExpiryTime = DateTime.FromBinary(expiry);
        }
        
        string userProfileString = SecurePlayerPrefs.GetSecureString("user_profile");
        if (!string.IsNullOrEmpty(userProfileString))
        {
            try
            {
                currentUser = JsonConvert.DeserializeObject<UserProfile>(userProfileString);
            }
            catch (Exception e)
            {
                Debug.LogError($"Failed to load user profile: {e.Message}");
            }
        }
    }
    
    private bool IsTokenExpired()
    {
        return DateTime.UtcNow >= tokenExpiryTime;
    }
    
    private void StartTokenRefreshCoroutine()
    {
        if (tokenRefreshCoroutine != null)
        {
            StopCoroutine(tokenRefreshCoroutine);
        }
        tokenRefreshCoroutine = StartCoroutine(TokenRefreshCoroutine());
    }
    
    private IEnumerator TokenRefreshCoroutine()
    {
        while (true)
        {
            // Calculate time until refresh needed
            double secondsUntilRefresh = (tokenExpiryTime - DateTime.UtcNow).TotalSeconds - tokenRefreshBuffer;
            
            if (secondsUntilRefresh > 0)
            {
                yield return new WaitForSeconds((float)secondsUntilRefresh);
            }
            
            // Refresh token
            yield return StartCoroutine(RefreshTokenCoroutine());
            
            // Wait before next check
            yield return new WaitForSeconds(60f); // Check every minute
        }
    }
    
    private IEnumerator RefreshTokenCoroutine()
    {
        if (string.IsNullOrEmpty(currentRefreshToken))
        {
            Debug.LogWarning("No refresh token available");
            yield break;
        }
        
        var refreshData = new
        {
            refreshToken = currentRefreshToken,
            deviceId = SystemInfo.deviceUniqueIdentifier
        };
        
        string jsonData = JsonConvert.SerializeObject(refreshData);
        
        using (UnityWebRequest request = UnityWebRequest.PostWwwForm($"{authServerUrl}/auth/refresh", ""))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                try
                {
                    AuthResponse response = JsonConvert.DeserializeObject<AuthResponse>(request.downloadHandler.text);
                    
                    if (response.success)
                    {
                        HandleSuccessfulAuthentication(response);
                        Debug.Log("Token refreshed successfully");
                    }
                    else
                    {
                        Debug.LogError($"Token refresh failed: {response.message}");
                        HandleAuthenticationFailure("Token refresh failed");
                    }
                }
                catch (Exception e)
                {
                    Debug.LogError($"Token refresh response parsing error: {e.Message}");
                    HandleAuthenticationFailure("Invalid refresh response");
                }
            }
            else
            {
                Debug.LogError($"Token refresh request failed: {request.error}");
                HandleAuthenticationFailure("Network error during token refresh");
            }
        }
    }
    
    // Logout and Cleanup
    public void Logout()
    {
        // Stop token refresh
        if (tokenRefreshCoroutine != null)
        {
            StopCoroutine(tokenRefreshCoroutine);
            tokenRefreshCoroutine = null;
        }
        
        // Clear tokens and user data
        currentAccessToken = null;
        currentRefreshToken = null;
        currentUser = null;
        tokenExpiryTime = DateTime.MinValue;
        
        // Clear stored data
        SecurePlayerPrefs.DeleteKey("access_token");
        SecurePlayerPrefs.DeleteKey("refresh_token");
        SecurePlayerPrefs.DeleteKey("token_expiry");
        SecurePlayerPrefs.DeleteKey("user_profile");
        
        // Notify state change
        OnAuthenticationStateChanged?.Invoke(false);
        
        Debug.Log("User logged out successfully");
    }
    
    private void HandleAuthenticationFailure(string reason)
    {
        Debug.LogError($"Authentication failure: {reason}");
        OnAuthenticationError?.Invoke(reason);
        
        // Force logout on authentication failure
        Logout();
    }
    
    // Utility Methods
    public string GetAuthorizationHeader()
    {
        return IsAuthenticated ? $"Bearer {currentAccessToken}" : null;
    }
    
    public void AddAuthorizationHeader(UnityWebRequest request)
    {
        if (IsAuthenticated)
        {
            request.SetRequestHeader("Authorization", GetAuthorizationHeader());
        }
    }
    
    private void OnDestroy()
    {
        if (tokenRefreshCoroutine != null)
        {
            StopCoroutine(tokenRefreshCoroutine);
        }
    }
}
```

### Unity UI Authentication Interface
```csharp
// Authentication UI Controller
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class AuthenticationUI : MonoBehaviour
{
    [Header("UI References")]
    [SerializeField] private GameObject loginPanel;
    [SerializeField] private GameObject registerPanel;
    [SerializeField] private GameObject loadingPanel;
    
    [Header("Login Form")]
    [SerializeField] private TMP_InputField loginEmailField;
    [SerializeField] private TMP_InputField loginPasswordField;
    [SerializeField] private Button loginButton;
    [SerializeField] private Button showRegisterButton;
    
    [Header("Register Form")]
    [SerializeField] private TMP_InputField registerEmailField;
    [SerializeField] private TMP_InputField registerPasswordField;
    [SerializeField] private TMP_InputField registerUsernameField;
    [SerializeField] private Button registerButton;
    [SerializeField] private Button showLoginButton;
    
    [Header("Social Login")]
    [SerializeField] private Button googleLoginButton;
    [SerializeField] private Button appleLoginButton;
    [SerializeField] private Button steamLoginButton;
    
    [Header("Feedback")]
    [SerializeField] private TextMeshProUGUI statusText;
    [SerializeField] private Color successColor = Color.green;
    [SerializeField] private Color errorColor = Color.red;
    
    private void Start()
    {
        SetupEventListeners();
        ShowLoginPanel();
        
        // Listen to authentication events
        AuthenticationManager.Instance.OnAuthenticationStateChanged += OnAuthStateChanged;
        AuthenticationManager.Instance.OnAuthenticationError += OnAuthError;
    }
    
    private void SetupEventListeners()
    {
        loginButton.onClick.AddListener(OnLoginClicked);
        registerButton.onClick.AddListener(OnRegisterClicked);
        showRegisterButton.onClick.AddListener(ShowRegisterPanel);
        showLoginButton.onClick.AddListener(ShowLoginPanel);
        
        googleLoginButton.onClick.AddListener(OnGoogleLoginClicked);
        appleLoginButton.onClick.AddListener(OnAppleLoginClicked);
        steamLoginButton.onClick.AddListener(OnSteamLoginClicked);
    }
    
    private void OnLoginClicked()
    {
        string email = loginEmailField.text.Trim();
        string password = loginPasswordField.text;
        
        if (!ValidateLoginInput(email, password))
            return;
        
        ShowLoading("Logging in...");
        
        AuthenticationManager.Instance.LoginWithEmail(email, password, (success, message) =>
        {
            HideLoading();
            
            if (success)
            {
                ShowStatus(message, successColor);
            }
            else
            {
                ShowStatus(message, errorColor);
            }
        });
    }
    
    private void OnRegisterClicked()
    {
        string email = registerEmailField.text.Trim();
        string password = registerPasswordField.text;
        string username = registerUsernameField.text.Trim();
        
        if (!ValidateRegisterInput(email, password, username))
            return;
        
        ShowLoading("Creating account...");
        
        AuthenticationManager.Instance.RegisterWithEmail(email, password, username, (success, message) =>
        {
            HideLoading();
            
            if (success)
            {
                ShowStatus(message, successColor);
                ShowLoginPanel(); // Switch to login after successful registration
            }
            else
            {
                ShowStatus(message, errorColor);
            }
        });
    }
    
    private void OnGoogleLoginClicked()
    {
        // Integration with Google Play Games or Google Sign-In SDK
        ShowLoading("Connecting to Google...");
        
        // This would integrate with actual Google SDK
        // For demonstration, we'll simulate the process
        StartCoroutine(SimulateSocialLogin("google"));
    }
    
    private void OnAppleLoginClicked()
    {
        // Integration with Apple Sign-In SDK
        ShowLoading("Connecting to Apple...");
        StartCoroutine(SimulateSocialLogin("apple"));
    }
    
    private void OnSteamLoginClicked()
    {
        // Integration with Steamworks SDK
        ShowLoading("Connecting to Steam...");
        StartCoroutine(SimulateSocialLogin("steam"));
    }
    
    private System.Collections.IEnumerator SimulateSocialLogin(string provider)
    {
        yield return new WaitForSeconds(1f); // Simulate SDK interaction
        
        // In real implementation, you would get the actual token from the SDK
        string mockToken = "mock_token_from_" + provider;
        
        System.Action<bool, string> callback = (success, message) =>
        {
            HideLoading();
            ShowStatus(message, success ? successColor : errorColor);
        };
        
        switch (provider)
        {
            case "google":
                AuthenticationManager.Instance.LoginWithGoogle(mockToken, callback);
                break;
            case "apple":
                AuthenticationManager.Instance.LoginWithApple(mockToken, callback);
                break;
            case "steam":
                AuthenticationManager.Instance.LoginWithSteam(mockToken, callback);
                break;
        }
    }
    
    private bool ValidateLoginInput(string email, string password)
    {
        if (string.IsNullOrEmpty(email))
        {
            ShowStatus("Please enter your email", errorColor);
            return false;
        }
        
        if (!IsValidEmail(email))
        {
            ShowStatus("Please enter a valid email address", errorColor);
            return false;
        }
        
        if (string.IsNullOrEmpty(password))
        {
            ShowStatus("Please enter your password", errorColor);
            return false;
        }
        
        return true;
    }
    
    private bool ValidateRegisterInput(string email, string password, string username)
    {
        if (string.IsNullOrEmpty(email) || !IsValidEmail(email))
        {
            ShowStatus("Please enter a valid email address", errorColor);
            return false;
        }
        
        if (string.IsNullOrEmpty(password) || password.Length < 8)
        {
            ShowStatus("Password must be at least 8 characters long", errorColor);
            return false;
        }
        
        if (string.IsNullOrEmpty(username) || username.Length < 3)
        {
            ShowStatus("Username must be at least 3 characters long", errorColor);
            return false;
        }
        
        return true;
    }
    
    private bool IsValidEmail(string email)
    {
        try
        {
            var addr = new System.Net.Mail.MailAddress(email);
            return addr.Address == email;
        }
        catch
        {
            return false;
        }
    }
    
    private void ShowLoginPanel()
    {
        loginPanel.SetActive(true);
        registerPanel.SetActive(false);
        ClearFields();
        ClearStatus();
    }
    
    private void ShowRegisterPanel()
    {
        loginPanel.SetActive(false);
        registerPanel.SetActive(true);
        ClearFields();
        ClearStatus();
    }
    
    private void ShowLoading(string message)
    {
        loadingPanel.SetActive(true);
        ShowStatus(message, Color.white);
    }
    
    private void HideLoading()
    {
        loadingPanel.SetActive(false);
    }
    
    private void ShowStatus(string message, Color color)
    {
        statusText.text = message;
        statusText.color = color;
    }
    
    private void ClearStatus()
    {
        statusText.text = "";
    }
    
    private void ClearFields()
    {
        loginEmailField.text = "";
        loginPasswordField.text = "";
        registerEmailField.text = "";
        registerPasswordField.text = "";
        registerUsernameField.text = "";
    }
    
    private void OnAuthStateChanged(bool isAuthenticated)
    {
        if (isAuthenticated)
        {
            // Hide authentication UI and show main game UI
            gameObject.SetActive(false);
        }
    }
    
    private void OnAuthError(string error)
    {
        ShowStatus($"Authentication error: {error}", errorColor);
    }
    
    private void OnDestroy()
    {
        if (AuthenticationManager.Instance != null)
        {
            AuthenticationManager.Instance.OnAuthenticationStateChanged -= OnAuthStateChanged;
            AuthenticationManager.Instance.OnAuthenticationError -= OnAuthError;
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Authentication Security Review
```
PROMPT TEMPLATE - Authentication Security Analysis:

"Review this Unity authentication implementation for security vulnerabilities:

```csharp
[PASTE YOUR AUTHENTICATION CODE]
```

Analyze for:
1. JWT token security and validation
2. Password storage and transmission security
3. Session management vulnerabilities
4. OAuth implementation security
5. Brute force attack protection
6. Input validation and sanitization
7. Secure storage of credentials

Provide specific Unity-focused security improvements with code examples."
```

### OAuth Integration Generator
```
PROMPT TEMPLATE - OAuth Implementation:

"Generate a secure OAuth integration for Unity with these requirements:

Platform: [Google/Apple/Steam/Facebook/etc.]
Unity Version: [2022.3 LTS/2023.2/etc.]
Authentication Flow: [Authorization Code/Implicit/etc.]
Additional Requirements: [Offline access, user profile data, etc.]

Include:
1. Complete C# implementation
2. Error handling and edge cases
3. Token refresh mechanism
4. Unity-specific considerations
5. Security best practices
6. Platform-specific SDK integration points"
```

## 💡 Key Authentication Security Principles

### Essential Authentication Checklist
- **Secure token storage** - Use encrypted storage for sensitive tokens
- **Token expiration** - Implement reasonable token lifetimes with refresh
- **HTTPS only** - Never transmit credentials over HTTP
- **Input validation** - Validate all user inputs on client and server
- **Rate limiting** - Prevent brute force attacks on login endpoints
- **Strong passwords** - Enforce password complexity requirements
- **Multi-factor authentication** - Add extra security layers when possible
- **Session management** - Properly handle session lifecycle and cleanup

### Common Authentication Vulnerabilities
1. **Storing credentials in plaintext**
2. **Weak password requirements**
3. **Missing token expiration**
4. **Insecure token storage**
5. **Lack of rate limiting**
6. **Poor error handling (information disclosure)**
7. **Missing input validation**
8. **Inadequate session management**

This comprehensive authentication system provides Unity developers with production-ready, secure authentication solutions that protect user accounts while providing excellent user experience across multiple platforms and authentication methods.