# @01-Git Unity Best Practices

## 🎯 Learning Objectives
- Master Git workflows optimized for Unity game development
- Implement proper .gitignore and LFS configuration for Unity projects
- Leverage AI tools for automated Git operations and conflict resolution
- Build collaborative development practices for Unity teams

## 📁 Unity-Specific Git Configuration

### Essential .gitignore Setup
**Comprehensive Unity .gitignore**:
```gitignore
# Unity generated files
[Ll]ibrary/
[Tt]emp/
[Oo]bj/
[Bb]uild/
[Bb]uilds/
[Ll]ogs/
[Uu]ser[Ss]ettings/

# Unity3D cache and temp directories
[Uu]nity[Gg]enerated/
[Cc]rash[Rr]eports/
[Mm]emoryCaptures/

# Asset meta files should be tracked
# But ignore temp meta files
*.tmp.meta
*.tmp

# Unity3D generated meta files
*.pidb.meta
*.pdb.meta
*.mdb.meta

# Unity specific
*.unityproj
*.sln
*.userprefs
*.csproj
*.user
*.suo
*.userosscache
*.sln.docstates
*.unitypackage
*.app

# OS generated
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Visual Studio
.vs/
*.csproj
*.user
*.unityproj
*.pidb
*.booproj
*.svd
*.pdb
*.mdb

# Rider IDE
.idea/

# Plastic SCM (if using alternative VCS)
.plastic/

# TextMeshPro
Assets/TextMeshPro/

# Development tools
*.log
*.tmp
```

### Git LFS for Large Assets
**LFS Configuration for Unity Assets**:
```bash
# Initialize Git LFS
git lfs install

# Track large Unity assets
git lfs track "*.psd"
git lfs track "*.fbx"
git lfs track "*.tga"
git lfs track "*.png"
git lfs track "*.jpg"
git lfs track "*.mp3"
git lfs track "*.wav"
git lfs track "*.ogg"
git lfs track "*.mp4"
git lfs track "*.mov"
git lfs track "*.anim"
git lfs track "*.unity"
git lfs track "*.prefab"
git lfs track "*.mat"
git lfs track "*.asset"

# Commit .gitattributes
git add .gitattributes
git commit -m "Configure Git LFS for Unity assets"
```

**AI-Enhanced LFS Management**:
```bash
# AI-generated script to optimize LFS tracking
#!/bin/bash
# auto-lfs-setup.sh - AI-optimized LFS configuration

echo "🤖 AI-Enhanced Unity LFS Setup"

# Analyze project for large files
find Assets/ -type f -size +10M | while read file; do
    ext="${file##*.}"
    echo "Large file detected: $file (${ext})"
    git lfs track "*.${ext}"
done

# Auto-commit LFS changes
git add .gitattributes
git commit -m "[AI] Auto-configure LFS for large Unity assets"
```

## 🌿 Unity-Optimized Branching Strategies

### Feature Branch Workflow for Game Development
**Branch Naming Conventions**:
```bash
# Feature development
feature/player-movement-system
feature/inventory-ui-overhaul
feature/boss-ai-behavior

# Bug fixes
bugfix/character-animation-glitch
bugfix/save-system-corruption

# Content creation
content/level-3-environment
content/character-animations

# Performance optimization
perf/rendering-optimization
perf/memory-usage-reduction

# Platform-specific work
platform/ios-integration
platform/console-porting
```

**Automated Branch Creation**:
```bash
# AI-assisted branch creation script
create_unity_branch() {
    local branch_type=$1
    local branch_name=$2
    local base_branch=${3:-main}
    
    echo "🤖 Creating Unity development branch..."
    
    # Create and switch to new branch
    git checkout -b "${branch_type}/${branch_name}" "${base_branch}"
    
    # Set up branch-specific Unity settings
    case $branch_type in
        "feature")
            echo "Setting up feature development environment"
            # Copy development build settings
            ;;
        "content")
            echo "Setting up content creation environment"
            # Configure asset import settings
            ;;
        "perf")
            echo "Setting up performance testing environment"
            # Enable profiler settings
            ;;
    esac
    
    echo "✅ Branch ${branch_type}/${branch_name} created and configured"
}

# Usage: create_unity_branch feature player-movement-system
```

### Collaborative Workflow Implementation
**Unity Team Collaboration Setup**:
```bash
# Team onboarding script
#!/bin/bash
# unity-team-setup.sh

echo "🎮 Unity Team Development Setup"

# Clone repository with LFS
git clone --recurse-submodules https://github.com/team/unity-project.git
cd unity-project

# Install Git LFS and pull assets
git lfs install
git lfs pull

# Set up Unity-specific Git config
git config core.autocrlf false  # Prevent line ending issues
git config core.filemode false # Ignore file permission changes

# Configure merge driver for Unity scenes and prefabs
git config merge.unityyamlmerge.name "Unity YAML Merge"
git config merge.unityyamlmerge.driver "UnityYAMLMerge merge -p %O %B %A %A"
git config merge.unityyamlmerge.recursive binary

echo "✅ Unity team environment configured"
```

## 🔄 Merge Strategies for Unity Assets

### Unity YAML Merge Tool Integration
**Merge Tool Configuration**:
```bash
# Configure Unity's merge tool
git config mergetool.unityyamlmerge.cmd 'UnityYAMLMerge merge -p "$BASE" "$REMOTE" "$LOCAL" "$MERGED"'
git config mergetool.unityyamlmerge.trustExitCode false

# Set as default merge tool for Unity files
echo "*.unity merge=unityyamlmerge eol=lf" >> .gitattributes
echo "*.prefab merge=unityyamlmerge" >> .gitattributes
echo "*.asset merge=unityyamlmerge" >> .gitattributes
echo "*.meta merge=unityyamlmerge" >> .gitattributes
```

**Automated Conflict Resolution**:
```csharp
// UnityMergeHelper.cs - AI-assisted merge conflict resolution
using UnityEngine;
using UnityEditor;
using System.IO;

public class UnityMergeHelper : EditorWindow
{
    [MenuItem("Tools/AI Merge Assistant")]
    public static void ShowWindow()
    {
        GetWindow<UnityMergeHelper>("AI Merge Assistant");
    }
    
    void OnGUI()
    {
        GUILayout.Label("🤖 AI-Powered Merge Conflict Resolution", EditorStyles.boldLabel);
        
        if (GUILayout.Button("Analyze Merge Conflicts"))
        {
            AnalyzeMergeConflicts();
        }
        
        if (GUILayout.Button("Auto-Resolve Safe Conflicts"))
        {
            AutoResolveSafeConflicts();
        }
        
        if (GUILayout.Button("Generate Merge Report"))
        {
            GenerateMergeReport();
        }
    }
    
    void AnalyzeMergeConflicts()
    {
        Debug.Log("🔍 Analyzing merge conflicts with AI assistance...");
        
        // Find conflicted files
        string[] conflictedFiles = System.IO.Directory.GetFiles(
            Application.dataPath, 
            "*", 
            SearchOption.AllDirectories
        ).Where(f => File.ReadAllText(f).Contains("<<<<<<< HEAD")).ToArray();
        
        foreach (string file in conflictedFiles)
        {
            Debug.Log($"Conflict detected in: {file}");
            AnalyzeConflictType(file);
        }
    }
    
    void AnalyzeConflictType(string filePath)
    {
        string content = File.ReadAllText(filePath);
        
        if (filePath.EndsWith(".unity"))
        {
            Debug.Log("🎬 Scene conflict detected - requires manual review");
        }
        else if (filePath.EndsWith(".prefab"))
        {
            Debug.Log("🧩 Prefab conflict detected - checking for component changes");
        }
        else if (filePath.EndsWith(".cs"))
        {
            Debug.Log("💻 Script conflict detected - analyzing for safe auto-merge");
        }
    }
    
    void AutoResolveSafeConflicts()
    {
        Debug.Log("🤖 Auto-resolving safe merge conflicts...");
        // Implementation for safe automatic conflict resolution
    }
    
    void GenerateMergeReport()
    {
        Debug.Log("📊 Generating merge conflict report...");
        // Generate detailed report for team review
    }
}
```

## 🚀 AI-Enhanced Git Workflows

### Automated Commit Message Generation
**AI Commit Message Helper**:
```bash
#!/bin/bash
# ai-commit.sh - AI-powered commit message generation

generate_commit_message() {
    echo "🤖 Analyzing changes for commit message generation..."
    
    # Get staged changes
    local changes=$(git diff --cached --name-only)
    local stats=$(git diff --cached --stat)
    
    # Analyze change patterns
    local has_scripts=$(echo "$changes" | grep -c "\.cs$")
    local has_scenes=$(echo "$changes" | grep -c "\.unity$")
    local has_prefabs=$(echo "$changes" | grep -c "\.prefab$")
    local has_assets=$(echo "$changes" | grep -c -E "\.(png|jpg|fbx|wav|mp3)$")
    
    # Generate appropriate commit message
    local message=""
    
    if [ $has_scripts -gt 0 ]; then
        message="feat: implement "
        if [ $has_scenes -gt 0 ]; then
            message+="gameplay system with scene integration"
        elif [ $has_prefabs -gt 0 ]; then
            message+="component system with prefab updates"
        else
            message+="new scripting functionality"
        fi
    elif [ $has_scenes -gt 0 ]; then
        message="content: update scene layouts and configurations"
    elif [ $has_assets -gt 0 ]; then
        message="assets: add new art and audio resources"
    else
        message="chore: project maintenance updates"
    fi
    
    echo "📝 Suggested commit message: $message"
    read -p "Use this message? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git commit -m "$message"
        echo "✅ Committed with AI-generated message"
    else
        echo "Please enter your commit message manually"
        git commit
    fi
}

# Usage: ./ai-commit.sh
generate_commit_message
```

### Intelligent Branch Management
**AI Branch Cleanup and Optimization**:
```bash
#!/bin/bash
# ai-branch-manager.sh

cleanup_merged_branches() {
    echo "🤖 AI Branch Cleanup Assistant"
    
    # Find merged branches
    local merged_branches=$(git branch --merged main | grep -v main | grep -v master)
    
    if [ -z "$merged_branches" ]; then
        echo "✅ No merged branches to clean up"
        return
    fi
    
    echo "📋 Merged branches found:"
    echo "$merged_branches"
    
    read -p "Delete these merged branches? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "$merged_branches" | xargs -n 1 git branch -d
        echo "✅ Merged branches cleaned up"
    fi
}

suggest_branch_strategy() {
    local current_branches=$(git branch -r | wc -l)
    local active_branches=$(git for-each-ref --format='%(refname:short) %(committerdate)' refs/remotes/origin | awk '$2 > "'$(date -d '30 days ago' '+%Y-%m-%d')'"' | wc -l)
    
    echo "📊 Branch Analysis:"
    echo "Total remote branches: $current_branches"
    echo "Active branches (last 30 days): $active_branches"
    
    if [ $current_branches -gt 20 ]; then
        echo "⚠️  Recommendation: Consider branch cleanup strategy"
        echo "💡 Suggestion: Implement branch naming conventions and automated cleanup"
    fi
}

# Run analysis
cleanup_merged_branches
suggest_branch_strategy
```

## 🔧 Unity-Specific Git Hooks

### Pre-commit Hooks for Unity Projects
**Unity Pre-commit Validation**:
```bash
#!/bin/bash
# .git/hooks/pre-commit
# Unity-specific pre-commit validation

echo "🎮 Unity Pre-commit Validation"

# Check for Unity Editor meta files
echo "Checking for missing meta files..."
missing_meta=false

while IFS= read -r -d '' file; do
    if [[ "$file" == *.cs ]] || [[ "$file" == *.js ]] || [[ "$file" == *.shader ]] || [[ "$file" == *.unity ]] || [[ "$file" == *.prefab ]]; then
        if [ ! -f "$file.meta" ]; then
            echo "❌ Missing meta file for: $file"
            missing_meta=true
        fi
    fi
done < <(git diff --cached --name-only -z)

if [ "$missing_meta" = true ]; then
    echo "💡 Generate missing meta files in Unity Editor before committing"
    exit 1
fi

# Check for Unity project settings consistency
echo "Validating Unity project settings..."

# Check if Physics settings are consistent
if git diff --cached --name-only | grep -q "ProjectSettings/DynamicsManager.asset"; then
    echo "⚠️  Physics settings modified - ensure team consensus"
fi

# Check for large files that should use LFS
echo "Checking for large files..."
large_files=$(git diff --cached --name-only | xargs -I {} find {} -size +10M 2>/dev/null)

if [ ! -z "$large_files" ]; then
    echo "❌ Large files detected that should use LFS:"
    echo "$large_files"
    echo "💡 Add these files to Git LFS tracking"
    exit 1
fi

echo "✅ Pre-commit validation passed"
```

### Post-merge Hook for Unity Projects
**Automated Unity Refresh**:
```bash
#!/bin/bash
# .git/hooks/post-merge
# Unity post-merge automation

echo "🔄 Unity Post-merge Automation"

# Check if Unity-related files changed
if git diff HEAD@{1} --name-only | grep -E "\.(unity|prefab|asset|cs)$" > /dev/null; then
    echo "Unity files changed - triggering refresh actions..."
    
    # Create marker file to trigger Unity refresh
    touch .unity-refresh-required
    
    # If Unity is running, send refresh command
    if pgrep -f "Unity" > /dev/null; then
        echo "Unity Editor detected - triggering asset refresh"
        # On macOS, send refresh command to Unity
        osascript -e 'tell application "Unity" to activate'
        osascript -e 'tell application "System Events" to keystroke "r" using {command down}'
    fi
    
    echo "💡 Open Unity Editor to refresh assets if not already running"
fi

# Check for package changes
if git diff HEAD@{1} --name-only | grep -q "Packages/manifest.json"; then
    echo "📦 Package manifest changed - consider refreshing Package Manager"
fi

echo "✅ Post-merge actions completed"
```

## 📊 Git Analytics and Reporting for Unity Teams

### Development Metrics Dashboard
**Unity Development Analytics**:
```bash
#!/bin/bash
# unity-git-analytics.sh

generate_unity_report() {
    echo "📊 Unity Development Analytics Report"
    echo "Generated: $(date)"
    echo "=========================================="
    
    # Commit activity by file type
    echo "📈 Commit Activity by Asset Type (Last 30 days):"
    git log --since="30 days ago" --name-only --pretty=format: | sort | uniq -c | sort -nr | head -20
    
    echo -e "\n🧑‍💻 Top Contributors (Last 30 days):"
    git log --since="30 days ago" --pretty=format:"%an" | sort | uniq -c | sort -nr
    
    echo -e "\n🎯 Most Modified Unity Assets:"
    git log --name-only --pretty=format: -- "*.unity" "*.prefab" "*.cs" | sort | uniq -c | sort -nr | head -10
    
    echo -e "\n🔥 Hotspot Analysis (Files with most commits):"
    git log --name-only --pretty=format: | grep -E "\.(cs|unity|prefab)$" | sort | uniq -c | sort -nr | head -15
    
    echo -e "\n📦 Repository Health:"
    echo "Total commits: $(git rev-list --count HEAD)"
    echo "Total contributors: $(git log --pretty=format:"%an" | sort | uniq | wc -l)"
    echo "Repository size: $(du -sh .git | cut -f1)"
    echo "LFS objects: $(git lfs ls-files | wc -l)"
}

# Generate and optionally save report
generate_unity_report
read -p "Save report to file? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    generate_unity_report > "unity-git-report-$(date +%Y%m%d).txt"
    echo "✅ Report saved to unity-git-report-$(date +%Y%m%d).txt"
fi
```

## 💡 Advanced Git Strategies for Unity Teams

### Continuous Integration Setup
**Unity CI/CD Git Integration**:
```yaml
# .github/workflows/unity-ci.yml
name: Unity CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  unity-test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
      with:
        lfs: true
        
    - name: Cache Unity Library
      uses: actions/cache@v3
      with:
        path: Library
        key: Library-${{ hashFiles('Assets/**', 'Packages/**', 'ProjectSettings/**') }}
        restore-keys: Library-
        
    - name: Run Unity Tests
      uses: game-ci/unity-test-runner@v2
      env:
        UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}
      with:
        projectPath: .
        testMode: EditMode
        
    - name: Build Unity Project
      uses: game-ci/unity-builder@v2
      env:
        UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}
      with:
        targetPlatform: StandaloneWindows64
```

### Code Review Optimization
**AI-Enhanced Code Review Process**:
```bash
#!/bin/bash
# ai-code-review.sh

analyze_unity_pr() {
    local pr_number=$1
    
    echo "🤖 AI-Enhanced Unity Code Review for PR #$pr_number"
    
    # Get changed files
    local changed_files=$(gh pr view $pr_number --json files -q '.files[].path')
    
    # Analyze changes by category
    local script_changes=$(echo "$changed_files" | grep "\.cs$" | wc -l)
    local scene_changes=$(echo "$changed_files" | grep "\.unity$" | wc -l)
    local prefab_changes=$(echo "$changed_files" | grep "\.prefab$" | wc -l)
    
    echo "📊 Change Analysis:"
    echo "Scripts modified: $script_changes"
    echo "Scenes modified: $scene_changes"
    echo "Prefabs modified: $prefab_changes"
    
    # Generate review checklist
    echo -e "\n✅ Review Checklist:"
    
    if [ $script_changes -gt 0 ]; then
        echo "- [ ] Code follows Unity C# conventions"
        echo "- [ ] Performance impact assessed"
        echo "- [ ] Unit tests added/updated"
    fi
    
    if [ $scene_changes -gt 0 ]; then
        echo "- [ ] Scene changes are intentional"
        echo "- [ ] No unnecessary object references"
        echo "- [ ] Lighting settings preserved"
    fi
    
    if [ $prefab_changes -gt 0 ]; then
        echo "- [ ] Prefab hierarchies maintained"
        echo "- [ ] Component configurations validated"
        echo "- [ ] Prefab variants still work"
    fi
}

# Usage: ./ai-code-review.sh 123
analyze_unity_pr $1
```

Proper Git workflows for Unity development ensure smooth collaboration, asset integrity, and efficient team productivity while leveraging AI tools for automation and optimization.