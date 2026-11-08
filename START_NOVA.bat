@echo off
echo ========================================
echo   NOVA - Distributed Processing System
echo ========================================
echo.
echo Se porneste sistemul...
echo.

REM Opreste procesoarele vechi
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

REM Porneste Dashboard NOVA
start "NOVA Dashboard" cmd /c "python nova_dashboard.py"
echo [+] NOVA Dashboard pornit pe port 8090

timeout /t 3 >nul

echo.
echo ========================================
echo   Sistemul ruleaza!
echo ========================================
echo.
echo Dashboard NOVA: http://localhost:8090
echo.
echo 1. Deschide browserul la adresa de mai sus
echo 2. Click pe "Invită în echipă" pentru a genera link
echo 3. Trimite linkul prietenilor cu MacBook
echo.
echo Se deschide browserul...
start http://localhost:8090

echo.
pause
