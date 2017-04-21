#!/bin/bash


redis-server &
cd /src && ./worker.py --model -m $MESOS_SANDBOX/$MODEL_PATH --io-threads 3 & 
cd /src && ./generic-app.py $SERVER_FLAGS