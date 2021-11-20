FROM python:3.7

WORKDIR /opt/gateway

RUN apt-get update

RUN /usr/local/bin/python -m pip install --upgrade pip
COPY requirements.txt .
COPY wait.py .
RUN chmod +x /opt/gateway/wait.py
RUN pip install -r requirements.txt

COPY app.py /opt/gateway/
COPY database.py /opt/gateway/

EXPOSE 9005
CMD uvicorn app:app --host 0.0.0.0 --port 9005
