import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import ConsultationSession, ChatMessage, StudentProfile, User
from app.schemas import ChatMessageInput, ChatMessageOutput
from app.guardrails import validate_user_message
from app.gemini_service import generate_chat_response, stream_chat_response
from app.routers.auth import get_current_user_optional

router = APIRouter(prefix="/chat", tags=["Chatbot Core Engine"])


def _load_chat_context(db: Session, chat_input: ChatMessageInput, user_text: str):
    """Các bước chung của cả 2 endpoint: nạp phiên, lưu tin nhắn user, kiểm duyệt,
    nạp hồ sơ và lịch sử hội thoại. Trả về (session, guardrail_fail_msg_or_None, history, profile)."""
    session = db.query(ConsultationSession).filter(ConsultationSession.id == chat_input.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên tư vấn tương ứng!")

    user_msg_db = ChatMessage(
        session_id=session.id,
        role="user",
        content=user_text,
        mode=chat_input.mode
    )
    db.add(user_msg_db)
    db.commit()

    is_safe, category, feedback_msg = validate_user_message(user_text)
    if not is_safe:
        return session, feedback_msg, None, None

    profile_data = {}
    if session.profile and session.profile.raw_json:
        try:
            profile_data = json.loads(session.profile.raw_json)
        except Exception:
            pass

    past_messages_db = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.asc())
        .limit(10)
        .all()
    )
    formatted_history = [
        {"role": m.role, "content": m.content}
        for m in past_messages_db
    ]
    return session, None, formatted_history, profile_data


def _save_assistant_reply(db: Session, session: ConsultationSession, reply: str, mode: str) -> ChatMessage:
    ai_msg_db = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=reply,
        mode=mode
    )
    db.add(ai_msg_db)
    db.commit()
    db.refresh(ai_msg_db)
    return ai_msg_db

@router.post("/message", response_model=ChatMessageOutput)
async def send_chat_message(
    chat_input: ChatMessageInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Gửi tin nhắn hội thoại với Chatbot AI:
    - Kiểm duyệt Guardrails backend chống lạc đề
    - Nạp bối cảnh hồ sơ sinh viên
    - Hỗ trợ 4 chế độ: multidimensional | university_detail | market_trend | roleplay
    - Lưu vết lịch sử đa lượt (Multi-turn conversation)
    """
    user_text = chat_input.message.strip()
    session, guardrail_fail, formatted_history, profile_data = _load_chat_context(db, chat_input, user_text)

    # Guardrails chặn lạc đề / prompt injection -> phản hồi từ chối trực tiếp
    if guardrail_fail:
        ai_msg_db = _save_assistant_reply(db, session, guardrail_fail, chat_input.mode)
        return ChatMessageOutput(
            id=ai_msg_db.id,
            role=ai_msg_db.role,
            content=ai_msg_db.content,
            mode=ai_msg_db.mode,
            created_at=ai_msg_db.created_at
        )

    # Gọi AI với system prompt chỉ định
    ai_reply_text = await generate_chat_response(
        messages=formatted_history,
        profile_data=profile_data,
        mode=chat_input.mode,
        custom_api_key=chat_input.api_key
    )

    ai_msg_db = _save_assistant_reply(db, session, ai_reply_text, chat_input.mode)
    return ChatMessageOutput(
        id=ai_msg_db.id,
        role=ai_msg_db.role,
        content=ai_msg_db.content,
        mode=ai_msg_db.mode,
        created_at=ai_msg_db.created_at
    )


@router.post("/message/stream")
async def stream_chat_message(
    chat_input: ChatMessageInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Giống /message nhưng stream từng đoạn phản hồi theo SSE.
    Sự kiện: {"delta": "..."} cho từng đoạn text, {"done": true, "id": ...} khi kết thúc."""
    user_text = chat_input.message.strip()
    session, guardrail_fail, formatted_history, profile_data = _load_chat_context(db, chat_input, user_text)

    if guardrail_fail:
        ai_msg_db = _save_assistant_reply(db, session, guardrail_fail, chat_input.mode)
        guardrail_id, guardrail_mode = ai_msg_db.id, ai_msg_db.mode

        def guardrail_events():
            yield f'data: {json.dumps({"delta": guardrail_fail}, ensure_ascii=False)}\n\n'
            yield f'data: {json.dumps({"done": True, "id": guardrail_id, "mode": guardrail_mode})}\n\n'

        return StreamingResponse(guardrail_events(), media_type="text/event-stream",
                                 headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})

    async def event_generator():
        chunks = []
        async for text in stream_chat_response(
            messages=formatted_history,
            profile_data=profile_data,
            mode=chat_input.mode,
            custom_api_key=chat_input.api_key
        ):
            chunks.append(text)
            yield f'data: {json.dumps({"delta": text}, ensure_ascii=False)}\n\n'

        ai_msg_db = _save_assistant_reply(db, session, "".join(chunks), chat_input.mode)
        yield f'data: {json.dumps({"done": True, "id": ai_msg_db.id, "mode": ai_msg_db.mode})}\n\n'

    return StreamingResponse(event_generator(), media_type="text/event-stream",
                             headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})


@router.get("/session/{session_id}/messages", response_model=List[ChatMessageOutput])
def get_session_messages(session_id: int, db: Session = Depends(get_db)):
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return [
        ChatMessageOutput(
            id=m.id,
            role=m.role,
            content=m.content,
            mode=m.mode,
            created_at=m.created_at
        )
        for m in messages
    ]
