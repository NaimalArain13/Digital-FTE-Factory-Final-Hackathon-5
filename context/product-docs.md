# Product Documentation — CRM Digital Customer Success FTE

## Product Summary
The Customer Success FTE is an AI-first support automation that:
- Ingests customer messages from Gmail, WhatsApp, and a web support form
- Normalizes and stores incoming messages in a PostgreSQL CRM
- Searches the Knowledge Hub (KB) to answer product questions
- Formats replies per channel and sends them via channel integrations
- Decides when to escalate to humans (based on rules & sentiment)
- Tracks metrics: response time, escalation rate, sentiment trends

---

## Core Modules & Capabilities

### 1) Ingestion & Channel Handlers
- Gmail: webhook / Gmail API with Pub/Sub or polling handlers
- WhatsApp: Twilio Webhook handler + outgoing messaging
- Web Form: Next.js/embedded component → FastAPI endpoint

Message payload should include:
- channel, channel_message_id, customer_email / customer_phone, subject, content, received_at, metadata

---

### 2) Unified Ticketing / CRM (Postgres)
- Tables: customers, customer_identifiers, conversations, messages, tickets, knowledge_base, channel_configs, agent_metrics
- Conversations keep cross-channel continuity; messages store inbound/outbound with channel metadata.

---

### 3) Knowledge Hub & Retrieval
- KB stores title, content, category, embedding (VECTOR/pgvector)
- Recommended search: semantic vector search, return top 5 results
- Fallback: keyword match, then escalate if no useful results after 2 attempts

---

### 4) Agent Tools (exposed as MCP or OpenAI Agents SDK tools)
- search_knowledge_base(query, max_results=5) -> formatted snippets
- create_ticket(customer_id, issue, priority, channel) -> ticket_id
- get_customer_history(customer_id) -> conversation history
- escalate_to_human(ticket_id, reason, details) -> escalation record
- send_response(ticket_id, message, channel) -> delivery status

---

### 5) Skills Manifest (high-level)
- Knowledge Retrieval Skill — use on product questions
- Sentiment Analysis Skill — run on each message; outputs score + confidence
- Escalation Decision Skill — decide should_escalate(bool) + reason
- Channel Adaptation Skill — format response for channel
- Customer Identification Skill — unify identifiers (email/phone)

---

## Policies & Constraints
- ALWAYS create a ticket before issuing a response
- NEVER answer pricing questions — escalate to billing
- NEVER process refunds — escalate with reason 'refund_request'
- NEVER promise features not present in KB
- Respect per-channel length limits (Email: up to 500 words; WhatsApp: concise; Web: ~300 words)

---

## SLAs (example)
Starter:
- First response target: 12 hours
- Resolution target: 48 hours

Growth:
- First response target: 4 hours
- Resolution target: 24 hours

Enterprise:
- First response target: 1 hour
- Resolution target: 8 hours

---

## Known Limitations
- KB must contain ≥50 training examples for high-quality answers
- WhatsApp throughput limited by Twilio / Meta rate limits
- Real-time analytics update every ~5 minutes (not truly streaming)
