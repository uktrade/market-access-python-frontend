#!/usr/bin/env bash
# This script is being run in the ci-pipeline
# for more info see https://github.com/uktrade/ci-pipeline-config/pull/158

echo "---- Apply Migrations ------"
python3 manage.py migrate

echo "---- Compile SCSS ------"
python3 manage.py compress -f

echo "---- Collect Static Files ------"
python3 manage.py collectstatic --noinput -i *.scss --clear
