# @b-Advanced-Color-Correction-Grading - Professional Photo Color Enhancement and Creative Grading

## 🎯 Learning Objectives
- Master advanced color correction and creative grading techniques for professional photography
- Understand color theory, color spaces, and technical color workflows
- Implement AI-enhanced color processing for consistent and efficient editing
- Build automated color correction systems for batch processing and Unity texture optimization

## 🔧 Color Theory and Technical Foundations

### Color Space Management
```yaml
Essential Color Spaces:
  sRGB: Standard web and monitor display (8-bit, limited gamut)
    - Gamma: 2.2 curve for display optimization
    - Primary Colors: Red (0.64, 0.33), Green (0.30, 0.60), Blue (0.15, 0.06)
    - White Point: D65 illuminant (6500K daylight)
    - Use Cases: Web display, social media, standard monitors
  
  Adobe RGB: Extended color space for print and professional work
    - Gamma: 2.2 curve with extended color gamut
    - Coverage: ~50% more colors than sRGB, better cyan/green reproduction
    - Primary Colors: Wider gamut covering more printable colors
    - Use Cases: Print preparation, professional photography, fine art
  
  ProPhoto RGB: Maximum color space for capture and archival
    - Gamma: 1.8 curve with massive color gamut
    - Coverage: Encompasses most camera sensor capabilities
    - Bit Depth: Requires 16-bit to prevent banding
    - Use Cases: RAW processing, archival storage, extreme color work
  
  Rec. 709: Broadcast television standard
    - Gamma: 2.4 curve for television display
    - Matches sRGB primaries but different gamma curve
    - Use Cases: Video content, broadcast, streaming media
  
  DCI-P3: Digital cinema and modern display standard
    - Gamma: 2.6 curve optimized for cinema projection
    - Extended red and green primaries over sRGB
    - Use Cases: Digital cinema, modern monitors, HDR content

Color Management Workflow:
  1. Capture: Shoot in camera's native color space (RAW recommended)
  2. Processing: Work in wide gamut space (ProPhoto RGB or Adobe RGB)
  3. Editing: Maintain wide gamut throughout adjustment process
  4. Output: Convert to appropriate space for final use (sRGB, Adobe RGB, etc.)
  5. Proofing: Soft-proof final output for target display/print conditions
```

### Advanced Color Correction Techniques
```yaml
Technical Color Correction Workflow:
  White Balance Correction:
    - Temperature Adjustment: 2000K-10000K range for warm/cool balance
    - Tint Adjustment: Magenta-Green axis compensation for color casts
    - Custom White Balance: Use gray card or known neutral reference
    - Split White Balance: Different WB for highlights and shadows
  
  Exposure and Tonal Adjustment:
    - Exposure: Overall brightness, affects entire image uniformly
    - Highlights: Recover blown highlights (-100 to +100 range)
    - Shadows: Lift blocked shadows (-100 to +100 range)
    - Whites: Set pure white point (0 to +100 range)
    - Blacks: Set pure black point (-100 to 0 range)
    - Contrast: Midtone separation (0.8 to 1.2 multiplier)
  
  Advanced Tonal Control:
    - Luminosity Masks: Target specific tonal ranges precisely
    - Curves Adjustment: Precise control over tonal relationships
    - Split Curves: Separate RGB curves for color and contrast control
    - Parametric Curves: Highlight/Light/Dark/Shadow region control
    - Point Curves: Manual curve shaping for creative looks

Color Correction Hierarchy:
  1. Global Corrections: Overall image balance and exposure
  2. Tonal Corrections: Contrast, brightness, and tonal relationships
  3. Color Corrections: Hue, saturation, and color balance adjustments
  4. Local Corrections: Selective area adjustments and refinements
  5. Creative Grading: Artistic color enhancement and mood creation
```

### AI-Enhanced Color Processing
```python
# AI-powered color correction and analysis system
import cv2
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from scipy import stats

class AIColorProcessor:
    def __init__(self):
        self.color_harmony_rules = {
            'complementary': 180,
            'triadic': 120,
            'analogous': 30,
            'split_complementary': 150,
            'tetradic': 90
        }
        self.reference_database = {}
    
    def analyze_image_color_profile(self, image_path):
        """
        Comprehensive AI analysis of image color characteristics
        """
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        analysis = {
            'dominant_colors': self.extract_dominant_colors(image_rgb),
            'color_temperature': self.estimate_color_temperature(image_rgb),
            'color_cast_detection': self.detect_color_cast(image_rgb),
            'saturation_analysis': self.analyze_saturation_distribution(image_rgb),
            'contrast_analysis': self.analyze_contrast_levels(image_rgb),
            'histogram_analysis': self.analyze_histogram_balance(image_rgb),
            'suggested_corrections': []
        }
        
        # Generate AI-powered correction suggestions
        analysis['suggested_corrections'] = self.generate_correction_suggestions(analysis)
        
        return analysis
    
    def extract_dominant_colors(self, image, n_colors=5):
        """Extract dominant colors using K-means clustering"""
        # Reshape image to be a list of pixels
        pixels = image.reshape((-1, 3))
        
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # Get colors and their percentages
        colors = kmeans.cluster_centers_.astype(int)
        labels = kmeans.labels_
        
        # Calculate color percentages
        percentages = []
        for i in range(n_colors):
            percentage = np.sum(labels == i) / len(labels) * 100
            percentages.append(percentage)
        
        # Sort by percentage
        color_data = list(zip(colors, percentages))
        color_data.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'colors': [color.tolist() for color, _ in color_data],
            'percentages': [percentage for _, percentage in color_data],
            'color_harmony': self.analyze_color_harmony([color for color, _ in color_data])
        }
    
    def estimate_color_temperature(self, image):
        """Estimate color temperature from image statistics"""
        # Convert to LAB color space for better analysis
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        
        # Analyze A and B channels (green-red and blue-yellow axes)
        a_channel = lab[:, :, 1].astype(np.float32) - 128
        b_channel = lab[:, :, 2].astype(np.float32) - 128
        
        # Calculate average color bias
        avg_a = np.mean(a_channel)  # Green-Red axis
        avg_b = np.mean(b_channel)  # Blue-Yellow axis
        
        # Estimate color temperature based on blue-yellow bias
        # Positive B = yellow (warm), Negative B = blue (cool)
        if avg_b > 0:
            # Warm image
            temperature = 6500 - (avg_b / 127) * 2500
        else:
            # Cool image
            temperature = 6500 + (abs(avg_b) / 127) * 3500
        
        return {
            'estimated_temperature': max(2000, min(12000, temperature)),
            'warmth_bias': avg_b,
            'magenta_green_bias': avg_a,
            'correction_needed': abs(avg_b) > 5 or abs(avg_a) > 5
        }
    
    def detect_color_cast(self, image):
        """Detect overall color cast in the image"""
        # Calculate average RGB values
        avg_rgb = np.mean(image, axis=(0, 1))
        
        # Normalize to detect bias
        total_avg = np.mean(avg_rgb)
        rgb_ratios = avg_rgb / total_avg
        
        # Detect dominant cast
        cast_threshold = 0.05  # 5% threshold
        casts = []
        
        if rgb_ratios[0] > 1 + cast_threshold:
            casts.append(('red_cast', (rgb_ratios[0] - 1) * 100))
        elif rgb_ratios[0] < 1 - cast_threshold:
            casts.append(('cyan_cast', (1 - rgb_ratios[0]) * 100))
        
        if rgb_ratios[1] > 1 + cast_threshold:
            casts.append(('green_cast', (rgb_ratios[1] - 1) * 100))
        elif rgb_ratios[1] < 1 - cast_threshold:
            casts.append(('magenta_cast', (1 - rgb_ratios[1]) * 100))
        
        if rgb_ratios[2] > 1 + cast_threshold:
            casts.append(('blue_cast', (rgb_ratios[2] - 1) * 100))
        elif rgb_ratios[2] < 1 - cast_threshold:
            casts.append(('yellow_cast', (1 - rgb_ratios[2]) * 100))
        
        return {
            'detected_casts': casts,
            'severity': max([severity for _, severity in casts]) if casts else 0,
            'correction_needed': len(casts) > 0
        }
    
    def analyze_saturation_distribution(self, image):
        """Analyze saturation levels throughout the image"""
        # Convert to HSV for saturation analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        saturation = hsv[:, :, 1]
        
        # Calculate saturation statistics
        mean_saturation = np.mean(saturation)
        std_saturation = np.std(saturation)
        
        # Analyze saturation distribution
        hist, bins = np.histogram(saturation, bins=50, range=(0, 255))
        
        # Detect oversaturation and undersaturation
        oversaturated_pixels = np.sum(saturation > 240) / saturation.size * 100
        undersaturated_pixels = np.sum(saturation < 30) / saturation.size * 100
        
        return {
            'mean_saturation': mean_saturation / 255 * 100,
            'saturation_variance': std_saturation,
            'oversaturated_percentage': oversaturated_pixels,
            'undersaturated_percentage': undersaturated_pixels,
            'saturation_distribution': hist.tolist(),
            'needs_saturation_boost': mean_saturation < 80,
            'needs_saturation_reduction': oversaturated_pixels > 5
        }
    
    def generate_correction_suggestions(self, analysis):
        """Generate specific correction recommendations based on analysis"""
        suggestions = []
        
        # Temperature corrections
        temp_data = analysis['color_temperature']
        if temp_data['correction_needed']:
            if temp_data['warmth_bias'] > 10:
                suggestions.append({
                    'type': 'temperature',
                    'adjustment': 'decrease_warmth',
                    'value': -200,
                    'description': 'Reduce yellow cast by cooling temperature'
                })
            elif temp_data['warmth_bias'] < -10:
                suggestions.append({
                    'type': 'temperature',
                    'adjustment': 'increase_warmth',
                    'value': +200,
                    'description': 'Reduce blue cast by warming temperature'
                })
        
        # Color cast corrections
        cast_data = analysis['color_cast_detection']
        for cast_type, severity in cast_data['detected_casts']:
            if severity > 3:  # Significant cast
                color = cast_type.split('_')[0]
                suggestions.append({
                    'type': 'color_cast',
                    'adjustment': f'reduce_{color}_cast',
                    'value': -severity * 0.5,
                    'description': f'Reduce {color} color cast by {severity:.1f}%'
                })
        
        # Saturation adjustments
        sat_data = analysis['saturation_analysis']
        if sat_data['needs_saturation_boost']:
            suggestions.append({
                'type': 'saturation',
                'adjustment': 'increase_saturation',
                'value': +15,
                'description': 'Boost overall saturation for more vibrant colors'
            })
        elif sat_data['needs_saturation_reduction']:
            suggestions.append({
                'type': 'saturation',
                'adjustment': 'decrease_saturation',
                'value': -10,
                'description': 'Reduce saturation to prevent clipping'
            })
        
        return suggestions
    
    def auto_correct_image(self, image_path, output_path, correction_strength=0.7):
        """
        Apply AI-generated corrections to image
        """
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        
        # Analyze image
        analysis = self.analyze_image_color_profile(image_path)
        
        # Apply corrections based on analysis
        corrected_image = image_rgb.copy()
        
        for suggestion in analysis['suggested_corrections']:
            if suggestion['type'] == 'temperature':
                corrected_image = self.apply_temperature_correction(
                    corrected_image, suggestion['value'] * correction_strength
                )
            elif suggestion['type'] == 'saturation':
                corrected_image = self.apply_saturation_correction(
                    corrected_image, suggestion['value'] * correction_strength
                )
        
        # Convert back and save
        corrected_image = (corrected_image * 255).astype(np.uint8)
        corrected_bgr = cv2.cvtColor(corrected_image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, corrected_bgr)
        
        return corrected_image
    
    def apply_temperature_correction(self, image, temperature_shift):
        """Apply temperature shift to image"""
        # Simple temperature adjustment by modifying blue/yellow balance
        temp_factor = temperature_shift / 1000.0
        
        # Adjust blue channel for temperature
        if temp_factor > 0:  # Warmer
            image[:, :, 2] *= (1 - temp_factor * 0.1)  # Reduce blue
            image[:, :, 0] *= (1 + temp_factor * 0.05)  # Slightly increase red
        else:  # Cooler
            image[:, :, 2] *= (1 - temp_factor * 0.1)  # Increase blue
            image[:, :, 0] *= (1 + temp_factor * 0.05)  # Slightly reduce red
        
        return np.clip(image, 0, 1)
    
    def apply_saturation_correction(self, image, saturation_change):
        """Apply saturation adjustment to image"""
        # Convert to HSV for saturation adjustment
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        # Adjust saturation channel
        saturation_multiplier = 1 + (saturation_change / 100.0)
        hsv[:, :, 1] *= saturation_multiplier
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 1)
        
        # Convert back to RGB
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

# Claude Code prompt for AI color correction:
"""
Analyze this photograph and create comprehensive color correction plan:
1. Detect color casts, temperature issues, and saturation problems
2. Generate specific correction values with explanations
3. Create before/after comparison with correction preview
4. Suggest creative grading options that complement the image content
5. Generate batch processing script for similar photos with same lighting conditions
"""
```

## 🔧 Creative Color Grading Techniques

### Cinematic Color Grading Workflows
```yaml
Popular Cinematic Looks:
  Orange and Teal:
    - Shadows: Cool blue tones (-20 temperature, +15 teal tint)
    - Highlights: Warm orange tones (+15 temperature, -10 magenta tint)
    - Midtones: Neutral with slight warmth (+5 temperature)
    - Saturation: Boost orange and teal selectively (+20 each)
  
  Bleach Bypass:
    - Contrast: High contrast with lifted blacks (+30)
    - Saturation: Reduced overall saturation (-25)
    - Highlights: Slightly overexposed (+0.5 stops)
    - Shadows: Retain detail but increase contrast
    - Color: Desaturated with retained silver retention look
  
  Film Emulation:
    - Kodak Vision3: Warm highlights, cool shadows, enhanced skin tones
    - Fuji Eterna: Muted colors, lifted shadows, film grain texture
    - Ilford HP5: High contrast B&W with characteristic grain structure
    - Polaroid: Instant film color palette with cyan shadows, warm highlights

Advanced Grading Techniques:
  Split Toning:
    - Highlight Color: Warm tones for golden hour mood
    - Shadow Color: Cool tones for depth and dimension
    - Balance: 60-70% toward highlights for natural look
    - Saturation: 15-25% for subtle effect, 40-60% for dramatic
  
  Color Wheels (Lift/Gamma/Gain):
    - Lift: Controls shadows and black point
    - Gamma: Controls midtones and overall exposure
    - Gain: Controls highlights and white point
    - Offset: Global color shift affecting entire image
  
  Selective Color Adjustments:
    - Reds: Adjust skin tones and warm elements
    - Oranges: Fine-tune skin tones and autumn colors
    - Yellows: Control sunlight and warm lighting
    - Greens: Adjust foliage and natural elements
    - Cyans: Control sky and water tones
    - Blues: Adjust sky, water, and cool elements
    - Magentas: Fine-tune color balance and creative effects
```

### Unity-Optimized Color Workflows
```csharp
// Unity Color Grading LUT Generator for consistent game visuals
using UnityEngine;
using UnityEngine.Rendering.PostProcessing;

public class ColorGradingLUTGenerator : MonoBehaviour
{
    [Header("Color Grading Parameters")]
    [SerializeField] private float temperature = 0f;
    [SerializeField] private float tint = 0f;
    [SerializeField] private float contrast = 1f;
    [SerializeField] private float saturation = 1f;
    [SerializeField] private float brightness = 0f;
    
    [Header("Creative Grading")]
    [SerializeField] private Color colorFilter = Color.white;
    [SerializeField] private float filterIntensity = 0f;
    [SerializeField] private AnimationCurve customCurve = AnimationCurve.Linear(0, 0, 1, 1);
    
    [Header("LUT Generation")]
    [SerializeField] private int lutSize = 32;
    [SerializeField] private string lutSavePath = "Assets/LUTs/";
    
    private PostProcessVolume postProcessVolume;
    private ColorGrading colorGradingLayer;
    
    void Start()
    {
        SetupPostProcessing();
    }
    
    void SetupPostProcessing()
    {
        postProcessVolume = GetComponent<PostProcessVolume>();
        if (postProcessVolume == null)
        {
            postProcessVolume = gameObject.AddComponent<PostProcessVolume>();
        }
        
        if (postProcessVolume.profile == null)
        {
            postProcessVolume.profile = ScriptableObject.CreateInstance<PostProcessProfile>();
        }
        
        // Add color grading if not present
        if (!postProcessVolume.profile.TryGetSettings(out colorGradingLayer))
        {
            colorGradingLayer = postProcessVolume.profile.AddSettings<ColorGrading>();
        }
        
        ApplyColorGrading();
    }
    
    public void ApplyColorGrading()
    {
        if (colorGradingLayer == null) return;
        
        // Temperature and Tint
        colorGradingLayer.temperature.value = temperature;
        colorGradingLayer.tint.value = tint;
        
        // Basic adjustments
        colorGradingLayer.contrast.value = contrast;
        colorGradingLayer.saturation.value = saturation;
        colorGradingLayer.brightness.value = brightness;
        
        // Creative color filter
        Vector4 colorBalance = new Vector4(
            colorFilter.r * filterIntensity,
            colorFilter.g * filterIntensity,
            colorFilter.b * filterIntensity,
            1f
        );
        colorGradingLayer.colorFilter.value = colorFilter;
        
        // Custom curve application
        ApplyCustomCurve();
    }
    
    void ApplyCustomCurve()
    {
        if (customCurve == null) return;
        
        // Convert AnimationCurve to Spline for Unity post-processing
        Spline masterCurve = new Spline(customCurve, 0f, false, new Vector2(0f, 1f));
        colorGradingLayer.masterCurve.value = masterCurve;
    }
    
    [ContextMenu("Generate LUT")]
    public void GenerateLUT()
    {
        // Create 3D LUT texture
        Texture3D lut = new Texture3D(lutSize, lutSize, lutSize, TextureFormat.RGBA32, false);
        Color[] lutColors = new Color[lutSize * lutSize * lutSize];
        
        for (int b = 0; b < lutSize; b++)
        {
            for (int g = 0; g < lutSize; g++)
            {
                for (int r = 0; r < lutSize; r++)
                {
                    float rNorm = r / (float)(lutSize - 1);
                    float gNorm = g / (float)(lutSize - 1);
                    float bNorm = b / (float)(lutSize - 1);
                    
                    Color inputColor = new Color(rNorm, gNorm, bNorm, 1f);
                    Color gradedColor = ApplyGradingToColor(inputColor);
                    
                    int index = b * lutSize * lutSize + g * lutSize + r;
                    lutColors[index] = gradedColor;
                }
            }
        }
        
        lut.SetPixels(lutColors);
        lut.Apply();
        
        // Save LUT as asset
        string fileName = $"ColorGradingLUT_{System.DateTime.Now:yyyyMMdd_HHmmss}.asset";
        string fullPath = lutSavePath + fileName;
        
        #if UNITY_EDITOR
        UnityEditor.AssetDatabase.CreateAsset(lut, fullPath);
        UnityEditor.AssetDatabase.SaveAssets();
        Debug.Log($"LUT saved to: {fullPath}");
        #endif
    }
    
    Color ApplyGradingToColor(Color input)
    {
        // Apply temperature (simplified)
        float tempFactor = temperature / 100f;
        if (tempFactor > 0)
        {
            input.r = Mathf.Min(1f, input.r * (1 + tempFactor * 0.1f));
            input.b = Mathf.Max(0f, input.b * (1 - tempFactor * 0.1f));
        }
        else
        {
            input.r = Mathf.Max(0f, input.r * (1 + tempFactor * 0.1f));
            input.b = Mathf.Min(1f, input.b * (1 - tempFactor * 0.1f));
        }
        
        // Apply contrast
        input.r = ApplyContrast(input.r, contrast);
        input.g = ApplyContrast(input.g, contrast);
        input.b = ApplyContrast(input.b, contrast);
        
        // Apply saturation
        float luminance = 0.299f * input.r + 0.587f * input.g + 0.114f * input.b;
        input.r = Mathf.Lerp(luminance, input.r, saturation);
        input.g = Mathf.Lerp(luminance, input.g, saturation);
        input.b = Mathf.Lerp(luminance, input.b, saturation);
        
        // Apply brightness
        input.r = Mathf.Clamp01(input.r + brightness);
        input.g = Mathf.Clamp01(input.g + brightness);
        input.b = Mathf.Clamp01(input.b + brightness);
        
        // Apply custom curve
        if (customCurve != null)
        {
            input.r = customCurve.Evaluate(input.r);
            input.g = customCurve.Evaluate(input.g);
            input.b = customCurve.Evaluate(input.b);
        }
        
        return input;
    }
    
    float ApplyContrast(float value, float contrast)
    {
        return Mathf.Clamp01((value - 0.5f) * contrast + 0.5f);
    }
    
    public void LoadPreset(ColorGradingPreset preset)
    {
        temperature = preset.temperature;
        tint = preset.tint;
        contrast = preset.contrast;
        saturation = preset.saturation;
        brightness = preset.brightness;
        colorFilter = preset.colorFilter;
        filterIntensity = preset.filterIntensity;
        customCurve = preset.customCurve;
        
        ApplyColorGrading();
    }
}

[System.Serializable]
public class ColorGradingPreset
{
    public string presetName;
    public float temperature;
    public float tint;
    public float contrast = 1f;
    public float saturation = 1f;
    public float brightness;
    public Color colorFilter = Color.white;
    public float filterIntensity;
    public AnimationCurve customCurve = AnimationCurve.Linear(0, 0, 1, 1);
}
```

## 💡 Key Highlights

### Professional Color Workflow Standards
- **Color Space Consistency**: Maintain proper color space throughout the entire workflow
- **Calibrated Displays**: Use calibrated monitors for accurate color representation
- **Soft Proofing**: Preview final output appearance before printing or publishing
- **Version Control**: Save adjustment layers and settings for future revisions

### AI-Enhanced Efficiency
- **Automated Analysis**: AI detection of color casts, exposure issues, and saturation problems
- **Intelligent Corrections**: Context-aware adjustments based on image content analysis
- **Batch Processing**: Consistent color correction across large photo collections
- **Learning Systems**: AI improvement through user feedback and correction patterns

### Unity Integration Benefits
- **Real-time Grading**: Interactive color adjustment for game development
- **Performance Optimization**: Efficient LUT-based color grading for real-time applications
- **Consistent Visuals**: Unified color palette across all game assets
- **Platform Compatibility**: Color grading that works across different display devices

### Creative Excellence Principles
- **Color Harmony**: Understanding complementary and analogous color relationships
- **Mood Enhancement**: Using color to support narrative and emotional impact
- **Technical Precision**: Maintaining detail and avoiding color artifacts
- **Artistic Vision**: Balancing technical accuracy with creative interpretation

This comprehensive color correction and grading system provides the foundation for creating professional-quality images while leveraging AI automation for efficiency and consistency in both photography and Unity game development workflows.