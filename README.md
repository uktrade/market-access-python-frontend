# Market Access Python Frontend

This repository provides a frontend client to consume the Market Access API.
It's built with python django.

## Background
The Market Access frontend was originally a node project:
https://github.com/uktrade/market-access-frontend

It was converted into Django from December 2019 to around February 2020. As a result, most of the css, javascript and html markup were copied directly across.

## Installation with Docker (preferred)

Market Access Python Frontend uses Docker compose to setup and run all the necessary components. \
The docker-compose.yml file provided is meant to be used for running tests and development.

#### Prerequisites
1. Install `docker` & `docker compose` - https://docs.docker.com/install/
2. Add the following to your `hosts` file:
    ```
    # Market Access Frontend Client (Python)
    127.0.0.1               market-access.local

    # Mock SSO
    127.0.0.1               mocksso
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
4. Whilst still in the container `run npm install` then `exit` the container
4. To start the dev server run - `make django-run`
5. The fronted client is now accessible via http://market-access.local:9880
6. run `make dev` - this will run the relevant gulp tasks (compile & watch CSS and JS files) and launch BrowserSync

##### BrowserSync auto-reload:
When you visit the site via http://127.0.0.1:9881 BrowserSync will automatically reload the page when you modify scss or js files.


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
The project is using CSS and fonts from `govuk-frontend` npm package.

Resources for GOV.UK Frontend:
- https://frontend.design-system.service.gov.uk/#gov-uk-frontend
- https://github.com/alphagov/govuk-frontend/tree/master/src/govuk

Fonts are copied while css is imported from node modules.
To prepare staticfiles for local run `make dev`

Staticfiles are compressed offline for most environments, so it makes sense that you could run the same way locally to test things out.
To do that, just:
1. stop the django development server (if it's running)
2. set `DEBUG` to `False` in `config/settings/local.py`
3. run `npm run build` for a one off run (or `make dev` if you want to recompile css and js real time when changes are saved)
3. run `make django-static`
4. start the django development server

**Note:** this is a good way to mimic how files are generated and served in an environment, \
but please note, lazy loading of static files is also disabled in offline mode, so your changes to templates, js, scss \
might not take effect unless you run step 3 from above and restart your dev server.
To keep watching and recompiling css and js file use `make dev` from step 3.

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

#### Running End to End tests using playwright with pytest
Playwright documentation - https://playwright.dev/python/docs/api/class-playwright

The end-to-end frontend tests reside in the test_frontend directory and are designed to operate independently of the rest of the application. This autonomy is facilitated through a local pytest.ini configuration file located within the same directory. The pytest.ini file configures specific parameters and settings essential for the execution of these tests, ensuring they can run in a self-contained environment. For detailed customization options and further information on pytest configuration files, refer to the [pytest configuration docs](https://docs.pytest.org/en/7.0.x/reference/customize.html)

If you are running the docker build

1. Ensure the API is running & the frondent service is runing and can be access on `http://localhost:{frontend_port}` or http://host.docker.internal:9880 if runing within the docker container

2. Ensure the frontend server is up and has reached the point where the Django development server is running.

By default the tests DO NOT RUN in headless mode, to activate headless mode the variable --is-headless will be required.

3. Run the tests:
`make test-end-to-end target_url=<target-url>` e.g target_url: `http://localhost:9880/` or `https://market-access.uat.uktrade.digital/`

4. To run a specific suite of frontend tests, specify the desired module:
`make test-end-to-end target_url=<target-url> target=test_examples.py`

To run headless:
`make test-end-to-end target_url=http://localhost:9880/ is-headless=true`

#### setup pytest & playwright end to end module

___module structure___

```
frontend_test/
├── .gitignore # Specifies intentionally untracked files to ignore
├── requirements.txt # Project dependencies
├── conftest.py # the pytest config file (the most important file to get things going)
├── README.md # The top-level README for developers using this project
└── pytest.ini # Configuration file for pytest
└── test_file.py # one test file for a specific end to end functionality
...
```
Inside the `conftest.py` file the functions below would be required to be implemented as shown.

```python
# conftest.py

BASE_URL = os.getenv("BASE_FRONTEND_TESTING_URL", "http://testserver/")
HEADLESS = os.getenv("TEST_HEADLESS", "false").lower() == "true"

@pytest.fixture(scope="session")
def session_data():
    """Return a dictionary to store session data."""
    return {
        "cookies": None,
        "barrier_id": None,
    }

@pytest.fixture(scope="session")
def playwright_instance():
    """Return a Playwright instance."""
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright_instance):
    """Return a browser instance."""
    if HEADLESS:
        browser = playwright_instance.chromium.launch(headless=True)
    else:
        browser = playwright_instance.chromium.launch(slow_mo=100, headless=HEADLESS)
    yield browser
    browser.close()

@pytest.fixture(scope="session")
def context(browser, session_data):
    # Create a new browser context
    context = browser.new_context()
    context.set_default_timeout(0)

    # Initially, session_data["cookies"] will be None.
    # Check if "cookies" key exists and has a value; if not, it means it's the first test run.
    if session_data.get("cookies") is None:
        # Since it's the first run, let the browser context initiate and capture the cookies.
        session_data["cookies"] = context.cookies()
    else:
        # If it's not the first run, load the initially captured cookies into the context.
        context.add_cookies(session_data["cookies"])

    yield context
    context.close()

@pytest.fixture(scope="session")
def page(context):
    # Create a new page in the provided context
    _page = context.new_page()
    _page.goto(BASE_URL, wait_until="domcontentloaded")
    # Wait for the page to load
    _page.wait_for_timeout(10000)
    yield _page

# the rest of the test fixures
# ...
```

now we can easily use the page fixture in our tests like you would in
playwright examples [here](https://playwright.dev/python/docs/api/class-page)

```python

# test_file.py

def test_home_page(page):
    ...

def test_dashboard(page):
    ...

def test_fill_form(page):
    ...
```


## Test Coverage

Testing code coverage is automatically ran as part of the CircleCI build and sent to [codecov.io](https://codecov.io/gh/uktrade/market-access-python-frontend).
You can run the tests locally and generate a coverage report by running:

With docker:
```docker compose run --rm web pytest tests --cov-report term```

Or for local builds:
```poetry run pytest tests --cov-report term```
