#!/usr/bin/env python3
"""
Test script for Customer Success FTE MCP Server Tools
Demonstrates all available tools with realistic scenarios
"""

import asyncio
import json
import sys
from pathlib import Path

# Import the MCP server functions
sys.path.insert(0, str(Path(__file__).parent))
from mcp_server import (
    search_knowledge_base,
    create_ticket,
    escalate_to_human,
    process_customer_message,
    agent  # Import agent for direct access to conversation memory
)


async def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f" {title}")
    print(f"{'='*80}\n")


async def print_result(result: str):
    """Pretty print JSON result"""
    try:
        data = json.loads(result)
        print(json.dumps(data, indent=2))
    except:
        print(result)


async def test_search_knowledge_base():
    """Test 1: Search Knowledge Base"""
    await print_section("TEST 1: Search Knowledge Base")

    print("Query: 'How do I connect WhatsApp?'\n")
    result = await search_knowledge_base(
        query="How do I connect WhatsApp to the FTE?",
        max_results=3
    )
    await print_result(result)


async def test_create_ticket():
    """Test 2: Create Ticket"""
    await print_section("TEST 2: Create Ticket")

    print("Creating ticket for Sarah Johnson...\n")
    result = await create_ticket(
        customer_email="sarah@company.com",
        customer_name="Sarah Johnson",
        customer_tier="Growth",
        issue="How do I connect WhatsApp to the FTE?",
        priority="normal",
        channel="email",
        subject="WhatsApp Integration Question"
    )
    await print_result(result)
    return json.loads(result)["ticket_id"] if "ticket_id" in result else None


async def test_process_customer_message():
    """Test 3: End-to-End Message Processing"""
    await print_section("TEST 3: Process Customer Message (End-to-End)")

    print("Scenario 1: Sarah's first message (email)\n")
    result1 = await process_customer_message(
        customer_email="sarah@company.com",
        customer_name="Sarah Johnson",
        customer_tier="Growth",
        message="How do I connect WhatsApp to the FTE?",
        channel="email"
    )
    data1 = json.loads(result1)
    print("Response preview:")
    if "response" in data1:
        print(data1["response"][:200] + "..." if len(data1["response"]) > 200 else data1["response"])
    print(f"\nEscalated: {data1.get('escalation', {}).get('escalate', False)}")

    print("\n" + "-"*80 + "\n")

    print("Scenario 2: Sarah's follow-up (same topic)\n")
    result2 = await process_customer_message(
        customer_email="sarah@company.com",
        customer_name="Sarah Johnson",
        customer_tier="Growth",
        message="Thanks! And where do I find the API credentials?",
        channel="email"
    )
    data2 = json.loads(result2)
    print("Response preview:")
    if "response" in data2:
        print(data2["response"][:200] + "..." if len(data2["response"]) > 200 else data2["response"])

    print("\n" + "-"*80 + "\n")

    print("Scenario 3: Mike's billing issue (WhatsApp)\n")
    result3 = await process_customer_message(
        customer_email="mike@startup.io",
        customer_name="Mike Chen",
        customer_tier="Growth",
        message="I see two charges for this month on my card. Can you check?",
        channel="whatsapp"
    )
    data3 = json.loads(result3)
    print("Response preview:")
    if "response" in data3:
        print(data3["response"][:200] + "..." if len(data3["response"]) > 200 else data3["response"])
    print(f"\n⚠️ ESCALATED: {data3.get('escalation', {}).get('escalate', False)}")

    print("\n" + "-"*80 + "\n")

    print("Scenario 4: Mike switches to email (channel switch!)\n")
    result4 = await process_customer_message(
        customer_email="mike@startup.io",
        customer_name="Mike Chen",
        customer_tier="Growth",
        message="Following up on my WhatsApp message. Can you send invoice breakdown?",
        channel="email"
    )
    data4 = json.loads(result4)
    print("Response preview:")
    if "response" in data4:
        print(data4["response"][:200] + "..." if len(data4["response"]) > 200 else data4["response"])


async def test_get_customer_history():
    """Test 4: Get Customer History (using agent directly)"""
    await print_section("TEST 4: Get Customer History (Direct Access)")

    print("Getting history for Mike Chen (should show channel switch)...\n")

    conversation = agent.conversation_memory.get_conversation("mike@startup.io")

    if conversation:
        print(f"Customer: {conversation.customer_name} ({conversation.customer_tier})")
        print(f"\nSummary:")
        print(f"  Total interactions: {len(conversation.turns)}")
        print(f"  Channels used: {', '.join(conversation.channels_used)}")
        print(f"  Original channel: {conversation.original_channel}")
        print(f"  Channel switch: {'✓ YES' if conversation.has_channel_switch() else '✗ NO'}")
        print(f"  Topics: {', '.join(conversation.topics_discussed)}")
        print(f"  Sentiment: {conversation._sentiment_label()} ({conversation.average_sentiment:.2f})")
        print(f"  Status: {conversation.resolution_status.value}")
    else:
        print("No conversation history found")


async def test_escalate_to_human():
    """Test 5: Manual Escalation"""
    await print_section("TEST 5: Escalate to Human")

    # First create a ticket
    print("Creating ticket for security issue...\n")
    ticket_result = await create_ticket(
        customer_email="david@enterprise.com",
        customer_name="David Martinez",
        customer_tier="Enterprise",
        issue="We suspect unauthorized access to our workspace",
        priority="critical",
        channel="email",
        subject="URGENT: Security Concern"
    )
    ticket_data = json.loads(ticket_result)
    ticket_id = ticket_data["ticket_id"]

    print(f"Ticket created: {ticket_id}\n")
    print("Escalating to Security Team...\n")

    escalation_result = await escalate_to_human(
        ticket_id=ticket_id,
        reason="security",
        priority="critical"
    )
    await print_result(escalation_result)


async def test_get_stats():
    """Test 6: Get Conversation Stats (using agent directly)"""
    await print_section("TEST 6: Overall Statistics")

    stats = agent.conversation_memory.get_conversation_stats()

    print("Conversation Statistics:")
    print(f"  Total conversations: {stats.get('total_conversations', 0)}")
    print(f"  Total turns: {stats.get('total_turns', 0)}")
    print(f"  Average sentiment: {stats.get('avg_sentiment', 0):.2f}")
    print(f"  Escalated: {stats.get('escalated_count', 0)}")
    print(f"  Solved: {stats.get('solved_count', 0)}")
    print(f"  Channel switches: {stats.get('channel_switches', 0)}")
    print(f"  Common topics: {', '.join(stats.get('common_topics', []))}")


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print(" CUSTOMER SUCCESS FTE - MCP TOOLS TEST SUITE")
    print("="*80)

    try:
        # Run tests in sequence
        await test_search_knowledge_base()
        await asyncio.sleep(0.5)

        await test_create_ticket()
        await asyncio.sleep(0.5)

        await test_process_customer_message()
        await asyncio.sleep(0.5)

        await test_get_customer_history()
        await asyncio.sleep(0.5)

        await test_escalate_to_human()
        await asyncio.sleep(0.5)

        await test_get_stats()

        print("\n" + "="*80)
        print(" ALL TESTS COMPLETED SUCCESSFULLY ✓")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
