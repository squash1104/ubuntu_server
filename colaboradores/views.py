from django.shortcuts import render, redirect, get_object_or_404
from .models import Colaborador
from .forms import ColaboradorForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from convidados.models import Convidado
from django.db.models import Q, Count, Sum
from django.http import HttpResponse # Adicione JsonResponse se for ter AJAX para cidade/bairro
from django.template.loader import get_template
from django.utils import timezone
from io import BytesIO
from django.db import models
from .forms import RelatorioColaboradoresForm
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from xhtml2pdf import pisa

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
    form = RelatorioColaboradoresForm(request.GET or None)

    # Anotar a contagem de convidados para cada colaborador
    # Assumimos que no seu modelo Convidado, há um ForeignKey para Colaborador,
    # e que o related_name padrão ou explícito permite 'colaborador.convidado_set.all()'
    # ou se você definiu related_name='convidado', apenas 'convidado' funciona.
    # Vou usar 'convidado' aqui, mas ajuste se seu related_name for diferente.
    colaborador = Colaborador.objects.annotate(
        num_convidados=models.Count('convidado')
    )

    if form.is_valid():
        data_cadastro_inicio = form.cleaned_data.get('data_cadastro_inicio')
        data_cadastro_fim = form.cleaned_data.get('data_cadastro_fim')
        min_convidados = form.cleaned_data.get('min_convidados')
        ordem_colaboradores = form.cleaned_data.get('ordem_colaboradores')

        if data_cadastro_inicio:
            colaboradores = colaboradores.filter(data_cadastro__gte=data_cadastro_inicio)
        if data_cadastro_fim:
            colaboradores = colaboradores.filter(data_cadastro__lte=data_cadastro_fim + timezone.timedelta(days=1))

        if min_convidados is not None:  # Verifica se o valor foi fornecido (pode ser 0)
            colaboradores = colaboradores.filter(num_convidados__gte=min_convidados)

        # Aplica a ordenação
        if ordem_colaboradores == 'nome_asc':
            colaboradores = colaboradores.order_by('nome')
        elif ordem_colaboradores == 'nome_desc':
            colaboradores = colaboradores.order_by('-nome')
        elif ordem_colaboradores == 'convidados_desc':
            colaboradores = colaboradores.order_by('-num_convidados', 'nome')  # Ordena por mais convidados, depois nome
        elif ordem_colaboradores == 'convidados_asc':
            colaboradores = colaboradores.order_by('num_convidados', 'nome')  # Ordena por menos convidados, depois nome
        else:
            colaboradores = colaboradores.order_by('data_cadastro')  # Ordenação padrão

        # Verifica qual botão foi clicado (via nome do parâmetro no GET)
        if 'export_excel' in request.GET:
            return exportar_colaboradores_excel(colaboradores)
        elif 'export_pdf' in request.GET:
            return exportar_colaboradores_pdf(colaboradores)

    return render(request, 'colaboradores/relatorios/relatorio_colaboradores_form.html',
                  {'form': form, 'colaboradores': colaboradores})


def exportar_colaboradores_excel(colaboradores_queryset):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="relatorio_colaboradores.xlsx"'

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Colaboradores"

    # Cabeçalhos: Removido 'ID'
    columns = ['Nome', 'Email', 'Telefone', 'Data Cadastro', 'Qtd Convidados'] # <--- COLUNAS AJUSTADAS
    sheet.append(columns)

    header_font = Font(bold=True)
    for cell in sheet[1]:
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')

    # Dados: Removido 'ID'
    for colaborador in colaboradores_queryset:
        data_cadastro_str = colaborador.data_cadastro.strftime('%Y-%m-%d %H:%M:%S') if colaborador.data_cadastro else ''

        sheet.append([
            colaborador.nome,
            colaborador.email,
            colaborador.telefone,
            data_cadastro_str,
            colaborador.num_convidados
        ])

    workbook.save(response)
    return response

def exportar_colaboradores_pdf(colaboradores_queryset):
    # O caminho do template continua o mesmo, a remoção da coluna será feita no HTML
    template_path = 'colaboradores/relatorios/relatorio_colaboradores_pdf.html'
    context = {'colaboradores': colaboradores_queryset, 'data_geracao': timezone.now()}

    template = get_template(template_path)
    html = template.render(context)

    result_file = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result_file)

    if pisa_status.err:
        return HttpResponse('Erro ao gerar PDF: <pre>%s</pre>' % html, status=400)

    response = HttpResponse(result_file.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_colaboradores.pdf"'
    return response