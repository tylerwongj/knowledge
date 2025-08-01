# 02-Google-Cloud-Unity.md

## 🎯 Learning Objectives
- Master Google Cloud Platform integration for Unity applications
- Implement Firebase real-time database and authentication systems
- Design scalable Google Cloud Functions for serverless game logic
- Develop efficient Cloud Storage solutions for Unity asset management

## 🔧 Google Cloud Platform Unity Integration

### Firebase Unity SDK Integration
```csharp
// Scripts/Cloud/FirebaseManager.cs
using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using Firebase;
using Firebase.Auth;
using Firebase.Database;
using Firebase.Storage;
using Firebase.Functions;
using Firebase.Analytics;

public class FirebaseManager : MonoBehaviour
{
    [Header("Firebase Configuration")]
    [SerializeField] private bool enableAnalytics = true;
    [SerializeField] private bool enableCrashlytics = true;
    [SerializeField] private string databaseURL = "https://your-project.firebaseio.com/";
    [SerializeField] private string storageBucket = "your-project.appspot.com";
    
    public static FirebaseManager Instance { get; private set; }
    
    // Firebase services
    public FirebaseApp App { get; private set; }
    public FirebaseAuth Auth { get; private set; }
    public DatabaseReference Database { get; private set; }
    public FirebaseStorage Storage { get; private set; }
    public FirebaseFunctions Functions { get; private set; }
    
    // Properties
    public bool IsInitialized { get; private set; }
    public FirebaseUser CurrentUser => Auth?.CurrentUser;
    public bool IsAuthenticated => CurrentUser != null;
    
    // Events
    public System.Action OnFirebaseInitialized;
    public System.Action<FirebaseUser> OnUserSignedIn;
    public System.Action OnUserSignedOut;
    public System.Action<string> OnFirebaseError;
    
    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            StartCoroutine(InitializeFirebase());
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    private IEnumerator InitializeFirebase()
    {
        Debug.Log("[Firebase] Initializing Firebase...");
        
        var initTask = FirebaseApp.CheckAndFixDependenciesAsync();
        yield return new WaitUntil(() => initTask.IsCompleted);
        
        if (initTask.Result == DependencyStatus.Available)
        {
            App = FirebaseApp.DefaultInstance;
            
            // Initialize Firebase services
            Auth = FirebaseAuth.DefaultInstance;
            Database = FirebaseDatabase.DefaultInstance.RootReference;
            Storage = FirebaseStorage.DefaultInstance;
            Functions = FirebaseFunctions.DefaultInstance;
            
            // Configure database URL if specified
            if (!string.IsNullOrEmpty(databaseURL))
            {
                Database = FirebaseDatabase.GetInstance(databaseURL).RootReference;
            }
            
            // Configure storage bucket if specified
            if (!string.IsNullOrEmpty(storageBucket))
            {
                Storage = FirebaseStorage.GetInstance($"gs://{storageBucket}");
            }
            
            // Setup authentication listeners
            Auth.StateChanged += OnAuthStateChanged;
            Auth.IdTokenChanged += OnIdTokenChanged;
            
            // Initialize Analytics if enabled
            if (enableAnalytics)
            {
                FirebaseAnalytics.SetAnalyticsCollectionEnabled(true);
                Debug.Log("[Firebase] Analytics enabled");
            }
            
            IsInitialized = true;
            Debug.Log("[Firebase] Firebase initialized successfully");
            OnFirebaseInitialized?.Invoke();
        }
        else
        {
            string error = $"Failed to initialize Firebase: {initTask.Result}";
            Debug.LogError($"[Firebase] {error}");
            OnFirebaseError?.Invoke(error);
        }
    }
    
    // Authentication Methods
    public async Task<bool> SignInAnonymouslyAsync()
    {
        try
        {
            var result = await Auth.SignInAnonymouslyAsync();
            Debug.Log($"[Firebase] Anonymous sign in successful: {result.UserId}");
            return true;
        }
        catch (FirebaseException e)
        {
            Debug.LogError($"[Firebase] Anonymous sign in failed: {e.Message}");
            OnFirebaseError?.Invoke(e.Message);
            return false;
        }
    }
    
    public async Task<bool> SignInWithEmailAsync(string email, string password)
    {
        try
        {
            var result = await Auth.SignInWithEmailAndPasswordAsync(email, password);
            Debug.Log($"[Firebase] Email sign in successful: {result.Email}");
            return true;
        }
        catch (FirebaseException e)
        {
            Debug.LogError($"[Firebase] Email sign in failed: {e.Message}");
            OnFirebaseError?.Invoke(e.Message);
            return false;
        }
    }
    
    public async Task<bool> CreateUserWithEmailAsync(string email, string password)
    {
        try
        {
            var result = await Auth.CreateUserWithEmailAndPasswordAsync(email, password);
            Debug.Log($"[Firebase] User creation successful: {result.Email}");
            return true;
        }
        catch (FirebaseException e)
        {
            Debug.LogError($"[Firebase] User creation failed: {e.Message}");
            OnFirebaseError?.Invoke(e.Message);
            return false;
        }
    }
    
    public void SignOut()
    {
        if (Auth != null)
        {
            Auth.SignOut();
            Debug.Log("[Firebase] User signed out");
        }
    }
    
    // Database Operations
    public async Task<T> GetDataAsync<T>(string path)
    {
        try
        {
            var snapshot = await Database.Child(path).GetValueAsync();
            
            if (snapshot.Exists)
            {
                string json = snapshot.GetRawJsonValue();
                return JsonUtility.FromJson<T>(json);
            }
            
            return default(T);
        }
        catch (Exception e)
        {
            Debug.LogError($"[Firebase] Get data failed for {path}: {e.Message}");
            OnFirebaseError?.Invoke(e.Message);
            return default(T);
        }
    }
    
    public async Task<bool> SetDataAsync<T>(string path, T data)
    {
        try
        {
            string json = JsonUtility.ToJson(data);
            await Database.Child(path).SetRawJsonValueAsync(json);
            Debug.Log($"[Firebase] Data set successfully at {path}");
            return true;
        }
        catch (Exception e)
        {
            Debug.LogError($"[Firebase] Set data failed for {path}: {e.Message}");
            OnFirebaseError?.Invoke(e.Message);
            return false;
        }
    }
    
    public async Task<bool> UpdateDataAsync(string path, Dictionary<string, object> updates)
    {
        try
        {
            await Database.Child(path).UpdateChildrenAsync(updates);
            Debug.Log($"[Firebase] Data updated successfully at {path}");
            return true;
        }
        catch (Exception e)
        {
            Debug.LogError($"[Firebase] Update data failed for {path}: {e.Message}");
            OnFirebaseError?.Invoke(e.Message);
            return false;
        }
    }
    
    public async Task<bool> DeleteDataAsync(string path)
    {
        try
        {
            await Database.Child(path).RemoveValueAsync();
            Debug.Log($"[Firebase] Data deleted successfully at {path}");
            return true;
        }
        catch (Exception e)
        {
            Debug.LogError($"[Firebase] Delete data failed for {path}: {e.Message}");
            OnFirebaseError?.Invoke(e.Message);
            return false;
        }
    }
    
    // Real-time Database Listeners
    public void ListenToData(string path, System.Action<DataSnapshot> onDataChanged)
    {
        Database.Child(path).ValueChanged += (sender, args) =>
        {
            if (args.DatabaseError != null)
            {
                Debug.LogError($"[Firebase] Database error: {args.DatabaseError.Message}");
                OnFirebaseError?.Invoke(args.DatabaseError.Message);
                return;
            }
            
            onDataChanged?.Invoke(args.Snapshot);
        };
    }
    
    public void StopListening(string path)
    {
        // Remove all listeners for the specified path
        Database.Child(path).ValueChanged -= null;
    }
    
    // Cloud Storage Operations
    public async Task<string> UploadFileAsync(string localPath, string remotePath, 
        System.Action<float> onProgress = null)
    {
        try
        {
            var fileRef = Storage.RootReference.Child(remotePath);
            
            var uploadTask = fileRef.PutFileAsync(localPath);
            
            // Monitor progress if callback provided
            if (onProgress != null)
            {
                uploadTask.Progress += (snapshot) =>
                {
                    float progress = (float)snapshot.BytesTransferred / snapshot.TotalByteCount;
                    onProgress(progress);
                };
            }
            
            await uploadTask;
            
            // Get download URL
            var downloadUrl = await fileRef.GetDownloadUrlAsync();
            Debug.Log($"[Firebase] File uploaded successfully: {downloadUrl}");
            
            return downloadUrl.ToString();
        }
        catch (Exception e)
        {
            Debug.LogError($"[Firebase] File upload failed: {e.Message}");
            OnFirebaseError?.Invoke(e.Message);
            return null;
        }
    }
    
    public async Task<byte[]> DownloadFileAsync(string remotePath, System.Action<float> onProgress = null)
    {
        try
        {
            var fileRef = Storage.RootReference.Child(remotePath);
            
            // Get file metadata first to track progress
            var metadata = await fileRef.GetMetadataAsync();
            var maxDownloadSize = metadata.SizeBytes;
            
            var downloadTask = fileRef.GetBytesAsync(maxDownloadSize);
            
            // Monitor progress if callback provided
            if (onProgress != null)
            {
                downloadTask.Progress += (snapshot) =>
                {
                    float progress = (float)snapshot.BytesTransferred / maxDownloadSize;
                    onProgress(progress);
                };
            }
            
            var fileBytes = await downloadTask;
            Debug.Log($"[Firebase] File downloaded successfully: {fileBytes.Length} bytes");
            
            return fileBytes;
        }
        catch (Exception e)
        {
            Debug.LogError($"[Firebase] File download failed: {e.Message}");
            OnFirebaseError?.Invoke(e.Message);
            return null;
        }
    }
    
    public async Task<bool> DeleteFileAsync(string remotePath)
    {
        try
        {
            var fileRef = Storage.RootReference.Child(remotePath);
            await fileRef.DeleteAsync();
            Debug.Log($"[Firebase] File deleted successfully: {remotePath}");
            return true;
        }
        catch (Exception e)
        {
            Debug.LogError($"[Firebase] File deletion failed: {e.Message}");
            OnFirebaseError?.Invoke(e.Message);
            return false;
        }
    }
    
    // Cloud Functions
    public async Task<T> CallFunctionAsync<T>(string functionName, object data = null)
    {
        try
        {
            var function = Functions.GetHttpsCallable(functionName);
            var result = await function.CallAsync(data);
            
            string json = result.Data.ToString();
            return JsonUtility.FromJson<T>(json);
        }
        catch (Exception e)
        {
            Debug.LogError($"[Firebase] Function call failed for {functionName}: {e.Message}");
            OnFirebaseError?.Invoke(e.Message);
            return default(T);
        }
    }
    
    // Analytics
    public void LogEvent(string eventName, Dictionary<string, object> parameters = null)
    {
        if (!enableAnalytics) return;
        
        if (parameters != null && parameters.Count > 0)
        {
            var firebaseParams = new Parameter[parameters.Count];
            int index = 0;
            
            foreach (var param in parameters)
            {
                firebaseParams[index] = new Parameter(param.Key, param.Value.ToString());
                index++;
            }
            
            FirebaseAnalytics.LogEvent(eventName, firebaseParams);
        }
        else
        {
            FirebaseAnalytics.LogEvent(eventName);
        }
        
        Debug.Log($"[Firebase] Analytics event logged: {eventName}");
    }
    
    public void SetUserProperty(string name, string value)
    {
        if (!enableAnalytics) return;
        
        FirebaseAnalytics.SetUserProperty(name, value);
        Debug.Log($"[Firebase] User property set: {name} = {value}");
    }
    
    // Event Handlers
    private void OnAuthStateChanged(object sender, EventArgs eventArgs)
    {
        if (Auth.CurrentUser != null)
        {
            Debug.Log($"[Firebase] User signed in: {Auth.CurrentUser.UserId}");
            OnUserSignedIn?.Invoke(Auth.CurrentUser);
        }
        else
        {
            Debug.Log("[Firebase] User signed out");
            OnUserSignedOut?.Invoke();
        }
    }
    
    private void OnIdTokenChanged(object sender, EventArgs eventArgs)
    {
        Debug.Log("[Firebase] ID token changed");
    }
    
    // Utility Methods
    public async Task<string> GetUserIdTokenAsync()
    {
        if (CurrentUser != null)
        {
            try
            {
                return await CurrentUser.TokenAsync(false);
            }
            catch (Exception e)
            {
                Debug.LogError($"[Firebase] Failed to get ID token: {e.Message}");
                return null;
            }
        }
        
        return null;
    }
    
    public async Task<bool> SendEmailVerificationAsync()
    {
        if (CurrentUser != null)
        {
            try
            {
                await CurrentUser.SendEmailVerificationAsync();
                Debug.Log("[Firebase] Email verification sent");
                return true;
            }
            catch (Exception e)
            {
                Debug.LogError($"[Firebase] Failed to send email verification: {e.Message}");
                OnFirebaseError?.Invoke(e.Message);
                return false;
            }
        }
        
        return false;
    }
    
    public async Task<bool> SendPasswordResetAsync(string email)
    {
        try
        {
            await Auth.SendPasswordResetEmailAsync(email);
            Debug.Log($"[Firebase] Password reset email sent to {email}");
            return true;
        }
        catch (Exception e)
        {
            Debug.LogError($"[Firebase] Failed to send password reset: {e.Message}");
            OnFirebaseError?.Invoke(e.Message);
            return false;
        }
    }
    
    private void OnDestroy()
    {
        if (Auth != null)
        {
            Auth.StateChanged -= OnAuthStateChanged;
            Auth.IdTokenChanged -= OnIdTokenChanged;
        }
    }
}
```

### Google Cloud Functions Integration
```csharp
// Scripts/Cloud/CloudFunctionsService.cs
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;

public class CloudFunctionsService : MonoBehaviour
{
    public static CloudFunctionsService Instance { get; private set; }
    
    // Events
    public System.Action<string, object> OnFunctionResult;
    public System.Action<string, string> OnFunctionError;
    
    [Serializable]
    public class PlayerData
    {
        public string playerId;
        public string username;
        public int level;
        public long experience;
        public int coins;
        public Dictionary<string, object> stats;
    }
    
    [Serializable]
    public class LeaderboardEntry
    {
        public string playerId;
        public string username;
        public long score;
        public DateTime timestamp;
    }
    
    [Serializable]
    public class MatchmakingRequest
    {
        public string playerId;
        public string gameMode;
        public int skillLevel;
        public string region;
    }
    
    [Serializable]
    public class MatchResult
    {
        public string matchId;
        public List<string> playerIds;
        public string serverEndpoint;
        public DateTime expiresAt;
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
    
    // Player Management Functions
    public async Task<PlayerData> CreatePlayerAsync(string username, string email)
    {
        var requestData = new
        {
            username = username,
            email = email,
            timestamp = DateTime.UtcNow
        };
        
        try
        {
            var result = await FirebaseManager.Instance.CallFunctionAsync<PlayerData>("createPlayer", requestData);
            Debug.Log($"[CloudFunctions] Player created: {result.playerId}");
            OnFunctionResult?.Invoke("createPlayer", result);
            return result;
        }
        catch (Exception e)
        {
            Debug.LogError($"[CloudFunctions] Create player failed: {e.Message}");
            OnFunctionError?.Invoke("createPlayer", e.Message);
            return null;
        }
    }
    
    public async Task<PlayerData> GetPlayerDataAsync(string playerId)
    {
        var requestData = new { playerId = playerId };
        
        try
        {
            var result = await FirebaseManager.Instance.CallFunctionAsync<PlayerData>("getPlayerData", requestData);
            Debug.Log($"[CloudFunctions] Player data retrieved: {result.username}");
            OnFunctionResult?.Invoke("getPlayerData", result);
            return result;
        }
        catch (Exception e)
        {
            Debug.LogError($"[CloudFunctions] Get player data failed: {e.Message}");
            OnFunctionError?.Invoke("getPlayerData", e.Message);
            return null;
        }
    }
    
    public async Task<bool> UpdatePlayerStatsAsync(string playerId, Dictionary<string, object> stats)
    {
        var requestData = new
        {
            playerId = playerId,
            stats = stats,
            timestamp = DateTime.UtcNow
        };
        
        try
        {
            var result = await FirebaseManager.Instance.CallFunctionAsync<object>("updatePlayerStats", requestData);
            Debug.Log($"[CloudFunctions] Player stats updated for {playerId}");
            OnFunctionResult?.Invoke("updatePlayerStats", result);
            return true;
        }
        catch (Exception e)
        {
            Debug.LogError($"[CloudFunctions] Update player stats failed: {e.Message}");
            OnFunctionError?.Invoke("updatePlayerStats", e.Message);
            return false;
        }
    }
    
    // Leaderboard Functions
    public async Task<List<LeaderboardEntry>> GetLeaderboardAsync(string leaderboardType, int limit = 100)
    {
        var requestData = new
        {
            leaderboardType = leaderboardType,
            limit = limit
        };
        
        try
        {
            var result = await FirebaseManager.Instance.CallFunctionAsync<List<LeaderboardEntry>>("getLeaderboard", requestData);
            Debug.Log($"[CloudFunctions] Leaderboard retrieved: {result.Count} entries");
            OnFunctionResult?.Invoke("getLeaderboard", result);
            return result;
        }
        catch (Exception e)
        {
            Debug.LogError($"[CloudFunctions] Get leaderboard failed: {e.Message}");
            OnFunctionError?.Invoke("getLeaderboard", e.Message);
            return null;
        }
    }
    
    public async Task<LeaderboardEntry> SubmitScoreAsync(string playerId, string leaderboardType, long score)
    {
        var requestData = new
        {
            playerId = playerId,
            leaderboardType = leaderboardType,
            score = score,
            timestamp = DateTime.UtcNow
        };
        
        try
        {
            var result = await FirebaseManager.Instance.CallFunctionAsync<LeaderboardEntry>("submitScore", requestData);
            Debug.Log($"[CloudFunctions] Score submitted: {score} for {leaderboardType}");
            OnFunctionResult?.Invoke("submitScore", result);
            return result;
        }
        catch (Exception e)
        {
            Debug.LogError($"[CloudFunctions] Submit score failed: {e.Message}");
            OnFunctionError?.Invoke("submitScore", e.Message);
            return null;
        }
    }
    
    // Matchmaking Functions
    public async Task<MatchResult> FindMatchAsync(string playerId, string gameMode, int skillLevel)
    {
        var requestData = new MatchmakingRequest
        {
            playerId = playerId,
            gameMode = gameMode,
            skillLevel = skillLevel,
            region = GetPlayerRegion()
        };
        
        try
        {
            var result = await FirebaseManager.Instance.CallFunctionAsync<MatchResult>("findMatch", requestData);
            Debug.Log($"[CloudFunctions] Match found: {result.matchId}");
            OnFunctionResult?.Invoke("findMatch", result);
            return result;
        }
        catch (Exception e)
        {
            Debug.LogError($"[CloudFunctions] Find match failed: {e.Message}");
            OnFunctionError?.Invoke("findMatch", e.Message);
            return null;
        }
    }
    
    public async Task<bool> CancelMatchmakingAsync(string playerId)
    {
        var requestData = new { playerId = playerId };
        
        try
        {
            var result = await FirebaseManager.Instance.CallFunctionAsync<object>("cancelMatchmaking", requestData);
            Debug.Log($"[CloudFunctions] Matchmaking cancelled for {playerId}");
            OnFunctionResult?.Invoke("cancelMatchmaking", result);
            return true;
        }
        catch (Exception e)
        {
            Debug.LogError($"[CloudFunctions] Cancel matchmaking failed: {e.Message}");
            OnFunctionError?.Invoke("cancelMatchmaking", e.Message);
            return false;
        }
    }
    
    // Game Session Functions
    public async Task<string> StartGameSessionAsync(string matchId, List<string> playerIds)
    {
        var requestData = new
        {
            matchId = matchId,
            playerIds = playerIds,
            timestamp = DateTime.UtcNow
        };
        
        try
        {
            var result = await FirebaseManager.Instance.CallFunctionAsync<Dictionary<string, object>>("startGameSession", requestData);
            string sessionId = result["sessionId"].ToString();
            Debug.Log($"[CloudFunctions] Game session started: {sessionId}");
            OnFunctionResult?.Invoke("startGameSession", result);
            return sessionId;
        }
        catch (Exception e)
        {
            Debug.LogError($"[CloudFunctions] Start game session failed: {e.Message}");
            OnFunctionError?.Invoke("startGameSession", e.Message);
            return null;
        }
    }
    
    public async Task<bool> EndGameSessionAsync(string sessionId, Dictionary<string, object> sessionData)
    {
        var requestData = new
        {
            sessionId = sessionId,
            sessionData = sessionData,
            endTime = DateTime.UtcNow
        };
        
        try
        {
            var result = await FirebaseManager.Instance.CallFunctionAsync<object>("endGameSession", requestData);
            Debug.Log($"[CloudFunctions] Game session ended: {sessionId}");
            OnFunctionResult?.Invoke("endGameSession", result);
            return true;
        }
        catch (Exception e)
        {
            Debug.LogError($"[CloudFunctions] End game session failed: {e.Message}");
            OnFunctionError?.Invoke("endGameSession", e.Message);
            return false;
        }
    }
    
    // In-App Purchase Validation
    public async Task<bool> ValidatePurchaseAsync(string purchaseToken, string productId, string platform)
    {
        var requestData = new
        {
            purchaseToken = purchaseToken,
            productId = productId,
            platform = platform,
            playerId = FirebaseManager.Instance.CurrentUser?.UserId,
            timestamp = DateTime.UtcNow
        };
        
        try
        {
            var result = await FirebaseManager.Instance.CallFunctionAsync<Dictionary<string, object>>("validatePurchase", requestData);
            bool isValid = Convert.ToBoolean(result["valid"]);
            Debug.Log($"[CloudFunctions] Purchase validation: {isValid}");
            OnFunctionResult?.Invoke("validatePurchase", result);
            return isValid;
        }
        catch (Exception e)
        {
            Debug.LogError($"[CloudFunctions] Purchase validation failed: {e.Message}");
            OnFunctionError?.Invoke("validatePurchase", e.Message);
            return false;
        }
    }
    
    // Moderation Functions
    public async Task<bool> ReportPlayerAsync(string reportedPlayerId, string reason, string description)
    {
        var requestData = new
        {
            reportedPlayerId = reportedPlayerId,
            reporterPlayerId = FirebaseManager.Instance.CurrentUser?.UserId,
            reason = reason,
            description = description,
            timestamp = DateTime.UtcNow
        };
        
        try
        {
            var result = await FirebaseManager.Instance.CallFunctionAsync<object>("reportPlayer", requestData);
            Debug.Log($"[CloudFunctions] Player reported: {reportedPlayerId}");
            OnFunctionResult?.Invoke("reportPlayer", result);
            return true;
        }
        catch (Exception e)
        {
            Debug.LogError($"[CloudFunctions] Report player failed: {e.Message}");
            OnFunctionError?.Invoke("reportPlayer", e.Message);
            return false;
        }
    }
    
    // Admin Functions
    public async Task<bool> BanPlayerAsync(string playerId, string reason, int durationHours)
    {
        var requestData = new
        {
            playerId = playerId,
            reason = reason,
            durationHours = durationHours,
            adminId = FirebaseManager.Instance.CurrentUser?.UserId,
            timestamp = DateTime.UtcNow
        };
        
        try
        {
            var result = await FirebaseManager.Instance.CallFunctionAsync<object>("banPlayer", requestData);
            Debug.Log($"[CloudFunctions] Player banned: {playerId}");
            OnFunctionResult?.Invoke("banPlayer", result);
            return true;
        }
        catch (Exception e)
        {
            Debug.LogError($"[CloudFunctions] Ban player failed: {e.Message}");
            OnFunctionError?.Invoke("banPlayer", e.Message);
            return false;
        }
    }
    
    // Utility Methods
    private string GetPlayerRegion()
    {
        // Implement region detection logic
        // This could be based on IP geolocation or user preference
        return "us-central1"; // Default region
    }
    
    public async Task<Dictionary<string, object>> GetServerStatusAsync()
    {
        try
        {
            var result = await FirebaseManager.Instance.CallFunctionAsync<Dictionary<string, object>>("getServerStatus", null);
            Debug.Log("[CloudFunctions] Server status retrieved");
            OnFunctionResult?.Invoke("getServerStatus", result);
            return result;
        }
        catch (Exception e)
        {
            Debug.LogError($"[CloudFunctions] Get server status failed: {e.Message}");
            OnFunctionError?.Invoke("getServerStatus", e.Message);
            return null;
        }
    }
}
```

### Google Cloud Storage Manager
```csharp
// Scripts/Cloud/CloudStorageManager.cs
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using UnityEngine;

public class CloudStorageManager : MonoBehaviour
{
    [Header("Storage Configuration")]
    [SerializeField] private string assetsBucket = "game-assets";
    [SerializeField] private string userDataBucket = "user-data";
    [SerializeField] private bool enableCompression = true;
    [SerializeField] private int maxConcurrentUploads = 3;
    
    public static CloudStorageManager Instance { get; private set; }
    
    // Events
    public System.Action<string, float> OnUploadProgress;
    public System.Action<string, float> OnDownloadProgress;
    public System.Action<string> OnUploadComplete;
    public System.Action<string> OnDownloadComplete;
    public System.Action<string, string> OnStorageError;
    
    // Upload queue management
    private Queue<UploadTask> uploadQueue;
    private List<UploadTask> activeUploads;
    
    private class UploadTask
    {
        public string localPath;
        public string remotePath;
        public string bucket;
        public System.Action<string> onComplete;
        public System.Action<string> onError;
        public System.Action<float> onProgress;
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
        uploadQueue = new Queue<UploadTask>();
        activeUploads = new List<UploadTask>();
        
        StartCoroutine(ProcessUploadQueue());
    }
    
    // Asset Management
    public async Task<string> UploadAssetAsync(string localPath, string assetId, 
        System.Action<float> onProgress = null)
    {
        string remotePath = $"assets/{assetId}/{Path.GetFileName(localPath)}";
        
        try
        {
            string downloadUrl = await FirebaseManager.Instance.UploadFileAsync(
                localPath, remotePath, onProgress);
            
            if (!string.IsNullOrEmpty(downloadUrl))
            {
                Debug.Log($"[CloudStorage] Asset uploaded: {assetId}");
                OnUploadComplete?.Invoke(assetId);
                
                // Update asset registry
                await UpdateAssetRegistry(assetId, downloadUrl, localPath);
            }
            
            return downloadUrl;
        }
        catch (Exception e)
        {
            Debug.LogError($"[CloudStorage] Asset upload failed: {e.Message}");
            OnStorageError?.Invoke("upload", e.Message);
            return null;
        }
    }
    
    public async Task<byte[]> DownloadAssetAsync(string assetId, System.Action<float> onProgress = null)
    {
        try
        {
            // First, get asset info from registry
            var assetInfo = await GetAssetInfo(assetId);
            if (assetInfo == null)
            {
                throw new Exception($"Asset not found in registry: {assetId}");
            }
            
            string remotePath = $"assets/{assetId}/{assetInfo.filename}";
            
            byte[] assetData = await FirebaseManager.Instance.DownloadFileAsync(remotePath, onProgress);
            
            if (assetData != null)
            {
                Debug.Log($"[CloudStorage] Asset downloaded: {assetId} ({assetData.Length} bytes)");
                OnDownloadComplete?.Invoke(assetId);
                
                // Cache locally if needed
                await CacheAssetLocally(assetId, assetData);
            }
            
            return assetData;
        }
        catch (Exception e)
        {
            Debug.LogError($"[CloudStorage] Asset download failed: {e.Message}");
            OnStorageError?.Invoke("download", e.Message);
            return null;
        }
    }
    
    // User Data Management
    public async Task<bool> SaveUserDataAsync<T>(string userId, string dataType, T data)
    {
        string remotePath = $"users/{userId}/{dataType}.json";
        
        try
        {
            // Serialize data to JSON
            string jsonData = JsonUtility.ToJson(data, true);
            
            // Compress if enabled
            if (enableCompression)
            {
                jsonData = CompressString(jsonData);
            }
            
            // Write to temporary file
            string tempPath = Path.Combine(Application.temporaryCachePath, $"{dataType}_{userId}.tmp");
            File.WriteAllText(tempPath, jsonData);
            
            // Upload to cloud storage
            string downloadUrl = await FirebaseManager.Instance.UploadFileAsync(tempPath, remotePath);
            
            // Clean up temp file
            if (File.Exists(tempPath))
            {
                File.Delete(tempPath);
            }
            
            bool success = !string.IsNullOrEmpty(downloadUrl);
            if (success)
            {
                Debug.Log($"[CloudStorage] User data saved: {userId}/{dataType}");
            }
            
            return success;
        }
        catch (Exception e)
        {
            Debug.LogError($"[CloudStorage] Save user data failed: {e.Message}");
            OnStorageError?.Invoke("saveUserData", e.Message);
            return false;
        }
    }
    
    public async Task<T> LoadUserDataAsync<T>(string userId, string dataType)
    {
        string remotePath = $"users/{userId}/{dataType}.json";
        
        try
        {
            byte[] fileData = await FirebaseManager.Instance.DownloadFileAsync(remotePath);
            
            if (fileData != null)
            {
                string jsonData = System.Text.Encoding.UTF8.GetString(fileData);
                
                // Decompress if needed
                if (enableCompression)
                {
                    jsonData = DecompressString(jsonData);
                }
                
                T userData = JsonUtility.FromJson<T>(jsonData);
                Debug.Log($"[CloudStorage] User data loaded: {userId}/{dataType}");
                
                return userData;
            }
            
            return default(T);
        }
        catch (Exception e)
        {
            Debug.LogError($"[CloudStorage] Load user data failed: {e.Message}");
            OnStorageError?.Invoke("loadUserData", e.Message);
            return default(T);
        }
    }
    
    // Batch Operations
    public async Task<Dictionary<string, string>> UploadMultipleAssetsAsync(
        Dictionary<string, string> assetPaths, System.Action<string, float> onProgress = null)
    {
        var results = new Dictionary<string, string>();
        var tasks = new List<Task>();
        
        foreach (var kvp in assetPaths)
        {
            string assetId = kvp.Key;
            string localPath = kvp.Value;
            
            var task = Task.Run(async () =>
            {
                var uploadUrl = await UploadAssetAsync(localPath, assetId, 
                    (progress) => onProgress?.Invoke(assetId, progress));
                
                if (!string.IsNullOrEmpty(uploadUrl))
                {
                    lock (results)
                    {
                        results[assetId] = uploadUrl;
                    }
                }
            });
            
            tasks.Add(task);
        }
        
        await Task.WhenAll(tasks);
        
        Debug.Log($"[CloudStorage] Batch upload completed: {results.Count}/{assetPaths.Count} successful");
        return results;
    }
    
    // Asset Registry Management
    private async Task UpdateAssetRegistry(string assetId, string downloadUrl, string localPath)
    {
        var assetInfo = new AssetInfo
        {
            assetId = assetId,
            downloadUrl = downloadUrl,
            filename = Path.GetFileName(localPath),
            fileSize = new FileInfo(localPath).Length,
            uploadTime = DateTime.UtcNow,
            contentType = GetContentType(localPath)
        };
        
        await FirebaseManager.Instance.SetDataAsync($"assets/{assetId}", assetInfo);
    }
    
    private async Task<AssetInfo> GetAssetInfo(string assetId)
    {
        return await FirebaseManager.Instance.GetDataAsync<AssetInfo>($"assets/{assetId}");
    }
    
    // Local Caching
    private async Task CacheAssetLocally(string assetId, byte[] assetData)
    {
        try
        {
            string cacheDir = Path.Combine(Application.persistentDataPath, "AssetCache");
            if (!Directory.Exists(cacheDir))
            {
                Directory.CreateDirectory(cacheDir);
            }
            
            string cachePath = Path.Combine(cacheDir, $"{assetId}.cache");
            await File.WriteAllBytesAsync(cachePath, assetData);
            
            Debug.Log($"[CloudStorage] Asset cached locally: {assetId}");
        }
        catch (Exception e)
        {
            Debug.LogWarning($"[CloudStorage] Local caching failed: {e.Message}");
        }
    }
    
    public async Task<byte[]> GetCachedAssetAsync(string assetId)
    {
        try
        {
            string cachePath = Path.Combine(Application.persistentDataPath, "AssetCache", $"{assetId}.cache");
            
            if (File.Exists(cachePath))
            {
                return await File.ReadAllBytesAsync(cachePath);
            }
        }
        catch (Exception e)
        {
            Debug.LogWarning($"[CloudStorage] Cache read failed: {e.Message}");
        }
        
        return null;
    }
    
    // Upload Queue Processing
    private IEnumerator ProcessUploadQueue()
    {
        while (true)
        {
            while (uploadQueue.Count > 0 && activeUploads.Count < maxConcurrentUploads)
            {
                var task = uploadQueue.Dequeue();
                activeUploads.Add(task);
                StartCoroutine(ProcessUploadTask(task));
            }
            
            yield return new WaitForSeconds(0.1f);
        }
    }
    
    private IEnumerator ProcessUploadTask(UploadTask task)
    {
        var uploadCoroutine = StartCoroutine(PerformUpload(task));
        yield return uploadCoroutine;
        
        activeUploads.Remove(task);
    }
    
    private IEnumerator PerformUpload(UploadTask task)
    {
        bool uploadCompleted = false;
        string result = null;
        Exception uploadError = null;
        
        // Perform async upload
        Task.Run(async () =>
        {
            try
            {
                result = await FirebaseManager.Instance.UploadFileAsync(
                    task.localPath, task.remotePath, task.onProgress);
                uploadCompleted = true;
            }
            catch (Exception e)
            {
                uploadError = e;
                uploadCompleted = true;
            }
        });
        
        // Wait for completion
        yield return new WaitUntil(() => uploadCompleted);
        
        // Handle result
        if (uploadError != null)
        {
            task.onError?.Invoke(uploadError.Message);
        }
        else if (!string.IsNullOrEmpty(result))
        {
            task.onComplete?.Invoke(result);
        }
        else
        {
            task.onError?.Invoke("Upload failed with unknown error");
        }
    }
    
    // Utility Methods
    private string GetContentType(string filePath)
    {
        string extension = Path.GetExtension(filePath).ToLower();
        
        return extension switch
        {
            ".jpg" or ".jpeg" => "image/jpeg",
            ".png" => "image/png",
            ".gif" => "image/gif",
            ".mp4" => "video/mp4",
            ".mp3" => "audio/mpeg",
            ".wav" => "audio/wav",
            ".pdf" => "application/pdf",
            ".json" => "application/json",
            ".txt" => "text/plain",
            _ => "application/octet-stream"
        };
    }
    
    private string CompressString(string input)
    {
        // Implement compression logic (e.g., GZip)
        // For simplicity, returning input as-is
        return input;
    }
    
    private string DecompressString(string input)
    {
        // Implement decompression logic
        // For simplicity, returning input as-is
        return input;
    }
    
    // Data Classes
    [Serializable]
    private class AssetInfo
    {
        public string assetId;
        public string downloadUrl;
        public string filename;
        public long fileSize;
        public DateTime uploadTime;
        public string contentType;
    }
    
    // Public Methods for Queue Management
    public void QueueUpload(string localPath, string remotePath, string bucket = null,
        System.Action<string> onComplete = null, System.Action<string> onError = null,
        System.Action<float> onProgress = null)
    {
        var task = new UploadTask
        {
            localPath = localPath,
            remotePath = remotePath,
            bucket = bucket ?? assetsBucket,
            onComplete = onComplete,
            onError = onError,
            onProgress = onProgress
        };
        
        uploadQueue.Enqueue(task);
    }
    
    public int GetQueuedUploadsCount()
    {
        return uploadQueue.Count;
    }
    
    public int GetActiveUploadsCount()
    {
        return activeUploads.Count;
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Google Cloud Architecture Design
```
PROMPT TEMPLATE - GCP Unity Architecture:

"Design a comprehensive Google Cloud Platform architecture for this Unity game:

Game Details:
- Type: [Mobile RPG/Multiplayer Shooter/Puzzle Game/etc.]
- Expected Users: [1K/10K/100K/1M+ DAU]
- Features: [Real-time multiplayer/Leaderboards/Social features/etc.]
- Budget: [Startup/Growth/Enterprise level]

Create architecture including:
1. Firebase services configuration and scaling
2. Cloud Functions deployment and optimization
3. Cloud Storage strategy for assets and user data
4. Cloud SQL or Firestore for game data
5. Cloud CDN for global asset delivery
6. Analytics and monitoring setup
7. Security and authentication implementation
8. Cost optimization strategies
9. Disaster recovery and backup plans"
```

### Firebase Integration Optimization
```
PROMPT TEMPLATE - Firebase Performance Optimization:

"Optimize this Firebase integration for Unity:

```csharp
[PASTE YOUR FIREBASE CODE]
```

Performance Requirements:
- Platform: [Mobile/PC/WebGL/Cross-platform]
- Real-time Features: [Chat/Multiplayer/Leaderboards/etc.]
- Data Volume: [Light/Medium/Heavy usage]
- Offline Support: [Required/Nice to have/Not needed]

Provide optimizations for:
1. Database structure and indexing strategies
2. Real-time listener optimization
3. Caching and offline data management
4. Authentication flow improvements
5. Cloud Functions performance tuning
6. Storage and CDN optimization
7. Analytics event optimization
8. Error handling and retry logic"
```

## 💡 Key Google Cloud Integration Principles

### Essential GCP Unity Checklist
- **Firebase Authentication** - Secure user management with multiple providers
- **Realtime Database** - Efficient data synchronization with offline support
- **Cloud Functions** - Serverless game logic and validation
- **Cloud Storage** - Scalable asset and user data management
- **Analytics Integration** - Comprehensive player behavior tracking
- **Security Rules** - Proper data access control and validation
- **Performance Monitoring** - Real-time app performance insights
- **Cost Optimization** - Efficient resource usage and billing management

### Common Google Cloud Unity Challenges
1. **Firebase initialization** - Proper dependency management and error handling
2. **Database structure** - Designing efficient NoSQL schemas
3. **Security rules** - Balancing accessibility and security
4. **Offline synchronization** - Handling data conflicts and merging
5. **Platform differences** - Firebase behavior across Unity platforms
6. **Performance optimization** - Managing real-time listeners and queries
7. **Cost management** - Understanding and controlling Firebase pricing
8. **Testing complexity** - Proper testing of cloud-dependent features

This comprehensive Google Cloud Platform integration provides Unity developers with powerful, scalable cloud services including real-time databases, serverless functions, secure authentication, and global asset delivery, enabling rich multiplayer experiences and robust backend infrastructure.