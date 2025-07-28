# @27-Game-State-Manager

## 🎯 Core Concept
Automated game state management system for handling menu, gameplay, and transition states.

## 🔧 Implementation

### Game State Framework
```csharp
using UnityEngine;
using System.Collections.Generic;

public enum GameState
{
    MainMenu,
    Loading,
    Gameplay,
    Paused,
    GameOver,
    Settings,
    Inventory
}

public class GameStateManager : MonoBehaviour
{
    public static GameStateManager Instance;
    
    [Header("State Settings")]
    public GameState initialState = GameState.MainMenu;
    public bool debugStateChanges = true;
    
    private GameState currentState;
    private GameState previousState;
    private Dictionary<GameState, IGameState> states;
    private Stack<GameState> stateHistory;
    
    public GameState CurrentState => currentState;
    public GameState PreviousState => previousState;
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeStates();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void Start()
    {
        ChangeState(initialState);
    }
    
    void InitializeStates()
    {
        states = new Dictionary<GameState, IGameState>();
        stateHistory = new Stack<GameState>();
        
        // Register state implementations
        states[GameState.MainMenu] = new MainMenuState();
        states[GameState.Loading] = new LoadingState();
        states[GameState.Gameplay] = new GameplayState();
        states[GameState.Paused] = new PausedState();
        states[GameState.GameOver] = new GameOverState();
        states[GameState.Settings] = new SettingsState();
        states[GameState.Inventory] = new InventoryState();
    }
    
    public void ChangeState(GameState newState)
    {
        if (currentState == newState) return;
        
        // Exit current state
        if (states.ContainsKey(currentState))
        {
            states[currentState].OnExit();
        }
        
        // Update state tracking
        previousState = currentState;
        if (currentState != GameState.Loading) // Don't track loading states
        {
            stateHistory.Push(currentState);
        }
        currentState = newState;
        
        // Enter new state
        if (states.ContainsKey(newState))
        {
            states[newState].OnEnter();
        }
        
        if (debugStateChanges)
        {
            Debug.Log($"State changed: {previousState} -> {currentState}");
        }
        
        // Notify listeners
        OnStateChanged?.Invoke(currentState, previousState);
    }
    
    public void GoToPreviousState()
    {
        if (stateHistory.Count > 0)
        {
            GameState lastState = stateHistory.Pop();
            ChangeState(lastState);
        }
    }
    
    public void PauseGame()
    {
        if (currentState == GameState.Gameplay)
        {
            ChangeState(GameState.Paused);
            Time.timeScale = 0f;
        }
    }
    
    public void ResumeGame()
    {
        if (currentState == GameState.Paused)
        {
            ChangeState(GameState.Gameplay);
            Time.timeScale = 1f;
        }
    }
    
    public void RestartLevel()
    {
        ChangeState(GameState.Loading);
        // Implement level restart logic
        UnityEngine.SceneManagement.SceneManager.LoadScene(
            UnityEngine.SceneManagement.SceneManager.GetActiveScene().name);
    }
    
    public void QuitToMainMenu()
    {
        Time.timeScale = 1f;
        ChangeState(GameState.Loading);
        // Load main menu scene
        UnityEngine.SceneManagement.SceneManager.LoadScene("MainMenu");
    }
    
    void Update()
    {
        // Update current state
        if (states.ContainsKey(currentState))
        {
            states[currentState].OnUpdate();
        }
        
        // Handle global input
        HandleGlobalInput();
    }
    
    void HandleGlobalInput()
    {
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            switch (currentState)
            {
                case GameState.Gameplay:
                    PauseGame();
                    break;
                case GameState.Paused:
                case GameState.Settings:
                case GameState.Inventory:
                    GoToPreviousState();
                    break;
            }
        }
    }
    
    public System.Action<GameState, GameState> OnStateChanged;
}

public interface IGameState
{
    void OnEnter();
    void OnUpdate();
    void OnExit();
}

public class MainMenuState : IGameState
{
    public void OnEnter()
    {
        Debug.Log("Entered Main Menu");
        // Show main menu UI
    }
    
    public void OnUpdate()
    {
        // Handle main menu input
    }
    
    public void OnExit()
    {
        Debug.Log("Exited Main Menu");
        // Hide main menu UI
    }
}

public class GameplayState : IGameState
{
    public void OnEnter()
    {
        Debug.Log("Entered Gameplay");
        Time.timeScale = 1f;
        // Enable gameplay systems
    }
    
    public void OnUpdate()
    {
        // Handle gameplay logic
    }
    
    public void OnExit()
    {
        Debug.Log("Exited Gameplay");
        // Disable gameplay systems
    }
}

public class PausedState : IGameState
{
    public void OnEnter()
    {
        Debug.Log("Game Paused");
        Time.timeScale = 0f;
        // Show pause menu
    }
    
    public void OnUpdate()
    {
        // Handle pause menu input
    }
    
    public void OnExit()
    {
        Debug.Log("Game Resumed");
        Time.timeScale = 1f;
        // Hide pause menu
    }
}

public class LoadingState : IGameState
{
    public void OnEnter()
    {
        Debug.Log("Loading...");
        // Show loading screen
    }
    
    public void OnUpdate()
    {
        // Update loading progress
    }
    
    public void OnExit()
    {
        Debug.Log("Loading Complete");
        // Hide loading screen
    }
}

public class GameOverState : IGameState
{
    public void OnEnter()
    {
        Debug.Log("Game Over");
        // Show game over screen
    }
    
    public void OnUpdate()
    {
        // Handle game over input
    }
    
    public void OnExit()
    {
        Debug.Log("Exited Game Over");
        // Hide game over screen
    }
}

public class SettingsState : IGameState
{
    public void OnEnter()
    {
        Debug.Log("Settings Opened");
        // Show settings UI
    }
    
    public void OnUpdate()
    {
        // Handle settings input
    }
    
    public void OnExit()
    {
        Debug.Log("Settings Closed");
        // Hide settings UI
    }
}

public class InventoryState : IGameState
{
    public void OnEnter()
    {
        Debug.Log("Inventory Opened");
        // Show inventory UI
    }
    
    public void OnUpdate()
    {
        // Handle inventory input
    }
    
    public void OnExit()
    {
        Debug.Log("Inventory Closed");
        // Hide inventory UI
    }
}
```

## 🚀 AI/LLM Integration
- Generate state machine logic from game design
- Automatically create state transitions
- Optimize state management for performance

## 💡 Key Benefits
- Clean game state organization
- Automatic state history tracking
- Simplified state transitions