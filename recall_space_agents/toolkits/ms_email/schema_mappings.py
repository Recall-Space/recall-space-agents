"""
This module defines the schema mappings for the Microsoft Graph email functionality,
including the input schemas for retrieving and sending emails.

Classes:
    GetEmailsInputSchema: Schema for retrieving emails with options to limit, skip, and filter.
    SendEmailInputSchema: Schema for sending an email with subject, body, and recipients.

Variables:
    method_mappings: A dictionary mapping method names to their descriptions and input schemas.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from textwrap import dedent

class GetEmailsInputSchema(BaseModel):
    limit: Optional[int] = Field(default=5, description="Number of emails to retrieve")
    skip: Optional[int] = Field(default=0, description="Number of emails to skip")
    filter: Optional[str] = Field(
        default="parentFolderId eq 'inbox'", 
        description=dedent("""
        OData filtering. For example: 
        1) Get unread emails from inbox 
            -> parentFolderId eq 'inbox' AND isRead eq false
        2) Get emails sent by Aniket
            -> contains(from/emailAddress/name, 'Aniket')
        3) Get emails sent by admin@recall.space
            -> from/emailAddress/address eq 'admin@recall.space'
        """))

class SendEmailInputSchema(BaseModel):
    subject: str = Field(..., description="Subject of the email")
    body_html: str = Field(..., description="HTML content of the email body")
    to_recipient: str = Field(
        ..., description="Recipient email addresses"
    )

class SendEmailByNameInputSchema(BaseModel):
    subject: str = Field(..., description="Subject of the email")
    body_html: str = Field(..., description="HTML content of the email body")
    to_recipient_by_name: str = Field(
        ..., description="Recipient name."
    )


schema_mappings = {
    "aget_emails": {
        "description": "Retrieve a list emails.",
        "input_schema": GetEmailsInputSchema,
    },
    "asend_email": {
        "description": "Send an email with the specified subject, body, and recipient.",
        "input_schema": SendEmailInputSchema,
    },
    "asend_email_by_name": {
        "description": "Send an email with the specified subject, body, and recipient's name.",
        "input_schema": SendEmailByNameInputSchema,
    },
}