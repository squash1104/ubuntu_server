#!/bin/bash
# Script para fazer backup da aplicação e banco de dados

# ===========================================
# CONFIGURAÇÕES
# ===========================================
DATA=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/srv/sisvot/backups"
APP_DIR="/srv/sisvot"
DB_NAME="sisvot_db"
DB_USER="sisuserdb"

# Criar diretório de backup se não existir
mkdir -p "$BACKUP_DIR"

# ===========================================
# BACKUP DO BANCO DE DADOS
# ===========================================
echo "=" 50
echo "FAZENDO BACKUP DO BANCO DE DADOS"
echo "=" 50

DB_BACKUP_FILE="$BACKUP_DIR/db_${DB_NAME}_${DATA}.sql"
echo "Gerando backup do banco: $DB_NAME..."
sudo -u postgres sh -c "pg_dump -U postgres -d $DB_NAME" > "$DB_BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup do banco criado: $DB_BACKUP_FILE"
    DB_SIZE=$(du -h "$DB_BACKUP_FILE" | cut -f1)
    echo "📦 Tamanho: $DB_SIZE"
else
    echo "❌ Erro ao criar backup do banco!"
    exit 1
fi

# ===========================================
# BACKUP DOS ARQUIVOS DA APLICAÇÃO
# ===========================================
echo ""
echo "=" 50
echo "FAZENDO BACKUP DA APLICAÇÃO"
echo "=" 50

APP_BACKUP_FILE="$BACKUP_DIR/app_${DATA}.tar.gz"
echo "Compactando aplicação..."
tar -czf "$APP_BACKUP_FILE" \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='backups' \
    --exclude='logs' \
    --exclude='media' \
    -C "$APP_DIR" .

if [ $? -eq 0 ]; then
    echo "✅ Backup da aplicação criado: $APP_BACKUP_FILE"
    APP_SIZE=$(du -h "$APP_BACKUP_FILE" | cut -f1)
    echo "📦 Tamanho: $APP_SIZE"
else
    echo "❌ Erro ao criar backup da aplicação!"
    exit 1
fi

# ===========================================
# RESUMO
# ===========================================
echo ""
echo "=" 50
echo "BACKUP CONCLUÍDO!"
echo "=" 50
echo "Data: $DATA"
echo "Banco: $DB_BACKUP_FILE ($DB_SIZE)"
echo "Aplicação: $APP_BACKUP_FILE ($APP_SIZE)"
echo ""
echo "Para restaurar:"
echo " Banco: psql -U $DB_USER -d $DB_NAME < $DB_BACKUP_FILE"
echo "  Aplicação: tar -xzf $APP_BACKUP_FILE -C /srv/sisvot"
