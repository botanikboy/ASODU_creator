FROM python:3.10-slim

WORKDIR /

COPY . .

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "ASODU.wsgi:application", "--bind", "0:8000" ]
