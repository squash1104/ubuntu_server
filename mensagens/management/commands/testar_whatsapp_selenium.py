from django.core.management.base import BaseCommand
from mensagens.whatsapp_selenium import WhatsAppSelenium


class Command(BaseCommand):
    help = 'Testa envio de WhatsApp via Selenium'

    def add_arguments(self, parser):
        parser.add_argument('--telefone', type=str, default='5565999616000', help='Número de telefone')
        parser.add_argument('--mensagem', type=str, default='🎉 Teste do WhatsApp Selenium! 🎉', help='Mensagem para enviar')

    def handle(self, *args, **options):
        telefone = options.get('telefone')
        mensagem = options.get('mensagem')
        
        self.stdout.write("📱 Testando WhatsApp via Selenium...")
        self.stdout.write(f"   Telefone: {telefone}")
        self.stdout.write(f"   Mensagem: {mensagem}")
        
        whatsapp = WhatsAppSelenium()
        
        try:
            # Fazer login
            if whatsapp.login():
                # Enviar mensagem
                sucesso = whatsapp.enviar_mensagem(telefone, mensagem)
                
                if sucesso:
                    self.stdout.write(self.style.SUCCESS("✅ Mensagem enviada com sucesso!"))
                else:
                    self.stdout.write(self.style.ERROR("❌ Falha ao enviar mensagem"))
            else:
                self.stdout.write(self.style.ERROR("❌ Falha no login"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro: {str(e)}"))
        finally:
            # Fechar navegador
            whatsapp.fechar()
        
        self.stdout.write("\n💡 INSTRUÇÕES:")
        self.stdout.write("   1. O Chrome abrirá automaticamente")
        self.stdout.write("   2. Escaneie o QR Code com seu WhatsApp")
        self.stdout.write("   3. Aguarde o login ser realizado")
        self.stdout.write("   4. A mensagem será enviada automaticamente")
