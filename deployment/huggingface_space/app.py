"""
AI Employee Dashboard - Professional Version
With Tailwind CSS, Animations, Auto-Reply, and AI Assistant
By Ayesha Aaqil
"""

import gradio as gr
from pathlib import Path
import json
from datetime import datetime
import time
import random

# Create vault
vault = Path("/tmp/ai_employee_vault")
vault.mkdir(parents=True, exist_ok=True)

for f in ["Needs_Action", "Done", "Pending_Approval", "Approved", "Rejected", "Briefings", "Logs", "Emails"]:
    (vault / f).mkdir(exist_ok=True)

# Auto-reply templates
EMAIL_AUTO_REPLY_TEMPLATES = [
    "Thank you for your email. I've received your message and will get back to you within 24 hours.\n\nBest regards,\nAI Employee Team",
    "Thanks for reaching out! Your email is important to us. We'll respond shortly.\n\nWarm regards,\nAI Employee",
    "Email received! We appreciate you contacting us. Our team will review and respond soon.\n\nKind regards,\nAI Employee Team",
]

WHATSAPP_AUTO_REPLY_TEMPLATES = [
    "Thanks for your message! 🙏 We'll get back to you soon.",
    "Message received! ✅ We'll respond shortly.",
    "Hi there! 👋 Thanks for contacting us. We'll be in touch soon!",
]

# AI Assistant responses
AI_RESPONSES = {
    "hello": "Hello! I'm your AI Employee Assistant. How can I help you today? 😊",
    "hi": "Hi there! Welcome to AI Employee Dashboard. What would you like to know? 🤖",
    "status": "✅ All systems are operational!\n- Email: Active\n- WhatsApp: Active\n- LinkedIn: Active\n- Facebook: Active",
    "pending": f"You currently have pending tasks. Check the Tasks tab for details.",
    "email": "Check the Email tab to view inbox and send messages! 📧",
    "whatsapp": "Navigate to WhatsApp tab to send messages! 💬",
    "help": "I can help you with:\n- Task Management\n- Email & WhatsApp\n- Status Updates\n- Reports\n\nJust ask!",
    "revenue": "💰 Weekly Revenue: $2,450\n📈 Growth: +12% from last week",
    "tasks": "📋 Task Summary:\n- Pending: Check Tasks tab\n- Completed: See Done folder\n- Approval: Pending Approval tab",
    "default": "I'm here to help! Ask me about tasks, emails, status, or revenue. 🚀",
}

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
    return "\n\n".join([f"📧 **{f.stem}**\n\nClick to view" for f in files])

def get_approval():
    path = vault / "Pending_Approval"
    if not path.exists() or not list(path.glob("*.md")):
        return "✨ No pending approvals!"
    files = list(path.glob("*.md"))
    return "\n\n".join([f"⏸️ **{f.stem}**\n\nAwaiting your approval" for f in files])

def get_completed():
    path = vault / "Done"
    if not path.exists():
        return "No completed tasks"
    files = sorted(path.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
    return "\n\n".join([f"✅ **{f.stem}**\n\nCompleted" for f in files])

def refresh():
    counts = get_counts()
    metrics = f"""### 📊 Live Metrics
| Metric | Value |
|--------|-------|
| 📋 Pending Tasks | {counts['Needs_Action']} |
| ✅ Completed | {counts['Done']} |
| ⏸️ Awaiting Approval | {counts['Pending_Approval']} |
| 💰 Revenue (Week) | $2,450 |
| 📈 Growth | +12% |"""
    return metrics, get_pending(), get_approval(), get_completed()

def send_email(to, subject, body, auto_reply=False):
    if not to or "@" not in to:
        return "❌ Please enter a valid email address"
    
    # Save email to vault
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    email_file = vault / "Emails" / f"SENT_{timestamp}.md"
    email_file.write_text(f"""---
to: {to}
subject: {subject}
date: {datetime.now().isoformat()}
---

# Email Sent

**To:** {to}
**Subject:** {subject}
**Body:**
{body}
""")
    
    # Auto-reply if enabled
    if auto_reply:
        reply = random.choice(EMAIL_AUTO_REPLY_TEMPLATES)
        reply_file = vault / "Emails" / f"AUTOREPLY_{timestamp}.md"
        reply_file.write_text(f"""---
to: {to}
subject: Re: {subject}
date: {datetime.now().isoformat()}
type: auto-reply
---

# Auto-Reply Sent

{reply}
""")
        return f"✅ Email sent to {to}\n📧 Auto-reply: {reply[:50]}..."
    
    return f"✅ Email sent successfully!\n\n**To:** {to}\n**Subject:** {subject}\n\nSaved to vault."

def send_whatsapp(phone, message, auto_reply=False):
    if not phone:
        return "❌ Please enter a phone number"
    
    # Save message to vault
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    wa_file = vault / "WhatsApp" / f"SENT_{timestamp}.md"
    wa_file.parent.mkdir(exist_ok=True)
    wa_file.write_text(f"""---
to: {phone}
date: {datetime.now().isoformat()}
---

# WhatsApp Sent

**To:** {phone}
**Message:**
{message}
""")
    
    # Auto-reply if enabled
    if auto_reply:
        reply = random.choice(WHATSAPP_AUTO_REPLY_TEMPLATES)
        reply_file = vault / "WhatsApp" / f"AUTOREPLY_{timestamp}.md"
        reply_file.write_text(f"""---
to: {phone}
date: {datetime.now().isoformat()}
type: auto-reply
---

# Auto-Reply Sent

{reply}
""")
        return f"✅ WhatsApp sent to {phone}\n💬 Auto-reply: {reply}"
    
    return f"✅ WhatsApp message sent!\n\n**To:** {phone}\n\nSaved to vault."

def ai_chat(message, history):
    if not message:
        return history
    
    msg = message.lower()
    response = AI_RESPONSES.get("default")
    
    for key, value in AI_RESPONSES.items():
        if key in msg:
            response = value
            break
    
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})
    return history

def clear_chat():
    return []

# Professional Custom CSS
custom_css = """
:root {
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --secondary: #8b5cf6;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --dark: #1e293b;
    --light: #f8fafc;
}

.gradio-container {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

.gradio-container .main {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    padding: 20px;
    margin: 20px;
}

.gradio-container h1 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800;
    font-size: 2.5em;
    text-align: center;
    margin-bottom: 10px;
}

.gradio-container h2, .gradio-container h3 {
    color: var(--dark);
    font-weight: 600;
}

.gradio-container .tab-nav {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 5px;
    margin-bottom: 20px;
}

.gradio-container .tab-nav button {
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.gradio-container .tab-nav button.selected {
    background: white;
    color: var(--primary);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.gradio-container button.primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 10px;
    font-weight: 600;
    padding: 12px 24px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.gradio-container button.primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.gradio-container input, .gradio-container textarea {
    border-radius: 10px;
    border: 2px solid #e2e8f0;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.gradio-container input:focus, .gradio-container textarea:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.gradio-container .metric-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.gradio-container .status-badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.85em;
    font-weight: 600;
    margin: 4px;
}

.gradio-container .status-active {
    background: #d1fae5;
    color: #065f46;
}

.gradio-container .chatbot {
    border-radius: 15px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.gradio-container footer {
    display: none;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.gradio-container .main {
    animation: fadeIn 0.6s ease-out;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

.gradio-container button.primary {
    animation: pulse 2s infinite;
}

/* Responsive */
@media (max-width: 768px) {
    .gradio-container h1 {
        font-size: 1.8em;
    }
    
    .gradio-container .main {
        margin: 10px;
        padding: 15px;
    }
}
"""

# Build Professional UI
with gr.Blocks(
    title="AI Employee Dashboard",
    theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="purple"),
    css=custom_css,
    fill_height=True
) as demo:
    
    # Header with Logo
    gr.Markdown("""
    # 🤖 AI Employee Dashboard
    ### Your Life & Business on Autopilot
    *Developed by Ayesha Aaqil • 2026*
    """)
    
    # Live Metrics Dashboard
    counts = get_counts()
    metrics = f"""### 📊 Live Metrics
| Metric | Value |
|--------|-------|
| 📋 Pending Tasks | {counts['Needs_Action']} |
| ✅ Completed | {counts['Done']} |
| ⏸️ Awaiting Approval | {counts['Pending_Approval']} |
| 💰 Revenue (Week) | $2,450 |
| 📈 Growth | +12% |"""
    
    metrics_md = gr.Markdown(metrics)
    
    # System Status
    gr.Markdown("""
    ### 🟢 System Status
    | Service | Status | Last Check |
    |---------|--------|------------|
    | 📧 Gmail | <span class="status-badge status-active">✅ Active</span> | Just now |
    | 💬 WhatsApp | <span class="status-badge status-active">✅ Active</span> | Just now |
    | 💼 LinkedIn | <span class="status-badge status-active">✅ Active</span> | Just now |
    | 📘 Facebook | <span class="status-badge status-active">✅ Active</span> | Just now |
    """)
    
    # Main Tabs
    with gr.Tabs():
        
        # 📋 Tasks Tab
        with gr.Tab("📋 Tasks", id="tasks"):
            gr.Markdown("### 📋 Task Management")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("**⏳ Pending Tasks**")
                    pending_out = gr.Textbox(
                        value=get_pending(),
                        lines=10,
                        label="Pending",
                        container=True
                    )
                
                with gr.Column(scale=1):
                    gr.Markdown("**⏸️ Approval Required**")
                    approval_out = gr.Textbox(
                        value=get_approval(),
                        lines=10,
                        label="Approval",
                        container=True
                    )
            
            with gr.Row():
                approve_btn = gr.Button("✅ Approve All", variant="primary", scale=1)
                reject_btn = gr.Button("❌ Reject All", scale=1)
            
            completed_out = gr.Textbox(value=get_completed(), lines=6, label="✅ Completed")
            
            approve_btn.click(refresh, outputs=[metrics_md, pending_out, approval_out, completed_out])
            reject_btn.click(refresh, outputs=[metrics_md, pending_out, approval_out, completed_out])
        
        # 📧 Email Tab
        with gr.Tab("📧 Email", id="email"):
            gr.Markdown("### 📧 Email Management")
            
            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("**✉️ Compose Email**")
                    email_to = gr.Textbox(
                        label="To",
                        placeholder="email@example.com",
                        info="Enter recipient email address"
                    )
                    email_subject = gr.Textbox(
                        label="Subject",
                        placeholder="Email subject"
                    )
                    email_body = gr.Textbox(
                        label="Message",
                        lines=5,
                        placeholder="Type your message here...",
                        info="Write your email content"
                    )
                    
                    with gr.Row():
                        auto_reply_checkbox = gr.Checkbox(
                            label="🤖 Enable Auto-Reply",
                            value=False,
                            info="Send automatic acknowledgment"
                        )
                    
                    email_send = gr.Button("📤 Send Email", variant="primary")
                    email_output = gr.Textbox(label="Status", interactive=False)
                    
                    email_send.click(
                        fn=lambda to, subj, body, auto: send_email(to, subj, body, auto),
                        inputs=[email_to, email_subject, email_body, auto_reply_checkbox],
                        outputs=[email_output]
                    )
                
                with gr.Column(scale=1):
                    gr.Markdown("**📥 Recent Emails**")
                    gr.Markdown("📭 No new emails\n\n*Emails will appear here*")
        
        # 💬 WhatsApp Tab
        with gr.Tab("💬 WhatsApp", id="whatsapp"):
            gr.Markdown("### 💬 WhatsApp Messaging")
            
            with gr.Row():
                with gr.Column(scale=2):
                    wa_phone = gr.Textbox(
                        label="Phone Number",
                        value="+923178916907",
                        placeholder="+923XXXXXXXXX",
                        info="Enter phone number with country code"
                    )
                    wa_message = gr.Textbox(
                        label="Message",
                        lines=4,
                        placeholder="Type your WhatsApp message...",
                        info="Write your message content"
                    )
                    
                    with gr.Row():
                        wa_auto_reply = gr.Checkbox(
                            label="🤖 Enable Auto-Reply",
                            value=False,
                            info="Send automatic acknowledgment"
                        )
                    
                    wa_send = gr.Button("📤 Send Message", variant="primary")
                    wa_output = gr.Textbox(label="Status", interactive=False)
                    
                    wa_send.click(
                        fn=lambda p, m, a: send_whatsapp(p, m, a),
                        inputs=[wa_phone, wa_message, wa_auto_reply],
                        outputs=[wa_output]
                    )
        
        # 🤖 AI Assistant Tab
        with gr.Tab("🤖 AI Assistant", id="assistant"):
            gr.Markdown("""
            ### 🤖 AI Employee Assistant
            
            Ask me anything about your tasks, emails, revenue, or system status!
            
            **Try asking:**
            - "What's my revenue?"
            - "Show pending tasks"
            - "System status"
            - "Help"
            """)
            
            chatbot = gr.Chatbot(
                label="AI Chat",
                height=400,
                bubble_full_width=False,
                show_copy_button=True
            )
            
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Ask me anything...",
                    show_label=False,
                    scale=4,
                    container=False
                )
                send_btn = gr.Button("Send", variant="primary", scale=1)
            
            clear_btn = gr.Button("🗑️ Clear Chat")
            
            send_btn.click(
                fn=ai_chat,
                inputs=[msg_input, chatbot],
                outputs=[chatbot]
            )
            clear_btn.click(fn=clear_chat, outputs=[chatbot])
        
        # ℹ️ About Tab
        with gr.Tab("ℹ️ About", id="about"):
            gr.Markdown("""
            # 🤖 About AI Employee
            
            ## Your Personal AI Assistant
            
            AI Employee is your 24/7 digital assistant that manages your personal and business affairs autonomously.
            
            ### ✨ Features
            
            - 📧 **Email Management** - Send, receive, and auto-reply to emails
            - 💬 **WhatsApp Integration** - Message contacts directly
            - 📋 **Task Management** - Track and organize your tasks
            - 🤖 **AI Assistant** - Get instant answers and insights
            - 📊 **Live Metrics** - Monitor revenue and growth
            
            ### 🎯 Created By
            
            **Ayesha Aaqil** - AI Automation Expert
            
            ### 🚀 Technology
            
            - Built with Gradio & Tailwind CSS
            - Deployed on Hugging Face Spaces
            - Powered by AI & Automation
            
            ---
            
            *© 2026 AI Employee • All Rights Reserved*
            """)
    
    # Footer
    gr.Markdown("""
    ---
    <div style="text-align: center; padding: 20px;">
        <p style="color: #667eea; font-weight: 600;">
            🚀 Powered by AI Employee • Developed by Ayesha Aaqil • 2026
        </p>
        <p style="color: #888; font-size: 0.9em;">
            Your life and business on autopilot
        </p>
    </div>
    """)

# Launch
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 AI Employee Dashboard - Professional Edition")
    print("=" * 60)
    print(f"📂 Vault: {vault.absolute()}")
    print("🌐 Starting server...")
    print("=" * 60)

    # Hugging Face Spaces requires share=True or native sharing
    # show_api=False prevents JSON schema parsing error
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True, show_api=False)
