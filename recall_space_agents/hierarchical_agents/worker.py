from abc import ABC, abstractmethod
from langgraph.graph import MessagesState
from langgraph.types import Command
from typing import Literal

class Worker(ABC):
    @abstractmethod
    async def get_worker_node(self, state: MessagesState) -> Command[Literal["supervisor"]]:
        pass

    @property
    @abstractmethod
    def agent_name(self) -> str:
        pass