import pytest
from fastapi.testclient import TestClient
from types import SimpleNamespace
from unittest.mock import patch, AsyncMock

from core.api.main import app
from core.api.v1 import webhook as webhook_module
from core.models.highlevel import IsrLeadTouchpoint


class FakeResult:
	def __init__(self, items):
		self._items = items
	def scalars(self):
		return self
	def all(self):
		return self._items


class FakeSession:
	def __init__(self, items):
		self._items = items
	async def __aenter__(self):
		return self
	async def __aexit__(self, exc_type, exc, tb):
		return False
	async def execute(self, *_args, **_kwargs):
		return FakeResult(self._items)


async def fake_get_session():
	items = [
		IsrLeadTouchpoint(
			dateAdded=__import__('datetime').datetime.utcnow(),
			locationId='loc1',
			contactId='c1',
			type='call',
			direction='in',
			context='ctx',
		)
	]
	yield FakeSession(items)


app.dependency_overrides[webhook_module.get_session] = fake_get_session
client = TestClient(app)


@patch('core.api.v1.webhook.Agent')
def test_webhook_returns_touchpoints_by_contact(mock_agent):
    # Mock the Agent.find_one to return a fake agent
    mock_agent_instance = SimpleNamespace()
    mock_agent_instance.id = "agent_123"
    mock_agent.find_one = AsyncMock(return_value=mock_agent_instance)
    
    payload = {"contactId": "c1", "type": "sms", "message": "hello"}
    resp = client.post("/v1/webhook/", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["contactId"] == "c1"
    assert "responseId" in data
    assert "responseMessage" in data
