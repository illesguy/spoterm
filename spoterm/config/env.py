REDIRECT_URI = 'http://localhost/'

SPOTIFY_AUTH_SCOPES = {'follow': ['user-follow-read', 'user-follow-modify'],
                       'listening_history': ['user-read-recently-played', 'user-top-read'],
                       'users': ['user-read-birthdate', 'user-read-email', 'user-read-private'],
                       'library': ['user-library-read', 'user-library-modify'],
                       'spotify_connect': ['user-read-playback-state', 'user-read-currently-playing',
                                           'user-modify-playback-state'],
                       'playlists': ['playlist-read-collaborative', 'playlist-modify-private',
                                     'playlist-modify-public', 'playlist-read-private'],
                       'playback': ['streaming', 'app-remote-control'],
                       'ugc': ['ugc-image-upload']}