import os


BASE_URL = os.environ.get("BASE_URL", "http://web-test:9000/")
WEB_DRIVER_URL = os.environ.get("WEB_DRIVER_URL", "http://chrome:4444/wd/hub")

TEST_BARRIER_ID = "8152467a-a59b-4481-aea9-deba8f0f397a"

TEST_SSO_EMAIL = os.environ.get("TEST_SSO_EMAIL")
TEST_SSO_PASSWORD = os.environ.get("TEST_SSO_PASSWORD")
TEST_SSO_NAME = os.environ.get("TEST_SSO_NAME")
