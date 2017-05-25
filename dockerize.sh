#!/bin/bash

DW_VERSION=2

# --
# Parse input

if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    exit 1
fi

config=$1
imname=$(jq -r .image_name $config)
config_version=$(jq -r ".dw_version //empty" $config)

if [ -n "$config_version" ]; then
    if [ $config_version != $DW_VERSION ]; then
        echo "Versions don't match: $config_version vs $DW_VERSION"
        exit 1
    fi;
fi;

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
cp ../`jq -r .class $config` images/$imname/model_class.py
jq -r '.additional | .[]' $config | xargs -I {} cp -r ../{} images/$imname/
jq '{"model_name": .model_name, "description": .description, "rest_args": .rest_args}' $config > images/$imname/config.json
cp $config images/$imname/.docker-wrapper-config.json

# --
# Symlink model

jq -r .model_path $config > images/$imname/model_path

# --
# Bootstrap image
bootstrap_flag=$(jq -r ".bootstrap //empty" $config)
if [[ $bootstrap_flag ]]
then
    cp -r ../`jq -r .bootstrap $config` images/$imname/app-bootstrap    
else
    mkdir -p images/$imname/app-bootstrap 
    echo "#!/bin/bash" > images/$imname/app-bootstrap/bootstrap.sh
fi

# --
# Use different base image?
base_image=$(jq -r ".base_image //empty" $config)
if [[ $base_image ]]
then
    sed  -i 's@FROM .*@FROM '"$base_image"'@' images/$imname/Dockerfile
    sed  -i 's@FROM .*@FROM '"$base_image"'@' images/$imname/Dockerfile.deploy
fi

# --
# Use NVIDIA-docker?
gpu_flag=$(jq -r ".gpu_flag //empty" $config)
if [[ $gpu_flag ]]
then
    sed  -i 's/docker run/NV_GPU=1 nvidia-docker run/' images/$imname/quickstart.sh
fi

# --
# Use non-`gunicorn` server?
legacy_flag=$(jq -r ".legacy_flag //empty" $config)
if [[ $legacy_flag ]]
then
    mv images/$imname/legacy-app.py images/$imname/generic-app.py
fi

tar -zcf images/$imname.tar.gz images/$imname