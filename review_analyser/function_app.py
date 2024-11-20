import json
import logging
import azure.functions as func
from azure.functions.decorators.core import DataType
import spacy
import pathlib
import asent
import requests
import time

app = func.FunctionApp()


# This function triggers based on changes in an SQL database that is constantly updated
# with new customer reviews. This function will perform sentiment analysis, average the ratings
# and extract sentences that mention the timeliness of service
@app.sql_trigger(
    arg_name="reviewTableTriggerBinding",
    table_name="customer_reviews",
    connection_string_setting="SqlConnectionString",
)
def review_analyser(reviewTableTriggerBinding: str) -> None:

    # Load new revies
    db_changes = json.loads(reviewTableTriggerBinding)
    logging.info(db_changes)

    # Filter out deletions or updates to rows to prevent errors
    new_reviews = [item for item in db_changes if item.get("Operation") == 0]

    # Calculate number of reviews
    num_reviews = len(new_reviews)

    # If there were only deletions or updates, exit to prevent errors
    if len(new_reviews) == 0:
        return

    logging.info(f"Number of reviews extracted: {num_reviews}")

    # Extract the text portion of the reviews
    review_texts = [item["Item"]["review_text"] for item in new_reviews]

    # Extract the ratings and store them in the list
    review_ratings = [item["Item"]["rating"] for item in new_reviews]

    # Initialise spacy model and add pipeline components
    model = get_spacy_model()
    model.add_pipe("sentencizer")
    model.add_pipe("asent_en_v1")

    # Empty list for storage review sentiment that will be averaged later
    sentiment_scores = []

    # Empty list for sentences that mention time
    temporal_sentences = []

    # Iterate through reviews and perform analysis
    for doc in model.pipe(
        review_texts,
        disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"],
    ):

        # Extract sentences that mention times, store them in the list
        for sent in doc.sents:
            if any(ent.label_ == "TIME" for ent in sent.ents):
                temporal_sentences.append(sent.text)

        # Perform sentiment analysis and store the "compound" metric in the list
        sentiment = doc._.polarity
        sentiment_scores.append(sentiment.compound)

    # Create an average of all the sentiment scores
    if sentiment_scores:
        average_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        logging.info(f"Average sentiment: {average_sentiment}")

    # Create an average of all the review ratings
    if review_ratings:
        average_rating = sum(review_ratings) / len(review_ratings)
        logging.info(f"Average rating: {average_rating}")

    logging.info(f"Sentences that mention time: {temporal_sentences}")

    # Notify the manager of the calculated metrics
    notify_manager(num_reviews, average_rating, average_sentiment, temporal_sentences)

    return


# The spaCy en_core_web_lg model is manually uploaded to the function app
# Its path is determined relative to the container and loaded in based on that
def get_spacy_model():

    path = pathlib.Path(__file__).parent / "en_core_web_md/en_core_web_md-3.8.0"

    model = spacy.load(path)

    return model


# Send a notification with the analysis to the managers mobile device using NTFY.sh
def notify_manager(num_reviews, average_rating, average_sentiment, temporal_sentences):

    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)

    summary = (
        f"Time of analysis: {current_time}\n"
        f"Number of reviews analysed: {num_reviews}\n"
        f"Average Rating: {average_rating:.2f}\n"
        f"Average Sentiment: {average_sentiment:.2f}\n"
    )

    if temporal_sentences:
        summary += "Sentences mentioning time:\n" + "\n".join(temporal_sentences) + "\n"

    # Post request contining summary to NTFY.sh, this can be subscribed to on the manager's smartphone
    requests.post(
        "https://ntfy.sh/BDATNmAG4qNtw2vMhQ", data=summary.encode(encoding="utf-8")
    )

    return
