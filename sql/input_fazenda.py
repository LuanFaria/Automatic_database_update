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

# Se é pra dar input na mão q seja na planilha

def inserir_dados(cursor, cliente_id, polo_id, cod_fazenda, descricao, tipo_propriedade_id, area_ha, geometria):
    """Inserir dados no banco de dados e retornar o id gerado."""
    query = """
        INSERT INTO ativos.fazenda (cliente_id, polo_id, cod_fazenda, descricao, tipo_propriedade_id, area_ha, geometria)
        VALUES (%s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326))
        RETURNING id  -- Alterado para refletir o nome correto da coluna no banco
    """
    try:
        cursor.execute(query, (str(cliente_id), str(polo_id), str(cod_fazenda), descricao, tipo_propriedade_id, area_ha, geometria))
        fazenda_id = cursor.fetchone()[0]  # Recupera o id gerado
        print(f"Dados inseridos: cliente_id={cliente_id}, polo_id={polo_id}, cod_fazenda={cod_fazenda}, id={fazenda_id}")
        return fazenda_id
    except Exception as e:
        print(f"Erro ao inserir dados: {e}")
        return None

def processar_planilha(caminho_planilha):
    """Processar a planilha, inserir dados no banco, e preencher a planilha com o fazenda_id gerado."""
    if not caminho_planilha:
        return "Por favor, selecione uma planilha primeiro."
    
    try:
        # Conectar ao banco
        conn = conectar_banco()
        cursor = conn.cursor()

        # Carregar a planilha Excel
        df = pd.read_excel(caminho_planilha)

        # Criar uma coluna nova para armazenar os fazenda_id gerados
        df['fazenda_id'] = None

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
                print(f"Dados já existem: {cliente_id}, {polo_id}, {cod_fazenda}")
            else:
                # Inserir dados no banco e obter o id gerado
                fazenda_id = inserir_dados(cursor, cliente_id, polo_id, cod_fazenda, descricao, tipo_propriedade_id, area_ha, geometria)
                
                # Preencher o fazenda_id na planilha
                df.at[index, 'fazenda_id'] = fazenda_id  # Atualiza a célula correspondente

        # Commit e fechamento da conexão com o banco
        conn.commit()
        cursor.close()
        conn.close()

        # Salvar a planilha de volta (no mesmo arquivo ou em um novo caminho)
        df.to_excel(caminho_planilha, index=False)
        print("Planilha atualizada com sucesso!")

        return "Processamento concluído com sucesso!"
    except Exception as e:
        return f"Erro: {e}"
