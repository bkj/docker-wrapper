#!/usr/bin/env python

"""
    redis_external.py
"""

import redis
import ujson as json
from uuid import uuid4

class RedisExternal(object):
    def __init__(self, queue_name="worker"):
        self.con = redis.Redis()
        self.queue_name = queue_name
    
    def clear(self):
        _ = self.con.delete(self.queue_name)
        
    def read(self, queue=None):
        if not queue:
            queue = self.queue_name
        
        _, obj = self.con.blpop(queue)
        return json.loads(obj)
    
    def write(self, queue, obj):
        _ = self.con.rpush(queue, json.dumps(obj))
        return None
    
    def rand_write(self, obj):
        rand_queue_name = self.queue_name + ':rpc:' + str(uuid4())
        _ = self.con.rpush(self.queue_name, json.dumps((rand_queue_name, obj)))
        return rand_queue_name