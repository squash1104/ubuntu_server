# 📱 Configuração do Sistema de Mensagens - Twilio

## 🚀 Passo a Passo para Configurar

### 1. Criar Conta no Twilio
1. Acesse: https://console.twilio.com/
2. Clique em "Sign up" para criar uma conta gratuita
3. Preencha os dados solicitados
4. Verifique seu telefone e email

### 2. Obter Credenciais
1. No dashboard do Twilio, você verá:
   - **Account SID**: Começa com "AC..."
   - **Auth Token**: Clique em "Show" para revelar

### 3. Configurar WhatsApp (Sandbox - Gratuito)
1. No console, vá em "Messaging" > "Try it out" > "Send a WhatsApp message"
2. Siga as instruções para conectar seu WhatsApp ao sandbox
3. O número sandbox é: `+14155238886`
4. Para ativar, envie a mensagem que aparece no console para o número

### 4. Configurar SMS (Pago)
1. No console, vá em "Phone Numbers" > "Manage" > "Buy a number"
2. Escolha um número de telefone
3. Configure as permissões necessárias

### 5. Atualizar Configurações
Edite o arquivo `twilio_config.py`:

```python
# Substitua pelos seus valores reais
TWILIO_ACCOUNT_SID = "AC1234567890abcdef1234567890abcdef"
TWILIO_AUTH_TOKEN = "your_auth_token_here"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Sandbox
TWILIO_SMS_NUMBER = "+1234567890"  # Seu número comprado
```

### 6. Testar o Sistema
```bash
# Teste em modo debug (simula envio)
python manage.py testar_mensagens --telefone=5511999999999 --tipo=whatsapp

# Teste real (após configurar credenciais)
python manage.py testar_mensagens --telefone=5511999999999 --tipo=whatsapp --real
```

## 🔧 Modo Debug vs Produção

### Modo Debug (Atual)
- ✅ Simula envio sem custos
- ✅ Salva no banco de dados
- ✅ Mostra logs detalhados
- ❌ Não envia mensagens reais

### Modo Produção
- ✅ Envia mensagens reais
- ✅ Usa API do Twilio
- ❌ Gera custos por mensagem
- ❌ Requer credenciais válidas

## 💰 Custos do Twilio

### WhatsApp
- **Sandbox**: Gratuito (limitado)
- **Produção**: ~$0.005 por mensagem

### SMS
- **Brasil**: ~$0.0075 por mensagem
- **Número de telefone**: ~$1.00/mês

## 🛠️ Solução de Problemas

### Erro: "Invalid Account SID"
- Verifique se copiou o SID corretamente
- Certifique-se de que não há espaços extras

### Erro: "Authentication failed"
- Verifique o Auth Token
- Certifique-se de que a conta está ativa

### WhatsApp não funciona
- Ative o sandbox enviando a mensagem de ativação
- Verifique se o número está no formato correto: `+5511999999999`

### SMS não funciona
- Verifique se comprou um número de telefone
- Confirme as permissões do número

## 📞 Formato de Telefone

Use sempre o formato internacional:
- **Brasil**: `+5511999999999`
- **Remover**: espaços, parênteses, hífens
- **Adicionar**: código do país (+55 para Brasil)

## 🔒 Segurança

- ⚠️ **NUNCA** commite credenciais no Git
- ✅ Use variáveis de ambiente em produção
- ✅ Mantenha as credenciais em arquivos separados
- ✅ Revogue tokens comprometidos imediatamente
