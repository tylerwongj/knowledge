# @o-Advanced-Async-Patterns-Unity

## 🎯 Learning Objectives

- Master async/await patterns in Unity game development
- Implement robust asynchronous workflows for game operations
- Handle complex async scenarios with proper error handling and cancellation
- Optimize performance with advanced async techniques

## 🔧 Core Async Patterns for Unity

### Async/Await Fundamentals in Unity Context

```csharp
using System;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;

public class AsyncUnityOperations : MonoBehaviour
{
    // Convert Unity coroutines to async/await
    public async Task<string> LoadTextFromWeb(string url)
    {
        using (var request = UnityWebRequest.Get(url))
        {
            // Extension method to make UnityWebRequest awaitable
            await request.SendWebRequest().AsTask();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                return request.downloadHandler.text;
            }
            else
            {
                throw new Exception($"Failed to load from {url}: {request.error}");
            }
        }
    }
    
    // Async resource loading
    public async Task<T> LoadResourceAsync<T>(string path) where T : UnityEngine.Object
    {
        var resourceRequest = Resources.LoadAsync<T>(path);
        
        // Convert ResourceRequest to Task
        while (!resourceRequest.isDone)
        {
            await Task.Yield(); // Yield control back to Unity's main thread
        }
        
        return resourceRequest.asset as T;
    }
    
    // Async scene operations
    public async Task LoadSceneAsync(string sceneName, CancellationToken cancellationToken = default)
    {
        var operation = UnityEngine.SceneManagement.SceneManager.LoadSceneAsync(sceneName);
        
        while (!operation.isDone)
        {
            cancellationToken.ThrowIfCancellationRequested();
            
            // Report progress if needed
            var progress = operation.progress;
            Debug.Log($"Scene loading progress: {progress * 100:F1}%");
            
            await Task.Yield();
        }
    }
}

// Extension methods for Unity operations
public static class UnityAsyncExtensions
{
    public static Task AsTask(this UnityWebRequestAsyncOperation operation)
    {
        var tcs = new TaskCompletionSource<bool>();
        
        operation.completed += _ =>
        {
            tcs.SetResult(true);
        };
        
        return tcs.Task;
    }
    
    public static Task<T> AsTask<T>(this ResourceRequest request) where T : UnityEngine.Object
    {
        var tcs = new TaskCompletionSource<T>();
        
        request.completed += _ =>
        {
            tcs.SetResult(request.asset as T);
        };
        
        return tcs.Task;
    }
}
```

### Advanced Async Game Systems

```csharp
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

// Async game state management
public class AsyncGameStateManager : MonoBehaviour
{
    private readonly Dictionary<string, Func<CancellationToken, Task>> stateTransitions 
        = new Dictionary<string, Func<CancellationToken, Task>>();
    
    private string currentState;
    private CancellationTokenSource currentStateCancellation;
    
    void Start()
    {
        // Register state transitions
        stateTransitions["MainMenu"] = EnterMainMenuState;
        stateTransitions["Loading"] = EnterLoadingState;
        stateTransitions["Gameplay"] = EnterGameplayState;
        stateTransitions["GameOver"] = EnterGameOverState;
        
        // Start with main menu
        _ = TransitionToStateAsync("MainMenu");
    }
    
    public async Task TransitionToStateAsync(string newState)
    {
        if (currentState == newState) return;
        
        // Cancel current state
        currentStateCancellation?.Cancel();
        currentStateCancellation = new CancellationTokenSource();
        
        string previousState = currentState;
        currentState = newState;
        
        Debug.Log($"Transitioning from {previousState} to {newState}");
        
        try
        {
            if (stateTransitions.TryGetValue(newState, out var transition))
            {
                await transition(currentStateCancellation.Token);
            }
        }
        catch (OperationCanceledException)
        {
            Debug.Log($"State transition to {newState} was cancelled");
        }
        catch (Exception ex)
        {
            Debug.LogError($"Error in state {newState}: {ex}");
        }
    }
    
    private async Task EnterMainMenuState(CancellationToken cancellationToken)
    {
        // Async main menu logic
        await LoadUIAsync("MainMenuUI", cancellationToken);
        
        // Wait for user input or timeout
        while (!cancellationToken.IsCancellationRequested)
        {
            if (Input.GetKeyDown(KeyCode.Space))
            {
                await TransitionToStateAsync("Loading");
                return;
            }
            
            await Task.Yield();
        }
    }
    
    private async Task EnterLoadingState(CancellationToken cancellationToken)
    {
        await LoadUIAsync("LoadingUI", cancellationToken);
        
        // Simulate loading with progress
        for (int i = 0; i <= 100; i++)
        {
            cancellationToken.ThrowIfCancellationRequested();
            
            // Update loading progress
            Debug.Log($"Loading: {i}%");
            
            await Task.Delay(50, cancellationToken); // Simulate work
        }
        
        await TransitionToStateAsync("Gameplay");
    }
    
    private async Task EnterGameplayState(CancellationToken cancellationToken)
    {
        await LoadUIAsync("GameplayUI", cancellationToken);
        
        // Game loop
        while (!cancellationToken.IsCancellationRequested)
        {
            // Update game logic
            await UpdateGameLogicAsync(cancellationToken);
            
            // Check for game over conditions
            if (CheckGameOverConditions())
            {
                await TransitionToStateAsync("GameOver");
                return;
            }
            
            await Task.Yield();
        }
    }
    
    private async Task EnterGameOverState(CancellationToken cancellationToken)
    {
        await LoadUIAsync("GameOverUI", cancellationToken);
        
        // Wait for restart input
        await Task.Delay(2000, cancellationToken); // Show game over for 2 seconds
        await TransitionToStateAsync("MainMenu");
    }
    
    private async Task LoadUIAsync(string uiName, CancellationToken cancellationToken)
    {
        Debug.Log($"Loading UI: {uiName}");
        await Task.Delay(500, cancellationToken); // Simulate UI loading
    }
    
    private async Task UpdateGameLogicAsync(CancellationToken cancellationToken)
    {
        // Simulate game logic update
        await Task.Yield();
    }
    
    private bool CheckGameOverConditions()
    {
        return Input.GetKeyDown(KeyCode.G); // Simulate game over trigger
    }
    
    void OnDestroy()
    {
        currentStateCancellation?.Cancel();
    }
}
```

### Async Networking and API Integration

```csharp
using System;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class APIResponse<T>
{
    public bool success;
    public T data;
    public string message;
    public int statusCode;
}

[Serializable]
public class PlayerData
{
    public string playerId;
    public string playerName;
    public int level;
    public int experience;
}

public class AsyncNetworkManager : MonoBehaviour
{
    private const string BASE_URL = "https://api.yourgame.com";
    private readonly SemaphoreSlim requestSemaphore = new SemaphoreSlim(3, 3); // Max 3 concurrent requests
    
    // Generic async HTTP request method
    private async Task<APIResponse<T>> SendRequestAsync<T>(
        string endpoint, 
        string method = "GET", 
        object payload = null,
        CancellationToken cancellationToken = default)
    {
        await requestSemaphore.WaitAsync(cancellationToken);
        
        try
        {
            string url = $"{BASE_URL}/{endpoint}";
            using var request = new UnityWebRequest(url, method);
            
            // Setup headers
            request.SetRequestHeader("Content-Type", "application/json");
            request.SetRequestHeader("Authorization", $"Bearer {GetAuthToken()}");
            
            // Add payload for POST/PUT requests
            if (payload != null)
            {
                string jsonPayload = JsonUtility.ToJson(payload);
                byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonPayload);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            }
            
            request.downloadHandler = new DownloadHandlerBuffer();
            
            // Send request with timeout
            var operation = request.SendWebRequest();
            var timeoutTask = Task.Delay(30000, cancellationToken); // 30 second timeout
            var completedTask = await Task.WhenAny(operation.AsTask(), timeoutTask);
            
            if (completedTask == timeoutTask)
            {
                throw new TimeoutException("Request timed out");
            }
            
            // Parse response
            var response = new APIResponse<T>
            {
                statusCode = (int)request.responseCode,
                success = request.result == UnityWebRequest.Result.Success
            };
            
            if (response.success)
            {
                string responseText = request.downloadHandler.text;
                response.data = JsonUtility.FromJson<T>(responseText);
            }
            else
            {
                response.message = request.error;
            }
            
            return response;
        }
        finally
        {
            requestSemaphore.Release();
        }
    }
    
    // Specific API methods
    public async Task<PlayerData> GetPlayerDataAsync(string playerId, CancellationToken cancellationToken = default)
    {
        var response = await SendRequestAsync<PlayerData>($"players/{playerId}", cancellationToken: cancellationToken);
        
        if (!response.success)
        {
            throw new Exception($"Failed to get player data: {response.message}");
        }
        
        return response.data;
    }
    
    public async Task<bool> UpdatePlayerDataAsync(PlayerData playerData, CancellationToken cancellationToken = default)
    {
        var response = await SendRequestAsync<PlayerData>(
            $"players/{playerData.playerId}", 
            "PUT", 
            playerData, 
            cancellationToken
        );
        
        return response.success;
    }
    
    // Batch operations with concurrency control
    public async Task<PlayerData[]> GetMultiplePlayersAsync(
        string[] playerIds, 
        CancellationToken cancellationToken = default)
    {
        var tasks = new Task<PlayerData>[playerIds.Length];
        
        for (int i = 0; i < playerIds.Length; i++)
        {
            string playerId = playerIds[i];
            tasks[i] = GetPlayerDataAsync(playerId, cancellationToken);
        }
        
        try
        {
            return await Task.WhenAll(tasks);
        }
        catch (Exception ex)
        {
            Debug.LogError($"Error in batch player data retrieval: {ex}");
            throw;
        }
    }
    
    // Retry pattern with exponential backoff
    public async Task<T> ExecuteWithRetryAsync<T>(
        Func<CancellationToken, Task<T>> operation,
        int maxRetries = 3,
        CancellationToken cancellationToken = default)
    {
        for (int attempt = 0; attempt <= maxRetries; attempt++)
        {
            try
            {
                return await operation(cancellationToken);
            }
            catch (Exception ex) when (attempt < maxRetries && ShouldRetry(ex))
            {
                int delay = (int)Math.Pow(2, attempt) * 1000; // Exponential backoff
                Debug.Log($"Retry attempt {attempt + 1} after {delay}ms delay");
                
                await Task.Delay(delay, cancellationToken);
            }
        }
        
        // Final attempt without catch
        return await operation(cancellationToken);
    }
    
    private bool ShouldRetry(Exception ex)
    {
        // Define which exceptions should trigger a retry
        return ex is TimeoutException || 
               ex is UnityEngine.Networking.UnityWebRequest.Result.ConnectionError ||
               ex is UnityEngine.Networking.UnityWebRequest.Result.DataProcessingError;
    }
    
    private string GetAuthToken()
    {
        // Implement your authentication token retrieval logic
        return PlayerPrefs.GetString("AuthToken", "");
    }
}
```

### Advanced Cancellation and Error Handling

```csharp
using System;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

public class AsyncErrorHandlingExample : MonoBehaviour
{
    private CancellationTokenSource mainCancellationSource;
    
    void Start()
    {
        mainCancellationSource = new CancellationTokenSource();
        
        // Start main game loop with proper error handling
        _ = RunMainGameLoopAsync(mainCancellationSource.Token);
    }
    
    private async Task RunMainGameLoopAsync(CancellationToken cancellationToken)
    {
        while (!cancellationToken.IsCancellationRequested)
        {
            try
            {
                await ExecuteGameFrameAsync(cancellationToken);
            }
            catch (OperationCanceledException)
            {
                Debug.Log("Game loop cancelled");
                break;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error in game loop: {ex}");
                
                // Implement recovery strategy
                await HandleGameErrorAsync(ex, cancellationToken);
            }
        }
    }
    
    private async Task ExecuteGameFrameAsync(CancellationToken cancellationToken)
    {
        // Combine multiple cancellation sources
        using var frameTimeout = new CancellationTokenSource(TimeSpan.FromSeconds(1));
        using var combinedCts = CancellationTokenSource.CreateLinkedTokenSource(
            cancellationToken, 
            frameTimeout.Token
        );
        
        // Execute multiple async operations in parallel
        var tasks = new[]
        {
            UpdatePlayerLogicAsync(combinedCts.Token),
            UpdateEnemyLogicAsync(combinedCts.Token),
            UpdateUIAsync(combinedCts.Token)
        };
        
        await Task.WhenAll(tasks);
    }
    
    private async Task UpdatePlayerLogicAsync(CancellationToken cancellationToken)
    {
        // Simulate player update logic
        await Task.Delay(50, cancellationToken);
        
        // Periodically check for cancellation
        cancellationToken.ThrowIfCancellationRequested();
        
        // More work...
    }
    
    private async Task UpdateEnemyLogicAsync(CancellationToken cancellationToken)
    {
        await Task.Delay(30, cancellationToken);
    }
    
    private async Task UpdateUIAsync(CancellationToken cancellationToken)
    {
        await Task.Delay(20, cancellationToken);
    }
    
    private async Task HandleGameErrorAsync(Exception exception, CancellationToken cancellationToken)
    {
        Debug.Log("Attempting error recovery...");
        
        // Implement specific recovery strategies based on exception type
        switch (exception)
        {
            case TimeoutException:
                await HandleTimeoutErrorAsync(cancellationToken);
                break;
            case NetworkException:
                await HandleNetworkErrorAsync(cancellationToken);
                break;
            default:
                await HandleGenericErrorAsync(exception, cancellationToken);
                break;
        }
    }
    
    private async Task HandleTimeoutErrorAsync(CancellationToken cancellationToken)
    {
        Debug.Log("Handling timeout error - reducing frame complexity");
        await Task.Delay(100, cancellationToken);
    }
    
    private async Task HandleNetworkErrorAsync(CancellationToken cancellationToken)
    {
        Debug.Log("Handling network error - switching to offline mode");
        await Task.Delay(1000, cancellationToken);
    }
    
    private async Task HandleGenericErrorAsync(Exception exception, CancellationToken cancellationToken)
    {
        Debug.LogError($"Generic error recovery for: {exception.GetType().Name}");
        await Task.Delay(500, cancellationToken);
    }
    
    void OnDestroy()
    {
        mainCancellationSource?.Cancel();
        mainCancellationSource?.Dispose();
    }
}

// Custom exception types for better error handling
public class NetworkException : Exception
{
    public NetworkException(string message) : base(message) { }
    public NetworkException(string message, Exception innerException) : base(message, innerException) { }
}

public class GameDataException : Exception
{
    public GameDataException(string message) : base(message) { }
    public GameDataException(string message, Exception innerException) : base(message, innerException) { }
}
```

## 🚀 AI/LLM Integration Opportunities

### Async AI-Powered Game Features

```csharp
using System;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

public class AIAsyncGameFeatures : MonoBehaviour
{
    // AI-powered content generation
    public async Task<string> GenerateDialogueAsync(string context, CancellationToken cancellationToken = default)
    {
        // Simulate AI API call
        var aiRequest = new
        {
            prompt = $"Generate game dialogue for context: {context}",
            maxTokens = 100,
            temperature = 0.7f
        };
        
        // Use async networking to call AI service
        var networkManager = FindObjectOfType<AsyncNetworkManager>();
        var response = await networkManager.ExecuteWithRetryAsync(async (ct) =>
        {
            // Replace with actual AI service call
            await Task.Delay(2000, ct); // Simulate AI processing time
            return "AI-generated dialogue response";
        }, cancellationToken: cancellationToken);
        
        return response;
    }
    
    // Dynamic difficulty adjustment with AI
    public async Task<float> CalculateOptimalDifficultyAsync(
        PlayerPerformanceData performanceData,
        CancellationToken cancellationToken = default)
    {
        // Async AI analysis of player performance
        await Task.Delay(500, cancellationToken); // Simulate AI processing
        
        // Mock AI calculation
        float baseDifficulty = 0.5f;
        float performanceModifier = performanceData.averageScore / 100f;
        
        return Mathf.Clamp(baseDifficulty + performanceModifier, 0.1f, 1.0f);
    }
}

[Serializable]
public class PlayerPerformanceData
{
    public float averageScore;
    public float averageReactionTime;
    public int gamesPlayed;
    public float successRate;
}
```

## 💡 Key Async Best Practices

### Performance Optimization
- **Use ConfigureAwait(false)**: For library code to avoid UI thread capture
- **Avoid Async Void**: Use async Task instead, except for event handlers
- **Proper Cancellation**: Always support CancellationToken for long-running operations
- **Resource Management**: Dispose of resources properly in async contexts

### Unity-Specific Considerations
- **Main Thread Safety**: Use Unity's SynchronizationContext for UI updates
- **Frame Spreading**: Use Task.Yield() to return control to Unity
- **Lifecycle Management**: Handle component destruction during async operations
- **Error Boundaries**: Implement proper exception handling for game stability

### Advanced Patterns
- **Producer-Consumer**: Use async queues for data processing
- **Circuit Breaker**: Implement fallback patterns for network operations
- **Bulkhead**: Isolate critical systems with separate task schedulers
- **Timeout Patterns**: Always implement timeouts for external operations

This comprehensive guide provides production-ready async patterns specifically tailored for Unity game development, ensuring robust and performant asynchronous operations.