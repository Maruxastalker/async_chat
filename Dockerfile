FROM python:3.11-slim as base

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ./chat_api ./chat_api

EXPOSE 8000

CMD [ "uvicorn", "chat_api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]