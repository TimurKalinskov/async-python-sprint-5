import pytest

from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio()
async def test_get_create(client: AsyncClient) -> None:
    response = await client.get('api/v1/url_shorts/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

    data = [{'url': 'https://stackoverflow.com/'}]
    response = await client.post(
        'api/v1/url_shorts/',
        json=data
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert len(response.json()) == 1
    assert 'url_short' in response.json()[0]
    assert 'created_at' in response.json()[0]
    assert len(response.json()[0].keys()) == 4

    data = [
        {'url': 'https://test.com/test/1'}, {'url': 'https://test.com/test/2'}
    ]
    response = await client.post(
        'api/v1/url_shorts/',
        json=data
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert len(response.json()) == 2

    response = await client.get('api/v1/url_shorts/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3
    pk = response.json()[0]['id']

    response = await client.get(f'api/v1/url_shorts/{pk}')
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT


@pytest.mark.asyncio()
async def test_status(client: AsyncClient) -> None:
    data = [
        {'url': 'https://test.com/test/1'}, {'url': 'https://test.com/test/2'}
    ]
    response = await client.post(
        'api/v1/url_shorts/',
        json=data
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert len(response.json()) == 2
    pk = response.json()[0]['id']

    response = await client.get(f'api/v1/url_shorts/{pk}/status')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['uses_count'] == 0

    response = await client.get(f'api/v1/url_shorts/{pk}')
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT

    response = await client.get(f'api/v1/url_shorts/{pk}/status')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['uses_count'] == 1
    assert 'statistics' not in response.json()

    response = await client.get(
        f'api/v1/url_shorts/{pk}/status', params={'full_info': True}
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'statistics' in response.json()
    assert isinstance(response.json()['statistics'], list)
    assert 'used_at' in response.json()['statistics'][0]
    assert 'client_host' in response.json()['statistics'][0]
    assert 'client_port' in response.json()['statistics'][0]


@pytest.mark.asyncio()
async def test_delete(client: AsyncClient) -> None:
    data = [
        {'url': 'https://test.com/test/1'}, {'url': 'https://test.com/test/2'}
    ]
    response = await client.post(
        'api/v1/url_shorts/',
        json=data
    )
    assert response.status_code == status.HTTP_201_CREATED

    response = await client.get('api/v1/url_shorts/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    pk = response.json()[0]['id']

    response = await client.delete(f'api/v1/url_shorts/{pk}')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = await client.get('api/v1/url_shorts/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1

    response = await client.get(f'api/v1/url_shorts/{pk}')
    assert response.status_code == status.HTTP_410_GONE
    assert response.json() == {'detail': 'URL deleted'}


@pytest.mark.asyncio()
async def test_inspect(client: AsyncClient) -> None:
    response = await client.get('/api/v1/inspect/ping')
    assert response.status_code == status.HTTP_200_OK
    assert 'info' in response.json()
    assert response.json()['status'] == 'connected'
