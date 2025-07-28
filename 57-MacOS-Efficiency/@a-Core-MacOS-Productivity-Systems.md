# @a-Core macOS Productivity Systems - Unity Developer Workflow Optimization

## 🎯 Learning Objectives
- Master macOS productivity features for Unity development workflows
- Implement AI-automated macOS systems for maximum efficiency
- Create custom shortcuts and automations for Unity development tasks
- Optimize macOS environment for 10x developer productivity
- Build seamless workflows between Unity, AI tools, and macOS native features

## ⚡ Essential macOS Productivity Features

### Spotlight and Alfred Power User Techniques
```bash
# Advanced Spotlight searches for Unity development
# Search by file type
kind:unity                          # Find all Unity files
kind:cs created:>2024-01-01        # Recent C# files
kind:prefab modified:today         # Today's prefab changes
name:"PlayerController" kind:cs     # Specific script searches

# System-wide file operations
mdfind "kMDItemContentType == 'com.unity3d.unity-scene'"  # Terminal Spotlight
mdfind "kMDItemLastUsedDate >= \$time.today"              # Today's files

# Alfred workflows for Unity (if using Alfred)
unity new project                   # Create new Unity project
unity open recent                   # Open recent Unity projects
unity build webgl                   # Quick build commands
unity docs {query}                  # Search Unity documentation
```

### Keyboard Shortcuts Mastery for Unity Development
```applescript
-- Custom AppleScript for Unity workflow shortcuts
-- Save as .scpt files and assign keyboard shortcuts

-- Quick Unity Project Switcher
tell application "Unity Hub"
    activate
    -- Switch between recent projects
end tell

-- Rapid File Navigation in Unity
tell application "Unity"
    activate
    -- Use CMD+T equivalent for Unity
    tell application "System Events"
        key code 17 using {command down} -- CMD+T
    end tell
end tell

-- Quick Documentation Lookup
on run {input, parameters}
    set searchTerm to input as string
    set unityDocsURL to "https://docs.unity3d.com/ScriptReference/" & searchTerm & ".html"
    open location unityDocsURL
    return input
end run
```

### Terminal and Shell Optimization
```bash
# ~/.zshrc optimizations for Unity development
export UNITY_PATH="/Applications/Unity/Hub/Editor"
export UNITY_LOG_PATH="~/Library/Logs/Unity"

# Unity-specific aliases
alias unity-hub='open -a "Unity Hub"'
alias unity-editor='open -a "Unity"'
alias unity-logs='tail -f ~/Library/Logs/Unity/Editor.log'
alias unity-clear-cache='rm -rf ~/Library/Caches/com.unity3d.*'
alias unity-prefs='open ~/Library/Preferences/com.unity3d.UnityEditor5.x.plist'

# Project management aliases
alias proj='cd ~/UnityProjects'
alias scripts='cd ~/UnityProjects/$(basename $(pwd))/Assets/Scripts'
alias scenes='cd ~/UnityProjects/$(basename $(pwd))/Assets/Scenes'

# Git shortcuts for Unity projects
alias git-unity='git add -A && git commit -m "Unity: $(date +%Y%m%d_%H%M)" && git push'
alias git-backup='git tag "backup-$(date +%Y%m%d_%H%M)" && git push --tags'

# AI development shortcuts
alias claude='open -a "Claude Code"'
alias gpt='open https://chat.openai.com'
alias prompt='pbpaste | pbcopy && echo "Prompt copied to clipboard"'

# Performance monitoring
alias unity-memory='ps aux | grep Unity | grep -v grep'
alias unity-cpu='top -pid $(pgrep Unity)'

# Quick file operations
function find-unity-script() {
    find ~/UnityProjects -name "*.cs" -type f | grep -i "$1"
}

function find-unity-asset() {
    find ~/UnityProjects -name "*$1*" -type f | grep -E "\.(prefab|asset|mat|unity)$"
}

# Development environment setup
function setup-unity-project() {
    local project_name=$1
    mkdir -p ~/UnityProjects/$project_name/{Scripts,Scenes,Prefabs,Materials,Textures}
    cd ~/UnityProjects/$project_name
    git init
    echo "Unity project $project_name created and initialized"
}
```

## 🚀 macOS Automation for Unity Development

### Shortcuts App Automations
```applescript
-- Shortcut: "New Unity Script"
-- Input: Text (script name)
-- Actions:
on run {input, parameters}
    set scriptName to input as string
    set scriptTemplate to "using UnityEngine;

public class " & scriptName & " : MonoBehaviour
{
    void Start()
    {
        
    }
    
    void Update()
    {
        
    }
}"
    
    -- Get current Unity project path
    tell application "Unity"
        -- Implementation depends on Unity's AppleScript support
    end tell
    
    -- Create the script file
    set scriptPath to "~/UnityProjects/CurrentProject/Assets/Scripts/" & scriptName & ".cs"
    do shell script "echo '" & scriptTemplate & "' > " & scriptPath
    
    -- Open in VS Code
    do shell script "code " & scriptPath
    
    return "Script " & scriptName & ".cs created successfully"
end run

-- Shortcut: "Unity Build & Deploy"
on run {input, parameters}
    -- Unity command line build
    set buildCommand to "/Applications/Unity/Hub/Editor/2023.3.0f1/Unity.app/Contents/MacOS/Unity -quit -batchmode -projectPath ~/UnityProjects/CurrentProject -buildTarget WebGL -buildPath ~/Builds/WebGL"
    
    do shell script buildCommand
    
    -- Deploy to web server (if configured)
    do shell script "rsync -av ~/Builds/WebGL/ username@server:/var/www/games/"
    
    return "Build completed and deployed"
end run

-- Shortcut: "AI Code Review"
on run {input, parameters}
    -- Get current clipboard content (code)
    set codeContent to the clipboard
    
    -- Format prompt for AI
    set aiPrompt to "Review this Unity C# code for best practices, performance, and potential bugs:

" & codeContent & "

Provide:
1. Code quality assessment
2. Performance optimization suggestions  
3. Unity-specific best practices
4. Potential bug identification
5. Refactoring recommendations"
    
    -- Copy prompt to clipboard for AI tool
    set the clipboard to aiPrompt
    
    -- Open Claude Code or ChatGPT
    open location "https://claude.ai/code"
    
    return "Code review prompt copied to clipboard"
end run
```

### Automator Workflows for Unity Development
```applescript
-- Automator Service: "Unity Project Backup"
-- Service receives: no input
-- in: any application

on run {input, parameters}
    set currentDate to do shell script "date +%Y%m%d_%H%M%S"
    set backupName to "UnityBackup_" & currentDate
    
    -- Create backup directory
    do shell script "mkdir -p ~/Backups/Unity/" & backupName
    
    -- Backup current Unity projects
    do shell script "rsync -av --exclude='Library' --exclude='Temp' --exclude='obj' ~/UnityProjects/ ~/Backups/Unity/" & backupName & "/"
    
    -- Compress backup
    do shell script "cd ~/Backups/Unity && tar -czf " & backupName & ".tar.gz " & backupName
    do shell script "rm -rf ~/Backups/Unity/" & backupName
    
    display notification "Unity projects backed up successfully" with title "Backup Complete"
    
    return input
end run

-- Automator Application: "Unity Development Environment"
-- Launches all necessary tools for Unity development

on run {input, parameters}
    -- Launch Unity Hub
    tell application "Unity Hub" to activate
    delay 2
    
    -- Launch Visual Studio Code
    tell application "Visual Studio Code" to activate
    delay 2
    
    -- Launch Terminal with development profile
    tell application "Terminal"
        activate
        do script "cd ~/UnityProjects && ls -la"
    end tell
    
    -- Launch AI assistant tools
    open location "https://claude.ai/code"
    
    -- Set up desktop spaces
    tell application "System Events"
        -- Switch to Unity development desktop
        key code 123 using {control down, command down} -- Ctrl+Cmd+Left
    end tell
    
    display notification "Unity development environment ready" with title "Environment Setup"
    
    return input
end run
```

### Hazel Rules for Unity File Management
```applescript
-- Hazel rule configurations for automated Unity file organization

-- Rule 1: Auto-organize Unity project files
-- Folder: ~/Downloads
-- Conditions: Name contains "unity" OR Extension is "unitypackage"
-- Actions: Move to ~/UnityProjects/Assets/Imported/

-- Rule 2: Clean Unity cache files
-- Folder: ~/Library/Caches
-- Conditions: Name starts with "com.unity3d" AND Date Last Opened is not in the last 7 days
-- Actions: Move to Trash

-- Rule 3: Archive old Unity builds
-- Folder: ~/Builds
-- Conditions: Date Created is not in the last 30 days
-- Actions: Compress and move to ~/Archives/Builds/

-- Rule 4: Unity log file management
-- Folder: ~/Library/Logs/Unity
-- Conditions: Date Created is not in the last 14 days
-- Actions: Move to Trash

-- Custom AppleScript for advanced Unity file processing
on run {input, parameters}
    set unityFile to input
    
    -- Determine file type and appropriate action
    tell application "System Events"
        set fileName to name of file unityFile
        set fileExtension to name extension of file unityFile
    end tell
    
    if fileExtension is "cs" then
        -- Process C# script files
        processUnityScript(unityFile)
    else if fileExtension is "unity" then
        -- Process Unity scene files
        processUnityScene(unityFile)
    else if fileExtension is "prefab" then
        -- Process Unity prefab files
        processUnityPrefab(unityFile)
    end if
    
    return input
end run

-- Helper functions for Unity file processing
on processUnityScript(scriptFile)
    -- Add to current Unity project Scripts folder
    set targetPath to "~/UnityProjects/CurrentProject/Assets/Scripts/"
    do shell script "mv '" & scriptFile & "' " & targetPath
end processUnityScript

on processUnityScene(sceneFile)
    -- Add to current Unity project Scenes folder
    set targetPath to "~/UnityProjects/CurrentProject/Assets/Scenes/"
    do shell script "mv '" & sceneFile & "' " & targetPath
end processUnityScene
```

## 🎨 Desktop and Window Management

### Mission Control and Desktop Optimization
```applescript
-- Desktop space organization for Unity development
-- Space 1: Unity Editor + Game View
-- Space 2: Code Editor (VS Code/Rider)
-- Space 3: Browser (Documentation, AI tools)
-- Space 4: Terminal, File Management, Utilities

-- AppleScript to setup development spaces
tell application "System Events"
    -- Create new desktop spaces if needed
    -- Note: This requires manual setup in Mission Control preferences
    
    -- Switch to Unity development space
    key code 18 using {control down} -- Ctrl+1 (Space 1)
    delay 1
    
    -- Launch Unity in current space
    tell application "Unity" to activate
    
    -- Switch to coding space
    key code 19 using {control down} -- Ctrl+2 (Space 2)
    delay 1
    
    -- Launch VS Code in coding space
    tell application "Visual Studio Code" to activate
    
    -- Switch to research space
    key code 20 using {control down} -- Ctrl+3 (Space 3)
    delay 1
    
    -- Open browser with Unity docs
    tell application "Safari"
        activate
        open location "https://docs.unity3d.com/"
    end tell
end tell
```

### Window Management with Rectangle/Magnet
```bash
# Rectangle CLI commands (if installed via Homebrew)
# Install: brew install --cask rectangle

# Custom Rectangle configurations for Unity development
# Rectangle preferences file: ~/Library/Preferences/com.knollsoft.Rectangle.plist

# Keyboard shortcuts for Unity workflow:
# Cmd+Option+Left: Left half (for Unity Inspector)
# Cmd+Option+Right: Right half (for Unity Scene/Game view)
# Cmd+Option+Up: Top half (for code editor)
# Cmd+Option+Down: Bottom half (for terminal/console)
# Cmd+Option+F: Fullscreen toggle

# Custom window arrangements
function unity-layout() {
    # Unity Editor - left 2/3
    osascript -e 'tell application "Unity" to activate'
    osascript -e 'tell application "System Events" to keystroke "left" using {command down, option down}'
    
    # Game window - right 1/3
    # (Implementation depends on Unity window management)
    
    # VS Code - bottom right quarter
    osascript -e 'tell application "Visual Studio Code" to activate'
    osascript -e 'tell application "System Events" to keystroke "down" using {command down, option down}'
}

function code-focus-layout() {
    # VS Code - full screen for coding sessions
    osascript -e 'tell application "Visual Studio Code" to activate'
    osascript -e 'tell application "System Events" to keystroke "f" using {command down, option down}'
}

function review-layout() {
    # Split screen: code on left, browser/AI on right
    osascript -e 'tell application "Visual Studio Code" to activate'
    osascript -e 'tell application "System Events" to keystroke "left" using {command down, option down}'
    
    osascript -e 'tell application "Safari" to activate'
    osascript -e 'tell application "System Events" to keystroke "right" using {command down, option down}'
}
```

## 🤖 AI Integration with macOS Native Features

### Siri Shortcuts for AI-Powered Development
```applescript
-- Siri Shortcut: "Review my Unity code"
-- Trigger: "Hey Siri, review my Unity code"

on run {input, parameters}
    -- Get currently selected text or clipboard
    tell application "System Events"
        keystroke "c" using {command down}
        delay 0.5
    end tell
    
    set codeContent to the clipboard
    
    -- Format AI prompt
    set aiPrompt to "Please review this Unity C# code and provide:
1. Code quality assessment
2. Performance optimization suggestions
3. Unity best practices compliance
4. Bug identification
5. Refactoring recommendations

Code:
" & codeContent
    
    -- Copy to clipboard and open AI tool
    set the clipboard to aiPrompt
    open location "https://claude.ai/code"
    
    return "Code review prompt ready for AI assistant"
end run

-- Siri Shortcut: "Unity documentation search"
-- Input: Spoken text
on run {input, parameters}
    set searchTerm to input as string
    set unityDocsURL to "https://docs.unity3d.com/ScriptReference/" & searchTerm & ".html"
    
    open location unityDocsURL
    
    return "Opening Unity documentation for " & searchTerm
end run

-- Siri Shortcut: "Create Unity script template"
-- Input: Script name (spoken)
on run {input, parameters}
    set scriptName to input as string
    
    -- Generate script template with AI assistance
    set aiPrompt to "Generate a Unity C# script template for a script named '" & scriptName & "'. Include:
1. Proper using statements
2. Class definition inheriting from MonoBehaviour
3. Common Unity lifecycle methods (Start, Update, etc.)
4. Appropriate comments and documentation
5. Best practices for Unity development"
    
    set the clipboard to aiPrompt
    open location "https://claude.ai/code"
    
    return "AI script template prompt ready for " & scriptName
end run
```

### Text Replacement and Snippets
```applescript
-- System Preferences > Keyboard > Text Replacements
-- Add these Unity development shortcuts:

-- Code snippets
ustart     -> void Start()
           {
               
           }

uupdate    -> void Update()
           {
               
           }

ufixed     -> void FixedUpdate()
           {
               
           }

uawake     -> void Awake()
           {
               
           }

uonable    -> void OnEnable()
           {
               
           }

uondisable -> void OnDisable()
           {
               
           }

-- Unity-specific shortcuts
ggobj      -> GameObject
tfm        -> transform
rb2d       -> GetComponent<Rigidbody2D>()
coll       -> GetComponent<Collider>()
anim       -> GetComponent<Animator>()

-- AI prompt templates
airev      -> Please review this Unity C# code for best practices, performance, and potential bugs:

aiopt      -> Optimize this Unity code for better performance:

airef      -> Refactor this Unity code to improve maintainability:

aidoc      -> Generate comprehensive documentation for this Unity script:
```

## 💡 Key Highlights

### macOS Productivity Essentials
- **Spotlight Mastery**: Advanced search techniques for Unity files and assets
- **Keyboard Shortcuts**: Custom shortcuts optimized for Unity development workflow
- **Terminal Optimization**: Unity-specific aliases and functions for rapid development
- **Window Management**: Efficient screen space utilization for multi-tool workflows

### Automation Benefits
- **Shortcuts App**: Custom automations for Unity tasks and AI integration
- **Automator Workflows**: Batch processing and environment setup automation
- **Hazel Rules**: Intelligent file organization for Unity projects
- **Siri Integration**: Voice-activated development tasks and AI assistance

### AI Integration Opportunities
- **Code Review Automation**: Instant AI-powered code analysis and feedback
- **Documentation Search**: Voice-activated Unity documentation lookup
- **Script Generation**: AI-assisted Unity script template creation
- **Workflow Optimization**: AI-powered development process improvements

### Unity-Specific Optimizations
- **Project Management**: Automated Unity project organization and backup
- **Build Automation**: Streamlined Unity build and deployment processes
- **Asset Organization**: Intelligent Unity asset management and file handling
- **Development Environment**: One-click setup of complete Unity development environment

## 🎯 Next Steps for macOS Unity Mastery
1. **Setup Custom Shortcuts**: Implement Unity-specific keyboard shortcuts and automations
2. **Configure Window Management**: Optimize screen real estate for Unity development
3. **Automate File Organization**: Setup Hazel rules for Unity project management
4. **Integrate AI Workflows**: Create seamless AI-assisted development processes
5. **Build Development Environment**: One-click Unity development environment setup