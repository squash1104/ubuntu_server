# 🔒 Guia de Segurança - Sistema de Fidelização

## ⚠️ PROBLEMAS CRÍTICOS IDENTIFICADOS

### 1. **SECRET_KEY Exposta**
- **Problema**: SECRET_KEY hardcoded no settings.py
- **Risco**: Alto - permite falsificação de tokens e sessões
- **Solução**: Mover para variáveis de ambiente

### 2. **DEBUG = True em Produção**
- **Problema**: Debug ativado expõe informações sensíveis
- **Risco**: Alto - vazamento de dados e código
- **Solução**: Desabilitar em produção

### 3. **Credenciais Hardcoded**
- **Problema**: Senhas do banco e email no código
- **Risco**: Alto - acesso não autorizado
- **Solução**: Usar variáveis de ambiente

### 4. **Falta de HTTPS Forçado**
- **Problema**: Tráfego pode ser interceptado
- **Risco**: Médio - interceptação de dados
- **Solução**: Configurar redirecionamento HTTPS

## 🛡️ MELHORIAS IMPLEMENTADAS

### ✅ **1. Estrutura de Segurança Criada**
```
/srv/sisvot/
├── security_config.py          # Configurações de segurança
├── setup_security.py           # Script de configuração
├── requirements-security.txt   # Dependências de segurança
├── .env.template              # Template de variáveis
├── security/                  # Middleware personalizado
├── logs/                      # Logs de segurança
├── backups/                   # Backups automáticos
├── backup.sh                  # Script de backup
└── monitor_security.sh        # Script de monitoramento
```

### ✅ **2. Pacotes de Segurança Instalados**
- `django-ratelimit` - Rate limiting
- `django-otp` - Autenticação de dois fatores
- `django-csp` - Content Security Policy
- `django-redis` - Cache seguro
- `django-extensions` - Ferramentas de desenvolvimento
- `cryptography` - Criptografia avançada

### ✅ **3. Middleware de Segurança**
- Detecção de requisições suspeitas
- Rate limiting por IP
- Logs de segurança automáticos
- Monitoramento de tentativas de acesso

### ✅ **4. Scripts de Backup e Monitoramento**
- Backup automático do banco de dados
- Backup dos arquivos de mídia
- Monitoramento de logs de erro
- Alertas de segurança

## 🚀 PRÓXIMOS PASSOS OBRIGATÓRIOS

### **1. Configurar Variáveis de Ambiente**
```bash
# Copiar template
cp .env.template .env

# Editar com suas credenciais
nano .env
```

### **2. Atualizar settings.py**
Adicione ao seu `settings.py`:
```python
import os
from security_config import apply_security_settings

# Aplicar configurações de segurança
apply_security_settings(locals())

# Configurações específicas de produção
if not DEBUG:
    # Configurações HTTPS
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Headers de segurança
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Cookies seguros
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
```

### **3. Configurar Cron Jobs**
```bash
# Editar crontab
crontab -e

# Adicionar linhas:
# Backup diário às 2h
0 2 * * * /srv/sisvot/backup.sh

# Monitoramento a cada 5 minutos
*/5 * * * * /srv/sisvot/monitor_security.sh
```

### **4. Configurar Firewall**
```bash
# Instalar UFW
sudo apt install ufw

# Configurar regras básicas
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### **5. Configurar SSL/TLS**
```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d fidelizamax.app.br
```

## 🔐 CONFIGURAÇÕES DE SEGURANÇA AVANÇADAS

### **1. Autenticação de Dois Fatores (2FA)**
```python
# Adicionar ao settings.py
INSTALLED_APPS = [
    # ... outras apps
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
]

MIDDLEWARE = [
    # ... outros middlewares
    'django_otp.middleware.OTPMiddleware',
]
```

### **2. Rate Limiting**
```python
# Adicionar ao settings.py
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Em views.py
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    # Sua view de login
    pass
```

### **3. Content Security Policy**
```python
# Adicionar ao settings.py
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:")
```

## 📊 MONITORAMENTO DE SEGURANÇA

### **1. Logs de Segurança**
- **Localização**: `/srv/sisvot/logs/security.log`
- **Monitoramento**: Tentativas de login, acessos suspeitos
- **Alertas**: Múltiplas tentativas de login falhadas

### **2. Métricas Importantes**
- Tentativas de login falhadas
- Acessos a URLs suspeitas
- Uso de recursos do servidor
- Espaço em disco disponível

### **3. Alertas Automáticos**
- Mais de 10 erros por hora
- Espaço em disco abaixo de 20%
- Serviço Django inativo
- Múltiplas tentativas de login

## 🔄 MANUTENÇÃO DE SEGURANÇA

### **1. Atualizações Regulares**
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade

# Atualizar dependências Python
pip install --upgrade -r requirements.txt
pip install --upgrade -r requirements-security.txt
```

### **2. Backup e Recuperação**
```bash
# Backup manual
./backup.sh

# Restaurar banco
psql -h localhost -U sisuserdb -d sisvot_db < backups/database/backup_YYYYMMDD_HHMMSS.sql

# Restaurar mídia
tar -xzf backups/media/media_YYYYMMDD_HHMMSS.tar.gz -C /
```

### **3. Testes de Segurança**
```bash
# Verificar configurações
python manage.py check --deploy

# Testar HTTPS
curl -I https://fidelizamax.app.br

# Verificar headers de segurança
curl -I https://fidelizamax.app.br | grep -i security
```

## ⚡ IMPLEMENTAÇÃO RÁPIDA

### **Para implementar AGORA:**

1. **Copie o arquivo .env:**
   ```bash
   cp .env.template .env
   ```

2. **Edite as credenciais no .env:**
   ```bash
   nano .env
   ```

3. **Atualize o settings.py:**
   ```python
   # Adicione no início do arquivo
   import os
   from security_config import apply_security_settings
   
   # Aplique as configurações
   apply_security_settings(locals())
   ```

4. **Reinicie o servidor:**
   ```bash
   sudo systemctl restart daphne
   ```

5. **Configure os cron jobs:**
   ```bash
   crontab -e
   # Adicione as linhas do backup e monitoramento
   ```

## 🎯 PRIORIDADES DE SEGURANÇA

### **CRÍTICO (Implementar HOJE):**
1. ✅ Mover credenciais para .env
2. ✅ Desabilitar DEBUG em produção
3. ✅ Configurar HTTPS obrigatório
4. ✅ Implementar rate limiting

### **ALTO (Implementar esta semana):**
1. 🔄 Configurar 2FA
2. 🔄 Implementar logs de segurança
3. 🔄 Configurar backup automático
4. 🔄 Configurar firewall

### **MÉDIO (Implementar este mês):**
1. ⏳ Implementar monitoramento avançado
2. ⏳ Configurar alertas por email
3. ⏳ Implementar testes de segurança
4. ⏳ Configurar WAF (Web Application Firewall)

## 📞 SUPORTE

Para dúvidas sobre implementação:
1. Consulte os logs em `/srv/sisvot/logs/`
2. Execute `python manage.py check --deploy`
3. Verifique o status dos serviços: `systemctl status daphne`

---

**⚠️ IMPORTANTE**: Este guia contém configurações sensíveis. Mantenha-o seguro e não compartilhe credenciais.


