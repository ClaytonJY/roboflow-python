import json
import os
import time

import requests

from roboflow.core.project import Project
from roboflow.config import *


def auth(api_key):
    response = requests.post(API_URL + "/token", data=({
        "api_key": api_key
    }))

    r = response.json()
    if "error" in r or response.status_code != 200:
        raise RuntimeError(response.text)

    token = r['token']
    token_expires = r['expires_in']
    return Roboflow(api_key, token, token_expires)


class Roboflow():
    def __init__(self, api_key, access_token, token_expires):
        self.api_key = api_key
        self.access_token = access_token
        self.token_expires = token_expires
        # TODO: Need an endpoint to retrieve publishable key based on access token/workspace/api key
        self.publishable_key = os.getenv("ROBOFLOW_PUBLISHABLE_KEY")
        # publishable_key_response = requests.get(API_URL + "/convert_key?access_token=" + self.access_token)
        # if publishable_key_response.status_code != 200:
        #     raise RuntimeError(publishable_key_response.text)
        # # self.publishable_key =

    def list_datasets(self):
        get_datasets_endpoint = API_URL + '/datasets'
        datasets = requests.get(get_datasets_endpoint + '?access_token=' + self.access_token).json()
        print(json.dumps(datasets, indent=2))
        return datasets

    def load(self, dataset_slug):
        # Get info about dataset being loaded
        dataset_info = requests.get(API_URL + "/dataset/" + dataset_slug + "?access_token=" + self.access_token)
        # Throw error if dataset isn't valid/user doesn't have permissions to access the dataset
        if dataset_info.status_code != 200:
            raise RuntimeError(dataset_info.text)
        # Turn dataset info into a json format otherwise
        dataset_info = dataset_info.json()
        # Get version info (i.e. version names + numbers)
        version_info = requests.get(
            API_URL + "/versions/dataset/" + dataset_slug + "?access_token=" + self.access_token)
        # Throw error if dataset isn't valid/user doesn't have permissions to access the dataset
        if version_info.status_code != 200:
            raise RuntimeError(version_info.text)
        # Turn dataset version info into a json format otherwise
        version_info = version_info.json()
        # Return a project object
        return Project(self.api_key, dataset_info['id'], dataset_info['type'], version_info['versions'],
                       self.access_token, self.publishable_key)

    def __str__(self):
        json_value = {'api_key': self.api_key, 'auth_token': self.access_token, 'token_expires': self.token_expires}
        return json.dumps(json_value, indent=2)