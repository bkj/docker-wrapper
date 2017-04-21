#!/bin/bash

apt-get clean && apt-get update
apt-get install -y git build-essential redis-server
pip install -r requirements.txt
