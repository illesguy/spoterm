from setuptools import find_packages, setup

install_requires = [
    "requests == 2.25.1",
    "tabulate == 0.8.9"
]

qt_requires = [
    "PyQt5 == 5.15.4",
    "PyQt5-Qt5 == 5.15.2",
    "PyQt5-sip == 12.9.0"
]

selenium_requires = [
    "selenium == 3.141.0"
]

test_requires = [
    "pytest == 5.3.5",
    "pytest-mock == 3.6.1",
    "pytest-cov == 2.12.0",
    "pylint == 2.8.2",
    "mypy == 0.812",
    "pycodestyle == 2.7.0",
    "freezegun == 1.1.0",
]

packages = [
    "spoterm",
    "spoterm.authorization",
    "spoterm.authorization.login",
    "spoterm.config",
    "spoterm.dao",
]

setup(
    packages=packages,
    version=0.1,
    name="spoterm",
    install_requires=install_requires,
    extras_require={
        "qt": qt_requires,
        "test": test_requires,
        "selenium": selenium_requires
    },
    entry_points={
        'console_scripts': [
            'edit_playlist = spoterm.edit_playlist:main',
            'get_my_followed_artists = spoterm.get_my_followed_artists:main',
            'get_my_playlists = spoterm.get_my_playlists:main',
            'get_playlist_tracks = spoterm.get_playlist_tracks:main',
            'track_info = spoterm.track_info:main',
        ],
    }
)
