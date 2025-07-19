from django.shortcuts import render, redirect, get_object_or_404
from .models import Colaborador
from .forms import ColaboradorForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from convidados.models import Convidado
from django.db.models import Count
from django.db.models import Q

@login_required
def lista_colaboradores(request):
    colaboradores = Colaborador.objects.all()

    # --- Lógica de Busca por Texto (novo) ---
    query = request.GET.get('q')
    if query:
        # Filtra por nome, contato, cidade ou bairro (case-insensitive contains)
        colaboradores = colaboradores.filter(
            Q(nome__icontains=query) |
            Q(contato__icontains=query) |
            Q(cidade__icontains=query) |
            Q(bairro__icontains=query)
        )
    # --- Fim da Lógica de Busca por Texto ---

    # --- Lógica de Ordenação ---
    # Pega os parâmetros 'ordenar_por' e 'direcao' da URL (GET request)
    ordenar_por = request.GET.get('ordenar_por', 'nome') # Padrão: ordenar por nome
    direcao = request.GET.get('direcao', 'asc')         # Padrão: ascendente

    # Mapeia os nomes das colunas do template para os nomes dos campos do modelo
    campos_ordenaveis = {
        'nome': 'nome',
        'contato': 'contato',
        'cidade': 'cidade',
        'bairro': 'bairro',
        'num_convidados': 'num_convidados', # Permite ordenar pela contagem de convidados
    }

    colaboradores = colaboradores.annotate(num_convidados=Count('convidados'))

    # Verifica se o campo de ordenação é válido
    if ordenar_por in campos_ordenaveis:
        # Se a direção é descendente, adiciona um '-' ao nome do campo
        prefixo = '-' if direcao == 'desc' else ''
        # Aplica a ordenação
        colaboradores = colaboradores.order_by(f'{prefixo}{campos_ordenaveis[ordenar_por]}')
    # --- Fim da Lógica de Ordenação ---

    
    context = {
        'colaboradores': colaboradores,
        'ordenar_por': ordenar_por, # Passa o campo de ordenação atual para o template
        'direcao': direcao,         # Passa a direção de ordenação atual para o template
        'query': query if query else '',
    }
    # --- LÓGICA DE RESPOSTA AJAX ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Se for uma requisição AJAX, renderiza apenas o fragmento da tabela
        return render(request, 'colaboradores/colaboradores_table_fragment.html', context)
    # --- FIM DA LÓGICA DE RESPOSTA AJAX ---

    # Para requisições normais (não AJAX), renderiza a página completa
    return render(request, 'colaboradores/lista_colaboradores.html', context)

@login_required
def cadastrar_colaborador(request):
    if request.method == 'POST':
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            colaborador = form.save()
            colaborador_nome = colaborador.nome
            messages.success(request, f'Colaborador "{colaborador_nome}" cadastrado com sucesso!')
            return redirect('colaboradores:lista_colaboradores')
    else:
        form = ColaboradorForm()
    return render(request, 'colaboradores/cadastrar_colaborador.html', {'form': form})

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
