from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from mensagens.services import MensagemService


class Command(BaseCommand):
    help = "Debug do sistema de envio de mensagens"

    def handle(self, *args, **options):
        # Buscar usuário
        try:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.first()
        except:
            user = None

        if not user:
            self.stdout.write(self.style.ERROR("❌ Nenhum usuário encontrado"))
            return

        self.stdout.write("🔍 Testando serviço de mensagens...")

        # Testar serviço
        service = MensagemService()

        # Verificar configurações
        self.stdout.write(f"   Account SID: {service.twilio_account_sid}")
        self.stdout.write(
            f"   Auth Token: {'*' * len(service.twilio_auth_token) if service.twilio_auth_token else 'None'}"
        )
        self.stdout.write(f"   WhatsApp Number: {service.twilio_whatsapp_number}")
        self.stdout.write(f"   SMS Number: {service.twilio_sms_number}")
        self.stdout.write(f"   Debug Mode: {service.debug_mode}")

        # Testar envio
        try:
            resultado = service.enviar_mensagem(
                destinatario_nome="Teste Debug",
                destinatario_telefone="5565999616000",
                destinatario_tipo="colaborador",
                destinatario_id=1,
                tipo_mensagem="whatsapp",
                conteudo="🎉 Teste de debug do sistema! 🎉",
                template_usado="debug",
                enviado_por=user,
            )

            self.stdout.write(f"✅ Resultado: {resultado}")
            self.stdout.write(f"   Success: {resultado.get('success')}")
            self.stdout.write(f"   Message ID: {resultado.get('message_id')}")
            self.stdout.write(f"   API Message ID: {resultado.get('api_message_id')}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro: {e!s}"))
            import traceback

            traceback.print_exc()
