from collections import OrderedDict

from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

# from xhtml2pdf import pisa  # Temporariamente comentario
# devido a incompatibilidade com Python 3.12


def exportar_convidados_excel(convidado_queryset, selected_columns):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="relatorio_convidados.xlsx"'

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Convidados"

    column_headers = OrderedDict(
        [
            ("nome", "Nome"),
            ("telefone", "Telefone"),
            ("cidade", "Cidade"),
            ("bairro", "Bairro"),
            ("convidado_por", "Convidado por"),
            ("data_cadastro", "Data Cadastro"),
        ]
    )

    headers = [column_headers[col] for col in selected_columns if col in column_headers]
    sheet.append(headers)

    header_font = Font(bold=True)
    for cell in sheet[1]:
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    # Dynamic data
    for convidado in convidado_queryset:
        row_data = []
        for col in selected_columns:
            if col == "cidade":
                row_data.append(str(convidado.cidade) if convidado.cidade else "")
            elif col == "bairro":
                row_data.append(str(convidado.bairro) if convidado.bairro else "")
            elif col == "convidado_por":
                row_data.append(
                    convidado.colaborador.nome if convidado.colaborador else ""
                )
            elif col == "data_cadastro":
                row_data.append(
                    convidado.data_cadastro.strftime("%Y-%m-%d %H:%M:%S")
                    if convidado.data_cadastro
                    else ""
                )
            else:
                row_data.append(getattr(convidado, col, ""))
        sheet.append(row_data)

    workbook.save(response)
    return response


def exportar_convidados_pdf(convidado_queryset, selected_columns, filter_obj=None):
    """
    Gera um arquivo HTML otimizado para impressao/salvar como PDF.
    O usuario pode abrir no navegador e salvar como PDF.
    """
    template_path = "report/guest_report_pdf_otimizado.html"

    # Mapeamento de valores de ordenacao para labels legiveis
    ordering_labels = {
        "nome": "Nome (A-Z)",
        "-nome": "Nome (Z-A)",
        "cidade__nome_cidade": "Cidade (A-Z)",
        "-cidade__nome_cidade": "Cidade (Z-A)",
        "bairro__nome_bairro": "Bairro (A-Z)",
        "-bairro__nome_bairro": "Bairro (Z-A)",
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
        "convidados": convidado_queryset,
        "data_geracao": timezone.now(),
        "selected_columns": selected_columns,
        "filtros_aplicados": filtros_aplicados,
    }
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(html, content_type="text/html")
    response["Content-Disposition"] = 'inline; filename="relatorio_convidados.html"'
    return response


def imprimir_relatorio(convidado_queryset, selected_columns, filter_obj=None):
    print(">>> EXECUTANDO FUNÇÃO IMPRIMIR (VERSÃO ATUAL) <<<")
    template_path = "report/guest_report_pdf.html"

    # Mapeamento de valores de ordenacao para labels legiveis
    ordering_labels = {
        "nome": "Nome (A-Z)",
        "-nome": "Nome (Z-A)",
        "cidade__nome_cidade": "Cidade (A-Z)",
        "-cidade__nome_cidade": "Cidade (Z-A)",
        "bairro__nome_bairro": "Bairro (A-Z)",
        "-bairro__nome_bairro": "Bairro (Z-A)",
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
        "convidados": convidado_queryset,
        "data_geracao": timezone.now(),
        "selected_columns": selected_columns,
        "filtros_aplicados": filtros_aplicados,
    }
    template = get_template(template_path)
    html = template.render(context)
    response = HttpResponse(html, content_type="text/html")
    response["Content-Disposition"] = 'inline; filename="imprimir_relatorio.html"'
    return response
