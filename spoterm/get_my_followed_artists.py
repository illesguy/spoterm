import os
import argparse
from spoterm.config.env import REDIRECT_URI, SPOTIFY_AUTH_SCOPES
from spoterm.dao.spotify_dao import SpotifyDao
from spoterm.authorization.authorization_code_token_provider import AuthorizationCodeTokenProvider
from spoterm.authorization.login.chrome_driver_login_handler import ChromeDriverLoginHandler


def _parse_args():
    parser = argparse.ArgumentParser(description='Arguments')
    parser.add_argument('--client-id', '-c', type=str, help='Client id required to use webapi',
                        default=os.environ['SPOTIFY_CLIENT_ID'])
    parser.add_argument('--client-secret', '-s', type=str, help='Client secret required to use webapi',
                        default=os.environ['SPOTIFY_CLIENT_SECRET'])
    parser.add_argument('--token-cache-loc', '-t', type=str, help='Location of token cache to use',
                        default=os.environ.get('SPOTIFY_TOKEN_CACHE_LOC'))
    parser.add_argument('--name', '-n', action='store_true', help='Also returns artist name')
    return parser.parse_args()


def get_my_followed_artists(dao):
    retrieved = []
    url = 'https://api.spotify.com/v1/me/following?limit=50&type=artist&fields=artists.items.uri,artists.next'
    while True:
        res = dao.get(url)
        retrieved.extend(res['artists']['items'])
        if res['artists']['next']:
            url = res['artists']['next']
        else:
            break
    return retrieved


def main():
    args = _parse_args()

    token_cache = None if args.token_cache_loc is None else os.path.join(args.token_cache_loc, '.ac_token_cache.json')
    scopes = [s for v in SPOTIFY_AUTH_SCOPES.values() for s in v]
    login_handler = ChromeDriverLoginHandler(os.environ.get('CHROME_DRIVER_PATH'))

    auth = AuthorizationCodeTokenProvider(args.client_id, args.client_secret, scopes, REDIRECT_URI,
                                          login_handler, token_cache)
    dao = SpotifyDao(auth)
    retrieved = get_my_followed_artists(dao)
    for r in retrieved:
        if args.name:
            print(r['uri'], r['name'])
        else:
            print(r['uri'])


if __name__ == '__main__':
    main()
