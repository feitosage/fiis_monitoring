#!/bin/bash

echo "🚀 Iniciando Monitor de FIIs - Premium Edition"
echo "=============================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para limpar processos ao sair
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Encerrando servidores...${NC}"
    pkill -f "python.*app.py" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    lsof -ti:$BACKEND_PORT 2>/dev/null | xargs kill -9 2>/dev/null
    lsof -ti:$FRONTEND_PORT 2>/dev/null | xargs kill -9 2>/dev/null
    # Limpa arquivo de configuração temporário
    rm -f frontend/vite.config.temp.mjs 2>/dev/null
    echo -e "${GREEN}✅ Servidores encerrados!${NC}"
    exit 0
}

trap cleanup INT TERM

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

# Verificar e encontrar portas disponíveis
echo -e "${BLUE}🔍 Verificando portas disponíveis...${NC}"

# Porta do Backend (padrão: 5001)
BACKEND_PORT=5001
if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Porta $BACKEND_PORT em uso, buscando porta alternativa...${NC}"
    BACKEND_PORT=$(find_available_port 5001)
    if [ $BACKEND_PORT -eq 0 ]; then
        echo -e "${RED}❌ Não foi possível encontrar porta disponível para o backend!${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} Usando porta alternativa para backend: ${GREEN}$BACKEND_PORT${NC}"
else
    echo -e "${GREEN}✓${NC} Porta $BACKEND_PORT disponível para backend"
fi

# Porta do Frontend (padrão: 5173)
FRONTEND_PORT=5173
if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Porta $FRONTEND_PORT em uso, buscando porta alternativa...${NC}"
    FRONTEND_PORT=$(find_available_port 5173)
    if [ $FRONTEND_PORT -eq 0 ]; then
        echo -e "${RED}❌ Não foi possível encontrar porta disponível para o frontend!${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} Usando porta alternativa para frontend: ${GREEN}$FRONTEND_PORT${NC}"
else
    echo -e "${GREEN}✓${NC} Porta $FRONTEND_PORT disponível para frontend"
fi

# Limpar apenas processos antigos desta aplicação (de forma segura)
# Mata apenas processos que estejam nas portas específicas deste projeto
lsof -ti:$BACKEND_PORT 2>/dev/null | xargs kill 2>/dev/null
lsof -ti:$FRONTEND_PORT 2>/dev/null | xargs kill 2>/dev/null
sleep 1

echo ""

# Verificar e instalar dependências do backend
echo -e "${BLUE}📦 Verificando backend...${NC}"
if [ ! -d "backend/venv" ]; then
    echo "Criando ambiente virtual Python..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
    cd ..
else
    echo -e "${GREEN}✓${NC} Ambiente virtual já existe"
fi

# Verificar e instalar dependências do frontend
echo -e "${BLUE}📦 Verificando frontend...${NC}"
if [ ! -d "frontend/node_modules" ]; then
    echo "Instalando dependências do frontend..."
    cd frontend
    npm install
    cd ..
else
    echo -e "${GREEN}✓${NC} Dependências do frontend já instaladas"
fi

echo ""
echo -e "${BLUE}🎯 Iniciando servidores...${NC}"
echo ""

# Atualizar configuração do backend se necessário
if [ $BACKEND_PORT -ne 5001 ]; then
    echo -e "${BLUE}⚙️  Atualizando configuração do backend para porta $BACKEND_PORT...${NC}"
fi

# Iniciar o backend em background
echo -e "${GREEN}🐍 Backend iniciando na porta $BACKEND_PORT...${NC}"
cd backend
source venv/bin/activate
FLASK_RUN_PORT=$BACKEND_PORT python app.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Aguardar o backend iniciar
echo "⏳ Aguardando backend..."
sleep 3

# Verificar se backend está rodando
if curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend OK!${NC}"
else
    echo -e "${YELLOW}⚠️  Backend ainda inicializando...${NC}"
fi

# Atualizar configuração do Vite se necessário
if [ $FRONTEND_PORT -ne 5173 ] || [ $BACKEND_PORT -ne 5001 ]; then
    echo -e "${BLUE}⚙️  Atualizando configuração do frontend...${NC}"
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

# Iniciar o frontend em background
echo -e "${GREEN}⚛️  Frontend iniciando na porta $FRONTEND_PORT...${NC}"
cd frontend
if [ -f vite.config.temp.mjs ]; then
    npm run dev -- --config vite.config.temp.mjs > ../frontend.log 2>&1 &
else
    npm run dev > ../frontend.log 2>&1 &
fi
FRONTEND_PID=$!
cd ..

echo ""
echo "=============================================="
echo -e "${GREEN}✅ Aplicação iniciada com sucesso!${NC}"
echo "=============================================="
echo ""
echo -e "${BLUE}📊 URLs da Aplicação:${NC}"
echo -e "   Frontend: ${GREEN}http://localhost:$FRONTEND_PORT${NC}"
echo -e "   Backend:  ${GREEN}http://localhost:$BACKEND_PORT${NC}"
echo ""
if [ $BACKEND_PORT -ne 5001 ] || [ $FRONTEND_PORT -ne 5173 ]; then
    echo -e "${YELLOW}ℹ️  Usando portas alternativas (portas padrão estavam em uso)${NC}"
    echo ""
fi
echo -e "${YELLOW}💡 Dica:${NC} Aguarde alguns segundos e acesse o frontend"
echo ""
echo -e "${YELLOW}⚠️  Pressione Ctrl+C para parar os servidores${NC}"
echo ""

# Aguardar um pouco antes de abrir o navegador
sleep 2

# Tentar abrir o navegador automaticamente
if command -v open &> /dev/null; then
    echo "🌐 Abrindo navegador..."
    open http://localhost:$FRONTEND_PORT
elif command -v xdg-open &> /dev/null; then
    echo "🌐 Abrindo navegador..."
    xdg-open http://localhost:$FRONTEND_PORT
fi

# Manter o script rodando e mostrar logs
echo ""
echo "📋 Logs em tempo real (Ctrl+C para sair):"
echo "=============================================="
tail -f backend.log frontend.log 2>/dev/null &
TAIL_PID=$!

# Aguardar interrupção
wait

