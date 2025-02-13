"""
This module defines the schema mappings for the Microsoft Graph To-Do functionality,
including the input schemas for creating, deleting, and managing to-do lists and tasks.

Classes:
    CreateTodoListInputSchema: Schema for creating a to-do list.
    DeleteTodoListInputSchema: Schema for deleting a to-do list.
    CreateTaskInputSchema: Schema for creating a task.
    DeleteTaskInputSchema: Schema for deleting a task.
    CompleteTaskInputSchema: Schema for completing a task.
    ListTasksInTodoListInputSchema: Schema for listing tasks in a to-do list by display name.

Variables:
    schema_mappings: A dictionary mapping method names to their descriptions and input schemas.
"""

from pydantic import BaseModel, Field


class CreateTodoListInputSchema(BaseModel):
    display_name: str = Field(..., description="Display name of the to-do list")


class DeleteTodoListInputSchema(BaseModel):
    todo_list_display_name: str = Field(
        default="",
        description="Display name of the todo list to delete. Required if 'todo_list_id' is not provided.",
    )
    todo_list_id: str = Field(
        default="",
        description="ID of the todo list to delete. Required if 'todo_list_display_name' is not provided.",
    )


class CreateTaskInputSchema(BaseModel):
    title: str = Field(description="Title of the task.")
    html_content: str = Field(default="", description="HTML content of the task.")
    linked_resource_list: list = Field(
        default_factory=list,
        description=(
            "List of linked resources. Each resource should be a dictionary with keys "
            "'web_url' and 'display_name'."
        ),
    )
    due_date: str = Field(
        default="",
        description="Due date of the task in 'YYYY-MM-DD' format, parsed to midday."
    )
    due_date_reminder: str = Field(
        default="",
        description="Reminder date of the task in 'YYYY-MM-DD' format, parsed to 8 a.m."
    )
    todo_list_display_name: str = Field(
        default="",
        description="Display name of the todo list. Required if 'todo_list_id' is not provided."
    )
    todo_list_id: str = Field(
        default="",
        description="ID of the todo list. Required if 'todo_list_display_name' is not provided."
    )
    categories_list: list = Field(
        default_factory=list,
        description="List of categories associated with the task."
    )


class DeleteTaskInputSchema(BaseModel):
    task_id: str = Field(
        default="",
        description="ID of the task to delete. Required if 'task_title' is not provided.",
    )
    task_title: str = Field(
        default="",
        description="Title of the task to delete. Required if 'task_id' is not provided.",
    )
    todo_list_display_name: str = Field(
        default="",
        description="Display name of the todo list. Required if 'todo_list_id' is not provided.",
    )
    todo_list_id: str = Field(
        default="",
        description="ID of the todo list. Required if 'todo_list_display_name' is not provided.",
    )


class CompleteTaskInputSchema(BaseModel):
    task_id: str = Field(
        default="",
        description="ID of the task to complete. Required if 'task_title' is not provided.",
    )
    task_title: str = Field(
        default="",
        description="Title of the task to complete. Required if 'task_id' is not provided.",
    )
    todo_list_display_name: str = Field(
        default="",
        description="Display name of the todo list containing the task. Required if 'todo_list_id' is not provided.",
    )
    todo_list_id: str = Field(
        default="",
        description="ID of the todo list containing the task. Required if 'todo_list_display_name' is not provided.",
    )

class ListTasksDueToday(BaseModel):
    pass  # No parameters needed

class ListTasksInTodoListInputSchema(BaseModel):
    todo_list_display_name: str = Field(..., description="Display name of the to-do list")

schema_mappings = {
    "acreate_todo_list": {
        "description": "Create a new to-do list with the specified display name.",
        "input_schema": CreateTodoListInputSchema,
    },
    "adelete_todo_list": {
        "description": "Delete a to-do list by its ID or display name.",
        "input_schema": DeleteTodoListInputSchema,
    },
    "acreate_task": {
        "description": "Create a new task with the specified details.",
        "input_schema": CreateTaskInputSchema,
    },
    "adelete_task": {
        "description": "Delete an existing task by its ID or title.",
        "input_schema": DeleteTaskInputSchema,
    },
    "acomplete_task": {
        "description": "Mark a task as completed by its ID or title.",
        "input_schema": CompleteTaskInputSchema,
    },
    "alist_tasks_due_today": {
        "description": "List all tasks that are due today.",
        "input_schema": ListTasksDueToday,
    },
    "alist_tasks_in_todo_list": {
        "description": "List all tasks in a given to-do list by display name.",
        "input_schema": ListTasksInTodoListInputSchema,
    },
}
