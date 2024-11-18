import json
import logging
import azure.functions as func
from azure.functions.decorators.core import DataType
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
import pathlib

app = func.FunctionApp()


@app.sql_trigger(
    arg_name="reviewTableTriggerBinding",
    table_name="customer_reviews",
    connection_string_setting="SqlConnectionString",
)
def review_analyser(reviewTableTriggerBinding: str) -> None:

    #logging.info("SQL Changes: %s", json.loads(reviewTableTriggerBinding))

    new_reviews = json.loads(reviewTableTriggerBinding)

    review_texts = [item['Item']['review_text'] for item in new_reviews]

    model = get_spacy_model()

    for doc in model.pipe(review_texts, disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"]):
        # Do something with the doc here
        logging.info([(ent.text, ent.label_) for ent in doc.ents])

    return

# The spaCy en_core_web_lg model is manually uploaded
# Its path is determined and loaded into the spaCy module
def get_spacy_model():

    path = pathlib.Path(__file__).parent / 'en_core_web_lg/en_core_web_lg-3.8.0'

    model = spacy.load(path)

    logging.info("spaCy model path:" + str(path))

    return model
