import pandas as pd
import psycopg2
from input_polo import conectar_banco

def adicionar_nome_id(cliente_id, nome):
    """Adicionar um novo cliente_id e nome ao banco de dados."""
    conn = conectar_banco()
    cursor = conn.cursor()
    query = "INSERT INTO ativos.polo (cliente_id, nome) VALUES (%s, %s)"
    cursor.execute(query, (cliente_id, nome))
    conn.commit()
    cursor.close()
    conn.close()

def verificar_existencia(cursor, cliente_id, polo_id, cod_fazenda):
    """Verificar se os dados já existem no banco."""
    query = """
        SELECT 1 
        FROM ativos.fazenda 
        WHERE cliente_id = %s AND polo_id = %s AND cod_fazenda = %s
    """
    cursor.execute(query, (str(cliente_id), str(polo_id), str(cod_fazenda)))
    resultado = cursor.fetchone()
    return resultado is not None  # Retorna True se já existir

def inserir_dados(cursor, cliente_id, polo_id, cod_fazenda, descricao, tipo_propriedade_id, area_ha, geometria):
    """Inserir dados no banco de dados."""
    query = """
        INSERT INTO ativos.fazenda (cliente_id, polo_id, cod_fazenda, descricao, tipo_propriedade_id, area_ha, geometria)
        VALUES (%s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326))
    """
    cursor.execute(query, (str(cliente_id), str(polo_id), str(cod_fazenda), descricao, tipo_propriedade_id, area_ha, geometria))
    print(f"Dados inseridos: cliente_id={cliente_id}, polo_id={polo_id}, cod_fazenda={cod_fazenda}")

def processar_planilha(caminho_planilha):
    """Processar a planilha e inserir os dados no banco."""
    if not caminho_planilha:
        return "Por favor, selecione uma planilha primeiro."
    
    try:
        # Conectar ao banco
        conn = conectar_banco()
        cursor = conn.cursor()

        # Carregar a planilha Excel
        df = pd.read_excel(caminho_planilha)

        # Iterar sobre as linhas da planilha
        for index, row in df.iterrows():
            cliente_id = row['cliente_id']
            polo_id = row['polo_id']
            cod_fazenda = row['cod_fazenda']
            descricao = row['descricao']
            tipo_propriedade_id = row['tipo_propriedade_id']
            area_ha = row['area_ha']
            geometria = row['geometria']  # Supondo que geometria esteja no formato WKT

            # Verificar se os dados já existem
            if verificar_existencia(cursor, cliente_id, polo_id, cod_fazenda):
                return f"Dados já existem: {cliente_id}, {polo_id}, {cod_fazenda}"
            else:
                # Inserir dados no banco
                inserir_dados(cursor, cliente_id, polo_id, cod_fazenda, descricao, tipo_propriedade_id, area_ha, geometria)

        # Commit e fechamento da conexão
        conn.commit()
        cursor.close()
        conn.close()

        return "Processamento concluído com sucesso!"
    except Exception as e:
        return f"Erro: {e}"
