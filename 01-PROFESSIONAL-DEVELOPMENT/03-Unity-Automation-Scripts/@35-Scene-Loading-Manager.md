# @35-Scene-Loading-Manager

## 🎯 Core Concept
Automated scene loading system with preloading, progress tracking, and seamless transitions.

## 🔧 Implementation

### Scene Loading Framework
```csharp
using UnityEngine;
using UnityEngine.SceneManagement;
using System.Collections;
using System.Collections.Generic;

public class SceneLoadingManager : MonoBehaviour
{
    public static SceneLoadingManager Instance;
    
    [Header("Loading Settings")]
    public GameObject loadingScreenPrefab;
    public float minimumLoadingTime = 1f;
    public bool preloadCommonScenes = true;
    public string[] commonScenes = {"UI", "Audio", "Managers"};
    
    [Header("Transition Settings")]
    public float fadeInDuration = 0.5f;
    public float fadeOutDuration = 0.5f;
    public AnimationCurve fadeCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);
    
    private Dictionary<string, AsyncOperation> preloadedScenes;
    private LoadingScreen currentLoadingScreen;
    private bool isLoading = false;
    
    public System.Action<string> OnSceneLoadStarted;
    public System.Action<string, float> OnSceneLoadProgress;
    public System.Action<string> OnSceneLoadCompleted;
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeSceneLoader();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void InitializeSceneLoader()
    {
        preloadedScenes = new Dictionary<string, AsyncOperation>();
        
        if (preloadCommonScenes)
        {
            StartCoroutine(PreloadCommonScenes());
        }
    }
    
    IEnumerator PreloadCommonScenes()
    {
        foreach (string sceneName in commonScenes)
        {
            if (Application.CanStreamedLevelBeLoaded(sceneName))
            {
                AsyncOperation preloadOperation = SceneManager.LoadSceneAsync(sceneName, LoadSceneMode.Additive);
                preloadOperation.allowSceneActivation = false;
                preloadedScenes[sceneName] = preloadOperation;
                
                Debug.Log($"Preloading scene: {sceneName}");
                yield return null;
            }
        }
        
        Debug.Log("Common scenes preloaded");
    }
    
    public void LoadScene(string sceneName, LoadSceneMode loadMode = LoadSceneMode.Single)
    {
        if (isLoading)
        {
            Debug.LogWarning("Scene loading already in progress");
            return;
        }
        
        StartCoroutine(LoadSceneAsync(sceneName, loadMode));
    }
    
    public void LoadSceneWithTransition(string sceneName, LoadSceneMode loadMode = LoadSceneMode.Single)
    {
        if (isLoading) return;
        
        StartCoroutine(LoadSceneWithTransitionAsync(sceneName, loadMode));
    }
    
    IEnumerator LoadSceneAsync(string sceneName, LoadSceneMode loadMode)
    {
        isLoading = true;
        float startTime = Time.time;
        
        OnSceneLoadStarted?.Invoke(sceneName);
        
        // Show loading screen
        if (loadingScreenPrefab != null)
        {
            GameObject loadingScreenObject = Instantiate(loadingScreenPrefab);
            currentLoadingScreen = loadingScreenObject.GetComponent<LoadingScreen>();
            
            if (currentLoadingScreen != null)
            {
                currentLoadingScreen.Initialize(sceneName);
            }
        }
        
        // Check if scene is preloaded
        AsyncOperation loadOperation;
        if (preloadedScenes.ContainsKey(sceneName))
        {
            loadOperation = preloadedScenes[sceneName];
            preloadedScenes.Remove(sceneName);
        }
        else
        {
            loadOperation = SceneManager.LoadSceneAsync(sceneName, loadMode);
        }
        
        loadOperation.allowSceneActivation = false;
        
        // Monitor loading progress
        while (!loadOperation.isDone)
        {
            float progress = Mathf.Clamp01(loadOperation.progress / 0.9f);
            OnSceneLoadProgress?.Invoke(sceneName, progress);
            
            if (currentLoadingScreen != null)
            {
                currentLoadingScreen.UpdateProgress(progress);
            }
            
            // Check if loading is complete but waiting for activation
            if (loadOperation.progress >= 0.9f)
            {
                // Ensure minimum loading time
                float elapsedTime = Time.time - startTime;
                if (elapsedTime >= minimumLoadingTime)
                {
                    loadOperation.allowSceneActivation = true;
                }
            }
            
            yield return null;
        }
        
        // Scene loading completed
        OnSceneLoadCompleted?.Invoke(sceneName);
        
        // Hide loading screen
        if (currentLoadingScreen != null)
        {
            yield return StartCoroutine(currentLoadingScreen.FadeOut());
            Destroy(currentLoadingScreen.gameObject);
            currentLoadingScreen = null;
        }
        
        isLoading = false;
        
        Debug.Log($"Scene '{sceneName}' loaded successfully");
    }
    
    IEnumerator LoadSceneWithTransitionAsync(string sceneName, LoadSceneMode loadMode)
    {
        isLoading = true;
        
        // Fade out current scene
        yield return StartCoroutine(FadeOut());
        
        // Load new scene
        yield return StartCoroutine(LoadSceneAsync(sceneName, loadMode));
        
        // Fade in new scene
        yield return StartCoroutine(FadeIn());
        
        isLoading = false;
    }
    
    IEnumerator FadeOut()
    {
        ScreenFader fader = ScreenFader.Instance;
        if (fader != null)
        {
            yield return StartCoroutine(fader.FadeToBlack(fadeOutDuration, fadeCurve));
        }
    }
    
    IEnumerator FadeIn()
    {
        ScreenFader fader = ScreenFader.Instance;
        if (fader != null)
        {
            yield return StartCoroutine(fader.FadeFromBlack(fadeInDuration, fadeCurve));
        }
    }
    
    public void UnloadScene(string sceneName)
    {
        if (SceneManager.GetSceneByName(sceneName).isLoaded)
        {
            StartCoroutine(UnloadSceneAsync(sceneName));
        }
    }
    
    IEnumerator UnloadSceneAsync(string sceneName)
    {
        AsyncOperation unloadOperation = SceneManager.UnloadSceneAsync(sceneName);
        
        while (!unloadOperation.isDone)
        {
            yield return null;
        }
        
        // Force garbage collection after unloading
        System.GC.Collect();
        Resources.UnloadUnusedAssets();
        
        Debug.Log($"Scene '{sceneName}' unloaded");
    }
    
    public bool IsSceneLoaded(string sceneName)
    {
        return SceneManager.GetSceneByName(sceneName).isLoaded;
    }
    
    public float GetLoadingProgress()
    {
        return currentLoadingScreen != null ? currentLoadingScreen.CurrentProgress : 0f;
    }
    
    public void RestartCurrentScene()
    {
        string currentSceneName = SceneManager.GetActiveScene().name;
        LoadScene(currentSceneName);
    }
}

public class LoadingScreen : MonoBehaviour
{
    [Header("UI References")]
    public UnityEngine.UI.Slider progressBar;
    public UnityEngine.UI.Text sceneName;
    public UnityEngine.UI.Text progressText;
    public UnityEngine.UI.Image backgroundImage;
    public GameObject[] loadingTips;
    
    [Header("Animation Settings")]
    public float tipRotationInterval = 3f;
    public AnimationCurve fadeInCurve;
    public AnimationCurve fadeOutCurve;
    
    private float currentProgress = 0f;
    private int currentTipIndex = 0;
    private CanvasGroup canvasGroup;
    
    public float CurrentProgress => currentProgress;
    
    void Awake()
    {
        canvasGroup = GetComponent<CanvasGroup>();
        if (canvasGroup == null)
        {
            canvasGroup = gameObject.AddComponent<CanvasGroup>();
        }
    }
    
    public void Initialize(string sceneNameText)
    {
        if (sceneName != null)
        {
            sceneName.text = $"Loading {sceneNameText}...";
        }
        
        currentProgress = 0f;
        UpdateProgressDisplay();
        
        // Start tip rotation
        if (loadingTips != null && loadingTips.Length > 0)
        {
            InvokeRepeating(nameof(RotateLoadingTip), tipRotationInterval, tipRotationInterval);
            ShowLoadingTip(0);
        }
        
        // Fade in
        StartCoroutine(FadeIn());
    }
    
    public void UpdateProgress(float progress)
    {
        currentProgress = Mathf.Clamp01(progress);
        UpdateProgressDisplay();
    }
    
    void UpdateProgressDisplay()
    {
        if (progressBar != null)
        {
            progressBar.value = currentProgress;
        }
        
        if (progressText != null)
        {
            progressText.text = $"{(currentProgress * 100):F0}%";
        }
    }
    
    void RotateLoadingTip()
    {
        if (loadingTips == null || loadingTips.Length == 0) return;
        
        // Hide current tip
        if (currentTipIndex < loadingTips.Length)
        {
            loadingTips[currentTipIndex].SetActive(false);
        }
        
        // Show next tip
        currentTipIndex = (currentTipIndex + 1) % loadingTips.Length;
        ShowLoadingTip(currentTipIndex);
    }
    
    void ShowLoadingTip(int index)
    {
        if (index >= 0 && index < loadingTips.Length)
        {
            loadingTips[index].SetActive(true);
        }
    }
    
    IEnumerator FadeIn()
    {
        float duration = 0.5f;
        float elapsed = 0f;
        
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float progress = elapsed / duration;
            
            if (fadeInCurve != null)
            {
                progress = fadeInCurve.Evaluate(progress);
            }
            
            canvasGroup.alpha = progress;
            yield return null;
        }
        
        canvasGroup.alpha = 1f;
    }
    
    public IEnumerator FadeOut()
    {
        CancelInvoke(nameof(RotateLoadingTip));
        
        float duration = 0.5f;
        float elapsed = 0f;
        
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float progress = 1f - (elapsed / duration);
            
            if (fadeOutCurve != null)
            {
                progress = fadeOutCurve.Evaluate(progress);
            }
            
            canvasGroup.alpha = progress;
            yield return null;
        }
        
        canvasGroup.alpha = 0f;
    }
}

public class ScreenFader : MonoBehaviour
{
    public static ScreenFader Instance;
    
    [Header("Fade Settings")]
    public UnityEngine.UI.Image fadeImage;
    public Color fadeColor = Color.black;
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            
            if (fadeImage == null)
            {
                CreateFadeImage();
            }
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void CreateFadeImage()
    {
        GameObject fadeCanvas = new GameObject("FadeCanvas");
        fadeCanvas.transform.SetParent(transform);
        
        Canvas canvas = fadeCanvas.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvas.sortingOrder = 1000;
        
        GameObject imageObject = new GameObject("FadeImage");
        imageObject.transform.SetParent(fadeCanvas.transform);
        
        fadeImage = imageObject.AddComponent<UnityEngine.UI.Image>();
        fadeImage.color = new Color(fadeColor.r, fadeColor.g, fadeColor.b, 0f);
        
        RectTransform rectTransform = fadeImage.GetComponent<RectTransform>();
        rectTransform.anchorMin = Vector2.zero;
        rectTransform.anchorMax = Vector2.one;
        rectTransform.offsetMin = Vector2.zero;
        rectTransform.offsetMax = Vector2.zero;
    }
    
    public IEnumerator FadeToBlack(float duration, AnimationCurve curve = null)
    {
        yield return StartCoroutine(Fade(0f, 1f, duration, curve));
    }
    
    public IEnumerator FadeFromBlack(float duration, AnimationCurve curve = null)
    {
        yield return StartCoroutine(Fade(1f, 0f, duration, curve));
    }
    
    IEnumerator Fade(float startAlpha, float endAlpha, float duration, AnimationCurve curve)
    {
        if (fadeImage == null) yield break;
        
        float elapsed = 0f;
        
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float progress = elapsed / duration;
            
            if (curve != null)
            {
                progress = curve.Evaluate(progress);
            }
            
            float alpha = Mathf.Lerp(startAlpha, endAlpha, progress);
            fadeImage.color = new Color(fadeColor.r, fadeColor.g, fadeColor.b, alpha);
            
            yield return null;
        }
        
        fadeImage.color = new Color(fadeColor.r, fadeColor.g, fadeColor.b, endAlpha);
    }
}
```

## 🚀 AI/LLM Integration
- Generate loading tips and hints automatically
- Optimize loading order based on usage patterns
- Create adaptive loading strategies

## 💡 Key Benefits
- Seamless scene transitions
- Progress tracking and feedback
- Preloading optimization