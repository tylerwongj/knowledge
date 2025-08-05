# 03-Code-Generation-Templates.md

## 🎯 Learning Objectives
- Master Unity code generation techniques for rapid development
- Create intelligent template systems that adapt to project needs
- Implement AI-powered code generation with context awareness
- Develop automated refactoring and code enhancement tools

## 🔧 Unity Code Generation Implementation

### Intelligent Code Generator System
```csharp
// Scripts/Editor/CodeGenerator.cs
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using UnityEngine;
using UnityEditor;

public class CodeGenerator : EditorWindow
{
    [Header("Code Generation Configuration")]
    [SerializeField] private string namespaceName = "GameCode";
    [SerializeField] private string outputPath = "Assets/Scripts/Generated";
    [SerializeField] private bool useRegions = true;
    [SerializeField] private bool generateDocumentation = true;
    [SerializeField] private bool addUnityAnalyzerSupport = true;
    
    // Template Categories
    public enum TemplateCategory
    {
        MonoBehaviour,
        ScriptableObject,
        EditorTool,
        DataStructure,
        Manager,
        Interface,
        StateMachine,
        EventSystem,
        Singleton,
        ObjectPool
    }
    
    // Code Templates
    [Serializable]
    public class CodeTemplate
    {
        public string templateName;
        public TemplateCategory category;
        public string description;
        public List<TemplateParameter> parameters;
        public string templateContent;
        public List<string> requiredUsings;
        public List<string> dependencies;
        public bool requiresCustomImplementation;
        
        public CodeTemplate()
        {
            parameters = new List<TemplateParameter>();
            requiredUsings = new List<string>();
            dependencies = new List<string>();
        }
    }
    
    [Serializable]
    public class TemplateParameter
    {
        public string parameterName;
        public ParameterType type;
        public string defaultValue;
        public string description;
        public bool isRequired;
        public List<string> validOptions; // For enum/dropdown parameters
        
        public TemplateParameter()
        {
            validOptions = new List<string>();
        }
    }
    
    public enum ParameterType
    {
        String,
        Integer,
        Float,
        Boolean,
        Enum,
        Class,
        Interface,
        UnityObject
    }
    
    // Generation Configuration
    [Serializable]
    public class GenerationRequest
    {
        public CodeTemplate template;
        public Dictionary<string, object> parameterValues;
        public string targetClassName;
        public string targetFilePath;
        public bool overwriteExisting;
        public List<string> additionalUsings;
        
        public GenerationRequest()
        {
            parameterValues = new Dictionary<string, object>();
            additionalUsings = new List<string>();
        }
    }
    
    private List<CodeTemplate> templates = new List<CodeTemplate>();
    private List<GenerationRequest> generationQueue = new List<GenerationRequest>();
    private List<string> generationLog = new List<string>();
    
    // UI State
    private Vector2 scrollPosition;
    private int selectedTab = 0;
    private string[] tabNames = { "Templates", "Generator", "AI Assistant", "Batch Generate", "Settings" };
    private int selectedTemplate = 0;
    private string searchFilter = "";
    
    // AI Integration
    private bool enableAIGeneration = true;
    private string aiApiEndpoint = "https://api.openai.com/v1/";
    private string aiModel = "gpt-4";
    
    [MenuItem("Tools/Code Generator")]
    public static void ShowWindow()
    {
        var window = GetWindow<CodeGenerator>("Code Generator");
        window.minSize = new Vector2(1000, 800);
        window.Show();
    }
    
    private void OnEnable()
    {
        LoadTemplates();
        LoadConfiguration();
    }
    
    private void OnGUI()
    {
        EditorGUILayout.BeginVertical();
        
        // Header
        DrawHeader();
        
        // Tab Selection
        selectedTab = GUILayout.Toolbar(selectedTab, tabNames);
        EditorGUILayout.Space();
        
        scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);
        
        switch (selectedTab)
        {
            case 0:
                DrawTemplatesTab();
                break;
            case 1:
                DrawGeneratorTab();
                break;
            case 2:
                DrawAIAssistantTab();
                break;
            case 3:
                DrawBatchGenerateTab();
                break;
            case 4:
                DrawSettingsTab();
                break;
        }
        
        EditorGUILayout.EndScrollView();
        EditorGUILayout.EndVertical();
    }
    
    private void DrawHeader()
    {
        EditorGUILayout.Space();
        EditorGUILayout.LabelField("Unity Code Generation System", EditorStyles.boldLabel);
        EditorGUILayout.LabelField($"Templates: {templates.Count} | Generated: {Directory.GetFiles(outputPath, "*.cs", SearchOption.AllDirectories).Length}", EditorStyles.miniLabel);
        EditorGUILayout.Space();
    }
    
    private void DrawTemplatesTab()
    {
        EditorGUILayout.LabelField("Code Templates", EditorStyles.boldLabel);
        EditorGUILayout.Space();
        
        // Search and Filter
        EditorGUILayout.BeginHorizontal();
        searchFilter = EditorGUILayout.TextField("Search Templates", searchFilter);
        if (GUILayout.Button("Clear", GUILayout.Width(60)))
        {
            searchFilter = "";
        }
        EditorGUILayout.EndHorizontal();
        EditorGUILayout.Space();
        
        // Template Categories
        var categorizedTemplates = templates
            .Where(t => string.IsNullOrEmpty(searchFilter) || 
                       t.templateName.ToLower().Contains(searchFilter.ToLower()) ||
                       t.description.ToLower().Contains(searchFilter.ToLower()))
            .GroupBy(t => t.category)
            .OrderBy(g => g.Key.ToString());
        
        foreach (var categoryGroup in categorizedTemplates)
        {
            EditorGUILayout.LabelField(categoryGroup.Key.ToString(), EditorStyles.boldLabel);
            EditorGUILayout.BeginVertical("box");
            
            foreach (var template in categoryGroup)
            {
                EditorGUILayout.BeginHorizontal();
                
                EditorGUILayout.BeginVertical();
                EditorGUILayout.LabelField(template.templateName, EditorStyles.boldLabel);
                EditorGUILayout.LabelField(template.description, EditorStyles.miniLabel);
                EditorGUILayout.LabelField($"Parameters: {template.parameters.Count}, Dependencies: {template.dependencies.Count}", EditorStyles.miniLabel);
                EditorGUILayout.EndVertical();
                
                GUILayout.FlexibleSpace();
                
                if (GUILayout.Button("Use Template", GUILayout.Width(100)))
                {
                    UseTemplate(template);
                }
                
                if (GUILayout.Button("Edit", GUILayout.Width(60)))
                {
                    EditTemplate(template);
                }
                
                if (GUILayout.Button("Clone", GUILayout.Width(60)))
                {
                    CloneTemplate(template);
                }
                
                EditorGUILayout.EndHorizontal();
                EditorGUILayout.Space();
            }
            
            EditorGUILayout.EndVertical();
            EditorGUILayout.Space();
        }
        
        // Template Management
        EditorGUILayout.BeginHorizontal();
        if (GUILayout.Button("Create New Template"))
        {
            CreateNewTemplate();
        }
        if (GUILayout.Button("Import Templates"))
        {
            ImportTemplates();
        }
        if (GUILayout.Button("Export Templates"))
        {
            ExportTemplates();
        }
        if (GUILayout.Button("Reset to Defaults"))
        {
            ResetToDefaultTemplates();
        }
        EditorGUILayout.EndHorizontal();
    }
    
    private void DrawGeneratorTab()
    {
        EditorGUILayout.LabelField("Code Generator", EditorStyles.boldLabel);
        EditorGUILayout.Space();
        
        if (templates.Count == 0)
        {
            EditorGUILayout.HelpBox("No templates available. Create or import templates first.", MessageType.Warning);
            return;
        }
        
        // Template Selection
        string[] templateNames = templates.Select(t => $"{t.category}: {t.templateName}").ToArray();
        selectedTemplate = EditorGUILayout.Popup("Select Template", selectedTemplate, templateNames);
        
        if (selectedTemplate >= 0 && selectedTemplate < templates.Count)
        {
            var template = templates[selectedTemplate];
            
            EditorGUILayout.Space();
            EditorGUILayout.LabelField($"Template: {template.templateName}", EditorStyles.boldLabel);
            EditorGUILayout.LabelField(template.description, EditorStyles.wordWrappedLabel);
            EditorGUILayout.Space();
            
            // Generation Parameters
            EditorGUILayout.LabelField("Generation Parameters", EditorStyles.boldLabel);
            EditorGUILayout.BeginVertical("box");
            
            // Basic Parameters
            string className = EditorGUILayout.TextField("Class Name", GetParameterValue("className", "NewClass"));
            string fileName = EditorGUILayout.TextField("File Name", className + ".cs");
            string filePath = EditorGUILayout.TextField("Output Path", Path.Combine(outputPath, fileName));
            
            // Template Parameters
            DrawTemplateParameters(template);
            
            EditorGUILayout.EndVertical();
            EditorGUILayout.Space();
            
            // Preview
            if (GUILayout.Button("Preview Generated Code"))
            {
                PreviewGeneratedCode(template, className);
            }
            
            EditorGUILayout.Space();
            
            // Generation Actions
            EditorGUILayout.BeginHorizontal();
            
            GUI.backgroundColor = Color.green;
            if (GUILayout.Button("Generate Code", GUILayout.Height(30)))
            {
                GenerateCode(template, className, filePath);
            }
            GUI.backgroundColor = Color.white;
            
            if (GUILayout.Button("Add to Queue", GUILayout.Height(30)))
            {
                AddToGenerationQueue(template, className, filePath);
            }
            
            if (GUILayout.Button("Generate with AI", GUILayout.Height(30)))
            {
                GenerateWithAI(template, className);
            }
            
            EditorGUILayout.EndHorizontal();
        }
    }
    
    private void DrawAIAssistantTab()
    {
        EditorGUILayout.LabelField("AI Code Generation Assistant", EditorStyles.boldLabel);
        EditorGUILayout.Space();
        
        EditorGUILayout.HelpBox("Use AI to generate custom Unity scripts based on natural language descriptions.", MessageType.Info);
        EditorGUILayout.Space();
        
        // AI Configuration
        EditorGUILayout.LabelField("AI Configuration", EditorStyles.boldLabel);
        EditorGUILayout.BeginVertical("box");
        
        enableAIGeneration = EditorGUILayout.Toggle("Enable AI Generation", enableAIGeneration);
        aiApiEndpoint = EditorGUILayout.TextField("API Endpoint", aiApiEndpoint);
        aiModel = EditorGUILayout.TextField("AI Model", aiModel);
        
        EditorGUILayout.EndVertical();
        EditorGUILayout.Space();
        
        // Natural Language Input
        EditorGUILayout.LabelField("Describe Your Script", EditorStyles.boldLabel);
        EditorGUILayout.BeginVertical("box");
        
        string scriptDescription = EditorGUILayout.TextArea("", GUILayout.Height(100));
        
        EditorGUILayout.LabelField("Example: \"Create a player controller with movement, jumping, and health system\"");
        
        EditorGUILayout.EndVertical();
        EditorGUILayout.Space();
        
        // Generation Options
        EditorGUILayout.LabelField("Generation Options", EditorStyles.boldLabel);
        EditorGUILayout.BeginVertical("box");
        
        EditorGUILayout.Popup("Code Style", 0, new string[] { "Clean Code", "Performance Optimized", "Mobile Optimized", "Beginner Friendly" });
        EditorGUILayout.Popup("Architecture Pattern", 0, new string[] { "Standard MonoBehaviour", "Component System", "MVC Pattern", "Observer Pattern" });
        EditorGUILayout.Toggle("Include Comments", true);
        EditorGUILayout.Toggle("Include Unit Tests", false);
        EditorGUILayout.Toggle("Include Documentation", true);
        
        EditorGUILayout.EndVertical();
        EditorGUILayout.Space();
        
        // AI Actions
        EditorGUILayout.BeginHorizontal();
        if (GUILayout.Button("Generate Script with AI"))
        {
            GenerateScriptWithAI(scriptDescription);
        }
        if (GUILayout.Button("Improve Existing Code"))
        {
            ImproveExistingCode();
        }
        if (GUILayout.Button("Generate Tests"))
        {
            GenerateTestCode();
        }
        EditorGUILayout.EndHorizontal();
        
        EditorGUILayout.Space();
        
        // AI Suggestions
        EditorGUILayout.LabelField("AI Suggestions", EditorStyles.boldLabel);
        EditorGUILayout.BeginVertical("box");
        
        EditorGUILayout.LabelField("• Consider using interfaces for better testability");
        EditorGUILayout.LabelField("• Implement object pooling for performance");
        EditorGUILayout.LabelField("• Add input validation for robustness");
        EditorGUILayout.LabelField("• Use UnityEvents for loose coupling");
        
        EditorGUILayout.EndVertical();
    }
    
    private void DrawBatchGenerateTab()
    {
        EditorGUILayout.LabelField("Batch Code Generation", EditorStyles.boldLabel);
        EditorGUILayout.Space();
        
        // Generation Queue
        EditorGUILayout.LabelField($"Generation Queue ({generationQueue.Count} items)", EditorStyles.boldLabel);
        EditorGUILayout.BeginVertical("box");
        
        if (generationQueue.Count > 0)
        {
            foreach (var request in generationQueue)
            {
                EditorGUILayout.BeginHorizontal();
                
                EditorGUILayout.LabelField($"{request.template.templateName}: {request.targetClassName}");
                GUILayout.FlexibleSpace();
                
                if (GUILayout.Button("Remove", GUILayout.Width(60)))
                {
                    generationQueue.Remove(request);
                    break;
                }
                
                EditorGUILayout.EndHorizontal();
            }
        }
        else
        {
            EditorGUILayout.LabelField("No items in generation queue", EditorStyles.centeredGreyMiniLabel);
        }
        
        EditorGUILayout.EndVertical();
        EditorGUILayout.Space();
        
        // Batch Operations
        EditorGUILayout.LabelField("Batch Operations", EditorStyles.boldLabel);
        EditorGUILayout.BeginHorizontal();
        
        if (GUILayout.Button("Process Queue") && generationQueue.Count > 0)
        {
            ProcessGenerationQueue();
        }
        
        if (GUILayout.Button("Clear Queue"))
        {
            generationQueue.Clear();
        }
        
        if (GUILayout.Button("Save Queue"))
        {
            SaveGenerationQueue();
        }
        
        if (GUILayout.Button("Load Queue"))
        {
            LoadGenerationQueue();
        }
        
        EditorGUILayout.EndHorizontal();
        EditorGUILayout.Space();
        
        // Bulk Generation Tools
        EditorGUILayout.LabelField("Bulk Generation Tools", EditorStyles.boldLabel);
        EditorGUILayout.BeginVertical("box");
        
        EditorGUILayout.BeginHorizontal();
        if (GUILayout.Button("Generate Manager Classes"))
        {
            GenerateManagerClasses();
        }
        if (GUILayout.Button("Generate Data Classes"))
        {
            GenerateDataClasses();
        }
        if (GUILayout.Button("Generate UI Controllers"))
        {
            GenerateUIControllers();
        }
        EditorGUILayout.EndHorizontal();
        
        EditorGUILayout.BeginHorizontal();
        if (GUILayout.Button("Generate Interfaces"))
        {
            GenerateInterfaces();
        }
        if (GUILayout.Button("Generate Enums"))
        {
            GenerateEnums();
        }
        if (GUILayout.Button("Generate ScriptableObjects"))
        {
            GenerateScriptableObjects();
        }
        EditorGUILayout.EndHorizontal();
        
        EditorGUILayout.EndVertical();
        EditorGUILayout.Space();
        
        // Project Analysis
        EditorGUILayout.LabelField("Project Analysis", EditorStyles.boldLabel);
        EditorGUILayout.BeginVertical("box");
        
        if (GUILayout.Button("Analyze Missing Components"))
        {
            AnalyzeMissingComponents();
        }
        
        if (GUILayout.Button("Suggest Code Improvements"))
        {
            SuggestCodeImprovements();
        }
        
        if (GUILayout.Button("Generate Documentation"))
        {
            GenerateProjectDocumentation();
        }
        
        EditorGUILayout.EndVertical();
    }
    
    private void DrawSettingsTab()
    {
        EditorGUILayout.LabelField("Code Generation Settings", EditorStyles.boldLabel);
        EditorGUILayout.Space();
        
        // General Settings
        EditorGUILayout.LabelField("General Settings", EditorStyles.boldLabel);
        EditorGUILayout.BeginVertical("box");
        
        namespaceName = EditorGUILayout.TextField("Default Namespace", namespaceName);
        outputPath = EditorGUILayout.TextField("Output Path", outputPath);
        
        EditorGUILayout.BeginHorizontal();
        if (GUILayout.Button("Browse"))
        {
            string path = EditorUtility.OpenFolderPanel("Select Output Folder", outputPath, "");
            if (!string.IsNullOrEmpty(path) && path.StartsWith(Application.dataPath))
            {
                outputPath = "Assets" + path.Substring(Application.dataPath.Length);
            }
        }
        EditorGUILayout.EndHorizontal();
        
        useRegions = EditorGUILayout.Toggle("Use Code Regions", useRegions);
        generateDocumentation = EditorGUILayout.Toggle("Generate Documentation", generateDocumentation);
        addUnityAnalyzerSupport = EditorGUILayout.Toggle("Unity Analyzer Support", addUnityAnalyzerSupport);
        
        EditorGUILayout.EndVertical();
        EditorGUILayout.Space();
        
        // Code Style Settings
        EditorGUILayout.LabelField("Code Style Settings", EditorStyles.boldLabel);
        EditorGUILayout.BeginVertical("box");
        
        EditorGUILayout.Popup("Brace Style", 0, new string[] { "K&R", "Allman", "GNU", "Horstmann" });
        EditorGUILayout.Popup("Naming Convention", 0, new string[] { "PascalCase", "camelCase", "snake_case" });
        EditorGUILayout.Toggle("Use var keyword", true);
        EditorGUILayout.Toggle("Add using statements", true);
        EditorGUILayout.IntSlider("Indentation Size", 4, 2, 8);
        
        EditorGUILayout.EndVertical();
        EditorGUILayout.Space();
        
        // Template Settings
        EditorGUILayout.LabelField("Template Settings", EditorStyles.boldLabel);
        EditorGUILayout.BeginVertical("box");
        
        EditorGUILayout.TextField("Template Directory", "Assets/Editor/Templates");
        EditorGUILayout.Toggle("Auto-save templates", true);
        EditorGUILayout.Toggle("Validate templates on load", true);
        EditorGUILayout.Toggle("Enable template versioning", false);
        
        EditorGUILayout.EndVertical();
        EditorGUILayout.Space();
        
        // Configuration Management
        EditorGUILayout.BeginHorizontal();
        if (GUILayout.Button("Save Configuration"))
        {
            SaveConfiguration();
        }
        if (GUILayout.Button("Load Configuration"))
        {
            LoadConfiguration();
        }
        if (GUILayout.Button("Reset to Defaults"))
        {
            ResetToDefaults();
        }
        EditorGUILayout.EndHorizontal();
    }
    
    // Core Generation Methods
    private void GenerateCode(CodeTemplate template, string className, string filePath)
    {
        try
        {
            AddLog($"Generating {className} using template {template.templateName}...");
            
            // Create output directory if it doesn't exist
            string directory = Path.GetDirectoryName(filePath);
            if (!Directory.Exists(directory))
            {
                Directory.CreateDirectory(directory);
            }
            
            // Generate code content
            string generatedCode = ProcessTemplate(template, className);
            
            // Write to file
            File.WriteAllText(filePath, generatedCode);
            
            // Refresh asset database
            AssetDatabase.Refresh();
            
            AddLog($"✓ Successfully generated {className} at {filePath}");
            
            // Select the generated file
            var asset = AssetDatabase.LoadAssetAtPath<UnityEngine.Object>(filePath);
            if (asset != null)
            {
                Selection.activeObject = asset;
                EditorGUIUtility.PingObject(asset);
            }
        }
        catch (Exception e)
        {
            AddLog($"✗ Error generating {className}: {e.Message}");
            EditorUtility.DisplayDialog("Generation Error", $"Failed to generate {className}: {e.Message}", "OK");
        }
    }
    
    private string ProcessTemplate(CodeTemplate template, string className)
    {
        string code = template.templateContent;
        
        // Replace template placeholders
        code = code.Replace("{{NAMESPACE}}", namespaceName);
        code = code.Replace("{{CLASS_NAME}}", className);
        code = code.Replace("{{TIMESTAMP}}", DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"));
        code = code.Replace("{{AUTHOR}}", Environment.UserName);
        
        // Process template parameters
        foreach (var param in template.parameters)
        {
            string value = GetParameterValue(param.parameterName, param.defaultValue);
            code = code.Replace($"{{{{{param.parameterName.ToUpper()}}}}}", value);
        }
        
        // Add using statements
        var usings = new List<string> { "System", "UnityEngine" };
        usings.AddRange(template.requiredUsings);
        
        string usingStatements = string.Join("\\n", usings.Select(u => $"using {u};"));
        code = code.Replace("{{USINGS}}", usingStatements);
        
        // Add documentation if enabled
        if (generateDocumentation)
        {
            code = AddDocumentation(code, className, template);
        }
        
        // Format code
        code = FormatCode(code);
        
        return code;
    }
    
    private string AddDocumentation(string code, string className, CodeTemplate template)
    {
        var documentation = new StringBuilder();
        documentation.AppendLine("/// <summary>");
        documentation.AppendLine($"/// {template.description}");
        documentation.AppendLine($"/// Generated on {DateTime.Now:yyyy-MM-dd} using {template.templateName} template");
        documentation.AppendLine("/// </summary>");
        
        // Insert before class declaration
        string classPattern = $@"(public\s+(?:abstract\s+)?(?:partial\s+)?class\s+{Regex.Escape(className)})";
        code = Regex.Replace(code, classPattern, documentation.ToString() + "$1", RegexOptions.Multiline);
        
        return code;
    }
    
    private string FormatCode(string code)
    {
        // Basic code formatting
        var lines = code.Split('\\n');
        var formattedLines = new List<string>();
        int indentLevel = 0;
        
        foreach (string line in lines)
        {
            string trimmedLine = line.Trim();
            
            if (trimmedLine.Contains("}"))
                indentLevel = Math.Max(0, indentLevel - 1);
            
            if (!string.IsNullOrEmpty(trimmedLine))
            {
                formattedLines.Add(new string(' ', indentLevel * 4) + trimmedLine);
            }
            else
            {
                formattedLines.Add("");
            }
            
            if (trimmedLine.Contains("{") && !trimmedLine.Contains("}"))
                indentLevel++;
        }
        
        return string.Join("\\n", formattedLines);
    }
    
    // Template Management
    private void LoadTemplates()
    {
        templates.Clear();
        
        // Load default templates
        LoadDefaultTemplates();
        
        // Load custom templates from files
        LoadCustomTemplates();
    }
    
    private void LoadDefaultTemplates()
    {
        // MonoBehaviour Template
        var monoBehaviourTemplate = new CodeTemplate
        {
            templateName = "MonoBehaviour Component",
            category = TemplateCategory.MonoBehaviour,
            description = "Standard Unity MonoBehaviour component with common lifecycle methods",
            templateContent = @"{{USINGS}}

namespace {{NAMESPACE}}
{
    {{DOCUMENTATION}}
    public class {{CLASS_NAME}} : MonoBehaviour
    {
        [Header(""{{CLASS_NAME}} Settings"")]
        [SerializeField] private bool debugMode = false;
        
        {{REGION_UNITY_LIFECYCLE}}
        private void Awake()
        {
            Initialize();
        }
        
        private void Start()
        {
            
        }
        
        private void Update()
        {
            if (debugMode)
            {
                // Debug updates
            }
        }
        {{ENDREGION}}
        
        {{REGION_PUBLIC_METHODS}}
        public void Initialize()
        {
            if (debugMode)
                Debug.Log($""[{name}] {GetType().Name} initialized"");
        }
        {{ENDREGION}}
        
        {{REGION_PRIVATE_METHODS}}
        {{ENDREGION}}
        
        {{REGION_EVENT_HANDLERS}}
        {{ENDREGION}}
    }
}",
            requiredUsings = new List<string> { "UnityEngine" }
        };
        
        templates.Add(monoBehaviourTemplate);
        
        // ScriptableObject Template
        var scriptableObjectTemplate = new CodeTemplate
        {
            templateName = "ScriptableObject Data",
            category = TemplateCategory.ScriptableObject,
            description = "ScriptableObject for game data storage",
            templateContent = @"{{USINGS}}

namespace {{NAMESPACE}}
{
    [CreateAssetMenu(fileName = ""New{{CLASS_NAME}}"", menuName = ""Game Data/{{CLASS_NAME}}"")]
    public class {{CLASS_NAME}} : ScriptableObject
    {
        [Header(""{{CLASS_NAME}} Configuration"")]
        [SerializeField] private string displayName = """";
        [SerializeField] private string description = """";
        
        public string DisplayName => displayName;
        public string Description => description;
        
        private void OnValidate()
        {
            if (string.IsNullOrEmpty(displayName))
                displayName = name;
        }
    }
}",
            requiredUsings = new List<string> { "UnityEngine" }
        };
        
        templates.Add(scriptableObjectTemplate);
        
        // Singleton Manager Template
        var singletonTemplate = new CodeTemplate
        {
            templateName = "Singleton Manager",
            category = TemplateCategory.Singleton,
            description = "Singleton pattern implementation for Unity managers",
            templateContent = @"{{USINGS}}

namespace {{NAMESPACE}}
{
    public class {{CLASS_NAME}} : MonoBehaviour
    {
        public static {{CLASS_NAME}} Instance { get; private set; }
        
        [Header(""{{CLASS_NAME}} Settings"")]
        [SerializeField] private bool dontDestroyOnLoad = true;
        [SerializeField] private bool debugMode = false;
        
        protected virtual void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                
                if (dontDestroyOnLoad)
                {
                    DontDestroyOnLoad(gameObject);
                }
                
                Initialize();
            }
            else if (Instance != this)
            {
                if (debugMode)
                    Debug.LogWarning($""Duplicate {GetType().Name} instance destroyed on {gameObject.name}"");
                
                Destroy(gameObject);
            }
        }
        
        protected virtual void Initialize()
        {
            if (debugMode)
                Debug.Log($""[{GetType().Name}] Initialized"");
        }
        
        protected virtual void OnDestroy()
        {
            if (Instance == this)
            {
                Instance = null;
            }
        }
    }
}",
            requiredUsings = new List<string> { "UnityEngine" }
        };
        
        templates.Add(singletonTemplate);
    }
    
    // Utility Methods
    private string GetParameterValue(string parameterName, string defaultValue)
    {
        // This would be connected to UI parameter inputs
        return defaultValue;
    }
    
    private void AddLog(string message)
    {
        string timestamp = DateTime.Now.ToString("HH:mm:ss");
        generationLog.Add($"[{timestamp}] {message}");
        Debug.Log($"[CodeGenerator] {message}");
    }
    
    // Placeholder methods for AI integration and other features
    private void DrawTemplateParameters(CodeTemplate template) { }
    private void UseTemplate(CodeTemplate template) { }
    private void EditTemplate(CodeTemplate template) { }
    private void CloneTemplate(CodeTemplate template) { }
    private void CreateNewTemplate() { }
    private void ImportTemplates() { }
    private void ExportTemplates() { }
    private void ResetToDefaultTemplates() { }
    private void PreviewGeneratedCode(CodeTemplate template, string className) { }
    private void AddToGenerationQueue(CodeTemplate template, string className, string filePath) { }
    private void GenerateWithAI(CodeTemplate template, string className) { }
    private void GenerateScriptWithAI(string description) { }
    private void ImproveExistingCode() { }
    private void GenerateTestCode() { }
    private void ProcessGenerationQueue() { }
    private void SaveGenerationQueue() { }
    private void LoadGenerationQueue() { }
    private void GenerateManagerClasses() { }
    private void GenerateDataClasses() { }
    private void GenerateUIControllers() { }
    private void GenerateInterfaces() { }
    private void GenerateEnums() { }
    private void GenerateScriptableObjects() { }
    private void AnalyzeMissingComponents() { }
    private void SuggestCodeImprovements() { }
    private void GenerateProjectDocumentation() { }
    private void LoadCustomTemplates() { }
    private void SaveConfiguration() { }
    private void LoadConfiguration() { }
    private void ResetToDefaults() { }
}
```

## 🚀 AI/LLM Integration Opportunities

### Intelligent Code Generation
```
PROMPT TEMPLATE - Unity Script Generation:

"Generate a Unity C# script based on this specification:

Script Requirements:
- Purpose: [Player Controller/UI Manager/Game Manager/etc.]
- Base Class: [MonoBehaviour/ScriptableObject/Interface/etc.]
- Functionality: [Detailed description of what the script should do]
- Dependencies: [Other systems it needs to interact with]

Technical Requirements:
- Unity Version: [2022.3 LTS/2023.2/etc.]
- Performance Considerations: [Mobile/Desktop/VR optimizations]
- Architecture Pattern: [MVC/Observer/Command/etc.]
- Code Style: [Clean Code/Performance/Beginner-friendly]

Generate:
1. Complete C# script with proper structure
2. XML documentation for all public members
3. Inspector-friendly serialized fields
4. Error handling and validation
5. Unity-specific optimizations
6. Event system integration if needed
7. Unit test stub methods
8. Usage examples in comments"
```

### Code Refactoring Assistant
```
PROMPT TEMPLATE - Unity Code Improvement:

"Analyze and improve this Unity C# code:

```csharp
[PASTE YOUR CODE HERE]
```

Current Issues:
[LIST ANY KNOWN PROBLEMS OR CONCERNS]

Improvement Goals:
- Performance: [Target FPS/Memory usage/etc.]
- Maintainability: [Team size/Code complexity/etc.]
- Unity Best Practices: [Mobile/Desktop/WebGL/etc.]
- Architecture: [Current vs desired patterns]

Provide:
1. Refactored code with improvements
2. Explanation of changes made
3. Performance impact analysis
4. Unity-specific optimizations applied
5. Code smell elimination
6. Architecture pattern improvements
7. Testing recommendations
8. Future scalability considerations"
```

## 💡 Key Code Generation Principles

### Essential Template Design Checklist
- **Flexibility** - Templates should adapt to different use cases and parameters
- **Unity Integration** - Proper Inspector support and Unity lifecycle methods
- **Documentation** - Auto-generated XML docs and usage examples
- **Performance** - Generated code follows Unity performance best practices
- **Maintainability** - Clean, readable code with proper organization
- **Extensibility** - Templates support inheritance and composition patterns
- **Error Handling** - Robust validation and error recovery mechanisms
- **Testing Support** - Generated code includes test stubs and validation

### Common Unity Code Generation Challenges
1. **Template Complexity** - Balancing flexibility with simplicity
2. **Parameter Validation** - Ensuring generated code compiles and runs
3. **Code Quality** - Maintaining high standards in generated code
4. **Integration Issues** - Ensuring generated code works with existing systems
5. **Performance Impact** - Generated code efficiency and optimization
6. **Maintenance Overhead** - Keeping templates updated with Unity changes
7. **Team Consistency** - Ensuring all team members follow same patterns
8. **Version Control** - Managing generated files in source control

This comprehensive code generation system enables Unity developers to rapidly create high-quality, consistent code templates while leveraging AI assistance for intelligent code generation and optimization, significantly reducing development time and improving code quality across projects.