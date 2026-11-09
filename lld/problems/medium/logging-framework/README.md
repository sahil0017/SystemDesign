# Logging Framework

## Problem Statement

Design a logging framework (like Log4j or SLF4J) that supports multiple log levels, appenders, formatters, asynchronous logging, and filtering.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Log levels**: DEBUG, INFO, WARN, ERROR, FATAL with hierarchical filtering.
- **Appenders**: Multiple output destinations (Console, File, Database, Network).
- **Formatters**: Configurable log message format (pattern-based, JSON, XML).
- **Async logging**: Non-blocking log writes using background thread pool.
- **Filters**: Include/exclude logs based on logger name, level, MDC (Mapped Diagnostic Context).
- **Rolling files**: Auto-rotate log files by size or time.
- **Thread safety**: Safe for concurrent use across multiple threads.

### Non-Functional Requirements
- **Performance**: Logging overhead < 1ms for async mode; < 10ms for sync mode.
- **Reliability**: No log loss on application crash (buffered flush).
- **Scalability**: Handle 100K+ log events per second.

## Key Design Decisions
- **Chain of Responsibility**: Filters process log events in sequence; any filter can reject.
- **Observer pattern**: Appenders observe log events and write to their destinations.
- **Builder pattern**: Fluent API for configuring loggers, appenders, and formatters.
- **Async queue**: Bounded blocking queue between logger and appender threads.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Logger     │────►│ LogEvent     │────►│  Appender    │◄── Abstract
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - level      │     │ - level      │     │ + append()   │
│ - appenders  │     │ - message    │     └──────┬───────┘
│ - filters    │     │ - timestamp  │            │
├──────────────┤     │ - threadName │            │
│ + debug()    │     │ - loggerName │            │
│ + info()     │     └──────────────┘     ┌──────┼───────┐
│ + error()    │                          │      │      │
└──────────────┘                 ┌────────┴┐ ┌───┴──┐ ┌─┴──────┐
                                 │Console  │ │File  │ │Database│
                                 │Appender │ │Appen │ │Appender│
                                 └─────────┘ │der   │ └────────┘
                                             └──────┘
```

## Staff-Level Design Considerations

### Async Logging Performance
- **Bounded queue**: Prevents OOM when log production rate exceeds consumption rate.
- **Staff insight**: Use a bounded `ArrayBlockingQueue` with a reject policy (drop oldest DEBUG logs first). Never use an unbounded queue for logging.

### Chain of Responsibility for Filters
- **Filter chain**: Each filter decides ACCEPT, DENY, or NEUTRAL. Short-circuit on DENY.
- **Staff insight**: This pattern is the same as servlet filters in Java and middleware in Express.js. Recognizing it across frameworks is a senior-level skill.

### Rolling File Strategy
- **Size-based**: Rotate when file exceeds N MB. Keep M backups.
- **Time-based**: Rotate daily/hourly. Compress old files.
- **Staff insight**: Use `FileLock` to prevent concurrent writes from multiple JVM instances to the same log file.
