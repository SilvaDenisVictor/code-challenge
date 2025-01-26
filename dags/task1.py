from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import shutil


def transfer_tables(src_folder: str, dest_parent_folder: str, dest_type: str, date: str):
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
            new_file_name = f"{dest_type}_{date}_{file_name.replace('public-', '')}"
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
    data = datetime.now(ZoneInfo("America/Sao_Paulo"))
    transfer_tables(src_folder='data_tube', dest_parent_folder='data_extracted', dest_type='postgres', date = data.strftime('%d-%m-%Y'))
    

def tube_to_extracted_csv():
    data = datetime.now(ZoneInfo("America/Sao_Paulo"))
    transfer_tables(src_folder='data_tube', dest_parent_folder='data_extracted', dest_type='csv', date = data.strftime('%d-%m-%Y'))

with DAG(
    'meltano_airflow_dag',
    start_date=datetime(2025, 1, 25), 
    schedule_interval='@daily'
    ) as dag:

    postgres_to_csv = BashOperator(
        task_id='postgres_to_csv',
        bash_command='docker exec code-challenge-meltano-1 meltano run tap-postgres target-csv',
        dag=dag
    )

    tube_to_extracted_postgres_dag = PythonOperator(
        task_id="tube_to_extracted_postgres",        # Identificador único da tarefa
        python_callable=tube_to_extracted_postgres  # Função Python que será chamada
    )

    csv_to_csv = BashOperator(
        task_id='csv_to_csv',
        bash_command='docker exec code-challenge-meltano-1 meltano run tap-csv target-csv',
        dag=dag
    )

    tube_to_extracted_csv_dag = PythonOperator(
        task_id="tube_to_extracted_csv",        # Identificador único da tarefa
        python_callable=tube_to_extracted_csv  # Função Python que será chamada
    )

    postgres_to_csv >> tube_to_extracted_postgres_dag >> csv_to_csv >> tube_to_extracted_csv_dag

    