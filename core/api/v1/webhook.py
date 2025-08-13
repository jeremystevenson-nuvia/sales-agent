from typing import Any, Dict, List
import os

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from core.db.mysql import AsyncSessionLocal
from core.models.highlevel import IsrLeadTouchpoint
from ai.openai.service import OpenAI
from langchain_core.messages import SystemMessage, HumanMessage


router = APIRouter()


async def get_session() -> AsyncSession:
	async with AsyncSessionLocal() as session:
		yield session


def sa_to_dict(instance) -> Dict[str, Any]:
	return {col.name: getattr(instance, col.name) for col in instance.__table__.columns}


class WebhookPayload(BaseModel):
	contactId: str
	message: str

	class Config:
		schema_extra = {
			"example": {
				"contactId": "****7MC2QjPkIuGt****",
				"message": "I'm following up with my pereviuse request",
			}
		}	


@router.post(
	"/",
	response_model=Dict[str, Any],
	responses={
		200: {
			"content": {
				"application/json": {
					"example": {
						"contactId": "****7MC2QjPkIuGt****",
						"count": 1,
						"items": [
							{
								"dateAdded": "3647-04-23T22:47:00",
								"locationId": "***N2TKojvo570Wybj*",
								"contactId": "****7MC2QjPkIuGt****",
								"type": "appointment",
								"direction": "",
								"context": "Completed",
							}
						],
						"responseId": "resp_689cd75487ac81a29b60493a1adcde7c0c22361bf1af636c",
						"responseMessage": "Hello! I’m following up regarding your previous request. How can I assist you further today? If you'd like, I can give you a call in a couple of minutes to discuss this—please let me know if that works for you.",
					}
				}
			}
		}
	}
)
async def receive_webhook(
	payload: WebhookPayload = Body(
		...,
		examples={
			"sample": {
				"summary": "Sample webhook request",
				"value": {
					"contactId": "****7MC2QjPkIuGt****",
					"message": "I'm following up with my pereviuse request",
				},
			}
		},
	),
	session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
	contact_id = payload.contactId

	result = await session.execute(
		select(IsrLeadTouchpoint)
		.where(IsrLeadTouchpoint.contactId == contact_id)
		.order_by(IsrLeadTouchpoint.dateAdded.desc())
	)
	items = result.scalars().all()
	serialized_items: List[Dict[str, Any]] = [sa_to_dict(i) for i in items]

	response_id: str = ""
	response_message: str = ""

	# Skip AI during tests unless explicitly enabled
	disable_ai = os.getenv("DISABLE_AI", "0") == "1" or ("PYTEST_CURRENT_TEST" in os.environ and os.getenv("ENABLE_AI_IN_TESTS", "0") != "1")
	if not disable_ai:
		try:
			messages = [
				SystemMessage(content=(
					"You are a helpful sales assistant. Use the prior touchpoints to craft a concise, helpful reply. "
					"Keep it friendly and relevant."
					"Assume that we have the contact information already from previous interactions."
					"Your end goal is to ask for a confirmation to call them in a couple of minutes."
					"But be professional and productive and answer their questions first."
					"If they ask for a call, ask for a confirmation to call them in a couple of minutes."
				)),
				HumanMessage(content=(
					f"ContactId: {contact_id}\n"
					f"New message: {payload.message}\n"
					f"Touchpoints count: {len(serialized_items)}\n"
					f"Touchpoints: {serialized_items}"
				)),
			]
			llm = OpenAI()
			ai_output = llm.call(messages)
			response_id = getattr(ai_output, "response_id", "") or getattr(ai_output, "id", "")
			response_message = getattr(ai_output, "text", "")
		except Exception as _:
			# Swallow AI errors to keep webhook robust
			response_id = ""
			response_message = ""

	return {
		"contactId": contact_id,
		"count": len(serialized_items),
		"items": serialized_items,
		"responseId": response_id,
		"responseMessage": response_message,
	}


