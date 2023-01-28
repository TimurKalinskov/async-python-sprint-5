import string
import random

from urllib.parse import urlparse

from core.config import app_settings


def generate_short_url(url: str):
    protocol = urlparse(url).scheme
    char = string.ascii_uppercase + string.digits + string.ascii_lowercase
    short_url = f'{protocol}://{app_settings.domain_prefix}' + ''.join(
        random.choice(char) for x in range(app_settings.length_url)
    )
    return short_url
