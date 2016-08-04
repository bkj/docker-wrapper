#!/bin/bash

docker kill $(docker ps -q) 
docker build -t docker_wrapper .
docker run -t -p 5000:5000 docker_wrapper
