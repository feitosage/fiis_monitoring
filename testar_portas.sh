#!/bin/bash

# Script de teste para verificar a detecção automática de portas

echo "🧪 Teste de Detecção Automática de Portas"
echo "========================================"
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função de teste
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

# Testa porta 5001
echo "📡 Testando porta 5001 (Backend)..."
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Porta 5001 está em uso${NC}"
    PORTA=$(find_available_port 5001)
    if [ $PORTA -ne 0 ]; then
        echo -e "${GREEN}✅ Porta alternativa encontrada: $PORTA${NC}"
    else
        echo -e "${RED}❌ Nenhuma porta disponível encontrada!${NC}"
    fi
else
    echo -e "${GREEN}✅ Porta 5001 está disponível${NC}"
fi

echo ""

# Testa porta 5173
echo "📡 Testando porta 5173 (Frontend)..."
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Porta 5173 está em uso${NC}"
    PORTA=$(find_available_port 5173)
    if [ $PORTA -ne 0 ]; then
        echo -e "${GREEN}✅ Porta alternativa encontrada: $PORTA${NC}"
    else
        echo -e "${RED}❌ Nenhuma porta disponível encontrada!${NC}"
    fi
else
    echo -e "${GREEN}✅ Porta 5173 está disponível${NC}"
fi

echo ""
echo "✅ Teste concluído!"
echo ""
echo "💡 Se as portas estão disponíveis, você pode executar:"
echo "   ./iniciar.sh"














