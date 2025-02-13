# 🚀Example: Open Purchase Orders.
+ Use a Hierarchical App to follow up on Open Purchase Orders.

```python
from azure.identity import UsernamePasswordCredential
from recall_space_agents.hierarchical_agents.realized_workers.email_manager import EmailManager
from recall_space_agents.hierarchical_agents.realized_workers.todo_manager import TodoManager
from recall_space_agents.hierarchical_agents.realized_workers.site_manager import SiteManager
from recall_space_agents.hierarchical_agents.realized_workers.site_workbook_manager import SiteWorkbookManager
import os
from langchain_openai import AzureChatOpenAI
from recall_space_agents.hierarchical_agents.supervisor import Supervisor
from recall_space_agents.hierarchical_agents.application_graph import ApplicationGraph
from zoneinfo import ZoneInfo
from datetime import datetime


credentials = UsernamePasswordCredential(...)

llm = AzureChatOpenAI(...)

## Application 1
# workers
email_manager = EmailManager(llm=llm, credentials=credentials)
todo_manager = TodoManager(llm=llm, credentials=credentials)

workers = [todo_manager, email_manager]

# Since this is a complex task, we need a plan.
supervisor = Supervisor(llm=llm, workers=workers, require_plan=True)
application_graph = ApplicationGraph(supervisor)

app = application_graph.get_compiled_graph()
```

+ The app is ready, let's command

```python
cet_tz = ZoneInfo('Europe/Paris')
today = datetime.now(cet_tz).date()

state = {
    "messages": [f"""
    Instructions:

    1. Extract Tasks Due Today:
    - Retrieve all the tasks from the TODO list titled "Open Purchase Orders" that are due today.

    2. Send Reminder Emails:
    - For each purchase order due today, send an email to the respective supplier.
    - The email should:
        - Include all available details of the purchase order.
        - Politely remind the supplier to send a confirmation.

    3. Update TODO List:
    - After sending the reminder:
        - Mark the corresponding purchase order task in the "Open Purchase Orders" TODO list as complete.
        - Create a new task in the "Open Purchase Orders" TODO list with the same title as the purchase order you just followed up on.
        - Set the due date of the new task to 3 days from now.
    Note. Today is {today} CTE.
    """,
    ],
    }
```

+ Stream the internal messages while the app works

```python
async for s in app.astream(state, stream_mode="values"):
    message = s["messages"][-1]
    if isinstance(message, tuple):
        print(message)
    else:
        message.pretty_print()
```


# 🚀Example: SiteWorkbookManager.

```python
from azure.identity import UsernamePasswordCredential
from recall_space_agents.hierarchical_agents.realized_workers.email_manager import EmailManager
from recall_space_agents.hierarchical_agents.realized_workers.site_workbook_manager import SiteWorkbookManager
import os
from langchain_openai import AzureChatOpenAI
from recall_space_agents.hierarchical_agents.supervisor import Supervisor
from recall_space_agents.hierarchical_agents.application_graph import ApplicationGraph

credentials = UsernamePasswordCredential(...)

# Initialize LLM (Large Language Model)
llm = AzureChatOpenAI(
        base_url=os.getenv("AZURE_GPT4O_BASE_URL"),
        api_key=os.getenv("AZURE_GPT4O_KEY"),
        api_version=os.getenv("AZURE_GPT4O_API_VERSION"),
        temperature=0
    )

# workers
email_manager = EmailManager(llm=llm, credentials=credentials)
site_workbook_manager = SiteWorkbookManager(llm=llm, credentials=credentials)
workers = [email_manager, site_workbook_manager]

# supervisor
supervisor = Supervisor(llm=llm, workers=workers)

# application graph
demo_application  = ApplicationGraph(supervisor).get_compiled_graph()

response = await demo_application.ainvoke(
    {
    "messages": [("user",
                  """
        Perform the following sequence
        1. Retrive the most recent email sent by 'user@example.com',
        2. Add a new row to the table 'SupplierMasterDataTable' with the content of email.
            here are the parameters:
            worksheet: 'suppliermasterdata'
            path : '/General/Development/ERP System.xlsx'
            site: 'Recall Space GmbH'
        
        The email might have partial information in relation to the table, make up
        the missing fields.
        """)]
    }
)
```