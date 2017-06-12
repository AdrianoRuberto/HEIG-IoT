from elasticsearch import Elasticsearch
import uuid
import time
import pprint

pp = pprint.PrettyPrinter(indent=4)

class IotData:
    def __init__(self, es_node_addr):
        self.es = Elasticsearch(es_node_addr)
    
    def add_event(self, parking, timestamp, device, typ):
        return self.es.create('data', 'events', uuid.uuid4(), {
            "parking": parking,
            "timestamp": timestamp,
            "device": device,
            "type": typ
        })
    
    def get_count(self, parking, timestamp=None):
        if not timestamp:
            timestamp = time.time()
        
        last_stat_resp = self.es.search('data', 'parking_stat', {
            "size": 1,
            "query": {
                "bool": {
                    "filter": [
                        { "term" : { "parking": 1 } },
                        { "range": { "timestamp": { "lt": int(timestamp) * 1000 } } }
                    ]
                }
                
            },
            "sort": [
                { "timestamp" : { "order": "desc" } }
            ]
        })

        last_stat = last_stat_resp['hits']['hits'][0]['_source']

        acc_resp = self.es.search('data', 'events', {
            "size": 0,
            "query": {
                "bool": {
                    "filter": [
                        { "term": { "parking": parking } },
                        { "range": { "timestamp": { "gte": last_stat['timestamp'] } } }
                    ]
                }
            },
            "aggs": {
                "in_count": {
                    "filter": { "term": { "type": "in" } }
                },
                "out_count": {
                    "filter": { "term": { "type": "out" } }
                }
            }
        })

        in_count = acc_resp['aggregations']['in_count']['doc_count']
        out_count = acc_resp['aggregations']['out_count']['doc_count']
        delta = in_count - out_count

        return last_stat['count'] + delta
    
    def get_stats(self, parking, date_from, date_to, granularity, device=None):
        return self.es.search('data', 'parking_stat', {
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
                        "avg_count": {
                            "avg": { "field": "count" }
                        }
                    }
                }
            }
        })

    def get_deltas(self, parking, date_from, date_to, granularity, device=None):
        return self.es.search('data', 'events', {
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
                        }
                    }
                }
            }
        })