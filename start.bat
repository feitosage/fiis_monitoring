@echo off
echo 🚀 Iniciando Monitor de FIIs...

REM Verifica se o ambiente virtual existe
if not exist "backend\venv\" (
    echo 📦 Criando ambiente virtual Python...
    cd backend
    python -m venv venv
    call venv\Scripts\activate
    echo 📥 Instalando dependências do backend...
    pip install -r requirements.txt
    cd ..
) else (
    echo ✅ Ambiente virtual já existe
)

REM Verifica se node_modules existe
if not exist "frontend\node_modules\" (
    echo 📥 Instalando dependências do frontend...
    cd frontend
    call npm install
    cd ..
) else (
    echo ✅ Dependências do frontend já instaladas
)

echo.
echo 🎯 Iniciando servidores...
echo.

REM Inicia o backend
echo 🐍 Iniciando backend na porta 5000...
start cmd /k "cd backend && venv\Scripts\activate && python app.py"

REM Aguarda alguns segundos
timeout /t 3 /nobreak >nul

REM Inicia o frontend
echo ⚛️  Iniciando frontend na porta 5173...
start cmd /k "cd frontend && npm run dev"

echo.
echo ✅ Aplicação iniciada com sucesso!
echo.
echo 📊 Frontend: http://localhost:5173
echo 🔌 Backend: http://localhost:5000
echo.
echo ⚠️  Feche as janelas do terminal para parar os servidores
echo.

pause

