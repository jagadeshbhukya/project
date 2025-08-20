import socketio
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio
import json

from .database import SessionLocal, User, Conversation, Message, memory_store
from .ai_service import AIService
from .config import settings

def setup_socket_handlers(sio: socketio.AsyncServer):
    """Setup WebSocket event handlers"""
    
    ai_service = AIService()
    
    async def get_user_from_token(token: str) -> User:
        """Authenticate user from JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email = payload.get("sub")
            if not email:
                return None
                
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.email == email).first()
                return user
            finally:
                db.close()
        except JWTError:
            return None
    
    @sio.event
    async def connect(sid, environ, auth):
        """Handle client connection"""
        if not auth or 'token' not in auth:
            await sio.disconnect(sid)
            return False
            
        user = await get_user_from_token(auth['token'])
        if not user:
            await sio.disconnect(sid)
            return False
            
        # Store user info in session
        await sio.save_session(sid, {'user_id': str(user.id), 'user_email': user.email})
        print(f"User {user.email} connected with session {sid}")
        return True
    
    @sio.event
    async def disconnect(sid):
        """Handle client disconnection"""
        session = await sio.get_session(sid)
        print(f"User {session.get('user_email', 'Unknown')} disconnected")
    
    @sio.event
    async def send_message(sid, data):
        """Handle incoming message from client"""
        try:
            session = await sio.get_session(sid)
            user_id = session.get('user_id')
            
            if not user_id:
                await sio.emit('error', {'message': 'User not authenticated'}, room=sid)
                return
            
            conversation_id = data.get('conversation_id')
            content = data.get('content')
            
            if not conversation_id or not content:
                await sio.emit('error', {'message': 'Missing conversation_id or content'}, room=sid)
                return
            
            db = SessionLocal()
            try:
                # Verify conversation ownership
                conversation = db.query(Conversation).filter(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id
                ).first()
                
                if not conversation:
                    await sio.emit('error', {'message': 'Conversation not found'}, room=sid)
                    return
                
                # Create user message
                user_message = Message(
                    content=content,
                    role='user',
                    conversation_id=conversation_id,
                    timestamp=datetime.utcnow()
                )
                
                db.add(user_message)
                db.commit()
                db.refresh(user_message)
                
                # Send user message confirmation
                await sio.emit('message_received', {
                    'id': str(user_message.id),
                    'content': user_message.content,
                    'role': user_message.role,
                    'timestamp': user_message.timestamp.isoformat(),
                    'conversation_id': str(user_message.conversation_id)
                }, room=sid)
                
                # Emit typing indicator
                await sio.emit('typing_indicator', {
                    'conversation_id': conversation_id,
                    'is_typing': True
                }, room=sid)
                
                # Get AI response
                start_time = datetime.utcnow()
                ai_response = await ai_service.generate_response(
                    user_message=content,
                    conversation_id=conversation_id,
                    user_id=user_id,
                    db=db
                )
                processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Create AI message
                ai_message = Message(
                    content=ai_response['content'],
                    role='assistant',
                    conversation_id=conversation_id,
                    timestamp=datetime.utcnow(),
                    metadata={
                        'processing_time': processing_time,
                        'confidence': ai_response.get('confidence', 0.9),
                        'context_used': ai_response.get('context_used', False)
                    }
                )
                
                db.add(ai_message)
                
                # Update conversation
                conversation.message_count += 2  # user + assistant
                conversation.updated_at = datetime.utcnow()
                
                # Update context if provided
                if ai_response.get('context'):
                    conversation.context_summary = ai_response['context'].get('summary')
                    conversation.context_entities = ai_response['context'].get('entities', [])
                    conversation.context_topics = ai_response['context'].get('topics', [])
                
                db.commit()
                db.refresh(ai_message)
                
                # Stop typing indicator
                await sio.emit('typing_indicator', {
                    'conversation_id': conversation_id,
                    'is_typing': False
                }, room=sid)
                
                # Send AI response
                await sio.emit('message_received', {
                    'id': str(ai_message.id),
                    'content': ai_message.content,
                    'role': ai_message.role,
                    'timestamp': ai_message.timestamp.isoformat(),
                    'conversation_id': str(ai_message.conversation_id),
                    'metadata': ai_message.metadata
                }, room=sid)
                
            finally:
                db.close()
                
        except Exception as e:
            print(f"Error in send_message: {e}")
            await sio.emit('error', {'message': 'An error occurred processing your message'}, room=sid)