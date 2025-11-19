#!/bin/bash

# Script para reiniciar Backend e Frontend com as novas correções

clear

cat << 'EOF'
═══════════════════════════════════════════════════════════════════════
🚀 REINICIANDO APLICAÇÃO COM CORREÇÕES
═══════════════════════════════════════════════════════════════════════

✅ Novas funcionalidades:
   • Alerta vermelho para dados desatualizados
   • Logs super detalhados no console
   • Fontes mais claras nos títulos
   • Bypass de cache agressivo

═══════════════════════════════════════════════════════════════════════
EOF

echo ""
echo "🔄 Matando processos antigos deste projeto..."
# Mata apenas processos nas portas específicas deste projeto (5001 e 5173)
lsof -ti:5001 2>/dev/null | xargs kill 2>/dev/null
lsof -ti:5173 2>/dev/null | xargs kill 2>/dev/null
sleep 2

# Limpa cache do Vite
echo "🧹 Limpando cache do Vite..."
rm -rf frontend/node_modules/.vite 2>/dev/null

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "📡 Iniciando BACKEND (porta 5001)..."
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Inicia backend em nova janela do terminal
osascript << APPLESCRIPT
tell application "Terminal"
    do script "cd '$PWD/backend' && source venv/bin/activate && python app.py"
end tell
APPLESCRIPT

sleep 3

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "🎨 Iniciando FRONTEND (porta 5173)..."
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Inicia frontend em nova janela do terminal
osascript << APPLESCRIPT
tell application "Terminal"
    do script "cd '$PWD/frontend' && npm run dev"
end tell
APPLESCRIPT

sleep 3

cat << 'EOF'

═══════════════════════════════════════════════════════════════════════
✅ APLICAÇÃO REINICIADA!
═══════════════════════════════════════════════════════════════════════

🌐 URLs:
   • Frontend: http://localhost:5173
   • Backend:  http://localhost:5001

═══════════════════════════════════════════════════════════════════════
🧪 PRÓXIMOS PASSOS - TESTE AGORA:
═══════════════════════════════════════════════════════════════════════

1. 🔥 ABRA MODO ANÔNIMO:
   • Pressione: Cmd + Shift + N
   • Vá para: http://localhost:5173
   
2. 🔍 ABRA O CONSOLE:
   • Pressione: F12
   • Vá para aba "Console"
   
3. 🔎 BUSQUE UM FII:
   • Digite: MXRF11
   • Clique em buscar
   
4. 📊 VERIFIQUE O CONSOLE:
   • Deve aparecer log detalhado com:
     "Última data: 2025-10-22"
   • E lista das 5 últimas datas
   
5. ⚠️ VERIFIQUE SE APARECE ALERTA VERMELHO:
   • Se aparecer = ainda tem cache
   • Se NÃO aparecer = dados corretos!

═══════════════════════════════════════════════════════════════════════

💡 DICA: Se ainda aparecer dados antigos (21/10):
   1. O alerta vermelho vai guiar você
   2. Clique no botão "Forçar Atualização" do alerta
   3. Ou siga as instruções do alerta

═══════════════════════════════════════════════════════════════════════
📖 Mais info: SOLUCAO_CACHE_FINAL.md
═══════════════════════════════════════════════════════════════════════

EOF

