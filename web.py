from flask import request
import logging
from sparql import query_product_with_uri

# setup logging
logging.basicConfig(level=logging.INFO, format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M")
logging.info('logger initialised')

@app.route("/get_structured_steps", methods=["POST"])
def ingest(uri):

    logging.info(f'start process of finding structured steps for product {uri}')
    product = query_product_with_uri(uri)[0] # take one
    print(product)
    # todo: make structured


    return "RESULT"
