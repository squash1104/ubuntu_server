# Configurações para APIs de Mensagens
# Adicione suas credenciais do Twilio aqui

# Twilio Configuration
TWILIO_ACCOUNT_SID = "your_account_sid_here"
TWILIO_AUTH_TOKEN = "your_auth_token_here"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Número sandbox do Twilio
TWILIO_SMS_NUMBER = "+1234567890"  # Seu número de SMS do Twilio

# Configurações de Rate Limiting
MAX_MESSAGES_PER_MINUTE = 10
MAX_MESSAGES_PER_HOUR = 100

# Configurações de Retry
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 30

# Configurações de Template
DEFAULT_SMS_TEMPLATE = """
Parabéns {nome}! 🎉

Hoje é seu aniversário e queremos te desejar muitas felicidades!

Atenciosamente,
Equipe Sistema Fidelização
"""

DEFAULT_WHATSAPP_TEMPLATE = """
🎉 *Parabéns {nome}!* 🎉

Hoje é um dia muito especial! Queremos te desejar um feliz aniversário e muitas felicidades!

Que este novo ano de vida seja repleto de alegrias, conquistas e momentos especiais! 🎂✨

Atenciosamente,
*Equipe Sistema Fidelização*
"""
