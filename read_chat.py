import re
import os
from typing import Generator
from collections import namedtuple

SpotifyTrack = namedtuple('SpotifyTrack', ['track_id', 'extra_params'])

SPOTIFY_URL_PATTERN = r"https://open\.spotify\.com/track/(?P<TRACK_ID>[^?\s]+)(\?(?P<EXTRA_PARAMS>[^\s]+))?"

def detect_spotify_tracks(chat_input: str) -> Generator[SpotifyTrack, None, None]:
    for spotify_match in re.finditer(SPOTIFY_URL_PATTERN, chat_input):
        yield SpotifyTrack(spotify_match.group('TRACK_ID'), spotify_match.group('EXTRA_PARAMS'))

def main():
    with open(os.path.join('test_data', 'test.txt')) as input_file_handle:
        data = input_file_handle.read()
    for link in detect_spotify_tracks(data):
        print(link)

if __name__ == '__main__':
    main()