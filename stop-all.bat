@echo off
chcp 65001 >nul
title GdeDoctor Bot - Остановка всех процессов
echo.
echo ========================================
echo   Остановка GdeDoctor Bot
echo ========================================
echo.

echo Останавливаем процессы Python...
taskkill /f /im python.exe 2>nul
if errorlevel 1 (
    echo   Процессы Python не найдены
) else (
    echo   ✓ Процессы Python остановлены
)

echo.
echo Ожидание завершения процессов...
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   Все процессы остановлены
echo ========================================
echo.
pause
