import requests
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Testa envio de WhatsApp diretamente"

    def add_arguments(self, parser):
        parser.add_argument(
            "--telefone", type=str, default="5565999616000", help="Número de telefone"
        )
        parser.add_argument(
            "--mensagem",
            type=str,
            default="🎉 Teste do sistema de mensagens! WhatsApp funcionando! 🎉",
            help="Mensagem para enviar",
        )

    def handle(self, *args, **options):
        telefone = options.get("telefone")
        mensagem = options.get("mensagem")

        # Carregar configurações
        try:
            from twilio_config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
        except ImportError:
            self.stdout.write(
                self.style.ERROR("❌ Arquivo twilio_config.py não encontrado")
            )
            return

        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            self.stdout.write(
                self.style.ERROR("❌ Credenciais do Twilio não configuradas")
            )
            return

        self.stdout.write("📱 Testando envio de WhatsApp...")
        self.stdout.write(f"   Para: +{telefone}")
        self.stdout.write(f"   Mensagem: {mensagem}")

        # Formatar telefone
        telefone_limpo = "".join(filter(str.isdigit, telefone))
        if not telefone_limpo.startswith("55"):
            telefone_limpo = "55" + telefone_limpo

        # Enviar mensagem
        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"

        data = {
            "From": "whatsapp:+14155238886",
            "To": f"whatsapp:+{telefone_limpo}",
            "Body": mensagem,
        }

        try:
            response = requests.post(
                url, data=data, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            )

            if response.status_code == 201:
                result = response.json()
                self.stdout.write(
                    self.style.SUCCESS("✅ WhatsApp enviado com sucesso!")
                )
                self.stdout.write(f"   Message SID: {result.get('sid')}")
                self.stdout.write(f"   Status: {result.get('status')}")
                self.stdout.write(f"   Para: {result.get('to')}")
                self.stdout.write(f"   De: {result.get('from')}")
            else:
                self.stdout.write(self.style.ERROR(f"❌ Erro: {response.status_code}"))
                self.stdout.write(f"   Resposta: {response.text}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro: {e!s}"))

        self.stdout.write(
            "\n💡 DICA: Se der erro 21212, você precisa ativar o sandbox:"
        )
        self.stdout.write("   1. Acesse: https://console.twilio.com/")
        self.stdout.write(
            "   2. Vá em: Messaging → Try it out → Send a WhatsApp message"
        )
        self.stdout.write("   3. Envie 'join <código>' para +1 415 523 8886")
