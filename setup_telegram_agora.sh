#!/bin/bash

# Script de configuração automática do Telegram Bot

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║     🚀 CONFIGURAÇÃO AUTOMÁTICA - TELEGRAM BOT 🚀          ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")/backend"

echo "📝 Criando arquivo de configuração..."

# Cria o arquivo .env com as credenciais fornecidas
cat > .env << 'EOF'
# ════════════════════════════════════════════════════════════
# CONFIGURAÇÕES DO MONITOR DE FIIs
# ════════════════════════════════════════════════════════════

# OpenAI API (opcional - para análises de IA)
OPENAI_API_KEY=

# ════════════════════════════════════════════════════════════
# TELEGRAM BOT - NOTIFICAÇÕES
# ════════════════════════════════════════════════════════════

# Token do bot do Telegram
TELEGRAM_BOT_TOKEN=<TOKEN_DO_BOT>

# ID do chat para receber notificações
TELEGRAM_CHAT_ID=<CHAT_ID_DO_BOT>

# ════════════════════════════════════════════════════════════
# CONFIGURAÇÕES DE ALERTAS
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

# Verifica ambiente virtual
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado!"
    echo "💡 Execute './start.sh' primeiro na raiz do projeto"
    cd ..
    exit 1
fi

echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

echo "📦 Instalando dependências do Telegram..."
pip install -q python-telegram-bot==20.8 schedule==1.2.0

if [ $? -eq 0 ]; then
    echo "✅ Dependências instaladas!"
else
    echo "❌ Erro ao instalar dependências"
    cd ..
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 TESTANDO CONEXÃO COM O TELEGRAM..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python telegram_notifier.py

if [ $? -eq 0 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║          ✅ ✅ ✅ SUCESSO! ✅ ✅ ✅                        ║"
    echo "║                                                            ║"
    echo "║     Você deve ter recebido uma mensagem no Telegram!      ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🚀 COMO VOCÊ QUER USAR O BOT?"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  1️⃣  Teste único - Executa UMA análise agora e para"
    echo "     (Para testar se está funcionando)"
    echo ""
    echo "  2️⃣  Monitoramento contínuo - Envia alertas a cada 30 Minutos ⭐"
    echo "     (Recomendado - mantém rodando e atualizando)"
    echo ""
    echo "  3️⃣  Background - Roda em segundo plano"
    echo "     (Libera o terminal, roda em background)"
    echo ""
    echo "  4️⃣  Personalizado - Define seu próprio intervalo"
    echo "     (Ex: a cada 30 minutos, 2 horas, etc)"
    echo ""
    read -p "👉 Escolha uma opção (1-4): " opcao
    
    echo ""
    
    case $opcao in
        1)
            echo "🧪 Executando teste único..."
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            python telegram_monitor.py --teste
            echo ""
            echo "✅ Teste concluído! Você recebeu a análise no Telegram?"
            ;;
        2)
            echo "🚀 Iniciando monitoramento contínuo (a cada 1 hora)..."
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "⚠️  DICA: Deixe este terminal aberto"
            echo "⚠️  Pressione Ctrl+C para parar o bot"
            echo ""
            python telegram_monitor.py
            ;;
        3)
            echo "🚀 Iniciando em background..."
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            nohup python telegram_monitor.py > ../telegram_bot.log 2>&1 &
            BOT_PID=$!
            echo ""
            echo "✅ Bot iniciado com sucesso!"
            echo ""
            echo "📊 Informações:"
            echo "  • PID: $BOT_PID"
            echo "  • Logs: telegram_bot.log"
            echo "  • Intervalo: 1 hora"
            echo ""
            echo "📋 Comandos úteis:"
            echo "  • Ver logs: tail -f telegram_bot.log"
            echo "  • Parar bot: pkill -f telegram_monitor.py"
            echo "  • Status: ps aux | grep telegram_monitor"
            echo ""
            ;;
        4)
            echo "⏰ Define o intervalo entre atualizações:"
            echo ""
            echo "Exemplos:"
            echo "  • 0.5 = a cada 30 minutos"
            echo "  • 1 = a cada 1 hora"
            echo "  • 2 = a cada 2 horas"
            echo "  • 4 = a cada 4 horas"
            echo ""
            read -p "👉 Intervalo em horas: " intervalo
            echo ""
            echo "🚀 Iniciando monitoramento a cada ${intervalo}h..."
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            python telegram_monitor.py --intervalo $intervalo
            ;;
        *)
            echo "❌ Opção inválida!"
            echo ""
            echo "💡 Execute novamente: ./setup_telegram_agora.sh"
            ;;
    esac
    
else
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║                  ❌ ERRO DE CONEXÃO ❌                    ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "💡 Possíveis causas:"
    echo ""
    echo "  1️⃣  Você não iniciou o bot no Telegram"
    echo "     → Procure o bot no Telegram e clique em 'Start'"
    echo ""
    echo "  2️⃣  Token ou Chat ID incorretos"
    echo "     → Verifique em: backend/.env"
    echo ""
    echo "  3️⃣  Sem conexão com internet"
    echo "     → Verifique sua conexão"
    echo ""
    echo "📖 Consulte: TELEGRAM_CONFIG.md para mais ajuda"
    echo ""
fi

cd ..

