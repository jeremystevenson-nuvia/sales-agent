from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from core.db.mysql import AsyncSessionLocal
from core.models.highlevel import IsrLeadTouchpoint


router = APIRouter()


async def get_session() -> AsyncSession:
	async with AsyncSessionLocal() as session:
		yield session


def sa_to_dict(instance) -> Dict[str, Any]:
	return {col.name: getattr(instance, col.name) for col in instance.__table__.columns}


class WebhookPayload(BaseModel):
	contactId: str
	message: str


@router.post("/", response_model=Dict[str, Any])
async def receive_webhook(payload: WebhookPayload, session: AsyncSession = Depends(get_session)) -> Dict[str, Any]:
	contact_id = payload.contactId

	result = await session.execute(
		select(IsrLeadTouchpoint)
		.where(IsrLeadTouchpoint.contactId == contact_id)
		.order_by(IsrLeadTouchpoint.contactId)
	)
	items = result.scalars().all()
	serialized_items: List[Dict[str, Any]] = [sa_to_dict(i) for i in items]
	
	return {
		"contactId": contact_id,
		"count": len(serialized_items),
		"items": serialized_items,
	}


