import csv

from django.core.management.base import BaseCommand, CommandError

from colaboradores.models import Colaborador  # Importe o seu modelo de colaborador aqui


class Command(BaseCommand):
    help = "Importa colaboradores de um arquivo CSV."

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file", type=str, help="O caminho para o arquivo CSV de colaboradores"
        )

    def handle(self, *args, **options):
        csv_file_path = options["csv_file"]

        try:
            with open(csv_file_path, encoding="latin-1") as file:
                reader = csv.reader(file, delimiter=";")

                # Pular o cabeçalho
                next(reader)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Iniciando a importação do arquivo: {csv_file_path}"
                    )
                )

                total_registros = 0
                registros_importados = 0
                linhas_ignoradas = 0

                for row in reader:
                    total_registros += 1

                    # Verifique se a linha tem o número de colunas esperado
                    if len(row) < 4:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Linha ignorada por formato inválido: {row}"
                            )
                        )
                        linhas_ignoradas += 1
                        continue

                    # Extrair os dados da linha
                    nome = row[0].strip()
                    telefone = row[1].strip() if len(row[1].strip()) > 0 else None
                    cidade_id = row[2].strip()
                    bairro_id = row[3].strip()

                    # Lidar com o problema de "nome do colaborador
                    # não encontrado ou vazio"
                    if not nome:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Linha ignorada: nome do colaborador não encontrado "
                                f"ou vazio. Dados: {row}"
                            )
                        )
                        linhas_ignoradas += 1
                        continue

                    # Tenta criar um novo objeto Colaborador.
                    # Se o nome já existir, você pode atualizar os dados.
                    # Adapte esta lógica conforme a necessidade do seu projeto.
                    try:
                        colaborador, created = Colaborador.objects.update_or_create(
                            nome=nome,
                            defaults={
                                "telefone": telefone,
                                "cidade_id": cidade_id,
                                "bairro_id": bairro_id,
                            },
                        )
                        registros_importados += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Erro ao processar a linha para o colaborador "
                                f"'{nome}': {e}"
                            )
                        )
                        linhas_ignoradas += 1

                self.stdout.write(
                    self.style.SUCCESS("------------------------------------")
                )
                self.stdout.write(self.style.SUCCESS("Importação concluída!"))
                self.stdout.write(
                    self.style.SUCCESS(f"Total de linhas lidas: {total_registros}")
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Registros importados/atualizados: {registros_importados}"
                    )
                )
                self.stdout.write(
                    self.style.WARNING(f"Linhas ignoradas: {linhas_ignoradas}")
                )
                self.stdout.write(
                    self.style.SUCCESS("------------------------------------")
                )

        except FileNotFoundError as e:
            raise CommandError(
                f'O arquivo CSV "{csv_file_path}" não foi encontrado.'
            ) from e
        except Exception as e:
            raise CommandError(f"Ocorreu um erro durante a importação: {e}") from e
