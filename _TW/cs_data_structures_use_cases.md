# 🧠 C# Data Structures: When to Use Each (with Unity/Game Dev Examples)



## ==Summary Table==

| Data Structure    | Use Case                                 | Unity/Game Example                                   |
| ----------------- | ---------------------------------------- | ---------------------------------------------------- |
| ==Array==         | ==Fixed==-size, fast indexing            | ==Spawn points, animation frames==                   |
| ==List==          | ==Dynamic== size, index access           | ==NPC list==, ==raycasts==, mesh data                |
| ==LinkedList==    | Fast insert/delete from ==middle==       | ==Turn queues==, level editor undo chain             |
| ==Stack==         | LIFO, ==backtracking==                   | ==Object pool==, game state machine                  |
| ==Queue==         | FIFO, ==orderly== processing             | ==Object pool==, ==turn manager==                    |
| ==Dictionary==    | ==Key==-based lookup                     | ==Prefab lookup==, ==input mapping==                 |
| ==HashSet==       | ==Unique== values, fast existence checks | Collision tracking, ==explored locations== node sets |
| ==SortedSet==     | ==Unique + sorted==                      | ==Leaderboards==, sorted enemy waves                 |
| ==PriorityQueue== | Min/Max ==priority== retrieval           | A* pathfinding, ==AI decision priority==             |
|                   |                                          |                                                      |




## Arrays

**When to Use:**

* ==Fixed==-size collections
* High performance required, predictable memory

**Examples in Unity:**

* Storing references to ==static enemy spawn points==
* Managing a ==fixed set of animation frames==

---

## `List<T>`

**When to Use:**

* ==Dynamic== collections that grow or shrink
* Random access and indexing is important

**Examples in Unity:**

* Managing a dynamic ==list of enemies== or NPCs
* ==Collecting raycast hits==
* Holding ==runtime-generated meshes or vertices==

---

## `LinkedList<T>`

**When to Use:**

* ==Frequent insertions/deletions from the middle==
* ==When order matters but indexing is rare==

**Examples in Unity:**

* ==Turn order management in a tactical RPG==
* ==Undo/Redo== stacks for level editors (when combining with cursor movement)

---

## `Stack<T>`

**When to Use:**

* LIFO behavior (Last In, First Out)
* Backtracking, ==undo==, or temporary memory

**Examples in Unity:**

* ==Object Pooling (optional struct111ure)==
* Implementing state stacks in game logic (==menus==, modes)
* Traversing trees or graphs (DFS)

---

## `Queue<T>`

**When to Use:**

* FIFO behavior (First In, First Out)
* ==Order of operations matters==

**Examples in Unity:**

* ==Object Pooling (commonly used with Queue)==
* ==Handling attack or movement queues==
* Turn-based AI actions

---

## `Dictionary<TKey, TValue>`

**When to Use:**

* ==Fast key-based lookups==
* Mapping relationships

**Examples in Unity:**

* Mapping ==string IDs to prefabs==
* Tracking ==scores by player ID==
* ==Mapping key inputs to actions==

---

## `HashSet<T>`

**When to Use:**

* ==Unique values only==
* Fast membership testing

**Examples in Unity:**

* Keeping track of ==explored nodes in pathfinding==
* ==Avoiding duplicate events/triggers==
* ==Fast collisions tag tracking== ("what have I hit?")

---

## `SortedSet<T>`

**When to Use:**

* Uniqueness + automatic sorting
* ==Priority without using keys==

**Examples in Unity:**

* ==Leaderboards== with unique scores
* Custom game systems needing sorted unique lists

---

## `PriorityQueue<TElement, TPriority>` (.NET 6+)

**When to Use:**

* Always needing the "lowest cost" or =="highest priority" item first==

**Examples in Unity:**

* A* pathfinding frontier queue (open set)
* Scheduling timed events or effects
* ==AI target prioritization==

---

---

## ⚠️ When to Use `List<T>` vs Arrays in Game Dev

- **Use `List<T>` by default** for most collections because of its flexibility and ease of use.
- **Arrays** are better for large fixed-size collections where you want to avoid resizing overhead.
- In most games, the performance difference is minimal, so start with `List<T>`.
- If performance or memory profiling shows bottlenecks, consider switching to arrays for critical sections.
- **Pre-size your lists** when possible to reduce costly reallocations:
  ```csharp
  var enemies = new List<Enemy>(100); // pre-allocates space for 100 items
  ```
- You can convert a list to an array if needed:
  ```csharp
  Enemy[] enemyArray = enemies.ToArray();
  ```
- Use Unity Profiler or other profiling tools to identify if and where optimizations are necessary.
