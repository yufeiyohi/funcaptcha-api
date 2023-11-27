import base64
import hashlib
import json
import time
from io import BytesIO
from PIL import Image

from app.routers.openai_arkose.funcaptcha_server.roll_animal_siamese_model import RollAnimalSiameseModel

animal_model = RollAnimalSiameseModel("model.onnx")


def process_image(base64_image, model):
    if base64_image.startswith("data:image/"):
        base64_image = base64_image.split(",")[1]
    image_bytes = base64.b64decode(base64_image)
    image_like_file = BytesIO(image_bytes)
    image = Image.open(image_like_file)
    return int(model.predict(image))


def process_data(data):
    client_key = data["clientKey"]
    task_type = data["task"]["type"]
    image = data["task"]["image"]
    question = data["task"]["question"]

    ans = {
        "errorId": 0,
        "errorCode": "",
        "status": "ready",
        "solution": {}
    }

    taskId = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()
    ans["taskId"] = taskId

    if question == "4_3d_rollball_animals":
        ans["solution"]["objects"] = [process_image(image, animal_model)]
    else:
        ans["errorId"] = 1
        ans["errorCode"] = "ERROR_TYPE_NOT_SUPPORTED"
        ans["status"] = "error"
        ans["solution"]["objects"] = []

    return ans
