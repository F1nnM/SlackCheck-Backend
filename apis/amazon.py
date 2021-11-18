import requests
import time
import dateutil.parser
import functools
from environs import Env

env = Env()
API_KEY = env("API_KEY")

def _create_job(query):
    url = "https://price-analytics.p.rapidapi.com/job"

    payload = "source=amazon&key=term&country=de&values={}".format(query)
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'x-rapidapi-host': "price-analytics.p.rapidapi.com",
        'x-rapidapi-key': API_KEY
        }

    response = requests.request("POST", url, data=payload, headers=headers).json()

    print(response)

    if response['error']:
        return None
    else:
        return response['jobid']

def _get_job_results(jobid, iter_depth=0):
    if iter_depth > 4:
        return None
    time.sleep(15)
    url = "https://price-analytics.p.rapidapi.com/job/{}".format(jobid)

    headers = {
        'x-rapidapi-host': "price-analytics.p.rapidapi.com",
        'x-rapidapi-key': API_KEY
        }

    response = requests.request("GET", url, headers=headers).json()

    print(response)

    if "results" not in response:
        return _get_job_results(jobid, iter_depth=iter_depth+1)
    else:
        return response['results'][0]['content']['offers'], response['results'][0]['updated_at']

#clean up the results
def _clean_up_data(results, timestamp):
    clean_results = []
    for result in results:
        clean_results.append({
            'name': result['name'],
            'price': result['price'],
            'url': "https://amazon.de/dp/"+result['asin'],
            'platform': 'Amazon',
            'history_id': 'amazon'+result['asin'],
            'history_timestamp': timestamp,
        })
    return clean_results

@functools.cache
def get_items_by_search(query):
    jobid = _create_job(query)
    if jobid is None:
        return []
    results, timestamp = _get_job_results(jobid)

    timestamp = dateutil.parser.isoparse(timestamp).timestamp()

    if results is None:
        return []
    return _clean_up_data(results, timestamp)
    