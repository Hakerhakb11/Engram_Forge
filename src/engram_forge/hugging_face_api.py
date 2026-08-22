import requests

url = "https://huggingface.co/api/models"


def search_model(model_name):
    params = {
        "search": model_name,
        "limit": 100,
        "sort": "downloads",
        "direction": -1
    }

    response = requests.get(url, params=params)

    response.raise_for_status()

    return response.json()
