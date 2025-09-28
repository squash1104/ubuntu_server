from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from mensagens.services import MensagemService


class Command(BaseCommand):
    help = 'Testa o sistema de envio de mensagens'

    def add_arguments(self, parser):
        parser.add_argument('--telefone', type=str, help='Número de telefone para teste')
        parser.add_argument('--tipo', type=str, choices=['sms', 'whatsapp'], default='whatsapp', help='Tipo de mensagem')
        parser.add_argument('--nome', type=str, default='Teste', help='Nome para o teste')

    def handle(self, *args, **options):
        telefone = options.get('telefone', '5511999999999')
        tipo = options.get('tipo', 'whatsapp')
        nome = options.get('nome', 'Teste')
        
        self.stdout.write(f"🧪 Testando envio de {tipo.upper()}...")
        self.stdout.write(f"   Para: {nome} ({telefone})")
        
        # Buscar usuário admin
        try:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.first()
        except:
            user = None
        
        if not user:
            self.stdout.write(self.style.ERROR("❌ Nenhum usuário encontrado para teste"))
            return
        
        # Testar envio
        service = MensagemService()
        
        try:
            resultado = service.enviar_mensagem(
                destinatario_nome=nome,
                destinatario_telefone=telefone,
                destinatario_tipo='colaborador',
                destinatario_id=1,
                tipo_mensagem=tipo,
                conteudo=f"🎉 Parabéns {nome}! Este é um teste do sistema de mensagens. 🎉",
                template_usado='teste',
                enviado_por=user
            )
            
            if resultado['success']:
                self.stdout.write(self.style.SUCCESS("✅ Teste realizado com sucesso!"))
                self.stdout.write(f"   Message ID: {resultado.get('api_message_id')}")
                if resultado.get('debug_mode'):
                    self.stdout.write(self.style.WARNING("   ⚠️  Modo DEBUG ativo - mensagem não foi enviada realmente"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ Erro no teste: {resultado.get('error')}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro durante o teste: {str(e)}"))
        
        self.stdout.write("\n📋 Para configurar o Twilio:")
        self.stdout.write("   1. Acesse https://console.twilio.com/")
        self.stdout.write("   2. Crie uma conta gratuita")
        self.stdout.write("   3. Copie Account SID e Auth Token")
        self.stdout.write("   4. Configure no arquivo twilio_config.py")
        self.stdout.write("   5. Para WhatsApp, use o sandbox: +14155238886")
