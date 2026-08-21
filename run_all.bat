@echo off
echo ==========================================
echo   GreenScan - Starting All Services
echo ==========================================

:: Start Backend in a new window
echo Starting Backend (FastAPI) on http://127.0.0.1:8000 ...
start "GreenScan Backend" cmd /k "cd backend && ..\venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

:: Start Frontend in a new window
echo Starting Frontend (Vite) on http://127.0.0.1:5173 ...
start "GreenScan Frontend" cmd /k "cd frontend && npm run dev -- --host 127.0.0.1"

echo.
echo ==========================================
echo   Services are starting in new windows.
echo ==========================================
echo - Backend:  http://127.0.0.1:8000
echo - Frontend: http://127.0.0.1:5173
echo.
echo If the site doesn't load immediately, please wait 5-10 seconds.
echo.
pause

