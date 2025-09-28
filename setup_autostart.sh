#!/bin/bash

echo "🚀 Configurando sistema para iniciar automaticamente..."

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script precisa ser executado como root ou com sudo"
    echo "Execute: sudo ./setup_autostart.sh"
    exit 1
fi

echo "📊 Verificando status dos serviços..."

# Verificar PostgreSQL
echo "🐘 PostgreSQL:"
systemctl status postgresql@15-main --no-pager -l

# Habilitar PostgreSQL para iniciar automaticamente
echo "🔧 Habilitando PostgreSQL para iniciar automaticamente..."
systemctl enable postgresql@15-main
systemctl start postgresql@15-main

# Verificar Daphne
echo "🌐 Daphne:"
systemctl status daphne --no-pager -l

# Verificar se Daphne está habilitado
if systemctl is-enabled daphne >/dev/null 2>&1; then
    echo "✅ Daphne já está habilitado para iniciar automaticamente"
else
    echo "🔧 Habilitando Daphne para iniciar automaticamente..."
    systemctl enable daphne
fi

# Verificar Nginx (se estiver instalado)
if systemctl list-unit-files | grep -q nginx; then
    echo "🌍 Nginx:"
    systemctl status nginx --no-pager -l
    if systemctl is-enabled nginx >/dev/null 2>&1; then
        echo "✅ Nginx já está habilitado para iniciar automaticamente"
    else
        echo "🔧 Habilitando Nginx para iniciar automaticamente..."
        systemctl enable nginx
    fi
fi

# Verificar Redis (se estiver instalado)
if systemctl list-unit-files | grep -q redis; then
    echo "🔴 Redis:"
    systemctl status redis --no-pager -l
    if systemctl is-enabled redis >/dev/null 2>&1; then
        echo "✅ Redis já está habilitado para iniciar automaticamente"
    else
        echo "🔧 Habilitando Redis para iniciar automaticamente..."
        systemctl enable redis
    fi
fi

echo ""
echo "📋 RESUMO DOS SERVIÇOS:"
echo "======================="

# PostgreSQL
if systemctl is-enabled postgresql@15-main >/dev/null 2>&1; then
    echo "✅ PostgreSQL: Habilitado para iniciar automaticamente"
else
    echo "❌ PostgreSQL: NÃO habilitado para iniciar automaticamente"
fi

# Daphne
if systemctl is-enabled daphne >/dev/null 2>&1; then
    echo "✅ Daphne: Habilitado para iniciar automaticamente"
else
    echo "❌ Daphne: NÃO habilitado para iniciar automaticamente"
fi

# Nginx
if systemctl list-unit-files | grep -q nginx && systemctl is-enabled nginx >/dev/null 2>&1; then
    echo "✅ Nginx: Habilitado para iniciar automaticamente"
elif systemctl list-unit-files | grep -q nginx; then
    echo "❌ Nginx: NÃO habilitado para iniciar automaticamente"
fi

# Redis
if systemctl list-unit-files | grep -q redis && systemctl is-enabled redis >/dev/null 2>&1; then
    echo "✅ Redis: Habilitado para iniciar automaticamente"
elif systemctl list-unit-files | grep -q redis; then
    echo "❌ Redis: NÃO habilitado para iniciar automaticamente"
fi

echo ""
echo "🎯 PRÓXIMOS PASSOS:"
echo "==================="
echo "1. Reinicie a VM para testar se os serviços sobem automaticamente"
echo "2. Após reiniciar, verifique se o sistema está acessível em:"
echo "   - http://localhost:8000 (Daphne)"
echo "   - http://localhost (Nginx, se instalado)"
echo ""
echo "3. Para verificar manualmente os serviços:"
echo "   sudo systemctl status postgresql@15-main"
echo "   sudo systemctl status daphne"
echo "   sudo systemctl status nginx"
echo ""
echo "✅ Configuração concluída!"



