FROM meltano/meltano:latest-python3.11

COPY meltano.yml /project/meltano.yml
COPY ./data/order_details.csv /project/order_details.csv
COPY .env /project/.env
COPY structure_files.json structure_files.json

RUN meltano lock --all --update

RUN meltano install

