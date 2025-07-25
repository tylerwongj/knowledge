
# 📚 C# Data Structures — Most Common Methods Cheat Sheet

## Arrays
```csharp
array.Length              ✅
Array.Sort(array)         ✅
Array.Reverse(array)
Array.IndexOf(array, value)
Array.Copy(src, dest, len)
```

---

## `List<T>` (Resizable array)
Namespace: `System.Collections.Generic`
```csharp
list.Add(item)            ✅
list.Remove(item)         ✅
list.RemoveAt(index)
list.Contains(item)
list.IndexOf(item)
list.Insert(index, item)
list.Count                ✅
list.Clear()
list.Sort()
list.Reverse()
list.ToArray()
```

---

## `LinkedList<T>` (Doubly linked list)
```csharp
list.AddFirst(value)
list.AddLast(value)       ✅
list.Remove(value)        ✅
list.First                ✅
list.Last
list.Find(value)
```

---

## `Stack<T>` (LIFO)
```csharp
stack.Push(item)          ✅
stack.Pop()               ✅
stack.Peek()              ✅
stack.Count
stack.Clear()
```

---

## `Queue<T>` (FIFO)
```csharp
queue.Enqueue(item)       ✅
queue.Dequeue()           ✅
queue.Peek()              ✅
queue.Count
queue.Clear()
```

---

## `Dictionary<TKey, TValue>` (Hash map)
```csharp
dict.Add(key, value)
dict.Remove(key)                          ✅
dict.ContainsKey(key)
dict.TryGetValue(key, out value)          ✅
dict[key] = value                         ✅  // access/set
dict.Keys
dict.Values
dict.Clear()
dict.Count
```

---

## `HashSet<T>` (Set of unique values)
```csharp
set.Add(item)             ✅
set.Remove(item)          ✅
set.Contains(item)        ✅
set.UnionWith(other)
set.IntersectWith(other)
set.Clear()
set.Count
```

---

## `SortedSet<T>` (Sorted unique set)
```csharp
sorted.Add(item)          ✅
sorted.Contains(item)     ✅
sorted.Remove(item)       ✅
sorted.Min
sorted.Max
```

---

## `PriorityQueue<TElement, TPriority>` (.NET 6+)
```csharp
pq.Enqueue("item", priority)   ✅
pq.Dequeue()                   ✅
pq.Peek()                      ✅
```

---

## 🧠 Longest Increasing Subsequence (LIS) — BinarySearch version
```csharp
List<int> lis = new List<int>();
foreach (int x in nums) {
    int i = lis.BinarySearch(x);
    if (i < 0) i = ~i;
    if (i == lis.Count) lis.Add(x);
    else lis[i] = x;
}
```

---

## ⚠️ Tips
- `List<T>` is the go-to for flexible arrays.
- Use `TryGetValue` over direct access when unsure about key existence.
- `Stack<T>` = DFS. `Queue<T>` = BFS.
- `HashSet<T>` is perfect for uniqueness and quick lookups.
- Learn `BinarySearch` for efficient LIS and insert placement problems.

