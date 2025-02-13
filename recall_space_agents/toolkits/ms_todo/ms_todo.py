from textwrap import dedent
from dataclasses import asdict
from datetime import datetime, timedelta

from agent_builder.builders.tool_builder import ToolBuilder
from dateutil.parser import isoparse
from msgraph import GraphServiceClient
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.date_time_time_zone import DateTimeTimeZone
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.linked_resource import LinkedResource
from msgraph.generated.models.task_status import TaskStatus
from msgraph.generated.models.todo_task import TodoTask
from msgraph.generated.models.todo_task_list import TodoTaskList
from zoneinfo import ZoneInfo

from recall_space_agents.toolkits.ms_todo.schema_mappings import schema_mappings


class MSTodoToolKit:
    def __init__(self, credentials):
        self.required_scopes_as_user = ["APIConnectors.Read.All", "Tasks.ReadWrite"]
        self.ms_graph_client = GraphServiceClient(
            credentials=credentials, scopes=self.required_scopes_as_user
        )
        self.schema_mappings = schema_mappings

    async def acreate_todo_list(self, display_name: str) -> dict:
        check = await self._aget_todo_list_id_by_display_name(display_name)
        if check is None:
            todo_task_list = TodoTaskList(
                display_name=display_name,
            )
            todo_task_list_response = await self.ms_graph_client.me.todo.lists.post(
                todo_task_list
            )
            return asdict(todo_task_list_response)
        else:
            return f"the todo list with display name: {display_name} already exist."
        

    async def adelete_todo_list(
        self,
        todo_list_id: str = "",
        todo_list_display_name: str = "",
    ) -> dict:
        # Ensure that either 'todo_list_id' or 'todo_list_display_name' is provided
        assert (
            todo_list_id != "" or todo_list_display_name != ""
        ), "Must provide 'todo_list_id' or 'todo_list_display_name'."

        # If 'todo_list_id' is not provided, get it via display name
        if todo_list_id == "":
            todo_list_id = await self._aget_todo_list_id_by_display_name(
                todo_list_display_name
            )
            if not todo_list_id:
                raise ValueError(
                    f"Todo list with display name '{todo_list_display_name}' not found."
                )

        # Proceed to delete the to-do list
        await self.ms_graph_client.me.todo.lists.by_todo_task_list_id(
            todo_list_id
        ).delete()
        return {"status": "Todo list deleted successfully."}

    async def acreate_task(
        self,
        title: str,
        html_content: str = "",
        linked_resource_list: list = [],
        due_date: str = "",
        due_date_reminder: str = "",
        todo_list_display_name: str = "",
        todo_list_id: str = "",
        categories_list: list = [],
    ) -> str:
        assert (
            todo_list_id != "" or todo_list_display_name != ""
        ), "must provide todo_list_id or todo_list_display_name"

        if todo_list_id == "":
            todo_list_id = await self._aget_todo_list_id_by_display_name(
                todo_list_display_name
            )

        todo_task = TodoTask()
        todo_task.title = title

        if html_content != "":
            body = ItemBody(content=html_content, content_type=BodyType("html"))
            todo_task.body = body

        if len(linked_resource_list) > 0:
            linked_resource_list_object = []
            for each_linked_resource in linked_resource_list:
                linked_file = LinkedResource(
                    web_url=each_linked_resource.get("web_url"),
                    application_name="Sharepoint",
                    display_name=each_linked_resource.get("display_name"),
                )
                linked_resource_list_object.append(linked_file)
            todo_task.linked_resources = linked_resource_list_object

        if due_date != "":
            try:
                # Parse due_date string to datetime at 12:00 PM (midday)
                due_date_time = datetime.strptime(due_date, "%Y-%m-%d")
                due_date_time = due_date_time.replace(hour=12, minute=0, second=0)
                due_date_time_iso = due_date_time.isoformat()
                todo_task.due_date_time = DateTimeTimeZone(
                    date_time=due_date_time_iso, time_zone="UTC"
                )
            except ValueError:
                raise ValueError(
                    f"Invalid due_date format. Expected 'YYYY-MM-DD', got '{due_date}'"
                )

        if due_date_reminder != "":
            try:
                # Parse due_date_reminder string to datetime at 8:00 AM
                due_date_reminder_time = datetime.strptime(
                    due_date_reminder, "%Y-%m-%d"
                )
                due_date_reminder_time = due_date_reminder_time.replace(
                    hour=8, minute=0, second=0
                )
                due_date_reminder_time_iso = due_date_reminder_time.isoformat()
                todo_task.reminder_date_time = DateTimeTimeZone(
                    date_time=due_date_reminder_time_iso, time_zone="UTC"
                )
            except ValueError:
                raise ValueError(
                    f"Invalid due_date_reminder format. Expected 'YYYY-MM-DD', got '{due_date_reminder}'"
                )

        if len(categories_list) > 0:
            todo_task.categories = categories_list
        todo_task_response = (
            await self.ms_graph_client.me.todo.lists.by_todo_task_list_id(
                todo_list_id
            ).tasks.post(todo_task)
        )

        formatted_task = self._format_task(todo_task_response)
        return formatted_task

    async def adelete_task(
        self,
        task_id: str = "",
        task_title: str = "",
        todo_list_display_name: str = "",
        todo_list_id: str = "",
    ) -> dict:
        # Ensure that either todo_list_id or todo_list_display_name is provided
        assert (
            todo_list_id != "" or todo_list_display_name != ""
        ), "Must provide 'todo_list_id' or 'todo_list_display_name'."

        # Ensure that either task_id or task_title is provided
        assert (
            task_id != "" or task_title != ""
        ), "Must provide 'task_id' or 'task_title'."

        # If todo_list_id is not provided, get it via display name
        if todo_list_id == "":
            todo_list_id = await self._aget_todo_list_id_by_display_name(
                todo_list_display_name
            )
            if not todo_list_id:
                raise ValueError(
                    f"Todo list with display name '{todo_list_display_name}' not found."
                )

        # If task_id is not provided, get it via task title
        if task_id == "":
            task_id = await self._aget_task_id_by_title(todo_list_id, task_title)
            if not task_id:
                raise ValueError(
                    f"Task with title '{task_title}' not found in todo list."
                )

        # Proceed to delete the task
        await self.ms_graph_client.me.todo.lists.by_todo_task_list_id(
            todo_list_id
        ).tasks.by_todo_task_id(task_id).delete()
        return {"status": "Task deleted successfully."}

    async def acomplete_task(
        self,
        task_id: str = "",
        task_title: str = "",
        todo_list_display_name: str = "",
        todo_list_id: str = "",
    ) -> str:
        # Ensure that either 'todo_list_id' or 'todo_list_display_name' is provided
        assert (
            todo_list_id != "" or todo_list_display_name != ""
        ), "Must provide 'todo_list_id' or 'todo_list_display_name'."

        # Ensure that either 'task_id' or 'task_title' is provided
        assert (
            task_id != "" or task_title != ""
        ), "Must provide 'task_id' or 'task_title'."

        # If 'todo_list_id' is not provided, get it via display name
        if todo_list_id == "":
            todo_list_id = await self._aget_todo_list_id_by_display_name(
                todo_list_display_name
            )
            if not todo_list_id:
                raise ValueError(
                    f"Todo list with display name '{todo_list_display_name}' not found."
                )

        # If 'task_id' is not provided, get it via task title
        if task_id == "":
            task_id = await self._aget_task_id_by_title(todo_list_id, task_title)
            if not task_id:
                raise ValueError(
                    f"Task with title '{task_title}' not found in todo list."
                )

        # Update the task status to 'completed'
        todo_task_update = TodoTask(status=TaskStatus("completed"))

        # Proceed to update the task
        updated_task = (
            await self.ms_graph_client.me.todo.lists.by_todo_task_list_id(todo_list_id)
            .tasks.by_todo_task_id(task_id)
            .patch(todo_task_update)
        )

        formatted_task = self._format_task(updated_task)
        return formatted_task

    async def alist_tasks_due_today(self) -> str:
        formatted_tasks = ""
        cet_tz = ZoneInfo('Europe/Paris')  # Change to your specific CET time zone if needed
        today = datetime.now(cet_tz).date()

        # Get all todo lists
        todo_lists_response = await self.ms_graph_client.me.todo.lists.get()
        for todo_list in todo_lists_response.value:
            # Get tasks in each list
            tasks_response = (
                await self.ms_graph_client.me.todo.lists.by_todo_task_list_id(
                    todo_list.id
                ).tasks.get()
            )
            for task in tasks_response.value:
                if task.due_date_time and task.due_date_time.date_time:
                    due_date_time_str = task.due_date_time.date_time
                    due_date_time_zone_str = task.due_date_time.time_zone or 'UTC'
                    try:
                        # Parse the date string
                        due_date_naive = isoparse(due_date_time_str)

                        # Attach timezone from the task's due date
                        due_date_time_zone = ZoneInfo(due_date_time_zone_str)
                        due_date = due_date_naive.replace(tzinfo=due_date_time_zone)

                        # Convert due_date to CET
                        due_date_cet = due_date.astimezone(cet_tz)
                    except ValueError:
                        # Handle parsing or time zone errors
                        continue

                    # Compare the date part only
                    if due_date_cet.date() == today:
                        formatted_task = self._format_task(task)
                        formatted_tasks += formatted_task
        return dedent(formatted_tasks)

    async def alist_tasks_in_todo_list(self, todo_list_display_name: str) -> str:
        # Get the todo list ID from the display name
        todo_list_id = await self._aget_todo_list_id_by_display_name(todo_list_display_name)

        if not todo_list_id:
            raise ValueError(f"Todo list with display name '{todo_list_display_name}' not found.")

        # Get the tasks in the specified todo list
        tasks_response = await self.ms_graph_client.me.todo.lists.by_todo_task_list_id(todo_list_id).tasks.get()

        tasks = tasks_response.value

        # Build a nicely formatted string containing task details
        formatted_tasks = ""
        for task in tasks:
            formatted_task = self._format_task(task)
            formatted_tasks += formatted_task
        return dedent(formatted_tasks)

    async def _aget_task_id_by_title(self, todo_list_id: str, task_title: str) -> str:
        # Get the tasks in the specified todo list
        tasks_response = await self.ms_graph_client.me.todo.lists.by_todo_task_list_id(
            todo_list_id
        ).tasks.get()

        # Filter for the desired task title
        task_id = next(
            (task.id for task in tasks_response.value if task.title == task_title), None
        )
        return task_id

    async def _aget_todo_list_id_by_display_name(self, display_name) -> str:
        todo_task_list_lists = await self.ms_graph_client.me.todo.lists.get()

        # Filter for the desired display name
        todo_task_list_id = next(
            (
                task_list.id
                for task_list in todo_task_list_lists.value
                if task_list.display_name == display_name
            ),
            None,
        )
        return todo_task_list_id

    def get_tools(self):
        """
        Retrieve a list of tools mapped to the methods in the toolkit.

        Returns:
            list: A list of ToolBuilder objects, each representing a method in the toolkit.
        """
        tools = []
        for each_method_key, each_method_value in self.schema_mappings.items():
            tool_builder = ToolBuilder()
            tool_builder.set_name(name=each_method_key)
            tool_builder.set_function(eval(f"self.{each_method_key}"))
            tool_builder.set_coroutine(eval(f"self.{each_method_key}"))
            tool_builder.set_description(description=each_method_value["description"])
            tool_builder.set_schema(schema=each_method_value["input_schema"])
            tool_builder = tool_builder.build()
            tools.append(tool_builder)
        return tools

    def _format_task(self, task: TodoTask) -> str:
        """Format a task object into a nicely formatted string with due date in CET."""
        cet_tz = ZoneInfo('Europe/Paris')  # Central European Time

        # Extract task properties, handling None values
        title = task.title if task.title else 'No Title'
        body_content = f"{task.body.content}" if task.body and task.body.content else 'No Content'

        # Process due date to convert to CET
        if task.due_date_time and task.due_date_time.date_time:
            due_date_time_str = task.due_date_time.date_time
            due_date_time_zone_str = task.due_date_time.time_zone or 'UTC'
            try:
                # Parse the date string
                due_date_naive = isoparse(due_date_time_str)

                # Attach timezone from the task's due date
                due_date_time_zone = ZoneInfo(due_date_time_zone_str)
                due_date = due_date_naive.replace(tzinfo=due_date_time_zone)

                # Convert due_date to CET
                due_date_cet = due_date.astimezone(cet_tz)
                due_date_formatted = due_date_cet.strftime('%Y-%m-%d %H:%M:%S %Z')
            except ValueError:
                # Handle parsing or time zone errors
                due_date_formatted = 'Invalid Due Date'
        else:
            due_date_formatted = 'No Due Date'

        # Process completed date
        if task.completed_date_time and task.completed_date_time.date_time:
            completed_date_time_str = task.completed_date_time.date_time
            completed_date_time_zone_str = task.completed_date_time.time_zone or 'UTC'
            try:
                # Parse the date string
                completed_date_naive = isoparse(completed_date_time_str)

                # Attach timezone from the task's completed date
                completed_date_time_zone = ZoneInfo(completed_date_time_zone_str)
                completed_date = completed_date_naive.replace(tzinfo=completed_date_time_zone)

                # Convert completed_date to CET
                completed_date_cet = completed_date.astimezone(cet_tz)
                completed_date_formatted = completed_date_cet.strftime('%Y-%m-%d %H:%M:%S %Z')
            except ValueError:
                # Handle parsing or time zone errors
                completed_date_formatted = 'Invalid Completed Date'
        else:
            completed_date_formatted = 'Not Completed'

        status = task.status.value if task.status else 'No Status'

        # Format attachments
        if task.attachments:
            attachments = ', '.join([attachment.name for attachment in task.attachments])
        else:
            attachments = 'No Attachments'

        # Format linked resources
        if task.linked_resources:
            linked_resources = ', '.join([resource.web_url for resource in task.linked_resources])
        else:
            linked_resources = 'No Linked Resources'

        # Format the task details
        formatted_task = dedent(f"""
        # Title: {title}
        Due Date: {due_date_formatted}
        Completed Date: {completed_date_formatted}
        Status: {status}
        Body: 
        ```
        {body_content}
        ```
        Attachments: {attachments}
        Linked Resources: {linked_resources}
        {'-'*40}
        """)

        return formatted_task