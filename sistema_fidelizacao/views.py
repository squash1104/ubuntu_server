from django.shortcuts import render
from django.contrib.auth.decorators import login_required # Importe este decorador
from colaboradores.models import Colaborador # Importe o modelo Colaborador
from convidados.models import Convidado
from django.contrib import messages
from django.db.models import Count
import logging

@login_required
def home(request):
	return render(request, 'home.html', {'titulo': 'Bem-vindo ao Sistema de Fidelização de Votos!'})

@login_required # Este decorador garante que apenas usuários logados acessem esta view
def dashboard(request):
    nome_usuario_logado = request.user.username # Nome padrão para teste
    colaborador_obj = None

    # Tentativa de encontrar um Colaborador baseado no nome de usuário logado
    # Isso é uma simplificação. O ideal seria ter um OneToOneField no modelo Colaborador
    # que linka diretamente para o modelo User do Django.
    try:
        colaborador_obj = Colaborador.objects.get(nome__iexact=request.user.username)

    except Colaborador.DoesNotExist:

        pass
    
    total_colaboradores = Colaborador.objects.count()
    total_convidados = Convidado.objects.count()

    context = {
        'nome_colaborador': nome_usuario_logado,
        'colaborador_obj': colaborador_obj, # Passamos o objeto para acesso a outros dados
        'total_colaboradores': total_colaboradores, # <-- Adiciona esta contagem ao contexto
        'total_convidados': total_convidados,      

 }
    return render(request, 'dashboard.html', context)

@login_required # Protege a view do mapa
def mapa_apoiadores(request):
    return render(request, 'mapa_apoiadores.html')

# função teste para correção, excluir depois
def teste_notificacao(request):
    return render(request, 'teste_notificacao.html')