#!/bin/bash
# Script de backup automático para o Sistema de Fidelização

BACKUP_DIR="/srv/sisvot/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="sisvot_db"
DB_USER="sisuserdb"

# Criar diretório de backup se não existir
mkdir -p $BACKUP_DIR/database
mkdir -p $BACKUP_DIR/media

# Backup do banco de dados
echo "Iniciando backup do banco de dados..."
pg_dump -h localhost -U $DB_USER -d $DB_NAME > $BACKUP_DIR/database/backup_$DATE.sql

# Backup dos arquivos de mídia
echo "Iniciando backup dos arquivos de mídia..."
tar -czf $BACKUP_DIR/media/media_$DATE.tar.gz /srv/sisvot/media/

# Remover backups antigos (manter apenas 30 dias)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup concluído: $DATE"
