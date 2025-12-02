@echo off
chcp 65001 >nul
title GdeDoctor Bot - Telegram Bot для поиска врачей
echo.
echo ========================================
echo   GdeDoctor Telegram Bot
echo   Бот для поиска врачей в Калуге
echo ========================================
echo.
echo Запуск бота...
echo.

cd bot

REM Проверка наличия виртуального окружения
if not exist ".venv" (
    echo [ОШИБКА] Виртуальное окружение не найдено!
    echo Запустите install.bat для установки зависимостей.
    echo.
    pause
    exit /b 1
)

REM Активация виртуального окружения и запуск бота
call .venv\Scripts\activate.bat
python -m app.main

REM Если бот завершился с ошибкой
if errorlevel 1 (
    echo.
    echo [ОШИБКА] Бот завершился с ошибкой!
    echo.
    pause
)

deactivate
