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

        # Consulta para listar tabelas e chaves primárias de cada esquema
        for schema in schemas:
            schema_name = schema[0]
            print(f"\nTabelas e chaves primárias no esquema '{schema_name}':")
            
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
                    table_name = table[0]
                    print(f"   Tabela: {table_name}")

                    # Consulta para verificar as chaves primárias da tabela
                    pk_query = f"""
                    SELECT column_name
                    FROM information_schema.key_column_usage
                    WHERE table_schema = %s
                    AND table_name = %s
                    AND constraint_name = (
                        SELECT constraint_name
                        FROM information_schema.table_constraints
                        WHERE table_schema = %s
                        AND table_name = %s
                        AND constraint_type = 'PRIMARY KEY'
                    );
                    """
                    cursor.execute(pk_query, (schema_name, table_name, schema_name, table_name))
                    pk_columns = cursor.fetchall()

                    if pk_columns:
                        pk_columns_list = [column[0] for column in pk_columns]
                        print(f"     Chave Primária: {', '.join(pk_columns_list)}")
                    else:
                        print("     (Sem chave primária)")
            else:
                print("   (Nenhuma tabela encontrada)")
except psycopg2.Error as e:
    print(f"Erro ao conectar ao banco de dados: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
        print("Conexão com o banco de dados encerrada.")