from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Q, Value, CharField, F
from django.shortcuts import render

from colaboradores.models import Colaborador
from convidados.models import Convidado


@login_required
def aniversariantes_view(request):
    # Filtros
    mes = request.GET.get('mes')  # 1-12
    tipo = request.GET.get('tipo', 'todos')  # 'colaboradores' | 'convidados' | 'todos'
    hoje = date.today()
    
    # Lista de meses em português
    meses_nomes = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    meses_lista = list(range(1, 13))
    mes_int = None
    if mes and mes.isdigit():
        mes_int = int(mes)

    colabs_base = (
        Colaborador.objects.select_related('cidade', 'bairro')
        .exclude(data_nascimento__isnull=True)
    )
    convs_base = (
        Convidado.objects.select_related('cidade', 'bairro', 'colaborador')
        .exclude(data_nascimento__isnull=True)
    )

    def serialize_colabs(qs):
        rows = list(
            qs.annotate(
                tipo_registro=Value('colaborador', output_field=CharField()),
                colaborador_nome=Value('', output_field=CharField()),
            )
            .values('nome', 'telefone', 'cidade__nome_cidade', 'bairro__nome_bairro', 'tipo_registro', 'colaborador_nome', 'data_nascimento')
            .order_by('nome')
        )
        for r in rows:
            dn = r.get('data_nascimento')
            if dn:
                aniversario_este_ano = dn.replace(year=hoje.year)
                idade = hoje.year - dn.year
                if aniversario_este_ano < hoje:
                    idade += 1  # idade que fará no próximo aniversário? Para "do dia", calcula idade que está fazendo hoje
                r['idade'] = hoje.year - dn.year if aniversario_este_ano == hoje else idade
            else:
                r['idade'] = None
        return rows

    def serialize_convs(qs):
        rows = list(
            qs.annotate(
                tipo_registro=Value('convidado', output_field=CharField()),
                colaborador_nome=F('colaborador__nome'),
            )
            .values('nome', 'telefone', 'cidade__nome_cidade', 'bairro__nome_bairro', 'tipo_registro', 'colaborador_nome', 'data_nascimento')
            .order_by('nome')
        )
        for r in rows:
            dn = r.get('data_nascimento')
            if dn:
                aniversario_este_ano = dn.replace(year=hoje.year)
                idade = hoje.year - dn.year
                if aniversario_este_ano < hoje:
                    idade += 1
                r['idade'] = hoje.year - dn.year if aniversario_este_ano == hoje else idade
            else:
                r['idade'] = None
        return rows

    # Aniversariantes do dia
    filtro_dia = Q(data_nascimento__day=hoje.day, data_nascimento__month=hoje.month)
    aniv_dia_all = serialize_colabs(colabs_base.filter(filtro_dia)) + serialize_convs(convs_base.filter(filtro_dia))
    if tipo == 'colaboradores':
        aniversariantes_hoje = [r for r in aniv_dia_all if r['tipo_registro'] == 'colaborador']
    elif tipo == 'convidados':
        aniversariantes_hoje = [r for r in aniv_dia_all if r['tipo_registro'] == 'convidado']
    else:
        aniversariantes_hoje = aniv_dia_all

    # Próximos 7 dias - agrupados por data
    proximos_por_data = {}
    for delta in range(1, 8):
        d = hoje + timedelta(days=delta)
        data_str = d.strftime("%d/%m")
        proximos_dia = []
        proximos_dia += serialize_colabs(colabs_base.filter(data_nascimento__day=d.day, data_nascimento__month=d.month))
        proximos_dia += serialize_convs(convs_base.filter(data_nascimento__day=d.day, data_nascimento__month=d.month))
        
        if tipo == 'colaboradores':
            proximos_dia = [r for r in proximos_dia if r['tipo_registro'] == 'colaborador']
        elif tipo == 'convidados':
            proximos_dia = [r for r in proximos_dia if r['tipo_registro'] == 'convidado']
        
        if proximos_dia:
            proximos_por_data[data_str] = proximos_dia

    # Filtrar por mês (opcional) - agrupados por data
    lista_mes_por_data = {}
    if mes_int:
        lista_mes_all = serialize_colabs(colabs_base.filter(data_nascimento__month=mes_int)) + serialize_convs(convs_base.filter(data_nascimento__month=mes_int))
        if tipo == 'colaboradores':
            lista_mes_all = [r for r in lista_mes_all if r['tipo_registro'] == 'colaborador']
        elif tipo == 'convidados':
            lista_mes_all = [r for r in lista_mes_all if r['tipo_registro'] == 'convidado']
        
        # Agrupar por data de aniversário
        for item in lista_mes_all:
            if item.get('data_nascimento'):
                data_aniv = item['data_nascimento']
                data_str = data_aniv.strftime("%d/%m")
                if data_str not in lista_mes_por_data:
                    lista_mes_por_data[data_str] = []
                lista_mes_por_data[data_str].append(item)

    context = {
        "hoje_str": hoje.strftime("%d/%m/%Y"),
        "aniversariantes_hoje": aniversariantes_hoje,
        "proximos_por_data": proximos_por_data,
        "lista_mes_por_data": lista_mes_por_data,
        "mes": mes,
        "mes_int": mes_int,
        "meses_lista": meses_lista,
        "meses_nomes": meses_nomes,
        "tipo": tipo,
    }
    return render(request, 'aniversarios/aniversariantes.html', context)
