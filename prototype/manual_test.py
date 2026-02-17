#!/usr/bin/env python3
"""
Manual Interactive Testing for MCP Tools
Run individual tools and see the results
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp_server import (
    search_knowledge_base,
    create_ticket,
    escalate_to_human,
    process_customer_message,
    agent  # For direct access to conversation memory
)


def print_json(data):
    """Pretty print JSON"""
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except:
            pass
    print(json.dumps(data, indent=2) if isinstance(data, dict) else data)


async def test_tool_1():
    """Test: Search Knowledge Base"""
    print("\n" + "="*70)
    print("TOOL 1: search_knowledge_base")
    print("="*70)

    query = input("\nEnter your search query (or press Enter for default): ").strip()
    if not query:
        query = "How do I connect WhatsApp?"

    print(f"\nSearching for: '{query}'...\n")
    result = await search_knowledge_base(query=query, max_results=3)
    print_json(result)


async def test_tool_2():
    """Test: Create Ticket"""
    print("\n" + "="*70)
    print("TOOL 2: create_ticket")
    print("="*70)

    print("\nEnter ticket details (or press Enter to use defaults):")
    email = input("Customer email [test@example.com]: ").strip() or "test@example.com"
    name = input("Customer name [Test User]: ").strip() or "Test User"
    tier = input("Customer tier (Starter/Growth/Enterprise) [Growth]: ").strip() or "Growth"
    issue = input("Issue description [Test issue]: ").strip() or "Test issue"
    priority = input("Priority (low/normal/high/critical) [normal]: ").strip() or "normal"
    channel = input("Channel (email/whatsapp/web_form) [email]: ").strip() or "email"

    print(f"\nCreating ticket...\n")
    result = await create_ticket(
        customer_email=email,
        customer_name=name,
        customer_tier=tier,
        issue=issue,
        priority=priority,
        channel=channel
    )
    print_json(result)

    # Return ticket ID for other tests
    data = json.loads(result)
    if data.get("success"):
        return data["ticket_id"], email
    return None, None


async def test_tool_3():
    """Test: Get Customer History (Direct Access)"""
    print("\n" + "="*70)
    print("TOOL 3: get_customer_history (via agent)")
    print("="*70)

    email = input("\nEnter customer email [test@example.com]: ").strip() or "test@example.com"

    print(f"\nFetching history for: {email}...\n")

    conversation = agent.conversation_memory.get_conversation(email)

    if conversation:
        result = {
            "success": True,
            "has_history": True,
            "customer_email": email,
            "customer_name": conversation.customer_name,
            "summary": {
                "total_interactions": len(conversation.turns),
                "channels_used": conversation.channels_used,
                "original_channel": conversation.original_channel,
                "has_channel_switch": conversation.has_channel_switch(),
                "topics_discussed": conversation.topics_discussed,
                "average_sentiment": conversation.average_sentiment,
                "resolution_status": conversation.resolution_status.value
            }
        }
    else:
        result = {
            "success": True,
            "has_history": False,
            "customer_email": email,
            "message": "No conversation history found"
        }

    print_json(result)


async def test_tool_4():
    """Test: Escalate to Human"""
    print("\n" + "="*70)
    print("TOOL 4: escalate_to_human")
    print("="*70)

    # First create a ticket
    print("\nFirst, let's create a ticket to escalate...")
    result = await create_ticket(
        customer_email="escalate@test.com",
        customer_name="Escalate Test",
        customer_tier="Enterprise",
        issue="Critical security issue - need immediate help",
        priority="critical",
        channel="email"
    )
    data = json.loads(result)
    ticket_id = data["ticket_id"]
    print(f"Ticket created: {ticket_id}")

    print("\nEnter escalation details:")
    reason = input("Reason (billing/security/legal/outage/bug) [security]: ").strip() or "security"
    priority = input("Priority (normal/high/critical) [critical]: ").strip() or "critical"

    print(f"\nEscalating ticket {ticket_id}...\n")
    result = await escalate_to_human(
        ticket_id=ticket_id,
        reason=reason,
        priority=priority
    )
    print_json(result)


async def test_tool_5():
    """Test: Process Customer Message (End-to-End)"""
    print("\n" + "="*70)
    print("TOOL 5: process_customer_message (RECOMMENDED)")
    print("="*70)

    print("\nThis tool does everything in one call!")
    print("Enter customer message details (or press Enter for defaults):")

    email = input("Customer email [demo@company.com]: ").strip() or "demo@company.com"
    name = input("Customer name [Demo User]: ").strip() or "Demo User"
    tier = input("Customer tier [Growth]: ").strip() or "Growth"
    message = input("Customer message [How do I upload training data?]: ").strip() or "How do I upload training data?"
    channel = input("Channel [email]: ").strip() or "email"

    print(f"\nProcessing message end-to-end...\n")
    result = await process_customer_message(
        customer_email=email,
        customer_name=name,
        customer_tier=tier,
        message=message,
        channel=channel
    )

    data = json.loads(result)
    print("\n" + "-"*70)
    print("RESPONSE GENERATED:")
    print("-"*70)
    print(data.get("response", ""))
    print("-"*70)
    if "escalation" in data:
        print(f"\nEscalated: {data['escalation'].get('escalate', False)}")
        if data['escalation'].get('escalate'):
            print(f"Reason: {data['escalation'].get('reason')}")


async def test_tool_6():
    """Test: Get Conversation Stats (Direct Access)"""
    print("\n" + "="*70)
    print("TOOL 6: get_conversation_stats (via agent)")
    print("="*70)

    print("\nFetching overall statistics...\n")
    stats = agent.conversation_memory.get_conversation_stats()
    print_json(stats)


async def main():
    """Interactive menu"""
    print("\n" + "="*70)
    print("  CUSTOMER SUCCESS FTE - MANUAL TOOL TESTING")
    print("="*70)

    while True:
        print("\n\nSelect a tool to test:")
        print("  1. search_knowledge_base - Search product docs")
        print("  2. create_ticket - Create a support ticket")
        print("  3. get_customer_history - View conversation history (direct)")
        print("  4. escalate_to_human - Escalate a ticket")
        print("  5. process_customer_message - Full pipeline (RECOMMENDED)")
        print("  6. get_conversation_stats - View overall stats (direct)")
        print("  7. Run all tests automatically")
        print("  0. Exit")

        choice = input("\nEnter your choice (0-7): ").strip()

        try:
            if choice == "1":
                await test_tool_1()
            elif choice == "2":
                await test_tool_2()
            elif choice == "3":
                await test_tool_3()
            elif choice == "4":
                await test_tool_4()
            elif choice == "5":
                await test_tool_5()
            elif choice == "6":
                await test_tool_6()
            elif choice == "7":
                print("\nRunning all tests...")
                await test_tool_1()
                await asyncio.sleep(1)
                await test_tool_2()
                await asyncio.sleep(1)
                await test_tool_5()
                await asyncio.sleep(1)
                await test_tool_3()
                await asyncio.sleep(1)
                await test_tool_6()
                print("\n\nAll tests completed!")
            elif choice == "0":
                print("\nGoodbye!")
                break
            else:
                print("\n❌ Invalid choice. Please enter 0-7.")

        except KeyboardInterrupt:
            print("\n\nTest interrupted. Returning to menu...")
            continue
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

        input("\n\nPress Enter to continue...")


if __name__ == "__main__":
    asyncio.run(main())
