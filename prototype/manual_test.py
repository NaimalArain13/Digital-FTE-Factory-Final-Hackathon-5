#!/usr/bin/env python3
"""
Manual Interactive Testing for Customer Success FTE
Calls CustomerSuccessAgent directly (no MCP layer needed for local testing)
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from customer_agent_prototype import (
    CustomerSuccessAgent,
    CustomerMessage,
    ResolutionStatus
)

# Shared agent instance + simple ticket store
agent = CustomerSuccessAgent(docs_path="../context/product-docs.md")
tickets: dict = {}
ticket_counter = 1000
escalations: dict = {}
escalation_counter = 5000


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def next_ticket_id() -> str:
    global ticket_counter
    ticket_counter += 1
    return f"TKT-{ticket_counter}"


def next_escalation_id() -> str:
    global escalation_counter
    escalation_counter += 1
    return f"ESC-{escalation_counter}"


def pj(data):
    """Pretty-print a dict as JSON."""
    print(json.dumps(data, indent=2, default=str))


def divider(title: str = "", width: int = 70):
    if title:
        print(f"\n{'='*width}")
        print(f"  {title}")
        print(f"{'='*width}")
    else:
        print("─" * width)


# ─────────────────────────────────────────────────────────────────────────────
# Tool 1 – search_knowledge_base
# ─────────────────────────────────────────────────────────────────────────────

def test_tool_1():
    divider("TOOL 1: search_knowledge_base")
    query = input("\nSearch query [How do I connect WhatsApp?]: ").strip()
    if not query:
        query = "How do I connect WhatsApp?"

    print(f"\nSearching for: '{query}'...\n")
    results = agent.knowledge_base.search(query, max_results=3)
    pj({"success": True, "results_count": len(results), "results": results})


# ─────────────────────────────────────────────────────────────────────────────
# Tool 2 – create_ticket
# ─────────────────────────────────────────────────────────────────────────────

def test_tool_2():
    divider("TOOL 2: create_ticket")
    print("\nEnter ticket details (Enter = use default):")
    email    = input("  Customer email    [test@example.com]: ").strip() or "test@example.com"
    name     = input("  Customer name     [Test User]: ").strip()         or "Test User"
    tier     = input("  Tier (Starter/Growth/Enterprise) [Growth]: ").strip() or "Growth"
    issue    = input("  Issue description [Test issue]: ").strip()        or "Test issue"
    priority = input("  Priority (low/normal/high/critical) [normal]: ").strip() or "normal"
    channel  = input("  Channel (email/whatsapp/web_form) [email]: ").strip() or "email"

    tid = next_ticket_id()
    sentiment = agent.sentiment_analyzer.analyze(issue)
    topics    = agent.topic_extractor.extract(issue)

    tickets[tid] = {
        "ticket_id":      tid,
        "customer_email": email,
        "customer_name":  name,
        "customer_tier":  tier,
        "issue":          issue,
        "priority":       priority,
        "channel":        channel,
        "topics":         topics,
        "sentiment_score": sentiment,
        "status":         "open",
        "created_at":     datetime.utcnow().isoformat(),
    }

    print(f"\nCreating ticket...\n")
    pj({"success": True, "ticket_id": tid, "topics": topics, "sentiment": sentiment})
    return tid, email


# ─────────────────────────────────────────────────────────────────────────────
# Tool 3 – get_customer_history
# ─────────────────────────────────────────────────────────────────────────────

def test_tool_3():
    divider("TOOL 3: get_customer_history")
    email = input("\nCustomer email [test@example.com]: ").strip() or "test@example.com"

    print(f"\nFetching history for: {email}...\n")
    conv = agent.conversation_memory.get_conversation(email)

    if conv:
        pj({
            "success":      True,
            "has_history":  True,
            "customer_email": email,
            "customer_name":  conv.customer_name,
            "summary": {
                "total_interactions":  len(conv.turns),
                "channels_used":       conv.channels_used,
                "original_channel":    conv.original_channel,
                "has_channel_switch":  conv.has_channel_switch(),
                "topics_discussed":    conv.topics_discussed,
                "average_sentiment":   round(conv.average_sentiment, 3),
                "resolution_status":   conv.resolution_status.value,
            }
        })
    else:
        pj({"success": True, "has_history": False, "customer_email": email,
            "message": "No conversation history found"})


# ─────────────────────────────────────────────────────────────────────────────
# Tool 4 – escalate_to_human
# ─────────────────────────────────────────────────────────────────────────────

def test_tool_4():
    divider("TOOL 4: escalate_to_human")

    print("\nCreating a sample ticket to escalate first...")
    tid = next_ticket_id()
    tickets[tid] = {
        "ticket_id": tid, "customer_email": "escalate@test.com",
        "customer_name": "Escalate Test", "customer_tier": "Enterprise",
        "issue": "Critical security issue", "priority": "critical",
        "channel": "email", "status": "open",
        "created_at": datetime.utcnow().isoformat(),
    }
    print(f"  Ticket created: {tid}")

    reason   = input("\nEscalation reason (billing/security/legal/outage/bug) [security]: ").strip() or "security"
    priority = input("Priority (normal/high/critical) [critical]: ").strip() or "critical"

    eid = next_escalation_id()
    escalations[eid] = {
        "escalation_id": eid, "ticket_id": tid,
        "reason": reason, "priority": priority,
        "created_at": datetime.utcnow().isoformat(),
    }
    tickets[tid]["status"] = "escalated"

    print(f"\nEscalating ticket {tid}...\n")
    pj({"success": True, "escalation_id": eid, "ticket_id": tid,
        "reason": reason, "priority": priority})


# ─────────────────────────────────────────────────────────────────────────────
# Tool 5 – process_customer_message  (full E2E pipeline)
# ─────────────────────────────────────────────────────────────────────────────

def test_tool_5():
    divider("TOOL 5: process_customer_message — FULL PIPELINE")
    print("\nEnter customer details (Enter = use default):")
    email   = input("  Email   [demo@company.com]: ").strip()  or "demo@company.com"
    name    = input("  Name    [Demo User]: ").strip()          or "Demo User"
    tier    = input("  Tier    [Growth]: ").strip()             or "Growth"
    message = input("  Message [How do I upload training data?]: ").strip() or "How do I upload training data?"
    channel = input("  Channel [email]: ").strip()              or "email"

    print(f"\nProcessing end-to-end...\n")
    msg = CustomerMessage(
        channel=channel,
        customer_email=email,
        customer_name=name,
        customer_tier=tier,
        content=message,
    )
    result = agent.process_message(msg)

    divider()
    print("RESPONSE GENERATED:")
    divider()
    print(result["response"])
    divider()

    esc = result.get("escalation", {})
    print(f"\nEscalated : {esc.get('escalate', False)}")
    if esc.get("escalate"):
        print(f"Reason    : {esc.get('reason')}")
        print(f"Team      : {esc.get('team')}")
        print(f"Priority  : {esc.get('priority')}")

    print(f"\nSentiment : {result['sentiment']:.2f}")
    print(f"Topics    : {', '.join(result['topics'])}")
    print(f"KB hits   : {len(result['kb_results'])}")


# ─────────────────────────────────────────────────────────────────────────────
# Tool 6 – get_conversation_stats
# ─────────────────────────────────────────────────────────────────────────────

def test_tool_6():
    divider("TOOL 6: get_conversation_stats")
    print("\nFetching overall statistics...\n")
    pj(agent.conversation_memory.get_conversation_stats())


# ─────────────────────────────────────────────────────────────────────────────
# Full interactive conversation loop
# ─────────────────────────────────────────────────────────────────────────────

def run_conversation_loop():
    divider("FULL INTERACTIVE CONVERSATION FLOW")
    print("\nSimulate a real customer conversation (multi-turn).")
    print("Type 'quit' or leave message blank to end the session.\n")

    email   = input("Customer email   [user@example.com]: ").strip() or "user@example.com"
    name    = input("Customer name    [Jane Doe]: ").strip()          or "Jane Doe"
    tier    = input("Customer tier    [Growth]: ").strip()            or "Growth"
    channel = input("Channel          [email]: ").strip()             or "email"

    turn = 0
    while True:
        turn += 1
        print(f"\n[Turn {turn}]")
        message = input("  Your message (or 'quit'): ").strip()
        if not message or message.lower() == "quit":
            print("\nEnding conversation.")
            break

        msg = CustomerMessage(
            channel=channel,
            customer_email=email,
            customer_name=name,
            customer_tier=tier,
            content=message,
        )
        result = agent.process_message(msg)

        divider()
        print("AGENT RESPONSE:")
        divider()
        print(result["response"])
        divider()

        esc = result.get("escalation", {})
        if esc.get("escalate"):
            print(f"  >> ESCALATED to {esc.get('team')} — reason: {esc.get('reason')}")
            print("  >> Ending session (ticket handed to human team).")
            break

        conv = agent.conversation_memory.get_conversation(email)
        if conv:
            print(f"  Sentiment so far: {conv.average_sentiment:.2f}  |  "
                  f"Topics: {', '.join(conv.topics_discussed)}")

    # Summary after conversation
    conv = agent.conversation_memory.get_conversation(email)
    if conv and conv.turns:
        print(f"\nConversation summary for {name}:")
        print(f"  Turns     : {len(conv.turns)}")
        print(f"  Channels  : {', '.join(conv.channels_used)}")
        print(f"  Topics    : {', '.join(conv.topics_discussed)}")
        print(f"  Status    : {conv.resolution_status.value}")
        print(f"  Sentiment : {conv.average_sentiment:.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# Main menu
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "="*70)
    print("  CUSTOMER SUCCESS FTE — MANUAL TESTING")
    print("="*70)

    while True:
        print("\n\nSelect an option:")
        print("  1. search_knowledge_base     — Search product docs")
        print("  2. create_ticket             — Create a support ticket")
        print("  3. get_customer_history      — View conversation history")
        print("  4. escalate_to_human         — Escalate a ticket")
        print("  5. process_customer_message  — Single E2E message (full pipeline)")
        print("  6. get_conversation_stats    — View overall stats")
        print("  7. FULL CONVERSATION LOOP    — Interactive multi-turn chat")
        print("  8. Run all single-tool tests")
        print("  0. Exit")

        choice = input("\nEnter your choice (0-8): ").strip()

        try:
            if   choice == "1": test_tool_1()
            elif choice == "2": test_tool_2()
            elif choice == "3": test_tool_3()
            elif choice == "4": test_tool_4()
            elif choice == "5": test_tool_5()
            elif choice == "6": test_tool_6()
            elif choice == "7": run_conversation_loop()
            elif choice == "8":
                print("\nRunning all single-tool tests...")
                test_tool_1()
                test_tool_2()
                test_tool_5()
                test_tool_3()
                test_tool_6()
                print("\n\nAll tests completed!")
            elif choice == "0":
                print("\nGoodbye!")
                break
            else:
                print("\nInvalid choice. Please enter 0-8.")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Returning to menu...")
            continue
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()

        input("\n\nPress Enter to continue...")


if __name__ == "__main__":
    main()
