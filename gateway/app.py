import fastapi
import datetime
import uuid
import json
import requests
import pika
from database import DB

app = fastapi.FastAPI()


def check_token(token):
    db_model = DB()
    db_model.cursor.execute("SELECT user_id, end FROM authorization WHERE token = '%s'" % token)
    res = db_model.cursor.fetchone()
    if res and (int(res[1]) - int(datetime.datetime.now().timestamp())) <= 30 * 60:
        return int(res[0])
    return False


class QueueSender(object):
    QUEUE_NAME = "QUEUE"

    def __init__(self, cor_id):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq", 5672))
        self.channel = self.connection.channel()
        self.cor_id = cor_id
        self.response = None
        self.channel.basic_consume(self.QUEUE_NAME, self.on_response, auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.cor_id == props.correlation_id:
            self.response = body

    def send(self, message_dict):
        message = json.dumps(message_dict).encode('utf-8')
        props = pika.BasicProperties(reply_to=self.QUEUE_NAME, correlation_id=self.cor_id)
        self.channel.basic_publish('', self.QUEUE_NAME, message, properties=props)
        while self.response is None:
            self.connection.process_data_events()
        return self.response


class TS(object):
    base_url = "http://temporary_storage:9003/"

    def __init__(self, cor_id):
        self.cor_id = cor_id

    async def put_video_to_ts(self, video, source="input"):
        url = self.base_url + "put_video"
        url += "?source=" + source
        files = {"video": (self.cor_id + ".mp4", video)}
        r = json.loads(requests.post(url, files=files, verify=False).content)
        if isinstance(r, dict) and "status" in r.keys() and r["status"] == 0:
            return True
        return False

    async def get_video_from_ts(self, source="output"):
        url = self.base_url + "get_video"
        url += "?source=" + source
        url += "&cor_id=" + self.cor_id
        r = requests.post(url, verify=False).content
        if len(r) < 50:
            try:
                r = json.loads(r)
                return False
            except "JSONDecodeError":
                pass
        return r

    async def clean_ts(self):
        url = self.base_url + "clean"
        url += "?cor_id=" + self.cor_id
        r = json.loads(requests.post(url).content)
        if isinstance(r, dict) and "status" in r.keys() and r["status"] == 0:
            return True
        return False


@app.post("/sign_up")
async def root(first_name: str = "", last_name: str = "", password: str = ""):
    db_model = DB()
    res1 = db_model.insert("users", {"firstname": first_name, "lastname": last_name})
    if not res1:
        return {"message": "Error: try again later"}
    res2 = db_model.insert("user_password", {"user_id": res1, "password": password})
    if not res2:
        db_model.delete("users", res1)
        return {"message": "Error: try again later"}
    return {"message": "User %s %s was signed up. id: %d" % (first_name, last_name, res1)}


@app.post("/get_access_token")
async def root(user_id: int = "", password: str = ""):
    db_model = DB()
    db_model.cursor.execute("SELECT COUNT(*) FROM user_password WHERE user_id = %d AND password = %s" % (user_id,
                                                                                                         password))
    if db_model.cursor.fetchone():
        current_time = datetime.datetime.now().timestamp()
        db_model.cursor.execute("DELETE FROM authorization WHERE user_id = %d AND end >= %d" % (user_id, current_time))
        new_token = str(int(datetime.datetime.now().timestamp())) + "_" + str(uuid.uuid4())
        end_time = current_time + 30 * 60
        db_model.db_connection.commit()
        db_model.insert("authorization", {"token": new_token,
                                          "user_id": user_id,
                                          "end": end_time})
        return {"access_token": new_token,
                "valid_until": datetime.datetime.fromtimestamp(end_time).strftime('%H:%M:%S')}
    return {"message": "Authorization error: wrong user_id or password"}


@app.post("/m1_yolo")
async def root(video: fastapi.UploadFile = fastapi.File(...), confidence: float = "0.5",
               non_max_suppression: float = "0.5", token: str = ""):
    user_id = check_token(token)
    if not user_id:
        return {"message": "Authorization error: invalid access token"}
    cor_id = "m1_yolo" + token
    ts_model = TS(cor_id)
    queue_sender_model = QueueSender(cor_id)
    _ = await ts_model.put_video_to_ts(video.file.read())
    message = {"confidence": confidence, "non_max_suppression": non_max_suppression,
               "cor_id": cor_id, "method": "m1_yolo"}
    _ = queue_sender_model.send(message)
    video_response = await ts_model.get_video_from_ts()
    # await ts_model.clean_ts()
    return fastapi.Response(content=video_response,
                            media_type="video/mp4",
                            headers={"filename": "output.mp4", "content-disposition": "attachment"})
