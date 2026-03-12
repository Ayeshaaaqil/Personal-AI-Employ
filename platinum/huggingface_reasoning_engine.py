"""
Hugging Face Reasoning Engine for AI Employee - Platinum Tier

This module replaces Claude Code with open-source LLMs from Hugging Face.
Supports: Llama 3, Mistral, Qwen, Phi-3, and more.

Features:
- Multiple model support with automatic fallback
- Hugging Face Inference API integration
- Local model deployment option
- Prompt templating for consistent outputs
- Response parsing for structured data
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from abc import ABC, abstractmethod

from dotenv import load_dotenv
from huggingface_hub import InferenceClient, HfApi
import requests

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseReasoningEngine(ABC):
    """Abstract base class for reasoning engines"""
    
    @abstractmethod
    def reason(self, prompt: str, context: str = "") -> str:
        """Generate reasoning output"""
        pass
    
    @abstractmethod
    def create_plan(self, task: str, context: Dict) -> Dict:
        """Create an action plan"""
        pass


class HuggingFaceReasoningEngine(BaseReasoningEngine):
    """
    Hugging Face Reasoning Engine
    
    Uses Hugging Face Inference API to run open-source LLMs
    """
    
    def __init__(
        self,
        model_name: str = "meta-llama/Meta-Llama-3-70B-Instruct",
        api_token: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: int = 120,
        vault_path: Optional[str] = None
    ):
        self.model_name = model_name
        self.api_token = api_token or os.getenv("HUGGINGFACE_TOKEN")
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout
        self.vault_path = Path(vault_path) if vault_path else None
        
        if not self.api_token:
            raise ValueError(
                "Hugging Face token required. Set HUGGINGFACE_TOKEN env var "
                "or pass api_token parameter."
            )
        
        # Initialize Hugging Face client
        self.client = InferenceClient(token=self.api_token)
        self.api = HfApi(token=self.api_token)
        
        # Model cache for performance
        self._model_cache = {}
        
        logger.info(f"HuggingFace Reasoning Engine initialized with {model_name}")
    
    def reason(self, prompt: str, context: str = "", system_prompt: Optional[str] = None) -> str:
        """
        Generate reasoning output from LLM
        
        Args:
            prompt: User prompt
            context: Additional context
            system_prompt: Optional system prompt override
            
        Returns:
            Generated text response
        """
        # Build messages
        messages = self._build_messages(prompt, context, system_prompt)
        
        try:
            response = self.client.chat_completion(
                model=self.model_name,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Hugging Face API error: {e}")
            # Try fallback model
            return self._fallback_reason(prompt, context)
    
    def create_plan(self, task: str, context: Dict) -> Dict:
        """
        Create an action plan for a task
        
        Args:
            task: Task description
            context: Context dictionary with vault info
            
        Returns:
            Plan dictionary with steps
        """
        plan_prompt = self._build_plan_prompt(task, context)
        plan_response = self.reason(plan_prompt)
        
        # Parse the plan response
        plan = self._parse_plan(plan_response, task, context)
        
        # Save plan to vault
        if self.vault_path:
            plan_path = self._save_plan(plan)
            logger.info(f"Plan saved to {plan_path}")
        
        return plan
    
    def analyze_task(self, task_file: Path) -> Dict:
        """
        Analyze a task file and generate recommendations
        
        Args:
            task_file: Path to task markdown file
            
        Returns:
            Analysis dictionary
        """
        content = task_file.read_text()
        
        analysis_prompt = f"""
Analyze this task and provide recommendations:

{content}

Provide:
1. Task type classification
2. Priority assessment
3. Required actions
4. Approval requirements
5. Estimated completion time

Format as JSON.
"""
        
        response = self.reason(analysis_prompt)
        
        # Try to parse as JSON
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                analysis = json.loads(response[json_start:json_end])
            else:
                analysis = {"raw_analysis": response}
        except:
            analysis = {"raw_analysis": response}
        
        return analysis
    
    def generate_ceo_briefing(self, period: str = "week") -> str:
        """
        Generate a CEO briefing for the specified period
        
        Args:
            period: Time period (day/week/month)
            
        Returns:
            Briefing markdown content
        """
        if not self.vault_path:
            raise ValueError("vault_path required for CEO briefing")
        
        # Gather data from vault
        data = self._gather_briefing_data(period)
        
        briefing_prompt = self._build_briefing_prompt(data, period)
        briefing = self.reason(briefing_prompt)
        
        return briefing
    
    def _build_messages(
        self,
        prompt: str,
        context: str = "",
        system_prompt: Optional[str] = None
    ) -> List[Dict]:
        """Build chat messages for LLM"""
        
        default_system = """You are an AI Employee assistant. You help manage business tasks,
emails, social media, and accounting. You are professional, efficient, and proactive.
You output structured responses when requested."""
        
        messages = [
            {"role": "system", "content": system_prompt or default_system}
        ]
        
        if context:
            messages.append({"role": "user", "content": f"Context: {context}"})
        
        messages.append({"role": "user", "content": prompt})
        
        return messages
    
    def _build_plan_prompt(self, task: str, context: Dict) -> str:
        """Build prompt for plan generation"""
        return f"""
Create a detailed action plan for this task:

TASK: {task}

CONTEXT:
{json.dumps(context, indent=2)}

Provide a plan with:
1. Objective
2. Steps (with checkboxes)
3. Required approvals
4. Dependencies
5. Estimated timeline

Format as markdown with frontmatter YAML.
"""
    
    def _parse_plan(self, response: str, task: str, context: Dict) -> Dict:
        """Parse plan response into structured format"""
        plan = {
            "task": task,
            "created": datetime.now().isoformat(),
            "status": "pending",
            "steps": [],
            "approvals_required": [],
            "raw_response": response
        }
        
        # Extract steps from markdown
        for line in response.split('\n'):
            if '- [ ]' in line or '1.' in line:
                plan["steps"].append(line.strip())
        
        # Check for approval requirements
        if "approval" in response.lower():
            plan["approvals_required"].append("human_review")
        
        return plan
    
    def _save_plan(self, plan: Dict) -> Path:
        """Save plan to vault"""
        plans_dir = self.vault_path / "Plans"
        plans_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_name = plan["task"][:30].replace(" ", "_")
        filename = f"PLAN_{task_name}_{timestamp}.md"
        filepath = plans_dir / filename
        
        content = f"""---
created: {plan['created']}
status: {plan['status']}
task: {plan['task']}
---

# Action Plan

{plan.get('raw_response', 'No details available')}
"""
        
        filepath.write_text(content)
        return filepath
    
    def _gather_briefing_data(self, period: str) -> Dict:
        """Gather data from vault for briefing"""
        data = {
            "completed_tasks": [],
            "pending_tasks": [],
            "revenue": 0,
            "expenses": 0,
            "bottlenecks": []
        }
        
        if not self.vault_path:
            return data
        
        # Read Done folder
        done_dir = self.vault_path / "Done"
        if done_dir.exists():
            data["completed_tasks"] = list(done_dir.glob("*.md"))[:10]
        
        # Read Needs_Action folder
        needs_action_dir = self.vault_path / "Needs_Action"
        if needs_action_dir.exists():
            data["pending_tasks"] = list(needs_action_dir.glob("*.md"))[:10]
        
        # Read Accounting folder
        accounting_dir = self.vault_path / "Accounting"
        if accounting_dir.exists():
            # Parse transactions (simplified)
            pass
        
        return data
    
    def _build_briefing_prompt(self, data: Dict, period: str) -> str:
        """Build prompt for CEO briefing generation"""
        return f"""
Generate a CEO Briefing for the {period}.

DATA:
- Completed tasks: {len(data.get('completed_tasks', []))}
- Pending tasks: {len(data.get('pending_tasks', []))}
- Revenue: ${data.get('revenue', 0):.2f}
- Expenses: ${data.get('expenses', 0):.2f}

Create a comprehensive briefing with:
1. Executive Summary
2. Revenue Breakdown
3. Completed Tasks
4. Bottlenecks
5. Proactive Suggestions

Format as markdown with frontmatter YAML.
"""
    
    def _fallback_reason(self, prompt: str, context: str = "") -> str:
        """Fallback to backup model if primary fails"""
        fallback_model = "mistralai/Mistral-7B-Instruct-v0.3"
        logger.info(f"Switching to fallback model: {fallback_model}")
        
        try:
            messages = self._build_messages(prompt, context)
            response = self.client.chat_completion(
                model=fallback_model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Fallback also failed: {e}")
            return f"Error: Unable to generate response. Both primary and fallback models failed. Details: {str(e)}"
    
    def test_connection(self) -> bool:
        """Test connection to Hugging Face API"""
        try:
            response = self.client.chat_completion(
                model=self.model_name,
                messages=[{"role": "user", "content": "Hello, are you there?"}],
                max_tokens=10
            )
            logger.info("Hugging Face connection test successful")
            return True
        except Exception as e:
            logger.error(f"Hugging Face connection test failed: {e}")
            return False


class ModelRouter:
    """
    Router for multiple Hugging Face models
    
    Routes requests to appropriate model based on task type
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.engines = {}
        self._initialize_engines()
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load model router configuration"""
        default_config = {
            "models": {
                "primary": {
                    "name": "meta-llama/Meta-Llama-3-70B-Instruct",
                    "max_tokens": 4096,
                    "temperature": 0.7,
                    "use_case": "general_reasoning"
                },
                "backup": {
                    "name": "mistralai/Mistral-7B-Instruct-v0.3",
                    "max_tokens": 2048,
                    "temperature": 0.7,
                    "use_case": "quick_tasks"
                },
                "fallback": {
                    "name": "microsoft/Phi-3-medium-128k-instruct",
                    "max_tokens": 4096,
                    "temperature": 0.7,
                    "use_case": "long_context"
                }
            },
            "routing_rules": [
                {"condition": "email_reply", "model": "backup"},
                {"condition": "ceo_briefing", "model": "primary"},
                {"condition": "audit_analysis", "model": "primary"},
                {"condition": "default", "model": "primary"}
            ]
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                return json.load(f)
        
        return default_config
    
    def _initialize_engines(self):
        """Initialize reasoning engines for each model"""
        for model_key, model_config in self.config.get("models", {}).items():
            self.engines[model_key] = HuggingFaceReasoningEngine(
                model_name=model_config["name"],
                max_tokens=model_config["max_tokens"],
                temperature=model_config["temperature"]
            )
    
    def get_engine(self, task_type: str) -> HuggingFaceReasoningEngine:
        """Get appropriate engine for task type"""
        for rule in self.config.get("routing_rules", []):
            if rule["condition"] == task_type or rule["condition"] == "default":
                model_key = rule["model"]
                return self.engines.get(model_key, self.engines["primary"])
        
        return self.engines["primary"]
    
    def reason(self, prompt: str, task_type: str = "default", context: str = "") -> str:
        """Route reasoning request to appropriate engine"""
        engine = self.get_engine(task_type)
        return engine.reason(prompt, context)


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Hugging Face Reasoning Engine")
    parser.add_argument("--test", action="store_true", help="Test connection")
    parser.add_argument("--model", type=str, help="Model name to use")
    parser.add_argument("--prompt", type=str, help="Test prompt")
    parser.add_argument("--server", action="store_true", help="Run as server")
    parser.add_argument("--vault", type=str, help="Path to vault")
    
    args = parser.parse_args()
    
    if args.test:
        engine = HuggingFaceReasoningEngine(
            model_name=args.model or "meta-llama/Meta-Llama-3-70B-Instruct",
            vault_path=args.vault
        )
        success = engine.test_connection()
        print(f"Connection test: {'PASSED' if success else 'FAILED'}")
    
    elif args.prompt:
        engine = HuggingFaceReasoningEngine(
            model_name=args.model or "meta-llama/Meta-Llama-3-70B-Instruct",
            vault_path=args.vault
        )
        response = engine.reason(args.prompt)
        print(f"\nResponse:\n{response}")
    
    elif args.server:
        print("Starting Hugging Face Reasoning Engine Server...")
        # Server implementation would go here
        # For now, just keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nServer stopped")
    
    else:
        parser.print_help()
