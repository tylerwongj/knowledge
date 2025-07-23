# @e-Asset-Management - Unity Asset Workflow & Optimization

## 🎯 Learning Objectives
- Master Unity's asset import pipeline and optimization
- Understand texture, model, audio, and animation asset workflows
- Learn asset organization, naming conventions, and version control
- Use AI to automate asset optimization and generate asset creation workflows

---

## 📁 Asset Organization & Structure

### Recommended Folder Structure
```
Assets/
├── 01_Scripts/
│   ├── Player/
│   ├── Enemies/
│   ├── UI/
│   └── Managers/
├── 02_Art/
│   ├── Textures/
│   ├── Materials/
│   ├── Models/
│   └── Sprites/
├── 03_Audio/
│   ├── Music/
│   ├── SFX/
│   └── Voice/
├── 04_Prefabs/
│   ├── Characters/
│   ├── Environment/
│   └── UI/
├── 05_Scenes/
├── 06_Animations/
├── 07_Resources/
└── 08_StreamingAssets/
```

### Asset Naming Conventions
```csharp
public static class AssetNamingConventions
{
    // Prefixes for different asset types
    public const string TEXTURE_PREFIX = "T_";
    public const string MATERIAL_PREFIX = "M_";
    public const string MODEL_PREFIX = "SM_"; // Static Mesh
    public const string PREFAB_PREFIX = "PF_";
    public const string ANIMATION_PREFIX = "A_";
    public const string AUDIO_PREFIX = "SFX_";
    
    // Examples:
    // T_PlayerDiffuse_1024
    // M_PlayerMaterial
    // SM_PlayerCharacter
    // PF_PlayerController
    // A_PlayerIdle
    // SFX_PlayerFootstep
}
```

---

## 🖼️ Texture & Material Management

### Texture Import Optimization
```csharp
using UnityEditor;
using UnityEngine;

public class TextureImportProcessor : AssetPostprocessor
{
    void OnPreprocessTexture()
    {
        TextureImporter importer = (TextureImporter)assetImporter;
        
        // Auto-setup based on texture name/path
        if (assetPath.Contains("UI"))
        {
            SetupUITexture(importer);
        }
        else if (assetPath.Contains("Diffuse") || assetPath.Contains("Albedo"))
        {
            SetupDiffuseTexture(importer);
        }
        else if (assetPath.Contains("Normal"))
        {
            SetupNormalTexture(importer);
        }
    }
    
    void SetupUITexture(TextureImporter importer)
    {
        importer.textureType = TextureImporterType.Sprite;
        importer.mipmapEnabled = false;
        importer.filterMode = FilterMode.Point; // For pixel art
        
        // Platform-specific settings
        TextureImporterPlatformSettings settings = new TextureImporterPlatformSettings();
        settings.name = "Standalone";
        settings.maxTextureSize = 1024;
        settings.format = TextureImporterFormat.RGBA32;
        importer.SetPlatformTextureSettings(settings);
    }
    
    void SetupDiffuseTexture(TextureImporter importer)
    {
        importer.textureType = TextureImporterType.Default;
        importer.mipmapEnabled = true;
        importer.sRGBTexture = true; // Color space
        
        // Compression settings
        TextureImporterPlatformSettings settings = new TextureImporterPlatformSettings();
        settings.name = "Standalone";
        settings.maxTextureSize = 2048;
        settings.format = TextureImporterFormat.DXT5; // Good quality/size balance
        importer.SetPlatformTextureSettings(settings);
    }
}
```

### Material System
```csharp
public class MaterialManager : MonoBehaviour
{
    [System.Serializable]
    public class MaterialSet
    {
        public string name;
        public Material[] materials;
    }
    
    [SerializeField] private MaterialSet[] materialSets;
    [SerializeField] private Renderer targetRenderer;
    
    public void SwitchMaterialSet(string setName)
    {
        MaterialSet set = System.Array.Find(materialSets, s => s.name == setName);
        if (set != null && targetRenderer != null)
        {
            targetRenderer.materials = set.materials;
        }
    }
    
    // Material property animation
    public void AnimateMaterialProperty(string propertyName, float targetValue, float duration)
    {
        StartCoroutine(AnimateProperty(propertyName, targetValue, duration));
    }
    
    IEnumerator AnimateProperty(string propertyName, float targetValue, float duration)
    {
        Material mat = targetRenderer.material;
        float startValue = mat.GetFloat(propertyName);
        float elapsedTime = 0f;
        
        while (elapsedTime < duration)
        {
            elapsedTime += Time.deltaTime;
            float currentValue = Mathf.Lerp(startValue, targetValue, elapsedTime / duration);
            mat.SetFloat(propertyName, currentValue);
            yield return null;
        }
        
        mat.SetFloat(propertyName, targetValue);
    }
}
```

---

## 🎵 Audio Asset Management

### Audio Import Settings
```csharp
public class AudioImportProcessor : AssetPostprocessor
{
    void OnPreprocessAudio()
    {
        AudioImporter importer = (AudioImporter)assetImporter;
        
        // Setup based on audio type
        if (assetPath.Contains("Music"))
        {
            SetupMusicAudio(importer);
        }
        else if (assetPath.Contains("SFX"))
        {
            SetupSFXAudio(importer);
        }
        else if (assetPath.Contains("Voice"))
        {
            SetupVoiceAudio(importer);
        }
    }
    
    void SetupMusicAudio(AudioImporter importer)
    {
        AudioImporterSampleSettings settings = new AudioImporterSampleSettings();
        settings.loadType = AudioClipLoadType.Streaming; // Don't load into memory
        settings.compressionFormat = AudioCompressionFormat.Vorbis;
        settings.quality = 0.7f; // Good quality/size balance
        
        importer.SetOverrideSampleSettings("Standalone", settings);
    }
    
    void SetupSFXAudio(AudioImporter importer)
    {
        AudioImporterSampleSettings settings = new AudioImporterSampleSettings();
        settings.loadType = AudioClipLoadType.DecompressOnLoad; // Fast access
        settings.compressionFormat = AudioCompressionFormat.PCM;
        
        importer.SetOverrideSampleSettings("Standalone", settings);
    }
}
```

### Dynamic Audio System
```csharp
public class AudioManager : MonoBehaviour
{
    [System.Serializable]
    public class AudioClipGroup
    {
        public string groupName;
        public AudioClip[] clips;
        [Range(0f, 1f)] public float volume = 1f;
        public bool randomizePitch = false;
        [Range(0.8f, 1.2f)] public float pitchVariance = 0.1f;
    }
    
    [SerializeField] private AudioClipGroup[] audioGroups;
    [SerializeField] private AudioSource[] audioSources; // Pool of audio sources
    
    private int currentSourceIndex = 0;
    
    public void PlayAudioGroup(string groupName)
    {
        AudioClipGroup group = System.Array.Find(audioGroups, g => g.groupName == groupName);
        if (group != null && group.clips.Length > 0)
        {
            AudioClip clipToPlay = group.clips[Random.Range(0, group.clips.Length)];
            AudioSource source = GetAvailableAudioSource();
            
            source.clip = clipToPlay;
            source.volume = group.volume;
            
            if (group.randomizePitch)
            {
                source.pitch = Random.Range(1f - group.pitchVariance, 1f + group.pitchVariance);
            }
            
            source.Play();
        }
    }
    
    AudioSource GetAvailableAudioSource()
    {
        // Round-robin through audio sources
        AudioSource source = audioSources[currentSourceIndex];
        currentSourceIndex = (currentSourceIndex + 1) % audioSources.Length;
        return source;
    }
}
```

---

## 🎨 Model & Animation Assets

### Model Import Pipeline
```csharp
public class ModelImportProcessor : AssetPostprocessor
{
    void OnPreprocessModel()
    {
        ModelImporter importer = (ModelImporter)assetImporter;
        
        // General settings
        importer.globalScale = 1f;
        importer.useFileScale = true;
        
        // Animation settings
        if (assetPath.Contains("@")) // Animation files (Character@Walk.fbx)
        {
            SetupAnimationImport(importer);
        }
        else // Static meshes
        {
            SetupStaticMeshImport(importer);
        }
    }
    
    void SetupAnimationImport(ModelImporter importer)
    {
        importer.importAnimation = true;
        importer.animationType = ModelImporterAnimationType.Human; // For humanoid rigs
        importer.optimizeGameObjects = true;
        
        // Animation compression
        importer.animationCompression = ModelImporterAnimationCompression.Optimal;
    }
    
    void SetupStaticMeshImport(ModelImporter importer)
    {
        importer.importAnimation = false;
        importer.importBlendShapes = false;
        importer.importCameras = false;
        importer.importLights = false;
        
        // Mesh optimization
        importer.meshOptimizationFlags = MeshOptimizationFlags.Everything;
        importer.weldVertices = true;
    }
}
```

---

## 🚀 AI/LLM Integration for Asset Management

### Asset Pipeline Automation
**Batch Processing Prompt:**
> "Generate a Unity editor script that automatically optimizes texture import settings based on file naming conventions and folder structure"

**Asset Validation:**
> "Create a Unity tool that validates asset naming conventions and suggests corrections for non-compliant files"

### Asset Creation Workflows
**Texture Generation:**
> "Generate a workflow for creating PBR materials in Unity, including diffuse, normal, metallic, and roughness maps"

**Audio Implementation:**
> "Create a Unity audio system that supports dynamic music layers and adaptive audio based on gameplay state"

### Code Generation Examples
```csharp
// AI-generated asset validator
public class AssetValidator : EditorWindow
{
    [MenuItem("Tools/Asset Validator")]
    public static void ShowWindow()
    {
        GetWindow<AssetValidator>("Asset Validator");
    }
    
    void OnGUI()
    {
        GUILayout.Label("Asset Validation", EditorStyles.boldLabel);
        
        if (GUILayout.Button("Validate Naming Conventions"))
        {
            ValidateAssetNames();
        }
        
        if (GUILayout.Button("Check Missing References"))
        {
            CheckMissingReferences();
        }
        
        if (GUILayout.Button("Optimize Import Settings"))
        {
            OptimizeImportSettings();
        }
    }
    
    void ValidateAssetNames()
    {
        string[] guids = AssetDatabase.FindAssets("", new[] { "Assets" });
        
        foreach (string guid in guids)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            string filename = Path.GetFileNameWithoutExtension(path);
            
            // Check naming conventions
            if (path.Contains("Textures") && !filename.StartsWith("T_"))
            {
                Debug.LogWarning($"Texture naming issue: {path}");
            }
            else if (path.Contains("Materials") && !filename.StartsWith("M_"))
            {
                Debug.LogWarning($"Material naming issue: {path}");
            }
        }
    }
}
```

---

## 📦 Asset Bundling & Resources

### Asset Bundle System
```csharp
public class AssetBundleManager : MonoBehaviour
{
    private Dictionary<string, AssetBundle> loadedBundles = new Dictionary<string, AssetBundle>();
    
    public async Task<T> LoadAssetAsync<T>(string bundleName, string assetName) where T : Object
    {
        AssetBundle bundle = await LoadBundleAsync(bundleName);
        if (bundle != null)
        {
            AssetBundleRequest request = bundle.LoadAssetAsync<T>(assetName);
            await Task.Yield(); // Yield control
            
            while (!request.isDone)
            {
                await Task.Yield();
            }
            
            return request.asset as T;
        }
        return null;
    }
    
    async Task<AssetBundle> LoadBundleAsync(string bundleName)
    {
        if (loadedBundles.ContainsKey(bundleName))
        {
            return loadedBundles[bundleName];
        }
        
        string bundlePath = Path.Combine(Application.streamingAssetsPath, bundleName);
        AssetBundleCreateRequest request = AssetBundle.LoadFromFileAsync(bundlePath);
        
        while (!request.isDone)
        {
            await Task.Yield();
        }
        
        if (request.assetBundle != null)
        {
            loadedBundles[bundleName] = request.assetBundle;
            return request.assetBundle;
        }
        
        return null;
    }
    
    public void UnloadBundle(string bundleName, bool unloadAllLoadedObjects = false)
    {
        if (loadedBundles.ContainsKey(bundleName))
        {
            loadedBundles[bundleName].Unload(unloadAllLoadedObjects);
            loadedBundles.Remove(bundleName);
        }
    }
}
```

### Addressable Assets (Modern Alternative)
```csharp
using UnityEngine.AddressableAssets;

public class AddressableManager : MonoBehaviour
{
    public async Task<GameObject> LoadPrefabAsync(string address)
    {
        var handle = Addressables.LoadAssetAsync<GameObject>(address);
        GameObject prefab = await handle.Task;
        
        if (prefab != null)
        {
            return Instantiate(prefab);
        }
        
        return null;
    }
    
    public async Task PreloadAssetsAsync(string[] addresses)
    {
        var tasks = new List<Task>();
        
        foreach (string address in addresses)
        {
            tasks.Add(Addressables.LoadAssetAsync<Object>(address).Task);
        }
        
        await Task.WhenAll(tasks);
        Debug.Log("All assets preloaded!");
    }
    
    void OnDestroy()
    {
        // Clean up addressable handles
        Addressables.ReleaseInstance(gameObject);
    }
}
```

---

## 🎯 Practical Exercises

### Exercise 1: Asset Pipeline Setup
Create an asset import system:
- Automatic texture optimization based on usage
- Model import settings for characters vs. environment
- Audio compression based on file type
- Validation tools for naming conventions

### Exercise 2: Dynamic Asset Loading
Build a system for:
- Loading assets based on player progression
- Streaming large environments
- Memory management for loaded assets
- Fallback loading for missing assets

### Exercise 3: Asset Bundle Workflow
Implement:
- Asset bundle creation pipeline
- Runtime loading/unloading system
- Version control for asset bundles
- Platform-specific asset optimization

---

## 🎯 Portfolio Project Ideas

### Beginner: "Asset Pipeline Demo"
- Show before/after optimization results
- Demonstrate different compression settings
- Include performance comparisons
- Document file size savings

### Intermediate: "Dynamic Content System"
- Asset streaming based on player location
- Modular character customization
- Dynamic texture swapping
- Performance monitoring tools

### Advanced: "Complete Asset Management Framework"
- Custom import pipeline
- Asset dependency tracking
- Automated optimization tools
- Cross-platform asset delivery

---

## 🔍 Interview Preparation

### Common Questions
1. **"How do you optimize texture memory usage?"**
   - Use appropriate compression formats
   - Implement texture streaming
   - Reduce texture resolution where possible
   - Use texture atlasing to reduce draw calls

2. **"What's the difference between Resources and Asset Bundles?"**
   - Resources: Built into app, can't be updated
   - Asset Bundles: External files, updateable, platform-specific

3. **"How do you handle missing asset references?"**
   - Implement fallback assets
   - Use validation tools during build
   - Create asset reference management system

### Technical Challenges
- Design an asset streaming system
- Optimize a project's memory usage
- Create automated asset validation tools
- Implement cross-platform asset delivery

---

## ⚡ AI Productivity Hacks

### Asset Optimization
- Generate compression setting recommendations
- Create automated optimization scripts
- Design asset naming convention systems
- Build performance analysis tools

### Pipeline Automation
- Generate import processor scripts
- Create asset validation workflows
- Design batch processing tools
- Build dependency tracking systems

### Learning Acceleration
- Generate asset optimization checklists
- Create performance testing scenarios
- Build troubleshooting guides
- Design best practice documentation

---

## 🎯 Next Steps
1. Implement organized asset structure in a project
2. Create automated import settings for different asset types
3. Move to **@f-Performance-Optimization.md** for runtime optimization
4. Build an asset management showcase for portfolio

> **AI Integration Reminder**: Use LLMs to automate asset pipeline setup, generate optimization scripts, and create validation tools. Proper asset management is crucial for professional Unity development - AI can help you build robust, scalable systems quickly!