import pika
import json
import requests
import urllib.parse
import datetime
import base64


class RabbitMQModel:
    QUEUE_NAME = "queue1"
    BASE_URL = "http://0.0.0.0"
    ENDPOINTS = {
        "hello": ["GET", 9001],
        "sign_up": ["POST", 9001],
        "method1": ["POST", 9000],
    }

    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters("0.0.0.0", 5672))
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

    def get_request_url(self, endpoint, path_params):
        total_url = self.BASE_URL + ":%d" % self.ENDPOINTS[endpoint][1]
        total_url = urllib.parse.urljoin(total_url, endpoint)
        if path_params:
            total_url = urllib.parse.urljoin(total_url, urllib.parse.urlencode(path_params))
        return total_url

    def send_response(self, response, properties, message=False):
        if message:
            response = {"message": response}
        response = json.dumps(response.json())
        self.channel.basic_publish('', properties.reply_to, response,
                                   properties=pika.BasicProperties(correlation_id=properties.correlation_id))
        print("[%s] Response has been sent" % self.get_current_time())

    def validate_message_body(self, message_body):
        for key in ["method", "endpoint"]:
            if key not in message_body.keys() or not message_body[key]:
                message = "Error: missing %s parameter" % key
                print(message)
                return message
        if message_body["endpoint"] not in self.ENDPOINTS.keys():
            message = "Error: invalid endpoint parameter (%s)" % message_body["endpoint"]
            print(message)
            return message
        if "method" not in message_body.keys():
            message = "Error: missing method parameter"
            print(message)
            return message
        if message_body["method"] not in list(set([val[0] for _, val in self.ENDPOINTS.items()])):
            message = "Error: invalid method parameter (%s)" % message_body["method"]
            print(message)
            return message
        return False
    
    def callback(self, ch, method, properties, message_body):
        print("[%s] Request was received" % self.get_current_time())
        message_body = json.loads(base64.b64decode(message_body))
        file = message_body["data_params"]["file"]
        del message_body["data_params"]["file"]
        message_body["data_params"]["file"] = base64.b64encode(file)
        message = self.validate_message_body(message_body)
        if message:
            self.send_response(message, properties, True)
            return message
        response = {}
        
        if message_body["endpoint"] in ["method1", ]:
            with open("input.mp4", "bw+") as f:
                f.write(message_body["data_params"]["video"])
            with open("input.mp4", "wb") as f:
                response = requests.post(urllib.parse.urljoin("http://0.0.0.0:9000/method1",
                                                              urllib.parse.urlencode(message_body["path_params"])),
                                         files={"file": ("input.mp4", f, "video/mp4")})

        elif message_body["method"] == "GET":
            response = requests.get(self.get_request_url(message_body["endpoint"], message_body["path_params"]),
                                    json=message_body["data_params"])
        
        elif message_body["method"] == "POST":
            response = requests.post(self.get_request_url(message_body["endpoint"], message_body["path_params"]),
                                     json=message_body["data_params"])
        
        self.send_response(response, properties)
        return response


if __name__ == "__main__":
    rabbit_mq = RabbitMQModel()
    rabbit_mq.start()
