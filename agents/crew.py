import sys
import os
from crewai import Agent, Task, Crew, Process
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.tools.sql_tool import execute_sql
from agents.tools.predict_tool import predict_late_delivery
from agents.tools.chart_tool import generate_bar_chart

load_dotenv()

def create_crew(user_question: str) -> Crew:
    """
    Creates and configures the 6-agent CrewAI system.
    """
    
    # --- LLM Configurations ---
    # Hosted API for Orchestration & Narrative
    hosted_llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
    
    # Local Ollama model for Data/Analysis/Visualization heavy lifting
    # Use host.docker.internal if running in Docker, else localhost
    ollama_url = "http://host.docker.internal:11434" if os.environ.get("PYTHONUNBUFFERED") else "http://localhost:11434"
    local_llm = ChatOllama(model="llama3.1:8b", base_url=ollama_url, temperature=0.1)

    # --- Agent Definitions ---
    
    orchestrator_agent = Agent(
        role='Chief Orchestrator',
        goal='Analyze the user request and determine exactly which subordinate tasks need to be executed.',
        backstory="You are the lead project manager. You parse questions and delegate to your team of specialists.",
        verbose=True,
        allow_delegation=True, # Allows it to pass context down
        llm=hosted_llm
    )
    
    retrieval_agent = Agent(
        role='Data Retrieval Specialist',
        goal='Write and execute precise DuckDB SQL queries against the `orders_master` table to extract historical data.',
        backstory="You are a veteran database architect. You translate human questions into perfect SQL and run them via your tool.",
        verbose=True,
        allow_delegation=False,
        tools=[execute_sql],
        llm=local_llm
    )
    
    predictive_agent = Agent(
        role='Machine Learning Predictor',
        goal='Extract features from the prompt and run them through the XGBoost prediction tool.',
        backstory="You are an expert ML engineer. You format order specifications into JSON and run the predict_late_delivery tool.",
        verbose=True,
        allow_delegation=False,
        tools=[predict_late_delivery],
        llm=local_llm
    )
    
    analysis_agent = Agent(
        role='Senior Data Analyst',
        goal='Review raw SQL output or ML predictions and calculate aggregates, averages, or key takeaways.',
        backstory="You are a meticulous analyst. You take raw data dumps and summarize them into clean numbers and insights.",
        verbose=True,
        allow_delegation=False,
        llm=local_llm
    )
    
    visualization_agent = Agent(
        role='Data Visualization Expert',
        goal='Generate visual charts from data if requested by the user.',
        backstory="You are a Python plotting master. You use your chart_tool to build PNG charts from raw data.",
        verbose=True,
        allow_delegation=False,
        tools=[generate_bar_chart],
        llm=local_llm
    )
    
    narrative_agent = Agent(
        role='Executive Communications Director',
        goal='Synthesize all findings into a final, professional plain-English response with a recommendation.',
        backstory="You are an executive writer. You take technical outputs and write punchy, readable business reports.",
        verbose=True,
        allow_delegation=False,
        llm=hosted_llm
    )

    # --- Task Definitions ---
    
    t_orchestrate = Task(
        description=f"Analyze this request: '{user_question}'. Break it down into sub-requirements (SQL lookup, prediction, chart generation).",
        expected_output="A list of specific requirements needed to answer the prompt.",
        agent=orchestrator_agent
    )
    
    t_retrieve = Task(
        description=f"If historical data is required for: '{user_question}', use your SQL tool to extract it. If not, output 'N/A'.",
        expected_output="Raw SQL data output or 'N/A'.",
        agent=retrieval_agent
    )
    
    t_predict = Task(
        description=f"If a prediction is required for: '{user_question}', extract the features and use the Predict tool. If not, output 'N/A'.",
        expected_output="The late delivery probability or 'N/A'.",
        agent=predictive_agent
    )
    
    t_analyze = Task(
        description="Review the outputs from the Retrieval and Predictive tasks. Summarize the raw data into key aggregate numbers.",
        expected_output="Clean, aggregated numbers and findings.",
        agent=analysis_agent
    )
    
    t_visualize = Task(
        description=f"If a chart is requested in '{user_question}', use the Chart tool with the analyzed data to build one. If not, output 'N/A'.",
        expected_output="Confirmation of chart generation or 'N/A'.",
        agent=visualization_agent
    )
    
    t_narrative = Task(
        description="Write the final response to the user. Incorporate the analyzed data, the prediction (if any), and note if a chart was generated. Add a brief business recommendation.",
        expected_output="A polished 2-paragraph final answer.",
        agent=narrative_agent
    )

    crew = Crew(
        agents=[orchestrator_agent, retrieval_agent, predictive_agent, analysis_agent, visualization_agent, narrative_agent],
        tasks=[t_orchestrate, t_retrieve, t_predict, t_analyze, t_visualize, t_narrative],
        verbose=2,
        process=Process.sequential
    )
    
    return crew

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agents/crew.py \"<your question here>\"")
        sys.exit(1)
        
    question = sys.argv[1]
    print(f"\n[ORCHESTRATING CREW FOR]: {question}\n")
    
    try:
        crew = create_crew(question)
        result = crew.kickoff()
        print("\n" + "="*60)
        print("📊 FINAL NARRATIVE RESPONSE")
        print("="*60)
        print(result)
    except Exception as e:
        print(f"\n❌ CREW EXECUTION FAILED: {str(e)}")
