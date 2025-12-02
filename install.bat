@echo off
chcp 65001 >nul
title GdeDoctor Bot - Установка зависимостей
echo.
echo ========================================
echo   GdeDoctor Bot - Установка
echo ========================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo Установите Python 3.9 или выше с https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo Найден Python:
python --version
echo.

echo Установка зависимостей бота...
echo.
cd bot

REM Создание виртуального окружения
if exist ".venv" (
    echo Виртуальное окружение уже существует, пропускаем создание...
) else (
    echo Создание виртуального окружения...
    python -m venv .venv
)

REM Активация и установка зависимостей
call .venv\Scripts\activate.bat
echo.
echo Обновление pip...
python -m pip install --upgrade pip --quiet
echo.
echo Установка зависимостей из requirements.txt...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Не удалось установить зависимости!
    echo.
    pause
    exit /b 1
)

deactivate
cd ..

echo.
echo ========================================
echo   ✓ Установка завершена успешно!
echo ========================================
echo.
echo Для запуска бота используйте: run-bot.bat
echo Для остановки: stop-all.bat
echo.
pause
