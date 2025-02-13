# MSSiteWorkbookToolKit

`MSSiteWorkbookToolKit` is a Python module that provides asynchronous methods to interact with Excel workbooks hosted on SharePoint sites via the Microsoft Graph API. It allows you to perform various operations on workbooks such as listing worksheets, tables, retrieving table contents, updating cells, and more. Additionally, it integrates with tool builders for agent-based applications.

+ Note. This tool kit can only be used with worbooks. You need 'Tables' on your worksheets. Please check the example workbook at  `/General/Development/ERP System.xlsx` on site `Recall Space GmbH`.

## Features

- **List Worksheets in a Workbook**: Retrieve the names of all worksheets within a specified Excel workbook.
- **List Tables in a Worksheet**: Get the names of all tables within a specified worksheet of an Excel workbook.
- **Get Table Content**: Retrieve the content of a table in an Excel workbook formatted as markdown.
- **Get Table Row by Index**: Fetch a specific row from a table in an Excel workbook by its zero-based index.
- **List Files and Folders**: List the names of files and folders within a given path inside a SharePoint site's drive.
- **Apply Filter to Table**: Apply filters to a table column based on specified criteria.
- **Update Cells Values**: Update specific cells in a worksheet with new values.
- **Add Row to Table**: Add a new row with specified values to a table within a workbook.
- **Integration with Agent Tools**: Provides tool definitions compatible with agent builders for seamless integration.

## Prerequisites

- **Python 3.7 or higher**
- **Microsoft Graph SDK for Python**:
  - Install via pip: `pip install msgraph-sdk`
- **Pydantic** for data validation:
  - Install via pip: `pip install pydantic`
- **An Azure AD application with the following Microsoft Graph API permissions**:
  - `Sites.Read.All`
  - `Files.ReadWrite.All`
- **Agent Builder** (from `agent_builder.builders.tool_builder`), if integrating with agent-based applications.

## Installation

You can install `MSSiteWorkbookToolKit` via pip:

```bash
pip install mssiteworkbooktoolkit
```

## Example Usage


```python
from azure.identity import UsernamePasswordCredential
from msgraph import GraphServiceClient
from recall_space_agents.toolkits.ms_site_workbook.ms_site_workbook import MSSiteWorkbookToolKit

credentials = UsernamePasswordCredential(...)

ms_site_workbook_tool_kit = MSSiteWorkbookToolKit(credentials=credentials)
```

### Methods
```python
worksheets_in_workbook = await ms_site_workbook_tool_kit.alist_worksheets_in_workbook(
    site_display_name="Recall Space GmbH",
    file_path="/General/Development/ERP System.xlsx"
)

tables_in_worksheet= await ms_site_workbook_tool_kit.alist_tables_in_worksheet(
    file_path="/General/Development/ERP System.xlsx",
    site_display_name="Recall Space GmbH",
    worksheet_name="suppliermasterdata"
)

table_content = await ms_site_workbook_tool_kit.aget_table_content(
    site_display_name="Recall Space GmbH",
    file_path="/General/Development/ERP System.xlsx",
    worksheet_name="suppliermasterdata",
    table_name="SupplierMasterDataTable"
    )

cells_to_update = [
    {'cell_address': 'B2', 
     'cell_value': 'ACME 2 Inc.'}
     ]

await ms_site_workbook_tool_kit.aupdate_cells_values(
    site_display_name="Recall Space GmbH",
    file_path="/General/Development/ERP System.xlsx",
    worksheet_name="Supplier Master Data",
    cells_to_update=cells_to_update
)
```

## Example Usage with Agent Builder

```python
from azure.identity import UsernamePasswordCredential
from recall_space_agents.toolkits.ms_site_workbook.ms_site_workbook import MSSiteWorkbookToolKit
from agent_builder.builders.agent_builder import AgentBuilder
from langchain_openai import AzureChatOpenAI
import os
from langchain_core.messages import AIMessage, HumanMessage

credentials = UsernamePasswordCredential(...)

ms_site_workbook_tool_kit = MSSiteWorkbookToolKit(credentials=credentials)

ms_site_workbook_tools= ms_site_workbook_tool_kit.get_tools()



# Initialize LLM (Large Language Model)
llm = AzureChatOpenAI(
        base_url=os.getenv("AZURE_GPT4O_MINI_BASE_URL"),
        api_key=os.getenv("AZURE_GPT4O_MINI_KEY"),
        api_version=os.getenv("AZURE_GPT4O_MINI_API_VERSION"),
        temperature=0
    )

# Create an agent
agent_builder = AgentBuilder()
agent_builder.set_goal(
    """help the user"""
)
agent_builder.set_llm(llm)

for each_tool in ms_site_workbook_tools:
    agent_builder.add_tool(each_tool)
agent = agent_builder.build()

chat_history = []
user_input="hi"
reply = await agent.ainvoke(user_input, chat_history=chat_history)
user_input_schema = HumanMessage(user_input)
chat_history.append(user_input_schema)
chat_history.append(AIMessage(reply.get("output")))
```

```python
user_input = """
we will be working on site 'Recall Space GmbH' with file path '/General/Development/ERP System.xlsx'.
Please show me the worksheets on that file
"""
reply = await agent.ainvoke(user_input, chat_history=chat_history)
user_input_schema = HumanMessage(user_input)
chat_history.append(user_input_schema)
chat_history.append(AIMessage(reply.get("output")))

user_input = """
thanks, what tables are in suppliermasterdata sheet ?
"""
reply = await agent.ainvoke(user_input, chat_history=chat_history)
user_input_schema = HumanMessage(user_input)
chat_history.append(user_input_schema)
chat_history.append(AIMessage(reply.get("output")))

user_input = """
thanks, show me content of table SupplierMasterDataTable
"""
reply = await agent.ainvoke(user_input, chat_history=chat_history)
user_input_schema = HumanMessage(user_input)
chat_history.append(user_input_schema)
chat_history.append(AIMessage(reply.get("output")))

user_input = """
thanks, filter the table by column 'City' and value 'Springfield'. please include cell addresses as metadata
"""
reply = await agent.ainvoke(user_input, chat_history=chat_history)
user_input_schema = HumanMessage(user_input)
chat_history.append(user_input_schema)
chat_history.append(AIMessage(reply.get("output")))


user_input = """
nice, update the SupplierName from 'ACME 2 Inc.' to 'ACME 11 Inc.'
"""
reply = await agent.ainvoke(user_input, chat_history=chat_history)
user_input_schema = HumanMessage(user_input)
chat_history.append(user_input_schema)
chat_history.append(AIMessage(reply.get("output")))


user_input = """
thanks, add new row to the table. This is just a test, make up the values
"""
reply = await agent.ainvoke(user_input, chat_history=chat_history)
user_input_schema = HumanMessage(user_input)
chat_history.append(user_input_schema)
chat_history.append(AIMessage(reply.get("output")))
```