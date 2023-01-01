from flask.wrappers import Request
from playlist_visibility import PlaylistVisibility
from read_chat import detect_spotify_tracks
from logging import Logger


class PlaylistInput(object):
    """
    Contains the information required to generate a playlist
    """

    def __init__(self, name: str, description: str,
                 visibility: PlaylistVisibility, collaborative: bool,
                 chat_input: str, logger: Logger):
        """
        :param name: Desired name for playlist
        :param description: Desired description for playlist
        :param visibility: Desired visibility for playlist
        :param collaborative: Desired collaborative state for playlist
        :param chat_input: Desired chat input to scan for spotify links
        """
        self.logger = logger
        self.name = name
        self.description = description
        self.visibility = visibility
        self.collaborative = collaborative
        self.track_infos = list(detect_spotify_tracks(chat_input))

        self.logger.info(f'Detected {len(self.track_infos)}\
                Spotify tracks from chat input')

    @classmethod
    def from_flask_request(cls, request_chat_content: str, request: Request,
                           logger: Logger):
        """
        Constructs a PlaylistInput from a flask request
        :param request_chat_content: Content of the chat that the playlist will
        be generated from.
        :param request: flask request with required form data and file upload
        :param logger: Logger
        """
        return cls(request.form['playlist_name'],
                   request.form['playlist_desc'],
                   PlaylistVisibility.from_str(
                       request.form['playlist_visibility']),
                   False,  # collaborative
                   request_chat_content,
                   logger)

    @property
    def num_tracks(self) -> int:
        """
        Ronseal.
        """
        return len(self.track_infos)
