from typing import Dict, Any
import requests
from authorization.spotify_token_provider import SpotifyTokenProvider


class SpotifyDao:

    def __init__(self, token_provider: SpotifyTokenProvider) -> None:
        self.token_provider = token_provider

    def _get_auth_headers(self):
        return {'Authorization': f'Bearer {self.token_provider.get_token()}'}

    def get(self, url: str) -> Dict[str, Any]:
        headers = self._get_auth_headers()
        resp = requests.get(url, headers=headers)
        return resp.json()

    def put(self, url: str, content_type: str, payload: Any) -> int:
        headers = self._get_auth_headers()
        headers['Content-Type'] = content_type
        resp = requests.put(url, headers=headers, data=payload)
        resp.raise_for_status()
        print(f"PUT: {resp.status_code}")
        return resp.status_code

    def delete(self, url: str, content_type: str, payload: Any) -> int:
        headers = self._get_auth_headers()
        headers['Content-Type'] = content_type
        resp = requests.delete(url, headers=headers, data=payload)
        resp.raise_for_status()
        print(f"DELETE: {resp.status_code}")
        return resp.status_code

    def post(self, url: str, payload: Any) -> int:
        headers = self._get_auth_headers()
        resp = requests.post(url, headers=headers, data=payload)
        resp.raise_for_status()
        print(f"POST: {resp.status_code}")
        return resp.status_code
