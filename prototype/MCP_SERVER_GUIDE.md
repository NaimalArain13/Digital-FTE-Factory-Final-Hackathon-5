# Customer Success FTE - MCP Server Guide

## Overview

This MCP server exposes the Customer Success AI agent as a set of tools that can be called by Claude or other AI systems via the Model Context Protocol.

## 🚀 Quick Start

### Installation

```bash
# Install MCP SDK
pip install mcp

# Navigate to prototype directory
cd prototype/

# Run the MCP server
python mcp_server.py
```

### Configuration for Claude Code

Add this to your Claude Code MCP configuration (`~/.claude/mcp.json`):

```json
{
  "mcpServers": {
    "customer-success-fte": {
      "command": "python",
      "args": ["/mnt/e/Q4 extension/Hackathon 2k25/Hackathon_05_Digital_FTE/prototype/mcp_server.py"],
      "cwd": "/mnt/e/Q4 extension/Hackathon 2k25/Hackathon_05_Digital_FTE/prototype"
    }
  }
}
```

---

## 📋 Available Tools

### 1. **search_knowledge_base**
Search product documentation for relevant information.

**Parameters:**
- `query` (string, required): The search query
- `max_results` (int, optional): Max results to return (default: 5)

**Returns:**
```json
{
  "success": true,
  "results_count": 3,
  "results": [
    {
      "title": "Product Summary",
      "relevance_score": 4.0,
      "content_preview": "The Customer Success FTE is..."
    }
  ],
  "formatted_output": "Formatted markdown results"
}
```

**Example Usage:**
```python
# Via MCP
result = await search_knowledge_base(
    query="How do I connect WhatsApp to the FTE?",
    max_results=3
)
```

---

### 2. **create_ticket**
Create a support ticket with full channel tracking.

**Parameters:**
- `customer_email` (string, required): Customer's email (primary key)
- `customer_name` (string, required): Customer's name
- `customer_tier` (string, required): Starter/Growth/Enterprise
- `issue` (string, required): Issue description
- `priority` (string, required): low/normal/high/critical
- `channel` (string, required): email/whatsapp/web_form
- `subject` (string, optional): Subject line (for email)

**Returns:**
```json
{
  "success": true,
  "ticket_id": "TKT-1001",
  "ticket": {
    "ticket_id": "TKT-1001",
    "customer_email": "sarah@company.com",
    "topics": ["integration", "channels"],
    "sentiment_score": 0.5,
    "status": "open"
  }
}
```

**Example Usage:**
```python
ticket = await create_ticket(
    customer_email="sarah@company.com",
    customer_name="Sarah Johnson",
    customer_tier="Growth",
    issue="How do I connect WhatsApp?",
    priority="normal",
    channel="email",
    subject="WhatsApp Integration Question"
)
```

---

### 3. **get_customer_history**
Get complete conversation history across ALL channels.

**Parameters:**
- `customer_email` (string, required): Customer's email address

**Returns:**
```json
{
  "success": true,
  "has_history": true,
  "customer_email": "mike@startup.io",
  "summary": {
    "total_interactions": 2,
    "channels_used": ["whatsapp", "email"],
    "original_channel": "whatsapp",
    "has_channel_switch": true,
    "topics_discussed": ["billing", "channels"],
    "average_sentiment": 0.50,
    "sentiment_label": "😐 Neutral",
    "resolution_status": "escalated"
  },
  "interaction_history": [
    {
      "timestamp": "2025-01-15T10:30:00",
      "channel": "whatsapp",
      "customer_message": "I see two charges...",
      "sentiment": 0.5,
      "topics": ["billing"],
      "escalated": true
    }
  ]
}
```

**Example Usage:**
```python
history = await get_customer_history(
    customer_email="mike@startup.io"
)
```

**Key Features:**
- ✅ Shows all interactions across channels
- ✅ Detects channel switches
- ✅ Tracks sentiment trends
- ✅ Lists all topics discussed

---

### 4. **escalate_to_human**
Escalate a ticket to human support team.

**Parameters:**
- `ticket_id` (string, required): Ticket to escalate
- `reason` (string, required): Escalation reason
  - `billing` → Billing Team
  - `legal` → Legal Team
  - `security` → Security Team
  - `outage` → Engineering Team
  - `sla_risk` → Support Manager
  - `no_kb_match` → Tier 2 Support
  - `negative_sentiment` → Senior Support
  - `bug` → Engineering Team
- `details` (string, optional): Additional context
- `priority` (string, optional): normal/high/critical

**Returns:**
```json
{
  "success": true,
  "escalation_id": "ESC-5001",
  "escalation": {
    "escalation_id": "ESC-5001",
    "ticket_id": "TKT-1001",
    "reason": "billing",
    "assigned_team": "Billing Team",
    "priority": "high",
    "status": "pending"
  },
  "message": "Ticket TKT-1001 escalated to Billing Team as ESC-5001"
}
```

**Example Usage:**
```python
escalation = await escalate_to_human(
    ticket_id="TKT-1001",
    reason="billing",
    details="Duplicate charges detected",
    priority="high"
)
```

---

### 5. **send_response**
Send formatted response via the appropriate channel.

**Parameters:**
- `ticket_id` (string, required): Ticket being responded to
- `message` (string, required): Response content
- `channel` (string, required): email/whatsapp/web_form
- `customer_email` (string, optional): Required if ticket not found
- `customer_name` (string, optional): Required if ticket not found

**Returns:**
```json
{
  "success": true,
  "ticket_id": "TKT-1001",
  "formatted_response": "Hi Sarah Johnson,\n\nHere's how...\n\nBest regards,\nCRM Digital Support Team",
  "delivery": {
    "status": "sent",
    "channel": "email",
    "timestamp": "2025-01-15T10:35:00",
    "recipient": "sarah@company.com"
  }
}
```

**Example Usage:**
```python
response = await send_response(
    ticket_id="TKT-1001",
    message="To connect WhatsApp, go to Settings > Integrations...",
    channel="email"
)
```

**Channel-Specific Formatting:**
- **Email**: Formal with greeting + signature
- **WhatsApp**: Concise (<300 chars)
- **Web Form**: Semi-formal

---

### 6. **get_conversation_stats**
Get aggregate statistics across all conversations.

**Parameters:** None

**Returns:**
```json
{
  "success": true,
  "statistics": {
    "total_conversations": 4,
    "total_turns": 6,
    "avg_sentiment": 0.64,
    "escalated_count": 2,
    "solved_count": 0,
    "channel_switches": 1,
    "common_topics": ["channels", "integration", "billing"],
    "tickets": {
      "total_tickets": 6,
      "escalated_tickets": 2,
      "escalation_rate": 33.33
    }
  }
}
```

**Example Usage:**
```python
stats = await get_conversation_stats()
```

---

### 7. **process_customer_message** ⭐ (Recommended)
Full end-to-end message processing pipeline.

**Parameters:**
- `customer_email` (string, required)
- `customer_name` (string, required)
- `customer_tier` (string, required)
- `message` (string, required)
- `channel` (string, required)
- `subject` (string, optional)

**Returns:**
```json
{
  "success": true,
  "ticket_id": "TKT-1005",
  "response": "Hi Sarah,\n\nTo connect WhatsApp...",
  "escalated": false,
  "escalation": null,
  "kb_results_count": 3,
  "sentiment": 0.5,
  "topics": ["integration", "channels"],
  "conversation_summary": "Previous 1 turn(s):\nTopics: integration, channels..."
}
```

**What This Tool Does:**
1. ✅ Creates customer message
2. ✅ Searches knowledge base
3. ✅ Generates response
4. ✅ Checks escalation rules
5. ✅ Formats for channel
6. ✅ Creates ticket
7. ✅ Updates conversation memory
8. ✅ Tracks sentiment & topics

**Example Usage:**
```python
result = await process_customer_message(
    customer_email="sarah@company.com",
    customer_name="Sarah Johnson",
    customer_tier="Growth",
    message="How do I connect WhatsApp to the FTE?",
    channel="email",
    subject="Integration Question"
)

print(result["response"])  # Ready-to-send response
print(result["ticket_id"])  # TKT-1005
```

---

## 🔄 Common Workflows

### Workflow 1: Handle New Customer Message

```python
# 1. Process message (all-in-one)
result = await process_customer_message(
    customer_email="new@customer.com",
    customer_name="New Customer",
    customer_tier="Starter",
    message="I can't log in to my account",
    channel="web_form"
)

# 2. Check if escalated
if result["escalated"]:
    print(f"Escalated to: {result['escalation']['team']}")
else:
    # Send the response
    await send_response(
        ticket_id=result["ticket_id"],
        message=result["response"],
        channel="web_form"
    )
```

### Workflow 2: Handle Follow-up Message

```python
# 1. Get customer history first
history = await get_customer_history(
    customer_email="sarah@company.com"
)

# 2. Process follow-up with context
result = await process_customer_message(
    customer_email="sarah@company.com",
    customer_name="Sarah Johnson",
    customer_tier="Growth",
    message="Thanks! Where do I find the API key?",
    channel="email"
)

# 3. Send response
await send_response(
    ticket_id=result["ticket_id"],
    message=result["response"],
    channel="email"
)
```

### Workflow 3: Manual Escalation

```python
# 1. Create ticket
ticket = await create_ticket(
    customer_email="vip@enterprise.com",
    customer_name="VIP Customer",
    customer_tier="Enterprise",
    issue="Platform is down for our entire team",
    priority="critical",
    channel="email"
)

# 2. Escalate immediately
escalation = await escalate_to_human(
    ticket_id=ticket["ticket_id"],
    reason="outage",
    details="Enterprise customer, critical priority",
    priority="critical"
)

# 3. Send acknowledgment
await send_response(
    ticket_id=ticket["ticket_id"],
    message="Our Engineering team has been notified and is investigating.",
    channel="email"
)
```

### Workflow 4: Research Customer Context

```python
# 1. Get full history
history = await get_customer_history(
    customer_email="problem@customer.com"
)

# 2. Check for patterns
if history["summary"]["has_channel_switch"]:
    print("⚠️ Customer switched channels - may be frustrated")

if history["summary"]["average_sentiment"] < 0.4:
    print("⚠️ Negative sentiment trend - consider escalation")

# 3. Search relevant topics
for topic in history["summary"]["topics_discussed"]:
    kb_results = await search_knowledge_base(query=topic)
```

---

## 🔍 Integration Examples

### Example 1: Gmail Webhook Integration

```python
@app.post("/webhook/gmail")
async def handle_gmail(email_data: dict):
    result = await process_customer_message(
        customer_email=email_data["from"],
        customer_name=email_data["sender_name"],
        customer_tier=get_tier(email_data["from"]),
        message=email_data["body"],
        channel="email",
        subject=email_data["subject"]
    )

    # Send via Gmail API
    send_gmail(to=email_data["from"], body=result["response"])
```

### Example 2: WhatsApp (Twilio) Integration

```python
@app.post("/webhook/whatsapp")
async def handle_whatsapp(msg: dict):
    result = await process_customer_message(
        customer_email=get_email_from_phone(msg["From"]),
        customer_name=msg["ProfileName"],
        customer_tier=get_tier_from_phone(msg["From"]),
        message=msg["Body"],
        channel="whatsapp"
    )

    # Send via Twilio
    send_whatsapp(to=msg["From"], body=result["response"])
```

### Example 3: Web Form Integration

```python
@app.post("/api/support")
async def handle_support_form(form: SupportForm):
    result = await process_customer_message(
        customer_email=form.email,
        customer_name=form.name,
        customer_tier=form.tier,
        message=form.message,
        channel="web_form"
    )

    return {
        "ticket_id": result["ticket_id"],
        "response": result["response"],
        "escalated": result["escalated"]
    }
```

---

## 📊 Monitoring & Analytics

### Get Real-time Stats

```python
# Overall statistics
stats = await get_conversation_stats()

print(f"Escalation Rate: {stats['statistics']['tickets']['escalation_rate']}%")
print(f"Avg Sentiment: {stats['statistics']['avg_sentiment']}")
print(f"Channel Switches: {stats['statistics']['channel_switches']}")
```

### Track Individual Customer Journey

```python
history = await get_customer_history("customer@example.com")

# Analyze sentiment trend
sentiments = [turn["sentiment"] for turn in history["interaction_history"]]
if sentiments[-1] < sentiments[0]:
    print("⚠️ Sentiment declining - needs attention")
```

---

## 🛠️ Production Considerations

### Current Limitations (Prototype)
- ✅ In-memory storage (tickets & escalations)
- ✅ Simple keyword-based KB search
- ✅ Basic sentiment analysis

### Production Enhancements Needed
1. **Database Integration**
   - PostgreSQL for tickets, conversations, escalations
   - pgvector for semantic search

2. **Real Channel Integration**
   - Gmail API + Pub/Sub
   - Twilio WhatsApp API
   - WebSocket for web form

3. **Advanced Features**
   - ML-based sentiment (not just keywords)
   - Vector embeddings for better KB search
   - Conversation timeout handling
   - SLA tracking & alerts

---

## 🎯 Success Metrics

Track these via `get_conversation_stats()`:

- **Escalation Rate**: Target <20%
- **Average Sentiment**: Target >0.6 (positive)
- **Channel Switch Rate**: Monitor for frustration signals
- **Resolution Time**: Track ticket lifecycle
- **Topic Coverage**: Identify KB gaps

---

## 📝 Notes

- All tools return JSON strings (parseable)
- Email is the primary customer identifier
- Conversation memory is cross-channel
- Sentiment tracked on every interaction
- Topics auto-extracted and tracked
- Escalations auto-route to correct team

---

## 🚀 Next Steps

1. Test each tool individually
2. Run the demo scenarios
3. Integrate with real channels
4. Monitor escalation patterns
5. Improve KB coverage based on common topics
