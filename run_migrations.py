#!/usr/bin/env python
import os
import sys
import django

# Adicionar o diretório do projeto ao path
sys.path.append('/srv/sisvot')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_fidelizacao.settings')
django.setup()

# Executar migrações
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    execute_from_command_line(['manage.py', 'migrate', 'user_profiles'])


