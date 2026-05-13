import contextlib
import json

from django.contrib.auth.decorators import login_required  # Importe este decorador
from django.db.models import Count
from django.shortcuts import render

from colaboradores.models import (  # Importe o modelo Colaborador
    Colaborador,
    TipoColaborador,
)
from convidados.models import Convidado

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

    colaboradores_com_contagem = Colaborador.objects.annotate(
        num_convidados=Count("convidados", distinct=True)
    )

    # Define as nossas metas
    meta = 20

    # Calcula quantos colaboradores estão em cada categoria de meta para grafico rosca
    abaixo_da_meta = colaboradores_com_contagem.filter(num_convidados__lt=meta).count()
    na_meta = colaboradores_com_contagem.filter(num_convidados=meta).count()
    meta_superada = colaboradores_com_contagem.filter(num_convidados__gt=meta).count()

    # Calcula nosso top 10 para grafico
    top_15_colaboradores = Colaborador.objects.annotate(
        num_convidados=Count("convidados", distinct=True)
    ).order_by("-num_convidados")[:15]

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

    # Top 15 cidades do interior por número de convidados
    top_cidades_interior_conv = (
        Convidado.objects.exclude(cidade__nome_cidade__in=["Cuiabá", "Várzea Grande"])
        .filter(cidade__nome_cidade__isnull=False)
        .values("cidade__nome_cidade")
        .annotate(total=Count("id"))
        .order_by("-total")[:15]
    )
    labels_cidades_interior = [
        item["cidade__nome_cidade"] for item in top_cidades_interior_conv
    ]
    data_cidades_interior = [item["total"] for item in top_cidades_interior_conv]

    # Série de colaboradores para as mesmas cidades do interior
    colab_cidades_interior = (
        Colaborador.objects.exclude(cidade__nome_cidade__in=["Cuiabá", "Várzea Grande"])
        .values("cidade__nome_cidade")
        .annotate(total=Count("id", distinct=True))
    )
    colab_cidades_interior_map = {
        item["cidade__nome_cidade"]: item["total"] for item in colab_cidades_interior
    }
    data_cidades_interior_colab = [
        int(colab_cidades_interior_map.get(cidade, 0))
        for cidade in labels_cidades_interior
    ]

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

    # 4. Prepara os dados para o Chart.js
    labels_regioes = list(dados_regioes_ordenados.keys())
    data_regioes = list(dados_regioes_ordenados.values())
    # --- FIM DO NOVO CÓDIGO ---

    # --- NOVO CÓDIGO PARA OS DADOS DO MAPA DE CALOR ---
    # Regra: somente Cuiabá por bairro; demais cidades por coordenada da cidade
    heat_by_bairro = {}
    heat_by_cidade = {}

    # Cuiabá por bairro - colaboradores
    colab_por_bairro = (
        Colaborador.objects.filter(
            bairro__latitude_bairro__isnull=False,
            bairro__longitude_bairro__isnull=False,
            bairro__cidade__nome_cidade__iexact="Cuiabá",
        )
        .values("bairro_id", "bairro__latitude_bairro", "bairro__longitude_bairro")
        .annotate(total=Count("id"))
    )
    for item in colab_por_bairro:
        bid = item["bairro_id"]
        heat_by_bairro[bid] = {
            "lat": float(item["bairro__latitude_bairro"]),
            "lon": float(item["bairro__longitude_bairro"]),
            "peso": int(item["total"]),
        }

    # Cuiabá por bairro - convidados
    conv_por_bairro = (
        Convidado.objects.filter(
            bairro__latitude_bairro__isnull=False,
            bairro__longitude_bairro__isnull=False,
            bairro__cidade__nome_cidade__iexact="Cuiabá",
        )
        .values("bairro_id", "bairro__latitude_bairro", "bairro__longitude_bairro")
        .annotate(total=Count("id"))
    )
    for item in conv_por_bairro:
        bid = item["bairro_id"]
        if bid in heat_by_bairro:
            heat_by_bairro[bid]["peso"] += int(item["total"])
        else:
            heat_by_bairro[bid] = {
                "lat": float(item["bairro__latitude_bairro"]),
                "lon": float(item["bairro__longitude_bairro"]),
                "peso": int(item["total"]),
            }

    # Outras cidades por cidade - colaboradores
    colab_por_cidade = (
        Colaborador.objects.filter(
            cidade__latitude_cidade__isnull=False,
            cidade__longitude_cidade__isnull=False,
        )
        .exclude(cidade__nome_cidade__iexact="Cuiabá")
        .values("cidade_id", "cidade__latitude_cidade", "cidade__longitude_cidade")
        .annotate(total=Count("id"))
    )
    for item in colab_por_cidade:
        cid = item["cidade_id"]
        heat_by_cidade[cid] = {
            "lat": float(item["cidade__latitude_cidade"]),
            "lon": float(item["cidade__longitude_cidade"]),
            "peso": int(item["total"]),
        }

    # Outras cidades por cidade - convidados
    conv_por_cidade = (
        Convidado.objects.filter(
            cidade__latitude_cidade__isnull=False,
            cidade__longitude_cidade__isnull=False,
        )
        .exclude(cidade__nome_cidade__iexact="Cuiabá")
        .values("cidade_id", "cidade__latitude_cidade", "cidade__longitude_cidade")
        .annotate(total=Count("id"))
    )
    for item in conv_por_cidade:
        cid = item["cidade_id"]
        if cid in heat_by_cidade:
            heat_by_cidade[cid]["peso"] += int(item["total"])
        else:
            heat_by_cidade[cid] = {
                "lat": float(item["cidade__latitude_cidade"]),
                "lon": float(item["cidade__longitude_cidade"]),
                "peso": int(item["total"]),
            }

    # Normalização conjunta (bairro de Cuiabá + outras cidades)
    pesos = [v["peso"] for v in heat_by_bairro.values()] + [
        v["peso"] for v in heat_by_cidade.values()
    ]
    max_peso = max(pesos) if pesos else 1
    heat_data = [
        [v["lat"], v["lon"], max(v["peso"] / max_peso, 0.1)]
        for v in heat_by_bairro.values()
    ] + [
        [v["lat"], v["lon"], max(v["peso"] / max_peso, 0.1)]
        for v in heat_by_cidade.values()
    ]
    # --- FIM DO NOVO CÓDIGO ---

    # --- NOVO CÓDIGO PARA OS NOVOS KPIs ---
    # Calcula a eficiência média (média de convidados por colaborador ativo)
    eficiencia_media = 0
    colaboradores_ativos = colaboradores_com_contagem.filter(
        num_convidados__gt=0
    ).count()
    if colaboradores_ativos > 0:
        eficiencia_media = total_convidados / colaboradores_ativos
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
                {"emoji": "👑", "nome": "Rei dos Colaboradores", "cor": "bg-primary"}
            )
        elif colaboradores >= 25:
            badges.append({"emoji": "👥", "nome": "Mentor Master", "cor": "bg-info"})
        elif colaboradores >= 10:
            badges.append(
                {"emoji": "👥", "nome": "Mentor de Colaboradores", "cor": "bg-info"}
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
        # <-- Adiciona esta contagem ao contexto
        "total_convidados": total_convidados,
        "dados_abaixo_meta": abaixo_da_meta,
        "dados_na_meta": na_meta,
        "dados_meta_superada": meta_superada,
        "top_15_colaboradores": top_15_colaboradores,
        "labels_cidades_colab": json.dumps(labels_cidades_colab),
        "data_cidades_colab": json.dumps(data_cidades_colab),
        "labels_cidades_conv": json.dumps(labels_cidades_conv),
        "data_cidades_conv": json.dumps(data_cidades_conv),
        "labels_regioes": json.dumps(labels_regioes),
        "data_regioes": json.dumps(data_regioes),
        "dados_regioes": dados_regioes_ordenados,
        "heat_data": json.dumps(heat_data),
        # Transparência: convidados sem colaborador (pode explicar diferenças de soma)
        "convidados_sem_colaborador": convidados_sem_colaborador,
        # Novos rankings geográficos
        "labels_bairros_capital": json.dumps(labels_bairros_capital),
        "data_bairros_capital": json.dumps(data_bairros_capital),
        "data_bairros_capital_colab": json.dumps(data_bairros_capital_colab),
        "labels_cidades_interior": json.dumps(labels_cidades_interior),
        "data_cidades_interior": json.dumps(data_cidades_interior),
        "data_cidades_interior_colab": json.dumps(data_cidades_interior_colab),
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


@login_required  # Protege a view do mapa
def mapa_apoiadores(request):
    # Mistura: Cuiabá por bairro, demais por cidade
    heat_by_bairro = {}
    heat_by_cidade = {}

    colab_por_bairro = (
        Colaborador.objects.filter(
            bairro__latitude_bairro__isnull=False,
            bairro__longitude_bairro__isnull=False,
            bairro__cidade__nome_cidade__iexact="Cuiabá",
        )
        .values("bairro_id", "bairro__latitude_bairro", "bairro__longitude_bairro")
        .annotate(total=Count("id"))
    )
    for item in colab_por_bairro:
        bid = item["bairro_id"]
        heat_by_bairro[bid] = {
            "lat": float(item["bairro__latitude_bairro"]),
            "lon": float(item["bairro__longitude_bairro"]),
            "peso": int(item["total"]),
        }

    conv_por_bairro = (
        Convidado.objects.filter(
            bairro__latitude_bairro__isnull=False,
            bairro__longitude_bairro__isnull=False,
            bairro__cidade__nome_cidade__iexact="Cuiabá",
        )
        .values("bairro_id", "bairro__latitude_bairro", "bairro__longitude_bairro")
        .annotate(total=Count("id"))
    )
    for item in conv_por_bairro:
        bid = item["bairro_id"]
        if bid in heat_by_bairro:
            heat_by_bairro[bid]["peso"] += int(item["total"])
        else:
            heat_by_bairro[bid] = {
                "lat": float(item["bairro__latitude_bairro"]),
                "lon": float(item["bairro__longitude_bairro"]),
                "peso": int(item["total"]),
            }

    colab_por_cidade = (
        Colaborador.objects.filter(
            cidade__latitude_cidade__isnull=False,
            cidade__longitude_cidade__isnull=False,
        )
        .exclude(cidade__nome_cidade__iexact="Cuiabá")
        .values("cidade_id", "cidade__latitude_cidade", "cidade__longitude_cidade")
        .annotate(total=Count("id"))
    )
    for item in colab_por_cidade:
        cid = item["cidade_id"]
        heat_by_cidade[cid] = {
            "lat": float(item["cidade__latitude_cidade"]),
            "lon": float(item["cidade__longitude_cidade"]),
            "peso": int(item["total"]),
        }

    conv_por_cidade = (
        Convidado.objects.filter(
            cidade__latitude_cidade__isnull=False,
            cidade__longitude_cidade__isnull=False,
        )
        .exclude(cidade__nome_cidade__iexact="Cuiabá")
        .values("cidade_id", "cidade__latitude_cidade", "cidade__longitude_cidade")
        .annotate(total=Count("id"))
    )
    for item in conv_por_cidade:
        cid = item["cidade_id"]
        if cid in heat_by_cidade:
            heat_by_cidade[cid]["peso"] += int(item["total"])
        else:
            heat_by_cidade[cid] = {
                "lat": float(item["cidade__latitude_cidade"]),
                "lon": float(item["cidade__longitude_cidade"]),
                "peso": int(item["total"]),
            }

    pesos = [v["peso"] for v in heat_by_bairro.values()] + [
        v["peso"] for v in heat_by_cidade.values()
    ]
    max_peso = max(pesos) if pesos else 1
    heat_data = [
        [v["lat"], v["lon"], max(v["peso"] / max_peso, 0.1)]
        for v in heat_by_bairro.values()
    ] + [
        [v["lat"], v["lon"], max(v["peso"] / max_peso, 0.1)]
        for v in heat_by_cidade.values()
    ]

    context = {"heat_data": json.dumps(heat_data)}
    return render(request, "mapa.html", context)


def sobre(request):
    # Futuramente, podemos passar a versão do app dinamicamente aqui
    context = {"versao_app": "1.0.0"}
    return render(request, "sobre.html", context)
