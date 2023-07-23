import os
import sys
import argparse
from spoterm.dao.spotify_dao import SpotifyDao
from spoterm.authorization.client_credentials_token_provider import ClientCredentialsTokenProvider


def _parse_args():
    parser = argparse.ArgumentParser(description='Arguments')
    parser.add_argument('playlists', type=str, nargs='*', help='playlists to get tracks for')
    parser.add_argument('--client-id', '-c', type=str, help='Client id required to use webapi',
                        default=os.environ['SPOTIFY_CLIENT_ID'])
    parser.add_argument('--client-secret', '-s', type=str, help='Client secret required to use webapi',
                        default=os.environ['SPOTIFY_CLIENT_SECRET'])
    parser.add_argument('--token-cache-loc', '-t', type=str, help='Location of token cache to use',
                        default=os.environ.get('SPOTIFY_TOKEN_CACHE_LOC'))
    return parser.parse_args()


def get_playlist_tracks(dao, playlists):
    retrieved = []
    for playlist in playlists:
        playlist_id = playlist.replace('spotify:playlist:', '')

        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?fields=items.track.uri,next'
        while True:
            res = dao.get(url)
            retrieved.extend(res['items'])
            if res['next']:
                url = res['next']
            else:
                break
    return retrieved


def main():
    args = _parse_args()
    if not args.playlists:
        playlists = [u.strip() for ln in sys.stdin.readlines() for u in ln.split(' ')]
    else:
        playlists = args.playlists

    token_cache = None if args.token_cache_loc is None else os.path.join(args.token_cache_loc, '.cc_token_cache.json')

    auth = ClientCredentialsTokenProvider(args.client_id, args.client_secret, token_cache)
    dao = SpotifyDao(auth)
    retrieved = get_playlist_tracks(dao, playlists)
    for r in retrieved:
        print(r['track']['uri'])


if __name__ == '__main__':
    main()
