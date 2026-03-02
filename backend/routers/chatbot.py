"""ChatBot Interface – conversational API for ticket creation and status queries."""
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models import Incident

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    intent: Optional[str] = None
    data: Optional[dict] = None


def _normalize(text: str) -> str:
    return text.strip().lower()


@router.post("", response_model=ChatResponse)
async def chat(
    body: ChatMessage,
    db: AsyncSession = Depends(get_db),
):
    """
    ChatBot endpoint: send a message and get a reply.
    Intents: create_ticket, status, list_incidents, help, greeting, default.
    """
    msg = _normalize(body.message)

    # Greeting
    if any(w in msg for w in ("hi", "hello", "hey")):
        return ChatResponse(
            reply="Hello! I can help you create a ticket, check status, or list incidents. Say 'create ticket', 'my tickets', or 'help'.",
            intent="greeting",
        )

    # Help
    if "help" in msg or "?" in msg:
        return ChatResponse(
            reply="You can say: 'create ticket &lt;title&gt;' to create an incident, 'my tickets' or 'list incidents' to see tickets, 'status &lt;id&gt;' for incident status.",
            intent="help",
        )

    # Create ticket
    if "create ticket" in msg or "create incident" in msg or "new ticket" in msg:
        title = msg.replace("create ticket", "").replace("create incident", "").replace("new ticket", "").strip()
        if not title:
            title = "Ticket from ChatBot"
        incident = Incident(
            title=title[:255],
            description=f"Created via ChatBot. User: {body.user_id or 'anonymous'}",
            source="chatbot",
            created_by=body.user_id or "chatbot",
        )
        db.add(incident)
        await db.commit()
        await db.refresh(incident)
        return ChatResponse(
            reply=f"Ticket created successfully. Incident ID: {incident.id}. You can track it in the Incidents page.",
            intent="create_ticket",
            data={"incident_id": incident.id, "title": incident.title},
        )

    # List incidents
    if ("list" in msg and "incident" in msg) or "my tickets" in msg or ("tickets" in msg and "create" not in msg):
        result = await db.execute(
            select(Incident).order_by(Incident.created_at.desc()).limit(10)
        )
        incidents = result.scalars().all()
        if not incidents:
            return ChatResponse(
                reply="You have no incidents yet.",
                intent="list_incidents",
                data={"count": 0},
            )
        lines = [f"• #{i.id}: {i.title} ({i.status.value})" for i in incidents]
        return ChatResponse(
            reply="Recent incidents:\n" + "\n".join(lines),
            intent="list_incidents",
            data={"count": len(incidents), "incidents": [{"id": i.id, "title": i.title, "status": i.status.value} for i in incidents]},
        )

    # Status by ID
    if "status" in msg:
        parts = msg.split()
        id_val = None
        for i, p in enumerate(parts):
            if p == "status" and i + 1 < len(parts) and parts[i + 1].isdigit():
                id_val = int(parts[i + 1])
                break
        if id_val is not None:
            result = await db.execute(select(Incident).where(Incident.id == id_val))
            inc = result.scalar_one_or_none()
            if inc:
                return ChatResponse(
                    reply=f"Incident #{inc.id}: {inc.title} — Status: {inc.status.value}, Priority: {inc.priority.value}.",
                    intent="status",
                    data={"id": inc.id, "status": inc.status.value, "priority": inc.priority.value},
                )
            return ChatResponse(reply=f"No incident found with ID {id_val}.", intent="status")

    # Default
    return ChatResponse(
        reply="I didn't understand. Say 'help' for options, or try 'create ticket &lt;title&gt;' or 'my tickets'.",
        intent="default",
    )
