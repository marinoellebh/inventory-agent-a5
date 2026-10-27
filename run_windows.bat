@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    where py >nul 2>&1
    if errorlevel 1 (
        python -m venv .venv
    ) else (
        py -m venv .venv
    )
)
if errorlevel 1 goto :failed
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :failed
.venv\Scripts\python.exe manage.py migrate
if errorlevel 1 goto :failed
echo.
echo Open http://127.0.0.1:8000/ in your browser.
echo The sample Chocolate bar has quantity 10 and unit price 2.50.
echo To enable the AI chat, put GEMINI_API_KEY=your_key in inventory\.env.
.venv\Scripts\python.exe manage.py runserver
goto :end
:failed
echo Setup failed. Read ASSIGNMENT_3_README.md for manual steps.
pause
:end
