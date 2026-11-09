# Task Management System

## Problem Statement

Design a task management system (like Todoist or Jira-lite) that allows users to create, update, delete, and organize tasks with priorities, due dates, labels, and assignments.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **CRUD operations**: Create, read, update, delete tasks.
- **Task properties**: Title, description, priority (Low/Medium/High/Critical), due date, status (Todo/In Progress/Done).
- **Labels/Tags**: Assign multiple labels to tasks for categorization.
- **Assignments**: Assign tasks to users; support shared projects.
- **Search/Filter**: Filter by status, priority, label, assignee, due date range.
- **Notifications**: Reminders for upcoming due dates.

### Non-Functional Requirements
- **Scale**: 100K+ tasks per user; 1M+ total tasks.
- **Latency**: Task creation < 200ms; search < 500ms.
- **Data integrity**: No lost updates on concurrent edits.

## Key Design Decisions
- **Entity model**: Task as core entity with one-to-many relationships to labels and assignments.
- **Status tracking**: State pattern for task lifecycle transitions.
- **Search**: Index by frequently filtered fields (status, priority, due date).
- **Concurrency**: Optimistic locking for task updates.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│     User     │────►│    Task      │────►│    Label     │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - userId     │     │ - taskId     │     │ - labelId    │
│ - name       │     │ - title      │     │ - name       │
│ - email      │     │ - description│     │ - color      │
└──────────────┘     │ - priority   │     └──────────────┘
                     │ - status     │
                     │ - dueDate    │
                     │ - assignees  │
                     └──────────────┘
```

## Staff-Level Design Considerations

### State Machine for Task Status
- **Valid transitions**: Todo → In Progress → Done; any state → Deleted.
- **Staff insight**: Enforce transitions in code, not just in UI. Use an enum-based state machine to prevent invalid states.

### Search Performance
- **Indexing**: Maintain separate indexes for status, priority, and due date.
- **Staff insight**: For large-scale systems, delegate search to Elasticsearch. In-memory filtering is O(n) — not scalable.

### Concurrency
- **Optimistic locking**: Version field on Task; reject updates with stale versions.
- **Staff insight**: Collaborative editing (like Google Docs) requires CRDTs or OT algorithms — beyond scope of basic LLD but worth mentioning.
