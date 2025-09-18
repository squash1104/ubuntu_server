from colaboradores.models import Colaborador
from convidados.models import Convidado


def user_badges(request):
    """
    Context processor para adicionar badges do usuário logado em todos os templates
    """
    if not request.user.is_authenticated:
        return {"badges_usuario_logado": []}

    # Busca estatísticas do usuário
    colaboradores_cadastrados = Colaborador.objects.filter(
        cadastrado_por=request.user
    ).count()
    convidados_cadastrados = Convidado.objects.filter(
        colaborador__cadastrado_por=request.user
    ).count()
    total_cadastros = colaboradores_cadastrados + convidados_cadastrados

    # Função para calcular badges do usuário
    def calcular_badges_usuario(total, colaboradores, convidados):
        badges = []

        # Badges por total de cadastros
        if total >= 1000:
            badges.append(
                {"emoji": "👑", "nome": "Rei dos Cadastros", "cor": "bg-danger"}
            )
        elif total >= 500:
            badges.append({"emoji": "💎", "nome": "Diamante", "cor": "bg-primary"})
        elif total >= 250:
            badges.append({"emoji": "🏆", "nome": "Campeão", "cor": "bg-warning"})
        elif total >= 100:
            badges.append({"emoji": "🥇", "nome": "Ouro", "cor": "bg-warning"})
        elif total >= 50:
            badges.append(
                {"emoji": "⭐", "nome": "Super Cadastrador", "cor": "bg-success"}
            )
        elif total >= 25:
            badges.append({"emoji": "🔥", "nome": "Em Chamas", "cor": "bg-danger"})
        elif total >= 10:
            badges.append({"emoji": "🚀", "nome": "Decolando", "cor": "bg-info"})
        elif total >= 5:
            badges.append({"emoji": "🌱", "nome": "Crescendo", "cor": "bg-success"})
        elif total >= 1:
            badges.append({"emoji": "🌱", "nome": "Iniciante", "cor": "bg-secondary"})
        else:
            badges.append({"emoji": "🌱", "nome": "Novato", "cor": "bg-secondary"})

        # Badges especiais por colaboradores
        if colaboradores >= 50:
            badges.append(
                {"emoji": "👑", "nome": "Rei dos Colaboradores", "cor": "bg-primary"}
            )
        elif colaboradores >= 25:
            badges.append({"emoji": "👥", "nome": "Mentor Master", "cor": "bg-info"})
        elif colaboradores >= 10:
            badges.append(
                {"emoji": "👥", "nome": "Mentor de Colaboradores", "cor": "bg-info"}
            )

        # Badges especiais por convidados
        if convidados >= 500:
            badges.append(
                {"emoji": "🎯", "nome": "Mestre dos Convidados", "cor": "bg-warning"}
            )
        elif convidados >= 250:
            badges.append(
                {"emoji": "🎯", "nome": "Expert em Convidados", "cor": "bg-warning"}
            )
        elif convidados >= 100:
            badges.append(
                {"emoji": "🎯", "nome": "Convidados Master", "cor": "bg-warning"}
            )
        elif convidados >= 50:
            badges.append(
                {
                    "emoji": "🎯",
                    "nome": "Especialista em Convidados",
                    "cor": "bg-warning",
                }
            )

        return badges

    badges_usuario_logado = calcular_badges_usuario(
        total_cadastros, colaboradores_cadastrados, convidados_cadastrados
    )

    return {"badges_usuario_logado": badges_usuario_logado}
