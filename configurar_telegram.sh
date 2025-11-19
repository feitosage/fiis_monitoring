#!/bin/bash

# Script para configurar o Telegram Bot automaticamente

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║        📱 CONFIGURAÇÃO DO TELEGRAM BOT - FIIs 📱          ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Navegue para a pasta backend
cd "$(dirname "$0")/backend"

# Token fornecido pelo usuário
TOKEN=<TOKEN_DO_BOT>

echo "✅ Token do bot já configurado!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 PRÓXIMO PASSO: Obter seu Chat ID"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣  Abra o Telegram"
echo "2️⃣  Procure por: @userinfobot"
echo "3️⃣  Clique em 'Start'"
echo "4️⃣  Copie o número que aparece em 'Id'"
echo ""
read -p "👉 Cole seu Chat ID aqui: " CHAT_ID

if [ -z "$CHAT_ID" ]; then
    echo ""
    echo "❌ Chat ID não pode estar vazio!"
    exit 1
fi

echo ""
echo "🔄 Criando arquivo .env..."

# Cria o arquivo .env
cat > .env << EOF
# ════════════════════════════════════════════════════════════
# CONFIGURAÇÕES DO MONITOR DE FIIs
# ════════════════════════════════════════════════════════════

# OpenAI API (opcional - para análises de IA)
OPENAI_API_KEY=

# ════════════════════════════════════════════════════════════
# TELEGRAM BOT - NOTIFICAÇÕES
# ════════════════════════════════════════════════════════════

# Token do bot do Telegram
TELEGRAM_BOT_TOKEN=$TOKEN

# ID do chat para receber notificações
TELEGRAM_CHAT_ID=$CHAT_ID

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

echo "✅ Arquivo .env criado com sucesso!"
echo ""

# Ativa o ambiente virtual
if [ -d "venv" ]; then
    echo "🔄 Ativando ambiente virtual..."
    source venv/bin/activate
    
    # Instala dependências se necessário
    echo "📦 Verificando dependências..."
    pip install -q python-telegram-bot==20.8 schedule==1.2.0
    
    echo ""
    echo "🧪 Testando conexão com o Telegram..."
    echo ""
    
    python telegram_notifier.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "╔════════════════════════════════════════════════════════════╗"
        echo "║                                                            ║"
        echo "║             ✅ CONFIGURAÇÃO CONCLUÍDA! ✅                  ║"
        echo "║                                                            ║"
        echo "╚════════════════════════════════════════════════════════════╝"
        echo ""
        echo "🎉 Tudo funcionando! Você deve ter recebido uma mensagem de teste."
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🚀 PRÓXIMOS PASSOS:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "Escolha como deseja executar:"
        echo ""
        echo "  1️⃣  Teste único (executa agora e sai)"
        echo "  2️⃣  Monitoramento contínuo (a cada 1 hora) ⭐"
        echo "  3️⃣  Background (roda em segundo plano)"
        echo ""
        read -p "Opção (1-3): " opcao
        
        case $opcao in
            1)
                echo ""
                echo "🧪 Executando teste único..."
                python telegram_monitor.py --teste
                ;;
            2)
                echo ""
                echo "🚀 Iniciando monitoramento contínuo..."
                echo "⚠️  Pressione Ctrl+C para parar"
                echo ""
                python telegram_monitor.py
                ;;
            3)
                echo ""
                echo "🚀 Iniciando em background..."
                nohup python telegram_monitor.py > ../telegram_bot.log 2>&1 &
                echo ""
                echo "✅ Bot iniciado em background!"
                echo ""
                echo "Para ver logs: tail -f telegram_bot.log"
                echo "Para parar: pkill -f telegram_monitor.py"
                ;;
            *)
                echo ""
                echo "❌ Opção inválida"
                ;;
        esac
    else
        echo ""
        echo "❌ Erro na conexão com o Telegram!"
        echo ""
        echo "💡 Verifique:"
        echo "  • Chat ID está correto"
        echo "  • Você clicou em 'Start' no bot no Telegram"
        echo ""
    fi
else
    echo "❌ Ambiente virtual não encontrado!"
    echo "💡 Execute './start.sh' primeiro para configurar o projeto"
fi

cd ..

