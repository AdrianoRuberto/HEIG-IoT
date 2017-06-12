from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
from argparse import ArgumentParser
from pprint import PrettyPrinter
import uuid

pp = PrettyPrinter(indent=2)

parking = 1

es = Elasticsearch()

last_parking_stat_resp = es.search('data', 'parking_stat', {
  "size": 1,
  "query": {
    "term" : {
      "parking": parking
    }
  },
  "sort": [
    { "timestamp" : { "order": "desc" } }
  ]
})

if last_parking_stat_resp['hits']['total'] == 0:
    print("No last value!")
    exit(1)

last_parking_stat = last_parking_stat_resp['hits']['hits'][0]['_source']
last_parking_count = last_parking_stat['count']

print("Last Value:", "{count} at {timestamp}".format(**last_parking_stat))

aggregates_resp = es.search('data', 'events', {
    "size": 0,
    "query": {
        "bool": {
            "filter": [
                { "term": { "parking": parking } },
                { "range": {
                    "timestamp": {
                        "gte": last_parking_stat['timestamp']
                    }
                } }
            ]
        }
    },
    "aggs": {
        "by_interval" : {
            "date_histogram": {
                "field": "timestamp",
                "interval": "15m",
                "format": "yyyy-MM-dd HH:mm"
            },
            "aggs": {
                "in_count": {
                    "filter": { "term": { "type": "in" } },
                    "aggs" : {
                        "count": {
                            "value_count": {
                                "field": "type"
                            }
                        }
                    }
                },
                "out_count": {
                    "filter": { "term": { "type": "out" } },
                    "aggs" : {
                        "count": {
                            "value_count": {
                                "field": "type"
                            }
                        }
                    }
                },
                "delta": {
                    "bucket_script": {
                        "buckets_path": {
                            "in": "in_count>count",
                            "out": "out_count>count"
                        },
                        "script": "params.in - params.out"
                    }
                },
                "counter": {
                    "cumulative_sum": {
                        "buckets_path": "delta"
                    }
                }
            }
        }
    }
})

def make_insert_query(bucket):
    if bucket['key'] == last_parking_stat['timestamp']:
        return None
    
    query = {
        "_op_type": "create",
        "_index": "data",
        "_type": "parking_stat",
        "_id": "{:d}-{:d}".format(parking, bucket['key']),
        "parking": parking,
        "timestamp": bucket['key'],
        "count": last_parking_count + bucket['counter']['value']
    }
    print("{_id}: {count} at {timestamp}".format(**query))
    return query

if len(aggregates_resp['aggregations']['by_interval']['buckets']) > 0:
    parking_stats = map(
        make_insert_query,
        aggregates_resp['aggregations']['by_interval']['buckets']
    )

    results = streaming_bulk(es, filter(lambda ps: ps, parking_stats))
    for ok, result in results:
        print(result['create']['_id'])
else:
    print("Stats up to date")