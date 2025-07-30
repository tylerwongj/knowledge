# @51-Data-Validation-Framework

## 🎯 Core Concept
Automated data validation framework for ensuring data integrity, type safety, and business rule compliance across game systems.

## 🔧 Implementation

### Data Validation Manager
```csharp
using UnityEngine;
using System.Collections.Generic;
using System;
using System.Reflection;
using System.Linq;

public class DataValidationManager : MonoBehaviour
{
    public static DataValidationManager Instance;
    
    [Header("Validation Settings")]
    public bool enableValidation = true;
    public bool enableRuntimeValidation = true;
    public bool logValidationErrors = true;
    public bool throwOnValidationFailure = false;
    public ValidationLevel minimumLevel = ValidationLevel.Warning;
    
    [Header("Performance")]
    public bool enableValidationCaching = true;
    public int maxCacheSize = 1000;
    public float cacheExpirationTime = 300f;
    
    private Dictionary<Type, List<ValidationRule>> typeValidators;
    private Dictionary<string, ValidationResult> validationCache;
    private List<IValidator> customValidators;
    private ValidationStatistics statistics;
    
    public System.Action<ValidationResult> OnValidationFailed;
    public System.Action<ValidationResult> OnValidationPassed;
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeValidation();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void InitializeValidation()
    {
        typeValidators = new Dictionary<Type, List<ValidationRule>>();
        validationCache = new Dictionary<string, ValidationResult>();
        customValidators = new List<IValidator>();
        statistics = new ValidationStatistics();
        
        // Register built-in validators
        RegisterBuiltInValidators();
        
        // Auto-discover validators from assemblies
        DiscoverValidators();
        
        Debug.Log("Data Validation Manager initialized");
    }
    
    void RegisterBuiltInValidators()
    {
        // Register common validation rules
        RegisterValidator<PlayerData>(new PlayerDataValidator());
        RegisterValidator<GameSettings>(new GameSettingsValidator());
        RegisterValidator<SaveData>(new SaveDataValidator());
        RegisterValidator<ItemData>(new ItemDataValidator());
        RegisterValidator<LevelData>(new LevelDataValidator());
    }
    
    void DiscoverValidators()
    {
        // Find all types that implement IValidator
        var validatorTypes = Assembly.GetExecutingAssembly()
            .GetTypes()
            .Where(t => typeof(IValidator).IsAssignableFrom(t) && !t.IsInterface && !t.IsAbstract);
        
        foreach (Type validatorType in validatorTypes)
        {
            try
            {
                IValidator validator = (IValidator)Activator.CreateInstance(validatorType);
                customValidators.Add(validator);
                Debug.Log($"Discovered validator: {validatorType.Name}");
            }
            catch (Exception e)
            {
                Debug.LogError($"Failed to create validator {validatorType.Name}: {e.Message}");
            }
        }
    }
    
    public void RegisterValidator<T>(IValidator<T> validator)
    {
        Type type = typeof(T);
        
        if (!typeValidators.ContainsKey(type))
        {
            typeValidators[type] = new List<ValidationRule>();
        }
        
        ValidationRule rule = new ValidationRule
        {
            validator = validator,
            targetType = type,
            level = ValidationLevel.Error
        };
        
        typeValidators[type].Add(rule);
    }
    
    public ValidationResult ValidateObject<T>(T obj, ValidationContext context = null)
    {
        if (!enableValidation)
        {
            return ValidationResult.Success();
        }
        
        Type type = typeof(T);
        string cacheKey = GenerateCacheKey(obj, type);
        
        // Check cache
        if (enableValidationCaching && validationCache.ContainsKey(cacheKey))
        {
            ValidationResult cachedResult = validationCache[cacheKey];
            if (Time.time - cachedResult.timestamp < cacheExpirationTime)
            {
                statistics.cacheHits++;
                return cachedResult;
            }
            else
            {
                validationCache.Remove(cacheKey);
            }
        }
        
        ValidationResult result = PerformValidation(obj, type, context);
        
        // Cache result
        if (enableValidationCaching)
        {
            CacheValidationResult(cacheKey, result);
        }
        
        // Update statistics
        UpdateStatistics(result);
        
        // Handle result
        HandleValidationResult(result);
        
        return result;
    }
    
    ValidationResult PerformValidation<T>(T obj, Type type, ValidationContext context)
    {
        ValidationResult result = new ValidationResult
        {
            isValid = true,
            errors = new List<ValidationError>(),
            warnings = new List<ValidationWarning>(),
            timestamp = Time.time,
            objectType = type.Name
        };
        
        if (context == null)
        {
            context = new ValidationContext { target = obj };
        }
        
        // Validate with type-specific validators
        if (typeValidators.ContainsKey(type))
        {
            foreach (ValidationRule rule in typeValidators[type])
            {
                try
                {
                    ValidationResult ruleResult = rule.validator.Validate(obj, context);
                    MergeValidationResults(result, ruleResult);
                }
                catch (Exception e)
                {
                    result.errors.Add(new ValidationError
                    {
                        message = $"Validator exception: {e.Message}",
                        propertyName = "Validator",
                        level = ValidationLevel.Error
                    });
                }
            }
        }
        
        // Validate with custom validators
        foreach (IValidator validator in customValidators)
        {
            if (validator.CanValidate(type))
            {
                try
                {
                    ValidationResult customResult = validator.Validate(obj, context);
                    MergeValidationResults(result, customResult);
                }
                catch (Exception e)
                {
                    result.errors.Add(new ValidationError
                    {
                        message = $"Custom validator exception: {e.Message}",
                        propertyName = "CustomValidator",
                        level = ValidationLevel.Error
                    });
                }
            }
        }
        
        // Validate with reflection-based attribute validation
        ValidateWithAttributes(obj, result, context);
        
        // Set overall validity
        result.isValid = result.errors.Count == 0 && 
                        (minimumLevel != ValidationLevel.Warning || result.warnings.Count == 0);
        
        return result;
    }
    
    void ValidateWithAttributes<T>(T obj, ValidationResult result, ValidationContext context)
    {
        Type type = typeof(T);
        PropertyInfo[] properties = type.GetProperties();
        
        foreach (PropertyInfo property in properties)
        {
            object value = property.GetValue(obj);
            
            // Check validation attributes
            object[] attributes = property.GetCustomAttributes(typeof(ValidationAttribute), true);
            
            foreach (ValidationAttribute attribute in attributes)
            {
                try
                {
                    ValidationResult attrResult = attribute.Validate(value, property.Name, context);
                    MergeValidationResults(result, attrResult);
                }
                catch (Exception e)
                {
                    result.errors.Add(new ValidationError
                    {
                        message = $"Attribute validation failed: {e.Message}",
                        propertyName = property.Name,
                        level = ValidationLevel.Error
                    });
                }
            }
        }
    }
    
    void MergeValidationResults(ValidationResult target, ValidationResult source)
    {
        if (source.errors != null)
        {
            target.errors.AddRange(source.errors);
        }
        
        if (source.warnings != null)
        {
            target.warnings.AddRange(source.warnings);
        }
    }
    
    string GenerateCacheKey<T>(T obj, Type type)
    {
        // Simple hash-based cache key
        int hash = obj?.GetHashCode() ?? 0;
        return $"{type.Name}_{hash}";
    }
    
    void CacheValidationResult(string key, ValidationResult result)
    {
        if (validationCache.Count >= maxCacheSize)
        {
            // Remove oldest entry
            string oldestKey = validationCache.Keys.FirstOrDefault();
            if (oldestKey != null)
            {
                validationCache.Remove(oldestKey);
            }
        }
        
        validationCache[key] = result;
    }
    
    void UpdateStatistics(ValidationResult result)
    {
        statistics.totalValidations++;
        
        if (result.isValid)
        {
            statistics.successfulValidations++;
        }
        else
        {
            statistics.failedValidations++;
        }
        
        statistics.totalErrors += result.errors.Count;
        statistics.totalWarnings += result.warnings.Count;
    }
    
    void HandleValidationResult(ValidationResult result)
    {
        if (result.isValid)
        {
            OnValidationPassed?.Invoke(result);
        }
        else
        {
            OnValidationFailed?.Invoke(result);
            
            if (logValidationErrors)
            {
                LogValidationResult(result);
            }
            
            if (throwOnValidationFailure)
            {
                throw new ValidationException(result);
            }
        }
    }
    
    void LogValidationResult(ValidationResult result)
    {
        if (result.errors.Count > 0)
        {
            Debug.LogError($"Validation failed for {result.objectType}:");
            foreach (var error in result.errors)
            {
                Debug.LogError($"  - {error.propertyName}: {error.message}");
            }
        }
        
        if (result.warnings.Count > 0)
        {
            Debug.LogWarning($"Validation warnings for {result.objectType}:");
            foreach (var warning in result.warnings)
            {
                Debug.LogWarning($"  - {warning.propertyName}: {warning.message}");
            }
        }
    }
    
    public bool ValidateAndFix<T>(ref T obj, ValidationContext context = null)
    {
        ValidationResult result = ValidateObject(obj, context);
        
        if (!result.isValid)
        {
            // Try to auto-fix common issues
            bool wasFixed = TryAutoFix(ref obj, result);
            
            if (wasFixed)
            {
                // Re-validate after fixing
                ValidationResult fixedResult = ValidateObject(obj, context);
                return fixedResult.isValid;
            }
        }
        
        return result.isValid;
    }
    
    bool TryAutoFix<T>(ref T obj, ValidationResult result)
    {
        bool wasFixed = false;
        Type type = typeof(T);
        
        foreach (var error in result.errors)
        {
            // Try to fix common validation errors
            if (error.message.Contains("null") && error.propertyName != null)
            {
                PropertyInfo property = type.GetProperty(error.propertyName);
                if (property != null && property.CanWrite)
                {
                    // Set default value for null properties
                    object defaultValue = GetDefaultValue(property.PropertyType);
                    property.SetValue(obj, defaultValue);
                    wasFixed = true;
                }
            }
            else if (error.message.Contains("range") && error.propertyName != null)
            {
                PropertyInfo property = type.GetProperty(error.propertyName);
                if (property != null && property.CanWrite)
                {
                    // Clamp numeric values to valid ranges
                    object value = property.GetValue(obj);
                    object clampedValue = ClampToValidRange(value, property);
                    if (clampedValue != null)
                    {
                        property.SetValue(obj, clampedValue);
                        wasFixed = true;
                    }
                }
            }
        }
        
        return wasFixed;
    }
    
    object GetDefaultValue(Type type)
    {
        if (type.IsValueType)
        {
            return Activator.CreateInstance(type);
        }
        else if (type == typeof(string))
        {
            return "";
        }
        else if (type.IsArray)
        {
            return Array.CreateInstance(type.GetElementType(), 0);
        }
        
        return null;
    }
    
    object ClampToValidRange(object value, PropertyInfo property)
    {
        RangeAttribute rangeAttr = property.GetCustomAttribute<RangeAttribute>();
        if (rangeAttr != null && value is IComparable)
        {
            if (value is float f)
                return Mathf.Clamp(f, rangeAttr.min, rangeAttr.max);
            else if (value is int i)
                return Mathf.Clamp(i, (int)rangeAttr.min, (int)rangeAttr.max);
        }
        
        return null;
    }
    
    public ValidationStatistics GetStatistics()
    {
        return statistics;
    }
    
    public void ClearCache()
    {
        validationCache.Clear();
        Debug.Log("Validation cache cleared");
    }
    
    public void ResetStatistics()
    {
        statistics = new ValidationStatistics();
        Debug.Log("Validation statistics reset");
    }
}

// Validation interfaces and base classes
public interface IValidator
{
    bool CanValidate(Type type);
    ValidationResult Validate(object obj, ValidationContext context);
}

public interface IValidator<T> : IValidator
{
    ValidationResult Validate(T obj, ValidationContext context);
}

public abstract class ValidationAttribute : Attribute
{
    public abstract ValidationResult Validate(object value, string propertyName, ValidationContext context);
}

// Common validation attributes
public class RequiredAttribute : ValidationAttribute
{
    public override ValidationResult Validate(object value, string propertyName, ValidationContext context)
    {
        ValidationResult result = ValidationResult.Success();
        
        if (value == null || (value is string str && string.IsNullOrEmpty(str)))
        {
            result.errors.Add(new ValidationError
            {
                message = $"{propertyName} is required",
                propertyName = propertyName,
                level = ValidationLevel.Error
            });
        }
        
        return result;
    }
}

public class RangeAttribute : ValidationAttribute
{
    public float min;
    public float max;
    
    public RangeAttribute(float min, float max)
    {
        this.min = min;
        this.max = max;
    }
    
    public override ValidationResult Validate(object value, string propertyName, ValidationContext context)
    {
        ValidationResult result = ValidationResult.Success();
        
        if (value is IComparable comparable)
        {
            float numValue = Convert.ToSingle(value);
            if (numValue < min || numValue > max)
            {
                result.errors.Add(new ValidationError
                {
                    message = $"{propertyName} must be between {min} and {max}",
                    propertyName = propertyName,
                    level = ValidationLevel.Error
                });
            }
        }
        
        return result;
    }
}

public class MinLengthAttribute : ValidationAttribute
{
    public int minLength;
    
    public MinLengthAttribute(int minLength)
    {
        this.minLength = minLength;
    }
    
    public override ValidationResult Validate(object value, string propertyName, ValidationContext context)
    {
        ValidationResult result = ValidationResult.Success();
        
        if (value is string str && str.Length < minLength)
        {
            result.errors.Add(new ValidationError
            {
                message = $"{propertyName} must be at least {minLength} characters",
                propertyName = propertyName,
                level = ValidationLevel.Error
            });
        }
        
        return result;
    }
}

// Built-in validators
public class PlayerDataValidator : IValidator<PlayerData>
{
    public bool CanValidate(Type type) => type == typeof(PlayerData);
    
    public ValidationResult Validate(object obj, ValidationContext context)
    {
        return Validate((PlayerData)obj, context);
    }
    
    public ValidationResult Validate(PlayerData data, ValidationContext context)
    {
        ValidationResult result = ValidationResult.Success();
        
        if (string.IsNullOrEmpty(data.playerName))
        {
            result.errors.Add(new ValidationError
            {
                message = "Player name cannot be empty",
                propertyName = nameof(data.playerName),
                level = ValidationLevel.Error
            });
        }
        
        if (data.level < 1)
        {
            result.errors.Add(new ValidationError
            {
                message = "Player level must be at least 1",
                propertyName = nameof(data.level),
                level = ValidationLevel.Error
            });
        }
        
        if (data.experience < 0)
        {
            result.errors.Add(new ValidationError
            {
                message = "Experience cannot be negative",
                propertyName = nameof(data.experience),
                level = ValidationLevel.Error
            });
        }
        
        return result;
    }
}

public class GameSettingsValidator : IValidator<GameSettings>
{
    public bool CanValidate(Type type) => type == typeof(GameSettings);
    
    public ValidationResult Validate(object obj, ValidationContext context)
    {
        return Validate((GameSettings)obj, context);
    }
    
    public ValidationResult Validate(GameSettings settings, ValidationContext context)
    {
        ValidationResult result = ValidationResult.Success();
        
        if (settings.musicVolume < 0f || settings.musicVolume > 1f)
        {
            result.errors.Add(new ValidationError
            {
                message = "Music volume must be between 0 and 1",
                propertyName = nameof(settings.musicVolume),
                level = ValidationLevel.Error
            });
        }
        
        if (settings.qualityLevel < 0 || settings.qualityLevel > 5)
        {
            result.errors.Add(new ValidationError
            {
                message = "Quality level must be between 0 and 5",
                propertyName = nameof(settings.qualityLevel),
                level = ValidationLevel.Error
            });
        }
        
        return result;
    }
}

public class SaveDataValidator : IValidator<SaveData>
{
    public bool CanValidate(Type type) => type == typeof(SaveData);
    
    public ValidationResult Validate(object obj, ValidationContext context)
    {
        return Validate((SaveData)obj, context);
    }
    
    public ValidationResult Validate(SaveData data, ValidationContext context)
    {
        ValidationResult result = ValidationResult.Success();
        
        if (data.version <= 0)
        {
            result.errors.Add(new ValidationError
            {
                message = "Save data version must be positive",
                propertyName = nameof(data.version),
                level = ValidationLevel.Error
            });
        }
        
        if (data.timestamp == default(DateTime))
        {
            result.warnings.Add(new ValidationWarning
            {
                message = "Save data timestamp is not set",
                propertyName = nameof(data.timestamp),
                level = ValidationLevel.Warning
            });
        }
        
        return result;
    }
}

public class ItemDataValidator : IValidator<ItemData>
{
    public bool CanValidate(Type type) => type == typeof(ItemData);
    
    public ValidationResult Validate(object obj, ValidationContext context)
    {
        return Validate((ItemData)obj, context);
    }
    
    public ValidationResult Validate(ItemData item, ValidationContext context)
    {
        ValidationResult result = ValidationResult.Success();
        
        if (string.IsNullOrEmpty(item.itemId))
        {
            result.errors.Add(new ValidationError
            {
                message = "Item ID cannot be empty",
                propertyName = nameof(item.itemId),
                level = ValidationLevel.Error
            });
        }
        
        if (item.value < 0)
        {
            result.errors.Add(new ValidationError
            {
                message = "Item value cannot be negative",
                propertyName = nameof(item.value),
                level = ValidationLevel.Error
            });
        }
        
        return result;
    }
}

public class LevelDataValidator : IValidator<LevelData>
{
    public bool CanValidate(Type type) => type == typeof(LevelData);
    
    public ValidationResult Validate(object obj, ValidationContext context)
    {
        return Validate((LevelData)obj, context);
    }
    
    public ValidationResult Validate(LevelData level, ValidationContext context)
    {
        ValidationResult result = ValidationResult.Success();
        
        if (level.levelId < 0)
        {
            result.errors.Add(new ValidationError
            {
                message = "Level ID cannot be negative",
                propertyName = nameof(level.levelId),
                level = ValidationLevel.Error
            });
        }
        
        if (level.difficulty < 1 || level.difficulty > 10)
        {
            result.errors.Add(new ValidationError
            {
                message = "Difficulty must be between 1 and 10",
                propertyName = nameof(level.difficulty),
                level = ValidationLevel.Error
            });
        }
        
        return result;
    }
}

// Data structures
public enum ValidationLevel
{
    Info = 0,
    Warning = 1,
    Error = 2,
    Critical = 3
}

[System.Serializable]
public class ValidationResult
{
    public bool isValid;
    public List<ValidationError> errors;
    public List<ValidationWarning> warnings;
    public float timestamp;
    public string objectType;
    
    public static ValidationResult Success()
    {
        return new ValidationResult
        {
            isValid = true,
            errors = new List<ValidationError>(),
            warnings = new List<ValidationWarning>(),
            timestamp = Time.time
        };
    }
}

[System.Serializable]
public class ValidationError
{
    public string message;
    public string propertyName;
    public ValidationLevel level;
}

[System.Serializable]
public class ValidationWarning
{
    public string message;
    public string propertyName;
    public ValidationLevel level;
}

[System.Serializable]
public class ValidationContext
{
    public object target;
    public Dictionary<string, object> properties = new Dictionary<string, object>();
}

[System.Serializable]
public class ValidationRule
{
    public IValidator validator;
    public Type targetType;
    public ValidationLevel level;
}

[System.Serializable]
public class ValidationStatistics
{
    public int totalValidations;
    public int successfulValidations;
    public int failedValidations;
    public int totalErrors;
    public int totalWarnings;
    public int cacheHits;
}

public class ValidationException : Exception
{
    public ValidationResult Result { get; }
    
    public ValidationException(ValidationResult result) 
        : base($"Validation failed: {result.errors.Count} errors, {result.warnings.Count} warnings")
    {
        Result = result;
    }
}

// Example data classes with validation attributes
[System.Serializable]
public class PlayerData
{
    [Required]
    [MinLength(2)]
    public string playerName;
    
    [Range(1, 100)]
    public int level;
    
    [Range(0, float.MaxValue)]
    public int experience;
    
    public Vector3 position;
}

[System.Serializable]
public class GameSettings
{
    [Range(0f, 1f)]
    public float musicVolume;
    
    [Range(0f, 1f)]
    public float sfxVolume;
    
    [Range(0, 5)]
    public int qualityLevel;
    
    public string language;
}

[System.Serializable]
public class SaveData
{
    [Required]
    public int version;
    
    public DateTime timestamp;
    public PlayerData playerData;
    public GameSettings settings;
}

[System.Serializable]
public class ItemData
{
    [Required]
    public string itemId;
    
    [Required]
    public string itemName;
    
    [Range(0, int.MaxValue)]
    public int value;
    
    public string description;
}

[System.Serializable]
public class LevelData
{
    [Range(0, int.MaxValue)]
    public int levelId;
    
    [Required]
    public string levelName;
    
    [Range(1, 10)]
    public int difficulty;
    
    public float timeLimit;
}
```

## 🚀 AI/LLM Integration
- Automatically generate validation rules from data patterns
- Create intelligent data cleaning and normalization
- Generate custom validation logic for business rules

## 💡 Key Benefits
- Comprehensive data integrity validation
- Automated error detection and correction
- Type-safe data handling with business rule enforcement