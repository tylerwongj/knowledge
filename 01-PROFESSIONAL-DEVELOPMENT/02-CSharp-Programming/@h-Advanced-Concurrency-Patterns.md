# @h-Advanced-Concurrency-Patterns - Mastering Parallel Programming in C#

## 🎯 Learning Objectives
- Master advanced concurrency patterns and thread-safe programming techniques
- Implement high-performance parallel algorithms using Task Parallel Library
- Create robust synchronization mechanisms and lock-free data structures
- Optimize concurrent code for Unity game development scenarios

## 🔧 Task Parallel Library (TPL) Mastery

### Advanced Task Patterns
```csharp
using System;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;

public class AdvancedTaskPatterns
{
    // Producer-Consumer Pattern with Backpressure
    public class BackpressureProducerConsumer<T>
    {
        private readonly SemaphoreSlim semaphore;
        private readonly ConcurrentQueue<T> queue;
        private readonly int maxCapacity;
        
        public BackpressureProducerConsumer(int maxCapacity = 100)
        {
            this.maxCapacity = maxCapacity;
            this.semaphore = new SemaphoreSlim(maxCapacity, maxCapacity);
            this.queue = new ConcurrentQueue<T>();
        }
        
        public async Task ProduceAsync(T item, CancellationToken cancellationToken = default)
        {
            await semaphore.WaitAsync(cancellationToken);
            queue.Enqueue(item);
        }
        
        public bool TryConsume(out T item)
        {
            if (queue.TryDequeue(out item))
            {
                semaphore.Release();
                return true;
            }
            return false;
        }
        
        public async Task<T> ConsumeAsync(CancellationToken cancellationToken = default)
        {
            while (!cancellationToken.IsCancellationRequested)
            {
                if (TryConsume(out T item))
                    return item;
                    
                await Task.Delay(1, cancellationToken);
            }
            throw new OperationCanceledException();
        }
    }
    
    // Parallel Pipeline Pattern
    public class ParallelPipeline<TInput, TOutput>
    {
        private readonly Func<TInput, TOutput> processor;
        private readonly int maxConcurrency;
        
        public ParallelPipeline(Func<TInput, TOutput> processor, int maxConcurrency = Environment.ProcessorCount)
        {
            this.processor = processor;
            this.maxConcurrency = maxConcurrency;
        }
        
        public async Task<IEnumerable<TOutput>> ProcessAsync(IEnumerable<TInput> inputs, 
            CancellationToken cancellationToken = default)
        {
            var semaphore = new SemaphoreSlim(maxConcurrency, maxConcurrency);
            var results = new ConcurrentBag<TOutput>();
            
            var tasks = inputs.Select(async input =>
            {
                await semaphore.WaitAsync(cancellationToken);
                try
                {
                    var result = await Task.Run(() => processor(input), cancellationToken);
                    results.Add(result);
                }
                finally
                {
                    semaphore.Release();
                }
            });
            
            await Task.WhenAll(tasks);
            return results;
        }
        
        public async IAsyncEnumerable<TOutput> ProcessStreamAsync(IAsyncEnumerable<TInput> inputs,
            [System.Runtime.CompilerServices.EnumeratorCancellation] CancellationToken cancellationToken = default)
        {
            var semaphore = new SemaphoreSlim(maxConcurrency, maxConcurrency);
            var channel = System.Threading.Channels.Channel.CreateUnbounded<TOutput>();
            
            var processingTask = Task.Run(async () =>
            {
                try
                {
                    await foreach (var input in inputs.WithCancellation(cancellationToken))
                    {
                        _ = Task.Run(async () =>
                        {
                            await semaphore.WaitAsync(cancellationToken);
                            try
                            {
                                var result = processor(input);
                                await channel.Writer.WriteAsync(result, cancellationToken);
                            }
                            finally
                            {
                                semaphore.Release();
                            }
                        }, cancellationToken);
                    }
                }
                finally
                {
                    channel.Writer.Complete();
                }
            }, cancellationToken);
            
            await foreach (var result in channel.Reader.ReadAllAsync(cancellationToken))
            {
                yield return result;
            }
            
            await processingTask;
        }
    }
    
    // Async Coordinator for Complex Workflows
    public class AsyncCoordinator
    {
        private readonly Dictionary<string, TaskCompletionSource<object>> completionSources;
        private readonly object lockObj = new object();
        
        public AsyncCoordinator()
        {
            completionSources = new Dictionary<string, TaskCompletionSource<object>>();
        }
        
        public Task WaitForSignalAsync(string signalName, CancellationToken cancellationToken = default)
        {
            TaskCompletionSource<object> tcs;
            
            lock (lockObj)
            {
                if (!completionSources.TryGetValue(signalName, out tcs))
                {
                    tcs = new TaskCompletionSource<object>();
                    completionSources[signalName] = tcs;
                }
            }
            
            cancellationToken.Register(() => tcs.TrySetCanceled());
            return tcs.Task;
        }
        
        public void SignalCompletion(string signalName, object result = null)
        {
            TaskCompletionSource<object> tcs;
            
            lock (lockObj)
            {
                if (completionSources.TryGetValue(signalName, out tcs))
                {
                    completionSources.Remove(signalName);
                }
            }
            
            tcs?.TrySetResult(result);
        }
        
        public void SignalFailure(string signalName, Exception exception)
        {
            TaskCompletionSource<object> tcs;
            
            lock (lockObj)
            {
                if (completionSources.TryGetValue(signalName, out tcs))
                {
                    completionSources.Remove(signalName);
                }
            }
            
            tcs?.TrySetException(exception);
        }
        
        public async Task<T[]> WaitForAllAsync<T>(params (string name, Func<Task<T>> factory)[] tasks)
        {
            var runningTasks = tasks.Select(async task =>
            {
                try
                {
                    return await task.factory();
                }
                catch (Exception ex)
                {
                    SignalFailure(task.name, ex);
                    throw;
                }
            });
            
            return await Task.WhenAll(runningTasks);
        }
    }
}
```

### Lock-Free Data Structures
```csharp
using System;
using System.Threading;
using System.Runtime.CompilerServices;

// Lock-free Stack implementation
public class LockFreeStack<T> where T : class
{
    private volatile Node head;
    
    private class Node
    {
        public readonly T Data;
        public volatile Node Next;
        
        public Node(T data)
        {
            Data = data;
        }
    }
    
    public void Push(T item)
    {
        var newNode = new Node(item);
        
        do
        {
            newNode.Next = head;
        } while (Interlocked.CompareExchange(ref head, newNode, newNode.Next) != newNode.Next);
    }
    
    public bool TryPop(out T result)
    {
        Node currentHead;
        
        do
        {
            currentHead = head;
            if (currentHead == null)
            {
                result = null;
                return false;
            }
        } while (Interlocked.CompareExchange(ref head, currentHead.Next, currentHead) != currentHead);
        
        result = currentHead.Data;
        return true;
    }
    
    public bool IsEmpty => head == null;
}

// Lock-free Queue with hazard pointers
public class LockFreeQueue<T> where T : class
{
    private volatile Node head;
    private volatile Node tail;
    
    private class Node
    {
        public volatile T Data;
        public volatile Node Next;
        
        public Node(T data = null)
        {
            Data = data;
        }
    }
    
    public LockFreeQueue()
    {
        var dummy = new Node();
        head = tail = dummy;
    }
    
    public void Enqueue(T item)
    {
        var newNode = new Node(item);
        
        while (true)
        {
            var currentTail = tail;
            var tailNext = currentTail.Next;
            
            if (currentTail == tail) // Tail hasn't changed
            {
                if (tailNext == null)
                {
                    // Try to link the new node
                    if (Interlocked.CompareExchange(ref currentTail.Next, newNode, null) == null)
                    {
                        // Try to move tail forward
                        Interlocked.CompareExchange(ref tail, newNode, currentTail);
                        break;
                    }
                }
                else
                {
                    // Try to move tail forward
                    Interlocked.CompareExchange(ref tail, tailNext, currentTail);
                }
            }
        }
    }
    
    public bool TryDequeue(out T result)
    {
        while (true)
        {
            var currentHead = head;
            var currentTail = tail;
            var headNext = currentHead.Next;
            
            if (currentHead == head) // Head hasn't changed
            {
                if (currentHead == currentTail)
                {
                    if (headNext == null)
                    {
                        result = null;
                        return false; // Queue is empty
                    }
                    
                    // Try to move tail forward
                    Interlocked.CompareExchange(ref tail, headNext, currentTail);
                }
                else
                {
                    if (headNext == null)
                        continue; // Another thread is in the process of updating
                        
                    result = headNext.Data;
                    
                    // Try to move head forward
                    if (Interlocked.CompareExchange(ref head, headNext, currentHead) == currentHead)
                    {
                        return true;
                    }
                }
            }
        }
    }
    
    public bool IsEmpty => head.Next == null;
}

// High-performance object pool
public class LockFreeObjectPool<T> where T : class, new()
{
    private readonly LockFreeStack<T> objects;
    private readonly Func<T> objectFactory;
    private volatile int currentCount;
    private readonly int maxSize;
    
    public LockFreeObjectPool(int maxSize = 100, Func<T> factory = null)
    {
        this.maxSize = maxSize;
        this.objects = new LockFreeStack<T>();
        this.objectFactory = factory ?? (() => new T());
    }
    
    public T Rent()
    {
        if (objects.TryPop(out T item))
        {
            Interlocked.Decrement(ref currentCount);
            return item;
        }
        
        return objectFactory();
    }
    
    public void Return(T item)
    {
        if (item == null) return;
        
        if (currentCount < maxSize)
        {
            objects.Push(item);
            Interlocked.Increment(ref currentCount);
        }
        // If pool is full, let GC handle the object
    }
    
    public int Count => currentCount;
}
```

## 🎮 Unity-Specific Concurrency Patterns

### Main Thread Dispatcher
```csharp
using UnityEngine;
using System;
using System.Collections.Concurrent;
using System.Threading;
using System.Threading.Tasks;

public class MainThreadDispatcher : MonoBehaviour
{
    private static MainThreadDispatcher instance;
    private readonly ConcurrentQueue<Action> actionQueue = new ConcurrentQueue<Action>();
    private readonly ConcurrentQueue<(TaskCompletionSource<object>, Func<object>)> functionQueue = 
        new ConcurrentQueue<(TaskCompletionSource<object>, Func<object>)>();
    
    public static MainThreadDispatcher Instance
    {
        get
        {
            if (instance == null)
            {
                var go = new GameObject("MainThreadDispatcher");
                instance = go.AddComponent<MainThreadDispatcher>();
                DontDestroyOnLoad(go);
            }
            return instance;
        }
    }
    
    private void Awake()
    {
        if (instance == null)
        {
            instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else if (instance != this)
        {
            Destroy(gameObject);
        }
    }
    
    private void Update()
    {
        // Execute queued actions
        while (actionQueue.TryDequeue(out Action action))
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
        
        // Execute queued functions
        while (functionQueue.TryDequeue(out var item))
        {
            try
            {
                var result = item.Item2?.Invoke();
                item.Item1.TrySetResult(result);
            }
            catch (Exception ex)
            {
                item.Item1.TrySetException(ex);
            }
        }
    }
    
    public static void Enqueue(Action action)
    {
        if (action == null) return;
        
        if (Thread.CurrentThread.ManagedThreadId == 1) // Already on main thread
        {
            action();
        }
        else
        {
            Instance.actionQueue.Enqueue(action);
        }
    }
    
    public static Task<T> EnqueueAsync<T>(Func<T> function)
    {
        if (function == null)
            return Task.FromResult(default(T));
            
        if (Thread.CurrentThread.ManagedThreadId == 1) // Already on main thread
        {
            try
            {
                return Task.FromResult(function());
            }
            catch (Exception ex)
            {
                return Task.FromException<T>(ex);
            }
        }
        
        var tcs = new TaskCompletionSource<object>();
        Instance.functionQueue.Enqueue((tcs, () => function()));
        
        return tcs.Task.ContinueWith(task => (T)task.Result, TaskContinuationOptions.ExecuteSynchronously);
    }
    
    public static Task EnqueueAsync(Action action)
    {
        return EnqueueAsync(() =>
        {
            action();
            return (object)null;
        });
    }
}

// Unity-specific async utilities
public static class UnityAsyncExtensions
{
    public static async Task<T> ConfigureAwaitFalse<T>(this Task<T> task)
    {
        return await task.ConfigureAwait(false);
    }
    
    public static async Task ConfigureAwaitFalse(this Task task)
    {
        await task.ConfigureAwait(false);
    }
    
    public static Task SwitchToMainThread()
    {
        return MainThreadDispatcher.EnqueueAsync(() => { });
    }
    
    public static Task<T> SwitchToMainThread<T>(Func<T> function)
    {
        return MainThreadDispatcher.EnqueueAsync(function);
    }
    
    public static async Task SwitchToThreadPool()
    {
        await Task.Yield();
    }
    
    // Custom awaitable for Unity's Update loop
    public struct NextFrameAwaitable : System.Runtime.CompilerServices.INotifyCompletion
    {
        public bool IsCompleted => false;
        
        public NextFrameAwaitable GetAwaiter() => this;
        
        public void GetResult() { }
        
        public void OnCompleted(Action continuation)
        {
            MainThreadDispatcher.Enqueue(() =>
            {
                // Wait one frame, then continue
                MainThreadDispatcher.Instance.StartCoroutine(WaitOneFrame(continuation));
            });
        }
        
        private static System.Collections.IEnumerator WaitOneFrame(Action continuation)
        {
            yield return null;
            continuation();
        }
    }
    
    public static NextFrameAwaitable NextFrame() => new NextFrameAwaitable();
}
```

### Parallel Processing for Unity
```csharp
using UnityEngine;
using System;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Linq;

public class UnityParallelProcessor : MonoBehaviour
{
    [Header("Processing Settings")]
    public int maxConcurrentTasks = 4;
    public bool useTimeSlicing = true;
    public float maxProcessingTimePerFrame = 0.016f; // 16ms
    
    private readonly Queue<Func<Task>> taskQueue = new Queue<Func<Task>>();
    private int activeTasks = 0;
    
    public static UnityParallelProcessor Instance { get; private set; }
    
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
    
    private void Update()
    {
        if (useTimeSlicing)
        {
            ProcessQueueTimeSliced();
        }
        else
        {
            ProcessQueue();
        }
    }
    
    private void ProcessQueue()
    {
        while (taskQueue.Count > 0 && activeTasks < maxConcurrentTasks)
        {
            var taskFactory = taskQueue.Dequeue();
            ProcessTaskAsync(taskFactory);
        }
    }
    
    private void ProcessQueueTimeSliced()
    {
        var startTime = Time.realtimeSinceStartup;
        
        while (taskQueue.Count > 0 && 
               activeTasks < maxConcurrentTasks && 
               (Time.realtimeSinceStartup - startTime) < maxProcessingTimePerFrame)
        {
            var taskFactory = taskQueue.Dequeue();
            ProcessTaskAsync(taskFactory);
        }
    }
    
    private async void ProcessTaskAsync(Func<Task> taskFactory)
    {
        activeTasks++;
        
        try
        {
            await taskFactory().ConfigureAwaitFalse();
        }
        catch (Exception ex)
        {
            Debug.LogError($"Parallel task failed: {ex}");
        }
        finally
        {
            activeTasks--;
        }
    }
    
    public void QueueTask(Func<Task> taskFactory)
    {
        taskQueue.Enqueue(taskFactory);
    }
    
    public Task<T> QueueTask<T>(Func<Task<T>> taskFactory)
    {
        var tcs = new TaskCompletionSource<T>();
        
        QueueTask(async () =>
        {
            try
            {
                var result = await taskFactory();
                tcs.SetResult(result);
            }
            catch (Exception ex)
            {
                tcs.SetException(ex);
            }
        });
        
        return tcs.Task;
    }
    
    // Parallel processing for collections
    public async Task ProcessParallelAsync<T>(IEnumerable<T> items, Func<T, Task> processor, 
        int? maxConcurrency = null)
    {
        var concurrency = maxConcurrency ?? maxConcurrentTasks;
        var semaphore = new System.Threading.SemaphoreSlim(concurrency, concurrency);
        
        var tasks = items.Select(async item =>
        {
            await semaphore.WaitAsync();
            try
            {
                await processor(item).ConfigureAwaitFalse();
            }
            finally
            {
                semaphore.Release();
            }
        });
        
        await Task.WhenAll(tasks).ConfigureAwaitFalse();
    }
    
    public async Task<IEnumerable<TResult>> ProcessParallelAsync<T, TResult>(
        IEnumerable<T> items, 
        Func<T, Task<TResult>> processor, 
        int? maxConcurrency = null)
    {
        var concurrency = maxConcurrency ?? maxConcurrentTasks;
        var semaphore = new System.Threading.SemaphoreSlim(concurrency, concurrency);
        var results = new System.Collections.Concurrent.ConcurrentBag<TResult>();
        
        var tasks = items.Select(async item =>
        {
            await semaphore.WaitAsync();
            try
            {
                var result = await processor(item).ConfigureAwaitFalse();
                results.Add(result);
            }
            finally
            {
                semaphore.Release();
            }
        });
        
        await Task.WhenAll(tasks).ConfigureAwaitFalse();
        return results;
    }
    
    // Batch processing for large datasets
    public async Task ProcessInBatchesAsync<T>(IEnumerable<T> items, 
        Func<IEnumerable<T>, Task> batchProcessor, 
        int batchSize = 100)
    {
        var batch = new List<T>(batchSize);
        
        foreach (var item in items)
        {
            batch.Add(item);
            
            if (batch.Count >= batchSize)
            {
                await batchProcessor(batch).ConfigureAwaitFalse();
                batch.Clear();
                
                // Allow other tasks to run
                await UnityAsyncExtensions.NextFrame();
            }
        }
        
        // Process remaining items
        if (batch.Count > 0)
        {
            await batchProcessor(batch).ConfigureAwaitFalse();
        }
    }
}

// Example usage for game-specific scenarios
public class GameConcurrencyExamples : MonoBehaviour
{
    // Parallel pathfinding for multiple units
    public async Task<Vector3[]> CalculatePathsAsync(Vector3[] starts, Vector3[] destinations)
    {
        var paths = new Vector3[starts.Length];
        
        await UnityParallelProcessor.Instance.ProcessParallelAsync(
            Enumerable.Range(0, starts.Length),
            async index =>
            {
                // Simulate pathfinding calculation
                await Task.Delay(UnityEngine.Random.Range(10, 50));
                paths[index] = Vector3.Lerp(starts[index], destinations[index], 0.5f);
            }
        );
        
        return paths;
    }
    
    // Parallel asset loading
    public async Task<Texture2D[]> LoadTexturesAsync(string[] assetPaths)
    {
        var results = await UnityParallelProcessor.Instance.ProcessParallelAsync(
            assetPaths,
            async path =>
            {
                // Switch to main thread for Unity API calls
                return await UnityAsyncExtensions.SwitchToMainThread(() =>
                {
                    return Resources.Load<Texture2D>(path);
                });
            }
        );
        
        return results.ToArray();
    }
    
    // Parallel physics calculations
    public async Task SimulatePhysicsAsync(Rigidbody[] rigidbodies, float deltaTime)
    {
        await UnityParallelProcessor.Instance.ProcessParallelAsync(
            rigidbodies,
            async rb =>
            {
                if (rb != null)
                {
                    // Perform physics calculations on background thread
                    await Task.Run(() =>
                    {
                        // Simulate physics step
                        var velocity = rb.velocity;
                        var gravity = Physics.gravity * deltaTime;
                        var newVelocity = velocity + gravity;
                        
                        // Apply back on main thread
                        MainThreadDispatcher.Enqueue(() =>
                        {
                            if (rb != null)
                                rb.velocity = newVelocity;
                        });
                    });
                }
            }
        );
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Concurrent Algorithm Generation
- **Parallel Algorithm Design**: AI-generated parallel processing algorithms for specific use cases
- **Lock-Free Structure Creation**: Automated generation of lock-free data structures
- **Performance Pattern Analysis**: AI analysis of concurrency patterns for optimization

### Deadlock Detection and Prevention
- **Static Analysis**: AI-powered detection of potential deadlock scenarios
- **Dynamic Monitoring**: Real-time analysis of thread interactions and bottlenecks
- **Optimization Suggestions**: Automated recommendations for improving concurrent code

### Threading Strategy Optimization
- **Workload Distribution**: AI-optimized task distribution across available cores
- **Resource Management**: Intelligent allocation of computational resources
- **Platform-Specific Tuning**: Automated optimization for different hardware configurations

## 💡 Key Highlights

- **Master Advanced TPL Patterns** including producer-consumer, pipelines, and coordinators
- **Implement Lock-Free Data Structures** for maximum performance and scalability
- **Create Unity-Specific Solutions** for main thread synchronization and parallel processing
- **Build Robust Error Handling** for complex concurrent scenarios
- **Optimize Memory Usage** with object pools and efficient data structures
- **Leverage AI Integration** for algorithm generation and performance optimization
- **Focus on Thread Safety** while maintaining high performance in game environments
- **Implement Backpressure Mechanisms** to prevent system overload in producer-consumer scenarios