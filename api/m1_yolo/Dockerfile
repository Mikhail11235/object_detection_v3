FROM python:3.7

WORKDIR /opt/object_detection_video

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

RUN /usr/local/bin/python -m pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app /opt/object_detection_video/app/
COPY model /opt/object_detection_video/model/
RUN wget -P /opt/object_detection_video/model/ https://github.com/Mikhail11235/object_detection_v3/releases/download/t1/yolov3.weights

# COPY output /opt/object_detection_video/output/
# COPY videos /opt/object_detection_video/videos/


# for local build
EXPOSE 9000
CMD python3 app/app.py

