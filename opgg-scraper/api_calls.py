import json
import requests

from fake_useragent import UserAgent


# API Call Function using Requests and FakeUserAgent
def api_call(url): # URL String
    # Initialize UserAgent
    ua = UserAgent()
    headers = {'User-Agent': ua.random}

    try:
        apiRequest = requests.get(url, headers = headers) # Send Request to URL with Headers
        data = json.loads(apiRequest.text) # Load Data as JSON

        return data
    # Return None on Error (e)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        #print(f"API_CALL Error: {e}")
        return None
    