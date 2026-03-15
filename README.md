# 🤖 Personal AI Employee - Digital FTE

> **Tagline:** Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

[![Tier Status](https://img.shields.io/badge/Status-PLATINUM%20COMPLETE-success)](PLATINUM_VERIFICATION.md)
[![Requirements](https://img.shields.io/badge/Requirements-35/35%20Complete-brightgreen)](hackathon%200.md)
[![Agent Skills](https://img.shields.io/badge/Skills-15%20Total-blue)](.qwen/skills/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📋 Overview

This is a **hackathon project** for building a "Digital FTE" (Full-Time Equivalent) — an autonomous AI agent that manages personal and business affairs 24/7. The architecture uses **Claude Code / Hugging Face LLMs** as the reasoning engine and **Obsidian** as the knowledge base/dashboard, with lightweight Python "Watcher" scripts for monitoring and **MCP (Model Context Protocol)** servers for external actions.

### Human FTE vs Digital FTE

| Feature | Human FTE | Digital FTE |
|---------|-----------|-------------|
| **Availability** | 40 hours/week | 168 hours/week (24/7) |
| **Monthly Cost** | $4,000 – $8,000+ | $0 – $200 |
| **Ramp-up Time** | 3 – 6 Months | Instant |
| **Consistency** | 85–95% accuracy | 99%+ consistency |
| **Scaling** | Linear (10x work = 10 hires) | Exponential (instant duplication) |
| **Cost per Task** | ~$5.00 | ~$0.50 |
| **Annual Hours** | ~2,000 hours | ~8,760 hours |

**The 'Aha!' Moment:** A Digital FTE works nearly 9,000 hours a year vs a human's 2,000. The cost per task reduction (from ~$5.00 to ~$0.50) is an 85–90% cost saving.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Digital FTE Architecture                  │
├─────────────────────────────────────────────────────────────┤
│  Perception Layer (Watchers)                                │
│  ├── Gmail Watcher (monitors emails)                        │
│  ├── WhatsApp Watcher (monitors messages)                   │
│  ├── LinkedIn Watcher (monitors posts/engagement)           │
│  ├── Facebook Watcher (monitors page activity)              │
│  ├── Instagram Watcher (monitors engagement)                │
│  ├── File System Watcher (monitors drops)                   │
│  └── CEO Briefing Generator (weekly audits)                 │
├─────────────────────────────────────────────────────────────┤
│  Reasoning Layer (Claude Code / Hugging Face)               │
│  ├── Reads from /Inbox, /Needs_Action                       │
│  ├── Creates Plan.md files with action items                │
│  ├── Generates CEO Briefings                                │
│  └── Supports: Llama 3, Mistral, Qwen, Phi-3                │
├─────────────────────────────────────────────────────────────┤
│  Action Layer (MCP Servers)                                 │
│  ├── Email MCP (send/draft emails)                          │
│  ├── LinkedIn MCP (auto-posting, engagement)                │
│  ├── Facebook MCP (page management)                         │
│  ├── Odoo MCP (invoicing, accounting)                       │
│  └── Audit MCP (logging & compliance)                       │
├─────────────────────────────────────────────────────────────┤
│  Memory/GUI (Obsidian Vault + Web Dashboard)                │
│  ├── Dashboard.md (real-time status)                        │
│  ├── Company_Handbook.md (rules of engagement)              │
│  ├── Business_Goals.md (objectives & metrics)               │
│  ├── /Inbox, /Needs_Action, /Done folders                   │
│  ├── /Pending_Approval (human-in-the-loop)                  │
│  └── Web Dashboard (Gradio-based UI)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Achievement Tiers

This project implements **all four tiers**, achieving **PLATINUM status** with 35/35 requirements complete.

### 🥉 Bronze Tier (Foundation)
**Time:** 8-12 hours | **Status:** ✅ Complete

- [x] Obsidian vault with Dashboard.md and Company_Handbook.md
- [x] One working Watcher script (File System monitoring)
- [x] Claude Code integration for reading/writing to vault
- [x] Basic folder structure: /Inbox, /Needs_Action, /Done
- [x] Agent Skill documentation (vault-operations)

**Read more:** [BRONZE_README.md](BRONZE_README.md)

### 🥈 Silver Tier (Functional Assistant)
**Time:** 20-30 hours | **Status:** ✅ Complete

- [x] All Bronze requirements plus:
- [x] Multiple Watcher scripts (Gmail, LinkedIn, WhatsApp)
- [x] LinkedIn auto-posting for business generation
- [x] Claude reasoning loop that creates Plan.md files
- [x] Email MCP server for sending emails
- [x] Human-in-the-loop approval workflow
- [x] Basic scheduling via cron or Task Scheduler
- [x] 8 Agent Skills total

**Read more:** [SILVER_README.md](SILVER_README.md)

### 🥇 Gold Tier (Autonomous Employee)
**Time:** 40+ hours | **Status:** ✅ Complete

- [x] All Silver requirements plus:
- [x] Full cross-domain integration (Personal + Business)
- [x] Odoo accounting integration (alternative to Xero)
- [x] Facebook & Instagram integration
- [x] Multiple MCP servers for different action types
- [x] Weekly Business and Accounting Audit with CEO Briefing
- [x] Error recovery and graceful degradation
- [x] Comprehensive audit logging
- [x] 13 Agent Skills total

**Read more:** [GOLD_README.md](GOLD_README.md)

### 💎 Platinum Tier (Open-Source Cloud Deployment)
**Time:** 50+ hours | **Status:** ✅ Complete

- [x] All Gold Tier requirements complete
- [x] Replace Claude Code with Hugging Face LLMs
- [x] Support for multiple open-source models (Llama 3, Mistral, Qwen, Phi-3)
- [x] Web Dashboard (Gradio-based)
- [x] REST API (FastAPI backend)
- [x] Docker deployment (Docker Compose)
- [x] CI/CD pipeline (GitHub Actions)
- [x] Real-time WebSocket monitoring
- [x] 15 Agent Skills total

**Read more:** [PLATINUM_README.md](PLATINUM_README.md)

---

## 📁 Project Structure

```
Personal-AI-Employ/
├── 📁 AI_Employee_Vault/          # Obsidian vault (knowledge base)
│   ├── Dashboard.md               # Real-time status dashboard
│   ├── Company_Handbook.md        # Rules of engagement
│   ├── Business_Goals.md          # Business objectives & metrics
│   ├── Inbox/                     # Drop folder for files
│   ├── Needs_Action/              # Items requiring attention
│   ├── Done/                      # Completed items
│   ├── Pending_Approval/          # Awaiting human approval
│   ├── Approved/                  # Approved actions
│   ├── Rejected/                  # Rejected actions
│   ├── Plans/                     # Action plans
│   ├── Briefings/                 # CEO briefings
│   ├── Accounting/                # Financial records
│   ├── Logs/                      # Activity logs
│   └── Invoices/                  # Generated invoices
│
├── 📁 watchers/                   # Perception layer
│   ├── base_watcher.py            # Abstract base class
│   ├── gmail_watcher.py           # Gmail API monitor
│   ├── gmail_smart_responder.py   # AI email responses
│   ├── linkedin_watcher.py        # LinkedIn monitor
│   ├── linkedin_auto_poster.py    # Auto-posting
│   ├── facebook_watcher.py        # Facebook monitor
│   ├── instagram_watcher.py       # Instagram monitor
│   ├── whatsapp_watcher.py        # WhatsApp monitor
│   ├── filesystem_watcher.py      # File drops
│   ├── ceo_briefing_generator.py  # Weekly audits
│   ├── audit_logger.py            # Compliance logging
│   └── requirements.txt           # Python dependencies
│
├── 📁 mcp-servers/                # Action layer
│   ├── email_mcp_server.py        # Gmail integration
│   ├── linkedin_mcp_server.py     # LinkedIn API
│   ├── facebook_mcp_server.py     # Facebook Graph API
│   ├── odoo_mcp_server.py         # Odoo ERP
│   ├── audit_mcp_server.py        # Audit logging
│   └── README.md                  # MCP documentation
│
├── 📁 platinum/                   # Platinum tier (open-source)
│   ├── huggingface_reasoning_engine.py
│   ├── huggingface_agent.py
│   ├── model_router.py
│   ├── prompt_templates.py
│   └── requirements.txt
│
├── 📁 web_dashboard/              # Platinum tier (web UI)
│   ├── app.py                     # Gradio web interface
│   ├── api.py                     # FastAPI backend
│   ├── dashboard.py               # Dashboard components
│   └── requirements.txt
│
├── 📁 deployment/                 # Deployment configs
│   ├── Dockerfile                 # Main Dockerfile
│   ├── docker-compose.yml         # Docker Compose
│   ├── huggingface_space/         # HF Spaces deployment
│   └── kubernetes/                # K8s configs (optional)
│
├── 📁 .qwen/skills/               # Agent Skills (15 total)
│   ├── vault-operations/
│   ├── browsing-with-playwright/
│   ├── email-mcp/
│   ├── gmail-watcher/
│   ├── linkedin-mcp/
│   ├── whatsapp-watcher/
│   ├── scheduler/
│   ├── approval-workflow/
│   ├── facebook-integration/
│   ├── instagram-integration/
│   ├── odoo-integration/
│   ├── ceo-briefing-generator/
│   ├── audit-logging/
│   ├── huggingface-deployment/    # Platinum
│   └── web-dashboard/             # Platinum
│
├── 📁 .github/workflows/          # CI/CD
│   └── deploy-huggingface.yml
│
├── orchestrator.py                # Master process manager
├── .env.example                   # Environment template
├── mcp-config.json                # MCP configuration
├── README.md                      # This file
├── hackathon 0.md                 # Original requirements
└── [TIER_README.md files]         # Tier documentation
```

---

## 🚀 Quick Start

### Prerequisites

| Component | Requirement | Purpose |
|-----------|-------------|---------|
| [Claude Code](https://claude.com/product/claude-code) | Active subscription | Primary reasoning engine |
| [Obsidian](https://obsidian.md/download) | v1.10.6+ | Knowledge base & dashboard |
| [Python](https://python.org/downloads/) | 3.13+ | Watcher scripts & orchestration |
| [Node.js](http://node.js) | v24+ LTS | MCP servers & automation |
| [GitHub Desktop](https://desktop.github.com/download/) | Latest | Version control |

**Hardware Requirements:**
- Minimum: 8GB RAM, 4-core CPU, 20GB free disk space
- Recommended: 16GB RAM, 8-core CPU, SSD storage

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd Personal-AI-Employ

# 2. Create Obsidian vault structure
mkdir -p AI_Employee_Vault/{Inbox,Needs_Action,Done,Pending_Approval,Approved,Rejected,Plans,Briefings,Accounting,Logs,Invoices}

# 3. Install Python dependencies
pip install -r watchers/requirements.txt
pip install -r platinum/requirements.txt
pip install -r web_dashboard/requirements.txt

# 4. Copy environment template
cp .env.example .env
# Edit .env with your API keys

# 5. Initialize Obsidian vault
# Open Obsidian and point to AI_Employee_Vault folder
```

### Configure Environment

```bash
# .env file
# Claude Code (for Bronze/Silver/Gold)
CLAUDE_API_KEY=your_claude_key

# Hugging Face (for Platinum)
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HUGGINGFACE_MODEL=meta-llama/Meta-Llama-3-70B-Instruct

# Gmail API
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret

# LinkedIn API
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret

# Facebook Graph API
FACEBOOK_ACCESS_TOKEN=your_token
FACEBOOK_PAGE_ID=your_page_id

# Odoo ERP
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_API_KEY=your_api_key
```

### Run Bronze Tier (Minimum)

```bash
# Terminal 1 - Run File System Watcher
cd watchers
python filesystem_watcher.py ../AI_Employee_Vault

# Terminal 2 - Run Orchestrator
cd ..
python orchestrator.py AI_Employee_Vault

# Terminal 3 - Trigger Claude Code manually
cd AI_Employee_Vault
claude --prompt "Process items in Needs_Action folder"
```

### Run Full Platinum Tier

```bash
# Terminal 1 - Hugging Face Reasoning Engine
cd platinum
python huggingface_reasoning_engine.py --server

# Terminal 2 - Web Dashboard
cd web_dashboard
python app.py ../AI_Employee_Vault --port 7860

# Terminal 3-10 - All Watchers
cd ..
python watchers/gmail_watcher.py AI_Employee_Vault &
python watchers/linkedin_watcher.py AI_Employee_Vault &
python watchers/facebook_watcher.py AI_Employee_Vault &
python watchers/instagram_watcher.py AI_Employee_Vault &
python watchers/filesystem_watcher.py AI_Employee_Vault &
python orchestrator.py AI_Employee_Vault

# Access Web Dashboard at: http://localhost:7860
```

### Deploy with Docker (Platinum)

```bash
cd deployment
docker-compose up -d

# Services:
# - Dashboard: http://localhost:7860
# - API: http://localhost:8000
# - Reasoning Engine: http://localhost:8001
```

### Deploy to Hugging Face Spaces (Platinum)

```bash
cd deployment
python deploy_to_huggingface.py --repo your-username/ai-employee-platinum

# Access at: https://huggingface.co/spaces/your-username/ai-employee-platinum
```

---

## 🤖 Agent Skills (15 Total)

| # | Skill | Tier | Purpose |
|---|-------|------|---------|
| 1 | vault-operations | Bronze | Read/write Obsidian vault |
| 2 | browsing-with-playwright | Bronze | Web automation |
| 3 | email-mcp | Silver | Send/draft emails |
| 4 | gmail-watcher | Silver | Monitor Gmail |
| 5 | linkedin-mcp | Silver | LinkedIn posting |
| 6 | whatsapp-watcher | Silver | WhatsApp monitoring |
| 7 | scheduler | Silver | Task scheduling |
| 8 | approval-workflow | Silver | HITL approvals |
| 9 | facebook-integration | Gold | Facebook Graph API |
| 10 | instagram-integration | Gold | Instagram posting |
| 11 | odoo-integration | Gold | Odoo ERP integration |
| 12 | ceo-briefing-generator | Gold | Weekly business audits |
| 13 | audit-logging | Gold | Compliance logging |
| 14 | huggingface-deployment | Platinum | HF LLM deployment |
| 15 | web-dashboard | Platinum | Gradio web UI |

---

## 📊 Tier Comparison

| Feature | Bronze | Silver | Gold | Platinum |
|---------|--------|--------|------|----------|
| **Reasoning Engine** | Claude Code | Claude Code | Claude Code | Hugging Face (Open Source) |
| **Watchers** | 1-2 | 3-5 | 5-8 | 5-8 |
| **MCP Servers** | 0-1 | 2-3 | 5 | 5 |
| **Web Dashboard** | ❌ | ❌ | ❌ | ✅ Gradio |
| **REST API** | ❌ | ❌ | ❌ | ✅ FastAPI |
| **Deployment** | Local | Local | Local | Local + Cloud (HF) |
| **Model Choice** | Claude only | Claude only | Claude only | 6+ Open Source |
| **Cost** | ~$20/mo | ~$20/mo | ~$20/mo | **FREE** |
| **Docker** | Basic | Basic | Basic | Full Compose |
| **CI/CD** | ❌ | ❌ | ❌ | ✅ GitHub Actions |
| **Agent Skills** | 2 | 8 | 13 | **15** |

---

## 🔑 Key Features

### 📬 Watcher Pattern
Lightweight Python scripts that run continuously, monitoring various inputs and creating actionable `.md` files in the `Needs_Action` folder.

### 🧠 Human-in-the-Loop (HITL)
For sensitive actions (payments, approvals), the AI writes an approval request file. The user must move the file to `/Approved` before the action executes.

### 📊 CEO Briefing
A scheduled feature where the AI autonomously audits bank transactions and tasks to generate a "Monday Morning CEO Briefing" highlighting revenue, bottlenecks, and proactive suggestions.

### 🔐 Security First
- Credentials stored in environment variables (never in vault)
- Dry-run mode for testing
- Audit logging for all actions
- Rate limiting and permission boundaries

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [hackathon 0.md](hackathon%200.md) | Original requirements & architecture |
| [BRONZE_README.md](BRONZE_README.md) | Bronze Tier guide |
| [SILVER_README.md](SILVER_README.md) | Silver Tier guide |
| [GOLD_README.md](GOLD_README.md) | Gold Tier guide |
| [PLATINUM_README.md](PLATINUM_README.md) | Platinum Tier guide |
| [PLATINUM_VERIFICATION.md](PLATINUM_VERIFICATION.md) | Complete verification |
| [MCP_SERVER_SETUP.md](MCP_SERVER_SETUP.md) | MCP server configuration |
| [COMPLETE_SETUP.md](COMPLETE_SETUP.md) | Full setup instructions |

---

## 🧪 Testing

```bash
# Test watchers
python watchers/gmail_watcher.py AI_Employee_Vault --test

# Test MCP servers
cd mcp-servers
python email_mcp_server.py --test

# Test Hugging Face integration (Platinum)
cd platinum
python huggingface_reasoning_engine.py --test

# Test web dashboard (Platinum)
cd web_dashboard
python app.py ../AI_Employee_Vault --test

# Run full test suite
pytest tests/ -v
```

---

## 🔐 Security & Privacy

### Credential Management
- Never store credentials in plain text or vault
- Use environment variables for API keys
- Use secrets manager for banking credentials (Keychain, 1Password)
- Rotate credentials monthly

### Audit Logging
Every action is logged with:
```json
{
  "timestamp": "2026-01-07T10:30:00Z",
  "action_type": "email_send",
  "actor": "claude_code",
  "target": "client@example.com",
  "approval_status": "approved",
  "approved_by": "human",
  "result": "success"
}
```

### Permission Boundaries
| Action Category | Auto-Approve | Always Require Approval |
|-----------------|--------------|------------------------|
| Email replies | To known contacts | New contacts, bulk sends |
| Payments | < $50 recurring | All new payees, > $100 |
| Social media | Scheduled posts | Replies, DMs |
| File operations | Create, read | Delete, move outside vault |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

### Development Conventions
1. **Local-first:** Keep data local in Obsidian Markdown files
2. **Human-in-the-loop:** Never auto-execute sensitive actions
3. **Watcher pattern:** Use lightweight scripts for monitoring
4. **Audit logging:** Log all actions for transparency

---

## 📅 Research Meetings

**Weekly Research Meeting:** Every Wednesday at 10:00 PM on Zoom

- **Zoom Link:** https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1
- **Meeting ID:** 871 8870 7642
- **Passcode:** 744832

**YouTube Channel:** https://www.youtube.com/@panaversity

---

## 🏆 Project Status

| Metric | Status |
|--------|--------|
| **Total Requirements** | 35 |
| **Requirements Complete** | 35/35 (100%) |
| **Current Tier** | 💎 Platinum |
| **Agent Skills** | 15 |
| **Watcher Scripts** | 8 |
| **MCP Servers** | 5 |
| **Vault Folders** | 11 |
| **Python Scripts** | 30+ |
| **Documentation Files** | 15+ |

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Claude Code** by Anthropic - Primary reasoning engine
- **Obsidian** - Knowledge base platform
- **Hugging Face** - Open-source LLM hosting
- **Playwright** - Web automation
- **FastAPI** - REST API framework
- **Gradio** - Web dashboard UI

---

## 📞 Support

- **Documentation:** See [Documentation Index](#-documentation) above
- **Issues:** Open a GitHub issue
- **Discussions:** GitHub Discussions tab
- **Research Meetings:** Wednesdays 10:00 PM on Zoom

---

**🎉 Congratulations! Your AI Employee is ready for deployment!**

*Built with ❤️ during the Personal AI Employee Hackathon 2026*
