#!/usr/bin/env python
"""
Script para copiar dados do banco sisvot_dev_db para sisvot_db
Rode via: python manage.py shell < copiar_dados.py
"""

# Temporariamente mudar para banco de desenvolvimento
import os

from django.db import connection

os.environ["DB_NAME"] = "sisvot_dev_db"

from django.db import connections


def copy_users():
    """Copia usuários do banco dev para prod"""
    # Ler do banco dev
    with connections["default"].cursor() as cursor:
        cursor.execute(
            "SELECT id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined FROM auth_user"
        )
        users = cursor.fetchall()

    # Escrever no banco prod
    with connection.cursor() as cursor:
        for user in users:
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

    print(f"Copiou {len(users)} usuários")


def copy_colaboradores():
    """Copia colaboradores do banco dev para prod"""

    # Primeiro, verificar se as cidades/bairros existem
    with connections["default"].cursor() as cursor:
        cursor.execute(
            """
            SELECT id, nome, telefone, data_nascimento, cidade_id, bairro_id, tipo, data_cadastro, cadastrado_por_id 
            FROM colaboradores
        """
        )
        cols = cursor.fetchall()

    # Verificar estrutura da tabela no destino
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'colaboradores'"
            )
            cols_dest = [c[0] for c in cursor.fetchall()]
            print(f"Colunas em colaboradores (dest): {cols_dest}")
    except Exception as e:
        print(f"Erro ao verificar colunas: {e}")
        return

    # Verificar se coluna 'tipo' existe na origem
    with connections["default"].cursor() as cursor:
        cursor.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'colaboradores'"
        )
        cols_orig = [c[0] for c in cursor.fetchall()]
        print(f"Colunas em colaboradores (orig): {cols_orig}")

    if cols:
        print(f"Encontrou {len(cols)} colaboradores no banco dev")
        # Mostrar primeiro registro
        print(f"Exemplo: {cols[0]}")


def copy_convidados():
    """Copia convidados"""
    with connections["default"].cursor() as cursor:
        cursor.execute(
            "SELECT id, nome, telefone, data_nascimento, cidade_id, bairro_id, colaborador_id, data_cadastro, cadastrado_por_id FROM convidados"
        )
        convs = cursor.fetchall()
    print(f"Encontrou {len(convs)} convidados no banco dev")
    if convs:
        print(f"Exemplo: {convs[0]}")


def copy_historico():
    """Copia histórico"""
    with connections["default"].cursor() as cursor:
        cursor.execute(
            "SELECT id, data_hora, acao, usuario_id, detalhes, ip_address FROM historico_historico"
        )
        hist = cursor.fetchall()
    print(f"Encontrou {len(hist)} registros de histórico no banco dev")
    if hist:
        print(f"Exemplo: {hist[0]}")


if __name__ == "__main__":
    print("=" * 50)
    print("Copiando dados de sisvot_dev_db para sisvot_db")
    print("=" * 50)

    print("\n1. Verificando estrutura...")
    copy_colaboradores()
    copy_convidados()
    copy_historico()
    copy_users()
