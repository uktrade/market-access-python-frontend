#!/usr/bin/env bash

echo "---- Apply Migrations ------"
python3 manage.py migrate

echo "---- Collect Static Files ------"
python3 manage.py collectstatic --noinput

echo "---- Compile SCSS ------"
python3 manage.py compress --force
