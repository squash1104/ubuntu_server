#!/usr/bin/env python
"""
Script para sincronizar APENAS 7 colaboradores específicos do sisvot_dev_db para sisvot_db
"""
import psycopg2

# IDs dos 7 colaboradores
IDS = [655, 656, 657, 658, 659, 660, 661]

def sync_colaboradores():
    """Sincroniza apenas os colaboradores com IDs específicos"""
    print("=" * 50)
    print("SINCRONIZANDO 7 COLABORADORES")
    print("=" * 50)
    
    # Conectar no banco dev (sisvot_dev_db)
    try:
        conn_dev = psycopg2.connect(
            dbname='sisvot_dev_db',
            user='sisuserdb',
            password='lu531676',
            host='127.0.0.1',
            port='5432'
        )
        cur_dev = conn_dev.cursor()
        print("✅ Conectado no sisvot_dev_db")
    except Exception as e:
        print(f"❌ Erro ao conectar no sisvot_dev_db: {e}")
        return
    
    # Conectar no banco atual (sisvot_db)
    try:
        conn_prod = psycopg2.connect(
            dbname='sisvot_db',
            user='sisuserdb',
            password='lu531676',
            host='127.0.0.1',
            port='5432'
        )
        cur_prod = conn_prod.cursor()
        print("✅ Conectado no sisvot_db")
    except Exception as e:
        print(f"❌ Erro ao conectar no sisvot_db: {e}")
        return
    
    # Ler do banco dev
    placeholders = ','.join(['%s'] * len(IDS))
    cur_dev.execute(f"""
        SELECT id, nome, telefone, data_nascimento, cidade_id, bairro_id, tipo, data_cadastro, cadastrado_por_id 
        FROM colaboradores
        WHERE id IN ({placeholders})
        ORDER BY id
    """, IDS)
    cols = cur_dev.fetchall()
    
    print(f"\nEncontrados {len(cols)} colaboradores no sisvot_dev_db:")
    for col in cols:
        print(f"  {col[0]}: {col[1]}")
    
    # Contar antes
    cur_prod.execute("SELECT COUNT(*) FROM colaboradores")
    antes = cur_prod.fetchone()[0]
    print(f"\nColaboradores no sisvot_db: {antes}")
    
    # Sincronizar
    for col in cols:
        # Verificar se já existe
        cur_prod.execute("SELECT id FROM colaboradores WHERE id = %s", [col[0]])
        existe = cur_prod.fetchone()
        
        try:
            if existe:
                print(f"  ⏭️ {col[0]}: {col[1]} (já existe, atualizando)")
                cur_prod.execute("""
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
                """, (col[1], col[2], col[3], col[4], col[5], col[6], col[7], col[8], col[0]))
            else:
                print(f"  ✅ {col[0]}: {col[1]} (novo)")
                cur_prod.execute("""
                    INSERT INTO colaboradores (id, nome, telefone, data_nascimento, cidade_id, bairro_id, tipo, data_cadastro, cadastrado_por_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, col)
        except Exception as e:
            print(f"  ❌ Erro ao sincronizar {col[1]}: {e}")
        
        conn_prod.commit()
    
    # Contar depois
    cur_prod.execute("SELECT COUNT(*) FROM colaboradores")
    depois = cur_prod.fetchone()[0]
    
    # Fechar conexões
    cur_dev.close()
    conn_dev.close()
    cur_prod.close()
    conn_prod.close()
    
    print(f"\n" + "=" * 50)
    print("RESULTADO:")
    print(f"  Total antes: {antes}")
    print(f"  Total depois: {depois}")
    print("=" * 50)

if __name__ == '__main__':
    sync_colaboradores()
