from agno.agent import Agent
from agno.team.team import Team
from agno.models.groq import Groq
from agno.tools.todoist import TodoistTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.tavily import TavilyTools

from prompts import jarvis_prompt, todo_prompt, web_prompt, memory_prompt, email_prompt
from memory_tools import MemoryToolkit
# from mymail import MyEmailTools
from utils import get_weather
from dotenv import load_dotenv
import json

from email_tools import read_last_emails, send_email

# Load environment variables
load_dotenv(override=True)

MODEL = "llama3-70b-8192"
# MODEL = "deepseek-r1-distill-llama-70b"
with open("user_data/user_info.txt", "r") as f:
    user_info = f.read()

with open("user_data/email_list.txt", "r") as f:
    email_list = f.read()

location = "Rabat"

todoist_agent = Agent(
    name="Todoist Agent",
    role="An AI assistant specialized in managing a Todoist task list.",
    instructions=todo_prompt,
    agent_id="todolist-agent",
    model=Groq(id=MODEL),
    tools=[TodoistTools(), ReasoningTools()],
    markdown=True,
    debug_mode=True,
    show_tool_calls=True,
)

email_agent = Agent(
    name="Email Agent",
    role="Sends and read emails using MyEmailTools",
    instructions=email_prompt +f"\n<contacts>{email_list}</contacts>",
    agent_id="email-agent",
    model=Groq(id=MODEL),
    tools=[read_last_emails, send_email],
    markdown=True,
    debug_mode=True,
    show_tool_calls=True,
)

web_agent = Agent(
    name="Web Agent",
    role="A specialized research assistant with access to web search and utility functions.",
    instructions=web_prompt + f"\nThe user is located in {location}.",
    agent_id="web-agent",
    model=Groq(id=MODEL),
    tools=[TavilyTools(), get_weather],
    markdown=True,
    debug_mode=True,
    show_tool_calls=True,
)

memory_agent = Agent(
    name="Memory Agent",
    role="Handles memory-related tasks and memory recall",
    agent_id="memory-agent",
    model=Groq(id=MODEL),
    tools=[MemoryToolkit()],
    instructions=memory_prompt,
    add_datetime_to_instructions=True,
)

team = Team(
    name="Jarvis",
    description="You are Jarvis, the sophisticated and quick-witted AI assistant from Iron Man.",
    instructions=jarvis_prompt+ f"\n<user_info>{user_info}</user_info>",
    mode="coordinate",
    model=Groq(id=MODEL),
    members=[todoist_agent, email_agent, web_agent],
    show_members_responses=True,
    markdown=True,
)

if __name__ == "__main__": 
    while (user_input := input("You: ")) not in ["exit", "quit", "q"]:
        
        memory = memory_agent.run(user_input)
        try:
            memory = json.loads(memory.content)
            if memory['recalled_memory']:
                prompt = f"<user_input>{user_input}</user_input>\n\n<retrived_memory>{memory['memory']}\n</retrived_memory>" 
            else:
                prompt = f"<user_input>{user_input}</user_input>"

        except json.JSONDecodeError:
            print(f"Memory response is not in JSON format: {memory.content}") 
            prompt = f"<user_input>{user_input}</user_input>"

        response = team.print_response(prompt)