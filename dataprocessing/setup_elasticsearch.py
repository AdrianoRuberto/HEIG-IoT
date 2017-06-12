from elasticsearch import Elasticsearch
from argparse import ArgumentParser

es = Elasticsearch()

if es.indices.exists('data'):
    print("Removing index ...")
    es.indices.delete('data')

es.indices.create('data', {
    "mappings": {
        "events": {
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
        },
        "parking_stat": {
            "properties": {
                "parking": {
                    "type": "long"
                },
                "timestamp": {
                    "type": "date",
                    "format": "epoch_millis"
                },
                "count": {
                    "type": "long"
                }
            }
        }
    }
})