from django.core.management.base import BaseCommand

from geografia.geocoding import geocode_bairro
from geografia.models import Bairro, Cidade


class Command(BaseCommand):
    help = "Geocodifica bairros de uma cidade (preenche latitude/longitude)"

    def add_arguments(self, parser):
        parser.add_argument("cidade", type=str, help="Nome da cidade (ex: Cuiabá)")
        parser.add_argument("uf", type=str, help="UF da cidade (ex: MT)")
        parser.add_argument(
            "--dry-run", action="store_true", help="Apenas exibe o que seria alterado"
        )
        parser.add_argument(
            "--only-empty", action="store_true", help="Apenas bairros sem lat/lon"
        )

    def handle(self, *args, **options):
        nome_cidade = options["cidade"]
        uf = options["uf"].upper()
        dry_run = options["dry_run"]
        only_empty = options["only_empty"]

        try:
            cidade = Cidade.objects.get(
                nome_cidade__iexact=nome_cidade, uf_cidade__iexact=uf
            )
        except Cidade.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Cidade não encontrada: {nome_cidade}-{uf}")
            )
            return

        qs = Bairro.objects.filter(cidade=cidade)
        if only_empty:
            qs = qs.filter(latitude_bairro__isnull=True) | qs.filter(
                longitude_bairro__isnull=True
            )

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("Nenhum bairro para processar"))
            return

        self.stdout.write(self.style.WARNING(f"🏙️ Cidade: {cidade} | Bairros: {total}"))
        atualizados = 0
        falhas = 0

        for bairro in qs.order_by("nome_bairro"):
            result = geocode_bairro(
                bairro.nome_bairro, cidade=cidade.nome_cidade, uf=cidade.uf_cidade
            )
            if not result:
                self.stdout.write(
                    self.style.ERROR(f"❌ {bairro.nome_bairro}: não encontrado")
                )
                falhas += 1
                continue

            lat, lon = result
            self.stdout.write(f"✔️ {bairro.nome_bairro}: lat={lat:.6f}, lon={lon:.6f}")

            if not dry_run:
                bairro.latitude_bairro = lat
                bairro.longitude_bairro = lon
                bairro.save(update_fields=["latitude_bairro", "longitude_bairro"])
                atualizados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Concluído. Atualizados: {atualizados} | Falhas: {falhas}"
            )
        )
