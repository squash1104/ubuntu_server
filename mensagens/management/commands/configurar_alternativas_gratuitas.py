from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Configura alternativas gratuitas para envio de mensagens"

    def handle(self, *args, **options):
        self.stdout.write("🆓 ALTERNATIVAS GRATUITAS PARA MENSAGENS:")
        self.stdout.write("=" * 50)

        self.stdout.write("\n1. 📧 EMAIL (100% Gratuito)")
        self.stdout.write("   - Usar Django Email Backend")
        self.stdout.write("   - Gmail, Outlook, etc.")
        self.stdout.write("   - Sem custos")

        self.stdout.write("\n2. 📱 WhatsApp Web API (Gratuito)")
        self.stdout.write("   - Usar selenium + WhatsApp Web")
        self.stdout.write("   - Requer automação")
        self.stdout.write("   - Limitações do WhatsApp")

        self.stdout.write("\n3. 📱 Telegram Bot (Gratuito)")
        self.stdout.write("   - Criar bot no Telegram")
        self.stdout.write("   - API gratuita")
        self.stdout.write("   - Usuários precisam ter Telegram")

        self.stdout.write("\n4. 📱 SMS via Email (Gratuito)")
        self.stdout.write("   - Enviar para: numero@operadora.com")
        self.stdout.write("   - Ex: 5565999616000@vivo.com.br")
        self.stdout.write("   - Funciona com algumas operadoras")

        self.stdout.write("\n5. 💬 Discord/Slack (Gratuito)")
        self.stdout.write("   - Webhooks gratuitos")
        self.stdout.write("   - Para notificações internas")

        self.stdout.write("\n💡 RECOMENDAÇÃO:")
        self.stdout.write("   Use SMS via Twilio (mais barato) ou")
        self.stdout.write("   Email (100% gratuito) para começar")

        self.stdout.write("\n🔧 Para implementar email:")
        self.stdout.write("   python manage.py configurar_email_gratuito")
