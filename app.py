import streamlit as st
from agno.agent import Agent
from agno.team.team import Team
from agno.models.groq import Groq
from agno.models.openrouter import OpenRouter
from agno.tools.todoist import TodoistTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.tavily import TavilyTools
from memory_tools import MemoryToolkit
from email_tools import read_last_emails, send_email
from utils import get_weather
from prompts import jarvis_prompt, todo_prompt, web_prompt, memory_prompt, email_prompt
from dotenv import load_dotenv
import json

def initialize_team(user_info, email_list, location, provider, model):
    load_dotenv()
    
    # Select the appropriate model provider
    ModelProvider = Groq if provider == "groq" else OpenRouter
    
    todoist_agent = Agent(
        name="Todoist Agent",
        role="An AI assistant specialized in managing a Todoist task list.",
        instructions=todo_prompt,
        agent_id="todolist-agent",
        model=ModelProvider(id=model),
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
        model=ModelProvider(id=model),
        tools=[read_last_emails, send_email, ReasoningTools()],
        markdown=True,
        debug_mode=True,
        show_tool_calls=True,
    )

    web_agent = Agent(
        name="Web Agent",
        role="A specialized research assistant with access to web search and utility functions.",
        instructions=web_prompt + f"\nThe user is located in {location}.",
        agent_id="web-agent",
        model=ModelProvider(id=model),
        tools=[ReasoningTools(), TavilyTools(), get_weather],
        markdown=True,
        debug_mode=True,
        show_tool_calls=True,
    )

    memory_agent = Agent(
        name="Memory Agent",
        role="Handles memory-related tasks and memory recall",
        agent_id="memory-agent",
        model=ModelProvider(id=model),
        tools=[MemoryToolkit()],
        instructions=memory_prompt,
        add_datetime_to_instructions=True,
    )

    team = Team(
        name="Jarvis",
        description="You are Jarvis, the sophisticated and quick-witted AI assistant from Iron Man.",
        instructions=jarvis_prompt+ f"\n<user_info>{user_info}</user_info>",
        mode="coordinate",
        model=ModelProvider(id=model),
        members=[todoist_agent, email_agent, web_agent],
        show_members_responses=True,
        markdown=True,
    )

    return team, memory_agent



def main(user_info, email_list, location):    # Add model selection
    st.sidebar.markdown("## Model Configuration")
    
    # Set default values if not in session state
    if "provider" not in st.session_state:
        st.session_state.provider = "openrouter"
    if "model" not in st.session_state:
        st.session_state.model = "deepseek/deepseek-chat-v3-0324:free"
    
    provider = st.sidebar.selectbox(
        "Select Provider",
        ["openrouter", "groq"],
        key="provider"
    )

    model_options = {
        "groq": ["llama3-70b-8192", "mixtral-8x7b-32768"],
        "openrouter": ["deepseek/deepseek-chat-v3-0324:free", "google/gemini-2.0-flash-exp:free", "qwen/qwq-32b:free"]
    }
    model = st.sidebar.selectbox(
        "Select Model",
        model_options[provider],
        key="model"
    )
    
    st.sidebar.divider()
    st.sidebar.write("Current model:", st.session_state.get("current_model", "Not set"))
    
    # Add update model button with custom styling
    if st.sidebar.button("🔄 Update Model", use_container_width=True, type="primary"):
        if "team" in st.session_state:
            with st.spinner("Updating model..."):
                ModelProvider = Groq if provider == "groq" else OpenRouter
                new_model = ModelProvider(id=model)
                
                # Update model for the team
                st.session_state.team.model = new_model
                
                # Update model for all team members
                for agent in st.session_state.team.members:
                    agent.model = new_model
                    
                # Update memory agent
                st.session_state.memory_agent.model = new_model
                
                st.session_state.current_model = model
                st.sidebar.success("Model updated successfully!")

    st.title("Jarvis - Your AI Assistant")
    st.markdown("""
    Welcome! I am Jarvis, your AI assistant. I can help you with:
    - Managing your tasks and to-dos
    - Reading and sending emails
    - Web searches and research
    - Weather information
    """)

    # Initialize session state
    if "messages" not in st.session_state or st.session_state.get("current_model") != model:
        st.session_state.messages = []
        st.session_state.current_model = model
        st.session_state.team, st.session_state.memory_agent = initialize_team(user_info, email_list, location, provider, model)

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("What would you like me to help you with?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get memory context
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Get memory context
                memory = st.session_state.memory_agent.run(prompt)
                try:
                    memory = json.loads(memory.content)
                    if memory['recalled_memory']:
                        final_prompt = f"<user_input>{prompt}</user_input>\n\n<retrived_memory>{memory['memory']}\n</retrived_memory>"
                    else:
                        final_prompt = f"<user_input>{prompt}</user_input>"
                except json.JSONDecodeError:
                    final_prompt = f"<user_input>{prompt}</user_input>"
                    
                print(final_prompt)                # Get team response
                response = st.session_state.team.run(final_prompt)
                st.markdown(response.content)
                
                # Add toggles for tools and metrics
                with st.expander("Show Tools"):
                    if response.tools:
                        st.json(response.tools)
                    else:
                        st.write("No tools were used in this response")
                        
                with st.expander("Show Metrics"):
                    if hasattr(response, 'metrics'):
                        st.json(response.metrics)
                    else:
                        st.write("No metrics available for this response")
                
                st.session_state.messages.append({"role": "assistant", "content": response.content})

if __name__ == "__main__":
    with open("user_data/user_info.txt", "r") as f:
    
        user_info = f.read()

    with open("user_data/email_list.txt", "r") as f:
        email_list = f.read()

    location = "Rabat"

    main(user_info=user_info, email_list=email_list, location=location)