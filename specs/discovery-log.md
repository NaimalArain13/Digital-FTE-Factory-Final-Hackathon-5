# Discovery Log — Customer Success FTE Incubation

> **Stage 1: Incubation** — Requirements discovered during exploration, prototyping, and testing.
> Period: Incubation Phase (Hours 1–16)
> Last updated: 2026-02-19

---

## Overview

This log documents requirements discovered iteratively during the incubation phase — things not obvious from the initial brief that surfaced through hands-on exploration of the sample tickets, context files, and prototype builds. Each discovery is tagged with how it was found and what it changed about the design.

---

## Discovery #1 — Channel Choice Is a Proxy for Urgency

**Found during:** Initial ticket pattern analysis (`context/sample-tickets.json`, 60 tickets)

**Discovery:**
Customers do not choose channels randomly. Channel selection directly signals expected response time and complexity:
- **WhatsApp** → Real-time urgency, sub-1-hour expectation
- **Email** → Detailed issue, 4–12 hour tolerance
- **Web Form** → Structured report, same-day expectation

**Impact on design:**
- SLA clocks must be set per channel, not just per priority
- WhatsApp responses must be shorter and faster — not just a formatting preference
- Channel alone is a useful pre-triage signal before reading the message

**Files updated:** `specs/customer-success-fte-spec.md`, `context/escalation-rules.md`

---

## Discovery #2 — 47% of Tickets Require Unconditional Escalation

**Found during:** Categorizing all 60 tickets by type and escalation need

**Discovery:**
A large portion of inbound tickets (47%, or ~28/60) cannot be handled by the AI at all, regardless of KB coverage. These fall into hard-escalation categories:
- Billing/pricing/refunds → Always escalate (7 tickets)
- Security incidents → Always escalate (4 tickets)
- Legal/compliance → Always escalate (2 tickets)
- Platform outages (P1) → Always escalate (4+ tickets)
- SLA breach claims → Always escalate (2 tickets)
- No KB match after 2 tries → Escalate to Tier 2 (5 tickets)

**Impact on design:**
- Keyword-based auto-escalation triggers are non-negotiable guardrails, not optional
- The KPI target of "<20% escalation rate" applies to the remaining ~53% of resolvable tickets — overall raw escalation rate will be higher
- Escalation logic must run before response generation to avoid generating a potentially misleading AI answer first

**Files updated:** `specs/customer-success-fte-spec.md`, `.claude/skills/escalation-decision/`

---

## Discovery #3 — Email Is the Universal Customer Identifier

**Found during:** Building cross-channel identity matching in prototype

**Discovery:**
All three channels can be anchored to a customer's email address:
- Email channel: email is the sender directly
- Web Form: email captured in the form submission field
- WhatsApp: phone number must be mapped to email via a lookup table (built during intake)

**Impact on design:**
- Email address becomes the primary key for `customer_id` across all channels
- WhatsApp-only customers who have never emailed need special handling (create new profile on first contact; gather email in first reply)
- Cross-channel conversation history must be keyed on email, not on channel-native IDs

**Files updated:** `prototype/customer_agent_prototype.py`, `.claude/skills/customer-identification/`

---

## Discovery #4 — Channel Switching Is a Frustration Signal

**Found during:** Implementing cross-channel conversation memory in prototype

**Discovery:**
When a customer who started on WhatsApp sends a follow-up on Email (or vice versa), it almost always indicates:
1. They did not get a satisfactory response on the first channel, OR
2. They are escalating in urgency

In the prototype test (Mike's channel switch scenario), a WhatsApp billing query → Email follow-up within 10 minutes was immediately flagged as a signal requiring higher-priority attention.

**Impact on design:**
- `get_customer_history` must detect channel switches explicitly and surface them
- Channel switch = additional escalation consideration (even if individual message does not trigger other rules)
- `has_channel_switch: true` must be passed to escalation decision skill

**Files updated:** `prototype/MCP_IMPLEMENTATION_SUMMARY.md`, `.claude/skills/escalation-decision/`

---

## Discovery #5 — Enterprise Customers Have 60% Escalation Rate

**Found during:** Cross-tabulating customer tier against escalation categories

**Discovery:**
Ticket escalation rate is not uniform across tiers:

| Tier | Escalation Rate | AI Resolution Rate |
|------|-----------------|-------------------|
| Starter | ~30% | ~70% |
| Growth | ~45% | ~55% |
| Enterprise | ~60% | ~40% |

Enterprise customers disproportionately raise security, legal, SLA, and outage tickets. They also appear across all three channels (not just email), and expect faster responses.

**Impact on design:**
- Customer tier must be retrieved before processing any ticket — it affects both priority and escalation likelihood
- Enterprise tickets should default to higher priority even before content analysis
- Enterprise customers who hit escalation should be routed to a dedicated success manager, not generic Tier 2

**Files updated:** `specs/customer-success-fte-spec.md`, `specs/TICKET_ANALYSIS.md`

---

## Discovery #6 — WhatsApp Responses Must Be Radically Shorter

**Found during:** Iterating on response formatting during prototype builds

**Discovery:**
Initial responses generated for WhatsApp were 300–500 words — appropriate for email, but completely wrong for WhatsApp. Customer expectation on WhatsApp is:
- 1–3 short sentences maximum
- Answer or action comes first (not context-setting)
- No bullet lists or headers
- Preferred: < 300 characters (fits on one screen without scrolling)
- Hard limit: 1000 characters before Twilio truncates

**Impact on design:**
- Channel Adaptation skill must actively truncate and restructure responses, not just trim them
- The underlying answer generation can be full-length; the formatter is responsible for channel-appropriate output
- WhatsApp escalation notice must be its own short sentence, not embedded in a long paragraph

**Files updated:** `.claude/skills/channel-adaptation/`, `context/brand-voice.md`

---

## Discovery #7 — KB Coverage Gap Will Cause Over-Escalation

**Found during:** Running prototype against 60 sample tickets

**Discovery:**
The prototype's keyword-based KB search achieved ~65% coverage on how-to questions. The target is >70%. The gap means:
- ~5 additional tickets per 60 will hit "no KB match" and be escalated to Tier 2 unnecessarily
- At scale, this compounds into a significant human support load

The root cause is that keyword-based search misses synonym matches and paraphrased questions.

**Impact on design:**
- Production KB must use vector embeddings (pgvector) for semantic search
- KB articles should have multiple example queries to broaden matching surface
- "No KB match" should trigger a second attempt with a broader/reformulated query before escalating

**Files updated:** `specs/customer-success-fte-spec.md` (Open Issues section)

---

## Discovery #8 — Sentiment Scoring Must Influence Response Tone, Not Just Escalation

**Found during:** Testing response quality on negative-sentiment tickets

**Discovery:**
The initial escalation-decision skill only escalated if sentiment < 0.30. But tickets in the 0.30–0.40 range (e.g., T006 "suspect unauthorized access", T009 "cannot access platform") had clearly anxious or frustrated customers who would benefit from an empathy-first response even if not escalated.

**Impact on design:**
- Sentiment thresholds must be tiered:
  - < 0.30 → Auto-escalate
  - 0.30–0.39 → Stay with AI but prepend empathy acknowledgement to response
  - 0.40–0.69 → Normal response
  - ≥ 0.70 → Positive; can be briefer
- Sentiment should also influence closing — do not close ticket with a curt one-liner if customer sentiment is borderline

**Files updated:** `.claude/skills/sentiment-analysis/`, `specs/customer-success-fte-spec.md`

---

## Discovery #9 — Ticket Must Be Created Before Response Is Generated

**Found during:** Designing the tool call sequence in the MCP server

**Discovery:**
The original prototype generated a response before creating a ticket. This created two problems:
1. If the response triggered an error, no audit trail existed
2. Escalation decisions are better made with the ticket ID already assigned (traceability)

**Impact on design:**
- Canonical tool call order: `create_ticket` → `search_knowledge_base` → `[escalate_to_human | send_response]`
- Ticket creation is a hard prerequisite, not an optional step
- Ticket ID must be included in the escalation payload

**Files updated:** `prototype/mcp_server.py`, `specs/customer-success-fte-spec.md`

---

## Discovery #10 — Legal Keywords Must Trigger Immediate Escalation Without KB Search

**Found during:** Reviewing edge tickets (T023 "legal team needs data export", T049 "counsel requests")

**Discovery:**
Legal escalation triggers (lawyer, legal, sue, attorney, complaint, GDPR, discovery request, counsel) must bypass the normal KB search flow entirely. Attempting a KB search first:
- Wastes time on a ticket that will always escalate
- Risks generating an AI response to a legal query before a human can intervene
- Could create liability if an incorrect answer is sent

**Impact on design:**
- Escalation keyword check must run immediately after ticket creation, before KB search
- Legal escalations must be flagged P1 regardless of message tone
- No AI-generated response body should be sent for legal category; only a templated "escalating to our team" acknowledgement

**Files updated:** `.claude/skills/escalation-decision/`, `context/escalation-rules.md`

---

## Discovery #11 — MCP Tool Descriptions Are Part of Agent Quality

**Found during:** Building and testing the 7 MCP tools

**Discovery:**
The quality of the tool's docstring/description directly affects how accurately the AI agent calls the tool. Vague descriptions led to incorrect parameter usage. Well-written tool descriptions (with explicit when-to-use guidance, parameter constraints, and example output formats) led to correct, consistent tool calls.

**Impact on design:**
- Every MCP tool must have a detailed docstring explaining: purpose, when to use it, parameter expectations, return format
- This transfers directly to production OpenAI Agents SDK `@function_tool` definitions

**Files updated:** `prototype/mcp_server.py`, `prototype/MCP_IMPLEMENTATION_SUMMARY.md`

---

## Discovery #12 — In-Memory State Does Not Survive Agent Restarts

**Found during:** Running multi-session tests on the prototype

**Discovery:**
All conversation history, tickets, and escalations stored in Python dicts are lost on server restart. This means:
- A customer who sends a WhatsApp message, then emails 2 hours later, will not be recognized as the same customer if the server restarted in between
- Cross-channel identity matching fails silently without any error

**Impact on design:**
- Production requires persistent storage (PostgreSQL) from Day 1 of Stage 2
- In-memory storage is acceptable for incubation/prototype only
- Database schema must be designed before any production code is written

**Files updated:** `specs/customer-success-fte-spec.md` (Open Issues), `prototype/MCP_IMPLEMENTATION_SUMMARY.md`

---

## Discovered Requirements Summary

| # | Requirement | Priority | Source Discovery |
|---|-------------|----------|-----------------|
| R1 | Per-channel SLA clocks | High | Discovery #1 |
| R2 | Hard-escalation keyword list (billing, legal, security) | Critical | Discovery #2 |
| R3 | Email as universal customer primary key | High | Discovery #3 |
| R4 | Channel-switch detection as frustration signal | Medium | Discovery #4 |
| R5 | Customer tier retrieval before processing | High | Discovery #5 |
| R6 | WhatsApp character limit enforcement (<300 chars preferred) | High | Discovery #6 |
| R7 | Vector/semantic KB search for production | High | Discovery #7 |
| R8 | Tiered sentiment response (empathy at 0.30–0.39, not just escalation) | Medium | Discovery #8 |
| R9 | Ticket creation as mandatory first step | Critical | Discovery #9 |
| R10 | Legal keyword bypass (no KB search, immediate P1 escalation) | Critical | Discovery #10 |
| R11 | Rich MCP tool docstrings for agent accuracy | Medium | Discovery #11 |
| R12 | PostgreSQL persistence from Stage 2 Day 1 | High | Discovery #12 |

---

## Working System Prompt (Extracted from Prototype)

The following system prompt produced the best results during incubation testing:

```
You are a Customer Success AI for CRM Digital — a B2B SaaS company.

Your job is to handle customer inquiries from three channels: Email (Gmail), WhatsApp, and Web Form.

For every incoming message, follow this sequence:
1. Retrieve customer history (check for prior conversations and channel switches)
2. Create a ticket (always do this first, before anything else)
3. Analyze sentiment (score 0.0–1.0; escalate if < 0.30)
4. Check for escalation keywords (billing, legal, security, outage — escalate immediately if present)
5. Search the knowledge base (2 attempts maximum)
6. Generate a response appropriate for the channel
7. Send the response

Tone rules:
- Email: formal, greeting + body + signature, detailed steps
- WhatsApp: 1–2 short sentences, action-first, max 300 chars preferred
- Web Form: semi-formal, clear next step, include ticket reference

Never:
- Discuss competitor products
- Promise features not in the KB
- Send a response to a legal/billing/security query without escalating first
- Skip ticket creation
```

---

## Edge Cases Found During Incubation

| Edge Case | How Handled | Production Test Needed |
|-----------|-------------|------------------------|
| Empty message body | Return "We received your message but it appears empty. Could you describe your issue?" | Yes |
| Customer sends same message on 2 channels simultaneously | Deduplicate by customer_email + message hash + 5-min window | Yes |
| WhatsApp phone number not in system | Create new profile, ask for email in first reply | Yes |
| Customer says "I already emailed you about this" but no prior email found | Acknowledge, ask for previous ticket reference, create new ticket | Yes |
| KB returns results but none are relevant (low confidence) | Attempt second search with reformulated query; if still low → escalate | Yes |
| Message contains both a how-to question AND a billing question | Split into two: answer the how-to, escalate the billing portion | Yes |
| Enterprise customer on WhatsApp (not typical) | Apply Enterprise SLA regardless of channel | Yes |
| Sentiment drops from Positive to Negative across two turns | Proactive escalation flag even if current message doesn't trigger keyword rules | Yes |
| Customer uses profanity but query is legitimate | Escalate (sentiment threshold), not refuse to serve | Yes |
| Legal keyword appears in a benign context ("legally required documentation") | Still escalate — legal team determines if it's a real legal risk | Yes |

---

## Performance Baseline (From Prototype Tests)

| Metric | Prototype Result | Production Target |
|--------|-----------------|-------------------|
| Average response time | ~1–2 seconds (in-memory) | < 3 seconds |
| AI resolution rate | 53% (32/60 tickets) | > 50% |
| Escalation rate | 33% (prototype) | < 20% (with better KB) |
| Cross-channel ID accuracy | 100% (email-based) | > 95% |
| Channel switch detection | 100% on test set | > 95% |
| Sentiment analysis accuracy | ~80% (keyword-based) | > 90% (ML-based) |

---

## Next Step: Stage 2 Transition

All discoveries above feed directly into the Stage 2 production build. The highest-risk items to address first:

1. **PostgreSQL schema** — Persistent storage is a blocker for everything else
2. **pgvector KB search** — Required to hit the 70% KB coverage target
3. **Gmail + Twilio webhooks** — Real channel integration for end-to-end testing
4. **SLA clock** — Cannot enforce SLA without a timer per ticket
5. **ML-based sentiment** — Keyword approach is too brittle for production volume
