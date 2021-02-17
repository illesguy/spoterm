import unittest
from unittest.mock import patch
from datetime import datetime
from requests.models import Response
from requests.exceptions import HTTPError
from freezegun import freeze_time
from spoterm.authorization.client_credentials_token_provider import ClientCredentialsTokenProvider


@freeze_time('2019-01-01 00:00:00')
class TestClientCredentialsTokenProvider(unittest.TestCase):

    def setUp(self):
        mock_b64encode = patch('spoterm.authorization.spotify_token_provider.base64.b64encode').start()
        mock_b64encode.side_effect = lambda _: _

    def tearDown(self):
        patch.stopall()
    
    @patch('spoterm.authorization.client_credentials_token_provider.requests')
    def test_get_token_not_expired(self, mock_requests):
        cred = ClientCredentialsTokenProvider('id', 'secret')
        cred.token = 'foo'
        cred.token_expires = datetime(2019, 1, 1, 0, 0, 1)

        token = cred.get_token()
        self.assertEqual('foo', token)
        mock_requests.post.assert_not_called()

    @patch('spoterm.authorization.client_credentials_token_provider.requests')
    def test_get_token_expired(self, mock_requests):
        mock_response = Response()
        mock_response._content = b'{"access_token": "bar", "expires_in": 3600}'
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response

        cred = ClientCredentialsTokenProvider('id', 'secret')
        cred.token = 'foo'
        cred.token_expires = datetime(2018, 12, 31, 23, 59, 59)

        token = cred.get_token()
        self.assertEqual('bar', token)
        self.assertEqual('bar', cred.token)
        self.assertEqual(datetime(2019, 1, 1, 1, 0, 0), cred.token_expires)
        mock_requests.post.assert_called_with('https://accounts.spotify.com/api/token',
                                              data={'grant_type': 'client_credentials'},
                                              headers={'Authorization': 'Basic id:secret'})

    @patch('spoterm.authorization.client_credentials_token_provider.requests')
    def test_get_token_expired_new_request_failed(self, mock_requests):
        mock_response = Response()
        mock_response.status_code = 404
        mock_requests.post.return_value = mock_response

        cred = ClientCredentialsTokenProvider('id', 'secret')
        cred.token = 'foo'
        cred.token_expires = datetime(2018, 12, 31, 23, 59, 59)

        with self.assertRaises(HTTPError) as context:
            cred.get_token() 
        
        self.assertEqual('404 Client Error: None for url: None', str(context.exception))
        self.assertEqual('foo', cred.token)
        self.assertEqual(datetime(2018, 12, 31, 23, 59, 59), cred.token_expires)
        mock_requests.post.assert_called_with('https://accounts.spotify.com/api/token',
                                              data={'grant_type': 'client_credentials'},
                                              headers={'Authorization': 'Basic id:secret'})


if __name__ == "__main__":
    unittest.main()