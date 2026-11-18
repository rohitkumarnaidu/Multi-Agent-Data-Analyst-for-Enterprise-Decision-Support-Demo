@echo off
echo Starting Multi-Agent Data Analyst System (Mock Mode)...

echo.
echo [1/1] Starting Streamlit Chat UI on Port 8501...
start "Streamlit UI" cmd /c ".\venv_312\Scripts\streamlit run ui/mock_app.py"

echo.
echo Services are booting up in separate command windows!
echo - Streamlit UI: http://localhost:8501
echo.
pause
