from django.core.management.base import BaseCommand, CommandError

from geografia.models import Bairro, Cidade


class Command(BaseCommand):
    help = "Importa bairros para uma cidade a partir de uma lista"

    def add_arguments(self, parser):
        parser.add_argument(
            "cidade",
            type=str,
            help="Nome da cidade (ex: Várzea Grande)",
        )
        parser.add_argument(
            "uf",
            type=str,
            help="UF da cidade (ex: MT)",
        )
        parser.add_argument(
            "bairros",
            nargs="+",
            type=str,
            help="Lista de nomes dos bairros",
        )
        parser.add_argument(
            "--arquivo",
            type=str,
            help="Caminho para arquivo com lista de bairros (um por linha)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Apenas exibe o que seria criado",
        )

    def handle(self, *args, **options):
        nome_cidade = options["cidade"]
        uf = options["uf"].upper()
        dry_run = options["dry_run"]
        arquivo = options.get("arquivo")

        # Obter lista de bairros
        if arquivo:
            try:
                with open(arquivo, "r", encoding="utf-8") as f:
                    bairros_lista = [
                        linha.strip()
                        for linha in f.readlines()
                        if linha.strip()
                    ]
            except FileNotFoundError:
                raise CommandError(f"Arquivo não encontrado: {arquivo}")
            except Exception as e:
                raise CommandError(f"Erro ao ler arquivo: {e}")
        else:
            bairros_lista = options["bairros"]

        if not bairros_lista:
            raise CommandError("Nenhum bairro fornecido")

        # Buscar cidade
        try:
            cidade = Cidade.objects.get(
                nome_cidade__iexact=nome_cidade, uf_cidade__iexact=uf
            )
        except Cidade.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Cidade não encontrada: {nome_cidade}-{uf}")
            )
            return
        except Cidade.MultipleObjectsReturned:
            self.stdout.write(
                self.style.ERROR(
                    f"Múltiplas cidades encontradas: {nome_cidade}-{uf}"
                )
            )
            return

        self.stdout.write(
            self.style.WARNING(
                f"🏙️ Cidade: {cidade} | Bairros a importar: {len(bairros_lista)}"
            )
        )

        criados = 0
        ja_existem = 0
        erros = 0

        for nome_bairro in sorted(bairros_lista):
            # Verificar se já existe
            existente = Bairro.objects.filter(
                nome_bairro__iexact=nome_bairro, cidade=cidade
            ).first()

            if existente:
                self.stdout.write(
                    f"  ⏭️ {nome_bairro} (já existe)"
                )
                ja_existem += 1
                continue

            if dry_run:
                self.stdout.write(
                    self.style.WARNING(f"  [DRY-RUN] Criaria: {nome_bairro}")
                )
                continue

            try:
                bairro = Bairro.objects.create(
                    nome_bairro=nome_bairro.strip(),
                    cidade=cidade,
                )
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ {bairro.nome_bairro}")
                )
                criados += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ❌ {nome_bairro}: {e}")
                )
                erros += 1

        # Resumo
        self.stdout.write("")
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"[DRY-RUN] Criaria: {len(bairros_lista) - ja_existem} bairros"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Concluído. Criados: {criados} | Já existiam: {ja_existem} | Erros: {erros}"
                )
            )
