import fastapi
from .config import VIDEO_PATH, OUTPUT_PATH
from .yolo import detect_objects


app = fastapi.FastAPI()


@app.post("/m1_yolo")
async def root(video: fastapi.UploadFile = fastapi.File(...), confidence: float = "0.5",
               non_max_suppression: float = "0.5", video_source: str = "nodb"):
    if video_source == "db":
        pass
    else:
        test_video = video.filename
        with open(config.VIDEO_PATH + test_video, "bw+") as f:
            f.write(video.file.read())
    print(f"[INFO] Processing Video....")
    total, elap = detect_objects(VIDEO_PATH + test_video, confidence, non_max_suppression)
    output_video = open(OUTPUT_PATH, 'rb')
    video_bytes = output_video.read()
    print(f"[INFO] The video has total of {total} frames")
    print(f"[INFO] Time required to process a single frame: {round(elap / 60, 2)} minutes")
    print(f"[INFO] Time required to process the entire video: {round((elap * total) / 60, 2)} minutes")
    return fastapi.Response(content=video_bytes, media_type="video/mp4", headers={"filename": "output.mp4",
                                                                                  "content-disposition": "attachment"})
