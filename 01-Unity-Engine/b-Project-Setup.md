# Unity Project Setup & Organization

## Overview
Master Unity project creation, organization, and collaborative workflows essential for professional game development.

## Key Concepts

**Template Selection Process:**
1. **2D Projects:** Use 2D URP template for modern 2D games
2. **3D Projects:** Use 3D URP template (better performance than Built-in)
3. **Mobile Games:** Use Mobile-optimized templates
4. **VR Projects:** Use VR template with XR Toolkit

**Post-Creation Setup:**
- Configure project settings immediately
- Set up folder structure using naming conventions
- Initialize version control with proper .gitignore
- Install essential packages for your project type

**Folder Structure Best Practices:**
- Use numbered prefixes (01_, 02_) to control folder order
- Group related assets together (Scripts/Player, Scripts/Enemies)
- Separate scenes by purpose (Main gameplay, Testing, UI scenes)
- Organize art assets by type and usage context

### Version Control Setup

**Git Configuration for Unity:**
- Initialize repository with proper Unity .gitignore
- Use Git LFS for large assets (textures, audio, models)
- Set up meaningful commit messages and branching strategy
- Configure merge tools for scene and prefab conflicts

**Essential Git LFS Tracking:**
```
*.psd, *.fbx, *.obj (3D assets)
*.png, *.jpg, *.tga (textures)  
*.wav, *.mp3, *.ogg (audio)
*.mp4, *.mov (video)
```

**Essential Packages by Project Type:**

**All Projects:**
- Input System (modern input handling)
- TextMeshPro (better text rendering)
- Cinemachine (camera management)

**3D Projects:**
- Universal Render Pipeline
- Post Processing Stack
- ProBuilder (level prototyping)

**2D Projects:**
- 2D Sprite/Tilemap packages
- 2D Lights/Shadows
- 2D Animation system

**Mobile Projects:**
- Addressables (memory management)
- Analytics (player data)
- Unity Ads (monetization)

**Critical Settings to Configure:**

**Player Settings:**
- Company/Product name for builds
- Bundle version and build numbers
- Target platforms and architectures
- Screen resolution and orientation

**Quality Settings:**
- Anti-aliasing levels per platform
- Shadow quality and distance
- Texture quality for different devices
- VSync settings for performance

**Graphics Settings:**
- Render pipeline selection (URP recommended)
- Lighting mode (realtime vs baked)
- Post-processing effects configuration

### Project Setup Workflow

**Day 1 - Initial Setup:**
1. Create project with appropriate template
2. Configure essential settings (company name, version)
3. Set up folder structure using numbering system
4. Initialize Git with Unity .gitignore
5. Install core packages (Input System, TextMeshPro)

**Week 1 - Development Framework:**
1. Create GameManager singleton pattern
2. Implement scene management system
3. Set up save/load data persistence
4. Configure audio and input systems
5. Establish UI framework and navigation

**GameManager Singleton Pattern:**
- Manages game states (Menu, Playing, Paused, GameOver)
- Handles scene transitions and loading
- Persists across scene changes with DontDestroyOnLoad
- Centralizes core game systems initialization

**Scene Management System:**
- Async scene loading with progress indicators
- Loading screen management during transitions
- Memory cleanup between scene switches
- Save/load integration with scene persistence

### Common Interview Questions

**"How do you organize a Unity project?"**
- Explain numbered folder structure (01_Scripts, 02_Scenes, etc.)
- Discuss version control setup with Git LFS
- Mention team collaboration workflows and naming conventions

**"What's your project setup process?"**
- Template selection based on project requirements
- Essential package installation strategy
- Configuration of player settings and quality settings

**"How do you handle version control with Unity?"**
- Git with LFS for large assets
- Proper .gitignore configuration for Unity
- Merge conflict resolution for scenes and prefabs

### Key Takeaways

**Project Organization Principles:**
- Use consistent naming and folder structure
- Set up version control from day one
- Configure essential settings before development
- Install packages based on project needs

**Professional Workflow:**
- Create reusable project templates
- Establish team coding conventions early
- Use AI tools to generate boilerplate code
- Implement proper scene management patterns