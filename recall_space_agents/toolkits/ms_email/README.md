# MSEmailToolKit

`MSEmailToolKit` is a Python module that provides asynchronous methods to interact with Microsoft Exchange emails via the Microsoft Graph API. It allows you to retrieve unread emails, fetch the latest emails, and send emails from a user's mailbox. Additionally, it integrates with tool builders for agent-based applications.

## Features

- **Retrieve Emails**: Fetch a list of emails with options to limit, skip, and filter based on various criteria.
- **Send Emails**: Send emails with specified subject, body, and recipients.
- **Integration with Agent Tools**: Provides tool definitions compatible with agent builders for seamless integration.

## Prerequisites

- Python 3.7 or higher
- An Azure AD application with the following Microsoft Graph API permissions:
  - `Mail.Read`
  - `Mail.ReadWrite`
  - `Mail.Send`
- **Microsoft Graph SDK for Python**:
  - Install via pip: `pip install msgraph-sdk`
- **Pydantic** for data validation:
  - Install via pip: `pip install pydantic`
- **Agent Builder** (from `agent_builder.builders.tool_builder`), if integrating with agent-based applications.


## Usage

### Initialize the Toolkit

First, you need to initialize the `MSEmailToolKit` with the necessary credentials:

```python
from ms_email import MSEmailToolKit
from azure.identity import UsernamePasswordCredential

credentials = UsernamePasswordCredential(
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "tenant_id": "your_tenant_id",
    "username":"lisa.ai@recall.space",
    "password":"password")

email_toolkit = MSEmailToolKit(credentials=credentials)
```

### Retrieve Emails

To retrieve emails, you can use the `aget_emails` method:

```python
emails = await email_toolkit.aget_emails(limit=5, skip=0, filter="parentFolderId eq 'inbox' AND isRead eq false")
for email in emails:
    print(email)
```

### Send Emails

To send an email, you can use the `asend_email` method:

```python
response = await email_toolkit.asend_email(
    subject="Test Email",
    body_html="<p>This is a test email.</p>",
    to_recipients=["recipient@example.com"]
)
print(response)
```

### Get Tools

To retrieve a list of tools mapped to the methods in the toolkit:

```python
tools = email_toolkit.get_tools()
for tool in tools:
    print(tool)
```

## Schema Mappings

The schema mappings for the input parameters are defined in `schema_mappings.py`:

- **GetEmailsInputSchema**: Schema for retrieving emails with options to limit, skip, and filter.
- **SendEmailInputSchema**: Schema for sending an email with subject, body, and recipients.