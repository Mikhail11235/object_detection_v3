import pika
import json
import datetime
import requests
from config import VIDEO_PATH, OUTPUT_PATH
from yolo import detect_objects


class TS(object):
    base_url = "http://temporary_storage:9003/"

    def __init__(self, cor_id):
        self.cor_id = cor_id

    def put_video_to_ts(self, video, source="input"):
        url = self.base_url + "put_video"
        url += "?source=" + source
        files = {"video": (self.cor_id + ".mp4", video)}
        r = requests.post(url, files=files).content
        if isinstance(r, dict) and "status" in r.keys() and r["status"] == 0:
            return True
        return False

    def get_video_from_ts(self, source="output"):
        url = self.base_url + "get_video"
        url += "?source=" + source
        url += "&cor_id=" + self.cor_id
        r = requests.post(url).content
        if isinstance(r, dict):
            return False
        return r


class QueueReceiver:
    QUEUE_NAME = "QUEUE"

    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq", 5672))
        self.channel = self.connection.channel()

    def start(self):
        self.channel.queue_declare(queue=self.QUEUE_NAME)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.QUEUE_NAME, self.callback, auto_ack=True)
        print(" [*] Waiting for messages. To exit press CTRL+C")
        self.channel.start_consuming()

    @staticmethod
    def get_current_time():
        return datetime.datetime.now().strftime("%H:%M:%S")

    def send_response(self, message, properties):
        response = json.dumps(message).encode('utf-8')
        self.channel.basic_publish('', properties.reply_to, response,
                                   properties=pika.BasicProperties(correlation_id=properties.correlation_id))
        print("[%s] Response has been sent" % self.get_current_time())

    def callback(self, ch, method, properties, message_body):
        print("[%s] Request was received" % self.get_current_time())
        message_body = json.loads(message_body)
        cor_id = message_body["cor_id"]
        del message_body["cor_id"]
        if message_body["method"] == "m1_yolo":
            confidence = message_body["confidence"]
            non_max_suppression = message_body["non_max_suppression"]
            res = m1_yolo(cor_id, confidence, non_max_suppression)
            if res:
                message = {"status": 0}
            else:
                message = {"status": "Error"}
            self.send_response(message, properties)
        return message


def m1_yolo(cor_id, confidence=0.5, non_max_suppression=0.5):
    ts_model = TS(cor_id)
    video = ts_model.get_video_from_ts("input")
    local_video_name = cor_id + ".mp4"
    with open(VIDEO_PATH + local_video_name, "bw+") as f:
        f.write(video)
    print(f"[INFO] Processing Video....")
    total, elap = detect_objects(VIDEO_PATH + local_video_name, confidence, non_max_suppression)
    output_video = open(OUTPUT_PATH, 'rb')
    res = ts_model.put_video_to_ts(output_video.read(), source="output")
    print(f"[INFO] The video has total of {total} frames")
    print(f"[INFO] Time required to process a single frame: {round(elap / 60, 2)} minutes")
    print(f"[INFO] Time required to process the entire video: {round((elap * total) / 60, 2)} minutes")
    return True


if __name__ == "__main__":
    rabbit_mq = QueueReceiver()
    rabbit_mq.start()
