# @33-Procedural-Content-Generator

## 🎯 Core Concept
Automated procedural content generation for infinite worlds, dungeons, and game assets.

## 🔧 Implementation

### Procedural Generation Framework
```csharp
using UnityEngine;
using System.Collections.Generic;

public class ProceduralGenerator : MonoBehaviour
{
    [Header("Generation Settings")]
    public int seed = 12345;
    public int chunkSize = 16;
    public int viewDistance = 3;
    public GameObject[] tilePrefabs;
    public GameObject[] decorationPrefabs;
    
    [Header("Noise Settings")]
    public float noiseScale = 0.1f;
    public int octaves = 4;
    public float persistence = 0.5f;
    public float lacunarity = 2f;
    
    private Dictionary<Vector2Int, TerrainChunk> loadedChunks;
    private Transform player;
    private Vector2Int currentChunkCoord;
    
    void Start()
    {
        Random.InitState(seed);
        loadedChunks = new Dictionary<Vector2Int, TerrainChunk>();
        player = FindObjectOfType<Camera>().transform;
        
        GenerateInitialChunks();
    }
    
    void Update()
    {
        Vector2Int playerChunkCoord = GetChunkCoordFromPosition(player.position);
        
        if (playerChunkCoord != currentChunkCoord)
        {
            currentChunkCoord = playerChunkCoord;
            UpdateChunks();
        }
    }
    
    void GenerateInitialChunks()
    {
        currentChunkCoord = GetChunkCoordFromPosition(player.position);
        
        for (int x = -viewDistance; x <= viewDistance; x++)
        {
            for (int z = -viewDistance; z <= viewDistance; z++)
            {
                Vector2Int chunkCoord = new Vector2Int(currentChunkCoord.x + x, currentChunkCoord.y + z);
                GenerateChunk(chunkCoord);
            }
        }
    }
    
    void UpdateChunks()
    {
        HashSet<Vector2Int> chunksToKeep = new HashSet<Vector2Int>();
        
        // Mark chunks to keep
        for (int x = -viewDistance; x <= viewDistance; x++)
        {
            for (int z = -viewDistance; z <= viewDistance; z++)
            {
                Vector2Int chunkCoord = new Vector2Int(currentChunkCoord.x + x, currentChunkCoord.y + z);
                chunksToKeep.Add(chunkCoord);
                
                if (!loadedChunks.ContainsKey(chunkCoord))
                {
                    GenerateChunk(chunkCoord);
                }
            }
        }
        
        // Remove distant chunks
        List<Vector2Int> chunksToRemove = new List<Vector2Int>();
        foreach (var kvp in loadedChunks)
        {
            if (!chunksToKeep.Contains(kvp.Key))
            {
                chunksToRemove.Add(kvp.Key);
            }
        }
        
        foreach (var coord in chunksToRemove)
        {
            DestroyChunk(coord);
        }
    }
    
    void GenerateChunk(Vector2Int chunkCoord)
    {
        GameObject chunkObject = new GameObject($"Chunk_{chunkCoord.x}_{chunkCoord.y}");
        chunkObject.transform.position = new Vector3(chunkCoord.x * chunkSize, 0, chunkCoord.y * chunkSize);
        
        TerrainChunk chunk = new TerrainChunk();
        chunk.chunkObject = chunkObject;
        chunk.coordinate = chunkCoord;
        
        GenerateTerrainForChunk(chunk);
        loadedChunks[chunkCoord] = chunk;
    }
    
    void GenerateTerrainForChunk(TerrainChunk chunk)
    {
        for (int x = 0; x < chunkSize; x++)
        {
            for (int z = 0; z < chunkSize; z++)
            {
                Vector3 worldPos = chunk.chunkObject.transform.position + new Vector3(x, 0, z);
                float height = GetHeightAtPosition(worldPos.x, worldPos.z);
                
                // Generate terrain tile
                GameObject tilePrefab = SelectTilePrefab(height);
                if (tilePrefab != null)
                {
                    Vector3 tilePosition = new Vector3(worldPos.x, height, worldPos.z);
                    GameObject tile = Instantiate(tilePrefab, tilePosition, Quaternion.identity, chunk.chunkObject.transform);
                    tile.name = $"Tile_{x}_{z}";
                }
                
                // Generate decorations
                if (ShouldPlaceDecoration(worldPos.x, worldPos.z))
                {
                    GameObject decorationPrefab = decorationPrefabs[Random.Range(0, decorationPrefabs.Length)];
                    Vector3 decorationPosition = new Vector3(worldPos.x, height + 1, worldPos.z);
                    GameObject decoration = Instantiate(decorationPrefab, decorationPosition, 
                        Quaternion.Euler(0, Random.Range(0, 360), 0), chunk.chunkObject.transform);
                    decoration.name = $"Decoration_{x}_{z}";
                }
            }
        }
    }
    
    float GetHeightAtPosition(float x, float z)
    {
        float height = 0;
        float amplitude = 1;
        float frequency = noiseScale;
        
        for (int i = 0; i < octaves; i++)
        {
            height += Mathf.PerlinNoise(x * frequency + seed, z * frequency + seed) * amplitude;
            amplitude *= persistence;
            frequency *= lacunarity;
        }
        
        return height * 10f; // Scale height
    }
    
    GameObject SelectTilePrefab(float height)
    {
        if (tilePrefabs.Length == 0) return null;
        
        // Select tile based on height
        if (height < 2f)
            return tilePrefabs[0]; // Water/Sand
        else if (height < 5f)
            return tilePrefabs[Mathf.Min(1, tilePrefabs.Length - 1)]; // Grass
        else if (height < 8f)
            return tilePrefabs[Mathf.Min(2, tilePrefabs.Length - 1)]; // Stone
        else
            return tilePrefabs[Mathf.Min(3, tilePrefabs.Length - 1)]; // Snow
    }
    
    bool ShouldPlaceDecoration(float x, float z)
    {
        float decorationNoise = Mathf.PerlinNoise(x * 0.05f + seed + 1000, z * 0.05f + seed + 1000);
        return decorationNoise > 0.6f && Random.value > 0.7f;
    }
    
    void DestroyChunk(Vector2Int chunkCoord)
    {
        if (loadedChunks.ContainsKey(chunkCoord))
        {
            TerrainChunk chunk = loadedChunks[chunkCoord];
            if (chunk.chunkObject != null)
            {
                Destroy(chunk.chunkObject);
            }
            loadedChunks.Remove(chunkCoord);
        }
    }
    
    Vector2Int GetChunkCoordFromPosition(Vector3 position)
    {
        return new Vector2Int(
            Mathf.FloorToInt(position.x / chunkSize),
            Mathf.FloorToInt(position.z / chunkSize)
        );
    }
}

public class TerrainChunk
{
    public GameObject chunkObject;
    public Vector2Int coordinate;
}

public class DungeonGenerator : MonoBehaviour
{
    [Header("Dungeon Settings")]
    public int dungeonWidth = 50;
    public int dungeonHeight = 50;
    public int roomCount = 10;
    public int minRoomSize = 5;
    public int maxRoomSize = 15;
    
    [Header("Prefabs")]
    public GameObject floorPrefab;
    public GameObject wallPrefab;
    public GameObject doorPrefab;
    
    private bool[,] dungeonGrid;
    private List<Room> rooms;
    
    [ContextMenu("Generate Dungeon")]
    public void GenerateDungeon()
    {
        ClearExistingDungeon();
        InitializeDungeon();
        GenerateRooms();
        GenerateCorridors();
        PlaceTiles();
    }
    
    void ClearExistingDungeon()
    {
        foreach (Transform child in transform)
        {
            DestroyImmediate(child.gameObject);
        }
    }
    
    void InitializeDungeon()
    {
        dungeonGrid = new bool[dungeonWidth, dungeonHeight];
        rooms = new List<Room>();
        
        // Initialize all cells as walls (false)
        for (int x = 0; x < dungeonWidth; x++)
        {
            for (int y = 0; y < dungeonHeight; y++)
            {
                dungeonGrid[x, y] = false;
            }
        }
    }
    
    void GenerateRooms()
    {
        for (int i = 0; i < roomCount; i++)
        {
            int attempts = 0;
            bool roomPlaced = false;
            
            while (!roomPlaced && attempts < 100)
            {
                int roomWidth = Random.Range(minRoomSize, maxRoomSize + 1);
                int roomHeight = Random.Range(minRoomSize, maxRoomSize + 1);
                int roomX = Random.Range(1, dungeonWidth - roomWidth - 1);
                int roomY = Random.Range(1, dungeonHeight - roomHeight - 1);
                
                Room newRoom = new Room(roomX, roomY, roomWidth, roomHeight);
                
                if (!RoomOverlaps(newRoom))
                {
                    rooms.Add(newRoom);
                    CarveRoom(newRoom);
                    roomPlaced = true;
                }
                
                attempts++;
            }
        }
    }
    
    bool RoomOverlaps(Room newRoom)
    {
        foreach (Room existingRoom in rooms)
        {
            if (newRoom.Overlaps(existingRoom))
                return true;
        }
        return false;
    }
    
    void CarveRoom(Room room)
    {
        for (int x = room.x; x < room.x + room.width; x++)
        {
            for (int y = room.y; y < room.y + room.height; y++)
            {
                dungeonGrid[x, y] = true; // true = floor
            }
        }
    }
    
    void GenerateCorridors()
    {
        for (int i = 0; i < rooms.Count - 1; i++)
        {
            Vector2Int roomACenter = rooms[i].GetCenter();
            Vector2Int roomBCenter = rooms[i + 1].GetCenter();
            
            // Create L-shaped corridor
            CarveCorridor(roomACenter.x, roomACenter.y, roomBCenter.x, roomACenter.y);
            CarveCorridor(roomBCenter.x, roomACenter.y, roomBCenter.x, roomBCenter.y);
        }
    }
    
    void CarveCorridor(int x1, int y1, int x2, int y2)
    {
        int startX = Mathf.Min(x1, x2);
        int endX = Mathf.Max(x1, x2);
        int startY = Mathf.Min(y1, y2);
        int endY = Mathf.Max(y1, y2);
        
        for (int x = startX; x <= endX; x++)
        {
            for (int y = startY; y <= endY; y++)
            {
                if (x >= 0 && x < dungeonWidth && y >= 0 && y < dungeonHeight)
                {
                    dungeonGrid[x, y] = true;
                }
            }
        }
    }
    
    void PlaceTiles()
    {
        for (int x = 0; x < dungeonWidth; x++)
        {
            for (int y = 0; y < dungeonHeight; y++)
            {
                Vector3 position = new Vector3(x, 0, y);
                
                if (dungeonGrid[x, y]) // Floor
                {
                    if (floorPrefab != null)
                    {
                        Instantiate(floorPrefab, position, Quaternion.identity, transform);
                    }
                }
                else // Wall
                {
                    if (wallPrefab != null && IsWallPosition(x, y))
                    {
                        Instantiate(wallPrefab, position + Vector3.up * 0.5f, Quaternion.identity, transform);
                    }
                }
            }
        }
    }
    
    bool IsWallPosition(int x, int y)
    {
        // Check if this wall position is adjacent to a floor
        for (int dx = -1; dx <= 1; dx++)
        {
            for (int dy = -1; dy <= 1; dy++)
            {
                int checkX = x + dx;
                int checkY = y + dy;
                
                if (checkX >= 0 && checkX < dungeonWidth && checkY >= 0 && checkY < dungeonHeight)
                {
                    if (dungeonGrid[checkX, checkY])
                        return true;
                }
            }
        }
        return false;
    }
}

[System.Serializable]
public class Room
{
    public int x, y, width, height;
    
    public Room(int x, int y, int width, int height)
    {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
    }
    
    public Vector2Int GetCenter()
    {
        return new Vector2Int(x + width / 2, y + height / 2);
    }
    
    public bool Overlaps(Room other)
    {
        return x < other.x + other.width + 1 &&
               x + width + 1 > other.x &&
               y < other.y + other.height + 1 &&
               y + height + 1 > other.y;
    }
}

// Procedural Name Generator
public static class NameGenerator
{
    private static string[] prefixes = { "Dark", "Ancient", "Lost", "Forgotten", "Hidden", "Sacred", "Cursed", "Golden" };
    private static string[] suffixes = { "Temple", "Ruins", "Cavern", "Sanctum", "Tomb", "Chamber", "Hall", "Fortress" };
    
    public static string GenerateDungeonName()
    {
        string prefix = prefixes[Random.Range(0, prefixes.Length)];
        string suffix = suffixes[Random.Range(0, suffixes.Length)];
        return $"{prefix} {suffix}";
    }
    
    public static string GenerateItemName()
    {
        string[] adjectives = { "Sharp", "Ancient", "Blessed", "Enchanted", "Legendary", "Mystical" };
        string[] items = { "Sword", "Shield", "Bow", "Staff", "Ring", "Amulet" };
        
        string adjective = adjectives[Random.Range(0, adjectives.Length)];
        string item = items[Random.Range(0, items.Length)];
        return $"{adjective} {item}";
    }
}
```

## 🚀 AI/LLM Integration
- Generate procedural content rules from descriptions
- Create balanced procedural algorithms
- Generate themed content automatically

## 💡 Key Benefits
- Infinite world generation
- Automated dungeon creation
- Dynamic content variety