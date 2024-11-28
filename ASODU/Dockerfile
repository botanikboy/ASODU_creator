FROM python:3.10-slim

WORKDIR /

COPY ASODU .

RUN ls -l

RUN pip3 install psycopg2-binary==2.9.6 --no-cache-dir

RUN pip3 install -r requirements_for_container.txt --no-cache-dir

CMD ["gunicorn", "ASODU.wsgi:application", "--bind", "0:8000" ]
