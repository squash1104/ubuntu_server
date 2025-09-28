#!/bin/bash

echo "🔍 DIAGNÓSTICO DOS SERVIÇOS DO SISTEMA"
echo "======================================"
echo ""

# Verificar PostgreSQL
echo "🐘 POSTGRESQL:"
echo "--------------"
# Verificar versão 16 (atual)
if systemctl list-units | grep -q postgresql@16-main; then
    echo "✅ Serviço postgresql@16-main encontrado"
    echo "   Status: $(systemctl is-active postgresql@16-main 2>/dev/null || echo 'inactive')"
    echo "   Habilitado: $(systemctl is-enabled postgresql@16-main 2>/dev/null || echo 'disabled')"
else
    echo "❌ Serviço postgresql@16-main NÃO encontrado"
fi

# Verificar versão 15 (legacy)
if systemctl list-unit-files | grep -q postgresql@15-main; then
    echo "ℹ️  Serviço postgresql@15-main encontrado (versão antiga)"
    echo "   Status: $(systemctl is-active postgresql@15-main 2>/dev/null || echo 'inactive')"
    echo "   Habilitado: $(systemctl is-enabled postgresql@15-main 2>/dev/null || echo 'disabled')"
fi

# Verificar se o PostgreSQL está rodando de outra forma
if pgrep -f postgres >/dev/null; then
    echo "✅ Processo PostgreSQL está rodando"
else
    echo "❌ Nenhum processo PostgreSQL encontrado"
fi

echo ""

# Verificar Daphne
echo "🌐 DAPHNE:"
echo "----------"
if systemctl list-unit-files | grep -q daphne; then
    echo "✅ Serviço daphne encontrado"
    echo "   Status: $(systemctl is-active daphne 2>/dev/null || echo 'inactive')"
    echo "   Habilitado: $(systemctl is-enabled daphne 2>/dev/null || echo 'disabled')"
else
    echo "❌ Serviço daphne NÃO encontrado"
fi

# Verificar se o Daphne está rodando
if pgrep -f daphne >/dev/null; then
    echo "✅ Processo Daphne está rodando"
    echo "   PID: $(pgrep -f daphne)"
else
    echo "❌ Nenhum processo Daphne encontrado"
fi

echo ""

# Verificar Nginx
echo "🌍 NGINX:"
echo "---------"
if systemctl list-unit-files | grep -q nginx; then
    echo "✅ Serviço nginx encontrado"
    echo "   Status: $(systemctl is-active nginx 2>/dev/null || echo 'inactive')"
    echo "   Habilitado: $(systemctl is-enabled nginx 2>/dev/null || echo 'disabled')"
else
    echo "ℹ️  Serviço nginx NÃO encontrado (opcional)"
fi

echo ""

# Verificar Redis
echo "🔴 REDIS:"
echo "---------"
if systemctl list-unit-files | grep -q redis; then
    echo "✅ Serviço redis encontrado"
    echo "   Status: $(systemctl is-active redis 2>/dev/null || echo 'inactive')"
    echo "   Habilitado: $(systemctl is-enabled redis 2>/dev/null || echo 'disabled')"
else
    echo "ℹ️  Serviço redis NÃO encontrado (opcional)"
fi

echo ""

# Verificar Cloudflare Tunnel
echo "☁️ CLOUDFLARE TUNNEL:"
echo "---------------------"
if systemctl list-unit-files | grep -q cloudflared; then
    echo "✅ Serviço cloudflared encontrado"
    
    # Verificar o serviço específico do sisvot
    if systemctl list-unit-files | grep -q cloudflared-sisvot; then
        echo "✅ Serviço cloudflared-sisvot encontrado"
        echo "   Status: $(systemctl is-active cloudflared-sisvot 2>/dev/null || echo 'inactive')"
        echo "   Habilitado: $(systemctl is-enabled cloudflared-sisvot 2>/dev/null || echo 'disabled')"
    else
        echo "❌ Serviço cloudflared-sisvot NÃO encontrado"
    fi
    
    # Verificar o serviço principal
    echo "   Status (principal): $(systemctl is-active cloudflared 2>/dev/null || echo 'inactive')"
    echo "   Habilitado (principal): $(systemctl is-enabled cloudflared 2>/dev/null || echo 'disabled')"
else
    echo "❌ Serviço cloudflared NÃO encontrado"
fi

# Verificar se o cloudflared está rodando
if pgrep -f cloudflared >/dev/null; then
    echo "✅ Processo cloudflared está rodando"
    echo "   PID: $(pgrep -f cloudflared)"
else
    echo "❌ Nenhum processo cloudflared encontrado"
fi

echo ""

# Verificar conectividade
echo "🌐 CONECTIVIDADE:"
echo "-----------------"
echo "Testando porta 8000 (Daphne):"
if nc -z localhost 8000 2>/dev/null; then
    echo "✅ Porta 8000 está aberta e respondendo"
else
    echo "❌ Porta 8000 não está respondendo"
fi

echo "Testando porta 5432 (PostgreSQL):"
if nc -z localhost 5432 2>/dev/null; then
    echo "✅ Porta 5432 (PostgreSQL) está aberta e respondendo"
else
    echo "❌ Porta 5432 (PostgreSQL) não está respondendo"
fi

echo "Testando porta 20242 (Cloudflare Tunnel metrics):"
if nc -z localhost 20242 2>/dev/null; then
    echo "✅ Porta 20242 (Cloudflare Tunnel metrics) está aberta e respondendo"
else
    echo "❌ Porta 20242 (Cloudflare Tunnel metrics) não está respondendo"
fi

echo ""

# Verificar arquivos de serviço
echo "📁 ARQUIVOS DE SERVIÇO:"
echo "----------------------"
if [ -f "/etc/systemd/system/daphne.service" ]; then
    echo "✅ Arquivo daphne.service encontrado"
else
    echo "❌ Arquivo daphne.service NÃO encontrado"
fi

echo ""

# Verificar logs recentes
echo "📋 LOGS RECENTES:"
echo "----------------"
echo "Últimas 5 linhas do log do Daphne:"
journalctl -u daphne -n 5 --no-pager 2>/dev/null || echo "❌ Não foi possível acessar logs do Daphne"

echo ""
echo "Últimas 5 linhas do log do PostgreSQL 16:"
journalctl -u postgresql@16-main -n 5 --no-pager 2>/dev/null || echo "❌ Não foi possível acessar logs do PostgreSQL 16"

echo ""
echo "Últimas 5 linhas do log do Cloudflare Tunnel:"
journalctl -u cloudflared-sisvot -n 5 --no-pager 2>/dev/null || echo "❌ Não foi possível acessar logs do Cloudflare Tunnel"

echo ""
echo "🎯 RECOMENDAÇÕES:"
echo "================="

# Verificar se PostgreSQL está habilitado
if ! systemctl is-enabled postgresql@16-main >/dev/null 2>&1; then
    echo "❌ PostgreSQL 16 não está habilitado para iniciar automaticamente"
    echo "   Execute: sudo systemctl enable postgresql@16-main"
fi

# Verificar se Daphne está habilitado
if ! systemctl is-enabled daphne >/dev/null 2>&1; then
    echo "❌ Daphne não está habilitado para iniciar automaticamente"
    echo "   Execute: sudo systemctl enable daphne"
fi

# Verificar se os serviços estão rodando
if ! systemctl is-active postgresql@16-main >/dev/null 2>&1; then
    echo "❌ PostgreSQL 16 não está rodando"
    echo "   Execute: sudo systemctl start postgresql@16-main"
fi

if ! systemctl is-active daphne >/dev/null 2>&1; then
    echo "❌ Daphne não está rodando"
    echo "   Execute: sudo systemctl start daphne"
fi

# Verificar Cloudflare Tunnel
if ! systemctl is-enabled cloudflared-sisvot >/dev/null 2>&1; then
    echo "❌ Cloudflare Tunnel não está habilitado para iniciar automaticamente"
    echo "   Execute: sudo systemctl enable cloudflared-sisvot"
fi

if ! systemctl is-active cloudflared-sisvot >/dev/null 2>&1; then
    echo "❌ Cloudflare Tunnel não está rodando"
    echo "   Execute: sudo systemctl start cloudflared-sisvot"
fi

echo ""
echo "✅ Diagnóstico concluído!"
