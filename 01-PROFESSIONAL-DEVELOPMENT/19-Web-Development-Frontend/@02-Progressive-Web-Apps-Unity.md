# @02-Progressive Web Apps Unity

## 🎯 Learning Objectives
- Master Progressive Web App development for Unity WebGL games
- Implement offline-first gaming experiences with service workers
- Leverage AI tools for automated PWA optimization and performance monitoring
- Build installable web games with native-like user experiences

## 📱 Unity PWA Architecture

### Service Worker Implementation
**Unity Game Service Worker**:
```javascript
// unity-game-sw.js - Service Worker for Unity WebGL PWA
const CACHE_NAME = 'unity-game-v1.2.0';
const UNITY_CACHE = 'unity-assets-v1.2.0';
const RUNTIME_CACHE = 'runtime-cache-v1.2.0';

// Unity WebGL assets that should be cached
const UNITY_ASSETS = [
  '/Build/WebGL.loader.js',
  '/Build/WebGL.framework.js',
  '/Build/WebGL.wasm',
  '/Build/WebGL.data',
  '/TemplateData/style.css',
  '/TemplateData/UnityProgress.js',
  '/TemplateData/favicon.ico'
];

// Core app shell files
const APP_SHELL = [
  '/',
  '/index.html',
  '/manifest.json',
  '/css/game-styles.css',
  '/js/unity-pwa-manager.js',
  '/images/icon-192.png',
  '/images/icon-512.png',
  '/offline.html'
];

// Install event - cache essential resources
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker installing...');
  
  event.waitUntil(
    Promise.all([
      caches.open(CACHE_NAME).then(cache => {
        console.log('📦 Caching app shell');
        return cache.addAll(APP_SHELL);
      }),
      caches.open(UNITY_CACHE).then(cache => {
        console.log('🎮 Caching Unity assets');
        return cache.addAll(UNITY_ASSETS);
      })
    ]).then(() => {
      console.log('✅ Service Worker installed successfully');
      return self.skipWaiting();
    })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('🚀 Service Worker activating...');
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME && 
              cacheName !== UNITY_CACHE && 
              cacheName !== RUNTIME_CACHE) {
            console.log('🗑️ Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('✅ Service Worker activated');
      return self.clients.claim();
    })
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Handle Unity WebGL assets
  if (isUnityAsset(request.url)) {
    event.respondWith(handleUnityAsset(request));
    return;
  }
  
  // Handle app shell
  if (isAppShellRequest(request)) {
    event.respondWith(handleAppShell(request));
    return;
  }
  
  // Handle API requests
  if (isAPIRequest(request.url)) {
    event.respondWith(handleAPIRequest(request));
    return;
  }
  
  // Handle game data
  if (isGameDataRequest(request.url)) {
    event.respondWith(handleGameData(request));
    return;
  }
  
  // Default: network first, fallback to cache
  event.respondWith(
    fetch(request)
      .then(response => {
        // Cache successful responses
        if (response.ok) {
          const responseClone = response.clone();
          caches.open(RUNTIME_CACHE).then(cache => {
            cache.put(request, responseClone);
          });
        }
        return response;
      })
      .catch(() => {
        return caches.match(request)
          .then(response => response || caches.match('/offline.html'));
      })
  );
});

// Unity asset handling - cache first strategy
async function handleUnityAsset(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      console.log('📦 Serving Unity asset from cache:', request.url);
      return cachedResponse;
    }
    
    // If not in cache, fetch and cache
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(UNITY_CACHE);
      cache.put(request, response.clone());
      console.log('💾 Cached Unity asset:', request.url);
    }
    
    return response;
  } catch (error) {
    console.error('❌ Failed to handle Unity asset:', error);
    throw error;
  }
}

// App shell handling - cache first with network fallback
async function handleAppShell(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      // Update cache in background
      fetch(request).then(response => {
        if (response.ok) {
          caches.open(CACHE_NAME).then(cache => {
            cache.put(request, response.clone());
          });
        }
      }).catch(() => {}); // Ignore background update errors
      
      return cachedResponse;
    }
    
    // Fallback to network
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    // Return offline page for navigation requests
    if (request.mode === 'navigate') {
      return caches.match('/offline.html');
    }
    throw error;
  }
}

// API request handling - network first with cache fallback
async function handleAPIRequest(request) {
  try {
    const response = await fetch(request);
    
    if (response.ok) {
      // Cache successful API responses
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log('🔄 Network failed, trying cache for:', request.url);
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      // Add offline indicator to cached response
      const offlineResponse = cachedResponse.clone();
      offlineResponse.headers.set('X-Served-From', 'cache');
      return offlineResponse;
    }
    
    throw error;
  }
}

// Game data handling - cache with expiration
async function handleGameData(request) {
  const cache = await caches.open(RUNTIME_CACHE);
  const cachedResponse = await cache.match(request);
  
  // Check if cached data is still valid (e.g., 1 hour)
  if (cachedResponse) {
    const cacheTime = new Date(cachedResponse.headers.get('date'));
    const now = new Date();
    const hoursSinceCached = (now - cacheTime) / (1000 * 60 * 60);
    
    if (hoursSinceCached < 1) {
      console.log('📊 Serving fresh game data from cache');
      return cachedResponse;
    }
  }
  
  try {
    const response = await fetch(request);
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    if (cachedResponse) {
      console.log('🔄 Serving stale game data from cache');
      return cachedResponse;
    }
    throw error;
  }
}

// Background sync for game data
self.addEventListener('sync', (event) => {
  if (event.tag === 'game-data-sync') {
    event.waitUntil(syncGameData());
  } else if (event.tag === 'player-stats-sync') {
    event.waitUntil(syncPlayerStats());
  }
});

async function syncGameData() {
  console.log('🔄 Syncing game data in background...');
  
  try {
    // Sync critical game data
    const gameDataResponse = await fetch('/api/game-data');
    if (gameDataResponse.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put('/api/game-data', gameDataResponse.clone());
    }
    
    // Notify clients about successful sync
    const clients = await self.clients.matchAll();
    clients.forEach(client => {
      client.postMessage({
        type: 'SYNC_COMPLETE',
        data: 'Game data synchronized'
      });
    });
    
  } catch (error) {
    console.error('❌ Background sync failed:', error);
  }
}

async function syncPlayerStats() {
  console.log('📊 Syncing player stats...');
  
  try {
    // Get pending player stats from IndexedDB
    const pendingStats = await getPendingPlayerStats();
    
    for (const stat of pendingStats) {
      const response = await fetch('/api/player-stats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(stat)
      });
      
      if (response.ok) {
        await removePendingPlayerStat(stat.id);
      }
    }
    
  } catch (error) {
    console.error('❌ Player stats sync failed:', error);
  }
}

// Push notification handling
self.addEventListener('push', (event) => {
  console.log('📱 Push notification received');
  
  const options = {
    body: 'Check out the latest game updates!',
    icon: '/images/icon-192.png',
    badge: '/images/badge-72.png',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Play Now',
        icon: '/images/play-icon.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/images/close-icon.png'
      }
    ]
  };
  
  if (event.data) {
    const payload = event.data.json();
    options.body = payload.body || options.body;
    options.title = payload.title || 'Unity Game';
  }
  
  event.waitUntil(
    self.registration.showNotification('Unity Game', options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
  console.log('📱 Notification clicked:', event.action);
  
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/?source=notification')
    );
  } else if (event.action === 'close') {
    // Just close the notification
    return;
  } else {
    // Default action
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Utility functions
function isUnityAsset(url) {
  return url.includes('/Build/') || 
         url.includes('/TemplateData/') ||
         url.includes('.wasm') ||
         url.includes('.data');
}

function isAppShellRequest(request) {
  return request.mode === 'navigate' ||
         APP_SHELL.some(url => request.url.endsWith(url));
}

function isAPIRequest(url) {
  return url.includes('/api/');
}

function isGameDataRequest(url) {
  return url.includes('/game-data/') ||
         url.includes('/leaderboard/') ||
         url.includes('/player-stats/');
}

// IndexedDB helpers for offline data storage
async function getPendingPlayerStats() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('UnityGameDB', 1);
    
    request.onsuccess = () => {
      const db = request.result;
      const transaction = db.transaction(['pendingStats'], 'readonly');
      const store = transaction.objectStore('pendingStats');
      const getAllRequest = store.getAll();
      
      getAllRequest.onsuccess = () => resolve(getAllRequest.result);
      getAllRequest.onerror = () => reject(getAllRequest.error);
    };
    
    request.onerror = () => reject(request.error);
  });
}

async function removePendingPlayerStat(id) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('UnityGameDB', 1);
    
    request.onsuccess = () => {
      const db = request.result;
      const transaction = db.transaction(['pendingStats'], 'readwrite');
      const store = transaction.objectStore('pendingStats');
      const deleteRequest = store.delete(id);
      
      deleteRequest.onsuccess = () => resolve();
      deleteRequest.onerror = () => reject(deleteRequest.error);
    };
    
    request.onerror = () => reject(request.error);
  });
}
```

### PWA Manager Implementation
**Unity PWA Manager**:
```csharp
// UnityPWAManager.cs - Unity integration for PWA features
using UnityEngine;
using System.Runtime.InteropServices;
using System.Collections.Generic;
using Newtonsoft.Json;

public class UnityPWAManager : MonoBehaviour
{
    [DllImport("__Internal")]
    private static extern void RegisterServiceWorker();
    
    [DllImport("__Internal")]
    private static extern void RequestNotificationPermission();
    
    [DllImport("__Internal")]
    private static extern void ShowInstallPrompt();
    
    [DllImport("__Internal")]
    private static extern void CacheGameData(string data);
    
    [DllImport("__Internal")]
    private static extern string GetOfflineStatus();
    
    [System.Serializable]
    public class PWAConfig
    {
        public bool enableServiceWorker = true;
        public bool enableNotifications = true;
        public bool enableOfflineMode = true;
        public bool enableBackgroundSync = true;
        public int cacheExpirationHours = 24;
    }
    
    [System.Serializable]
    public class OfflineGameData
    {
        public int playerScore;
        public int playerLevel;
        public float gameProgress;
        public Dictionary<string, object> gameState;
        public System.DateTime lastSaved;
    }
    
    [Header("PWA Configuration")]
    public PWAConfig pwaConfig;
    
    [Header("Offline Game Data")]
    public bool saveGameDataLocally = true;
    public float autoSaveInterval = 30f; // seconds
    
    private bool isOnline = true;
    private bool isPWAInstalled = false;
    private OfflineGameData currentGameData;
    private float lastAutoSaveTime;
    
    private static UnityPWAManager instance;
    public static UnityPWAManager Instance => instance;
    
    // Events
    public System.Action<bool> OnOnlineStatusChanged;
    public System.Action OnPWAInstalled;
    public System.Action<string> OnNotificationReceived;
    
    void Awake()
    {
        if (instance == null)
        {
            instance = this;
            DontDestroyOnLoad(gameObject);
            InitializePWA();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void Start()
    {
        if (Application.platform == RuntimePlatform.WebGLPlayer)
        {
            StartCoroutine(MonitorConnectionStatus());
            
            if (saveGameDataLocally)
            {
                LoadOfflineGameData();
            }
        }
    }
    
    void Update()
    {
        if (saveGameDataLocally && Time.time - lastAutoSaveTime >= autoSaveInterval)
        {
            AutoSaveGameData();
            lastAutoSaveTime = Time.time;
        }
    }
    
    void InitializePWA()
    {
        Debug.Log("🚀 Initializing Unity PWA Manager...");
        
        if (Application.platform == RuntimePlatform.WebGLPlayer)
        {
            if (pwaConfig.enableServiceWorker)
            {
                RegisterServiceWorker();
                Debug.Log("📦 Service Worker registration requested");
            }
            
            if (pwaConfig.enableNotifications)
            {
                RequestNotificationPermission();
                Debug.Log("📱 Notification permission requested");
            }
            
            // Check if PWA is already installed
            CheckPWAInstallStatus();
        }
        
        currentGameData = new OfflineGameData
        {
            gameState = new Dictionary<string, object>(),
            lastSaved = System.DateTime.Now
        };
    }
    
    System.Collections.IEnumerator MonitorConnectionStatus()
    {
        while (true)
        {
            yield return new WaitForSeconds(5f);
            
            bool previousStatus = isOnline;
            string offlineStatus = GetOfflineStatus();
            isOnline = offlineStatus == "online";
            
            if (previousStatus != isOnline)
            {
                Debug.Log(isOnline ? "🌐 Connection restored" : "📵 Connection lost - switching to offline mode");
                OnOnlineStatusChanged?.Invoke(isOnline);
                
                if (isOnline)
                {
                    SyncOfflineData();
                }
            }
        }
    }
    
    void CheckPWAInstallStatus()
    {
        // This would be called from JavaScript
        // For now, we'll simulate it
        isPWAInstalled = false;
    }
    
    public void ShowPWAInstallPrompt()
    {
        if (Application.platform == RuntimePlatform.WebGLPlayer && !isPWAInstalled)
        {
            ShowInstallPrompt();
            Debug.Log("📲 PWA install prompt shown");
        }
    }
    
    public void SaveGameData(int score, int level, float progress, Dictionary<string, object> gameState = null)
    {
        currentGameData.playerScore = score;
        currentGameData.playerLevel = level;
        currentGameData.gameProgress = progress;
        currentGameData.lastSaved = System.DateTime.Now;
        
        if (gameState != null)
        {
            currentGameData.gameState = gameState;
        }
        
        if (Application.platform == RuntimePlatform.WebGLPlayer)
        {
            string jsonData = JsonConvert.SerializeObject(currentGameData);
            CacheGameData(jsonData);
            
            Debug.Log("💾 Game data saved locally");
        }
    }
    
    void AutoSaveGameData()
    {
        // Auto-save current game state
        var gameState = new Dictionary<string, object>
        {
            ["currentScene"] = UnityEngine.SceneManagement.SceneManager.GetActiveScene().name,
            ["gameTime"] = Time.time,
            ["isPaused"] = Time.timeScale == 0f
        };
        
        SaveGameData(currentGameData.playerScore, currentGameData.playerLevel, currentGameData.gameProgress, gameState);
    }
    
    void LoadOfflineGameData()
    {
        // This would load from IndexedDB via JavaScript
        // For now, we'll use PlayerPrefs as fallback
        if (PlayerPrefs.HasKey("OfflineGameData"))
        {
            string jsonData = PlayerPrefs.GetString("OfflineGameData");
            try
            {
                currentGameData = JsonConvert.DeserializeObject<OfflineGameData>(jsonData);
                Debug.Log("📂 Offline game data loaded");
                
                // Apply loaded data to current game
                ApplyOfflineGameData();
            }
            catch (System.Exception e)
            {
                Debug.LogError($"❌ Failed to load offline game data: {e.Message}");
            }
        }
    }
    
    void ApplyOfflineGameData()
    {
        if (currentGameData != null)
        {
            // Apply loaded game data to current game state
            // This would depend on your specific game implementation
            Debug.Log($"📊 Restored game data - Score: {currentGameData.playerScore}, Level: {currentGameData.playerLevel}");
        }
    }
    
    void SyncOfflineData()
    {
        if (!isOnline || currentGameData == null) return;
        
        Debug.Log("🔄 Syncing offline data with server...");
        
        // Implement server sync logic here
        StartCoroutine(SyncWithServer());
    }
    
    System.Collections.IEnumerator SyncWithServer()
    {
        // Create sync request
        var syncData = new Dictionary<string, object>
        {
            ["playerScore"] = currentGameData.playerScore,
            ["playerLevel"] = currentGameData.playerLevel,
            ["gameProgress"] = currentGameData.gameProgress,
            ["lastSaved"] = currentGameData.lastSaved.ToString(),
            ["gameState"] = currentGameData.gameState
        };
        
        string jsonData = JsonConvert.SerializeObject(syncData);
        
        // This would make an actual HTTP request in a real implementation
        yield return new WaitForSeconds(1f); // Simulate network delay
        
        Debug.Log("✅ Data synced successfully");
    }
    
    public void RequestNotification(string title, string body, int delaySeconds = 0)
    {
        if (Application.platform == RuntimePlatform.WebGLPlayer && pwaConfig.enableNotifications)
        {
            StartCoroutine(ShowDelayedNotification(title, body, delaySeconds));
        }
    }
    
    System.Collections.IEnumerator ShowDelayedNotification(string title, string body, int delaySeconds)
    {
        yield return new WaitForSeconds(delaySeconds);
        
        // This would call JavaScript function to show notification
        Debug.Log($"📱 Notification: {title} - {body}");
    }
    
    // Called from JavaScript when PWA is installed
    public void OnPWAInstallComplete()
    {
        isPWAInstalled = true;
        OnPWAInstalled?.Invoke();
        Debug.Log("🎉 PWA installed successfully");
    }
    
    // Called from JavaScript when notification is received
    public void OnNotificationClicked(string notificationData)
    {
        OnNotificationReceived?.Invoke(notificationData);
        Debug.Log($"📱 Notification clicked: {notificationData}");
    }
    
    public bool IsOnline() => isOnline;
    public bool IsPWAInstalled() => isPWAInstalled;
    
    void OnApplicationPause(bool pauseStatus)
    {
        if (pauseStatus && saveGameDataLocally)
        {
            // Save game data when app is paused
            AutoSaveGameData();
        }
    }
    
    void OnApplicationFocus(bool hasFocus)
    {
        if (!hasFocus && saveGameDataLocally)
        {
            // Save game data when app loses focus
            AutoSaveGameData();
        }
    }
}
```

## 🚀 AI Integration Opportunities

### Smart PWA Development
**AI-Enhanced Progressive Web App Creation**:
- Generate optimized service worker strategies based on game content
- Automate offline-first architecture with intelligent caching policies
- Create adaptive loading strategies for different network conditions
- Build intelligent background sync patterns for game data
- Generate performance monitoring and optimization recommendations

### Prompt Templates for PWA Development
```
"Create a service worker configuration for a Unity puzzle game that prioritizes game assets, implements smart caching for player progress, and handles offline gameplay gracefully"

"Generate a PWA manifest and installation flow for a Unity racing game with custom icons, splash screens, and platform-specific optimizations"

"Build an automated testing suite for Unity PWA features including offline functionality, service worker updates, and push notification handling"
```

Progressive Web Apps for Unity games enable native-like experiences on web platforms, providing offline functionality, push notifications, and app-like installation while maintaining cross-platform compatibility.