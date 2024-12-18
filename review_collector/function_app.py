import logging
import json
import random
import uuid
import azure.functions as func
from azure.functions.decorators.core import DataType

app = func.FunctionApp()


# This function collates reviews from 3 different review APIs and stores them in the azure database
# It is called based on a timer, so for example could be called every 30 minutes or at 5pm every day at the close of business
# Note that each API call for review collection actually uses processed and simplified dummy data from the Yelp reviews dataset
# Real life implementation examples are given in the docstring of each helper function
@app.schedule(
    schedule="0 0 * * * *",
    arg_name="collectionTimer",
    run_on_startup=True,
    use_monitor=False,
)
@app.generic_output_binding(
    arg_name="reviewTableBinding",
    type="sql",
    CommandText="dbo.customer_reviews",
    ConnectionStringSetting="SqlConnectionString",
    data_type=DataType.STRING,
)
def review_collector(
    collectionTimer: func.TimerRequest, reviewTableBinding: func.Out[func.SqlRow]
) -> None:

    # Open the file that contains the dummy reviews
    with open("sorted_modified_reviews.json", "r") as file:
        dataset = json.load(file)

    # Collect and collate the reviews from each source
    new_reviews = (
        collect_google(dataset)
        + collect_tripadvisor(dataset)
        + collect_trustpilot(dataset)
    )

    # Commit the reviews to a DB, note that this is done in a batch to reduce individual operations
    if new_reviews:
        logging.info(new_reviews)
        batch_reviews = [
            func.SqlRow(
                {
                    "db_review_id": str(uuid.uuid4()),
                    "api_review_id": str(review["review_id"]),
                    "rating": int(review["stars"]),
                    "review_text": str(review["text"]),
                }
            )
            for review in new_reviews
        ]
        reviewTableBinding.set(batch_reviews)

    return


# Note that in the real implementation of the following functions, we would implement some logic to filter out only
# reviews that are new. We could check the date of the review and compare it to the previous function invocation


# Collects reviews from the Google reviews API
# Real life example implementation:
# headers = {"Authorization": "Bearer ACCESS_TOKEN"}
# reviews = requests.get("https://mybusiness.googleapis.com/v4/accounts/{account_id}/locations/{location_id}/reviews", headers=headers)
def collect_google(dataset):

    logging.info("Collecting reviews from Google")

    reviews = []

    # Simulate that there may or may not be new review(s)
    if random.choices([0, 1], weights=[0.3, 0.7], k=1)[0] == 1:

        # Randomly pick some reviews from the dataset
        reviews = random.sample(dataset, random.randint(1, 12))

    return reviews


# Collects reviews from the Tripadvisor content API
# Real life example implementation:
# headers = {"accept": "application/json"}
# reviews = response = requests.get("https://api.content.tripadvisor.com/api/v1/location/locationId/reviews?language=en", headers=headers)
def collect_tripadvisor(dataset):

    logging.info("Collecting reviews from Tripadvisor")

    reviews = []

    # Simulate that there may or may not be new review(s)
    if random.choices([0, 1], weights=[0.8, 0.2], k=1)[0] == 1:

        # Randomly pick between 1 and 3 reviews from the dataset
        reviews = random.sample(dataset, random.randint(1, 3))

    return reviews


# Collects reviews from the Trustpilot business units API
# Real life example implementation:
# headers = {"apikey": "key"}
# reviews = response = requests.get("https://api.trustpilot.com/v1/private/business-units/{businessUnitId}/reviews", headers=headers)
def collect_trustpilot(dataset):

    logging.info("Collecting reviews from Trustpilot")

    reviews = []

    # Simulate that there may or may not be new review(s)
    if random.choices([0, 1], weights=[0.9, 0.1], k=1)[0] == 1:

        # Pick a review from the dataset
        reviews = random.sample(dataset, 1)

    return reviews
