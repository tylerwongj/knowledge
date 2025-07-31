# @38-Debugging-Helper-Tools

## 🎯 Core Concept
Automated debugging tools and helpers for efficient game development and troubleshooting.

## 🔧 Implementation

### Debug Helper Framework
```csharp
using UnityEngine;
using System.Collections.Generic;
using System.Reflection;

public class DebugHelper : MonoBehaviour
{
    public static DebugHelper Instance;
    
    [Header("Debug Settings")]
    public bool enableDebugMode = true;
    public bool showDebugUI = true;
    public bool enableConsoleCommands = true;
    public KeyCode debugToggleKey = KeyCode.F1;
    
    [Header("Visual Debug")]
    public bool showFPS = true;
    public bool showMemoryUsage = true;
    public bool showSystemInfo = false;
    
    private bool debugUIVisible = false;
    private Dictionary<string, System.Action<string[]>> debugCommands;
    private float fps = 0f;
    private List<string> consoleHistory;
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeDebugHelper();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void InitializeDebugHelper()
    {
        debugCommands = new Dictionary<string, System.Action<string[]>>();
        consoleHistory = new List<string>();
        
        RegisterDefaultCommands();
        
        // Only enable in development builds
        if (!Debug.isDebugBuild)
        {
            enableDebugMode = false;
        }
    }
    
    void RegisterDefaultCommands()
    {
        RegisterCommand("help", ShowHelp);
        RegisterCommand("fps", ToggleFPS);
        RegisterCommand("memory", ShowMemoryInfo);
        RegisterCommand("scene", LoadScene);
        RegisterCommand("time", SetTimeScale);
        RegisterCommand("god", ToggleGodMode);
        RegisterCommand("teleport", TeleportPlayer);
        RegisterCommand("spawn", SpawnObject);
        RegisterCommand("clear", ClearConsole);
        RegisterCommand("quit", QuitGame);
    }
    
    public void RegisterCommand(string command, System.Action<string[]> action)
    {
        debugCommands[command.ToLower()] = action;
    }
    
    void Update()
    {
        if (!enableDebugMode) return;
        
        // Toggle debug UI
        if (Input.GetKeyDown(debugToggleKey))
        {
            debugUIVisible = !debugUIVisible;
        }
        
        // Update FPS
        if (showFPS)
        {
            fps = 1f / Time.smoothDeltaTime;
        }
        
        // Handle console input
        if (enableConsoleCommands)
        {
            HandleConsoleInput();
        }
    }
    
    void HandleConsoleInput()
    {
        // This would typically be handled by a proper console UI
        // For demonstration, we'll use keyboard shortcuts
        
        if (Input.GetKeyDown(KeyCode.F2))
        {
            ExecuteCommand("fps");
        }
        else if (Input.GetKeyDown(KeyCode.F3))
        {
            ExecuteCommand("memory");
        }
        else if (Input.GetKeyDown(KeyCode.F4))
        {
            ExecuteCommand("time 2");
        }
        else if (Input.GetKeyDown(KeyCode.F5))
        {
            ExecuteCommand("time 1");
        }
    }
    
    public void ExecuteCommand(string commandLine)
    {
        if (string.IsNullOrEmpty(commandLine)) return;
        
        consoleHistory.Add(commandLine);
        
        string[] parts = commandLine.ToLower().Split(' ');
        string command = parts[0];
        string[] args = new string[parts.Length - 1];
        System.Array.Copy(parts, 1, args, 0, args.Length);
        
        if (debugCommands.ContainsKey(command))
        {
            try
            {
                debugCommands[command](args);
                Debug.Log($"Executed command: {commandLine}");
            }
            catch (System.Exception e)
            {
                Debug.LogError($"Command execution failed: {e.Message}");
            }
        }
        else
        {
            Debug.LogWarning($"Unknown command: {command}");
        }
    }
    
    // Default Commands
    void ShowHelp(string[] args)
    {
        string helpText = "Available Commands:\n";
        foreach (var command in debugCommands.Keys)
        {
            helpText += $"- {command}\n";
        }
        Debug.Log(helpText);
    }
    
    void ToggleFPS(string[] args)
    {
        showFPS = !showFPS;
        Debug.Log($"FPS display: {(showFPS ? "ON" : "OFF")}");
    }
    
    void ShowMemoryInfo(string[] args)
    {
        long totalMemory = System.GC.GetTotalMemory(false);
        long allocatedMemory = UnityEngine.Profiling.Profiler.GetTotalAllocatedMemory(false);
        
        Debug.Log($"Total Memory: {totalMemory / (1024 * 1024)}MB");
        Debug.Log($"Allocated Memory: {allocatedMemory / (1024 * 1024)}MB");
    }
    
    void LoadScene(string[] args)
    {
        if (args.Length > 0)
        {
            UnityEngine.SceneManagement.SceneManager.LoadScene(args[0]);
        }
        else
        {
            Debug.LogWarning("Usage: scene <sceneName>");
        }
    }
    
    void SetTimeScale(string[] args)
    {
        if (args.Length > 0 && float.TryParse(args[0], out float timeScale))
        {
            Time.timeScale = timeScale;
            Debug.Log($"Time scale set to: {timeScale}");
        }
        else
        {
            Debug.LogWarning("Usage: time <scale>");
        }
    }
    
    void ToggleGodMode(string[] args)
    {
        // Find player and toggle invincibility
        GameObject player = GameObject.FindGameObjectWithTag("Player");
        if (player != null)
        {
            // This would depend on your player implementation
            Debug.Log("God mode toggled");
        }
    }
    
    void TeleportPlayer(string[] args)
    {
        if (args.Length >= 3)
        {
            if (float.TryParse(args[0], out float x) && 
                float.TryParse(args[1], out float y) && 
                float.TryParse(args[2], out float z))
            {
                GameObject player = GameObject.FindGameObjectWithTag("Player");
                if (player != null)
                {
                    player.transform.position = new Vector3(x, y, z);
                    Debug.Log($"Player teleported to ({x}, {y}, {z})");
                }
            }
        }
        else
        {
            Debug.LogWarning("Usage: teleport <x> <y> <z>");
        }
    }
    
    void SpawnObject(string[] args)
    {
        if (args.Length > 0)
        {
            GameObject prefab = Resources.Load<GameObject>(args[0]);
            if (prefab != null)
            {
                Vector3 spawnPos = Camera.main.transform.position + Camera.main.transform.forward * 5f;
                Instantiate(prefab, spawnPos, Quaternion.identity);
                Debug.Log($"Spawned: {args[0]}");
            }
            else
            {
                Debug.LogWarning($"Prefab not found: {args[0]}");
            }
        }
        else
        {
            Debug.LogWarning("Usage: spawn <prefabName>");
        }
    }
    
    void ClearConsole(string[] args)
    {
        consoleHistory.Clear();
        Debug.Log("Console cleared");
    }
    
    void QuitGame(string[] args)
    {
        Debug.Log("Quitting game...");
        Application.Quit();
    }
    
    void OnGUI()
    {
        if (!enableDebugMode || !debugUIVisible) return;
        
        GUI.skin.label.fontSize = 16;
        
        // FPS Display
        if (showFPS)
        {
            GUI.Label(new Rect(10, 10, 200, 30), $"FPS: {fps:F1}");
        }
        
        // Memory Display
        if (showMemoryUsage)
        {
            long memory = System.GC.GetTotalMemory(false) / (1024 * 1024);
            GUI.Label(new Rect(10, 40, 200, 30), $"Memory: {memory}MB");
        }
        
        // System Info Display
        if (showSystemInfo)
        {
            GUI.Label(new Rect(10, 70, 300, 30), $"Platform: {Application.platform}");
            GUI.Label(new Rect(10, 100, 300, 30), $"Unity: {Application.unityVersion}");
        }
        
        // Command History
        if (consoleHistory.Count > 0)
        {
            GUI.Box(new Rect(10, Screen.height - 200, 400, 150), "Console History");
            
            int startIndex = Mathf.Max(0, consoleHistory.Count - 5);
            for (int i = startIndex; i < consoleHistory.Count; i++)
            {
                GUI.Label(new Rect(15, Screen.height - 185 + (i - startIndex) * 20, 390, 20), 
                    $"> {consoleHistory[i]}");
            }
        }
    }
}

// Visual debug tools
public static class DebugDraw
{
    public static void DrawWireSphere(Vector3 center, float radius, Color color, float duration = 0f)
    {
        DrawWireCircle(center, radius, Vector3.up, color, duration);
        DrawWireCircle(center, radius, Vector3.right, color, duration);
        DrawWireCircle(center, radius, Vector3.forward, color, duration);
    }
    
    public static void DrawWireCircle(Vector3 center, float radius, Vector3 normal, Color color, float duration = 0f)
    {
        int segments = 32;
        float angleStep = 360f / segments;
        
        Vector3 perpendicular = Vector3.Cross(normal, Vector3.up);
        if (perpendicular.magnitude < 0.1f)
        {
            perpendicular = Vector3.Cross(normal, Vector3.right);
        }
        perpendicular.Normalize();
        
        Vector3 lastPoint = center + perpendicular * radius;
        
        for (int i = 1; i <= segments; i++)
        {
            float angle = i * angleStep * Mathf.Deg2Rad;
            Vector3 currentPoint = center + (Quaternion.AngleAxis(angle * Mathf.Rad2Deg, normal) * perpendicular) * radius;
            
            Debug.DrawLine(lastPoint, currentPoint, color, duration);
            lastPoint = currentPoint;
        }
    }
    
    public static void DrawArrow(Vector3 start, Vector3 end, Color color, float arrowSize = 0.5f, float duration = 0f)
    {
        Debug.DrawLine(start, end, color, duration);
        
        Vector3 direction = (end - start).normalized;
        Vector3 right = Vector3.Cross(direction, Vector3.up).normalized;
        Vector3 up = Vector3.Cross(right, direction).normalized;
        
        Vector3 arrowHead1 = end - direction * arrowSize + right * arrowSize * 0.5f;
        Vector3 arrowHead2 = end - direction * arrowSize - right * arrowSize * 0.5f;
        Vector3 arrowHead3 = end - direction * arrowSize + up * arrowSize * 0.5f;
        Vector3 arrowHead4 = end - direction * arrowSize - up * arrowSize * 0.5f;
        
        Debug.DrawLine(end, arrowHead1, color, duration);
        Debug.DrawLine(end, arrowHead2, color, duration);
        Debug.DrawLine(end, arrowHead3, color, duration);
        Debug.DrawLine(end, arrowHead4, color, duration);
    }
    
    public static void DrawBounds(Bounds bounds, Color color, float duration = 0f)
    {
        Vector3 center = bounds.center;
        Vector3 size = bounds.size;
        
        // Draw bottom face
        Debug.DrawLine(center + new Vector3(-size.x, -size.y, -size.z) * 0.5f, 
                      center + new Vector3(size.x, -size.y, -size.z) * 0.5f, color, duration);
        Debug.DrawLine(center + new Vector3(size.x, -size.y, -size.z) * 0.5f, 
                      center + new Vector3(size.x, -size.y, size.z) * 0.5f, color, duration);
        Debug.DrawLine(center + new Vector3(size.x, -size.y, size.z) * 0.5f, 
                      center + new Vector3(-size.x, -size.y, size.z) * 0.5f, color, duration);
        Debug.DrawLine(center + new Vector3(-size.x, -size.y, size.z) * 0.5f, 
                      center + new Vector3(-size.x, -size.y, -size.z) * 0.5f, color, duration);
        
        // Draw top face
        Debug.DrawLine(center + new Vector3(-size.x, size.y, -size.z) * 0.5f, 
                      center + new Vector3(size.x, size.y, -size.z) * 0.5f, color, duration);
        Debug.DrawLine(center + new Vector3(size.x, size.y, -size.z) * 0.5f, 
                      center + new Vector3(size.x, size.y, size.z) * 0.5f, color, duration);
        Debug.DrawLine(center + new Vector3(size.x, size.y, size.z) * 0.5f, 
                      center + new Vector3(-size.x, size.y, size.z) * 0.5f, color, duration);
        Debug.DrawLine(center + new Vector3(-size.x, size.y, size.z) * 0.5f, 
                      center + new Vector3(-size.x, size.y, -size.z) * 0.5f, color, duration);
        
        // Draw vertical edges
        Debug.DrawLine(center + new Vector3(-size.x, -size.y, -size.z) * 0.5f, 
                      center + new Vector3(-size.x, size.y, -size.z) * 0.5f, color, duration);
        Debug.DrawLine(center + new Vector3(size.x, -size.y, -size.z) * 0.5f, 
                      center + new Vector3(size.x, size.y, -size.z) * 0.5f, color, duration);
        Debug.DrawLine(center + new Vector3(size.x, -size.y, size.z) * 0.5f, 
                      center + new Vector3(size.x, size.y, size.z) * 0.5f, color, duration);
        Debug.DrawLine(center + new Vector3(-size.x, -size.y, size.z) * 0.5f, 
                      center + new Vector3(-size.x, size.y, size.z) * 0.5f, color, duration);
    }
}

// Component for debugging specific game objects
public class GameObjectDebugger : MonoBehaviour
{
    [Header("Debug Options")]
    public bool showBounds = false;
    public bool showVelocity = false;
    public bool showTransformInfo = false;
    public Color debugColor = Color.yellow;
    
    private Rigidbody rb;
    private Collider col;
    
    void Start()
    {
        rb = GetComponent<Rigidbody>();
        col = GetComponent<Collider>();
    }
    
    void Update()
    {
        if (showVelocity && rb != null)
        {
            DebugDraw.DrawArrow(transform.position, transform.position + rb.velocity, debugColor);
        }
    }
    
    void OnDrawGizmos()
    {
        if (showBounds && col != null)
        {
            Gizmos.color = debugColor;
            Gizmos.DrawWireCube(col.bounds.center, col.bounds.size);
        }
    }
    
    void OnGUI()
    {
        if (showTransformInfo)
        {
            Vector3 screenPos = Camera.main.WorldToScreenPoint(transform.position);
            
            if (screenPos.z > 0)
            {
                GUI.Label(new Rect(screenPos.x, Screen.height - screenPos.y, 200, 60),
                    $"Pos: {transform.position}\nRot: {transform.eulerAngles}\nScale: {transform.localScale}");
            }
        }
    }
}
```

## 🚀 AI/LLM Integration
- Generate debug commands based on game systems
- Automatically create debugging visualizations
- Provide intelligent debugging suggestions

## 💡 Key Benefits
- Comprehensive debugging toolkit
- Runtime command console
- Visual debugging helpers