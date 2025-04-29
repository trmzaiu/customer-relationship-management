@echo off
start cmd /k "cd backend && venv\Scripts\activate && python app.py"
start cmd /k "cd frontend && streamlit run main.py"
