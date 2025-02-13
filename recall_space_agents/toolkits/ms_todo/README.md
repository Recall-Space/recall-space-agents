# MSTodoToolKit

MSTodoToolKit is a Python module designed for managing Microsoft To Do tasks and lists using the Microsoft Graph API. This toolkit allows users to create, delete, and manage tasks and to-do lists programmatically.

## Features

- Create and delete to-do lists
- Create, delete, and mark tasks as completed
- List tasks that are due today
- Support for linked resources and categories for tasks

## Usage as tools for agent

+ You need the agent builder package `pip install agent-builder==0.0.2`
+ ToolKit init
```python
from workflows.tookits.MSGraph.ms_todo import MSTodoTookKit
from azure.identity import UsernamePasswordCredential

credentials = UsernamePasswordCredential(
    client_id="", 
    authority="https://login.microsoftonline.com/", 
    tenant_id="",
    username="lisa.ai@recall.space",
    password="lisa's password")

ms_todo_tool_kit = MSTodoTookKit(credentials=credentials)

ms_todo_tools = ms_todo_tool_kit.get_tools()
```

+ Agent build
```python
from agent_builder.builders.agent_builder import AgentBuilder
from langchain_openai import AzureChatOpenAI

import os

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

for each_tool in ms_todo_tools:
    agent_builder.add_tool(each_tool)
agent = agent_builder.build()
```

```python
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

chat_history = []
user_input="hi"
reply = await agent.ainvoke(user_input, chat_history=chat_history)
user_input_schema = HumanMessage(user_input)
chat_history.append(user_input_schema)
chat_history.append(AIMessage(reply.get("output")))
```

```python
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

chat_history = []
user_input="hi"
reply = await agent.ainvoke(user_input, chat_history=chat_history)
user_input_schema = HumanMessage(user_input)
chat_history.append(user_input_schema)
chat_history.append(AIMessage(reply.get("output")))
```

```python
user_input = "Please create todo list named 'my-test-routine-3'"
reply = await agent.ainvoke(user_input, chat_history=chat_history)
user_input_schema = HumanMessage(user_input)
chat_history.append(user_input_schema)
chat_history.append(AIMessage(reply.get("output")))
```

```python
user_input = "Please add a task to read my book in the todo list 'my-test-routine-3' in 3 hours"
reply = await agent.ainvoke(user_input, chat_history=chat_history)
user_input_schema = HumanMessage(user_input)
chat_history.append(user_input_schema)
chat_history.append(AIMessage(reply.get("output")))
```

```python
user_input = "thanks. Please create a new todo list named 'personal-space'"
reply = await agent.ainvoke(user_input, chat_history=chat_history)
user_input_schema = HumanMessage(user_input)
chat_history.append(user_input_schema)
chat_history.append(AIMessage(reply.get("output")))
```

```python
user_input = "thanks. add a task 'good to the doctor' in 4 hours"
reply = await agent.ainvoke(user_input, chat_history=chat_history)
user_input_schema = HumanMessage(user_input)
chat_history.append(user_input_schema)
chat_history.append(AIMessage(reply.get("output")))
```

```python
chat_history=[]
user_input = "What are the current todos, give the due date times or remainders?"
reply = await agent.ainvoke(user_input, chat_history=chat_history)
user_input_schema = HumanMessage(user_input)
chat_history.append(user_input_schema)
chat_history.append(AIMessage(reply.get("output")))
```