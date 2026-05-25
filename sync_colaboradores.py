#!/usr/bin/env python
"""
Script para sincronizar APENAS colaboradores do sisvot_dev_db para sisvot_db
"""
import os
import sys

sys.path.insert(0, "/srv/sisvot")
os.chdir("/srv/sisvot")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema_fidelizacao.settings")
os.environ["DB_NAME"] = "sisvot_db"

import django

django.setup()

from django.db import connection, connections


def sync_colaboradores():
    """Sincroniza colaboradores do banco dev para prod"""
    print("=" * 50)
    print("SINCRONIZANDO COLABORADORES")
    print("=" * 50)

    # Ler do banco dev
    with connections["default"].cursor() as cursor:
        cursor.execute(
            """
            SELECT id, nome, telefone, data_nascimento, cidade_id, bairro_id, tipo, data_cadastro, cadastrado_por_id 
            FROM colaboradores
        """
        )
        cols = cursor.fetchall()

    print(f"Encontrados {len(cols)} colaboradores no banco dev")

    # Contar antes
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM colaboradores")
        antes = cursor.fetchone()[0]

    print(f"Colaboradores no banco atual: {antes}")

    # Sincronizar
    copiados = 0
    atualizados = 0

    with connection.cursor() as cursor:
        for col in cols:
            # Verificar se já existe
            cursor.execute("SELECT id FROM colaboradores WHERE id = %s", [col[0]])
            existe = cursor.fetchone()

            try:
                if existe:
                    # Atualizar
                    cursor.execute(
                        """
                        UPDATE colaboradores SET
                            nome = %s,
                            telefone = %s,
                            data_nascimento = %s,
                            cidade_id = %s,
                            bairro_id = %s,
                            tipo = %s,
                            data_cadastro = %s,
                            cadastrado_por_id = %s
                        WHERE id = %s
                    """,
                        (
                            col[1],
                            col[2],
                            col[3],
                            col[4],
                            col[5],
                            col[6],
                            col[7],
                            col[8],
                            col[0],
                        ),
                    )
                    atualizados += 1
                else:
                    # Inserir
                    cursor.execute(
                        """
                        INSERT INTO colaboradores (id, nome, telefone, data_nascimento, cidade_id, bairro_id, tipo, data_cadastro, cadastrado_por_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                        col,
                    )
                    copiados += 1
            except Exception as e:
                print(f"Erro ao sincronizar {col[1]}: {e}")

    # Contar depois
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM colaboradores")
        depois = cursor.fetchone()[0]

    print("\nRESULTADO:")
    print(f"  Novos: {copiados}")
    print(f"  Atualizados: {atualizados}")
    print(f"  Total antes: {antes}")
    print(f"  Total depois: {depois}")
    print("=" * 50)


if __name__ == "__main__":
    sync_colaboradores()
