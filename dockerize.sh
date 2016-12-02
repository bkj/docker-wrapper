#!/bin/bash

# --
# Parse input

if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    exit 1
fi

config=$1
imname=$(cat $config | jq -r .image_name)

# --
# Create target directory

mkdir -p images

if [ -e images/$imname ]
then
    rm -r images/$imname
fi

mkdir images/$imname

# --
# Copy files

cp -r resources/* images/$imname/
cp resources/.dockerignore images/$imname/

cp ../`cat $config | jq -r .class` images/$imname/model_class.py
cp -r ../`cat $config | jq -r .model` images/$imname/model
cp -r ../`cat $config | jq -r .bootstrap` images/$imname/app-bootstrap
cat $config | jq -r '.additional | .[]' | xargs -I {} cp -r ../{} images/$imname/

cat $config | jq '{"model_name": .model_name, "description": .description, "rest_args": .rest_args}' > images/$imname/config.json
cp $config images/$imname/.docker-wrapper-config.json

# --
# Use different base image?
base_image=$(cat $config | jq -r ".base_image //empty")
if [[ $base_image ]]
then
    sed  -i 's@FROM .*@FROM '"$base_image"'@' images/$imname/Dockerfile
    sed  -i 's@FROM .*@FROM '"$base_image"'@' images/$imname/Dockerfile.deploy
fi

# --
# Use NVIDIA-docker?
gpu_flag=$(cat $config | jq -r ".gpu_flag //empty")
if [[ $gpu_flag ]]
then
    sed  -i 's/docker run/NV_GPU=1 sudo nvidia-docker run/' images/$imname/quickstart.sh
fi

# --
# Use non-`gunicorn` server?
legacy_flag=$(cat $config | jq -r ".legacy_flag //empty")
if [[ $gpu_flag ]]
then
    mv images/$imname/legacy-app.py images/$imname/generic-app.py
fi

tar -zcf images/$imname.tar.gz images/$imname