from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import os

from Vector_setup.services.email_service import _send_email

router = APIRouter()

CONTACT_RECIPIENT = os.getenv("CONTACT_RECIPIENT", "specisaac@gmail.com")



class ContactIn(BaseModel):
    name: str
    email: EmailStr
    category: str
    message: str
    
@router.post("/contact")
def create_contact(payload: ContactIn):
    if not CONTACT_RECIPIENT:
        raise HTTPException(status_code=500, detail="Contact recipient not configured")
    
    subject = f"[CG Assistant] {payload.category.title()} - {payload.name}"
    html_body = f"""
        <p><strong>Name:</strong> {payload.name} </p>
        <p><strong>Email:</strong> {payload.email} </p>
        <p><strong>Category:</strong> {payload.category}</p>
        <p><strong>Message:</strong></p>
        <p>{payload.message.replace('\n', '<br/>')} </p>
    """
    try:
        # send to you vendor
        _send_email(CONTACT_RECIPIENT, subject, html_body)
    except Exception:
        raise HTTPException(status_code=500, detail="Could not send message")
    
    return {"detail": "Message sent"}