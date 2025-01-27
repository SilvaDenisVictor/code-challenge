# Pré-requisitos

Antes de começar, certifique-se de que as versões a seguir do Docker e do Docker Compose estão instaladas:

- **Docker**: versão 26.1.1
- **Docker Compose**: versão v2.27.0-desktop.2

# Instalação

Este projeto é totalmente containerizado, o que significa que você precisará apenas do Docker e do Docker Compose para executá-lo.

1. Clone o repositório:
   ```bash
   git clone https://github.com/usuario/projeto.git

2. Entre na pasta:
   ```bash
   cd projeto
   
3. Entre na pasta:
   ```bash
   docker-compose up --build

# Acessar pagina airflow

Pelo seu navegador acesse ao endereço https://localhost:8090, lá será possível visualizar as dags.

![image](docs/diagrama_embulk_meltano.jpg)

as tags principais são:
1. csv_to_csv	
  utiliza o meltano para extrair o csv e colocar na pasta data_extracted devidamente organizado
2. postgres_to_csv
	utiliza o meltano para extrair os dados do Postgres e também colocar na pasta devidamente organizado
3. csv_to_postgres
	utiliza o meltano para extrair os dados em formato csv e passar para o banco Postgres de destino
4. dbt_query
	utiliza meltano e dbt para criar uma nova tabela order_with_details e extrair os dados para a pasta query

The solution should be based on the diagrams below:

