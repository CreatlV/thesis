# Thesis


## Demo

The demo consists of two parts.
1. FastAPI server that runs the model inference.
2. UI written in React

Start the fastAPI server using `uvicorn main:app --host 0.0.0.0 --port 8989`
Start the UI using `yarn dev`

Ensure that the required dependencies are installed. 
Tested with Node 18 and python 3.10.6 in the docker container. 

The demo expects a `HUGGINGFACE_TOKEN` and `OPENAI_API_KEY` with GPT-4 access to work fully as expected.

## Training
Finetune_DETR.ipynb together with the other files in the /src directory contains all requirements to train replicate the results. 

The training expects a `HUGGINGFACE_TOKEN`, but would work if limited to public datasets and models.  
