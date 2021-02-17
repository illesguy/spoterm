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
