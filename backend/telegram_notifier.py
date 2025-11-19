"""
Módulo de notificações do Telegram para monitoramento de FIIs
"""
import asyncio
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class TelegramNotifier:
    """Classe para enviar notificações sobre FIIs no Telegram"""
    
    def __init__(self):
        """Inicializa o notificador do Telegram"""
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token:
            raise ValueError("❌ TELEGRAM_BOT_TOKEN não configurado no arquivo .env")
        
        if not self.chat_id:
            raise ValueError("❌ TELEGRAM_CHAT_ID não configurado no arquivo .env")
        
        self.bot = Bot(token=self.bot_token)
    
    async def enviar_mensagem(self, mensagem, parse_mode='HTML'):
        """
        Envia uma mensagem para o Telegram
        
        Args:
            mensagem (str): Texto da mensagem
            parse_mode (str): Formato da mensagem ('HTML' ou 'Markdown')
        
        Returns:
            bool: True se enviou com sucesso, False caso contrário
        """
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=mensagem,
                parse_mode=parse_mode
            )
            return True
        except TelegramError as e:
            print(f"❌ Erro ao enviar mensagem no Telegram: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado ao enviar mensagem: {str(e)}")
            return False
    
    def formatar_variacao(self, variacao):
        """
        Formata variação com emoji apropriado
        
        Args:
            variacao (float): Variação percentual
        
        Returns:
            str: Texto formatado com emoji
        """
        if variacao > 0:
            return f"📈 +{variacao:.2f}%"
        elif variacao < 0:
            return f"📉 {variacao:.2f}%"
        else:
            return f"➖ {variacao:.2f}%"
    
    def formatar_alerta_resumo(self, dados_fiis, total_analisados):
        """
        Formata um alerta resumido com as principais variações
        
        Args:
            dados_fiis (dict): Dados dos FIIs com 'altas' e 'baixas'
            total_analisados (int): Total de FIIs analisados
        
        Returns:
            str: Mensagem formatada
        """
        agora = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        maiores_altas = dados_fiis.get('altas', [])[:5]
        maiores_baixas = dados_fiis.get('baixas', [])[:5]
        
        # Estatísticas gerais
        total_altas = len([f for f in dados_fiis.get('todos', []) if f['variacao'] > 0])
        total_baixas = len([f for f in dados_fiis.get('todos', []) if f['variacao'] < 0])
        total_estavel = total_analisados - total_altas - total_baixas
        
        # Variação média
        if dados_fiis.get('todos'):
            variacao_media = sum(f['variacao'] for f in dados_fiis['todos']) / len(dados_fiis['todos'])
        else:
            variacao_media = 0
        
        mensagem = f"""🔔 <b>MONITOR DE FIIs</b> 🔔
📅 {agora}

📊 <b>RESUMO DO MERCADO:</b>
• Total analisado: {total_analisados} FIIs
• 📈 Em alta: {total_altas} ({(total_altas/max(total_analisados,1)*100):.1f}%)
• 📉 Em baixa: {total_baixas} ({(total_baixas/max(total_analisados,1)*100):.1f}%)
• ➖ Estável: {total_estavel} ({(total_estavel/max(total_analisados,1)*100):.1f}%)
• Variação média: {variacao_media:+.2f}%

"""
        
        if maiores_altas:
            mensagem += "🔥 <b>TOP 5 MAIORES ALTAS:</b>\n"
            for i, fii in enumerate(maiores_altas, 1):
                ticker = fii['ticker'].replace('.SA', '')
                mensagem += f"{i}. <b>{ticker}</b>: R$ {fii['preco']:.2f} {self.formatar_variacao(fii['variacao'])}\n"
                if fii.get('dy'):
                    mensagem += f"   DY: {fii['dy']:.2f}%"
                    if fii.get('pvp'):
                        mensagem += f" | P/VP: {fii['pvp']:.2f}"
                    mensagem += "\n"
            mensagem += "\n"
        
        if maiores_baixas:
            mensagem += "❄️ <b>TOP 5 MAIORES BAIXAS:</b>\n"
            for i, fii in enumerate(maiores_baixas, 1):
                ticker = fii['ticker'].replace('.SA', '')
                mensagem += f"{i}. <b>{ticker}</b>: R$ {fii['preco']:.2f} {self.formatar_variacao(fii['variacao'])}\n"
                if fii.get('dy'):
                    mensagem += f"   DY: {fii['dy']:.2f}%"
                    if fii.get('pvp'):
                        mensagem += f" | P/VP: {fii['pvp']:.2f}"
                    mensagem += "\n"
            mensagem += "\n"
        
        # OPORTUNIDADES P/VP: Menores P/VP entre os TOP 5 MAIORES BAIXAS
        maiores_baixas = dados_fiis.get('baixas', [])[:5]
        
        # Filtra as baixas que têm P/VP e ordena por menor P/VP
        oportunidades_pvp = [
            f for f in maiores_baixas 
            if f.get('pvp') and f['pvp'] > 0
        ]
        oportunidades_pvp.sort(key=lambda x: x.get('pvp', 999))
        
        if oportunidades_pvp:
            mensagem += "💎 <b>OPORTUNIDADES P/VP (TOP 5 Baixas):</b>\n"
            for i, fii in enumerate(oportunidades_pvp, 1):
                ticker = fii['ticker'].replace('.SA', '')
                desconto = (1 - fii['pvp']) * 100 if fii['pvp'] < 1 else 0
                mensagem += f"{i}. <b>{ticker}</b>: P/VP {fii['pvp']:.2f}"
                if desconto > 0:
                    mensagem += f" (Desconto: {desconto:.1f}%)"
                mensagem += f"\n   {self.formatar_variacao(fii['variacao'])}"
                if fii.get('dy'):
                    mensagem += f" | DY: {fii['dy']:.2f}%"
                mensagem += f" | Preço: R$ {fii['preco']:.2f}"
                mensagem += "\n"
            mensagem += "\n"
        else:
            mensagem += "💎 <b>OPORTUNIDADES P/VP:</b>\n"
            mensagem += "   Sem dados de P/VP nas maiores baixas\n\n"
        
        mensagem += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        mensagem += "💡 Próxima atualização em 30 minutos\n"
        mensagem += "🌐 Acesse o painel completo em http://localhost:5173"
        
        return mensagem
    
    def formatar_alerta_personalizado(self, ticker, dados_fii, tipo_alerta):
        """
        Formata um alerta personalizado para um FII específico
        
        Args:
            ticker (str): Ticker do FII
            dados_fii (dict): Dados do FII
            tipo_alerta (str): Tipo do alerta ('alta', 'baixa', 'desconto')
        
        Returns:
            str: Mensagem formatada
        """
        agora = datetime.now().strftime('%d/%m/%Y %H:%M')
        ticker_limpo = ticker.replace('.SA', '')
        
        if tipo_alerta == 'alta':
            emoji = "🚀"
            titulo = "ALTA SIGNIFICATIVA"
        elif tipo_alerta == 'baixa':
            emoji = "⚠️"
            titulo = "BAIXA SIGNIFICATIVA"
        else:
            emoji = "💎"
            titulo = "OPORTUNIDADE DE DESCONTO"
        
        mensagem = f"""{emoji} <b>{titulo}</b> {emoji}
📅 {agora}

<b>{ticker_limpo}</b>
━━━━━━━━━━━━━━━━━━━━━━━━

💰 Preço: R$ {dados_fii['preco']:.2f}
{self.formatar_variacao(dados_fii['variacao'])}
"""
        
        if dados_fii.get('dy'):
            mensagem += f"📊 Dividend Yield: {dados_fii['dy']:.2f}%\n"
        
        if dados_fii.get('pvp'):
            mensagem += f"📈 P/VP: {dados_fii['pvp']:.2f}"
            if dados_fii['pvp'] < 1:
                desconto = (1 - dados_fii['pvp']) * 100
                mensagem += f" (Desconto: {desconto:.1f}%)"
            mensagem += "\n"
        
        if dados_fii.get('volume'):
            mensagem += f"📦 Volume: {dados_fii['volume']:,}\n"
        
        return mensagem
    
    async def enviar_alerta_resumo(self, dados_fiis, total_analisados):
        """
        Envia um alerta resumido com as principais variações
        
        Args:
            dados_fiis (dict): Dados dos FIIs
            total_analisados (int): Total de FIIs analisados
        
        Returns:
            bool: True se enviou com sucesso
        """
        mensagem = self.formatar_alerta_resumo(dados_fiis, total_analisados)
        return await self.enviar_mensagem(mensagem)
    
    async def enviar_alerta_personalizado(self, ticker, dados_fii, tipo_alerta):
        """
        Envia um alerta personalizado para um FII específico
        
        Args:
            ticker (str): Ticker do FII
            dados_fii (dict): Dados do FII
            tipo_alerta (str): Tipo do alerta
        
        Returns:
            bool: True se enviou com sucesso
        """
        mensagem = self.formatar_alerta_personalizado(ticker, dados_fii, tipo_alerta)
        return await self.enviar_mensagem(mensagem)
    
    async def testar_conexao(self):
        """
        Testa a conexão com o bot do Telegram
        
        Returns:
            bool: True se a conexão foi bem-sucedida
        """
        try:
            me = await self.bot.get_me()
            print(f"✅ Conectado ao bot: @{me.username}")
            
            # Envia mensagem de teste
            mensagem_teste = """✅ <b>Bot de FIIs Conectado!</b>

🤖 O sistema de notificações está ativo.
⏰ Você receberá atualizações a cada 30 minutos.

📊 Monitorando FIIs em tempo real...
"""
            sucesso = await self.enviar_mensagem(mensagem_teste)
            
            if sucesso:
                print(f"✅ Mensagem de teste enviada para chat_id: {self.chat_id}")
            
            return sucesso
            
        except TelegramError as e:
            print(f"❌ Erro ao conectar com o bot: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado: {str(e)}")
            return False


def run_async(coro):
    """
    Helper para executar funções async de forma síncrona
    
    Args:
        coro: Coroutine a ser executada
    
    Returns:
        Resultado da coroutine
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


# Exemplo de uso
if __name__ == "__main__":
    # Testa o notificador
    try:
        notifier = TelegramNotifier()
        print("🔄 Testando conexão com o Telegram...")
        
        sucesso = run_async(notifier.testar_conexao())
        
        if sucesso:
            print("✅ Teste concluído com sucesso!")
        else:
            print("❌ Falha no teste de conexão")
            
    except ValueError as e:
        print(str(e))
        print("\n💡 Configure as variáveis de ambiente TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID no arquivo .env")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

