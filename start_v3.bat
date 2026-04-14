@echo off
echo 🚀 Starting Synapse Studio V3 Backend (FastAPI)...
start "Synapse V3 Backend" cmd /c "uvicorn main:app --reload --port 8000"

timeout /t 3 /nobreak > nul

echo 🎨 Starting Synapse Studio V3 Frontend (Streamlit)...
start "Synapse V3 Frontend" cmd /c "streamlit run app.py"

echo ✅ V3 System running! Check your browser.
