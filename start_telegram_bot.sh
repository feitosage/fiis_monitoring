#!/bin/bash

# Script para iniciar o bot de monitoramento do Telegram

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║     📱 INICIANDO BOT DE NOTIFICAÇÕES - TELEGRAM 📱        ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Verifica se está na pasta do projeto
if [ ! -f "backend/telegram_monitor.py" ]; then
    echo "❌ Erro: Execute este script na raiz do projeto fii_yahoo/"
    exit 1
fi

# Verifica se o ambiente virtual existe
if [ ! -d "backend/venv" ]; then
    echo "❌ Erro: Ambiente virtual não encontrado!"
    echo "💡 Execute './start.sh' primeiro para configurar o projeto"
    exit 1
fi

# Verifica se as dependências estão instaladas
cd backend
source venv/bin/activate

echo "🔍 Verificando dependências..."
if ! python -c "import telegram" 2>/dev/null; then
    echo "📦 Instalando dependências do Telegram..."
    pip install -q python-telegram-bot==20.8 schedule==1.2.0
    if [ $? -eq 0 ]; then
        echo "✅ Dependências instaladas com sucesso!"
    else
        echo "❌ Erro ao instalar dependências"
        exit 1
    fi
else
    echo "✅ Dependências já instaladas"
fi

# Verifica se o .env está configurado
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  Arquivo .env não encontrado!"
    echo ""
    echo "📝 Criando arquivo .env..."
    cat > .env << 'EOF'
# ════════════════════════════════════════════════════════════
# TELEGRAM BOT - NOTIFICAÇÕES
# ════════════════════════════════════════════════════════════

# Token do bot do Telegram (obtenha em: https://t.me/BotFather)
TELEGRAM_BOT_TOKEN=

# ID do chat para receber notificações (obtenha em: https://t.me/userinfobot)
TELEGRAM_CHAT_ID=

# ════════════════════════════════════════════════════════════
# CONFIGURAÇÕES DE ALERTAS (Opcional)
# ════════════════════════════════════════════════════════════

# Variação mínima para alertar sobre ALTA (em %)
ALERTA_ALTA_MINIMA=1.5

# Variação mínima para alertar sobre BAIXA (em %)
ALERTA_BAIXA_MINIMA=-1.5

# P/VP mínimo para alertar sobre DESCONTO
ALERTA_DESCONTO_PVP=0.95
EOF
    echo "✅ Arquivo .env criado!"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "📋 PRÓXIMOS PASSOS:"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "1️⃣  Crie seu bot no Telegram:"
    echo "   • Procure por @BotFather no Telegram"
    echo "   • Envie /newbot e siga as instruções"
    echo "   • Copie o TOKEN fornecido"
    echo ""
    echo "2️⃣  Obtenha seu Chat ID:"
    echo "   • Procure por @userinfobot no Telegram"
    echo "   • Clique em Start"
    echo "   • Copie o número do 'Id'"
    echo ""
    echo "3️⃣  Edite o arquivo backend/.env e adicione:"
    echo "   TELEGRAM_BOT_TOKEN=seu_token_aqui"
    echo "   TELEGRAM_CHAT_ID=seu_chat_id_aqui"
    echo ""
    echo "4️⃣  Execute este script novamente!"
    echo ""
    echo "📖 Instruções completas: TELEGRAM_CONFIG.md"
    echo "═══════════════════════════════════════════════════════════"
    cd ..
    exit 0
fi

# Verifica se as variáveis estão configuradas
source .env 2>/dev/null

if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo ""
    echo "⚠️  Configurações do Telegram não encontradas!"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "📋 CONFIGURE O BOT:"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "1️⃣  Edite o arquivo: backend/.env"
    echo ""
    echo "2️⃣  Adicione suas credenciais:"
    echo "   TELEGRAM_BOT_TOKEN=seu_token_do_botfather"
    echo "   TELEGRAM_CHAT_ID=seu_chat_id"
    echo ""
    echo "📖 Veja instruções completas em: TELEGRAM_CONFIG.md"
    echo "═══════════════════════════════════════════════════════════"
    cd ..
    exit 0
fi

echo ""
echo "🔄 Testando conexão com o Telegram..."
echo ""

# Testa a conexão
python telegram_notifier.py
TEST_RESULT=$?

if [ $TEST_RESULT -ne 0 ]; then
    echo ""
    echo "❌ Falha no teste de conexão!"
    echo ""
    echo "💡 Verifique:"
    echo "  • Token do bot está correto"
    echo "  • Chat ID está correto"
    echo "  • Bot foi iniciado no Telegram (clique em 'Start')"
    echo ""
    echo "📖 Consulte: TELEGRAM_CONFIG.md"
    cd ..
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ TESTE CONCLUÍDO - BOT FUNCIONANDO!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Escolha como deseja executar:"
echo ""
echo "  1️⃣  Teste único (executa agora e sai)"
echo "  2️⃣  Monitoramento contínuo (a cada 1 hora)"
echo "  3️⃣  Monitoramento personalizado"
echo "  4️⃣  Background (executa e libera o terminal)"
echo "  5️⃣  Cancelar"
echo ""
read -p "Opção (1-5): " opcao

case $opcao in
    1)
        echo ""
        echo "🧪 Executando teste único..."
        echo ""
        python telegram_monitor.py --teste
        ;;
    2)
        echo ""
        echo "🚀 Iniciando monitoramento contínuo (1 hora)..."
        echo ""
        python telegram_monitor.py
        ;;
    3)
        echo ""
        read -p "Intervalo em horas (ex: 0.5 para 30min, 2 para 2h): " intervalo
        echo ""
        echo "🚀 Iniciando monitoramento a cada ${intervalo}h..."
        echo ""
        python telegram_monitor.py --intervalo $intervalo
        ;;
    4)
        echo ""
        echo "🚀 Iniciando em background..."
        nohup python telegram_monitor.py > ../telegram_bot.log 2>&1 &
        BOT_PID=$!
        echo ""
        echo "✅ Bot iniciado em background!"
        echo "  • PID: $BOT_PID"
        echo "  • Logs: telegram_bot.log"
        echo ""
        echo "Para ver logs em tempo real:"
        echo "  tail -f telegram_bot.log"
        echo ""
        echo "Para parar o bot:"
        echo "  pkill -f telegram_monitor.py"
        echo ""
        ;;
    5)
        echo ""
        echo "👋 Operação cancelada"
        cd ..
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Opção inválida!"
        cd ..
        exit 1
        ;;
esac

cd ..

