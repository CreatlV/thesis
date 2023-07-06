from fastapi import Body, FastAPI, HTTPException, UploadFile, File
import logging
from pydantic import BaseModel
from starlette.responses import JSONResponse
import torch
from PIL import Image
import io
from fastapi.middleware.cors import CORSMiddleware
from transformers import (
    ConditionalDetrImageProcessor,  # type: ignore
    ConditionalDetrForObjectDetection,  # type: ignore
)
from dotenv import load_dotenv
import os
from huggingface_hub import HfApi, HfFolder
import base64
from io import BytesIO
import openai
from lm.openai_parser import ModelType, extract_dictionary_from_text
from lm.dict_match import get_html_xpath_from_dict

from lm.html_utils import clean_html, download_html_and_text
from lm.xpath_scraper import extract_data_from_html

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

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

TARGET_SIZE = 1280

logging.basicConfig(level=logging.INFO)

adapted_domains = dict()

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
    width, height = image.size
    scale_factor = TARGET_SIZE / width

    # Resize the width to the target size and scale the height proportionally
    resized_img = image.resize((TARGET_SIZE, int(height * scale_factor)))

    # Calculate coordinates to crop the height to the target size
    top = 0
    bottom = TARGET_SIZE

    # Crop the image
    cropped_img = resized_img.crop((0, top, TARGET_SIZE, bottom))
    buffered = BytesIO()
    cropped_img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    logging.info(f"Recieved an image!")

    image_input = image_processor(images=cropped_img, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model(**image_input)

    if outputs is not None:
        postprocessed_outputs = image_processor.post_process_object_detection(
            outputs, 0.5, target_sizes=[(TARGET_SIZE, TARGET_SIZE)]
        )
        print(postprocessed_outputs)

        serialized_item = {}

        for item in postprocessed_outputs:
            for key, tensor in item.items():
                serialized_item[key] = tensor.detach().cpu().numpy().tolist()

        return JSONResponse(content={**serialized_item, "processed_image": img_str})

    return JSONResponse(content={"message": "Something went wrong!"})


class Website(BaseModel):
    url: str


@app.post("/lm/predict")
async def lm_predict(website: Website):
    logging.info(f"Recieved a url: {website.url}")
    visible_text, html_string = await download_html_and_text(
        website.url, use_cache=False
    )
    model: ModelType = "gpt-3.5-turbo"
    openai_response = extract_dictionary_from_text(model, visible_text)

    return JSONResponse(content={"gpt": openai_response, "text": visible_text})

@app.post("/lm/adapt")
async def lm_adapt(website: Website):
    logging.info(f"Recieved a url: {website.url}")
    visible_text, html_string = await download_html_and_text(
        website.url, use_cache=False
    )
    logging.info(f"Text downloaded")
    model: ModelType = "gpt-4"
    
    logging.info("Sending to Open-AI")
    openai_response = extract_dictionary_from_text(model, visible_text)
    cleaned_html = clean_html(html_string)

    logging.info("Extracting xpaths")
    xpath_dict = get_html_xpath_from_dict(openai_response, cleaned_html, keys_to_ignore=["currency"])

    ## Extract domain from url
    domain = website.url.split("/")[2]
    adapted_domains[domain] = xpath_dict
    logging.info(f"Adapted domain: {domain}")

    return JSONResponse(content={"xpaths": xpath_dict, "domains": adapted_domains})

@app.post("/lm/extract")
async def lm_extract(website: Website):
    logging.info(f"Recieved a url: {website.url}")
    domain = website.url.split("/")[2]
    if domain not in adapted_domains:
        raise HTTPException(status_code=400, detail=f"Domain {domain} not found in adapted domains!")
    
    visible_text, html_string = await download_html_and_text(
        website.url, use_cache=False
    )
    cleaned_html = clean_html(html_string)

    
    xpath_dict = adapted_domains[domain]
    data = extract_data_from_html(xpath_dict, html_string=cleaned_html)

    return JSONResponse(content={"data": data})