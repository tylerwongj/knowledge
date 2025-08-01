# @i-Reflection-Metaprogramming - Advanced Runtime Code Manipulation in C#

## 🎯 Learning Objectives
- Master reflection and metaprogramming techniques for dynamic code execution
- Implement attribute-driven programming and custom serialization systems
- Create code generation tools and dynamic proxy systems
- Build flexible plugin architectures and dependency injection containers

## 🔧 Advanced Reflection Techniques

### High-Performance Reflection with Caching
```csharp
using System;
using System.Collections.Generic;
using System.Collections.Concurrent;
using System.Reflection;
using System.Linq.Expressions;
using System.Linq;

public static class FastReflection
{
    private static readonly ConcurrentDictionary<string, Func<object, object[], object>> MethodCache
        = new ConcurrentDictionary<string, Func<object, object[], object>>();
    
    private static readonly ConcurrentDictionary<string, Func<object, object>> PropertyGetterCache
        = new ConcurrentDictionary<string, Func<object, object>>();
        
    private static readonly ConcurrentDictionary<string, Action<object, object>> PropertySetterCache
        = new ConcurrentDictionary<string, Action<object, object>>();
        
    private static readonly ConcurrentDictionary<Type, Func<object>> ConstructorCache
        = new ConcurrentDictionary<Type, Func<object>>();
    
    // Fast method invocation using compiled expressions
    public static object InvokeMethod(object instance, string methodName, params object[] parameters)
    {
        var type = instance.GetType();
        var key = $"{type.FullName}.{methodName}({string.Join(",", parameters.Select(p => p?.GetType().Name ?? "null"))})";
        
        var invoker = MethodCache.GetOrAdd(key, _ =>
        {
            var method = type.GetMethod(methodName, parameters.Select(p => p?.GetType()).ToArray());
            if (method == null)
                throw new MethodAccessException($"Method {methodName} not found on type {type.Name}");
            
            return CreateMethodInvoker(method);
        });
        
        return invoker(instance, parameters);
    }
    
    private static Func<object, object[], object> CreateMethodInvoker(MethodInfo method)
    {
        var instanceParam = Expression.Parameter(typeof(object), "instance");
        var parametersParam = Expression.Parameter(typeof(object[]), "parameters");
        
        var instanceCast = Expression.Convert(instanceParam, method.DeclaringType);
        
        var parameterExpressions = method.GetParameters()
            .Select((param, index) => Expression.Convert(
                Expression.ArrayIndex(parametersParam, Expression.Constant(index)),
                param.ParameterType))
            .ToArray();
        
        var methodCall = Expression.Call(instanceCast, method, parameterExpressions);
        
        Expression resultExpression;
        if (method.ReturnType == typeof(void))
        {
            resultExpression = Expression.Block(methodCall, Expression.Constant(null));
        }
        else
        {
            resultExpression = Expression.Convert(methodCall, typeof(object));
        }
        
        var lambda = Expression.Lambda<Func<object, object[], object>>(
            resultExpression, instanceParam, parametersParam);
            
        return lambda.Compile();
    }
    
    // Fast property access
    public static T GetProperty<T>(object instance, string propertyName)
    {
        var type = instance.GetType();
        var key = $"{type.FullName}.{propertyName}";
        
        var getter = PropertyGetterCache.GetOrAdd(key, _ =>
        {
            var property = type.GetProperty(propertyName);
            if (property == null || !property.CanRead)
                throw new PropertyAccessException($"Property {propertyName} not found or not readable on type {type.Name}");
            
            return CreatePropertyGetter(property);
        });
        
        return (T)getter(instance);
    }
    
    public static void SetProperty(object instance, string propertyName, object value)
    {
        var type = instance.GetType();
        var key = $"{type.FullName}.{propertyName}";
        
        var setter = PropertySetterCache.GetOrAdd(key, _ =>
        {
            var property = type.GetProperty(propertyName);
            if (property == null || !property.CanWrite)
                throw new PropertyAccessException($"Property {propertyName} not found or not writable on type {type.Name}");
            
            return CreatePropertySetter(property);
        });
        
        setter(instance, value);
    }
    
    private static Func<object, object> CreatePropertyGetter(PropertyInfo property)
    {
        var instanceParam = Expression.Parameter(typeof(object), "instance");
        var instanceCast = Expression.Convert(instanceParam, property.DeclaringType);
        var propertyAccess = Expression.Property(instanceCast, property);
        var resultCast = Expression.Convert(propertyAccess, typeof(object));
        
        var lambda = Expression.Lambda<Func<object, object>>(resultCast, instanceParam);
        return lambda.Compile();
    }
    
    private static Action<object, object> CreatePropertySetter(PropertyInfo property)
    {
        var instanceParam = Expression.Parameter(typeof(object), "instance");
        var valueParam = Expression.Parameter(typeof(object), "value");
        
        var instanceCast = Expression.Convert(instanceParam, property.DeclaringType);
        var valueCast = Expression.Convert(valueParam, property.PropertyType);
        var propertySet = Expression.Call(instanceCast, property.SetMethod, valueCast);
        
        var lambda = Expression.Lambda<Action<object, object>>(propertySet, instanceParam, valueParam);
        return lambda.Compile();
    }
    
    // Fast object creation
    public static T CreateInstance<T>() where T : new()
    {
        var factory = ConstructorCache.GetOrAdd(typeof(T), type =>
        {
            var constructor = type.GetConstructor(Type.EmptyTypes);
            if (constructor == null)
                throw new InvalidOperationException($"Type {type.Name} does not have a parameterless constructor");
            
            var newExpression = Expression.New(constructor);
            var lambda = Expression.Lambda<Func<object>>(newExpression);
            return lambda.Compile();
        });
        
        return (T)factory();
    }
    
    public static object CreateInstance(Type type, params object[] args)
    {
        var argTypes = args.Select(a => a?.GetType()).ToArray();
        var constructor = type.GetConstructor(argTypes);
        
        if (constructor == null)
            throw new InvalidOperationException($"Constructor not found for type {type.Name} with given arguments");
        
        return constructor.Invoke(args);
    }
}

// Custom attribute-driven object mapper
public class AttributeMapper
{
    [AttributeUsage(AttributeTargets.Property)]
    public class MapFromAttribute : Attribute
    {
        public string SourceProperty { get; }
        public Type ConverterType { get; set; }
        
        public MapFromAttribute(string sourceProperty)
        {
            SourceProperty = sourceProperty;
        }
    }
    
    [AttributeUsage(AttributeTargets.Property)]
    public class IgnoreAttribute : Attribute { }
    
    public interface IValueConverter
    {
        object Convert(object value, Type targetType);
    }
    
    public class StringToIntConverter : IValueConverter
    {
        public object Convert(object value, Type targetType)
        {
            if (value is string str && int.TryParse(str, out int result))
                return result;
            return 0;
        }
    }
    
    public static TTarget Map<TSource, TTarget>(TSource source) where TTarget : new()
    {
        var target = new TTarget();
        Map(source, target);
        return target;
    }
    
    public static void Map<TSource, TTarget>(TSource source, TTarget target)
    {
        var sourceType = typeof(TSource);
        var targetType = typeof(TTarget);
        
        var targetProperties = targetType.GetProperties(BindingFlags.Public | BindingFlags.Instance)
            .Where(p => p.CanWrite && !p.HasAttribute<IgnoreAttribute>());
        
        foreach (var targetProp in targetProperties)
        {
            var mapFromAttr = targetProp.GetCustomAttribute<MapFromAttribute>();
            var sourcePropertyName = mapFromAttr?.SourceProperty ?? targetProp.Name;
            
            var sourceProp = sourceType.GetProperty(sourcePropertyName);
            if (sourceProp?.CanRead != true) continue;
            
            var sourceValue = sourceProp.GetValue(source);
            if (sourceValue == null) continue;
            
            object convertedValue = sourceValue;
            
            // Apply converter if specified
            if (mapFromAttr?.ConverterType != null)
            {
                var converter = Activator.CreateInstance(mapFromAttr.ConverterType) as IValueConverter;
                convertedValue = converter?.Convert(sourceValue, targetProp.PropertyType) ?? sourceValue;
            }
            else if (sourceValue.GetType() != targetProp.PropertyType)
            {
                // Attempt basic type conversion
                try
                {
                    convertedValue = System.Convert.ChangeType(sourceValue, targetProp.PropertyType);
                }
                catch
                {
                    continue; // Skip if conversion fails
                }
            }
            
            targetProp.SetValue(target, convertedValue);
        }
    }
}

// Extension methods for reflection
public static class ReflectionExtensions
{
    public static bool HasAttribute<T>(this MemberInfo member) where T : Attribute
    {
        return member.GetCustomAttribute<T>() != null;
    }
    
    public static T GetAttribute<T>(this MemberInfo member) where T : Attribute
    {
        return member.GetCustomAttribute<T>();
    }
    
    public static IEnumerable<T> GetAttributes<T>(this MemberInfo member) where T : Attribute
    {
        return member.GetCustomAttributes<T>();
    }
    
    public static bool IsSubclassOfGeneric(this Type type, Type genericType)
    {
        while (type != null && type != typeof(object))
        {
            var current = type.IsGenericType ? type.GetGenericTypeDefinition() : type;
            if (genericType == current)
                return true;
            type = type.BaseType;
        }
        return false;
    }
    
    public static bool ImplementsInterface<T>(this Type type)
    {
        return typeof(T).IsAssignableFrom(type);
    }
    
    public static IEnumerable<Type> GetAllTypes(this Assembly assembly)
    {
        try
        {
            return assembly.GetTypes();
        }
        catch (ReflectionTypeLoadException ex)
        {
            return ex.Types.Where(t => t != null);
        }
    }
}
```

### Dynamic Code Generation and Compilation
```csharp
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.Emit;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;

public class DynamicCodeCompiler
{
    private readonly Dictionary<string, Assembly> compiledAssemblies;
    private readonly List<MetadataReference> defaultReferences;
    
    public DynamicCodeCompiler()
    {
        compiledAssemblies = new Dictionary<string, Assembly>();
        defaultReferences = new List<MetadataReference>
        {
            MetadataReference.CreateFromFile(typeof(object).Assembly.Location),
            MetadataReference.CreateFromFile(typeof(Console).Assembly.Location),
            MetadataReference.CreateFromFile(typeof(System.Runtime.AssemblyTargetedPatchBandAttribute).Assembly.Location),
            MetadataReference.CreateFromFile(typeof(Microsoft.CSharp.RuntimeBinder.CSharpArgumentInfo).Assembly.Location),
        };
    }
    
    public Assembly CompileCode(string code, string assemblyName = null, params string[] additionalReferences)
    {
        assemblyName = assemblyName ?? $"DynamicAssembly_{Guid.NewGuid():N}";
        
        if (compiledAssemblies.TryGetValue(assemblyName, out Assembly cached))
            return cached;
        
        var syntaxTree = CSharpSyntaxTree.ParseText(code);
        
        var references = new List<MetadataReference>(defaultReferences);
        foreach (var reference in additionalReferences)
        {
            references.Add(MetadataReference.CreateFromFile(reference));
        }
        
        var compilation = CSharpCompilation.Create(
            assemblyName,
            new[] { syntaxTree },
            references,
            new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary));
        
        using (var ms = new MemoryStream())
        {
            var result = compilation.Emit(ms);
            
            if (!result.Success)
            {
                var failures = result.Diagnostics
                    .Where(diagnostic => diagnostic.IsWarningAsError || diagnostic.Severity == DiagnosticSeverity.Error);
                
                var error = string.Join("\n", failures.Select(f => f.ToString()));
                throw new InvalidOperationException($"Compilation failed:\n{error}");
            }
            
            ms.Seek(0, SeekOrigin.Begin);
            var assembly = Assembly.Load(ms.ToArray());
            compiledAssemblies[assemblyName] = assembly;
            return assembly;
        }
    }
    
    public T CreateInstance<T>(string code, string typeName, string assemblyName = null)
    {
        var assembly = CompileCode(code, assemblyName);
        var type = assembly.GetType(typeName);
        
        if (type == null)
            throw new TypeLoadException($"Type {typeName} not found in compiled assembly");
        
        return (T)Activator.CreateInstance(type);
    }
    
    public object ExecuteMethod(string code, string typeName, string methodName, params object[] parameters)
    {
        var assembly = CompileCode(code);
        var type = assembly.GetType(typeName);
        var method = type.GetMethod(methodName);
        
        if (method.IsStatic)
        {
            return method.Invoke(null, parameters);
        }
        else
        {
            var instance = Activator.CreateInstance(type);
            return method.Invoke(instance, parameters);
        }
    }
}

// Code generation helper
public class CodeGenerator
{
    private readonly StringBuilder code;
    private int indentLevel;
    
    public CodeGenerator()
    {
        code = new StringBuilder();
        indentLevel = 0;
    }
    
    private string Indent => new string(' ', indentLevel * 4);
    
    public CodeGenerator Using(string namespaceName)
    {
        code.AppendLine($"using {namespaceName};");
        return this;
    }
    
    public CodeGenerator Namespace(string namespaceName)
    {
        code.AppendLine($"namespace {namespaceName}");
        code.AppendLine("{");
        indentLevel++;
        return this;
    }
    
    public CodeGenerator Class(string className, string baseClass = null, params string[] interfaces)
    {
        var inheritance = new List<string>();
        if (!string.IsNullOrEmpty(baseClass))
            inheritance.Add(baseClass);
        inheritance.AddRange(interfaces);
        
        var inheritanceClause = inheritance.Count > 0 ? $" : {string.Join(", ", inheritance)}" : "";
        
        code.AppendLine($"{Indent}public class {className}{inheritanceClause}");
        code.AppendLine($"{Indent}{{");
        indentLevel++;
        return this;
    }
    
    public CodeGenerator Method(string methodName, string returnType = "void", string accessibility = "public", 
        params (string type, string name)[] parameters)
    {
        var paramList = string.Join(", ", parameters.Select(p => $"{p.type} {p.name}"));
        code.AppendLine($"{Indent}{accessibility} {returnType} {methodName}({paramList})");
        code.AppendLine($"{Indent}{{");
        indentLevel++;
        return this;
    }
    
    public CodeGenerator Property(string propertyName, string type, bool hasGetter = true, bool hasSetter = true, 
        string accessibility = "public")
    {
        code.Append($"{Indent}{accessibility} {type} {propertyName} {{");
        
        if (hasGetter) code.Append(" get;");
        if (hasSetter) code.Append(" set;");
        
        code.AppendLine(" }");
        return this;
    }
    
    public CodeGenerator Field(string fieldName, string type, string accessibility = "private", object defaultValue = null)
    {
        var defaultValueStr = defaultValue != null ? $" = {FormatValue(defaultValue)}" : "";
        code.AppendLine($"{Indent}{accessibility} {type} {fieldName}{defaultValueStr};");
        return this;
    }
    
    public CodeGenerator Line(string codeLine)
    {
        code.AppendLine($"{Indent}{codeLine}");
        return this;
    }
    
    public CodeGenerator Raw(string rawCode)
    {
        code.AppendLine(rawCode);
        return this;
    }
    
    public CodeGenerator EndBlock()
    {
        indentLevel--;
        code.AppendLine($"{Indent}}}");
        return this;
    }
    
    private string FormatValue(object value)
    {
        return value switch
        {
            string s => $"\"{s}\"",
            char c => $"'{c}'",
            bool b => b.ToString().ToLower(),
            null => "null",
            _ => value.ToString()
        };
    }
    
    public override string ToString()
    {
        return code.ToString();
    }
}

// Example usage: Dynamic DTO generator
public class DtoGenerator
{
    private readonly DynamicCodeCompiler compiler;
    
    public DtoGenerator()
    {
        compiler = new DynamicCodeCompiler();
    }
    
    public Type GenerateDtoType(string className, Dictionary<string, Type> properties)
    {
        var generator = new CodeGenerator()
            .Using("System")
            .Using("System.ComponentModel.DataAnnotations")
            .Namespace("Generated")
            .Class(className);
        
        foreach (var prop in properties)
        {
            generator.Property(prop.Key, GetTypeString(prop.Value));
        }
        
        generator.EndBlock().EndBlock(); // End class and namespace
        
        var code = generator.ToString();
        var assembly = compiler.CompileCode(code);
        
        return assembly.GetType($"Generated.{className}");
    }
    
    private string GetTypeString(Type type)
    {
        if (type == typeof(int)) return "int";
        if (type == typeof(string)) return "string";
        if (type == typeof(bool)) return "bool";
        if (type == typeof(DateTime)) return "DateTime";
        if (type == typeof(decimal)) return "decimal";
        if (type == typeof(double)) return "double";
        if (type == typeof(float)) return "float";
        
        return type.Name;
    }
    
    public object CreateDto(Type dtoType, Dictionary<string, object> values)
    {
        var instance = Activator.CreateInstance(dtoType);
        
        foreach (var value in values)
        {
            var property = dtoType.GetProperty(value.Key);
            if (property?.CanWrite == true)
            {
                property.SetValue(instance, value.Value);
            }
        }
        
        return instance;
    }
}
```

## 🎮 Unity-Specific Metaprogramming

### Component System Automation
```csharp
using UnityEngine;
using System;
using System.Collections.Generic;
using System.Reflection;
using System.Linq;

// Attribute-driven component system
[AttributeUsage(AttributeTargets.Field)]
public class AutoInjectAttribute : Attribute
{
    public bool Required { get; set; } = true;
    public bool SearchChildren { get; set; } = false;
    public string ComponentName { get; set; }
}

[AttributeUsage(AttributeTargets.Method)]
public class EventHandlerAttribute : Attribute
{
    public string EventName { get; }
    
    public EventHandlerAttribute(string eventName)
    {
        EventName = eventName;
    }
}

[AttributeUsage(AttributeTargets.Method)]
public class UnityEventAttribute : Attribute
{
    public string EventType { get; }
    
    public UnityEventAttribute(string eventType)
    {
        EventType = eventType;
    }
}

public class ComponentAutoWiring : MonoBehaviour
{
    private static readonly Dictionary<Type, List<FieldInfo>> CachedFields = 
        new Dictionary<Type, List<FieldInfo>>();
    private static readonly Dictionary<Type, List<MethodInfo>> CachedMethods = 
        new Dictionary<Type, List<MethodInfo>>();
    
    protected virtual void Awake()
    {
        AutoInjectComponents();
        RegisterEventHandlers();
    }
    
    private void AutoInjectComponents()
    {
        var type = GetType();
        
        if (!CachedFields.TryGetValue(type, out var fields))
        {
            fields = type.GetFields(BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Instance)
                .Where(f => f.HasAttribute<AutoInjectAttribute>())
                .ToList();
            CachedFields[type] = fields;
        }
        
        foreach (var field in fields)
        {
            var attr = field.GetAttribute<AutoInjectAttribute>();
            var component = FindComponent(field.FieldType, attr);
            
            if (component != null)
            {
                field.SetValue(this, component);
            }
            else if (attr.Required)
            {
                Debug.LogError($"Required component {field.FieldType.Name} not found on {gameObject.name}");
            }
        }
    }
    
    private Component FindComponent(Type componentType, AutoInjectAttribute attr)
    {
        Component component = null;
        
        if (!string.IsNullOrEmpty(attr.ComponentName))
        {
            // Find by name
            var namedObject = attr.SearchChildren 
                ? transform.Find(attr.ComponentName)
                : GameObject.Find(attr.ComponentName)?.transform;
                
            component = namedObject?.GetComponent(componentType);
        }
        else
        {
            // Find by type
            component = attr.SearchChildren
                ? GetComponentInChildren(componentType)
                : GetComponent(componentType);
        }
        
        return component;
    }
    
    private void RegisterEventHandlers()
    {
        var type = GetType();
        
        if (!CachedMethods.TryGetValue(type, out var methods))
        {
            methods = type.GetMethods(BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Instance)
                .Where(m => m.HasAttribute<EventHandlerAttribute>() || m.HasAttribute<UnityEventAttribute>())
                .ToList();
            CachedMethods[type] = methods;
        }
        
        foreach (var method in methods)
        {
            RegisterMethod(method);
        }
    }
    
    private void RegisterMethod(MethodInfo method)
    {
        var eventHandler = method.GetAttribute<EventHandlerAttribute>();
        if (eventHandler != null)
        {
            RegisterCustomEventHandler(method, eventHandler.EventName);
        }
        
        var unityEvent = method.GetAttribute<UnityEventAttribute>();
        if (unityEvent != null)
        {
            RegisterUnityEventHandler(method, unityEvent.EventType);
        }
    }
    
    private void RegisterCustomEventHandler(MethodInfo method, string eventName)
    {
        // Custom event system registration
        EventManager.Instance?.Subscribe(eventName, CreateEventDelegate(method));
    }
    
    private void RegisterUnityEventHandler(MethodInfo method, string eventType)
    {
        // Unity event registration based on type
        switch (eventType.ToLower())
        {
            case "collision":
                // Register collision events
                break;
            case "trigger":
                // Register trigger events
                break;
        }
    }
    
    private Action<object> CreateEventDelegate(MethodInfo method)
    {
        return (data) =>
        {
            try
            {
                var parameters = method.GetParameters();
                if (parameters.Length == 0)
                {
                    method.Invoke(this, null);
                }
                else if (parameters.Length == 1)
                {
                    method.Invoke(this, new[] { data });
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error invoking event handler {method.Name}: {ex}");
            }
        };
    }
}

// Example usage
public class ExampleComponent : ComponentAutoWiring
{
    [AutoInject]
    private Rigidbody rigidBody;
    
    [AutoInject(SearchChildren = true)]
    private Animator animator;
    
    [AutoInject(ComponentName = "UI Canvas", Required = false)]
    private Canvas uiCanvas;
    
    [EventHandler("PlayerDied")]
    private void OnPlayerDied()
    {
        Debug.Log("Player died event received");
    }
    
    [EventHandler("ScoreChanged")]
    private void OnScoreChanged(int newScore)
    {
        Debug.Log($"Score changed to: {newScore}");
    }
    
    [UnityEvent("Collision")]
    private void HandleCollision(Collision collision)
    {
        Debug.Log($"Collision with: {collision.gameObject.name}");
    }
}

// Scriptable object generator
public class ScriptableObjectGenerator
{
    public static Type GenerateScriptableObjectType(string className, Dictionary<string, Type> properties)
    {
        var generator = new CodeGenerator()
            .Using("UnityEngine")
            .Using("System")
            .Namespace("Generated")
            .Class(className, "ScriptableObject");
        
        // Add CreateAssetMenu attribute
        generator.Line("[CreateAssetMenu(fileName = \"" + className + "\", menuName = \"Generated/" + className + "\")]");
        
        foreach (var prop in properties)
        {
            generator.Field(prop.Key.ToLower(), GetUnityTypeString(prop.Value), "public");
        }
        
        generator.EndBlock().EndBlock();
        
        var compiler = new DynamicCodeCompiler();
        var code = generator.ToString();
        var assembly = compiler.CompileCode(code, 
            typeof(UnityEngine.Object).Assembly.Location,
            typeof(UnityEngine.ScriptableObject).Assembly.Location);
        
        return assembly.GetType($"Generated.{className}");
    }
    
    private static string GetUnityTypeString(Type type)
    {
        if (type == typeof(Vector3)) return "Vector3";
        if (type == typeof(Vector2)) return "Vector2";
        if (type == typeof(Color)) return "Color";
        if (type == typeof(GameObject)) return "GameObject";
        if (type == typeof(Transform)) return "Transform";
        
        // Fallback to system types
        return type.Name.ToLower();
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Code Generation Automation
- **Dynamic Class Generation**: AI-generated class structures based on requirements
- **Attribute-Based Code**: Automated generation of boilerplate code using custom attributes
- **Template System**: AI-powered code template generation and customization

### Runtime Code Analysis
- **Performance Profiling**: AI analysis of reflection-heavy code for optimization opportunities
- **Type Safety Analysis**: Automated detection of potential runtime type errors
- **Memory Usage Optimization**: AI-assisted optimization of reflection caching strategies

### Plugin Architecture Enhancement
- **Dynamic Assembly Loading**: AI-optimized plugin loading and dependency resolution
- **Interface Generation**: Automated creation of plugin interfaces and contracts
- **Version Compatibility**: AI-driven compatibility analysis for dynamic assemblies

## 💡 Key Highlights

- **Master High-Performance Reflection** with expression trees and caching mechanisms
- **Implement Attribute-Driven Programming** for flexible and maintainable code architecture
- **Create Dynamic Code Compilation** systems for runtime code generation and execution
- **Build Unity-Specific Solutions** for component auto-wiring and dynamic object creation
- **Optimize Memory Usage** with efficient caching strategies for reflection operations
- **Leverage AI Integration** for automated code generation and analysis
- **Focus on Type Safety** while maintaining flexibility in dynamic scenarios
- **Implement Robust Error Handling** for reflection operations and dynamic code execution