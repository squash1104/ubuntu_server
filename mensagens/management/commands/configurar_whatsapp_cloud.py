from django.core.management.base import BaseCommand
import os
import re


class Command(BaseCommand):
    help = 'Configura as credenciais do WhatsApp Cloud API'

    def add_arguments(self, parser):
        parser.add_argument('--phone-id', type=str, help='Phone Number ID do WhatsApp')
        parser.add_argument('--access-token', type=str, help='Access Token do WhatsApp')
        parser.add_argument('--business-id', type=str, help='Business Account ID (opcional)')

    def handle(self, *args, **options):
        phone_id = options.get('phone_id')
        access_token = options.get('access_token')
        business_id = options.get('business_id')
        
        if not phone_id or not access_token:
            self.stdout.write(self.style.ERROR("❌ Erro: Phone ID e Access Token são obrigatórios"))
            self.stdout.write("\n🔧 USO:")
            self.stdout.write("python manage.py configurar_whatsapp_cloud \\")
            self.stdout.write("  --phone-id=SEU_PHONE_NUMBER_ID \\")
            self.stdout.write("  --access-token=SEU_ACCESS_TOKEN \\")
            self.stdout.write("  --business-id=SEU_BUSINESS_ACCOUNT_ID")
            return
        
        # Atualizar twilio_config.py
        config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'twilio_config.py')
        
        if not os.path.exists(config_file):
            self.stdout.write(self.style.ERROR(f"❌ Arquivo {config_file} não encontrado"))
            return
        
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Atualizar Phone Number ID
        content = re.sub(
            r'WHATSAPP_PHONE_NUMBER_ID = "[^"]*"',
            f'WHATSAPP_PHONE_NUMBER_ID = "{phone_id}"',
            content
        )
        
        # Atualizar Access Token
        content = re.sub(
            r'WHATSAPP_ACCESS_TOKEN = "[^"]*"',
            f'WHATSAPP_ACCESS_TOKEN = "{access_token}"',
            content
        )
        
        # Atualizar Business Account ID se fornecido
        if business_id:
            content = re.sub(
                r'WHATSAPP_BUSINESS_ACCOUNT_ID = "[^"]*"',
                f'WHATSAPP_BUSINESS_ACCOUNT_ID = "{business_id}"',
                content
            )
        
        # Ativar WhatsApp Cloud API
        content = re.sub(
            r'USAR_WHATSAPP_CLOUD_API = (True|False)',
            'USAR_WHATSAPP_CLOUD_API = True',
            content
        )
        
        with open(config_file, 'w') as f:
            f.write(content)
        
        self.stdout.write(self.style.SUCCESS("✅ Configurações do WhatsApp Cloud API atualizadas!"))
        self.stdout.write(f"   Phone Number ID: {phone_id}")
        self.stdout.write(f"   Access Token: {access_token[:10]}...")
        if business_id:
            self.stdout.write(f"   Business Account ID: {business_id}")
        
        self.stdout.write("\n🧪 Testando configuração...")
        
        # Testar configuração
        from mensagens.whatsapp_cloud_api import WhatsAppCloudAPI
        whatsapp = WhatsAppCloudAPI()
        config_ok, config_msg = whatsapp.verificar_configuracao()
        
        if config_ok:
            self.stdout.write(self.style.SUCCESS(f"✅ {config_msg}"))
            self.stdout.write("\n📱 Para testar envio de mensagem:")
            self.stdout.write("python manage.py testar_whatsapp_cloud_api --telefone=5565999616000")
        else:
            self.stdout.write(self.style.ERROR(f"❌ {config_msg}"))
        
        self.stdout.write("\n⚠️ IMPORTANTE:")
        self.stdout.write("   - Token temporário expira em 24h")
        self.stdout.write("   - Para token permanente, configure webhook")
        self.stdout.write("   - Reinicie o servidor Django após configurar")
