# Manual Testing Guide for MCP Tools

## 🚀 Quick Start - 3 Ways to Test

### Method 1: Interactive Menu (Recommended for Beginners)

```bash
cd prototype/
python manual_test.py
```

This gives you an interactive menu where you can:
- Select which tool to test (1-7)
- Enter custom data or use defaults
- See formatted results instantly

**Example Session:**
```
Select a tool to test:
  1. search_knowledge_base - Search product docs
  2. create_ticket - Create a support ticket
  7. process_customer_message - Full pipeline (RECOMMENDED)

Enter your choice: 7

Customer email [demo@company.com]: sarah@company.com
Customer name [Demo User]: Sarah Johnson
Customer message [How do I upload training data?]: How do I connect WhatsApp?

Processing message end-to-end...

RESPONSE GENERATED:
----------------------------------------------------------------------
Hi Sarah Johnson,

Based on our product documentation...
```

---

### Method 2: Python REPL (Quick Tests)

```bash
cd prototype/
python3
```

Then run individual tools:

```python
import asyncio
from mcp_server import search_knowledge_base, process_customer_message

# Test 1: Search knowledge base
result = asyncio.run(search_knowledge_base(
    query="How do I connect WhatsApp?",
    max_results=3
))
print(result)

# Test 2: Process a complete customer message
result = asyncio.run(process_customer_message(
    customer_email="test@example.com",
    customer_name="Test User",
    customer_tier="Growth",
    message="I see duplicate charges on my card",
    channel="email"
))

import json
data = json.loads(result)
print("Response:", data["response"])
print("Escalated:", data["escalated"])
print("Sentiment:", data["sentiment"])
```

---

### Method 3: Automated Test Suite

```bash
cd prototype/
python test_mcp_tools.py
```

Runs all 7 tools with predefined scenarios showing:
- Sarah's multi-turn email conversation
- Mike's channel switch (WhatsApp → Email)
- David's security escalation
- Emma's positive feedback

---

## 📋 Tool-by-Tool Testing Examples

### Tool 1: search_knowledge_base

**Python REPL:**
```python
import asyncio
from mcp_server import search_knowledge_base

result = asyncio.run(search_knowledge_base(
    query="How to set up integrations?",
    max_results=5
))
print(result)
```

**Expected Output:**
```json
{
  "success": true,
  "results_count": 3,
  "results": [
    {
      "title": "1) Ingestion & Channel Handlers",
      "relevance_score": 4.5,
      "content_preview": "Gmail: webhook / Gmail API..."
    }
  ]
}
```

---

### Tool 2: create_ticket

**Python REPL:**
```python
import asyncio
from mcp_server import create_ticket

result = asyncio.run(create_ticket(
    customer_email="sarah@company.com",
    customer_name="Sarah Johnson",
    customer_tier="Growth",
    issue="How do I connect WhatsApp to the FTE?",
    priority="normal",
    channel="email",
    subject="Integration Question"
))
print(result)
```

**Expected Output:**
```json
{
  "success": true,
  "ticket_id": "TKT-1001",
  "ticket": {
    "customer_email": "sarah@company.com",
    "topics": ["integration", "channels"],
    "sentiment_score": 0.5,
    "status": "open"
  }
}
```

---

### Tool 3: get_customer_history

**Python REPL:**
```python
import asyncio
from mcp_server import get_customer_history

# First, create some conversation history
from mcp_server import process_customer_message

# Message 1
asyncio.run(process_customer_message(
    customer_email="mike@startup.io",
    customer_name="Mike Chen",
    customer_tier="Growth",
    message="I see two charges on my card",
    channel="whatsapp"
))

# Message 2 (channel switch!)
asyncio.run(process_customer_message(
    customer_email="mike@startup.io",
    customer_name="Mike Chen",
    customer_tier="Growth",
    message="Following up on my WhatsApp message",
    channel="email"
))

# Now get history
result = asyncio.run(get_customer_history(
    customer_email="mike@startup.io"
))
print(result)
```

**Expected Output:**
```json
{
  "success": true,
  "has_history": true,
  "summary": {
    "total_interactions": 2,
    "channels_used": ["whatsapp", "email"],
    "has_channel_switch": true,
    "topics_discussed": ["billing", "channels"],
    "average_sentiment": 0.50,
    "resolution_status": "escalated"
  }
}
```

---

### Tool 4: escalate_to_human

**Python REPL:**
```python
import asyncio
import json
from mcp_server import create_ticket, escalate_to_human

# First create a ticket
ticket_result = asyncio.run(create_ticket(
    customer_email="urgent@company.com",
    customer_name="Urgent Customer",
    customer_tier="Enterprise",
    issue="Platform is down",
    priority="critical",
    channel="email"
))
ticket_id = json.loads(ticket_result)["ticket_id"]

# Then escalate it
result = asyncio.run(escalate_to_human(
    ticket_id=ticket_id,
    reason="outage",
    details="Enterprise customer, critical production issue",
    priority="critical"
))
print(result)
```

**Expected Output:**
```json
{
  "success": true,
  "escalation_id": "ESC-5001",
  "escalation": {
    "reason": "outage",
    "assigned_team": "Engineering Team",
    "priority": "critical",
    "status": "pending"
  }
}
```

---

### Tool 5: send_response

**Python REPL:**
```python
import asyncio
import json
from mcp_server import create_ticket, send_response

# Create ticket
ticket_result = asyncio.run(create_ticket(
    customer_email="customer@example.com",
    customer_name="Customer Name",
    customer_tier="Growth",
    issue="How do I reset password?",
    priority="normal",
    channel="email"
))
ticket_id = json.loads(ticket_result)["ticket_id"]

# Send response
result = asyncio.run(send_response(
    ticket_id=ticket_id,
    message="To reset your password, go to Settings > Account > Reset Password.",
    channel="email"
))
print(result)
```

**Expected Output:**
```json
{
  "success": true,
  "formatted_response": "Hi Customer Name,\n\nTo reset your password...\n\nBest regards,\nCRM Digital Support Team",
  "delivery": {
    "status": "sent",
    "channel": "email",
    "recipient": "customer@example.com"
  }
}
```

---

### Tool 6: get_conversation_stats

**Python REPL:**
```python
import asyncio
from mcp_server import get_conversation_stats

result = asyncio.run(get_conversation_stats())
print(result)
```

**Expected Output:**
```json
{
  "success": true,
  "statistics": {
    "total_conversations": 4,
    "total_turns": 6,
    "avg_sentiment": 0.64,
    "escalated_count": 2,
    "channel_switches": 1,
    "common_topics": ["billing", "integration", "channels"],
    "tickets": {
      "total_tickets": 6,
      "escalation_rate": 33.33
    }
  }
}
```

---

### Tool 7: process_customer_message ⭐ (Recommended)

**Python REPL:**
```python
import asyncio
import json
from mcp_server import process_customer_message

result = asyncio.run(process_customer_message(
    customer_email="sarah@company.com",
    customer_name="Sarah Johnson",
    customer_tier="Growth",
    message="How do I connect WhatsApp to the FTE?",
    channel="email",
    subject="Integration Question"
))

data = json.loads(result)
print("="*70)
print("RESPONSE:")
print("="*70)
print(data["response"])
print("\nDetails:")
print(f"  Ticket ID: {data['ticket_id']}")
print(f"  Escalated: {data['escalated']}")
print(f"  Sentiment: {data['sentiment']:.2f}")
print(f"  Topics: {', '.join(data['topics'])}")
```

**Expected Output:**
```
======================================================================
RESPONSE:
======================================================================
Hi Sarah Johnson,

Here's how to do that:

The Customer Success FTE is an AI-first support automation that:
- Ingests customer messages from Gmail, WhatsApp, and a web support form
...

Best regards,
CRM Digital Support Team

Details:
  Ticket ID: TKT-1005
  Escalated: False
  Sentiment: 0.50
  Topics: integration, channels
```

---

## 🧪 Test Scenarios

### Scenario 1: Happy Path (How-to Question)

```python
import asyncio
from mcp_server import process_customer_message

# Customer asks a how-to question
result = asyncio.run(process_customer_message(
    customer_email="happy@customer.com",
    customer_name="Happy Customer",
    customer_tier="Starter",
    message="Thanks for the great service! How do I upload training data?",
    channel="web_form"
))

# Should:
# ✓ Return helpful response from KB
# ✓ Not escalate
# ✓ Show positive sentiment (>0.7)
# ✓ Extract topic: "setup", "ai_features"
```

### Scenario 2: Billing Issue (Auto-Escalation)

```python
result = asyncio.run(process_customer_message(
    customer_email="billing@customer.com",
    customer_name="Billing Customer",
    customer_tier="Growth",
    message="I see duplicate charges on my credit card this month",
    channel="whatsapp"
))

# Should:
# ✓ Auto-escalate to Billing Team
# ✓ Short WhatsApp response
# ✓ Extract topic: "billing"
# ✓ Create escalation record
```

### Scenario 3: Channel Switch

```python
# Turn 1: WhatsApp
result1 = asyncio.run(process_customer_message(
    customer_email="switcher@customer.com",
    customer_name="Channel Switcher",
    customer_tier="Enterprise",
    message="I can't log in",
    channel="whatsapp"
))

# Turn 2: Email (switch!)
result2 = asyncio.run(process_customer_message(
    customer_email="switcher@customer.com",
    customer_name="Channel Switcher",
    customer_tier="Enterprise",
    message="Following up on my WhatsApp message about login",
    channel="email"
))

# Then check history
from mcp_server import get_customer_history
history = asyncio.run(get_customer_history("switcher@customer.com"))

# Should show:
# ✓ has_channel_switch: true
# ✓ channels_used: ["whatsapp", "email"]
# ✓ 2 interactions
```

### Scenario 4: Security Escalation

```python
result = asyncio.run(process_customer_message(
    customer_email="security@customer.com",
    customer_name="Security Concern",
    customer_tier="Enterprise",
    message="We suspect unauthorized access to our account",
    channel="email",
    subject="URGENT: Security Issue"
))

# Should:
# ✓ Auto-escalate to Security Team (Critical)
# ✓ Extract topic: "security", "account"
# ✓ Priority: critical
```

---

## 🔍 Debugging Tips

### Check if tools are working:

```python
import asyncio
from mcp_server import search_knowledge_base

# Simple test
result = asyncio.run(search_knowledge_base("test"))
print("Success!" if "success" in result else "Failed")
```

### View raw data structures:

```python
import asyncio
import json
from mcp_server import process_customer_message

result = asyncio.run(process_customer_message(
    customer_email="debug@test.com",
    customer_name="Debug",
    customer_tier="Growth",
    message="test",
    channel="email"
))

# Parse and inspect
data = json.loads(result)
print(json.dumps(data, indent=2))
```

### Check conversation memory:

```python
from mcp_server import agent

# View all conversations
for email, conv in agent.conversation_memory.conversations.items():
    print(f"{email}: {len(conv.turns)} turns")
    print(f"  Channels: {conv.channels_used}")
    print(f"  Sentiment: {conv.average_sentiment:.2f}")
```

### Check tickets:

```python
from mcp_server import tickets

print(f"Total tickets: {len(tickets)}")
for ticket_id, ticket in tickets.items():
    print(f"{ticket_id}: {ticket['status']}")
```

---

## ✅ Quick Verification Checklist

After testing, verify:

- [ ] **search_knowledge_base** returns relevant docs
- [ ] **create_ticket** generates ticket IDs (TKT-XXXX)
- [ ] **get_customer_history** shows conversation turns
- [ ] **escalate_to_human** routes to correct team
- [ ] **send_response** formats correctly per channel
- [ ] **get_conversation_stats** shows aggregate data
- [ ] **process_customer_message** does end-to-end processing
- [ ] Billing keywords trigger auto-escalation
- [ ] Channel switches are detected
- [ ] Sentiment is analyzed correctly
- [ ] Topics are extracted

---

## 🎯 Next Steps

Once manual testing is complete:
1. Test with real customer data (sanitized)
2. Integrate with actual Gmail/WhatsApp webhooks
3. Monitor escalation rates
4. Analyze common topics for KB improvements
5. Track sentiment trends

Happy testing! 🚀
