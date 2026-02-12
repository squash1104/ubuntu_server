#!/bin/bash
# Script para corrigir e reiniciar o serviço Daphne

echo "🔧 Corrigindo configuração do Daphne..."

# Adicionar EnvironmentFile ao daphne.service
sudo sed -i '/^WorkingDirectory=\/srv\/sisvot$/a EnvironmentFile=/srv/sisvot/.env' /etc/systemd/system/daphne.service

echo "✅ Arquivo daphne.service atualizado"

# Recarregar systemd
sudo systemctl daemon-reload

echo "✅ Systemd recarregado"

# Resetar estado de falha e iniciar
sudo systemctl reset-failed daphne.service 2>/dev/null || true
sudo systemctl enable daphne
sudo systemctl start daphne

echo "✅ Serviço Daphne iniciado"

# Verificar status
sudo systemctl status daphne
