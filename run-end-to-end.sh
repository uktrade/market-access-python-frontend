#!/bin/bash

# activate python virtual environment
source .venv/bin/activate

# install python dependencies if not already installed
pip install -r requirements.txt

ENV_FILE="docker-compose.env"

# load environment variables
export $(cat $ENV_FILE | sed 's/#.*//g' | xargs)

# run playwright with pytest
pytest test_frontend/

# deactivate python virtual environment
deactivate
