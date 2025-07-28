# @29-Dialogue-System-Builder

## 🎯 Core Concept
Automated dialogue system with branching conversations, character management, and localization support.

## 🔧 Implementation

### Dialogue Framework
```csharp
using UnityEngine;
using System.Collections.Generic;

[CreateAssetMenu(fileName = "New Dialogue", menuName = "Dialogue/Dialogue Data")]
public class DialogueData : ScriptableObject
{
    public string dialogueId;
    public DialogueNode[] nodes;
    public Character[] characters;
}

[System.Serializable]
public class DialogueNode
{
    public string nodeId;
    public string characterId;
    public string text;
    public DialogueChoice[] choices;
    public string nextNodeId;
    public DialogueCondition[] conditions;
    public DialogueAction[] actions;
}

[System.Serializable]
public class DialogueChoice
{
    public string choiceText;
    public string targetNodeId;
    public DialogueCondition[] conditions;
}

[System.Serializable]
public class Character
{
    public string characterId;
    public string displayName;
    public Sprite portrait;
    public Color textColor = Color.white;
}

public class DialogueManager : MonoBehaviour
{
    public static DialogueManager Instance;
    
    [Header("UI References")]
    public GameObject dialoguePanel;
    public UnityEngine.UI.Text characterNameText;
    public UnityEngine.UI.Text dialogueText;
    public UnityEngine.UI.Image characterPortrait;
    public Transform choicesParent;
    public GameObject choiceButtonPrefab;
    
    [Header("Settings")]
    public float typewriterSpeed = 50f;
    public AudioClip typingSound;
    
    private DialogueData currentDialogue;
    private DialogueNode currentNode;
    private bool isTyping;
    private Coroutine typingCoroutine;
    
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
    
    public void StartDialogue(DialogueData dialogue)
    {
        currentDialogue = dialogue;
        dialoguePanel.SetActive(true);
        
        // Find starting node
        DialogueNode startNode = System.Array.Find(dialogue.nodes, node => node.nodeId == "start");
        if (startNode == null && dialogue.nodes.Length > 0)
        {
            startNode = dialogue.nodes[0];
        }
        
        if (startNode != null)
        {
            ShowNode(startNode);
        }
    }
    
    void ShowNode(DialogueNode node)
    {
        currentNode = node;
        
        // Check conditions
        if (!CheckConditions(node.conditions))
        {
            // Skip to next node if conditions not met
            if (!string.IsNullOrEmpty(node.nextNodeId))
            {
                DialogueNode nextNode = GetNodeById(node.nextNodeId);
                if (nextNode != null)
                {
                    ShowNode(nextNode);
                    return;
                }
            }
        }
        
        // Get character data
        Character character = GetCharacterById(node.characterId);
        if (character != null)
        {
            characterNameText.text = character.displayName;
            characterPortrait.sprite = character.portrait;
            dialogueText.color = character.textColor;
        }
        
        // Clear previous choices
        ClearChoices();
        
        // Start typing effect
        if (typingCoroutine != null)
        {
            StopCoroutine(typingCoroutine);
        }
        typingCoroutine = StartCoroutine(TypeText(node.text));
        
        // Execute actions
        ExecuteActions(node.actions);
    }
    
    System.Collections.IEnumerator TypeText(string text)
    {
        isTyping = true;
        dialogueText.text = "";
        
        foreach (char letter in text.ToCharArray())
        {
            dialogueText.text += letter;
            
            if (typingSound != null)
            {
                AudioSource.PlayClipAtPoint(typingSound, Camera.main.transform.position, 0.1f);
            }
            
            yield return new WaitForSeconds(1f / typewriterSpeed);
        }
        
        isTyping = false;
        ShowChoicesOrContinue();
    }
    
    void ShowChoicesOrContinue()
    {
        if (currentNode.choices != null && currentNode.choices.Length > 0)
        {
            ShowChoices();
        }
        else if (!string.IsNullOrEmpty(currentNode.nextNodeId))
        {
            // Auto-continue to next node
            Invoke(nameof(ContinueToNextNode), 1f);
        }
        else
        {
            // End dialogue
            EndDialogue();
        }
    }
    
    void ShowChoices()
    {
        foreach (var choice in currentNode.choices)
        {
            if (CheckConditions(choice.conditions))
            {
                GameObject choiceButton = Instantiate(choiceButtonPrefab, choicesParent);
                UnityEngine.UI.Button button = choiceButton.GetComponent<UnityEngine.UI.Button>();
                UnityEngine.UI.Text buttonText = choiceButton.GetComponentInChildren<UnityEngine.UI.Text>();
                
                buttonText.text = choice.choiceText;
                
                string targetId = choice.targetNodeId;
                button.onClick.AddListener(() => OnChoiceSelected(targetId));
            }
        }
    }
    
    void OnChoiceSelected(string targetNodeId)
    {
        ClearChoices();
        
        DialogueNode targetNode = GetNodeById(targetNodeId);
        if (targetNode != null)
        {
            ShowNode(targetNode);
        }
        else
        {
            EndDialogue();
        }
    }
    
    void ContinueToNextNode()
    {
        DialogueNode nextNode = GetNodeById(currentNode.nextNodeId);
        if (nextNode != null)
        {
            ShowNode(nextNode);
        }
        else
        {
            EndDialogue();
        }
    }
    
    void ClearChoices()
    {
        foreach (Transform child in choicesParent)
        {
            Destroy(child.gameObject);
        }
    }
    
    void EndDialogue()
    {
        dialoguePanel.SetActive(false);
        currentDialogue = null;
        currentNode = null;
    }
    
    DialogueNode GetNodeById(string nodeId)
    {
        return System.Array.Find(currentDialogue.nodes, node => node.nodeId == nodeId);
    }
    
    Character GetCharacterById(string characterId)
    {
        return System.Array.Find(currentDialogue.characters, character => character.characterId == characterId);
    }
    
    bool CheckConditions(DialogueCondition[] conditions)
    {
        if (conditions == null || conditions.Length == 0) return true;
        
        foreach (var condition in conditions)
        {
            if (!EvaluateCondition(condition))
                return false;
        }
        
        return true;
    }
    
    bool EvaluateCondition(DialogueCondition condition)
    {
        // Implement condition evaluation logic
        // Examples: quest completion, item possession, variable values
        return true; // Placeholder
    }
    
    void ExecuteActions(DialogueAction[] actions)
    {
        if (actions == null) return;
        
        foreach (var action in actions)
        {
            ExecuteAction(action);
        }
    }
    
    void ExecuteAction(DialogueAction action)
    {
        // Implement action execution logic
        // Examples: give items, start quests, change variables
        Debug.Log($"Executing action: {action.actionType}");
    }
    
    void Update()
    {
        if (dialoguePanel.activeInHierarchy && Input.GetKeyDown(KeyCode.Space))
        {
            if (isTyping)
            {
                // Skip typing animation
                if (typingCoroutine != null)
                {
                    StopCoroutine(typingCoroutine);
                }
                dialogueText.text = currentNode.text;
                isTyping = false;
                ShowChoicesOrContinue();
            }
        }
    }
}

[System.Serializable]
public class DialogueCondition
{
    public string conditionType;
    public string parameter;
    public string value;
}

[System.Serializable]
public class DialogueAction
{
    public string actionType;
    public string parameter;
    public string value;
}
```

## 🚀 AI/LLM Integration
- Generate dialogue content from character descriptions
- Create branching conversation trees automatically
- Localize dialogue text for multiple languages

## 💡 Key Benefits
- Complete dialogue system with branching
- Character management and portraits
- Conditions and actions support