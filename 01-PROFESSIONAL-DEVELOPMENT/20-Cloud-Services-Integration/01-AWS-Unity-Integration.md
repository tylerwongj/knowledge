# 01-AWS-Unity-Integration.md

## 🎯 Learning Objectives
- Master AWS SDK integration for Unity game development
- Implement scalable cloud storage and user management with AWS Cognito
- Design efficient data synchronization with DynamoDB and S3
- Develop serverless backend architecture using AWS Lambda and API Gateway

## 🔧 AWS Unity SDK Implementation

### AWS Configuration Manager
```csharp
// Scripts/AWS/AWSManager.cs
using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Amazon;
using Amazon.CognitoIdentity;
using Amazon.CognitoIdentityProvider;
using Amazon.DynamoDBv2;
using Amazon.S3;
using Amazon.Lambda;
using Amazon.GameLift;

public class AWSManager : MonoBehaviour
{
    [Header("AWS Configuration")]
    [SerializeField] private string cognitoIdentityPoolId = "us-east-1:your-identity-pool-id";
    [SerializeField] private string cognitoUserPoolId = "us-east-1_yourUserPool";
    [SerializeField] private string cognitoUserPoolClientId = "your-client-id";
    [SerializeField] private string s3BucketName = "your-game-bucket";
    [SerializeField] private string dynamoDBTablePrefix = "YourGame";
    [SerializeField] private RegionEndpoint awsRegion = RegionEndpoint.USEast1;
    [SerializeField] private bool enableAnalytics = true;
    
    public static AWSManager Instance { get; private set; }
    
    // AWS Service Clients
    public AmazonCognitoIdentityProviderClient CognitoUserPoolClient { get; private set; }
    public CognitoAWSCredentials CognitoCredentials { get; private set; }
    public AmazonDynamoDBClient DynamoDBClient { get; private set; }
    public AmazonS3Client S3Client { get; private set; }
    public AmazonLambdaClient LambdaClient { get; private set; }
    public AmazonGameLiftClient GameLiftClient { get; private set; }
    
    // Properties
    public bool IsInitialized { get; private set; }
    public string CurrentUserId { get; private set; }
    public bool IsUserAuthenticated => !string.IsNullOrEmpty(CurrentUserId);
    
    // Events
    public System.Action OnInitialized;
    public System.Action<string> OnInitializationError;
    public System.Action<bool> OnAuthenticationChanged;
    
    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            StartCoroutine(InitializeAWS());
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    private IEnumerator InitializeAWS()
    {
        try
        {
            Debug.Log("[AWS] Initializing AWS services...");
            
            // Configure AWS settings
            AWSConfigs.HttpClient = AWSConfigs.HttpClientOption.UnityWebRequest;
            AWSConfigs.RegionEndpoint = awsRegion;
            AWSConfigs.LoggingConfig.LogMetrics = true;
            AWSConfigs.LoggingConfig.LogResponses = ResponseLoggingOption.OnError;
            
            // Initialize Cognito Identity Pool
            CognitoCredentials = new CognitoAWSCredentials(cognitoIdentityPoolId, awsRegion);
            
            // Initialize Cognito User Pool
            CognitoUserPoolClient = new AmazonCognitoIdentityProviderClient(CognitoCredentials, awsRegion);
            
            // Initialize other AWS services
            DynamoDBClient = new AmazonDynamoDBClient(CognitoCredentials, awsRegion);
            S3Client = new AmazonS3Client(CognitoCredentials, awsRegion);
            LambdaClient = new AmazonLambdaClient(CognitoCredentials, awsRegion);
            GameLiftClient = new AmazonGameLiftClient(CognitoCredentials, awsRegion);
            
            // Test connectivity
            yield return StartCoroutine(TestAWSConnection());
            
            IsInitialized = true;
            Debug.Log("[AWS] AWS services initialized successfully");
            OnInitialized?.Invoke();
        }
        catch (Exception e)
        {
            Debug.LogError($"[AWS] Initialization failed: {e.Message}");
            OnInitializationError?.Invoke(e.Message);
        }
    }
    
    private IEnumerator TestAWSConnection()
    {
        bool connectionTested = false;
        bool connectionSuccess = false;
        string errorMessage = "";
        
        // Test with a simple Cognito operation
        CognitoCredentials.GetCredentialsAsync((result) =>
        {
            connectionTested = true;
            if (result.Exception == null)
            {
                connectionSuccess = true;
                Debug.Log("[AWS] Connection test successful");
            }
            else
            {
                connectionSuccess = false;
                errorMessage = result.Exception.Message;
                Debug.LogError($"[AWS] Connection test failed: {errorMessage}");
            }
        });
        
        // Wait for test completion
        while (!connectionTested)
        {
            yield return new WaitForSeconds(0.1f);
        }
        
        if (!connectionSuccess)
        {
            throw new Exception($"AWS connection test failed: {errorMessage}");
        }
    }
    
    // User Authentication with Cognito
    public void SignUp(string username, string password, string email, 
        System.Action<bool, string> onComplete)
    {
        if (!IsInitialized)
        {
            onComplete?.Invoke(false, "AWS not initialized");
            return;
        }
        
        StartCoroutine(SignUpCoroutine(username, password, email, onComplete));
    }
    
    private IEnumerator SignUpCoroutine(string username, string password, string email,
        System.Action<bool, string> onComplete)
    {
        bool operationComplete = false;
        bool success = false;
        string message = "";
        
        var signUpRequest = new Amazon.CognitoIdentityProvider.Model.SignUpRequest
        {
            ClientId = cognitoUserPoolClientId,
            Username = username,
            Password = password,
            UserAttributes = new List<Amazon.CognitoIdentityProvider.Model.AttributeType>
            {
                new Amazon.CognitoIdentityProvider.Model.AttributeType
                {
                    Name = "email",
                    Value = email
                }
            }
        };
        
        CognitoUserPoolClient.SignUpAsync(signUpRequest, (result) =>
        {
            operationComplete = true;
            if (result.Exception == null)
            {
                success = true;
                message = "Sign up successful. Please check your email for verification.";
                Debug.Log($"[AWS] User signed up: {username}");
            }
            else
            {
                success = false;
                message = result.Exception.Message;
                Debug.LogError($"[AWS] Sign up failed: {message}");
            }
        });
        
        while (!operationComplete)
        {
            yield return new WaitForSeconds(0.1f);
        }
        
        onComplete?.Invoke(success, message);
    }
    
    public void SignIn(string username, string password, System.Action<bool, string> onComplete)
    {
        if (!IsInitialized)
        {
            onComplete?.Invoke(false, "AWS not initialized");
            return;
        }
        
        StartCoroutine(SignInCoroutine(username, password, onComplete));
    }
    
    private IEnumerator SignInCoroutine(string username, string password,
        System.Action<bool, string> onComplete)
    {
        bool operationComplete = false;
        bool success = false;
        string message = "";
        
        var authRequest = new Amazon.CognitoIdentityProvider.Model.InitiateAuthRequest
        {
            ClientId = cognitoUserPoolClientId,
            AuthFlow = Amazon.CognitoIdentityProvider.AuthFlowType.USER_PASSWORD_AUTH,
            AuthParameters = new Dictionary<string, string>
            {
                {"USERNAME", username},
                {"PASSWORD", password}
            }
        };
        
        CognitoUserPoolClient.InitiateAuthAsync(authRequest, (result) =>
        {
            operationComplete = true;
            if (result.Exception == null && result.Response.AuthenticationResult != null)
            {
                success = true;
                message = "Sign in successful";
                
                // Store authentication tokens
                var authResult = result.Response.AuthenticationResult;
                CurrentUserId = username; // In production, extract from ID token
                
                // Update Cognito credentials with the new tokens
                CognitoCredentials.Clear();
                
                Debug.Log($"[AWS] User signed in: {username}");
                OnAuthenticationChanged?.Invoke(true);
            }
            else
            {
                success = false;
                message = result.Exception?.Message ?? "Authentication failed";
                Debug.LogError($"[AWS] Sign in failed: {message}");
            }
        });
        
        while (!operationComplete)
        {
            yield return new WaitForSeconds(0.1f);
        }
        
        onComplete?.Invoke(success, message);
    }
    
    public void SignOut()
    {
        CurrentUserId = null;
        CognitoCredentials.Clear();
        OnAuthenticationChanged?.Invoke(false);
        Debug.Log("[AWS] User signed out");
    }
    
    // Utility Methods
    public void RefreshCredentials(System.Action<bool> onComplete = null)
    {
        if (!IsInitialized)
        {
            onComplete?.Invoke(false);
            return;
        }
        
        CognitoCredentials.GetCredentialsAsync((result) =>
        {
            bool success = result.Exception == null;
            if (success)
            {
                Debug.Log("[AWS] Credentials refreshed successfully");
            }
            else
            {
                Debug.LogError($"[AWS] Credential refresh failed: {result.Exception.Message}");
            }
            onComplete?.Invoke(success);
        });
    }
    
    public bool IsServiceAvailable()
    {
        return IsInitialized && Application.internetReachability != NetworkReachability.NotReachable;
    }
    
    private void OnApplicationPause(bool pauseStatus)
    {
        if (!pauseStatus && IsInitialized)
        {
            // Refresh credentials when app resumes
            RefreshCredentials();
        }
    }
    
    private void OnDestroy()
    {
        // Clean up AWS clients
        CognitoUserPoolClient?.Dispose();
        DynamoDBClient?.Dispose();
        S3Client?.Dispose();
        LambdaClient?.Dispose();
        GameLiftClient?.Dispose();
    }
}
```

### DynamoDB Data Service
```csharp
// Scripts/AWS/DynamoDBService.cs
using System;
using System.Collections.Generic;
using System.Collections;
using UnityEngine;
using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.Model;
using Amazon.DynamoDBv2.DocumentModel;
using Newtonsoft.Json;

public class DynamoDBService : MonoBehaviour
{
    [Header("DynamoDB Configuration")]
    [SerializeField] private string playerDataTable = "PlayerData";
    [SerializeField] private string gameSessionsTable = "GameSessions";
    [SerializeField] private string leaderboardTable = "Leaderboard";
    [SerializeField] private string achievementsTable = "Achievements";
    
    public static DynamoDBService Instance { get; private set; }
    
    // Table references
    private Table playerDataTableRef;
    private Table gameSessionsTableRef;
    private Table leaderboardTableRef;
    private Table achievementsTableRef;
    
    [System.Serializable]
    public class PlayerData
    {
        public string PlayerId { get; set; }
        public string Username { get; set; }
        public int Level { get; set; }
        public long Experience { get; set; }
        public int Coins { get; set; }
        public int Gems { get; set; }
        public List<string> UnlockedItems { get; set; }
        public Dictionary<string, object> CustomData { get; set; }
        public DateTime LastLoginTime { get; set; }
        public DateTime CreatedTime { get; set; }
        public string Version { get; set; }
        
        public PlayerData()
        {
            UnlockedItems = new List<string>();
            CustomData = new Dictionary<string, object>();
            Version = Application.version;
        }
    }
    
    [System.Serializable]
    public class GameSession
    {
        public string SessionId { get; set; }
        public string PlayerId { get; set; }
        public string GameMode { get; set; }
        public DateTime StartTime { get; set; }
        public DateTime EndTime { get; set; }
        public int Score { get; set; }
        public int Duration { get; set; }
        public Dictionary<string, object> SessionData { get; set; }
        
        public GameSession()
        {
            SessionData = new Dictionary<string, object>();
        }
    }
    
    [System.Serializable]
    public class LeaderboardEntry
    {
        public string PlayerId { get; set; }
        public string Username { get; set; }
        public long Score { get; set; }
        public string LeaderboardType { get; set; }
        public DateTime AchievedAt { get; set; }
        public Dictionary<string, object> Metadata { get; set; }
        
        public LeaderboardEntry()
        {
            Metadata = new Dictionary<string, object>();
        }
    }
    
    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    private void Start()
    {
        if (AWSManager.Instance != null && AWSManager.Instance.IsInitialized)
        {
            InitializeTables();
        }
        else
        {
            AWSManager.Instance.OnInitialized += InitializeTables;
        }
    }
    
    private void InitializeTables()
    {
        try
        {
            playerDataTableRef = Table.LoadTable(AWSManager.Instance.DynamoDBClient, playerDataTable);
            gameSessionsTableRef = Table.LoadTable(AWSManager.Instance.DynamoDBClient, gameSessionsTable);
            leaderboardTableRef = Table.LoadTable(AWSManager.Instance.DynamoDBClient, leaderboardTable);
            achievementsTableRef = Table.LoadTable(AWSManager.Instance.DynamoDBClient, achievementsTable);
            
            Debug.Log("[DynamoDB] Tables initialized successfully");
        }
        catch (Exception e)
        {
            Debug.LogError($"[DynamoDB] Table initialization failed: {e.Message}");
        }
    }
    
    // Player Data Operations
    public void SavePlayerData(PlayerData playerData, System.Action<bool, string> onComplete)
    {
        if (playerDataTableRef == null || !AWSManager.Instance.IsServiceAvailable())
        {
            onComplete?.Invoke(false, "Service not available");
            return;
        }
        
        StartCoroutine(SavePlayerDataCoroutine(playerData, onComplete));
    }
    
    private IEnumerator SavePlayerDataCoroutine(PlayerData playerData, System.Action<bool, string> onComplete)
    {
        bool operationComplete = false;
        bool success = false;
        string message = "";
        
        try
        {
            // Convert PlayerData to Document
            var document = new Document();
            document["PlayerId"] = playerData.PlayerId;
            document["Username"] = playerData.Username;
            document["Level"] = playerData.Level;
            document["Experience"] = playerData.Experience;
            document["Coins"] = playerData.Coins;
            document["Gems"] = playerData.Gems;
            document["UnlockedItems"] = JsonConvert.SerializeObject(playerData.UnlockedItems);
            document["CustomData"] = JsonConvert.SerializeObject(playerData.CustomData);
            document["LastLoginTime"] = playerData.LastLoginTime.ToString("O");
            document["CreatedTime"] = playerData.CreatedTime.ToString("O");
            document["Version"] = playerData.Version;
            document["UpdatedAt"] = DateTime.UtcNow.ToString("O");
            
            playerDataTableRef.PutItemAsync(document, (result) =>
            {
                operationComplete = true;
                if (result.Exception == null)
                {
                    success = true;
                    message = "Player data saved successfully";
                    Debug.Log($"[DynamoDB] Player data saved: {playerData.PlayerId}");
                }
                else
                {
                    success = false;
                    message = result.Exception.Message;
                    Debug.LogError($"[DynamoDB] Save failed: {message}");
                }
            });
        }
        catch (Exception e)
        {
            operationComplete = true;
            success = false;
            message = e.Message;
            Debug.LogError($"[DynamoDB] Save exception: {message}");
        }
        
        while (!operationComplete)
        {
            yield return new WaitForSeconds(0.1f);
        }
        
        onComplete?.Invoke(success, message);
    }
    
    public void LoadPlayerData(string playerId, System.Action<PlayerData, string> onComplete)
    {
        if (playerDataTableRef == null || !AWSManager.Instance.IsServiceAvailable())
        {
            onComplete?.Invoke(null, "Service not available");
            return;
        }
        
        StartCoroutine(LoadPlayerDataCoroutine(playerId, onComplete));
    }
    
    private IEnumerator LoadPlayerDataCoroutine(string playerId, System.Action<PlayerData, string> onComplete)
    {
        bool operationComplete = false;
        PlayerData playerData = null;
        string errorMessage = "";
        
        try
        {
            playerDataTableRef.GetItemAsync(playerId, (result) =>
            {
                operationComplete = true;
                if (result.Exception == null)
                {
                    if (result.Result != null)
                    {
                        playerData = DocumentToPlayerData(result.Result);
                        Debug.Log($"[DynamoDB] Player data loaded: {playerId}");
                    }
                    else
                    {
                        errorMessage = "Player data not found";
                    }
                }
                else
                {
                    errorMessage = result.Exception.Message;
                    Debug.LogError($"[DynamoDB] Load failed: {errorMessage}");
                }
            });
        }
        catch (Exception e)
        {
            operationComplete = true;
            errorMessage = e.Message;
            Debug.LogError($"[DynamoDB] Load exception: {errorMessage}");
        }
        
        while (!operationComplete)
        {
            yield return new WaitForSeconds(0.1f);
        }
        
        onComplete?.Invoke(playerData, errorMessage);
    }
    
    // Game Session Operations
    public void SaveGameSession(GameSession session, System.Action<bool, string> onComplete)
    {
        if (gameSessionsTableRef == null || !AWSManager.Instance.IsServiceAvailable())
        {
            onComplete?.Invoke(false, "Service not available");
            return;
        }
        
        StartCoroutine(SaveGameSessionCoroutine(session, onComplete));
    }
    
    private IEnumerator SaveGameSessionCoroutine(GameSession session, System.Action<bool, string> onComplete)
    {
        bool operationComplete = false;
        bool success = false;
        string message = "";
        
        try
        {
            var document = new Document();
            document["SessionId"] = session.SessionId;
            document["PlayerId"] = session.PlayerId;
            document["GameMode"] = session.GameMode;
            document["StartTime"] = session.StartTime.ToString("O");
            document["EndTime"] = session.EndTime.ToString("O");
            document["Score"] = session.Score;
            document["Duration"] = session.Duration;
            document["SessionData"] = JsonConvert.SerializeObject(session.SessionData);
            
            gameSessionsTableRef.PutItemAsync(document, (result) =>
            {
                operationComplete = true;
                if (result.Exception == null)
                {
                    success = true;
                    message = "Game session saved successfully";
                    Debug.Log($"[DynamoDB] Game session saved: {session.SessionId}");
                }
                else
                {
                    success = false;
                    message = result.Exception.Message;
                    Debug.LogError($"[DynamoDB] Session save failed: {message}");
                }
            });
        }
        catch (Exception e)
        {
            operationComplete = true;
            success = false;
            message = e.Message;
            Debug.LogError($"[DynamoDB] Session save exception: {message}");
        }
        
        while (!operationComplete)
        {
            yield return new WaitForSeconds(0.1f);
        }
        
        onComplete?.Invoke(success, message);
    }
    
    // Leaderboard Operations
    public void SubmitScore(LeaderboardEntry entry, System.Action<bool, string> onComplete)
    {
        if (leaderboardTableRef == null || !AWSManager.Instance.IsServiceAvailable())
        {
            onComplete?.Invoke(false, "Service not available");
            return;
        }
        
        StartCoroutine(SubmitScoreCoroutine(entry, onComplete));
    }
    
    private IEnumerator SubmitScoreCoroutine(LeaderboardEntry entry, System.Action<bool, string> onComplete)
    {
        bool operationComplete = false;
        bool success = false;
        string message = "";
        
        try
        {
            var document = new Document();
            document["LeaderboardType"] = entry.LeaderboardType;
            document["PlayerId"] = entry.PlayerId;
            document["Username"] = entry.Username;
            document["Score"] = entry.Score;
            document["AchievedAt"] = entry.AchievedAt.ToString("O");
            document["Metadata"] = JsonConvert.SerializeObject(entry.Metadata);
            
            // Use conditional put to only update if score is higher
            var putConfig = new PutItemOperationConfig
            {
                ConditionalExpression = "attribute_not_exists(Score) OR Score < :newScore",
                ExpressionAttributeValues = new Dictionary<string, DynamoDBEntry>
                {
                    {":newScore", entry.Score}
                }
            };
            
            leaderboardTableRef.PutItemAsync(document, putConfig, (result) =>
            {
                operationComplete = true;
                if (result.Exception == null)
                {
                    success = true;
                    message = "Score submitted successfully";
                    Debug.Log($"[DynamoDB] Score submitted: {entry.PlayerId} - {entry.Score}");
                }
                else
                {
                    success = false;
                    message = result.Exception.Message;
                    Debug.LogError($"[DynamoDB] Score submission failed: {message}");
                }
            });
        }
        catch (Exception e)
        {
            operationComplete = true;
            success = false;
            message = e.Message;
            Debug.LogError($"[DynamoDB] Score submission exception: {message}");
        }
        
        while (!operationComplete)
        {
            yield return new WaitForSeconds(0.1f);
        }
        
        onComplete?.Invoke(success, message);
    }
    
    public void GetLeaderboard(string leaderboardType, int limit, 
        System.Action<List<LeaderboardEntry>, string> onComplete)
    {
        if (leaderboardTableRef == null || !AWSManager.Instance.IsServiceAvailable())
        {
            onComplete?.Invoke(null, "Service not available");
            return;
        }
        
        StartCoroutine(GetLeaderboardCoroutine(leaderboardType, limit, onComplete));
    }
    
    private IEnumerator GetLeaderboardCoroutine(string leaderboardType, int limit,
        System.Action<List<LeaderboardEntry>, string> onComplete)
    {
        bool operationComplete = false;
        List<LeaderboardEntry> leaderboard = null;
        string errorMessage = "";
        
        try
        {
            var queryConfig = new QueryOperationConfig
            {
                KeyExpression = new Expression
                {
                    ExpressionStatement = "LeaderboardType = :leaderboardType",
                    ExpressionAttributeValues = new Dictionary<string, DynamoDBEntry>
                    {
                        {":leaderboardType", leaderboardType}
                    }
                },
                BackwardSearch = true, // Highest scores first
                Limit = limit
            };
            
            leaderboardTableRef.Query(queryConfig).GetRemainingAsync((result) =>
            {
                operationComplete = true;
                if (result.Exception == null)
                {
                    leaderboard = new List<LeaderboardEntry>();
                    foreach (var document in result.Result)
                    {
                        leaderboard.Add(DocumentToLeaderboardEntry(document));
                    }
                    Debug.Log($"[DynamoDB] Leaderboard loaded: {leaderboardType} ({leaderboard.Count} entries)");
                }
                else
                {
                    errorMessage = result.Exception.Message;
                    Debug.LogError($"[DynamoDB] Leaderboard query failed: {errorMessage}");
                }
            });
        }
        catch (Exception e)
        {
            operationComplete = true;
            errorMessage = e.Message;
            Debug.LogError($"[DynamoDB] Leaderboard query exception: {errorMessage}");
        }
        
        while (!operationComplete)
        {
            yield return new WaitForSeconds(0.1f);
        }
        
        onComplete?.Invoke(leaderboard, errorMessage);
    }
    
    // Helper Methods
    private PlayerData DocumentToPlayerData(Document document)
    {
        var playerData = new PlayerData
        {
            PlayerId = document["PlayerId"],
            Username = document["Username"],
            Level = document["Level"],
            Experience = document["Experience"],
            Coins = document["Coins"],
            Gems = document["Gems"],
            Version = document.ContainsKey("Version") ? document["Version"] : "1.0.0"
        };
        
        if (document.ContainsKey("UnlockedItems"))
        {
            playerData.UnlockedItems = JsonConvert.DeserializeObject<List<string>>(document["UnlockedItems"]);
        }
        
        if (document.ContainsKey("CustomData"))
        {
            playerData.CustomData = JsonConvert.DeserializeObject<Dictionary<string, object>>(document["CustomData"]);
        }
        
        if (document.ContainsKey("LastLoginTime"))
        {
            DateTime.TryParse(document["LastLoginTime"], out DateTime lastLogin);
            playerData.LastLoginTime = lastLogin;
        }
        
        if (document.ContainsKey("CreatedTime"))
        {
            DateTime.TryParse(document["CreatedTime"], out DateTime created);
            playerData.CreatedTime = created;
        }
        
        return playerData;
    }
    
    private LeaderboardEntry DocumentToLeaderboardEntry(Document document)
    {
        var entry = new LeaderboardEntry
        {
            LeaderboardType = document["LeaderboardType"],
            PlayerId = document["PlayerId"],
            Username = document["Username"],
            Score = document["Score"]
        };
        
        if (document.ContainsKey("AchievedAt"))
        {
            DateTime.TryParse(document["AchievedAt"], out DateTime achievedAt);
            entry.AchievedAt = achievedAt;
        }
        
        if (document.ContainsKey("Metadata"))
        {
            entry.Metadata = JsonConvert.DeserializeObject<Dictionary<string, object>>(document["Metadata"]);
        }
        
        return entry;
    }
}
```

### S3 Asset Storage Service
```csharp
// Scripts/AWS/S3Service.cs
using System;
using System.Collections;
using System.IO;
using UnityEngine;
using Amazon.S3;
using Amazon.S3.Model;
using System.Collections.Generic;

public class S3Service : MonoBehaviour
{
    [Header("S3 Configuration")]
    [SerializeField] private string bucketName = "your-game-bucket";
    [SerializeField] private string saveDataFolder = "save-data";
    [SerializeField] private string screenshotsFolder = "screenshots";
    [SerializeField] private string userContentFolder = "user-content";
    [SerializeField] private bool enableCaching = true;
    [SerializeField] private int cacheExpiryHours = 24;
    
    public static S3Service Instance { get; private set; }
    
    // Properties
    public bool IsInitialized => AWSManager.Instance != null && AWSManager.Instance.IsInitialized;
    
    // Events
    public System.Action<string, float> OnUploadProgress;
    public System.Action<string, float> OnDownloadProgress;
    
    private Dictionary<string, CachedFile> fileCache;
    
    private struct CachedFile
    {
        public byte[] data;
        public DateTime cacheTime;
        public bool IsExpired => DateTime.UtcNow.Subtract(cacheTime).TotalHours > Instance.cacheExpiryHours;
    }
    
    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            Initialize();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    private void Initialize()
    {
        fileCache = new Dictionary<string, CachedFile>();
    }
    
    // Save Data Operations
    public void UploadSaveData(string playerId, string saveFileName, byte[] saveData,
        System.Action<bool, string> onComplete)
    {
        string key = $"{saveDataFolder}/{playerId}/{saveFileName}";
        UploadFile(key, saveData, "application/octet-stream", onComplete);
    }
    
    public void DownloadSaveData(string playerId, string saveFileName,
        System.Action<byte[], string> onComplete)
    {
        string key = $"{saveDataFolder}/{playerId}/{saveFileName}";
        DownloadFile(key, onComplete);
    }
    
    public void ListSaveFiles(string playerId, System.Action<List<string>, string> onComplete)
    {
        string prefix = $"{saveDataFolder}/{playerId}/";
        ListFiles(prefix, onComplete);
    }
    
    public void DeleteSaveData(string playerId, string saveFileName,
        System.Action<bool, string> onComplete)
    {
        string key = $"{saveDataFolder}/{playerId}/{saveFileName}";
        DeleteFile(key, onComplete);
    }
    
    // Screenshot Operations
    public void UploadScreenshot(string playerId, Texture2D screenshot,
        System.Action<bool, string> onComplete)
    {
        if (screenshot == null)
        {
            onComplete?.Invoke(false, "Screenshot is null");
            return;
        }
        
        // Convert texture to PNG bytes
        byte[] imageData = screenshot.EncodeToPNG();
        string fileName = $"screenshot_{DateTime.UtcNow:yyyyMMdd_HHmmss}.png";
        string key = $"{screenshotsFolder}/{playerId}/{fileName}";
        
        UploadFile(key, imageData, "image/png", onComplete);
    }
    
    public void DownloadScreenshot(string playerId, string screenshotName,
        System.Action<Texture2D, string> onComplete)
    {
        string key = $"{screenshotsFolder}/{playerId}/{screenshotName}";
        
        DownloadFile(key, (data, error) =>
        {
            if (data != null)
            {
                Texture2D texture = new Texture2D(2, 2);
                if (texture.LoadImage(data))
                {
                    onComplete?.Invoke(texture, null);
                }
                else
                {
                    onComplete?.Invoke(null, "Failed to load image data");
                }
            }
            else
            {
                onComplete?.Invoke(null, error);
            }
        });
    }
    
    // User Content Operations
    public void UploadUserContent(string playerId, string contentName, byte[] contentData,
        string contentType, System.Action<bool, string> onComplete)
    {
        string key = $"{userContentFolder}/{playerId}/{contentName}";
        UploadFile(key, contentData, contentType, onComplete);
    }
    
    public void DownloadUserContent(string playerId, string contentName,
        System.Action<byte[], string> onComplete)
    {
        string key = $"{userContentFolder}/{playerId}/{contentName}";
        DownloadFile(key, onComplete);
    }
    
    // Generic File Operations
    public void UploadFile(string key, byte[] data, string contentType,
        System.Action<bool, string> onComplete)
    {
        if (!IsInitialized)
        {
            onComplete?.Invoke(false, "S3 service not initialized");
            return;
        }
        
        StartCoroutine(UploadFileCoroutine(key, data, contentType, onComplete));
    }
    
    private IEnumerator UploadFileCoroutine(string key, byte[] data, string contentType,
        System.Action<bool, string> onComplete)
    {
        bool operationComplete = false;
        bool success = false;
        string message = "";
        
        try
        {
            var request = new PutObjectRequest
            {
                BucketName = bucketName,
                Key = key,
                ContentType = contentType,
                InputStream = new MemoryStream(data),
                ServerSideEncryptionMethod = ServerSideEncryptionMethod.AES256
            };
            
            // Add metadata
            request.Metadata.Add("uploaded-by", AWSManager.Instance.CurrentUserId ?? "anonymous");
            request.Metadata.Add("upload-time", DateTime.UtcNow.ToString("O"));
            request.Metadata.Add("file-size", data.Length.ToString());
            
            AWSManager.Instance.S3Client.PutObjectAsync(request, (result) =>
            {
                operationComplete = true;
                if (result.Exception == null)
                {
                    success = true;
                    message = "File uploaded successfully";
                    Debug.Log($"[S3] File uploaded: {key} ({data.Length} bytes)");
                    
                    // Update cache
                    if (enableCaching)
                    {
                        fileCache[key] = new CachedFile
                        {
                            data = data,
                            cacheTime = DateTime.UtcNow
                        };
                    }
                }
                else
                {
                    success = false;
                    message = result.Exception.Message;
                    Debug.LogError($"[S3] Upload failed: {message}");
                }
            });
            
            // Monitor upload progress
            StartCoroutine(MonitorUploadProgress(key, data.Length));
        }
        catch (Exception e)
        {
            operationComplete = true;
            success = false;
            message = e.Message;
            Debug.LogError($"[S3] Upload exception: {message}");
        }
        
        while (!operationComplete)
        {
            yield return new WaitForSeconds(0.1f);
        }
        
        onComplete?.Invoke(success, message);
    }
    
    public void DownloadFile(string key, System.Action<byte[], string> onComplete)
    {
        if (!IsInitialized)
        {
            onComplete?.Invoke(null, "S3 service not initialized");
            return;
        }
        
        // Check cache first
        if (enableCaching && fileCache.ContainsKey(key))
        {
            var cached = fileCache[key];
            if (!cached.IsExpired)
            {
                Debug.Log($"[S3] Cache hit for: {key}");
                onComplete?.Invoke(cached.data, null);
                return;
            }
            else
            {
                fileCache.Remove(key);
            }
        }
        
        StartCoroutine(DownloadFileCoroutine(key, onComplete));
    }
    
    private IEnumerator DownloadFileCoroutine(string key, System.Action<byte[], string> onComplete)
    {
        bool operationComplete = false;
        byte[] fileData = null;
        string errorMessage = "";
        
        try
        {
            var request = new GetObjectRequest
            {
                BucketName = bucketName,
                Key = key
            };
            
            AWSManager.Instance.S3Client.GetObjectAsync(request, (result) =>
            {
                operationComplete = true;
                if (result.Exception == null)
                {
                    using (var stream = result.Response.ResponseStream)
                    using (var memoryStream = new MemoryStream())
                    {
                        stream.CopyTo(memoryStream);
                        fileData = memoryStream.ToArray();
                    }
                    
                    Debug.Log($"[S3] File downloaded: {key} ({fileData.Length} bytes)");
                    
                    // Update cache
                    if (enableCaching)
                    {
                        fileCache[key] = new CachedFile
                        {
                            data = fileData,
                            cacheTime = DateTime.UtcNow
                        };
                    }
                }
                else
                {
                    errorMessage = result.Exception.Message;
                    Debug.LogError($"[S3] Download failed: {errorMessage}");
                }
            });
            
            // Monitor download progress
            StartCoroutine(MonitorDownloadProgress(key));
        }
        catch (Exception e)
        {
            operationComplete = true;
            errorMessage = e.Message;
            Debug.LogError($"[S3] Download exception: {errorMessage}");
        }
        
        while (!operationComplete)
        {
            yield return new WaitForSeconds(0.1f);
        }
        
        onComplete?.Invoke(fileData, string.IsNullOrEmpty(errorMessage) ? null : errorMessage);
    }
    
    public void DeleteFile(string key, System.Action<bool, string> onComplete)
    {
        if (!IsInitialized)
        {
            onComplete?.Invoke(false, "S3 service not initialized");
            return;
        }
        
        StartCoroutine(DeleteFileCoroutine(key, onComplete));
    }
    
    private IEnumerator DeleteFileCoroutine(string key, System.Action<bool, string> onComplete)
    {
        bool operationComplete = false;
        bool success = false;
        string message = "";
        
        try
        {
            var request = new DeleteObjectRequest
            {
                BucketName = bucketName,
                Key = key
            };
            
            AWSManager.Instance.S3Client.DeleteObjectAsync(request, (result) =>
            {
                operationComplete = true;
                if (result.Exception == null)
                {
                    success = true;
                    message = "File deleted successfully";
                    Debug.Log($"[S3] File deleted: {key}");
                    
                    // Remove from cache
                    fileCache.Remove(key);
                }
                else
                {
                    success = false;
                    message = result.Exception.Message;
                    Debug.LogError($"[S3] Delete failed: {message}");
                }
            });
        }
        catch (Exception e)
        {
            operationComplete = true;
            success = false;
            message = e.Message;
            Debug.LogError($"[S3] Delete exception: {message}");
        }
        
        while (!operationComplete)
        {
            yield return new WaitForSeconds(0.1f);
        }
        
        onComplete?.Invoke(success, message);
    }
    
    public void ListFiles(string prefix, System.Action<List<string>, string> onComplete)
    {
        if (!IsInitialized)
        {
            onComplete?.Invoke(null, "S3 service not initialized");
            return;
        }
        
        StartCoroutine(ListFilesCoroutine(prefix, onComplete));
    }
    
    private IEnumerator ListFilesCoroutine(string prefix, System.Action<List<string>, string> onComplete)
    {
        bool operationComplete = false;
        List<string> fileList = null;
        string errorMessage = "";
        
        try
        {
            var request = new ListObjectsV2Request
            {
                BucketName = bucketName,
                Prefix = prefix,
                MaxKeys = 1000
            };
            
            AWSManager.Instance.S3Client.ListObjectsV2Async(request, (result) =>
            {
                operationComplete = true;
                if (result.Exception == null)
                {
                    fileList = new List<string>();
                    foreach (var obj in result.Response.S3Objects)
                    {
                        // Remove prefix from key to get just the filename
                        string fileName = obj.Key.Substring(prefix.Length);
                        if (!string.IsNullOrEmpty(fileName))
                        {
                            fileList.Add(fileName);
                        }
                    }
                    Debug.Log($"[S3] Listed {fileList.Count} files with prefix: {prefix}");
                }
                else
                {
                    errorMessage = result.Exception.Message;
                    Debug.LogError($"[S3] List files failed: {errorMessage}");
                }
            });
        }
        catch (Exception e)
        {
            operationComplete = true;
            errorMessage = e.Message;
            Debug.LogError($"[S3] List files exception: {errorMessage}");
        }
        
        while (!operationComplete)
        {
            yield return new WaitForSeconds(0.1f);
        }
        
        onComplete?.Invoke(fileList, string.IsNullOrEmpty(errorMessage) ? null : errorMessage);
    }
    
    // Progress Monitoring
    private IEnumerator MonitorUploadProgress(string key, long totalBytes)
    {
        float startTime = Time.time;
        while (Time.time - startTime < 30f) // 30 second timeout
        {
            // This is a simplified progress simulation
            // In a real implementation, you'd track actual progress
            float progress = Mathf.Clamp01((Time.time - startTime) / 5f);
            OnUploadProgress?.Invoke(key, progress);
            
            if (progress >= 1f) break;
            yield return new WaitForSeconds(0.1f);
        }
    }
    
    private IEnumerator MonitorDownloadProgress(string key)
    {
        float startTime = Time.time;
        while (Time.time - startTime < 30f) // 30 second timeout
        {
            // This is a simplified progress simulation
            // In a real implementation, you'd track actual progress
            float progress = Mathf.Clamp01((Time.time - startTime) / 3f);
            OnDownloadProgress?.Invoke(key, progress);
            
            if (progress >= 1f) break;
            yield return new WaitForSeconds(0.1f);
        }
    }
    
    // Utility Methods
    public void ClearCache()
    {
        fileCache.Clear();
        Debug.Log("[S3] File cache cleared");
    }
    
    public void CleanExpiredCache()
    {
        var expiredKeys = new List<string>();
        foreach (var kvp in fileCache)
        {
            if (kvp.Value.IsExpired)
            {
                expiredKeys.Add(kvp.Key);
            }
        }
        
        foreach (var key in expiredKeys)
        {
            fileCache.Remove(key);
        }
        
        if (expiredKeys.Count > 0)
        {
            Debug.Log($"[S3] Cleaned {expiredKeys.Count} expired cache entries");
        }
    }
    
    public long GetCacheSize()
    {
        long totalSize = 0;
        foreach (var cached in fileCache.Values)
        {
            totalSize += cached.data.Length;
        }
        return totalSize;
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### AWS Architecture Optimization
```
PROMPT TEMPLATE - AWS Gaming Architecture:

"Design an optimal AWS architecture for this Unity game:

Game Details:
- Type: [Mobile/PC/Multiplayer/etc.]
- Expected Users: [1K/10K/100K/1M+]
- Data Requirements: [User profiles/Leaderboards/Real-time/etc.]
- Budget Considerations: [Startup/Growth/Enterprise]

Create architecture including:
1. AWS service selection and configuration
2. Cost optimization strategies
3. Scalability and auto-scaling setup
4. Security and compliance considerations
5. Monitoring and observability implementation
6. Disaster recovery and backup strategies
7. Performance optimization recommendations
8. Unity-specific integration patterns
9. Development vs production environment setup"
```

### DynamoDB Schema Design
```
PROMPT TEMPLATE - DynamoDB Game Schema:

"Design optimal DynamoDB schemas for this Unity game data:

Game Data Requirements:
```
[DESCRIBE YOUR DATA MODELS]
```

Usage Patterns:
- Read/Write Frequency: [High/Medium/Low for each data type]
- Query Patterns: [How data will be accessed]
- Scale Requirements: [Expected growth patterns]

Generate schemas including:
1. Table design with partition and sort keys
2. Global Secondary Index (GSI) strategies
3. Local Secondary Index (LSI) considerations
4. Attribute definitions and data types
5. Capacity planning and auto-scaling
6. Query optimization recommendations
7. Cost optimization through efficient access patterns
8. Unity integration code examples"
```

## 💡 Key AWS Integration Principles

### Essential AWS Unity Checklist
- **Security first** - Use IAM roles, Cognito for authentication, encrypt data
- **Cost optimization** - Monitor usage, use appropriate instance types, implement caching
- **Scalability planning** - Design for growth, use auto-scaling, consider global regions  
- **Performance monitoring** - CloudWatch metrics, application insights, error tracking
- **Disaster recovery** - Multi-region backup, data replication, recovery procedures
- **Development workflow** - Separate dev/staging/prod environments
- **Mobile optimization** - Handle offline scenarios, minimize data usage
- **Compliance awareness** - GDPR, COPPA, platform-specific requirements

### Common AWS Unity Integration Challenges
1. **Authentication complexity** - Cognito setup and token management
2. **Network latency** - Global distribution and edge optimization
3. **Cost management** - Monitoring and controlling AWS service costs
4. **Data synchronization** - Offline/online state management
5. **Security configuration** - Proper IAM policies and encryption
6. **Platform differences** - iOS/Android/PC specific considerations
7. **Debugging complexity** - Troubleshooting cloud service issues
8. **Vendor lock-in** - Architecture decisions and migration considerations

This comprehensive AWS integration provides Unity developers with enterprise-grade cloud infrastructure capabilities, enabling scalable user management, data storage, and backend services while maintaining security, performance, and cost-effectiveness across mobile and desktop platforms.