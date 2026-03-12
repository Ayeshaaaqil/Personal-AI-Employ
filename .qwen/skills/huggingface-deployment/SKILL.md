# Hugging Face Deployment Skill - Platinum Tier

**Skill Name:** `huggingface-deployment`

**Tier:** Platinum

**Description:** Deploy and manage AI Employee on Hugging Face Spaces using open-source LLMs.

---

## When to Use This Skill

Use this skill when you want to:

1. **Deploy AI Employee to Hugging Face Spaces** - Run your AI Employee on free cloud infrastructure
2. **Use open-source LLMs** - Replace Claude Code with Llama 3, Mistral, Qwen, etc.
3. **Enable web dashboard** - Provide browser-based monitoring and control
4. **Reduce costs** - Run on Hugging Face free tier (no API costs)
5. **Customize models** - Fine-tune on your specific data

---

## Server Lifecycle Management

### 1. Install Dependencies

```bash
cd C:\Users\Dell\Documents\GitHub\Personal-AI-Employ
pip install -r platinum/requirements.txt
```

### 2. Set Environment Variables

```bash
# Get token from: https://huggingface.co/settings/tokens
export HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
export HUGGINGFACE_MODEL=meta-llama/Meta-Llama-3-70B-Instruct
```

Or create `.env` file:
```bash
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HUGGINGFACE_MODEL=meta-llama/Meta-Llama-3-70B-Instruct
```

### 3. Test Connection

```bash
cd platinum
python huggingface_reasoning_engine.py --test
```

### 4. Deploy to Hugging Face Spaces

```bash
cd deployment
python deploy_to_huggingface.py --repo your-username/ai-employee-platinum
```

### 5. Access Your Space

Your AI Employee will be live at:
```
https://huggingface.co/spaces/your-username/ai-employee-platinum
```

---

## Quick Reference

### Deploy to Hugging Face

```python
from .qwen.skills.huggingface-deployment.skill import HuggingFaceDeploymentSkill

skill = HuggingFaceDeploymentSkill(vault_path="AI_Employee_Vault")

# Deploy
result = skill.deploy_to_huggingface("your-username/ai-employee-platinum")
print(f"Space URL: {result['space_url']}")
```

### Query the Model

```python
# Query with default model
response = skill.query_model("What tasks are pending?")

# Query with specific model
response = skill.query_model(
    "Generate an email reply",
    model="mistralai/Mistral-7B-Instruct-v0.3"
)
```

### List Available Models

```python
models = skill.list_available_models()
for model in models:
    print(f"- {model['name']} ({model['size']})")
```

### Switch Model

```python
result = skill.switch_model("Qwen/Qwen2.5-72B-Instruct")
print(result['message'])
```

### Test Connection

```bash
python .qwen/skills/huggingface-deployment/skill.py AI_Employee_Vault --test
```

### Get Status

```bash
python .qwen/skills/huggingface-deployment/skill.py AI_Employee_Vault --status
```

---

## Configuration

### Model Configuration

Edit `platinum/model_config.yaml`:

```yaml
models:
  primary:
    name: "meta-llama/Meta-Llama-3-70B-Instruct"
    max_tokens: 4096
    temperature: 0.7
  
  backup:
    name: "mistralai/Mistral-7B-Instruct-v0.3"
    max_tokens: 2048
    temperature: 0.7
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HUGGINGFACE_TOKEN` | Your HF API token | Required |
| `HUGGINGFACE_MODEL` | Model to use | `meta-llama/Meta-Llama-3-70B-Instruct` |
| `VAULT_PATH` | Path to Obsidian vault | `/tmp/ai_employee_vault` |
| `PORT` | Web dashboard port | `7860` |

---

## Troubleshooting

### Connection Failed

**Error:** `Hugging Face API error: 401 Unauthorized`

**Solution:**
1. Check token is valid: https://huggingface.co/settings/tokens
2. Ensure token has `read` permissions
3. Verify environment variable is set

### Rate Limit Exceeded

**Error:** `429 Too Many Requests`

**Solution:**
1. Switch to smaller model (Llama 3 8B)
2. Add retry logic with backoff
3. Upgrade to Hugging Face Pro ($9/month)

### Model Not Found

**Error:** `404 Model not found`

**Solution:**
1. Verify model name is correct
2. Check model exists on Hugging Face
3. Ensure you have access permissions

### Deployment Failed

**Error:** `Failed to create Space`

**Solution:**
1. Check repository name format: `username/repo-name`
2. Verify token has `write` permissions
3. Check Space doesn't already exist

---

## Performance Benchmarks

| Model | Avg Response Time | Context Window | Best For |
|-------|------------------|----------------|----------|
| Llama 3 70B | 2-5s | 8K | General reasoning |
| Llama 3 8B | 0.5-2s | 8K | Fast tasks |
| Mistral 7B | 0.5-2s | 32K | Quick inference |
| Qwen 2.5 72B | 3-6s | 32K | Multi-language |
| Phi-3 Medium | 1-3s | 128K | Long context |

---

## Cost Comparison

| Tier | Model | Monthly Cost |
|------|-------|--------------|
| **Free** | Llama 3 8B, Mistral 7B | $0 |
| **Pro** | Llama 3 70B, Qwen 72B | $9 |
| **Enterprise** | Custom fine-tuned | Custom |

**vs Claude Code:**
- Claude Pro: $20/month
- Hugging Face Free: $0/month
- **Savings: 100%**

---

## Examples

### Example 1: Generate Email Reply

```python
skill = HuggingFaceDeploymentSkill("AI_Employee_Vault")

prompt = """
Generate a professional email reply:

Original: Hi, I'm interested in your AI Employee product.
Can you send me pricing information?

Tone: Professional and friendly
"""

response = skill.query_model(prompt)
print(response)
```

### Example 2: Generate CEO Briefing

```python
prompt = """
Generate a weekly CEO briefing with:
- Revenue summary
- Completed tasks
- Bottlenecks
- Proactive suggestions

Format as markdown with YAML frontmatter.
"""

briefing = skill.query_model(prompt)

# Save to vault
with open("AI_Employee_Vault/Briefings/weekly_briefing.md", "w") as f:
    f.write(briefing)
```

### Example 3: Deploy with Custom Model

```python
skill = HuggingFaceDeploymentSkill("AI_Employee_Vault")

# Switch to Mistral for faster responses
skill.switch_model("mistralai/Mistral-7B-Instruct-v0.3")

# Deploy
result = skill.deploy_to_huggingface("my-org/ai-employee")
print(f"Deployed with Mistral 7B: {result['space_url']}")
```

---

## Security Considerations

1. **Never commit tokens** - Add `.env` to `.gitignore`
2. **Use Hugging Face Secrets** - Store tokens in Space settings
3. **Rotate tokens monthly** - Generate new tokens regularly
4. **Limit Space access** - Use private Spaces for sensitive data

---

## Additional Resources

- [Hugging Face Inference API Docs](https://huggingface.co/docs/api-inference)
- [Hugging Face Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [Llama 3 Model Card](https://huggingface.co/meta-llama/Meta-Llama-3-70B-Instruct)
- [Platinum Tier Documentation](../../../PLATINUM_README.md)

---

*Platinum Tier Skill - AI Employee*
