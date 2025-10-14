# Guia de Configuração - Ambiente de Desenvolvimento

## Visão Geral
- **Desenvolvimento**: VM local (192.168.18.158) + PostgreSQL local
- **Produção**: AWS EC2 (sistema.fidelizamax.app.br) + RDS PostgreSQL

## 1. Configurações do Ambiente de Desenvolvimento

### 1.1 Arquivo de Ambiente (.env)
Crie um arquivo `.env` no seu ambiente de desenvolvimento com:

```bash
# ===========================================
# CONFIGURAÇÕES DE DESENVOLVIMENTO
# ===========================================
DB_ENGINE=django.db.backends.postgresql
DB_NAME=fidelizamax_dev
DB_USER=fidelizamax_dev
DB_PASSWORD=dev_password_123
DB_HOST=127.0.0.1
DB_PORT=5432

SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.18.158,0.0.0.0

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DOMAIN_NAME=192.168.18.158
CSRF_TRUSTED_ORIGINS=http://192.168.18.158,http://localhost,http://127.0.0.1

# Configurações de segurança para desenvolvimento
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0
```

### 1.2 Configuração do PostgreSQL
```bash
# No ambiente de desenvolvimento
sudo -u postgres psql
CREATE DATABASE fidelizamax_dev;
CREATE USER fidelizamax_dev WITH PASSWORD 'dev_password_123';
GRANT ALL PRIVILEGES ON DATABASE fidelizamax_dev TO fidelizamax_dev;
\q
```

## 2. Scripts de Deploy

### 2.1 Script de Deploy para Produção
Crie `deploy_production.sh`:

```bash
#!/bin/bash
# Script de deploy para produção

echo "🚀 Iniciando deploy para produção..."

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
```

## 3. Configurações do Git

### 3.1 .gitignore
Adicione ao `.gitignore`:

```gitignore
# Arquivos de ambiente
.env
.env.local
.env.development
.env.production

# Arquivos de backup
*.json
backup_*.json
dev_data.json

# Logs
logs/
*.log

# Arquivos temporários
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

## 4. Verificações de Segurança

### 4.1 Checklist de Desenvolvimento
- [ ] DEBUG=False em produção
- [ ] SECRET_KEY diferente entre ambientes
- [ ] ALLOWED_HOSTS configurado corretamente
- [ ] CSRF_TRUSTED_ORIGINS configurado
- [ ] Banco de dados isolado por ambiente
- [ ] Logs configurados adequadamente

### 4.2 Checklist de Deploy
- [ ] Backup do banco antes do deploy
- [ ] Testes passando localmente
- [ ] Migrações testadas
- [ ] Arquivos estáticos coletados
- [ ] Serviços reiniciados
- [ ] Aplicação funcionando

## 5. Comandos Úteis

### 5.1 Desenvolvimento
```bash
# Executar servidor de desenvolvimento
python manage.py runserver 0.0.0.0:8000

# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Executar testes
python manage.py test
```

### 5.2 Produção
```bash
# Verificar status dos serviços
sudo systemctl status daphne
sudo systemctl status nginx

# Ver logs
sudo journalctl -u daphne -f
sudo tail -f /var/log/nginx/error.log

# Backup do banco
python manage.py dumpdata > backup_$(date +%Y%m%d).json
```

## Como usar o development.env localmente

1. Copie o arquivo de exemplo para `.env` na sua VM de desenvolvimento:

   ```bash
   cd /srv/fidelizamax/app
   cp development.env .env
   ```

2. Edite `.env` e ajuste `DB_NAME`, `DB_USER`, `DB_PASSWORD` conforme seu PostgreSQL local.

3. Crie e ative o ambiente virtual, instale dependências e rode migrações:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   ```

4. Suba o servidor de desenvolvimento acessível pela rede local:

   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

5. Acesse via navegador em `http://192.168.18.158:8000` (ajuste o IP se necessário).

Observações:
- O `settings.py` lê variáveis do `.env` via `python-decouple`.
- Em produção (AWS), use um `.env` com as credenciais do RDS e domínios `https://sistema.fidelizamax.app.br`.
