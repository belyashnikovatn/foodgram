FROM python:3.9

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt --no-cache-dir

ENTRYPOINT ["sh", "entrypoint.sh"]