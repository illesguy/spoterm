from typing import List, Optional
import urllib
from datetime import datetime
from datetime import timedelta
import uuid
import requests
from spoterm.authorization.spotify_token_provider import SpotifyTokenProvider
from spoterm.authorization.login.login_handler import LoginHandler


class AuthorizationCodeTokenProvider(SpotifyTokenProvider):

    AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'

    def __init__(self, client_id: str, client_secret: str, scopes: List[str],
                 redirect_uri: str, login_handler: LoginHandler,
                 token_cache: Optional[str] = None) -> None:
        self.scopes = scopes
        self.redirect_uri = redirect_uri
        self.login_handler = login_handler
        self.state = str(uuid.uuid4())
        super().__init__(client_id, client_secret, token_cache)

    def _renew_token(self) -> None:
        if self.refresh_token is not None:
            params = {'grant_type': 'refresh_token', 'refresh_token': self.refresh_token}
        else:
            code = self._get_new_authorization_code()
            params = {'grant_type': 'authorization_code', 'code': code, 'redirect_uri': self.redirect_uri}

        headers = {'Authorization': 'Basic {}'.format(self._encode_client_credentials())}

        now = datetime.now()
        response = requests.post(self.TOKEN_URL, data=params, headers=headers)
        response.raise_for_status()
        result = response.json()
        self.token = result['access_token']
        self.refresh_token = result.get('refresh_token', self.refresh_token)
        self.token_expires = now + timedelta(seconds=result['expires_in'])

    def _get_new_authorization_code(self):
        params = {'client_id': self.client_id, 'response_type': 'code', 'redirect_uri': self.redirect_uri,
                  'scope': ' '.join(self.scopes), 'state': self.state}
        url_params = urllib.parse.urlencode(params)
        login_url = '{}?{}'.format(self.AUTHORIZE_URL, url_params)

        response_url = self.login_handler.login(login_url, self.redirect_uri)

        response_params = urllib.parse.parse_qs(response_url.split('?')[1])
        response_state = response_params['state'][0]
        if response_state != self.state:
            raise InvalidStateError('Returned state "{}" didn\'t match expected state "{}".'.format(response_state,
                                                                                                    self.state))
        response_error = response_params.get('error')
        if response_error is not None:
            raise AuthorizationCodeError(response_error[0])

        return response_params['code'][0]


class InvalidStateError(ValueError):
    pass


class AuthorizationCodeError(Exception):
    pass
