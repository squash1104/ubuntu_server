#!/bin/bash
# Script para rodar migrações no banco sisvot_db

echo "Rodando migrações no banco sisvot_db..."

# Exportar variáveis para usar o banco sisvot_db
export DB_NAME=sisvot_db

# Entrar no diretório do projeto
cd /srv/sisvot

# Ativar virtualenv
source .venv/bin/activate

# Mostrar migrações pendentes
echo "Migrações pendentes:"
python manage.py showmigrations --database=sisvot_db 2>/dev/null || python manage.py showmigrations

# Rodar migrações
echo ""
echo "Rodando migrações..."
python manage.py migrate --database=sisvot_db 2>/dev/null || python manage.py migrate

echo ""
echo "Migrações concluídas!"
