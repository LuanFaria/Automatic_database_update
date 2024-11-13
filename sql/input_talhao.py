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

     # Removendo as colunas 
    df.drop(columns=['cliente','tp_prop','estagio', 'safra', 'objetivo', 'grupo_dash', 'grupo_ndvi', 'nmro_corte', 'desc_cana', 'tch_rest', 'tc_rest', 'dt_corte','dt_plantio','atr_est', 'tah'], inplace=True, errors='ignore')
    
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
    df.to_excel(pasta_saida, index=False)
    print("Linhas sem valores na coluna 'geometria' foram removidas com sucesso.")
