# database_utils.py

import psycopg2

# Função para conectar ao banco de dados
def conectar_banco():
    try:
        conn = psycopg2.connect(
            host="localhost",
            dbname="postgis_34_sample",
            user="postgres",
            password="postgres",
            options="-c client_encoding=UTF8"
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise


# Função para obter lista de IDs e nomes da tabela 'polo'
def obter_ids_nomes():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM ativos.polo")
    ids_nomes = cursor.fetchall()
    conn.close()
    return ids_nomes

# Função para adicionar um novo registro ao banco
def adicionar_nome_id(cliente_id, nome):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ativos.polo (cliente_id, nome) VALUES (%s, %s)", (cliente_id, nome))
    conn.commit()
    conn.close()
