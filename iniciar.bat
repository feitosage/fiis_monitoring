@echo off
chcp 65001 > nul
title Monitor de FIIs - Premium Edition

echo 🚀 Iniciando Monitor de FIIs - Premium Edition
echo ==============================================
echo.

echo 🧹 Limpando portas...

REM Matar processos nas portas
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5001" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5173" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1

REM Matar processos Python e Node antigos
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Flask*" >nul 2>&1
taskkill /F /IM node.exe /FI "WINDOWTITLE eq *vite*" >nul 2>&1

timeout /t 1 /nobreak >nul
echo ✓ Portas liberadas
echo.

REM Verificar e criar ambiente virtual
if not exist "backend\venv\" (
    echo 📦 Criando ambiente virtual Python...
    cd backend
    python -m venv venv
    call venv\Scripts\activate
    pip install -q -r requirements.txt
    cd ..
) else (
    echo ✓ Ambiente virtual já existe
)

REM Verificar e instalar dependências do frontend
if not exist "frontend\node_modules\" (
    echo 📦 Instalando dependências do frontend...
    cd frontend
    call npm install
    cd ..
) else (
    echo ✓ Dependências do frontend já instaladas
)

echo.
echo 🎯 Iniciando servidores...
echo.

REM Iniciar o backend
echo 🐍 Backend iniciando na porta 5001...
start /B cmd /c "cd backend && venv\Scripts\activate && python app.py > ..\backend.log 2>&1"

REM Aguardar alguns segundos
timeout /t 3 /nobreak >nul

REM Iniciar o frontend
echo ⚛️  Frontend iniciando na porta 5173...
start /B cmd /c "cd frontend && npm run dev > ..\frontend.log 2>&1"

REM Aguardar alguns segundos
timeout /t 2 /nobreak >nul

echo.
echo ==============================================
echo ✅ Aplicação iniciada com sucesso!
echo ==============================================
echo.
echo 📊 URLs da Aplicação:
echo    Frontend: http://localhost:5173
echo    Backend:  http://localhost:5001
echo.
echo 💡 Dica: Aguarde alguns segundos e acesse o frontend
echo.
echo 🌐 Abrindo navegador...
start http://localhost:5173

echo.
echo ⚠️  Para encerrar, feche esta janela
echo.

REM Manter janela aberta
pause

