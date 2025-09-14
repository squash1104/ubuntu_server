from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from convidados.models import Convidado
from geografia.models import Bairro

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
    termo_busca = request.GET.get("q", "")
    ordenar_por_param = request.GET.get("ordenar_por", "nome")
    direcao = request.GET.get("direcao", "asc")

    ordenar_por_query = ordenar_por_param
    if direcao == "desc":
        ordenar_por_query = f"-{ordenar_por_param}"

    colaboradores_qs = Colaborador.objects.select_related("cidade", "bairro")

    if termo_busca:
        colaboradores_qs = colaboradores_qs.filter(
            Q(nome__icontains=termo_busca)
            | Q(telefone__icontains=termo_busca)
            | Q(cidade__nome_cidade__icontains=termo_busca)
            | Q(bairro__nome_bairro__icontains=termo_busca)
        )

    colaboradores_final = colaboradores_qs.annotate(
        num_convidados=Count("convidados", distinct=True)
    ).order_by(ordenar_por_query)

    total_colaboradores_filtrados = colaboradores_final.count()
    soma_convidados = colaboradores_final.aggregate(total=Sum("num_convidados"))
    total_convidados_filtrados = soma_convidados["total"] or 0

    context = {
        "colaboradores": colaboradores_final,
        "termo_busca": termo_busca,
        "ordenar_por": ordenar_por_param,
        "direcao": direcao,
        "total_colaboradores_filtrados": total_colaboradores_filtrados,
        "total_convidados_filtrados": total_convidados_filtrados,
    }

    # 7. Responde de forma inteligente (AJAX ou requisição normal)
    if request.GET.get("is_ajax") == "true":
        # Se for AJAX, retorna APENAS o fragmento da tabela
        return render(
            request, "colaboradores/colaboradores_table_fragment.html", context
        )
    # Se for uma requisição normal, retorna a página completa
    return render(request, "colaboradores/lista_colaboradores.html", context)


@login_required
def adicionar_colaborador(request):
    if request.method == "POST":
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            colaborador = form.save(commit=False)
            colaborador.cadastrado_por = request.user
            colaborador.save()

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

    if request.method == "POST":
        form = ColaboradorForm(request.POST, instance=colaborador)
        if form.is_valid():
            form.save()
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
            "data_cadastro",
        ]  # Colunas padrão

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
        queryset = Colaborador.objects.filter(telefone=telefone)
        if colaborador_id:
            queryset = queryset.exclude(pk=colaborador_id)

        exists = queryset.exists()
        return JsonResponse({"exists": exists})
    return JsonResponse({"exists": False})


@require_http_methods(["GET"])
def check_nome_exists(request):
    nome = request.GET.get("nome", None)
    colaborador_id = request.GET.get("pk", None)

    if nome:
        queryset = Colaborador.objects.filter(nome__iexact=nome)
        if colaborador_id:
            queryset = queryset.exclude(pk=colaborador_id)

        exists = queryset.exists()
        return JsonResponse({"exists": exists})
    return JsonResponse({"exists": False})
