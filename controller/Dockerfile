FROM python:3.7

WORKDIR /opt/controller

RUN apt-get update

RUN /usr/local/bin/python -m pip install --upgrade pip
COPY requirements.txt .
COPY wait.py .
RUN chmod +x /opt/controller/wait.py
RUN pip install -r requirements.txt

COPY app.py /opt/controller/

# EXPOSE 5672
CMD python3 app.py

