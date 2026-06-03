#!/bin/bash

# Script para iniciar o Daphne
cd /srv/sisvot

# Ativar ambiente virtual
source .venv/bin/activate

# Configurar variáveis de ambiente
export DJANGO_SETTINGS_MODULE=sistema_fidelizacao.settings

# Verificar se o Django está funcionando
echo "Verificando Django..."
python manage.py check --deploy || exit 1

# Iniciar Daphne
echo "Iniciando Daphne..."
exec daphne -b 127.0.0.1 -p 8000 sistema_fidelizacao.asgi:application
