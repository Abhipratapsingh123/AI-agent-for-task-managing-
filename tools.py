from langchain.tools import tool
import db


@tool
def add_task_tool(conv_id: str, title: str, assigned_to: str, due_date: str = None) -> str:
    """Adds a new task to the database.
    This tool should be used when the user explicitly asks to create a task.
    Args:
        conv_id (str): The unique identifier for the conversation.
        title (str): A brief title for the task.
        assigned_to (str): The person to whom the task is assigned.
        due_date (str, optional): The due date of the task in YYYY-MM-DD format.
    Returns:
        str: A confirmation message that the task has been added."""
    db.add_task(conv_id, title, assigned_to, "OPEN", due_date)
    return f"Task added: {title} -> {assigned_to}"

@tool
def update_task_tool(task_id: int, status: str) -> str:
    """ Update the status of an existing task.

        Use this tool when the user explicitly asks to change the status of a task.

        Important:
        - Task IDs are auto-incremented within each conversation.
        - Do NOT ask the user for the task ID.
        - Instead, determine the correct task ID based on the order of tasks (e.g., the first task created has ID = 1, the next has ID = 2, and so on).

        Args:
            task_id (int): The unique auto-incremented ID of the task to update.
            status (str): The new status. Must be one of ['OPEN', 'INPR', 'DONE'].

        Returns:
            str: A confirmation message that the task was updated successfully.
        """
    db.update_task(task_id, status)
    return f"Task {task_id} updated to {status}"

@tool
def list_tasks_tool(conv_id: str) -> str:
    """Lists all tasks for a conversation.
    This tool should be used when the user explicitly asks to see a list of tasks.
    Args:
        conv_id (str): The unique identifier for the conversation.
    Returns:
        str: A formatted string of all tasks."""
    tasks = db.list_tasks(conv_id)
    if not tasks: return "No tasks yet."
    return "\n".join([f"[{t['id']}] {t['title']} ({t['status']}, {t['assigned_to']})" for t in tasks])

    