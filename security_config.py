# ===========================================
# CONFIGURAÇÕES DE SEGURANÇA - SISTEMA FIDELIZAÇÃO
# ===========================================
# Este arquivo contém as configurações de segurança recomendadas
# Copie as configurações necessárias para seu settings.py


# ===========================================
# CONFIGURAÇÕES DE PRODUÇÃO
# ===========================================

# 1. CONFIGURAÇÕES BÁSICAS DE SEGURANÇA
SECURITY_SETTINGS = {
    # Desabilitar DEBUG em produção
    "DEBUG": False,
    # Configurar hosts permitidos
    "ALLOWED_HOSTS": [
        "sistema.fidelizamax.app.br",
        "www.sistema.fidelizamax.app.br",
        "localhost",
        "127.0.0.1",
    ],
    # Configurar CSRF
    "CSRF_TRUSTED_ORIGINS": [
        "https://sistema.fidelizamax.app.br",
        "https://www.sistema.fidelizamax.app.br",
    ],
}

# 2. CONFIGURAÇÕES HTTPS
HTTPS_SETTINGS = {
    "SECURE_SSL_REDIRECT": True,
    "SECURE_HSTS_SECONDS": 31536000,  # 1 ano
    "SECURE_HSTS_INCLUDE_SUBDOMAINS": True,
    "SECURE_HSTS_PRELOAD": True,
    "SECURE_CONTENT_TYPE_NOSNIFF": True,
    "SECURE_BROWSER_XSS_FILTER": True,
    "X_FRAME_OPTIONS": "DENY",
    "SECURE_PROXY_SSL_HEADER": ("HTTP_X_FORWARDED_PROTO", "https"),
}

# 3. CONFIGURAÇÕES DE SESSÃO E COOKIES
SESSION_SETTINGS = {
    "SESSION_COOKIE_SECURE": True,
    "SESSION_COOKIE_HTTPONLY": True,
    "SESSION_COOKIE_AGE": 3600,  # 1 hora
    "SESSION_EXPIRE_AT_BROWSER_CLOSE": True,
    "CSRF_COOKIE_SECURE": True,
    "CSRF_COOKIE_HTTPONLY": True,
    "CSRF_COOKIE_SAMESITE": "Strict",
}

# 4. CONFIGURAÇÕES DE SENHA
PASSWORD_SETTINGS = {
    "AUTH_PASSWORD_VALIDATORS": [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
            "OPTIONS": {
                "min_length": 12,  # Aumentar para 12 caracteres
            },
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ],
    # Configurações de login
    "LOGIN_ATTEMPTS_LIMIT": 5,
    "LOGIN_ATTEMPTS_TIMEOUT": 300,  # 5 minutos
}

# 5. CONFIGURAÇÕES DE LOG
LOGGING_SETTINGS = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "/srv/sisvot/logs/security.log",
            "formatter": "verbose",
        },
        "security_file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": "/srv/sisvot/logs/security_events.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "django.security": {
            "handlers": ["security_file"],
            "level": "WARNING",
            "propagate": True,
        },
        "chat": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

# 6. MIDDLEWARE DE SEGURANÇA
SECURITY_MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Adicionar middleware de rate limiting
    "django_ratelimit.middleware.RatelimitMiddleware",
]

# 7. CONFIGURAÇÕES DE CACHE PARA SEGURANÇA
CACHE_SETTINGS = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "sisvot",
        "TIMEOUT": 300,
    }
}

# 8. CONFIGURAÇÕES DE EMAIL SEGURO
EMAIL_SECURITY_SETTINGS = {
    "EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
    "EMAIL_HOST": "smtp.gmail.com",
    "EMAIL_PORT": 587,
    "EMAIL_USE_TLS": True,
    "EMAIL_TIMEOUT": 30,
    "EMAIL_USE_LOCALTIME": False,
}

# 9. CONFIGURAÇÕES DE BACKUP
BACKUP_SETTINGS = {
    "BACKUP_ENABLED": True,
    "BACKUP_SCHEDULE": "0 2 * * *",  # Diário às 2h
    "BACKUP_RETENTION_DAYS": 30,
    "BACKUP_LOCATION": "/srv/backups/sisvot/",
    "BACKUP_DATABASE": True,
    "BACKUP_MEDIA": True,
    "BACKUP_STATIC": False,
}

# 10. CONFIGURAÇÕES DE MONITORAMENTO
MONITORING_SETTINGS = {
    "ENABLE_SECURITY_LOGS": True,
    "LOG_FAILED_LOGINS": True,
    "LOG_ADMIN_ACTIONS": True,
    "LOG_FILE_UPLOADS": True,
    "LOG_DATABASE_CHANGES": True,
    "ALERT_ON_MULTIPLE_FAILED_LOGINS": True,
    "ALERT_ON_ADMIN_ACCESS": True,
}


# ===========================================
# FUNÇÃO PARA APLICAR CONFIGURAÇÕES
# ===========================================
def apply_security_settings(settings_dict):
    """
    Aplica as configurações de segurança ao settings.py
    """
    # Aplicar configurações básicas
    settings_dict.update(SECURITY_SETTINGS)

    # Aplicar configurações HTTPS
    settings_dict.update(HTTPS_SETTINGS)

    # Aplicar configurações de sessão
    settings_dict.update(SESSION_SETTINGS)

    # Aplicar configurações de senha
    settings_dict.update(PASSWORD_SETTINGS)

    # Aplicar configurações de email
    settings_dict.update(EMAIL_SECURITY_SETTINGS)

    # Aplicar configurações de cache
    settings_dict.update(CACHE_SETTINGS)

    # Aplicar configurações de monitoramento
    settings_dict.update(MONITORING_SETTINGS)

    return settings_dict


# ===========================================
# CHECKLIST DE SEGURANÇA
# ===========================================
SECURITY_CHECKLIST = [
    "✅ Configurar DEBUG=False em produção",
    "✅ Usar variáveis de ambiente para dados sensíveis",
    "✅ Configurar HTTPS obrigatório",
    "✅ Configurar headers de segurança",
    "✅ Configurar cookies seguros",
    "✅ Implementar rate limiting",
    "✅ Configurar logs de segurança",
    "✅ Implementar backup automático",
    "✅ Configurar autenticação de dois fatores",
    "✅ Implementar monitoramento de segurança",
    "✅ Configurar firewall",
    "✅ Atualizar dependências regularmente",
    "✅ Implementar testes de segurança",
    "✅ Configurar alertas de segurança",
]
