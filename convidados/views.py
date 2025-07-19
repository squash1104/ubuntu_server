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
    convidados = Convidado.objects.all()

    query = request.GET.get('q')
    if query:
        convidados = convidados.filter(
            Q(nome__icontains=query) |
            Q(telefone__icontains=query) |
            Q(cidade__icontains=query) |
            Q(bairro__icontains=query) |
            Q(colaborador__nome__icontains=query)
        ).distinct()

    ordenar_por = request.GET.get('ordenar_por', 'nome')
    direcao = request.GET.get('direcao', 'asc')

    campos_ordenaveis = {
        'nome': 'nome',
        'telefone': 'telefone',
        'cidade': 'cidade',
        'bairro': 'bairro',
        'colaborador': 'colaborador__nome',
    }

    if ordenar_por in campos_ordenaveis:
        prefixo = '-' if direcao == 'desc' else ''
        convidados = convidados.order_by(f'{prefixo}{campos_ordenaveis[ordenar_por]}')

    context = {
        'convidados': convidados,
        'ordenar_por': ordenar_por,
        'direcao': direcao,
        'query': query if query else '',
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('is_ajax') == 'true':
         return render(request, 'convidados/convidados_table_fragment.html', context)

    return render(request, 'convidados/lista_todos_convidados.html', context)

@login_required
def colaborador_convidados(request, colaborador_id):
    colaborador = get_object_or_404(Colaborador, pk=colaborador_id)
    convidados_do_colaborador = Convidado.objects.filter(colaborador=colaborador)

    # --- Lógica de Ordenação (similar à lista geral de convidados) ---
    ordenar_por = request.GET.get('ordenar_por', 'nome') # Padrão: ordenar por nome
    direcao = request.GET.get('direcao', 'asc')         # Padrão: ascendente

    # Mapeia os nomes das colunas do template para os nomes dos campos do modelo
    campos_ordenaveis = {
        'nome': 'nome',
        'telefone': 'telefone',
        'cidade': 'cidade',
        'bairro': 'bairro',
    }

    # Verifica se o campo de ordenação é válido e aplica a ordenação
    if ordenar_por in campos_ordenaveis:
        prefixo = '-' if direcao == 'desc' else ''
        convidados_do_colaborador = convidados_do_colaborador.order_by(f'{prefixo}{campos_ordenaveis[ordenar_por]}')
    # --- Fim da Lógica de Ordenação ---

    context = {
        'colaborador': colaborador,
        'convidados': convidados_do_colaborador,
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

    if request.method == 'POST':
        form = ConvidadoForm(request.POST, instance=convidado)
        if form.is_valid():
            form.save()
            messages.warning(request, 'Convidado editado com sucesso!')
            # Após salvar, redireciona para a lista de convidados do colaborador, se houver um colaborador associado
            if convidado.colaborador:
                return redirect('convidados:lista_convidados')
    else:
        form = ConvidadoForm(instance=convidado)
    return render(request, 'convidados/editar_convidado.html', {'form': form, 'convidado': convidado})

@login_required
def excluir_convidado(request, pk): # <-- A função espera 'pk'
    convidado = get_object_or_404(Convidado, pk=pk)
    if request.method == 'POST':
        try:
            convidado_nome = convidado.nome
            convidado.delete()
            messages.error(request, f'Convidado "{convidado_nome}" excluído com sucesso!')
            return redirect('convidados:lista_convidados')
        except ProtectedError:
            messages.error(request, 'Colaborador não pode ser excluído porque possui associações. Por favor, remova as associações primeiro.')
            # Renderiza o template de confirmação novamente com o contexto de erro
            return render(request, 'convidados/confirmar_exclusao_convidado.html', {'convidado': convidado}) # Se passar contexto, precisa do template
        except Exception as e:
            messages.error(request, f'Ocorreu um erro inesperado ao excluir o convidado: {e}')
            return render(request, 'convidados/confirmar_exclusao_convidado.html', {'convidado': convidado})
    return render(request, 'convidados/confirmar_exclusao_convidado.html', {'convidado': convidado})