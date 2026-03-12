# Web Dashboard Skill - Platinum Tier

**Skill Name:** `web-dashboard`

**Tier:** Platinum

**Description:** Gradio-based web interface for monitoring and controlling AI Employee.

---

## When to Use This Skill

Use this skill when you want to:

1. **Access web-based dashboard** - Browser-based UI instead of Obsidian
2. **Monitor in real-time** - Live updates of tasks and metrics
3. **Approve/reject tasks** - Web-based approval workflow
4. **Generate briefings** - On-demand CEO briefings
5. **Query the AI** - Chat interface with reasoning engine
6. **Browse vault files** - Web-based file explorer

---

## Server Lifecycle Management

### 1. Install Dependencies

```bash
cd C:\Users\Dell\Documents\GitHub\Personal-AI-Employ
pip install -r web_dashboard/requirements.txt
```

### 2. Start Web Dashboard

```bash
cd web_dashboard
python app.py AI_Employee_Vault --port 7860
```

### 3. Access Dashboard

Open browser to:
```
http://localhost:7860
```

### 4. Run in Background (Windows)

```powershell
# PowerShell
Start-Process python -ArgumentList "web_dashboard/app.py AI_Employee_Vault" -WindowStyle Hidden
```

### 5. Run with Docker

```bash
cd deployment
docker-compose up -d web-dashboard
```

Access at: `http://localhost:7860`

---

## Quick Reference

### Start Dashboard

```bash
cd web_dashboard
python app.py AI_Employee_Vault --port 7860
```

### Start with Public Link

```bash
python app.py AI_Employee_Vault --share
```

### Start Dashboard + API Server

```bash
# Terminal 1 - Dashboard
python app.py AI_Employee_Vault

# Terminal 2 - API Server
python api.py --port 8000
```

### Access via Docker

```bash
docker-compose up -d
# Dashboard: http://localhost:7860
# API: http://localhost:8000
```

---

## Dashboard Features

### 1. Task Management Tab

- **View Needs_Action items** - List of pending tasks
- **Process tasks** - Trigger AI to analyze and plan
- **Approve/Reject** - Move files between folders
- **View task details** - Read full task content

### 2. CEO Briefings Tab

- **Generate briefings** - Daily, Weekly, Monthly
- **View past briefings** - Browse briefing history
- **Download briefings** - Export as markdown

### 3. Audit Logs Tab

- **View logs** - Filter by date and text
- **Search logs** - Full-text search
- **Export logs** - Download as JSON

### 4. Query Agent Tab

- **Chat with AI** - Ask questions about your business
- **Get recommendations** - Proactive suggestions
- **Analyze data** - Transaction categorization, etc.

### 5. File Browser Tab

- **Browse vault** - Navigate all folders
- **View files** - Read markdown files
- **Search files** - Find specific content

### 6. Settings Tab

- **Model configuration** - Switch LLM models
- **Vault settings** - Configure vault path
- **System status** - Health monitoring

---

## REST API Endpoints

The web dashboard includes a FastAPI backend:

### Tasks

```bash
# List tasks
GET http://localhost:8000/api/v1/tasks/list

# Get task details
GET http://localhost:8000/api/v1/tasks/{filename}

# Approve task
POST http://localhost:8000/api/v1/tasks/{filename}/approve

# Reject task
POST http://localhost:8000/api/v1/tasks/{filename}/reject

# Process task
POST http://localhost:8000/api/v1/tasks/process
```

### Briefings

```bash
# Generate briefing
POST http://localhost:8000/api/v1/briefings/generate
{
  "type": "daily|weekly|monthly"
}

# List briefings
GET http://localhost:8000/api/v1/briefings/list

# Get briefing
GET http://localhost:8000/api/v1/briefings/{filename}
```

### Query

```bash
# Query AI
POST http://localhost:8000/api/v1/query
{
  "prompt": "What tasks are pending?",
  "context": "business"
}
```

### Models

```bash
# List models
GET http://localhost:8000/api/v1/models/list

# Switch model
POST http://localhost:8000/api/v1/models/switch
{
  "model": "mistralai/Mistral-7B-Instruct-v0.3"
}

# Get status
GET http://localhost:8000/api/v1/status
```

---

## Configuration

### Dashboard Configuration

Edit `web_dashboard/config.py`:

```python
DASHBOARD_CONFIG = {
    "port": 7860,
    "host": "0.0.0.0",
    "theme": "soft",
    "title": "AI Employee Dashboard",
    "refresh_interval": 30,  # seconds
    "max_logs": 1000
}
```

### API Configuration

Edit `web_dashboard/api_config.py`:

```python
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "api_key": "your_secret_key",
    "rate_limit": 100,  # requests per minute
    "cors_origins": ["*"]
}
```

---

## Troubleshooting

### Dashboard Won't Start

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 7860
netstat -ano | findstr :7860

# Kill process
taskkill /PID <PID> /F

# Or use different port
python app.py AI_Employee_Vault --port 7861
```

### Gradio Import Error

**Error:** `ModuleNotFoundError: No module named 'gradio'`

**Solution:**
```bash
pip install -r web_dashboard/requirements.txt
```

### Dashboard Slow to Load

**Solution:**
1. Check vault size (reduce if > 1000 files)
2. Enable file caching
3. Use smaller model for queries

### API Returns 401

**Error:** `401 Unauthorized`

**Solution:**
```bash
# Check API key in request
curl -H "Authorization: Bearer your_api_key" http://localhost:8000/api/v1/status
```

---

## Examples

### Example 1: Start Dashboard and Access

```bash
# Start
cd web_dashboard
python app.py ../AI_Employee_Vault --port 7860

# Open browser
# http://localhost:7860
```

### Example 2: Generate Briefing via API

```bash
curl -X POST http://localhost:8000/api/v1/briefings/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key" \
  -d '{"type": "weekly"}'
```

### Example 3: Query AI via API

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key" \
  -d '{
    "prompt": "What are the top 3 pending tasks?",
    "context": "business"
  }'
```

### Example 4: Switch Model via API

```bash
curl -X POST http://localhost:8000/api/v1/models/switch \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key" \
  -d '{
    "model": "Qwen/Qwen2.5-72B-Instruct"
  }'
```

---

## Customization

### Custom Theme

```python
# In app.py
import gradio as gr

# Create custom theme
custom_theme = gr.themes.Base(
    primary_hue="blue",
    secondary_hue="gray",
    neutral_hue="slate"
)

# Apply theme
demo = gr.Blocks(theme=custom_theme)
```

### Custom Widgets

```python
# Add custom metric display
with gr.Group():
    gr.Markdown("### 📊 Key Metrics")
    
    with gr.Row():
        gr.Number(label="Tasks Completed", value=42)
        gr.Number(label="Pending Tasks", value=7)
```

### Custom Endpoints

```python
# In api.py
@app.post("/api/v1/custom/endpoint")
async def custom_endpoint():
    return {"message": "Custom response"}
```

---

## Performance Optimization

### Enable Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_file_content(folder: str, filename: str) -> str:
    # Cached file reading
    pass
```

### Async Operations

```python
import asyncio

async def process_task_async(task_name: str):
    await asyncio.sleep(0)  # Non-blocking
    # Process task
```

### Database for Logs

For large vaults, use SQLite instead of JSON files:

```python
import sqlite3

conn = sqlite3.connect('audit_logs.db')
cursor = conn.cursor()
```

---

## Security Considerations

1. **Use API keys** - Require authentication for API access
2. **Enable HTTPS** - Use reverse proxy for production
3. **Rate limiting** - Prevent abuse
4. **Input validation** - Sanitize user inputs
5. **CORS configuration** - Restrict origins

---

## Additional Resources

- [Gradio Documentation](https://gradio.app/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Platinum Tier Documentation](../../PLATINUM_README.md)
- [Hugging Face Deployment Skill](../huggingface-deployment/SKILL.md)

---

*Platinum Tier Skill - AI Employee*
