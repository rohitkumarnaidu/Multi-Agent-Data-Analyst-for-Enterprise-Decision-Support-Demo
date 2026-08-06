from langchain.tools import tool
import matplotlib.pyplot as plt
import os
import time

@tool("Generate Bar Chart")
def generate_bar_chart(data_json: str) -> str:
    """
    Generates a simple bar chart and saves it as a PNG image.
    Input must be a JSON string with three keys:
    - 'title': The title of the chart
    - 'labels': A list of string labels for the x-axis
    - 'values': A list of numerical values for the y-axis
    
    Example: '{"title": "Late vs On-Time", "labels": ["Late", "On-Time"], "values": [8, 92]}'
    """
    try:
        import json
        data = json.loads(data_json)
        
        plt.figure(figsize=(8, 5))
        plt.bar(data['labels'], data['values'], color=['#3498db', '#e74c3c'])
        plt.title(data['title'])
        plt.ylabel("Value")
        
        # Save to a dynamic file
        os.makedirs('reports/charts', exist_ok=True)
        filename = f"reports/charts/agent_chart_{int(time.time())}.png"
        plt.savefig(filename)
        plt.close()
        
        return f"Chart successfully generated and saved to {filename}!"
        
    except Exception as e:
        return f"Chart Error: {str(e)}"
