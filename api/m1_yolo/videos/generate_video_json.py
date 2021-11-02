with  open("car_chase_01.mp4", "br") as f:
    data = f.read()
data = b'{"confidence": 0.5, "non_max_suppression": 0.5, "video_source": "nodb", "video": "' + data + b'"}'
with open("json_string.txt", "bw+") as f:
    f.write(data)
