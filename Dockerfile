FROM meltano/meltano:latest

COPY meltano.yml /project/meltano.yml

RUN meltano lock --all --update

RUN meltano install

COPY ./data/order_details.csv /project/order_details.csv
COPY .env /project/.env
COPY structure_files.json structure_files.json
COPY transform transform