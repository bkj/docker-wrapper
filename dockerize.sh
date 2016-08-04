#!/bin/bash

# --
# Parse input

if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    exit 1
fi

config=$1
imname=$(cat config.json | jq -r .image_name)

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

cp resources/* images/$imname/
cp `cat $config | jq -r .class` images/$imname/model_class.py
cp -r `cat $config | jq -r .model` images/$imname/model
cp `cat $config | jq -r .bootstrap` images/$imname/bootstrap.sh
cat $config | jq -r '.additional | .[]' | xargs -I {} cp -r {} images/$imname/
cat $config | jq '{"description" : .description, "rest_args" : .rest_args}' > images/$imname/config.json
cp $config images/$imname/.docker-wrapper-config.json

tar -zcf images/$imname.tar.gz images/$imname