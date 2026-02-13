from collections import OrderedDict

from django.http import HttpResponse
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
    template_path = "relatorios/relatorios_colaboradores_pdf_moderno.html"

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
        if not ordering_value:
            ordering_value = (
                filter_obj.form.initial.get("ordering")
                if hasattr(filter_obj.form, "initial")
                else None
            )

        if ordering_value and ordering_value in ordering_labels:
            filtros_aplicados.append(f"Ordenar por: {ordering_labels[ordering_value]}")

        # Depois, verificar os outros filtros
        for field_name, filter_field in filter_obj.filters.items():
            if field_name == "ordering":
                continue  # Ja tratado acima
            value = getattr(filter_obj.form, field_name, None)
            if value and value.value():
                display_value = value.value()
                if hasattr(filter_field, "label"):
                    label = filter_field.label
                else:
                    label = (
                        filter_obj.filters[field_name].field.label
                        if hasattr(filter_obj.filters[field_name], "field")
                        else field_name
                    )
                filtros_aplicados.append(f"{label}: {display_value}")

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
        if not ordering_value and hasattr(filter_obj.form, "initial"):
            ordering_value = filter_obj.form.initial.get("ordering")

        if ordering_value and ordering_value in ordering_labels:
            filtros_aplicados.append(f"Ordenar por: {ordering_labels[ordering_value]}")

        # Depois, verificar os outros filtros
        for field_name, filter_field in filter_obj.filters.items():
            if field_name == "ordering":
                continue
            value = getattr(filter_obj.form, field_name, None)
            if value and value.value():
                display_value = value.value()
                if hasattr(filter_field, "label"):
                    label = filter_field.label
                else:
                    label = (
                        filter_obj.filters[field_name].field.label
                        if hasattr(filter_obj.filters[field_name], "field")
                        else field_name
                    )
                filtros_aplicados.append(f"{label}: {display_value}")

    context = {
        "colaboradores": colaborador_queryset,
        "selected_columns": selected_columns,
        "data_geracao": timezone.now(),
        "filtros_aplicados": filtros_aplicados,
    }
    template = get_template(template_path)
    html = template.render(context)
    return HttpResponse(html)
