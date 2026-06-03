from collections import OrderedDict

from django.http import HttpResponse

from .models import TipoColaborador


def tipos_do_usuario(user):
    """Retorna QuerySet de TipoColaborador que o user pode gerenciar"""
    if user.is_superuser:
        return TipoColaborador.objects.filter(ativo=True)
    return TipoColaborador.objects.filter(responsaveis=user, ativo=True)


def usuario_e_gestor(user):
    """True se é gestor de grupo (não superuser, mas responsável por ao menos um tipo)"""
    return (
        user.is_authenticated
        and not user.is_superuser
        and TipoColaborador.objects.filter(responsaveis=user, ativo=True).exists()
    )


def verificar_acesso_modulo(user, modulo):
    """Verifica se user tem acesso a um módulo restrito.
    Retorna (permitido, mensagem_erro)."""
    if user.is_superuser:
        return True, ""
    if not usuario_e_gestor(user):
        return True, ""
    try:
        profile = user.profile
    except Exception:
        return False, "Perfil de usuário não encontrado."
    flags = {
        "aniversariantes": profile.acesso_aniversariantes,
        "mensagens": profile.acesso_mensagens,
        "historico": profile.acesso_historico,
    }
    if flags.get(modulo):
        return True, ""
    return False, "Acesso restrito. Você não tem permissão para acessar este módulo."


from django.template.loader import get_template
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

# from xhtml2pdf import pisa  # Temporariamente comentado
# devido a incompatibilidade com Python 3.12


def exportar_colaboradores_excel(colaborador_queryset, selected_columns):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        "attachment; filename=relatorio_colaboradores.xlsx"
    )

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Relatório de Colaboradores"

    column_headers = OrderedDict(
        [
            ("nome", "Nome"),
            ("telefone", "Telefone"),
            ("cidade", "Cidade"),
            ("bairro", "Bairro"),
            ("total_convidados", "Convidados"),
            ("data_cadastro", "Data Cadastro"),
        ]
    )

    headers = [column_headers[col] for col in selected_columns if col in column_headers]
    sheet.append(headers)

    header_font = Font(bold=True)
    for cell in sheet[1]:
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    for colaborador in colaborador_queryset:
        row_data = []
        for col in selected_columns:
            if col == "cidade":
                row_data.append(str(colaborador.cidade) if colaborador.cidade else "")
            elif col == "bairro":
                row_data.append(str(colaborador.bairro) if colaborador.bairro else "")
            elif col == "total_convidados":
                row_data.append(colaborador.total_convidados)
            elif col == "tipo":
                row_data.append(colaborador.tipo.nome if colaborador.tipo else "")
            elif col == "data_cadastro":
                row_data.append(
                    colaborador.data_cadastro.strftime("%Y-%m-%d %H:%M:%S")
                    if colaborador.data_cadastro
                    else ""
                )
            else:
                row_data.append(getattr(colaborador, col, ""))
        sheet.append(row_data)

    workbook.save(response)
    return response


def exportar_colaboradores_pdf(colaborador_queryset, selected_columns, filter_obj=None):
    """
    Gera um arquivo HTML otimizado para impressao/salvar como PDF.
    O usuario pode abrir no navegador e salvar como PDF.
    """
    template_path = "relatorios/relatorios_colaboradores_pdf_otimizado.html"

    # Mapeamento de valores de ordenacao para labels legiveis
    ordering_labels = {
        "nome": "Nome (A-Z)",
        "-nome": "Nome (Z-A)",
        "cidade__nome_cidade": "Cidade (A-Z)",
        "-cidade__nome_cidade": "Cidade (Z-A)",
        "bairro__nome_bairro": "Bairro (A-Z)",
        "-bairro__nome_bairro": "Bairro (Z-A)",
        "total_convidados": "Convidados (Menor para Maior)",
        "-total_convidados": "Convidados (Maior para Menor)",
        "data_cadastro": "Data (Mais antiga)",
        "-data_cadastro": "Data (Mais recente)",
    }

    # Gerar lista de filtros aplicados
    filtros_aplicados = []
    if filter_obj:
        # Primeiro, verificar o campo de ordenacao
        ordering_value = (
            filter_obj.form.cleaned_data.get("ordering")
            if hasattr(filter_obj.form, "cleaned_data")
            else None
        )
        # ordering_value pode ser lista ou tuple, converter para string
        if ordering_value and isinstance(ordering_value, list | tuple):
            ordering_value = ordering_value[0] if ordering_value else None
        if not ordering_value:
            ordering_value = (
                filter_obj.form.initial.get("ordering")
                if hasattr(filter_obj.form, "initial")
                else None
            )
            # Tambem pode ser lista ou tuple
            if ordering_value and isinstance(ordering_value, list | tuple):
                ordering_value = ordering_value[0] if ordering_value else None

        if ordering_value and ordering_value in ordering_labels:
            filtros_aplicados.append(f"Ordenar por: {ordering_labels[ordering_value]}")

        # Depois, verificar os outros filtros
        if filter_obj.form.is_valid():
            for field_name, filter_field in filter_obj.filters.items():
                if field_name == "ordering":
                    continue
                cleaned = filter_obj.form.cleaned_data.get(field_name)
                if cleaned is None or cleaned == "" or cleaned == [] or cleaned == ():
                    continue
                label = filter_field.label or field_name
                if hasattr(cleaned, "strftime"):
                    display = cleaned.strftime("%d/%m/%Y")
                elif hasattr(cleaned, "pk"):
                    display = str(cleaned)
                else:
                    choices = getattr(getattr(filter_field, "field", None), "choices", None)
                    if choices:
                        display = dict(choices).get(cleaned, str(cleaned))
                    else:
                        display = str(cleaned)
                filtros_aplicados.append(f"{label}: {display}")

    context = {
        "colaboradores": colaborador_queryset,
        "selected_columns": selected_columns,
        "data_geracao": timezone.now(),
        "filtros_aplicados": filtros_aplicados,
    }
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(html, content_type="text/html")
    response["Content-Disposition"] = 'inline; filename="relatorio_colaboradores.html"'
    return response


def imprimir_relatorio_colaboradores(
    colaborador_queryset, selected_columns, filter_obj=None
):
    template_path = "relatorios/relatorios_colaboradores_pdf.html"

    # Mapeamento de valores de ordenacao para labels legiveis
    ordering_labels = {
        "nome": "Nome (A-Z)",
        "-nome": "Nome (Z-A)",
        "cidade__nome_cidade": "Cidade (A-Z)",
        "-cidade__nome_cidade": "Cidade (Z-A)",
        "bairro__nome_bairro": "Bairro (A-Z)",
        "-bairro__nome_bairro": "Bairro (Z-A)",
        "total_convidados": "Convidados (Menor para Maior)",
        "-total_convidados": "Convidados (Maior para Menor)",
        "data_cadastro": "Data (Mais antiga)",
        "-data_cadastro": "Data (Mais recente)",
    }

    # Gerar lista de filtros aplicados
    filtros_aplicados = []
    if filter_obj:
        # Primeiro, verificar o campo de ordenacao
        ordering_value = None
        if hasattr(filter_obj.form, "cleaned_data"):
            ordering_value = filter_obj.form.cleaned_data.get("ordering")
        # ordering_value pode ser lista ou tuple, converter para string
        if ordering_value and isinstance(ordering_value, list | tuple):
            ordering_value = ordering_value[0] if ordering_value else None
        if not ordering_value and hasattr(filter_obj.form, "initial"):
            ordering_value = filter_obj.form.initial.get("ordering")
            if ordering_value and isinstance(ordering_value, list | tuple):
                ordering_value = ordering_value[0] if ordering_value else None

        if ordering_value and ordering_value in ordering_labels:
            filtros_aplicados.append(f"Ordenar por: {ordering_labels[ordering_value]}")

        # Depois, verificar os outros filtros
        if filter_obj.form.is_valid():
            for field_name, filter_field in filter_obj.filters.items():
                if field_name == "ordering":
                    continue
                cleaned = filter_obj.form.cleaned_data.get(field_name)
                if cleaned is None or cleaned == "" or cleaned == [] or cleaned == ():
                    continue
                label = filter_field.label or field_name
                if hasattr(cleaned, "strftime"):
                    display = cleaned.strftime("%d/%m/%Y")
                elif hasattr(cleaned, "pk"):
                    display = str(cleaned)
                else:
                    choices = getattr(getattr(filter_field, "field", None), "choices", None)
                    if choices:
                        display = dict(choices).get(cleaned, str(cleaned))
                    else:
                        display = str(cleaned)
                filtros_aplicados.append(f"{label}: {display}")

    context = {
        "colaboradores": colaborador_queryset,
        "selected_columns": selected_columns,
        "data_geracao": timezone.now(),
        "filtros_aplicados": filtros_aplicados,
    }
    template = get_template(template_path)
    html = template.render(context)
    return HttpResponse(html)
