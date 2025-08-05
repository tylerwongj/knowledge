# @r-Unity-Services-Integration - Unity Cloud Services & Backend

## 🎯 Learning Objectives

- Master Unity Cloud Services integration for scalable game development
- Implement authentication, analytics, and remote configuration systems
- Design multiplayer networking architecture with Unity services
- Optimize cloud-based asset delivery and live operations

## 🔧 Unity Cloud Services Overview

### Authentication Service
```csharp
using Unity.Services.Authentication;
using Unity.Services.Core;

public class AuthenticationManager : MonoBehaviour
{
    async void Start()
    {
        await UnityServices.InitializeAsync();
        
        if (!AuthenticationService.Instance.IsSignedIn)
        {
            await AuthenticationService.Instance.SignInAnonymouslyAsync();
        }
        
        Debug.Log($"Player ID: {AuthenticationService.Instance.PlayerId}");
    }
    
    public async Task SignInWithApple()
    {
        try
        {
            await AuthenticationService.Instance.SignInWithAppleAsync(idToken);
            Debug.Log("Sign in successful");
        }
        catch (AuthenticationException ex)
        {
            Debug.LogError($"Sign in failed: {ex.Message}");
        }
    }
}
```

### Cloud Save Implementation
```csharp
using Unity.Services.CloudSave;

public class CloudSaveManager
{
    public async Task SavePlayerData(PlayerData data)
    {
        var saveData = new Dictionary<string, object>
        {
            {"playerLevel", data.level},
            {"playerScore", data.score},
            {"unlockedItems", data.unlockedItems}
        };
        
        await CloudSaveService.Instance.Data.Player.SaveAsync(saveData);
    }
    
    public async Task<PlayerData> LoadPlayerData()
    {
        var query = await CloudSaveService.Instance.Data.Player.LoadAsync(
            new HashSet<string> {"playerLevel", "playerScore", "unlockedItems"}
        );
        
        return new PlayerData
        {
            level = query.TryGetValue("playerLevel", out var level) ? (int)level : 1,
            score = query.TryGetValue("playerScore", out var score) ? (long)score : 0,
            unlockedItems = query.TryGetValue("unlockedItems", out var items) ? 
                items as List<string> : new List<string>()
        };
    }
}
```

## 🚀 Analytics & Live Operations

### Unity Analytics Integration
```csharp
using Unity.Services.Analytics;

public class AnalyticsManager : MonoBehaviour
{
    void Start()
    {
        AnalyticsService.Instance.StartDataCollection();
    }
    
    public void TrackLevelComplete(int level, float timeToComplete)
    {
        var parameters = new Dictionary<string, object>
        {
            {"level", level},
            {"completion_time", timeToComplete},
            {"player_level", GameManager.Instance.PlayerLevel}
        };
        
        AnalyticsService.Instance.CustomData("level_complete", parameters);
    }
    
    public void TrackPurchase(string itemId, string currency, int amount)
    {
        var parameters = new Dictionary<string, object>
        {
            {"item_id", itemId},
            {"currency_type", currency},
            {"amount", amount}
        };
        
        AnalyticsService.Instance.CustomData("item_purchased", parameters);
    }
}
```

### Remote Configuration
```csharp
using Unity.Services.RemoteConfig;

public class RemoteConfigManager : MonoBehaviour
{
    [SerializeField] private float defaultEnemySpeed = 5f;
    [SerializeField] private int defaultMaxHealth = 100;
    
    async void Start()
    {
        await UnityServices.InitializeAsync();
        
        RemoteConfigService.Instance.FetchCompleted += OnConfigFetched;
        await RemoteConfigService.Instance.FetchConfigsAsync(new userAttributes{}, 
            new appAttributes{});
    }
    
    void OnConfigFetched(ConfigResponse response)
    {
        switch (response.requestOrigin)
        {
            case ConfigOrigin.Default:
                Debug.Log("No config available, using default values");
                break;
            case ConfigOrigin.Cached:
                Debug.Log("Config loaded from cache");
                break;
            case ConfigOrigin.Remote:
                Debug.Log("Config loaded from remote");
                ApplyRemoteConfig();
                break;
        }
    }
    
    void ApplyRemoteConfig()
    {
        var enemySpeed = RemoteConfigService.Instance.appConfig.GetFloat("enemy_speed", defaultEnemySpeed);
        var maxHealth = RemoteConfigService.Instance.appConfig.GetInt("max_health", defaultMaxHealth);
        
        GameSettings.Instance.UpdateEnemySpeed(enemySpeed);
        GameSettings.Instance.UpdateMaxHealth(maxHealth);
    }
}
```

## 🎮 Multiplayer & Networking

### Unity Netcode Integration
```csharp
using Unity.Netcode;

public class NetworkGameManager : NetworkBehaviour
{
    [SerializeField] private GameObject playerPrefab;
    
    void Start()
    {
        if (IsServer)
        {
            NetworkManager.Singleton.OnClientConnectedCallback += OnClientConnected;
            NetworkManager.Singleton.OnClientDisconnectCallback += OnClientDisconnected;
        }
    }
    
    void OnClientConnected(ulong clientId)
    {
        Debug.Log($"Client {clientId} connected");
        SpawnPlayerServerRpc(clientId);
    }
    
    [ServerRpc]
    void SpawnPlayerServerRpc(ulong clientId)
    {
        var playerInstance = Instantiate(playerPrefab);
        var networkObject = playerInstance.GetComponent<NetworkObject>();
        networkObject.SpawnAsPlayerObject(clientId);
    }
    
    void OnClientDisconnected(ulong clientId)
    {
        Debug.Log($"Client {clientId} disconnected");
    }
}
```

### Lobby Service Implementation
```csharp
using Unity.Services.Lobbies;
using Unity.Services.Lobbies.Models;

public class LobbyManager : MonoBehaviour
{
    private Lobby currentLobby;
    private string lobbyId;
    
    public async Task<Lobby> CreateLobby(string lobbyName, int maxPlayers)
    {
        var options = new CreateLobbyOptions
        {
            IsPrivate = false,
            Data = new Dictionary<string, DataObject>
            {
                {"GameMode", new DataObject(DataObject.VisibilityOptions.Public, "TeamDeathmatch")},
                {"Map", new DataObject(DataObject.VisibilityOptions.Public, "Forest")}
            }
        };
        
        currentLobby = await LobbyService.Instance.CreateLobbyAsync(lobbyName, maxPlayers, options);
        lobbyId = currentLobby.Id;
        
        StartCoroutine(HeartbeatLobbyCoroutine());
        
        return currentLobby;
    }
    
    public async Task<List<Lobby>> QueryLobbies()
    {
        var options = new QueryLobbiesOptions
        {
            Count = 25,
            Filters = new List<QueryFilter>
            {
                new QueryFilter(QueryFilter.FieldOptions.AvailableSlots, "0", QueryFilter.OpOptions.GT),
                new QueryFilter(QueryFilter.FieldOptions.S1, "TeamDeathmatch", QueryFilter.OpOptions.EQ)
            }
        };
        
        var response = await LobbyService.Instance.QueryLobbiesAsync(options);
        return response.Results;
    }
    
    IEnumerator HeartbeatLobbyCoroutine()
    {
        while (currentLobby != null)
        {
            LobbyService.Instance.SendHeartbeatPingAsync(lobbyId);
            yield return new WaitForSeconds(15);
        }
    }
}
```

## 💡 Cloud Build & Deployment

### Unity Cloud Build Configuration
```csharp
using UnityEngine;
using System.Collections.Generic;

[System.Serializable]
public class BuildConfiguration
{
    public string buildTargetName;
    public BuildTarget platform;
    public string scmBranch;
    public Dictionary<string, string> environmentVariables;
    
    public void ConfigurePreBuildScript()
    {
        // Custom pre-build configurations
        #if UNITY_CLOUD_BUILD
        var manifest = UnityCloudBuildManifest.LoadManifest();
        Debug.Log($"Build Number: {manifest.GetValue<string>("buildNumber")}");
        Debug.Log($"Git Commit: {manifest.GetValue<string>("scmCommitId")}");
        #endif
    }
}

public class CloudBuildPreProcessor
{
    public static void PreExport()
    {
        // Configure build settings
        PlayerSettings.bundleVersion = GetVersionFromGit();
        PlayerSettings.applicationIdentifier = "com.yourstudio.yourgame";
        
        // Platform-specific configurations
        #if UNITY_ANDROID
        PlayerSettings.Android.bundleVersionCode = GetBuildNumber();
        #elif UNITY_IOS
        PlayerSettings.iOS.buildNumber = GetBuildNumber().ToString();
        #endif
    }
    
    static string GetVersionFromGit()
    {
        // Implementation to get version from git tags
        return "1.0.0";
    }
    
    static int GetBuildNumber()
    {
        // Implementation to get build number
        return UnityCloudBuildManifest.LoadManifest().GetValue<int>("buildNumber");
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Automated Cloud Service Configuration
```csharp
// Prompt: "Generate Unity Cloud Services configuration for [game type] with [features]"
public class CloudServiceAutomator
{
    public void GenerateServiceConfiguration()
    {
        // AI-generated service setup based on game requirements
        // Automated authentication flow configuration
        // Dynamic analytics event generation
        // Remote config parameter optimization
    }
}
```

### Performance Monitoring Automation
```csharp
// Prompt: "Create performance monitoring setup for Unity Cloud Services"
public class PerformanceMonitor
{
    public void SetupAutomatedMetrics()
    {
        // AI-optimized metric collection
        // Automated performance alerting
        // Dynamic scaling recommendations
    }
}
```

## 💡 Key Highlights

- **Service Integration**: Unity Cloud Services provide scalable backend infrastructure
- **Authentication**: Implement secure player identity and cross-platform accounts
- **Live Operations**: Use remote config and analytics for data-driven decisions
- **Multiplayer**: Leverage Netcode and Lobby services for seamless networking
- **Cloud Build**: Automate build and deployment processes across platforms
- **Analytics**: Track player behavior and optimize game experience
- **Scalability**: Design for millions of players with Unity's cloud infrastructure

## 🎯 Best Practices

1. **Service Initialization**: Always initialize Unity Services early in application lifecycle
2. **Error Handling**: Implement robust error handling for network operations
3. **Caching**: Cache remote data locally for offline functionality
4. **Security**: Never expose sensitive data in client-side code
5. **Performance**: Batch cloud operations to minimize API calls
6. **Testing**: Use Unity's testing tools for cloud service validation
7. **Monitoring**: Implement comprehensive logging and analytics

## 📚 Unity Services Resources

- Unity Cloud Services Documentation
- Netcode for GameObjects Guide
- Unity Analytics Best Practices
- Remote Config Implementation Guide
- Cloud Build Setup Documentation
- Lobby Service API Reference
- Authentication Service Integration