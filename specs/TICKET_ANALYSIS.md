# Customer Success AI Agent — Ticket Analysis & Patterns

## Executive Summary
Analyzed 60 sample tickets across 3 channels (Email, WhatsApp, Web Form) to identify patterns, escalation triggers, and system requirements for the Customer Success FTE.

---

## Channel Distribution

| Channel   | Count | Percentage | Characteristics |
|-----------|-------|------------|-----------------|
| Email     | 24    | 40%        | More formal, detailed issues, billing/legal/security |
| WhatsApp  | 18    | 30%        | Concise queries, how-to questions, real-time urgency |
| Web Form  | 18    | 30%        | Mixed formality, feature requests, bug reports |

### Channel-Specific Insights

**Email (40%)**
- **Primary use cases**: Billing, legal, security, SLA concerns, outages
- **Tone**: Formal, detailed problem descriptions
- **Customer expectation**: Thorough responses with next steps
- **Average complexity**: Higher (integration issues, security incidents)
- **Response format**: Structured with greeting, body, signature

**WhatsApp (30%)**
- **Primary use cases**: Quick how-to questions, urgent bugs, setup help
- **Tone**: Casual, conversational, impatient
- **Customer expectation**: Fast, concise answers
- **Average complexity**: Lower to medium (configuration, training)
- **Response format**: Short messages (<300 chars), actionable

**Web Form (30%)**
- **Primary use cases**: Feature requests, feedback, bug reports, account management
- **Tone**: Semi-formal, structured
- **Customer expectation**: Clear acknowledgment and resolution timeline
- **Average complexity**: Medium
- **Response format**: Professional but concise (300 words max)

---

## Category Breakdown (60 tickets)

| Category          | Count | % of Total | Escalation Required? |
|-------------------|-------|------------|----------------------|
| How-to            | 13    | 21.7%      | ❌ No (KB lookup)     |
| Bug               | 11    | 18.3%      | ⚠️ Medium-High         |
| Billing           | 7     | 11.7%      | ✅ **Always**          |
| Integration       | 5     | 8.3%       | ⚠️ Medium              |
| Security          | 4     | 6.7%       | ✅ **Always**          |
| Feature Request   | 5     | 8.3%       | ❌ No (document only)  |
| Account           | 5     | 8.3%       | ⚠️ Sometimes           |
| Analytics         | 4     | 6.7%       | ⚠️ Sometimes           |
| Outage/Incident   | 4     | 6.7%       | ✅ **Always (P1)**     |
| Legal             | 2     | 3.3%       | ✅ **Always**          |

---

## Priority Distribution

| Priority | Count | % of Total | Expected SLA (Growth) |
|----------|-------|------------|-----------------------|
| Critical | 10    | 16.7%      | 1 hour (Enterprise)   |
| High     | 17    | 28.3%      | 4 hours               |
| Normal   | 24    | 40.0%      | 12 hours              |
| Low      | 9     | 15.0%      | 24-48 hours           |

**Critical tickets require immediate escalation** (see escalation patterns below).

---

## Escalation Pattern Analysis

### Auto-Escalate Triggers Found (28 tickets = 46.7%)

| Trigger Type              | Count | Example Ticket IDs |
|---------------------------|-------|--------------------|
| **Billing/Pricing**       | 7     | T001, T011, T020, T032, T039, T050 |
| **Security**              | 4     | T006, T027, T045 (DPA compliance) |
| **Legal/Compliance**      | 2     | T023, T049 |
| **Outage/Incident (P1)**  | 4     | T009, T018, T030, T035, T056 |
| **SLA Risk**              | 2     | T013, T053 |
| **No KB Match (likely)**  | 5     | Integration bugs: T004, T015, T036 |
| **Account Deletion**      | 1     | T014 (GDPR-sensitive) |
| **Refund Request**        | 1     | T050 |

### AI Can Resolve (32 tickets = 53.3%)

| Category              | Count | Resolution Method |
|-----------------------|-------|-------------------|
| **How-to questions**  | 13    | KB search → step-by-step guide |
| **Feature requests**  | 5     | Acknowledge + log for product team |
| **Low-priority bugs** | 6     | Gather details → create ticket → notify engineering |
| **Feedback**          | 2     | Thank + forward to product |
| **Simple account ops**| 6     | KB lookup (API key reset, add teammates, etc.) |

---

## Cross-Channel Patterns

### 1. **Channel Choice Indicates Urgency**
- **WhatsApp** → Customers expect sub-1-hour response (real-time)
- **Email** → Customers accept 4-12 hour response
- **Web Form** → Customers expect same-day response

### 2. **Enterprise Customers Across All Channels**
- Enterprise tickets appear in all 3 channels
- Higher priority and stricter SLAs
- More frequent security/legal/compliance requests
- Expectation: dedicated human support (but AI can triage)

### 3. **Starter vs Growth vs Enterprise**

| Tier       | Common Issues | Escalation Rate (est.) | AI Resolution Rate |
|------------|---------------|------------------------|--------------------|
| Starter    | How-to, setup, basic billing | ~30% | ~70% |
| Growth     | Integrations, analytics, bugs | ~45% | ~55% |
| Enterprise | Security, legal, SLA, outages | ~60% | ~40% |

### 4. **Repeat Issue Categories by Channel**

**Email-dominant issues:**
- Billing disputes (T001, T011, T020, T039, T050)
- Security incidents (T006, T027, T045)
- Legal/compliance (T023, T049)

**WhatsApp-dominant issues:**
- Quick how-to (T002, T005, T008, T022, T025)
- Urgent bugs with immediate impact (T012, T029, T046)

**Web Form-dominant issues:**
- Feature requests (T010, T026, T048, T060)
- Feedback (T034, T057)
- Non-urgent bugs (T007, T024, T040, T051)

---

## Sentiment & Escalation Signals

### High-Risk Keywords Detected (require sentiment analysis)

| Ticket | Channel | Keywords/Signals | Recommended Action |
|--------|---------|------------------|-------------------|
| T013   | Email   | "SLA concern" | Auto-escalate to manager |
| T023   | Email   | "legal team", "discovery request" | Auto-escalate to legal |
| T035   | WhatsApp| "reputation risk" | Auto-escalate to leadership |
| T049   | WhatsApp| "counsel requests" | Auto-escalate to legal |
| T050   | Email   | "refund request" | Auto-escalate to billing |
| T053   | Email   | "SLA breach" | Auto-escalate to manager |

### Likely Negative Sentiment (contextual clues)

- T006: "suspect unauthorized access" → anxiety
- T009: "cannot access platform" → frustration
- T016: "incorrect product details (hallucination)" → trust issue
- T050: "didn't work as advertised" → dissatisfaction

**Action**: Run sentiment analysis; if score < 0.30 → flag for human review.

---

## AI Agent Skill Requirements

Based on ticket patterns, the AI needs these **core skills**:

### 1. **Knowledge Retrieval** (for 53% of tickets)
- Vector search on KB for how-to, setup, configuration questions
- Fallback to keyword match if semantic search fails
- Return top 5 results with relevance scores

### 2. **Escalation Decision** (for 47% of tickets)
- Rule-based triggers: billing, legal, security, SLA, outage
- Sentiment-based triggers: angry tone, low confidence score
- No KB match after 2 attempts → escalate

### 3. **Channel Adaptation**
- Email: formal tone, greeting + signature, detailed steps
- WhatsApp: concise (<300 chars), friendly, action-first
- Web Form: semi-formal, clear next steps

### 4. **Customer Context Retrieval**
- Lookup customer tier (Starter/Growth/Enterprise)
- Retrieve conversation history across channels
- Identify repeat issues or escalation patterns

### 5. **Ticket Creation & Routing**
- Auto-create ticket on every inbound message
- Tag with: channel, category, priority, customer_tier
- Route to correct team: support, engineering, billing, legal

### 6. **Sentiment Analysis**
- Analyze each message for sentiment score
- Flag scores < 0.30 for human review
- Detect legal/aggressive keywords

---

## Recommended System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    INGESTION LAYER                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  Gmail   │  │ WhatsApp │  │ Web Form │                 │
│  │  Webhook │  │  Twilio  │  │ Next.js  │                 │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                 │
└───────┼─────────────┼─────────────┼────────────────────────┘
        │             │             │
        └─────────────┼─────────────┘
                      ▼
        ┌─────────────────────────────┐
        │   FastAPI Message Handler   │
        │  - Normalize message format │
        │  - Extract customer info    │
        │  - Add channel metadata     │
        └──────────────┬──────────────┘
                       │
                       ▼
        ┌─────────────────────────────┐
        │   PostgreSQL CRM/Ticketing  │
        │  - customers                │
        │  - conversations (unified)  │
        │  - messages (with channel)  │
        │  - tickets                  │
        │  - knowledge_base (pgvector)│
        └──────────────┬──────────────┘
                       │
                       ▼
        ┌─────────────────────────────┐
        │    AI Agent Orchestrator    │
        │  - OpenAI Agents SDK        │
        │  - Tool calling (MCP)       │
        │  - Sentiment analysis       │
        │  - Escalation logic         │
        └──────────────┬──────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌───────────────┐           ┌──────────────────┐
│  KB Search    │           │  Escalation Flow │
│  (pgvector)   │           │  - Create ticket │
│               │           │  - Notify team   │
└───────┬───────┘           │  - Update customer│
        │                   └──────────┬────────┘
        │                              │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌─────────────────────────────┐
        │   Response Formatter        │
        │  - Apply brand voice        │
        │  - Channel-specific format  │
        └──────────────┬──────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
  ┌──────────┐              ┌──────────────────┐
  │  Gmail   │              │  WhatsApp/Form   │
  │  Sender  │              │  Sender          │
  └──────────┘              └──────────────────┘
```

---

## Key Metadata Fields to Track

Every message/ticket should store:

```json
{
  "ticket_id": "T001",
  "conversation_id": "CONV_12345",
  "customer_id": "CUST_789",
  "channel": "email | whatsapp | web_form",
  "channel_message_id": "msg_xyz",
  "customer_tier": "Starter | Growth | Enterprise",
  "category": "billing | how_to | bug | security | ...",
  "priority": "critical | high | normal | low",
  "sentiment_score": 0.75,
  "sentiment_confidence": 0.92,
  "escalated": false,
  "escalation_reason": null,
  "kb_results": ["KB_001", "KB_042"],
  "response_time_seconds": 45,
  "resolved_by": "ai | human",
  "created_at": "2025-01-15T10:30:00Z",
  "resolved_at": "2025-01-15T11:00:00Z"
}
```

---

## Next Steps: Implementation Roadmap

### Phase 1: Foundation (Week 1)
1. ✅ Design database schema (customers, conversations, messages, tickets, kb)
2. ✅ Set up FastAPI ingestion endpoints for 3 channels
3. ✅ Implement channel normalization layer
4. ✅ Create basic ticket creation flow

### Phase 2: AI Agent (Week 2)
1. ✅ Set up OpenAI Agents SDK or custom agent loop
2. ✅ Implement KB search tool (pgvector semantic search)
3. ✅ Build escalation decision logic (rule-based)
4. ✅ Add sentiment analysis (OpenAI or local model)

### Phase 3: Channel Integration (Week 3)
1. ✅ Gmail API integration (inbound/outbound)
2. ✅ Twilio WhatsApp webhook + sender
3. ✅ Web form component + API
4. ✅ Response formatter per channel

### Phase 4: Testing & Refinement (Week 4)
1. ✅ Test with sample tickets (all 60)
2. ✅ Measure escalation rate (target <20%)
3. ✅ Validate SLA adherence
4. ✅ Add analytics dashboard

---

## Success Metrics

| Metric | Target |
|--------|--------|
| AI resolution rate | >50% |
| Escalation rate | <20% |
| First response time (Growth) | <4 hours |
| Sentiment preservation | No degradation after AI reply |
| False escalations | <5% |
| KB coverage | Answer ≥70% of how-to questions |

---

## Risk Areas & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **AI hallucination** | High | Always cite KB sources; escalate if low confidence |
| **Cross-channel identity mismatch** | Medium | Fuzzy matching on email/phone; manual linking UI |
| **WhatsApp rate limits** | Medium | Queue + throttle; fallback to email |
| **Legal/GDPR missteps** | Critical | Auto-escalate all legal keywords |
| **Sentiment misreads** | Medium | Human-in-loop for borderline scores |

---

## Conclusion

The 60-ticket analysis reveals:
- **47% of tickets require escalation** (billing, security, legal, outages)
- **53% can be handled by AI** with proper KB coverage
- **Channel choice correlates with urgency and formality**
- **Enterprise customers have higher escalation needs but appear across all channels**

**Recommendation**: Build a hybrid AI+human system where:
1. AI handles routine how-to and low-risk tickets
2. Auto-escalation triggers protect against legal/billing/security risks
3. Cross-channel continuity is preserved via unified conversation model
4. Metadata-rich tracking enables continuous improvement

This system can reduce support load by ~50% while maintaining quality and safety.
