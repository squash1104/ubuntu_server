# Configurações do Twilio para o Sistema de Mensagens
#
# INSTRUÇÕES PARA CONFIGURAR:
# 1. Acesse https://console.twilio.com/
# 2. Crie uma conta gratuita se não tiver
# 3. Copie o Account SID e Auth Token
# 4. Para WhatsApp, use o número sandbox: +14155238886
# 5. Para SMS, compre um número de telefone no Twilio
# 6. Substitua os valores abaixo pelas suas credenciais

# Credenciais do Twilio
TWILIO_ACCOUNT_SID = "AC7d5465be0e9daf62173f0f7371d81058"
TWILIO_AUTH_TOKEN = "4bc1dc570f548f287fb30d4fbaac3e46"

# Números do Twilio
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Número sandbox do WhatsApp
TWILIO_SMS_NUMBER = "+17257653917"  # Seu número de SMS do Twilio

# Configurações de Rate Limiting
MAX_MESSAGES_PER_MINUTE = 10
MAX_MESSAGES_PER_HOUR = 100

# Configurações de Retry
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 30

# Para testar sem enviar mensagens reais (modo debug)
DEBUG_MODE = False  # Mude para False quando estiver pronto para enviar mensagens reais

# Configuração para usar apenas SMS (mais barato)
USAR_APENAS_SMS = True  # Desabilita WhatsApp e usa apenas SMS

# =============================================================================
# CONFIGURAÇÕES WHATSAPP CLOUD API (META) - GRATUITO
# =============================================================================
# Para configurar:
# 1. Acesse: https://developers.facebook.com/
# 2. Crie uma aplicação Business
# 3. Configure WhatsApp Cloud API
# 4. Obtenha Phone Number ID e Access Token
# 5. Substitua os valores abaixo

# Credenciais do WhatsApp Cloud API
WHATSAPP_PHONE_NUMBER_ID = "SEU_PHONE_NUMBER_ID_AQUI"
WHATSAPP_ACCESS_TOKEN = "SEU_ACCESS_TOKEN_AQUI"
WHATSAPP_BUSINESS_ACCOUNT_ID = "SEU_BUSINESS_ACCOUNT_ID_AQUI"

# Configuração para usar WhatsApp Cloud API
USAR_WHATSAPP_CLOUD_API = False  # Mude para True quando configurar
