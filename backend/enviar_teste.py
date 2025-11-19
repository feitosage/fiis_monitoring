"""
Script para enviar mensagem de teste no Telegram
"""
from telegram_notifier import TelegramNotifier, run_async
from datetime import datetime

print("📱 Enviando mensagem de teste no Telegram...")
print()

try:
    notifier = TelegramNotifier()
    
    # Mensagem de teste personalizada
    mensagem = f"""🎉 <b>BOT DE FIIs ATIVADO!</b> 🎉
📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━
✅ <b>Configuração Concluída!</b>
━━━━━━━━━━━━━━━━━━━━━━━━

🤖 Seu bot está funcionando perfeitamente!

⚙️ <b>Configurações:</b>
• 📊 Monitorando: 16 FIIs
• ⏰ Intervalo: A cada 30 minutos
• 📅 Dias: Segunda a Sexta
• 🕐 Horário: 10h às 17h

━━━━━━━━━━━━━━━━━━━━━━━━
📋 <b>O que você receberá:</b>
━━━━━━━━━━━━━━━━━━━━━━━━

🔥 Top 5 maiores ALTAS
❄️ Top 5 maiores BAIXAS  
💎 Top 5 menores P/VP (oportunidades)
📊 Estatísticas do mercado

━━━━━━━━━━━━━━━━━━━━━━━━

🚀 Primeiro alerta será enviado em 30 minutos
   (dentro do horário de pregão: 10h-17h)

💡 <b>Dica:</b> Salve este chat para não perder as análises!

━━━━━━━━━━━━━━━━━━━━━━━━
Bons investimentos! 📈
"""
    
    sucesso = run_async(notifier.enviar_mensagem(mensagem))
    
    if sucesso:
        print("✅ Mensagem de teste enviada com sucesso!")
        print()
        print("📱 Verifique seu Telegram - você deve ter recebido a mensagem!")
        print()
    else:
        print("❌ Falha ao enviar mensagem")
        print()
        print("💡 Verifique:")
        print("  • Você clicou em 'Start' no bot no Telegram?")
        print("  • As credenciais no arquivo .env estão corretas?")
        print()

except ValueError as e:
    print(f"❌ {str(e)}")
    print()
    print("💡 Configure as variáveis de ambiente no arquivo backend/.env")
    print()
except Exception as e:
    print(f"❌ Erro: {str(e)}")
    print()

