# @b-Input-Validation-Sanitization - Comprehensive Input Security Framework

## 🎯 Learning Objectives
- Master comprehensive input validation and sanitization techniques for Unity games
- Implement robust defense against injection attacks, malformed data, and malicious input
- Develop automated input validation systems with real-time threat detection
- Create secure input handling frameworks that prevent common attack vectors

## 🛡️ Input Validation Fundamentals

### Core Input Validation Principles
```csharp
namespace UnitySecurityFramework.InputValidation
{
    /// <summary>
    /// Comprehensive input validation system following security best practices
    /// </summary>
    public static class SecureInputValidation
    {
        /// <summary>
        /// Validates input using whitelist approach - only allow known good patterns
        /// </summary>
        public static ValidationResult ValidateWithWhitelist<T>(T input, ValidationRules<T> rules)
        {
            // Null/empty check first
            if (IsNullOrEmpty(input))
            {
                return rules.AllowEmpty 
                    ? ValidationResult.Success() 
                    : ValidationResult.Failure("Input cannot be null or empty");
            }
            
            // Type-specific validation
            var typeValidation = ValidateType(input, rules);
            if (!typeValidation.IsValid)
                return typeValidation;
            
            // Pattern validation (whitelist approach)
            var patternValidation = ValidatePattern(input, rules);
            if (!patternValidation.IsValid)
                return patternValidation;
            
            // Length and size constraints
            var sizeValidation = ValidateSize(input, rules);
            if (!sizeValidation.IsValid)
                return sizeValidation;
            
            // Business logic validation
            var businessValidation = ValidateBusinessRules(input, rules);
            if (!businessValidation.IsValid)
                return businessValidation;
            
            // Security-specific validation
            var securityValidation = ValidateSecurityConstraints(input, rules);
            if (!securityValidation.IsValid)
                return securityValidation;
            
            return ValidationResult.Success();
        }
        
        /// <summary>
        /// Sanitizes input by removing or escaping potentially dangerous content
        /// </summary>
        public static T SanitizeInput<T>(T input, SanitizationRules<T> rules)
        {
            if (IsNullOrEmpty(input))
                return input;
                
            var sanitized = input;
            
            // Apply sanitization rules in order of priority
            foreach (var rule in rules.Rules.OrderBy(r => r.Priority))
            {
                sanitized = rule.Apply(sanitized);
            }
            
            // Final validation after sanitization
            var validationResult = ValidateWithWhitelist(sanitized, rules.ValidationRules);
            if (!validationResult.IsValid)
            {
                throw new SanitizationException($"Input failed validation after sanitization: {validationResult.ErrorMessage}");
            }
            
            return sanitized;
        }
        
        private static ValidationResult ValidateType<T>(T input, ValidationRules<T> rules)
        {
            var inputType = typeof(T);
            
            // Check if type is allowed
            if (!rules.AllowedTypes.Contains(inputType))
            {
                return ValidationResult.Failure($"Type {inputType.Name} is not allowed");
            }
            
            // Type-specific validation
            return inputType.Name switch
            {
                nameof(String) => ValidateStringType(input as string, rules as ValidationRules<string>),
                nameof(Int32) => ValidateIntegerType((int)(object)input, rules as ValidationRules<int>),
                nameof(Single) => ValidateFloatType((float)(object)input, rules as ValidationRules<float>),
                nameof(Vector3) => ValidateVector3Type((Vector3)(object)input, rules as ValidationRules<Vector3>),
                _ => ValidationResult.Success() // Default pass for other types
            };
        }
        
        private static ValidationResult ValidateStringType(string input, ValidationRules<string> rules)
        {
            if (rules == null) return ValidationResult.Success();
            
            // Length validation
            if (input.Length > rules.MaxLength)
                return ValidationResult.Failure($"String exceeds maximum length of {rules.MaxLength}");
                
            if (input.Length < rules.MinLength)
                return ValidationResult.Failure($"String below minimum length of {rules.MinLength}");
            
            // Character set validation (whitelist)
            if (rules.AllowedCharacters != null && !rules.AllowedCharacters.IsMatch(input))
                return ValidationResult.Failure("String contains disallowed characters");
            
            // Encoding validation
            if (!IsValidEncoding(input, rules.RequiredEncoding))
                return ValidationResult.Failure("String contains invalid encoding");
            
            return ValidationResult.Success();
        }
        
        private static ValidationResult ValidatePattern<T>(T input, ValidationRules<T> rules)
        {
            if (rules.RequiredPatterns == null || !rules.RequiredPatterns.Any())
                return ValidationResult.Success();
            
            var inputString = input.ToString();
            
            // All required patterns must match
            foreach (var pattern in rules.RequiredPatterns)
            {
                if (!pattern.IsMatch(inputString))
                {
                    return ValidationResult.Failure($"Input does not match required pattern: {pattern}");
                }
            }
            
            // No forbidden patterns should match
            if (rules.ForbiddenPatterns != null)
            {
                foreach (var pattern in rules.ForbiddenPatterns)
                {
                    if (pattern.IsMatch(inputString))
                    {
                        return ValidationResult.Failure($"Input matches forbidden pattern: {pattern}");
                    }
                }
            }
            
            return ValidationResult.Success();
        }
        
        private static ValidationResult ValidateSecurityConstraints<T>(T input, ValidationRules<T> rules)
        {
            var inputString = input.ToString();
            
            // Check for common injection patterns
            if (ContainsInjectionPatterns(inputString))
                return ValidationResult.Failure("Input contains potential injection patterns");
            
            // Check for script injection
            if (ContainsScriptInjection(inputString))
                return ValidationResult.Failure("Input contains potential script injection");
            
            // Check for path traversal
            if (ContainsPathTraversal(inputString))
                return ValidationResult.Failure("Input contains potential path traversal");
            
            // Check for command injection
            if (ContainsCommandInjection(inputString))
                return ValidationResult.Failure("Input contains potential command injection");
            
            return ValidationResult.Success();
        }
        
        private static bool ContainsInjectionPatterns(string input)
        {
            var injectionPatterns = new[]
            {
                @"('|(\')|;|--|\*|xp_|sp_)",
                @"(\b(ALTER|CREATE|DELETE|DROP|EXEC(UTE){0,1}|INSERT( +INTO){0,1}|MERGE|SELECT|UPDATE|UNION( +ALL){0,1})\b)",
                @"(\b(DECLARE|CAST|CONVERT|CHAR|NCHAR|VARCHAR|NVARCHAR)\b)",
                @"(SCRIPT\b|JAVASCRIPT\b|VBSCRIPT\b|IFRAME\b|OBJECT\b|EMBED\b|FORM\b)",
                @"(<|>|&lt;|&gt;|&quot;|&#x27;|&#x2F;)"
            };
            
            return injectionPatterns.Any(pattern => 
                Regex.IsMatch(input, pattern, RegexOptions.IgnoreCase));
        }
        
        private static bool ContainsScriptInjection(string input)
        {
            var scriptPatterns = new[]
            {
                @"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>",
                @"javascript:",
                @"vbscript:",
                @"data:text\/html",
                @"on\w+\s*=",
                @"expression\s*\(",
                @"eval\s*\(",
                @"setTimeout\s*\(",
                @"setInterval\s*\("
            };
            
            return scriptPatterns.Any(pattern => 
                Regex.IsMatch(input, pattern, RegexOptions.IgnoreCase));
        }
        
        private static bool ContainsPathTraversal(string input)
        {
            var pathTraversalPatterns = new[]
            {
                @"\.\./",
                @"\.\.\\",
                @"%2e%2e%2f",
                @"%2e%2e\\",
                @"\.\.%2f",
                @"\.\.%5c"
            };
            
            return pathTraversalPatterns.Any(pattern => 
                Regex.IsMatch(input, pattern, RegexOptions.IgnoreCase));
        }
        
        private static bool ContainsCommandInjection(string input)
        {
            var commandPatterns = new[]
            {
                @"[;&|`]",
                @"\$\(",
                @"`.*`",
                @"\|\s*\w+",
                @"&&\s*\w+",
                @"\|\|\s*\w+"
            };
            
            return commandPatterns.Any(pattern => 
                Regex.IsMatch(input, pattern, RegexOptions.IgnoreCase));
        }
    }
}
```

### Unity-Specific Input Validation
```csharp
namespace UnitySecurityFramework.InputValidation.Unity
{
    /// <summary>
    /// Unity-specific input validation for game-related data types
    /// </summary>
    public static class UnityInputValidator
    {
        /// <summary>
        /// Validates player movement input to prevent speed hacking and teleportation
        /// </summary>
        public static ValidationResult ValidateMovementInput(MovementInput input, MovementConstraints constraints)
        {
            // Null check
            if (input == null)
                return ValidationResult.Failure("Movement input cannot be null");
            
            // Position validation
            var positionValidation = ValidatePosition(input.Position, constraints);
            if (!positionValidation.IsValid)
                return positionValidation;
            
            // Velocity validation
            var velocityValidation = ValidateVelocity(input.Velocity, constraints);
            if (!velocityValidation.IsValid)
                return velocityValidation;
            
            // Time validation
            var timeValidation = ValidateTimestamp(input.Timestamp, constraints);
            if (!timeValidation.IsValid)
                return timeValidation;
            
            // Physics validation
            var physicsValidation = ValidatePhysicsConsistency(input, constraints);
            if (!physicsValidation.IsValid)
                return physicsValidation;
            
            return ValidationResult.Success();
        }
        
        private static ValidationResult ValidatePosition(Vector3 position, MovementConstraints constraints)
        {
            // Boundary checking
            if (!constraints.AllowedBounds.Contains(position))
                return ValidationResult.Failure("Position is outside allowed game bounds");
            
            // NaN and infinity checking
            if (float.IsNaN(position.x) || float.IsNaN(position.y) || float.IsNaN(position.z))
                return ValidationResult.Failure("Position contains NaN values");
                
            if (float.IsInfinity(position.x) || float.IsInfinity(position.y) || float.IsInfinity(position.z))
                return ValidationResult.Failure("Position contains infinite values");
            
            // Precision validation (prevent floating point exploits)
            if (HasExcessivePrecision(position, constraints.MaxPrecision))
                return ValidationResult.Failure("Position has excessive precision");
            
            return ValidationResult.Success();
        }
        
        private static ValidationResult ValidateVelocity(Vector3 velocity, MovementConstraints constraints)
        {
            var speed = velocity.magnitude;
            
            // Speed limit validation
            if (speed > constraints.MaxSpeed)
                return ValidationResult.Failure($"Speed {speed} exceeds maximum allowed {constraints.MaxSpeed}");
            
            // Acceleration validation
            if (constraints.PreviousVelocity.HasValue)
            {
                var acceleration = (velocity - constraints.PreviousVelocity.Value).magnitude / constraints.TimeDelta;
                if (acceleration > constraints.MaxAcceleration)
                    return ValidationResult.Failure($"Acceleration {acceleration} exceeds maximum allowed {constraints.MaxAcceleration}");
            }
            
            // Direction validation (prevent impossible movement)
            if (speed > 0 && constraints.RestrictedDirections != null)
            {
                var direction = velocity.normalized;
                foreach (var restrictedDirection in constraints.RestrictedDirections)
                {
                    if (Vector3.Dot(direction, restrictedDirection) > 0.9f)
                        return ValidationResult.Failure("Movement in restricted direction");
                }
            }
            
            return ValidationResult.Success();
        }
        
        /// <summary>
        /// Validates player action input to prevent action spamming and impossible actions
        /// </summary>
        public static ValidationResult ValidatePlayerAction(PlayerAction action, ActionConstraints constraints)
        {
            // Basic validation
            if (action == null)
                return ValidationResult.Failure("Player action cannot be null");
            
            // Action type validation
            if (!constraints.AllowedActionTypes.Contains(action.ActionType))
                return ValidationResult.Failure($"Action type {action.ActionType} is not allowed");
            
            // Cooldown validation
            var cooldownValidation = ValidateActionCooldown(action, constraints);
            if (!cooldownValidation.IsValid)
                return cooldownValidation;
            
            // Resource requirements validation
            var resourceValidation = ValidateResourceRequirements(action, constraints);
            if (!resourceValidation.IsValid)
                return resourceValidation;
            
            // Sequence validation (prevent impossible action sequences)
            var sequenceValidation = ValidateActionSequence(action, constraints);
            if (!sequenceValidation.IsValid)
                return sequenceValidation;
            
            return ValidationResult.Success();
        }
        
        private static ValidationResult ValidateActionCooldown(PlayerAction action, ActionConstraints constraints)
        {
            if (!constraints.ActionCooldowns.TryGetValue(action.ActionType, out var cooldownDuration))
                return ValidationResult.Success(); // No cooldown defined
            
            var lastActionTime = constraints.GetLastActionTime(action.ActionType);
            if (lastActionTime.HasValue)
            {
                var timeSinceLastAction = action.Timestamp - lastActionTime.Value;
                if (timeSinceLastAction < cooldownDuration)
                {
                    return ValidationResult.Failure($"Action {action.ActionType} is on cooldown for {cooldownDuration - timeSinceLastAction} more seconds");
                }
            }
            
            return ValidationResult.Success();
        }
        
        /// <summary>
        /// Validates chat messages for profanity, spam, and malicious content
        /// </summary>
        public static ValidationResult ValidateChatMessage(ChatMessage message, ChatConstraints constraints)
        {
            if (message == null)
                return ValidationResult.Failure("Chat message cannot be null");
            
            // Length validation
            if (message.Content.Length > constraints.MaxMessageLength)
                return ValidationResult.Failure($"Message exceeds maximum length of {constraints.MaxMessageLength}");
            
            // Rate limiting validation
            var rateLimitValidation = ValidateMessageRateLimit(message, constraints);
            if (!rateLimitValidation.IsValid)
                return rateLimitValidation;
            
            // Content validation
            var contentValidation = ValidateMessageContent(message.Content, constraints);
            if (!contentValidation.IsValid)
                return contentValidation;
            
            // Spam detection
            var spamValidation = ValidateSpamDetection(message, constraints);
            if (!spamValidation.IsValid)
                return spamValidation;
            
            return ValidationResult.Success();
        }
        
        private static ValidationResult ValidateMessageContent(string content, ChatConstraints constraints)
        {
            // Profanity filtering
            if (constraints.ProfanityFilter.ContainsProfanity(content))
                return ValidationResult.Failure("Message contains inappropriate content");
            
            // URL validation
            if (constraints.BlockUrls && ContainsUrls(content))
                return ValidationResult.Failure("URLs are not allowed in chat messages");
            
            // Personal information detection
            if (ContainsPersonalInformation(content))
                return ValidationResult.Failure("Message appears to contain personal information");
            
            // Advertising detection
            if (ContainsAdvertising(content, constraints))
                return ValidationResult.Failure("Message appears to contain advertising");
            
            return ValidationResult.Success();
        }
        
        private static bool ContainsUrls(string content)
        {
            var urlPattern = @"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)";
            return Regex.IsMatch(content, urlPattern, RegexOptions.IgnoreCase);
        }
        
        private static bool ContainsPersonalInformation(string content)
        {
            var personalInfoPatterns = new[]
            {
                @"\b\d{3}-\d{2}-\d{4}\b", // SSN pattern
                @"\b\d{3}-\d{3}-\d{4}\b", // Phone number pattern
                @"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", // Email pattern
                @"\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b" // Credit card pattern
            };
            
            return personalInfoPatterns.Any(pattern => 
                Regex.IsMatch(content, pattern, RegexOptions.IgnoreCase));
        }
        
        /// <summary>
        /// Validates file upload input to prevent malicious file uploads
        /// </summary>
        public static ValidationResult ValidateFileUpload(FileUploadInput fileInput, FileUploadConstraints constraints)
        {
            if (fileInput == null)
                return ValidationResult.Failure("File upload input cannot be null");
            
            // File size validation
            if (fileInput.FileSize > constraints.MaxFileSize)
                return ValidationResult.Failure($"File size {fileInput.FileSize} exceeds maximum allowed {constraints.MaxFileSize}");
            
            // File type validation
            var fileTypeValidation = ValidateFileType(fileInput, constraints);
            if (!fileTypeValidation.IsValid)
                return fileTypeValidation;
            
            // File name validation
            var fileNameValidation = ValidateFileName(fileInput.FileName, constraints);
            if (!fileNameValidation.IsValid)
                return fileNameValidation;
            
            // File content validation
            var contentValidation = ValidateFileContent(fileInput, constraints);
            if (!contentValidation.IsValid)
                return contentValidation;
            
            return ValidationResult.Success();
        }
        
        private static ValidationResult ValidateFileType(FileUploadInput fileInput, FileUploadConstraints constraints)
        {
            // Extension validation
            var extension = Path.GetExtension(fileInput.FileName).ToLowerInvariant();
            if (!constraints.AllowedExtensions.Contains(extension))
                return ValidationResult.Failure($"File extension {extension} is not allowed");
            
            // MIME type validation
            if (!constraints.AllowedMimeTypes.Contains(fileInput.MimeType))
                return ValidationResult.Failure($"MIME type {fileInput.MimeType} is not allowed");
            
            // Magic number validation (file header signature)
            var magicNumberValidation = ValidateFileMagicNumber(fileInput, constraints);
            if (!magicNumberValidation.IsValid)
                return magicNumberValidation;
            
            return ValidationResult.Success();
        }
        
        private static ValidationResult ValidateFileMagicNumber(FileUploadInput fileInput, FileUploadConstraints constraints)
        {
            if (fileInput.FileData == null || fileInput.FileData.Length < 4)
                return ValidationResult.Failure("File data is too small to validate");
            
            var fileHeader = fileInput.FileData.Take(16).ToArray();
            var extension = Path.GetExtension(fileInput.FileName).ToLowerInvariant();
            
            // Check if file header matches expected signature for file type
            return extension switch
            {
                ".png" => ValidatePngHeader(fileHeader),
                ".jpg" or ".jpeg" => ValidateJpegHeader(fileHeader),
                ".gif" => ValidateGifHeader(fileHeader),
                ".pdf" => ValidatePdfHeader(fileHeader),
                ".txt" => ValidationResult.Success(), // Text files don't have magic numbers
                _ => ValidationResult.Failure($"Unknown file type validation for {extension}")
            };
        }
        
        private static ValidationResult ValidatePngHeader(byte[] header)
        {
            var pngSignature = new byte[] { 0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A };
            
            if (header.Length < pngSignature.Length)
                return ValidationResult.Failure("File header too short for PNG validation");
            
            for (int i = 0; i < pngSignature.Length; i++)
            {
                if (header[i] != pngSignature[i])
                    return ValidationResult.Failure("File header does not match PNG signature");
            }
            
            return ValidationResult.Success();
        }
        
        private static ValidationResult ValidateJpegHeader(byte[] header)
        {
            if (header.Length < 3)
                return ValidationResult.Failure("File header too short for JPEG validation");
            
            if (header[0] != 0xFF || header[1] != 0xD8 || header[2] != 0xFF)
                return ValidationResult.Failure("File header does not match JPEG signature");
            
            return ValidationResult.Success();
        }
    }
}
```

## 🚀 AI/LLM Integration for Advanced Input Security

### AI-Powered Input Analysis
```csharp
input_security_ai_prompts = {
    'suspicious_input_analysis': """
    Analyze this potentially suspicious input for security threats:
    
    Input Details:
    - Input type: {input_type}
    - Input value: {input_value}
    - Source: {input_source}
    - Context: {input_context}
    - User information: {user_info}
    
    Previous Patterns:
    - Similar inputs from this user: {user_input_history}
    - Recent suspicious activities: {recent_suspicious_activities}
    - Known attack patterns: {known_attack_patterns}
    
    Analyze for:
    1. Injection attack attempts (SQL, XSS, command injection)
    2. Buffer overflow or memory corruption attempts
    3. Social engineering or phishing content
    4. Automated/bot-like input patterns
    5. Unusual encoding or obfuscation techniques
    6. Rate limiting violations or spam indicators
    
    Provide:
    - Threat level assessment (Critical, High, Medium, Low, None)
    - Specific attack vector identification
    - Confidence level in the assessment
    - Recommended actions (block, sanitize, monitor, allow)
    - Suggested additional monitoring or logging
    """,
    
    'input_pattern_learning': """
    Learn and improve input validation from this dataset:
    
    Input Dataset:
    - Legitimate inputs: {legitimate_inputs}
    - Malicious inputs: {malicious_inputs}
    - Edge cases: {edge_cases}
    - False positives: {false_positives}
    - False negatives: {false_negatives}
    
    Current Validation Rules:
    - Whitelist patterns: {current_whitelist}
    - Blacklist patterns: {current_blacklist}
    - Length constraints: {length_constraints}
    - Type constraints: {type_constraints}
    
    Analyze and recommend:
    1. New whitelist patterns to allow legitimate edge cases
    2. Additional blacklist patterns to catch new threats
    3. Constraint adjustments to reduce false positives
    4. Security rule improvements to catch false negatives
    5. Priority order for implementing changes
    6. Risk assessment for each recommended change
    """,
    
    'input_sanitization_optimization': """
    Optimize input sanitization strategy for this application:
    
    Application Context:
    - Application type: {app_type}
    - User base: {user_demographics}
    - Threat landscape: {threat_environment}
    - Performance requirements: {performance_constraints}
    - Compliance requirements: {compliance_needs}
    
    Current Sanitization:
    - Methods used: {current_sanitization_methods}
    - Performance impact: {performance_metrics}
    - Effectiveness metrics: {effectiveness_data}
    - User experience impact: {ux_impact}
    
    Optimize for:
    1. Balance between security and usability
    2. Performance optimization while maintaining security
    3. Contextual sanitization based on input purpose
    4. Multi-layer sanitization strategy
    5. Real-time threat adaptation
    6. Minimal false positive generation
    """
}
```

### Real-Time Input Monitoring System
```csharp
namespace UnitySecurityFramework.InputValidation.Monitoring
{
    /// <summary>
    /// Real-time input monitoring and threat detection system
    /// </summary>
    public class InputSecurityMonitor : MonoBehaviour
    {
        [SerializeField] private InputSecurityConfig _config;
        private readonly Dictionary<string, PlayerInputProfile> _playerProfiles = new Dictionary<string, PlayerInputProfile>();
        private readonly Queue<InputSecurityEvent> _securityEvents = new Queue<InputSecurityEvent>();
        private readonly IInputSecurityAnalyzer _aiAnalyzer;
        
        private void Start()
        {
            StartCoroutine(ProcessSecurityEvents());
            StartCoroutine(UpdatePlayerProfiles());
        }
        
        public ValidationResult ValidateAndMonitorInput<T>(string playerId, T input, string inputContext)
        {
            // Get or create player profile
            if (!_playerProfiles.TryGetValue(playerId, out var profile))
            {
                profile = new PlayerInputProfile(playerId);
                _playerProfiles[playerId] = profile;
            }
            
            // Basic validation first
            var basicValidation = PerformBasicValidation(input, inputContext);
            if (!basicValidation.IsValid)
            {
                RecordSecurityEvent(playerId, SecurityEventType.ValidationFailure, input, basicValidation.ErrorMessage);
                return basicValidation;
            }
            
            // Behavioral analysis
            var behavioralValidation = AnalyzeBehavioralPatterns(playerId, input, inputContext, profile);
            if (!behavioralValidation.IsValid)
            {
                RecordSecurityEvent(playerId, SecurityEventType.SuspiciousBehavior, input, behavioralValidation.ErrorMessage);
                return behavioralValidation;
            }
            
            // AI-enhanced threat detection
            var aiValidation = PerformAIThreatDetection(playerId, input, inputContext, profile);
            if (!aiValidation.IsValid)
            {
                RecordSecurityEvent(playerId, SecurityEventType.AIDetectedThreat, input, aiValidation.ErrorMessage);
                return aiValidation;
            }
            
            // Update player profile with successful input
            profile.RecordSuccessfulInput(input, inputContext);
            
            return ValidationResult.Success();
        }
        
        private ValidationResult AnalyzeBehavioralPatterns<T>(string playerId, T input, string context, PlayerInputProfile profile)
        {
            // Rate limiting analysis
            var rateLimit = AnalyzeInputRate(profile, context);
            if (!rateLimit.IsValid)
                return rateLimit;
            
            // Pattern deviation analysis
            var patternAnalysis = AnalyzeInputPatterns(profile, input, context);
            if (!patternAnalysis.IsValid)
                return patternAnalysis;
            
            // Timing analysis (detect bots)
            var timingAnalysis = AnalyzeInputTiming(profile, context);
            if (!timingAnalysis.IsValid)
                return timingAnalysis;
            
            // Sequence analysis
            var sequenceAnalysis = AnalyzeInputSequence(profile, input, context);
            if (!sequenceAnalysis.IsValid)
                return sequenceAnalysis;
            
            return ValidationResult.Success();
        }
        
        private ValidationResult AnalyzeInputRate(PlayerInputProfile profile, string context)
        {
            var recentInputs = profile.GetRecentInputs(TimeSpan.FromMinutes(1), context);
            var inputRate = recentInputs.Count();
            
            var maxRate = _config.GetMaxInputRate(context);
            if (inputRate > maxRate)
            {
                return ValidationResult.Failure($"Input rate {inputRate} exceeds maximum {maxRate} for context {context}");
            }
            
            // Check for burst patterns (many inputs in short time)
            var burstInputs = profile.GetRecentInputs(TimeSpan.FromSeconds(5), context);
            var burstRate = burstInputs.Count();
            var maxBurstRate = _config.GetMaxBurstRate(context);
            
            if (burstRate > maxBurstRate)
            {
                return ValidationResult.Failure($"Burst input rate {burstRate} exceeds maximum {maxBurstRate}");
            }
            
            return ValidationResult.Success();
        }
        
        private ValidationResult AnalyzeInputPatterns<T>(PlayerInputProfile profile, T input, string context)
        {
            // Check for repetitive patterns (possible automation)
            if (IsRepetitivePattern(profile, input, context))
            {
                return ValidationResult.Failure("Repetitive input pattern detected - possible automation");
            }
            
            // Check for abnormal input diversity
            if (IsAbnormalInputDiversity(profile, input, context))
            {
                return ValidationResult.Failure("Abnormal input diversity pattern detected");
            }
            
            // Check for input complexity (too simple or too complex)
            if (IsAbnormalInputComplexity(input, context))
            {
                return ValidationResult.Failure("Abnormal input complexity detected");
            }
            
            return ValidationResult.Success();
        }
        
        private ValidationResult AnalyzeInputTiming(PlayerInputProfile profile, string context)
        {
            var recentTimings = profile.GetRecentInputTimings(context, 10);
            
            if (recentTimings.Count < 3)
                return ValidationResult.Success(); // Not enough data
            
            // Calculate timing statistics
            var intervals = recentTimings.Zip(recentTimings.Skip(1), (a, b) => (b - a).TotalMilliseconds).ToList();
            var averageInterval = intervals.Average();
            var standardDeviation = CalculateStandardDeviation(intervals);
            
            // Very consistent timing might indicate automation
            if (standardDeviation < 50 && averageInterval < 1000) // Less than 50ms deviation with sub-second intervals
            {
                return ValidationResult.Failure("Suspiciously consistent input timing - possible automation");
            }
            
            // Extremely fast input might indicate automation
            if (averageInterval < 100) // Less than 100ms between inputs
            {
                return ValidationResult.Failure("Suspiciously fast input timing - possible automation");
            }
            
            return ValidationResult.Success();
        }
        
        private IEnumerator ProcessSecurityEvents()
        {
            while (true)
            {
                while (_securityEvents.Count > 0)
                {
                    var securityEvent = _securityEvents.Dequeue();
                    yield return StartCoroutine(HandleSecurityEvent(securityEvent));
                }
                yield return new WaitForSeconds(0.1f);
            }
        }
        
        private IEnumerator HandleSecurityEvent(InputSecurityEvent securityEvent)
        {
            // Log the event
            Debug.LogWarning($"Input Security Event: {securityEvent.EventType} for player {securityEvent.PlayerId}: {securityEvent.Description}");
            
            // Update player risk score
            if (_playerProfiles.TryGetValue(securityEvent.PlayerId, out var profile))
            {
                profile.IncreaseRiskScore(securityEvent.EventType);
            }
            
            // Take action based on event severity
            switch (securityEvent.EventType)
            {
                case SecurityEventType.ValidationFailure:
                    // Minor issue - just log
                    break;
                case SecurityEventType.SuspiciousBehavior:
                    // Moderate issue - increase monitoring
                    IncreasePlayerMonitoring(securityEvent.PlayerId);
                    break;
                case SecurityEventType.AIDetectedThreat:
                    // Serious issue - consider temporary restrictions
                    yield return StartCoroutine(ApplyTemporaryRestrictions(securityEvent.PlayerId));
                    break;
            }
        }
        
        private void RecordSecurityEvent<T>(string playerId, SecurityEventType eventType, T input, string description)
        {
            var securityEvent = new InputSecurityEvent
            {
                PlayerId = playerId,
                EventType = eventType,
                Input = input?.ToString(),
                Description = description,
                Timestamp = DateTime.UtcNow
            };
            
            _securityEvents.Enqueue(securityEvent);
        }
        
        private double CalculateStandardDeviation(List<double> values)
        {
            if (values.Count < 2) return 0;
            
            var average = values.Average();
            var sumOfSquaresOfDifferences = values.Select(val => (val - average) * (val - average)).Sum();
            return Math.Sqrt(sumOfSquaresOfDifferences / values.Count);
        }
    }
}
```

## 💡 Implementation Best Practices

### Input Validation Checklist
```yaml
Input_Validation_Checklist:
  Basic_Validation:
    - "Validate all inputs at system boundaries"
    - "Use whitelist validation approach whenever possible"
    - "Implement proper length and size constraints"
    - "Validate data types and formats strictly"
    - "Check for null, empty, and undefined values"
    
  Security_Validation:
    - "Scan for injection attack patterns"
    - "Validate encoding and character sets"
    - "Check for path traversal attempts"
    - "Detect script injection patterns"
    - "Validate file uploads thoroughly"
    
  Business_Logic_Validation:
    - "Implement domain-specific validation rules"
    - "Validate business constraints and workflows"
    - "Check for logical consistency"
    - "Validate state transitions"
    - "Implement proper authorization checks"
    
  Performance_Validation:
    - "Implement rate limiting and throttling"
    - "Validate resource consumption limits"
    - "Check for denial of service patterns"
    - "Monitor validation performance impact"
    - "Implement caching for expensive validations"
```

This comprehensive input validation and sanitization system provides robust protection against injection attacks, malformed data, and malicious input while maintaining usability and performance for Unity game development.