from dacite import from_dict
import openai
from typing import Literal, Union
import json


from lm.models.openai import APIResponse

ModelType = Union[Literal["gpt-3.5-turbo"], Literal["gpt-4"]]

def extract_dictionary_from_text(model: ModelType, text: str) -> dict:

  prompt: str = f"""From the following HTML text answer a json object with the following strucutre, answer the json object and nothing else:
  productName: string
  originalPrice: number
  currentPrice: number
  currency: string
  description: string
  specifications: string[]

  {text}"""
          

  response = openai.ChatCompletion.create(
      model=model,
      messages=[
          {
              "role": "user",
              "content": prompt,
          },
      ],
      max_tokens=500,
  )

  print(response)


  response_parsed = from_dict(APIResponse, response) # type: ignore

  return json.loads(response_parsed.choices[0].message.content)

  ## TODO: Add a check to see if the response is valid json
  ## TODO: Add a check to see if the response contains the required fields

  ## TODO: find the HTML from the json object
  ## TODO: pre-process the HTML, look at scrape ghost
  ## TODO: check if original spacing shuold be kept
