from django.shortcuts import render, redirect, get_object_or_404
from .models import Convidado
from colaboradores.models import Colaborador
from .forms import ConvidadoForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template # Para PDF
from django.utils import timezone
from io import BytesIO # Para PDF
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from xhtml2pdf import pisa
from .forms import RelatorioConvidadosForm
from geografia.models import Cidade, Bairro

@login_required
def lista_convidados(request):
    termo_busca = request.GET.get('q', '')
    ordenar_por_param = request.GET.get('ordenar_por', 'nome')
    direcao = request.GET.get('direcao', 'asc')

    ordenar_por_query = ordenar_por_param
    if direcao == 'desc':
        ordenar_por_query = f'-{ordenar_por_param}'

    convidados_qs = Convidado.objects.select_related('colaborador', 'cidade', 'bairro')

    if termo_busca:
        convidados_qs = convidados_qs.filter(
            Q(nome__icontains=termo_busca) |
            Q(telefone__icontains=termo_busca) |
            Q(cidade__nome_cidade__icontains=termo_busca) |
            Q(bairro__nome_bairro__icontains=termo_busca) |
            Q(colaborador__nome__icontains=termo_busca)
        )

    convidados_final = convidados_qs.order_by(ordenar_por_query)
    total_convidados_filtrados = convidados_final.count()

    context = {
        'convidados': convidados_final,
        'termo_busca': termo_busca,
        'ordenar_por': ordenar_por_param,
        'direcao': direcao,
        'total_convidados_filtrados': total_convidados_filtrados,
    }

    if request.GET.get('is_ajax') == 'true':
        return render(request, 'convidados/convidados_table_fragment.html', context)
    else:
        return render(request, 'convidados/lista_convidados.html', context)

@login_required
def colaborador_convidados(request, pk):
    colaborador = get_object_or_404(Colaborador, pk=pk)
    convidados_do_colaborador = Convidado.objects.filter(colaborador=colaborador)
    total_convidados = convidados_do_colaborador.count()

    # --- Lógica de Ordenação (similar à lista geral de convidados) ---
    ordenar_por = request.GET.get('ordenar_por', 'nome') # Padrão: ordenar por nome
    direcao = request.GET.get('direcao', 'asc')         # Padrão: ascendente

    # Mapeia os nomes das colunas do template para os nomes dos campos do modelo
    campos_ordenaveis = {
        'nome': 'nome',
        'telefone': 'telefone',
        'cidade': 'cidade',
        'bairro': 'bairro',
        'colaborador': 'colaborador',
    }

    # Verifica se o campo de ordenação é válido e aplica a ordenação
    if ordenar_por in campos_ordenaveis:
        prefixo = '-' if direcao == 'desc' else ''
        convidados_do_colaborador = convidados_do_colaborador.order_by(f'{prefixo}{campos_ordenaveis[ordenar_por]}')
    # --- Fim da Lógica de Ordenação ---

    context = {
        'colaborador': colaborador,
        'convidados': convidados_do_colaborador,
        'total_convidados': convidados_do_colaborador.count(),
        'ordenar_por': ordenar_por, # Passa o campo de ordenação atual para o template
        'direcao': direcao,         # Passa a direção de ordenação atual para o template
    }
    return render(request, 'convidados/colaborador_convidados.html', context)

@login_required
def cadastrar_convidado(request, colaborador_id=None): # <--- Garanta que aceita colaborador_id=None
    colaborador = None
    if colaborador_id:
        colaborador = get_object_or_404(Colaborador, pk=colaborador_id)

    if request.method == 'POST':
        form = ConvidadoForm(request.POST)
        if form.is_valid():
            convidado = form.save()
            messages.success(request, f'Convidado "{convidado.nome}" cadastrado com sucesso!')
            if colaborador:
                form = ConvidadoForm(initial={'colaborador': colaborador})

                context = {
                    'form': form,
                    'colaborador': colaborador,
                }
                return render(request,'convidados/cadastrar_convidado.html', context)
            else:
                # Caso contrário, volta para a lista geral
                return redirect('convidados:lista_convidados')
    else:
        # Se for o primeiro acesso (GET) e viemos de um colaborador,
        # já preenche o campo 'colaborador' no formulário
        if colaborador:
            form = ConvidadoForm(initial={'colaborador': colaborador})
        else:
            form = ConvidadoForm()

    context = {
        'form': form,
        # Envia o colaborador (ou None) para o template saber de onde viemos
        'colaborador': colaborador,
    }
    return render(request, 'convidados/cadastrar_convidado.html', context)

@login_required
def editar_convidado(request, pk):
    convidado = get_object_or_404(Convidado, pk=pk)
    colaborador_origem_id = request.GET.get('colaborador_origem_id')

    if request.method == 'POST':
        form = ConvidadoForm(request.POST, instance=convidado)
        if form.is_valid():
            form.save()
            messages.warning(request, f'Convidado "{convidado.nome}" editado com sucesso!')
            if colaborador_origem_id:
                return redirect('convidados:colaborador_convidados', pk=colaborador_origem_id)
            else:
                return redirect('convidados:lista_convidados')
    else:
        form = ConvidadoForm(instance=convidado)

    # **THE CORRECTION IS HERE**
    # This `context` and `return render` block must be outside the `else` block
    # so that it is executed for both GET and invalid POST requests.
    context = {
        'form': form,
        'convidado': convidado,
    }
    return render(request, 'convidados/editar_convidado.html', context)

@login_required
def excluir_convidado(request, pk):
    convidado = get_object_or_404(Convidado, pk=pk)

    if request.method == 'POST':
        # Pega a URL de redirecionamento que o formulário enviou
        redirect_url = request.POST.get('redirect_url', None)

        # Guarda o nome do convidado antes de o apagar
        nome_convidado = convidado.nome

        # Apaga o convidado do banco de dados
        convidado.delete()

        messages.success(request, f'Convidado "{nome_convidado}" excluído com sucesso!')

        # Se a URL de redirecionamento foi enviada, usa-a.
        # Caso contrário, usa uma URL padrão (fallback de segurança).
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect('convidados:lista_convidados')

    # Se a requisição não for POST, simplesmente redireciona para a lista geral.
    return redirect('convidados:lista_convidados')


def relatorio_convidados_view(request):
    form = RelatorioConvidadosForm(request.GET or None)
    convidados = Convidado.objects.all() # Queryset inicial, será filtrado

    if form.is_valid():
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        cidade = form.cleaned_data.get('cidade') # Novo filtro
        bairro = form.cleaned_data.get('bairro') # Novo filtro
        ordem_alfabetica = form.cleaned_data.get('ordem_alfabetica') # Novo filtro

        if data_inicio:
            convidados = convidados.filter(data_cadastro__gte=data_inicio)
        if data_fim:
            convidados = convidados.filter(data_cadastro__lte=data_fim + timezone.timedelta(days=1)) # Inclui o dia todo

        if cidade:
            convidados = convidados.filter(cidade=cidade)
        if bairro:
            convidados = convidados.filter(bairro=bairro)

        # Aplica a ordenação
        if ordem_alfabetica == 'nome_asc':
            convidados = convidados.order_by('nome')
        elif ordem_alfabetica == 'nome_desc':
            convidados = convidados.order_by('-nome')
        else:
            convidados = convidados.order_by('data_cadastro') # Ordenação padrão se nenhum critério for escolhido

        # Verifica qual botão foi clicado (via nome do parâmetro no GET)
        if 'export_excel' in request.GET:
            return exportar_convidados_excel(convidados)
        elif 'export_pdf' in request.GET:
            return exportar_convidados_pdf(convidados)

    return render(request, 'report/guest_report_form.html', {'form': form, 'convidados': convidados})


# Mantenha as funções exportar_convidados_excel e exportar_convidados_pdf como estão,
# elas já receberão o queryset 'convidados' filtrado.

# NOVO: View para retornar bairros via AJAX
def get_bairros_ajax(request):
    cidade_id = request.GET.get('cidade_id')
    bairros = []
    if cidade_id:
        bairros_qs = Bairro.objects.filter(cidade_id=cidade_id).order_by('nome_bairro')
        bairros = [{'id': bairro.id, 'nome_bairro': bairro.nome_bairro} for bairro in bairros_qs]
    return JsonResponse(bairros, safe=False)


def exportar_convidados_excel(convidados_queryset):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="relatorio_convidados.xlsx"'

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Convidados"

    # Cabeçalhos: Removido 'ID' e 'Status'
    columns = ['Nome', 'Email', 'Telefone', 'Data Cadastro', 'Cidade', 'Bairro'] # <--- COLUNAS AJUSTADAS
    sheet.append(columns)

    header_font = Font(bold=True)
    for cell in sheet[1]:
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')

    # Dados: Removido 'ID' e 'Status'
    for convidado in convidados_queryset:
        data_cadastro_str = convidado.data_cadastro.strftime('%Y-%m-%d %H:%M:%S') if convidado.data_cadastro else ''

        sheet.append([
            convidado.nome,
            convidado.email,
            convidado.telefone,
            data_cadastro_str,
            str(convidado.cidade) if convidado.cidade else '', # Converte para string se for objeto
            str(convidado.bairro) if convidado.bairro else ''  # Converte para string se for objeto
        ])

    workbook.save(response)
    return response

def exportar_convidados_pdf(convidados_queryset):
    # O caminho do template continua o mesmo, a remoção das colunas será feita no HTML
    template_path = 'convidados/relatorios/relatorio_convidados_pdf.html' # ou 'report/guest_report_form.html' se usar o mesmo

    context = {
        'convidados': convidados_queryset,
        'data_geracao': timezone.now()
    }

    template = get_template(template_path)
    html = template.render(context)

    result_file = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result_file)

    if pisa_status.err:
        return HttpResponse('Erro ao gerar PDF: <pre>%s</pre>' % html, status=400)

    response = HttpResponse(result_file.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_convidados.pdf"'
    return response