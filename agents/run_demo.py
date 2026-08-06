import sys
import os

# Add project root to path so we can run this from anywhere
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.crew import create_crew

def main():
    print("="*60)
    print("🤖 Multi-Agent Data Analyst - Demo Execution")
    print("="*60)
    
    questions = [
        # Question 1: SQL Only
        "What is our overall historical late delivery rate for all orders?",
        
        # Question 2: Prediction Only
        "Predict the late delivery risk for a new order with these specs: Weight 500g, Volume 1000cm3, Freight 15.5, Price 49.9, Freight ratio 0.31, Approval hrs 2.5, ordered on Monday (0) in May (5), seller late rate 0.05, Customer state SP, Seller state RJ.",
        
        # Question 3: Hybrid (SQL + Charting conceptually)
        "What are the top 3 states with the highest late delivery rates? Please use the bar chart tool to visualize them."
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n[Demo Question {i}]:\n> {question}\n")
        print("Starting Crew... (Ensure Ollama is running!)")
        
        try:
            crew = create_crew(question)
            result = crew.kickoff()
            
            print("\n" + "="*60)
            print(f"📊 FINAL EXECUTIVE SUMMARY (Q{i})")
            print("="*60)
            print(result)
            
        except Exception as e:
            print(f"\n❌ CREW EXECUTION FAILED for Question {i}")
            print(f"Error: {str(e)}")
            print("\nTroubleshooting:")
            print("1. Is Ollama running? Open a terminal and run: ollama serve")
            print("2. Do you have the model pulled? Run: ollama run phi3:mini")
            break

if __name__ == "__main__":
    main()
