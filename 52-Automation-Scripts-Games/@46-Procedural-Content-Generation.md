# @46-Procedural-Content-Generation

## 🎯 Core Concept
Automated procedural content generation system for creating dynamic levels, items, quests, and game environments.

## 🔧 Implementation

### Procedural Generation Manager
```csharp
using UnityEngine;
using System.Collections.Generic;
using System.Linq;

public class ProceduralGenerator : MonoBehaviour
{
    public static ProceduralGenerator Instance;
    
    [Header("Generation Settings")]
    public int randomSeed = 0;
    public bool useTimeSeed = false;
    public GenerationQuality quality = GenerationQuality.Medium;
    
    [Header("Level Generation")]
    public int levelWidth = 100;
    public int levelHeight = 100;
    public float noiseScale = 0.1f;
    public AnimationCurve heightCurve = AnimationCurve.Linear(0, 0, 1, 1);
    
    [Header("Content Density")]
    [Range(0f, 1f)] public float itemDensity = 0.1f;
    [Range(0f, 1f)] public float enemyDensity = 0.05f;
    [Range(0f, 1f)] public float structureDensity = 0.02f;
    
    private System.Random random;
    private Dictionary<BiomeType, BiomeData> biomes;
    private List<GameObject> generatedObjects;
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeGenerator();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void InitializeGenerator()
    {
        if (useTimeSeed)
        {
            randomSeed = (int)System.DateTime.Now.Ticks;
        }
        
        random = new System.Random(randomSeed);
        generatedObjects = new List<GameObject>();
        InitializeBiomes();
        
        Debug.Log($"Procedural Generator initialized with seed: {randomSeed}");
    }
    
    void InitializeBiomes()
    {
        biomes = new Dictionary<BiomeType, BiomeData>();
        
        // Forest biome
        biomes[BiomeType.Forest] = new BiomeData
        {
            name = "Forest",
            groundColor = new Color(0.2f, 0.4f, 0.1f),
            treeTypes = new string[] { "Pine", "Oak", "Birch" },
            treeDensity = 0.3f,
            enemyTypes = new string[] { "Wolf", "Bear", "Goblin" },
            itemTypes = new string[] { "Wood", "Berry", "Herb" }
        };
        
        // Desert biome
        biomes[BiomeType.Desert] = new BiomeData
        {
            name = "Desert",
            groundColor = new Color(0.8f, 0.7f, 0.3f),
            treeTypes = new string[] { "Cactus", "PalmTree" },
            treeDensity = 0.05f,
            enemyTypes = new string[] { "Scorpion", "Snake", "Bandit" },
            itemTypes = new string[] { "Sand", "Cactus Fruit", "Gems" }
        };
        
        // Mountain biome
        biomes[BiomeType.Mountain] = new BiomeData
        {
            name = "Mountain",
            groundColor = new Color(0.5f, 0.5f, 0.5f),
            treeTypes = new string[] { "Pine" },
            treeDensity = 0.1f,
            enemyTypes = new string[] { "Eagle", "Goat", "Troll" },
            itemTypes = new string[] { "Stone", "Iron", "Crystal" }
        };
        
        // Ocean biome
        biomes[BiomeType.Ocean] = new BiomeData
        {
            name = "Ocean",
            groundColor = new Color(0.1f, 0.3f, 0.7f),
            treeTypes = new string[] { },
            treeDensity = 0f,
            enemyTypes = new string[] { "Shark", "Jellyfish", "Pirate" },
            itemTypes = new string[] { "Fish", "Seaweed", "Pearl" }
        };
    }
    
    [ContextMenu("Generate Level")]
    public void GenerateLevel()
    {
        ClearGenerated();
        
        Debug.Log("Starting level generation...");
        
        // Generate terrain
        TerrainData terrainData = GenerateTerrain();
        
        // Generate biome map
        BiomeType[,] biomeMap = GenerateBiomeMap();
        
        // Generate objects based on biomes
        GenerateObjects(biomeMap, terrainData);
        
        // Generate structures
        GenerateStructures(biomeMap, terrainData);
        
        // Generate quests
        GenerateQuests();
        
        Debug.Log($"Level generation complete. Generated {generatedObjects.Count} objects.");
    }
    
    TerrainData GenerateTerrain()
    {
        TerrainData terrainData = new TerrainData();
        terrainData.heightmapResolution = levelWidth + 1;
        terrainData.size = new Vector3(levelWidth, 20, levelHeight);
        
        float[,] heights = new float[levelWidth + 1, levelHeight + 1];
        
        for (int x = 0; x <= levelWidth; x++)
        {
            for (int z = 0; z <= levelHeight; z++)
            {
                // Generate height using Perlin noise
                float noiseValue = Mathf.PerlinNoise(x * noiseScale, z * noiseScale);
                
                // Apply additional noise layers for complexity
                noiseValue += Mathf.PerlinNoise(x * noiseScale * 2f, z * noiseScale * 2f) * 0.5f;
                noiseValue += Mathf.PerlinNoise(x * noiseScale * 4f, z * noiseScale * 4f) * 0.25f;
                
                // Apply height curve for more control
                noiseValue = heightCurve.Evaluate(noiseValue);
                
                heights[x, z] = noiseValue;
            }
        }
        
        terrainData.SetHeights(0, 0, heights);
        
        // Create terrain GameObject
        GameObject terrainObject = Terrain.CreateTerrainGameObject(terrainData);
        terrainObject.name = "Generated_Terrain";
        generatedObjects.Add(terrainObject);
        
        return terrainData;
    }
    
    BiomeType[,] GenerateBiomeMap()
    {
        BiomeType[,] biomeMap = new BiomeType[levelWidth, levelHeight];
        
        // Generate biome regions using Voronoi diagram
        List<BiomeCenter> biomeCenters = GenerateBiomeCenters();
        
        for (int x = 0; x < levelWidth; x++)
        {
            for (int z = 0; z < levelHeight; z++)
            {
                BiomeCenter closestCenter = biomeCenters.OrderBy(center => 
                    Vector2.Distance(new Vector2(x, z), center.position)).First();
                
                biomeMap[x, z] = closestCenter.biomeType;
            }
        }
        
        return biomeMap;
    }
    
    List<BiomeCenter> GenerateBiomeCenters()
    {
        List<BiomeCenter> centers = new List<BiomeCenter>();
        int biomeCount = random.Next(3, 8); // 3-7 biomes per level
        
        BiomeType[] availableBiomes = System.Enum.GetValues(typeof(BiomeType)).Cast<BiomeType>().ToArray();
        
        for (int i = 0; i < biomeCount; i++)
        {
            BiomeCenter center = new BiomeCenter
            {
                position = new Vector2(
                    random.Next(0, levelWidth),
                    random.Next(0, levelHeight)
                ),
                biomeType = availableBiomes[random.Next(availableBiomes.Length)]
            };
            
            centers.Add(center);
        }
        
        return centers;
    }
    
    void GenerateObjects(BiomeType[,] biomeMap, TerrainData terrainData)
    {
        for (int x = 0; x < levelWidth; x += 2) // Skip every other position for performance
        {
            for (int z = 0; z < levelHeight; z += 2)
            {
                BiomeType biome = biomeMap[x, z];
                BiomeData biomeData = biomes[biome];
                
                Vector3 worldPosition = GetWorldPosition(x, z, terrainData);
                
                // Generate trees
                if (random.NextDouble() < biomeData.treeDensity)
                {
                    GenerateTree(worldPosition, biomeData);
                }
                
                // Generate items
                if (random.NextDouble() < itemDensity)
                {
                    GenerateItem(worldPosition, biomeData);
                }
                
                // Generate enemies
                if (random.NextDouble() < enemyDensity)
                {
                    GenerateEnemy(worldPosition, biomeData);
                }
            }
        }
    }
    
    void GenerateTree(Vector3 position, BiomeData biomeData)
    {
        if (biomeData.treeTypes.Length == 0) return;
        
        string treeType = biomeData.treeTypes[random.Next(biomeData.treeTypes.Length)];
        
        GameObject tree = CreatePrimitiveObject(PrimitiveType.Cylinder, position);
        tree.name = $"Tree_{treeType}";
        tree.transform.localScale = new Vector3(
            0.3f + (float)random.NextDouble() * 0.4f,
            2f + (float)random.NextDouble() * 3f,
            0.3f + (float)random.NextDouble() * 0.4f
        );
        
        // Add foliage
        GameObject foliage = CreatePrimitiveObject(PrimitiveType.Sphere, 
            position + Vector3.up * tree.transform.localScale.y);
        foliage.name = $"Foliage_{treeType}";
        foliage.transform.localScale = Vector3.one * (1f + (float)random.NextDouble());
        foliage.GetComponent<Renderer>().material.color = Color.green;
        foliage.transform.SetParent(tree.transform);
        
        generatedObjects.Add(tree);
    }
    
    void GenerateItem(Vector3 position, BiomeData biomeData)
    {
        if (biomeData.itemTypes.Length == 0) return;
        
        string itemType = biomeData.itemTypes[random.Next(biomeData.itemTypes.Length)];
        
        GameObject item = CreatePrimitiveObject(PrimitiveType.Cube, position + Vector3.up * 0.5f);
        item.name = $"Item_{itemType}";
        item.transform.localScale = Vector3.one * 0.3f;
        item.GetComponent<Renderer>().material.color = GetItemColor(itemType);
        
        // Add collectible component
        CollectibleItem collectible = item.AddComponent<CollectibleItem>();
        collectible.itemType = itemType;
        collectible.value = random.Next(1, 10);
        
        generatedObjects.Add(item);
    }
    
    void GenerateEnemy(Vector3 position, BiomeData biomeData)
    {
        if (biomeData.enemyTypes.Length == 0) return;
        
        string enemyType = biomeData.enemyTypes[random.Next(biomeData.enemyTypes.Length)];
        
        GameObject enemy = CreatePrimitiveObject(PrimitiveType.Capsule, position + Vector3.up);
        enemy.name = $"Enemy_{enemyType}";
        enemy.GetComponent<Renderer>().material.color = Color.red;
        
        // Add enemy AI component
        SimpleEnemyAI enemyAI = enemy.AddComponent<SimpleEnemyAI>();
        enemyAI.enemyType = enemyType;
        enemyAI.health = random.Next(50, 150);
        enemyAI.damage = random.Next(10, 30);
        
        generatedObjects.Add(enemy);
    }
    
    void GenerateStructures(BiomeType[,] biomeMap, TerrainData terrainData)
    {
        int structureCount = (int)(levelWidth * levelHeight * structureDensity);
        
        for (int i = 0; i < structureCount; i++)
        {
            int x = random.Next(5, levelWidth - 5);
            int z = random.Next(5, levelHeight - 5);
            
            Vector3 position = GetWorldPosition(x, z, terrainData);
            BiomeType biome = biomeMap[x, z];
            
            GenerateStructure(position, biome);
        }
    }
    
    void GenerateStructure(Vector3 position, BiomeType biome)
    {
        StructureType structureType = GetRandomStructureForBiome(biome);
        
        switch (structureType)
        {
            case StructureType.House:
                GenerateHouse(position);
                break;
            case StructureType.Tower:
                GenerateTower(position);
                break;
            case StructureType.Ruins:
                GenerateRuins(position);
                break;
            case StructureType.Camp:
                GenerateCamp(position);
                break;
        }
    }
    
    void GenerateHouse(Vector3 position)
    {
        GameObject house = CreatePrimitiveObject(PrimitiveType.Cube, position + Vector3.up * 1.5f);
        house.name = "Structure_House";
        house.transform.localScale = new Vector3(4f, 3f, 4f);
        house.GetComponent<Renderer>().material.color = new Color(0.6f, 0.4f, 0.2f);
        
        // Add roof
        GameObject roof = CreatePrimitiveObject(PrimitiveType.Cube, position + Vector3.up * 3.5f);
        roof.name = "Roof";
        roof.transform.localScale = new Vector3(5f, 1f, 5f);
        roof.GetComponent<Renderer>().material.color = Color.red;
        roof.transform.SetParent(house.transform);
        
        generatedObjects.Add(house);
    }
    
    void GenerateTower(Vector3 position)
    {
        GameObject tower = CreatePrimitiveObject(PrimitiveType.Cylinder, position + Vector3.up * 5f);
        tower.name = "Structure_Tower";
        tower.transform.localScale = new Vector3(2f, 10f, 2f);
        tower.GetComponent<Renderer>().material.color = Color.gray;
        
        generatedObjects.Add(tower);
    }
    
    void GenerateRuins(Vector3 position)
    {
        for (int i = 0; i < 3; i++)
        {
            Vector3 ruinPosition = position + new Vector3(
                (float)random.NextDouble() * 4f - 2f,
                0,
                (float)random.NextDouble() * 4f - 2f
            );
            
            GameObject ruin = CreatePrimitiveObject(PrimitiveType.Cube, ruinPosition + Vector3.up * 0.5f);
            ruin.name = "Structure_Ruin";
            ruin.transform.localScale = new Vector3(
                1f + (float)random.NextDouble(),
                0.5f + (float)random.NextDouble() * 2f,
                1f + (float)random.NextDouble()
            );
            ruin.GetComponent<Renderer>().material.color = new Color(0.4f, 0.4f, 0.4f);
            
            generatedObjects.Add(ruin);
        }
    }
    
    void GenerateCamp(Vector3 position)
    {
        // Central fire
        GameObject fire = CreatePrimitiveObject(PrimitiveType.Cylinder, position + Vector3.up * 0.2f);
        fire.name = "Campfire";
        fire.transform.localScale = new Vector3(0.8f, 0.4f, 0.8f);
        fire.GetComponent<Renderer>().material.color = Color.yellow;
        
        // Surrounding tents
        for (int i = 0; i < 3; i++)
        {
            float angle = i * 120f * Mathf.Deg2Rad;
            Vector3 tentPosition = position + new Vector3(
                Mathf.Cos(angle) * 3f,
                0,
                Mathf.Sin(angle) * 3f
            );
            
            GameObject tent = CreatePrimitiveObject(PrimitiveType.Cube, tentPosition + Vector3.up);
            tent.name = "Tent";
            tent.transform.localScale = new Vector3(1.5f, 2f, 1.5f);
            tent.GetComponent<Renderer>().material.color = new Color(0.3f, 0.5f, 0.3f);
            
            generatedObjects.Add(tent);
        }
        
        generatedObjects.Add(fire);
    }
    
    void GenerateQuests()
    {
        List<ProceduralQuest> quests = new List<ProceduralQuest>();
        int questCount = random.Next(3, 8);
        
        for (int i = 0; i < questCount; i++)
        {
            ProceduralQuest quest = GenerateRandomQuest();
            quests.Add(quest);
        }
        
        // Store quests in quest manager if available
        if (QuestManager.Instance != null)
        {
            foreach (var quest in quests)
            {
                QuestManager.Instance.AddGeneratedQuest(quest);
            }
        }
        
        Debug.Log($"Generated {quests.Count} procedural quests");
    }
    
    ProceduralQuest GenerateRandomQuest()
    {
        QuestType questType = (QuestType)random.Next(System.Enum.GetValues(typeof(QuestType)).Length);
        
        ProceduralQuest quest = new ProceduralQuest
        {
            id = System.Guid.NewGuid().ToString(),
            title = GenerateQuestTitle(questType),
            description = GenerateQuestDescription(questType),
            questType = questType,
            targetCount = random.Next(1, 10),
            experienceReward = random.Next(100, 500),
            currencyReward = random.Next(50, 200),
            timeLimit = random.NextDouble() < 0.3 ? random.Next(300, 1800) : -1
        };
        
        return quest;
    }
    
    string GenerateQuestTitle(QuestType questType)
    {
        switch (questType)
        {
            case QuestType.Kill:
                return $"Eliminate {random.Next(3, 15)} enemies";
            case QuestType.Collect:
                return $"Gather {random.Next(5, 20)} resources";
            case QuestType.Deliver:
                return "Deliver important package";
            case QuestType.Explore:
                return "Explore unknown territory";
            default:
                return "Complete the objective";
        }
    }
    
    string GenerateQuestDescription(QuestType questType)
    {
        switch (questType)
        {
            case QuestType.Kill:
                return "The area has become dangerous. Clear out the hostile creatures.";
            case QuestType.Collect:
                return "We need supplies for the settlement. Gather the required materials.";
            case QuestType.Deliver:
                return "This package must reach its destination safely and quickly.";
            case QuestType.Explore:
                return "Scout the area and report back with your findings.";
            default:
                return "Complete the given objective to earn your reward.";
        }
    }
    
    Vector3 GetWorldPosition(int x, int z, TerrainData terrainData)
    {
        float height = terrainData.GetHeight(x, z);
        return new Vector3(x, height, z);
    }
    
    GameObject CreatePrimitiveObject(PrimitiveType type, Vector3 position)
    {
        GameObject obj = GameObject.CreatePrimitive(type);
        obj.transform.position = position;
        return obj;
    }
    
    Color GetItemColor(string itemType)
    {
        switch (itemType.ToLower())
        {
            case "wood": return new Color(0.4f, 0.2f, 0.1f);
            case "stone": return Color.gray;
            case "iron": return new Color(0.3f, 0.3f, 0.3f);
            case "gold": return Color.yellow;
            case "gem": return Color.magenta;
            case "herb": return Color.green;
            case "berry": return Color.red;
            case "fish": return Color.blue;
            default: return Color.white;
        }
    }
    
    StructureType GetRandomStructureForBiome(BiomeType biome)
    {
        switch (biome)
        {
            case BiomeType.Forest:
                return random.NextDouble() < 0.5 ? StructureType.House : StructureType.Camp;
            case BiomeType.Desert:
                return random.NextDouble() < 0.6 ? StructureType.Ruins : StructureType.Camp;
            case BiomeType.Mountain:
                return random.NextDouble() < 0.7 ? StructureType.Tower : StructureType.Ruins;
            case BiomeType.Ocean:
                return StructureType.Ruins;
            default:
                return StructureType.House;
        }
    }
    
    public void ClearGenerated()
    {
        foreach (GameObject obj in generatedObjects)
        {
            if (obj != null)
            {
                DestroyImmediate(obj);
            }
        }
        
        generatedObjects.Clear();
        Debug.Log("Cleared all generated content");
    }
    
    public void SaveGeneratedLevel(string fileName)
    {
        LevelData levelData = new LevelData
        {
            seed = randomSeed,
            width = levelWidth,
            height = levelHeight,
            objectCount = generatedObjects.Count,
            generatedAt = System.DateTime.Now.ToString()
        };
        
        string json = JsonUtility.ToJson(levelData, true);
        System.IO.File.WriteAllText($"{fileName}.json", json);
        
        Debug.Log($"Level data saved to {fileName}.json");
    }
}

// Supporting data structures
public enum BiomeType { Forest, Desert, Mountain, Ocean }
public enum StructureType { House, Tower, Ruins, Camp }
public enum QuestType { Kill, Collect, Deliver, Explore }
public enum GenerationQuality { Low, Medium, High, Ultra }

[System.Serializable]
public class BiomeData
{
    public string name;
    public Color groundColor;
    public string[] treeTypes;
    public float treeDensity;
    public string[] enemyTypes;
    public string[] itemTypes;
}

[System.Serializable]
public class BiomeCenter
{
    public Vector2 position;
    public BiomeType biomeType;
}

[System.Serializable]
public class ProceduralQuest
{
    public string id;
    public string title;
    public string description;
    public QuestType questType;
    public int targetCount;
    public int experienceReward;
    public int currencyReward;
    public int timeLimit;
}

[System.Serializable]
public class LevelData
{
    public int seed;
    public int width;
    public int height;
    public int objectCount;
    public string generatedAt;
}

// Components for generated objects
public class CollectibleItem : MonoBehaviour
{
    public string itemType;
    public int value;
    
    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            // Collect item logic
            Debug.Log($"Collected {itemType} worth {value}");
            Destroy(gameObject);
        }
    }
}

public class SimpleEnemyAI : MonoBehaviour
{
    public string enemyType;
    public int health;
    public int damage;
    public float detectionRange = 10f;
    
    private Transform player;
    
    void Start()
    {
        player = GameObject.FindGameObjectWithTag("Player")?.transform;
    }
    
    void Update()
    {
        if (player != null)
        {
            float distance = Vector3.Distance(transform.position, player.position);
            
            if (distance < detectionRange)
            {
                // Simple chase behavior
                Vector3 direction = (player.position - transform.position).normalized;
                transform.position += direction * 2f * Time.deltaTime;
                transform.LookAt(player);
            }
        }
    }
}
```

## 🚀 AI/LLM Integration
- Generate unique quest narratives and dialogue
- Create balanced item statistics and enemy configurations
- Produce diverse biome compositions and structure layouts

## 💡 Key Benefits
- Dynamic level generation
- Infinite content variety
- Automated quest and item creation