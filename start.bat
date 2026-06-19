@echo off
title Avvio PLC Code Generator
color 0A

echo ===================================================
echo   PLC Ladder Logic Generator - Avvio Rapido Locale
echo ===================================================
echo.

:: Controllo dipendenze principali
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERRORE] Python non e' installato o non e' nel PATH.
    pause
    exit /b
)

where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERRORE] Node.js / npm non e' installato o non e' nel PATH.
    pause
    exit /b
)

echo [1/3] Configurazione Backend (FastAPI)...
cd api
if not exist ".venv" (
    echo Creazione ambiente virtuale Python...
    python -m venv .venv
)
call .venv\Scripts\activate.bat
echo Installazione librerie Python...
pip install -r ..\requirements.txt -q
cd ..

echo.
echo [2/3] Configurazione Frontend (React/Vite)...
if not exist "node_modules" (
    echo Installazione pacchetti Node.js...
    call npm install
)

echo.
echo [3/3] Avvio dei Server...
echo.
echo ===================================================
echo IMPORTANTE: Si aprira' una seconda finestra nera 
echo per il backend. NON CHIUDERLA!
echo ===================================================
echo.

:: Avvia il backend in una nuova finestra
start "Backend PLC (FastAPI)" cmd /k "cd api && call .venv\Scripts\activate.bat && uvicorn index:app --reload"

:: Avvia il frontend in questa finestra
echo Avvio Interfaccia Grafica...
call npm run dev
