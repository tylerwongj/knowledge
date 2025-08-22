# @j-Unity-AI-Debugging-Code-Generation-Workflows

## 🎯 Learning Objectives

- Master AI-powered debugging techniques for Unity development
- Implement automated code generation workflows for Unity projects
- Create intelligent error analysis and resolution systems
- Develop AI-assisted testing and optimization pipelines

## 🔧 AI-Powered Unity Debugging

### Automated Error Analysis System

```csharp
using System;
using System.Collections.Generic;
using System.Text;
using System.Text.RegularExpressions;
using UnityEngine;
using System.IO;
using System.Diagnostics;

[System.Serializable]
public class ErrorAnalysisResult
{
    public string errorType;
    public string description;
    public string[] suggestedFixes;
    public string aiAnalysis;
    public float confidenceScore;
    public string codeContext;
}

public class AIDebuggingAssistant : MonoBehaviour
{
    [Header("AI Configuration")]
    [SerializeField] private string aiApiKey = "";
    [SerializeField] private bool enableAutoAnalysis = true;
    [SerializeField] private bool logDetailedAnalysis = true;
    
    [Header("Error Tracking")]
    [SerializeField] private int maxErrorHistory = 100;
    [SerializeField] private bool enableSmartFiltering = true;
    
    private List<ErrorAnalysisResult> errorHistory = new List<ErrorAnalysisResult>();
    private Dictionary<string, int> errorFrequency = new Dictionary<string, int>();
    private StringBuilder aiPromptBuilder = new StringBuilder();
    
    // Error pattern database for quick fixes
    private Dictionary<string, string[]> commonSolutions = new Dictionary<string, string[]>
    {
        ["NullReferenceException"] = new string[]
        {
            "Add null checks before accessing objects",
            "Initialize variables in Awake() or Start()",
            "Use ?. null-conditional operator",
            "Check if GameObject is destroyed before use"
        },
        ["IndexOutOfRangeException"] = new string[]
        {
            "Validate array/list bounds before access",
            "Use Count/Length property for bounds checking",
            "Consider using TryGetValue for dictionaries",
            "Add defensive programming checks"
        },
        ["MissingComponentException"] = new string[]
        {
            "Add RequireComponent attribute",
            "Use GetComponent with null check",
            "Ensure component exists before accessing",
            "Consider using TryGetComponent method"
        }
    };
    
    private void OnEnable()
    {
        Application.logMessageReceived += OnLogMessageReceived;
    }
    
    private void OnDisable()
    {
        Application.logMessageReceived -= OnLogMessageReceived;
    }
    
    private void OnLogMessageReceived(string logString, string stackTrace, LogType type)
    {
        if (type == LogType.Error || type == LogType.Exception)
        {
            if (enableAutoAnalysis)
            {
                StartCoroutine(AnalyzeErrorWithAI(logString, stackTrace));
            }
        }
    }
    
    private System.Collections.IEnumerator AnalyzeErrorWithAI(string errorMessage, string stackTrace)
    {
        try
        {
            // Extract error context
            var errorContext = ExtractErrorContext(errorMessage, stackTrace);
            
            // Check for common patterns first
            var quickFix = GetQuickFix(errorMessage);
            if (quickFix != null)
            {
                LogQuickFix(errorMessage, quickFix);
                yield break;
            }
            
            // Generate AI analysis prompt
            string prompt = GenerateDebuggingPrompt(errorMessage, stackTrace, errorContext);
            
            // Call AI service (placeholder for actual implementation)
            string aiResponse = yield return CallAIService(prompt);
            
            // Parse and store analysis
            var analysis = ParseAIResponse(aiResponse, errorMessage, stackTrace);
            StoreAnalysis(analysis);
            
            if (logDetailedAnalysis)
            {
                LogAIAnalysis(analysis);
            }
        }
        catch (Exception ex)
        {
            UnityEngine.Debug.LogError($"AI Debugging Assistant Error: {ex.Message}");
        }
    }
    
    private ErrorContext ExtractErrorContext(string errorMessage, string stackTrace)
    {
        var context = new ErrorContext();
        
        // Extract file and line number
        var fileMatch = Regex.Match(stackTrace, @"(.*\.cs):line (\d+)");
        if (fileMatch.Success)
        {
            context.fileName = Path.GetFileName(fileMatch.Groups[1].Value);
            context.lineNumber = int.Parse(fileMatch.Groups[2].Value);
            
            // Read surrounding code lines
            context.codeContext = GetCodeContext(fileMatch.Groups[1].Value, context.lineNumber);
        }
        
        // Extract method information
        var methodMatch = Regex.Match(stackTrace, @"at (.*?)\s*\(");
        if (methodMatch.Success)
        {
            context.methodName = methodMatch.Groups[1].Value;
        }
        
        // Determine error category
        context.errorCategory = CategorizeError(errorMessage);
        
        return context;
    }
    
    private string GetCodeContext(string filePath, int lineNumber, int contextLines = 5)
    {
        try
        {
            if (!File.Exists(filePath)) return "";
            
            var lines = File.ReadAllLines(filePath);
            int start = Math.Max(0, lineNumber - contextLines - 1);
            int end = Math.Min(lines.Length, lineNumber + contextLines);
            
            var contextBuilder = new StringBuilder();
            for (int i = start; i < end; i++)
            {
                string marker = (i == lineNumber - 1) ? ">>> " : "    ";
                contextBuilder.AppendLine($"{marker}{i + 1}: {lines[i]}");
            }
            
            return contextBuilder.ToString();
        }
        catch
        {
            return "";
        }
    }
    
    private string GenerateDebuggingPrompt(string errorMessage, string stackTrace, ErrorContext context)
    {
        aiPromptBuilder.Clear();
        
        aiPromptBuilder.AppendLine("# Unity C# Debugging Analysis Request");
        aiPromptBuilder.AppendLine();
        aiPromptBuilder.AppendLine("## Error Information");
        aiPromptBuilder.AppendLine($"**Error Message:** {errorMessage}");
        aiPromptBuilder.AppendLine($"**Error Category:** {context.errorCategory}");
        aiPromptBuilder.AppendLine($"**File:** {context.fileName}");
        aiPromptBuilder.AppendLine($"**Method:** {context.methodName}");
        aiPromptBuilder.AppendLine($"**Line:** {context.lineNumber}");
        aiPromptBuilder.AppendLine();
        
        aiPromptBuilder.AppendLine("## Code Context");
        aiPromptBuilder.AppendLine("```csharp");
        aiPromptBuilder.AppendLine(context.codeContext);
        aiPromptBuilder.AppendLine("```");
        aiPromptBuilder.AppendLine();
        
        aiPromptBuilder.AppendLine("## Stack Trace");
        aiPromptBuilder.AppendLine("```");
        aiPromptBuilder.AppendLine(stackTrace);
        aiPromptBuilder.AppendLine("```");
        aiPromptBuilder.AppendLine();
        
        aiPromptBuilder.AppendLine("## Analysis Request");
        aiPromptBuilder.AppendLine("Please provide:");
        aiPromptBuilder.AppendLine("1. **Root Cause Analysis**: What is causing this error?");
        aiPromptBuilder.AppendLine("2. **Immediate Fix**: Specific code changes to resolve the issue");
        aiPromptBuilder.AppendLine("3. **Prevention Strategy**: How to prevent similar errors");
        aiPromptBuilder.AppendLine("4. **Code Quality Improvements**: Suggestions for better practices");
        aiPromptBuilder.AppendLine("5. **Confidence Score**: Rate your analysis confidence (0-100)");
        aiPromptBuilder.AppendLine();
        
        aiPromptBuilder.AppendLine("Focus on Unity-specific patterns and best practices.");
        
        return aiPromptBuilder.ToString();
    }
    
    private System.Collections.IEnumerator CallAIService(string prompt)
    {
        // Placeholder for actual AI service integration
        // This would integrate with Claude, GPT-4, or other AI services
        
        yield return new WaitForSeconds(0.1f); // Simulate API call
        
        // Mock response for demonstration
        return @"
## Root Cause Analysis
The NullReferenceException indicates that a reference is null when trying to access its members.

## Immediate Fix
```csharp
if (targetObject != null)
{
    targetObject.SetActive(true);
}
```

## Prevention Strategy
- Always initialize references in Awake() or Start()
- Use null-conditional operators (?.)
- Add RequireComponent attributes for essential components

## Code Quality Improvements
- Implement defensive programming practices
- Add error handling and logging
- Use Unity's built-in null checks

## Confidence Score
85
";
    }
    
    private ErrorAnalysisResult ParseAIResponse(string response, string originalError, string stackTrace)
    {
        var analysis = new ErrorAnalysisResult
        {
            errorType = CategorizeError(originalError),
            description = originalError,
            aiAnalysis = response,
            codeContext = stackTrace,
            confidenceScore = ExtractConfidenceScore(response),
            suggestedFixes = ExtractSuggestedFixes(response)
        };
        
        return analysis;
    }
    
    private float ExtractConfidenceScore(string response)
    {
        var match = Regex.Match(response, @"Confidence Score.*?(\d+)", RegexOptions.IgnoreCase);
        if (match.Success && float.TryParse(match.Groups[1].Value, out float score))
        {
            return score / 100f;
        }
        return 0.5f; // Default confidence
    }
    
    private string[] ExtractSuggestedFixes(string response)
    {
        var fixes = new List<string>();
        
        // Extract code blocks
        var codeMatches = Regex.Matches(response, @"```csharp\n(.*?)\n```", RegexOptions.Singleline);
        foreach (Match match in codeMatches)
        {
            fixes.Add(match.Groups[1].Value.Trim());
        }
        
        // Extract bullet points
        var bulletMatches = Regex.Matches(response, @"^[-*]\s*(.+)$", RegexOptions.Multiline);
        foreach (Match match in bulletMatches)
        {
            fixes.Add(match.Groups[1].Value.Trim());
        }
        
        return fixes.ToArray();
    }
    
    private void LogAIAnalysis(ErrorAnalysisResult analysis)
    {
        UnityEngine.Debug.Log($"<color=cyan>AI Debugging Analysis</color>\n" +
                             $"<b>Error Type:</b> {analysis.errorType}\n" +
                             $"<b>Confidence:</b> {analysis.confidenceScore:P0}\n" +
                             $"<b>Suggested Fixes:</b>\n{string.Join("\n", analysis.suggestedFixes)}");
    }
}

[System.Serializable]
public class ErrorContext
{
    public string fileName;
    public int lineNumber;
    public string methodName;
    public string codeContext;
    public string errorCategory;
}

// Error categorization helper
public static class ErrorCategorizer
{
    private static readonly Dictionary<string, string> errorPatterns = new Dictionary<string, string>
    {
        ["NullReferenceException"] = "Null Reference",
        ["IndexOutOfRangeException"] = "Array/Collection Access",
        ["ArgumentException"] = "Invalid Arguments",
        ["InvalidOperationException"] = "Invalid State",
        ["MissingComponentException"] = "Component Access",
        ["UnityException"] = "Unity Framework",
        ["NotImplementedException"] = "Incomplete Implementation"
    };
    
    public static string CategorizeError(string errorMessage)
    {
        foreach (var pattern in errorPatterns)
        {
            if (errorMessage.Contains(pattern.Key))
            {
                return pattern.Value;
            }
        }
        return "Unknown";
    }
}
```

### Automated Code Generation System

```csharp
using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEngine;
using UnityEditor;

public class AICodeGenerator : EditorWindow
{
    [MenuItem("Tools/AI Code Generator")]
    public static void ShowWindow()
    {
        GetWindow<AICodeGenerator>("AI Code Generator");
    }
    
    [System.Serializable]
    public class CodeGenerationRequest
    {
        public string description;
        public CodeType codeType;
        public string targetNamespace;
        public string targetFolder;
        public bool includeComments;
        public bool followUnityConventions;
        public bool generateTests;
        public string[] additionalRequirements;
    }
    
    public enum CodeType
    {
        MonoBehaviour,
        ScriptableObject,
        System,
        Interface,
        StateMachine,
        Manager,
        Utility,
        Component,
        Editor
    }
    
    private CodeGenerationRequest currentRequest = new CodeGenerationRequest();
    private Vector2 scrollPosition;
    private string generatedCode = "";
    private bool isGenerating = false;
    
    private void OnGUI()
    {
        scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);
        
        GUILayout.Label("AI Code Generator", EditorStyles.boldLabel);
        GUILayout.Space(10);
        
        // Code generation parameters
        DrawCodeGenerationUI();
        
        GUILayout.Space(10);
        
        // Generation controls
        DrawGenerationControls();
        
        GUILayout.Space(10);
        
        // Generated code display
        DrawGeneratedCodeUI();
        
        EditorGUILayout.EndScrollView();
    }
    
    private void DrawCodeGenerationUI()
    {
        GUILayout.Label("Code Specification", EditorStyles.boldLabel);
        
        currentRequest.description = EditorGUILayout.TextArea(
            currentRequest.description,
            GUILayout.MinHeight(100)
        );
        
        currentRequest.codeType = (CodeType)EditorGUILayout.EnumPopup("Code Type", currentRequest.codeType);
        currentRequest.targetNamespace = EditorGUILayout.TextField("Namespace", currentRequest.targetNamespace);
        currentRequest.targetFolder = EditorGUILayout.TextField("Target Folder", currentRequest.targetFolder);
        
        GUILayout.Space(5);
        
        currentRequest.includeComments = EditorGUILayout.Toggle("Include Comments", currentRequest.includeComments);
        currentRequest.followUnityConventions = EditorGUILayout.Toggle("Unity Conventions", currentRequest.followUnityConventions);
        currentRequest.generateTests = EditorGUILayout.Toggle("Generate Tests", currentRequest.generateTests);
    }
    
    private void DrawGenerationControls()
    {
        GUILayout.Label("Generation Controls", EditorStyles.boldLabel);
        
        EditorGUILayout.BeginHorizontal();
        
        GUI.enabled = !isGenerating && !string.IsNullOrEmpty(currentRequest.description);
        if (GUILayout.Button("Generate Code", GUILayout.Height(30)))
        {
            GenerateCode();
        }
        
        GUI.enabled = !string.IsNullOrEmpty(generatedCode);
        if (GUILayout.Button("Save to File", GUILayout.Height(30)))
        {
            SaveGeneratedCode();
        }
        
        GUI.enabled = !string.IsNullOrEmpty(generatedCode);
        if (GUILayout.Button("Copy to Clipboard", GUILayout.Height(30)))
        {
            EditorGUIUtility.systemCopyBuffer = generatedCode;
        }
        
        GUI.enabled = true;
        
        EditorGUILayout.EndHorizontal();
        
        if (isGenerating)
        {
            EditorGUILayout.HelpBox("Generating code...", MessageType.Info);
        }
    }
    
    private void DrawGeneratedCodeUI()
    {
        if (!string.IsNullOrEmpty(generatedCode))
        {
            GUILayout.Label("Generated Code", EditorStyles.boldLabel);
            
            var style = new GUIStyle(EditorStyles.textArea)
            {
                font = EditorStyles.miniFont,
                fontSize = 12
            };
            
            generatedCode = EditorGUILayout.TextArea(generatedCode, style, GUILayout.MinHeight(300));
        }
    }
    
    private async void GenerateCode()
    {
        isGenerating = true;
        
        try
        {
            string prompt = BuildCodeGenerationPrompt();
            generatedCode = await CallAICodeGenerationService(prompt);
            
            // Post-process the generated code
            generatedCode = PostProcessGeneratedCode(generatedCode);
        }
        catch (Exception ex)
        {
            EditorUtility.DisplayDialog("Error", $"Code generation failed: {ex.Message}", "OK");
            generatedCode = "";
        }
        finally
        {
            isGenerating = false;
            Repaint();
        }
    }
    
    private string BuildCodeGenerationPrompt()
    {
        var promptBuilder = new StringBuilder();
        
        promptBuilder.AppendLine("# Unity C# Code Generation Request");
        promptBuilder.AppendLine();
        promptBuilder.AppendLine("## Requirements");
        promptBuilder.AppendLine($"**Description:** {currentRequest.description}");
        promptBuilder.AppendLine($"**Code Type:** {currentRequest.codeType}");
        promptBuilder.AppendLine($"**Namespace:** {currentRequest.targetNamespace}");
        promptBuilder.AppendLine();
        
        promptBuilder.AppendLine("## Code Standards");
        promptBuilder.AppendLine("- Follow Unity C# coding conventions");
        promptBuilder.AppendLine("- Use proper naming conventions (PascalCase for public, camelCase for private)");
        promptBuilder.AppendLine("- Include proper using statements");
        promptBuilder.AppendLine("- Add SerializeField attributes for Inspector exposure");
        promptBuilder.AppendLine("- Implement proper Unity lifecycle methods");
        promptBuilder.AppendLine();
        
        if (currentRequest.includeComments)
        {
            promptBuilder.AppendLine("## Documentation Requirements");
            promptBuilder.AppendLine("- Add XML documentation comments for public members");
            promptBuilder.AppendLine("- Include inline comments for complex logic");
            promptBuilder.AppendLine("- Add header comments explaining the class purpose");
            promptBuilder.AppendLine();
        }
        
        AppendCodeTypeSpecificRequirements(promptBuilder);
        
        promptBuilder.AppendLine("## Output Format");
        promptBuilder.AppendLine("Provide only the complete, ready-to-use C# code without additional explanations.");
        
        return promptBuilder.ToString();
    }
    
    private void AppendCodeTypeSpecificRequirements(StringBuilder promptBuilder)
    {
        promptBuilder.AppendLine("## Specific Requirements");
        
        switch (currentRequest.codeType)
        {
            case CodeType.MonoBehaviour:
                promptBuilder.AppendLine("- Inherit from MonoBehaviour");
                promptBuilder.AppendLine("- Include appropriate Unity lifecycle methods");
                promptBuilder.AppendLine("- Use SerializeField for inspector values");
                promptBuilder.AppendLine("- Consider performance in Update methods");
                break;
                
            case CodeType.ScriptableObject:
                promptBuilder.AppendLine("- Inherit from ScriptableObject");
                promptBuilder.AppendLine("- Include CreateAssetMenu attribute");
                promptBuilder.AppendLine("- Implement data validation where appropriate");
                break;
                
            case CodeType.System:
                promptBuilder.AppendLine("- Create a singleton or static system");
                promptBuilder.AppendLine("- Implement proper initialization and cleanup");
                promptBuilder.AppendLine("- Use events for loose coupling");
                break;
                
            case CodeType.Interface:
                promptBuilder.AppendLine("- Define clear interface contracts");
                promptBuilder.AppendLine("- Use appropriate naming (I prefix)");
                promptBuilder.AppendLine("- Include generic constraints if needed");
                break;
                
            case CodeType.StateMachine:
                promptBuilder.AppendLine("- Implement state pattern");
                promptBuilder.AppendLine("- Include state transition logic");
                promptBuilder.AppendLine("- Provide debugging capabilities");
                break;
        }
        
        promptBuilder.AppendLine();
    }
    
    private async System.Threading.Tasks.Task<string> CallAICodeGenerationService(string prompt)
    {
        // Placeholder for actual AI service integration
        await System.Threading.Tasks.Task.Delay(2000); // Simulate API call
        
        // Mock generated code based on request type
        return GenerateMockCode();
    }
    
    private string GenerateMockCode()
    {
        switch (currentRequest.codeType)
        {
            case CodeType.MonoBehaviour:
                return GenerateMockMonoBehaviour();
            case CodeType.ScriptableObject:
                return GenerateMockScriptableObject();
            default:
                return "// Generated code will appear here";
        }
    }
    
    private string GenerateMockMonoBehaviour()
    {
        return @"using UnityEngine;

namespace " + (string.IsNullOrEmpty(currentRequest.targetNamespace) ? "Game" : currentRequest.targetNamespace) + @"
{
    /// <summary>
    /// " + currentRequest.description + @"
    /// </summary>
    public class GeneratedController : MonoBehaviour
    {
        [Header(""Configuration"")]
        [SerializeField] private float speed = 5f;
        [SerializeField] private bool enableDebugMode = false;
        
        [Header(""References"")]
        [SerializeField] private Transform targetTransform;
        
        private Vector3 velocity;
        private bool isInitialized;
        
        /// <summary>
        /// Initialize the controller
        /// </summary>
        private void Awake()
        {
            ValidateReferences();
        }
        
        /// <summary>
        /// Start the controller behavior
        /// </summary>
        private void Start()
        {
            Initialize();
        }
        
        /// <summary>
        /// Update the controller behavior
        /// </summary>
        private void Update()
        {
            if (!isInitialized) return;
            
            UpdateBehavior();
        }
        
        /// <summary>
        /// Validate required references
        /// </summary>
        private void ValidateReferences()
        {
            if (targetTransform == null)
            {
                Debug.LogWarning(""Target transform not assigned"", this);
            }
        }
        
        /// <summary>
        /// Initialize the controller
        /// </summary>
        private void Initialize()
        {
            isInitialized = true;
            
            if (enableDebugMode)
            {
                Debug.Log(""Controller initialized"", this);
            }
        }
        
        /// <summary>
        /// Update the main behavior logic
        /// </summary>
        private void UpdateBehavior()
        {
            // Implement your behavior logic here
        }
        
        /// <summary>
        /// Clean up when destroyed
        /// </summary>
        private void OnDestroy()
        {
            // Cleanup logic here
        }
        
        #if UNITY_EDITOR
        /// <summary>
        /// Draw debug gizmos in the scene view
        /// </summary>
        private void OnDrawGizmosSelected()
        {
            if (enableDebugMode && targetTransform != null)
            {
                Gizmos.color = Color.yellow;
                Gizmos.DrawWireSphere(targetTransform.position, 1f);
            }
        }
        #endif
    }
}";
    }
    
    private string GenerateMockScriptableObject()
    {
        return @"using UnityEngine;

namespace " + (string.IsNullOrEmpty(currentRequest.targetNamespace) ? "Game.Data" : currentRequest.targetNamespace) + @"
{
    /// <summary>
    /// " + currentRequest.description + @"
    /// </summary>
    [CreateAssetMenu(fileName = ""New Data"", menuName = ""Game/Data/Generated Data"")]
    public class GeneratedData : ScriptableObject
    {
        [Header(""Basic Properties"")]
        [SerializeField] private string displayName = ""Generated Data"";
        [SerializeField, TextArea(3, 5)] private string description = """";
        
        [Header(""Numeric Values"")]
        [SerializeField] private float value = 1.0f;
        [SerializeField] private int count = 1;
        [SerializeField] private bool isEnabled = true;
        
        /// <summary>
        /// Display name for this data
        /// </summary>
        public string DisplayName => displayName;
        
        /// <summary>
        /// Description of this data
        /// </summary>
        public string Description => description;
        
        /// <summary>
        /// Numeric value
        /// </summary>
        public float Value => value;
        
        /// <summary>
        /// Count value
        /// </summary>
        public int Count => count;
        
        /// <summary>
        /// Whether this data is enabled
        /// </summary>
        public bool IsEnabled => isEnabled;
        
        /// <summary>
        /// Validate the data when values change
        /// </summary>
        private void OnValidate()
        {
            // Clamp values to valid ranges
            value = Mathf.Max(0f, value);
            count = Mathf.Max(0, count);
            
            // Ensure display name is not empty
            if (string.IsNullOrEmpty(displayName))
            {
                displayName = name;
            }
        }
    }
}";
    }
    
    private string PostProcessGeneratedCode(string code)
    {
        // Remove any markdown code block markers
        code = code.Replace("```csharp", "").Replace("```", "");
        
        // Ensure proper line endings
        code = code.Replace("\r\n", "\n").Replace("\r", "\n");
        
        // Add proper namespace if not specified
        if (string.IsNullOrEmpty(currentRequest.targetNamespace) && !code.Contains("namespace"))
        {
            code = "namespace Game\n{\n" + code + "\n}";
        }
        
        return code.Trim();
    }
    
    private void SaveGeneratedCode()
    {
        if (string.IsNullOrEmpty(generatedCode)) return;
        
        string defaultName = "GeneratedScript.cs";
        string path = EditorUtility.SaveFilePanel("Save Generated Code", 
                                                 Application.dataPath, 
                                                 defaultName, 
                                                 "cs");
        
        if (!string.IsNullOrEmpty(path))
        {
            File.WriteAllText(path, generatedCode);
            AssetDatabase.Refresh();
            
            // Try to ping the created file
            string relativePath = "Assets" + path.Substring(Application.dataPath.Length);
            var asset = AssetDatabase.LoadAssetAtPath<MonoScript>(relativePath);
            if (asset != null)
            {
                EditorGUIUtility.PingObject(asset);
            }
        }
    }
}
```

## 🚀 AI/LLM Integration Prompts

### Advanced Debugging Analysis

```
Analyze this Unity error with comprehensive debugging assistance:

Error: [Insert error message]
Stack Trace: [Insert stack trace]
Code Context: [Insert relevant code]

Provide:
1. Root cause analysis with technical explanation
2. Step-by-step debugging approach
3. Immediate fix with code examples
4. Prevention strategies and best practices
5. Performance implications and optimizations
6. Unit testing recommendations
7. Code review suggestions

Focus on Unity-specific patterns and production-ready solutions.
```

### Code Generation Templates

```
Generate Unity C# code with the following specifications:

Purpose: [Describe functionality]
Type: [MonoBehaviour/ScriptableObject/System/etc.]
Architecture: [Design patterns to use]
Performance: [Performance requirements]
Platform: [Target platform considerations]

Requirements:
- Follow Unity coding conventions
- Include comprehensive error handling
- Add performance optimizations
- Implement proper lifecycle management
- Include debug/testing features
- Add comprehensive documentation

Generate production-ready, maintainable code.
```

## 💡 AI-Enhanced Testing Workflows

### Automated Test Generation

```csharp
using UnityEngine;
using UnityEngine.TestTools;
using NUnit.Framework;
using System.Collections;
using System.Collections.Generic;

public class AIGeneratedTestSuite
{
    [Test]
    public void TestObjectPooling_ValidatesCorrectBehavior()
    {
        // AI-generated test for object pooling system
        var pool = new GameObject("TestPool").AddComponent<ObjectPool<TestBullet>>();
        
        // Setup pool with test prefab
        var bulletPrefab = new GameObject("Bullet").AddComponent<TestBullet>();
        pool.SetPrefab(bulletPrefab);
        pool.Initialize(10);
        
        // Test getting objects from pool
        var bullet1 = pool.Get();
        var bullet2 = pool.Get();
        
        Assert.IsNotNull(bullet1);
        Assert.IsNotNull(bullet2);
        Assert.AreNotEqual(bullet1, bullet2);
        
        // Test returning objects to pool
        pool.Return(bullet1);
        var bullet3 = pool.Get();
        
        Assert.AreEqual(bullet1, bullet3); // Should reuse returned object
        
        // Cleanup
        Object.DestroyImmediate(pool.gameObject);
        Object.DestroyImmediate(bulletPrefab);
    }
    
    [UnityTest]
    public IEnumerator TestAIBehavior_StateTransitions()
    {
        // AI-generated test for state machine behavior
        var aiEntity = new GameObject("AI").AddComponent<AIController>();
        var player = new GameObject("Player").AddComponent<PlayerController>();
        
        // Setup initial state
        aiEntity.Initialize();
        Assert.AreEqual(AIState.Patrol, aiEntity.CurrentState);
        
        // Move player into detection range
        player.transform.position = aiEntity.transform.position + Vector3.forward * 5f;
        
        // Wait for state update
        yield return new WaitForSeconds(0.1f);
        
        Assert.AreEqual(AIState.Chase, aiEntity.CurrentState);
        
        // Move player into attack range
        player.transform.position = aiEntity.transform.position + Vector3.forward * 1f;
        
        yield return new WaitForSeconds(0.1f);
        
        Assert.AreEqual(AIState.Attack, aiEntity.CurrentState);
        
        // Cleanup
        Object.DestroyImmediate(aiEntity.gameObject);
        Object.DestroyImmediate(player.gameObject);
    }
}

// Mock components for testing
public class TestBullet : MonoBehaviour, IPoolable
{
    public bool IsActive => gameObject.activeInHierarchy;
    public void OnSpawn() { }
    public void OnDespawn() { }
}
```

This comprehensive AI-powered debugging and code generation system provides intelligent assistance throughout the Unity development workflow, significantly accelerating development while maintaining code quality.