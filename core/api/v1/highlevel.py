from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.mysql import AsyncSessionLocal
from core.models.highlevel import GoHighLevelMessage, IsrLeadTouchpoint

router = APIRouter()


async def get_session() -> AsyncSession:
	async with AsyncSessionLocal() as session:
		yield session


def sa_to_dict(instance) -> Dict[str, Any]:
	return {col.name: getattr(instance, col.name) for col in instance.__table__.columns}


@router.get("/messages", response_model=List[Dict[str, Any]])
async def list_messages(limit: int = 50, offset: int = 0, session: AsyncSession = Depends(get_session)):
	result = await session.execute(
		select(GoHighLevelMessage).order_by(GoHighLevelMessage.createdAt.desc()).limit(limit).offset(offset)
	)
	items = result.scalars().all()
	return [sa_to_dict(i) for i in items]


@router.get("/messages/{message_id}", response_model=Dict[str, Any])
async def get_message(message_id: str, session: AsyncSession = Depends(get_session)):
	item = await session.get(GoHighLevelMessage, message_id)
	if not item:
		raise HTTPException(status_code=404, detail="Message not found")
	return sa_to_dict(item)


@router.post("/messages", response_model=Dict[str, Any])
async def create_message(payload: Dict[str, Any], session: AsyncSession = Depends(get_session)):
	item = GoHighLevelMessage(**payload)
	session.add(item)
	await session.commit()
	await session.refresh(item)
	return sa_to_dict(item)


@router.put("/messages/{message_id}", response_model=Dict[str, Any])
async def update_message(message_id: str, payload: Dict[str, Any], session: AsyncSession = Depends(get_session)):
	item = await session.get(GoHighLevelMessage, message_id)
	if not item:
		raise HTTPException(status_code=404, detail="Message not found")
	for key, value in payload.items():
		if key in item.__table__.columns.keys():
			setattr(item, key, value)
	await session.commit()
	await session.refresh(item)
	return sa_to_dict(item)


@router.delete("/messages/{message_id}")
async def delete_message(message_id: str, session: AsyncSession = Depends(get_session)):
	item = await session.get(GoHighLevelMessage, message_id)
	if not item:
		raise HTTPException(status_code=404, detail="Message not found")
	await session.delete(item)
	await session.commit()
	return {"ok": True}


@router.get("/touchpoints", response_model=List[Dict[str, Any]])
async def list_touchpoints(limit: int = 50, offset: int = 0, session: AsyncSession = Depends(get_session)):
	result = await session.execute(
		select(IsrLeadTouchpoint).order_by(IsrLeadTouchpoint.dateAdded.desc()).limit(limit).offset(offset)
	)
	items = result.scalars().all()
	return [sa_to_dict(i) for i in items]


@router.get("/touchpoint", response_model=Dict[str, Any])
async def get_touchpoint(
	dateAdded: datetime,
	locationId: str,
	contactId: str,
	type: str,
	context: str,
	session: AsyncSession = Depends(get_session),
):
	pk = {
		"dateAdded": dateAdded,
		"locationId": locationId,
		"contactId": contactId,
		"type": type,
		"context": context,
	}
	item = await session.get(IsrLeadTouchpoint, pk)
	if not item:
		raise HTTPException(status_code=404, detail="Touchpoint not found")
	return sa_to_dict(item)


@router.post("/touchpoints", response_model=Dict[str, Any])
async def create_touchpoint(payload: Dict[str, Any], session: AsyncSession = Depends(get_session)):
	item = IsrLeadTouchpoint(**payload)
	session.add(item)
	await session.commit()
	await session.refresh(item)
	return sa_to_dict(item)


@router.put("/touchpoint", response_model=Dict[str, Any])
async def update_touchpoint(
	dateAdded: datetime,
	locationId: str,
	contactId: str,
	type: str,
	context: str,
	payload: Dict[str, Any],
	session: AsyncSession = Depends(get_session),
):
	pk = {
		"dateAdded": dateAdded,
		"locationId": locationId,
		"contactId": contactId,
		"type": type,
		"context": context,
	}
	item = await session.get(IsrLeadTouchpoint, pk)
	if not item:
		raise HTTPException(status_code=404, detail="Touchpoint not found")
	for key, value in payload.items():
		if key in item.__table__.columns.keys():
			setattr(item, key, value)
	await session.commit()
	await session.refresh(item)
	return sa_to_dict(item)


@router.delete("/touchpoint")
async def delete_touchpoint(
	dateAdded: datetime,
	locationId: str,
	contactId: str,
	type: str,
	context: str,
	session: AsyncSession = Depends(get_session),
):
	pk = {
		"dateAdded": dateAdded,
		"locationId": locationId,
		"contactId": contactId,
		"type": type,
		"context": context,
	}
	item = await session.get(IsrLeadTouchpoint, pk)
	if not item:
		raise HTTPException(status_code=404, detail="Touchpoint not found")
	await session.delete(item)
	await session.commit()
	return {"ok": True}
