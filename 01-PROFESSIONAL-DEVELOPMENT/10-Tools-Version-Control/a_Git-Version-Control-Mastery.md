# Git Version Control Mastery

## Overview
Master Git version control system for professional software development, including advanced workflows, collaboration strategies, and Unity-specific best practices.

## Key Concepts

### Git Fundamentals

**Core Git Operations:**
- **Repository Management:** Initialize, clone, and configure repositories
- **Staging and Committing:** Track changes and create meaningful commits
- **Branching:** Create, merge, and manage development branches
- **Remote Operations:** Push, pull, and sync with remote repositories

**Essential Git Commands:**
```bash
# Repository initialization and cloning
git init                          # Initialize new repository
git clone <repository-url>        # Clone existing repository
git remote add origin <url>       # Add remote repository

# Basic workflow commands
git status                        # Check repository status
git add <file-name>              # Stage specific file
git add .                        # Stage all changes
git commit -m "commit message"    # Commit staged changes
git push origin <branch-name>     # Push to remote branch
git pull origin <branch-name>     # Pull from remote branch

# Branch management
git branch                        # List all branches
git branch <branch-name>          # Create new branch
git checkout <branch-name>        # Switch to branch
git checkout -b <branch-name>     # Create and switch to new branch
git merge <branch-name>           # Merge branch into current branch
git branch -d <branch-name>       # Delete branch

# History and information
git log                          # View commit history
git log --oneline               # Condensed commit history
git show <commit-hash>          # Show commit details
git diff                        # Show unstaged changes
git diff --staged               # Show staged changes
```

**Git Configuration Best Practices:**
```bash
# Global configuration
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global core.editor "code --wait"
git config --global init.defaultBranch main

# Unity-specific configuration
git config --global core.autocrlf true          # Windows line endings
git config --global core.filemode false         # Ignore file permission changes
git config --global filter.lfs.clean "git-lfs clean -- %f"
git config --global filter.lfs.smudge "git-lfs smudge -- %f"
git config --global filter.lfs.process "git-lfs filter-process"
git config --global filter.lfs.required true

# Set up aliases for common commands
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage "reset HEAD --"
git config --global alias.last "log -1 HEAD"
git config --global alias.visual "!gitk"
```

### Advanced Git Workflows

**Feature Branch Workflow:**
```bash
# Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/user-authentication

# Work on feature
git add .
git commit -m "Add user login functionality"
git commit -m "Implement password validation"
git commit -m "Add user session management"

# Push feature branch
git push origin feature/user-authentication

# Create pull request through GitHub/GitLab interface

# After review, merge and cleanup
git checkout main
git pull origin main
git branch -d feature/user-authentication
git push origin --delete feature/user-authentication
```

**Git Flow Workflow:**
```bash
# Initialize git flow
git flow init

# Start new feature
git flow feature start user-authentication
# Work on feature...
git flow feature finish user-authentication

# Start new release
git flow release start v1.2.0
# Prepare release...
git flow release finish v1.2.0

# Handle hotfix
git flow hotfix start critical-bug-fix
# Fix the bug...
git flow hotfix finish critical-bug-fix
```

**Rebasing and History Management:**
```bash
# Interactive rebase to clean up commits
git rebase -i HEAD~3                # Rebase last 3 commits
git rebase -i <commit-hash>         # Rebase from specific commit

# Rebase feature branch onto main
git checkout feature/new-feature
git rebase main
git push --force-with-lease origin feature/new-feature

# Squash commits during merge
git merge --squash feature/new-feature
git commit -m "Add new feature with complete implementation"

# Amend last commit
git commit --amend -m "Updated commit message"
git commit --amend --no-edit        # Add changes to last commit

# Reset operations
git reset --soft HEAD~1             # Undo last commit, keep changes staged
git reset --mixed HEAD~1            # Undo last commit, unstage changes
git reset --hard HEAD~1             # Undo last commit, discard changes
```

### Unity-Specific Git Setup

**Unity .gitignore Configuration:**
```gitignore
# Unity generated files
[Ll]ibrary/
[Tt]emp/
[Oo]bj/
[Bb]uild/
[Bb]uilds/
[Ll]ogs/
[Mm]emoryCaptures/

# Unity cache and temporary files
/[Ll]ibrary/
/[Tt]emp/
/[Oo]bj/
/[Bb]uild/
/[Bb]uilds/
/[Ll]ogs/
/[Uu]ser[Ss]ettings/

# Unity auto generated files
*.pidb
*.booproj
*.svd
*.userprefs
*.csproj
*.unityproj
*.sln
*.suo
*.tmp
*.user
*.userprefs
*.pidb
*.booproj

# Unity specific
*.unitypackage
*.unityproj
.consulo/
*.csproj
*.unityproj
*.sln
*.suo
*.tmp
*.user
*.userprefs
*.pidb
*.booproj
*.svd

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Visual Studio / VS Code
.vscode/
.vs/
*.userprefs

# JetBrains Rider
.idea/
*.sln.iml

# Build results
[Dd]ebug/
[Dd]ebugPublic/
[Rr]elease/
[Rr]eleases/
x64/
x86/
[Aa][Rr][Mm]/
[Aa][Rr][Mm]64/
bld/
[Bb]in/
[Oo]bj/
[Ll]og/

# Asset bundles
*.assetbundle
*.bundle

# Addressables
/[Aa]ssets/[Aa]ddressable[Aa]ssets[Dd]ata/*/*.bin*
/[Aa]ssets/[Aa]ddressable[Aa]ssets[Dd]ata/*/*.json*
/[Aa]ssets/[Ss]treamingAssets/aa.meta
/[Aa]ssets/[Ss]treamingAssets/aa/*
```

**Git LFS Setup for Unity:**
```bash
# Install Git LFS
git lfs install

# Track Unity binary files
git lfs track "*.psd"
git lfs track "*.png"
git lfs track "*.jpg"
git lfs track "*.jpeg"
git lfs track "*.gif"
git lfs track "*.bmp"
git lfs track "*.tga"
git lfs track "*.tiff"
git lfs track "*.iff"
git lfs track "*.pict"
git lfs track "*.dds"
git lfs track "*.xcf"

# Audio files
git lfs track "*.mp3"
git lfs track "*.wav"
git lfs track "*.ogg"
git lfs track "*.aif"
git lfs track "*.aiff"
git lfs track "*.mod"
git lfs track "*.it"
git lfs track "*.s3m"
git lfs track "*.xm"

# Video files
git lfs track "*.mov"
git lfs track "*.avi"
git lfs track "*.asf"
git lfs track "*.mpg"
git lfs track "*.mpeg"
git lfs track "*.mp4"
git lfs track "*.flv"
git lfs track "*.ogv"

# 3D models
git lfs track "*.fbx"
git lfs track "*.obj"
git lfs track "*.max"
git lfs track "*.blend"
git lfs track "*.dae"
git lfs track "*.mb"
git lfs track "*.ma"
git lfs track "*.3ds"
git lfs track "*.dfx"
git lfs track "*.c4d"
git lfs track "*.lwo"
git lfs track "*.lwo2"
git lfs track "*.abc"

# Unity packages and assets
git lfs track "*.unitypackage"
git lfs track "*.asset"
git lfs track "*.cubemap"
git lfs track "*.unity"

# Add .gitattributes to repository
git add .gitattributes
git commit -m "Configure Git LFS for Unity project"
```

### Collaboration and Code Review

**Collaborative Development Workflow:**
```bash
# Setup for team collaboration
git clone <repository-url>
cd project-name

# Create personal development branch
git checkout -b develop/<your-name>
git push -u origin develop/<your-name>

# Daily workflow
git checkout main
git pull origin main                # Get latest changes
git checkout develop/<your-name>
git rebase main                     # Rebase your branch onto main
git push --force-with-lease origin develop/<your-name>

# Feature development
git checkout -b feature/inventory-system
# ... work on feature ...
git add .
git commit -m "Implement inventory item management"

# Push and create pull request
git push origin feature/inventory-system
# Create PR through GitHub/GitLab interface

# Address review feedback
git add .
git commit -m "Address code review feedback"
git push origin feature/inventory-system

# After merge, cleanup
git checkout main
git pull origin main
git branch -d feature/inventory-system
```

**Code Review Best Practices:**
```markdown
## Pull Request Template

### Description
Brief description of changes and why they were made.

### Changes Made
- [ ] Added new inventory system
- [ ] Updated UI for item management
- [ ] Added unit tests for inventory logic
- [ ] Updated documentation

### Testing Done
- [ ] Unit tests pass
- [ ] Manual testing completed
- [ ] Performance tested
- [ ] Works on target platforms

### Screenshots
[Include screenshots of UI changes or new features]

### Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes
```

### Advanced Git Techniques

**Conflict Resolution:**
```bash
# When merge conflicts occur
git status                          # See conflicted files
# Edit files to resolve conflicts
git add <resolved-file>            # Mark conflicts as resolved
git commit                         # Complete the merge

# Use merge tools
git config --global merge.tool vimdiff
git mergetool                      # Launch merge tool

# Abort merge if needed
git merge --abort

# Cherry-pick specific commits
git cherry-pick <commit-hash>      # Apply specific commit
git cherry-pick -n <commit-hash>   # Cherry-pick without committing
```

**Git Hooks for Unity Projects:**
```bash
#!/bin/sh
# pre-commit hook to prevent large files
# Save as .git/hooks/pre-commit

# Check for large files
git diff --cached --name-only | while read file; do
    if [ -f "$file" ]; then
        size=$(wc -c <"$file")
        if [ $size -gt 10485760 ]; then  # 10MB
            echo "Error: $file is larger than 10MB"
            echo "Use Git LFS for large files"
            exit 1
        fi
    fi
done

# Run Unity tests before commit
if [ -d "Assets" ]; then
    echo "Running Unity tests..."
    # Add Unity test runner command here
fi
```

**Repository Maintenance:**
```bash
# Clean up repository
git gc --aggressive --prune=now    # Garbage collect and optimize
git remote prune origin            # Remove stale remote branches
git branch --merged | grep -v "\*\|main\|develop" | xargs -n 1 git branch -d

# Find large files in repository
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | sed -n 's/^blob //p' | sort --numeric-sort --key=2 | tail -20

# Analyze repository size
git count-objects -vH

# Remove sensitive data (use carefully!)
git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch sensitive-file.txt' --prune-empty --tag-name-filter cat -- --all
```

## Practical Applications

### Team Development Scenarios

**Multi-Developer Unity Project:**
```bash
# Project lead setup
git init unity-game-project
cd unity-game-project

# Create initial Unity project structure
mkdir Assets Scripts Resources
echo "# Unity Game Project" > README.md

# Setup initial files
cp standard-unity.gitignore .gitignore
git lfs track "*.fbx"
git lfs track "*.png"
# ... other LFS configurations

git add .
git commit -m "Initial Unity project setup"
git remote add origin https://github.com/team/unity-game-project.git
git push -u origin main

# Create development branches
git checkout -b develop
git push -u origin develop

# Developer workflow
git checkout -b feature/player-movement
# ... implement player movement ...
git add Assets/Scripts/PlayerController.cs
git commit -m "Add basic player movement controller

- Implement WASD movement
- Add mouse look functionality
- Handle ground detection"

git push origin feature/player-movement
# Create pull request for review
```

**Release Management:**
```bash
# Prepare release branch
git checkout -b release/v1.0.0
git push -u origin release/v1.0.0

# Version bump and changelog
echo "v1.0.0" > VERSION
git add VERSION
git commit -m "Bump version to v1.0.0"

# Final testing and bug fixes
git commit -m "Fix critical player respawn bug"
git commit -m "Update UI scaling for mobile devices"

# Merge to main and tag
git checkout main
git merge --no-ff release/v1.0.0
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin main
git push origin v1.0.0

# Merge back to develop
git checkout develop
git merge --no-ff release/v1.0.0
git push origin develop

# Cleanup
git branch -d release/v1.0.0
git push origin --delete release/v1.0.0
```

### Emergency Procedures

**Hotfix Workflow:**
```bash
# Critical bug found in production
git checkout main
git pull origin main
git checkout -b hotfix/critical-save-bug

# Fix the bug
git add Assets/Scripts/SaveSystem.cs
git commit -m "Fix critical save data corruption bug

- Validate save data before writing
- Add error handling for corrupted files
- Implement backup save mechanism"

# Test the fix
git push origin hotfix/critical-save-bug
# Fast-track review and merge

# Deploy hotfix
git checkout main
git merge --no-ff hotfix/critical-save-bug
git tag -a v1.0.1 -m "Hotfix v1.0.1 - Critical save bug fix"
git push origin main
git push origin v1.0.1

# Merge back to develop
git checkout develop
git merge --no-ff hotfix/critical-save-bug
git push origin develop

# Cleanup
git branch -d hotfix/critical-save-bug
```

**Disaster Recovery:**
```bash
# Recover from accidental force push
git reflog                          # Find lost commits
git reset --hard HEAD@{2}          # Reset to previous state
git push --force-with-lease origin main

# Recover deleted branch
git reflog --all                    # Find branch reference
git checkout -b recovered-branch <commit-hash>

# Undo public merge
git revert -m 1 <merge-commit-hash>
git push origin main
```

## Interview Preparation

### Git Interview Questions

**Technical Questions:**
- "Explain the difference between `git merge` and `git rebase`"
- "How do you resolve merge conflicts in Unity scene files?"
- "What is Git LFS and why is it important for Unity projects?"
- "Describe a Git workflow suitable for a team of 5 developers"

**Practical Scenarios:**
- "You accidentally committed sensitive data. How do you remove it?"
- "A team member force-pushed and overwrote important commits. How do you recover?"
- "How do you set up a CI/CD pipeline with Git hooks?"
- "Explain how you would handle binary assets in a Unity project with Git"

### Key Takeaways

**Git Mastery Essentials:**
- Master branching strategies for team collaboration
- Understand Unity-specific Git configuration and LFS setup
- Practice conflict resolution and repository maintenance
- Implement proper code review processes and PR workflows

**Professional Development:**
- Learn advanced Git features like interactive rebase and cherry-picking
- Set up automated workflows with Git hooks and CI/CD integration
- Understand different Git workflows (Git Flow, GitHub Flow, GitLab Flow)
- Practice disaster recovery and emergency hotfix procedures