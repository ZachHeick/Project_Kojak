"""
Topic: Project 5  
Subject: Getting Track data from Spotify API
Date: 12/12/2017  
Name: Zach Heick  
"""

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, select
import os
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import time
import pickle
from sqlalchemy import create_engine, MetaData, Table
import boto3

# Connect to database
engine_name = 'postgresql://' + str(os.environ['POSTGRESQL_U']) + ':' + str(os.environ['POSTGRESQL_P']) + str(os.environ['AWS_PROJECT_KOJAK_EC2'])

engine = create_engine(engine_name)

artist_ids = list(pd.read_sql_query('''SELECT * FROM artists WHERE artist_type = 'group';''', engine)['artist_id'])

client_credentials_manager = SpotifyClientCredentials(client_id=os.environ['SPOTIFY_CLIENT_ID'],
                                                      client_secret=os.environ['SPOTIFY_CLIENT_SECRET'])

spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_albums_data(artist_id):
    """
    Gets album metadata for each artist_id
    :param artist_id: spotify artist_id
    :returns: artist_id with dictionary of album metadata
    """
    results = spotify.artist_albums(artist_id, album_type='album')
    albums = results['items']
    albums_data = []
    for album in albums:
        album_data = {}
        album_data['album_name'] = album['name']
        album_data['album_id'] = album['id']
        if len(album['images']) > 0:
            album_data['album_art'] = album['images'][0]['url']
        else:
            album_data['album_art'] = 'No Album Art'
        albums_data.append(album_data)
    return {'artist_id': artist_id, 'albums_data': albums_data}

def get_track_data(artist_album_data):
    """
    Gets track metadata from each artist's album
    :param artist_album_data: JSON-like object of artist and their albums
    :returns: track metadata
    """
    tracks_data = []
    albums = artist_album_data['albums_data']
    for album in albums:
        album_id = album['album_id']
        results = spotify.album_tracks(album_id)
        tracks = results['items']
        for track in tracks:
            track_data = {}
            track_data['artist_id'] = artist_album_data['artist_id']
            track_data['album_name'] = album['album_name']
            track_data['album_id'] = album['album_id']
            track_data['album_art'] = album['album_art']
            track_data['track_name'] = track['name']
            track_data['track_id'] = track['id']
            track_data['duration_ms'] = track['duration_ms']

            features = spotify.audio_features(track['id'])[0]

            if features is not None:
                track_data['energy'] = features['energy']
                track_data['liveness'] = features['liveness']
                track_data['loudness'] = features['loudness']
                track_data['tempo'] = features['tempo']
                track_data['speechiness'] = features['speechiness']
            else:
                track_data['energy'] = None
                track_data['liveness'] = None
                track_data['loudness'] = None
                track_data['tempo'] = None
                track_data['speechiness'] = None
            tracks_data.append(track_data)
    return tracks_data

# Get track data
tracks = []
for artist_id in artist_ids:
    albums_data = get_albums_data(artist_id)
    tracks += get_track_data(albums_data)

print('tracks saved')

# Remove those with duplicate IDs
curr_track_ids = set()
tracks_no_dups = []
for track in tracks:
    if track is not []:
        if track['track_id'] not in curr_track_ids:
            curr_track_ids.add(track['track_id'])
            tracks_no_dups.append(track)
            
# Store in database
m = MetaData()
m.reflect(engine)
conn = engine.connect()
conn.execute(m.tables['tracks'].insert(), tracks_no_dups)