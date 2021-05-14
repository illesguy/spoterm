#!/usr/bin/env python
import os
import sys
import argparse
from tabulate import tabulate
from spoterm.dao.spotify_dao import SpotifyDao
from spoterm.authorization.client_credentials_token_provider import ClientCredentialsTokenProvider

parser = argparse.ArgumentParser(description='Arguments')
parser.add_argument('uris', type=str, nargs='*', help='track uris to print info for')
parser.add_argument('--client-id', '-c', type=str, help='Client id required to use webapi',
                    default=os.environ['SPOTIFY_CLIENT_ID'])
parser.add_argument('--client-secret', '-s', type=str, help='Client secret required to use webapi',
                    default=os.environ['SPOTIFY_CLIENT_SECRET'])
parser.add_argument('--token-cache-loc', '-t', type=str, help='Location of token cache to use',
                    default=os.environ.get('SPOTIFY_TOKEN_CACHE_LOC'))
parser.add_argument('--uri', '-u', action='store_true')
parser.add_argument('--bpm', '-b', action='store_true')
parser.add_argument('--release', '-r', action='store_true')
args = parser.parse_args()

if not args.uris:
    track_uris = [u.strip() for ln in sys.stdin.readlines() for u in ln.split(' ')]
else:
    track_uris = args.uris

if not track_uris:
    print('No tracks found')
    sys.exit(0)

token_cache = None if args.token_cache_loc is None else os.path.join(args.token_cache_loc, '.cc_token_cache.json')

auth = ClientCredentialsTokenProvider(args.client_id, args.client_secret, token_cache)
dao = SpotifyDao(auth)


def format_duration(millis):
    hours = int(millis / 3600000)
    remaining_millis = millis % 3600000
    mins = int(remaining_millis / 60000)
    secs = int((remaining_millis % 60000) / 1000)
    return f'{mins:02}:{secs:02}' if not hours else f'{hours:02}:{mins:02}:{secs:02}'


def format_track_result(track_result, add_uri, add_release, bpms):
    res = dict()
    if add_uri:
        res['uri'] = track_result['uri']
    res['name'] = track_result['name']
    res['artists'] = ', '.join([a['name'] for a in track_result['artists']])
    res['duration'] = format_duration(track_result['duration_ms'])
    if bpms:
        res['BPM'] = bpms[track_result['uri']]
    if add_release:
        res['release'] = track_result['album']['release_date']
    return res


track_data = []

while True:
    ids_to_get = '%2C'.join([u.replace('spotify:track:', '') for u in track_uris[:50]])
    url = f'https://api.spotify.com/v1/tracks?ids={ids_to_get}'
    results = dao.get(url)
    if args.bpm:
        af_url = f'https://api.spotify.com/v1/audio-features?ids={ids_to_get}'
        af_results = dao.get(af_url)
        res_bpms = {r['uri']: round(r['tempo']) for r in af_results['audio_features']}
    else:
        res_bpms = dict()

    track_data.extend([format_track_result(t, args.uri, args.release, res_bpms) for t in results['tracks']])
    if len(track_uris) > 50:
        track_uris = track_uris[50:]
    else:
        break

if not track_data:
    print('No track data found for provided uri(s)')
else:
    table_data = [list(t.values()) for t in track_data]
    headers = list(track_data[0].keys())
    print(tabulate(table_data, headers=headers, tablefmt='orgtbl'), '\n')
