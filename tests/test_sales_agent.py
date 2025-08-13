from fastapi.testclient import TestClient
from core.api.main import app
from core.db.mongo import client
from beanie import init_beanie
import asyncio
from core.models.mongo import Agent, UniversalRule, Conversation, Message

# Initialize a separate test database for Beanie
async def _init_test_db():
	db = client["salesdb_test"]
	await init_beanie(database=db, document_models=[Agent, UniversalRule, Conversation, Message])

asyncio.get_event_loop().run_until_complete(_init_test_db())

client_api = TestClient(app)


def test_agents_crud():
	# Create
	resp = client_api.post("/v1/sales-agent/agents", json={"name": "A1", "type": "bot"})
	assert resp.status_code == 200
	agent_id = resp.json()["id"]
	# Read
	resp = client_api.get(f"/v1/sales-agent/agents/{agent_id}")
	assert resp.status_code == 200
	# Update
	resp = client_api.put(f"/v1/sales-agent/agents/{agent_id}", json={"behavior": "friendly"})
	assert resp.status_code == 200
	assert resp.json()["behavior"] == "friendly"
	# List
	resp = client_api.get("/v1/sales-agent/agents")
	assert resp.status_code == 200 and isinstance(resp.json(), list)
	# Delete
	resp = client_api.delete(f"/v1/sales-agent/agents/{agent_id}")
	assert resp.status_code == 200


def test_universal_rules_crud():
	resp = client_api.post("/v1/sales-agent/universal-rules", json={"value": "Always be polite"})
	assert resp.status_code == 200
	rule_id = resp.json()["id"]
	resp = client_api.get("/v1/sales-agent/universal-rules")
	assert resp.status_code == 200 and isinstance(resp.json(), list)
	resp = client_api.delete(f"/v1/sales-agent/universal-rules/{rule_id}")
	assert resp.status_code == 200


def test_conversations_and_messages_crud():
	# Conversation
	conv = {
		"contact_id": "c1",
		"agent_ids": [],
		"last_response": None,
		"response_id": None,
		"total_token": 0,
	}
	resp = client_api.post("/v1/sales-agent/conversations", json=conv)
	assert resp.status_code == 200
	conv_id = resp.json()["id"]
	resp = client_api.get(f"/v1/sales-agent/conversations/{conv_id}")
	assert resp.status_code == 200
	# Messages
	msg = {"conversation_id": conv_id, "inbound": True, "outbound": False}
	resp = client_api.post("/v1/sales-agent/messages", json=msg)
	assert resp.status_code == 200
	msg_id = resp.json()["id"]
	# List messages
	resp = client_api.get(f"/v1/sales-agent/messages", params={"conversation_id": conv_id})
	assert resp.status_code == 200 and isinstance(resp.json(), list)
	# Delete message
	resp = client_api.delete(f"/v1/sales-agent/messages/{msg_id}")
	assert resp.status_code == 200
	# Cleanup conversation
	resp = client_api.delete(f"/v1/sales-agent/conversations/{conv_id}")
	assert resp.status_code == 200

