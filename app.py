import os
from flask import Flask, request, redirect, session, jsonify
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

# Spotify Client Credentials
CLIENT_ID = 'd95b2e7d01b641ae8cdeb53a665e9b78' 
CLIENT_SECRET = '3230597be96f41faa69ea9a4283f8c26'  
REDIRECT_URI = 'https://<username>.github.io/callback' 

# Flask Uygulaması Başlatılıyor
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_NAME'] = 'your_session_name'

# Spotify OAuth İstemcisi
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                         client_secret=CLIENT_SECRET,
                         redirect_uri=REDIRECT_URI,
                         scope="user-library-read user-read-playback-state user-read-currently-playing")

def get_spotify_client():
    token_info = session.get('token_info', None)

    if not token_info:
        return None

    # Token yenilenmesi gerekiyorsa yenile
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info

    return Spotify(auth=token_info['access_token'])

@app.route('/')
def home():
    return 'Spotify Auth API!'

# Kullanıcıyı Spotify Login Sayfasına Yönlendir
@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# Spotify'dan geri dönüp, Token alma işlemi
@app.route('/callback')
def callback():
    token_info = sp_oauth.get_access_token(request.args['code'])
    session['token_info'] = token_info
    return redirect('/currently_playing')

# Kullanıcının Şu Anda Dinlediği Parçayı Al
@app.route('/currently_playing')
def currently_playing():
    sp = get_spotify_client()

    if sp is None:
        return redirect('/login')  # Token yoksa login sayfasına yönlendir

    # Şu an çalınan şarkıyı alıyoruz
    current_track = sp.current_playback()

    if current_track is None or 'item' not in current_track:
        return "No track is currently playing."

    track_name = current_track['item']['name']
    track_url = current_track['item']['external_urls']['spotify']
    
    return jsonify({
        'track_name': track_name,
        'track_url': track_url
    })

# API'yi çalıştırma
if __name__ == '__main__':
    app.run(debug=True)
