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

def process_product(title, description, procedure) -> dict:
    # This makes the Product pydantic model injectable into the prompt
    pydantic_parser = PydanticOutputParser(pydantic_object=Product)
    
    # Defines contextual information about how the LLM should respond and how to interpret the upcomming user message
    system_message = """You are a Dutch administrative assistant tasked with presenting the information of a product offered by the Flemish Government in a clear way. Your job is to extract all necessary information asked by the user and provide it in a specified format."""
    extraction_instructions=pydantic_parser.get_format_instructions()
    
    # Clear instruction on what the LLM should do
    user_message = f"""Extract the fields specified bellow. Be complete but only return relevant information. If the field is not in the text, you can answer with None.
    {extraction_instructions}
    
Given the following information in Dutch:
    
    -Title (is the name of the product or service): {title}
    -Description (is the description of the product or service): {description}
    -Procedure (procedure or steps that the user should take or consider regarding the product or service): {procedure}
    
    Please reformulate the information in a way that is comprehensive considering that it is official governmental information for citizens. The output should also be in Dutch.
    Take into account the following points:

    1. Highlight the service or product related to the query based on the title, summarizing the description (if any) of that product or service.
    2. Mention the requirements or prerequisites (if any) related to the product or service using simple bullet points that are easy to follow. Note that you can find additional description points in the requirements. Pay attention to the information to present it clearly.
    3. Mention the procedure or steps (if any) that the user should consider or take. Note that the procedure is complementary to requirements and/or prerequisites and, in some cases, could not add additional relevant info. If no procedure is mentioned, state: "No additional procedure found"
    4. Try not to repeat information, and also spot relevant fields that can be mentioned separately based on the information, like to whom it is specifically directed, special notes, etc.
    5. You may find symbols or HTML links that are not relevant and should be avoided in the response/output. So, add relevant information, be careful if the information has no sense based on the context.
    6. Important: DO NOT ADD additional information if is not provided in the data. Avoid adding information that was not given, if there is no specific information that is relevant, better to mention that "There is no more relevant info".
    7. Important: the output should be in the Dutch language.

    This is an example:

    title = "Europese blauwe kaart voor hoogopgeleide vreemdelingen",
    description = "Hoogopgeleide buitenlanders kunnen onder bepaalde voorwaarden gedurende meer dan 90 dagen in Vlaanderen wonen en werken. In dat geval kan hun toekomstige werkgever een Europese blauwe kaart voor hen aanvragen..",
    requirement = "Europese blauwe kaart kan een werknemer die niet de nationaliteit van een lidstaat van de EER</a> of Zwitserland heeft, meer dan 90 dagen in België werken en verblijven. De regelgeving is de omzetting van de Europese Richtlijn (van 2009/50 van 25 mei 2009) voor de voorwaarden voor toegang en verblijf van onderdanen van derde landen met het oog op een hooggekwalificeerde baan."
    procedure = "De toekomstige werkgever vraagt de Europese blauwe kaart"

    An output for this data could be something like:

    "Europese blauwe kaart voor hoogopgeleide vreemdelingen.

    Dankzij deze dienst kunnen hoogopgeleide buitenlanders onder bepaalde voorwaarden langer dan 90 dagen in Vlaanderen wonen en werken. Je toekomstige werkgever kan dit aanvragen.

    Doelgroep / Vereisten:

    - Buitenlandse werknemer die lid is van de EER of Zwitserland.

    Procedure:

    - De toekomstige werkgever moet de Europese blauwe kaart aanvragen.

    Andere relevante informatie:

    De verordening is de omzetting van de Europese richtlijn (van 2009/50 van 25 mei 2009) betreffende de voorwaarden voor toegang en verblijf van onderdanen van derde landen met het oog op een hooggekwalificeerde baan."

Your output consists only out of a JSON object containing ONLY the fields specified above and their corresponding value, extracted from the text. Return only the JOSN object, no other words/phrases before or after!
    """
    
    model_name = "llama3.2" # TODO: DEFINE
    temperature = 0.1
    host = "http://ollama:11434/" # TODO: DEFINE
    seed = 42
    
    messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
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
    
    product_as_dict = process_product(product["title"]["value"], product["description"]["value"], product["procedureDescription"]["value"])

    # TODO: DO SOMETHING WITH product_as_dict

    print(product_as_dict, flush=True)

    return product_as_dict

print("This is our code <3")
