# Personal AI Employee - Project Context

## Project Overview

This is a **hackathon project** for building a "Digital FTE" (Full-Time Equivalent) — an autonomous AI agent that manages personal and business affairs 24/7. The architecture uses **Claude Code** as the reasoning engine and **Obsidian** as the knowledge base/dashboard, with lightweight Python "Watcher" scripts for monitoring and **MCP (Model Context Protocol)** servers for external actions.

**Tagline:** _Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop._

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Digital FTE Architecture                  │
├─────────────────────────────────────────────────────────────┤
│  Perception Layer (Watchers)                                │
│  ├── Gmail Watcher (monitors emails)                        │
│  ├── WhatsApp Watcher (monitors messages)                   │
│  ├── File System Watcher (monitors drops)                   │
│  └── Finance Watcher (monitors transactions)                │
├─────────────────────────────────────────────────────────────┤
│  Reasoning Layer (Claude Code)                              │
│  ├── Reads from /Inbox, /Needs_Action                       │
│  ├── Creates Plan.md files with action items                │
│  └── Generates CEO Briefings                                │
├─────────────────────────────────────────────────────────────┤
│  Action Layer (MCP Servers)                                 │
│  ├── Email MCP (send/draft emails)                          │
│  ├── Browser MCP (Playwright for web automation)            │
│  ├── Calendar MCP (scheduling)                              │
│  └── Custom MCPs (Xero, Social Media, etc.)                 │
├─────────────────────────────────────────────────────────────┤
│  Memory/GUI (Obsidian Vault)                                │
│  ├── Dashboard.md (real-time status)                        │
│  ├── Company_Handbook.md (rules of engagement)              │
│  ├── Business_Goals.md (objectives & metrics)               │
│  ├── /Inbox, /Needs_Action, /Done folders                   │
│  └── /Pending_Approval (human-in-the-loop)                  │
└─────────────────────────────────────────────────────────────┘
```

## Key Concepts

### Watcher Pattern
Lightweight Python scripts that run continuously in the background, monitoring various inputs and creating actionable `.md` files in the `Needs_Action` folder when events occur.

### Human-in-the-Loop (HITL)
For sensitive actions (payments, approvals), Claude writes an approval request file instead of acting directly. The user must move the file to `/Approved` before the action executes.

### CEO Briefing
A scheduled feature where the AI autonomously audits bank transactions and tasks to generate a "Monday Morning CEO Briefing" highlighting revenue, bottlenecks, and proactive suggestions.

## Project Structure

```
Personal-AI-Employ/
├── hackathon 0.md          # Comprehensive hackathon blueprint & architecture guide
├── skills-lock.json        # Skill version tracking (browsing-with-playwright)
├── .gitattributes          # Git text file normalization
└── .qwen/
    └── skills/
        └── browsing-with-playwright/
            ├── SKILL.md              # Playwright MCP usage documentation
            ├── references/
            │   └── playwright-tools.md
            └── scripts/
                ├── mcp-client.py     # MCP client for browser automation
                ├── start-server.sh   # Start Playwright MCP server
                ├── stop-server.sh    # Stop Playwright MCP server
                └── verify.py         # Server verification script
```

## Building and Running

### Prerequisites

| Component | Requirement | Purpose |
|-----------|-------------|---------|
| Claude Code | Active subscription | Primary reasoning engine |
| Obsidian | v1.10.6+ | Knowledge base & dashboard |
| Python | 3.13+ | Watcher scripts & orchestration |
| Node.js | v24+ LTS | MCP servers & automation |
| GitHub Desktop | Latest | Version control |

### Hardware Requirements

- **Minimum:** 8GB RAM, 4-core CPU, 20GB free disk space
- **Recommended:** 16GB RAM, 8-core CPU, SSD storage
- Stable internet connection for API calls (10+ Mbps)

### Setup Commands

```bash
# Verify Claude Code installation
claude --version

# Start Playwright MCP server (for browser automation)
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Verify server is running
python3 .qwen/skills/browsing-with-playwright/scripts/verify.py

# Stop server when done
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

### MCP Server Configuration

Configure MCP servers in `~/.config/claude-code/mcp.json`:

```json
{
  "servers": [
    {
      "name": "browser",
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "env": {
        "HEADLESS": "true"
      }
    }
  ]
}
```

## Development Conventions

### Folder Structure (Obsidian Vault)

Create an Obsidian vault with this structure:

```
AI_Employee_Vault/
├── Dashboard.md
├── Company_Handbook.md
├── Business_Goals.md
├── Inbox/
├── Needs_Action/
├── Done/
├── Pending_Approval/
├── Approved/
├── Rejected/
├── Accounting/
└── Briefings/
```

### Agent Skills

All AI functionality should be implemented as **Agent Skills** following the pattern in `SKILL.md` files. Each skill should document:
- When to use it
- Server lifecycle management
- Quick reference commands
- Troubleshooting guide

### Coding Practices

1. **Local-first:** Keep data local in Obsidian Markdown files
2. **Human-in-the-loop:** Never auto-execute sensitive actions
3. **Watcher pattern:** Use lightweight scripts for monitoring
4. **Audit logging:** Log all actions for transparency

## Hackathon Tiers

| Tier | Description | Time Estimate |
|------|-------------|---------------|
| **Bronze** | Foundation (Dashboard, 1 Watcher, basic Claude integration) | 8-12 hours |
| **Silver** | Functional Assistant (multiple Watchers, MCP servers, HITL workflow) | 20-30 hours |
| **Gold** | Autonomous Employee (full integration, Xero, social media, CEO Briefing) | 40+ hours |

## Resources

- **Hackathon Blueprint:** `hackathon 0.md` - Complete architectural guide
- **Playwright Skill:** `.qwen/skills/browsing-with-playwright/SKILL.md`
- **Research Meetings:** Wednesdays 10:00 PM on Zoom (see hackathon doc for link)

## Key Files Reference

| File | Purpose |
|------|---------|
| `hackathon 0.md` | Comprehensive architecture blueprint, templates, and implementation guide |
| `skills-lock.json` | Tracks installed skill versions |
| `.qwen/skills/browsing-with-playwright/SKILL.md` | Browser automation documentation |
| `.qwen/skills/browsing-with-playwright/scripts/mcp-client.py` | MCP client for Playwright |

## Watcher Architecture

All Watchers follow the `BaseWatcher` pattern:

```python
class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
    
    @abstractmethod
    def check_for_updates(self) -> list:
        """Return list of new items to process"""
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        """Create .md file in Needs_Action folder"""
        pass
```

## MCP Servers Reference

| Server | Capabilities | Use Case |
|--------|--------------|----------|
| filesystem | Read, write, list files | Built-in for vault |
| email-mcp | Send, draft, search emails | Gmail integration |
| browser-mcp | Navigate, click, fill forms | Web automation (Playwright) |
| calendar-mcp | Create, update events | Scheduling |
| xero-mcp | Accounting operations | Xero integration |
