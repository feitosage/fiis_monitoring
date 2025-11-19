#!/bin/bash

echo "🚀 Iniciando Monitor de FIIs..."

# Função para encontrar porta disponível
find_available_port() {
    local start_port=$1
    local port=$start_port
    
    while [ $port -lt $((start_port + 100)) ]; do
        if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo $port
            return 0
        fi
        port=$((port + 1))
    done
    
    echo 0
    return 1
}

# Verifica se o ambiente virtual existe
if [ ! -d "backend/venv" ]; then
    echo "📦 Criando ambiente virtual Python..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    echo "📥 Instalando dependências do backend..."
    pip install -r requirements.txt
    cd ..
else
    echo "✅ Ambiente virtual já existe"
fi

# Verifica se node_modules existe
if [ ! -d "frontend/node_modules" ]; then
    echo "📥 Instalando dependências do frontend..."
    cd frontend
    npm install
    cd ..
else
    echo "✅ Dependências do frontend já instaladas"
fi

# Verificar e encontrar portas disponíveis
echo ""
echo "🔍 Verificando portas disponíveis..."
echo ""

# Porta do Backend (padrão: 5001)
BACKEND_PORT=5001
if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Porta $BACKEND_PORT em uso, buscando porta alternativa..."
    BACKEND_PORT=$(find_available_port 5001)
    if [ $BACKEND_PORT -eq 0 ]; then
        echo "❌ Não foi possível encontrar porta disponível para o backend!"
        exit 1
    fi
    echo "✓ Usando porta alternativa para backend: $BACKEND_PORT"
else
    echo "✓ Porta $BACKEND_PORT disponível para backend"
fi

# Porta do Frontend (padrão: 5173)
FRONTEND_PORT=5173
if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Porta $FRONTEND_PORT em uso, buscando porta alternativa..."
    FRONTEND_PORT=$(find_available_port 5173)
    if [ $FRONTEND_PORT -eq 0 ]; then
        echo "❌ Não foi possível encontrar porta disponível para o frontend!"
        exit 1
    fi
    echo "✓ Usando porta alternativa para frontend: $FRONTEND_PORT"
else
    echo "✓ Porta $FRONTEND_PORT disponível para frontend"
fi

# Limpar apenas processos antigos desta aplicação (de forma segura)
# Mata apenas processos que estejam nas portas específicas deste projeto
lsof -ti:$BACKEND_PORT 2>/dev/null | xargs kill 2>/dev/null
lsof -ti:$FRONTEND_PORT 2>/dev/null | xargs kill 2>/dev/null
sleep 1

echo ""
echo "🎯 Iniciando servidores..."
echo ""

# Atualizar configuração do Vite se necessário
if [ $FRONTEND_PORT -ne 5173 ] || [ $BACKEND_PORT -ne 5001 ]; then
    echo "⚙️  Atualizando configuração do frontend..."
    # Cria arquivo temporário de configuração
    cat > frontend/vite.config.temp.js << EOF
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: $FRONTEND_PORT,
    proxy: {
      '/api': {
        target: 'http://localhost:$BACKEND_PORT',
        changeOrigin: true,
      }
    }
  }
})
EOF
    mv frontend/vite.config.temp.js frontend/vite.config.temp.mjs
fi

# Inicia o backend em background
echo "🐍 Iniciando backend na porta $BACKEND_PORT..."
cd backend
source venv/bin/activate
FLASK_RUN_PORT=$BACKEND_PORT python app.py &
BACKEND_PID=$!
cd ..

# Aguarda o backend iniciar
sleep 3

# Inicia o frontend
echo "⚛️  Iniciando frontend na porta $FRONTEND_PORT..."
cd frontend
if [ -f vite.config.temp.mjs ]; then
    npm run dev -- --config vite.config.temp.mjs &
else
    npm run dev &
fi
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Aplicação iniciada com sucesso!"
echo ""
echo "📊 Frontend: http://localhost:$FRONTEND_PORT"
echo "🔌 Backend: http://localhost:$BACKEND_PORT"
echo ""
if [ $BACKEND_PORT -ne 5001 ] || [ $FRONTEND_PORT -ne 5173 ]; then
    echo "ℹ️  Usando portas alternativas (portas padrão estavam em uso)"
    echo ""
fi

# Verifica se deve iniciar o bot do Telegram
if [ -f "backend/.env" ]; then
    # Verifica se as credenciais do Telegram estão configuradas
    if grep -q "TELEGRAM_BOT_TOKEN=" backend/.env 2>/dev/null && \
       grep -q "TELEGRAM_CHAT_ID=" backend/.env 2>/dev/null; then
        
        # Verifica se as variáveis não estão vazias
        source backend/.env 2>/dev/null
        if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "🤖 Iniciando bot do Telegram automaticamente..."
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            cd backend
            source venv/bin/activate
            nohup python telegram_monitor.py > ../telegram_bot.log 2>&1 &
            TELEGRAM_PID=$!
            cd ..
            echo "✅ Bot do Telegram iniciado! (PID: $TELEGRAM_PID)"
            echo "   • Monitoramento: A cada 1 hora"
            echo "   • Logs: telegram_bot.log"
            echo "   • Para parar: pkill -f telegram_monitor.py"
            echo ""
        fi
    fi
fi

echo "⚠️  Pressione Ctrl+C para parar os servidores"

# Função para limpar processos ao sair
cleanup() {
    echo ""
    echo "🛑 Parando servidores..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    
    # Para o bot do Telegram se estiver rodando
    if [ -n "$TELEGRAM_PID" ]; then
        echo "🤖 Parando bot do Telegram..."
        kill $TELEGRAM_PID 2>/dev/null
    fi
    pkill -f telegram_monitor.py 2>/dev/null
    
    lsof -ti:$BACKEND_PORT 2>/dev/null | xargs kill -9 2>/dev/null
    lsof -ti:$FRONTEND_PORT 2>/dev/null | xargs kill -9 2>/dev/null
    # Limpa arquivo de configuração temporário
    rm -f frontend/vite.config.temp.mjs 2>/dev/null
    echo "👋 Aplicação encerrada!"
    exit 0
}

trap cleanup INT

# Mantém o script rodando
wait

