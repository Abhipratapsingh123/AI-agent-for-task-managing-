import sqlite3
import datetime
from typing import Optional, Dict, List, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


DB_PATH = "chat_tasks.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        title TEXT,
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT,
        sender TEXT,
        content TEXT,
        timestamp TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT,
        title TEXT,
        assigned_to TEXT,
        status TEXT,
        due_date TEXT,
        created_at TEXT,
        updated_at TEXT
    )""")
    conn.commit()
    conn.close()


# Inserting into conversation table
def create_conversation(conv_id: str, title: str = ""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.date.today().isoformat()
    c.execute("INSERT OR IGNORE INTO conversations VALUES (?, ?, ?)",
              (conv_id, title, now))
    conn.commit()
    conn.close()


# deleting the conversation
def delete_conversation(conv_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Deleting  all tasks associated with the conversation
    c.execute("DELETE FROM tasks WHERE conversation_id=?", (conv_id,))
    # Deleting  all messages associated with the conversation
    c.execute("DELETE FROM messages WHERE conversation_id=?", (conv_id,))
    # Finally, deleting the conversation itself
    c.execute("DELETE FROM conversations WHERE id=?", (conv_id,))
    # Even after deleting the task and messages counter starts from the previous chat, so we have to reset them for a new chat
    c.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")
    c.execute("DELETE FROM sqlite_sequence WHERE name='messages'")
    conn.commit()
    conn.close()


# adding messages to the messages table
def add_message(conv_id: str, sender: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    c.execute("INSERT INTO messages (conversation_id, sender, content, timestamp) VALUES (?, ?, ?, ?)", (conv_id, sender, content, now))
    conn.commit()
    conn.close()


# adding task to task table
def add_task(conv_id: str, title: str, assigned_to: str, status="OPEN", due_date: Optional[str] = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    c.execute("INSERT INTO tasks (conversation_id, title, assigned_to, status, due_date, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
              (conv_id, title, assigned_to, status, due_date, now, now))
    conn.commit()
    conn.close()

# updating the task


def update_task(task_id: int, status: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    c.execute("UPDATE tasks SET status=?, updated_at=? WHERE id=?",
              (status, now, task_id))
    conn.commit()
    conn.close()


# listing all the tasks
def list_tasks(conv_id: str) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id,title,assigned_to,status,due_date FROM tasks WHERE conversation_id=?", (conv_id,))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "assigned_to": r[2], "status": r[3], "due_date": r[4]} for r in rows]


def get_messages(conv_id: str) -> List[Dict]:
    """Retrieves all messages for a conversation for UI display."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT sender, content FROM messages WHERE conversation_id=? ORDER BY timestamp ASC", (conv_id,))
    rows = c.fetchall()
    conn.close()
    return [{"sender": r[0], "content": r[1]} for r in rows]


def get_langchain_history(conv_id: str) -> List[Any]:
    """Retrieves and formats all messages for the LangChain agent context."""
    # Start with the System prompt
    history = [SystemMessage(
        content="You are a helpful assistant who helps the user manage tasks. You can create, update, and list tasks based on the conversation.Be concise and direct in your responses.")]

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT sender, content FROM messages WHERE conversation_id=? ORDER BY timestamp ASC", (conv_id,))
    rows = c.fetchall()
    conn.close()

    for sender, content in rows:
        # Agent's replies should be AIMessages, others are HumanMessages
        if sender == "Agent":
            history.append(AIMessage(content=content))
        else:
            # Wrap Human/Employer messages in context for the Agent
            # The agent only sees this formatted message, not the bare text
            human_message_content = f"In conversation {conv_id}, {sender} said: '{content}'. If this is a task or update, handle it."
            history.append(HumanMessage(content=human_message_content))

    return history
