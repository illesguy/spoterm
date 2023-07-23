from datetime import datetime
from datetime import timedelta
import requests
from spoterm.authorization.spotify_token_provider import SpotifyTokenProvider


class ClientCredentialsTokenProvider(SpotifyTokenProvider):

    def _renew_token(self) -> None:
        params = {'grant_type': 'client_credentials'}
        headers = {'Authorization': 'Basic {}'.format(self._encode_client_credentials())}
        now = datetime.now()
        response = requests.post(self.TOKEN_URL, data=params, headers=headers)
        response.raise_for_status()
        result = response.json()
        self.token = result['access_token']
        self.token_expires = now + timedelta(seconds=result['expires_in'])
