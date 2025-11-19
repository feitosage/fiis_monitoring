#!/usr/bin/env python3
"""
Script interativo para configurar as chaves de API do projeto FII Yahoo
"""
import os
import sys
from pathlib import Path

def exibir_banner():
    """Exibe banner inicial"""
    print("\n" + "═" * 70)
    print("🔐  CONFIGURAÇÃO DE CHAVES E VARIÁVEIS DE AMBIENTE")
    print("    Projeto: Monitor de FIIs - Yahoo Finance")
    print("═" * 70 + "\n")

def verificar_arquivo_env():
    """Verifica se arquivo .env já existe"""
    env_paths = [
        Path("backend/.env"),
        Path(".env")
    ]
    
    for path in env_paths:
        if path.exists():
            print(f"⚠️  Arquivo {path} já existe!")
            resposta = input("\n   Deseja sobrescrever? (s/N): ").strip().lower()
            if resposta != 's':
                print("\n❌ Operação cancelada.")
                return None
            return path
    
    # Se não existe, usa backend/.env como padrão
    return Path("backend/.env")

def obter_chave_openai():
    """Solicita chave da OpenAI"""
    print("\n" + "─" * 70)
    print("📝 1. OPENAI API KEY (Análise de IA)")
    print("─" * 70)
    print("\n💡 Como obter:")
    print("   1. Acesse: https://platform.openai.com/api-keys")
    print("   2. Faça login e clique em 'Create new secret key'")
    print("   3. Copie a chave (formato: sk-proj-...)")
    print("\n⚠️  OPCIONAL: Deixe em branco para pular (análise de IA não funcionará)")
    
    chave = input("\n🔑 Cole sua OPENAI_API_KEY: ").strip()
    
    if not chave:
        print("   ⏭️  Pulado - Análise de IA desabilitada")
        return None
    
    if not chave.startswith("sk-"):
        print("   ⚠️  Atenção: Formato incomum (esperado: sk-...)")
        confirmar = input("   Continuar mesmo assim? (s/N): ").strip().lower()
        if confirmar != 's':
            return obter_chave_openai()
    
    print("   ✅ Chave OpenAI configurada!")
    return chave

def obter_telegram_bot_token():
    """Solicita token do bot do Telegram"""
    print("\n" + "─" * 70)
    print("📝 2. TELEGRAM BOT TOKEN (Notificações)")
    print("─" * 70)
    print("\n💡 Como obter:")
    print("   1. Abra o Telegram e procure por @BotFather")
    print("   2. Envie: /newbot")
    print("   3. Escolha um nome e username para o bot")
    print("   4. Copie o token (formato: 1234567890:ABC...)")
    print("\n⚠️  OBRIGATÓRIO para notificações no Telegram")
    print("   (Deixe em branco para pular - bot não funcionará)")
    
    token = input("\n🔑 Cole seu TELEGRAM_BOT_TOKEN: ").strip()
    
    if not token:
        print("   ⏭️  Pulado - Notificações do Telegram desabilitadas")
        return None
    
    if ':' not in token or not token.split(':')[0].isdigit():
        print("   ⚠️  Atenção: Formato inválido (esperado: número:texto)")
        confirmar = input("   Continuar mesmo assim? (s/N): ").strip().lower()
        if confirmar != 's':
            return obter_telegram_bot_token()
    
    print("   ✅ Token do bot configurado!")
    return token

def obter_telegram_chat_id():
    """Solicita Chat ID do Telegram"""
    print("\n" + "─" * 70)
    print("📝 3. TELEGRAM CHAT ID (Destino das notificações)")
    print("─" * 70)
    print("\n💡 Como obter (MÉTODO FÁCIL):")
    print("   1. Procure seu bot no Telegram")
    print("   2. Clique em 'Start' ou envie qualquer mensagem")
    print("   3. Execute: cd backend && python enviar_teste.py")
    print("   4. O script mostrará seu Chat ID")
    print("\n💡 Como obter (MÉTODO MANUAL):")
    print("   1. Envie uma mensagem para seu bot")
    print("   2. Acesse: https://api.telegram.org/bot<SEU_TOKEN>/getUpdates")
    print("   3. Procure por: \"chat\":{\"id\":123456789}")
    print("   4. Copie o número do id")
    print("\n⚠️  OBRIGATÓRIO se você configurou o bot token")
    
    chat_id = input("\n🔑 Digite seu TELEGRAM_CHAT_ID: ").strip()
    
    if not chat_id:
        print("   ⏭️  Pulado - Notificações do Telegram desabilitadas")
        return None
    
    # Remove possível '-' no início (grupos)
    if chat_id.startswith('-'):
        if not chat_id[1:].isdigit():
            print("   ⚠️  Atenção: Formato inválido (esperado: número ou -número)")
            confirmar = input("   Continuar mesmo assim? (s/N): ").strip().lower()
            if confirmar != 's':
                return obter_telegram_chat_id()
    elif not chat_id.isdigit():
        print("   ⚠️  Atenção: Formato inválido (esperado: número ou -número)")
        confirmar = input("   Continuar mesmo assim? (s/N): ").strip().lower()
        if confirmar != 's':
            return obter_telegram_chat_id()
    
    print("   ✅ Chat ID configurado!")
    return chat_id

def obter_configuracoes_opcionais():
    """Solicita configurações opcionais"""
    print("\n" + "─" * 70)
    print("📝 4. CONFIGURAÇÕES OPCIONAIS")
    print("─" * 70)
    print("\n⚙️  Pressione ENTER para usar valores padrão")
    
    config = {}
    
    # Porta do Flask
    print("\n🌐 Porta do servidor Flask:")
    porta = input("   FLASK_RUN_PORT [5001]: ").strip()
    config['FLASK_RUN_PORT'] = porta if porta else '5001'
    
    # Alerta de alta
    print("\n📈 Variação mínima para alertar ALTA (%):")
    alta = input("   ALERTA_ALTA_MINIMA [1.5]: ").strip()
    config['ALERTA_ALTA_MINIMA'] = alta if alta else '1.5'
    
    # Alerta de baixa
    print("\n📉 Variação mínima para alertar BAIXA (%):")
    baixa = input("   ALERTA_BAIXA_MINIMA [-1.5]: ").strip()
    config['ALERTA_BAIXA_MINIMA'] = baixa if baixa else '-1.5'
    
    # Alerta de desconto P/VP
    print("\n💎 P/VP máximo para alertar DESCONTO:")
    pvp = input("   ALERTA_DESCONTO_PVP [0.95]: ").strip()
    config['ALERTA_DESCONTO_PVP'] = pvp if pvp else '0.95'
    
    print("\n   ✅ Configurações opcionais definidas!")
    return config

def criar_arquivo_env(caminho, chaves):
    """Cria arquivo .env com as chaves fornecidas"""
    print("\n" + "─" * 70)
    print("💾 Criando arquivo de configuração...")
    print("─" * 70)
    
    # Cria diretório se não existir
    caminho.parent.mkdir(parents=True, exist_ok=True)
    
    conteudo = [
        "# ════════════════════════════════════════════════════════════════",
        "# CONFIGURAÇÃO DE CHAVES - FII YAHOO",
        f"# Gerado automaticamente em: {Path.cwd()}",
        "# ⚠️  NÃO COMPARTILHE ESTE ARQUIVO!",
        "# ════════════════════════════════════════════════════════════════",
        "",
        "# OpenAI API (Análise de IA)",
    ]
    
    if chaves.get('OPENAI_API_KEY'):
        conteudo.append(f"OPENAI_API_KEY={chaves['OPENAI_API_KEY']}")
    else:
        conteudo.append("# OPENAI_API_KEY=sk-proj-... (não configurado)")
    
    conteudo.extend([
        "",
        "# Telegram Bot (Notificações)",
    ])
    
    if chaves.get('TELEGRAM_BOT_TOKEN'):
        conteudo.append(f"TELEGRAM_BOT_TOKEN={chaves['TELEGRAM_BOT_TOKEN']}")
    else:
        conteudo.append("# TELEGRAM_BOT_TOKEN=1234567890:ABC... (não configurado)")
    
    if chaves.get('TELEGRAM_CHAT_ID'):
        conteudo.append(f"TELEGRAM_CHAT_ID={chaves['TELEGRAM_CHAT_ID']}")
    else:
        conteudo.append("# TELEGRAM_CHAT_ID=123456789 (não configurado)")
    
    conteudo.extend([
        "",
        "# Configurações do servidor",
        f"FLASK_RUN_PORT={chaves.get('FLASK_RUN_PORT', '5001')}",
        "",
        "# Configurações de alertas",
        f"ALERTA_ALTA_MINIMA={chaves.get('ALERTA_ALTA_MINIMA', '1.5')}",
        f"ALERTA_BAIXA_MINIMA={chaves.get('ALERTA_BAIXA_MINIMA', '-1.5')}",
        f"ALERTA_DESCONTO_PVP={chaves.get('ALERTA_DESCONTO_PVP', '0.95')}",
        ""
    ])
    
    try:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write('\n'.join(conteudo))
        
        print(f"\n✅ Arquivo criado com sucesso: {caminho}")
        
        # Define permissões restritivas (apenas leitura/escrita para o dono)
        try:
            os.chmod(caminho, 0o600)
            print("🔒 Permissões de segurança aplicadas (apenas você pode ler)")
        except:
            print("⚠️  Não foi possível definir permissões (pode ser necessário manualmente)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao criar arquivo: {str(e)}")
        return False

def exibir_resumo(chaves):
    """Exibe resumo das configurações"""
    print("\n" + "═" * 70)
    print("📊 RESUMO DA CONFIGURAÇÃO")
    print("═" * 70)
    
    status_openai = "✅ Configurado" if chaves.get('OPENAI_API_KEY') else "❌ Não configurado"
    status_telegram = "✅ Configurado" if (chaves.get('TELEGRAM_BOT_TOKEN') and chaves.get('TELEGRAM_CHAT_ID')) else "❌ Não configurado"
    
    print(f"\n🤖 OpenAI (Análise de IA):      {status_openai}")
    print(f"📱 Telegram (Notificações):     {status_telegram}")
    print(f"🌐 Porta do servidor:           {chaves.get('FLASK_RUN_PORT', '5001')}")
    print(f"📈 Alerta de alta mínima:       {chaves.get('ALERTA_ALTA_MINIMA', '1.5')}%")
    print(f"📉 Alerta de baixa mínima:      {chaves.get('ALERTA_BAIXA_MINIMA', '-1.5')}%")
    print(f"💎 Alerta de desconto P/VP:     < {chaves.get('ALERTA_DESCONTO_PVP', '0.95')}")
    
    print("\n" + "─" * 70)
    
    if not chaves.get('OPENAI_API_KEY'):
        print("\n⚠️  OpenAI não configurado:")
        print("   • A análise de IA no Painel Geral não funcionará")
        print("   • Você pode configurar depois editando o arquivo .env")
    
    if not (chaves.get('TELEGRAM_BOT_TOKEN') and chaves.get('TELEGRAM_CHAT_ID')):
        print("\n⚠️  Telegram não configurado:")
        print("   • As notificações automáticas não funcionarão")
        print("   • Você pode configurar depois editando o arquivo .env")

def exibir_proximos_passos(caminho_env):
    """Exibe próximos passos após configuração"""
    print("\n" + "═" * 70)
    print("🚀 PRÓXIMOS PASSOS")
    print("═" * 70)
    
    print("\n1️⃣  Testar conexão com Telegram (se configurado):")
    print("    cd backend")
    print("    python enviar_teste.py")
    
    print("\n2️⃣  Testar notificação completa com dados de FIIs:")
    print("    cd backend")
    print("    python testar_notificacao.py")
    
    print("\n3️⃣  Iniciar o servidor backend:")
    print("    cd backend")
    print("    python app.py")
    
    print("\n4️⃣  Iniciar o monitoramento automático (opcional):")
    print("    cd backend")
    print("    python telegram_monitor.py")
    
    print("\n" + "─" * 70)
    print("\n💡 DICAS:")
    print("   • Consulte CONFIGURACAO_CHAVES.md para mais detalhes")
    print("   • Mantenha suas chaves em segurança!")
    print("   • NUNCA compartilhe o arquivo .env")
    
    print("\n" + "═" * 70)

def main():
    """Função principal"""
    try:
        exibir_banner()
        
        # Verifica se arquivo já existe
        caminho_env = verificar_arquivo_env()
        if caminho_env is None:
            return
        
        # Coleta as chaves
        chaves = {}
        
        chaves['OPENAI_API_KEY'] = obter_chave_openai()
        chaves['TELEGRAM_BOT_TOKEN'] = obter_telegram_bot_token()
        
        if chaves['TELEGRAM_BOT_TOKEN']:
            chaves['TELEGRAM_CHAT_ID'] = obter_telegram_chat_id()
        
        config_opcional = obter_configuracoes_opcionais()
        chaves.update(config_opcional)
        
        # Exibe resumo
        exibir_resumo(chaves)
        
        # Confirma criação
        print("\n" + "─" * 70)
        confirmar = input("\n💾 Salvar configurações? (S/n): ").strip().lower()
        
        if confirmar == 'n':
            print("\n❌ Operação cancelada.")
            return
        
        # Cria arquivo
        if criar_arquivo_env(caminho_env, chaves):
            exibir_proximos_passos(caminho_env)
            print("\n✅ Configuração concluída com sucesso!\n")
        else:
            print("\n❌ Falha ao criar arquivo de configuração.\n")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()

