import os

from django.conf import settings
from django.utils import timezone

from .models import Mensagem, MensagemAniversario, StatusMensagem


class MensagemService:
    """Serviço para envio de mensagens via WhatsApp Cloud API (Meta)"""

    def __init__(self):
        self.debug_mode = settings.DEBUG

    def _media_url_para_caminho(self, media_url):
        """Converte URL de mídia (/mensagens/arquivo/...) para caminho absoluto no disco"""
        if not media_url:
            return None
        if media_url.startswith("/mensagens/arquivo/"):
            relative_path = media_url.replace("/mensagens/arquivo/", "", 1)
            return os.path.normpath(os.path.join(settings.MEDIA_ROOT, relative_path))
        return None

    def _upload_media_para_meta(self, api, media_url):
        """Faz upload de mídia para o Meta e retorna o media_id e tipo"""
        caminho = self._media_url_para_caminho(media_url)
        if not caminho or not os.path.exists(caminho):
            return None, None
        resultado = api.upload_midia(caminho)
        if not resultado.get("success"):
            return None, None

        ext = os.path.splitext(caminho)[1].lower()
        tipo_map = {
            ".jpg": "image", ".jpeg": "image", ".png": "image",
            ".mp4": "video", ".3gp": "video",
            ".pdf": "document",
            ".mp3": "audio", ".ogg": "audio", ".amr": "audio",
        }
        header_type = tipo_map.get(ext, "image")
        return resultado["media_id"], header_type

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

    def _enviar_template_via_whatsapp_cloud(
        self, telefone, template_name, language_code="pt_BR", media_url=None
    ):
        """Envia template aprovado do Meta, com suporte a mídia opcional no header"""
        from .whatsapp_cloud_api import WhatsAppCloudAPI

        api = WhatsAppCloudAPI()
        header_media_id = None
        header_type = "image"

        if media_url:
            header_media_id, header_type = self._upload_media_para_meta(api, media_url)

        resultado = api.enviar_template(
            telefone=telefone,
            template_name=template_name,
            language_code=language_code,
            header_media_id=header_media_id,
            header_type=header_type,
        )

        if resultado.get("success"):
            return resultado
        raise Exception(resultado.get("error", "Falha ao enviar template via WhatsApp Cloud API"))

    def _send_message(
        self, telefone, conteudo, tipo_mensagem, media_url,
        meta_template_name=None, meta_template_language="pt_BR",
        debug_info=None,
    ):
        """Decide entre enviar template Meta ou texto livre"""
        if self.debug_mode:
            return None

        if meta_template_name and tipo_mensagem == "whatsapp":
            return self._enviar_template_via_whatsapp_cloud(
                telefone, meta_template_name, meta_template_language, media_url=media_url
            )

        if tipo_mensagem == "whatsapp":
            return self._enviar_via_whatsapp_cloud(telefone, conteudo, media_url=media_url)

        if tipo_mensagem == "sms":
            raise ValueError("SMS não implementado no momento")

        raise ValueError(f"Tipo de mensagem não suportado: {tipo_mensagem}")

    def _make_debug_result(self, mensagem, media_url=None):
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

    def _handle_failure(self, mensagem, e):
        mensagem.status = StatusMensagem.FALHOU
        mensagem.data_processamento = timezone.now()
        mensagem.erro_detalhes = str(e)
        mensagem.save()
        return {"success": False, "error": str(e), "message_id": mensagem.id}

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
        media_url=None,
        meta_template_name=None,
        meta_template_language="pt_BR",
    ):
        """Envia uma mensagem para um destinatário"""
        conteudo_processado = self.processar_template(conteudo, destinatario_nome)

        if media_url:
            conteudo_processado = conteudo_processado.replace("[📷 Imagem anexada]", "").strip()

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
            if self.debug_mode:
                print(f"🔧 MODO DEBUG - Simulando envio de {tipo_mensagem.upper()}")
                print(f"   Para: {destinatario_nome} ({destinatario_telefone})")
                print(f"   Conteúdo: {conteudo}")
                if media_url:
                    print(f"   Mídia: {media_url}")
                print(f"   {'='*50}")
                return self._make_debug_result(mensagem, media_url)

            resultado = self._send_message(
                destinatario_telefone, conteudo_processado, tipo_mensagem, media_url,
                meta_template_name=meta_template_name,
                meta_template_language=meta_template_language,
            )

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
            return self._handle_failure(mensagem, e)

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
        meta_template_name=None,
        meta_template_language="pt_BR",
    ):
        """Envia uma mensagem usando o modelo Mensagem (genérico)"""

        conteudo_processado = self.processar_template(conteudo, destinatario_nome)

        if media_url:
            conteudo_processado = conteudo_processado.replace("[📷 Imagem anexada]", "").strip()

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
            if self.debug_mode:
                print(f"🔧 MODO DEBUG - Simulando envio de {tipo_mensagem.upper()}")
                print(f"   Para: {destinatario_nome} ({destinatario_telefone})")
                print(f"   Conteúdo: {conteudo}")
                if media_url:
                    print(f"   Mídia: {media_url}")
                print(f"   {'='*50}")
                return self._make_debug_result(mensagem, media_url)

            resultado = self._send_message(
                destinatario_telefone, conteudo_processado, tipo_mensagem, media_url,
                meta_template_name=meta_template_name,
                meta_template_language=meta_template_language,
            )

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
            return self._handle_failure(mensagem, e)

    def processar_template(self, template_conteudo, nome, idade=None):
        """Processa um template substituindo variáveis"""
        conteudo = template_conteudo.replace("{nome}", nome)
        if idade is not None:
            conteudo = conteudo.replace("{idade}", str(idade))
        return conteudo
