# Lock-Free Stack

## Problem Statement

Implement a lock-free thread-safe stack using Compare-And-Swap (CAS) operations. The stack should support concurrent push and pop operations without using any locks, achieving high throughput under contention by allowing multiple threads to operate simultaneously.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Push**: Add element to top of stack atomically.
- **Pop**: Remove and return top element atomically.
- **Peek**: View top element without removing.
- **Empty check**: Determine if stack is empty.
- **Lock-free progress**: At least one thread makes progress under contention.

### Non-Functional Requirements
- **No locks**: Use only CAS operations for synchronization.
- **Memory safety**: Handle ABA problem correctly.
- **GC awareness**: Avoid premature reclamation of popped nodes.

## Key Design Decisions
- **CAS on head**: AtomicReference for head node; CAS to update.
- **ABA mitigation**: Use AtomicMarkableReference or versioned nodes.
- **Unsafe publication**: Ensure node is fully constructed before CAS.

## Implementation

```java
public class LockFreeStack<E> {
    private static class Node<E> {
        final E item;
        AtomicReference<Node<E>> next;
        Node(E item) { this.item = item; this.next = new AtomicReference<>(); }
    }

    private final AtomicReference<Node<E>> head = new AtomicReference<>(null);

    public void push(E item) {
        Node<E> newNode = new Node(item);
        Node<E> oldHead;
        do {
            oldHead = head.get();
            newNode.next.set(oldHead);
        } while (!head.compareAndSet(oldHead, newNode));
    }

    public E pop() {
        Node<E> oldHead;
        Node<E> newHead;
        do {
            oldHead = head.get();
            if (oldHead == null) return null;
            newHead = oldHead.next.get();
        } while (!head.compareAndSet(oldHead, newHead));
        return oldHead.item;
    }

    public E peek() {
        return head.get() != null ? head.get().item : null;
    }

    public boolean isEmpty() {
        return head.get() == null;
    }
}
```

## Staff-Level Design Considerations

### The ABA Problem
- **Problem**: Thread 1 reads head=A. Thread 2 pops A, pops B, pushes A. Head is A again. Thread 1's CAS succeeds, but now points to a different A.
- **Solution**: Use `AtomicMarkableReference` or versioned nodes with monotonic counter.
- **Staff insight**: In a simple stack, ABA is **theoretical but rare** in practice. The popped node's `next` still points to the old value, so the stack remains correct. However, for production use, use **AtomicStampedReference** to add a version stamp to each CAS, preventing ABA from succeeding.

### Lock-Free vs Wait-Free
- **Lock-free**: At least one thread makes progress — CAS retry loops.
- **Wait-free**: Every thread completes in bounded steps — no retry.
- **Staff insight**: Lock-free is **practical and sufficient** for most use cases. Wait-free is theoretically superior but extremely complex to implement. Java's concurrent collections are lock-free, not wait-free. Accept that under extreme contention, some threads may retry many times — this is rare in production.

### When to Use Lock-Free Structures
- **High contention**: Many threads pushing/popping simultaneously.
- **Low latency**: Can't afford lock acquisition delay.
- **Staff insight**: **Prefer `ConcurrentLinkedQueue` over lock-free stack** for most use cases. Lock-free stacks have the ABA problem and are harder to get right. Use lock-free structures only when profiling shows lock contention as the bottleneck. For 95% of use cases, `synchronized` or `ReentrantLock` is simpler and performant enough.

### Memory Reclamation
- **Problem**: Popped nodes may still be referenced by in-flight CAS operations.
- **Java GC**: Garbage collector handles reclamation — nodes are collected when no longer referenced.
- **Staff insight**: In Java, **memory reclamation is handled by GC** — unlike C++ where you need hazard pointers or epoch-based reclamation. However, be aware that popped nodes remain in memory until GC runs. For high-throughput stacks, this creates GC pressure. Use object pooling for nodes if GC becomes a bottleneck.
