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

    try:
        colaborador_obj = Colaborador.objects.get(nome__iexact=request.user.username)

    except Colaborador.DoesNotExist:

        pass

    # Calcula total de convidados e colaboradores cadastrados para nossos cards
    total_colaboradores = Colaborador.objects.count()
    total_convidados = Convidado.objects.count()

    colaboradores_com_contagem = Colaborador.objects.annotate(
        num_convidados=Count('convidados')
    )

    # Define as nossas metas
    meta = 15

    # Calcula quantos colaboradores estão em cada categoria de meta para grafico rosca
    abaixo_da_meta = colaboradores_com_contagem.filter(num_convidados__lt=meta).count()
    na_meta = colaboradores_com_contagem.filter(num_convidados=meta).count()
    meta_superada = colaboradores_com_contagem.filter(num_convidados__gt=meta).count()

    # Calcula nosso top 10 para grafico
    top_5_colaboradores = Colaborador.objects.annotate(
        num_convidados=Count('convidados')
    ).order_by('-num_convidados')[:5]

    context = {
        'nome_colaborador': nome_usuario_logado,
        'colaborador_obj': colaborador_obj, # Passamos o objeto para acesso a outros dados
        'total_colaboradores': total_colaboradores, # <-- Adiciona esta contagem ao contexto
        'total_convidados': total_convidados,
        'dados_abaixo_meta': abaixo_da_meta,
        'dados_na_meta': na_meta,
        'dados_meta_superada': meta_superada,
        'top_5_colaboradores': top_5_colaboradores,
 }
    return render(request, 'dashboard.html', context)

@login_required # Protege a view do mapa
def mapa_apoiadores(request):
    return render(request, 'mapa_apoiadores.html')



def sobre(request):
    # Futuramente, podemos passar a versão do app dinamicamente aqui
    context = {
        'versao_app': '1.0.0'
    }
    return render(request, 'sobre.html', context)