@echo off
echo ========================================
echo   QA DNA - Sistem Complet
echo ========================================
echo.
echo Se porneste sistemul distribuit...
echo.

REM Opreste procesoele vechi
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

REM Porneste Master-ul in background
start "QA DNA Master" cmd /c "python master.py --port 8003"
echo [+] Master pornit pe port 8003

timeout /t 3 >nul

REM Porneste Dashboard Wave in background  
start "QA DNA Dashboard" cmd /c "python dashboard_wave.py"
echo [+] Dashboard pornit pe port 8090

timeout /t 3 >nul

echo.
echo ========================================
echo   Sistemul ruleaza!
echo ========================================
echo.
echo Dashboard: http://localhost:8090
echo Master:    http://localhost:8003
echo.
echo Se deschide browserul...
start http://localhost:8090

echo.
pause
