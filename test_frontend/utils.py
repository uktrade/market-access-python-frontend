import inspect
import os
import re
import time
from functools import wraps

import pytest
from playwright._impl._errors import TimeoutError


def get_base_url():
    return os.getenv("BASE_FRONTEND_TESTING_URL", "http://market-access.local:9880/")


def get_text_content_without_line_separators(text_content):
    text_content = text_content.replace("\n", "")
    text_content = text_content.replace("\r", "")
    text_content = re.sub(r"\s+", " ", text_content)
    return text_content


def clean_full_url(url):
    """Clean a URL by removing multiple slashes."""

    # Split the URL into protocol and the rest.
    if "://" in url:
        protocol, rest = url.split("://", 1)
        # Clean the 'rest' part of the URL by replacing multiple slashes with a single one.
        rest = re.sub(r"/+", "/", rest)
        # Concatenate the protocol and the cleaned part back together.
        cleaned_url = f"{protocol}://{rest}"
    else:
        # If there's no protocol, just clean the URL directly.
        cleaned_url = re.sub(r"/+", "/", url)
    return cleaned_url


def retry(tries=3, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff."""

    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            # Get argument names of the function
            arg_names = inspect.getfullargspec(f).args

            # Run the function with retries
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except TimeoutError as e:
                    msg = f"{e}, Retrying in {mdelay} seconds..."
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff

            # Final attempt
            return f(*args, **kwargs)

        # If the function expects a fixture named 'request', assume it's a pytest test
        if "request" in inspect.getfullargspec(f).args:
            # Use pytest's request fixture to modify the function with retry logic
            @pytest.fixture
            def wrapper(request, *args, **kwargs):
                # Modify the test function by injecting the retry decorator
                return f_retry(*args, **kwargs)

            return wrapper
        else:
            return f_retry

    return deco_retry


def get_username(page):
    if get_base_url() == "http://market-access.local:9880/":
        return "Your"
    page.goto(get_base_url() + "account")
    page.locator("dt").filter(has_text="Name").click()
    # name = page.get_by_test_id("username").inner_text()
    name = "Elizabeth Pedley"
    return name


def change_permissions(page, username, permission):
    page.goto(get_base_url() + "users")
    if not page.get_by_role("link", name=username).is_visible():
        page.get_by_placeholder("E.g. full name").fill(username)
        page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name=username).click()
    page.get_by_role("link", name="Edit profile").click()
    page.get_by_label(permission).check()
    page.get_by_role("button", name="Save").click()


def admin_user(page):
    page.goto(get_base_url() + "users")
    if page.get_by_role("heading", name="Manage users and groups").is_visible():
        return True
    return False
