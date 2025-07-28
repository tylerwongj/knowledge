# @10-Code-Documentation-Generator

## 🎯 Core Concept
Automated code documentation generation and API reference creation for Unity game projects.

## 🔧 Implementation

### Documentation Generator
```csharp
using UnityEngine;
using UnityEditor;
using System.IO;
using System.Reflection;
using System.Linq;

public class DocumentationGenerator
{
    [MenuItem("Tools/Generate Documentation")]
    public static void GenerateDocumentation()
    {
        string outputPath = "Documentation/API_Reference.md";
        Directory.CreateDirectory(Path.GetDirectoryName(outputPath));
        
        using (StreamWriter writer = new StreamWriter(outputPath))
        {
            writer.WriteLine("# API Reference");
            writer.WriteLine();
            
            // Get all MonoBehaviour classes in the project
            Assembly[] assemblies = System.AppDomain.CurrentDomain.GetAssemblies();
            
            foreach (Assembly assembly in assemblies)
            {
                if (assembly.GetName().Name.Contains("Assembly-CSharp"))
                {
                    DocumentAssembly(writer, assembly);
                }
            }
        }
        
        AssetDatabase.Refresh();
        Debug.Log($"Documentation generated at {outputPath}");
    }
    
    static void DocumentAssembly(StreamWriter writer, Assembly assembly)
    {
        var types = assembly.GetTypes()
            .Where(t => t.IsSubclassOf(typeof(MonoBehaviour)) || t.IsSubclassOf(typeof(ScriptableObject)))
            .OrderBy(t => t.Name);
        
        foreach (Type type in types)
        {
            DocumentClass(writer, type);
        }
    }
    
    static void DocumentClass(StreamWriter writer, Type type)
    {
        writer.WriteLine($"## {type.Name}");
        writer.WriteLine();
        
        // Class description
        var summaryAttr = type.GetCustomAttribute<System.ComponentModel.DescriptionAttribute>();
        if (summaryAttr != null)
        {
            writer.WriteLine(summaryAttr.Description);
            writer.WriteLine();
        }
        
        // Public fields
        var publicFields = type.GetFields(BindingFlags.Public | BindingFlags.Instance)
            .Where(f => !f.IsSpecialName);
        
        if (publicFields.Any())
        {
            writer.WriteLine("### Public Fields");
            writer.WriteLine();
            
            foreach (FieldInfo field in publicFields)
            {
                writer.WriteLine($"- **{field.Name}** ({field.FieldType.Name}): {GetFieldDescription(field)}");
            }
            writer.WriteLine();
        }
        
        // Public methods
        var publicMethods = type.GetMethods(BindingFlags.Public | BindingFlags.Instance)
            .Where(m => m.DeclaringType == type && !m.IsSpecialName && !m.Name.StartsWith("get_") && !m.Name.StartsWith("set_"));
        
        if (publicMethods.Any())
        {
            writer.WriteLine("### Public Methods");
            writer.WriteLine();
            
            foreach (MethodInfo method in publicMethods)
            {
                string parameters = string.Join(", ", method.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                writer.WriteLine($"- **{method.Name}({parameters})**: {GetMethodDescription(method)}");
            }
            writer.WriteLine();
        }
        
        writer.WriteLine("---");
        writer.WriteLine();
    }
    
    static string GetFieldDescription(FieldInfo field)
    {
        var tooltipAttr = field.GetCustomAttribute<TooltipAttribute>();
        return tooltipAttr?.tooltip ?? "No description available";
    }
    
    static string GetMethodDescription(MethodInfo method)
    {
        // In a real implementation, you might parse XML documentation comments
        return "No description available";
    }
}
```

### README Generator
```csharp
[MenuItem("Tools/Generate README")]
public static void GenerateREADME()
{
    string readmePath = "README.md";
    
    using (StreamWriter writer = new StreamWriter(readmePath))
    {
        writer.WriteLine($"# {PlayerSettings.productName}");
        writer.WriteLine();
        writer.WriteLine($"Version: {PlayerSettings.bundleVersion}");
        writer.WriteLine($"Unity Version: {Application.unityVersion}");
        writer.WriteLine();
        
        writer.WriteLine("## Description");
        writer.WriteLine("// Add your game description here");
        writer.WriteLine();
        
        writer.WriteLine("## Features");
        var scenes = EditorBuildSettings.scenes.Where(s => s.enabled);
        foreach (var scene in scenes)
        {
            string sceneName = Path.GetFileNameWithoutExtension(scene.path);
            writer.WriteLine($"- {sceneName}");
        }
        writer.WriteLine();
        
        writer.WriteLine("## Installation");
        writer.WriteLine("1. Clone the repository");
        writer.WriteLine("2. Open in Unity");
        writer.WriteLine("3. Build and run");
        writer.WriteLine();
        
        writer.WriteLine("## Controls");
        writer.WriteLine("// Add control instructions here");
        writer.WriteLine();
    }
    
    AssetDatabase.Refresh();
    Debug.Log("README.md generated");
}
```

## 🚀 AI/LLM Integration
- Generate comprehensive code comments automatically
- Create user manuals from code structure
- Generate API documentation with usage examples

## 💡 Key Benefits
- Automated documentation maintenance
- Consistent documentation format
- Reduced manual documentation work