# Priority Queue (Binary Heap)

## Problem Statement

Design and implement a priority queue using a binary heap that supports O(log n) insertion and O(1) peek of the highest-priority element.

**Reference**: [AlgoMaster](https://algomaster.io/), [HelloInterview](https://www.hellointerview.com/)

## Requirements

### Functional Requirements
- **Offer/Poll**: Insert element with O(log n) time; remove highest-priority element with O(log n).
- **Peek**: Return highest-priority element without removal in O(1).
- **Comparator**: Support natural ordering or custom comparator.
- **Iterate**: Non-guaranteed order iteration (heap order, not sorted).
- **Remove**: Arbitrary element removal in O(n) or O(log n) with backing map.

### Non-Functional Requirements
- **Performance**: O(log n) for offer/poll; O(1) for peek.
- **Memory efficiency**: Array-based storage; no per-node overhead.
- **Not thread-safe**: Like Java's PriorityQueue; use PriorityBlockingQueue for concurrent access.

## Key Design Decisions
- **Binary min-heap**: Array-based complete binary tree; parent at i/2, children at 2i and 2i+1.
- **Heapify up**: After insertion, bubble up to maintain heap property.
- **Heapify down**: After removal, sink root to maintain heap property.
- **Array resizing**: Double capacity when full; like ArrayList.

## Staff-Level Design Considerations

### Heap Operations
- **Insert (offer)**: Add to end, then heapify up by swapping with parent while violating heap property.
- **Remove (poll)**: Swap root with last element, remove last, then heapify down from root.
- **Peek**: Return root element (index 0); O(1) operation.
- **Staff insight**: The array representation of a binary heap is cache-friendly because parent-child relationships map to nearby array indices.

### When to Use PriorityQueue
- **Top-K elements**: Find K largest/smallest elements in a stream.
- **Dijkstra's algorithm**: Graph shortest path with priority-based exploration.
- **Task scheduling**: Process tasks by priority.
- **Merge K sorted lists**: Use min-heap to efficiently merge.
- **Staff insight**: PriorityQueue is the go-to data structure for any problem involving "top K" or "next best" selection.

### Performance Characteristics
- **Build heap**: O(n) using bottom-up heapify (not O(n log n)).
- **Heap sort**: O(n log n) by repeatedly extracting min/max.
- **Space**: O(n) for array storage; no per-node object overhead.
- **Staff insight**: Building a heap from an array is O(n), not O(n log n). The bottom-up approach exploits the fact that most nodes are near the leaves and require few swaps.

### Common Pitfalls
- **Null elements**: PriorityQueue doesn't allow null elements; throws NullPointerException.
- **Non-thread-safe**: Use PriorityBlockingQueue for concurrent producer-consumer scenarios.
- **Iteration order**: Iterating a PriorityQueue does NOT yield sorted order; use `drainTo()` or sort explicitly.
- **Remove overhead**: `remove(Object)` is O(n) because it must find the element first. Use a backing HashMap for O(log n) removal.
- **Staff insight**: For O(log n) arbitrary removal, maintain a HashMap from element to heap index. This is how advanced priority queues (like those in Dijkstra implementations) achieve efficient deletion.
