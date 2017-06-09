#!/usr/bin/env python

from elasticsearch import Elasticsearch
import argparse
import random
import uuid
import time

parser = argparse.ArgumentParser()
parser.add_argument('count', type=int)

args = parser.parse_args()

es_index = 'data-input'
es_type = 'events'
parking = 1
device = 'flir'
base_timestamp = int(time.time())
step_timestamp = 30
num_events = args.count

es = Elasticsearch()

if es.indices.exists(es_index):
    print("Removing index")
    es.indices.delete(es_index)

es.indices.create(es_index, {
    "mappings": {
        es_type: {
            "properties": {
                "parking": {
                    "type": "long"
                },
                "device": {
                    "type": "text"
                },
                "timestamp": {
                    "type": "date",
                    "format": "epoch_millis"
                },
                "type": {
                    "type": "text",
                    "fielddata": True
                }
            }
        }
    }
})

print("Generating Events ...")
for k in range(0, num_events):
    if k > 0 and k % 1000 == 0:
        print("generated ", k)
    
    timestamp = (base_timestamp + step_timestamp * k) * 1000
    if random.randint(0, 1):
        direction = 'in'
    else:
        direction = 'out'
    
    es.create(es_index, es_type, uuid.uuid4(), {
        "parking": parking,
        "device": device,
        "timestamp": timestamp,
        "type": direction
    })

print("generated ", num_events)
print("Done!")
