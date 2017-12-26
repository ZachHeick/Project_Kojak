import flask
import os
import boto3
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, select
import string
import pickle

app = flask.Flask(__name__)

POSTGRESQL_U = str(os.environ['zU'])
POSTGRESQL_P = str(os.environ['zP'])
AWS_PROJECT_KOJAK_EC2 = str(os.environ['AWS_PROJECT_KOJAK_EC2'])

# Connect to database
DB_URL = 'postgresql://' + POSTGRESQL_U + ':' + POSTGRESQL_P + AWS_PROJECT_KOJAK_EC2
engine = create_engine(DB_URL)

df = pd.read_sql_query('''SELECT
                           tracks.track_name,
                           artists.artist_name,
                           tracks.album_art,
                           lyrics.lyrics,
                           tracks.track_id,
                           track_previews.track_preview_url
                           FROM tracks
                           JOIN artists ON tracks.artist_id = artists.artist_id
                           JOIN lyrics ON tracks.track_id = lyrics.track_id
                           JOIN track_previews ON track_previews.track_id = tracks.track_id
                           WHERE tracks.energy IS NOT NULL
                           AND lyrics.lyrics IS NOT NULL
                           AND artists.artist_name != 'Kid Rock'
                           ORDER BY tracks.track_name;''', engine)

# Create dataframe
df['track_name'] = df['track_name'].apply(lambda i: string.capwords(i))
df.drop_duplicates(subset=['track_name', 'artist_name'], inplace=True)
df.reset_index(drop=True, inplace=True)
df.drop(df[df['lyrics'].str.contains('<span')].index, inplace=True)
df.reset_index(drop=True, inplace=True)

with open('Web_App/static/all_lyrics_dataframe.pickle', 'rb') as f:
    df = pickle.load(f)

# Lookup table for tracks and artists where keys are "Track by Artist" and value is an index
TRACKS_AND_ARTISTS = []
TRACKS_AND_ARTIST_INDEXES = {}
for i, row in enumerate(df[['track_name', 'artist_name']].itertuples()):
    track_name = row[1]
    artist_name = row[2]
    TRACKS_AND_ARTISTS.append(track_name + ' by ' + artist_name)
    TRACKS_AND_ARTIST_INDEXES[track_name + ' by ' + artist_name] = i

with open('Web_App/static/neighbors', 'rb') as f:
    NEIGHBORS = pickle.load(f)


@app.route('/track_preview', methods=['POST'])
def play_track_preview():
    """
    Gets track audio preview
    :return: jsonified audio preview
    """
    data = flask.request.get_json()
    track_and_artist = data['track_and_artist']
    index = TRACKS_AND_ARTIST_INDEXES[track_and_artist]
    track_preview_data = {}
    track = df.iloc[index]
    track_preview_data = {'preview_url': track['track_preview_url']}

    return flask.jsonify(track_preview_data)


@app.route('/track_info', methods=['POST'])
def track_info():
    """
    Gets basic track data
    :return: jsonified track data
    """
    data = flask.request.get_json()
    track_and_artist = data['track_and_artist']
    index = TRACKS_AND_ARTIST_INDEXES[track_and_artist]
    track_data = {}
    track = df.iloc[index]

    track_data = {'track_info': [
        track['album_art'],
        track['track_name'],
        track['artist_name'],
        track['lyrics']
    ]}
    return flask.jsonify(track_data)


@app.route('/playlist', methods=['POST'])
def playlist():
    """
    Gets the playlist
    :return: jsonified playlist
    """
    data = flask.request.get_json()
    track_and_artist = data['track_and_artist']
    index = TRACKS_AND_ARTIST_INDEXES[track_and_artist]

    playlist_data = {}
    for i, track in enumerate(df.iloc[NEIGHBORS[index]].iterrows()):
        track_name = track[1]['track_name']
        artist_name = track[1]['artist_name']
        playlist_data[i] = [track_name, artist_name]

    playlist = {'playlist': playlist_data}
    return flask.jsonify(playlist)


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    """
    jquery autocomplete available songs
    :return: jsonified tracks and artists
    """
    return flask.jsonify(json_list=TRACKS_AND_ARTISTS)


@app.route('/')
def home():
    with open("Web_App/templates/home.html", 'r') as home_file:
        return home_file.read()

if __name__ == '__main__':
    app.run(debug=True)
