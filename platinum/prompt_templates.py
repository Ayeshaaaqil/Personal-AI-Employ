"""
Prompt Templates for Hugging Face Reasoning Engine

Standardized prompts for consistent AI Employee behavior
"""

# System prompts for different contexts
SYSTEM_PROMPTS = {
    "default": """You are an AI Employee assistant. You help manage business tasks,
emails, social media, and accounting. You are professional, efficient, and proactive.
You output structured responses when requested.""",

    "email_assistant": """You are an email assistant for a business professional.
You draft professional, courteous, and concise email replies.
You understand business context and respond appropriately to tone.
You never include sensitive information without explicit approval.""",

    "social_media_manager": """You are a social media manager for a tech business.
You create engaging posts for LinkedIn, Facebook, and Instagram.
You understand platform-specific best practices and character limits.
You include relevant hashtags when appropriate.""",

    "accounting_assistant": """You are an accounting assistant.
You categorize transactions, track expenses, and generate financial reports.
You are accurate and detail-oriented.
You flag unusual transactions for human review.""",

    "ceo_briefing": """You are an executive assistant creating CEO briefings.
You synthesize complex information into clear, actionable insights.
You highlight important metrics, bottlenecks, and opportunities.
You are concise but comprehensive.""",

    "task_planner": """You are a task planning assistant.
You break down complex tasks into actionable steps.
You identify dependencies and approval requirements.
You estimate timelines realistically."""
}

# Task-specific prompt templates
PROMPT_TEMPLATES = {
    "email_reply": """
Generate a professional email reply to this message:

--- ORIGINAL EMAIL ---
{email_content}

--- REPLY GUIDELINES ---
- Tone: {tone}
- Length: {length}
- Key points to address: {key_points}
- Call-to-action: {call_to_action}

--- YOUR REPLY ---
""",

    "task_analysis": """
Analyze this task and provide recommendations:

--- TASK ---
{task_content}

--- ANALYSIS REQUIRED ---
1. Task type classification
2. Priority (Low/Medium/High/Urgent)
3. Required actions
4. Approval requirements (Yes/No)
5. Estimated completion time
6. Dependencies

--- FORMAT ---
Respond in JSON format:
{{
  "task_type": "...",
  "priority": "...",
  "actions": [...],
  "requires_approval": true/false,
  "estimated_time": "...",
  "dependencies": [...],
  "notes": "..."
}}
""",

    "action_plan": """
Create a detailed action plan for this task:

--- TASK ---
{task}

--- CONTEXT ---
{context}

--- PLAN REQUIREMENTS ---
1. Clear objective statement
2. Step-by-step actions (with checkboxes)
3. Approval requirements
4. Dependencies and prerequisites
5. Estimated timeline

--- FORMAT ---
Use markdown with YAML frontmatter:
---
created: {timestamp}
status: pending
task: {task}
---

# Action Plan: {task}

## Objective
...

## Steps
- [ ] Step 1
- [ ] Step 2
...

## Approvals Required
...

## Timeline
...
""",

    "transaction_categorization": """
Categorize this business transaction:

--- TRANSACTION ---
Description: {description}
Amount: ${amount}
Date: {date}
Merchant: {merchant}

--- CATEGORIZATION ---
1. Primary Category (Revenue/Expense/Transfer)
2. Subcategory (Software/Marketing/Office/Travel/etc.)
3. Tax-deductible (Yes/No/Partial)
4. Business purpose
5. Notes or flags

--- FORMAT ---
Respond in JSON format:
{{
  "primary_category": "...",
  "subcategory": "...",
  "tax_deductible": true/false,
  "business_purpose": "...",
  "notes": "...",
  "flag_for_review": true/false
}}
""",

    "social_post": """
Create a social media post:

--- TOPIC ---
{topic}

--- PLATFORM ---
{platform}

--- AUDIENCE ---
{audience}

--- POST REQUIREMENTS ---
- Engaging hook/opening
- Main content
- Call-to-action
- Hashtags (if appropriate for platform)
- Emojis (if appropriate for platform)

--- PLATFORM GUIDELINES ---
LinkedIn: Professional, 1300 chars max, business-focused
Facebook: Friendly, engaging, emojis welcome
Instagram: Visual caption, hashtags important, emojis encouraged
Twitter/X: Concise, 280 chars, hashtags important

--- YOUR POST ---
""",

    "ceo_briefing_daily": """
Generate a Daily CEO Briefing:

--- DATE ---
{date}

--- DATA ---
Completed Tasks: {completed_tasks}
Pending Tasks: {pending_tasks}
Revenue Today: ${revenue}
Expenses Today: ${expenses}
Key Metrics: {metrics}

--- BRIEFING STRUCTURE ---
1. Executive Summary (2-3 sentences)
2. Today's Wins
3. Pending Items Requiring Attention
4. Financial Summary
5. Tomorrow's Priorities

--- FORMAT ---
Use markdown with YAML frontmatter.
""",

    "ceo_briefing_weekly": """
Generate a Weekly CEO Briefing:

--- WEEK ---
Week {week_number}, {year}
Period: {start_date} to {end_date}

--- DATA ---
Completed Tasks: {completed_tasks}
Pending Tasks: {pending_tasks}
Revenue This Week: ${revenue}
Expenses This Week: ${expenses}
MRR/ARR: ${mrr}/${arr}
Client Activity: {client_activity}
Team Productivity: {productivity}

--- BRIEFING STRUCTURE ---
1. Executive Summary
2. Revenue Breakdown
   - This Week
   - MTD
   - Trend Analysis
3. Completed Tasks (Top 5)
4. Bottlenecks Identified
5. Financial Summary
6. Proactive Suggestions
   - Cost Optimization
   - Revenue Opportunities
   - Process Improvements
7. Upcoming Deadlines
8. Key Metrics Dashboard

--- FORMAT ---
Use markdown with YAML frontmatter.
Include tables for metrics.
""",

    "approval_request": """
Evaluate if this action requires human approval:

--- ACTION ---
{action_description}

--- CONTEXT ---
{context}

--- APPROVAL RULES ---
- Payments over $500: Require approval
- New recipients: Require approval
- Email to new contacts: Require approval
- Social media posts: Auto-approve if scheduled
- Accounting categorization: Auto-approve under $1000

--- EVALUATION ---
Does this require approval? Why?

--- FORMAT ---
{{
  "requires_approval": true/false,
  "reason": "...",
  "rule_triggered": "...",
  "suggested_reviewer": "..."
}}
""",

    "error_recovery": """
Analyze this error and suggest recovery actions:

--- ERROR ---
Error Type: {error_type}
Error Message: {error_message}
Context: {context}
Timestamp: {timestamp}

--- RECOVERY ANALYSIS ---
1. Root cause
2. Impact assessment
3. Immediate recovery actions
4. Preventive measures
5. Retry recommendation

--- FORMAT ---
{{
  "root_cause": "...",
  "impact": "Low/Medium/High",
  "immediate_actions": [...],
  "preventive_measures": [...],
  "retry_recommended": true/false,
  "retry_delay_seconds": 0
}}
"""
}

# Few-shot examples for better model performance
FEW_SHOT_EXAMPLES = {
    "email_reply": [
        {
            "input": """
Original: Hi, I'm interested in your AI Employee product. Can you send me pricing information?

Tone: Professional and friendly
""",
            "output": """
Subject: Re: AI Employee Pricing Information

Hello,

Thank you for your interest in our AI Employee product! I'd be happy to provide you with pricing information.

Our AI Employee solution is available in three tiers:

• **Bronze Tier**: $500/month - Basic automation (email + file monitoring)
• **Silver Tier**: $1,000/month - Multi-channel automation (email + social media)
• **Gold Tier**: $2,000/month - Full business automation (all channels + accounting)
• **Platinum Tier**: $3,000/month - Enterprise with custom deployment

Each tier includes:
- 24/7 autonomous operation
- Human-in-the-loop approval workflow
- Comprehensive audit logging
- Weekly CEO briefings

Would you like to schedule a 15-minute demo to see the AI Employee in action? I can also provide a custom quote based on your specific needs.

Best regards,
AI Employee Team
"""
        }
    ],
    
    "transaction_categorization": [
        {
            "input": """
Description: AWS Web Services Charge
Amount: $247.50
Merchant: Amazon Web Services
""",
            "output": """
{
  "primary_category": "Expense",
  "subcategory": "Cloud Infrastructure",
  "tax_deductible": true,
  "business_purpose": "Cloud hosting and computing services",
  "notes": "Recurring monthly infrastructure cost",
  "flag_for_review": false
}
"""
        }
    ]
}


def get_prompt(template_name: str, **kwargs) -> str:
    """
    Get a prompt template with variables filled in
    
    Args:
        template_name: Name of template
        **kwargs: Variables to fill in template
        
    Returns:
        Formatted prompt string
    """
    template = PROMPT_TEMPLATES.get(template_name)
    if not template:
        raise ValueError(f"Unknown template: {template_name}")
    
    return template.format(**kwargs)


def get_system_prompt(context: str = "default") -> str:
    """
    Get system prompt for a context
    
    Args:
        context: Context name
        
    Returns:
        System prompt string
    """
    return SYSTEM_PROMPTS.get(context, SYSTEM_PROMPTS["default"])


def get_few_shot_examples(task_type: str) -> list:
    """
    Get few-shot examples for a task type
    
    Args:
        task_type: Type of task
        
    Returns:
        List of example input/output pairs
    """
    return FEW_SHOT_EXAMPLES.get(task_type, [])
