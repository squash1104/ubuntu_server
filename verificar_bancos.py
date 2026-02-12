#!/usr/bin/env python
"""
Script para verificar colaboradores em todos os bancos PostgreSQL
"""
import psycopg2

def verificar_banco(nome_banco):
    """Verifica quantos colaboradores tem em um banco"""
    try:
        conn = psycopg2.connect(
            dbname=nome_banco,
            user='sisuserdb',
            password='lu531676',
            host='127.0.0.1',
            port='5432'
        )
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM colaboradores")
        count = cur.fetchone()[0]
        print(f"  📊 {nome_banco}: {count} colaboradores")
        cur.close()
        conn.close()
        return count
    except Exception as e:
        print(f"  ❌ {nome_banco}: Erro - {e}")
        return 0

# Bancos conhecidos
bancos = ['sisvot_db', 'sisvot_dev_db', 'postgres', 'template1', 'template0']

print("=" * 50)
print("VERIFICANDO COLABORADORES EM TODOS OS BANCOS")
print("=" * 50)

for banco in bancos:
    verificar_banco(banco)

print("=" * 50)
