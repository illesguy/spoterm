import os
import json
from typing import Optional
from abc import ABC, abstractmethod
import base64
from datetime import datetime


class SpotifyTokenProvider(ABC):

    TOKEN_URL = 'https://accounts.spotify.com/api/token'

    def __init__(self, client_id: str, client_secret: str,
                 token_cache: Optional[str] = None) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_cache = token_cache
        self._init_token()

    def get_token(self) -> str:
        if not self.token or self.token_expires < datetime.now():   
            self._renew_token()
            self._save_token_to_cache()
        return self.token

    def _init_token(self) -> None:
        if self.token_cache is not None and os.path.exists(self.token_cache):
            with open(self.token_cache, 'r') as tc:
                token_data = json.loads(tc.read())
                self.token = token_data['token']
                self.token_expires = datetime.fromtimestamp(token_data['token_expires'])
                self.refresh_token = token_data.get('refresh_token')
        else:
            self.token = ''
            self.token_expires = datetime.now()
            self.refresh_token = None

    def _save_token_to_cache(self) -> None:
        if self.token_cache is not None:
            with open(self.token_cache, 'w') as tc:
                token_data = {
                    'token': self.token,
                    'token_expires': datetime.timestamp(self.token_expires)
                }
                if self.refresh_token is not None:
                    token_data['refresh_token'] = self.refresh_token
                tc.write(json.dumps(token_data))

    @abstractmethod
    def _renew_token(self) -> None:  # pragma: no cover
        pass

    def _encode_client_credentials(self) -> str:
        return base64.b64encode('{}:{}'.format(self.client_id, self.client_secret).encode('UTF-8')).decode('UTF-8')
