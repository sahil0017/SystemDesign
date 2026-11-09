# Data Aggregation Pipeline

## Problem Statement

Design a data aggregation pipeline using Java Streams that processes large datasets to compute summaries, groupings, and statistics in a single pass for ETL and reporting use cases.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Grouping**: Group data by key (e.g., by category, date, region).
- **Aggregation**: Compute sum, average, min, max, count per group.
- **Partitioning**: Split data by boolean condition (e.g., active/inactive).
- **Statistics**: Compute summary statistics (mean, deviation, count) in one pass.
- **Chaining**: Combine multiple aggregation steps in a single pipeline.

### Non-Functional Requirements
- **Single pass**: Process data once; compute all aggregations in one traversal.
- **Memory efficiency**: Use primitive streams to avoid boxing overhead.
- **Performance**: Match or exceed SQL-like aggregation performance.

## Key Design Decisions
- **groupingBy**: Primary operation for grouping data by key.
- **downstream collectors**: Chain collectors (counting, summing, averaging) after groupingBy.
- **summarizing**: Use `summarizingInt/Long/Double` for one-pass statistics.
- **partitioningBy**: Binary split for boolean conditions.

## Staff-Level Design Considerations

### Downstream Collectors
```java
// Group by category and compute multiple aggregations
Map<String, LongSummaryStatistics> stats = data.stream()
    .collect(Collectors.groupingBy(
        Item::getCategory,
        Collectors.summarizingLong(Item::getPrice)
    ));
// Result: count, sum, min, max, average in one pass

// Group and count
Map<String, Long> count = data.stream()
    .collect(Collectors.groupingBy(Item::getCategory, Collectors.counting()));

// Group and sum
Map<String, Long> total = data.stream()
    .collect(Collectors.groupingBy(Item::getCategory, Collectors.summingLong(Item::getPrice())));
```
- **Staff insight**: `summarizingLong` computes count, sum, min, max, and average in a single pass. This is equivalent to SQL's `GROUP BY category SELECT COUNT(*), SUM(price), MIN(price), MAX(price), AVG(price)`.

### Multi-Level Grouping
```java
// Group by category, then by status
Map<String, Map<String, Long>> nested = data.stream()
    .collect(Collectors.groupingBy(
        Item::getCategory,
        Collectors.groupingBy(Item::getStatus, Collectors.counting())
    ));
```
- **Staff insight**: Nested groupingBy is equivalent to SQL's `GROUP BY category, status`. For deep nesting (3+ levels), consider using a custom key (e.g., `category + "|" + status`) for better performance and readability.

### Partitioning vs Grouping
- **partitioningBy**: Returns a Map<Boolean, List<T>>; exactly two groups (true/false).
- **groupingBy**: Returns a Map<K, List<T>>; any number of groups.
- **Staff insight**: Use `partitioningBy` when you have a boolean split. It's slightly more efficient than `groupingBy` because it knows there are exactly two groups and can pre-allocate the map.

### Common Pitfalls
- **Boxing overhead**: `Stream<Item>.mapToInt()` vs `Stream<Integer>` — always use primitive downstream collectors.
- **Multiple passes**: Calling `groupingBy` then `stream().map()` is two passes. Use downstream collectors for single-pass aggregation.
- **Null keys**: `groupingBy` throws NullPointerException on null keys. Filter nulls first.
- **Staff insight**: The most common mistake is making multiple passes over the data. Use downstream collectors to compute all aggregations in a single pass. This is especially important for large datasets where each pass adds significant overhead.
