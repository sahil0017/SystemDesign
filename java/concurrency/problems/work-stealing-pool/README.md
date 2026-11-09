# Work Stealing Pool

## Problem Statement

Design a work-stealing thread pool where each thread has its own deque of tasks, and idle threads can "steal" tasks from other threads' deques to maximize CPU utilization and minimize contention.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Per-thread deque**: Each thread has a double-ended queue for its tasks.
- **Work submission**: New tasks are added to the submitting thread's deque.
- **Work stealing**: Idle threads steal from the tail of another thread's deque.
- **Fork/Join**: Tasks can spawn subtasks that are added to the current thread's deque.
- **Load balancing**: Automatic distribution of work across all threads.

### Non-Functional Requirements
- **Low contention**: Threads mostly operate on their own deque; minimal synchronization.
- **Cache friendly**: LIFO access pattern for both owner and thief improves cache locality.
- **Scalability**: Performance improves with more CPU cores.

## Key Design Decisions
- **LIFO for owner**: Thread pops from the head of its own deque (last task submitted is processed first).
- **FIFO for thief**: Stealing thread pops from the tail (oldest tasks are stolen first).
- **CAS operations**: Lock-free deque using Compare-And-Swap for concurrent access.
- **Random victim**: Stealing thread picks a random victim to avoid hotspot contention.

## Staff-Level Design Considerations

### Why Work Stealing Works
- **Low contention**: Each thread primarily operates on its own deque. Synchronization only occurs during stealing.
- **Good load balancing**: If one thread finishes its work, it steals from busy threads. No thread stays idle while work exists.
- **Cache friendly**: LIFO access means the owner works on recently allocated tasks that are likely in cache.
- **Staff insight**: Java's `ForkJoinPool` uses work stealing. It's the foundation of parallel streams and the `ForkJoinTask` framework. Understanding work stealing is key to writing efficient parallel algorithms.

### Deque Design
- **Array-based**: Power-of-2 sized array with index masking for fast modulo.
- **Base pointer**: Owner thread's pointer; points to the next available slot at the head.
- **Top pointer**: Thief's pointer; points to the next available slot at the tail.
- **CAS update**: Both pointers use CAS for lock-free concurrent updates.
- **Staff insight**: The deque uses two pointers (base and top) that move in opposite directions. The owner increments base (head), and the thief decrements top (tail). If base > top, the deque is empty. CAS ensures atomicity without locks.

### Fork/Join Pattern
```java
class MergeSortTask extends RecursiveAction {
    protected void compute() {
        if (data.length < THRESHOLD) {
            Arrays.sort(data);  // Base case: sort directly
        } else {
            MergeSortTask left = new MergeSortTask(leftHalf);
            MergeSortTask right = new MergeSortTask(rightHalf);
            left.fork();   // Asynchronously execute left half
            right.compute();  // Execute right half directly
            left.join();    // Wait for left half to complete
            merge(leftHalf, rightHalf);  // Merge results
        }
    }
}
```
- **Staff insight**: The fork/join pattern is most effective when the problem can be divided into roughly equal subproblems. The `fork()` method submits the subtask to the pool, and `join()` waits for its completion. Always set a threshold to avoid excessive task creation.

### Common Pitfalls
- **Too many tasks**: Creating more tasks than work items adds overhead. Set appropriate threshold.
- **Blocking in task**: If a task blocks (IO, sleep), it wastes a pool thread. Use managed blocking.
- **Unbalanced work**: If one subtask is much larger than others, work stealing helps but doesn't fully compensate.
- **Staff insight**: Work stealing is most effective for CPU-bound recursive algorithms (merge sort, matrix multiplication, tree traversal). For IO-bound tasks, use a regular thread pool with appropriate sizing. Never block a ForkJoinPool thread on IO.
