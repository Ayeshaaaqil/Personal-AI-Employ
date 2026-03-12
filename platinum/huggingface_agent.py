"""
Hugging Face Agent - Wrapper for AI Employee tasks

This module provides a high-level agent interface that uses
the Hugging Face reasoning engine to manage AI Employee tasks.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from huggingface_reasoning_engine import HuggingFaceReasoningEngine, ModelRouter

logger = logging.getLogger(__name__)


class HuggingFaceAgent:
    """
    AI Employee Agent powered by Hugging Face

    This agent replaces Claude Code with open-source LLMs
    """

    def __init__(
        self,
        vault_path: str,
        model_name: Optional[str] = None,
        use_router: bool = False  # Changed to False for briefing generation
    ):
        self.vault_path = Path(vault_path)
        self.use_router = use_router

        # Initialize reasoning engine
        # For briefing generation, use direct engine instead of router
        self.engine = HuggingFaceReasoningEngine(
            model_name=model_name or "meta-llama/Meta-Llama-3-70B-Instruct",
            vault_path=vault_path
        )

        logger.info(f"HuggingFace Agent initialized (vault: {vault_path})")
    
    def process_needs_action(self) -> List[Dict]:
        """
        Process all items in Needs_Action folder
        
        Returns:
            List of processed items with plans
        """
        needs_action_dir = self.vault_path / "Needs_Action"
        if not needs_action_dir.exists():
            return []
        
        processed = []
        for md_file in needs_action_dir.glob("*.md"):
            result = self.process_single_item(md_file)
            processed.append(result)
        
        return processed
    
    def process_single_item(self, item_path: Path) -> Dict:
        """
        Process a single item from Needs_Action
        
        Args:
            item_path: Path to markdown file
            
        Returns:
            Processing result dictionary
        """
        content = item_path.read_text()
        
        # Analyze the item
        analysis = self.engine.analyze_task(item_path)
        
        # Determine task type from content
        task_type = self._extract_task_type(content)
        
        # Create plan
        plan = self.engine.create_plan(
            task=item_path.stem,
            context={
                "file": str(item_path),
                "content": content,
                "analysis": analysis
            }
        )
        
        # Check if approval is needed
        requires_approval = self._check_approval_required(content, plan)
        
        if requires_approval:
            # Create approval request
            approval_path = self._create_approval_request(item_path, plan)
            return {
                "status": "pending_approval",
                "approval_file": str(approval_path),
                "plan": plan
            }
        else:
            # Can execute directly
            return {
                "status": "ready_to_execute",
                "plan": plan
            }
    
    def generate_daily_briefing(self) -> Path:
        """Generate a daily briefing"""
        briefing_content = self.engine.generate_ceo_briefing(period="day")
        
        briefings_dir = self.vault_path / "Briefings"
        briefings_dir.mkdir(exist_ok=True)
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        briefing_path = briefings_dir / f"{date_str}_Daily_Briefing.md"
        
        briefing_path.write_text(briefing_content)
        logger.info(f"Daily briefing saved to {briefing_path}")
        
        return briefing_path
    
    def generate_weekly_briefing(self) -> Path:
        """Generate a weekly CEO briefing"""
        briefing_content = self.engine.generate_ceo_briefing(period="week")
        
        briefings_dir = self.vault_path / "Briefings"
        briefings_dir.mkdir(exist_ok=True)
        
        week_num = datetime.now().isocalendar()[1]
        year = datetime.now().year
        briefing_path = briefings_dir / f"{year}-W{week_num:02d}_Weekly_Briefing.md"
        
        briefing_path.write_text(briefing_content)
        logger.info(f"Weekly briefing saved to {briefing_path}")
        
        return briefing_path
    
    def reply_to_email(self, email_content: str) -> str:
        """
        Generate email reply
        
        Args:
            email_content: Original email content
            
        Returns:
            Generated reply
        """
        prompt = f"""
Generate a professional email reply to this message:

{email_content}

Guidelines:
- Be polite and professional
- Keep it concise
- Address all points raised
- Include appropriate call-to-action

Reply:
"""
        
        reply = self.engine.reason(prompt, task_type="email_reply")
        return reply
    
    def generate_social_post(self, topic: str, platform: str = "linkedin") -> str:
        """
        Generate social media post
        
        Args:
            topic: Post topic
            platform: Social platform (linkedin, facebook, instagram)
            
        Returns:
            Generated post content
        """
        platform_guidelines = {
            "linkedin": "Professional, business-focused, 1300 characters max",
            "facebook": "Friendly, engaging, can include emojis",
            "instagram": "Visual-focused caption, use hashtags, emojis welcome"
        }
        
        prompt = f"""
Generate a {platform} post about: {topic}

Platform guidelines: {platform_guidelines.get(platform, '')}

Include:
- Engaging opening
- Main content
- Call-to-action
- Relevant hashtags (for Instagram/Facebook)

Post:
"""
        
        post = self.engine.reason(prompt, task_type="social_media")
        return post
    
    def categorize_transaction(self, transaction_description: str, amount: float) -> Dict:
        """
        Categorize a financial transaction
        
        Args:
            transaction_description: Transaction description
            amount: Transaction amount
            
        Returns:
            Categorization result
        """
        prompt = f"""
Categorize this business transaction:

Description: {transaction_description}
Amount: ${amount:.2f}

Provide:
1. Category (e.g., Revenue, Expense, Software, Marketing, etc.)
2. Subcategory
3. Tax-deductible (yes/no)
4. Notes

Format as JSON.
"""
        
        response = self.engine.reason(prompt, task_type="accounting")
        
        # Parse JSON response
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response[json_start:json_end])
        except:
            pass
        
        return {
            "category": "Uncategorized",
            "subcategory": "General",
            "tax_deductible": "unknown",
            "notes": response
        }
    
    def _extract_task_type(self, content: str) -> str:
        """Extract task type from content"""
        content_lower = content.lower()
        
        if "email" in content_lower:
            return "email_reply"
        elif "invoice" in content_lower:
            return "invoice"
        elif "ceo briefing" in content_lower or "briefing" in content_lower:
            return "ceo_briefing"
        elif "audit" in content_lower:
            return "audit_analysis"
        elif "social" in content_lower or "post" in content_lower:
            return "social_media"
        elif "payment" in content_lower:
            return "payment"
        
        return "default"
    
    def _check_approval_required(self, content: str, plan: Dict) -> bool:
        """Check if task requires human approval"""
        # Check for sensitive keywords
        sensitive_keywords = [
            "payment", "transfer", "approve", "authorization",
            "over $500", "large amount", "bank"
        ]
        
        content_lower = content.lower()
        for keyword in sensitive_keywords:
            if keyword in content_lower:
                return True
        
        # Check plan for approval requirements
        if plan.get("approvals_required"):
            return True
        
        return False
    
    def _create_approval_request(self, item_path: Path, plan: Dict) -> Path:
        """Create approval request file"""
        approval_dir = self.vault_path / "Pending_Approval"
        approval_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        approval_path = approval_dir / f"APPROVAL_{item_path.stem}_{timestamp}.md"
        
        content = f"""---
type: approval_request
created: {datetime.now().isoformat()}
source_file: {item_path.name}
status: pending
---

# Approval Required

**Task:** {plan.get('task', 'Unknown')}

**Reason:** This action requires human approval before execution.

## Plan Summary

{json.dumps(plan, indent=2, default=str)}

## To Approve

Move this file to the `/Approved` folder.

## To Reject

Move this file to the `/Rejected` folder.

## Source File

Original file: `{item_path.name}`
"""
        
        approval_path.write_text(content)
        return approval_path
    
    def update_dashboard(self):
        """Update the Dashboard.md with current status"""
        dashboard_path = self.vault_path / "Dashboard.md"
        
        # Count items in each folder
        counts = {
            "needs_action": len(list((self.vault_path / "Needs_Action").glob("*.md"))) if (self.vault_path / "Needs_Action").exists() else 0,
            "pending_approval": len(list((self.vault_path / "Pending_Approval").glob("*.md"))) if (self.vault_path / "Pending_Approval").exists() else 0,
            "done_today": 0,
            "done_total": len(list((self.vault_path / "Done").glob("*.md"))) if (self.vault_path / "Done").exists() else 0
        }
        
        # Count today's completed items
        done_dir = self.vault_path / "Done"
        if done_dir.exists():
            today_str = datetime.now().strftime("%Y-%m-%d")
            for f in done_dir.glob("*.md"):
                if today_str in f.stem:
                    counts["done_today"] += 1
        
        # Generate dashboard content
        dashboard_content = f"""---
last_updated: {datetime.now().isoformat()}
status: active
---

# AI Employee Dashboard

_Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop._

## Quick Status

| Metric | Count |
|--------|-------|
| Needs Action | {counts['needs_action']} |
| Pending Approval | {counts['pending_approval']} |
| Completed Today | {counts['done_today']} |
| Completed Total | {counts['done_total']} |

## Recent Activity

*Updated automatically by HuggingFace Agent*

## System Status

- **Reasoning Engine:** Hugging Face (Open Source)
- **Active Model:** Llama 3 / Mistral / Qwen
- **Vault Path:** {self.vault_path}
- **Last Check:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

*Generated by AI Employee Platinum Tier*
"""
        
        dashboard_path.write_text(dashboard_content)
        logger.info("Dashboard updated")


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Hugging Face Agent")
    parser.add_argument("vault", type=str, help="Path to vault")
    parser.add_argument("--process", action="store_true", help="Process Needs_Action items")
    parser.add_argument("--briefing", action="store_true", help="Generate briefing")
    parser.add_argument("--update-dashboard", action="store_true", help="Update dashboard")
    parser.add_argument("--model", type=str, help="Model to use")
    
    args = parser.parse_args()
    
    agent = HuggingFaceAgent(
        vault_path=args.vault,
        model_name=args.model
    )
    
    if args.process:
        results = agent.process_needs_action()
        print(f"Processed {len(results)} items")
        for result in results:
            print(f"  - {result.get('status', 'unknown')}")
    
    elif args.briefing:
        briefing_path = agent.generate_weekly_briefing()
        print(f"Briefing generated: {briefing_path}")
    
    elif args.update_dashboard:
        agent.update_dashboard()
        print("Dashboard updated")
    
    else:
        parser.print_help()
