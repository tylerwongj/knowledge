# @r-Unity-Advanced-Audio-Implementation

## 🎯 Learning Objectives

- Master Unity's advanced audio systems and real-time processing
- Implement dynamic music systems and adaptive audio
- Create immersive 3D spatial audio experiences
- Build performance-optimized audio streaming and management systems

## 🔧 Core Audio Architecture

### Advanced Audio Manager System

```csharp
using UnityEngine;
using UnityEngine.Audio;
using System.Collections;
using System.Collections.Generic;
using Unity.Collections;
using Unity.Jobs;
using System;

[System.Serializable]
public class AudioEventData
{
    public string eventName;
    public AudioClip[] clips;
    public AudioMixerGroup mixerGroup;
    public float baseVolume = 1f;
    public float basePitch = 1f;
    public float spatialBlend = 0f;
    public float minDistance = 1f;
    public float maxDistance = 500f;
    public AudioRolloffMode rolloffMode = AudioRolloffMode.Logarithmic;
    public bool loop = false;
    public bool randomizePitch = false;
    public Vector2 pitchRange = new Vector2(0.9f, 1.1f);
    public bool randomizeVolume = false;
    public Vector2 volumeRange = new Vector2(0.8f, 1.0f);
}

public class AdvancedAudioManager : MonoBehaviour
{
    [Header("Audio Configuration")]
    [SerializeField] private AudioMixer masterMixer;
    [SerializeField] private AudioEventData[] audioEvents;
    [SerializeField] private int maxAudioSources = 32;
    [SerializeField] private float cullingDistance = 100f;
    
    [Header("Performance Settings")]
    [SerializeField] private bool enableAudioCulling = true;
    [SerializeField] private float cullingUpdateRate = 0.1f;
    [SerializeField] private int priorityThreshold = 128;
    
    // Audio source pooling
    private Queue<AudioSource> availableAudioSources;
    private List<PlayingAudioSource> playingAudioSources;
    private Dictionary<string, AudioEventData> audioEventLookup;
    
    // Spatial audio tracking
    private Transform listenerTransform;
    private Camera mainCamera;
    
    // Performance optimization
    private Coroutine cullingCoroutine;
    private WaitForSeconds cullingWaitTime;
    
    [System.Serializable]
    private class PlayingAudioSource
    {
        public AudioSource source;
        public string eventName;
        public float startTime;
        public bool isLooping;
        public Transform followTarget;
        public Vector3 worldPosition;
        public float priority;
        
        public bool IsFinished => !source.isPlaying && !isLooping;
        public float PlayTime => Time.time - startTime;
    }
    
    void Awake()
    {
        // Initialize singleton pattern
        if (FindObjectsOfType<AdvancedAudioManager>().Length > 1)
        {
            Destroy(gameObject);
            return;
        }
        DontDestroyOnLoad(gameObject);
        
        InitializeAudioSystem();
    }
    
    void InitializeAudioSystem()
    {
        // Setup audio event lookup
        audioEventLookup = new Dictionary<string, AudioEventData>();
        foreach (var audioEvent in audioEvents)
        {
            if (!audioEventLookup.ContainsKey(audioEvent.eventName))
            {
                audioEventLookup[audioEvent.eventName] = audioEvent;
            }
        }
        
        // Initialize audio source pool
        availableAudioSources = new Queue<AudioSource>();
        playingAudioSources = new List<PlayingAudioSource>();
        
        for (int i = 0; i < maxAudioSources; i++)
        {
            GameObject audioObject = new GameObject($"AudioSource_{i:00}");
            audioObject.transform.SetParent(transform);
            
            AudioSource source = audioObject.AddComponent<AudioSource>();
            source.playOnAwake = false;
            source.spatialBlend = 0f; // Default to 2D
            
            availableAudioSources.Enqueue(source);
        }
        
        // Get listener reference
        listenerTransform = FindObjectOfType<AudioListener>()?.transform;
        mainCamera = Camera.main;
        
        // Initialize performance optimization
        cullingWaitTime = new WaitForSeconds(cullingUpdateRate);
        
        if (enableAudioCulling)
        {
            cullingCoroutine = StartCoroutine(AudioCullingUpdate());
        }
    }
    
    public void PlayAudio(string eventName, Vector3 position = default, Transform followTarget = null, float priority = 128f)
    {
        if (!audioEventLookup.TryGetValue(eventName, out AudioEventData eventData))
        {
            Debug.LogWarning($"Audio event '{eventName}' not found!");
            return;
        }
        
        // Check if we should cull this audio based on distance
        if (enableAudioCulling && listenerTransform != null)
        {
            float distanceToListener = Vector3.Distance(position, listenerTransform.position);
            if (distanceToListener > cullingDistance && priority < priorityThreshold)
            {
                return; // Cull distant, low-priority audio
            }
        }
        
        // Get audio source from pool
        AudioSource audioSource = GetAvailableAudioSource(priority);
        if (audioSource == null) return;
        
        // Configure audio source
        SetupAudioSource(audioSource, eventData, position, followTarget);
        
        // Play audio
        audioSource.Play();
        
        // Track playing audio
        var playingAudio = new PlayingAudioSource
        {
            source = audioSource,
            eventName = eventName,
            startTime = Time.time,
            isLooping = eventData.loop,
            followTarget = followTarget,
            worldPosition = position,
            priority = priority
        };
        
        playingAudioSources.Add(playingAudio);
    }
    
    private AudioSource GetAvailableAudioSource(float priority)
    {
        // Try to get from available pool first
        if (availableAudioSources.Count > 0)
        {
            return availableAudioSources.Dequeue();
        }
        
        // Find lowest priority playing source to steal
        PlayingAudioSource lowestPriorityAudio = null;
        float lowestPriority = float.MaxValue;
        
        foreach (var playingAudio in playingAudioSources)
        {
            if (playingAudio.priority < lowestPriority && playingAudio.priority < priority)
            {
                lowestPriority = playingAudio.priority;
                lowestPriorityAudio = playingAudio;
            }
        }
        
        if (lowestPriorityAudio != null)
        {
            // Stop and reclaim the audio source
            lowestPriorityAudio.source.Stop();
            playingAudioSources.Remove(lowestPriorityAudio);
            return lowestPriorityAudio.source;
        }
        
        Debug.LogWarning("No available audio sources!");
        return null;
    }
    
    private void SetupAudioSource(AudioSource source, AudioEventData eventData, Vector3 position, Transform followTarget)
    {
        // Select random clip if multiple available
        AudioClip clipToPlay = eventData.clips[UnityEngine.Random.Range(0, eventData.clips.Length)];
        source.clip = clipToPlay;
        
        // Basic settings
        source.outputAudioMixerGroup = eventData.mixerGroup;
        source.loop = eventData.loop;
        source.spatialBlend = eventData.spatialBlend;
        
        // Volume and pitch with randomization
        float volume = eventData.baseVolume;
        if (eventData.randomizeVolume)
        {
            volume *= UnityEngine.Random.Range(eventData.volumeRange.x, eventData.volumeRange.y);
        }
        source.volume = volume;
        
        float pitch = eventData.basePitch;
        if (eventData.randomizePitch)
        {
            pitch *= UnityEngine.Random.Range(eventData.pitchRange.x, eventData.pitchRange.y);
        }
        source.pitch = pitch;
        
        // 3D audio settings
        if (eventData.spatialBlend > 0f)
        {
            source.minDistance = eventData.minDistance;
            source.maxDistance = eventData.maxDistance;
            source.rolloffMode = eventData.rolloffMode;
            source.dopplerLevel = 1f; // Enable doppler effect for 3D audio
        }
        
        // Position audio source
        if (followTarget != null)
        {
            source.transform.SetParent(followTarget);
            source.transform.localPosition = Vector3.zero;
        }
        else
        {
            source.transform.SetParent(transform);
            source.transform.position = position;
        }
    }
    
    private IEnumerator AudioCullingUpdate()
    {
        while (true)
        {
            yield return cullingWaitTime;
            
            if (listenerTransform == null) continue;
            
            // Update playing audio sources
            for (int i = playingAudioSources.Count - 1; i >= 0; i--)
            {
                var playingAudio = playingAudioSources[i];
                
                // Remove finished audio
                if (playingAudio.IsFinished)
                {
                    ReturnAudioSourceToPool(playingAudio.source);
                    playingAudioSources.RemoveAt(i);
                    continue;
                }
                
                // Update position for following audio
                if (playingAudio.followTarget != null)
                {
                    playingAudio.worldPosition = playingAudio.followTarget.position;
                }
                
                // Distance-based culling
                float distance = Vector3.Distance(playingAudio.worldPosition, listenerTransform.position);
                
                if (distance > cullingDistance)
                {
                    playingAudio.source.volume = 0f; // Mute distant audio
                }
                else
                {
                    // Restore original volume with distance falloff
                    if (audioEventLookup.TryGetValue(playingAudio.eventName, out AudioEventData eventData))
                    {
                        float volumeFalloff = Mathf.Clamp01(1f - (distance / cullingDistance));
                        playingAudio.source.volume = eventData.baseVolume * volumeFalloff;
                    }
                }
            }
        }
    }
    
    private void ReturnAudioSourceToPool(AudioSource source)
    {
        source.Stop();
        source.clip = null;
        source.transform.SetParent(transform);
        source.volume = 1f;
        source.pitch = 1f;
        availableAudioSources.Enqueue(source);
    }
    
    public void StopAudio(string eventName)
    {
        for (int i = playingAudioSources.Count - 1; i >= 0; i--)
        {
            if (playingAudioSources[i].eventName == eventName)
            {
                var playingAudio = playingAudioSources[i];
                ReturnAudioSourceToPool(playingAudio.source);
                playingAudioSources.RemoveAt(i);
            }
        }
    }
    
    public void StopAllAudio()
    {
        foreach (var playingAudio in playingAudioSources)
        {
            ReturnAudioSourceToPool(playingAudio.source);
        }
        playingAudioSources.Clear();
    }
    
    public void SetMasterVolume(float volume)
    {
        masterMixer.SetFloat("MasterVolume", Mathf.Log10(Mathf.Clamp(volume, 0.001f, 1f)) * 20f);
    }
    
    public void SetMixerGroupVolume(string parameterName, float volume)
    {
        masterMixer.SetFloat(parameterName, Mathf.Log10(Mathf.Clamp(volume, 0.001f, 1f)) * 20f);
    }
    
    void OnDestroy()
    {
        if (cullingCoroutine != null)
        {
            StopCoroutine(cullingCoroutine);
        }
    }
}
```

### Dynamic Music System

```csharp
using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using UnityEngine.Audio;

[System.Serializable]
public class MusicTrack
{
    public string trackName;
    public AudioClip introClip;
    public AudioClip loopClip;
    public AudioClip outroClip;
    public float bpm = 120f;
    public int beatsPerMeasure = 4;
    public float fadeInTime = 2f;
    public float fadeOutTime = 2f;
    public AudioMixerGroup mixerGroup;
}

[System.Serializable]
public class MusicState
{
    public string stateName;
    public MusicTrack[] tracks;
    public float crossfadeTime = 4f;
    public bool allowInterruption = true;
    public int priority = 0;
}

public class DynamicMusicSystem : MonoBehaviour
{
    [Header("Music Configuration")]
    [SerializeField] private MusicState[] musicStates;
    [SerializeField] private AudioMixerGroup musicMixerGroup;
    [SerializeField] private float masterVolume = 1f;
    
    [Header("Transition Settings")]
    [SerializeField] private bool quantizeTransitions = true;
    [SerializeField] private float transitionTolerance = 0.1f;
    
    // Current playback state
    private MusicState currentState;
    private MusicTrack currentTrack;
    private AudioSource primaryAudioSource;
    private AudioSource secondaryAudioSource;
    private Dictionary<string, MusicState> musicStateLookup;
    
    // Timing and synchronization
    private double nextEventTime;
    private int flip = 0;
    private bool isTransitioning = false;
    private Coroutine transitionCoroutine;
    
    // Playback tracking
    private double trackStartTime;
    private double currentBeat;
    private int currentMeasure;
    
    public System.Action<string> OnMusicStateChanged;
    public System.Action<float> OnBeatEvent;
    public System.Action<int> OnMeasureEvent;
    
    void Awake()
    {
        InitializeMusicSystem();
    }
    
    void InitializeMusicSystem()
    {
        // Setup music state lookup
        musicStateLookup = new Dictionary<string, MusicState>();
        foreach (var state in musicStates)
        {
            musicStateLookup[state.stateName] = state;
        }
        
        // Create audio sources
        GameObject primarySource = new GameObject("PrimaryMusicSource");
        primarySource.transform.SetParent(transform);
        primaryAudioSource = primarySource.AddComponent<AudioSource>();
        SetupMusicAudioSource(primaryAudioSource);
        
        GameObject secondarySource = new GameObject("SecondaryMusicSource");
        secondarySource.transform.SetParent(transform);
        secondaryAudioSource = secondarySource.AddComponent<AudioSource>();
        SetupMusicAudioSource(secondaryAudioSource);
    }
    
    void SetupMusicAudioSource(AudioSource source)
    {
        source.outputAudioMixerGroup = musicMixerGroup;
        source.loop = false;
        source.playOnAwake = false;
        source.spatialBlend = 0f; // 2D audio
        source.volume = masterVolume;
    }
    
    void Update()
    {
        if (currentTrack != null && primaryAudioSource.isPlaying)
        {
            UpdateMusicTiming();
        }
    }
    
    void UpdateMusicTiming()
    {
        double currentTime = AudioSettings.dspTime;
        double timeSinceStart = currentTime - trackStartTime;
        
        // Calculate current beat and measure
        double beatsPerSecond = currentTrack.bpm / 60.0;
        currentBeat = timeSinceStart * beatsPerSecond;
        currentMeasure = (int)(currentBeat / currentTrack.beatsPerMeasure);
        
        // Check for beat events
        int beatIndex = (int)currentBeat;
        if (beatIndex != (int)((timeSinceStart - Time.unscaledDeltaTime) * beatsPerSecond))
        {
            OnBeatEvent?.Invoke((float)currentBeat);
            
            // Check for measure events
            if (beatIndex % currentTrack.beatsPerMeasure == 0)
            {
                OnMeasureEvent?.Invoke(currentMeasure);
            }
        }
    }
    
    public void TransitionToMusicState(string stateName, bool immediate = false)
    {
        if (!musicStateLookup.TryGetValue(stateName, out MusicState newState))
        {
            Debug.LogWarning($"Music state '{stateName}' not found!");
            return;
        }
        
        // Check if we can interrupt current state
        if (currentState != null && !currentState.allowInterruption && !immediate)
        {
            if (newState.priority <= currentState.priority)
            {
                return; // Cannot interrupt higher priority state
            }
        }
        
        if (transitionCoroutine != null)
        {
            StopCoroutine(transitionCoroutine);
        }
        
        if (immediate || currentState == null)
        {
            transitionCoroutine = StartCoroutine(ImmediateTransition(newState));
        }
        else if (quantizeTransitions)
        {
            transitionCoroutine = StartCoroutine(QuantizedTransition(newState));
        }
        else
        {
            transitionCoroutine = StartCoroutine(CrossfadeTransition(newState));
        }
    }
    
    private IEnumerator ImmediateTransition(MusicState newState)
    {
        StopCurrentMusic();
        
        currentState = newState;
        MusicTrack selectedTrack = SelectRandomTrack(newState);
        
        if (selectedTrack != null)
        {
            yield return StartCoroutine(PlayTrack(selectedTrack, primaryAudioSource));
        }
        
        OnMusicStateChanged?.Invoke(newState.stateName);
        isTransitioning = false;
    }
    
    private IEnumerator QuantizedTransition(MusicState newState)
    {
        isTransitioning = true;
        
        // Wait for next measure boundary
        if (currentTrack != null)
        {
            double currentTime = AudioSettings.dspTime;
            double timeSinceStart = currentTime - trackStartTime;
            double beatsPerSecond = currentTrack.bpm / 60.0;
            double currentBeat = timeSinceStart * beatsPerSecond;
            
            int nextMeasureBeat = ((int)(currentBeat / currentTrack.beatsPerMeasure) + 1) * currentTrack.beatsPerMeasure;
            double timeToNextMeasure = (nextMeasureBeat - currentBeat) / beatsPerSecond;
            
            if (timeToNextMeasure > transitionTolerance)
            {
                yield return new WaitForSecondsRealtime((float)timeToNextMeasure);
            }
        }
        
        yield return StartCoroutine(CrossfadeTransition(newState));
    }
    
    private IEnumerator CrossfadeTransition(MusicState newState)
    {
        isTransitioning = true;
        
        currentState = newState;
        MusicTrack selectedTrack = SelectRandomTrack(newState);
        
        if (selectedTrack == null)
        {
            isTransitioning = false;
            yield break;
        }
        
        // Start new track on secondary source
        AudioSource fadeInSource = secondaryAudioSource;
        AudioSource fadeOutSource = primaryAudioSource;
        
        fadeInSource.volume = 0f;
        yield return StartCoroutine(PlayTrack(selectedTrack, fadeInSource));
        
        // Crossfade
        float crossfadeTime = newState.crossfadeTime;
        float elapsedTime = 0f;
        
        while (elapsedTime < crossfadeTime)
        {
            elapsedTime += Time.unscaledDeltaTime;
            float t = elapsedTime / crossfadeTime;
            
            fadeInSource.volume = Mathf.Lerp(0f, masterVolume, t);
            fadeOutSource.volume = Mathf.Lerp(masterVolume, 0f, t);
            
            yield return null;
        }
        
        // Complete transition
        fadeOutSource.Stop();
        fadeOutSource.volume = masterVolume;
        
        // Swap sources
        AudioSource temp = primaryAudioSource;
        primaryAudioSource = secondaryAudioSource;
        secondaryAudioSource = temp;
        
        OnMusicStateChanged?.Invoke(newState.stateName);
        isTransitioning = false;
    }
    
    private MusicTrack SelectRandomTrack(MusicState state)
    {
        if (state.tracks.Length == 0) return null;
        return state.tracks[Random.Range(0, state.tracks.Length)];
    }
    
    private IEnumerator PlayTrack(MusicTrack track, AudioSource audioSource)
    {
        currentTrack = track;
        
        // Play intro if available
        if (track.introClip != null)
        {
            audioSource.clip = track.introClip;
            trackStartTime = AudioSettings.dspTime;
            audioSource.Play();
            
            yield return new WaitForSecondsRealtime(track.introClip.length);
        }
        
        // Start main loop
        if (track.loopClip != null)
        {
            audioSource.clip = track.loopClip;
            audioSource.loop = true;
            
            if (track.introClip == null)
            {
                trackStartTime = AudioSettings.dspTime;
            }
            
            audioSource.Play();
        }
    }
    
    public void StopMusic(float fadeOutTime = 0f)
    {
        if (transitionCoroutine != null)
        {
            StopCoroutine(transitionCoroutine);
        }
        
        if (fadeOutTime > 0f)
        {
            StartCoroutine(FadeOutMusic(fadeOutTime));
        }
        else
        {
            StopCurrentMusic();
        }
    }
    
    private IEnumerator FadeOutMusic(float fadeTime)
    {
        float startVolume = primaryAudioSource.volume;
        float elapsedTime = 0f;
        
        while (elapsedTime < fadeTime)
        {
            elapsedTime += Time.unscaledDeltaTime;
            float t = elapsedTime / fadeTime;
            
            primaryAudioSource.volume = Mathf.Lerp(startVolume, 0f, t);
            yield return null;
        }
        
        StopCurrentMusic();
        primaryAudioSource.volume = masterVolume;
    }
    
    private void StopCurrentMusic()
    {
        primaryAudioSource.Stop();
        secondaryAudioSource.Stop();
        currentState = null;
        currentTrack = null;
        isTransitioning = false;
    }
    
    public void SetMusicVolume(float volume)
    {
        masterVolume = Mathf.Clamp01(volume);
        primaryAudioSource.volume = masterVolume;
        secondaryAudioSource.volume = masterVolume;
    }
    
    public bool IsPlaying => primaryAudioSource.isPlaying;
    public bool IsTransitioning => isTransitioning;
    public string CurrentStateName => currentState?.stateName;
    public float CurrentBeat => (float)currentBeat;
    public int CurrentMeasure => currentMeasure;
}
```

### Real-time Audio Processing

```csharp
using UnityEngine;
using Unity.Collections;
using Unity.Jobs;

public class RealtimeAudioProcessor : MonoBehaviour
{
    [Header("Audio Analysis")]
    [SerializeField] private int sampleSize = 1024;
    [SerializeField] private float updateRate = 0.1f;
    [SerializeField] private bool enableSpectralAnalysis = true;
    
    [Header("Audio Effects")]
    [SerializeField] private bool enableRealTimeReverb = false;
    [SerializeField] private float reverbDecay = 1.5f;
    [SerializeField] private float reverbMix = 0.3f;
    
    // Audio analysis data
    private float[] audioSamples;
    private float[] spectrumData;
    private NativeArray<float> samplesNative;
    private NativeArray<float> spectrumNative;
    
    // Audio effects
    private CircularBuffer reverbBuffer;
    private float[] reverbDelayLines;
    
    // Performance optimization
    private JobHandle audioProcessingJob;
    
    public float AverageVolume { get; private set; }
    public float[] FrequencyBands { get; private set; }
    public System.Action<float> OnVolumeChanged;
    public System.Action<float[]> OnSpectrumAnalyzed;
    
    void Start()
    {
        InitializeAudioProcessing();
    }
    
    void InitializeAudioProcessing()
    {
        audioSamples = new float[sampleSize];
        spectrumData = new float[sampleSize];
        FrequencyBands = new float[8]; // Standard 8-band EQ
        
        // Initialize native arrays for job system
        samplesNative = new NativeArray<float>(sampleSize, Allocator.Persistent);
        spectrumNative = new NativeArray<float>(sampleSize, Allocator.Persistent);
        
        // Initialize reverb system
        if (enableRealTimeReverb)
        {
            InitializeReverb();
        }
        
        InvokeRepeating(nameof(AnalyzeAudio), 0f, updateRate);
    }
    
    void InitializeReverb()
    {
        int reverbBufferSize = (int)(AudioSettings.outputSampleRate * reverbDecay);
        reverbBuffer = new CircularBuffer(reverbBufferSize);
        
        // Initialize delay lines for multiple reflections
        reverbDelayLines = new float[6]
        {
            0.03f, 0.05f, 0.07f, 0.11f, 0.13f, 0.17f // Delay times in seconds
        };
    }
    
    void AnalyzeAudio()
    {
        // Get audio data from listener
        AudioListener.GetOutputData(audioSamples, 0);
        
        if (enableSpectralAnalysis)
        {
            AudioListener.GetSpectrumData(spectrumData, 0, FFTWindow.Hamming);
        }
        
        // Copy to native arrays for job processing
        samplesNative.CopyFrom(audioSamples);
        if (enableSpectralAnalysis)
        {
            spectrumNative.CopyFrom(spectrumData);
        }
        
        // Schedule audio analysis job
        var analysisJob = new AudioAnalysisJob
        {
            audioSamples = samplesNative,
            spectrumData = spectrumNative,
            enableSpectral = enableSpectralAnalysis
        };
        
        audioProcessingJob = analysisJob.Schedule();
    }
    
    void Update()
    {
        // Complete audio processing job and get results
        if (audioProcessingJob.IsCompleted)
        {
            audioProcessingJob.Complete();
            
            // Calculate average volume
            float volumeSum = 0f;
            for (int i = 0; i < audioSamples.Length; i++)
            {
                volumeSum += Mathf.Abs(audioSamples[i]);
            }
            
            AverageVolume = volumeSum / audioSamples.Length;
            OnVolumeChanged?.Invoke(AverageVolume);
            
            // Calculate frequency bands
            if (enableSpectralAnalysis)
            {
                CalculateFrequencyBands();
                OnSpectrumAnalyzed?.Invoke(FrequencyBands);
            }
        }
    }
    
    void CalculateFrequencyBands()
    {
        // Map spectrum data to 8 frequency bands
        int[] bandLimits = { 2, 4, 8, 16, 32, 64, 128, 256 }; // Sample indices for each band
        int bandIndex = 0;
        int sampleIndex = 0;
        
        for (int i = 0; i < FrequencyBands.Length; i++)
        {
            float bandSum = 0f;
            int sampleCount = 0;
            
            while (sampleIndex < bandLimits[i] && sampleIndex < spectrumData.Length)
            {
                bandSum += spectrumData[sampleIndex];
                sampleCount++;
                sampleIndex++;
            }
            
            FrequencyBands[i] = sampleCount > 0 ? bandSum / sampleCount : 0f;
        }
    }
    
    void OnAudioFilterRead(float[] data, int channels)
    {
        if (!enableRealTimeReverb || reverbBuffer == null) return;
        
        // Apply real-time reverb processing
        for (int i = 0; i < data.Length; i += channels)
        {
            float sample = data[i];
            
            // Add to reverb buffer
            reverbBuffer.Write(sample);
            
            // Calculate reverb output
            float reverbOutput = 0f;
            int sampleRate = AudioSettings.outputSampleRate;
            
            foreach (float delayTime in reverbDelayLines)
            {
                int delaySamples = (int)(delayTime * sampleRate);
                if (delaySamples < reverbBuffer.Size)
                {
                    reverbOutput += reverbBuffer.Read(delaySamples) * 0.3f;
                }
            }
            
            // Apply decay
            reverbOutput *= reverbDecay;
            
            // Mix with original signal
            float processedSample = sample + (reverbOutput * reverbMix);
            
            // Apply to all channels
            for (int channel = 0; channel < channels; channel++)
            {
                data[i + channel] = processedSample;
            }
        }
    }
    
    void OnDestroy()
    {
        if (samplesNative.IsCreated) samplesNative.Dispose();
        if (spectrumNative.IsCreated) spectrumNative.Dispose();
        
        if (audioProcessingJob.IsCompleted == false)
        {
            audioProcessingJob.Complete();
        }
    }
}

[Unity.Burst.BurstCompile]
public struct AudioAnalysisJob : IJob
{
    [ReadOnly] public NativeArray<float> audioSamples;
    [ReadOnly] public NativeArray<float> spectrumData;
    [ReadOnly] public bool enableSpectral;
    
    public void Execute()
    {
        // Perform any additional audio processing here
        // This runs on a background thread with Burst compilation
        
        // Example: Apply noise gate
        for (int i = 0; i < audioSamples.Length; i++)
        {
            if (Mathf.Abs(audioSamples[i]) < 0.01f) // Noise gate threshold
            {
                // audioSamples[i] = 0f; // Note: ReadOnly array, would need WriteOnly version
            }
        }
    }
}

public class CircularBuffer
{
    private float[] buffer;
    private int writeIndex = 0;
    
    public int Size => buffer.Length;
    
    public CircularBuffer(int size)
    {
        buffer = new float[size];
    }
    
    public void Write(float value)
    {
        buffer[writeIndex] = value;
        writeIndex = (writeIndex + 1) % buffer.Length;
    }
    
    public float Read(int samplesBack)
    {
        int readIndex = (writeIndex - samplesBack - 1 + buffer.Length) % buffer.Length;
        return buffer[readIndex];
    }
    
    public void Clear()
    {
        for (int i = 0; i < buffer.Length; i++)
        {
            buffer[i] = 0f;
        }
        writeIndex = 0;
    }
}
```

## 🚀 AI/LLM Integration Opportunities

### Intelligent Audio System Generation

```
Create advanced Unity audio systems:
1. Procedural music composition based on gameplay events
2. Dynamic dialogue system with context-aware responses
3. Adaptive ambient audio that responds to player behavior
4. Real-time audio mixing optimization based on performance metrics

Context: Unity 2022.3 LTS with Audio Mixer and Timeline integration
Focus: Immersive audio experience, performance optimization, scalable architecture
Requirements: Cross-platform compatibility, memory-efficient streaming
```

### Audio Processing Optimization

```
Develop optimized audio processing systems:
1. Multi-threaded audio analysis and effects processing
2. Adaptive quality scaling based on platform capabilities
3. Intelligent audio LOD system for performance optimization
4. Advanced spatial audio with HRTF implementation

Environment: Unity DOTS-compatible audio systems for massive scale
Goals: Real-time performance, minimal latency, high-quality output
```

This comprehensive audio system provides the foundation for creating immersive, performance-optimized audio experiences in Unity games with advanced real-time processing capabilities.