from typing import Any, Dict, List, Literal
import os

from fastapi import APIRouter, Depends, HTTPException, Body, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, constr

from core.db.mysql import AsyncSessionLocal
from core.models.base import AIInput, ContactInfo
from core.models.highlevel import IsrLeadTouchpoint
from ai.chats.service import answer_question
from core.models.mongo import Conversation




router = APIRouter()


async def get_session() -> AsyncSession:
	async with AsyncSessionLocal() as session:
		yield session


def sa_to_dict(instance) -> Dict[str, Any]:
	return {col.name: getattr(instance, col.name) for col in instance.__table__.columns}


class WebhookPayload(BaseModel):
	contactId: constr(strip_whitespace=True, min_length=1)
	type: Literal["email", "sms", "call"]
	message: constr(strip_whitespace=True, min_length=1)

	class Config:
		json_schema_extra = {
			"example": {
				"contactId": "****7MC2QjPkIuGt****",
				"type": "sms",
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
	},
	summary="Webhook endpoint with API token authentication.",
	description="""
**Authentication Required**: Set the `X-API-Token` header to access this endpoint.

**Test Token:**
```
X-API-Token: ZLiNX9XdhCYxThYFGcl0mDGnwhDR1VWwFTSXN1ju5nw
```
"""
)
async def receive_webhook(
	payload: WebhookPayload = Body(
		...,
		examples={
			"sample": {
				"summary": "Sample webhook request",
				"value": {
					"contactId": "****7MC2QjPkIuGt****",
					"type": "sms | email | call",
					"message": "I'm following up with my pereviuse request",
				},
			}
		},
	),
	session: AsyncSession = Depends(get_session),
	x_api_token: str = Header(None, alias="X-API-Token")
) -> Dict[str, Any]:
	# API Token Authentication
	api_token_env = os.getenv("API_TOKEN")
	if not x_api_token or x_api_token != api_token_env:
		raise HTTPException(status_code=401, detail="Invalid or missing API token.")
	# Defensive validation (Pydantic enforces too; this returns 400 with a clear message)
	
	invalid_fields: List[str] = []
	if not payload.contactId or not payload.contactId.strip():
		invalid_fields.append("contactId")
	if not payload.message or not payload.message.strip():
		invalid_fields.append("message")
	if payload.type not in ("email", "sms", "call"):
		invalid_fields.append("type")
	if invalid_fields:
		raise HTTPException(status_code=400, detail={
			"message": "Invalid or empty fields",
			"fields": invalid_fields,
		})
	
	contact_id = payload.contactId
	message = payload.message

	# After fetching serialized_items
	conversation = await Conversation.find_one({"contact_id": contact_id})
	response_id = conversation.response_id if conversation and conversation.response_id else None


	#if response id available we don't need to call db
	serialized_items = []
	if not response_id:
		result = await session.execute(
		select(IsrLeadTouchpoint)
		.where(IsrLeadTouchpoint.contactId == contact_id)
		.order_by(IsrLeadTouchpoint.dateAdded.desc())
		)
		items = result.scalars().all()
		serialized_items: List[Dict[str, Any]] = [sa_to_dict(i) for i in items]
		
	# Inputs
	ai_input = AIInput(
		contact_id=contact_id,
		agent_id='agent_1',
		response_id=response_id or "",
		contact_info=ContactInfo(name="John Doe", email="john@example.com", phone="123-456-7890"),
		message=message,
		data=serialized_items
	)
	response = answer_question(ai_input)

	# Save all relevant fields in Conversation collection
	if conversation:
		conversation.last_response = response.response_message
		conversation.response_id = response.response_id
		conversation.total_token = response.total_token if hasattr(response, 'total_token') else None
		conversation.metrics = None
		conversation.set_appointment = bool(response.appointment) if response.appointment is not None else False
		await conversation.save()
	else:
		conversation = Conversation(
			contact_id=contact_id,
			last_response=response.response_message,
			response_id=response.response_id,
			total_token=response.total_token if hasattr(response, 'total_token') else None,
			metrics=None,
			set_appointment=bool(response.appointment) if response.appointment is not None else False,
		)
		await conversation.insert()

	return {
		"contactId": contact_id,
		"responseId": response.response_id,
		"responseMessage": response.response_message,
		"appointment": response.appointment or 0,
		"nextStep": response.next_step or "",
		"summary": response.summary or ""
	}
