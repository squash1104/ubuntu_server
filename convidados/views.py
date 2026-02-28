import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from colaboradores.models import Colaborador
from geografia.models import Bairro
from historico.utils import (
    registrar_criacao_convidado,
    registrar_edicao_convidado,
    registrar_exclusao_convidado,
)

from .filters import ConvidadoFilter
from .forms import ConvidadoForm
from .models import Convidado
from .utils import (
    exportar_convidados_excel,
    exportar_convidados_pdf,
    imprimir_relatorio,
)


@login_required
def lista_convidados(request):
    termo_busca = request.GET.get("q", "")
    ordenar_por_param = request.GET.get("ordenar_por", "nome")
    direcao = request.GET.get("direcao", "asc")
    per_page = int(request.GET.get("per_page", 20))
    page_number = request.GET.get("page", 1)

    # Opções de registros por página
    per_page_options = [20, 50, 100, 200]

    ordenar_por_query = ordenar_por_param
    if direcao == "desc":
        ordenar_por_query = f"-{ordenar_por_param}"

    convidados_qs = Convidado.objects.select_related("colaborador", "cidade", "bairro")

    if termo_busca:
        convidados_qs = convidados_qs.filter(
            Q(nome__icontains=termo_busca)
            | Q(telefone__icontains=termo_busca)
            | Q(cidade__nome_cidade__icontains=termo_busca)
            | Q(bairro__nome_bairro__icontains=termo_busca)
            | Q(colaborador__nome__icontains=termo_busca)
        )

    convidados_final = convidados_qs.order_by(ordenar_por_query)

    # Implementar paginação
    paginator = Paginator(convidados_final, per_page)
    page_obj = paginator.get_page(page_number)

    # Totais apenas da página atual
    total_convidados_filtrados = page_obj.object_list.count()

    context = {
        "convidados": page_obj,
        "page_obj": page_obj,
        "paginator": paginator,
        "termo_busca": termo_busca,
        "ordenar_por": ordenar_por_param,
        "direcao": direcao,
        "per_page": per_page,
        "per_page_options": per_page_options,
        "total_convidados_filtrados": total_convidados_filtrados,
    }

    return render(request, "convidados/lista_convidados.html", context)


@login_required
def colaborador_convidados(request, pk):
    colaborador = get_object_or_404(Colaborador, pk=pk)
    convidados_do_colaborador = Convidado.objects.filter(colaborador=colaborador)
    total_convidados = convidados_do_colaborador.count()

    # --- Lógica de Ordenação (similar à lista geral de convidados) ---
    ordenar_por = request.GET.get("ordenar_por", "nome")  # Padrão: ordenar por nome
    direcao = request.GET.get("direcao", "asc")  # Padrão: ascendente

    # Mapeia os nomes das colunas do template para os nomes dos campos do modelo
    campos_ordenaveis = {
        "nome": "nome",
        "telefone": "telefone",
        "cidade": "cidade",
        "bairro": "bairro",
        "colaborador": "colaborador",
    }

    # Verifica se o campo de ordenação é válido e aplica a ordenação
    if ordenar_por in campos_ordenaveis:
        prefixo = "-" if direcao == "desc" else ""
        convidados_do_colaborador = convidados_do_colaborador.order_by(
            f"{prefixo}{campos_ordenaveis[ordenar_por]}"
        )
    # --- Fim da Lógica de Ordenação ---

    meta = 20
    meta_status = ""
    porcentagem_meta = 0

    if meta > 0:
        porcentagem_meta = (total_convidados / meta) * 100

    if total_convidados == meta:
        meta_status = "sucesso"
    elif total_convidados < meta:
        meta_status = "andamento"
    elif total_convidados > meta:
        meta_status = "superada"

    context = {
        "colaborador": colaborador,
        "convidados": convidados_do_colaborador,
        "total_convidados": convidados_do_colaborador.count(),
        "ordenar_por": ordenar_por,  # Passa o campo de ordenação atual para o template
        "direcao": direcao,  # Passa a direção de ordenação atual para o template
        "meta": meta,
        "meta_status": meta_status,
        "porcentagem_meta": porcentagem_meta,
    }
    return render(request, "convidados/colaborador_convidados.html", context)


@login_required
def cadastrar_convidado(request, colaborador_id=None):
    colaborador = None
    if colaborador_id:
        colaborador = get_object_or_404(Colaborador, pk=colaborador_id)

    if request.method == "POST":
        form = ConvidadoForm(request.POST)
        if form.is_valid():
            try:
                convidado = form.save(commit=False)
                # Garantir vínculo com colaborador para refletir no ranking
                if colaborador and not getattr(convidado, "colaborador", None):
                    convidado.colaborador = colaborador
                # Registrar quem cadastrou o convidado
                if not getattr(convidado, "cadastrado_por", None):
                    convidado.cadastrado_por = request.user
                convidado.save()

                # REGISTRAR NO HISTÓRICO
                registrar_criacao_convidado(convidado, request.user, request)

                convidado_nome = convidado.nome

                # Verificar avisos de telefone duplicado
                if getattr(form, "phone_is_duplicate", False):
                    if hasattr(form, "duplicate_phone_convidado"):
                        messages.warning(
                            request,
                            f'AVISO: O telefone "{convidado.telefone}" já está '
                            f"cadastrado no convidado "
                            f'"{form.duplicate_phone_convidado}". '
                            f'Convidado "{convidado_nome}" salvo com sucesso!',
                        )
                    elif hasattr(form, "duplicate_phone_colaborador"):
                        messages.warning(
                            request,
                            f'AVISO: O telefone "{convidado.telefone}" já está '
                            f"cadastrado no colaborador "
                            f'"{form.duplicate_phone_colaborador}". '
                            f'Convidado "{convidado_nome}" salvo com sucesso!',
                        )
                else:
                    messages.success(
                        request, f'Convidado "{convidado_nome}" salvo com sucesso!'
                    )

                # Verificar qual botão foi clicado
                if "salvar_e_adicionar" in request.POST:
                    # Manter na mesma página com formulário limpo
                    if colaborador:
                        form = ConvidadoForm(initial={"colaborador": colaborador})
                    else:
                        form = ConvidadoForm()
                    messages.info(
                        request,
                        "Convidado salvo! Preencha os dados do próximo convidado.",
                    )
                    context = {
                        "form": form,
                        "colaborador": colaborador,
                        "colaborador_id": colaborador_id,
                    }
                    return render(
                        request, "convidados/cadastrar_convidado.html", context
                    )
                if "salvar_e_fechar" in request.POST:
                    # Redirecionar para a página do colaborador
                    if colaborador:
                        return redirect(
                            "convidados:colaborador_convidados", pk=colaborador_id
                        )
                    return redirect("convidados:lista_convidados")
                # Comportamento padrão (redirecionar)
                if colaborador:
                    return redirect(
                        "convidados:colaborador_convidados", pk=colaborador_id
                    )
                return redirect("convidados:lista_convidados")

            except Exception as e:
                messages.error(
                    request,
                    f"Erro ao salvar convidado: {e!s}. "
                    "Verifique se todos os campos obrigatórios foram preenchidos.",
                )
    else:
        if colaborador:
            form = ConvidadoForm(initial={"colaborador": colaborador})
        else:
            form = ConvidadoForm()

    context = {
        "form": form,
        "colaborador": colaborador,
        "colaborador_id": colaborador_id,
    }
    return render(request, "convidados/cadastrar_convidado.html", context)


@login_required
def editar_convidado(request, pk):
    convidado = get_object_or_404(Convidado, pk=pk)

    # SALVAR DADOS ANTES DA EDIÇÃO
    dados_antes = {
        "nome": convidado.nome,
        "telefone": convidado.telefone,
        "data_nascimento": getattr(convidado, "data_nascimento", None),
        "cidade": (
            str(getattr(convidado, "cidade", None))
            if getattr(convidado, "cidade", None)
            else None
        ),
        "bairro": str(convidado.bairro) if convidado.bairro else None,
        "colaborador": str(convidado.colaborador) if convidado.colaborador else None,
    }

    if request.method == "POST":
        form = ConvidadoForm(request.POST, instance=convidado)
        if form.is_valid():
            form.save()

            # REGISTRAR NO HISTÓRICO
            registrar_edicao_convidado(convidado, request.user, dados_antes, request)

            messages.success(
                request, f'Convidado "{convidado.nome}" atualizado com sucesso!'
            )

            # --- MODIFICAÇÃO PRINCIPAL AQUI ---
            # Pega a URL de retorno do formulário, se ela existir.
            next_url = request.POST.get("next", None)
            if next_url:
                # Redireciona para a URL completa fornecida pelo formulário
                return redirect(next_url)
            # Se não houver, volta para a lista geral como fallback
            return redirect("convidados:lista_convidados")
            # ----------------------------------
    else:
        form = ConvidadoForm(instance=convidado)

    # Adiciona a URL de retorno para o contexto, se ela existir
    next_url_get = request.GET.get("next", None)
    return render(
        request,
        "convidados/editar_convidado.html",
        {"form": form, "convidado": convidado, "next": next_url_get},
    )


@login_required
def excluir_convidado(request, pk):
    convidado = get_object_or_404(Convidado, pk=pk)

    if request.method == "POST":
        # Pega a URL de redirecionamento que o formulário enviou
        redirect_url = request.POST.get("redirect_url", None)

        # REGISTRAR NO HISTÓRICO ANTES DE EXCLUIR
        registrar_exclusao_convidado(convidado, request.user, request)

        # Guarda o nome do convidado antes de o apagar
        nome_convidado = convidado.nome

        # Apaga o convidado do banco de dados
        convidado.delete()

        messages.success(request, f'Convidado "{nome_convidado}" excluído com sucesso!')

        # Se a URL de redirecionamento foi enviada, usa-a.
        # Caso contrário, usa uma URL padrão (fallback de segurança).
        if redirect_url:
            return redirect(redirect_url)
        return redirect("convidados:lista_convidados")

    # Se a requisição não for POST, simplesmente redireciona para a lista geral.
    return redirect("convidados:lista_convidados")


def relatorio_convidados_view(request):
    f = ConvidadoFilter(request.GET, queryset=Convidado.objects.all())

    selected_columns = request.GET.getlist("columns")

    # Definir colunas padrão: todas exceto data_cadastro
    if not selected_columns:
        selected_columns = ["nome", "telefone", "cidade", "bairro", "convidado_por"]

    # Verificar se é uma requisição de exportação (não paginar)
    is_export = "export_excel" in request.GET or "export_pdf" in request.GET or "export_print" in request.GET

    if not is_export:
        # Parâmetros de paginação
        per_page = request.GET.get("per_page", "20")
        valid_per_page_options = [20, 50, 100, 200]
        try:
            per_page = int(per_page)
            if per_page not in valid_per_page_options:
                per_page = 20
        except (ValueError, TypeError):
            per_page = 20

        # Paginação
        paginator = Paginator(f.qs, per_page)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        convidados_page = page_obj.object_list
    else:
        # Sem paginação para exportação
        per_page = 20
        page_obj = None
        convidados_page = f.qs

    if "export_excel" in request.GET:
        print("Colunas para Excel:", selected_columns)  # <-- Adicione esta linha
        return exportar_convidados_excel(f.qs, selected_columns)
    if "export_pdf" in request.GET:
        print("Colunas para PDF:", selected_columns)  # <-- Adicione esta linha
        return exportar_convidados_pdf(f.qs, selected_columns, f)
    if "export_print" in request.GET:
        print("Colunas para Impressão:", selected_columns)  # <-- Adicione esta linha
        return imprimir_relatorio(f.qs, selected_columns, f)

    context = {
        "filter": f,
        "convidados": convidados_page,
        "selected_columns": selected_columns,
        "page_obj": page_obj,
        "per_page": per_page,
        "per_page_options": [20, 50, 100, 200],
    }
    return render(request, "report/guest_report_form.html", context)


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
    convidado_id = request.GET.get("pk", None)

    if telefone:
        # Normalizar o telefone (substituir + por espaço)
        telefone_normalizado = telefone.replace("+", " ")

        # Função para normalizar telefone (remover formatação)
        def normalizar_telefone(tel):
            return re.sub(r"[\(\)\-\s]", "", tel)

        # Normalizar o telefone de entrada
        telefone_entrada_limpo = normalizar_telefone(telefone_normalizado)

        # Buscar todos os telefones de convidados e normalizar
        convidados_queryset = Convidado.objects.exclude(telefone__isnull=True).exclude(
            telefone=""
        )
        if convidado_id:
            convidados_queryset = convidados_queryset.exclude(pk=convidado_id)

        # Buscar todos os telefones de colaboradores e normalizar
        colaboradores_queryset = Colaborador.objects.exclude(
            telefone__isnull=True
        ).exclude(telefone="")

        # Verificar se o telefone normalizado existe
        nome_existente = None
        tipo_existente = None
        exists = False

        # Verificar em convidados
        for convidado in convidados_queryset:
            telefone_banco_limpo = normalizar_telefone(convidado.telefone)
            if telefone_entrada_limpo == telefone_banco_limpo:
                exists = True
                nome_existente = convidado.nome
                tipo_existente = "convidado"
                break

        # Se não encontrou em convidados, verificar em colaboradores
        if not exists:
            for colaborador in colaboradores_queryset:
                telefone_banco_limpo = normalizar_telefone(colaborador.telefone)
                if telefone_entrada_limpo == telefone_banco_limpo:
                    exists = True
                    nome_existente = colaborador.nome
                    tipo_existente = "colaborador"
                    break

        return JsonResponse(
            {
                "exists": exists,
                "nome_existente": nome_existente,
                "tipo_existente": tipo_existente,
            }
        )
    return JsonResponse({"exists": False, "nome_existente": None})


@require_http_methods(["GET"])
def check_nome_exists(request):
    nome = request.GET.get("nome", None)
    convidado_id = request.GET.get("pk", None)

    if nome:
        # Checa se o nome existe em convidados
        convidados_queryset = Convidado.objects.filter(nome__iexact=nome)
        if convidado_id:
            convidados_queryset = convidados_queryset.exclude(pk=convidado_id)

        # Checa se o nome existe em colaboradores
        colaboradores_queryset = Colaborador.objects.filter(nome__iexact=nome)

        exists = convidados_queryset.exists() or colaboradores_queryset.exists()

        # Determinar onde o nome existe
        tipo_existente = None
        if convidados_queryset.exists():
            tipo_existente = "convidados"
        elif colaboradores_queryset.exists():
            tipo_existente = "colaboradores"

        return JsonResponse({"exists": exists, "tipo_existente": tipo_existente})
    return JsonResponse({"exists": False, "tipo_existente": None})
