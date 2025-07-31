# @28-Inventory-System-Generator

## 🎯 Core Concept
Automated inventory system creation with item management, drag-drop, and persistence.

## 🔧 Implementation

### Inventory Framework
```csharp
using UnityEngine;
using System.Collections.Generic;

[CreateAssetMenu(fileName = "New Item", menuName = "Inventory/Item")]
public class InventoryItem : ScriptableObject
{
    public string itemName;
    public string description;
    public Sprite icon;
    public ItemType itemType;
    public ItemRarity rarity;
    public bool isStackable = true;
    public int maxStackSize = 99;
    public int value;
    public float weight;
}

public enum ItemType
{
    Weapon,
    Armor,
    Consumable,
    Material,
    Quest,
    Misc
}

public enum ItemRarity
{
    Common,
    Uncommon,
    Rare,
    Epic,
    Legendary
}

[System.Serializable]
public class InventorySlot
{
    public InventoryItem item;
    public int quantity;
    
    public bool IsEmpty => item == null || quantity <= 0;
    public bool IsFull => item != null && quantity >= item.maxStackSize;
    
    public bool CanAddItem(InventoryItem newItem, int amount)
    {
        if (IsEmpty) return true;
        if (item == newItem && item.isStackable)
        {
            return quantity + amount <= item.maxStackSize;
        }
        return false;
    }
    
    public void AddItem(InventoryItem newItem, int amount)
    {
        if (IsEmpty)
        {
            item = newItem;
            quantity = amount;
        }
        else if (item == newItem && item.isStackable)
        {
            quantity = Mathf.Min(quantity + amount, item.maxStackSize);
        }
    }
    
    public void RemoveItem(int amount)
    {
        quantity -= amount;
        if (quantity <= 0)
        {
            item = null;
            quantity = 0;
        }
    }
    
    public void Clear()
    {
        item = null;
        quantity = 0;
    }
}

public class InventoryManager : MonoBehaviour
{
    public static InventoryManager Instance;
    
    [Header("Inventory Settings")]
    public int inventorySize = 20;
    public float maxWeight = 100f;
    
    private List<InventorySlot> inventory;
    private float currentWeight;
    
    public System.Action<InventorySlot, int> OnItemAdded;
    public System.Action<InventorySlot, int> OnItemRemoved;
    public System.Action OnInventoryChanged;
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeInventory();
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void InitializeInventory()
    {
        inventory = new List<InventorySlot>();
        for (int i = 0; i < inventorySize; i++)
        {
            inventory.Add(new InventorySlot());
        }
        
        LoadInventory();
    }
    
    public bool AddItem(InventoryItem item, int quantity = 1)
    {
        if (item == null || quantity <= 0) return false;
        
        float weightToAdd = item.weight * quantity;
        if (currentWeight + weightToAdd > maxWeight) return false;
        
        int remainingQuantity = quantity;
        
        // Try to stack with existing items first
        if (item.isStackable)
        {
            for (int i = 0; i < inventory.Count && remainingQuantity > 0; i++)
            {
                if (inventory[i].item == item && !inventory[i].IsFull)
                {
                    int spaceAvailable = item.maxStackSize - inventory[i].quantity;
                    int amountToAdd = Mathf.Min(remainingQuantity, spaceAvailable);
                    
                    inventory[i].AddItem(item, amountToAdd);
                    remainingQuantity -= amountToAdd;
                    currentWeight += item.weight * amountToAdd;
                    
                    OnItemAdded?.Invoke(inventory[i], i);
                }
            }
        }
        
        // Add to empty slots
        for (int i = 0; i < inventory.Count && remainingQuantity > 0; i++)
        {
            if (inventory[i].IsEmpty)
            {
                int amountToAdd = item.isStackable ? 
                    Mathf.Min(remainingQuantity, item.maxStackSize) : 1;
                
                inventory[i].AddItem(item, amountToAdd);
                remainingQuantity -= amountToAdd;
                currentWeight += item.weight * amountToAdd;
                
                OnItemAdded?.Invoke(inventory[i], i);
            }
        }
        
        OnInventoryChanged?.Invoke();
        SaveInventory();
        
        return remainingQuantity == 0;
    }
    
    public bool RemoveItem(InventoryItem item, int quantity = 1)
    {
        if (item == null || quantity <= 0) return false;
        
        int totalAvailable = GetItemCount(item);
        if (totalAvailable < quantity) return false;
        
        int remainingToRemove = quantity;
        
        for (int i = 0; i < inventory.Count && remainingToRemove > 0; i++)
        {
            if (inventory[i].item == item)
            {
                int amountToRemove = Mathf.Min(remainingToRemove, inventory[i].quantity);
                inventory[i].RemoveItem(amountToRemove);
                remainingToRemove -= amountToRemove;
                currentWeight -= item.weight * amountToRemove;
                
                OnItemRemoved?.Invoke(inventory[i], i);
            }
        }
        
        OnInventoryChanged?.Invoke();
        SaveInventory();
        
        return true;
    }
    
    public int GetItemCount(InventoryItem item)
    {
        int count = 0;
        foreach (var slot in inventory)
        {
            if (slot.item == item)
                count += slot.quantity;
        }
        return count;
    }
    
    public bool HasItem(InventoryItem item, int quantity = 1)
    {
        return GetItemCount(item) >= quantity;
    }
    
    public InventorySlot GetSlot(int index)
    {
        return index >= 0 && index < inventory.Count ? inventory[index] : null;
    }
    
    public void SwapSlots(int index1, int index2)
    {
        if (index1 < 0 || index1 >= inventory.Count || 
            index2 < 0 || index2 >= inventory.Count) return;
        
        var temp = inventory[index1];
        inventory[index1] = inventory[index2];
        inventory[index2] = temp;
        
        OnInventoryChanged?.Invoke();
        SaveInventory();
    }
    
    public void SortInventory()
    {
        inventory.Sort((slot1, slot2) =>
        {
            if (slot1.IsEmpty && slot2.IsEmpty) return 0;
            if (slot1.IsEmpty) return 1;
            if (slot2.IsEmpty) return -1;
            
            int typeCompare = slot1.item.itemType.CompareTo(slot2.item.itemType);
            if (typeCompare != 0) return typeCompare;
            
            int rarityCompare = slot2.item.rarity.CompareTo(slot1.item.rarity);
            if (rarityCompare != 0) return rarityCompare;
            
            return string.Compare(slot1.item.itemName, slot2.item.itemName);
        });
        
        OnInventoryChanged?.Invoke();
        SaveInventory();
    }
    
    void SaveInventory()
    {
        InventorySaveData saveData = new InventorySaveData();
        saveData.slots = new List<SlotSaveData>();
        
        foreach (var slot in inventory)
        {
            saveData.slots.Add(new SlotSaveData
            {
                itemName = slot.item?.name ?? "",
                quantity = slot.quantity
            });
        }
        
        string json = JsonUtility.ToJson(saveData);
        PlayerPrefs.SetString("InventoryData", json);
        PlayerPrefs.Save();
    }
    
    void LoadInventory()
    {
        string json = PlayerPrefs.GetString("InventoryData", "");
        if (string.IsNullOrEmpty(json)) return;
        
        InventorySaveData saveData = JsonUtility.FromJson<InventorySaveData>(json);
        
        for (int i = 0; i < saveData.slots.Count && i < inventory.Count; i++)
        {
            var slotData = saveData.slots[i];
            if (!string.IsNullOrEmpty(slotData.itemName))
            {
                InventoryItem item = Resources.Load<InventoryItem>($"Items/{slotData.itemName}");
                if (item != null)
                {
                    inventory[i].AddItem(item, slotData.quantity);
                    currentWeight += item.weight * slotData.quantity;
                }
            }
        }
    }
    
    public float GetCurrentWeight() => currentWeight;
    public float GetWeightPercentage() => currentWeight / maxWeight;
    public bool IsOverweight() => currentWeight > maxWeight;
}

[System.Serializable]
public class InventorySaveData
{
    public List<SlotSaveData> slots;
}

[System.Serializable]
public class SlotSaveData
{
    public string itemName;
    public int quantity;
}
```

## 🚀 AI/LLM Integration
- Generate item data from descriptions
- Create balanced item statistics
- Automatically organize inventory layouts

## 💡 Key Benefits
- Complete inventory management system
- Automatic save/load functionality
- Weight and stacking mechanics