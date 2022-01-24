# import the necessary packages
from threading import Thread
import requests, time, json
import pandas as pd
import random, itertools

# CLASSIFY_API_URL = "http://0.0.0.0:5000/api/search/text/xc"
CLASSIFY_API_URL = "https://xc.tst03.platform.michaels.com/api/search/text/xc"

# initialize the number of requests for the stress test along with
# the sleep amount between requests
NUM_REQUESTS = 20
SLEEP_COUNT = 0.05
TEST_SAMPLE_SIZE = 100

df = pd.read_csv('query_records.csv')
input_list = random.sample(list(df['Term']), TEST_SAMPLE_SIZE)


def call_classify_endpoint(n):
    # load the input image and construct the payload for the request
    payload = {"query": input_list[random.randrange(TEST_SAMPLE_SIZE)]}

    headers = {
        'User-Agent': 'Stress Test',
        'From': 'fanglin@michaels.com'  # This is another valid field
    }

    # submit the request
    r = requests.post(CLASSIFY_API_URL, headers=headers, json=payload)
    print(r)
    # print(r.json())

    # ensure the request was sucessful
    if len(r.json().keys()):
        print("[INFO] thread {} OK".format(n))
    # # otherwise, the request failed
    else:
        print("[INFO] thread {} FAILED".format(n))


# loop over the number of threads
for i in range(0, NUM_REQUESTS):
    # start a new thread to call the API
    t = Thread(target=call_classify_endpoint, args=(i,))
    t.daemon = True
    t.start()
    time.sleep(SLEEP_COUNT)
# insert a long sleep so we can wait until the server is finished
# processing the images
time.sleep(300)
