import click
import time
import json
import random
import faker
import uuid

from datetime import datetime
from confluent_kafka import Producer
import socket



@click.command()
@click.option('--topic', help ='the kafka topic. audit_log_demo by default', default='audit_log_demo')
@click.option('--sample', type=int, default=10_000)
@click.option('--sleep', type=float, default=1)
@click.option('--mps', help='number of messages per sleep (by default 200, and as by default sleep is 1, 200 messages/s',type=int, default=200)
@click.option('--repeat', type=int, default=1)
@click.option('--bootstrap-servers')
@click.option('--security_protocol', default='SASL_SSL')
@click.option('--sasl_mechanism', default='PLAIN')
@click.option('--sasl_plain_username')
@click.option('--sasl_plain_password')
@click.option('--utc', help='UTC datetime for tmstmp by default', type=bool, default=True)
@click.option('--bcp', is_flag=True, default=False)
def produce(topic,
            sample,
            sleep,
            mps,
            repeat,
            bootstrap_servers,
            security_protocol,
            sasl_mechanism,
            sasl_plain_username,
            sasl_plain_password,
            utc,
            bcp):
  
  conf = {
    'bootstrap.servers': bootstrap_servers,
    'client.id': socket.gethostname(),
    'security.protocol': security_protocol,
    'sasl.mechanism': sasl_mechanism,
    'sasl.username': sasl_plain_username,
    'sasl.password': sasl_plain_password,
    'compression.type': 'lz4'
    }

  producer = Producer(conf)
  fake = faker.Faker()
  cus_emails = [fake.email() for s in range(max(10,int(sample/10)))]

  onqueue = -1
  t = time.time()
  for _ in range(repeat):

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
  
    
    for i in range(sample):
      message = {
        'datetime': datetime.utcnow().isoformat(),
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
      msg=json.dumps(message).encode('utf-8')

      print(message)   
      producer.produce(topic, value=msg)

      onqueue += 1
      while onqueue >= mps:
        before_onqueue = onqueue
        time.sleep(sleep)
        onqueue = producer.flush(2)
        sent = before_onqueue - onqueue
        dt = time.time() - t
        print(f"Uploading rate: {int(sent/dt)} messsages/second. {i} of {sample}")
        t = time.time()

    if sleep:
      producer.flush()
      time.sleep(sleep)
      print(f'{sample} sent! {_+1} of {repeat} - {datetime.now()}')
    producer.flush()

if __name__ == '__main__':
    produce()
