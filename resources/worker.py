#!/usr/bin/env python

"""
    worker.py
"""

import sys
import redis
import argparse
import ujson as json

from multiprocessing import Process, Queue
from Queue import Empty

from redis_external import RedisExternal
from model_class import Worker

# --
# Params

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', help='Specify model file.', type=str, required=True)
    parser.add_argument('--io-threads', type=int, default=1)
    parser.add_argument('--timeout', type=int, default=60000)
    return parser.parse_args()

# --
# Worker classes

def do_io(external, model, io_queue, args):
    print >> sys.stderr, 'worker.do_io: started'
    while True:
        try:
            response_queue, req = external.read()
            try:
                obj, err = model.load(req)
                io_queue.put((response_queue, req, obj, err))
            except:
                print >> sys.stderr, "worker.do_work: uncaught error:" % req
                io_queue.put((response_queue, req, None, 501))
        except KeyboardInterrupt:
            raise
        except Empty:
            return
        except:
            raise

def do_work(external, model, io_queue, args):
    print >> sys.stderr, 'worker.do_work: started'
    while True:
        try:
            response_queue, req, obj, err = io_queue.get(timeout=args.timeout)
            if not err:
                pred, err = model.predict(req, obj)
                external.write(response_queue, (req, pred, err))
            else:
                print >> sys.stderr, "worker.do_work: error getting from IO queue"
                external.write(response_queue, (req, None, err))
        except KeyboardInterrupt:
            os._exit(0)
        except Empty:
            print >> sys.stderr, "worker.do_work: io_queue is empty"
        except:
            print >> sys.stderr, "worker.do_work: uncaught error:" % req

# --
# Run

if __name__ == "__main__":
    args = parse_args()
    config = json.load(open('/src/config.json'))
    
    external = RedisExternal()
    model = Worker(args.model, config['model_name'])
    io_queue = Queue()
    
    # IO threads
    for _ in range(args.io_threads):
        io_worker = Process(target=do_io, args=(external, model, io_queue, args))
        io_worker.start()
    
    # Work thread (only one for now)
    do_work(external, model, io_queue, args)
