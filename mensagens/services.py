import os

import requests
from django.conf import settings
from django.utils import timezone

from .models import Mensagem, MensagemAniversario, StatusMensagem


class MensagemService:
    """Serviço para envio de mensagens via SMS e WhatsApp"""

    def __init__(self):
        try:
            import sys

            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from twilio_config import (
                DEBUG_MODE,
                TWILIO_ACCOUNT_SID,
                TWILIO_AUTH_TOKEN,
                TWILIO_SMS_NUMBER,
                TWILIO_WHATSAPP_NUMBER,
                USAR_WHATSAPP_CLOUD_API,
            )

            self.twilio_account_sid = TWILIO_ACCOUNT_SID
            self.twilio_auth_token = TWILIO_AUTH_TOKEN
            self.twilio_whatsapp_number = TWILIO_WHATSAPP_NUMBER
            self.twilio_sms_number = TWILIO_SMS_NUMBER
            self.debug_mode = DEBUG_MODE
            self.usar_apenas_sms = getattr(
                __import__("twilio_config"), "USAR_APENAS_SMS", False
            )
            self.usar_whatsapp_cloud_api = USAR_WHATSAPP_CLOUD_API
        except ImportError:
            self.twilio_account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
            self.twilio_auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
            self.twilio_whatsapp_number = getattr(
                settings, "TWILIO_WHATSAPP_NUMBER", None
            )
            self.twilio_sms_number = getattr(settings, "TWILIO_SMS_NUMBER", None)
            self.debug_mode = getattr(settings, "DEBUG", True)
            self.usar_whatsapp_cloud_api = getattr(
                settings, "USAR_WHATSAPP_CLOUD_API", False
            )

    def _media_url_para_caminho(self, media_url):
        """Converte URL de mídia (/mensagens/arquivo/...) para caminho absoluto no disco"""
        if not media_url:
            return None
        if media_url.startswith("/mensagens/arquivo/"):
            relative_path = media_url.replace("/mensagens/arquivo/", "", 1)
            return os.path.normpath(os.path.join(settings.MEDIA_ROOT, relative_path))
        return None

    def _enviar_via_whatsapp_cloud(self, telefone, conteudo, media_url=None):
        """Envia mensagem via WhatsApp Cloud API (Meta), com suporte a mídia"""
        from .whatsapp_cloud_api import WhatsAppCloudAPI

        api = WhatsAppCloudAPI()
        caminho_midia = self._media_url_para_caminho(media_url) if media_url else None

        resultados = api.enviar_mensagem_completa(
            telefone=telefone,
            mensagem=conteudo,
            caminho_midia=caminho_midia,
        )

        sucesso = any(r.get("success") for r in resultados)
        primeiro = resultados[0] if resultados else {}

        if sucesso:
            return {
                "message_id": primeiro.get("message_id", "cloud_api"),
                "status": "sent",
                "api_response": resultados,
            }
        raise Exception(primeiro.get("error", "Falha ao enviar via WhatsApp Cloud API"))

    def enviar_mensagem(
        self,
        destinatario_nome,
        destinatario_telefone,
        destinatario_tipo,
        destinatario_id,
        tipo_mensagem,
        conteudo,
        template_usado,
        enviado_por,
    ):
        """Envia uma mensagem para um destinatário"""
        conteudo_processado = self.processar_template(conteudo, destinatario_nome)

        mensagem = MensagemAniversario.objects.create(
            destinatario_nome=destinatario_nome,
            destinatario_telefone=destinatario_telefone,
            destinatario_tipo=destinatario_tipo,
            destinatario_id=destinatario_id,
            tipo_mensagem=tipo_mensagem,
            conteudo=conteudo_processado,
            template_usado=template_usado,
            enviado_por=enviado_por,
            status=StatusMensagem.PENDENTE,
        )

        try:
            if (
                self.debug_mode
                or not self.twilio_account_sid
                or not self.twilio_auth_token
            ):
                print(f"🔧 MODO DEBUG - Simulando envio de {tipo_mensagem.upper()}")
                print(f"   Para: {destinatario_nome} ({destinatario_telefone})")
                print(f"   Conteúdo: {conteudo}")
                print(f"   {'='*50}")

                resultado = {
                    "message_id": f"debug_{mensagem.id}",
                    "status": "sent",
                    "debug_mode": True,
                }

                mensagem.status = StatusMensagem.ENVIADA
                mensagem.data_processamento = timezone.now()
                mensagem.api_message_id = resultado.get("message_id")
                mensagem.api_response = resultado
                mensagem.save()

                return {
                    "success": True,
                    "message_id": mensagem.id,
                    "api_message_id": resultado.get("message_id"),
                    "debug_mode": True,
                }

            if tipo_mensagem == "whatsapp" and self.usar_whatsapp_cloud_api:
                resultado = self._enviar_via_whatsapp_cloud(
                    destinatario_telefone, conteudo_processado
                )
            elif tipo_mensagem == "whatsapp" and not self.usar_apenas_sms:
                resultado = self._enviar_whatsapp(
                    destinatario_telefone, conteudo_processado
                )
            elif tipo_mensagem == "whatsapp" and self.usar_apenas_sms:
                resultado = self._enviar_sms(
                    destinatario_telefone, f"📱 WhatsApp: {conteudo_processado}"
                )
            elif tipo_mensagem == "sms":
                resultado = self._enviar_sms(destinatario_telefone, conteudo_processado)
            else:
                raise ValueError(f"Tipo de mensagem não suportado: {tipo_mensagem}")

            mensagem.status = StatusMensagem.ENVIADA
            mensagem.data_processamento = timezone.now()
            mensagem.api_message_id = resultado.get("message_id")
            mensagem.api_response = resultado
            mensagem.save()

            return {
                "success": True,
                "message_id": mensagem.id,
                "api_message_id": resultado.get("message_id"),
            }

        except Exception as e:
            mensagem.status = StatusMensagem.FALHOU
            mensagem.data_processamento = timezone.now()
            mensagem.erro_detalhes = str(e)
            mensagem.save()

            return {"success": False, "error": str(e), "message_id": mensagem.id}

    def _enviar_whatsapp(self, telefone, conteudo, media_url=None):
        """Envia mensagem via WhatsApp usando Twilio, com suporte a mídia"""
        if not all(
            [
                self.twilio_account_sid,
                self.twilio_auth_token,
                self.twilio_whatsapp_number,
            ]
        ):
            raise Exception("Configurações do WhatsApp não encontradas")

        telefone_limpo = "".join(filter(str.isdigit, telefone))
        if not telefone_limpo.startswith("55"):
            telefone_limpo = "55" + telefone_limpo

        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"

        data = {
            "From": "whatsapp:+14155238886",
            "To": f"whatsapp:+{telefone_limpo}",
            "Body": conteudo,
        }

        if media_url:
            data["MediaUrl"] = media_url

        response = requests.post(
            url, data=data, auth=(self.twilio_account_sid, self.twilio_auth_token)
        )

        if response.status_code == 201:
            result = response.json()
            return {
                "message_id": result.get("sid"),
                "status": result.get("status", "sent"),
                "account_sid": result.get("account_sid"),
                "api_version": result.get("api_version"),
            }
        raise Exception(f"Erro ao enviar WhatsApp: {response.text}")

    def _enviar_sms(self, telefone, conteudo):
        """Envia SMS usando Twilio"""
        if not all(
            [self.twilio_account_sid, self.twilio_auth_token, self.twilio_sms_number]
        ):
            raise Exception("Configurações do SMS não encontradas")

        telefone_limpo = "".join(filter(str.isdigit, telefone))
        if not telefone_limpo.startswith("55"):
            telefone_limpo = "55" + telefone_limpo

        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"

        data = {
            "From": self.twilio_sms_number,
            "To": f"+{telefone_limpo}",
            "Body": conteudo,
        }

        response = requests.post(
            url, data=data, auth=(self.twilio_account_sid, self.twilio_auth_token)
        )

        if response.status_code == 201:
            return {"message_id": response.json().get("sid"), "status": "sent"}
        raise Exception(f"Erro ao enviar SMS: {response.text}")

    def enviar_mensagem_generico(
        self,
        destinatario_nome,
        destinatario_telefone,
        destinatario_tipo,
        destinatario_id,
        tipo_mensagem,
        conteudo,
        template_usado,
        enviado_por,
        campanha=None,
        media_url=None,
    ):
        """Envia uma mensagem usando o modelo Mensagem (genérico)"""

        conteudo_processado = self.processar_template(conteudo, destinatario_nome)

        mensagem = Mensagem.objects.create(
            campanha=campanha,
            destinatario_nome=destinatario_nome,
            destinatario_telefone=destinatario_telefone,
            destinatario_tipo=destinatario_tipo,
            destinatario_id=destinatario_id,
            tipo_mensagem=tipo_mensagem,
            conteudo=conteudo_processado,
            template_usado=template_usado,
            enviado_por=enviado_por,
            status=StatusMensagem.PENDENTE,
        )

        try:
            if (
                self.debug_mode
                or not self.twilio_account_sid
                or not self.twilio_auth_token
            ):
                print(f"🔧 MODO DEBUG - Simulando envio de {tipo_mensagem.upper()}")
                print(f"   Para: {destinatario_nome} ({destinatario_telefone})")
                print(f"   Conteúdo: {conteudo}")
                if media_url:
                    print(f"   Mídia: {media_url}")
                print(f"   {'='*50}")

                resultado = {
                    "message_id": f"debug_{mensagem.id}",
                    "status": "sent",
                    "debug_mode": True,
                }

                mensagem.status = StatusMensagem.ENVIADA
                mensagem.data_processamento = timezone.now()
                mensagem.api_message_id = resultado.get("message_id")
                mensagem.api_response = resultado
                mensagem.save()

                return {
                    "success": True,
                    "message_id": mensagem.id,
                    "api_message_id": resultado.get("message_id"),
                    "debug_mode": True,
                }

            if tipo_mensagem == "whatsapp" and self.usar_whatsapp_cloud_api:
                resultado = self._enviar_via_whatsapp_cloud(
                    destinatario_telefone, conteudo_processado, media_url
                )
            elif tipo_mensagem == "whatsapp" and not self.usar_apenas_sms:
                resultado = self._enviar_whatsapp(
                    destinatario_telefone, conteudo_processado, media_url
                )
            elif tipo_mensagem == "whatsapp" and self.usar_apenas_sms:
                resultado = self._enviar_sms(
                    destinatario_telefone, f"📱 WhatsApp: {conteudo_processado}"
                )
            elif tipo_mensagem == "sms":
                if media_url:
                    conteudo_processado += f"\n\n{media_url}"
                resultado = self._enviar_sms(destinatario_telefone, conteudo_processado)
            else:
                raise ValueError(f"Tipo de mensagem não suportado: {tipo_mensagem}")

            mensagem.status = StatusMensagem.ENVIADA
            mensagem.data_processamento = timezone.now()
            mensagem.api_message_id = resultado.get("message_id")
            mensagem.api_response = resultado
            mensagem.save()

            return {
                "success": True,
                "message_id": mensagem.id,
                "api_message_id": resultado.get("message_id"),
            }

        except Exception as e:
            mensagem.status = StatusMensagem.FALHOU
            mensagem.data_processamento = timezone.now()
            mensagem.erro_detalhes = str(e)
            mensagem.save()

            return {"success": False, "error": str(e), "message_id": mensagem.id}

    def processar_template(self, template_conteudo, nome, idade=None):
        """Processa um template substituindo variáveis"""
        conteudo = template_conteudo.replace("{nome}", nome)
        if idade is not None:
            conteudo = conteudo.replace("{idade}", str(idade))
        return conteudo
