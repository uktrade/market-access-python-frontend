#!/bin/bash

# get test file name from command line argument
$target=$1

# activate python virtual environment
source .venv/bin/activate

# install python dependencies if not already installed
pip install -r requirements.txt

ENV_FILE="docker-compose.env"

# load environment variables
export $(cat $ENV_FILE | sed 's/#.*//g' | xargs)

# run playwright with pytest
PWDEBUG=0 pytest test_frontend/$target

# deactivate python virtual environment
deactivate
