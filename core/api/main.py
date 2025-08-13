from fastapi import FastAPI
from core.api.v1 import webhook
from core.api.v1 import highlevel
from core.api.v1 import sales_agent
from dotenv import load_dotenv
from beanie import init_beanie
from core.db.mongo import client, MONGO_DB
from core.models.mongo import Agent, UniversalRule, Conversation, Message

# Load .env for local/dev usage; in Docker, envs come from compose
load_dotenv()

app = FastAPI(title="Sales Agent API", version="1.0.0")


@app.on_event("startup")
async def startup_event():
	await init_beanie(database=client[MONGO_DB], document_models=[Agent, UniversalRule, Conversation, Message])


app.include_router(webhook.router, prefix="/v1/webhook", tags=["webhook"])
app.include_router(highlevel.router, prefix="/v1/highlevel", tags=["highlevel"])
app.include_router(sales_agent.router, prefix="/v1/sales-agent", tags=["sales-agent"])
