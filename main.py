import base64
import hashlib
import time
from io import BytesIO

from PIL import Image
from fastapi import FastAPI, HTTPException, Request
from funcaptcha_challenger import predict
from pydantic import BaseModel

from util.log import logger
from util.model_support_fetcher import ModelSupportFetcher

app = FastAPI()
PORT = 8181
IS_DEBUG = True
fetcher = ModelSupportFetcher()


class Task(BaseModel):
    type: str
    image: str
    question: str


class TaskData(BaseModel):
    clientKey: str
    task: Task


def process_image(base64_image: str, variant: str):
    if base64_image.startswith("data:image/"):
        base64_image = base64_image.split(",")[1]

    image_bytes = base64.b64decode(base64_image)
    image = Image.open(BytesIO(image_bytes))

    ans = predict(image, variant)
    logger.debug(f"predict {variant} result: {ans}")
    return ans


@app.post("/createTask")
async def create_task(data: TaskData):
    client_key = data.clientKey
    task_type = data.task.type
    image = data.task.image
    question = data.task.question
    ans = {
        "errorId": 0,
        "errorCode": "",
        "status": "ready",
        "solution": {}
    }

    taskId = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()
    ans["taskId"] = taskId
    if question in fetcher.supported_models:
        ans["solution"]["objects"] = [process_image(image, question)]
    else:
        ans["errorId"] = 1
        ans["errorCode"] = "ERROR_TYPE_NOT_SUPPORTED"
        ans["status"] = "error"
        ans["solution"]["objects"] = []

    return ans


@app.get("/support")
async def support():
    # 从文件中读取模型列表
    return fetcher.supported_models


@app.exception_handler(Exception)
async def error_handler(request: Request, exc: Exception):
    logger.error(f"error: {exc}")
    return {
        "errorId": 1,
        "errorCode": "ERROR_UNKNOWN",
        "status": "error",
        "solution": {"objects": []}
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)