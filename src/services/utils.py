import string
import random
from uuid import UUID

from urllib.parse import urlparse

from core.config import app_settings


symbols = (
    u'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ',
    u'abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA'
)

translit = {ord(a): ord(b) for a, b in zip(*symbols)}


def generate_short_url(url: str):
    protocol = urlparse(url).scheme
    char = string.ascii_uppercase + string.digits + string.ascii_lowercase
    short_url = f'{protocol}://{app_settings.domain_prefix}' + ''.join(
        random.choice(char) for x in range(app_settings.length_url)
    )
    return short_url


def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.
     Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}
     Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.
     Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """

    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test
