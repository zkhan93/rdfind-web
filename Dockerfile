FROM python:3.10
ENV PYTHONUNBUFFERED 1
WORKDIR /app

RUN pip install --upgrade pip
COPY install-packages.sh .
RUN ./install-packages.sh

COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
EXPOSE 80
