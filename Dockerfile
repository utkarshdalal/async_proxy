FROM python:3.8-slim
WORKDIR /app
COPY . /app
RUN apt-get update && \
    apt-get install -y \
    g++ \
    gcc
RUN pip install -r requirements.txt
EXPOSE 8080
CMD ["python", "proxy_server.py"]