# HLD Diagrams

This directory contains Excalidraw diagrams for High-Level Design (HLD) system architecture, sequence flows, and deployment topologies.

## Diagram Types

| Directory | Description |
|-----------|-------------|
| [architecture/](architecture/) | System architecture diagrams showing components and their relationships |
| [sequence/](sequence/) | Sequence diagrams illustrating request/response flows between services |
| [deployment/](deployment/) | Deployment diagrams showing infrastructure topology and service distribution |

## Getting Started

### Installing the Excalidraw Plugin

1. Open **IntelliJ IDEA**
2. Go to **Settings/Preferences** → **Plugins** → **Marketplace**
3. Search for **"Excalidraw Integration"**
4. Click **Install** and restart the IDE

### Creating New Diagrams

- **Right-click** on any directory → **New** → **Excalidraw File**
- Or open an existing `.excalidraw` file to edit it in the built-in canvas

### File Format

All diagrams use the `.excalidraw` extension (JSON-based format). You can also:

- Import diagrams from [excalidraw.com](https://excalidraw.com) by copying the JSON and saving as `.excalidraw`
- Export diagrams as **PNG** or **SVG** from within the IDE plugin

## Conventions

- Use meaningful file names: `<system>-architecture.excalidraw`, `<system>-sequence.excalidraw`
- Keep diagrams focused on one concept per file
- Add descriptive text labels within diagrams for clarity
- Use consistent colors across related diagrams
