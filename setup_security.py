#!/usr/bin/env python3
"""
Script de configuração de segurança para o Sistema de Fidelização
Execute este script para aplicar as configurações de segurança
"""

import os
import subprocess
import sys
from pathlib import Path


def print_header():
    print("=" * 60)
    print("🔒 CONFIGURAÇÃO DE SEGURANÇA - SISTEMA FIDELIZAÇÃO")
    print("=" * 60)


def check_django_project():
    """Verifica se estamos em um projeto Django válido"""
    if not os.path.exists("manage.py"):
        print("❌ Erro: Este não é um projeto Django válido!")
        print("   Execute este script na raiz do projeto Django.")
        sys.exit(1)
    print("✅ Projeto Django detectado")


def create_directories():
    """Cria diretórios necessários para segurança"""
    directories = [
        "logs",
        "backups",
        "backups/database",
        "backups/media",
        "security",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Diretório criado: {directory}")


def create_gitignore():
    """Cria/atualiza .gitignore com entradas de segurança"""
    gitignore_entries = [
        "",
        "# Arquivos de segurança",
        ".env",
        "*.env",
        "logs/",
        "backups/",
        "security/",
        "*.log",
        "*.sql",
        "*.dump",
        "",
        "# Arquivos sensíveis",
        "local_settings.py",
        "secret_key.txt",
        "database_credentials.txt",
        "",
        "# Cache e temporários",
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".Python",
        "env/",
        "venv/",
        ".venv/",
        "",
        "# IDEs",
        ".vscode/",
        ".idea/",
        "*.swp",
        "*.swo",
        "",
        "# Sistema",
        ".DS_Store",
        "Thumbs.db",
    ]

    gitignore_path = Path(".gitignore")

    if gitignore_path.exists():
        with open(gitignore_path) as f:
            existing_content = f.read()
    else:
        existing_content = ""

    new_entries = []
    for entry in gitignore_entries:
        if entry not in existing_content:
            new_entries.append(entry)

    if new_entries:
        with open(gitignore_path, "a") as f:
            f.write("\n".join(new_entries))
        print("✅ .gitignore atualizado com entradas de segurança")
    else:
        print("✅ .gitignore já está atualizado")


def create_env_template():
    """Cria template de arquivo .env"""
    env_template = """# ===========================================
# CONFIGURAÇÕES DE SEGURANÇA - SISTEMA FIDELIZAÇÃO
# ===========================================
# NUNCA commite este arquivo no Git!
# Copie este arquivo para .env e configure suas credenciais

# ===========================================
# DJANGO CORE
# ===========================================
SECRET_KEY=SUA_SECRET_KEY_AQUI
DEBUG=False
ALLOWED_HOSTS=fidelizamax.app.br,www.fidelizamax.app.br,localhost,127.0.0.1

# ===========================================
# BANCO DE DADOS
# ===========================================
DB_NAME=sisvot_db
DB_USER=sisuserdb
DB_PASSWORD=SUA_SENHA_DB_AQUI
DB_HOST=127.0.0.1
DB_PORT=5432

# ===========================================
# EMAIL CONFIGURATION
# ===========================================
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=SUA_SENHA_EMAIL_AQUI
DEFAULT_FROM_EMAIL=suporte@fidelizamax.app.br
SERVER_EMAIL=suporte@fidelizamax.app.br

# ===========================================
# SEGURANÇA HTTPS
# ===========================================
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY

# ===========================================
# SESSÕES E COOKIES
# ===========================================
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_AGE=3600
SESSION_EXPIRE_AT_BROWSER_CLOSE=True
CSRF_COOKIE_SECURE=True
CSRF_COOKIE_HTTPONLY=True
"""

    with open(".env.template", "w") as f:
        f.write(env_template)
    print("✅ Template .env.template criado")


def install_security_packages():
    """Instala pacotes de segurança"""
    print("📦 Instalando pacotes de segurança...")

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements-security.txt"],
            check=True,
        )
        print("✅ Pacotes de segurança instalados")
    except subprocess.CalledProcessError:
        print("⚠️  Erro ao instalar pacotes. Execute manualmente:")
        print("   pip install -r requirements-security.txt")


def create_security_middleware():
    """Cria middleware de segurança personalizado"""
    middleware_code = '''"""
Middleware de segurança personalizado
"""

import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger('django.security')

class SecurityMiddleware(MiddlewareMixin):
    """Middleware para monitoramento de segurança"""
    
    def process_request(self, request):
        """Processa requisições para monitoramento de segurança"""
        # Log de tentativas de acesso suspeitas
        if self.is_suspicious_request(request):
            logger.warning(
                f"Tentativa suspeita detectada: {request.META.get('REMOTE_ADDR')} - "
                f"{request.method} {request.path}"
            )
        
        # Rate limiting básico
        if self.is_rate_limited(request):
            logger.warning(
                f"Rate limit excedido: {request.META.get('REMOTE_ADDR')}"
            )
            return HttpResponseForbidden("Rate limit excedido")
        
        return None
    
    def is_suspicious_request(self, request):
        """Detecta requisições suspeitas"""
        suspicious_patterns = [
            'admin',
            'wp-admin',
            'phpmyadmin',
            'config',
            'backup',
            'test',
            'debug',
        ]
        
        path = request.path.lower()
        return any(pattern in path for pattern in suspicious_patterns)
    
    def is_rate_limited(self, request):
        """Verifica se o IP excedeu o rate limit"""
        ip = request.META.get('REMOTE_ADDR')
        if not ip:
            return False
        
        cache_key = f"rate_limit_{ip}"
        requests = cache.get(cache_key, 0)
        
        if requests >= 100:  # 100 requests por hora
            return True
        
        cache.set(cache_key, requests + 1, 3600)  # 1 hora
        return False
'''

    security_dir = Path("security")
    security_dir.mkdir(exist_ok=True)

    with open(security_dir / "middleware.py", "w") as f:
        f.write(middleware_code)

    print("✅ Middleware de segurança criado")


def create_backup_script():
    """Cria script de backup automático"""
    backup_script = """#!/bin/bash
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
"""

    with open("backup.sh", "w") as f:
        f.write(backup_script)

    # Tornar o script executável
    os.chmod("backup.sh", 0o755)
    print("✅ Script de backup criado")


def create_monitoring_script():
    """Cria script de monitoramento de segurança"""
    monitoring_script = """#!/bin/bash
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
"""

    with open("monitor_security.sh", "w") as f:
        f.write(monitoring_script)

    os.chmod("monitor_security.sh", 0o755)
    print("✅ Script de monitoramento criado")


def main():
    """Função principal"""
    print_header()

    print("🔍 Verificando projeto Django...")
    check_django_project()

    print("\\n📁 Criando diretórios de segurança...")
    create_directories()

    print("\\n📝 Configurando .gitignore...")
    create_gitignore()

    print("\\n🔐 Criando template de variáveis de ambiente...")
    create_env_template()

    print("\\n🛡️ Criando middleware de segurança...")
    create_security_middleware()

    print("\\n💾 Criando script de backup...")
    create_backup_script()

    print("\\n📊 Criando script de monitoramento...")
    create_monitoring_script()

    print("\\n📦 Instalando pacotes de segurança...")
    install_security_packages()

    print("\\n" + "=" * 60)
    print("✅ CONFIGURAÇÃO DE SEGURANÇA CONCLUÍDA!")
    print("=" * 60)
    print("\\n📋 PRÓXIMOS PASSOS:")
    print("1. Copie .env.template para .env e configure suas credenciais")
    print("2. Atualize seu settings.py com as configurações de security_config.py")
    print("3. Configure o cron para executar backup.sh diariamente")
    print("4. Configure o cron para executar monitor_security.sh a cada 5 minutos")
    print("5. Reinicie o servidor Django")
    print("\\n⚠️  IMPORTANTE:")
    print("- Nunca commite o arquivo .env no Git")
    print("- Mantenha as dependências atualizadas")
    print("- Monitore os logs regularmente")
    print("- Faça backups regulares")


if __name__ == "__main__":
    main()
