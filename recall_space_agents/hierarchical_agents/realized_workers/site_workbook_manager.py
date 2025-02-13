"""
Module that defines the SiteWorkbookManager class, a worker that manages site workbook-related tasks.

This module provides the SiteWorkbookManager class, which extends the Worker class.
SiteWorkbookManager uses a language model and Microsoft Site Workbook Toolkit to perform
site workbook-related tasks as part of a hierarchical agent system.
"""

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

from recall_space_agents.hierarchical_agents.worker import Worker
from recall_space_agents.toolkits.ms_site_workbook.ms_site_workbook import MSSiteWorkbookToolKit
from typing import Literal

class SiteWorkbookManager(Worker):
    """SiteWorkbookManager class that handles site workbook-related tasks.

    The SiteWorkbookManager is a worker agent that uses a language model and site workbook tools
    to perform tasks like managing workbooks in Microsoft Sites, etc. It interacts with
    a supervisor agent in a hierarchical agent system.
    """

    def __init__(self, llm, credentials):
        """Initialize the SiteWorkbookManager with an LLM and credentials.

        Args:
            llm: The language model to use for processing messages.
            credentials: The credentials required for accessing site workbook tools.
        """
        self.llm = llm
        self.tools = MSSiteWorkbookToolKit(credentials=credentials).get_tools()
        self._agent_name = 'site_workbook_manager'
        self.system_prompt = f"You are a worker agent named {self._agent_name}"
        self.extracted_tool_description = "\n + ".join(
            [tool.description for tool in self.tools]
        )
        self.agent = create_react_agent(
            self.llm, 
            tools=self.tools, 
            state_modifier=self.system_prompt
        )

    @property
    def agent_name(self):
        """Get the name of the agent.

        Returns:
            str: The agent's name.
        """
        return self._agent_name

    async def get_worker_node(self, state: MessagesState) -> Command[Literal["supervisor"]]:
        """Process the worker node in the conversation graph.

        The worker processes the last message from the supervisor and responds accordingly.
        It is only aware of the supervisor's command, not the full state of messages.

        Args:
            state (MessagesState): The current state of the conversation messages.

        Returns:
            Command[str]: The command indicating the next agent (usually the supervisor)
            and any updates to the messages.
        """
        # Worker is only aware of the supervisor command, not the full state of messages.
        try:
            response = await self.agent.ainvoke(
                {"messages": [("user", state["messages"][-1].content)]}
            )
        except Exception as error:
            response = {"messages":[AIMessage(f"""
                execution failed due to the following error:
                {str(error)}
                Hint: Try to reformulate the task.
            """)]}
        # It responds as a Human, so that its answer is taken as priority.
        return Command(
            goto="supervisor",
            update={
                "messages": [
                    HumanMessage(
                        content=response["messages"][-1].content,
                        name=self.agent_name
                    )
                ]
            },
        )