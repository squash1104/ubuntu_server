from django.core.management.base import BaseCommand
import requests
import json


class Command(BaseCommand):
    help = 'Configura e testa o WhatsApp Sandbox do Twilio'

    def add_arguments(self, parser):
        parser.add_argument('--telefone', type=str, help='Número de telefone para teste')
        parser.add_argument('--codigo', type=str, help='Código de ativação do sandbox')

    def handle(self, *args, **options):
        telefone = options.get('telefone', '5565999616000')
        codigo = options.get('codigo')
        
        # Carregar configurações
        try:
            from twilio_config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
        except ImportError:
            self.stdout.write(self.style.ERROR("❌ Arquivo twilio_config.py não encontrado"))
            return
        
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            self.stdout.write(self.style.ERROR("❌ Credenciais do Twilio não configuradas"))
            return
        
        self.stdout.write("🔧 Configurando WhatsApp Sandbox...")
        self.stdout.write(f"   Account SID: {TWILIO_ACCOUNT_SID}")
        self.stdout.write(f"   Telefone: +{telefone}")
        
        # Verificar se o sandbox está ativo
        self.verificar_sandbox_status(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        if codigo:
            self.ativar_sandbox(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, codigo)
        else:
            self.mostrar_instrucoes_ativacao()

    def verificar_sandbox_status(self, account_sid, auth_token):
        """Verifica o status do sandbox"""
        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
            response = requests.get(url, auth=(account_sid, auth_token))
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS("✅ Conexão com Twilio OK"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ Erro na conexão: {response.status_code}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro: {str(e)}"))

    def ativar_sandbox(self, account_sid, auth_token, codigo):
        """Ativa o sandbox com o código"""
        try:
            # Enviar mensagem de ativação
            url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
            data = {
                'From': 'whatsapp:+14155238886',
                'To': f'whatsapp:+{codigo}',
                'Body': 'join <código-do-sandbox>'
            }
            
            response = requests.post(url, data=data, auth=(account_sid, auth_token))
            
            if response.status_code == 201:
                self.stdout.write(self.style.SUCCESS("✅ Sandbox ativado com sucesso!"))
                self.testar_envio(account_sid, auth_token)
            else:
                self.stdout.write(self.style.ERROR(f"❌ Erro ao ativar: {response.text}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro: {str(e)}"))

    def testar_envio(self, account_sid, auth_token):
        """Testa o envio de mensagem"""
        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
            data = {
                'From': 'whatsapp:+14155238886',
                'To': 'whatsapp:+5565999616000',
                'Body': '🎉 Teste do sistema de mensagens! WhatsApp funcionando! 🎉'
            }
            
            response = requests.post(url, data=data, auth=(account_sid, auth_token))
            
            if response.status_code == 201:
                result = response.json()
                self.stdout.write(self.style.SUCCESS("✅ Mensagem WhatsApp enviada com sucesso!"))
                self.stdout.write(f"   Message SID: {result.get('sid')}")
            else:
                self.stdout.write(self.style.ERROR(f"❌ Erro ao enviar: {response.text}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro: {str(e)}"))

    def mostrar_instrucoes_ativacao(self):
        """Mostra instruções para ativar o sandbox"""
        self.stdout.write("\n📱 INSTRUÇÕES PARA ATIVAR O WHATSAPP SANDBOX:")
        self.stdout.write("=" * 60)
        self.stdout.write("1. Acesse: https://console.twilio.com/")
        self.stdout.write("2. Vá em: Messaging → Try it out → Send a WhatsApp message")
        self.stdout.write("3. Você verá um código como: 'join <código>'")
        self.stdout.write("4. Envie essa mensagem para: +1 415 523 8886")
        self.stdout.write("5. Aguarde a confirmação")
        self.stdout.write("6. Execute: python manage.py configurar_whatsapp_sandbox --codigo=SEU_CODIGO")
        self.stdout.write("\n💡 DICA: Use o número +1 415 523 8886 para ativar o sandbox")
        self.stdout.write("   Depois você pode enviar para qualquer número brasileiro!")
