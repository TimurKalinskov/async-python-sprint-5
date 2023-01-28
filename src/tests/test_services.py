import pytest
from urllib.parse import urlparse

from services.utils import generate_short_url


@pytest.mark.asyncio()
async def test_get_create() -> None:
    url = 'https://github.com/test'
    short_url = generate_short_url(url)
    result = urlparse(short_url)

    assert all([result.scheme, result.netloc])
