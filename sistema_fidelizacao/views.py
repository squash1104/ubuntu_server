import contextlib
import io
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.utils import timezone
from xhtml2pdf import pisa

from colaboradores.models import Colaborador, TipoColaborador
from convidados.models import Convidado
from geografia.models import Bairro, Cidade

CIDADE_PARA_MESORREGIAO = {
    # NORTE
    "Alta Floresta": "Norte",
    "Apiacás": "Norte",
    "Carlinda": "Norte",
    "Nova Bandeirantes": "Norte",
    "Nova Monte Verde": "Norte",
    "Paranaíta": "Norte",
    "Ipiranga do Norte": "Norte",
    "Itanhangá": "Norte",
    "Lucas do Rio Verde": "Norte",
    "Nobres": "Norte",
    "Nova Mutum": "Norte",
    "Nova Ubiratã": "Norte",
    "Santa Rita do Trivelato": "Norte",
    "Sorriso": "Norte",
    "Tapurah": "Norte",
    "Juara": "Norte",
    "Nova Maringá": "Norte",
    "Novo Horizonte do Norte": "Norte",
    "Porto dos Gaúchos": "Norte",
    "São José do Rio Claro": "Norte",
    "Tabaporã": "Norte",
    "Aripuanã": "Norte",
    "Brasnorte": "Norte",
    "Castanheira": "Norte",
    "Colniza": "Norte",
    "Cotriguaçu": "Norte",
    "Juína": "Norte",
    "Juruena": "Norte",
    "Rondolândia": "Norte",
    "Colíder": "Norte",
    "Guarantã do Norte": "Norte",
    "Matupá": "Norte",
    "Nova Canaã do Norte": "Norte",
    "Nova Guarita": "Norte",
    "Novo Mundo": "Norte",
    "Peixoto de Azevedo": "Norte",
    "Terra Nova do Norte": "Norte",
    "Cláudia": "Norte",
    "Feliz Natal": "Norte",
    "Itaúba": "Norte",
    "Marcelândia": "Norte",
    "Nova Santa Helena": "Norte",
    "Santa Carmem": "Norte",
    "Sinop": "Norte",
    "União do Sul": "Norte",
    "Vera": "Norte",
    # NORDESTE
    "Alto Boa Vista": "Nordeste",
    "Bom Jesus do Araguaia": "Nordeste",
    "Canabrava do Norte": "Nordeste",
    "Confresa": "Nordeste",
    "Luciara": "Nordeste",
    "Novo Santo Antônio": "Nordeste",
    "Porto Alegre do Norte": "Nordeste",
    "Ribeirão Cascalheira": "Nordeste",
    "Santa Cruz do Xingu": "Nordeste",
    "Santa Terezinha": "Nordeste",
    "São Félix do Araguaia": "Nordeste",
    "São José do Xingu": "Nordeste",
    "Serra Nova Dourada": "Nordeste",
    "Vila Rica": "Nordeste",
    "Água Boa": "Nordeste",
    "Campinápolis": "Nordeste",
    "Canarana": "Nordeste",
    "Nova Nazaré": "Nordeste",
    "Nova Xavantina": "Nordeste",
    "Novo São Joaquim": "Nordeste",
    "Querência": "Nordeste",
    "Santo Antônio do Leste": "Nordeste",
    "Araguaiana": "Nordeste",
    "Barra do Garças": "Nordeste",
    "Cocalinho": "Nordeste",
    # SUDESTE
    "Gaúcha do Norte": "Sudeste",
    "Paranatinga": "Sudeste",
    "Planalto da Serra": "Sudeste",
    "Campo Verde": "Sudeste",
    "Dom Aquino": "Sudeste",
    "Itiquira": "Sudeste",
    "Jaciara": "Sudeste",
    "Juscimeira": "Sudeste",
    "Pedra Preta": "Sudeste",
    "Poxoréu": "Sudeste",
    "Primavera do Leste": "Sudeste",
    "Rondonópolis": "Sudeste",
    "São Pedro da Cipa": "Sudeste",
    "General Carneiro": "Sudeste",
    "Pontal do Araguaia": "Sudeste",
    "Tesouro": "Sudeste",
    "Torixoréu": "Sudeste",
    "Guiratinga": "Sudeste",
    "São José do Povo": "Sudeste",
    "Araguainha": "Sudeste",
    "Ponte Branca": "Sudeste",
    "Ribeirãozinho": "Sudeste",
    "Alto Araguaia": "Sudeste",
    "Alto Garças": "Sudeste",
    "Alto Taquari": "Sudeste",
    # SUDOESTE
    "Conquista d" "Oeste": "Sudoeste",
    "Nova Lacerda": "Sudoeste",
    "Pontes e Lacerda": "Sudoeste",
    "Vale de São Domingos": "Sudoeste",
    "Vila Bela da Santíssima Trindade": "Sudoeste",
    "Araputanga": "Sudoeste",
    "Figueirópolis d" "Oeste": "Sudoeste",
    "Glória d" "Oeste": "Sudoeste",
    "Indiavaí": "Sudoeste",
    "Jauru": "Sudoeste",
    "Lambari d" "Oeste": "Sudoeste",
    "Mirassol d" "Oeste": "Sudoeste",
    "Porto Esperidião": "Sudoeste",
    "Reserva do Cabaçal": "Sudoeste",
    "Rio Branco": "Sudoeste",
    "Salto do Céu": "Sudoeste",
    "São José dos Quatro Marcos": "Sudoeste",
    "Barra do Bugres": "Sudoeste",
    "Denise": "Sudoeste",
    "Nova Olímpia": "Sudoeste",
    "Porto Estrela": "Sudoeste",
    "Tangará da Serra": "Sudoeste",
    "Campos de Júlio": "Sudoeste",
    "Comodoro": "Sudoeste",
    "Sapezal": "Sudoeste",
    # CENTRO-SUL
    "Alto Paraguai": "Centro-Sul",
    "Arenápolis": "Centro-Sul",
    "Nortelândia": "Centro-Sul",
    "Nova Marilândia": "Centro-Sul",
    "Santo Afonso": "Centro-Sul",
    "Acorizal": "Centro-Sul",
    "Jangada": "Centro-Sul",
    "Rosário Oeste": "Centro-Sul",
    "Chapada dos Guimarães": "Centro-Sul",
    "Cuiabá": "Centro-Sul",
    "Nossa Senhora do Livramento": "Centro-Sul",
    "Santo Antônio de Leverger": "Centro-Sul",
    "Várzea Grande": "Centro-Sul",
    "Barão de Melgaço": "Centro-Sul",
    "Cáceres": "Centro-Sul",
    "Curvelândia": "Centro-Sul",
    "Poconé": "Centro-Sul",
    "Nova Brasilândia": "Centro-Sul",
    "Diamantino": "Centro-Sul",
}


@login_required
def home(request):
    # Redireciona recepcionistas não-supervisores para a Home da Recepção
    if request.user.is_authenticated:
        grupos = set(request.user.groups.values_list("name", flat=True))
        if (
            "Recepcionista" in grupos
            and "Supervisor" not in grupos
            and not request.user.is_superuser
        ):
            from django.shortcuts import redirect

            return redirect("recepcao:home")
    return render(request, "home.html")


@login_required  # Este decorador garante que apenas usuários logados acessem esta view
def dashboard(request):
    nome_usuario_logado = request.user.username  # Nome padrão para teste
    colaborador_obj = None
    with contextlib.suppress(Colaborador.DoesNotExist):
        colaborador_obj = Colaborador.objects.get(nome__iexact=request.user.username)

    # Calcula total de convidados e colaboradores cadastrados para nossos cards
    total_colaboradores = Colaborador.objects.count()
    total_convidados = Convidado.objects.count()
    total_colaboradores_cuiaba = Colaborador.objects.filter(
        cidade__nome_cidade="Cuiabá"
    ).count()
    total_colaboradores_interior = Colaborador.objects.exclude(
        cidade__nome_cidade="Cuiabá"
    ).count()
    total_convidados_cuiaba = Convidado.objects.filter(
        cidade__nome_cidade="Cuiabá"
    ).count()
    total_convidados_interior = Convidado.objects.exclude(
        cidade__nome_cidade="Cuiabá"
    ).count()

    colaboradores_com_contagem = Colaborador.objects.annotate(
        num_convidados=Count("convidados", distinct=True)
    )

    # Define as nossas metas
    meta = 30

    # Calcula quantos colaboradores estão em cada categoria de meta para grafico rosca
    abaixo_da_meta = colaboradores_com_contagem.filter(num_convidados__lt=meta).count()
    na_meta = colaboradores_com_contagem.filter(num_convidados=meta).count()
    meta_superada = colaboradores_com_contagem.filter(num_convidados__gt=meta).count()
    total_com_meta = abaixo_da_meta + na_meta + meta_superada
    pct_abaixo = (
        round(abaixo_da_meta / total_com_meta * 100, 1) if total_com_meta else 0
    )
    pct_na = round(na_meta / total_com_meta * 100, 1) if total_com_meta else 0
    pct_superada = (
        round(meta_superada / total_com_meta * 100, 1) if total_com_meta else 0
    )

    # Calcula nosso top 10 para grafico
    top_15_colaboradores = (
        Colaborador.objects.select_related("tipo")
        .annotate(num_convidados=Count("convidados", distinct=True))
        .order_by("-num_convidados")[:20]
    )

    # --- NOVO CÓDIGO PARA O GRÁFICO DE APOIADORES POR CIDADE ---
    # 1. Conta colaboradores por cidade
    colaboradores_por_cidade = Colaborador.objects.values(
        "cidade__nome_cidade"
    ).annotate(total=Count("id"))

    # 2. Conta convidados por cidade
    convidados_por_cidade = Convidado.objects.values("cidade__nome_cidade").annotate(
        total=Count("id")
    )

    # 3. Combina os resultados em Python
    dados_cidades = {}
    for item in colaboradores_por_cidade:
        cidade_nome = item["cidade__nome_cidade"]
        if cidade_nome:  # Ignora entradas sem cidade
            dados_cidades[cidade_nome] = (
                dados_cidades.get(cidade_nome, 0) + item["total"]
            )

    for item in convidados_por_cidade:
        cidade_nome = item["cidade__nome_cidade"]
        if cidade_nome:
            dados_cidades[cidade_nome] = (
                dados_cidades.get(cidade_nome, 0) + item["total"]
            )

    # 4. Ordena as cidades por maior número de apoiadores e pega o Top 15
    # cidades_ordenadas = sorted(
    #     dados_cidades.items(), key=lambda item: item[1], reverse=True
    # )[:15]

    # 5. Prepara os dados para o Chart.js (não utilizados atualmente)
    # labels_cidades = [item[0] for item in cidades_ordenadas]
    # data_cidades = [item[1] for item in cidades_ordenadas]
    # --- FIM DO NOVO CÓDIGO ---

    # --- GRÁFICOS: COLABORADORES/CONVIDADOS POR GRUPOS (CAPITAL vs INTERIOR) ---
    capitais = ["Cuiabá", "Várzea Grande"]

    # Colaboradores por grupo
    total_colab_capital = Colaborador.objects.filter(
        cidade__nome_cidade__in=capitais
    ).count()
    # Interior inclui demais cidades e registros sem cidade
    total_colab_interior = Colaborador.objects.exclude(
        cidade__nome_cidade__in=capitais
    ).count()

    labels_cidades_colab = ["Capital", "Interior"]
    data_cidades_colab = [total_colab_capital, total_colab_interior]

    # Convidados por grupo
    total_conv_capital = Convidado.objects.filter(
        cidade__nome_cidade__in=capitais
    ).count()
    # Interior inclui demais cidades e registros sem cidade
    total_conv_interior = Convidado.objects.exclude(
        cidade__nome_cidade__in=capitais
    ).count()

    labels_cidades_conv = ["Capital", "Interior"]
    data_cidades_conv = [total_conv_capital, total_conv_interior]

    # --- NOVOS RANKINGS GEOGRÁFICOS ---
    # Top 15 bairros da capital (Cuiabá) por número de convidados
    top_bairros_capital = (
        Convidado.objects.filter(bairro__cidade__nome_cidade__iexact="Cuiabá")
        .filter(bairro__nome_bairro__isnull=False)
        .values("bairro__nome_bairro")
        .annotate(total=Count("id"))
        .order_by("-total")[:15]
    )
    labels_bairros_capital = [
        item["bairro__nome_bairro"] for item in top_bairros_capital
    ]
    data_bairros_capital = [item["total"] for item in top_bairros_capital]

    # Série de colaboradores para os mesmos bairros (Cuiabá)
    colab_bairros_capital = (
        Colaborador.objects.filter(bairro__cidade__nome_cidade__iexact="Cuiabá")
        .values("bairro__nome_bairro")
        .annotate(total=Count("id", distinct=True))
    )
    colab_bairros_capital_map = {
        item["bairro__nome_bairro"]: item["total"] for item in colab_bairros_capital
    }
    data_bairros_capital_colab = [
        int(colab_bairros_capital_map.get(bairro, 0))
        for bairro in labels_bairros_capital
    ]

    # Top bairro em cada categoria (capital)
    if labels_bairros_capital:
        idx_top_colab_bairro = max(
            range(len(data_bairros_capital_colab)),
            key=lambda i: data_bairros_capital_colab[i],
        )
        idx_top_conv_bairro = max(
            range(len(data_bairros_capital)),
            key=lambda i: data_bairros_capital[i],
        )
        top_bairro_colab_nome = labels_bairros_capital[idx_top_colab_bairro]
        top_bairro_colab_valor = data_bairros_capital_colab[idx_top_colab_bairro]
        top_bairro_conv_nome = labels_bairros_capital[idx_top_conv_bairro]
        top_bairro_conv_valor = data_bairros_capital[idx_top_conv_bairro]
        top_bairro_colab_pct = (
            round(top_bairro_colab_valor / total_colaboradores_cuiaba * 100)
            if total_colaboradores_cuiaba > 0
            else 0
        )
        top_bairro_conv_pct = (
            round(top_bairro_conv_valor / total_convidados_cuiaba * 100)
            if total_convidados_cuiaba > 0
            else 0
        )
    else:
        top_bairro_colab_nome = top_bairro_conv_nome = ""
        top_bairro_colab_pct = top_bairro_conv_pct = 0

    # Top 15 cidades por número de convidados
    top_cidades_interior_conv = (
        Convidado.objects.filter(cidade__nome_cidade__isnull=False)
        .values("cidade__nome_cidade")
        .annotate(total=Count("id"))
        .order_by("-total")[:15]
    )
    labels_cidades_interior = [
        item["cidade__nome_cidade"] for item in top_cidades_interior_conv
    ]
    data_cidades_interior = [item["total"] for item in top_cidades_interior_conv]

    # Série de colaboradores para as mesmas cidades
    colab_cidades_interior = Colaborador.objects.values("cidade__nome_cidade").annotate(
        total=Count("id", distinct=True)
    )
    colab_cidades_interior_map = {
        item["cidade__nome_cidade"]: item["total"] for item in colab_cidades_interior
    }
    data_cidades_interior_colab = [
        int(colab_cidades_interior_map.get(cidade, 0))
        for cidade in labels_cidades_interior
    ]

    # Top cidade em cada categoria (interior)
    if labels_cidades_interior:
        idx_top_colab_cidade = max(
            range(len(data_cidades_interior_colab)),
            key=lambda i: data_cidades_interior_colab[i],
        )
        idx_top_conv_cidade = max(
            range(len(data_cidades_interior)),
            key=lambda i: data_cidades_interior[i],
        )
        top_cidade_colab_nome = labels_cidades_interior[idx_top_colab_cidade]
        top_cidade_colab_valor = data_cidades_interior_colab[idx_top_colab_cidade]
        top_cidade_conv_nome = labels_cidades_interior[idx_top_conv_cidade]
        top_cidade_conv_valor = data_cidades_interior[idx_top_conv_cidade]
        top_cidade_colab_pct = (
            round(top_cidade_colab_valor / total_colaboradores * 100)
            if total_colaboradores > 0
            else 0
        )
        top_cidade_conv_pct = (
            round(top_cidade_conv_valor / total_convidados * 100)
            if total_convidados > 0
            else 0
        )
    else:
        top_cidade_colab_nome = top_cidade_conv_nome = ""
        top_cidade_colab_pct = top_cidade_conv_pct = 0

    # --- NOVO CÓDIGO PARA O GRÁFICO DE CONVIDADOS POR MESORREGIÃO ---
    # 1. Define as regiões e inicializa os contadores
    regioes = ["Norte", "Nordeste", "Sudeste", "Sudoeste", "Centro-Sul"]
    dados_regioes = {regiao: 0 for regiao in regioes}

    # 2. Busca todos os convidados com a sua cidade
    convidados_qs = Convidado.objects.select_related("cidade").all()
    convidados_sem_colaborador = Convidado.objects.filter(
        colaborador__isnull=True
    ).count()

    # 3. Itera em Python para agregar os dados por região
    nao_mapeada = 0
    for convidado in convidados_qs:
        if convidado.cidade and convidado.cidade.nome_cidade in CIDADE_PARA_MESORREGIAO:
            regiao = CIDADE_PARA_MESORREGIAO[convidado.cidade.nome_cidade]
            dados_regioes[regiao] += 1
        else:
            # Contabiliza convidados sem cidade ou cidade não mapeada
            nao_mapeada += 1

    dados_regioes_ordenados = dict(
        sorted(dados_regioes.items(), key=lambda item: item[1], reverse=True)
    )

    # Não incluir bucket de não mapeada/sem cidade no gráfico

    # 4. Conta colaboradores por mesorregião (mesmo mapeamento)
    dados_regioes_colab = {regiao: 0 for regiao in regioes}
    for colaborador in Colaborador.objects.select_related("cidade").all():
        if (
            colaborador.cidade
            and colaborador.cidade.nome_cidade in CIDADE_PARA_MESORREGIAO
        ):
            regiao = CIDADE_PARA_MESORREGIAO[colaborador.cidade.nome_cidade]
            dados_regioes_colab[regiao] += 1

    # 5. Prepara os dados para o Chart.js
    labels_regioes = list(dados_regioes_ordenados.keys())
    data_regioes = list(dados_regioes_ordenados.values())
    data_regioes_colab = [dados_regioes_colab[r] for r in labels_regioes]

    # 6. Regiões com maior concentração
    dados_regioes_colab_ordenados = dict(
        sorted(dados_regioes_colab.items(), key=lambda item: item[1], reverse=True)
    )
    top_regiao_colab = next(iter(dados_regioes_colab_ordenados))
    top_regiao_colab_pct = (
        round(
            dados_regioes_colab_ordenados[top_regiao_colab] / total_colaboradores * 100
        )
        if total_colaboradores > 0
        else 0
    )
    top_regiao_conv = next(iter(dados_regioes_ordenados))
    top_regiao_conv_pct = (
        round(dados_regioes_ordenados[top_regiao_conv] / total_convidados * 100)
        if total_convidados > 0
        else 0
    )
    # --- FIM DO NOVO CÓDIGO ---

    # --- DADOS DO MAPA DE CALOR COM INFO PARA TOOLTIP ---
    # Regra: Cuiabá por bairro; demais cidades por coordenada da cidade
    heat_points = {}

    # Cuiabá por bairro - colaboradores
    colab_por_bairro = (
        Colaborador.objects.filter(
            bairro__latitude_bairro__isnull=False,
            bairro__longitude_bairro__isnull=False,
            bairro__cidade__nome_cidade__iexact="Cuiabá",
        )
        .values(
            "bairro_id",
            "bairro__nome_bairro",
            "bairro__latitude_bairro",
            "bairro__longitude_bairro",
        )
        .annotate(total=Count("id"))
    )
    for item in colab_por_bairro:
        bid = f"b{item['bairro_id']}"
        heat_points[bid] = {
            "lat": float(item["bairro__latitude_bairro"]),
            "lon": float(item["bairro__longitude_bairro"]),
            "nome": item["bairro__nome_bairro"],
            "cidade": "Cuiabá",
            "tipo": "bairro",
            "colaboradores": int(item["total"]),
            "convidados": 0,
        }

    # Cuiabá por bairro - convidados
    conv_por_bairro = (
        Convidado.objects.filter(
            bairro__latitude_bairro__isnull=False,
            bairro__longitude_bairro__isnull=False,
            bairro__cidade__nome_cidade__iexact="Cuiabá",
        )
        .values(
            "bairro_id",
            "bairro__nome_bairro",
            "bairro__latitude_bairro",
            "bairro__longitude_bairro",
        )
        .annotate(total=Count("id"))
    )
    for item in conv_por_bairro:
        bid = f"b{item['bairro_id']}"
        if bid in heat_points:
            heat_points[bid]["convidados"] += int(item["total"])
        else:
            heat_points[bid] = {
                "lat": float(item["bairro__latitude_bairro"]),
                "lon": float(item["bairro__longitude_bairro"]),
                "nome": item["bairro__nome_bairro"],
                "cidade": "Cuiabá",
                "tipo": "bairro",
                "colaboradores": 0,
                "convidados": int(item["total"]),
            }

    # Outras cidades por cidade - colaboradores
    colab_por_cidade = (
        Colaborador.objects.filter(
            cidade__latitude_cidade__isnull=False,
            cidade__longitude_cidade__isnull=False,
        )
        .exclude(cidade__nome_cidade__iexact="Cuiabá")
        .values(
            "cidade_id",
            "cidade__nome_cidade",
            "cidade__latitude_cidade",
            "cidade__longitude_cidade",
        )
        .annotate(total=Count("id"))
    )
    for item in colab_por_cidade:
        cid = f"c{item['cidade_id']}"
        heat_points[cid] = {
            "lat": float(item["cidade__latitude_cidade"]),
            "lon": float(item["cidade__longitude_cidade"]),
            "nome": item["cidade__nome_cidade"],
            "cidade": "",
            "tipo": "cidade",
            "colaboradores": int(item["total"]),
            "convidados": 0,
        }

    # Outras cidades por cidade - convidados
    conv_por_cidade = (
        Convidado.objects.filter(
            cidade__latitude_cidade__isnull=False,
            cidade__longitude_cidade__isnull=False,
        )
        .exclude(cidade__nome_cidade__iexact="Cuiabá")
        .values(
            "cidade_id",
            "cidade__nome_cidade",
            "cidade__latitude_cidade",
            "cidade__longitude_cidade",
        )
        .annotate(total=Count("id"))
    )
    for item in conv_por_cidade:
        cid = f"c{item['cidade_id']}"
        if cid in heat_points:
            heat_points[cid]["convidados"] += int(item["total"])
        else:
            heat_points[cid] = {
                "lat": float(item["cidade__latitude_cidade"]),
                "lon": float(item["cidade__longitude_cidade"]),
                "nome": item["cidade__nome_cidade"],
                "cidade": "",
                "tipo": "cidade",
                "colaboradores": 0,
                "convidados": int(item["total"]),
            }

    # Normalização e montagem da lista final
    pesos = [v["colaboradores"] + v["convidados"] for v in heat_points.values()]
    max_peso = max(pesos) if pesos else 1
    heat_data = [
        {
            "lat": v["lat"],
            "lon": v["lon"],
            "intensity": max(
                ((v["colaboradores"] + v["convidados"]) / max_peso) ** 0.3, 0.25
            ),
            "nome": v["nome"],
            "cidade": v["cidade"],
            "tipo": v["tipo"],
            "colaboradores": v["colaboradores"],
            "convidados": v["convidados"],
        }
        for v in heat_points.values()
    ]
    # --- FIM DOS DADOS DO MAPA DE CALOR ---

    # --- NOVO CÓDIGO PARA OS NOVOS KPIs ---
    # Calcula a eficiência média (média de convidados por colaborador ativo)
    eficiencia_media = 0
    if total_colaboradores > 0:
        eficiencia_media = total_convidados / total_colaboradores
    # --- FIM DO NOVO CÓDIGO ---

    # Contagem de colaboradores e convidados por grupo
    grupos_qs = (
        TipoColaborador.objects.filter(ativo=True)
        .annotate(
            total_colab=Count("colaboradores", distinct=True),
            total_conv=Count("colaboradores__convidados", distinct=True),
        )
        .order_by("-total_colab")
    )
    total_grupos = grupos_qs.count()

    # --- RANKING DE USUÁRIOS ---
    from django.contrib.auth.models import User

    # Busca todos os usuários com suas estatísticas
    ranking_usuarios = []
    usuarios = User.objects.all()

    for usuario in usuarios:
        # Conta colaboradores cadastrados por este usuário
        colaboradores_cadastrados = Colaborador.objects.filter(
            cadastrado_por=usuario
        ).count()

        # Conta convidados cadastrados por este usuário (através dos colaboradores)
        # Convidados: conta uma vez se for por colaborador do usuário OU direto por ele
        from django.db.models import Q

        convidados_cadastrados = (
            Convidado.objects.filter(
                Q(colaborador__cadastrado_por=usuario) | Q(cadastrado_por=usuario)
            )
            .distinct()
            .count()
        )

        # Total de cadastros (colaboradores + convidados)
        total_cadastros = colaboradores_cadastrados + convidados_cadastrados

        ranking_usuarios.append(
            {
                "usuario": usuario,
                "colaboradores": colaboradores_cadastrados,
                "convidados": convidados_cadastrados,
                "total": total_cadastros,
                "username": usuario.username,
                "first_name": usuario.first_name or usuario.username,
            }
        )

    # Ordena por total de cadastros (decrescente)
    ranking_usuarios.sort(key=lambda x: x["total"], reverse=True)

    # Adiciona posição no ranking
    for i, usuario_data in enumerate(ranking_usuarios, 1):
        usuario_data["posicao"] = i

    # Top 3 para destaque
    top_3_usuarios = ranking_usuarios[:3]

    # Posição do usuário logado
    usuario_logado_posicao = None
    for usuario_data in ranking_usuarios:
        if usuario_data["usuario"] == request.user:
            usuario_logado_posicao = usuario_data
            break

    # Função para calcular badges do usuário
    def calcular_badges_usuario(usuario_data):
        badges = []
        total = usuario_data["total"]
        colaboradores = usuario_data["colaboradores"]
        convidados = usuario_data["convidados"]

        # Badges por total de cadastros
        if total >= 1000:
            badges.append(
                {"emoji": "👑", "nome": "Rei dos Cadastros", "cor": "bg-danger"}
            )
        elif total >= 500:
            badges.append({"emoji": "💎", "nome": "Diamante", "cor": "bg-primary"})
        elif total >= 250:
            badges.append({"emoji": "🏆", "nome": "Campeão", "cor": "bg-warning"})
        elif total >= 100:
            badges.append({"emoji": "🥇", "nome": "Ouro", "cor": "bg-warning"})
        elif total >= 50:
            badges.append(
                {"emoji": "⭐", "nome": "Super Cadastrador", "cor": "bg-success"}
            )
        elif total >= 25:
            badges.append({"emoji": "🔥", "nome": "Em Chamas", "cor": "bg-danger"})
        elif total >= 10:
            badges.append({"emoji": "🚀", "nome": "Decolando", "cor": "bg-info"})
        elif total >= 5:
            badges.append({"emoji": "🌱", "nome": "Crescendo", "cor": "bg-success"})
        elif total >= 1:
            badges.append({"emoji": "🌱", "nome": "Iniciante", "cor": "bg-secondary"})
        else:
            badges.append({"emoji": "🌱", "nome": "Novato", "cor": "bg-secondary"})

        # Badges especiais por colaboradores
        if colaboradores >= 50:
            badges.append(
                {"emoji": "👑", "nome": "Rei dos Apoiadores", "cor": "bg-primary"}
            )
        elif colaboradores >= 25:
            badges.append({"emoji": "👥", "nome": "Mentor Master", "cor": "bg-info"})
        elif colaboradores >= 10:
            badges.append(
                {"emoji": "👥", "nome": "Mentor de Apoiadores", "cor": "bg-info"}
            )

        # Badges especiais por convidados
        if convidados >= 500:
            badges.append(
                {"emoji": "🎯", "nome": "Mestre dos Convidados", "cor": "bg-warning"}
            )
        elif convidados >= 250:
            badges.append(
                {"emoji": "🎯", "nome": "Expert em Convidados", "cor": "bg-warning"}
            )
        elif convidados >= 100:
            badges.append(
                {"emoji": "🎯", "nome": "Convidados Master", "cor": "bg-warning"}
            )
        elif convidados >= 50:
            badges.append(
                {
                    "emoji": "🎯",
                    "nome": "Especialista em Convidados",
                    "cor": "bg-warning",
                }
            )

        return badges

    # Badges do usuário logado
    badges_usuario_logado = []
    if usuario_logado_posicao:
        badges_usuario_logado = calcular_badges_usuario(usuario_logado_posicao)
    # --- FIM DO RANKING ---

    context = {
        "nome_colaborador": nome_usuario_logado,
        "colaborador_obj": colaborador_obj,
        # Passamos o objeto para acesso a outros dados
        "total_colaboradores": total_colaboradores,
        "total_convidados": total_convidados,
        "total_colaboradores_cuiaba": total_colaboradores_cuiaba,
        "total_colaboradores_interior": total_colaboradores_interior,
        "total_convidados_cuiaba": total_convidados_cuiaba,
        "total_convidados_interior": total_convidados_interior,
        "dados_abaixo_meta": abaixo_da_meta,
        "dados_na_meta": na_meta,
        "dados_meta_superada": meta_superada,
        "pct_abaixo": pct_abaixo,
        "pct_na": pct_na,
        "pct_superada": pct_superada,
        "top_15_colaboradores": top_15_colaboradores,
        "labels_cidades_colab": json.dumps(labels_cidades_colab),
        "data_cidades_colab": json.dumps(data_cidades_colab),
        "labels_cidades_conv": json.dumps(labels_cidades_conv),
        "data_cidades_conv": json.dumps(data_cidades_conv),
        "labels_regioes": json.dumps(labels_regioes),
        "data_regioes": json.dumps(data_regioes),
        "data_regioes_colab": json.dumps(data_regioes_colab),
        "top_regiao_colab": top_regiao_colab,
        "top_regiao_colab_pct": top_regiao_colab_pct,
        "top_regiao_conv": top_regiao_conv,
        "top_regiao_conv_pct": top_regiao_conv_pct,
        "dados_regioes": dados_regioes_ordenados,
        "heat_data": json.dumps(heat_data),
        # Transparência: convidados sem colaborador (pode explicar diferenças de soma)
        "convidados_sem_colaborador": convidados_sem_colaborador,
        # Novos rankings geográficos
        "labels_bairros_capital": json.dumps(labels_bairros_capital),
        "data_bairros_capital": json.dumps(data_bairros_capital),
        "data_bairros_capital_colab": json.dumps(data_bairros_capital_colab),
        "top_bairro_colab_nome": top_bairro_colab_nome,
        "top_bairro_colab_pct": top_bairro_colab_pct,
        "top_bairro_conv_nome": top_bairro_conv_nome,
        "top_bairro_conv_pct": top_bairro_conv_pct,
        "labels_cidades_interior": json.dumps(labels_cidades_interior),
        "data_cidades_interior": json.dumps(data_cidades_interior),
        "data_cidades_interior_colab": json.dumps(data_cidades_interior_colab),
        "top_cidade_colab_nome": top_cidade_colab_nome,
        "top_cidade_colab_pct": top_cidade_colab_pct,
        "top_cidade_conv_nome": top_cidade_conv_nome,
        "top_cidade_conv_pct": top_cidade_conv_pct,
        # --- NOVOS KPIs ---
        "eficiencia_media": eficiencia_media,
        "grupos_qs": grupos_qs,
        "total_grupos": total_grupos,
        # --- RANKING ---
        "ranking_usuarios": ranking_usuarios,
        "top_3_usuarios": top_3_usuarios,
        "usuario_logado_posicao": usuario_logado_posicao,
        "badges_usuario_logado": badges_usuario_logado,
    }
    return render(request, "dashboard.html", context)


@login_required
def mapa_apoiadores(request):
    heat_points = {}

    # Colaboradores em Cuiabá por bairro
    colab_por_bairro = (
        Colaborador.objects.filter(
            bairro__latitude_bairro__isnull=False,
            bairro__longitude_bairro__isnull=False,
            bairro__cidade__nome_cidade__iexact="Cuiabá",
        )
        .values(
            "bairro_id",
            "bairro__nome_bairro",
            "bairro__latitude_bairro",
            "bairro__longitude_bairro",
        )
        .annotate(total=Count("id"))
    )
    for item in colab_por_bairro:
        bid = f"b{item['bairro_id']}"
        heat_points[bid] = {
            "lat": float(item["bairro__latitude_bairro"]),
            "lon": float(item["bairro__longitude_bairro"]),
            "nome": item["bairro__nome_bairro"],
            "cidade": "Cuiabá",
            "tipo": "bairro",
            "colaboradores": int(item["total"]),
            "convidados": 0,
        }

    # Convidados em Cuiabá por bairro
    conv_por_bairro = (
        Convidado.objects.filter(
            bairro__latitude_bairro__isnull=False,
            bairro__longitude_bairro__isnull=False,
            bairro__cidade__nome_cidade__iexact="Cuiabá",
        )
        .values(
            "bairro_id",
            "bairro__nome_bairro",
            "bairro__latitude_bairro",
            "bairro__longitude_bairro",
        )
        .annotate(total=Count("id"))
    )
    for item in conv_por_bairro:
        bid = f"b{item['bairro_id']}"
        if bid in heat_points:
            heat_points[bid]["convidados"] += int(item["total"])
            heat_points[bid]["nome"] = item["bairro__nome_bairro"]
        else:
            heat_points[bid] = {
                "lat": float(item["bairro__latitude_bairro"]),
                "lon": float(item["bairro__longitude_bairro"]),
                "nome": item["bairro__nome_bairro"],
                "cidade": "Cuiabá",
                "tipo": "bairro",
                "colaboradores": 0,
                "convidados": int(item["total"]),
            }

    # Colaboradores fora de Cuiabá por cidade
    colab_por_cidade = (
        Colaborador.objects.filter(
            cidade__latitude_cidade__isnull=False,
            cidade__longitude_cidade__isnull=False,
        )
        .exclude(cidade__nome_cidade__iexact="Cuiabá")
        .values(
            "cidade_id",
            "cidade__nome_cidade",
            "cidade__latitude_cidade",
            "cidade__longitude_cidade",
        )
        .annotate(total=Count("id"))
    )
    for item in colab_por_cidade:
        cid = f"c{item['cidade_id']}"
        heat_points[cid] = {
            "lat": float(item["cidade__latitude_cidade"]),
            "lon": float(item["cidade__longitude_cidade"]),
            "nome": item["cidade__nome_cidade"],
            "cidade": "",
            "tipo": "cidade",
            "colaboradores": int(item["total"]),
            "convidados": 0,
        }

    # Convidados fora de Cuiabá por cidade
    conv_por_cidade = (
        Convidado.objects.filter(
            cidade__latitude_cidade__isnull=False,
            cidade__longitude_cidade__isnull=False,
        )
        .exclude(cidade__nome_cidade__iexact="Cuiabá")
        .values(
            "cidade_id",
            "cidade__nome_cidade",
            "cidade__latitude_cidade",
            "cidade__longitude_cidade",
        )
        .annotate(total=Count("id"))
    )
    for item in conv_por_cidade:
        cid = f"c{item['cidade_id']}"
        if cid in heat_points:
            heat_points[cid]["convidados"] += int(item["total"])
        else:
            heat_points[cid] = {
                "lat": float(item["cidade__latitude_cidade"]),
                "lon": float(item["cidade__longitude_cidade"]),
                "nome": item["cidade__nome_cidade"],
                "cidade": "",
                "tipo": "cidade",
                "colaboradores": 0,
                "convidados": int(item["total"]),
            }

    # Normalização
    pesos = [v["colaboradores"] + v["convidados"] for v in heat_points.values()]
    max_peso = max(pesos) if pesos else 1
    heat_data = [
        {
            "lat": v["lat"],
            "lon": v["lon"],
            "intensity": max(
                ((v["colaboradores"] + v["convidados"]) / max_peso) ** 0.3, 0.25
            ),
            "nome": v["nome"],
            "cidade": v["cidade"],
            "tipo": v["tipo"],
            "colaboradores": v["colaboradores"],
            "convidados": v["convidados"],
        }
        for v in heat_points.values()
    ]

    context = {"heat_data": json.dumps(heat_data)}
    return render(request, "mapa.html", context)


def sobre(request):
    context = {"versao_app": "1.0.0"}
    return render(request, "sobre.html", context)


@login_required
def apresentacao_pdf(request):
    img_dir = settings.BASE_DIR / "static" / "img" / "apresentacao"

    def img_path(name):
        p = img_dir / name
        return str(p) if p.exists() else ""

    paginas = [
        {
            "nome": "Tela de Login",
            "descricao": (
                "Autenticação segura com proteção contra ataques de força bruta (rate "
                "limiting de 5 tentativas/minuto por IP). Suporte a reset de senha via "
                "e-mail."
            ),
            "descricao_curta": "Autenticação com rate limiting e recuperação de senha",
            "imagem": img_path("01_login.png"),
            "caracteristicas": [
                "Rate limiting: 5 tentativas por minuto por IP",
                "Redirecionamento inteligente (Recepcionistas para Recepção)",
                "Idle timeout com notificação na tela de login",
                "Recuperação de senha via e-mail SMTP",
                "CSRF protection e HTTPS obrigatório em produção",
            ],
        },
        {
            "nome": "Página Inicial",
            "descricao": (
                "Home page do sistema com visão geral e acesso rápido aos principais "
                "módulos."
            ),
            "descricao_curta": "Home com visão geral e navegação principal",
            "imagem": img_path("02_home.png"),
            "caracteristicas": [
                "Cards de atalho para principais funcionalidades",
                "Indicadores resumidos de desempenho",
                "Navegação responsiva com Bootstrap 5",
                "Menu adaptado ao perfil do usuário",
            ],
        },
        {
            "nome": "Dashboard - Mapa de Concentração",
            "descricao": (
                "Mapa de calor interativo (Leaflet.js + Leaflet.heat) mostrando a "
                "distribuição geográfica de apoiadores e convidados em todo o estado. "
                "Cuiabá é detalhada por bairro; demais cidades por coordenada "
                "geográfica."
            ),
            "descricao_curta": (
                "Mapa de calor com distribuição geográfica de apoiadores"
            ),
            "imagem": img_path("03_dashboard_top.png"),
            "caracteristicas": [
                "Gradiente de cores: azul (baixa) até vermelho (alta concentração)",
                "Tooltips com nome, quantidade de apoiadores e convidados",
                "Normalização com transformação exponencial (^0.3) para "
                "melhor visibilidade",
                "Zoom e pan interativos",
            ],
        },
        {
            "nome": "Dashboard - Gráficos Analíticos",
            "descricao": (
                "Conjunto de gráficos Chart.js com dados de desempenho: Convidados por "
                "Região do Estado (dual dataset: apoiadores + convidados), Capital vs "
                "Interior (barras agrupadas), Top 15 Bairros, Top 15 Cidades e "
                "Desempenho por Meta (doughnut)."
            ),
            "descricao_curta": (
                "Gráficos de desempenho por região, capital/interior e rankings"
            ),
            "imagem": img_path("04_dashboard_charts.png"),
            "caracteristicas": [
                "Barras agrupadas com dual dataset (apoiadores + convidados)",
                "ChartDataLabels com valores nas barras",
                "Subtítulos informativos com percentuais",
                "Gráfico de rosca para metas (threshold: 30 convidados)",
                "Ranking Top 20 apoiadores com badges",
            ],
        },
        {
            "nome": "Dashboard - Completo",
            "descricao": (
                "Visão completa do dashboard com todos os indicadores, rankings de "
                "usuários, badges de desempenho e eficiência média."
            ),
            "descricao_curta": "Dashboard completo com KPIs, rankings e badges",
            "imagem": img_path("05_dashboard_full.png"),
            "caracteristicas": [
                "Cards de KPI: total apoiadores, convidados, eficiência média",
                "Ranking de usuários com badges (Ouro, Diamante, etc.)",
                "Desempenho por tipo de colaborador (grupos)",
                "Indicador de convidados sem colaborador vinculado",
            ],
        },
        {
            "nome": "Mapa de Apoiadores",
            "descricao": (
                "Página dedicada ao mapa interativo em tela cheia, com os mesmos dados "
                "do dashboard mas em visualização ampliada para melhor exploração "
                "geográfica."
            ),
            "descricao_curta": "Mapa interativo em tela cheia",
            "imagem": img_path("06_mapa_apoiadores.png"),
            "caracteristicas": [
                "Leaflet.js com tiles OpenStreetMap",
                "Camada de calor (heatLayer) com gradiente azul até vermelho",
                "Markers invisíveis com tooltips em popups",
                "Zoom para nível de rua em Cuiabá (bairros)",
            ],
        },
        {
            "nome": "Lista de Apoiadores",
            "descricao": (
                "Listagem completa de todos os apoiadores cadastrados, com busca, "
                "filtros e paginação. Acesso rápido para editar, excluir ou visualizar "
                "convidados vinculados."
            ),
            "descricao_curta": "CRUD completo de apoiadores com busca e filtros",
            "imagem": img_path("07_colaboradores_lista.png"),
            "caracteristicas": [
                "Busca por nome e telefone",
                "Filtros por tipo de colaborador, cidade e bairro",
                "Paginação integrada",
                "Ações rápidas: editar, excluir, ver convidados",
                "Indicador visual de meta (>=30 convidados)",
            ],
        },
        {
            "nome": "Cadastro de Apoiador",
            "descricao": (
                "Formulário de cadastro com validação de unicidade (nome e telefone "
                "via"
                "AJAX), seleção de cidade/bairro com cascata AJAX, e campos completos "
                "de endereço e contato."
            ),
            "descricao_curta": "Formulário com validação AJAX e cascata cidade/bairro",
            "imagem": img_path("08_colaboradores_form.png"),
            "caracteristicas": [
                "Verificação AJAX de nome e telefone duplicados",
                "Dropdowns em cascata: estado para cidade para bairro",
                "Máscaras de telefone via JavaScript",
                "Suporte a WhatsApp e múltiplos telefones",
            ],
        },
        {
            "nome": "Tipos de Colaborador",
            "descricao": (
                "Gerenciamento dos tipos/grupos de colaboradores (ex: Liderança, "
                "Militante, Simpatizante). CRUD completo com controle de responsáveis "
                "por cada tipo."
            ),
            "descricao_curta": "CRUD de tipos/grupos de colaboradores",
            "imagem": img_path("09_tipos_colaborador.png"),
            "caracteristicas": [
                "Cadastro, edição e exclusão de tipos",
                "Atribuição de responsáveis (usuários gestores)",
                "Controle de acesso por tipo de colaborador",
                "Indicador ativo/inativo",
            ],
        },
        {
            "nome": "Lista de Convidados",
            "descricao": (
                "Listagem de todos os convidados indicados pelos apoiadores, com "
                "vínculo ao colaborador que realizou a indicação. Busca, filtros e "
                "ações de edição/exclusão."
            ),
            "descricao_curta": "CRUD de convidados com vínculo ao apoiador",
            "imagem": img_path("10_convidados_lista.png"),
            "caracteristicas": [
                "Filtros por cidade, bairro e colaborador",
                "Busca por nome e telefone",
                "Visualização do apoiador responsável pela indicação",
                "Exportação para Excel e HTML (impressão)",
            ],
        },
        {
            "nome": "Cadastro de Convidado",
            "descricao": (
                "Formulário de cadastro de convidados com cascata cidade/bairro, "
                "validação AJAX de unicidade e vínculo opcional a um colaborador "
                "existente."
            ),
            "descricao_curta": "Formulário com validação e vínculo ao apoiador",
            "imagem": img_path("11_convidados_form.png"),
            "caracteristicas": [
                "Dropdowns em cascata: cidade para bairro",
                "Verificação AJAX de duplicidade",
                "Vínculo opcional a colaborador",
                "Máscaras de telefone automáticas",
            ],
        },
        {
            "nome": "Recepção - Home",
            "descricao": (
                "Interface simplificada para recepcionistas, com acesso rápido às "
                "funções de atendimento: registro de visitantes, fila de espera e "
                "declarações."
            ),
            "descricao_curta": "Interface do recepcionista com acesso rápido",
            "imagem": img_path("12_recepcao_home.png"),
            "caracteristicas": [
                "Redirecionamento automático para recepcionistas",
                "Acesso rápido a visitantes e fila",
                "Interface simplificada e objetiva",
            ],
        },
        {
            "nome": "Recepção - Dashboard",
            "descricao": (
                "Painel da recepção com indicadores de atendimento, visitantes do dia "
                "e"
                "estatísticas operacionais."
            ),
            "descricao_curta": "Painel de indicadores da recepção",
            "imagem": img_path("13_recepcao_dashboard.png"),
            "caracteristicas": [
                "Métricas de atendimento do dia",
                "Lista de visitantes aguardando",
                "Histórico de atendimentos",
            ],
        },
        {
            "nome": "Recepção - Visitantes",
            "descricao": (
                "Gerenciamento completo de visitantes: cadastro, edição, "
                "encaminhamento"
                "para fila de atendimento e declaração de visita."
            ),
            "descricao_curta": "Gerenciamento de visitantes e fila",
            "imagem": img_path("14_recepcao_visitantes.png"),
            "caracteristicas": [
                "Cadastro e edição de visitantes",
                "Fila de atendimento (chamar próximo)",
                "Declaração de visita em PDF",
                "Anexos aos atendimentos",
            ],
        },
        {
            "nome": "Painel de Mensagens",
            "descricao": (
                "Central de comunicação com integração Twilio (SMS) e WhatsApp Cloud "
                "API (Meta). Envio individual ou em massa, templates e campanhas."
            ),
            "descricao_curta": "Central de comunicação SMS + WhatsApp",
            "imagem": img_path("15_mensagens_painel.png"),
            "caracteristicas": [
                "Envio individual e em massa",
                "Suporte a SMS (Twilio) e WhatsApp (Meta Cloud API)",
                "Templates de mensagens reutilizáveis",
                "Campanhas com agendamento",
                "Upload de imagens para mídia WhatsApp",
            ],
        },
        {
            "nome": "Envio de Mensagens",
            "descricao": (
                "Compositor de mensagens com seleção de destinatários, templates "
                "salvos"
                "e preview antes do envio."
            ),
            "descricao_curta": "Compositor de mensagens com templates",
            "imagem": img_path("16_mensagens_enviar.png"),
            "caracteristicas": [
                "Seleção múltipla de destinatários",
                "Templates de mensagens com variáveis",
                "Upload de imagens e mídia",
                "Confirmação antes do envio",
            ],
        },
        {
            "nome": "Histórico de Mensagens",
            "descricao": (
                "Registro completo de todas as mensagens enviadas, com status de "
                "entrega, data/hora e conteúdo."
            ),
            "descricao_curta": "Registro de mensagens enviadas",
            "imagem": img_path("17_mensagens_historico.png"),
            "caracteristicas": [
                "Filtros por data, status e destinatário",
                "Indicador visual de entrega (enviada, recebida, falha)",
                "Detalhamento por campanha",
                "Reenvio de mensagens",
            ],
        },
        {
            "nome": "Campanhas",
            "descricao": (
                "Gerenciamento de campanhas de comunicação: criação, agendamento, "
                "execução e relatórios de desempenho."
            ),
            "descricao_curta": "Gerenciamento de campanhas de comunicação",
            "imagem": img_path("18_mensagens_campanhas.png"),
            "caracteristicas": [
                "Criação e agendamento de campanhas",
                "Segmentação de público",
                "Relatórios de entrega",
                "Métricas de engajamento",
            ],
        },
        {
            "nome": "Histórico do Sistema",
            "descricao": (
                "Log completo de todas as ações realizadas no sistema (cadastros, "
                "edições, exclusões) com atualização em tempo real via WebSocket."
            ),
            "descricao_curta": "Log de ações com WebSocket em tempo real",
            "imagem": img_path("19_historico.png"),
            "caracteristicas": [
                "Registro automático de todas as ações CRUD",
                "Atualização em tempo real via Django Channels",
                "Filtros por usuário, ação e data",
                "Detalhamento completo de cada evento",
            ],
        },
        {
            "nome": "Aniversariantes",
            "descricao": (
                "Lista de aniversariantes do mês entre apoiadores e convidados, com "
                "opção de envio de mensagens personalizadas de parabéns."
            ),
            "descricao_curta": "Aniversariantes do mês com envio de parabéns",
            "imagem": img_path("20_aniversariantes.png"),
            "caracteristicas": [
                "Agrupamento por mês",
                "Filtro por tipo (apoiador/convidado)",
                "Botão para envio de mensagem de parabéns",
                "Integração com WhatsApp",
            ],
        },
        {
            "nome": "Sobre o Sistema",
            "descricao": (
                "Informações da versão, tecnologias utilizadas e créditos do sistema "
                "SisAps."
            ),
            "descricao_curta": "Informações e versão do sistema",
            "imagem": img_path("21_sobre.png"),
            "caracteristicas": [
                "Versão do sistema",
                "Tecnologias utilizadas (Django, PostgreSQL, etc.)",
                "Links de suporte",
            ],
        },
        {
            "nome": "Relatório de Apoiadores",
            "descricao": (
                "Relatório personalizado com seleção de colunas, filtros avançados "
                "(tipo, cidade, bairro, período) e ordenação. Exportação para Excel e "
                "HTML otimizado para impressão."
            ),
            "descricao_curta": "Relatório personalizado com exportação Excel/HTML",
            "imagem": img_path("22_relatorio_colaboradores.png"),
            "caracteristicas": [
                "Seleção dinâmica de colunas",
                "Filtros por tipo, cidade, bairro e data",
                "Ordenação por qualquer campo",
                "Exportação Excel (openpyxl) e HTML para impressão",
            ],
        },
        {
            "nome": "Relatório de Convidados",
            "descricao": (
                "Relatório de convidados com filtros, seleção de colunas e exportação, "
                "similar ao relatório de apoiadores."
            ),
            "descricao_curta": "Relatório de convidados com exportação",
            "imagem": img_path("23_relatorio_convidados.png"),
            "caracteristicas": [
                "Filtros por cidade, bairro e período",
                "Seleção de colunas para exibição",
                "Exportação Excel e HTML",
                "Vínculo com apoiador",
            ],
        },
        {
            "nome": "Configurações do Usuário",
            "descricao": (
                "Preferências do usuário: dados do perfil, senha, notificações e "
                "permissões de acesso a módulos."
            ),
            "descricao_curta": "Perfil, senha e preferências do usuário",
            "imagem": img_path("24_user_settings.png"),
            "caracteristicas": [
                "Edição de dados pessoais",
                "Alteração de senha",
                "Configuração de notificações",
                "Controle de acesso a módulos (para gestores)",
            ],
        },
        {
            "nome": "Administração Django",
            "descricao": (
                "Interface administrativa nativa do Django para gerenciamento avançado "
                "de usuários, grupos, permissões e dados do sistema."
            ),
            "descricao_curta": "Painel administrativo Django nativo",
            "imagem": img_path("25_admin.png"),
            "caracteristicas": [
                "Gerenciamento de usuários e grupos",
                "Controle de permissões granular",
                "Gerenciamento de todos os modelos do sistema",
                "Logs de ações administrativas",
            ],
        },
    ]

    modulos = [
        {
            "nome": "Apoiadores (Colaboradores)",
            "descricao": (
                "Cadastro completo com tipos, geolocalização por bairro/cidade, "
                "ranking"
                "por convidados indicados e meta de desempenho (30 convidados)."
            ),
        },
        {
            "nome": "Convidados",
            "descricao": (
                "Cadastro de convidados vinculados a apoiadores, com geolocalização e "
                "relatórios exportáveis."
            ),
        },
        {
            "nome": "Dashboard",
            "descricao": (
                "Painel analítico com mapa de calor, gráficos Chart.js, KPIs, rankings "
                "e badges de usuários."
            ),
        },
        {
            "nome": "Recepção",
            "descricao": (
                "Módulo de atendimento presencial com fila de visitantes, declarações "
                "e histórico de atendimentos."
            ),
        },
        {
            "nome": "Mensagens",
            "descricao": (
                "Comunicação multicanal (SMS + WhatsApp) com templates, campanhas e "
                "envio em massa."
            ),
        },
        {
            "nome": "Geografia",
            "descricao": (
                "Cadastro de cidades e bairros com coordenadas geográficas "
                "para mapa de calor."
            ),
        },
        {
            "nome": "Histórico",
            "descricao": (
                "Auditoria completa com WebSocket para atualizações " "em tempo real."
            ),
        },
        {
            "nome": "Aniversariantes",
            "descricao": (
                "Lista de aniversários com integração ao sistema " "de mensagens."
            ),
        },
    ]

    total_apoiadores = Colaborador.objects.count()
    total_convidados = Convidado.objects.count()
    total_cidades = Cidade.objects.count()
    total_bairros = Bairro.objects.count()

    context = {
        "versao": "1.0.0",
        "data_geracao": timezone.now().strftime("%d/%m/%Y %H:%M"),
        "paginas": paginas,
        "modulos": modulos,
        "total_apoiadores": total_apoiadores,
        "total_convidados": total_convidados,
        "total_cidades": total_cidades,
        "total_bairros": total_bairros,
    }

    template = get_template("presentation.html")
    html = template.render(context)

    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("utf-8")), dest=result)

    if pdf.err:
        return HttpResponse(f"Erro ao gerar PDF: {pdf.err}", status=500)

    response = HttpResponse(result.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="sisaps_apresentacao_{timezone.now():%Y%m%d}.pdf"'
    )
    return response
