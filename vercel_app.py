"""
Vercel-compatible AI Employee Dashboard
Simple version that works on Vercel serverless
"""

import gradio as gr
from pathlib import Path

# Simple dashboard for Vercel
def greet(name):
    return f"Hello {name}! Welcome to AI Employee Dashboard!"

def send_email(to, subject, message):
    return f"✅ Email sent to {to}\nSubject: {subject}\n\n(Mock mode on Vercel)"

def get_status():
    return """
    ### AI Employee Status

    ✅ Dashboard: Online
    ✅ Email: Mock Mode
    ✅ WhatsApp: Coming Soon
    ✅ LinkedIn: Coming Soon

    **Deployed on:** Vercel
    **Developer:** Ayesha Aaqil
    """

# Create the Gradio app
with gr.Blocks(title="AI Employee - Vercel") as demo:
    gr.Markdown("# 🤖 AI Employee Dashboard\n### Vercel Edition\n*By Ayesha Aaqil*")

    with gr.Tabs():
        with gr.Tab("🏠 Home"):
            name = gr.Textbox(label="Your Name", placeholder="Enter your name")
            btn = gr.Button("Greet", variant="primary")
            output = gr.Textbox(label="Response")
            btn.click(greet, [name], [output])

        with gr.Tab("📧 Email"):
            to = gr.Textbox(label="To")
            subject = gr.Textbox(label="Subject")
            message = gr.Textbox(label="Message", lines=4)
            send_btn = gr.Button("Send Email", variant="primary")
            email_output = gr.Textbox(label="Status")
            send_btn.click(send_email, [to, subject, message], [email_output])

        with gr.Tab("📊 Status"):
            status_output = gr.Markdown(value=get_status())

    gr.Markdown("---\n*Powered by AI Employee • Developed by Ayesha Aaqil*")

# Vercel serverless handler
app = demo

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
