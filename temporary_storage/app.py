import fastapi
import os
import re
INPUT_DIR = "/opt/temporary_storage/input/"
OUTPUT_DIR = "/opt/temporary_storage/output/"


app = fastapi.FastAPI()


@app.post("/put_video")
async def root(video: fastapi.UploadFile = fastapi.File(...), source: str = "input"):
    if source == "output":
        file_path = OUTPUT_DIR + video.filename
    else:
        file_path = INPUT_DIR + video.filename
    with open(file_path, "wb+") as f:
        f.write(video.file.read())
    return {"status": 0}


@app.post("/get_video")
async def root(cor_id: str = "", source: str = "input"):
    if source == "output":
        file_path = OUTPUT_DIR + cor_id + ".mp4"
    else:
        file_path = INPUT_DIR + cor_id + ".mp4"
    if os.path.isfile(file_path):
        with open(file_path, "rb") as f:
            video_bytes = f.read()
        return fastapi.Response(content=video_bytes,
                                media_type="video/mp4",
                                headers={"filename": cor_id + ".mp4", "content-disposition": "attachment"})
    return {"message": "Error: file doesn't exist"}


@app.post("/clean")
async def root(cor_id: str = ""):
    file_name = "%s.mp4" % cor_id
    if os.path.isfile(OUTPUT_DIR + file_name):
        os.remove(OUTPUT_DIR + file_name)
    if os.path.isfile(INPUT_DIR + file_name):
        os.remove(INPUT_DIR + file_name)
    return {"status": 0}

