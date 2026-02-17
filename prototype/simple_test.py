#!/usr/bin/env python3
"""
Simple standalone test for Customer Success Agent
Tests the core logic without MCP server
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from customer_agent_prototype import (
    CustomerSuccessAgent,
    CustomerMessage
)


def print_section(title):
    """Print formatted section"""
    print(f"\n{'='*80}")
    print(f" {title}")
    print(f"{'='*80}\n")


def main():
    """Run simple tests"""
    print("\n" + "="*80)
    print(" CUSTOMER SUCCESS AGENT - SIMPLE TEST")
    print("="*80)

    # Initialize agent
    agent = CustomerSuccessAgent(docs_path="../context/product-docs.md")

    # Test 1: Search Knowledge Base
    print_section("TEST 1: Knowledge Base Search")
    query = "How do I connect WhatsApp?"
    print(f"Query: '{query}'\n")
    results = agent.knowledge_base.search(query, max_results=3)
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['title']} (score: {result['score']:.1f})")

    # Test 2: Process Customer Message (Email)
    print_section("TEST 2: Process Email Message")
    msg1 = CustomerMessage(
        channel="email",
        customer_email="sarah@company.com",
        customer_name="Sarah Johnson",
        customer_tier="Growth",
        content="How do I connect WhatsApp to the FTE?",
        subject="Integration Question"
    )
    print(f"Processing: {msg1.content}\n")
    result1 = agent.process_message(msg1)
    print("Response:")
    print("-" * 80)
    print(result1["response"])
    print("-" * 80)
    print(f"Escalated: {result1['escalation'].get('escalate', False)}")
    print(f"KB Results: {len(result1['kb_results'])}")

    # Test 3: Follow-up Message (Same Customer)
    print_section("TEST 3: Follow-up Message")
    msg2 = CustomerMessage(
        channel="email",
        customer_email="sarah@company.com",
        customer_name="Sarah Johnson",
        customer_tier="Growth",
        content="Thanks! Where do I find the API credentials?",
    )
    print(f"Processing: {msg2.content}\n")
    result2 = agent.process_message(msg2)

    # Check conversation history
    conversation = agent.conversation_memory.get_conversation("sarah@company.com")
    print(f"Conversation turns: {len(conversation.turns)}")
    print(f"Topics discussed: {', '.join(conversation.topics_discussed)}")
    print(f"Average sentiment: {conversation.average_sentiment:.2f}")

    # Test 4: Billing Issue (Auto-Escalation)
    print_section("TEST 4: Billing Issue (Auto-Escalation)")
    msg3 = CustomerMessage(
        channel="whatsapp",
        customer_email="mike@startup.io",
        customer_name="Mike Chen",
        customer_tier="Growth",
        content="I see two charges for this month on my card. Can you check?"
    )
    print(f"Processing: {msg3.content}\n")
    result3 = agent.process_message(msg3)
    print("Response (WhatsApp format):")
    print("-" * 80)
    print(result3["response"])
    print("-" * 80)
    print(f"⚠️ ESCALATED: {result3['escalation'].get('escalate', False)}")
    if result3['escalation'].get('escalate'):
        print(f"   Reason: {result3['escalation'].get('reason')}")
        print(f"   Team: {result3['escalation'].get('team')}")

    # Test 5: Channel Switch
    print_section("TEST 5: Channel Switch Detection")
    msg4 = CustomerMessage(
        channel="email",
        customer_email="mike@startup.io",
        customer_name="Mike Chen",
        customer_tier="Growth",
        content="Following up on my WhatsApp message about billing.",
        subject="Billing Follow-up"
    )
    print(f"Processing: {msg4.content}\n")
    result4 = agent.process_message(msg4)

    # Check channel switch
    conversation = agent.conversation_memory.get_conversation("mike@startup.io")
    print(f"Channels used: {', '.join(conversation.channels_used)}")
    print(f"⚠️ CHANNEL SWITCH: {conversation.has_channel_switch()}")
    print(f"Original channel: {conversation.original_channel}")

    # Test 6: Overall Statistics
    print_section("TEST 6: Overall Statistics")
    stats = agent.conversation_memory.get_conversation_stats()
    print(f"Total conversations: {stats.get('total_conversations', 0)}")
    print(f"Total turns: {stats.get('total_turns', 0)}")
    print(f"Average sentiment: {stats.get('avg_sentiment', 0):.2f}")
    print(f"Escalated count: {stats.get('escalated_count', 0)}")
    print(f"Channel switches: {stats.get('channel_switches', 0)}")
    print(f"Common topics: {', '.join(stats.get('common_topics', []))}")

    # Test 7: Sentiment Analysis
    print_section("TEST 7: Sentiment Analysis")
    test_messages = [
        ("Thanks for the great service! This is awesome!", "Positive"),
        ("I'm frustrated with this. Nothing works.", "Negative"),
        ("How do I reset my password?", "Neutral")
    ]
    for msg, expected in test_messages:
        sentiment = agent.sentiment_analyzer.analyze(msg)
        print(f"Message: '{msg}'")
        print(f"  Sentiment: {sentiment:.2f} ({expected})")

    print("\n" + "="*80)
    print(" ALL TESTS COMPLETED ✓")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
