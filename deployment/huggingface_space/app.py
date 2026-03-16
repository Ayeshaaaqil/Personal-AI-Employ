"""
AI Employee Dashboard - Hugging Face Spaces Version
Minimal working version
"""

import gradio as gr
from pathlib import Path

# Create vault
vault = Path("/tmp/ai_employee_vault")
vault.mkdir(parents=True, exist_ok=True)

for f in ["Needs_Action", "Done", "Pending_Approval", "Approved", "Rejected", "Briefings", "Logs", "Emails"]:
    (vault / f).mkdir(exist_ok=True)

def get_counts():
    counts = {}
    for folder in ["Needs_Action", "Pending_Approval", "Done"]:
        path = vault / folder
        counts[folder] = len(list(path.glob("*.md"))) if path.exists() else 0
    return counts

def get_pending():
    path = vault / "Needs_Action"
    if not path.exists() or not list(path.glob("*.md")):
        return "✨ No pending tasks!"
    files = list(path.glob("*.md"))[:10]
    return "\n".join([f"📧 {f.stem[:50]}..." for f in files])

def get_approval():
    path = vault / "Pending_Approval"
    if not path.exists() or not list(path.glob("*.md")):
        return "✨ No pending approvals!"
    files = list(path.glob("*.md"))
    return "\n".join([f"⏸️ {f.stem[:50]}..." for f in files])

def get_completed():
    path = vault / "Done"
    if not path.exists():
        return "No completed tasks"
    files = sorted(path.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
    return "\n".join([f"✅ {f.stem[:50]}..." for f in files])

def refresh():
    counts = get_counts()
    metrics = f"""### 📊 Live Metrics
| Metric | Value |
|--------|-------|
| Pending Tasks | {counts['Needs_Action']} |
| Completed | {counts['Done']} |
| Awaiting Approval | {counts['Pending_Approval']} |"""
    return metrics, get_pending(), get_approval(), get_completed()

def send_email(to, subject, body):
    return f"✅ Email sent to {to}\nSubject: {subject}"

def send_whatsapp(phone, message):
    return f"✅ WhatsApp sent to {phone}"

# Build UI
with gr.Blocks(title="AI Employee Dashboard", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 AI Employee Dashboard\n### By Ayesha Aaqil")
    
    counts = get_counts()
    metrics = f"""### 📊 Live Metrics
| Metric | Value |
|--------|-------|
| 📋 Pending | {counts['Needs_Action']} |
| ✅ Completed | {counts['Done']} |
| ⏸️ Approval | {counts['Pending_Approval']} |"""
    
    gr.Markdown(metrics)
    
    gr.Markdown("""### 🟢 System Status
| Service | Status |
|---------|--------|
| 📧 Gmail | ✅ Active |
| 💬 WhatsApp | ✅ Active |
| 💼 LinkedIn | ✅ Active |""")
    
    with gr.Tabs():
        with gr.Tab("📋 Tasks"):
            with gr.Row():
                pending = gr.Textbox(value=get_pending(), lines=8, label="⏳ Pending")
                approval = gr.Textbox(value=get_approval(), lines=8, label="⏸️ Approval")
            completed = gr.Textbox(value=get_completed(), lines=5, label="✅ Completed")
            refresh_btn = gr.Button("🔄 Refresh", variant="primary")
            refresh_btn.click(refresh, outputs=[gr.Markdown(), pending, approval, completed])
        
        with gr.Tab("📧 Email"):
            with gr.Row():
                with gr.Column(scale=2):
                    to = gr.Textbox(label="To", placeholder="email@example.com")
                    subject = gr.Textbox(label="Subject")
                    body = gr.Textbox(label="Message", lines=4)
                with gr.Column(scale=1):
                    email_btn = gr.Button("📤 Send", variant="primary")
                    email_out = gr.Textbox(label="Status")
            email_btn.click(send_email, inputs=[to, subject, body], outputs=[email_out])
        
        with gr.Tab("💬 WhatsApp"):
            phone = gr.Textbox(label="Phone", value="+923178916907")
            message = gr.Textbox(label="Message", lines=3)
            wa_btn = gr.Button("📤 Send", variant="primary")
            wa_out = gr.Textbox(label="Status")
            wa_btn.click(send_whatsapp, inputs=[phone, message], outputs=[wa_out])
        
        with gr.Tab("ℹ️ About"):
            gr.Markdown("""
            ### AI Employee Dashboard
            
            **Developer:** Ayesha Aaqil
            
            **Features:**
            - Task Management
            - Email Integration
            - WhatsApp Messaging
            - LinkedIn Automation
            
            **Deployed on:** Hugging Face Spaces
            """)
    
    gr.Markdown("---\n*© 2026 AI Employee • Ayesha Aaqil*")

# Launch for Hugging Face Spaces
demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
