"""
Hugging Face Deployment Agent Skill - Platinum Tier

This skill provides the capability to deploy and manage
AI Employee on Hugging Face Spaces using open-source LLMs.

When to use:
- Deploy AI Employee to Hugging Face Spaces
- Manage open-source LLM models (Llama, Mistral, Qwen)
- Run reasoning engine on cloud infrastructure
- Enable web dashboard for monitoring

Server Lifecycle:
1. Install dependencies: pip install -r platinum/requirements.txt
2. Set environment: HUGGINGFACE_TOKEN, HUGGINGFACE_MODEL
3. Deploy: python deployment/deploy_to_huggingface.py
4. Monitor: Access web dashboard at HF Spaces URL
"""

import os
import sys
from pathlib import Path

# Add platinum to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'platinum'))

try:
    from huggingface_reasoning_engine import HuggingFaceReasoningEngine, ModelRouter
    from huggingface_agent import HuggingFaceAgent
    SKILL_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Hugging Face modules not available: {e}")
    SKILL_AVAILABLE = False


class HuggingFaceDeploymentSkill:
    """
    Skill for deploying AI Employee on Hugging Face
    """
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.agent = None
        self.engine = None
        
        if SKILL_AVAILABLE:
            try:
                self.agent = HuggingFaceAgent(vault_path=vault_path)
                self.engine = self.agent.engine
            except Exception as e:
                print(f"Warning: Could not initialize agent: {e}")
    
    def deploy_to_huggingface(self, repo_name: str) -> dict:
        """
        Deploy AI Employee to Hugging Face Spaces
        
        Args:
            repo_name: Repository name (username/repo-name)
            
        Returns:
            Deployment result dictionary
        """
        if not SKILL_AVAILABLE:
            return {
                "success": False,
                "error": "Hugging Face modules not available"
            }
        
        # Check for token
        token = os.getenv("HUGGINGFACE_TOKEN")
        if not token:
            return {
                "success": False,
                "error": "HUGGINGFACE_TOKEN environment variable not set"
            }
        
        # Run deployment script
        deploy_script = Path(__file__).parent.parent.parent / 'deployment' / 'deploy_to_huggingface.py'
        
        if not deploy_script.exists():
            return {
                "success": False,
                "error": "Deployment script not found"
            }
        
        import subprocess
        result = subprocess.run(
            [sys.executable, str(deploy_script), "--repo", repo_name],
            capture_output=True,
            text=True
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "space_url": f"https://huggingface.co/spaces/{repo_name}"
        }
    
    def query_model(self, prompt: str, model: str = None) -> str:
        """
        Query the Hugging Face model
        
        Args:
            prompt: User prompt
            model: Optional model override
            
        Returns:
            Model response
        """
        if not self.engine:
            return "Error: Hugging Face engine not available"
        
        if model:
            # Create temporary engine with different model
            temp_engine = HuggingFaceReasoningEngine(model_name=model)
            return temp_engine.reason(prompt)
        
        return self.engine.reason(prompt)
    
    def list_available_models(self) -> list:
        """
        List available open-source models
        
        Returns:
            List of model dictionaries
        """
        return [
            {
                "name": "meta-llama/Meta-Llama-3-70B-Instruct",
                "size": "70B",
                "context": "8K",
                "best_for": "General reasoning"
            },
            {
                "name": "meta-llama/Meta-Llama-3-8B-Instruct",
                "size": "8B",
                "context": "8K",
                "best_for": "Fast, cheap tasks"
            },
            {
                "name": "mistralai/Mistral-7B-Instruct-v0.3",
                "size": "7B",
                "context": "32K",
                "best_for": "Quick inference"
            },
            {
                "name": "Qwen/Qwen2.5-72B-Instruct",
                "size": "72B",
                "context": "32K",
                "best_for": "Multi-language"
            },
            {
                "name": "microsoft/Phi-3-medium-128k-instruct",
                "size": "14B",
                "context": "128K",
                "best_for": "Long context"
            },
            {
                "name": "mistralai/Mixtral-8x22B-Instruct-v0.1",
                "size": "39B (MoE)",
                "context": "64K",
                "best_for": "Complex tasks"
            }
        ]
    
    def switch_model(self, new_model: str) -> dict:
        """
        Switch to a different model
        
        Args:
            new_model: New model name
            
        Returns:
            Switch result dictionary
        """
        if not SKILL_AVAILABLE:
            return {"success": False, "error": "Skill not available"}
        
        try:
            self.agent = HuggingFaceAgent(
                vault_path=str(self.vault_path),
                model_name=new_model,
                use_router=False
            )
            self.engine = self.agent.engine
            
            return {
                "success": True,
                "model": new_model,
                "message": f"Switched to {new_model}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_connection(self) -> dict:
        """
        Test connection to Hugging Face API
        
        Returns:
            Test result dictionary
        """
        if not self.engine:
            return {
                "success": False,
                "error": "Engine not available"
            }
        
        success = self.engine.test_connection()
        
        return {
            "success": success,
            "model": self.engine.model_name,
            "message": "Connection successful" if success else "Connection failed"
        }
    
    def get_status(self) -> dict:
        """
        Get deployment status
        
        Returns:
            Status dictionary
        """
        return {
            "skill_available": SKILL_AVAILABLE,
            "agent_initialized": self.agent is not None,
            "engine_initialized": self.engine is not None,
            "vault_path": str(self.vault_path),
            "model": self.engine.model_name if self.engine else None,
            "hf_token_set": bool(os.getenv("HUGGINGFACE_TOKEN"))
        }


# Skill interface functions
def get_skill_description() -> str:
    """Get skill description"""
    return """
Hugging Face Deployment Skill for AI Employee Platinum Tier.

Capabilities:
- Deploy to Hugging Face Spaces
- Query open-source LLMs (Llama, Mistral, Qwen)
- Switch between models
- Test API connection
- Monitor deployment status

Usage:
    skill = HuggingFaceDeploymentSkill(vault_path)
    skill.deploy_to_huggingface("username/repo")
    skill.query_model("What tasks are pending?")
    skill.list_available_models()
    skill.switch_model("mistralai/Mistral-7B-Instruct-v0.3")
    skill.test_connection()
    skill.get_status()
"""


def create_skill(vault_path: str) -> HuggingFaceDeploymentSkill:
    """Create skill instance"""
    return HuggingFaceDeploymentSkill(vault_path)


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Hugging Face Deployment Skill")
    parser.add_argument("vault", type=str, help="Path to vault")
    parser.add_argument("--test", action="store_true", help="Test connection")
    parser.add_argument("--status", action="store_true", help="Get status")
    parser.add_argument("--list-models", action="store_true", help="List models")
    parser.add_argument("--query", type=str, help="Query model")
    parser.add_argument("--model", type=str, help="Model to use for query")
    parser.add_argument("--switch", type=str, help="Switch to model")
    
    args = parser.parse_args()
    
    skill = HuggingFaceDeploymentSkill(vault_path=args.vault)
    
    if args.test:
        result = skill.test_connection()
        print(f"Connection test: {result}")
    
    elif args.status:
        result = skill.get_status()
        print(f"Status: {result}")
    
    elif args.list_models:
        models = skill.list_available_models()
        print("Available Models:")
        for model in models:
            print(f"  - {model['name']} ({model['size']}, {model['context']} context)")
            print(f"    Best for: {model['best_for']}")
    
    elif args.query:
        response = skill.query_model(args.query, args.model)
        print(f"Response:\n{response}")
    
    elif args.switch:
        result = skill.switch_model(args.switch)
        print(f"Switch result: {result}")
    
    else:
        parser.print_help()
