from collections import OrderedDict

from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

# from xhtml2pdf import pisa  # Temporariamente comentado devido a incompatibilidade com Python 3.12


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


def exportar_convidados_pdf(convidado_queryset, selected_columns):
    # Temporariamente desabilitado devido a incompatibilidade com Python 3.12
    return HttpResponse("Funcionalidade PDF temporariamente indisponível", status=503)

    # print(">>> EXECUTANDO FUNÇÃO PDF (VERSÃO ATUAL) <<<")
    # template_path = "report/guest_report_pdf.html"

    # context = {
    #     "convidados": convidado_queryset,
    #     "data_geracao": timezone.now(),
    #     "selected_columns": selected_columns,
    # }

    # template = get_template(template_path)
    # html = template.render(context)

    # result_file = BytesIO()
    # pisa_status = pisa.CreatePDF(html, dest=result_file)

    # if pisa_status.err:
    #     return HttpResponse(f"Erro ao gerar PDF: <pre>{html}</pre>", status=400)

    # response = HttpResponse(result_file.getvalue(), content_type="application/pdf")
    # response["Content-Disposition"] = 'inline; filename="relatorio_convidados.pdf"'
    # return response


def imprimir_relatorio(convidado_queryset, selected_columns):
    print(">>> EXECUTANDO FUNÇÃO IMPRIMIR (VERSÃO ATUAL) <<<")
    template_path = "report/guest_report_pdf.html"
    context = {
        "convidados": convidado_queryset,
        "data_geracao": timezone.now(),
        "selected_columns": selected_columns,
    }
    template = get_template(template_path)
    html = template.render(context)
    response = HttpResponse(html, content_type="text/html")
    response["Content-Disposition"] = 'inline; filename="imprimir_relatorio.html"'
    return response
