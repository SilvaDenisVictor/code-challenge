from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime
from zoneinfo import ZoneInfo
from ELT_aux import tube_to_extracted_csv, tube_to_extracted_postgres, copiar_arquivos, recuperar_tabela

# EXECUTA O ELT COMPLETO
with DAG(
    'ELT',
    start_date=datetime(2025, 1, 25),
    schedule_interval='@daily',
    catchup=False
) as elt:

    trigger_postgres_to_csv = TriggerDagRunOperator(
        task_id='trigger_postgres_to_csv',
        trigger_dag_id='postgres_to_csv',
        wait_for_completion=True,
    )

    trigger_csv_to_csv = TriggerDagRunOperator(
        task_id='trigger_csv_to_csv',
        trigger_dag_id='csv_to_csv',
        wait_for_completion=True,
    )

    trigger_csv_to_postgres = TriggerDagRunOperator(
        task_id='trigger_csv_to_postgres',
        trigger_dag_id='csv_to_postgres',
        wait_for_completion=True,
    )

    trigger_dbt_query = TriggerDagRunOperator(
        task_id='trigger_dbt_query',
        trigger_dag_id='dbt_query',
        wait_for_completion=True,
    )

    trigger_postgres_to_csv >> trigger_csv_to_csv >> trigger_csv_to_postgres >> trigger_dbt_query

# EXECUTA A PRIMEIRA PARTE DO ELT
with DAG(
    'task_1',
    catchup=False
) as task_1:
    
    trigger_postgres_to_csv = TriggerDagRunOperator(
        task_id='trigger_postgres_to_csv',
        trigger_dag_id='postgres_to_csv',
        wait_for_completion=True,
    )

    trigger_csv_to_csv = TriggerDagRunOperator(
        task_id='trigger_csv_to_csv',
        trigger_dag_id='csv_to_csv',
        wait_for_completion=True,
    )

    trigger_postgres_to_csv >> trigger_csv_to_csv

# EXECUTA A SEGUNDA PARTE DO ELT
with DAG(
    'task_2',
    catchup=False
) as task_2:
    
    trigger_csv_to_postgres = TriggerDagRunOperator(
        task_id='trigger_csv_to_postgres',
        trigger_dag_id='csv_to_postgres',
        wait_for_completion=True,
    )

    trigger_dbt_query = TriggerDagRunOperator(
        task_id='trigger_dbt_query',
        trigger_dag_id='dbt_query',
        wait_for_completion=True,
    )

    trigger_csv_to_postgres >> trigger_dbt_query

# UTILIZA O MELTANO PARA EXTRAIR AS TABELAS DO POSTGRES, TAMBÉM ORGANIZA OS ARQUIVOS
with DAG(
    'postgres_to_csv',
    catchup=False
    ) as postgres_to_csv:

    postgres_to_csv = BashOperator(
        task_id='postgres_to_csv',
        bash_command='docker exec code-challenge-meltano-1 meltano run tap-postgres target-csv',
    )

    tube_to_extracted_postgres_dag = PythonOperator(
        task_id="tube_to_extracted_postgres",
        python_callable=tube_to_extracted_postgres
    )

    postgres_to_csv >> tube_to_extracted_postgres_dag  

# UTILIZA O MELTANO PARA EXTRAIR AS TABELA CSV, TAMBÉM ORGANIZA OS ARQUIVOS
with DAG(
    'csv_to_csv',
    catchup=False
    ) as csv_to_csv:

    csv_to_csv = BashOperator(
        task_id='csv_to_csv',
        bash_command='docker exec code-challenge-meltano-1 meltano run tap-csv-1 target-csv',
    )

    tube_to_extracted_csv_dag = PythonOperator(
        task_id="tube_to_extracted_csv",
        python_callable=tube_to_extracted_csv
    )

    csv_to_csv >> tube_to_extracted_csv_dag


# EXTRAI TODAS AS TABELAS EM FORMATO CSV E TRANSFERE PARA O BANCO DE DADOS UTILIZANDO O MELTANO
with DAG(
    'csv_to_postgres',
    catchup=False
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

# CRIA UMA NOVA TABELA NO BANCO CHAMADA ORDER_WITH_DETAILS E SALVA ESSA TABELA EM FORMATO CSV
with DAG(
    'dbt_query',
    catchup=False
    ) as dbt_query:

    dbt_query = BashOperator(
        task_id='dbt_query',
        bash_command='docker exec code-challenge-meltano-1 meltano invoke dbt-postgres:run',
    )

    saving_order_with_details_table = PythonOperator(
        task_id="saving_order_with_details_table",   
        python_callable=recuperar_tabela
    )

    dbt_query >> saving_order_with_details_table