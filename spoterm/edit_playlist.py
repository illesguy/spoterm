#!/usr/bin/env python
import os
import sys
import json
import base64
import argparse
import requests
from spoterm.config.env import REDIRECT_URI, SPOTIFY_AUTH_SCOPES
from spoterm.dao.spotify_dao import SpotifyDao
from spoterm.authorization.authorization_code_token_provider import AuthorizationCodeTokenProvider
from spoterm.authorization.login.chrome_driver_login_handler import ChromeDriverLoginHandler

parser = argparse.ArgumentParser(description='Arguments')
parser.add_argument('uris', type=str, nargs='*', help='track uris to print info for')
parser.add_argument('--playlist', '-p', type=str, help='URI of playlist to edit', required=True)
parser.add_argument('--image', '-i', type=str, help='Image to set for playlist, either path to file or an album uri')
parser.add_argument('--client-id', '-c', type=str, help='Client id required to use webapi',
                    default=os.environ['SPOTIFY_CLIENT_ID'])
parser.add_argument('--client-secret', '-s', type=str, help='Client secret required to use webapi',
                    default=os.environ['SPOTIFY_CLIENT_SECRET'])
parser.add_argument('--token-cache-loc', '-t', type=str, help='Location of token cache to use',
                    default=os.environ.get('SPOTIFY_TOKEN_CACHE_LOC'))
parser.add_argument('--overwrite', '-o', action='store_true', help='Overwrites previous tracks in playlist')
args = parser.parse_args()

if not args.uris:
    uris = [u.strip() for ln in sys.stdin.readlines() for u in ln.split(' ')]
else:
    uris = args.uris

token_cache = None if args.token_cache_loc is None else os.path.join(args.token_cache_loc, '.ac_token_cache.json')
scopes = [s for v in SPOTIFY_AUTH_SCOPES.values() for s in v]
login_handler = ChromeDriverLoginHandler(os.environ.get('CHROME_DRIVER_PATH'))

auth = AuthorizationCodeTokenProvider(args.client_id, args.client_secret, scopes, REDIRECT_URI,
                                      login_handler, token_cache)
dao = SpotifyDao(auth)
playlist_id = args.playlist.replace("spotify:playlist:", "")


def set_image_from_url(image_url):
    image_data = base64.b64encode(requests.get(image_url).content)
    print(dao.put(
        f"https://api.spotify.com/v1/playlists/{playlist_id}/images",
        "image/jpeg",
        image_data
    ))


if args.image:
    if args.image.startswith('spotify:album:'):
        album_id = args.image.replace("spotify:album:", "")
        album_info = dao.get(f"https://api.spotify.com/v1/albums/{album_id}")
        image_url = album_info['images'][0]['url']
        set_image_from_url(image_url)
    elif args.image.startswith('spotify:playlist:'):
        playlist_id = args.image.replace("spotify:playlist:", "")
        playlist_info = dao.get(f"https://api.spotify.com/v1/playlists/{playlist_id}")
        image_url = playlist_info['images'][0]['url']
        set_image_from_url(image_url)

if uris:
    if args.overwrite:
        batches = []
        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?fields=items.track.uri,next'
        while True:
            res = dao.get(url)
            batches.append(res['items'])
            if res['next']:
                url = res['next']
            else:
                break

        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        for batch in batches:
            if batch:
                batch_tracks = [{'uri': u['track']['uri']} for u in batch]
                body = {'tracks': batch_tracks}
                dao.delete(url, 'application/json', json.dumps(body))

    if len(uris) > 100:
        uris_to_add = uris[:100]
        uris_left = uris[100:]
    else:
        uris_to_add = uris
        uris_left = []

    while True:
        tracks_to_add = {"uris": uris_to_add}
        dao.post(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", json.dumps(tracks_to_add))

        if not uris_left:
            break
        elif len(uris_left) > 100:
            uris_to_add = uris_left[:100]
            uris_left = uris_left[100:]
        else:
            uris_to_add = uris_left
            uris_left = []
