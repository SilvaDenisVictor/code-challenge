import os
import shutil
import psycopg2
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

#SALVANDO ARQUIVOS EM PASTAS ESTRUTURADAS
def transfer_tables(src_folder: str, dest_parent_folder: str, dest_type: str):
    # Consumindo data
    date = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime('%d-%m-%Y')
    
    # Verificando type
    if dest_type not in ["csv", "postgres"]:
        raise ValueError("O tipo de destino deve ser 'csv' ou 'postgres'.")

    # Caminho para a pasta de destino específica
    dest_folder = os.path.join(dest_parent_folder, dest_type, date)

    # Criar a nova pasta se não existir
    os.makedirs(dest_folder, exist_ok=True)

    # Iterar pelos arquivos na pasta de origem
    for file_name in os.listdir(src_folder):
        if file_name.endswith(".csv"):
            # Renomear o arquivo no formato tipo_data_nome.csv
            new_file_name = f"{file_name.replace('public-', '')}"
            src_file_path = os.path.join(src_folder, file_name)
            dest_file_path = os.path.join(dest_folder, new_file_name)

            # Copiar o arquivo para o destino
            shutil.copy(src_file_path, dest_file_path)

            #print(f"Arquivo '{file_name}' transferido para '{dest_file_path}'.")

    # Remover todos os arquivos na pasta
    pasta = f'./{src_folder}'
    for arquivo in os.listdir(pasta):
        caminho_arquivo = os.path.join(pasta, arquivo)
        if os.path.isfile(caminho_arquivo):
            os.remove(caminho_arquivo)

def tube_to_extracted_postgres():
    transfer_tables(src_folder='data_tube', dest_parent_folder='data_extracted', dest_type='postgres')    

def tube_to_extracted_csv():
    transfer_tables(src_folder='data_tube', dest_parent_folder='data_extracted', dest_type='csv')

#TRANSFERINDO ARQUIVOS CSV PARA IMPORTAR PARA O POSTGRES
def copiar_arquivos(data = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime('%d-%m-%Y'), diretorio_origem = './data_extracted', diretorio_destino = './data_tube'):
    # Verifica se o diretório de origem existe
    if not os.path.exists(diretorio_origem):
        raise FileNotFoundError(f"O diretório de origem '{diretorio_origem}' não existe.")
    
    # Constrói os caminhos das subpastas csv e postgres
    subpastas = ['csv', 'postgres']
    data_pasta = data  # Nome da pasta com a data
    for subpasta in subpastas:
        caminho_origem = os.path.join(diretorio_origem, subpasta, data_pasta)

        # Verifica se a pasta da data existe
        if not os.path.exists(caminho_origem):
            print(f"Pasta não encontrada: {caminho_origem}. Pulando...")
            continue

        # Cria o caminho no diretório de destino
        caminho_destino = os.path.join(diretorio_destino)
        os.makedirs(caminho_destino, exist_ok=True)

        # Copia os arquivos
        for arquivo in os.listdir(caminho_origem):
            caminho_arquivo_origem = os.path.join(caminho_origem, arquivo)
            caminho_arquivo_destino = os.path.join(caminho_destino, arquivo)

            if os.path.isfile(caminho_arquivo_origem):
                shutil.copy(caminho_arquivo_origem, caminho_arquivo_destino)
                print(f"Arquivo copiado: {caminho_arquivo_origem} -> {caminho_arquivo_destino}")

#RECUPERANDO COM PYTHON A TABELA, ORDER_WITH_DETAILS, CRIADA PELO DBT
def recuperar_tabela():
    #configuração db
    db_config = {
        "dbname": "destination_db",
        "user": "destination_db_user",
        "password": "destination_db_password",
        "host": "destination_db", 
        "port": 5432,
        "options": "-c search_path=tap_csv_2"
    }
    
    #conexão com db
    conn = psycopg2.connect(**db_config)

    #query
    query = """
        SELECT *
        FROM order_with_details;
    """

    #recuperando tabela
    df = pd.read_sql_query(query, conn)

    #transformando tabela em csv
    df.to_csv('/opt/airflow/query/order_with_details.csv', index=False)