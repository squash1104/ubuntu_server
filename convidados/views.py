from django.shortcuts import render, redirect, get_object_or_404
from .models import Convidado
from colaboradores.models import Colaborador
from .forms import ConvidadoForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView


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
    colaborador_selecionado = None
    if colaborador_id:
        colaborador_selecionado = get_object_or_404(Colaborador, pk=colaborador_id)

    if request.method == 'POST':
        form = ConvidadoForm(request.POST)
        if form.is_valid():
            convidado = form.save(commit=False)
            if colaborador_selecionado:
                convidado.colaborador = colaborador_selecionado
            convidado.save()
            messages.success(request, f'Convidado "{convidado.nome}" cadastrado com sucesso!')

            # --- LÓGICA DE REDIRECIONAMENTO AGORA CORRETA ---
            # Redireciona para a mesma página de cadastro para o mesmo colaborador, se aplicável.
            # Se o convidado foi cadastrado a partir de uma página de colaborador, volta para o mesmo formulário.
            if colaborador_selecionado:
                return redirect('convidados:cadastrar_convidado_para_colaborador', colaborador_id=colaborador_selecionado.id)
            else:
                # Se não foi cadastrado para um colaborador específico (veio do dashboard, por exemplo),
                # redireciona para a lista geral de convidados.
                return redirect('convidados:lista_convidados')
            # --- FIM DA LÓGICA DE REDIRECIONAMENTO ---
        else:
            messages.error(request, 'Erro ao cadastrar convidado. Verifique os dados.')
    else:
        if colaborador_selecionado:
            form = ConvidadoForm(initial={'colaborador': colaborador_selecionado})
        else:
            form = ConvidadoForm()

    context = {
        'form': form,
        'colaborador_selecionado': colaborador_selecionado
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