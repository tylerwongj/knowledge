# @02-Project-Setup - Unity Project Creation & Organization

## 🎯 Learning Objectives
- Master Unity project creation and template selection
- Understand project folder structure and organization best practices
- Learn version control setup and collaborative workflows
- Use AI tools to generate project templates and boilerplate code

---

## 🚀 Creating New Unity Projects

### Project Creation Workflow

```csharp
// Unity Hub Project Creation - Best Practices
// 1. Choose appropriate template based on project type
// 2. Set proper naming conventions
// 3. Configure version control from the start
// 4. Set up folder structure immediately

public class ProjectSetupChecklist 
{
    // Essential setup steps after project creation
    void PostProjectCreationSetup()
    {
        SetupFolderStructure();
        ConfigureProjectSettings();
        SetupVersionControl();
        ImportEssentialPackages();
        CreateBasicScenes();
    }
}
```

### Unity Templates

**2D Templates:**
- **2D Core** - Basic 2D setup with sprite rendering
- **2D Mobile** - Optimized for mobile devices
- **2D URP** - Universal Render Pipeline for 2D

**3D Templates:**
- **3D Core** - Standard built-in render pipeline
- **3D URP** - Universal Render Pipeline (recommended)
- **3D HDRP** - High Definition Render Pipeline (high-end)

**Specialized Templates:**
- **VR** - Virtual Reality setup with XR Toolkit
- **Mobile 3D** - 3D optimized for mobile platforms
- **Microgame Templates** - Learning-focused mini-projects

---

## 📁 Project Folder Structure

### Standard Unity Project Organization

```
MyUnityProject/
├── Assets/
│   ├── 01_Scripts/
│   │   ├── Player/
│   │   ├── Enemies/
│   │   ├── Managers/
│   │   ├── UI/
│   │   └── Utilities/
│   ├── 02_Scenes/
│   │   ├── Main/
│   │   ├── Levels/
│   │   └── Testing/
│   ├── 03_Prefabs/
│   │   ├── Characters/
│   │   ├── Environment/
│   │   ├── UI/
│   │   └── Effects/
│   ├── 04_Materials/
│   │   ├── Characters/
│   │   ├── Environment/
│   └── 05_Art/
│       ├── Textures/
│       ├── Models/
│       ├── Sprites/
│       └── Audio/
├── ProjectSettings/
├── Packages/
└── Logs/
```

### Folder Organization Script

```csharp
using UnityEngine;
using UnityEditor;
using System.IO;

public class ProjectStructureSetup
{
    [MenuItem("Tools/Setup Project Structure")]
    public static void CreateProjectFolders()
    {
        string[] folders = {
            "Assets/01_Scripts/Player",
            "Assets/01_Scripts/Enemies", 
            "Assets/01_Scripts/Managers",
            "Assets/01_Scripts/UI",
            "Assets/01_Scripts/Utilities",
            "Assets/02_Scenes/Main",
            "Assets/02_Scenes/Levels",
            "Assets/02_Scenes/Testing",
            "Assets/03_Prefabs/Characters",
            "Assets/03_Prefabs/Environment",
            "Assets/03_Prefabs/UI",
            "Assets/03_Prefabs/Effects",
            "Assets/04_Materials/Characters",
            "Assets/04_Materials/Environment",
            "Assets/05_Art/Textures",
            "Assets/05_Art/Models",
            "Assets/05_Art/Sprites",
            "Assets/05_Art/Audio"
        };
        
        foreach (string folder in folders)
        {
            if (!AssetDatabase.IsValidFolder(folder))
            {
                string[] pathParts = folder.Split('/');
                string currentPath = pathParts[0];
                
                for (int i = 1; i < pathParts.Length; i++)
                {
                    string nextPath = currentPath + "/" + pathParts[i];
                    if (!AssetDatabase.IsValidFolder(nextPath))
                    {
                        AssetDatabase.CreateFolder(currentPath, pathParts[i]);
                    }
                    currentPath = nextPath;
                }
            }
        }
        
        AssetDatabase.Refresh();
        Debug.Log("Project structure created successfully!");
    }
}
```

---

## ⚙️ Essential Project Settings

### Player Settings Configuration

```csharp
// Essential Player Settings to configure immediately
public class ProjectSettingsConfig
{
    // Platform-specific settings
    void ConfigurePlayerSettings()
    {
        // Company & Product Info
        PlayerSettings.companyName = "YourStudioName";
        PlayerSettings.productName = "YourGameName";
        
        // Build Settings
        PlayerSettings.bundleVersion = "1.0.0";
        PlayerSettings.Android.bundleVersionCode = 1;
        
        // Graphics Settings
        PlayerSettings.defaultScreenWidth = 1920;
        PlayerSettings.defaultScreenHeight = 1080;
        PlayerSettings.fullScreenMode = FullScreenMode.FullScreenWindow;
        
        // Input Settings
        PlayerSettings.useOldInputManagerInNewInputSystem = false;
    }
    
    // Quality Settings optimization
    void OptimizeQualitySettings()
    {
        // Mobile optimization
        QualitySettings.antiAliasing = 2;
        QualitySettings.shadowResolution = ShadowResolution.Medium;
        QualitySettings.shadowDistance = 50f;
        QualitySettings.vSyncCount = 1;
    }
}
```

### Graphics Settings

```csharp
using UnityEngine;
using UnityEngine.Rendering;

public class GraphicsSetup
{
    // Render Pipeline configuration
    void SetupRenderPipeline()
    {
        // URP setup for better performance and visuals
        var urpAsset = Resources.Load<UniversalRenderPipelineAsset>("UniversalRP-HighQuality");
        if (urpAsset != null)
        {
            GraphicsSettings.renderPipelineAsset = urpAsset;
        }
    }
    
    // Lighting settings for consistent visuals
    void ConfigureLighting()
    {
        RenderSettings.ambientMode = AmbientMode.Trilight;
        RenderSettings.ambientSkyColor = Color.white * 0.2f;
        RenderSettings.ambientEquatorColor = Color.white * 0.1f;
        RenderSettings.ambientGroundColor = Color.black;
    }
}
```

---

## 🔧 Version Control Setup

### Git Configuration for Unity

```bash
# Initialize git repository
git init

# Essential Unity .gitignore
echo "# Unity generated files
[Ll]ibrary/
[Tt]emp/
[Oo]bj/
[Bb]uild/
[Bb]uilds/
[Ll]ogs/
[Uu]ser[Ss]ettings/

# Memory Dumps
*.tmp
*.dmp

# Asset meta data should only be ignored when the corresponding asset is also ignored
!/[Aa]ssets/**/*.meta

# Uncomment this line if you wish to ignore the asset store tools plugin
# /[Aa]ssets/AssetStoreTools*

# Visual Studio cache directory
.vs/

# Gradle cache directory
.gradle/

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db" > .gitignore

# Initial commit
git add .
git commit -m "Initial Unity project setup"
```

### Git LFS for Large Assets

```bash
# Install Git LFS
git lfs install

# Track large Unity files
git lfs track "*.psd"
git lfs track "*.fbx"
git lfs track "*.obj"
git lfs track "*.png"
git lfs track "*.jpg"
git lfs track "*.tga"
git lfs track "*.wav"
git lfs track "*.mp3"
git lfs track "*.ogg"
git lfs track "*.mp4"
git lfs track "*.mov"

# Commit LFS configuration
git add .gitattributes
git commit -m "Add Git LFS configuration for Unity assets"
```

---

## 📦 Package Management

### Essential Packages Setup

```csharp
using UnityEngine;
using UnityEditor.PackageManager;
using UnityEditor.PackageManager.Requests;

public class PackageSetup
{
    private static AddRequest[] packageRequests;
    
    [MenuItem("Tools/Install Essential Packages")]
    public static void InstallEssentialPackages()
    {
        string[] essentialPackages = {
            "com.unity.inputsystem",           // New Input System
            "com.unity.cinemachine",           // Camera system
            "com.unity.timeline",              // Cutscenes and animations  
            "com.unity.postprocessing",        // Visual effects
            "com.unity.textmeshpro",           // Better text rendering
            "com.unity.addressables",          // Asset management
            "com.unity.analytics",             // Player analytics
            "com.unity.ads"                    // Monetization
        };
        
        foreach (string package in essentialPackages)
        {
            Client.Add(package);
        }
        
        Debug.Log("Installing essential packages...");
    }
    
    // Development/debugging packages
    static string[] developmentPackages = {
        "com.unity.test-framework",         // Unit testing
        "com.unity.ide.visualstudio",      // VS integration
        "com.unity.recorder",               // Screen recording
        "com.unity.performance.profile-analyzer" // Profiling
    };
}
```

### Package Manifest Configuration

```json
{
  "dependencies": {
    "com.unity.collab-proxy": "2.0.7",
    "com.unity.feature.development": "1.0.1",
    "com.unity.inputsystem": "1.7.0",
    "com.unity.postprocessing": "3.2.2",
    "com.unity.render-pipelines.universal": "14.0.8",
    "com.unity.textmeshpro": "3.0.6",
    "com.unity.timeline": "1.7.5",
    "com.unity.ugui": "1.0.0",
    "com.unity.visualscripting": "1.9.0",
    "com.unity.modules.ai": "1.0.0",
    "com.unity.modules.animation": "1.0.0",
    "com.unity.modules.physics": "1.0.0",
    "com.unity.modules.physics2d": "1.0.0",
    "com.unity.modules.ui": "1.0.0"
  }
}
```

---

## 🏗️ Project Templates & Boilerplate

### Game Manager Template

```csharp
using UnityEngine;
using UnityEngine.SceneManagement;

public class GameManager : MonoBehaviour
{
    [Header("Game State")]
    public GameState currentState = GameState.MainMenu;
    
    [Header("Scene References")]
    [SerializeField] private string mainMenuScene = "MainMenu";
    [SerializeField] private string gameplayScene = "Gameplay";
    [SerializeField] private string gameOverScene = "GameOver";
    
    public static GameManager Instance { get; private set; }
    
    // Events for game state changes
    public static event System.Action<GameState> OnGameStateChanged;
    
    void Awake()
    {
        // Singleton pattern
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void Start()
    {
        InitializeGame();
    }
    
    private void InitializeGame()
    {
        // Load saved settings
        LoadGameSettings();
        
        // Initialize core systems
        InitializeAudio();
        InitializeInput();
        
        ChangeGameState(GameState.MainMenu);
    }
    
    public void ChangeGameState(GameState newState)
    {
        currentState = newState;
        OnGameStateChanged?.Invoke(newState);
        
        switch (newState)
        {
            case GameState.MainMenu:
                Time.timeScale = 1f;
                break;
            case GameState.Playing:
                Time.timeScale = 1f;
                break;
            case GameState.Paused:
                Time.timeScale = 0f;
                break;
            case GameState.GameOver:
                Time.timeScale = 1f;
                break;
        }
    }
    
    public void LoadScene(string sceneName)
    {
        SceneManager.LoadScene(sceneName);
    }
    
    private void LoadGameSettings()
    {
        // Load player preferences, settings, etc.
        AudioListener.volume = PlayerPrefs.GetFloat("MasterVolume", 1f);
    }
    
    private void InitializeAudio()
    {
        // Setup audio systems
    }
    
    private void InitializeInput()
    {
        // Setup input systems
    }
}

public enum GameState
{
    MainMenu,
    Playing,
    Paused,
    GameOver
}
```

### Scene Management Template

```csharp
using UnityEngine;
using UnityEngine.SceneManagement;
using System.Collections;

public class SceneController : MonoBehaviour
{
    [Header("Loading Settings")]
    [SerializeField] private GameObject loadingScreen;
    [SerializeField] private UnityEngine.UI.Slider progressBar;
    
    public static SceneController Instance { get; private set; }
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    public void LoadSceneAsync(string sceneName)
    {
        StartCoroutine(LoadSceneCoroutine(sceneName));
    }
    
    private IEnumerator LoadSceneCoroutine(string sceneName)
    {
        // Show loading screen
        if (loadingScreen != null)
            loadingScreen.SetActive(true);
        
        // Begin async loading
        AsyncOperation asyncLoad = SceneManager.LoadSceneAsync(sceneName);
        asyncLoad.allowSceneActivation = false;
        
        // Update progress bar
        while (!asyncLoad.isDone)
        {
            float progress = Mathf.Clamp01(asyncLoad.progress / 0.9f);
            
            if (progressBar != null)
                progressBar.value = progress;
            
            // Scene is ready to activate
            if (asyncLoad.progress >= 0.9f)
            {
                yield return new WaitForSeconds(0.5f); // Minimum loading time
                asyncLoad.allowSceneActivation = true;
            }
            
            yield return null;
        }
        
        // Hide loading screen
        if (loadingScreen != null)
            loadingScreen.SetActive(false);
    }
}
```

---

## 🤖 AI-Powered Project Setup

### Using AI for Project Generation

**Project Setup Prompts:**
> "Create a Unity project structure for a 2D platformer game with player character, enemies, collectibles, and UI systems. Include folder organization and basic manager scripts."

**Boilerplate Generation:**
> "Generate a Unity GameManager script with scene management, save/load system, and game state handling for a mobile puzzle game."

**Package Recommendations:**
> "What Unity packages should I install for a multiplayer FPS game? Include networking, input system, and rendering pipeline recommendations."

### AI-Generated Project Templates

```csharp
// AI-Generated Project Initializer
using UnityEngine;
using UnityEditor;

public class AIProjectSetup : EditorWindow
{
    private string projectType = "2D Platformer";
    private bool includeNetworking = false;
    private bool includeMobileOptimizations = false;
    
    [MenuItem("AI Tools/Project Setup Wizard")]
    public static void ShowWindow()
    {
        GetWindow<AIProjectSetup>("AI Project Setup");
    }
    
    void OnGUI()
    {
        GUILayout.Label("AI-Powered Project Setup", EditorStyles.boldLabel);
        
        projectType = EditorGUILayout.TextField("Project Type:", projectType);
        includeNetworking = EditorGUILayout.Toggle("Include Networking", includeNetworking);
        includeMobileOptimizations = EditorGUILayout.Toggle("Mobile Optimizations", includeMobileOptimizations);
        
        if (GUILayout.Button("Generate Project Structure"))
        {
            GenerateProjectStructure();
        }
        
        if (GUILayout.Button("Ask AI for Recommendations"))
        {
            Debug.Log($"AI Prompt: 'Set up Unity project for {projectType} with networking: {includeNetworking}, mobile: {includeMobileOptimizations}'");
        }
    }
    
    private void GenerateProjectStructure()
    {
        // Call AI-generated setup based on project type
        ProjectStructureSetup.CreateProjectFolders();
        
        if (includeNetworking)
        {
            // Install networking packages
            UnityEditor.PackageManager.Client.Add("com.unity.netcode.gameobjects");
        }
        
        if (includeMobileOptimizations)
        {
            // Configure mobile settings
            PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
        }
    }
}
```

---

## 📋 Project Setup Checklist

### Initial Setup (Day 1)
- [ ] Create project with appropriate template
- [ ] Set up folder structure
- [ ] Configure version control (Git + LFS)
- [ ] Install essential packages
- [ ] Configure player settings
- [ ] Create basic scenes (Main Menu, Gameplay, Game Over)
- [ ] Set up lighting and render pipeline

### Development Setup (Week 1)
- [ ] Implement GameManager and core systems
- [ ] Set up scene management
- [ ] Configure input system
- [ ] Implement save/load system
- [ ] Set up audio management
- [ ] Create UI framework
- [ ] Establish coding conventions

### Production Setup (Month 1)
- [ ] Set up build automation
- [ ] Configure analytics
- [ ] Implement crash reporting
- [ ] Set up testing framework
- [ ] Configure platform-specific settings
- [ ] Optimize for target devices
- [ ] Set up continuous integration

---

## 🎯 Interview Preparation

### Common Questions
1. **"How do you organize a Unity project?"**
   - Folder structure, naming conventions, asset organization
   - Version control setup and collaboration workflows

2. **"What's your process for setting up a new Unity project?"**
   - Template selection, essential packages, project settings
   - Team collaboration and development environment setup

3. **"How do you handle version control with Unity?"**
   - Git with LFS, .gitignore configuration, binary assets
   - Merge conflicts resolution, collaborative workflows

### Practical Challenges
- Set up a complete project structure in 10 minutes
- Configure Git LFS for a Unity project
- Create a custom project template
- Implement automated build pipeline

---

## 🚀 Next Steps
1. Practice creating projects with different templates
2. Set up your own project template for rapid prototyping
3. Move to **@03-Scene-Management.md** for scene workflows
4. Create a personal Unity project setup checklist

> **AI Integration Reminder**: Use AI to generate project templates, boilerplate code, and setup scripts. Focus on understanding project organization principles and collaboration workflows!