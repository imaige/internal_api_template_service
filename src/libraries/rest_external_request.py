import requests
from typing import Dict, Union, List
import logging
from logging_file_format import configure_logger
import json


logger = logging.getLogger(__name__)
configure_logger(logger, level=logging.INFO)


def request(url: str, request_type: str, headers: Union[Dict, None]):
    response = ''

    if request_type == 'get':
        response = requests.get(url, headers=headers)
    elif request_type == 'post':
        response = requests.post(url, headers=headers)

    response_json = response.json()
    # logger.info(f"Request {response.status_code}: {response_json}")
    return response_json


def request_with_body(url: str, obj: Dict, request_type: str, headers: Union[Dict, None]):
    response = ''

    if request_type == 'get':
        response = requests.get(url, json=obj, headers=headers)
    elif request_type == 'post':
        response = requests.post(url, json=obj, headers=headers)

    response_json = response.json()
    # logger.info(f"Request with body {response.status_code}: {response_json}")
    return response_json


def request_with_body_and_photo(url: str, recipe: List[str], request_type: str, heads: Union[Dict, None], photo_path: str):
    response = ''

    with open(photo_path, 'rb') as photo_file:
        photo_data = photo_file.read()

    files = [("photo", photo_data)]

    if request_type == 'get':
        response = requests.get(url, data=recipe, headers=heads)
    elif request_type == 'post':
        print("making post request")
        response = requests.post(url, data=recipe, files=files, headers=heads)

    response_json = response.json()
    logger.info(f"Request with body {response.status_code}: {response_json}")
    return response_json


if __name__ == '__main__':
    recipe = {
        "name": "test-recipe",
        "description": "describe me",
        "models": [
            "model",
            "other-model"
        ]
    }

    heads = {
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMSIsImNvbXBhbnlfaWQiOiJOb25lIiwiZXhwIjoxNzE1MTc2NDkyfQ.SxJ93UO_3yRdBXCnOxo6ImxUb4hYcQyrCa6iMIGdtZQ',
    }

    request_with_body_and_photo("http://0.0.0.0:8000/api/v1/photos/model_request", recipe, "post",
                                heads, "test_image.jpg")