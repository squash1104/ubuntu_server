from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Bairro, Cidade


def get_bairros(request):
    # 1. Pega o ID da cidade que o JavaScript enviou pela URL
    cidade_id = request.GET.get("cidade_id")

    # 2. **ESTA É A LINHA CRÍTICA:** Filtra o modelo Bairro para pegar
    #    SOMENTE os bairros cujo campo 'cidade_id' seja igual ao ID recebido.
    #    Se esta linha estiver como Bairro.objects.all(), esse é o erro.
    bairros = Bairro.objects.filter(cidade_id=cidade_id).order_by("nome_bairro")

    data = list(bairros.values("id", nome=F("nome_bairro")))

    # 3. Retorna apenas a lista já filtrada em formato JSON
    return JsonResponse(data, safe=False)


@require_http_methods(["POST"])
def criar_bairro(request):
    """Endpoint AJAX para criar um novo bairro."""
    import json
    try:
        data = json.loads(request.body)
        nome_bairro = data.get('nome_bairro', '').strip()
        cidade_id = data.get('cidade_id')

        if not nome_bairro:
            return JsonResponse({'success': False, 'error': 'Nome do bairro é obrigatório'}, status=400)

        if not cidade_id:
            return JsonResponse({'success': False, 'error': 'Cidade é obrigatória'}, status=400)

        # Verificar se já existe um bairro com o mesmo nome na mesma cidade
        existing = Bairro.objects.filter(nome_bairro__iexact=nome_bairro, cidade_id=cidade_id).first()
        if existing:
            return JsonResponse({
                'success': False, 
                'error': 'Este bairro já existe nesta cidade',
                'bairro_id': existing.id
            }, status=400)

        # Criar o novo bairro
        bairro = Bairro.objects.create(
            nome_bairro=nome_bairro,
            cidade_id=cidade_id
        )

        return JsonResponse({
            'success': True,
            'bairro': {
                'id': bairro.id,
                'nome': bairro.nome_bairro
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dados inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
