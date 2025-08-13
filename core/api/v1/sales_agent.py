from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.models.mongo import Agent, UniversalRule, Conversation, Message

router = APIRouter()


def serialize_doc(doc) -> Dict[str, Any]:
	if doc is None:
		return {}
	data = doc.model_dump()
	if getattr(doc, "id", None) is not None:
		data["id"] = str(doc.id)
	return data


# Agents CRUD
@router.get("/agents", response_model=List[Dict[str, Any]])
async def list_agents() -> List[Dict[str, Any]]:
	docs = await Agent.find().to_list()
	return [serialize_doc(d) for d in docs]


@router.get("/agents/{agent_id}", response_model=Dict[str, Any])
async def get_agent(agent_id: str) -> Dict[str, Any]:
	doc = await Agent.get(agent_id)
	if not doc:
		raise HTTPException(status_code=404, detail="Agent not found")
	return serialize_doc(doc)


@router.post("/agents", response_model=Dict[str, Any])
async def create_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
	doc = Agent(**payload)
	await doc.insert()
	return serialize_doc(doc)


@router.put("/agents/{agent_id}", response_model=Dict[str, Any])
async def update_agent(agent_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
	doc = await Agent.get(agent_id)
	if not doc:
		raise HTTPException(status_code=404, detail="Agent not found")
	for k, v in payload.items():
		setattr(doc, k, v)
	await doc.save()
	return serialize_doc(doc)


@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str) -> Dict[str, bool]:
	doc = await Agent.get(agent_id)
	if not doc:
		raise HTTPException(status_code=404, detail="Agent not found")
	await doc.delete()
	return {"ok": True}


# UniversalRules CRUD
@router.get("/universal-rules", response_model=List[Dict[str, Any]])
async def list_universal_rules() -> List[Dict[str, Any]]:
	docs = await UniversalRule.find().to_list()
	return [serialize_doc(d) for d in docs]


@router.post("/universal-rules", response_model=Dict[str, Any])
async def create_universal_rule(payload: Dict[str, Any]) -> Dict[str, Any]:
	doc = UniversalRule(**payload)
	await doc.insert()
	return serialize_doc(doc)


@router.delete("/universal-rules/{rule_id}")
async def delete_universal_rule(rule_id: str) -> Dict[str, bool]:
	doc = await UniversalRule.get(rule_id)
	if not doc:
		raise HTTPException(status_code=404, detail="Rule not found")
	await doc.delete()
	return {"ok": True}


# Conversations CRUD
@router.get("/conversations", response_model=List[Dict[str, Any]])
async def list_conversations() -> List[Dict[str, Any]]:
	docs = await Conversation.find().to_list()
	return [serialize_doc(d) for d in docs]


@router.get("/conversations/{conv_id}", response_model=Dict[str, Any])
async def get_conversation(conv_id: str) -> Dict[str, Any]:
	doc = await Conversation.get(conv_id)
	if not doc:
		raise HTTPException(status_code=404, detail="Conversation not found")
	return serialize_doc(doc)


@router.post("/conversations", response_model=Dict[str, Any])
async def create_conversation(payload: Dict[str, Any]) -> Dict[str, Any]:
	doc = Conversation(**payload)
	await doc.insert()
	return serialize_doc(doc)


@router.put("/conversations/{conv_id}", response_model=Dict[str, Any])
async def update_conversation(conv_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
	doc = await Conversation.get(conv_id)
	if not doc:
		raise HTTPException(status_code=404, detail="Conversation not found")
	for k, v in payload.items():
		setattr(doc, k, v)
	await doc.save()
	return serialize_doc(doc)


@router.delete("/conversations/{conv_id}")
async def delete_conversation(conv_id: str) -> Dict[str, bool]:
	doc = await Conversation.get(conv_id)
	if not doc:
		raise HTTPException(status_code=404, detail="Conversation not found")
	await doc.delete()
	return {"ok": True}


# Messages CRUD
@router.get("/messages", response_model=List[Dict[str, Any]])
async def list_messages(conversation_id: Optional[str] = None) -> List[Dict[str, Any]]:
	q = Message.find({}) if conversation_id is None else Message.find({"conversation_id": conversation_id})
	docs = await q.to_list()
	return [serialize_doc(d) for d in docs]


@router.get("/messages/{msg_id}", response_model=Dict[str, Any])
async def get_message(msg_id: str) -> Dict[str, Any]:
	doc = await Message.get(msg_id)
	if not doc:
		raise HTTPException(status_code=404, detail="Message not found")
	return serialize_doc(doc)


@router.post("/messages", response_model=Dict[str, Any])
async def create_message(payload: Dict[str, Any]) -> Dict[str, Any]:
	doc = Message(**payload)
	await doc.insert()
	return serialize_doc(doc)


@router.delete("/messages/{msg_id}")
async def delete_message(msg_id: str) -> Dict[str, bool]:
	doc = await Message.get(msg_id)
	if not doc:
		raise HTTPException(status_code=404, detail="Message not found")
	await doc.delete()
	return {"ok": True}

