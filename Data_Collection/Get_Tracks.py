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

class Spotify_Tracks():
    def __init__(self):
        self.tracks = []
        self.track_ids = {} 
          
        self.engine_name = 'postgresql://' + 
                            str(os.environ['POSTGRESQL_U']) + ':' + 
                            str(os.environ['POSTGRESQL_P']) + 
                           '@13.59.54.149:5432/project_kojak'
        
        self.engine = create_engine(self.engine_name)
        self.artist_ids = list(pd.read_sql_query('''SELECT * FROM artists;''', self.engine)['artist_id']) 
             
        self.client_credentials_manager = SpotifyClientCredentials(client_id=os.environ['SPOTIFY_CLIENT_ID'],
                                                     client_secret=os.environ['SPOTIFY_CLIENT_SECRET'])
    
        self.spotify = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)
        
        
    def __get_albums_data(self, artist_id):
        """
        Gets album metadata for each artist_id
        :param artist_id: spotify artist_id
        :returns: artist_id with dictionary of album metadata
        """
        results = self.spotify.artist_albums(artist_id, album_type='album')
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
    
    
    def __get_track_data(self, artist_album_data):
        """
        Gets track metadata from each artist's album
        :param artist_album_data: JSON-like object of artist and their albums
        :returns: track metadata
        """
        tracks_data = []
        albums = artist_album_data['albums_data']
        for album in albums:
            album_id = album['album_id']
            results = self.spotify.album_tracks(album_id)
            tracks = results['items']
            for track in tracks:
                if track['id'] not in self.track_ids:
                    track_data = {}
                    self.track_ids[track['id']] = 1
                    track_data['artist_id'] = artist_album_data['artist_id']
                    track_data['album_name'] = album['album_name']
                    track_data['album_id'] = album['album_id']
                    track_data['album_art'] = album['album_art']
                    track_data['track_name'] = track['name']
                    track_data['track_id'] = track['id']
                    track_data['duration_ms'] = track['duration_ms']
                    
                    features = self.spotify.audio_features(track['id'])[0]
                    
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
    
    
    def __insert_into_psql(self):
        """
        Inserts all collected data into PostgreSQL database
        """
        m = MetaData()
        m.reflect(self.engine)
        conn = self.engine.connect()
        conn.execute(m.tables['tracks'].insert(), [d for d in self.tracks if d is not []])

    
    def collect_and_save_tracks(self):
        """
        Uploads saved data to AWS bucket
        """
        for artist_id in self.artist_ids:
            albums_data = self.__get_albums_data(artist_id)
            self.tracks += self.__get_track_data(albums_data)
            
        print('Got tracks')
        
        s3 = boto3.client('s3', 
                  aws_access_key_id=os.environ['AWS_ACCESS_KEY'], 
                  aws_secret_access_key=os.environ['AWS_SECRET_KEY'])
        
        s3.upload_file('tracks.pickle', 'metis-project-kojak-bucket', 'tracks.pickle')

        self.__insert_into_psql()
        print('Inserted Tracks')



st = Spotify_Tracks()
st.collect_and_save_tracks()