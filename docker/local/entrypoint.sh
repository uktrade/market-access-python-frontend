#!/usr/bin/env bash

# Django Migrations
python manage.py makemigrations
python manage.py migrate
npm run build
python manage.py collectstatic --no-input

echo -e "╔══════════════════════════════════════════════════════╗"
echo -e "                👏  Ready to roll!  👏                 "
echo -e "╠══════════════════════════════════════════════════════╣"
echo -e "║  - To list all available make commands               ║"
echo -e "║    run 'make help'.                                  ║"
echo -e "╚══════════════════════════════════════════════════════╝"

# Allow any command to be run against the image
exec "$@"
