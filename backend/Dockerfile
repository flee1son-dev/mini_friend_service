FROM python:3.13-slim

WORKDIR /backend

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/backend

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

