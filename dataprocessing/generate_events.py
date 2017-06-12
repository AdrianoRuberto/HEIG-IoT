#!/usr/bin/env python

from elasticsearch import Elasticsearch
import argparse
import random
import uuid
import time

parser = argparse.ArgumentParser()
parser.add_argument('--count', type=int, default=1000)
parser.add_argument('--when', type=int, default=int(time.time()))
parser.add_argument('--range', type=int, default=3600 * 24 * 15)

args = parser.parse_args()

es_index = 'data'
es_type = 'events'
parking = 1
device = 'flir'
base_timestamp = args.when
num_events = args.count

es = Elasticsearch()

print("Generating Events ...")
for k in range(0, num_events):
    if k > 0 and k % 1000 == 0:
        print("generated ", k)
    
    timestamp = (base_timestamp + random.randint(-args.range, args.range)) * 1000
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
