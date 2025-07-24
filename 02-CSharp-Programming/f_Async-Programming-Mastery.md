# @f-Async-Programming-Mastery - Advanced Async/Await & Concurrency in C#

## 🎯 Learning Objectives
- Master async/await patterns for Unity and general C# development
- Implement advanced concurrency patterns and thread-safe operations
- Create AI-enhanced async workflow automation and optimization
- Develop high-performance asynchronous game systems

## 🔧 Core Async Programming Concepts

### Advanced Async/Await Patterns
```csharp
// Async operation manager for Unity
public class AsyncOperationManager : MonoBehaviour
{
    private readonly CancellationTokenSource cancellationTokenSource = new CancellationTokenSource();
    
    void Start()
    {
        // Start multiple async operations
        _ = LoadGameDataAsync(cancellationTokenSource.Token);
        _ = InitializeNetworkAsync(cancellationTokenSource.Token);
        _ = PreloadAssetsAsync(cancellationTokenSource.Token);
    }
    
    // Async loading with progress reporting
    public async Task<GameData> LoadGameDataAsync(CancellationToken cancellationToken)
    {
        var progress = new Progress<float>(value => 
        {
            Debug.Log($"Loading progress: {value:P}");
        });
        
        try
        {
            // Simulate async loading with progress
            var gameData = new GameData();
            
            for (int i = 0; i <= 100; i += 10)
            {
                cancellationToken.ThrowIfCancellationRequested();
                
                // Simulate work
                await Task.Delay(100, cancellationToken);
                
                // Report progress
                ((IProgress<float>)progress)?.Report(i / 100f);
            }
            
            return gameData;
        }
        catch (OperationCanceledException)
        {
            Debug.Log("Game data loading was cancelled");
            throw;
        }
    }
    
    // Async with timeout and retry logic
    public async Task<bool> InitializeNetworkAsync(CancellationToken cancellationToken)
    {
        const int maxRetries = 3;
        const int timeoutMs = 5000;
        
        for (int attempt = 1; attempt <= maxRetries; attempt++)
        {
            try
            {
                using var timeoutCts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
                timeoutCts.CancelAfter(timeoutMs);
                
                await ConnectToServerAsync(timeoutCts.Token);
                Debug.Log("Network initialized successfully");
                return true;
            }
            catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested)
            {
                throw; // Re-throw if main cancellation was requested
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Network initialization attempt {attempt} failed: {ex.Message}");
                
                if (attempt == maxRetries)
                {
                    Debug.LogError("Network initialization failed after all retries");
                    return false;
                }
                
                // Exponential backoff
                await Task.Delay(1000 * attempt, cancellationToken);
            }
        }
        
        return false;
    }
    
    private async Task ConnectToServerAsync(CancellationToken cancellationToken)
    {
        // Simulate network connection
        await Task.Delay(2000, cancellationToken);
        
        // Simulate random failure for demo
        if (UnityEngine.Random.value < 0.3f)
        {
            throw new NetworkException("Connection failed");
        }
    }
    
    void OnDestroy()
    {
        cancellationTokenSource.Cancel();
        cancellationTokenSource.Dispose();
    }
}

// Custom exception for network operations
public class NetworkException : Exception
{
    public NetworkException(string message) : base(message) { }
}

// Game data class
public class GameData
{
    public string PlayerName { get; set; }
    public int Level { get; set; }
    public Dictionary<string, object> Settings { get; set; } = new Dictionary<string, object>();
}
```

### Thread-Safe Collections and Concurrency
```csharp
// Thread-safe event system for Unity
public class ThreadSafeEventSystem : MonoBehaviour
{
    private readonly ConcurrentQueue<System.Action> mainThreadActions = new ConcurrentQueue<System.Action>();
    private readonly ConcurrentDictionary<string, List<System.Action<object>>> eventHandlers = 
        new ConcurrentDictionary<string, List<System.Action<object>>>();
    
    // Singleton pattern for global access
    public static ThreadSafeEventSystem Instance { get; private set; }
    
    void Awake()
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
    
    void Update()
    {
        // Process queued main thread actions
        while (mainThreadActions.TryDequeue(out var action))
        {
            try
            {
                action?.Invoke();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error executing main thread action: {ex}");
            }
        }
    }
    
    // Thread-safe event subscription
    public void Subscribe(string eventName, System.Action<object> handler)
    {
        eventHandlers.AddOrUpdate(eventName, 
            new List<System.Action<object>> { handler },
            (key, existingList) =>
            {
                lock (existingList)
                {
                    existingList.Add(handler);
                    return existingList;
                }
            });
    }
    
    // Thread-safe event publishing
    public void Publish(string eventName, object data = null)
    {
        if (eventHandlers.TryGetValue(eventName, out var handlers))
        {
            // Execute on main thread if called from background thread
            if (Thread.CurrentThread.ManagedThreadId != 1)
            {
                mainThreadActions.Enqueue(() => InvokeHandlers(handlers, data));
            }
            else
            {
                InvokeHandlers(handlers, data);
            }
        }
    }
    
    private void InvokeHandlers(List<System.Action<object>> handlers, object data)
    {
        lock (handlers)
        {
            foreach (var handler in handlers)
            {
                try
                {
                    handler?.Invoke(data);
                }
                catch (Exception ex)
                {
                    Debug.LogError($"Error invoking event handler: {ex}");
                }
            }
        }
    }
}
```

### Async Unity Coroutine Bridge
```csharp
// Bridge between Unity coroutines and async/await
public static class AsyncCoroutineExtensions
{
    // Convert coroutine to Task
    public static Task ToTask(this Coroutine coroutine, MonoBehaviour monoBehaviour)
    {
        var tcs = new TaskCompletionSource<object>();
        
        monoBehaviour.StartCoroutine(WaitForCoroutine(coroutine, tcs));
        
        return tcs.Task;
    }
    
    private static IEnumerator WaitForCoroutine(Coroutine coroutine, TaskCompletionSource<object> tcs)
    {
        yield return coroutine;
        tcs.SetResult(null);
    }
    
    // Convert Task to coroutine
    public static Coroutine StartAsync(this MonoBehaviour monoBehaviour, Task task)
    {
        return monoBehaviour.StartCoroutine(WaitForTask(task));
    }
    
    private static IEnumerator WaitForTask(Task task)
    {
        while (!task.IsCompleted)
        {
            yield return null;
        }
        
        if (task.IsFaulted)
        {
            Debug.LogError($"Async task failed: {task.Exception}");
        }
    }
    
    // Async file loading example
    public static async Task<Texture2D> LoadTextureAsync(string path)
    {
        var request = UnityWebRequestTexture.GetTexture(path);
        
        // Convert UnityWebRequest to Task
        var tcs = new TaskCompletionSource<Texture2D>();
        
        request.SendWebRequest().completed += _ =>
        {
            if (request.result == UnityWebRequest.Result.Success)
            {
                tcs.SetResult(DownloadHandlerTexture.GetContent(request));
            }
            else
            {
                tcs.SetException(new Exception(request.error));
            }
            
            request.Dispose();
        };
        
        return await tcs.Task;
    }
}

// Usage example
public class AsyncTextureLoader : MonoBehaviour
{
    async void Start()
    {
        try
        {
            var texture = await AsyncCoroutineExtensions.LoadTextureAsync("file://path/to/texture.png");
            GetComponent<Renderer>().material.mainTexture = texture;
        }
        catch (Exception ex)
        {
            Debug.LogError($"Failed to load texture: {ex.Message}");
        }
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Intelligent Async Pattern Analysis
```csharp
// AI-powered async code analyzer
public class AsyncPatternAnalyzer
{
    [System.Serializable]
    public class AsyncAnalysisReport
    {
        public int totalAsyncMethods;
        public int potentialDeadlocks;
        public int improperAsyncPatterns;
        public List<string> optimizationSuggestions;
        public float asyncEfficiencyScore;
    }
    
    public AsyncAnalysisReport AnalyzeAsyncCode(string sourceCode)
    {
        var report = new AsyncAnalysisReport
        {
            optimizationSuggestions = new List<string>()
        };
        
        // AI analysis would analyze the source code here
        AnalyzeAsyncPatterns(sourceCode, report);
        GenerateOptimizationSuggestions(report);
        
        return report;
    }
    
    private void AnalyzeAsyncPatterns(string sourceCode, AsyncAnalysisReport report)
    {
        // Pattern detection logic (would use AI in real implementation)
        if (sourceCode.Contains(".Result") || sourceCode.Contains(".Wait()"))
        {
            report.potentialDeadlocks++;
            report.optimizationSuggestions.Add("Replace blocking calls with await");
        }
        
        if (sourceCode.Contains("async void") && !sourceCode.Contains("event"))
        {
            report.improperAsyncPatterns++;
            report.optimizationSuggestions.Add("Use async Task instead of async void");
        }
        
        // Calculate efficiency score
        int totalIssues = report.potentialDeadlocks + report.improperAsyncPatterns;
        report.asyncEfficiencyScore = Mathf.Clamp01(1f - (totalIssues / 10f));
    }
    
    private void GenerateOptimizationSuggestions(AsyncAnalysisReport report)
    {
        // AI-generated suggestions based on analysis
        if (report.potentialDeadlocks > 0)
        {
            report.optimizationSuggestions.Add("Consider using ConfigureAwait(false) for library code");
        }
        
        if (report.asyncEfficiencyScore < 0.7f)
        {
            report.optimizationSuggestions.Add("Review async/await usage patterns for optimization opportunities");
        }
    }
}
```

### Automated Async Refactoring
- **Deadlock Detection**: AI identifies potential async deadlock scenarios
- **Pattern Optimization**: Automated conversion of synchronous to asynchronous code
- **Performance Analysis**: AI analyzes async operation performance and suggests improvements
- **Concurrency Planning**: AI suggests optimal concurrency patterns for specific use cases

## 💡 Key Highlights

### Async/Await Best Practices
- **Always use async Task, never async void** (except for event handlers)
- **Use ConfigureAwait(false)** in library code to avoid deadlocks
- **Prefer Task.Run for CPU-bound work**, async/await for I/O-bound work
- **Use CancellationToken** for cooperative cancellation
- **Handle exceptions properly** with try-catch in async methods

### Unity-Specific Considerations
- **Main Thread Access**: Unity API calls must be on main thread
- **Coroutine Integration**: Bridge async/await with Unity coroutines when needed
- **Frame Rate Impact**: Avoid long-running synchronous operations
- **Memory Management**: Be careful with async operations and object lifetimes

### Common Async Pitfalls
```csharp
// ❌ Bad: Blocking on async code (can cause deadlocks)
public void BadExample()
{
    var result = SomeAsyncMethod().Result; // Don't do this!
}

// ✅ Good: Proper async all the way
public async Task GoodExample()
{
    var result = await SomeAsyncMethod();
}

// ❌ Bad: Fire and forget without error handling
public void BadFireAndForget()
{
    _ = SomeAsyncMethod(); // Exceptions will be lost
}

// ✅ Good: Proper fire and forget with error handling
public void GoodFireAndForget()
{
    _ = Task.Run(async () =>
    {
        try
        {
            await SomeAsyncMethod();
        }
        catch (Exception ex)
        {
            Debug.LogError($"Async operation failed: {ex}");
        }
    });
}
```

### AI-Enhanced Async Workflow
1. **Code Analysis**: AI continuously monitors async patterns for issues
2. **Performance Optimization**: AI suggests optimal async patterns for specific scenarios
3. **Error Prediction**: AI predicts potential async-related errors before runtime
4. **Automated Testing**: AI generates comprehensive async operation test cases

This advanced async programming knowledge enables developers to create highly responsive, scalable applications with proper error handling and optimal performance characteristics.