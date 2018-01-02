"""
Topic: Project 5  
Subject: Getting Track preview data from Spotify API
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
from sqlalchemy import create_engine, MetaData, Table
import string


# Connect to database
engine_name = 'postgresql://' + str(os.environ['zU']) + ':' + str(os.environ['zP']) + str(os.environ['AWS_PROJECT_KOJAK_EC2'])
engine = create_engine(engine_name)

df = pd.read_sql_query('''SELECT
                           tracks.track_name,
                           artists.artist_name,
                           tracks.album_art,
                           lyrics.lyrics,
                           tracks.track_id,
                           FROM tracks
                           JOIN artists ON tracks.artist_id = artists.artist_id
                           JOIN lyrics ON tracks.track_id = lyrics.track_id
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

client_credentials_manager = SpotifyClientCredentials(client_id=os.environ['SPOTIFY_CLIENT_ID'],
                                                      client_secret=os.environ['SPOTIFY_CLIENT_SECRET'])

spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

track_ids = df['track_id']

def get_track_preview_data(track_ids):
    """
    Gets track preview url from Spotify API
    :param track_ids: list of Spotify track IDs
    :returns: list of track preview urls
    """
    tracks_preview_data = []
    for i, id_ in enumerate(track_ids):
        if i % 1000 == 0:
            time.sleep(30)
        track_preview_data = {}
        track_preview_url = spotify.track(track_ids[i])['preview_url']
        track_preview_data['track_id'] = id_
        track_preview_data['track_preview_url'] = track_preview_url
        tracks_preview_data.append(track_preview_data)
    return tracks_preview_data

tracks_preview_data = get_track_preview_data(track_ids)

# Store preview URLs into database
m = MetaData()
m.reflect(engine)
conn = engine.connect()
conn.execute(m.tables['track_previews'].insert(), tracks_preview_data)
