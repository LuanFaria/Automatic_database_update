import pandas as pd
import psycopg2
from input_polo import conectar_banco


# Função para consultar o id da tabela 'estagio' usando a coluna 'nome'
def consultar_estagio(estagio_cliente):
    conn = conectar_banco()
    cur = conn.cursor()
   
    try:
        # Ajustando a consulta para usar o schema 'ativos' e a tabela 'estagio'
        query = "SELECT id FROM ativos.estagio WHERE nome = %s"
        cur.execute(query, (estagio_cliente,))
        resultado = cur.fetchone()  # Retorna o primeiro resultado
        return resultado[0] if resultado else None
    except Exception as e:
        print(f"Erro ao executar a consulta: {e}")
    finally:
        cur.close()
        conn.close()

# Função principal para processar o arquivo Excel
def att_bd_agro(caminho_arquivo_excel,saida):
    # Lendo o arquivo Excel
    print('\nProcessando TALHAO!')
    df = pd.read_excel(caminho_arquivo_excel)
    
    # Criando a coluna 'estagio_id' e preenchendo-a com os ids encontrados no banco
    df['estagio_id'] = df['ESTAGIO'].apply(lambda estagio: consultar_estagio(estagio))
    
    # Convertendo os nomes das colunas para minúsculas
    df.columns = df.columns.str.lower()
    df['produto_id'] = 4
     # Removendo as colunas 
    df.drop(columns=['cliente','tp_prop','estagio', 'safra', 'objetivo', 'grupo_dash', 'grupo_ndvi', 'nmro_corte', 'desc_cana', 'tch_rest', 'tc_rest', 'dt_corte','atr_est', 'tah'], inplace=True, errors='ignore')
    
    df['dt_plantio'] = pd.to_datetime(df['dt_plantio'], dayfirst=True).dt.strftime('%Y-%m-%d')
    df['dt_ult_corte'] = pd.to_datetime(df['dt_ult_corte'], dayfirst=True).dt.strftime('%Y-%m-%d')

    # Renomeando as colunas conforme solicitado
    df.rename(columns={
        'a_est_moagem': 'area_est_moagem',
        'a_colhida': 'area_colhida',
        'a_est_muda': 'area_est_muda'
    }, inplace=True)
    
    # Salvando o Excel com as novas colunas
    df.to_excel(saida+"/saida_talhao.xlsx", index=False)
    print("Arquivo Excel atualizado com sucesso!")

def remover_linhas_sem_geometria(pasta_saida):
    # Lê a planilha
    df = pd.read_excel(pasta_saida)
    print(pasta_saida)

    # Remove as linhas onde a coluna "geometria" está vazia (nula ou vazia)
    df = df.dropna(subset=['geometria'])

    # Salva o DataFrame resultante no mesmo arquivo, sobrescrevendo-o
    df.to_excel(pasta_saida, sheet_name='TALHAO', index=False)
    print("Linhas sem valores na coluna 'geometria' foram removidas com sucesso.")


def cruza_planilhas(talhao_path, fazenda_path):
    # Carregar as tabelas
    df_fazenda = pd.read_excel(fazenda_path)
    df_talhao = pd.read_excel(talhao_path, sheet_name='TALHAO')

    # Realizar o merge entre 'FAZENDA' de TALHAO e 'cod_fazenda' de FAZENDA
    df_talhao = df_talhao.merge(df_fazenda[['cod_fazenda', 'fazenda_id', 'cliente_id', 'polo_id']], 
                                left_on='FAZENDA', right_on='cod_fazenda', how='left')

    # Salvar a tabela TALHAO atualizada na mesma planilha, substituindo a aba existente
    with pd.ExcelWriter(talhao_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        df_talhao.to_excel(writer, sheet_name='TALHAO', index=False)

    print(f"Planilha '{talhao_path}' atualizada com sucesso na aba 'TALHAO'.")

def insere_talhao(talhao_path):
    # Carregar a planilha TALHAO
    df_talhao = pd.read_excel(talhao_path)

    # Adicionar colunas ausentes, se necessário
    colunas_necessarias = [
        'cliente_id', 'polo_id', 'fazenda_id', 'setor', 'secao', 'bloco', 'pivo', 'talhao', 
        'produto_id', 'variedade_id', 'estagio_id', 'ambiente', 'geometria', 'area_ha', 
        'area_est_moagem', 'area_colhida', 'area_est_muda', 'tch_est', 'tc_est', 'tch_real', 
        'tc_real', 'atr', 'data_plantio', 'data_ult_corte'
    ]
    for coluna in colunas_necessarias:
        if coluna not in df_talhao.columns:
            df_talhao[coluna] = None  # Preencher com valores nulos

    conn = conectar_banco()

    try:
        # Teste de conexão: Executar uma consulta simples
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("Conexão bem-sucedida com o banco de dados.")
            else:
                print("Erro: Não foi possível verificar a conexão com o banco de dados.")
        
        # Carregar os dados existentes da tabela talhao no banco de dados
        query = """
            SELECT cliente_id, polo_id, fazenda_id, setor, secao, bloco, pivo, talhao, 
                   produto_id, variedade_id, estagio_id, ambiente, geometria, area_ha, 
                   area_est_moagem, area_colhida, area_est_muda, tch_est, tc_est, tch_real, 
                   tc_real, atr, data_plantio, data_ult_corte
            FROM ativos.talhao
        """
        with conn.cursor() as cursor:
            cursor.execute(query)
            registros = cursor.fetchall()
            colunas = [desc[0] for desc in cursor.description]
        df_db = pd.DataFrame(registros, columns=colunas)

        # Selecionar as colunas para comparação
        cols_verificacao = ['cliente_id', 'polo_id', 'fazenda_id', 'setor', 'secao', 'bloco', 'pivo', 'talhao']
        df_talhao_check = df_talhao[cols_verificacao]
        df_db_check = df_db[cols_verificacao]
        
        df_db_check.replace('', pd.NA, inplace=True) # substitui vazi por nan
        df_db_check = df_db_check.fillna(1) #nan por 0
        df_db_check = df_db_check.astype('int64') #obj por int


        # Identificar os registros da planilha que não estão no banco
        novos_registros = df_talhao[~df_talhao_check.apply(tuple, 1).isin(df_db_check.apply(tuple, 1))]
        

        if novos_registros.empty:
            print("Esses registros já existem no banco de dados e não foram duplicados.")
        else:
            # Inserir novos registros no banco de dados
            with conn.cursor() as cursor:
                for _, row in novos_registros.iterrows():
                    cursor.execute(""" 
                        INSERT INTO ativos.talhao (
                            cliente_id, polo_id, fazenda_id, setor, secao, bloco, pivo, talhao, 
                            produto_id, variedade_id, estagio_id, ambiente, geometria, area_ha, 
                            area_est_moagem, area_colhida, area_est_muda, tch_est, tc_est, 
                            tch_real, tc_real, atr, data_plantio, data_ult_corte
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, tuple(row[colunas_necessarias]))
                conn.commit()
            print(f"{len(novos_registros)} novos registros inseridos no banco de dados.")
    
    except Exception as e:
         print(f"Erro ao verificar e inserir registros: {e}")
    
    finally:
         # Fechar a conexão com o banco de dados
        conn.close()



#insere_talhao('C:/ATIVOS/planilhas/saida_talhao.xlsx') #kapetaaaaa
