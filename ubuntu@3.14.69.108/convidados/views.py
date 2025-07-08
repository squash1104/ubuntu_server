from django.shortcuts import render, redirect, get_object_or_404
from .models import Convidado # Importa o modelo Convidado
from colaboradores.models import Colaborador
from .forms import ConvidadoForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

@login_required
def lista_convidados(request):
    convidados = Convidado.objects.all()

    # --- Lógica de Ordenação ---
    ordenar_por = request.GET.get('ordenar_por', 'nome') # Padrão: ordenar por nome
    direcao = request.GET.get('direcao', 'asc')         # Padrão: ascendente

    # Mapeia os nomes das colunas do template para os nomes dos campos do modelo
    campos_ordenaveis = {
        'nome': 'nome',
        'telefone': 'telefone',
        'cidade': 'cidade',
        'bairro': 'bairro',
        'colaborador': 'colaborador__nome', # Ordena pelo nome do colaborador relacionado
    }

    # Verifica se o campo de ordenação é válido e aplica a ordenação
    if ordenar_por in campos_ordenaveis:
        prefixo = '-' if direcao == 'desc' else ''
        convidados = convidados.order_by(f'{prefixo}{campos_ordenaveis[ordenar_por]}')
    # --- Fim da Lógica de Ordenação ---

    context = {
        'convidados': convidados,
        'ordenar_por': ordenar_por, # Passa o campo de ordenação atual para o template
        'direcao': direcao,         # Passa a direção de ordenação atual para o template
    }
    return render(request, 'convidados/lista_convidados.html', context)   

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
def editar_convidado(request, convidado_id):
    convidado = get_object_or_404(Convidado, pk=convidado_id)

    if request.method == 'POST':
        form = ConvidadoForm(request.POST, instance=convidado)
        if form.is_valid():
            form.save()
            # Após salvar, redireciona para a lista de convidados do colaborador, se houver um colaborador associado
            if convidado.colaborador:
                return redirect('convidados:colaborador_convidados', colaborador_id=convidado.colaborador.id)
            else:
                # Caso contrário, redireciona para a lista geral de convidados
                return redirect('convidados:lista_convidados')
    else:
        form = ConvidadoForm(instance=convidado)

    context = {
        'form': form,
        'convidado': convidado, # Passa o objeto convidado para o template
    }
    return render(request, 'convidados/editar_convidado.html', context)

@login_required # Protege a view de exclusão
def excluir_convidado(request, convidado_id):
    convidado = get_object_or_404(Convidado, pk=convidado_id)

    # Opcional: Salva o ID do colaborador antes de excluir, caso precise após a exclusão do convidado
    colaborador_id_do_convidado = None
    if convidado.colaborador:
        colaborador_id_do_convidado = convidado.colaborador.id

    if request.method == 'POST':
        convidado.delete()
        messages.success(request, f'Convidado "{convidado.nome}" excluído com sucesso!')

        # --- LÓGICA DE REDIRECIONAMENTO AJUSTADA AQUI ---
        # Verifica se a requisição veio da página de convidados de um colaborador
        # Isso é uma forma de inferir de onde a exclusão foi acionada.
        referer = request.META.get('HTTP_REFERER')
        if referer and f'/convidados/do_colaborador/{colaborador_id_do_convidado}/' in referer:
            # Se veio da página específica de um colaborador, volta para lá
            return redirect('convidados:colaborador_convidados', colaborador_id=colaborador_id_do_convidado)
        else:
            # Caso contrário (ex: veio da lista geral), volta para a lista geral
            return redirect('convidados:lista_convidados')
        # --- FIM DA LÓGICA AJUSTADA ---

    messages.error(request, 'A exclusão deve ser feita via POST. Por favor, use o botão "Excluir" na lista.')

    # Redirecionamento de fallback caso a exclusão não seja POST (deve gerar erro de segurança antes)
    if convidado.colaborador:
        return redirect('convidados:colaborador_convidados', colaborador_id=convidado.colaborador.id)
    else:
        return redirect('convidados:lista_convidados')
