#!/usr/bin/env python
"""
Script completo para:
1. Rodar migrações no sisvot_db
2. Copiar dados do sisvot_dev_db para sisvot_db
"""
import os
import sys

# Adicionar o projeto ao path
sys.path.insert(0, "/srv/sisvot")
os.chdir("/srv/sisvot")

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema_fidelizacao.settings")
os.environ["DB_NAME"] = "sisvot_db"

import django

django.setup()

from django.db import connection, connections


def run_migrations():
    """Roda migrações"""
    from django.core.management import call_command

    print("=" * 50)
    print("RODANDO MIGRAÇÕES")
    print("=" * 50)
    call_command("migrate", verbosity=2, interactive=False)
    print("\nMigrações concluídas!\n")


def copy_users():
    """Copia usuários do banco dev para prod"""
    print("=" * 50)
    print("COPIANDO USUÁRIOS")
    print("=" * 50)

    # Ler do banco dev
    with connections["default"].cursor() as cursor:
        cursor.execute(
            "SELECT id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined FROM auth_user"
        )
        users = cursor.fetchall()

    print(f"Encontrados {len(users)} usuários para copiar")

    # Escrever no banco prod
    with connection.cursor() as cursor:
        copied = 0
        for user in users:
            try:
                cursor.execute(
                    """
                    INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        password = EXCLUDED.password,
                        last_login = EXCLUDED.last_login,
                        is_superuser = EXCLUDED.is_superuser,
                        username = EXCLUDED.username,
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        email = EXCLUDED.email,
                        is_staff = EXCLUDED.is_staff,
                        is_active = EXCLUDED.is_active,
                        date_joined = EXCLUDED.date_joined
                """,
                    user,
                )
                copied += 1
            except Exception as e:
                print(f"Erro ao copiar usuário {user[4]}: {e}")

    print(f"Copiados {copied}/{len(users)} usuários\n")


def copy_colaboradores():
    """Copia colaboradores"""
    print("=" * 50)
    print("COPIANDO COLABORADORES")
    print("=" * 50)

    with connections["default"].cursor() as cursor:
        cursor.execute(
            """
            SELECT id, nome, telefone, data_nascimento, cidade_id, bairro_id, tipo, data_cadastro, cadastrado_por_id 
            FROM colaboradores
        """
        )
        cols = cursor.fetchall()

    print(f"Encontrados {len(cols)} colaboradores para copiar")

    with connection.cursor() as cursor:
        copied = 0
        for col in cols:
            try:
                cursor.execute(
                    """
                    INSERT INTO colaboradores (id, nome, telefone, data_nascimento, cidade_id, bairro_id, tipo, data_cadastro, cadastrado_por_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        nome = EXCLUDED.nome,
                        telefone = EXCLUDED.telefone,
                        data_nascimento = EXCLUDED.data_nascimento,
                        cidade_id = EXCLUDED.cidade_id,
                        bairro_id = EXCLUDED.bairro_id,
                        tipo = EXCLUDED.tipo,
                        data_cadastro = EXCLUDED.data_cadastro,
                        cadastrado_por_id = EXCLUDED.cadastrado_por_id
                """,
                    col,
                )
                copied += 1
            except Exception as e:
                print(f"Erro ao copiar colaborador {col[1]}: {e}")

    print(f"Copiados {copied}/{len(cols)} colaboradores\n")


def copy_convidados():
    """Copia convidados"""
    print("=" * 50)
    print("COPIANDO CONVIDADOS")
    print("=" * 50)

    with connections["default"].cursor() as cursor:
        cursor.execute(
            """
            SELECT id, nome, telefone, data_nascimento, cidade_id, bairro_id, colaborador_id, data_cadastro, cadastrado_por_id 
            FROM convidados
        """
        )
        convs = cursor.fetchall()

    print(f"Encontrados {len(convs)} convidados para copiar")

    with connection.cursor() as cursor:
        copied = 0
        for conv in convs:
            try:
                cursor.execute(
                    """
                    INSERT INTO convidados (id, nome, telefone, data_nascimento, cidade_id, bairro_id, colaborador_id, data_cadastro, cadastrado_por_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        nome = EXCLUDED.nome,
                        telefone = EXCLUDED.telefone,
                        data_nascimento = EXCLUDED.data_nascimento,
                        cidade_id = EXCLUDED.cidade_id,
                        bairro_id = EXCLUDED.bairro_id,
                        colaborador_id = EXCLUDED.colaborador_id,
                        data_cadastro = EXCLUDED.data_cadastro,
                        cadastrado_por_id = EXCLUDED.cadastrado_por_id
                """,
                    conv,
                )
                copied += 1
            except Exception as e:
                print(f"Erro ao copiar convidado {conv[1]}: {e}")

    print(f"Copiados {copied}/{len(convs)} convidados\n")


def copy_historico():
    """Copia histórico"""
    print("=" * 50)
    print("COPIANDO HISTÓRICO")
    print("=" * 50)

    # Verificar colunas disponíveis
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'historico_historico'"
            )
            cols = [c[0] for c in cursor.fetchall()]
        print(f"Colunas disponíveis: {cols}")

        # Determinar colunas para SELECT e INSERT
        select_cols = ", ".join(cols)
        placeholders = ", ".join(["%s"] * len(cols))

        with connections["default"].cursor() as cursor:
            cursor.execute(f"SELECT {select_cols} FROM historico_historico")
            hist = cursor.fetchall()

        print(f"Encontrados {len(hist)} registros de histórico para copiar")

        with connection.cursor() as cursor:
            copied = 0
            for h in hist:
                try:
                    cursor.execute(
                        f"""
                        INSERT INTO historico_historico ({select_cols})
                        VALUES ({placeholders})
                        ON CONFLICT (id) DO UPDATE SET
                            data_hora = EXCLUDED.data_hora,
                            acao = EXCLUDED.acao,
                            usuario_id = EXCLUDED.usuario_id,
                            ip_address = EXCLUDED.ip_address
                    """,
                        h,
                    )
                    copied += 1
                except Exception as e:
                    print(f"Erro ao copiar histórico {h[0]}: {e}")

        print(f"Copiados {copied}/{len(hist)} registros de histórico\n")

    except Exception as e:
        print(f"Aviso: Não foi possível copiar histórico: {e}\n")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("SCRIPT DE MIGRAÇÃO E CÓPIA DE DADOS")
    print("=" * 50 + "\n")

    # Configurar para usar sisvot_db
    print("Banco de dados atual:", connection.settings_dict["NAME"])

    try:
        # 1. Rodar migrações
        run_migrations()

        # 2. Copiar dados
        copy_users()
        copy_colaboradores()
        copy_convidados()
        copy_historico()

        print("=" * 50)
        print("TUDO CONCLUÍDO!")
        print("=" * 50)
        print("\nReinicie o gunicorn para aplicar as mudanças:")
        print("  sudo systemctl restart gunicorn")

    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback

        traceback.print_exc()
