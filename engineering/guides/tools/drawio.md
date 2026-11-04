# draw.io

## What Is It?

draw.io (also called diagrams.net) is a free, open-source diagramming tool for creating architecture diagrams, flowcharts, network maps, and sequence diagrams. It is the standard tool for visualizing [system design](../../concepts/backend/architecture/system-design.md) — used by all team members for producing documentation diagrams.

## Options — Choose One

| Option | Best for | How to access |
|---|---|---|
| Web (browser) | Quick diagrams, no install | https://app.diagrams.net |
| Desktop app | Offline, faster, saves locally | Download below |
| VS Code extension | Edit diagrams inside VS Code | Extension Marketplace |

## Install — Desktop App

| OS | Method |
|---|---|
| Windows | Download `.exe` from https://github.com/jgraph/drawio-desktop/releases |
| Mac | Download `.dmg` from the same page |
| Linux | Download `.AppImage` or `.deb` from the same page |

The desktop app saves `.drawio` files locally and works fully offline.

## Install — VS Code Extension

1. Open VS Code → Extensions (`Ctrl+Shift+X`)
2. Search: **Draw.io Integration** by Henning Dieterichs
3. Click Install

After installing, any `.drawio` or `.drawio.png` file you open in VS Code renders as an interactive diagram editor — no separate app needed.

## File Format

draw.io saves files as `.drawio` (XML). You can also export to:

| Format | Use case |
|---|---|
| `.png` | Embed in Markdown, reports, presentations |
| `.svg` | Scalable vector — good for documents |
| `.pdf` | Print quality |
| `.html` | Embed interactive diagram in a web page |

**Tip:** Commit `.drawio` source files to Git alongside exported `.png` images. This way the diagram is both editable and viewable in GitHub without opening the app.

## Common Diagram Types for System Projects

| Diagram | What it shows |
|---|---|
| Architecture diagram | All components and how they connect (VM, [Docker](../../concepts/containers/docker.md), Nextcloud, AI service) |
| Network diagram | [VNet](../../concepts/cloud/azure/azure-vnet.md), Subnet, [NSG](../../concepts/cloud/azure/azure-nsg.md), public/private IPs, port flows |
| Sequence diagram | Step-by-step flow (e.g., user query → [RAG](../../concepts/ai/rag/rag.md) → [LLM](../../concepts/ai/generation/llm.md) → response) |
| Deployment diagram | Where each service runs (cloud vs local, container vs host) |
| Flowchart | Decision logic (e.g., permission check in [RAG](../../concepts/ai/rag/rag.md) pipeline) |

## Quick Start

1. Open draw.io (web or desktop)
2. Choose a blank template or pick from the template gallery
3. Drag shapes from the left panel onto the canvas
4. Double-click a shape to add a label
5. Connect shapes by hovering over a shape edge until a blue arrow appears, then drag
6. Export: **File → Export As → PNG** (or SVG/PDF)

## Useful Shape Libraries

Enable in draw.io via **View → Shapes**:

- **Network** — servers, firewalls, cloud icons
- **[Azure](../../concepts/cloud/azure/azure.md)** — official [Microsoft Azure](../../concepts/cloud/azure/azure.md) service icons
- **[AWS](../../concepts/cloud/infrastructure/aws.md)** — [Amazon Web Services](../../concepts/cloud/infrastructure/aws.md) icons
- **Flowchart** — standard process flow shapes
- **UML** — sequence, class, component diagrams

## Tips

- Use the [Azure](../../concepts/cloud/azure/azure.md) shape library for cloud architecture diagrams — it uses the official Microsoft icons
- Save `.drawio` files in a `docs/diagrams/` folder in the repo
- Export a `.png` alongside the `.drawio` file so diagrams are visible on GitHub without opening the app
- Use layers to separate concerns (e.g., network layer vs application layer) in complex diagrams

## Related

- [VS Code](vscode.md)
- [Git & GitHub Basics](../git/git-github-basics.md)
