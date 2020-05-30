from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from requests_futures.sessions import FuturesSession
from requests.exceptions import ConnectionError
from time import time
import json
import csv
import logging
import uuid
import asyncio
import argparse

logging.basicConfig(filename='./test-api.log',
                    level=logging.INFO,
                    filemode='w',
                    format='%(asctime)s:%(levelname)s:%(message)s')

#creating a class from Futures Session to use hooks and track time elapsed() for every hit
class ElapsedFuturesSession(FuturesSession):

    def request(self, method, url, hooks={}, *args, **kwargs):
        start = time()

        def timing(r, *args, **kwargs):
            r.elapsed_secs = time() - start

        try:
            if isinstance(hooks['response'], (list, tuple)):
                # needs to be first so we don't time other hooks execution
                hooks['response'].insert(0, timing)
            else:
                hooks['response'] = [timing, hooks['response']]
        except KeyError:
            hooks['response'] = timing

        return super(ElapsedFuturesSession, self) \
            .request(method, url, hooks=hooks, *args, **kwargs)


with open('config.json') as f:
    configs =  json.load(f)

#parse args from command line if running locally
parser = argparse.ArgumentParser()
parser.add_argument("--url",help="url of api to be rate tested")
parser.add_argument("--hitrate", type=int, help="no of api hits per sec")
parser.add_argument("--duration", type=int, help="duration of the test")
args = parser.parse_args()

#default to values from config file if args are not provided
url = args.url or configs["api_url"]
hitrate = args.hitrate or configs["hits_per_sec"]
duration = args.duration or configs["duration"]


#generate a unique test_Id for each run
test_Id = uuid.uuid1()
start_time = time()
logging.info('Triggering api rate test with testId=%s to url=%s with hitrate=%s requests per second for duration=%s seconds',test_Id,url,hitrate,duration)

#method to execute n calls asynchronously using request_futures session
async def send_requests():
    while True:
        with ElapsedFuturesSession(executor=ThreadPoolExecutor(max_workers=10)) as session:
            futures = [session.get(url) for i in range(hitrate)]
            for future in as_completed(futures):
                #adding try block since exceptions are thrown while calling the future.result()
                try:
                    resp = future.result()
                    if resp.status_code != 200:
                        logging.info('Request failed for Api=%s in ttlb=%s seconds ',url,resp.elapsed)
                    else :
                        #logging resp.elapased as ttlb and resp.elapsed_secs(returned from hook) as time after the run was triggered and a particular request was sent along with other details
                        logging.info('Request succeeded with responseCode=%s during test_Id=%s in %s secs for Api=%s with ttlb=%s seconds and data=%s',resp.status_code,test_Id,resp.elapsed_secs,url,resp.elapsed,resp.json())
                except ConnectionError as e:
                    #logging error if unable to connect to host
                    logging.error('Error connecting to url=%s in test_Id=%s : %s',url,test_Id,e)
        await asyncio.sleep(1)

def stop():
    task.cancel()

#using asycio loop to repeat the hits every second
loop = asyncio.get_event_loop()
loop.call_later(duration, stop)
task = loop.create_task(send_requests())

try:
    loop.run_until_complete(task)
except asyncio.CancelledError as e:
    logging.error('Test loop cancelled  for test_Id=%s : %s',test_Id,e)
    pass
logging.info('Rate test completed  for testId=%s in %s seconds',test_Id,time()-start_time)
