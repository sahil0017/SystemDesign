# Course Registration System

## Problem Statement

Design a university course registration system that allows students to browse courses, register for classes, handle prerequisites, manage conflicts, and support waitlisting.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Course catalog**: Browse courses by department, semester, instructor, and schedule.
- **Registration**: Add/drop courses; check prerequisites and corequisites.
- **Conflict detection**: Prevent time conflicts; enforce credit hour limits.
- **Waitlist**: Auto-enroll when seats become available; priority by standing.
- **Prerequisites**: Validate completed prerequisites before allowing registration.
- **Sections**: Multiple sections per course with different instructors and times.
- **Reporting**: Registration statistics; capacity utilization; waitlist analytics.

### Non-Functional Requirements
- **Concurrency**: 10K+ students registering simultaneously at opening.
- **Latency**: Course search < 500ms; registration confirmation < 2s.
- **Consistency**: No over-enrollment; accurate seat counts.

## Key Design Decisions
- **Constraint checking**: Prerequisite graph (DAG) for validation; interval tree for time conflicts.
- **Concurrency**: Optimistic locking with retry; queue-based registration during peak.
- **Waitlist**: Priority queue ordered by academic standing and timestamp.
- **State machine**: Registration states: Open → Closed → Waitlist → Cancelled.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Student    │────►│ Enrollment   │────►│   Course     │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - studentId  │     │ - enrollId   │     │ - courseId   │
│ - name       │     │ - status     │     │ - title      │
│ - credits    │     │ - grade      │     │ - credits    │
└──────────────┘     └──────────────┘     │ - capacity   │
                                          │ - enrolled   │
                                          └──────┬───────┘
                                                 │ has
                                          ┌──────┴───────┐
                                          │   Section    │
                                          ├──────────────┤
                                          │ - sectionId  │
                                          │ - instructor │
                                          │ - schedule   │
                                          │ - room       │
                                          └──────────────┘
```

## Staff-Level Design Considerations

### Prerequisite Validation
- **DAG traversal**: Prerequisites form a directed acyclic graph. Topological sort validates completion order.
- **Staff insight**: Cycle detection is critical. If Course A requires B and B requires A, the system should reject the configuration. Use DFS with a visited set.

### Time Conflict Detection
- **Interval tree**: Store class schedules as intervals. O(log n + k) overlap detection.
- **Staff insight**: A naive O(n²) comparison of all enrolled courses is too slow for 10K concurrent students. Pre-compute conflicts and cache per-student.

### Registration Queue
- **FIFO queue**: During peak registration, place students in a queue and process in batches.
- **Staff insight**: This prevents database overload. Use a token bucket to admit N students per second. The queue position is visible to students to reduce anxiety.
