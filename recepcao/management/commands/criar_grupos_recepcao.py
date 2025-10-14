from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Cria grupos: Recepcionista, Atendente, Supervisor"

    def handle(self, *args, **options):
        grupos = ["Recepcionista", "Atendente", "Supervisor"]
        for nome in grupos:
            g, created = Group.objects.get_or_create(name=nome)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Grupo criado: {nome}"))
            else:
                self.stdout.write(f"Grupo já existe: {nome}")

        # Permissões simples (poderemos refinar depois)
        # Aqui, deixamos sem anexar permissões específicas; usaremos decorators nos views.
        self.stdout.write(self.style.SUCCESS("Grupos verificados."))
