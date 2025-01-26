from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime
from zoneinfo import ZoneInfo
from aux_task1 import tube_to_extracted_csv, tube_to_extracted_postgres, copiar_arquivos



with DAG(
    'task_1',
    start_date=datetime(2025, 1, 25),
    schedule_interval='@daily',
) as dag:

    trigger_postgres_to_csv = TriggerDagRunOperator(
        task_id='trigger_postgres_to_csv',
        trigger_dag_id='postgres_to_csv',  # ID da DAG a ser acionada
    )

    trigger_csv_to_csv = TriggerDagRunOperator(
        task_id='trigger_csv_to_csv',
        trigger_dag_id='csv_to_csv',  # ID da DAG a ser acionada
    )

    trigger_postgres_to_csv >> trigger_csv_to_csv 

with DAG(
    'postgres_to_csv',
    start_date=datetime(2025, 1, 25), 
    schedule_interval='@daily'
    ) as postgres_to_csv:

    postgres_to_csv = BashOperator(
        task_id='postgres_to_csv',
        bash_command='docker exec code-challenge-meltano-1 meltano run tap-postgres target-csv',
    )

    tube_to_extracted_postgres_dag = PythonOperator(
        task_id="tube_to_extracted_postgres",        # Identificador único da tarefa
        python_callable=tube_to_extracted_postgres  # Função Python que será chamada
    )

    postgres_to_csv >> tube_to_extracted_postgres_dag  

with DAG(
    'csv_to_csv',
    start_date=datetime(2025, 1, 25), 
    schedule_interval='@daily'
    ) as csv_to_csv:

    csv_to_csv = BashOperator(
        task_id='csv_to_csv',
        bash_command='docker exec code-challenge-meltano-1 meltano run tap-csv-1 target-csv',
    )

    tube_to_extracted_csv_dag = PythonOperator(
        task_id="tube_to_extracted_csv",        # Identificador único da tarefa
        python_callable=tube_to_extracted_csv  # Função Python que será chamada
    )

    csv_to_csv >> tube_to_extracted_csv_dag



with DAG(
    'csv_to_postgres',
    start_date=datetime(2025, 1, 25), 
    schedule_interval='@daily'
    ) as csv_to_csv:

    extracted_to_tube_dag = PythonOperator(
        task_id="data_extracted_to_data_tube",   
        python_callable=copiar_arquivos  
    )

    tube_to_postgres = BashOperator(
        task_id='tube_to_postgres',
        bash_command='docker exec code-challenge-meltano-1 meltano run tap-csv-2 target-postgres',
    )

    cleaning_tube = BashOperator(
        task_id='cleaning_tube',
        bash_command='cd /opt/airflow/data_tube && rm *',
    )

    extracted_to_tube_dag >> tube_to_postgres >> cleaning_tube