import requests
import json
from django.conf import settings
from django.utils import timezone
from .models import MensagemAniversario, StatusMensagem


class MensagemService:
    """Serviço para envio de mensagens via SMS e WhatsApp"""
    
    def __init__(self):
        # Tentar carregar do arquivo de configuração primeiro
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from twilio_config import (
                TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, 
                TWILIO_WHATSAPP_NUMBER, TWILIO_SMS_NUMBER, DEBUG_MODE
            )
            self.twilio_account_sid = TWILIO_ACCOUNT_SID
            self.twilio_auth_token = TWILIO_AUTH_TOKEN
            self.twilio_whatsapp_number = TWILIO_WHATSAPP_NUMBER
            self.twilio_sms_number = TWILIO_SMS_NUMBER
            self.debug_mode = DEBUG_MODE
            self.usar_apenas_sms = getattr(__import__('twilio_config'), 'USAR_APENAS_SMS', False)
        except ImportError:
            # Fallback para settings do Django
            self.twilio_account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
            self.twilio_auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
            self.twilio_whatsapp_number = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', None)
            self.twilio_sms_number = getattr(settings, 'TWILIO_SMS_NUMBER', None)
            self.debug_mode = getattr(settings, 'DEBUG', True)
    
    def enviar_mensagem(self, destinatario_nome, destinatario_telefone, destinatario_tipo, 
                       destinatario_id, tipo_mensagem, conteudo, template_usado, enviado_por):
        """Envia uma mensagem para um destinatário"""
        
        # Processar template substituindo variáveis
        conteudo_processado = self.processar_template(conteudo, destinatario_nome)
        
        # Criar registro da mensagem
        mensagem = MensagemAniversario.objects.create(
            destinatario_nome=destinatario_nome,
            destinatario_telefone=destinatario_telefone,
            destinatario_tipo=destinatario_tipo,
            destinatario_id=destinatario_id,
            tipo_mensagem=tipo_mensagem,
            conteudo=conteudo_processado,
            template_usado=template_usado,
            enviado_por=enviado_por,
            status=StatusMensagem.PENDENTE
        )
        
        try:
            # Modo debug - simular envio sem usar API real
            if self.debug_mode or not self.twilio_account_sid or not self.twilio_auth_token:
                print(f"🔧 MODO DEBUG - Simulando envio de {tipo_mensagem.upper()}")
                print(f"   Para: {destinatario_nome} ({destinatario_telefone})")
                print(f"   Conteúdo: {conteudo}")
                print(f"   {'='*50}")
                
                # Simular sucesso
                resultado = {
                    'message_id': f'debug_{mensagem.id}',
                    'status': 'sent',
                    'debug_mode': True
                }
                
                mensagem.status = StatusMensagem.ENVIADA
                mensagem.data_processamento = timezone.now()
                mensagem.api_message_id = resultado.get('message_id')
                mensagem.api_response = resultado
                mensagem.save()
                
                return {
                    'success': True,
                    'message_id': mensagem.id,
                    'api_message_id': resultado.get('message_id'),
                    'debug_mode': True
                }
            
            # Modo produção - usar API real do Twilio
            if tipo_mensagem == 'whatsapp' and not self.usar_apenas_sms:
                resultado = self._enviar_whatsapp(destinatario_telefone, conteudo_processado)
            elif tipo_mensagem == 'whatsapp' and self.usar_apenas_sms:
                # Se configurado para usar apenas SMS, enviar WhatsApp como SMS
                resultado = self._enviar_sms(destinatario_telefone, f"📱 WhatsApp: {conteudo_processado}")
            elif tipo_mensagem == 'sms':
                resultado = self._enviar_sms(destinatario_telefone, conteudo_processado)
            else:
                raise ValueError(f"Tipo de mensagem não suportado: {tipo_mensagem}")
            
            # Atualizar status da mensagem
            mensagem.status = StatusMensagem.ENVIADA
            mensagem.data_processamento = timezone.now()
            mensagem.api_message_id = resultado.get('message_id')
            mensagem.api_response = resultado
            mensagem.save()
            
            return {
                'success': True,
                'message_id': mensagem.id,
                'api_message_id': resultado.get('message_id')
            }
            
        except Exception as e:
            # Marcar como falhou
            mensagem.status = StatusMensagem.FALHOU
            mensagem.data_processamento = timezone.now()
            mensagem.erro_detalhes = str(e)
            mensagem.save()
            
            return {
                'success': False,
                'error': str(e),
                'message_id': mensagem.id
            }
    
    def _enviar_whatsapp(self, telefone, conteudo):
        """Envia mensagem via WhatsApp usando Twilio"""
        if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_whatsapp_number]):
            raise Exception("Configurações do WhatsApp não encontradas")
        
        # Formatar telefone para WhatsApp (remover caracteres especiais e adicionar código do país)
        telefone_limpo = ''.join(filter(str.isdigit, telefone))
        if not telefone_limpo.startswith('55'):  # Código do Brasil
            telefone_limpo = '55' + telefone_limpo
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
        
        data = {
            'From': 'whatsapp:+14155238886',
            'To': f'whatsapp:+{telefone_limpo}',
            'Body': conteudo
        }
        
        response = requests.post(
            url,
            data=data,
            auth=(self.twilio_account_sid, self.twilio_auth_token)
        )
        
        if response.status_code == 201:
            result = response.json()
            return {
                'message_id': result.get('sid'),
                'status': result.get('status', 'sent'),
                'account_sid': result.get('account_sid'),
                'api_version': result.get('api_version')
            }
        else:
            raise Exception(f"Erro ao enviar WhatsApp: {response.text}")
    
    def _enviar_sms(self, telefone, conteudo):
        """Envia SMS usando Twilio"""
        if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_sms_number]):
            raise Exception("Configurações do SMS não encontradas")
        
        # Formatar telefone para SMS
        telefone_limpo = ''.join(filter(str.isdigit, telefone))
        if not telefone_limpo.startswith('55'):  # Código do Brasil
            telefone_limpo = '55' + telefone_limpo
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
        
        data = {
            'From': self.twilio_sms_number,
            'To': f'+{telefone_limpo}',
            'Body': conteudo
        }
        
        response = requests.post(
            url,
            data=data,
            auth=(self.twilio_account_sid, self.twilio_auth_token)
        )
        
        if response.status_code == 201:
            return {
                'message_id': response.json().get('sid'),
                'status': 'sent'
            }
        else:
            raise Exception(f"Erro ao enviar SMS: {response.text}")
    
    def processar_template(self, template_conteudo, nome, idade=None):
        """Processa um template substituindo variáveis"""
        conteudo = template_conteudo.replace('{nome}', nome)
        if idade is not None:
            conteudo = conteudo.replace('{idade}', str(idade))
        return conteudo
