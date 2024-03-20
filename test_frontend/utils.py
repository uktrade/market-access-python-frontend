import os
import re

def get_base_url():
    return os.getenv("BASE_FRONTEND_TESTING_URL", "http://market-access.local:9880/")

def get_text_content_without_line_separators(text_content):
    text_content = text_content.replace("\n", "")
    text_content = text_content.replace("\r", "")
    text_content = re.sub(r"\s+", " ", text_content)
    return text_content
