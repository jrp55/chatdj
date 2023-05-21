from flask import Flask, render_template, request, redirect
import os
import random
import string
from logging.config import dictConfig
from spotify_client import SpotifyClient
from playlist_input import PlaylistInput

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'stream': 'ext://sys.stderr'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': [
            'console'
        ]
    }
})

def create_app():
    app = Flask(__name__, instance_relative_config=True)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

CLIENT_ID = 'e3bcb9c19d2b46259687ee8ec7cc2528'
CLIENT_SECRET = os.environ['CLIENT_SECRET']
REDIRECT_URI = os.environ['REDIRECT_URI']

@app.route('/')
def index():
    """
    Start point for this app.
    """
    return render_template('welcome.html')

@app.route('/get_permissions')
def get_permissions():
    """
    Redirects the user to the spotify authorization code flow
    https://developer.spotify.com/documentation/general/guides/authorization/code-flow/
    """
    state = ''.join(random.choice(string.ascii_letters) for x in range(16))
    return redirect(f'https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&state={state}&scope=playlist-modify-private%20playlist-modify-public')

@app.route('/create_playlist', methods=['GET', 'POST'])
def create_playlist():
    """
    Either renders the input form for GET request, for processes the form input on POST request.
    """
    if request.method == 'POST':
        # POST request, create and populate the playlist
        app.logger.info('Hello')
        spotify_client = SpotifyClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, app.logger)
        app.logger.info('Created spotify client')
        playlist_input = PlaylistInput.from_flask_request(request, app.logger)
        app.logger.info('Created playlist input')
        
        spotify_client.obtain_access_token_from_spotify(request.form['access_code'])

        try:
            playlist_url = spotify_client.create_playlist_on_spotify(playlist_input)
        except Exception as e:
            return render_template("playlist_failure.html", error=str(e))

        return render_template("success.html", 
            num_tracks=playlist_input.num_tracks,
            name=playlist_input.name,
            description=playlist_input.description,
            visibility=playlist_input.visibility.to_str(),
            playlist_url=playlist_url
        )
    elif request.method == 'GET':
        # GET request, this is the endpoint that the user is redirected to
        # during the Spotify authorization code flow - so should expect
        # an access code in the 'code' query parameter at this point
        if 'code' in request.args:
            return render_template('input_form.html', access_code=request.args['code'])
        else:
            return render_template('login_failure.html', error=request.args.get('error', 'unknown error'))
    else:
        raise RuntimeError(f'Mad method: {request.method}')
