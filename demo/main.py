from fastapi import FastAPI, UploadFile, File
import logging
from starlette.responses import JSONResponse
import torch
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import io
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# origins = [
#     "http://localhost:5173",  # Replace with the origin of your client application
# ]

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

# model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32').to(device)
# processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')

# Preprocessing for images
# transform = Compose([
#     Resize([224, 224]),
#     ToTensor(),
#     Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711))
# ])


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    logging.info(f"Recieved an image!")

    # image_input = transform(image).unsqueeze(0).to(device)

    # with torch.no_grad():
    #     image_features = model.get_image_features(image_input)

    # image_features = image_features.cpu().numpy().tolist()
    # return JSONResponse(content={"image_features": image_features})

    return JSONResponse(content={"bounding_boxes": []})
