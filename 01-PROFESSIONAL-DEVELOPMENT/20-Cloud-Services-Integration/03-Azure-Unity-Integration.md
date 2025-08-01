# 03-Azure-Unity-Integration.md

## 🎯 Learning Objectives
- Master Microsoft Azure cloud services integration for Unity applications
- Implement Azure PlayFab for comprehensive game backend services
- Design scalable Azure Functions for serverless game logic
- Develop efficient Azure Storage and CDN solutions for Unity games

## 🔧 Azure PlayFab Unity Integration

### PlayFab Unity SDK Implementation
```csharp
// Scripts/Cloud/PlayFabManager.cs
using System;
using System.Collections.Generic;
using UnityEngine;
using PlayFab;
using PlayFab.ClientModels;
using PlayFab.ServerModels;
using PlayFab.CloudScriptModels;

public class PlayFabManager : MonoBehaviour
{
    [Header("PlayFab Configuration")]
    [SerializeField] private string titleId = "YOUR_TITLE_ID";
    [SerializeField] private bool enableAutoLogin = true;
    [SerializeField] private bool enableAnalytics = true;
    [SerializeField] private string catalogVersion = "main";
    
    public static PlayFabManager Instance { get; private set; }
    
    // Properties
    public bool IsLoggedIn { get; private set; }
    public string PlayFabId { get; private set; }
    public string SessionTicket { get; private set; }
    public GetPlayerCombinedInfoResultPayload PlayerInfo { get; private set; }
    
    // Events
    public System.Action<LoginResult> OnLoginSuccess;
    public System.Action<PlayFabError> OnLoginFailure;
    public System.Action OnLogout;
    public System.Action<GetPlayerCombinedInfoResultPayload> OnPlayerDataUpdated;
    public System.Action<PlayFabError> OnPlayFabError;
    
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
        // Set PlayFab title ID
        if (!string.IsNullOrEmpty(titleId))
        {
            PlayFabSettings.staticSettings.TitleId = titleId;
        }
        
        // Configure PlayFab settings
        PlayFabSettings.staticSettings.RequestType = WebRequestType.UnityWww;
        PlayFabSettings.staticSettings.CompressApiData = true;
        
        Debug.Log("[PlayFab] PlayFab Manager initialized");
        
        // Auto-login if enabled
        if (enableAutoLogin)
        {
            AttemptAutoLogin();
        }
    }
    
    // Authentication Methods
    public void LoginWithCustomID(string customId, bool createAccount = true)
    {
        var request = new LoginWithCustomIDRequest
        {
            CustomId = customId,
            CreateAccount = createAccount,
            InfoRequestParameters = GetDefaultInfoRequestParameters()
        };
        
        PlayFabClientAPI.LoginWithCustomID(request, OnLoginSuccessCallback, OnLoginFailureCallback);
        Debug.Log($"[PlayFab] Attempting login with Custom ID: {customId}");
    }
    
    public void LoginWithEmailAddress(string email, string password)
    {
        var request = new LoginWithEmailAddressRequest
        {
            Email = email,
            Password = password,
            InfoRequestParameters = GetDefaultInfoRequestParameters()
        };
        
        PlayFabClientAPI.LoginWithEmailAddress(request, OnLoginSuccessCallback, OnLoginFailureCallback);
        Debug.Log($"[PlayFab] Attempting login with email: {email}");
    }
    
    public void RegisterWithEmail(string email, string password, string username)
    {
        var request = new RegisterPlayFabUserRequest
        {
            Email = email,
            Password = password,
            Username = username,
            RequireBothUsernameAndEmail = false,
            InfoRequestParameters = GetDefaultInfoRequestParameters()
        };
        
        PlayFabClientAPI.RegisterPlayFabUser(request, OnRegisterSuccessCallback, OnLoginFailureCallback);
        Debug.Log($"[PlayFab] Attempting registration with email: {email}");
    }
    
    public void LoginWithDeviceID()
    {
        string deviceId = SystemInfo.deviceUniqueIdentifier;
        
        var request = new LoginWithCustomIDRequest
        {
            CustomId = deviceId,
            CreateAccount = true,
            InfoRequestParameters = GetDefaultInfoRequestParameters()
        };
        
        PlayFabClientAPI.LoginWithCustomID(request, OnLoginSuccessCallback, OnLoginFailureCallback);
        Debug.Log($"[PlayFab] Attempting device ID login: {deviceId}");
    }
    
    private void AttemptAutoLogin()
    {
        // Try to login with saved device ID
        if (PlayerPrefs.HasKey("PlayFab_DeviceId"))
        {
            string savedDeviceId = PlayerPrefs.GetString("PlayFab_DeviceId");
            LoginWithCustomID(savedDeviceId);
        }
        else
        {
            // First time - use device ID
            LoginWithDeviceID();
        }
    }
    
    // Callback Handlers
    private void OnLoginSuccessCallback(LoginResult result)
    {
        IsLoggedIn = true;
        PlayFabId = result.PlayFabId;
        SessionTicket = result.SessionTicket;
        PlayerInfo = result.InfoResultPayload;
        
        // Save device ID for auto-login
        if (!string.IsNullOrEmpty(result.NewlyCreated) && result.NewlyCreated == "true")
        {
            PlayerPrefs.SetString("PlayFab_DeviceId", SystemInfo.deviceUniqueIdentifier);
            PlayerPrefs.Save();
        }
        
        Debug.Log($"[PlayFab] Login successful! PlayFab ID: {PlayFabId}");
        OnLoginSuccess?.Invoke(result);
        OnPlayerDataUpdated?.Invoke(PlayerInfo);
        
        // Send login analytics event
        if (enableAnalytics)
        {
            LogCustomEvent("player_login", new Dictionary<string, object>
            {
                {"platform", Application.platform.ToString()},
                {"version", Application.version}
            });
        }
    }
    
    private void OnRegisterSuccessCallback(RegisterPlayFabUserResult result)
    {
        Debug.Log($"[PlayFab] Registration successful! PlayFab ID: {result.PlayFabId}");
        
        // Treat registration success as login success
        var loginResult = new LoginResult
        {
            PlayFabId = result.PlayFabId,
            SessionTicket = result.SessionTicket,
            NewlyCreated = "true"
        };
        
        OnLoginSuccessCallback(loginResult);
    }
    
    private void OnLoginFailureCallback(PlayFabError error)
    {
        IsLoggedIn = false;
        Debug.LogError($"[PlayFab] Login failed: {error.GenerateErrorReport()}");
        OnLoginFailure?.Invoke(error);
        OnPlayFabError?.Invoke(error);
    }
    
    // Player Data Management
    public void GetPlayerData(List<string> keys = null, System.Action<GetUserDataResult> onSuccess = null)
    {
        var request = new GetUserDataRequest
        {
            Keys = keys
        };
        
        PlayFabClientAPI.GetUserData(request, 
            (result) =>
            {
                Debug.Log($"[PlayFab] Player data retrieved: {result.Data.Count} entries");
                onSuccess?.Invoke(result);
            },
            (error) =>
            {
                Debug.LogError($"[PlayFab] Get player data failed: {error.GenerateErrorReport()}");
                OnPlayFabError?.Invoke(error);
            });
    }
    
    public void UpdatePlayerData(Dictionary<string, string> data, 
        System.Action<UpdateUserDataResult> onSuccess = null)
    {
        var request = new UpdateUserDataRequest
        {
            Data = data,
            Permission = UserDataPermission.Public
        };
        
        PlayFabClientAPI.UpdateUserData(request,
            (result) =>
            {
                Debug.Log($"[PlayFab] Player data updated successfully");
                onSuccess?.Invoke(result);
            },
            (error) =>
            {
                Debug.LogError($"[PlayFab] Update player data failed: {error.GenerateErrorReport()}");
                OnPlayFabError?.Invoke(error);
            });
    }
    
    // Virtual Currency Management
    public void GetVirtualCurrencies(System.Action<GetUserInventoryResult> onSuccess = null)
    {
        PlayFabClientAPI.GetUserInventory(new GetUserInventoryRequest(),
            (result) =>
            {
                Debug.Log($"[PlayFab] Virtual currencies retrieved");
                onSuccess?.Invoke(result);
            },
            (error) =>
            {
                Debug.LogError($"[PlayFab] Get virtual currencies failed: {error.GenerateErrorReport()}");
                OnPlayFabError?.Invoke(error);
            });
    }
    
    public void AddVirtualCurrency(string currencyCode, int amount, 
        System.Action<ModifyUserVirtualCurrencyResult> onSuccess = null)
    {
        var request = new AddUserVirtualCurrencyRequest
        {
            VirtualCurrency = currencyCode,
            Amount = amount
        };
        
        PlayFabClientAPI.AddUserVirtualCurrency(request,
            (result) =>
            {
                Debug.Log($"[PlayFab] Added {amount} {currencyCode}. New balance: {result.Balance}");
                onSuccess?.Invoke(result);
            },
            (error) =>
            {
                Debug.LogError($"[PlayFab] Add virtual currency failed: {error.GenerateErrorReport()}");
                OnPlayFabError?.Invoke(error);
            });
    }
    
    // Leaderboards
    public void GetLeaderboard(string statisticName, int maxResults = 100, 
        System.Action<GetLeaderboardResult> onSuccess = null)
    {
        var request = new GetLeaderboardRequest
        {
            StatisticName = statisticName,
            StartPosition = 0,
            MaxResultsCount = maxResults
        };
        
        PlayFabClientAPI.GetLeaderboard(request,
            (result) =>
            {
                Debug.Log($"[PlayFab] Leaderboard retrieved: {result.Leaderboard.Count} entries");
                onSuccess?.Invoke(result);
            },
            (error) =>
            {
                Debug.LogError($"[PlayFab] Get leaderboard failed: {error.GenerateErrorReport()}");
                OnPlayFabError?.Invoke(error);
            });
    }
    
    public void UpdatePlayerStatistics(Dictionary<string, int> statistics, 
        System.Action<UpdatePlayerStatisticsResult> onSuccess = null)
    {
        var statisticUpdates = new List<StatisticUpdate>();
        
        foreach (var stat in statistics)
        {
            statisticUpdates.Add(new StatisticUpdate
            {
                StatisticName = stat.Key,
                Value = stat.Value
            });
        }
        
        var request = new UpdatePlayerStatisticsRequest
        {
            Statistics = statisticUpdates
        };
        
        PlayFabClientAPI.UpdatePlayerStatistics(request,
            (result) =>
            {
                Debug.Log($"[PlayFab] Player statistics updated: {statistics.Count} stats");
                onSuccess?.Invoke(result);
            },
            (error) =>
            {
                Debug.LogError($"[PlayFab] Update statistics failed: {error.GenerateErrorReport()}");
                OnPlayFabError?.Invoke(error);
            });
    }
    
    // Cloud Script Execution
    public void ExecuteCloudScript(string functionName, object functionParameter = null,
        System.Action<ExecuteCloudScriptResult> onSuccess = null)
    {
        var request = new ExecuteCloudScriptRequest
        {
            FunctionName = functionName,
            FunctionParameter = functionParameter,
            GeneratePlayStreamEvent = true
        };
        
        PlayFabClientAPI.ExecuteCloudScript(request,
            (result) =>
            {
                if (result.Error != null)
                {
                    Debug.LogError($"[PlayFab] Cloud script error: {result.Error.Error}");
                }
                else
                {
                    Debug.Log($"[PlayFab] Cloud script executed: {functionName}");
                    onSuccess?.Invoke(result);
                }
            },
            (error) =>
            {
                Debug.LogError($"[PlayFab] Execute cloud script failed: {error.GenerateErrorReport()}");
                OnPlayFabError?.Invoke(error);
            });
    }
    
    // Store and Purchases
    public void GetCatalogItems(System.Action<GetCatalogItemsResult> onSuccess = null)
    {
        var request = new GetCatalogItemsRequest
        {
            CatalogVersion = catalogVersion
        };
        
        PlayFabClientAPI.GetCatalogItems(request,
            (result) =>
            {
                Debug.Log($"[PlayFab] Catalog items retrieved: {result.Catalog.Count} items");
                onSuccess?.Invoke(result);
            },
            (error) =>
            {
                Debug.LogError($"[PlayFab] Get catalog failed: {error.GenerateErrorReport()}");
                OnPlayFabError?.Invoke(error);
            });
    }
    
    public void PurchaseItem(string itemId, string currencyCode, int price,
        System.Action<PurchaseItemResult> onSuccess = null)
    {
        var request = new PurchaseItemRequest
        {
            ItemId = itemId,
            VirtualCurrency = currencyCode,
            Price = price,
            CatalogVersion = catalogVersion
        };
        
        PlayFabClientAPI.PurchaseItem(request,
            (result) =>
            {
                Debug.Log($"[PlayFab] Item purchased: {itemId}");
                onSuccess?.Invoke(result);
            },
            (error) =>
            {
                Debug.LogError($"[PlayFab] Purchase failed: {error.GenerateErrorReport()}");
                OnPlayFabError?.Invoke(error);
            });
    }
    
    // Multiplayer and Matchmaking
    public void CreateMultiplayerRoom(string gameMode, int maxPlayers,
        System.Action<string> onSuccess = null)
    {
        var roomData = new Dictionary<string, object>
        {
            {"gameMode", gameMode},
            {"maxPlayers", maxPlayers},
            {"hostId", PlayFabId},
            {"created", DateTime.UtcNow.ToString()}
        };
        
        ExecuteCloudScript("createRoom", roomData,
            (result) =>
            {
                if (result.FunctionResult != null)
                {
                    string roomId = result.FunctionResult.ToString();
                    Debug.Log($"[PlayFab] Room created: {roomId}");
                    onSuccess?.Invoke(roomId);
                }
            });
    }
    
    public void JoinMultiplayerRoom(string roomId, System.Action<bool> onSuccess = null)
    {
        var joinData = new Dictionary<string, object>
        {
            {"roomId", roomId},
            {"playerId", PlayFabId}
        };
        
        ExecuteCloudScript("joinRoom", joinData,
            (result) =>
            {
                if (result.FunctionResult != null)
                {
                    bool success = Convert.ToBoolean(result.FunctionResult);
                    Debug.Log($"[PlayFab] Join room result: {success}");
                    onSuccess?.Invoke(success);
                }
            });
    }
    
    // Analytics and Events
    public void LogCustomEvent(string eventName, Dictionary<string, object> parameters = null)
    {
        if (!enableAnalytics) return;
        
        var request = new WriteClientPlayerEventRequest
        {
            EventName = eventName,
            Body = parameters ?? new Dictionary<string, object>()
        };
        
        PlayFabClientAPI.WritePlayerEvent(request,
            (result) =>
            {
                Debug.Log($"[PlayFab] Custom event logged: {eventName}");
            },
            (error) =>
            {
                Debug.LogWarning($"[PlayFab] Log event failed: {error.GenerateErrorReport()}");
            });
    }
    
    // Friends and Social
    public void GetFriendsList(System.Action<GetFriendsListResult> onSuccess = null)
    {
        var request = new GetFriendsListRequest
        {
            IncludeSteamFriends = false,
            IncludeFacebookFriends = false
        };
        
        PlayFabClientAPI.GetFriendsList(request,
            (result) =>
            {
                Debug.Log($"[PlayFab] Friends list retrieved: {result.Friends.Count} friends");
                onSuccess?.Invoke(result);
            },
            (error) =>
            {
                Debug.LogError($"[PlayFab] Get friends failed: {error.GenerateErrorReport()}");
                OnPlayFabError?.Invoke(error);
            });
    }
    
    public void AddFriend(string friendPlayFabId, System.Action<AddFriendResult> onSuccess = null)
    {
        var request = new AddFriendRequest
        {
            FriendPlayFabId = friendPlayFabId
        };
        
        PlayFabClientAPI.AddFriend(request,
            (result) =>
            {
                Debug.Log($"[PlayFab] Friend added: {friendPlayFabId}");
                onSuccess?.Invoke(result);
            },
            (error) =>
            {
                Debug.LogError($"[PlayFab] Add friend failed: {error.GenerateErrorReport()}");
                OnPlayFabError?.Invoke(error);
            });
    }
    
    // Utility Methods
    private GetPlayerCombinedInfoRequestParams GetDefaultInfoRequestParameters()
    {
        return new GetPlayerCombinedInfoRequestParams
        {
            GetUserAccountInfo = true,
            GetUserInventory = true,
            GetUserVirtualCurrency = true,
            GetUserData = true,
            GetUserReadOnlyData = true,
            GetCharacterInventories = false,
            GetCharacterList = false,
            GetPlayerProfile = true,
            GetPlayerStatistics = true,
            GetTitleData = true
        };
    }
    
    public void Logout()
    {
        if (IsLoggedIn)
        {
            IsLoggedIn = false;
            PlayFabId = null;
            SessionTicket = null;
            PlayerInfo = null;
            
            Debug.Log("[PlayFab] User logged out");
            OnLogout?.Invoke();
        }
    }
    
    // Error Handling
    public string GetErrorMessage(PlayFabError error)
    {
        if (error.Error == PlayFabErrorCode.InvalidParams && 
            error.ErrorDetails != null && error.ErrorDetails.Count > 0)
        {
            return string.Join(", ", error.ErrorDetails.Values);
        }
        
        return error.ErrorMessage ?? error.Error.ToString();
    }
}
```

### Azure Functions Integration
```csharp
// Scripts/Cloud/AzureFunctionsService.cs
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;

public class AzureFunctionsService : MonoBehaviour
{
    [Header("Azure Functions Configuration")]
    [SerializeField] private string functionAppUrl = "https://your-app.azurewebsites.net";
    [SerializeField] private string functionKey = "your-function-key";
    [SerializeField] private float defaultTimeout = 30f;
    [SerializeField] private int maxRetryAttempts = 3;
    
    public static AzureFunctionsService Instance { get; private set; }
    
    // Events
    public System.Action<string, object> OnFunctionResult;
    public System.Action<string, string> OnFunctionError;
    
    private Dictionary<string, string> defaultHeaders;
    
    [Serializable]
    public class FunctionRequest
    {
        public string functionName;
        public object parameters;
        public Dictionary<string, string> headers;
        public float timeout;
        public int retryAttempts;
    }
    
    [Serializable]
    public class FunctionResponse<T>
    {
        public bool success;
        public T data;
        public string error;
        public int statusCode;
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
        defaultHeaders = new Dictionary<string, string>
        {
            {"Content-Type", "application/json"},
            {"x-functions-key", functionKey}
        };
        
        Debug.Log("[AzureFunctions] Service initialized");
    }
    
    // Core Function Execution
    public async Task<T> CallFunctionAsync<T>(string functionName, object parameters = null)
    {
        var request = new FunctionRequest
        {
            functionName = functionName,
            parameters = parameters,
            headers = new Dictionary<string, string>(defaultHeaders),
            timeout = defaultTimeout,
            retryAttempts = 0
        };
        
        return await ExecuteFunctionAsync<T>(request);
    }
    
    private async Task<T> ExecuteFunctionAsync<T>(FunctionRequest request)
    {
        string url = $"{functionAppUrl}/api/{request.functionName}";
        
        for (int attempt = 0; attempt <= maxRetryAttempts; attempt++)
        {
            try
            {
                using (UnityWebRequest webRequest = new UnityWebRequest(url, "POST"))
                {
                    // Set request body
                    if (request.parameters != null)
                    {
                        string jsonData = JsonConvert.SerializeObject(request.parameters);
                        byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
                        webRequest.uploadHandler = new UploadHandlerRaw(bodyRaw);
                    }
                    
                    webRequest.downloadHandler = new DownloadHandlerBuffer();
                    webRequest.timeout = (int)request.timeout;
                    
                    // Set headers
                    foreach (var header in request.headers)
                    {
                        webRequest.SetRequestHeader(header.Key, header.Value);
                    }
                    
                    Debug.Log($"[AzureFunctions] Calling function: {request.functionName} (attempt {attempt + 1})");
                    
                    var operation = webRequest.SendWebRequest();
                    
                    // Wait for completion
                    while (!operation.isDone)
                    {
                        await Task.Yield();
                    }
                    
                    if (webRequest.result == UnityWebRequest.Result.Success)
                    {
                        var response = JsonConvert.DeserializeObject<FunctionResponse<T>>(
                            webRequest.downloadHandler.text);
                        
                        if (response.success)
                        {
                            Debug.Log($"[AzureFunctions] Function succeeded: {request.functionName}");
                            OnFunctionResult?.Invoke(request.functionName, response.data);
                            return response.data;
                        }
                        else
                        {
                            throw new Exception(response.error ?? "Function returned failure");
                        }
                    }
                    else
                    {
                        throw new Exception($"HTTP Error: {webRequest.error}");
                    }
                }
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[AzureFunctions] Attempt {attempt + 1} failed: {e.Message}");
                
                if (attempt == maxRetryAttempts)
                {
                    Debug.LogError($"[AzureFunctions] Function failed after {maxRetryAttempts + 1} attempts: {request.functionName}");
                    OnFunctionError?.Invoke(request.functionName, e.Message);
                    throw;
                }
                
                // Exponential backoff
                await Task.Delay((int)(Math.Pow(2, attempt) * 1000));
            }
        }
        
        return default(T);
    }
    
    // Game-Specific Functions
    public async Task<PlayerValidationResult> ValidatePlayerAsync(string playerId, string sessionToken)
    {
        var parameters = new
        {
            playerId = playerId,
            sessionToken = sessionToken,
            timestamp = DateTime.UtcNow
        };
        
        return await CallFunctionAsync<PlayerValidationResult>("validatePlayer", parameters);
    }
    
    public async Task<LeaderboardResult> UpdateLeaderboardAsync(string playerId, string leaderboardId, int score)
    {
        var parameters = new
        {
            playerId = playerId,
            leaderboardId = leaderboardId,
            score = score,
            timestamp = DateTime.UtcNow
        };
        
        return await CallFunctionAsync<LeaderboardResult>("updateLeaderboard", parameters);
    }
    
    public async Task<MatchmakingResult> RequestMatchmakingAsync(string playerId, string gameMode, int skillRating)
    {
        var parameters = new
        {
            playerId = playerId,
            gameMode = gameMode,
            skillRating = skillRating,
            region = GetPlayerRegion(),
            timestamp = DateTime.UtcNow
        };
        
        return await CallFunctionAsync<MatchmakingResult>("requestMatchmaking", parameters);
    }
    
    public async Task<TournamentResult> JoinTournamentAsync(string playerId, string tournamentId)
    {
        var parameters = new
        {
            playerId = playerId,
            tournamentId = tournamentId,
            timestamp = DateTime.UtcNow
        };
        
        return await CallFunctionAsync<TournamentResult>("joinTournament", parameters);
    }
    
    public async Task<RewardResult> ClaimDailyRewardAsync(string playerId)
    {
        var parameters = new
        {
            playerId = playerId,
            timestamp = DateTime.UtcNow
        };
        
        return await CallFunctionAsync<RewardResult>("claimDailyReward", parameters);
    }
    
    public async Task<AntiCheatResult> ValidateGameActionAsync(string playerId, string actionType, 
        Dictionary<string, object> actionData)
    {
        var parameters = new
        {
            playerId = playerId,
            actionType = actionType,
            actionData = actionData,
            timestamp = DateTime.UtcNow,
            clientVersion = Application.version
        };
        
        return await CallFunctionAsync<AntiCheatResult>("validateGameAction", parameters);
    }
    
    // Utility Methods
    private string GetPlayerRegion()
    {
        // Implement region detection logic
        return "us-east-1"; // Default region
    }
    
    public void SetFunctionKey(string newKey)
    {
        functionKey = newKey;
        defaultHeaders["x-functions-key"] = newKey;
    }
    
    public void SetFunctionAppUrl(string newUrl)
    {
        functionAppUrl = newUrl.TrimEnd('/');
    }
    
    // Response Data Classes
    [Serializable]
    public class PlayerValidationResult
    {
        public bool isValid;
        public string playerId;
        public Dictionary<string, object> playerData;
        public DateTime validUntil;
    }
    
    [Serializable]
    public class LeaderboardResult
    {
        public string leaderboardId;
        public int newRank;
        public int previousRank;
        public long newScore;
        public bool isNewBest;
    }
    
    [Serializable]
    public class MatchmakingResult
    {
        public string matchId;
        public List<string> playerIds;
        public string serverEndpoint;
        public int estimatedWaitTime;
        public Dictionary<string, object> matchSettings;
    }
    
    [Serializable]
    public class TournamentResult
    {
        public string tournamentId;
        public bool joinedSuccessfully;
        public int currentParticipants;
        public int maxParticipants;
        public DateTime startTime;
        public Dictionary<string, object> tournamentInfo;
    }
    
    [Serializable]
    public class RewardResult
    {
        public bool rewardClaimed;
        public List<RewardItem> rewards;
        public DateTime nextClaimTime;
        public int streakCount;
    }
    
    [Serializable]
    public class RewardItem
    {
        public string itemType;
        public string itemId;
        public int quantity;
        public Dictionary<string, object> metadata;
    }
    
    [Serializable]
    public class AntiCheatResult
    {
        public bool actionValid;
        public float confidenceScore;
        public string reason;
        public Dictionary<string, object> additionalData;
    }
}
```

### Azure Storage Integration
```csharp
// Scripts/Cloud/AzureStorageService.cs
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;

public class AzureStorageService : MonoBehaviour
{
    [Header("Azure Storage Configuration")]
    [SerializeField] private string storageAccountName = "yourstorageaccount";
    [SerializeField] private string containerName = "game-assets";
    [SerializeField] private string sasToken = "your-sas-token";
    [SerializeField] private string cdnEndpoint = "https://yourcdn.azureedge.net";
    
    public static AzureStorageService Instance { get; private set; }
    
    // Events
    public System.Action<string, float> OnUploadProgress;
    public System.Action<string, float> OnDownloadProgress;
    public System.Action<string> OnUploadComplete;
    public System.Action<string> OnDownloadComplete;
    public System.Action<string, string> OnStorageError;
    
    private string baseStorageUrl;
    private Dictionary<string, string> uploadHeaders;
    
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
        baseStorageUrl = $"https://{storageAccountName}.blob.core.windows.net/{containerName}";
        
        uploadHeaders = new Dictionary<string, string>
        {
            {"x-ms-blob-type", "BlockBlob"},
            {"Content-Type", "application/octet-stream"}
        };
        
        Debug.Log("[AzureStorage] Service initialized");
    }
    
    // Blob Storage Operations
    public async Task<string> UploadBlobAsync(string blobName, byte[] data, string contentType = null)
    {
        string url = $"{baseStorageUrl}/{blobName}?{sasToken}";
        
        try
        {
            using (UnityWebRequest request = UnityWebRequest.Put(url, data))
            {
                // Set headers
                request.SetRequestHeader("x-ms-blob-type", "BlockBlob");
                request.SetRequestHeader("Content-Type", contentType ?? "application/octet-stream");
                
                Debug.Log($"[AzureStorage] Uploading blob: {blobName}");
                
                var operation = request.SendWebRequest();
                
                // Track progress
                while (!operation.isDone)
                {
                    OnUploadProgress?.Invoke(blobName, request.uploadProgress);
                    await Task.Yield();
                }
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    string downloadUrl = GetDownloadUrl(blobName);
                    Debug.Log($"[AzureStorage] Blob uploaded successfully: {blobName}");
                    OnUploadComplete?.Invoke(blobName);
                    return downloadUrl;
                }
                else
                {
                    throw new Exception($"Upload failed: {request.error}");
                }
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"[AzureStorage] Upload failed for {blobName}: {e.Message}");
            OnStorageError?.Invoke("upload", e.Message);
            return null;
        }
    }
    
    public async Task<byte[]> DownloadBlobAsync(string blobName)
    {
        string url = GetDownloadUrl(blobName);
        
        try
        {
            using (UnityWebRequest request = UnityWebRequest.Get(url))
            {
                Debug.Log($"[AzureStorage] Downloading blob: {blobName}");
                
                var operation = request.SendWebRequest();
                
                // Track progress
                while (!operation.isDone)
                {
                    OnDownloadProgress?.Invoke(blobName, request.downloadProgress);
                    await Task.Yield();
                }
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    Debug.Log($"[AzureStorage] Blob downloaded successfully: {blobName} ({request.downloadHandler.data.Length} bytes)");
                    OnDownloadComplete?.Invoke(blobName);
                    return request.downloadHandler.data;
                }
                else
                {
                    throw new Exception($"Download failed: {request.error}");
                }
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"[AzureStorage] Download failed for {blobName}: {e.Message}");
            OnStorageError?.Invoke("download", e.Message);
            return null;
        }
    }
    
    public async Task<bool> DeleteBlobAsync(string blobName)
    {
        string url = $"{baseStorageUrl}/{blobName}?{sasToken}";
        
        try
        {
            using (UnityWebRequest request = UnityWebRequest.Delete(url))
            {
                Debug.Log($"[AzureStorage] Deleting blob: {blobName}");
                
                await request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    Debug.Log($"[AzureStorage] Blob deleted successfully: {blobName}");
                    return true;
                }
                else
                {
                    throw new Exception($"Delete failed: {request.error}");
                }
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"[AzureStorage] Delete failed for {blobName}: {e.Message}");
            OnStorageError?.Invoke("delete", e.Message);
            return false;
        }
    }
    
    // Asset Management
    public async Task<string> UploadGameAssetAsync(string assetPath, string assetId, string version = "latest")
    {
        try
        {
            byte[] assetData = File.ReadAllBytes(assetPath);
            string blobName = $"assets/{assetId}/{version}/{Path.GetFileName(assetPath)}";
            string contentType = GetContentType(assetPath);
            
            string downloadUrl = await UploadBlobAsync(blobName, assetData, contentType);
            
            if (!string.IsNullOrEmpty(downloadUrl))
            {
                // Update asset metadata
                await UpdateAssetMetadata(assetId, version, downloadUrl, assetData.Length);
            }
            
            return downloadUrl;
        }
        catch (Exception e)
        {
            Debug.LogError($"[AzureStorage] Upload game asset failed: {e.Message}");
            OnStorageError?.Invoke("uploadAsset", e.Message);
            return null;
        }
    }
    
    public async Task<byte[]> DownloadGameAssetAsync(string assetId, string version = "latest")
    {
        try
        {
            // Get asset metadata to find the correct blob name
            var metadata = await GetAssetMetadata(assetId, version);
            if (metadata == null)
            {
                throw new Exception($"Asset metadata not found: {assetId}/{version}");
            }
            
            string blobName = $"assets/{assetId}/{version}/{metadata.filename}";
            return await DownloadBlobAsync(blobName);
        }
        catch (Exception e)
        {
            Debug.LogError($"[AzureStorage] Download game asset failed: {e.Message}");
            OnStorageError?.Invoke("downloadAsset", e.Message);
            return null;
        }
    }
    
    // User Data Management
    public async Task<bool> SaveUserDataAsync<T>(string userId, string dataType, T data)
    {
        try
        {
            string jsonData = JsonUtility.ToJson(data, true);
            byte[] dataBytes = Encoding.UTF8.GetBytes(jsonData);
            
            string blobName = $"userdata/{userId}/{dataType}.json";
            string downloadUrl = await UploadBlobAsync(blobName, dataBytes, "application/json");
            
            return !string.IsNullOrEmpty(downloadUrl);
        }
        catch (Exception e)
        {
            Debug.LogError($"[AzureStorage] Save user data failed: {e.Message}");
            OnStorageError?.Invoke("saveUserData", e.Message);
            return false;
        }
    }
    
    public async Task<T> LoadUserDataAsync<T>(string userId, string dataType)
    {
        try
        {
            string blobName = $"userdata/{userId}/{dataType}.json";
            byte[] dataBytes = await DownloadBlobAsync(blobName);
            
            if (dataBytes != null)
            {
                string jsonData = Encoding.UTF8.GetString(dataBytes);
                return JsonUtility.FromJson<T>(jsonData);
            }
            
            return default(T);
        }
        catch (Exception e)
        {
            Debug.LogError($"[AzureStorage] Load user data failed: {e.Message}");
            OnStorageError?.Invoke("loadUserData", e.Message);
            return default(T);
        }
    }
    
    // CDN Integration
    public string GetCDNUrl(string blobName)
    {
        if (!string.IsNullOrEmpty(cdnEndpoint))
        {
            return $"{cdnEndpoint}/{blobName}";
        }
        
        return GetDownloadUrl(blobName);
    }
    
    private string GetDownloadUrl(string blobName)
    {
        // Use CDN if available, otherwise direct blob URL
        if (!string.IsNullOrEmpty(cdnEndpoint))
        {
            return $"{cdnEndpoint}/{blobName}";
        }
        
        return $"{baseStorageUrl}/{blobName}";
    }
    
    // Metadata Management
    private async Task UpdateAssetMetadata(string assetId, string version, string downloadUrl, long fileSize)
    {
        var metadata = new AssetMetadata
        {
            assetId = assetId,
            version = version,
            downloadUrl = downloadUrl,
            fileSize = fileSize,
            uploadTime = DateTime.UtcNow,
            filename = Path.GetFileName(downloadUrl)
        };
        
        string metadataJson = JsonUtility.ToJson(metadata);
        byte[] metadataBytes = Encoding.UTF8.GetBytes(metadataJson);
        
        string metadataBlobName = $"metadata/{assetId}/{version}.json";
        await UploadBlobAsync(metadataBlobName, metadataBytes, "application/json");
    }
    
    private async Task<AssetMetadata> GetAssetMetadata(string assetId, string version)
    {
        try
        {
            string metadataBlobName = $"metadata/{assetId}/{version}.json";
            byte[] metadataBytes = await DownloadBlobAsync(metadataBlobName);
            
            if (metadataBytes != null)
            {
                string metadataJson = Encoding.UTF8.GetString(metadataBytes);
                return JsonUtility.FromJson<AssetMetadata>(metadataJson);
            }
            
            return null;
        }
        catch
        {
            return null;
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
            ".unity3d" => "application/unity3d",
            _ => "application/octet-stream"
        };
    }
    
    public void UpdateSasToken(string newSasToken)
    {
        sasToken = newSasToken;
        Debug.Log("[AzureStorage] SAS token updated");
    }
    
    // Data Classes
    [Serializable]
    private class AssetMetadata
    {
        public string assetId;
        public string version;
        public string downloadUrl;
        public long fileSize;
        public DateTime uploadTime;
        public string filename;
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Azure Architecture Design
```
PROMPT TEMPLATE - Azure Unity Architecture:

"Design a comprehensive Microsoft Azure architecture for this Unity game:

Game Details:
- Type: [Mobile/PC/Console game type]
- Scale: [Expected concurrent users and growth]
- Features: [Multiplayer/Social/Analytics/etc.]
- Budget: [Startup/Enterprise level constraints]

Create architecture including:
1. PlayFab services configuration and scaling
2. Azure Functions for serverless game logic
3. Azure Storage and CDN for global asset delivery
4. Azure SQL or Cosmos DB for game data
5. Application Insights for monitoring
6. Azure Active Directory for enterprise auth
7. Security and compliance implementation
8. Cost optimization strategies
9. Multi-region deployment considerations"
```

### PlayFab Integration Optimization
```
PROMPT TEMPLATE - PlayFab Performance Tuning:

"Optimize this PlayFab integration for Unity:

```csharp
[PASTE YOUR PLAYFAB CODE]
```

Performance Requirements:
- Platform: [Mobile/PC/Console targets]
- Features: [Leaderboards/Multiplayer/Economy/etc.]
- Scale: [Expected player volume]
- Monetization: [IAP/Virtual currency/Subscriptions]

Provide optimizations for:
1. Authentication flow and session management
2. Player data structure and caching
3. Virtual economy and transaction handling
4. Leaderboard and statistics optimization
5. Cloud script performance tuning
6. Error handling and retry strategies
7. Analytics and telemetry integration
8. Cost optimization recommendations"
```

## 💡 Key Azure Integration Principles

### Essential Azure Unity Checklist
- **PlayFab Integration** - Comprehensive game backend with economy and social features
- **Azure Functions** - Serverless game logic and anti-cheat validation
- **Secure Authentication** - Multiple authentication providers and SSO support
- **Global CDN** - Fast asset delivery worldwide with edge caching
- **Real-time Analytics** - Player behavior tracking and business intelligence
- **Scalable Storage** - Blob storage for assets and user-generated content
- **Performance Monitoring** - Application insights and custom telemetry
- **Cost Management** - Resource optimization and budget monitoring

### Common Azure Unity Challenges
1. **PlayFab complexity** - Understanding the extensive feature set and pricing
2. **Authentication flows** - Managing multiple auth providers and edge cases
3. **Cloud script limitations** - Working within execution time and memory constraints
4. **Data modeling** - Designing efficient schemas for player and game data
5. **Cost control** - Managing expenses with scaling usage
6. **Regional availability** - Handling global deployment and latency
7. **Integration testing** - Testing cloud-dependent features effectively
8. **Performance optimization** - Balancing features with response times

This comprehensive Azure integration provides Unity developers with enterprise-grade cloud services including robust game backend, serverless computing, global content delivery, and advanced analytics, enabling scalable multiplayer games with rich social and economic features.