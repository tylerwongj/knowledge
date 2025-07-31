# @01-React Unity Integration

## 🎯 Learning Objectives
- Master React integration with Unity WebGL for hybrid game applications
- Develop responsive web interfaces that communicate with Unity runtime
- Leverage AI tools for automated React-Unity development workflows
- Build scalable front-end architectures for Unity web games

## ⚛️ React-Unity Communication Bridge

### Core Integration Framework
**Unity WebGL React Communication**:
```csharp
// UnityReactBridge.cs - Bridge for React-Unity communication
using UnityEngine;
using System.Runtime.InteropServices;
using System.Collections.Generic;
using Newtonsoft.Json;

public class UnityReactBridge : MonoBehaviour
{
    // JavaScript interface functions
    [DllImport("__Internal")]
    private static extern void SendToReact(string eventType, string data);
    
    [DllImport("__Internal")]
    private static extern void RequestReactData(string requestType);
    
    [System.Serializable]
    public class GameEvent
    {
        public string eventType;
        public string data;
        public float timestamp;
    }
    
    [System.Serializable]
    public class PlayerStats
    {
        public string playerName;
        public int score;
        public int level;
        public float progress;
        public Dictionary<string, object> achievements;
    }
    
    private static UnityReactBridge instance;
    public static UnityReactBridge Instance => instance;
    
    [Header("Bridge Configuration")]
    public bool enableDebugLogging = true;
    public float communicationTimeout = 5f;
    
    private Queue<GameEvent> eventQueue = new Queue<GameEvent>();
    private PlayerStats currentPlayerStats;
    
    void Awake()
    {
        if (instance == null)
        {
            instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeBridge();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void InitializeBridge()
    {
        Debug.Log("🌉 Initializing Unity-React Bridge...");
        
        // Initialize player stats
        currentPlayerStats = new PlayerStats
        {
            playerName = "Player",
            score = 0,
            level = 1,
            progress = 0f,
            achievements = new Dictionary<string, object>()
        };
        
        // Notify React that Unity is ready
        SendGameEvent("unity_ready", "Unity WebGL loaded successfully");
    }
    
    // Called from React via JavaScript
    public void ReceiveFromReact(string jsonData)
    {
        try
        {
            var eventData = JsonConvert.DeserializeObject<GameEvent>(jsonData);
            ProcessReactEvent(eventData);
            
            if (enableDebugLogging)
            {
                Debug.Log($"📨 Received from React: {eventData.eventType}");
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError($"❌ Failed to parse React data: {e.Message}");
        }
    }
    
    void ProcessReactEvent(GameEvent eventData)
    {
        switch (eventData.eventType)
        {
            case "player_name_changed":
                UpdatePlayerName(eventData.data);
                break;
                
            case "game_settings_updated":
                UpdateGameSettings(eventData.data);
                break;
                
            case "ui_action":
                ProcessUIAction(eventData.data);
                break;
                
            case "request_game_state":
                SendGameState();
                break;
                
            default:
                Debug.LogWarning($"⚠️ Unhandled React event: {eventData.eventType}");
                break;
        }
    }
    
    void UpdatePlayerName(string newName)
    {
        currentPlayerStats.playerName = newName;
        Debug.Log($"👤 Player name updated to: {newName}");
        
        // Notify game systems of name change
        var nameChangeEvent = new GameEvent
        {
            eventType = "player_name_updated",
            data = newName,
            timestamp = Time.time
        };
        
        BroadcastToGameSystems(nameChangeEvent);
    }
    
    void UpdateGameSettings(string settingsJson)
    {
        try
        {
            var settings = JsonConvert.DeserializeObject<Dictionary<string, object>>(settingsJson);
            
            foreach (var setting in settings)
            {
                ApplyGameSetting(setting.Key, setting.Value);
            }
            
            SendGameEvent("settings_applied", "Game settings updated successfully");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"❌ Failed to apply game settings: {e.Message}");
        }
    }
    
    void ApplyGameSetting(string key, object value)
    {
        switch (key)
        {
            case "volume":
                AudioListener.volume = System.Convert.ToSingle(value);
                break;
                
            case "quality":
                int qualityLevel = System.Convert.ToInt32(value);
                QualitySettings.SetQualityLevel(qualityLevel);
                break;
                
            case "fullscreen":
                bool isFullscreen = System.Convert.ToBoolean(value);
                Screen.fullScreen = isFullscreen;
                break;
                
            default:
                Debug.LogWarning($"⚠️ Unknown game setting: {key}");
                break;
        }
    }
    
    void ProcessUIAction(string actionData)
    {
        var actionInfo = JsonConvert.DeserializeObject<Dictionary<string, string>>(actionData);
        
        if (actionInfo.ContainsKey("action"))
        {
            string action = actionInfo["action"];
            
            switch (action)
            {
                case "pause_game":
                    PauseGame();
                    break;
                    
                case "resume_game":
                    ResumeGame();
                    break;
                    
                case "restart_game":
                    RestartGame();
                    break;
                    
                case "show_leaderboard":
                    ShowLeaderboard();
                    break;
                    
                default:
                    Debug.LogWarning($"⚠️ Unknown UI action: {action}");
                    break;
            }
        }
    }
    
    public void SendGameEvent(string eventType, string data)
    {
        if (Application.platform == RuntimePlatform.WebGLPlayer)
        {
            var gameEvent = new GameEvent
            {
                eventType = eventType,
                data = data,
                timestamp = Time.time
            };
            
            string jsonData = JsonConvert.SerializeObject(gameEvent);
            SendToReact(eventType, jsonData);
            
            if (enableDebugLogging)
            {
                Debug.Log($"📤 Sent to React: {eventType}");
            }
        }
    }
    
    public void UpdateScore(int newScore)
    {
        currentPlayerStats.score = newScore;
        SendPlayerStats();
    }
    
    public void UpdateLevel(int newLevel)
    {
        currentPlayerStats.level = newLevel;
        SendPlayerStats();
    }
    
    public void UpdateProgress(float newProgress)
    {
        currentPlayerStats.progress = Mathf.Clamp01(newProgress);
        SendPlayerStats();
    }
    
    void SendPlayerStats()
    {
        string statsJson = JsonConvert.SerializeObject(currentPlayerStats);
        SendGameEvent("player_stats_updated", statsJson);
    }
    
    void SendGameState()
    {
        var gameState = new Dictionary<string, object>
        {
            ["isPlaying"] = !IsPaused(),
            ["currentScene"] = UnityEngine.SceneManagement.SceneManager.GetActiveScene().name,
            ["playerStats"] = currentPlayerStats,
            ["gameTime"] = Time.time,
            ["frameRate"] = Application.targetFrameRate
        };
        
        string stateJson = JsonConvert.SerializeObject(gameState);
        SendGameEvent("game_state_response", stateJson);
    }
    
    void PauseGame()
    {
        Time.timeScale = 0f;
        SendGameEvent("game_paused", "Game paused by UI");
    }
    
    void ResumeGame()
    {
        Time.timeScale = 1f;
        SendGameEvent("game_resumed", "Game resumed by UI");
    }
    
    void RestartGame()
    {
        Time.timeScale = 1f;
        UnityEngine.SceneManagement.SceneManager.LoadScene(0);
        SendGameEvent("game_restarted", "Game restarted");
    }
    
    void ShowLeaderboard()
    {
        // Request leaderboard data from React
        RequestReactData("leaderboard");
    }
    
    bool IsPaused()
    {
        return Mathf.Approximately(Time.timeScale, 0f);
    }
    
    void BroadcastToGameSystems(GameEvent gameEvent)
    {
        // Broadcast to all game systems that need to respond to events
        var eventSystemComponents = FindObjectsOfType<MonoBehaviour>()
            .Where(mb => mb is IGameEventHandler)
            .Cast<IGameEventHandler>();
        
        foreach (var handler in eventSystemComponents)
        {
            handler.HandleGameEvent(gameEvent);
        }
    }
    
    void OnApplicationPause(bool pauseStatus)
    {
        string eventType = pauseStatus ? "application_paused" : "application_resumed";
        SendGameEvent(eventType, pauseStatus.ToString());
    }
    
    void OnApplicationFocus(bool hasFocus)
    {
        string eventType = hasFocus ? "application_focused" : "application_lost_focus";
        SendGameEvent(eventType, hasFocus.ToString());
    }
}

// Interface for game systems that need to handle events
public interface IGameEventHandler
{
    void HandleGameEvent(UnityReactBridge.GameEvent gameEvent);
}
```

### React Integration Component
**React Side Communication**:
```javascript
// UnityReactManager.js - React component for Unity integration
import React, { useEffect, useState, useCallback } from 'react';

class UnityReactManager {
  constructor() {
    this.unityInstance = null;
    this.eventCallbacks = new Map();
    this.isUnityReady = false;
    
    // Bind methods
    this.sendToUnity = this.sendToUnity.bind(this);
    this.receiveFromUnity = this.receiveFromUnity.bind(this);
    
    // Make globally available for Unity to call
    window.receiveFromUnity = this.receiveFromUnity;
  }
  
  // Initialize Unity integration
  initialize(unityInstance) {
    this.unityInstance = unityInstance;
    console.log('🎮 Unity React Manager initialized');
    
    // Set up Unity event listeners
    this.setupUnityEventHandlers();
  }
  
  setupUnityEventHandlers() {
    // Listen for Unity ready event
    this.addEventListener('unity_ready', (data) => {
      this.isUnityReady = true;
      console.log('✅ Unity is ready for communication');
      
      // Request initial game state
      this.requestGameState();
    });
    
    // Listen for player stats updates
    this.addEventListener('player_stats_updated', (data) => {
      const playerStats = JSON.parse(data);
      this.handlePlayerStatsUpdate(playerStats);
    });
    
    // Listen for game state changes
    this.addEventListener('game_paused', () => {
      this.handleGamePause(true);
    });
    
    this.addEventListener('game_resumed', () => {
      this.handleGamePause(false);
    });
  }
  
  // Send data to Unity
  sendToUnity(eventType, data) {
    if (!this.isUnityReady) {
      console.warn('⚠️ Unity not ready, queuing event:', eventType);
      return;
    }
    
    const eventData = {
      eventType,
      data: JSON.stringify(data),
      timestamp: Date.now()
    };
    
    try {
      this.unityInstance.SendMessage(
        'UnityReactBridge', 
        'ReceiveFromReact', 
        JSON.stringify(eventData)
      );
      
      console.log('📤 Sent to Unity:', eventType);
    } catch (error) {
      console.error('❌ Failed to send to Unity:', error);
    }
  }
  
  // Receive data from Unity
  receiveFromUnity(eventType, jsonData) {
    try {
      const eventData = JSON.parse(jsonData);
      console.log('📨 Received from Unity:', eventType);
      
      // Trigger registered callbacks
      if (this.eventCallbacks.has(eventType)) {
        const callbacks = this.eventCallbacks.get(eventType);
        callbacks.forEach(callback => callback(eventData.data));
      }
    } catch (error) {
      console.error('❌ Failed to parse Unity data:', error);
    }
  }
  
  // Register event listener
  addEventListener(eventType, callback) {
    if (!this.eventCallbacks.has(eventType)) {
      this.eventCallbacks.set(eventType, []);
    }
    
    this.eventCallbacks.get(eventType).push(callback);
  }
  
  // Remove event listener
  removeEventListener(eventType, callback) {
    if (this.eventCallbacks.has(eventType)) {
      const callbacks = this.eventCallbacks.get(eventType);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }
  
  // Unity control methods
  pauseGame() {
    this.sendToUnity('ui_action', { action: 'pause_game' });
  }
  
  resumeGame() {
    this.sendToUnity('ui_action', { action: 'resume_game' });
  }
  
  restartGame() {
    this.sendToUnity('ui_action', { action: 'restart_game' });
  }
  
  updatePlayerName(name) {
    this.sendToUnity('player_name_changed', name);
  }
  
  updateGameSettings(settings) {
    this.sendToUnity('game_settings_updated', settings);
  }
  
  requestGameState() {
    this.sendToUnity('request_game_state', {});
  }
  
  // Event handlers
  handlePlayerStatsUpdate(playerStats) {
    // Update React state with player stats
    console.log('📊 Player stats updated:', playerStats);
  }
  
  handleGamePause(isPaused) {
    console.log(isPaused ? '⏸️ Game paused' : '▶️ Game resumed');
  }
}

// React Hook for Unity integration
export const useUnityIntegration = () => {
  const [unityManager] = useState(() => new UnityReactManager());
  const [isUnityReady, setIsUnityReady] = useState(false);
  const [gameState, setGameState] = useState({
    isPlaying: false,
    playerStats: null,
    currentScene: '',
    gameTime: 0
  });
  
  useEffect(() => {
    // Listen for Unity ready event
    unityManager.addEventListener('unity_ready', () => {
      setIsUnityReady(true);
    });
    
    // Listen for game state updates
    unityManager.addEventListener('game_state_response', (data) => {
      const state = JSON.parse(data);
      setGameState(state);
    });
    
    // Listen for player stats updates
    unityManager.addEventListener('player_stats_updated', (data) => {
      const playerStats = JSON.parse(data);
      setGameState(prev => ({
        ...prev,
        playerStats
      }));
    });
    
    return () => {
      // Cleanup listeners
      unityManager.eventCallbacks.clear();
    };
  }, [unityManager]);
  
  const controls = {
    pauseGame: () => unityManager.pauseGame(),
    resumeGame: () => unityManager.resumeGame(),
    restartGame: () => unityManager.restartGame(),
    updatePlayerName: (name) => unityManager.updatePlayerName(name),
    updateSettings: (settings) => unityManager.updateGameSettings(settings),
    requestGameState: () => unityManager.requestGameState()
  };
  
  return {
    unityManager,
    isUnityReady,
    gameState,
    controls
  };
};

// React Component for Unity Game Interface
export const UnityGameInterface = ({ unityInstance }) => {
  const { unityManager, isUnityReady, gameState, controls } = useUnityIntegration();
  const [playerName, setPlayerName] = useState('Player');
  const [gameSettings, setGameSettings] = useState({
    volume: 1.0,
    quality: 2,
    fullscreen: false
  });
  
  useEffect(() => {
    if (unityInstance) {
      unityManager.initialize(unityInstance);
    }
  }, [unityInstance, unityManager]);
  
  const handlePlayerNameChange = (e) => {
    const newName = e.target.value;
    setPlayerName(newName);
    controls.updatePlayerName(newName);
  };
  
  const handleSettingChange = (key, value) => {
    const newSettings = { ...gameSettings, [key]: value };
    setGameSettings(newSettings);
    controls.updateSettings(newSettings);
  };
  
  return (
    <div className="unity-game-interface">
      <div className="game-container">
        {/* Unity WebGL canvas will be inserted here */}
        <div id="unity-container" />
      </div>
      
      <div className="game-controls">
        <div className="player-info">
          <h3>Player Information</h3>
          <div className="form-group">
            <label>Player Name:</label>
            <input
              type="text"
              value={playerName}
              onChange={handlePlayerNameChange}
              disabled={!isUnityReady}
            />
          </div>
          
          {gameState.playerStats && (
            <div className="stats-display">
              <p>Score: {gameState.playerStats.score}</p>
              <p>Level: {gameState.playerStats.level}</p>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${gameState.playerStats.progress * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>
        
        <div className="game-settings">
          <h3>Game Settings</h3>
          <div className="form-group">
            <label>Volume:</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={gameSettings.volume}
              onChange={(e) => handleSettingChange('volume', parseFloat(e.target.value))}
              disabled={!isUnityReady}
            />
          </div>
          
          <div className="form-group">
            <label>Quality:</label>
            <select
              value={gameSettings.quality}
              onChange={(e) => handleSettingChange('quality', parseInt(e.target.value))}
              disabled={!isUnityReady}
            >
              <option value={0}>Low</option>
              <option value={1}>Medium</option>
              <option value={2}>High</option>
              <option value={3}>Ultra</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>
              <input
                type="checkbox"
                checked={gameSettings.fullscreen}
                onChange={(e) => handleSettingChange('fullscreen', e.target.checked)}
                disabled={!isUnityReady}
              />
              Fullscreen
            </label>
          </div>
        </div>
        
        <div className="game-actions">
          <h3>Game Controls</h3>
          <button 
            onClick={controls.pauseGame}
            disabled={!isUnityReady || !gameState.isPlaying}
          >
            Pause Game
          </button>
          
          <button 
            onClick={controls.resumeGame}
            disabled={!isUnityReady || gameState.isPlaying}
          >
            Resume Game
          </button>
          
          <button 
            onClick={controls.restartGame}
            disabled={!isUnityReady}
          >
            Restart Game
          </button>
          
          <button 
            onClick={controls.requestGameState}
            disabled={!isUnityReady}
          >
            Refresh State
          </button>
        </div>
      </div>
      
      <div className="connection-status">
        <div className={`status-indicator ${isUnityReady ? 'connected' : 'disconnected'}`}>
          {isUnityReady ? '🟢 Unity Connected' : '🔴 Unity Disconnected'}
        </div>
      </div>
    </div>
  );
};

export default UnityReactManager;
```

## 🚀 AI Integration Opportunities

### Smart Development Workflow
**AI-Enhanced React-Unity Development**:
- Generate Unity-React communication boilerplate with specific event types
- Automate responsive design patterns for game interfaces
- Create intelligent state synchronization between Unity and React
- Build automated testing frameworks for cross-platform communication
- Generate performance monitoring dashboards for hybrid applications

### Prompt Templates for Development
```
"Create a React component that displays Unity game leaderboards with real-time updates, smooth animations, and mobile-responsive design"

"Generate Unity C# code for sending complex game events to React UI, including player inventory, achievement progress, and multiplayer status"

"Build an automated deployment pipeline for Unity WebGL games with React front-ends, including CDN optimization and progressive loading"
```

React-Unity integration enables powerful hybrid game applications that combine Unity's rendering capabilities with React's flexible UI framework, creating seamless player experiences across web and mobile platforms.