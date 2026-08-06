from crewai import Agent, Task, Crew, Process
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI
import os

from agents.tools.sql_tool import execute_sql
from agents.tools.predict_tool import predict_late_delivery

# 1. Setup the LLM
# The user specified using Ollama with the phi3:mini model.
# Ensure Ollama is running (`ollama run phi3:mini`) before executing this.
try:
    # Attempt to use local Ollama
    default_llm = ChatOllama(model="phi3:mini")
except Exception:
    # Fallback to OpenAI if desired (needs OPENAI_API_KEY env var)
    default_llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

# 2. Define the Agents
data_agent = Agent(
    role='Senior SQL Data Engineer',
    goal='Write and execute exact SQL queries against DuckDB to answer data questions accurately.',
    backstory="You are a veteran database architect. You write precise DuckDB SQL queries to extract data. You NEVER guess data; you ALWAYS use your SQL tool to look it up.",
    verbose=True,
    allow_delegation=False,
    tools=[execute_sql],
    llm=default_llm
)

predictive_agent = Agent(
    role='Machine Learning Engineer',
    goal='Predict late delivery risk using your predictive model tool.',
    backstory="You are an expert ML engineer. You take order features, format them precisely into JSON, and run them through your predictive model tool to get a risk percentage.",
    verbose=True,
    allow_delegation=False,
    tools=[predict_late_delivery],
    llm=default_llm
)

analysis_agent = Agent(
    role='Lead Business Analyst',
    goal='Synthesize raw data and ML predictions into a clear, actionable business narrative.',
    backstory="You are a top-tier business analyst. You review the output from the data engineer and ML engineer, and write short, punchy, easy-to-read executive summaries without technical jargon.",
    verbose=True,
    allow_delegation=False,
    tools=[],
    llm=default_llm
)

# 3. Create the Factory
def create_crew(user_question: str) -> Crew:
    """
    Creates the tasks based on the user's question and orchestrates the crew.
    """
    
    task1 = Task(
        description=f"Analyze this question: '{user_question}'. If it asks for historical data, use your SQL tool to query the `orders_master` table to find the answer. If it doesn't require SQL, just pass.",
        expected_output="The raw data extracted from the database, or a note saying no historical data was needed.",
        agent=data_agent
    )
    
    task2 = Task(
        description=f"Analyze this question: '{user_question}'. If it asks to predict a risk or probability for an order, use your Predict tool. Formulate the JSON payload based on the details in the question. If no prediction is requested, pass.",
        expected_output="The predicted late delivery probability, or a note saying no prediction was needed.",
        agent=predictive_agent
    )
    
    task3 = Task(
        description=f"Review the user's original question: '{user_question}'. Review the raw data from the SQL agent and the prediction from the ML agent. Write a 2-3 paragraph final answer to the user summarizing everything clearly.",
        expected_output="A polished, final business summary answering the user's question.",
        agent=analysis_agent
    )
    
    crew = Crew(
        agents=[data_agent, predictive_agent, analysis_agent],
        tasks=[task1, task2, task3],
        verbose=2,
        process=Process.sequential
    )
    
    return crew
