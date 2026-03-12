---
name: linkedin-mcp
description: |
  LinkedIn MCP for AI Employee. Post updates, articles, and engage with
  LinkedIn network. Uses Playwright for browser automation. Use when
  tasks require posting business updates, sharing content, or networking.
---

# LinkedIn MCP Skill

Post and manage LinkedIn content for the AI Employee.

## Prerequisites

1. **Install Playwright:**
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **LinkedIn Account:**
   - Have LinkedIn credentials ready
   - First-time login required

3. **Install Dependencies:**
   ```bash
   pip install playwright
   ```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Qwen Code      │────▶│  LinkedIn MCP    │────▶│  LinkedIn Web   │
│  (create post)  │     │  (Playwright)    │     │  (post content) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Setup

### First-Time Login

```bash
cd watchers
python linkedin_watcher.py --login
```

This opens a browser for you to login to LinkedIn. The session is saved for future use.

### Start LinkedIn MCP Server

```bash
# The MCP server runs via Playwright
npx @playwright/mcp@latest --port 8808
```

## Quick Reference

### Post Update

```bash
# Post a business update
qwen "Post on LinkedIn: Excited to announce our new AI Employee service!"
```

### Share Article

```bash
# Share an article with commentary
qwen "Share this article on LinkedIn: https://example.com/article with comment 'Great insights on AI automation'"
```

### Engage with Network

```bash
# Comment on recent posts
qwen "Find recent posts from my network and engage with 3 of them"
```

## Post Templates

### Business Announcement

```
🚀 Exciting News!

We're thrilled to announce [PRODUCT/SERVICE]!

After months of development, we're ready to help businesses automate their workflows with AI.

Key features:
✅ 24/7 monitoring
✅ Automated responses
✅ Human-in-the-loop approvals

Learn more: [LINK]

#AI #Automation #Business #Innovation
```

### Project Completion

```
✅ Project Complete!

Just wrapped up [PROJECT NAME] for [CLIENT].

Results:
📈 50% time saved
💰 30% cost reduction
⭐ Happy client

Ready to start your automation journey? Let's connect!

#ProjectSuccess #Automation #AI
```

### Thought Leadership

```
💡 Insight of the Day

[INDUSTRY] is changing fast. Here's what I'm seeing:

1. [TREND 1]
2. [TREND 2]
3. [TREND 3]

What trends are you watching?

#ThoughtLeadership #Industry #Future
```

### Client Testimonial

```
⭐ Client Love

"[TESTIMONIAL TEXT]"

- [CLIENT NAME], [COMPANY]

We're honored to help businesses like [COMPANY] achieve their goals.

#ClientSuccess #Testimonial #AI
```

## Workflow: Post Business Update

1. **Qwen creates** post content in Plans/
2. **Creates approval** in Pending_Approval/
3. **Human approves** (move to Approved/)
4. **LinkedIn MCP posts** via Playwright
5. **Logs result** to Dashboard

## Approval Request Format

```markdown
---
type: approval_request
action: linkedin_post
content: Excited to announce...
scheduled_time: 2026-03-05T14:00:00
created: 2026-03-05T12:00:00
---

# LinkedIn Post Approval

## Content

[Post content here]

## To Approve

Move to /Approved folder.

## To Reject

Move to /Rejected folder.
```

## Posting Schedule

| Type | Best Time | Frequency |
|------|-----------|-----------|
| Business updates | Tue-Thu 9-11 AM | 2-3/week |
| Thought leadership | Wed 2-4 PM | 1-2/week |
| Client success | Mon, Fri | 1/week |
| Industry news | Daily | 1/day |

## Engagement Rules

| Action | Auto-Approve | Require Approval |
|--------|--------------|------------------|
| Scheduled posts | Yes | No |
| Responding to comments | No | Yes |
| Sharing industry news | Yes | No |
| Original content | No | Yes |

## Error Handling

| Error | Recovery |
|-------|----------|
| Session expired | Re-run: `linkedin_watcher.py --login` |
| Post failed | Check content length (< 3000 chars) |
| Rate limited | Wait 24 hours, reduce frequency |
| Browser crash | Restart Playwright server |

## Best Practices

1. **Keep it professional**: LinkedIn is a business network
2. **Use hashtags**: 3-5 relevant hashtags per post
3. **Include visuals**: Posts with images get 2x engagement
4. **Engage authentically**: Respond to comments within 24 hours
5. **Track metrics**: Monitor views, likes, comments

## Security Notes

- Store session outside the vault
- Never commit session files to git
- Review posts before publishing
- Log all posted content

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't login | Clear session: delete linkedin-session/ |
| Post not appearing | Check LinkedIn for errors |
| Session keeps expiring | Login with "Remember me" checked |
| Browser won't start | Run: `playwright install chromium` |

## Metrics to Track

- Post views
- Engagement rate (likes + comments / views)
- Connection requests received
- Profile views after posting

## Integration with AI Employee

```
Business goal updated in Business_Goals.md
    ↓
Qwen detects milestone reached
    ↓
Creates LinkedIn post draft
    ↓
Approval request in Pending_Approval/
    ↓
Human approves
    ↓
LinkedIn MCP posts
    ↓
Logs to Dashboard
```
