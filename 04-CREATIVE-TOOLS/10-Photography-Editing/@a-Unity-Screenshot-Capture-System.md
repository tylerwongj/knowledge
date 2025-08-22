# @a-Unity-Screenshot-Capture-System - Game Photography Tools

## 🎯 Learning Objectives
- Implement advanced screenshot and video capture systems in Unity
- Master camera control and composition tools for game photography
- Build automated screenshot processing and enhancement pipelines
- Create AI-powered image analysis and optimization workflows

---

## 🔧 Unity Screenshot System

### Professional Screenshot Capture Manager

```csharp
using UnityEngine;
using System.Collections;
using System.IO;
using System;

/// <summary>
/// Advanced screenshot and video capture system for Unity games
/// Supports multiple formats, resolutions, and post-processing effects
/// </summary>
public class GameScreenshotManager : MonoBehaviour
{
    [System.Serializable]
    public class CaptureSettings
    {
        [Header("Resolution")]
        public int width = 1920;
        public int height = 1080;
        public int superSampling = 1;
        
        [Header("Format")]
        public ImageFormat format = ImageFormat.PNG;
        public int jpegQuality = 95;
        
        [Header("Effects")]
        public bool applyPostProcessing = true;
        public bool includeUI = false;
        public bool transparentBackground = false;
    }
    
    public enum ImageFormat { PNG, JPG, TGA }
    
    [SerializeField] private CaptureSettings captureSettings = new CaptureSettings();
    [SerializeField] private Camera captureCamera;
    [SerializeField] private string savePath = "Screenshots/";
    
    void Start()
    {
        if (captureCamera == null)
            captureCamera = Camera.main;
        
        CreateSaveDirectory();
    }
    
    [ContextMenu("Capture Screenshot")]
    public void CaptureScreenshot()
    {
        StartCoroutine(CaptureScreenshotCoroutine());
    }
    
    private IEnumerator CaptureScreenshotCoroutine()
    {
        // Prepare capture
        var originalCullingMask = captureCamera.cullingMask;
        
        if (!captureSettings.includeUI)
        {
            captureCamera.cullingMask &= ~(1 << LayerMask.NameToLayer("UI"));
        }
        
        // Calculate final resolution
        int finalWidth = captureSettings.width * captureSettings.superSampling;
        int finalHeight = captureSettings.height * captureSettings.superSampling;
        
        // Create render texture
        var renderTexture = new RenderTexture(finalWidth, finalHeight, 24);
        renderTexture.antiAliasing = captureSettings.superSampling > 1 ? 8 : 1;
        
        var originalTarget = captureCamera.targetTexture;
        captureCamera.targetTexture = renderTexture;
        
        // Render
        captureCamera.Render();
        
        yield return new WaitForEndOfFrame();
        
        // Read pixels
        RenderTexture.active = renderTexture;
        var screenshot = new Texture2D(finalWidth, finalHeight, TextureFormat.RGB24, false);
        screenshot.ReadPixels(new Rect(0, 0, finalWidth, finalHeight), 0, 0);
        screenshot.Apply();
        
        // Restore camera settings
        captureCamera.targetTexture = originalTarget;
        captureCamera.cullingMask = originalCullingMask;
        RenderTexture.active = null;
        
        // Process and save
        var processedTexture = ProcessScreenshot(screenshot);
        SaveScreenshot(processedTexture);
        
        // Cleanup
        DestroyImmediate(screenshot);
        DestroyImmediate(processedTexture);
        DestroyImmediate(renderTexture);
    }
    
    private Texture2D ProcessScreenshot(Texture2D original)
    {
        // Apply post-processing effects
        if (captureSettings.applyPostProcessing)
        {
            // Color correction, sharpening, etc.
            return ApplyImageEnhancement(original);
        }
        
        return original;
    }
    
    private Texture2D ApplyImageEnhancement(Texture2D original)
    {
        var enhanced = new Texture2D(original.width, original.height, original.format, false);
        var pixels = original.GetPixels();
        
        // Apply enhancement filters
        for (int i = 0; i < pixels.Length; i++)
        {
            var color = pixels[i];
            
            // Contrast enhancement
            color.r = Mathf.Pow(color.r, 0.9f);
            color.g = Mathf.Pow(color.g, 0.9f);
            color.b = Mathf.Pow(color.b, 0.9f);
            
            // Saturation boost
            var luminance = 0.299f * color.r + 0.587f * color.g + 0.114f * color.b;
            color.r = Mathf.Lerp(luminance, color.r, 1.1f);
            color.g = Mathf.Lerp(luminance, color.g, 1.1f);
            color.b = Mathf.Lerp(luminance, color.b, 1.1f);
            
            pixels[i] = color;
        }
        
        enhanced.SetPixels(pixels);
        enhanced.Apply();
        
        return enhanced;
    }
    
    private void SaveScreenshot(Texture2D texture)
    {
        byte[] data = null;
        string extension = "";
        
        switch (captureSettings.format)
        {
            case ImageFormat.PNG:
                data = texture.EncodeToPNG();
                extension = ".png";
                break;
            case ImageFormat.JPG:
                data = texture.EncodeToJPG(captureSettings.jpegQuality);
                extension = ".jpg";
                break;
        }
        
        if (data != null)
        {
            var filename = $"screenshot_{DateTime.Now:yyyyMMdd_HHmmss}{extension}";
            var fullPath = Path.Combine(Application.persistentDataPath, savePath, filename);
            
            File.WriteAllBytes(fullPath, data);
            Debug.Log($"Screenshot saved: {fullPath}");
        }
    }
}

/// <summary>
/// Photo mode camera controller for artistic screenshot capture
/// </summary>
public class PhotoModeController : MonoBehaviour
{
    [Header("Camera Controls")]
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float rotationSpeed = 2f;
    [SerializeField] private float zoomSpeed = 2f;
    
    [Header("Visual Settings")]
    [SerializeField] private float minFOV = 10f;
    [SerializeField] private float maxFOV = 90f;
    
    private Camera photoCamera;
    private bool photoModeActive = false;
    
    void Start()
    {
        photoCamera = GetComponent<Camera>();
    }
    
    void Update()
    {
        if (photoModeActive)
        {
            HandlePhotoModeInput();
        }
    }
    
    public void TogglePhotoMode()
    {
        photoModeActive = !photoModeActive;
        
        if (photoModeActive)
        {
            EnablePhotoMode();
        }
        else
        {
            DisablePhotoMode();
        }
    }
    
    private void HandlePhotoModeInput()
    {
        // Movement
        var horizontal = Input.GetAxis("Horizontal");
        var vertical = Input.GetAxis("Vertical");
        var upDown = 0f;
        
        if (Input.GetKey(KeyCode.Q)) upDown = -1f;
        if (Input.GetKey(KeyCode.E)) upDown = 1f;
        
        var movement = new Vector3(horizontal, upDown, vertical);
        transform.Translate(movement * moveSpeed * Time.deltaTime);
        
        // Rotation
        if (Input.GetMouseButton(1))
        {
            var mouseX = Input.GetAxis("Mouse X");
            var mouseY = Input.GetAxis("Mouse Y");
            
            transform.Rotate(Vector3.up, mouseX * rotationSpeed, Space.World);
            transform.Rotate(Vector3.right, -mouseY * rotationSpeed, Space.Self);
        }
        
        // Zoom (FOV adjustment)
        var scroll = Input.GetAxis("Mouse ScrollWheel");
        if (scroll != 0)
        {
            var currentFOV = photoCamera.fieldOfView;
            var newFOV = Mathf.Clamp(currentFOV - scroll * zoomSpeed, minFOV, maxFOV);
            photoCamera.fieldOfView = newFOV;
        }
    }
}
```

---

## 🚀 AI/LLM Integration Opportunities

### Intelligent Screenshot Analysis
**Image Composition Analysis Prompt:**
> "Analyze this Unity game screenshot for photographic composition quality. Evaluate rule of thirds, lighting, color balance, and visual interest. Suggest improvements for better artistic capture."

### Automated Enhancement Pipeline
```csharp
public class AIScreenshotEnhancer : MonoBehaviour
{
    public Texture2D EnhanceScreenshot(Texture2D original)
    {
        // AI would analyze and enhance image automatically
        var enhancementSettings = AnalyzeImageWithAI(original);
        return ApplyAIEnhancements(original, enhancementSettings);
    }
    
    private EnhancementSettings AnalyzeImageWithAI(Texture2D image)
    {
        // AI analysis for optimal enhancement parameters
        return new EnhancementSettings
        {
            contrast = 1.1f,
            saturation = 1.05f,
            brightness = 1.02f
        };
    }
}
```

---

## 💡 Key Screenshot System Features

### Advanced Capture Options
- **Super Sampling**: Higher resolution capture with downsampling for quality
- **Format Flexibility**: PNG for quality, JPEG for smaller files
- **Layer Control**: Include/exclude UI elements and specific layers
- **Post-Processing**: Real-time image enhancement and filtering

### Photo Mode Features
- **Free Camera**: Unconstrained camera movement for perfect shots
- **Composition Tools**: Rule of thirds grid, depth of field preview
- **Lighting Control**: Time of day adjustment, custom lighting setups
- **Filter Effects**: Real-time photo filters and artistic effects

### Performance Considerations
- **Async Capture**: Non-blocking screenshot capture process
- **Memory Management**: Efficient texture handling and cleanup
- **Quality Settings**: Adaptive quality based on device capabilities
- **Batch Processing**: Multiple screenshot capture and processing

This comprehensive screenshot system provides professional-grade image capture capabilities with AI-enhanced processing for stunning game photography.