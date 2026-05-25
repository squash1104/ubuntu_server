import mimetypes
import os

import requests
from django.conf import settings


class WhatsAppCloudAPI:
    """Serviço para envio de mensagens via WhatsApp Cloud API do Meta"""

    def __init__(self):
        self.base_url = "https://graph.facebook.com/v18.0"
        self.phone_number_id = getattr(settings, "WHATSAPP_PHONE_NUMBER_ID", None)
        self.access_token = getattr(settings, "WHATSAPP_ACCESS_TOKEN", None)
        self.business_account_id = getattr(
            settings, "WHATSAPP_BUSINESS_ACCOUNT_ID", None
        )

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _format_telefone(self, telefone):
        telefone_limpo = "".join(filter(str.isdigit, telefone))
        if not telefone_limpo.startswith("55"):
            telefone_limpo = "55" + telefone_limpo
        return telefone_limpo

    def enviar_mensagem_texto(self, telefone, mensagem):
        """Envia uma mensagem de texto via WhatsApp Cloud API"""
        if not all([self.phone_number_id, self.access_token]):
            raise Exception("Configurações do WhatsApp não encontradas")

        telefone_limpo = self._format_telefone(telefone)
        url = f"{self.base_url}/{self.phone_number_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "to": telefone_limpo,
            "type": "text",
            "text": {"body": mensagem},
            "preview_url": False,
        }

        try:
            response = requests.post(url, headers=self._headers(), json=payload)
            response.raise_for_status()
            result = response.json()

            return {
                "success": True,
                "message_id": result.get("messages", [{}])[0].get("id"),
                "status": "sent",
                "api_response": result,
            }

        except requests.exceptions.RequestException as e:
            erro_info = {}
            if hasattr(e, "response") and e.response is not None:
                try:
                    erro_info = e.response.json()
                except Exception:
                    erro_info = {"body": e.response.text}
            return {
                "success": False,
                "error": str(e),
                "api_response": erro_info,
            }

    def upload_midia(self, caminho_arquivo):
        """Faz upload de uma imagem para o servidor do Meta e retorna o media_id"""
        if not os.path.exists(caminho_arquivo):
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")

        url = f"{self.base_url}/{self.phone_number_id}/media"

        mime_type, _ = mimetypes.guess_type(caminho_arquivo)
        if not mime_type:
            mime_type = "image/jpeg"

        nome_arquivo = os.path.basename(caminho_arquivo)

        with open(caminho_arquivo, "rb") as f:
            files = {
                "file": (nome_arquivo, f, mime_type),
            }
            data = {"messaging_product": "whatsapp"}

            headers = {
                "Authorization": f"Bearer {self.access_token}",
            }

            response = requests.post(url, headers=headers, data=data, files=files)

        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "media_id": result.get("id"),
                "api_response": result,
            }
        try:
            erro = response.json()
        except Exception:
            erro = {"body": response.text}
        raise Exception(f"Erro ao fazer upload de mídia: {erro}")

    def enviar_mensagem_midia(self, telefone, media_id, caption=None):
        """Envia uma mensagem com mídia (imagem) usando media_id já enviado ao Meta"""
        if not all([self.phone_number_id, self.access_token]):
            raise Exception("Configurações do WhatsApp não encontradas")

        telefone_limpo = self._format_telefone(telefone)
        url = f"{self.base_url}/{self.phone_number_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "to": telefone_limpo,
            "type": "image",
            "image": {
                "id": media_id,
            },
        }

        if caption:
            payload["image"]["caption"] = caption

        try:
            response = requests.post(url, headers=self._headers(), json=payload)
            response.raise_for_status()
            result = response.json()

            return {
                "success": True,
                "message_id": result.get("messages", [{}])[0].get("id"),
                "status": "sent",
                "api_response": result,
            }

        except requests.exceptions.RequestException as e:
            erro_info = {}
            if hasattr(e, "response") and e.response is not None:
                try:
                    erro_info = e.response.json()
                except Exception:
                    erro_info = {"body": e.response.text}
            return {
                "success": False,
                "error": str(e),
                "api_response": erro_info,
            }

    def enviar_mensagem_completa(self, telefone, mensagem=None, caminho_midia=None):
        """Envia texto + mídia para um destinatário.
        Se houver mídia, faz upload para o Meta e envia em sequência.
        Retorna lista de resultados (texto + mídia)."""
        resultados = []

        if mensagem:
            resultado = self.enviar_mensagem_texto(telefone, mensagem)
            resultados.append(resultado)

            if not resultado.get("success"):
                return resultados

        if caminho_midia:
            try:
                upload = self.upload_midia(caminho_midia)
                if upload.get("success"):
                    media_id = upload["media_id"]
                    resultado_midia = self.enviar_mensagem_midia(
                        telefone, media_id, caption=mensagem if not mensagem else None
                    )
                    resultados.append(resultado_midia)
                else:
                    resultados.append(
                        {"success": False, "error": "Falha no upload da mídia"}
                    )
            except Exception as e:
                resultados.append({"success": False, "error": f"Erro no upload: {e!s}"})

        return resultados

    def enviar_mensagem(self, telefone, mensagem):
        """Método mantido para compatibilidade com código existente"""
        return self.enviar_mensagem_texto(telefone, mensagem)

    def verificar_configuracao(self):
        """Verifica se a configuração está correta"""
        if not self.phone_number_id:
            return False, "WHATSAPP_PHONE_NUMBER_ID não configurado"
        if not self.access_token:
            return False, "WHATSAPP_ACCESS_TOKEN não configurado"

        try:
            url = f"{self.base_url}/{self.phone_number_id}"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return True, "Configuração OK"
        except Exception as e:
            return False, f"Erro na configuração: {e!s}"
