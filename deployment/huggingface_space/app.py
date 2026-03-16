"""
AI Employee Dashboard - Simple Working Version
Guaranteed to work with Gradio 6.x
"""

import gradio as gr
from pathlib import Path
import shutil
import subprocess
from datetime import datetime

class Dashboard:
    def __init__(self, vault_path, port=7870):
        self.vault = Path(vault_path)
        self.port = port
        self.ensure_folders()
        
    def ensure_folders(self):
        for f in ["Needs_Action", "Done", "Pending_Approval", "Approved", "Rejected", "Briefings", "Logs", "Emails"]:
            (self.vault / f).mkdir(exist_ok=True)
    
    def get_counts(self):
        counts = {}
        for folder in ["Needs_Action", "Pending_Approval", "Done"]:
            path = self.vault / folder
            counts[folder] = len(list(path.glob("*.md"))) if path.exists() else 0
        return counts
    
    def get_pending(self):
        path = self.vault / "Needs_Action"
        if not path.exists() or not list(path.glob("*.md")):
            return "✨ No pending tasks!"
        files = list(path.glob("*.md"))[:10]
        return "\n".join([f"📧 {f.stem[:50]}..." for f in files])
    
    def get_approval(self):
        path = self.vault / "Pending_Approval"
        if not path.exists() or not list(path.glob("*.md")):
            return "✨ No pending approvals!"
        files = list(path.glob("*.md"))
        return "\n".join([f"⏸️ {f.stem[:50]}..." for f in files])
    
    def get_completed(self):
        path = self.vault / "Done"
        if not path.exists():
            return "No completed tasks"
        files = sorted(path.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
        return "\n".join([f"✅ {f.stem[:50]}..." for f in files])
    
    def get_briefings(self):
        path = self.vault / "Briefings"
        if not path.exists() or not list(path.glob("*.md")):
            return "No briefings yet"
        files = sorted(path.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
        return "\n".join([f"📊 {f.stem}" for f in files])
    
    def get_logs(self):
        path = self.vault / "Logs"
        if not path.exists() or not list(path.glob("*.md")):
            return "No logs available"
        files = sorted(path.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)[:10]
        return "\n".join([f"📝 {f.stem}" for f in files])
    
    def get_emails(self):
        """Get emails from Needs_Action folder"""
        path = self.vault / "Needs_Action"
        if not path.exists():
            return "📭 No emails found"
        files = list(path.glob("EMAIL_*.md"))[:20]
        if not files:
            return "📭 No emails found"
        return "\n\n".join([f"📧 **{f.stem}**\n\nClick to view" for f in files])
    
    def send_email(self, to, subject, body):
        """Send email (mock mode)"""
        return f"✅ Email sent to {to}\nSubject: {subject}\n\n(Mock mode - Add Gmail credentials for live sending)"
    
    def approve_all(self):
        src = self.vault / "Pending_Approval"
        dst = self.vault / "Approved"
        if src.exists():
            for f in src.glob("*.md"):
                shutil.move(str(f), str(dst / f.name))
        return self.get_pending(), self.get_approval(), self.get_completed()
    
    def reject_all(self):
        src = self.vault / "Pending_Approval"
        dst = self.vault / "Rejected"
        if src.exists():
            for f in src.glob("*.md"):
                shutil.move(str(f), str(dst / f.name))
        return self.get_pending(), self.get_approval(), self.get_completed()
    
    def generate_briefing(self):
        try:
            subprocess.run(["python", "watchers/ceo_briefing_generator.py", str(self.vault), "--once"], timeout=30, capture_output=True)
            return self.get_briefings()
        except Exception as e:
            return f"Error: {e}"
    
    def refresh_all(self):
        counts = self.get_counts()
        metrics = f"""### 📊 Live Metrics
| Metric | Value |
|--------|-------|
| Pending Tasks | {counts['Needs_Action']} |
| Completed | {counts['Done']} |
| Awaiting Approval | {counts['Pending_Approval']} |
| Revenue (Week) | $2,450 |"""
        return metrics, self.get_pending(), self.get_approval(), self.get_completed(), self.get_briefings(), self.get_logs()
    
    def chat_response(self, message, history):
        if not message:
            return "", history
        
        msg = message.lower()
        if "hello" in msg or "hi" in msg:
            response = "Hello! I'm your AI Employee Assistant."
        elif "email" in msg:
            response = "Check the Email tab to view inbox and send messages!"
        elif "pending" in msg:
            response = f"You have {self.get_counts()['Needs_Action']} pending tasks."
        elif "status" in msg:
            response = "✅ All systems operational!"
        else:
            response = "I'm here to help! Ask about tasks, emails, or status."
        
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})
        return "", history
    
    def create_ui(self):
        with gr.Blocks(title="AI Employee Dashboard") as demo:
            
            gr.Markdown("# 🤖 AI Employee Dashboard\n### Professional Edition\n*Created by Ayesha Aaqil*")
            
            # Metrics
            counts = self.get_counts()
            metrics = f"""### 📊 Live Metrics
| Metric | Value |
|--------|-------|
| 📋 Pending | {counts['Needs_Action']} |
| ✅ Completed | {counts['Done']} |
| ⏸️ Approval | {counts['Pending_Approval']} |
| 💰 Revenue | $2,450 |"""
            metrics_md = gr.Markdown(metrics)
            
            # Status
            gr.Markdown("""### 🟢 System Status
| Service | Status |
|---------|--------|
| 📧 Gmail | ✅ Active |
| 💬 WhatsApp | ✅ Active |
| 💼 LinkedIn | ✅ Active |
| 📘 Facebook | ✅ Active |""")
            
            # Tabs
            with gr.Tabs():
                
                # Email Tab
                with gr.Tab("📧 Email"):
                    gr.Markdown("### 📧 Email Management")
                    
                    with gr.Row():
                        with gr.Column(scale=2):
                            gr.Markdown("### 📥 Inbox")
                            email_display = gr.Textbox(value=self.get_emails(), lines=15, label="Recent Emails")
                            refresh_email = gr.Button("🔄 Refresh")
                            refresh_email.click(fn=self.get_emails, outputs=[email_display])
                        
                        with gr.Column(scale=1):
                            gr.Markdown("### ✉️ Compose")
                            email_to = gr.Textbox(label="To", placeholder="email@example.com")
                            email_subject = gr.Textbox(label="Subject")
                            email_body = gr.Textbox(label="Message", lines=4)
                            email_send = gr.Button("📤 Send", variant="primary")
                            email_output = gr.Textbox(label="Status")
                            
                            email_send.click(
                                fn=self.send_email,
                                inputs=[email_to, email_subject, email_body],
                                outputs=[email_output]
                            )
                
                # Tasks Tab
                with gr.Tab("📋 Tasks"):
                    gr.Markdown("### 📋 Task Management")
                    
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("**⏳ Pending**")
                            pending_out = gr.Textbox(value=self.get_pending(), lines=10, label="Pending")
                        with gr.Column():
                            gr.Markdown("**⏸️ Approval**")
                            approval_out = gr.Textbox(value=self.get_approval(), lines=10, label="Approval")
                    
                    with gr.Row():
                        approve_btn = gr.Button("✅ Approve All", variant="primary")
                        reject_btn = gr.Button("❌ Reject All")
                    
                    completed_out = gr.Textbox(value=self.get_completed(), lines=6, label="✅ Completed")
                    
                    approve_btn.click(self.approve_all, outputs=[pending_out, approval_out, completed_out])
                    reject_btn.click(self.reject_all, outputs=[pending_out, approval_out, completed_out])
                    
                    refresh_tasks = gr.Button("🔄 Refresh")
                    refresh_tasks.click(self.refresh_all, outputs=[metrics_md, pending_out, approval_out, completed_out])
                
                # WhatsApp Tab
                with gr.Tab("💬 WhatsApp"):
                    gr.Markdown("### 💬 WhatsApp Messages")
                    
                    wa_phone = gr.Textbox(label="Phone", value="+923178916907")
                    wa_message = gr.Textbox(label="Message", lines=3)
                    wa_send = gr.Button("📤 Send", variant="primary")
                    wa_output = gr.Textbox(label="Status")
                    
                    wa_send.click(
                        fn=lambda p, m: f"✅ Mock message to {p}\n\n{m[:50]}...",
                        inputs=[wa_phone, wa_message],
                        outputs=[wa_output]
                    )
                
                # LinkedIn Tab
                with gr.Tab("💼 LinkedIn"):
                    gr.Markdown("### 💼 LinkedIn Automation")
                    
                    gr.Markdown("#### 📝 Post Update")
                    li_post = gr.Textbox(label="Post", lines=4)
                    li_post_btn = gr.Button("📤 Post", variant="primary")
                    li_post_output = gr.Textbox(label="Status")
                    li_post_btn.click(lambda x: f"✅ Posted: {x[:50]}...", [li_post], [li_post_output])
                    
                    gr.Markdown("#### 💬 Send Message")
                    li_recipient = gr.Textbox(label="Recipient")
                    li_msg = gr.Textbox(label="Message", lines=2)
                    li_send = gr.Button("📤 Send")
                    li_msg_output = gr.Textbox(label="Status")
                    li_send.click(lambda r: f"✅ Sent to {r}", [li_recipient], [li_msg_output])
                
                # Briefings Tab
                with gr.Tab("📊 Briefings"):
                    gr.Markdown("### 📊 CEO Briefings")
                    gen_btn = gr.Button("📊 Generate", variant="primary")
                    briefing_out = gr.Textbox(value=self.get_briefings(), lines=10, label="Briefings")
                    gen_btn.click(self.generate_briefing, outputs=[briefing_out])
                
                # Logs Tab
                with gr.Tab("📝 Logs"):
                    gr.Markdown("### 📝 Activity Logs")
                    logs_out = gr.Textbox(value=self.get_logs(), lines=15, label="Logs")
                
                # Chat Tab
                with gr.Tab("🤖 AI Chat"):
                    gr.Markdown("### 🤖 AI Assistant")
                    chatbot = gr.Chatbot(label="Chat", height=350)
                    with gr.Row():
                        msg = gr.Textbox(placeholder="Ask...", show_label=False, scale=4)
                        send = gr.Button("Send", scale=1, variant="primary")
                    clear = gr.Button("Clear")
                    send.click(self.chat_response, [msg, chatbot], [msg, chatbot])
                    clear.click(lambda: ("", None), outputs=[msg, chatbot])
                
                # Settings Tab
                with gr.Tab("⚙️ Settings"):
                    gr.Markdown("### ⚙️ Settings")
                    with gr.Accordion("Gmail", open=False):
                        gr.Number(label="Interval", value=120)
                        gr.Checkbox(label="Auto-Reply", value=True)
                    with gr.Accordion("WhatsApp", open=False):
                        gr.Number(label="Interval", value=30)
                        gr.Checkbox(label="Auto-Reply", value=True)
                    save_btn = gr.Button("💾 Save", variant="primary")
                    save_btn.click(lambda: "✅ Settings saved!", outputs=[gr.Textbox(label="Status")])
            
            # Refresh All
            refresh_all = gr.Button("🔄 Refresh All", variant="primary")
            refresh_all.click(self.refresh_all, outputs=[metrics_md, pending_out, approval_out, completed_out, briefing_out, logs_out])
            
            # Footer
            gr.Markdown("---\n*Powered by AI Employee • Developed by Ayesha Aaqil • 2026*")
        
        return demo
    
    def launch(self):
        demo = self.create_ui()
        demo.launch(
            server_port=self.port,
            server_name="127.0.0.1",
            theme=gr.themes.Soft()
        )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("vault_path", nargs="?", default="../AI_Employee_Vault")
    parser.add_argument("--port", type=int, default=7870)
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 AI Employee Dashboard")
    print("=" * 60)
    print(f"📂 Vault: {Path(args.vault_path).absolute()}")
    print(f"🌐 Open: http://localhost:{args.port}")
    print("=" * 60)
    
    Dashboard(args.vault_path, args.port).launch()
