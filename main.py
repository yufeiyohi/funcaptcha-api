import base64
import hashlib
import json
import time
from io import BytesIO

from flask import Flask, jsonify, request
from PIL import Image

from roll_animal_siamese_model import RollAnimalSiameseModel

app = Flask(__name__)
PORT = 8181

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

    return jsonify(ans)


# curl --location --request POST 'http://127.0.0.1:8191/createTask' \
# --header 'Content-Type: application/json' \
# --data-raw '{
#     "clientKey": "bb11d056130b5e41f3d870edfa21c6a4",
#     "task": {
#         "type": "FunCaptcha",
#         "image": "data:image/jpeg;base64,base64图片编码"
#         "question": "4_3d_rollball_animals"
#     }
# }'
@app.route("/createTask", methods=["POST"])
def create_task():
    # 获取请求数据
    data = request.get_json()
    return process_data(data)


# 捕获异常
@app.errorhandler(Exception)
def error_handler(e):
    return jsonify({
        "errorId": 1,
        "errorCode": "ERROR_UNKNOWN",
        "status": "error",
        "solution": {"objects": []}
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=PORT)
