#!/usr/bin/env bash

# Django Migrations
pipenv run python manage.py makemigrations
pipenv run python manage.py migrate
pipenv run python manage.py collectstatic --no-input

echo -e "╔══════════════════════════════════════════════════════╗"
echo -e "                👏  Ready to roll!  👏                 "
echo -e "╠══════════════════════════════════════════════════════╣"
echo -e "║  - To list all available make commands               ║"
echo -e "║    run 'make help'.                                  ║"
echo -e "╚══════════════════════════════════════════════════════╝"

# tail a file to keep the container alive
tail -f /dev/null
