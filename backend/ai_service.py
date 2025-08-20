import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from .database import User, Conversation, Message, UserMemory, memory_store

class AIService:
    """AI Service for generating responses with context retention"""
    
    def __init__(self):
        self.model_name = "gemini-pro"  # Would be configured for actual Gemini Pro
        
    async def generate_response(
        self,
        user_message: str,
        conversation_id: str,
        user_id: str,
        db: Session
    ) -> Dict:
        """Generate AI response with context awareness"""
        
        # Get user and conversation context
        user = db.query(User).filter(User.id == user_id).first()
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        
        # Build context
        context = await self._build_context(user, conversation, db)
        
        # Get recent messages for conversation context
        recent_messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.desc()).limit(10).all()
        
        # Prepare conversation history
        conversation_history = []
        for msg in reversed(recent_messages):
            conversation_history.append({
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            })
        
        # Generate response (simulated - would integrate with actual Gemini Pro)
        response = await self._generate_ai_response(
            user_message=user_message,
            context=context,
            conversation_history=conversation_history,
            user_preferences=user.preferences or {}
        )
        
        # Update memory stores
        await self._update_memory(user_id, conversation_id, user_message, response, db)
        
        return response
    
    async def _build_context(self, user: User, conversation: Conversation, db: Session) -> Dict:
        """Build comprehensive context for AI response"""
        
        context = {
            "user_profile": {
                "name": user.name,
                "preferences": user.preferences or {},
                "communication_style": user.preferences.get("communication_style", "casual") if user.preferences else "casual"
            },
            "conversation_context": {
                "title": conversation.title,
                "message_count": conversation.message_count,
                "summary": conversation.context_summary,
                "entities": conversation.context_entities or [],
                "topics": conversation.context_topics or []
            },
            "memory": {
                "short_term": {},
                "long_term": [],
                "semantic": []
            }
        }
        
        # Get short-term memory from Redis
        short_term_keys = ["current_topic", "user_intent", "session_context"]
        for key in short_term_keys:
            value = memory_store.get_short_term(str(user.id), key)
            if value:
                context["memory"]["short_term"][key] = value
        
        # Get long-term memory from database
        long_term_memories = db.query(UserMemory).filter(
            UserMemory.user_id == user.id,
            UserMemory.memory_type == "long_term"
        ).order_by(UserMemory.importance_score.desc()).limit(5).all()
        
        for memory in long_term_memories:
            context["memory"]["long_term"].append({
                "content": memory.content,
                "importance": memory.importance_score,
                "created_at": memory.created_at.isoformat()
            })
        
        # Get semantic memory
        semantic_memories = db.query(UserMemory).filter(
            UserMemory.user_id == user.id,
            UserMemory.memory_type == "semantic"
        ).order_by(UserMemory.importance_score.desc()).limit(3).all()
        
        for memory in semantic_memories:
            context["memory"]["semantic"].append({
                "content": memory.content,
                "importance": memory.importance_score
            })
        
        return context
    
    async def _generate_ai_response(
        self,
        user_message: str,
        context: Dict,
        conversation_history: List[Dict],
        user_preferences: Dict
    ) -> Dict:
        """Generate AI response (simulated - would integrate with Gemini Pro)"""
        
        # Simulate processing delay
        await asyncio.sleep(1.5)
        
        # Extract user preferences
        communication_style = user_preferences.get("communication_style", "casual")
        response_length = user_preferences.get("response_length", "medium")
        
        # Build response based on context and preferences
        if "hello" in user_message.lower() or "hi" in user_message.lower():
            if communication_style == "formal":
                base_response = f"Good day! How may I assist you today?"
            else:
                base_response = f"Hello there! How can I help you today?"
        elif "weather" in user_message.lower():
            base_response = "I'd be happy to help with weather information, but I don't have access to real-time weather data at the moment. You might want to check your local weather app or website for accurate conditions."
        elif "remember" in user_message.lower():
            base_response = "I have access to our conversation history and can remember context from our previous interactions. What would you like me to remember or recall?"
        elif any(topic in user_message.lower() for topic in ["ai", "artificial intelligence", "machine learning"]):
            if communication_style == "technical":
                base_response = "Artificial Intelligence encompasses machine learning algorithms, neural networks, and computational models designed to simulate human cognitive functions. What specific aspect would you like to explore?"
            else:
                base_response = "AI is fascinating! It's technology that can learn and make decisions similar to how humans think. What would you like to know about AI?"
        else:
            # Generic helpful response
            context_aware_intro = ""
            if context["conversation_context"]["topics"]:
                topics = context["conversation_context"]["topics"][:2]
                context_aware_intro = f"Building on our discussion about {', '.join(topics)}, "
            
            base_response = f"{context_aware_intro}I understand you're asking about '{user_message}'. Let me help you with that."
        
        # Adjust response length
        if response_length == "short":
            response_content = base_response.split('.')[0] + '.'
        elif response_length == "detailed":
            response_content = base_response + "\n\nWould you like me to elaborate on any particular aspect? I'm here to provide detailed explanations based on your preferences and our conversation history."
        else:
            response_content = base_response
        
        # Extract entities and topics for context updating
        entities = self._extract_entities(user_message)
        topics = self._extract_topics(user_message)
        
        return {
            "content": response_content,
            "confidence": 0.92,
            "context_used": True,
            "context": {
                "summary": f"User asked about: {user_message[:50]}...",
                "entities": entities,
                "topics": topics
            }
        }
    
    async def _update_memory(
        self,
        user_id: str,
        conversation_id: str,
        user_message: str,
        ai_response: Dict,
        db: Session
    ):
        """Update various memory stores"""
        
        # Update short-term memory in Redis
        current_topics = ai_response.get("context", {}).get("topics", [])
        if current_topics:
            memory_store.store_short_term(user_id, "current_topic", current_topics[0])
        
        # Determine user intent and store
        intent = self._analyze_intent(user_message)
        memory_store.store_short_term(user_id, "user_intent", intent)
        
        # Store conversation context
        context_data = {
            "last_message": user_message,
            "ai_response_summary": ai_response["content"][:100] + "...",
            "timestamp": datetime.utcnow().isoformat()
        }
        memory_store.store_conversation_context(conversation_id, context_data)
        
        # Update long-term memory if message is important
        importance = self._calculate_importance(user_message)
        if importance >= 7:  # High importance threshold
            long_term_memory = UserMemory(
                user_id=user_id,
                memory_type="long_term",
                content=f"User expressed: {user_message}",
                importance_score=importance,
                metadata={
                    "conversation_id": conversation_id,
                    "context": ai_response.get("context", {})
                }
            )
            db.add(long_term_memory)
            db.commit()
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text (simplified)"""
        entities = []
        
        # Simple entity extraction (would use NLP models in production)
        common_entities = ["weather", "time", "date", "location", "person", "ai", "technology"]
        for entity in common_entities:
            if entity in text.lower():
                entities.append(entity)
        
        return entities[:5]  # Limit to top 5
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text (simplified)"""
        topics = []
        
        # Simple topic extraction
        topic_keywords = {
            "technology": ["ai", "computer", "software", "tech", "digital"],
            "weather": ["weather", "temperature", "rain", "sunny", "cloudy"],
            "general": ["help", "question", "information", "explain"],
            "personal": ["remember", "preference", "like", "dislike", "favorite"]
        }
        
        text_lower = text.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics[:3]  # Limit to top 3
    
    def _analyze_intent(self, text: str) -> str:
        """Analyze user intent (simplified)"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["hello", "hi", "hey"]):
            return "greeting"
        elif any(word in text_lower for word in ["help", "how", "what", "explain"]):
            return "information_seeking"
        elif any(word in text_lower for word in ["remember", "recall", "previous"]):
            return "memory_retrieval"
        elif any(word in text_lower for word in ["thank", "thanks", "bye", "goodbye"]):
            return "closing"
        else:
            return "general_query"
    
    def _calculate_importance(self, text: str) -> int:
        """Calculate importance score for memory storage"""
        score = 1
        
        # Increase score for certain indicators
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["important", "remember", "crucial", "critical"]):
            score += 5
        elif any(word in text_lower for word in ["prefer", "like", "dislike", "favorite"]):
            score += 4
        elif any(word in text_lower for word in ["always", "never", "usually"]):
            score += 3
        elif len(text) > 100:  # Longer messages might be more important
            score += 2
        
        return min(score, 10)  # Cap at 10