FROM meltano/meltano:latest

COPY meltano.yml /project/meltano.yml
COPY ./data/order_details.csv /project/order_details.csv
COPY .env /project/.env

RUN meltano lock --all --update

RUN meltano install

