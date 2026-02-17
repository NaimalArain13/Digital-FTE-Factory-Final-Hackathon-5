# Testing Guide - Customer Success FTE

## ✅ Updated for FastMCP

Your MCP server now uses FastMCP and has **4 core tools**:
1. `search_knowledge_base` - Search product docs
2. `create_ticket` - Create support tickets
3. `escalate_to_human` - Escalate tickets
4. `process_customer_message` - Full end-to-end processing (⭐ Recommended)

---

## 🚀 Quick Test (Easiest)

### Option 1: Run Simple Standalone Test

```bash
cd prototype/
python simple_test.py
```

This tests the **core agent logic** without MCP:
- ✅ Knowledge base search
- ✅ Message processing
- ✅ Conversation memory
- ✅ Channel switches
- ✅ Sentiment analysis
- ✅ Auto-escalation

**Output Example:**
```
TEST 4: Billing Issue (Auto-Escalation)
----------------------------------------
Processing: I see two charges for this month on my card...

Response (WhatsApp format):
Connecting you with Billing team — they'll reply within 4 hrs.

⚠️ ESCALATED: True
   Reason: billing
   Team: Billing Team
```

---

## 🔧 Manual Testing Methods

### Method 1: Python REPL (Interactive)

```bash
cd prototype/
python3
```

Then test directly:

```python
from customer_agent_prototype import CustomerSuccessAgent, CustomerMessage

# Initialize agent
agent = CustomerSuccessAgent(docs_path="../context/product-docs.md")

# Test 1: Search KB
results = agent.knowledge_base.search("How to connect WhatsApp?", max_results=3)
for r in results:
    print(f"{r['title']}: {r['score']}")

# Test 2: Process a message
msg = CustomerMessage(
    channel="email",
    customer_email="test@example.com",
    customer_name="Test User",
    customer_tier="Growth",
    content="How do I connect WhatsApp to the FTE?"
)

result = agent.process_message(msg)
print(result["response"])
print(f"Escalated: {result['escalation'].get('escalate')}")

# Test 3: Check conversation history
conv = agent.conversation_memory.get_conversation("test@example.com")
print(f"Turns: {len(conv.turns)}")
print(f"Topics: {conv.topics_discussed}")
print(f"Sentiment: {conv.average_sentiment:.2f}")
```

---

### Method 2: Test Scenarios

Create a file `my_test.py`:

```python
from customer_agent_prototype import CustomerSuccessAgent, CustomerMessage

agent = CustomerSuccessAgent(docs_path="../context/product-docs.md")

# Scenario: Billing issue with channel switch
print("="*60)
print("SCENARIO: Billing Issue with Channel Switch")
print("="*60)

# Turn 1: WhatsApp
msg1 = CustomerMessage(
    channel="whatsapp",
    customer_email="customer@example.com",
    customer_name="Customer Name",
    customer_tier="Growth",
    content="I see duplicate charges on my card"
)
result1 = agent.process_message(msg1)
print(f"\nWhatsApp Response:\n{result1['response']}")

# Turn 2: Email (channel switch!)
msg2 = CustomerMessage(
    channel="email",
    customer_email="customer@example.com",
    customer_name="Customer Name",
    customer_tier="Growth",
    content="Following up on my WhatsApp message about billing"
)
result2 = agent.process_message(msg2)
print(f"\nEmail Response:\n{result2['response']}")

# Check channel switch
conv = agent.conversation_memory.get_conversation("customer@example.com")
print(f"\n⚠️ Channel Switch Detected: {conv.has_channel_switch()}")
print(f"Channels: {conv.channels_used}")
```

Run it:
```bash
python my_test.py
```

---

## 🧪 Test the MCP Server

### Start the Server

```bash
cd prototype/
python mcp_server.py
```

The server will start and be available via the MCP protocol. You can then:
1. Connect from Claude Code
2. Call the tools via MCP client
3. Test end-to-end workflows

### Configure in Claude Code

Add to `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "customer-success-fte": {
      "command": "python",
      "args": ["/mnt/e/Q4 extension/Hackathon 2k25/Hackathon_05_Digital_FTE/prototype/mcp_server.py"]
    }
  }
}
```

Then in Claude Code, you can call:
- `search_knowledge_base(query="...")`
- `create_ticket(customer_email="...", message="...")`
- `process_customer_message(...)` ⭐

---

## 📋 Test Checklist

### ✅ Core Functionality

- [ ] **KB Search** works and returns relevant results
- [ ] **Message Processing** generates appropriate responses
- [ ] **Email formatting** includes greeting and signature
- [ ] **WhatsApp formatting** is concise (<300 chars)
- [ ] **Billing keywords** trigger auto-escalation
- [ ] **Security keywords** trigger auto-escalation
- [ ] **Sentiment analysis** detects positive/negative/neutral

### ✅ Conversation Memory

- [ ] **Follow-up messages** recognize existing conversation
- [ ] **Topics** are extracted and tracked
- [ ] **Sentiment** running average is calculated
- [ ] **Channel switches** are detected
- [ ] **Resolution status** is updated correctly

### ✅ Escalation

- [ ] **Billing issues** escalate to Billing Team
- [ ] **Security issues** escalate to Security Team
- [ ] **Legal keywords** escalate to Legal Team
- [ ] **Low KB match** escalates to Tier 2 Support

---

## 🎯 Example Test Cases

### Test Case 1: Happy Path (How-to Question)

```python
msg = CustomerMessage(
    channel="email",
    customer_email="happy@test.com",
    customer_name="Happy Customer",
    customer_tier="Starter",
    content="Thanks! How do I upload training data for the AI?"
)
result = agent.process_message(msg)

# Expected:
# ✓ Positive sentiment (>0.7)
# ✓ Topics: ["setup", "ai_features"]
# ✓ No escalation
# ✓ KB results returned
```

### Test Case 2: Billing (Auto-Escalation)

```python
msg = CustomerMessage(
    channel="whatsapp",
    customer_email="billing@test.com",
    customer_name="Billing Customer",
    customer_tier="Growth",
    content="I see two charges on my card this month"
)
result = agent.process_message(msg)

# Expected:
# ✓ escalation.escalate = True
# ✓ escalation.reason = "billing"
# ✓ escalation.team = "Billing Team"
# ✓ Short WhatsApp response
```

### Test Case 3: Channel Switch

```python
# Turn 1: WhatsApp
msg1 = CustomerMessage(
    channel="whatsapp",
    customer_email="switch@test.com",
    customer_name="Switcher",
    customer_tier="Enterprise",
    content="Can't log in to my account"
)
agent.process_message(msg1)

# Turn 2: Email
msg2 = CustomerMessage(
    channel="email",
    customer_email="switch@test.com",
    customer_name="Switcher",
    customer_tier="Enterprise",
    content="Following up on my WhatsApp message"
)
agent.process_message(msg2)

conv = agent.conversation_memory.get_conversation("switch@test.com")

# Expected:
# ✓ conv.has_channel_switch() = True
# ✓ conv.channels_used = ["whatsapp", "email"]
# ✓ len(conv.turns) = 2
```

---

## 🔍 Debugging

### View Conversation Memory

```python
from mcp_server import agent

# View all conversations
for email, conv in agent.conversation_memory.conversations.items():
    print(f"\n{email}:")
    print(f"  Turns: {len(conv.turns)}")
    print(f"  Channels: {conv.channels_used}")
    print(f"  Sentiment: {conv.average_sentiment:.2f}")
    print(f"  Status: {conv.resolution_status.value}")
```

### View Tickets

```python
from mcp_server import tickets

for ticket_id, ticket in tickets.items():
    print(f"{ticket_id}: {ticket['status']} - {ticket['issue'][:50]}")
```

### View Escalations

```python
from mcp_server import escalations

for esc_id, esc in escalations.items():
    print(f"{esc_id}: {esc['reason']} -> {esc.get('assigned_team', 'N/A')}")
```

---

## 📊 Expected Test Output

When you run `simple_test.py`, you should see:

```
✓ TEST 1: Knowledge Base Search
  - Found 3 results

✓ TEST 2: Process Email Message
  - Response generated with greeting and signature
  - No escalation for how-to question

✓ TEST 3: Follow-up Message
  - Conversation recognized (2 turns)
  - Topics tracked

✓ TEST 4: Billing Issue
  - Auto-escalated to Billing Team
  - Short WhatsApp response format

✓ TEST 5: Channel Switch Detection
  - Switch detected: whatsapp → email

✓ TEST 6: Overall Statistics
  - 2 conversations, 4 turns
  - 1 channel switch
  - Common topics: billing, integration, channels

✓ TEST 7: Sentiment Analysis
  - Positive: 1.00
  - Negative: 0.30
  - Neutral: 0.50
```

---

## 🚀 Production Testing

Once manual tests pass:

1. **Load Test**: Process 100+ messages
2. **Real Data**: Test with sanitized customer messages
3. **Channel Integration**: Connect to Gmail/WhatsApp webhooks
4. **Monitoring**: Track escalation rate (<20% target)
5. **KB Improvement**: Identify common topics with no KB match

---

## 💡 Tips

- Use `simple_test.py` for quick validation
- Use Python REPL for interactive exploration
- Check conversation memory after each test
- Verify sentiment scores make sense
- Ensure channel switches are detected
- Test all escalation triggers (billing, legal, security)

Happy testing! 🎉
