from fastapi.testclient import TestClient
from core.api.main import app
from core.api.v1 import highlevel as highlevel_module
from core.models.highlevel import GoHighLevelMessage, IsrLeadTouchpoint
from datetime import datetime

# Shared in-memory store across requests
_shared_store = {}


def _key_for(item):
	if hasattr(item, "id") and getattr(item, "id") is not None:
		return (item.__tablename__, getattr(item, "id"))
	return (
		item.__tablename__,
		(
			getattr(item, "dateAdded"),
			getattr(item, "locationId"),
			getattr(item, "contactId"),
			getattr(item, "type"),
			getattr(item, "context"),
		),
	)


class FakeResult:
	def __init__(self, items):
		self._items = items
	def scalars(self):
		return self
	def all(self):
		return self._items


class FakeSession:
	def __init__(self, store):
		self.store = store
	async def __aenter__(self):
		return self
	async def __aexit__(self, exc_type, exc, tb):
		return False
	async def execute(self, *_args, **_kwargs):
		# For list endpoints, return everything we have in store for that model
		# Simple union of all values
		return FakeResult([v for _, v in self.store.items()])
	async def get(self, model, pk):
		if isinstance(pk, dict):
			pk_tuple = (
				pk.get("dateAdded"), pk.get("locationId"), pk.get("contactId"), pk.get("type"), pk.get("context")
			)
			return self.store.get((model.__tablename__, pk_tuple))
		return self.store.get((model.__tablename__, pk))
	def add(self, item):
		self.store[_key_for(item)] = item
	async def commit(self):
		return None
	async def refresh(self, _item):
		return None
	async def delete(self, item):
		self.store.pop(_key_for(item), None)


async def fake_get_session():
	yield FakeSession(_shared_store)


# Override dependency
app.dependency_overrides[highlevel_module.get_session] = fake_get_session
client = TestClient(app)


def test_messages_crud_flow():
	# Create
	payload = {
		"id": "m-crud-1",
		"type": 1,
		"messageType": "sms",
		"locationId": "loc1",
		"contactId": "c-crud",
		"conversationId": "conv1",
		"dateAdded": "2025-01-01T00:00:00",
		"attachments": {},
		"createdAt": "2025-01-01T00:00:00",
		"updatedAt": "2025-01-01T00:00:00",
	}
	resp = client.post("/v1/highlevel/messages", json=payload)
	assert resp.status_code == 200
	# Read
	resp = client.get("/v1/highlevel/messages/m-crud-1")
	assert resp.status_code == 200
	assert resp.json()["id"] == "m-crud-1"
	# Update
	resp = client.put("/v1/highlevel/messages/m-crud-1", json={"status": "sent"})
	assert resp.status_code == 200
	assert resp.json()["status"] == "sent"
	# Delete
	resp = client.delete("/v1/highlevel/messages/m-crud-1")
	assert resp.status_code == 200
	# Verify 404 after delete
	resp = client.get("/v1/highlevel/messages/m-crud-1")
	assert resp.status_code == 404


def test_touchpoints_crud_flow():
	date_str = "2025-02-02T10:00:00"
	# Create
	payload = {
		"dateAdded": date_str,
		"locationId": "loc2",
		"contactId": "c-touch",
		"type": "call",
		"direction": "out",
		"context": "ctx2",
	}
	resp = client.post("/v1/highlevel/touchpoints", json=payload)
	assert resp.status_code == 200
	# Read
	params = {
		"dateAdded": date_str,
		"locationId": "loc2",
		"contactId": "c-touch",
		"type": "call",
		"context": "ctx2",
	}
	resp = client.get("/v1/highlevel/touchpoint", params=params)
	assert resp.status_code == 200
	assert resp.json()["contactId"] == "c-touch"
	# Update
	resp = client.put("/v1/highlevel/touchpoint", params=params, json={"direction": "in"})
	assert resp.status_code == 200
	assert resp.json()["direction"] == "in"
	# Delete
	resp = client.delete("/v1/highlevel/touchpoint", params=params)
	assert resp.status_code == 200
	# Verify 404 after delete
	resp = client.get("/v1/highlevel/touchpoint", params=params)
	assert resp.status_code == 404

