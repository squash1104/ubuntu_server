#!/bin/bash
# Script de monitoramento de segurança

LOG_FILE="/srv/sisvot/logs/security_monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Verificar logs de erro
ERROR_COUNT=$(grep -c "ERROR" /srv/sisvot/logs/security.log 2>/dev/null || echo "0")
WARNING_COUNT=$(grep -c "WARNING" /srv/sisvot/logs/security.log 2>/dev/null || echo "0")

# Verificar espaço em disco
DISK_USAGE=$(df /srv/sisvot | tail -1 | awk '{print $5}' | sed 's/%//')

# Verificar status do serviço
SERVICE_STATUS=$(systemctl is-active daphne 2>/dev/null || echo "unknown")

# Log do monitoramento
echo "[$DATE] Errors: $ERROR_COUNT, Warnings: $WARNING_COUNT, Disk: ${DISK_USAGE}%, Service: $SERVICE_STATUS" >> $LOG_FILE

# Alertas
if [ $ERROR_COUNT -gt 10 ]; then
    echo "ALERTA: Muitos erros detectados ($ERROR_COUNT)" >> $LOG_FILE
fi

if [ $DISK_USAGE -gt 80 ]; then
    echo "ALERTA: Espaço em disco baixo (${DISK_USAGE}%)" >> $LOG_FILE
fi

if [ "$SERVICE_STATUS" != "active" ]; then
    echo "ALERTA: Serviço não está ativo ($SERVICE_STATUS)" >> $LOG_FILE
fi
