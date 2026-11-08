@echo off
chcp 65001 >nul
echo ========================================
echo   QA DNA - Versiunea 1:46 AM
echo   JavaScript File Upload - Functional
echo ========================================
echo.
echo Pornesc:
echo   1. Master (port 8003)
echo   2. UI cu JavaScript (port 8081)
echo.
echo Apasa orice tasta pentru a continua...
pause >nul

echo.
echo [+] Pornesc Master-ul pe port 8003...
start "QA DNA - Master (8003)" cmd /k "python master.py --host 0.0.0.0 --port 8003"

echo [+] Astept 3 secunde...
timeout /t 3 /nobreak >nul

echo [+] Pornesc UI-ul (JavaScript upload)...
start "QA DNA - UI (8081)" cmd /k "cd desktop_app && python js_upload.py"

echo [+] Astept 5 secunde pentru pornire UI...
timeout /t 5 /nobreak >nul

echo [+] Deschid browser...
start http://localhost:8081

echo.
echo ========================================
echo   Sistemul ruleaza!
echo ========================================
echo.
echo   Master:   http://localhost:8003
echo   UI:       http://localhost:8081
echo   Dashboard: http://localhost:8003/status
echo.
echo   Inchide ferestrele cmd pentru a opri.
echo ========================================
echo.
pause
