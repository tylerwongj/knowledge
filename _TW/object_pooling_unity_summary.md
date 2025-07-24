
# Object Pooling in Unity — Summary


==`IPoolable`, `ObjectPool<T>`==

## Overview
Object pooling is a common pattern to efficiently reuse objects instead of creating/destroying them repeatedly. This reduces GC pressure and runtime instantiation spikes.

---

## Core Concepts

### 1. ==IPoolable== Interface
- Defines a ==`ResetState()`== method that pooled objects implement to reset themselves when returned to the pool.
- Ensures the pool can reset any pooled object generically.

### 2. Generic ==ObjectPool`<T>`== Class
- Manages a pool of objects of type `T` where `T` is `MonoBehaviour` and implements `IPoolable`.
- Uses a ==`Stack<T>` (LIFO)== internally to store inactive objects.
- Pre-instantiates a specified number of objects ==(`initialSize`)== and stores them inactive.
- Provides:
  - ==`GetObject()`== to retrieve an object (pops from the stack or instantiates if empty) and activates it.
  - ==`ReturnObject()`== to reset and deactivate an object, then push it back into the stack.

### 3. Stack vs Queue
- Stack (LIFO) is preferred over Queue (FIFO) for better CPU cache locality and performance.
- Stack reuses the most recently returned objects first, which is often beneficial in games.
- Queue can be used if strict fairness in reuse is needed, but usually not required.

### 4. Pool Growth and Size Considerations
- Pool can be auto-growing (instantiating new objects when empty) or fixed size.
- Auto-growing pools are flexible but can cause runtime spikes.
- Fixed-size pools require handling when no objects are available (e.g., returning null).
- It's recommended to set an initial pool size based on expected max concurrent objects.

### 5. Usage Pattern
- Attach `ObjectPool<T>` to a GameObject.
- Assign prefab implementing `IPoolable`.
- Use `GetObject()` to obtain objects for use.
- Use `ReturnObject()` to recycle objects.

---

## Code Examples

### IPoolable Interface

```csharp
public interface IPoolable
{
    void ResetState();
}
```

### Generic ObjectPool using Stack`<T>`

```csharp
using UnityEngine;
using System.Collections.Generic;

public class ObjectPool<T> : MonoBehaviour where T : MonoBehaviour, IPoolable
{
    [SerializeField] private T prefab;
    [SerializeField] private int initialSize = 10;

    private Stack<T> pool = new Stack<T>();

    void Start()
    {
        for (int i = 0; i < initialSize; i++)
        {
            T obj = Instantiate(prefab);
            obj.gameObject.SetActive(false);
            pool.Push(obj);
        }
    }

    public T GetObject()
    {
        if (pool.Count > 0)
        {
            T obj = pool.Pop();
            obj.gameObject.SetActive(true);
            return obj;
        }
        else
        {
            return Instantiate(prefab);
        }
    }

    public void ReturnObject(T obj)
    {
        obj.ResetState();
        obj.gameObject.SetActive(false);
        pool.Push(obj);
    }
}
```

### Example Projectile Class Implementing IPoolable


```csharp
using UnityEngine;

public class Projectile : MonoBehaviour, IPoolable
{
    private Rigidbody rb;

    void Awake()
    {
        rb = GetComponent<Rigidbody>();
    }

    public void ResetState()
    {
        // Reset transform
        transform.position = Vector3.zero;
        transform.rotation = Quaternion.identity;

        // Reset physics
        if (rb != null)
        {
            rb.velocity = Vector3.zero;
            rb.angularVelocity = Vector3.zero;
        }

        // Reset any other projectile-specific state here
    }
}
```

---

## Notes from Discussion

- The pool does **not** implement `IPoolable`. Only pooled objects do.
- Prefabs must be `MonoBehaviour` and implement `IPoolable`.
- Using a generic class increases reusability.
- The pool manages activation/deactivation and reset logic separation.
- Stack usage is a slight performance optimization over queue.
- When pool runs out, new objects are instantiated (auto-grow behavior).
- You can configure pool size based on expected load.
- Alternative patterns exist (factory methods, fixed-size pools, event-driven resets).

---

# Summary

This design cleanly separates responsibilities, provides flexibility, and helps maintain consistent, performant object reuse in Unity games.
