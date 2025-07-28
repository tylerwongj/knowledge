# @b-Command Line Terminal Mastery - Unity Development Shell Optimization

## 🎯 Learning Objectives
- Master advanced terminal techniques for Unity development workflows
- Implement AI-automated command line tools and scripts
- Create custom shell functions and aliases for maximum productivity
- Build terminal-based Unity project management systems
- Optimize shell environment for seamless AI tool integration

## 🚀 Advanced Shell Configuration

### Zsh Configuration for Unity Development
```bash
# ~/.zshrc - Optimized for Unity Development and AI Integration

# Environment Variables
export UNITY_HUB_PATH="/Applications/Unity Hub.app/Contents/MacOS/Unity Hub"
export UNITY_EDITOR_PATH="/Applications/Unity/Hub/Editor"
export UNITY_PROJECTS_PATH="$HOME/UnityProjects"
export UNITY_BUILDS_PATH="$HOME/Builds"
export UNITY_ASSETS_PATH="$HOME/UnityAssets"

# AI Tool Integration
export OPENAI_API_KEY="your-api-key-here"
export CLAUDE_API_KEY="your-claude-key-here"
export AI_PROMPTS_PATH="$HOME/.ai-prompts"

# Performance optimizations
export HISTSIZE=50000
export SAVEHIST=50000
export HISTFILE="$HOME/.zsh_history"
setopt HIST_VERIFY
setopt SHARE_HISTORY
setopt APPEND_HISTORY
setopt INC_APPEND_HISTORY
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_ALL_DUPS
setopt HIST_REDUCE_BLANKS

# Enable autocompletion
autoload -Uz compinit
compinit

# Advanced completion settings
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"

# Custom prompt with Unity project info
autoload -U colors && colors
setopt PROMPT_SUBST

function unity_project_info() {
    if [[ -f "ProjectSettings/ProjectSettings.asset" ]]; then
        local project_name=$(basename "$PWD")
        local unity_version=$(grep "m_EditorVersion:" ProjectSettings/ProjectVersion.txt 2>/dev/null | cut -d' ' -f2)
        echo "%{$fg[blue]%}[Unity: $project_name v$unity_version]%{$reset_color%} "
    fi
}

PROMPT='$(unity_project_info)%{$fg[green]%}%n@%m%{$reset_color%} %{$fg[cyan]%}%~%{$reset_color%} $ '
```

### Unity Development Aliases and Functions
```bash
# ~/.zsh_aliases - Unity Development Shortcuts

# === UNITY PROJECT MANAGEMENT ===
alias unity-hub='open -a "Unity Hub"'
alias unity-editor='open -a "Unity"'
alias unity-logs='tail -f ~/Library/Logs/Unity/Editor.log'
alias unity-console='tail -f ~/Library/Logs/Unity/Player.log'
alias unity-clear-cache='rm -rf ~/Library/Caches/com.unity3d.* && echo "Unity cache cleared"'
alias unity-clear-logs='rm -f ~/Library/Logs/Unity/*.log && echo "Unity logs cleared"'

# Project navigation
alias proj='cd $UNITY_PROJECTS_PATH'
alias builds='cd $UNITY_BUILDS_PATH'
alias assets='cd $UNITY_ASSETS_PATH'

# Quick project directory navigation
function scripts() {
    if [[ -d "Assets/Scripts" ]]; then
        cd "Assets/Scripts"
    else
        echo "Not in a Unity project or Scripts folder doesn't exist"
    fi
}

function scenes() {
    if [[ -d "Assets/Scenes" ]]; then
        cd "Assets/Scenes"
    else
        echo "Not in a Unity project or Scenes folder doesn't exist"
    fi
}

function prefabs() {
    if [[ -d "Assets/Prefabs" ]]; then
        cd "Assets/Prefabs"
    else
        echo "Not in a Unity project or Prefabs folder doesn't exist"
    fi
}

# === UNITY PROJECT CREATION ===
function unity-new() {
    local project_name=$1
    local template=${2:-"3D"}
    
    if [[ -z "$project_name" ]]; then
        echo "Usage: unity-new <project_name> [template]"
        echo "Templates: 2D, 3D, VR, AR, Mobile"
        return 1
    fi
    
    local project_path="$UNITY_PROJECTS_PATH/$project_name"
    
    # Create project directory structure
    mkdir -p "$project_path"/{Assets/{Scripts,Scenes,Prefabs,Materials,Textures,Audio},Builds,Documentation}
    
    # Initialize git repository
    cd "$project_path"
    git init
    
    # Create Unity .gitignore
    curl -s https://raw.githubusercontent.com/github/gitignore/main/Unity.gitignore > .gitignore
    
    # Create initial commit
    git add .gitignore
    git commit -m "Initial commit: Unity project structure"
    
    # Create README
    cat > README.md << EOF
# $project_name

Unity $template project created on $(date)

## Project Structure
- \`Assets/Scripts/\` - C# scripts
- \`Assets/Scenes/\` - Unity scenes
- \`Assets/Prefabs/\` - Game object prefabs
- \`Assets/Materials/\` - Materials and shaders
- \`Assets/Textures/\` - Texture assets
- \`Assets/Audio/\` - Audio clips and music
- \`Builds/\` - Built game files
- \`Documentation/\` - Project documentation

## Development Notes
TODO: Add development notes and progress tracking
EOF
    
    git add README.md
    git commit -m "Add project README"
    
    echo "Unity project '$project_name' created at $project_path"
    echo "Opening Unity Hub to add project..."
    unity-hub
}

# === UNITY BUILD AUTOMATION ===
function unity-build() {
    local build_target=${1:-"WebGL"}
    local build_path="$UNITY_BUILDS_PATH/$(basename "$PWD")/$build_target"
    
    if [[ ! -f "ProjectSettings/ProjectSettings.asset" ]]; then
        echo "Error: Not in a Unity project directory"
        return 1
    fi
    
    echo "Building Unity project for $build_target..."
    echo "Build path: $build_path"
    
    # Get Unity Editor path for current project
    local unity_version=$(grep "m_EditorVersion:" ProjectSettings/ProjectVersion.txt | cut -d' ' -f2)
    local unity_executable="$UNITY_EDITOR_PATH/$unity_version/Unity.app/Contents/MacOS/Unity"
    
    if [[ ! -f "$unity_executable" ]]; then
        echo "Error: Unity $unity_version not found"
        return 1
    fi
    
    # Build command
    "$unity_executable" \
        -quit \
        -batchmode \
        -projectPath "$PWD" \
        -buildTarget "$build_target" \
        -buildPath "$build_path" \
        -logFile "$UNITY_BUILDS_PATH/build_$(date +%Y%m%d_%H%M%S).log"
    
    if [[ $? -eq 0 ]]; then
        echo "Build completed successfully!"
        echo "Build location: $build_path"
        
        # Open build folder
        open "$build_path"
    else
        echo "Build failed. Check log file in $UNITY_BUILDS_PATH"
    fi
}

# Build shortcuts for common targets
alias unity-build-webgl='unity-build WebGL'
alias unity-build-mac='unity-build StandaloneOSX'
alias unity-build-windows='unity-build StandaloneWindows64'
alias unity-build-ios='unity-build iOS'
alias unity-build-android='unity-build Android'

# === FILE SEARCH AND MANAGEMENT ===
function find-unity-script() {
    local search_term=$1
    if [[ -z "$search_term" ]]; then
        echo "Usage: find-unity-script <search_term>"
        return 1
    fi
    
    find "$UNITY_PROJECTS_PATH" -name "*.cs" -type f | xargs grep -l "$search_term" 2>/dev/null
}

function find-unity-asset() {
    local search_term=$1
    if [[ -z "$search_term" ]]; then
        echo "Usage: find-unity-asset <search_term>"
        return 1
    fi
    
    find "$UNITY_PROJECTS_PATH" -name "*$search_term*" -type f | grep -E "\.(prefab|asset|mat|unity|fbx|png|jpg)$"
}

function unity-project-size() {
    if [[ -f "ProjectSettings/ProjectSettings.asset" ]]; then
        echo "Project: $(basename "$PWD")"
        echo "Total size: $(du -sh . | cut -f1)"
        echo ""
        echo "Breakdown:"
        echo "  Assets: $(du -sh Assets 2>/dev/null | cut -f1 || echo "N/A")"
        echo "  Library: $(du -sh Library 2>/dev/null | cut -f1 || echo "N/A")"
        echo "  Logs: $(du -sh Logs 2>/dev/null | cut -f1 || echo "N/A")"
        echo "  Packages: $(du -sh Packages 2>/dev/null | cut -f1 || echo "N/A")"
    else
        echo "Not in a Unity project directory"
    fi
}

# === GIT INTEGRATION ===
function unity-commit() {
    local message=${1:-"Unity: Auto-commit $(date +%Y%m%d_%H%M)"}
    
    if [[ ! -d ".git" ]]; then
        echo "Error: Not in a git repository"
        return 1
    fi
    
    # Add Unity-specific files
    git add Assets/ ProjectSettings/ Packages/
    
    # Show what will be committed
    echo "Files to be committed:"
    git diff --cached --name-only
    
    echo ""
    read "confirm?Commit with message '$message'? (y/N): "
    
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        git commit -m "$message"
        echo "Committed successfully!"
        
        # Ask about pushing
        read "push?Push to remote? (y/N): "
        if [[ "$push" =~ ^[Yy]$ ]]; then
            git push
        fi
    else
        echo "Commit cancelled"
    fi
}

alias unity-status='git status --porcelain | grep -E "\.(cs|unity|prefab|asset|mat)$"'
alias unity-diff='git diff --name-only | grep -E "\.(cs|unity|prefab|asset|mat)$"'
```

### AI Integration Command Line Tools
```bash
# === AI-POWERED DEVELOPMENT TOOLS ===

# AI code review function
function ai-review() {
    local file=${1:-}
    
    if [[ -z "$file" && -t 0 ]]; then
        echo "Usage: ai-review <file> or pipe content to ai-review"
        echo "Example: ai-review PlayerController.cs"
        echo "Example: cat script.cs | ai-review"
        return 1
    fi
    
    local code_content
    if [[ -n "$file" ]]; then
        if [[ ! -f "$file" ]]; then
            echo "Error: File '$file' not found"
            return 1
        fi
        code_content=$(cat "$file")
    else
        # Read from stdin
        code_content=$(cat)
    fi
    
    local prompt="Review this Unity C# code for best practices, performance, and potential bugs:

\`\`\`csharp
$code_content
\`\`\`

Please provide:
1. Code quality assessment
2. Performance optimization suggestions
3. Unity-specific best practices
4. Potential bug identification
5. Refactoring recommendations"
    
    # Copy to clipboard for AI tool
    echo "$prompt" | pbcopy
    echo "AI review prompt copied to clipboard!"
    echo "Opening Claude Code..."
    open "https://claude.ai/code"
}

# AI script generation
function ai-script() {
    local script_name=$1
    local script_type=${2:-"MonoBehaviour"}
    
    if [[ -z "$script_name" ]]; then
        echo "Usage: ai-script <script_name> [script_type]"
        echo "Types: MonoBehaviour, ScriptableObject, Editor, System"
        return 1
    fi
    
    local prompt="Generate a Unity C# script named '$script_name' of type '$script_type'.

Requirements:
1. Follow Unity C# conventions and best practices
2. Include appropriate using statements
3. Add XML documentation comments
4. Include common Unity lifecycle methods if applicable
5. Add proper error handling where appropriate
6. Follow SOLID principles
7. Include performance considerations

Additional context:
- This is for a professional Unity project
- Code should be production-ready
- Include helpful comments for team collaboration"
    
    echo "$prompt" | pbcopy
    echo "AI script generation prompt for '$script_name' copied to clipboard!"
    open "https://claude.ai/code"
}

# AI documentation generator
function ai-docs() {
    local file=$1
    
    if [[ -z "$file" || ! -f "$file" ]]; then
        echo "Usage: ai-docs <script_file.cs>"
        return 1
    fi
    
    local code_content=$(cat "$file")
    local prompt="Generate comprehensive documentation for this Unity C# script:

\`\`\`csharp
$code_content
\`\`\`

Please provide:
1. Class/script overview and purpose
2. Method documentation with parameters and return values
3. Usage examples
4. Integration notes for Unity workflow
5. Performance considerations
6. Potential gotchas or important notes

Format as markdown for inclusion in project documentation."
    
    echo "$prompt" | pbcopy
    echo "Documentation generation prompt copied to clipboard!"
    open "https://claude.ai/code"
}

# AI performance optimization
function ai-optimize() {
    local file=$1
    
    if [[ -z "$file" || ! -f "$file" ]]; then
        echo "Usage: ai-optimize <script_file.cs>"
        return 1
    fi
    
    local code_content=$(cat "$file")
    local prompt="Optimize this Unity C# code for better performance:

\`\`\`csharp
$code_content
\`\`\`

Focus on:
1. Memory allocation reduction
2. Garbage collection optimization
3. CPU performance improvements
4. Unity-specific optimizations
5. Caching strategies
6. Object pooling opportunities
7. Coroutine vs Update optimization
8. Physics and rendering performance

Provide optimized code with explanations for each improvement."
    
    echo "$prompt" | pbcopy
    echo "Performance optimization prompt copied to clipboard!"
    open "https://claude.ai/code"
}

# === PERFORMANCE MONITORING ===
function unity-performance() {
    echo "Unity Editor Processes:"
    ps aux | grep Unity | grep -v grep | while read line; do
        echo "  $line"
    done
    
    echo ""
    echo "Memory Usage:"
    ps -o pid,rss,comm -p $(pgrep Unity) 2>/dev/null | while read pid rss comm; do
        if [[ "$pid" != "PID" ]]; then
            local mb=$((rss / 1024))
            echo "  PID $pid: ${mb}MB ($comm)"
        else
            echo "  $pid $rss $comm"
        fi
    done
    
    echo ""
    echo "Disk Usage:"
    echo "  Unity Cache: $(du -sh ~/Library/Caches/com.unity3d.* 2>/dev/null | awk '{sum+=$1} END {print sum "B"}' || echo "0B")"
    echo "  Unity Logs: $(du -sh ~/Library/Logs/Unity 2>/dev/null | cut -f1 || echo "0B")"
    echo "  Unity Projects: $(du -sh $UNITY_PROJECTS_PATH 2>/dev/null | cut -f1 || echo "0B")"
}

# === PROJECT ANALYSIS ===
function unity-analyze() {
    if [[ ! -f "ProjectSettings/ProjectSettings.asset" ]]; then
        echo "Error: Not in a Unity project directory"
        return 1
    fi
    
    echo "Unity Project Analysis: $(basename "$PWD")"
    echo "=================================="
    
    # Project info
    local unity_version=$(grep "m_EditorVersion:" ProjectSettings/ProjectVersion.txt | cut -d' ' -f2)
    echo "Unity Version: $unity_version"
    
    # File counts
    echo ""
    echo "Asset Counts:"
    echo "  C# Scripts: $(find Assets -name "*.cs" -type f | wc -l)"
    echo "  Scenes: $(find Assets -name "*.unity" -type f | wc -l)"
    echo "  Prefabs: $(find Assets -name "*.prefab" -type f | wc -l)"
    echo "  Materials: $(find Assets -name "*.mat" -type f | wc -l)"
    echo "  Textures: $(find Assets -name "*.png" -o -name "*.jpg" -o -name "*.tga" | wc -l)"
    echo "  Audio: $(find Assets -name "*.wav" -o -name "*.mp3" -o -name "*.ogg" | wc -l)"
    
    # Code analysis
    echo ""
    echo "Code Analysis:"
    local total_lines=$(find Assets -name "*.cs" -type f -exec wc -l {} + | tail -n 1 | awk '{print $1}')
    echo "  Total Lines of Code: $total_lines"
    
    # Recent activity
    echo ""
    echo "Recent Activity (last 7 days):"
    echo "  Modified Scripts: $(find Assets -name "*.cs" -type f -mtime -7 | wc -l)"
    echo "  Modified Scenes: $(find Assets -name "*.unity" -type f -mtime -7 | wc -l)"
    echo "  Modified Prefabs: $(find Assets -name "*.prefab" -type f -mtime -7 | wc -l)"
    
    # Git status (if in git repo)
    if [[ -d ".git" ]]; then
        echo ""
        echo "Git Status:"
        echo "  Uncommitted files: $(git status --porcelain | wc -l)"
        echo "  Current branch: $(git branch --show-current)"
        echo "  Last commit: $(git log -1 --format="%h %s (%cr)")"
    fi
}

# === CLEANUP FUNCTIONS ===
function unity-cleanup() {
    echo "Unity Development Environment Cleanup"
    echo "====================================="
    
    # Clear Unity caches
    echo "Clearing Unity caches..."
    rm -rf ~/Library/Caches/com.unity3d.*
    
    # Clear Unity logs older than 7 days
    echo "Clearing old Unity logs..."
    find ~/Library/Logs/Unity -name "*.log" -mtime +7 -delete
    
    # Clear old build files
    echo "Clearing old build files..."
    find "$UNITY_BUILDS_PATH" -type d -mtime +30 -exec rm -rf {} +
    
    # Clear temporary files from Unity projects
    echo "Clearing temporary Unity project files..."
    find "$UNITY_PROJECTS_PATH" -name "Temp" -type d -exec rm -rf {} +
    find "$UNITY_PROJECTS_PATH" -name "obj" -type d -exec rm -rf {} +
    
    echo "Cleanup completed!"
    unity-performance
}

# === HELP FUNCTION ===
function unity-help() {
    echo "Unity Development Terminal Commands"
    echo "=================================="
    echo ""
    echo "Project Management:"
    echo "  unity-new <name> [template]  - Create new Unity project"
    echo "  unity-analyze               - Analyze current Unity project"
    echo "  unity-project-size          - Show project size breakdown"
    echo "  unity-cleanup               - Clean up Unity caches and temp files"
    echo ""
    echo "Navigation:"
    echo "  proj                        - Go to Unity projects directory"
    echo "  scripts                     - Go to Scripts folder (in Unity project)"
    echo "  scenes                      - Go to Scenes folder (in Unity project)"
    echo "  prefabs                     - Go to Prefabs folder (in Unity project)"
    echo ""
    echo "Building:"
    echo "  unity-build [target]        - Build Unity project"
    echo "  unity-build-webgl           - Build for WebGL"
    echo "  unity-build-mac             - Build for macOS"
    echo ""
    echo "AI Integration:"
    echo "  ai-review <file>            - AI code review"
    echo "  ai-script <name> [type]     - Generate script with AI"
    echo "  ai-docs <file>              - Generate documentation"
    echo "  ai-optimize <file>          - Optimize code with AI"
    echo ""
    echo "Search:"
    echo "  find-unity-script <term>    - Find scripts containing term"
    echo "  find-unity-asset <term>     - Find assets matching term"
    echo ""
    echo "Git Integration:"
    echo "  unity-commit [message]      - Smart Unity git commit"
    echo "  unity-status                - Git status for Unity files"
    echo "  unity-diff                  - Git diff for Unity files"
    echo ""
    echo "Monitoring:"
    echo "  unity-performance           - Show Unity performance metrics"
    echo "  unity-logs                  - Tail Unity editor logs"
    echo ""
    echo "Apps:"
    echo "  unity-hub                   - Open Unity Hub"
    echo "  unity-editor                - Open Unity Editor"
}

# Auto-completion for custom functions
_unity_projects() {
    local projects=($(ls "$UNITY_PROJECTS_PATH" 2>/dev/null))
    _describe 'unity projects' projects
}

compdef _unity_projects unity-project
```

## 🔧 Advanced Terminal Tools and Utilities

### Custom Terminal Scripts
```bash
#!/bin/bash
# ~/.local/bin/unity-dev-setup - Development environment setup script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    log_error "This script is designed for macOS only"
    exit 1
fi

# Setup Unity development environment
setup_unity_environment() {
    log_info "Setting up Unity development environment..."
    
    # Create directory structure
    mkdir -p "$HOME/UnityProjects"
    mkdir -p "$HOME/Builds"
    mkdir -p "$HOME/UnityAssets"
    mkdir -p "$HOME/.unity-templates"
    mkdir -p "$HOME/.ai-prompts"
    
    # Install Homebrew if not present
    if ! command -v brew &> /dev/null; then
        log_info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install useful tools
    log_info "Installing development tools..."
    brew_packages=(
        "git"
        "node"
        "python3"
        "jq"
        "tree"
        "bat"
        "fzf"
        "ripgrep"
        "fd"
        "exa"
        "zoxide"
    )
    
    for package in "${brew_packages[@]}"; do
        if brew list "$package" &>/dev/null; then
            log_success "$package already installed"
        else
            log_info "Installing $package..."
            brew install "$package"
        fi
    done
    
    # Install cask applications
    cask_apps=(
        "visual-studio-code"
        "unity-hub"
        "rectangle"
        "alfred"
        "github-desktop"
    )
    
    for app in "${cask_apps[@]}"; do
        if brew list --cask "$app" &>/dev/null; then
            log_success "$app already installed"
        else
            log_info "Installing $app..."
            brew install --cask "$app"
        fi
    done
}

# Setup AI prompt templates
setup_ai_prompts() {
    log_info "Setting up AI prompt templates..."
    
    cat > "$HOME/.ai-prompts/unity-code-review.txt" << 'EOF'
Review this Unity C# code for best practices, performance, and potential bugs:

```csharp
{CODE_CONTENT}
```

Please provide:
1. Code quality assessment
2. Performance optimization suggestions
3. Unity-specific best practices
4. Potential bug identification
5. Refactoring recommendations
EOF
    
    cat > "$HOME/.ai-prompts/unity-script-generation.txt" << 'EOF'
Generate a Unity C# script named '{SCRIPT_NAME}' of type '{SCRIPT_TYPE}'.

Requirements:
1. Follow Unity C# conventions and best practices
2. Include appropriate using statements
3. Add XML documentation comments
4. Include common Unity lifecycle methods if applicable
5. Add proper error handling where appropriate
6. Follow SOLID principles
7. Include performance considerations
EOF
    
    cat > "$HOME/.ai-prompts/unity-optimization.txt" << 'EOF'
Optimize this Unity C# code for better performance:

```csharp
{CODE_CONTENT}
```

Focus on:
1. Memory allocation reduction
2. Garbage collection optimization
3. CPU performance improvements
4. Unity-specific optimizations
5. Caching strategies
6. Object pooling opportunities
EOF
    
    log_success "AI prompt templates created"
}

# Setup VS Code extensions for Unity development
setup_vscode_extensions() {
    log_info "Setting up VS Code extensions for Unity development..."
    
    extensions=(
        "ms-dotnettools.csharp"
        "ms-vscode.vscode-typescript-next"
        "visualstudiotoolsforunity.vstuc"
        "github.copilot"
        "ms-vscode.vscode-ai"
        "bradlc.vscode-tailwindcss"
        "esbenp.prettier-vscode"
        "ms-vscode.vscode-json"
        "redhat.vscode-yaml"
        "ms-python.python"
    )
    
    for extension in "${extensions[@]}"; do
        log_info "Installing VS Code extension: $extension"
        code --install-extension "$extension" --force
    done
    
    log_success "VS Code extensions installed"
}

# Setup git configuration for Unity projects
setup_git_config() {
    log_info "Setting up Git configuration for Unity development..."
    
    # Unity-specific .gitignore template
    curl -s https://raw.githubusercontent.com/github/gitignore/main/Unity.gitignore > "$HOME/.unity-gitignore"
    
    # Git hooks for Unity projects
    mkdir -p "$HOME/.git-templates/hooks"
    
    cat > "$HOME/.git-templates/hooks/pre-commit" << 'EOF'
#!/bin/bash
# Unity project pre-commit hook

# Check if this is a Unity project
if [[ ! -f "ProjectSettings/ProjectSettings.asset" ]]; then
    exit 0
fi

# Validate C# scripts
echo "Validating Unity C# scripts..."
find Assets -name "*.cs" -type f | while read script; do
    # Basic syntax checking (requires mono/mcs)
    if command -v mcs &> /dev/null; then
        if ! mcs -t:library "$script" -out:/tmp/test.dll &> /dev/null; then
            echo "Syntax error in $script"
            exit 1
        fi
        rm -f /tmp/test.dll
    fi
done

echo "Unity pre-commit validation passed"
EOF
    
    chmod +x "$HOME/.git-templates/hooks/pre-commit"
    
    git config --global init.templatedir "$HOME/.git-templates"
    
    log_success "Git configuration for Unity projects complete"
}

# Main setup function
main() {
    log_info "Starting Unity development environment setup..."
    
    setup_unity_environment
    setup_ai_prompts
    setup_vscode_extensions
    setup_git_config
    
    log_success "Unity development environment setup complete!"
    log_info "Please restart your terminal to apply all changes"
    log_info "Run 'unity-help' to see available commands"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

### Terminal Productivity Enhancements
```bash
# ~/.zshrc additions for enhanced productivity

# FZF integration for Unity development
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

# Custom FZF functions for Unity
function fzf-unity-project() {
    local project=$(ls -1 "$UNITY_PROJECTS_PATH" | fzf --preview "ls -la $UNITY_PROJECTS_PATH/{}")
    if [[ -n "$project" ]]; then
        cd "$UNITY_PROJECTS_PATH/$project"
    fi
}

function fzf-unity-script() {
    local script=$(find "$UNITY_PROJECTS_PATH" -name "*.cs" -type f | fzf --preview "bat --color=always {}")
    if [[ -n "$script" ]]; then
        code "$script"
    fi
}

function fzf-unity-scene() {
    local scene=$(find "$UNITY_PROJECTS_PATH" -name "*.unity" -type f | fzf --preview "echo 'Unity Scene: {}' && head -20 {}")
    if [[ -n "$scene" ]]; then
        echo "Selected scene: $scene"
        # Open in Unity (requires additional AppleScript)
    fi
}

# Bind FZF functions to key combinations
bindkey '^P' fzf-unity-project  # Ctrl+P for project selection
bindkey '^S' fzf-unity-script   # Ctrl+S for script selection
bindkey '^U' fzf-unity-scene    # Ctrl+U for scene selection

# Zoxide integration for smart directory jumping
eval "$(zoxide init zsh)"

# Replace cd with zoxide
alias cd='z'

# Better ls with exa
alias ls='exa --icons'
alias ll='exa -alh --icons'
alias tree='exa --tree --icons'

# Better cat with bat
alias cat='bat'

# Better grep with ripgrep
alias grep='rg'

# Better find with fd
alias find='fd'
```

## 💡 Key Highlights

### Terminal Mastery Benefits
- **Custom Aliases**: Unity-specific shortcuts for rapid development workflow
- **AI Integration**: Command-line AI tools for code review and generation
- **Project Management**: Automated Unity project creation and organization
- **Build Automation**: Streamlined Unity build processes from terminal

### Advanced Shell Features
- **Smart Prompts**: Unity project information in terminal prompt
- **FZF Integration**: Fuzzy finding for Unity projects, scripts, and scenes
- **Auto-completion**: Custom completion for Unity development commands
- **Performance Monitoring**: Real-time Unity process and resource monitoring

### AI-Powered Development
- **Code Review Automation**: Instant AI-powered code analysis from terminal
- **Script Generation**: AI-assisted Unity script creation with templates
- **Documentation Generation**: Automated code documentation with AI
- **Performance Optimization**: AI-driven code optimization suggestions

### Workflow Optimization
- **One-Command Setup**: Complete Unity development environment initialization
- **Git Integration**: Unity-aware git workflows and commit automation
- **VS Code Integration**: Seamless editor integration with terminal workflows
- **Cross-Tool Communication**: Efficient data flow between terminal and GUI applications

## 🎯 Next Steps for Terminal Mastery
1. **Implement Custom Setup**: Run unity-dev-setup script for complete environment
2. **Configure FZF Integration**: Setup fuzzy finding for Unity development
3. **Create AI Workflows**: Implement AI-powered development commands
4. **Optimize Performance**: Monitor and optimize Unity development workflows
5. **Build Custom Tools**: Create project-specific terminal automation scripts