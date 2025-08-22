# @i-AI-Documentation-Generation-Pipeline - Automated Technical Writing Systems

## 🎯 Learning Objectives
- Build automated documentation generation pipelines using AI/LLM technology
- Create sustainable technical writing workflows that scale with project complexity
- Develop intelligent content management systems for evolving documentation needs
- Master integration of AI tools with existing documentation platforms and workflows

## 🔧 Core Documentation Automation Architecture

### AI-Powered Code Documentation System
```csharp
using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using UnityEditor;

public class AIDocumentationGenerator
{
    [MenuItem("Documentation/Generate AI Documentation")]
    public static void GenerateProjectDocumentation()
    {
        var documentationPipeline = new DocumentationPipeline();
        documentationPipeline.GenerateComprehensiveDocumentation();
    }
}

public class DocumentationPipeline
{
    private readonly string outputPath = "Documentation/Generated/";
    private readonly List<Type> documentedTypes = new List<Type>();
    
    public void GenerateComprehensiveDocumentation()
    {
        CreateOutputDirectories();
        
        // Generate different types of documentation
        GenerateAPIDocumentation();
        GenerateArchitectureDocumentation();
        GenerateUserGuides();
        GenerateSetupInstructions();
        
        Debug.Log($"Documentation generated at: {Path.GetFullPath(outputPath)}");
    }
    
    private void GenerateAPIDocumentation()
    {
        var apiDocs = new StringBuilder();
        apiDocs.AppendLine("# API Documentation");
        apiDocs.AppendLine();
        
        // Scan project for MonoBehaviour classes
        var monoBehaviours = GetProjectMonoBehaviours();
        
        foreach (var type in monoBehaviours)
        {
            var classDoc = GenerateClassDocumentation(type);
            apiDocs.AppendLine(classDoc);
            documentedTypes.Add(type);
        }
        
        // Scan for ScriptableObjects
        var scriptableObjects = GetProjectScriptableObjects();
        
        foreach (var type in scriptableObjects)
        {
            var classDoc = GenerateClassDocumentation(type);
            apiDocs.AppendLine(classDoc);
            documentedTypes.Add(type);
        }
        
        File.WriteAllText(Path.Combine(outputPath, "API_Documentation.md"), apiDocs.ToString());
    }
    
    private string GenerateClassDocumentation(Type type)
    {
        var doc = new StringBuilder();
        doc.AppendLine($"## {type.Name}");
        doc.AppendLine();
        
        // Add class summary from XML comments if available
        var classSummary = ExtractXmlDocumentation(type);
        if (!string.IsNullOrEmpty(classSummary))
        {
            doc.AppendLine($"**Summary:** {classSummary}");
            doc.AppendLine();
        }
        
        // Add inheritance hierarchy
        if (type.BaseType != typeof(object) && type.BaseType != typeof(MonoBehaviour) && type.BaseType != typeof(ScriptableObject))
        {
            doc.AppendLine($"**Inherits from:** `{type.BaseType.Name}`");
            doc.AppendLine();
        }
        
        // Document serialized fields
        var serializedFields = GetSerializedFields(type);
        if (serializedFields.Count > 0)
        {
            doc.AppendLine("### Serialized Fields");
            doc.AppendLine();
            foreach (var field in serializedFields)
            {
                var fieldDoc = ExtractFieldDocumentation(field);
                doc.AppendLine($"- **{field.Name}** (`{field.FieldType.Name}`): {fieldDoc}");
            }
            doc.AppendLine();
        }
        
        // Document public methods
        var publicMethods = GetPublicMethods(type);
        if (publicMethods.Count > 0)
        {
            doc.AppendLine("### Public Methods");
            doc.AppendLine();
            foreach (var method in publicMethods)
            {
                var methodDoc = GenerateMethodDocumentation(method);
                doc.AppendLine(methodDoc);
            }
        }
        
        // Add usage examples
        var usageExample = GenerateUsageExample(type);
        if (!string.IsNullOrEmpty(usageExample))
        {
            doc.AppendLine("### Usage Example");
            doc.AppendLine();
            doc.AppendLine("```csharp");
            doc.AppendLine(usageExample);
            doc.AppendLine("```");
            doc.AppendLine();
        }
        
        return doc.ToString();
    }
    
    private string GenerateMethodDocumentation(MethodInfo method)
    {
        var doc = new StringBuilder();
        doc.AppendLine($"#### {method.Name}");
        doc.AppendLine();
        
        var methodSummary = ExtractXmlDocumentation(method);
        if (!string.IsNullOrEmpty(methodSummary))
        {
            doc.AppendLine(methodSummary);
            doc.AppendLine();
        }
        
        // Method signature
        var parameters = string.Join(", ", Array.ConvertAll(method.GetParameters(), 
            p => $"{p.ParameterType.Name} {p.Name}"));
        doc.AppendLine($"**Signature:** `{method.ReturnType.Name} {method.Name}({parameters})`");
        doc.AppendLine();
        
        // Parameter documentation
        var methodParams = method.GetParameters();
        if (methodParams.Length > 0)
        {
            doc.AppendLine("**Parameters:**");
            foreach (var param in methodParams)
            {
                var paramDoc = ExtractParameterDocumentation(method, param.Name);
                doc.AppendLine($"- `{param.Name}` ({param.ParameterType.Name}): {paramDoc}");
            }
            doc.AppendLine();
        }
        
        // Return value documentation
        if (method.ReturnType != typeof(void))
        {
            var returnDoc = ExtractReturnDocumentation(method);
            doc.AppendLine($"**Returns:** {returnDoc}");
            doc.AppendLine();
        }
        
        return doc.ToString();
    }
    
    private List<Type> GetProjectMonoBehaviours()
    {
        var types = new List<Type>();
        var assemblies = System.AppDomain.CurrentDomain.GetAssemblies();
        
        foreach (var assembly in assemblies)
        {
            if (assembly.FullName.Contains("Assembly-CSharp"))
            {
                try
                {
                    foreach (var type in assembly.GetTypes())
                    {
                        if (type.IsSubclassOf(typeof(MonoBehaviour)) && !type.IsAbstract)
                        {
                            types.Add(type);
                        }
                    }
                }
                catch (ReflectionTypeLoadException)
                {
                    // Handle cases where types can't be loaded
                    continue;
                }
            }
        }
        
        return types;
    }
    
    private string GenerateUsageExample(Type type)
    {
        // This would integrate with AI service to generate contextual usage examples
        // For now, return a basic template
        if (type.IsSubclassOf(typeof(MonoBehaviour)))
        {
            return $@"// Add {type.Name} component to a GameObject
var gameObject = new GameObject(""{type.Name} Example"");
var component = gameObject.AddComponent<{type.Name}>();

// Configure component properties
// component.SomeProperty = someValue;";
        }
        
        return "";
    }
}
```

### AI-Enhanced Documentation Content Generation
```python
import openai
import os
import json
import re
from pathlib import Path
from typing import List, Dict, Optional

class AIDocumentationWriter:
    def __init__(self, api_key: str, project_path: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.project_path = Path(project_path)
        self.documentation_templates = self.load_templates()
    
    def generate_comprehensive_documentation(self, code_files: List[str]):
        """Generate comprehensive documentation for Unity project"""
        documentation_suite = {
            'api_reference': {},
            'user_guides': {},
            'architecture_docs': {},
            'setup_instructions': {},
            'troubleshooting': {}
        }
        
        for file_path in code_files:
            if self.is_unity_script(file_path):
                code_content = self.read_file(file_path)
                
                # Generate API documentation
                api_docs = self.generate_api_documentation(code_content, file_path)
                documentation_suite['api_reference'][file_path] = api_docs
                
                # Generate user guide if it's a user-facing component
                if self.is_user_facing_component(code_content):
                    user_guide = self.generate_user_guide(code_content, file_path)
                    documentation_suite['user_guides'][file_path] = user_guide
        
        # Generate architecture documentation
        architecture_docs = self.generate_architecture_documentation(code_files)
        documentation_suite['architecture_docs'] = architecture_docs
        
        # Generate setup and troubleshooting docs
        setup_docs = self.generate_setup_documentation(code_files)
        documentation_suite['setup_instructions'] = setup_docs
        
        troubleshooting_docs = self.generate_troubleshooting_documentation(code_files)
        documentation_suite['troubleshooting'] = troubleshooting_docs
        
        return documentation_suite
    
    def generate_api_documentation(self, code_content: str, file_path: str) -> str:
        """Generate API documentation for a Unity script"""
        api_prompt = f"""
        Generate comprehensive API documentation for this Unity C# script:
        
        File: {file_path}
        Code:
        {code_content}
        
        Create documentation that includes:
        1. Class overview and purpose
        2. Public properties and their usage
        3. Public methods with parameters and return values
        4. Unity-specific lifecycle methods (Start, Update, etc.)
        5. Serialized fields visible in Inspector
        6. Code examples showing typical usage
        7. Performance considerations
        8. Common use cases and scenarios
        
        Format as markdown with clear sections and code examples.
        Focus on practical usage for other developers.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": api_prompt}],
            max_tokens=1500,
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    def generate_user_guide(self, code_content: str, file_path: str) -> str:
        """Generate user-friendly guide for Unity components"""
        user_guide_prompt = f"""
        Create a user guide for this Unity component:
        
        File: {file_path}
        Code:
        {code_content}
        
        Write a guide that includes:
        1. What this component does (non-technical explanation)
        2. How to add it to a GameObject
        3. Inspector settings and what they control
        4. Step-by-step setup instructions
        5. Common configuration scenarios
        6. Troubleshooting common issues
        7. Tips and best practices
        8. Visual aids descriptions (where helpful)
        
        Write for game designers and artists who may not be programmers.
        Use clear, friendly language with practical examples.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_guide_prompt}],
            max_tokens=1200,
            temperature=0.4
        )
        
        return response.choices[0].message.content
    
    def generate_architecture_documentation(self, code_files: List[str]) -> str:
        """Generate high-level architecture documentation"""
        # Analyze code files to understand project structure
        project_analysis = self.analyze_project_structure(code_files)
        
        architecture_prompt = f"""
        Generate architecture documentation for this Unity project:
        
        Project Analysis:
        {json.dumps(project_analysis, indent=2)}
        
        Create documentation covering:
        1. Overall project architecture and design patterns
        2. Core system interactions and dependencies
        3. Data flow between major components
        4. Key abstractions and interfaces
        5. Performance architecture decisions
        6. Scalability considerations
        7. Extension points for future development
        8. Technical debt and areas for improvement
        
        Focus on high-level design decisions and system relationships.
        Include diagrams descriptions where helpful.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": architecture_prompt}],
            max_tokens=1800,
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    def generate_setup_documentation(self, code_files: List[str]) -> str:
        """Generate project setup and installation documentation"""
        setup_prompt = f"""
        Generate comprehensive setup documentation for this Unity project:
        
        Based on the code structure and dependencies, create setup documentation including:
        1. Unity version requirements and installation
        2. Required packages and dependencies
        3. Project import and configuration steps
        4. Platform-specific setup requirements
        5. Development environment configuration
        6. Build system setup and configuration
        7. Version control setup (if applicable)
        8. Team collaboration setup instructions
        9. Common setup troubleshooting
        10. Verification steps to ensure everything works
        
        Write clear, step-by-step instructions suitable for new team members.
        Include command line examples and Unity Editor instructions.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": setup_prompt}],
            max_tokens=1400,
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    def generate_troubleshooting_documentation(self, code_files: List[str]) -> str:
        """Generate troubleshooting and FAQ documentation"""
        troubleshooting_prompt = f"""
        Generate troubleshooting documentation for this Unity project:
        
        Create a comprehensive troubleshooting guide covering:
        1. Common build errors and solutions
        2. Runtime error patterns and fixes
        3. Performance issues and optimization tips
        4. Platform-specific problems and workarounds
        5. Unity Editor issues and solutions
        6. Version control conflicts and resolutions
        7. Package manager problems
        8. Debugging techniques and tools
        9. FAQ section with common questions
        10. When and how to seek additional help
        
        Format as a searchable reference with clear problem/solution pairs.
        Include code examples and Unity Editor screenshots descriptions.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": troubleshooting_prompt}],
            max_tokens=1600,
            temperature=0.4
        )
        
        return response.choices[0].message.content
    
    def analyze_project_structure(self, code_files: List[str]) -> Dict:
        """Analyze project structure to understand architecture"""
        analysis = {
            'managers': [],
            'controllers': [],
            'ui_systems': [],
            'data_systems': [],
            'utilities': [],
            'interfaces': [],
            'patterns_detected': []
        }
        
        for file_path in code_files:
            if self.is_unity_script(file_path):
                code_content = self.read_file(file_path)
                file_name = Path(file_path).stem
                
                # Categorize files based on naming and content
                if 'manager' in file_name.lower():
                    analysis['managers'].append(file_name)
                elif 'controller' in file_name.lower():
                    analysis['controllers'].append(file_name)
                elif 'ui' in file_name.lower() or 'menu' in file_name.lower():
                    analysis['ui_systems'].append(file_name)
                elif 'data' in file_name.lower() or 'scriptableobject' in code_content.lower():
                    analysis['data_systems'].append(file_name)
                elif 'utility' in file_name.lower() or 'helper' in file_name.lower():
                    analysis['utilities'].append(file_name)
                
                # Detect interfaces
                if 'interface' in code_content.lower() or code_content.count('I') > 0:
                    analysis['interfaces'].append(file_name)
                
                # Detect design patterns
                if 'singleton' in code_content.lower():
                    analysis['patterns_detected'].append('Singleton')
                if 'observer' in code_content.lower() or 'event' in code_content.lower():
                    analysis['patterns_detected'].append('Observer/Events')
                if 'factory' in code_content.lower():
                    analysis['patterns_detected'].append('Factory')
                if 'pool' in code_content.lower():
                    analysis['patterns_detected'].append('Object Pooling')
        
        return analysis
    
    def is_unity_script(self, file_path: str) -> bool:
        """Check if file is a Unity C# script"""
        return file_path.endswith('.cs') and 'Assets' in file_path
    
    def is_user_facing_component(self, code_content: str) -> bool:
        """Determine if component is user-facing (has serialized fields)"""
        return '[SerializeField]' in code_content or 'public ' in code_content
    
    def read_file(self, file_path: str) -> str:
        """Read file content safely"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""
    
    def save_documentation_suite(self, documentation_suite: Dict, output_path: str):
        """Save generated documentation to organized file structure"""
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save API reference
        api_dir = output_dir / "api"
        api_dir.mkdir(exist_ok=True)
        for file_path, content in documentation_suite['api_reference'].items():
            file_name = Path(file_path).stem + "_API.md"
            with open(api_dir / file_name, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Save user guides
        guides_dir = output_dir / "guides"
        guides_dir.mkdir(exist_ok=True)
        for file_path, content in documentation_suite['user_guides'].items():
            file_name = Path(file_path).stem + "_Guide.md"
            with open(guides_dir / file_name, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Save architecture docs
        with open(output_dir / "Architecture.md", 'w', encoding='utf-8') as f:
            f.write(documentation_suite['architecture_docs'])
        
        # Save setup instructions
        with open(output_dir / "Setup.md", 'w', encoding='utf-8') as f:
            f.write(documentation_suite['setup_instructions'])
        
        # Save troubleshooting guide
        with open(output_dir / "Troubleshooting.md", 'w', encoding='utf-8') as f:
            f.write(documentation_suite['troubleshooting'])

# Usage example
def generate_project_documentation():
    doc_writer = AIDocumentationWriter("your-api-key", "/path/to/unity/project")
    
    # Get all Unity script files
    unity_scripts = []
    project_assets = Path("/path/to/unity/project/Assets")
    for cs_file in project_assets.rglob("*.cs"):
        unity_scripts.append(str(cs_file))
    
    # Generate comprehensive documentation
    documentation = doc_writer.generate_comprehensive_documentation(unity_scripts)
    
    # Save to organized structure
    doc_writer.save_documentation_suite(documentation, "/path/to/documentation/output")
    
    print(f"Documentation generated for {len(unity_scripts)} files")
    return documentation
```

## 💡 Advanced Documentation Workflows

### Living Documentation System
```python
import git
import hashlib
from datetime import datetime
from pathlib import Path

class LivingDocumentationSystem:
    def __init__(self, project_path: str, doc_output_path: str):
        self.project_path = Path(project_path)
        self.doc_output_path = Path(doc_output_path)
        self.repo = git.Repo(project_path)
        self.doc_cache = {}
        self.load_documentation_cache()
    
    def update_documentation_on_changes(self):
        """Update documentation only for changed files"""
        changed_files = self.get_changed_files()
        unity_scripts = [f for f in changed_files if f.endswith('.cs') and 'Assets' in f]
        
        if not unity_scripts:
            print("No Unity scripts changed, skipping documentation update")
            return
        
        print(f"Updating documentation for {len(unity_scripts)} changed files")
        
        doc_writer = AIDocumentationWriter("your-api-key", str(self.project_path))
        
        for script_path in unity_scripts:
            # Check if file actually needs documentation update
            file_hash = self.get_file_hash(script_path)
            
            if script_path in self.doc_cache and self.doc_cache[script_path]['hash'] == file_hash:
                print(f"Skipping {script_path} - no changes detected")
                continue
            
            print(f"Generating documentation for {script_path}")
            
            # Generate updated documentation
            code_content = doc_writer.read_file(script_path)
            api_docs = doc_writer.generate_api_documentation(code_content, script_path)
            
            # Save documentation
            doc_file_path = self.get_documentation_path(script_path)
            doc_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(doc_file_path, 'w', encoding='utf-8') as f:
                f.write(api_docs)
            
            # Update cache
            self.doc_cache[script_path] = {
                'hash': file_hash,
                'last_updated': datetime.now().isoformat(),
                'doc_path': str(doc_file_path)
            }
        
        self.save_documentation_cache()
        self.update_documentation_index()
    
    def get_changed_files(self) -> List[str]:
        """Get list of files changed since last documentation update"""
        # Get changed files from git
        changed_files = []
        
        # Get staged changes
        staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
        changed_files.extend(staged_files)
        
        # Get unstaged changes
        unstaged_files = [item.a_path for item in self.repo.index.diff(None)]
        changed_files.extend(unstaged_files)
        
        # Get untracked files
        untracked_files = self.repo.untracked_files
        changed_files.extend(untracked_files)
        
        return list(set(changed_files))
    
    def get_file_hash(self, file_path: str) -> str:
        """Get hash of file content for change detection"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except FileNotFoundError:
            return ""
    
    def get_documentation_path(self, script_path: str) -> Path:
        """Get output path for documentation file"""
        relative_path = Path(script_path).relative_to(self.project_path / "Assets")
        doc_path = self.doc_output_path / "api" / relative_path.with_suffix(".md")
        return doc_path
    
    def update_documentation_index(self):
        """Generate index file linking all documentation"""
        index_content = ["# Project Documentation Index", ""]
        index_content.append(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        index_content.append("")
        
        # Group documentation by category
        categories = {
            'Managers': [],
            'Controllers': [],
            'UI Systems': [],
            'Utilities': [],
            'Other': []
        }
        
        for script_path, cache_info in self.doc_cache.items():
            doc_path = Path(cache_info['doc_path'])
            relative_doc_path = doc_path.relative_to(self.doc_output_path)
            
            script_name = Path(script_path).stem
            
            # Categorize based on naming
            if 'manager' in script_name.lower():
                categories['Managers'].append((script_name, relative_doc_path))
            elif 'controller' in script_name.lower():
                categories['Controllers'].append((script_name, relative_doc_path))
            elif 'ui' in script_name.lower():
                categories['UI Systems'].append((script_name, relative_doc_path))
            elif 'util' in script_name.lower() or 'helper' in script_name.lower():
                categories['Utilities'].append((script_name, relative_doc_path))
            else:
                categories['Other'].append((script_name, relative_doc_path))
        
        # Generate index content
        for category, items in categories.items():
            if items:
                index_content.append(f"## {category}")
                index_content.append("")
                for script_name, doc_path in sorted(items):
                    index_content.append(f"- [{script_name}]({doc_path})")
                index_content.append("")
        
        # Save index file
        index_path = self.doc_output_path / "README.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(index_content))
    
    def load_documentation_cache(self):
        """Load documentation cache from file"""
        cache_file = self.doc_output_path / ".doc_cache.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                self.doc_cache = json.load(f)
    
    def save_documentation_cache(self):
        """Save documentation cache to file"""
        cache_file = self.doc_output_path / ".doc_cache.json"
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump(self.doc_cache, f, indent=2)

# Usage in CI/CD or git hook
def setup_automated_documentation():
    living_docs = LivingDocumentationSystem(
        "/path/to/unity/project",
        "/path/to/documentation/output"
    )
    
    # This would be called by git hook or CI/CD pipeline
    living_docs.update_documentation_on_changes()
```

## 💡 Key Highlights

- **Automated code analysis** generates comprehensive API documentation from Unity scripts
- **AI-enhanced content creation** produces user-friendly guides and technical references
- **Living documentation system** maintains up-to-date docs through automated change detection
- **Multi-format output** supports various documentation platforms and consumption methods
- **Intelligent categorization** organizes documentation for easy navigation and discovery
- **Integration-ready design** works with existing development workflows and CI/CD pipelines

## 🎯 Documentation Maintenance Excellence

### Quality Assurance Automation
```python
class DocumentationQualityAssurance:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    def review_documentation_quality(self, doc_content: str, doc_type: str) -> Dict:
        """AI-powered documentation quality review"""
        review_prompt = f"""
        Review this {doc_type} documentation for quality and completeness:
        
        Documentation Content:
        {doc_content}
        
        Evaluate:
        1. Clarity and readability
        2. Technical accuracy
        3. Completeness of information
        4. Code example quality
        5. Structure and organization
        6. Consistency with style guide
        7. Accessibility for target audience
        8. Missing information or sections
        
        Provide specific improvement suggestions and a quality score (1-10).
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": review_prompt}],
            max_tokens=800,
            temperature=0.3
        )
        
        return {
            'review': response.choices[0].message.content,
            'timestamp': datetime.now().isoformat()
        }
    
    def suggest_documentation_improvements(self, existing_docs: List[str]) -> str:
        """Suggest systematic improvements to documentation suite"""
        improvement_prompt = f"""
        Analyze this documentation suite and suggest systematic improvements:
        
        Existing Documentation:
        {json.dumps(existing_docs, indent=2)}
        
        Suggest improvements for:
        1. Coverage gaps and missing documentation
        2. Consistency across different document types
        3. Navigation and discoverability improvements
        4. Integration with development workflow
        5. Maintenance and update processes
        6. User experience enhancements
        7. Technical writing best practices
        8. Documentation architecture improvements
        
        Provide actionable recommendations prioritized by impact.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": improvement_prompt}],
            max_tokens=1000,
            temperature=0.4
        )
        
        return response.choices[0].message.content

# Usage example
def maintain_documentation_quality():
    qa_system = DocumentationQualityAssurance("your-api-key")
    
    # Review existing documentation
    doc_files = list(Path("documentation").rglob("*.md"))
    
    for doc_file in doc_files:
        with open(doc_file, 'r') as f:
            content = f.read()
        
        review = qa_system.review_documentation_quality(content, "API")
        print(f"Quality review for {doc_file.name}:")
        print(review['review'])
```

This AI documentation generation pipeline creates maintainable, high-quality technical documentation that evolves with your Unity projects while ensuring consistency and comprehensiveness across all documentation types.