import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from convidados.models import Convidado
from geografia.models import Bairro
from historico.utils import (
    registrar_criacao_colaborador,
    registrar_edicao_colaborador,
    registrar_exclusao_colaborador,
)

from .filters import ColaboradorFilter
from .forms import ColaboradorForm
from .models import Colaborador
from .utils import (
    exportar_colaboradores_excel,
    exportar_colaboradores_pdf,
    imprimir_relatorio_colaboradores,
)


@login_required
def lista_colaboradores(request):
    # Parâmetros de busca e ordenação
    termo_busca = request.GET.get("q", "")
    ordenar_por_param = request.GET.get("ordenar_por", "nome")
    direcao = request.GET.get("direcao", "asc")
    per_page = request.GET.get("per_page", "20")
    regiao = request.GET.get("regiao", "todos")  # Filtro por região (capital/interior)
    tipo = request.GET.get("tipo", "todos")  # Filtro por tipo (colaborador/acs_ace)

    # Validar per_page
    valid_per_page_options = [20, 50, 100, 200]
    try:
        per_page = int(per_page)
        if per_page not in valid_per_page_options:
            per_page = 20
    except (ValueError, TypeError):
        per_page = 20

    # Ordenação
    ordenar_por_query = ordenar_por_param
    if direcao == "desc":
        ordenar_por_query = f"-{ordenar_por_param}"

    # Query base
    colaboradores_qs = Colaborador.objects.select_related("cidade", "bairro")

    # Filtro por região (Capital/Interior)
    capitais = ["Cuiabá", "Várzea Grande"]
    if regiao == "capital":
        colaboradores_qs = colaboradores_qs.filter(cidade__nome_cidade__in=capitais)
    elif regiao == "interior":
        # Interior inclui demais cidades e registros sem cidade
        colaboradores_qs = colaboradores_qs.exclude(cidade__nome_cidade__in=capitais)

    # Filtro por tipo (Colaborador/ACS/ACE)
    if tipo == "colaborador":
        colaboradores_qs = colaboradores_qs.filter(tipo="colaborador")
    elif tipo == "acs_ace":
        colaboradores_qs = colaboradores_qs.filter(tipo="acs_ace")

    # Filtro de busca
    if termo_busca:
        colaboradores_qs = colaboradores_qs.filter(
            Q(nome__icontains=termo_busca)
            | Q(telefone__icontains=termo_busca)
            | Q(cidade__nome_cidade__icontains=termo_busca)
            | Q(bairro__nome_bairro__icontains=termo_busca)
        )

    # Aplicar ordenação
    colaboradores_final = colaboradores_qs.annotate(
        num_convidados=Count("convidados", distinct=True)
    ).order_by(ordenar_por_query)

    # Totais do conjunto filtrado (não apenas da página) e da página atual
    total_colaboradores_filtrados = colaboradores_final.count()
    soma_convidados_filtrados = colaboradores_final.aggregate(
        total=Sum("num_convidados")
    )
    total_convidados_filtrados = soma_convidados_filtrados["total"] or 0

    # Paginação
    paginator = Paginator(colaboradores_final, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Totais da página atual (após paginação)
    total_colaboradores_pagina = page_obj.object_list.count()
    soma_convidados_pagina = page_obj.object_list.aggregate(total=Sum("num_convidados"))
    total_convidados_pagina = soma_convidados_pagina["total"] or 0

    context = {
        "page_obj": page_obj,  # Usar page_obj (padrão Django)
        "paginator": paginator,  # Adicionar paginator também
        "termo_busca": termo_busca,
        "ordenar_por": ordenar_por_param,
        "direcao": direcao,
        "per_page": per_page,
        "per_page_options": valid_per_page_options,
        "regiao": regiao,
        "tipo": tipo,
        "total_colaboradores_filtrados": total_colaboradores_filtrados,
        "total_convidados_filtrados": total_convidados_filtrados,
        "total_colaboradores_pagina": total_colaboradores_pagina,
        "total_convidados_pagina": total_convidados_pagina,
    }

    return render(request, "colaboradores/lista_colaboradores.html", context)


@login_required
def adicionar_colaborador(request):
    if request.method == "POST":
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            colaborador = form.save(commit=False)
            colaborador.cadastrado_por = request.user
            colaborador.save()

            # REGISTRAR NO HISTÓRICO
            registrar_criacao_colaborador(colaborador, request.user, request)

            if form.has_phone_warning:
                messages.warning(
                    request,
                    f'AVISO: O telefone "{colaborador.telefone}" já está '
                    f"cadastrado em outro colaborador.",
                )

            colaborador_nome = colaborador.nome
            messages.success(
                request, f'Colaborador "{colaborador_nome}" cadastrado com sucesso!'
            )
            return redirect("colaboradores:lista_colaboradores")
    else:
        form = ColaboradorForm()
    return render(request, "colaboradores/adicionar_colaborador.html", {"form": form})


@login_required
def editar_colaborador(request, pk):
    colaborador = get_object_or_404(Colaborador, pk=pk)

    # SALVAR DADOS ANTES DA EDIÇÃO
    dados_antes = {
        "nome": colaborador.nome,
        "telefone": colaborador.telefone,
        "data_nascimento": getattr(colaborador, "data_nascimento", None),
        "cidade": (
            str(getattr(colaborador, "cidade", None))
            if getattr(colaborador, "cidade", None)
            else None
        ),
        "bairro": (
            str(getattr(colaborador, "bairro", None))
            if getattr(colaborador, "bairro", None)
            else None
        ),
        "cadastrado_por": getattr(
            getattr(colaborador, "cadastrado_por", None), "username", None
        ),
    }

    if request.method == "POST":
        form = ColaboradorForm(request.POST, instance=colaborador)
        if form.is_valid():
            form.save()

            # REGISTRAR NO HISTÓRICO
            registrar_edicao_colaborador(
                colaborador, request.user, dados_antes, request
            )

            messages.success(request, "Colaborador editado com sucesso!")
            return redirect("colaboradores:lista_colaboradores")
    else:
        form = ColaboradorForm(instance=colaborador)

    context = {
        "form": form,
        "colaborador": colaborador,
    }
    return render(request, "colaboradores/editar_colaborador.html", context)


@login_required  # Protege a view de exclusão
def excluir_colaborador(request, colaborador_id):
    colaborador = get_object_or_404(Colaborador, pk=colaborador_id)

    # Contagem de convidados associados
    quantidade_convidados = Convidado.objects.filter(colaborador=colaborador).count()

    if request.method == "POST":
        if quantidade_convidados == 0:
            # REGISTRAR NO HISTÓRICO ANTES DE EXCLUIR
            registrar_exclusao_colaborador(colaborador, request.user, request)

            # Se não há convidados, pode excluir
            colaborador.delete()
            messages.success(
                request, f'Colaborador "{colaborador.nome}" excluído com sucesso!'
            )
        else:
            # Se há convidados, impede a exclusão e adiciona uma mensagem de erro
            messages.error(
                request,
                f'Não foi possível excluir o colaborador "{colaborador.nome}" '
                f"porque ele possui {quantidade_convidados} convidados associados.",
            )
        return redirect("colaboradores:lista_colaboradores")

    # Para requisições GET (se você quiser uma página de confirmação de exclusão)
    # Por enquanto, vamos fazer a exclusão direto com POST para simplificar.
    # No entanto, é boa prática ter uma página de confirmação para exclusão.
    # Caso queira uma página de confirmação, remova o
    # `if request.method == 'POST':` e adicione um template.

    # Alternativa para GET: exibir uma mensagem de erro ou um
    # formulário de confirmação simples
    messages.error(
        request,
        "A exclusão deve ser feita via POST. Por favor, use o botão "
        '"Excluir" na lista.',
    )
    return redirect(
        "colaboradores:lista_colaboradores"
    )  # Redireciona de volta com a mensagem de erro


def relatorio_colaboradores_view(request):
    # Anota a contagem de convidados para cada colaborador
    queryset = Colaborador.objects.annotate(total_convidados=Count("convidados"))

    f = ColaboradorFilter(request.GET, queryset=queryset)

    selected_columns = request.GET.getlist("columns")
    if not selected_columns:
        selected_columns = [
            "nome",
            "telefone",
            "cidade",
            "bairro",
            "total_convidados",
            "tipo",
        ]  # Colunas padrão (exceto data_cadastro)

    if "export_excel" in request.GET:
        return exportar_colaboradores_excel(f.qs, selected_columns)
    if "export_pdf" in request.GET:
        return exportar_colaboradores_pdf(f.qs, selected_columns)
    if "export_print" in request.GET:
        return imprimir_relatorio_colaboradores(f.qs, selected_columns)

    context = {
        "filter": f,
        "colaboradores": f.qs,
        "selected_columns": selected_columns,
    }
    return render(request, "relatorios/relatorio_colaboradores_form.html", context)


def get_bairros_ajax(request):
    cidade_id = request.GET.get("cidade_id")
    bairros = []
    if cidade_id:
        bairros_qs = Bairro.objects.filter(cidade_id=cidade_id).order_by("nome_bairro")
        bairros = [
            {"id": bairro.id, "nome_bairro": bairro.nome_bairro}
            for bairro in bairros_qs
        ]
    return JsonResponse(bairros, safe=False)


@require_http_methods(["GET"])
def check_telefone_exists(request):
    telefone = request.GET.get("telefone", None)
    colaborador_id = request.GET.get("pk", None)

    if telefone:
        # Normalizar o telefone (substituir + por espaço)
        telefone_normalizado = telefone.replace("+", " ")

        # Função para normalizar telefone (remover formatação)
        def normalizar_telefone(tel):
            return re.sub(r"[\(\)\-\s]", "", tel)

        # Normalizar o telefone de entrada
        telefone_entrada_limpo = normalizar_telefone(telefone_normalizado)

        # Buscar todos os telefones de colaboradores e normalizar
        colaboradores_queryset = Colaborador.objects.exclude(
            telefone__isnull=True
        ).exclude(telefone="")
        if colaborador_id:
            colaboradores_queryset = colaboradores_queryset.exclude(pk=colaborador_id)

        # Buscar todos os telefones de convidados e normalizar
        from convidados.models import Convidado

        convidados_queryset = Convidado.objects.exclude(telefone__isnull=True).exclude(
            telefone=""
        )

        # Verificar se o telefone normalizado existe
        nome_existente = None
        tipo_existente = None
        exists = False

        # Verificar em colaboradores
        for colaborador in colaboradores_queryset:
            telefone_banco_limpo = normalizar_telefone(colaborador.telefone)
            if telefone_entrada_limpo == telefone_banco_limpo:
                exists = True
                nome_existente = colaborador.nome
                tipo_existente = "colaborador"
                break

        # Se não encontrou em colaboradores, verificar em convidados
        if not exists:
            for convidado in convidados_queryset:
                telefone_banco_limpo = normalizar_telefone(convidado.telefone)
                if telefone_entrada_limpo == telefone_banco_limpo:
                    exists = True
                    nome_existente = convidado.nome
                    tipo_existente = "convidado"
                    break

        return JsonResponse(
            {
                "exists": exists,
                "nome_existente": nome_existente,
                "tipo_existente": tipo_existente,
            }
        )
    return JsonResponse(
        {"exists": False, "nome_existente": None, "tipo_existente": None}
    )


@require_http_methods(["GET"])
def check_nome_exists(request):
    nome = request.GET.get("nome", None)
    colaborador_id = request.GET.get("pk", None)

    if nome:
        # Checa se o nome existe em colaboradores
        colaboradores_queryset = Colaborador.objects.filter(nome__iexact=nome)
        if colaborador_id:
            colaboradores_queryset = colaboradores_queryset.exclude(pk=colaborador_id)

        # Checa se o nome existe em convidados
        from convidados.models import Convidado

        convidados_queryset = Convidado.objects.filter(nome__iexact=nome)

        exists = colaboradores_queryset.exists() or convidados_queryset.exists()

        # Determinar onde o nome existe
        tipo_existente = None
        if colaboradores_queryset.exists():
            tipo_existente = "colaboradores"
        elif convidados_queryset.exists():
            tipo_existente = "convidados"

        return JsonResponse({"exists": exists, "tipo_existente": tipo_existente})
    return JsonResponse({"exists": False, "tipo_existente": None})
