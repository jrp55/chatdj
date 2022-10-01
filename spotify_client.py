from base64 import b64encode
from collections import namedtuple
import requests
import json
from typing import List
from playlist_input import PlaylistInput
from playlist_visibility import PlaylistVisibility
from logging import Logger

PlaylistCreationDetails = namedtuple('PlaylistCreationDetails', ['id', 'external_url'])

class SpotifyClient(object):
    def __init__(self, client_id: str, client_secret: str, logger: Logger):
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token = None
        self.logger = logger

        self._client_authorization = b64encode(bytes(f'{self._client_id}:{self._client_secret}', 'utf-8')).decode('utf-8')

    @property
    def client_id(self):
        return self._client_id

    @property
    def client_authorization(self):
        return self._client_authorization
    
    @property
    def access_token(self):
        if self._access_token is None:
            raise RuntimeError('Tried to use access_token before calling obtain_access_token_from_spotify')
        return self._access_token

    def default_headers(self):
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def obtain_access_token_from_spotify(self, code: str) -> None:
        """
        Converts the access code to an access token, which is stored on this client.
        Expects that this client hasn't obtained an access token via this call previously.
        https://developer.spotify.com/documentation/general/guides/authorization/code-flow/#request-access-token
        """
        if self._access_token is not None:
            raise RuntimeError('Tried calling obtain_access_token_from_spotify multiple times')

        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': 'http://localhost:5000/create_playlist'
        }
        headers = {
            'Authorization': f'Basic {self.client_authorization}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(f'https://accounts.spotify.com/api/token', headers=headers, data=payload)
        if 200 != response.status_code:
            raise RuntimeError(f'Got a {response} code from /api/token endpoint, expected 200')
        self._access_token = response.json()['access_token']
        self.logger.info('Obtained access token from Spotify')

    def _get_user_id(self, access_token: str) -> str:
        """
        Get the user ID associated with a given access token
        https://developer.spotify.com/documentation/web-api/reference/#/operations/get-current-users-profile
        :return: the user id
        """
        headers = self.default_headers()
        response = requests.get(f'https://api.spotify.com/v1/me', headers=headers)
        if not response.ok:
            self.logger.error(f'Error getting user id: {response.status_code}: {response.content}')
        response.raise_for_status()
        return response.json()['id']

    def _create_playlist(self, userid: str, name: str, description: str, public: bool, collab: bool) -> PlaylistCreationDetails:
        """
        Create the playlist.
        https://developer.spotify.com/documentation/web-api/reference/#/operations/create-playlist
        :return: the playlist creation details
        """
        headers = self.default_headers()
        payload = json.dumps({
            'name': name,
            'description': description,
            'public': public,
            'collaborative': collab
        })
        response = requests.post(f'https://api.spotify.com/v1/users/{userid}/playlists', headers=headers, data=payload)
        if not response.ok:
            self.logger.error(f'Error creating playlist: {response.status_code}: {response.content}')
        response.raise_for_status()
        return PlaylistCreationDetails(response.json()['id'], response.json()['external_urls']['spotify'])


    def _add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str]) -> None:
        """
        Add tracks to playlist.
        https://developer.spotify.com/documentation/web-api/reference/#/operations/add-tracks-to-playlist
        NB only 100 tracks can be added at once
        """
        headers = self.default_headers()
        NUM_TRACKS = 100
        cursor = 0
        total_tracks_to_add = len(track_ids)
        while cursor < total_tracks_to_add-1:
            next_cursor = min(total_tracks_to_add, cursor+NUM_TRACKS-1)
            payload = json.dumps({
                'uris': [f'spotify:track:{ti}' for ti in track_ids[cursor:next_cursor]]
            })

            response = requests.post(f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks', headers=headers, data=payload)
            if not response.ok:
                self.logger.error(f'Error adding tracks to playlist: {response.status_code}: {response.content}')
            response.raise_for_status()
            cursor = next_cursor


    def create_playlist_on_spotify(self, playlist_input: PlaylistInput):
        """
        Does the donkey work of talking to Spotify to create and populate the playlist
        :return: The external URL for the created playlist
        """
        try:
            user_id = self._get_user_id(self.access_token)
            playlist_creation_details = self._create_playlist(user_id
                ,playlist_input.name
                ,playlist_input.description
                ,True if playlist_input.visibility == PlaylistVisibility.Public else False
                ,playlist_input.collaborative
            )
            self._add_tracks_to_playlist(playlist_creation_details.id, [
                track_info.track_id for track_info in playlist_input.track_infos
            ])
        except Exception as e:
            self.logger.error(f'Exception occurred while creating and populating playlist: {str(e)}')
            raise
        return playlist_creation_details.external_url

