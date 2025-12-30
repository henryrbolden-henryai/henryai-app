"""Network/Outreach Pydantic models"""

from typing import List
from pydantic import BaseModel, Field


class Contact(BaseModel):
    name: str
    company: str
    title: str
    relationship: str


class NetworkRecommendRequest(BaseModel):
    company: str
    role_title: str
    contacts: List[Contact]


class ContactRecommendation(BaseModel):
    name: str
    company: str
    title: str
    relationship: str
    priority: int = Field(ge=1, le=3)
    reason: str
    suggested_message_stub: str


class NetworkRecommendResponse(BaseModel):
    recommendations: List[ContactRecommendation]
