from elasticsearch import Elasticsearch
import uuid

class IotData:
    def __init__(self, es_node_addr):
        self.es = Elasticsearch(es_node_addr)
    
    def add_event(self, parking, timestamp, device, typ):
        return self.es.create('data-input', 'events', uuid.uuid4(), {
            "parking": parking,
            "timestamp": timestamp,
            "device": device,
            "type": typ
        })
    
    def get_stats(self, parking, date_from, date_to, granularity, device=None):
        return self.es.search('data-input', 'events', {
            "size": 0,
            "query": {
                "bool": {
                    "filter": [
                        { "term": { "parking": parking } },
                        { "range": { "timestamp": { "gte": date_from * 1000, "lt": date_to * 1000 } } }
                    ]
                }
            },
            "aggs": {
                "by_interval" : {
                    "date_histogram": {
                        "field": "timestamp",
                        "interval": granularity,
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