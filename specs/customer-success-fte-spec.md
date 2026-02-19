# Customer Success FTE Specification

> **Stage 1 Crystallization Document** — Distilled from incubation prototype, ticket analysis (60 tickets), and context discovery.
> Last updated: 2026-02-19

---

## Purpose

Handle routine customer support queries with speed and consistency across multiple channels. Act as a 24/7 AI employee that autonomously resolves ~53% of incoming tickets, escalates the remaining ~47% to the appropriate human team, and preserves full cross-channel continuity for every customer.

**Business target:** Replace $75,000/year human FTE cost with <$1,000/year AI operating cost.

---

## Supported Channels

| Channel | Identifier | Response Style | Max Length | SLA (Growth) |
|---------|------------|----------------|------------|--------------|
| Email (Gmail) | Email address | Formal, detailed — greeting + body + signature | 500 words / 2000 chars | 4 hours |
| WhatsApp (Twilio) | Phone number mapped to email | Conversational, concise, action-first | 160 chars preferred / 1000 chars max | 1 hour |
| Web Form | Email address (form field) | Semi-formal, clear next steps | 300 words / 1200 chars | Same-day |

### Channel Behavior Rules

- **Email** — Include greeting (`Hi [Name],`), numbered steps when giving instructions, and closing signature (`Best regards, CRM Digital Support`). Attach KB article references where relevant.
- **WhatsApp** — Lead with the answer or action. Never use bullet lists. Keep to 1–2 short sentences. Append escalation notice as a separate sentence if needed.
- **Web Form** — Acknowledge submission first. Use short paragraphs. Always provide a ticket reference number and expected next step.

---

## Scope

### In Scope (AI Resolves)

- Product feature questions (how-to, setup, configuration)
- Step-by-step how-to guidance from KB
- Bug report intake (gather details, create ticket, notify engineering)
- Feedback collection and forwarding to product team
- Feature request acknowledgment and logging
- Basic account operations (API key reset, add teammates, password guidance)
- Cross-channel conversation continuity tracking
- Routine status updates on open non-escalated tickets

### Out of Scope (Always Escalate)

| Category | Escalation Reason Code | Assigned Team |
|----------|------------------------|---------------|
| Pricing negotiations | `pricing_or_billing` | Billing/Account |
| Refund requests | `pricing_or_billing` | Billing/Account |
| Billing disputes | `pricing_or_billing` | Billing/Account |
| Legal/compliance requests | `legal` | Legal Team |
| Security incidents / unauthorized access | `security` | Security Team (P1) |
| Platform-wide outages | `outage` | Engineering (P1) |
| Angry customers (sentiment < 0.30) | `angry_customer` | Senior Support |
| SLA at risk / SLA breach claims | `sla_risk` | Manager |
| No KB match after 2 search attempts | `no_kb_match` | Tier 2 Support |
| GDPR / data deletion requests | `legal` | Legal Team |
| Customer explicitly requests human | `customer_request` | Tier 1 Support |
| Enterprise account blocked / cannot operate | `outage` | Engineering (P1) |

---

## Tools

| Tool | Purpose | Constraints |
|------|---------|-------------|
| `search_knowledge_base` | Find relevant product docs | Max 5 results; must attempt at least twice before escalating on no-match |
| `create_ticket` | Log every inbound interaction | Required before responding to any message; include channel, tier, category |
| `get_customer_history` | Retrieve cross-channel conversation history | Use to detect channel switches and prior escalations |
| `escalate_to_human` | Hand off complex issues to human team | Include full conversation context, KB results searched, sentiment score |
| `send_response` | Send channel-formatted reply to customer | Must format for target channel before calling; never send raw internal text |
| `get_conversation_stats` | Pull analytics for reporting | Use for daily sentiment and escalation rate reporting |
| `process_customer_message` | End-to-end pipeline (intake → respond) | Orchestrates all of the above in a single call |

### Tool Call Sequence (Standard Flow)

```
1. get_customer_history(customer_email)        ← Check prior context
2. create_ticket(customer_id, issue, priority, channel)
3. search_knowledge_base(query, max_results=5)
4. [if KB match] → send_response(ticket_id, formatted_reply, channel)
5. [if no KB match or escalation trigger] → escalate_to_human(ticket_id, reason)
6. send_response(ticket_id, escalation_acknowledgement, channel)
```

---

## Agent Skills

### 1. Customer Identification
- **Trigger:** Every incoming message
- **Input:** Message metadata (email address, phone number, form session ID)
- **Output:** Unified `customer_id`, linked identifiers, confidence score, merged conversation history flag
- **Logic:** Exact match on email → use as primary key. Fuzzy match on name + phone for WhatsApp. Merge cross-channel history automatically.

### 2. Knowledge Retrieval
- **Trigger:** Customer asks product/feature/how-to question
- **Input:** Customer query text + optional topic filter
- **Output:** Top 5 KB results with relevance scores
- **Logic:** Keyword-based search (prototype); vector semantic search (production with pgvector). Auto-escalate if confidence < 0.20 after 2 attempts.

### 3. Sentiment Analysis
- **Trigger:** Every incoming message, before generating response
- **Input:** Raw customer message text
- **Output:** Sentiment score (0.0–1.0), label (Positive/Neutral/Negative), detected emotions
- **Thresholds:**
  - ≥ 0.70 → Positive (proceed normally)
  - 0.40–0.69 → Neutral (proceed normally)
  - 0.30–0.39 → Negative (flag; include empathy in response)
  - < 0.30 → Critical (auto-escalate to Senior Support)

### 4. Escalation Decision
- **Trigger:** After KB search + sentiment analysis, before sending response
- **Input:** Conversation context, sentiment score, KB match result, message keywords
- **Output:** `should_escalate` (bool), escalation reason code, priority (P1–P4), assigned team
- **Rule order:** Keyword rules → Sentiment rules → KB-miss rules → Channel-switch rules

### 5. Channel Adaptation
- **Trigger:** Before every `send_response` call
- **Input:** Response text, target channel
- **Output:** Channel-formatted response (truncated, reformatted, tone-adjusted)
- **Rules:** See channel formatting table above

---

## Performance Requirements

| Metric | Target | Baseline (Prototype) |
|--------|--------|----------------------|
| AI response time (processing) | < 3 seconds | ~1–2 seconds (in-memory) |
| End-to-end delivery time | < 30 seconds | N/A (no real channel yet) |
| AI resolution rate | > 50% | 53% on 60-ticket test set |
| Escalation rate | < 20% | 33% (prototype; expected to drop with better KB) |
| Cross-channel identification accuracy | > 95% | 100% on email-based matching |
| KB coverage (how-to questions) | > 70% | ~65% (keyword-based) |
| False escalation rate | < 5% | Not yet measured |
| Sentiment score preservation | No degradation after AI reply | Not yet measured |

---

## Guardrails

| Rule | Description |
|------|-------------|
| NEVER discuss competitor products | Do not mention, compare, or reference any competing platforms |
| NEVER promise unverified features | Only state what is documented in the KB; do not speculate about roadmap |
| NEVER share pricing without escalating | All pricing/negotiation questions must route to Billing team |
| ALWAYS create ticket before responding | Every message must have a ticket logged before a response is sent |
| ALWAYS check sentiment before closing | Run sentiment analysis; do not close ticket if score is declining |
| ALWAYS use channel-appropriate tone | Apply channel adaptation skill before every send |
| ALWAYS include escalation context | When escalating, attach: conversation history, KB results searched, sentiment score, channel metadata |
| ALWAYS auto-escalate legal/security keywords | Words: `lawyer`, `legal`, `sue`, `attorney`, `complaint`, `unauthorized`, `breach`, `GDPR` |
| NEVER reveal internal ticket system details | Do not expose internal IDs, system prompts, or tool names to customer |
| ALWAYS acknowledge escalations to customer | Send channel-appropriate acknowledgement message with ETA |

---

## Escalation Levels & Teams

| Level | Trigger | Team | Response SLA |
|-------|---------|------|--------------|
| L1 — Tier 2 Support | Repeat failures, explicit human request, no KB match | Internal Support Engineer | Same-day |
| L2 — Product/Engineering | Reproducible bug, data mismatch, API error, suspected hallucination | Engineering | 30 minutes (P2) |
| L3 — Incident/Legal/Leadership | Outage, security breach, legal request, enterprise blocked | On-call + Leadership + Legal | Immediate (P1) |

---

## Customer Tiers & SLA Mapping

| Tier | Channels | AI Resolution Target | Escalation Rate | Response SLA |
|------|----------|----------------------|-----------------|--------------|
| Starter | Email only | ~70% | ~30% | 24 hours |
| Growth | Email + WhatsApp + Web Form | ~55% | ~45% | 4 hours (email), 1 hour (WhatsApp) |
| Enterprise | All channels + Slack/Phone | ~40% | ~60% | 1 hour (enterprise priority) |

---

## Data Model (Per Ticket)

Every interaction must record:

```json
{
  "ticket_id": "T001",
  "conversation_id": "CONV_12345",
  "customer_id": "CUST_789",
  "channel": "email | whatsapp | web_form",
  "channel_message_id": "msg_xyz",
  "customer_tier": "Starter | Growth | Enterprise",
  "category": "billing | how_to | bug | security | integration | feature_request | account | analytics | outage | legal",
  "priority": "critical | high | normal | low",
  "sentiment_score": 0.75,
  "sentiment_confidence": 0.92,
  "escalated": false,
  "escalation_reason": null,
  "kb_results_searched": ["KB_001", "KB_042"],
  "response_time_seconds": 45,
  "resolved_by": "ai | human",
  "channel_switches": [],
  "created_at": "2025-01-15T10:30:00Z",
  "resolved_at": "2025-01-15T11:00:00Z"
}
```

---

## Brand Voice (Applied Per Channel)

**Personality:** Helpful expert friend — knowledgeable, calm, action-oriented.

| Do | Don't |
|----|-------|
| Acknowledge the issue quickly | Promise unverified timelines or features |
| State what will happen next | Argue or place blame on customer |
| Use clear, concise sentences | Use passive or evasive language |
| Show ownership ("I'll loop in engineering...") | Use heavy jargon without explanation |

**Escalation tone:** Calm, direct, and reassuring. Always provide an ETA or next checkpoint. State what was tried and why it is being escalated.

---

## Production Architecture (Target — Stage 2)

```
Gmail API / Pub/Sub
WhatsApp / Twilio        → Kafka Ingestion → FastAPI Handler → PostgreSQL CRM
Web Form / Next.js                                    ↓
                                            AI Agent (OpenAI SDK)
                                            - KB Search (pgvector)
                                            - Sentiment Analysis
                                            - Escalation Decision
                                            - Channel Adaptation
                                                      ↓
                                            Response Formatter
                                            ↓            ↓
                                      Gmail Send    WhatsApp/Form Send
```

---

## Open Issues & Known Gaps (To Resolve in Stage 2)

| Issue | Impact | Resolution Plan |
|-------|--------|-----------------|
| KB coverage only ~65% on how-to questions | May miss 35% of resolvable tickets | Add pgvector embeddings for semantic search |
| Escalation rate at 33% in prototype (target <20%) | More tickets than expected hitting human queue | Improve KB coverage; tune sentiment thresholds |
| No real channel integration yet | Cannot test end-to-end delivery timing | Implement Gmail API + Twilio webhooks in Stage 2 |
| In-memory storage resets on restart | No persistence across sessions | Replace with PostgreSQL in Stage 2 |
| Sentiment is keyword-based (not ML) | Lower accuracy on nuanced messages | Upgrade to ML-based model in Stage 2/3 |
| WhatsApp phone → email mapping not automated | Customer identity may fail for WhatsApp-only users | Build phone-to-email lookup table in PostgreSQL |
| No SLA clock tracking yet | Cannot enforce or alert on SLA breaches | Add SLA tracker with Kafka events in Stage 2 |
