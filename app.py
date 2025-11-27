# app.py (Revised)

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from agent import get_agent
import db
import time # For the chat-like rerun

# --- App Initialization ---
st.set_page_config(page_title="AI Task Manager", layout="wide")
st.title("🤖 AI-Agent For Managing Task")
st.markdown("### Multi-User/Multi-Device Simulation")

# --- Database Setup ---
db.init_db()
conv_id = "conv1" # Static conversation ID for this demo
if "initialized" not in st.session_state:
    db.create_conversation(conv_id, "Streamlit Demo Chat")
    st.session_state.initialized = True
    
# --- Agent Setup ---
agent_executor = get_agent()

# --- Sidebar for Task Management ---
st.sidebar.header("📋 Task Controls")

if st.sidebar.button("🔄 List Tasks"):
    # Re-fetch the current history for context
    current_chat_history = db.get_langchain_history(conv_id)
    
    response = agent_executor.invoke({
        "input": f"List all tasks for conversation {conv_id}",
        "chat_history": current_chat_history
    })
    
    ai_reply = response["output"]
    db.add_message(conv_id, "Agent", ai_reply)
    st.sidebar.success(ai_reply)
    st.rerun() # Rerun to display new message

if st.sidebar.button("🗑️ Delete Chat"):
    db.delete_conversation(conv_id)
    st.sidebar.warning(f"Deleted chat for {conv_id}")
    st.session_state.initialized = False
    st.rerun() 

st.sidebar.markdown("---")
st.sidebar.info("Use the main chat to create or update tasks dynamically!")


# --- Chat Interface ---
st.subheader("💬 Chat Window")

# 1. READ ALL MESSAGES FROM DB FOR DISPLAY
all_messages = db.get_messages(conv_id) 

# Display chat messages
for msg in all_messages:
    if msg["sender"] == "You":
        st.chat_message("user").write(msg["content"])
    elif msg["sender"] == "Employer":
        st.chat_message("user").write(f" Employer: {msg['content']}")
    else: # Agent messages
        st.chat_message("assistant").write(f" Agent: {msg['content']}")

# --- Input Area ---
current_role = st.selectbox("I am speaking as:", ["You", "Employer"])
user_input = st.chat_input(f"Send a message as {current_role}")

if user_input:
    sender, text = current_role, user_input.strip()

    # 1. Add Human/Employer message to DB
    db.add_message(conv_id, sender, text)
    
    # 2. Get the full, updated history from DB for agent context
    current_chat_history = db.get_langchain_history(conv_id)
    
    # The last message is the HumanMessage we just added (the prompt for the agent)
    human_message_content = current_chat_history[-1].content
    
    # 3. Invoke the AI agent
    response = agent_executor.invoke({
        "input": human_message_content,
        "chat_history": current_chat_history
    })
    ai_reply = response["output"]

    # 4. Add Agent's reply to DB
    db.add_message(conv_id, "Agent", ai_reply)

    # 5. Auto-refresh to show both user message and agent response
    st.rerun()