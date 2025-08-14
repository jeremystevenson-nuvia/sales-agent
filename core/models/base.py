from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class SerializedItem(BaseModel):
    dateAdded: Optional[datetime] = None
    locationId: Optional[str] = None
    contactId: Optional[str] = None
    type: Optional[str] = None
    direction: Optional[str] = None
    context: Optional[str] = None
    
class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    
class AIInput(BaseModel):
    contact_id: str
    agent_id: str
    contact_info: ContactInfo
    message: str
    data: List[SerializedItem]

class AIOutput(BaseModel):
    response_id: Optional[str] = None
    response_message: Optional[str] = None
    response_text: Optional[str] = None
    summary: Optional[str] = None
    next_step: Optional[str] = None
    appointment:Optional[int] = None
    total_token: Optional[int] = None
    error_message: Optional[str] = None
    


