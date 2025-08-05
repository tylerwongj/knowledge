# @a-Unity-WebGL-Frontend-Integration

## 🎯 Learning Objectives
- Master Unity WebGL builds and web integration patterns
- Implement React/Vue.js interfaces for Unity games
- Understand JavaScript-Unity communication bridges
- Build responsive web wrappers for Unity applications

## 🔧 Unity WebGL Build Optimization

### WebGL Build Configuration
```csharp
using UnityEditor;
using UnityEngine;

public class WebGLBuildProcessor
{
    [MenuItem("Build/Configure WebGL Build")]
    public static void ConfigureWebGLBuild()
    {
        // Optimization settings for WebGL
        PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Gzip;
        PlayerSettings.WebGL.memorySize = 256; // MB
        PlayerSettings.WebGL.exceptionSupport = WebGLExceptionSupport.ExplicitlyThrownExceptionsOnly;
        PlayerSettings.WebGL.linkerTarget = WebGLLinkerTarget.Wasm;
        
        // Template and branding
        PlayerSettings.WebGL.template = "PROJECT:Custom";
        PlayerSettings.companyName = "Your Company";
        PlayerSettings.productName = "Your Game";
        
        Debug.Log("WebGL build configured successfully");
    }
}
```

### Custom WebGL Template
```html
<!DOCTYPE html>
<html lang="en-us">
<head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>%UNITY_WEB_NAME%</title>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            background: #1e1e1e;
            color: #e8e8e8;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        #unity-container {
            position: relative;
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        #unity-canvas {
            background: #232323;
            max-width: 100%;
            max-height: 100%;
        }
        
        #unity-loading-bar {
            position: absolute;
            width: 60%;
            height: 4px;
            background: #404040;
            border-radius: 2px;
            overflow: hidden;
        }
        
        #unity-progress-bar {
            width: 0%;
            height: 100%;
            background: #4a9eff;
            transition: width 0.3s ease;
        }
        
        .loading-text {
            position: absolute;
            top: 60%;
            left: 50%;
            transform: translateX(-50%);
            font-size: 16px;
            color: #c0c0c0;
        }
    </style>
</head>
<body>
    <div id="unity-container">
        <canvas id="unity-canvas"></canvas>
        <div id="unity-loading-bar">
            <div id="unity-progress-bar"></div>
        </div>
        <div class="loading-text">Loading...</div>
    </div>

    <script>
        const buildUrl = "Build";
        const loaderUrl = buildUrl + "/%UNITY_WEBGL_LOADER_FILENAME%";
        const config = {
            dataUrl: buildUrl + "/%UNITY_WEBGL_DATA_FILENAME%",
            frameworkUrl: buildUrl + "/%UNITY_WEBGL_FRAMEWORK_FILENAME%",
            codeUrl: buildUrl + "/%UNITY_WEBGL_CODE_FILENAME%",
            streamingAssetsUrl: "StreamingAssets",
            companyName: "%UNITY_COMPANY_NAME%",
            productName: "%UNITY_PRODUCT_NAME%",
            productVersion: "%UNITY_PRODUCT_VERSION%",
        };

        const container = document.querySelector("#unity-container");
        const canvas = document.querySelector("#unity-canvas");
        const loadingBar = document.querySelector("#unity-loading-bar");
        const progressBar = document.querySelector("#unity-progress-bar");
        const loadingText = document.querySelector(".loading-text");

        // Unity instance for communication
        let unityInstance = null;

        // Loading progress handler
        if (/iPhone|iPad|iPod|Android/i.test(navigator.userAgent)) {
            container.className = "unity-mobile";
            config.devicePixelRatio = 1;
        }

        const script = document.createElement("script");
        script.src = loaderUrl;
        script.onload = () => {
            createUnityInstance(canvas, config, (progress) => {
                progressBar.style.width = 100 * progress + "%";
                loadingText.textContent = `Loading... ${Math.round(100 * progress)}%`;
            }).then((instance) => {
                unityInstance = instance;
                loadingBar.style.display = "none";
                loadingText.style.display = "none";
                
                // Enable communication with Unity
                window.unityInstance = instance;
                
                // Notify parent frame if embedded
                if (window.parent !== window) {
                    window.parent.postMessage({ type: 'unity-loaded' }, '*');
                }
            }).catch((message) => {
                alert(message);
            });
        };
        document.body.appendChild(script);

        // JavaScript to Unity communication
        function sendToUnity(gameObject, methodName, value) {
            if (unityInstance) {
                unityInstance.SendMessage(gameObject, methodName, value);
            }
        }

        // Unity to JavaScript communication (called from Unity)
        function receiveFromUnity(message) {
            console.log('Message from Unity:', message);
            // Handle Unity messages here
            if (window.parent !== window) {
                window.parent.postMessage({ 
                    type: 'unity-message', 
                    data: message 
                }, '*');
            }
        }
    </script>
</body>
</html>
```

## 🚀 React Integration with Unity WebGL

### React Unity Component
```jsx
import React, { useRef, useEffect, useState } from 'react';
import { Unity, useUnityContext } from 'react-unity-webgl';

const UnityGameComponent = ({ gameConfig, onGameLoaded, onGameMessage }) => {
    const [loadingProgress, setLoadingProgress] = useState(0);
    const [isLoaded, setIsLoaded] = useState(false);

    const {
        unityProvider,
        sendMessage,
        addEventListener,
        removeEventListener,
        requestFullscreen,
        isLoaded: unityIsLoaded,
        loadingProgression,
    } = useUnityContext({
        loaderUrl: gameConfig.loaderUrl,
        dataUrl: gameConfig.dataUrl,
        frameworkUrl: gameConfig.frameworkUrl,
        codeUrl: gameConfig.codeUrl,
    });

    // Handle loading progress
    useEffect(() => {
        setLoadingProgress(loadingProgression);
    }, [loadingProgression]);

    // Handle game loaded
    useEffect(() => {
        if (unityIsLoaded && !isLoaded) {
            setIsLoaded(true);
            onGameLoaded && onGameLoaded();
        }
    }, [unityIsLoaded, isLoaded, onGameLoaded]);

    // Unity event handlers
    useEffect(() => {
        const handleGameMessage = (message) => {
            onGameMessage && onGameMessage(message);
        };

        const handlePlayerProgress = (data) => {
            console.log('Player progress:', data);
        };

        addEventListener('GameMessage', handleGameMessage);
        addEventListener('PlayerProgress', handlePlayerProgress);

        return () => {
            removeEventListener('GameMessage', handleGameMessage);
            removeEventListener('PlayerProgress', handlePlayerProgress);
        };
    }, [addEventListener, removeEventListener, onGameMessage]);

    // Game control functions
    const startGame = () => {
        sendMessage('GameManager', 'StartGame');
    };

    const pauseGame = () => {
        sendMessage('GameManager', 'PauseGame');
    };

    const setPlayerName = (name) => {
        sendMessage('PlayerManager', 'SetPlayerName', name);
    };

    return (
        <div className="unity-game-container">
            {!isLoaded && (
                <div className="loading-overlay">
                    <div className="loading-bar">
                        <div 
                            className="loading-progress" 
                            style={{ width: `${loadingProgress * 100}%` }}
                        />
                    </div>
                    <p>Loading... {Math.round(loadingProgress * 100)}%</p>
                </div>
            )}
            
            <Unity 
                unityProvider={unityProvider}
                style={{
                    width: '100%',
                    height: '100%',
                    display: isLoaded ? 'block' : 'none'
                }}
            />
            
            {isLoaded && (
                <div className="game-controls">
                    <button onClick={startGame}>Start Game</button>
                    <button onClick={pauseGame}>Pause Game</button>
                    <button onClick={requestFullscreen}>Fullscreen</button>
                </div>
            )}
        </div>
    );
};

export default UnityGameComponent;
```

### React Game Dashboard
```jsx
import React, { useState, useEffect } from 'react';
import UnityGameComponent from './UnityGameComponent';
import PlayerStats from './PlayerStats';
import GameChat from './GameChat';

const GameDashboard = () => {
    const [gameData, setGameData] = useState({
        playerStats: { level: 1, score: 0, coins: 100 },
        isGameLoaded: false,
        gameMessages: []
    });

    const gameConfig = {
        loaderUrl: '/Build/WebGL.loader.js',
        dataUrl: '/Build/WebGL.data',
        frameworkUrl: '/Build/WebGL.framework.js',
        codeUrl: '/Build/WebGL.wasm',
    };

    const handleGameLoaded = () => {
        setGameData(prev => ({ ...prev, isGameLoaded: true }));
        console.log('Unity game loaded successfully');
    };

    const handleGameMessage = (message) => {
        console.log('Game message:', message);
        
        try {
            const data = JSON.parse(message);
            
            switch (data.type) {
                case 'playerStats':
                    setGameData(prev => ({
                        ...prev,
                        playerStats: { ...prev.playerStats, ...data.stats }
                    }));
                    break;
                    
                case 'gameEvent':
                    setGameData(prev => ({
                        ...prev,
                        gameMessages: [...prev.gameMessages, data.message]
                    }));
                    break;
                    
                default:
                    console.log('Unknown message type:', data.type);
            }
        } catch (error) {
            console.error('Error parsing game message:', error);
        }
    };

    const sendChatMessage = (message) => {
        // Send chat message to Unity
        if (window.unityInstance) {
            window.unityInstance.SendMessage('ChatManager', 'ReceiveChatMessage', message);
        }
    };

    return (
        <div className="game-dashboard">
            <div className="dashboard-header">
                <h1>Unity WebGL Game Dashboard</h1>
                <PlayerStats stats={gameData.playerStats} />
            </div>
            
            <div className="dashboard-content">
                <div className="game-area">
                    <UnityGameComponent
                        gameConfig={gameConfig}
                        onGameLoaded={handleGameLoaded}
                        onGameMessage={handleGameMessage}
                    />
                </div>
                
                <div className="sidebar">
                    <GameChat
                        messages={gameData.gameMessages}
                        onSendMessage={sendChatMessage}
                        isGameLoaded={gameData.isGameLoaded}
                    />
                </div>
            </div>
        </div>
    );
};

export default GameDashboard;
```

## 🔧 Unity-JavaScript Communication Bridge

### Unity C# Communication Script
```csharp
using UnityEngine;
using System.Runtime.InteropServices;
using Newtonsoft.Json;

public class WebGLCommunication : MonoBehaviour
{
    [DllImport("__Internal")]
    private static extern void SendMessageToJS(string message);

    [DllImport("__Internal")]
    private static extern void RequestFullscreen();

    public static WebGLCommunication Instance { get; private set; }

    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }

    // Called from JavaScript
    public void ReceiveMessageFromJS(string message)
    {
        Debug.Log($"Received from JS: {message}");
        
        try
        {
            var data = JsonConvert.DeserializeObject<JSMessage>(message);
            HandleJSMessage(data);
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Error parsing JS message: {e.Message}");
        }
    }

    private void HandleJSMessage(JSMessage message)
    {
        switch (message.type)
        {
            case "setPlayerName":
                PlayerManager.Instance?.SetPlayerName(message.data);
                break;
                
            case "startGame":
                GameManager.Instance?.StartGame();
                break;
                
            case "pauseGame":
                GameManager.Instance?.PauseGame();
                break;
                
            case "chatMessage":
                ChatManager.Instance?.ReceiveChatMessage(message.data);
                break;
        }
    }

    // Send data to JavaScript
    public void SendPlayerStats(PlayerStats stats)
    {
        var message = new UnityMessage
        {
            type = "playerStats",
            data = JsonConvert.SerializeObject(stats)
        };

        SendToJS(JsonConvert.SerializeObject(message));
    }

    public void SendGameEvent(string eventName, object eventData)
    {
        var message = new UnityMessage
        {
            type = "gameEvent",
            data = JsonConvert.SerializeObject(new { eventName, eventData })
        };

        SendToJS(JsonConvert.SerializeObject(message));
    }

    private void SendToJS(string message)
    {
        #if UNITY_WEBGL && !UNITY_EDITOR
            SendMessageToJS(message);
        #else
            Debug.Log($"Would send to JS: {message}");
        #endif
    }

    [System.Serializable]
    public class JSMessage
    {
        public string type;
        public string data;
    }

    [System.Serializable]
    public class UnityMessage
    {
        public string type;
        public string data;
    }
}
```

### JavaScript Plugin for Unity
```javascript
// WebGLCommunication.jslib
mergeInto(LibraryManager.library, {
    SendMessageToJS: function(message) {
        const messageStr = UTF8ToString(message);
        
        // Call the global receiveFromUnity function
        if (typeof receiveFromUnity !== 'undefined') {
            receiveFromUnity(messageStr);
        }
        
        // Post message to parent frame if embedded
        if (window.parent !== window) {
            window.parent.postMessage({
                type: 'unity-message',
                data: messageStr
            }, '*');
        }
    },

    RequestFullscreen: function() {
        if (document.documentElement.requestFullscreen) {
            document.documentElement.requestFullscreen();
        } else if (document.documentElement.webkitRequestFullscreen) {
            document.documentElement.webkitRequestFullscreen();
        } else if (document.documentElement.msRequestFullscreen) {
            document.documentElement.msRequestFullscreen();
        }
    },

    GetBrowserLanguage: function() {
        const lang = navigator.language || navigator.userLanguage || 'en';
        const bufferSize = lengthBytesUTF8(lang) + 1;
        const buffer = _malloc(bufferSize);
        stringToUTF8(lang, buffer, bufferSize);
        return buffer;
    },

    OpenExternalLink: function(url) {
        const urlStr = UTF8ToString(url);
        window.open(urlStr, '_blank');
    }
});
```

## 🚀 AI/LLM Integration Opportunities

### Frontend Integration Automation
```prompt
Generate React frontend integration for Unity WebGL game [GAME_NAME] including:
- Responsive game container with loading states
- Real-time communication bridge with Unity
- Player dashboard with stats and controls
- Chat system integration
- Progressive Web App (PWA) configuration
- Performance monitoring and analytics
```

### WebGL Optimization Guide
```prompt
Create comprehensive Unity WebGL optimization guide for [PROJECT_TYPE]:
- Build configuration for minimal file sizes
- Asset compression and streaming strategies
- Memory management for web browsers
- Performance profiling and bottleneck identification
- Cross-browser compatibility testing
- Mobile web optimization techniques
```

## 💡 Key Frontend Integration Best Practices

### 1. Performance Optimization
- Minimize Unity build size through asset optimization
- Implement progressive loading for large games
- Use efficient communication protocols between Unity and JS
- Monitor memory usage and implement cleanup strategies

### 2. User Experience
- Provide clear loading indicators and progress feedback
- Implement responsive design for various screen sizes
- Handle browser compatibility issues gracefully
- Offer offline functionality where possible

### 3. Communication Architecture
- Design clean message protocols between Unity and web
- Implement error handling for communication failures
- Use typed interfaces for message structure
- Provide fallback mechanisms for unsupported features

This comprehensive guide provides everything needed to successfully integrate Unity WebGL builds with modern frontend frameworks and create professional web-based gaming experiences.