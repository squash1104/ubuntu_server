from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Configura o modo de envio de mensagens"

    def add_arguments(self, parser):
        parser.add_argument(
            "--modo",
            type=str,
            choices=["sms", "whatsapp", "ambos"],
            default="sms",
            help="Modo de envio: sms, whatsapp ou ambos",
        )

    def handle(self, *args, **options):
        modo = options.get("modo")

        # Ler arquivo atual
        try:
            with open("/srv/sisvot/twilio_config.py") as f:
                conteudo = f.read()
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR("❌ Arquivo twilio_config.py não encontrado")
            )
            return

        # Atualizar configuração
        if modo == "sms":
            conteudo = conteudo.replace(
                "USAR_APENAS_SMS = False", "USAR_APENAS_SMS = True"
            )
            self.stdout.write("✅ Configurado para usar APENAS SMS")
            self.stdout.write("   - WhatsApp será enviado como SMS")
            self.stdout.write("   - Mais barato que WhatsApp")
        elif modo == "whatsapp":
            conteudo = conteudo.replace(
                "USAR_APENAS_SMS = True", "USAR_APENAS_SMS = False"
            )
            self.stdout.write("✅ Configurado para usar WhatsApp")
            self.stdout.write("   - Requer upgrade da conta Twilio")
            self.stdout.write("   - Mais caro que SMS")
        elif modo == "ambos":
            conteudo = conteudo.replace(
                "USAR_APENAS_SMS = True", "USAR_APENAS_SMS = False"
            )
            self.stdout.write("✅ Configurado para usar SMS e WhatsApp")
            self.stdout.write("   - Requer upgrade da conta Twilio para WhatsApp")

        # Salvar arquivo
        try:
            with open("/srv/sisvot/twilio_config.py", "w") as f:
                f.write(conteudo)
            self.stdout.write(self.style.SUCCESS("✅ Configuração salva com sucesso!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao salvar: {e!s}"))

        self.stdout.write("\n💡 Para testar:")
        self.stdout.write(
            "   python manage.py testar_mensagens --telefone=5565999616000 --tipo=whatsapp"
        )
