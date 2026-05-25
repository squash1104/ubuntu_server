import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import CharField, F, Q, Value
from django.http import JsonResponse
from django.shortcuts import redirect, render

from colaboradores.models import Colaborador, TipoColaborador
from convidados.models import Convidado
from geografia.models import Bairro, Cidade

from .models import (
    CampanhaMensagem,
    Mensagem,
    MensagemAniversario,
    StatusCampanha,
    StatusMensagem,
    TemplateMensagem,
    TipoMensagem,
)
from .services import MensagemService


@login_required
def enviar_mensagens_view(request):
    """View para exibir a interface de envio de mensagens"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            destinatarios = data.get("destinatarios", [])
            tipo_mensagem = data.get("tipo_mensagem")
            conteudo = data.get("conteudo")
            template_id = data.get("template_id")

            if not destinatarios or not tipo_mensagem or not conteudo:
                return JsonResponse(
                    {"success": False, "error": "Dados incompletos"}, status=400
                )

            # Processar envio das mensagens
            service = MensagemService()
            resultados = []

            for destinatario in destinatarios:
                try:
                    resultado = service.enviar_mensagem(
                        destinatario_nome=destinatario["nome"],
                        destinatario_telefone=destinatario["telefone"],
                        destinatario_tipo=destinatario["tipo"],
                        destinatario_id=destinatario["id"],
                        tipo_mensagem=tipo_mensagem,
                        conteudo=conteudo,
                        template_usado=template_id,
                        enviado_por=request.user,
                    )
                    resultados.append(resultado)
                except Exception as e:
                    resultados.append(
                        {
                            "success": False,
                            "error": str(e),
                            "destinatario": destinatario["nome"],
                        }
                    )

            return JsonResponse(
                {
                    "success": True,
                    "resultados": resultados,
                    "total_enviadas": len([r for r in resultados if r.get("success")]),
                }
            )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    # GET - exibir formulário
    templates = TemplateMensagem.objects.filter(ativo=True).order_by("nome")
    context = {"templates": templates, "tipos_mensagem": TipoMensagem.choices}
    return render(request, "mensagens/enviar_mensagens.html", context)


@login_required
def get_templates_view(request):
    """API para buscar templates por tipo de mensagem"""
    tipo = request.GET.get("tipo")
    if not tipo:
        return JsonResponse({"error": "Tipo de mensagem não especificado"}, status=400)

    templates = TemplateMensagem.objects.filter(tipo_mensagem=tipo, ativo=True).values(
        "id", "nome", "conteudo"
    )

    return JsonResponse({"templates": list(templates)})


@login_required
def historico_mensagens_view(request):
    """View para exibir histórico de mensagens enviadas"""
    mensagens = MensagemAniversario.objects.select_related("enviado_por").order_by(
        "-data_envio"
    )

    # Filtros
    tipo_filtro = request.GET.get("tipo")
    status_filtro = request.GET.get("status")

    if tipo_filtro:
        mensagens = mensagens.filter(tipo_mensagem=tipo_filtro)
    if status_filtro:
        mensagens = mensagens.filter(status=status_filtro)

    context = {
        "mensagens": mensagens,
        "tipos_mensagem": TipoMensagem.choices,
        "status_mensagem": StatusMensagem.choices,
        "tipo_filtro": tipo_filtro,
        "status_filtro": status_filtro,
    }
    return render(request, "mensagens/historico_mensagens.html", context)


@login_required
def gerenciar_templates_view(request):
    """View para gerenciar templates de mensagem"""
    if request.method == "POST":
        nome = request.POST.get("nome")
        tipo_mensagem = request.POST.get("tipo_mensagem")
        conteudo = request.POST.get("conteudo")

        if nome and tipo_mensagem and conteudo:
            TemplateMensagem.objects.create(
                nome=nome,
                tipo_mensagem=tipo_mensagem,
                conteudo=conteudo,
                criado_por=request.user,
            )
            messages.success(request, "Template criado com sucesso!")
        else:
            messages.error(request, "Todos os campos são obrigatórios!")

        return redirect("gerenciar_templates")

    templates = TemplateMensagem.objects.filter(ativo=True).order_by("nome")
    context = {"templates": templates, "tipos_mensagem": TipoMensagem.choices}
    return render(request, "mensagens/gerenciar_templates.html", context)


@login_required
def painel_mensagens_view(request):
    """View principal da seção Mensagens com filtros avançados"""
    tipo = request.GET.get("tipo", "todos")
    grupo_id = request.GET.get("grupo")
    cidade_id = request.GET.get("cidade")
    bairro_id = request.GET.get("bairro")

    colaboradores = Colaborador.objects.select_related("cidade", "bairro", "tipo")
    convidados = Convidado.objects.select_related("cidade", "bairro", "colaborador")

    # Aplicar filtros
    if grupo_id:
        colaboradores = colaboradores.filter(tipo_id=grupo_id)
    if cidade_id:
        colaboradores = colaboradores.filter(cidade_id=cidade_id)
        convidados = convidados.filter(cidade_id=cidade_id)
    if bairro_id:
        colaboradores = colaboradores.filter(bairro_id=bairro_id)
        convidados = convidados.filter(bairro_id=bairro_id)

    # Filtrar apenas com telefone
    colaboradores = colaboradores.exclude(
        Q(telefone__isnull=True) | Q(telefone__exact="")
    )
    convidados = convidados.exclude(Q(telefone__isnull=True) | Q(telefone__exact=""))

    def serialize_colabs(qs):
        return list(
            qs.annotate(
                tipo_registro=Value("colaborador", output_field=CharField()),
                colaborador_nome=Value("", output_field=CharField()),
            )
            .values(
                "id",
                "nome",
                "telefone",
                "cidade__nome_cidade",
                "bairro__nome_bairro",
                "tipo__nome",
                "tipo_registro",
                "colaborador_nome",
            )
            .order_by("nome")
        )

    def serialize_convs(qs):
        return list(
            qs.annotate(
                tipo_registro=Value("convidado", output_field=CharField()),
                colaborador_nome=F("colaborador__nome"),
                tipo__nome=Value("", output_field=CharField()),
            )
            .values(
                "id",
                "nome",
                "telefone",
                "cidade__nome_cidade",
                "bairro__nome_bairro",
                "tipo__nome",
                "tipo_registro",
                "colaborador_nome",
            )
            .order_by("nome")
        )

    contatos = []
    if tipo in ("todos", "colaboradores"):
        contatos += serialize_colabs(colaboradores)
    if tipo in ("todos", "convidados"):
        contatos += serialize_convs(convidados)

    # Remover duplicatas por telefone quando tipo=todos
    if tipo == "todos":
        vistos = set()
        contatos_unicos = []
        for c in contatos:
            tel = c.get("telefone", "")
            if tel and tel not in vistos:
                vistos.add(tel)
                contatos_unicos.append(c)
            elif not tel:
                contatos_unicos.append(c)
        contatos = contatos_unicos

    context = {
        "contatos": contatos,
        "total_contatos": len(contatos),
        "tipos_colaborador": TipoColaborador.objects.filter(ativo=True).order_by(
            "nome"
        ),
        "cidades": Cidade.objects.all().order_by("nome_cidade"),
        "bairros": Bairro.objects.select_related("cidade")
        .all()
        .order_by("nome_bairro"),
        "tipo": tipo,
        "grupo_id": int(grupo_id) if grupo_id and grupo_id.isdigit() else None,
        "cidade_id": int(cidade_id) if cidade_id and cidade_id.isdigit() else None,
        "bairro_id": int(bairro_id) if bairro_id and bairro_id.isdigit() else None,
        "tipos_mensagem": TipoMensagem.choices,
        "templates": TemplateMensagem.objects.filter(ativo=True).order_by("nome"),
    }
    return render(request, "mensagens/painel_mensagens.html", context)


@login_required
def enviar_mensagens_massa_view(request):
    """View para enviar mensagens em massa apenas para contatos selecionados"""
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "Método não permitido"}, status=405
        )

    try:
        data = json.loads(request.body)
        destinatarios = data.get("destinatarios", [])
        tipo_mensagem = data.get("tipo_mensagem")
        conteudo = data.get("conteudo")
        template_id = data.get("template_id")
        titulo_campanha = data.get("titulo_campanha", "Disparo em Massa")
        imagem_url = data.get("imagem_url", "")

        if not destinatarios or not tipo_mensagem or not conteudo:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Destinatários, tipo e conteúdo são obrigatórios",
                },
                status=400,
            )

        campanha = CampanhaMensagem.objects.create(
            titulo=titulo_campanha,
            filtros_usados={"total_selecionados": len(destinatarios)},
            tipo_mensagem=tipo_mensagem,
            conteudo=conteudo,
            template_usado=template_id,
            total_destinatarios=len(destinatarios),
            status=StatusCampanha.ENVIANDO,
            criado_por=request.user,
        )

        service = MensagemService()
        enviadas = 0
        falhas = 0

        for dest in destinatarios:
            try:
                resultado = service.enviar_mensagem_generico(
                    destinatario_nome=dest["nome"],
                    destinatario_telefone=dest["telefone"],
                    destinatario_tipo=dest["tipo"],
                    destinatario_id=dest["id"],
                    tipo_mensagem=tipo_mensagem,
                    conteudo=conteudo,
                    template_usado=template_id,
                    enviado_por=request.user,
                    campanha=campanha,
                    media_url=imagem_url,
                )
                if resultado.get("success"):
                    enviadas += 1
                else:
                    falhas += 1
            except Exception:
                falhas += 1

        campanha.total_enviadas = enviadas
        campanha.total_falhas = falhas
        if falhas == 0:
            campanha.status = StatusCampanha.CONCLUIDO
        elif enviadas > 0:
            campanha.status = StatusCampanha.PARCIAL
        else:
            campanha.status = StatusCampanha.CONCLUIDO
        campanha.save()

        return JsonResponse(
            {
                "success": True,
                "campanha_id": campanha.id,
                "total_destinatarios": len(destinatarios),
                "total_enviadas": enviadas,
                "total_falhas": falhas,
            }
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def salvar_template_rapido_view(request):
    """API para salvar template diretamente do modal de envio"""
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "Método não permitido"}, status=405
        )

    try:
        data = json.loads(request.body)
        nome = data.get("nome", "").strip()
        tipo_mensagem = data.get("tipo_mensagem")
        conteudo = data.get("conteudo", "").strip()

        if not nome or not tipo_mensagem or not conteudo:
            return JsonResponse(
                {"success": False, "error": "Nome, tipo e conteúdo são obrigatórios"},
                status=400,
            )

        template = TemplateMensagem.objects.create(
            nome=nome,
            tipo_mensagem=tipo_mensagem,
            conteudo=conteudo,
            criado_por=request.user,
        )

        return JsonResponse(
            {
                "success": True,
                "template": {
                    "id": template.id,
                    "nome": template.nome,
                    "conteudo": template.conteudo,
                },
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def upload_imagem_view(request):
    """Upload de imagem para anexar em mensagens WhatsApp"""
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "Método não permitido"}, status=405
        )

    if "imagem" not in request.FILES:
        return JsonResponse(
            {"success": False, "error": "Nenhuma imagem enviada"}, status=400
        )

    try:
        arquivo = request.FILES["imagem"]
        extensao = arquivo.name.split(".")[-1].lower()
        if extensao not in ("jpg", "jpeg", "png", "gif", "webp"):
            return JsonResponse(
                {"success": False, "error": "Formato de imagem não suportado"},
                status=400,
            )

        import uuid

        from django.core.files.storage import default_storage

        nome_arquivo = f"mensagens/{uuid.uuid4()}.{extensao}"
        default_storage.save(nome_arquivo, arquivo)
        url = f"/mensagens/arquivo/{nome_arquivo}"

        return JsonResponse({"success": True, "url": url})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def servir_arquivo_mensagem_view(request, caminho):
    """Serve arquivos uploaded (imagens) para usuarios autenticados"""
    import os

    from django.conf import settings
    from django.http import FileResponse, HttpResponseNotFound

    caminho_completo = os.path.join(settings.MEDIA_ROOT, caminho)
    caminho_completo = os.path.normpath(caminho_completo)

    if not caminho_completo.startswith(os.path.normpath(settings.MEDIA_ROOT)):
        return HttpResponseNotFound()

    if not os.path.exists(caminho_completo):
        return HttpResponseNotFound()

    return FileResponse(open(caminho_completo, "rb"))


@login_required
def editar_template_view(request, template_id):
    """View para editar um template de mensagem"""
    try:
        template = TemplateMensagem.objects.get(id=template_id, ativo=True)
    except TemplateMensagem.DoesNotExist:
        messages.error(request, "Template não encontrado")
        return redirect("mensagens:gerenciar_templates")

    if request.method == "POST":
        nome = request.POST.get("nome")
        tipo_mensagem = request.POST.get("tipo_mensagem")
        conteudo = request.POST.get("conteudo")

        if nome and tipo_mensagem and conteudo:
            template.nome = nome
            template.tipo_mensagem = tipo_mensagem
            template.conteudo = conteudo
            template.save()
            messages.success(request, "Template atualizado com sucesso!")
        else:
            messages.error(request, "Todos os campos são obrigatórios!")

        return redirect("mensagens:gerenciar_templates")

    context = {
        "template": template,
        "tipos_mensagem": TipoMensagem.choices,
    }
    return render(request, "mensagens/editar_template.html", context)


@login_required
def excluir_template_view(request, template_id):
    """View para excluir (desativar) um template"""
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "Método não permitido"}, status=405
        )

    try:
        template = TemplateMensagem.objects.get(id=template_id, ativo=True)
        template.ativo = False
        template.save()
        return JsonResponse({"success": True})
    except TemplateMensagem.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Template não encontrado"}, status=404
        )


@login_required
def campanhas_list_view(request):
    """View para listar campanhas de mensagens"""
    campanhas = CampanhaMensagem.objects.select_related("criado_por").all()

    context = {
        "campanhas": campanhas,
    }
    return render(request, "mensagens/campanhas_list.html", context)


@login_required
def campanha_detail_view(request, campanha_id):
    """View para detalhes de uma campanha"""
    try:
        campanha = CampanhaMensagem.objects.get(id=campanha_id)
    except CampanhaMensagem.DoesNotExist:
        messages.error(request, "Campanha não encontrada")
        return redirect("mensagens:campanhas_list")

    mensagens = Mensagem.objects.filter(campanha=campanha).order_by("-data_envio")

    context = {
        "campanha": campanha,
        "mensagens": mensagens,
    }
    return render(request, "mensagens/campanha_detail.html", context)
