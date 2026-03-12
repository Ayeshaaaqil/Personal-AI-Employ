"""
Web Dashboard for AI Employee - Platinum Tier

Gradio-based web interface for monitoring and controlling AI Employee
"""

import os
import gradio as gr
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIEmployeeDashboard:
    """Web Dashboard for AI Employee"""
    
    def __init__(self, vault_path: str, port: int = 7860):
        self.vault_path = Path(vault_path)
        self.port = port
        
        # Ensure vault folders exist
        self._ensure_vault_structure()
        
        # Create Gradio interface
        self.demo = self._create_interface()
        
        logger.info(f"Dashboard initialized (vault: {vault_path}, port: {port})")
    
    def _ensure_vault_structure(self):
        """Ensure all vault folders exist"""
        folders = [
            "Inbox", "Needs_Action", "Done", "Pending_Approval",
            "Approved", "Rejected", "Plans", "Briefings",
            "Accounting", "Logs", "Audit"
        ]
        for folder in folders:
            (self.vault_path / folder).mkdir(exist_ok=True)
    
    def _create_interface(self):
        """Create Gradio interface"""
        with gr.Blocks(title="AI Employee Dashboard") as demo:
            gr.Markdown("""
            # 🤖 AI Employee Dashboard
            ### Platinum Tier - Powered by Hugging Face
            
            _Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop._
            """)
            
            # Status Row
            with gr.Row():
                with gr.Column(scale=1):
                    status_box = self._create_status_box()
                with gr.Column(scale=2):
                    metrics_box = self._create_metrics_box()
            
            # Tabs
            with gr.Tab("📋 Task Management"):
                self._create_task_tab()
            
            with gr.Tab("📊 CEO Briefings"):
                self._create_briefings_tab()
            
            with gr.Tab("📝 Audit Logs"):
                self._create_audit_tab()
            
            with gr.Tab("⚙️ Settings"):
                self._create_settings_tab()
            
            # Refresh button
            refresh_btn = gr.Button("🔄 Refresh Dashboard", variant="primary")
            refresh_btn.click(
                fn=self._refresh_dashboard,
                inputs=[],
                outputs=[status_box, metrics_box]
            )
        
        return demo
    
    def _create_status_box(self):
        """Create status display box"""
        counts = self._get_vault_counts()
        
        status = gr.Markdown(self._generate_status_markdown(counts))
        return status
    
    def _create_metrics_box(self):
        """Create metrics display"""
        metrics = self._get_metrics()

        with gr.Group():
            gr.Markdown("### 📈 Key Metrics")

            with gr.Row():
                gr.Number(
                    value=metrics["tasks_completed_today"],
                    label="Tasks Completed Today",
                    interactive=False
                )
                gr.Number(
                    value=metrics["pending_tasks"],
                    label="Pending Tasks",
                    interactive=False
                )
            
            with gr.Row():
                gr.Textbox(
                    value=metrics["revenue_mtd"],
                    label="Revenue MTD",
                    interactive=False
                )
                gr.Number(
                    value=metrics["approval_queue"],
                    label="Pending Approvals",
                    interactive=False
                )
        
        return gr.JSON(value=metrics, label="Detailed Metrics")
    
    def _create_task_tab(self):
        """Create task management tab"""
        gr.Markdown("## 📋 Task Management")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Needs Action")
                needs_action_list = self._list_folder("Needs_Action")
                needs_action = gr.Dropdown(
                    choices=needs_action_list,
                    label="Select Task",
                    interactive=True
                )
            
            with gr.Column(scale=2):
                gr.Markdown("### Task Details")
                task_display = gr.Textbox(
                    label="Task Content",
                    lines=10,
                    interactive=False
                )
                
                with gr.Row():
                    approve_btn = gr.Button("✅ Approve", variant="primary")
                    reject_btn = gr.Button("❌ Reject", variant="stop")
        
        # Task actions
        needs_action.change(
            fn=self._load_task_content,
            inputs=[needs_action],
            outputs=[task_display]
        )
        
        approve_btn.click(
            fn=self._approve_task,
            inputs=[needs_action],
            outputs=[task_display]
        )
        
        reject_btn.click(
            fn=self._reject_task,
            inputs=[needs_action],
            outputs=[task_display]
        )
    
    def _create_briefings_tab(self):
        """Create CEO briefings tab"""
        gr.Markdown("## 📊 CEO Briefings")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Generate Briefing")
                
                briefing_type = gr.Radio(
                    choices=["Daily", "Weekly", "Monthly"],
                    label="Briefing Type",
                    value="Daily"
                )
                
                generate_btn = gr.Button("📝 Generate Briefing", variant="primary")
            
            with gr.Column():
                gr.Markdown("### Recent Briefings")
                briefings_list = self._list_folder("Briefings")
                briefings = gr.Dropdown(
                    choices=briefings_list,
                    label="Select Briefing",
                    interactive=True
                )
        
        briefing_display = gr.Textbox(
            label="Briefing Content",
            lines=20,
            interactive=False
        )
        
        briefings.change(
            fn=self._load_briefing_content,
            inputs=[briefings],
            outputs=[briefing_display]
        )
        
        generate_btn.click(
            fn=self._generate_briefing,
            inputs=[briefing_type],
            outputs=[briefing_display]
        )
    
    def _create_audit_tab(self):
        """Create audit logs tab"""
        gr.Markdown("## 📝 Audit Logs")
        
        with gr.Row():
            with gr.Column(scale=1):
                log_filter = gr.Textbox(
                    label="Filter Logs",
                    placeholder="Search logs...",
                    interactive=True
                )
            
            with gr.Column(scale=1):
                log_date = gr.Textbox(
                    label="Date (YYYY-MM-DD)",
                    value=datetime.now().strftime("%Y-%m-%d"),
                    interactive=True
                )
        
        logs_display = gr.JSON(
            label="Audit Logs",
            value=self._load_audit_logs()
        )
        
        export_btn = gr.Button("📥 Export Logs")
        
        log_filter.change(
            fn=self._filter_logs,
            inputs=[log_filter, log_date],
            outputs=[logs_display]
        )
        
        log_date.change(
            fn=self._load_audit_logs_from_text,
            inputs=[log_date],
            outputs=[logs_display]
        )
    
    def _create_settings_tab(self):
        """Create settings tab"""
        gr.Markdown("## ⚙️ Settings")
        
        with gr.Group():
            gr.Markdown("### Model Configuration")
            
            model_select = gr.Dropdown(
                choices=[
                    "meta-llama/Meta-Llama-3-70B-Instruct",
                    "meta-llama/Meta-Llama-3-8B-Instruct",
                    "mistralai/Mistral-7B-Instruct-v0.3",
                    "Qwen/Qwen2.5-72B-Instruct",
                    "microsoft/Phi-3-medium-128k-instruct"
                ],
                label="Active Model",
                value="meta-llama/Meta-Llama-3-70B-Instruct"
            )
            
            save_model_btn = gr.Button("💾 Save Model Configuration", variant="primary")
        
        with gr.Group():
            gr.Markdown("### Vault Configuration")
            
            vault_path = gr.Textbox(
                label="Vault Path",
                value=str(self.vault_path),
                interactive=True
            )
            
            save_vault_btn = gr.Button("💾 Save Vault Configuration")
        
        with gr.Group():
            gr.Markdown("### System Status")
            
            system_status = gr.JSON(
                value=self._get_system_status(),
                label="System Health"
            )
            
            refresh_status_btn = gr.Button("🔄 Refresh Status")
    
    def _get_vault_counts(self) -> Dict:
        """Get counts for all vault folders"""
        counts = {}
        folders = ["Needs_Action", "Pending_Approval", "Approved", "Done", "Briefings"]
        
        for folder in folders:
            folder_path = self.vault_path / folder
            if folder_path.exists():
                counts[folder] = len(list(folder_path.glob("*.md")))
            else:
                counts[folder] = 0
        
        return counts
    
    def _get_metrics(self) -> Dict:
        """Get detailed metrics"""
        counts = self._get_vault_counts()
        
        # Count today's completed tasks
        done_dir = self.vault_path / "Done"
        today_str = datetime.now().strftime("%Y-%m-%d")
        tasks_today = 0
        
        if done_dir.exists():
            for f in done_dir.glob("*.md"):
                if today_str in f.stem:
                    tasks_today += 1
        
        # Calculate revenue (simplified)
        revenue_mtd = 0  # Would parse from Accounting folder
        
        return {
            "tasks_completed_today": tasks_today,
            "pending_tasks": counts.get("Needs_Action", 0),
            "revenue_mtd": f"${revenue_mtd:,.2f}",
            "approval_queue": counts.get("Pending_Approval", 0),
            "total_completed": counts.get("Done", 0),
            "briefings_generated": counts.get("Briefings", 0)
        }
    
    def _generate_status_markdown(self, counts: Dict) -> str:
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
"""
    
    def _list_folder(self, folder_name: str) -> List[str]:
        """List files in a vault folder"""
        folder_path = self.vault_path / folder_name
        if not folder_path.exists():
            return []
        
        return sorted([f.name for f in folder_path.glob("*.md")], reverse=True)
    
    def _load_task_content(self, task_name: str) -> str:
        """Load task content"""
        if not task_name:
            return ""
        
        task_path = self.vault_path / "Needs_Action" / task_name
        if task_path.exists():
            return task_path.read_text()
        
        return "Task file not found"
    
    def _approve_task(self, task_name: str) -> str:
        """Approve a task (move to Approved folder)"""
        if not task_name:
            return "No task selected"
        
        src = self.vault_path / "Needs_Action" / task_name
        dst = self.vault_path / "Approved" / task_name
        
        if src.exists():
            dst.parent.mkdir(exist_ok=True)
            src.rename(dst)
            return f"✅ Task approved and moved to Approved folder"
        
        return "Task file not found"
    
    def _reject_task(self, task_name: str) -> str:
        """Reject a task (move to Rejected folder)"""
        if not task_name:
            return "No task selected"
        
        src = self.vault_path / "Needs_Action" / task_name
        dst = self.vault_path / "Rejected" / task_name
        
        if src.exists():
            dst.parent.mkdir(exist_ok=True)
            src.rename(dst)
            return f"❌ Task rejected and moved to Rejected folder"
        
        return "Task file not found"
    
    def _load_briefing_content(self, briefing_name: str) -> str:
        """Load briefing content"""
        if not briefing_name:
            return ""
        
        briefing_path = self.vault_path / "Briefings" / briefing_name
        if briefing_path.exists():
            return briefing_path.read_text()
        
        return "Briefing not found"
    
    def _generate_briefing(self, briefing_type: str) -> str:
        """Generate a new briefing"""
        # This would call the HuggingFace agent to generate
        # For now, create a placeholder
        content = f"""---
generated: {datetime.now().isoformat()}
type: {briefing_type.lower()}
---

# {briefing_type} CEO Briefing

*Briefing generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Executive Summary

This is a placeholder briefing. Connect the HuggingFace Agent to generate real content.

## Revenue

- This Period: $0.00
- Trend: Stable

## Completed Tasks

- Task 1
- Task 2
- Task 3

## Proactive Suggestions

1. Review pending approvals
2. Check recent transactions
3. Schedule team meetings

---

*Generated by AI Employee Platinum Tier*
"""
        return content
    
    def _load_audit_logs(self, date: Optional[datetime] = None) -> Dict:
        """Load audit logs"""
        audit_dir = self.vault_path / "Audit"
        if not audit_dir.exists():
            return {"logs": [], "message": "No audit logs found"}
        
        # Load today's logs
        date_str = date.strftime("%Y-%m-%d") if date else datetime.now().strftime("%Y-%m-%d")
        log_file = audit_dir / f"{date_str}.jsonl"
        
        if not log_file.exists():
            return {"logs": [], "message": f"No logs for {date_str}"}
        
        logs = []
        for line in log_file.read_text().splitlines():
            try:
                logs.append(json.loads(line))
            except:
                pass
        
        return {"logs": logs[-50:], "total": len(logs)}  # Last 50 logs
    
    def _load_audit_logs_from_text(self, date_str: str) -> Dict:
        """Load audit logs from text date input"""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            return self._load_audit_logs(date)
        except ValueError:
            return {"logs": [], "message": f"Invalid date format: {date_str}. Use YYYY-MM-DD"}
    
    def _filter_logs(self, filter_text: str, date: datetime) -> Dict:
        """Filter audit logs"""
        logs = self._load_audit_logs(date)
        
        if not filter_text:
            return logs
        
        filtered = []
        for log in logs.get("logs", []):
            if filter_text.lower() in json.dumps(log).lower():
                filtered.append(log)
        
        return {"logs": filtered, "total": len(filtered)}
    
    def _get_system_status(self) -> Dict:
        """Get system status"""
        return {
            "vault_path": str(self.vault_path),
            "vault_exists": self.vault_path.exists(),
            "timestamp": datetime.now().isoformat(),
            "python_version": "3.x",
            "gradio_version": gr.__version__,
            "status": "healthy"
        }
    
    def _refresh_dashboard(self):
        """Refresh dashboard data"""
        counts = self._get_vault_counts()
        status = self._generate_status_markdown(counts)
        metrics = self._get_metrics()
        
        return status, metrics
    
    def launch(self, **kwargs):
        """Launch the dashboard"""
        self.demo.launch(
            server_port=self.port,
            **kwargs
        )


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Employee Web Dashboard")
    parser.add_argument("vault", type=str, help="Path to vault")
    parser.add_argument("--port", type=int, default=7860, help="Port to run on")
    parser.add_argument("--share", action="store_true", help="Create public link")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    
    args = parser.parse_args()
    
    dashboard = AIEmployeeDashboard(
        vault_path=args.vault,
        port=args.port
    )
    
    dashboard.launch(
        share=args.share,
        debug=args.debug
    )
