#!/usr/bin/env python
import os
import sys
import argparse
from dao.spotify_dao import SpotifyDao
from authorization.client_credentials_token_provider import ClientCredentialsTokenProvider

parser = argparse.ArgumentParser(description='Arguments')
parser.add_argument('--artists' '-a', type=str, help='artist to query')
parser.add_argument('--track', '-t', type=str, help='track to query')
parser.add_argument('--client-id', '-c', type=str, help='Client id required to use webapi', default=os.environ['SPOTIFY_CLIENT_ID'])
parser.add_argument('--client-secret', '-s', type=str, help='Client secret required to use webapi', default=os.environ['SPOTIFY_CLIENT_SECRET'])
parser.add_argument('--token-cache-loc', '-l', type=str, help='Location of token cache to use', default=os.environ.get('SPOTIFY_TOKEN_CACHE_LOC'))
args = parser.parse_args()

entity_type = None
track_query = ''
artist_query = ''

if args.track:
    entity_type = 'track'

if args.artist:
    entity_type = 'artist' if entity_type is None else entity_type

if entity_type is None:
    print('Error, either -a or -t flags need to be used to create the query')
    sys.exit(-1)

token_cache = None if args.token_cache_loc is None else os.path.join(args.token_cache_loc, '.cc_token_cache.json')

auth = ClientCredentialsTokenProvider(args.client_id, args.client_secret, token_cache)
dao = SpotifyDao(auth)

mix_filters = 'NOT%20mixed%20NOT%20"mix%20cut"%20NOT%20ASOT'

query = args.query[0].replace(" ", "%20")
url = f'https://api.spotify.com/v1/search?q={query}%20{mix_filters}&type=track'

results = dao.get(url)
for res in results['tracks']['items']:
    print(res['uri'])
