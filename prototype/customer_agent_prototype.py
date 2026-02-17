#!/usr/bin/env python3
"""
Customer Success AI Agent - Core Interaction Loop Prototype
Enhanced with conversation memory and cross-channel tracking
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
from enum import Enum


# ============================================================================
# 1. DATA MODELS - Normalize messages from different channels
# ============================================================================

class ResolutionStatus(Enum):
    """Status of conversation resolution"""
    PENDING = "pending"
    SOLVED = "solved"
    ESCALATED = "escalated"
    IN_PROGRESS = "in_progress"


@dataclass
class CustomerMessage:
    """Normalized customer message regardless of channel"""
    channel: str  # "email", "whatsapp", "web_form"
    customer_email: str  # Primary identifier for customer
    customer_name: str
    customer_tier: str  # "Starter", "Growth", "Enterprise"
    content: str
    subject: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    message_id: str = ""

    def __post_init__(self):
        if not self.message_id:
            # Generate simple message ID
            self.message_id = f"msg_{int(self.timestamp.timestamp()*1000)}"

    def __str__(self):
        return f"[{self.channel.upper()}] {self.customer_name} ({self.customer_tier}): {self.content[:50]}..."


@dataclass
class ConversationTurn:
    """A single turn in the conversation (customer message + agent response)"""
    customer_message: CustomerMessage
    agent_response: str
    kb_results: List[Dict]
    escalated: bool
    sentiment_score: float  # 0.0 (negative) to 1.0 (positive)
    topics: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Conversation:
    """Complete conversation history for a customer"""
    customer_email: str  # Primary key
    customer_name: str
    customer_tier: str
    turns: List[ConversationTurn] = field(default_factory=list)
    topics_discussed: List[str] = field(default_factory=list)
    channels_used: List[str] = field(default_factory=list)
    original_channel: Optional[str] = None
    resolution_status: ResolutionStatus = ResolutionStatus.PENDING
    average_sentiment: float = 0.5  # Neutral
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def add_turn(self, turn: ConversationTurn):
        """Add a conversation turn and update metadata"""
        self.turns.append(turn)
        self.last_updated = datetime.utcnow()

        # Update topics (avoid duplicates)
        for topic in turn.topics:
            if topic not in self.topics_discussed:
                self.topics_discussed.append(topic)

        # Track channel usage
        channel = turn.customer_message.channel
        if not self.original_channel:
            self.original_channel = channel
        if channel not in self.channels_used:
            self.channels_used.append(channel)

        # Update average sentiment
        if self.turns:
            sentiments = [t.sentiment_score for t in self.turns]
            self.average_sentiment = sum(sentiments) / len(sentiments)

        # Update resolution status
        if turn.escalated:
            self.resolution_status = ResolutionStatus.ESCALATED

    def get_context_summary(self, max_turns: int = 3) -> str:
        """Get a summary of recent conversation context"""
        if not self.turns:
            return "New conversation"

        recent_turns = self.turns[-max_turns:]
        summary_parts = [
            f"Previous {len(recent_turns)} turn(s):",
            f"Topics: {', '.join(self.topics_discussed)}",
            f"Channels: {', '.join(self.channels_used)}",
            f"Sentiment: {self._sentiment_label()}",
        ]

        # Add recent exchanges
        for i, turn in enumerate(recent_turns, 1):
            msg = turn.customer_message.content[:50]
            summary_parts.append(f"  {i}. Customer: {msg}...")

        return '\n'.join(summary_parts)

    def _sentiment_label(self) -> str:
        """Convert sentiment score to label"""
        if self.average_sentiment >= 0.7:
            return "😊 Positive"
        elif self.average_sentiment >= 0.4:
            return "😐 Neutral"
        else:
            return "😞 Negative"

    def has_channel_switch(self) -> bool:
        """Check if customer has switched channels"""
        return len(self.channels_used) > 1


# ============================================================================
# 2. CONVERSATION MEMORY - Track customer conversations
# ============================================================================

class ConversationMemory:
    """In-memory storage for customer conversations (would be DB in production)"""

    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}  # Key: customer_email

    def get_or_create_conversation(self, customer_email: str, customer_name: str,
                                   customer_tier: str) -> Conversation:
        """Get existing conversation or create new one"""
        if customer_email not in self.conversations:
            self.conversations[customer_email] = Conversation(
                customer_email=customer_email,
                customer_name=customer_name,
                customer_tier=customer_tier
            )
        return self.conversations[customer_email]

    def get_conversation(self, customer_email: str) -> Optional[Conversation]:
        """Get existing conversation"""
        return self.conversations.get(customer_email)

    def has_conversation(self, customer_email: str) -> bool:
        """Check if customer has existing conversation"""
        return customer_email in self.conversations

    def get_all_conversations(self) -> List[Conversation]:
        """Get all conversations"""
        return list(self.conversations.values())

    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get statistics across all conversations"""
        if not self.conversations:
            return {"total": 0}

        convos = self.get_all_conversations()
        return {
            "total_conversations": len(convos),
            "total_turns": sum(len(c.turns) for c in convos),
            "avg_sentiment": sum(c.average_sentiment for c in convos) / len(convos),
            "escalated_count": sum(1 for c in convos if c.resolution_status == ResolutionStatus.ESCALATED),
            "solved_count": sum(1 for c in convos if c.resolution_status == ResolutionStatus.SOLVED),
            "channel_switches": sum(1 for c in convos if c.has_channel_switch()),
            "common_topics": self._get_common_topics(convos)
        }

    def _get_common_topics(self, convos: List[Conversation], top_n: int = 5) -> List[str]:
        """Get most common topics discussed"""
        topic_counts = {}
        for conv in convos:
            for topic in conv.topics_discussed:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1

        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, _ in sorted_topics[:top_n]]


# ============================================================================
# 3. SENTIMENT ANALYSIS - Detect customer sentiment
# ============================================================================

class SentimentAnalyzer:
    """Simple keyword-based sentiment analysis"""

    POSITIVE_KEYWORDS = [
        'thanks', 'thank you', 'great', 'awesome', 'excellent', 'perfect',
        'appreciate', 'helpful', 'love', 'good', 'wonderful', 'fantastic'
    ]

    NEGATIVE_KEYWORDS = [
        'frustrated', 'angry', 'disappointed', 'terrible', 'awful', 'worst',
        'useless', 'broken', 'not working', 'problem', 'issue', 'bug',
        'unacceptable', 'unhappy', 'annoyed', 'upset'
    ]

    NEUTRAL_KEYWORDS = [
        'how', 'what', 'when', 'where', 'can', 'please', 'help', 'question'
    ]

    def analyze(self, text: str) -> float:
        """
        Analyze sentiment of text
        Returns score from 0.0 (very negative) to 1.0 (very positive)
        """
        text_lower = text.lower()

        positive_count = sum(1 for word in self.POSITIVE_KEYWORDS if word in text_lower)
        negative_count = sum(1 for word in self.NEGATIVE_KEYWORDS if word in text_lower)
        neutral_count = sum(1 for word in self.NEUTRAL_KEYWORDS if word in text_lower)

        # Calculate base sentiment
        if positive_count == 0 and negative_count == 0:
            # Neutral query
            return 0.5

        # Weighted scoring
        total = positive_count + negative_count
        if total == 0:
            return 0.5

        positive_ratio = positive_count / total

        # Adjust based on negative intensity
        if negative_count > 2:
            return max(0.1, 0.3 - (negative_count * 0.05))
        elif negative_count > 0:
            return 0.3 + (positive_ratio * 0.2)
        elif positive_count > 0:
            return 0.7 + min(0.3, positive_count * 0.1)

        return 0.5


# ============================================================================
# 4. TOPIC EXTRACTION - Identify conversation topics
# ============================================================================

class TopicExtractor:
    """Extract topics from customer messages"""

    TOPIC_KEYWORDS = {
        'billing': ['billing', 'charge', 'invoice', 'payment', 'refund', 'price', 'cost'],
        'integration': ['integration', 'connect', 'sync', 'api', 'webhook', 'salesforce', 'hubspot'],
        'setup': ['setup', 'configure', 'install', 'upload', 'training', 'getting started'],
        'bug': ['bug', 'error', 'broken', 'not working', 'issue', 'problem', '500', '502'],
        'security': ['security', 'unauthorized', 'breach', 'hack', 'login', 'access'],
        'analytics': ['analytics', 'dashboard', 'report', 'export', 'metrics', 'data'],
        'channels': ['email', 'whatsapp', 'sms', 'chat', 'channel'],
        'account': ['account', 'workspace', 'user', 'team', 'delete', 'ownership'],
        'ai_features': ['ai', 'bot', 'automation', 'agent', 'response', 'training'],
    }

    def extract(self, text: str) -> List[str]:
        """Extract topics from text"""
        text_lower = text.lower()
        topics = []

        for topic, keywords in self.TOPIC_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)

        return topics if topics else ['general_inquiry']


# ============================================================================
# 5. KNOWLEDGE SEARCH - Search product docs for answers
# ============================================================================

class SimpleKnowledgeBase:
    """Simple text-based search of product documentation"""

    def __init__(self, docs_path: str = "context/product-docs.md"):
        self.docs_path = Path(docs_path)
        self.sections = self._load_and_parse()

    def _load_and_parse(self) -> List[Dict[str, str]]:
        """Load and parse documentation into sections"""
        if not self.docs_path.exists():
            print(f"Warning: {self.docs_path} not found")
            return []

        content = self.docs_path.read_text(encoding='utf-8')
        sections = []
        current_section = {"title": "Product Summary", "content": []}

        for line in content.split('\n'):
            if line.startswith('##'):
                # Save previous section
                if current_section["content"]:
                    sections.append({
                        "title": current_section["title"],
                        "content": '\n'.join(current_section["content"])
                    })
                # Start new section
                current_section = {
                    "title": line.strip('#').strip(),
                    "content": []
                }
            elif line.strip():
                current_section["content"].append(line)

        # Add last section
        if current_section["content"]:
            sections.append({
                "title": current_section["title"],
                "content": '\n'.join(current_section["content"])
            })

        return sections

    def search(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant documentation sections"""
        query_lower = query.lower()
        query_terms = set(re.findall(r'\w+', query_lower))

        scored_sections = []
        for section in self.sections:
            score = self._calculate_relevance(section, query_lower, query_terms)
            if score > 0:
                scored_sections.append({
                    "title": section["title"],
                    "content": section["content"],
                    "score": score
                })

        # Sort by score and return top results
        scored_sections.sort(key=lambda x: x["score"], reverse=True)
        return scored_sections[:max_results]

    def _calculate_relevance(self, section: Dict, query: str, query_terms: set) -> float:
        """Calculate relevance score for a section"""
        content_lower = section["content"].lower()
        title_lower = section["title"].lower()

        score = 0.0

        # Exact phrase match (highest weight)
        if query in content_lower or query in title_lower:
            score += 10.0

        # Title keyword matches
        title_terms = set(re.findall(r'\w+', title_lower))
        title_matches = query_terms & title_terms
        score += len(title_matches) * 3.0

        # Content keyword matches
        content_terms = set(re.findall(r'\w+', content_lower))
        content_matches = query_terms & content_terms
        score += len(content_matches) * 1.0

        return score


# ============================================================================
# 6. ESCALATION ENGINE - Decide when to escalate to humans
# ============================================================================

class EscalationEngine:
    """Determines when to escalate to human support"""

    # Auto-escalation keyword triggers (including common variations)
    BILLING_KEYWORDS = [
        'billing', 'bill', 'billed',
        'charge', 'charges', 'charged', 'charging',
        'invoice', 'invoices', 'invoiced',
        'payment', 'payments', 'paid', 'pay',
        'refund', 'refunds', 'refunded',
        'pricing', 'price', 'prices', 'priced',
        'cost', 'costs', 'costly',
        'upgrade', 'upgrades', 'upgraded',
        'downgrade', 'downgrades', 'downgraded'
    ]
    LEGAL_KEYWORDS = ['lawyer', 'legal', 'sue', 'suing', 'attorney', 'complaint', 'litigation', 'court', 'counsel']
    SECURITY_KEYWORDS = ['unauthorized', 'breach', 'breached', 'hack', 'hacked', 'security', 'suspicious', 'compromised', 'data leak']
    OUTAGE_KEYWORDS = ['down', 'outage', 'cannot access', '500 error', '502 error', 'not working', 'broken', 'unavailable']
    SLA_KEYWORDS = ['sla', 'sla breach', 'urgent', 'critical', 'waiting hours', 'no response']

    def should_escalate(self, message: CustomerMessage, kb_results: List[Dict]) -> Dict[str, Any]:
        """Decide if escalation is needed"""
        text = f"{message.subject or ''} {message.content}".lower()

        # Check for auto-escalation triggers

        # 1. Billing - ALWAYS escalate
        if self._contains_keywords(text, self.BILLING_KEYWORDS):
            return {
                "escalate": True,
                "reason": "billing",
                "team": "Billing Team",
                "priority": "high",
                "message": "I'm escalating this to our Billing team for assistance."
            }

        # 2. Legal - ALWAYS escalate
        if self._contains_keywords(text, self.LEGAL_KEYWORDS):
            return {
                "escalate": True,
                "reason": "legal",
                "team": "Legal Team",
                "priority": "critical",
                "message": "I'm forwarding this to our Legal team immediately."
            }

        # 3. Security - ALWAYS escalate
        if self._contains_keywords(text, self.SECURITY_KEYWORDS):
            return {
                "escalate": True,
                "reason": "security",
                "team": "Security Team",
                "priority": "critical",
                "message": "I'm escalating this to our Security team as a priority."
            }

        # 4. Outage - ALWAYS escalate
        if self._contains_keywords(text, self.OUTAGE_KEYWORDS):
            return {
                "escalate": True,
                "reason": "outage",
                "team": "Engineering Team",
                "priority": "critical",
                "message": "I've notified our Engineering team of this critical issue."
            }

        # 5. SLA risk
        if self._contains_keywords(text, self.SLA_KEYWORDS):
            return {
                "escalate": True,
                "reason": "sla_risk",
                "team": "Support Manager",
                "priority": "high",
                "message": "I'm escalating this to our Support Manager for priority handling."
            }

        # 6. No useful KB results
        if not kb_results or (kb_results and kb_results[0]["score"] < 2.0):
            return {
                "escalate": True,
                "reason": "no_knowledge_match",
                "team": "Tier 2 Support",
                "priority": "normal",
                "message": "I'm connecting you with a specialist who can help."
            }

        # No escalation needed
        return {"escalate": False}

    def _contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if text contains any keywords (handles exact matches)"""
        text_lower = text.lower()
        for keyword in keywords:
            # Simple substring match to catch all variations
            # Keywords list already includes plurals and variations
            if keyword.lower() in text_lower:
                return True
        return False


# ============================================================================
# 7. RESPONSE GENERATOR - Create helpful responses
# ============================================================================

class ResponseGenerator:
    """Generates customer responses based on KB results"""

    def generate(self, message: CustomerMessage, kb_results: List[Dict],
                 max_sentences: int = 3) -> str:
        """Generate a helpful response from KB results"""
        if not kb_results:
            return "I apologize, but I couldn't find specific information about that in our documentation."

        # Use the top result
        top_result = kb_results[0]

        # Extract relevant content (first few sentences)
        content = top_result["content"]
        sentences = content.split('. ')

        # Build response
        response_parts = []

        # Acknowledge and provide answer
        if "how" in message.content.lower():
            response_parts.append("Here's how to do that:")
        else:
            response_parts.append("Based on our product documentation:")

        # Add relevant content (keep it concise)
        for sentence in sentences[:max_sentences]:
            if sentence.strip() and not sentence.startswith('-'):
                response_parts.append(sentence.strip())

        # Add helpful closing
        response_parts.append("\nLet me know if you need any clarification!")

        return '\n\n'.join(response_parts)

    def generate_concise(self, message: CustomerMessage, kb_results: List[Dict]) -> str:
        """Generate a brief response optimized for chat channels like WhatsApp"""
        if not kb_results:
            return "I couldn't find info on that. Let me connect you with support."

        # Use the top result
        top_result = kb_results[0]

        # Extract just the most relevant sentence
        content = top_result["content"]
        sentences = [s.strip() for s in content.split('. ') if s.strip() and not s.startswith('-')]

        if not sentences:
            return "Let me help with that! Can you give me more details?"

        # Return just 1-2 key sentences for WhatsApp
        if "how" in message.content.lower():
            intro = "Here's how:"
        else:
            intro = "Quick answer:"

        main_content = '. '.join(sentences[:2]) + '.'

        # Keep it conversational and short
        return f"{intro} {main_content}"


# ============================================================================
# 8. RESPONSE FORMATTER - Format for different channels
# ============================================================================

class ResponseFormatter:
    """Format responses appropriately for each channel"""

    def format(self, message: CustomerMessage, content: str, escalation: Dict) -> str:
        """Format response based on channel"""
        if message.channel == "email":
            return self._format_email(message, content, escalation)
        elif message.channel == "whatsapp":
            return self._format_whatsapp(content, escalation)
        elif message.channel == "web_form":
            return self._format_web_form(message, content, escalation)
        else:
            return content

    def _format_email(self, message: CustomerMessage, content: str, escalation: Dict) -> str:
        """Email: Formal with greeting and signature"""
        parts = [
            f"Hi {message.customer_name},",
            "",
            content
        ]

        if escalation.get("escalate"):
            parts.extend(["", escalation["message"]])

        parts.extend([
            "",
            "Best regards,",
            "CRM Digital Support Team"
        ])

        return "\n".join(parts)

    def _format_whatsapp(self, content: str, escalation: Dict) -> str:
        """WhatsApp: Concise and conversational (no formal greeting/signature)"""
        if escalation.get("escalate"):
            # Shorter escalation messages for WhatsApp
            short_escalation = {
                "billing": "Connecting you with Billing team — they'll reply within 4 hrs.",
                "legal": "Forwarding to Legal team — they'll contact you shortly.",
                "security": "Escalating to Security team now — expect reply within 1 hr.",
                "outage": "Engineering team notified — investigating now.",
                "sla_risk": "Escalating to manager for faster resolution.",
                "no_knowledge_match": "Connecting you with a specialist.",
            }
            escalation_msg = short_escalation.get(
                escalation.get("reason"),
                "Connecting you with our support team."
            )
            return escalation_msg

        # Keep it short and casual for WhatsApp
        sentences = content.split('\n\n')
        short_content = sentences[0] if sentences else content

        # Limit length for WhatsApp
        if len(short_content) > 300:
            short_content = short_content[:297] + "..."

        return short_content

    def _format_web_form(self, message: CustomerMessage, content: str, escalation: Dict) -> str:
        """Web Form: Semi-formal and clear"""
        parts = [
            f"Hi {message.customer_name},",
            "",
            content
        ]

        if escalation.get("escalate"):
            parts.extend(["", escalation["message"]])

        parts.extend(["", "— CRM Digital Support"])

        return "\n".join(parts)


# ============================================================================
# 9. MAIN ORCHESTRATOR - Core customer interaction loop with memory
# ============================================================================

class CustomerSuccessAgent:
    """Main orchestrator for customer interactions with conversation memory"""

    def __init__(self, docs_path: str = "context/product-docs.md"):
        self.knowledge_base = SimpleKnowledgeBase(docs_path)
        self.escalation_engine = EscalationEngine()
        self.response_generator = ResponseGenerator()
        self.response_formatter = ResponseFormatter()
        self.conversation_memory = ConversationMemory()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.topic_extractor = TopicExtractor()

    def process_message(self, message: CustomerMessage) -> Dict[str, Any]:
        """
        Enhanced interaction loop with conversation memory:
        1. Retrieve/create conversation history
        2. Analyze sentiment and extract topics
        3. Search knowledge base (with context)
        4. Generate response
        5. Check escalation
        6. Format for channel
        7. Update conversation memory
        """
        print(f"\n{'='*80}")
        print(f"Processing: {message}")
        print(f"{'='*80}")

        # Step 0: Get or create conversation
        print("\n[0] Loading conversation context...")
        conversation = self.conversation_memory.get_or_create_conversation(
            message.customer_email,
            message.customer_name,
            message.customer_tier
        )

        if conversation.turns:
            print(f"    ✓ Existing conversation found ({len(conversation.turns)} previous turns)")
            print(f"    Topics: {', '.join(conversation.topics_discussed)}")
            if conversation.has_channel_switch():
                print(f"    ⚠ CHANNEL SWITCH: {conversation.original_channel} → {message.channel}")
        else:
            print(f"    ✓ New conversation started")

        # Step 1: Analyze sentiment and extract topics
        print("\n[1] Analyzing message...")
        sentiment_score = self.sentiment_analyzer.analyze(message.content)
        topics = self.topic_extractor.extract(message.content)

        sentiment_label = "Positive 😊" if sentiment_score >= 0.7 else "Negative 😞" if sentiment_score < 0.4 else "Neutral 😐"
        print(f"    Sentiment: {sentiment_label} (score: {sentiment_score:.2f})")
        print(f"    Topics: {', '.join(topics)}")

        # Step 2: Search knowledge base (could use context for better results)
        print("\n[2] Searching knowledge base...")
        # Enhance search query with context if available
        search_query = message.content
        if conversation.topics_discussed:
            # Add context from previous topics for better search
            context_topics = ' '.join(conversation.topics_discussed[-2:])
            search_query = f"{search_query} {context_topics}"

        kb_results = self.knowledge_base.search(search_query)

        if kb_results:
            print(f"    ✓ Found {len(kb_results)} relevant sections")
            for i, result in enumerate(kb_results, 1):
                print(f"      {i}. {result['title']} (score: {result['score']:.1f})")
        else:
            print("    ✗ No relevant results found")

        # Step 3: Check if escalation needed
        print("\n[3] Checking escalation rules...")
        escalation = self.escalation_engine.should_escalate(message, kb_results)

        if escalation.get("escalate"):
            print(f"    ⚠ ESCALATION NEEDED")
            print(f"      Reason: {escalation['reason']}")
            print(f"      Team: {escalation['team']}")
            print(f"      Priority: {escalation['priority']}")
        else:
            print("    ✓ Can handle with AI")

        # Step 4: Generate response
        print("\n[4] Generating response...")
        if escalation.get("escalate") and escalation["reason"] in ["billing", "legal", "security"]:
            # For critical escalations, keep response minimal
            response_content = escalation["message"]
        else:
            # Generate concise responses for WhatsApp, detailed for email
            if message.channel == "whatsapp":
                response_content = self.response_generator.generate_concise(message, kb_results)
            else:
                response_content = self.response_generator.generate(message, kb_results)

        # Step 5: Format for channel
        print(f"\n[5] Formatting for {message.channel}...")
        formatted_response = self.response_formatter.format(
            message, response_content, escalation
        )

        # Step 6: Update conversation memory
        print("\n[6] Updating conversation memory...")
        turn = ConversationTurn(
            customer_message=message,
            agent_response=formatted_response,
            kb_results=kb_results,
            escalated=escalation.get("escalate", False),
            sentiment_score=sentiment_score,
            topics=topics
        )
        conversation.add_turn(turn)

        # Update resolution status
        if escalation.get("escalate"):
            conversation.resolution_status = ResolutionStatus.ESCALATED
        elif kb_results and kb_results[0]["score"] > 5.0:
            conversation.resolution_status = ResolutionStatus.SOLVED
        else:
            conversation.resolution_status = ResolutionStatus.IN_PROGRESS

        print(f"    ✓ Conversation updated")
        print(f"    Status: {conversation.resolution_status.value}")
        print(f"    Average sentiment: {conversation.average_sentiment:.2f}")

        # Return complete result
        return {
            "message": message,
            "conversation": conversation,
            "kb_results": kb_results,
            "sentiment": sentiment_score,
            "topics": topics,
            "escalation": escalation,
            "response": formatted_response
        }

    def get_conversation_summary(self, customer_email: str) -> Optional[str]:
        """Get a summary of a customer's conversation"""
        conversation = self.conversation_memory.get_conversation(customer_email)
        if not conversation:
            return None

        return conversation.get_context_summary()

    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics"""
        return self.conversation_memory.get_conversation_stats()


# ============================================================================
# 10. DEMO / TEST - Enhanced with conversation memory
# ============================================================================

def run_demo():
    """Run demonstration with conversation memory and context tracking"""

    print("\n" + "="*80)
    print("CUSTOMER SUCCESS AI AGENT - ENHANCED PROTOTYPE DEMO")
    print("With Conversation Memory & Cross-Channel Tracking")
    print("="*80)

    # Initialize agent
    agent = CustomerSuccessAgent()

    # Sample test messages demonstrating conversation memory
    test_scenarios = [
        # Scenario 1: Sarah - Multi-turn conversation on same topic
        [
            CustomerMessage(
                channel="email",
                customer_email="sarah@company.com",
                customer_name="Sarah Johnson",
                customer_tier="Growth",
                subject="How to connect WhatsApp?",
                content="How do I connect WhatsApp to the FTE?"
            ),
            # Follow-up question in same channel
            CustomerMessage(
                channel="email",
                customer_email="sarah@company.com",
                customer_name="Sarah Johnson",
                customer_tier="Growth",
                subject="Re: How to connect WhatsApp?",
                content="Thanks! And where do I find the API credentials you mentioned?"
            ),
        ],

        # Scenario 2: Mike - Billing issue then channel switch
        [
            CustomerMessage(
                channel="whatsapp",
                customer_email="mike@startup.io",
                customer_name="Mike Chen",
                customer_tier="Growth",
                content="I see two charges for this month on my card. Can you check?"
            ),
            # Switches to email for detailed follow-up
            CustomerMessage(
                channel="email",
                customer_email="mike@startup.io",
                customer_name="Mike Chen",
                customer_tier="Growth",
                subject="Billing inquiry follow-up",
                content="Following up on my WhatsApp message. Can you send me an invoice breakdown?"
            ),
        ],

        # Scenario 3: David - Security escalation (single message)
        [
            CustomerMessage(
                channel="email",
                customer_email="david@enterprise.com",
                customer_name="David Martinez",
                customer_tier="Enterprise",
                subject="Unauthorized access concern",
                content="We suspect unauthorized access to our workspace — unfamiliar IP addresses."
            ),
        ],

        # Scenario 4: Emma - Happy customer, positive sentiment
        [
            CustomerMessage(
                channel="web_form",
                customer_email="emma@business.com",
                customer_name="Emma Wilson",
                customer_tier="Starter",
                content="Thanks for the great service! How do I upload training examples for the AI model?"
            ),
        ],
    ]

    # Process all scenarios
    for scenario_num, scenario_messages in enumerate(test_scenarios, 1):
        print(f"\n{'='*80}")
        print(f"SCENARIO {scenario_num}: {scenario_messages[0].customer_name}")
        print(f"{'='*80}")

        for msg_num, msg in enumerate(scenario_messages, 1):
            result = agent.process_message(msg)

            print(f"\n{'─'*80}")
            print(f"FINAL RESPONSE (Turn {msg_num}):")
            print(f"{'─'*80}")
            print(result["response"])
            print(f"{'─'*80}")

            if msg_num < len(scenario_messages):
                print(f"\n{'·'*80}\n")

    # Show overall statistics
    print("\n" + "="*80)
    print("OVERALL STATISTICS")
    print("="*80)
    stats = agent.get_stats()
    print(f"Total conversations: {stats['total_conversations']}")
    print(f"Total turns: {stats['total_turns']}")
    print(f"Average sentiment: {stats['avg_sentiment']:.2f}")
    print(f"Escalated: {stats['escalated_count']}")
    print(f"Solved: {stats['solved_count']}")
    print(f"Channel switches: {stats['channel_switches']}")
    print(f"Common topics: {', '.join(stats['common_topics'])}")

    # Show individual conversation summaries
    print("\n" + "="*80)
    print("CONVERSATION SUMMARIES")
    print("="*80)
    for conv in agent.conversation_memory.get_all_conversations():
        print(f"\n{conv.customer_name} ({conv.customer_email}):")
        print(f"  Channels: {', '.join(conv.channels_used)}")
        print(f"  Topics: {', '.join(conv.topics_discussed)}")
        print(f"  Status: {conv.resolution_status.value}")
        print(f"  Sentiment: {conv.average_sentiment:.2f}")
        print(f"  Turns: {len(conv.turns)}")

    print("\n" + "="*80)
    print("DEMO COMPLETE")
    print("="*80)


if __name__ == "__main__":
    run_demo()
