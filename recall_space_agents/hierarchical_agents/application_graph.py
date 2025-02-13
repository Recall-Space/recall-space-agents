from langgraph.graph import MessagesState, START, StateGraph
from langgraph.types import Command
from typing import Literal

class ApplicationGraph:
    def __init__(self, supervisor):
        self.supervisor = supervisor
        self.workers = supervisor.workers
        self.graph = self._build_graph()

    def _build_graph(self):
        # Initialize the graph builder with the appropriate state
        builder = StateGraph(MessagesState)
        # Add the supervisor node to the graph
        builder.add_edge(START, "supervisor")
        
        # Dynamically add worker nodes to the graph
        fix_graph_expression = 'Command[Literal["__end__",'
        for _, worker in self.workers.items():
            builder.add_node(worker.agent_name, worker.get_worker_node)
            fix_graph_expression += f'"{worker.agent_name}",'
        fix_graph_expression += ']]'
        self.supervisor.supervisor_node.__annotations__["return"] = eval(fix_graph_expression)
        builder.add_node("supervisor", self.supervisor.supervisor_node)
        graph = builder.compile()
        return graph

    def get_compiled_graph(self):
        """
        Returns the compiled graph.
        """
        return self.graph

    async def application_node(self, state: dict):
        """
        Wraps the compiled graph's `ainvoke` method.

        Args:
            state (dict): The state containing the messages.

        Returns:
            The result of invoking the graph with the provided messages.
        """
        # Invoke the compiled graph with the messages
        response = await self.graph.ainvoke({"messages": state["messages"]})
        
        state["messages"] = state["messages"]+ response["messages"]
        return state