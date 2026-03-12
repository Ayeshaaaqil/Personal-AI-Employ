# 🚀 Platinum Tier - Quick Reference Card

**AI Employee Platinum Tier - Open Source Cloud Deployment**

---

## ⚡ 1-Minute Setup

```bash
# 1. Install
pip install -r platinum/requirements.txt

# 2. Set Token
export HUGGINGFACE_TOKEN=hf_xxxxx

# 3. Run Dashboard
cd web_dashboard && python app.py ../AI_Employee_Vault

# 4. Open Browser
# http://localhost:7860
```

---

## 📋 Essential Commands

### Test Connection
```bash
python platinum/huggingface_reasoning_engine.py --test
```

### Run Web Dashboard
```bash
python web_dashboard/app.py AI_Employee_Vault --port 7860
```

### Deploy to Hugging Face
```bash
python deployment/deploy_to_huggingface.py --repo username/ai-employee-platinum
```

### Run with Docker
```bash
cd deployment && docker-compose up -d
```

### Query Model
```bash
python platinum/huggingface_agent.py AI_Employee_Vault --process
```

### Generate Briefing
```bash
python platinum/huggingface_agent.py AI_Employee_Vault --briefing
```

---

## 🤖 Supported Models

| Model | Size | Speed | Best For |
|-------|------|-------|----------|
| **Llama 3 70B** | 70B | Medium | General reasoning |
| **Llama 3 8B** | 8B | Fast | Quick tasks |
| **Mistral 7B** | 7B | Fast | Fast inference |
| **Qwen 2.5 72B** | 72B | Slow | Multi-language |
| **Phi-3 Medium** | 14B | Medium | Long context |

---

## 🌐 URLs

| Service | URL |
|---------|-----|
| **Local Dashboard** | http://localhost:7860 |
| **Local API** | http://localhost:8000 |
| **Hugging Face Spaces** | https://huggingface.co/spaces/{username}/{repo} |
| **Get HF Token** | https://huggingface.co/settings/tokens |

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `platinum/huggingface_reasoning_engine.py` | Main HF integration |
| `platinum/huggingface_agent.py` | Agent wrapper |
| `web_dashboard/app.py` | Gradio web UI |
| `deployment/deploy_to_huggingface.py` | Deploy script |
| `PLATINUM_README.md` | Full documentation |

---

## 🔧 Environment Variables

```bash
# Required
HUGGINGFACE_TOKEN=hf_xxxxx

# Optional
HUGGINGFACE_MODEL=meta-llama/Meta-Llama-3-70B-Instruct
WEB_DASHBOARD_PORT=7860
API_KEY=your_secret_key
```

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| **401 Unauthorized** | Check HF token is valid |
| **429 Rate Limit** | Switch to smaller model |
| **Port in use** | Use `--port 7861` |
| **Module not found** | `pip install -r requirements.txt` |
| **Deploy failed** | Check repo name format |

---

## 📊 API Endpoints

```bash
# List tasks
GET /api/v1/tasks/list

# Generate briefing
POST /api/v1/briefings/generate

# Query AI
POST /api/v1/query

# Switch model
POST /api/v1/models/switch

# Get status
GET /api/v1/status
```

---

## 💰 Cost Comparison

| Solution | Monthly | Annual |
|----------|---------|--------|
| Claude Pro | $20 | $240 |
| **HF Free** | **$0** | **$0** |
| **Savings** | **100%** | **$240** |

---

## 🎯 Platinum Features

- ✅ **Open Source LLMs** - Llama, Mistral, Qwen
- ✅ **Web Dashboard** - Gradio-based UI
- ✅ **REST API** - FastAPI backend
- ✅ **Docker Deploy** - Containerized
- ✅ **HF Spaces** - Free cloud hosting
- ✅ **Model Router** - Auto-fallback
- ✅ **100% FREE** - No API costs

---

## 📚 Documentation

- **Full Guide**: `PLATINUM_README.md`
- **Verification**: `PLATINUM_VERIFICATION.md`
- **Summary**: `PLATINUM_SUMMARY.md`
- **Skills**: `.qwen/skills/huggingface-deployment/`

---

## 🆘 Get Help

1. Check documentation in `PLATINUM_README.md`
2. Review troubleshooting in `SKILL.md`
3. Join Wednesday Research Meetings (10 PM Zoom)
4. Check Hugging Face docs

---

**🏆 All Tiers Complete: Bronze ✅ Silver ✅ Gold ✅ Platinum ✅**
