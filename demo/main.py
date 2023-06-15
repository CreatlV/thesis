from fastapi import FastAPI, UploadFile, File
import logging
from starlette.responses import JSONResponse
import torch
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize
from PIL import Image
import io
from fastapi.middleware.cors import CORSMiddleware
from transformers import (
    ConditionalDetrImageProcessor,
    ConditionalDetrForObjectDetection,
)
from dotenv import load_dotenv
import os
from huggingface_hub import HfApi, HfFolder

load_dotenv()
token = os.getenv("HUGGINGFACE_TOKEN")
if token is None:
    raise ValueError("Missing huggingface token!")

api = HfApi()
api.token = token
folder = HfFolder()
folder.save_token(token)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)

# Load pre-trained model
device = "cuda" if torch.cuda.is_available() else "cpu"
logging.info(f"Using device: {device}")
image_processor = ConditionalDetrImageProcessor()
categories = {0: "price", 1: "title", 2: "image"}
id2label = categories
label2id = {v: k for k, v in id2label.items()}

model = ConditionalDetrForObjectDetection.from_pretrained(
    "CreatlV/conditional-detr-resnet-50_fine_tuned_cova_v2",
    num_labels=len(categories.keys()),
    id2label=id2label,
    label2id=label2id,
    ignore_mismatched_sizes=True,
    num_queries=20,
)

model.to(device)
model.eval()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    logging.info(f"Recieved an image!")

    image_input = image_processor(images=image, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model(**image_input)

    if outputs is not None:
        postprocessed_outputs = image_processor.post_process_object_detection(
            outputs, 0.5, target_sizes=[(1280, 1280)]
        )
        print(postprocessed_outputs)

        serialized_output = []

        for item in postprocessed_outputs:
            serialized_item = {}
            for key, tensor in item.items():
                serialized_item[key] = tensor.detach().cpu().numpy().tolist()
            serialized_output.append(serialized_item)


        return JSONResponse(
            content={
                "data": serialized_output
            }
        )

    return JSONResponse(content={"bounding_boxes": []})
