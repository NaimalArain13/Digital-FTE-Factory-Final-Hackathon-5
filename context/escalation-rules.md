# Escalation Rules — CRM Digital

## Philosophy
Escalate when the issue cannot be resolved confidently by the AI, when customer impact is high, when security/compliance/billing/legal risk exists, or when SLA is at risk.

## Escalation Levels

### Level 1 — Tier 2 Support (internal support engineer)
**When:** Troubleshooting needs deeper logs, repeat failures, integration/user settings issues, or customer explicitly requests human help.  
**Target response:** Acknowledge and provide ETA for human takeover. Provide context and reproduce steps.

### Level 2 — Product / Engineering
**When:** Reproducible bug, data mismatch, feature regression, API errors, or suspected model hallucination.  
**Action:** Create detailed bug ticket with logs, KB search attempts, and example messages.

### Level 3 — Incident / Leadership / Legal
**When:** Platform-wide outage, suspected security breach, sensitive legal/compliance request, enterprise account blocked, or public reputation risk.  
**Action:** Trigger incident playbook, page on-call engineers, notify leadership.

---

## Automatic Escalation Triggers
- **Pricing/Contracts/Refunds** — escalate immediately to Billing/Account team with reason `pricing_or_billing`.
- **Legal words** — presence of words like `lawyer`, `legal`, `sue`, `attorney`, `complaint` → escalate immediately.
- **Profanity / Aggressive/Angry tone** — sentiment < 0.30 → escalate or hand to human depending on severity.
- **Security or unauthorized access** — any language suggesting data leak or unauthorized login → escalate to Security.
- **SLA at risk** — if projected resolution exceeds SLA or response time exceeded → escalate to manager.
- **No KB match** — after 2 search attempts with no useful content → escalate with `no_kb_match`.

---

## Severity (example mapping)
- **P1 (Critical)** — Platform down / data loss / enterprise unable to operate → Immediate Level 3
- **P2 (High)** — Major feature broken for multiple customers → Level 2 (within 30 minutes)
- **P3 (Medium)** — Single-customer issue or non-critical bug → Level 1 (same day)
- **P4 (Low)** — Feature requests, low-impact questions → No escalation (document as feature request)

---

## Escalation Flow & Communication
1. **Log ticket** with full context (conversation, KB snippets searched, tool-call history).  
2. **Notify human team** with an escalation summary (subject, priority, customer impact, steps to reproduce).  
3. **Auto-update customer**: send acknowledgement and expected ETA (channel-appropriate).  
4. **Follow-up cadence**: update every X hours (Enterprise) or every 24 hours (lower tiers) until resolution.

---

## Escalation Metadata (fields to include)
- escalation_id
- ticket_id
- reason (short code: pricing, security, legal, no_kb_match, angry_customer)
- severity (P1..P4)
- assigned_team
- notes (links to logs, KB results, attachments)
- timestamp

---

## KPIs
- Mean time to escalate
- Escalation rate (goal < 20%)
- Escalation resolution SLA
