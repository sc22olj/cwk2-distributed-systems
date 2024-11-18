import json
import logging
import azure.functions as func
from azure.functions.decorators.core import DataType

app = func.FunctionApp()


@app.sql_trigger(
    arg_name="reviewTableBinding",
    table_name="customer_reviews",
    connection_string_setting="SqlConnectionString",
)
def review_analyser(reviewTableBinding: str) -> None:
    logging.info("SQL Changes: %s", json.loads(reviewTableBinding))
