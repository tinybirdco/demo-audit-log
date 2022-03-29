import requests
import json
from datetime import datetime, timedelta
import click
import random
from faker import Faker
import uuid

def send_event(ds: str, token: str, messages: list):
  params = {
    'name': ds,
    'token': token,
    'wait': 'false',
  }
  data = '\n'.join(json.dumps(m) for m in messages)
  r = requests.post('https://api.tinybird.co/v0/events', params=params, data=data)
  # uncomment the following two lines in case you don't see your data in the datasource
  # print(r.status_code)
  # print(r.text)

@click.command()
@click.option('--datasource', help ='the destination datasource', default='audit_log_hfi')
@click.option('--sample', help = 'number of messages simulated in each repetition', type=int, default=100)
@click.option('--events', help = 'number of events per request. Sent as NDJSON in the body', type=int, default=87)
@click.option('--repeat', type=int, default=1)
@click.option('--silent', is_flag=True, default=False)
def send_hfi(datasource,
             sample,
             events,
             repeat,
             silent
             ):
 
  with open ("./.tinyb") as tinyb:
    token = json.load(tinyb)['token']
   
  fake = Faker()

  for _ in range(repeat):

    sample = sample + random.randint(0, int(events/10))

    rand_browsrers_weights = [x + y for x, y in zip([45,8,21,15], [random.randint(-3,12) for _ in range(4)])]
    rand_OSs_weights = [x + y for x, y in zip([41,20,32,65,80], [random.randint(-10,22) for _ in range(5)])]
    rand_entities_weights = [x + y for x, y in zip([6,1,90,33,15], [random.randint(-1,4) for _ in range(5)])]
    rand_actions_weights = [x + y for x, y in zip([2,50,1], [random.randint(1,15) for _ in range(3)])]
    
    browsers = random.choices(['Chrome','Brave','Firefox','Safari'],weights=rand_browsrers_weights,k=sample)
    OSs = random.choices(['Windows','Linux','OSX','iOS','Android'],weights=rand_OSs_weights,k=sample)
    entities = random.choices(['user','group','file','folder','project'], weights=rand_entities_weights, k=sample)
    entity_ids = [uuid.uuid4().hex for s in range(sample)]
    actions = random.choices(['created','updated','deleted'], weights=rand_actions_weights,k=sample)
    company_names=['tinybird','auditlog-company','example','speedwins','realtime-dataproducts']
    companies = random.choices(company_names, weights=[random.randint(1,10) for c in company_names], k=sample)
  
    nd = []
    
    for i in range(sample):
      message = {
        'datetime': datetime.utcnow().isoformat() ,
        'company_id': company_names.index(companies[i])+1,
        'event': f'{entities[i]}_{actions[i]}',
        'payload':  {
          'entity_id': entity_ids[i],
          'author': f'{fake.email().replace("example",companies[i])}'
            },
        'device': {
          'browser': browsers[i],
          'OS': OSs[i]
          }
        }
      nd.append(message) 
      if len(nd) == events:
        send_event(datasource, token, nd)
        nd = []
      if not(silent):
       print(message) 
    send_event(datasource, token, nd)
    nd = []


if __name__ == '__main__':
    send_hfi()