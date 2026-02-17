#!/usr/bin/env python3

from fastmcp import FastMCP
import json
from datetime import datetime
from typing import Dict, Any, List

# Your existing imports
from customer_agent_prototype import (
    CustomerSuccessAgent,
    CustomerMessage,
    ResolutionStatus
)

# =================================================================
# INIT
# =================================================================

mcp = FastMCP("customer-success-fte")

agent = CustomerSuccessAgent(docs_path="../context/product-docs.md")

tickets: Dict[str, Dict[str, Any]] = {}
ticket_counter = 1000

escalations: Dict[str, Dict[str, Any]] = {}
escalation_counter = 5000


# =================================================================
# HELPERS
# =================================================================

def generate_ticket_id() -> str:
    global ticket_counter
    ticket_counter += 1
    return f"TKT-{ticket_counter}"


def generate_escalation_id() -> str:
    global escalation_counter
    escalation_counter += 1
    return f"ESC-{escalation_counter}"


# =================================================================
# TOOLS
# =================================================================

@mcp.tool()
async def search_knowledge_base(query: str, max_results: int = 5) -> str:
    """Search product documentation for relevant information."""
    try:
        results = agent.knowledge_base.search(query, max_results=max_results)

        return json.dumps({
            "success": True,
            "results_count": len(results),
            "results": results
        }, indent=2)

    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool()
async def create_ticket(
    customer_email: str,
    customer_name: str,
    customer_tier: str,
    issue: str,
    priority: str,
    channel: str,
    subject: str = ""
) -> str:
    """Create support ticket."""

    ticket_id = generate_ticket_id()

    sentiment = agent.sentiment_analyzer.analyze(issue)
    topics = agent.topic_extractor.extract(issue)

    ticket = {
        "ticket_id": ticket_id,
        "customer_email": customer_email,
        "customer_name": customer_name,
        "customer_tier": customer_tier,
        "issue": issue,
        "priority": priority,
        "channel": channel,
        "topics": topics,
        "sentiment_score": sentiment,
        "status": "open",
        "created_at": datetime.utcnow().isoformat()
    }

    tickets[ticket_id] = ticket

    return json.dumps({
        "success": True,
        "ticket_id": ticket_id
    })


@mcp.tool()
async def escalate_to_human(
    ticket_id: str,
    reason: str,
    priority: str = "normal"
) -> str:
    """Escalate ticket to human."""

    if ticket_id not in tickets:
        return json.dumps({"success": False, "error": "Ticket not found"})

    escalation_id = generate_escalation_id()

    escalation = {
        "escalation_id": escalation_id,
        "ticket_id": ticket_id,
        "reason": reason,
        "priority": priority,
        "created_at": datetime.utcnow().isoformat()
    }

    escalations[escalation_id] = escalation
    tickets[ticket_id]["status"] = "escalated"

    return json.dumps({
        "success": True,
        "escalation_id": escalation_id
    })


@mcp.tool()
async def process_customer_message(
    customer_email: str,
    customer_name: str,
    customer_tier: str,
    message: str,
    channel: str
) -> str:
    """Full E2E message processing."""

    customer_msg = CustomerMessage(
        channel=channel,
        customer_email=customer_email,
        customer_name=customer_name,
        customer_tier=customer_tier,
        content=message
    )

    result = agent.process_message(customer_msg)

    return json.dumps(result, indent=2)


# =================================================================
# RUN SERVER
# =================================================================

if __name__ == "__main__":
    mcp.run()
