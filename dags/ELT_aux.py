import os
import shutil
import psycopg2
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from airflow.models import Variable

# SALVANDO ARQUIVOS EM PASTAS ESTRUTURADAS
def transfer_tables(src_folder: str, dest_parent_folder: str, dest_type: str):
    # Consumindo data
    date = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime('%d-%m-%Y')

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

    # Remover todos os arquivos na pasta
    folder = f'./{src_folder}'
    for archive in os.listdir(folder):
        path_archive = os.path.join(folder, archive)
        if os.path.isfile(path_archive):
            os.remove(path_archive)

def tube_to_extracted_postgres():
    transfer_tables(src_folder='data_tube', dest_parent_folder='data_extracted', dest_type='postgres')    

def tube_to_extracted_csv():
    transfer_tables(src_folder='data_tube', dest_parent_folder='data_extracted', dest_type='csv')

# VALIDANDO DATA PASSADA COMO PARAMETRO
def validar_data(data, formato="%d-%m-%Y"):
    try:
        datetime.strptime(data, formato)
        return True
    except ValueError:
        return False


# TRANSFERINDO ARQUIVOS CSV PARA IMPORTAR PARA O POSTGRES
def transfer_archives(date = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime('%d-%m-%Y'), src_folder = './data_extracted', dest_parent_folder = './data_tube'):
    # Verifica se alguma dag foi passada como parametro para 
    var_date = Variable.get("DATE_EXPECTED", default_var="")

    if var_date != '' and validar_data(var_date) and os.path.exists(f'{src_folder}/csv/{var_date}') and os.path.exists(f'{src_folder}/postgres/{var_date}'):
        date = var_date
    
    print(f'Date utilized {date}')

    # Verifica se o diretório de origem existe
    if not os.path.exists(src_folder):
        raise FileNotFoundError(f"O diretório de origem '{src_folder}' não existe.")
    
    # Constrói os caminhos das subpastas csv e postgres
    date_folder = date  
    for subpasta in ['csv', 'postgres']:
        source_path = os.path.join(src_folder, subpasta, date_folder)

        # Cria a pasta csv ou postgres, caso não exista
        os.makedirs(source_path, exist_ok=True)
    
        # Cria o caminho no diretório de destino
        path_dest = os.path.join(dest_parent_folder)
        os.makedirs(path_dest, exist_ok=True)

        # Copia os arquivos
        for archive in os.listdir(source_path):
            path_archive_source = os.path.join(source_path, archive)
            path_archive_dest = os.path.join(path_dest, archive)

            if os.path.isfile(path_archive_source):
                shutil.copy(path_archive_source, path_archive_dest)

#RECUPERANDO COM PYTHON A TABELA, ORDER_WITH_DETAILS, CRIADA PELO DBT
def retrive_table():
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