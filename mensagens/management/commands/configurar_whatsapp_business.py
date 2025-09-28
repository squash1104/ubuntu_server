from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Configura WhatsApp Business API gratuito'

    def handle(self, *args, **options):
        self.stdout.write("📱 WHATSAPP BUSINESS API GRATUITO:")
        self.stdout.write("=" * 50)
        
        self.stdout.write("\n1. 🆓 META DEVELOPERS (Gratuito)")
        self.stdout.write("   - Acesse: https://developers.facebook.com/")
        self.stdout.write("   - Crie uma conta de desenvolvedor")
        self.stdout.write("   - Configure WhatsApp Business API")
        self.stdout.write("   - 1000 mensagens/mês gratuitas")
        
        self.stdout.write("\n2. 📱 WHATSAPP CLOUD API")
        self.stdout.write("   - API oficial do Meta")
        self.stdout.write("   - Sem custos para pequenos volumes")
        self.stdout.write("   - Requer verificação de negócio")
        
        self.stdout.write("\n3. 🔧 IMPLEMENTAÇÃO:")
        self.stdout.write("   - Usar requests + Meta API")
        self.stdout.write("   - Mais simples que Selenium")
        self.stdout.write("   - Mais confiável")
        
        self.stdout.write("\n4. 📋 PASSOS:")
        self.stdout.write("   1. Criar app no Meta Developers")
        self.stdout.write("   2. Configurar WhatsApp Business")
        self.stdout.write("   3. Obter token de acesso")
        self.stdout.write("   4. Implementar envio via API")
        
        self.stdout.write("\n💡 VANTAGENS:")
        self.stdout.write("   ✅ 1000 mensagens/mês gratuitas")
        self.stdout.write("   ✅ API oficial e confiável")
        self.stdout.write("   ✅ Sem necessidade de navegador")
        self.stdout.write("   ✅ Funciona em servidor")
        
        self.stdout.write("\n🔧 Para implementar:")
        self.stdout.write("   python manage.py implementar_whatsapp_cloud_api")
