#!/bin/bash

docker kill $(docker ps -q) 
docker build -t docker_analytic .
docker run -t -p 5000:5000 -v $(pwd):/scratch/ docker_analytic