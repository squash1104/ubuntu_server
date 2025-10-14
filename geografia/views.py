from django.db.models import F
from django.http import JsonResponse

from .models import Bairro


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
