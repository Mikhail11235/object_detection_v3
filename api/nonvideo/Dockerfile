FROM python:3.7

WORKDIR /opt/nonvideo_api

RUN apt-get update

RUN /usr/local/bin/python -m pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY database.py /opt/nonvideo_api/
COPY app.py /opt/nonvideo_api/

EXPOSE 8502
CMD uvicorn app:app --host 0.0.0.0 --port 9001

