# @15-Localization-Manager

## 🎯 Core Concept
Automated localization system for multi-language game support with CSV import/export capabilities.

## 🔧 Implementation

### Localization System
```csharp
using UnityEngine;
using System.Collections.Generic;
using System.IO;

public class LocalizationManager : MonoBehaviour
{
    public static LocalizationManager Instance;
    
    [Header("Settings")]
    public SystemLanguage defaultLanguage = SystemLanguage.English;
    public string localizationFileName = "localization.csv";
    
    private Dictionary<string, Dictionary<SystemLanguage, string>> localizedText;
    private SystemLanguage currentLanguage;
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeLocalization();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void InitializeLocalization()
    {
        localizedText = new Dictionary<string, Dictionary<SystemLanguage, string>>();
        currentLanguage = Application.systemLanguage;
        LoadLocalizationData();
    }
    
    public void LoadLocalizationData()
    {
        string filePath = Path.Combine(Application.streamingAssetsPath, localizationFileName);
        
        if (File.Exists(filePath))
        {
            string[] lines = File.ReadAllLines(filePath);
            
            if (lines.Length > 0)
            {
                // Parse header to get supported languages
                string[] header = lines[0].Split(',');
                SystemLanguage[] languages = new SystemLanguage[header.Length - 1];
                
                for (int i = 1; i < header.Length; i++)
                {
                    System.Enum.TryParse(header[i], out languages[i - 1]);
                }
                
                // Parse localization data
                for (int i = 1; i < lines.Length; i++)
                {
                    string[] values = lines[i].Split(',');
                    string key = values[0];
                    
                    localizedText[key] = new Dictionary<SystemLanguage, string>();
                    
                    for (int j = 1; j < values.Length && j - 1 < languages.Length; j++)
                    {
                        localizedText[key][languages[j - 1]] = values[j];
                    }
                }
            }
        }
        else
        {
            Debug.LogWarning($"Localization file not found: {filePath}");
        }
    }
    
    public string GetLocalizedText(string key)
    {
        if (localizedText.ContainsKey(key))
        {
            if (localizedText[key].ContainsKey(currentLanguage))
            {
                return localizedText[key][currentLanguage];
            }
            else if (localizedText[key].ContainsKey(defaultLanguage))
            {
                return localizedText[key][defaultLanguage];
            }
        }
        
        Debug.LogWarning($"Localization key not found: {key}");
        return key; // Return key as fallback
    }
    
    public void SetLanguage(SystemLanguage language)
    {
        currentLanguage = language;
        // Notify all localized text components to update
        LocalizedText[] localizedTexts = FindObjectsOfType<LocalizedText>();
        foreach (var localizedText in localizedTexts)
        {
            localizedText.UpdateText();
        }
    }
    
    public SystemLanguage GetCurrentLanguage()
    {
        return currentLanguage;
    }
}

// Component for UI Text localization
[RequireComponent(typeof(UnityEngine.UI.Text))]
public class LocalizedText : MonoBehaviour
{
    [SerializeField] private string localizationKey;
    private UnityEngine.UI.Text textComponent;
    
    void Start()
    {
        textComponent = GetComponent<UnityEngine.UI.Text>();
        UpdateText();
    }
    
    public void UpdateText()
    {
        if (LocalizationManager.Instance != null && !string.IsNullOrEmpty(localizationKey))
        {
            textComponent.text = LocalizationManager.Instance.GetLocalizedText(localizationKey);
        }
    }
    
    public void SetLocalizationKey(string key)
    {
        localizationKey = key;
        UpdateText();
    }
}
```

### Localization Editor Tools
```csharp
#if UNITY_EDITOR
using UnityEditor;
using System.Text;

public class LocalizationTools
{
    [MenuItem("Tools/Localization/Generate CSV Template")]
    public static void GenerateCSVTemplate()
    {
        StringBuilder csv = new StringBuilder();
        csv.AppendLine("Key,English,Spanish,French,German,Japanese");
        
        // Add sample entries
        csv.AppendLine("ui_start_game,Start Game,Iniciar Juego,Commencer le Jeu,Spiel Starten,ゲーム開始");
        csv.AppendLine("ui_settings,Settings,Configuración,Paramètres,Einstellungen,設定");
        csv.AppendLine("ui_quit,Quit,Salir,Quitter,Beenden,終了");
        csv.AppendLine("game_score,Score,Puntuación,Score,Punktzahl,スコア");
        csv.AppendLine("game_level,Level,Nivel,Niveau,Level,レベル");
        
        string path = Path.Combine(Application.streamingAssetsPath, "localization_template.csv");
        Directory.CreateDirectory(Application.streamingAssetsPath);
        File.WriteAllText(path, csv.ToString());
        
        AssetDatabase.Refresh();
        Debug.Log($"Localization template generated: {path}");
    }
    
    [MenuItem("Tools/Localization/Find Missing Keys")]
    public static void FindMissingKeys()
    {
        LocalizedText[] localizedTexts = Object.FindObjectsOfType<LocalizedText>();
        HashSet<string> usedKeys = new HashSet<string>();
        
        foreach (var localizedText in localizedTexts)
        {
            string key = localizedText.GetComponent<LocalizedText>().localizationKey;
            if (!string.IsNullOrEmpty(key))
            {
                usedKeys.Add(key);
            }
        }
        
        // Load existing localization data
        string filePath = Path.Combine(Application.streamingAssetsPath, "localization.csv");
        HashSet<string> existingKeys = new HashSet<string>();
        
        if (File.Exists(filePath))
        {
            string[] lines = File.ReadAllLines(filePath);
            for (int i = 1; i < lines.Length; i++)
            {
                string[] values = lines[i].Split(',');
                if (values.Length > 0)
                {
                    existingKeys.Add(values[0]);
                }
            }
        }
        
        // Find missing keys
        foreach (string usedKey in usedKeys)
        {
            if (!existingKeys.Contains(usedKey))
            {
                Debug.LogWarning($"Missing localization key: {usedKey}");
            }
        }
        
        Debug.Log("Missing key check complete");
    }
}

// Custom property drawer for localization keys
[CustomPropertyDrawer(typeof(LocalizationKeyAttribute))]
public class LocalizationKeyDrawer : PropertyDrawer
{
    public override void OnGUI(Rect position, SerializedProperty property, GUIContent label)
    {
        EditorGUI.PropertyField(position, property, label);
        
        // Add button to validate key
        Rect buttonRect = new Rect(position.x + position.width - 60, position.y, 60, position.height);
        if (GUI.Button(buttonRect, "Validate"))
        {
            // Validate if key exists in localization data
            Debug.Log($"Validating key: {property.stringValue}");
        }
    }
}

public class LocalizationKeyAttribute : PropertyAttribute { }
#endif
```

## 🚀 AI/LLM Integration
- Automatically translate text keys using AI translation services
- Generate localization keys from UI text content
- Validate translation quality and consistency

## 💡 Key Benefits
- Streamlined multi-language support
- Automated translation workflows
- Consistent localization management