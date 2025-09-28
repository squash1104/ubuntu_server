import requests
import json
from django.conf import settings


class WhatsAppCloudAPI:
    """Serviço para envio de mensagens via WhatsApp Cloud API do Meta"""
    
    def __init__(self):
        # Configurações do WhatsApp Cloud API
        self.base_url = "https://graph.facebook.com/v18.0"
        self.phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', None)
        self.access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', None)
        self.business_account_id = getattr(settings, 'WHATSAPP_BUSINESS_ACCOUNT_ID', None)
        
    def enviar_mensagem(self, telefone, mensagem):
        """Envia uma mensagem via WhatsApp Cloud API"""
        
        if not all([self.phone_number_id, self.access_token]):
            raise Exception("Configurações do WhatsApp não encontradas. Configure WHATSAPP_PHONE_NUMBER_ID e WHATSAPP_ACCESS_TOKEN")
        
        # Formatar telefone
        telefone_limpo = ''.join(filter(str.isdigit, telefone))
        if not telefone_limpo.startswith('55'):
            telefone_limpo = '55' + telefone_limpo
        
        # URL da API
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        # Headers
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Payload da mensagem
        payload = {
            "messaging_product": "whatsapp",
            "to": telefone_limpo,
            "type": "text",
            "text": {
                "body": mensagem
            }
        }
        
        try:
            # Fazer requisição
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                'success': True,
                'message_id': result.get('messages', [{}])[0].get('id'),
                'status': 'sent',
                'api_response': result
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'api_response': getattr(e.response, 'json', lambda: {})() if hasattr(e, 'response') else {}
            }
    
    def enviar_multiplas_mensagens(self, destinatarios):
        """Envia mensagens para múltiplos destinatários"""
        resultados = []
        
        for destinatario in destinatarios:
            telefone = destinatario.get('telefone', '')
            nome = destinatario.get('nome', '')
            mensagem = destinatario.get('mensagem', '')
            
            resultado = self.enviar_mensagem(telefone, mensagem)
            resultado['nome'] = nome
            resultado['telefone'] = telefone
            
            resultados.append(resultado)
        
        return resultados
    
    def verificar_configuracao(self):
        """Verifica se a configuração está correta"""
        if not self.phone_number_id:
            return False, "WHATSAPP_PHONE_NUMBER_ID não configurado"
        
        if not self.access_token:
            return False, "WHATSAPP_ACCESS_TOKEN não configurado"
        
        # Testar conexão
        try:
            url = f"{self.base_url}/{self.phone_number_id}"
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return True, "Configuração OK"
        except Exception as e:
            return False, f"Erro na configuração: {str(e)}"
