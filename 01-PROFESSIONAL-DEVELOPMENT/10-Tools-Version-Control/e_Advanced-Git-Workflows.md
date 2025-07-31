# @e-Advanced-Git-Workflows - Professional Git Mastery & AI-Enhanced Version Control

## 🎯 Learning Objectives
- Master advanced Git workflows for professional development teams
- Implement AI-enhanced Git automation and intelligent commit management
- Develop sophisticated branching strategies and merge conflict resolution
- Create automated code review and quality assurance pipelines

## 🔧 Core Advanced Git Concepts

### Professional Branching Strategies
```bash
# Gitflow workflow setup
git flow init

# Feature development workflow
git flow feature start new-player-system
# Work on feature...
git add .
git commit -m "feat: implement player movement system"
git flow feature finish new-player-system

# Release preparation
git flow release start v1.2.0
# Final testing and bug fixes...
git commit -m "fix: resolve player collision edge case"
git flow release finish v1.2.0

# Hotfix for production issues
git flow hotfix start critical-bug-fix
# Fix the critical issue...
git commit -m "fix: resolve game-breaking save corruption"
git flow hotfix finish critical-bug-fix
```

### Intelligent Commit Management
```bash
# Advanced commit message templates
# ~/.gitmessage template
# <type>[optional scope]: <description>
# 
# [optional body]
# 
# [optional footer(s)]
# 
# Types: feat, fix, docs, style, refactor, perf, test, chore
# Scope: api, ui, core, auth, etc.

# Configure commit template
git config --global commit.template ~/.gitmessage

# Interactive staging for precise commits
git add -p  # Stage specific chunks
git add -i  # Interactive staging menu

# Advanced commit amending
git commit --amend --no-edit  # Amend without changing message
git commit --fixup <commit-hash>  # Create fixup commit
git rebase -i --autosquash HEAD~5  # Auto-squash fixup commits
```

### Advanced Merge and Rebase Strategies
```bash
# Strategic merge options
git merge --no-ff feature-branch  # Always create merge commit
git merge --squash feature-branch  # Squash all commits into one

# Advanced rebase operations
git rebase -i HEAD~5  # Interactive rebase last 5 commits
git rebase --onto main feature-base feature-tip  # Rebase onto different branch

# Conflict resolution strategies
git config merge.tool vimdiff  # Set merge tool
git mergetool  # Launch merge tool for conflicts

# Cherry-picking with conflict resolution
git cherry-pick -x <commit-hash>  # Cherry-pick with source reference
git cherry-pick --continue  # Continue after resolving conflicts
```

### Git Hooks and Automation
```bash
#!/bin/bash
# .git/hooks/pre-commit - AI-enhanced pre-commit hook

echo "Running AI-enhanced pre-commit checks..."

# Check for debugging code
if grep -r "console.log\|Debug.Log\|debugger" --include="*.js" --include="*.cs" .; then
    echo "❌ Debug statements found. Please remove before committing."
    exit 1
fi

# Run AI code analysis
if command -v claude-analyze &> /dev/null; then
    echo "🤖 Running AI code analysis..."
    claude-analyze --staged-files
    if [ $? -ne 0 ]; then
        echo "❌ AI analysis found issues. Please review."
        exit 1
    fi
fi

# Format code automatically
if command -v prettier &> /dev/null; then
    echo "🎨 Auto-formatting staged files..."
    git diff --cached --name-only --diff-filter=ACM | xargs prettier --write
    git add .
fi

echo "✅ Pre-commit checks passed!"
```

## 🚀 AI/LLM Integration Opportunities

### Intelligent Commit Message Generation
```bash
#!/bin/bash
# AI-powered commit message generator script

generate_commit_message() {
    local diff_content=$(git diff --cached)
    local branch_name=$(git branch --show-current)
    
    # Call AI service to generate commit message
    local ai_message=$(curl -s -X POST "https://api.anthropic.com/v1/messages" \
        -H "Content-Type: application/json" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -d "{
            \"model\": \"claude-3-sonnet-20240229\",
            \"max_tokens\": 100,
            \"messages\": [{
                \"role\": \"user\",
                \"content\": \"Generate a concise, conventional commit message for these changes:\n\nBranch: $branch_name\n\nDiff:\n$diff_content\"
            }]
        }" | jq -r '.content[0].text')
    
    echo "$ai_message"
}

# Usage: ai-commit
alias ai-commit='git commit -m "$(generate_commit_message)"'
```

### Automated Code Review System
```bash
#!/bin/bash
# AI-powered code review automation

perform_ai_review() {
    local target_branch=${1:-main}
    local current_branch=$(git branch --show-current)
    
    echo "🤖 Performing AI code review..."
    echo "Comparing $current_branch with $target_branch"
    
    # Get diff for review
    local diff_content=$(git diff $target_branch...$current_branch)
    
    # AI analysis (placeholder for actual AI integration)
    echo "Analyzing code changes with AI..."
    
    # Generate review report
    cat << EOF > .git/ai-review-report.md
# AI Code Review Report

## Branch: $current_branch
## Target: $target_branch
## Date: $(date)

## Analysis Summary
- **Code Quality**: ⭐⭐⭐⭐⭐
- **Security**: ✅ No issues found
- **Performance**: ⚠️ Consider optimization in player movement
- **Maintainability**: ✅ Good structure

## Recommendations
1. Add null checks in PlayerController.cs:45
2. Consider caching expensive calculations in GameManager
3. Add unit tests for new collision detection logic

## Automated Fixes Applied
- Code formatting
- Import optimization
- Documentation updates
EOF
    
    echo "📋 Review report generated: .git/ai-review-report.md"
}

# Git alias for AI review
git config --global alias.ai-review '!bash -c "perform_ai_review"'
```

### Smart Branch Management
```bash
#!/bin/bash
# Intelligent branch management with AI suggestions

smart_branch_cleanup() {
    echo "🧹 Analyzing branches for cleanup recommendations..."
    
    # Get merged branches
    local merged_branches=$(git branch --merged main | grep -v main | grep -v '*')
    
    # Get stale branches (no commits in 30 days)
    local stale_branches=$(git for-each-ref --format='%(refname:short) %(committerdate)' refs/heads | 
        awk '$2 < "'$(date -d '30 days ago' -I)'"' | cut -d' ' -f1)
    
    echo "📊 Branch Analysis Report:"
    echo "Merged branches (safe to delete):"
    echo "$merged_branches" | while read branch; do
        if [ ! -z "$branch" ]; then
            echo "  - $branch"
        fi
    done
    
    echo "Stale branches (consider reviewing):"
    echo "$stale_branches" | while read branch; do
        if [ ! -z "$branch" ]; then
            echo "  - $branch"
        fi
    done
    
    # Interactive cleanup
    read -p "Delete merged branches? (y/N): " confirm
    if [[ $confirm =~ ^[Yy]$ ]]; then
        echo "$merged_branches" | xargs -n 1 git branch -d
        echo "✅ Merged branches deleted"
    fi
}

# Git alias for smart cleanup
git config --global alias.smart-cleanup '!bash -c "smart_branch_cleanup"'
```

## 💡 Key Highlights

### Professional Git Workflow Best Practices
- **Consistent Branching**: Use gitflow or GitHub flow consistently across team
- **Atomic Commits**: Each commit should represent one logical change
- **Descriptive Messages**: Follow conventional commit format for clarity
- **Regular Integration**: Merge/rebase frequently to avoid large conflicts
- **Protected Branches**: Use branch protection rules for main/master

### Advanced Git Commands for Daily Use
```bash
# Powerful log and history commands
git log --oneline --graph --all --decorate  # Visual commit history
git log -p --follow filename  # Follow file history through renames
git log --author="John" --since="2 weeks ago"  # Filter commits by author/date

# Advanced diff and comparison
git diff --word-diff  # Word-level diff highlighting
git diff --stat  # Summary of changes
git diff main...feature-branch  # Three-dot diff (feature changes only)

# Stashing and temporary storage
git stash push -m "WIP: working on feature X"  # Named stash
git stash push --include-untracked  # Include untracked files
git stash apply stash@{2}  # Apply specific stash

# Advanced searching and blame
git grep "function.*player" -- "*.cs"  # Search in tracked files
git blame -L 10,20 filename  # Blame specific lines
git log -S "playerHealth" --pickaxe-regex  # Search for code changes
```

### AI-Enhanced Git Workflow Benefits
- **Intelligent Commit Messages**: AI generates descriptive, conventional commits
- **Automated Code Reviews**: AI analyzes changes for quality and security issues
- **Smart Conflict Resolution**: AI suggests optimal merge strategies
- **Branch Management**: AI recommends cleanup and optimization strategies
- **Workflow Optimization**: AI analyzes team patterns and suggests improvements

### Git Configuration for Professional Development
```bash
# Essential Git configuration
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"
git config --global core.editor "code --wait"
git config --global merge.tool "vscode"
git config --global diff.tool "vscode"

# Advanced configuration
git config --global pull.rebase true  # Always rebase on pull
git config --global push.default simple  # Safe push behavior
git config --global core.autocrlf true  # Handle line endings (Windows)
git config --global alias.unstage "reset HEAD --"  # Unstage alias
git config --global alias.last "log -1 HEAD"  # Show last commit

# Security and signing
git config --global commit.gpgsign true  # Sign commits with GPG
git config --global user.signingkey YOUR_GPG_KEY_ID
```

### Integration with Unity and Game Development
- **Large File Support**: Use Git LFS for binary assets
- **Ignore Templates**: Comprehensive .gitignore for Unity projects
- **Asset Serialization**: Configure Unity for VCS-friendly serialization
- **Binary Merge Tools**: Set up merge tools for Unity scenes and prefabs

This advanced Git knowledge enables professional-level version control with AI-enhanced automation, ensuring high-quality code management and streamlined development workflows.