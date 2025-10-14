import csv

from django.core.management.base import BaseCommand, CommandError

from convidados.models import Colaborador, Convidado  # Importe seus modelos aqui


class Command(BaseCommand):
    help = "Importa convidados de um arquivo CSV e os associa a colaboradores."

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file", type=str, help="O caminho para o arquivo CSV de convidados"
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

                total_linhas = 0
                registros_criados = 0
                linhas_ignoradas = 0

                for row in reader:
                    total_linhas += 1

                    if len(row) < 5:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Linha ignorada por formato inválido: {row}"
                            )
                        )
                        linhas_ignoradas += 1
                        continue

                    # Extrair os dados da linha, limpando espaços em branco
                    nome = row[0].strip()
                    telefone = row[1].strip() if row[1].strip() else None
                    cidade_id = row[2].strip()
                    bairro_id = row[3].strip()
                    colaborador_id = row[4].strip()

                    # Lidar com dados ausentes ou mal formatados
                    if not nome or not colaborador_id.isdigit():
                        self.stdout.write(
                            self.style.WARNING(
                                f"Linha ignorada: nome do convidado ou ID do "
                                f"colaborador inválido. Dados: {row}"
                            )
                        )
                        linhas_ignoradas += 1
                        continue

                    try:
                        # Tentar encontrar o colaborador. Se não encontrar,
                        # pular a linha.
                        colaborador = Colaborador.objects.get(pk=int(colaborador_id))

                        # Criar o objeto Convidado
                        Convidado.objects.create(
                            nome=nome,
                            telefone=telefone,
                            cidade_id=cidade_id,
                            bairro_id=bairro_id,
                            colaborador=colaborador,  # Associa o objeto Colaborador
                        )
                        registros_criados += 1
                    except Colaborador.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Linha ignorada: Colaborador com ID "
                                f"'{colaborador_id}' não encontrado. Convidado: {nome}"
                            )
                        )
                        linhas_ignoradas += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Erro ao processar a linha para o convidado "
                                f"'{nome}': {e}"
                            )
                        )
                        linhas_ignoradas += 1

                self.stdout.write(
                    self.style.SUCCESS("------------------------------------")
                )
                self.stdout.write(self.style.SUCCESS("Importação concluída!"))
                self.stdout.write(
                    self.style.SUCCESS(f"Total de linhas lidas: {total_linhas}")
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Registros de convidados criados: {registros_criados}"
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
