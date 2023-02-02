import zipfile
import io

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from fastapi import status

from services.auth.auth_handler import decode_jwt


async def download_iterator():
    file = b'testing'
    yield file


@pytest.mark.asyncio()
async def test_auth(client: AsyncClient) -> None:
    # register user
    username = 'user_test'
    password = 'pass123_'
    user_data = {
        'username': username,
        'password': password
    }
    response = await client.post(
        'api/v1/auth/register',
        json=user_data
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['access_token']
    in_data = decode_jwt(response.json()['access_token'])
    assert isinstance(in_data, dict)
    assert in_data['username'] == username

    # check login
    response = await client.post(
        'api/v1/auth/login',
        json=user_data
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['access_token']
    in_data = decode_jwt(response.json()['access_token'])
    assert isinstance(in_data, dict)
    assert in_data['username'] == username

    wrong_user = {
        'username': 'user_2',
        'password': password
    }
    response = await client.post(
        'api/v1/auth/login',
        json=wrong_user
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    wrong_password = {
        'username': username,
        'password': 'wrong_password'
    }
    response = await client.post(
        'api/v1/auth/login',
        json=wrong_password
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@patch('api.v1.files.upload_content', return_value=None)
@patch('api.v1.files.download_content')
@pytest.mark.asyncio()
async def test_files(
        mocked_download: AsyncMock, mocked_upload: AsyncMock,
        client: AsyncClient
) -> None:
    # login user
    user_data = {
        'username': 'user_test',
        'password': 'pass123_'
    }
    response = await client.post(
        'api/v1/auth/register',
        json=user_data
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['access_token']
    access_token = f'Bearer {response.json()["access_token"]}'

    # get empty list of files
    response = await client.get(
        'api/v1/files/list',
        headers={'Authorization': access_token}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['files'] == []

    # upload file
    file_content = b'test'
    response = await client.post(
        'api/v1/files/upload',
        data={'path': 'test/path/file.txt'},
        files={'file_bytes': file_content},
        headers={'Authorization': access_token}
    )
    assert response.status_code == status.HTTP_201_CREATED

    # check file created
    response = await client.get(
        'api/v1/files/list',
        headers={'Authorization': access_token}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['files']) == 1
    file_id = response.json()['files'][0]['id']

    # download file
    mocked_download.return_value = download_iterator()
    response = await client.get(
        'api/v1/files/download',
        params={'path': file_id},
        headers={'Authorization': access_token}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.content == b'testing'

    response = await client.get(
        'api/v1/files/download',
        params={'path': file_id, 'zipped': True},
        headers={'Authorization': access_token}
    )
    assert response.status_code == status.HTTP_200_OK
    assert zipfile.is_zipfile(io.BytesIO(response.content))

    # test search
    # upload new files
    file_content = b'test'
    response = await client.post(
        'api/v1/files/upload',
        data={'path': 'test/path/new.png'},
        files={'file_bytes': file_content},
        headers={'Authorization': access_token}
    )
    assert response.status_code == status.HTTP_201_CREATED
    response = await client.post(
        'api/v1/files/upload',
        data={'path': 'home/doc.txt'},
        files={'file_bytes': file_content},
        headers={'Authorization': access_token}
    )
    assert response.status_code == status.HTTP_201_CREATED
    response = await client.post(
        'api/v1/files/upload',
        data={'path': 'life/for_search.xml'},
        files={'file_bytes': file_content},
        headers={'Authorization': access_token}
    )
    assert response.status_code == status.HTTP_201_CREATED

    # check files
    response = await client.get(
        'api/v1/files/list',
        headers={'Authorization': access_token}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['files']) == 4

    # search files
    response = await client.get(
        'api/v1/files/search',
        params={'query': 'test'},
        headers={'Authorization': access_token}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['matches']) == 2

    response = await client.get(
        'api/v1/files/search',
        params={'query': 'search'},
        headers={'Authorization': access_token}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['matches']) == 1

    response = await client.get(
        'api/v1/files/search',
        params={'extension': 'txt'},
        headers={'Authorization': access_token}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['matches']) == 2

    response = await client.get(
        'api/v1/files/search',
        params={'extension': 'txt', 'query': 'doc'},
        headers={'Authorization': access_token}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['matches']) == 1

    response = await client.get(
        'api/v1/files/search',
        params={'is_regex': True, 'query': '^test.*txt$'},
        headers={'Authorization': access_token}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['matches']) == 1
    assert response.json()['matches'][0]['name'] == 'file.txt'
