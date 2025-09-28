from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Guia completo para configurar WhatsApp Business API"

    def handle(self, *args, **options):
        self.stdout.write("📱 GUIA COMPLETO - WHATSAPP BUSINESS API")
        self.stdout.write("=" * 60)

        self.stdout.write("\n🔗 PASSO 1: CRIAR CONTA META DEVELOPERS")
        self.stdout.write("-" * 40)
        self.stdout.write("1. Acesse: https://developers.facebook.com/")
        self.stdout.write("2. Clique em 'Get Started'")
        self.stdout.write("3. Faça login com sua conta Facebook")
        self.stdout.write("4. Se não tiver, crie uma conta Facebook")
        self.stdout.write("5. Complete o perfil de desenvolvedor")

        self.stdout.write("\n🔗 PASSO 2: CRIAR APLICAÇÃO")
        self.stdout.write("-" * 40)
        self.stdout.write("1. No painel, clique em 'Create App'")
        self.stdout.write("2. Escolha 'Business' como tipo")
        self.stdout.write("3. Preencha:")
        self.stdout.write("   - App Name: Sistema Fidelização")
        self.stdout.write("   - App Contact Email: seu@email.com")
        self.stdout.write("   - Business Account: (criar se necessário)")
        self.stdout.write("4. Clique em 'Create App'")

        self.stdout.write("\n🔗 PASSO 3: CONFIGURAR WHATSAPP")
        self.stdout.write("-" * 40)
        self.stdout.write("1. No painel da app, procure 'WhatsApp'")
        self.stdout.write("2. Clique em 'Set up'")
        self.stdout.write("3. Escolha 'Cloud API' (gratuito)")
        self.stdout.write("4. Anote o 'Phone Number ID'")
        self.stdout.write("5. Anote o 'WhatsApp Business Account ID'")

        self.stdout.write("\n🔗 PASSO 4: OBTER TOKEN DE ACESSO")
        self.stdout.write("-" * 40)
        self.stdout.write("1. Vá em 'WhatsApp' > 'API Setup'")
        self.stdout.write("2. Clique em 'Generate Token'")
        self.stdout.write("3. Copie o 'Temporary Access Token'")
        self.stdout.write("4. ⚠️ IMPORTANTE: Este token expira em 24h")
        self.stdout.write("5. Para token permanente, configure webhook")

        self.stdout.write("\n🔗 PASSO 5: CONFIGURAR WEBHOOK (OPCIONAL)")
        self.stdout.write("-" * 40)
        self.stdout.write("1. Vá em 'WhatsApp' > 'Configuration'")
        self.stdout.write("2. Em 'Webhook', clique em 'Configure'")
        self.stdout.write("3. URL do Webhook: https://seu-dominio.com/webhook/")
        self.stdout.write("4. Verify Token: (crie um token aleatório)")
        self.stdout.write("5. Marque 'messages' e 'message_deliveries'")

        self.stdout.write("\n🔗 PASSO 6: TESTAR CONFIGURAÇÃO")
        self.stdout.write("-" * 40)
        self.stdout.write("1. Use o comando:")
        self.stdout.write("   python manage.py testar_whatsapp_cloud_api")
        self.stdout.write("2. Ou teste via cURL:")
        self.stdout.write(
            "   curl -X POST 'https://graph.facebook.com/v18.0/SEU_PHONE_NUMBER_ID/messages' \\"
        )
        self.stdout.write("   -H 'Authorization: Bearer SEU_ACCESS_TOKEN' \\")
        self.stdout.write("   -H 'Content-Type: application/json' \\")
        self.stdout.write(
            '   -d \'{"messaging_product": "whatsapp", "to": "5565999616000", "type": "text", "text": {"body": "Teste!"}}\''
        )

        self.stdout.write("\n💡 INFORMAÇÕES IMPORTANTES:")
        self.stdout.write("-" * 40)
        self.stdout.write("✅ 1000 mensagens/mês gratuitas")
        self.stdout.write("✅ API oficial do Meta")
        self.stdout.write("✅ Sem necessidade de navegador")
        self.stdout.write("✅ Funciona em servidor")
        self.stdout.write("⚠️ Token temporário expira em 24h")
        self.stdout.write("⚠️ Precisa de domínio HTTPS para webhook")

        self.stdout.write("\n🔧 PRÓXIMOS PASSOS:")
        self.stdout.write("-" * 40)
        self.stdout.write("1. Configure as credenciais no sistema")
        self.stdout.write("2. Teste o envio de mensagens")
        self.stdout.write("3. Configure webhook para token permanente")
        self.stdout.write("4. Implemente no sistema de aniversários")
