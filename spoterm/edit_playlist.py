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


def _parse_args():
    parser = argparse.ArgumentParser(description='Arguments')
    parser.add_argument('uris', type=str, nargs='*', help='track uris to print info for')
    parser.add_argument('--playlist', '-p', type=str, help='URI of playlist to edit', required=True)
    parser.add_argument('--image', '-i', type=str,
                        help='Image to set for playlist, either path to file or an album uri')
    parser.add_argument('--client-id', '-c', type=str, help='Client id required to use webapi',
                        default=os.environ['SPOTIFY_CLIENT_ID'])
    parser.add_argument('--client-secret', '-s', type=str, help='Client secret required to use webapi',
                        default=os.environ['SPOTIFY_CLIENT_SECRET'])
    parser.add_argument('--token-cache-loc', '-t', type=str, help='Location of token cache to use',
                        default=os.environ.get('SPOTIFY_TOKEN_CACHE_LOC'))
    parser.add_argument('--delete', '-d', action='store_true', help='Delete specified tracks from playlist')
    return parser.parse_args()


def _set_image_from_url(dao, playlist_id, image_url):
    image_data = base64.b64encode(requests.get(image_url).content)
    print(dao.put(
        f"https://api.spotify.com/v1/playlists/{playlist_id}/images",
        "image/jpeg",
        image_data
    ))


def update_playlist_image(dao, playlist_id, image_uri):
    if image_uri.startswith('spotify:album:'):
        image_album_id = image_uri.replace("spotify:album:", "")
        album_info = dao.get(f"https://api.spotify.com/v1/albums/{image_album_id}")
        image_url = album_info['images'][0]['url']
        _set_image_from_url(dao, playlist_id, image_url)
    elif image_uri.startswith('spotify:playlist:'):
        image_playlist_id = image_uri.replace("spotify:playlist:", "")
        playlist_info = dao.get(f"https://api.spotify.com/v1/playlists/{image_playlist_id}")
        image_url = playlist_info['images'][0]['url']
        _set_image_from_url(dao, playlist_id, image_url)


def delete_tracks_from_playlist(dao, playlist_id, track_uris):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    if len(track_uris) > 100:
        uris_to_delete = track_uris[:100]
        uris_left = track_uris[100:]
    else:
        uris_to_delete = track_uris
        uris_left = []

    while True:
        tracks_to_delete = [{'uri': u} for u in uris_to_delete]
        body = {'tracks': tracks_to_delete}
        dao.delete(url, 'application/json', json.dumps(body))

        if not uris_left:
            break
        
        if len(uris_left) > 100:
            uris_to_delete = uris_left[:100]
            uris_left = uris_left[100:]
        else:
            uris_to_delete = uris_left
            uris_left = []


def add_tracks_to_playlist(dao, playlist_id, track_uris):
    if len(track_uris) > 100:
        uris_to_add = track_uris[:100]
        uris_left = track_uris[100:]
    else:
        uris_to_add = track_uris
        uris_left = []

    while True:
        tracks_to_add = {"uris": uris_to_add}
        dao.post(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", json.dumps(tracks_to_add))

        if not uris_left:
            break
        
        if len(uris_left) > 100:
            uris_to_add = uris_left[:100]
            uris_left = uris_left[100:]
        else:
            uris_to_add = uris_left
            uris_left = []


def main():
    args = _parse_args()

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

    if args.image:
        update_playlist_image(dao, playlist_id, args.image)

    if uris:
        if args.delete:
            delete_tracks_from_playlist(dao, playlist_id, uris)
        else:
            add_tracks_to_playlist(dao, playlist_id, uris)


if __name__ == '__main__':
    main()
