from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from colaboradores.models import Colaborador
from geografia.models import Bairro

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
    total_convidados_filtrados = convidados_final.count()

    context = {
        "convidados": convidados_final,
        "termo_busca": termo_busca,
        "ordenar_por": ordenar_por_param,
        "direcao": direcao,
        "total_convidados_filtrados": total_convidados_filtrados,
    }

    if request.GET.get("is_ajax") == "true":
        return render(request, "convidados/convidados_table_fragment.html", context)
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

    meta = 15
    meta_status = ""
    porcentagem_meta = 0

    if meta > 0:
        porcentagem_meta = (total_convidados / meta) * 100

    if total_convidados == meta:
        meta_status = "sucesso"
    elif total_convidados <= 14:
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
def cadastrar_convidado(
    request, colaborador_id=None
):  # <--- Garanta que aceita colaborador_id=None
    colaborador = None
    if colaborador_id:
        colaborador = get_object_or_404(Colaborador, pk=colaborador_id)

    if request.method == "POST":
        form = ConvidadoForm(request.POST)
        if form.is_valid():
            convidado = form.save()
            messages.success(
                request, f'Convidado "{convidado.nome}" cadastrado com sucesso!'
            )
            if colaborador:
                form = ConvidadoForm(initial={"colaborador": colaborador})

                context = {
                    "form": form,
                    "colaborador": colaborador,
                }
                return render(request, "convidados/cadastrar_convidado.html", context)
            # Caso contrário, volta para a lista geral
            return redirect("convidados:lista_convidados")
    else:
        # Se for o primeiro acesso (GET) e viemos de um colaborador,
        # já preenche o campo 'colaborador' no formulário
        if colaborador:
            form = ConvidadoForm(initial={"colaborador": colaborador})
        else:
            form = ConvidadoForm()

    context = {
        "form": form,
        # Envia o colaborador (ou None) para o template saber de onde viemos
        "colaborador": colaborador,
    }
    return render(request, "convidados/cadastrar_convidado.html", context)


@login_required
def editar_convidado(request, pk):
    convidado = get_object_or_404(Convidado, pk=pk)
    colaborador_origem_id = request.GET.get("colaborador_origem_id")

    if request.method == "POST":
        form = ConvidadoForm(request.POST, instance=convidado)
        if form.is_valid():
            form.save()
            messages.warning(
                request, f'Convidado "{convidado.nome}" editado com sucesso!'
            )
            if colaborador_origem_id:
                return redirect(
                    "convidados:colaborador_convidados", pk=colaborador_origem_id
                )
            return redirect("convidados:lista_convidados")
    else:
        form = ConvidadoForm(instance=convidado)

    # **THE CORRECTION IS HERE**
    # This `context` and `return render` block must be outside the `else` block
    # so that it is executed for both GET and invalid POST requests.
    context = {
        "form": form,
        "convidado": convidado,
    }
    return render(request, "convidados/editar_convidado.html", context)


@login_required
def excluir_convidado(request, pk):
    convidado = get_object_or_404(Convidado, pk=pk)

    if request.method == "POST":
        # Pega a URL de redirecionamento que o formulário enviou
        redirect_url = request.POST.get("redirect_url", None)

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

    if "export_excel" in request.GET:
        print("Colunas para Excel:", selected_columns)  # <-- Adicione esta linha
        return exportar_convidados_excel(f.qs, selected_columns)
    if "export_pdf" in request.GET:
        print("Colunas para PDF:", selected_columns)  # <-- Adicione esta linha
        return exportar_convidados_pdf(f.qs, selected_columns)
    if "export_print" in request.GET:
        print("Colunas para Impressão:", selected_columns)  # <-- Adicione esta linha
        return imprimir_relatorio(f.qs, selected_columns)

    context = {
        "filter": f,
        "convidados": f.qs,
        "selected_columns": selected_columns,
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
