FROM python:3.7

WORKDIR /opt/temporary_storage

RUN apt-get update

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install fastapi uvicorn python-multipart
COPY app.py .
# RUN mkdir input &&  mkdir output

EXPOSE 8502
CMD uvicorn app:app --host 0.0.0.0 --port 9003

