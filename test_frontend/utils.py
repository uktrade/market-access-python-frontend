import os
import re


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
