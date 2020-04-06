# Market Access Python Frontend

This repository provides a frontend client to consume the Market Access API.
It's built with python django. 

## Installation with Docker (preferred)

Market Access Python Frontend uses Docker compose to setup and run all the necessary components. \
The docker-compose.yml file provided is meant to be used for running tests and development.

#### Prerequisites
1. Install `docker` & `docker compose` - https://docs.docker.com/install/
2. Add the following to your `hosts` file:
    ```
    # Market Access Frontend Client (Python)
    127.0.0.1               market-access.local
    ```
3. Clone the repository:
    ```shell
    git clone https://github.com/uktrade/market-access-python-frontend.git
    cd market-access-python-frontend
    ```
4. Copy the env file - `cp docker-compose.local-template.env docker-compose.env`

#### Install
Please note that as of Jan 2020 you will need to run the containers from https://github.com/uktrade/market-access-api/ first \
as they currently share some dependencies (this only applies for local development).  
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


#### Staticfiles
Staticfiles are compressed offline for most environments, so it makes sense that you could run the same way locally to test things out. 
To do that, just: 
1. stop the django development server 
2. set `DEBUG` to `False` in `config/settings/local.py`
3. run `make django-static`
4. start the django development server

**Note:** this is a good way to mimic how files are generated and served in an environment, \
but please note, lazy loading of static files is also disabled in offline mode, so your changes to templates, js, scss \
might not take effect unless you run step 3 from above and restart your dev server.


## Builds
Builds can be initiated from Jenkins or from the command line using `cf` CLI tool (using `cf push <app_name>`).
To use `cf push` you will need to be in the root of the project.

The preferred way to deploy apps remains Jenkins as of now because Jenkins will set environment variables as part of the flow. 

#### Init Tasks
Tasks that should be run at app initialisation can be defined in `.profile` file.
If you would like to check the output of that you can do so via `cf logs <app_name> --recent`, but 
please note that these logs get trimmed so it's best to check straight after deployment. 


## Tests
Front end tests are grouped under `./test` directory. When writing tests please use the corresponding app name to keep the same folder structure as the main app so it's easy to tell which test belongs to which app.

#### Running Django Tests
The project's testrunner is pytest - https://docs.pytest.org/en/latest/
1. You can run all or a subset of tests via `make django-test`, if you pass in a value in `path` then it will run that subset of tests.
Example usage.:
	- `make django-test` - run all tests
	- `make django-test path=barriers` - run a subset of tests just for the barriers app
	- `make django-test path=assessments/test_assessment_detail.py::EmptyAssessmentDetailTestCase::test_view` - run a specific test case
2. To run tests with coverage use `make django-test-coverage` - this will output the report to the console.

#### Running Selenium Tests Locally
1. Ensure the API is running locally.

2. Spin up the testing container:
`docker-compose -f docker-compose.test.yml -p market-access-test up -d`
This consists of the python frontend and the selenium chrome driver.

3. Run the tests:
`make django-ui-test-with-server`
This will start the frontend `runserver`, run the tests, then end `runserver`

#### Running Selenium Tests Against UAT
1. Ensure you are on the VPN.

2. Edit docker-compose.test.env:
WEB_DRIVER_URL=http://chrome:4444/wd/hub
TEST_BASE_URL=https://market-access-pyfe-uat.london.cloudapps.digital/
TEST_BARRIER_ID=0e78b943-df63-4fa7-9620-23fdf972286e
TEST_SSO_LOGIN_URL=https://sso.trade.uat.uktrade.io/login/
TEST_SSO_EMAIL=lite-team-1@digital.trade.gov.uk
TEST_SSO_PASSWORD=See lite-e2e-internal-frontend job on Jenkins
TEST_SSO_NAME=1 Lite-team

Note that webops have told us to use the lite team's test SSO user for now.

3. Spin up the testing container:
`docker-compose -f docker-compose.test.yml -p market-access-test up -d`

4. Run the tests:
`make django-ui-test`

Ideally we would be able to run this from CircleCI and change WEB_DRIVER_URL to point to BrowserStack (https://USERNAME:API_KEY@hub-cloud.browserstack.com/wd/hub). However this presents a few difficulties, such as getting around the VPN, so for now we can just run the end to end tests from our local machines against UAT.

-----
