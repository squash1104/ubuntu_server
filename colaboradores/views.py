from django.shortcuts import render, redirect, get_object_or_404
from .models import Colaborador
from .forms import ColaboradorForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from convidados.models import Convidado
from django.db.models import Q, Count, Sum
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.utils import timezone
from io import BytesIO
from django.db import models
from .forms import RelatorioColaboradoresForm
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from xhtml2pdf import pisa
from .filters import ColaboradorFilter
from .utils import exportar_colaboradores_excel, exportar_colaboradores_pdf, imprimir_relatorio_colaboradores
from geografia.models import Cidade, Bairro


@login_required
def lista_colaboradores(request):
    termo_busca = request.GET.get('q', '')
    ordenar_por_param = request.GET.get('ordenar_por', 'nome')
    direcao = request.GET.get('direcao', 'asc')

    ordenar_por_query = ordenar_por_param
    if direcao == 'desc':
        ordenar_por_query = f'-{ordenar_por_param}'

    colaboradores_qs = Colaborador.objects.select_related('cidade', 'bairro')

    if termo_busca:
        colaboradores_qs = colaboradores_qs.filter(
            Q(nome__icontains=termo_busca) |
            Q(telefone__icontains=termo_busca) |
            Q(cidade__nome_cidade__icontains=termo_busca) |
            Q(bairro__nome_bairro__icontains=termo_busca)
        )

    colaboradores_final = colaboradores_qs.annotate(
        num_convidados=Count('convidados', distinct=True)
    ).order_by(ordenar_por_query)

    total_colaboradores_filtrados = colaboradores_final.count()
    soma_convidados = colaboradores_final.aggregate(
        total=Sum('num_convidados')
    )
    total_convidados_filtrados = soma_convidados['total'] or 0

    context = {
        'colaboradores': colaboradores_final,
        'termo_busca': termo_busca,
        'ordenar_por': ordenar_por_param,
        'direcao': direcao,
        'total_colaboradores_filtrados': total_colaboradores_filtrados,
        'total_convidados_filtrados': total_convidados_filtrados,
    }

    # 7. Responde de forma inteligente (AJAX ou requisição normal)
    if request.GET.get('is_ajax') == 'true':
        # Se for AJAX, retorna APENAS o fragmento da tabela
        return render(request, 'colaboradores/colaboradores_table_fragment.html', context)
    else:
        # Se for uma requisição normal, retorna a página completa
        return render(request, 'colaboradores/lista_colaboradores.html', context)


@login_required
def adicionar_colaborador(request):
    if request.method == 'POST':
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            colaborador = form.save()
            colaborador_nome = colaborador.nome
            messages.success(request, f'Colaborador "{colaborador_nome}" cadastrado com sucesso!')
            return redirect('colaboradores:lista_colaboradores')
    else:
        form = ColaboradorForm()
    return render(request, 'colaboradores/adicionar_colaborador.html', {'form': form})

@login_required
def editar_colaborador(request, colaborador_id):
    colaborador = get_object_or_404(Colaborador, pk=colaborador_id)

    if request.method == 'POST':
        # Se a requisição for POST, o formulário foi enviado com dados atualizados
        # Preenche o formulário com os dados da requisição E a instância do colaborador (para atualização)
        form = ColaboradorForm(request.POST, instance=colaborador)
        if form.is_valid():
            # Se os dados são válidos, salva as alterações no banco de dados
            form.save()
            messages.warning(request, 'Colaborador editado com sucesso!')
            # Redireciona para a lista de colaboradores após a edição bem-sucedida
            return redirect('colaboradores:lista_colaboradores')
    else:
        # Se a requisição for GET, exibe o formulário pré-preenchido com os dados atuais do colaborador
        form = ColaboradorForm(instance=colaborador)

    context = {
        'form': form,
        'colaborador': colaborador, # Passa o objeto colaborador para o template
    }
    return render(request, 'colaboradores/editar_colaborador.html', context)

@login_required # Protege a view de exclusão
def excluir_colaborador(request, colaborador_id):
    colaborador = get_object_or_404(Colaborador, pk=colaborador_id)

    # Contagem de convidados associados
    quantidade_convidados = Convidado.objects.filter(colaborador=colaborador).count()

    if request.method == 'POST':
        if quantidade_convidados == 0:
            # Se não há convidados, pode excluir
            colaborador.delete()
            messages.success(request, f'Colaborador "{colaborador.nome}" excluído com sucesso!')
        else:
            # Se há convidados, impede a exclusão e adiciona uma mensagem de erro
            messages.error(request, f'Não foi possível excluir o colaborador "{colaborador.nome}" porque ele possui {quantidade_convidados} convidados associados.')
        return redirect('colaboradores:lista_colaboradores')

    # Para requisições GET (se você quiser uma página de confirmação de exclusão)
    # Por enquanto, vamos fazer a exclusão direto com POST para simplificar.
    # No entanto, é boa prática ter uma página de confirmação para exclusão.
    # Caso queira uma página de confirmação, remova o `if request.method == 'POST':` e adicione um template.

    # Alternativa para GET: exibir uma mensagem de erro ou um formulário de confirmação simples
    messages.error(request, 'A exclusão deve ser feita via POST. Por favor, use o botão "Excluir" na lista.')
    return redirect('colaboradores:lista_colaboradores') # Redireciona de volta com a mensagem de erro


def relatorio_colaboradores_view(request):
    # Anota a contagem de convidados para cada colaborador
    queryset = Colaborador.objects.annotate(total_convidados=Count('convidados'))

    f = ColaboradorFilter(request.GET, queryset=queryset)

    selected_columns = request.GET.getlist('columns')
    if not selected_columns:
        selected_columns = ['nome', 'telefone', 'cidade', 'bairro', 'total_convidados', 'data_cadastro']  # Colunas padrão

    if 'export_excel' in request.GET:
        return exportar_colaboradores_excel(f.qs, selected_columns)
    elif 'export_pdf' in request.GET:
        return exportar_colaboradores_pdf(f.qs, selected_columns)
    elif 'export_print' in request.GET:
        return imprimir_relatorio_colaboradores(f.qs, selected_columns)

    context = {
        'filter': f,
        'colaboradores': f.qs,
        'selected_columns': selected_columns,
    }
    return render(request, 'relatorios/relatorio_colaboradores_form.html', context)


def get_bairros_ajax(request):
    cidade_id = request.GET.get('cidade_id')
    bairros = []
    if cidade_id:
        bairros_qs = Bairro.objects.filter(cidade_id=cidade_id).order_by('nome_bairro')
        bairros = [{'id': bairro.id, 'nome_bairro': bairro.nome_bairro} for bairro in bairros_qs]
    return JsonResponse(bairros, safe=False)