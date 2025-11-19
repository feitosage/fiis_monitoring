# 📊 Monitor de FIIs - Yahoo Finance

Sistema profissional para acompanhamento de Fundos Imobiliários (FIIs) em tempo real, com design premium dark mode e análise por IA.

---

## 🚀 Início Rápido

### Instalação Automática (Recomendado)

**macOS/Linux:**
```bash
./start.sh
```

**Windows:**
```bash
start.bat
```

O script detecta automaticamente portas disponíveis e instala todas as dependências.

Depois de alguns segundos, acesse: **http://localhost:5173**

---

## 🔐 Configuração de Chaves e Credenciais

### ⚡ Método Rápido (Interativo)

Execute o script de configuração:

```bash
python configurar_chaves.py
```

O script irá:
- ✅ Guiá-lo passo a passo
- ✅ Validar os formatos das chaves
- ✅ Criar o arquivo `.env` automaticamente
- ✅ Aplicar permissões de segurança

### 📋 Chaves Necessárias

| Chave | Status | Função |
|-------|--------|--------|
| `OPENAI_API_KEY` | ⚠️ Opcional | Análise de IA no Painel Geral |
| `TELEGRAM_BOT_TOKEN` | ✅ Obrigatória* | Autenticação do bot no Telegram |
| `TELEGRAM_CHAT_ID` | ✅ Obrigatória* | Destino das notificações |

*Obrigatórias apenas para usar notificações no Telegram

### 🔑 Como Obter as Chaves

#### 1. OpenAI API Key (Opcional)

1. Acesse: https://platform.openai.com/api-keys
2. Faça login e clique em **"Create new secret key"**
3. Copie a chave (formato: `sk-proj-...`)
4. Cole no `.env`: `OPENAI_API_KEY=sk-proj-...`

**Custo**: ~$0.01 USD por análise (modelo gpt-4o-mini)

#### 2. Telegram Bot Token (Obrigatória para notificações)

1. Procure `@BotFather` no Telegram
2. Envie `/newbot`
3. Escolha nome e username (deve terminar com 'bot')
4. **Copie o token** fornecido
5. Cole no `.env`: `TELEGRAM_BOT_TOKEN=1234567890:ABC...`

#### 3. Telegram Chat ID (Obrigatória para notificações)

**Método Automático (Recomendado):**
1. Inicie conversa com seu bot (clique em "Start")
2. Execute: `cd backend && python enviar_teste.py`
3. O script mostrará seu Chat ID automaticamente

**Método Manual:**
1. Envie mensagem para seu bot
2. Acesse: `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
3. Procure por `"chat":{"id":123456789}`
4. Cole no `.env`: `TELEGRAM_CHAT_ID=123456789`

### 📝 Configuração Manual

Se preferir configurar manualmente:

```bash
# 1. Copie o arquivo de exemplo
cp .env.example backend/.env

# 2. Edite com suas chaves
nano backend/.env

# 3. Teste as configurações
cd backend
python enviar_teste.py
python testar_notificacao.py
```

### 🔒 Segurança das Credenciais

✅ **O projeto já faz:**
- `.env` está no `.gitignore` (não vai para o Git)
- Permissões restritivas aplicadas automaticamente
- Exemplos usam placeholders

⚠️ **Você DEVE fazer:**
- **NUNCA** compartilhar o arquivo `.env`
- **NUNCA** fazer commit de chaves no Git
- **SEMPRE** revogar chaves comprometidas
- Usar gerenciador de senhas para backup

### 🆘 Problemas Comuns

#### ❌ "TELEGRAM_BOT_TOKEN não configurado"
```bash
python configurar_chaves.py
```

#### ❌ "Erro ao enviar mensagem no Telegram"
1. Verifique se clicou em **"Start"** no bot
2. Confirme se o token está correto
3. Teste: `cd backend && python telegram_notifier.py`

#### ❌ "OpenAI API não configurada"
- Se não quiser IA: ignore este erro (resto funciona)
- Se quiser IA: configure a chave no `.env`

---

## 🎯 Funcionalidades Principais

### 📊 Painel Geral do Mercado
- **16 FIIs monitorados** automaticamente
- Top 5 maiores altas 🚀
- Top 5 maiores baixas 💎
- Estatísticas do mercado em tempo real
- Identificação de oportunidades

### 📈 Análise Individual de FIIs
- **Cotações históricas** com 9 períodos (1d até máximo)
- **Gráficos profissionais** (área/linha) com Recharts
- **Média móvel de 20 dias** (indicador técnico)
- **Análise técnica automática** (tendência, volatilidade, amplitude)
- **Histórico de dividendos** com análise completa
- **Dividend Yield destacado** e métricas de consistência

### 🤖 Análise de IA Setorial
- Análise contextual do mercado com OpenAI
- Avalia movimentos por setor (Logística, Shoppings, Lajes, CRI, Híbridos)
- Relaciona com fatores macroeconômicos (Selic, PIB, consumo)
- **Destaque de oportunidades táticas** (descontos P/VP)
- Estrutura clara em 4 parágrafos

### 📱 Notificações no Telegram
- Alertas automáticos a cada 1 hora (personalizável)
- Resumo completo do mercado
- Top 5 altas e baixas
- Oportunidades de desconto P/VP < 0.95
- Estatísticas gerais

### 🎨 Design Premium
- **Dark theme sofisticado** inspirado em Bloomberg Terminal
- Paleta investment-focused (verde bull, vermelho bear, ciano dividendos)
- **Animações suaves** e efeitos glow
- **Alto contraste** onde importa
- **Sidebar colapsável** para mais espaço

---

## 🛠️ Tecnologias

### Backend
- **Python 3.8+** com Flask
- **yfinance 0.2.66** - Dados do Yahoo Finance
- **OpenAI GPT-4** - Análise de IA
- **python-telegram-bot** - Notificações
- **BeautifulSoup4** - Web scraping

### Frontend
- **React 18** com Vite
- **Recharts** - Gráficos profissionais
- **Lucide Icons** - Ícones modernos
- **Tipografia:** Inter + JetBrains Mono

---

## 📋 Instalação Manual

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Servidor backend em: `http://localhost:5001`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend em: `http://localhost:5173`

### 3. Configurar Notificações Telegram

```bash
# Configure as chaves
python configurar_chaves.py

# Teste a conexão
cd backend
python enviar_teste.py

# Teste notificação completa
python testar_notificacao.py

# Inicie o monitoramento (a cada 1 hora)
python telegram_monitor.py

# Personalizar intervalo (ex: 2 horas)
python telegram_monitor.py --intervalo 2

# Rodar em background
nohup python telegram_monitor.py > monitor.log 2>&1 &
```

---

## 🏗️ Estrutura do Projeto

```
fii_yahoo/
├── backend/
│   ├── app.py                    # API principal
│   ├── setores_fiis.py           # Classificação de setores
│   ├── telegram_monitor.py       # Bot de monitoramento
│   ├── telegram_notifier.py      # Envio de mensagens
│   ├── enviar_teste.py           # Teste de conexão
│   ├── testar_notificacao.py     # Teste completo
│   └── requirements.txt          # Dependências Python
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # App principal
│   │   ├── components/
│   │   │   ├── PainelGeralTab.jsx    # Painel do mercado
│   │   │   ├── CotacoesTab.jsx       # Gráfico de cotações
│   │   │   ├── DividendosTab.jsx     # Histórico dividendos
│   │   │   ├── FIIList.jsx           # Sidebar de FIIs
│   │   │   └── SearchBar.jsx         # Busca
│   │   └── utils/
│   │       └── chartUtils.js         # Utilidades
│   └── package.json              # Dependências Node
│
├── configurar_chaves.py          # Script de configuração
├── .env.example                  # Template de credenciais
├── .gitignore                    # Arquivos ignorados pelo Git
├── start.sh                      # Inicialização macOS/Linux
├── start.bat                     # Inicialização Windows
└── README.md                     # Este arquivo
```

---

## 📡 API Endpoints

### Geral
- `GET /api/health` - Health check
- `GET /api/fiis` - Lista 16 FIIs populares com timestamp

### FII Específico
- `GET /api/fii/<ticker>` - Informações detalhadas
- `GET /api/fii/<ticker>/cotacoes?periodo=1mo` - Histórico cotações
- `GET /api/fii/<ticker>/dividendos` - Histórico dividendos
- `GET /api/search?q=MXRF11` - Busca por ticker

### Análise IA
- `POST /api/analise-ia` - Análise setorial contextual

---

## 💡 Como Usar

### 1. Painel Geral
- Acesse `http://localhost:5173`
- Veja automaticamente 16 FIIs
- Top 5 altas (verde) e baixas (vermelho)
- Clique **"Atualizar"** para refresh

### 2. Buscar FII
- Digite o ticker na busca (ex: `MXRF11`)
- Pressione Enter
- O FII aparece na sidebar à esquerda
- Clique nele para ver detalhes

### 3. Analisar Cotações
- Aba **"📈 Cotações"**
- Escolha o período (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
- Toggle entre gráfico de **Área** ou **Linha**
- Veja **Média Móvel 20 dias** (linha dourada)
- Análise técnica automática abaixo

### 4. Analisar Dividendos
- Aba **"💰 Dividendos"**
- Veja DY destacado em ciano
- Filtre por período (6m, 1y, 2y, max)
- Gráfico de barras com média
- Análise de consistência e frequência

### 5. Gerar Análise de IA
- Aba **"🤖 Análise de IA"**
- Clique **"Gerar Análise"**
- Aguarde ~10-20 segundos
- Leia análise contextual setorial
- Veja oportunidades destacadas com 🔥

### 6. Sidebar
- Clique **◀** para ocultar
- Clique **▶** (botão flutuante) para mostrar
- Mais espaço para gráficos

---

## 🧪 FIIs Pré-configurados (16)

```
MXRF11  MCRE11  VGHF11  VISC11  RURA11  TRXF11  XPLG11  RZTR11
CPTS11  HSML11  PVBI11  OUJP11  VILG11  VRTA11  HGRU11  RBRP11
```

**Setores cobertos:**
- Logística (MXRF11, VILG11, etc.)
- Shoppings (VISC11, HSML11, etc.)
- Lajes Corporativas (CPTS11, etc.)
- Recebíveis Imobiliários (MXRF11, VRTA11)
- Híbridos (HGRU11, RBRP11)

---

## 📝 Comandos Úteis

### Backend
```bash
# Iniciar API
cd backend && source venv/bin/activate && python app.py

# Testar conexão Telegram
python enviar_teste.py

# Testar notificação completa
python testar_notificacao.py

# Monitoramento contínuo
python telegram_monitor.py

# Parar bot Telegram
pkill -f telegram_monitor.py
```

### Frontend
```bash
# Iniciar dev server
cd frontend && npm run dev

# Build para produção
npm run build

# Preview build
npm run preview
```

### Geral
```bash
# Configurar chaves (interativo)
python configurar_chaves.py

# Reiniciar tudo
./reiniciar.sh

# Testar portas
./testar_portas.sh

# Ver logs
tail -f backend.log
tail -f telegram_bot.log
```

---

## ⚠️ Solução de Problemas

### Porta já em uso
✅ **Solução:** Os scripts detectam automaticamente portas alternativas.

### Dados não carregam
- Verifique se o backend está rodando
- Verifique conexão com internet
- Alguns FIIs podem não ter dados completos no Yahoo Finance

### Erro "TELEGRAM_BOT_TOKEN não configurado"
- Execute: `python configurar_chaves.py`
- Ou crie manualmente: `backend/.env`

### Erro "Unauthorized" (Telegram)
- Token do bot incorreto
- Verifique no @BotFather

### Erro "Chat not found" (Telegram)
- Chat ID incorreto
- Se for grupo, adicione o bot ao grupo primeiro

### Datas incorretas
✅ **Corrigido:** Função `formatDate()` em `chartUtils.js` resolve timezone

### Gráfico de dividendos invertido
✅ **Corrigido:** Domínio `[0, max × 1.1]` resolve proporção das barras

---

## 🎨 Paleta de Cores

```css
Verde Bull      → #10b981  (altas, positivo)
Vermelho Bear   → #dc2626  (baixas, negativo)
Ciano Dividendos→ #06b6d4  (DY, destaque)
Violeta Acentos → #8b5cf6  (sidebar, ícones)
Backgrounds     → #020617 a #475569 (5 camadas)
```

---

## 📊 Features Premium

### Gráficos Avançados
- ✅ Toggle Área/Linha
- ✅ Média Móvel 20 dias (MM20)
- ✅ Linha de referência (média período)
- ✅ Active dot com glow
- ✅ Legenda completa
- ✅ Tooltip com 2 valores

### Análise Automática
- ✅ Tendência (alta/baixa)
- ✅ Volatilidade (%)
- ✅ Amplitude (R$)
- ✅ Variação absoluta
- ✅ Consistência de dividendos
- ✅ Frequência mensal

### UX/UI
- ✅ Animações suaves (shimmer, pulse, slide)
- ✅ Glow effects contextuais
- ✅ Alto contraste em variações
- ✅ Timestamps em 3 locais
- ✅ Loading spinners animados
- ✅ Badges informativos
- ✅ Responsivo completo

---

## 💰 Exemplo de Análise

### Telegram
```
🔔 MONITOR DE FIIs 🔔
📅 17/11/2025 14:30

📊 RESUMO DO MERCADO:
• Total: 16 FIIs
• 📈 Em alta: 9 (56.3%)
• 📉 Em baixa: 6 (37.5%)
• Variação média: +0.45%

🔥 TOP 5 MAIORES ALTAS:
1. MXRF11: R$ 10.45 📈 +2.15%
   DY: 12.50% | P/VP: 0.98
...

💎 OPORTUNIDADES (P/VP < 0.95):
• HGRU11: P/VP 0.92 (8% desconto)
  📉 -1.20% | DY: 10.50%
```

### Web (Análise de IA)
```
📊 Leitura Geral do Dia
Mercado de FIIs misto hoje, com shoppings em recuperação 
após dados de consumo. Logística pressionada por custos...

📈 Análise de Altas
Setor de Shoppings lidera com HSML11 (+2.1%) e VISC11 
(+1.8%), refletindo otimismo pós-Black Friday...

📉 Análise de Baixas
Lajes Corporativas sob pressão com CPTS11 (-1.5%), 
impactado por vacância em SP...

💎 Oportunidades Táticas
🔥 HGRU11 (Híbrido) com P/VP 0.92 (8% desconto) e DY 10.5%
Desconto aumentando, sinal de possível entrada...
```

---

## 🚧 Sugestões de Melhorias

- [ ] Watchlist personalizada
- [ ] Comparação lado-a-lado de FIIs
- [ ] Alertas de preço customizados
- [ ] Mais indicadores técnicos (RSI, MACD, Bollinger)
- [ ] Exportar relatórios PDF/Excel
- [ ] Cache local para performance
- [ ] PWA (Progressive Web App)
- [ ] Sistema de autenticação

---

## 🎓 Recursos de Aprendizado

### APIs Utilizadas
- [Yahoo Finance via yfinance](https://pypi.org/project/yfinance/)
- [OpenAI API](https://platform.openai.com/docs)
- [Telegram Bot API](https://core.telegram.org/bots/api)

### Bibliotecas Frontend
- [Recharts](https://recharts.org/)
- [Lucide Icons](https://lucide.dev/)
- [React](https://react.dev/)

---

## 🙏 Créditos

- **Yahoo Finance** - Dados de mercado
- **yfinance** - Biblioteca Python
- **OpenAI** - Análise de IA
- **Recharts** - Gráficos React
- **Comunidade Python e React**

---

## 📄 Licença

Este projeto é livre para uso pessoal e educacional.

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a seção **Solução de Problemas** acima
2. Consulte os logs: `backend.log` e `telegram_bot.log`
3. Teste a API diretamente: `curl http://localhost:5001/api/health`

---

**Desenvolvido com ❤️ para facilitar o acompanhamento de investimentos em FIIs**

*Versão: 3.0.0 - Novembro 2025*

---

## 🎯 Resumo de 30 Segundos

1. **Clone o projeto**
2. **Configure:** `python configurar_chaves.py` (configure suas credenciais)
3. **Execute:** `./start.sh` (macOS/Linux) ou `start.bat` (Windows)
4. **Acesse:** http://localhost:5173
5. **Explore:** Painel Geral → Busque FII → Analise gráficos
6. **Telegram (opcional):** `cd backend && python telegram_monitor.py`
7. **Aproveite!** 📊💰✨

---
