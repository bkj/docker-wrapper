#!/bin/bash

redis-server &
cd /src && ./worker.py --model /scratch/model --io-threads 2 & 
cd /src && ./generic-app.py -w 2 -t 2