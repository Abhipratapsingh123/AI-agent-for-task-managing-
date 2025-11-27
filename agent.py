from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv

load_dotenv()

# Importing tools
from tools import add_task_tool, update_task_tool, list_tasks_tool


def get_agent():
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant who helps the user manage tasks. You can create, update, and list tasks based on the conversation.Be concise and direct in your responses."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    
    tools = [add_task_tool, update_task_tool, list_tasks_tool]

   
    agent = create_tool_calling_agent(llm, tools, prompt)

    
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    return agent_executor
