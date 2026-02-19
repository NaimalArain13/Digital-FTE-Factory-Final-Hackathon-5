# Edge Cases — Customer Success FTE

> **Stage 1 Deliverable** — 20+ edge cases per channel (Email, WhatsApp, Web Form).
> These cases cover boundary conditions, error paths, unusual customer behaviors, and escalation edge cases discovered during incubation.
> Last updated: 2026-02-19

---

## How to Use This Document

Each edge case includes:
- **EC-ID**: Unique identifier for reference in test code
- **Scenario**: What the customer does or what state the system is in
- **Expected Behavior**: What the agent should do
- **Escalate?**: Whether this triggers human escalation
- **Test Status**: Whether an automated test exists

---

## Email Channel Edge Cases (EC-E001 – EC-E022)

| ID | Scenario | Expected Behavior | Escalate? | Test Status |
|----|----------|-------------------|-----------|-------------|
| EC-E001 | Customer sends blank email with only a subject line (no body) | Reply asking customer to describe their issue; create ticket with category=unclear | No | Needed |
| EC-E002 | Customer sends email with only an image attachment (no text body) | Acknowledge receipt; inform that image-only emails cannot be processed automatically; ask for text description | No | Needed |
| EC-E003 | Customer sends duplicate email within 5 minutes (same body, same sender) | Deduplicate: do not create a second ticket; acknowledge first ticket only | No | Needed |
| EC-E004 | Customer replies to an existing closed ticket thread | Reopen ticket or create linked new ticket; retrieve prior context before responding | No | Needed |
| EC-E005 | Customer emails from a different address than their registered account email | Cannot match customer_id; ask for their registered email address; create unlinked ticket in the meantime | No | Needed |
| EC-E006 | Email contains the word "legal" in a clearly benign context ("We need the legally required documentation for our audit") | Still escalate to legal team — legal team determines if it is an actual legal risk; AI must not make this judgement | Yes — Legal | Needed |
| EC-E007 | Email contains a billing question AND a how-to question in the same message | Split handling: answer the how-to portion from KB, escalate the billing portion; communicate both actions in the response | Yes — Billing | Needed |
| EC-E008 | Email is written in a language other than English (e.g., Spanish, French) | Respond in the customer's language if possible; if not, respond in English with an apology note; create ticket with language tag | No | Needed |
| EC-E009 | Customer explicitly says "I want to speak to a human" in the email | Immediately escalate to Tier 1 Support with reason `customer_request`; acknowledge in reply with ETA | Yes — Customer Request | Needed |
| EC-E010 | Customer's email sentiment is Positive overall, but contains the word "disappointed" once | Do not escalate solely on the word; use the overall sentiment score; if score ≥ 0.40 proceed with AI response that acknowledges the concern | No (unless score < 0.40) | Needed |
| EC-E011 | Customer sends an email with extremely long body (>5000 words) | Truncate for processing but do not lose key details; extract main issue from first 500 words + conclusion; create ticket | No | Needed |
| EC-E012 | Enterprise customer emails with a P1 outage report at 3 AM | Trigger P1 escalation immediately regardless of time; page on-call engineering; send acknowledgement within 5 minutes | Yes — Outage P1 | Needed |
| EC-E013 | Customer's email domain matches a known Enterprise account but the email itself is not in the customer database | Treat as a new Enterprise contact under the same org; create profile linked to org domain; flag for account manager | No (but flag) | Needed |
| EC-E014 | Repeat customer who has already been escalated 3+ times on the same issue in the past 7 days | Detect escalation pattern from history; route directly to senior support without KB search attempt | Yes — Repeat Escalation | Needed |
| EC-E015 | Customer sends an email with an attachment (.pdf contract) and asks the agent to "review it" | Do not process attachments beyond metadata; reply that document review requires human handling; escalate | Yes — Legal/Human | Needed |
| EC-E016 | Customer's sentiment drops from Positive (turn 1) to Negative (turn 3) in an email thread | Proactive escalation on the third turn even if no keyword trigger exists; sentiment trend = escalation signal | Yes — Sentiment Trend | Needed |
| EC-E017 | Customer asks about pricing for upgrading from Starter to Growth | Escalate to Billing/Account team immediately; do not provide pricing from any source; acknowledge and give ETA | Yes — Billing | Needed |
| EC-E018 | Customer sends an automated out-of-office reply to an agent response | Detect OOO pattern (keywords: "out of office", "automatic reply", "away"); do not create a new ticket; mark existing ticket as awaiting customer | No (suppress) | Needed |
| EC-E019 | KB search returns 5 results, all with relevance score below 0.20 | Do not send low-confidence KB content; attempt second search with reformulated query; if still < 0.20 → escalate with reason `no_kb_match` | Yes — No KB Match | Needed |
| EC-E020 | Customer's email is flagged as spam or suspicious by the email provider | Log to system as a suspicious message; do not process or respond; alert admin | No (suppress) | Needed |
| EC-E021 | Customer asks the agent to delete all their data ("GDPR right to erasure") | Escalate immediately to Legal team with reason `legal`; acknowledge to customer that the request has been logged | Yes — Legal/GDPR | Needed |
| EC-E022 | Customer CC's multiple people on the email (e.g., their own team + CRM Digital) | Respond only to the sender (From address); do not reply-all; note in ticket that there are CC recipients | No | Needed |

---

## WhatsApp Channel Edge Cases (EC-W001 – EC-W022)

| ID | Scenario | Expected Behavior | Escalate? | Test Status |
|----|----------|-------------------|-----------|-------------|
| EC-W001 | Customer's WhatsApp phone number is not linked to any email in the system | Create new contact profile; ask for email address in first reply to enable cross-channel tracking | No | Needed |
| EC-W002 | Customer sends a voice note (audio message) instead of text | Reply that voice notes cannot be processed automatically; ask them to type their question; create placeholder ticket | No | Needed |
| EC-W003 | Customer sends a photo of an error screen (image, no text) | Acknowledge receipt of image; cannot read images automatically; ask customer to describe the error in text | No | Needed |
| EC-W004 | Customer sends a very long message (>500 characters) for WhatsApp | Process the full message; respond in WhatsApp-appropriate short format (<300 chars); do not truncate the customer's input | No | Needed |
| EC-W005 | Customer sends only an emoji (e.g., "👍" or "❓") | Respond asking them to describe their issue; do not create a support ticket until a real issue is described | No | Needed |
| EC-W006 | Customer sends a message at 2 AM in their timezone | Respond immediately (24/7 system); do not add time-zone delays; use WhatsApp short format | No | Needed |
| EC-W007 | Twilio webhook fires twice for the same message (duplicate webhook delivery) | Deduplicate on message ID; process only once; log duplicate detection | No | Needed |
| EC-W008 | Customer says "forget what I said, new question:" mid-conversation | Treat new question as a new context; retain conversation history but do not carry over unresolved issue from prior turn unless customer references it | No | Needed |
| EC-W009 | Customer switches from WhatsApp to Email within the same hour | Detect channel switch; surface as frustration signal; elevate priority; carry full WhatsApp context into email processing | Conditional — if billing/legal present | Needed |
| EC-W010 | Customer sends a WhatsApp message but their account has been suspended | Check account status before responding; inform customer their account is on hold; escalate to Account team | Yes — Account | Needed |
| EC-W011 | Customer asks a question that requires a step-by-step guide (5+ steps) | Condense to max 3 steps for WhatsApp; offer to send full instructions via email; log intent to email | No | Needed |
| EC-W012 | Customer's message contains profanity directed at the company | Escalate to Senior Support with reason `angry_customer`; do not argue; reply calmly with escalation notice in WhatsApp format | Yes — Angry Customer | Needed |
| EC-W013 | WhatsApp rate limit hit (Twilio returns 429 Too Many Requests) | Queue the message; retry after rate-limit window; do not lose the message; notify customer when processed | No (technical) | Needed |
| EC-W014 | Customer sends the same message 5 times in a row rapidly | Detect spam pattern; respond once; do not create 5 tickets; log the burst behavior | No | Needed |
| EC-W015 | Customer's message is only "help" or "?" | Reply with a short list of what the agent can assist with (3 bullet points max for WhatsApp); ask what they need | No | Needed |
| EC-W016 | Customer mentions they are having the same problem as "another user they know" | Do not cross-reference or discuss other customers' data; treat this as a standard support query from this customer | No | Needed |
| EC-W017 | Customer asks for the agent's name ("are you a bot?") | Be transparent: confirm it is an AI agent; do not pretend to be human; offer escalation to human if needed | No | Needed |
| EC-W018 | Customer sends a WhatsApp message in response to a delivery notification (not a support query) | Classify as non-support message; do not create a support ticket; respond with appropriate acknowledgement | No | Needed |
| EC-W019 | Customer's sentiment progressively declines across 3 WhatsApp turns | On third turn, trigger proactive escalation even if no keyword rule fires; cite sentiment trend as reason | Yes — Sentiment Trend | Needed |
| EC-W020 | Enterprise customer contacts via WhatsApp (not the expected email channel) | Apply Enterprise SLA (1-hour response target) regardless of channel; route to Enterprise support queue | No (but elevated priority) | Needed |
| EC-W021 | Customer is in the middle of a WhatsApp conversation and the session times out on Twilio | On reconnect, retrieve prior conversation history by phone number; resume context; do not treat as new customer | No | Needed |
| EC-W022 | Customer asks for a refund via WhatsApp | Escalate immediately to Billing; WhatsApp response: "I'm connecting you with our billing team — they'll reply within 4 hrs." | Yes — Billing | Needed |

---

## Web Form Channel Edge Cases (EC-F001 – EC-F022)

| ID | Scenario | Expected Behavior | Escalate? | Test Status |
|----|----------|-------------------|-----------|-------------|
| EC-F001 | Form submitted with all required fields empty (no validation on front-end) | Return validation error before creating ticket; prompt customer to fill in required fields | No | Needed |
| EC-F002 | Customer submits the same form twice within 2 minutes (double-click or page reload) | Deduplicate on email + message hash + time window; confirm first submission only; do not create duplicate ticket | No | Needed |
| EC-F003 | Customer submits a form with a fake/invalid email address (no @ or no domain) | Validate email format before creating ticket; return error asking for valid email | No | Needed |
| EC-F004 | Form submission includes a file upload (e.g., screenshot) | Acknowledge file receipt; store reference in ticket; note that human review needed for attachments; do not process image content | No (attach flag) | Needed |
| EC-F005 | Customer uses the web form to report a bug but provides no steps to reproduce | Respond with a structured follow-up asking for: steps to reproduce, browser/OS, frequency; create ticket as `bug - needs info` | No | Needed |
| EC-F006 | Customer submits a feature request via the web form | Acknowledge the request; log as `feature_request` category; forward to product team; do not promise delivery timeline | No | Needed |
| EC-F007 | Customer submits a form but their account email is different from the form email | Cannot auto-link; ask for their account email; create unlinked ticket; flag for manual merging | No | Needed |
| EC-F008 | Customer's form message is written entirely in UPPERCASE | Normalize casing for processing; respond in normal mixed case; do not mirror the aggressive formatting | No | Needed |
| EC-F009 | Customer submits a very short message ("it doesn't work") with no additional context | Reply asking for more details: what feature, what error message, what they expected; create ticket as `unclear` | No | Needed |
| EC-F010 | Customer submits a form outside business hours on Starter plan (Starter = 24/5, not 24/7) | Auto-reply: "You're on our Starter plan with 24/5 support. We'll respond on the next business day."; create ticket | No | Needed |
| EC-F011 | Form submission triggers a CSRF / bot detection flag | Block submission; do not create ticket; alert admin; do not send any response to the submitter | No (security block) | Needed |
| EC-F012 | Customer submits a form asking to compare CRM Digital with a competitor | Do not compare; explain that the agent can only help with CRM Digital products; redirect to product docs | No | Needed |
| EC-F013 | Customer submits a second form before the first ticket is resolved | Link both tickets to the same customer; create new ticket with reference to open prior ticket; ask if it's related | No | Needed |
| EC-F014 | Customer says their issue was "never resolved" but the ticket shows "resolved" in the system | Reopen ticket; do not challenge the customer; apologize; investigate; escalate to Tier 2 for review | Yes — Tier 2 | Needed |
| EC-F015 | Form submission contains a security report ("I found a vulnerability in your system") | Escalate immediately to Security team (P1); acknowledge receipt with standard security disclosure message; do not provide KB response | Yes — Security P1 | Needed |
| EC-F016 | Customer's form message sentiment is Negative (score 0.25) | Escalate to Senior Support; reply with empathy-first acknowledgement; do not attempt KB resolution | Yes — Sentiment | Needed |
| EC-F017 | Customer submits a form asking for an export of all their data | Escalate to Legal team (GDPR data portability request); acknowledge with expected processing time | Yes — Legal/GDPR | Needed |
| EC-F018 | Customer form includes a request for a custom contract or enterprise pricing | Escalate to Account/Sales team; acknowledge that custom contracts require human handling | Yes — Billing/Sales | Needed |
| EC-F019 | Form submitted by a user who is not yet a customer (prospect inquiry) | Detect that email is not in the customer database; treat as a pre-sales inquiry; route to Sales team | Yes — Pre-Sales | Needed |
| EC-F020 | Customer submits multiple web forms in 24 hours on different topics | Create separate tickets for each; detect as same customer from email; flag the pattern for account manager | No (but flag) | Needed |
| EC-F021 | Customer submits a form and includes a payment card number in the message body | Redact card number from all logs and responses immediately; flag as security sensitive; escalate to Security team | Yes — Security/PCI | Needed |
| EC-F022 | Web form is submitted during a platform outage (when the system itself is down) | Queue submission for processing when system recovers; auto-acknowledge via email as soon as system is back; create ticket retroactively | No (queue) | Needed |

---

## Cross-Channel Edge Cases (EC-X001 – EC-X005)

These cases span multiple channels and apply universally.

| ID | Scenario | Expected Behavior | Escalate? | Test Status |
|----|----------|-------------------|-----------|-------------|
| EC-X001 | Customer contacts all three channels simultaneously with the same issue | Deduplicate across channels using email as key; process once; acknowledge on all channels with the same ticket reference | No | Needed |
| EC-X002 | Customer's email changes mid-conversation (account update) | Flag for manual review; do not auto-merge; create new profile linked to new email; preserve old conversation history with old email | No (flag) | Needed |
| EC-X003 | AI response contains a factual error and customer replies correcting it | Acknowledge the correction; escalate to Tier 2 for review of the KB article; flag as potential hallucination | Yes — Tier 2 | Needed |
| EC-X004 | Human agent resolves an escalated ticket and marks it closed, but customer follows up on a new channel asking the same question | Detect closed-but-followed-up pattern; create linked ticket; reference prior resolution; do not reopen old ticket | No | Needed |
| EC-X005 | Customer's message arrives on a channel the system is not yet integrated with (e.g., Slack DM from Enterprise customer) | Log as unsupported channel; notify customer to use Email/WhatsApp/Web Form; escalate to Enterprise success manager | Yes — Enterprise | Needed |

---

## Summary: Edge Case Count by Channel

| Channel | Edge Cases | Automated Tests Needed |
|---------|-----------|----------------------|
| Email | 22 (EC-E001–EC-E022) | 22 |
| WhatsApp | 22 (EC-W001–EC-W022) | 22 |
| Web Form | 22 (EC-F001–EC-F022) | 22 |
| Cross-Channel | 5 (EC-X001–EC-X005) | 5 |
| **Total** | **71** | **71** |

---

## Priority Testing Tiers

### Must Test First (P0 — Safety Critical)

These edge cases can cause data loss, legal liability, or security exposure if handled incorrectly:

- EC-E006 (Legal keyword in benign context — still escalate)
- EC-E021 (GDPR right to erasure)
- EC-F015 (Security vulnerability report)
- EC-F021 (Payment card number in form body)
- EC-W012 (Profanity / aggressive customer)
- EC-E012 (P1 outage email at 3 AM)

### Test Second (P1 — Core Functionality)

- EC-E001, EC-W001, EC-F001 (Empty/blank inputs)
- EC-E003, EC-W007, EC-F002 (Duplicate message deduplication)
- EC-E005, EC-W001, EC-F007 (Unknown customer identity)
- EC-E007 (Billing + how-to in same message)
- EC-W011 (Long step-by-step needed on WhatsApp)
- EC-W009 (Channel switch mid-conversation)

### Test Third (P2 — Edge Behavior)

All remaining edge cases covering unusual inputs, rate limits, and non-standard customer behaviors.
