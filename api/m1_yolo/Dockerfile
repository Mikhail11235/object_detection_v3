FROM python:3.7

WORKDIR /opt/object_detection_video

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

RUN /usr/local/bin/python -m pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app /opt/object_detection_video/app/
COPY model /opt/object_detection_video/model/
# COPY output /opt/object_detection_video/output/
# COPY videos /opt/object_detection_video/videos/


# for local build
EXPOSE 8501
CMD uvicorn app.app:app --host 0.0.0.0 --port 9000

