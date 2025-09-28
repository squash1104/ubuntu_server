#!/bin/bash

echo "🔧 CORRIGINDO CONFIGURAÇÃO DE INICIALIZAÇÃO AUTOMÁTICA"
echo "====================================================="
echo ""

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script precisa ser executado como root ou com sudo"
    echo "Execute: sudo ./fix_autostart.sh"
    exit 1
fi

echo "📊 Verificando serviços atuais..."

# PostgreSQL 16
echo "🐘 PostgreSQL 16:"
echo "   Status: $(systemctl is-active postgresql@16-main)"
echo "   Habilitado: $(systemctl is-enabled postgresql@16-main)"

# Habilitar PostgreSQL 16 permanentemente
echo "🔧 Habilitando PostgreSQL 16 para iniciar automaticamente..."
systemctl enable postgresql@16-main

# Daphne
echo "🌐 Daphne:"
echo "   Status: $(systemctl is-active daphne)"
echo "   Habilitado: $(systemctl is-enabled daphne)"

# Verificar se Daphne está habilitado
if systemctl is-enabled daphne >/dev/null 2>&1; then
    echo "✅ Daphne já está habilitado para iniciar automaticamente"
else
    echo "🔧 Habilitando Daphne para iniciar automaticamente..."
    systemctl enable daphne
fi

# Nginx (se estiver instalado)
if systemctl list-unit-files | grep -q nginx; then
    echo "🌍 Nginx:"
    echo "   Status: $(systemctl is-active nginx)"
    echo "   Habilitado: $(systemctl is-enabled nginx)"
    
    if systemctl is-enabled nginx >/dev/null 2>&1; then
        echo "✅ Nginx já está habilitado para iniciar automaticamente"
    else
        echo "🔧 Habilitando Nginx para iniciar automaticamente..."
        systemctl enable nginx
    fi
fi

# Redis (se estiver instalado)
if systemctl list-unit-files | grep -q redis; then
    echo "🔴 Redis:"
    echo "   Status: $(systemctl is-active redis)"
    echo "   Habilitado: $(systemctl is-enabled redis)"
    
    if systemctl is-enabled redis >/dev/null 2>&1; then
        echo "✅ Redis já está habilitado para iniciar automaticamente"
    else
        echo "🔧 Habilitando Redis para iniciar automaticamente..."
        systemctl enable redis
    fi
fi

# Cloudflare Tunnel
echo "☁️ Cloudflare Tunnel:"
echo "   Status: $(systemctl is-active cloudflared-sisvot)"
echo "   Habilitado: $(systemctl is-enabled cloudflared-sisvot)"

if systemctl is-enabled cloudflared-sisvot >/dev/null 2>&1; then
    echo "✅ Cloudflare Tunnel já está habilitado para iniciar automaticamente"
else
    echo "🔧 Habilitando Cloudflare Tunnel para iniciar automaticamente..."
    systemctl enable cloudflared-sisvot
fi

echo ""
echo "📋 VERIFICAÇÃO FINAL:"
echo "====================="

# Verificar se todos os serviços estão habilitados
all_enabled=true

if systemctl is-enabled postgresql@16-main >/dev/null 2>&1; then
    echo "✅ PostgreSQL 16: Habilitado para iniciar automaticamente"
else
    echo "❌ PostgreSQL 16: NÃO habilitado para iniciar automaticamente"
    all_enabled=false
fi

if systemctl is-enabled daphne >/dev/null 2>&1; then
    echo "✅ Daphne: Habilitado para iniciar automaticamente"
else
    echo "❌ Daphne: NÃO habilitado para iniciar automaticamente"
    all_enabled=false
fi

if systemctl list-unit-files | grep -q nginx; then
    if systemctl is-enabled nginx >/dev/null 2>&1; then
        echo "✅ Nginx: Habilitado para iniciar automaticamente"
    else
        echo "❌ Nginx: NÃO habilitado para iniciar automaticamente"
        all_enabled=false
    fi
fi

if systemctl list-unit-files | grep -q redis; then
    if systemctl is-enabled redis >/dev/null 2>&1; then
        echo "✅ Redis: Habilitado para iniciar automaticamente"
    else
        echo "❌ Redis: NÃO habilitado para iniciar automaticamente"
        all_enabled=false
    fi
fi

# Cloudflare Tunnel
if systemctl is-enabled cloudflared-sisvot >/dev/null 2>&1; then
    echo "✅ Cloudflare Tunnel: Habilitado para iniciar automaticamente"
else
    echo "❌ Cloudflare Tunnel: NÃO habilitado para iniciar automaticamente"
    all_enabled=false
fi

echo ""
if [ "$all_enabled" = true ]; then
    echo "🎉 TODOS OS SERVIÇOS ESTÃO CONFIGURADOS PARA INICIAR AUTOMATICAMENTE!"
    echo ""
    echo "🎯 PRÓXIMOS PASSOS:"
    echo "==================="
    echo "1. Reinicie a VM para testar:"
    echo "   sudo reboot"
    echo ""
    echo "2. Após reiniciar, verifique se o sistema está acessível:"
    echo "   - http://localhost:8000 (Daphne)"
    echo "   - http://localhost (Nginx, se instalado)"
    echo "   - Via Cloudflare Tunnel (URL configurada no Cloudflare)"
    echo ""
    echo "3. Para verificar os serviços após reiniciar:"
    echo "   sudo systemctl status postgresql@16-main"
    echo "   sudo systemctl status daphne"
    echo "   sudo systemctl status cloudflared-sisvot"
    echo "   sudo systemctl status nginx"
else
    echo "⚠️ Alguns serviços ainda não estão configurados corretamente."
    echo "Verifique os erros acima e execute o script novamente se necessário."
fi

echo ""
echo "✅ Configuração concluída!"
