import re

from django import template

register = template.Library()


@register.filter
def format_telefone(value):
    """
    Formata um número de telefone para o padrão (xx) xxxxx-xxxx
    Remove todos os caracteres não numéricos e aplica a máscara
    """
    if not value:
        return value

    # Remove todos os caracteres não numéricos
    numeros = re.sub(r"\D", "", str(value))

    # Se tem 11 dígitos (celular com DDD)
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    # Se tem 10 dígitos (telefone fixo com DDD)
    if len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    # Se tem menos de 10 dígitos, retorna como está
    return value
