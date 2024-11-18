import spacy
import pathlib

texts = [
    "Net income was $9.4 million compared to the prior year of $2.7 million.",
    "Revenue exceeded twelve billion dollars, with a loss of $1b.",
]

path = pathlib.Path(__file__).parent / 'en_core_web_lg/en_core_web_lg-3.8.0'

print(str(path))

nlp = spacy.load(path)

for doc in nlp.pipe(texts, disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"]):
    # Do something with the doc here
    print([(ent.text, ent.label_) for ent in doc.ents])
