#!/bin/bash

docker kill $(docker ps -q) 
docker build -t docker_analytic .
docker run -it -p 5000:5000 -v $(cat model_path):/scratch/model/ docker_analytic