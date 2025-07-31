# @44-Localization-System

## 🎯 Core Concept
Automated localization system for managing multi-language support, text extraction, and translation workflows.

## 🔧 Implementation

### Localization Manager
```csharp
using UnityEngine;
using System.Collections.Generic;
using System.IO;
using UnityEngine.Events;

public class LocalizationManager : MonoBehaviour
{
    public static LocalizationManager Instance;
    
    [Header("Localization Settings")]
    public SystemLanguage defaultLanguage = SystemLanguage.English;
    public bool autoDetectLanguage = true;
    public bool loadOnStart = true;
    public string localizationFolder = "Localization";
    
    [Header("Events")]
    public UnityEvent OnLanguageChanged;
    
    private Dictionary<string, Dictionary<string, string>> localizedTexts;
    private SystemLanguage currentLanguage;
    private bool isInitialized = false;
    
    public SystemLanguage CurrentLanguage => currentLanguage;
    public bool IsInitialized => isInitialized;
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            
            if (loadOnStart)
            {
                InitializeLocalization();
            }
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void InitializeLocalization()
    {
        localizedTexts = new Dictionary<string, Dictionary<string, string>>();
        
        // Determine language to use
        if (autoDetectLanguage)
        {
            currentLanguage = DetectSystemLanguage();
        }
        else
        {
            currentLanguage = defaultLanguage;
        }
        
        // Load saved language preference if exists
        if (PlayerPrefs.HasKey("SelectedLanguage"))
        {
            string savedLanguage = PlayerPrefs.GetString("SelectedLanguage");
            if (System.Enum.TryParse(savedLanguage, out SystemLanguage parsedLanguage))
            {
                currentLanguage = parsedLanguage;
            }
        }
        
        LoadAllLocalizations();
        isInitialized = true;
        
        Debug.Log($"Localization initialized with language: {currentLanguage}");
    }
    
    SystemLanguage DetectSystemLanguage()
    {
        SystemLanguage detectedLanguage = Application.systemLanguage;
        
        // Check if we support the detected language
        if (IsSupportedLanguage(detectedLanguage))
        {
            return detectedLanguage;
        }
        
        // Fallback to default if not supported
        return defaultLanguage;
    }
    
    bool IsSupportedLanguage(SystemLanguage language)
    {
        string languageCode = GetLanguageCode(language);
        string filePath = Path.Combine(Application.streamingAssetsPath, localizationFolder, $"{languageCode}.json");
        return File.Exists(filePath);
    }
    
    void LoadAllLocalizations()
    {
        string localizationPath = Path.Combine(Application.streamingAssetsPath, localizationFolder);
        
        if (!Directory.Exists(localizationPath))
        {
            Debug.LogWarning($"Localization folder not found: {localizationPath}");
            return;
        }
        
        string[] jsonFiles = Directory.GetFiles(localizationPath, "*.json");
        
        foreach (string filePath in jsonFiles)
        {
            string fileName = Path.GetFileNameWithoutExtension(filePath);
            LoadLocalizationFile(fileName, filePath);
        }
        
        Debug.Log($"Loaded {localizedTexts.Count} localization files");
    }
    
    void LoadLocalizationFile(string languageCode, string filePath)
    {
        try
        {
            string jsonContent = File.ReadAllText(filePath);
            LocalizationData data = JsonUtility.FromJson<LocalizationData>(jsonContent);
            
            if (data != null && data.entries != null)
            {
                Dictionary<string, string> languageTexts = new Dictionary<string, string>();
                
                foreach (var entry in data.entries)
                {
                    languageTexts[entry.key] = entry.value;
                }
                
                localizedTexts[languageCode] = languageTexts;
                Debug.Log($"Loaded {languageTexts.Count} entries for language: {languageCode}");
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Failed to load localization file {filePath}: {e.Message}");
        }
    }
    
    public string GetLocalizedText(string key, SystemLanguage? language = null)
    {
        if (!isInitialized)
        {
            Debug.LogWarning("Localization not initialized");
            return key;
        }
        
        SystemLanguage targetLanguage = language ?? currentLanguage;
        string languageCode = GetLanguageCode(targetLanguage);
        
        // Try to get text in target language
        if (localizedTexts.ContainsKey(languageCode) && 
            localizedTexts[languageCode].ContainsKey(key))
        {
            return localizedTexts[languageCode][key];
        }
        
        // Fallback to default language
        string defaultLanguageCode = GetLanguageCode(defaultLanguage);
        if (localizedTexts.ContainsKey(defaultLanguageCode) && 
            localizedTexts[defaultLanguageCode].ContainsKey(key))
        {
            Debug.LogWarning($"Localization key '{key}' not found for {targetLanguage}, using default language");
            return localizedTexts[defaultLanguageCode][key];
        }
        
        // Return key if no localization found
        Debug.LogWarning($"Localization key '{key}' not found");
        return key;
    }
    
    public void ChangeLanguage(SystemLanguage newLanguage)
    {
        if (!IsSupportedLanguage(newLanguage))
        {
            Debug.LogWarning($"Language {newLanguage} is not supported");
            return;
        }
        
        currentLanguage = newLanguage;
        
        // Save preference
        PlayerPrefs.SetString("SelectedLanguage", newLanguage.ToString());
        PlayerPrefs.Save();
        
        // Notify listeners
        OnLanguageChanged?.Invoke();
        
        Debug.Log($"Language changed to: {currentLanguage}");
    }
    
    public List<SystemLanguage> GetSupportedLanguages()
    {
        List<SystemLanguage> supportedLanguages = new List<SystemLanguage>();
        
        foreach (string languageCode in localizedTexts.Keys)
        {
            SystemLanguage language = GetLanguageFromCode(languageCode);
            if (language != SystemLanguage.Unknown)
            {
                supportedLanguages.Add(language);
            }
        }
        
        return supportedLanguages;
    }
    
    string GetLanguageCode(SystemLanguage language)
    {
        switch (language)
        {
            case SystemLanguage.English: return "en";
            case SystemLanguage.Spanish: return "es";
            case SystemLanguage.French: return "fr";
            case SystemLanguage.German: return "de";
            case SystemLanguage.Italian: return "it";
            case SystemLanguage.Portuguese: return "pt";
            case SystemLanguage.Russian: return "ru";
            case SystemLanguage.Japanese: return "ja";
            case SystemLanguage.Korean: return "ko";
            case SystemLanguage.Chinese: return "zh";
            case SystemLanguage.ChineseSimplified: return "zh-CN";
            case SystemLanguage.ChineseTraditional: return "zh-TW";
            case SystemLanguage.Arabic: return "ar";
            case SystemLanguage.Dutch: return "nl";
            case SystemLanguage.Polish: return "pl";
            case SystemLanguage.Swedish: return "sv";
            case SystemLanguage.Norwegian: return "no";
            case SystemLanguage.Danish: return "da";
            case SystemLanguage.Finnish: return "fi";
            case SystemLanguage.Turkish: return "tr";
            case SystemLanguage.Greek: return "el";
            case SystemLanguage.Hebrew: return "he";
            case SystemLanguage.Thai: return "th";
            case SystemLanguage.Vietnamese: return "vi";
            case SystemLanguage.Hindi: return "hi";
            default: return "en";
        }
    }
    
    SystemLanguage GetLanguageFromCode(string code)
    {
        switch (code.ToLower())
        {
            case "en": return SystemLanguage.English;
            case "es": return SystemLanguage.Spanish;
            case "fr": return SystemLanguage.French;
            case "de": return SystemLanguage.German;
            case "it": return SystemLanguage.Italian;
            case "pt": return SystemLanguage.Portuguese;
            case "ru": return SystemLanguage.Russian;
            case "ja": return SystemLanguage.Japanese;
            case "ko": return SystemLanguage.Korean;
            case "zh": return SystemLanguage.Chinese;
            case "zh-cn": return SystemLanguage.ChineseSimplified;
            case "zh-tw": return SystemLanguage.ChineseTraditional;
            case "ar": return SystemLanguage.Arabic;
            case "nl": return SystemLanguage.Dutch;
            case "pl": return SystemLanguage.Polish;
            case "sv": return SystemLanguage.Swedish;
            case "no": return SystemLanguage.Norwegian;
            case "da": return SystemLanguage.Danish;
            case "fi": return SystemLanguage.Finnish;
            case "tr": return SystemLanguage.Turkish;
            case "el": return SystemLanguage.Greek;
            case "he": return SystemLanguage.Hebrew;
            case "th": return SystemLanguage.Thai;
            case "vi": return SystemLanguage.Vietnamese;
            case "hi": return SystemLanguage.Hindi;
            default: return SystemLanguage.Unknown;
        }
    }
    
    [ContextMenu("Export Missing Keys")]
    public void ExportMissingKeys()
    {
        HashSet<string> allKeys = new HashSet<string>();
        
        // Collect all keys from all languages
        foreach (var languageDict in localizedTexts.Values)
        {
            foreach (string key in languageDict.Keys)
            {
                allKeys.Add(key);
            }
        }
        
        // Find missing keys for each language
        Dictionary<string, List<string>> missingKeys = new Dictionary<string, List<string>>();
        
        foreach (var kvp in localizedTexts)
        {
            string languageCode = kvp.Key;
            Dictionary<string, string> languageTexts = kvp.Value;
            
            List<string> missing = new List<string>();
            foreach (string key in allKeys)
            {
                if (!languageTexts.ContainsKey(key))
                {
                    missing.Add(key);
                }
            }
            
            if (missing.Count > 0)
            {
                missingKeys[languageCode] = missing;
            }
        }
        
        // Export to file
        string reportPath = "localization_missing_keys.txt";
        using (StreamWriter writer = new StreamWriter(reportPath))
        {
            writer.WriteLine("Missing Localization Keys Report");
            writer.WriteLine($"Generated: {System.DateTime.Now}");
            writer.WriteLine();
            
            foreach (var kvp in missingKeys)
            {
                writer.WriteLine($"Language: {kvp.Key}");
                writer.WriteLine($"Missing keys: {kvp.Value.Count}");
                foreach (string key in kvp.Value)
                {
                    writer.WriteLine($"  - {key}");
                }
                writer.WriteLine();
            }
        }
        
        Debug.Log($"Missing keys report exported to: {reportPath}");
    }
    
    public void CreateTemplateFile(SystemLanguage language)
    {
        string languageCode = GetLanguageCode(language);
        string templatePath = Path.Combine(Application.streamingAssetsPath, localizationFolder, $"{languageCode}_template.json");
        
        // Collect all keys from existing files
        HashSet<string> allKeys = new HashSet<string>();
        foreach (var languageDict in localizedTexts.Values)
        {
            foreach (string key in languageDict.Keys)
            {
                allKeys.Add(key);
            }
        }
        
        // Create template with empty values
        LocalizationData template = new LocalizationData();
        template.entries = new List<LocalizationEntry>();
        
        foreach (string key in allKeys)
        {
            template.entries.Add(new LocalizationEntry { key = key, value = "" });
        }
        
        string json = JsonUtility.ToJson(template, true);
        
        Directory.CreateDirectory(Path.GetDirectoryName(templatePath));
        File.WriteAllText(templatePath, json);
        
        Debug.Log($"Template file created: {templatePath}");
    }
}

// Localized Text Component
public class LocalizedText : MonoBehaviour
{
    [Header("Localization")]
    public string localizationKey = "";
    public bool updateOnLanguageChange = true;
    
    private UnityEngine.UI.Text textComponent;
    private TMPro.TextMeshProUGUI tmpTextComponent;
    
    void Start()
    {
        // Get text component
        textComponent = GetComponent<UnityEngine.UI.Text>();
        tmpTextComponent = GetComponent<TMPro.TextMeshProUGUI>();
        
        // Subscribe to language changes
        if (updateOnLanguageChange && LocalizationManager.Instance != null)
        {
            LocalizationManager.Instance.OnLanguageChanged.AddListener(UpdateText);
        }
        
        // Initial text update
        UpdateText();
    }
    
    void UpdateText()
    {
        if (LocalizationManager.Instance == null || string.IsNullOrEmpty(localizationKey))
            return;
        
        string localizedText = LocalizationManager.Instance.GetLocalizedText(localizationKey);
        
        if (textComponent != null)
        {
            textComponent.text = localizedText;
        }
        else if (tmpTextComponent != null)
        {
            tmpTextComponent.text = localizedText;
        }
    }
    
    public void SetLocalizationKey(string newKey)
    {
        localizationKey = newKey;
        UpdateText();
    }
    
    void OnDestroy()
    {
        if (LocalizationManager.Instance != null)
        {
            LocalizationManager.Instance.OnLanguageChanged.RemoveListener(UpdateText);
        }
    }
}

// Data structures
[System.Serializable]
public class LocalizationData
{
    public string language;
    public string version;
    public List<LocalizationEntry> entries;
}

[System.Serializable]
public class LocalizationEntry
{
    public string key;
    public string value;
}

// Language Selection UI
public class LanguageSelector : MonoBehaviour
{
    [Header("UI References")]
    public UnityEngine.UI.Dropdown languageDropdown;
    public UnityEngine.UI.Button applyButton;
    
    void Start()
    {
        SetupLanguageDropdown();
        
        if (applyButton != null)
        {
            applyButton.onClick.AddListener(ApplyLanguageSelection);
        }
    }
    
    void SetupLanguageDropdown()
    {
        if (languageDropdown == null || LocalizationManager.Instance == null)
            return;
        
        languageDropdown.ClearOptions();
        
        List<SystemLanguage> supportedLanguages = LocalizationManager.Instance.GetSupportedLanguages();
        List<string> languageNames = new List<string>();
        
        int currentLanguageIndex = 0;
        for (int i = 0; i < supportedLanguages.Count; i++)
        {
            SystemLanguage language = supportedLanguages[i];
            languageNames.Add(GetLanguageDisplayName(language));
            
            if (language == LocalizationManager.Instance.CurrentLanguage)
            {
                currentLanguageIndex = i;
            }
        }
        
        languageDropdown.AddOptions(languageNames);
        languageDropdown.value = currentLanguageIndex;
    }
    
    void ApplyLanguageSelection()
    {
        if (languageDropdown == null || LocalizationManager.Instance == null)
            return;
        
        List<SystemLanguage> supportedLanguages = LocalizationManager.Instance.GetSupportedLanguages();
        
        if (languageDropdown.value < supportedLanguages.Count)
        {
            SystemLanguage selectedLanguage = supportedLanguages[languageDropdown.value];
            LocalizationManager.Instance.ChangeLanguage(selectedLanguage);
        }
    }
    
    string GetLanguageDisplayName(SystemLanguage language)
    {
        switch (language)
        {
            case SystemLanguage.English: return "English";
            case SystemLanguage.Spanish: return "Español";
            case SystemLanguage.French: return "Français";
            case SystemLanguage.German: return "Deutsch";
            case SystemLanguage.Italian: return "Italiano";
            case SystemLanguage.Portuguese: return "Português";
            case SystemLanguage.Russian: return "Русский";
            case SystemLanguage.Japanese: return "日本語";
            case SystemLanguage.Korean: return "한국어";
            case SystemLanguage.Chinese: return "中文";
            case SystemLanguage.ChineseSimplified: return "简体中文";
            case SystemLanguage.ChineseTraditional: return "繁體中文";
            case SystemLanguage.Arabic: return "العربية";
            case SystemLanguage.Dutch: return "Nederlands";
            case SystemLanguage.Polish: return "Polski";
            case SystemLanguage.Swedish: return "Svenska";
            case SystemLanguage.Norwegian: return "Norsk";
            case SystemLanguage.Danish: return "Dansk";
            case SystemLanguage.Finnish: return "Suomi";
            case SystemLanguage.Turkish: return "Türkçe";
            case SystemLanguage.Greek: return "Ελληνικά";
            case SystemLanguage.Hebrew: return "עברית";
            case SystemLanguage.Thai: return "ไทย";
            case SystemLanguage.Vietnamese: return "Tiếng Việt";
            case SystemLanguage.Hindi: return "हिन्दी";
            default: return language.ToString();
        }
    }
}

// Editor Tools
#if UNITY_EDITOR
using UnityEditor;

public class LocalizationTools : EditorWindow
{
    [MenuItem("Tools/Localization/Localization Tools")]
    public static void ShowWindow()
    {
        GetWindow<LocalizationTools>("Localization Tools");
    }
    
    void OnGUI()
    {
        GUILayout.Label("Localization Tools", EditorStyles.boldLabel);
        
        EditorGUILayout.Space();
        
        if (GUILayout.Button("Scan Scene for Text Components"))
        {
            ScanSceneForTextComponents();
        }
        
        if (GUILayout.Button("Generate Localization Keys"))
        {
            GenerateLocalizationKeys();
        }
        
        if (GUILayout.Button("Create Language Template"))
        {
            CreateLanguageTemplate();
        }
        
        if (GUILayout.Button("Validate Localization Files"))
        {
            ValidateLocalizationFiles();
        }
    }
    
    void ScanSceneForTextComponents()
    {
        UnityEngine.UI.Text[] textComponents = FindObjectsOfType<UnityEngine.UI.Text>();
        TMPro.TextMeshProUGUI[] tmpComponents = FindObjectsOfType<TMPro.TextMeshProUGUI>();
        
        Debug.Log($"Found {textComponents.Length} Text components and {tmpComponents.Length} TextMeshPro components");
        
        foreach (var text in textComponents)
        {
            if (!string.IsNullOrEmpty(text.text))
            {
                Debug.Log($"Text: '{text.text}' on {text.gameObject.name}");
            }
        }
        
        foreach (var tmp in tmpComponents)
        {
            if (!string.IsNullOrEmpty(tmp.text))
            {
                Debug.Log($"TMP Text: '{tmp.text}' on {tmp.gameObject.name}");
            }
        }
    }
    
    void GenerateLocalizationKeys()
    {
        Debug.Log("Generating localization keys from scene text components...");
        // Implementation would scan and create keys
    }
    
    void CreateLanguageTemplate()
    {
        if (LocalizationManager.Instance != null)
        {
            LocalizationManager.Instance.CreateTemplateFile(SystemLanguage.English);
        }
        else
        {
            Debug.LogWarning("LocalizationManager instance not found");
        }
    }
    
    void ValidateLocalizationFiles()
    {
        Debug.Log("Validating localization files...");
        // Implementation would check for missing keys, formatting issues, etc.
    }
}
#endif
```

## 🚀 AI/LLM Integration
- Automatically extract text from UI components for localization
- Generate translation templates and missing key reports
- Provide intelligent text formatting for different languages

## 💡 Key Benefits
- Automated multi-language support
- Dynamic language switching
- Missing translation detection