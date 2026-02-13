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


def exportar_colaboradores_pdf(colaborador_queryset, selected_columns):
    # Temporariamente desabilitado devido a incompatibilidade com Python 3.12
    return HttpResponse("Funcionalidade PDF temporariamente indisponível", status=503)

    # template_path = "relatorios/relatorios_colaboradores_pdf.html"
    # context = {
    #     "colaboradores": colaborador_queryset,
    #     "selected_columns": selected_columns,
    #     "data_geracao": timezone.now(),
    # }

    # template = get_template(template_path)
    # html = template.render(context)

    # response = HttpResponse(content_type="application/pdf")
    # response["Content-Disposition"] = (
    #     'attachment; filename="relatorio_colaboradores.pdf"'
    # )

    # pisa_status = pisa.CreatePDF(html, dest=response)
    # if pisa_status.err:
    #     return HttpResponse("Erro ao gerar o PDF", status=500)

    # return response


def imprimir_relatorio_colaboradores(
    colaborador_queryset, selected_columns, filter_obj=None
):
    template_path = "relatorios/relatorios_colaboradores_pdf.html"

    # Gerar lista de filtros aplicados
    filtros_aplicados = []
    if filter_obj:
        for field_name, filter_field in filter_obj.filters.items():
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
