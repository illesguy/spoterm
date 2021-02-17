import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from requests.models import Response
from requests.exceptions import HTTPError
from freezegun import freeze_time
from spoterm.authorization.authorization_code_token_provider import (AuthorizationCodeTokenProvider,
                                                                     InvalidStateError, AuthorizationCodeError)


@freeze_time('2019-01-01 00:00:00')
class TestAuthorizationCodeTokenProvider(unittest.TestCase):

    def setUp(self):
        mock_b64encode = patch('spoterm.authorization.spotify_token_provider.base64.b64encode').start()
        mock_urlencode = patch('spoterm.authorization.authorization_code_token_provider.urllib.parse.urlencode').start()
        self.mock_uuid = patch('spoterm.authorization.authorization_code_token_provider.uuid.uuid4').start()
        
        mock_b64encode.side_effect = lambda _: _
        mock_urlencode.side_effect = lambda p: '_'.join(p.values())
        self.mock_uuid.return_value = 'st'

        self.mock_login_handler = MagicMock()
        self.mock_login_handler.login.return_value = 'localhost?code=code&state=st'

    def tearDown(self):
        patch.stopall()

    @patch('spoterm.authorization.authorization_code_token_provider.requests')
    def test_get_token_not_expired(self, mock_requests):
        cred = AuthorizationCodeTokenProvider('id', 'secret', ['scope'], 'localhost', self.mock_login_handler)
        cred.token = 'foo'
        cred.token_expires = datetime(2019, 1, 1, 0, 0, 1)

        token = cred.get_token()
        self.assertEqual('foo', token)
        mock_requests.post.assert_not_called()
        self.mock_login_handler.login.assert_not_called()

    @patch('spoterm.authorization.authorization_code_token_provider.requests')
    def test_get_token_expired_with_refresh_token(self, mock_requests):
        mock_response = Response()
        mock_response._content = b'{"access_token": "bar", "expires_in": 3600}'
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response

        cred = AuthorizationCodeTokenProvider('id', 'secret', ['scope'], 'localhost', self.mock_login_handler)
        cred.token = 'foo'
        cred.refresh_token = 'refresh'
        cred.token_expires = datetime(2018, 12, 31, 23, 59, 59)

        token = cred.get_token()
        self.assertEqual('bar', token)
        self.assertEqual('bar', cred.token)
        self.assertEqual('refresh', cred.refresh_token)
        self.assertEqual(datetime(2019, 1, 1, 1, 0, 0), cred.token_expires)
        mock_requests.post.assert_called_with('https://accounts.spotify.com/api/token',
                                              data={'grant_type': 'refresh_token', 'refresh_token': 'refresh'},
                                              headers={'Authorization': 'Basic id:secret'})
        self.mock_login_handler.login.assert_not_called()

    @patch('spoterm.authorization.authorization_code_token_provider.requests')
    def test_get_token_expired_with_refresh_token_failed(self, mock_requests):
        mock_response = Response()
        mock_response.status_code = 404
        mock_requests.post.return_value = mock_response

        cred = AuthorizationCodeTokenProvider('id', 'secret', ['scope'], 'localhost', self.mock_login_handler)
        cred.token = 'foo'
        cred.refresh_token = 'refresh'
        cred.token_expires = datetime(2018, 12, 31, 23, 59, 59)

        with self.assertRaises(HTTPError) as context:
            cred.get_token() 
        
        self.assertEqual('404 Client Error: None for url: None', str(context.exception))
        self.assertEqual('foo', cred.token)
        self.assertEqual('refresh', cred.refresh_token)
        self.assertEqual(datetime(2018, 12, 31, 23, 59, 59), cred.token_expires)
        mock_requests.post.assert_called_with('https://accounts.spotify.com/api/token',
                                              data={'grant_type': 'refresh_token', 'refresh_token': 'refresh'},
                                              headers={'Authorization': 'Basic id:secret'})
        self.mock_login_handler.login.assert_not_called()

    @patch('spoterm.authorization.authorization_code_token_provider.requests')
    def test_get_token_expired_with_new_authorization_code(self, mock_requests):
        mock_response = Response()
        mock_response._content = b'{"access_token": "bar", "expires_in": 3600, "refresh_token": "new_refresh"}'
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response

        cred = AuthorizationCodeTokenProvider('id', 'secret', ['scope'], 'localhost', self.mock_login_handler)
        cred.token = 'foo'
        cred.token_expires = datetime(2018, 12, 31, 23, 59, 59)

        token = cred.get_token()
        self.assertEqual('bar', token)
        self.assertEqual('bar', cred.token)
        self.assertEqual('new_refresh', cred.refresh_token)
        self.assertEqual(datetime(2019, 1, 1, 1, 0, 0), cred.token_expires)
        mock_requests.post.assert_called_with('https://accounts.spotify.com/api/token',
                                              data={'grant_type': 'authorization_code', 'code': 'code',
                                                    'redirect_uri': 'localhost'},
                                              headers={'Authorization': 'Basic id:secret'})
        self.mock_login_handler.login.assert_called_with(
            'https://accounts.spotify.com/authorize?id_code_localhost_scope_st',
            'localhost'
        )

    @patch('spoterm.authorization.authorization_code_token_provider.requests')
    def test_get_token_expired_with_new_authorization_code_webdriver_timeout(self, mock_requests):
        self.mock_login_handler.login.side_effect = Exception('Browser did nothing.')

        cred = AuthorizationCodeTokenProvider('id', 'secret', ['scope'], 'localhost', self.mock_login_handler)
        cred.token = 'foo'
        cred.token_expires = datetime(2018, 12, 31, 23, 59, 59)

        with self.assertRaises(Exception) as context:
            cred.get_token()
        
        self.assertEqual('Browser did nothing.', str(context.exception))
        self.assertEqual('foo', cred.token)
        self.assertIsNone(cred.refresh_token)
        self.assertEqual(datetime(2018, 12, 31, 23, 59, 59), cred.token_expires)

        mock_requests.post.assert_not_called()
        self.mock_login_handler.login.assert_called_with(
            'https://accounts.spotify.com/authorize?id_code_localhost_scope_st',
            'localhost'
        )


    @patch('spoterm.authorization.authorization_code_token_provider.requests')
    def test_get_token_expired_with_new_authorization_code_invalid_state(self, mock_requests):
        self.mock_uuid.return_value = 'ts'

        cred = AuthorizationCodeTokenProvider('id', 'secret', ['scope'], 'localhost', self.mock_login_handler)
        cred.token = 'foo'
        cred.token_expires = datetime(2018, 12, 31, 23, 59, 59)

        with self.assertRaises(InvalidStateError) as context:
            cred.get_token()

        self.assertEqual('Returned state "st" didn\'t match expected state "ts".', str(context.exception))
        self.assertEqual('foo', cred.token)
        self.assertIsNone(cred.refresh_token)
        self.assertEqual(datetime(2018, 12, 31, 23, 59, 59), cred.token_expires)

        mock_requests.post.assert_not_called()
        self.mock_login_handler.login.assert_called_with(
            'https://accounts.spotify.com/authorize?id_code_localhost_scope_ts',
            'localhost'
        )

    @patch('spoterm.authorization.authorization_code_token_provider.requests')
    def test_get_token_expired_with_new_authorization_code_failed(self, mock_requests):
        self.mock_login_handler.login.return_value = 'localhost?error=Error%20occurred%20while%20getting%20code&state=st'
        
        cred = AuthorizationCodeTokenProvider('id', 'secret', ['scope'], 'localhost', self.mock_login_handler)
        cred.token = 'foo'
        cred.token_expires = datetime(2018, 12, 31, 23, 59, 59)

        with self.assertRaises(AuthorizationCodeError) as context:
            cred.get_token()
        
        self.assertEqual('Error occurred while getting code', str(context.exception))
        self.assertEqual('foo', cred.token)
        self.assertIsNone(cred.refresh_token)
        self.assertEqual(datetime(2018, 12, 31, 23, 59, 59), cred.token_expires)

        mock_requests.post.assert_not_called()
        self.mock_login_handler.login.assert_called_with(
            'https://accounts.spotify.com/authorize?id_code_localhost_scope_st',
            'localhost'
        )


if __name__ == "__main__":
    unittest.main()
