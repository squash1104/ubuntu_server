from collections import OrderedDict
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import CharField, F, Q, Value
from django.shortcuts import redirect, render

from colaboradores.models import Colaborador, TipoColaborador
from colaboradores.utils import verificar_acesso_modulo
from convidados.models import Convidado


@login_required
def aniversariantes_view(request):
    permitido, erro = verificar_acesso_modulo(request.user, "aniversariantes")
    if not permitido:
        messages.error(request, erro)
        return redirect("home")
    # Filtros
    mes = request.GET.get("mes")  # 1-12
    tipo = request.GET.get("tipo", "todos")  # 'colaboradores' | 'convidados' | 'todos'
    grupo = request.GET.get("grupo", "")
    hoje = date.today()

    # Lista de meses em português
    meses_nomes = [
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    ]
    meses_lista = list(range(1, 13))
    mes_int = None
    if mes and mes.isdigit():
        mes_int = int(mes)

    colabs_base = Colaborador.objects.select_related(
        "cidade", "bairro", "tipo"
    ).exclude(data_nascimento__isnull=True)

    if grupo and grupo.isdigit():
        colabs_base = colabs_base.filter(tipo_id=int(grupo))

    convs_base = Convidado.objects.select_related(
        "cidade", "bairro", "colaborador", "colaborador__tipo"
    ).exclude(data_nascimento__isnull=True)

    def serialize_colabs(qs):
        rows = list(
            qs.annotate(
                tipo_registro=Value("colaborador", output_field=CharField()),
                colaborador_nome=Value("", output_field=CharField()),
            )
            .values(
                "nome",
                "telefone",
                "cidade__nome_cidade",
                "bairro__nome_bairro",
                "tipo_registro",
                "colaborador_nome",
                "data_nascimento",
                "tipo__nome",
                "tipo__cor",
            )
            .order_by("data_nascimento__month", "data_nascimento__day", "nome")
        )
        for r in rows:
            dn = r.get("data_nascimento")
            if dn:
                aniversario_este_ano = dn.replace(year=hoje.year)
                idade = hoje.year - dn.year
                if aniversario_este_ano < hoje:
                    idade += 1
                r["idade"] = (
                    hoje.year - dn.year if aniversario_este_ano == hoje else idade
                )
            else:
                r["idade"] = None
        return rows

    def serialize_convs(qs):
        rows = list(
            qs.annotate(
                tipo_registro=Value("convidado", output_field=CharField()),
                colaborador_nome=F("colaborador__nome"),
            )
            .values(
                "nome",
                "telefone",
                "cidade__nome_cidade",
                "bairro__nome_bairro",
                "tipo_registro",
                "colaborador_nome",
                "data_nascimento",
                "colaborador__tipo__nome",
                "colaborador__tipo__cor",
            )
            .order_by("data_nascimento__month", "data_nascimento__day", "nome")
        )
        for r in rows:
            dn = r.get("data_nascimento")
            if dn:
                aniversario_este_ano = dn.replace(year=hoje.year)
                idade = hoje.year - dn.year
                if aniversario_este_ano < hoje:
                    idade += 1
                r["idade"] = (
                    hoje.year - dn.year if aniversario_este_ano == hoje else idade
                )
            else:
                r["idade"] = None
        return rows

    # Aniversariantes do dia
    filtro_dia = Q(data_nascimento__day=hoje.day, data_nascimento__month=hoje.month)
    aniv_dia_all = serialize_colabs(colabs_base.filter(filtro_dia)) + serialize_convs(
        convs_base.filter(filtro_dia)
    )
    if tipo == "colaboradores":
        aniversariantes_hoje = [
            r for r in aniv_dia_all if r["tipo_registro"] == "colaborador"
        ]
    elif tipo == "convidados":
        aniversariantes_hoje = [
            r for r in aniv_dia_all if r["tipo_registro"] == "convidado"
        ]
    else:
        aniversariantes_hoje = aniv_dia_all

    # Próximo dia
    amanha = hoje + timedelta(days=1)
    proximos_amanha = []
    proximos_amanha += serialize_colabs(
        colabs_base.filter(
            data_nascimento__day=amanha.day, data_nascimento__month=amanha.month
        )
    )
    proximos_amanha += serialize_convs(
        convs_base.filter(
            data_nascimento__day=amanha.day, data_nascimento__month=amanha.month
        )
    )

    if tipo == "colaboradores":
        proximos_amanha = [
            r for r in proximos_amanha if r["tipo_registro"] == "colaborador"
        ]
    elif tipo == "convidados":
        proximos_amanha = [
            r for r in proximos_amanha if r["tipo_registro"] == "convidado"
        ]

    # Filtrar por mês (opcional) - agrupados por data
    lista_mes_por_data = {}
    lista_todos_meses = {}
    lista_meses_circular = OrderedDict()
    lista_anteriores = OrderedDict()
    if mes_int:
        lista_mes_all = serialize_colabs(
            colabs_base.filter(data_nascimento__month=mes_int)
        ) + serialize_convs(convs_base.filter(data_nascimento__month=mes_int))
        if tipo == "colaboradores":
            lista_mes_all = [
                r for r in lista_mes_all if r["tipo_registro"] == "colaborador"
            ]
        elif tipo == "convidados":
            lista_mes_all = [
                r for r in lista_mes_all if r["tipo_registro"] == "convidado"
            ]

        for item in lista_mes_all:
            if item.get("data_nascimento"):
                data_aniv = item["data_nascimento"]
                data_str = data_aniv.strftime("%d/%m")
                if data_str not in lista_mes_por_data:
                    lista_mes_por_data[data_str] = []
                lista_mes_por_data[data_str].append(item)

        lista_mes_por_data = OrderedDict(
            sorted(
                lista_mes_por_data.items(),
                key=lambda kv: datetime.strptime(kv[0], "%d/%m").timetuple().tm_yday,
            )
        )
    else:
        # Quando NÃO há filtro de mês específico: mostra todos os meses
        # em ordem circular a partir do mês atual
        lista_all = serialize_colabs(colabs_base) + serialize_convs(convs_base)
        if tipo == "colaboradores":
            lista_all = [r for r in lista_all if r["tipo_registro"] == "colaborador"]
        elif tipo == "convidados":
            lista_all = [r for r in lista_all if r["tipo_registro"] == "convidado"]

        for item in lista_all:
            dn = item.get("data_nascimento")
            if not dn:
                continue
            mes_item = dn.month
            data_str = dn.strftime("%d/%m")
            if mes_item not in lista_todos_meses:
                lista_todos_meses[mes_item] = {}
            if data_str not in lista_todos_meses[mes_item]:
                lista_todos_meses[mes_item][data_str] = []
            lista_todos_meses[mes_item][data_str].append(item)

        # Ordenar meses em ordem circular (a partir do mês atual)
        mes_atual = hoje.month

        def chave_circular(item):
            m = item[0]
            return (m - mes_atual) % 12

        lista_todos_meses = OrderedDict(
            sorted(lista_todos_meses.items(), key=chave_circular)
        )

        # Ordenar datas dentro de cada mês por dia do ano (crescente)
        for m in list(lista_todos_meses.keys()):
            datas_dict = lista_todos_meses[m]
            lista_todos_meses[m] = OrderedDict(
                sorted(
                    datas_dict.items(),
                    key=lambda kv: datetime.strptime(kv[0], "%d/%m")
                    .timetuple()
                    .tm_yday,
                )
            )

        # Separar meses: circulares (mes_atual-Dez) e anteriores (Jan-mes_atual-1)
        lista_meses_circular = OrderedDict()
        lista_anteriores = OrderedDict()
        mes_atual = hoje.month

        for mes_num in sorted(lista_todos_meses.keys()):
            if mes_num >= mes_atual:
                lista_meses_circular[mes_num] = lista_todos_meses[mes_num]
            else:
                lista_anteriores[mes_num] = lista_todos_meses[mes_num]

        # Dividir mês atual: futuros/hoje para circular,
        # passados para anteriores
        if mes_atual in lista_meses_circular:
            datas_dict = lista_meses_circular[mes_atual]
            datas_futuras = OrderedDict()
            datas_passadas = OrderedDict()
            for data_str, pessoas in datas_dict.items():
                day = int(data_str.split("/")[0])
                if day >= hoje.day:
                    datas_futuras[data_str] = pessoas
                else:
                    datas_passadas[data_str] = pessoas
            if datas_futuras:
                lista_meses_circular[mes_atual] = datas_futuras
            else:
                del lista_meses_circular[mes_atual]
            if datas_passadas:
                lista_anteriores[mes_atual] = datas_passadas

    context = {
        "hoje_str": hoje.strftime("%d/%m"),
        "aniversariantes_hoje": aniversariantes_hoje,
        "proximos_amanha": proximos_amanha,
        "proximos_amanha_data": amanha.strftime("%d/%m"),
        "lista_mes_por_data": lista_mes_por_data,
        "lista_meses_circular": lista_meses_circular,
        "lista_anteriores": lista_anteriores,
        "mes": mes,
        "mes_int": mes_int,
        "sem_filtro_mes": True,
        "meses_lista": meses_lista,
        "meses_nomes": meses_nomes,
        "tipo": tipo,
        "grupo_id": grupo,
        "tipos_colaborador": TipoColaborador.objects.filter(ativo=True),
    }
    return render(request, "aniversarios/aniversariantes.html", context)
