from django.core.management.base import BaseCommand
from mensagens.whatsapp_cloud_api import WhatsAppCloudAPI


class Command(BaseCommand):
    help = 'Testa envio de WhatsApp via Cloud API do Meta'

    def add_arguments(self, parser):
        parser.add_argument('--telefone', type=str, default='5565999616000', help='Número de telefone')
        parser.add_argument('--mensagem', type=str, default='🎉 Teste do WhatsApp Cloud API! 🎉', help='Mensagem para enviar')
        parser.add_argument('--verificar', action='store_true', help='Apenas verificar configuração')

    def handle(self, *args, **options):
        telefone = options.get('telefone')
        mensagem = options.get('mensagem')
        verificar = options.get('verificar')
        
        self.stdout.write("📱 Testando WhatsApp Cloud API...")
        
        whatsapp = WhatsAppCloudAPI()
        
        # Verificar configuração
        config_ok, config_msg = whatsapp.verificar_configuracao()
        
        if not config_ok:
            self.stdout.write(self.style.ERROR(f"❌ {config_msg}"))
            self.stdout.write("\n🔧 CONFIGURAÇÃO NECESSÁRIA:")
            self.stdout.write("1. Acesse: https://developers.facebook.com/")
            self.stdout.write("2. Crie uma aplicação Business")
            self.stdout.write("3. Configure WhatsApp Cloud API")
            self.stdout.write("4. Obtenha Phone Number ID e Access Token")
            self.stdout.write("5. Configure no settings.py:")
            self.stdout.write("   WHATSAPP_PHONE_NUMBER_ID = 'seu_phone_number_id'")
            self.stdout.write("   WHATSAPP_ACCESS_TOKEN = 'seu_access_token'")
            return
        
        self.stdout.write(self.style.SUCCESS(f"✅ {config_msg}"))
        
        if verificar:
            return
        
        # Enviar mensagem de teste
        self.stdout.write(f"\n📤 Enviando mensagem...")
        self.stdout.write(f"   Para: {telefone}")
        self.stdout.write(f"   Mensagem: {mensagem}")
        
        resultado = whatsapp.enviar_mensagem(telefone, mensagem)
        
        if resultado['success']:
            self.stdout.write(self.style.SUCCESS("✅ Mensagem enviada com sucesso!"))
            self.stdout.write(f"   Message ID: {resultado.get('message_id')}")
        else:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao enviar: {resultado.get('error')}"))
            if 'api_response' in resultado:
                self.stdout.write(f"   Resposta da API: {resultado['api_response']}")
        
        self.stdout.write("\n💡 INFORMAÇÕES:")
        self.stdout.write("   ✅ 1000 mensagens/mês gratuitas")
        self.stdout.write("   ✅ API oficial do Meta")
        self.stdout.write("   ✅ Sem necessidade de navegador")
        self.stdout.write("   ⚠️ Token temporário expira em 24h")
