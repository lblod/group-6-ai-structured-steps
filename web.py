from flask import request
import logging
from sparql import query_product_with_uri
from langchain.output_parsers import PydanticOutputParser
from parser_class import Product
from model_config import ModelConfig
from ollama import Client
import json

# setup logging
logging.basicConfig(level=logging.INFO, format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M")
logging.info('logger initialised')

def parse_json(response: str) -> str:
    response = response.replace(u'\xa0', u' ')
    response = response.replace("```json", "")
    response = response.replace("```", "")
    return response

def process_product(product: str) -> dict:
    # This makes the Product pydantic model injectable into the prompt
    pydantic_parser = PydanticOutputParser(pydantic_object=Product)
    
    # Defines contextual information about how the LLM should respond and how to interpret the upcomming user message
    system_message = """You are a Dutch administrative assistant tasked with presenting the information of a product offered by the Flemish Government in a clear way. Your job is to extract all necessary information asked by the user and provide it in a specified format."""
    
    # Clear instruction on what the LLM should do
    user_message = """Extract the fields specified bellow. Be complete but only return relevant information. If the field is not in the text, you can answer with None.
    {extraction_instructions}
    
    The text is:
    {text}
    Your output consists only out of a JSON object containing ONLY the fields specified above and their corresponding value, extracted from the text. Return only the JOSN object, no other words/phrases before or after!"""
    
    model_name = "llama3.2" # TODO: DEFINE
    temperature = 0.1
    host = "http://ollama:11434/" # TODO: DEFINE
    seed = 42
    
    messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message.format(text = product, extraction_instructions=pydantic_parser.get_format_instructions())}
            ]
    
    config = ModelConfig(model_name, system_message=system_message, user_message=user_message, temperature=temperature, seed=seed)
    
    llama_client = Client(host=host)
    
    response = llama_client.chat(config.model, messages=messages, options={"ctx_length": 16384, "temperature": config.temperature}, format='json')["message"]
    if not isinstance(response, str):
        response = response['content']
    extraction = parse_json(response)
    
    return json.loads(extraction)

@app.route("/get_structured_steps", methods=["GET"])
def ingest():
    uri = request.args.get('uri')
    logging.info(f'start process of finding structured steps for product {uri}')
    
    product = query_product_with_uri(uri)[0] # take one
    print(product, flush=True)

    productString = "Product title: {} Procedure description: {} Product description: {}".format(product["title"]["value"], product["procedureDescription"]["value"], product["description"]["value"])
    
    product_as_dict = process_product(productString) # Currently assumed that product and its information will be provided as string

    # TODO: DO SOMETHING WITH product_as_dict

    print(product_as_dict, flush=True)

    return product_as_dict

print("This is our code <3")
