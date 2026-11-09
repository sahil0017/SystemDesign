# Text Editor

## Problem Statement (Staff-Level)

Design a text editor system that supports multi-cursor editing, undo/redo with command pattern, find and replace, syntax highlighting, and collaborative editing with operational transformation (OT) for real-time collaboration.

**Reference**: AlgoMaster, HelloInterview, LLD Coding

## Requirements

### Functional Requirements
- **Text manipulation**: Insert, delete, replace text with O(1) operations using gap buffer.
- **Multi-cursor**: Support multiple cursors with independent insert/delete operations.
- **Undo/redo**: Unlimited undo/redo stack with command pattern; grouped operations.
- **Find and replace**: Regex-based search with highlight and batch replace.
- **Syntax highlighting**: Tokenize text by language; apply color themes.
- **Collaborative editing**: Real-time multi-user editing with OT/CRDT conflict resolution.
- **Document management**: Save, load, and auto-save documents with version history.

### Non-Functional Requirements
- **Scale**: 1MB+ document size; 100+ concurrent collaborators.
- **Latency**: Text insertion < 10ms; find/replace < 100ms; sync latency < 200ms.
- **Memory**: Gap buffer for efficient text operations; < 100MB for 1MB document.
- **Consistency**: Strong consistency for single-user; eventual consistency for collaboration.

## Key Design Decisions
- **Gap buffer**: O(1) insert/delete at cursor; O(n) for random access.
- **Command pattern**: Each edit is a command with execute/undo methods for undo/redo.
- **Operational Transformation**: Resolve concurrent edits by transforming operations against each other.
- **Tokenizer**: State machine-based tokenizer for syntax highlighting.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Document   │────►│  GapBuffer   │────►│    Cursor    │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - commands   │     │ - buffer     │     │ - row        │
│ - undoStack  │     │ - gapStart   │     │ - column     │
│ - redoStack  │     │ - gapSize    │     └──────────────┘
└──────────────┘
           │
    ┌──────┴──────┐
    │  Command    │
    ├─────────────┤
    │ + execute() │
    │ + undo()    │
    └─────────────┘
```

## Staff-Level Design Considerations

### Gap Buffer vs Rope
- **Gap buffer**: Simple and fast for cursor-adjacent operations. O(1) insert/delete at cursor; O(n) for random access.
- **Rope**: Tree-based structure for O(log n) random access. Better for very large documents (> 10MB).
- **Staff insight**: Gap buffer is the standard for text editors up to 1MB. Switch to rope for large files (e.g., minified JS, log files). VS Code uses a hybrid: gap buffer for small files, rope for large ones.

### Command Pattern for Undo/Redo
- **Command interface**: Each edit implements `execute()` and `undo()`.
- **Command grouping**: Group multiple commands into a single undo unit (e.g., typeahead characters).
- **Staff insight**: The command pattern is the cleanest way to implement undo/redo. Group commands by "intent" — a burst of typing is one command, not 50. Use a time-based grouping (e.g., characters typed within 300ms are one command).

### Operational Transformation
- **Problem**: Two users edit simultaneously; their conflicts must be resolved without losing data.
- **Solution**: Transform operations against each other. If A inserts at position 5 and B deletes at position 3, adjust A's position to 4.
- **Staff insight**: OT is complex. For collaboration, consider using CRDTs (Conflict-free Replicated Data Types) instead — they're simpler to implement and guarantee convergence without a central server. Yjs is a popular CRDT library for collaborative text editing.

### Syntax Highlighting
- **Tokenizer**: State machine that reads characters and emits tokens (keyword, string, comment, etc.).
- **Incremental highlighting**: Only re-highlight changed lines, not the entire document.
- **Staff insight**: Syntax highlighting should never block the main thread. Run tokenization in a Web Worker (browser) or background thread (desktop). Cache tokenized lines and only re-tokenize on changes.
