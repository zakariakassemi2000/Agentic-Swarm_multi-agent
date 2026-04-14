@echo off
echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║       AGENTIC SWARM — Infinite Debate        ║
echo  ╚══════════════════════════════════════════════╝
echo.
echo [1/3] Installing dependencies...
pip install -r requirements.txt -q
echo.
echo [2/3] Starting FastAPI backend (port 8000)...
start "FastAPI Backend" cmd /k "python main.py"
timeout /t 3 /nobreak > NUL
echo.
echo [3/3] Starting Streamlit UI (port 8501)...
start "Streamlit UI" cmd /k "streamlit run app.py --server.port 8501 --server.headless false"
echo.
echo  ✅ Both services are running!
echo  → Open your browser at: http://localhost:8501
echo.
pause
