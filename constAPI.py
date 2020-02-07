import requests
from dotenv import load_dotenv
from pathlib import Path  # python3 only
import os

env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("API_KEY")

headers = {"Authorization": "Bearer {}".format(API_KEY)}
owner = os.getenv("OWNER")

sample_repo = "amazon_for_test"
sample_search_string = "DJANGO_SETTINGS_MODULE"
sample_regex = "^s"


# A simple function to use requests.post to make the API call. Note the json= section.
def run_query(query):
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        result = request.json()
        # print(result)
        if "data" in result:
            return result["data"]
        return "Err"
    else:
        return "Err"
        # raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def run_query_v3(query):
    request_str = 'https://api.github.com/%s' % query
    request = requests.get(request_str, headers=headers)

    if request.status_code == 200:
        result = request.json()
        # print(result)
        return result
    else:
        return ""
        # raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

