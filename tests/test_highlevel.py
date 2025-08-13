from fastapi.testclient import TestClient
from core.api.main import app
from core.api.v1 import highlevel as highlevel_module
from core.models.highlevel import GoHighLevelMessage, IsrLeadTouchpoint
from datetime import datetime

class FakeResult:
	def __init__(self, items):
		self._items = items
	def scalars(self):
		return self
	def all(self):
		return self._items

class FakeSession:
	def __init__(self, items=None):
		self._items = items or []
		self._store = {}
	async def __aenter__(self):
		return self
	async def __aexit__(self, exc_type, exc, tb):
		return False
	async def execute(self, *_args, **_kwargs):
		return FakeResult(self._items)
	async def get(self, model, pk):
		return self._store.get((model.__tablename__, pk))
	def add(self, item):
		key = getattr(item, 'id', None) or tuple(getattr(item, k) for k in ['dateAdded','locationId','contactId','type','context'])
		self._store[(item.__tablename__, key)] = item
	async def commit(self):
		return None
	async def refresh(self, _item):
		return None
	async def delete(self, item):
		key = getattr(item, 'id', None) or tuple(getattr(item, k) for k in ['dateAdded','locationId','contactId','type','context'])
		self._store.pop((item.__tablename__, key), None)


async def fake_get_session():
	# seed with one message and one touchpoint
	session = FakeSession([
		GoHighLevelMessage(
			id='m1', type=1, messageType='sms', locationId='l1', contactId='c1', conversationId='cv1',
			dateAdded=datetime.utcnow(), attachments={}, createdAt=datetime.utcnow(), updatedAt=datetime.utcnow()
		),
		IsrLeadTouchpoint(
			dateAdded=datetime.utcnow(), locationId='l1', contactId='c1', type='call', direction='out', context='ctx'
		)
	])
	yield session


app.dependency_overrides[highlevel_module.get_session] = fake_get_session
client = TestClient(app)


def test_list_messages_ok():
	resp = client.get("/v1/highlevel/messages")
	assert resp.status_code == 200
	assert isinstance(resp.json(), list)


def test_list_touchpoints_ok():
	resp = client.get("/v1/highlevel/touchpoints")
	assert resp.status_code == 200
	assert isinstance(resp.json(), list)

