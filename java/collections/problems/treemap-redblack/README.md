# TreeMap and Red-Black Tree

## Problem Statement

Design and implement a sorted map using a Red-Black tree that maintains keys in sorted order and supports O(log n) operations for insertion, deletion, and range queries.

**Reference**: [AlgoMaster](https://algomaster.io/), [HelloInterview](https://www.hellointerview.com/)

## Requirements

### Functional Requirements
- **Put/Get/Delete**: O(log n) time complexity for basic operations.
- **Sorted order**: Keys maintained in ascending order (natural or custom comparator).
- **Range queries**: `subMap`, `headMap`, `tailMap` for key range navigation.
- **Navigation**: `firstKey`, `lastKey`, `floorKey`, `ceilingKey`, `lowerKey`, `higherKey`.
- **Red-Black properties**: Self-balancing binary search tree with color invariants.

### Non-Functional Requirements
- **Balanced tree**: O(log n) height guarantee; no degenerate cases.
- **Memory efficiency**: Minimal overhead per node (color bit + parent/left/right references).
- **Consistent iteration**: In-order traversal yields sorted keys.

## Key Design Decisions
- **Red-Black tree**: Self-balancing BST with 5 properties that guarantee O(log n) height.
- **Coloring**: Each node is red or black; root is always black; no two consecutive red nodes.
- **Rotations**: Left and right rotations to maintain balance after insert/delete.
- **Comparator**: Natural ordering by default; custom comparator for custom sort order.

## Staff-Level Design Considerations

### Red-Black Tree Properties
1. Every node is red or black.
2. Root is always black.
3. All leaves (NIL nodes) are black.
4. If a node is red, both children are black (no two consecutive reds).
5. Every path from root to leaf has the same number of black nodes.
- **Staff insight**: Property 4 and 5 together guarantee the tree height is at most 2×log(n+1). This ensures O(log n) worst-case for all operations.

### Insertion Algorithm
- **Step 1**: Insert as a red node using BST insertion.
- **Step 2**: Fix violations by recoloring and rotations.
- **Cases**: Uncle is red (recolor), uncle is black (rotate).
- **Staff insight**: Inserting as red minimizes violations (doesn't break property 5). Fixing may require up to 2 rotations.

### Deletion Algorithm
- **Step 1**: Standard BST deletion.
- **Step 2**: If black node is removed, fix double-black violation.
- **Cases**: Sibling is red (rotate), sibling is black with red/black children (recolor/rotate).
- **Staff insight**: Deletion is more complex than insertion. The "double-black" concept is a virtual state that represents a deficit of black height.

### When to Use TreeMap
- **Sorted iteration**: When you need keys in sorted order.
- **Range queries**: `subMap`, `floorEntry`, `ceilingEntry` for range-based lookups.
- **Custom ordering**: When natural ordering isn't sufficient.
- **Staff insight**: Use HashMap for O(1) average access. Use TreeMap only when you need sorted order or range queries. TreeMap's O(log n) is 3-5× slower than HashMap's O(1) for point lookups.
