#!/bin/bash
# Script de deploy para produção

echo "🚀 Iniciando deploy para produção..."
cd /srv/sisvot
source .venv/bin/activate

# 1. Backup do banco de dados atual
echo "📦 Fazendo backup do banco de dados..."
python manage.py dumpdata --indent=2 > backup_$(date +%Y%m%d_%H%M%S).json

# 2. Pull do código do GitHub
echo "📥 Baixando código do GitHub..."
git pull origin main

# 3. Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# 4. Executar migrações
echo "🔄 Executando migrações..."
python manage.py migrate

# 5. Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# 6. Reiniciar serviços
echo "🔄 Reiniciando serviços..."
sudo systemctl restart daphne
sudo systemctl restart nginx

echo "✅ Deploy concluído com sucesso!"
