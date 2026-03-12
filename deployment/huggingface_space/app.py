# Hugging Face Spaces Deployment for AI Employee Platinum Tier
# This folder contains files for deploying to Hugging Face Spaces

# app.py - Main Gradio app for Hugging Face Spaces
import os
import gradio as gr
from pathlib import Path
from datetime import datetime
import json

# Import from platinum module
import sys
sys.path.insert(0, '/app')

try:
    from platinum.huggingface_agent import HuggingFaceAgent
    from platinum.huggingface_reasoning_engine import HuggingFaceReasoningEngine
except ImportError:
    print("Warning: Could not import platinum modules. Running in demo mode.")


# Configuration
VAULT_PATH = os.getenv("VAULT_PATH", "/tmp/ai_employee_vault")
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")
MODEL_NAME = os.getenv("HUGGINGFACE_MODEL", "meta-llama/Meta-Llama-3-70B-Instruct")

# Ensure vault structure exists
def ensure_vault_structure():
    """Ensure all vault folders exist"""
    vault = Path(VAULT_PATH)
    folders = [
        "Inbox", "Needs_Action", "Done", "Pending_Approval",
        "Approved", "Rejected", "Plans", "Briefings",
        "Accounting", "Logs", "Audit"
    ]
    for folder in folders:
        (vault / folder).mkdir(parents=True, exist_ok=True)
    
    # Create default files if they don't exist
    dashboard_file = vault / "Dashboard.md"
    if not dashboard_file.exists():
        dashboard_file.write_text("""---
last_updated: 2026-03-07
status: active
---

# AI Employee Dashboard

_Status: Running on Hugging Face Spaces_

## Quick Status

| Metric | Count |
|--------|-------|
| Needs Action | 0 |
| Pending Approval | 0 |
| Completed Today | 0 |

---

*Powered by Hugging Face - Platinum Tier*
""")
    
    handbook_file = vault / "Company_Handbook.md"
    if not handbook_file.exists():
        handbook_file.write_text("""---
version: 1.0
last_updated: 2026-03-07
---

# Company Handbook

## Rules of Engagement

1. Always be professional in communications
2. Flag payments over $500 for approval
3. Respond to emails within 24 hours
4. Review social media posts before posting

## Working Hours

- Monday - Friday: 9 AM - 6 PM
- Weekend: Emergency only

## Escalation Rules

- Urgent client issues: Immediate notification
- Payment issues: Flag for review
- Technical issues: Log and retry

---

*Customize this handbook for your business*
""")

ensure_vault_structure()


# Initialize agent (with error handling for demo mode)
try:
    agent = HuggingFaceAgent(
        vault_path=VAULT_PATH,
        model_name=MODEL_NAME if HF_TOKEN else None,
        use_router=False
    )
    AGENT_AVAILABLE = True
except Exception as e:
    print(f"Agent initialization failed: {e}. Running in demo mode.")
    AGENT_AVAILABLE = False


def get_vault_counts():
    """Get counts for all vault folders"""
    vault = Path(VAULT_PATH)
    counts = {}
    folders = ["Needs_Action", "Pending_Approval", "Approved", "Done", "Briefings"]
    
    for folder in folders:
        folder_path = vault / folder
        if folder_path.exists():
            counts[folder] = len(list(folder_path.glob("*.md")))
        else:
            counts[folder] = 0
    
    return counts


def generate_status_markdown(counts):
    """Generate status markdown"""
    return f"""
### 📊 Vault Status

| Folder | Count |
|--------|-------|
| Needs Action | {counts.get('Needs_Action', 0)} |
| Pending Approval | {counts.get('Pending_Approval', 0)} |
| Done | {counts.get('Done', 0)} |
| Briefings | {counts.get('Briefings', 0)} |

_Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_

**Model:** {MODEL_NAME}
**Status:** {'✅ Connected' if AGENT_AVAILABLE else '⚠️ Demo Mode'}
"""


def list_folder(folder_name):
    """List files in a vault folder"""
    folder_path = Path(VAULT_PATH) / folder_name
    if not folder_path.exists():
        return []
    
    return sorted([f.name for f in folder_path.glob("*.md")], reverse=True)


def read_file(folder, filename):
    """Read a file from the vault"""
    if not filename:
        return ""
    
    file_path = Path(VAULT_PATH) / folder / filename
    if file_path.exists():
        return file_path.read_text()
    
    return "File not found"


def move_file(src_folder, filename, dst_folder):
    """Move a file between folders"""
    if not filename:
        return "No file selected"
    
    src = Path(VAULT_PATH) / src_folder / filename
    dst = Path(VAULT_PATH) / dst_folder / filename
    
    if src.exists():
        dst.parent.mkdir(exist_ok=True)
        src.rename(dst)
        return f"✅ Moved {filename} to {dst_folder}"
    
    return "File not found"


def process_task(task_name):
    """Process a task using the agent"""
    if not AGENT_AVAILABLE:
        return "Demo mode: Agent not available. Connect Hugging Face token to enable."
    
    task_path = Path(VAULT_PATH) / "Needs_Action" / task_name
    if not task_path.exists():
        return "Task not found"
    
    try:
        result = agent.process_single_item(task_path)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return f"Error processing task: {str(e)}"


def generate_briefing(briefing_type):
    """Generate a briefing"""
    if not AGENT_AVAILABLE:
        return """---
generated: """ + datetime.now().isoformat() + """
type: """ + briefing_type.lower() + """
status: demo_mode
---

# """ + briefing_type + """ CEO Briefing

*Demo Mode - Connect Hugging Face token to generate real briefings*

## Executive Summary

This is a demo briefing. To generate real briefings:

1. Get a Hugging Face token from: https://huggingface.co/settings/tokens
2. Add it as a secret in your Space settings
3. Restart the Space

## Revenue

- This Period: $0.00 (demo)
- Trend: Stable

## Completed Tasks

- Task 1 (demo)
- Task 2 (demo)

## Proactive Suggestions

1. Configure Hugging Face token
2. Add your business data
3. Start using AI Employee!

---

*AI Employee Platinum Tier - Demo Mode*
"""
    
    try:
        if briefing_type == "Daily":
            path = agent.generate_daily_briefing()
        else:
            path = agent.generate_weekly_briefing()
        return path.read_text()
    except Exception as e:
        return f"Error generating briefing: {str(e)}"


def query_agent(query, context=""):
    """Query the reasoning agent"""
    if not AGENT_AVAILABLE:
        return "Demo mode: Agent not available. Please add a Hugging Face token to enable the reasoning engine."
    
    try:
        response = agent.engine.reason(query, context)
        return response
    except Exception as e:
        return f"Error querying agent: {str(e)}"


# Create Gradio Interface
with gr.Blocks(title="AI Employee Platinum", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🤖 AI Employee - Platinum Tier
    ### Powered by Hugging Face & Open-Source LLMs
    
    _Your life and business on autopilot. Deploy on Hugging Face Spaces._
    """)
    
    # Status Row
    with gr.Row():
        with gr.Column(scale=1):
            status_display = gr.Markdown(generate_status_markdown(get_vault_counts()))
        
        with gr.Column(scale=2):
            gr.Markdown("""
            ### 🚀 Quick Actions
            
            - **Monitor** emails, LinkedIn, Facebook, Instagram
            - **Auto-reply** to messages
            - **Generate** CEO briefings
            - **Track** accounting and invoices
            - **Approve** sensitive actions
            
            ### 📁 Vault Files
            
            Upload files to the vault or use the watchers to auto-populate.
            """)
    
    # Tabs
    with gr.Tab("📋 Task Management"):
        gr.Markdown("## Task Management")
        
        with gr.Row():
            with gr.Column(scale=1):
                needs_action_files = gr.Dropdown(
                    choices=list_folder("Needs_Action"),
                    label="Needs Action",
                    interactive=True
                )
            
            with gr.Column(scale=2):
                task_content = gr.Textbox(
                    label="Task Content",
                    lines=10,
                    interactive=False
                )
        
        with gr.Row():
            process_btn = gr.Button("⚙️ Process Task", variant="primary")
            approve_btn = gr.Button("✅ Approve (Move to Approved)", variant="primary")
            reject_btn = gr.Button("❌ Reject (Move to Rejected)", variant="stop")
        
        process_output = gr.Textbox(label="Processing Result", lines=10)
        
        needs_action_files.change(
            fn=lambda x: read_file("Needs_Action", x),
            inputs=[needs_action_files],
            outputs=[task_content]
        )
        
        process_btn.click(
            fn=process_task,
            inputs=[needs_action_files],
            outputs=[process_output]
        )
        
        approve_btn.click(
            fn=lambda x: move_file("Needs_Action", x, "Approved"),
            inputs=[needs_action_files],
            outputs=[process_output]
        )
        
        reject_btn.click(
            fn=lambda x: move_file("Needs_Action", x, "Rejected"),
            inputs=[needs_action_files],
            outputs=[process_output]
        )
    
    with gr.Tab("📊 CEO Briefings"):
        gr.Markdown("## CEO Briefings")
        
        with gr.Row():
            with gr.Column(scale=1):
                briefing_type = gr.Radio(
                    choices=["Daily", "Weekly"],
                    label="Briefing Type",
                    value="Weekly"
                )
                generate_briefing_btn = gr.Button("📝 Generate Briefing", variant="primary")
            
            with gr.Column(scale=1):
                briefings_files = gr.Dropdown(
                    choices=list_folder("Briefings"),
                    label="Existing Briefings",
                    interactive=True
                )
        
        briefing_content = gr.Textbox(
            label="Briefing Content",
            lines=20,
            interactive=False
        )
        
        generate_briefing_btn.click(
            fn=generate_briefing,
            inputs=[briefing_type],
            outputs=[briefing_content]
        )
        
        briefings_files.change(
            fn=lambda x: read_file("Briefings", x),
            inputs=[briefings_files],
            outputs=[briefing_content]
        )
    
    with gr.Tab("💬 Query Agent"):
        gr.Markdown("## Query the AI Agent")
        
        query_input = gr.Textbox(
            label="Your Query",
            placeholder="Ask the AI Employee anything about your business...",
            lines=3
        )
        
        context_input = gr.Textbox(
            label="Additional Context (optional)",
            placeholder="Provide business context...",
            lines=2
        )
        
        query_btn = gr.Button("🤖 Query Agent", variant="primary")
        query_output = gr.Textbox(
            label="Agent Response",
            lines=10,
            interactive=False
        )
        
        query_btn.click(
            fn=query_agent,
            inputs=[query_input, context_input],
            outputs=[query_output]
        )
    
    with gr.Tab("📁 File Browser"):
        gr.Markdown("## Browse Vault Files")
        
        with gr.Row():
            folder_select = gr.Dropdown(
                choices=["Needs_Action", "Approved", "Done", "Plans", "Briefings", "Logs"],
                label="Folder",
                value="Needs_Action"
            )
            
            file_select = gr.Dropdown(
                choices=[],
                label="File",
                interactive=True
            )
        
        file_content = gr.Textbox(
            label="File Content",
            lines=20,
            interactive=False
        )
        
        def update_file_list(folder):
            return gr.Dropdown(choices=list_folder(folder))
        
        folder_select.change(
            fn=update_file_list,
            inputs=[folder_select],
            outputs=[file_select]
        )
        
        file_select.change(
            fn=lambda folder, file: read_file(folder, file),
            inputs=[folder_select, file_select],
            outputs=[file_content]
        )
    
    with gr.Tab("⚙️ Settings"):
        gr.Markdown("## Settings")
        
        gr.Markdown(f"""
        ### Current Configuration
        
        - **Vault Path:** {VAULT_PATH}
        - **Model:** {MODEL_NAME}
        - **Hugging Face Token:** {'✅ Set' if HF_TOKEN else '❌ Not Set'}
        - **Agent Status:** {'✅ Available' if AGENT_AVAILABLE else '⚠️ Demo Mode'}
        
        ### To Enable Full Functionality
        
        1. Get a Hugging Face token from: https://huggingface.co/settings/tokens
        2. Add it as a secret in your Space settings (HUGGINGFACE_TOKEN)
        3. Restart the Space
        4. Optionally set HUGGINGFACE_MODEL to use a different model
        
        ### Environment Variables
        
        - `VAULT_PATH`: Path to Obsidian vault (default: /tmp/ai_employee_vault)
        - `HUGGINGFACE_TOKEN`: Your Hugging Face API token
        - `HUGGINGFACE_MODEL`: Model to use (default: meta-llama/Meta-Llama-3-70B-Instruct)
        """)
    
    # Refresh button
    refresh_btn = gr.Button("🔄 Refresh Status", variant="secondary")
    refresh_btn.click(
        fn=lambda: generate_status_markdown(get_vault_counts()),
        inputs=[],
        outputs=[status_display]
    )


# Launch
if __name__ == "__main__":
    demo.launch(server_port=int(os.getenv("PORT", "7860")))
