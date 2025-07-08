from django.shortcuts import render
from django.contrib.auth.decorators import login_required # Importe este decorador
from colaboradores.models import Colaborador # Importe o modelo Colaborador
from convidados.models import Convidado

def home(request):
	return render(request, 'home.html', {'titulo': 'Bem-vindo ao Sistema de Fidelização de Votos!'})

@login_required # Este decorador garante que apenas usuários logados acessem esta view
def dashboard(request):
    # Aqui, vamos tentar encontrar o Colaborador associado ao usuário logado.
    # Por enquanto, faremos uma busca simples por nome ou uma forma mais direta se já tivermos um vínculo.
    # Para fins de demonstração, vamos simular o nome do colaborador.
    # Em um sistema real, você vincularia o Colaborador ao usuário Django (ex: através de um campo OneToOneField).

    nome_colaborador = "Colaborador Padrão" # Nome padrão para teste
    colaborador_obj = None

    # Tentativa de encontrar um Colaborador baseado no nome de usuário logado
    # Isso é uma simplificação. O ideal seria ter um OneToOneField no modelo Colaborador
    # que linka diretamente para o modelo User do Django.
    try:
        colaborador_obj = Colaborador.objects.get(nome__iexact=request.user.username)
        nome_colaborador = colaborador_obj.nome
    except Colaborador.DoesNotExist:
        # Se não encontrar um Colaborador com o nome de usuário, tenta com o primeiro Colaborador cadastrado
        # ou mantém o nome padrão.
        primeiro_colaborador = Colaborador.objects.first()
        if primeiro_colaborador:
            nome_colaborador = primeiro_colaborador.nome
            colaborador_obj = primeiro_colaborador
        else:
            nome_colaborador = "Usuário sem Colaborador associado"

    total_colaboradores = Colaborador.objects.count()
    total_convidados = Convidado.objects.count()

    context = {
        'nome_colaborador': nome_colaborador,
        'colaborador_obj': colaborador_obj, # Passamos o objeto para acesso a outros dados
        'total_colaboradores': total_colaboradores, # <-- Adiciona esta contagem ao contexto
        'total_convidados': total_convidados,      

 }
    return render(request, 'dashboard.html', context)

@login_required # Protege a view do mapa
def mapa_apoiadores(request):
    return render(request, 'mapa_apoiadores.html')
