import string
from nltk.corpus import stopwords
from names_dataset import NameDataset
import os
from google.cloud import pubsub_v1

from app.main.recommender.features._text import TextClean
from app.main.database.mongodb import PymongoConnection
from app.main.util.snowflake_id_generator import SnowflakeIDGenerator

from app.main.configuration.vault_vars_config import PUBSUB_CREDENTIAL

"""
Initialize global variables, which could be used by the API multi times, to avoid:
1. Latency caused by crating the object
2. Memory overflow
"""
names_set = NameDataset()

"""
Following is the count for suggested store names
"""
suggested_store_name_count = 5

"""
Initialize text_clean
Add single characters to stop_words
"""
stop_words = set(stopwords.words("english"))
alphabet = string.ascii_lowercase
for char in alphabet:
    stop_words.add(char)
text_clean = TextClean(
    text_cols=["search_term"],
    fill_na=False,
    lemmatization=True,
    stop_words=stop_words,
    rejoin=True,
)

"""
Get dimension of word embedding vectors
"""
rec_connection = PymongoConnection("mongo_rec", "recWordEmbedding")
word_vector_length = len(
    rec_connection.get_collection_instance().find().limit(1).next()["vector"]
)

rec_ngram_word_embedding_connection = PymongoConnection(
    "mongo_rec", "recWordEmbeddingNgram"
)
ngram_word_vector_length = len(
    rec_ngram_word_embedding_connection.get_collection_instance()
    .find()
    .limit(1)
    .next()["vector"]
)

"""
The gcp publisher
"""
gcp_publisher = pubsub_v1.PublisherClient.from_service_account_json(PUBSUB_CREDENTIAL)

"""
The snowflake ID generator
"""
snowflake_id_generator = SnowflakeIDGenerator(
    worker_id=1, data_center_id=1
).snowflake_generator()

"""
The redis hash key for ad item status
"""
ad_items_status_redis_hkey = "ads:products:sku:status"

"""
user_agent used in the http header
"""
user_agent = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0"
)
