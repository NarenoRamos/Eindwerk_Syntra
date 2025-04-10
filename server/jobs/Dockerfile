FROM ubuntu:24.04

RUN apt update && apt install -y cron python3 python3-pip python3-venv libpq-dev gcc

RUN python3 -m venv /app/venv
RUN /app/venv/bin/pip install --upgrade pip pandas psycopg2-binary requests python-dotenv

WORKDIR /app
COPY measure_point_data_etl.py /app/measure_point_data_etl.py
RUN chmod +x /app/measure_point_data_etl.py

COPY crontab /etc/cron.d/my-cron
RUN chmod 644 /etc/cron.d/my-cron
RUN crontab /etc/cron.d/my-cron

ENV PATH="/app/venv/bin:$PATH"

ENTRYPOINT ["cron", "-f"]