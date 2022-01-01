FROM postgres:latest

RUN apt-get update && apt-get install -y python3 python3-pip
RUN apt-get -y install python3.8-dev
RUN apt-get install postgresql-server-dev-10 gcc python3-dev musl-dev

RUN pip3 install psycopg2

USER postgres


EXPOSE 5432

VOLUME ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]
