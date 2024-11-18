import json
import logging
import azure.functions as func
from azure.functions.decorators.core import DataType
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob

app = func.FunctionApp()


@app.sql_trigger(
    arg_name="reviewTableBinding",
    table_name="customer_reviews",
    connection_string_setting="SqlConnectionString",
)
def review_analyser(reviewTableBinding: str) -> None:
    logging.info("SQL Changes: %s", json.loads(reviewTableBinding))

    print(get_spacy_path())
    nlp = spacy.load(get_spacy_path())


# Function from https://williamandrewgriffin.com/best-way-to-deploy-spacy-to-azure-functions/
# Used to deploy a spacy model to azure functions
def get_spacy_path():
    current_path = pathlib.Path(__file__).parent.parent
    return str(current_path / "en_core_web_lg-2.2.5")
