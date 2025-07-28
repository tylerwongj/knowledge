# @32-Networking-Multiplayer-Tools

## 🎯 Core Concept
Automated multiplayer networking setup with player synchronization and room management.

## 🔧 Implementation

### Network Manager Framework
```csharp
using UnityEngine;
using UnityEngine.Networking;
using System.Collections.Generic;

public class NetworkGameManager : NetworkBehaviour
{
    public static NetworkGameManager Instance;
    
    [Header("Network Settings")]
    public GameObject playerPrefab;
    public Transform[] spawnPoints;
    public int maxPlayers = 8;
    public float respawnTime = 5f;
    
    [SyncVar]
    public int gameScore = 0;
    
    [SyncVar]
    public float gameTimer = 300f; // 5 minutes
    
    private List<NetworkPlayer> connectedPlayers = new List<NetworkPlayer>();
    private bool gameStarted = false;
    
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
    
    public override void OnStartServer()
    {
        NetworkManager.singleton.maxConnections = maxPlayers;
        Debug.Log("Server started");
    }
    
    [Server]
    public void StartGame()
    {
        if (gameStarted) return;
        
        gameStarted = true;
        gameTimer = 300f;
        
        RpcGameStarted();
        InvokeRepeating(nameof(UpdateGameTimer), 1f, 1f);
    }
    
    [ClientRpc]
    void RpcGameStarted()
    {
        Debug.Log("Game started!");
        // Update UI to show game has started
    }
    
    [Server]
    void UpdateGameTimer()
    {
        if (!gameStarted) return;
        
        gameTimer -= 1f;
        
        if (gameTimer <= 0)
        {
            EndGame();
        }
    }
    
    [Server]
    void EndGame()
    {
        gameStarted = false;
        CancelInvoke(nameof(UpdateGameTimer));
        
        RpcGameEnded();
    }
    
    [ClientRpc]
    void RpcGameEnded()
    {
        Debug.Log("Game ended!");
        // Show end game UI
    }
    
    [Server]
    public void RegisterPlayer(NetworkPlayer player)
    {
        if (!connectedPlayers.Contains(player))
        {
            connectedPlayers.Add(player);
            RpcPlayerJoined(player.playerName);
            
            if (connectedPlayers.Count >= 2 && !gameStarted)
            {
                StartGame();
            }
        }
    }
    
    [Server]
    public void UnregisterPlayer(NetworkPlayer player)
    {
        if (connectedPlayers.Contains(player))
        {
            connectedPlayers.Remove(player);
            RpcPlayerLeft(player.playerName);
        }
    }
    
    [ClientRpc]
    void RpcPlayerJoined(string playerName)
    {
        Debug.Log($"Player joined: {playerName}");
    }
    
    [ClientRpc]
    void RpcPlayerLeft(string playerName)
    {
        Debug.Log($"Player left: {playerName}");
    }
    
    [Server]
    public Vector3 GetSpawnPoint()
    {
        if (spawnPoints.Length == 0)
            return Vector3.zero;
        
        return spawnPoints[Random.Range(0, spawnPoints.Length)].position;
    }
    
    [Server]
    public void AddScore(int points)
    {
        gameScore += points;
        RpcScoreUpdated(gameScore);
    }
    
    [ClientRpc]
    void RpcScoreUpdated(int newScore)
    {
        // Update score UI
        Debug.Log($"Score updated: {newScore}");
    }
}

public class NetworkPlayer : NetworkBehaviour
{
    [Header("Player Settings")]
    public float moveSpeed = 5f;
    public float jumpForce = 10f;
    public int maxHealth = 100;
    
    [SyncVar(hook = "OnNameChanged")]
    public string playerName;
    
    [SyncVar(hook = "OnHealthChanged")]
    public int currentHealth;
    
    [SyncVar(hook = "OnScoreChanged")]
    public int playerScore;
    
    private Rigidbody playerRigidbody;
    private bool isGrounded;
    
    void Start()
    {
        playerRigidbody = GetComponent<Rigidbody>();
        currentHealth = maxHealth;
        
        if (isLocalPlayer)
        {
            // Set player name
            CmdSetPlayerName($"Player_{Random.Range(1000, 9999)}");
            
            // Register with game manager
            if (NetworkGameManager.Instance != null)
            {
                NetworkGameManager.Instance.RegisterPlayer(this);
            }
        }
    }
    
    void Update()
    {
        if (!isLocalPlayer) return;
        
        HandleMovement();
        HandleInput();
    }
    
    void HandleMovement()
    {
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");
        
        Vector3 movement = new Vector3(horizontal, 0, vertical) * moveSpeed;
        movement.y = playerRigidbody.velocity.y;
        
        playerRigidbody.velocity = movement;
        
        if (movement.magnitude > 0.1f)
        {
            transform.LookAt(transform.position + new Vector3(horizontal, 0, vertical));
        }
    }
    
    void HandleInput()
    {
        if (Input.GetKeyDown(KeyCode.Space) && isGrounded)
        {
            CmdJump();
        }
        
        if (Input.GetKeyDown(KeyCode.F))
        {
            CmdAttack();
        }
    }
    
    [Command]
    void CmdSetPlayerName(string name)
    {
        playerName = name;
    }
    
    [Command]
    void CmdJump()
    {
        if (isGrounded)
        {
            playerRigidbody.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
            RpcPlayJumpEffect();
        }
    }
    
    [Command]
    void CmdAttack()
    {
        // Perform attack logic on server
        Collider[] hitTargets = Physics.OverlapSphere(transform.position + transform.forward, 2f);
        
        foreach (var target in hitTargets)
        {
            NetworkPlayer targetPlayer = target.GetComponent<NetworkPlayer>();
            if (targetPlayer != null && targetPlayer != this)
            {
                targetPlayer.TakeDamage(25);
                AddScore(10);
            }
        }
        
        RpcPlayAttackEffect();
    }
    
    [ClientRpc]
    void RpcPlayJumpEffect()
    {
        // Play jump visual/audio effects
        Debug.Log($"{playerName} jumped!");
    }
    
    [ClientRpc]
    void RpcPlayAttackEffect()
    {
        // Play attack visual/audio effects
        Debug.Log($"{playerName} attacked!");
    }
    
    [Server]
    public void TakeDamage(int damage)
    {
        currentHealth -= damage;
        
        if (currentHealth <= 0)
        {
            Die();
        }
    }
    
    [Server]
    void Die()
    {
        RpcOnDeath();
        
        // Respawn after delay
        Invoke(nameof(Respawn), NetworkGameManager.Instance.respawnTime);
    }
    
    [Server]
    void Respawn()
    {
        currentHealth = maxHealth;
        Vector3 spawnPoint = NetworkGameManager.Instance.GetSpawnPoint();
        transform.position = spawnPoint;
        
        RpcOnRespawn();
    }
    
    [ClientRpc]
    void RpcOnDeath()
    {
        Debug.Log($"{playerName} died!");
        // Play death effects
    }
    
    [ClientRpc]
    void RpcOnRespawn()
    {
        Debug.Log($"{playerName} respawned!");
        // Play respawn effects
    }
    
    [Server]
    void AddScore(int points)
    {
        playerScore += points;
        
        if (NetworkGameManager.Instance != null)
        {
            NetworkGameManager.Instance.AddScore(points);
        }
    }
    
    void OnNameChanged(string newName)
    {
        gameObject.name = newName;
    }
    
    void OnHealthChanged(int newHealth)
    {
        // Update health UI
        if (isLocalPlayer)
        {
            Debug.Log($"Health: {newHealth}/{maxHealth}");
        }
    }
    
    void OnScoreChanged(int newScore)
    {
        // Update score UI
        if (isLocalPlayer)
        {
            Debug.Log($"Score: {newScore}");
        }
    }
    
    void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.CompareTag("Ground"))
        {
            isGrounded = true;
        }
    }
    
    void OnCollisionExit(Collision collision)
    {
        if (collision.gameObject.CompareTag("Ground"))
        {
            isGrounded = false;
        }
    }
    
    void OnDestroy()
    {
        if (NetworkGameManager.Instance != null)
        {
            NetworkGameManager.Instance.UnregisterPlayer(this);
        }
    }
}

public class NetworkLobby : NetworkLobbyManager
{
    [Header("Lobby Settings")]
    public int minPlayersToStart = 2;
    
    public override void OnLobbyServerPlayersReady()
    {
        if (numReadyPlayers >= minPlayersToStart)
        {
            ServerChangeScene(playScene);
        }
    }
    
    public override bool OnLobbyServerSceneLoadedForPlayer(GameObject lobbyPlayer, GameObject gamePlayer)
    {
        // Configure game player when spawned
        NetworkPlayer player = gamePlayer.GetComponent<NetworkPlayer>();
        if (player != null)
        {
            // Set spawn position
            if (NetworkGameManager.Instance != null)
            {
                Vector3 spawnPoint = NetworkGameManager.Instance.GetSpawnPoint();
                gamePlayer.transform.position = spawnPoint;
            }
        }
        
        return true;
    }
}

// Network Sync Helper
public class NetworkSync : NetworkBehaviour
{
    [SyncVar]
    public Vector3 syncPosition;
    
    [SyncVar]
    public Quaternion syncRotation;
    
    [SyncVar]
    public Vector3 syncVelocity;
    
    private Rigidbody rb;
    private float lerpRate = 15f;
    
    void Start()
    {
        rb = GetComponent<Rigidbody>();
    }
    
    void FixedUpdate()
    {
        TransmitPosition();
        LerpPosition();
    }
    
    void TransmitPosition()
    {
        if (isLocalPlayer)
        {
            syncPosition = transform.position;
            syncRotation = transform.rotation;
            if (rb != null)
                syncVelocity = rb.velocity;
        }
    }
    
    void LerpPosition()
    {
        if (!isLocalPlayer)
        {
            transform.position = Vector3.Lerp(transform.position, syncPosition, Time.fixedDeltaTime * lerpRate);
            transform.rotation = Quaternion.Lerp(transform.rotation, syncRotation, Time.fixedDeltaTime * lerpRate);
            
            if (rb != null)
                rb.velocity = syncVelocity;
        }
    }
}
```

## 🚀 AI/LLM Integration
- Generate networking protocols based on game requirements
- Automatically optimize network synchronization
- Create lag compensation algorithms

## 💡 Key Benefits
- Complete multiplayer framework
- Automatic player synchronization
- Server-client validation