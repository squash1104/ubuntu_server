from django.shortcuts import render
from django.contrib.auth.decorators import login_required # Importe este decorador
from colaboradores.models import Colaborador # Importe o modelo Colaborador
from convidados.models import Convidado
from django.contrib import messages
from django.db.models import Count
import json
import logging
from django.utils import timezone
import csv # Para CSV
from openpyxl import Workbook # Para Excel
from openpyxl.styles import Font
from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import get_template


CIDADE_PARA_MESORREGIAO = {
    # NORTE
    'Alta Floresta': 'Norte', 'Apiacás': 'Norte', 'Carlinda': 'Norte', 'Nova Bandeirantes': 'Norte', 'Nova Monte Verde': 'Norte', 'Paranaíta': 'Norte',
    'Ipiranga do Norte': 'Norte', 'Itanhangá': 'Norte', 'Lucas do Rio Verde': 'Norte', 'Nobres': 'Norte', 'Nova Mutum': 'Norte', 'Nova Ubiratã': 'Norte', 'Santa Rita do Trivelato': 'Norte', 'Sorriso': 'Norte', 'Tapurah': 'Norte',
    'Juara': 'Norte', 'Nova Maringá': 'Norte', 'Novo Horizonte do Norte': 'Norte', 'Porto dos Gaúchos': 'Norte', 'São José do Rio Claro': 'Norte', 'Tabaporã': 'Norte',
    'Aripuanã': 'Norte', 'Brasnorte': 'Norte', 'Castanheira': 'Norte', 'Colniza': 'Norte', 'Cotriguaçu': 'Norte', 'Juína': 'Norte', 'Juruena': 'Norte', 'Rondolândia': 'Norte',
    'Colíder': 'Norte', 'Guarantã do Norte': 'Norte', 'Matupá': 'Norte', 'Nova Canaã do Norte': 'Norte', 'Nova Guarita': 'Norte', 'Novo Mundo': 'Norte', 'Peixoto de Azevedo': 'Norte', 'Terra Nova do Norte': 'Norte',
    'Cláudia': 'Norte', 'Feliz Natal': 'Norte', 'Itaúba': 'Norte', 'Marcelândia': 'Norte', 'Nova Santa Helena': 'Norte', 'Santa Carmem': 'Norte', 'Sinop': 'Norte', 'União do Sul': 'Norte', 'Vera': 'Norte',

    # NORDESTE
    'Alto Boa Vista': 'Nordeste', 'Bom Jesus do Araguaia': 'Nordeste', 'Canabrava do Norte': 'Nordeste', 'Confresa': 'Nordeste', 'Luciara': 'Nordeste', 'Novo Santo Antônio': 'Nordeste',
    'Porto Alegre do Norte': 'Nordeste', 'Ribeirão Cascalheira': 'Nordeste', 'Santa Cruz do Xingu': 'Nordeste', 'Santa Terezinha': 'Nordeste', 'São Félix do Araguaia': 'Nordeste',
    'São José do Xingu': 'Nordeste', 'Serra Nova Dourada': 'Nordeste', 'Vila Rica': 'Nordeste', 'Água Boa': 'Nordeste', 'Campinápolis': 'Nordeste', 'Canarana': 'Nordeste',
    'Nova Nazaré': 'Nordeste', 'Nova Xavantina': 'Nordeste', 'Novo São Joaquim': 'Nordeste', 'Querência': 'Nordeste', 'Santo Antônio do Leste': 'Nordeste',
    'Araguaiana': 'Nordeste', 'Barra do Garças': 'Nordeste', 'Cocalinho': 'Nordeste',

    # SUDESTE
    'Gaúcha do Norte': 'Sudeste', 'Paranatinga': 'Sudeste', 'Planalto da Serra': 'Sudeste', 'Campo Verde': 'Sudeste', 'Dom Aquino': 'Sudeste', 'Itiquira': 'Sudeste',
    'Jaciara': 'Sudeste', 'Juscimeira': 'Sudeste', 'Pedra Preta': 'Sudeste', 'Poxoréu': 'Sudeste', 'Primavera do Leste': 'Sudeste', 'Rondonópolis': 'Sudeste', 'São Pedro da Cipa': 'Sudeste',
    'General Carneiro': 'Sudeste', 'Pontal do Araguaia': 'Sudeste', 'Tesouro': 'Sudeste', 'Torixoréu': 'Sudeste', 'Guiratinga': 'Sudeste', 'São José do Povo': 'Sudeste',
    'Araguainha': 'Sudeste', 'Ponte Branca': 'Sudeste', 'Ribeirãozinho': 'Sudeste', 'Alto Araguaia': 'Sudeste', 'Alto Garças': 'Sudeste', 'Alto Taquari': 'Sudeste',

    # SUDOESTE
    'Conquista d''Oeste': 'Sudoeste', 'Nova Lacerda': 'Sudoeste', 'Pontes e Lacerda': 'Sudoeste', 'Vale de São Domingos': 'Sudoeste', 'Vila Bela da Santíssima Trindade': 'Sudoeste',
    'Araputanga': 'Sudoeste', 'Figueirópolis d''Oeste': 'Sudoeste', 'Glória d''Oeste': 'Sudoeste', 'Indiavaí': 'Sudoeste', 'Jauru': 'Sudoeste', 'Lambari d''Oeste': 'Sudoeste',
    'Mirassol d''Oeste': 'Sudoeste', 'Porto Esperidião': 'Sudoeste', 'Reserva do Cabaçal': 'Sudoeste', 'Rio Branco': 'Sudoeste', 'Salto do Céu': 'Sudoeste', 'São José dos Quatro Marcos': 'Sudoeste',
    'Barra do Bugres': 'Sudoeste', 'Denise': 'Sudoeste', 'Nova Olímpia': 'Sudoeste', 'Porto Estrela': 'Sudoeste', 'Tangará da Serra': 'Sudoeste', 'Campos de Júlio': 'Sudoeste',
    'Comodoro': 'Sudoeste', 'Sapezal': 'Sudoeste',

    # CENTRO-SUL
    'Alto Paraguai': 'Centro-Sul', 'Arenápolis': 'Centro-Sul', 'Nortelândia': 'Centro-Sul', 'Nova Marilândia': 'Centro-Sul', 'Santo Afonso': 'Centro-Sul',
    'Acorizal': 'Centro-Sul', 'Jangada': 'Centro-Sul', 'Rosário Oeste': 'Centro-Sul',
    'Chapada dos Guimarães': 'Centro-Sul', 'Cuiabá': 'Centro-Sul', 'Nossa Senhora do Livramento': 'Centro-Sul', 'Santo Antônio de Leverger': 'Centro-Sul', 'Várzea Grande': 'Centro-Sul',
    'Barão de Melgaço': 'Centro-Sul', 'Cáceres': 'Centro-Sul', 'Curvelândia': 'Centro-Sul', 'Poconé': 'Centro-Sul', 'Nova Brasilândia': 'Centro-Sul', 'Diamantino': 'Centro-Sul',
}

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
    top_15_colaboradores = Colaborador.objects.annotate(
        num_convidados=Count('convidados')
    ).order_by('-num_convidados')[:15]

    # --- NOVO CÓDIGO PARA O GRÁFICO DE APOIADORES POR CIDADE ---
    # 1. Conta colaboradores por cidade
    colaboradores_por_cidade = Colaborador.objects.values('cidade__nome_cidade').annotate(total=Count('id'))

    # 2. Conta convidados por cidade
    convidados_por_cidade = Convidado.objects.values('cidade__nome_cidade').annotate(total=Count('id'))

    # 3. Combina os resultados em Python
    dados_cidades = {}
    for item in colaboradores_por_cidade:
        cidade_nome = item['cidade__nome_cidade']
        if cidade_nome:  # Ignora entradas sem cidade
            dados_cidades[cidade_nome] = dados_cidades.get(cidade_nome, 0) + item['total']

    for item in convidados_por_cidade:
        cidade_nome = item['cidade__nome_cidade']
        if cidade_nome:
            dados_cidades[cidade_nome] = dados_cidades.get(cidade_nome, 0) + item['total']

    # 4. Ordena as cidades por maior número de apoiadores e pega o Top 15
    cidades_ordenadas = sorted(dados_cidades.items(), key=lambda item: item[1], reverse=True)[:15]

    # 5. Prepara os dados para o Chart.js
    labels_cidades = [item[0] for item in cidades_ordenadas]
    data_cidades = [item[1] for item in cidades_ordenadas]
    # --- FIM DO NOVO CÓDIGO ---

    # --- NOVO CÓDIGO PARA OS DOIS GRÁFICOS SEPARADOS ---
    # 1. Ranking Top 10 Cidades por NÚMERO DE COLABORADORES
    top_cidades_colaboradores = Colaborador.objects.values(
        'cidade__nome_cidade'
    ).annotate(
        total=Count('id')
    ).order_by('-total').filter(cidade__nome_cidade__isnull=False)[:10]

    labels_cidades_colab = [item['cidade__nome_cidade'] for item in top_cidades_colaboradores]
    data_cidades_colab = [item['total'] for item in top_cidades_colaboradores]

    # 2. Ranking Top 10 Cidades por NÚMERO DE CONVIDADOS
    top_cidades_convidados = Convidado.objects.values(
        'cidade__nome_cidade'
    ).annotate(
        total=Count('id')
    ).order_by('-total').filter(cidade__nome_cidade__isnull=False)[:10]

    labels_cidades_conv = [item['cidade__nome_cidade'] for item in top_cidades_convidados]
    data_cidades_conv = [item['total'] for item in top_cidades_convidados]

    # --- NOVO CÓDIGO PARA O GRÁFICO DE CONVIDADOS POR MESORREGIÃO ---
    # 1. Define as regiões e inicializa os contadores
    regioes = ['Norte', 'Nordeste', 'Sudeste', 'Sudoeste', 'Centro-Sul']
    dados_regioes = {regiao: 0 for regiao in regioes}

    # 2. Busca todos os convidados com a sua cidade
    convidados_qs = Convidado.objects.select_related('cidade').all()

    # 3. Itera em Python para agregar os dados por região
    for convidado in convidados_qs:
        if convidado.cidade and convidado.cidade.nome_cidade in CIDADE_PARA_MESORREGIAO:
            regiao = CIDADE_PARA_MESORREGIAO[convidado.cidade.nome_cidade]
            dados_regioes[regiao] += 1

    dados_regioes_ordenados = dict(sorted(dados_regioes.items(), key=lambda item: item[1], reverse=True))

    # 4. Prepara os dados para o Chart.js
    labels_regioes = list(dados_regioes_ordenados.keys())
    data_regioes = list(dados_regioes_ordenados.values())
    # --- FIM DO NOVO CÓDIGO ---

    # --- NOVO CÓDIGO PARA OS DADOS DO MAPA DE CALOR ---
    # 1. Busca as coordenadas das cidades dos colaboradores
    coords_colaboradores = Colaborador.objects.filter(
        cidade__latitude_cidade__isnull=False
    ).values_list('cidade__latitude_cidade', 'cidade__longitude_cidade')

    # 2. Busca as coordenadas das cidades dos convidados
    coords_convidados = Convidado.objects.filter(
        cidade__latitude_cidade__isnull=False
    ).values_list('cidade__latitude_cidade', 'cidade__longitude_cidade')

    # 3. Combina todas as coordenadas numa única lista para o mapa de calor
    # Opcional: Adicione um "peso" se quiser que colaboradores valham mais que convidados
    heat_data = [[float(lat), float(lon)] for lat, lon in list(coords_colaboradores) + list(coords_convidados)]
    # --- FIM DO NOVO CÓDIGO ---

    context = {
        'nome_colaborador': nome_usuario_logado,
        'colaborador_obj': colaborador_obj, # Passamos o objeto para acesso a outros dados
        'total_colaboradores': total_colaboradores, # <-- Adiciona esta contagem ao contexto
        'total_convidados': total_convidados,
        'dados_abaixo_meta': abaixo_da_meta,
        'dados_na_meta': na_meta,
        'dados_meta_superada': meta_superada,
        'top_15_colaboradores': top_15_colaboradores,
        'labels_cidades_colab': json.dumps(labels_cidades_colab),
        'data_cidades_colab': json.dumps(data_cidades_colab),
        'labels_cidades_conv': json.dumps(labels_cidades_conv),
        'data_cidades_conv': json.dumps(data_cidades_conv),
        'labels_regioes': json.dumps(labels_regioes),
        'data_regioes': json.dumps(data_regioes),
        'dados_regioes': dados_regioes_ordenados,
        'heat_data': json.dumps(heat_data),
 }
    return render(request, 'dashboard.html', context)

@login_required # Protege a view do mapa
def mapa_apoiadores(request):
    coords_colaboradores = Colaborador.objects.filter(cidade__latitude_cidade__isnull=False).values_list(
        'cidade__latitude_cidade', 'cidade__longitude_cidade')
    coords_convidados = Convidado.objects.filter(cidade__latitude_cidade__isnull=False).values_list(
        'cidade__latitude_cidade', 'cidade__longitude_cidade')

    # Combina todas as coordenadas numa única lista
    heat_data = [[float(lat), float(lon)] for lat, lon in list(coords_colaboradores) + list(coords_convidados)]

    context = {
        'heat_data': json.dumps(heat_data)
    }
    return render(request, 'mapa.html', context)



def sobre(request):
    # Futuramente, podemos passar a versão do app dinamicamente aqui
    context = {
        'versao_app': '1.0.0'
    }
    return render(request, 'sobre.html', context)