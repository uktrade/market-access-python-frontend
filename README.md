# Market Access Python Frontend

This repository provides a frontend client to consume the Market Access API.

## Installation with Docker (preferred)

Market Access Python Frontend uses Docker compose to setup and run all the necessary components. \
The docker-compose.yml file provided is meant to be used for running tests and development.

#### Prerequisites
1. Install `docker` & `docker compose` - https://docs.docker.com/install/
2. Add the following to your `hosts` file:

        # Market Access Frontend Client (Python)
        127.0.0.1               market-access.local
3. Clone the repository:
    ```shell
    git clone https://github.com/uktrade/market-access-python-frontend.git
    cd market-access-python-frontend
    ```
4. Copy the env file - `cp docker-compose.local-template.env docker-compose.env`         

#### Install
1. Build the images and spin up the containers by running - `docker-compose up --build`
2. Set up git hooks by running - `make git-hooks`
3. Enter bash within the django container using `docker-compose exec web bash`  
then create a superuser `py3 manage.py createsuperuser --email your@email.here`
4. To start the dev server run - `make django-run`
5. The fronted client is now accessible via http://market-access.local:9880

#### Running in detached mode
The installation steps above will require 2 terminal windows to be open to run the processes.
If desired this can be reduced to 0 via the following commands:
1. Start the containers in detached mode - `docker-compose up -d`
2. Start django in detached mode - `make django-run-detached`
3. The frontend client is now accessible via http://market-access.local:9880

Now even if you closed your terminal, the server would be still running.

#### Make commands
There's a set of make commands that you can utilize straight away. \
To list all available commands with help text type `make help` in terminal and hit `Enter`.

-----
