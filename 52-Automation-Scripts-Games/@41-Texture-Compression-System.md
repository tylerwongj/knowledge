# @41-Texture-Compression-System

## 🎯 Core Concept
Automated texture compression and optimization system for reducing memory usage and improving loading times.

## 🔧 Implementation

### Texture Compression Manager
```csharp
using UnityEngine;
using UnityEditor;
using System.Collections.Generic;
using System.IO;

public class TextureCompressionManager
{
    [Header("Compression Settings")]
    public static bool enableAutoCompression = true;
    public static int maxTextureSize = 2048;
    public static bool generateMipmaps = true;
    public static bool useStreamingMipmaps = true;
    
    [MenuItem("Tools/Texture Compression/Compress All Textures")]
    public static void CompressAllTextures()
    {
        string[] textureGUIDs = AssetDatabase.FindAssets("t:Texture2D");
        int processed = 0;
        
        foreach (string guid in textureGUIDs)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
            
            if (importer != null)
            {
                bool changed = OptimizeTextureImporter(importer, path);
                if (changed)
                {
                    AssetDatabase.ImportAsset(path);
                    processed++;
                }
            }
        }
        
        AssetDatabase.Refresh();
        Debug.Log($"Processed {processed} textures for compression optimization");
    }
    
    public static bool OptimizeTextureImporter(TextureImporter importer, string assetPath)
    {
        bool changed = false;
        Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(assetPath);
        
        if (texture == null) return false;
        
        // Determine optimal settings based on texture type
        TextureCompressionSettings settings = GetOptimalSettings(texture, assetPath);
        
        // Apply general settings
        if (importer.maxTextureSize != settings.maxSize)
        {
            importer.maxTextureSize = settings.maxSize;
            changed = true;
        }
        
        if (importer.mipmapEnabled != settings.generateMipmaps)
        {
            importer.mipmapEnabled = settings.generateMipmaps;
            changed = true;
        }
        
        if (importer.streamingMipmaps != settings.streamingMipmaps)
        {
            importer.streamingMipmaps = settings.streamingMipmaps;
            changed = true;
        }
        
        // Apply platform-specific settings
        changed |= ApplyPlatformSettings(importer, BuildTarget.StandaloneWindows64, settings);
        changed |= ApplyPlatformSettings(importer, BuildTarget.Android, settings);
        changed |= ApplyPlatformSettings(importer, BuildTarget.iOS, settings);
        
        return changed;
    }
    
    static TextureCompressionSettings GetOptimalSettings(Texture2D texture, string assetPath)
    {
        TextureCompressionSettings settings = new TextureCompressionSettings();
        
        // Determine texture category
        TextureCategory category = CategorizeTexture(assetPath, texture);
        
        switch (category)
        {
            case TextureCategory.UI:
                settings.maxSize = 1024;
                settings.generateMipmaps = false;
                settings.streamingMipmaps = false;
                settings.defaultFormat = TextureImporterFormat.RGBA32;
                settings.androidFormat = TextureImporterFormat.ETC2_RGBA8;
                settings.iosFormat = TextureImporterFormat.PVRTC_RGBA4;
                break;
                
            case TextureCategory.Character:
                settings.maxSize = 2048;
                settings.generateMipmaps = true;
                settings.streamingMipmaps = true;
                settings.defaultFormat = TextureImporterFormat.DXT5;
                settings.androidFormat = TextureImporterFormat.ETC2_RGBA8;
                settings.iosFormat = TextureImporterFormat.PVRTC_RGBA4;
                break;
                
            case TextureCategory.Environment:
                settings.maxSize = 1024;
                settings.generateMipmaps = true;
                settings.streamingMipmaps = true;
                settings.defaultFormat = TextureImporterFormat.DXT1;
                settings.androidFormat = TextureImporterFormat.ETC_RGB4;
                settings.iosFormat = TextureImporterFormat.PVRTC_RGB4;
                break;
                
            case TextureCategory.Normal:
                settings.maxSize = 1024;
                settings.generateMipmaps = true;
                settings.streamingMipmaps = true;
                settings.defaultFormat = TextureImporterFormat.DXT5;
                settings.androidFormat = TextureImporterFormat.ETC2_RGBA8;
                settings.iosFormat = TextureImporterFormat.PVRTC_RGBA4;
                break;
                
            case TextureCategory.Icon:
                settings.maxSize = 256;
                settings.generateMipmaps = false;
                settings.streamingMipmaps = false;
                settings.defaultFormat = TextureImporterFormat.RGBA32;
                settings.androidFormat = TextureImporterFormat.ETC2_RGBA8;
                settings.iosFormat = TextureImporterFormat.PVRTC_RGBA4;
                break;
                
            default:
                // Generic settings
                settings.maxSize = 1024;
                settings.generateMipmaps = true;
                settings.streamingMipmaps = false;
                settings.defaultFormat = TextureImporterFormat.DXT1;
                settings.androidFormat = TextureImporterFormat.ETC_RGB4;
                settings.iosFormat = TextureImporterFormat.PVRTC_RGB4;
                break;
        }
        
        // Adjust based on texture size
        AdjustSettingsForSize(settings, texture);
        
        return settings;
    }
    
    static TextureCategory CategorizeTexture(string assetPath, Texture2D texture)
    {
        string pathLower = assetPath.ToLower();
        string fileName = Path.GetFileNameWithoutExtension(pathLower);
        
        // UI textures
        if (pathLower.Contains("/ui/") || pathLower.Contains("/gui/") || 
            fileName.Contains("ui_") || fileName.Contains("button"))
        {
            return TextureCategory.UI;
        }
        
        // Character textures
        if (pathLower.Contains("/character/") || pathLower.Contains("/player/") || 
            fileName.Contains("char_") || fileName.Contains("skin"))
        {
            return TextureCategory.Character;
        }
        
        // Environment textures
        if (pathLower.Contains("/environment/") || pathLower.Contains("/terrain/") || 
            fileName.Contains("env_") || fileName.Contains("ground"))
        {
            return TextureCategory.Environment;
        }
        
        // Normal maps
        if (fileName.Contains("normal") || fileName.Contains("_n") || fileName.EndsWith("_normal"))
        {
            return TextureCategory.Normal;
        }
        
        // Icons
        if (pathLower.Contains("/icons/") || fileName.Contains("icon_") || texture.width <= 128)
        {
            return TextureCategory.Icon;
        }
        
        return TextureCategory.Generic;
    }
    
    static void AdjustSettingsForSize(TextureCompressionSettings settings, Texture2D texture)
    {
        int size = Mathf.Max(texture.width, texture.height);
        
        // Very large textures - more aggressive compression
        if (size > 2048)
        {
            settings.maxSize = 2048;
            settings.compressionQuality = 50;
        }
        // Large textures
        else if (size > 1024)
        {
            settings.maxSize = 1024;
            settings.compressionQuality = 75;
        }
        // Medium textures
        else if (size > 512)
        {
            settings.maxSize = 512;
            settings.compressionQuality = 85;
        }
        // Small textures - preserve quality
        else
        {
            settings.maxSize = size;
            settings.compressionQuality = 100;
        }
    }
    
    static bool ApplyPlatformSettings(TextureImporter importer, BuildTarget platform, 
                                    TextureCompressionSettings settings)
    {
        string platformName = GetPlatformName(platform);
        TextureImporterPlatformSettings platformSettings = importer.GetPlatformTextureSettings(platformName);
        
        bool changed = false;
        
        // Override settings for platform
        if (!platformSettings.overridden)
        {
            platformSettings.overridden = true;
            changed = true;
        }
        
        if (platformSettings.maxTextureSize != settings.maxSize)
        {
            platformSettings.maxTextureSize = settings.maxSize;
            changed = true;
        }
        
        TextureImporterFormat targetFormat = GetPlatformFormat(platform, settings);
        if (platformSettings.format != targetFormat)
        {
            platformSettings.format = targetFormat;
            changed = true;
        }
        
        if (platformSettings.compressionQuality != settings.compressionQuality)
        {
            platformSettings.compressionQuality = settings.compressionQuality;
            changed = true;
        }
        
        if (changed)
        {
            importer.SetPlatformTextureSettings(platformSettings);
        }
        
        return changed;
    }
    
    static TextureImporterFormat GetPlatformFormat(BuildTarget platform, TextureCompressionSettings settings)
    {
        switch (platform)
        {
            case BuildTarget.Android:
                return settings.androidFormat;
            case BuildTarget.iOS:
                return settings.iosFormat;
            default:
                return settings.defaultFormat;
        }
    }
    
    static string GetPlatformName(BuildTarget platform)
    {
        switch (platform)
        {
            case BuildTarget.StandaloneWindows64:
            case BuildTarget.StandaloneWindows:
                return "Standalone";
            case BuildTarget.Android:
                return "Android";
            case BuildTarget.iOS:
                return "iPhone";
            default:
                return "Default";
        }
    }
    
    [MenuItem("Tools/Texture Compression/Analyze Texture Memory")]
    public static void AnalyzeTextureMemory()
    {
        Dictionary<string, long> categoryMemory = new Dictionary<string, long>();
        Dictionary<string, int> categoryCount = new Dictionary<string, int>();
        
        string[] textureGUIDs = AssetDatabase.FindAssets("t:Texture2D");
        long totalMemory = 0;
        
        foreach (string guid in textureGUIDs)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            
            if (texture != null)
            {
                TextureCategory category = CategorizeTexture(path, texture);
                string categoryName = category.ToString();
                
                long textureMemory = CalculateTextureMemory(texture);
                totalMemory += textureMemory;
                
                if (!categoryMemory.ContainsKey(categoryName))
                {
                    categoryMemory[categoryName] = 0;
                    categoryCount[categoryName] = 0;
                }
                
                categoryMemory[categoryName] += textureMemory;
                categoryCount[categoryName]++;
            }
        }
        
        Debug.Log("=== Texture Memory Analysis ===");
        Debug.Log($"Total Texture Memory: {totalMemory / (1024 * 1024):F1} MB");
        Debug.Log("");
        
        foreach (var category in categoryMemory)
        {
            float memoryMB = category.Value / (1024f * 1024f);
            float percentage = (category.Value / (float)totalMemory) * 100f;
            int count = categoryCount[category.Key];
            
            Debug.Log($"{category.Key}: {memoryMB:F1} MB ({percentage:F1}%) - {count} textures");
        }
    }
    
    static long CalculateTextureMemory(Texture2D texture)
    {
        // Estimate memory usage based on format and size
        int width = texture.width;
        int height = texture.height;
        long pixelCount = width * height;
        
        TextureFormat format = texture.format;
        int bytesPerPixel = GetBytesPerPixel(format);
        
        long memory = pixelCount * bytesPerPixel;
        
        // Add mipmap memory if enabled
        if (texture.mipmapCount > 1)
        {
            memory = (long)(memory * 1.33f); // Approximate mipmap overhead
        }
        
        return memory;
    }
    
    static int GetBytesPerPixel(TextureFormat format)
    {
        switch (format)
        {
            case TextureFormat.RGBA32:
            case TextureFormat.ARGB32:
                return 4;
            case TextureFormat.RGB24:
                return 3;
            case TextureFormat.RGBA4444:
            case TextureFormat.RGB565:
                return 2;
            case TextureFormat.DXT1:
                return 1; // Compressed
            case TextureFormat.DXT5:
                return 1; // Compressed
            case TextureFormat.ETC_RGB4:
            case TextureFormat.ETC2_RGBA8:
                return 1; // Compressed
            case TextureFormat.PVRTC_RGB4:
            case TextureFormat.PVRTC_RGBA4:
                return 1; // Compressed
            default:
                return 4; // Conservative estimate
        }
    }
    
    [MenuItem("Tools/Texture Compression/Generate Compression Report")]
    public static void GenerateCompressionReport()
    {
        List<TextureCompressionInfo> compressionInfo = new List<TextureCompressionInfo>();
        string[] textureGUIDs = AssetDatabase.FindAssets("t:Texture2D");
        
        foreach (string guid in textureGUIDs)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
            
            if (texture != null && importer != null)
            {
                TextureCompressionInfo info = new TextureCompressionInfo
                {
                    path = path,
                    originalSize = new Vector2Int(texture.width, texture.height),
                    importSize = new Vector2Int(importer.maxTextureSize, importer.maxTextureSize),
                    format = texture.format.ToString(),
                    memorySize = CalculateTextureMemory(texture),
                    hasMipmaps = texture.mipmapCount > 1,
                    category = CategorizeTexture(path, texture).ToString()
                };
                
                compressionInfo.Add(info);
            }
        }
        
        // Export to CSV
        string csvContent = "Path,Original Width,Original Height,Import Size,Format,Memory (MB),Has Mipmaps,Category\n";
        
        foreach (var info in compressionInfo)
        {
            csvContent += $"{info.path},{info.originalSize.x},{info.originalSize.y}," +
                         $"{info.importSize.x},{info.format},{info.memorySize / (1024f * 1024f):F2}," +
                         $"{info.hasMipmaps},{info.category}\n";
        }
        
        File.WriteAllText("texture_compression_report.csv", csvContent);
        Debug.Log("Texture compression report generated: texture_compression_report.csv");
    }
}

public enum TextureCategory
{
    UI,
    Character,
    Environment,
    Normal,
    Icon,
    Generic
}

[System.Serializable]
public class TextureCompressionSettings
{
    public int maxSize = 1024;
    public bool generateMipmaps = true;
    public bool streamingMipmaps = false;
    public int compressionQuality = 50;
    public TextureImporterFormat defaultFormat = TextureImporterFormat.DXT1;
    public TextureImporterFormat androidFormat = TextureImporterFormat.ETC_RGB4;
    public TextureImporterFormat iosFormat = TextureImporterFormat.PVRTC_RGB4;
}

[System.Serializable]
public class TextureCompressionInfo
{
    public string path;
    public Vector2Int originalSize;
    public Vector2Int importSize;
    public string format;
    public long memorySize;
    public bool hasMipmaps;
    public string category;
}

// Runtime texture optimization
public class RuntimeTextureOptimizer : MonoBehaviour
{
    [Header("Runtime Settings")]
    public bool optimizeOnStart = true;
    public bool unloadUnusedTextures = true;
    public float optimizationInterval = 30f;
    
    void Start()
    {
        if (optimizeOnStart)
        {
            OptimizeTextures();
        }
        
        if (unloadUnusedTextures)
        {
            InvokeRepeating(nameof(UnloadUnusedTextures), optimizationInterval, optimizationInterval);
        }
    }
    
    void OptimizeTextures()
    {
        // Reduce texture quality on low-end devices
        if (SystemInfo.systemMemorySize < 4000) // Less than 4GB RAM
        {
            QualitySettings.masterTextureLimit = 1; // Half resolution
            Debug.Log("Texture quality reduced for low-end device");
        }
        else if (SystemInfo.systemMemorySize < 8000) // Less than 8GB RAM
        {
            QualitySettings.masterTextureLimit = 0; // Full resolution
        }
    }
    
    void UnloadUnusedTextures()
    {
        Resources.UnloadUnusedAssets();
        System.GC.Collect();
    }
}
```

## 🚀 AI/LLM Integration
- Automatically categorize textures based on usage patterns
- Generate optimal compression settings for different use cases
- Create texture optimization recommendations

## 💡 Key Benefits
- Automated texture compression
- Memory usage optimization
- Platform-specific texture formats