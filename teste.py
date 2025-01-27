import psycopg2
from psycopg2 import OperationalError

# Configurações do banco de dados
db_config = {
    "dbname": "destination_db",
    "user": "destination_db_user",
    "password": "destination_db_password",
    "host": "localhost",  # Use 'localhost' se estiver executando localmente
    "port": 5438          # Porta mapeada no Docker Compose
}

try:
    # Conexão com o banco de dados
    conn = psycopg2.connect(**db_config)
    print("Conexão bem-sucedida!")

    # Criação de um cursor para executar comandos SQL
    with conn.cursor() as cursor:
        # Consulta para listar os esquemas do banco de dados
        schema_query = """
        SELECT schema_name
        FROM information_schema.schemata
        ORDER BY schema_name;
        """
        cursor.execute(schema_query)

        # Recupera os esquemas
        schemas = cursor.fetchall()
        print("Esquemas disponíveis no banco de dados:")
        for schema in schemas:
            print(f" - {schema[0]}")

        # Consulta para listar tabelas de cada esquema
        for schema in schemas:
            schema_name = schema[0]
            print(f"\nTabelas no esquema '{schema_name}':")
            
            table_query = f"""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
            ORDER BY table_name;
            """
            cursor.execute(table_query, (schema_name,))
            tables = cursor.fetchall()

            if tables:
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("   (Nenhuma tabela encontrada)")
except psycopg2.Error as e:
    print(f"Erro ao conectar ao banco de dados: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
        print("Conexão com o banco de dados encerrada.")