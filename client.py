import pika
import uuid
import json
import datetime
import base64

message1 = b'{"method": "POST", "endpoint": "sign_up", "path_params": "", "data_params": {"firstname": "test1", ' \
           b'"lastname": "test1", "password": "test1"}}'
# with open("api/m1_yolo/videos/car_chase_01.mp4", "rb") as f:
#     message1 = base64.b64encode(b'{"method": "POST", "endpoint": "method1", "path_params": {"confidence: 0.5, '
#                                 b'"non_max_suppression": 0.5, "video_source": "nodb"}, "data_params": {"file": "' + \
#                                 f.read() + b'}}')


class ClientModel(object):
    QUEUE_NAME = "queue1"
    ENDPOINTS = {
        "hello": ["GET", 9001],
        "sign_up": ["POST", 9001],
        "method1": ["POST", 9000],
    }

    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters("0.0.0.0", 5672))
        self.channel = self.connection.channel()
        self.corr_id = str(uuid.uuid4())
        self.response = None
        self.channel.basic_consume(self.QUEUE_NAME, self.on_response, auto_ack=True)

    @staticmethod
    def get_current_time():
        return datetime.datetime.now().strftime("%H:%M:%S")

    def get_response(self, _response):
        _response = json.loads(_response)
        if "message" in _response.keys():
            print("[%s] Response was received: %s" % (self.get_current_time(), _response["message"]))
        else:
            print("[%s] Response was received" % self.get_current_time())
        return _response

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, message):
        props = pika.BasicProperties(reply_to=self.QUEUE_NAME, correlation_id=self.corr_id)
        self.channel.basic_publish('', self.QUEUE_NAME, message, properties=props)
        print("[%s] Request has been sent" % self.get_current_time())
        while self.response is None:
            self.connection.process_data_events()
        self.response = self.get_response(self.response)
        return self.response

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

    def create_message(self):
        # TODO add the ability to enter messages
        return self.call(message1)


if __name__ == "__main__":
    client = ClientModel()
    client_response = client.create_message()
