# h_Audio-Systems - Unity Audio Engine & Sound Design

## 🎯 Learning Objectives
- Master Unity's audio system and components
- Implement dynamic music and sound effects
- Create spatial 3D audio experiences
- Optimize audio performance and memory usage

## 🔧 Core Audio Components

### Audio Source and Listener
```csharp
// Audio source management
public class AudioManager : MonoBehaviour
{
    [Header("Audio Sources")]
    public AudioSource musicSource;
    public AudioSource sfxSource;
    public AudioSource ambientSource;
    
    [Header("Audio Clips")]
    public AudioClip[] musicTracks;
    public AudioClip[] soundEffects;
    
    private Dictionary<string, AudioClip> audioClips = new Dictionary<string, AudioClip>();
    
    void Start()
    {
        // Initialize audio clips dictionary
        foreach (var clip in soundEffects)
        {
            audioClips[clip.name] = clip;
        }
        
        // Configure audio sources
        musicSource.loop = true;
        musicSource.volume = 0.7f;
        
        sfxSource.loop = false;
        sfxSource.volume = 1f;
    }
    
    public void PlayMusic(int trackIndex)
    {
        if (trackIndex < musicTracks.Length)
        {
            musicSource.clip = musicTracks[trackIndex];
            musicSource.Play();
        }
    }
    
    public void PlaySFX(string clipName, float volume = 1f)
    {
        if (audioClips.ContainsKey(clipName))
        {
            sfxSource.PlayOneShot(audioClips[clipName], volume);
        }
    }
    
    public void PlaySFXAtPosition(string clipName, Vector3 position, float volume = 1f)
    {
        if (audioClips.ContainsKey(clipName))
        {
            AudioSource.PlayClipAtPoint(audioClips[clipName], position, volume);
        }
    }
}
```

### 3D Spatial Audio
```csharp
// 3D audio controller
public class SpatialAudioController : MonoBehaviour
{
    private AudioSource audioSource;
    
    [Header("3D Audio Settings")]
    [Range(0f, 1f)]
    public float spatialBlend = 1f; // 0 = 2D, 1 = 3D
    
    [Range(0f, 5f)]
    public float dopplerLevel = 1f;
    
    public float minDistance = 1f;
    public float maxDistance = 500f;
    
    public AudioRolloffMode rolloffMode = AudioRolloffMode.Logarithmic;
    
    void Start()
    {
        audioSource = GetComponent<AudioSource>();
        ConfigureSpatialAudio();
    }
    
    void ConfigureSpatialAudio()
    {
        audioSource.spatialBlend = spatialBlend;
        audioSource.dopplerLevel = dopplerLevel;
        audioSource.minDistance = minDistance;
        audioSource.maxDistance = maxDistance;
        audioSource.rolloffMode = rolloffMode;
    }
    
    // Distance-based volume control
    void Update()
    {
        if (Camera.main != null)
        {
            float distance = Vector3.Distance(transform.position, Camera.main.transform.position);
            float volumeMultiplier = Mathf.Clamp01(1f - (distance / maxDistance));
            audioSource.volume = volumeMultiplier;
        }
    }
}
```

### Audio Mixer Groups
```csharp
// Audio mixer controller
using UnityEngine.Audio;

public class AudioMixerController : MonoBehaviour
{
    [Header("Audio Mixer")]
    public AudioMixer mainMixer;
    
    [Header("Volume Settings")]
    [Range(-80f, 20f)]
    public float masterVolume = 0f;
    [Range(-80f, 20f)]
    public float musicVolume = 0f;
    [Range(-80f, 20f)]
    public float sfxVolume = 0f;
    
    void Start()
    {
        // Load saved volume settings
        LoadVolumeSettings();
        ApplyVolumeSettings();
    }
    
    public void SetMasterVolume(float volume)
    {
        masterVolume = volume;
        mainMixer.SetFloat("MasterVolume", volume);
        PlayerPrefs.SetFloat("MasterVolume", volume);
    }
    
    public void SetMusicVolume(float volume)
    {
        musicVolume = volume;
        mainMixer.SetFloat("MusicVolume", volume);
        PlayerPrefs.SetFloat("MusicVolume", volume);
    }
    
    public void SetSFXVolume(float volume)
    {
        sfxVolume = volume;
        mainMixer.SetFloat("SFXVolume", volume);
        PlayerPrefs.SetFloat("SFXVolume", volume);
    }
    
    void LoadVolumeSettings()
    {
        masterVolume = PlayerPrefs.GetFloat("MasterVolume", 0f);
        musicVolume = PlayerPrefs.GetFloat("MusicVolume", 0f);
        sfxVolume = PlayerPrefs.GetFloat("SFXVolume", 0f);
    }
    
    void ApplyVolumeSettings()
    {
        mainMixer.SetFloat("MasterVolume", masterVolume);
        mainMixer.SetFloat("MusicVolume", musicVolume);
        mainMixer.SetFloat("SFXVolume", sfxVolume);
    }
}
```

### Dynamic Music System
```csharp
// Adaptive music system
public class DynamicMusicSystem : MonoBehaviour
{
    [Header("Music Tracks")]
    public AudioClip explorationMusic;
    public AudioClip combatMusic;
    public AudioClip victoryMusic;
    
    [Header("Fade Settings")]
    public float fadeTime = 2f;
    
    private AudioSource musicSource;
    private Coroutine fadeCoroutine;
    
    public enum MusicState
    {
        Exploration,
        Combat,
        Victory
    }
    
    private MusicState currentState = MusicState.Exploration;
    
    void Start()
    {
        musicSource = GetComponent<AudioSource>();
        PlayMusic(MusicState.Exploration);
    }
    
    public void TransitionToMusic(MusicState newState)
    {
        if (newState != currentState)
        {
            currentState = newState;
            
            if (fadeCoroutine != null)
                StopCoroutine(fadeCoroutine);
                
            fadeCoroutine = StartCoroutine(FadeToNewMusic(GetMusicClip(newState)));
        }
    }
    
    AudioClip GetMusicClip(MusicState state)
    {
        switch (state)
        {
            case MusicState.Exploration: return explorationMusic;
            case MusicState.Combat: return combatMusic;
            case MusicState.Victory: return victoryMusic;
            default: return explorationMusic;
        }
    }
    
    IEnumerator FadeToNewMusic(AudioClip newClip)
    {
        // Fade out current music
        float startVolume = musicSource.volume;
        
        while (musicSource.volume > 0)
        {
            musicSource.volume -= startVolume * Time.deltaTime / fadeTime;
            yield return null;
        }
        
        // Change clip
        musicSource.clip = newClip;
        musicSource.Play();
        
        // Fade in new music
        while (musicSource.volume < startVolume)
        {
            musicSource.volume += startVolume * Time.deltaTime / fadeTime;
            yield return null;
        }
        
        musicSource.volume = startVolume;
    }
    
    void PlayMusic(MusicState state)
    {
        musicSource.clip = GetMusicClip(state);
        musicSource.Play();
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Audio System Architecture
```
Prompt: "Design a Unity audio system architecture for [game type]. Include audio manager, mixer groups, 3D spatial audio, and dynamic music systems with code examples."

Example: "Design a Unity audio system for an open-world RPG with ambient zones, combat music transitions, UI sounds, and voice-over dialogue management."
```

### Audio Optimization
```
Prompt: "Analyze this Unity audio setup for performance optimization: [paste audio configuration]. Suggest improvements for memory usage, loading times, and CPU performance."
```

### Interactive Audio Design
```
Prompt: "Create Unity scripts for interactive audio elements: [specific requirements]. Include environmental audio triggers, dynamic mixing, and player-responsive sound design."
```

## 🔧 Advanced Audio Features

### Audio Occlusion and Reverb
```csharp
// Audio occlusion system
public class AudioOcclusionSystem : MonoBehaviour
{
    [Header("Occlusion Settings")]
    public LayerMask occlusionLayers = -1;
    public float occlusionUpdateRate = 0.1f;
    public AnimationCurve occlusionCurve = AnimationCurve.Linear(0, 1, 1, 0.1f);
    
    private AudioSource audioSource;
    private AudioLowPassFilter lowPassFilter;
    private float originalVolume;
    
    void Start()
    {
        audioSource = GetComponent<AudioSource>();
        lowPassFilter = GetComponent<AudioLowPassFilter>();
        
        if (lowPassFilter == null)
            lowPassFilter = gameObject.AddComponent<AudioLowPassFilter>();
            
        originalVolume = audioSource.volume;
        
        InvokeRepeating(nameof(UpdateOcclusion), 0f, occlusionUpdateRate);
    }
    
    void UpdateOcclusion()
    {
        if (Camera.main == null) return;
        
        Vector3 listenerPosition = Camera.main.transform.position;
        Vector3 sourcePosition = transform.position;
        Vector3 direction = (sourcePosition - listenerPosition).normalized;
        float distance = Vector3.Distance(listenerPosition, sourcePosition);
        
        // Raycast for occlusion
        if (Physics.Raycast(listenerPosition, direction, out RaycastHit hit, distance, occlusionLayers))
        {
            // Calculate occlusion amount
            float occlusionAmount = hit.distance / distance;
            float volumeMultiplier = occlusionCurve.Evaluate(occlusionAmount);
            
            // Apply occlusion effects
            audioSource.volume = originalVolume * volumeMultiplier;
            lowPassFilter.cutoffFrequency = Mathf.Lerp(500f, 22000f, volumeMultiplier);
        }
        else
        {
            // No occlusion
            audioSource.volume = originalVolume;
            lowPassFilter.cutoffFrequency = 22000f;
        }
    }
}
```

### Audio Pool System
```csharp
// Object pooling for audio sources
public class AudioSourcePool : MonoBehaviour
{
    [Header("Pool Settings")]
    public int poolSize = 10;
    public GameObject audioSourcePrefab;
    
    private Queue<AudioSource> availableSources = new Queue<AudioSource>();
    private List<AudioSource> allSources = new List<AudioSource>();
    
    public static AudioSourcePool Instance { get; private set; }
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializePool();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void InitializePool()
    {
        for (int i = 0; i < poolSize; i++)
        {
            GameObject obj = Instantiate(audioSourcePrefab, transform);
            AudioSource source = obj.GetComponent<AudioSource>();
            
            allSources.Add(source);
            availableSources.Enqueue(source);
            
            obj.SetActive(false);
        }
    }
    
    public AudioSource GetAudioSource()
    {
        if (availableSources.Count > 0)
        {
            AudioSource source = availableSources.Dequeue();
            source.gameObject.SetActive(true);
            return source;
        }
        
        // If pool is empty, create new source temporarily
        GameObject obj = Instantiate(audioSourcePrefab, transform);
        return obj.GetComponent<AudioSource>();
    }
    
    public void ReturnAudioSource(AudioSource source)
    {
        source.Stop();
        source.clip = null;
        source.gameObject.SetActive(false);
        
        if (allSources.Contains(source))
        {
            availableSources.Enqueue(source);
        }
        else
        {
            // Destroy temporary sources
            Destroy(source.gameObject);
        }
    }
    
    // Convenience method for one-shot audio
    public void PlayOneShot(AudioClip clip, Vector3 position, float volume = 1f)
    {
        StartCoroutine(PlayOneShotCoroutine(clip, position, volume));
    }
    
    IEnumerator PlayOneShotCoroutine(AudioClip clip, Vector3 position, float volume)
    {
        AudioSource source = GetAudioSource();
        source.transform.position = position;
        source.volume = volume;
        source.PlayOneShot(clip);
        
        yield return new WaitForSeconds(clip.length);
        
        ReturnAudioSource(source);
    }
}
```

## 💡 Key Highlights

### Essential Audio Concepts
- **Audio Source**: Main component for playing audio clips
- **Audio Listener**: Receives 3D audio (usually on camera)
- **Audio Mixer**: Professional mixing and effects processing
- **Audio Clips**: Compressed audio files (MP3, OGG, WAV)

### 3D Audio Best Practices
- **Spatial Blend**: Use 1.0 for full 3D, 0.0 for UI sounds
- **Rolloff Curves**: Linear for realistic, logarithmic for game feel
- **Doppler Effect**: Subtle values (0.1-1.0) for realism
- **Min/Max Distance**: Set appropriate ranges for your world scale

### Performance Optimization
- **Audio Compression**: Use compressed formats for music, uncompressed for short SFX
- **Audio Loading**: Use "Load in Background" for large files
- **Voice Limiting**: Implement audio source pooling for many simultaneous sounds
- **Memory Management**: Unload unused audio clips to free memory

### Audio Design Patterns
- **Singleton Audio Manager**: Centralized audio control
- **Event-Driven System**: Trigger audio through events
- **State-Based Music**: Dynamic music that responds to gameplay
- **Audio Zones**: Trigger different ambient sounds by location

### Mobile Audio Considerations
- **File Size**: Use lower bitrates and shorter loops
- **Simultaneous Voices**: Limit concurrent audio sources (8-16)
- **Hardware Limitations**: Test on target devices
- **Battery Usage**: Audio processing affects battery life