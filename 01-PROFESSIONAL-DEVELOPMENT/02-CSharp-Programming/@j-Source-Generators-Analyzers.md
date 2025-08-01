# @j-Source-Generators-Analyzers - Compile-Time Code Generation and Analysis

## 🎯 Learning Objectives
- Master C# Source Generators for compile-time code generation
- Implement custom Roslyn analyzers for code quality enforcement
- Create automated serialization and data binding systems
- Build development productivity tools and code validation frameworks

## 🔧 Source Generators Fundamentals

### Basic Source Generator Implementation
```csharp
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Text;
using System.Collections.Generic;
using System.Linq;
using System.Text;

[Generator]
public class PropertyNotificationGenerator : ISourceGenerator
{
    public void Initialize(GeneratorInitializationContext context)
    {
        // Register for syntax notifications
        context.RegisterForSyntaxNotifications(() => new PropertyNotificationSyntaxReceiver());
    }
    
    public void Execute(GeneratorExecutionContext context)
    {
        if (context.SyntaxReceiver is not PropertyNotificationSyntaxReceiver receiver)
            return;
        
        foreach (var classDeclaration in receiver.CandidateClasses)
        {
            var model = context.Compilation.GetSemanticModel(classDeclaration.SyntaxTree);
            var classSymbol = model.GetDeclaredSymbol(classDeclaration) as INamedTypeSymbol;
            
            if (classSymbol == null) continue;
            
            var source = GenerateNotificationClass(classSymbol, classDeclaration);
            context.AddSource($"{classSymbol.Name}_Generated.cs", SourceText.From(source, Encoding.UTF8));
        }
    }
    
    private string GenerateNotificationClass(INamedTypeSymbol classSymbol, ClassDeclarationSyntax classDeclaration)
    {
        var namespaceName = classSymbol.ContainingNamespace.IsGlobalNamespace 
            ? "" 
            : classSymbol.ContainingNamespace.ToDisplayString();
        
        var className = classSymbol.Name;
        var properties = GetNotifiableProperties(classDeclaration);
        
        var sourceBuilder = new StringBuilder();
        
        sourceBuilder.AppendLine("using System.ComponentModel;");
        sourceBuilder.AppendLine("using System.Runtime.CompilerServices;");
        sourceBuilder.AppendLine();
        
        if (!string.IsNullOrEmpty(namespaceName))
        {
            sourceBuilder.AppendLine($"namespace {namespaceName}");
            sourceBuilder.AppendLine("{");
        }
        
        sourceBuilder.AppendLine($"    public partial class {className} : INotifyPropertyChanged");
        sourceBuilder.AppendLine("    {");
        sourceBuilder.AppendLine("        public event PropertyChangedEventHandler PropertyChanged;");
        sourceBuilder.AppendLine();
        
        // Generate OnPropertyChanged method
        sourceBuilder.AppendLine("        protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)");
        sourceBuilder.AppendLine("        {");
        sourceBuilder.AppendLine("            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));");
        sourceBuilder.AppendLine("        }");
        sourceBuilder.AppendLine();
        
        // Generate SetField method
        sourceBuilder.AppendLine("        protected bool SetField<T>(ref T field, T value, [CallerMemberName] string propertyName = null)");
        sourceBuilder.AppendLine("        {");
        sourceBuilder.AppendLine("            if (EqualityComparer<T>.Default.Equals(field, value)) return false;");
        sourceBuilder.AppendLine("            field = value;");
        sourceBuilder.AppendLine("            OnPropertyChanged(propertyName);");
        sourceBuilder.AppendLine("            return true;");
        sourceBuilder.AppendLine("        }");
        sourceBuilder.AppendLine();
        
        // Generate properties
        foreach (var property in properties)
        {
            GenerateProperty(sourceBuilder, property);
        }
        
        sourceBuilder.AppendLine("    }");
        
        if (!string.IsNullOrEmpty(namespaceName))
        {
            sourceBuilder.AppendLine("}");
        }
        
        return sourceBuilder.ToString();
    }
    
    private void GenerateProperty(StringBuilder sourceBuilder, PropertyInfo property)
    {
        var fieldName = $"_{property.Name.Substring(0, 1).ToLower()}{property.Name.Substring(1)}";
        
        sourceBuilder.AppendLine($"        private {property.Type} {fieldName};");
        sourceBuilder.AppendLine($"        public {property.Type} {property.Name}");
        sourceBuilder.AppendLine("        {");
        sourceBuilder.AppendLine($"            get => {fieldName};");
        sourceBuilder.AppendLine($"            set => SetField(ref {fieldName}, value);");
        sourceBuilder.AppendLine("        }");
        sourceBuilder.AppendLine();
    }
    
    private List<PropertyInfo> GetNotifiableProperties(ClassDeclarationSyntax classDeclaration)
    {
        var properties = new List<PropertyInfo>();
        
        foreach (var member in classDeclaration.Members.OfType<PropertyDeclarationSyntax>())
        {
            // Look for properties with [Notify] attribute
            if (member.AttributeLists.Any(al => 
                al.Attributes.Any(a => a.Name.ToString() == "Notify")))
            {
                properties.Add(new PropertyInfo
                {
                    Name = member.Identifier.Text,
                    Type = member.Type.ToString()
                });
            }
        }
        
        return properties;
    }
    
    private class PropertyInfo
    {
        public string Name { get; set; }
        public string Type { get; set; }
    }
}

// Syntax receiver for finding candidate classes
public class PropertyNotificationSyntaxReceiver : ISyntaxReceiver
{
    public List<ClassDeclarationSyntax> CandidateClasses { get; } = new List<ClassDeclarationSyntax>();
    
    public void OnVisitSyntaxNode(SyntaxNode syntaxNode)
    {
        if (syntaxNode is ClassDeclarationSyntax classDeclaration &&
            classDeclaration.Modifiers.Any(m => m.IsKind(SyntaxKind.PartialKeyword)))
        {
            // Check if class has properties with [Notify] attribute
            if (HasNotifiableProperties(classDeclaration))
            {
                CandidateClasses.Add(classDeclaration);
            }
        }
    }
    
    private bool HasNotifiableProperties(ClassDeclarationSyntax classDeclaration)
    {
        return classDeclaration.Members
            .OfType<PropertyDeclarationSyntax>()
            .Any(p => p.AttributeLists.Any(al => 
                al.Attributes.Any(a => a.Name.ToString() == "Notify")));
    }
}

// Attribute for marking properties
[System.AttributeUsage(System.AttributeTargets.Property)]
public class NotifyAttribute : System.Attribute { }
```

### Advanced JSON Serialization Generator
```csharp
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Text;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json;

[Generator]
public class JsonSerializationGenerator : ISourceGenerator
{
    public void Initialize(GeneratorInitializationContext context)
    {
        context.RegisterForSyntaxNotifications(() => new JsonSerializationSyntaxReceiver());
    }
    
    public void Execute(GeneratorExecutionContext context)
    {
        if (context.SyntaxReceiver is not JsonSerializationSyntaxReceiver receiver)
            return;
        
        foreach (var classDeclaration in receiver.CandidateClasses)
        {
            var model = context.Compilation.GetSemanticModel(classDeclaration.SyntaxTree);
            var classSymbol = model.GetDeclaredSymbol(classDeclaration) as INamedTypeSymbol;
            
            if (classSymbol == null) continue;
            
            var source = GenerateJsonSerialization(classSymbol, classDeclaration);
            context.AddSource($"{classSymbol.Name}_JsonSerialization.cs", SourceText.From(source, Encoding.UTF8));
        }
    }
    
    private string GenerateJsonSerialization(INamedTypeSymbol classSymbol, ClassDeclarationSyntax classDeclaration)
    {
        var namespaceName = classSymbol.ContainingNamespace.IsGlobalNamespace 
            ? "" 
            : classSymbol.ContainingNamespace.ToDisplayString();
        
        var className = classSymbol.Name;
        var properties = GetSerializableProperties(classDeclaration);
        
        var sourceBuilder = new StringBuilder();
        
        sourceBuilder.AppendLine("using System;");
        sourceBuilder.AppendLine("using System.Text.Json;");
        sourceBuilder.AppendLine("using System.Text.Json.Serialization;");
        sourceBuilder.AppendLine();
        
        if (!string.IsNullOrEmpty(namespaceName))
        {
            sourceBuilder.AppendLine($"namespace {namespaceName}");
            sourceBuilder.AppendLine("{");
        }
        
        sourceBuilder.AppendLine($"    public partial class {className}");
        sourceBuilder.AppendLine("    {");
        
        // Generate ToJson method
        GenerateToJsonMethod(sourceBuilder, properties);
        
        // Generate FromJson method
        GenerateFromJsonMethod(sourceBuilder, className, properties);
        
        // Generate custom JsonConverter
        GenerateJsonConverter(sourceBuilder, className, properties);
        
        sourceBuilder.AppendLine("    }");
        
        if (!string.IsNullOrEmpty(namespaceName))
        {
            sourceBuilder.AppendLine("}");
        }
        
        return sourceBuilder.ToString();
    }
    
    private void GenerateToJsonMethod(StringBuilder sourceBuilder, List<SerializableProperty> properties)
    {
        sourceBuilder.AppendLine("        public string ToJson()");
        sourceBuilder.AppendLine("        {");
        sourceBuilder.AppendLine("            using var stream = new System.IO.MemoryStream();");
        sourceBuilder.AppendLine("            using var writer = new Utf8JsonWriter(stream);");
        sourceBuilder.AppendLine("            writer.WriteStartObject();");
        
        foreach (var property in properties)
        {
            var jsonName = property.JsonName ?? property.Name.ToLower();
            
            sourceBuilder.AppendLine($"            writer.WritePropertyName(\"{jsonName}\");");
            
            switch (property.Type.ToLower())
            {
                case "string":
                    sourceBuilder.AppendLine($"            writer.WriteStringValue({property.Name});");
                    break;
                case "int":
                case "int32":
                    sourceBuilder.AppendLine($"            writer.WriteNumberValue({property.Name});");
                    break;
                case "bool":
                case "boolean":
                    sourceBuilder.AppendLine($"            writer.WriteBooleanValue({property.Name});");
                    break;
                case "datetime":
                    sourceBuilder.AppendLine($"            writer.WriteStringValue({property.Name}.ToString(\"O\"));");
                    break;
                default:
                    sourceBuilder.AppendLine($"            JsonSerializer.Serialize(writer, {property.Name});");
                    break;
            }
        }
        
        sourceBuilder.AppendLine("            writer.WriteEndObject();");
        sourceBuilder.AppendLine("            writer.Flush();");
        sourceBuilder.AppendLine("            return System.Text.Encoding.UTF8.GetString(stream.ToArray());");
        sourceBuilder.AppendLine("        }");
        sourceBuilder.AppendLine();
    }
    
    private void GenerateFromJsonMethod(StringBuilder sourceBuilder, string className, List<SerializableProperty> properties)
    {
        sourceBuilder.AppendLine($"        public static {className} FromJson(string json)");
        sourceBuilder.AppendLine("        {");
        sourceBuilder.AppendLine($"            var instance = new {className}();");
        sourceBuilder.AppendLine("            using var document = JsonDocument.Parse(json);");
        sourceBuilder.AppendLine("            var root = document.RootElement;");
        sourceBuilder.AppendLine();
        
        foreach (var property in properties)
        {
            var jsonName = property.JsonName ?? property.Name.ToLower();
            
            sourceBuilder.AppendLine($"            if (root.TryGetProperty(\"{jsonName}\", out var {property.Name.ToLower()}Element))");
            sourceBuilder.AppendLine("            {");
            
            switch (property.Type.ToLower())
            {
                case "string":
                    sourceBuilder.AppendLine($"                instance.{property.Name} = {property.Name.ToLower()}Element.GetString();");
                    break;
                case "int":
                case "int32":
                    sourceBuilder.AppendLine($"                instance.{property.Name} = {property.Name.ToLower()}Element.GetInt32();");
                    break;
                case "bool":
                case "boolean":
                    sourceBuilder.AppendLine($"                instance.{property.Name} = {property.Name.ToLower()}Element.GetBoolean();");
                    break;
                case "datetime":
                    sourceBuilder.AppendLine($"                instance.{property.Name} = {property.Name.ToLower()}Element.GetDateTime();");
                    break;
                default:
                    sourceBuilder.AppendLine($"                instance.{property.Name} = JsonSerializer.Deserialize<{property.Type}>({property.Name.ToLower()}Element.GetRawText());");
                    break;
            }
            
            sourceBuilder.AppendLine("            }");
        }
        
        sourceBuilder.AppendLine();
        sourceBuilder.AppendLine("            return instance;");
        sourceBuilder.AppendLine("        }");
        sourceBuilder.AppendLine();
    }
    
    private void GenerateJsonConverter(StringBuilder sourceBuilder, string className, List<SerializableProperty> properties)
    {
        sourceBuilder.AppendLine($"        public class {className}JsonConverter : JsonConverter<{className}>");
        sourceBuilder.AppendLine("        {");
        sourceBuilder.AppendLine($"            public override {className} Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)");
        sourceBuilder.AppendLine("            {");
        sourceBuilder.AppendLine("                using var document = JsonDocument.ParseValue(ref reader);");
        sourceBuilder.AppendLine("                return FromJson(document.RootElement.GetRawText());");
        sourceBuilder.AppendLine("            }");
        sourceBuilder.AppendLine();
        sourceBuilder.AppendLine($"            public override void Write(Utf8JsonWriter writer, {className} value, JsonSerializerOptions options)");
        sourceBuilder.AppendLine("            {");
        sourceBuilder.AppendLine("                var json = value.ToJson();");
        sourceBuilder.AppendLine("                using var document = JsonDocument.Parse(json);");
        sourceBuilder.AppendLine("                document.WriteTo(writer);");
        sourceBuilder.AppendLine("            }");
        sourceBuilder.AppendLine("        }");
    }
    
    private List<SerializableProperty> GetSerializableProperties(ClassDeclarationSyntax classDeclaration)
    {
        var properties = new List<SerializableProperty>();
        
        foreach (var member in classDeclaration.Members.OfType<PropertyDeclarationSyntax>())
        {
            var jsonAttribute = member.AttributeLists
                .SelectMany(al => al.Attributes)
                .FirstOrDefault(a => a.Name.ToString() == "JsonSerialize");
            
            if (jsonAttribute != null)
            {
                var jsonName = GetAttributeArgument(jsonAttribute, "Name");
                
                properties.Add(new SerializableProperty
                {
                    Name = member.Identifier.Text,
                    Type = member.Type.ToString(),
                    JsonName = jsonName
                });
            }
        }
        
        return properties;
    }
    
    private string GetAttributeArgument(AttributeSyntax attribute, string argumentName)
    {
        return attribute.ArgumentList?.Arguments
            .OfType<AttributeArgumentSyntax>()
            .FirstOrDefault(arg => arg.NameEquals?.Name.Identifier.Text == argumentName)
            ?.Expression.ToString().Trim('"');
    }
    
    private class SerializableProperty
    {
        public string Name { get; set; }
        public string Type { get; set; }
        public string JsonName { get; set; }
    }
}

public class JsonSerializationSyntaxReceiver : ISyntaxReceiver
{
    public List<ClassDeclarationSyntax> CandidateClasses { get; } = new List<ClassDeclarationSyntax>();
    
    public void OnVisitSyntaxNode(SyntaxNode syntaxNode)
    {
        if (syntaxNode is ClassDeclarationSyntax classDeclaration &&
            classDeclaration.Modifiers.Any(m => m.IsKind(SyntaxKind.PartialKeyword)))
        {
            if (HasJsonSerializableProperties(classDeclaration))
            {
                CandidateClasses.Add(classDeclaration);
            }
        }
    }
    
    private bool HasJsonSerializableProperties(ClassDeclarationSyntax classDeclaration)
    {
        return classDeclaration.Members
            .OfType<PropertyDeclarationSyntax>()
            .Any(p => p.AttributeLists.Any(al => 
                al.Attributes.Any(a => a.Name.ToString() == "JsonSerialize")));
    }
}

// Attribute for marking serializable properties
[System.AttributeUsage(System.AttributeTargets.Property)]
public class JsonSerializeAttribute : System.Attribute
{
    public string Name { get; set; }
}
```

## 🔍 Custom Roslyn Analyzers

### Code Quality Analyzer
```csharp
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Diagnostics;
using System.Collections.Immutable;
using System.Linq;

[DiagnosticAnalyzer(LanguageNames.CSharp)]
public class UnityBestPracticesAnalyzer : DiagnosticAnalyzer
{
    // Diagnostic descriptors
    public static readonly DiagnosticDescriptor UnityUpdateMethodRule = new DiagnosticDescriptor(
        "UBP001",
        "Avoid empty Update methods",
        "Update method '{0}' is empty and should be removed to improve performance",
        "Performance",
        DiagnosticSeverity.Warning,
        isEnabledByDefault: true,
        description: "Empty Update methods still consume CPU cycles in Unity. Remove them if not needed.");
    
    public static readonly DiagnosticDescriptor UnityFindGameObjectRule = new DiagnosticDescriptor(
        "UBP002",
        "Avoid using GameObject.Find in Update methods",
        "GameObject.Find call in Update method '{0}' can cause performance issues",
        "Performance",
        DiagnosticSeverity.Warning,
        isEnabledByDefault: true,
        description: "GameObject.Find is expensive and should not be called repeatedly in Update methods.");
    
    public static readonly DiagnosticDescriptor UnitySerializeFieldRule = new DiagnosticDescriptor(
        "UBP003",
        "Use [SerializeField] instead of public fields",
        "Field '{0}' should use [SerializeField] attribute instead of being public",
        "Design",
        DiagnosticSeverity.Info,
        isEnabledByDefault: true,
        description: "Use [SerializeField] for Unity serialization instead of public fields to maintain encapsulation.");
    
    public static readonly DiagnosticDescriptor UnityStringComparisonRule = new DiagnosticDescriptor(
        "UBP004",
        "Use CompareTag instead of string comparison for tags",
        "Use CompareTag('{0}') instead of string comparison for better performance",
        "Performance",
        DiagnosticSeverity.Info,
        isEnabledByDefault: true,
        description: "CompareTag is more efficient than string comparison for Unity tags.");
    
    public override ImmutableArray<DiagnosticDescriptor> SupportedDiagnostics =>
        ImmutableArray.Create(UnityUpdateMethodRule, UnityFindGameObjectRule, 
                             UnitySerializeFieldRule, UnityStringComparisonRule);
    
    public override void Initialize(AnalysisContext context)
    {
        context.ConfigureGeneratedCodeAnalysis(GeneratedCodeAnalysisFlags.None);
        context.EnableConcurrentExecution();
        context.RegisterSyntaxNodeAction(AnalyzeMethod, SyntaxKind.MethodDeclaration);
        context.RegisterSyntaxNodeAction(AnalyzeField, SyntaxKind.FieldDeclaration);
        context.RegisterSyntaxNodeAction(AnalyzeBinaryExpression, SyntaxKind.EqualsExpression);
    }
    
    private static void AnalyzeMethod(SyntaxNodeAnalysisContext context)
    {
        var methodDeclaration = (MethodDeclarationSyntax)context.Node;
        var methodName = methodDeclaration.Identifier.Text;
        
        // Check for empty Update methods
        if (IsUnityUpdateMethod(methodName) && IsMethodEmpty(methodDeclaration))
        {
            var diagnostic = Diagnostic.Create(UnityUpdateMethodRule,
                methodDeclaration.Identifier.GetLocation(),
                methodName);
            context.ReportDiagnostic(diagnostic);
        }
        
        // Check for GameObject.Find in Update methods
        if (IsUnityUpdateMethod(methodName))
        {
            CheckForGameObjectFind(context, methodDeclaration);
        }
    }
    
    private static void AnalyzeField(SyntaxNodeAnalysisContext context)
    {
        var fieldDeclaration = (FieldDeclarationSyntax)context.Node;
        
        // Check if field is public and could use [SerializeField] instead
        if (IsUnityMonoBehaviourField(context, fieldDeclaration) && 
            fieldDeclaration.Modifiers.Any(SyntaxKind.PublicKeyword) &&
            !HasSerializeFieldAttribute(fieldDeclaration))
        {
            foreach (var variable in fieldDeclaration.Declaration.Variables)
            {
                var diagnostic = Diagnostic.Create(UnitySerializeFieldRule,
                    variable.GetLocation(),
                    variable.Identifier.Text);
                context.ReportDiagnostic(diagnostic);
            }
        }
    }
    
    private static void AnalyzeBinaryExpression(SyntaxNodeAnalysisContext context)
    {
        var binaryExpression = (BinaryExpressionSyntax)context.Node;
        
        // Check for tag string comparisons
        if (IsTagStringComparison(binaryExpression))
        {
            var tagValue = GetTagValue(binaryExpression);
            if (!string.IsNullOrEmpty(tagValue))
            {
                var diagnostic = Diagnostic.Create(UnityStringComparisonRule,
                    binaryExpression.GetLocation(),
                    tagValue);
                context.ReportDiagnostic(diagnostic);
            }
        }
    }
    
    private static bool IsUnityUpdateMethod(string methodName)
    {
        return methodName == "Update" || methodName == "FixedUpdate" || 
               methodName == "LateUpdate" || methodName == "OnGUI";
    }
    
    private static bool IsMethodEmpty(MethodDeclarationSyntax method)
    {
        if (method.Body == null) return false;
        
        var statements = method.Body.Statements;
        return statements.Count == 0 || 
               statements.All(s => s.IsKind(SyntaxKind.EmptyStatement));
    }
    
    private static void CheckForGameObjectFind(SyntaxNodeAnalysisContext context, 
        MethodDeclarationSyntax method)
    {
        var findCalls = method.DescendantNodes()
            .OfType<InvocationExpressionSyntax>()
            .Where(inv => IsGameObjectFindCall(inv));
        
        foreach (var call in findCalls)
        {
            var diagnostic = Diagnostic.Create(UnityFindGameObjectRule,
                call.GetLocation(),
                method.Identifier.Text);
            context.ReportDiagnostic(diagnostic);
        }
    }
    
    private static bool IsGameObjectFindCall(InvocationExpressionSyntax invocation)
    {
        if (invocation.Expression is MemberAccessExpressionSyntax memberAccess)
        {
            return memberAccess.Expression.ToString() == "GameObject" &&
                   (memberAccess.Name.Identifier.Text == "Find" ||
                    memberAccess.Name.Identifier.Text == "FindWithTag" ||
                    memberAccess.Name.Identifier.Text == "FindGameObjectWithTag");
        }
        
        return false;
    }
    
    private static bool IsUnityMonoBehaviourField(SyntaxNodeAnalysisContext context, 
        FieldDeclarationSyntax field)
    {
        var classDeclaration = field.Ancestors().OfType<ClassDeclarationSyntax>().FirstOrDefault();
        if (classDeclaration == null) return false;
        
        var semanticModel = context.SemanticModel;
        var classSymbol = semanticModel.GetDeclaredSymbol(classDeclaration);
        
        return InheritsFromMonoBehaviour(classSymbol);
    }
    
    private static bool InheritsFromMonoBehaviour(INamedTypeSymbol classSymbol)
    {
        var baseType = classSymbol?.BaseType;
        while (baseType != null)
        {
            if (baseType.Name == "MonoBehaviour" && 
                baseType.ContainingNamespace.ToDisplayString() == "UnityEngine")
                return true;
            baseType = baseType.BaseType;
        }
        return false;
    }
    
    private static bool HasSerializeFieldAttribute(FieldDeclarationSyntax field)
    {
        return field.AttributeLists.Any(al =>
            al.Attributes.Any(a => a.Name.ToString() == "SerializeField"));
    }
    
    private static bool IsTagStringComparison(BinaryExpressionSyntax binary)
    {
        // Check if one side is gameObject.tag and the other is a string literal
        var left = binary.Left.ToString();
        var right = binary.Right.ToString();
        
        return (left.EndsWith(".tag") && right.StartsWith("\"")) ||
               (right.EndsWith(".tag") && left.StartsWith("\""));
    }
    
    private static string GetTagValue(BinaryExpressionSyntax binary)
    {
        var left = binary.Left.ToString();
        var right = binary.Right.ToString();
        
        if (left.StartsWith("\"") && left.EndsWith("\""))
            return left.Trim('"');
        if (right.StartsWith("\"") && right.EndsWith("\""))
            return right.Trim('"');
        
        return null;
    }
}

// Code fix provider for the analyzer
[ExportCodeFixProvider(LanguageNames.CSharp, Name = nameof(UnityBestPracticesCodeFixProvider)), Shared]
public class UnityBestPracticesCodeFixProvider : CodeFixProvider
{
    public sealed override ImmutableArray<string> FixableDiagnosticIds =>
        ImmutableArray.Create(UnityBestPracticesAnalyzer.UnityUpdateMethodRule.Id,
                             UnityBestPracticesAnalyzer.UnitySerializeFieldRule.Id,
                             UnityBestPracticesAnalyzer.UnityStringComparisonRule.Id);
    
    public sealed override FixAllProvider GetFixAllProvider() => WellKnownFixAllProviders.BatchFixer;
    
    public sealed override async Task RegisterCodeFixesAsync(CodeFixContext context)
    {
        var root = await context.Document.GetSyntaxRootAsync(context.CancellationToken).ConfigureAwait(false);
        
        foreach (var diagnostic in context.Diagnostics)
        {
            switch (diagnostic.Id)
            {
                case "UBP001": // Empty Update method
                    RegisterRemoveMethodFix(context, root, diagnostic);
                    break;
                case "UBP003": // SerializeField
                    RegisterSerializeFieldFix(context, root, diagnostic);
                    break;
                case "UBP004": // CompareTag
                    RegisterCompareTagFix(context, root, diagnostic);
                    break;
            }
        }
    }
    
    private void RegisterRemoveMethodFix(CodeFixContext context, SyntaxNode root, Diagnostic diagnostic)
    {
        var diagnosticSpan = diagnostic.Location.SourceSpan;
        var methodDeclaration = root.FindToken(diagnosticSpan.Start).Parent.AncestorsAndSelf()
            .OfType<MethodDeclarationSyntax>().FirstOrDefault();
        
        if (methodDeclaration != null)
        {
            var action = CodeAction.Create(
                title: "Remove empty Update method",
                createChangedDocument: c => RemoveMethod(context.Document, methodDeclaration, c),
                equivalenceKey: "RemoveEmptyUpdateMethod");
            
            context.RegisterCodeFix(action, diagnostic);
        }
    }
    
    private void RegisterSerializeFieldFix(CodeFixContext context, SyntaxNode root, Diagnostic diagnostic)
    {
        var diagnosticSpan = diagnostic.Location.SourceSpan;
        var fieldDeclaration = root.FindToken(diagnosticSpan.Start).Parent.AncestorsAndSelf()
            .OfType<FieldDeclarationSyntax>().FirstOrDefault();
        
        if (fieldDeclaration != null)
        {
            var action = CodeAction.Create(
                title: "Use [SerializeField] attribute",
                createChangedDocument: c => AddSerializeFieldAttribute(context.Document, fieldDeclaration, c),
                equivalenceKey: "AddSerializeFieldAttribute");
            
            context.RegisterCodeFix(action, diagnostic);
        }
    }
    
    private void RegisterCompareTagFix(CodeFixContext context, SyntaxNode root, Diagnostic diagnostic)
    {
        var diagnosticSpan = diagnostic.Location.SourceSpan;
        var binaryExpression = root.FindToken(diagnosticSpan.Start).Parent.AncestorsAndSelf()
            .OfType<BinaryExpressionSyntax>().FirstOrDefault();
        
        if (binaryExpression != null)
        {
            var action = CodeAction.Create(
                title: "Use CompareTag method",
                createChangedDocument: c => ReplaceWithCompareTag(context.Document, binaryExpression, c),
                equivalenceKey: "ReplaceWithCompareTag");
            
            context.RegisterCodeFix(action, diagnostic);
        }
    }
    
    private async Task<Document> RemoveMethod(Document document, MethodDeclarationSyntax method, 
        CancellationToken cancellationToken)
    {
        var root = await document.GetSyntaxRootAsync(cancellationToken);
        var newRoot = root.RemoveNode(method, SyntaxRemoveOptions.KeepNoTrivia);
        return document.WithSyntaxRoot(newRoot);
    }
    
    private async Task<Document> AddSerializeFieldAttribute(Document document, FieldDeclarationSyntax field, 
        CancellationToken cancellationToken)
    {
        var root = await document.GetSyntaxRootAsync(cancellationToken);
        
        // Remove public modifier
        var newModifiers = field.Modifiers.Where(m => !m.IsKind(SyntaxKind.PublicKeyword));
        
        // Add private if no access modifier
        if (!newModifiers.Any(m => m.IsKind(SyntaxKind.PrivateKeyword) || 
                                  m.IsKind(SyntaxKind.ProtectedKeyword)))
        {
            newModifiers = newModifiers.Concat(new[] { SyntaxFactory.Token(SyntaxKind.PrivateKeyword) });
        }
        
        // Add SerializeField attribute
        var attribute = SyntaxFactory.Attribute(SyntaxFactory.IdentifierName("SerializeField"));
        var attributeList = SyntaxFactory.AttributeList(SyntaxFactory.SingletonSeparatedList(attribute));
        
        var newField = field
            .WithModifiers(SyntaxFactory.TokenList(newModifiers))
            .WithAttributeLists(field.AttributeLists.Add(attributeList));
        
        var newRoot = root.ReplaceNode(field, newField);
        return document.WithSyntaxRoot(newRoot);
    }
    
    private async Task<Document> ReplaceWithCompareTag(Document document, BinaryExpressionSyntax binary, 
        CancellationToken cancellationToken)
    {
        var root = await document.GetSyntaxRootAsync(cancellationToken);
        
        // Extract tag value and object reference
        var left = binary.Left.ToString();
        var right = binary.Right.ToString();
        
        string objectRef, tagValue;
        if (left.EndsWith(".tag"))
        {
            objectRef = left.Substring(0, left.Length - 4);
            tagValue = right.Trim('"');
        }
        else
        {
            objectRef = right.Substring(0, right.Length - 4);
            tagValue = left.Trim('"');
        }
        
        // Create CompareTag invocation
        var compareTagCall = SyntaxFactory.InvocationExpression(
            SyntaxFactory.MemberAccessExpression(
                SyntaxKind.SimpleMemberAccessExpression,
                SyntaxFactory.ParseExpression(objectRef),
                SyntaxFactory.IdentifierName("CompareTag")))
            .WithArgumentList(SyntaxFactory.ArgumentList(
                SyntaxFactory.SingletonSeparatedList(
                    SyntaxFactory.Argument(SyntaxFactory.LiteralExpression(
                        SyntaxKind.StringLiteralExpression,
                        SyntaxFactory.Literal(tagValue))))));
        
        var newRoot = root.ReplaceNode(binary, compareTagCall);
        return document.WithSyntaxRoot(newRoot);
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Intelligent Code Generation
- **Context-Aware Generators**: AI-powered source generators that understand project context
- **Pattern Recognition**: Machine learning-based identification of code generation opportunities
- **Custom Template Creation**: AI-generated source generator templates for specific use cases

### Advanced Code Analysis
- **Deep Semantic Analysis**: AI-enhanced analyzers that understand code intent and business logic
- **Performance Prediction**: Machine learning models for predicting performance impacts
- **Best Practice Enforcement**: AI-driven code quality rules based on project-specific patterns

### Automated Refactoring
- **Smart Code Fixes**: AI-generated code fix providers for complex refactoring scenarios
- **Architecture Improvements**: Automated suggestions for architectural enhancements
- **Technical Debt Detection**: ML-based identification and resolution of technical debt

## 💡 Key Highlights

- **Master Source Generators** for compile-time code generation and productivity improvements
- **Implement Custom Analyzers** for enforcing project-specific code quality standards
- **Create Automated Systems** for serialization, data binding, and boilerplate reduction
- **Build Development Tools** that enhance team productivity and code consistency
- **Optimize Compile-Time Performance** with efficient syntax analysis and generation
- **Leverage AI Integration** for intelligent code generation and analysis
- **Focus on Maintainability** with clear, documented generator and analyzer implementations
- **Implement Comprehensive Testing** for source generators and analyzers to ensure reliability