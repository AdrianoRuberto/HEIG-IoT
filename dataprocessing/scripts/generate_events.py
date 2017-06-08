#!/usr/bin/env python

from cassandra.cluster import Cluster
import random
import uuid
import time

cluster = Cluster(['127.0.0.1'])
session = cluster.connect('data')

parking = 1
device = 'flir'
base_timestamp = int(time.time())
step_timestamp = 30
num_events = 10000

print("Generating Events ...")
for k in range(0, num_events):
    if k > 0 and k % 1000 == 0:
        print("generated ", k)
    
    timestamp = (base_timestamp + step_timestamp * k) * 1000
    if random.randint(0, 1):
        direction = 'in'
    else:
        direction = 'out'
    
    session.execute("""
        insert into events(event_id, parking, device, timestamp, type)
        values(%s, %s, %s, %s, %s)
    """, (uuid.uuid4(), parking, device, timestamp, direction))

print("generated ", num_events)
print("Done!")
