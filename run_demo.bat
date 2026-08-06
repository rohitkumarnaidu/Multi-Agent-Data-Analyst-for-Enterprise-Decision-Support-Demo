@echo off
echo Starting Multi-Agent Data Analyst System...

echo.
echo [1/2] Starting FastAPI Backend on Port 8000...
start "FastAPI Backend" cmd /c ".\venv_312\Scripts\uvicorn api.main:app --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo.
echo [2/2] Starting Streamlit Chat UI on Port 8501...
start "Streamlit UI" cmd /c ".\venv_312\Scripts\streamlit run ui/app.py"

echo.
echo Services are booting up in separate command windows!
echo - API Backend: http://localhost:8000/docs
echo - Streamlit UI: http://localhost:8501
echo.
pause
